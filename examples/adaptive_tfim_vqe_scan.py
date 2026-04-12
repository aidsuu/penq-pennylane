import argparse
import csv
from pathlib import Path

from QML.PenQ.penq_algorithms import adaptive_tfim_vqe


def parse_float_grid(text):
    return tuple(float(value) for value in text.split(","))


def parse_int_grid(text):
    values = []
    for value in text.split(","):
        stripped = value.strip().lower()
        if stripped in {"full", "none"}:
            values.append(None)
        else:
            values.append(int(stripped))
    return tuple(values)


def adaptive_tfim_vqe_scan_rows(
    qubit_counts=(6, 8),
    J_values=(1.0,),
    h_values=(0.5, 1.0),
    include_exact=True,
    mps_bond_dims=(2, 4),
    max_layers=4,
    steps=2,
    svd_cutoff=1e-12,
):
    """Build deterministic adaptive TFIM scan rows for exact and MPS backends."""
    rows = []

    for n in qubit_counts:
        for J in J_values:
            for h in h_values:
                if include_exact:
                    result = adaptive_tfim_vqe(
                        n=n,
                        J=J,
                        h=h,
                        backend="qml",
                        max_layers=max_layers,
                        steps=steps,
                    )
                    for history_row in result["history"]:
                        rows.append(
                            {
                                "n": int(n),
                                "J": float(J),
                                "h": float(h),
                                "backend": "qml",
                                "layer": int(history_row["layer"]),
                                "energy": float(history_row["energy"]),
                                "energy_per_site": float(history_row["energy_per_site"]),
                                "expval_x0": float(history_row["expval_x0"]),
                                "expval_z0z1": float(history_row["expval_z0z1"]),
                                "converged": bool(history_row["converged"]),
                                "final_delta_energy": float(history_row["final_delta_energy"]),
                                "max_bond_dim": "",
                                "svd_cutoff": float(history_row["svd_cutoff"]),
                            }
                        )

                for max_bond_dim in mps_bond_dims:
                    result = adaptive_tfim_vqe(
                        n=n,
                        J=J,
                        h=h,
                        backend="mps",
                        max_layers=max_layers,
                        max_bond_dim=max_bond_dim,
                        svd_cutoff=svd_cutoff,
                        steps=steps,
                    )
                    for history_row in result["history"]:
                        rows.append(
                            {
                                "n": int(n),
                                "J": float(J),
                                "h": float(h),
                                "backend": "mps",
                                "layer": int(history_row["layer"]),
                                "energy": float(history_row["energy"]),
                                "energy_per_site": float(history_row["energy_per_site"]),
                                "expval_x0": float(history_row["expval_x0"]),
                                "expval_z0z1": float(history_row["expval_z0z1"]),
                                "converged": bool(history_row["converged"]),
                                "final_delta_energy": float(history_row["final_delta_energy"]),
                                "max_bond_dim": "" if max_bond_dim is None else int(max_bond_dim),
                                "svd_cutoff": float(history_row["svd_cutoff"]),
                            }
                        )

    return rows


def write_adaptive_tfim_vqe_scan_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "J",
        "h",
        "backend",
        "layer",
        "energy",
        "energy_per_site",
        "expval_x0",
        "expval_z0z1",
        "converged",
        "final_delta_energy",
        "max_bond_dim",
        "svd_cutoff",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic adaptive TFIM VQE scan.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument("--h-grid", dest="h_grid", default="0.5,1.0", help="Comma-separated h grid.")
    parser.add_argument(
        "--mps-bonds",
        dest="mps_bonds",
        default="2,4",
        help="Comma-separated MPS bond-dimension grid. Use full for None.",
    )
    args = parser.parse_args()

    rows = adaptive_tfim_vqe_scan_rows(
        h_values=parse_float_grid(args.h_grid),
        mps_bond_dims=parse_int_grid(args.mps_bonds),
    )
    if args.csv_path is not None:
        write_adaptive_tfim_vqe_scan_csv(args.csv_path, rows)

    print("workflow=Adaptive TFIM VQE scan")
    print("hamiltonian=H=-J sum_i Z_i Z_{i+1} - h sum_i X_i")
    print("ansatz=U_l(gamma_l,beta_l)=U_X(beta_l)U_ZZ(gamma_l)")
    print("stop_rule=Delta_L<=tol or L==max_layers")
    for row in rows:
        bond_text = "full" if row["max_bond_dim"] == "" else str(row["max_bond_dim"])
        print(
            f"n={row['n']:>2} J={row['J']:.2f} h={row['h']:.2f} backend={row['backend']} "
            f"layer={row['layer']:>2} energy={row['energy']:.8f} "
            f"err/site={row['energy_per_site']:.8f} x0={row['expval_x0']:.8f} "
            f"z0z1={row['expval_z0z1']:.8f} bond={bond_text} converged={row['converged']}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
