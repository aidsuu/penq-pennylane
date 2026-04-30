# penq

`penq` is a PennyLane research package with two analytic backends: exact statevector and MPS. It targets deterministic TFIM workflows, exact-vs-MPS comparisons, and outputs that are ready for analysis.

The current public release is `1.2.0`. Public plugin names are stable, so code built around PennyLane device creation does not need API changes when switching backends.

The repository includes a broad workflow set (1D, 2D square, and 3D cubic; static and dynamics), while the runtime devices remain intentionally compact and strict.

## What it is

`penq` exposes two PennyLane devices:

- `penq.qml_starter`: exact full-statevector backend
- `penq.mps_starter`: MPS backend for bond-dimension and truncation studies

Both are analytic-only (`shots=None`/`0`) and are used for deterministic workflows with reproducible table/plot outputs.

## Installation

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install penq-pennylane
```

Optional plotting support for report scripts:

```bash
python -m pip install "penq-pennylane[plots]"
```

For local development from this repository:

```bash
python -m pip install -e . --no-build-isolation
python -m pip install -e .[plots] --no-build-isolation
```

## Device names

- `penq.qml_starter`
- `penq.mps_starter`

Both have been validated through PennyLane plugin discovery in a clean environment.

## Minimal PennyLane example

This minimal usage snippet follows current PennyLane documentation style and uses `import pennylane as qp`.

```python
import pennylane as qp

# Exact backend
exact_dev = qp.device("penq.qml_starter", wires=2)

# MPS backend
mps_dev = qp.device("penq.mps_starter", wires=2)

@qp.qnode(exact_dev)
def exact_circuit(theta):
    qp.Hadamard(wires=0)
    qp.CNOT(wires=[0, 1])
    qp.RX(theta, wires=0)
    return qp.expval(qp.PauliZ(0) @ qp.PauliZ(1))

@qp.qnode(mps_dev)
def mps_circuit(theta):
    qp.Hadamard(wires=0)
    qp.CNOT(wires=[0, 1])
    qp.RX(theta, wires=0)
    return qp.expval(qp.PauliZ(0) @ qp.PauliZ(1))

print(exact_circuit(0.2))
print(mps_circuit(0.2))
```

## Current scope

The current public package includes:

- exact and MPS backends
- 1D TFIM workflows: static, adaptive VQE, imaginary-time, real-time
- 2D square TFIM workflows: static and dynamics
- 3D cubic TFIM workflows: static and dynamics
- exact-vs-MPS comparison workflows
- CSV-ready scans for downstream analysis
- report pipelines with PNG/PDF outputs

Practical backend difference:

- Exact backend (`penq.qml_starter`): full-precision numerical reference, best for baselines and validation.
- MPS backend (`penq.mps_starter`): useful for scaling/truncation studies (`max_bond_dim`, `svd_cutoff`); can match exact behavior with enough bond dimension, and becomes approximate under truncation.

A common workflow is to start with exact as a baseline, then compare against MPS to quantify cost-error trade-offs.

## Tested environment

- PennyLane 0.44.1
- penq-pennylane 1.2.0
- Python 3.13.5
- NumPy 2.4.4
- SciPy 1.17.1
