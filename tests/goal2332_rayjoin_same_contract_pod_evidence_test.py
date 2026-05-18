from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2332_rayjoin_same_contract_pod_evidence_2026-05-18.md"
ARTIFACTS = ROOT / "docs" / "reports" / "goal2332_rayjoin_same_contract_pod"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> object:
    return json.loads(_read(path))


def _rayjoin_query_ms(log_text: str) -> float:
    match = re.search(r"- Query:\s*([0-9.]+)\s*ms", log_text)
    if not match:
        raise AssertionError("RayJoin query timing not found")
    return float(match.group(1))


def _rayjoin_lsi_count(log_text: str) -> int:
    match = re.search(r"Intersections:\s*(\d+)", log_text)
    if not match:
        raise AssertionError("RayJoin LSI count not found")
    return int(match.group(1))


class Goal2332RayJoinSameContractPodEvidenceTest(unittest.TestCase):
    def test_report_records_partial_status_and_claim_boundary(self) -> None:
        text = _read(REPORT)
        self.assertIn("same-query-pod-evidence-partial-lsi-blocked", text)
        self.assertIn("NVIDIA RTX A5000, 570.211.01", text)
        self.assertIn("617b43aef389b91f8a9daa52e645c7a964fb9a1d", text)
        self.assertIn("one-hit LSI semantic", text)
        self.assertIn("blocker", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL-beats-RayJoin claim", text)
        self.assertIn("v2.0 release decision", text)

    def test_rayjoin_exported_streams_are_same_query_schema(self) -> None:
        for name, workload, seed in [
            ("rayjoin_lsi_stream_65536.json", "lsi", 2327),
            ("rayjoin_pip_stream_65536.json", "pip", 2328),
        ]:
            payload = _json(ARTIFACTS / name)
            self.assertEqual(payload["schema"], "rtdl.rayjoin.same_query_stream.v1")
            self.assertEqual(payload["producer"], "rayjoin_query_exec_export_patch")
            self.assertEqual(payload["workload"], workload)
            self.assertEqual(payload["query_count"], 65536)
            self.assertEqual(payload["rayjoin_query_exec_flags"]["seed"], seed)
            self.assertEqual(len(payload["queries"]), 65536)

    def test_rayjoin_logs_capture_visible_timing_and_lsi_count(self) -> None:
        lsi_log = _read(ARTIFACTS / "rayjoin_lsi_65536.log")
        pip_log = _read(ARTIFACTS / "rayjoin_pip_65536.log")
        self.assertEqual(_rayjoin_lsi_count(lsi_log), 5809)
        self.assertAlmostEqual(_rayjoin_query_ms(lsi_log), 0.460211, places=6)
        self.assertAlmostEqual(_rayjoin_query_ms(pip_log), 0.389942, places=6)
        self.assertNotIn("Intersections:", pip_log)

    def test_rtdl_replay_is_deterministic_but_lsi_mismatches_rayjoin(self) -> None:
        comparison = _json(ARTIFACTS / "rtdl_replay" / "same_query_prepared_comparison.json")
        self.assertEqual(comparison["commit"], "617b43aef389b91f8a9daa52e645c7a964fb9a1d")
        self.assertEqual(comparison["gpu"], "NVIDIA RTX A5000, 570.211.01")
        self.assertEqual(comparison["lsi"]["query_stream_producer"], "rayjoin_query_exec_export_patch")
        self.assertEqual(comparison["pip"]["query_stream_producer"], "rayjoin_query_exec_export_patch")

        lsi_values = comparison["lsi"]["scalar_count"]["values"]
        pip_values = comparison["pip"]["scalar_count"]["values"]
        self.assertEqual(set(lsi_values), {5808})
        self.assertEqual(set(pip_values), {5783})
        self.assertNotEqual(lsi_values[0], 5809)
        self.assertTrue(comparison["lsi"]["row_count_parity"])
        self.assertTrue(comparison["pip"]["row_count_parity"])

        self.assertGreater(comparison["lsi"]["scalar_count"]["median_sec"], 0.004)
        self.assertGreater(comparison["pip"]["scalar_count"]["median_sec"], 0.005)

    def test_claim_boundary_stays_locked(self) -> None:
        boundary = _json(ARTIFACTS / "rtdl_replay" / "claim_boundary.json")
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])
        self.assertTrue(boundary["requires_external_review_before_public_claim"])

    def test_debug_run_reproduces_one_hit_lsi_shape(self) -> None:
        rayjoin_debug = _read(ARTIFACTS / "debug_4096" / "rayjoin_lsi_4096.log")
        rtdl_debug = _json(ARTIFACTS / "debug_4096" / "rtdl_prepared_comparison_4096.json")
        self.assertEqual(_rayjoin_lsi_count(rayjoin_debug), 342)
        self.assertEqual(set(rtdl_debug["lsi"]["scalar_count"]["values"]), {341})
        first_phase = rtdl_debug["lsi"]["scalar_count"]["phase_samples"][0]
        self.assertEqual(first_phase["raw_candidate_count"], 342)
        self.assertEqual(first_phase["emitted_count"], 341)


if __name__ == "__main__":
    unittest.main()
