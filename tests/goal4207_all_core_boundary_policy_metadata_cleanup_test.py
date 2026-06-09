import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
REPORT = ROOT / "docs" / "reports" / "goal4207_all_core_boundary_policy_metadata_cleanup_2026-06-09.md"


class Goal4207AllCoreBoundaryPolicyMetadataCleanupTest(unittest.TestCase):
    def test_all_core_fast_path_fills_policy_metadata(self) -> None:
        text = ADAPTERS.read_text(encoding="utf-8")
        numba_start = text.index("class PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D")
        text = text[numba_start:]
        marker = "optix_applies_all_items_grouped_union_without_predicate_or_fallback_workspace"
        self.assertIn(marker, text)
        before_marker = text[: text.index(marker)]
        self.assertIn('"boundary_assignment_policy": self.boundary_assignment_policy', before_marker)
        self.assertIn('"boundary_assignment_pass_count": 1', before_marker)
        self.assertIn('"fallback_candidate_policy": "not_needed_all_items_satisfy_predicate"', before_marker)

    def test_report_bounds_change_to_metadata_cleanup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("metadata cleanup only", text)
        self.assertIn("does not change labels", text)
        self.assertIn("Rerun a dense all-core fixture", text)


if __name__ == "__main__":
    unittest.main()
