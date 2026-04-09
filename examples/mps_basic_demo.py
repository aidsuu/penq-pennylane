import pennylane as qml


DEVICE_NAME = "penq.mps_starter"


def run_mps_basic_demo():
    dev = qml.device(DEVICE_NAME, wires=2)

    @qml.qnode(dev)
    def bell_state():
        qml.Hadamard(0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    @qml.qnode(dev)
    def z0():
        return qml.expval(qml.PauliZ(0))

    return {
        "expval_z0": float(z0()),
        "bell_state": bell_state(),
    }


def main():
    result = run_mps_basic_demo()
    print(f"device={DEVICE_NAME}")
    print("workflow=MPS basic demo")
    print(f"expval_z0={result['expval_z0']:.8f}")
    print("bell_state=" + " ".join(f"{complex(amplitude):.8g}" for amplitude in result["bell_state"]))


if __name__ == "__main__":
    main()
