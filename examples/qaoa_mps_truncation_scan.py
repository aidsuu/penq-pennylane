import argparse
import csv
from pathlib import Path

import numpy as np
import pennylane as qml

from QML.PenQ.examples.qaoa_ising_small import qaoa_layer


STATEVECTOR_DEVICE_NAME = "penq.qml_starter"
MPS_DEVICE_NAME = "penq.mps_starter"


def parse_grid_values(text):
    return tuple(float(value) for value in text.split(","))


def validate_qaoa_mps_inputs(qubit_counts, gamma_values, beta_values, truncation_settings):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not gamma_values:
        raise ValueError("gamma_values must not be empty.")
    if not beta_values:
        raise ValueError("beta_values must not be empty.")
    if not truncation_settings:
        raise ValueError("truncation_settings must not be empty.")
    for num_qubits in qubit_counts:
        if num_qubits not in {8, 10}:
            raise ValueError("QAOA MPS truncation scan expects qubit counts chosen from 8 and 10.")


def qaoa_chain_energy(dev, num_qubits, gamma, beta):
    energy = 0.0
    for wire in range(num_qubits - 1):
        @qml.qnode(dev)
        def zz_expval(pair_wire=wire):
            for qubit in range(num_qubits):
                qml.Hadamard(qubit)
            qaoa_layer(num_qubits, gamma, beta)
            return qml.expval(qml.PauliZ(pair_wire) @ qml.PauliZ(pair_wire + 1))

        energy += float(zz_expval())
    return float(energy)


def qaoa_mps_truncation_rows(
    qubit_counts=(8, 10),
    gamma_values=(0.0, np.pi / 4.0, np.pi / 2.0),
    beta_values=(0.0, np.pi / 8.0),
    truncation_settings=((None, 0.0), (2, 1e-12), (1, 0.0)),
):
    validate_qaoa_mps_inputs(qubit_counts, gamma_values, beta_values, truncation_settings)
    rows = []

    for num_qubits in qubit_counts:
        reference_dev = qml.device(STATEVECTOR_DEVICE_NAME, wires=num_qubits)
        for gamma in gamma_values:
            for beta in beta_values:
                reference_energy = qaoa_chain_energy(reference_dev, num_qubits, gamma, beta)
                for max_bond_dim, svd_cutoff in truncation_settings:
                    mps_dev = qml.device(
                        MPS_DEVICE_NAME,
                        wires=num_qubits,
                        max_bond_dim=max_bond_dim,
                        svd_cutoff=svd_cutoff,
                    )
                    mps_energy = qaoa_chain_energy(mps_dev, num_qubits, gamma, beta)
                    rows.append(
                        {
                            "n": int(num_qubits),
                            "gamma": float(gamma),
                            "beta": float(beta),
                            "max_bond_dim": "" if max_bond_dim is None else int(max_bond_dim),
                            "svd_cutoff": float(svd_cutoff),
                            "reference_energy": float(reference_energy),
                            "mps_energy": float(mps_energy),
                            "abs_error": float(abs(mps_energy - reference_energy)),
                        }
                    )
    return rows


def write_qaoa_mps_truncation_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "n",
        "gamma",
        "beta",
        "max_bond_dim",
        "svd_cutoff",
        "reference_energy",
        "mps_energy",
        "abs_error",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic QAOA MPS truncation scan.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    parser.add_argument(
        "--gamma-grid",
        dest="gamma_grid",
        default="0.0,0.7853981634,1.5707963268",
        help="Comma-separated deterministic gamma grid.",
    )
    parser.add_argument(
        "--beta-grid",
        dest="beta_grid",
        default="0.0,0.3926990817",
        help="Comma-separated deterministic beta grid.",
    )
    args = parser.parse_args()

    rows = qaoa_mps_truncation_rows(
        gamma_values=parse_grid_values(args.gamma_grid),
        beta_values=parse_grid_values(args.beta_grid),
    )
    if args.csv_path is not None:
        write_qaoa_mps_truncation_csv(args.csv_path, rows)

    print(f"reference_device={STATEVECTOR_DEVICE_NAME}")
    print(f"mps_device={MPS_DEVICE_NAME}")
    print("workflow=QAOA MPS truncation scan")
    print("energy = p=1 open-chain Ising QAOA cost")
    for row in rows:
        bond_text = "full" if row["max_bond_dim"] == "" else str(row["max_bond_dim"])
        print(
            f"n={row['n']:>2} gamma={row['gamma']:.6f} beta={row['beta']:.6f} "
            f"max_bond_dim={bond_text} svd_cutoff={row['svd_cutoff']:.1e} "
            f"ref={row['reference_energy']:.8f} mps={row['mps_energy']:.8f} "
            f"abs_error={row['abs_error']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
