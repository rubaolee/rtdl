from __future__ import annotations

import copy
import json
import unittest

from scripts.goal5790_a1_rejected_encoding_cases import (
    CASE_IDS,
    RejectedEncodingContractError,
    build_suite,
    canonical_sha256,
    evaluate_case,
    expected_rejection_reasons,
    parse_suite_json,
    resign_suite_for_test,
    validate_suite,
)


class Goal5790A1RejectedEncodingCasesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = build_suite()

    def test_six_app_neutral_cases_recompute_real_wrong_outputs(self) -> None:
        self.assertEqual(tuple(row["case_id"] for row in self.suite["cases"]), CASE_IDS)
        self.assertEqual(len(self.suite["cases"]), 6)
        for row in self.suite["cases"]:
            expected, counterfactual = evaluate_case(
                row["case_id"], row["minimal_witness"])
            self.assertEqual(row["independent_oracle"]["expected_output"], expected)
            self.assertEqual(
                row["counterfactual_execution"]["counterfactual_output"],
                counterfactual,
            )
            self.assertNotEqual(expected, counterfactual, row["case_id"])
            self.assertFalse(row["counterfactual_execution"]["valid_optix_receipt_claimed"])
            self.assertEqual(
                expected_rejection_reasons(row), (row["expected_rule_id"],))

    def test_exact_minimal_counterexamples_are_frozen(self) -> None:
        rows = {row["case_id"]: row for row in self.suite["cases"]}
        self.assertEqual(
            rows[CASE_IDS[0]]["independent_oracle"]["expected_output"], 1)
        self.assertEqual(
            rows[CASE_IDS[0]]["counterfactual_execution"]["counterfactual_output"], 0)
        self.assertEqual(
            rows[CASE_IDS[1]]["independent_oracle"]["expected_output"], 0)
        self.assertEqual(
            rows[CASE_IDS[1]]["counterfactual_execution"]["counterfactual_output"], 1)
        self.assertEqual(
            rows[CASE_IDS[2]]["independent_oracle"]["expected_output"], 1 << 64)
        self.assertEqual(
            rows[CASE_IDS[2]]["counterfactual_execution"]["counterfactual_output"], 0)
        self.assertEqual(
            rows[CASE_IDS[3]]["independent_oracle"]["expected_output"], 5)
        self.assertEqual(
            rows[CASE_IDS[3]]["counterfactual_execution"]["counterfactual_output"], 2)
        self.assertEqual(
            rows[CASE_IDS[4]]["independent_oracle"]["expected_output"], [7, 9, 0])
        self.assertEqual(
            rows[CASE_IDS[4]]["counterfactual_execution"]["counterfactual_output"], [9, 7, 0])
        self.assertEqual(
            rows[CASE_IDS[5]]["independent_oracle"]["expected_output"], [[0, 1]])
        self.assertEqual(
            rows[CASE_IDS[5]]["counterfactual_execution"]["counterfactual_output"], [])

    def test_three_authorities_are_separately_pinned_and_valid_roundtrip(self) -> None:
        parsed = parse_suite_json(json.dumps(
            self.suite, sort_keys=True, allow_nan=False))
        self.assertEqual(parsed, self.suite)
        for row in parsed["cases"]:
            pins = {
                row["source_authority"]["authority_sha256"],
                row["semantic_authority"]["authority_sha256"],
                row["physical_authority"]["authority_sha256"],
            }
            self.assertEqual(len(pins), 3)
            for value in pins:
                self.assertRegex(value, r"^[0-9a-f]{64}$")

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_numbers(self) -> None:
        with self.assertRaisesRegex(RejectedEncodingContractError, "duplicate JSON key"):
            parse_suite_json('{"schema":"x","schema":"y","cases":[],"suite_sha256":"z"}')
        rendered = json.dumps(self.suite, sort_keys=True).replace(
            '"valid_optix_receipt_claimed": false',
            '"valid_optix_receipt_claimed": NaN',
            1,
        )
        with self.assertRaisesRegex(RejectedEncodingContractError, "non-finite JSON constant"):
            parse_suite_json(rendered)

    def test_unsigned_tamper_fails_case_digest(self) -> None:
        attacked = copy.deepcopy(self.suite)
        attacked["cases"][0]["minimal_witness"]["values"][0] = 99
        attacked["suite_sha256"] = canonical_sha256({
            "schema": attacked["schema"], "cases": attacked["cases"]})
        with self.assertRaisesRegex(RejectedEncodingContractError, "case.*digest mismatch"):
            validate_suite(attacked)

    def test_resigned_semantic_authority_substitution_still_fails(self) -> None:
        attacked = copy.deepcopy(self.suite)
        attacked["cases"][1]["semantic_authority"]["policy"]["tie_policy"] = (
            "rightmost_minimum_index")
        attacked = resign_suite_for_test(attacked)
        with self.assertRaisesRegex(
                RejectedEncodingContractError, "semantic_authority independent pin mismatch"):
            validate_suite(attacked)

    def test_resigned_physical_or_source_authority_substitution_still_fails(self) -> None:
        physical = copy.deepcopy(self.suite)
        physical["cases"][3]["physical_authority"]["guarantees"]["multiplicity"] = (
            "paper_owned_weighted_hit_multiplicity")
        physical = resign_suite_for_test(physical)
        with self.assertRaisesRegex(
                RejectedEncodingContractError, "physical_authority independent pin mismatch"):
            validate_suite(physical)

        source = copy.deepcopy(self.suite)
        source["cases"][5]["source_authority"]["sources"][0]["sha256"] = "0" * 64
        source = resign_suite_for_test(source)
        with self.assertRaisesRegex(
                RejectedEncodingContractError, "source_authority independent pin mismatch"):
            validate_suite(source)

    def test_resigned_false_oracle_and_counterfactual_outputs_fail_recomputation(self) -> None:
        false_oracle = copy.deepcopy(self.suite)
        false_oracle["cases"][0]["independent_oracle"]["expected_output"] = 0
        false_oracle = resign_suite_for_test(false_oracle)
        with self.assertRaisesRegex(
                RejectedEncodingContractError, "oracle recomputation mismatch"):
            validate_suite(false_oracle)

        false_counterfactual = copy.deepcopy(self.suite)
        false_counterfactual["cases"][2]["counterfactual_execution"][
            "counterfactual_output"] = 1 << 64
        false_counterfactual = resign_suite_for_test(false_counterfactual)
        with self.assertRaisesRegex(
                RejectedEncodingContractError, "counterfactual recomputation mismatch"):
            validate_suite(false_counterfactual)

    def test_schema_coverage_order_and_test_only_boundary_fail_closed(self) -> None:
        removed = copy.deepcopy(self.suite)
        removed["cases"].pop()
        removed = resign_suite_for_test(removed)
        with self.assertRaisesRegex(RejectedEncodingContractError, "exactly six cases"):
            validate_suite(removed)

        reordered = copy.deepcopy(self.suite)
        reordered["cases"][0], reordered["cases"][1] = (
            reordered["cases"][1], reordered["cases"][0])
        reordered = resign_suite_for_test(reordered)
        with self.assertRaisesRegex(RejectedEncodingContractError, "order/coverage mismatch"):
            validate_suite(reordered)

        for row in self.suite["cases"]:
            self.assertEqual(
                row["unsafe_transform"]["scope"],
                "test_only_nonregistrable_counterfactual",
            )
            self.assertFalse(row["unsafe_transform"]["production_authority_minted"])
            self.assertEqual(
                row["counterfactual_execution"]["execution_scope"],
                "cpu_recomputation_only__gpu_not_executed",
            )


if __name__ == "__main__":
    unittest.main()

