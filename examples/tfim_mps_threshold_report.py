import argparse
import csv
from pathlib import Path


def read_csv_rows(path):
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _normalize_rows(input_rows):
    normalized_rows = []
    for row in input_rows:
        if "mean_abs_error" in row:
            normalized_rows.append(
                {
                    "n": int(row["n"]),
                    "h": float(row["h"]),
                    "max_bond_dim": int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                    "abs_error": float(row["mean_abs_error"]),
                    "energy_error_per_site": float(row["energy_error_per_site"]),
                }
            )
        else:
            normalized_rows.append(
                {
                    "n": int(row["n"]),
                    "h": float(row["h"]),
                    "max_bond_dim": int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                    "abs_error": float(row["abs_error"]),
                    "energy_error_per_site": float(row["energy_error_per_site"]),
                }
            )
    return normalized_rows


def build_tfim_mps_threshold_report(report_csv, error_threshold=1e-6, per_site_threshold=1e-7):
    report_path = Path(report_csv)
    input_rows = _normalize_rows(read_csv_rows(report_path))

    grouped = {}
    for row in input_rows:
        key = (row["n"], row["h"])
        grouped.setdefault(key, []).append(row)

    summary_rows = []
    for (num_qubits, h), rows in sorted(grouped.items()):
        rows = sorted(rows, key=lambda row: (row["max_bond_dim"], row["svd_cutoff"]))
        best_row = min(rows, key=lambda row: (row["abs_error"], row["energy_error_per_site"], row["max_bond_dim"]))
        threshold_match = next(
            (
                row
                for row in rows
                if row["abs_error"] <= error_threshold and row["energy_error_per_site"] <= per_site_threshold
            ),
            None,
        )
        summary_rows.append(
            {
                "n": int(num_qubits),
                "h": float(h),
                "error_threshold": float(error_threshold),
                "per_site_threshold": float(per_site_threshold),
                "min_bond_dim_meeting_threshold": (
                    "" if threshold_match is None else int(threshold_match["max_bond_dim"])
                ),
                "best_abs_error": float(best_row["abs_error"]),
                "best_energy_error_per_site": float(best_row["energy_error_per_site"]),
            }
        )

    return {
        "report_csv": report_path,
        "input_row_count": len(input_rows),
        "summary_row_count": len(summary_rows),
        "summary_rows": summary_rows,
    }


def write_tfim_mps_threshold_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "error_threshold",
        "per_site_threshold",
        "min_bond_dim_meeting_threshold",
        "best_abs_error",
        "best_energy_error_per_site",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM MPS threshold report.")
    parser.add_argument("--report-csv", dest="report_csv", required=True, help="Exact-vs-MPS report or sensitivity CSV path.")
    parser.add_argument("--error-threshold", dest="error_threshold", type=float, default=1e-6, help="Absolute error threshold.")
    parser.add_argument(
        "--per-site-threshold",
        dest="per_site_threshold",
        type=float,
        default=1e-7,
        help="Per-site error threshold.",
    )
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional output CSV path.")
    args = parser.parse_args()

    result = build_tfim_mps_threshold_report(
        args.report_csv,
        error_threshold=args.error_threshold,
        per_site_threshold=args.per_site_threshold,
    )
    if args.csv_path is not None:
        write_tfim_mps_threshold_csv(args.csv_path, result["summary_rows"])

    print("workflow=TFIM MPS threshold report")
    print(f"report_csv={result['report_csv']}")
    print(f"input_rows={result['input_row_count']} summary_rows={result['summary_row_count']}")
    print(
        f"thresholds=abs<={args.error_threshold:.1e} per_site<={args.per_site_threshold:.1e}"
    )
    for row in result["summary_rows"]:
        bond_text = "none" if row["min_bond_dim_meeting_threshold"] == "" else str(row["min_bond_dim_meeting_threshold"])
        print(
            f"n={row['n']:>2} h={row['h']:.2f} min_bond_dim={bond_text} "
            f"best_abs_error={row['best_abs_error']:.8f} "
            f"best_err/site={row['best_energy_error_per_site']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
