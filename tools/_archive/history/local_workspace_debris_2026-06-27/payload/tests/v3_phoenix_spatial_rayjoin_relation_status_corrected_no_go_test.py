import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_rayjoin_relation_status_corrected_no_go.py"
NO_GO_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.json"
)
NO_GO_MD = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.md"
)


class V3PhoenixSpatialRayjoinRelationStatusCorrectedNoGoTest(unittest.TestCase):
    def load(self):
        return json.loads(NO_GO_JSON.read_text(encoding="utf-8"))

    def test_no_go_packet_rejects_candidate_without_authorizing_claims(self):
        payload = self.load()
        self.assertEqual(
            payload["status"],
            "spatial_rayjoin_relation_status_corrected_executor_no_go_exact_mismatch",
        )
        self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
        self.assertEqual(payload["candidate_route"], "relation_status_corrected_executor_validated")
        self.assertEqual(payload["exact_authority_count"], 47262)
        self.assertEqual(payload["candidate_count"], 47259)
        self.assertEqual(payload["candidate_minus_exact"], -3)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)

    def test_log_records_explicit_mode_and_fail_closed_mismatch(self):
        payload = self.load()
        log = (ROOT / payload["source_log"]).read_text(encoding="utf-8")
        self.assertIn("--count-mode relation_status_corrected_executor_validated", log)
        self.assertIn("47259 != 47262", log)
        self.assertIn("RuntimeError", log)

    def test_markdown_keeps_goal_level_audit(self):
        text = NO_GO_MD.read_text(encoding="utf-8")
        for phrase in (
            "not a release packet, not M7, and not public speedup evidence",
            "Candidate minus exact: `-3`",
            "validated_candidate_exactness_mismatch",
            "Goal-Level Decision Self-Audit",
            "Do not promote relation-status corrected Spatial",
        ):
            self.assertIn(phrase, text)

    def test_script_rebuilds_no_go_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "no_go.json"
            md_out = Path(tmp) / "no_go.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertEqual(md_out.read_text(encoding="utf-8"), NO_GO_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
