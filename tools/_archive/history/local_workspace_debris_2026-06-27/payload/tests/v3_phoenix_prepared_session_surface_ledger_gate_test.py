import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts import v3_phoenix_prepared_session_surface_ledger_gate as gate


ROOT = Path(__file__).resolve().parents[1]


class V3PhoenixPreparedSessionSurfaceLedgerGateTest(unittest.TestCase):
    def test_current_ledger_covers_all_public_prepared_session_helpers(self):
        payload = gate.build_payload()

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["public_helper_count"], 13)
        self.assertEqual(payload["ledger_row_count"], 13)
        self.assertEqual(payload["missing_from_ledger"], [])
        self.assertEqual(payload["stale_ledger_rows"], [])
        self.assertEqual(payload["missing_from_package_exports"], [])
        self.assertEqual(payload["classification_counts"]["step4_ready"], 9)
        self.assertEqual(payload["classification_counts"]["blocked_set_a_seed"], 1)
        self.assertEqual(payload["classification_counts"]["blocked_set_b_control"], 3)
        self.assertEqual(payload["classification_counts"]["other"], 0)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["all_app_pod_spend_authorized"])

    def test_gate_cli_outputs_json_and_fails_closed(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "v3_phoenix_prepared_session_surface_ledger_gate.py"),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["tool"], "v3_phoenix_prepared_session_surface_ledger_gate")
        self.assertEqual(payload["version"], "2026_06_23_m37")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["count_mismatches"], {})


if __name__ == "__main__":
    unittest.main()
