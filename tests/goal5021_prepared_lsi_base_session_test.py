import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal5021PreparedLsiBaseSessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")

    def test_cli_exposes_prepared_lsi_base_session(self):
        self.assertIn('"--prepared-lsi-base-session"', self.source)
        self.assertIn("prepare only the LSI base/right planar-map session once", self.source)
        self.assertIn("prepared_lsi_base_session", self.source)

    def test_prepared_base_builds_fresh_query_per_route(self):
        self.assertIn("def produce_lsi_bounded_exact_device_columns_from_prepared_base", self.source)
        helper = self.source[
            self.source.index("def produce_lsi_bounded_exact_device_columns_from_prepared_base") :
            self.source.index("def produce_lsi_bounded_exact_device_columns_from_prepared_query")
        ]
        self.assertIn("with lsi.prepare_query(left.lsi_segments) as query", helper)
        self.assertIn("produce_lsi_bounded_exact_device_columns_from_prepared_query", helper)
        self.assertNotIn("prepared_lsi_query", helper)

    def test_repeat_protocol_keeps_base_session_distinct_from_full_session(self):
        self.assertIn("--prepared-operator-session and --prepared-lsi-base-session are mutually exclusive", self.source)
        self.assertIn('setattr(args, "_prepared_lsi_session", lsi)', self.source)
        self.assertIn('setattr(args, "_prepared_lsi_base_session_active", True)', self.source)
        self.assertNotIn('setattr(args, "_prepared_lsi_query", query)\n                setattr(args, "_prepared_lsi_base_session_active"', self.source)

    def test_repeat_summary_reports_lsi_extended_timings(self):
        self.assertIn('"lsi_extended_timings": lsi_extended', self.source)
        self.assertIn('"prepared_lsi_base_session_measurement"', self.source)
        self.assertIn('"prepared_lsi_base_session": bool(getattr(args, "prepared_lsi_base_session", False))', self.source)

    def test_query_chain_batches_are_full_dataset_slices(self):
        self.assertIn('"--query-chain-batches"', self.source)
        self.assertIn("def _slice_dataset_by_chain_range", self.source)
        helper = self.source[
            self.source.index("def _slice_dataset_by_chain_range") :
            self.source.index("def _split_dataset_by_chain_batches")
        ]
        self.assertIn("base.DatasetArrays", helper)
        self.assertIn("base.pack_segments", helper)
        self.assertIn("base.pack_cdb_segments_from_arrays", helper)
        self.assertIn("base.pack_points", helper)
        self.assertIn("seg_ids = np.arange(1, edge_count + 1", helper)
        self.assertIn("point_ids = np.arange(1, point_x.size + 1", helper)

    def test_query_chain_batch_mode_reports_batch_metadata(self):
        self.assertIn('"query_batch": summary.get("query_batch")', self.source)
        self.assertIn('"query_chain_batches": query_chain_batches', self.source)
        self.assertIn('"distinct_query_batches": distinct_query_batches', self.source)
        self.assertIn('"query_many_measurement_kind"', self.source)
        self.assertIn('summary["query_batch"] = {', self.source)

    def test_query_batch_right_vertex_points_can_be_prepared_once(self):
        self.assertIn('"--prepared-query-batch-right-vertex-points"', self.source)
        self.assertIn("--prepared-query-batch-right-vertex-points requires", self.source)
        self.assertIn("session_prepare_query_batch_right_vertex_point_locator_sec", self.source)
        self.assertIn("session_prepare_query_batch_right_vertex_points_sec", self.source)
        self.assertIn('setattr(args, "_prepared_vertex_points_map1_in_map0", query_batch_right_vertex_points)', self.source)
        self.assertIn('"_prepared_vertex_points_map1_in_map0"', self.source)
        self.assertIn('"prepared_query_batch_right_vertex_points"', self.source)

    def test_query_batch_segment_arrays_can_be_prepared_once(self):
        self.assertIn('"--prepared-query-batch-segment-arrays"', self.source)
        self.assertIn("--prepared-query-batch-segment-arrays requires", self.source)
        self.assertIn("session_prepare_query_batch_right_segment_device_arrays_sec", self.source)
        self.assertIn("session_prepare_query_batch_", self.source)
        self.assertIn("_left_segment_device_arrays_sec", self.source)
        self.assertIn('setattr(args, "_device_segment_arrays_right", query_batch_right_segment_arrays)', self.source)
        self.assertIn('setattr(\n                                args,\n                                "_device_segment_arrays_left"', self.source)
        self.assertIn('"prepared_query_batch_segment_arrays"', self.source)

    def test_lsi_base_workspace_warmup_is_session_only(self):
        self.assertIn('"--prepared-lsi-base-workspace-warmup"', self.source)
        self.assertIn("--prepared-lsi-base-workspace-warmup requires", self.source)
        self.assertIn("session_prepare_lsi_base_workspace_warmup_sec", self.source)
        self.assertIn("_slice_dataset_by_chain_range(left, start_chain=0, end_chain=1)", self.source)
        self.assertIn("produce_lsi_bounded_exact_device_columns_from_prepared_base", self.source)
        self.assertIn("device_columns.close()", self.source)
        self.assertIn('"prepared_lsi_base_workspace_warmup"', self.source)

    def test_query_batch_device_carrier_arrays_can_be_prepared_once(self):
        self.assertIn("session_prepare_query_batch_right_carrier_device_arrays_sec", self.source)
        self.assertIn("left_carrier_device_arrays_sec", self.source)
        self.assertIn('setattr(args, "_device_carrier_arrays_right", query_batch_right_carrier_arrays)', self.source)
        self.assertIn('"_device_carrier_arrays_left"', self.source)
        self.assertIn('"_device_carrier_arrays_right"', self.source)

    def test_device_carrier_route_can_skip_host_run_tables(self):
        self.assertIn("with_host_run_tables: bool = True", self.source)
        self.assertIn("with_host_run_tables=not device_resident_carrier_enabled", self.source)
        self.assertIn("_host_run_tables_skipped", self.source)


if __name__ == "__main__":
    unittest.main()
