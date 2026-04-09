from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt
from examples.reference.rtdl_language_reference import county_zip_join_reference
from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import load_cdb
from rtdsl.lowering import lower_to_execution_plan
from rtdsl.reference import Segment


class Goal31LsiGapClosureTest(unittest.TestCase):
    def test_minimal_exact_source_reproducer_is_parity_clean(self) -> None:
        left = (
            Segment(id=24, x0=-92.864493, y0=42.202805, x1=-92.86446, y1=42.21008),
            Segment(id=25, x0=-92.86446, y0=42.21008, x1=-92.854876, y1=42.210026),
            Segment(id=26, x0=-92.854876, y0=42.210026, x1=-92.845057, y1=42.210089),
            Segment(id=111, x0=-92.767498, y0=42.222858, x1=-92.7674645, y1=42.2195138),
        )
        right = (
            Segment(id=345, x0=-92.767483, y0=42.224668, x1=-92.767464, y1=42.218844),
            Segment(id=365, x0=-92.845061, y0=42.210052, x1=-92.854730997, y1=42.210063486),
            Segment(id=367, x0=-92.854873996, y0=42.210063582, x1=-92.864443, y1=42.210078),
            Segment(id=368, x0=-92.864443, y0=42.210078, x1=-92.864472, y1=42.210078),
        )

        cpu = {
            (row["left_id"], row["right_id"])
            for row in rt.run_cpu(county_zip_join_reference, left=left, right=right)
        }
        embree = {
            (row["left_id"], row["right_id"])
            for row in rt.run_embree(county_zip_join_reference, left=left, right=right)
        }

        expected = {(24, 368), (25, 367), (26, 365), (111, 345)}
        self.assertEqual(cpu, expected)
        self.assertEqual(embree, expected)

    def test_lsi_lowering_marks_current_local_backend_as_native_loop(self) -> None:
        plan = lower_to_execution_plan(rt.compile_kernel(county_zip_join_reference))
        self.assertEqual(plan.workload_kind, "lsi")
        self.assertEqual(plan.accel_kind, "native_loop")
        self.assertIn("native_loop", plan.bvh_policy)

    def test_frozen_k5_slice_is_parity_clean_when_local_snapshot_exists(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        left_path = repo / "build" / "goal29_zipcode_selected_k5.cdb"
        right_path = repo / "build" / "goal29_uscounty_selected_k5.cdb"
        if not left_path.exists() or not right_path.exists():
            self.skipTest("frozen k=5 exact-source snapshot is not available in this checkout")

        left = tuple(segments_from_records(chains_to_segments(load_cdb(left_path))))
        right = tuple(segments_from_records(chains_to_segments(load_cdb(right_path))))

        cpu = {
            (row["left_id"], row["right_id"])
            for row in rt.run_cpu(county_zip_join_reference, left=left, right=right)
        }
        embree = {
            (row["left_id"], row["right_id"])
            for row in rt.run_embree(county_zip_join_reference, left=left, right=right)
        }
        self.assertEqual(embree, cpu)
        self.assertEqual(len(cpu), 7)


if __name__ == "__main__":
    unittest.main()
