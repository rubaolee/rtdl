from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4508_v3_0_m112_rtnn_clean_target_closeout_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4508_v3_0_m112_rtnn_clean_target_closeout_2026-06-17.md"
README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4508V30M112RtnnCleanTargetCloseoutTest(unittest.TestCase):
    def test_script_rebuilds_contract_aware_closeout(self) -> None:
        module = importlib.import_module("scripts.goal4508_m112_rtnn_clean_target_closeout")
        packet = module.build_packet(ROOT)
        rows = {row["lane"]: row for row in packet["contract_rows"]}

        self.assertEqual("rtdl.v3_0.rtnn_clean_target_closeout.goal4508.v1", packet["version"])
        self.assertEqual(
            "rtnn_clean_target_internally_closed_with_public_claim_gates",
            packet["status"],
        )
        self.assertTrue(packet["readiness"]["internal_clean_target_closed"])
        self.assertTrue(packet["readiness"]["same_input_rtdl_optix_embree_gate_ready"])
        self.assertTrue(packet["readiness"]["point_file_app_front_door_ready"])
        self.assertTrue(packet["readiness"]["author_same_input_diagnostic_ready"])
        self.assertTrue(packet["readiness"]["dual_partner_chunked_runtime_ready"])
        self.assertFalse(packet["readiness"]["official_paper_dataset_reproduction_ready"])
        self.assertFalse(packet["readiness"]["same_output_author_comparison_ready"])
        self.assertFalse(packet["readiness"]["public_rt_core_speedup_claim_ready"])

        backend = rows["RTDL OptiX vs Embree same-input backend gate"]
        self.assertIn("15.50x", backend["reading"])
        self.assertIn("tie-sensitive", backend["boundary"])
        aggregate = rows["Current RTDL aggregate-only route"]
        self.assertIn("0.153553s", aggregate["primary_measure"])
        author = rows["Author-code diagnostic comparison"]
        self.assertIn("0.010274s", author["primary_measure"])
        self.assertIn("not an RTDL-beats-author", author["boundary"])
        partner_rows = {row["distribution"]: row for row in packet["chunked_partner_matrix"]}
        self.assertEqual(("uniform", "shell", "clustered"), tuple(partner_rows))
        self.assertLess(
            partner_rows["uniform"]["cupy_hot_device_run_seconds_median_sum"],
            partner_rows["shell"]["cupy_hot_device_run_seconds_median_sum"],
        )
        self.assertLess(
            partner_rows["shell"]["cupy_hot_device_run_seconds_median_sum"],
            partner_rows["clustered"]["cupy_hot_device_run_seconds_median_sum"],
        )

    def test_report_and_docs_publish_closeout_boundaries(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")

        self.assertTrue(packet["readiness"]["internal_clean_target_closed"])
        self.assertIn("RTNN is internally closed as a V3 clean target", report)
        self.assertIn("Public RT-core speedup", report)
        self.assertIn("Same-output author comparison", report)
        self.assertIn("Goal4508 is the RTNN clean-target closeout", readme)
        self.assertIn("internal V3 RTNN target is closed", readme)
        self.assertIn("Goal4508 RTNN clean-target closeout", index)
        self.assertIn("public speedup and same-output author claims still blocked", index)


if __name__ == "__main__":
    unittest.main()
