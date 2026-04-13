import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ.examples.plotting_utils import finalize_axes
from QML.PenQ.examples.plotting_utils import load_publication_pyplot
from QML.PenQ.examples.plotting_utils import save_required_figure_outputs
from QML.PenQ.examples.real_time_tfim_scan import real_time_tfim_scan_rows
from QML.PenQ.examples.tfim_dynamics_utils import final_exact_vs_mps_rows
from QML.PenQ.examples.tfim_dynamics_utils import read_tfim_dynamics_scan_csv
from QML.PenQ.examples.tfim_dynamics_utils import write_tfim_dynamics_scan_csv


def run_and_save_report(scan_csv="real_tfim_scan.csv", output_dir=".", report_csv="real_tfim_report.csv"):
    print("Generating Real-Time TFIM Report...")
    plt, style_used = load_publication_pyplot()
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scan_path = pathlib.Path(scan_csv)
    if scan_path.exists():
        rows = read_tfim_dynamics_scan_csv(scan_path)
    else:
        rows = real_time_tfim_scan_rows(
            qubit_counts=(6,),
            J_values=(1.0,),
            h_values=(0.5,),
            include_exact=True,
            mps_bond_dims=(4,),
            dt=0.05,
            steps=20,
            svd_cutoff=1e-12,
        )
        write_tfim_dynamics_scan_csv(scan_path, rows)
        print(f"Wrote {scan_path}")

    rows = [row for row in rows if row["dynamics"] == "real"]
    write_tfim_dynamics_scan_csv(report_csv, rows)
    print(f"Wrote {report_csv}")

    exact_rows = [row for row in rows if row["backend"] == "qml"]
    mps_rows = [row for row in rows if row["backend"] == "mps"]

    available_bonds = sorted({row["max_bond_dim"] for row in mps_rows if row["max_bond_dim"] is not None})
    selected_bond = available_bonds[0] if available_bonds else None
    if selected_bond is None:
        mps_selected = mps_rows
    else:
        mps_selected = [row for row in mps_rows if row["max_bond_dim"] == selected_bond]

    fig_energy, ax_energy = plt.subplots(figsize=(6, 4))
    ax_energy.plot([r["time"] for r in exact_rows], [r["energy"] for r in exact_rows], "o-", label="Exact")
    mps_label = "MPS" if selected_bond is None else f"MPS chi={selected_bond}"
    ax_energy.plot([r["time"] for r in mps_selected], [r["energy"] for r in mps_selected], "s--", label=mps_label)
    finalize_axes(ax_energy, "Time", "Energy", "Real-Time TFIM Energy vs Time")
    ax_energy.legend(frameon=False)
    save_required_figure_outputs(fig_energy, output_dir, "real_tfim_energy_vs_time")
    plt.close(fig_energy)

    fig_obs, ax_obs = plt.subplots(figsize=(6, 4))
    ax_obs.plot([r["time"] for r in exact_rows], [r["expval_x0"] for r in exact_rows], "-", label="Exact <X0>")
    ax_obs.plot([r["time"] for r in exact_rows], [r["expval_z0z1"] for r in exact_rows], "--", label="Exact <Z0Z1>")
    ax_obs.plot([r["time"] for r in mps_selected], [r["expval_x0"] for r in mps_selected], ":", label=f"{mps_label} <X0>")
    ax_obs.plot(
        [r["time"] for r in mps_selected],
        [r["expval_z0z1"] for r in mps_selected],
        "-.",
        label=f"{mps_label} <Z0Z1>",
    )
    finalize_axes(ax_obs, "Time", "Observable", "Real-Time TFIM Observables vs Time")
    ax_obs.legend(frameon=False, ncol=2)
    save_required_figure_outputs(fig_obs, output_dir, "real_tfim_observables_vs_time")
    plt.close(fig_obs)

    fig_compare, ax_compare = plt.subplots(figsize=(6, 4))
    paired_length = min(len(exact_rows), len(mps_selected))
    exact_energy = [r["energy"] for r in exact_rows[:paired_length]]
    mps_energy = [r["energy"] for r in mps_selected[:paired_length]]
    ax_compare.scatter(exact_energy, mps_energy, marker="o", label="time points")
    if exact_energy and mps_energy:
        lower = min(min(exact_energy), min(mps_energy))
        upper = max(max(exact_energy), max(mps_energy))
        ax_compare.plot([lower, upper], [lower, upper], "--", color="0.5", label="ideal")
    finalize_axes(ax_compare, "Exact Energy", "MPS Energy", "Real-Time TFIM Exact vs MPS")
    ax_compare.legend(frameon=False)
    save_required_figure_outputs(fig_compare, output_dir, "real_tfim_exact_vs_mps")
    plt.close(fig_compare)

    comparison_rows = final_exact_vs_mps_rows(rows)
    print(f"style={style_used}")
    print(f"comparison_rows={len(comparison_rows)}")
    print("Saved all mandatory plots.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scientific plots for real-time TFIM scan data.")
    parser.add_argument("--scan-csv", default="real_tfim_scan.csv", help="Input or generated scan CSV path.")
    parser.add_argument("--output-dir", default=".", help="Output directory for plots.")
    parser.add_argument("--csv", dest="csv_path", default="real_tfim_report.csv", help="Output report CSV path.")
    args = parser.parse_args()
    run_and_save_report(scan_csv=args.scan_csv, output_dir=args.output_dir, report_csv=args.csv_path)
