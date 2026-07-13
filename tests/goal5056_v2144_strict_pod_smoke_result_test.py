from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
POD_JSON = ROOT / "history" / "internal_docs" / "goal5052_v2144_public_api_pod_smoke_result.json"
PREFLIGHT_JSON = ROOT / "history" / "internal_docs" / "goal5053_v2144_release_preflight_result.json"
REPORT = ROOT / "history" / "internal_docs" / "goal5056_v2_14_4_strict_pod_smoke_result_2026-07-06.md"
CALL = ROOT / "history" / "internal_docs" / "call_for_review_goal5056_v2_14_4_strict_pod_smoke_result_2026-07-06.md"


class Goal5056V2144StrictPodSmokeResultTest(unittest.TestCase):
    def test_strict_pod_smoke_json_passed(self) -> None:
        payload = json.loads(POD_JSON.read_text(encoding="utf-8"))
        self.assertEqual("rtdl.goal5052.v2_14_4_public_api_pod_smoke.v1", payload["schema"])
        self.assertTrue(payload["strict"])
        self.assertEqual("pass", payload["overall_status"])
        by_label = {step["label"]: step for step in payload["steps"]}
        self.assertEqual("pass", by_label["public_numba_partner_continuation_cuda"]["status"])
        self.assertFalse(by_label["public_numba_partner_continuation_cuda"]["host_fallback_used"])
        self.assertEqual([False, True, True, False], by_label["public_numba_partner_continuation_cuda"]["mask"])
        self.assertEqual("pass", by_label["rayjoin_public_device_order_by_native_cuda_path"]["status"])
        self.assertTrue(by_label["rayjoin_public_device_order_by_native_cuda_path"]["public_device_order_by_used"])
        self.assertEqual([2, 1, 3, 0], by_label["rayjoin_public_device_order_by_native_cuda_path"]["observed_order"])

    def test_preflight_pod_gate_passes_and_review_debt_is_retired(self) -> None:
        payload = json.loads(PREFLIGHT_JSON.read_text(encoding="utf-8"))
        strict = next(check for check in payload["checks"] if check["id"] == "strict_pod_smoke")
        review = next(check for check in payload["checks"] if check["id"] == "external_review_debt")
        self.assertEqual("pass", strict["status"])
        self.assertEqual("pass", review["status"])
        self.assertEqual([], review["open"])
        self.assertEqual("ready_for_public_release_staging", payload["overall_status"])

    def test_report_preserves_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("completed_strict_pod_smoke_passed__release_still_blocked_by_review_debt", text)
        self.assertIn("public_release_ready", text)
        self.assertIn("v2_14_4_speedup_claim", text)
        self.assertIn("true_zero_copy_claim", text)
        self.assertIn("author_parity_claim", text)
        self.assertIn("device_group_by_public_ready", text)
        authorized_section = text.split("Not authorized:", 1)[0]
        self.assertNotIn("public_release_ready", authorized_section)

    def test_call_for_review_exists(self) -> None:
        text = CALL.read_text(encoding="utf-8")
        self.assertIn("approve_goal5056_strict_pod_smoke_passed_release_still_blocked_by_review", text)
        self.assertIn("strict POD smoke JSON", text)


if __name__ == "__main__":
    unittest.main()
