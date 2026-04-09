import numpy as np
import pennylane as qml


MPS_DEVICE_NAME = "penq.mps_starter"
STATEVECTOR_DEVICE_NAME = "penq.qml_starter"


def general_pauli_demo_rows():
    mps_dev = qml.device(MPS_DEVICE_NAME, wires=3, max_bond_dim=4, svd_cutoff=1e-12)
    reference_dev = qml.device(STATEVECTOR_DEVICE_NAME, wires=3)

    observables = [
        ("X0", qml.PauliX(0)),
        ("Y1", qml.PauliY(1)),
        ("X0@Y1@X2", qml.PauliX(0) @ qml.PauliY(1) @ qml.PauliX(2)),
    ]

    rows = []
    for label, observable in observables:
        @qml.qnode(mps_dev)
        def mps_circuit(obs=observable):
            qml.Hadamard(0)
            qml.RX(-np.pi / 2.0, wires=1)
            qml.CNOT(wires=[0, 2])
            return qml.expval(obs)

        @qml.qnode(reference_dev)
        def reference_circuit(obs=observable):
            qml.Hadamard(0)
            qml.RX(-np.pi / 2.0, wires=1)
            qml.CNOT(wires=[0, 2])
            return qml.expval(obs)

        mps_value = float(mps_circuit())
        reference_value = float(reference_circuit())
        rows.append(
            {
                "observable": label,
                "mps_value": mps_value,
                "reference_value": reference_value,
                "abs_error": abs(mps_value - reference_value),
            }
        )

    return rows


def main():
    rows = general_pauli_demo_rows()
    print(f"device={MPS_DEVICE_NAME}")
    print(f"reference_device={STATEVECTOR_DEVICE_NAME}")
    print("workflow=MPS general Pauli demo")
    print("circuit = H(0), RX(-pi/2,1), routed CNOT(0,2)")
    for row in rows:
        print(
            f"observable={row['observable']} mps={row['mps_value']:.8f} "
            f"ref={row['reference_value']:.8f} abs_error={row['abs_error']:.8f}"
        )


if __name__ == "__main__":
    main()
