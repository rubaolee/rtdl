from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from scripts import goal5839_build_real_artifact_census_preregistration as prereg
from scripts import goal5839_build_discovery_execution_binding as discovery_binding


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = prereg.AUTHORITY_PATH
REPORT = prereg.EVIDENCE_ROOT / "PREREGISTRATION.md"
SCRIPT = ROOT / "scripts" / "goal5839_build_real_artifact_census_preregistration.py"


class Goal5839RealArtifactCensusPreregistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = json.loads(AUTHORITY.read_text(encoding="ascii"))

    def test_authority_seal_and_preinspection_state(self) -> None:
        prereg.validate_authority(self.authority)
        self.assertEqual(
            self.authority["status"],
            "FROZEN_PROTOCOL__CENSUS_EXTRACTION_NOT_STARTED__NO_FIELD_RESULT",
        )
        self.assertTrue(self.authority["claim_boundary"]["preregistration_only"])
        self.assertTrue(
            all(value == 0 for value in self.authority["execution_state"].values())
        )

    def test_complete_29_work_denominator_is_never_availability_filtered(self) -> None:
        denominator = self.authority["denominator"]
        self.assertEqual(denominator["paper_problem_row_count"], 35)
        self.assertEqual(denominator["distinct_problem_label_count"], 32)
        self.assertEqual(denominator["unique_work_count"], 29)
        self.assertEqual(denominator["expected_minimum_property_cell_count_after_census"], 145)
        self.assertEqual(len(denominator["works"]), 29)
        self.assertTrue(
            all(
                row["artifact_discovery_status"] == "NOT_STARTED_AT_PREREGISTRATION"
                and row["classification_cell_count"] == 0
                for row in denominator["works"]
            )
        )
        discovery = self.authority["artifact_discovery_and_selection_protocol"]
        self.assertTrue(discovery["work_denominator_never_shrinks"])
        self.assertIn("five UNRESOLVED_WITH_REASON cells", discovery["no_public_artifact_found_effect"])

    def test_exact_survey_identity_and_legacy_custody_gap_are_explicit(self) -> None:
        source = self.authority["source_authority"]
        self.assertEqual(source["survey_archive"]["bytes"], 752_766)
        self.assertEqual(source["survey_archive"]["sha256"], prereg.SURVEY_ARCHIVE_SHA256)
        self.assertEqual(source["sample_bib"]["sha256"], prereg.SAMPLE_BIB_SHA256)
        self.assertEqual(source["prob_csv"]["sha256"], prereg.PROB_CSV_SHA256)
        legacy = source["legacy_goal5753_custody"]
        self.assertFalse(legacy["byte_identical_reproduction"])
        self.assertIn("DO_NOT_USE", legacy["disposition"])
        self.assertNotEqual(
            legacy["expected_historical_artifact"],
            legacy["current_generator_rebuild_from_exact_source"],
        )

    def test_five_properties_and_four_labels_are_closed(self) -> None:
        self.assertEqual(
            [row["id"] for row in self.authority["protocol_properties"]],
            [row["id"] for row in prereg.PROPERTIES],
        )
        contract = self.authority["classification_contract"]
        self.assertEqual(contract["allowed_labels_only"], list(prereg.ALLOWED_LABELS))
        self.assertFalse(contract["absence_of_explicit_check_is_violation"])
        self.assertFalse(contract["successful_build_or_output_is_enforcement"])
        self.assertEqual(contract["ambiguity_default"], "UNRESOLVED_WITH_REASON")
        self.assertFalse(contract["not_applicable_is_standalone_label"])

    def test_selection_cannot_follow_observed_labels(self) -> None:
        protocol = self.authority["artifact_discovery_and_selection_protocol"]
        self.assertEqual(
            protocol["same_precedence_tie_breaker"],
            "lexicographically smallest normalized canonical URL",
        )
        self.assertIn("classify every distinct eligible official artifact", protocol["multiple_distinct_official_artifacts"])
        self.assertIn("never choose based on observed labels", protocol["multiple_distinct_official_artifacts"])
        self.assertIn("29 survey works", protocol["completeness_boundary"])

    def test_independence_and_responsible_disclosure_fail_closed(self) -> None:
        independence = self.authority["independence_and_adjudication"]
        self.assertFalse(independence["same_codex_session_repeated_extraction_counts_as_independent"])
        self.assertFalse(independence["project_author_may_resolve_ambiguity_favorably"])
        self.assertFalse(independence["paper_ready_census_claim_authorized"])
        disclosure = self.authority["responsible_disclosure"]
        self.assertFalse(disclosure["concrete_violation_public_naming_allowed_before_notification"])
        self.assertIn("14 calendar days", " ".join(disclosure["required_before_public_naming"]))
        self.assertIn("Do not commit or push", disclosure["public_repository_rule"])

    def test_report_states_zero_result_and_no_consensus_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        self.assertIn("Zero violations is a valid result", normalized)
        self.assertIn("Absence of a check is not a bug", normalized)
        self.assertIn("This corpus is not blind", normalized)
        self.assertIn("cannot produce a paper-ready census claim", normalized)
        self.assertIn("no field prevalence", normalized)
        self.assertIn("external review or consensus", normalized)

    def test_builder_has_no_network_or_candidate_checkout_surface(self) -> None:
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertTrue(
            imports.isdisjoint(
                {"requests", "urllib", "http", "socket", "subprocess", "git"}
            )
        )

    def test_discovery_execution_binding_is_frozen_before_results(self) -> None:
        binding = json.loads(discovery_binding.OUTPUT_PATH.read_text(encoding="ascii"))
        discovery_binding.validate_binding(binding)
        self.assertEqual(len(binding["query_rows"]), 29)
        self.assertEqual(binding["github_repository_search"]["preserve_first_n_items"], 50)
        self.assertEqual(binding["general_web_search"]["provider"], "DuckDuckGo HTML")
        self.assertEqual(binding["general_web_search"]["preserve_first_n_items"], 20)
        self.assertTrue(all(value == 0 for value in binding["execution_state"].values()))
        self.assertFalse(binding["claim_boundary"]["artifact_discovered"])


if __name__ == "__main__":
    unittest.main()
