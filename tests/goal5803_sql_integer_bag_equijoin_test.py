from __future__ import annotations

import ast
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments.goal5803_sql_integer_bag_equijoin.integer_bag_equijoin import (
    DEFAULT_A,
    DEFAULT_B,
    DEFAULT_EXPECTED_PAIRS,
    IntegerJoinRow,
    MAX_EXACT_JOIN_KEY,
    MINIMUM_OVERLAP_F32,
    REUSE_A,
    REUSE_EXPECTED_PAIRS,
    build_public_inputs,
    relation_rows,
)
from experiments.goal5803_sql_integer_bag_equijoin.sqlite_oracle import (
    DDL_A,
    DDL_B,
    QUERY,
    main as oracle_main,
    pure_python_integer_bag_oracle,
    sqlite_integer_bag_equijoin_oracle,
)


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "experiments/goal5803_sql_integer_bag_equijoin"
PREACTION = CASE / "preaction.json"
TASK_FREEZE = CASE / "task_semantics_freeze.json"
ADAPTER = CASE / "integer_bag_equijoin.py"
ORACLE = CASE / "sqlite_oracle.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _plain(rows):
    return tuple(row.as_pair() for row in rows)


def _mapped_pairs(indexed, sources):
    pairs = set()
    for sx0, sy0, sx1, sy1, source_id in sources:
        for ix0, iy0, ix1, iy1, indexed_id in indexed:
            width = max(0.0, min(sx1, ix1) - max(sx0, ix0))
            height = max(0.0, min(sy1, iy1) - max(sy0, iy0))
            if width * height >= MINIMUM_OVERLAP_F32:
                pairs.add((source_id, indexed_id))
    return tuple(sorted(pairs))


class Goal5803SqlIntegerBagEquijoinTest(unittest.TestCase):
    def test_task_semantics_were_bound_before_implementation(self):
        freeze = json.loads(TASK_FREEZE.read_text(encoding="utf-8"))
        binding = freeze["preaction"]
        self.assertEqual(binding["bytes"], PREACTION.stat().st_size)
        self.assertEqual(binding["sha256"], _sha(PREACTION))
        self.assertEqual(
            binding["sha256"],
            "6cab8acb1b3bc7243232839074852c772fe5644560c923dea2da6328d7e71aa9",
        )
        chronology = freeze["chronology_observation"]
        self.assertIs(chronology["adapter_exists_at_freeze"], False)
        self.assertIs(
            chronology["independent_sqlite_oracle_exists_at_freeze"], False)
        self.assertIs(chronology["goal_specific_tests_exist_at_freeze"], False)
        self.assertEqual(chronology["gpu_call_count"], 0)
        authorization = freeze["authorization"]
        self.assertIs(authorization["local_cpu_tests"], True)
        self.assertIs(authorization["core_or_native_change"], False)
        self.assertIs(authorization["gpu_or_ssh_or_pod"], False)

    def test_preaction_preserves_bed_failure_and_post_failure_selection(self):
        payload = json.loads(PREACTION.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["status"],
            "TASK_SEMANTICS_FROZEN_BEFORE_ADAPTER_IMPLEMENTATION__"
            "EXACT_EXECUTION_FREEZE_PENDING",
        )
        lineage = payload["lineage"]
        self.assertEqual(lineage["predecessor_disposition"],
                         "CORE_CHANGE_REQUIRED")
        self.assertEqual(lineage["predecessor_observed_public_error"],
                         "RX035_DEVICE_STATUS_INVALID")
        self.assertEqual(lineage["predecessor_required_public_error"],
                         "RX041_OUTPUT_OVERFLOW")
        self.assertIs(lineage["predecessor_failure_preserved"], True)
        self.assertIs(
            lineage["generic_overflow_repair_may_count_only_as_regression"],
            True,
        )
        self.assertIs(
            lineage["this_task_selected_after_predecessor_failure_was_observed"],
            True,
        )
        for key in (
            "blind_claim_allowed", "unseen_claim_allowed",
            "held_out_claim_allowed", "unbiased_generalization_exam_claim_allowed",
            "third_party_author_claim_allowed",
        ):
            self.assertIs(lineage[key], False)

    def test_claim_ceiling_discloses_goal5798_unit_box_precedent(self):
        payload = json.loads(PREACTION.read_text(encoding="utf-8"))
        disclosure = payload["task"]["unit_box_precedent_disclosure"]
        self.assertIs(disclosure["goal5798_already_used_unit_boxes"], True)
        self.assertIs(disclosure["unit_box_geometry_claimed_new"], False)
        ceiling = payload["claim_ceiling"]
        self.assertIs(
            ceiling["constructive_cross_domain_existing_family_reuse_witness_allowed"],
            True,
        )
        for key in (
            "original_bed_failure_superseded_or_erased",
            "two_of_two_transfer_claim_allowed",
            "blind_unseen_or_held_out_claim_allowed",
            "unbiased_generalization_or_transfer_rate_claim_allowed",
            "new_protocol_or_geometry_family_claim_allowed",
            "arbitrary_callback_ir_gpu_transfer_claim_allowed",
            "third_party_user_or_author_claim_allowed",
            "usability_productivity_or_performance_claim_allowed",
        ):
            self.assertIs(ceiling[key], False)

    def test_implementation_constants_match_frozen_fixtures(self):
        payload = json.loads(PREACTION.read_text(encoding="utf-8"))
        task = payload["task"]
        self.assertEqual(task["oracle"]["ddl"], [DDL_A, DDL_B])
        self.assertEqual(task["oracle"]["query"], QUERY)
        mapping = task["mapping"]
        self.assertEqual(mapping["minimum_overlap_f32"],
                         MINIMUM_OVERLAP_F32)
        self.assertEqual(mapping["same_key_intersection_area"], 1.0)
        self.assertEqual(
            mapping["different_integer_key_maximum_intersection_area"], 0.0)
        self.assertIs(mapping["new_geometry_family_required"], False)
        self.assertIs(mapping["new_protocol_family_required"], False)
        normal = payload["frozen_fixtures"]["normal"]
        reuse = payload["frozen_fixtures"]["prepared_reuse_batch"]
        self.assertEqual(
            _plain(DEFAULT_A),
            tuple((row["row_id"], row["join_key"]) for row in normal["A"]),
        )
        self.assertEqual(
            _plain(DEFAULT_B),
            tuple((row["row_id"], row["join_key"]) for row in normal["B"]),
        )
        self.assertEqual(DEFAULT_EXPECTED_PAIRS,
                         tuple(map(tuple, normal["expected_pairs"])))
        self.assertEqual(
            _plain(REUSE_A),
            tuple((row["row_id"], row["join_key"]) for row in reuse["A"]),
        )
        self.assertEqual(REUSE_EXPECTED_PAIRS,
                         tuple(map(tuple, reuse["expected_pairs"])))

    def test_independent_sqlite_oracle_matches_both_frozen_batches(self):
        normal = sqlite_integer_bag_equijoin_oracle(
            _plain(DEFAULT_A), _plain(DEFAULT_B))
        reuse = sqlite_integer_bag_equijoin_oracle(
            _plain(REUSE_A), _plain(DEFAULT_B))
        self.assertEqual(normal.pairs, DEFAULT_EXPECTED_PAIRS)
        self.assertEqual(reuse.pairs, REUSE_EXPECTED_PAIRS)
        self.assertTrue(normal.sqlite_version)
        self.assertTrue(normal.sqlite_source_id)
        self.assertEqual(normal.oracle_source_sha256, _sha(ORACLE))
        self.assertEqual(
            normal.query_utf8_sha256,
            hashlib.sha256(QUERY.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            pure_python_integer_bag_oracle(_plain(DEFAULT_A), _plain(DEFAULT_B)),
            DEFAULT_EXPECTED_PAIRS,
        )

    def test_mapping_exactly_matches_sqlite_bag_semantics(self):
        indexed, sources = relation_rows(DEFAULT_A, DEFAULT_B)
        self.assertEqual(_mapped_pairs(indexed, sources), DEFAULT_EXPECTED_PAIRS)
        reuse_indexed, reuse_sources = relation_rows(REUSE_A, DEFAULT_B)
        self.assertEqual(
            _mapped_pairs(reuse_indexed, reuse_sources),
            REUSE_EXPECTED_PAIRS,
        )
        # The two-by-two duplicate key must retain all four row pairs.
        key_seven = tuple(
            row for row in _mapped_pairs(indexed, sources)
            if row[0] in (11, 12) and row[1] in (101, 102)
        )
        self.assertEqual(len(key_seven), 4)
        # Adjacent keys share only a zero-area boundary and must not join.
        self.assertNotIn((13, 104), _mapped_pairs(indexed, sources))
        self.assertNotIn((15, 106), _mapped_pairs(indexed, sources))
        # Both endpoints of the admitted exact-f32 key domain are live.
        self.assertIn((10, 100), _mapped_pairs(indexed, sources))
        self.assertIn((14, 105), _mapped_pairs(indexed, sources))
        max_source = next(row for row in sources if row[4] == 14)
        self.assertEqual(max_source[0], float(MAX_EXACT_JOIN_KEY))
        self.assertEqual(max_source[2], float(1 << 24))

    def test_mapping_iff_integer_equality_exhaustively_on_small_domain(self):
        next_id = 1
        for a_key in range(17):
            for b_key in range(17):
                a = (IntegerJoinRow(next_id, a_key),)
                b = (IntegerJoinRow(next_id + 1, b_key),)
                next_id += 2
                indexed, sources = relation_rows(a, b)
                observed = bool(_mapped_pairs(indexed, sources))
                self.assertEqual(observed, a_key == b_key,
                                 (a_key, b_key, indexed, sources))

    def test_public_inputs_never_receive_oracle(self):
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

    def test_adapter_rejects_rows_outside_frozen_domain(self):
        for label, values in (
            ("null", (1, None)),
            ("bool_key", (1, True)),
            ("negative_key", (1, -1)),
            ("too_large_key", (1, 1 << 24)),
            ("bool_id", (True, 1)),
            ("negative_id", (-1, 1)),
            ("too_large_id", (1 << 32, 1)),
        ):
            with self.subTest(label=label), self.assertRaises(ValueError):
                IntegerJoinRow(*values)
        with self.assertRaisesRegex(ValueError, "must be nonempty"):
            relation_rows((), DEFAULT_B)
        with self.assertRaisesRegex(ValueError, "must be nonempty"):
            relation_rows(DEFAULT_A, ())
        duplicate = (IntegerJoinRow(1, 1), IntegerJoinRow(1, 2))
        with self.assertRaisesRegex(ValueError, "ids must be unique"):
            relation_rows(duplicate, DEFAULT_B)

    def test_oracle_validates_independently_and_imports_no_project_code(self):
        tree = ast.parse(ORACLE.read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        self.assertFalse(any(name == "rtdsl" or name.startswith("rtdsl.")
                             for name in imports))
        self.assertFalse(any("integer_bag_equijoin" in name for name in imports))
        self.assertFalse(any(name in {"requests", "urllib", "socket"}
                             for name in imports))
        adapter_tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
        adapter_imports = []
        for node in ast.walk(adapter_tree):
            if isinstance(node, ast.Import):
                adapter_imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                adapter_imports.append(node.module or "")
        self.assertFalse(any(name == "rtdsl" or name.startswith("rtdsl.")
                             for name in adapter_imports))
        for bad in (
            ((), ((1, 1),)),
            (((1, 1),), ()),
            (((1, True),), ((2, 1),)),
            (((1, -1),), ((2, 1),)),
            (((1, 1), (1, 2)), ((2, 1),)),
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                sqlite_integer_bag_equijoin_oracle(*bad)

    def test_oracle_cli_is_create_only_and_emits_a_self_identifying_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.json"
            output_path = root / "output.json"
            input_path.write_text(json.dumps({
                "A": [list(row) for row in _plain(DEFAULT_A)],
                "B": [list(row) for row in _plain(DEFAULT_B)],
            }), encoding="utf-8")
            with patch.object(sys, "argv", [
                    "sqlite_oracle", "--input", str(input_path),
                    "--output", str(output_path)]), redirect_stdout(io.StringIO()):
                self.assertEqual(oracle_main(), 0)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(tuple(map(tuple, payload["pairs"])),
                             DEFAULT_EXPECTED_PAIRS)
            self.assertIs(payload["imports_rtdsl"], False)
            self.assertIs(payload["imports_application_adapter"], False)
            self.assertEqual(payload["network_call_count"], 0)
            with patch.object(sys, "argv", [
                    "sqlite_oracle", "--input", str(input_path),
                    "--output", str(output_path)]), self.assertRaises(FileExistsError):
                oracle_main()

    def test_no_execution_or_performance_authority_is_hidden(self):
        payload = json.loads(PREACTION.read_text(encoding="utf-8"))
        rule = payload["execution_rule"]
        self.assertEqual(rule["exact_execution_freeze_status"],
                         "PENDING_CORE_SUCCESSOR_IDENTITY")
        self.assertIs(rule["gpu_call_authorized_by_this_preaction"], False)
        self.assertIs(rule["performance_timing_allowed"], False)
        counts = payload["scientific_counts_before_execution"]
        self.assertEqual(counts["post_failure_project_selected_sql_successor_attempts"], 0)
        self.assertEqual(counts["post_failure_project_selected_sql_successor_passes"], 0)
        self.assertEqual(counts["unbiased_prospective_generalization_exams"], 0)


if __name__ == "__main__":
    unittest.main()
