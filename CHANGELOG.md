# Changelog

## v1.0.1

- Added an explicit `LICENSE` file to the public repository.
- Refreshed the GitHub PyPI publishing workflow for current GitHub Actions runtime guidance.
- Kept runtime backend capability unchanged.

## v1.0.0

- First public release of `penq` as a dual-backend PennyLane research pack.
- Ships the stable public device names `penq.qml_starter` and `penq.mps_starter`.
- Keeps runtime capability unchanged while finalizing packaging, wheel validation, and release metadata for PyPI publication.

## v6.5

- Added `examples/tfim_quench_threshold_report.py` for deterministic threshold selection on top of the TFIM quench dynamical error map.
- Added CSV export with `n, h, dt, time, trotter_order, error_threshold_z0, error_threshold_z0z1, min_bond_dim_for_z0, min_bond_dim_for_z0z1, best_abs_error_z0, best_abs_error_z0z1`.
- Added lightweight tests for threshold-report row structure and CSV header.

## v6.4

- Added `examples/tfim_quench_error_map.py` for deterministic TFIM time-evolution error maps derived from the exact-vs-MPS quench comparison workflow.
- Added CSV export with `n, h, dt, steps, time, trotter_order, max_bond_dim, svd_cutoff, abs_error_z0, abs_error_z0z1`.
- Added lightweight tests for error-map row structure and CSV header.

## v6.3

- Added `examples/mps_vs_statevector_tfim_quench.py` for deterministic exact-vs-MPS validation of TFIM quench observables across Trotter order, `dt`, and bond dimension.
- Added CSV export with `n, h, dt, steps, time, trotter_order, max_bond_dim, svd_cutoff, reference_z0, mps_z0, abs_error_z0, reference_z0z1, mps_z0z1, abs_error_z0z1`.
- Added lightweight tests for quench-comparison row structure, CSV header, and zero-error smoke checks on matched small cases.

## v6.2

- Added `examples/mps_trotter_order_study.py` for deterministic comparison of first-order and second-order TFIM Trotterization on `penq.mps_starter`.
- Added CSV export with `n, h, dt, steps, time, trotter_order, max_bond_dim, svd_cutoff, expval_z0, expval_z0z1`.
- Added lightweight tests for Trotter-order row structure, CSV header, and bounded-observable smoke checks.

## v6.1

- Added `examples/mps_tebd_tfim_quench.py` for deterministic TFIM time evolution on `penq.mps_starter` using a first-order Trotter / TEBD-like split.
- Added CSV export with `n, h, dt, step, time, max_bond_dim, svd_cutoff, expval_z0, expval_z0z1`.
- Added lightweight tests for TEBD row structure, CSV header, and deterministic step-0 observables.

## v6.0

- Expanded `penq.mps_starter` runtime support to direct Pauli-word expectation values for arbitrary tensor products of `PauliX`, `PauliY`, and `PauliZ` on distinct wires.
- Added small linear-combination support in `penq.mps_starter` for observables exposed through `observable.terms()` when every term is a supported Pauli word.
- Added internally routed non-nearest-neighbor `CNOT` support to `penq.mps_starter` while preserving the adjacent update path.
- Added runtime tests for `PauliX`, `PauliY`, arbitrary Pauli words, exact-vs-MPS observable agreement, and routed `CNOT`.
- Added `examples/mps_general_pauli_demo.py` for deterministic general-Pauli and routed-`CNOT` validation against `penq.qml_starter`.

## v5.4

- Added `examples/tfim_mps_threshold_report.py` to determine the minimum bond dimension that satisfies deterministic TFIM truncation-error thresholds.
- Added optional CSV export with `n, h, error_threshold, per_site_threshold, min_bond_dim_meeting_threshold, best_abs_error, best_energy_error_per_site`.
- Added lightweight tests for the threshold-report row schema and CSV header.

## v5.3

- Added `examples/tfim_mps_sensitivity_report.py` to summarize large exact-vs-MPS TFIM truncation errors as a function of `h` and `max_bond_dim`.
- Added optional CSV export with `n, h, max_bond_dim, svd_cutoff, mean_abs_error, energy_error_per_site, error_rank, sensitivity_label`.
- Added lightweight tests for the sensitivity-report row schema and CSV header.

## v5.2

- Added `examples/tfim_exact_vs_mps_large_report.py` to compare overlap points from the exact and MPS TFIM large campaigns.
- Aligned the large exact-vs-MPS report to use an exact statevector chain-energy reference on the matched overlap points, so the reported error reflects the same deterministic TFIM-style chain observable as the MPS campaign.
- Added optional CSV export with `n, h, max_bond_dim, svd_cutoff, reference_energy, mps_energy, abs_error, energy_error_per_site`.
- Added lightweight tests for the large-report row schema and CSV header.

## v5.1

- Added `examples/tfim_exact_large_campaign.py` for deterministic exact large-batch TFIM baseline data.
- Added `examples/tfim_mps_large_campaign.py` for deterministic larger MPS batch scans across fixed bond-dimension settings.
- Added lightweight tests for the large-campaign row schemas and CSV headers.

## v5.0

- Froze `penq` documentation as a dual-backend research pack built around `penq.qml_starter` and `penq.mps_starter`.
- Added explicit backend comparison and backend selection guidance to the README.
- Reworked the workflow index to distinguish exact-only, MPS-only, and exact-vs-MPS comparative workflows.

## v4.5

- Added `examples/qaoa_mps_truncation_scan.py` for deterministic QAOA truncation studies with `penq.mps_starter` against a `penq.qml_starter` reference.
- Added CSV export with `n, gamma, beta, max_bond_dim, svd_cutoff, reference_energy, mps_energy, abs_error`.
- Added lightweight tests for the QAOA truncation-study row schema and CSV header.

## v4.4

- Added `examples/mps_depth_bond_study.py` for deterministic depth-versus-bond-dimension studies with `penq.mps_starter` against a `penq.qml_starter` reference.
- Added CSV export with `n, h, depth, max_bond_dim, svd_cutoff, mps_energy, reference_energy, abs_error, energy_error_per_site`.
- Added lightweight tests for the depth-versus-bond row schema and CSV header.

## v4.3

- Added `examples/tfim_mps_truncation_scan.py` for deterministic TFIM-style truncation studies with `penq.mps_starter` against a `penq.qml_starter` reference.
- Added CSV export with `n, h, max_bond_dim, svd_cutoff, mps_energy, reference_energy, abs_error, energy_error_per_site`.
- Added lightweight tests for the truncation-study row schema and CSV header.

## v4.2

- Added `examples/mps_vs_statevector_tfim.py` for deterministic comparison between `penq.qml_starter` and `penq.mps_starter`.
- Added CSV export with `n, h, max_bond_dim, svd_cutoff, reference_energy, mps_energy, abs_error`.
- Added lightweight tests for the comparison row schema and CSV header.

## v4.1

- Added `max_bond_dim` and `svd_cutoff` to `penq.mps_starter` for controlled SVD truncation on nearest-neighbor two-qubit splits.
- Added `examples/mps_truncation_demo.py` to show deterministic truncation behavior on a small Bell-state circuit.
- Added MPS tests covering no-truncation, sufficiently large truncation, `Z` and `ZZ` expectations, and a small comparison against `penq.qml_starter`.

## v4.0

- Added `qml_mps_device.py` with a new minimal tensor-network backend exposed as `penq.mps_starter`.
- Added pure-NumPy MPS support for single-qubit gates, nearest-neighbor `CNOT`, `qml.state()`, `qml.expval(qml.PauliZ(wire))`, and `qml.expval(qml.PauliZ(w0) @ qml.PauliZ(w1))`.
- Added `examples/mps_basic_demo.py` and basic integration tests for the new MPS device.

## v3.5.1

- Renamed `examples/tfim_hpc_campaign.py` to `examples/tfim_large_scale_campaign.py` for more neutral and longer-lived naming.
- Renamed the corresponding README section from `HPC Campaigns` to `Large-Scale Campaigns`.
- Removed mention of specific hardware models while keeping the general note that the backend remains full-statevector, CPU-only, and analytic-only.

## v3.5

- Added `examples/tfim_large_scale_campaign.py` for deterministic larger-system TFIM batch studies on even qubit counts between `12` and `20`.
- Added structured CSV export for large-scale TFIM campaign rows with stable schema for batch analysis.
- Added lightweight tests for the large-scale campaign row schema and CSV header.

## v3.4

- Added `examples/research_report.py` as a deterministic comparative report layer across TFIM and QAOA campaigns.
- Added optional aggregated CSV output for the cross-campaign report.
- Added lightweight tests for report structure and report CSV header.

## v3.3

- Added `examples/qaoa_research_campaign.py` for deterministic multi-CSV QAOA campaign orchestration.
- Added `examples/qaoa_campaign_summary.py` for reading QAOA campaign outputs and producing a compact deterministic summary.
- Added lightweight tests for QAOA campaign file layout and QAOA summary CSV structure.

## v3.2

- Added `examples/tfim_campaign_summary.py` to summarize TFIM campaign outputs without re-running the underlying workflows.
- Added optional aggregated CSV output for campaign summaries.
- Added lightweight tests for summary structure and summary CSV header.

## v3.1

- Added `examples/tfim_research_campaign.py` to orchestrate multiple deterministic TFIM workflows in one campaign run.
- Added structured multi-CSV output for reference scan, variational scaling, ansatz comparison, and grid-resolution analysis.
- Added lightweight tests for stable campaign file names and output structure.

## v3.0

- Froze the repository positioning as a stable backend plus deterministic research workflow pack.
- Reworked the README to separate backend/runtime, performance tools, research workflows, and data workflows.
- Added a workflow index and documented stable CSV schemas for the CSV-producing examples.

## v2.9

- Added `examples/tfim_grid_resolution_study.py` for deterministic TFIM grid-resolution studies on entangling ansatz families.
- Added CSV export with `grid_size` together with total and per-site energy error.
- Added lightweight tests for the grid-resolution row schema and CSV header.

## v2.8

- Added `examples/tfim_ansatz_depth_study.py` for deterministic TFIM depth studies across baseline, depth-1, and depth-2 ansatz families.
- Added CSV export with `depth`, `parameter_count`, and per-site error reporting.
- Added lightweight tests for the ansatz-depth row schema and CSV header.

## v2.7

- Added `examples/tfim_ansatz_cost_quality.py` for deterministic TFIM cost-vs-quality studies across ansatz families.
- Added CSV export with `parameter_count` together with total and per-site energy error.
- Added lightweight tests for the cost-vs-quality row schema and CSV header.

## v2.6

- Added `examples/tfim_ansatz_comparison.py` for deterministic comparison between baseline product and simple entangling TFIM ansatz families.
- Added CSV export with per-site error reporting for direct ansatz-to-reference comparison.
- Added lightweight tests for the ansatz-comparison row schema and CSV header.

## v2.5

- Added `examples/tfim_variational_scaling.py` for deterministic comparative TFIM variational studies across system sizes.
- Added CSV export with `theta_best`, `energy_error`, and `energy_error_per_site` for downstream analysis.
- Added lightweight tests for the comparative variational row schema and CSV header.

## v2.4

- Added `examples/tfim_groundstate_ansatz.py` for deterministic TFIM variational studies on safe system sizes.
- Added direct comparison against TFIM reference energies plus CSV export for downstream analysis.
- Added lightweight tests for the variational row schema and CSV header.

## v2.3

- Extended `examples/tfim_scaling_scan.py` with `energy_per_site` for finite-size comparison.
- Added `examples/tfim_finite_size_summary.py` for deterministic comparative TFIM summaries across system sizes.
- Added lightweight tests for the comparative row schema and CSV header.

## v2.2

- Added CSV export support to `examples/tfim_scaling_scan.py` and `examples/qaoa_chain_landscape.py`.
- Added lightweight tests for deterministic row schemas and CSV headers.
- Documented the examples as research data workflows for downstream analysis.

## v2.1

- Added `examples/tfim_scaling_scan.py` for deterministic medium-scale TFIM scans across `n = 6, 8, 10, 12, 14, 16`.
- Added `examples/qaoa_chain_landscape.py` for deterministic medium-scale p=1 QAOA landscape scans.
- Added lightweight helper tests for both new workflow examples and clarified the practical full-statevector limit in the README.

## v2.0

- Added `examples/qaoa_ising_small.py` as a deterministic research workflow beyond TFIM.
- Added lightweight test coverage for the QAOA helper.
- Reframed the package documentation around `penq.qml_starter` as a backend plus compact research examples.

## v1.9

- Added `examples/tfim_scan.py` for deterministic transverse-field Ising model scans on `6..10` qubits.
- Added a lightweight analytic cross-check for the TFIM example helper.
- Kept the runtime device unchanged.

## v1.8

- Consolidated the performance documentation so shipped optimizations and rejected candidates are easier to distinguish.
- Added explicit performance engineering notes for `v1.3`, `v1.5`, and `v1.7`.
- Kept the runtime device unchanged.

## v1.7

- Audited the single-qubit execute path against the `v1.6` baseline.
- Measured a scalar-coefficient candidate optimization and rejected it because it regressed both `single_qubit_gates` and `execute_path`.
- Kept the released runtime behavior aligned with `v1.6` and documented the rejected candidate in the performance baseline.

## v1.6

- Split the internal profiling view of `qnode_end_to_end` into `tape_setup`, `measurement_handling`, and `execute_path`.
- Reduced small repeated allocations and parsing in the execute/measurement path without changing public behavior.
- Documented the `v1.5 -> v1.6` comparison and the finer stage breakdown in the performance baseline.

## v1.5

- Optimized the internal `CNOT` kernel with a block-structured swap path.
- Documented the `v1.4 -> v1.5` before/after baseline for `cnot_chain` and `qnode_end_to_end`.
- Confirmed that the next clearer bottleneck among those two candidates is the end-to-end `QNode` path.

## v1.4

- Added `docs/performance_baseline.md` with the official `v1.2 -> v1.3` hotspot baseline.
- Documented safe-wire baseline data for `single_qubit_gates` and `pauli_word_expval` at `8`, `12`, and `16` wires.
- Kept the runtime device implementation unchanged.

## v1.3

- Optimized the internal Pauli-word expectation path with cheaper parity handling and pairwise iteration.
- Audited the single-qubit gate hotspot and kept the proven loop structure to avoid regressions.
- Kept the public API, supported capability set, and runtime device scope unchanged.

## v1.2

- Added `examples/internal_profile.py` for lightweight deterministic profiling of internal hotspots.
- Documented internal hotspot categories alongside the existing performance notes.
- Kept the runtime device scope unchanged.

## v1.1

- Added `examples/performance_scan.py` for deterministic runtime benchmarking on safe wire counts.
- Added documentation for practical performance characteristics alongside the existing memory-scaling notes.
- Kept the runtime device scope unchanged.

## v1.0

- Froze the public `penq.qml_starter` capability set without widening runtime scope.
- Added `examples/statevector_size_table.py` for deterministic amplitude and memory scaling guidance.
- Documented practical RAM limits up to the 30-wire design target.

## v0.9

- Added `examples/ising_chain_scan.py` for deterministic `6..12` qubit spin-chain scans.
- Added direct integration coverage for a small spin-chain Hamiltonian built from arbitrary Pauli words.
- Kept the runtime device scope unchanged while extending example-level validation.

## v0.8

- Generalized expectation-value evaluation to arbitrary Pauli words on distinct wires.
- Added direct support for small linear combinations of those arbitrary Pauli words.
- Added higher-wire integration tests for `Z0Z7`, `X1Y9`, and `X1Y9Z13`.

## v0.7

- Increased the supported wire count to `1..30`.
- Generalized statevector gate application to arbitrary wires using in-place updates.
- Added higher-wire integration tests, including non-adjacent CNOT and larger-system execution paths.

## v0.6

- Added limited mixed 2-qubit observables: `X0Z1`, `Z0X1`, `Y0Z1`, and `Z0Y1`.
- Enabled small direct Hamiltonians that include those supported mixed terms.

## v0.5

- Added the `examples/two_qubit_spin_scan.py` physics-oriented 2-qubit example.
- Documented the new example in the README.

## v0.4

- Clarified and tested explicit public support for `PauliX`, `PauliY`, and `PauliZ` on general wires.
- Extended linear-combination coverage for small Hamiltonians using `X0`, `Y0`, `Z0`, `X1`, `Y1`, and `Z1`.

## v0.3

- Added 2-qubit observables `X0X1` and `Y0Y1`.
- Enabled direct evaluation of mixed small Hamiltonians when all terms are supported.

## v0.2

- Added direct small-Hamiltonian evaluation through PennyLane linear combinations via `observable.terms()`.
- Kept the backend analytic-only and deterministic.

## v0.1

- Implemented the initial `penq.qml_starter` backend.
- Added the first integration tests, basic Hamiltonian scans, and mini VQE example.
