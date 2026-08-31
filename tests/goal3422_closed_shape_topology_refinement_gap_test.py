from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3422_closed_shape_topology_refinement_gap_2026-06-04.md"
FUTURE_TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
CLOSED_SHAPE_TOPOLOGY = ROOT / "src" / "rtdsl" / "closed_shape_topology.py"


class Goal3422ClosedShapeTopologyRefinementGapTest(unittest.TestCase):
    def test_report_records_candidate_and_simple_ring_gaps(self):
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("RT device predicate candidates", report)
        self.assertIn("47,570", report)
        self.assertIn("0 missing, 308 extra", report)
        self.assertIn("CuPy simple-ring refine", report)
        self.assertIn("47,045", report)
        self.assertIn("217 missing, 0 extra", report)
        self.assertIn("97 mismatched groups", report)

    def test_report_rules_out_naive_topology_and_names_next_contract(self):
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("simple OR shared_face", report)
        self.assertIn("not a valid exact rule", report)
        self.assertIn("topology-aware closed-boundary refinement contract", report)
        self.assertIn("topology rows as caller-provided data", report)
        self.assertIn("not native app policy", report)
        self.assertIn("does not solve the exact predicate", report)

    def test_future_todo_and_helper_boundary_are_updated(self):
        todo = FUTURE_TODO.read_text(encoding="utf-8")
        source = CLOSED_SHAPE_TOPOLOGY.read_text(encoding="utf-8")

        self.assertIn("Goal3422", todo)
        self.assertIn("topology-aware closed-boundary refinement contract", todo)
        self.assertIn("simple-ring predicate", source)
        self.assertIn("matches_geos_topology_oracle", source)
        self.assertIn('"matches_geos_topology_oracle": False', source)


if __name__ == "__main__":
    unittest.main()
