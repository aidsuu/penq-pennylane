import argparse
import csv
from pathlib import Path


def read_csv_rows(path):
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _sensitivity_label(error_rank, total_rows):
    if total_rows <= 1:
        return "low"
    if error_rank <= max(1, total_rows // 3):
        return "high"
    if error_rank >= total_rows - max(1, total_rows // 3) + 1:
        return "low"
    return "medium"


def build_tfim_mps_sensitivity_report(report_csv):
    report_path = Path(report_csv)
    input_rows = read_csv_rows(report_path)

    grouped = {}
    for row in input_rows:
        key = (
            int(row["n"]),
            float(row["h"]),
            int(row["max_bond_dim"]),
            float(row["svd_cutoff"]),
        )
        grouped.setdefault(key, []).append(row)

    summary_rows = []
    for (num_qubits, h, max_bond_dim, svd_cutoff), rows in sorted(grouped.items()):
        mean_abs_error = sum(float(row["abs_error"]) for row in rows) / len(rows)
        mean_error_per_site = sum(float(row["energy_error_per_site"]) for row in rows) / len(rows)
        summary_rows.append(
            {
                "n": int(num_qubits),
                "h": float(h),
                "max_bond_dim": int(max_bond_dim),
                "svd_cutoff": float(svd_cutoff),
                "mean_abs_error": float(mean_abs_error),
                "energy_error_per_site": float(mean_error_per_site),
            }
        )

    ranked_rows = sorted(
        summary_rows,
        key=lambda row: (-row["mean_abs_error"], row["n"], row["h"], row["max_bond_dim"], row["svd_cutoff"]),
    )
    for index, row in enumerate(ranked_rows, start=1):
        row["error_rank"] = int(index)
        row["sensitivity_label"] = _sensitivity_label(index, len(ranked_rows))

    summary_rows = sorted(
        ranked_rows,
        key=lambda row: (row["n"], row["h"], row["max_bond_dim"], row["svd_cutoff"]),
    )
    min_row = min(summary_rows, key=lambda row: row["mean_abs_error"]) if summary_rows else None
    max_row = max(summary_rows, key=lambda row: row["mean_abs_error"]) if summary_rows else None

    return {
        "report_csv": report_path,
        "input_row_count": len(input_rows),
        "summary_row_count": len(summary_rows),
        "summary_rows": summary_rows,
        "min_error_row": min_row,
        "max_error_row": max_row,
    }


def write_tfim_mps_sensitivity_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "max_bond_dim",
        "svd_cutoff",
        "mean_abs_error",
        "energy_error_per_site",
        "error_rank",
        "sensitivity_label",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM MPS sensitivity report.")
    parser.add_argument("--report-csv", dest="report_csv", required=True, help="Exact-vs-MPS report CSV path.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional output CSV path.")
    args = parser.parse_args()

    result = build_tfim_mps_sensitivity_report(args.report_csv)
    if args.csv_path is not None:
        write_tfim_mps_sensitivity_csv(args.csv_path, result["summary_rows"])

    print("workflow=TFIM MPS sensitivity report")
    print(f"report_csv={result['report_csv']}")
    print(f"input_rows={result['input_row_count']} summary_rows={result['summary_row_count']}")
    if result["min_error_row"] is not None:
        row = result["min_error_row"]
        print(
            f"min_error=n={row['n']} h={row['h']:.2f} max_bond_dim={row['max_bond_dim']} "
            f"svd_cutoff={row['svd_cutoff']:.1e} mean_abs_error={row['mean_abs_error']:.8f} "
            f"err/site={row['energy_error_per_site']:.8f} label={row['sensitivity_label']}"
        )
    if result["max_error_row"] is not None:
        row = result["max_error_row"]
        print(
            f"max_error=n={row['n']} h={row['h']:.2f} max_bond_dim={row['max_bond_dim']} "
            f"svd_cutoff={row['svd_cutoff']:.1e} mean_abs_error={row['mean_abs_error']:.8f} "
            f"err/site={row['energy_error_per_site']:.8f} label={row['sensitivity_label']}"
        )
    for row in result["summary_rows"]:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} max_bond_dim={row['max_bond_dim']} "
            f"svd_cutoff={row['svd_cutoff']:.1e} mean_abs_error={row['mean_abs_error']:.8f} "
            f"err/site={row['energy_error_per_site']:.8f} rank={row['error_rank']} "
            f"label={row['sensitivity_label']}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
