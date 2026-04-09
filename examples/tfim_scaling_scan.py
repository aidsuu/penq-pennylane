import argparse
import csv

import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def validate_tfim_scaling_inputs(qubit_counts, h_values):
    if not qubit_counts:
        raise ValueError("qubit_counts must not be empty.")
    if not h_values:
        raise ValueError("h_values must not be empty.")
    for num_qubits in qubit_counts:
        if not 6 <= num_qubits <= 16 or num_qubits % 2 != 0:
            raise ValueError("TFIM scaling scan expects even qubit counts between 6 and 16.")


def tfim_hamiltonian(num_qubits, h):
    coefficients = []
    terms = []
    for wire in range(num_qubits - 1):
        coefficients.append(1.0)
        terms.append(qml.PauliZ(wire) @ qml.PauliZ(wire + 1))
    for wire in range(num_qubits):
        coefficients.append(float(h))
        terms.append(qml.PauliX(wire))
    return qml.dot(coefficients, terms)


def prepare_tfim_state(name, num_qubits):
    if name == "all_zero":
        return
    if name == "all_plus":
        for wire in range(num_qubits):
            qml.Hadamard(wire)
        return
    if name == "neel":
        for wire in range(1, num_qubits, 2):
            qml.PauliX(wire)
        return
    raise ValueError("Unsupported TFIM scaling state. Expected one of: all_zero, all_plus, neel.")


def evaluate_tfim_observables(num_qubits, h, state_name):
    dev = qml.device(DEVICE_NAME, wires=num_qubits)
    hamiltonian = tfim_hamiltonian(num_qubits, h)

    @qml.qnode(dev)
    def energy_circuit():
        prepare_tfim_state(state_name, num_qubits)
        return qml.expval(hamiltonian)

    @qml.qnode(dev)
    def x0_circuit():
        prepare_tfim_state(state_name, num_qubits)
        return qml.expval(qml.PauliX(0))

    @qml.qnode(dev)
    def zz01_circuit():
        prepare_tfim_state(state_name, num_qubits)
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    return {
        "energy": float(energy_circuit()),
        "x0": float(x0_circuit()),
        "zz01": float(zz01_circuit()),
    }


def scaling_scan_rows(qubit_counts=(6, 8, 10, 12, 14, 16), h_values=(0.0, 0.5, 1.0), state_name="all_plus"):
    validate_tfim_scaling_inputs(qubit_counts, h_values)
    rows = []
    for num_qubits in qubit_counts:
        for h in h_values:
            values = evaluate_tfim_observables(num_qubits, h, state_name)
            rows.append(
                {
                    "n": int(num_qubits),
                    "h": float(h),
                    "energy": values["energy"],
                    "energy_per_site": float(values["energy"] / num_qubits),
                    "expval_x0": values["x0"],
                    "expval_z0z1": values["zz01"],
                }
            )
    return rows


def write_tfim_scaling_csv(path, rows):
    fieldnames = ["n", "h", "energy", "energy_per_site", "expval_x0", "expval_z0z1"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_h_values(text):
    return tuple(float(value) for value in text.split(","))


def main():
    parser = argparse.ArgumentParser(description="Deterministic TFIM scaling scan.")
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default=None,
        help="Optional CSV output path.",
    )
    parser.add_argument(
        "--h-grid",
        dest="h_grid",
        default="0.0,0.5,1.0",
        help="Comma-separated deterministic h grid.",
    )
    args = parser.parse_args()

    rows = scaling_scan_rows(h_values=parse_h_values(args.h_grid))
    if args.csv_path is not None:
        write_tfim_scaling_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=TFIM scaling scan")
    print("H = sum_i Z_i Z_{i+1} + h * sum_i X_i")
    print("state = all_plus")
    for row in rows:
        print(
            f"n={row['n']:>2} h={row['h']:.2f} "
            f"energy={row['energy']:.8f} e/site={row['energy_per_site']:.8f} "
            f"x0={row['expval_x0']:.8f} zz01={row['expval_z0z1']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
