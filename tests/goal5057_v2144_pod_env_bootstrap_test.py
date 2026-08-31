from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "goal5057_v2144_pod_env_bootstrap.sh"
RUNNER = ROOT / "scripts" / "goal5057_v2144_strict_pod_smoke_with_env.sh"
ENV_JSON = ROOT / "history" / "internal_docs" / "goal5057_v2144_pod_env_bootstrap_result.json"
SMOKE_JSON = ROOT / "history" / "internal_docs" / "goal5052_v2144_public_api_pod_smoke_result.json"


class Goal5057V2144PodEnvBootstrapTest(unittest.TestCase):
    def test_bootstrap_pins_cuda_numba_stack_and_writes_exports(self) -> None:
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("NUMPY_VERSION=\"${RTDL_V2144_NUMPY_VERSION:-2.2.6}\"", text)
        self.assertIn("NUMBA_VERSION=\"${RTDL_V2144_NUMBA_VERSION:-0.61.2}\"", text)
        self.assertIn("CUDA_NVCC_VERSION=\"${RTDL_V2144_CUDA_NVCC_VERSION:-12.4.131}\"", text)
        self.assertIn("CUDA_NVRTC_VERSION=\"${RTDL_V2144_CUDA_NVRTC_VERSION:-12.4.127}\"", text)
        self.assertIn("NVJITLINK_VERSION=\"${RTDL_V2144_NVJITLINK_VERSION:-12.4.127}\"", text)
        self.assertIn("export CUDA_HOME=", text)
        self.assertIn("export CUDA_PATH=", text)
        self.assertIn("export LD_LIBRARY_PATH=", text)
        self.assertIn('"\\${LD_LIBRARY_PATH:-}"', text)
        self.assertIn("minimal_cuda_kernel_result", text)

    def test_bootstrap_preserves_claim_boundaries(self) -> None:
        text = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("v2_14_4_speedup_claim", text)
        self.assertIn("true_zero_copy_claim", text)
        self.assertIn("author_parity_claim", text)
        self.assertIn("device_group_by_public_ready", text)

    def test_strict_runner_uses_bootstrap_before_goal5052_smoke(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("goal5057_v2144_pod_env_bootstrap.sh", text)
        self.assertIn("source \"${EXPORTS_SH}\"", text)
        self.assertIn("goal5052_v2144_public_api_pod_smoke_runner.sh", text)
        self.assertIn("--strict", (ROOT / "scripts" / "goal5052_v2144_public_api_pod_smoke_runner.sh").read_text(encoding="utf-8"))

    def test_pod_env_bootstrap_result_passed(self) -> None:
        payload = json.loads(ENV_JSON.read_text(encoding="utf-8"))
        self.assertEqual("rtdl.goal5057.v2_14_4_pod_env_bootstrap.v1", payload["schema"])
        self.assertEqual("pass", payload["overall_status"])
        self.assertEqual("0.61.2", payload["numba_version"])
        self.assertEqual("2.2.6", payload["numpy_version"])
        self.assertEqual([2], payload["minimal_cuda_kernel_result"])
        self.assertIn("V12.4.131", payload["ptxas_version"])

    def test_strict_smoke_still_passed_after_bootstrap(self) -> None:
        payload = json.loads(SMOKE_JSON.read_text(encoding="utf-8"))
        self.assertTrue(payload["strict"])
        self.assertEqual("pass", payload["overall_status"])


if __name__ == "__main__":
    unittest.main()
