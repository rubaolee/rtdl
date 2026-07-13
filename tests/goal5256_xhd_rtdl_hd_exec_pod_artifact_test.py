from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"


class Goal5256XhdRtdlHdExecPodArtifactTest(unittest.TestCase):
    def _load(self, name: str) -> dict[str, object]:
        path = RESULTS / name
        if not path.exists():
            self.skipTest(f"missing POD artifact: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_exact_witness_pod_artifact_has_author_shaped_json_and_boundaries(self) -> None:
        payload = self._load("xhd_goal5256_rtdl_hd_exec_bounded3d_exact_witness_pod.json")

        self.assertEqual(payload["HDResult"], 2.0)
        self.assertEqual(payload["Running"]["Algorithm"], "RTDL-cell-mbr-exact-witness")
        self.assertIn("RTDL route wall time", payload["Running"]["TimeSemantics"])
        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-exact-witness")
        self.assertEqual(payload["RTDL"]["hd_result_semantics"], "directed_input1_to_input2")
        self.assertIn("not be compared to author internal", payload["RTDL"]["running_avg_time_semantics"])
        self.assertTrue(payload["RTDL"]["route"]["per_source_witness_exact"])
        boundary = payload["RTDL"]["claim_boundary"]
        self.assertFalse(boundary["full_xhd_paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claim_authorized"])
        self.assertFalse(boundary["performance_claim_authorized"])
        self.assertFalse(boundary["author_performance_parity_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_identity_claimed"])

    def test_fast_scalar_pod_artifact_has_distinct_route_label(self) -> None:
        payload = self._load("xhd_goal5256_rtdl_hd_exec_bounded3d_fast_scalar_pod.json")

        self.assertEqual(payload["HDResult"], 2.0)
        self.assertEqual(payload["Running"]["Algorithm"], "RTDL-cell-mbr-fast-scalar")
        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-fast-scalar")
        self.assertEqual(payload["RTDL"]["schema"], "rtdl.paper_reproduction.xhd.rtdl_hd_exec_compatible.v1")
        self.assertIn("cell-MBR frontier route", payload["RTDL"]["route"]["route_contract"])


if __name__ == "__main__":
    unittest.main()
