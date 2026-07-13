from pathlib import Path
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from rtdsl.output_assembly import assemble_grouped_path_split_records
from rtdsl.output_assembly import materialize_grouped_output_row_buffer


class Goal4939GroupedPathSplitRecordsTest(unittest.TestCase):
    def test_public_path_split_api_is_exported(self):
        self.assertIs(rt.assemble_grouped_path_split_records, assemble_grouped_path_split_records)
        self.assertIn("assemble_grouped_path_split_records", rt.__all__)
        self.assertIn("assemble_grouped_path_split_records", dir(rt))

    def test_non_app_path_segmentation_fixture(self):
        row_buffer = assemble_grouped_path_split_records(
            chain_ids=np.asarray([10], dtype=np.int64),
            chain_point_offsets=np.asarray([0], dtype=np.int64),
            chain_point_counts=np.asarray([3], dtype=np.int64),
            point_x=np.asarray([0.0, 10.0, 20.0], dtype=np.float64),
            point_y=np.asarray([0.0, 0.0, 0.0], dtype=np.float64),
            split_chain_ids=np.asarray([10, 10, 10], dtype=np.int64),
            split_edge_orders=np.asarray([0, 1, 1], dtype=np.int64),
            split_event_orders=np.asarray([0, 0, 1], dtype=np.int64),
            split_x=np.asarray([5.0, 12.0, 18.0], dtype=np.float64),
            split_y=np.asarray([0.0, 0.0, 0.0], dtype=np.float64),
            interval_descriptor_columns={
                "zone_id": np.asarray([101, 102, 103, 104], dtype=np.int64),
            },
        )

        result = materialize_grouped_output_row_buffer(row_buffer)

        self.assertEqual(row_buffer.stats["producer_schema"], "rtdl.grouped_path_split_records.v1")
        self.assertEqual(row_buffer.stats["chain_count"], 1)
        self.assertEqual(row_buffer.stats["split_event_count"], 3)
        self.assertEqual(row_buffer.stats["interval_count"], 4)
        self.assertEqual(result.group_count, 4)
        np.testing.assert_array_equal(result.descriptor_columns["zone_id"], np.asarray([101, 102, 103, 104]))
        segments = []
        for group_index in range(result.group_count):
            rows = result.group_slice(group_index)
            segments.append(
                list(
                    zip(
                        result.item_columns["x"][rows].tolist(),
                        result.item_columns["y"][rows].tolist(),
                    )
                )
            )
        self.assertEqual(
            segments,
            [
                [(0.0, 0.0), (5.0, 0.0)],
                [(5.0, 0.0), (10.0, 0.0), (12.0, 0.0)],
                [(12.0, 0.0), (18.0, 0.0)],
                [(18.0, 0.0), (20.0, 0.0)],
            ],
        )

    def test_validity_mask_skips_intervals_without_reordering_remaining_records(self):
        row_buffer = assemble_grouped_path_split_records(
            chain_ids=[1],
            chain_point_offsets=[0],
            chain_point_counts=[2],
            point_x=[0.0, 10.0],
            point_y=[0.0, 0.0],
            split_chain_ids=[1],
            split_edge_orders=[0],
            split_event_orders=[0],
            split_x=[5.0],
            split_y=[0.0],
            interval_descriptor_columns={
                "class_id": np.asarray([7, 8], dtype=np.int64),
            },
            interval_validity=np.asarray([0, 1], dtype=np.int8),
            output_group_ids=np.asarray([100, 200], dtype=np.int64),
        )

        result = materialize_grouped_output_row_buffer(row_buffer)

        np.testing.assert_array_equal(result.group_keys["group_id"], np.asarray([200]))
        np.testing.assert_array_equal(result.descriptor_columns["class_id"], np.asarray([8]))
        rows = result.group_slice(0)
        np.testing.assert_array_equal(result.item_columns["x"][rows], np.asarray([5.0, 10.0]))

    def test_labeled_planar_chain_shape_without_domain_names(self):
        row_buffer = assemble_grouped_path_split_records(
            chain_ids=np.asarray([21, 22], dtype=np.int64),
            chain_point_offsets=np.asarray([0, 3], dtype=np.int64),
            chain_point_counts=np.asarray([3, 2], dtype=np.int64),
            point_x=np.asarray([0.0, 2.0, 4.0, 10.0, 14.0], dtype=np.float64),
            point_y=np.asarray([0.0, 0.0, 0.0, 1.0, 1.0], dtype=np.float64),
            split_chain_ids=np.asarray([21, 22], dtype=np.int64),
            split_edge_orders=np.asarray([0, 0], dtype=np.int64),
            split_event_orders=np.asarray([0, 0], dtype=np.int64),
            split_x=np.asarray([1.0, 12.0], dtype=np.float64),
            split_y=np.asarray([0.0, 1.0], dtype=np.float64),
            interval_descriptor_columns={
                "left_label": np.asarray([1, 2, 3, 4], dtype=np.int64),
                "right_label": np.asarray([11, 12, 13, 14], dtype=np.int64),
            },
        )

        result = materialize_grouped_output_row_buffer(row_buffer)

        self.assertEqual(result.group_count, 4)
        np.testing.assert_array_equal(result.descriptor_columns["left_label"], np.asarray([1, 2, 3, 4]))
        np.testing.assert_array_equal(result.descriptor_columns["right_label"], np.asarray([11, 12, 13, 14]))
        self.assertEqual(result.item_count, 9)

    def test_rejects_descriptor_with_wrong_interval_count(self):
        with self.assertRaisesRegex(ValueError, "must have 2 rows"):
            assemble_grouped_path_split_records(
                chain_ids=[1],
                chain_point_offsets=[0],
                chain_point_counts=[2],
                point_x=[0.0, 10.0],
                point_y=[0.0, 0.0],
                split_chain_ids=[1],
                split_edge_orders=[0],
                split_event_orders=[0],
                split_x=[5.0],
                split_y=[0.0],
                interval_descriptor_columns={"label": np.asarray([1], dtype=np.int64)},
            )

    def test_rejects_split_events_for_unknown_chains(self):
        with self.assertRaisesRegex(ValueError, "unknown chain ids"):
            assemble_grouped_path_split_records(
                chain_ids=[1],
                chain_point_offsets=[0],
                chain_point_counts=[2],
                point_x=[0.0, 10.0],
                point_y=[0.0, 0.0],
                split_chain_ids=[2],
                split_edge_orders=[0],
                split_event_orders=[0],
                split_x=[5.0],
                split_y=[0.0],
            )

    def test_output_assembly_module_still_contains_no_app_identity(self):
        source = (ROOT / "src" / "rtdsl" / "output_assembly.py").read_text(encoding="utf-8").lower()
        for forbidden in ("rayjoin", "overlay", "section57", "author", "map0", "map1"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
