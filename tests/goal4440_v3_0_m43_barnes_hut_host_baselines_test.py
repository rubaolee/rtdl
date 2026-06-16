from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
REPORT = ROOT / "docs/reports/goal4440_v3_0_m43_barnes_hut_host_baselines_2026-06-16.md"
CPU_SMOKE = ROOT / "docs/reports/goal4440_v3_0_m43_barnes_hut_cpu_host_128_smoke_2026-06-16.json"
EMBREE_SMOKE = ROOT / "docs/reports/goal4440_v3_0_m43_barnes_hut_embree_host_128_smoke_2026-06-16.json"
CPU_8192 = ROOT / "docs/reports/goal4440_v3_0_m43_barnes_hut_cpu_host_8192_2026-06-16.json"
EMBREE_8192 = ROOT / "docs/reports/goal4440_v3_0_m43_barnes_hut_embree_host_8192_2026-06-16.json"
OPTIX_NUMBA_8192 = ROOT / "docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_8192_2026-06-16.json"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


class Goal4440V30M43BarnesHutHostBaselinesTest(unittest.TestCase):
    def test_app_exposes_cpu_and_embree_host_baseline_modes(self) -> None:
        from examples.current.research_benchmarks.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        scope = barnes_hut.run_benchmark("scope")
        self.assertIn("aggregate_frontier_weighted_vector_cpu_host", barnes_hut.MODES)
        self.assertIn("aggregate_frontier_weighted_vector_embree_host", barnes_hut.MODES)
        self.assertIn(
            "generic_aggregate_frontier_collect_2d_host_weighted_vector_sum_baseline",
            scope["current_supported_contracts"],
        )

        source = APP.read_text(encoding="utf-8")
        for phrase in (
            "_aggregate_frontier_weighted_vector_host_payload",
            "_host_weighted_vector_sum_from_frontier_rows",
            "same_device_resident_contract",
            "frontier_rows_materialized_on_host",
            "streamed_host_accumulation",
        ):
            self.assertIn(phrase, source)

        with self.assertRaisesRegex(ValueError, "--require-rt-core requires"):
            barnes_hut.run_benchmark(
                "aggregate_frontier_weighted_vector_cpu_host",
                body_count=8,
                require_rt_core=True,
            )

    def test_readme_and_report_document_host_baseline_boundary(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for text in (readme, report):
            self.assertIn("aggregate_frontier_weighted_vector_cpu_host", text)
            self.assertIn("aggregate_frontier_weighted_vector_embree_host", text)
        for phrase in (
            "host-materialized logical baselines",
            "not a same device-resident backend comparison",
            "Diagnostic Ratios",
            "not public speedup claims",
            "not an optimized CPU RT opponent",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_matches_logical_contract_and_keeps_claim_flags_closed(self) -> None:
        cpu_smoke = json.loads(CPU_SMOKE.read_text(encoding="utf-8"))
        embree_smoke = json.loads(EMBREE_SMOKE.read_text(encoding="utf-8"))
        cpu_8192 = json.loads(CPU_8192.read_text(encoding="utf-8"))
        embree_8192 = json.loads(EMBREE_8192.read_text(encoding="utf-8"))
        optix_numba = json.loads(OPTIX_NUMBA_8192.read_text(encoding="utf-8"))

        self.assertFalse(cpu_smoke["validation"]["skipped"])
        self.assertFalse(embree_smoke["validation"]["skipped"])
        self.assertTrue(cpu_smoke["validation"]["passed"])
        self.assertTrue(embree_smoke["validation"]["passed"])
        self.assertEqual(cpu_smoke["frontier_collection"]["frontier_row_count"], 8_766)
        self.assertEqual(embree_smoke["frontier_collection"]["frontier_row_count"], 8_766)

        for payload in (cpu_8192, embree_8192):
            self.assertEqual(payload["body_count"], 8192)
            self.assertEqual(payload["frontier_collection"]["frontier_row_count"], 3_406_489)
            self.assertEqual(payload["frontier_collection"]["accepted_aggregate_row_count"], 477_919)
            self.assertEqual(payload["frontier_collection"]["fallback_exact_row_count"], 2_928_570)
            self.assertEqual(payload["vector_sum_summary"]["frontier_row_count"], 3_406_489)
            self.assertEqual(payload["vector_sum_summary"]["aggregate_contribution_row_count"], 477_919)
            self.assertEqual(payload["vector_sum_summary"]["exact_contribution_row_count"], 2_928_570)
            self.assertAlmostEqual(
                payload["vector_sum_summary"]["checksum_force_x"],
                optix_numba["vector_sum_summary"]["checksum_force_x"],
                places=8,
            )
            self.assertAlmostEqual(
                payload["vector_sum_summary"]["checksum_force_y"],
                optix_numba["vector_sum_summary"]["checksum_force_y"],
                places=8,
            )
            flags = payload["claim_flags"]
            self.assertTrue(flags["same_logical_frontier_contract"])
            self.assertFalse(flags["same_device_resident_contract"])
            self.assertTrue(flags["frontier_rows_materialized_on_host"])
            self.assertFalse(flags["contribution_rows_materialized_on_host"])
            self.assertFalse(flags["public_speedup_claim_authorized"])
            self.assertFalse(flags["rt_core_speedup_claim_authorized"])
            self.assertFalse(flags["whole_app_speedup_claim_authorized"])

        self.assertGreater(
            cpu_8192["run_phases"]["total_sec"],
            optix_numba["medians"]["hot_seconds_native_plus_partner"],
        )
        self.assertGreater(
            embree_8192["run_phases"]["total_sec"],
            optix_numba["medians"]["hot_seconds_native_plus_partner"],
        )
        self.assertGreater(
            embree_8192["run_phases"]["frontier_collect_sec"],
            cpu_8192["run_phases"]["frontier_collect_sec"],
        )

    def test_route_registry_records_m43_without_public_backend_wording(self) -> None:
        import rtdsl as rt

        route = rt.explain_current_benchmark_route("barnes_hut")
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4453.v1",
            route["version"],
        )
        self.assertIn("Goal4440", route["evidence_refs"])
        self.assertIn("Goal4441", route["evidence_refs"])
        self.assertIn("Goal4442", route["evidence_refs"])
        self.assertIn("host-materialized logical baselines", route["current_reader_decision"])
        self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", route["current_reader_decision"])
        self.assertIn("fused RT-native/device route", route["next_runtime_action"])
        self.assertIn(
            "public backend speedup claim from host-materialized CPU/Embree baselines",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    def test_live_cpu_host_mode_matches_reference_on_small_case(self) -> None:
        from examples.current.research_benchmarks.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        payload = barnes_hut.run_benchmark(
            "aggregate_frontier_weighted_vector_cpu_host",
            body_count=32,
            bucket_size=16,
            theta=0.5,
            force_output_mode="force_summary",
        )

        self.assertEqual(payload["mode"], "aggregate_frontier_weighted_vector_cpu_host")
        self.assertFalse(payload["validation"]["skipped"])
        self.assertTrue(payload["validation"]["passed"])
        self.assertTrue(payload["claim_flags"]["frontier_rows_materialized_on_host"])
        self.assertFalse(payload["claim_flags"]["same_device_resident_contract"])


if __name__ == "__main__":
    unittest.main()
