from pathlib import Path
import sys
import time
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from rtdsl.output_assembly import GroupedOutputRowBufferSchema
from rtdsl.output_assembly import materialize_grouped_output_row_buffer
from rtdsl.output_assembly import prepare_grouped_output_row_buffer


def _python_reference_materialize(columns, schema):
    valid = np.ones(columns[schema.group_key_columns[0]].shape[0], dtype=bool)
    if schema.validity_column is not None:
        valid = np.asarray(columns[schema.validity_column], dtype=bool)
    valid_indices = np.nonzero(valid)[0]
    sort_keys = [np.asarray(columns[name][valid_indices]) for name in schema.group_key_columns + schema.item_order_columns]
    sort_keys.append(valid_indices)
    order = np.lexsort(tuple(reversed(sort_keys)))
    indices = valid_indices[order]

    group_key_values = []
    descriptors = {name: [] for name in schema.group_descriptor_columns}
    group_offsets = []
    group_lengths = []
    items = {name: [] for name in schema.item_payload_columns}
    current_group = None

    for source_index in indices:
        group = tuple(int(columns[name][source_index]) for name in schema.group_key_columns)
        if group != current_group:
            current_group = group
            group_key_values.append(group)
            group_offsets.append(len(next(iter(items.values()))) if items else 0)
            group_lengths.append(0)
            for name in schema.group_descriptor_columns:
                descriptors[name].append(columns[name][source_index])
        group_lengths[-1] += 1
        for name in schema.item_payload_columns:
            items[name].append(columns[name][source_index])

    return {
        "group_keys": group_key_values,
        "descriptors": descriptors,
        "group_offsets": group_offsets,
        "group_lengths": group_lengths,
        "items": items,
    }


class Goal4936OutputMaterializerTest(unittest.TestCase):
    def test_public_materializer_api_is_exported(self):
        self.assertIs(rt.materialize_grouped_output_row_buffer, materialize_grouped_output_row_buffer)
        self.assertIn("GroupedOutputMaterializationResult", rt.__all__)
        self.assertIn("materialize_grouped_output_row_buffer", rt.__all__)
        self.assertIn("materialize_grouped_output_row_buffer", dir(rt))

    def test_materializes_neutral_descriptor_and_item_columns(self):
        columns = {
            "group_id": np.asarray([2, 1, 1, 2], dtype=np.int64),
            "item_order": np.asarray([1, 1, 0, 0], dtype=np.int64),
            "group_label": np.asarray([20, 10, 10, 20], dtype=np.int64),
            "item_id": np.asarray([4, 2, 1, 3], dtype=np.int64),
            "x": np.asarray([4.0, 2.0, 1.0, 3.0], dtype=np.float64),
            "y": np.asarray([40.0, 20.0, 10.0, 30.0], dtype=np.float64),
        }
        schema = GroupedOutputRowBufferSchema(
            group_key_columns=("group_id",),
            item_order_columns=("item_order",),
            group_descriptor_columns=("group_label",),
            item_payload_columns=("item_id", "x", "y"),
        )

        row_buffer = prepare_grouped_output_row_buffer(columns, schema)
        result = materialize_grouped_output_row_buffer(row_buffer)

        np.testing.assert_array_equal(result.group_keys["group_id"], np.asarray([1, 2]))
        np.testing.assert_array_equal(result.descriptor_columns["group_label"], np.asarray([10, 20]))
        np.testing.assert_array_equal(result.group_offsets, np.asarray([0, 2]))
        np.testing.assert_array_equal(result.group_lengths, np.asarray([2, 2]))
        np.testing.assert_array_equal(result.item_columns["item_id"], np.asarray([1, 2, 3, 4]))
        self.assertEqual(result.stats["schema"], "rtdl.grouped_output_materialization.v1")
        self.assertEqual(result.group_count, 2)
        self.assertEqual(result.item_count, 4)

    def test_non_rayjoin_radius_neighbor_materialization(self):
        columns = {
            "query_id": np.asarray([9, 3, 3, 9], dtype=np.int64),
            "rank": np.asarray([1, 1, 0, 0], dtype=np.int64),
            "query_result_count": np.asarray([2, 2, 2, 2], dtype=np.int64),
            "neighbor_id": np.asarray([91, 32, 31, 90], dtype=np.int64),
            "distance": np.asarray([0.4, 0.2, 0.1, 0.3], dtype=np.float64),
        }
        schema = GroupedOutputRowBufferSchema(
            group_key_columns=("query_id",),
            item_order_columns=("rank",),
            group_descriptor_columns=("query_result_count",),
            item_payload_columns=("neighbor_id", "distance"),
        )

        result = materialize_grouped_output_row_buffer(prepare_grouped_output_row_buffer(columns, schema))

        grouped = {}
        for group_index, query_id in enumerate(result.group_keys["query_id"]):
            rows = result.group_slice(group_index)
            grouped[int(query_id)] = result.item_columns["neighbor_id"][rows].tolist()
        self.assertEqual(grouped, {3: [31, 32], 9: [90, 91]})

    def test_synthetic_scale_materializer_beats_python_loop(self):
        group_count = 20000
        items_per_group = 8
        row_count = group_count * items_per_group
        group_ids = np.repeat(np.arange(group_count, dtype=np.int64), items_per_group)
        item_order = np.tile(np.arange(items_per_group, dtype=np.int64), group_count)
        permutation = np.random.default_rng(4936).permutation(row_count)
        columns = {
            "group_id": group_ids[permutation],
            "item_order": item_order[permutation],
            "first_item_id": (group_ids * items_per_group)[permutation],
            "last_item_id": (group_ids * items_per_group + items_per_group - 1)[permutation],
            "item_id": np.arange(row_count, dtype=np.int64)[permutation],
            "x": (np.arange(row_count, dtype=np.float64) * 0.25)[permutation],
            "y": (np.arange(row_count, dtype=np.float64) * -0.5)[permutation],
        }
        schema = GroupedOutputRowBufferSchema(
            group_key_columns=("group_id",),
            item_order_columns=("item_order",),
            group_descriptor_columns=("first_item_id", "last_item_id"),
            item_payload_columns=("item_id", "x", "y"),
        )
        row_buffer = prepare_grouped_output_row_buffer(columns, schema)

        start = time.perf_counter()
        result = materialize_grouped_output_row_buffer(row_buffer)
        materializer_sec = time.perf_counter() - start

        start = time.perf_counter()
        reference = _python_reference_materialize(columns, schema)
        python_sec = time.perf_counter() - start

        self.assertEqual(result.group_count, group_count)
        self.assertEqual(result.item_count, row_count)
        self.assertEqual(len(reference["group_keys"]), group_count)
        self.assertLess(materializer_sec, python_sec)
        self.assertLess(materializer_sec, python_sec * 0.7)

    def test_output_assembly_module_still_contains_no_app_identity(self):
        source = (ROOT / "src" / "rtdsl" / "output_assembly.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("rayjoin", source)
        self.assertNotIn("overlay", source)
        self.assertNotIn("section57", source)
        self.assertNotIn("author", source)


if __name__ == "__main__":
    unittest.main()
