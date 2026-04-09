import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def validate_chain_inputs(num_qubits, fields_x, couplings_zz):
    if not 6 <= num_qubits <= 12:
        raise ValueError("Ising chain scan expects 6 to 12 qubits.")
    if len(fields_x) != num_qubits:
        raise ValueError("fields_x must have length num_qubits.")
    if len(couplings_zz) != num_qubits - 1:
        raise ValueError("couplings_zz must have length num_qubits - 1.")


def ising_chain_hamiltonian(num_qubits, fields_x, couplings_zz):
    validate_chain_inputs(num_qubits, fields_x, couplings_zz)
    coefficients = []
    terms = []

    for wire, coefficient in enumerate(fields_x):
        coefficients.append(coefficient)
        terms.append(qml.PauliX(wire))

    for wire, coefficient in enumerate(couplings_zz):
        coefficients.append(coefficient)
        terms.append(qml.PauliZ(wire) @ qml.PauliZ(wire + 1))

    return qml.dot(coefficients, terms)


def prepare_chain_state(name, num_qubits):
    if name == "all_zero":
        return
    if name == "all_one":
        for wire in range(num_qubits):
            qml.PauliX(wire)
        return
    if name == "all_plus":
        for wire in range(num_qubits):
            qml.Hadamard(wire)
        return
    if name == "neel":
        for wire in range(1, num_qubits, 2):
            qml.PauliX(wire)
        return
    raise ValueError("Unsupported chain state. Expected one of: all_zero, all_one, all_plus, neel.")


def analytic_chain_energy(name, fields_x, couplings_zz):
    num_qubits = len(fields_x)
    validate_chain_inputs(num_qubits, fields_x, couplings_zz)

    if name == "all_zero":
        return float(sum(couplings_zz))
    if name == "all_one":
        return float(sum(couplings_zz))
    if name == "all_plus":
        return float(sum(fields_x))
    if name == "neel":
        return float(-sum(couplings_zz))

    raise ValueError("Unsupported chain state. Expected one of: all_zero, all_one, all_plus, neel.")


def evaluate_chain_scan(num_qubits, fields_x, couplings_zz):
    validate_chain_inputs(num_qubits, fields_x, couplings_zz)
    dev = qml.device(DEVICE_NAME, wires=num_qubits)
    hamiltonian = ising_chain_hamiltonian(num_qubits, fields_x, couplings_zz)
    states = ["all_zero", "all_one", "all_plus", "neel"]
    results = []

    for state_name in states:
        @qml.qnode(dev)
        def energy_circuit():
            prepare_chain_state(state_name, num_qubits)
            return qml.expval(hamiltonian)

        energy = float(energy_circuit())
        results.append(
            {
                "state": state_name,
                "energy": energy,
                "analytic": float(analytic_chain_energy(state_name, fields_x, couplings_zz)),
            }
        )

    return results


def main():
    num_qubits = 6
    fields_x = [0.25, -0.40, 0.15, 0.05, -0.30, 0.20]
    couplings_zz = [1.10, -0.70, 0.90, 0.40, -1.20]
    print(f"device={DEVICE_NAME}")
    print(f"n_qubits={num_qubits}")
    print("H = sum_i h_i X_i + sum_i J_i Z_i Z_{i+1}")
    for row in evaluate_chain_scan(num_qubits, fields_x, couplings_zz):
        print(
            f"{row['state']}: energy={row['energy']:.8f} analytic={row['analytic']:.8f}"
        )


if __name__ == "__main__":
    main()
