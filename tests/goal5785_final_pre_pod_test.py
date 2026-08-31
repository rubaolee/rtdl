from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tarfile
import unittest

from scripts.goal5785_generate_authority import formal_body, prepare_body
from scripts.goal5785_generate_authority_v2 import python_path_without_symlink_resolution


ROOT = Path(__file__).resolve().parents[1]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Goal5785FinalPrePodTest(unittest.TestCase):
    def test_preregistration_freezes_full_shape_and_negative_outcomes(self) -> None:
        payload = json.loads((ROOT / "history/internal_docs/goal5785_final_nine_app_preregistration_20260815.json").read_text())
        self.assertEqual(payload["cohort"]["formal_worker_count"], 464)
        self.assertEqual(payload["cohort"]["independent_row_count"], 34)
        self.assertFalse(payload["expected_result_before_timing"]["overall_all_row_no_slower_expected"])
        self.assertTrue(payload["expected_result_before_timing"]["goal5784_triangle_clear_wins_may_fail_to_reproduce"])
        self.assertFalse(payload["claim_boundary"]["pod_authorized_by_this_artifact"])

    def test_budget_uses_measured_successor_cost_and_ten_hour_window(self) -> None:
        payload = json.loads((ROOT / "history/internal_docs/goal5785_final_nine_app_runtime_budget_20260815.json").read_text())
        self.assertEqual(payload["worker_count"], 464)
        self.assertGreater(payload["source_measurements"]["goal5784_successor_128_endpoint_sum_seconds"],
                           payload["source_measurements"]["goal5776_affected_128_endpoint_sum_seconds"])
        self.assertGreater(payload["total_transaction_conservative_budget_hours"], 8.0)
        self.assertEqual(payload["recommended_minimum_pod_window_hours"], 10.0)

    def test_final_bundle_is_transaction_bound_and_contains_no_native(self) -> None:
        bundle = ROOT / "history/internal_docs/goal5785_final_nine_app_pre_pod_bundle_v6_20260815.tar.gz"
        twin = ROOT / "history/internal_docs/goal5785_final_nine_app_pre_pod_bundle_v6_twin_20260815.tar.gz"
        self.assertEqual(bundle.read_bytes(), twin.read_bytes())
        with tarfile.open(bundle, "r:gz") as archive:
            names = {member.name for member in archive.getmembers() if member.isfile()}
            manifest = json.load(archive.extractfile("PORTABLE_MANIFEST.json"))
            transaction = json.load(archive.extractfile("TRANSACTION.json"))
            source = archive.extractfile("SOURCE.tar.gz").read()
        self.assertEqual(manifest["run_goal_id"], 5785)
        self.assertEqual(transaction["run_goal_id"], 5785)
        self.assertEqual(manifest["goal5785_candidate_revision"], 6)
        self.assertEqual(
            transaction["outer_harness_amendment"],
            "A4__preserve_venv_entrypoint_and_pre_worker_partner_probe")
        self.assertFalse(transaction[
            "application_compiler_native_timer_or_statistics_changed"])
        self.assertEqual(manifest["formal_worker_count"], 464)
        self.assertEqual(manifest["independent_comparison_row_count"], 34)
        self.assertFalse(manifest["contains_target_native"])
        self.assertNotIn("librtdl_optix.so", names)
        self.assertEqual(_sha(source), manifest["source_archive_sha256"])
    def test_bundle_v6_preserves_venv_python_in_prepare_and_formal(self) -> None:
        bundle = ROOT / "history/internal_docs/goal5785_final_nine_app_pre_pod_bundle_v6_20260815.tar.gz"
        with tarfile.open(bundle, "r:gz") as archive:
            harness = archive.extractfile("HARNESS/goal5776_target_prepare.py").read().decode()
            source = archive.extractfile("SOURCE.tar.gz").read()
        self.assertIn("Path(os.path.abspath(args.python))", harness)
        self.assertNotIn("python = args.python.resolve()", harness)
        with tarfile.open(fileobj=io.BytesIO(source), mode="r:gz") as source_archive:
            controller = source_archive.extractfile(
                "scripts/goal5776_real_scale_formal_controller.py").read().decode()
        self.assertIn("_preserve_python_entrypoint", controller)
        self.assertIn("_validate_worker_python_environment", controller)
        self.assertNotIn(
            'runtime["python_executable"])).resolve()', controller)

    def test_source_manifest_covers_every_nonmanifest_file(self) -> None:
        source = (ROOT / "history/internal_docs/goal5785_final_nine_app_source_v6_20260815.tar.gz").read_bytes()
        with tarfile.open(fileobj=io.BytesIO(source), mode="r:gz") as archive:
            files = {member.name: archive.extractfile(member).read()
                     for member in archive.getmembers() if member.isfile()}
        manifest_name = "history/internal_docs/goal5776_source_file_manifest.json"
        manifest = json.loads(files.pop(manifest_name))
        expected = {row["path"]: row for row in manifest["files"]}
        self.assertEqual(set(files), set(expected))
        for name, data in files.items():
            self.assertEqual(len(data), expected[name]["size_bytes"])
            self.assertEqual(_sha(data), expected[name]["sha256"])

    def test_authority_templates_fail_closed_until_owner_flag(self) -> None:
        python_identity = {
            "python_executable_sha256": "p", "python": "3.12.3",
            "numba": "0.65.1", "numpy": "2.2.6", "cupy": "14.0.1",
            "scipy": "1.16.1",
        }
        prepare = prepare_body(
            bundle_sha256="b", source_sha256="s", data_sha256="d",
            expectation_sha256="e", gpu=("gpu", "uuid", "driver", "8.9"),
            cc="89", python_identity=python_identity, authorized=False)
        self.assertFalse(prepare["owner_authorized_create_only_prepare"])
        runtime = {
            **{key: key for key in (
                "bundle_sha256", "execution_source_sha256", "data_archive_sha256",
                "rtdbscan_evidence_sha256", "native_library_sha256",
                "target_identity_sha256", "prepared_identity_sha256", "plan_sha256",
                "formal_identity_sha256", "leaf_cache_manifest_sha256",
                "runtime_budget_sha256", "expected_value_statement_sha256",
                "formal_contract_sha256")},
            "conservative_budget_seconds": 28293.29693696338,
        }
        formal = formal_body(runtime, "runtime", authorized=False)
        self.assertFalse(formal["owner_authorized_exactly_once"])
        self.assertFalse(formal["repair_retry_resume_replacement_allowed"])

    def test_authority_v2_preserves_linux_venv_python_spelling(self) -> None:
        relative = Path("stage_a2") / "venv" / "bin" / "python"
        actual = python_path_without_symlink_resolution(relative)
        self.assertEqual(actual, Path.cwd() / relative)
        self.assertEqual(actual.parts[-4:], ("stage_a2", "venv", "bin", "python"))

    def test_upload_manifest_rehashes_every_local_payload(self) -> None:
        manifest = json.loads((ROOT / "history/internal_docs/goal5785_upload_manifest_v8_20260815.json").read_text())
        self.assertEqual(len(manifest["files"]), 6)
        self.assertEqual(
            [row["role"] for row in manifest["files"]].count("optix_9_headers"), 1)
        optix = next(row for row in manifest["files"] if row["role"] == "optix_9_headers")
        self.assertEqual(optix["verified_optix_version_macro"], 90000)
        self.assertEqual(
            [row["role"] for row in manifest["files"]].count("sole_authority_generator_v2"), 1)
        self.assertEqual(
            [row["role"] for row in manifest["files"]].count("sole_execution_bundle_v6"), 1)
        for row in manifest["files"]:
            path = ROOT / row["path"]
            data = path.read_bytes()
            self.assertEqual(len(data), row["size_bytes"])
            self.assertEqual(_sha(data), row["sha256"])
        self.assertFalse(manifest["formal_worker_authorized"])


if __name__ == "__main__":
    unittest.main()
