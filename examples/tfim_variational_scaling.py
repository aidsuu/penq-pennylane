import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.tfim_groundstate_ansatz import DEVICE_NAME, parse_h_values, variational_study_rows


def comparative_variational_rows(qubit_counts=(6, 8, 10), h_values=(0.0, 0.5, 1.0, 1.5), num_theta=17):
    rows = variational_study_rows(qubit_counts=qubit_counts, h_values=h_values, num_theta=num_theta)
    comparative_rows = []

    for row in rows:
        comparative_rows.append(
            {
                "n": int(row["n"]),
                "h": float(row["h"]),
                "theta_best": float(row["theta"]),
                "variational_energy": float(row["variational_energy"]),
                "reference_energy": float(row["reference_energy"]),
                "energy_error": float(row["energy_error"]),
                "energy_error_per_site": float(row["energy_error"] / row["n"]),
            }
        )

    return comparative_rows


def write_tfim_variational_scaling_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "theta_best",
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
    parser = argparse.ArgumentParser(description="Deterministic comparative TFIM variational scaling study.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0,1.5",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = comparative_variational_rows(h_values=parse_h_values(args.h_grid))
    if args.csv_path is not None:
        write_tfim_variational_scaling_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM comparative variational scaling")
    print("ansatz = product RY(theta) with deterministic grid search")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} theta_best={row['theta_best']:.8f} "
            f"var={row['variational_energy']:.8f} ref={row['reference_energy']:.8f} "
            f"err={row['energy_error']:.8f} err/site={row['energy_error_per_site']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
