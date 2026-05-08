from pathlib import Path
import unittest

from scripts import goal1517_v1_5_4_embree_prepared_summary_reuse_perf as goal1517


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1517_v1_5_4_embree_prepared_summary_reuse_perf.py"
REPORT_JSON = ROOT / "docs" / "reports" / "goal1517_v1_5_4_embree_prepared_summary_reuse_perf_2026-05-08.json"
REPORT_MD = ROOT / "docs" / "reports" / "goal1517_v1_5_4_embree_prepared_summary_reuse_perf_2026-05-08.md"


def _app_payload() -> dict:
    return {
        "one_shot": {"median_sec": 0.02, "row_count": 8},
        "prepare_sec": 0.01,
        "prepared_run_only": {"median_sec": 0.01, "row_count": 8},
        "prepared_speedup_vs_one_shot": 2.0,
    }


def _payload() -> dict:
    return {
        "goal": "Goal1517",
        "status": "goal1517_embree_prepared_summary_reuse_perf_recorded",
        "valid": True,
        "git_commit": "synthetic",
        "source_goal": 718,
        "host": "synthetic",
        "platform": "synthetic",
        "python": "synthetic",
        "embree_version": "synthetic",
        "embree_threads": {"requested": "auto"},
        "copies": [8],
        "repeats": 3,
        "warmups": 1,
        "cases": [
            {
                "copies": 8,
                "outlier_point_count": 8,
                "dbscan_point_count": 8,
                "outlier": _app_payload(),
                "dbscan": _app_payload(),
            }
        ],
        "timing_scope": "synthetic",
        "claim_flags": {
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rtx_wording_authorized": False,
            "true_zero_copy_authorized": False,
            "stable_collect_k_promotion_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": "does not authorize public speedup wording",
    }


class Goal1517EmbreePreparedSummaryReusePerfTest(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_validator_accepts_synthetic_payload(self):
        payload = _payload()
        self.assertIs(goal1517.validate_payload(payload), payload)
        markdown = goal1517.to_markdown(payload)
        self.assertIn("Goal 1517", markdown)
        self.assertIn("Prepared/one-shot ratio", markdown)
        self.assertIn("Claim Boundary", markdown)

    def test_validator_rejects_claim_expansion(self):
        payload = _payload()
        payload["claim_flags"]["true_zero_copy_authorized"] = True
        with self.assertRaisesRegex(ValueError, "true_zero_copy_authorized"):
            goal1517.validate_payload(payload)

    def test_validator_rejects_missing_prepared_summary_rows(self):
        payload = _payload()
        payload["cases"][0]["outlier"]["prepared_run_only"]["row_count"] = 0
        with self.assertRaisesRegex(ValueError, "per-point summary rows"):
            goal1517.validate_payload(payload)

    def test_measured_artifacts_are_valid_when_present(self):
        if not REPORT_JSON.exists() or not REPORT_MD.exists():
            self.skipTest("Goal1517 measured artifacts are not present yet")
        import json

        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        goal1517.validate_payload(payload)
        self.assertTrue(payload["valid"])
        self.assertEqual("Goal1517", payload["goal"])
        self.assertGreaterEqual(len(payload["cases"]), 1)
        markdown = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("outlier", markdown)
        self.assertIn("dbscan", markdown)
        self.assertIn("does not authorize public speedup wording", markdown)


if __name__ == "__main__":
    unittest.main()
