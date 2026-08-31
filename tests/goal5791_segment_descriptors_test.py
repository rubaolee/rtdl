from __future__ import annotations

import sys
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

from examples.current.research_benchmarks.triangle_counting import (
    segmented_rt_graph,
)
from scripts.goal5791_segment_descriptors import (
    SCHEMA,
    iter_rt2a1_segment_descriptors,
    validate_observed_segment,
)


class _FakeCupy:
    @staticmethod
    def asarray(value):
        return np.asarray(value)

    @staticmethod
    def get_default_memory_pool():
        return SimpleNamespace(free_all_blocks=lambda: None)


def _contract():
    # Degree-oriented CSR with enough two-hop multiplicity to exercise both
    # ordinary and single-source split partitions.
    rows = (
        (1, 2, 3, 4),
        (2, 3, 4),
        (3, 4),
        (4,),
        (),
    )
    offsets = [0]
    columns = []
    for row in rows:
        columns.extend(row)
        offsets.append(len(columns))
    return segmented_rt_graph.SegmentedRTGraphCSR(
        original_edge_count=len(columns),
        compacted_vertex_count=5,
        directed_vertex_count=5,
        row_offsets=np.asarray(offsets, dtype=np.int64),
        column_indices=np.asarray(columns, dtype=np.int64),
        expected_triangle_count=0,
        removed_low_degree_vertex_count=0,
        removed_low_degree_edge_count=0,
        removed_duplicate_or_self_edge_count=0,
        input_path="/frozen/goal5791.fixture",
        preprocessing={"global_two_hop_materialized": False},
    )


class Goal5791SegmentDescriptorTest(unittest.TestCase):
    def test_cpu_plan_matches_exact_device_generator_shape(self):
        contract = _contract()
        planned = list(iter_rt2a1_segment_descriptors(
            contract, max_relation_rows=5, max_directed_edge_rows=5))
        with mock.patch.dict(sys.modules, {"cupy": _FakeCupy}):
            observed = list(
                segmented_rt_graph.iter_segmented_rt_graph_device_geometry(
                    contract,
                    paper_algorithm="RT-2A1",
                    max_relation_rows=5,
                    max_directed_edge_rows=5,
                )
            )
        self.assertEqual(len(planned), len(observed))
        self.assertTrue(planned)
        for expected, actual in zip(planned, observed, strict=True):
            self.assertEqual(expected["schema"], SCHEMA)
            self.assertFalse(expected["gpu_touched"])
            validate_observed_segment(expected, actual)
            self.assertEqual(
                expected["host_geometry_bytes"], actual["host_geometry_bytes"])
            weights = np.asarray(actual["ray_weights"])
            self.assertEqual(expected["maximum_weight"], int(weights.max()))
            self.assertEqual(
                expected["weight_sum"], int(weights.sum(dtype=np.uint64)))

    def test_descriptor_plan_is_deterministic(self):
        first = list(iter_rt2a1_segment_descriptors(
            _contract(), max_relation_rows=5, max_directed_edge_rows=5))
        second = list(iter_rt2a1_segment_descriptors(
            _contract(), max_relation_rows=5, max_directed_edge_rows=5))
        self.assertEqual(first, second)
        self.assertEqual(
            [row["segment_id"] for row in first], list(range(len(first))))
        self.assertEqual(
            [row["partition"]["global_segment_id"] for row in first],
            list(range(len(first))),
        )

    def test_observed_drift_and_invalid_bounds_fail_closed(self):
        plan = next(iter(iter_rt2a1_segment_descriptors(
            _contract(), max_relation_rows=5, max_directed_edge_rows=5)))
        observed = {
            "segment_id": plan["segment_id"],
            "partition": dict(plan["partition"]),
            "relation_count": plan["relation_count"],
            "triangles": {"ids": np.arange(plan["primitive_count"])},
            "rays": {"ids": np.arange(plan["query_count"])},
            "host_geometry_bytes": plan["host_geometry_bytes"],
        }
        validate_observed_segment(plan, observed)
        for mutation in (
            {"segment_id": 99},
            {"relation_count": int(plan["relation_count"]) + 1},
            {"host_geometry_bytes": int(plan["host_geometry_bytes"]) + 8},
        ):
            changed = dict(observed)
            changed.update(mutation)
            with self.assertRaisesRegex(RuntimeError, "differs from CPU plan"):
                validate_observed_segment(plan, changed)
        for invalid in (0, -1, True, 1.5):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    list(iter_rt2a1_segment_descriptors(
                        _contract(), max_relation_rows=invalid))


if __name__ == "__main__":
    unittest.main()
