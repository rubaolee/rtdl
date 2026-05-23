from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / "docs/reports/goal2551_codex_rethinking_benchmark_app_wave_2026-05-23.md"
GEMINI = ROOT / "docs/reports/goal2551_gemini_rethinking_benchmark_app_wave_2026-05-23.md"
CLAUDE = ROOT / "docs/reports/goal2551_claude_rethinking_benchmark_app_wave_2026-05-23.md"
CONSENSUS = ROOT / "docs/reports/goal2551_codex_gemini_claude_consensus_benchmark_app_wave_2026-05-23.md"


class Goal2551BenchmarkAppWaveRethinkingConsensusTest(unittest.TestCase):
    def test_three_reviews_exist_and_have_verdicts(self) -> None:
        for path in (CODEX, GEMINI, CLAUDE):
            with self.subTest(path=path.name):
                text = path.read_text()
                self.assertGreater(len(text), 1000)
                self.assertIn("internal", text.lower())
                self.assertIn("public", text.lower())
                self.assertIn("engine", text.lower())

    def test_consensus_records_p0_engine_purity_and_capacity_work(self) -> None:
        text = CONSENSUS.read_text()
        for phrase in [
            "internal-benchmark-apps-2026-05-23",
            "Native Naming And ABI Purity",
            "Capacity/Overflow Contract Fix",
            "RtdlDbField",
            "DbScanPipeline",
            "overflowed_out",
            "Unified Columnar Device ABI",
            "Shared Grouped-Reduction Substrate",
            "not complete enough for public release",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_consensus_preserves_barnes_hut_native_boundary(self) -> None:
        text = CONSENSUS.read_text()
        self.assertIn("Goal2549", text)
        self.assertIn("inverse-square force math", text)
        self.assertIn("not be fused into native OptiX", text)
        self.assertIn("reviewed operator plug-in or partner mechanism", text)


if __name__ == "__main__":
    unittest.main()
