from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal2326ExamplesRecipeBoundaryTest(unittest.TestCase):
    def test_examples_do_not_import_app_shaped_core_facades(self) -> None:
        forbidden = [
            "rtdsl.geo",
            "rtdsl.robotics",
            "rt.geo",
            "rt.robotics",
            "road_hazard_priority(",
            "rt.rayjoin",
            "rt.hausdorff",
        ]
        offenders: list[str] = []
        for path in (ROOT / "examples" / "v2_0").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)}: {token}")
        self.assertEqual(offenders, [])

    def test_goal2326_report_records_contract_first_boundary(self) -> None:
        report = ROOT / "docs" / "reports" / "goal2326_contract_first_primitive_reconstruction_plan_2026-05-18.md"
        text = report.read_text(encoding="utf-8")
        for phrase in [
            "RTDL is not an app library",
            "No public core API like `rtdsl.geo.road_hazard_priority(...)`",
            "ExecutionPolicy",
            "ExecutionReport",
            "rtdsl.adapters.traversal",
            "app recipes stay in docs/examples",
        ]:
            self.assertIn(phrase, text)

    def test_dsl_reference_teaches_execution_report_boundary(self) -> None:
        text = (ROOT / "docs" / "rtdl" / "dsl_reference.md").read_text(encoding="utf-8")
        for phrase in [
            "Contract-First Public Surface",
            "RTDL v2.0 treats the language as a set of generic contracts",
            "rt.ExecutionPolicy",
            "rt.ExecutionReport",
            "selected backend",
            "claim boundaries",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
