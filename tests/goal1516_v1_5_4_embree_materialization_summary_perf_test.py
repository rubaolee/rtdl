from pathlib import Path
import unittest

from scripts import goal1516_v1_5_4_embree_materialization_summary_perf as goal1516


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1516_v1_5_4_embree_materialization_summary_perf.py"
REPORT_JSON = ROOT / "docs" / "reports" / "goal1516_v1_5_4_embree_materialization_summary_perf_2026-05-08.json"
REPORT_MD = ROOT / "docs" / "reports" / "goal1516_v1_5_4_embree_materialization_summary_perf_2026-05-08.md"


def _case(app: str) -> dict:
    return {
        "app": app,
        "copies": 8,
        "row_mode": {
            "median_sec": 0.02,
            "min_sec": 0.01,
            "max_sec": 0.03,
            "row_count": 16,
            "summary_row_count": 0,
        },
        "summary_mode": {
            "name": "summary",
            "median_sec": 0.01,
            "min_sec": 0.01,
            "max_sec": 0.02,
            "row_count": 0,
            "summary_row_count": 8,
            "native_continuation_active": True,
        },
        "parity_passed": True,
        "summary_speedup_vs_rows": 2.0,
        "materialized_rows_avoided": 16,
    }


def _payload() -> dict:
    return {
        "goal": "Goal1516",
        "status": "goal1516_embree_materialization_summary_perf_recorded",
        "valid": True,
        "git_commit": "synthetic",
        "host": "synthetic",
        "platform": "synthetic",
        "python": "synthetic",
        "embree_version": "synthetic",
        "embree_threads": {"requested": "auto"},
        "copies": [8],
        "repeats": 3,
        "warmups": 1,
        "cases": [_case("event_hotspot_screening"), _case("service_coverage_gaps")],
        "all_parity_passed": True,
        "timing_scope": "Python app function timing",
        "claim_flags": {
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rtx_wording_authorized": False,
            "true_zero_copy_authorized": False,
            "stable_collect_k_promotion_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": "does not authorize public speedup wording or true zero-copy wording",
    }


class Goal1516EmbreeMaterializationSummaryPerfTest(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_validator_accepts_synthetic_payload(self):
        payload = _payload()
        self.assertIs(goal1516.validate_payload(payload), payload)
        markdown = goal1516.to_markdown(payload)
        self.assertIn("Goal 1516", markdown)
        self.assertIn("Materialized rows avoided", markdown)
        self.assertIn("Claim Boundary", markdown)

    def test_validator_rejects_summary_row_materialization(self):
        payload = _payload()
        payload["cases"][0]["summary_mode"]["row_count"] = 1
        with self.assertRaisesRegex(ValueError, "avoid row materialization"):
            goal1516.validate_payload(payload)

    def test_validator_rejects_claim_expansion(self):
        payload = _payload()
        payload["claim_flags"]["public_speedup_wording_authorized"] = True
        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized"):
            goal1516.validate_payload(payload)

    def test_validator_rejects_aggregate_parity_mismatch(self):
        payload = _payload()
        payload["cases"][0]["parity_passed"] = False
        with self.assertRaisesRegex(ValueError, "aggregate parity"):
            goal1516.validate_payload(payload)

    def test_measured_artifacts_are_valid_when_present(self):
        self.assertTrue(REPORT_JSON.exists())
        self.assertTrue(REPORT_MD.exists())
        import json

        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        goal1516.validate_payload(payload)
        self.assertTrue(payload["valid"])
        self.assertTrue(payload["all_parity_passed"])
        self.assertEqual("lx1", payload["host"])
        self.assertEqual([256, 1024, 4096], payload["copies"])
        self.assertEqual(6, len(payload["cases"]))
        self.assertGreater(
            sum(int(case["materialized_rows_avoided"]) for case in payload["cases"]),
            0,
        )

        markdown = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Goal 1516", markdown)
        self.assertIn("event_hotspot_screening", markdown)
        self.assertIn("service_coverage_gaps", markdown)
        self.assertIn("does not authorize public speedup wording", markdown)


if __name__ == "__main__":
    unittest.main()
