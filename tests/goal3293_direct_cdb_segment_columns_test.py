from __future__ import annotations

import inspect
from pathlib import Path
import unittest

import numpy as np
import rtdsl as rt
from examples.v2_0.research_benchmarks.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)
from rtdsl import embree_runtime


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
REPORT = ROOT / "docs" / "reports" / "goal3293_direct_cdb_segment_columns_2026-06-04.md"


def _packed_ids(packed) -> list[int]:
    return [int(packed.records[index].id) for index in range(int(packed.count))]


class Goal3293DirectCdbSegmentColumnsTest(unittest.TestCase):
    def test_cdb_chain_segment_columns_match_record_conversion(self) -> None:
        dataset = rt.load_cdb(ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb")
        records = rt.chains_to_segments(dataset)
        columns = rt.chains_to_segment_columns(dataset)

        self.assertIsInstance(columns, rt.SegmentColumns2D)
        self.assertIs(columns.owner, dataset)
        self.assertEqual(columns.count, len(records))
        self.assertEqual(int(columns.ids[0]), int(records[0]["id"]))
        self.assertEqual(int(columns.ids[-1]), int(records[-1]["id"]))
        self.assertAlmostEqual(float(columns.x0[0]), float(records[0]["x0"]))
        self.assertAlmostEqual(float(columns.y0[-1]), float(records[-1]["y0"]))
        self.assertAlmostEqual(float(columns.x1[-1]), float(records[-1]["x1"]))
        self.assertAlmostEqual(float(columns.y1[-1]), float(records[-1]["y1"]))

    def test_direct_cdb_columns_pack_to_same_native_ids_as_records(self) -> None:
        dataset = rt.load_cdb(ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb")
        records = rt.chains_to_segments(dataset)
        columns = rt.chains_to_segment_columns(dataset)

        packed_records = embree_runtime.pack_segments(records=records)
        packed_columns = embree_runtime.pack_segments(records=columns)

        self.assertEqual(packed_records.count, packed_columns.count)
        self.assertEqual(_packed_ids(packed_records), _packed_ids(packed_columns))
        self.assertIsNotNone(packed_columns.owner)
        self.assertEqual(packed_columns.owner.dtype.itemsize, embree_runtime._rtdl_segment_numpy_dtype(np).itemsize)

    def test_external_lsi_loader_can_choose_direct_columns_for_prepared_routes(self) -> None:
        left = ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb"
        right = ROOT / "tests" / "fixtures" / "rayjoin" / "br_soil_subset.cdb"
        dataset = f"{left} + {right}"

        record_case = rayjoin_app._load_rayjoin_case("lsi", dataset)
        column_case = rayjoin_app._load_rayjoin_case("lsi", dataset, segment_column_inputs=True)

        self.assertNotIsInstance(record_case.inputs["left"], rt.SegmentColumns2D)
        self.assertIsInstance(column_case.inputs["left"], rt.SegmentColumns2D)
        self.assertIsInstance(column_case.inputs["right"], rt.SegmentColumns2D)
        self.assertEqual(column_case.inputs["left"].count, len(record_case.inputs["left"]))
        self.assertIn("direct generic segment columns", column_case.note)

    def test_prepared_count_route_is_column_aware_without_app_native_symbols(self) -> None:
        source = inspect.getsource(rayjoin_app)

        self.assertIn("chains_to_segment_columns", source)
        self.assertIn('segment_column_inputs=workload == "lsi"', source)
        self.assertIn("def _reusable_segment_input", source)
        self.assertIn("self._right_segment_count", source)
        self.assertNotIn("rtdl_optix_run_rayjoin", source)

    def test_report_records_local_scope_and_pod_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("direct CDB-to-segment-column path", text)
        self.assertIn("CPU reference route still uses ordinary segment records", text)
        self.assertIn("No native ABI changed", text)
        self.assertIn("Pod timing is still required", text)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized: false", text)


if __name__ == "__main__":
    unittest.main()
