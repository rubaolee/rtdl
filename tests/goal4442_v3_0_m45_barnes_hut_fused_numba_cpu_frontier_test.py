from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
EVIDENCE_INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
PARTNER_CHOICE = ROOT / "docs/learn/partner_choice_for_custom_logic.md"
AUTHOR_STRATEGY = ROOT / "docs/learn/v2_14_app_author_implementation_strategy.md"
REPORT = ROOT / "docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_frontier_2026-06-16.md"
SMOKE = ROOT / "docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_128_smoke_2026-06-16.json"
FUSED_8192 = ROOT / "docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_8192_r11_2026-06-16.json"
FUSED_16384 = ROOT / "docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_16384_r11_2026-06-16.json"
FUSED_32768 = ROOT / "docs/reports/goal4442_v3_0_m45_barnes_hut_fused_numba_cpu_32768_r11_2026-06-16.json"
OPTIX_8192 = ROOT / "docs/reports/goal4439_v3_0_m42_barnes_hut_app_mode_numba_8192_2026-06-16.json"
OPTIX_LADDER = ROOT / "docs/reports/goal4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder_2026-06-16.json"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _has_numba_cpu() -> bool:
    try:
        import numba  # noqa: F401
        import numpy  # noqa: F401
    except Exception:
        return False
    return True


class Goal4442V30M45BarnesHutFusedNumbaCpuFrontierTest(unittest.TestCase):
    def test_app_exposes_fused_numba_cpu_mode(self) -> None:
        from examples.current.research_benchmarks.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        scope = barnes_hut.run_benchmark("scope")
        self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", barnes_hut.MODES)
        self.assertIn(
            "generic_aggregate_frontier_weighted_vector_sum_2d_numba_cpu_v1",
            scope["current_supported_contracts"],
        )

        source = APP.read_text(encoding="utf-8")
        for phrase in (
            "_fused_frontier_force_sum_numba_payload",
            "_host_numba_cpu_fused_frontier_vector_sum_kernel",
            "materialized_frontier_rows",
            "parallel_by_source",
            "cpu_numba_fused_frontier_vector_sum",
        ):
            self.assertIn(phrase, source)

    def test_readme_and_report_document_m45_conclusion(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for text in (readme, report):
            self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", text)
        for phrase in (
            "current fastest measured Barnes-Hut route",
            "faster than the current RTDL/OptiX prepared aggregate-frontier device-column route",
            "not evidence that RT cores accelerate Barnes-Hut",
            "not an Embree implementation",
            "mixed explicit choice",
        ):
            self.assertIn(phrase, report)

    def test_current_guidance_docs_do_not_carry_old_barnes_hut_partner_winner(self) -> None:
        readme = README.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")
        partner_choice = PARTNER_CHOICE.read_text(encoding="utf-8")
        author_strategy = AUTHOR_STRATEGY.read_text(encoding="utf-8")
        readme_flat = " ".join(readme.split())

        self.assertNotIn(
            "CuPy remains the faster measured force-vector partner path overall",
            partner_choice,
        )
        self.assertIn("Goal4442's fused CPU/Numba route", partner_choice)
        self.assertIn(
            "Numba wins the prepared RTDL/OptiX device-column partner route",
            evidence_index,
        )
        self.assertIn("strongest measured CPU fused baseline", readme_flat)
        self.assertIn("no-C++ fused GPU partner route", readme_flat)
        self.assertIn("fused_frontier_force_sum_bucketized_numba_cuda", readme_flat)
        self.assertIn("Current V3 note for Barnes-Hut", author_strategy)

    def test_pod_evidence_records_fused_cpu_numba_scale_ladder(self) -> None:
        smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
        fused_8192 = json.loads(FUSED_8192.read_text(encoding="utf-8"))
        fused_16384 = json.loads(FUSED_16384.read_text(encoding="utf-8"))
        fused_32768 = json.loads(FUSED_32768.read_text(encoding="utf-8"))
        optix_8192 = json.loads(OPTIX_8192.read_text(encoding="utf-8"))
        optix_ladder = json.loads(OPTIX_LADDER.read_text(encoding="utf-8"))

        self.assertFalse(smoke["validation"]["skipped"])
        self.assertTrue(smoke["validation"]["passed"])
        self.assertEqual(smoke["vector_sum_summary"]["contribution_row_count"], 8_766)

        self.assertEqual(fused_8192["vector_sum_summary"]["contribution_row_count"], 3_406_489)
        self.assertEqual(optix_8192["vector_sum_summary"]["frontier_row_count"], 3_406_489)
        self.assertAlmostEqual(
            fused_8192["vector_sum_summary"]["checksum_force_x"],
            optix_8192["vector_sum_summary"]["checksum_force_x"],
            places=8,
        )
        self.assertAlmostEqual(
            fused_8192["vector_sum_summary"]["checksum_force_y"],
            optix_8192["vector_sum_summary"]["checksum_force_y"],
            places=8,
        )

        for payload in (fused_8192, fused_16384, fused_32768):
            flags = payload["claim_flags"]
            self.assertTrue(flags["numba_cpu_njit_used"])
            self.assertFalse(flags["frontier_rows_materialized_on_host"])
            self.assertFalse(flags["contribution_rows_materialized_on_host"])
            self.assertFalse(flags["public_speedup_claim_authorized"])
            self.assertEqual(payload["vector_sum_summary"]["repeat"], 11)
            self.assertEqual(payload["vector_sum_summary"]["warmup"], 2)

        self.assertLess(
            fused_8192["run_phases"]["vector_run_median_sec"],
            optix_8192["medians"]["hot_seconds_native_plus_partner"],
        )
        ladder_by_count = {int(row["point_count"]): row for row in optix_ladder["rows"]}
        for body_count, fused in (
            (8192, fused_8192),
            (16384, fused_16384),
            (32768, fused_32768),
        ):
            self.assertIn(body_count, ladder_by_count)
            self.assertLess(
                fused["run_phases"]["vector_run_median_sec"],
                ladder_by_count[body_count]["comparison"]["numba_hot_seconds_median"],
            )

    def test_route_registry_is_mixed_explicit_after_m45(self) -> None:
        import rtdsl as rt

        route = rt.explain_current_benchmark_route("barnes_hut")
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4461.v1",
            route["version"],
        )
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual(
            "explicit_route_choice_cpu_numba_or_optix_numba_cupy_comparison",
            route["partner_policy"],
        )
        self.assertIn("Goal4442", route["evidence_refs"])
        self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", route["current_reader_decision"])
        self.assertIn("prepared_aggregate_frontier_weighted_vector_optix", route["user_choice_guidance"])
        self.assertIn(
            "Barnes-Hut RT-core speedup claim after Goal4442 fused CPU/Numba evidence",
            route["rejected_or_unpromoted_candidates"],
        )
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])

    @unittest.skipUnless(_has_numba_cpu(), "Numba CPU is required for live fused CPU smoke")
    def test_live_fused_numba_cpu_mode_matches_reference_on_small_case(self) -> None:
        from examples.current.research_benchmarks.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        payload = barnes_hut.run_benchmark(
            "fused_frontier_force_sum_bucketized_cpu_numba",
            body_count=32,
            bucket_size=16,
            theta=0.5,
            warmup=1,
            query_repeat=2,
            force_output_mode="force_summary",
        )

        self.assertEqual(payload["mode"], "fused_frontier_force_sum_bucketized_cpu_numba")
        self.assertFalse(payload["validation"]["skipped"])
        self.assertTrue(payload["validation"]["passed"])
        self.assertFalse(payload["claim_flags"]["frontier_rows_materialized_on_host"])
        self.assertFalse(payload["claim_flags"]["contribution_rows_materialized_on_host"])


if __name__ == "__main__":
    unittest.main()
