import hashlib
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "data" / "generated" / "goal5303_arcgis_county_zcta_bounded" / "manifest.json"


def _load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _repo_path(path_text: str) -> pathlib.Path:
    return ROOT / pathlib.Path(path_text.replace("\\", "/"))


class Goal5303CountyZctaArcgisBoundedFixtureTest(unittest.TestCase):
    def test_manifest_declares_level_b_fixture_not_exact_paper_input(self) -> None:
        manifest = _load_manifest()
        self.assertEqual(manifest["schema"], "rtdl.paper_reproduction.xhd.goal5303.arcgis_county_zcta_bounded_fixture.v1")
        self.assertEqual(manifest["goal"], "Goal5303")
        self.assertEqual(
            manifest["status"],
            "arcgis_county_zcta_bounded_fixture_ready__level_b_only__not_exact_paper_input",
        )

        source = manifest["source_contract"]
        self.assertIn("ArcGIS name-matched services", source["source_family"])
        self.assertEqual(source["query_order"], "OBJECTID")
        self.assertEqual(source["out_sr"], 4326)
        self.assertEqual(source["county_feature_count_requested"], 3)
        self.assertEqual(source["zipcode_feature_count_requested"], 5)
        self.assertIn("USA_Census_Counties", source["county_service"])
        self.assertIn("USA_ZIP_Code_Areas_anaylsis", source["zipcode_service"])

        author_loader = manifest["author_loader_contract"]
        self.assertEqual(author_loader["input_type"], "wkt")
        self.assertEqual(author_loader["n_dims"], 2)
        self.assertIs(author_loader["normalize"], False)
        self.assertIs(author_loader["one_geometry_per_line"], True)
        self.assertIs(author_loader["polygon_outer_ring_only_for_author_point_count"], True)

        claims = manifest["claim_boundary"]
        self.assertIs(claims["level_b_same_source_fixture"], True)
        self.assertIs(claims["exact_paper_dataset_reproduction_claimed"], False)
        self.assertIs(claims["geo_correctness_claimed"], False)
        self.assertIs(claims["figure5_reproduction_claimed"], False)
        self.assertIs(claims["performance_ratio_claimed"], False)

    def test_wkt_outputs_exist_with_manifest_hashes_and_one_geometry_per_line(self) -> None:
        manifest = _load_manifest()
        expected = {
            "county": (3, {"Polygon", "MultiPolygon"}),
            "zipcode": (5, {"Polygon", "MultiPolygon"}),
        }
        for name, (expected_lines, allowed_types) in expected.items():
            with self.subTest(output=name):
                meta = manifest["outputs"][name]
                path = _repo_path(meta["path"])
                self.assertTrue(path.exists(), path)
                data = path.read_bytes()
                self.assertEqual(len(data), meta["bytes"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), meta["sha256"])

                lines = path.read_text(encoding="utf-8").splitlines()
                self.assertEqual(len(lines), expected_lines)
                self.assertEqual(meta["line_count"], expected_lines)
                self.assertEqual(meta["feature_count"], expected_lines)
                self.assertGreater(meta["outer_ring_point_count_author_loader_estimate"], 0)
                self.assertEqual(set(meta["geometry_types"]).issubset(allowed_types), True)
                self.assertEqual(sorted(meta["object_ids"]), list(range(1, expected_lines + 1)))
                self.assertEqual(len(meta["sample_names"]), expected_lines)
                self.assertEqual(len(meta["bbox"]), 4)
                self.assertLess(meta["bbox"][0], meta["bbox"][1])
                self.assertLess(meta["bbox"][2], meta["bbox"][3])
                for line in lines:
                    self.assertRegex(line, r"^(POLYGON|MULTIPOLYGON) ")

    def test_comparison_is_explicitly_deferred_to_later_pod_gate(self) -> None:
        readiness = _load_manifest()["comparison_readiness"]
        self.assertIs(readiness["author_hd_exec_ready"], False)
        self.assertIs(readiness["rtdl_route_ready"], False)
        self.assertIn("separate gate", readiness["reason"])
        command_shape = readiness["first_author_command_shape"]
        self.assertIn("-input_type wkt", command_shape)
        self.assertIn("-n_dims 2", command_shape)
        self.assertIn("-variant rt", command_shape)
        self.assertIn("-execution gpu", command_shape)
        self.assertIn("-normalize=false", command_shape)


if __name__ == "__main__":
    unittest.main()
