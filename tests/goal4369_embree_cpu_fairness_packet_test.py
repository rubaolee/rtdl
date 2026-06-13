from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rtdsl.v2_13_embree_cpu_fairness_packet import (
    markdown_v2_13_embree_cpu_fairness_packet,
    v2_13_embree_cpu_fairness_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_13_embree_cpu_fairness_packet.py"
REPORT = ROOT / "docs" / "reports" / "goal4369_embree_cpu_fairness_hardening_2026-06-13.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4369_embree_cpu_fairness_hardening_2026-06-13.json"
CPU_THREADS8 = (
    ROOT
    / "docs"
    / "reports"
    / "goal4369_embree_cpu_fairness_hardening_2026-06-13"
    / "v2_11_cpu_partner_threads8.json"
)


class Goal4369EmbreeCpuFairnessPacketTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = v2_13_embree_cpu_fairness_packet()

    def test_packet_accepts_cpu_side_fairness_boundary(self) -> None:
        self.assertEqual("accept", self.payload["validation"]["status"], self.payload["validation"]["errors"])
        self.assertEqual("accept_internal_cpu_fairness_hardened", self.payload["status"])
        self.assertEqual(11, self.payload["summary"]["row_count"])
        self.assertEqual(10, self.payload["summary"]["promoted_app_count"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["automatic_partner_selection_authorized"])

    def test_fresh_threads8_cpu_reference_all_passes(self) -> None:
        cpu = json.loads(CPU_THREADS8.read_text(encoding="utf-8"))
        self.assertTrue(cpu["all_pass"])
        self.assertEqual(10, len(cpu["rows"]))
        env = cpu["runtime_environment"]["cpu_thread_env"]
        for name in (
            "OMP_NUM_THREADS",
            "TBB_NUM_THREADS",
            "MKL_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
            "RTDL_EMBREE_THREADS",
        ):
            self.assertEqual("8", env[name])
        self.assertTrue(all(row["status"] == "pass" for row in cpu["rows"]))

    def test_rows_are_embree_cpu_not_rt_core_and_no_fallback(self) -> None:
        self.assertEqual(0, self.payload["summary"]["embree_rt_core_accelerated_row_count"])
        self.assertEqual(0, self.payload["summary"]["fallback_detected_row_count"])
        for row in self.payload["rows"]:
            self.assertFalse(row["embree_rt_core_accelerated"], row["row_label"])
            self.assertFalse(row["fallback_detected"], row["row_label"])
            self.assertTrue(row["same_contract_or_same_stream"], row["row_label"])
            self.assertEqual("pass", row["fresh_threaded_reference_status"], row["row_label"])
            self.assertEqual(8, row["fresh_threaded_reference_threads"], row["row_label"])
            self.assertIsNotNone(row["repeat"], row["row_label"])
            self.assertIsNotNone(row["warmup"], row["row_label"])

    def test_partner_policy_is_fixed_not_auto_selected(self) -> None:
        numba_rows = [row for row in self.payload["rows"] if row["partner_policy"] == "numba_fixed_on_both_sides"]
        self.assertEqual(1, len(numba_rows))
        self.assertEqual("rt_dbscan", numba_rows[0]["app"])
        for row in self.payload["rows"]:
            self.assertNotEqual("auto", row["partner_policy"])

    def test_pip_row_uses_goal4368_optimized_exact_baseline(self) -> None:
        pip = next(row for row in self.payload["rows"] if row["contract"] == "pip_same_stream_scalar_count")
        self.assertTrue(pip["v2_13_metric_supersedes_v2_12_pip"])
        self.assertGreater(pip["embree_divided_by_optix"], 3.0)
        self.assertEqual("hot_query_median_ms", pip["metric_name"])
        self.assertIn("goal4368_pip_exact_prepared_points_executor", pip["source"])

    def test_markdown_mentions_thread_protocol_and_claim_boundary(self) -> None:
        markdown = markdown_v2_13_embree_cpu_fairness_packet(self.payload)
        self.assertIn("Goal4369 Embree CPU Fairness Hardening Packet", markdown)
        self.assertIn("Thread Protocol", markdown)
        self.assertIn("RTDL_EMBREE_THREADS", markdown)
        self.assertIn("RT-DBSCAN is the only Numba-partner row", markdown)
        self.assertIn("does not authorize public speedup", markdown)

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "packet.json"
            out_md = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("Goal4369 Embree CPU Fairness", report)

    def test_committed_artifacts_are_current(self) -> None:
        committed = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["version"], committed["version"])
        self.assertEqual("accept", committed["validation"]["status"])
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal4369 Embree CPU Fairness Hardening Packet", report)
        self.assertIn("Fallback rows accepted | 0", report)


if __name__ == "__main__":
    unittest.main()
