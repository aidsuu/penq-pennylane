import numpy as np
import pennylane as qml


DEVICE_NAME = "penq.qml_starter"


def ansatz(theta0, theta1):
    qml.RY(theta0, wires=0)
    qml.RY(theta1, wires=1)
    qml.CNOT(wires=[0, 1])


def energy_from_qnodes(dev, a, b, c, theta0, theta1):
    @qml.qnode(dev)
    def z0():
        ansatz(theta0, theta1)
        return qml.expval(qml.PauliZ(0))

    @qml.qnode(dev)
    def z1():
        ansatz(theta0, theta1)
        return qml.expval(qml.PauliZ(1))

    @qml.qnode(dev)
    def z0z1():
        ansatz(theta0, theta1)
        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

    return a * z0() + b * z1() + c * z0z1()


def analytic_minimum(a, b, c):
    energies = [a * z0 + b * z1 + c * z0 * z1 for z0 in (1.0, -1.0) for z1 in (1.0, -1.0)]
    return min(energies)


def grid_search(a, b, c, num_points=17):
    dev = qml.device(DEVICE_NAME, wires=2)
    angle_grid = np.linspace(0.0, np.pi, num_points)
    best_energy = None
    best_thetas = None

    for theta0 in angle_grid:
        for theta1 in angle_grid:
            energy = energy_from_qnodes(dev, a, b, c, theta0, theta1)
            if best_energy is None or energy < best_energy:
                best_energy = energy
                best_thetas = (float(theta0), float(theta1))

    return {
        "best_energy": float(best_energy),
        "best_thetas": best_thetas,
        "analytic_minimum": float(analytic_minimum(a, b, c)),
    }


def main():
    a, b, c = 0.6, -0.9, 0.35
    result = grid_search(a, b, c)
    print(f"device={DEVICE_NAME}")
    print(f"H = {a} * Z0 + {b} * Z1 + {c} * Z0Z1")
    print(f"best_energy = {result['best_energy']:.8f}")
    print(f"best_thetas = ({result['best_thetas'][0]:.8f}, {result['best_thetas'][1]:.8f})")
    print(f"analytic_minimum = {result['analytic_minimum']:.8f}")


if __name__ == "__main__":
    main()
