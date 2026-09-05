from __future__ import annotations

import struct
import sys
import unittest

from experiments.goal5798_premeasurement.workload import digest
from experiments.goal5798_premeasurement.workload import (
    relation_workload as legacy_relation_workload,
)
from experiments.goal5798_premeasurement.workload import (
    triangle_workload as legacy_triangle_workload,
)
from experiments.goal5848_strong_baseline import workloads
from rtdsl import v4_rtdlexe as runtime


class Goal5848PackedWorkloadTest(unittest.TestCase):
    def test_relation_bytes_are_exact_legacy_task(self):
        packed = workloads.relation_workload()
        legacy = legacy_relation_workload()
        decoded_bounds = tuple(struct.iter_unpack(
            "<4f", packed.indexed_bounds_f32le
        ))
        decoded_ids = tuple(
            row[0] for row in struct.iter_unpack(
                "<I", packed.indexed_ids_u32le
            )
        )
        decoded = [
            [*bounds, item_id]
            for bounds, item_id in zip(decoded_bounds, decoded_ids)
        ]
        interleaved = [
            list(row) for row in struct.iter_unpack(
                "<4fI", packed.indexed_interleaved_4f_u32le
            )
        ]
        self.assertEqual(decoded, legacy["indexed"])
        self.assertEqual(interleaved, legacy["indexed"])
        self.assertEqual(packed.source_bounds_f32le, packed.indexed_bounds_f32le)
        self.assertEqual(packed.source_ids_u32le, packed.indexed_ids_u32le)
        self.assertEqual(packed.expected_rows, tuple(
            tuple(row) for row in legacy["expected_rows"]
        ))
        self.assertEqual(packed.semantic_input_sha256, digest({
            "indexed": legacy["indexed"],
            "sources": legacy["sources"],
            "capacity": legacy["capacity"],
            "minimum_overlap": legacy["minimum_overlap"],
        }))
        self.assertEqual(packed.public_output_sha256, digest(packed.expected_rows))

    def test_triangle_bytes_are_exact_legacy_task(self):
        packed = workloads.triangle_workload()
        legacy = legacy_triangle_workload()
        vertices = [
            list(row) for row in struct.iter_unpack("<3f", packed.vertices_f32le)
        ]
        triangles = [
            tuple(row) for row in struct.iter_unpack(
                "<3I", packed.triangles_u32le
            )
        ]
        origins = tuple(struct.iter_unpack("<3f", packed.query_origins_f32le))
        directions = tuple(struct.iter_unpack(
            "<3f", packed.query_directions_f32le
        ))
        maxima = tuple(
            row[0] for row in struct.iter_unpack(
                "<f", packed.query_tmax_f32le
            )
        )
        rays = [
            [list(origin), list(direction)]
            for origin, direction in zip(origins, directions)
        ]
        weights = [
            row[0] for row in struct.iter_unpack(
                "<Q", packed.query_weights_u64le
            )
        ]
        self.assertEqual(vertices, legacy["vertices"])
        self.assertEqual(
            triangles,
            [(index, index + 1, index + 2)
             for index in range(0, len(vertices), 3)],
        )
        self.assertEqual(rays, legacy["rays"])
        self.assertEqual(list(maxima), [legacy["tmax"]] * packed.query_count)
        self.assertEqual(weights, legacy["weights"])
        self.assertEqual(
            packed.expected_reduced_u64,
            legacy["expected_weighted_sum"],
        )
        self.assertEqual(packed.semantic_input_sha256, digest({
            "vertices": legacy["vertices"],
            "rays": legacy["rays"],
            "weights": legacy["weights"],
            "tmin": legacy["tmin"],
            "tmax": legacy["tmax"],
        }))
        self.assertEqual(
            packed.public_output_sha256,
            digest(packed.expected_reduced_u64),
        )

    def test_public_buffer_front_doors_accept_exact_packed_authority(self):
        relation = workloads.relation_workload()
        relation_static = runtime.BoundedRelationBufferStaticInput(
            relation.indexed_bounds_f32le,
            relation.indexed_ids_u32le,
            relation.count,
        )
        relation_batch = runtime.BoundedRelationBufferBatch(
            relation.source_bounds_f32le,
            relation.source_ids_u32le,
            relation.count,
            expected_rows=relation.expected_rows,
        )
        self.assertEqual(relation_static.indexed_count, workloads.RELATION_COUNT)
        self.assertEqual(relation_batch.expected_rows, relation.expected_rows)

        triangle = workloads.triangle_workload()
        triangle_static = runtime.TriangleReductionBufferStaticInput(
            triangle.vertices_f32le,
            triangle.triangles_u32le,
            triangle.vertex_count,
            triangle.triangle_count,
            event_capacity=triangle.query_count,
        )
        triangle_batch = runtime.TriangleReductionBufferBatch(
            triangle.query_origins_f32le,
            triangle.query_directions_f32le,
            triangle.query_tmax_f32le,
            triangle.query_count,
            query_weights_u64le=triangle.query_weights_u64le,
            expected_reduced_u64=triangle.expected_reduced_u64,
        )
        self.assertEqual(triangle_static.triangle_count, workloads.TRIANGLE_COUNT)
        self.assertEqual(
            triangle_batch.expected_reduced_u64,
            triangle.expected_reduced_u64,
        )

    def test_workload_module_imports_no_rtdl_or_gpu_package(self):
        source = sys.modules[workloads.__name__]
        names = set(source.__dict__)
        self.assertNotIn("numpy", names)
        self.assertNotIn("cupy", names)
        self.assertNotIn("rtdsl", names)


if __name__ == "__main__":
    unittest.main()
