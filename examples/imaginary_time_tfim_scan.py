import pathlib
import sys
import argparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ import imaginary_time_tfim
from QML.PenQ.examples.tfim_dynamics_utils import history_to_scan_rows
from QML.PenQ.examples.tfim_dynamics_utils import write_tfim_dynamics_scan_csv


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


def imaginary_time_tfim_scan_rows(
    qubit_counts=(2, 4, 6),
    J_values=(1.0,),
    h_values=(0.1, 0.5, 1.0),
    include_exact=True,
    mps_bond_dims=(4, 8),
    delta_tau=0.02,
    steps=10,
    max_layers=2,
    svd_cutoff=1e-12,
    seed=123,
):
    rows = []
    for n in qubit_counts:
        for J in J_values:
            for h in h_values:
                if include_exact:
                    exact = imaginary_time_tfim(
                        n=n,
                        J=J,
                        h=h,
                        backend="qml",
                        delta_tau=delta_tau,
                        steps=steps,
                        max_layers=max_layers,
                        seed=seed,
                    )
                    rows.extend(history_to_scan_rows(exact, dynamics="imaginary", step_size=delta_tau))

                for max_bond_dim in mps_bond_dims:
                    mps = imaginary_time_tfim(
                        n=n,
                        J=J,
                        h=h,
                        backend="mps",
                        delta_tau=delta_tau,
                        steps=steps,
                        max_layers=max_layers,
                        max_bond_dim=max_bond_dim,
                        svd_cutoff=svd_cutoff,
                        seed=seed,
                    )
                    rows.extend(history_to_scan_rows(mps, dynamics="imaginary", step_size=delta_tau))
    return rows

def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM imaginary-time scan.")
    parser.add_argument("--csv", dest="csv_path", default="imaginary_tfim_scan.csv", help="Scan CSV output path.")
    parser.add_argument("--h-grid", dest="h_grid", default="0.1,0.5,1.0", help="Comma-separated h grid.")
    parser.add_argument(
        "--mps-bonds",
        dest="mps_bonds",
        default="4,8",
        help="Comma-separated MPS bond-dimension grid. Use full for None.",
    )
    args = parser.parse_args()

    rows = imaginary_time_tfim_scan_rows(
        h_values=parse_float_grid(args.h_grid),
        mps_bond_dims=parse_int_grid(args.mps_bonds),
    )
    write_tfim_dynamics_scan_csv(args.csv_path, rows)

    print("workflow=TFIM imaginary-time scan")
    print("hamiltonian=H=-J sum_i Z_i Z_{i+1} - h sum_i X_i")
    print("target=|psi(tau)>=exp(-tau H)|psi0>/||exp(-tau H)|psi0>||")
    print(f"rows={len(rows)}")
    print(f"csv={args.csv_path}")

if __name__ == "__main__":
    main()
