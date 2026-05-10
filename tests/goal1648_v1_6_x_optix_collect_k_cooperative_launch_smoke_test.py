import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
SCRIPT = ROOT / "scripts" / "goal1648_v1_6_x_optix_collect_k_cooperative_launch_smoke.py"
POD_MD = ROOT / "docs" / "reports" / "goal1648_pod_a4500_cooperative_launch_smoke_2026-05-10.md"
POD_JSON = ROOT / "docs" / "reports" / "goal1648_pod_a4500_cooperative_launch_smoke_2026-05-10.json"


class Goal1648OptixCollectKCooperativeLaunchSmokeTest(unittest.TestCase):
    def test_native_smoke_entrypoint_launches_cooperative_kernel(self) -> None:
        api = API.read_text(encoding="utf-8")
        core = CORE.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_cooperative_launch_smoke", prelude)
        self.assertIn("rtdl_optix_collect_k_cooperative_launch_smoke", api)
        self.assertIn("cuLaunchCooperativeKernel", api)
        self.assertIn("cooperative_groups.h", core)
        self.assertIn("cg::this_grid", core)
        self.assertIn("grid.sync", core)

    def test_script_records_readiness_only_claim_boundary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("ctypes.CDLL", text)
        self.assertIn("cooperative_grid_sync_smoke_passed", text)
        self.assertIn("\"performance_evidence_authorized\": False", text)
        self.assertIn("readiness evidence only", text)
        self.assertIn("does not authorize public speedup wording", text)

    def test_pod_a4500_smoke_artifact_records_success_without_perf_claims(self) -> None:
        md = POD_MD.read_text(encoding="utf-8")
        payload = POD_JSON.read_text(encoding="utf-8")

        self.assertIn("NVIDIA RTX A4500", md)
        self.assertIn("Cooperative grid-sync smoke passed: `True`", md)
        self.assertIn('"cooperative_grid_sync_smoke_passed": true', payload)
        self.assertIn('"performance_evidence_authorized": false', payload)


if __name__ == "__main__":
    unittest.main()
