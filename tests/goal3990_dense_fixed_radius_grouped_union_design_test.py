import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3990_dense_fixed_radius_grouped_union_design_2026-06-08.md"
FUTURE_TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"


class Goal3990DenseFixedRadiusGroupedUnionDesignTest(unittest.TestCase):
    def test_design_names_generic_primitive_and_rejects_app_vocabulary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("fixed_radius_grouped_union_dense_3d", text)
        self.assertIn("must remain generic", text)
        self.assertIn("must not use native ABI names or native implementation vocabulary tied to DBSCAN", text)
        self.assertIn("epsilon/min-points semantics", text)

    def test_design_is_grounded_in_recent_probe_evidence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Goal3987",
            "Goal3988",
            "Goal3989",
            "20x",
            "86x",
            "1.24",
            "Atomics are not the sole bottleneck",
        ]:
            self.assertIn(fragment, text)

    def test_acceptance_criteria_include_parity_metadata_and_review(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "deterministic root/component policy",
            "Staleness/convergence metadata",
            "Same-contract parity tests",
            "Pod performance evidence",
            "Independent external review",
        ]:
            self.assertIn(fragment, text)

    def test_boundary_blocks_public_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "does not authorize release",
            "broad RT-core speedup wording",
            "true-zero-copy wording",
            "automatic backend/partner selection",
            "app-specific native-engine logic",
        ]:
            self.assertIn(fragment, text)

    def test_future_todo_captures_grouped_union_lesson(self) -> None:
        text = FUTURE_TODO.read_text(encoding="utf-8")
        for fragment in [
            "Dense Fixed-Radius Grouped Union",
            "Goal3989 added atomic telemetry",
            "fixed-radius pairs, groups, component roots",
            "must not encode DBSCAN",
        ]:
            self.assertIn(fragment, text)
        self.assertIn("atomics are not the sole bottleneck", text.lower())


if __name__ == "__main__":
    unittest.main()
