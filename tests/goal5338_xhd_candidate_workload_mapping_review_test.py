import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
HASH_MAPPER = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "map_xhd_acm_candidate_bytes_hashes.py"
)
WORKLOAD_REVIEW = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "review_xhd_candidate_workload_mapping.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5338_candidate_workload_mapping_review.json"
)


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_json(args):
    proc = subprocess.run(args, check=False, text=True, capture_output=True)
    return proc, json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None


def make_clean_candidate_mapping(temp_dir):
    dragon = "ply dragon"
    happy = "ply happy"
    zip_path = pathlib.Path(temp_dir) / "ics26-106.zip"
    write_zip(
        zip_path,
        {
            "artifact/HDDatasets/graphics/dragon.ply": dragon,
            "artifact/HDDatasets/graphics/happy.ply": happy,
            "artifact/checksums.sha256": (
                f"{sha256_text(dragon)}  artifact/HDDatasets/graphics/dragon.ply\n"
                f"{sha256_text(happy)}  artifact/HDDatasets/graphics/happy.ply\n"
            ),
        },
    )
    mapping_path = pathlib.Path(temp_dir) / "candidate_mapping.json"
    proc = subprocess.run(
        [sys.executable, str(HASH_MAPPER), str(zip_path), "--output", str(mapping_path)],
        check=False,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr)
    return mapping_path


def write_mapping_spec(path, status="accepted", dataset2="HappyBuddha"):
    path.write_text(
        json.dumps(
            {
                "schema": "rtdl.paper_reproduction.xhd.candidate_workload_mapping_spec.v1",
                "external_mapping_review_status": status,
                "workload_mappings": [
                    {
                        "workload_id": "figure5_graphics_dragon_happybuddha",
                        "figure": "Figure 5",
                        "direction": "input1_to_input2",
                        "input_type": "ply",
                        "n_dims": 3,
                        "input1": {
                            "candidate_path": "artifact/HDDatasets/graphics/dragon.ply",
                            "paper_dataset_name": "Dragon",
                        },
                        "input2": {
                            "candidate_path": "artifact/HDDatasets/graphics/happy.ply",
                            "paper_dataset_name": dataset2,
                        },
                        "mapping_evidence": [
                            "synthetic ACM manifest path names match paper graphics dataset names",
                            "external reviewer accepted this mapping for the synthetic test case",
                        ],
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


class Goal5338CandidateWorkloadMappingReviewTest(unittest.TestCase):
    def test_accepted_clean_mapping_becomes_same_input_gate_ready_but_not_exact_claim(self):
        with tempfile.TemporaryDirectory() as td:
            candidate_mapping = make_clean_candidate_mapping(td)
            spec = pathlib.Path(td) / "mapping_spec.json"
            write_mapping_spec(spec, status="accepted")
            proc, review = run_json([sys.executable, str(WORKLOAD_REVIEW), str(candidate_mapping), str(spec)])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(review["classification"], "accepted_workload_mapping_ready_for_same_input_gate")
            self.assertEqual(review["recommended_goal_type"], "mapped_candidate_same_input_author_rtdl_gate")
            self.assertTrue(review["pod_allowed_next"])
            self.assertTrue(review["requires_separate_pod_goal"])
            self.assertFalse(review["sufficient_to_claim_exact_input"])
            self.assertEqual(review["invalid_workload_review_count"], 0)

    def test_proposed_mapping_requires_external_acceptance_before_pod(self):
        with tempfile.TemporaryDirectory() as td:
            candidate_mapping = make_clean_candidate_mapping(td)
            spec = pathlib.Path(td) / "mapping_spec.json"
            write_mapping_spec(spec, status="proposed")
            proc, review = run_json([sys.executable, str(WORKLOAD_REVIEW), str(candidate_mapping), str(spec)])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(review["classification"], "proposed_workload_mapping_requires_external_acceptance")
            self.assertEqual(review["recommended_goal_type"], "external_workload_mapping_acceptance_review")
            self.assertFalse(review["pod_allowed_next"])

    def test_unknown_paper_dataset_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            candidate_mapping = make_clean_candidate_mapping(td)
            spec = pathlib.Path(td) / "mapping_spec.json"
            write_mapping_spec(spec, status="accepted", dataset2="NotAPaperDataset")
            proc, review = run_json([sys.executable, str(WORKLOAD_REVIEW), str(candidate_mapping), str(spec)])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(review["classification"], "workload_mapping_invalid_or_incomplete")
            self.assertFalse(review["pod_allowed_next"])
            self.assertEqual(review["invalid_workload_review_count"], 1)
            self.assertIn("NotAPaperDataset", json.dumps(review))

    def test_dirty_candidate_hash_mapping_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            zip_path = pathlib.Path(td) / "ics26-106.zip"
            write_zip(
                zip_path,
                {
                    "artifact/HDDatasets/graphics/dragon.ply": "actual dragon",
                    "artifact/HDDatasets/graphics/happy.ply": "ply happy",
                    "artifact/checksums.sha256": (
                        f"{'0' * 64}  artifact/HDDatasets/graphics/dragon.ply\n"
                        f"{sha256_text('ply happy')}  artifact/HDDatasets/graphics/happy.ply\n"
                    ),
                },
            )
            candidate_mapping = pathlib.Path(td) / "candidate_mapping.json"
            proc = subprocess.run(
                [sys.executable, str(HASH_MAPPER), str(zip_path), "--output", str(candidate_mapping)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            spec = pathlib.Path(td) / "mapping_spec.json"
            write_mapping_spec(spec, status="accepted")
            proc, review = run_json([sys.executable, str(WORKLOAD_REVIEW), str(candidate_mapping), str(spec)])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(review["classification"], "workload_mapping_invalid_or_incomplete")
            self.assertFalse(review["pod_allowed_next"])
            self.assertIn("candidate_hash_mismatch_detected", review["errors"][0])

    def test_summary_records_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "candidate_workload_mapping_review_ready__await_real_mapping_spec")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
