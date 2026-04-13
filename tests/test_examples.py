import pathlib
import sys
import tempfile
import unittest
from importlib.util import find_spec

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

matplotlib = None if find_spec("matplotlib") is None else True

try:
    from QML.PenQ.examples.hamiltonian_scan import analytic_basis_energy, scan_basis_energies
    from QML.PenQ.examples.ising_chain_scan import analytic_chain_energy, evaluate_chain_scan
    from QML.PenQ.examples.internal_profile import profile_rows
    from QML.PenQ.examples.mini_vqe import analytic_minimum, grid_search
    from QML.PenQ.examples.performance_scan import performance_rows
    from QML.PenQ.examples.qaoa_campaign_summary import build_qaoa_campaign_summary
    from QML.PenQ.examples.qaoa_campaign_summary import write_qaoa_campaign_summary_csv
    from QML.PenQ.examples.qaoa_chain_landscape import qaoa_chain_landscape
    from QML.PenQ.examples.qaoa_chain_landscape import write_qaoa_landscape_csv
    from QML.PenQ.examples.qaoa_ising_small import exact_classical_minimum, qaoa_grid_search
    from QML.PenQ.examples.qaoa_research_campaign import qaoa_campaign_output_paths
    from QML.PenQ.examples.qaoa_research_campaign import run_qaoa_research_campaign
    from QML.PenQ.examples.statevector_size_table import statevector_size_rows
    from QML.PenQ.examples.tfim_scan import analytic_tfim_energy, evaluate_tfim_scan
    from QML.PenQ.examples.tfim_finite_size_summary import finite_size_summary_rows
    from QML.PenQ.examples.tfim_finite_size_summary import write_finite_size_summary_csv
    from QML.PenQ.examples.tfim_groundstate_ansatz import variational_study_rows
    from QML.PenQ.examples.tfim_groundstate_ansatz import write_tfim_groundstate_csv
    from QML.PenQ.examples.research_report import build_research_report
    from QML.PenQ.examples.research_report import report_rows
    from QML.PenQ.examples.research_report import write_research_report_csv
    from QML.PenQ.examples.tfim_campaign_summary import build_campaign_summary
    from QML.PenQ.examples.tfim_campaign_summary import write_campaign_summary_csv
    from QML.PenQ.examples.tfim_research_campaign import campaign_output_paths
    from QML.PenQ.examples.tfim_research_campaign import run_tfim_research_campaign
    from QML.PenQ.examples.tfim_grid_resolution_study import grid_resolution_rows
    from QML.PenQ.examples.tfim_grid_resolution_study import write_tfim_grid_resolution_csv
    from QML.PenQ.examples.tfim_ansatz_depth_study import ansatz_depth_rows
    from QML.PenQ.examples.tfim_ansatz_depth_study import write_tfim_ansatz_depth_csv
    from QML.PenQ.examples.tfim_ansatz_comparison import ansatz_comparison_rows
    from QML.PenQ.examples.tfim_ansatz_comparison import write_tfim_ansatz_comparison_csv
    from QML.PenQ.examples.tfim_ansatz_cost_quality import cost_quality_rows
    from QML.PenQ.examples.tfim_ansatz_cost_quality import write_tfim_ansatz_cost_quality_csv
    from QML.PenQ.examples.tfim_large_scale_campaign import large_scale_campaign_rows
    from QML.PenQ.examples.tfim_large_scale_campaign import write_tfim_large_scale_csv
    from QML.PenQ.examples.tfim_exact_large_campaign import tfim_exact_large_rows
    from QML.PenQ.examples.tfim_exact_large_campaign import write_tfim_exact_large_csv
    from QML.PenQ.examples.tfim_mps_large_campaign import tfim_mps_large_rows
    from QML.PenQ.examples.tfim_mps_large_campaign import write_tfim_mps_large_csv
    from QML.PenQ.examples.tfim_exact_vs_mps_large_report import build_tfim_exact_vs_mps_large_report
    from QML.PenQ.examples.tfim_exact_vs_mps_large_report import write_tfim_exact_vs_mps_large_report_csv
    from QML.PenQ.examples.tfim_mps_sensitivity_report import build_tfim_mps_sensitivity_report
    from QML.PenQ.examples.tfim_mps_sensitivity_report import write_tfim_mps_sensitivity_csv
    from QML.PenQ.examples.tfim_mps_threshold_report import build_tfim_mps_threshold_report
    from QML.PenQ.examples.tfim_mps_threshold_report import write_tfim_mps_threshold_csv
    from QML.PenQ.examples.mps_general_pauli_demo import general_pauli_demo_rows
    from QML.PenQ.examples.mps_paulirot_demo import paulirot_demo_rows
    from QML.PenQ.examples.mps_isingzz_quench import mps_isingzz_quench_rows
    from QML.PenQ.examples.mps_isingzz_quench import write_mps_isingzz_quench_csv
    from QML.PenQ.examples.adaptive_tfim_vqe_demo import demo_rows as adaptive_tfim_demo_rows
    from QML.PenQ.examples.adaptive_tfim_vqe_scan import adaptive_tfim_vqe_scan_rows
    from QML.PenQ.examples.adaptive_tfim_vqe_scan import write_adaptive_tfim_vqe_scan_csv
    from QML.PenQ.examples.adaptive_tfim_vqe_report import generate_adaptive_tfim_report
    from QML.PenQ.examples.adaptive_tfim_vqe_report import write_adaptive_tfim_report_csv
    from QML.PenQ.examples.imaginary_time_tfim_scan import imaginary_time_tfim_scan_rows
    from QML.PenQ.examples.real_time_tfim_scan import real_time_tfim_scan_rows
    from QML.PenQ.examples.tfim_dynamics_utils import write_tfim_dynamics_scan_csv
    from QML.PenQ.examples.mps_tebd_tfim_quench import mps_tebd_tfim_rows
    from QML.PenQ.examples.mps_tebd_tfim_quench import write_mps_tebd_tfim_csv
    from QML.PenQ.examples.mps_trotter_order_study import mps_trotter_order_rows
    from QML.PenQ.examples.mps_trotter_order_study import write_mps_trotter_order_csv
    from QML.PenQ.examples.mps_vs_statevector_tfim_quench import tfim_quench_comparison_rows
    from QML.PenQ.examples.mps_vs_statevector_tfim_quench import write_tfim_quench_comparison_csv
    from QML.PenQ.examples.tfim_quench_error_map import tfim_quench_error_map_rows
    from QML.PenQ.examples.tfim_quench_error_map import write_tfim_quench_error_map_csv
    from QML.PenQ.examples.tfim_quench_threshold_report import build_tfim_quench_threshold_report
    from QML.PenQ.examples.tfim_quench_threshold_report import write_tfim_quench_threshold_csv
    from QML.PenQ.examples.mps_vs_statevector_tfim import comparison_rows as mps_vs_statevector_rows
    from QML.PenQ.examples.mps_vs_statevector_tfim import write_mps_vs_statevector_csv
    from QML.PenQ.examples.tfim_mps_truncation_scan import tfim_mps_truncation_rows
    from QML.PenQ.examples.tfim_mps_truncation_scan import write_tfim_mps_truncation_csv
    from QML.PenQ.examples.mps_depth_bond_study import depth_bond_rows
    from QML.PenQ.examples.mps_depth_bond_study import write_mps_depth_bond_csv
    from QML.PenQ.examples.qaoa_mps_truncation_scan import qaoa_mps_truncation_rows
    from QML.PenQ.examples.qaoa_mps_truncation_scan import write_qaoa_mps_truncation_csv
    from QML.PenQ.examples.tfim_scaling_scan import scaling_scan_rows
    from QML.PenQ.examples.tfim_scaling_scan import write_tfim_scaling_csv
    from QML.PenQ.examples.tfim_variational_scaling import comparative_variational_rows
    from QML.PenQ.examples.tfim_variational_scaling import write_tfim_variational_scaling_csv
    from QML.PenQ.examples.two_qubit_spin_scan import evaluate_spin_scan
except ImportError:  # pragma: no cover - dependency is external to this repo
    analytic_basis_energy = None
    scan_basis_energies = None
    analytic_chain_energy = None
    evaluate_chain_scan = None
    profile_rows = None
    analytic_minimum = None
    grid_search = None
    performance_rows = None
    build_qaoa_campaign_summary = None
    write_qaoa_campaign_summary_csv = None
    qaoa_chain_landscape = None
    write_qaoa_landscape_csv = None
    exact_classical_minimum = None
    qaoa_grid_search = None
    qaoa_campaign_output_paths = None
    run_qaoa_research_campaign = None
    statevector_size_rows = None
    analytic_tfim_energy = None
    evaluate_tfim_scan = None
    finite_size_summary_rows = None
    write_finite_size_summary_csv = None
    variational_study_rows = None
    write_tfim_groundstate_csv = None
    build_research_report = None
    report_rows = None
    write_research_report_csv = None
    build_campaign_summary = None
    write_campaign_summary_csv = None
    campaign_output_paths = None
    run_tfim_research_campaign = None
    grid_resolution_rows = None
    write_tfim_grid_resolution_csv = None
    ansatz_depth_rows = None
    write_tfim_ansatz_depth_csv = None
    ansatz_comparison_rows = None
    write_tfim_ansatz_comparison_csv = None
    cost_quality_rows = None
    write_tfim_ansatz_cost_quality_csv = None
    large_scale_campaign_rows = None
    write_tfim_large_scale_csv = None
    tfim_exact_large_rows = None
    write_tfim_exact_large_csv = None
    tfim_mps_large_rows = None
    write_tfim_mps_large_csv = None
    build_tfim_exact_vs_mps_large_report = None
    write_tfim_exact_vs_mps_large_report_csv = None
    build_tfim_mps_sensitivity_report = None
    write_tfim_mps_sensitivity_csv = None
    build_tfim_mps_threshold_report = None
    write_tfim_mps_threshold_csv = None
    general_pauli_demo_rows = None
    paulirot_demo_rows = None
    mps_isingzz_quench_rows = None
    write_mps_isingzz_quench_csv = None
    adaptive_tfim_demo_rows = None
    adaptive_tfim_vqe_scan_rows = None
    write_adaptive_tfim_vqe_scan_csv = None
    generate_adaptive_tfim_report = None
    write_adaptive_tfim_report_csv = None
    imaginary_time_tfim_scan_rows = None
    real_time_tfim_scan_rows = None
    write_tfim_dynamics_scan_csv = None
    mps_tebd_tfim_rows = None
    write_mps_tebd_tfim_csv = None
    mps_trotter_order_rows = None
    write_mps_trotter_order_csv = None
    tfim_quench_comparison_rows = None
    write_tfim_quench_comparison_csv = None
    tfim_quench_error_map_rows = None
    write_tfim_quench_error_map_csv = None
    build_tfim_quench_threshold_report = None
    write_tfim_quench_threshold_csv = None
    mps_vs_statevector_rows = None
    write_mps_vs_statevector_csv = None
    tfim_mps_truncation_rows = None
    write_tfim_mps_truncation_csv = None
    depth_bond_rows = None
    write_mps_depth_bond_csv = None
    qaoa_mps_truncation_rows = None
    write_qaoa_mps_truncation_csv = None
    scaling_scan_rows = None
    write_tfim_scaling_csv = None
    comparative_variational_rows = None
    write_tfim_variational_scaling_csv = None
    evaluate_spin_scan = None


@unittest.skipIf(grid_search is None, "PennyLane examples are not importable")
class TestExamples(unittest.TestCase):
    def test_mini_vqe_grid_search_matches_analytic_minimum(self):
        a, b, c = 0.6, -0.9, 0.35
        result = grid_search(a, b, c, num_points=17)
        self.assertAlmostEqual(result["best_energy"], analytic_minimum(a, b, c), places=8)

    def test_hamiltonian_scan_matches_analytic_values(self):
        a, b, c = 0.7, -0.2, 1.3
        results = scan_basis_energies(a, b, c)
        self.assertEqual([row["state"] for row in results], ["00", "01", "10", "11"])
        for row in results:
            self.assertAlmostEqual(
                row["numeric"], analytic_basis_energy(row["state"], a, b, c), places=8
            )

    def test_two_qubit_spin_scan_returns_deterministic_rows(self):
        coeffs = {
            "x0": 0.35,
            "y0": -0.10,
            "z0": 0.80,
            "x1": -0.25,
            "y1": 0.30,
            "z1": -0.40,
            "zz": 1.10,
            "xx": 0.55,
            "yy": -0.45,
        }
        results = evaluate_spin_scan(coeffs)
        self.assertEqual(
            [row["state"] for row in results],
            ["basis_00", "basis_01", "plus0_plus1", "phase0_phase1", "bell"],
        )
        expected = {
            "basis_00": 1.5,
            "basis_01": 0.1,
            "plus0_plus1": 0.65,
            "phase0_phase1": -0.25,
            "bell": 2.1,
        }
        for row in results:
            self.assertAlmostEqual(row["energy"], expected[row["state"]], places=8)

    def test_ising_chain_scan_matches_analytic_values(self):
        num_qubits = 6
        fields_x = [0.25, -0.40, 0.15, 0.05, -0.30, 0.20]
        couplings_zz = [1.10, -0.70, 0.90, 0.40, -1.20]
        results = evaluate_chain_scan(num_qubits, fields_x, couplings_zz)
        self.assertEqual(
            [row["state"] for row in results],
            ["all_zero", "all_one", "all_plus", "neel"],
        )
        for row in results:
            self.assertAlmostEqual(
                row["energy"],
                analytic_chain_energy(row["state"], fields_x, couplings_zz),
                places=8,
            )
            self.assertAlmostEqual(row["energy"], row["analytic"], places=8)

    def test_tfim_scan_matches_analytic_values(self):
        rows = evaluate_tfim_scan(6, (0.0, 1.0))
        self.assertEqual(
            [(row["h"], row["state"]) for row in rows],
            [
                (0.0, "all_zero"),
                (0.0, "all_plus"),
                (0.0, "neel"),
                (1.0, "all_zero"),
                (1.0, "all_plus"),
                (1.0, "neel"),
            ],
        )
        for row in rows:
            self.assertAlmostEqual(
                row["energy"],
                analytic_tfim_energy(row["state"], row["n_qubits"], row["h"]),
                places=8,
            )
            self.assertAlmostEqual(row["energy"], row["analytic"], places=8)

    def test_qaoa_ising_small_grid_search_is_deterministic(self):
        result = qaoa_grid_search(num_qubits=4, num_gamma=9, num_beta=9)
        self.assertEqual(result["num_qubits"], 4)
        self.assertAlmostEqual(result["exact_classical_minimum"], exact_classical_minimum(4), places=8)
        self.assertGreaterEqual(result["best_gamma"], 0.0)
        self.assertLessEqual(result["best_gamma"], np.pi)
        self.assertGreaterEqual(result["best_beta"], 0.0)
        self.assertLessEqual(result["best_beta"], np.pi / 2.0)
        self.assertLessEqual(result["best_energy"], 0.0)
        self.assertGreaterEqual(result["best_energy"], result["exact_classical_minimum"])

    def test_tfim_scaling_scan_rows_have_expected_structure(self):
        rows = scaling_scan_rows(qubit_counts=(6, 8), h_values=(0.0, 1.0), state_name="all_plus")
        self.assertEqual(
            [(row["n"], row["h"]) for row in rows],
            [(6, 0.0), (6, 1.0), (8, 0.0), (8, 1.0)],
        )
        for row in rows:
            self.assertEqual(
                set(row), {"n", "h", "energy", "energy_per_site", "expval_x0", "expval_z0z1"}
            )
            self.assertAlmostEqual(row["expval_x0"], 1.0, places=8)
            self.assertAlmostEqual(row["expval_z0z1"], 0.0, places=8)
            self.assertAlmostEqual(row["energy"], row["h"] * row["n"], places=8)
            self.assertAlmostEqual(row["energy_per_site"], row["energy"] / row["n"], places=8)

    def test_qaoa_chain_landscape_rows_have_expected_structure(self):
        rows = qaoa_chain_landscape(num_qubits=8, num_gamma=3, num_beta=3)
        self.assertEqual(len(rows), 9)
        self.assertEqual(rows[0]["n"], 8)
        self.assertAlmostEqual(rows[0]["gamma"], 0.0, places=8)
        self.assertAlmostEqual(rows[0]["beta"], 0.0, places=8)
        for row in rows:
            self.assertEqual(set(row), {"n", "gamma", "beta", "energy"})
            self.assertGreaterEqual(row["gamma"], 0.0)
            self.assertLessEqual(row["gamma"], np.pi)
            self.assertGreaterEqual(row["beta"], 0.0)
            self.assertLessEqual(row["beta"], np.pi / 2.0)

    def test_tfim_scaling_csv_has_expected_header(self):
        rows = scaling_scan_rows(qubit_counts=(6,), h_values=(0.0,), state_name="all_plus")
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim.csv"
            write_tfim_scaling_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "n,h,energy,energy_per_site,expval_x0,expval_z0z1")
        self.assertEqual(len(lines), 2)

    def test_tfim_large_scale_campaign_rows_have_expected_structure(self):
        rows = large_scale_campaign_rows(qubit_counts=(12, 14), h_values=(0.0, 1.0), state_name="all_plus")
        self.assertEqual(
            [(row["n"], row["h"]) for row in rows],
            [(12, 0.0), (12, 1.0), (14, 0.0), (14, 1.0)],
        )
        for row in rows:
            self.assertEqual(
                set(row), {"n", "h", "energy", "energy_per_site", "expval_x0", "expval_z0z1"}
            )
            self.assertAlmostEqual(row["expval_x0"], 1.0, places=8)
            self.assertAlmostEqual(row["expval_z0z1"], 0.0, places=8)
            self.assertAlmostEqual(row["energy"], row["h"] * row["n"], places=8)
            self.assertAlmostEqual(row["energy_per_site"], row["energy"] / row["n"], places=8)

    def test_tfim_large_scale_campaign_csv_has_expected_header(self):
        rows = large_scale_campaign_rows(qubit_counts=(12,), h_values=(0.0,), state_name="all_plus")
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_large_scale.csv"
            write_tfim_large_scale_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "n,h,energy,energy_per_site,expval_x0,expval_z0z1")
        self.assertEqual(len(lines), 2)

    def test_tfim_exact_large_campaign_rows_have_expected_structure(self):
        rows = tfim_exact_large_rows(qubit_counts=(8, 10), h_values=(0.0, 1.0), state_name="all_plus")
        self.assertEqual(
            [(row["n"], row["h"]) for row in rows],
            [(8, 0.0), (8, 1.0), (10, 0.0), (10, 1.0)],
        )
        for row in rows:
            self.assertEqual(
                set(row), {"n", "h", "energy", "energy_per_site", "expval_x0", "expval_z0z1"}
            )
            self.assertAlmostEqual(row["energy_per_site"], row["energy"] / row["n"], places=8)

    def test_tfim_exact_large_campaign_csv_has_expected_header(self):
        rows = tfim_exact_large_rows(qubit_counts=(8,), h_values=(0.0,), state_name="all_plus")
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_exact_large.csv"
            write_tfim_exact_large_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "n,h,energy,energy_per_site,expval_x0,expval_z0z1")
        self.assertEqual(len(lines), 2)

    def test_tfim_mps_large_campaign_rows_have_expected_structure(self):
        rows = tfim_mps_large_rows(
            qubit_counts=(12,),
            h_values=(0.0, 0.5),
            bond_dims=(2, 4),
            svd_cutoff=1e-12,
        )
        self.assertEqual(
            [(row["n"], row["h"], row["max_bond_dim"]) for row in rows],
            [(12, 0.0, 2), (12, 0.0, 4), (12, 0.5, 2), (12, 0.5, 4)],
        )
        for row in rows:
            self.assertEqual(
                set(row), {"n", "h", "max_bond_dim", "svd_cutoff", "mps_energy", "energy_per_site"}
            )
            self.assertAlmostEqual(row["energy_per_site"], row["mps_energy"] / row["n"], places=8)

    def test_tfim_mps_large_campaign_csv_has_expected_header(self):
        rows = tfim_mps_large_rows(
            qubit_counts=(12,),
            h_values=(0.0,),
            bond_dims=(2,),
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_mps_large.csv"
            write_tfim_mps_large_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "n,h,max_bond_dim,svd_cutoff,mps_energy,energy_per_site")
        self.assertEqual(len(lines), 2)

    def test_tfim_exact_vs_mps_large_report_has_expected_structure(self):
        with tempfile.TemporaryDirectory() as tempdir:
            exact_rows = tfim_exact_large_rows(qubit_counts=(12,), h_values=(0.0, 0.5), state_name="all_plus")
            mps_rows = tfim_mps_large_rows(qubit_counts=(12,), h_values=(0.0, 0.5), bond_dims=(2, 4), svd_cutoff=1e-12)
            exact_path = pathlib.Path(tempdir) / "exact.csv"
            mps_path = pathlib.Path(tempdir) / "mps.csv"
            write_tfim_exact_large_csv(exact_path, exact_rows)
            write_tfim_mps_large_csv(mps_path, mps_rows)

            result = build_tfim_exact_vs_mps_large_report(exact_path, mps_path)

        self.assertEqual(result["exact_row_count"], 2)
        self.assertEqual(result["mps_row_count"], 4)
        self.assertEqual(result["overlap_row_count"], 4)
        self.assertEqual(
            result["reference_workflow"],
            "sum_i <Z_i Z_{i+1}> on the deterministic TFIM-style chain ansatz",
        )
        for row in result["rows"]:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "max_bond_dim",
                    "svd_cutoff",
                    "reference_energy",
                    "mps_energy",
                    "abs_error",
                    "energy_error_per_site",
                },
            )
            self.assertGreaterEqual(row["abs_error"], 0.0)
            self.assertAlmostEqual(row["energy_error_per_site"], row["abs_error"] / row["n"], places=8)
            self.assertAlmostEqual(row["abs_error"], 0.0, places=8)

    def test_tfim_exact_vs_mps_large_report_csv_has_expected_header(self):
        with tempfile.TemporaryDirectory() as tempdir:
            exact_rows = tfim_exact_large_rows(qubit_counts=(12,), h_values=(0.0,), state_name="all_plus")
            mps_rows = tfim_mps_large_rows(qubit_counts=(12,), h_values=(0.0,), bond_dims=(2,), svd_cutoff=1e-12)
            exact_path = pathlib.Path(tempdir) / "exact.csv"
            mps_path = pathlib.Path(tempdir) / "mps.csv"
            report_path = pathlib.Path(tempdir) / "report.csv"
            write_tfim_exact_large_csv(exact_path, exact_rows)
            write_tfim_mps_large_csv(mps_path, mps_rows)
            result = build_tfim_exact_vs_mps_large_report(exact_path, mps_path)
            write_tfim_exact_vs_mps_large_report_csv(report_path, result["rows"])
            lines = report_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,max_bond_dim,svd_cutoff,reference_energy,mps_energy,abs_error,energy_error_per_site",
        )
        self.assertEqual(len(lines), 2)

    def test_tfim_mps_sensitivity_report_has_expected_structure(self):
        with tempfile.TemporaryDirectory() as tempdir:
            exact_rows = tfim_exact_large_rows(qubit_counts=(12,), h_values=(0.0, 0.5), state_name="all_plus")
            mps_rows = tfim_mps_large_rows(qubit_counts=(12,), h_values=(0.0, 0.5), bond_dims=(2, 4), svd_cutoff=1e-12)
            exact_path = pathlib.Path(tempdir) / "exact.csv"
            mps_path = pathlib.Path(tempdir) / "mps.csv"
            report_path = pathlib.Path(tempdir) / "report.csv"
            write_tfim_exact_large_csv(exact_path, exact_rows)
            write_tfim_mps_large_csv(mps_path, mps_rows)
            report = build_tfim_exact_vs_mps_large_report(exact_path, mps_path)
            write_tfim_exact_vs_mps_large_report_csv(report_path, report["rows"])

            result = build_tfim_mps_sensitivity_report(report_path)

        self.assertEqual(result["input_row_count"], 4)
        self.assertEqual(result["summary_row_count"], 4)
        self.assertIsNotNone(result["min_error_row"])
        self.assertIsNotNone(result["max_error_row"])
        for row in result["summary_rows"]:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "max_bond_dim",
                    "svd_cutoff",
                    "mean_abs_error",
                    "energy_error_per_site",
                    "error_rank",
                    "sensitivity_label",
                },
            )
            self.assertGreaterEqual(row["mean_abs_error"], 0.0)
            self.assertAlmostEqual(row["mean_abs_error"] / row["n"], row["energy_error_per_site"], places=8)
            self.assertIn(row["sensitivity_label"], {"low", "medium", "high"})
            self.assertGreaterEqual(row["error_rank"], 1)

    def test_tfim_mps_sensitivity_report_csv_has_expected_header(self):
        with tempfile.TemporaryDirectory() as tempdir:
            exact_rows = tfim_exact_large_rows(qubit_counts=(12,), h_values=(0.0,), state_name="all_plus")
            mps_rows = tfim_mps_large_rows(qubit_counts=(12,), h_values=(0.0,), bond_dims=(2,), svd_cutoff=1e-12)
            exact_path = pathlib.Path(tempdir) / "exact.csv"
            mps_path = pathlib.Path(tempdir) / "mps.csv"
            report_path = pathlib.Path(tempdir) / "report.csv"
            summary_path = pathlib.Path(tempdir) / "summary.csv"
            write_tfim_exact_large_csv(exact_path, exact_rows)
            write_tfim_mps_large_csv(mps_path, mps_rows)
            report = build_tfim_exact_vs_mps_large_report(exact_path, mps_path)
            write_tfim_exact_vs_mps_large_report_csv(report_path, report["rows"])
            result = build_tfim_mps_sensitivity_report(report_path)
            write_tfim_mps_sensitivity_csv(summary_path, result["summary_rows"])
            lines = summary_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,max_bond_dim,svd_cutoff,mean_abs_error,energy_error_per_site,error_rank,sensitivity_label",
        )
        self.assertEqual(len(lines), 2)

    def test_tfim_mps_threshold_report_has_expected_structure(self):
        with tempfile.TemporaryDirectory() as tempdir:
            exact_rows = tfim_exact_large_rows(qubit_counts=(12,), h_values=(0.0, 0.5), state_name="all_plus")
            mps_rows = tfim_mps_large_rows(qubit_counts=(12,), h_values=(0.0, 0.5), bond_dims=(1, 2, 4), svd_cutoff=1e-12)
            exact_path = pathlib.Path(tempdir) / "exact.csv"
            mps_path = pathlib.Path(tempdir) / "mps.csv"
            report_path = pathlib.Path(tempdir) / "report.csv"
            sensitivity_path = pathlib.Path(tempdir) / "sensitivity.csv"
            write_tfim_exact_large_csv(exact_path, exact_rows)
            write_tfim_mps_large_csv(mps_path, mps_rows)
            report = build_tfim_exact_vs_mps_large_report(exact_path, mps_path)
            write_tfim_exact_vs_mps_large_report_csv(report_path, report["rows"])
            sensitivity = build_tfim_mps_sensitivity_report(report_path)
            write_tfim_mps_sensitivity_csv(sensitivity_path, sensitivity["summary_rows"])

            result = build_tfim_mps_threshold_report(sensitivity_path, error_threshold=1e-6, per_site_threshold=1e-7)

        self.assertEqual(result["input_row_count"], 6)
        self.assertEqual(result["summary_row_count"], 2)
        for row in result["summary_rows"]:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "error_threshold",
                    "per_site_threshold",
                    "min_bond_dim_meeting_threshold",
                    "best_abs_error",
                    "best_energy_error_per_site",
                },
            )
            self.assertGreaterEqual(row["best_abs_error"], 0.0)
            self.assertGreaterEqual(row["best_energy_error_per_site"], 0.0)
            self.assertAlmostEqual(row["error_threshold"], 1e-6, places=12)
            self.assertAlmostEqual(row["per_site_threshold"], 1e-7, places=12)
        zero_h_row = next(row for row in result["summary_rows"] if row["h"] == 0.0)
        self.assertEqual(zero_h_row["min_bond_dim_meeting_threshold"], 1)

    def test_tfim_mps_threshold_report_csv_has_expected_header(self):
        with tempfile.TemporaryDirectory() as tempdir:
            exact_rows = tfim_exact_large_rows(qubit_counts=(12,), h_values=(0.0,), state_name="all_plus")
            mps_rows = tfim_mps_large_rows(qubit_counts=(12,), h_values=(0.0,), bond_dims=(1, 2), svd_cutoff=1e-12)
            exact_path = pathlib.Path(tempdir) / "exact.csv"
            mps_path = pathlib.Path(tempdir) / "mps.csv"
            report_path = pathlib.Path(tempdir) / "report.csv"
            threshold_path = pathlib.Path(tempdir) / "threshold.csv"
            write_tfim_exact_large_csv(exact_path, exact_rows)
            write_tfim_mps_large_csv(mps_path, mps_rows)
            report = build_tfim_exact_vs_mps_large_report(exact_path, mps_path)
            write_tfim_exact_vs_mps_large_report_csv(report_path, report["rows"])
            result = build_tfim_mps_threshold_report(report_path)
            write_tfim_mps_threshold_csv(threshold_path, result["summary_rows"])
            lines = threshold_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,error_threshold,per_site_threshold,min_bond_dim_meeting_threshold,best_abs_error,best_energy_error_per_site",
        )
        self.assertEqual(len(lines), 2)

    def test_mps_general_pauli_demo_rows_have_expected_structure(self):
        rows = general_pauli_demo_rows()
        self.assertEqual([row["observable"] for row in rows], ["X0", "Y1", "X0@Y1@X2"])
        for row in rows:
            self.assertEqual(set(row), {"observable", "mps_value", "reference_value", "abs_error"})
            self.assertAlmostEqual(row["mps_value"], row["reference_value"], places=8)
            self.assertAlmostEqual(row["abs_error"], 0.0, places=8)

    def test_mps_tebd_tfim_rows_have_expected_structure(self):
        rows = mps_tebd_tfim_rows(
            qubit_counts=(8,),
            h_values=(0.5,),
            dt=0.1,
            num_steps=2,
            max_bond_dim=4,
            svd_cutoff=1e-12,
        )
        self.assertEqual(
            [(row["n"], row["h"], row["step"]) for row in rows],
            [(8, 0.5, 0), (8, 0.5, 1), (8, 0.5, 2)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "dt",
                    "step",
                    "time",
                    "max_bond_dim",
                    "svd_cutoff",
                    "expval_z0",
                    "expval_z0z1",
                },
            )
            self.assertAlmostEqual(row["time"], row["step"] * row["dt"], places=8)
        self.assertAlmostEqual(rows[0]["expval_z0"], 1.0, places=8)
        self.assertAlmostEqual(rows[0]["expval_z0z1"], 1.0, places=8)

    def test_mps_tebd_tfim_csv_has_expected_header(self):
        rows = mps_tebd_tfim_rows(
            qubit_counts=(8,),
            h_values=(0.5,),
            dt=0.1,
            num_steps=1,
            max_bond_dim=4,
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "mps_tebd_tfim.csv"
            write_mps_tebd_tfim_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,dt,step,time,max_bond_dim,svd_cutoff,expval_z0,expval_z0z1",
        )
        self.assertEqual(len(lines), 3)

    def test_mps_trotter_order_rows_have_expected_structure(self):
        rows = mps_trotter_order_rows(
            qubit_counts=(8,),
            h_values=(0.5,),
            dt_values=(0.2, 0.1),
            total_time=0.4,
            max_bond_dim=4,
            svd_cutoff=1e-12,
        )
        self.assertEqual(
            [(row["n"], row["dt"], row["trotter_order"]) for row in rows],
            [(8, 0.2, 1), (8, 0.2, 2), (8, 0.1, 1), (8, 0.1, 2)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "dt",
                    "steps",
                    "time",
                    "trotter_order",
                    "max_bond_dim",
                    "svd_cutoff",
                    "expval_z0",
                    "expval_z0z1",
                },
            )
            self.assertIn(row["trotter_order"], {1, 2})
            self.assertAlmostEqual(row["time"], row["steps"] * row["dt"], places=8)
            self.assertGreaterEqual(row["expval_z0"], -1.0)
            self.assertLessEqual(row["expval_z0"], 1.0)
            self.assertGreaterEqual(row["expval_z0z1"], -1.0)
            self.assertLessEqual(row["expval_z0z1"], 1.0)

    def test_mps_trotter_order_csv_has_expected_header(self):
        rows = mps_trotter_order_rows(
            qubit_counts=(8,),
            h_values=(0.5,),
            dt_values=(0.2,),
            total_time=0.4,
            max_bond_dim=4,
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "mps_trotter_order.csv"
            write_mps_trotter_order_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,dt,steps,time,trotter_order,max_bond_dim,svd_cutoff,expval_z0,expval_z0z1",
        )
        self.assertEqual(len(lines), 3)

    def test_tfim_quench_comparison_rows_have_expected_structure(self):
        rows = tfim_quench_comparison_rows(
            qubit_counts=(6,),
            h_values=(0.5,),
            dt_values=(0.2,),
            total_time=0.4,
            bond_dims=(2, 4),
            svd_cutoff=1e-12,
        )
        self.assertEqual(
            [(row["n"], row["trotter_order"], row["max_bond_dim"]) for row in rows],
            [(6, 1, 2), (6, 1, 4), (6, 2, 2), (6, 2, 4)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "dt",
                    "steps",
                    "time",
                    "trotter_order",
                    "max_bond_dim",
                    "svd_cutoff",
                    "reference_z0",
                    "mps_z0",
                    "abs_error_z0",
                    "reference_z0z1",
                    "mps_z0z1",
                    "abs_error_z0z1",
                },
            )
            self.assertAlmostEqual(row["time"], row["steps"] * row["dt"], places=8)
            self.assertGreaterEqual(row["abs_error_z0"], 0.0)
            self.assertGreaterEqual(row["abs_error_z0z1"], 0.0)
        by_key = {(row["trotter_order"], row["max_bond_dim"]): row for row in rows}
        self.assertLess(by_key[(1, 2)]["abs_error_z0"], 1e-8)
        self.assertLess(by_key[(1, 2)]["abs_error_z0z1"], 1e-8)
        self.assertLess(by_key[(1, 4)]["abs_error_z0"], 1e-8)
        self.assertLess(by_key[(1, 4)]["abs_error_z0z1"], 1e-8)
        self.assertLess(by_key[(2, 2)]["abs_error_z0"], 1e-4)
        self.assertLess(by_key[(2, 2)]["abs_error_z0z1"], 1e-3)
        self.assertLess(by_key[(2, 4)]["abs_error_z0"], 1e-5)
        self.assertLess(by_key[(2, 4)]["abs_error_z0z1"], 1e-5)

    def test_tfim_quench_comparison_csv_has_expected_header(self):
        rows = tfim_quench_comparison_rows(
            qubit_counts=(6,),
            h_values=(0.5,),
            dt_values=(0.2,),
            total_time=0.4,
            bond_dims=(2,),
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "mps_vs_statevector_tfim_quench.csv"
            write_tfim_quench_comparison_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,dt,steps,time,trotter_order,max_bond_dim,svd_cutoff,reference_z0,mps_z0,abs_error_z0,reference_z0z1,mps_z0z1,abs_error_z0z1",
        )
        self.assertEqual(len(lines), 3)

    def test_tfim_quench_error_map_rows_have_expected_structure(self):
        rows = tfim_quench_error_map_rows(
            qubit_counts=(6,),
            h_values=(0.5,),
            dt_values=(0.2,),
            total_time=0.4,
            bond_dims=(2, 4),
            svd_cutoff=1e-12,
        )
        self.assertEqual(
            [(row["n"], row["trotter_order"], row["max_bond_dim"]) for row in rows],
            [(6, 1, 2), (6, 1, 4), (6, 2, 2), (6, 2, 4)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "dt",
                    "steps",
                    "time",
                    "trotter_order",
                    "max_bond_dim",
                    "svd_cutoff",
                    "abs_error_z0",
                    "abs_error_z0z1",
                },
            )
            self.assertAlmostEqual(row["time"], row["steps"] * row["dt"], places=8)
            self.assertGreaterEqual(row["abs_error_z0"], 0.0)
            self.assertGreaterEqual(row["abs_error_z0z1"], 0.0)

    def test_tfim_quench_error_map_csv_has_expected_header(self):
        rows = tfim_quench_error_map_rows(
            qubit_counts=(6,),
            h_values=(0.5,),
            dt_values=(0.2,),
            total_time=0.4,
            bond_dims=(2,),
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_quench_error_map.csv"
            write_tfim_quench_error_map_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,dt,steps,time,trotter_order,max_bond_dim,svd_cutoff,abs_error_z0,abs_error_z0z1",
        )
        self.assertEqual(len(lines), 3)

    def test_tfim_quench_threshold_report_has_expected_structure(self):
        rows = tfim_quench_error_map_rows(
            qubit_counts=(6,),
            h_values=(0.5,),
            dt_values=(0.2,),
            total_time=0.4,
            bond_dims=(2, 4),
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            error_map_path = pathlib.Path(tempdir) / "tfim_quench_error_map.csv"
            write_tfim_quench_error_map_csv(error_map_path, rows)
            result = build_tfim_quench_threshold_report(
                error_map_path,
                error_threshold_z0=1e-5,
                error_threshold_z0z1=1e-4,
            )

        self.assertEqual(result["input_row_count"], 4)
        self.assertEqual(result["summary_row_count"], 2)
        for row in result["summary_rows"]:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "dt",
                    "time",
                    "trotter_order",
                    "error_threshold_z0",
                    "error_threshold_z0z1",
                    "min_bond_dim_for_z0",
                    "min_bond_dim_for_z0z1",
                    "best_abs_error_z0",
                    "best_abs_error_z0z1",
                },
            )
            self.assertGreaterEqual(row["best_abs_error_z0"], 0.0)
            self.assertGreaterEqual(row["best_abs_error_z0z1"], 0.0)
        by_order = {row["trotter_order"]: row for row in result["summary_rows"]}
        self.assertEqual(by_order[1]["min_bond_dim_for_z0"], 2)
        self.assertEqual(by_order[1]["min_bond_dim_for_z0z1"], 2)
        self.assertEqual(by_order[2]["min_bond_dim_for_z0"], 2)
        self.assertEqual(by_order[2]["min_bond_dim_for_z0z1"], 4)

    def test_tfim_quench_threshold_csv_has_expected_header(self):
        rows = tfim_quench_error_map_rows(
            qubit_counts=(6,),
            h_values=(0.5,),
            dt_values=(0.2,),
            total_time=0.4,
            bond_dims=(2, 4),
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            error_map_path = pathlib.Path(tempdir) / "tfim_quench_error_map.csv"
            threshold_path = pathlib.Path(tempdir) / "tfim_quench_threshold.csv"
            write_tfim_quench_error_map_csv(error_map_path, rows)
            result = build_tfim_quench_threshold_report(error_map_path)
            write_tfim_quench_threshold_csv(threshold_path, result["summary_rows"])
            lines = threshold_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,dt,time,trotter_order,error_threshold_z0,error_threshold_z0z1,min_bond_dim_for_z0,min_bond_dim_for_z0z1,best_abs_error_z0,best_abs_error_z0z1",
        )
        self.assertEqual(len(lines), 3)

    def test_mps_vs_statevector_rows_have_expected_structure(self):
        rows = mps_vs_statevector_rows(
            qubit_counts=(6,),
            h_values=(0.0, 0.5),
            truncation_settings=((None, 0.0), (2, 1e-12), (1, 0.0)),
        )
        self.assertEqual(
            [(row["n"], row["h"]) for row in rows],
            [(6, 0.0), (6, 0.0), (6, 0.0), (6, 0.5), (6, 0.5), (6, 0.5)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {"n", "h", "max_bond_dim", "svd_cutoff", "reference_energy", "mps_energy", "abs_error"},
            )
            self.assertGreaterEqual(row["abs_error"], 0.0)

        by_key = {(row["h"], row["max_bond_dim"]): row for row in rows}
        self.assertAlmostEqual(by_key[(0.0, "")]["abs_error"], 0.0, places=8)
        self.assertAlmostEqual(by_key[(0.5, 2)]["abs_error"], 0.0, places=8)

    def test_mps_vs_statevector_csv_has_expected_header(self):
        rows = mps_vs_statevector_rows(
            qubit_counts=(6,),
            h_values=(0.0,),
            truncation_settings=((None, 0.0),),
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "mps_vs_statevector.csv"
            write_mps_vs_statevector_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,max_bond_dim,svd_cutoff,reference_energy,mps_energy,abs_error",
        )
        self.assertEqual(len(lines), 2)

    def test_tfim_mps_truncation_rows_have_expected_structure(self):
        rows = tfim_mps_truncation_rows(
            qubit_counts=(8,),
            h_values=(0.0, 0.5),
            truncation_settings=((None, 0.0), (2, 1e-12), (1, 0.0)),
        )
        self.assertEqual(
            [(row["n"], row["h"]) for row in rows],
            [(8, 0.0), (8, 0.0), (8, 0.0), (8, 0.5), (8, 0.5), (8, 0.5)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "max_bond_dim",
                    "svd_cutoff",
                    "mps_energy",
                    "reference_energy",
                    "abs_error",
                    "energy_error_per_site",
                },
            )
            self.assertGreaterEqual(row["abs_error"], 0.0)
            self.assertAlmostEqual(row["energy_error_per_site"], row["abs_error"] / row["n"], places=8)

        by_key = {(row["h"], row["max_bond_dim"]): row for row in rows}
        self.assertAlmostEqual(by_key[(0.0, "")]["abs_error"], 0.0, places=8)
        self.assertAlmostEqual(by_key[(0.5, 2)]["abs_error"], 0.0, places=8)

    def test_tfim_mps_truncation_csv_has_expected_header(self):
        rows = tfim_mps_truncation_rows(
            qubit_counts=(8,),
            h_values=(0.0,),
            truncation_settings=((None, 0.0),),
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_mps_truncation.csv"
            write_tfim_mps_truncation_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,max_bond_dim,svd_cutoff,mps_energy,reference_energy,abs_error,energy_error_per_site",
        )
        self.assertEqual(len(lines), 2)

    def test_mps_depth_bond_rows_have_expected_structure(self):
        rows = depth_bond_rows(
            qubit_counts=(8,),
            h_values=(0.5,),
            depths=(1, 2),
            truncation_settings=((None, 0.0), (1, 0.0)),
        )
        self.assertEqual(
            [(row["n"], row["h"], row["depth"]) for row in rows],
            [(8, 0.5, 1), (8, 0.5, 1), (8, 0.5, 2), (8, 0.5, 2)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "depth",
                    "max_bond_dim",
                    "svd_cutoff",
                    "mps_energy",
                    "reference_energy",
                    "abs_error",
                    "energy_error_per_site",
                },
            )
            self.assertGreaterEqual(row["abs_error"], 0.0)
            self.assertAlmostEqual(row["energy_error_per_site"], row["abs_error"] / row["n"], places=8)

        by_key = {(row["depth"], row["max_bond_dim"]): row for row in rows}
        self.assertAlmostEqual(by_key[(1, "")]["abs_error"], 0.0, places=8)
        self.assertLessEqual(by_key[(1, "")]["abs_error"], by_key[(1, 1)]["abs_error"] + 1e-12)

    def test_mps_depth_bond_csv_has_expected_header(self):
        rows = depth_bond_rows(
            qubit_counts=(8,),
            h_values=(0.5,),
            depths=(1,),
            truncation_settings=((None, 0.0),),
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "mps_depth_bond.csv"
            write_mps_depth_bond_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,depth,max_bond_dim,svd_cutoff,mps_energy,reference_energy,abs_error,energy_error_per_site",
        )
        self.assertEqual(len(lines), 2)

    def test_qaoa_mps_truncation_rows_have_expected_structure(self):
        rows = qaoa_mps_truncation_rows(
            qubit_counts=(8,),
            gamma_values=(0.0, np.pi / 4.0),
            beta_values=(0.0,),
            truncation_settings=((None, 0.0), (1, 0.0)),
        )
        self.assertEqual(
            [(row["n"], row["gamma"], row["beta"]) for row in rows],
            [(8, 0.0, 0.0), (8, 0.0, 0.0), (8, np.pi / 4.0, 0.0), (8, np.pi / 4.0, 0.0)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "gamma",
                    "beta",
                    "max_bond_dim",
                    "svd_cutoff",
                    "reference_energy",
                    "mps_energy",
                    "abs_error",
                },
            )
            self.assertGreaterEqual(row["abs_error"], 0.0)

        by_key = {(row["gamma"], row["max_bond_dim"]): row for row in rows}
        self.assertAlmostEqual(by_key[(0.0, "")]["abs_error"], 0.0, places=8)

    def test_qaoa_mps_truncation_csv_has_expected_header(self):
        rows = qaoa_mps_truncation_rows(
            qubit_counts=(8,),
            gamma_values=(0.0,),
            beta_values=(0.0,),
            truncation_settings=((None, 0.0),),
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "qaoa_mps_truncation.csv"
            write_qaoa_mps_truncation_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,gamma,beta,max_bond_dim,svd_cutoff,reference_energy,mps_energy,abs_error",
        )
        self.assertEqual(len(lines), 2)

    def test_tfim_finite_size_summary_rows_have_expected_structure(self):
        rows = finite_size_summary_rows(qubit_counts=(6, 8), h_values=(0.0, 1.0), state_name="all_plus")
        self.assertEqual([row["h"] for row in rows], [0.0, 1.0])
        for row in rows:
            self.assertEqual(
                set(row), {"h", "min_energy_per_site", "max_energy_per_site", "delta_energy_per_site"}
            )
            self.assertLessEqual(row["min_energy_per_site"], row["max_energy_per_site"])
            self.assertGreaterEqual(row["delta_energy_per_site"], 0.0)

    def test_tfim_finite_size_summary_csv_has_expected_header(self):
        rows = finite_size_summary_rows(qubit_counts=(6, 8), h_values=(0.0,), state_name="all_plus")
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_summary.csv"
            write_finite_size_summary_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "h,min_energy_per_site,max_energy_per_site,delta_energy_per_site")
        self.assertEqual(len(lines), 2)

    def test_tfim_variational_study_rows_have_expected_structure(self):
        rows = variational_study_rows(qubit_counts=(6,), h_values=(0.0, 1.0), num_theta=5)
        self.assertEqual([(row["n"], row["h"]) for row in rows], [(6, 0.0), (6, 1.0)])
        for row in rows:
            self.assertEqual(
                set(row), {"n", "h", "theta", "variational_energy", "reference_energy", "energy_error"}
            )
            self.assertGreaterEqual(row["theta"], 0.0)
            self.assertLessEqual(row["theta"], np.pi)
            self.assertAlmostEqual(
                row["energy_error"], row["variational_energy"] - row["reference_energy"], places=8
            )
            self.assertGreaterEqual(row["variational_energy"], row["reference_energy"])

    def test_tfim_variational_csv_has_expected_header(self):
        rows = variational_study_rows(qubit_counts=(6,), h_values=(0.0,), num_theta=5)
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_variational.csv"
            write_tfim_groundstate_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "n,h,theta,variational_energy,reference_energy,energy_error")
        self.assertEqual(len(lines), 2)

    def test_tfim_variational_scaling_rows_have_expected_structure(self):
        rows = comparative_variational_rows(qubit_counts=(6, 8), h_values=(0.0, 1.0), num_theta=5)
        self.assertEqual(
            [(row["n"], row["h"]) for row in rows],
            [(6, 0.0), (6, 1.0), (8, 0.0), (8, 1.0)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "theta_best",
                    "variational_energy",
                    "reference_energy",
                    "energy_error",
                    "energy_error_per_site",
                },
            )
            self.assertGreaterEqual(row["theta_best"], 0.0)
            self.assertLessEqual(row["theta_best"], np.pi)
            self.assertAlmostEqual(
                row["energy_error"], row["variational_energy"] - row["reference_energy"], places=8
            )
            self.assertAlmostEqual(
                row["energy_error_per_site"], row["energy_error"] / row["n"], places=8
            )

    def test_tfim_variational_scaling_csv_has_expected_header(self):
        rows = comparative_variational_rows(qubit_counts=(6,), h_values=(0.0,), num_theta=5)
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_variational_scaling.csv"
            write_tfim_variational_scaling_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,theta_best,variational_energy,reference_energy,energy_error,energy_error_per_site",
        )
        self.assertEqual(len(lines), 2)

    def test_tfim_ansatz_comparison_rows_have_expected_structure(self):
        rows = ansatz_comparison_rows(qubit_counts=(6,), h_values=(0.0, 1.0), num_theta=5)
        self.assertEqual(
            [(row["n"], row["h"], row["ansatz_type"]) for row in rows],
            [
                (6, 0.0, "product_ry"),
                (6, 0.0, "entangling_ry_cnot_ry"),
                (6, 1.0, "product_ry"),
                (6, 1.0, "entangling_ry_cnot_ry"),
            ],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "ansatz_type",
                    "variational_energy",
                    "reference_energy",
                    "energy_error",
                    "energy_error_per_site",
                },
            )
            self.assertAlmostEqual(
                row["energy_error"], row["variational_energy"] - row["reference_energy"], places=8
            )
            self.assertAlmostEqual(
                row["energy_error_per_site"], row["energy_error"] / row["n"], places=8
            )

        grouped = {(row["n"], row["h"], row["ansatz_type"]): row for row in rows}
        self.assertLessEqual(
            grouped[(6, 0.0, "entangling_ry_cnot_ry")]["energy_error"],
            grouped[(6, 0.0, "product_ry")]["energy_error"],
        )

    def test_tfim_ansatz_comparison_csv_has_expected_header(self):
        rows = ansatz_comparison_rows(qubit_counts=(6,), h_values=(0.0,), num_theta=5)
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_ansatz_comparison.csv"
            write_tfim_ansatz_comparison_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,ansatz_type,variational_energy,reference_energy,energy_error,energy_error_per_site",
        )
        self.assertEqual(len(lines), 3)

    def test_tfim_ansatz_cost_quality_rows_have_expected_structure(self):
        rows = cost_quality_rows(qubit_counts=(6,), h_values=(0.0, 1.0), num_theta=5)
        self.assertEqual(
            [(row["n"], row["h"], row["ansatz_type"]) for row in rows],
            [
                (6, 0.0, "product_ry"),
                (6, 0.0, "entangling_ry_cnot_ry"),
                (6, 1.0, "product_ry"),
                (6, 1.0, "entangling_ry_cnot_ry"),
            ],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "ansatz_type",
                    "parameter_count",
                    "variational_energy",
                    "reference_energy",
                    "energy_error",
                    "energy_error_per_site",
                },
            )
            if row["ansatz_type"] == "product_ry":
                self.assertEqual(row["parameter_count"], row["n"])
            else:
                self.assertEqual(row["parameter_count"], 2 * row["n"])
            self.assertAlmostEqual(
                row["energy_error"], row["variational_energy"] - row["reference_energy"], places=8
            )
            self.assertAlmostEqual(
                row["energy_error_per_site"], row["energy_error"] / row["n"], places=8
            )

    def test_tfim_ansatz_cost_quality_csv_has_expected_header(self):
        rows = cost_quality_rows(qubit_counts=(6,), h_values=(0.0,), num_theta=5)
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_ansatz_cost_quality.csv"
            write_tfim_ansatz_cost_quality_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,ansatz_type,parameter_count,variational_energy,reference_energy,energy_error,energy_error_per_site",
        )
        self.assertEqual(len(lines), 3)

    def test_tfim_ansatz_depth_rows_have_expected_structure(self):
        rows = ansatz_depth_rows(qubit_counts=(6,), h_values=(0.0, 1.0), num_theta=5)
        self.assertEqual(
            [(row["n"], row["h"], row["ansatz_type"], row["depth"]) for row in rows],
            [
                (6, 0.0, "product_ry", 0),
                (6, 0.0, "entangling_ry_cnot_ry", 1),
                (6, 0.0, "entangling_ry_cnot_ry", 2),
                (6, 1.0, "product_ry", 0),
                (6, 1.0, "entangling_ry_cnot_ry", 1),
                (6, 1.0, "entangling_ry_cnot_ry", 2),
            ],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "ansatz_type",
                    "depth",
                    "parameter_count",
                    "variational_energy",
                    "reference_energy",
                    "energy_error",
                    "energy_error_per_site",
                },
            )
            if row["ansatz_type"] == "product_ry":
                self.assertEqual(row["depth"], 0)
                self.assertEqual(row["parameter_count"], row["n"])
            elif row["depth"] == 1:
                self.assertEqual(row["parameter_count"], 2 * row["n"])
            else:
                self.assertEqual(row["parameter_count"], 3 * row["n"])
            self.assertAlmostEqual(
                row["energy_error"], row["variational_energy"] - row["reference_energy"], places=8
            )
            self.assertAlmostEqual(
                row["energy_error_per_site"], row["energy_error"] / row["n"], places=8
            )

        grouped = {(row["n"], row["h"], row["depth"]): row for row in rows}
        self.assertLessEqual(
            grouped[(6, 0.0, 1)]["energy_error"],
            grouped[(6, 0.0, 0)]["energy_error"],
        )
        self.assertLessEqual(
            grouped[(6, 0.0, 2)]["energy_error"],
            grouped[(6, 0.0, 1)]["energy_error"],
        )

    def test_tfim_ansatz_depth_csv_has_expected_header(self):
        rows = ansatz_depth_rows(qubit_counts=(6,), h_values=(0.0,), num_theta=5)
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_ansatz_depth.csv"
            write_tfim_ansatz_depth_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,ansatz_type,depth,parameter_count,variational_energy,reference_energy,energy_error,energy_error_per_site",
        )
        self.assertEqual(len(lines), 4)

    def test_tfim_grid_resolution_rows_have_expected_structure(self):
        rows = grid_resolution_rows(
            qubit_counts=(6,),
            h_values=(0.0, 1.0),
            grid_sizes={"coarse": 3, "medium": 5},
        )
        self.assertEqual(
            [(row["n"], row["h"], row["depth"], row["grid_size"]) for row in rows],
            [
                (6, 0.0, 1, "coarse"),
                (6, 0.0, 2, "coarse"),
                (6, 1.0, 1, "coarse"),
                (6, 1.0, 2, "coarse"),
                (6, 0.0, 1, "medium"),
                (6, 0.0, 2, "medium"),
                (6, 1.0, 1, "medium"),
                (6, 1.0, 2, "medium"),
            ],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "ansatz_type",
                    "depth",
                    "grid_size",
                    "variational_energy",
                    "reference_energy",
                    "energy_error",
                    "energy_error_per_site",
                },
            )
            self.assertEqual(row["ansatz_type"], "entangling_ry_cnot_ry")
            self.assertIn(row["depth"], {1, 2})
            self.assertIn(row["grid_size"], {"coarse", "medium"})
            self.assertAlmostEqual(
                row["energy_error"], row["variational_energy"] - row["reference_energy"], places=8
            )
            self.assertAlmostEqual(
                row["energy_error_per_site"], row["energy_error"] / row["n"], places=8
            )

    def test_tfim_grid_resolution_csv_has_expected_header(self):
        rows = grid_resolution_rows(qubit_counts=(6,), h_values=(0.0,), grid_sizes={"coarse": 3})
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "tfim_grid_resolution.csv"
            write_tfim_grid_resolution_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,ansatz_type,depth,grid_size,variational_energy,reference_energy,energy_error,energy_error_per_site",
        )
        self.assertEqual(len(lines), 3)

    def test_tfim_research_campaign_output_paths_are_stable(self):
        paths = campaign_output_paths("campaign_out")
        self.assertEqual(paths["reference_scan"].name, "tfim_reference_scan.csv")
        self.assertEqual(paths["variational_scaling"].name, "tfim_variational_scaling.csv")
        self.assertEqual(paths["ansatz_comparison"].name, "tfim_ansatz_comparison.csv")
        self.assertEqual(paths["grid_resolution"].name, "tfim_grid_resolution.csv")

    def test_tfim_research_campaign_writes_expected_files(self):
        with tempfile.TemporaryDirectory() as tempdir:
            result = run_tfim_research_campaign(pathlib.Path(tempdir) / "campaign", h_values=(0.0,))

            self.assertEqual(
                set(result["paths"]),
                {"reference_scan", "variational_scaling", "ansatz_comparison", "grid_resolution"},
            )
            for path in result["paths"].values():
                self.assertTrue(path.exists())

            self.assertEqual(result["row_counts"]["reference_scan"], 6)
            self.assertEqual(result["row_counts"]["variational_scaling"], 2)
            self.assertEqual(result["row_counts"]["ansatz_comparison"], 4)
            self.assertEqual(result["row_counts"]["grid_resolution"], 12)

    def test_tfim_campaign_summary_has_expected_structure(self):
        with tempfile.TemporaryDirectory() as tempdir:
            campaign_dir = pathlib.Path(tempdir) / "campaign"
            run_tfim_research_campaign(campaign_dir, h_values=(0.0,))
            result = build_campaign_summary(campaign_dir)

            self.assertEqual(
                set(result["row_counts"]),
                {"reference_scan", "variational_scaling", "ansatz_comparison", "grid_resolution"},
            )
            self.assertEqual(len(result["summary_rows"]), 2)
            for row in result["summary_rows"]:
                self.assertEqual(
                    set(row),
                    {
                        "n",
                        "h",
                        "variational_min_error",
                        "best_ansatz_type",
                        "best_ansatz_error",
                        "best_grid_depth",
                        "best_grid_size",
                        "best_grid_error",
                        "worst_grid_size",
                        "worst_grid_error",
                    },
                )
                self.assertIn(row["best_ansatz_type"], {"product_ry", "entangling_ry_cnot_ry"})
                self.assertIn(row["best_grid_depth"], {1, 2})
                self.assertIn(row["best_grid_size"], {"coarse", "medium", "fine"})
                self.assertIn(row["worst_grid_size"], {"coarse", "medium", "fine"})

    def test_tfim_campaign_summary_csv_has_expected_header(self):
        with tempfile.TemporaryDirectory() as tempdir:
            campaign_dir = pathlib.Path(tempdir) / "campaign"
            run_tfim_research_campaign(campaign_dir, h_values=(0.0,))
            result = build_campaign_summary(campaign_dir)
            path = pathlib.Path(tempdir) / "campaign_summary.csv"
            write_campaign_summary_csv(path, result["summary_rows"])
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,variational_min_error,best_ansatz_type,best_ansatz_error,best_grid_depth,best_grid_size,best_grid_error,worst_grid_size,worst_grid_error",
        )
        self.assertEqual(len(lines), 3)

    def test_qaoa_landscape_csv_has_expected_header(self):
        rows = qaoa_chain_landscape(num_qubits=8, num_gamma=2, num_beta=2)
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "qaoa.csv"
            write_qaoa_landscape_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "n,gamma,beta,energy")
        self.assertEqual(len(lines), 5)

    def test_qaoa_research_campaign_output_paths_are_stable(self):
        paths = qaoa_campaign_output_paths("qaoa_campaign")
        self.assertEqual(paths["grid_search"].name, "qaoa_grid_search.csv")
        self.assertEqual(paths["landscape"].name, "qaoa_chain_landscape.csv")

    def test_qaoa_research_campaign_writes_expected_files(self):
        with tempfile.TemporaryDirectory() as tempdir:
            result = run_qaoa_research_campaign(pathlib.Path(tempdir) / "campaign")
            self.assertEqual(set(result["paths"]), {"grid_search", "landscape"})
            for path in result["paths"].values():
                self.assertTrue(path.exists())
            self.assertEqual(result["row_counts"]["grid_search"], 2)
            self.assertEqual(result["row_counts"]["landscape"], 49)

    def test_qaoa_campaign_summary_has_expected_structure(self):
        with tempfile.TemporaryDirectory() as tempdir:
            campaign_dir = pathlib.Path(tempdir) / "campaign"
            run_qaoa_research_campaign(campaign_dir)
            result = build_qaoa_campaign_summary(campaign_dir)
            self.assertEqual(set(result["row_counts"]), {"grid_search", "landscape"})
            self.assertEqual(
                set(result["summary"]),
                {
                    "grid_search_best_num_qubits",
                    "grid_search_best_energy",
                    "grid_search_best_gamma",
                    "grid_search_best_beta",
                    "landscape_best_n",
                    "landscape_best_gamma",
                    "landscape_best_beta",
                    "landscape_best_energy",
                    "landscape_worst_energy",
                    "landscape_energy_span",
                },
            )
            self.assertGreaterEqual(result["summary"]["landscape_energy_span"], 0.0)

    def test_qaoa_campaign_summary_csv_has_expected_header(self):
        with tempfile.TemporaryDirectory() as tempdir:
            campaign_dir = pathlib.Path(tempdir) / "campaign"
            run_qaoa_research_campaign(campaign_dir)
            result = build_qaoa_campaign_summary(campaign_dir)
            path = pathlib.Path(tempdir) / "qaoa_campaign_summary.csv"
            write_qaoa_campaign_summary_csv(path, result["summary"])
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "grid_search_best_num_qubits,grid_search_best_energy,grid_search_best_gamma,grid_search_best_beta,landscape_best_n,landscape_best_gamma,landscape_best_beta,landscape_best_energy,landscape_worst_energy,landscape_energy_span",
        )
        self.assertEqual(len(lines), 2)

    def test_research_report_has_expected_structure(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tfim_dir = pathlib.Path(tempdir) / "tfim_campaign"
            qaoa_dir = pathlib.Path(tempdir) / "qaoa_campaign"
            run_tfim_research_campaign(tfim_dir, h_values=(0.0,))
            run_qaoa_research_campaign(qaoa_dir)
            report = build_research_report(tfim_input_dir=tfim_dir, qaoa_input_dir=qaoa_dir)
            self.assertEqual(set(report), {"tfim", "qaoa"})
            self.assertIn("best_variational_error", report["tfim"])
            self.assertIn("best_ansatz_type", report["tfim"])
            self.assertIn("best_energy", report["qaoa"])
            self.assertIn("landscape_energy_span", report["qaoa"])
            rows = report_rows(report)
            self.assertEqual(len(rows), 2)
            self.assertEqual({row["campaign"] for row in rows}, {"tfim", "qaoa"})

    def test_research_report_csv_has_expected_header(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tfim_dir = pathlib.Path(tempdir) / "tfim_campaign"
            qaoa_dir = pathlib.Path(tempdir) / "qaoa_campaign"
            run_tfim_research_campaign(tfim_dir, h_values=(0.0,))
            run_qaoa_research_campaign(qaoa_dir)
            report = build_research_report(tfim_input_dir=tfim_dir, qaoa_input_dir=qaoa_dir)
            rows = report_rows(report)
            path = pathlib.Path(tempdir) / "research_report.csv"
            write_research_report_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "campaign,file_count,best_metric_name,best_metric_value,context_a,context_b",
        )
        self.assertEqual(len(lines), 3)

    def test_statevector_size_rows_are_deterministic(self):
        rows = statevector_size_rows((8, 12, 16, 20, 24, 28, 30))
        self.assertEqual([row["wires"] for row in rows], [8, 12, 16, 20, 24, 28, 30])
        self.assertEqual(rows[0]["amplitudes"], 256)
        self.assertEqual(rows[0]["memory_bytes"], 4096)
        self.assertEqual(rows[0]["memory_gib"], "0.000 GiB")
        self.assertEqual(rows[-1]["amplitudes"], 1 << 30)
        self.assertEqual(rows[-1]["memory_bytes"], (1 << 30) * 16)
        self.assertEqual(rows[-1]["memory_gib"], "16.000 GiB")

    def test_performance_rows_have_stable_structure(self):
        rows = performance_rows((8, 12), repeats=1)
        self.assertEqual([row["wires"] for row in rows], [8, 12])
        for row in rows:
            self.assertEqual(row["repeats"], 1)
            self.assertGreaterEqual(row["elapsed_seconds"], 0.0)
            self.assertGreaterEqual(row["seconds_per_run"], 0.0)
            self.assertGreaterEqual(row["final_value"], -1.0)
            self.assertLessEqual(row["final_value"], 1.0)

    def test_internal_profile_rows_have_stable_structure(self):
        rows = profile_rows((8,), repeats=1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["wires"], 8)
        stage_names = [stage["stage"] for stage in rows[0]["stages"]]
        self.assertEqual(
            stage_names,
            [
                "single_qubit_gates",
                "cnot_chain",
                "pauli_word_expval",
                "tape_setup",
                "measurement_handling",
                "execute_path",
                "qnode_end_to_end",
            ],
        )
        for stage in rows[0]["stages"]:
            self.assertEqual(stage["repeats"], 1)
            self.assertGreaterEqual(stage["elapsed_seconds"], 0.0)
            self.assertGreaterEqual(stage["seconds_per_run"], 0.0)
        self.assertEqual(rows[0]["stages"][3]["operation_count"], 23)
        self.assertEqual(rows[0]["stages"][3]["measurement_count"], 1)
        measured_stages = rows[0]["stages"][2:]
        for stage in measured_stages:
            if "final_value" in stage:
                self.assertGreaterEqual(stage["final_value"], -1.0)
                self.assertLessEqual(stage["final_value"], 1.0)

    def test_mps_paulirot_demo_rows_have_expected_structure(self):
        rows = paulirot_demo_rows()
        self.assertEqual([row["case"] for row in rows], ["CZ_state_overlap", "PauliRot_XY", "IsingYY"])
        for row in rows:
            self.assertEqual(set(row), {"case", "mps_value", "reference_value", "abs_error"})
            self.assertGreaterEqual(row["abs_error"], 0.0)

    def test_mps_isingzz_quench_rows_have_expected_structure(self):
        rows = mps_isingzz_quench_rows(
            qubit_counts=(8,),
            h_values=(0.25,),
            dt=0.1,
            steps=2,
            max_bond_dim=4,
            svd_cutoff=1e-12,
        )
        self.assertEqual(
            [(row["n"], row["step"]) for row in rows],
            [(8, 0), (8, 1), (8, 2)],
        )
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "n",
                    "h",
                    "dt",
                    "step",
                    "time",
                    "max_bond_dim",
                    "svd_cutoff",
                    "expval_z0",
                    "expval_z0z1",
                },
            )
            self.assertGreaterEqual(row["expval_z0"], -1.0)
            self.assertLessEqual(row["expval_z0"], 1.0)
            self.assertGreaterEqual(row["expval_z0z1"], -1.0)
            self.assertLessEqual(row["expval_z0z1"], 1.0)

    def test_mps_isingzz_quench_csv_has_expected_header(self):
        rows = mps_isingzz_quench_rows(
            qubit_counts=(8,),
            h_values=(0.25,),
            dt=0.1,
            steps=1,
            max_bond_dim=4,
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "mps_isingzz_quench.csv"
            write_mps_isingzz_quench_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,h,dt,step,time,max_bond_dim,svd_cutoff,expval_z0,expval_z0z1",
        )
        self.assertEqual(len(lines), 3)

    def test_adaptive_tfim_vqe_demo_has_expected_structure(self):
        rows = adaptive_tfim_demo_rows()
        self.assertEqual(set(rows), {"exact", "mps", "comparison"})
        self.assertIn("energy", rows["exact"])
        self.assertIn("energy", rows["mps"])
        self.assertIn("abs_energy_error", rows["comparison"])

    def test_adaptive_tfim_vqe_scan_rows_have_expected_structure(self):
        rows = adaptive_tfim_vqe_scan_rows(
            qubit_counts=(6,),
            J_values=(1.0,),
            h_values=(0.5,),
            include_exact=True,
            mps_bond_dims=(2,),
            max_layers=2,
            steps=1,
        )
        self.assertEqual(
            set(rows[0]),
            {
                "n",
                "J",
                "h",
                "backend",
                "layer",
                "energy",
                "energy_per_site",
                "expval_x0",
                "expval_z0z1",
                "converged",
                "final_delta_energy",
                "max_bond_dim",
                "svd_cutoff",
            },
        )
        self.assertEqual({row["backend"] for row in rows}, {"qml", "mps"})

    def test_adaptive_tfim_vqe_scan_csv_has_expected_header(self):
        rows = adaptive_tfim_vqe_scan_rows(
            qubit_counts=(6,),
            J_values=(1.0,),
            h_values=(0.5,),
            include_exact=True,
            mps_bond_dims=(2,),
            max_layers=1,
            steps=1,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "adaptive_tfim_vqe_scan.csv"
            write_adaptive_tfim_vqe_scan_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "n,J,h,backend,layer,energy,energy_per_site,expval_x0,expval_z0z1,converged,final_delta_energy,max_bond_dim,svd_cutoff",
        )
        self.assertGreaterEqual(len(lines), 3)

    @unittest.skipIf(matplotlib is None, "matplotlib is not installed")
    def test_adaptive_tfim_report_generates_plot_files(self):
        rows = adaptive_tfim_vqe_scan_rows(
            qubit_counts=(6,),
            J_values=(1.0,),
            h_values=(0.5,),
            include_exact=True,
            mps_bond_dims=(2, 4),
            max_layers=2,
            steps=1,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            csv_path = pathlib.Path(tempdir) / "adaptive_tfim_vqe_scan.csv"
            output_dir = pathlib.Path(tempdir) / "report"
            report_csv = pathlib.Path(tempdir) / "adaptive_tfim_report.csv"
            write_adaptive_tfim_vqe_scan_csv(csv_path, rows)
            report = generate_adaptive_tfim_report(csv_path, output_dir)
            write_adaptive_tfim_report_csv(report_csv, report["comparison_rows"])
            self.assertTrue((output_dir / "adaptive_tfim_energy_vs_layer.png").exists())
            self.assertTrue((output_dir / "adaptive_tfim_energy_vs_layer.pdf").exists())
            self.assertTrue((output_dir / "adaptive_tfim_exact_vs_mps.png").exists())
            self.assertTrue((output_dir / "adaptive_tfim_exact_vs_mps.pdf").exists())
            self.assertTrue(report_csv.exists())

    @unittest.skipIf(matplotlib is None, "matplotlib is not installed")
    def test_imaginary_time_report_generates_plot_files(self):
        import subprocess
        import os
        with tempfile.TemporaryDirectory() as tempdir:
            repo_base = pathlib.Path(__file__).resolve().parents[1]
            script_path = repo_base / "examples" / "imaginary_time_tfim_report.py"
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{str(ROOT)}:" + env.get("PYTHONPATH", "")
            subprocess.run([sys.executable, str(script_path)], cwd=tempdir, env=env, check=True)
            self.assertTrue((pathlib.Path(tempdir) / "imaginary_tfim_report.csv").exists())
            self.assertTrue((pathlib.Path(tempdir) / "imaginary_tfim_energy_vs_step.png").exists())
            self.assertTrue((pathlib.Path(tempdir) / "imaginary_tfim_energy_vs_step.pdf").exists())
            self.assertTrue((pathlib.Path(tempdir) / "imaginary_tfim_exact_vs_mps.png").exists())
            self.assertTrue((pathlib.Path(tempdir) / "imaginary_tfim_exact_vs_mps.pdf").exists())
            self.assertTrue((pathlib.Path(tempdir) / "imaginary_tfim_error_vs_max_bond_dim.png").exists())
            self.assertTrue((pathlib.Path(tempdir) / "imaginary_tfim_error_vs_max_bond_dim.pdf").exists())

    def test_imaginary_time_scan_csv_has_expected_header(self):
        rows = imaginary_time_tfim_scan_rows(
            qubit_counts=(4,),
            J_values=(1.0,),
            h_values=(0.5,),
            include_exact=True,
            mps_bond_dims=(4,),
            delta_tau=0.02,
            steps=2,
            max_layers=2,
            svd_cutoff=1e-12,
            seed=123,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "imaginary_tfim_scan.csv"
            write_tfim_dynamics_scan_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "dynamics,n,J,h,backend,step,time,step_size,energy,energy_per_site,expval_x0,expval_z0z1,max_bond_dim,svd_cutoff",
        )
        self.assertGreaterEqual(len(lines), 3)

    def test_real_time_scan_rows_have_expected_structure(self):
        rows = real_time_tfim_scan_rows(
            qubit_counts=(4,),
            J_values=(1.0,),
            h_values=(0.5,),
            include_exact=True,
            mps_bond_dims=(4,),
            dt=0.05,
            steps=2,
            svd_cutoff=1e-12,
        )
        self.assertEqual(
            set(rows[0]),
            {
                "dynamics",
                "n",
                "J",
                "h",
                "backend",
                "step",
                "time",
                "step_size",
                "energy",
                "energy_per_site",
                "expval_x0",
                "expval_z0z1",
                "max_bond_dim",
                "svd_cutoff",
            },
        )
        self.assertEqual({row["backend"] for row in rows}, {"qml", "mps"})
        self.assertEqual({row["dynamics"] for row in rows}, {"real"})

    def test_real_time_scan_csv_has_expected_header(self):
        rows = real_time_tfim_scan_rows(
            qubit_counts=(4,),
            J_values=(1.0,),
            h_values=(0.5,),
            include_exact=True,
            mps_bond_dims=(4,),
            dt=0.05,
            steps=2,
            svd_cutoff=1e-12,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            path = pathlib.Path(tempdir) / "real_tfim_scan.csv"
            write_tfim_dynamics_scan_csv(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "dynamics,n,J,h,backend,step,time,step_size,energy,energy_per_site,expval_x0,expval_z0z1,max_bond_dim,svd_cutoff",
        )
        self.assertGreaterEqual(len(lines), 3)

    @unittest.skipIf(matplotlib is None, "matplotlib is not installed")
    def test_real_time_report_generates_plot_files(self):
        import os
        import subprocess

        with tempfile.TemporaryDirectory() as tempdir:
            repo_base = pathlib.Path(__file__).resolve().parents[1]
            script_path = repo_base / "examples" / "real_time_tfim_report.py"
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{str(ROOT)}:" + env.get("PYTHONPATH", "")
            subprocess.run([sys.executable, str(script_path)], cwd=tempdir, env=env, check=True)
            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_report.csv").exists())
            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_energy_vs_time.png").exists())
            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_energy_vs_time.pdf").exists())
            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_observables_vs_time.png").exists())
            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_observables_vs_time.pdf").exists())
            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_exact_vs_mps.png").exists())
            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_exact_vs_mps.pdf").exists())

    @unittest.skipIf(matplotlib is None, "matplotlib is not installed")
    def test_real_time_report_from_scan_csv_with_multiple_bonds(self):
        import os
        import subprocess

        with tempfile.TemporaryDirectory() as tempdir:
            repo_base = pathlib.Path(__file__).resolve().parents[1]
            scan_script = repo_base / "examples" / "real_time_tfim_scan.py"
            report_script = repo_base / "examples" / "real_time_tfim_report.py"
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{str(ROOT)}:" + env.get("PYTHONPATH", "")

            scan_csv = pathlib.Path(tempdir) / "real_tfim_scan.csv"
            subprocess.run(
                [sys.executable, str(scan_script), "--csv", str(scan_csv), "--mps-bonds", "4,8"],
                cwd=tempdir,
                env=env,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(report_script),
                    "--scan-csv",
                    str(scan_csv),
                    "--csv",
                    str(pathlib.Path(tempdir) / "real_tfim_report.csv"),
                    "--output-dir",
                    str(pathlib.Path(tempdir)),
                ],
                cwd=tempdir,
                env=env,
                check=True,
            )

            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_exact_vs_mps.png").exists())
            self.assertTrue((pathlib.Path(tempdir) / "real_tfim_exact_vs_mps.pdf").exists())


if __name__ == "__main__":
    unittest.main()
