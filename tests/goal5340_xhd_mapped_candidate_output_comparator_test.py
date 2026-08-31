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
COMPARATOR = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "compare_xhd_mapped_candidate_same_input_outputs.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5340_mapped_candidate_output_comparison.json"
)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_json(args):
    proc = subprocess.run(args, check=False, text=True, capture_output=True)
    return proc, json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None


def prepare_command_packet(temp_dir, *, accepted=True, materialize=True):
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
    subprocess.run(
        [sys.executable, str(HASH_MAPPER), str(zip_path), "--output", str(candidate_mapping)],
        check=True,
        text=True,
        capture_output=True,
    )
    spec = td / "mapping_spec.json"
    spec.write_text(
        json.dumps(
            {
                "schema": "rtdl.paper_reproduction.xhd.candidate_workload_mapping_spec.v1",
                "external_mapping_review_status": "accepted" if accepted else "proposed",
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
    subprocess.run(
        [sys.executable, str(WORKLOAD_REVIEW), str(candidate_mapping), str(spec), "--output", str(review)],
        check=True,
        text=True,
        capture_output=True,
    )
    packet = td / "packet.json"
    subprocess.run(
        [
            sys.executable,
            str(PACKET_BUILDER),
            str(review),
            "--materialized-root",
            str(materialized_root),
            "--output-dir",
            str(td / "gate-output"),
            "--output",
            str(packet),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return packet


def write_outputs_for_packet(packet_path, *, author_hd=1.25, rtdl_hd=1.25):
    packet = json.loads(pathlib.Path(packet_path).read_text(encoding="utf-8"))
    expected = packet["workload_packets"][0]["expected_outputs"]
    write_json(
        pathlib.Path(expected["author_json"]),
        {
            "HDResult": author_hd,
            "Running": {
                "AvgTime": 3.5,
                "Repeats": [{"ReportedTime": 3.25}, {"ReportedTime": 3.75}],
            },
        },
    )
    write_json(
        pathlib.Path(expected["rtdl_json"]),
        {
            "HDResult": rtdl_hd,
            "Running": {"AvgTime": 4.5},
            "RTDL": {
                "route_label": "cell-mbr-exact-witness",
                "run_phases": {"rtdl_route_sec": 0.0045, "entrypoint_total_sec": 0.005},
                "running_avg_time_semantics": "RTDL route wall time; not author internal timing",
            },
        },
    )


class Goal5340MappedCandidateOutputComparatorTest(unittest.TestCase):
    def test_matching_outputs_pass_without_performance_ratio(self):
        with tempfile.TemporaryDirectory() as td:
            packet = prepare_command_packet(td)
            write_outputs_for_packet(packet, author_hd=1.25, rtdl_hd=1.2500001)
            proc, comparison = run_json([sys.executable, str(COMPARATOR), str(packet), "--tolerance", "1e-5"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(comparison["classification"], "mapped_candidate_same_input_gate_passed")
            self.assertTrue(comparison["same_input_gate_passed"])
            self.assertFalse(comparison["performance_ratio_reported"])
            self.assertFalse(comparison["sufficient_to_claim_exact_input"])
            item = comparison["comparisons"][0]
            self.assertEqual(item["author_timing"]["reported_time_ms_median"], 3.5)
            self.assertEqual(item["rtdl_timing"]["route_label"], "cell-mbr-exact-witness")

    def test_mismatch_fails_gate(self):
        with tempfile.TemporaryDirectory() as td:
            packet = prepare_command_packet(td)
            write_outputs_for_packet(packet, author_hd=1.25, rtdl_hd=1.5)
            proc, comparison = run_json([sys.executable, str(COMPARATOR), str(packet), "--tolerance", "1e-6"])
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(comparison["classification"], "mapped_candidate_same_input_gate_failed")
            self.assertFalse(comparison["same_input_gate_passed"])
            self.assertGreater(comparison["comparisons"][0]["abs_diff"], 0.0)

    def test_missing_outputs_fail_gate(self):
        with tempfile.TemporaryDirectory() as td:
            packet = prepare_command_packet(td)
            proc, comparison = run_json([sys.executable, str(COMPARATOR), str(packet)])
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(comparison["classification"], "mapped_candidate_outputs_missing")
            self.assertFalse(comparison["same_input_gate_passed"])

    def test_packet_not_ready_fails_gate(self):
        with tempfile.TemporaryDirectory() as td:
            packet = prepare_command_packet(td, accepted=False)
            proc, comparison = run_json([sys.executable, str(COMPARATOR), str(packet)])
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(comparison["classification"], "packet_not_ready_for_output_comparison")
            self.assertIn("not command-ready", comparison["errors"][0])

    def test_summary_records_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "mapped_candidate_same_input_output_comparator_ready__await_real_pod_outputs")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["same_input_gate_passed"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
