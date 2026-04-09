import math
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.reference.rtdl_workload_reference import make_fixture_point_nearest_segment_case
from examples.reference.rtdl_workload_reference import make_fixture_segment_polygon_case
from examples.reference.rtdl_workload_reference import make_point_nearest_segment_authored_case
from examples.reference.rtdl_workload_reference import make_segment_polygon_authored_case
from examples.reference.rtdl_workload_reference import point_nearest_segment_reference
from examples.reference.rtdl_workload_reference import segment_polygon_anyhit_rows_reference
from examples.reference.rtdl_workload_reference import segment_polygon_hitcount_reference
from tests._embree_support import embree_available


class Goal10WorkloadsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not embree_available():
            raise unittest.SkipTest("Embree is not installed in the current environment")

    def test_segment_polygon_hitcount_authored_cpu_embree_parity(self) -> None:
        case = make_segment_polygon_authored_case()
        cpu_rows = rt.run_cpu(segment_polygon_hitcount_reference, **case)
        embree_rows = rt.run_embree(segment_polygon_hitcount_reference, **case)
        self.assertEqual(cpu_rows, embree_rows)
        self.assertEqual(cpu_rows[0]["hit_count"], 1)
        self.assertEqual(cpu_rows[1]["hit_count"], 1)

    def test_segment_polygon_hitcount_fixture_cpu_embree_parity(self) -> None:
        case = make_fixture_segment_polygon_case()
        cpu_rows = rt.run_cpu(segment_polygon_hitcount_reference, **case)
        embree_rows = rt.run_embree(segment_polygon_hitcount_reference, **case)
        self.assertEqual(cpu_rows, embree_rows)
        self.assertTrue(any(row["hit_count"] >= 1 for row in cpu_rows))

    def test_segment_polygon_anyhit_rows_authored_cpu_embree_parity(self) -> None:
        case = make_segment_polygon_authored_case()
        cpu_rows = rt.run_cpu(segment_polygon_anyhit_rows_reference, **case)
        embree_rows = rt.run_embree(segment_polygon_anyhit_rows_reference, **case)
        self.assertEqual(cpu_rows, embree_rows)
        self.assertEqual(
            cpu_rows,
            (
                {"segment_id": 1, "polygon_id": 10},
                {"segment_id": 2, "polygon_id": 11},
            ),
        )

    def test_point_nearest_segment_authored_cpu_embree_parity(self) -> None:
        case = make_point_nearest_segment_authored_case()
        cpu_rows = rt.run_cpu(point_nearest_segment_reference, **case)
        embree_rows = rt.run_embree(point_nearest_segment_reference, **case)
        self.assertEqual(len(cpu_rows), len(embree_rows))
        for cpu_row, embree_row in zip(cpu_rows, embree_rows):
            self.assertEqual(cpu_row["point_id"], embree_row["point_id"])
            self.assertEqual(cpu_row["segment_id"], embree_row["segment_id"])
            self.assertTrue(math.isclose(cpu_row["distance"], embree_row["distance"], rel_tol=1e-6, abs_tol=1e-6))

    def test_point_nearest_segment_fixture_cpu_embree_parity(self) -> None:
        case = make_fixture_point_nearest_segment_case()
        cpu_rows = rt.run_cpu(point_nearest_segment_reference, **case)
        embree_rows = rt.run_embree(point_nearest_segment_reference, **case)
        self.assertEqual(len(cpu_rows), len(embree_rows))
        for cpu_row, embree_row in zip(cpu_rows, embree_rows):
            self.assertEqual(cpu_row["point_id"], embree_row["point_id"])
            self.assertEqual(cpu_row["segment_id"], embree_row["segment_id"])
            self.assertTrue(math.isclose(cpu_row["distance"], embree_row["distance"], rel_tol=1e-6, abs_tol=1e-6))

    def test_goal10_lowering_support(self) -> None:
        plan_a = rt.lower_to_execution_plan(rt.compile_kernel(segment_polygon_hitcount_reference))
        plan_b = rt.lower_to_execution_plan(rt.compile_kernel(segment_polygon_anyhit_rows_reference))
        plan_c = rt.lower_to_execution_plan(rt.compile_kernel(point_nearest_segment_reference))
        self.assertEqual(plan_a.workload_kind, "segment_polygon_hitcount")
        self.assertEqual(plan_b.workload_kind, "segment_polygon_anyhit_rows")
        self.assertEqual(plan_c.workload_kind, "point_nearest_segment")
