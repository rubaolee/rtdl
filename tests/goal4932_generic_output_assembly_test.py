from pathlib import Path
import importlib.util
import sys
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from rtdsl.output_assembly import GroupedSequenceAssemblyPlan
from rtdsl.output_assembly import assemble_grouped_sequences


class Goal4932GenericOutputAssemblyTest(unittest.TestCase):
    def test_public_grouped_sequence_assembly_api_is_exported(self):
        self.assertIs(rt.GroupedSequenceAssemblyPlan, GroupedSequenceAssemblyPlan)
        self.assertIs(rt.assemble_grouped_sequences, assemble_grouped_sequences)
        self.assertIn("GroupedSequenceAssemblyPlan", rt.__all__)
        self.assertIn("GroupedSequenceAssemblyResult", rt.__all__)
        self.assertIn("assemble_grouped_sequences", rt.__all__)
        self.assertIn("GroupedSequenceAssemblyPlan", dir(rt))
        self.assertIn("assemble_grouped_sequences", dir(rt))

    def test_groups_rows_deterministically_by_key_and_order(self):
        columns = {
            "group_id": np.asarray([2, 1, 2, 1], dtype=np.int64),
            "rank": np.asarray([1, 2, 0, 1], dtype=np.int64),
            "value": np.asarray([20, 12, 10, 11], dtype=np.int64),
        }
        plan = GroupedSequenceAssemblyPlan(
            group_key_columns=("group_id",),
            order_key_columns=("rank",),
            payload_columns=("value",),
        )

        result = assemble_grouped_sequences(columns, plan)

        np.testing.assert_array_equal(result.group_keys["group_id"], np.asarray([1, 2]))
        np.testing.assert_array_equal(result.group_offsets, np.asarray([0, 2]))
        np.testing.assert_array_equal(result.group_lengths, np.asarray([2, 2]))
        np.testing.assert_array_equal(result.item_columns["value"], np.asarray([11, 12, 10, 20]))
        self.assertEqual(result.stats["schema"], "rtdl.grouped_sequence_assembly.v1")
        self.assertEqual(result.stats["group_count"], 2)

    def test_validity_and_consecutive_dedupe_are_generic(self):
        columns = {
            "group_id": np.asarray([1, 1, 1, 1, 2], dtype=np.int64),
            "rank": np.asarray([0, 1, 2, 3, 0], dtype=np.int64),
            "point_id": np.asarray([7, 7, 8, 9, 7], dtype=np.int64),
            "x": np.asarray([1.0, 1.0, 2.0, 99.0, 3.0], dtype=np.float64),
            "emit": np.asarray([1, 1, 1, 0, 1], dtype=np.int8),
        }
        plan = GroupedSequenceAssemblyPlan(
            group_key_columns=("group_id",),
            order_key_columns=("rank",),
            payload_columns=("point_id", "x"),
            validity_column="emit",
            dedupe_key_columns=("point_id",),
        )

        result = assemble_grouped_sequences(columns, plan)

        np.testing.assert_array_equal(result.group_keys["group_id"], np.asarray([1, 2]))
        np.testing.assert_array_equal(result.group_lengths, np.asarray([2, 1]))
        np.testing.assert_array_equal(result.item_columns["point_id"], np.asarray([7, 8, 7]))
        np.testing.assert_allclose(result.item_columns["x"], np.asarray([1.0, 2.0, 3.0]))
        self.assertEqual(result.stats["valid_rows"], 4)
        self.assertTrue(result.stats["dedupe_enabled"])

    def test_non_rayjoin_spatial_join_grouped_pairs_consumer(self):
        columns = {
            "left_id": np.asarray([3, 1, 1, 3, 2], dtype=np.int64),
            "right_id": np.asarray([30, 12, 10, 31, 20], dtype=np.int64),
            "score": np.asarray([0.3, 0.9, 0.1, 0.2, 0.7], dtype=np.float64),
            "emit": np.asarray([1, 1, 1, 1, 0], dtype=np.int8),
        }
        plan = GroupedSequenceAssemblyPlan(
            group_key_columns=("left_id",),
            order_key_columns=("right_id",),
            payload_columns=("right_id", "score"),
            validity_column="emit",
        )

        result = assemble_grouped_sequences(columns, plan)
        grouped = {}
        for group_index, left_id in enumerate(result.group_keys["left_id"]):
            rows = result.group_slice(group_index)
            grouped[int(left_id)] = result.item_columns["right_id"][rows].tolist()

        self.assertEqual(grouped, {1: [10, 12], 3: [30, 31]})
        self.assertEqual(result.stats["input_rows"], 5)
        self.assertEqual(result.stats["item_rows"], 4)

    def test_section57_like_chain_descriptor_shape_without_app_formatting(self):
        columns = {
            "chain_id": np.asarray([20, 10, 10, 20, 20], dtype=np.int64),
            "point_order": np.asarray([1, 1, 0, 0, 2], dtype=np.int64),
            "point_id": np.asarray([4, 2, 1, 3, 5], dtype=np.int64),
            "x": np.asarray([4.0, 2.0, 1.0, 3.0, 5.0], dtype=np.float64),
            "y": np.asarray([40.0, 20.0, 10.0, 30.0, 50.0], dtype=np.float64),
            "emit": np.asarray([1, 1, 1, 1, 1], dtype=np.int8),
        }
        plan = GroupedSequenceAssemblyPlan(
            group_key_columns=("chain_id",),
            order_key_columns=("point_order",),
            payload_columns=("point_id", "x", "y"),
            validity_column="emit",
            output_shape="descriptors_and_items",
        )

        result = assemble_grouped_sequences(columns, plan)

        np.testing.assert_array_equal(result.group_keys["chain_id"], np.asarray([10, 20]))
        np.testing.assert_array_equal(result.group_offsets, np.asarray([0, 2]))
        np.testing.assert_array_equal(result.group_lengths, np.asarray([2, 3]))
        np.testing.assert_array_equal(result.item_columns["point_id"], np.asarray([1, 2, 3, 4, 5]))
        self.assertEqual(result.stats["output_shape"], "descriptors_and_items")

    def test_section57_app_adapter_can_use_generic_assembly_on_tiny_case(self):
        module_path = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_numba.py"
        spec = importlib.util.spec_from_file_location("goal4932_section57_overlay_numba", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules["goal4932_section57_overlay_numba"] = module
        spec.loader.exec_module(module)

        left = SimpleNamespace(
            chain_count=1,
            chain_offsets=np.asarray([0], dtype=np.int64),
            chain_point_counts=np.asarray([2], dtype=np.int64),
            chain_left_faces=np.asarray([10], dtype=np.int64),
            chain_right_faces=np.asarray([0], dtype=np.int64),
            point_x=np.asarray([0.0, 1.0], dtype=np.float64),
            point_y=np.asarray([0.0, 0.0], dtype=np.float64),
        )
        right = SimpleNamespace(
            chain_count=1,
            chain_offsets=np.asarray([0], dtype=np.int64),
            chain_point_counts=np.asarray([2], dtype=np.int64),
            chain_left_faces=np.asarray([30], dtype=np.int64),
            chain_right_faces=np.asarray([0], dtype=np.int64),
            point_x=np.asarray([0.0, 1.0], dtype=np.float64),
            point_y=np.asarray([1.0, 1.0], dtype=np.float64),
        )
        point_faces = (
            np.asarray([20, 20], dtype=np.int64),
            np.asarray([40, 40], dtype=np.int64),
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = root / "expected.txt"
            actual = root / "actual.txt"
            module.base.write_output_chains_streaming((left, right), ([], []), point_faces, expected)
            stats = module.write_output_chains_streaming_numba_skip((left, right), ([], []), point_faces, actual)

            self.assertEqual(expected.read_text(encoding="utf-8"), actual.read_text(encoding="utf-8"))
            self.assertTrue(stats["generic_output_assembly"]["enabled"])
            self.assertEqual(stats["generic_output_assembly"]["group_count"], 2)
            self.assertEqual(stats["chain_count"], 2)

    def test_output_assembly_module_contains_no_app_identity(self):
        source = (ROOT / "src" / "rtdsl" / "output_assembly.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("rayjoin", source)
        self.assertNotIn("overlay", source)
        self.assertNotIn("section57", source)


if __name__ == "__main__":
    unittest.main()
