import csv

from QML.PenQ.examples.tfim_scaling_scan import scaling_scan_rows


def finite_size_summary_rows(qubit_counts=(6, 8, 10, 12, 14, 16), h_values=(0.0, 0.5, 1.0), state_name="all_plus"):
    rows = scaling_scan_rows(qubit_counts=qubit_counts, h_values=h_values, state_name=state_name)
    summary_rows = []
    for h in h_values:
        matching = [row for row in rows if row["h"] == float(h)]
        energy_per_site_values = [row["energy_per_site"] for row in matching]
        summary_rows.append(
            {
                "h": float(h),
                "min_energy_per_site": float(min(energy_per_site_values)),
                "max_energy_per_site": float(max(energy_per_site_values)),
                "delta_energy_per_site": float(max(energy_per_site_values) - min(energy_per_site_values)),
            }
        )
    return summary_rows


def write_finite_size_summary_csv(path, rows):
    fieldnames = ["h", "min_energy_per_site", "max_energy_per_site", "delta_energy_per_site"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = finite_size_summary_rows()
    print("workflow=TFIM finite-size comparative summary")
    for row in rows:
        print(
            f"h={row['h']:.2f} min_e/site={row['min_energy_per_site']:.8f} "
            f"max_e/site={row['max_energy_per_site']:.8f} "
            f"delta_e/site={row['delta_energy_per_site']:.8f}"
        )


if __name__ == "__main__":
    main()
