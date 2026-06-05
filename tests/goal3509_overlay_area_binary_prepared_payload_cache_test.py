from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"


class Goal3509OverlayAreaBinaryPreparedPayloadCacheTest(unittest.TestCase):
    def test_prepared_payload_numpy_column_round_trip_preserves_contract(self) -> None:
        payload = rt.prepare_simple_polygon_component_payload(
            (
                ((0.0, 0.0), (4.0, 0.0), (4.0, 1.0), (1.0, 1.0), (1.0, 4.0), (0.0, 4.0)),
                ((5.0, 5.0), (7.0, 5.0), (6.0, 8.0)),
            ),
            source_shape_ids=(101, 102),
        )

        columns = rt.prepared_simple_polygon_component_payload_to_numpy_columns(payload)
        restored = rt.prepared_simple_polygon_component_payload_from_numpy_columns(columns)

        self.assertEqual(
            str(columns["schema"].reshape(-1)[0]),
            rt.V2_8_OVERLAY_AREA_PREPARED_PAYLOAD_SERIALIZATION_VERSION,
        )
        self.assertEqual(restored.triangles, payload.triangles)
        self.assertEqual(
            tuple(component.to_metadata() for component in restored.components),
            tuple(component.to_metadata() for component in payload.components),
        )

    def test_runner_exposes_binary_cache_format_as_goal3509(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--payload-cache-format",
            'choices=("json", "binary")',
            'default="json"',
            "_binary_cache_schema",
            "_binary_payload_npz_path",
            "_binary_shape_components_npz_path",
            "_binary_geometry_wkb_npz_path",
            "prepared_simple_polygon_component_payload_to_numpy_columns",
            "prepared_simple_polygon_component_payload_from_numpy_columns",
            "rtdl.goal3509.overlay_area_binary_prepared_payload_cache.v1",
            '3509 if payload_cache_format == "binary" else 3507',
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
