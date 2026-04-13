import argparse
import csv
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ.examples.plotting_utils import finalize_axes
from QML.PenQ.examples.plotting_utils import load_publication_pyplot
from QML.PenQ.examples.plotting_utils import save_required_figure_outputs
from QML.PenQ.examples.cubic_tfim_scan import CUBIC_TFIM_SCAN_FIELDNAMES
from QML.PenQ.examples.cubic_tfim_scan import cubic_tfim_scan_rows
from QML.PenQ.examples.cubic_tfim_scan import write_cubic_tfim_scan_csv


def read_cubic_tfim_scan_csv(path):
    rows = []
    with pathlib.Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CUBIC_TFIM_SCAN_FIELDNAMES:
            raise ValueError(
                f"Unexpected cubic TFIM scan CSV header: {reader.fieldnames}. "
                f"Expected {CUBIC_TFIM_SCAN_FIELDNAMES}."
            )
        for row in reader:
            rows.append(
                {
                    "Lx": int(row["Lx"]),
                    "Ly": int(row["Ly"]),
                    "Lz": int(row["Lz"]),
                    "n_sites": int(row["n_sites"]),
                    "Jx": float(row["Jx"]),
                    "Jy": float(row["Jy"]),
                    "Jz": float(row["Jz"]),
                    "h": float(row["h"]),
                    "backend": row["backend"],
                    "energy": float(row["energy"]),
                    "energy_per_site": float(row["energy_per_site"]),
                    "magnetization_x": float(row["magnetization_x"]),
                    "magnetization_z": float(row["magnetization_z"]),
                    "nn_zz_x": float(row["nn_zz_x"]),
                    "nn_zz_y": float(row["nn_zz_y"]),
                    "nn_zz_z": float(row["nn_zz_z"]),
                    "max_bond_dim": None if row["max_bond_dim"] == "" else int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                }
            )
    return rows


def _exact_vs_mps_pairs(rows):
    exact = {}
    pairs = []
    for row in rows:
        key = (row["Lx"], row["Ly"], row["Lz"], row["Jx"], row["Jy"], row["Jz"], row["h"])
        if row["backend"] == "qml":
            exact[key] = row

    for row in rows:
        key = (row["Lx"], row["Ly"], row["Lz"], row["Jx"], row["Jy"], row["Jz"], row["h"])
        if row["backend"] != "mps" or key not in exact:
            continue
        pairs.append(
            {
                "Lx": row["Lx"],
                "Ly": row["Ly"],
                "Lz": row["Lz"],
                "h": row["h"],
                "max_bond_dim": row["max_bond_dim"],
                "exact_energy": exact[key]["energy"],
                "mps_energy": row["energy"],
                "abs_error": abs(row["energy"] - exact[key]["energy"]),
            }
        )
    return pairs


def run_cubic_tfim_report(scan_csv="cubic_tfim_scan.csv", output_dir="."):
    plt, style_used = load_publication_pyplot()
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scan_path = pathlib.Path(scan_csv)
    if scan_path.exists():
        rows = read_cubic_tfim_scan_csv(scan_path)
    else:
        rows = cubic_tfim_scan_rows()
        write_cubic_tfim_scan_csv(scan_path, rows)

    fig_energy, ax_energy = plt.subplots(figsize=(6, 4))
    energy_series = defaultdict(list)
    for row in rows:
        bond_label = "exact" if row["backend"] == "qml" else f"mps-b{row['max_bond_dim']}"
        label = f"{row['Lx']}x{row['Ly']}x{row['Lz']} {bond_label}"
        energy_series[label].append((row["h"], row["energy_per_site"]))

    for label, points in sorted(energy_series.items()):
        points = sorted(points)
        ax_energy.plot([p[0] for p in points], [p[1] for p in points], marker="o", label=label)
    finalize_axes(ax_energy, "h", "Energy per site", "Cubic TFIM Energy vs Field")
    ax_energy.legend(frameon=False, ncol=2)
    save_required_figure_outputs(fig_energy, output_dir, "cubic_tfim_energy_vs_field")
    plt.close(fig_energy)

    fig_mag, ax_mag = plt.subplots(figsize=(6, 4))
    mag_series = defaultdict(list)
    for row in rows:
        if row["backend"] != "qml":
            continue
        label_x = f"{row['Lx']}x{row['Ly']}x{row['Lz']} exact <X>"
        label_z = f"{row['Lx']}x{row['Ly']}x{row['Lz']} exact <Z>"
        mag_series[label_x].append((row["h"], row["magnetization_x"]))
        mag_series[label_z].append((row["h"], row["magnetization_z"]))

    for label, points in sorted(mag_series.items()):
        points = sorted(points)
        ax_mag.plot([p[0] for p in points], [p[1] for p in points], marker="s", label=label)
    finalize_axes(ax_mag, "h", "Magnetization", "Cubic TFIM Magnetization vs Field")
    ax_mag.legend(frameon=False, ncol=2)
    save_required_figure_outputs(fig_mag, output_dir, "cubic_tfim_magnetization_vs_field")
    plt.close(fig_mag)

    fig_compare, ax_compare = plt.subplots(figsize=(6, 4))
    pairs = _exact_vs_mps_pairs(rows)
    if pairs:
        ax_compare.scatter([p["exact_energy"] for p in pairs], [p["mps_energy"] for p in pairs], marker="o")
        lower = min(min(p["exact_energy"] for p in pairs), min(p["mps_energy"] for p in pairs))
        upper = max(max(p["exact_energy"] for p in pairs), max(p["mps_energy"] for p in pairs))
        ax_compare.plot([lower, upper], [lower, upper], "--", color="0.5")
    finalize_axes(ax_compare, "Exact energy", "MPS energy", "Cubic TFIM Exact vs MPS")
    save_required_figure_outputs(fig_compare, output_dir, "cubic_tfim_exact_vs_mps")
    plt.close(fig_compare)

    return {
        "style_used": style_used,
        "rows": rows,
        "comparison_rows": pairs,
    }


def main():
    parser = argparse.ArgumentParser(description="Scientific plots for 3D cubic TFIM scan data.")
    parser.add_argument("--scan-csv", default="cubic_tfim_scan.csv", help="Input or generated scan CSV path.")
    parser.add_argument("--output-dir", default=".", help="Output directory for plots.")
    args = parser.parse_args()

    report = run_cubic_tfim_report(scan_csv=args.scan_csv, output_dir=args.output_dir)
    print("workflow=3D cubic TFIM report")
    print(f"style={report['style_used']}")
    print("saved=cubic_tfim_energy_vs_field.[png|pdf]")
    print("saved=cubic_tfim_magnetization_vs_field.[png|pdf]")
    print("saved=cubic_tfim_exact_vs_mps.[png|pdf]")


if __name__ == "__main__":
    main()
