import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
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


if __name__ == "__main__":
    unittest.main()
