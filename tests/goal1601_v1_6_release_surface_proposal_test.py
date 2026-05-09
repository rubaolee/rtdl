from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "docs" / "reports" / "goal1601_v1_6_release_surface_proposal_2026-05-09.md"


class Goal1601V16ReleaseSurfaceProposalTest(unittest.TestCase):
    def test_proposal_exists_and_defines_python_rtdl_surface(self):
        self.assertTrue(PROPOSAL.exists())
        text = " ".join(PROPOSAL.read_text(encoding="utf-8").split())
        for phrase in [
            "first historical Python+RTDL public closure milestone",
            "Python remains the app/control layer",
            "RTDL owns the RT-shaped primitive contract",
            "native Embree/OptiX execution",
            "reviewed RT primitive subpaths",
        ]:
            self.assertIn(phrase, text)

    def test_proposal_keeps_performance_priority_without_overclaiming(self):
        text = " ".join(PROPOSAL.read_text(encoding="utf-8").split())
        for phrase in [
            "architecture anchor, not a performance freeze",
            "NVIDIA RT-core performance",
            "`COLLECT_K_BOUNDED` optimization",
            "true device-memory/zero-copy evidence",
            "No future performance claim should be broadened merely because `v1.6` exists",
            "exact-subpath evidence and external review",
        ]:
            self.assertIn(phrase, text)

    def test_proposal_blocks_release_and_public_claims(self):
        text = " ".join(PROPOSAL.read_text(encoding="utf-8").split())
        for phrase in [
            "This statement should not be used until the remaining closure gates pass",
            "do not publish it yet",
            "`v1.6` release",
            "release tag action",
            "stable `COLLECT_K_BOUNDED` promotion",
            "public speedup wording",
            "whole-app speedup wording",
            "broad RTX/GPU acceleration wording",
            "true zero-copy wording",
            "partner support claims",
            "package-install claims",
        ]:
            self.assertIn(phrase, text)
        for forbidden in [
            "authorizes `v1.6` release",
            "authorizes release tag action",
            "authorizes public speedup wording",
            "authorizes true zero-copy wording",
            "approves stable `COLLECT_K_BOUNDED` promotion",
            "approves partner support claims",
        ]:
            self.assertNotIn(forbidden, text)

    def test_proposal_couples_included_and_excluded_surfaces(self):
        text = " ".join(PROPOSAL.read_text(encoding="utf-8").split())
        for phrase in [
            "This included surface must always be read together with the Pending Or Excluded Surface section",
            "naming OptiX as an active backend does not imply that every `--backend optix` run is a NVIDIA RT-core speedup",
        ]:
            self.assertIn(phrase, text)

    def test_proposal_names_required_closure_gates(self):
        text = " ".join(PROPOSAL.read_text(encoding="utf-8").split())
        for phrase in [
            "Public docs overclaim audit",
            "Stable native-path app-leakage audit",
            "Windows source-tree validation",
            "Linux source-tree validation",
            "Real NVIDIA OptiX validation",
            "3-AI consensus",
            "Explicit user authorization",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
