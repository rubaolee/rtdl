import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
SCRIPT = ROOT / "scripts" / "goal1647_v1_6_x_optix_collect_k_cooperative_capability_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal1647_v1_6_x_optix_collect_k_cooperative_merge_chain_prep_2026-05-09.md"
LINUX_CAPABILITY_MD = ROOT / "docs" / "reports" / "goal1647_linux_local_cooperative_capability_2026-05-09.md"
LINUX_CAPABILITY_JSON = ROOT / "docs" / "reports" / "goal1647_linux_local_cooperative_capability_2026-05-09.json"
POD_CAPABILITY_MD = ROOT / "docs" / "reports" / "goal1647_pod_a4500_cooperative_capability_2026-05-10.md"
POD_CAPABILITY_JSON = ROOT / "docs" / "reports" / "goal1647_pod_a4500_cooperative_capability_2026-05-10.json"
CLAUDE = ROOT / "docs" / "reviews" / "claude_goal1647_collect_k_cooperative_merge_chain_prep_review_2026-05-09.md"
GEMINI = ROOT / "docs" / "reviews" / "gemini_goal1647_collect_k_cooperative_merge_chain_prep_review_2026-05-09.md"
CONSENSUS = ROOT / "docs" / "reviews" / "goal1647_v1_6_x_optix_collect_k_cooperative_merge_chain_prep_3ai_consensus_2026-05-09.md"


class Goal1647OptixCollectKCooperativeMergeChainPrepTest(unittest.TestCase):
    def test_native_capability_probe_is_declared_and_queries_cuda_attributes(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_cooperative_launch_capability", prelude)
        self.assertIn("rtdl_optix_collect_k_cooperative_launch_capability", api)
        self.assertIn("CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH", api)
        self.assertIn("CU_DEVICE_ATTRIBUTE_COOPERATIVE_MULTI_DEVICE_LAUNCH", api)
        self.assertIn("CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT", api)
        self.assertIn("CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN", api)
        self.assertIn("*cooperative_launch_supported_out = 0", api)

    def test_capability_probe_script_is_claim_bounded(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("ctypes.CDLL", text)
        self.assertIn("\"cuda_device_index\": 0", text)
        self.assertIn("next_probe_allowed", text)
        self.assertIn("\"performance_evidence_authorized\": False", text)
        self.assertIn("\"fastest_candidate_behavior_changed\": False", text)
        self.assertIn("does not authorize public speedup wording", text)

    def test_report_preserves_diagnostic_boundary_and_pod_plan(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`cooperative_merge_chain_probe_prepared_locally`", text)
        self.assertIn("Goal1642 showed that the remaining final-pair wait is mostly deferred merge-chain work", text)
        self.assertIn("It must not be enabled by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`", text)
        self.assertIn("Require exact parity and at least `1.15x` first-probe speedup", text)
        self.assertIn("cooperative launch residency", text)
        self.assertIn("device-0-specific", text)
        self.assertIn("Local Linux Validation", text)

    def test_local_linux_capability_smoke_is_recorded_as_non_performance_evidence(self) -> None:
        md = LINUX_CAPABILITY_MD.read_text(encoding="utf-8")
        payload = LINUX_CAPABILITY_JSON.read_text(encoding="utf-8")

        self.assertIn("NVIDIA GeForce GTX 1070", md)
        self.assertIn("Next cooperative merge-chain probe allowed: `True`", md)
        self.assertIn("It is not performance evidence", md)
        self.assertIn('"next_probe_allowed": true', payload)
        self.assertIn('"performance_evidence_authorized": false', payload)

    def test_pod_a4500_capability_smoke_is_recorded(self) -> None:
        md = POD_CAPABILITY_MD.read_text(encoding="utf-8")
        payload = POD_CAPABILITY_JSON.read_text(encoding="utf-8")

        self.assertIn("NVIDIA RTX A4500", md)
        self.assertIn("Next cooperative merge-chain probe allowed: `True`", md)
        self.assertIn("It is not performance evidence", md)
        self.assertIn('"next_probe_allowed": true', payload)
        self.assertIn('"performance_evidence_authorized": false', payload)

    def test_external_reviews_and_consensus_are_recorded(self) -> None:
        claude = CLAUDE.read_text(encoding="utf-8")
        gemini = GEMINI.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Approved", claude)
        self.assertIn("technically sound and procedurally compliant", gemini)
        self.assertIn("`cooperative_merge_chain_capability_probe_ready_for_pod`", consensus)
        self.assertIn("The local files were updated for those points", consensus)
        self.assertIn("does not authorize public speedup wording", consensus)


if __name__ == "__main__":
    unittest.main()
