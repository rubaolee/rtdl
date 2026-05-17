from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2198_rayjoin_same_query_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2198_rayjoin_same_query_pod_runbook_2026-05-17.md"


class Goal2198RayJoinSameQueryPodRunnerTest(unittest.TestCase):
    def test_runner_applies_export_patch_and_uses_same_query_consumer(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff", text)
        self.assertIn("-query_stream_output=${stream_output}", text)
        self.assertIn("goal2192_rayjoin_same_query_stream_runner.py", text)
        self.assertIn("--backends cpu,embree,optix", text)
        self.assertIn("rayjoin_query_exec_export_patch", text)
        self.assertIn("same_contract_with_rayjoin_query_exec", text)

    def test_runner_has_bounded_progress_and_environment_setup(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("STEP_TIMEOUT_SECONDS", text)
        self.assertIn("progress.log", text)
        self.assertIn("nvidia-smi", text)
        self.assertIn("https://github.com/NVIDIA/optix-sdk", text)
        self.assertIn("libgflags-dev", text)
        self.assertIn("libgoogle-glog-dev", text)
        self.assertIn("install_cuda_nvtx_if_available", text)
        self.assertIn("cuda-nvtx-", text)
        self.assertNotIn("libnvtx3-dev", text)
        self.assertIn("RTDL_OPTIX_PTX_ARCH", text)
        self.assertIn("CUDA_PREFIX", text)
        self.assertIn("detect_cuda_major", text)
        self.assertIn("ALLOW_NON_CUDA12", text)
        self.assertIn("cupy-cuda12x", text)
        self.assertIn("prepare_python_environment", text)
        self.assertIn("USE_PYTHON_VENV", text)
        self.assertIn("-m venv", text)

    def test_runner_preserves_external_rayjoin_and_claim_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("RAYJOIN_COMMIT", text)
        self.assertIn("RTDL_GOAL2198_VEC2_HASH_EQUAL_PATCH", text)
        self.assertIn("set(ENABLED_ARCHS 86)", text)
        self.assertIn("#include <nvtx3/nvToolsExt.h>", text)
        self.assertIn('"paper_scale_perf_claim_authorized": False', text)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', text)
        self.assertIn('"broad_rt_core_speedup_claim_authorized": False', text)
        self.assertIn('"v2_0_release_authorized": False', text)

    def test_runbook_marks_status_as_not_yet_pod_evidence(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("pod runner prepared; RTX execution still required", text)
        self.assertIn("not evidence", text)
        self.assertIn("does not prove RTDL beats RayJoin", text)
        self.assertIn("does not authorize a v2.0 release", text)
        self.assertIn("summary.json", text)


if __name__ == "__main__":
    unittest.main()
