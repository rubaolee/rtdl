from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rtdsl.v2_14_benchmark_cleanup import (
    markdown_v2_14_benchmark_cleanup_gap_matrix,
    v2_14_benchmark_cleanup_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_14_benchmark_cleanup_gap_matrix.py"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4379_v2_14_benchmark_cleanup_gap_matrix_2026-06-14.json"
REPORT = ROOT / "docs" / "reports" / "goal4379_v2_14_benchmark_cleanup_gap_matrix_2026-06-14.md"


class Goal4379V214BenchmarkCleanupGatesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = v2_14_benchmark_cleanup_packet()

    def test_packet_is_draft_gate_not_release(self) -> None:
        self.assertEqual("accept_draft_gate", self.packet["validation"]["status"], self.packet["validation"]["errors"])
        self.assertFalse(self.packet["summary"]["release_ready"])
        self.assertEqual(10, self.packet["summary"]["promoted_app_count"])
        self.assertEqual(12, self.packet["summary"]["row_count"])
        self.assertEqual(12, self.packet["summary"]["fresh_measurement_required_count"])
        self.assertEqual(0, self.packet["summary"]["public_wording_authorized_count"])
        self.assertFalse(self.packet["summary"]["broad_rt_core_claim_authorized"])
        self.assertFalse(self.packet["summary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.packet["summary"]["automatic_partner_selection_authorized"])
        self.assertFalse(self.packet["summary"]["app_specific_native_engine_logic_allowed"])

    def test_rows_cover_promoted_apps_and_split_rayjoin(self) -> None:
        rows = self.packet["rows"]
        apps = {row["app"] for row in rows}
        self.assertEqual(
            {
                "hausdorff_xhd",
                "spatial_rayjoin",
                "rt_dbscan",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "barnes_hut",
                "librts_spatial_index",
                "rtnn",
                "triangle_counting",
            },
            apps,
        )
        rayjoin_ids = {row["row_id"] for row in rows if row["app"] == "spatial_rayjoin"}
        self.assertEqual(
            {"spatial_rayjoin_lsi", "spatial_rayjoin_pip", "spatial_rayjoin_overlay"},
            rayjoin_ids,
        )

    def test_every_row_blocks_public_wording_until_fresh_evidence(self) -> None:
        for row in self.packet["rows"]:
            self.assertTrue(row["fresh_v2_14_measurement_required"], row["row_id"])
            self.assertTrue(row["same_contract_required"], row["row_id"])
            self.assertTrue(row["best_known_route_required"], row["row_id"])
            self.assertTrue(row["phase_explanation_required"], row["row_id"])
            self.assertFalse(row["release_ready"], row["row_id"])
            self.assertFalse(row["row_scoped_public_wording_authorized"], row["row_id"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"], row["row_id"])
            self.assertFalse(row["broad_rt_core_claim_authorized"], row["row_id"])
            self.assertFalse(row["automatic_partner_selection_authorized"], row["row_id"])
            self.assertFalse(row["paper_reproduction_claim_authorized"], row["row_id"])
            self.assertFalse(row["author_hot_compute_parity_claim_authorized"], row["row_id"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"], row["row_id"])

    def test_rayjoin_overlay_requires_author_hot_path_caveat(self) -> None:
        overlay = next(row for row in self.packet["rows"] if row["row_id"] == "spatial_rayjoin_overlay")
        self.assertTrue(overlay["rayjoin_author_caveat_required"])
        self.assertIn("author", overlay["primary_blocker"].lower())
        self.assertIn("hot-compute parity", overlay["primary_blocker"])
        self.assertIn("Goal4376", overlay["v2_13_starting_point"])

    def test_markdown_renderer_names_rows_and_boundaries(self) -> None:
        markdown = markdown_v2_14_benchmark_cleanup_gap_matrix(self.packet)
        self.assertIn("Goal4379 v2.14 Benchmark Cleanup Gap Matrix", markdown)
        self.assertIn("spatial_rayjoin_overlay", markdown)
        self.assertIn("author-hot-compute parity wording", markdown)
        self.assertIn("Public wording authorized rows now: `0`", markdown)

    def test_script_writes_gap_matrix_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "gap.json"
            out_md = Path(tmp) / "gap.md"
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
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept_draft_gate", payload["validation"]["status"])
            self.assertIn("spatial_rayjoin_overlay", report)

    def test_release_docs_are_published_and_v2_13_has_bridge_caveat(self) -> None:
        v214 = "\n".join(
            [
                (ROOT / "docs" / "release_reports" / "v2_14" / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "release_reports" / "v2_14" / "publication.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "release_reports" / "v2_14" / "public_rt_vs_embree_comparison.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "release_reports" / "v2_14" / "rayjoin_author_vs_rtdl_caveat.md").read_text(encoding="utf-8"),
            ]
        )
        self.assertIn("released source-tree packet for tag `v2.14`", v214)
        self.assertIn("published source-tree release note for tag `v2.14`", v214)
        self.assertIn("published caveat in source-tree tag `v2.14`", v214)
        self.assertIn("Maintainer explicitly authorizes publication", v214)
        self.assertIn("author-hot-compute parity", v214)
        self.assertIn("released as row-scoped scalar-count evidence", v214)
        self.assertIn("blocked only for full 8/8 Section 5.7 reproduction", v214)

        v213 = "\n".join(
            [
                (ROOT / "docs" / "release_reports" / "v2_13" / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "release_reports" / "v2_13" / "publication.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "release_reports" / "v2_13" / "public_rt_vs_embree_comparison.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "release_reports" / "v2_13" / "tag_preparation.md").read_text(encoding="utf-8"),
            ]
        )
        self.assertIn("Goal4378", v213)
        self.assertIn("near author process wall", v213)
        self.assertIn("hot-compute parity", v213)
        self.assertIn("Do not move a published `v2.13` tag", v213)

    def test_committed_gap_matrix_artifacts_are_current(self) -> None:
        committed = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(self.packet["version"], committed["version"])
        self.assertEqual("accept_draft_gate", committed["validation"]["status"])
        self.assertEqual(12, committed["summary"]["row_count"])
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal4379 v2.14 Benchmark Cleanup Gap Matrix", report)
        self.assertIn("spatial_rayjoin_overlay", report)


if __name__ == "__main__":
    unittest.main()
