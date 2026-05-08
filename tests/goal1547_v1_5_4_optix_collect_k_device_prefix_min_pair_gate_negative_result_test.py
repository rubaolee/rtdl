from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1547_v1_5_4_optix_collect_k_device_prefix_min_pair_gate_negative_result_2026-05-08.md"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py"


class Goal1547V154OptixCollectKDevicePrefixMinPairGateNegativeResultTest(unittest.TestCase):
    def test_report_records_rejected_min_pair_gate(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Rejected as an implementation path", text)
        self.assertIn("Base commit: `b2bc7023ce2ad1d6890d0aba0a8c51b285bbdfe5`", text)
        self.assertIn("Do not add `RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_MIN_PAIRS`", text)
        self.assertIn("0.156797", text)
        self.assertIn("0.142450", text)
        self.assertIn("does not authorize a public speedup claim", text)

    def test_rejected_env_flag_is_not_left_in_runtime_or_topology_model(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        probe = PROBE.read_text(encoding="utf-8")

        self.assertNotIn("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_MIN_PAIRS", api)
        self.assertNotIn("collect_k_device_prefix_min_pairs", api)
        self.assertNotIn("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_MIN_PAIRS", probe)


if __name__ == "__main__":
    unittest.main()
