from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = ROOT / "docs" / "technical_app_notes" / "app_primitive_classification.md"
REPORT = ROOT / "docs" / "reports" / "goal1510_v1_5_4_non_pod_app_classification_and_pod_readiness_2026-05-08.md"
INDEX = ROOT / "docs" / "technical_app_notes" / "README.md"


class Goal1510NonPodAppClassificationTest(unittest.TestCase):
    def test_files_exist(self):
        self.assertTrue(CLASSIFICATION.exists())
        self.assertTrue(REPORT.exists())

    def test_classification_has_required_groups(self):
        text = CLASSIFICATION.read_text(encoding="utf-8")
        for heading in [
            "## Classification Table",
            "### Reduction-First Apps",
            "### Split-Contract Apps",
            "### Candidate-Refinement Apps",
            "### Bounded-Collection Blocked Apps",
            "## Copy And Materialization Implications",
        ]:
            self.assertIn(heading, text)

    def test_classification_covers_app_patterns(self):
        text = CLASSIFICATION.read_text(encoding="utf-8")
        for phrase in [
            "Database analytics",
            "Segment/polygon any-hit rows",
            "Polygon-set Jaccard",
            "Robot collision screening",
            "`ANY_HIT`",
            "`COUNT_HITS`",
            "`REDUCE_FLOAT(SUM)`",
            "`COLLECT_K_BOUNDED`",
        ]:
            self.assertIn(phrase, text)

    def test_classification_keeps_claim_boundaries(self):
        text = CLASSIFICATION.read_text(encoding="utf-8")
        for phrase in [
            "does not authorize public speedup",
            "true zero-copy claims",
            "Broad graph analytics claims are unsafe",
            "Copy reduction is not zero-copy",
            "fail-closed overflow behavior",
        ]:
            self.assertIn(phrase, text)

    def test_report_is_pod_ready_but_non_claiming(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "No GPU pod was available",
            "Next Pod Work Queue",
            "OPTIX_PREFIX=/root/vendor/optix-sdk bash scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh",
            "Acceptance Gates",
            "Claim Boundary",
            "does not authorize public speedup",
            "does not promote `COLLECT_K_BOUNDED`",
        ]:
            self.assertIn(phrase, text)

    def test_index_links_classification(self):
        text = INDEX.read_text(encoding="utf-8")
        self.assertIn("app_primitive_classification.md", text)


if __name__ == "__main__":
    unittest.main()
