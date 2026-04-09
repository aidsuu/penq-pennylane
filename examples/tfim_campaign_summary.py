import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.tfim_groundstate_ansatz import DEVICE_NAME
from QML.PenQ.examples.tfim_research_campaign import campaign_output_paths


def read_csv_rows(path):
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def campaign_row_counts(paths):
    return {name: len(read_csv_rows(path)) for name, path in paths.items() if Path(path).exists()}


def build_campaign_summary(output_dir):
    paths = campaign_output_paths(output_dir)
    row_counts = campaign_row_counts(paths)

    variational_rows = read_csv_rows(paths["variational_scaling"])
    comparison_rows = read_csv_rows(paths["ansatz_comparison"])
    grid_rows = read_csv_rows(paths["grid_resolution"])

    summary_rows = []
    keys = sorted(
        {(int(row["n"]), float(row["h"])) for row in variational_rows},
        key=lambda item: (item[0], item[1]),
    )

    for num_qubits, h in keys:
        variational_match = next(
            row for row in variational_rows if int(row["n"]) == num_qubits and float(row["h"]) == h
        )
        comparison_match = [
            row for row in comparison_rows if int(row["n"]) == num_qubits and float(row["h"]) == h
        ]
        best_ansatz = min(comparison_match, key=lambda row: float(row["energy_error"]))

        grid_match = [row for row in grid_rows if int(row["n"]) == num_qubits and float(row["h"]) == h]
        best_grid = min(grid_match, key=lambda row: float(row["energy_error"]))
        worst_grid = max(grid_match, key=lambda row: float(row["energy_error"]))

        summary_rows.append(
            {
                "n": int(num_qubits),
                "h": float(h),
                "variational_min_error": float(variational_match["energy_error"]),
                "best_ansatz_type": best_ansatz["ansatz_type"],
                "best_ansatz_error": float(best_ansatz["energy_error"]),
                "best_grid_depth": int(best_grid["depth"]),
                "best_grid_size": best_grid["grid_size"],
                "best_grid_error": float(best_grid["energy_error"]),
                "worst_grid_size": worst_grid["grid_size"],
                "worst_grid_error": float(worst_grid["energy_error"]),
            }
        )

    return {"paths": paths, "row_counts": row_counts, "summary_rows": summary_rows}


def write_campaign_summary_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "variational_min_error",
        "best_ansatz_type",
        "best_ansatz_error",
        "best_grid_depth",
        "best_grid_size",
        "best_grid_error",
        "worst_grid_size",
        "worst_grid_error",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM campaign summary.")
    parser.add_argument(
        "--input-dir",
        dest="input_dir",
        default="tfim_research_campaign",
        help="Directory containing TFIM research campaign CSV outputs.",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default=None,
        help="Optional CSV output path for the aggregated summary.",
    )
    args = parser.parse_args()

    result = build_campaign_summary(args.input_dir)
    if args.csv_path is not None:
        write_campaign_summary_csv(args.csv_path, result["summary_rows"])

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM campaign summary")
    print(f"input_dir={Path(args.input_dir)}")
    for key in ("reference_scan", "variational_scaling", "ansatz_comparison", "grid_resolution"):
        print(f"{key}: rows={result['row_counts'][key]}")
    for row in result["summary_rows"]:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} var_min_err={row['variational_min_error']:.8f} "
            f"best_ansatz={row['best_ansatz_type']} best_ansatz_err={row['best_ansatz_error']:.8f} "
            f"best_grid=depth{row['best_grid_depth']}/{row['best_grid_size']} "
            f"best_grid_err={row['best_grid_error']:.8f} "
            f"worst_grid={row['worst_grid_size']} worst_grid_err={row['worst_grid_error']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
