import csv
import pathlib


CUBIC_TFIM_REAL_TIME_FIELDNAMES = [
    "Lx",
    "Ly",
    "Lz",
    "n_sites",
    "Jx",
    "Jy",
    "Jz",
    "h",
    "backend",
    "step",
    "time",
    "energy",
    "magnetization_x",
    "magnetization_z",
    "nn_zz_x",
    "nn_zz_y",
    "nn_zz_z",
    "max_bond_dim",
    "svd_cutoff",
]

CUBIC_TFIM_IMAG_TIME_FIELDNAMES = [
    "Lx",
    "Ly",
    "Lz",
    "n_sites",
    "Jx",
    "Jy",
    "Jz",
    "h",
    "backend",
    "step",
    "delta_tau",
    "energy",
    "magnetization_x",
    "magnetization_z",
    "nn_zz_x",
    "nn_zz_y",
    "nn_zz_z",
    "max_bond_dim",
    "svd_cutoff",
]


def write_cubic_tfim_real_time_csv(path, rows):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CUBIC_TFIM_REAL_TIME_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_cubic_tfim_imag_time_csv(path, rows):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CUBIC_TFIM_IMAG_TIME_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def read_cubic_tfim_real_time_csv(path):
    rows = []
    with pathlib.Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CUBIC_TFIM_REAL_TIME_FIELDNAMES:
            raise ValueError(
                f"Unexpected cubic real-time CSV header: {reader.fieldnames}. "
                f"Expected {CUBIC_TFIM_REAL_TIME_FIELDNAMES}."
            )
        for row in reader:
            rows.append(
                {
                    "Lx": int(row["Lx"]),
                    "Ly": int(row["Ly"]),
                    "Lz": int(row["Lz"]),
                    "n_sites": int(row["n_sites"]),
                    "Jx": float(row["Jx"]),
                    "Jy": float(row["Jy"]),
                    "Jz": float(row["Jz"]),
                    "h": float(row["h"]),
                    "backend": row["backend"],
                    "step": int(row["step"]),
                    "time": float(row["time"]),
                    "energy": float(row["energy"]),
                    "magnetization_x": float(row["magnetization_x"]),
                    "magnetization_z": float(row["magnetization_z"]),
                    "nn_zz_x": float(row["nn_zz_x"]),
                    "nn_zz_y": float(row["nn_zz_y"]),
                    "nn_zz_z": float(row["nn_zz_z"]),
                    "max_bond_dim": None if row["max_bond_dim"] == "" else int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                }
            )
    return rows


def read_cubic_tfim_imag_time_csv(path):
    rows = []
    with pathlib.Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CUBIC_TFIM_IMAG_TIME_FIELDNAMES:
            raise ValueError(
                f"Unexpected cubic imaginary-time CSV header: {reader.fieldnames}. "
                f"Expected {CUBIC_TFIM_IMAG_TIME_FIELDNAMES}."
            )
        for row in reader:
            rows.append(
                {
                    "Lx": int(row["Lx"]),
                    "Ly": int(row["Ly"]),
                    "Lz": int(row["Lz"]),
                    "n_sites": int(row["n_sites"]),
                    "Jx": float(row["Jx"]),
                    "Jy": float(row["Jy"]),
                    "Jz": float(row["Jz"]),
                    "h": float(row["h"]),
                    "backend": row["backend"],
                    "step": int(row["step"]),
                    "delta_tau": float(row["delta_tau"]),
                    "energy": float(row["energy"]),
                    "magnetization_x": float(row["magnetization_x"]),
                    "magnetization_z": float(row["magnetization_z"]),
                    "nn_zz_x": float(row["nn_zz_x"]),
                    "nn_zz_y": float(row["nn_zz_y"]),
                    "nn_zz_z": float(row["nn_zz_z"]),
                    "max_bond_dim": None if row["max_bond_dim"] == "" else int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                }
            )
    return rows
