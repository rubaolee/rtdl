from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2222_optix_pip_one_pass_compact_experiment_2026-05-17.md"


class Goal2222OptixPipOnePassCompactExperimentTest(unittest.TestCase):
    def test_one_pass_compact_has_opt_out_and_overflow_fallback(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_PIP_DISABLE_ONE_PASS_COMPACT", text)
        self.assertIn("pip_one_pass_compact", text)
        self.assertIn("allow_overflow", text)
        self.assertIn("pip_fallback_chunks", text)
        self.assertIn("gpu_count <= optimistic_capacity", text)
        self.assertIn("PIP positive-hit candidate count changed between count and write passes", text)

    def test_profile_reports_one_pass_and_fallback_chunks(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("one_pass=%u", text)
        self.assertIn("fallback_chunks=%zu", text)

    def test_report_preserves_experimental_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2222", text)
        self.assertIn("one-pass optimistic compact writer", text)
        self.assertIn("RTDL_OPTIX_PIP_DISABLE_ONE_PASS_COMPACT=1", text)
        self.assertIn("overflow fallback", text)
        self.assertIn("does not authorize a performance claim", text)


if __name__ == "__main__":
    unittest.main()
