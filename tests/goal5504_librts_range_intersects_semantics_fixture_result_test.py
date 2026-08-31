from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5504_range_intersects_semantics_fixtures.json"


class Goal5504RangeIntersectsSemanticsFixtureResultTest(unittest.TestCase):
    def test_result_preserves_source_driven_emulation_boundary(self) -> None:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.librts.goal5504_range_intersects_semantics_fixtures.v1",
        )
        self.assertEqual(payload["status"], "semantics_fixture_diagnostic_completed")
        self.assertEqual(payload["summary"]["case_count"], 5)
        self.assertEqual(payload["summary"]["discriminating_case_count"], 1)
        self.assertFalse(payload["summary"]["cpu_gpu_emulation_equivalent_on_all_cases"])
        self.assertFalse(payload["claim_boundary"]["author_gpu_runtime_executed"])
        self.assertFalse(payload["claim_boundary"]["cpu_oracle_is_author_truth"])
        self.assertFalse(payload["claim_boundary"]["rtdl_core_change_authorized"])
        self.assertEqual(
            payload["contract_inputs"]["gpu_contract_emulation"],
            "rayparams_float32_slab_nextafter_t1_tfar_gamma",
        )


if __name__ == "__main__":
    unittest.main()
