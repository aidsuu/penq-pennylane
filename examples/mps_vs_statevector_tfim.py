import argparse
import csv
from pathlib import Path

import pennylane as qml


STATEVECTOR_DEVICE_NAME = "penq.qml_starter"
MPS_DEVICE_NAME = "penq.mps_starter"


def parse_h_values(text):
    return tuple(float(value) for value in text.split(","))


def validate_comparison_inputs(qubit_counts, h_values, truncation_settings):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    if not truncation_settings:
        raise ValueError("truncation_settings must not be empty.")
    for num_qubits in qubit_counts:
        if num_qubits not in {6, 8, 10}:
            raise ValueError("MPS vs statevector study expects qubit counts chosen from 6, 8, 10.")


def prepare_entangling_chain(num_qubits, h):
    for wire in range(num_qubits):
        qml.RY(h, wires=wire)
    for wire in range(num_qubits - 1):
        qml.CNOT(wires=[wire, wire + 1])


def zz_chain_energy(dev, num_qubits, h):
    energy = 0.0
    for wire in range(num_qubits - 1):
        @qml.qnode(dev)
        def pair_expval(pair_wire=wire):
            prepare_entangling_chain(num_qubits, h)
            return qml.expval(qml.PauliZ(pair_wire) @ qml.PauliZ(pair_wire + 1))

        energy += float(pair_expval())
    return float(energy)


def comparison_rows(
    qubit_counts=(6, 8, 10),
    h_values=(0.0, 0.5, 1.0),
    truncation_settings=((None, 0.0), (2, 1e-12), (1, 0.0)),
):
    validate_comparison_inputs(qubit_counts, h_values, truncation_settings)
    rows = []

    for num_qubits in qubit_counts:
        reference_dev = qml.device(STATEVECTOR_DEVICE_NAME, wires=num_qubits)
        for h in h_values:
            reference_energy = zz_chain_energy(reference_dev, num_qubits, h)
            for max_bond_dim, svd_cutoff in truncation_settings:
                mps_dev = qml.device(
                    MPS_DEVICE_NAME,
                    wires=num_qubits,
                    max_bond_dim=max_bond_dim,
                    svd_cutoff=svd_cutoff,
                )
                mps_energy = zz_chain_energy(mps_dev, num_qubits, h)
                rows.append(
                    {
                        "n": int(num_qubits),
                        "h": float(h),
                        "max_bond_dim": "" if max_bond_dim is None else int(max_bond_dim),
                        "svd_cutoff": float(svd_cutoff),
                        "reference_energy": float(reference_energy),
                        "mps_energy": float(mps_energy),
                        "abs_error": float(abs(mps_energy - reference_energy)),
                    }
                )
    return rows


def write_mps_vs_statevector_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["n", "h", "max_bond_dim", "svd_cutoff", "reference_energy", "mps_energy", "abs_error"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic MPS vs statevector comparison study.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = comparison_rows(h_values=parse_h_values(args.h_grid))
    if args.csv_path is not None:
        write_mps_vs_statevector_csv(args.csv_path, rows)

    print(f"reference_device={STATEVECTOR_DEVICE_NAME}")
    print(f"mps_device={MPS_DEVICE_NAME}")
    print("workflow=MPS vs statevector TFIM-style chain study")
    print("energy = sum_i <Z_i Z_{i+1}> on a deterministic entangling chain circuit")
    for row in rows:
        bond_text = "full" if row["max_bond_dim"] == "" else str(row["max_bond_dim"])
        print(
            f"n={row['n']:>2} h={row['h']:.2f} "
            f"max_bond_dim={bond_text} svd_cutoff={row['svd_cutoff']:.1e} "
            f"ref={row['reference_energy']:.8f} mps={row['mps_energy']:.8f} "
            f"abs_error={row['abs_error']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
