import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
INSPECTOR = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "inspect_xhd_acm_supplement_zip.py"
)
VALIDATOR = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "validate_xhd_external_response_intake.py"
)
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
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5335_acm_supplement_zip_inspector.json"
)


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)


def run_json(args):
    proc = subprocess.run(args, check=False, text=True, capture_output=True)
    return proc, json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None


class Goal5335AcmSupplementZipInspectorTest(unittest.TestCase):
    def test_camera_ready_only_zip_emits_no_artifact_intake(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            write_zip(zip_path, {"paper106-camera-ready.pdf": b"%PDF synthetic"})
            proc, payload = run_json(
                [
                    sys.executable,
                    str(INSPECTOR),
                    str(zip_path),
                    "--reviewer-name",
                    "test reviewer",
                    "--contact-or-source",
                    "test",
                    "--received-date",
                    "2026-07-09",
                ]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            listing = payload["artifacts"]["acm_supplement_listing"]
            self.assertFalse(listing["contains_artifact_material"])
            self.assertEqual(listing["top_level_files"], ["paper106-camera-ready.pdf"])
            self.assertEqual(listing["dataset_or_hash_entries"], [])
            self.assertEqual(listing["script_or_instruction_entries"], [])

            response = pathlib.Path(td) / "response.json"
            response.write_text(json.dumps(payload), encoding="utf-8")
            validator = subprocess.run(
                [sys.executable, str(VALIDATOR), str(response)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(validator.returncode, 0, validator.stderr)
            result = json.loads(validator.stdout)
            self.assertTrue(result["valid"])
            self.assertFalse(result["pod_expected"])
            self.assertEqual(result["next_action"], "acm_listing_inspected_no_actionable_artifact__keep_blocked")

    def test_artifact_bearing_zip_emits_instruction_intake_and_planner_goal(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            zip_path = root / "ics26-106.zip"
            write_zip(
                zip_path,
                {
                    "artifact/README.md": "download instructions",
                    "artifact/HDDatasets/graphics/dragon.ply": "ply",
                    "artifact/checksums.sha256": "abc  dragon.ply",
                    "artifact/scripts/regenerate_inputs.py": "print('regen')",
                },
            )
            response = root / "response.json"
            inspector = subprocess.run(
                [
                    sys.executable,
                    str(INSPECTOR),
                    str(zip_path),
                    "--reviewer-name",
                    "test reviewer",
                    "--contact-or-source",
                    "test",
                    "--received-date",
                    "2026-07-09",
                    "--output",
                    str(response),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(inspector.returncode, 0, inspector.stderr)
            payload = json.loads(response.read_text(encoding="utf-8"))
            listing = payload["artifacts"]["acm_supplement_listing"]
            self.assertTrue(listing["contains_artifact_material"])
            self.assertIn("artifact/HDDatasets/graphics/dragon.ply", listing["dataset_or_hash_entries"])
            self.assertIn("artifact/checksums.sha256", listing["dataset_or_hash_entries"])
            self.assertIn("artifact/scripts/regenerate_inputs.py", listing["script_or_instruction_entries"])

            incoming = root / "incoming"
            ingest = subprocess.run(
                [
                    sys.executable,
                    str(INGEST),
                    str(response),
                    "--incoming-dir",
                    str(incoming),
                    "--case-id",
                    "acm-artifact",
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(ingest.returncode, 0, ingest.stderr)
            case_dir = incoming / "acm-artifact"
            validation = json.loads((case_dir / "validation_result.json").read_text(encoding="utf-8"))
            self.assertEqual(validation["next_action"], "acm_artifact_instructions_present__ingest_before_pod")
            self.assertFalse(validation["pod_expected"])
            self.assertTrue(validation["claim_boundary"]["acm_supplement_inspected"])

            planner = subprocess.run(
                [sys.executable, str(PLANNER), str(case_dir)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(planner.returncode, 0, planner.stderr)
            plan = json.loads(planner.stdout)
            self.assertEqual(plan["plan_status"], "ready_for_separate_artifact_instruction_ingestion_goal")
            self.assertEqual(plan["recommended_goal_type"], "acm_artifact_instruction_ingestion_gate")
            self.assertFalse(plan["pod_allowed_next"])
            self.assertTrue(plan["requires_new_goal_before_pod"])
            self.assertFalse(plan["sufficient_to_claim_exact_input"])

    def test_invalid_zip_fails_without_output_claim(self):
        with tempfile.TemporaryDirectory() as td:
            bad = pathlib.Path(td) / "ics26-106.zip"
            bad.write_text("not a zip", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(INSPECTOR), str(bad)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("not a zip", proc.stderr)

    def test_summary_records_no_claim_boundary(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "acm_supplement_zip_inspector_ready__await_real_zip")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
