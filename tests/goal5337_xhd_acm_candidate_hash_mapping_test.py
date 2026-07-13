import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
MAPPER = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "map_xhd_acm_candidate_bytes_hashes.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5337_acm_candidate_hash_mapping.json"
)


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_mapping(zip_path):
    proc = subprocess.run(
        [sys.executable, str(MAPPER), str(zip_path)],
        check=False,
        text=True,
        capture_output=True,
    )
    return proc, json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None


class Goal5337AcmCandidateHashMappingTest(unittest.TestCase):
    def test_matching_candidate_hashes_require_workload_mapping_before_pod(self):
        dragon = "ply dragon"
        happy = "ply happy"
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            write_zip(
                zip_path,
                {
                    "artifact/HDDatasets/graphics/dragon.ply": dragon,
                    "artifact/HDDatasets/graphics/happy.ply": happy,
                    "artifact/checksums.sha256": (
                        f"{sha256_text(dragon)}  artifact/HDDatasets/graphics/dragon.ply\n"
                        f"{sha256_text(happy)}  happy.ply\n"
                    ),
                },
            )
            proc, mapping = run_mapping(zip_path)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(
                mapping["classification"],
                "all_candidate_hashes_matched__workload_mapping_required",
            )
            self.assertEqual(mapping["recommended_goal_type"], "candidate_workload_mapping_review")
            self.assertFalse(mapping["pod_allowed_next"])
            self.assertTrue(mapping["requires_workload_mapping_before_pod"])
            self.assertEqual(mapping["candidate_count"], 2)
            statuses = {record["status"] for record in mapping["candidate_mappings"]}
            self.assertEqual(statuses, {"matched_by_path_and_sha256"})

    def test_named_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            write_zip(
                zip_path,
                {
                    "artifact/HDDatasets/graphics/dragon.ply": "actual dragon",
                    "artifact/checksums.sha256": f"{'0' * 64}  artifact/HDDatasets/graphics/dragon.ply\n",
                },
            )
            proc, mapping = run_mapping(zip_path)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(mapping["classification"], "candidate_hash_mismatch_detected")
            self.assertEqual(mapping["recommended_goal_type"], "candidate_hash_mismatch_review")
            self.assertFalse(mapping["pod_allowed_next"])
            self.assertEqual(mapping["candidate_mappings"][0]["status"], "hash_mismatch_for_named_candidate")

    def test_candidate_without_hash_manifest_stays_no_pod(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            write_zip(zip_path, {"artifact/HDDatasets/graphics/dragon.ply": "actual dragon"})
            proc, mapping = run_mapping(zip_path)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(mapping["classification"], "candidate_bytes_without_parseable_hash_manifest")
            self.assertEqual(mapping["recommended_goal_type"], "candidate_identity_review")
            self.assertFalse(mapping["pod_allowed_next"])
            self.assertFalse(mapping["sufficient_to_claim_exact_input"])

    def test_invalid_zip_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            zip_path.write_text("not zip", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(MAPPER), str(zip_path)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("not a zip", proc.stderr)

    def test_summary_records_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "acm_candidate_hash_mapping_gate_ready__await_real_candidate_zip")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
