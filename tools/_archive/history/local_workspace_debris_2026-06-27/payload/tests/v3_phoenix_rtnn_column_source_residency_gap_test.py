import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_column_source_residency_gap.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtnn_column_source_residency_gap_2026-06-21.json"
REPORT = PACKET.with_suffix(".md")


class V3PhoenixRtnnColumnSourceResidencyGapTest(unittest.TestCase):
    def load(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_records_npz_ingestion_path_without_m7(self):
        payload = self.load()
        self.assertEqual(payload["status"], "rtnn_npz_column_source_ready_for_pod_rerun_not_m7")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertEqual(payload["implemented_v3_surface"]["default_point_column_source"], "npz")
        self.assertIn("npz", payload["implemented_v3_surface"]["point_column_source_choices"])
        self.assertTrue(payload["implemented_v3_surface"]["uses_existing_vectorized_pack_points"])
        self.assertFalse(payload["implemented_v3_surface"]["v4_c_abi_or_embedding"])
        self.assertFalse(payload["implemented_v3_surface"]["app_specific_native_engine"])

    def test_packet_explains_wall_blocker_and_rerun_requirements(self):
        payload = self.load()
        comparisons = payload["comparisons"]
        measurements = payload["measurements"]["new_prepared_self_query"]
        self.assertGreater(comparisons["new_self_query_over_cupy_hot_speedup"], 2.0)
        self.assertLess(comparisons["new_self_query_over_cupy_runner_wall_speedup"], 2.0)
        self.assertGreater(measurements["input_load_share_of_runner_wall"], 0.50)
        self.assertGreater(comparisons["self_query_non_hot_over_hot_query"], 100.0)
        requirements = "\n".join(payload["pod_rerun_requirements"])
        self.assertIn("--point-column-source npz", requirements)
        self.assertIn("same-contract integer parity", requirements)
        self.assertIn("runner-wall speedups", requirements)
        self.assertIn("external AI", requirements)
        forbidden = "\n".join(payload["forbidden_shortcuts"])
        self.assertIn("19.437x hot-query", forbidden)
        self.assertIn("zero-copy", forbidden)
        self.assertIn("V4", forbidden)

    def test_report_contains_decision_audit(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Phoenix V3 RTNN Column-Source Residency Gap",
            "npz column-source route is implemented",
            "not M7",
            "POD Rerun Requirements",
            "Goal-Level Decision Audit",
            "Was I foolish?",
        ):
            self.assertIn(phrase, text)

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertIn("RTNN Column-Source", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
