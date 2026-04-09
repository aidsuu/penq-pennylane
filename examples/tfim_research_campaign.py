import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.tfim_groundstate_ansatz import DEVICE_NAME, parse_h_values
from QML.PenQ.examples.tfim_scan import evaluate_tfim_scan
from QML.PenQ.examples.tfim_variational_scaling import comparative_variational_rows
from QML.PenQ.examples.tfim_variational_scaling import write_tfim_variational_scaling_csv
from QML.PenQ.examples.tfim_ansatz_comparison import ansatz_comparison_rows
from QML.PenQ.examples.tfim_ansatz_comparison import write_tfim_ansatz_comparison_csv
from QML.PenQ.examples.tfim_grid_resolution_study import grid_resolution_rows
from QML.PenQ.examples.tfim_grid_resolution_study import write_tfim_grid_resolution_csv


def write_reference_scan_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["n_qubits", "h", "state", "energy", "analytic"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def campaign_output_paths(output_dir):
    output_dir = Path(output_dir)
    return {
        "reference_scan": output_dir / "tfim_reference_scan.csv",
        "variational_scaling": output_dir / "tfim_variational_scaling.csv",
        "ansatz_comparison": output_dir / "tfim_ansatz_comparison.csv",
        "grid_resolution": output_dir / "tfim_grid_resolution.csv",
    }


def run_tfim_research_campaign(output_dir, h_values=(0.0, 0.5, 1.0)):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = campaign_output_paths(output_dir)

    reference_rows = []
    for num_qubits in (6, 8):
        reference_rows.extend(evaluate_tfim_scan(num_qubits, h_values))
    write_reference_scan_csv(paths["reference_scan"], reference_rows)

    variational_rows = comparative_variational_rows(qubit_counts=(6, 8), h_values=h_values, num_theta=9)
    write_tfim_variational_scaling_csv(paths["variational_scaling"], variational_rows)

    comparison_rows = ansatz_comparison_rows(qubit_counts=(6, 8), h_values=h_values, num_theta=7)
    write_tfim_ansatz_comparison_csv(paths["ansatz_comparison"], comparison_rows)

    grid_rows = grid_resolution_rows(
        qubit_counts=(6, 8),
        h_values=h_values,
        grid_sizes={"coarse": 3, "medium": 5, "fine": 7},
    )
    write_tfim_grid_resolution_csv(paths["grid_resolution"], grid_rows)

    return {
        "output_dir": output_dir,
        "paths": paths,
        "row_counts": {
            "reference_scan": len(reference_rows),
            "variational_scaling": len(variational_rows),
            "ansatz_comparison": len(comparison_rows),
            "grid_resolution": len(grid_rows),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM research campaign.")
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="tfim_research_campaign",
        help="Directory where campaign CSV outputs will be written.",
    )
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    result = run_tfim_research_campaign(args.output_dir, h_values=parse_h_values(args.h_grid))

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM research campaign")
    print(f"output_dir={result['output_dir']}")
    for key in ("reference_scan", "variational_scaling", "ansatz_comparison", "grid_resolution"):
        print(f"{key}: rows={result['row_counts'][key]} file={result['paths'][key]}")


if __name__ == "__main__":
    main()
