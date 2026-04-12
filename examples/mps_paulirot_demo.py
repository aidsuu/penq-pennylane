import pennylane as qml


MPS_DEVICE_NAME = "penq.mps_starter"
STATEVECTOR_DEVICE_NAME = "penq.qml_starter"


def paulirot_demo_rows():
    mps_dev = qml.device(MPS_DEVICE_NAME, wires=3, max_bond_dim=4, svd_cutoff=1e-12)
    reference_dev = qml.device(STATEVECTOR_DEVICE_NAME, wires=3)

    cases = [
        ("CZ_state_overlap", lambda: qml.CZ(wires=[0, 1]), qml.PauliX(0) @ qml.PauliX(1)),
        ("PauliRot_XY", lambda: qml.PauliRot(0.41, "XY", wires=[0, 2]), qml.PauliX(0) @ qml.PauliY(2)),
        ("IsingYY", lambda: qml.IsingYY(0.29, wires=[1, 2]), qml.PauliY(1) @ qml.PauliY(2)),
    ]

    rows = []
    for label, operation_builder, observable in cases:
        @qml.qnode(mps_dev)
        def mps_circuit(op_builder=operation_builder, obs=observable):
            qml.Hadamard(0)
            qml.RX(-0.3, wires=1)
            qml.RY(0.2, wires=2)
            op_builder()
            return qml.expval(obs)

        @qml.qnode(reference_dev)
        def reference_circuit(op_builder=operation_builder, obs=observable):
            qml.Hadamard(0)
            qml.RX(-0.3, wires=1)
            qml.RY(0.2, wires=2)
            op_builder()
            return qml.expval(obs)

        mps_value = float(mps_circuit())
        reference_value = float(reference_circuit())
        rows.append(
            {
                "case": label,
                "mps_value": mps_value,
                "reference_value": reference_value,
                "abs_error": abs(mps_value - reference_value),
            }
        )

    return rows


def main():
    rows = paulirot_demo_rows()
    print(f"device={MPS_DEVICE_NAME}")
    print(f"reference_device={STATEVECTOR_DEVICE_NAME}")
    print("workflow=MPS PauliRot and general two-qubit gate demo")
    for row in rows:
        print(
            f"case={row['case']} mps={row['mps_value']:.8f} "
            f"ref={row['reference_value']:.8f} abs_error={row['abs_error']:.8f}"
        )


if __name__ == "__main__":
    main()
