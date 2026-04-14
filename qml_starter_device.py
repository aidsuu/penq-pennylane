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
    raise ImportError(
        "QMLStarterDevice requires PennyLane to be installed."
    ) from exc


class QMLStarterDevice(QubitDevice):
    name = "QML Starter Device"
    short_name = "penq.qml_starter"
    pennylane_requires = ">=0.0.0"
    version = "1.7.0"
    author = "Aidsuu"
    operations = {"PauliX", "PauliY", "PauliZ", "Hadamard", "RX", "RY", "RZ", "CNOT"}
    observables = {"Identity", "PauliX", "PauliY", "PauliZ", "Hadamard", "Prod"}
    _MAX_WIRES = 30

    @classmethod
    def capabilities(cls):
        return {
            "model": "qubit",
            "supports_tensor_observables": False,
        }

    def __init__(self, wires, shots=None, analytic=None):
        if isinstance(wires, int):
            num_wires = wires
        else:
            num_wires = len(wires)

        if not 1 <= num_wires <= self._MAX_WIRES:
            raise ValueError(f"QMLStarterDevice supports between 1 and {self._MAX_WIRES} wires.")

        if shots is not None and int(shots) < 1:
            raise ValueError("QMLStarterDevice shots must be None or a positive integer.")

        normalized_shots = None if shots in (None, 0) else int(shots)

        super().__init__(wires=wires, shots=normalized_shots)
        self._state = None
        self._pre_rotated_state = None
        self._force_analytic_probability = False
        self.reset()

    def reset(self):
        self._state = self._initialize_basis_state(0)
        self._pre_rotated_state = self._state

    @property
    def state(self):
        return self._pre_rotated_state.copy()

    def apply(self, operations, rotations=None, **kwargs):
        self._state = self._execute_single_circuit(operations)
        self._pre_rotated_state = self._state.copy()
        for rotation in rotations or []:
            self._apply_operation_to_state(self._state, rotation)

    def analytic_probability(self, wires=None):
        probabilities = np.abs(self._state) ** 2
        if wires is None:
            return probabilities
        return self.marginal_prob(probabilities, wires=wires)

    def probability(self, wires=None, shot_range=None, bin_size=None):
        if self._force_analytic_probability and shot_range is None and bin_size is None:
            return self.analytic_probability(wires=wires)
        return super().probability(wires=wires, shot_range=shot_range, bin_size=bin_size)

    def expval(self, observable, shot_range=None, bin_size=None):
        if self._is_linear_combination(observable):
            coefficients, terms = observable.terms()
            expectation = 0.0
            for coefficient, term in zip(coefficients, terms):
                expectation += float(coefficient) * self._expval_supported_observable(term)
            return float(np.real_if_close(expectation))

        return self._expval_supported_observable(observable)

    def _expval_supported_observable(self, observable):
        if self._observable_name(observable) == "Hadamard":
            if len(observable.wires) != 1:
                self._raise_unsupported_observable()
            wire = self._wire_index(observable.wires[0])
            state = self._pre_rotated_state
            ex = self._expval_pauli_product(state, ["PauliX"], [wire])
            ez = self._expval_pauli_product(state, ["PauliZ"], [wire])
            return float((ex + ez) / np.sqrt(2.0))

        pauli_word = getattr(observable, "_penq_pauli_word", None)
        if pauli_word is None:
            pauli_word = self._supported_pauli_word(observable)
            try:
                observable._penq_pauli_word = pauli_word
            except Exception:
                pass
        pauli_names, wire_indices = pauli_word
        return self._expval_pauli_product(self._pre_rotated_state, pauli_names, wire_indices)

    def batch_execute(self, circuits):
        return [self.execute(circuit) for circuit in circuits]

    def execute(self, circuit, **kwargs):
        measurements = list(getattr(circuit, "measurements", []))
        has_prob = any(self._measurement_kind(measurement) == "probability" for measurement in measurements)
        self._force_analytic_probability = has_prob and len(measurements) > 1
        try:
            return super().execute(circuit, **kwargs)
        finally:
            self._force_analytic_probability = False

    def _execute_single_circuit(self, operations):
        state = self._initialize_basis_state(0)
        for operation in operations:
            self._apply_operation_to_state(state, operation)
        return state

    def _initialize_basis_state(self, basis_index):
        dim = 2 ** self.num_wires
        if not 0 <= basis_index < dim:
            raise ValueError(f"Invalid basis state index {basis_index}; expected 0 <= index < {dim}.")
        state = np.zeros(dim, dtype=np.complex128)
        state[basis_index] = 1.0
        return state

    def _apply_operation_to_state(self, state, operation):
        name = operation.name
        if name == "CNOT":
            if len(operation.wires) != 2:
                raise DeviceError("Unsupported operation: CNOT requires exactly two wires.")
            control = self._wire_index(operation.wires[0])
            target = self._wire_index(operation.wires[1])
            self._apply_cnot_inplace(state, control, target)
            return

        if len(operation.wires) != 1:
            raise DeviceError(f"Unsupported operation: {name} requires exactly one wire.")
        wire = self._wire_index(operation.wires[0])
        matrix = self._single_qubit_matrix(operation)
        self._apply_single_qubit_gate_inplace(state, matrix, wire)

    def _wire_index(self, wire):
        mapped = self.map_wires(qml.wires.Wires([wire]))
        return int(mapped[0])

    def _single_qubit_matrix(self, operation):
        name = operation.name

        if name in {"PauliX", "PauliY", "PauliZ"}:
            return self._single_qubit_observable_matrix(name)
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

        # Allow internal basis-change rotations used by PennyLane measurement processing.
        matrix = np.asarray(qml.matrix(operation), dtype=np.complex128)
        if matrix.shape == (2, 2):
            return matrix

        raise DeviceError(
            f"Unsupported operation: {name}. Supported gates are PauliX, PauliY, PauliZ, Hadamard, RX, RY, RZ, and CNOT."
        )

    @staticmethod
    def _single_qubit_observable_matrix(name):
        if name == "PauliX":
            return np.array([[0, 1], [1, 0]], dtype=np.complex128)
        if name == "PauliY":
            return np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
        if name == "PauliZ":
            return np.array([[1, 0], [0, -1]], dtype=np.complex128)
        raise DeviceError(f"Unsupported observable: {name}.")

    def _apply_single_qubit_gate_inplace(self, state, matrix, wire):
        stride = 1 << (self.num_wires - wire - 1)
        block = stride << 1
        m00, m01 = matrix[0, 0], matrix[0, 1]
        m10, m11 = matrix[1, 0], matrix[1, 1]
        for base in range(0, state.size, block):
            for offset in range(stride):
                index0 = base + offset
                index1 = index0 + stride
                amplitude0 = state[index0]
                amplitude1 = state[index1]
                state[index0] = m00 * amplitude0 + m01 * amplitude1
                state[index1] = m10 * amplitude0 + m11 * amplitude1

    def _apply_cnot_inplace(self, state, control, target):
        control_mask = 1 << (self.num_wires - control - 1)
        target_mask = 1 << (self.num_wires - target - 1)
        if control_mask > target_mask:
            outer_mask = control_mask
            inner_mask = target_mask
            inner_offset = control_mask
        else:
            outer_mask = target_mask
            inner_mask = control_mask
            inner_offset = control_mask

        work = np.empty(inner_mask, dtype=np.complex128)
        for base in range(0, state.size, outer_mask << 1):
            for mid in range(0, outer_mask, inner_mask << 1):
                left_start = base + mid + inner_offset
                left_end = left_start + inner_mask
                right_start = left_start + target_mask
                right_end = right_start + inner_mask
                work[:] = state[left_start:left_end]
                state[left_start:left_end] = state[right_start:right_end]
                state[right_start:right_end] = work

    def _expval_pauli_product(self, state, pauli_names, wires):
        flip_mask = 0
        z_mask = 0
        y_mask = 0
        num_y = 0

        for pauli_name, wire in zip(pauli_names, wires):
            mask = 1 << (self.num_wires - wire - 1)
            if pauli_name == "PauliX":
                flip_mask |= mask
            elif pauli_name == "PauliY":
                flip_mask |= mask
                y_mask |= mask
                num_y += 1
            else:
                z_mask |= mask

        if flip_mask == 0:
            expectation = 0.0
            for basis_index, amplitude in enumerate(state):
                probability = amplitude.real * amplitude.real + amplitude.imag * amplitude.imag
                if (basis_index & z_mask).bit_count() & 1:
                    expectation -= probability
                else:
                    expectation += probability
            return float(expectation)

        expectation = 0.0j
        phase_mask = y_mask | z_mask
        pair_phase = -1.0 if ((flip_mask & phase_mask).bit_count() & 1) else 1.0
        base_phase = (1j) ** num_y

        for basis_index in range(state.size):
            mapped_index = basis_index ^ flip_mask
            if basis_index >= mapped_index:
                continue

            phase = -base_phase if ((basis_index & phase_mask).bit_count() & 1) else base_phase
            amplitude = state[basis_index]
            mapped_amplitude = state[mapped_index]
            expectation += phase * (
                np.conjugate(mapped_amplitude) * amplitude
                + pair_phase * np.conjugate(amplitude) * mapped_amplitude
            )

        return float(np.real_if_close(expectation))

    def _supported_pauli_word(self, observable):
        factors = self._observable_factors(observable)
        if not factors:
            self._raise_unsupported_observable()

        pauli_names = []
        wire_indices = []
        seen_wires = set()

        for factor in factors:
            factor_name = self._observable_name(factor)
            if factor_name == "Identity":
                continue
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
    def _raise_unsupported_observable():
        raise DeviceError(
            "Unsupported measurement: supported expectation values are qml.expval(qml.PauliX(wire)), "
            "qml.expval(qml.PauliY(wire)), qml.expval(qml.PauliZ(wire)), arbitrary Pauli-word tensor "
            "products of PauliX, PauliY, and PauliZ on distinct wires, and linear combinations of those observables."
        )

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

    @staticmethod
    def _is_linear_combination(observable):
        return callable(getattr(observable, "terms", None)) and getattr(observable, "name", None) in {
            "Hamiltonian",
            "LinearCombination",
            "Sum",
        }

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
            if "probability" in return_type_text or "probs" in return_type_text:
                return "probability"
            if "expectation" in return_type_text or "expval" in return_type_text:
                return "expectation"
            return return_type_text

        measurement_name = measurement.__class__.__name__.lower()
        if "state" in measurement_name:
            return "state"
        if "probability" in measurement_name or "probs" in measurement_name:
            return "probability"
        if "expectation" in measurement_name or "expval" in measurement_name:
            return "expectation"
        return measurement_name
