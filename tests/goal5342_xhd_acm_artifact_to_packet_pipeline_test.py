import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_acm_artifact_to_packet_pipeline.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5342_acm_artifact_to_packet_pipeline.json"
)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)


def write_mapping_spec(path, *, accepted=True):
    path.write_text(
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


def prepare_zip(path):
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
    write_zip(path, entries)


class Goal5342XhdAcmArtifactToPacketPipelineTest(unittest.TestCase):
    def test_accepted_mapping_materializes_candidates_and_builds_packet(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = pathlib.Path(td)
            zip_path = td_path / "ics26-106.zip"
            spec = td_path / "mapping_spec.json"
            out_root = td_path / "out"
            summary_path = td_path / "summary.json"
            prepare_zip(zip_path)
            write_mapping_spec(spec, accepted=True)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(zip_path),
                    str(spec),
                    "--output-root",
                    str(out_root),
                    "--output",
                    str(summary_path),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["classification"], "local_artifact_pipeline_packet_ready__await_pod_execution")
            self.assertTrue(summary["pod_allowed_next"])
            self.assertFalse(summary["commands_executed"])
            self.assertEqual(summary["intermediate_classifications"]["candidate_mapping"], "all_candidate_hashes_matched__workload_mapping_required")
            self.assertEqual(summary["intermediate_classifications"]["workload_review"], "accepted_workload_mapping_ready_for_same_input_gate")
            self.assertEqual(summary["intermediate_classifications"]["gate_packet"], "mapped_candidate_same_input_gate_commands_ready")
            self.assertEqual(summary["materialization_summary"]["materialized_count"], 2)
            packet = json.loads(pathlib.Path(summary["artifacts"]["mapped_candidate_same_input_gate_packet_json"]).read_text(encoding="utf-8"))
            self.assertTrue(packet["pod_allowed_next"])
            self.assertFalse(packet["commands_executed"])

    def test_proposed_mapping_is_not_pod_ready(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = pathlib.Path(td)
            zip_path = td_path / "ics26-106.zip"
            spec = td_path / "mapping_spec.json"
            summary_path = td_path / "summary.json"
            prepare_zip(zip_path)
            write_mapping_spec(spec, accepted=False)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(zip_path),
                    str(spec),
                    "--output-root",
                    str(td_path / "out"),
                    "--output",
                    str(summary_path),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["classification"], "local_artifact_pipeline_not_pod_ready")
            self.assertFalse(summary["pod_allowed_next"])
            self.assertEqual(summary["intermediate_classifications"]["workload_review"], "proposed_workload_mapping_requires_external_acceptance")
            self.assertEqual(summary["intermediate_classifications"]["gate_packet"], "mapping_review_not_ready_for_same_input_gate")

    def test_summary_records_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "acm_artifact_to_packet_pipeline_ready__await_real_zip_and_mapping")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["commands_executed"])
        self.assertFalse(summary["claim_boundary"]["same_input_gate_passed"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
