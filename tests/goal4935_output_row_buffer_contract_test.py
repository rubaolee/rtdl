from pathlib import Path
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from rtdsl.output_assembly import GroupedOutputRowBufferSchema
from rtdsl.output_assembly import assemble_grouped_output_row_buffer
from rtdsl.output_assembly import prepare_grouped_output_row_buffer


class Goal4935OutputRowBufferContractTest(unittest.TestCase):
    def test_public_row_buffer_contract_api_is_exported(self):
        self.assertIs(rt.GroupedOutputRowBufferSchema, GroupedOutputRowBufferSchema)
        self.assertIs(rt.prepare_grouped_output_row_buffer, prepare_grouped_output_row_buffer)
        self.assertIs(rt.assemble_grouped_output_row_buffer, assemble_grouped_output_row_buffer)
        self.assertIn("GroupedOutputRowBufferSchema", rt.__all__)
        self.assertIn("GroupedOutputRowBuffer", rt.__all__)
        self.assertIn("prepare_grouped_output_row_buffer", rt.__all__)
        self.assertIn("assemble_grouped_output_row_buffer", rt.__all__)
        self.assertIn("GroupedOutputRowBufferSchema", dir(rt))
        self.assertIn("prepare_grouped_output_row_buffer", dir(rt))

    def test_neutral_descriptor_and_item_columns_assemble(self):
        columns = {
            "group_id": np.asarray([2, 1, 1, 2], dtype=np.int64),
            "item_order": np.asarray([1, 1, 0, 0], dtype=np.int64),
            "group_label": np.asarray([20, 10, 10, 20], dtype=np.int64),
            "item_id": np.asarray([4, 2, 1, 3], dtype=np.int64),
            "x": np.asarray([4.0, 2.0, 1.0, 3.0], dtype=np.float64),
            "y": np.asarray([40.0, 20.0, 10.0, 30.0], dtype=np.float64),
            "emit": np.asarray([1, 1, 1, 1], dtype=np.int8),
        }
        schema = GroupedOutputRowBufferSchema(
            group_key_columns=("group_id",),
            item_order_columns=("item_order",),
            group_descriptor_columns=("group_label",),
            item_payload_columns=("item_id", "x", "y"),
            validity_column="emit",
        )

        row_buffer = prepare_grouped_output_row_buffer(columns, schema)
        result = assemble_grouped_output_row_buffer(row_buffer)

        self.assertEqual(row_buffer.stats["schema"], "rtdl.grouped_output_row_buffer.v1")
        self.assertEqual(row_buffer.stats["row_count"], 4)
        np.testing.assert_array_equal(result.group_keys["group_id"], np.asarray([1, 2]))
        np.testing.assert_array_equal(result.group_offsets, np.asarray([0, 2]))
        np.testing.assert_array_equal(result.group_lengths, np.asarray([2, 2]))
        np.testing.assert_array_equal(result.item_columns["group_label"], np.asarray([10, 10, 20, 20]))
        np.testing.assert_array_equal(result.item_columns["item_id"], np.asarray([1, 2, 3, 4]))

    def test_rejects_object_dtype_before_generic_materialization(self):
        columns = {
            "group_id": np.asarray([1, 1], dtype=np.int64),
            "item_order": np.asarray([0, 1], dtype=np.int64),
            "payload": np.asarray(["already formatted", "python text"], dtype=object),
        }
        schema = GroupedOutputRowBufferSchema(
            group_key_columns=("group_id",),
            item_order_columns=("item_order",),
            item_payload_columns=("payload",),
        )

        with self.assertRaisesRegex(ValueError, "object dtype"):
            prepare_grouped_output_row_buffer(columns, schema)

    def test_rejects_descriptor_that_changes_inside_group(self):
        columns = {
            "group_id": np.asarray([1, 1, 2], dtype=np.int64),
            "item_order": np.asarray([0, 1, 0], dtype=np.int64),
            "descriptor": np.asarray([7, 8, 9], dtype=np.int64),
            "payload": np.asarray([10, 11, 12], dtype=np.int64),
        }
        schema = GroupedOutputRowBufferSchema(
            group_key_columns=("group_id",),
            item_order_columns=("item_order",),
            group_descriptor_columns=("descriptor",),
            item_payload_columns=("payload",),
        )

        with self.assertRaisesRegex(ValueError, "changes within a group"):
            prepare_grouped_output_row_buffer(columns, schema)

    def test_rayjoin_style_adapter_can_map_to_neutral_columns(self):
        columns = {
            "group_id": np.asarray([10, 10, 20], dtype=np.int64),
            "item_order": np.asarray([0, 1, 0], dtype=np.int64),
            "first_item_id": np.asarray([1, 1, 3], dtype=np.int64),
            "last_item_id": np.asarray([2, 2, 3], dtype=np.int64),
            "left_region_id": np.asarray([101, 101, 103], dtype=np.int64),
            "right_region_id": np.asarray([202, 202, 204], dtype=np.int64),
            "item_id": np.asarray([1, 2, 3], dtype=np.int64),
            "x": np.asarray([0.0, 1.0, 2.0], dtype=np.float64),
            "y": np.asarray([0.0, 0.0, 1.0], dtype=np.float64),
        }
        schema = GroupedOutputRowBufferSchema(
            group_key_columns=("group_id",),
            item_order_columns=("item_order",),
            group_descriptor_columns=("first_item_id", "last_item_id", "left_region_id", "right_region_id"),
            item_payload_columns=("item_id", "x", "y"),
        )

        row_buffer = prepare_grouped_output_row_buffer(columns, schema)
        result = assemble_grouped_output_row_buffer(row_buffer)

        np.testing.assert_array_equal(result.group_keys["group_id"], np.asarray([10, 20]))
        self.assertEqual(result.group_count, 2)
        self.assertEqual(result.item_count, 3)
        np.testing.assert_array_equal(result.item_columns["item_id"], np.asarray([1, 2, 3]))
        self.assertEqual(result.stats["schema"], "rtdl.grouped_sequence_assembly.v1")

    def test_non_rayjoin_radius_neighbor_output_uses_same_shape(self):
        columns = {
            "query_id": np.asarray([5, 5, 8, 8, 8], dtype=np.int64),
            "rank": np.asarray([1, 0, 2, 0, 1], dtype=np.int64),
            "query_result_count": np.asarray([2, 2, 3, 3, 3], dtype=np.int64),
            "neighbor_id": np.asarray([52, 51, 83, 81, 82], dtype=np.int64),
            "distance": np.asarray([0.2, 0.1, 0.5, 0.3, 0.4], dtype=np.float64),
            "emit": np.asarray([1, 1, 0, 1, 1], dtype=np.int8),
        }
        schema = GroupedOutputRowBufferSchema(
            group_key_columns=("query_id",),
            item_order_columns=("rank",),
            group_descriptor_columns=("query_result_count",),
            item_payload_columns=("neighbor_id", "distance"),
            validity_column="emit",
        )

        row_buffer = prepare_grouped_output_row_buffer(columns, schema)
        result = assemble_grouped_output_row_buffer(row_buffer)
        grouped = {}
        for group_index, query_id in enumerate(result.group_keys["query_id"]):
            rows = result.group_slice(group_index)
            grouped[int(query_id)] = result.item_columns["neighbor_id"][rows].tolist()

        self.assertEqual(grouped, {5: [51, 52], 8: [81, 82]})
        self.assertEqual(result.item_count, 4)

    def test_output_assembly_module_still_contains_no_app_identity(self):
        source = (ROOT / "src" / "rtdsl" / "output_assembly.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("rayjoin", source)
        self.assertNotIn("overlay", source)
        self.assertNotIn("section57", source)
        self.assertNotIn("author", source)


if __name__ == "__main__":
    unittest.main()
