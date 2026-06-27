import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_grouped_reduction_device_column_candidate.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_ray_batch_candidate_2026-06-21.json"
)
PACKET_MD = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_ray_batch_candidate_2026-06-21.md"
)


class V3PhoenixGroupedReductionDeviceColumnCandidateTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET_JSON.read_text(encoding="utf-8"))

    def test_candidate_is_pending_pod_not_release(self):
        payload = self.payload()
        self.assertEqual(
            payload["status"],
            "grouped_reduction_device_column_ray_batch_candidate_pending_pod_not_m7",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertTrue(payload["default_route_unchanged"])
        self.assertEqual(payload["existing_m7_row_unchanged"], "grouped_reduction_sum_scalar_broadcast_repeat100_262144")
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_candidate_records_required_pod_evidence_and_forbidden_wording(self):
        payload = self.payload()
        evidence = "\n".join(payload["required_pod_evidence_before_any_promotion"])
        forbidden = "\n".join(payload["forbidden_wording"])
        self.assertIn("prepared_ray_batch_layout=cupy_device_columns", evidence)
        self.assertIn("native_device_column_path_used=true", evidence)
        self.assertIn("host_packed_ray_count=0", evidence)
        self.assertIn("2-AI review", evidence)
        self.assertIn("Do not claim the device-column candidate is faster before pod evidence exists", forbidden)
        self.assertIn("Do not call this true zero-copy", forbidden)
        self.assertIn("--optix-ray-batch-layout cupy_device_columns", payload["rerun_command"])

    def test_markdown_keeps_boundary_and_rerun_command_visible(self):
        text = PACKET_MD.read_text(encoding="utf-8")
        for phrase in (
            "not release authorization",
            "not an M7 promotion",
            "default_route_unchanged: true",
            "cupy_device_columns",
            "host_packed_ray_count=0",
            "Do not call this true zero-copy",
            "Goal-Level Decision Audit",
        ):
            self.assertIn(phrase, text)

    def test_script_rebuilds_candidate_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "candidate.json"
            md_out = Path(tmp) / "candidate.md"
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
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.payload())
            self.assertIn("Grouped-Reduction Device-Column", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
