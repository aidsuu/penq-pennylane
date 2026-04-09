import pathlib
import sys
import tomllib
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import pennylane as qml
except ImportError:  # pragma: no cover - dependency is external to this repo
    qml = None

if qml is not None:
    from QML.PenQ import QMLStarterDevice
else:  # pragma: no cover - dependency is external to this repo
    QMLStarterDevice = None


@unittest.skipIf(qml is None, "PennyLane is not installed")
class TestQMLStarterDevice(unittest.TestCase):
    @staticmethod
    def _integration_device(wires):
        try:
            return qml.device(QMLStarterDevice.short_name, wires=wires)
        except Exception:
            return QMLStarterDevice(wires=wires)

    @staticmethod
    def _ising_energy_from_qnodes(dev, a, b, c, prepare=None):
        @qml.qnode(dev)
        def z0():
            if prepare is not None:
                prepare()
            return qml.expval(qml.PauliZ(0))

        @qml.qnode(dev)
        def z1():
            if prepare is not None:
                prepare()
            return qml.expval(qml.PauliZ(1))

        @qml.qnode(dev)
        def z0z1():
            if prepare is not None:
                prepare()
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        return a * z0() + b * z1() + c * z0z1()

    @staticmethod
    def _ansatz_energy_from_qnodes(dev, a, b, c, theta0, theta1):
        @qml.qnode(dev)
        def z0():
            qml.RY(theta0, wires=0)
            qml.RY(theta1, wires=1)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0))

        @qml.qnode(dev)
        def z1():
            qml.RY(theta0, wires=0)
            qml.RY(theta1, wires=1)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(1))

        @qml.qnode(dev)
        def z0z1():
            qml.RY(theta0, wires=0)
            qml.RY(theta1, wires=1)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        return a * z0() + b * z1() + c * z0z1()

    def test_zero_state_expval_z_is_one(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            return qml.expval(qml.PauliZ(0))

        self.assertAlmostEqual(circuit(), 1.0)

    def test_x_flips_expval_z(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(0)
            return qml.expval(qml.PauliZ(0))

        self.assertAlmostEqual(circuit(), -1.0)

    def test_hadamard_returns_expected_state(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            return qml.state()

        expected = np.array([1 / np.sqrt(2), 1 / np.sqrt(2)], dtype=np.complex128)
        np.testing.assert_allclose(circuit(), expected, atol=1e-8)

    def test_bell_state(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        expected = np.array([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)], dtype=np.complex128)
        np.testing.assert_allclose(circuit(), expected, atol=1e-8)

    def test_rx_pi_flips_expval_z(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            qml.RX(np.pi, wires=0)
            return qml.expval(qml.PauliZ(0))

        self.assertAlmostEqual(circuit(), -1.0, places=7)

    def test_bell_state_is_normalized(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        state = circuit()
        self.assertAlmostEqual(float(np.sum(np.abs(state) ** 2)), 1.0, places=8)

    def test_batch_execute_simple(self):
        dev = self._integration_device(wires=1)
        with qml.tape.QuantumTape() as tape0:
            qml.expval(qml.PauliZ(0))
        with qml.tape.QuantumTape() as tape1:
            qml.PauliX(0)
            qml.expval(qml.PauliZ(0))

        results = dev.batch_execute([tape0, tape1])
        np.testing.assert_allclose(results, [1.0, -1.0], atol=1e-8)

    def test_invalid_shots_raises_value_error(self):
        with self.assertRaisesRegex(
            ValueError, "analytic execution only; shots must be None or 0"
        ):
            QMLStarterDevice(wires=1, shots=10)

    def test_invalid_wire_count_above_thirty_raises_value_error(self):
        with self.assertRaisesRegex(ValueError, "supports between 1 and 30 wires"):
            QMLStarterDevice(wires=31)

    def test_qnode_loader_or_direct_device_path(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            return qml.expval(qml.PauliZ(0))

        self.assertAlmostEqual(circuit(), 1.0)

    def test_plus_state_expval_x_is_one(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            return qml.expval(qml.PauliX(0))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_phase_state_expval_y_is_one(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.RZ(np.pi / 2, wires=0)
            return qml.expval(qml.PauliY(0))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_phase_state_on_wire_one_expval_y_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(1)
            qml.RZ(np.pi / 2, wires=1)
            return qml.expval(qml.PauliY(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_plus_state_on_wire_one_expval_x_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(1)
            return qml.expval(qml.PauliX(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_bell_state_expval_zz_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_bell_state_expval_xx_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliX(0) @ qml.PauliX(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_bell_state_expval_yy_is_minus_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliY(0) @ qml.PauliY(1))

        self.assertAlmostEqual(circuit(), -1.0, places=8)

    def test_plus_zero_state_expval_xz_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            return qml.expval(qml.PauliX(0) @ qml.PauliZ(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_zero_plus_state_expval_zx_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(1)
            return qml.expval(qml.PauliZ(0) @ qml.PauliX(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_phase_zero_state_expval_yz_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.RZ(np.pi / 2, wires=0)
            return qml.expval(qml.PauliY(0) @ qml.PauliZ(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_zero_phase_state_expval_zy_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(1)
            qml.RZ(np.pi / 2, wires=1)
            return qml.expval(qml.PauliZ(0) @ qml.PauliY(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_z0_z7_on_ten_qubits(self):
        dev = self._integration_device(wires=10)

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(7)
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(7))

        self.assertAlmostEqual(circuit(), -1.0, places=8)

    def test_x1_y9_on_ten_qubits(self):
        dev = self._integration_device(wires=10)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(1)
            qml.Hadamard(9)
            qml.RZ(np.pi / 2, wires=9)
            return qml.expval(qml.PauliX(1) @ qml.PauliY(9))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_x1_y9_z13_on_sixteen_qubits(self):
        dev = self._integration_device(wires=16)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(1)
            qml.Hadamard(9)
            qml.RZ(np.pi / 2, wires=9)
            return qml.expval(qml.PauliX(1) @ qml.PauliY(9) @ qml.PauliZ(13))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_product_state_expval_zz_is_minus_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(1)
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        self.assertAlmostEqual(circuit(), -1.0, places=8)

    def test_two_qubit_ising_energy_basis_states(self):
        a, b, c = 0.7, -0.2, 1.3
        cases = [
            ("00", lambda: None, a + b + c),
            ("01", lambda: qml.PauliX(1), a - b - c),
            ("10", lambda: qml.PauliX(0), -a + b - c),
            ("11", lambda: (qml.PauliX(0), qml.PauliX(1)), -a - b + c),
        ]

        for label, prepare, expected in cases:
            with self.subTest(state=label):
                dev = self._integration_device(wires=2)
                energy = self._ising_energy_from_qnodes(dev, a, b, c, prepare=prepare)
                self.assertAlmostEqual(energy, expected, places=8)

    def test_z1_qnode_integration_on_basis_state(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(1)
            return qml.expval(qml.PauliZ(1))

        self.assertAlmostEqual(circuit(), -1.0, places=8)

    def test_x_on_wire_seven_in_ten_qubits(self):
        dev = self._integration_device(wires=10)

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(7)
            return qml.expval(qml.PauliZ(7))

        self.assertAlmostEqual(circuit(), -1.0, places=8)

    def test_z_on_wire_nine_in_ten_qubits(self):
        dev = self._integration_device(wires=10)

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(9)
            return qml.expval(qml.PauliZ(9))

        self.assertAlmostEqual(circuit(), -1.0, places=8)

    def test_non_adjacent_cnot_state_in_ten_qubits(self):
        dev = self._integration_device(wires=10)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(2)
            qml.CNOT(wires=[2, 9])
            return qml.state()

        expected = np.zeros(2**10, dtype=np.complex128)
        expected[0] = 1 / np.sqrt(2)
        expected[(1 << (10 - 2 - 1)) | (1 << (10 - 9 - 1))] = 1 / np.sqrt(2)
        np.testing.assert_allclose(circuit(), expected, atol=1e-8)

    def test_large_statevector_path_in_sixteen_qubits(self):
        dev = self._integration_device(wires=16)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(15)
            return qml.expval(qml.PauliX(15))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_two_qubit_ry_cnot_ansatz_observables(self):
        dev = self._integration_device(wires=2)
        theta = np.pi / 3

        @qml.qnode(dev)
        def expval_z0():
            qml.RY(theta, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0))

        @qml.qnode(dev)
        def expval_z1():
            qml.RY(theta, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(1))

        @qml.qnode(dev)
        def expval_z0z1():
            qml.RY(theta, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        self.assertAlmostEqual(expval_z0(), np.cos(theta), places=8)
        self.assertAlmostEqual(expval_z1(), np.cos(theta), places=8)
        self.assertAlmostEqual(expval_z0z1(), 1.0, places=8)

    def test_unsupported_observable_raises_explicit_error(self):
        dev = QMLStarterDevice(wires=1)

        class UnsupportedObservable:
            name = "Hadamard"
            wires = (0,)

        with self.assertRaisesRegex(
            Exception,
            "Unsupported measurement: supported expectation values are",
        ):
            dev.expval(UnsupportedObservable())

    def test_two_qubit_vqe_grid_search_matches_analytic_minimum(self):
        a, b, c = 0.6, -0.9, 0.35
        angle_grid = np.linspace(0.0, np.pi, 17)
        best_energy = None
        best_angles = None

        for theta0 in angle_grid:
            for theta1 in angle_grid:
                dev = self._integration_device(wires=2)
                energy = self._ansatz_energy_from_qnodes(dev, a, b, c, theta0, theta1)
                if best_energy is None or energy < best_energy:
                    best_energy = energy
                    best_angles = (theta0, theta1)

        analytic_corner_energies = [
            a * z0 + b * z0 * z1 + c * z1
            for z0 in (1.0, -1.0)
            for z1 in (1.0, -1.0)
        ]
        analytic_minimum = min(analytic_corner_energies)

        self.assertIsNotNone(best_angles)
        self.assertAlmostEqual(best_energy, analytic_minimum, places=8)

    def test_direct_hamiltonian_expval_single_qnode(self):
        dev = self._integration_device(wires=2)
        a, b, c = 0.7, -0.2, 1.3
        hamiltonian = qml.dot(
            [a, b, c],
            [qml.PauliZ(0), qml.PauliZ(1), qml.PauliZ(0) @ qml.PauliZ(1)],
        )

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(0)
            return qml.expval(hamiltonian)

        self.assertAlmostEqual(circuit(), -a + b - c, places=8)

    def test_direct_mixed_hamiltonian_expval_single_qnode(self):
        dev = self._integration_device(wires=2)
        a, b, c, d = 0.7, -0.2, 1.3, 0.5
        hamiltonian = qml.dot(
            [a, b, c, d],
            [
                qml.PauliZ(0),
                qml.PauliZ(1),
                qml.PauliZ(0) @ qml.PauliZ(1),
                qml.PauliX(0) @ qml.PauliX(1),
            ],
        )

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(hamiltonian)

        self.assertAlmostEqual(circuit(), c + d, places=8)

    def test_direct_hamiltonian_with_zz_and_xz_terms(self):
        dev = self._integration_device(wires=2)
        c, d = 1.3, 0.5
        theta = np.pi / 3
        hamiltonian = qml.dot(
            [c, d],
            [qml.PauliZ(0) @ qml.PauliZ(1), qml.PauliX(0) @ qml.PauliZ(1)],
        )

        @qml.qnode(dev)
        def circuit():
            qml.RY(theta, wires=0)
            return qml.expval(hamiltonian)

        self.assertAlmostEqual(circuit(), c * np.cos(theta) + d * np.sin(theta), places=8)

    def test_direct_linear_combination_with_single_qubit_x1_y1_terms(self):
        dev = self._integration_device(wires=2)
        a, b, c = 0.4, -0.6, 0.8
        hamiltonian = qml.dot(
            [a, b, c],
            [qml.PauliX(1), qml.PauliY(1), qml.PauliZ(0)],
        )

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(1)
            qml.RZ(np.pi / 2, wires=1)
            return qml.expval(hamiltonian)

        self.assertAlmostEqual(circuit(), b + c, places=8)

    def test_direct_linear_combination_with_arbitrary_pauli_words(self):
        dev = self._integration_device(wires=16)
        a, b, c = 0.3, -0.8, 0.55
        hamiltonian = qml.dot(
            [a, b, c],
            [
                qml.PauliZ(0) @ qml.PauliZ(7),
                qml.PauliX(1) @ qml.PauliY(9),
                qml.PauliX(1) @ qml.PauliY(9) @ qml.PauliZ(13),
            ],
        )

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(7)
            qml.Hadamard(1)
            qml.Hadamard(9)
            qml.RZ(np.pi / 2, wires=9)
            return qml.expval(hamiltonian)

        self.assertAlmostEqual(circuit(), -a + b + c, places=8)

    def test_direct_spin_chain_hamiltonian_expval_on_six_qubits(self):
        dev = self._integration_device(wires=6)
        fields_x = [0.25, -0.40, 0.15, 0.05, -0.30, 0.20]
        couplings_zz = [1.10, -0.70, 0.90, 0.40, -1.20]
        coefficients = list(fields_x) + list(couplings_zz)
        terms = [qml.PauliX(wire) for wire in range(6)] + [
            qml.PauliZ(wire) @ qml.PauliZ(wire + 1) for wire in range(5)
        ]
        hamiltonian = qml.dot(coefficients, terms)

        @qml.qnode(dev)
        def circuit():
            for wire in range(6):
                qml.Hadamard(wire)
            return qml.expval(hamiltonian)

        self.assertAlmostEqual(circuit(), sum(fields_x), places=8)

    def test_direct_hamiltonian_with_unsupported_term_raises_explicit_error(self):
        dev = self._integration_device(wires=1)
        hamiltonian = qml.dot([1.0], [qml.Hadamard(0)])

        @qml.qnode(dev)
        def circuit():
            return qml.expval(hamiltonian)

        with self.assertRaisesRegex(
            Exception,
            "linear combinations of those observables",
        ):
            circuit()

    def test_unsupported_mixed_two_qubit_observable_raises_explicit_error(self):
        dev = QMLStarterDevice(wires=2)
        with self.assertRaisesRegex(
            Exception,
            "arbitrary Pauli-word tensor products",
        ):
            dev.expval(qml.PauliX(0) @ qml.Hadamard(1))


class TestPenQPackagingMetadata(unittest.TestCase):
    def test_pyproject_declares_pennylane_plugin_entry_point(self):
        pyproject_path = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
        with pyproject_path.open("rb") as handle:
            metadata = tomllib.load(handle)

        entry_points = metadata["project"]["entry-points"]["pennylane.plugins"]
        self.assertEqual(entry_points["penq.qml_starter"], "QML.PenQ:QMLStarterDevice")


if __name__ == "__main__":
    unittest.main()
