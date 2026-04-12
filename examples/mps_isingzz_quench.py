import argparse
import csv
from pathlib import Path

import pennylane as qml


MPS_DEVICE_NAME = "penq.mps_starter"


def parse_h_values(text):
    return tuple(float(value) for value in text.split(","))


def validate_mps_isingzz_inputs(qubit_counts, h_values, dt, steps):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    if dt <= 0.0:
        raise ValueError("dt must be positive.")
    if steps < 1:
        raise ValueError("steps must be at least one.")
    for num_qubits in qubit_counts:
        if num_qubits not in {8, 10}:
            raise ValueError("MPS IsingZZ quench expects qubit counts chosen from 8 and 10.")


def _prepare_quench_circuit(num_qubits, h, dt, step_count):
    for wire in range(num_qubits):
        qml.Hadamard(wires=wire)
    for _ in range(step_count):
        for wire in range(num_qubits - 1):
            qml.IsingZZ(2.0 * dt, wires=[wire, wire + 1])
        for wire in range(num_qubits):
            qml.RX(2.0 * h * dt, wires=wire)


def mps_isingzz_quench_rows(
    qubit_counts=(8, 10),
    h_values=(0.25, 0.50, 1.00),
    dt=0.1,
    steps=4,
    max_bond_dim=4,
    svd_cutoff=1e-12,
):
    validate_mps_isingzz_inputs(qubit_counts, h_values, dt, steps)
    rows = []

    for num_qubits in qubit_counts:
        dev = qml.device(
            MPS_DEVICE_NAME,
            wires=num_qubits,
            max_bond_dim=max_bond_dim,
            svd_cutoff=svd_cutoff,
        )
        for h in h_values:
            for step in range(steps + 1):
                @qml.qnode(dev)
                def z0_circuit(step_count=step):
                    _prepare_quench_circuit(num_qubits, h, dt, step_count)
                    return qml.expval(qml.PauliZ(0))

                @qml.qnode(dev)
                def z0z1_circuit(step_count=step):
                    _prepare_quench_circuit(num_qubits, h, dt, step_count)
                    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

                rows.append(
                    {
                        "n": int(num_qubits),
                        "h": float(h),
                        "dt": float(dt),
                        "step": int(step),
                        "time": float(step * dt),
                        "max_bond_dim": int(max_bond_dim),
                        "svd_cutoff": float(svd_cutoff),
                        "expval_z0": float(z0_circuit()),
                        "expval_z0z1": float(z0z1_circuit()),
                    }
                )
    return rows


def write_mps_isingzz_quench_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "dt",
        "step",
        "time",
        "max_bond_dim",
        "svd_cutoff",
        "expval_z0",
        "expval_z0z1",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic MPS native IsingZZ quench workflow.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.25,0.50,1.00",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = mps_isingzz_quench_rows(h_values=parse_h_values(args.h_grid))
    if args.csv_path is not None:
        write_mps_isingzz_quench_csv(args.csv_path, rows)

    print(f"device={MPS_DEVICE_NAME}")
    print("workflow=MPS native IsingZZ quench")
    print("evolution = product_i IsingZZ(2 dt) followed by product_i RX(2 h dt)")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} dt={row['dt']:.2f} step={row['step']:>2} "
            f"time={row['time']:.2f} bond={row['max_bond_dim']} "
            f"z0={row['expval_z0']:.8f} z0z1={row['expval_z0z1']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
