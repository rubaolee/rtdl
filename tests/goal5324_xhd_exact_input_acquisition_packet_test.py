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
    / "xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json"
)


class Goal5324ExactInputAcquisitionPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_claim_boundary_remains_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertTrue(boundary["acquisition_packet_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["new_rtdl_route_code_added"])
        self.assertFalse(boundary["pod_execution_claimed"])

    def test_global_decision_says_route_work_is_not_next(self) -> None:
        decision = self.payload["global_decision"]
        self.assertEqual(
            decision["full_reproduction_next_blocker"],
            "exact_input_artifacts_or_explicit_exact_equivalence_acceptance",
        )
        self.assertFalse(decision["more_route_performance_work_is_next"])
        self.assertIn("exact", "\n".join(decision["valid_next_paths"]))

    def test_author_artifact_request_covers_all_families(self) -> None:
        request = self.payload["author_artifact_request"]
        self.assertEqual(request["preferred_hash_algorithm"], "sha256")
        self.assertEqual(request["paper_log_path_root"], "/local/storage/shared/HDDatasets")
        families = {item["family"]: item for item in request["families"]}
        self.assertIn("graphics_stanford", families)
        self.assertIn("geo_wkt", families)
        self.assertIn("brats2020_validation", families)
        self.assertTrue(
            any("USADetailedWaterBodies.wkt" in x for x in families["geo_wkt"]["request_items"])
        )
        self.assertTrue(
            any("NIfTI-to-point" in x for x in families["brats2020_validation"]["request_items"])
        )
        self.assertTrue(
            any("AsianDragon" in x for x in families["graphics_stanford"]["request_items"])
        )

    def test_public_exact_equivalence_protocol_is_strict(self) -> None:
        protocol = self.payload["public_exact_equivalence_review_protocol"]
        required = "\n".join(protocol["required_before_exact_equivalence_can_be_considered"])
        self.assertIn("source snapshot", required)
        self.assertIn("generated input file sha256", required)
        self.assertIn("external review explicitly accepts", required)
        not_sufficient = "\n".join(protocol["not_sufficient"])
        self.assertIn("matching point counts", not_sufficient)
        self.assertIn("matching HDResult alone", not_sufficient)
        self.assertIn("checked-in author logs", not_sufficient)

    def test_water_bg_is_best_candidate_but_not_exact(self) -> None:
        candidate = self.payload["current_best_candidate_for_exact_equivalence_review"]
        self.assertEqual(candidate["row_id"], "geo_waterbodies_blockgroups")
        self.assertGreaterEqual(len(candidate["why_best"]), 4)
        blockers = "\n".join(candidate["why_not_exact_yet"])
        self.assertIn("No author WKT file hashes", blockers)
        self.assertIn("Remaining point-count deltas are nonzero", blockers)
        self.assertIn("do not self-promote", candidate["recommended_decision"])

    def test_stop_or_continue_matrix_has_clear_outcomes(self) -> None:
        matrix = self.payload["stop_or_continue_decision_matrix"]
        conditions = "\n".join(row["condition"] for row in matrix)
        self.assertIn("author files/hashes", conditions)
        self.assertIn("byte-identical regeneration", conditions)
        self.assertIn("external review accepts", conditions)
        self.assertIn("no external artifacts", conditions)
        no_artifact = [row for row in matrix if row["condition"].startswith("no external")][0]
        self.assertFalse(no_artifact["pod_expected"])
        self.assertIn("stop full-paper claims at Level-B", no_artifact["next"])

    def test_no_pod_and_forbidden_claims(self) -> None:
        pod = self.payload["pod_usage"]
        self.assertFalse(pod["used"])
        self.assertFalse(pod["expected_next"])
        self.assertIn("acquisition", pod["reason"])
        forbidden = "\n".join(self.payload["not_allowed"])
        self.assertIn("Figure 5 reproduction", forbidden)
        self.assertIn("full X-HD paper reproduction", forbidden)
        self.assertIn("author-vs-RTDL performance ratio", forbidden)
        self.assertIn("more performance work", forbidden)


if __name__ == "__main__":
    unittest.main()
