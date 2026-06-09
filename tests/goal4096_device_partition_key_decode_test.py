from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"


class Goal4096DevicePartitionKeyDecodeTest(unittest.TestCase):
    def test_device_pair_kernel_decodes_unique_cells_without_host_key_arrays(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")

        self.assertIn("const long long encoded = unique_cells[left];", source)
        self.assertIn("const long long base_x = encoded / plane;", source)
        self.assertIn("occupied_key_x = (local_key_x + min_kx).astype", source)
        self.assertNotIn("const int* key_x", source)
        self.assertNotIn("const int* key_y", source)
        self.assertNotIn("const int* key_z", source)
        self.assertNotIn("key_rows=key_rows", source)

    def test_non_skip_device_mode_preserves_small_signature_when_cupy_available(self) -> None:
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
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit_non_skip",
            validate_summary_same_contract=False,
            validate_against_component_labels=True,
        )
        self.assertEqual(result["metadata"]["status"], "accept")
        self.assertTrue(result["metadata"]["same_contract_against_component_labels"])
        self.assertEqual(tuple(result["columns"]["component_size_signature"]), (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
