from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4294_a40_pod_validation_2026-06-11.md"
ARTIFACTS = ROOT / "docs" / "reports" / "goal4294_a40_pod_validation_artifacts_2026-06-11"


def _read_json(name: str) -> dict[str, object]:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


class Goal4294A40PodValidationTest(unittest.TestCase):
    def test_report_documents_boundary_and_environment(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("NVIDIA A40", text)
        self.assertIn("6a556994a5176a3acc8bad2557c0905caa893898", text)
        self.assertIn("working tree for the accepted scale-profile rerun: clean", text.lower())
        self.assertIn("does not authorize release action", text)
        self.assertIn("true-zero-copy wording", text)
        self.assertIn("automatic partner selection", text)

    def test_clean_scale_profile_passes_all_rows_on_clean_tree(self) -> None:
        payload = _read_json("scale_profile_summary_clean.json")
        runtime = payload["runtime_environment"]
        summary = payload["summary"]
        rows = payload["rows"]

        self.assertTrue(payload["all_pass"])
        self.assertEqual(10, summary["row_count"])
        self.assertEqual(10, len(rows))
        self.assertTrue(runtime["working_tree_clean"])
        self.assertEqual([], runtime["git_status_short"])
        self.assertEqual("6a556994", runtime["source_commit_short"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])

        row_ids = {row["row_id"] for row in rows}
        self.assertIn("spatial_rayjoin_public_cdb_representative_mixed_route_scale_default", row_ids)
        self.assertTrue(all(row["status"] == "pass" for row in rows))
        self.assertTrue(all(row["returncode"] == 0 for row in rows))

    def test_front_door_hardware_passes_all_rows(self) -> None:
        payload = _read_json("front_door_hardware_summary.json")
        summary = payload["summary"]

        self.assertTrue(payload["all_pass"])
        self.assertEqual(10, summary["row_count"])
        self.assertEqual(10, len(payload["rows"]))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertTrue(all(row["status"] == "pass" for row in payload["rows"]))

    def test_large_scale_partner_comparison_is_correctness_clean_and_bounded(self) -> None:
        payload = _read_json("large_scale_partner_comparison.json")
        summary = payload["summary"]
        grouped = payload["grouped_suite"]
        compact = payload["compact_mask_suite"]

        self.assertTrue(summary["all_match_cpu_oracle"])
        self.assertTrue(summary["all_partner_contract_totals_meet_one_second_floor"])
        self.assertEqual([], summary["subsecond_hot_total_rows"])
        self.assertAlmostEqual(5.55115851201117, grouped["partner_hot_total_sec"]["cupy"], places=9)
        self.assertAlmostEqual(11.53770140465349, grouped["partner_hot_total_sec"]["numba"], places=9)
        self.assertAlmostEqual(1.4153931555338204, compact["partners"]["cupy"]["hot_total_sec"], places=9)
        self.assertAlmostEqual(39.41230903821997, compact["partners"]["numba"]["hot_total_sec"], places=9)
        self.assertGreater(summary["cupy_speedup_vs_numba"]["grouped_suite_hot_total"], 1.0)
        self.assertGreater(summary["cupy_speedup_vs_numba"]["compact_mask_hot_total"], 1.0)
        self.assertTrue(grouped["all_match_cpu_oracle"])
        self.assertTrue(compact["all_match_cpu_oracle"])
        self.assertFalse(grouped["claim_boundary"]["release_authorized"])
        self.assertFalse(compact["claim_boundary"]["release_authorized"])
        self.assertFalse(grouped["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(compact["claim_boundary"]["whole_app_speedup_claim_authorized"])

    def test_short_named_scale_row_artifacts_exist(self) -> None:
        expected = {
            "hausdorff_xhd.json",
            "spatial_rayjoin.json",
            "rt_dbscan.json",
            "robot_collision.json",
            "contact_manifold.json",
            "raydb_count.json",
            "barnes_hut.json",
            "librts_spatial_index.json",
            "rtnn_prepared.json",
            "triangle_counting.json",
        }
        row_dir = ARTIFACTS / "scale_rows"

        self.assertTrue(row_dir.is_dir())
        self.assertTrue(expected.issubset({path.name for path in row_dir.glob("*.json")}))


if __name__ == "__main__":
    unittest.main()
