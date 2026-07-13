import importlib.util
import unittest
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


def load_app_module():
    spec = importlib.util.spec_from_file_location("section57_overlay_columnar_binary_goal4990", APP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal4990BinaryRepeatProtocolTest(unittest.TestCase):
    def test_cli_exposes_auditable_repeat_protocol_without_changing_default_route(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"--repeat"', source)
        self.assertIn('"--warmup-runs"', source)
        self.assertIn('"--prepared-operator-session"', source)
        self.assertIn("run_pipeline_repeat_protocol(args)", source)
        self.assertIn("fresh_one_shot_headline", source)
        self.assertIn("warmup_only_headline_authorized", source)
        self.assertIn("_prepared_lsi_session", source)
        self.assertIn("_prepared_point_location_map0_in_map1", source)
        self.assertIn("_prepared_vertex_points_map1_in_map0", source)
        self.assertIn("session_prepare_vertex_points_map1_in_map0_sec", source)
        self.assertIn("_device_segment_arrays_left", source)
        self.assertIn("session_prepare_reprojection_right_segment_device_arrays_sec", source)
        self.assertIn("np.asarray(point_faces[side_id], dtype=np.uint32)", source)
        self.assertIn("np.asarray(midpoint_faces[side_id], dtype=np.uint32)", source)

    def test_repeat_summary_keeps_warmup_visible_and_blocks_fresh_headline(self):
        module = load_app_module()
        args = Namespace(
            pair_name="tiny_pair",
            repeat=2,
            warmup_runs=1,
            device_columnar=True,
            compiled_group=True,
            bounded_exact_lsi_device_columns=True,
            exact_lsi_device_columns=False,
            point_location_device_face_columns=True,
            fast_scaled_point_pack=True,
            prepared_operator_session=True,
        )

        def fake_summary(writer_free, lsi, downstream):
            return {
                "writer_free_hot_sec": writer_free,
                "lsi_row_count": 7,
                "downstream_consumer": {"pair_count": 3},
                "downstream_floor_breakdown": {
                    "lsi_phase_sec": lsi,
                    "downstream_floor_sec": downstream,
                },
                "claim_boundary": {
                    "lsi_pair_input_device_resident": True,
                    "lsi_pair_host_to_device_copy_used": False,
                    "bounded_exact_lsi_numba_direct_handoff_used": True,
                },
                "phase_seconds": {
                    "lsi_bounded_exact_pair_id_device_columns_sec": lsi,
                    "grouped_compiled_columnar_carrier_construction_sec": downstream,
                },
            }

        summary = module.summarize_repeat_protocol(
            args=args,
            warmup_summaries=[fake_summary(1.0, 0.8, 0.2)],
            measured_summaries=[fake_summary(0.4, 0.3, 0.1), fake_summary(0.2, 0.1, 0.1)],
        )
        self.assertEqual(
            summary["schema"],
            "rtdl.paper_reproduction.rayjoin.section57.binary_repeat_protocol.v1",
        )
        self.assertEqual(len(summary["warmup_rows"]), 1)
        self.assertEqual(len(summary["measured_rows"]), 2)
        self.assertAlmostEqual(summary["median_writer_free_hot_sec"], 0.3)
        self.assertTrue(summary["structural_consistency"]["single_lsi_row_count"])
        self.assertTrue(summary["structural_consistency"]["single_descriptor_pair_count"])
        self.assertFalse(summary["claim_boundary"]["fresh_one_shot_headline"])
        self.assertFalse(summary["claim_boundary"]["warmup_only_headline_authorized"])
        self.assertTrue(summary["claim_boundary"]["prepared_operator_body_measurement"])
        self.assertFalse(summary["claim_boundary"]["true_query_many_measurement"])
        self.assertTrue(summary["claim_boundary"]["prepared_operator_session"])
        self.assertTrue(summary["route"]["prepared_operator_session"])


if __name__ == "__main__":
    unittest.main()
