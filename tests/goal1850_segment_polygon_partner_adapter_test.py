from __future__ import annotations

import pathlib
import json
import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import partner_adapters


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1850_segment_polygon_partner_adapter_2026-05-13.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1850_segment_polygon_partner_adapter_pod_smoke.json"


class _FakeColumn:
    def __init__(self, values):
        self.values = list(values)


class _FakeScene:
    def __init__(self) -> None:
        self.closed = False

    def write_device_any_hit_all_witnesses(self, rays, witness_ray_ids, witness_primitive_ids):
        witness_ray_ids.values[:3] = [101, 101, 101]
        witness_primitive_ids.values[:3] = [12, 11, 11]
        return {
            "metadata": {
                "emitted_count": 3,
                "overflowed": False,
                "true_zero_copy_authorized": True,
            }
        }

    def close(self) -> None:
        self.closed = True


def _fake_partner_module(name: str):
    if name != "torch":
        raise AssertionError(name)
    return {
        "name": "torch",
        "device": "cuda:0",
        "uint32": "uint32",
        "float64": "float64",
        "float32": "float32",
        "tensor": lambda values, dtype, device: _FakeColumn(values),
        "zeros": lambda shape, dtype, device: _FakeColumn([0] * int(shape[0])),
        "sync": lambda: None,
        "to_host": lambda value: [int(item) for item in value.values],
    }


class Goal1850SegmentPolygonPartnerAdapterTest(unittest.TestCase):
    def test_adapter_is_exported_as_python_app_layer_not_native_domain_surface(self) -> None:
        adapter_source = ADAPTER.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIs(rt.segment_polygon_anyhit_rows_optix_partner, partner_adapters.segment_polygon_anyhit_rows_optix_partner)
        self.assertIn("write_device_any_hit_all_witnesses", adapter_source)
        self.assertIn("generic_ray_primitive_witness_pairs", adapter_source)
        self.assertIn("caller_supplied_partner_device_columns", adapter_source)
        self.assertIn("_require_uint32_id", adapter_source)
        self.assertIn("whole_app_speedup_claim_authorized", adapter_source)
        self.assertIn("v2_0_release_authorized", adapter_source)
        self.assertIn('ids.append(_require_uint32_id(polygon.id, "polygon"))', adapter_source)
        self.assertIn("sorted(set(zip(ray_ids, primitive_ids)))", adapter_source)
        self.assertIn("segment_polygon_anyhit_rows_optix_partner", init_source)
        self.assertIn("segment_polygon_anyhit_rows_optix_partner_columns", init_source)

    def test_adapter_deduplicates_generic_witness_pairs_into_app_rows(self) -> None:
        scene = _FakeScene()
        segments = (rt.Segment(101, -0.25, 0.25, 1.25, 0.25),)
        polygons = (
            rt.Polygon(11, ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))),
            rt.Polygon(12, ((0.25, 0.20), (0.75, 0.20), (0.25, 0.80))),
        )

        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            with mock.patch.object(
                partner_adapters._optix,
                "prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene",
                return_value=scene,
            ):
                result = rt.segment_polygon_anyhit_rows_optix_partner(
                    segments,
                    polygons,
                    partner="torch",
                    output_capacity=4,
                    return_metadata=True,
                )

        self.assertEqual(
            result["rows"],
            (
                {"segment_id": 101, "polygon_id": 11},
                {"segment_id": 101, "polygon_id": 12},
            ),
        )
        self.assertTrue(scene.closed)
        self.assertEqual(result["metadata"]["adapter"], "segment_polygon_anyhit_rows_optix_partner")
        self.assertEqual(result["metadata"]["native_engine_row_contract"], "generic_ray_primitive_witness_pairs")
        self.assertFalse(result["metadata"]["v2_0_release_authorized"])
        self.assertFalse(result["metadata"]["whole_app_speedup_claim_authorized"])

    def test_record_adapter_rejects_ids_that_do_not_fit_native_witness_contract(self) -> None:
        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            with self.assertRaisesRegex(ValueError, "segment IDs must fit uint32"):
                rt.segment_polygon_anyhit_rows_optix_partner(
                    (rt.Segment(2**32, 0.0, 0.0, 1.0, 0.0),),
                    (rt.Polygon(11, ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))),),
                )

            with self.assertRaisesRegex(ValueError, "polygon IDs must fit uint32"):
                rt.segment_polygon_anyhit_rows_optix_partner(
                    (rt.Segment(101, 0.0, 0.0, 1.0, 0.0),),
                    (rt.Polygon(-1, ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))),),
                )

    def test_column_adapter_keeps_caller_supplied_partner_input_contract(self) -> None:
        scene = _FakeScene()
        segment_ray_columns = {
            "ids": _FakeColumn([101, 102]),
            "ox": _FakeColumn([-0.25, 2.0]),
            "oy": _FakeColumn([0.25, 2.0]),
            "dx": _FakeColumn([1.5, 1.0]),
            "dy": _FakeColumn([0.0, 0.0]),
            "tmax": _FakeColumn([1.0, 1.0]),
        }
        polygon_triangle_columns = {
            "ids": _FakeColumn([11, 12]),
            "x0": _FakeColumn([0.0, 0.25]),
            "y0": _FakeColumn([0.0, 0.20]),
            "x1": _FakeColumn([1.0, 0.75]),
            "y1": _FakeColumn([0.0, 0.20]),
            "x2": _FakeColumn([0.0, 0.25]),
            "y2": _FakeColumn([1.0, 0.80]),
        }
        aabbs = _FakeColumn([0.0] * 12)

        with mock.patch.object(partner_adapters, "_partner_module", side_effect=_fake_partner_module):
            with mock.patch.object(
                partner_adapters._optix,
                "prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene",
                return_value=scene,
            ) as prepare_scene:
                result = rt.segment_polygon_anyhit_rows_optix_partner_columns(
                    segment_ray_columns,
                    polygon_triangle_columns,
                    aabbs,
                    partner="torch",
                    output_capacity=4,
                    return_metadata=True,
                )

        prepare_scene.assert_called_once_with(polygon_triangle_columns, aabbs)
        self.assertEqual(
            result["rows"],
            (
                {"segment_id": 101, "polygon_id": 11},
                {"segment_id": 101, "polygon_id": 12},
            ),
        )
        self.assertEqual(result["metadata"]["adapter"], "segment_polygon_anyhit_rows_optix_partner_columns")
        self.assertEqual(result["metadata"]["input_contract"], "caller_supplied_partner_device_columns")
        self.assertFalse(result["metadata"]["v2_0_release_authorized"])

    def test_empty_inputs_return_empty_rows_without_native_scene(self) -> None:
        with mock.patch.object(
            partner_adapters._optix,
            "prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene",
        ) as prepare_scene:
            result = rt.segment_polygon_anyhit_rows_optix_partner(
                (),
                (),
                partner="torch",
                return_metadata=True,
            )

        self.assertEqual(result["rows"], ())
        self.assertEqual(result["metadata"]["app_rows_emitted"], 0)
        prepare_scene.assert_not_called()

    def test_report_and_pod_smoke_keep_v2_0_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("pass-with-boundary", report)
        self.assertIn("ray/primitive witness pairs", report)
        self.assertIn("not a v2.0 release gate pass", report)
        self.assertEqual(artifact["status"], "pass")
        for partner in ("cupy", "torch"):
            with self.subTest(partner=partner):
                result = artifact["results"][partner]
                self.assertEqual(
                    result["rows"],
                    [
                        {"polygon_id": 11, "segment_id": 101},
                        {"polygon_id": 12, "segment_id": 101},
                    ],
                )
                metadata = result["metadata"]
                self.assertEqual(metadata["adapter"], "segment_polygon_anyhit_rows_optix_partner")
                self.assertEqual(metadata["native_engine_row_contract"], "generic_ray_primitive_witness_pairs")
                self.assertIs(metadata["true_zero_copy_authorized"], True)
                self.assertIs(metadata["exact_row_semantics_authorized"], True)
                self.assertIs(metadata["v2_0_release_authorized"], False)
                self.assertIs(metadata["whole_app_speedup_claim_authorized"], False)


if __name__ == "__main__":
    unittest.main()
