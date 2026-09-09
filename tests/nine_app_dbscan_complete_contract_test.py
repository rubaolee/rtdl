from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src/native/optix/rtdl_optix_core.cpp"
ADAPTERS = ROOT / "src/rtdsl/partner_adapters.py"
APP = ROOT / "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py"


class NineAppDbscanCompleteContractTest(unittest.TestCase):
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

    def test_application_contract_requires_all_three_full_outputs(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('arrays["neighbor_counts_u32.npy"]', source)
        self.assertGreaterEqual(
            source.count('"neighbor_counts": result.value["neighbor_counts"]'),
            2,
        )
        self.assertIn(
            'boundary_assignment_policy="lowest_component_root_two_pass"', source)


if __name__ == "__main__":
    unittest.main()
