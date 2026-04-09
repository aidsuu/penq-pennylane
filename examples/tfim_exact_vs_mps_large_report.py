import argparse
import csv
from pathlib import Path

import pennylane as qml

from QML.PenQ.examples.tfim_mps_truncation_scan import tfim_style_chain_energy


STATEVECTOR_DEVICE_NAME = "penq.qml_starter"


def read_csv_rows(path):
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_tfim_exact_vs_mps_large_report(exact_csv, mps_csv):
    exact_path = Path(exact_csv)
    mps_path = Path(mps_csv)

    exact_rows = read_csv_rows(exact_path)
    mps_rows = read_csv_rows(mps_path)

    exact_by_key = {(int(row["n"]), float(row["h"])): row for row in exact_rows}
    reference_energy_cache = {}
    overlap_rows = []

    for row in mps_rows:
        key = (int(row["n"]), float(row["h"]))
        if key not in exact_by_key:
            continue
        if key not in reference_energy_cache:
            num_qubits, h = key
            dev = qml.device(STATEVECTOR_DEVICE_NAME, wires=num_qubits)
            reference_energy_cache[key] = float(tfim_style_chain_energy(dev, num_qubits, h))
        reference_energy = reference_energy_cache[key]
        mps_energy = float(row["mps_energy"])
        abs_error = abs(mps_energy - reference_energy)
        overlap_rows.append(
            {
                "n": int(row["n"]),
                "h": float(row["h"]),
                "max_bond_dim": int(row["max_bond_dim"]),
                "svd_cutoff": float(row["svd_cutoff"]),
                "reference_energy": reference_energy,
                "mps_energy": mps_energy,
                "abs_error": float(abs_error),
                "energy_error_per_site": float(abs_error / int(row["n"])),
            }
        )

    overlap_rows.sort(key=lambda row: (row["n"], row["h"], row["max_bond_dim"], row["svd_cutoff"]))
    return {
        "exact_csv": exact_path,
        "mps_csv": mps_path,
        "exact_row_count": len(exact_rows),
        "mps_row_count": len(mps_rows),
        "overlap_row_count": len(overlap_rows),
        "reference_workflow": "sum_i <Z_i Z_{i+1}> on the deterministic TFIM-style chain ansatz",
        "rows": overlap_rows,
    }


def write_tfim_exact_vs_mps_large_report_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "max_bond_dim",
        "svd_cutoff",
        "reference_energy",
        "mps_energy",
        "abs_error",
        "energy_error_per_site",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM exact-vs-MPS large report.")
    parser.add_argument("--exact-csv", dest="exact_csv", required=True, help="Exact campaign CSV path.")
    parser.add_argument("--mps-csv", dest="mps_csv", required=True, help="MPS campaign CSV path.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional output CSV path.")
    args = parser.parse_args()

    result = build_tfim_exact_vs_mps_large_report(args.exact_csv, args.mps_csv)
    if args.csv_path is not None:
        write_tfim_exact_vs_mps_large_report_csv(args.csv_path, result["rows"])

    print("workflow=TFIM exact-vs-MPS large report")
    print(f"exact_csv={result['exact_csv']}")
    print(f"mps_csv={result['mps_csv']}")
    print(f"reference_workflow={result['reference_workflow']}")
    print(
        f"exact_rows={result['exact_row_count']} mps_rows={result['mps_row_count']} overlap_rows={result['overlap_row_count']}"
    )
    for row in result["rows"]:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} max_bond_dim={row['max_bond_dim']} "
            f"svd_cutoff={row['svd_cutoff']:.1e} ref={row['reference_energy']:.8f} "
            f"mps={row['mps_energy']:.8f} abs_error={row['abs_error']:.8f} "
            f"err/site={row['energy_error_per_site']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
