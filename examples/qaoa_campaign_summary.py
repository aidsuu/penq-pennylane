import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.qaoa_ising_small import DEVICE_NAME
from QML.PenQ.examples.qaoa_research_campaign import qaoa_campaign_output_paths


def read_csv_rows(path):
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def qaoa_campaign_row_counts(paths):
    return {name: len(read_csv_rows(path)) for name, path in paths.items() if Path(path).exists()}


def build_qaoa_campaign_summary(input_dir):
    paths = qaoa_campaign_output_paths(input_dir)
    row_counts = qaoa_campaign_row_counts(paths)
    grid_search_rows = read_csv_rows(paths["grid_search"])
    landscape_rows = read_csv_rows(paths["landscape"])

    best_grid_search = min(grid_search_rows, key=lambda row: float(row["best_energy"]))
    best_landscape = min(landscape_rows, key=lambda row: float(row["energy"]))
    worst_landscape = max(landscape_rows, key=lambda row: float(row["energy"]))

    summary = {
        "grid_search_best_num_qubits": int(best_grid_search["num_qubits"]),
        "grid_search_best_energy": float(best_grid_search["best_energy"]),
        "grid_search_best_gamma": float(best_grid_search["best_gamma"]),
        "grid_search_best_beta": float(best_grid_search["best_beta"]),
        "landscape_best_n": int(best_landscape["n"]),
        "landscape_best_gamma": float(best_landscape["gamma"]),
        "landscape_best_beta": float(best_landscape["beta"]),
        "landscape_best_energy": float(best_landscape["energy"]),
        "landscape_worst_energy": float(worst_landscape["energy"]),
        "landscape_energy_span": float(float(worst_landscape["energy"]) - float(best_landscape["energy"])),
    }

    return {"paths": paths, "row_counts": row_counts, "summary": summary}


def write_qaoa_campaign_summary_csv(path, summary):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "grid_search_best_num_qubits",
        "grid_search_best_energy",
        "grid_search_best_gamma",
        "grid_search_best_beta",
        "landscape_best_n",
        "landscape_best_gamma",
        "landscape_best_beta",
        "landscape_best_energy",
        "landscape_worst_energy",
        "landscape_energy_span",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(summary)


def main():
    parser = argparse.ArgumentParser(description="Deterministic QAOA campaign summary.")
    parser.add_argument(
        "--input-dir",
        dest="input_dir",
        default="qaoa_research_campaign",
        help="Directory containing QAOA campaign CSV outputs.",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default=None,
        help="Optional CSV output path for the aggregated summary.",
    )
    args = parser.parse_args()

    result = build_qaoa_campaign_summary(args.input_dir)
    if args.csv_path is not None:
        write_qaoa_campaign_summary_csv(args.csv_path, result["summary"])

    print(f"device={DEVICE_NAME}")
    print("workflow=QAOA campaign summary")
    print(f"input_dir={Path(args.input_dir)}")
    for key in ("grid_search", "landscape"):
        print(f"{key}: rows={result['row_counts'][key]}")
    summary = result["summary"]
    print(
        f"best_grid_search=n{summary['grid_search_best_num_qubits']} "
        f"energy={summary['grid_search_best_energy']:.8f} "
        f"gamma={summary['grid_search_best_gamma']:.8f} beta={summary['grid_search_best_beta']:.8f}"
    )
    print(
        f"best_landscape=n{summary['landscape_best_n']} "
        f"energy={summary['landscape_best_energy']:.8f} "
        f"gamma={summary['landscape_best_gamma']:.8f} beta={summary['landscape_best_beta']:.8f}"
    )
    print(
        f"landscape_span={summary['landscape_energy_span']:.8f} "
        f"worst_energy={summary['landscape_worst_energy']:.8f}"
    )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
