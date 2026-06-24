import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORDING_GATE = REPO_ROOT / "scripts" / "v3_release_wording_gate.py"


def load_wording_gate_module():
    spec = importlib.util.spec_from_file_location("v3_release_wording_gate_for_test", WORDING_GATE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class V3ReleaseWordingGateTest(unittest.TestCase):
    def test_wording_gate_passes_current_clean_surface(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(WORDING_GATE)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["gate_level"], "v3_0_public_release_wording_gate")
        self.assertEqual(payload["final_public_surface_scope"], "clean_v3_0_user_release_surface")
        self.assertTrue(payload["final_public_surface_gate"])
        self.assertTrue(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["violations"], [])
        self.assertEqual(payload["missing_expected_m7_row_ids"], [])
        self.assertEqual(payload["expected_m7_row_ids"], [])
        self.assertIn("V3.0.0 public release wording gate", payload["release_authorization_note"])
        self.assertTrue(payload["claim_flags"]["release_authorized"])
        self.assertFalse(payload["claim_flags"]["public_speedup_claim_authorized"])

        scanned = {path.replace("\\", "/") for path in payload["scanned_files"]}
        self.assertIn("README.md", scanned)
        self.assertIn("docs/README.md", scanned)
        self.assertIn("docs/current_v3_status.md", scanned)
        self.assertIn("docs/learn/performance_wording.md", scanned)
        self.assertIn("tutorials/current/05_measurement_boundaries.md", scanned)
        self.assertIn("examples/current/README.md", scanned)
        self.assertFalse(any(path.startswith("history/") for path in scanned))
        self.assertFalse(any(path.startswith("docs/rebuild/") for path in scanned))
        self.assertFalse(any(path.startswith("docs/reviews/") for path in scanned))

    def test_required_scanned_file_gate_fails_closed(self) -> None:
        module = load_wording_gate_module()
        payload = module.build_payload(("docs/rebuild/v3/README.md",))
        self.assertEqual(payload["status"], "fail")
        self.assertIn("docs/rebuild/v3/README.md", payload["missing_required_scanned_files"])

    def test_overclaim_scanner_catches_positive_release_wording(self) -> None:
        module = load_wording_gate_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "bad.md"
            target.write_text("V3 is now released.\n", encoding="utf-8")
            original_root = module.ROOT
            try:
                module.ROOT = tmp_path
                violations = module.scan_file(target)
            finally:
                module.ROOT = original_root
        self.assertEqual(1, len(violations))
        self.assertEqual(1, violations[0]["line"])

    def test_json_out_writes_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gate.json"
            completed = subprocess.run(
                [sys.executable, str(WORDING_GATE), "--json-out", str(out)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue(out.exists())
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "pass")


if __name__ == "__main__":
    unittest.main()
