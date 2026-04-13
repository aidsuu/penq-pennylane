# PenQ Dual-Backend Research Pack

`penq` is a deterministic PennyLane research pack built around two public backends:
- `penq.qml_starter`
- `penq.mps_starter`

## Project Status

Public release: `1.1.0`

The current public package release keeps the public plugin names stable while the internal runtime milestone for this work is `v8.1`:
- a stable analytic statevector backend with the public device name `penq.qml_starter`
- an analytic MPS backend with the public device name `penq.mps_starter`
- a compact set of deterministic research workflows, scans, comparisons, and CSV-producing analysis helpers

## Research Pack Status

- both runtime devices remain analytic-only
- no new runtime dependency is required beyond PennyLane
- examples are deterministic and intended for reproducible small and medium-scale studies
- CSV-producing workflows now form a stable analysis layer on top of the backend
- campaign-level orchestration is available for generating multiple CSV analysis artifacts in one run
- campaign summaries are available for quick analysis before plotting
- both TFIM and QAOA now have campaign-level orchestration and summary layers
- a cross-campaign comparative report layer is available for compact combined analysis
- a large-scale TFIM campaign is available for larger deterministic full-statevector batch runs
- practical scale is still bounded by full-statevector memory
- `penq.mps_starter` now has a wider local two-qubit runtime subset than the original public release
- the repository now includes an official adaptive TFIM variational solver with CSV-ready and plot-ready workflows

## Backend And Runtime

## Backend Comparison

| Backend Name | Exact Or Approximate | Truncation Support | Good Fit |
| --- | --- | --- | --- |
| `penq.qml_starter` | Exact | None | exact baselines, exact reference energies, plugin validation, small Hamiltonian studies |
| `penq.mps_starter` | Exact for sufficiently large retained bond dimension, approximate under truncation | `max_bond_dim`, `svd_cutoff` | bond-dimension studies, truncation scans, approximate 1D circuit studies, general Pauli-word comparisons |

## Choosing A Backend

- Use `penq.qml_starter` when you need exact reference results, exact states, or exact-vs-approximate comparisons.
- Use `penq.mps_starter` when you want to study truncation error, bond-dimension effects, or approximate tensor-network behavior.
- Start with `penq.qml_starter` for correctness, then compare against `penq.mps_starter` when moving into larger or truncation-oriented workflows.
- Prefer the comparative MPS workflows when deciding whether a given `max_bond_dim` is adequate for a circuit family.

### Public Device

- public device name: `penq.qml_starter`
- wires: `1..30`
- execution mode: analytic only
- shots must be `None` or `0`

## Tensor / MPS Device

`penq.mps_starter` is a separate minimal tensor-network backend intended as a starter MPS runtime.

- public device name: `penq.mps_starter`
- state representation: list of local MPS tensors
- initialization: `|0...0>`
- execution mode: analytic only
- shots must be `None` or `0`
- supported gates:
  - `PauliX`
  - `PauliY`
  - `PauliZ`
  - `Hadamard`
  - `RX`
  - `RY`
  - `RZ`
  - `CNOT` including internally routed non-nearest-neighbor cases
  - `CZ`
  - `PauliRot` on supported one-wire and two-wire Pauli words
  - `IsingZZ`
  - `IsingXX`
  - `IsingYY`
- supported measurements:
  - `qml.state()`
  - `qml.expval(qml.PauliX(wire))`
  - `qml.expval(qml.PauliY(wire))`
  - `qml.expval(qml.PauliZ(wire))`
  - arbitrary Pauli-word tensor products of `X`, `Y`, and `Z` on distinct wires
  - small linear combinations via `observable.terms()` when every term is a supported Pauli word
- current scope is intentionally minimal and pure NumPy

## MPS General Pauli Support

`penq.mps_starter` now supports direct expectation values for Pauli words on distinct wires without building a full dense `2^n x 2^n` operator.

- single-wire `PauliX`, `PauliY`, and `PauliZ`
- multi-wire tensor products such as `X(0) @ Y(2) @ Z(5)`
- small linear combinations of supported Pauli words via `observable.terms()`

Expectation values are evaluated directly from the MPS representation.

## MPS Routed Two-Qubit Gates

`penq.mps_starter` now supports a generic adjacent two-qubit update path plus explicit routing for non-nearest-neighbor cases.

- adjacent updates contract two tensors, apply a local `4x4` unitary, and split back with SVD
- the split path respects `max_bond_dim` and `svd_cutoff`
- non-nearest-neighbor two-qubit gates are routed internally with adjacent `SWAP` steps and then restored
- this widens the usable circuit class without exposing `SWAP` as a new public gate

## MPS General Two-Qubit Gates

`penq.mps_starter` now includes a generic nearest-neighbor two-qubit gate engine for local `4x4` unitaries.

- no dense global statevector is built during the update path
- the local engine is reused by adjacent `CNOT`, `CZ`, `IsingZZ`, `IsingXX`, `IsingYY`, and supported two-wire `PauliRot`
- routed non-nearest-neighbor two-qubit gates reuse the same local engine after explicit `SWAP` routing

## Native PauliRot / Ising Support

`penq.mps_starter` now supports additional native runtime operations relevant to PennyLane workflows.

- `qml.CZ`
- `qml.PauliRot` for one-wire and two-wire Pauli words with at most two non-identity local factors
- `qml.IsingZZ`
- `qml.IsingXX`
- `qml.IsingYY`

Operations outside this subset still fail explicitly.

## MPS Time Evolution

The repository now includes a deterministic TFIM time-evolution workflow built on top of `penq.mps_starter`.

- first-order Trotter / TEBD-like splitting
- nearest-neighbor `ZZ` evolution implemented from supported gates
- single-site transverse-field `X` evolution implemented from supported gates
- safe sizes such as `8` and `10`
- fixed `dt`, fixed number of steps, and stable CSV output for simple dynamics analysis

## MPS Trotter Order Studies

The repository also includes a deterministic comparison between first-order and second-order Trotterization for TFIM dynamics on `penq.mps_starter`.

- fixed total evolution time
- multiple deterministic `dt` values
- both first-order and second-order splitting
- stable CSV output for comparing observable drift versus `dt`

## Exact vs MPS Time Evolution

The repository also includes a direct exact-vs-MPS validation workflow for TFIM quench dynamics.

- compares `penq.qml_starter` and `penq.mps_starter`
- covers first-order and second-order Trotterization
- uses matched circuits, matched `dt`, and matched total evolution time
- reports observable-level errors for `Z0` and `Z0Z1`

## Dynamical Error Maps

The repository also includes a compact error-map layer for TFIM quench dynamics.

- built directly from the exact-vs-MPS TFIM quench comparison
- scans `h`, `dt`, `trotter_order`, and `max_bond_dim`
- writes a reduced CSV focused on observable errors
- intended for downstream analysis of error versus time-step and bond dimension

## Dynamical Threshold Studies

The repository also includes a threshold-selection layer on top of the TFIM quench dynamical error map.

- reads the error-map CSV directly
- determines the minimum bond dimension that satisfies fixed error thresholds
- reports thresholds separately for `Z0` and `Z0Z1`
- writes a compact CSV for bond-dimension selection across time-evolution settings

## MPS Truncation Controls

`penq.mps_starter` now supports two optional SVD truncation controls for its internal adjacent two-qubit updates:

- `max_bond_dim`
  - `None` keeps the full split rank
  - a positive integer caps the retained bond dimension after SVD
- `svd_cutoff`
  - singular values less than or equal to this cutoff are dropped
  - `0.0` keeps all singular values before any `max_bond_dim` cap is applied

The current truncation policy is:

- apply cutoff first
- keep at least one singular value
- then apply `max_bond_dim` if provided

## MPS vs Statevector Studies

The repository now includes a deterministic comparison workflow between:

- `penq.qml_starter`
- `penq.mps_starter`

The current study uses a simple nearest-neighbor `ZZ` chain energy on a deterministic entangling circuit and reports truncation error across:

- safe sizes such as `6, 8, 10`
- fixed `h` values
- multiple `max_bond_dim` and `svd_cutoff` settings

## MPS Truncation Studies

The repository also includes a TFIM-style truncation study focused on `penq.mps_starter` against a `penq.qml_starter` reference.

- safe sizes such as `8, 10, 12`
- fixed `h` values
- multiple `max_bond_dim` and `svd_cutoff` settings
- CSV output includes both total absolute error and per-site error

## MPS Depth vs Bond Studies

The repository also includes a deterministic study of how layered circuit depth interacts with MPS truncation.

- safe sizes such as `8` and `10`
- fixed depth values
- multiple `max_bond_dim` settings
- comparison against a `penq.qml_starter` reference
- CSV output includes both total and per-site truncation error

## MPS QAOA Truncation Studies

The repository also includes a deterministic QAOA truncation study for `penq.mps_starter` against a `penq.qml_starter` reference.

- open-chain Ising QAOA cost
- safe sizes such as `8` and `10`
- fixed `(gamma, beta)` points
- multiple `max_bond_dim` settings
- CSV output for direct truncation-error analysis

### Supported Gates

- `PauliX`
- `PauliY`
- `PauliZ`
- `Hadamard`
- `RX`
- `RY`
- `RZ`
- `CNOT`
- `CZ`
- `PauliRot` for supported one-wire and two-wire Pauli words
- `IsingZZ`
- `IsingXX`
- `IsingYY`

### Supported Measurements

- `qml.state()`
- `qml.expval(qml.PauliX(wire))`
- `qml.expval(qml.PauliY(wire))`
- `qml.expval(qml.PauliZ(wire))`
- `qml.expval(...)` for arbitrary Pauli words built from `PauliX`, `PauliY`, and `PauliZ` on distinct wires
- small linear combinations of supported Pauli words

### Runtime Notes

- PennyLane plugin loader and direct instantiation fallback are both supported
- the backend uses in-place statevector updates and does not build dense `2^n x 2^n` operator matrices
- unsupported operations, observables, or measurements fail explicitly with clear error messages

## Practical Limits

The public device target remains up to `30` wires, but the real limit depends on machine RAM because the backend stores the full statevector in memory.

Assumptions:
- `complex128` amplitudes
- `16` bytes per amplitude
- memory shown below is for the raw statevector only

| Wires | Amplitudes | Estimated Memory |
| --- | ---: | ---: |
| 8 | 256 | 4 KiB |
| 12 | 4,096 | 64 KiB |
| 16 | 65,536 | 1 MiB |
| 20 | 1,048,576 | 16 MiB |
| 24 | 16,777,216 | 256 MiB |
| 28 | 268,435,456 | 4 GiB |
| 30 | 1,073,741,824 | 16 GiB |

For routine research workflows, smaller systems are usually more practical than the 30-wire design ceiling.

## Large-Scale Campaigns

The repository also includes a large-scale orchestration layer for larger deterministic TFIM scans.

- `tfim_large_scale_campaign.py` targets larger even system sizes such as `12, 14, 16, 18, 20`.
- The backend remains full-statevector and CPU-oriented.
- Practical scale is still RAM-bound.
- The backend does not use GPU acceleration at this time.
- The intended output is structured CSV for batch analysis rather than interactive tuning.

## Large Numerical Campaigns

The repository also includes larger deterministic batch workflows intended for offline numerical analysis.

- `tfim_exact_large_campaign.py`
  - exact baseline data from `penq.qml_starter`
  - safe sizes such as `8, 10, 12`
  - CSV columns: `n, h, energy, energy_per_site, expval_x0, expval_z0z1`
- `tfim_mps_large_campaign.py`
  - larger MPS-only scan from `penq.mps_starter`
  - sizes such as `12, 16, 20, 24, 28`
  - fixed `max_bond_dim` grid and `svd_cutoff`
  - CSV columns: `n, h, max_bond_dim, svd_cutoff, mps_energy, energy_per_site`

## Exact vs MPS Large Reports

The repository also includes a report layer for the large TFIM campaigns.

- `tfim_exact_vs_mps_large_report.py`
  - reads the CSV outputs from the exact and MPS large campaigns
  - compares only overlap points that exist in both files
  - recomputes the exact reference on those overlap points with `penq.qml_starter` for the same deterministic TFIM-style chain observable used by the MPS campaign
  - reports total and per-site truncation error
  - can also write one comparison CSV for downstream analysis

## MPS Sensitivity Studies

The repository also includes a sensitivity-analysis layer on top of the large exact-vs-MPS report.

- `tfim_mps_sensitivity_report.py`
  - reads the CSV produced by `tfim_exact_vs_mps_large_report.py`
  - summarizes truncation error as a function of `h` and `max_bond_dim`
  - identifies minimum-error and maximum-error parameter regions
  - can also write one aggregated CSV with a simple deterministic sensitivity ranking

## MPS Threshold Studies

The repository also includes a threshold-analysis layer for determining a sufficient bond dimension.

- `tfim_mps_threshold_report.py`
  - reads either the exact-vs-MPS report CSV or the sensitivity summary CSV
  - determines the minimum bond dimension that satisfies deterministic error thresholds for each `(n, h)` pair
  - supports both total-error and per-site-error thresholds
  - can also write one aggregated CSV for downstream threshold selection

## Performance Tools

The repository includes deterministic performance utilities separate from the runtime itself.

| File | Purpose | Output |
| --- | --- | --- |
| `examples/performance_scan.py` | Fixed shallow-circuit runtime scan on safe wire counts | Terminal |
| `examples/internal_profile.py` | Internal stage timing for gates, expval path, and end-to-end QNode overhead | Terminal |
| `examples/statevector_size_table.py` | Statevector amplitude and memory scaling table | Terminal |
| `docs/performance_baseline.md` | Recorded baseline and optimization history for shipped and rejected candidates | Markdown document |

### Performance Notes

- runtime grows roughly exponentially with wire count because this is a full statevector backend
- dominant costs are single-qubit gate application, `CNOT`, Pauli-word expectation evaluation, and end-to-end `QNode` overhead
- the official baseline history includes:
  - `v1.3`: shipped `pauli_word_expval` improvement
  - `v1.5`: shipped `CNOT` kernel improvement
  - `v1.7`: single-qubit execute-path candidate evaluated and rejected due to regression

## Research Workflows

The repository also acts as a deterministic workflow pack for small and medium-scale studies.

## Adaptive Variational TFIM Solver

The repository now includes an official adaptive TFIM variational solver exposed through:

- `QML.PenQ.penq_algorithms.adaptive_tfim_vqe`
- `QML.PenQ.penq_algorithms.compare_tfim_vqe_exact_vs_mps`

The solver is deterministic and portable across:

- `penq.qml_starter`
- `penq.mps_starter`

The physical model is the open-chain TFIM Hamiltonian

- `H = -J * sum_i Z_i Z_{i+1} - h * sum_i X_i`

The adaptive ansatz uses only gates that are portable across both public backends:

- initial `Hadamard` preparation
- portable nearest-neighbor ZZ blocks implemented as `CNOT-RZ-CNOT`
- global `RX` mixer rotations

Layer growth is explicit and deterministic:

- start from a shallow base circuit
- add one new `(gamma, beta)` layer at a time
- search each new layer with a deterministic grid
- stop when energy improvement falls below tolerance or `max_layers` is reached

## Adaptive TFIM VQE: Mathematical Formulation

This solver uses explicit TFIM formulas in both code and report docs.

- Hamiltonian:
  - `H = -J sum_i Z_i Z_{i+1} - h sum_i X_i`
- Objective:
  - `E(theta) = <psi(theta)|H|psi(theta)>`
- Per-layer variational block:
  - `U_l(gamma_l, beta_l) = U_X(beta_l) U_ZZ(gamma_l)`
- Full `L`-layer state:
  - `|psi_L> = prod_l U_l |+>^n`
- Adaptive improvement after adding one layer:
  - `Delta_L = E_{L-1}^* - E_L^*`
- Stop rule:
  - `Delta_L <= tol or L == max_layers`

Portable ZZ block identity used on both public backends:

- `CNOT - RZ(2 gamma) - CNOT = exp(-i gamma Z⊗Z)`

The current adaptive solver keeps backend portability by building `U_ZZ` from supported `CNOT` and `RZ` gates rather than relying on backend-specific circuit transforms.

## Variational Imaginary-Time TFIM Solver

Added in `v9.0`, PenQ now includes a deterministic Variational Imaginary-Time Evolution (VITE) style solver: `imaginary_time_tfim`.

Instead of adding layers adaptively, this solver optimizes a fixed-depth ansatz with iterative imaginary-time-inspired updates.

- Theoretical target:
  - `|psi(tau)> = exp(-tau H)|psi0> / ||exp(-tau H)|psi0>||`
- Discrete variational step update for parameters `theta`:
  - `theta_{k+1} = theta_k - delta_tau * grad_E(theta_k)`
- Current approximation used in implementation:
  - identity/diagonal variational metric (`A ~= I`) rather than solving a full dense McLachlan linear system each step
- Gradients `grad_E` are evaluated exactly via a macroscopic parameter-shift rule without relying on backpropagation.
- Energy monotonicity is structurally targeted: the update minimizes energy at each step proportional to `delta_tau`.

Portable ZZ and X blocks identical to the adaptive approach are used, ensuring perfect compatibility with the strict runtime constraints of `penq.mps_starter`.

## Real-Time TFIM Evolution Solver

Added in `v10.0`, PenQ now also includes deterministic real-time TFIM evolution through `real_time_tfim`.

- Continuous target dynamics:
  - `|psi(t)> = exp(-i H t)|psi0>`
- Hamiltonian:
  - `H = -J sum_i Z_i Z_{i+1} - h sum_i X_i`
- Current implementation:
  - first-order Trotterized step updates with portable `ZZ` and `X` blocks that are supported on both `penq.qml_starter` and `penq.mps_starter`

The solver returns trajectory histories for:

- energy
- `expval_x0`
- `expval_z0z1`

as well as the explicit time grid used during evolution.

## TFIM Dynamics Reports

Imaginary-time and real-time TFIM workflows now share one consistent scan CSV schema for dynamics histories:

- `dynamics,n,J,h,backend,step,time,step_size,energy,energy_per_site,expval_x0,expval_z0z1,max_bond_dim,svd_cutoff`

The two report workflows both enforce mandatory PNG and PDF outputs per figure stem.

- Imaginary-time report stems:
  - `imaginary_tfim_energy_vs_step`
  - `imaginary_tfim_exact_vs_mps`
  - `imaginary_tfim_error_vs_max_bond_dim`
- Real-time report stems:
  - `real_tfim_energy_vs_time`
  - `real_tfim_observables_vs_time`
  - `real_tfim_exact_vs_mps`

An additional optional summary report can aggregate final exact-vs-MPS errors across both dynamics modes.

## Scientific Plotting and Reports

The repository now includes a report layer for the adaptive TFIM VQE workflows.

- plotting uses Matplotlib only inside the report script
- `SciencePlots` is used only if available
- when `SciencePlots` is unavailable, the report falls back to a clean Matplotlib style
- plotting is optional and not required for importing or using the runtime devices

## Mandatory Plot Outputs

Adaptive TFIM report plots always save both output formats for each figure stem:

- PNG at `300 dpi`
- PDF

For example, the stem `adaptive_tfim_energy_vs_layer` always produces:

- `adaptive_tfim_energy_vs_layer.png`
- `adaptive_tfim_energy_vs_layer.pdf`

The plotting helper validates that both files exist after save. Missing PNG or PDF output raises an explicit runtime error.

## Optional SciencePlots Without Runtime Dependency

SciencePlots is optional and never required for importing runtime devices or solver code.

- `matplotlib` and `SciencePlots` live in optional plotting extras
- report scripts check explicitly whether `scienceplots` is installed
- if available, the report uses `plt.style.use(["science", "ieee"])`
- if unavailable, the report uses an explicit Matplotlib fallback style
- normal plotting control flow uses explicit validation instead of `try/except`-driven style selection

### Workflow Index

| Example File | Class | Purpose | Output |
| --- | --- | --- | --- |
| `examples/hamiltonian_scan.py` | Exact-only | Basis-state scan for a small 2-qubit Ising Hamiltonian | Terminal |
| `examples/mini_vqe.py` | Exact-only | Deterministic 2-qubit VQE-style grid search | Terminal |
| `examples/two_qubit_spin_scan.py` | Exact-only | Two-qubit mixed-spin Hamiltonian scan using supported observables | Terminal |
| `examples/ising_chain_scan.py` | Exact-only | Open-chain Ising scan on simple deterministic states | Terminal |
| `examples/tfim_scan.py` | Exact-only | TFIM scan on deterministic reference states | Terminal |
| `examples/qaoa_ising_small.py` | Exact-only | Small deterministic p=1 QAOA workflow | Terminal |
| `examples/tfim_scaling_scan.py` | Exact-only | TFIM scaling scan across system size and field values | Terminal + CSV |
| `examples/tfim_finite_size_summary.py` | Exact-only | Finite-size TFIM summary aggregated across system sizes | Terminal + CSV helper |
| `examples/tfim_groundstate_ansatz.py` | Exact-only | Baseline TFIM variational ansatz with reference comparison | Terminal + CSV |
| `examples/tfim_variational_scaling.py` | Exact-only | Comparative TFIM variational scaling across system sizes | Terminal + CSV |
| `examples/tfim_ansatz_comparison.py` | Exact-only | Product-vs-entangling TFIM ansatz comparison | Terminal + CSV |
| `examples/tfim_ansatz_cost_quality.py` | Exact-only | TFIM ansatz cost-versus-quality study with parameter counts | Terminal + CSV |
| `examples/tfim_ansatz_depth_study.py` | Exact-only | TFIM depth comparison across baseline, depth-1, and depth-2 ansatz families | Terminal + CSV |
| `examples/tfim_grid_resolution_study.py` | Exact-only | TFIM grid-resolution study for entangling ansatz families | Terminal + CSV |
| `examples/adaptive_tfim_vqe_demo.py` | Exact-vs-MPS comparative | Deterministic adaptive TFIM VQE demo on the exact and MPS backends | Terminal |
| `examples/adaptive_tfim_vqe_scan.py` | Exact-vs-MPS comparative | Adaptive TFIM VQE layer-by-layer scan with CSV-ready history rows | Terminal + CSV |
| `examples/adaptive_tfim_vqe_report.py` | Exact-vs-MPS comparative | Scientific report and plot generator for adaptive TFIM VQE scan CSVs | Terminal + PNG/PDF + CSV |
| `examples/imaginary_time_tfim_demo.py` | Exact-vs-MPS comparative | Deterministic variational imaginary-time TFIM demo on exact and MPS backends | Terminal |
| `examples/imaginary_time_tfim_scan.py` | Exact-vs-MPS comparative | Imaginary-time TFIM dynamics scan with unified CSV schema | Terminal + CSV |
| `examples/imaginary_time_tfim_report.py` | Exact-vs-MPS comparative | Imaginary-time TFIM report with mandatory PNG/PDF artifact pairs | Terminal + PNG/PDF + CSV |
| `examples/real_time_tfim_demo.py` | Exact-vs-MPS comparative | Deterministic real-time TFIM evolution demo on exact and MPS backends | Terminal |
| `examples/real_time_tfim_scan.py` | Exact-vs-MPS comparative | Real-time TFIM dynamics scan with unified CSV schema | Terminal + CSV |
| `examples/real_time_tfim_report.py` | Exact-vs-MPS comparative | Real-time TFIM dynamics report with energy and observable trajectories | Terminal + PNG/PDF + CSV |
| `examples/tfim_dynamics_comparison_report.py` | Exact-vs-MPS comparative | Optional summary of final exact-vs-MPS errors across imaginary-time and real-time workflows | Terminal + PNG/PDF |
| `examples/tfim_research_campaign.py` | Exact-only | TFIM campaign runner that writes multiple CSV analysis artifacts in one directory | Terminal + multiple CSV |
| `examples/tfim_campaign_summary.py` | Exact-only | Summary reader for campaign outputs with optional aggregated CSV | Terminal + CSV |
| `examples/tfim_large_scale_campaign.py` | Exact-only | Larger-system deterministic TFIM campaign for batch full-statevector scans | Terminal + CSV |
| `examples/tfim_exact_large_campaign.py` | Exact-only | Exact large-batch TFIM baseline campaign for offline analysis | Terminal + CSV |
| `examples/qaoa_research_campaign.py` | Exact-only | QAOA campaign runner that writes grid-search and landscape CSV artifacts | Terminal + multiple CSV |
| `examples/qaoa_campaign_summary.py` | Exact-only | Summary reader for QAOA campaign outputs with optional aggregated CSV | Terminal + CSV |
| `examples/research_report.py` | Exact-only | Cross-campaign report over TFIM and QAOA campaign outputs | Terminal + CSV |
| `examples/qaoa_chain_landscape.py` | Exact-only | Medium-scale p=1 QAOA chain landscape scan | Terminal + CSV |
| `examples/mps_basic_demo.py` | MPS-only | Minimal loader and Bell-state demo for the MPS backend | Terminal |
| `examples/mps_general_pauli_demo.py` | Exact-vs-MPS comparative | General Pauli-word and routed-CNOT demo comparing the MPS backend against the exact backend on a small circuit | Terminal |
| `examples/mps_paulirot_demo.py` | Exact-vs-MPS comparative | Small demo for native `CZ`, `PauliRot`, and Ising-gate agreement between the MPS and exact backends | Terminal |
| `examples/mps_isingzz_quench.py` | MPS-only | Deterministic native `IsingZZ` quench workflow with CSV-ready observable output | Terminal + CSV |
| `examples/mps_tebd_tfim_quench.py` | MPS-only | Deterministic TFIM time evolution using a TEBD-like Trotter split with CSV output for dynamics analysis | Terminal + CSV |
| `examples/mps_trotter_order_study.py` | MPS-only | Deterministic comparison between first-order and second-order TFIM Trotterization at fixed total time | Terminal + CSV |
| `examples/mps_vs_statevector_tfim_quench.py` | Exact-vs-MPS comparative | Deterministic exact-vs-MPS validation for TFIM quench observables across Trotter order, `dt`, and bond dimension | Terminal + CSV |
| `examples/tfim_quench_error_map.py` | Exact-vs-MPS comparative | Reduced error-map workflow for TFIM quench dynamics across `dt`, Trotter order, and bond dimension | Terminal + CSV |
| `examples/tfim_quench_threshold_report.py` | Exact-vs-MPS comparative | Threshold report over TFIM quench error maps to select a sufficient bond dimension for `Z0` and `Z0Z1` | Terminal + CSV |
| `examples/mps_truncation_demo.py` | MPS-only | Minimal truncation-control demo for the MPS backend | Terminal |
| `examples/mps_vs_statevector_tfim.py` | Exact-vs-MPS comparative | Deterministic error study between statevector and MPS chain energies under truncation | Terminal + CSV |
| `examples/tfim_mps_truncation_scan.py` | Exact-vs-MPS comparative | Deterministic TFIM-style truncation error scan for the MPS backend against a statevector reference | Terminal + CSV |
| `examples/mps_depth_bond_study.py` | Exact-vs-MPS comparative | Deterministic study of layered circuit depth versus required MPS bond dimension | Terminal + CSV |
| `examples/qaoa_mps_truncation_scan.py` | Exact-vs-MPS comparative | Deterministic QAOA truncation error scan for the MPS backend against a statevector reference | Terminal + CSV |
| `examples/tfim_exact_vs_mps_large_report.py` | Exact-vs-MPS comparative | Report layer over overlap points from the exact and MPS TFIM large campaigns using an exact chain-energy reference on the matched rows | Terminal + CSV |
| `examples/tfim_mps_sensitivity_report.py` | Exact-vs-MPS comparative | Sensitivity summary over the exact-vs-MPS large TFIM report to identify easy and hard truncation regions | Terminal + CSV |
| `examples/tfim_mps_threshold_report.py` | Exact-vs-MPS comparative | Threshold summary over exact-vs-MPS TFIM errors to identify the minimum bond dimension that is sufficient | Terminal + CSV |
| `examples/tfim_mps_large_campaign.py` | MPS-only | Larger MPS batch campaign for TFIM-style chain scans across bond dimensions | Terminal + CSV |

### Workflow Families

#### Reference And Physics Scans

- `hamiltonian_scan.py`
- `two_qubit_spin_scan.py`
- `ising_chain_scan.py`
- `tfim_scan.py`
- `tfim_scaling_scan.py`
- `tfim_finite_size_summary.py`

#### Variational Studies

- `mini_vqe.py`
- `tfim_groundstate_ansatz.py`
- `tfim_variational_scaling.py`
- `tfim_ansatz_comparison.py`
- `tfim_ansatz_cost_quality.py`
- `tfim_ansatz_depth_study.py`
- `tfim_grid_resolution_study.py`
- `adaptive_tfim_vqe_demo.py`
- `adaptive_tfim_vqe_scan.py`
- `adaptive_tfim_vqe_report.py`

#### QAOA Studies

- `qaoa_ising_small.py`
- `qaoa_chain_landscape.py`

## QAOA Campaigns

The repository now also includes orchestration-level QAOA workflows.

- `qaoa_research_campaign.py` writes a small deterministic QAOA campaign into one output directory.
- The current campaign bundles:
  - small QAOA grid search
  - QAOA chain landscape scan
- `qaoa_campaign_summary.py` reads those campaign outputs and reports best parameters, best energy, and a compact landscape summary.

## Data Workflows

CSV-producing examples are intended for downstream plotting, aggregation, or comparative analysis.

## Research Campaigns

The repository also includes orchestration-level workflows that combine several existing deterministic studies.

- `tfim_research_campaign.py` runs a compact TFIM campaign in one command.
- It writes multiple CSV files into one output directory.
- The current campaign bundles:
  - reference TFIM scan
  - comparative variational scaling
  - ansatz comparison
  - grid-resolution study
- Terminal output is a stable file summary rather than a full data dump.

## Campaign Summaries

The TFIM campaign outputs can also be summarized without re-running the underlying studies.

- `tfim_campaign_summary.py` reads the CSV files produced by `tfim_research_campaign.py`.
- It reports row counts for each input file.
- It summarizes minimum variational error per `(n, h)`, the best ansatz when comparison data is present, and the observed grid-resolution effect when grid data is present.
- It can also write one aggregated CSV summary file.

## Comparative Reports

The repository also includes a higher-level report layer across campaigns.

- `research_report.py` reads TFIM and/or QAOA campaign outputs when available.
- It reports campaign file counts, row counts, TFIM best variational error, TFIM best ansatz, QAOA best parameters, QAOA best energy, and QAOA landscape span.
- It can also write one compact aggregated CSV for downstream tabulation.

### Stable CSV Schemas

The following CSV outputs are considered stable at the `v3.0` documentation freeze.

| Example File | Stable CSV Columns |
| --- | --- |
| `examples/tfim_scaling_scan.py` | `n, h, energy, energy_per_site, expval_x0, expval_z0z1` |
| `examples/tfim_finite_size_summary.py` | `h, min_energy_per_site, max_energy_per_site, delta_energy_per_site` |
| `examples/tfim_groundstate_ansatz.py` | `n, h, theta, variational_energy, reference_energy, energy_error` |
| `examples/tfim_variational_scaling.py` | `n, h, theta_best, variational_energy, reference_energy, energy_error, energy_error_per_site` |
| `examples/tfim_ansatz_comparison.py` | `n, h, ansatz_type, variational_energy, reference_energy, energy_error, energy_error_per_site` |
| `examples/tfim_ansatz_cost_quality.py` | `n, h, ansatz_type, parameter_count, variational_energy, reference_energy, energy_error, energy_error_per_site` |
| `examples/tfim_ansatz_depth_study.py` | `n, h, ansatz_type, depth, parameter_count, variational_energy, reference_energy, energy_error, energy_error_per_site` |
| `examples/tfim_grid_resolution_study.py` | `n, h, ansatz_type, depth, grid_size, variational_energy, reference_energy, energy_error, energy_error_per_site` |
| `examples/tfim_research_campaign.py` | campaign output directory containing `tfim_reference_scan.csv`, `tfim_variational_scaling.csv`, `tfim_ansatz_comparison.csv`, `tfim_grid_resolution.csv` |
| `examples/tfim_campaign_summary.py` | `n, h, variational_min_error, best_ansatz_type, best_ansatz_error, best_grid_depth, best_grid_size, best_grid_error, worst_grid_size, worst_grid_error` |
| `examples/tfim_large_scale_campaign.py` | `n, h, energy, energy_per_site, expval_x0, expval_z0z1` |
| `examples/qaoa_research_campaign.py` | campaign output directory containing `qaoa_grid_search.csv`, `qaoa_chain_landscape.csv` |
| `examples/qaoa_campaign_summary.py` | `grid_search_best_num_qubits, grid_search_best_energy, grid_search_best_gamma, grid_search_best_beta, landscape_best_n, landscape_best_gamma, landscape_best_beta, landscape_best_energy, landscape_worst_energy, landscape_energy_span` |
| `examples/research_report.py` | `campaign, file_count, best_metric_name, best_metric_value, context_a, context_b` |
| `examples/qaoa_chain_landscape.py` | `n, gamma, beta, energy` |

## Unsupported Features And Known Limits

- no shot-based sampling
- no gradient support
- no optimizer stack beyond deterministic scans and grid searches
- no observables outside the supported Pauli-word subset
- large wire counts remain RAM-limited because the backend stores the full statevector

## Install

Create a local virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel pytest pennylane
```

Install the package in editable mode:

```bash
python -m pip install -e . --no-build-isolation
```

Install optional plotting support for report scripts:

```bash
python -m pip install -e .[plots] --no-build-isolation
```

`--no-build-isolation` is useful when the environment does not have network access and `pip` would otherwise try to fetch build dependencies again.

## Running Tests

```bash
.venv/bin/pytest -q
```

## Running Examples

### Terminal-Only Examples

```bash
.venv/bin/python examples/hamiltonian_scan.py
.venv/bin/python examples/mini_vqe.py
.venv/bin/python examples/tfim_large_scale_campaign.py
.venv/bin/python examples/tfim_exact_large_campaign.py
.venv/bin/python examples/mps_basic_demo.py
.venv/bin/python examples/mps_paulirot_demo.py
.venv/bin/python examples/mps_truncation_demo.py
.venv/bin/python examples/mps_isingzz_quench.py --csv mps_isingzz_quench.csv
.venv/bin/python examples/adaptive_tfim_vqe_demo.py
.venv/bin/python examples/mps_tebd_tfim_quench.py --csv mps_tebd_tfim_quench.csv
.venv/bin/python examples/mps_trotter_order_study.py --csv mps_trotter_order_study.csv
.venv/bin/python examples/mps_vs_statevector_tfim_quench.py --csv mps_vs_statevector_tfim_quench.csv
.venv/bin/python examples/tfim_quench_error_map.py --csv tfim_quench_error_map.csv
.venv/bin/python examples/tfim_quench_threshold_report.py --error-map-csv tfim_quench_error_map.csv --csv tfim_quench_threshold_report.csv
.venv/bin/python examples/mps_vs_statevector_tfim.py
.venv/bin/python examples/tfim_mps_truncation_scan.py
.venv/bin/python examples/mps_depth_bond_study.py
.venv/bin/python examples/qaoa_mps_truncation_scan.py
.venv/bin/python examples/tfim_mps_large_campaign.py
.venv/bin/python examples/tfim_exact_vs_mps_large_report.py --exact-csv tfim_exact_large_campaign.csv --mps-csv tfim_mps_large_campaign.csv --csv tfim_exact_vs_mps_large_report.csv

.venv/bin/python examples/tfim_mps_sensitivity_report.py --report-csv tfim_exact_vs_mps_large_report.csv --csv tfim_mps_sensitivity_report.csv

.venv/bin/python examples/tfim_mps_threshold_report.py --report-csv tfim_exact_vs_mps_large_report.csv --error-threshold 1e-6 --per-site-threshold 1e-7 --csv tfim_mps_threshold_report.csv
.venv/bin/python examples/two_qubit_spin_scan.py
.venv/bin/python examples/ising_chain_scan.py
.venv/bin/python examples/tfim_scan.py
.venv/bin/python examples/qaoa_ising_small.py
.venv/bin/python examples/tfim_finite_size_summary.py
.venv/bin/python examples/performance_scan.py
.venv/bin/python examples/internal_profile.py
.venv/bin/python examples/statevector_size_table.py
```

### Examples With CSV Export

```bash
.venv/bin/python examples/tfim_scaling_scan.py --csv tfim_scaling.csv
.venv/bin/python examples/tfim_groundstate_ansatz.py --csv tfim_variational.csv
.venv/bin/python examples/tfim_variational_scaling.py --csv tfim_variational_scaling.csv
.venv/bin/python examples/tfim_ansatz_comparison.py --csv tfim_ansatz_comparison.csv
.venv/bin/python examples/tfim_ansatz_cost_quality.py --csv tfim_ansatz_cost_quality.csv
.venv/bin/python examples/tfim_ansatz_depth_study.py --csv tfim_ansatz_depth.csv
.venv/bin/python examples/tfim_grid_resolution_study.py --csv tfim_grid_resolution.csv
.venv/bin/python examples/adaptive_tfim_vqe_scan.py --csv adaptive_tfim_vqe_scan.csv
.venv/bin/python examples/adaptive_tfim_vqe_report.py --scan-csv adaptive_tfim_vqe_scan.csv --output-dir adaptive_tfim_report --csv adaptive_tfim_report.csv
.venv/bin/python examples/qaoa_chain_landscape.py --csv qaoa_landscape.csv
.venv/bin/python examples/tfim_research_campaign.py --output-dir tfim_research_campaign
.venv/bin/python examples/tfim_campaign_summary.py --input-dir tfim_research_campaign --csv tfim_campaign_summary.csv
.venv/bin/python examples/qaoa_research_campaign.py --output-dir qaoa_research_campaign
.venv/bin/python examples/qaoa_campaign_summary.py --input-dir qaoa_research_campaign --csv qaoa_campaign_summary.csv
.venv/bin/python examples/research_report.py --tfim-dir tfim_research_campaign --qaoa-dir qaoa_research_campaign --csv research_report.csv
```

## Roadmap

- `v0.1`: basic device + examples
- `v0.2`: small Hamiltonian direct evaluation
- `v0.3`: `X0X1` and `Y0Y1`
- `v0.4`: explicit public support for `X/Y/Z` on general wires
- `v0.5`: `two_qubit_spin_scan` example
- `v0.6`: limited mixed 2-qubit observables `XZ`, `ZX`, `YZ`, `ZY`
- `v0.7`: statevector backend generalized to arbitrary wires with a 30-qubit design target
- `v0.8`: arbitrary Pauli-word expectation values on distinct wires
- `v0.9`: medium-scale Ising-chain example and validation on top of arbitrary Pauli words
- `v1.0`: public capability freeze with practical limits and scaling documentation
- `v1.1`: deterministic runtime benchmark example and performance notes
- `v1.2`: lightweight internal profiling and hotspot documentation
- `v1.3`: targeted internal hotspot optimization without public API changes
- `v1.4`: official performance baseline documentation
- `v1.5`: targeted `CNOT` kernel optimization and next-hotspot evaluation
- `v1.6`: finer QNode-path characterization and small execute-path reductions
- `v1.7`: single-qubit execute-path candidate evaluation, rejected due regression
- `v1.8`: documentation freeze for shipped optimizations and rejected candidates
- `v1.9`: transverse-field Ising model scan example
- `v2.0`: backend plus small research workflows
- `v2.1`: medium-scale TFIM and QAOA chain workflows
- `v2.2`: data-oriented TFIM and QAOA workflow exports
- `v2.3`: comparative finite-size TFIM workflows
- `v2.4`: TFIM variational studies with reference comparison
- `v2.5`: comparative TFIM variational scaling studies
- `v2.6`: TFIM ansatz comparison studies
- `v2.7`: TFIM ansatz cost-vs-quality studies
- `v2.8`: TFIM ansatz depth studies
- `v2.9`: TFIM grid resolution studies
- `v3.0`: backend + research workflow pack freeze
- `v3.1`: TFIM research campaign orchestration
- `v3.2`: TFIM campaign summary layer
- `v3.3`: QAOA campaign and summary layers
- `v3.4`: comparative report layer across campaigns
- `v3.5`: larger-system deterministic TFIM batch studies
- `v4.0`: minimal tensor-network backend `penq.mps_starter` with pure-NumPy updates
- `v4.1`: runtime truncation controls `max_bond_dim` and `svd_cutoff` for the MPS backend
- `v5.0`: documentation freeze as a dual-backend research pack
- `v6.0`: extended MPS device with arbitrary Pauli expectations and routed CNOT
- `v7.0`: expanded MPS native 2-qubit gates (`CZ`, `PauliRot`, `IsingZZ`/`XX`/`YY`)
- `v8.0`: adaptive TFIM VQE solver and deterministic scanning workflows
- `v8.1`: robust plotting/reporting standard guaranteeing PNG and PDF output pairs
