from __future__ import annotations

import json
import pathlib
import unittest

import rtdsl as rt
from rtdsl import partner_adapters


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal1853_segment_polygon_partner_column_adapter_2026-05-13.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1853_segment_polygon_partner_column_adapter_pod_smoke.json"


class Goal1853SegmentPolygonPartnerColumnAdapterTest(unittest.TestCase):
    def test_public_column_adapter_surface_is_exported(self) -> None:
        adapter_source = ADAPTER.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIsNotNone(rt.segment_polygon_anyhit_rows_optix_partner_columns)
        self.assertIn("segment_polygon_anyhit_rows_optix_partner_columns", adapter_source)
        self.assertIn("caller_supplied_partner_device_columns", adapter_source)
        self.assertIn("write_device_any_hit_all_witnesses", adapter_source)
        self.assertIn("generic_ray_primitive_witness_pairs", adapter_source)
        self.assertIn("segment_polygon_anyhit_rows_optix_partner_columns", init_source)

    def test_report_and_pod_artifact_preserve_claim_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("pass-with-boundary", report)
        self.assertIn("caller-supplied PyTorch/CuPy GPU columns", report)
        self.assertIn("not a v2.0 release gate pass", report)
        self.assertEqual(artifact["status"], "pass")
        self.assertIn("NVIDIA RTX A4500", artifact["gpu"])

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
                self.assertEqual(metadata["adapter"], "segment_polygon_anyhit_rows_optix_partner_columns")
                self.assertEqual(metadata["input_contract"], "caller_supplied_partner_device_columns")
                self.assertEqual(metadata["native_engine_row_contract"], "generic_ray_primitive_witness_pairs")
                self.assertIs(metadata["direct_device_pointer_observed"], True)
                self.assertIs(metadata["true_zero_copy_authorized"], True)
                self.assertIs(metadata["exact_row_semantics_authorized"], True)
                self.assertIs(metadata["v2_0_release_authorized"], False)
                self.assertIs(metadata["whole_app_speedup_claim_authorized"], False)

    def test_column_length_failure_is_explicit_for_unsupported_column_objects(self) -> None:
        with self.assertRaisesRegex(ValueError, "ids column must expose shape"):
            partner_adapters._column_length({"ids": object()}, "ids")


if __name__ == "__main__":
    unittest.main()
