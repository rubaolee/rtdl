from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rtdsl.v2_12_public_release_comparison import (
    markdown_v2_12_public_release_comparison,
    v2_12_public_release_comparison,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_12_public_release_comparison.py"
RELEASE_DIR = ROOT / "docs" / "release_reports" / "v2_12"


class Goal4365V212ReleasePublicationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = v2_12_public_release_comparison()

    def test_release_comparison_is_accepted_and_scoped(self) -> None:
        self.assertEqual("accept", self.payload["validation"]["status"], self.payload["validation"]["errors"])
        summary = self.payload["summary"]
        self.assertEqual(10, summary["promoted_app_count"])
        self.assertEqual(11, summary["release_table_row_count"])
        self.assertEqual(10, summary["optix_faster_row_count"])
        self.assertEqual(1, summary["embree_faster_row_count"])
        self.assertEqual(8, summary["scoped_rt_core_value_row_count"])
        self.assertEqual(2, summary["near_parity_row_count"])
        self.assertEqual(0, summary["boundary_limited_phase_ratio_count"])
        self.assertEqual(0, summary["contract_choice_blocker_count"])
        self.assertEqual(0, summary["same_contract_scale_pair_required_count"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["whole_app_speedup_claim_authorized"])
        self.assertFalse(summary["broad_rt_core_claim_authorized"])
        self.assertTrue(summary["release_marker_authorized"])

    def test_mixed_rows_stay_visible(self) -> None:
        rows = {(row["app"], row["contract"]): row for row in self.payload["rows"]}
        contact = next(row for row in self.payload["rows"] if row["app"] == "contact_manifold")
        self.assertEqual("embree", contact["faster_backend"])
        self.assertEqual("embree_faster_scoped_row", contact["release_wording_status"])

        rtnn = next(row for row in self.payload["rows"] if row["app"] == "rtnn")
        self.assertEqual("near_parity_not_rt_core_claim", rtnn["release_wording_status"])
        self.assertIn("not an RT-core", rtnn["scope"])

        pip = next(row for row in self.payload["rows"] if row["contract"] == "pip_same_stream_scalar_count")
        self.assertEqual("near_parity_scoped_engineering_row", pip["release_wording_status"])

        raydb = rows[("raydb_style", "generic_ray_triangle_primitive_grouped_i64_reduction_3d_prepared_count")]
        self.assertGreater(raydb["embree_divided_by_optix"], 20.0)
        self.assertIn("not SQL", raydb["scope"])

    def test_script_writes_release_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "comparison.json"
            out_md = Path(tmp) / "comparison.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            markdown = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("RTDL v2.12 Scoped RT-Core vs Embree CPU Comparison", markdown)
            self.assertIn("Contact Manifold and RTNN stay explicitly mixed", markdown)

    def test_committed_release_package_remains_archived_baseline(self) -> None:
        readme = (RELEASE_DIR / "README.md").read_text(encoding="utf-8")
        publication = (RELEASE_DIR / "publication.md").read_text(encoding="utf-8")
        tag_preparation = (RELEASE_DIR / "tag_preparation.md").read_text(encoding="utf-8")
        comparison = (RELEASE_DIR / "public_rt_vs_embree_comparison.md").read_text(encoding="utf-8")
        comparison_json = json.loads((RELEASE_DIR / "public_rt_vs_embree_comparison.json").read_text(encoding="utf-8"))

        self.assertIn("Version marker: `v2.12`", readme)
        self.assertIn("zero active boundary-limited rows", readme)
        self.assertIn("Public Wording That Is Allowed", publication)
        self.assertIn("Intended tag: `v2.12`", tag_preparation)
        self.assertIn("Contact Manifold is Embree-faster", publication)
        self.assertIn("RTDL v2.12 Scoped RT-Core vs Embree CPU Comparison", comparison)
        self.assertEqual("accept", comparison_json["validation"]["status"])

    def test_front_door_docs_point_at_v2_13_release(self) -> None:
        docs = "\n".join(
            [
                (ROOT / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "versioning.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "learn" / "current_claim_boundaries.md").read_text(encoding="utf-8"),
            ]
        )
        self.assertIn("current v2.13 source-tree", docs)
        self.assertIn("docs/release_reports/v2_13/README.md", docs)
        self.assertIn("row-scoped RT-core versus Embree CPU", docs)
        self.assertNotIn("current v2.12 source-tree", docs)
        self.assertNotIn("current v2.11 source-tree", docs)

    def test_markdown_helper_contains_claim_boundary(self) -> None:
        markdown = markdown_v2_12_public_release_comparison(self.payload)
        self.assertIn("Blocked Wording", markdown)
        self.assertIn("Do not say that RT cores make every benchmark app faster", markdown)
        self.assertIn("Validation status: `accept`", markdown)


if __name__ == "__main__":
    unittest.main()
