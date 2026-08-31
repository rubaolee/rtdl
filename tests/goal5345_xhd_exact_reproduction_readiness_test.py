import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "check_xhd_exact_reproduction_readiness.py"
)
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5345_exact_reproduction_readiness.json"
)


def load_module():
    spec = importlib.util.spec_from_file_location("xhd_goal5345_readiness", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path, payload):
    pathlib.Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class Goal5345XhdExactReproductionReadinessTest(unittest.TestCase):
    def test_current_status_blocks_pod_until_artifact_access(self):
        module = load_module()
        summary = module.build_readiness(
            acm_probe_path=module.DEFAULT_ACM_PROBE,
            pipeline_path=module.DEFAULT_PIPELINE,
            plan_path=module.DEFAULT_PLAN,
            runner_path=module.DEFAULT_RUNNER,
        )
        self.assertEqual(summary["classification"], "exact_reproduction_not_pod_ready__await_artifact_access")
        self.assertFalse(summary["pod_execution_allowed_now"])
        self.assertFalse(summary["readiness"]["artifact_access_or_zip_ready"])
        self.assertFalse(summary["readiness"]["command_ready_packet_ready"])
        self.assertFalse(summary["readiness"]["pod_execution_plan_ready"])
        self.assertTrue(summary["readiness"]["pod_runner_capability_ready"])
        self.assertFalse(summary["claim_boundary"]["pod_preflight_ran"])
        self.assertFalse(summary["claim_boundary"]["same_input_gate_passed"])
        self.assertIn("403 HTML", " ".join(summary["not_allowed"]))

    def test_synthetic_ready_chain_allows_only_explicit_execution_goal(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            acm = root / "acm.json"
            pipeline = root / "pipeline.json"
            plan = root / "plan.json"
            runner = root / "runner.json"
            write_json(
                acm,
                {
                    "schema": "probe",
                    "interpretation": {
                        "exact_input_blocker_removed": True,
                        "current_environment_can_download_zip": True,
                    },
                },
            )
            write_json(
                pipeline,
                {
                    "schema": "pipeline",
                    "classification": "local_artifact_pipeline_packet_ready__await_pod_execution",
                    "pod_allowed_next": True,
                },
            )
            write_json(
                plan,
                {
                    "schema": "plan",
                    "classification": "mapped_candidate_pod_execution_plan_ready",
                    "pod_allowed_next": True,
                },
            )
            write_json(
                runner,
                {
                    "schema": "runner",
                    "script": {"execute_requires_flag": "--execute"},
                },
            )
            summary = module.build_readiness(
                acm_probe_path=acm,
                pipeline_path=pipeline,
                plan_path=plan,
                runner_path=runner,
            )
        self.assertEqual(summary["classification"], "exact_reproduction_pod_execution_ready__requires_explicit_execute_goal")
        self.assertTrue(summary["pod_execution_allowed_now"])
        self.assertTrue(summary["pod_usage"]["expected_next"])
        self.assertIn("--execute", summary["next_action"])
        self.assertFalse(summary["claim_boundary"]["remote_commands_executed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])

    def test_missing_status_artifacts_fail_closed(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            summary = module.build_readiness(
                acm_probe_path=root / "missing-acm.json",
                pipeline_path=root / "missing-pipeline.json",
                plan_path=root / "missing-plan.json",
                runner_path=root / "missing-runner.json",
            )
        self.assertEqual(summary["classification"], "exact_reproduction_readiness_unknown__missing_status_artifacts")
        self.assertFalse(summary["pod_execution_allowed_now"])
        self.assertFalse(summary["readiness"]["status_artifacts_loaded"])

    def test_status_artifact_records_no_reproduction_claims(self):
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.exact_reproduction_readiness.v1")
        self.assertFalse(summary["pod_execution_allowed_now"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["performance_ratio_claimed"])


if __name__ == "__main__":
    unittest.main()
