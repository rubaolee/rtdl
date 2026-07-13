from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
DATA_DIR = APP_DIR / "data" / "representative" / "goal5466_blockgroups_simple64_100k"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Goal5466LibRtsRepresentativePipDatasetTest(unittest.TestCase):
    def test_manifest_pins_level_b_identity_and_file_hashes(self) -> None:
        manifest = json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["identity_level"],
            "level_b_public_source_representative_subset",
        )
        self.assertEqual(manifest["polygon_count"], 64)
        self.assertEqual(manifest["query_count"], 100000)
        self.assertEqual(
            _sha256(DATA_DIR / manifest["polygon_selection"]["output_file"]),
            manifest["polygon_selection"]["output_sha256"],
        )
        self.assertEqual(
            _sha256(DATA_DIR / manifest["query_generation"]["output_file"]),
            manifest["query_generation"]["output_sha256"],
        )
        self.assertFalse(
            manifest["claim_boundary"]["exact_paper_dataset_reproduction_claimed"]
        )
        self.assertFalse(manifest["claim_boundary"]["performance_claimed"])

    def test_polygon_subset_and_query_cardinality_are_deterministic(self) -> None:
        polygon_lines = (
            DATA_DIR / "blockgroups_simple64_arcgis.wkt"
        ).read_text(encoding="utf-8").splitlines()
        query_lines = (
            DATA_DIR / "blockgroups_simple64_queries_seed0_100k.wkt"
        ).read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(polygon_lines), 64)
        self.assertEqual(len(query_lines), 100000)
        self.assertTrue(all(line.startswith("POLYGON") for line in polygon_lines))
        self.assertTrue(all("), (" not in line and "),(" not in line for line in polygon_lines))
        self.assertTrue(all(line.startswith("POINT(") for line in query_lines))

    def test_generator_wrapper_builds_only_pinned_author_generator(self) -> None:
        wrapper = (
            APP_DIR
            / "author_patches"
            / "goal5466_spatialquerybenchmark_gen_only_CMakeLists.txt"
        ).read_text(encoding="utf-8")
        self.assertIn("src/gen/gen.cpp", wrapper)
        self.assertIn("src/flags.cpp", wrapper)
        self.assertNotIn("pip_query.cu", wrapper)
        self.assertNotIn("Embree", wrapper)


if __name__ == "__main__":
    unittest.main()
