from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

import rtdsl as rt
from examples.v2_0.research_benchmarks.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
APP = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
REPORT = REPO_ROOT / "docs" / "reports" / "goal3002_rayjoin_numba_compact_mask_wiring_2026-06-01.md"


class Goal3002RayjoinNumbaCompactMaskWiringTest(unittest.TestCase):
    def test_plan_exposes_generic_compact_mask_for_each_workload(self) -> None:
        for workload in ("pip", "lsi", "overlay_seed"):
            with self.subTest(workload=workload):
                payload = rayjoin.v2_6_numba_compact_mask_plan_payload(workload)
                self.assertEqual(payload["app"], "rayjoin_v2_spatial_join")
                self.assertEqual(payload["workload"], workload)
                self.assertEqual(payload["selected_partner"], "numba")
                self.assertEqual(payload["operation"], "compact_mask_i64")
                self.assertEqual(payload["numba_descriptor"]["operation"], "compact_mask_i64")
                self.assertEqual(payload["input_columns"], ("candidate_row_ids:int64", "keep_mask:bool"))
                self.assertTrue(payload["uses_v2_6_neutral_partner_handoff"])
                self.assertTrue(payload["uses_v2_8_segmented_typed_stream_front_door"])
                self.assertFalse(payload["uses_legacy_torch_carrier"])
                self.assertFalse(payload["uses_torch_conversion"])
                self.assertFalse(payload["replaces_rt_traversal"])
                self.assertFalse(payload["promoted_performance_path"])
                self.assertFalse(payload["public_speedup_claim_authorized"])
                self.assertFalse(payload["rt_core_speedup_claim_authorized"])
                self.assertFalse(payload["true_zero_copy_claim_authorized"])
                self.assertFalse(payload["paper_reproduction_claim_authorized"])

    def test_preview_rejects_host_numpy_arrays_before_cuda_execution(self) -> None:
        inputs = {
            "candidate_row_ids": np.asarray([4, 5, 6, 7], dtype=np.int64),
            "keep_mask": np.asarray([True, False, True, False], dtype=np.bool_),
        }
        with self.assertRaisesRegex(ValueError, "device-resident CUDA column is required"):
            rayjoin.run_rayjoin_v2_6_numba_compact_mask_preview(inputs, workload="pip")

    def test_cli_exposes_plan_route(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(APP),
                "--workload",
                "pip",
                "--execution-route",
                "v2_6_numba_compact_mask_plan",
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn('"mode": "v2_6_numba_compact_mask_plan"', completed.stdout)
        self.assertIn('"operation": "compact_mask_i64"', completed.stdout)
        self.assertIn('"selected_partner": "numba"', completed.stdout)

    def test_v2_6_roadmap_indexes_goal3002_without_speedup_claim(self) -> None:
        roadmap = rt.v2_6_roadmap()

        self.assertEqual(roadmap["rayjoin_compact_mask_goal"], "Goal3002")
        self.assertIn("rayjoin_v2_spatial_join", roadmap["rayjoin_compact_mask_status"])
        self.assertIn("not_speedup_evidence", roadmap["rayjoin_compact_mask_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_report_and_source_record_boundary(self) -> None:
        source = APP.read_text(encoding="utf-8")
        for phrase in (
            "RAYJOIN_V2_6_NUMBA_COMPACT_MASK_VERSION",
            "describe_rayjoin_v2_6_numba_compact_mask_continuation",
            "run_rayjoin_v2_6_numba_compact_mask_preview",
            "build_segmented_typed_stream_adapter",
            "execute_segmented_typed_stream_partner_continuation",
            "v2_8_segmented_typed_stream_front_door_used",
        ):
            self.assertIn(phrase, source)
        self.assertNotIn("rt.run_numba_compact_mask_i64(", source)
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3002",
            "RayJoin",
            "compact_mask_i64",
            "Prepared generic RTDL count/parity primitives remain the recommended path",
            "Not a RayJoin performance claim",
            "CUDA pod runtime evidence for this app wiring is still pending",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
