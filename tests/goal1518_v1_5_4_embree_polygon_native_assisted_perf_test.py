from pathlib import Path
import unittest

from scripts import goal1518_v1_5_4_embree_polygon_native_assisted_perf as goal1518


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1518_v1_5_4_embree_polygon_native_assisted_perf.py"
REPORT_JSON = ROOT / "docs" / "reports" / "goal1518_v1_5_4_embree_polygon_native_assisted_perf_2026-05-08.json"
REPORT_MD = ROOT / "docs" / "reports" / "goal1518_v1_5_4_embree_polygon_native_assisted_perf_2026-05-08.md"


def _payload() -> dict:
    return {
        "goal": "Goal1518",
        "status": "goal1518_embree_polygon_native_assisted_perf_recorded",
        "valid": True,
        "git_commit": "synthetic",
        "repeats": 3,
        "polygon_pair_overlap_area_rows": {
            "app": "polygon_pair_overlap_area_rows",
            "cases": [
                {
                    "copies": 8,
                    "rows": {"median_seconds": 0.02, "json_bytes_median": 200},
                    "summary": {
                        "output_mode": "summary",
                        "median_seconds": 0.01,
                        "speedup_vs_rows": 2.0,
                        "json_bytes_median": 100,
                        "json_reduction_vs_rows": 2.0,
                    },
                }
            ],
        },
        "polygon_set_jaccard": {
            "app": "polygon_set_jaccard",
            "cases": [
                {
                    "copies": 8,
                    "cpu_python_reference": {"median_seconds": 0.02, "json_bytes_median": 100},
                    "embree": {
                        "backend": "embree",
                        "median_seconds": 0.01,
                        "json_bytes_median": 100,
                        "speedup_vs_cpu_python_reference": 2.0,
                    },
                }
            ],
        },
        "timing_scope": "synthetic",
        "claim_flags": {
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_polygon_or_gis_claim_authorized": False,
            "broad_rtx_wording_authorized": False,
            "true_zero_copy_authorized": False,
            "stable_collect_k_promotion_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": "does not authorize public speedup wording",
    }


class Goal1518EmbreePolygonNativeAssistedPerfTest(unittest.TestCase):
    def test_script_exists(self):
        self.assertTrue(SCRIPT.exists())

    def test_validator_accepts_synthetic_payload(self):
        payload = _payload()
        self.assertIs(goal1518.validate_payload(payload), payload)
        markdown = goal1518.to_markdown(payload)
        self.assertIn("Goal 1518", markdown)
        self.assertIn("Polygon Pair Summary", markdown)
        self.assertIn("Polygon Set Jaccard", markdown)

    def test_validator_rejects_claim_expansion(self):
        payload = _payload()
        payload["claim_flags"]["broad_polygon_or_gis_claim_authorized"] = True
        with self.assertRaisesRegex(ValueError, "broad_polygon_or_gis_claim_authorized"):
            goal1518.validate_payload(payload)

    def test_validator_rejects_missing_polygon_cases(self):
        payload = _payload()
        payload["polygon_set_jaccard"]["cases"] = []
        with self.assertRaisesRegex(ValueError, "requires polygon pair and Jaccard"):
            goal1518.validate_payload(payload)

    def test_measured_artifacts_are_valid(self):
        self.assertTrue(REPORT_JSON.exists(), "Goal1518 measured JSON artifact must be tracked")
        self.assertTrue(REPORT_MD.exists(), "Goal1518 measured Markdown artifact must be tracked")
        import json

        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        goal1518.validate_payload(payload)
        self.assertTrue(payload["valid"])
        self.assertGreaterEqual(len(payload["polygon_pair_overlap_area_rows"]["cases"]), 3)
        self.assertGreaterEqual(len(payload["polygon_set_jaccard"]["cases"]), 3)
        pair_ratios = [
            case["summary"]["speedup_vs_rows"]
            for case in payload["polygon_pair_overlap_area_rows"]["cases"]
        ]
        jaccard_ratios = [
            case["embree"]["speedup_vs_cpu_python_reference"]
            for case in payload["polygon_set_jaccard"]["cases"]
        ]
        self.assertTrue(any(ratio > 1.0 for ratio in pair_ratios))
        self.assertTrue(any(ratio < 1.0 for ratio in jaccard_ratios))
        for value in payload["claim_flags"].values():
            self.assertFalse(value)
        markdown = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("polygon/GIS claims", markdown)
        self.assertIn("does not authorize public speedup wording", markdown)


if __name__ == "__main__":
    unittest.main()
