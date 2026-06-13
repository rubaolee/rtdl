from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

from rtdsl.v2_13_release_publication import (
    markdown_v2_13_public_rt_vs_embree_comparison,
    markdown_v2_13_publication,
    markdown_v2_13_release_readme,
    markdown_v2_13_tag_preparation,
    v2_13_release_publication_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_13_release_publication.py"
RELEASE_DIR = ROOT / "docs" / "release_reports" / "v2_13"


class Goal4371V213ReleasePublicationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = v2_13_release_publication_packet()

    def test_release_packet_accepts_only_scoped_directional_wording(self) -> None:
        self.assertEqual("accept", self.payload["validation"]["status"], self.payload["validation"]["errors"])
        self.assertEqual("published_source_tree_release_package", self.payload["status"])
        self.assertEqual("v2.13", self.payload["release"]["version_marker"])
        self.assertEqual("2.13.0", self.payload["release"]["pyproject_version"])

        summary = self.payload["summary"]
        self.assertEqual(10, summary["promoted_app_count"])
        self.assertEqual(11, summary["scoped_row_count"])
        self.assertEqual(10, summary["row_scoped_wording_authorized_count"])
        self.assertEqual(1, summary["blocked_row_count"])
        self.assertTrue(summary["human_scale_all_rows_in_1_to_10_sec_band"])
        self.assertLess(summary["human_scale_pip_embree_divided_by_optix"], 1.0)
        self.assertGreater(summary["goal4368_exact_pip_embree_divided_by_optix"], 3.0)
        self.assertGreater(summary["goal4368_rayjoin_rt_faster_than_rtdl_optix_pip"], 7.0)
        self.assertFalse(summary["broad_rt_core_claim_authorized"])
        self.assertFalse(summary["whole_app_speedup_claim_authorized"])
        self.assertFalse(summary["rayjoin_whole_system_claim_authorized"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])

    def test_mixed_pip_and_blocked_rtnn_stay_visible(self) -> None:
        rows = {row["app"]: row for row in self.payload["rows"]}
        pip = rows["spatial_rayjoin_pip"]
        rtnn = rows["rtnn"]

        self.assertEqual("ready_row_scoped_embree_faster_wording", pip["public_wording_status"])
        self.assertIn("not as an RT-core speedup", pip["allowed_wording"])
        self.assertEqual("blocked_not_rt_core_neighbor_search_claim", rtnn["public_wording_status"])
        self.assertFalse(rtnn["row_scoped_public_wording_authorized"])
        self.assertIn("RTNN is an RT-core neighbor-search", "\n".join(self.payload["blocked_wording"]))

    def test_script_writes_full_release_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            release_dir = Path(tmp) / "v2_13"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--release-dir", str(release_dir)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads((release_dir / "release_publication.json").read_text(encoding="utf-8"))
            readme = (release_dir / "README.md").read_text(encoding="utf-8")
            comparison = (release_dir / "public_rt_vs_embree_comparison.md").read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("Promoted apps covered | 10", readme)
            self.assertIn("Embree 1.06x faster", comparison)

    def test_committed_release_package_is_current(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual("v2.13", version)
        self.assertEqual("2.13.0", pyproject["project"]["version"])

        readme = (RELEASE_DIR / "README.md").read_text(encoding="utf-8")
        publication = (RELEASE_DIR / "publication.md").read_text(encoding="utf-8")
        tag_preparation = (RELEASE_DIR / "tag_preparation.md").read_text(encoding="utf-8")
        comparison_json = json.loads((RELEASE_DIR / "public_rt_vs_embree_comparison.json").read_text(encoding="utf-8"))

        self.assertIn("Version marker: `v2.13`", readme)
        self.assertIn("Promoted apps covered | 10", readme)
        self.assertIn("Public Wording That Is Allowed", publication)
        self.assertIn("Intended tag: `v2.13`", tag_preparation)
        self.assertEqual("accept", comparison_json["validation"]["status"])

    def test_front_door_docs_point_at_v2_13_release(self) -> None:
        docs = "\n".join(
            [
                (ROOT / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "versioning.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "capability_boundaries.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "partner_acceleration_boundaries.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "current_main_support_matrix.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "app_engine_support_matrix.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "learn" / "current_claim_boundaries.md").read_text(encoding="utf-8"),
            ]
        )
        self.assertIn("current v2.13 source-tree", docs)
        self.assertIn("docs/release_reports/v2_13/README.md", docs)
        self.assertIn("row-scoped RT-core versus Embree CPU", docs)
        self.assertNotIn("current v2.12 source-tree", docs)

    def test_markdown_helpers_contain_public_boundaries(self) -> None:
        readme = markdown_v2_13_release_readme(self.payload)
        publication = markdown_v2_13_publication(self.payload)
        comparison = markdown_v2_13_public_rt_vs_embree_comparison(self.payload)
        tag = markdown_v2_13_tag_preparation(self.payload)

        self.assertIn("RTDL v2.13 Release Package", readme)
        self.assertIn("RTDL-beats-RayJoin", readme)
        self.assertIn("not a broad RT-core win", publication)
        self.assertIn("RTDL v2.13 Row-Scoped RT-Core vs Embree CPU Comparison", comparison)
        self.assertIn("tests.goal4371_v2_13_release_publication_test", tag)


if __name__ == "__main__":
    unittest.main()
