import csv
from pathlib import Path


TFIM_DYNAMICS_SCAN_FIELDNAMES = [
    "dynamics",
    "n",
    "J",
    "h",
    "backend",
    "step",
    "time",
    "step_size",
    "energy",
    "energy_per_site",
    "expval_x0",
    "expval_z0z1",
    "max_bond_dim",
    "svd_cutoff",
]


def history_to_scan_rows(result, dynamics, step_size):
    rows = []
    for row in result["history"]:
        rows.append(
            {
                "dynamics": str(dynamics),
                "n": int(result["n"]),
                "J": float(result["J"]),
                "h": float(result["h"]),
                "backend": str(result["backend"]),
                "step": int(row["step"]),
                "time": float(row.get("time", row["step"] * step_size)),
                "step_size": float(step_size),
                "energy": float(row["energy"]),
                "energy_per_site": float(row["energy_per_site"]),
                "expval_x0": float(row["expval_x0"]),
                "expval_z0z1": float(row["expval_z0z1"]),
                "max_bond_dim": row["max_bond_dim"],
                "svd_cutoff": float(row["svd_cutoff"]),
            }
        )
    return rows


def write_tfim_dynamics_scan_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TFIM_DYNAMICS_SCAN_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def read_tfim_dynamics_scan_csv(path):
    rows = []
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != TFIM_DYNAMICS_SCAN_FIELDNAMES:
            raise ValueError(
                f"Unexpected TFIM dynamics scan CSV header: {reader.fieldnames}. "
                f"Expected {TFIM_DYNAMICS_SCAN_FIELDNAMES}."
            )
        for row in reader:
            rows.append(
                {
                    "dynamics": row["dynamics"],
                    "n": int(row["n"]),
                    "J": float(row["J"]),
                    "h": float(row["h"]),
                    "backend": row["backend"],
                    "step": int(row["step"]),
                    "time": float(row["time"]),
                    "step_size": float(row["step_size"]),
                    "energy": float(row["energy"]),
                    "energy_per_site": float(row["energy_per_site"]),
                    "expval_x0": float(row["expval_x0"]),
                    "expval_z0z1": float(row["expval_z0z1"]),
                    "max_bond_dim": None if row["max_bond_dim"] == "" else int(row["max_bond_dim"]),
                    "svd_cutoff": float(row["svd_cutoff"]),
                }
            )
    return rows


def final_rows(rows):
    grouped = {}
    for row in rows:
        key = (
            row["dynamics"],
            row["n"],
            row["J"],
            row["h"],
            row["backend"],
            row["max_bond_dim"],
            row["svd_cutoff"],
        )
        if key not in grouped or row["step"] > grouped[key]["step"]:
            grouped[key] = row
    return list(grouped.values())


def final_exact_vs_mps_rows(rows):
    exact = {}
    comparison_rows = []
    for row in final_rows(rows):
        key = (row["dynamics"], row["n"], row["J"], row["h"])
        if row["backend"] == "qml":
            exact[key] = row

    for row in final_rows(rows):
        key = (row["dynamics"], row["n"], row["J"], row["h"])
        if row["backend"] != "mps" or key not in exact:
            continue
        ref = exact[key]
        comparison_rows.append(
            {
                "dynamics": row["dynamics"],
                "n": row["n"],
                "J": row["J"],
                "h": row["h"],
                "max_bond_dim": row["max_bond_dim"],
                "exact_energy": ref["energy"],
                "mps_energy": row["energy"],
                "abs_error": abs(row["energy"] - ref["energy"]),
            }
        )
    return comparison_rows
