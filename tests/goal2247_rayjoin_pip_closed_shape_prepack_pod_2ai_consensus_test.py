from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reports" / "goal2247_rayjoin_pip_closed_shape_prepack_pod_2ai_consensus_2026-05-17.md"
REPORT = ROOT / "docs" / "reports" / "goal2245_rayjoin_pip_closed_shape_prepack_pod_evidence_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2245_rayjoin_pip_closed_shape_prepack_same_query_pod_2026-05-17.json"
REVIEW = ROOT / "docs" / "reviews" / "goal2246_gemini_review_goal2245_pip_closed_shape_prepack_pod_evidence_2026-05-17.md"


class Goal2247RayjoinPipClosedShapePrepackPod2AiConsensusTest(unittest.TestCase):
    def test_consensus_links_evidence_and_review(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        for path in (REPORT, ARTIFACT, REVIEW):
            self.assertIn(str(path.relative_to(ROOT)).replace("\\", "/"), text)
        self.assertIn("Codex and Gemini agree", text)

    def test_consensus_records_narrow_numeric_result(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("100,000-query", text)
        self.assertIn("0.08343074284493923", text)
        self.assertIn("all_parity_vs_reference: true", text)
        self.assertIn("row_count_consistent: true", text)

    def test_boundary_remains_blocked_for_release_scale_claims(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("full RayJoin reproduction", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("paper-scale speedup claims", text)
        self.assertIn("v2.0 release readiness", text)


if __name__ == "__main__":
    unittest.main()
