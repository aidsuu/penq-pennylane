import argparse
import csv

import numpy as np
import pennylane as qml

from QML.PenQ.examples.tfim_scan import DEVICE_NAME, evaluate_tfim_scan, tfim_hamiltonian


def variational_energy(dev, num_qubits, h, theta):
    hamiltonian = tfim_hamiltonian(num_qubits, h)

    @qml.qnode(dev)
    def circuit():
        for wire in range(num_qubits):
            qml.RY(theta, wires=wire)
        return qml.expval(hamiltonian)

    return float(circuit())


def reference_energy(num_qubits, h):
    reference_rows = evaluate_tfim_scan(num_qubits, (h,))
    return float(min(row["energy"] for row in reference_rows))


def variational_study_rows(qubit_counts=(6, 8, 10), h_values=(0.0, 0.5, 1.0, 1.5), num_theta=17):
    theta_grid = np.linspace(0.0, np.pi, num_theta)
    rows = []

    for num_qubits in qubit_counts:
        dev = qml.device(DEVICE_NAME, wires=num_qubits)
        for h in h_values:
            best_energy = None
            best_theta = None
            for theta in theta_grid:
                energy = variational_energy(dev, num_qubits, h, theta)
                if best_energy is None or energy < best_energy:
                    best_energy = energy
                    best_theta = float(theta)

            ref_energy = reference_energy(num_qubits, h)
            rows.append(
                {
                    "n": int(num_qubits),
                    "h": float(h),
                    "theta": float(best_theta),
                    "variational_energy": float(best_energy),
                    "reference_energy": float(ref_energy),
                    "energy_error": float(best_energy - ref_energy),
                }
            )

    return rows


def write_tfim_groundstate_csv(path, rows):
    fieldnames = ["n", "h", "theta", "variational_energy", "reference_energy", "energy_error"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_h_values(text):
    return tuple(float(value) for value in text.split(","))


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM variational study.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0,1.5",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = variational_study_rows(h_values=parse_h_values(args.h_grid))
    if args.csv_path is not None:
        write_tfim_groundstate_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM variational ground-state ansatz")
    print("ansatz = product RY(theta) with deterministic grid search")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} theta={row['theta']:.8f} "
            f"var={row['variational_energy']:.8f} ref={row['reference_energy']:.8f} "
            f"err={row['energy_error']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
