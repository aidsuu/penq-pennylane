import argparse
import csv
from pathlib import Path

import numpy as np
import pennylane as qml


MPS_DEVICE_NAME = "penq.mps_starter"


def parse_h_values(text):
    return tuple(float(value) for value in text.split(","))


def parse_n_values(text):
    return tuple(int(value) for value in text.split(","))


def validate_mps_tebd_inputs(qubit_counts, h_values, dt, num_steps):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    if dt <= 0.0:
        raise ValueError("dt must be positive.")
    if int(num_steps) < 1:
        raise ValueError("num_steps must be at least 1.")
    for num_qubits in qubit_counts:
        if num_qubits not in {8, 10}:
            raise ValueError("MPS TEBD TFIM quench expects qubit counts chosen from 8 and 10.")


def apply_zz_evolution(wire0, wire1, dt):
    qml.CNOT(wires=[wire0, wire1])
    qml.RZ(2.0 * dt, wires=wire1)
    qml.CNOT(wires=[wire0, wire1])


def apply_x_evolution(num_qubits, h, dt):
    angle = 2.0 * dt * h
    for wire in range(num_qubits):
        qml.RX(angle, wires=wire)


def apply_tebd_step(num_qubits, h, dt):
    for wire in range(num_qubits - 1):
        apply_zz_evolution(wire, wire + 1, dt)
    apply_x_evolution(num_qubits, h, dt)


def prepare_tfim_quench_state(num_qubits, h, dt, step):
    for _ in range(step):
        apply_tebd_step(num_qubits, h, dt)


def mps_tebd_tfim_rows(
    qubit_counts=(8, 10),
    h_values=(0.5, 1.0),
    dt=0.1,
    num_steps=4,
    max_bond_dim=4,
    svd_cutoff=1e-12,
):
    validate_mps_tebd_inputs(qubit_counts, h_values, dt, num_steps)
    rows = []

    for num_qubits in qubit_counts:
        dev = qml.device(
            MPS_DEVICE_NAME,
            wires=num_qubits,
            max_bond_dim=max_bond_dim,
            svd_cutoff=svd_cutoff,
        )

        for h in h_values:
            for step in range(num_steps + 1):
                @qml.qnode(dev)
                def z0_circuit(current_step=step):
                    prepare_tfim_quench_state(num_qubits, h, dt, current_step)
                    return qml.expval(qml.PauliZ(0))

                @qml.qnode(dev)
                def zz01_circuit(current_step=step):
                    prepare_tfim_quench_state(num_qubits, h, dt, current_step)
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
                        "expval_z0z1": float(zz01_circuit()),
                    }
                )

    return rows


def write_mps_tebd_tfim_csv(path, rows):
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
    parser = argparse.ArgumentParser(description="Deterministic MPS TEBD-like TFIM quench.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument("--h-grid", dest="h_grid", default="0.5,1.0", help="Comma-separated deterministic h grid.")
    parser.add_argument("--n-grid", dest="n_grid", default="8,10", help="Comma-separated deterministic qubit-count grid.")
    parser.add_argument("--dt", dest="dt", type=float, default=0.1, help="Fixed time step.")
    parser.add_argument("--steps", dest="steps", type=int, default=4, help="Fixed number of TEBD-like steps.")
    parser.add_argument("--max-bond-dim", dest="max_bond_dim", type=int, default=4, help="Fixed max bond dimension.")
    parser.add_argument("--svd-cutoff", dest="svd_cutoff", type=float, default=1e-12, help="Fixed singular-value cutoff.")
    args = parser.parse_args()

    rows = mps_tebd_tfim_rows(
        qubit_counts=parse_n_values(args.n_grid),
        h_values=parse_h_values(args.h_grid),
        dt=args.dt,
        num_steps=args.steps,
        max_bond_dim=args.max_bond_dim,
        svd_cutoff=args.svd_cutoff,
    )
    if args.csv_path is not None:
        write_mps_tebd_tfim_csv(args.csv_path, rows)

    print(f"device={MPS_DEVICE_NAME}")
    print("workflow=MPS TEBD-like TFIM quench")
    print("evolution = first-order Trotter with ZZ layer then X layer")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} dt={row['dt']:.3f} step={row['step']:>2} "
            f"time={row['time']:.3f} max_bond_dim={row['max_bond_dim']} "
            f"svd_cutoff={row['svd_cutoff']:.1e} z0={row['expval_z0']:.8f} zz01={row['expval_z0z1']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
