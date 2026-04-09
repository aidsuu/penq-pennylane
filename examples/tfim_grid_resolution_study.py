import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.tfim_ansatz_depth_study import ansatz_depth_rows
from QML.PenQ.examples.tfim_groundstate_ansatz import DEVICE_NAME, parse_h_values


GRID_SIZES = {
    "coarse": 3,
    "medium": 5,
    "fine": 7,
}


def grid_resolution_rows(qubit_counts=(6, 8), h_values=(0.0, 0.5, 1.0), grid_sizes=GRID_SIZES):
    rows = []

    for grid_name, grid_size in grid_sizes.items():
        depth_rows = ansatz_depth_rows(qubit_counts=qubit_counts, h_values=h_values, num_theta=grid_size)
        for row in depth_rows:
            if row["ansatz_type"] != "entangling_ry_cnot_ry":
                continue
            rows.append(
                {
                    "n": int(row["n"]),
                    "h": float(row["h"]),
                    "ansatz_type": row["ansatz_type"],
                    "depth": int(row["depth"]),
                    "grid_size": grid_name,
                    "variational_energy": float(row["variational_energy"]),
                    "reference_energy": float(row["reference_energy"]),
                    "energy_error": float(row["energy_error"]),
                    "energy_error_per_site": float(row["energy_error_per_site"]),
                }
            )

    return rows


def write_tfim_grid_resolution_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "ansatz_type",
        "depth",
        "grid_size",
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
    parser = argparse.ArgumentParser(description="Deterministic TFIM grid-resolution study.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = grid_resolution_rows(h_values=parse_h_values(args.h_grid))
    if args.csv_path is not None:
        write_tfim_grid_resolution_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM grid resolution study")
    print("ansatzes = entangling depth-1, entangling depth-2")
    print("grid_sizes = coarse, medium, fine")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} depth={row['depth']} grid={row['grid_size']} "
            f"var={row['variational_energy']:.8f} ref={row['reference_energy']:.8f} "
            f"err={row['energy_error']:.8f} err/site={row['energy_error_per_site']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
