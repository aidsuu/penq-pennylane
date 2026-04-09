import argparse
import csv
from pathlib import Path

from QML.PenQ.examples.qaoa_campaign_summary import build_qaoa_campaign_summary
from QML.PenQ.examples.tfim_campaign_summary import build_campaign_summary
from QML.PenQ.examples.tfim_groundstate_ansatz import DEVICE_NAME


def build_research_report(tfim_input_dir=None, qaoa_input_dir=None):
    report = {}

    if tfim_input_dir is not None and Path(tfim_input_dir).exists():
        tfim_result = build_campaign_summary(tfim_input_dir)
        best_tfim_row = min(tfim_result["summary_rows"], key=lambda row: float(row["variational_min_error"]))
        report["tfim"] = {
            "file_count": len(tfim_result["row_counts"]),
            "row_counts": tfim_result["row_counts"],
            "best_variational_n": int(best_tfim_row["n"]),
            "best_variational_h": float(best_tfim_row["h"]),
            "best_variational_error": float(best_tfim_row["variational_min_error"]),
            "best_ansatz_type": best_tfim_row["best_ansatz_type"],
            "best_ansatz_error": float(best_tfim_row["best_ansatz_error"]),
        }

    if qaoa_input_dir is not None and Path(qaoa_input_dir).exists():
        qaoa_result = build_qaoa_campaign_summary(qaoa_input_dir)
        summary = qaoa_result["summary"]
        report["qaoa"] = {
            "file_count": len(qaoa_result["row_counts"]),
            "row_counts": qaoa_result["row_counts"],
            "best_num_qubits": int(summary["grid_search_best_num_qubits"]),
            "best_energy": float(summary["grid_search_best_energy"]),
            "best_gamma": float(summary["grid_search_best_gamma"]),
            "best_beta": float(summary["grid_search_best_beta"]),
            "landscape_best_energy": float(summary["landscape_best_energy"]),
            "landscape_energy_span": float(summary["landscape_energy_span"]),
        }

    return report


def report_rows(report):
    rows = []
    if "tfim" in report:
        tfim = report["tfim"]
        rows.append(
            {
                "campaign": "tfim",
                "file_count": int(tfim["file_count"]),
                "best_metric_name": "best_variational_error",
                "best_metric_value": float(tfim["best_variational_error"]),
                "context_a": f"n={tfim['best_variational_n']}",
                "context_b": f"h={tfim['best_variational_h']:.2f}",
            }
        )
    if "qaoa" in report:
        qaoa = report["qaoa"]
        rows.append(
            {
                "campaign": "qaoa",
                "file_count": int(qaoa["file_count"]),
                "best_metric_name": "best_energy",
                "best_metric_value": float(qaoa["best_energy"]),
                "context_a": f"gamma={qaoa['best_gamma']:.8f}",
                "context_b": f"beta={qaoa['best_beta']:.8f}",
            }
        )
    return rows


def write_research_report_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["campaign", "file_count", "best_metric_name", "best_metric_value", "context_a", "context_b"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Deterministic cross-campaign research report.")
    parser.add_argument("--tfim-dir", dest="tfim_dir", default=None, help="Optional TFIM campaign directory.")
    parser.add_argument("--qaoa-dir", dest="qaoa_dir", default=None, help="Optional QAOA campaign directory.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Optional CSV output path.")
    args = parser.parse_args()

    report = build_research_report(tfim_input_dir=args.tfim_dir, qaoa_input_dir=args.qaoa_dir)
    rows = report_rows(report)
    if args.csv_path is not None:
        write_research_report_csv(args.csv_path, rows)

    print(f"device={DEVICE_NAME}")
    print("workflow=Comparative research report")
    if "tfim" in report:
        tfim = report["tfim"]
        print(
            f"tfim: files={tfim['file_count']} rows={tfim['row_counts']} "
            f"best_var_err={tfim['best_variational_error']:.8f} "
            f"best_ansatz={tfim['best_ansatz_type']} best_ansatz_err={tfim['best_ansatz_error']:.8f}"
        )
    if "qaoa" in report:
        qaoa = report["qaoa"]
        print(
            f"qaoa: files={qaoa['file_count']} rows={qaoa['row_counts']} "
            f"best_energy={qaoa['best_energy']:.8f} "
            f"best_gamma={qaoa['best_gamma']:.8f} best_beta={qaoa['best_beta']:.8f} "
            f"landscape_span={qaoa['landscape_energy_span']:.8f}"
        )
    if args.csv_path is not None:
        print(f"csv={args.csv_path}")


if __name__ == "__main__":
    main()
