import csv
import pathlib
import sys
import argparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ import compare_imag_time_exact_vs_mps
from QML.PenQ.examples.imaginary_time_tfim_scan import imaginary_time_tfim_scan_rows
from QML.PenQ.examples.plotting_utils import finalize_axes
from QML.PenQ.examples.plotting_utils import load_publication_pyplot
from QML.PenQ.examples.plotting_utils import save_required_figure_outputs
from QML.PenQ.examples.tfim_dynamics_utils import final_exact_vs_mps_rows
from QML.PenQ.examples.tfim_dynamics_utils import read_tfim_dynamics_scan_csv
from QML.PenQ.examples.tfim_dynamics_utils import write_tfim_dynamics_scan_csv


def run_and_save_report(scan_csv="imaginary_tfim_scan.csv", output_dir=".", report_csv="imaginary_tfim_report.csv"):
    print("Generating Imaginary Time TFIM Report...")
    plt, style_used = load_publication_pyplot()
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scan_path = pathlib.Path(scan_csv)
    if scan_path.exists():
        rows = read_tfim_dynamics_scan_csv(scan_path)
    else:
        rows = imaginary_time_tfim_scan_rows(
            qubit_counts=(6,),
            J_values=(1.0,),
            h_values=(0.5,),
            include_exact=True,
            mps_bond_dims=(4,),
            delta_tau=0.05,
            steps=15,
            max_layers=3,
            svd_cutoff=1e-12,
            seed=42,
        )
        write_tfim_dynamics_scan_csv(scan_path, rows)
        print(f"Wrote {scan_path}")

    rows = [row for row in rows if row["dynamics"] == "imaginary"]

    with open(report_csv, "w", newline="", encoding="utf-8") as f:
        fields = [
            "dynamics",
            "n",
            "J",
            "h",
            "backend",
            "step",
            "time",
            "step_size",
            "energy",
            "energy_per_site",
            "expval_x0",
            "expval_z0z1",
            "max_bond_dim",
            "svd_cutoff",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {report_csv}")

    exact_rows = [row for row in rows if row["backend"] == "qml"]
    mps_rows = [row for row in rows if row["backend"] == "mps"]

    # Plot 1: Energy vs Step
    fig_energy, ax_energy = plt.subplots(figsize=(6, 4))

    exact_steps = [r["step"] for r in exact_rows]
    exact_energy = [r["energy"] for r in exact_rows]
    mps_steps = [r["step"] for r in mps_rows]
    mps_energy = [r["energy"] for r in mps_rows]

    ax_energy.plot(exact_steps, exact_energy, "o-", label="Exact")
    ax_energy.plot(mps_steps, mps_energy, "s--", label="MPS")
    finalize_axes(ax_energy, "VITE Step", "Energy", "Variational Imaginary Time Evolution")
    ax_energy.legend(frameon=False)
    save_required_figure_outputs(fig_energy, output_dir, "imaginary_tfim_energy_vs_step")
    plt.close(fig_energy)
    
    # Plot 2: Exact vs MPS at final step (bar chart comparison)
    fig_compare, ax_compare = plt.subplots(figsize=(6, 4))
    comparison_rows = final_exact_vs_mps_rows(rows)
    if comparison_rows:
        exact_energy_final = comparison_rows[0]["exact_energy"]
        mps_energy_final = comparison_rows[0]["mps_energy"]
    else:
        exact_energy_final = exact_energy[-1]
        mps_energy_final = mps_energy[-1]
    x = [1]
    w = 0.2
    ax_compare.bar([i - w / 2 for i in x], [exact_energy_final], w, label="Exact Final")
    ax_compare.bar([i + w / 2 for i in x], [mps_energy_final], w, label="MPS Final")
    ax_compare.set_xticks(x)
    ax_compare.set_xticklabels(["Energy"])
    finalize_axes(ax_compare, "", "Value", "Exact vs MPS Final States")
    ax_compare.legend(frameon=False)
    save_required_figure_outputs(fig_compare, output_dir, "imaginary_tfim_exact_vs_mps")
    plt.close(fig_compare)

    # Plot 3: Error vs Max Bond Dim
    bond_dims = [2, 4, 6]
    errors = []

    for chi in bond_dims:
        comp = compare_imag_time_exact_vs_mps(
            n=4, J=1.0, h=0.5, delta_tau=0.05, steps=10,
            max_layers=2, max_bond_dim=chi, svd_cutoff=0.0, seed=123
        )
        errors.append(comp["abs_energy_error_per_site"])

    fig_error, ax_error = plt.subplots(figsize=(6, 4))
    ax_error.plot(bond_dims, errors, "D-")
    ax_error.set_yscale("log")
    finalize_axes(
        ax_error,
        r"Max Bond Dimension ($\chi$)",
        "Absolute Energy Error Per Site",
        "VITE MPS Truncation Error",
    )
    save_required_figure_outputs(fig_error, output_dir, "imaginary_tfim_error_vs_max_bond_dim")
    plt.close(fig_error)

    print(f"style={style_used}")
    print("Saved all mandatory plots.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scientific plots for imaginary-time TFIM scan data.")
    parser.add_argument("--scan-csv", default="imaginary_tfim_scan.csv", help="Input or generated scan CSV path.")
    parser.add_argument("--output-dir", default=".", help="Output directory for plots.")
    parser.add_argument("--csv", dest="csv_path", default="imaginary_tfim_report.csv", help="Output report CSV path.")
    args = parser.parse_args()
    run_and_save_report(scan_csv=args.scan_csv, output_dir=args.output_dir, report_csv=args.csv_path)
