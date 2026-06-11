import json
import unittest
from pathlib import Path

from scripts.goal4248_current_public_docs_claim_boundary_scan import SCHEMA, scan


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs/reports/goal4248_current_public_docs_claim_boundary_scan.json"


class Goal4248CurrentPublicDocsClaimBoundaryScanTest(unittest.TestCase):
    def test_scan_artifact_passes_with_no_hard_blockers(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], SCHEMA)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["hard_blocker_count"], 0)
        self.assertEqual(payload["hard_blockers"], [])
        self.assertEqual(payload["public_file_count"], 30)
        self.assertGreaterEqual(payload["finding_count"], 90)
        self.assertGreater(payload["accepted_boundary_or_negative_count"], 0)
        self.assertGreater(payload["accepted_scoped_evidence_count"], 0)

    def test_live_scan_matches_pass_boundary(self) -> None:
        payload = scan(ROOT)

        self.assertEqual(payload["schema"], SCHEMA)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["hard_blocker_count"], 0)
        self.assertEqual(payload["hard_blockers"], [])

    def test_public_doc_set_includes_front_doors(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        public_files = set(payload["public_files_scanned"])

        self.assertIn("README.md", public_files)
        self.assertIn("examples/README.md", public_files)
        self.assertIn("docs/learn/partner_choice_for_custom_logic.md", public_files)
        self.assertIn("tutorials/current/README.md", public_files)
        self.assertIn("tutorials/current/08_spatial_join_rayjoin_reference.md", public_files)
        self.assertIn("examples/current/research_benchmarks/spatial_rayjoin/README.md", public_files)
        self.assertIn("examples/current/research_benchmarks/rt_dbscan/README.md", public_files)

    def test_all_claim_boundary_authorizations_remain_false(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        claim_boundary = payload["claim_boundary"]

        expected_false_keys = {
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "paper_reproduction_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "amd_performance_claim_authorized",
            "package_install_claim_authorized",
        }
        self.assertEqual(set(claim_boundary), expected_false_keys)
        for key in expected_false_keys:
            self.assertFalse(claim_boundary[key], key)

    def test_initial_wording_blockers_stay_repaired(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        examples_readme = (ROOT / "examples/README.md").read_text(encoding="utf-8")
        tutorial_index = (ROOT / "tutorials" / "README.md").read_text(encoding="utf-8")

        self.assertIn("Dependency install only; this does not install RTDL", readme)
        self.assertIn("Dependency install only; this does not install RTDL", examples_readme)
        self.assertNotIn("package-install is unsupported", readme)
        self.assertNotIn("docs/tutorials", tutorial_index)
        self.assertIn("ordered learning path", tutorial_index)


if __name__ == "__main__":
    unittest.main()
