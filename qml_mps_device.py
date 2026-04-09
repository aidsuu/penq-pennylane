import numpy as np

try:
    import pennylane as qml
    try:
        from pennylane.devices import QubitDevice
    except ImportError:  # pragma: no cover - depends on PennyLane version
        from pennylane import QubitDevice
    try:
        from pennylane.exceptions import DeviceError
    except ImportError:  # pragma: no cover - depends on PennyLane version
        from pennylane.devices._legacy_device import DeviceError
except ImportError as exc:  # pragma: no cover - exercised only when PennyLane is missing
    raise ImportError("QMLMPSDevice requires PennyLane to be installed.") from exc


class QMLMPSDevice(QubitDevice):
    name = "QML MPS Starter Device"
    short_name = "penq.mps_starter"
    pennylane_requires = ">=0.0.0"
    version = "6.0.0"
    author = "Aidsuu"
    operations = {"PauliX", "PauliY", "PauliZ", "Hadamard", "RX", "RY", "RZ", "CNOT"}
    observables = {"PauliX", "PauliY", "PauliZ"}
    _MAX_WIRES = 30

    def __init__(self, wires, shots=None, analytic=None, max_bond_dim=None, svd_cutoff=0.0):
        if isinstance(wires, int):
            num_wires = wires
        else:
            num_wires = len(wires)

        if not 1 <= num_wires <= self._MAX_WIRES:
            raise ValueError(f"QMLMPSDevice supports between 1 and {self._MAX_WIRES} wires.")

        if shots not in (None, 0):
            raise ValueError(
                "QMLMPSDevice supports analytic execution only; shots must be None or 0."
            )
        if max_bond_dim is not None and int(max_bond_dim) < 1:
            raise ValueError("QMLMPSDevice max_bond_dim must be None or a positive integer.")
        if float(svd_cutoff) < 0.0:
            raise ValueError("QMLMPSDevice svd_cutoff must be non-negative.")

        super().__init__(wires=wires, shots=None)
        self.max_bond_dim = None if max_bond_dim is None else int(max_bond_dim)
        self.svd_cutoff = float(svd_cutoff)
        self._mps = None
        self.reset()

    def reset(self):
        self._mps = self._initialize_zero_mps()

    @property
    def state(self):
        return self._mps_to_statevector().copy()

    def apply(self, operations, rotations=None, **kwargs):
        self._mps = self._execute_single_circuit(operations)

    def analytic_probability(self, wires=None):
        probabilities = np.abs(self.state) ** 2
        if wires is None:
            return probabilities
        return self.marginal_prob(probabilities, wires=wires)

    def batch_execute(self, circuits):
        return [self.execute(circuit) for circuit in circuits]

    def execute(self, circuit, **kwargs):
        operations = list(getattr(circuit, "operations", []))
        measurements = list(getattr(circuit, "measurements", []))

        if not measurements:
            raise DeviceError("Unsupported measurement: at least one measurement per circuit is required.")

        self._mps = self._execute_single_circuit(operations)
        results = [self._evaluate_measurement(measurement) for measurement in measurements]
        if len(results) == 1:
            return results[0]
        return tuple(results)

    def _evaluate_measurement(self, measurement):
        measurement_kind = self._measurement_kind(measurement)
        if measurement_kind == "state":
            return self.state
        if measurement_kind == "expectation":
            return self.expval(measurement.obs)
        raise DeviceError(
            "Unsupported measurement: only qml.state(), qml.expval(qml.PauliX(wire)), "
            "qml.expval(qml.PauliY(wire)), qml.expval(qml.PauliZ(wire)), arbitrary Pauli-word tensor "
            "products of PauliX, PauliY, and PauliZ on distinct wires, plus linear combinations of those "
            "observables, are supported."
        )

    def expval(self, observable, shot_range=None, bin_size=None):
        if self._is_linear_combination(observable):
            coefficients, terms = observable.terms()
            expectation = 0.0
            for coefficient, term in zip(coefficients, terms):
                expectation += float(coefficient) * self._expval_supported_observable(term)
            return float(np.real_if_close(expectation))
        return self._expval_supported_observable(observable)

    def _initialize_zero_mps(self):
        zero_tensor = np.zeros((1, 2, 1), dtype=np.complex128)
        zero_tensor[0, 0, 0] = 1.0
        return [zero_tensor.copy() for _ in range(self.num_wires)]

    def _execute_single_circuit(self, operations):
        mps = self._initialize_zero_mps()
        for operation in operations:
            self._apply_operation_to_mps(mps, operation)
        return mps

    def _apply_operation_to_mps(self, mps, operation):
        name = operation.name
        if name == "CNOT":
            if len(operation.wires) != 2:
                raise DeviceError("Unsupported operation: CNOT requires exactly two wires.")
            control = self._wire_index(operation.wires[0])
            target = self._wire_index(operation.wires[1])
            if control == target:
                raise DeviceError("Unsupported operation: CNOT requires two distinct wires.")
            self._apply_cnot_with_routing(mps, control, target)
            return

        if len(operation.wires) != 1:
            raise DeviceError(f"Unsupported operation: {name} requires exactly one wire.")
        matrix = self._single_qubit_matrix(operation)
        wire = self._wire_index(operation.wires[0])
        self._apply_single_qubit_gate(mps, matrix, wire)

    def _apply_single_qubit_gate(self, mps, matrix, wire):
        tensor = mps[wire]
        updated = np.tensordot(matrix, tensor, axes=([1], [1]))
        mps[wire] = np.transpose(updated, (1, 0, 2))

    def _apply_two_qubit_gate(self, mps, gate_matrix, left_wire):
        left_tensor = mps[left_wire]
        right_tensor = mps[left_wire + 1]

        pair = np.tensordot(left_tensor, right_tensor, axes=([2], [0]))
        pair = np.transpose(pair, (0, 1, 2, 3))
        left_bond, _, _, right_bond = pair.shape

        pair = pair.reshape(left_bond, 4, right_bond)
        updated = np.tensordot(gate_matrix, pair, axes=([1], [1]))
        updated = np.transpose(updated, (1, 0, 2)).reshape(left_bond, 2, 2, right_bond)

        matrix = updated.reshape(left_bond * 2, 2 * right_bond)
        u_matrix, singular_values, vh_matrix = np.linalg.svd(matrix, full_matrices=False)
        bond_dim = self._truncated_bond_dim(singular_values)
        u_matrix = u_matrix[:, :bond_dim]
        singular_values = singular_values[:bond_dim]
        vh_matrix = vh_matrix[:bond_dim, :]

        mps[left_wire] = u_matrix.reshape(left_bond, 2, bond_dim)
        mps[left_wire + 1] = (singular_values[:, None] * vh_matrix).reshape(bond_dim, 2, right_bond)

    def _apply_cnot_with_routing(self, mps, control, target):
        if control < target:
            routed_target = target
            while routed_target > control + 1:
                self._apply_two_qubit_gate(mps, self._swap_matrix(), routed_target - 1)
                routed_target -= 1
            self._apply_two_qubit_gate(mps, self._cnot_matrix(), control)
            while routed_target < target:
                self._apply_two_qubit_gate(mps, self._swap_matrix(), routed_target)
                routed_target += 1
            return

        routed_control = control
        while routed_control > target + 1:
            self._apply_two_qubit_gate(mps, self._swap_matrix(), routed_control - 1)
            routed_control -= 1
        self._apply_two_qubit_gate(mps, self._reverse_cnot_matrix(), target)
        while routed_control < control:
            self._apply_two_qubit_gate(mps, self._swap_matrix(), routed_control)
            routed_control += 1

    def _truncated_bond_dim(self, singular_values):
        if singular_values.size == 0:
            return 1

        keep = singular_values.size
        if self.svd_cutoff > 0.0:
            keep = int(np.count_nonzero(singular_values > self.svd_cutoff))
            keep = max(1, keep)
        if self.max_bond_dim is not None:
            keep = min(keep, self.max_bond_dim)
        return max(1, keep)

    def _mps_to_statevector(self):
        tensor = self._mps[0]
        for next_tensor in self._mps[1:]:
            tensor = np.tensordot(tensor, next_tensor, axes=([-1], [0]))
        return tensor.reshape(2 ** self.num_wires).astype(np.complex128, copy=False)

    def _expval_supported_observable(self, observable):
        pauli_word = getattr(observable, "_penq_pauli_word", None)
        if pauli_word is None:
            pauli_word = self._supported_pauli_word(observable)
            try:
                observable._penq_pauli_word = pauli_word
            except Exception:
                pass
        pauli_names, wires = pauli_word
        return self._expval_pauli_word(pauli_names, wires)

    def _expval_pauli_word(self, pauli_names, wires):
        wire_to_name = {wire: pauli_name for pauli_name, wire in zip(pauli_names, wires)}
        env = np.ones((1, 1), dtype=np.complex128)
        for wire, tensor in enumerate(self._mps):
            matrix = self._single_qubit_observable_matrix(wire_to_name.get(wire, "Identity"))
            env = np.einsum("lL,lsr,st,LtR->rR", env, np.conjugate(tensor), matrix, tensor)
        value = np.real_if_close(env[0, 0]).item()
        return float(value)

    def _wire_index(self, wire):
        mapped = self.map_wires(qml.wires.Wires([wire]))
        return int(mapped[0])

    @staticmethod
    def _single_qubit_matrix(operation):
        name = operation.name
        if name == "PauliX":
            return np.array([[0, 1], [1, 0]], dtype=np.complex128)
        if name == "PauliY":
            return np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
        if name == "PauliZ":
            return np.array([[1, 0], [0, -1]], dtype=np.complex128)
        if name == "Hadamard":
            return np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)
        if name == "RX":
            theta = float(operation.parameters[0])
            return np.array(
                [
                    [np.cos(theta / 2), -1j * np.sin(theta / 2)],
                    [-1j * np.sin(theta / 2), np.cos(theta / 2)],
                ],
                dtype=np.complex128,
            )
        if name == "RY":
            theta = float(operation.parameters[0])
            return np.array(
                [
                    [np.cos(theta / 2), -np.sin(theta / 2)],
                    [np.sin(theta / 2), np.cos(theta / 2)],
                ],
                dtype=np.complex128,
            )
        if name == "RZ":
            theta = float(operation.parameters[0])
            return np.array(
                [
                    [np.exp(-0.5j * theta), 0],
                    [0, np.exp(0.5j * theta)],
                ],
                dtype=np.complex128,
            )
        raise DeviceError(
            f"Unsupported operation: {name}. Supported gates are PauliX, PauliY, PauliZ, Hadamard, RX, RY, RZ, and CNOT."
        )

    @staticmethod
    def _cnot_matrix():
        return np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
            ],
            dtype=np.complex128,
        )

    @staticmethod
    def _reverse_cnot_matrix():
        return np.array(
            [
                [1, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
            ],
            dtype=np.complex128,
        )

    @staticmethod
    def _swap_matrix():
        return np.array(
            [
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
            ],
            dtype=np.complex128,
        )

    @staticmethod
    def _single_qubit_observable_matrix(name):
        if name == "Identity":
            return np.eye(2, dtype=np.complex128)
        if name == "PauliX":
            return np.array([[0, 1], [1, 0]], dtype=np.complex128)
        if name == "PauliY":
            return np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
        if name == "PauliZ":
            return np.array([[1, 0], [0, -1]], dtype=np.complex128)
        raise DeviceError(f"Unsupported observable: {name}.")

    @staticmethod
    def _observable_name(observable):
        name = getattr(observable, "name", None)
        if isinstance(name, (list, tuple)):
            return "@".join(str(item) for item in name)
        return str(name)

    @staticmethod
    def _observable_factors(observable):
        if hasattr(observable, "operands"):
            return observable.operands
        if hasattr(observable, "obs"):
            obs = observable.obs
            if isinstance(obs, (list, tuple)):
                return obs
        return (observable,)

    def _supported_pauli_word(self, observable):
        factors = self._observable_factors(observable)
        if not factors:
            self._raise_unsupported_observable()

        pauli_names = []
        wire_indices = []
        seen_wires = set()

        for factor in factors:
            factor_name = self._observable_name(factor)
            if factor_name not in {"PauliX", "PauliY", "PauliZ"} or len(factor.wires) != 1:
                self._raise_unsupported_observable()

            wire = self._wire_index(factor.wires[0])
            if wire in seen_wires:
                self._raise_unsupported_observable()

            seen_wires.add(wire)
            pauli_names.append(factor_name)
            wire_indices.append(wire)

        return pauli_names, wire_indices

    @staticmethod
    def _is_linear_combination(observable):
        return callable(getattr(observable, "terms", None)) and getattr(observable, "name", None) in {
            "Hamiltonian",
            "LinearCombination",
            "Sum",
        }

    @staticmethod
    def _raise_unsupported_observable():
        raise DeviceError(
            "Unsupported measurement: supported expectation values are qml.expval(qml.PauliX(wire)), "
            "qml.expval(qml.PauliY(wire)), qml.expval(qml.PauliZ(wire)), arbitrary Pauli-word tensor "
            "products of PauliX, PauliY, and PauliZ on distinct wires, and linear combinations of those observables."
        )

    @staticmethod
    def _measurement_kind(measurement):
        return_type = getattr(measurement, "return_type", None)
        if return_type is not None:
            if return_type is getattr(qml.measurements, "State", None):
                return "state"
            if return_type is getattr(qml.measurements, "Expectation", None):
                return "expectation"
            return_type_text = str(return_type).lower()
            if "state" in return_type_text:
                return "state"
            if "expectation" in return_type_text or "expval" in return_type_text:
                return "expectation"
            return return_type_text

        measurement_name = measurement.__class__.__name__.lower()
        if "state" in measurement_name:
            return "state"
        if "expectation" in measurement_name or "expval" in measurement_name:
            return "expectation"
        return measurement_name
