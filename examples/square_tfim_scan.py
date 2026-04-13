import argparse
import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ import square_tfim_observables


SQUARE_TFIM_SCAN_FIELDNAMES = [
    "Lx",
    "Ly",
    "n_sites",
    "Jx",
    "Jy",
    "h",
    "backend",
    "energy",
    "energy_per_site",
    "magnetization_x",
    "magnetization_z",
    "nn_zz_horizontal",
    "nn_zz_vertical",
    "max_bond_dim",
    "svd_cutoff",
]


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


def square_tfim_scan_rows(
    lattice_sizes=((2, 2), (3, 2)),
    Jx_values=(1.0,),
    Jy_values=(1.0,),
    h_values=(0.2, 0.6, 1.0),
    include_exact=True,
    mps_bond_dims=(4, 8),
    svd_cutoff=1e-12,
    seed=0,
):
    rows = []
    for Lx, Ly in lattice_sizes:
        for Jx in Jx_values:
            for Jy in Jy_values:
                for h in h_values:
                    if include_exact:
                        exact = square_tfim_observables(
                            Lx=Lx,
                            Ly=Ly,
                            Jx=Jx,
                            Jy=Jy,
                            h=h,
                            backend="qml",
                            seed=seed,
                        )
                        rows.append(
                            {
                                "Lx": int(exact["Lx"]),
                                "Ly": int(exact["Ly"]),
                                "n_sites": int(exact["n_sites"]),
                                "Jx": float(exact["Jx"]),
                                "Jy": float(exact["Jy"]),
                                "h": float(exact["h"]),
                                "backend": "qml",
                                "energy": float(exact["energy"]),
                                "energy_per_site": float(exact["energy_per_site"]),
                                "magnetization_x": float(exact["magnetization_x"]),
                                "magnetization_z": float(exact["magnetization_z"]),
                                "nn_zz_horizontal": float(exact["nn_zz_horizontal"]),
                                "nn_zz_vertical": float(exact["nn_zz_vertical"]),
                                "max_bond_dim": "",
                                "svd_cutoff": float(exact["svd_cutoff"]),
                            }
                        )

                    for max_bond_dim in mps_bond_dims:
                        mps = square_tfim_observables(
                            Lx=Lx,
                            Ly=Ly,
                            Jx=Jx,
                            Jy=Jy,
                            h=h,
                            backend="mps",
                            max_bond_dim=max_bond_dim,
                            svd_cutoff=svd_cutoff,
                            seed=seed,
                        )
                        rows.append(
                            {
                                "Lx": int(mps["Lx"]),
                                "Ly": int(mps["Ly"]),
                                "n_sites": int(mps["n_sites"]),
                                "Jx": float(mps["Jx"]),
                                "Jy": float(mps["Jy"]),
                                "h": float(mps["h"]),
                                "backend": "mps",
                                "energy": float(mps["energy"]),
                                "energy_per_site": float(mps["energy_per_site"]),
                                "magnetization_x": float(mps["magnetization_x"]),
                                "magnetization_z": float(mps["magnetization_z"]),
                                "nn_zz_horizontal": float(mps["nn_zz_horizontal"]),
                                "nn_zz_vertical": float(mps["nn_zz_vertical"]),
                                "max_bond_dim": "" if max_bond_dim is None else int(max_bond_dim),
                                "svd_cutoff": float(mps["svd_cutoff"]),
                            }
                        )
    return rows


def write_square_tfim_scan_csv(path, rows):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SQUARE_TFIM_SCAN_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic 2D square-lattice TFIM scan.")
    parser.add_argument("--csv", dest="csv_path", default="square_tfim_scan.csv", help="Scan CSV output path.")
    parser.add_argument("--h-grid", dest="h_grid", default="0.2,0.6,1.0", help="Comma-separated h grid.")
    parser.add_argument("--Jx-grid", dest="Jx_grid", default="1.0", help="Comma-separated Jx grid.")
    parser.add_argument("--Jy-grid", dest="Jy_grid", default="1.0", help="Comma-separated Jy grid.")
    parser.add_argument(
        "--mps-bonds",
        dest="mps_bonds",
        default="4,8",
        help="Comma-separated MPS bond-dimension grid. Use full for None.",
    )
    args = parser.parse_args()

    rows = square_tfim_scan_rows(
        Jx_values=parse_float_grid(args.Jx_grid),
        Jy_values=parse_float_grid(args.Jy_grid),
        h_values=parse_float_grid(args.h_grid),
        mps_bond_dims=parse_int_grid(args.mps_bonds),
    )
    write_square_tfim_scan_csv(args.csv_path, rows)

    print("workflow=2D square TFIM scan")
    print("mapping=s(x,y)=x+Lx*y")
    print("hamiltonian=H_2D=-Jx sum_<i,j>_x ZZ - Jy sum_<i,j>_y ZZ - h sum_i X")
    print("method=fixed deterministic mapped-lattice ansatz (not exact ground-state guarantee)")
    print(f"rows={len(rows)}")
    print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
