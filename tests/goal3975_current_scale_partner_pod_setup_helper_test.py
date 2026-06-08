import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3975_current_scale_partner_pod_setup.sh"
RUNBOOK = ROOT / "docs" / "audit" / "runbooks" / "rtx_cloud_single_session_runbook.md"
REPORT = ROOT / "docs" / "reports" / "goal3975_current_scale_partner_pod_setup_helper_2026-06-08.md"


class Goal3975CurrentScalePartnerPodSetupHelperTest(unittest.TestCase):
    def test_helper_pins_driver_550_partner_stack(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for fragment in [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            "numba==0.60.0",
            "numpy==2.0.2",
            "nvidia-cuda-nvcc-cu12==12.4.131",
            "cupy-cuda12x==14.1.1",
            "nvidia/cuda_nvcc",
            "export CUDA_HOME=\"${NUMBA_CUDA_PREFIX}\"",
            "export RTDL_CUDA_PREFIX",
            "RTDL_OPTIX_PTX_ARCH=compute_89",
            "RTDL_OPTIX_CUBIN_ARCH=sm_89",
            'export PATH="${NUMBA_CUDA_PREFIX}/bin:${RTDL_CUDA_PREFIX}/bin:\\$PATH"',
            'export RTDL_OPTIX_LIBRARY="\\$PWD/build/librtdl_optix.so"',
        ]:
            self.assertIn(fragment, text)
        self.assertNotIn("\\\\$PATH", text)
        self.assertNotIn("\\\\$PWD", text)

    def test_helper_smokes_numba_and_cupy(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("@cuda.jit", text)
        self.assertIn("partner_smoke_ok", text)
        self.assertIn("cp.sum(cp.arange(8, dtype=cp.int32))", text)

    def test_runbook_references_helper(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("scripts/goal3975_current_scale_partner_pod_setup.sh", text)

    def test_report_records_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "already-running Linux RTX pod",
            "does not create cloud resources",
            "partner_smoke_ok",
            "literal `$PATH`",
            "does not authorize release",
            "app-specific native-engine logic",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
