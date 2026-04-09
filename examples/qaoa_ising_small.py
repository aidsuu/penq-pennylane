import numpy as np
import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def ising_cost_hamiltonian(num_qubits):
    if num_qubits < 2:
        raise ValueError("QAOA Ising example expects at least 2 qubits.")
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


def qaoa_energy(dev, num_qubits, gamma, beta):
    hamiltonian = ising_cost_hamiltonian(num_qubits)

    @qml.qnode(dev)
    def circuit():
        for wire in range(num_qubits):
            qml.Hadamard(wire)
        qaoa_layer(num_qubits, gamma, beta)
        return qml.expval(hamiltonian)

    return float(circuit())


def exact_classical_minimum(num_qubits):
    return float(-(num_qubits - 1))


def qaoa_grid_search(num_qubits=4, num_gamma=9, num_beta=9):
    dev = qml.device(DEVICE_NAME, wires=num_qubits)
    gamma_grid = np.linspace(0.0, np.pi, num_gamma)
    beta_grid = np.linspace(0.0, np.pi / 2.0, num_beta)
    best_energy = None
    best_params = None

    for gamma in gamma_grid:
        for beta in beta_grid:
            energy = qaoa_energy(dev, num_qubits, gamma, beta)
            if best_energy is None or energy < best_energy:
                best_energy = energy
                best_params = (float(gamma), float(beta))

    return {
        "num_qubits": int(num_qubits),
        "best_energy": float(best_energy),
        "best_gamma": best_params[0],
        "best_beta": best_params[1],
        "exact_classical_minimum": exact_classical_minimum(num_qubits),
    }


def main():
    result = qaoa_grid_search(num_qubits=4, num_gamma=9, num_beta=9)
    print(f"device={DEVICE_NAME}")
    print("workflow=QAOA p=1 for open-chain Ising cost sum_i Z_i Z_{i+1}")
    print(f"n_qubits = {result['num_qubits']}")
    print(f"best_energy = {result['best_energy']:.8f}")
    print(f"best_gamma = {result['best_gamma']:.8f}")
    print(f"best_beta = {result['best_beta']:.8f}")
    print(f"exact_classical_minimum = {result['exact_classical_minimum']:.8f}")


if __name__ == "__main__":
    main()
