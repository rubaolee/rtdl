from __future__ import annotations

import py_compile
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.prepared_execution import audit_prepared_execution_continuation_metadata
from rtdsl.prepared_execution import audit_prepared_execution_session_metadata
from rtdsl.prepared_execution import run_segment_intersection_topology_stream_prepared_session
from rtdsl.prepared_session_residency import ExplicitPreparedSessionCache

APP = ROOT / "examples" / "current" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"


class V3PhoenixSpatialSegmentIntersectionRunnerWiringTest(unittest.TestCase):
    def test_runtime_helper_is_generic_not_rayjoin_named(self) -> None:
        source = PREPARED_EXECUTION.read_text(encoding="utf-8")

        self.assertIn("def run_segment_intersection_topology_stream_prepared_session", source)
        self.assertIn('primitive="segment_intersection_topology_stream"', source)
        self.assertIn('"segment_intersection_topology_stream_prepared_session"', source)
        helper_start = source.index("def run_segment_intersection_topology_stream_prepared_session")
        helper_end = source.index("def run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session", helper_start)
        helper_body = source[helper_start:helper_end]
        self.assertNotIn("rayjoin", helper_body.lower())
        self.assertIn("external_device_buffer_interop_authorized", helper_body)
        self.assertIn("focused_material_gain_required_before_all_app", helper_body)
        self.assertIn("full_all_app_rerun_authorized_by_this_packet", helper_body)
        self.assertIn('"run_segment_intersection_topology_stream_prepared_session"', source)

    def test_app_wires_lsi_to_productized_segment_intersection_runner(self) -> None:
        source = APP.read_text(encoding="utf-8")

        for phrase in (
            "class PreparedExecutionRayJoinSegmentIntersectionTopologyStream",
            "def run_rayjoin_prepared_execution_segment_intersection_topology_stream_workload",
            "run_segment_intersection_topology_stream_prepared_session",
            "measured_run_prepared=lambda prepared: prepared.run_hot()",
            "finalize_output=lambda prepared, output: prepared.finalize_run(output)",
            "prepared_execution_segment_intersection_topology_stream",
            "prepared_execution_runner_segment_intersection_topology_stream",
            'generic_capability="segment_intersection_topology_stream"',
            '"productized_execution_path"',
            '"prepared_execution_session_runner"',
            '"runtime_trunk_executes_end_to_end"',
            "left_id_count_prepared_left_device_columns",
            "device_resident_prepared_left_segment_set_dense_left_id_count",
            "segment_segment_intersection_count_by_left_id_dense_device_column",
        ):
            self.assertIn(phrase, source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn('"broad_v3_faster_than_v2_claim_authorized": False', source)
        self.assertIn('"true_zero_copy_claim_authorized": False', source)
        self.assertIn('"v4_embedding_or_external_zero_copy_authorized": False', source)
        self.assertIn('"full_all_app_rerun_authorized_by_this_packet"] = False', source)
        self.assertNotIn('"public_speedup_claim_authorized": True', source)
        self.assertNotIn('"rtdl_beats_rayjoin_claim_authorized": True', source)
        self.assertNotIn('"true_zero_copy_claim_authorized": True', source)

    def test_generic_runner_metadata_with_fake_segment_stream(self) -> None:
        class FakePrepared:
            pass

        def prepare_session() -> FakePrepared:
            return FakePrepared()

        def run_topology_stream(_prepared: FakePrepared) -> dict[str, object]:
            return {
                "metadata": {
                    "internal_device_residency_between_rtdl_phases": True,
                    "hot_path_host_materialization": False,
                },
                "topology_stream_prepared_handle": {
                    "contract": "topology_stream_prepared_handle_v1",
                    "query_stream_prepared": True,
                    "query_stream_residency": "device_resident_fake_segment_stream",
                },
                "topology_stream_m3_phase_table": {
                    "contract": "topology_stream_m3_phase_table_v1",
                },
                "phases_sec": {
                    "static_segment_pack_sec": 0.001,
                    "prepare_static_scene_sec": 0.002,
                    "prepare_left_set_sec": 0.003,
                    "prepared_left_set_sec": 0.004,
                    "prepared_query_sec": 0.010,
                },
                "native_phase_timings": {
                    "left_upload": 0.0,
                    "traversal": 0.004,
                    "active_scan": 0.001,
                    "count_download": 0.0,
                    "row_download": 0.0,
                },
                "summary": {
                    "output_contract": "fake_segment_count",
                },
            }

        result = run_segment_intersection_topology_stream_prepared_session(
            query_stream_fingerprint={"left": "fake"},
            static_scene_fingerprint={"right": "fake"},
            output_contract="fake_segment_count",
            query_count=4,
            right_segment_count=3,
            backend="optix",
            partner="none",
            cache=ExplicitPreparedSessionCache(max_entries=1),
            prepare_session=prepare_session,
            run_topology_stream=run_topology_stream,
            measured_run_prepared=run_topology_stream,
            finalize_output=lambda _prepared, output: {
                **output,
                "finalized_once": True,
            },
            measured_repeat_count=2,
            warmup_count=1,
            validate_output=lambda output: {
                "contract_seen": output["summary"]["output_contract"] == "fake_segment_count"
            },
        )

        metadata = result.to_metadata()
        audit = result.runtime_audit()
        continuation_audit = audit_prepared_execution_continuation_metadata(metadata)
        self.assertEqual(metadata["primitive_family"], "segment_intersection_topology_stream")
        self.assertEqual(metadata["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(metadata["runtime_trunk_family"], "segment_intersection_topology_stream_left_id_dense_count")
        self.assertTrue(metadata["measured_run_prepared_override_used"])
        self.assertTrue(metadata["measured_output_finalized_once"])
        self.assertTrue(metadata["per_repeat_output_finalization_avoided"])
        self.assertGreaterEqual(metadata["output_finalize_sec"], 0.0)
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertEqual(
            metadata["prepared_execution_to_topology_stream_m3_bridge_contract"],
            "prepared_execution_to_topology_stream_m3_bridge_v1",
        )
        self.assertEqual(
            metadata["prepared_execution_to_topology_stream_m3_bridge_status"],
            "complete_non_authorizing_m3_bridge",
        )
        self.assertTrue(metadata["topology_stream_m3_phase_table_complete"])
        self.assertEqual(metadata["topology_stream_m3_missing_phases_for_public_row"], ())
        self.assertAlmostEqual(
            metadata["topology_stream_m3_phase_seconds"]["static_scene_prepare_sec"],
            0.003,
        )
        self.assertAlmostEqual(
            metadata["topology_stream_m3_phase_seconds"]["query_stream_prepare_sec"],
            0.007,
        )
        self.assertAlmostEqual(metadata["topology_stream_m3_phase_seconds"]["rt_traversal_sec"], 0.004)
        self.assertAlmostEqual(metadata["topology_stream_m3_phase_seconds"]["topology_continuation_sec"], 0.001)
        self.assertEqual(
            metadata["topology_stream_prepared_handle"]["generic_capability"],
            "segment_intersection_topology_stream",
        )
        self.assertFalse(metadata["topology_stream_m3_bridge_public_row_authorized"])
        self.assertFalse(metadata["topology_stream_m3_bridge_m7_promotion_authorized"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertIs(metadata["true_zero_copy_claim_authorized"], False)
        self.assertFalse(metadata["full_all_app_rerun_authorized_by_this_packet"])
        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["step3_residency_default_ready"])
        self.assertTrue(audit["topology_stream_set_a_candidate"])
        self.assertTrue(audit["topology_stream_m3_bridge_contract_ok"])
        self.assertTrue(audit["topology_stream_m3_bridge_complete"])
        self.assertTrue(audit["topology_stream_m3_bridge_non_authorizing"])
        self.assertTrue(audit["topology_stream_m3_bridge_ready"])
        self.assertEqual(continuation_audit["status"], "accept_step4_continuation_core_ready")
        self.assertTrue(continuation_audit["step4_continuation_core_ready"])
        self.assertEqual(continuation_audit["continuation_contract"], "fake_segment_count")
        self.assertTrue(continuation_audit["set_a_probe_candidate"])
        self.assertFalse(continuation_audit["set_b_control_candidate"])
        self.assertEqual(continuation_audit["missing_step4_fields"], ())

        negative_cases = (
            (
                "partial_phase_table",
                {
                    "topology_stream_m3_phase_table_complete": False,
                    "topology_stream_m3_missing_phases_for_public_row": (
                        "topology_continuation_sec",
                    ),
                },
                {
                    "topology_stream_m3_bridge_contract_ok": True,
                    "topology_stream_m3_bridge_complete": False,
                    "topology_stream_m3_bridge_non_authorizing": True,
                },
            ),
            (
                "bad_bridge_contract",
                {
                    "prepared_execution_to_topology_stream_m3_bridge_contract": "bad_contract",
                },
                {
                    "topology_stream_m3_bridge_contract_ok": False,
                    "topology_stream_m3_bridge_complete": True,
                    "topology_stream_m3_bridge_non_authorizing": True,
                },
            ),
            (
                "bad_bridge_status",
                {
                    "prepared_execution_to_topology_stream_m3_bridge_status": (
                        "partial_non_authorizing_m3_bridge"
                    ),
                },
                {
                    "topology_stream_m3_bridge_contract_ok": True,
                    "topology_stream_m3_bridge_complete": False,
                    "topology_stream_m3_bridge_non_authorizing": True,
                },
            ),
            (
                "bridge_public_row_authorized",
                {
                    "topology_stream_m3_bridge_public_row_authorized": True,
                },
                {
                    "topology_stream_m3_bridge_contract_ok": True,
                    "topology_stream_m3_bridge_complete": True,
                    "topology_stream_m3_bridge_non_authorizing": False,
                },
            ),
            (
                "bridge_m7_authorized",
                {
                    "topology_stream_m3_bridge_m7_promotion_authorized": True,
                },
                {
                    "topology_stream_m3_bridge_contract_ok": True,
                    "topology_stream_m3_bridge_complete": True,
                    "topology_stream_m3_bridge_non_authorizing": False,
                },
            ),
        )
        for label, changes, expected_audit_fields in negative_cases:
            with self.subTest(label=label):
                broken_metadata = dict(metadata)
                broken_metadata.update(changes)
                broken_audit = audit_prepared_execution_session_metadata(broken_metadata)
                for field, expected_value in expected_audit_fields.items():
                    self.assertIs(broken_audit[field], expected_value)
                self.assertEqual(broken_audit["status"], "incomplete_step3_audit")
                self.assertFalse(broken_audit["topology_stream_m3_bridge_ready"])
                self.assertIn(
                    "complete_non_authorizing_topology_stream_m3_bridge",
                    broken_audit["missing_step3_fields"],
                )

    def test_modified_python_files_compile(self) -> None:
        py_compile.compile(str(APP), doraise=True)
        py_compile.compile(str(PREPARED_EXECUTION), doraise=True)


if __name__ == "__main__":
    unittest.main()
