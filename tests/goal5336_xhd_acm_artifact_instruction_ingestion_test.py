import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
INGEST_ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "ingest_xhd_acm_artifact_instructions.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5336_acm_artifact_instruction_ingestion.json"
)


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)


def run_manifest(zip_path):
    proc = subprocess.run(
        [sys.executable, str(INGEST_ARTIFACT), str(zip_path)],
        check=False,
        text=True,
        capture_output=True,
    )
    return proc, json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None


class Goal5336AcmArtifactInstructionIngestionTest(unittest.TestCase):
    def test_candidate_bytes_and_hashes_choose_hash_mapping_gate(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            write_zip(
                zip_path,
                {
                    "artifact/HDDatasets/graphics/dragon.ply": "ply dragon",
                    "artifact/HDDatasets/graphics/happy.ply": "ply happy",
                    "artifact/checksums.sha256": "abc  dragon.ply",
                    "artifact/scripts/regenerate_inputs.py": "print('regen')",
                },
            )
            proc, manifest = run_manifest(zip_path)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(manifest["classification"], "candidate_bytes_and_hash_material_found")
            self.assertEqual(manifest["recommended_goal_type"], "acm_candidate_bytes_hash_mapping_gate")
            self.assertFalse(manifest["pod_allowed_next"])
            self.assertFalse(manifest["sufficient_to_claim_exact_input"])
            records = manifest["records"]
            categories = {record["category"] for record in records}
            self.assertIn("candidate_input_or_archive", categories)
            self.assertIn("hash_or_manifest", categories)
            self.assertIn("script", categories)
            dragon = [r for r in records if r["path"].endswith("dragon.ply") and r["category"] == "candidate_input_or_archive"]
            self.assertEqual(len(dragon), 1)
            self.assertEqual(len(dragon[0]["sha256"]), 64)

    def test_script_only_zip_requires_regeneration_review(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            write_zip(zip_path, {"artifact/README.md": "download instructions", "artifact/run_reproduce.sh": "echo hi"})
            proc, manifest = run_manifest(zip_path)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(manifest["classification"], "script_or_instruction_material_found")
            self.assertEqual(manifest["recommended_goal_type"], "acm_regeneration_or_instruction_review")
            self.assertFalse(manifest["pod_allowed_next"])

    def test_manuscript_only_zip_has_no_actionable_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            write_zip(zip_path, {"paper106-camera-ready.pdf": "%PDF synthetic"})
            proc, manifest = run_manifest(zip_path)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(manifest["classification"], "no_actionable_artifact_material_found")
            self.assertEqual(manifest["records"], [])
            self.assertFalse(manifest["pod_allowed_next"])

    def test_invalid_zip_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            zip_path.write_text("not zip", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(INGEST_ARTIFACT), str(zip_path)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("not a zip", proc.stderr)

    def test_summary_records_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "acm_artifact_instruction_ingestion_ready__await_real_artifact_zip")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
