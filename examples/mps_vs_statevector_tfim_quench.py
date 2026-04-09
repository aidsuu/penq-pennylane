import argparse
import csv
from pathlib import Path

import pennylane as qml

from QML.PenQ.examples.mps_tebd_tfim_quench import parse_h_values
from QML.PenQ.examples.mps_tebd_tfim_quench import parse_n_values
from QML.PenQ.examples.mps_trotter_order_study import parse_dt_values
from QML.PenQ.examples.mps_trotter_order_study import prepare_trotter_state


STATEVECTOR_DEVICE_NAME = "penq.qml_starter"
MPS_DEVICE_NAME = "penq.mps_starter"


def validate_quench_comparison_inputs(qubit_counts, h_values, dt_values, total_time, bond_dims):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    if not dt_values:
        raise ValueError("dt_values must not be empty.")
    if not bond_dims:
        raise ValueError("bond_dims must not be empty.")
    if total_time <= 0.0:
        raise ValueError("total_time must be positive.")
    for num_qubits in qubit_counts:
        if num_qubits not in {6, 8}:
            raise ValueError("MPS vs statevector TFIM quench expects qubit counts chosen from 6 and 8.")
    for dt in dt_values:
        if dt <= 0.0:
            raise ValueError("dt values must be positive.")
    for bond_dim in bond_dims:
        if int(bond_dim) < 1:
            raise ValueError("bond_dims must contain positive integers.")


def tfim_quench_comparison_rows(
    qubit_counts=(6, 8),
    h_values=(0.5, 1.0),
    dt_values=(0.2, 0.1),
    total_time=0.4,
    bond_dims=(2, 4),
    svd_cutoff=1e-12,
):
    validate_quench_comparison_inputs(qubit_counts, h_values, dt_values, total_time, bond_dims)
    rows = []

    for num_qubits in qubit_counts:
        reference_dev = qml.device(STATEVECTOR_DEVICE_NAME, wires=num_qubits)
        for h in h_values:
            for dt in dt_values:
                steps = int(round(total_time / dt))
                time = steps * dt
                for trotter_order in (1, 2):
                    @qml.qnode(reference_dev)
                    def reference_z0():
                        prepare_trotter_state(num_qubits, h, dt, steps, trotter_order)
                        return qml.expval(qml.PauliZ(0))

                    @qml.qnode(reference_dev)
                    def reference_zz01():
                        prepare_trotter_state(num_qubits, h, dt, steps, trotter_order)
                        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

                    reference_z0_value = float(reference_z0())
                    reference_z0z1_value = float(reference_zz01())

                    for max_bond_dim in bond_dims:
                        mps_dev = qml.device(
                            MPS_DEVICE_NAME,
                            wires=num_qubits,
                            max_bond_dim=max_bond_dim,
                            svd_cutoff=svd_cutoff,
                        )

                        @qml.qnode(mps_dev)
                        def mps_z0():
                            prepare_trotter_state(num_qubits, h, dt, steps, trotter_order)
                            return qml.expval(qml.PauliZ(0))

                        @qml.qnode(mps_dev)
                        def mps_zz01():
                            prepare_trotter_state(num_qubits, h, dt, steps, trotter_order)
                            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

                        mps_z0_value = float(mps_z0())
                        mps_z0z1_value = float(mps_zz01())
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
                                "reference_z0": reference_z0_value,
                                "mps_z0": mps_z0_value,
                                "abs_error_z0": abs(mps_z0_value - reference_z0_value),
                                "reference_z0z1": reference_z0z1_value,
                                "mps_z0z1": mps_z0z1_value,
                                "abs_error_z0z1": abs(mps_z0z1_value - reference_z0z1_value),
                            }
                        )
    return rows


def write_tfim_quench_comparison_csv(path, rows):
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
        "reference_z0",
        "mps_z0",
        "abs_error_z0",
        "reference_z0z1",
        "mps_z0z1",
        "abs_error_z0z1",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic exact-vs-MPS TFIM quench comparison.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument("--h-grid", dest="h_grid", default="0.5,1.0", help="Comma-separated deterministic h grid.")
    parser.add_argument("--n-grid", dest="n_grid", default="6,8", help="Comma-separated deterministic qubit-count grid.")
    parser.add_argument("--dt-grid", dest="dt_grid", default="0.2,0.1", help="Comma-separated deterministic dt grid.")
    parser.add_argument("--total-time", dest="total_time", type=float, default=0.4, help="Fixed total evolution time.")
    parser.add_argument("--bond-grid", dest="bond_grid", default="2,4", help="Comma-separated deterministic max_bond_dim grid.")
    parser.add_argument("--svd-cutoff", dest="svd_cutoff", type=float, default=1e-12, help="Fixed singular-value cutoff.")
    args = parser.parse_args()

    rows = tfim_quench_comparison_rows(
        qubit_counts=parse_n_values(args.n_grid),
        h_values=parse_h_values(args.h_grid),
        dt_values=parse_dt_values(args.dt_grid),
        total_time=args.total_time,
        bond_dims=tuple(int(value) for value in args.bond_grid.split(",")),
        svd_cutoff=args.svd_cutoff,
    )
    if args.csv_path is not None:
        write_tfim_quench_comparison_csv(args.csv_path, rows)

    print(f"reference_device={STATEVECTOR_DEVICE_NAME}")
    print(f"mps_device={MPS_DEVICE_NAME}")
    print("workflow=Exact-vs-MPS TFIM quench")
    print("comparison = first-order and second-order Trotter dynamics on matched circuits")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} dt={row['dt']:.3f} steps={row['steps']:>2} "
            f"time={row['time']:.3f} order={row['trotter_order']} max_bond_dim={row['max_bond_dim']} "
            f"z0_ref={row['reference_z0']:.8f} z0_mps={row['mps_z0']:.8f} err_z0={row['abs_error_z0']:.8f} "
            f"zz_ref={row['reference_z0z1']:.8f} zz_mps={row['mps_z0z1']:.8f} err_zz={row['abs_error_z0z1']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
