import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
PIPELINE = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_acm_artifact_to_packet_pipeline.py"
)
PLAN_BUILDER = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_mapped_candidate_pod_execution_plan.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5343_mapped_candidate_pod_execution_plan.json"
)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_zip(path):
    dragon = "ply dragon"
    happy = "ply happy"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("artifact/HDDatasets/graphics/dragon.ply", dragon)
        zf.writestr("artifact/HDDatasets/graphics/happy.ply", happy)
        zf.writestr(
            "artifact/checksums.sha256",
            (
                f"{sha256_text(dragon)}  artifact/HDDatasets/graphics/dragon.ply\n"
                f"{sha256_text(happy)}  artifact/HDDatasets/graphics/happy.ply\n"
            ),
        )


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


def build_packet(temp_dir, *, accepted=True):
    td = pathlib.Path(temp_dir)
    zip_path = td / "ics26-106.zip"
    spec = td / "mapping_spec.json"
    summary = td / "pipeline_summary.json"
    write_zip(zip_path)
    write_mapping_spec(spec, accepted=accepted)
    subprocess.run(
        [
            sys.executable,
            str(PIPELINE),
            str(zip_path),
            str(spec),
            "--output-root",
            str(td / "pipeline"),
            "--output",
            str(summary),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(summary.read_text(encoding="utf-8"))
    return pathlib.Path(payload["artifacts"]["mapped_candidate_same_input_gate_packet_json"])


class Goal5343XhdMappedCandidatePodExecutionPlanTest(unittest.TestCase):
    def test_command_ready_packet_builds_wrapper_only_plan(self):
        with tempfile.TemporaryDirectory() as td:
            packet = build_packet(td, accepted=True)
            out = pathlib.Path(td) / "plan.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(PLAN_BUILDER),
                    str(packet),
                    "--remote-root",
                    "/tmp/xhd-goal",
                    "--remote-repo-root",
                    "/workspace/rtdl",
                    "--remote-author-bin",
                    "/workspace/X-HD/build/hd_exec",
                    "--host",
                    "pod.example",
                    "--port",
                    "22051",
                    "--output",
                    str(out),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            plan = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(plan["classification"], "mapped_candidate_pod_execution_plan_ready")
            self.assertTrue(plan["pod_allowed_next"])
            self.assertFalse(plan["commands_executed"])
            self.assertFalse(plan["outputs_compared"])
            self.assertIn("current_pod_ssh.py", " ".join(plan["wrapper_preflight_command"]))
            self.assertIn("current_pod_ssh.py", " ".join(plan["wrapper_remote_execute_command"]))
            self.assertEqual(len(plan["upload_steps"]), 2)
            self.assertEqual(len(plan["download_steps"]), 2)
            remote_shell = plan["remote_execute_shell"]
            self.assertIn("/workspace/X-HD/build/hd_exec", remote_shell)
            self.assertIn("/workspace/rtdl/Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py", remote_shell)
            self.assertIn("/tmp/xhd-goal/inputs/figure5_graphics_dragon_happybuddha/input1.ply", remote_shell)

    def test_not_ready_packet_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            packet = build_packet(td, accepted=False)
            out = pathlib.Path(td) / "plan.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(PLAN_BUILDER),
                    str(packet),
                    "--remote-root",
                    "/tmp/xhd-goal",
                    "--remote-repo-root",
                    "/workspace/rtdl",
                    "--host",
                    "pod.example",
                    "--port",
                    "22051",
                    "--output",
                    str(out),
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 1)
            plan = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(plan["classification"], "mapped_candidate_pod_execution_plan_not_ready")
            self.assertFalse(plan["pod_allowed_next"])
            self.assertTrue(plan["errors"])

    def test_summary_records_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "mapped_candidate_pod_execution_plan_ready__await_real_command_ready_packet")
        self.assertFalse(summary["pod_usage"]["used"])
        self.assertFalse(summary["claim_boundary"]["pod_preflight_ran"])
        self.assertFalse(summary["claim_boundary"]["remote_commands_executed"])
        self.assertFalse(summary["claim_boundary"]["outputs_compared"])
        self.assertFalse(summary["claim_boundary"]["same_input_gate_passed"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
