from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal1479GpuMemoryArchitectureConsensusTest(unittest.TestCase):
    def test_architecture_consensus_artifacts_exist(self) -> None:
        for relative_path in (
            "docs/reports/goal1479_gpu_memory_architecture_python_rtdl_vs_partner_rtdl_2026-05-07.md",
            "docs/handoff/goal1479_gpu_memory_architecture_external_review_request_2026-05-07.md",
            "docs/reports/claude_goal1479_gpu_memory_architecture_review_2026-05-07.md",
            "docs/reports/gemini_goal1479_gpu_memory_architecture_review_2026-05-07.md",
            "docs/reports/three_ai_goal1479_gpu_memory_architecture_consensus_2026-05-07.md",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())

    def test_architecture_report_separates_python_rtdl_and_partner_rtdl(self) -> None:
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal1479_gpu_memory_architecture_python_rtdl_vs_partner_rtdl_2026-05-07.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(report.split())

        self.assertIn("Python+RTDL", report)
        self.assertIn("Python+partner+RTDL", report)
        self.assertIn("RTDL itself becomes the memory owner or memory manager", report)
        self.assertIn("RTDL should not replace that memory manager", report)
        self.assertIn("true zero-copy is not automatic", normalized)

    def test_consensus_keeps_claims_blocked(self) -> None:
        consensus = (
            ROOT
            / "docs"
            / "reports"
            / "three_ai_goal1479_gpu_memory_architecture_consensus_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Claude: `ACCEPT`", consensus)
        self.assertIn("Gemini: `ACCEPT`", consensus)
        self.assertIn("not a performance or release claim", consensus)
        self.assertIn("does not authorize true zero-copy", consensus)
        self.assertIn("public speedup wording", consensus)
        self.assertIn("partner tensor handoff", consensus)
        self.assertIn("release action", consensus)


if __name__ == "__main__":
    unittest.main()
