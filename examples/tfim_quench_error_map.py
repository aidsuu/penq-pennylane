import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.mps_tebd_tfim_quench import parse_h_values
from QML.PenQ.examples.mps_tebd_tfim_quench import parse_n_values
from QML.PenQ.examples.mps_trotter_order_study import parse_dt_values
from QML.PenQ.examples.mps_vs_statevector_tfim_quench import tfim_quench_comparison_rows


def tfim_quench_error_map_rows(
    qubit_counts=(6, 8),
    h_values=(0.5, 1.0),
    dt_values=(0.2, 0.1),
    total_time=0.4,
    bond_dims=(2, 4),
    svd_cutoff=1e-12,
):
    comparison_rows = tfim_quench_comparison_rows(
        qubit_counts=qubit_counts,
        h_values=h_values,
        dt_values=dt_values,
        total_time=total_time,
        bond_dims=bond_dims,
        svd_cutoff=svd_cutoff,
    )
    rows = []
    for row in comparison_rows:
        rows.append(
            {
                "n": int(row["n"]),
                "h": float(row["h"]),
                "dt": float(row["dt"]),
                "steps": int(row["steps"]),
                "time": float(row["time"]),
                "trotter_order": int(row["trotter_order"]),
                "max_bond_dim": int(row["max_bond_dim"]),
                "svd_cutoff": float(row["svd_cutoff"]),
                "abs_error_z0": float(row["abs_error_z0"]),
                "abs_error_z0z1": float(row["abs_error_z0z1"]),
            }
        )
    return rows


def write_tfim_quench_error_map_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "h",
        "dt",
        "steps",
        "time",
        "trotter_order",
        "max_bond_dim",
        "svd_cutoff",
        "abs_error_z0",
        "abs_error_z0z1",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM quench dynamical error map.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument("--h-grid", dest="h_grid", default="0.5,1.0", help="Comma-separated deterministic h grid.")
    parser.add_argument("--n-grid", dest="n_grid", default="6,8", help="Comma-separated deterministic qubit-count grid.")
    parser.add_argument("--dt-grid", dest="dt_grid", default="0.2,0.1", help="Comma-separated deterministic dt grid.")
    parser.add_argument("--total-time", dest="total_time", type=float, default=0.4, help="Fixed total evolution time.")
    parser.add_argument("--bond-grid", dest="bond_grid", default="2,4", help="Comma-separated deterministic max_bond_dim grid.")
    parser.add_argument("--svd-cutoff", dest="svd_cutoff", type=float, default=1e-12, help="Fixed singular-value cutoff.")
    args = parser.parse_args()

    rows = tfim_quench_error_map_rows(
        qubit_counts=parse_n_values(args.n_grid),
        h_values=parse_h_values(args.h_grid),
        dt_values=parse_dt_values(args.dt_grid),
        total_time=args.total_time,
        bond_dims=tuple(int(value) for value in args.bond_grid.split(",")),
        svd_cutoff=args.svd_cutoff,
    )
    if args.csv_path is not None:
        write_tfim_quench_error_map_csv(args.csv_path, rows)

    print("workflow=TFIM quench dynamical error map")
    print("source=exact-vs-MPS TFIM quench comparison")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} dt={row['dt']:.3f} steps={row['steps']:>2} "
            f"time={row['time']:.3f} order={row['trotter_order']} max_bond_dim={row['max_bond_dim']} "
            f"err_z0={row['abs_error_z0']:.8f} err_zz={row['abs_error_z0z1']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
