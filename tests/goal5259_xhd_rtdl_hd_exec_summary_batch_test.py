from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_PATH = APP_DIR / "scripts" / "run_xhd_rtdl_hd_exec_summary_batch.py"
FIXTURE_A = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_a.wkt"
FIXTURE_B = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_b.wkt"


def _load_runner():
    spec = importlib.util.spec_from_file_location("xhd_rtdl_hd_exec_summary_batch", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5259XhdRtdlHdExecSummaryBatchTest(unittest.TestCase):
    def test_batch_bridge_drives_hd_exec_entrypoint_from_case_summary(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "cases.json"
            out = Path(tmp) / "summary.json"
            source.write_text(
                json.dumps(
                    {
                        "schema": "test.case_summary.v1",
                        "cases": [
                            {
                                "case_name": "directed2d_asymmetric",
                                "public_paths": [str(FIXTURE_A), str(FIXTURE_B)],
                                "author_normalized": {"hd_result": 0.5},
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            rc = runner.main(
                [
                    "--case-summary",
                    str(source),
                    "--summary",
                    str(out),
                    "--max-cases",
                    "1",
                    "--rtdl-route",
                    "public-columnar",
                    "--n-dims",
                    "2",
                    "--input-type",
                    "wkt",
                    "--execution",
                    "cpu",
                ]
            )
            summary = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.rtdl_hd_exec_summary_batch.v1")
        self.assertEqual(summary["selected_case_count"], 1)
        self.assertEqual(summary["matched_case_count"], 1)
        self.assertTrue(summary["all_cases_matched"])
        case = summary["cases"][0]
        self.assertEqual(case["case_name"], "directed2d_asymmetric")
        self.assertEqual(case["route_label"], "public-columnar")
        self.assertAlmostEqual(case["rtdl_hd_result"], 0.5)
        self.assertAlmostEqual(case["author_abs_diff"], 0.0)
        self.assertTrue(case["matched_author"])
        self.assertIn("RTDL route wall time", case["running_time_semantics"])
        self.assertFalse(summary["claim_boundary"]["bulk_all400_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["author_performance_parity_claimed"])

    def test_missing_public_paths_fail_closed(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "bad.json"
            out = Path(tmp) / "summary.json"
            source.write_text(json.dumps({"cases": [{"case_name": "bad"}]}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "public_paths"):
                runner.main(["--case-summary", str(source), "--summary", str(out)])


if __name__ == "__main__":
    unittest.main()
