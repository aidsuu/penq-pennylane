import csv
import pathlib


SQUARE_TFIM_REAL_TIME_FIELDNAMES = [
    "Lx",
    "Ly",
    "n_sites",
    "Jx",
    "Jy",
    "h",
    "backend",
    "step",
    "time",
    "energy",
    "magnetization_x",
    "magnetization_z",
    "nn_zz_horizontal",
    "nn_zz_vertical",
    "max_bond_dim",
    "svd_cutoff",
]

SQUARE_TFIM_IMAG_TIME_FIELDNAMES = [
    "Lx",
    "Ly",
    "n_sites",
    "Jx",
    "Jy",
    "h",
    "backend",
    "step",
    "delta_tau",
    "energy",
    "magnetization_x",
    "magnetization_z",
    "nn_zz_horizontal",
    "nn_zz_vertical",
    "max_bond_dim",
    "svd_cutoff",
]


def write_square_tfim_real_time_csv(path, rows):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SQUARE_TFIM_REAL_TIME_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_square_tfim_imag_time_csv(path, rows):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SQUARE_TFIM_IMAG_TIME_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def read_square_tfim_real_time_csv(path):
    rows = []
    with pathlib.Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SQUARE_TFIM_REAL_TIME_FIELDNAMES:
            raise ValueError(
                f"Unexpected square real-time CSV header: {reader.fieldnames}. "
                f"Expected {SQUARE_TFIM_REAL_TIME_FIELDNAMES}."
            )
        for row in reader:
            rows.append(
                {
                    "Lx": int(row["Lx"]),
                    "Ly": int(row["Ly"]),
                    "n_sites": int(row["n_sites"]),
                    "Jx": float(row["Jx"]),
                    "Jy": float(row["Jy"]),
                    "h": float(row["h"]),
                    "backend": row["backend"],
                    "step": int(row["step"]),
                    "time": float(row["time"]),
                    "energy": float(row["energy"]),
                    "magnetization_x": float(row["magnetization_x"]),
                    "magnetization_z": float(row["magnetization_z"]),
                    "nn_zz_horizontal": float(row["nn_zz_horizontal"]),
                    "nn_zz_vertical": float(row["nn_zz_vertical"]),
                    "max_bond_dim": None if row["max_bond_dim"] == "" else int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                }
            )
    return rows


def read_square_tfim_imag_time_csv(path):
    rows = []
    with pathlib.Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != SQUARE_TFIM_IMAG_TIME_FIELDNAMES:
            raise ValueError(
                f"Unexpected square imaginary-time CSV header: {reader.fieldnames}. "
                f"Expected {SQUARE_TFIM_IMAG_TIME_FIELDNAMES}."
            )
        for row in reader:
            rows.append(
                {
                    "Lx": int(row["Lx"]),
                    "Ly": int(row["Ly"]),
                    "n_sites": int(row["n_sites"]),
                    "Jx": float(row["Jx"]),
                    "Jy": float(row["Jy"]),
                    "h": float(row["h"]),
                    "backend": row["backend"],
                    "step": int(row["step"]),
                    "delta_tau": float(row["delta_tau"]),
                    "energy": float(row["energy"]),
                    "magnetization_x": float(row["magnetization_x"]),
                    "magnetization_z": float(row["magnetization_z"]),
                    "nn_zz_horizontal": float(row["nn_zz_horizontal"]),
                    "nn_zz_vertical": float(row["nn_zz_vertical"]),
                    "max_bond_dim": None if row["max_bond_dim"] == "" else int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                }
            )
    return rows
