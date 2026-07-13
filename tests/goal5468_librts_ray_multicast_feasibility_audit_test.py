from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
SOURCE = APP / "data" / "author_source" / "goal5468_ray_multicast_source_manifest.json"
RESULT = APP / "results" / "librts_goal5468_5469_ray_multicast_feasibility.json"


class Goal5468LibRtsRayMulticastFeasibilityAuditTest(unittest.TestCase):
    def test_paper_and_source_contract_are_pinned(self) -> None:
        payload = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(payload["paper"]["section"], "3.4 Ray Multicast for Load Balancing")
        self.assertEqual(payload["source"]["commit"], "7c54c181b1058c87768767998c00e225cc58666e")
        files = {row["path"]: row for row in payload["source"]["files"]}
        self.assertIn("include/rtspatial/spatial_index.cuh", files)
        self.assertIn("src/shaders/shaders_intersects_envelope_query_2d.cu", files)
        self.assertEqual(payload["mechanism"]["scope"], "range-intersects backward casting only")
        self.assertFalse(payload["claim_boundary"]["native_backend_implemented"])

    def test_audit_distinguishes_existing_assets_from_native_gaps(self) -> None:
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertIn("prepared box-query GAS", payload["existing_rtdl_assets"])
        self.assertIn(
            "per-ray partition fanout in a two-dimensional OptiX launch",
            payload["missing_native_capabilities"],
        )
        self.assertIn(
            "query batching does not partition one traversal workload",
            payload["historical_non_equivalences"],
        )
        self.assertEqual(payload["genericity_gate"]["kill_gate"], "pass_for_bounded_native_spike")
        self.assertTrue(payload["next_pod_gate"]["authorized"])
        self.assertFalse(payload["claim_boundary"]["runtime_speedup_measured"])
        self.assertFalse(payload["claim_boundary"]["author_equivalence_claimed"])


if __name__ == "__main__":
    unittest.main()
