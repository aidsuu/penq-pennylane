import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.qaoa_ising_small import DEVICE_NAME, qaoa_grid_search
from QML.PenQ.examples.qaoa_chain_landscape import qaoa_chain_landscape, write_qaoa_landscape_csv


def write_qaoa_grid_search_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["num_qubits", "best_energy", "best_gamma", "best_beta", "exact_classical_minimum"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def qaoa_campaign_output_paths(output_dir):
    output_dir = Path(output_dir)
    return {
        "grid_search": output_dir / "qaoa_grid_search.csv",
        "landscape": output_dir / "qaoa_chain_landscape.csv",
    }


def run_qaoa_research_campaign(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = qaoa_campaign_output_paths(output_dir)

    grid_search_rows = [
        qaoa_grid_search(num_qubits=4, num_gamma=9, num_beta=9),
        qaoa_grid_search(num_qubits=6, num_gamma=9, num_beta=9),
    ]
    write_qaoa_grid_search_csv(paths["grid_search"], grid_search_rows)

    landscape_rows = qaoa_chain_landscape(num_qubits=8, num_gamma=7, num_beta=7)
    write_qaoa_landscape_csv(paths["landscape"], landscape_rows)

    return {
        "output_dir": output_dir,
        "paths": paths,
        "row_counts": {
            "grid_search": len(grid_search_rows),
            "landscape": len(landscape_rows),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic QAOA research campaign.")
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="qaoa_research_campaign",
        help="Directory where campaign CSV outputs will be written.",
    )
    args = parser.parse_args()

    result = run_qaoa_research_campaign(args.output_dir)

    print(f"device={DEVICE_NAME}")
    print("workflow=QAOA research campaign")
    print(f"output_dir={result['output_dir']}")
    for key in ("grid_search", "landscape"):
        print(f"{key}: rows={result['row_counts'][key]} file={result['paths'][key]}")


if __name__ == "__main__":
    main()
