from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

from examples.benchmark_apps.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin,
)
from examples.benchmark_apps.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as triangle,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3800_legacy_versioned_helper_alias_cleanup_2026-06-07.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
TRIANGLE_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)
RAYJOIN_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)


class Goal3800LegacyVersionedHelperAliasCleanupTest(unittest.TestCase):
    def test_triangle_current_aliases_preserve_legacy_payloads(self) -> None:
        primitive = triangle.run_app("primitive_first_plan")
        legacy_primitive = triangle.run_app("v2_5_plan")
        self.assertEqual(primitive["mode"], "primitive_first_plan")
        self.assertEqual(primitive["legacy_mode_alias"], "v2_5_plan")
        self.assertEqual(
            primitive["v2_5_primitive_first_plan"],
            legacy_primitive["v2_5_primitive_first_plan"],
        )

        current = triangle.run_app("segmented_compact_mask_numba_plan")
        legacy = triangle.run_app("v2_6_numba_compact_mask_plan")
        self.assertEqual(current["mode"], "segmented_compact_mask_numba_plan")
        self.assertEqual(current["legacy_mode_alias"], "v2_6_numba_compact_mask_plan")
        self.assertEqual(current["operation"], legacy["operation"])
        self.assertEqual(current["selected_partner"], "numba")
        self.assertTrue(current["uses_v2_8_segmented_typed_stream_front_door"])
        self.assertFalse(current["public_speedup_claim_authorized"])

    def test_rayjoin_current_aliases_preserve_legacy_payloads(self) -> None:
        primitive = rayjoin.primitive_first_plan_payload()
        legacy_primitive = rayjoin.v2_5_plan_payload()
        self.assertEqual(primitive["mode"], "primitive_first_plan")
        self.assertEqual(primitive["legacy_mode_alias"], "v2_5_plan")
        self.assertEqual(
            primitive["v2_5_primitive_first_plan"],
            legacy_primitive["v2_5_primitive_first_plan"],
        )

        current = rayjoin.segmented_compact_mask_numba_plan_payload("pip")
        legacy = rayjoin.v2_6_numba_compact_mask_plan_payload("pip")
        self.assertEqual(current["mode"], "segmented_compact_mask_numba_plan")
        self.assertEqual(current["legacy_mode_alias"], "v2_6_numba_compact_mask_plan")
        self.assertEqual(current["operation"], legacy["operation"])
        self.assertEqual(current["selected_partner"], "numba")
        self.assertTrue(current["uses_v2_8_segmented_typed_stream_front_door"])
        self.assertFalse(current["public_speedup_claim_authorized"])

    def test_current_preview_aliases_fail_closed_on_host_numpy_arrays(self) -> None:
        triangle_inputs = {
            "candidate_row_ids": np.asarray([1, 2, 3], dtype=np.int64),
            "valid_triangle_mask": np.asarray([True, False, True], dtype=np.bool_),
        }
        with self.assertRaisesRegex(ValueError, "device-resident CUDA column is required"):
            triangle.run_triangle_counting_segmented_compact_mask_numba_preview(triangle_inputs)

        rayjoin_inputs = {
            "candidate_row_ids": np.asarray([1, 2, 3], dtype=np.int64),
            "keep_mask": np.asarray([True, False, True], dtype=np.bool_),
        }
        with self.assertRaisesRegex(ValueError, "device-resident CUDA column is required"):
            rayjoin.run_rayjoin_segmented_compact_mask_numba_preview(rayjoin_inputs)

    def test_rayjoin_cli_exposes_current_alias(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(RAYJOIN_APP),
                "--workload",
                "pip",
                "--execution-route",
                "segmented_compact_mask_numba_plan",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "segmented_compact_mask_numba_plan")
        self.assertEqual(payload["legacy_mode_alias"], "v2_6_numba_compact_mask_plan")
        self.assertEqual(payload["operation"], "compact_mask_i64")

    def test_triangle_cli_exposes_current_alias(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(TRIANGLE_APP),
                "--mode",
                "segmented_compact_mask_numba_plan",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["mode"], "segmented_compact_mask_numba_plan")
        self.assertEqual(payload["legacy_mode_alias"], "v2_6_numba_compact_mask_plan")
        self.assertEqual(payload["operation"], "compact_mask_i64")

    def test_report_and_todo_record_partial_cleanup_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3800",
            "No native-engine code changed",
            "`v2_5_plan`",
            "`v2_6_numba_compact_mask_plan`",
            "`segmented_compact_mask_numba_plan`",
            "does not declare all legacy versioned helper names cleaned",
        ):
            self.assertIn(phrase, text)
        todo = TODO.read_text(encoding="utf-8")
        self.assertIn("Goal3800 started this migration", todo)
        self.assertIn("compatibility shims", todo)


if __name__ == "__main__":
    unittest.main()
