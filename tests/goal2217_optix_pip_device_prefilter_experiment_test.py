from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2217_optix_pip_device_prefilter_experiment_2026-05-17.md"


class Goal2217OptixPipDevicePrefilterExperimentTest(unittest.TestCase):
    def test_device_prefilter_is_opt_in(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("device_prefilter", workloads)
        self.assertTrue(
            'std::getenv("RTDL_OPTIX_PIP_DEVICE_PREFILTER")' in workloads
            or 'std::getenv("RTDL_OPTIX_PIP_DISABLE_DEVICE_PREFILTER")' in workloads
        )

    def test_positive_only_path_prefilters_before_reporting_candidate(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        self.assertIn("uint32_t device_prefilter", core)
        self.assertIn("if (params.device_prefilter != 0u)", core)
        self.assertIn("if (!point_in_polygon(px, py, poly))", core)
        self.assertIn("optixReportIntersection(0.5f, 0u)", core)
        self.assertIn("host exact refinement", core)

    def test_report_keeps_experimental_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2217", text)
        self.assertIn("RTDL_OPTIX_PIP_DEVICE_PREFILTER", text)
        self.assertIn("Default behavior remains conservative", text)
        self.assertIn("app-agnostic", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
