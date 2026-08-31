from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5325_public_web_supplement_artifact_sweep.json"
)


class Goal5325PublicWebSupplementArtifactSweepTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_claim_boundary_remains_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["public_web_artifact_search_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["pod_execution_claimed"])

    def test_acm_supplement_is_unresolved_not_overclaimed(self) -> None:
        unresolved = self.payload["important_unresolved_artifacts"][0]
        self.assertEqual(unresolved["artifact"], "ACM `ics26-106.zip` supplementary item")
        self.assertEqual(unresolved["status"], "unresolved_403")
        self.assertIn("must be inspected", unresolved["current_inference"])
        acm_surface = [
            surface
            for surface in self.payload["search_surfaces"]
            if surface["surface"] == "ACM proceedings supplementary listing"
        ][0]
        self.assertEqual(acm_surface["dataset_artifact_found"], "unresolved")
        self.assertTrue(all(attempt["status"] == 403 for attempt in acm_surface["download_attempts"]))

    def test_other_public_surfaces_found_no_dataset_artifacts(self) -> None:
        surfaces = {surface["surface"]: surface for surface in self.payload["search_surfaces"]}
        self.assertFalse(surfaces["ACM DOI page"]["dataset_artifact_found"])
        self.assertFalse(surfaces["Rubao Lee public PDF"]["dataset_artifact_found"])
        self.assertFalse(surfaces["Liang Geng publication page"]["dataset_artifact_found"])
        self.assertFalse(surfaces["NSF Public Access record"]["dataset_artifact_found"])
        self.assertFalse(surfaces["ResearchGate publication page"]["dataset_artifact_found"])
        self.assertFalse(surfaces["Zenodo / Figshare / OSF targeted web search"]["dataset_artifact_found"])

    def test_brats_public_mirrors_do_not_close_xhd_exact_identity(self) -> None:
        brats = [
            surface
            for surface in self.payload["search_surfaces"]
            if surface["surface"] == "BraTS public mirrors"
        ][0]
        self.assertFalse(brats["dataset_artifact_found"])
        self.assertIn("not author converted point sets", brats["notes"])
        self.assertIn("kaggle.com", "\n".join(brats["examples"]))

    def test_classification_preserves_unresolved_acm_item(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["public_exact_dataset_artifacts_found"])
        self.assertFalse(classification["publication_supplement_fully_inspected"])
        self.assertIn("ACM", classification["blocking_unresolved_item"])
        self.assertEqual(
            classification["current_level"],
            "no_public_exact_dataset_found__one_acm_supplement_requires_access_or_confirmation",
        )

    def test_goal5324_relationship_and_next_actions(self) -> None:
        relation = self.payload["relationship_to_goal5324"]
        self.assertTrue(relation["supports_acquisition_packet"])
        self.assertIn("ACM supplement inspection", relation["modifies_next_action"])
        self.assertIn("No Figure 5 claim", relation["does_not_change"])
        actions = self.payload["recommended_next_actions"]
        self.assertIn("Inspect ACM", actions[0]["action"])
        self.assertFalse(actions[0]["requires_pod"])
        self.assertFalse(actions[3]["requires_pod"])

    def test_forbidden_claims_and_exit_label(self) -> None:
        self.assertEqual(
            self.payload["exit_label"],
            "public_web_exact_dataset_artifacts_not_found__acm_supplement_unresolved",
        )
        forbidden = "\n".join(self.payload["not_allowed"])
        self.assertIn("ACM supplement contains datasets without inspection", forbidden)
        self.assertIn("contains no useful artifacts without inspection", forbidden)
        self.assertIn("full X-HD paper reproduction", forbidden)
        self.assertIn("performance ratio", forbidden)
        pod = self.payload["pod_usage"]
        self.assertFalse(pod["used"])
        self.assertFalse(pod["expected_next"])


if __name__ == "__main__":
    unittest.main()
