from __future__ import annotations

import json
from pathlib import Path
from unittest import mock
import unittest

from examples.current.research_benchmarks.rtnn import rtdl_rtnn_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py"
RUNNER = ROOT / "scripts/v3_0_m25_rtnn_app_bridge_measure.py"
REPORT = ROOT / "docs/reports/goal4422_v3_0_m25_rtnn_app_bridge_2026-06-15.md"
EVIDENCE_JSON = ROOT / "docs/reports/goal4422_v3_0_m25_rtnn_app_bridge_uniform_65536_2026-06-15.json"
LARGE_EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4422_v3_0_m25_rtnn_app_bridge_uniform_262144q65536_2026-06-15.json"
)


class Goal4422V30M25RtnnAppBridgeTest(unittest.TestCase):
    def test_rtnn_app_exposes_m19_graph_partner_bridge_mode(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"prepared_ranked_summary_graph_partner_bridge"', source)
        self.assertIn("rtnn_prepared_ranked_summary_graph_partner_bridge_payload", source)
        self.assertIn("run_v3_m19_ranked_summary_bridge_case", source)
        self.assertIn("validate_v3_m19_ranked_summary_bridge_payload", source)
        self.assertIn("query_count=args.query_count", source)
        self.assertIn('"same_stream_partner_continuation_evidence": True', source)
        self.assertNotIn("rtdl_optix_rtnn", source.lower())

    def test_mocked_app_mode_calls_m19_bridge_with_explicit_transfer_counter(self) -> None:
        m19_payload = _fake_m19_payload()
        with mock.patch.object(app.rt, "run_v3_m19_ranked_summary_bridge_case", return_value=m19_payload) as run:
            with mock.patch.object(
                app.rt,
                "validate_v3_m19_ranked_summary_bridge_payload",
                return_value={"signature_match": True, "partner_count": 2},
            ) as validate:
                payload = app.run_app(
                    "prepared_ranked_summary_graph_partner_bridge",
                    copies=16,
                    distribution="uniform",
                    warmups=1,
                    repeats=2,
                    transfer_counter_library="build/fake_counter.so",
                    hardware="unit-test",
                )

        run.assert_called_once()
        self.assertEqual(run.call_args.kwargs["point_count"], 16)
        self.assertEqual(run.call_args.kwargs["warmups"], 1)
        self.assertEqual(run.call_args.kwargs["repeats"], 2)
        self.assertEqual(Path(run.call_args.kwargs["transfer_counter_library"]).parts[-2:], ("build", "fake_counter.so"))
        validate.assert_called_once_with(m19_payload)
        self.assertEqual(payload["mode"], "prepared_ranked_summary_graph_partner_bridge")
        self.assertTrue(payload["uses_v3_m19_bridge"])
        self.assertTrue(payload["validation"]["signature_match"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertTrue(payload["claim_boundary"]["same_stream_partner_continuation_evidence"])

    def test_runner_uses_app_front_door_and_records_compact_summary(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("rtdl_rtnn_benchmark_app", source)
        self.assertIn('"prepared_ranked_summary_graph_partner_bridge"', source)
        self.assertIn("_ensure_transfer_counter_preloaded", source)
        self.assertIn("--query-count", source)
        self.assertIn('choices=("uniform", "clustered", "shell")', source)
        self.assertIn("--numba-cuda-home", source)
        self.assertIn("compact_summary", source)

    def test_report_and_optional_evidence_capture_app_bridge_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("RTNN app-level ranked-summary bridge", report)
        self.assertIn("current RTNN benchmark app", report)
        self.assertIn("CuPy and Numba", report)
        self.assertIn("262,144 resident search points", report)
        self.assertIn("not an RTNN-specific native engine ABI", report)
        if not EVIDENCE_JSON.exists() or not LARGE_EVIDENCE_JSON.exists():
            self.skipTest("M25 pod evidence JSON has not been generated on this checkout")
        for path, point_count, query_count in (
            (EVIDENCE_JSON, 65_536, 65_536),
            (LARGE_EVIDENCE_JSON, 262_144, 65_536),
        ):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                compact = payload["compact_summary"]
                self.assertEqual(compact["point_count"], point_count)
                self.assertEqual(compact["query_count"], query_count)
                self.assertTrue(compact["signature_match"])
                self.assertTrue(compact["hot_no_hidden_column_copy_ready"])
                self.assertEqual(["cupy", "numba"], compact["partners"])
                self.assertFalse(compact["public_claim_authorized"])
                self.assertEqual(payload["mode"], "prepared_ranked_summary_graph_partner_bridge")


def _fake_m19_payload() -> dict[str, object]:
    return {
        "comparison": {
            "signature_match": True,
            "hot_no_hidden_column_copy_ready": True,
            "device_result_materialization_after_hot_window": True,
            "public_claim_authorized": False,
        },
        "partner_rows": (
            {
                "partner": "cupy",
                "hot_device_run_seconds_median": 0.001,
                "materialize_seconds_median": 0.0001,
                "cuda_graph_replay_used": True,
                "same_stream_partner_device_reduction_used": True,
                "hot_no_hidden_column_copy_ready": True,
                "device_result_materialization_after_hot_window": True,
            },
            {
                "partner": "numba",
                "hot_device_run_seconds_median": 0.0011,
                "materialize_seconds_median": 0.0002,
                "cuda_graph_replay_used": True,
                "same_stream_partner_device_reduction_used": True,
                "hot_no_hidden_column_copy_ready": True,
                "device_result_materialization_after_hot_window": True,
            },
        ),
    }


if __name__ == "__main__":
    unittest.main()
