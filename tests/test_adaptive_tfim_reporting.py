import pathlib
import sys
import tempfile
import unittest
from importlib.util import find_spec


ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import QML.PenQ as penq_package
from QML.PenQ.examples.adaptive_tfim_vqe_report import generate_adaptive_tfim_report
from QML.PenQ.examples.adaptive_tfim_vqe_scan import adaptive_tfim_vqe_scan_rows
from QML.PenQ.examples.adaptive_tfim_vqe_scan import write_adaptive_tfim_vqe_scan_csv
from QML.PenQ.examples.plotting_utils import save_required_figure_outputs


MATPLOTLIB_AVAILABLE = find_spec("matplotlib") is not None
README_PATH = pathlib.Path(penq_package.__file__).resolve().parent / "README.md"


class _MissingPdfFigure:
    def __init__(self, output_dir):
        self.output_dir = pathlib.Path(output_dir)

    def tight_layout(self):
        return None

    def savefig(self, path, dpi=None):
        path = pathlib.Path(path)
        if path.suffix == ".png":
            path.write_bytes(b"png")


class TestAdaptiveTFIMReporting(unittest.TestCase):
    def test_readme_contains_required_adaptive_sections_and_formulas(self):
        text = README_PATH.read_text(encoding="utf-8")
        self.assertIn("## Adaptive TFIM VQE: Mathematical Formulation", text)
        self.assertIn("## Mandatory Plot Outputs", text)
        self.assertIn("## Optional SciencePlots Without Runtime Dependency", text)
        self.assertIn("H = -J sum_i Z_i Z_{i+1} - h sum_i X_i", text)
        self.assertIn("E(theta) = <psi(theta)|H|psi(theta)>", text)
        self.assertIn("U_l(gamma_l, beta_l) = U_X(beta_l) U_ZZ(gamma_l)", text)
        self.assertIn("|psi_L> = prod_l U_l |+>^n", text)
        self.assertIn("Delta_L = E_{L-1}^* - E_L^*", text)
        self.assertIn("Delta_L <= tol or L == max_layers", text)
        self.assertIn("CNOT - RZ(2 gamma) - CNOT = exp(-i gamma Z⊗Z)", text)

    def test_plot_helper_raises_if_pdf_missing(self):
        with tempfile.TemporaryDirectory() as tempdir:
            fig = _MissingPdfFigure(tempdir)
            with self.assertRaisesRegex(RuntimeError, "missing required PDF"):
                save_required_figure_outputs(fig, tempdir, "broken_plot")

    @unittest.skipUnless(MATPLOTLIB_AVAILABLE, "matplotlib is not installed")
    def test_report_generates_required_png_and_pdf_pairs(self):
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
            write_adaptive_tfim_vqe_scan_csv(csv_path, rows)
            report = generate_adaptive_tfim_report(csv_path, output_dir)
            expected_stems = {
                "adaptive_tfim_energy_vs_layer",
                "adaptive_tfim_exact_vs_mps",
                "adaptive_tfim_error_vs_max_bond_dim",
            }
            for stem in expected_stems:
                self.assertTrue((output_dir / f"{stem}.png").exists())
                self.assertTrue((output_dir / f"{stem}.pdf").exists())
            self.assertEqual(len(report["files"]), 6)


if __name__ == "__main__":
    unittest.main()
