from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
WRITE_ARTIFACT = ROOT / "docs" / "reports" / "goal3509_overlay_area_binary_prepared_payload_cache_write_pod_2026-06-05.json"
READ_ARTIFACT = ROOT / "docs" / "reports" / "goal3509_overlay_area_binary_prepared_payload_cache_read_pod_2026-06-05.json"


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

    def test_pod_artifacts_record_binary_write_then_read_cache_route(self) -> None:
        write_data = json.loads(WRITE_ARTIFACT.read_text(encoding="utf-8"))
        read_data = json.loads(READ_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(write_data["schema"], "rtdl.goal3509.overlay_area_binary_prepared_payload_cache.v1")
        self.assertEqual(read_data["schema"], "rtdl.goal3509.overlay_area_binary_prepared_payload_cache.v1")
        self.assertEqual(write_data["goal"], 3509)
        self.assertEqual(read_data["goal"], 3509)
        self.assertTrue(write_data["rtdl_commit"].startswith("d1a9ac19"))
        self.assertTrue(read_data["rtdl_commit"].startswith("d1a9ac19"))

        self.assertEqual(write_data["payload_cache_mode"], "refresh")
        self.assertEqual(read_data["payload_cache_mode"], "read")
        self.assertEqual(write_data["payload_cache_format"], "binary")
        self.assertEqual(read_data["payload_cache_format"], "binary")
        self.assertTrue(write_data["payload_cache_metadata"]["write_used"])
        self.assertFalse(write_data["payload_cache_metadata"]["read_used"])
        self.assertFalse(read_data["payload_cache_metadata"]["write_used"])
        self.assertTrue(read_data["payload_cache_metadata"]["read_used"])

        for side in ("left", "right"):
            with self.subTest(side=side):
                side_metadata = read_data["payload_cache_metadata"][side]
                self.assertEqual(side_metadata["format"], "binary")
                self.assertEqual(side_metadata["schema"], "rtdl.goal3509.overlay_area_binary_prepared_payload_cache.v1")
                self.assertIn("_payload_columns.npz", side_metadata["payload_columns"])
                self.assertIn("_shape_component_columns.npz", side_metadata["shape_component_columns"])
                self.assertIn("_geometry_wkb_columns.npz", side_metadata["geometry_wkb_columns"])
                self.assertGreater(side_metadata["component_count"], 0)
                self.assertGreater(side_metadata["payload_triangle_count"], 0)

        for key in (
            "relation_row_count",
            "supported_relation_row_count",
            "unsupported_relation_row_count",
            "exact_positive_row_count",
            "observed_positive_row_count",
            "left_payload_triangle_count",
            "right_payload_triangle_count",
            "tile_task_count",
            "planned_triangle_pair_count",
            "expected_triangle_pair_count",
        ):
            with self.subTest(key=key):
                self.assertEqual(write_data[key], read_data[key])

        self.assertEqual(read_data["relation_row_count"], 4543)
        self.assertEqual(read_data["supported_relation_row_count"], 2149)
        self.assertEqual(read_data["tile_task_count"], 11617)
        self.assertEqual(read_data["planned_triangle_pair_count"], 4070240)
        self.assertLess(read_data["total_area_abs_error"], 1.0e-8)
        self.assertLess(read_data["max_relation_abs_error"], 2.0e-9)
        self.assertTrue(read_data["positive_row_count_match"])

        self.assertLess(write_data["timing_sec"]["payload_cache_write"], 0.2)
        self.assertEqual(read_data["timing_sec"]["payload_cache_write"], 0.0)
        self.assertGreater(read_data["timing_sec"]["payload_cache_load"], 0.0)
        self.assertLess(read_data["timing_sec"]["payload_cache_load"], 0.2)
        self.assertEqual(
            read_data["timing_sec"]["geometry_plus_payload_prepare"],
            read_data["timing_sec"]["payload_cache_load"],
        )

        for data in (write_data, read_data):
            for field, value in data["claim_boundary"].items():
                with self.subTest(field=field, mode=data["payload_cache_mode"]):
                    self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
