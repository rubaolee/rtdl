from __future__ import annotations

import json
from pathlib import Path
import struct
import unittest

import rtdsl.v4_rtdlexe as public_runtime

from experiments.goal5803_sql_integer_bag_equijoin.integer_bag_equijoin import (
    DEFAULT_A,
    DEFAULT_B,
    IntegerJoinRow,
    MAX_EXACT_JOIN_KEY,
    MAX_U32,
    MINIMUM_OVERLAP_F32,
    build_public_inputs,
    relation_rows,
)
from experiments.goal5803_sql_integer_bag_equijoin.sqlite_oracle import (
    pure_python_integer_bag_oracle,
    sqlite_integer_bag_equijoin_oracle,
)


ROOT = Path(__file__).resolve().parents[1]
PREACTION = (
    ROOT / "experiments/goal5803_sql_integer_bag_equijoin/preaction.json"
)


def _plain(rows):
    return tuple(row.as_pair() for row in rows)


def _f32(value: float | int) -> float:
    """Round one scalar through the actual little-endian binary32 ABI."""

    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _f32_area(left, right) -> float:
    lx0, ly0, lx1, ly1 = (_f32(value) for value in left[:4])
    rx0, ry0, rx1, ry1 = (_f32(value) for value in right[:4])
    width = _f32(max(_f32(0.0), _f32(min(lx1, rx1) - max(lx0, rx0))))
    height = _f32(max(_f32(0.0), _f32(min(ly1, ry1) - max(ly0, ry0))))
    return _f32(width * height)


def _f32_geometry_pairs(indexed, sources):
    pairs = []
    for source in sources:
        for target in indexed:
            if _f32_area(source, target) >= _f32(MINIMUM_OVERLAP_F32):
                pairs.append((source[4], target[4]))
    # Row ids are unique within each input side, so no two distinct SQL
    # Cartesian rows can collapse to the same application-visible id pair.
    return tuple(sorted(pairs))


class Goal5803SqlIntegerBagEquijoinHostileTest(unittest.TestCase):
    def test_true_f32_upper_boundary_is_exact_and_adjacent_keys_do_not_join(self):
        critical_keys = (
            0,
            1,
            (1 << 23) - 1,
            1 << 23,
            MAX_EXACT_JOIN_KEY - 1,
            MAX_EXACT_JOIN_KEY,
        )
        for key in critical_keys:
            with self.subTest(key=key):
                self.assertEqual(_f32(key), float(key))
                self.assertEqual(_f32(key + 1), float(key + 1))
                indexed, sources = relation_rows(
                    (IntegerJoinRow(1, key),),
                    (IntegerJoinRow(2, key),),
                )
                self.assertEqual(_f32_area(sources[0], indexed[0]), 1.0)
                self.assertEqual(
                    _f32_geometry_pairs(indexed, sources), ((1, 2),))

        lower = MAX_EXACT_JOIN_KEY - 1
        upper = MAX_EXACT_JOIN_KEY
        for a_key, b_key in ((lower, upper), (upper, lower)):
            with self.subTest(a_key=a_key, b_key=b_key):
                indexed, sources = relation_rows(
                    (IntegerJoinRow(3, a_key),),
                    (IntegerJoinRow(4, b_key),),
                )
                self.assertEqual(_f32_area(sources[0], indexed[0]), 0.0)
                self.assertEqual(_f32_geometry_pairs(indexed, sources), ())

        with self.assertRaises(ValueError):
            IntegerJoinRow(5, 1 << 24)

    def test_multirow_bag_multiplicity_matches_sqlite_python_and_f32_geometry(self):
        # Two duplicate-key rows on each side must produce four Cartesian
        # result rows per key, including at the exact-f32 upper endpoint.
        a_rows = (
            IntegerJoinRow(0, 0),
            IntegerJoinRow(MAX_U32, 0),
            IntegerJoinRow(5, MAX_EXACT_JOIN_KEY),
            IntegerJoinRow(6, MAX_EXACT_JOIN_KEY),
            IntegerJoinRow(7, 123),
        )
        b_rows = (
            IntegerJoinRow(MAX_U32, 0),
            IntegerJoinRow(0, 0),
            IntegerJoinRow(8, MAX_EXACT_JOIN_KEY),
            IntegerJoinRow(9, MAX_EXACT_JOIN_KEY),
            IntegerJoinRow(10, 124),
        )
        sqlite_pairs = sqlite_integer_bag_equijoin_oracle(
            _plain(a_rows), _plain(b_rows)).pairs
        python_pairs = pure_python_integer_bag_oracle(
            _plain(a_rows), _plain(b_rows))
        indexed, sources = relation_rows(a_rows, b_rows)
        geometry_pairs = _f32_geometry_pairs(indexed, sources)

        self.assertEqual(sqlite_pairs, python_pairs)
        self.assertEqual(geometry_pairs, sqlite_pairs)
        self.assertEqual(len(sqlite_pairs), 8)
        self.assertEqual(
            sum(1 for pair in sqlite_pairs if pair[0] in (0, MAX_U32)
                and pair[1] in (0, MAX_U32)),
            4,
        )
        self.assertEqual(
            sum(1 for pair in sqlite_pairs if pair[0] in (5, 6)
                and pair[1] in (8, 9)),
            4,
        )

    def test_adapter_constructs_the_real_exported_public_input_types(self):
        static, batch = build_public_inputs(
            public_runtime, DEFAULT_A, DEFAULT_B)
        self.assertIsInstance(static, public_runtime.BoundedRelationStaticInput)
        self.assertIsInstance(batch, public_runtime.BoundedRelationBatch)
        self.assertIsNone(batch.expected_rows)
        self.assertEqual(len(static.indexed_boxes), len(DEFAULT_B))
        self.assertEqual(len(batch.source_boxes), len(DEFAULT_A))
        # Construction normalizes every coordinate through the real f32 public
        # ABI without invoking load, prepare, execute, CUDA, or OptiX.
        for row in (*static.indexed_boxes, *batch.source_boxes):
            for coordinate in row[:4]:
                self.assertEqual(coordinate, _f32(coordinate))

    def test_threshold_and_capacity_remain_exact_execution_freeze_obligations(self):
        # The application adapter deliberately supplies neither threshold nor
        # capacity.  Therefore these local tests cannot be cited as proof that
        # a future prepared GPU owner used SQL equality semantics.  Before the
        # first GPU call, the runner must independently assert both the loaded
        # product projection and the prepared-owner values:
        #   minimum_overlap_f32 == 1.0 (inclusive), and
        #   semantic capacity >= the exact SQLite output cardinality.
        payload = json.loads(PREACTION.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["execution_rule"]["exact_execution_freeze_status"],
            "PENDING_CORE_SUCCESSOR_IDENTITY",
        )
        self.assertIs(
            payload["execution_rule"]["gpu_call_authorized_by_this_preaction"],
            False,
        )
        self.assertEqual(
            payload["task"]["mapping"]["minimum_overlap_f32"], 1.0)
        self.assertEqual(
            payload["task"]["declared_domain"]["capacity"],
            "number of unique output id-pairs does not exceed the sealed "
            "semantic capacity",
        )
        static, batch = build_public_inputs(
            public_runtime, DEFAULT_A, DEFAULT_B)
        self.assertFalse(hasattr(static, "minimum_overlap_f32"))
        self.assertFalse(hasattr(batch, "minimum_overlap_f32"))
        self.assertFalse(hasattr(static, "capacity"))
        self.assertFalse(hasattr(batch, "capacity"))

    def test_task_selection_ceiling_cannot_be_promoted_to_generalization(self):
        payload = json.loads(PREACTION.read_text(encoding="utf-8"))
        lineage = payload["lineage"]
        ceiling = payload["claim_ceiling"]
        self.assertIs(lineage["this_task_selected_by_project"], True)
        self.assertIs(
            lineage["this_task_selected_after_predecessor_failure_was_observed"],
            True,
        )
        self.assertIs(lineage["blind_claim_allowed"], False)
        self.assertIs(lineage["unseen_claim_allowed"], False)
        self.assertIs(
            ceiling["constructive_cross_domain_existing_family_reuse_witness_allowed"],
            True,
        )
        self.assertIs(
            ceiling["unbiased_generalization_or_transfer_rate_claim_allowed"],
            False,
        )


if __name__ == "__main__":
    unittest.main()
