import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal5035PublicPerfBoundaryGuardTest(unittest.TestCase):
    def test_public_rayjoin_docs_do_not_reintroduce_stale_regime_headlines(self):
        public_docs = [
            ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "README.md",
            ROOT / "docs" / "release_reports" / "v2_14" / "rayjoin_reproduction_packet.md",
        ]
        forbidden = [
            "Fresh/cold writer-free route",
            "Prepared/query-many writer-free route",
            "0.33-0.35s",
            "measured median about `0.44s`",
            "latest measured median about `0.44s`",
        ]
        required = [
            "Warm-process fresh writer-free route",
            "Prepared LSI base-session, six distinct query batches",
            "0.755s",
            "excludes cold Python/CUDA process startup",
        ]
        for path in public_docs:
            text = path.read_text(encoding="utf-8")
            for needle in forbidden:
                self.assertNotIn(needle, text, f"{path} reintroduced stale wording: {needle}")
            for needle in required:
                self.assertIn(needle, text, f"{path} is missing current bounded wording: {needle}")


if __name__ == "__main__":
    unittest.main()
