from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"
FREEZE = DOCS / "goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json"
MARKDOWN = DOCS / "goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.md"
A1_RAW = (
    DOCS
    / "goal5790_a1_home_s3_execution_evidence_staging_20260816"
    / "controller"
    / "RAW"
)
ADMISSION_SOURCE = (
    ROOT / "src" / "rtdsl" / "v4_semantic_physical_admission.py"
)
ADMISSION_SOURCE_SHA256 = (
    "eb8a4a33352b94ad18d95cabe1e9c89389427b09a2bf98dbae3028d8fa940267"
)


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(path)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Goal5791PreWorkerZeroClaimFreezeTest(unittest.TestCase):
    def test_every_controlling_predecessor_rehashes(self) -> None:
        freeze = _load(FREEZE)
        for record in freeze["controlling_predecessors"]:
            path = ROOT / record["path"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.stat().st_size, record["bytes"], path)
            self.assertEqual(_sha256(path), record["sha256"], path)

    def test_sigmetrics_doi_algorithm_ownership_and_experiment_scope_are_frozen(self) -> None:
        freeze = _load(FREEZE)
        prior = freeze["nearest_adjacent_primary_work"]
        self.assertEqual(prior["doi"], "10.1145/3727108")
        self.assertEqual(prior["doi_url"], "https://doi.org/10.1145/3727108")
        ownership = prior["attribution"]
        self.assertTrue(ownership["rt_1a2_algorithm_and_name_owned_by_paper_authors"])
        self.assertTrue(ownership["rt_2a1_algorithm_and_name_owned_by_paper_authors"])
        self.assertTrue(ownership["graph_to_bvh_geometry_mapping_owned_by_paper_authors"])
        self.assertTrue(ownership["graph_to_ray_mapping_owned_by_paper_authors"])
        self.assertFalse(ownership["goal5791_invents_or_selects_any_of_these"])

        experiment = freeze["goal5791_experiment_claim_freeze"]
        self.assertEqual(experiment["paper_algorithm"], "RT-2A1")
        self.assertTrue(experiment["paper_algorithm_is_fixed_not_selected"])
        self.assertFalse(experiment["rt_1a2_included"])
        self.assertFalse(experiment["particle_included"])
        self.assertFalse(experiment["v2_or_v3_arm_included"])
        self.assertFalse(experiment["author_binary_arm_included"])
        self.assertEqual(experiment["only_allowlisted_variant"],
                         "checked_u64_product_sum_downstream_lowering.v1")
        self.assertEqual(experiment["arms"]["fusion_on"]["event_count_per_qualified_home_lane"], 2)
        self.assertEqual(experiment["arms"]["fusion_off"]["event_count_per_qualified_home_lane"], 7)
        matrix = experiment["maximum_matrix"]
        self.assertEqual(matrix["independent_rows"], 6)
        self.assertEqual(matrix["maximum_fresh_parent_pid_workers"], 96)
        self.assertEqual(
            len(matrix["datasets"])
            * len(matrix["lifecycles"])
            * matrix["balanced_pairs_per_row"]
            * matrix["arms_per_pair"],
            matrix["maximum_fresh_parent_pid_workers"],
        )

    def test_a1_raw_rejects_prove_five_facade_plus_one_tps(self) -> None:
        expected = {
            "builtin_triangle__checked_u64_overflow__v1__product_admission_reject.json": True,
            "builtin_triangle__deterministic_tie_rank__v1__product_admission_reject.json": True,
            "builtin_triangle__discrete_interval_boundary__v1__product_admission_reject.json": True,
            "builtin_triangle__front_back_orientation__v1__product_admission_reject.json": False,
            "builtin_triangle__weighted_multiplicity__v1__product_admission_reject.json": True,
            "custom_aabb__closed_boundary__v1__product_admission_reject.json": True,
        }
        observed: dict[str, bool] = {}
        for name in expected:
            record = _load(A1_RAW / name)
            arm = record["arm_result"]
            observed[name] = arm["production_facade_called"]
            self.assertEqual(arm["compiler_call_count"], 0)
            self.assertEqual(arm["low_level_compiler_call_count"], 0)
            self.assertEqual(arm["native_prepare_call_count"], 0)
            self.assertEqual(arm["native_execute_call_count"], 0)
            self.assertEqual(arm["traversal_launch_count"], 0)
            self.assertFalse(arm["executable_issued"])
            self.assertFalse(arm["execution_authorized"])
        self.assertEqual(observed, expected)
        self.assertEqual(sum(observed.values()), 5)

        freeze = _load(FREEZE)["goal5790_a1_external_review_absorption"]
        counts = freeze["downstream_count_authority"]
        self.assertEqual(counts["public_semantically_admitted_facade_rejects"], 5)
        self.assertEqual(counts["earlier_typed_physical_schema_rejects"], 1)
        self.assertFalse(counts["particle_orientation_production_facade_called"])
        self.assertTrue(freeze["reviewer_transcription_defect"]["present"])
        self.assertFalse(freeze["reviewer_transcription_defect"]["scientific_artifact_defect"])

    def test_p3_wording_and_bounded_anti_circularity_reconstruct(self) -> None:
        freeze = _load(FREEZE)["goal5790_a1_external_review_absorption"]
        loci = freeze["p3_1_diagnostic_delta_locus"]
        self.assertEqual(set(loci["allowed_loci"]), {"input_buffer", "reducer", "predicate"})
        self.assertEqual(len(loci["case_loci"]), 6)
        self.assertEqual(loci["case_loci"]["builtin_triangle.checked_u64_overflow.v1"], "reducer")
        self.assertEqual(loci["case_loci"]["custom_aabb.closed_boundary.v1"], "predicate")

        particle = freeze["p3_2_particle_earliest_gate"]
        self.assertEqual(particle["observed_gate"], "verify_typed_physical_schema")
        self.assertEqual(particle["observed_rule"], "triangle_orientation_mapping")
        self.assertEqual(particle["calculus_contains_related_rule"],
                         "SP039_ORIENTATION_CONTRACT_MISMATCH")
        self.assertFalse(particle["production_facade_called"])

        hardware = freeze["p3_3_hardware_scope"]
        self.assertIn("GTX 1070", hardware["executed_evidence_target"])
        self.assertFalse(hardware["modern_rtx_or_rt_silicon_claim"])
        self.assertFalse(hardware["ada_rerun_required_to_close_this_presentational_item"])

        source = ADMISSION_SOURCE.read_text(encoding="utf-8")
        rules = set(re.findall(r"SP\d{3}_[A-Z0-9_]+", source))
        bounded = freeze["bounded_anti_circularity"]
        self.assertEqual(_sha256(ADMISSION_SOURCE), ADMISSION_SOURCE_SHA256)
        self.assertEqual(
            bounded["executed_admission_source_sha256"],
            ADMISSION_SOURCE_SHA256,
        )
        self.assertEqual(len(rules), bounded["distinct_sp_rule_count"])
        self.assertTrue(set(bounded["six_cases_trigger_unique_sp_rules"]).issubset(rules))
        self.assertIn("SP039_ORIENTATION_CONTRACT_MISMATCH", rules)
        self.assertIn("SP053_TARGET_CAPABILITY_MISSING", rules)
        for forbidden_name in (
            "rtxrmq", "librts", "particle tracking", "triangle counting",
            "com-dblp", "cit-patents", "soc-livejournal", "soc-livejournal1",
            "microfluidics", "microfluidics_5000", "rayjoin", "ray join",
            "rtdbscan", "rt-dbscan", "raydb", "ray db", "barneshut",
            "rt-barneshut", "x-hd", "rtnn",
        ):
            self.assertNotIn(forbidden_name, source.lower())
        self.assertEqual(bounded["admission_source_app_or_dataset_name_scan_matches"], 0)
        self.assertIn("bounded supporting evidence", bounded["allowed_wording"])

    def test_markdown_and_non_authorization_are_explicit(self) -> None:
        freeze = _load(FREEZE)
        markdown = MARKDOWN.read_text(encoding="utf-8")
        normalized_markdown = " ".join(markdown.split())
        self.assertIn("10.1145/3727108", markdown)
        self.assertIn("five facade rejects plus one earlier Typed Physical Schema reject",
                      normalized_markdown)
        self.assertIn("bounded supporting", normalized_markdown)
        authorization = freeze["authorization"]
        for key, value in authorization.items():
            if key.startswith("authorizes_"):
                self.assertFalse(value, key)
        self.assertFalse(freeze["scope"]["overall_goal5791_pre_pod_readiness_established"])
        self.assertEqual(freeze["scope"]["formal_worker_count"], 0)


if __name__ == "__main__":
    unittest.main()
