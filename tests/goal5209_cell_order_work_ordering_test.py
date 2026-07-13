from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SCRIPT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_cell_mbr_frontier_route_gate.py"


def _load_route_module():
    spec = importlib.util.spec_from_file_location("run_xhd_cell_mbr_frontier_route_gate_goal5209", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load route module from {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CellOrderWorkOrderingTest(unittest.TestCase):
    def test_point_count_order_preserves_cell_payloads(self) -> None:
        route = _load_route_module()
        columns = {
            "cell_ids": np.asarray([30, 10, 20], dtype=np.int64),
            "point_begin_offsets": np.asarray([300, 100, 200], dtype=np.uint64),
            "point_counts": np.asarray([3, 1, 3], dtype=np.uint64),
            "min_x": np.asarray([3.0, 1.0, 2.0], dtype=np.float64),
            "max_x": np.asarray([3.5, 1.5, 2.5], dtype=np.float64),
            "metadata": {"ignored": True},
        }

        ordered, metadata = route._order_cell_columns(columns, cell_order="point-count-asc")

        self.assertEqual(metadata["cell_order"], "point-count-asc")
        self.assertTrue(metadata["cell_order_changed"])
        self.assertEqual(ordered["cell_ids"].tolist(), [10, 20, 30])
        self.assertEqual(ordered["point_begin_offsets"].tolist(), [100, 200, 300])
        self.assertEqual(ordered["point_counts"].tolist(), [1, 3, 3])
        self.assertEqual(ordered["metadata"], {"ignored": True})

    def test_native_order_is_passthrough(self) -> None:
        route = _load_route_module()
        columns = {
            "cell_ids": np.asarray([2, 1], dtype=np.int64),
            "point_counts": np.asarray([4, 2], dtype=np.uint64),
        }

        ordered, metadata = route._order_cell_columns(columns, cell_order="native")

        self.assertIs(ordered, columns)
        self.assertFalse(metadata["cell_order_changed"])
        self.assertEqual(metadata["cell_order_contract"], "input_order_preserved")

    def test_unknown_order_fails_closed(self) -> None:
        route = _load_route_module()
        columns = {
            "cell_ids": np.asarray([1], dtype=np.int64),
            "point_counts": np.asarray([1], dtype=np.uint64),
        }

        with self.assertRaisesRegex(ValueError, "--cell-order"):
            route._order_cell_columns(columns, cell_order="paper-special")


if __name__ == "__main__":
    unittest.main()
