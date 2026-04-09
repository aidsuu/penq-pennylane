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
    from QML.PenQ import QMLMPSDevice
    from QML.PenQ import QMLStarterDevice
else:  # pragma: no cover - dependency is external to this repo
    QMLMPSDevice = None
    QMLStarterDevice = None


@unittest.skipIf(qml is None, "PennyLane is not installed")
class TestQMLMPSDevice(unittest.TestCase):
    @staticmethod
    def _integration_device(wires):
        try:
            return qml.device(QMLMPSDevice.short_name, wires=wires)
        except Exception:
            return QMLMPSDevice(wires=wires)

    def test_zero_state_expval_z_is_one(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            return qml.expval(qml.PauliZ(0))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_x_flips_expval_z(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(0)
            return qml.expval(qml.PauliZ(0))

        self.assertAlmostEqual(circuit(), -1.0, places=8)

    def test_bell_state(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        expected = np.array([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)], dtype=np.complex128)
        np.testing.assert_allclose(circuit(), expected, atol=1e-8)

    def test_bell_state_with_large_enough_truncation_is_identical(self):
        dev = QMLMPSDevice(wires=2, max_bond_dim=2, svd_cutoff=1e-12)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        expected = np.array([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)], dtype=np.complex128)
        np.testing.assert_allclose(circuit(), expected, atol=1e-8)

    def test_bell_state_expval_zz_is_one(self):
        dev = self._integration_device(wires=2)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_expval_x_is_supported(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            qml.Hadamard(0)
            return qml.expval(qml.PauliX(0))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_expval_y_is_supported(self):
        dev = self._integration_device(wires=1)

        @qml.qnode(dev)
        def circuit():
            qml.RX(-np.pi / 2.0, wires=0)
            return qml.expval(qml.PauliY(0))

        self.assertAlmostEqual(circuit(), 1.0, places=8)

    def test_multi_wire_pauli_word_matches_qml_starter(self):
        mps_dev = QMLMPSDevice(wires=3, max_bond_dim=4, svd_cutoff=1e-12)
        statevector_dev = QMLStarterDevice(wires=3)

        @qml.qnode(mps_dev)
        def mps_circuit():
            qml.Hadamard(0)
            qml.RX(-np.pi / 2.0, wires=1)
            qml.CNOT(wires=[0, 2])
            return qml.expval(qml.PauliX(0) @ qml.PauliY(1) @ qml.PauliX(2))

        @qml.qnode(statevector_dev)
        def statevector_circuit():
            qml.Hadamard(0)
            qml.RX(-np.pi / 2.0, wires=1)
            qml.CNOT(wires=[0, 2])
            return qml.expval(qml.PauliX(0) @ qml.PauliY(1) @ qml.PauliX(2))

        self.assertAlmostEqual(mps_circuit(), statevector_circuit(), places=8)

    def test_linear_combination_of_pauli_words_is_supported(self):
        mps_dev = QMLMPSDevice(wires=3, max_bond_dim=4, svd_cutoff=1e-12)
        statevector_dev = QMLStarterDevice(wires=3)
        hamiltonian = qml.dot(
            [0.5, -0.25, 0.75],
            [
                qml.PauliX(0),
                qml.PauliY(1),
                qml.PauliX(0) @ qml.PauliY(1) @ qml.PauliX(2),
            ],
        )

        @qml.qnode(mps_dev)
        def mps_circuit():
            qml.Hadamard(0)
            qml.RX(-np.pi / 2.0, wires=1)
            qml.CNOT(wires=[0, 2])
            return qml.expval(hamiltonian)

        @qml.qnode(statevector_dev)
        def statevector_circuit():
            qml.Hadamard(0)
            qml.RX(-np.pi / 2.0, wires=1)
            qml.CNOT(wires=[0, 2])
            return qml.expval(hamiltonian)

        self.assertAlmostEqual(mps_circuit(), statevector_circuit(), places=8)

    def test_expval_z_and_zz_remain_correct_with_truncation_controls(self):
        dev = QMLMPSDevice(wires=2, max_bond_dim=2, svd_cutoff=1e-12)

        @qml.qnode(dev)
        def z0():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0))

        @qml.qnode(dev)
        def zz():
            qml.Hadamard(0)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        self.assertAlmostEqual(z0(), 0.0, places=8)
        self.assertAlmostEqual(zz(), 1.0, places=8)

    def test_small_circuit_matches_qml_starter_device(self):
        mps_dev = QMLMPSDevice(wires=2, max_bond_dim=2, svd_cutoff=1e-12)
        statevector_dev = QMLStarterDevice(wires=2)

        @qml.qnode(mps_dev)
        def mps_circuit():
            qml.RY(0.37, wires=0)
            qml.Hadamard(1)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        @qml.qnode(statevector_dev)
        def statevector_circuit():
            qml.RY(0.37, wires=0)
            qml.Hadamard(1)
            qml.CNOT(wires=[0, 1])
            return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))

        self.assertAlmostEqual(mps_circuit(), statevector_circuit(), places=8)

    def test_non_nearest_neighbor_cnot_matches_qml_starter_device(self):
        mps_dev = QMLMPSDevice(wires=3, max_bond_dim=4, svd_cutoff=1e-12)
        statevector_dev = QMLStarterDevice(wires=3)

        @qml.qnode(mps_dev)
        def mps_circuit():
            qml.CNOT(wires=[0, 2])
            return qml.state()

        @qml.qnode(statevector_dev)
        def statevector_circuit():
            qml.CNOT(wires=[0, 2])
            return qml.state()

        np.testing.assert_allclose(mps_circuit(), statevector_circuit(), atol=1e-8)


class TestPenQMPSPackagingMetadata(unittest.TestCase):
    def test_pyproject_declares_mps_plugin_entry_point(self):
        pyproject_path = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
        with pyproject_path.open("rb") as handle:
            metadata = tomllib.load(handle)

        entry_points = metadata["project"]["entry-points"]["pennylane.plugins"]
        self.assertEqual(entry_points["penq.mps_starter"], "QML.PenQ:QMLMPSDevice")


if __name__ == "__main__":
    unittest.main()
