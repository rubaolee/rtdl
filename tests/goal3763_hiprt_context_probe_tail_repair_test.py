from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3763_hiprt_context_probe_tail_repair_and_cuda_path_smoke_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3763_hiprt_context_probe_tail_repair_and_cuda_path_smoke_a5000.json"


class Goal3763HiprtContextProbeTailRepairTest(unittest.TestCase):
    def test_context_probe_tail_is_complete(self) -> None:
        text = HIPRT_API.read_text(encoding="utf-8")
        probe_start = text.index("extern \"C\" int rtdl_hiprt_context_probe(")
        probe = text[probe_start:]
        self.assertIn("oroGetDeviceProperties(&props, device)", probe)
        self.assertIn("hiprtCreateContext(HIPRT_API_VERSION, input, hiprt_ctx)", probe)
        self.assertIn("hiprtDestroyContext(hiprt_ctx)", probe)
        self.assertIn("oroCtxDestroy(ctx)", probe)
        self.assertIn("return 0;", probe)
        self.assertTrue(probe.rstrip().endswith("}"))

    def test_report_and_artifact_when_present_keep_amd_boundary(self) -> None:
        if not REPORT.exists() or not ARTIFACT.exists():
            self.skipTest("Goal3763 pod build artifact/report not generated yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3763.hiprt_context_probe_tail_repair_and_cuda_path_smoke.v1")
        self.assertEqual(payload["build_status"], "pass")
        self.assertEqual(payload["focused_test_status"], "pass")
        self.assertEqual(payload["focused_test_count"], 26)
        self.assertTrue(payload["hiprt_sdk_sha256"].startswith("72172d20"))
        self.assertFalse(payload["claim_boundary"]["amd_hardware_perf_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["broad_rt_core_claim_authorized"])
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("26 focused HIPRT tests", report)


if __name__ == "__main__":
    unittest.main()
