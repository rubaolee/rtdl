from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "reports" / "goal2408_codex_rt_dbscan_next_fight_plan_2026-05-19.md"
HANDOFF = ROOT / "docs" / "handoff" / "HANDOFF_CLAUDE_GOAL2408_RT_DBSCAN_NEXT_FIGHT_REVIEW_2026-05-19.md"


def _compact(text: str) -> str:
    return " ".join(text.split())


class Goal2408RtDbscanNextFightPlanTest(unittest.TestCase):
    def test_plan_records_positive_and_negative_evidence(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")

        self.assertIn("Goal2405 is the current positive result", plan)
        self.assertIn("Goal2407 is the current negative result", plan)
        self.assertIn("raw any-hit atomic union is not the continuation primitive", plan)
        self.assertIn("RTDL can use RT cores to classify fixed-radius core points", plan)

    def test_plan_recommends_generic_cell_graph_continuation(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        compact = _compact(plan).lower()

        self.assertIn("Candidate B: Generic Cell-Graph All-Core Continuation", plan)
        self.assertIn("best next fight", plan)
        self.assertIn("radius_graph_components_3d_cupy_cell_graph_partner_columns", plan)
        self.assertIn("optix_rt_core_flags_cupy_cell_graph_components_3d", plan)
        self.assertIn("fall back to the existing cupy grid continuation", compact)

    def test_plan_preserves_app_agnostic_boundary(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        compact = _compact(plan)

        self.assertIn("Disallowed native direction", plan)
        self.assertIn("DBSCAN cluster expansion hard-coded into OptiX", plan)
        self.assertIn("app-specific neighborhood semantics", plan)
        self.assertIn("The engine must remain app-agnostic throughout", compact)

    def test_claude_handoff_is_executable_and_bounded(self) -> None:
        handoff = HANDOFF.read_text(encoding="utf-8")

        self.assertIn("goal2409_claude_review_goal2408_rt_dbscan_next_fight_plan_2026-05-19.md", handoff)
        self.assertIn("Does the proposed direction preserve the app-agnostic RTDL engine boundary", handoff)
        self.assertIn("accept-with-boundary", handoff)
        self.assertIn("Do not recommend adding a", handoff)
        self.assertIn("DBSCAN-shaped native ABI", handoff)


if __name__ == "__main__":
    unittest.main()
