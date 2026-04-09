import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def prepare_basis_state(label):
    if label == "00":
        return
    if label == "01":
        qml.PauliX(1)
        return
    if label == "10":
        qml.PauliX(0)
        return
    if label == "11":
        qml.PauliX(0)
        qml.PauliX(1)
        return
    raise ValueError("Unsupported basis label. Expected one of: 00, 01, 10, 11.")


def analytic_basis_energy(label, a, b, c):
    values = {
        "00": (1.0, 1.0),
        "01": (1.0, -1.0),
        "10": (-1.0, 1.0),
        "11": (-1.0, -1.0),
    }
    if label not in values:
        raise ValueError("Unsupported basis label. Expected one of: 00, 01, 10, 11.")
    z0, z1 = values[label]
    return a * z0 + b * z1 + c * z0 * z1


def numeric_basis_energy(dev, label, a, b, c):
    @qml.qnode(dev)
    def z0():
        prepare_basis_state(label)
        return qml.expval(qml.PauliZ(0))

    @qml.qnode(dev)
    def z1():
        prepare_basis_state(label)
        return qml.expval(qml.PauliZ(1))

    @qml.qnode(dev)
    def z0z1():
        prepare_basis_state(label)
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    return a * z0() + b * z1() + c * z0z1()


def scan_basis_energies(a, b, c):
    dev = qml.device(DEVICE_NAME, wires=2)
    results = []
    for label in ("00", "01", "10", "11"):
        numeric = numeric_basis_energy(dev, label, a, b, c)
        analytic = analytic_basis_energy(label, a, b, c)
        results.append(
            {
                "state": label,
                "numeric": float(numeric),
                "analytic": float(analytic),
            }
        )
    return results


def main():
    a, b, c = 0.7, -0.2, 1.3
    print(f"device={DEVICE_NAME}")
    print(f"H = {a} * Z0 + {b} * Z1 + {c} * Z0Z1")
    for row in scan_basis_energies(a, b, c):
        print(f"|{row['state']}>: numeric={row['numeric']:.8f} analytic={row['analytic']:.8f}")


if __name__ == "__main__":
    main()
