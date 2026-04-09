import argparse
import csv

import numpy as np
import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def ising_cost_hamiltonian(num_qubits):
    if num_qubits < 2:
        raise ValueError("QAOA chain landscape expects at least 2 qubits.")
    coefficients = [1.0] * (num_qubits - 1)
    terms = [qml.PauliZ(wire) @ qml.PauliZ(wire + 1) for wire in range(num_qubits - 1)]
    return qml.dot(coefficients, terms)


def qaoa_layer(num_qubits, gamma, beta):
    for wire in range(num_qubits - 1):
        qml.CNOT(wires=[wire, wire + 1])
        qml.RZ(2.0 * gamma, wires=wire + 1)
        qml.CNOT(wires=[wire, wire + 1])
    for wire in range(num_qubits):
        qml.RX(2.0 * beta, wires=wire)


def qaoa_chain_landscape(num_qubits=8, num_gamma=7, num_beta=7):
    dev = qml.device(DEVICE_NAME, wires=num_qubits)
    hamiltonian = ising_cost_hamiltonian(num_qubits)
    gamma_grid = np.linspace(0.0, np.pi, num_gamma)
    beta_grid = np.linspace(0.0, np.pi / 2.0, num_beta)
    rows = []

    for gamma in gamma_grid:
        for beta in beta_grid:
            @qml.qnode(dev)
            def energy_circuit():
                for wire in range(num_qubits):
                    qml.Hadamard(wire)
                qaoa_layer(num_qubits, gamma, beta)
                return qml.expval(hamiltonian)

            rows.append(
                {
                    "n": int(num_qubits),
                    "gamma": float(gamma),
                    "beta": float(beta),
                    "energy": float(energy_circuit()),
                }
            )

    return rows


def write_qaoa_landscape_csv(path, rows):
    fieldnames = ["n", "gamma", "beta", "energy"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic QAOA chain landscape scan.")
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default=None,
        help="Optional CSV output path.",
    )
    args = parser.parse_args()

    rows = qaoa_chain_landscape(num_qubits=8, num_gamma=7, num_beta=7)
    if args.csv_path is not None:
        write_qaoa_landscape_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=QAOA p=1 landscape for open-chain Ising cost")
    print("n_qubits = 8")
    for row in rows:
        print(
            f"gamma={row['gamma']:.6f} beta={row['beta']:.6f} energy={row['energy']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
