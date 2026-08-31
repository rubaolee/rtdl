from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
AUTHOR_HDRESULT = 0.09761668741703033
TOLERANCE = 1e-6


class Goal5257XhdRtdlHdExecModelNet40PodArtifactTest(unittest.TestCase):
    def _load(self, name: str) -> dict[str, object]:
        path = RESULTS / name
        if not path.exists():
            self.skipTest(f"missing POD artifact: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _assert_common_modelnet40_contract(self, payload: dict[str, object]) -> None:
        self.assertAlmostEqual(payload["HDResult"], AUTHOR_HDRESULT, delta=TOLERANCE)
        self.assertEqual(payload["RTDL"]["input_type"], "off")
        self.assertEqual(payload["RTDL"]["n_dims"], 3)
        self.assertEqual(payload["RTDL"]["variant"], "rt")
        self.assertEqual(payload["RTDL"]["execution"], "gpu")
        self.assertEqual(payload["RTDL"]["point_count_a"], 370568)
        self.assertEqual(payload["RTDL"]["point_count_b"], 376741)
        self.assertEqual(
            payload["RTDL"]["reference_preprocessing"],
            ["normalize_each_input_to_author_float32_unit_box"],
        )
        self.assertEqual(payload["RTDL"]["hd_result_semantics"], "directed_input1_to_input2")
        self.assertIn("RTDL route wall time", payload["Running"]["TimeSemantics"])
        self.assertIn("not be compared to author internal", payload["RTDL"]["running_avg_time_semantics"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["performance_claim_authorized"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["author_performance_parity_claimed"])

    def test_modelnet40_exact_witness_entrypoint_artifact(self) -> None:
        payload = self._load("xhd_goal5257_modelnet40_airplane_0036_0515_exact_witness_hd_exec_pod.json")

        self._assert_common_modelnet40_contract(payload)
        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-exact-witness")
        self.assertEqual(payload["Running"]["Algorithm"], "RTDL-cell-mbr-exact-witness")
        self.assertTrue(payload["RTDL"]["route"]["per_source_witness_exact"])

    def test_modelnet40_fast_scalar_entrypoint_artifact(self) -> None:
        payload = self._load("xhd_goal5257_modelnet40_airplane_0036_0515_fast_scalar_hd_exec_pod.json")

        self._assert_common_modelnet40_contract(payload)
        self.assertEqual(payload["RTDL"]["route_label"], "cell-mbr-fast-scalar")
        self.assertEqual(payload["Running"]["Algorithm"], "RTDL-cell-mbr-fast-scalar")
        self.assertFalse(payload["RTDL"]["route"]["per_source_witness_exact"])


if __name__ == "__main__":
    unittest.main()
