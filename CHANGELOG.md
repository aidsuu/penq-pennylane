# Changelog

This file summarizes public releases and major internal milestones, with focus on public releases.

## 1.2.0

This release consolidates `penq` as a stable dual-backend package for multi-dimensional TFIM studies, including static workflows, dynamics workflows, and exact-vs-MPS comparisons with consistent data/report outputs.

Highlights:

- Physics coverage now includes 2D square and 3D cubic TFIM (static + dynamics).
- 1D workflows include adaptive TFIM VQE, imaginary-time, and real-time.
- The analysis layer is now cleaner: CSV scans, PNG/PDF reports, and exact-vs-MPS comparison workflows.
- Plugin discovery was validated in a clean environment for:
  - `qml.device("penq.qml_starter", wires=2)`
  - `qml.device("penq.mps_starter", wires=2)`
  - simple QNode execution on both backends.

Compatibility notes:

- Public device names remain unchanged: `penq.qml_starter` and `penq.mps_starter`.
- No public API change requires user migration.

## 1.0.1

- Added an explicit `LICENSE` file.
- Refreshed the GitHub Actions workflow for PyPI publishing.
- Runtime capability is unchanged.

## 1.0.0

First public release of `penq` as a dual-backend PennyLane research package with two stable devices:

- `penq.qml_starter`
- `penq.mps_starter`

This release focused on packaging finalization, wheel validation, and publication metadata.

## Internal milestones (brief)

The list below preserves development history without dominating the public changelog.

- `v11.0-a` to `v11.0-c`: TFIM lattice expansion to 2D square and 3D cubic, including static/dynamics APIs, example workflows, stable CSV schemas, and PNG/PDF reports.
- `v10.0` and `v9.0`: real-time and imaginary-time TFIM solvers, exact-vs-MPS comparators, and dynamics report layers.
- `v8.x`: official adaptive TFIM VQE, scan/report workflows, and solver formula documentation.
- `v7.0` to `v4.0`: maturation of `penq.mps_starter` (truncation controls, routed two-qubit path, Pauli/Ising support, and truncation studies).
- `v3.x` and `v2.x`: stronger research/data pipeline (campaigns, summaries, comparative reports, and CSV-ready scans).
- `v1.x` (internal): performance baseline, profiling, and optimization iterations before public release hardening.
- `v0.9`: early deterministic Ising-chain workflow.
