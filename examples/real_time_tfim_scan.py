import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ import real_time_tfim
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


def real_time_tfim_scan_rows(
    qubit_counts=(4, 6),
    J_values=(1.0,),
    h_values=(0.5, 1.0),
    include_exact=True,
    mps_bond_dims=(4, 8),
    dt=0.05,
    steps=20,
    svd_cutoff=1e-12,
):
    rows = []
    for n in qubit_counts:
        for J in J_values:
            for h in h_values:
                if include_exact:
                    exact = real_time_tfim(
                        n=n,
                        J=J,
                        h=h,
                        backend="qml",
                        dt=dt,
                        steps=steps,
                    )
                    rows.extend(history_to_scan_rows(exact, dynamics="real", step_size=dt))

                for max_bond_dim in mps_bond_dims:
                    mps = real_time_tfim(
                        n=n,
                        J=J,
                        h=h,
                        backend="mps",
                        dt=dt,
                        steps=steps,
                        max_bond_dim=max_bond_dim,
                        svd_cutoff=svd_cutoff,
                    )
                    rows.extend(history_to_scan_rows(mps, dynamics="real", step_size=dt))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM real-time scan.")
    parser.add_argument("--csv", dest="csv_path", default="real_tfim_scan.csv", help="Scan CSV output path.")
    parser.add_argument("--h-grid", dest="h_grid", default="0.5,1.0", help="Comma-separated h grid.")
    parser.add_argument(
        "--mps-bonds",
        dest="mps_bonds",
        default="4,8",
        help="Comma-separated MPS bond-dimension grid. Use full for None.",
    )
    args = parser.parse_args()

    rows = real_time_tfim_scan_rows(
        h_values=parse_float_grid(args.h_grid),
        mps_bond_dims=parse_int_grid(args.mps_bonds),
    )
    write_tfim_dynamics_scan_csv(args.csv_path, rows)

    print("workflow=TFIM real-time scan")
    print("hamiltonian=H=-J sum_i Z_i Z_{i+1} - h sum_i X_i")
    print("target=|psi(t)>=exp(-i H t)|psi0>")
    print(f"rows={len(rows)}")
    print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
