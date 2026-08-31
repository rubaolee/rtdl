from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import rtdsl as rt
from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "rtdl_v2_11_embree_cpu_partner_reference_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md"
LOCAL_LINUX_ARTIFACT = ROOT / "docs" / "reports" / "goal4308_rtnn_embree_front_door_local_linux.json"


class Goal4298V211EmbreeCpuPartnerReferencePacketTest(unittest.TestCase):
    def test_registry_covers_current_benchmark_apps_without_claim_authorization(self) -> None:
        rows = rt.current_embree_cpu_partner_reference_rows()
        self.assertEqual({row["app"] for row in rows}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["row_id"] for row in rows}), 10)

        validation = rt.validate_current_embree_cpu_partner_reference()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

        for row in rows:
            self.assertFalse(row["release_authorized"], row["row_id"])
            self.assertFalse(row["public_speedup_claim_authorized"], row["row_id"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"], row["row_id"])
            self.assertFalse(row["broad_rt_core_claim_authorized"], row["row_id"])
            self.assertFalse(row["paper_reproduction_claim_authorized"], row["row_id"])
            self.assertFalse(row["true_zero_copy_claim_authorized"], row["row_id"])
            self.assertFalse(row["automatic_partner_selection_authorized"], row["row_id"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"], row["row_id"])
            self.assertFalse(row["intel_gpu_performance_claim_authorized"], row["row_id"])

    def test_embree_cpu_and_numba_roles_are_precise(self) -> None:
        rows = {row["app"]: row for row in rt.current_embree_cpu_partner_reference_rows()}

        embree_apps = {app for app, row in rows.items() if row["uses_embree"]}
        self.assertEqual(embree_apps, set(V2_8_PROMOTED_BENCHMARK_APPS))

        self.assertTrue(rows["rtnn"]["uses_embree"])
        self.assertTrue(rows["rtnn"]["requires_embree_library"])
        self.assertFalse(rows["rtnn"]["uses_numba"])
        self.assertFalse(rows["rtnn"]["requires_numba"])
        self.assertEqual(
            rows["rtnn"]["route_class"],
            "embree_cpu_rt_plus_python_continuation",
        )

        for app, row in rows.items():
            command_text = " ".join(row["command"]).lower()
            self.assertNotIn("optix", command_text, app)
            self.assertNotIn("cupy", command_text, app)
            self.assertNotIn("--require-rt-core", command_text, app)
            self.assertIn("examples/current/research_benchmarks/", command_text, app)

    def test_runner_dry_run_outputs_machine_readable_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "embree_cpu_reference.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--dry-run",
                    "--threads",
                    "2",
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("current_embree_cpu_partner_reference.goal4308", completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        self.assertIsNone(payload["all_pass"])
        self.assertEqual(payload["summary"]["app_count"], 10)
        self.assertEqual(payload["summary"]["row_count"], 10)
        self.assertEqual(payload["runtime_environment"]["cpu_thread_env"]["RTDL_EMBREE_THREADS"], "2")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["v2_11_release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["automatic_partner_selection_authorized"])
        self.assertFalse(payload["intel_gpu_performance_claim_authorized"])

        row_ids = {row["row_id"] for row in payload["rows"]}
        self.assertIn("spatial_rayjoin_pip_count_embree_cpu_generic_kernel", row_ids)
        self.assertIn("rtnn_embree_cpu_ann_candidate_quality_reference", row_ids)

    def test_runner_only_filter_is_resumable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "rtnn_only.json"
            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--dry-run",
                    "--only",
                    "rtnn",
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["summary"]["row_count"], 1)
        self.assertEqual(payload["rows"][0]["row_id"], "rtnn_embree_cpu_ann_candidate_quality_reference")

    def test_report_documents_scope_and_linux_validation_status(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal4298",
            "v2.11 Embree CPU plus current CPU partner reference",
            "ten current benchmark apps",
            "RTNN",
            "Goal4308 follow-up",
            "does not authorize release action",
            "broad RT-core wording",
            "Intel GPU performance wording",
            "Local Linux validation",
            "all_pass: true",
            "ann_embree_quality",
        ):
            self.assertIn(phrase, text)

    def test_local_linux_artifact_records_all_rows_passed(self) -> None:
        payload = json.loads(LOCAL_LINUX_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], rt.CURRENT_EMBREE_CPU_PARTNER_REFERENCE_VERSION)
        self.assertTrue(payload["all_pass"])
        self.assertFalse(payload["dry_run"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["v2_11_release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["automatic_partner_selection_authorized"])
        self.assertFalse(payload["intel_gpu_performance_claim_authorized"])
        self.assertEqual(payload["validation"]["status"], "accept")
        self.assertEqual(payload["validation"]["errors"], [])
        self.assertEqual(payload["summary"]["row_count"], 1)
        self.assertEqual(len(payload["rows"]), 1)
        self.assertTrue(all(row["status"] == "pass" for row in payload["rows"]))

        rows = {row["app"]: row for row in payload["rows"]}
        self.assertTrue(rows["rtnn"]["uses_embree"])
        self.assertFalse(rows["rtnn"]["uses_numba"])
        self.assertIn("ann_embree_quality", rows["rtnn"]["stdout_tail"])


if __name__ == "__main__":
    unittest.main()
