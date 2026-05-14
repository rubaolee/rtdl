from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2000_optix_candidate_witness_exact_filter_pod_audit_2026-05-14.md"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
PERF = ROOT / "scripts" / "goal1856_segment_polygon_v2_partner_perf.py"
ARTIFACT_256 = ROOT / "docs" / "reports" / "goal2000_pod_smoke" / "goal1856_segment_polygon_count256_exact_filter.json"
ARTIFACT_2048 = ROOT / "docs" / "reports" / "goal2000_pod_smoke" / "goal1856_segment_polygon_count2048_exact_filter.json"
ARTIFACT_8192 = ROOT / "docs" / "reports" / "goal2000_pod_smoke" / "goal1856_segment_polygon_count8192_cupy_exact_filter.json"


class Goal2000OptixCandidateWitnessExactFilterPodAuditTest(unittest.TestCase):
    def test_report_records_candidate_contract_and_release_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: pass-with-boundary", report)
        self.assertIn("NVIDIA RTX A5000", report)
        self.assertIn("generic_ray_primitive_candidate_witness_pairs", report)
        self.assertIn("host_segment_triangle_filter_from_generic_witness_candidates", report)
        self.assertIn("native_exact_row_semantics_authorized: false", report)
        self.assertIn("app_exact_row_semantics_authorized: true", report)
        self.assertIn("whole_app_true_zero_copy_authorized: false", report)
        self.assertIn("count-256 and count-2048 rows are negative evidence", report)
        self.assertIn("v2.0 release authorization", report)
        self.assertIn("CuPy\nRawKernel exact segment/triangle candidate filter", report)

    def test_runtime_fails_closed_on_float64_all_witness_rays(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        perf = PERF.read_text(encoding="utf-8")

        self.assertIn("bounded all-witness ray column", runtime)
        self.assertIn("must use dtype float32", runtime)
        self.assertIn('"ox": runtime["tensor"]([segment.x0 for segment in segments], runtime["float32"])', perf)
        self.assertIn('"tmax": runtime["tensor"]([1.0 for _ in segments], runtime["float32"])', perf)
        self.assertNotIn('"ox": runtime["tensor"]([segment.x0 for segment in segments], runtime["float64"])', perf)

    def test_adapter_filters_generic_candidates_before_exact_app_rows(self) -> None:
        adapter = ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("_exact_segment_triangle_rows_from_witness_columns", adapter)
        self.assertIn("_finite_ray_hits_triangle", adapter)
        self.assertIn('"native_engine_row_contract": "generic_ray_primitive_candidate_witness_pairs"', adapter)
        self.assertIn('"app_exact_filter": "host_segment_triangle_filter_from_generic_witness_candidates"', adapter)
        self.assertIn('"native_exact_row_semantics_authorized": False', adapter)
        self.assertIn('"app_exact_row_semantics_authorized": True', adapter)
        self.assertIn('"whole_app_true_zero_copy_authorized": False', adapter)
        self.assertIn('"partner_columns_from_host_exact_filter"', adapter)

    def test_pod_artifacts_preserve_strict_parity_and_boundaries(self) -> None:
        for path, expected_count in (
            (ARTIFACT_256, 256),
            (ARTIFACT_2048, 2048),
            (ARTIFACT_8192, 8192),
        ):
            with self.subTest(path=path.name):
                artifact = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(artifact["status"], "pass")
                self.assertIn("NVIDIA RTX A5000", artifact["gpu"])
                self.assertEqual(artifact["parity"]["expected_row_count"], expected_count)
                self.assertTrue(artifact["parity"]["strict_rows_match"])
                self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])
                self.assertFalse(artifact["claim_boundary"]["whole_app_true_zero_copy_authorized"])
                self.assertFalse(artifact["claim_boundary"]["whole_app_speedup_claim_authorized"])
                self.assertFalse(artifact["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

        count8192 = json.loads(ARTIFACT_8192.read_text(encoding="utf-8"))
        cupy = count8192["partners"]["cupy"]
        self.assertEqual(cupy["row_count"], 8192)
        self.assertLess(cupy["query_median_ratio_vs_v1_8_native"], 1.0)
        self.assertEqual(cupy["overflow_check"]["status"], "pass")

        count2048 = json.loads(ARTIFACT_2048.read_text(encoding="utf-8"))
        self.assertGreater(count2048["partners"]["cupy"]["query_median_ratio_vs_v1_8_native"], 1.0)


if __name__ == "__main__":
    unittest.main()
