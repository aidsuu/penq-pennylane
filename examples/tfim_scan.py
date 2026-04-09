import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def validate_tfim_inputs(num_qubits, h_values):
    if not 6 <= num_qubits <= 10:
        raise ValueError("TFIM scan expects 6 to 10 qubits.")
    if not h_values:
        raise ValueError("h_values must not be empty.")


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
    raise ValueError("Unsupported TFIM state. Expected one of: all_zero, all_plus, neel.")


def analytic_tfim_energy(name, num_qubits, h):
    if name == "all_zero":
        return float(num_qubits - 1)
    if name == "all_plus":
        return float(h * num_qubits)
    if name == "neel":
        return float(-(num_qubits - 1))
    raise ValueError("Unsupported TFIM state. Expected one of: all_zero, all_plus, neel.")


def evaluate_tfim_scan(num_qubits, h_values):
    validate_tfim_inputs(num_qubits, h_values)
    dev = qml.device(DEVICE_NAME, wires=num_qubits)
    states = ["all_zero", "all_plus", "neel"]
    rows = []

    for h in h_values:
        hamiltonian = tfim_hamiltonian(num_qubits, h)
        for state_name in states:
            @qml.qnode(dev)
            def energy_circuit():
                prepare_tfim_state(state_name, num_qubits)
                return qml.expval(hamiltonian)

            rows.append(
                {
                    "n_qubits": int(num_qubits),
                    "h": float(h),
                    "state": state_name,
                    "energy": float(energy_circuit()),
                    "analytic": float(analytic_tfim_energy(state_name, num_qubits, h)),
                }
            )

    return rows


def main():
    qubit_counts = (6, 8, 10)
    h_values = (0.0, 0.5, 1.0, 1.5)
    print(f"device={DEVICE_NAME}")
    print("H = sum_i Z_i Z_{i+1} + h * sum_i X_i")
    for num_qubits in qubit_counts:
        print(f"n_qubits={num_qubits}")
        for row in evaluate_tfim_scan(num_qubits, h_values):
            print(
                f"  h={row['h']:.2f} state={row['state']} "
                f"energy={row['energy']:.8f} analytic={row['analytic']:.8f}"
            )


if __name__ == "__main__":
    main()
