from __future__ import annotations

import unittest

import rtdsl as rt


class Goal35BlockgroupWaterbodiesTest(unittest.TestCase):
    def test_blockgroup_feature_service_is_registered(self) -> None:
        assets = {asset.asset_id: asset for asset in rt.rayjoin_feature_service_layers()}
        self.assertIn("blockgroup_feature_layer", assets)
        self.assertEqual(
            assets["blockgroup_feature_layer"].service_url,
            "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_BlockGroups/FeatureServer",
        )

    def test_build_arcgis_query_url_supports_envelope_filter(self) -> None:
        url = rt.build_arcgis_query_url(
            "https://example.com/FeatureServer",
            0,
            offset=0,
            record_count=100,
            geometry="-1,2,3,4",
            geometry_type="esriGeometryEnvelope",
            in_sr=4326,
            spatial_rel="esriSpatialRelIntersects",
        )
        self.assertIn("geometry=-1%2C2%2C3%2C4", url)
        self.assertIn("geometryType=esriGeometryEnvelope", url)
        self.assertIn("inSR=4326", url)
        self.assertIn("spatialRel=esriSpatialRelIntersects", url)


if __name__ == "__main__":
    unittest.main()
