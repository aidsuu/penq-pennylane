import argparse
import csv
from pathlib import Path

import pennylane as qml

from QML.PenQ.examples.mps_tebd_tfim_quench import MPS_DEVICE_NAME
from QML.PenQ.examples.mps_tebd_tfim_quench import apply_x_evolution
from QML.PenQ.examples.mps_tebd_tfim_quench import apply_zz_evolution
from QML.PenQ.examples.mps_tebd_tfim_quench import parse_h_values
from QML.PenQ.examples.mps_tebd_tfim_quench import parse_n_values


def parse_dt_values(text):
    return tuple(float(value) for value in text.split(","))


def validate_trotter_order_inputs(qubit_counts, h_values, dt_values, total_time):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    if not dt_values:
        raise ValueError("dt_values must not be empty.")
    if total_time <= 0.0:
        raise ValueError("total_time must be positive.")
    for num_qubits in qubit_counts:
        if num_qubits not in {8, 10}:
            raise ValueError("MPS Trotter order study expects qubit counts chosen from 8 and 10.")
    for dt in dt_values:
        if dt <= 0.0:
            raise ValueError("dt values must be positive.")


def apply_zz_layer(num_qubits, dt):
    for wire in range(num_qubits - 1):
        apply_zz_evolution(wire, wire + 1, dt)


def apply_first_order_step(num_qubits, h, dt):
    apply_zz_layer(num_qubits, dt)
    apply_x_evolution(num_qubits, h, dt)


def apply_second_order_step(num_qubits, h, dt):
    apply_zz_layer(num_qubits, 0.5 * dt)
    apply_x_evolution(num_qubits, h, dt)
    apply_zz_layer(num_qubits, 0.5 * dt)


def prepare_trotter_state(num_qubits, h, dt, steps, trotter_order):
    for _ in range(steps):
        if trotter_order == 1:
            apply_first_order_step(num_qubits, h, dt)
        elif trotter_order == 2:
            apply_second_order_step(num_qubits, h, dt)
        else:
            raise ValueError("Unsupported trotter_order. Expected 1 or 2.")


def mps_trotter_order_rows(
    qubit_counts=(8, 10),
    h_values=(0.5, 1.0),
    dt_values=(0.2, 0.1),
    total_time=0.4,
    max_bond_dim=4,
    svd_cutoff=1e-12,
):
    validate_trotter_order_inputs(qubit_counts, h_values, dt_values, total_time)
    rows = []

    for num_qubits in qubit_counts:
        dev = qml.device(
            MPS_DEVICE_NAME,
            wires=num_qubits,
            max_bond_dim=max_bond_dim,
            svd_cutoff=svd_cutoff,
        )
        for h in h_values:
            for dt in dt_values:
                steps = int(round(total_time / dt))
                time = steps * dt
                for trotter_order in (1, 2):
                    @qml.qnode(dev)
                    def z0_circuit():
                        prepare_trotter_state(num_qubits, h, dt, steps, trotter_order)
                        return qml.expval(qml.PauliZ(0))

                    @qml.qnode(dev)
                    def zz01_circuit():
                        prepare_trotter_state(num_qubits, h, dt, steps, trotter_order)
                        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

                    rows.append(
                        {
                            "n": int(num_qubits),
                            "h": float(h),
                            "dt": float(dt),
                            "steps": int(steps),
                            "time": float(time),
                            "trotter_order": int(trotter_order),
                            "max_bond_dim": int(max_bond_dim),
                            "svd_cutoff": float(svd_cutoff),
                            "expval_z0": float(z0_circuit()),
                            "expval_z0z1": float(zz01_circuit()),
                        }
                    )

    return rows


def write_mps_trotter_order_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "dt",
        "steps",
        "time",
        "trotter_order",
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
    parser = argparse.ArgumentParser(description="Deterministic MPS Trotter order study for TFIM.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument("--h-grid", dest="h_grid", default="0.5,1.0", help="Comma-separated deterministic h grid.")
    parser.add_argument("--n-grid", dest="n_grid", default="8,10", help="Comma-separated deterministic qubit-count grid.")
    parser.add_argument("--dt-grid", dest="dt_grid", default="0.2,0.1", help="Comma-separated deterministic dt grid.")
    parser.add_argument("--total-time", dest="total_time", type=float, default=0.4, help="Fixed total evolution time.")
    parser.add_argument("--max-bond-dim", dest="max_bond_dim", type=int, default=4, help="Fixed max bond dimension.")
    parser.add_argument("--svd-cutoff", dest="svd_cutoff", type=float, default=1e-12, help="Fixed singular-value cutoff.")
    args = parser.parse_args()

    rows = mps_trotter_order_rows(
        qubit_counts=parse_n_values(args.n_grid),
        h_values=parse_h_values(args.h_grid),
        dt_values=parse_dt_values(args.dt_grid),
        total_time=args.total_time,
        max_bond_dim=args.max_bond_dim,
        svd_cutoff=args.svd_cutoff,
    )
    if args.csv_path is not None:
        write_mps_trotter_order_csv(args.csv_path, rows)

    print(f"device={MPS_DEVICE_NAME}")
    print("workflow=MPS Trotter order study")
    print("comparison = first-order vs second-order TFIM Trotterization at fixed total time")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} dt={row['dt']:.3f} steps={row['steps']:>2} "
            f"time={row['time']:.3f} order={row['trotter_order']} "
            f"max_bond_dim={row['max_bond_dim']} svd_cutoff={row['svd_cutoff']:.1e} "
            f"z0={row['expval_z0']:.8f} zz01={row['expval_z0z1']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
