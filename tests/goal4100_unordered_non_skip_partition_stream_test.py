from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"


class Goal4100UnorderedNonSkipPartitionStreamTest(unittest.TestCase):
    def test_unordered_non_skip_mode_is_explicit_and_labeled(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        for text in (source, app):
            self.assertIn("device_count_then_emit_non_skip_unordered", text)
        self.assertIn("sort_pairs=pair_enumeration != \"device_count_then_emit_non_skip_unordered\"", source)
        self.assertIn("device_atomic_append_unordered", source)
        self.assertIn("pair_order", source)

    def test_unordered_non_skip_preserves_component_signature_when_cupy_available(self) -> None:
        try:
            import cupy  # noqa: F401
        except Exception:
            self.skipTest("CuPy is not available in this local environment")

        points = [
            (0.00, 0.00, 0.00),
            (0.01, 0.00, 0.00),
            (0.02, 0.00, 0.00),
            (1.00, 1.00, 1.00),
            (1.01, 1.00, 1.00),
            (4.00, 4.00, 4.00),
        ]
        sorted_result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit_non_skip",
            validate_summary_same_contract=False,
            validate_against_component_labels=False,
        )
        unordered_result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit_non_skip_unordered",
            validate_summary_same_contract=False,
            validate_against_component_labels=True,
        )
        self.assertEqual(unordered_result["metadata"]["status"], "accept")
        self.assertTrue(unordered_result["metadata"]["same_contract_against_component_labels"])
        self.assertEqual(
            tuple(unordered_result["columns"]["component_size_signature"]),
            tuple(sorted_result["columns"]["component_size_signature"]),
        )
        self.assertEqual(
            unordered_result["metadata"]["partition_summary_pair_order"],
            "device_atomic_append_unordered",
        )


if __name__ == "__main__":
    unittest.main()
