import unittest

from scripts.goal1204_repaired_rtx_pod_packet import ROWS, build_packet


class Goal1204RepairedRtxPodPacketTest(unittest.TestCase):
    def test_rows_batch_repaired_paths_for_single_pod_session(self):
        labels = {row["label"] for row in ROWS}
        self.assertIn("db_embree_100000_chunked_repair", labels)
        self.assertIn("db_optix_100000_chunked_repair", labels)
        self.assertIn("db_embree_300000_chunked_repair", labels)
        self.assertIn("db_optix_300000_chunked_repair", labels)
        self.assertIn("jaccard_optix_8192_public_safe_chunk_1024", labels)
        self.assertIn("jaccard_optix_8192_diagnostic_chunk_64", labels)
        self.assertIn("road_hazard_embree_control_40000", labels)
        self.assertIn("road_hazard_optix_control_40000", labels)

    def test_public_safe_jaccard_row_uses_reviewed_chunk_policy(self):
        row = next(row for row in ROWS if row["label"] == "jaccard_optix_8192_public_safe_chunk_1024")
        self.assertIn("--chunk-copies 1024", row["command"])
        self.assertIn("--validation-mode analytic_summary", row["command"])

    def test_diagnostic_jaccard_row_is_not_named_claim_ready(self):
        row = next(row for row in ROWS if row["label"] == "jaccard_optix_8192_diagnostic_chunk_64")
        self.assertIn("diagnostic", row["label"])
        self.assertIn("--chunk-copies 64", row["command"])
        self.assertIn("diagnostic-only", row["purpose"])

    def test_packet_boundary_blocks_public_wording(self):
        payload = build_packet()
        self.assertTrue(payload["valid"])
        self.assertIn("does not run cloud", payload["boundary"])
        self.assertIn("public RTX speedup wording", payload["boundary"])
        self.assertIn("database_analytics chunked compact-summary", payload["pod_batch"]["target_repairs"])
        self.assertIn("polygon_set_jaccard public-safe chunk policy", payload["pod_batch"]["target_repairs"])
        self.assertIn("road_hazard_screening floor-safe scale", payload["pod_batch"]["target_repairs"])


if __name__ == "__main__":
    unittest.main()
