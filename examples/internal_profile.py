import time

import numpy as np
import pennylane as qml

from QML.PenQ import QMLStarterDevice


DEVICE_NAME = "penq.qml_starter"


def profile_angles(num_wires):
    return [0.05 * (wire + 1) for wire in range(num_wires)]


def single_qubit_gate_profile(dev, repeats=1):
    angles = profile_angles(dev.num_wires)
    start = time.perf_counter()
    for _ in range(repeats):
        state = dev._initialize_basis_state(0)
        for wire, angle in enumerate(angles):
            operation = qml.RY(angle, wires=wire)
            matrix = dev._single_qubit_matrix(operation)
            dev._apply_single_qubit_gate_inplace(state, matrix, wire)
    elapsed = time.perf_counter() - start
    return {
        "stage": "single_qubit_gates",
        "repeats": int(repeats),
        "elapsed_seconds": float(elapsed),
        "seconds_per_run": float(elapsed / repeats),
    }


def cnot_profile(dev, repeats=1):
    start = time.perf_counter()
    for _ in range(repeats):
        state = dev._initialize_basis_state(0)
        state[0] = 0.0
        state[1 << (dev.num_wires - 1)] = 1.0
        for wire in range(dev.num_wires - 1):
            dev._apply_cnot_inplace(state, wire, wire + 1)
    elapsed = time.perf_counter() - start
    return {
        "stage": "cnot_chain",
        "repeats": int(repeats),
        "elapsed_seconds": float(elapsed),
        "seconds_per_run": float(elapsed / repeats),
    }


def pauli_word_profile(dev, repeats=1):
    state = dev._initialize_basis_state(0)
    for wire, angle in enumerate(profile_angles(dev.num_wires)):
        operation = qml.RY(angle, wires=wire)
        matrix = dev._single_qubit_matrix(operation)
        dev._apply_single_qubit_gate_inplace(state, matrix, wire)

    wires = [0, dev.num_wires // 2, dev.num_wires - 1]
    pauli_names = ["PauliX", "PauliY", "PauliZ"]

    start = time.perf_counter()
    value = None
    for _ in range(repeats):
        value = dev._expval_pauli_product(state, pauli_names, wires)
    elapsed = time.perf_counter() - start
    return {
        "stage": "pauli_word_expval",
        "repeats": int(repeats),
        "elapsed_seconds": float(elapsed),
        "seconds_per_run": float(elapsed / repeats),
        "final_value": float(value),
        "pauli_word": "X(0) @ Y(mid) @ Z(last)",
    }


def tape_setup_profile(num_wires, repeats=1):
    angles = profile_angles(num_wires)

    start = time.perf_counter()
    for _ in range(repeats):
        with qml.tape.QuantumTape() as tape:
            for wire, angle in enumerate(angles):
                qml.Hadamard(wire)
                qml.RY(angle, wires=wire)
            for wire in range(num_wires - 1):
                qml.CNOT(wires=[wire, wire + 1])
            qml.expval(qml.PauliX(0) @ qml.PauliY(num_wires // 2) @ qml.PauliZ(num_wires - 1))
    elapsed = time.perf_counter() - start
    return {
        "stage": "tape_setup",
        "repeats": int(repeats),
        "elapsed_seconds": float(elapsed),
        "seconds_per_run": float(elapsed / repeats),
        "operation_count": len(tape.operations),
        "measurement_count": len(tape.measurements),
    }


def measurement_handling_profile(dev, repeats=1):
    angles = profile_angles(dev.num_wires)
    state = dev._initialize_basis_state(0)
    for wire, angle in enumerate(angles):
        operation = qml.RY(angle, wires=wire)
        matrix = dev._single_qubit_matrix(operation)
        dev._apply_single_qubit_gate_inplace(state, matrix, wire)
    dev._state = state
    dev._pre_rotated_state = state
    observable = qml.PauliX(0) @ qml.PauliY(dev.num_wires // 2) @ qml.PauliZ(dev.num_wires - 1)

    start = time.perf_counter()
    value = None
    for _ in range(repeats):
        value = dev.expval(observable)
    elapsed = time.perf_counter() - start
    return {
        "stage": "measurement_handling",
        "repeats": int(repeats),
        "elapsed_seconds": float(elapsed),
        "seconds_per_run": float(elapsed / repeats),
        "final_value": float(value),
    }


def execute_path_profile(num_wires, repeats=1):
    dev = QMLStarterDevice(wires=num_wires)
    angles = profile_angles(num_wires)
    with qml.tape.QuantumTape() as tape:
        for wire, angle in enumerate(angles):
            qml.Hadamard(wire)
            qml.RY(angle, wires=wire)
        for wire in range(num_wires - 1):
            qml.CNOT(wires=[wire, wire + 1])
        qml.expval(qml.PauliX(0) @ qml.PauliY(num_wires // 2) @ qml.PauliZ(num_wires - 1))

    dev.execute(tape)
    start = time.perf_counter()
    value = None
    for _ in range(repeats):
        value = dev.execute(tape)
    elapsed = time.perf_counter() - start
    return {
        "stage": "execute_path",
        "repeats": int(repeats),
        "elapsed_seconds": float(elapsed),
        "seconds_per_run": float(elapsed / repeats),
        "final_value": float(value),
    }


def qnode_profile(num_wires, repeats=1):
    dev = qml.device(DEVICE_NAME, wires=num_wires)
    angles = profile_angles(num_wires)

    @qml.qnode(dev)
    def circuit():
        for wire, angle in enumerate(angles):
            qml.Hadamard(wire)
            qml.RY(angle, wires=wire)
        for wire in range(num_wires - 1):
            qml.CNOT(wires=[wire, wire + 1])
        return qml.expval(qml.PauliX(0) @ qml.PauliY(num_wires // 2) @ qml.PauliZ(num_wires - 1))

    circuit()
    start = time.perf_counter()
    value = None
    for _ in range(repeats):
        value = circuit()
    elapsed = time.perf_counter() - start
    return {
        "stage": "qnode_end_to_end",
        "repeats": int(repeats),
        "elapsed_seconds": float(elapsed),
        "seconds_per_run": float(elapsed / repeats),
        "final_value": float(value),
    }


def profile_rows(wire_counts=(8, 12, 16), repeats=1):
    rows = []
    for num_wires in wire_counts:
        internal_dev = QMLStarterDevice(wires=num_wires)
        stage_rows = [
            single_qubit_gate_profile(internal_dev, repeats=repeats),
            cnot_profile(internal_dev, repeats=repeats),
            pauli_word_profile(internal_dev, repeats=repeats),
            tape_setup_profile(num_wires, repeats=repeats),
            measurement_handling_profile(internal_dev, repeats=repeats),
            execute_path_profile(num_wires, repeats=repeats),
            qnode_profile(num_wires, repeats=repeats),
        ]
        rows.append({"wires": int(num_wires), "stages": stage_rows})
    return rows


def main():
    print(f"device={DEVICE_NAME}")
    print("Deterministic internal profiling on safe wire counts")
    print(
        "stages: single_qubit_gates, cnot_chain, pauli_word_expval, tape_setup, "
        "measurement_handling, execute_path, qnode_end_to_end"
    )
    for row in profile_rows():
        print(f"wires={row['wires']}")
        for stage in row["stages"]:
            line = (
                f"  {stage['stage']}: repeats={stage['repeats']} "
                f"elapsed_s={stage['elapsed_seconds']:.6f} "
                f"per_run_s={stage['seconds_per_run']:.6f}"
            )
            if "final_value" in stage:
                line += f" final_value={stage['final_value']:.8f}"
            if "pauli_word" in stage:
                line += f" pauli_word={stage['pauli_word']}"
            if "operation_count" in stage:
                line += (
                    f" operation_count={stage['operation_count']} "
                    f"measurement_count={stage['measurement_count']}"
                )
            print(line)


if __name__ == "__main__":
    main()
