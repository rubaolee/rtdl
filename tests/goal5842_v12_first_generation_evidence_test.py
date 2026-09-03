"""Fail-closed custody tests for the formal Goal5842 V12 Ada transaction."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import goal5842_build_first_generation_authority as authority_builder

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_PATH = (
    ROOT / "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "V12_ADA_FIRST_GENERATION_AUTHORITY.json"
)


class Goal5842V12FirstGenerationEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stored = json.loads(AUTHORITY_PATH.read_text(encoding="ascii"))

    def test_authority_rebuild_replays_exact_frozen_recount(self) -> None:
        rebuilt = authority_builder.build()
        self.assertEqual(rebuilt, self.stored)
        self.assertEqual(
            rebuilt["authority_sha256"],
            authority_builder.authority_seal(rebuilt),
        )
        self.assertTrue(
            rebuilt["execution"]["local_recount_byte_identical_to_pod_recount"]
        )
        self.assertTrue(
            rebuilt["identity_witnesses"][
                "all_registered_baseline_cross_arm_public_outputs_exact"
            ]
        )
        self.assertFalse(
            rebuilt["identity_witnesses"]["sphere_provider_baseline_claimed"]
        )

    def test_same_size_archive_mutation_fails_before_extraction(self) -> None:
        source = authority_builder.ARCHIVE_PATH.read_bytes()
        mutated = bytearray(source)
        mutated[len(mutated) // 2] ^= 0x01
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "mutated.tar.gz"
            archive.write_bytes(mutated)
            destination = root / "extracted"
            destination.mkdir()
            with (
                mock.patch.object(authority_builder, "ARCHIVE_PATH", archive),
                self.assertRaisesRegex(RuntimeError, "archive SHA mismatch"),
            ):
                authority_builder.extract_verified_archive(destination)
            self.assertEqual(list(destination.iterdir()), [])

    def test_one_generation_cannot_be_relabelled_as_goal_completion(self) -> None:
        self.assertEqual(
            self.stored["status"],
            "PASS__V12_ADA_FIRST_GENERATION_EVIDENCE_VERIFIED__"
            "SECOND_GENERATION_REQUIRED",
        )
        boundary = self.stored["claim_boundary"]
        self.assertEqual(boundary["observed_gpu_architecture_generation_count"], 1)
        self.assertEqual(boundary["required_gpu_architecture_generation_count"], 2)
        for key in (
            "goal5842_complete",
            "cross_generation_gate_passed",
            "cross_machine_raw_time_ratio_computed",
            "public_performance_claim_authorized",
            "external_review_or_consensus",
            "checker_off_is_supported_api",
            "checker_removal_recommended",
            "hardware_independent_performance_claimed",
        ):
            self.assertIs(boundary[key], False, key)

    def test_all_adverse_baseline_ratios_and_three_causal_tasks_are_retained(
        self,
    ) -> None:
        causal = self.stored["causal_summaries"]
        baseline = self.stored["baseline_summaries"]
        self.assertEqual(len(causal), 3)
        self.assertEqual({row["worker_count"] for row in causal}, {72})
        self.assertEqual(len(baseline), 2)
        self.assertEqual({len(row["comparisons"]) for row in baseline}, {6})
        self.assertTrue(
            all(
                comparison["registered_gate"] is None
                for row in baseline
                for comparison in row["comparisons"]
            )
        )
        triangle = next(
            row
            for row in baseline
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
            108.748608164,
        )


if __name__ == "__main__":
    unittest.main()
