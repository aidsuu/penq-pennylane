# Performance Baseline

This document records the current lightweight baseline for the main internal hotspots of `penq.qml_starter`.

The goal is not to claim universal absolute timings. The backend is CPU-bound and machine-dependent. Instead, this baseline fixes:

- the profiling script: `examples/internal_profile.py`
- the wire counts: `8`, `12`, `16`
- the reported hotspot stages
- the before/after comparison format between milestone pairs

The output format is deterministic even though the measured times depend on the machine.

## Scope

The baseline currently records:

- `v1.2 -> v1.3` for:
  - `single_qubit_gates`
  - `pauli_word_expval`
- `v1.4 -> v1.5` for:
  - `cnot_chain`
  - `qnode_end_to_end`
- `v1.5 -> v1.6` for:
  - `qnode_end_to_end`
  - stage breakdown of:
    - `tape_setup`
    - `measurement_handling`
    - `execute_path`
- `v1.6 -> v1.7` candidate evaluation for:
  - `single_qubit_gates`
  - `execute_path`

No public capability changed across these comparisons. The runtime device remained:

- public device name: `penq.qml_starter`
- analytic-only
- same supported gates and measurements

## Shipped Improvements

### v1.2 -> v1.3

Measured with `examples/internal_profile.py` in this environment.

| Stage | Wires | v1.2 Time (s) | v1.3 Time (s) | Direction |
| --- | ---: | ---: | ---: | --- |
| `single_qubit_gates` | 8 | 0.000929 | 0.000922 | effectively unchanged |
| `single_qubit_gates` | 12 | 0.018399 | 0.018419 | effectively unchanged |
| `single_qubit_gates` | 16 | 0.400191 | 0.401843 | effectively unchanged |
| `pauli_word_expval` | 8 | 0.000343 | 0.000252 | improved |
| `pauli_word_expval` | 12 | 0.004090 | 0.002818 | improved |
| `pauli_word_expval` | 16 | 0.064154 | 0.048000 | improved |

### v1.4 -> v1.5

Measured with the same profiling script and safe wire counts.

| Stage | Wires | v1.4 Time (s) | v1.5 Time (s) | Direction |
| --- | ---: | ---: | ---: | --- |
| `cnot_chain` | 8 | 0.000228 | 0.000205 | improved |
| `cnot_chain` | 12 | 0.006227 | 0.003051 | improved |
| `cnot_chain` | 16 | 0.182192 | 0.051820 | improved |
| `qnode_end_to_end` | 8 | 0.004355 | 0.004170 | improved |
| `qnode_end_to_end` | 12 | 0.049452 | 0.044723 | improved |
| `qnode_end_to_end` | 16 | 1.089817 | 0.866752 | improved |

## Characterization Data

### v1.5 -> v1.6

Measured with the expanded profiling breakdown in the same environment.

| Stage | Wires | v1.5 Time (s) | v1.6 Time (s) | Direction |
| --- | ---: | ---: | ---: | --- |
| `qnode_end_to_end` | 8 | 0.004170 | 0.004122 | improved |
| `qnode_end_to_end` | 12 | 0.044723 | 0.047331 | effectively unchanged |
| `qnode_end_to_end` | 16 | 0.866752 | 0.927684 | effectively unchanged |

### v1.6 Stage Breakdown

The `v1.6` profiling split characterizes the end-to-end path more directly.

| Stage | Wires | Time (s) |
| --- | ---: | ---: |
| `tape_setup` | 8 | 0.001221 |
| `measurement_handling` | 8 | 0.000237 |
| `execute_path` | 8 | 0.002143 |
| `qnode_end_to_end` | 8 | 0.004122 |
| `tape_setup` | 12 | 0.000833 |
| `measurement_handling` | 12 | 0.002702 |
| `execute_path` | 12 | 0.044864 |
| `qnode_end_to_end` | 12 | 0.047331 |
| `tape_setup` | 16 | 0.001136 |
| `measurement_handling` | 16 | 0.041546 |
| `execute_path` | 16 | 0.933701 |
| `qnode_end_to_end` | 16 | 0.927684 |

## Rejected Candidates

### v1.6 Candidate Evaluation For v1.7

An alternative single-qubit execute-path optimization was tested and rejected. The released `v1.7` runtime keeps the `v1.6` kernel because the candidate regressed both `single_qubit_gates` and `execute_path`.

| Stage | Wires | v1.6 Baseline (s) | Candidate (s) | Direction |
| --- | ---: | ---: | ---: | --- |
| `single_qubit_gates` | 8 | 0.000941 | 0.001422 | worse |
| `single_qubit_gates` | 12 | 0.019224 | 0.031141 | worse |
| `single_qubit_gates` | 16 | 0.426140 | 0.660930 | worse |
| `execute_path` | 8 | 0.002030 | 0.003135 | worse |
| `execute_path` | 12 | 0.043421 | 0.067722 | worse |
| `execute_path` | 16 | 1.047344 | 1.389630 | worse |

## Interpretation

- `v1.3` is the shipped improvement milestone for `pauli_word_expval`.
- `v1.5` is the shipped improvement milestone for the `CNOT` kernel.
- `v1.6` adds the clearest characterization of end-to-end overhead: tape setup is small, measurement handling is modest, and the execute path is the dominant component.
- `v1.7` is a rejected-candidate milestone: the tested single-qubit execute-path rewrite was clearly slower on the same safe wire counts and was not shipped.
- The public profiling output format remains stable, so future updates can be compared against the same structure.

## Reproducing

Run:

```bash
.venv/bin/python examples/internal_profile.py
```

Optionally compare with the runtime-oriented benchmark:

```bash
.venv/bin/python examples/performance_scan.py
```
