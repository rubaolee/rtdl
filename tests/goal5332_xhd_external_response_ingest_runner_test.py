import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "ingest_xhd_external_response.py"
)
EXAMPLES = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "requests" / "examples"
TEMPLATE = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "requests"
    / "external_response_intake_template.json"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5332_external_response_ingest_runner.json"
)


class Goal5332ExternalResponseIngestRunnerTest(unittest.TestCase):
    def test_valid_positive_response_creates_auditable_case(self):
        with tempfile.TemporaryDirectory() as td:
            incoming = pathlib.Path(td) / "incoming"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(EXAMPLES / "author_input_archive_private.json"),
                    "--incoming-dir",
                    str(incoming),
                    "--case-id",
                    "archive-positive",
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            case_dir = incoming / "archive-positive"
            manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
            validation = json.loads((case_dir / "validation_result.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["valid"])
            self.assertTrue(manifest["pod_expected"])
            self.assertEqual(manifest["next_action"], "archive_present__record_hashes_extract_then_pod_gate")
            self.assertTrue((case_dir / "response.json").exists())
            self.assertTrue((case_dir / "next_action.md").exists())
            self.assertFalse(manifest["sufficient_to_claim_exact_input"])
            self.assertFalse(validation["sufficient_to_claim_exact_input"])
            self.assertFalse(manifest["claim_boundary"]["full_paper_reproduction_claimed"])

    def test_invalid_template_is_recorded_and_returns_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            incoming = pathlib.Path(td) / "incoming"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(TEMPLATE),
                    "--incoming-dir",
                    str(incoming),
                    "--case-id",
                    "template-invalid",
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 2)
            case_dir = incoming / "template-invalid"
            manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
            validation = json.loads((case_dir / "validation_result.json").read_text(encoding="utf-8"))
            self.assertFalse(manifest["valid"])
            self.assertFalse(manifest["pod_expected"])
            self.assertIn("template_not_filled is not a usable response", validation["errors"])
            self.assertIn("Keep the affected X-HD", (case_dir / "next_action.md").read_text(encoding="utf-8"))

    def test_duplicate_case_fails_closed_without_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            incoming = pathlib.Path(td) / "incoming"
            args = [
                sys.executable,
                str(SCRIPT),
                str(EXAMPLES / "explicit_non_availability_statement.json"),
                "--incoming-dir",
                str(incoming),
                "--case-id",
                "duplicate-case",
            ]
            first = subprocess.run(args, check=False, text=True, capture_output=True)
            second = subprocess.run(args, check=False, text=True, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 3)
            self.assertIn("intake case already exists", second.stderr)

    def test_summary_records_no_pod_and_no_claim_contract(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "external_response_ingest_runner_ready__await_real_response")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
