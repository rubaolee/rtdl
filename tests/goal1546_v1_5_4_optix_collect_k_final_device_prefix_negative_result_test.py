from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1546_v1_5_4_optix_collect_k_final_device_prefix_negative_result_2026-05-08.md"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py"


class Goal1546V154OptixCollectKFinalDevicePrefixNegativeResultTest(unittest.TestCase):
    def test_report_records_rejected_final_prefix_path(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Rejected as an implementation path", text)
        self.assertIn("Base commit: `c50555fb32936ffce353b1b5e8ff20631e716ef6`", text)
        self.assertIn("Do not add `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_FINAL_COMPACT`", text)
        self.assertIn("0.475852", text)
        self.assertIn("0.492944", text)
        self.assertIn("does not authorize a public speedup claim", text)

    def test_rejected_env_flag_is_not_left_in_runtime_or_topology_model(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        probe = PROBE.read_text(encoding="utf-8")

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_FINAL_COMPACT", api)
        self.assertNotIn("collect_k_use_device_prefix_final_compact", api)
        self.assertNotIn("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_FINAL_COMPACT", probe)


if __name__ == "__main__":
    unittest.main()
