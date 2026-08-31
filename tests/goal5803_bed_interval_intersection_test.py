from __future__ import annotations

import json
from pathlib import Path
import unittest

from experiments.goal5803_bed_interval_intersection.bed_transfer import (
    BedInterval,
    DEFAULT_A,
    DEFAULT_B,
    DEFAULT_EXPECTED_PAIRS,
    MAX_EXACT_F32_INTEGER,
    MINIMUM_OVERLAP_F32,
    bedtools_default_pair_oracle,
    build_public_inputs,
    relation_rows,
)
from experiments.goal5803_bed_interval_intersection.run_untimed import (
    _execute_expected_capacity_overflow,
)


class Goal5803BedIntervalIntersectionTest(unittest.TestCase):
    def test_preaction_freezes_external_semantics_and_honest_claim_ceiling(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((
            root / "experiments/goal5803_bed_interval_intersection/preaction.json"
        ).read_text(encoding="utf-8"))
        self.assertEqual(
            payload["status"],
            "TASK_SEMANTICS_DECLARED_BEFORE_IMPLEMENTATION__"
            "EXACT_EXECUTION_BYTES_FROZEN_BEFORE_NEXT_GPU_CALL",
        )
        self.assertIn("bedtools", payload["task"]["external_specification"]["provider"])
        self.assertEqual(payload["task"]["mapping"]["minimum_overlap_f32"], 1.0)
        exposure = payload["selection_and_exposure"]
        for key in (
            "blind_claim_allowed", "held_out_claim_allowed",
            "unseen_claim_allowed", "third_party_user_claim_allowed",
        ):
            self.assertIs(exposure[key], False)
        self.assertIs(payload["claim_ceiling"]["transfer_rate_claim_allowed"], False)
        chronology = payload["chronology_and_governance_boundary"]
        self.assertIs(chronology["implementation_preregistered_claim_allowed"], False)
        self.assertIs(
            chronology["first_home_gpu_attempt_scientific_task_executed"], False)
        artifact = payload["frozen_execution_artifact"]
        self.assertEqual(artifact["deployment_id"], "goal5801/lx1/relation/v14")
        self.assertEqual(artifact["artifact_sha256"],
                         "71a9a9f1b99612373f67f11dd70b613b13493776f0916ccf007a25cdc14924d6")
        self.assertEqual(artifact["native_sha256"],
                         "912ad474868c72c9ba24b1ab98d005f0279c0d205abe884cca692c5e721a23bd")

    def test_execution_freeze_binds_current_exam_bytes(self):
        root = Path(__file__).resolve().parents[1]
        freeze_path = (
            root
            / "experiments/goal5803_bed_interval_intersection/"
              "execution_freeze_v2.json"
        )
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        self.assertEqual(
            freeze["status"],
            "FROZEN_BEFORE_NEXT_GPU_CALL__NO_SCIENTIFIC_RESULT_YET",
        )
        self.assertEqual(len(freeze["files"]), 4)
        for row in freeze["files"]:
            path = root / row["path"]
            import hashlib
            self.assertEqual(path.stat().st_size, row["bytes"])
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"])
    def test_default_fixture_covers_hits_misses_boundaries_and_chromosomes(self):
        observed = bedtools_default_pair_oracle(DEFAULT_A, DEFAULT_B)
        self.assertEqual(observed, DEFAULT_EXPECTED_PAIRS)
        # Adjacent half-open boundaries are not overlap.
        self.assertNotIn((100, 201), observed)
        self.assertNotIn((101, 200), observed)
        self.assertNotIn((103, 203), observed)
        # Same coordinates on different chromosomes are not overlap.
        self.assertNotIn((100, 206), observed)
        # A one-base overlap at the largest exact f32 integer remains live.
        self.assertIn((104, 204), observed)

    def test_aabb_mapping_exactly_separates_chromosomes_and_boundaries(self):
        indexed, sources = relation_rows(DEFAULT_A, DEFAULT_B)
        self.assertEqual(len(indexed), len(DEFAULT_B))
        self.assertEqual(len(sources), len(DEFAULT_A))
        # IDs and exact integer x coordinates survive the mapping.
        max_a = next(row for row in sources if row[4] == 104)
        self.assertEqual(max_a[0], float(MAX_EXACT_F32_INTEGER - 1))
        self.assertEqual(max_a[2], float(MAX_EXACT_F32_INTEGER))
        # Same chromosome has identical y band; different chromosomes have a gap.
        a_chr1 = next(row for row in sources if row[4] == 100)
        b_chr1 = next(row for row in indexed if row[4] == 200)
        b_chr4 = next(row for row in indexed if row[4] == 206)
        self.assertEqual(a_chr1[1:4:2], b_chr1[1:4:2])
        self.assertLess(a_chr1[3], b_chr4[1])
        self.assertEqual(MINIMUM_OVERLAP_F32, 1.0)

    def test_public_inputs_do_not_receive_oracle(self):
        class Static:
            def __init__(self, *, indexed_boxes):
                self.indexed_boxes = indexed_boxes

        class Batch:
            def __init__(self, *, source_boxes, expected_rows):
                self.source_boxes = source_boxes
                self.expected_rows = expected_rows

        module = type("Public", (), {
            "BoundedRelationStaticInput": Static,
            "BoundedRelationBatch": Batch,
        })
        static, batch = build_public_inputs(module, DEFAULT_A, DEFAULT_B)
        self.assertEqual(len(static.indexed_boxes), len(DEFAULT_B))
        self.assertEqual(len(batch.source_boxes), len(DEFAULT_A))
        self.assertIsNone(batch.expected_rows)

    def test_real_public_input_types_accept_frozen_mapping_without_oracle(self):
        import rtdsl

        static, batch = build_public_inputs(rtdsl, DEFAULT_A, DEFAULT_B)
        self.assertIsInstance(static, rtdsl.BoundedRelationStaticInput)
        self.assertIsInstance(batch, rtdsl.BoundedRelationBatch)
        self.assertIsNone(batch.expected_rows)

    def test_binary32_closed_aabb_predicate_equals_half_open_bed_oracle(self):
        indexed, sources = relation_rows(DEFAULT_A, DEFAULT_B)
        mapped_pairs = set()
        for sx0, sy0, sx1, sy1, source_id in sources:
            for ix0, iy0, ix1, iy1, indexed_id in indexed:
                width = max(0.0, min(sx1, ix1) - max(sx0, ix0))
                height = max(0.0, min(sy1, iy1) - max(sy0, iy0))
                if width * height >= MINIMUM_OVERLAP_F32:
                    mapped_pairs.add((source_id, indexed_id))
        self.assertEqual(tuple(sorted(mapped_pairs)), DEFAULT_EXPECTED_PAIRS)

    def test_mapping_matches_bed_oracle_exhaustively_on_small_domain(self):
        intervals = tuple(
            (start, end)
            for start in range(6)
            for end in range(start + 1, 7)
        )
        next_id = 0
        for a_chromosome in ("chrA", "chrB"):
            for b_chromosome in ("chrA", "chrB"):
                for a_start, a_end in intervals:
                    for b_start, b_end in intervals:
                        next_id += 2
                        a = BedInterval(
                            a_chromosome, a_start, a_end, next_id)
                        b = BedInterval(
                            b_chromosome, b_start, b_end, next_id + 1)
                        expected = bool(bedtools_default_pair_oracle((a,), (b,)))
                        indexed, sources = relation_rows((a,), (b,))
                        sx0, sy0, sx1, sy1, _ = sources[0]
                        ix0, iy0, ix1, iy1, _ = indexed[0]
                        area = (
                            max(0.0, min(sx1, ix1) - max(sx0, ix0))
                            * max(0.0, min(sy1, iy1) - max(sy0, iy0))
                        )
                        self.assertEqual(
                            area >= MINIMUM_OVERLAP_F32,
                            expected,
                            (a, b, area),
                        )

    def test_capacity_plus_one_fixture_has_k_plus_one_unique_bed_pairs(self):
        capacity = 4096
        a_rows = tuple(
            BedInterval("chrOverflow", 10, 11, index)
            for index in range(capacity + 1)
        )
        b_rows = (BedInterval("chrOverflow", 0, 100, 0),)
        observed = bedtools_default_pair_oracle(a_rows, b_rows)
        self.assertEqual(len(observed), capacity + 1)
        self.assertEqual(observed[0], (0, 0))
        self.assertEqual(observed[-1], (capacity, 0))

    def test_capacity_branch_accepts_only_exact_public_overflow_code(self):
        class ExecutableError(RuntimeError):
            def __init__(self, code):
                self.code = code
                super().__init__(code)

        class Prepared:
            def __init__(self, outcome):
                self.outcome = outcome

            def execute(self, _batch, *, include_diagnostics):
                self.include_diagnostics = include_diagnostics
                if isinstance(self.outcome, BaseException):
                    raise self.outcome
                return self.outcome

        accepted = Prepared(ExecutableError("RX041_OUTPUT_OVERFLOW"))
        self.assertEqual(
            _execute_expected_capacity_overflow(
                accepted, object(), executable_error_type=ExecutableError),
            ("RX041_OUTPUT_OVERFLOW", "RX041_OUTPUT_OVERFLOW"),
        )
        self.assertIs(accepted.include_diagnostics, False)

        for label, outcome, expected_error in (
            ("cuda", ExecutableError("RX031_CUDA_DRIVER_UNAVAILABLE"), RuntimeError),
            ("identity", ExecutableError("RX027_NATIVE_IDENTITY_MISMATCH"), RuntimeError),
            ("oom", MemoryError("oom"), MemoryError),
            ("result", object(), RuntimeError),
        ):
            with self.subTest(label=label), self.assertRaises(expected_error):
                _execute_expected_capacity_overflow(
                    Prepared(outcome), object(),
                    executable_error_type=ExecutableError,
                )

    def test_input_domain_rejects_lossy_or_ambiguous_bed_rows(self):
        bad = (
            ("zero_length", ("chr1", 4, 4, 1)),
            ("negative", ("chr1", -1, 4, 1)),
            ("f32_loss", ("chr1", 0, MAX_EXACT_F32_INTEGER + 1, 1)),
            ("bool", ("chr1", False, 4, 1)),
            ("bad_id", ("chr1", 0, 4, 1 << 32)),
        )
        for label, values in bad:
            with self.subTest(label=label), self.assertRaises(ValueError):
                BedInterval(*values)

    def test_duplicate_ids_fail_before_public_input_construction(self):
        duplicate_a = (
            BedInterval("chr1", 0, 2, 7),
            BedInterval("chr2", 0, 2, 7),
        )
        with self.assertRaisesRegex(ValueError, "ids must be unique"):
            bedtools_default_pair_oracle(duplicate_a, DEFAULT_B)


if __name__ == "__main__":
    unittest.main()
