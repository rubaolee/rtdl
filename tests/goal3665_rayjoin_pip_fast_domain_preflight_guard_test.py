from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_2026-06-06.md"
SUMMARY = ROOT / "docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_a5000/summary.json"
APP = ROOT / "examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py"
RUNNER = ROOT / "scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py"


class Goal3665RayJoinPipFastDomainPreflightGuardTest(unittest.TestCase):
    def test_report_records_guard_and_no_overclaiming(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "device_predicate_eps",
            "--rtdl-pip-require-validated-fast-domain",
            "preflight rejected before RayJoin timing",
            "47264 != 47262",
            "fail_probe_rayjoin_started no",
            "not performance evidence",
            "does not add RayJoin-specific native-engine logic",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_pod_smoke_summary_records_pass_and_fail_closed_lanes(self) -> None:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3665)
        self.assertEqual(data["unit_tests"]["result"], "34 tests OK")
        self.assertFalse(data["source_state"]["clean_source_performance_evidence"])

        valid = data["validated_slice_pass_probe"]
        self.assertEqual(valid["exact_count"], 1417)
        self.assertEqual(valid["fast_count"], 1417)
        self.assertEqual(valid["preflight_status"], "validated_fast_route_allowed")
        self.assertTrue(valid["rayjoin_timing_started_after_preflight"])

        full = data["full_county_fail_closed_probe"]
        self.assertEqual(full["exact_count"], 47262)
        self.assertEqual(full["fast_count"], 47264)
        self.assertEqual(full["preflight_status"], "fast_route_rejected")
        self.assertFalse(full["rayjoin_timing_started"])
        self.assertEqual(full["return_code"], 1)

        for authorized in data["claim_boundary"].values():
            self.assertIs(authorized, False)

    def test_code_wires_eps_and_runner_guard(self) -> None:
        app = APP.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("device_predicate_eps: float | None = None", app)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS", app)
        self.assertIn("device_predicate_eps", app)
        self.assertIn("--rtdl-pip-require-validated-fast-domain", runner)
        self.assertIn("preflight_rayjoin_pip_fast_count_domain", runner)
        self.assertIn("require_match=True", runner)
        self.assertIn('"rtdl_preflights": rtdl_preflights', runner)


if __name__ == "__main__":
    unittest.main()
