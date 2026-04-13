import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ import square_tfim_imag_time
from QML.PenQ.examples.square_tfim_dynamics_utils import write_square_tfim_imag_time_csv


def square_tfim_imag_time_rows(
    Lx=2,
    Ly=2,
    Jx=1.0,
    Jy=1.0,
    h=0.6,
    delta_tau=0.05,
    steps=20,
    max_layers=4,
    max_bond_dim=8,
    svd_cutoff=1e-12,
    seed=0,
):
    exact = square_tfim_imag_time(
        Lx=Lx,
        Ly=Ly,
        Jx=Jx,
        Jy=Jy,
        h=h,
        backend="qml",
        delta_tau=delta_tau,
        steps=steps,
        max_layers=max_layers,
        seed=seed,
    )
    mps = square_tfim_imag_time(
        Lx=Lx,
        Ly=Ly,
        Jx=Jx,
        Jy=Jy,
        h=h,
        backend="mps",
        delta_tau=delta_tau,
        steps=steps,
        max_layers=max_layers,
        max_bond_dim=max_bond_dim,
        svd_cutoff=svd_cutoff,
        seed=seed,
    )

    rows = []
    for backend_result in (exact, mps):
        for step in range(len(backend_result["energy_history"])):
            rows.append(
                {
                    "Lx": int(backend_result["Lx"]),
                    "Ly": int(backend_result["Ly"]),
                    "n_sites": int(backend_result["n_sites"]),
                    "Jx": float(backend_result["Jx"]),
                    "Jy": float(backend_result["Jy"]),
                    "h": float(backend_result["h"]),
                    "backend": backend_result["backend"],
                    "step": int(step),
                    "delta_tau": float(backend_result["delta_tau"]),
                    "energy": float(backend_result["energy_history"][step]),
                    "magnetization_x": float(backend_result["magnetization_x_history"][step]),
                    "magnetization_z": float(backend_result["magnetization_z_history"][step]),
                    "nn_zz_horizontal": float(backend_result["nn_zz_horizontal_history"][step]),
                    "nn_zz_vertical": float(backend_result["nn_zz_vertical_history"][step]),
                    "max_bond_dim": "" if backend_result["backend"] == "qml" else int(max_bond_dim),
                    "svd_cutoff": float(backend_result["svd_cutoff"]),
                }
            )
    return rows


def main():
    parser = argparse.ArgumentParser(description="2D square TFIM imaginary-time trajectory writer.")
    parser.add_argument("--csv", dest="csv_path", default="square_tfim_imag_time.csv", help="Trajectory CSV path.")
    parser.add_argument("--Lx", type=int, default=2)
    parser.add_argument("--Ly", type=int, default=2)
    parser.add_argument("--Jx", type=float, default=1.0)
    parser.add_argument("--Jy", type=float, default=1.0)
    parser.add_argument("--h", type=float, default=0.6)
    parser.add_argument("--delta-tau", type=float, default=0.05)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--max-layers", type=int, default=4)
    parser.add_argument("--max-bond-dim", type=int, default=8)
    parser.add_argument("--svd-cutoff", type=float, default=1e-12)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rows = square_tfim_imag_time_rows(
        Lx=args.Lx,
        Ly=args.Ly,
        Jx=args.Jx,
        Jy=args.Jy,
        h=args.h,
        delta_tau=args.delta_tau,
        steps=args.steps,
        max_layers=args.max_layers,
        max_bond_dim=args.max_bond_dim,
        svd_cutoff=args.svd_cutoff,
        seed=args.seed,
    )
    write_square_tfim_imag_time_csv(args.csv_path, rows)

    print("workflow=2D square TFIM imaginary-time")
    print("mapping=s(x,y)=x+Lx*y")
    print("method=mapped-lattice variational projected update (approximate)")
    print(f"rows={len(rows)}")
    print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
