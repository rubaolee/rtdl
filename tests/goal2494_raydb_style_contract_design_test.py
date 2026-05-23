from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2494_raydb_style_contract_design_2026-05-22.md"


class Goal2494RaydbStyleContractDesignTest(unittest.TestCase):
    def test_contract_defines_columnar_prepared_boundary(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "ColumnarRecordSet",
            "AxisEncodingPlan",
            "PredicateRangeSet",
            "GroupSlotMap",
            "AggregatePlan",
            "PreparedAxisScene",
            "GroupedAggregateResult",
        ]:
            self.assertIn(phrase, text)

    def test_native_engine_vocabulary_stays_app_agnostic(self) -> None:
        text = REPORT.read_text()
        self.assertIn("Use database terms only in Python benchmark/app code and docs", text)
        self.assertIn("Native Embree and\nOptiX implementation paths", text)
        for forbidden in ["RayDB", "SQL", "SSB", "database operators"]:
            self.assertIn(forbidden, text)
        self.assertIn("native database-specific ABI", text)

    def test_first_slice_excludes_full_dbms_features(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "no disjunction",
            "no joins",
            "no subqueries",
            "no nullable three-valued SQL logic",
            "Materialized row output is out of scope",
        ]:
            self.assertIn(phrase, text)

    def test_goal2495_starting_point_is_cpu_reference_only(self) -> None:
        text = REPORT.read_text()
        self.assertIn("Goal2495 should implement only the CPU reference and fixture", text)
        self.assertIn("no Embree, OptiX, or authors-code timing", text)
        self.assertIn("two queries: one grouped count and one grouped sum", text)

    def test_known_failure_modes_are_recorded(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "hot atomic slot",
            "too many groups",
            "duplicate primitive hits",
            "row materialization",
            "online BVH rebuilds",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
