from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "docs" / "reviews" / "goal1607_v1_6_final_release_3ai_consensus_2026-05-09.md"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class Goal1607V16FinalReleaseConsensusTest(unittest.TestCase):
    def test_consensus_accepts_release_package_and_names_reviewed_commit(self):
        text = _flat(CONSENSUS)
        self.assertIn("Accepted for final public-release completion", text)
        self.assertIn("6477a55d Add v1.6 release package", text)
        self.assertIn("Codex, Claude, and Gemini agree", text)

    def test_consensus_preserves_release_statement_and_claim_boundary(self):
        text = _flat(CONSENSUS)
        for phrase in [
            "first Python+RTDL architecture milestone",
            "Python remains the app/control layer",
            "RTDL owns the supported RT-shaped primitive contract",
            "`ANY_HIT`, `COUNT_HITS`",
            "`REDUCE_FLOAT(MIN|MAX|SUM)`",
            "`REDUCE_INT(COUNT|SUM)`",
            "does not optimize arbitrary Python code or whole applications",
            "performance claims remain scoped to exact reviewed primitive subpaths",
        ]:
            self.assertIn(phrase, text)

    def test_consensus_records_validation_evidence(self):
        text = _flat(CONSENSUS)
        for phrase in [
            "Windows source-tree validation",
            "Ran 38 tests",
            "Linux source-tree validation",
            "NVIDIA GeForce GTX 1070, 580.126.09",
            "Ran 33 tests",
            "OK",
        ]:
            self.assertIn(phrase, text)

    def test_consensus_blocks_unsupported_claims(self):
        text = _flat(CONSENSUS)
        for phrase in [
            "package-install support",
            "arbitrary user-Python optimization",
            "whole-application speedup",
            "broad NVIDIA RTX/GPU acceleration",
            "true zero-copy support",
            "partner tensor handoff support",
            "stable `COLLECT_K_BOUNDED` promotion",
            "fully app-agnostic native internals",
        ]:
            self.assertIn(phrase, text)

    def test_consensus_requires_public_docs_update_before_tag(self):
        text = _flat(CONSENSUS)
        for phrase in [
            "update public front-door docs",
            "rerun the final v1.6 package/gate test slice",
            "create the annotated `v1.6` tag",
            "push `main` and the `v1.6` tag",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
