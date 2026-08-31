from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3818_current_benchmark_contract_smoke_a5000"
REPORT = ROOT / "docs" / "reports" / "goal3818_current_benchmark_contract_smoke_a5000_2026-06-07.md"


class Goal3818CurrentBenchmarkContractSmokeTest(unittest.TestCase):
    def test_first_pass_and_repair_artifacts_cover_all_benchmark_rows(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
        repair = json.loads((ARTIFACT_DIR / "repair_summary.json").read_text(encoding="utf-8"))

        self.assertEqual(summary["commit"], "b56a8927")
        self.assertEqual(summary["gpu"], "NVIDIA RTX A5000")
        first_rows = {row["name"]: row for row in summary["rows"]}
        repair_rows = {row["name"]: row for row in repair["rows"]}

        expected_first_rows = {
            "hausdorff_xhd",
            "spatial_rayjoin_pip_count",
            "rt_dbscan_numba",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "barnes_hut_numba",
            "librts_spatial_index",
            "rtnn_plan",
            "triangle_counting",
        }
        self.assertEqual(set(first_rows), expected_first_rows)

        passing_first_rows = {name for name, row in first_rows.items() if row["status"] == "pass"}
        self.assertEqual(
            passing_first_rows,
            expected_first_rows - {"hausdorff_xhd", "contact_manifold"},
        )
        self.assertEqual(first_rows["hausdorff_xhd"]["status"], "fail")
        self.assertEqual(first_rows["contact_manifold"]["status"], "fail")

        self.assertEqual(repair_rows["hausdorff_xhd_repaired"]["status"], "pass")
        self.assertEqual(repair_rows["contact_manifold_repaired"]["status"], "pass")
        self.assertIn("directed_threshold_prepared", repair_rows["hausdorff_xhd_repaired"]["command"])
        self.assertIn("--witness-capacity", repair_rows["contact_manifold_repaired"]["command"])

    def test_fail_closed_messages_are_preserved(self) -> None:
        hausdorff_stderr = (ARTIFACT_DIR / "hausdorff_xhd.stderr.txt").read_text(encoding="utf-8")
        contact_stderr = (ARTIFACT_DIR / "contact_manifold.stderr.txt").read_text(encoding="utf-8")
        self.assertIn("requires --backend optix --optix-summary-mode directed_threshold_prepared", hausdorff_stderr)
        self.assertIn("COLLECT_K_BOUNDED overflowed capacity", contact_stderr)
        self.assertIn("partial_result_returned=False", contact_stderr)

    def test_report_records_claim_boundary_and_docs_actions(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "contract-smoke packet",
            "not a long-run performance matrix",
            "directed_threshold_prepared",
            "witness-capacity 32",
            "does not authorize release action",
            "separate AMD/HIPRT functional validation lane",
        ):
            self.assertIn(phrase, report)

    def test_active_docs_show_current_guidance_for_smoked_commands(self) -> None:
        hausdorff = (
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "README.md"
        ).read_text(encoding="utf-8")
        contact = (
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "contact_manifold" / "README.md"
        ).read_text(encoding="utf-8")
        app_building = (ROOT / "docs" / "tutorials" / "v2_app_building.md").read_text(encoding="utf-8")
        rayjoin = (
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"
        ).read_text(encoding="utf-8")
        segment = (ROOT / "docs" / "tutorials" / "segment_polygon_workloads.md").read_text(encoding="utf-8")

        self.assertIn("current RTDL user", hausdorff)
        self.assertIn("directed_threshold_prepared", hausdorff)
        self.assertIn("--mode native_collect_k --backend optix", contact)
        self.assertIn("--witness-capacity 32", contact)
        self.assertIn("# Current App Building", app_building)
        self.assertNotIn("best first v2.8", app_building)
        self.assertIn("current RTDL user", rayjoin)
        self.assertNotIn("v2.8 user", rayjoin)
        self.assertIn("[Current App Building]", segment)


if __name__ == "__main__":
    unittest.main()
