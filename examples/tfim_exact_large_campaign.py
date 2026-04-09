import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.tfim_scaling_scan import evaluate_tfim_observables, parse_h_values


DEVICE_NAME = "penq.qml_starter"


def validate_tfim_exact_large_inputs(qubit_counts, h_values):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    for num_qubits in qubit_counts:
        if num_qubits not in {8, 10, 12}:
            raise ValueError("TFIM exact large campaign expects qubit counts chosen from 8, 10, 12.")


def parse_n_values(text):
    return tuple(int(value) for value in text.split(","))


def tfim_exact_large_rows(qubit_counts=(8, 10, 12), h_values=(0.0, 0.5, 1.0), state_name="all_plus"):
    validate_tfim_exact_large_inputs(qubit_counts, h_values)
    rows = []
    for num_qubits in qubit_counts:
        for h in h_values:
            values = evaluate_tfim_observables(num_qubits, h, state_name)
            rows.append(
                {
                    "n": int(num_qubits),
                    "h": float(h),
                    "energy": float(values["energy"]),
                    "energy_per_site": float(values["energy"] / num_qubits),
                    "expval_x0": float(values["x0"]),
                    "expval_z0z1": float(values["zz01"]),
                }
            )
    return rows


def write_tfim_exact_large_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["n", "h", "energy", "energy_per_site", "expval_x0", "expval_z0z1"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM exact large campaign.")
    parser.add_argument("--csv", dest="csv_path", default="tfim_exact_large_campaign.csv", help="CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0",
        help="Comma-separated deterministic h grid.",
    )
    parser.add_argument(
        "--n-grid",
        dest="n_grid",
        default="8,10,12",
        help="Comma-separated deterministic qubit-count grid.",
    )
    args = parser.parse_args()

    rows = tfim_exact_large_rows(
        qubit_counts=parse_n_values(args.n_grid),
        h_values=parse_h_values(args.h_grid),
    )
    write_tfim_exact_large_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM exact large campaign")
    print("state = all_plus")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} "
            f"energy={row['energy']:.8f} e/site={row['energy_per_site']:.8f} "
            f"x0={row['expval_x0']:.8f} zz01={row['expval_z0z1']:.8f}"
        )
    print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
