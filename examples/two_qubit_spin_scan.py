import numpy as np
import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def mixed_spin_hamiltonian(coeffs):
    return qml.dot(
        [
            coeffs["x0"],
            coeffs["y0"],
            coeffs["z0"],
            coeffs["x1"],
            coeffs["y1"],
            coeffs["z1"],
            coeffs["zz"],
            coeffs["xx"],
            coeffs["yy"],
        ],
        [
            qml.PauliX(0),
            qml.PauliY(0),
            qml.PauliZ(0),
            qml.PauliX(1),
            qml.PauliY(1),
            qml.PauliZ(1),
            qml.PauliZ(0) @ qml.PauliZ(1),
            qml.PauliX(0) @ qml.PauliX(1),
            qml.PauliY(0) @ qml.PauliY(1),
        ],
    )


def prepare_named_state(name):
    if name == "basis_00":
        return
    if name == "basis_01":
        qml.PauliX(1)
        return
    if name == "plus0_plus1":
        qml.Hadamard(0)
        qml.Hadamard(1)
        return
    if name == "phase0_phase1":
        qml.Hadamard(0)
        qml.RZ(np.pi / 2, wires=0)
        qml.Hadamard(1)
        qml.RZ(np.pi / 2, wires=1)
        return
    if name == "bell":
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return
    raise ValueError(
        "Unsupported scan state. Expected one of: basis_00, basis_01, plus0_plus1, phase0_phase1, bell."
    )


def evaluate_spin_scan(coeffs):
    dev = qml.device(DEVICE_NAME, wires=2)
    hamiltonian = mixed_spin_hamiltonian(coeffs)
    states = ["basis_00", "basis_01", "plus0_plus1", "phase0_phase1", "bell"]
    results = []

    for state_name in states:
        @qml.qnode(dev)
        def energy_circuit():
            prepare_named_state(state_name)
            return qml.expval(hamiltonian)

        results.append({"state": state_name, "energy": float(energy_circuit())})

    return results


def main():
    coeffs = {
        "x0": 0.35,
        "y0": -0.10,
        "z0": 0.80,
        "x1": -0.25,
        "y1": 0.30,
        "z1": -0.40,
        "zz": 1.10,
        "xx": 0.55,
        "yy": -0.45,
    }
    print(f"device={DEVICE_NAME}")
    print(
        "H = "
        f"{coeffs['x0']} X0 + {coeffs['y0']} Y0 + {coeffs['z0']} Z0 + "
        f"{coeffs['x1']} X1 + {coeffs['y1']} Y1 + {coeffs['z1']} Z1 + "
        f"{coeffs['zz']} Z0Z1 + {coeffs['xx']} X0X1 + {coeffs['yy']} Y0Y1"
    )
    for row in evaluate_spin_scan(coeffs):
        print(f"{row['state']}: energy={row['energy']:.8f}")


if __name__ == "__main__":
    main()
