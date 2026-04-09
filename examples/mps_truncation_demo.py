import pennylane as qml


DEVICE_NAME = "penq.mps_starter"


def run_mps_truncation_demo():
    exact_dev = qml.device(DEVICE_NAME, wires=2)
    bounded_dev = qml.device(DEVICE_NAME, wires=2, max_bond_dim=2, svd_cutoff=1e-12)
    truncated_dev = qml.device(DEVICE_NAME, wires=2, max_bond_dim=1, svd_cutoff=0.0)

    @qml.qnode(exact_dev)
    def exact_state():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    @qml.qnode(bounded_dev)
    def bounded_state():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    @qml.qnode(truncated_dev)
    def truncated_state():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    @qml.qnode(exact_dev)
    def exact_zz():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    @qml.qnode(truncated_dev)
    def truncated_zz():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    return {
        "exact_state": exact_state(),
        "bounded_state": bounded_state(),
        "truncated_state": truncated_state(),
        "exact_zz": float(exact_zz()),
        "truncated_zz": float(truncated_zz()),
    }


def main():
    result = run_mps_truncation_demo()
    print(f"device={DEVICE_NAME}")
    print("workflow=MPS truncation demo")
    print("exact_state=" + " ".join(f"{complex(amplitude):.8g}" for amplitude in result["exact_state"]))
    print(
        "bounded_state="
        + " ".join(f"{complex(amplitude):.8g}" for amplitude in result["bounded_state"])
    )
    print(
        "truncated_state="
        + " ".join(f"{complex(amplitude):.8g}" for amplitude in result["truncated_state"])
    )
    print(f"exact_zz={result['exact_zz']:.8f}")
    print(f"truncated_zz={result['truncated_zz']:.8f}")


if __name__ == "__main__":
    main()
