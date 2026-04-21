import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal699_rtx_profile_report.py"


def _case(app, path, total, backend, matches=True):
    return {
        "app": app,
        "path": path,
        "phase_stats": {
            "total": {"median_sec": total, "min_sec": total, "max_sec": total},
            "backend_execute_or_materialize_rows": {
                "median_sec": backend,
                "min_sec": backend,
                "max_sec": backend,
            },
        },
        "last_output": {
            "matches_oracle": matches,
            "neighbor_row_count": 0 if path in {"rt_count_threshold", "rt_core_flags"} else 16,
            "native_summary_row_count": 8 if path in {"rt_count_threshold", "rt_core_flags"} else 0,
        },
    }


class Goal699RtxProfileReportTest(unittest.TestCase):
    def test_report_computes_ratios_and_keeps_speedup_review_gated(self):
        profile = {
            "goal": "Goal697 OptiX fixed-radius app-level phase profiler",
            "backend": "optix",
            "mode": "optix",
            "copies": 128,
            "iterations": 5,
            "classification_change": False,
            "rtx_speedup_claim": False,
            "cases": [
                _case("outlier_detection", "rows", 4.0, 3.0),
                _case("outlier_detection", "rt_count_threshold", 2.0, 1.0),
                _case("dbscan_clustering", "rows", 8.0, 6.0),
                _case("dbscan_clustering", "rt_core_flags", 4.0, 2.0),
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            profile_path = Path(td) / "profile.json"
            env_path = Path(td) / "env.txt"
            output_path = Path(td) / "report.md"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            env_path.write_text("GPU: NVIDIA L4\n", encoding="utf-8")
            subprocess.check_call(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--profile-json",
                    str(profile_path),
                    "--environment",
                    str(env_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
            )
            text = output_path.read_text(encoding="utf-8")
        self.assertIn("eligible_for_rtx_claim_review: `true`", text)
        self.assertIn("| outlier_detection | 4.000000 | 2.000000 | 2.000 |", text)
        self.assertIn("| dbscan_clustering | 8.000000 | 4.000000 | 2.000 |", text)
        self.assertIn("does not by itself upgrade RTDL's public OptiX app classification", text)

    def test_dry_run_report_is_not_eligible_for_rtx_claim_review(self):
        profile = {
            "goal": "Goal697 OptiX fixed-radius app-level phase profiler",
            "backend": "cpu_python_reference_dry_run",
            "mode": "dry-run",
            "copies": 1,
            "iterations": 1,
            "classification_change": False,
            "rtx_speedup_claim": False,
            "cases": [
                _case("outlier_detection", "rows", 4.0, 3.0),
                _case("outlier_detection", "rt_count_threshold", 2.0, 1.0),
                _case("dbscan_clustering", "rows", 8.0, 6.0),
                _case("dbscan_clustering", "rt_core_flags", 4.0, 2.0),
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            profile_path = Path(td) / "profile.json"
            output_path = Path(td) / "report.md"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            subprocess.check_call(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--profile-json",
                    str(profile_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
            )
            text = output_path.read_text(encoding="utf-8")
        self.assertIn("eligible_for_rtx_claim_review: `false`", text)
        self.assertIn("Dry-run or GTX 1070 data must remain correctness/instrumentation evidence", text)

    def test_report_surfaces_oracle_failures_as_validation_errors(self):
        profile = {
            "goal": "Goal697 OptiX fixed-radius app-level phase profiler",
            "backend": "optix",
            "mode": "optix",
            "cases": [
                _case("outlier_detection", "rows", 4.0, 3.0, matches=False),
                _case("outlier_detection", "rt_count_threshold", 2.0, 1.0),
                _case("dbscan_clustering", "rows", 8.0, 6.0),
                _case("dbscan_clustering", "rt_core_flags", 4.0, 2.0),
            ],
            "classification_change": False,
            "rtx_speedup_claim": False,
        }
        with tempfile.TemporaryDirectory() as td:
            profile_path = Path(td) / "profile.json"
            output_path = Path(td) / "report.md"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            subprocess.check_call(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--profile-json",
                    str(profile_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
            )
            text = output_path.read_text(encoding="utf-8")
        self.assertIn("oracle_parity: `false`", text)
        self.assertIn("Validation Errors", text)
        self.assertIn("did not preserve oracle parity", text)


if __name__ == "__main__":
    unittest.main()
