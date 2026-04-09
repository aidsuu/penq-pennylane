import time

import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def benchmark_angles(num_wires):
    return [0.05 * (wire + 1) for wire in range(num_wires)]


def benchmark_circuit(depth_angles):
    num_wires = len(depth_angles)
    for wire, angle in enumerate(depth_angles):
        qml.Hadamard(wire)
        qml.RY(angle, wires=wire)

    for wire in range(num_wires - 1):
        qml.CNOT(wires=[wire, wire + 1])

    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(num_wires - 1))


def measure_benchmark(dev, repeats=1):
    depth_angles = benchmark_angles(dev.num_wires)

    @qml.qnode(dev)
    def circuit():
        return benchmark_circuit(depth_angles)

    circuit()
    start = time.perf_counter()
    value = None
    for _ in range(repeats):
        value = circuit()
    elapsed = time.perf_counter() - start
    return {
        "repeats": int(repeats),
        "elapsed_seconds": float(elapsed),
        "seconds_per_run": float(elapsed / repeats),
        "final_value": float(value),
    }


def performance_rows(wire_counts=(8, 12, 16), repeats=1):
    rows = []
    for num_wires in wire_counts:
        dev = qml.device(DEVICE_NAME, wires=num_wires)
        measurement = measure_benchmark(dev, repeats=repeats)
        rows.append(
            {
                "wires": int(num_wires),
                "repeats": measurement["repeats"],
                "elapsed_seconds": measurement["elapsed_seconds"],
                "seconds_per_run": measurement["seconds_per_run"],
                "final_value": measurement["final_value"],
            }
        )
    return rows


def main():
    print(f"device={DEVICE_NAME}")
    print("Deterministic benchmark: one fixed shallow circuit per wire count")
    print("Times depend on the machine, but growth is expected to be roughly exponential in n")
    print("wires repeats elapsed_s per_run_s final_expval")
    for row in performance_rows():
        print(
            f"{row['wires']:>5} {row['repeats']:>7} "
            f"{row['elapsed_seconds']:.6f} {row['seconds_per_run']:.6f} {row['final_value']:.8f}"
        )


if __name__ == "__main__":
    main()
