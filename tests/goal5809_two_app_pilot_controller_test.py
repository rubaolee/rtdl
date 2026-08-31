from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from scripts import goal5809_two_app_pilot_controller as controller


def _result(
    *, admission: int, first_prepare: int, first_execute: int,
    second_prepare: int = 130, second_execute: int = 170,
    runtime_preload: int = 100, load_relation: int = 50,
    load_triangle: int = 60, close: int = 70,
    input_admission: int = 20, workload_materialization: int = 30,
) -> dict[str, object]:
    values = {
        "input_admission": input_admission,
        "runtime_preload": runtime_preload,
        "workload_materialization": workload_materialization,
        "load_relation": load_relation,
        "load_triangle": load_triangle,
        "first_session_admission": admission,
        "first_app_prepare": first_prepare,
        "first_app_first_exact_execute": first_execute,
        "second_app_prepare": second_prepare,
        "second_app_first_exact_execute": second_execute,
        "close": close,
    }
    clock = 10_000
    phases: dict[str, dict[str, int]] = {}
    for name, value in values.items():
        phases[name] = {
            "start_perf_counter_ns": clock,
            "end_perf_counter_ns": clock + value,
            "duration_ns": value,
        }
        clock += value
    return {
        "phase_times_absolute": {
            "phases": phases,
        },
    }


class TwoAppPilotControllerTest(unittest.TestCase):
    def test_first_use_ratio_includes_both_shared_admission_phases(self) \
            -> None:
        rtdl = _result(
            admission=100, first_prepare=60, first_execute=40)
        small_py_admission = _result(
            admission=100, first_prepare=60, first_execute=40)
        large_py_admission = _result(
            admission=900, first_prepare=60, first_execute=40)

        small = controller._descriptive_ratios(rtdl, small_py_admission)
        large = controller._descriptive_ratios(rtdl, large_py_admission)
        small_row = small["rows"]["first_use_through_first_exact_output"]
        large_row = large["rows"]["first_use_through_first_exact_output"]
        self.assertEqual(small_row["rtdl_ns"], 200)
        self.assertEqual(small_row["pyoptix_ns"], 200)
        self.assertEqual(small_row["rtdl_over_pyoptix"], 1.0)
        self.assertEqual(large_row["rtdl_ns"], 200)
        self.assertEqual(large_row["pyoptix_ns"], 1000)
        self.assertEqual(large_row["rtdl_over_pyoptix"], 0.2)
        self.assertEqual(
            large["first_use_definition"]["pyoptix"],
            "continuous shared_context_admission.start -> "
            "first_app_first_exact_execute.end")

    def test_close_is_absolute_but_mechanically_noncomparative(self) -> None:
        ratios = controller._descriptive_ratios(
            _result(
                admission=10, first_prepare=11, first_execute=9, close=31),
            _result(
                admission=40, first_prepare=21, first_execute=29, close=61))
        self.assertNotIn("close", ratios["rows"])
        close = ratios["noncomparative_absolute_phases"]["close"]
        self.assertEqual(close["rtdl_ns"], 31)
        self.assertEqual(close["pyoptix_ns"], 61)
        self.assertIsNone(close["rtdl_over_pyoptix"])
        self.assertFalse(close["comparison_authorized"])
        self.assertIn("process teardown", close["reason"])

    def test_continuous_boundaries_include_all_intervening_work(self) -> None:
        rtdl = _result(
            input_admission=2, runtime_preload=3,
            workload_materialization=5, load_relation=7,
            load_triangle=11, admission=13,
            first_prepare=17, first_execute=19,
            second_prepare=23, second_execute=29, close=31)
        pyoptix = _result(
            input_admission=37, runtime_preload=41,
            workload_materialization=43, load_relation=47,
            load_triangle=53, admission=59,
            first_prepare=61, first_execute=67,
            second_prepare=71, second_execute=73, close=79)

        rows = controller._descriptive_ratios(rtdl, pyoptix)["rows"]
        post_preload = rows["post_runtime_preload_to_first_exact_output"]
        self.assertEqual(
            post_preload["rtdl_ns"], 5 + 7 + 11 + 13 + 17 + 19)
        self.assertEqual(
            post_preload["pyoptix_ns"], 43 + 47 + 53 + 59 + 61 + 67)
        post_preload_both = rows[
            "post_runtime_preload_to_second_exact_output"]
        self.assertEqual(
            post_preload_both["rtdl_ns"],
            5 + 7 + 11 + 13 + 17 + 19 + 23 + 29)
        self.assertEqual(
            post_preload_both["pyoptix_ns"],
            43 + 47 + 53 + 59 + 61 + 67 + 71 + 73)
        first_to_second = rows["first_exact_output_to_second_exact_output"]
        self.assertEqual(first_to_second["rtdl_ns"], 23 + 29)
        self.assertEqual(first_to_second["pyoptix_ns"], 71 + 73)
        full = rows["application_lifecycle_start_to_second_exact_output"]
        self.assertEqual(
            full["rtdl_ns"],
            3 + 5 + 7 + 11 + 13 + 17 + 19 + 23 + 29)
        self.assertEqual(
            full["pyoptix_ns"],
            41 + 43 + 47 + 53 + 59 + 61 + 67 + 71 + 73)
        self.assertEqual(rows["first_app_prepare"]["rtdl_ns"], 17)
        self.assertEqual(
            rows["first_app_first_exact_execute"]["rtdl_ns"], 19)
        self.assertEqual(rows["second_app_prepare"]["rtdl_ns"], 23)
        self.assertEqual(
            rows["second_app_first_exact_execute"]["rtdl_ns"], 29)
        self.assertEqual(
            rows["first_app_prepare_to_first_exact_output"]["rtdl_ns"],
            17 + 19)
        self.assertEqual(
            rows["second_app_prepare_to_first_exact_output"]["rtdl_ns"],
            23 + 29)
        self.assertEqual(rows["workload_materialization"]["rtdl_ns"], 5)
        self.assertEqual(rows["first_session_admission"]["rtdl_ns"], 13)
        self.assertIn("experiment-only input", controller._descriptive_ratios(
            rtdl, pyoptix)["continuous_boundary_definitions"][
                "application_lifecycle_start_to_second_exact_output"])

    def test_experiment_input_admission_is_mechanically_noncomparative(self) \
            -> None:
        ratios = controller._descriptive_ratios(
            _result(
                admission=10, first_prepare=11, first_execute=9,
                input_admission=31),
            _result(
                admission=40, first_prepare=21, first_execute=29,
                input_admission=61))
        self.assertNotIn("input_admission", ratios["rows"])
        admission = ratios["noncomparative_absolute_phases"][
            "input_admission"]
        self.assertEqual(admission["rtdl_ns"], 31)
        self.assertEqual(admission["pyoptix_ns"], 61)
        self.assertIsNone(admission["rtdl_over_pyoptix"])
        self.assertFalse(admission["comparison_authorized"])
        self.assertIn("RTDL artifacts for both", admission["reason"])

    def test_continuous_boundary_rejects_reversed_child_clock(self) -> None:
        broken = _result(
            admission=10, first_prepare=11, first_execute=9)
        broken["phase_times_absolute"]["phases"][
            "second_app_first_exact_execute"]["end_perf_counter_ns"] = 1
        with self.assertRaisesRegex(RuntimeError, "invalid_continuous_boundary"):
            controller._descriptive_ratios(
                broken, _result(
                    admission=30, first_prepare=17, first_execute=23))

    def test_controller_defines_no_threshold_or_pass_fail_gate(self) -> None:
        result = controller._descriptive_ratios(
            _result(admission=10, first_prepare=11, first_execute=9),
            _result(admission=30, first_prepare=17, first_execute=23))
        self.assertFalse(result["threshold_defined"])
        self.assertFalse(result["pass_fail_decision_defined"])
        self.assertFalse(result["confidence_interval_computed"])
        self.assertFalse(result["statistics_computed"])
        self.assertIn("NO_THRESHOLD_OR_INFERENCE", result["label"])

    def test_comparison_identity_rejects_different_workload_bytes(self) -> None:
        rtdl = _result(admission=10, first_prepare=11, first_execute=9)
        pyoptix = _result(
            admission=30, first_prepare=17, first_execute=23)
        for result in (rtdl, pyoptix):
            result["inputs"] = {
                "matched_ptx_sha256": "c" * 64,
                "pyoptix_matched_baseline_ptx_sha256": "c" * 64,
                "workload_source_sha256": "d" * 64,
                "workload_bundle_sha256": "e" * 64,
            }
            result["applications"] = {
                task: {
                    "exact_oracle_passed": True,
                    "device_status_ok": True,
                    "matched_ptx_sha256": "c" * 64,
                    "composed_ptx_sha256": "f" * 64,
                    "observed_loaded_matched_ptx_sha256": "c" * 64,
                    "observed_loaded_relation_compaction_cubin_sha256": (
                        "9" * 64 if task == "relation" else None),
                }
                for task in ("relation", "triangle")
            }
        pyoptix["inputs"]["workload_bundle_sha256"] = "0" * 64
        with self.assertRaisesRegex(RuntimeError, "workload identities differ"):
            controller._comparison_identity(
                rtdl=rtdl, pyoptix=pyoptix,
                target_matched_ptx_sha256="c" * 64,
                target_relation_compaction_cubin_sha256="9" * 64)

    def test_controller_launches_one_distinct_fresh_child_per_arm(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            calls: list[list[str]] = []
            environments: list[dict[str, str]] = []

            def fake_popen(command: list[str], **kwargs: object) -> object:
                calls.append(command)
                environments.append(dict(kwargs["env"]))
                arm = (
                    "pyoptix" if "goal5809_pyoptix" in " ".join(command)
                    else "rtdl")
                pid = 9001 if arm == "rtdl" else 9002
                output = Path(command[command.index("--output") + 1])
                first = command[command.index("--first-app") + 1]
                result = _result(
                    admission=100, first_prepare=120, first_execute=80)
                result.update({
                    "schema": (
                        "rtdl.goal5809.pyoptix_two_app_pilot.v2"
                        if arm == "pyoptix" else
                        "rtdl.goal5809.runtime_session_two_app_pilot.v2"),
                    "status": (
                        "COMPLETE__DIAGNOSTIC_IDIOMATIC_PYOPTIX_"
                        "TWO_APPLICATION_PILOT" if arm == "pyoptix" else
                        "COMPLETE__DIAGNOSTIC_TWO_APPLICATION_"
                        "RUNTIME_SESSION_PILOT"),
                    "process_pid": pid,
                    "registered_performance_timing_count": 0,
                    "formal_worker_count": 0,
                    "execution_identity": {
                        "manifest_file_sha256": "1" * 64,
                        "execution_identity_sha256": "2" * 64,
                        "files_rehashed": True,
                        "runtime_environment_admission": {
                            "environment_identity_sha256": "3" * 64,
                        },
                    },
                    "lifecycle": {
                        "app_order": [
                            first,
                            "triangle" if first == "relation" else "relation",
                        ],
                    },
                    "inputs": {
                        "matched_ptx_sha256": "c" * 64,
                        "pyoptix_matched_baseline_ptx_sha256": "c" * 64,
                        "workload_source_sha256": "d" * 64,
                        "workload_bundle_sha256": "e" * 64,
                    },
                    "applications": {
                        task: {
                            "exact_oracle_passed": True,
                            "device_status_ok": True,
                            "matched_ptx_sha256": "c" * 64,
                            "observed_loaded_matched_ptx_sha256": "c" * 64,
                            "observed_loaded_relation_compaction_cubin_sha256": (
                                "9" * 64 if task == "relation" else None),
                            "composed_ptx_sha256": (
                                ("f" if task == "relation" else "a") * 64),
                        }
                        for task in ("relation", "triangle")
                    },
                })
                result["pilot_sha256"] = controller._digest(result)
                output.write_text(json.dumps(result), encoding="utf-8")
                return _FakeProcess(pid)

            args = argparse.Namespace(
                target_manifest=target,
                expected_target_manifest_sha256="a" * 64,
                execution_identity_manifest=root / "execution_identity.json",
                expected_execution_identity_manifest_sha256="1" * 64,
                first_app="triangle",
                arm_order="rtdl-first",
                output_dir=root / "output",
            )
            admitted = {
                "target_path": target.resolve(),
                "target_file_sha256": "a" * 64,
                "target": {
                    "target_manifest_sha256": "b" * 64,
                    "files": {
                        "matched_ptx": {"sha256": "c" * 64},
                        "relation_compaction_cubin": {"sha256": "9" * 64},
                    },
                },
            }
            admitted_identity = {
                "manifest_file_sha256": "1" * 64,
                "execution_identity_sha256": "2" * 64,
                "file_count": 27,
                "files_rehashed": True,
                "runtime_environment_admission": {
                    "environment_identity_sha256": "3" * 64,
                    "admitted_interpreter_path": str(
                        Path(sys.executable).resolve()),
                    "source_package_import_root": str(root.resolve()),
                    "source_import_root": str(root.resolve()),
                    "site_packages_import_root": str(root.resolve()),
                    "loader_environment": {
                        "LD_LIBRARY_PATH": None,
                        "LD_PRELOAD": None,
                    },
                },
            }
            (root / "execution_identity.json").write_text(
                "{}", encoding="utf-8")
            with mock.patch.object(
                    controller, "_admit_target", return_value=admitted), \
                    mock.patch.object(
                        controller, "admit_execution_identity",
                        return_value=admitted_identity), \
                    mock.patch.object(
                        controller, "verify_loaded_modules",
                        return_value={
                            "loaded_module_identity_verified": True,
                            "loaded_modules": {},
                        }), \
                    mock.patch.dict(
                        controller.os.environ, {
                            "RTDL_DUMP_PTX_DIR": "forbidden",
                            "RTDL_GOAL5807_PROFILE_NATIVE": "1",
                            "RTDL_OPTIX_LOG_LEVEL": "4",
                        }):
                result = controller._run(args, popen_factory=fake_popen)

            self.assertEqual(len(calls), 2)
            self.assertEqual(result["execution"]["fresh_child_process_count"], 2)
            self.assertEqual(result["execution"]["distinct_child_pids"], [
                9001, 9002])
            self.assertEqual(result["execution"]["first_app"], "triangle")
            self.assertTrue((root / "output" / "rtdl.json").is_file())
            self.assertTrue((root / "output" / "pyoptix.json").is_file())
            self.assertTrue((root / "output" / "summary.json").is_file())
            self.assertFalse(result["comparison_identity"][
                "all_arm_ptx_byte_identical"])
            self.assertFalse(result["comparison_identity"][
                "same_ptx_claim_authorized"])
            self.assertEqual(result["scope"]["direct_arm_count"], 0)
            self.assertFalse(result["scope"]["direct_arm_present"])
            self.assertFalse(
                result["scope"]["host_language_control_present"])
            self.assertFalse(
                result["scope"]["design_attribution_authorized"])
            self.assertFalse(result["scope"]["paper_evidence"])
            self.assertEqual(result["direct_arm_count"], 0)
            self.assertFalse(result["direct_arm_present"])
            self.assertFalse(result["host_language_control_present"])
            self.assertFalse(result["design_attribution_authorized"])
            self.assertEqual(
                result["execution"]["boundary_scope"],
                "POST_CUSTODY_ADMISSION__FILE_BYTES_ALREADY_REHASHED__"
                "CUDA_PROVIDER_OR_CONTEXT_FIRST_USE_PRESERVED")
            for command in calls:
                self.assertEqual(command[1:6], ["-I", "-S", "-B", "-P", "-c"])
                self.assertEqual(
                    command[command.index("--target-manifest") + 1],
                    str(target.resolve()))
                self.assertEqual(
                    command[command.index("--first-app") + 1], "triangle")
                self.assertEqual(
                    command[command.index(
                        "--execution-identity-manifest") + 1],
                    str((root / "execution_identity.json").resolve()))
            for environment in environments:
                self.assertEqual(environment["CUDA_CACHE_DISABLE"], "1")
                self.assertEqual(environment["OPTIX_CACHE_ENABLED"], "0")
                self.assertEqual(environment["OPTIX_CACHE_MAXSIZE"], "0")
                self.assertEqual(environment["RTDL_DISABLE_CUBIN_CACHE"], "1")
                self.assertEqual(environment["PYTHONNOUSERSITE"], "1")
                self.assertIn("TMPDIR", environment)
                self.assertNotIn("RTDL_DUMP_PTX_DIR", environment)
                self.assertNotIn("RTDL_GOAL5807_PROFILE_NATIVE", environment)
                self.assertNotIn("RTDL_OPTIX_LOG_LEVEL", environment)
                self.assertNotIn("PYTHONPATH", environment)
                self.assertNotIn("PYTHONHOME", environment)
                self.assertNotIn("LD_PRELOAD", environment)
            self.assertNotEqual(
                environments[0]["OPTIX_CACHE_PATH"],
                environments[1]["OPTIX_CACHE_PATH"])
            self.assertNotEqual(
                environments[0]["TMPDIR"], environments[1]["TMPDIR"])
            self.assertTrue(result["execution"][
                "isolated_empty_cache_roots_per_arm"])
            self.assertTrue(result["execution_identity"][
                "loaded_identity_verified_by_each_child"])


class _FakeProcess:
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.returncode = 0

    @staticmethod
    def communicate() -> tuple[str, str]:
        return "synthetic child summary\n", ""


if __name__ == "__main__":
    unittest.main()
