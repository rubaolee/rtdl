from pathlib import Path
import importlib.util
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.output_assembly import assemble_grouped_path_split_records
from rtdsl.output_assembly import materialize_grouped_output_row_buffer


def _load_spike_module():
    path = ROOT / "history" / "internal_docs" / "goal4951_compiled_path_split_spike.py"
    spec = importlib.util.spec_from_file_location("goal4951_compiled_path_split_spike", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


spike = _load_spike_module()


class Goal4951CompiledPathSplitSourceTest(unittest.TestCase):
    def test_spike_source_avoids_app_identity_terms(self):
        source = (ROOT / "history" / "internal_docs" / "goal4951_compiled_path_split_spike.py").read_text(
            encoding="utf-8"
        ).lower()
        for forbidden in ("rayjoin", "overlay", "section57", "author", "map0", "map1"):
            self.assertNotIn(forbidden, source)


@unittest.skipUnless(spike.NUMBA_AVAILABLE, "Goal4951 compiled spike requires numba")
class Goal4951CompiledPathSplitSpikeTest(unittest.TestCase):
    def _compare_to_reference(self, **kwargs):
        reference = materialize_grouped_output_row_buffer(
            assemble_grouped_path_split_records(**kwargs)
        )
        actual = materialize_grouped_output_row_buffer(
            spike.assemble_compiled_path_split_records(**kwargs)
        )
        np.testing.assert_array_equal(actual.group_keys["group_id"], reference.group_keys["group_id"])
        np.testing.assert_array_equal(actual.group_offsets, reference.group_offsets)
        np.testing.assert_array_equal(actual.group_lengths, reference.group_lengths)
        np.testing.assert_array_equal(actual.item_columns["x"], reference.item_columns["x"])
        np.testing.assert_array_equal(actual.item_columns["y"], reference.item_columns["y"])
        for name in reference.descriptor_columns:
            np.testing.assert_array_equal(actual.descriptor_columns[name], reference.descriptor_columns[name])

    def test_non_app_multi_chain_fixture_matches_reference(self):
        self._compare_to_reference(
            chain_ids=np.asarray([10, 11, 12], dtype=np.int64),
            chain_point_offsets=np.asarray([0, 3, 5], dtype=np.int64),
            chain_point_counts=np.asarray([3, 2, 4], dtype=np.int64),
            point_x=np.asarray([0.0, 10.0, 20.0, 100.0, 110.0, -1.0, 0.0, 1.0, 2.0]),
            point_y=np.asarray([0.0, 0.0, 0.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0]),
            split_chain_ids=np.asarray([10, 10, 12, 12], dtype=np.int64),
            split_edge_orders=np.asarray([0, 1, 0, 2], dtype=np.int64),
            split_event_orders=np.asarray([0, 0, 0, 0], dtype=np.int64),
            split_x=np.asarray([5.0, 15.0, -0.5, 1.5]),
            split_y=np.asarray([0.0, 0.0, 4.0, 4.0]),
            interval_descriptor_columns={
                "label": np.asarray([1, 2, 3, 4, 5, 6, 7], dtype=np.int64),
            },
        )

    def test_validity_and_group_ids_match_reference(self):
        self._compare_to_reference(
            chain_ids=np.asarray([1, 2, 3], dtype=np.int64),
            chain_point_offsets=np.asarray([0, 2, 4], dtype=np.int64),
            chain_point_counts=np.asarray([2, 2, 2], dtype=np.int64),
            point_x=np.asarray([0.0, 10.0, 20.0, 30.0, 40.0, 50.0]),
            point_y=np.asarray([0.0, 0.0, 1.0, 1.0, 2.0, 2.0]),
            split_chain_ids=np.asarray([1, 3], dtype=np.int64),
            split_edge_orders=np.asarray([0, 0], dtype=np.int64),
            split_event_orders=np.asarray([0, 0], dtype=np.int64),
            split_x=np.asarray([5.0, 45.0]),
            split_y=np.asarray([0.0, 2.0]),
            interval_descriptor_columns={
                "code": np.asarray([7, 8, 9, 10, 11], dtype=np.int64),
            },
            interval_validity=np.asarray([1, 0, 1, 1, 1], dtype=np.int8),
            output_group_ids=np.asarray([101, 102, 201, 301, 302], dtype=np.int64),
        )

    def test_rejects_split_event_outside_chain_edge_range(self):
        with self.assertRaisesRegex(ValueError, "outside chain"):
            spike.assemble_compiled_path_split_records(
                chain_ids=np.asarray([10], dtype=np.int64),
                chain_point_offsets=np.asarray([0], dtype=np.int64),
                chain_point_counts=np.asarray([2], dtype=np.int64),
                point_x=np.asarray([0.0, 1.0]),
                point_y=np.asarray([0.0, 0.0]),
                split_chain_ids=np.asarray([10], dtype=np.int64),
                split_edge_orders=np.asarray([1], dtype=np.int64),
                split_event_orders=np.asarray([0], dtype=np.int64),
                split_x=np.asarray([0.5]),
                split_y=np.asarray([0.0]),
            )

    def test_rejects_split_event_on_single_point_chain(self):
        with self.assertRaisesRegex(ValueError, "at least two points"):
            spike.assemble_compiled_path_split_records(
                chain_ids=np.asarray([10], dtype=np.int64),
                chain_point_offsets=np.asarray([0], dtype=np.int64),
                chain_point_counts=np.asarray([1], dtype=np.int64),
                point_x=np.asarray([0.0]),
                point_y=np.asarray([0.0]),
                split_chain_ids=np.asarray([10], dtype=np.int64),
                split_edge_orders=np.asarray([0], dtype=np.int64),
                split_event_orders=np.asarray([0], dtype=np.int64),
                split_x=np.asarray([0.5]),
                split_y=np.asarray([0.0]),
            )


if __name__ == "__main__":
    unittest.main()
