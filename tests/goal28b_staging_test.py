import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import gzip
import json

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from scripts import goal28b_stage_uscounty_zipcode as stage_mod
from scripts.goal28b_stage_uscounty_zipcode import render_summary


class Goal28BStagingTest(unittest.TestCase):
    def test_feature_service_registry_includes_county_and_zipcode(self) -> None:
        layers = {layer.asset_id: layer for layer in rt.rayjoin_feature_service_layers()}
        self.assertIn("uscounty_feature_layer", layers)
        self.assertIn("zipcode_feature_layer", layers)
        self.assertEqual(layers["uscounty_feature_layer"].feature_count, 3144)
        self.assertEqual(layers["zipcode_feature_layer"].feature_count, 32294)
        self.assertEqual(layers["zipcode_feature_layer"].layer_id, 0)

    def test_arcgis_geojson_query_url_contains_expected_paging_fields(self) -> None:
        url = rt.build_arcgis_query_url(
            "https://example.com/FeatureServer",
            0,
            offset=2000,
            record_count=1000,
            response_format="json",
        )
        self.assertIn("/0/query?", url)
        self.assertIn("resultOffset=2000", url)
        self.assertIn("resultRecordCount=1000", url)
        self.assertIn("f=json", url)
        self.assertIn("orderByFields=OBJECTID", url)

    def test_render_summary_mentions_boundary_note_and_assets(self) -> None:
        summary = render_summary(
            {
                "generated_epoch": 1,
                "host_label": "lx1",
                "assets": [
                    {
                        "asset_id": "uscounty_feature_layer",
                        "expected_feature_count": 3144,
                        "downloaded_feature_count": 3144,
                        "pages": [{}, {}, {}],
                        "status": "complete",
                        "output_root": "/tmp/uscounty",
                    }
                ],
            }
        )
        self.assertIn("uscounty_feature_layer", summary)
        self.assertIn("Boundary note", summary)
        self.assertIn("raw paginated FeatureServer exports", summary)

    def test_stage_asset_can_resume_with_existing_pages(self) -> None:
        asset = rt.RayJoinFeatureServiceLayer(
            asset_id="zipcode_feature_layer",
            title="Zipcode",
            source_url="https://example.com/item",
            service_url="https://example.com/FeatureServer",
            layer_id=0,
            geometry_type="esriGeometryPolygon",
            max_record_count=2,
            feature_count=2,
            current_status="test",
            notes="",
        )
        payload = {"features": [{"attributes": {"OBJECTID": 1}}, {"attributes": {"OBJECTID": 2}}]}
        with tempfile.TemporaryDirectory() as tmpdir:
            asset_root = Path(tmpdir) / asset.asset_id
            asset_root.mkdir(parents=True, exist_ok=True)
            with gzip.open(asset_root / "page_000000.json.gz", "wt", encoding="utf-8") as handle:
                json.dump(payload, handle)
            with mock.patch.object(stage_mod, "fetch_json", side_effect=[{"maxRecordCount": 2}, {"count": 2}]):
                with mock.patch.object(stage_mod, "fetch_bytes", side_effect=AssertionError("should not fetch page")):
                    manifest = stage_mod.stage_asset(
                        asset,
                        output_dir=Path(tmpdir),
                        page_size=2,
                        sleep_sec=0.0,
                        use_gzip=True,
                        response_format="json",
                        resume_skip_existing=True,
                    )
        self.assertEqual(manifest["downloaded_feature_count"], 2)
        self.assertTrue(manifest["pages"][0]["reused_existing"])

    def test_stage_asset_refetches_invalid_existing_tail_page(self) -> None:
        asset = rt.RayJoinFeatureServiceLayer(
            asset_id="zipcode_feature_layer",
            title="Zipcode",
            source_url="https://example.com/item",
            service_url="https://example.com/FeatureServer",
            layer_id=0,
            geometry_type="esriGeometryPolygon",
            max_record_count=2,
            feature_count=2,
            current_status="test",
            notes="",
        )
        payload = {"features": [{"attributes": {"OBJECTID": 1}}, {"attributes": {"OBJECTID": 2}}]}
        with tempfile.TemporaryDirectory() as tmpdir:
            asset_root = Path(tmpdir) / asset.asset_id
            asset_root.mkdir(parents=True, exist_ok=True)
            (asset_root / "page_000000.json.gz").write_bytes(b"broken")
            with mock.patch.object(stage_mod, "fetch_json", side_effect=[{"maxRecordCount": 2}, {"count": 2}]):
                with mock.patch.object(stage_mod, "fetch_bytes", return_value=json.dumps(payload).encode("utf-8")):
                    manifest = stage_mod.stage_asset(
                        asset,
                        output_dir=Path(tmpdir),
                        page_size=2,
                        sleep_sec=0.0,
                        use_gzip=True,
                        response_format="json",
                        resume_skip_existing=True,
                    )
        self.assertEqual(manifest["downloaded_feature_count"], 2)
        self.assertFalse(manifest["pages"][0]["reused_existing"])


if __name__ == "__main__":
    unittest.main()
