import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ.examples.plotting_utils import finalize_axes
from QML.PenQ.examples.plotting_utils import load_publication_pyplot
from QML.PenQ.examples.plotting_utils import save_required_figure_outputs
from QML.PenQ.examples.tfim_dynamics_utils import final_exact_vs_mps_rows
from QML.PenQ.examples.tfim_dynamics_utils import read_tfim_dynamics_scan_csv


def run_summary_report(imaginary_scan_csv, real_scan_csv, output_dir="."):
    plt, _ = load_publication_pyplot()
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    imag_rows = [row for row in read_tfim_dynamics_scan_csv(imaginary_scan_csv) if row["dynamics"] == "imaginary"]
    real_rows = [row for row in read_tfim_dynamics_scan_csv(real_scan_csv) if row["dynamics"] == "real"]

    imag_final = final_exact_vs_mps_rows(imag_rows)
    real_final = final_exact_vs_mps_rows(real_rows)

    fig, ax = plt.subplots(figsize=(6, 4))
    if imag_final:
        ax.scatter(
            ["imaginary"] * len(imag_final),
            [row["abs_error"] for row in imag_final],
            marker="o",
            label="imaginary-time",
        )
    if real_final:
        ax.scatter(
            ["real"] * len(real_final),
            [row["abs_error"] for row in real_final],
            marker="s",
            label="real-time",
        )
    ax.set_yscale("log")
    finalize_axes(ax, "Dynamics", "|E_mps - E_exact|", "TFIM Dynamics Exact vs MPS Summary")
    ax.legend(frameon=False)
    save_required_figure_outputs(fig, output_dir, "tfim_dynamics_exact_vs_mps_summary")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summary exact-vs-MPS plot over imaginary and real-time TFIM scans.")
    parser.add_argument("--imaginary-scan-csv", default="imaginary_tfim_scan.csv")
    parser.add_argument("--real-scan-csv", default="real_tfim_scan.csv")
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    run_summary_report(args.imaginary_scan_csv, args.real_scan_csv, output_dir=args.output_dir)
