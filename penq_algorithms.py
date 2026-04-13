"""Adaptive TFIM variational solver on top of exact and MPS PenQ backends.

Mathematical model used by this module:

- TFIM open-chain Hamiltonian:
  ``H = -J sum_i Z_i Z_{i+1} - h sum_i X_i``
- Variational objective:
  ``E(theta) = <psi(theta)|H|psi(theta)>``
- Per-layer ansatz block:
  ``U_l(gamma_l, beta_l) = U_X(beta_l) U_ZZ(gamma_l)``
- Full ``L``-layer state:
  ``|psi_L> = prod_l U_l |+>^n``
- Adaptive improvement:
  ``Delta_L = E_{L-1}^* - E_L^*``
- Stop rule:
  ``Delta_L <= tol or L == max_layers``

Portable ZZ identity used by both exact and MPS paths:

``CNOT - RZ(2 gamma) - CNOT = exp(-i gamma Z⊗Z)``
"""

import math

import numpy as np
import pennylane as qml

from .lattice_geometry_utils import square_horizontal_pairs
from .lattice_geometry_utils import square_site_count
from .lattice_geometry_utils import square_vertical_pairs
from .lattice_geometry_utils import cubic_site_count
from .lattice_geometry_utils import cubic_x_pairs
from .lattice_geometry_utils import cubic_y_pairs
from .lattice_geometry_utils import cubic_z_pairs


EXACT_BACKEND_NAMES = {"qml", "exact", "statevector", "penq.qml_starter"}
MPS_BACKEND_NAMES = {"mps", "penq.mps_starter"}


def tfim_open_chain_hamiltonian(n, J, h):
    """Return 1D open-chain TFIM Hamiltonian ``H = -J sum ZZ - h sum X``."""
    if n < 2:
        raise ValueError("adaptive_tfim_vqe expects n >= 2.")

    coefficients = []
    terms = []

    for wire in range(n - 1):
        coefficients.append(float(-J))
        terms.append(qml.PauliZ(wire) @ qml.PauliZ(wire + 1))

    for wire in range(n):
        coefficients.append(float(-h))
        terms.append(qml.PauliX(wire))

    return qml.dot(coefficients, terms)


def _backend_device_name(backend):
    if backend in EXACT_BACKEND_NAMES:
        return "penq.qml_starter", "qml"
    if backend in MPS_BACKEND_NAMES:
        return "penq.mps_starter", "mps"
    raise ValueError("backend must be one of: qml, exact, statevector, penq.qml_starter, mps, penq.mps_starter.")


def _make_device(n, backend, max_bond_dim=None, svd_cutoff=0.0):
    device_name, backend_label = _backend_device_name(backend)
    if backend_label == "qml":
        return qml.device(device_name, wires=n), backend_label
    return (
        qml.device(device_name, wires=n, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff),
        backend_label,
    )


def _apply_portable_zz_block(gamma, n):
    """Apply ``U_ZZ(gamma)`` on open-chain neighbors with portable supported gates.

    Uses identity
    ``CNOT - RZ(2 gamma) - CNOT = exp(-i gamma Z⊗Z)``
    on each nearest-neighbor bond.
    """
    for wire in range(n - 1):
        qml.CNOT(wires=[wire, wire + 1])
        qml.RZ(2.0 * gamma, wires=wire + 1)
        qml.CNOT(wires=[wire, wire + 1])


def apply_adaptive_tfim_ansatz(n, layer_params):
    """Prepare ``|psi_L> = prod_l U_l |+>^n`` with portable TFIM layers.

    Each layer uses
    ``U_l(gamma_l, beta_l) = U_X(beta_l) U_ZZ(gamma_l)``.
    ``U_ZZ`` is implemented by adjacent ``CNOT-RZ-CNOT`` blocks.
    ``U_X`` is implemented by global ``RX(2 beta_l)`` rotations.
    """
    for wire in range(n):
        qml.Hadamard(wires=wire)

    for gamma, beta in layer_params:
        _apply_portable_zz_block(gamma, n)
        for wire in range(n):
            qml.RX(2.0 * beta, wires=wire)


def _observable_values(dev, n, J, h, layer_params):
    hamiltonian = tfim_open_chain_hamiltonian(n, J, h)

    @qml.qnode(dev)
    def energy_circuit():
        apply_adaptive_tfim_ansatz(n, layer_params)
        return qml.expval(hamiltonian)

    @qml.qnode(dev)
    def x0_circuit():
        apply_adaptive_tfim_ansatz(n, layer_params)
        return qml.expval(qml.PauliX(0))

    @qml.qnode(dev)
    def z0z1_circuit():
        apply_adaptive_tfim_ansatz(n, layer_params)
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    energy = float(energy_circuit())
    expval_x0 = float(x0_circuit())
    expval_z0z1 = float(z0z1_circuit())
    return energy, expval_x0, expval_z0z1


def _layer_search(dev, n, J, h, fixed_params, search_rounds, grid_points):
    """Deterministic local grid search for one new adaptive TFIM layer."""
    center_gamma = 0.0
    center_beta = 0.0
    span_gamma = np.pi / 2.0
    span_beta = np.pi / 2.0
    best_gamma = 0.0
    best_beta = 0.0
    best_energy = math.inf

    for _ in range(search_rounds):
        gamma_grid = np.linspace(center_gamma - span_gamma, center_gamma + span_gamma, grid_points)
        beta_grid = np.linspace(center_beta - span_beta, center_beta + span_beta, grid_points)
        for gamma in gamma_grid:
            for beta in beta_grid:
                candidate = fixed_params + [(float(gamma), float(beta))]
                energy, _, _ = _observable_values(dev, n, J, h, candidate)
                if energy < best_energy:
                    best_energy = float(energy)
                    best_gamma = float(gamma)
                    best_beta = float(beta)
        center_gamma = best_gamma
        center_beta = best_beta
        span_gamma *= 0.5
        span_beta *= 0.5

    return best_gamma, best_beta, best_energy


def adaptive_tfim_vqe(
    n,
    J,
    h,
    backend="mps",
    max_layers=4,
    max_bond_dim=None,
    svd_cutoff=0.0,
    optimizer="deterministic_grid",
    steps=2,
    seed=None,
    tol=1e-6,
    grid_points=7,
):
    """Solve TFIM variational problem with deterministic adaptive layer growth.

    Physics:
    - ``H = -J sum_i Z_i Z_{i+1} - h sum_i X_i``
    - ``E(theta) = <psi(theta)|H|psi(theta)>``

    Ansatz:
    - ``U_l(gamma_l, beta_l) = U_X(beta_l) U_ZZ(gamma_l)``
    - ``|psi_L> = prod_l U_l |+>^n``

    Adaptive rule:
    - ``Delta_L = E_{L-1}^* - E_L^*``
    - stop when ``Delta_L <= tol`` or when ``L == max_layers``

    Returns structured deterministic result for exact or MPS backend.
    """
    if optimizer not in {None, "deterministic_grid"}:
        raise ValueError("adaptive_tfim_vqe supports only optimizer='deterministic_grid'.")
    if n < 2:
        raise ValueError("adaptive_tfim_vqe expects n >= 2.")
    if max_layers < 0:
        raise ValueError("max_layers must be non-negative.")
    if steps < 1:
        raise ValueError("steps must be at least one.")
    if grid_points < 3 or grid_points % 2 == 0:
        raise ValueError("grid_points must be an odd integer >= 3.")
    if seed is not None:
        seed = int(seed)

    dev, backend_label = _make_device(n, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)
    layer_params = []
    history = []

    base_energy, base_x0, base_z0z1 = _observable_values(dev, n, J, h, layer_params)
    history.append(
        {
            "layer": 0,
            "energy": float(base_energy),
            "energy_per_site": float(base_energy / n),
            "expval_x0": float(base_x0),
            "expval_z0z1": float(base_z0z1),
            "converged": False,
            "final_delta_energy": 0.0,
            "max_bond_dim": "" if backend_label == "qml" or max_bond_dim is None else int(max_bond_dim),
            "svd_cutoff": float(svd_cutoff),
        }
    )

    current_energy = float(base_energy)
    current_x0 = float(base_x0)
    current_z0z1 = float(base_z0z1)
    converged = False
    final_delta = 0.0

    for layer_index in range(1, max_layers + 1):
        gamma, beta, candidate_energy = _layer_search(
            dev,
            n,
            J,
            h,
            layer_params,
            search_rounds=steps,
            grid_points=grid_points,
        )
        delta_energy = float(current_energy - candidate_energy)
        final_delta = delta_energy

        if delta_energy <= tol:
            converged = True
            history[-1]["converged"] = True
            history[-1]["final_delta_energy"] = float(delta_energy)
            break

        layer_params.append((gamma, beta))
        current_energy, current_x0, current_z0z1 = _observable_values(dev, n, J, h, layer_params)
        history.append(
            {
                "layer": int(layer_index),
                "energy": float(current_energy),
                "energy_per_site": float(current_energy / n),
                "expval_x0": float(current_x0),
                "expval_z0z1": float(current_z0z1),
                "converged": False,
                "final_delta_energy": float(delta_energy),
                "max_bond_dim": "" if backend_label == "qml" or max_bond_dim is None else int(max_bond_dim),
                "svd_cutoff": float(svd_cutoff),
            }
        )

    if history:
        history[-1]["converged"] = converged
        history[-1]["final_delta_energy"] = float(final_delta)

    return {
        "n": int(n),
        "J": float(J),
        "h": float(h),
        "backend": backend_label,
        "energy": float(current_energy),
        "energy_per_site": float(current_energy / n),
        "best_params": [{"gamma": float(gamma), "beta": float(beta)} for gamma, beta in layer_params],
        "layers_used": int(len(layer_params)),
        "converged": bool(converged),
        "final_delta_energy": float(final_delta),
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
        "expval_x0": float(current_x0),
        "expval_z0z1": float(current_z0z1),
        "history": history,
        "seed": seed,
    }


def compare_tfim_vqe_exact_vs_mps(
    n,
    J,
    h,
    max_layers=4,
    max_bond_dim=4,
    svd_cutoff=1e-12,
    optimizer="deterministic_grid",
    steps=2,
    seed=None,
    tol=1e-6,
    grid_points=7,
):
    """Compare adaptive TFIM VQE on exact and MPS backends for same small case."""
    exact_result = adaptive_tfim_vqe(
        n=n,
        J=J,
        h=h,
        backend="qml",
        max_layers=max_layers,
        optimizer=optimizer,
        steps=steps,
        seed=seed,
        tol=tol,
        grid_points=grid_points,
    )
    mps_result = adaptive_tfim_vqe(
        n=n,
        J=J,
        h=h,
        backend="mps",
        max_layers=max_layers,
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        optimizer=optimizer,
        steps=steps,
        seed=seed,
        tol=tol,
        grid_points=grid_points,
    )
    return {
        "n": int(n),
        "J": float(J),
        "h": float(h),
        "exact": exact_result,
        "mps": mps_result,
        "abs_energy_error": float(abs(mps_result["energy"] - exact_result["energy"])),
        "abs_energy_error_per_site": float(abs(mps_result["energy"] - exact_result["energy"]) / n),
    }


def _evaluate_gradient(dev, n, J, h, params):
    """Analytically evaluate gradient of energy using macroscopic parameter-shift rule.
    
    Both ZZ and RX(2*theta) blocks are generated by Pauli strings of norm 1.
    Therefore, the exact gradient is `0.5 * (E(theta + pi/4) - E(theta - pi/4))`
    """
    shift = math.pi / 4.0
    grad = []
    
    for l, (gamma, beta) in enumerate(params):
        # Shift gamma
        params_plus = [(g + shift if i == l else g, b) for i, (g, b) in enumerate(params)]
        params_minus = [(g - shift if i == l else g, b) for i, (g, b) in enumerate(params)]
        E_plus, _, _ = _observable_values(dev, n, J, h, params_plus)
        E_minus, _, _ = _observable_values(dev, n, J, h, params_minus)
        grad_gamma = 0.5 * (E_plus - E_minus)
        
        # Shift beta
        params_plus = [(g, b + shift if i == l else b) for i, (g, b) in enumerate(params)]
        params_minus = [(g, b - shift if i == l else b) for i, (g, b) in enumerate(params)]
        E_plus, _, _ = _observable_values(dev, n, J, h, params_plus)
        E_minus, _, _ = _observable_values(dev, n, J, h, params_minus)
        grad_beta = 0.5 * (E_plus - E_minus)
        
        grad.append((grad_gamma, grad_beta))
        
    return grad


def imaginary_time_tfim(
    n,
    J,
    h,
    backend="mps",
    delta_tau=0.05,
    steps=20,
    max_layers=4,
    max_bond_dim=None,
    svd_cutoff=0.0,
    seed=0,
    tol=1e-6,
):
    """Solve TFIM using deterministic Variational Imaginary Time Evolution (VITE).
    
    In exact imaginary time, the trajectory is:
    |psi(tau)> = exp(-tau H)|psi0> / ||exp(-tau H)|psi0>||

    Under a simplified VITE framework assuming an identity/diagonal geometry
    approximation (A ~= I in McLachlan-style formulations),
    the variational parameters are updated iteratively per discrete delta_tau:
    theta_{k+1} = theta_k - delta_tau * grad_E(theta_k)

    Returns structured deterministic result for exact or MPS backend.
    """
    if n < 2:
        raise ValueError("imaginary_time_tfim expects n >= 2.")
    if max_layers < 1:
        raise ValueError("max_layers must be strictly positive.")
    if steps < 1:
        raise ValueError("steps must be at least one.")
    if delta_tau <= 0.0:
        raise ValueError("delta_tau must be strictly positive.")
    if seed is not None:
        seed = int(seed)

    dev, backend_label = _make_device(n, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)
    
    # Initialize with small deterministic pseudo-random constants to break symmetry
    rng = np.random.default_rng(seed)
    params = [(float(rng.uniform(-0.01, 0.01)), float(rng.uniform(-0.01, 0.01))) for _ in range(max_layers)]
    
    history = []
    
    current_energy, current_x0, current_z0z1 = _observable_values(dev, n, J, h, params)
    history.append({
        "step": 0,
        "delta_tau": float(delta_tau),
        "energy": float(current_energy),
        "energy_per_site": float(current_energy / n),
        "expval_x0": float(current_x0),
        "expval_z0z1": float(current_z0z1),
        "converged": False,
        "final_delta_energy": 0.0,
        "max_bond_dim": "" if backend_label == "qml" or max_bond_dim is None else int(max_bond_dim),
        "svd_cutoff": float(svd_cutoff),
    })

    converged = False
    final_delta = 0.0

    for step_index in range(1, steps + 1):
        grad = _evaluate_gradient(dev, n, J, h, params)
        
        candidate_params = [
            (g - delta_tau * dg, b - delta_tau * db) 
            for (g, b), (dg, db) in zip(params, grad)
        ]
        
        candidate_energy, candidate_x0, candidate_z0z1 = _observable_values(dev, n, J, h, candidate_params)
        
        delta_energy = float(current_energy - candidate_energy)
        final_delta = delta_energy
        
        if abs(delta_energy) <= tol and delta_energy >= 0:
            converged = True
            params = candidate_params
            current_energy, current_x0, current_z0z1 = candidate_energy, candidate_x0, candidate_z0z1
            history.append({
                "step": int(step_index),
                "delta_tau": float(delta_tau),
                "energy": float(current_energy),
                "energy_per_site": float(current_energy / n),
                "expval_x0": float(current_x0),
                "expval_z0z1": float(current_z0z1),
                "converged": True,
                "final_delta_energy": float(delta_energy),
                "max_bond_dim": "" if backend_label == "qml" or max_bond_dim is None else int(max_bond_dim),
                "svd_cutoff": float(svd_cutoff),
            })
            break
            
        params = candidate_params
        current_energy, current_x0, current_z0z1 = candidate_energy, candidate_x0, candidate_z0z1
        history.append({
            "step": int(step_index),
            "delta_tau": float(delta_tau),
            "energy": float(current_energy),
            "energy_per_site": float(current_energy / n),
            "expval_x0": float(current_x0),
            "expval_z0z1": float(current_z0z1),
            "converged": False,
            "final_delta_energy": float(delta_energy),
            "max_bond_dim": "" if backend_label == "qml" or max_bond_dim is None else int(max_bond_dim),
            "svd_cutoff": float(svd_cutoff),
        })

    if history:
        history[-1]["converged"] = converged
        history[-1]["final_delta_energy"] = float(final_delta)

    return {
        "n": int(n),
        "J": float(J),
        "h": float(h),
        "backend": backend_label,
        "delta_tau": float(delta_tau),
        "steps": int(steps),
        "energy": float(current_energy),
        "energy_per_site": float(current_energy / n),
        "best_params": [{"gamma": float(gamma), "beta": float(beta)} for gamma, beta in params],
        "converged": bool(converged),
        "final_delta_energy": float(final_delta),
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
        "expval_x0": float(current_x0),
        "expval_z0z1": float(current_z0z1),
        "energy_history": [float(h["energy"]) for h in history],
        "history": history,
        "seed": seed,
    }


def compare_imag_time_exact_vs_mps(
    n,
    J,
    h,
    delta_tau=0.05,
    steps=20,
    max_layers=4,
    max_bond_dim=4,
    svd_cutoff=1e-12,
    seed=0,
    tol=1e-6,
):
    """Compare Variational Imaginary Time Evolution on exact and MPS backends."""
    exact_result = imaginary_time_tfim(
        n=n,
        J=J,
        h=h,
        backend="qml",
        delta_tau=delta_tau,
        steps=steps,
        max_layers=max_layers,
        seed=seed,
        tol=tol,
    )
    mps_result = imaginary_time_tfim(
        n=n,
        J=J,
        h=h,
        backend="mps",
        delta_tau=delta_tau,
        steps=steps,
        max_layers=max_layers,
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        seed=seed,
        tol=tol,
    )
    return {
        "n": int(n),
        "J": float(J),
        "h": float(h),
        "exact": exact_result,
        "mps": mps_result,
        "abs_energy_error": float(abs(mps_result["energy"] - exact_result["energy"])),
        "abs_energy_error_per_site": float(abs(mps_result["energy"] - exact_result["energy"]) / n),
    }


def _apply_real_time_tfim_step(n, J, h, dt):
    """Apply one first-order Trotter real-time TFIM step.

    For ``H = -J sum ZZ - h sum X``, the first-order split is
    ``U(dt) ~= exp(+i J dt sum ZZ) exp(+i h dt sum X)``.
    Using PenQ blocks ``exp(-i gamma ZZ)`` and ``RX(2 beta)=exp(-i beta X)``,
    this is implemented with ``gamma=-J dt`` and ``beta=-h dt``.
    """
    gamma = float(-J * dt)
    beta = float(-h * dt)
    _apply_portable_zz_block(gamma, n)
    for wire in range(n):
        qml.RX(2.0 * beta, wires=wire)


def _real_time_observable_values(dev, n, J, h, dt, step):
    hamiltonian = tfim_open_chain_hamiltonian(n, J, h)

    @qml.qnode(dev)
    def energy_circuit():
        for wire in range(n):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _apply_real_time_tfim_step(n, J, h, dt)
        return qml.expval(hamiltonian)

    @qml.qnode(dev)
    def x0_circuit():
        for wire in range(n):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _apply_real_time_tfim_step(n, J, h, dt)
        return qml.expval(qml.PauliX(0))

    @qml.qnode(dev)
    def z0z1_circuit():
        for wire in range(n):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _apply_real_time_tfim_step(n, J, h, dt)
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    energy = float(energy_circuit())
    expval_x0 = float(x0_circuit())
    expval_z0z1 = float(z0z1_circuit())
    return energy, expval_x0, expval_z0z1


def real_time_tfim(
    n,
    J,
    h,
    backend="mps",
    dt=0.05,
    steps=20,
    max_bond_dim=None,
    svd_cutoff=0.0,
):
    """Evolve TFIM in real time with a deterministic Trotterized trajectory.

    The continuous target dynamics is
    ``|psi(t)> = exp(-i H t)|psi0>``
    with ``H = -J sum_i Z_i Z_{i+1} - h sum_i X_i``.

    Current implementation uses a first-order Trotter split per step.
    """
    if n < 2:
        raise ValueError("real_time_tfim expects n >= 2.")
    if steps < 1:
        raise ValueError("steps must be at least one.")
    if dt <= 0.0:
        raise ValueError("dt must be strictly positive.")

    dev, backend_label = _make_device(n, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)

    history = []
    for step in range(steps + 1):
        energy, x0, z0z1 = _real_time_observable_values(dev, n, J, h, dt, step)
        history.append(
            {
                "step": int(step),
                "time": float(step * dt),
                "dt": float(dt),
                "energy": float(energy),
                "energy_per_site": float(energy / n),
                "expval_x0": float(x0),
                "expval_z0z1": float(z0z1),
                "max_bond_dim": "" if backend_label == "qml" or max_bond_dim is None else int(max_bond_dim),
                "svd_cutoff": float(svd_cutoff),
            }
        )

    final = history[-1]
    return {
        "n": int(n),
        "J": float(J),
        "h": float(h),
        "backend": backend_label,
        "dt": float(dt),
        "steps": int(steps),
        "energy": float(final["energy"]),
        "energy_per_site": float(final["energy_per_site"]),
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
        "expval_x0": float(final["expval_x0"]),
        "expval_z0z1": float(final["expval_z0z1"]),
        "energy_history": [float(row["energy"]) for row in history],
        "expval_x0_history": [float(row["expval_x0"]) for row in history],
        "expval_z0z1_history": [float(row["expval_z0z1"]) for row in history],
        "time_history": [float(row["time"]) for row in history],
        "history": history,
    }


def compare_real_time_exact_vs_mps(
    n,
    J,
    h,
    dt=0.05,
    steps=20,
    max_bond_dim=4,
    svd_cutoff=1e-12,
):
    """Compare real-time TFIM trajectories on exact and MPS backends."""
    exact_result = real_time_tfim(
        n=n,
        J=J,
        h=h,
        backend="qml",
        dt=dt,
        steps=steps,
    )
    mps_result = real_time_tfim(
        n=n,
        J=J,
        h=h,
        backend="mps",
        dt=dt,
        steps=steps,
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
    )

    energy_diffs = [
        abs(float(mps_e) - float(exact_e))
        for exact_e, mps_e in zip(exact_result["energy_history"], mps_result["energy_history"])
    ]
    return {
        "n": int(n),
        "J": float(J),
        "h": float(h),
        "exact": exact_result,
        "mps": mps_result,
        "abs_energy_error": float(abs(mps_result["energy"] - exact_result["energy"])),
        "abs_energy_error_per_site": float(abs(mps_result["energy"] - exact_result["energy"]) / n),
        "max_abs_energy_error_over_time": float(max(energy_diffs) if energy_diffs else 0.0),
    }


def _square_tfim_mapped_ansatz(Lx, Ly, Jx, Jy, h, seed):
    """Apply one deterministic mapped-lattice ansatz layer for 2D TFIM studies.

    This is a fixed, non-optimized variational proxy circuit. It is not a
    certified exact ground-state solver.
    """
    n_sites = square_site_count(Lx, Ly)
    horizontal_pairs = square_horizontal_pairs(Lx, Ly)
    vertical_pairs = square_vertical_pairs(Lx, Ly)

    for wire in range(n_sites):
        qml.Hadamard(wires=wire)

    seed = int(seed)
    rng = np.random.default_rng(seed)
    jitter = float(rng.uniform(-0.02, 0.02))
    gamma_x = float(0.35 * Jx + 0.1 * jitter)
    gamma_y = float(0.35 * Jy - 0.1 * jitter)
    beta = float(0.35 * h + 0.05 * jitter)

    _apply_square_variational_layer(n_sites, horizontal_pairs, vertical_pairs, gamma_x, gamma_y, beta)


def _apply_square_variational_layer(n_sites, horizontal_pairs, vertical_pairs, gamma_x, gamma_y, beta):
    for wire_a, wire_b in horizontal_pairs:
        qml.CNOT(wires=[wire_a, wire_b])
        qml.RZ(2.0 * gamma_x, wires=wire_b)
        qml.CNOT(wires=[wire_a, wire_b])

    for wire_a, wire_b in vertical_pairs:
        qml.CNOT(wires=[wire_a, wire_b])
        qml.RZ(2.0 * gamma_y, wires=wire_b)
        qml.CNOT(wires=[wire_a, wire_b])

    for wire in range(n_sites):
        qml.RX(2.0 * beta, wires=wire)


def _apply_square_variational_ansatz(n_sites, horizontal_pairs, vertical_pairs, layer_params):
    for wire in range(n_sites):
        qml.Hadamard(wires=wire)

    for gamma_x, gamma_y, beta in layer_params:
        _apply_square_variational_layer(n_sites, horizontal_pairs, vertical_pairs, gamma_x, gamma_y, beta)


def _square_deterministic_initial_params(Jx, Jy, h, max_layers, seed):
    seed = int(seed)
    rng = np.random.default_rng(seed)
    params = []
    for _ in range(max_layers):
        jitter_x = float(rng.uniform(-0.02, 0.02))
        jitter_y = float(rng.uniform(-0.02, 0.02))
        jitter_b = float(rng.uniform(-0.02, 0.02))
        params.append(
            (
                float(0.35 * Jx + 0.1 * jitter_x),
                float(0.35 * Jy + 0.1 * jitter_y),
                float(0.35 * h + 0.05 * jitter_b),
            )
        )
    return params


def _square_tfim_hamiltonian(Lx, Ly, Jx, Jy, h):
    n_sites = square_site_count(Lx, Ly)
    horizontal_pairs = square_horizontal_pairs(Lx, Ly)
    vertical_pairs = square_vertical_pairs(Lx, Ly)

    coeffs = []
    ops = []
    for wire_a, wire_b in horizontal_pairs:
        coeffs.append(float(-Jx))
        ops.append(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b))
    for wire_a, wire_b in vertical_pairs:
        coeffs.append(float(-Jy))
        ops.append(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b))
    for wire in range(n_sites):
        coeffs.append(float(-h))
        ops.append(qml.PauliX(wire))
    return qml.dot(coeffs, ops)


def _square_observable_values(dev, Lx, Ly, Jx, Jy, h, layer_params):
    n_sites = square_site_count(Lx, Ly)
    horizontal_pairs = square_horizontal_pairs(Lx, Ly)
    vertical_pairs = square_vertical_pairs(Lx, Ly)
    hamiltonian = _square_tfim_hamiltonian(Lx, Ly, Jx, Jy, h)

    @qml.qnode(dev)
    def energy_circuit():
        _apply_square_variational_ansatz(n_sites, horizontal_pairs, vertical_pairs, layer_params)
        return qml.expval(hamiltonian)

    @qml.qnode(dev)
    def magnetization_x_circuit():
        _apply_square_variational_ansatz(n_sites, horizontal_pairs, vertical_pairs, layer_params)
        return [qml.expval(qml.PauliX(wire)) for wire in range(n_sites)]

    @qml.qnode(dev)
    def magnetization_z_circuit():
        _apply_square_variational_ansatz(n_sites, horizontal_pairs, vertical_pairs, layer_params)
        return [qml.expval(qml.PauliZ(wire)) for wire in range(n_sites)]

    @qml.qnode(dev)
    def horizontal_zz_circuit():
        _apply_square_variational_ansatz(n_sites, horizontal_pairs, vertical_pairs, layer_params)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in horizontal_pairs]

    @qml.qnode(dev)
    def vertical_zz_circuit():
        _apply_square_variational_ansatz(n_sites, horizontal_pairs, vertical_pairs, layer_params)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in vertical_pairs]

    energy = float(energy_circuit())
    mx_values = np.asarray(magnetization_x_circuit(), dtype=float)
    mz_values = np.asarray(magnetization_z_circuit(), dtype=float)
    hzz_values = np.asarray(horizontal_zz_circuit(), dtype=float) if horizontal_pairs else np.asarray([0.0])
    vzz_values = np.asarray(vertical_zz_circuit(), dtype=float) if vertical_pairs else np.asarray([0.0])
    return {
        "energy": float(energy),
        "magnetization_x": float(np.mean(mx_values)),
        "magnetization_z": float(np.mean(mz_values)),
        "nn_zz_horizontal": float(np.mean(hzz_values)),
        "nn_zz_vertical": float(np.mean(vzz_values)),
    }


def square_tfim_observables(
    Lx,
    Ly,
    Jx,
    Jy,
    h,
    backend="mps",
    max_bond_dim=None,
    svd_cutoff=0.0,
    seed=0,
):
    """Evaluate mapped-lattice 2D square TFIM observables on exact or MPS backends.

    Target model on open boundaries:
    ``H_2D = -Jx sum_<i,j>_x Z_i Z_j - Jy sum_<i,j>_y Z_i Z_j - h sum_i X_i``

    Lattice-to-wire mapping is row-major:
    ``s(x, y) = x + Lx * y``.

    Current implementation uses one deterministic fixed ansatz layer; this is a
    proxy low-energy workflow, not a guaranteed exact ground-state computation.
    """
    if Lx < 1 or Ly < 1:
        raise ValueError("square_tfim_observables expects Lx >= 1 and Ly >= 1.")
    n_sites = square_site_count(Lx, Ly)
    if n_sites < 2:
        raise ValueError("square_tfim_observables expects at least two lattice sites.")

    horizontal_pairs = square_horizontal_pairs(Lx, Ly)
    vertical_pairs = square_vertical_pairs(Lx, Ly)
    layer_params = _square_deterministic_initial_params(Jx, Jy, h, max_layers=1, seed=seed)

    dev, backend_label = _make_device(n_sites, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)
    obs = _square_observable_values(dev, Lx, Ly, Jx, Jy, h, layer_params)

    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "n_sites": int(n_sites),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "h": float(h),
        "backend": backend_label,
        "energy": float(obs["energy"]),
        "energy_per_site": float(obs["energy"] / n_sites),
        "magnetization_x": float(obs["magnetization_x"]),
        "magnetization_z": float(obs["magnetization_z"]),
        "nn_zz_horizontal": float(obs["nn_zz_horizontal"]),
        "nn_zz_vertical": float(obs["nn_zz_vertical"]),
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
    }


def compare_square_tfim_exact_vs_mps(
    Lx,
    Ly,
    Jx,
    Jy,
    h,
    max_bond_dim=8,
    svd_cutoff=1e-12,
    seed=0,
):
    """Compare mapped-lattice square TFIM observables between exact and MPS backends."""
    exact = square_tfim_observables(
        Lx=Lx,
        Ly=Ly,
        Jx=Jx,
        Jy=Jy,
        h=h,
        backend="qml",
        seed=seed,
    )
    mps = square_tfim_observables(
        Lx=Lx,
        Ly=Ly,
        Jx=Jx,
        Jy=Jy,
        h=h,
        backend="mps",
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        seed=seed,
    )
    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "n_sites": int(exact["n_sites"]),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "h": float(h),
        "exact_energy": float(exact["energy"]),
        "mps_energy": float(mps["energy"]),
        "abs_energy_error": float(abs(mps["energy"] - exact["energy"])),
        "abs_energy_error_per_site": float(abs(mps["energy"] - exact["energy"]) / exact["n_sites"]),
        "exact_magnetization_x": float(exact["magnetization_x"]),
        "mps_magnetization_x": float(mps["magnetization_x"]),
        "abs_magnetization_x_error": float(abs(mps["magnetization_x"] - exact["magnetization_x"])),
        "exact": exact,
        "mps": mps,
    }


def _square_tfim_real_time_step(n_sites, horizontal_pairs, vertical_pairs, Jx, Jy, h, dt):
    gamma_x = float(-Jx * dt)
    gamma_y = float(-Jy * dt)
    beta = float(-h * dt)
    _apply_square_variational_layer(n_sites, horizontal_pairs, vertical_pairs, gamma_x, gamma_y, beta)


def _square_tfim_real_time_observables(dev, Lx, Ly, Jx, Jy, h, dt, step):
    n_sites = square_site_count(Lx, Ly)
    horizontal_pairs = square_horizontal_pairs(Lx, Ly)
    vertical_pairs = square_vertical_pairs(Lx, Ly)
    hamiltonian = _square_tfim_hamiltonian(Lx, Ly, Jx, Jy, h)

    @qml.qnode(dev)
    def energy_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _square_tfim_real_time_step(n_sites, horizontal_pairs, vertical_pairs, Jx, Jy, h, dt)
        return qml.expval(hamiltonian)

    @qml.qnode(dev)
    def magnetization_x_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _square_tfim_real_time_step(n_sites, horizontal_pairs, vertical_pairs, Jx, Jy, h, dt)
        return [qml.expval(qml.PauliX(wire)) for wire in range(n_sites)]

    @qml.qnode(dev)
    def magnetization_z_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _square_tfim_real_time_step(n_sites, horizontal_pairs, vertical_pairs, Jx, Jy, h, dt)
        return [qml.expval(qml.PauliZ(wire)) for wire in range(n_sites)]

    @qml.qnode(dev)
    def horizontal_zz_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _square_tfim_real_time_step(n_sites, horizontal_pairs, vertical_pairs, Jx, Jy, h, dt)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in horizontal_pairs]

    @qml.qnode(dev)
    def vertical_zz_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _square_tfim_real_time_step(n_sites, horizontal_pairs, vertical_pairs, Jx, Jy, h, dt)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in vertical_pairs]

    energy = float(energy_circuit())
    mx_values = np.asarray(magnetization_x_circuit(), dtype=float)
    mz_values = np.asarray(magnetization_z_circuit(), dtype=float)
    hzz_values = np.asarray(horizontal_zz_circuit(), dtype=float) if horizontal_pairs else np.asarray([0.0])
    vzz_values = np.asarray(vertical_zz_circuit(), dtype=float) if vertical_pairs else np.asarray([0.0])
    return {
        "energy": float(energy),
        "magnetization_x": float(np.mean(mx_values)),
        "magnetization_z": float(np.mean(mz_values)),
        "nn_zz_horizontal": float(np.mean(hzz_values)),
        "nn_zz_vertical": float(np.mean(vzz_values)),
    }


def square_tfim_real_time(
    Lx,
    Ly,
    Jx,
    Jy,
    h,
    backend="mps",
    dt=0.05,
    steps=20,
    max_bond_dim=None,
    svd_cutoff=0.0,
    seed=0,
):
    """Real-time mapped-lattice 2D TFIM dynamics with first-order Trotter updates.

    Continuous target is ``|psi(t)> = exp(-i H_2D t)|psi0>``.
    Current implementation is a deterministic mapped-lattice Trotterized path.
    """
    if Lx < 1 or Ly < 1:
        raise ValueError("square_tfim_real_time expects Lx >= 1 and Ly >= 1.")
    n_sites = square_site_count(Lx, Ly)
    if n_sites < 2:
        raise ValueError("square_tfim_real_time expects at least two lattice sites.")
    if steps < 1:
        raise ValueError("steps must be at least one.")
    if dt <= 0.0:
        raise ValueError("dt must be strictly positive.")

    dev, backend_label = _make_device(n_sites, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)

    time_history = []
    energy_history = []
    magnetization_x_history = []
    magnetization_z_history = []
    nn_zz_horizontal_history = []
    nn_zz_vertical_history = []

    for step in range(steps + 1):
        obs = _square_tfim_real_time_observables(dev, Lx, Ly, Jx, Jy, h, dt, step)
        time_history.append(float(step * dt))
        energy_history.append(float(obs["energy"]))
        magnetization_x_history.append(float(obs["magnetization_x"]))
        magnetization_z_history.append(float(obs["magnetization_z"]))
        nn_zz_horizontal_history.append(float(obs["nn_zz_horizontal"]))
        nn_zz_vertical_history.append(float(obs["nn_zz_vertical"]))

    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "n_sites": int(n_sites),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "h": float(h),
        "backend": backend_label,
        "dt": float(dt),
        "steps": int(steps),
        "time_history": time_history,
        "energy_history": energy_history,
        "magnetization_x_history": magnetization_x_history,
        "magnetization_z_history": magnetization_z_history,
        "nn_zz_horizontal_history": nn_zz_horizontal_history,
        "nn_zz_vertical_history": nn_zz_vertical_history,
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
        "seed": int(seed),
    }


def _square_tfim_imag_gradient(dev, Lx, Ly, Jx, Jy, h, params):
    shift = math.pi / 4.0
    grad = []
    for layer_idx in range(len(params)):
        grad_layer = []
        for param_idx in range(3):
            plus_params = list(params)
            minus_params = list(params)
            p_plus = list(plus_params[layer_idx])
            p_minus = list(minus_params[layer_idx])
            p_plus[param_idx] += shift
            p_minus[param_idx] -= shift
            plus_params[layer_idx] = tuple(p_plus)
            minus_params[layer_idx] = tuple(p_minus)
            energy_plus = _square_observable_values(dev, Lx, Ly, Jx, Jy, h, plus_params)["energy"]
            energy_minus = _square_observable_values(dev, Lx, Ly, Jx, Jy, h, minus_params)["energy"]
            grad_layer.append(float(0.5 * (energy_plus - energy_minus)))
        grad.append(tuple(grad_layer))
    return grad


def square_tfim_imag_time(
    Lx,
    Ly,
    Jx,
    Jy,
    h,
    backend="mps",
    delta_tau=0.05,
    steps=20,
    max_layers=4,
    max_bond_dim=None,
    svd_cutoff=0.0,
    seed=0,
):
    """Imaginary-time style mapped-lattice 2D TFIM updates via variational proxy.

    This is a projected/variational approximation with identity-metric style
    gradient updates. It is not a full non-unitary exact propagator.
    """
    if Lx < 1 or Ly < 1:
        raise ValueError("square_tfim_imag_time expects Lx >= 1 and Ly >= 1.")
    n_sites = square_site_count(Lx, Ly)
    if n_sites < 2:
        raise ValueError("square_tfim_imag_time expects at least two lattice sites.")
    if steps < 1:
        raise ValueError("steps must be at least one.")
    if max_layers < 1:
        raise ValueError("max_layers must be at least one.")
    if delta_tau <= 0.0:
        raise ValueError("delta_tau must be strictly positive.")

    dev, backend_label = _make_device(n_sites, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)
    params = _square_deterministic_initial_params(Jx, Jy, h, max_layers=max_layers, seed=seed)

    energy_history = []
    magnetization_x_history = []
    magnetization_z_history = []
    nn_zz_horizontal_history = []
    nn_zz_vertical_history = []

    current = _square_observable_values(dev, Lx, Ly, Jx, Jy, h, params)
    energy_history.append(float(current["energy"]))
    magnetization_x_history.append(float(current["magnetization_x"]))
    magnetization_z_history.append(float(current["magnetization_z"]))
    nn_zz_horizontal_history.append(float(current["nn_zz_horizontal"]))
    nn_zz_vertical_history.append(float(current["nn_zz_vertical"]))

    converged = False
    final_delta_energy = 0.0
    tol = 1e-8

    for _ in range(steps):
        grad = _square_tfim_imag_gradient(dev, Lx, Ly, Jx, Jy, h, params)
        candidate_params = []
        for (gx, gy, b), (dgx, dgy, db) in zip(params, grad):
            candidate_params.append(
                (
                    float(gx - delta_tau * dgx),
                    float(gy - delta_tau * dgy),
                    float(b - delta_tau * db),
                )
            )

        candidate = _square_observable_values(dev, Lx, Ly, Jx, Jy, h, candidate_params)
        delta = float(current["energy"] - candidate["energy"])
        final_delta_energy = float(delta)
        params = candidate_params
        current = candidate

        energy_history.append(float(current["energy"]))
        magnetization_x_history.append(float(current["magnetization_x"]))
        magnetization_z_history.append(float(current["magnetization_z"]))
        nn_zz_horizontal_history.append(float(current["nn_zz_horizontal"]))
        nn_zz_vertical_history.append(float(current["nn_zz_vertical"]))

        if delta >= 0.0 and abs(delta) <= tol:
            converged = True
            break

    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "n_sites": int(n_sites),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "h": float(h),
        "backend": backend_label,
        "delta_tau": float(delta_tau),
        "steps": int(steps),
        "energy_history": energy_history,
        "magnetization_x_history": magnetization_x_history,
        "magnetization_z_history": magnetization_z_history,
        "nn_zz_horizontal_history": nn_zz_horizontal_history,
        "nn_zz_vertical_history": nn_zz_vertical_history,
        "converged": bool(converged),
        "final_delta_energy": float(final_delta_energy),
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
        "seed": int(seed),
    }


def compare_square_tfim_real_time_exact_vs_mps(
    Lx,
    Ly,
    Jx,
    Jy,
    h,
    dt=0.05,
    steps=20,
    max_bond_dim=8,
    svd_cutoff=1e-12,
    seed=0,
):
    """Compare mapped-lattice square TFIM real-time dynamics between exact and MPS."""
    exact = square_tfim_real_time(
        Lx=Lx,
        Ly=Ly,
        Jx=Jx,
        Jy=Jy,
        h=h,
        backend="qml",
        dt=dt,
        steps=steps,
        seed=seed,
    )
    mps = square_tfim_real_time(
        Lx=Lx,
        Ly=Ly,
        Jx=Jx,
        Jy=Jy,
        h=h,
        backend="mps",
        dt=dt,
        steps=steps,
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        seed=seed,
    )

    diffs = [abs(me - ee) for ee, me in zip(exact["energy_history"], mps["energy_history"])]
    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "n_sites": int(exact["n_sites"]),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "h": float(h),
        "exact": exact,
        "mps": mps,
        "abs_energy_error": float(abs(mps["energy_history"][-1] - exact["energy_history"][-1])),
        "abs_energy_error_per_site": float(abs(mps["energy_history"][-1] - exact["energy_history"][-1]) / exact["n_sites"]),
        "max_abs_energy_error_over_time": float(max(diffs) if diffs else 0.0),
    }


def compare_square_tfim_imag_time_exact_vs_mps(
    Lx,
    Ly,
    Jx,
    Jy,
    h,
    delta_tau=0.05,
    steps=20,
    max_layers=4,
    max_bond_dim=8,
    svd_cutoff=1e-12,
    seed=0,
):
    """Compare mapped-lattice square TFIM imaginary-time proxy updates between exact and MPS."""
    exact = square_tfim_imag_time(
        Lx=Lx,
        Ly=Ly,
        Jx=Jx,
        Jy=Jy,
        h=h,
        backend="qml",
        delta_tau=delta_tau,
        steps=steps,
        max_layers=max_layers,
        seed=seed,
    )
    mps = square_tfim_imag_time(
        Lx=Lx,
        Ly=Ly,
        Jx=Jx,
        Jy=Jy,
        h=h,
        backend="mps",
        delta_tau=delta_tau,
        steps=steps,
        max_layers=max_layers,
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        seed=seed,
    )
    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "n_sites": int(exact["n_sites"]),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "h": float(h),
        "exact": exact,
        "mps": mps,
        "abs_energy_error": float(abs(mps["energy_history"][-1] - exact["energy_history"][-1])),
        "abs_energy_error_per_site": float(abs(mps["energy_history"][-1] - exact["energy_history"][-1]) / exact["n_sites"]),
        "abs_magnetization_x_error": float(
            abs(mps["magnetization_x_history"][-1] - exact["magnetization_x_history"][-1])
        ),
    }


def _apply_cubic_variational_layer(n_sites, x_pairs, y_pairs, z_pairs, gamma_x, gamma_y, gamma_z, beta):
    for wire_a, wire_b in x_pairs:
        qml.CNOT(wires=[wire_a, wire_b])
        qml.RZ(2.0 * gamma_x, wires=wire_b)
        qml.CNOT(wires=[wire_a, wire_b])

    for wire_a, wire_b in y_pairs:
        qml.CNOT(wires=[wire_a, wire_b])
        qml.RZ(2.0 * gamma_y, wires=wire_b)
        qml.CNOT(wires=[wire_a, wire_b])

    for wire_a, wire_b in z_pairs:
        qml.CNOT(wires=[wire_a, wire_b])
        qml.RZ(2.0 * gamma_z, wires=wire_b)
        qml.CNOT(wires=[wire_a, wire_b])

    for wire in range(n_sites):
        qml.RX(2.0 * beta, wires=wire)


def _apply_cubic_variational_ansatz(n_sites, x_pairs, y_pairs, z_pairs, layer_params):
    for wire in range(n_sites):
        qml.Hadamard(wires=wire)

    for gamma_x, gamma_y, gamma_z, beta in layer_params:
        _apply_cubic_variational_layer(n_sites, x_pairs, y_pairs, z_pairs, gamma_x, gamma_y, gamma_z, beta)


def _cubic_deterministic_initial_params(Jx, Jy, Jz, h, max_layers, seed):
    seed = int(seed)
    rng = np.random.default_rng(seed)
    params = []
    for _ in range(max_layers):
        jitter_x = float(rng.uniform(-0.02, 0.02))
        jitter_y = float(rng.uniform(-0.02, 0.02))
        jitter_z = float(rng.uniform(-0.02, 0.02))
        jitter_b = float(rng.uniform(-0.02, 0.02))
        params.append(
            (
                float(0.35 * Jx + 0.1 * jitter_x),
                float(0.35 * Jy + 0.1 * jitter_y),
                float(0.35 * Jz + 0.1 * jitter_z),
                float(0.35 * h + 0.05 * jitter_b),
            )
        )
    return params


def _cubic_tfim_hamiltonian(Lx, Ly, Lz, Jx, Jy, Jz, h):
    n_sites = cubic_site_count(Lx, Ly, Lz)
    x_pairs = cubic_x_pairs(Lx, Ly, Lz)
    y_pairs = cubic_y_pairs(Lx, Ly, Lz)
    z_pairs = cubic_z_pairs(Lx, Ly, Lz)

    coeffs = []
    ops = []
    for wire_a, wire_b in x_pairs:
        coeffs.append(float(-Jx))
        ops.append(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b))
    for wire_a, wire_b in y_pairs:
        coeffs.append(float(-Jy))
        ops.append(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b))
    for wire_a, wire_b in z_pairs:
        coeffs.append(float(-Jz))
        ops.append(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b))
    for wire in range(n_sites):
        coeffs.append(float(-h))
        ops.append(qml.PauliX(wire))
    return qml.dot(coeffs, ops)


def _cubic_observable_values(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, layer_params):
    n_sites = cubic_site_count(Lx, Ly, Lz)
    x_pairs = cubic_x_pairs(Lx, Ly, Lz)
    y_pairs = cubic_y_pairs(Lx, Ly, Lz)
    z_pairs = cubic_z_pairs(Lx, Ly, Lz)
    hamiltonian = _cubic_tfim_hamiltonian(Lx, Ly, Lz, Jx, Jy, Jz, h)

    @qml.qnode(dev)
    def energy_circuit():
        _apply_cubic_variational_ansatz(n_sites, x_pairs, y_pairs, z_pairs, layer_params)
        return qml.expval(hamiltonian)

    @qml.qnode(dev)
    def magnetization_x_circuit():
        _apply_cubic_variational_ansatz(n_sites, x_pairs, y_pairs, z_pairs, layer_params)
        return [qml.expval(qml.PauliX(wire)) for wire in range(n_sites)]

    @qml.qnode(dev)
    def magnetization_z_circuit():
        _apply_cubic_variational_ansatz(n_sites, x_pairs, y_pairs, z_pairs, layer_params)
        return [qml.expval(qml.PauliZ(wire)) for wire in range(n_sites)]

    @qml.qnode(dev)
    def x_zz_circuit():
        _apply_cubic_variational_ansatz(n_sites, x_pairs, y_pairs, z_pairs, layer_params)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in x_pairs]

    @qml.qnode(dev)
    def y_zz_circuit():
        _apply_cubic_variational_ansatz(n_sites, x_pairs, y_pairs, z_pairs, layer_params)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in y_pairs]

    @qml.qnode(dev)
    def z_zz_circuit():
        _apply_cubic_variational_ansatz(n_sites, x_pairs, y_pairs, z_pairs, layer_params)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in z_pairs]

    energy = float(energy_circuit())
    mx_values = np.asarray(magnetization_x_circuit(), dtype=float)
    mz_values = np.asarray(magnetization_z_circuit(), dtype=float)
    xzz_values = np.asarray(x_zz_circuit(), dtype=float) if x_pairs else np.asarray([0.0])
    yzz_values = np.asarray(y_zz_circuit(), dtype=float) if y_pairs else np.asarray([0.0])
    zzz_values = np.asarray(z_zz_circuit(), dtype=float) if z_pairs else np.asarray([0.0])
    return {
        "energy": float(energy),
        "magnetization_x": float(np.mean(mx_values)),
        "magnetization_z": float(np.mean(mz_values)),
        "nn_zz_x": float(np.mean(xzz_values)),
        "nn_zz_y": float(np.mean(yzz_values)),
        "nn_zz_z": float(np.mean(zzz_values)),
    }


def cubic_tfim_observables(
    Lx,
    Ly,
    Lz,
    Jx,
    Jy,
    Jz,
    h,
    backend="mps",
    max_bond_dim=None,
    svd_cutoff=0.0,
    seed=0,
):
    """Evaluate mapped-lattice 3D cubic TFIM observables on exact or MPS backends.

    Target model on open boundaries:
    ``H_3D = -Jx sum_<i,j>_x Z_i Z_j - Jy sum_<i,j>_y Z_i Z_j - Jz sum_<i,j>_z Z_i Z_j - h sum_i X_i``

    Lattice-to-wire mapping is row-major by plane:
    ``s(x,y,z) = x + Lx*y + Lx*Ly*z``.

    Current implementation uses deterministic fixed mapped-lattice ansatz layers;
    it is a proxy low-energy workflow, not a certified exact ground-state solver.
    """
    if Lx < 1 or Ly < 1 or Lz < 1:
        raise ValueError("cubic_tfim_observables expects Lx >= 1, Ly >= 1, and Lz >= 1.")
    n_sites = cubic_site_count(Lx, Ly, Lz)
    if n_sites < 2:
        raise ValueError("cubic_tfim_observables expects at least two lattice sites.")

    layer_params = _cubic_deterministic_initial_params(Jx, Jy, Jz, h, max_layers=1, seed=seed)
    dev, backend_label = _make_device(n_sites, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)
    obs = _cubic_observable_values(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, layer_params)

    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "Lz": int(Lz),
        "n_sites": int(n_sites),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "Jz": float(Jz),
        "h": float(h),
        "backend": backend_label,
        "energy": float(obs["energy"]),
        "energy_per_site": float(obs["energy"] / n_sites),
        "magnetization_x": float(obs["magnetization_x"]),
        "magnetization_z": float(obs["magnetization_z"]),
        "nn_zz_x": float(obs["nn_zz_x"]),
        "nn_zz_y": float(obs["nn_zz_y"]),
        "nn_zz_z": float(obs["nn_zz_z"]),
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
    }


def compare_cubic_tfim_exact_vs_mps(
    Lx,
    Ly,
    Lz,
    Jx,
    Jy,
    Jz,
    h,
    max_bond_dim=8,
    svd_cutoff=1e-12,
    seed=0,
):
    """Compare mapped-lattice 3D cubic TFIM observables between exact and MPS backends."""
    exact = cubic_tfim_observables(
        Lx=Lx,
        Ly=Ly,
        Lz=Lz,
        Jx=Jx,
        Jy=Jy,
        Jz=Jz,
        h=h,
        backend="qml",
        seed=seed,
    )
    mps = cubic_tfim_observables(
        Lx=Lx,
        Ly=Ly,
        Lz=Lz,
        Jx=Jx,
        Jy=Jy,
        Jz=Jz,
        h=h,
        backend="mps",
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        seed=seed,
    )
    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "Lz": int(Lz),
        "n_sites": int(exact["n_sites"]),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "Jz": float(Jz),
        "h": float(h),
        "exact_energy": float(exact["energy"]),
        "mps_energy": float(mps["energy"]),
        "abs_energy_error": float(abs(mps["energy"] - exact["energy"])),
        "abs_energy_error_per_site": float(abs(mps["energy"] - exact["energy"]) / exact["n_sites"]),
        "exact_magnetization_x": float(exact["magnetization_x"]),
        "mps_magnetization_x": float(mps["magnetization_x"]),
        "abs_magnetization_x_error": float(abs(mps["magnetization_x"] - exact["magnetization_x"])),
        "exact": exact,
        "mps": mps,
    }


def _cubic_tfim_real_time_step(n_sites, x_pairs, y_pairs, z_pairs, Jx, Jy, Jz, h, dt):
    gamma_x = float(-Jx * dt)
    gamma_y = float(-Jy * dt)
    gamma_z = float(-Jz * dt)
    beta = float(-h * dt)
    _apply_cubic_variational_layer(n_sites, x_pairs, y_pairs, z_pairs, gamma_x, gamma_y, gamma_z, beta)


def _cubic_tfim_real_time_observables(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, dt, step):
    n_sites = cubic_site_count(Lx, Ly, Lz)
    x_pairs = cubic_x_pairs(Lx, Ly, Lz)
    y_pairs = cubic_y_pairs(Lx, Ly, Lz)
    z_pairs = cubic_z_pairs(Lx, Ly, Lz)
    hamiltonian = _cubic_tfim_hamiltonian(Lx, Ly, Lz, Jx, Jy, Jz, h)

    @qml.qnode(dev)
    def energy_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _cubic_tfim_real_time_step(n_sites, x_pairs, y_pairs, z_pairs, Jx, Jy, Jz, h, dt)
        return qml.expval(hamiltonian)

    @qml.qnode(dev)
    def magnetization_x_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _cubic_tfim_real_time_step(n_sites, x_pairs, y_pairs, z_pairs, Jx, Jy, Jz, h, dt)
        return [qml.expval(qml.PauliX(wire)) for wire in range(n_sites)]

    @qml.qnode(dev)
    def magnetization_z_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _cubic_tfim_real_time_step(n_sites, x_pairs, y_pairs, z_pairs, Jx, Jy, Jz, h, dt)
        return [qml.expval(qml.PauliZ(wire)) for wire in range(n_sites)]

    @qml.qnode(dev)
    def x_zz_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _cubic_tfim_real_time_step(n_sites, x_pairs, y_pairs, z_pairs, Jx, Jy, Jz, h, dt)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in x_pairs]

    @qml.qnode(dev)
    def y_zz_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _cubic_tfim_real_time_step(n_sites, x_pairs, y_pairs, z_pairs, Jx, Jy, Jz, h, dt)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in y_pairs]

    @qml.qnode(dev)
    def z_zz_circuit():
        for wire in range(n_sites):
            qml.Hadamard(wires=wire)
        for _ in range(step):
            _cubic_tfim_real_time_step(n_sites, x_pairs, y_pairs, z_pairs, Jx, Jy, Jz, h, dt)
        return [qml.expval(qml.PauliZ(wire_a) @ qml.PauliZ(wire_b)) for wire_a, wire_b in z_pairs]

    energy = float(energy_circuit())
    mx_values = np.asarray(magnetization_x_circuit(), dtype=float)
    mz_values = np.asarray(magnetization_z_circuit(), dtype=float)
    xzz_values = np.asarray(x_zz_circuit(), dtype=float) if x_pairs else np.asarray([0.0])
    yzz_values = np.asarray(y_zz_circuit(), dtype=float) if y_pairs else np.asarray([0.0])
    zzz_values = np.asarray(z_zz_circuit(), dtype=float) if z_pairs else np.asarray([0.0])
    return {
        "energy": float(energy),
        "magnetization_x": float(np.mean(mx_values)),
        "magnetization_z": float(np.mean(mz_values)),
        "nn_zz_x": float(np.mean(xzz_values)),
        "nn_zz_y": float(np.mean(yzz_values)),
        "nn_zz_z": float(np.mean(zzz_values)),
    }


def cubic_tfim_real_time(
    Lx,
    Ly,
    Lz,
    Jx,
    Jy,
    Jz,
    h,
    backend="mps",
    dt=0.05,
    steps=20,
    max_bond_dim=None,
    svd_cutoff=0.0,
    seed=0,
):
    """Real-time mapped-lattice 3D TFIM dynamics with first-order Trotter updates.

    Continuous target is ``|psi(t)> = exp(-i H_3D t)|psi0>``.
    Current implementation is a deterministic mapped-lattice Trotterized path.
    """
    if Lx < 1 or Ly < 1 or Lz < 1:
        raise ValueError("cubic_tfim_real_time expects Lx >= 1, Ly >= 1, and Lz >= 1.")
    n_sites = cubic_site_count(Lx, Ly, Lz)
    if n_sites < 2:
        raise ValueError("cubic_tfim_real_time expects at least two lattice sites.")
    if steps < 1:
        raise ValueError("steps must be at least one.")
    if dt <= 0.0:
        raise ValueError("dt must be strictly positive.")

    dev, backend_label = _make_device(n_sites, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)

    time_history = []
    energy_history = []
    magnetization_x_history = []
    magnetization_z_history = []
    nn_zz_x_history = []
    nn_zz_y_history = []
    nn_zz_z_history = []

    for step in range(steps + 1):
        obs = _cubic_tfim_real_time_observables(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, dt, step)
        time_history.append(float(step * dt))
        energy_history.append(float(obs["energy"]))
        magnetization_x_history.append(float(obs["magnetization_x"]))
        magnetization_z_history.append(float(obs["magnetization_z"]))
        nn_zz_x_history.append(float(obs["nn_zz_x"]))
        nn_zz_y_history.append(float(obs["nn_zz_y"]))
        nn_zz_z_history.append(float(obs["nn_zz_z"]))

    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "Lz": int(Lz),
        "n_sites": int(n_sites),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "Jz": float(Jz),
        "h": float(h),
        "backend": backend_label,
        "dt": float(dt),
        "steps": int(steps),
        "time_history": time_history,
        "energy_history": energy_history,
        "magnetization_x_history": magnetization_x_history,
        "magnetization_z_history": magnetization_z_history,
        "nn_zz_x_history": nn_zz_x_history,
        "nn_zz_y_history": nn_zz_y_history,
        "nn_zz_z_history": nn_zz_z_history,
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
        "seed": int(seed),
    }


def _cubic_tfim_imag_gradient(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, params):
    shift = math.pi / 4.0
    grad = []
    for layer_idx in range(len(params)):
        grad_layer = []
        for param_idx in range(4):
            plus_params = list(params)
            minus_params = list(params)
            p_plus = list(plus_params[layer_idx])
            p_minus = list(minus_params[layer_idx])
            p_plus[param_idx] += shift
            p_minus[param_idx] -= shift
            plus_params[layer_idx] = tuple(p_plus)
            minus_params[layer_idx] = tuple(p_minus)
            energy_plus = _cubic_observable_values(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, plus_params)["energy"]
            energy_minus = _cubic_observable_values(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, minus_params)["energy"]
            grad_layer.append(float(0.5 * (energy_plus - energy_minus)))
        grad.append(tuple(grad_layer))
    return grad


def cubic_tfim_imag_time(
    Lx,
    Ly,
    Lz,
    Jx,
    Jy,
    Jz,
    h,
    backend="mps",
    delta_tau=0.05,
    steps=20,
    max_layers=4,
    max_bond_dim=None,
    svd_cutoff=0.0,
    seed=0,
):
    """Imaginary-time style mapped-lattice 3D TFIM updates via variational proxy.

    This is a projected/variational approximation with identity-metric style
    gradient updates. It is not a full non-unitary exact propagator.
    """
    if Lx < 1 or Ly < 1 or Lz < 1:
        raise ValueError("cubic_tfim_imag_time expects Lx >= 1, Ly >= 1, and Lz >= 1.")
    n_sites = cubic_site_count(Lx, Ly, Lz)
    if n_sites < 2:
        raise ValueError("cubic_tfim_imag_time expects at least two lattice sites.")
    if steps < 1:
        raise ValueError("steps must be at least one.")
    if max_layers < 1:
        raise ValueError("max_layers must be at least one.")
    if delta_tau <= 0.0:
        raise ValueError("delta_tau must be strictly positive.")

    dev, backend_label = _make_device(n_sites, backend, max_bond_dim=max_bond_dim, svd_cutoff=svd_cutoff)
    params = _cubic_deterministic_initial_params(Jx, Jy, Jz, h, max_layers=max_layers, seed=seed)

    energy_history = []
    magnetization_x_history = []
    magnetization_z_history = []
    nn_zz_x_history = []
    nn_zz_y_history = []
    nn_zz_z_history = []

    current = _cubic_observable_values(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, params)
    energy_history.append(float(current["energy"]))
    magnetization_x_history.append(float(current["magnetization_x"]))
    magnetization_z_history.append(float(current["magnetization_z"]))
    nn_zz_x_history.append(float(current["nn_zz_x"]))
    nn_zz_y_history.append(float(current["nn_zz_y"]))
    nn_zz_z_history.append(float(current["nn_zz_z"]))

    converged = False
    final_delta_energy = 0.0
    tol = 1e-8

    for _ in range(steps):
        grad = _cubic_tfim_imag_gradient(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, params)
        candidate_params = []
        for (gx, gy, gz, b), (dgx, dgy, dgz, db) in zip(params, grad):
            candidate_params.append(
                (
                    float(gx - delta_tau * dgx),
                    float(gy - delta_tau * dgy),
                    float(gz - delta_tau * dgz),
                    float(b - delta_tau * db),
                )
            )

        candidate = _cubic_observable_values(dev, Lx, Ly, Lz, Jx, Jy, Jz, h, candidate_params)
        delta = float(current["energy"] - candidate["energy"])
        final_delta_energy = float(delta)
        params = candidate_params
        current = candidate

        energy_history.append(float(current["energy"]))
        magnetization_x_history.append(float(current["magnetization_x"]))
        magnetization_z_history.append(float(current["magnetization_z"]))
        nn_zz_x_history.append(float(current["nn_zz_x"]))
        nn_zz_y_history.append(float(current["nn_zz_y"]))
        nn_zz_z_history.append(float(current["nn_zz_z"]))

        if delta >= 0.0 and abs(delta) <= tol:
            converged = True
            break

    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "Lz": int(Lz),
        "n_sites": int(n_sites),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "Jz": float(Jz),
        "h": float(h),
        "backend": backend_label,
        "delta_tau": float(delta_tau),
        "steps": int(steps),
        "energy_history": energy_history,
        "magnetization_x_history": magnetization_x_history,
        "magnetization_z_history": magnetization_z_history,
        "nn_zz_x_history": nn_zz_x_history,
        "nn_zz_y_history": nn_zz_y_history,
        "nn_zz_z_history": nn_zz_z_history,
        "converged": bool(converged),
        "final_delta_energy": float(final_delta_energy),
        "max_bond_dim": None if backend_label == "qml" else max_bond_dim,
        "svd_cutoff": float(svd_cutoff),
        "seed": int(seed),
    }


def compare_cubic_tfim_real_time_exact_vs_mps(
    Lx,
    Ly,
    Lz,
    Jx,
    Jy,
    Jz,
    h,
    dt=0.05,
    steps=20,
    max_bond_dim=8,
    svd_cutoff=1e-12,
    seed=0,
):
    """Compare mapped-lattice cubic TFIM real-time dynamics between exact and MPS."""
    exact = cubic_tfim_real_time(
        Lx=Lx,
        Ly=Ly,
        Lz=Lz,
        Jx=Jx,
        Jy=Jy,
        Jz=Jz,
        h=h,
        backend="qml",
        dt=dt,
        steps=steps,
        seed=seed,
    )
    mps = cubic_tfim_real_time(
        Lx=Lx,
        Ly=Ly,
        Lz=Lz,
        Jx=Jx,
        Jy=Jy,
        Jz=Jz,
        h=h,
        backend="mps",
        dt=dt,
        steps=steps,
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        seed=seed,
    )

    diffs = [abs(me - ee) for ee, me in zip(exact["energy_history"], mps["energy_history"])]
    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "Lz": int(Lz),
        "n_sites": int(exact["n_sites"]),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "Jz": float(Jz),
        "h": float(h),
        "exact": exact,
        "mps": mps,
        "abs_energy_error": float(abs(mps["energy_history"][-1] - exact["energy_history"][-1])),
        "abs_energy_error_per_site": float(abs(mps["energy_history"][-1] - exact["energy_history"][-1]) / exact["n_sites"]),
        "max_abs_energy_error_over_time": float(max(diffs) if diffs else 0.0),
    }


def compare_cubic_tfim_imag_time_exact_vs_mps(
    Lx,
    Ly,
    Lz,
    Jx,
    Jy,
    Jz,
    h,
    delta_tau=0.05,
    steps=20,
    max_layers=4,
    max_bond_dim=8,
    svd_cutoff=1e-12,
    seed=0,
):
    """Compare mapped-lattice cubic TFIM imaginary-time proxy updates between exact and MPS."""
    exact = cubic_tfim_imag_time(
        Lx=Lx,
        Ly=Ly,
        Lz=Lz,
        Jx=Jx,
        Jy=Jy,
        Jz=Jz,
        h=h,
        backend="qml",
        delta_tau=delta_tau,
        steps=steps,
        max_layers=max_layers,
        seed=seed,
    )
    mps = cubic_tfim_imag_time(
        Lx=Lx,
        Ly=Ly,
        Lz=Lz,
        Jx=Jx,
        Jy=Jy,
        Jz=Jz,
        h=h,
        backend="mps",
        delta_tau=delta_tau,
        steps=steps,
        max_layers=max_layers,
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        seed=seed,
    )
    return {
        "Lx": int(Lx),
        "Ly": int(Ly),
        "Lz": int(Lz),
        "n_sites": int(exact["n_sites"]),
        "Jx": float(Jx),
        "Jy": float(Jy),
        "Jz": float(Jz),
        "h": float(h),
        "exact": exact,
        "mps": mps,
        "abs_energy_error": float(abs(mps["energy_history"][-1] - exact["energy_history"][-1])),
        "abs_energy_error_per_site": float(abs(mps["energy_history"][-1] - exact["energy_history"][-1]) / exact["n_sites"]),
        "abs_magnetization_x_error": float(
            abs(mps["magnetization_x_history"][-1] - exact["magnetization_x_history"][-1])
        ),
    }
