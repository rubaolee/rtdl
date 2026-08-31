from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rtdsl.v4_fusion_ablation import (
    FusionVariant,
    build_checked_u64_product_sum_ablation_plan,
    load_verified_shared_contract_freeze,
)
from rtdsl.v4_operation_evidence import OperationTrace

from tests.goal5790_fusion_ablation_contract_test import FREEZE, NATIVE, _authority


ROOT = Path(__file__).parents[1]
RECOUNT = ROOT / "scripts/goal5790_recount_home_functional.py"
RUNNER = ROOT / "scripts/goal5790_home_functional_validation.py"
CLEAN = ROOT / "scripts/goal5790_home_clean_validate.py"
PREREGISTRATION = (
    ROOT / "history/internal_docs/"
    "goal5790_preregistered_expected_value_and_fallback_20260816.json"
)
HOME_MACHINE = (
    ROOT / "history/internal_docs/"
    "goal5790_frozen_home_machine_authority_20260816.json"
)
SPEC = importlib.util.spec_from_file_location("goal5790_home_recount", RECOUNT)
assert SPEC is not None and SPEC.loader is not None
HOME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOME)
CLEAN_SPEC = importlib.util.spec_from_file_location(
    "goal5790_home_clean", CLEAN)
assert CLEAN_SPEC is not None and CLEAN_SPEC.loader is not None
CLEAN_MODULE = importlib.util.module_from_spec(CLEAN_SPEC)
CLEAN_SPEC.loader.exec_module(CLEAN_MODULE)
RUNNER_SPEC = importlib.util.spec_from_file_location(
    "goal5790_home_runner", RUNNER)
assert RUNNER_SPEC is not None and RUNNER_SPEC.loader is not None
RUNNER_MODULE = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(RUNNER_MODULE)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _traversal(output_sha: str) -> dict[str, object]:
    bundle_id = HOME._program_bundle_id(HOME.PROGRAM_BUNDLE)
    receipt = {
        "schema": "rtdl.physical_execution.traversal_receipt.v1",
        "provider_library": "librtdl_optix",
        "provider_library_path": "/tmp/librtdl_optix.so",
        "provider_library_sha256": NATIVE,
        "physical_executor_classification": "optix_traversal_observed",
        "route_identity": (
            "v4_builtin_triangle_callback_ir:partner_resident_checked_count_v1"),
        "semantic_digest": "3" * 64,
        "output_digest": output_sha,
        "nonce": {"hi": 10, "lo": 20},
        "expected_program_bundles": [HOME.PROGRAM_BUNDLE],
        "expected_program_bundle_ids": [bundle_id],
        "expected_program_observed_at_receipt_edge": True,
        "native_snapshot": {
            "nonce_hi": 10, "nonce_lo": 20,
            "attempted_launch_count": 1,
            "successful_launch_count": 1,
            "complete_context_launch_count": 1,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "context_bind_count": 1,
            "raygen_invocation_count": 5,
            "program_bundle_mix": 11,
            "traversable_mix": 12,
            "pipeline_mix": 13,
            "sbt_mix": 14,
            "stream_mix": 15,
            "params_mix": 16,
            "callsite_mix": 17,
            "first_program_bundle_id": bundle_id,
            "last_program_bundle_id": bundle_id,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": 123,
            "last_traversable": 123,
            "incomplete_callsite_record_count": 0,
            "incomplete_callsite_lines": [0] * 32,
        },
        "claim_rules": dict(HOME.TRAVERSAL_CLAIM_RULES),
    }
    receipt["receipt_sha256"] = _digest(receipt)
    return receipt


def _evidence() -> tuple[dict[str, object], dict[str, object], dict[str, object],
                         dict[str, object], dict[str, object]]:
    freeze = load_verified_shared_contract_freeze(FREEZE.read_bytes())
    authority = _authority(native=NATIVE, target="4")
    row = {
        "oracle_sha256": _digest({"oracle": "k4"}),
        "timer_contract_sha256": _digest(HOME.TIMER_CONTRACTS["cold"]),
        "lifecycle_contract_sha256": _digest({
            "lifecycle": "cold", "fresh_parent_pid": True,
            "first_prepared_execute_only": False, "complete_endpoint": True,
            "bounded_functional_smoke_only": False,
        }),
    }
    segment_input_sha = _digest({"segment": "k4"})
    plan = build_checked_u64_product_sum_ablation_plan(
        freeze, variant=FusionVariant.FUSION_ON,
        target_materialization=authority,
        input_sha256=segment_input_sha,
        output_contract_sha256=_digest(HOME.OUTPUT_CONTRACT),
        oracle_sha256=row["oracle_sha256"],
        timer_contract_sha256=row["timer_contract_sha256"],
        lifecycle_contract_sha256=row["lifecycle_contract_sha256"],
        value_count=5,
    )
    output_sha = _digest(4)
    semantic_binding = {
        "authority": authority.callback_authority_nonce,
        "contract": authority.contract_sha256,
        "abi": authority.abi_sha256,
        "composed_ptx": authority.composed_program_sha256,
        "native": NATIVE,
        "device_column_count": True,
    }
    traversal = _traversal(output_sha)
    traversal["semantic_digest"] = _digest(semantic_binding)
    traversal["receipt_sha256"] = _digest({
        key: value for key, value in traversal.items()
        if key != "receipt_sha256"
    })
    trace = OperationTrace(
        plan.operation_contract(),
        execution_nonce="goal5790-small-cold-fusion_on-0001", value_count=5)
    for requirement in plan.operation_requirements:
        trace.execute(requirement.operation_id, lambda: None)
    operation = trace.finalize(
        output_sha256=output_sha,
        traversal_receipt_sha256=traversal["receipt_sha256"],
    ).to_dict()
    reduction = {
        "schema": "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
        "maximum_value": 1, "maximum_weight": 2, "weight_sum": 4,
        "value_count": 5, "value_upper_bound": 6,
        "device_kernel_launch_count": 1, "host_synchronization_count": 1,
        "logical_reduction_count": 0, "device_materialization_count": 0,
        "operation_counts_event_derived": True,
        "maximum_value_is_device_observed": True,
        "maximum_value_provenance": "device_observed",
        "provisional_sum_trusted_only_after_bounds": True,
    }
    return row, authority.to_dict(), plan.to_dict(), traversal, {
        "operation": operation, "reduction": reduction,
        "segment_input_sha": segment_input_sha,
        "semantic_binding": semantic_binding,
    }


class Goal5790HomeFunctionalHarnessTest(unittest.TestCase):
    def test_strace_ptx_producer_filter_ignores_numba_python_modules(self) -> None:
        machine = json.loads(HOME_MACHINE.read_text(encoding="utf-8"))
        trace_lines = []
        for field in (
            "cuda_nvrtc_resolved_path",
            "cuda_nvrtc_builtins_resolved_path",
            "cuda_nvvm_resolved_path",
            "cuda_libdevice_resolved_path",
        ):
            trace_lines.append(
                f'5790 openat(AT_FDCWD, "{machine[field]}", '
                'O_RDONLY|O_CLOEXEC) = 3'
            )
        for benign in (
            "/venv/lib/python3.12/site-packages/numba/cuda/__pycache__/"
            "libdevice.cpython-312.pyc",
            "/venv/lib/python3.12/site-packages/numba/cuda/__pycache__/"
            "libdevicedecl.cpython-312.pyc",
            "/venv/lib/python3.12/site-packages/numba/cuda/__pycache__/"
            "libdevicefuncs.cpython-312.pyc",
        ):
            trace_lines.append(
                f'5790 openat(AT_FDCWD, "{benign}", O_RDONLY|O_CLOEXEC) = 4'
            )
        with tempfile.TemporaryDirectory() as temp:
            trace = Path(temp) / "producer.trace"
            trace.write_text("\n".join(trace_lines) + "\n", encoding="utf-8")
            audit = CLEAN_MODULE._verify_strace_producer_opens(trace, machine)
            trace.write_text(
                "\n".join(trace_lines + [
                    '5790 openat(AT_FDCWD, "/foreign/libdevice.11.bc", '
                    'O_RDONLY|O_CLOEXEC) = 5',
                ]) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "foreign PTX producers"):
                CLEAN_MODULE._verify_strace_producer_opens(trace, machine)
        self.assertEqual(audit["foreign_successful_producer_opens"], [])
        self.assertEqual(len(audit["successful_exact_producer_opens"]), 4)

    def test_strict_plan_operation_traversal_and_scalar_bindings_accept(self) -> None:
        row, authority, plan, traversal, tail = _evidence()
        HOME._verify_plan(
            plan, variant="fusion_on", target=authority, row=row,
            segment_input_sha=tail["segment_input_sha"], query_count=5)
        self.assertTrue(HOME._receipt_ok(
            traversal, output_sha=_digest(4),
            expected_native_sha256=NATIVE, query_count=5,
            semantic_binding=tail["semantic_binding"]))
        HOME._verify_operation_receipt(
            tail["operation"], plan, traversal, variant="fusion_on",
            query_count=5, output_sha=_digest(4),
            expected_execution_nonce="goal5790-small-cold-fusion_on-0001")
        HOME._verify_reduction(
            tail["reduction"], variant="fusion_on", query_count=5,
            primitive_count=6, scalar_sum=4)

    def test_resigned_wrong_value_count_fails_closed(self) -> None:
        _row, _authority, plan, traversal, tail = _evidence()
        forged = dict(tail["operation"])
        forged["value_count"] = 999
        forged["receipt_sha256"] = _digest({
            key: value for key, value in forged.items()
            if key != "receipt_sha256"
        })
        with self.assertRaisesRegex(
                AssertionError, "contract/value/output binding mismatch"):
            HOME._verify_operation_receipt(
                forged, plan, traversal, variant="fusion_on",
                query_count=5, output_sha=_digest(4),
                expected_execution_nonce="goal5790-small-cold-fusion_on-0001")

    def test_internally_resigned_false_output_fails_scalar_binding(self) -> None:
        _row, _authority, plan, traversal, tail = _evidence()
        false_sha = "f" * 64
        forged_traversal = dict(traversal)
        forged_traversal["output_digest"] = false_sha
        forged_traversal["receipt_sha256"] = _digest({
            key: value for key, value in forged_traversal.items()
            if key != "receipt_sha256"
        })
        forged = dict(tail["operation"])
        forged["output_sha256"] = false_sha
        forged["traversal_receipt_sha256"] = forged_traversal["receipt_sha256"]
        forged["receipt_sha256"] = _digest({
            key: value for key, value in forged.items()
            if key != "receipt_sha256"
        })
        self.assertFalse(HOME._receipt_ok(
            forged_traversal, output_sha=_digest(4),
            expected_native_sha256=NATIVE, query_count=5,
            semantic_binding=tail["semantic_binding"]))
        with self.assertRaisesRegex(
                AssertionError, "contract/value/output binding mismatch"):
            HOME._verify_operation_receipt(
                forged, plan, forged_traversal, variant="fusion_on",
                query_count=5, output_sha=_digest(4),
                expected_execution_nonce="goal5790-small-cold-fusion_on-0001")

    def test_resigned_arbitrary_operation_nonce_fails_replay_binding(self) -> None:
        _row, _authority, plan, traversal, tail = _evidence()
        forged = dict(tail["operation"])
        forged["execution_nonce"] = "goal5790-attacker-replay-valid-shape-0001"
        forged["receipt_sha256"] = _digest({
            key: value for key, value in forged.items()
            if key != "receipt_sha256"
        })
        with self.assertRaisesRegex(AssertionError, "nonce/replay binding"):
            HOME._verify_operation_receipt(
                forged, plan, traversal, variant="fusion_on",
                query_count=5, output_sha=_digest(4),
                expected_execution_nonce="goal5790-small-cold-fusion_on-0001")

    def test_resigned_wrong_native_or_program_bundle_fails_traversal(self) -> None:
        _row, _authority, _plan, traversal, _tail = _evidence()
        for field, forged_value in (
            ("provider_library_sha256", "f" * 64),
            ("expected_program_bundles", ["wrong_program"]),
        ):
            with self.subTest(field=field):
                forged = dict(traversal)
                forged[field] = forged_value
                forged["receipt_sha256"] = _digest({
                    key: value for key, value in forged.items()
                    if key != "receipt_sha256"
                })
                self.assertFalse(HOME._receipt_ok(
                    forged, output_sha=_digest(4),
                    expected_native_sha256=NATIVE, query_count=5,
                    semantic_binding=_evidence()[4]["semantic_binding"]))

    def test_resigned_wrong_traversal_semantic_digest_fails_closed(self) -> None:
        _row, _authority, _plan, traversal, tail = _evidence()
        forged = dict(traversal)
        forged["semantic_digest"] = "f" * 64
        forged["receipt_sha256"] = _digest({
            key: value for key, value in forged.items()
            if key != "receipt_sha256"
        })
        self.assertFalse(HOME._receipt_ok(
            forged, output_sha=_digest(4), expected_native_sha256=NATIVE,
            query_count=5, semantic_binding=tail["semantic_binding"]))

    def test_resigned_semantic_authority_contract_or_abi_fails_target_binding(
            self) -> None:
        _row, authority, _plan, traversal, tail = _evidence()
        bindings = {
            "authority": "goal5790-attacker-authority-0001",
            "contract": "8" * 64,
            "abi": "9" * 64,
        }
        for field, forged_value in bindings.items():
            with self.subTest(field=field):
                forged_binding = dict(tail["semantic_binding"])
                forged_binding[field] = forged_value
                forged_traversal = dict(traversal)
                forged_traversal["semantic_digest"] = _digest(forged_binding)
                forged_traversal["receipt_sha256"] = _digest({
                    key: value for key, value in forged_traversal.items()
                    if key != "receipt_sha256"
                })
                self.assertTrue(HOME._receipt_ok(
                    forged_traversal, output_sha=_digest(4),
                    expected_native_sha256=NATIVE, query_count=5,
                    semantic_binding=forged_binding))
                with self.assertRaisesRegex(
                        AssertionError, "semantic binding/target authority"):
                    HOME._verify_semantic_binding_against_target(
                        forged_binding, authority)

    def test_ptx_program_identity_is_bound_to_target_and_directives(self) -> None:
        authority = _authority(native=NATIVE, target="4").to_dict()
        common = {"version": "8.2", "target": "sm_61", "address_size": "64"}
        identity = {
            "schema": "rtdl.goal5790.ptx_program_identity.v1",
            "wrapper": {"ptx_sha256": "a" * 64, "directives": common},
            "ordered_leaves": [{
                "role": "any_hit", "abi_name": "goal5790_any_hit",
                "ptx_sha256": "b" * 64, "directives": common,
            }],
            "composed": {
                "ptx_sha256": authority["composed_program_sha256"],
                "directives": common,
            },
            "composer_leaf_bindings": [["any_hit", "goal5790_any_hit"]],
            "wrapper_leaf_composed_directive_equality_verified": True,
        }
        HOME._verify_ptx_program_identity(identity, _digest(identity), authority)
        forged = json.loads(json.dumps(identity))
        forged["ordered_leaves"][0]["directives"]["version"] = "8.7"
        with self.assertRaisesRegex(AssertionError, "role/symbol/directive"):
            HOME._verify_ptx_program_identity(
                forged, _digest(forged), authority)
        forged = json.loads(json.dumps(identity))
        forged["composed"]["ptx_sha256"] = "f" * 64
        with self.assertRaisesRegex(AssertionError, "target authority"):
            HOME._verify_ptx_program_identity(
                forged, _digest(forged), authority)

    def test_off_reduction_requires_declared_primitive_bound_provenance(self) -> None:
        _row, _authority, _plan, _traversal, tail = _evidence()
        reduction = dict(tail["reduction"])
        reduction.update({
            "maximum_value": 6,
            "maximum_value_is_device_observed": False,
            "maximum_value_provenance": (
                "optix_producer_declared_primitive_bound"),
            "device_kernel_launch_count": 0,
            "host_synchronization_count": 3,
            "logical_reduction_count": 3,
            "device_materialization_count": 1,
        })
        HOME._verify_reduction(
            reduction, variant="fusion_off", query_count=5,
            primitive_count=6, scalar_sum=4)
        forged = dict(reduction)
        forged["maximum_value_provenance"] = "device_observed"
        with self.assertRaisesRegex(AssertionError, "operation-count/evidence"):
            HOME._verify_reduction(
                forged, variant="fusion_off", query_count=5,
                primitive_count=6, scalar_sum=4)

    def test_k4_oracle_and_exact_ten_lane_cardinality(self) -> None:
        self.assertEqual(HOME._triangle_count(
            [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]), 4)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = root / "raw"
            raw.mkdir()
            for index in range(9):
                (raw / f"{index:02d}.json").write_text("{}\n", encoding="utf-8")
            completed = subprocess.run([
                sys.executable, str(RECOUNT), "--raw", str(raw),
                "--expected-native-sha256", NATIVE,
                "--output", str(root / "RECOUNT.json"),
            ], cwd=ROOT, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, check=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("expected 10 raw lanes", completed.stdout)

    def test_recount_is_independent_and_runner_records_no_elapsed_values(self) -> None:
        recount = RECOUNT.read_text(encoding="utf-8")
        self.assertNotIn("from rtdsl", recount)
        self.assertNotIn("import rtdsl", recount)
        self.assertNotIn("Paper-reproduction-apps", recount)
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertNotIn("time.perf_counter", runner)
        self.assertIn('"elapsed_values_recorded": False', runner)
        self.assertIn("downstream_operation_recipe_scope", runner)
        self.assertIn("execute_segment_unsealed", runner)
        self.assertIn("unsealed.seal()", runner)
        self.assertIn(
            '"evidence_hashing_or_serialization_inside_registered_timer": False',
            runner,
        )

    def test_clean_validator_binds_executing_harness_and_preregistration(self) -> None:
        source = CLEAN.read_text(encoding="utf-8")
        self.assertIn("executing_harness_sha = _sha(Path(__file__).resolve())", source)
        self.assertIn("outer/source Goal5790 clean validator identity mismatch", source)
        authority = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
        self.assertEqual(authority["scope"]["independent_row_count"], 6)
        self.assertFalse(authority["comparison"]["fixed_speedup_floor_used"])
        self.assertTrue(authority["success_and_fallback"][
            "all_six_rows_must_be_retained"])
        self.assertEqual(
            authority["success_and_fallback"]["zero_ci_clear_wins"],
            "no_demonstrated_performance_fusion_claim__retain_all_rows__no_rerun_or_tuning",
        )
        self.assertFalse(authority["governance"][
            "home_elapsed_values_may_change_this_authority"])
        machine = json.loads(HOME_MACHINE.read_text(encoding="utf-8"))
        unsigned = dict(machine)
        claimed = unsigned.pop("receipt_sha256")
        self.assertEqual(_digest(unsigned), claimed)
        self.assertEqual(machine["execution_environment_class"],
                         "HOME_PASCAL_FUNCTIONAL_ONLY")
        self.assertEqual(machine["gpu_uuid"],
                         "GPU-8e04454e-c177-6e5b-3f43-e676980ecdfa")
        self.assertEqual(machine["compute_capability"], "6.1")
        self.assertEqual(machine["cuda_host_compiler_path"], "/usr/bin/g++-12")
        self.assertEqual(
            machine["cuda_host_compiler_version"],
            "g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0",
        )
        self.assertEqual(
            machine["cuda_nvcc_version"],
            "Build cuda_12.2.r12.2/compiler.33191640_0",
        )
        self.assertEqual(
            machine["cuda_nvrtc_resolved_path"],
            "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
            "libnvrtc.so.12.2.140",
        )
        self.assertEqual(
            machine["cuda_nvrtc_sha256"],
            "000ca6278ba8b32a7dac383eb7440929c5a09095b43dd5f2df3911f63520db70",
        )
        self.assertEqual(machine["cuda_nvrtc_runtime_version"], [12, 2])
        self.assertEqual(
            machine["cuda_nvrtc_builtins_resolved_path"],
            "/home/lestat/vendor/cuda-12.2.2/targets/x86_64-linux/lib/"
            "libnvrtc-builtins.so.12.2.140",
        )
        self.assertEqual(
            machine["cuda_nvrtc_builtins_sha256"],
            "968ebb00640e461f587ad96d01735ac85bf4b2ab4d1cb35b3b489c3cf2cc7f18",
        )
        self.assertEqual(
            machine["cuda_nvvm_resolved_path"],
            "/home/lestat/vendor/cuda-12.2.2/nvvm/lib64/libnvvm.so.4.0.0",
        )
        self.assertEqual(
            machine["cuda_nvvm_sha256"],
            "b69eaddcce6a063361f2d172ed535c3d6f7ae494a40c6ffdb7de024f89dbf80a",
        )
        self.assertEqual(
            machine["cuda_libdevice_resolved_path"],
            "/home/lestat/vendor/cuda-12.2.2/nvvm/libdevice/libdevice.10.bc",
        )
        self.assertEqual(
            machine["cuda_libdevice_sha256"],
            "5c9f80bf689d5d0e67dabf914a2a865a3d8b8c5ff86b86c46f63c3bb067ca523",
        )
        self.assertEqual(
            machine["cuda_toolkit_resolved_path"],
            "/home/lestat/vendor/cuda-12.2.2",
        )
        self.assertFalse(machine["modern_rtx_execution_authorized"])
        self.assertFalse(machine["pod_used"])
        self.assertEqual(HOME.HOME_MACHINE_AUTHORITY, machine)
        runner_machine = dict(RUNNER_MODULE.HOME_MACHINE_AUTHORITY)
        runner_machine["receipt_sha256"] = _digest(runner_machine)
        self.assertEqual(runner_machine, machine)
        self.assertIn('choices=("61",)', source)
        self.assertIn("Goal5790 rejects non-Home GPU identity", source)
        self.assertIn("Goal5790 CUDA host compiler identity drift", source)
        self.assertIn('env["LD_PRELOAD"] = str(expected_authority[', source)
        self.assertIn('env["CUDA_HOME"] = str(expected_authority[', source)
        self.assertIn('env["CUDA_PATH"] = str(expected_authority[', source)
        self.assertIn('env.pop("NUMBA_CUDA_NVVM", None)', source)
        self.assertIn('"RTDL_V4_FORMAL_LEAF_CACHE"', source)
        self.assertIn("goal5790_home_ptx_producer_probe.py", source)
        self.assertIn("loaded_nvrtc_family_paths", source)
        self.assertIn("Goal5790 loaded NVRTC-family path drift", source)
        self.assertIn('Path("/usr/bin/strace")', source)
        self.assertIn("_verify_strace_producer_opens", source)
        self.assertIn(
            'str(strace_path), "-f", "-s", "4096", "-e"', source)
        runner_source = RUNNER.read_text(encoding="utf-8")
        self.assertIn('os.environ.get("LD_PRELOAD")', runner_source)
        self.assertIn("observe_ptx_producers()", runner_source)
        self.assertIn("cuda_nvrtc_builtins_resolved_path", runner_source)
        self.assertIn("rejects ambient formal-leaf cache authority", runner_source)
        observation = {
            "schema": "rtdl.goal5790.home_ptx_producer_observation.v1",
            "cuda_home": machine["cuda_toolkit_resolved_path"],
            "cuda_path": machine["cuda_toolkit_resolved_path"],
            "numba_selected_nvvm_by": "CUDA_HOME",
            "numba_selected_nvvm_path": machine["cuda_nvvm_resolved_path"],
            "numba_selected_nvvm_sha256": machine["cuda_nvvm_sha256"],
            "numba_selected_libdevice_by": "CUDA_HOME",
            "numba_selected_libdevice_path": machine[
                "cuda_libdevice_resolved_path"],
            "numba_selected_libdevice_sha256": machine["cuda_libdevice_sha256"],
            "loaded_nvvm_paths": [machine["cuda_nvvm_resolved_path"]],
            "cupy_nvrtc_runtime_version": [12, 2],
            "loaded_nvrtc_family_paths": sorted([
                machine["cuda_nvrtc_resolved_path"],
                machine["cuda_nvrtc_builtins_resolved_path"],
            ]),
            "nvrtc_probe_output": 5790,
            "elapsed_values_recorded": False,
            "application_input_used": False,
            "registered_performance_timing_created": False,
        }
        CLEAN_MODULE._verify_home_nvrtc_runtime(machine, observation)
        with self.assertRaisesRegex(RuntimeError, "runtime version drift"):
            forged = dict(observation)
            forged["cupy_nvrtc_runtime_version"] = [12, 6]
            CLEAN_MODULE._verify_home_nvrtc_runtime(machine, forged)
        with self.assertRaisesRegex(RuntimeError, "loaded NVRTC-family path drift"):
            forged = dict(observation)
            forged["loaded_nvrtc_family_paths"] = ["/wheel/libnvrtc.so.12"]
            CLEAN_MODULE._verify_home_nvrtc_runtime(machine, forged)
        with self.assertRaisesRegex(RuntimeError, "producer selector drift"):
            forged = dict(observation)
            forged["cuda_home"] = "/usr/local/cuda"
            CLEAN_MODULE._verify_home_nvrtc_runtime(machine, forged)
        self.assertIn("CXX_OPTIX={nvcc} -ccbin {host_compiler}", source)
        self.assertNotIn(
            'home_machine_authority["cuda_host_compiler_path"])).resolve()',
            source,
        )
        admitted = CLEAN_MODULE._verify_home_authority(
            HOME_MACHINE,
            "NVIDIA GeForce GTX 1070, "
            "GPU-8e04454e-c177-6e5b-3f43-e676980ecdfa, 580.126.09, 6.1",
        )
        self.assertEqual(admitted, machine)
        with self.assertRaisesRegex(RuntimeError, "rejects non-Home GPU"):
            CLEAN_MODULE._verify_home_authority(
                HOME_MACHINE,
                "NVIDIA RTX 4000 Ada Generation, GPU-attacker, 580.126.09, 8.9",
            )


if __name__ == "__main__":
    unittest.main()
