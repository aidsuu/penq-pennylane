import argparse
import csv
from pathlib import Path

import pennylane as qml

from QML.PenQ.examples.tfim_mps_truncation_scan import parse_h_values, tfim_style_chain_energy


DEVICE_NAME = "penq.mps_starter"


def parse_bond_values(text):
    return tuple(int(value) for value in text.split(","))


def parse_n_values(text):
    return tuple(int(value) for value in text.split(","))


def validate_tfim_mps_large_inputs(qubit_counts, h_values, bond_dims):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    if not bond_dims:
        raise ValueError("bond_dims must not be empty.")
    for num_qubits in qubit_counts:
        if num_qubits not in {12, 16, 20, 24, 28}:
            raise ValueError("TFIM MPS large campaign expects qubit counts chosen from 12, 16, 20, 24, 28.")


def tfim_mps_large_rows(
    qubit_counts=(12, 16, 20, 24, 28),
    h_values=(0.0, 0.5, 1.0),
    bond_dims=(2, 4, 8),
    svd_cutoff=1e-12,
):
    validate_tfim_mps_large_inputs(qubit_counts, h_values, bond_dims)
    rows = []
    for num_qubits in qubit_counts:
        for h in h_values:
            for max_bond_dim in bond_dims:
                dev = qml.device(
                    DEVICE_NAME,
                    wires=num_qubits,
                    max_bond_dim=max_bond_dim,
                    svd_cutoff=svd_cutoff,
                )
                energy = tfim_style_chain_energy(dev, num_qubits, h)
                rows.append(
                    {
                        "n": int(num_qubits),
                        "h": float(h),
                        "max_bond_dim": int(max_bond_dim),
                        "svd_cutoff": float(svd_cutoff),
                        "mps_energy": float(energy),
                        "energy_per_site": float(energy / num_qubits),
                    }
                )
    return rows


def write_tfim_mps_large_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["n", "h", "max_bond_dim", "svd_cutoff", "mps_energy", "energy_per_site"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM MPS large campaign.")
    parser.add_argument("--csv", dest="csv_path", default="tfim_mps_large_campaign.csv", help="CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0",
        help="Comma-separated deterministic h grid.",
    )
    parser.add_argument(
        "--bond-grid",
        dest="bond_grid",
        default="2,4,8",
        help="Comma-separated deterministic max_bond_dim grid.",
    )
    parser.add_argument(
        "--n-grid",
        dest="n_grid",
        default="12,16,20,24,28",
        help="Comma-separated deterministic qubit-count grid.",
    )
    args = parser.parse_args()

    rows = tfim_mps_large_rows(
        qubit_counts=parse_n_values(args.n_grid),
        h_values=parse_h_values(args.h_grid),
        bond_dims=parse_bond_values(args.bond_grid),
    )
    write_tfim_mps_large_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM MPS large campaign")
    print("energy = sum_i <Z_i Z_{i+1}> on a deterministic TFIM-style chain ansatz")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} max_bond_dim={row['max_bond_dim']} "
            f"svd_cutoff={row['svd_cutoff']:.1e} "
            f"mps={row['mps_energy']:.8f} e/site={row['energy_per_site']:.8f}"
        )
    print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
