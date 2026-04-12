import argparse
import csv
from collections import defaultdict
from pathlib import Path

from QML.PenQ.examples.plotting_utils import finalize_axes
from QML.PenQ.examples.plotting_utils import load_publication_pyplot
from QML.PenQ.examples.plotting_utils import save_required_figure_outputs


SCAN_FIELDNAMES = [
    "n",
    "J",
    "h",
    "backend",
    "layer",
    "energy",
    "energy_per_site",
    "expval_x0",
    "expval_z0z1",
    "converged",
    "final_delta_energy",
    "max_bond_dim",
    "svd_cutoff",
]


def read_adaptive_tfim_scan_csv(path):
    """Read deterministic adaptive TFIM scan CSV with explicit schema validation."""
    rows = []
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SCAN_FIELDNAMES:
            raise ValueError(
                f"Unexpected adaptive TFIM scan CSV header: {reader.fieldnames}. "
                f"Expected {SCAN_FIELDNAMES}."
            )
        for row in reader:
            rows.append(
                {
                    "n": int(row["n"]),
                    "J": float(row["J"]),
                    "h": float(row["h"]),
                    "backend": row["backend"],
                    "layer": int(row["layer"]),
                    "energy": float(row["energy"]),
                    "energy_per_site": float(row["energy_per_site"]),
                    "expval_x0": float(row["expval_x0"]),
                    "expval_z0z1": float(row["expval_z0z1"]),
                    "converged": row["converged"] == "True",
                    "final_delta_energy": float(row["final_delta_energy"]),
                    "max_bond_dim": None if row["max_bond_dim"] == "" else int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                }
            )
    return rows


def _final_rows(rows):
    grouped = {}
    for row in rows:
        key = (row["n"], row["J"], row["h"], row["backend"], row["max_bond_dim"], row["svd_cutoff"])
        if key not in grouped or row["layer"] > grouped[key]["layer"]:
            grouped[key] = row
    return list(grouped.values())


def _exact_vs_mps_rows(rows):
    exact_rows = {}
    comparison_rows = []
    for row in _final_rows(rows):
        key = (row["n"], row["J"], row["h"])
        if row["backend"] == "qml":
            exact_rows[key] = row

    for row in _final_rows(rows):
        key = (row["n"], row["J"], row["h"])
        if row["backend"] != "mps" or key not in exact_rows:
            continue
        exact_row = exact_rows[key]
        comparison_rows.append(
            {
                "n": row["n"],
                "J": row["J"],
                "h": row["h"],
                "max_bond_dim": row["max_bond_dim"],
                "exact_energy": exact_row["energy"],
                "mps_energy": row["energy"],
                "abs_error": abs(row["energy"] - exact_row["energy"]),
            }
        )
    return comparison_rows


def write_adaptive_tfim_report_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["n", "J", "h", "max_bond_dim", "exact_energy", "mps_energy", "abs_error"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_adaptive_tfim_report(scan_csv, output_dir):
    """Generate adaptive TFIM report figures and require PNG+PDF output pairs."""
    rows = read_adaptive_tfim_scan_csv(scan_csv)
    plt, style_used = load_publication_pyplot()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig_energy, ax_energy = plt.subplots(figsize=(5.5, 3.4))
    series = defaultdict(list)
    for row in rows:
        bond_text = "exact" if row["backend"] == "qml" else f"mps-b{row['max_bond_dim']}"
        label = f"n={row['n']} h={row['h']:.2f} {bond_text}"
        series[label].append((row["layer"], row["energy"]))
    for label, points in sorted(series.items()):
        points = sorted(points)
        ax_energy.plot([point[0] for point in points], [point[1] for point in points], marker="o", label=label)
    finalize_axes(ax_energy, "Layer", "Variational energy", "Adaptive TFIM VQE energy vs layer")
    ax_energy.legend(frameon=False, ncol=1)
    energy_png, energy_pdf = save_required_figure_outputs(
        fig_energy, output_dir, "adaptive_tfim_energy_vs_layer"
    )
    plt.close(fig_energy)

    comparison_rows = _exact_vs_mps_rows(rows)
    fig_compare, ax_compare = plt.subplots(figsize=(4.8, 3.6))
    if comparison_rows:
        x_values = [row["exact_energy"] for row in comparison_rows]
        y_values = [row["mps_energy"] for row in comparison_rows]
        ax_compare.scatter(x_values, y_values, marker="o", color="black", label="final runs")
        lower = min(min(x_values), min(y_values))
        upper = max(max(x_values), max(y_values))
        ax_compare.plot([lower, upper], [lower, upper], linestyle="--", color="0.5", label="ideal")
    finalize_axes(ax_compare, "Exact energy", "MPS energy", "Adaptive TFIM exact vs MPS")
    ax_compare.legend(frameon=False)
    compare_png, compare_pdf = save_required_figure_outputs(
        fig_compare, output_dir, "adaptive_tfim_exact_vs_mps"
    )
    plt.close(fig_compare)

    fig_error, ax_error = plt.subplots(figsize=(5.2, 3.4))
    error_series = defaultdict(list)
    for row in comparison_rows:
        if row["max_bond_dim"] is None:
            continue
        label = f"n={row['n']} h={row['h']:.2f}"
        error_series[label].append((row["max_bond_dim"], row["abs_error"]))
    for label, points in sorted(error_series.items()):
        points = sorted(points)
        ax_error.plot([point[0] for point in points], [point[1] for point in points], marker="s", label=label)
    finalize_axes(ax_error, "max_bond_dim", "Absolute energy error", "Adaptive TFIM MPS error vs bond dimension")
    if error_series:
        ax_error.legend(frameon=False)
    error_png, error_pdf = save_required_figure_outputs(
        fig_error, output_dir, "adaptive_tfim_error_vs_max_bond_dim"
    )
    plt.close(fig_error)

    return {
        "style_used": style_used,
        "rows": rows,
        "comparison_rows": comparison_rows,
        "files": [
            energy_png,
            energy_pdf,
            compare_png,
            compare_pdf,
            error_png,
            error_pdf,
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Scientific plots for adaptive TFIM VQE scan data.")
    parser.add_argument("--scan-csv", required=True, help="Input adaptive TFIM VQE scan CSV.")
    parser.add_argument("--output-dir", default="adaptive_tfim_report", help="Output directory for plots.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional aggregated exact-vs-MPS CSV path.")
    args = parser.parse_args()

    report = generate_adaptive_tfim_report(args.scan_csv, args.output_dir)
    if args.csv_path is not None:
        write_adaptive_tfim_report_csv(args.csv_path, report["comparison_rows"])

    print("workflow=Adaptive TFIM VQE report")
    print(f"style={report['style_used']}")
    print(f"input_csv={args.scan_csv}")
    for file_path in report["files"]:
        print(f"plot={file_path}")
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
