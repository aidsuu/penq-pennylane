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
