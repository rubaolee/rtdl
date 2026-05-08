from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1545_v1_5_4_optix_collect_k_device_prefix_pod_runner.py"


class Goal1545V154OptixCollectKDevicePrefixPodRunnerTest(unittest.TestCase):
    def test_runner_encodes_control_and_candidate_envs(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT", text)

    def test_runner_writes_comparison_and_claim_boundary(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("accepted_candidate_by_runner_rule", text)
        self.assertIn("candidate_total_ms", text)
        self.assertIn("control_total_ms", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
