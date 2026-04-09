import argparse
import csv
from pathlib import Path


def read_csv_rows(path):
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_tfim_quench_threshold_report(
    error_map_csv,
    error_threshold_z0=1e-5,
    error_threshold_z0z1=1e-4,
):
    error_map_path = Path(error_map_csv)
    input_rows = read_csv_rows(error_map_path)

    grouped = {}
    for row in input_rows:
        key = (
            int(row["n"]),
            float(row["h"]),
            float(row["dt"]),
            float(row["time"]),
            int(row["trotter_order"]),
        )
        grouped.setdefault(key, []).append(row)

    summary_rows = []
    for (num_qubits, h, dt, time, trotter_order), rows in sorted(grouped.items()):
        rows = sorted(rows, key=lambda row: (int(row["max_bond_dim"]), float(row["svd_cutoff"])))
        min_bond_dim_for_z0 = next(
            (
                int(row["max_bond_dim"])
                for row in rows
                if float(row["abs_error_z0"]) <= error_threshold_z0
            ),
            "",
        )
        min_bond_dim_for_z0z1 = next(
            (
                int(row["max_bond_dim"])
                for row in rows
                if float(row["abs_error_z0z1"]) <= error_threshold_z0z1
            ),
            "",
        )
        best_abs_error_z0 = min(float(row["abs_error_z0"]) for row in rows)
        best_abs_error_z0z1 = min(float(row["abs_error_z0z1"]) for row in rows)
        summary_rows.append(
            {
                "n": int(num_qubits),
                "h": float(h),
                "dt": float(dt),
                "time": float(time),
                "trotter_order": int(trotter_order),
                "error_threshold_z0": float(error_threshold_z0),
                "error_threshold_z0z1": float(error_threshold_z0z1),
                "min_bond_dim_for_z0": min_bond_dim_for_z0,
                "min_bond_dim_for_z0z1": min_bond_dim_for_z0z1,
                "best_abs_error_z0": float(best_abs_error_z0),
                "best_abs_error_z0z1": float(best_abs_error_z0z1),
            }
        )

    return {
        "error_map_csv": error_map_path,
        "input_row_count": len(input_rows),
        "summary_row_count": len(summary_rows),
        "summary_rows": summary_rows,
    }


def write_tfim_quench_threshold_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "dt",
        "time",
        "trotter_order",
        "error_threshold_z0",
        "error_threshold_z0z1",
        "min_bond_dim_for_z0",
        "min_bond_dim_for_z0z1",
        "best_abs_error_z0",
        "best_abs_error_z0z1",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM quench threshold report.")
    parser.add_argument("--error-map-csv", dest="error_map_csv", required=True, help="Dynamical error-map CSV path.")
    parser.add_argument("--threshold-z0", dest="threshold_z0", type=float, default=1e-5, help="Threshold for abs_error_z0.")
    parser.add_argument("--threshold-z0z1", dest="threshold_z0z1", type=float, default=1e-4, help="Threshold for abs_error_z0z1.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional output CSV path.")
    args = parser.parse_args()

    result = build_tfim_quench_threshold_report(
        args.error_map_csv,
        error_threshold_z0=args.threshold_z0,
        error_threshold_z0z1=args.threshold_z0z1,
    )
    if args.csv_path is not None:
        write_tfim_quench_threshold_csv(args.csv_path, result["summary_rows"])

    print("workflow=TFIM quench threshold report")
    print(f"error_map_csv={result['error_map_csv']}")
    print(f"input_rows={result['input_row_count']} summary_rows={result['summary_row_count']}")
    for row in result["summary_rows"]:
        bond_z0 = "none" if row["min_bond_dim_for_z0"] == "" else str(row["min_bond_dim_for_z0"])
        bond_z0z1 = "none" if row["min_bond_dim_for_z0z1"] == "" else str(row["min_bond_dim_for_z0z1"])
        print(
            f"n={row['n']:>2} h={row['h']:.2f} dt={row['dt']:.3f} time={row['time']:.3f} "
            f"order={row['trotter_order']} min_bond_z0={bond_z0} min_bond_zz={bond_z0z1} "
            f"best_err_z0={row['best_abs_error_z0']:.8f} best_err_zz={row['best_abs_error_z0z1']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
