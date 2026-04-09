import argparse
import csv
from pathlib import Path

import numpy as np
import pennylane as qml

from QML.PenQ.examples.tfim_groundstate_ansatz import DEVICE_NAME, parse_h_values, reference_energy
from QML.PenQ.examples.tfim_scan import tfim_hamiltonian


def parameter_count(num_qubits, ansatz_type, depth):
    if ansatz_type == "product_ry":
        return int(num_qubits)
    if ansatz_type == "entangling_ry_cnot_ry":
        return int((depth + 1) * num_qubits)
    raise ValueError("Unsupported ansatz_type. Expected one of: product_ry, entangling_ry_cnot_ry.")


def product_ry_energy(dev, num_qubits, h, theta):
    hamiltonian = tfim_hamiltonian(num_qubits, h)

    @qml.qnode(dev)
    def circuit():
        for wire in range(num_qubits):
            qml.RY(theta, wires=wire)
        return qml.expval(hamiltonian)

    return float(circuit())


def entangling_depth_energy(dev, num_qubits, h, thetas):
    hamiltonian = tfim_hamiltonian(num_qubits, h)

    @qml.qnode(dev)
    def circuit():
        for layer_index, theta in enumerate(thetas):
            for wire in range(num_qubits):
                qml.RY(theta, wires=wire)
            if layer_index < len(thetas) - 1:
                for wire in range(num_qubits - 1):
                    qml.CNOT(wires=[wire, wire + 1])
        return qml.expval(hamiltonian)

    return float(circuit())


def best_product_row(dev, num_qubits, h, theta_grid, ref_energy):
    best_energy = None
    for theta in theta_grid:
        energy = product_ry_energy(dev, num_qubits, h, theta)
        if best_energy is None or energy < best_energy:
            best_energy = energy

    return {
        "n": int(num_qubits),
        "h": float(h),
        "ansatz_type": "product_ry",
        "depth": 0,
        "parameter_count": parameter_count(num_qubits, "product_ry", 0),
        "variational_energy": float(best_energy),
        "reference_energy": float(ref_energy),
        "energy_error": float(best_energy - ref_energy),
        "energy_error_per_site": float((best_energy - ref_energy) / num_qubits),
    }


def best_entangling_row(dev, num_qubits, h, theta_grid, ref_energy, depth):
    best_energy = None

    if depth == 1:
        for theta_0 in theta_grid:
            for theta_1 in theta_grid:
                energy = entangling_depth_energy(dev, num_qubits, h, (theta_0, theta_1))
                if best_energy is None or energy < best_energy:
                    best_energy = energy
    elif depth == 2:
        for theta_0 in theta_grid:
            for theta_1 in theta_grid:
                for theta_2 in theta_grid:
                    energy = entangling_depth_energy(dev, num_qubits, h, (theta_0, theta_1, theta_2))
                    if best_energy is None or energy < best_energy:
                        best_energy = energy
    else:
        raise ValueError("Unsupported entangling depth. Expected one of: 1, 2.")

    return {
        "n": int(num_qubits),
        "h": float(h),
        "ansatz_type": "entangling_ry_cnot_ry",
        "depth": int(depth),
        "parameter_count": parameter_count(num_qubits, "entangling_ry_cnot_ry", depth),
        "variational_energy": float(best_energy),
        "reference_energy": float(ref_energy),
        "energy_error": float(best_energy - ref_energy),
        "energy_error_per_site": float((best_energy - ref_energy) / num_qubits),
    }


def ansatz_depth_rows(qubit_counts=(6, 8, 10), h_values=(0.0, 0.5, 1.0, 1.5), num_theta=5):
    theta_grid = np.linspace(0.0, np.pi, num_theta)
    rows = []

    for num_qubits in qubit_counts:
        dev = qml.device(DEVICE_NAME, wires=num_qubits)
        for h in h_values:
            ref_energy = reference_energy(num_qubits, h)
            rows.append(best_product_row(dev, num_qubits, h, theta_grid, ref_energy))
            rows.append(best_entangling_row(dev, num_qubits, h, theta_grid, ref_energy, depth=1))
            rows.append(best_entangling_row(dev, num_qubits, h, theta_grid, ref_energy, depth=2))

    return rows


def write_tfim_ansatz_depth_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "ansatz_type",
        "depth",
        "parameter_count",
        "variational_energy",
        "reference_energy",
        "energy_error",
        "energy_error_per_site",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM ansatz depth study.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0,1.5",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = ansatz_depth_rows(h_values=parse_h_values(args.h_grid))
    if args.csv_path is not None:
        write_tfim_ansatz_depth_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM ansatz depth study")
    print("ansatzes = product RY, entangling depth-1, entangling depth-2")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} ansatz={row['ansatz_type']} "
            f"depth={row['depth']} params={row['parameter_count']:>2} "
            f"var={row['variational_energy']:.8f} ref={row['reference_energy']:.8f} "
            f"err={row['energy_error']:.8f} err/site={row['energy_error_per_site']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
