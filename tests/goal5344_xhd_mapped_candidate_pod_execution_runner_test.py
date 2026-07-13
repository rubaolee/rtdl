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
RUNNER = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_mapped_candidate_pod_execution_plan.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5344_mapped_candidate_pod_execution_runner.json"
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


def build_plan(temp_dir, *, accepted=True):
    td = pathlib.Path(temp_dir)
    zip_path = td / "ics26-106.zip"
    spec = td / "mapping_spec.json"
    pipeline_summary = td / "pipeline_summary.json"
    plan_path = td / "plan.json"
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
            str(pipeline_summary),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    pipeline_payload = json.loads(pipeline_summary.read_text(encoding="utf-8"))
    packet = pipeline_payload["artifacts"]["mapped_candidate_same_input_gate_packet_json"]
    proc = subprocess.run(
        [
            sys.executable,
            str(PLAN_BUILDER),
            packet,
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
            str(plan_path),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    return plan_path, proc.returncode


class Goal5344XhdMappedCandidatePodExecutionRunnerTest(unittest.TestCase):
    def test_ready_plan_dry_run_lists_all_stages_without_execution(self):
        with tempfile.TemporaryDirectory() as td:
            plan, rc = build_plan(td, accepted=True)
            self.assertEqual(rc, 0)
            out = pathlib.Path(td) / "run.json"
            proc = subprocess.run(
                [sys.executable, str(RUNNER), str(plan), "--output", str(out)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(summary["classification"], "mapped_candidate_pod_execution_dry_run_ready")
            self.assertTrue(summary["dry_run"])
            self.assertFalse(summary["pod_execution_attempted"])
            self.assertEqual(summary["stage_count"], 7)
            self.assertTrue(all(stage["executed"] is False for stage in summary["stages"]))
            self.assertEqual(summary["stages"][0]["stage"], "preflight")
            self.assertEqual(summary["stages"][-1]["stage"], "local_compare")
            self.assertFalse(summary["claim_boundary"]["pod_preflight_ran"])
            self.assertFalse(summary["claim_boundary"]["same_input_gate_passed"])

    def test_not_ready_plan_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            plan, rc = build_plan(td, accepted=False)
            self.assertEqual(rc, 1)
            out = pathlib.Path(td) / "run.json"
            proc = subprocess.run(
                [sys.executable, str(RUNNER), str(plan), "--output", str(out)],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 1)
            summary = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(summary["classification"], "mapped_candidate_pod_execution_run_not_ready")
            self.assertFalse(summary["pod_execution_attempted"])
            self.assertTrue(summary["validation_errors"])

    def test_summary_records_boundaries(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["exit_label"], "mapped_candidate_pod_execution_runner_ready__dry_run_only_until_real_plan")
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
