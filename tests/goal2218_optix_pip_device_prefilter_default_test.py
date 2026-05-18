from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2218_optix_pip_device_prefilter_default_2026-05-17.md"


class Goal2218OptixPipDevicePrefilterDefaultTest(unittest.TestCase):
    def test_positive_only_pip_enables_device_prefilter_by_default(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_DEVICE_PREFILTER", text)
        self.assertIn("positive_only != 0u", text)
        self.assertIn("device_prefilter =", text)
        self.assertNotIn('std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DEVICE_PREFILTER") != nullptr ? 1u : 0u', text)

    def test_report_documents_default_and_opt_out_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2218", text)
        self.assertIn("promotes the device prefilter to the default", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_DEVICE_PREFILTER=1", text)
        self.assertIn("host exact refinement", text)
        self.assertIn("does not by itself authorize a public performance claim", text)


if __name__ == "__main__":
    unittest.main()
