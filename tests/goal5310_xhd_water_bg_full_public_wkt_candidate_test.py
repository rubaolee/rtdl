import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5310_water_bg_full_public_wkt_candidate.py"
)
FULL_MANIFEST = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "data"
    / "generated"
    / "goal5310_water_bg_full_public_wkt_candidate"
    / "manifest.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5310_wkt", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5310XhdWaterBgFullPublicWktCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()

    def test_polygon_wkt_closes_outer_ring_and_preserves_holes(self) -> None:
        geometry = {
            "type": "Polygon",
            "coordinates": [
                [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]],
                [[0.2, 0.2], [0.4, 0.2], [0.2, 0.2]],
            ],
        }

        wkt, point_count, bounds = self.mod._geometry_to_wkt_and_meta(geometry)

        self.assertTrue(wkt.startswith("POLYGON "))
        self.assertIn("0 0", wkt)
        self.assertEqual(point_count, 4)
        self.assertEqual(bounds, [0.0, 1.0, 0.0, 1.0])

    def test_multipolygon_wkt_counts_outer_rings_only_for_author_contract(self) -> None:
        geometry = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0.0, 0.0], [1.0, 0.0], [0.0, 0.0]]],
                [[[2.0, 2.0], [3.0, 2.0], [3.0, 3.0]]],
            ],
        }

        wkt, point_count, bounds = self.mod._geometry_to_wkt_and_meta(geometry)

        self.assertTrue(wkt.startswith("MULTIPOLYGON "))
        self.assertEqual(point_count, 7)
        self.assertEqual(bounds, [0.0, 3.0, 0.0, 3.0])

    def test_checkpoint_requires_matching_output_file_for_resume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            checkpoint = tmp_path / "waterbodies.json"
            output = tmp_path / "missing.wkt"
            checkpoint.write_text(
                json.dumps(
                    {
                        "key": "waterbodies",
                        "features_seen": 1,
                        "pages_seen": 1,
                        "author_loader_point_count": 3,
                        "geometry_types": {"Polygon": 1},
                        "output_wkt": str(output),
                        "complete": False,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "output WKT is missing"):
                self.mod._load_checkpoint(checkpoint, key="waterbodies", service_count=2, output_wkt=output)

    def test_claim_boundary_in_default_parser_mentions_no_exact_or_performance_claim(self) -> None:
        parser = self.mod.build_parser()
        args = parser.parse_args(["--max-pages", "1"])
        self.assertIn("goal5310_water_bg_full_public_wkt_candidate", args.output_dir)
        self.assertEqual(args.services, ["waterbodies", "blockgroups"])

    def test_full_public_manifest_records_complete_water_bg_candidate(self) -> None:
        payload = json.loads(FULL_MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5310.water_bg_full_public_wkt_candidate.v1",
        )
        self.assertEqual(payload["status"], "water_bg_full_public_wkt_candidate_complete")
        self.assertTrue(payload["comparison_readiness"]["author_hd_exec_ready"])
        self.assertTrue(payload["comparison_readiness"]["rtdl_route_ready"])

        water = payload["services"]["waterbodies"]
        self.assertTrue(water["complete"])
        self.assertEqual(water["features_seen"], 463_591)
        self.assertEqual(water["author_loader_point_count"], 22_824_823)
        self.assertEqual(water["output_bytes"], 741_925_630)
        self.assertEqual(
            water["sha256"],
            "0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39",
        )

        blockgroups = payload["services"]["blockgroups"]
        self.assertTrue(blockgroups["complete"])
        self.assertEqual(blockgroups["features_seen"], 239_203)
        self.assertEqual(blockgroups["author_loader_point_count"], 52_271_467)
        self.assertEqual(blockgroups["output_bytes"], 1_560_257_609)
        self.assertEqual(
            blockgroups["sha256"],
            "8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e",
        )

    def test_full_public_manifest_keeps_claim_boundary_bounded(self) -> None:
        boundary = json.loads(FULL_MANIFEST.read_text(encoding="utf-8"))["claim_boundary"]

        self.assertTrue(boundary["full_public_wkt_candidate_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()
