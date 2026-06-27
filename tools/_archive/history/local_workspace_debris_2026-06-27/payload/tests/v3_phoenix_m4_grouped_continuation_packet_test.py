import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m4_grouped_continuation_rerun_packet_2026-06-20.md"


class V3PhoenixM4GroupedContinuationPacketTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_is_not_release_authorization(self):
        payload = self.payload()
        self.assertEqual(payload["status"], "ready_for_pod_after_external_review_not_executed")
        self.assertEqual(payload["goal4392_gate"], "M4")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)
        policy = payload["external_use_policy"]
        self.assertFalse(policy["public_or_partner_facing_citation_allowed"])
        self.assertTrue(policy["requires_distinct_public_claim_authorization_step"])
        source_policy = payload["source_identity_policy"]
        self.assertEqual(source_policy["expected_source_version_when_no_git"], "v3-rebuild-2026-06-20")
        self.assertTrue(source_policy["git_commit_preferred"])
        self.assertTrue(source_policy["no_git_fallback_allowed"])
        self.assertIn("not git-commit based", source_policy["fallback_caveat"])
        for artifact in [
            "source_version.txt",
            "source_identity_check.txt",
            "provenance_search.txt",
            "source_manifest.sha256",
        ]:
            self.assertIn(artifact, source_policy["required_no_git_artifacts"])
        self.assertEqual(payload["remote"]["python"], "/root/rtdl_v3_rebuild_20260620/.venv/bin/python")
        env = payload["binding_execution_environment"]
        self.assertEqual(env["python"], "/root/rtdl_v3_rebuild_20260620/.venv/bin/python")
        self.assertEqual(env["required_package_versions"]["cupy-cuda12x"], "14.1.1")
        self.assertEqual(env["required_package_versions"]["numba"], "0.65.1")
        self.assertEqual(env["required_package_versions"]["torch"], "2.6.0+cu124")
        self.assertEqual(env["system_python3_preflight_status"], "failed_gpu_partner_gate_missing_cupy_and_numba")
        self.assertTrue(env["pod_reverification_required"])
        self.assertTrue(
            env["plain_python_invocation_policy"][
                "required_commands_must_not_use_plain_python3_for_tests_or_measurements"
            ]
        )

    def test_required_commands_cover_m4_cross_app_reuse(self):
        payload = self.payload()
        commands = {row["id"]: row for row in payload["required_commands"]}
        for required in [
            "env_probe",
            "pre_run_packet_gate",
            "artifact_dir_preflight",
            "native_build",
            "focused_tests",
            "m9_grouped_partner_65536",
            "m10_same_stream_65536",
            "m11_no_hidden_copy_65536",
            "m18_device_grouped_65536",
            "m23_dbscan_component_signature_524288",
            "m28_raydb_grouped_reduction_262144",
        ]:
            self.assertIn(required, commands)
            self.assertTrue(commands[required]["required"])

        self.assertIn("--point-count 65536", commands["m9_grouped_partner_65536"]["command"])
        self.assertIn("--point-count 65536", commands["m10_same_stream_65536"]["command"])
        self.assertIn("--point-count 65536", commands["m11_no_hidden_copy_65536"]["command"])
        self.assertIn("--ray-count 65536", commands["m18_device_grouped_65536"]["command"])
        self.assertIn("--copies 65536", commands["m23_dbscan_component_signature_524288"]["command"])
        self.assertIn("--generated-rows 262144", commands["m28_raydb_grouped_reduction_262144"]["command"])
        for command_id, row in commands.items():
            if command_id in {"native_build"}:
                continue
            if command_id == "env_probe":
                self.assertIn("system_python3_gpu_env_gate.json", row["command"])
                continue
            self.assertNotIn("PYTHONPATH=src:. python3", row["command"])
            self.assertNotIn("PYTHONPATH=src:. python ", row["command"])
            self.assertIn("/root/rtdl_v3_rebuild_20260620/.venv/bin/python", row["command"])
        self.assertIn("no_git_worktree", commands["env_probe"]["command"])
        self.assertIn("v3-rebuild-2026-06-20", commands["env_probe"]["command"])
        self.assertIn("source_manifest.sha256", commands["env_probe"]["command"])
        self.assertIn("source_identity_check.txt", commands["env_probe"]["command"])
        self.assertIn("provenance_search.txt", commands["env_probe"]["command"])
        self.assertIn("system_python3_gpu_env_gate.json", commands["env_probe"]["command"])
        self.assertIn("build/librtdl_embree.so", commands["env_probe"]["command"])
        self.assertIn("build/librtdl_optix.so", commands["env_probe"]["command"])
        self.assertIn("find src scripts", commands["env_probe"]["command"])

        gate_command = commands["pre_run_packet_gate"]["command"]
        self.assertIn("release_authorized", gate_command)
        self.assertIn("public_speedup_claim_authorized", gate_command)
        self.assertIn("phoenix_m7_qualified_release_rows", gate_command)
        self.assertIn("2147483648", commands["artifact_dir_preflight"]["command"])

    def test_m28_requires_independent_backend_rows(self):
        payload = self.payload()
        commands = {row["id"]: row for row in payload["required_commands"]}
        m28 = commands["m28_raydb_grouped_reduction_262144"]
        expected_rows = {
            ("embree", "count"),
            ("embree", "sum"),
            ("optix", "count"),
            ("optix", "sum"),
        }
        actual_rows = {(row["backend"], row["mode"]) for row in m28["required_independent_rows"]}
        self.assertEqual(actual_rows, expected_rows)
        self.assertFalse(m28["merge_or_average_backend_rows_allowed"])

    def test_packet_preserves_denominator_and_failure_policy(self):
        payload = self.payload()
        rule = payload["broad_v2_v3_denominator_rule"]
        self.assertEqual(rule["original_same_metric_comparison_rows"], 46)
        self.assertFalse(rule["broad_v3_faster_than_v2_claim_authorized"])
        self.assertTrue(rule["subset_geomean_must_be_labeled_subset"])
        self.assertTrue(payload["must_not_downshift_scale_without_supersession"])
        failure_policy = payload["failure_policy"]
        self.assertTrue(failure_policy["preserve_failed_artifacts"])
        self.assertTrue(failure_policy["no_scale_down_without_new_packet"])
        self.assertTrue(failure_policy["no_public_claim_from_partial_success"])
        self.assertTrue(failure_policy["record_failed_rows_at_stated_scale"])
        self.assertTrue(failure_policy["no_backfill_or_average_with_old_small_scale_rows"])
        self.assertIn("65536 rays", failure_policy["if_m18_65536_fails"])
        self.assertIn("8192-ray", failure_policy["if_m18_65536_fails"])

    def test_report_states_serious_scale_and_no_release(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "not release evidence",
            "does not authorize public speedup wording",
            "65,536 points",
            "524,288 points",
            "262,144 generated rows",
            "must not be silently",
            "public-facing or partner-facing",
            "pre_run_packet_gate",
            "embree/count",
            "optix/sum",
            "must not be backfilled",
            "source_manifest.sha256",
            "expanded non-git worktree",
            "source_version_match=pass",
            "provenance_search.txt",
            "git-commit based",
            "build/librtdl_embree.so",
            "build/librtdl_optix.so",
            "export PY=/root/rtdl_v3_rebuild_20260620/.venv/bin/python",
            "cupy-cuda12x==14.1.1",
            "numba==0.65.1",
            "torch==2.6.0+cu124",
            "System `python3` on this pod failed",
            "missing-CuPy/Numba packaging gap",
            "system_python3_gpu_env_gate.json",
            "sys.executable",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
