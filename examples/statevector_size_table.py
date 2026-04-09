DEVICE_NAME = "penq.qml_starter"


def amplitude_count(num_wires):
    if num_wires < 1:
        raise ValueError("num_wires must be at least 1.")
    return 1 << num_wires


def statevector_bytes(num_wires, bytes_per_amplitude=16):
    if bytes_per_amplitude < 1:
        raise ValueError("bytes_per_amplitude must be at least 1.")
    return amplitude_count(num_wires) * bytes_per_amplitude


def format_gib(byte_count):
    gib = byte_count / float(1024**3)
    return f"{gib:.3f} GiB"


def statevector_size_rows(wire_counts=(8, 12, 16, 20, 24, 28, 30)):
    rows = []
    for num_wires in wire_counts:
        amplitudes = amplitude_count(num_wires)
        memory_bytes = statevector_bytes(num_wires)
        rows.append(
            {
                "wires": int(num_wires),
                "amplitudes": int(amplitudes),
                "memory_bytes": int(memory_bytes),
                "memory_gib": format_gib(memory_bytes),
            }
        )
    return rows


def main():
    print(f"device={DEVICE_NAME}")
    print("Assumption: complex128 statevector, 16 bytes per amplitude")
    print("wires amplitudes memory_bytes memory_gib")
    for row in statevector_size_rows():
        print(
            f"{row['wires']:>5} {row['amplitudes']:>12} {row['memory_bytes']:>12} {row['memory_gib']}"
        )


if __name__ == "__main__":
    main()
