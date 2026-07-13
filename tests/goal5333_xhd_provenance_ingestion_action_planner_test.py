import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
INGEST = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "ingest_xhd_external_response.py"
)
PLANNER = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "plan_xhd_provenance_ingestion_from_case.py"
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
    / "xhd_goal5333_provenance_ingestion_action_planner.json"
)


def run_ingest(incoming, response, case_id):
    proc = subprocess.run(
        [
            sys.executable,
            str(INGEST),
            str(response),
            "--incoming-dir",
            str(incoming),
            "--case-id",
            case_id,
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    return proc


def run_plan(case_dir, *extra):
    return subprocess.run(
        [sys.executable, str(PLANNER), str(case_dir), *extra],
        check=False,
        text=True,
        capture_output=True,
    )


class Goal5333ProvenanceIngestionActionPlannerTest(unittest.TestCase):
    def test_positive_archive_case_plans_separate_pod_goal(self):
        with tempfile.TemporaryDirectory() as td:
            incoming = pathlib.Path(td) / "incoming"
            ingest = run_ingest(incoming, EXAMPLES / "author_input_archive_private.json", "archive")
            self.assertEqual(ingest.returncode, 0, ingest.stderr)
            case_dir = incoming / "archive"
            plan_proc = run_plan(case_dir, "--write")
            self.assertEqual(plan_proc.returncode, 0, plan_proc.stderr)
            plan = json.loads((case_dir / "provenance_action_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["plan_status"], "ready_for_separate_provenance_ingestion_goal")
            self.assertEqual(plan["recommended_goal_type"], "author_archive_provenance_ingestion_gate")
            self.assertTrue(plan["pod_allowed_next"])
            self.assertTrue(plan["requires_new_goal_before_pod"])
            self.assertFalse(plan["sufficient_to_claim_exact_input"])
            self.assertTrue((case_dir / "provenance_action_plan.md").exists())

    def test_valid_hash_only_case_stays_blocked_no_pod(self):
        with tempfile.TemporaryDirectory() as td:
            incoming = pathlib.Path(td) / "incoming"
            ingest = run_ingest(incoming, EXAMPLES / "hash_manifest_hashes_only.json", "hash-only")
            self.assertEqual(ingest.returncode, 0, ingest.stderr)
            case_dir = incoming / "hash-only"
            plan = json.loads(run_plan(case_dir).stdout)
            self.assertEqual(
                plan["plan_status"],
                "valid_response_but_no_pod_gate__keep_blocked_or_request_missing_material",
            )
            self.assertFalse(plan["pod_allowed_next"])
            self.assertIn("Hashes alone", plan["recommendation"])

    def test_invalid_template_case_requests_correction(self):
        with tempfile.TemporaryDirectory() as td:
            incoming = pathlib.Path(td) / "incoming"
            ingest = run_ingest(incoming, TEMPLATE, "template")
            self.assertEqual(ingest.returncode, 2)
            case_dir = incoming / "template"
            plan = json.loads(run_plan(case_dir).stdout)
            self.assertEqual(plan["plan_status"], "invalid_response__keep_blocked")
            self.assertEqual(plan["recommended_goal_type"], "request_corrected_response")
            self.assertFalse(plan["pod_allowed_next"])

    def test_inconsistent_case_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            incoming = pathlib.Path(td) / "incoming"
            ingest = run_ingest(incoming, EXAMPLES / "author_input_archive_private.json", "broken")
            self.assertEqual(ingest.returncode, 0, ingest.stderr)
            case_dir = incoming / "broken"
            manifest_path = case_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["pod_expected"] = False
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            plan = json.loads(run_plan(case_dir).stdout)
            self.assertEqual(plan["plan_status"], "invalid_case_record__repair_before_use")
            self.assertFalse(plan["pod_allowed_next"])
            self.assertIn("manifest and validation_result disagree on pod_expected", plan["case_record_errors"])

    def test_summary_records_no_claim_boundary(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "provenance_action_planner_ready__await_real_ingested_case")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
