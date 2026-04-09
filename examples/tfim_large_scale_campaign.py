import argparse
import csv
from pathlib import Path

import pennylane as qml

from QML.PenQ.examples.tfim_groundstate_ansatz import DEVICE_NAME, parse_h_values
from QML.PenQ.examples.tfim_scaling_scan import prepare_tfim_state, tfim_hamiltonian


def validate_tfim_large_scale_inputs(qubit_counts, h_values):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    for num_qubits in qubit_counts:
        if not 12 <= num_qubits <= 20 or num_qubits % 2 != 0:
            raise ValueError("TFIM large-scale campaign expects even qubit counts between 12 and 20.")


def evaluate_tfim_large_scale_row(num_qubits, h, state_name):
    dev = qml.device(DEVICE_NAME, wires=num_qubits)
    hamiltonian = tfim_hamiltonian(num_qubits, h)

    @qml.qnode(dev)
    def energy_circuit():
        prepare_tfim_state(state_name, num_qubits)
        return qml.expval(hamiltonian)

    @qml.qnode(dev)
    def x0_circuit():
        prepare_tfim_state(state_name, num_qubits)
        return qml.expval(qml.PauliX(0))

    @qml.qnode(dev)
    def zz01_circuit():
        prepare_tfim_state(state_name, num_qubits)
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    energy = float(energy_circuit())
    return {
        "n": int(num_qubits),
        "h": float(h),
        "energy": energy,
        "energy_per_site": float(energy / num_qubits),
        "expval_x0": float(x0_circuit()),
        "expval_z0z1": float(zz01_circuit()),
    }


def large_scale_campaign_rows(
    qubit_counts=(12, 14, 16, 18, 20),
    h_values=(0.0, 0.5, 1.0),
    state_name="all_plus",
):
    validate_tfim_large_scale_inputs(qubit_counts, h_values)
    rows = []
    for num_qubits in qubit_counts:
        for h in h_values:
            rows.append(evaluate_tfim_large_scale_row(num_qubits, h, state_name))
    return rows


def write_tfim_large_scale_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["n", "h", "energy", "energy_per_site", "expval_x0", "expval_z0z1"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM large-scale campaign.")
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default="tfim_large_scale_campaign/tfim_large_scale_scan.csv",
        help="CSV output path for the campaign rows.",
    )
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = large_scale_campaign_rows(h_values=parse_h_values(args.h_grid))
    write_tfim_large_scale_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM large-scale campaign")
    print("H = sum_i Z_i Z_{i+1} + h * sum_i X_i")
    print("state = all_plus")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} "
            f"energy={row['energy']:.8f} e/site={row['energy_per_site']:.8f} "
            f"x0={row['expval_x0']:.8f} zz01={row['expval_z0z1']:.8f}"
        )
    print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
