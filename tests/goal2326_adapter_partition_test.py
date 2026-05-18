from __future__ import annotations

import importlib
from pathlib import Path
import unittest

import rtdsl.partner_adapters as flat


ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "adapters"
FORBIDDEN = (
    "geo",
    "road",
    "hazard",
    "rayjoin",
    "hausdorff",
    "dbscan",
    "facility",
    "robot",
    "pose",
)


class Goal2326AdapterPartitionTest(unittest.TestCase):
    def test_adapter_modules_are_contract_family_named(self) -> None:
        expected = {
            "collection.py",
            "columnar_payload.py",
            "partner_handoff.py",
            "prepared_handles.py",
            "reductions.py",
            "traversal.py",
        }
        self.assertTrue(ADAPTERS.exists())
        actual = {path.name for path in ADAPTERS.glob("*.py") if path.name != "__init__.py"}
        self.assertTrue(expected.issubset(actual))
        bad = sorted(
            name
            for name in actual
            if any(fragment in name.lower() for fragment in FORBIDDEN)
        )
        self.assertEqual(bad, [])

    def test_adapter_exports_are_contract_family_named(self) -> None:
        bad: list[str] = []
        for path in ADAPTERS.glob("*.py"):
            if path.name == "__init__.py":
                continue
            module = importlib.import_module(f"rtdsl.adapters.{path.stem}")
            for symbol in getattr(module, "__all__", ()):
                symbol_lower = symbol.lower()
                if any(fragment in symbol_lower for fragment in FORBIDDEN):
                    bad.append(f"{module.__name__}.{symbol}")
        self.assertEqual(bad, [])

    def test_reexports_preserve_existing_low_level_functions(self) -> None:
        checks = {
            "rtdsl.adapters.reductions": "partner_group_sum_by_key",
            "rtdsl.adapters.columnar_payload": "columnar_payload_to_partner_columns",
            "rtdsl.adapters.partner_handoff": "point_rows_to_partner_columns",
            "rtdsl.adapters.collection": "top_k_nearest_points_2d_partner_columns",
            "rtdsl.adapters.traversal": "segment_polygon_hitcount_optix_partner_columns",
            "rtdsl.adapters.prepared_handles": "prepare_segment_polygon_anyhit_optix_partner_device_scene",
        }
        for module_name, symbol in checks.items():
            module = importlib.import_module(module_name)
            self.assertIs(getattr(module, symbol), getattr(flat, symbol), module_name)


if __name__ == "__main__":
    unittest.main()
