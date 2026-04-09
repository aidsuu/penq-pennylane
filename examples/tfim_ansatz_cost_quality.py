import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.tfim_ansatz_comparison import ansatz_comparison_rows
from QML.PenQ.examples.tfim_groundstate_ansatz import DEVICE_NAME, parse_h_values


def parameter_count(num_qubits, ansatz_type):
    if ansatz_type == "product_ry":
        return int(num_qubits)
    if ansatz_type == "entangling_ry_cnot_ry":
        return int(2 * num_qubits)
    raise ValueError("Unsupported ansatz_type. Expected one of: product_ry, entangling_ry_cnot_ry.")


def cost_quality_rows(qubit_counts=(6, 8, 10), h_values=(0.0, 0.5, 1.0, 1.5), num_theta=9):
    rows = ansatz_comparison_rows(qubit_counts=qubit_counts, h_values=h_values, num_theta=num_theta)
    cost_rows = []

    for row in rows:
        cost_rows.append(
            {
                "n": int(row["n"]),
                "h": float(row["h"]),
                "ansatz_type": row["ansatz_type"],
                "parameter_count": parameter_count(row["n"], row["ansatz_type"]),
                "variational_energy": float(row["variational_energy"]),
                "reference_energy": float(row["reference_energy"]),
                "energy_error": float(row["energy_error"]),
                "energy_error_per_site": float(row["energy_error_per_site"]),
            }
        )

    return cost_rows


def write_tfim_ansatz_cost_quality_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "ansatz_type",
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
    parser = argparse.ArgumentParser(description="Deterministic TFIM ansatz cost-vs-quality study.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0,1.5",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = cost_quality_rows(h_values=parse_h_values(args.h_grid))
    if args.csv_path is not None:
        write_tfim_ansatz_cost_quality_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM ansatz cost vs quality")
    print("ansatzes = product RY, entangling RY + CNOT chain + RY")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} ansatz={row['ansatz_type']} "
            f"params={row['parameter_count']:>2} var={row['variational_energy']:.8f} "
            f"ref={row['reference_energy']:.8f} err={row['energy_error']:.8f} "
            f"err/site={row['energy_error_per_site']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
