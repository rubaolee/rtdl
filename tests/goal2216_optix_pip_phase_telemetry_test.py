from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2216_optix_pip_phase_telemetry_2026-05-17.md"


class Goal2216OptixPipPhaseTelemetryTest(unittest.TestCase):
    def test_pip_profile_is_opt_in_and_names_all_phases(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn('std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_PROFILE")', text)
        self.assertIn("[rtdl_optix_point_primitive_anyhit_profile]", text)
        for field in (
            "host_pack_s",
            "upload_s",
            "accel_build_s",
            "count_pass_s",
            "write_pass_s",
            "compact_download_s",
            "exact_refine_s",
            "total_s",
            "candidates",
            "emitted",
        ):
            self.assertIn(field, text)

    def test_count_and_write_passes_are_measured_separately(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("pip_count_pass_s += seconds_between", text)
        self.assertIn("pip_write_pass_s += seconds_between", text)
        self.assertIn("pip_candidate_count += static_cast<size_t>(gpu_count)", text)
        self.assertIn("pip_refine_s = seconds_between", text)

    def test_report_preserves_diagnostic_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2216", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_PROFILE", text)
        self.assertIn("Default behavior is unchanged", text)
        self.assertIn("diagnostic infrastructure only", text)
        self.assertIn("does not authorize a performance claim", text)


if __name__ == "__main__":
    unittest.main()
