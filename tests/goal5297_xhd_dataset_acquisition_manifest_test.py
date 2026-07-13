import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json"
)


class Goal5297XhdDatasetAcquisitionManifestTest(unittest.TestCase):
    def test_claim_boundary_keeps_full_reproduction_false(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["status"],
            "dataset_acquisition_manifest_ready__graphics_level_b_transfer_possible__exact_hddatasets_missing",
        )
        for key, value in payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertFalse(payload["current_pod"]["author_dataset_root_exists"])

    def test_local_graphics_assets_are_complete_but_level_b_only(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        graphics = payload["dataset_families"]["graphics_stanford"]
        assets = graphics["local_workspace_assets"]

        for key in (
            "dragon_vrip",
            "happy_vrip",
            "asian_dragon",
            "asian_dragon_scaled_1e-3",
            "thai_statuette",
            "thai_statuette_scaled_1e-3",
        ):
            self.assertIn(key, assets)
            self.assertGreater(assets[key]["bytes"], 0)
            self.assertRegex(assets[key]["sha256"], r"^[0-9A-F]{64}$")

        self.assertEqual(graphics["public_source"]["source_status"], "public_same_source_candidate")
        self.assertEqual(graphics["public_source"]["exact_paper_identity_status"], "not_proven")
        self.assertEqual(
            graphics["authorized_status_after_upload"],
            "level_b_same_source_graphics_matrix_candidate_only",
        )
        self.assertEqual(graphics["forbidden_status_after_upload"], "exact_paper_dataset_reproduction")

    def test_current_pod_has_only_partial_graphics_subset(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        pod_assets = payload["dataset_families"]["graphics_stanford"]["current_pod_assets"]

        self.assertTrue(pod_assets["/tmp/xhd_goal5234/data/dragon.ply"]["exists"])
        self.assertTrue(pod_assets["/tmp/xhd_goal5234/data/asian_dragon.ply"]["exists"])
        self.assertTrue(pod_assets["/tmp/xhd_goal5234/data/asian_dragon_scaled_1e-3.ply"]["exists"])
        self.assertFalse(pod_assets["/tmp/xhd_goal5234/data/thai_statuette.ply"]["exists"])
        self.assertFalse(pod_assets["/tmp/xhd_goal5234/data/happy_buddha.ply"]["exists"])

    def test_non_graphics_families_remain_blocked_without_provenance(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        families = payload["dataset_families"]

        self.assertEqual(families["brats_2020"]["access_status"], "registration_or_license_required")
        self.assertIn("blocked_without_author_image_list", families["brats_2020"]["exact_paper_identity_status"])
        self.assertEqual(families["census_tiger_geospatial"]["local_workspace_assets"], "absent")
        self.assertIn("blocked_without_source_year", families["census_tiger_geospatial"]["exact_paper_identity_status"])
        self.assertEqual(families["osm_geospatial"]["current_pod_assets"], "absent")
        self.assertIn("blocked_without_osm_snapshot", families["osm_geospatial"]["exact_paper_identity_status"])

    def test_next_goal_is_upload_author_only_level_b_precheck(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        next_goal = payload["recommended_next_goal"]

        self.assertEqual(next_goal["goal"], "Goal5298")
        scope = "\n".join(next_goal["scope"])
        self.assertIn("scripts/current_pod_ssh.py upload", scope)
        self.assertIn("author hd_exec value prechecks", scope)
        self.assertIn("Level-B same-source only", scope)
        self.assertIn("Do not run RTDL comparison", scope)


if __name__ == "__main__":
    unittest.main()
