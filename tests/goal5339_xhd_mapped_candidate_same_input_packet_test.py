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
PACKET_BUILDER = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_mapped_candidate_same_input_gate_packet.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5339_mapped_candidate_same_input_gate_packet.json"
)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)


def run_json(args):
    proc = subprocess.run(args, check=False, text=True, capture_output=True)
    return proc, json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None


def prepare_mapping_review(temp_dir, *, review_status="accepted", materialize=True):
    td = pathlib.Path(temp_dir)
    dragon = "ply dragon"
    happy = "ply happy"
    entries = {
        "artifact/HDDatasets/graphics/dragon.ply": dragon,
        "artifact/HDDatasets/graphics/happy.ply": happy,
        "artifact/checksums.sha256": (
            f"{sha256_text(dragon)}  artifact/HDDatasets/graphics/dragon.ply\n"
            f"{sha256_text(happy)}  artifact/HDDatasets/graphics/happy.ply\n"
        ),
    }
    zip_path = td / "ics26-106.zip"
    write_zip(zip_path, entries)

    materialized_root = td / "materialized"
    if materialize:
        for name, content in entries.items():
            if name.endswith(".ply"):
                out = materialized_root / pathlib.PurePosixPath(name)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(content, encoding="utf-8")

    candidate_mapping = td / "candidate_mapping.json"
    proc = subprocess.run(
        [sys.executable, str(HASH_MAPPER), str(zip_path), "--output", str(candidate_mapping)],
        check=False,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr)

    spec = td / "mapping_spec.json"
    spec.write_text(
        json.dumps(
            {
                "schema": "rtdl.paper_reproduction.xhd.candidate_workload_mapping_spec.v1",
                "external_mapping_review_status": review_status,
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
                            "paper_dataset_name": "HappyBuddha",
                        },
                        "mapping_evidence": ["synthetic accepted fixture"],
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    review = td / "workload_review.json"
    proc = subprocess.run(
        [sys.executable, str(WORKLOAD_REVIEW), str(candidate_mapping), str(spec), "--output", str(review)],
        check=False,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stderr)
    return review, materialized_root


class Goal5339MappedCandidateSameInputPacketTest(unittest.TestCase):
    def test_accepted_mapping_with_materialized_files_builds_command_packet(self):
        with tempfile.TemporaryDirectory() as td:
            review, materialized_root = prepare_mapping_review(td, review_status="accepted", materialize=True)
            proc, packet = run_json(
                [
                    sys.executable,
                    str(PACKET_BUILDER),
                    str(review),
                    "--materialized-root",
                    str(materialized_root),
                    "--output-dir",
                    str(pathlib.Path(td) / "gate-output"),
                    "--author-bin",
                    "/opt/xhd/bin/hd_exec",
                    "--rtdl-route",
                    "cell-mbr-exact-witness",
                ]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(packet["classification"], "mapped_candidate_same_input_gate_commands_ready")
            self.assertTrue(packet["pod_allowed_next"])
            self.assertFalse(packet["commands_executed"])
            self.assertEqual(packet["workload_packet_count"], 1)
            workload = packet["workload_packets"][0]
            self.assertTrue(workload["files_ready"])
            self.assertIn("/opt/xhd/bin/hd_exec", workload["author_command"][0])
            self.assertIn("run_xhd_rtdl_hd_exec.py", " ".join(workload["rtdl_command"]))
            self.assertIn("cell-mbr-exact-witness", workload["rtdl_command"])
            self.assertFalse(workload["claim_boundary"]["same_input_gate_passed"])

    def test_accepted_mapping_without_materialized_files_is_not_pod_ready(self):
        with tempfile.TemporaryDirectory() as td:
            review, materialized_root = prepare_mapping_review(td, review_status="accepted", materialize=False)
            proc, packet = run_json(
                [
                    sys.executable,
                    str(PACKET_BUILDER),
                    str(review),
                    "--materialized-root",
                    str(materialized_root),
                    "--output-dir",
                    str(pathlib.Path(td) / "gate-output"),
                ]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(packet["classification"], "accepted_mapping_but_candidate_files_not_materialized")
            self.assertFalse(packet["pod_allowed_next"])
            self.assertFalse(packet["workload_packets"][0]["files_ready"])

    def test_proposed_mapping_is_not_command_ready(self):
        with tempfile.TemporaryDirectory() as td:
            review, materialized_root = prepare_mapping_review(td, review_status="proposed", materialize=True)
            proc, packet = run_json(
                [
                    sys.executable,
                    str(PACKET_BUILDER),
                    str(review),
                    "--materialized-root",
                    str(materialized_root),
                    "--output-dir",
                    str(pathlib.Path(td) / "gate-output"),
                ]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(packet["classification"], "mapping_review_not_ready_for_same_input_gate")
            self.assertFalse(packet["pod_allowed_next"])
            self.assertIn("not accepted", packet["errors"][0])

    def test_summary_records_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "mapped_candidate_same_input_gate_packet_ready__await_real_accepted_mapping_and_files")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["same_input_gate_passed"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
