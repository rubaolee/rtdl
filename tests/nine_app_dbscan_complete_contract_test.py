from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src/native/optix/rtdl_optix_core.cpp"
ADAPTERS = ROOT / "src/rtdsl/partner_adapters.py"
APP = ROOT / "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py"
HOME_SMOKE = ROOT / "scripts/goal5776_home_rtdbscan_real_scale_smoke.py"
PYOPTIX = ROOT / "experiments/v4_paper_apps_pyoptix"


class NineAppDbscanCompleteContractTest(unittest.TestCase):
    def test_predicate_false_source_ranges_are_maximal_and_complete(self):
        from rtdsl.partner_adapters import (
            _contiguous_predicate_false_source_ranges,
            _plan_predicate_false_second_pass_ranges,
        )

        self.assertEqual(
            _contiguous_predicate_false_source_ranges(
                np.asarray([0, 0, 1, 0, 1, 0, 0, 0], dtype=np.uint32)
            ),
            ((0, 2), (3, 1), (5, 3)),
        )
        self.assertEqual(
            _contiguous_predicate_false_source_ranges(
                np.asarray([1, 1, 1], dtype=np.uint32)
            ),
            (),
        )
        self.assertEqual(
            _plan_predicate_false_second_pass_ranges(
                point_count=4096,
                false_source_ranges=((4095, 1),),
                maximum_count=None,
            ),
            (((4095, 1),), "contiguous_predicate_false_source_ranges"),
        )
        self.assertEqual(
            _plan_predicate_false_second_pass_ranges(
                point_count=6,
                false_source_ranges=((1, 1), (3, 1), (5, 1)),
                maximum_count=None,
            ),
            (((0, 6),), "all_sources_due_predicate_range_fragmentation"),
        )

    def test_vectorized_partition_labels_match_first_occurrence_contract(self):
        from rtdsl.component_partition import canonical_partition_labels
        from rtdsl.v4_radius_graph_grouped_lowering import (
            _canonicalize_dense_partition_labels,
        )

        cases = (
            [-1, -1, -1],
            [7, 7, 3, -1, 9, 3, 7],
            [10, 2, 10, 4, 2, 4],
            [-4, 8, -1, 8, 6],
        )
        for labels in cases:
            with self.subTest(labels=labels):
                actual = _canonicalize_dense_partition_labels(
                    np.asarray(labels, dtype=np.int64)
                )
                self.assertEqual(
                    tuple(actual.tolist()),
                    canonical_partition_labels(labels),
                )

    def test_native_grouped_union_preserves_competing_parent_edges(self):
        source = CORE.read_text(encoding="utf-8")
        start = source.index("void union_grouped_min_root(")
        end = source.index("void apply_grouped_union_side_effect", start)
        union_source = source[start:end]
        self.assertEqual(
            union_source.count("atomicCAS(parent + high, high, low)"), 2)
        self.assertNotIn("atomicMin(parent + high, low)", union_source)
        self.assertIn("failed CAS recomputes both roots", union_source)

    def test_grouped_numba_path_materializes_exact_counts_then_flags(self):
        source = ADAPTERS.read_text(encoding="utf-8")
        start = source.index(
            "class PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D")
        end = source.index(
            "def prepare_optix_cupy_radius_graph_components_3d", start)
        grouped = source[start:end]
        self.assertIn("threshold=self.point_count", grouped)
        self.assertIn("self.uint32_greater_equal_flags_kernel", grouped)
        self.assertIn("exact_count_cache_reused", grouped)
        self.assertIn(
            '"neighbor_count_policy": "exact_full_degree_via_maximum_possible_threshold"',
            grouped,
        )
        self.assertNotIn(
            '"neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree"',
            grouped,
        )
        self.assertIn("contiguous_predicate_false_source_ranges", grouped)
        self.assertIn("apply_device_grouped_union_self_range", grouped)

    def test_application_contract_requires_all_three_full_outputs(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('arrays["neighbor_counts_u32.npy"]', source)
        self.assertGreaterEqual(
            source.count('"neighbor_counts": result.value["neighbor_counts"]'),
            2,
        )
        self.assertIn(
            'boundary_assignment_policy="lowest_component_root_two_pass"', source)

    def test_existing_gpu_smoke_projects_exact_neighbor_counts(self):
        source = HOME_SMOKE.read_text(encoding="utf-8")
        self.assertIn('columns["neighbor_counts"].copy_to_host()', source)
        self.assertIn('"neighbor_counts": tuple(counts)', source)

    def test_strong_public_pyoptix_arm_owns_full_application_path(self):
        owner = (PYOPTIX / "dbscan_owner.py").read_text(encoding="utf-8")
        device = (PYOPTIX / "dbscan_device.cu").read_text(encoding="utf-8")
        continuation = (PYOPTIX / "dbscan_continuation.cu").read_text(
            encoding="utf-8")
        self.assertNotIn("rtdsl", owner)
        self.assertIn("exact_count_and_core_cache_reused", owner)
        self.assertIn("if not count_and_core_reused:", owner)
        self.assertIn("2 if count_and_core_reused else 3", owner)
        self.assertIn('"neighbor_counts": tuple(map(int, counts))', owner)
        self.assertIn("atomicCAS(params.parent + high, high, low)", device)
        self.assertNotIn("atomicMin(params.parent + high", device)
        self.assertIn("optixIgnoreIntersection()", device)
        self.assertIn('extern "C" __global__ void write_labels', continuation)
        self.assertNotIn("#include <limits.h>", device + continuation)

    def test_public_pyoptix_host_abi_locks_every_parameter_offset(self):
        from experiments.v4_paper_apps_pyoptix import dbscan_owner

        expected_offsets = {
            **{name: index * 8 for index, name in enumerate(
                dbscan_owner.POINTERS)},
            "count": 64,
            "min_points": 68,
            "mode": 72,
            "reserved": 76,
            "radius": 80,
            "trace_tmax": 84,
        }
        self.assertEqual(dbscan_owner.PARAM_DTYPE.itemsize, 88)
        self.assertEqual(
            {name: dbscan_owner.PARAM_DTYPE.fields[name][1]
             for name in dbscan_owner.PARAM_DTYPE.names},
            expected_offsets,
        )

    def test_public_pyoptix_comparator_requires_every_output_column(self):
        adapter = (PYOPTIX / "dbscan_adapter.py").read_text(encoding="utf-8")
        self.assertIn('set(actual) != set(expected)', adapter)
        self.assertIn('"neighbor_counts_u32.npy"', adapter)
        self.assertIn('"canonical_component_labels"', adapter)


if __name__ == "__main__":
    unittest.main()
