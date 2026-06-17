from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4485_v3_0_m89_rtdbscan_1m_compact_signature_matrix_2026-06-16.json"
JSONL = ROOT / "docs/reports/goal4485_v3_0_m89_rtdbscan_1m_compact_signature_matrix_2026-06-16.jsonl"
REPORT = ROOT / "docs/reports/goal4485_v3_0_m89_rtdbscan_1m_compact_signature_matrix_2026-06-16.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4485V30M89Rtdbscan1MCompactSignatureMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = [row for row in cls.packet["rows"] if row.get("status") == "ok"]

    def test_packet_completed_without_errors(self) -> None:
        self.assertEqual("rtdl.v3_0.rtdbscan_1m_compact_signature_matrix.goal4485.v1", self.packet["version"])
        self.assertEqual(1_048_576, self.packet["point_count"])
        self.assertEqual(18, self.packet["case_count"])
        self.assertEqual(18, self.packet["ok_count"])
        self.assertEqual(0, self.packet["error_count"])
        self.assertTrue(JSONL.exists())

    def test_1m_rows_have_same_contract_signatures(self) -> None:
        for protocol in ("one_shot_no_warmup", "warmed_replay"):
            for dataset in ("clustered3d", "road3d", "ngsim_dense"):
                rows = [
                    row
                    for row in self.rows
                    if row["case"]["dataset"] == dataset
                    and row["case"]["protocol"] == protocol
                ]
                signatures = {
                    row["case"]["mode_key"]: json.dumps(row["signature"], sort_keys=True)
                    for row in rows
                }

                self.assertEqual(
                    signatures["grouped_numba"],
                    signatures["grouped_cupy"],
                    (dataset, protocol),
                )
                self.assertEqual(
                    signatures["grouped_numba"],
                    signatures["predicate_direct_status"],
                    (dataset, protocol),
                )

    def test_predicate_direct_status_is_fastest_on_1m_rows(self) -> None:
        for protocol in ("one_shot_no_warmup", "warmed_replay"):
            metric = "prepare_plus_replay_sec" if protocol == "one_shot_no_warmup" else "elapsed_sec"
            for dataset in ("clustered3d", "road3d", "ngsim_dense"):
                rows = [
                    row
                    for row in self.rows
                    if row["case"]["dataset"] == dataset
                    and row["case"]["protocol"] == protocol
                ]
                by_mode = {row["case"]["mode_key"]: float(row[metric]) for row in rows}

                self.assertLess(by_mode["predicate_direct_status"], by_mode["grouped_numba"])
                self.assertLess(by_mode["predicate_direct_status"], by_mode["grouped_cupy"])

    def test_report_index_and_current_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rt_dbscan")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rt_dbscan"]

        self.assertIn("Goal4485", report)
        self.assertIn("1,048,576", report)
        self.assertIn("Goal4485 RT-DBSCAN 1M compact-signature route matrix", index)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4486.v1", route["version"])
        self.assertIn("524k and 1M", route["current_reader_decision"])
        self.assertIn("Goal4485", route["evidence_refs"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_adequacy.goal4486.v1",
            adequacy_module.CURRENT_BENCHMARK_ADEQUACY_VERSION,
        )
        self.assertIn("524k/1M", adequacy["current_recommended_path"])
        self.assertIn("Goal4485", adequacy["evidence_refs"])


if __name__ == "__main__":
    unittest.main()
