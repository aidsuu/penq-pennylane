import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ.examples.plotting_utils import finalize_axes
from QML.PenQ.examples.plotting_utils import load_publication_pyplot
from QML.PenQ.examples.plotting_utils import save_required_figure_outputs
from QML.PenQ.examples.cubic_tfim_dynamics_utils import read_cubic_tfim_imag_time_csv
from QML.PenQ.examples.cubic_tfim_dynamics_utils import read_cubic_tfim_real_time_csv
from QML.PenQ.examples.cubic_tfim_dynamics_utils import write_cubic_tfim_imag_time_csv
from QML.PenQ.examples.cubic_tfim_dynamics_utils import write_cubic_tfim_real_time_csv
from QML.PenQ.examples.cubic_tfim_imag_time import cubic_tfim_imag_time_rows
from QML.PenQ.examples.cubic_tfim_real_time import cubic_tfim_real_time_rows


def run_cubic_tfim_dynamics_report(real_csv="cubic_tfim_real_time.csv", imag_csv="cubic_tfim_imag_time.csv", output_dir="."):
    plt, style_used = load_publication_pyplot()
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    real_path = pathlib.Path(real_csv)
    if real_path.exists():
        real_rows = read_cubic_tfim_real_time_csv(real_path)
    else:
        real_rows = cubic_tfim_real_time_rows()
        write_cubic_tfim_real_time_csv(real_path, real_rows)

    imag_path = pathlib.Path(imag_csv)
    if imag_path.exists():
        imag_rows = read_cubic_tfim_imag_time_csv(imag_path)
    else:
        imag_rows = cubic_tfim_imag_time_rows()
        write_cubic_tfim_imag_time_csv(imag_path, imag_rows)

    real_exact = [row for row in real_rows if row["backend"] == "qml"]
    real_mps = [row for row in real_rows if row["backend"] == "mps"]

    fig_rt_energy, ax_rt_energy = plt.subplots(figsize=(6, 4))
    ax_rt_energy.plot([row["time"] for row in real_exact], [row["energy"] for row in real_exact], "o-", label="Exact")
    ax_rt_energy.plot([row["time"] for row in real_mps], [row["energy"] for row in real_mps], "s--", label="MPS")
    finalize_axes(ax_rt_energy, "Time", "Energy", "Cubic TFIM Real-Time Energy vs Time")
    ax_rt_energy.legend(frameon=False)
    save_required_figure_outputs(fig_rt_energy, output_dir, "cubic_tfim_real_time_energy_vs_time")
    plt.close(fig_rt_energy)

    fig_rt_obs, ax_rt_obs = plt.subplots(figsize=(6, 4))
    ax_rt_obs.plot([row["time"] for row in real_exact], [row["magnetization_x"] for row in real_exact], "-", label="Exact <X>")
    ax_rt_obs.plot([row["time"] for row in real_exact], [row["magnetization_z"] for row in real_exact], "--", label="Exact <Z>")
    ax_rt_obs.plot([row["time"] for row in real_mps], [row["magnetization_x"] for row in real_mps], ":", label="MPS <X>")
    ax_rt_obs.plot([row["time"] for row in real_mps], [row["magnetization_z"] for row in real_mps], "-.", label="MPS <Z>")
    finalize_axes(ax_rt_obs, "Time", "Observable", "Cubic TFIM Real-Time Observables vs Time")
    ax_rt_obs.legend(frameon=False, ncol=2)
    save_required_figure_outputs(fig_rt_obs, output_dir, "cubic_tfim_real_time_observables_vs_time")
    plt.close(fig_rt_obs)

    imag_exact = [row for row in imag_rows if row["backend"] == "qml"]
    imag_mps = [row for row in imag_rows if row["backend"] == "mps"]

    fig_it_energy, ax_it_energy = plt.subplots(figsize=(6, 4))
    ax_it_energy.plot([row["step"] for row in imag_exact], [row["energy"] for row in imag_exact], "o-", label="Exact")
    ax_it_energy.plot([row["step"] for row in imag_mps], [row["energy"] for row in imag_mps], "s--", label="MPS")
    finalize_axes(ax_it_energy, "Imag-Time Step", "Energy", "Cubic TFIM Imag-Time Energy vs Step")
    ax_it_energy.legend(frameon=False)
    save_required_figure_outputs(fig_it_energy, output_dir, "cubic_tfim_imag_time_energy_vs_step")
    plt.close(fig_it_energy)

    fig_it_cmp, ax_it_cmp = plt.subplots(figsize=(6, 4))
    if imag_exact and imag_mps:
        pair_count = min(len(imag_exact), len(imag_mps))
        exact_energy = [row["energy"] for row in imag_exact[:pair_count]]
        mps_energy = [row["energy"] for row in imag_mps[:pair_count]]
        ax_it_cmp.scatter(exact_energy, mps_energy, marker="o")
        lower = min(min(exact_energy), min(mps_energy))
        upper = max(max(exact_energy), max(mps_energy))
        ax_it_cmp.plot([lower, upper], [lower, upper], "--", color="0.5")
    finalize_axes(ax_it_cmp, "Exact Energy", "MPS Energy", "Cubic TFIM Imag-Time Exact vs MPS")
    save_required_figure_outputs(fig_it_cmp, output_dir, "cubic_tfim_imag_time_exact_vs_mps")
    plt.close(fig_it_cmp)

    return {
        "style_used": style_used,
        "real_rows": real_rows,
        "imag_rows": imag_rows,
    }


def main():
    parser = argparse.ArgumentParser(description="Scientific plots for cubic TFIM real-time and imag-time trajectories.")
    parser.add_argument("--real-csv", default="cubic_tfim_real_time.csv", help="Input or generated real-time CSV path.")
    parser.add_argument("--imag-csv", default="cubic_tfim_imag_time.csv", help="Input or generated imaginary-time CSV path.")
    parser.add_argument("--output-dir", default=".", help="Output directory for plots.")
    args = parser.parse_args()

    report = run_cubic_tfim_dynamics_report(real_csv=args.real_csv, imag_csv=args.imag_csv, output_dir=args.output_dir)
    print("workflow=3D cubic TFIM dynamics report")
    print(f"style={report['style_used']}")
    print("saved=cubic_tfim_real_time_energy_vs_time.[png|pdf]")
    print("saved=cubic_tfim_real_time_observables_vs_time.[png|pdf]")
    print("saved=cubic_tfim_imag_time_energy_vs_step.[png|pdf]")
    print("saved=cubic_tfim_imag_time_exact_vs_mps.[png|pdf]")


if __name__ == "__main__":
    main()
