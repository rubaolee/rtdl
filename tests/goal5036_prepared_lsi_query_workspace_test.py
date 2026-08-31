import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal5036PreparedLsiQueryWorkspaceTest(unittest.TestCase):
    def test_cli_flag_and_boundary_metadata_exist(self):
        text = APP.read_text(encoding="utf-8")
        self.assertIn("--prepared-query-batch-lsi-query-workspaces", text)
        self.assertIn("prepared_query_batch_lsi_query_workspaces", text)
        self.assertIn(
            "session_prepares_and_warms_each_distinct_batch_lsi_query_workspace_without_reusing_results",
            text,
        )

    def test_prepares_and_warms_each_batch_query_before_measured_body(self):
        text = APP.read_text(encoding="utf-8")
        self.assertIn("query_batch_lsi_queries = [", text)
        self.assertIn('f"session_prepare_query_batch_{int(batch[\'index\'])}_lsi_query_sec"', text)
        self.assertIn("produce_lsi_bounded_exact_device_columns_from_prepared_query", text)
        self.assertIn('f"session_prepare_query_batch_{batch_index}_lsi_workspace_warmup_sec"', text)
        self.assertIn('setattr(args, "_prepared_lsi_query", query_batch_lsi_queries[int(batch["index"])])', text)

    def test_workspace_route_keeps_results_out_of_hot_body_and_cleans_handles(self):
        text = APP.read_text(encoding="utf-8")
        self.assertIn("Measured ", text)
        self.assertIn("rows still recompute LSI pair-id device columns", text)
        self.assertIn('"_prepared_lsi_query"', text)
        self.assertIn("for prepared_query in query_batch_lsi_queries:", text)
        self.assertIn("prepared_query.close()", text)

    def test_left_vertex_points_can_be_prepared_per_query_batch(self):
        text = APP.read_text(encoding="utf-8")
        self.assertIn("--prepared-query-batch-left-vertex-points", text)
        self.assertIn("query_batch_left_vertex_locator", text)
        self.assertIn("query_batch_left_vertex_points = [", text)
        self.assertIn('f"session_prepare_query_batch_{int(batch[\'index\'])}_left_vertex_points_sec"', text)
        self.assertIn('"_prepared_point_location_map0_in_map1"', text)
        self.assertIn('"_prepared_vertex_points_map0_in_map1"', text)
        self.assertIn("for prepared_points in query_batch_left_vertex_points:", text)

    def test_device_carrier_vertex_pip_does_not_force_host_copy(self):
        text = APP.read_text(encoding="utf-8")
        vertex_block = text.split('point_faces0 = timed(', 1)[1].split('midpoint_faces = (', 1)[0]
        self.assertIn("copy_host=not device_resident_carrier_enabled", vertex_block)
        self.assertNotIn("copy_host=True", vertex_block)


if __name__ == "__main__":
    unittest.main()
