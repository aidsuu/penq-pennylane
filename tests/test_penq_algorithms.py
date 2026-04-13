import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ.penq_algorithms import adaptive_tfim_vqe
from QML.PenQ.penq_algorithms import compare_tfim_vqe_exact_vs_mps


class TestAdaptiveTFIMVQE(unittest.TestCase):
    def test_result_has_expected_fields(self):
        result = adaptive_tfim_vqe(
            n=6,
            J=1.0,
            h=0.5,
            backend="qml",
            max_layers=3,
            steps=2,
            grid_points=5,
        )
        self.assertEqual(
            set(result),
            {
                "n",
                "J",
                "h",
                "backend",
                "energy",
                "energy_per_site",
                "best_params",
                "layers_used",
                "converged",
                "final_delta_energy",
                "max_bond_dim",
                "svd_cutoff",
                "expval_x0",
                "expval_z0z1",
                "history",
                "seed",
            },
        )
        self.assertEqual(result["n"], 6)
        self.assertEqual(result["backend"], "qml")
        self.assertIsInstance(result["best_params"], list)
        self.assertGreaterEqual(result["layers_used"], 0)

    def test_energy_history_is_nonincreasing(self):
        result = adaptive_tfim_vqe(
            n=6,
            J=1.0,
            h=0.5,
            backend="qml",
            max_layers=4,
            steps=2,
            grid_points=5,
        )
        energies = [row["energy"] for row in result["history"]]
        self.assertEqual(energies, sorted(energies, reverse=True))

    def test_exact_vs_mps_agree_on_small_case(self):
        comparison = compare_tfim_vqe_exact_vs_mps(
            n=6,
            J=1.0,
            h=0.5,
            max_layers=3,
            max_bond_dim=4,
            svd_cutoff=1e-12,
            steps=2,
            grid_points=5,
        )
        self.assertLessEqual(comparison["abs_energy_error"], 1e-8)
        self.assertLessEqual(comparison["abs_energy_error_per_site"], 1e-8)

    def test_module_docstring_contains_required_formulas(self):
        module_doc = adaptive_tfim_vqe.__module__
        self.assertEqual(module_doc, "QML.PenQ.penq_algorithms")
        import QML.PenQ.penq_algorithms as penq_algorithms  # local import for docstring check

        text = penq_algorithms.__doc__
        self.assertIsNotNone(text)
        self.assertIn("H = -J sum_i Z_i Z_{i+1} - h sum_i X_i", text)
        self.assertIn("E(theta) = <psi(theta)|H|psi(theta)>", text)
        self.assertIn("U_l(gamma_l, beta_l) = U_X(beta_l) U_ZZ(gamma_l)", text)
        self.assertIn("|psi_L> = prod_l U_l |+>^n", text)
        self.assertIn("Delta_L = E_{L-1}^* - E_L^*", text)
        self.assertIn("Delta_L <= tol or L == max_layers", text)
        self.assertIn("CNOT - RZ(2 gamma) - CNOT = exp(-i gamma Z⊗Z)", text)


class TestImaginaryTimeTFIM(unittest.TestCase):
    def test_result_has_expected_fields(self):
        from QML.PenQ.penq_algorithms import imaginary_time_tfim
        result = imaginary_time_tfim(
            n=4,
            J=1.0,
            h=0.5,
            backend="qml",
            delta_tau=0.01,
            steps=2,
            max_layers=2,
        )
        self.assertEqual(
            set(result),
            {
                "n",
                "J",
                "h",
                "backend",
                "delta_tau",
                "steps",
                "energy",
                "energy_per_site",
                "best_params",
                "converged",
                "final_delta_energy",
                "max_bond_dim",
                "svd_cutoff",
                "expval_x0",
                "expval_z0z1",
                "energy_history",
                "history",
                "seed",
            },
        )
        self.assertEqual(result["n"], 4)
        self.assertEqual(result["backend"], "qml")
        self.assertIsInstance(result["best_params"], list)
        self.assertGreaterEqual(len(result["best_params"]), 2)
        self.assertIsInstance(result["energy_history"], list)

    def test_energy_history_is_nonincreasing(self):
        from QML.PenQ.penq_algorithms import imaginary_time_tfim
        result = imaginary_time_tfim(
            n=4,
            J=1.0,
            h=0.5,
            backend="qml",
            delta_tau=0.05,
            steps=3,
            max_layers=2,
        )
        energies = result["energy_history"]
        self.assertEqual(energies, sorted(energies, reverse=True))

    def test_exact_vs_mps_agree_on_small_case(self):
        from QML.PenQ.penq_algorithms import compare_imag_time_exact_vs_mps
        comparison = compare_imag_time_exact_vs_mps(
            n=4,
            J=1.0,
            h=0.5,
            delta_tau=0.05,
            steps=3,
            max_layers=2,
            max_bond_dim=4,
            svd_cutoff=1e-12,
        )
        self.assertLessEqual(comparison["abs_energy_error"], 1e-8)
        self.assertLessEqual(comparison["abs_energy_error_per_site"], 1e-8)

    def test_module_docstring_contains_vite_formulas(self):
        from QML.PenQ import penq_algorithms
        text = penq_algorithms.imaginary_time_tfim.__doc__
        self.assertIsNotNone(text)
        self.assertIn("|psi(tau)> = exp(-tau H)|psi0> / ||exp(-tau H)|psi0>||", text)
        self.assertIn("theta_{k+1} = theta_k - delta_tau * grad_E(theta_k)", text)


class TestRealTimeTFIM(unittest.TestCase):
    def test_result_has_expected_fields(self):
        from QML.PenQ.penq_algorithms import real_time_tfim

        result = real_time_tfim(
            n=4,
            J=1.0,
            h=0.5,
            backend="qml",
            dt=0.02,
            steps=3,
        )
        self.assertEqual(
            set(result),
            {
                "n",
                "J",
                "h",
                "backend",
                "dt",
                "steps",
                "energy",
                "energy_per_site",
                "max_bond_dim",
                "svd_cutoff",
                "expval_x0",
                "expval_z0z1",
                "energy_history",
                "expval_x0_history",
                "expval_z0z1_history",
                "time_history",
                "history",
            },
        )
        self.assertEqual(result["backend"], "qml")
        self.assertEqual(len(result["energy_history"]), 4)
        self.assertEqual(len(result["expval_x0_history"]), 4)
        self.assertEqual(len(result["expval_z0z1_history"]), 4)
        self.assertEqual(len(result["time_history"]), 4)

    def test_time_history_is_monotonic(self):
        from QML.PenQ.penq_algorithms import real_time_tfim

        result = real_time_tfim(
            n=4,
            J=1.0,
            h=0.5,
            backend="qml",
            dt=0.05,
            steps=5,
        )
        times = result["time_history"]
        self.assertEqual(times, sorted(times))
        for value in result["expval_x0_history"]:
            self.assertLessEqual(value, 1.0)
            self.assertGreaterEqual(value, -1.0)
        for value in result["expval_z0z1_history"]:
            self.assertLessEqual(value, 1.0)
            self.assertGreaterEqual(value, -1.0)

    def test_exact_vs_mps_agree_on_small_case(self):
        from QML.PenQ.penq_algorithms import compare_real_time_exact_vs_mps

        comparison = compare_real_time_exact_vs_mps(
            n=4,
            J=1.0,
            h=0.5,
            dt=0.05,
            steps=6,
            max_bond_dim=4,
            svd_cutoff=1e-12,
        )
        self.assertLessEqual(comparison["abs_energy_error"], 1e-8)
        self.assertLessEqual(comparison["abs_energy_error_per_site"], 1e-8)
        self.assertLessEqual(comparison["max_abs_energy_error_over_time"], 1e-8)


class TestSquareGeometryAndTFIM(unittest.TestCase):
    def test_square_geometry_helpers(self):
        from QML.PenQ import square_horizontal_pairs
        from QML.PenQ import square_site_count
        from QML.PenQ import square_site_index
        from QML.PenQ import square_vertical_pairs

        self.assertEqual(square_site_count(3, 2), 6)
        self.assertEqual(square_site_index(3, 0, 0), 0)
        self.assertEqual(square_site_index(3, 2, 1), 5)
        self.assertEqual(square_horizontal_pairs(3, 2), [(0, 1), (1, 2), (3, 4), (4, 5)])
        self.assertEqual(square_vertical_pairs(3, 2), [(0, 3), (1, 4), (2, 5)])

    def test_square_tfim_observables_result_shape(self):
        from QML.PenQ.penq_algorithms import square_tfim_observables

        result = square_tfim_observables(
            Lx=2,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.5,
            backend="qml",
            seed=0,
        )
        self.assertEqual(
            set(result),
            {
                "Lx",
                "Ly",
                "n_sites",
                "Jx",
                "Jy",
                "h",
                "backend",
                "energy",
                "energy_per_site",
                "magnetization_x",
                "magnetization_z",
                "nn_zz_horizontal",
                "nn_zz_vertical",
                "max_bond_dim",
                "svd_cutoff",
            },
        )
        self.assertEqual(result["n_sites"], 4)

    def test_square_exact_vs_mps_small_case(self):
        from QML.PenQ.penq_algorithms import compare_square_tfim_exact_vs_mps

        comparison_2x2 = compare_square_tfim_exact_vs_mps(
            Lx=2,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.6,
            max_bond_dim=8,
            svd_cutoff=1e-12,
            seed=1,
        )
        self.assertLessEqual(comparison_2x2["abs_energy_error"], 1e-8)
        self.assertLessEqual(comparison_2x2["abs_energy_error_per_site"], 1e-8)

        comparison_3x2 = compare_square_tfim_exact_vs_mps(
            Lx=3,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.6,
            max_bond_dim=16,
            svd_cutoff=1e-12,
            seed=1,
        )
        self.assertLessEqual(comparison_3x2["abs_energy_error_per_site"], 1e-6)


class TestSquareTFIMDynamics(unittest.TestCase):
    def test_square_real_time_result_shape(self):
        from QML.PenQ.penq_algorithms import square_tfim_real_time

        result = square_tfim_real_time(
            Lx=2,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.6,
            backend="qml",
            dt=0.05,
            steps=4,
            seed=2,
        )
        self.assertEqual(
            set(result),
            {
                "Lx",
                "Ly",
                "n_sites",
                "Jx",
                "Jy",
                "h",
                "backend",
                "dt",
                "steps",
                "time_history",
                "energy_history",
                "magnetization_x_history",
                "magnetization_z_history",
                "nn_zz_horizontal_history",
                "nn_zz_vertical_history",
                "max_bond_dim",
                "svd_cutoff",
                "seed",
            },
        )
        self.assertEqual(len(result["time_history"]), 5)
        self.assertEqual(len(result["energy_history"]), 5)

    def test_square_imag_time_result_shape(self):
        from QML.PenQ.penq_algorithms import square_tfim_imag_time

        result = square_tfim_imag_time(
            Lx=2,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.6,
            backend="qml",
            delta_tau=0.05,
            steps=4,
            max_layers=2,
            seed=2,
        )
        self.assertEqual(
            set(result),
            {
                "Lx",
                "Ly",
                "n_sites",
                "Jx",
                "Jy",
                "h",
                "backend",
                "delta_tau",
                "steps",
                "energy_history",
                "magnetization_x_history",
                "magnetization_z_history",
                "nn_zz_horizontal_history",
                "nn_zz_vertical_history",
                "converged",
                "final_delta_energy",
                "max_bond_dim",
                "svd_cutoff",
                "seed",
            },
        )
        self.assertGreaterEqual(len(result["energy_history"]), 2)

    def test_square_real_imag_histories_are_finite_and_stable(self):
        from QML.PenQ.penq_algorithms import square_tfim_imag_time
        from QML.PenQ.penq_algorithms import square_tfim_real_time

        real_result = square_tfim_real_time(
            Lx=2,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.6,
            backend="qml",
            dt=0.05,
            steps=6,
            seed=2,
        )
        self.assertEqual(real_result["time_history"], sorted(real_result["time_history"]))
        for value in real_result["energy_history"]:
            self.assertTrue(abs(value) < 1e6)

        imag_result = square_tfim_imag_time(
            Lx=2,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.6,
            backend="qml",
            delta_tau=0.05,
            steps=6,
            max_layers=3,
            seed=2,
        )
        for value in imag_result["energy_history"]:
            self.assertTrue(abs(value) < 1e6)

    def test_square_real_and_imag_exact_vs_mps_small_case(self):
        from QML.PenQ.penq_algorithms import compare_square_tfim_imag_time_exact_vs_mps
        from QML.PenQ.penq_algorithms import compare_square_tfim_real_time_exact_vs_mps

        real_comp = compare_square_tfim_real_time_exact_vs_mps(
            Lx=2,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.6,
            dt=0.05,
            steps=6,
            max_bond_dim=8,
            svd_cutoff=1e-12,
            seed=3,
        )
        self.assertLessEqual(real_comp["abs_energy_error_per_site"], 1e-8)

        imag_comp = compare_square_tfim_imag_time_exact_vs_mps(
            Lx=2,
            Ly=2,
            Jx=1.0,
            Jy=0.8,
            h=0.6,
            delta_tau=0.05,
            steps=6,
            max_layers=3,
            max_bond_dim=8,
            svd_cutoff=1e-12,
            seed=3,
        )
        self.assertLessEqual(imag_comp["abs_energy_error_per_site"], 1e-8)


if __name__ == "__main__":
    unittest.main()
