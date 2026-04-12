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


if __name__ == "__main__":
    unittest.main()
