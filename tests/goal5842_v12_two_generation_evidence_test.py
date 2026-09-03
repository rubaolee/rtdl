"""Fail-closed custody tests for Goal5842's V12 two-generation evidence."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import goal5842_build_final_authority as final_builder
from scripts import goal5842_build_second_generation_authority as ampere_builder


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "history/internal_docs/goal5842_causal_admission_cost_20260903"


class Goal5842V12TwoGenerationEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ampere = json.loads(
            (EVIDENCE / "V12_AMPERE_SECOND_GENERATION_AUTHORITY.json").read_text(
                encoding="ascii"
            )
        )
        cls.final = json.loads(
            (EVIDENCE / "GOAL5842_FINAL_INTERNAL_AUTHORITY.json").read_text(
                encoding="ascii"
            )
        )

    def test_ampere_authority_rebuilds_with_byte_identical_recount(self) -> None:
        rebuilt = ampere_builder.build()
        self.assertEqual(rebuilt, self.ampere)
        self.assertEqual(
            rebuilt["authority_sha256"], ampere_builder.authority_seal(rebuilt)
        )
        self.assertTrue(
            rebuilt["execution"]["local_recount_byte_identical_to_pod_recount"]
        )
        self.assertEqual(rebuilt["execution"]["causal_receipt_count"], 216)
        self.assertEqual(rebuilt["execution"]["baseline_subworker_count"], 216)
        self.assertEqual(rebuilt["execution"]["baseline_composite_count"], 108)

    def test_same_size_ampere_archive_mutation_fails_before_extraction(self) -> None:
        source = ampere_builder.ARCHIVE_PATH.read_bytes()
        mutated = bytearray(source)
        mutated[len(mutated) // 2] ^= 0x01
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "mutated.tar.gz"
            archive.write_bytes(mutated)
            destination = root / "extracted"
            destination.mkdir()
            with (
                mock.patch.object(ampere_builder, "ARCHIVE_PATH", archive),
                self.assertRaisesRegex(RuntimeError, "archive SHA mismatch"),
            ):
                ampere_builder.extract_verified_archive(destination)
            self.assertEqual(list(destination.iterdir()), [])

    def test_final_authority_requires_two_distinct_generation_identities(self) -> None:
        rebuilt = final_builder.build()
        self.assertEqual(rebuilt, self.final)
        self.assertEqual(
            rebuilt["authority_sha256"], final_builder.authority_seal(rebuilt)
        )
        basis = rebuilt["completion_basis"]
        self.assertEqual(basis["distinct_gpu_architecture_generation_count"], 2)
        self.assertEqual(basis["distinct_gpu_uuid_count"], 2)
        self.assertEqual(basis["local_byte_identical_recount_count"], 2)
        rows = rebuilt["generation_authorities"]
        self.assertEqual(
            {row["architecture_generation"] for row in rows}, {"ADA", "AMPERE"}
        )

    def test_internal_completion_does_not_authorize_public_claims(self) -> None:
        self.assertEqual(
            self.final["status"],
            "PASS__GOAL5842_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING",
        )
        boundary = self.final["claim_boundary"]
        self.assertTrue(boundary["goal5842_internal_technical_complete"])
        for key in (
            "goal5842_external_review_complete",
            "external_review_or_consensus",
            "public_performance_claim_authorized",
            "manuscript_performance_wording_authorized",
            "hardware_independent_timing_magnitude_claimed",
            "intrinsic_language_overhead_claimed",
            "checker_off_is_supported_api",
            "optimization_result_included",
        ):
            self.assertIs(boundary[key], False, key)

    def test_adverse_rows_and_optimization_boundary_are_retained(self) -> None:
        self.assertTrue(
            self.final["scientific_result"]["current_provider_baselines_are_adverse"]
        )
        self.assertFalse(
            self.final["scientific_result"]["checker_removal_recommended"]
        )
        triangle = next(
            row
            for row in self.ampere["baseline_summaries"]
            if row["task"] == "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"
        )
        ratios = {
            (row["metric"], row["denominator"]): row["median_ratio"]
            for row in triangle["comparisons"]
        }
        self.assertEqual(
            ratios[
                (
                    "steady_complete_execution_median_ns",
                    "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API",
                )
            ],
            155.210480493,
        )


if __name__ == "__main__":
    unittest.main()
