from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_current_optix_embree_comparison_index.py"
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4338_current_optix_embree_comparison_index_2026-06-11.md"
)
JSON_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4338_current_optix_embree_comparison_index_2026-06-11.json"
)


class Goal4338CurrentOptixEmbreeComparisonIndexTest(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(ROOT / "src"))
        from rtdsl.current_optix_embree_comparison_index import (
            current_optix_embree_comparison_index,
        )

        self.payload = current_optix_embree_comparison_index()

    def test_all_ten_benchmark_apps_are_indexed(self) -> None:
        apps = {row["app"] for row in self.payload["rows"]}
        self.assertEqual(
            apps,
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
        )
        self.assertEqual(10, self.payload["summary"]["row_count"])
        self.assertEqual("accept", self.payload["validation"]["status"], self.payload["validation"]["errors"])

    def test_no_existing_artifact_ratio_is_authorized(self) -> None:
        self.assertEqual(0, self.payload["summary"]["ratio_authorized_from_existing_artifacts_count"])
        for row in self.payload["rows"]:
            self.assertFalse(row["ratio_authorized_from_existing_artifacts"], row["app"])
            self.assertFalse(row["public_speedup_claim_authorized"], row["app"])
            self.assertFalse(row["release_authorized"], row["app"])
            self.assertIn("required_next_action", row)
            self.assertIn("reason_existing_artifacts_are_not_speedup_grade", row)

    def test_current_mismatch_for_rtnn_artifact_is_visible(self) -> None:
        rows = {row["app"]: row for row in self.payload["rows"]}
        rtnn = rows["rtnn"]
        self.assertEqual("rtnn_embree_cpu_ann_candidate_quality_reference", rtnn["embree_cpu"]["row_id"])
        self.assertFalse(rtnn["embree_cpu"]["artifact"]["artifact_present"])
        self.assertEqual("missing_current_row_artifact", rtnn["embree_cpu"]["artifact"]["status"])
        self.assertIn("refresh the current Embree artifact", rtnn["required_next_action"])

    def test_comparison_classes_are_not_public_claim_classes(self) -> None:
        classes = {row["comparison_class"] for row in self.payload["rows"]}
        self.assertEqual(
            classes,
            {"same_contract_different_scale_pair_required", "contract_split_pair_required"},
        )
        self.assertGreaterEqual(
            self.payload["summary"]["same_contract_different_scale_pair_required_count"],
            4,
        )
        self.assertGreaterEqual(
            self.payload["summary"]["contract_split_pair_required_count"],
            4,
        )

    def test_script_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "comparison.json"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--output-json", str(out)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("not a speedup table", completed.stdout)

    def test_report_and_json_artifact_are_present_and_non_authorizing(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not a public speedup table", text)
        self.assertIn("RTNN artifact mismatch", text)
        self.assertIn("Fresh same-contract paired runs", text)
        forbidden = (
            "public speedup claim " + "authorized",
            "release " + "authorized",
            "broad rt-core claim " + "authorized",
        )
        lowered = text.lower()
        for phrase in forbidden:
            self.assertNotIn(phrase, lowered)

        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(10, payload["summary"]["row_count"])


if __name__ == "__main__":
    unittest.main()
