from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3677_relation_status_filtered_exact_count_2026-06-06.md"
ARTIFACT = ROOT / "docs/reports/goal3677_relation_status_exact_count_a5000/summary.json"


class Goal3677RelationStatusFilteredExactCountTest(unittest.TestCase):
    def test_native_relation_status_filtered_symbol_is_generic(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        symbol = (
            "rtdl_optix_prepared_point_closed_shape_membership_relation_status_"
            "candidate_device_columns_prepared_points_2d"
        )
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        for forbidden in ("rayjoin", "county", "cdb"):
            self.assertNotIn(forbidden, symbol.lower())

    def test_relation_status_pipeline_filters_in_anyhit_not_app_layer(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        start = workloads.index("static void ensure_pip_relation_status_candidate_device_columns_pipeline")
        end = workloads.index("static void ensure_pip_point_id_count_device_columns_pipeline", start)
        body = workloads[start:end]
        self.assertIn("relation_status_filter", body)
        self.assertIn("closed-shape relation-status candidate raygen count snippet not found", body)
        self.assertIn("relation_status == params.relation_status_filter", body)
        self.assertIn("point_closed_shape_relation_status_candidate_device_columns_kernel.cu", body)
        self.assertNotIn("rayjoin", body.lower())
        self.assertNotIn("county", body.lower())

    def test_python_front_door_and_composed_numba_count_are_non_authorizing(self) -> None:
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        topology = (ROOT / "src/rtdsl/closed_shape_topology.py").read_text(encoding="utf-8")
        script = (ROOT / "scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("relation_status_candidate_device_columns_prepared_points", runtime)
        self.assertIn("relation_status_filter must be 0(all), 1(interior), or 2(boundary)", runtime)
        self.assertIn("count_relation_status_corrected_prepared_points_numba", topology)
        self.assertIn("produce_boundary_columns(retry)", topology)
        self.assertIn('"public_speedup_claim_authorized": False', script)
        self.assertIn('"true_zero_copy_claim_authorized": False', script)
        self.assertIn('"native_default_route_authorized": False', script)

    def test_report_and_artifact_keep_boundary_and_record_negative_insight(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("Relation-status filtering is not sparse", report)
        self.assertIn("does not authorize", report)
        self.assertTrue(artifact["correctness"]["all_match_exact_count"])
        self.assertEqual(artifact["correctness"]["corrected_count"], artifact["correctness"]["exact_count"])
        self.assertFalse(artifact["goal3677_scoped_source_dirty"])
        self.assertEqual(artifact["timings"]["all_candidate_count_only"]["stability_value"], 47264)
        self.assertEqual(artifact["timings"]["relation_status_corrected_exact_numba_count"]["stability_value"], 47262)
        for value in artifact["claim_boundary"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
