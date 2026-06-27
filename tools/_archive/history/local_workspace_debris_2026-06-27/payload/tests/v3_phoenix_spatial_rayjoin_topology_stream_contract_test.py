import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rtdsl.v3_0_topology_stream_accounting import (
    TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT,
    TOPOLOGY_STREAM_PHASE_ACCOUNTING_CONTRACT,
    TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT,
    build_topology_stream_m3_phase_table,
    build_topology_stream_phase_accounting,
    build_topology_stream_prepared_handle_metadata,
    compare_author_timer_to_topology_stream,
    compare_topology_stream_accounting,
)
from scripts import v3_phoenix_spatial_rayjoin_topology_stream_contract as contract


SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_rayjoin_topology_stream_contract.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixSpatialRayJoinTopologyStreamContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_is_contract_candidate_not_m7(self):
        payload = self.payload
        self.assertEqual(payload["status"], "spatial_rayjoin_topology_stream_contract_candidate_not_m7")
        self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
        self.assertEqual(payload["phase_accounting_contract"], TOPOLOGY_STREAM_PHASE_ACCOUNTING_CONTRACT)
        self.assertEqual(payload["m3_phase_table_contract"], TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT)
        self.assertEqual(payload["prepared_handle_contract"], TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT)
        self.assertEqual(
            payload["prepared_handle_interface_status"],
            "local_payload_interface_added_not_pod_performance_closed",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_pip_accounting_exposes_overhead_and_author_gap(self):
        pip = self.payload["pip_point_location"]
        self.assertEqual(pip["query_points"], 100000)
        self.assertEqual(pip["exact_mismatch_count"], 0)
        self.assertAlmostEqual(
            pip["rtdl_optix_vs_embree"]["candidate_over_baseline_wall_speedup"],
            1.91993187575488,
        )
        self.assertAlmostEqual(
            pip["optix_accounting"]["visible_non_traversal_overhead_fraction_of_wall"],
            0.3259454850010501,
        )
        self.assertGreater(
            pip["optix_accounting"]["visible_non_traversal_overhead_fraction_of_wall"],
            0.25,
        )
        self.assertAlmostEqual(
            pip["author_gap"]["author_speedup_vs_rtdl_wall"],
            5.72759569862135,
        )
        self.assertFalse(pip["author_gap"]["rtdl_beats_author_claim_authorized"])
        self.assertFalse(pip["author_gap"]["paper_reproduction_claim_authorized"])
        self.assertFalse(pip["optix_accounting"]["full_m3_phase_table_complete"])
        self.assertIn(
            "topology_continuation_sec",
            pip["optix_accounting"]["missing_m3_phases_for_public_row"],
        )

    def test_overlay_accounting_stays_active_count_only(self):
        overlay = self.payload["overlay_active_count"]
        self.assertEqual(overlay["contract"], "overlay_active_pair_dependency_count")
        self.assertEqual(overlay["active_count"], 174)
        self.assertAlmostEqual(
            overlay["rtdl_optix_vs_embree"]["candidate_over_baseline_wall_speedup"],
            499.11182637483904,
        )
        self.assertIn("not full polygon overlay", overlay["reading"])
        for row in (overlay["optix_accounting"], overlay["embree_accounting"]):
            self.assertFalse(row["m7_promotion_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])

    def test_markdown_records_future_requirements_and_forbidden_shortcuts(self):
        for phrase in (
            "M7 rows added by this packet: 0",
            "RTDL OptiX visible non-traversal overhead fraction",
            "RayJoin author / RTDL OptiX wall speedup",
            "full M3 phase table",
            "topology_stream_m3_phase_table_v1",
            "topology_stream_prepared_handle_v1",
            "not POD performance closure",
            "Do not invert the 5.728x",
            "Do not publish the 499x overlay active-count row as full polygon overlay.",
            "Was I foolish?",
            "No. This exposes the RTDL overhead",
        ):
            self.assertIn(phrase, self.text)

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.payload)
            self.assertIn("Spatial RayJoin Topology-Stream Contract", md_out.read_text(encoding="utf-8"))

    def test_generic_accounting_helper_never_authorizes_public_claims(self):
        embree = build_topology_stream_phase_accounting(
            backend="embree",
            output_contract="toy_topology_count",
            query_count=10,
            wall_sec=0.010,
            native_traversal_sec=0.009,
            repeat=5,
            warmup=1,
            timer_basis="test",
        )
        optix = build_topology_stream_phase_accounting(
            backend="optix",
            output_contract="toy_topology_count",
            query_count=10,
            wall_sec=0.005,
            native_traversal_sec=0.003,
            repeat=5,
            warmup=1,
            timer_basis="test",
        )
        comparison = compare_topology_stream_accounting(baseline=embree, candidate=optix)
        author = compare_author_timer_to_topology_stream(
            author_label="author",
            author_query_sec=0.001,
            rtdl_accounting=optix,
            author_timer_basis="author timer",
        )
        self.assertEqual(comparison["candidate_over_baseline_wall_speedup"], 2.0)
        self.assertFalse(comparison["public_speedup_claim_authorized"])
        self.assertFalse(author["rtdl_beats_author_claim_authorized"])
        self.assertTrue(author["mixed_timing_basis"])

    def test_generic_m3_phase_table_and_prepared_handle_are_non_authorizing(self):
        table = build_topology_stream_m3_phase_table(
            phases_sec={
                "static_shape_pack_sec": 0.001,
                "prepare_static_scene_sec": 0.002,
                "query_pack_sec": 0.003,
                "prepare_query_points_sec": 0.004,
                "prepared_query_sec": 0.010,
            },
            native_phase_timings={
                "point_upload": 0.0,
                "candidate_count_pass": 0.005,
                "candidate_write_pass": 0.001,
                "candidate_download": 0.0002,
                "exact_refine": 0.0003,
            },
            output_contract="point_to_shape_positive_hit_count_exact_prepared_points",
            query_count=100,
            repeat=5,
            warmup=1,
            query_stream_resident=True,
            table_basis="unit test explicit phases",
        )
        handle = build_topology_stream_prepared_handle_metadata(
            backend="OptiX",
            generic_capability="point_location_topology_stream",
            output_contract="point_to_shape_positive_hit_count_exact_prepared_points",
            query_count=100,
            static_scene_prepared=True,
            query_stream_prepared=True,
            query_stream_residency="device_resident_prepared_point_probe_columns",
            m3_phase_table=table,
        )

        self.assertEqual(table["contract"], TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT)
        self.assertTrue(table["full_m3_phase_table_complete"])
        self.assertEqual(table["missing_m3_phases_for_public_row"], ())
        self.assertAlmostEqual(table["phase_seconds"]["static_scene_prepare_sec"], 0.003)
        self.assertAlmostEqual(table["phase_seconds"]["query_stream_prepare_sec"], 0.007)
        self.assertAlmostEqual(table["phase_seconds"]["rt_traversal_sec"], 0.005)
        self.assertAlmostEqual(table["phase_seconds"]["topology_continuation_sec"], 0.0013)
        self.assertFalse(table["public_speedup_claim_authorized"])
        self.assertFalse(table["m7_promotion_authorized"])
        self.assertFalse(table["true_zero_copy_claim_authorized"])

        self.assertEqual(handle["contract"], TOPOLOGY_STREAM_PREPARED_HANDLE_CONTRACT)
        self.assertEqual(handle["backend"], "optix")
        self.assertEqual(handle["generic_capability"], "point_location_topology_stream")
        self.assertTrue(handle["reusable_engine_surface"])
        self.assertFalse(handle["app_specific_native_engine_logic_allowed"])
        self.assertFalse(handle["release_authorized"])
        self.assertFalse(handle["v4_embedding_claim_authorized"])

    def test_exact_prepared_points_executor_m3_counts_candidate_write_as_rt_traversal(self):
        table = build_topology_stream_m3_phase_table(
            phases_sec={
                "static_shape_pack_sec": 0.001,
                "prepare_static_scene_sec": 0.002,
                "query_pack_sec": 0.003,
                "prepare_query_points_sec": 0.004,
                "prepare_exact_scalar_count_executor_sec": 0.005,
                "prepared_query_sec": 0.010,
            },
            native_phase_timings={
                "mode": "prepared_points_exact_count_executor_run",
                "point_upload": 0.0,
                "candidate_count_pass": 0.0,
                "candidate_write_pass": 0.006,
                "candidate_download": 0.0002,
                "exact_refine": 0.0003,
            },
            output_contract="point_to_shape_positive_hit_count_exact_prepared_points_executor",
            query_count=100,
            repeat=5,
            warmup=1,
            query_stream_resident=True,
            table_basis="unit test exact prepared-points executor phases",
        )

        self.assertTrue(table["full_m3_phase_table_complete"])
        self.assertAlmostEqual(table["phase_seconds"]["query_stream_prepare_sec"], 0.012)
        self.assertAlmostEqual(table["phase_seconds"]["rt_traversal_sec"], 0.006)
        self.assertAlmostEqual(table["phase_seconds"]["topology_continuation_sec"], 0.0003)
        self.assertAlmostEqual(
            table["phase_seconds"]["host_return_or_scalar_materialization_sec"],
            0.0002,
        )
        self.assertFalse(table["m7_promotion_authorized"])

    def test_relation_status_corrected_executor_prepare_counts_as_query_stream_prepare(self):
        table = build_topology_stream_m3_phase_table(
            phases_sec={
                "static_shape_pack_sec": 0.001,
                "prepare_static_scene_sec": 0.002,
                "query_pack_sec": 0.003,
                "prepare_query_points_sec": 0.004,
                "prepare_relation_status_corrected_scalar_count_executor_sec": 0.005,
                "prepared_query_sec": 0.010,
            },
            native_phase_timings={
                "mode": "relation_status_corrected_scalar_count_executor_run",
                "point_upload": 0.0,
                "candidate_count_pass": 0.006,
                "candidate_write_pass": 0.0,
                "candidate_download": 0.0,
                "exact_refine": 0.0,
            },
            output_contract="point_to_shape_positive_hit_count_relation_status_corrected_executor_validated",
            query_count=100,
            repeat=5,
            warmup=1,
            query_stream_resident=True,
            table_basis="unit test relation-status corrected executor phases",
        )

        self.assertTrue(table["full_m3_phase_table_complete"])
        self.assertAlmostEqual(table["phase_seconds"]["query_stream_prepare_sec"], 0.012)
        self.assertAlmostEqual(table["phase_seconds"]["rt_traversal_sec"], 0.006)
        self.assertEqual(table["phase_seconds"]["topology_continuation_sec"], 0.0)
        self.assertEqual(table["phase_seconds"]["host_return_or_scalar_materialization_sec"], 0.0)
        self.assertFalse(table["public_speedup_claim_authorized"])

    def test_shape_pair_active_count_executor_prepare_counts_as_query_stream_prepare(self):
        table = build_topology_stream_m3_phase_table(
            phases_sec={
                "prepare_static_scene_sec": 0.010,
                "left_shape_pack_sec": 0.002,
                "prepared_left_set_sec": 0.003,
                "prepare_active_count_executor_sec": 0.004,
                "prepared_query_sec": 0.020,
            },
            native_phase_timings={
                "mode": "shape_pair_active_count_prepared_left_executor_run",
                "candidate_count_pass": 0.006,
                "containment": 0.007,
                "active_scan": 0.008,
                "count_download": 0.0001,
            },
            output_contract="overlay_active_pair_dependency_count",
            query_count=1_000_000,
            repeat=25,
            warmup=3,
            query_stream_resident=True,
            table_basis="unit test shape-pair active-count executor phases",
        )

        self.assertTrue(table["full_m3_phase_table_complete"])
        self.assertEqual(table["missing_m3_phases_for_public_row"], ())
        self.assertAlmostEqual(table["phase_seconds"]["static_scene_prepare_sec"], 0.010)
        self.assertAlmostEqual(table["phase_seconds"]["query_stream_prepare_sec"], 0.009)
        self.assertEqual(table["phase_seconds"]["device_transfer_or_residency_sec"], 0.0)
        self.assertAlmostEqual(table["phase_seconds"]["rt_traversal_sec"], 0.006)
        self.assertAlmostEqual(table["phase_seconds"]["topology_continuation_sec"], 0.015)
        self.assertAlmostEqual(
            table["phase_seconds"]["host_return_or_scalar_materialization_sec"],
            0.0001,
        )
        self.assertFalse(table["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(table["m7_promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
