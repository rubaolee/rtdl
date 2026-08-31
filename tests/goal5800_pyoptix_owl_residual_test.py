from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PYOPTIX = (
    ROOT / "experiments" / "goal5800_pyoptix_owl"
    / "pyoptix_idiomatic_arm.py"
)
PYOPTIX_BASELINE = (
    ROOT / "experiments" / "goal5796_matched" / "pyoptix_baseline.py"
)
OWL = ROOT / "experiments" / "goal5800_pyoptix_owl" / "owl_residual"
OWL_BUNDLE = (
    ROOT / "history" / "internal_docs"
    / "goal5800_owl_untimed_functional_bundle_v5_20260824.tar.gz"
)
THREE_ARM = (
    ROOT / "history" / "internal_docs"
    / "goal5800_three_arm_responsibility_and_executable_residual_result_v6_20260824.json"
)


class Goal5800PyOptixOwlResidualTest(unittest.TestCase):
    @staticmethod
    def load_pyoptix_arm():
        spec = importlib.util.spec_from_file_location(
            "goal5800_pyoptix_idiomatic_arm_test", PYOPTIX)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load Goal5800 PyOptiX arm")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_pyoptix_source_parses_and_plan_is_untimed(self) -> None:
        ast.parse(PYOPTIX.read_text(encoding="utf-8"))
        completed = subprocess.run(
            [sys.executable, str(PYOPTIX), "--plan-only"],
            check=True,
            capture_output=True,
            text=True,
        )
        plan = json.loads(completed.stdout)
        self.assertEqual(plan["status"], "PASS__SOURCE_PLAN_ONLY__GPU_NOT_IMPORTED")
        self.assertEqual(plan["registered_performance_timing_count"], 0)
        self.assertFalse(plan["performance_claimed"])
        self.assertEqual(plan["relation_launch_count"], 2)
        self.assertEqual(plan["triangle_launch_count"], 1)
        self.assertTrue(plan["persistent_stream_per_prepared_owner"])
        self.assertTrue(
            plan["persistent_launch_param_device_buffer_per_prepared_owner"])
        self.assertTrue(plan["same_stream_async_param_h2d_and_launch"])
        self.assertFalse(plan["current_stream_preexecute_sync"])
        self.assertFalse(plan["sync_after_every_launch"])
        self.assertEqual(plan["relation_explicit_sync_count_per_execute"], 2)
        self.assertEqual(plan["triangle_explicit_sync_count_per_execute"], 2)
        self.assertEqual(plan["relation_async_h2d_count_per_execute"], 2)
        self.assertEqual(plan["triangle_async_h2d_count_per_execute"], 1)
        self.assertEqual(plan["relation_async_d2h_count_per_execute"], 2)
        self.assertEqual(plan["triangle_async_d2h_count_per_execute"], 3)
        self.assertEqual(plan["relation_blocking_d2h_count_per_execute"], 0)
        self.assertEqual(plan["triangle_blocking_d2h_count_per_execute"], 0)
        self.assertEqual(plan["relation_total_host_blocking_count_per_execute"], 2)
        self.assertEqual(plan["triangle_total_host_blocking_count_per_execute"], 2)

    def test_pyoptix_uses_bulk_materialization_and_status_first(self) -> None:
        text = PYOPTIX.read_text(encoding="utf-8")
        self.assertIn(".reshape((-1, 2)).tolist()", text)
        self.assertIn("sorted(set(map(tuple, raw)))", text)
        self.assertIn("per_ray = self.h_per_ray.tolist()", text)
        self.assertNotIn("[int(value)" + " for value in cp.asnumpy", text)
        self.assertNotIn("for row" + " in raw", text)
        self.assertNotIn("cp.asnumpy(", text)
        self.assertLess(text.index("status = int(self.h_status[0])"),
                        text.index("per_ray = self.h_per_ray.tolist()"))

    def test_prepared_launch_owns_stream_params_and_counts_real_calls(self) -> None:
        baseline = PYOPTIX_BASELINE.read_text(encoding="utf-8")
        idiomatic = PYOPTIX.read_text(encoding="utf-8")
        self.assertIn("class PreparedLaunch:", baseline)
        self.assertIn("self._raw_stream = cp.cuda.Stream(non_blocking=True)", baseline)
        self.assertIn("self.device_params = cp.cuda.alloc(PARAM_DTYPE.itemsize)",
                      baseline)
        self.assertIn("self.device_params.copy_from_async(", baseline)
        self.assertIn("self.pipeline, self.stream.ptr, self.device_params.ptr",
                      baseline)
        self.assertNotIn("cp.asnumpy(array, stream=self.stream, blocking=True)",
                         baseline)
        for counter in (
            "prepare_device_allocation_call_count",
            "prepare_h2d_call_count",
            "prepare_pinned_host_allocation_call_count",
            "prepare_stream_creation_count",
            "execute_device_allocation_call_count",
            "execute_pinned_host_allocation_call_count",
            "execute_async_h2d_call_count",
            "execute_async_d2h_call_count",
            "execute_blocking_d2h_call_count",
            "execute_device_zero_fill_call_count",
            "execute_explicit_stream_sync_call_count",
            "execute_launch_call_count",
        ):
            self.assertIn(counter, baseline + idiomatic)
        self.assertNotIn("get_current_stream().synchronize()", idiomatic)
        self.assertNotIn("b.launch(", idiomatic)
        self.assertIn("copy_to_host_async(", baseline)
        self.assertIn("alloc_pinned_memory", baseline)
        self.assertIn("event=\"status_ready_sync\"", idiomatic)
        self.assertIn("event=\"output_ready_sync\"", idiomatic)
        self.assertGreaterEqual(
            idiomatic.count("stream=self.launcher.stream"), 3)
        self.assertIn("stream_ptr = 0 if stream is None else stream.ptr", baseline)
        self.assertIn("require_execution_contract(", idiomatic)
        self.assertIn("execute_device_allocation_call_count", baseline)
        self.assertIn("execute_stream_creation_call_count", baseline)
        self.assertIn("execute_stream_destroy_call_count", baseline)
        self.assertIn("cp.cuda.runtime.memsetAsync(", baseline)
        self.assertNotIn("array.fill(0)\n                _bump(", baseline)
        self.assertIn("cp.cuda.set_allocator(observed_allocator)", baseline)
        self.assertIn("cp.asnumpy = observed_asnumpy", baseline)
        self.assertIn("unauthorized_direct_stream_sync_count", baseline)

    def test_source_boundary_rejects_direct_allocation_and_sync_mutants(self) -> None:
        arm = self.load_pyoptix_arm()
        original = PYOPTIX.read_text(encoding="utf-8")
        marker = "        b = self.b\n        before = dict(self.operation_counts)"
        self.assertIn(marker, original)
        mutants = (
            original.replace(
                marker,
                "        b = self.b\n        b.cp.empty(1)\n"
                "        before = dict(self.operation_counts)",
                1,
            ),
            original.replace(
                marker,
                "        b = self.b\n"
                "        self.launcher.stream.synchronize()\n"
                "        before = dict(self.operation_counts)",
                1,
            ),
            original.replace(
                marker,
                "        b = self.b\n        self.cheat()\n"
                "        before = dict(self.operation_counts)",
                1,
            ),
        )
        for index, mutant in enumerate(mutants):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "mutant.py"
                path.write_text(mutant, encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    arm.validate_execute_source_boundary(path)

    def test_prepared_event_order_and_bytes_are_explicit(self) -> None:
        text = PYOPTIX.read_text(encoding="utf-8")
        relation_events = (
            'events=("rows_reset", "control_reset")',
            'h2d_event=f"params{index}_h2d"',
            'launch_event=f"launch{index}"',
            'event="control_d2h"',
            'event="status_ready_sync"',
            'event="rows_d2h"',
            'event="output_ready_sync"',
        )
        positions = [text.index(event) for event in relation_events]
        self.assertEqual(positions, sorted(positions))
        for field in (
            "control_d2h_bytes", "output_d2h_bytes",
            "rows_reset_bytes", "control_reset_bytes",
            "status_d2h_bytes", "per_ray_d2h_bytes",
            "weighted_d2h_bytes", "per_ray_reset_bytes",
            "weighted_reset_bytes", "status_reset_bytes",
            "total_host_blocking_count", "operation_order",
        ):
            self.assertIn(field, text)
        for order in (
            '"params0_h2d", "launch0", "params1_h2d", "launch1"',
            '"control_d2h", "status_ready_sync"',
            '"rows_d2h", "output_ready_sync"',
            '"params_h2d", "launch", "control_d2h"',
            '"status_ready_sync", "per_ray_d2h", "weighted_d2h"',
        ):
            self.assertIn(order, text)

    def test_operation_contract_rejects_count_or_order_drift(self) -> None:
        arm = self.load_pyoptix_arm()
        class FakeBaseline:
            @staticmethod
            def new_operation_counts():
                return {"a": 0, "b": 0}

        expected = arm.exact_counts(FakeBaseline, a=1)
        good = {
            "execute_operation_counts": expected,
            "operation_order": ["first", "second"],
        }
        arm.require_execution_contract(
            good, expected_counts=expected,
            expected_order=["first", "second"])
        with self.assertRaises(RuntimeError):
            arm.require_execution_contract(
                {**good, "execute_operation_counts": {"a": 1, "b": 1}},
                expected_counts=expected,
                expected_order=["first", "second"])
        with self.assertRaises(RuntimeError):
            arm.require_execution_contract(
                good, expected_counts=expected,
                expected_order=["second", "first"])

    def test_same_owner_repeats_and_lifecycle_keepalive_are_structural(self) -> None:
        text = PYOPTIX.read_text(encoding="utf-8")
        self.assertEqual(text.count("relation_owner.execute()"), 2)
        self.assertEqual(text.count("triangle_owner.execute()"), 2)
        self.assertIn("pipeline_keepalive=relation_groups", text)
        self.assertIn("sbt_keepalive=relation_sbt_keepalive", text)
        self.assertIn("pipeline_keepalive=triangle_groups", text)
        self.assertIn("sbt_keepalive=triangle_sbt_keepalive", text)
        self.assertIn("relation_owner.close()", text)
        self.assertIn("triangle_owner.close()", text)
        self.assertIn("if self.closed:", text)
        self.assertIn("initial_repeat_exact", text)

    def test_executed_dependency_custody_includes_extension_and_maps(self) -> None:
        text = PYOPTIX.read_text(encoding="utf-8")
        self.assertIn('sys.modules.get("optix._optix")', text)
        self.assertIn('Path("/proc/self/maps")', text)
        self.assertIn('"address_fields_recorded": False', text)
        self.assertIn('"loaded_optix_extension"', text)
        self.assertIn('"loaded_shared_library_manifest"', text)
        self.assertIn('"pyoptix_source_authority_identity"', text)
        self.assertNotIn('"pyoptix_installed_from_source_identity"', text)
        self.assertIn("--pyoptix-wheel-build-receipt", text)
        self.assertIn("--pyoptix-clean-install-receipt", text)
        self.assertIn(
            "rtdl.goal5800.pyoptix_clean_wheel_build_receipt.v1", text)
        self.assertIn(
            "rtdl.goal5800.pyoptix_clean_install_receipt.v1", text)
        self.assertIn('"operation_ledger": operation_ledger', text)
        self.assertIn(
            "TASK_OWNER_CONSTRUCTION_AND_EXECUTE__SOURCE_OBSERVABLE_WRAPPERS__",
            text,
        )
        self.assertIn('"source_observable_wrapper_counter_keys"', text)
        self.assertIn('"complete_driver_operation_observation_claimed": False', text)
        self.assertIn('"owner_close_operation_counts_claimed": False', text)

    def test_frozen_owl_bundle_identity_is_exact_and_self_contained(self) -> None:
        self.assertEqual(
            hashlib.sha256(OWL_BUNDLE.read_bytes()).hexdigest(),
            "2840ae5fff2200c76c18664176b46f6b179c1be20f0216bd7237e28181d16993",
        )
        files: dict[str, bytes] = {}
        with tarfile.open(OWL_BUNDLE, "r:gz") as archive:
            for member in archive.getmembers():
                parts = Path(member.name).parts
                self.assertFalse(Path(member.name).is_absolute())
                self.assertNotIn("..", parts)
                self.assertFalse(member.issym() or member.islnk())
                if not member.isfile():
                    continue
                self.assertNotIn(member.name, files)
                stream = archive.extractfile(member)
                self.assertIsNotNone(stream)
                files[member.name] = stream.read()
        prefix = "goal5800_owl_source/"
        manifest_name = prefix + "GOAL5800_SOURCE_MANIFEST.json"
        manifest = json.loads(files[manifest_name])
        source_files = {
            name.removeprefix(prefix): value
            for name, value in files.items()
            if name.startswith(prefix) and name != manifest_name
        }
        rows = manifest["files"]
        self.assertEqual(len(rows), manifest["file_count_excluding_manifest"])
        self.assertEqual(set(source_files), {row["path"] for row in rows})
        for row in rows:
            value = source_files[row["path"]]
            self.assertEqual(len(value), row["bytes"])
            self.assertEqual(hashlib.sha256(value).hexdigest(), row["sha256"])
        stage = json.loads(source_files["GOAL5800_STAGE_IDENTITY.json"])
        self.assertEqual(
            stage["owl_upstream"]["commit"],
            "df7390b16bce5244b7352ca6d3e320f838297072",
        )
        self.assertEqual(
            stage["owl_upstream"]["tree"],
            "c31d2c7510050fc3d57a4c4e0a4d4d84bc7b03ff",
        )
        self.assertTrue(stage["owl_upstream"]["working_tree_clean_before_archive"])

    def test_owl_host_freezes_valid_and_all_five_wrong_outputs(self) -> None:
        host = (OWL / "hostCode.cpp").read_text(encoding="utf-8")
        device = (OWL / "deviceCode.cu").read_text(encoding="utf-8")
        for anchor in (
            "{100, 10}, {101, 20}",
            "{100, 0}, {101, 1}",
            "{100, 20}, {101, 10}",
            "std::vector<uint64_t>({3, 2, 0, 1})",
            "std::vector<uint64_t>({1, 1, 0, 1})",
            "wrong_effect.weighted_sum == 11",
            "std::vector<uint64_t>({6, 4, 0, 2})",
            "wrong_identity.weighted_sum == 32",
            "overflow.raw_count == 8",
            "overflow.rows.size() == 7",
        ):
            self.assertIn(anchor, host)
        for program in (
            "TriangleCount", "TriangleTerminate", "TriangleDouble",
            "RelationValid", "RelationWrongAbi", "RelationSwappedRayGen",
        ):
            self.assertIn(program, device)
        self.assertIn("cudaGetLastError()", host)
        self.assertIn("registered_performance_timing_count", host)

    def test_owl_validation_overlay_is_narrow_and_explicit(self) -> None:
        patch = (OWL / "owl_validation_mode_all.patch").read_text(
            encoding="utf-8")
        self.assertIn("OPTIX_DEVICE_CONTEXT_VALIDATION_MODE_ALL", patch)
        self.assertIn("optixDeviceContextCreate(cudaContext, &options", patch)
        self.assertNotIn("owl/Context.cpp", patch)
        self.assertNotIn("owl/RayGen.cpp", patch)

    def test_no_clock_api_in_owl_harness(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (OWL / "hostCode.cpp", OWL / "deviceCode.cu")
        )
        for forbidden in ("chrono", "clock_gettime", "QueryPerformanceCounter",
                          "cudaEventElapsedTime"):
            self.assertNotIn(forbidden, combined)

    def test_three_arm_successor_is_immutable_source_backed_and_narrow(self) -> None:
        result = json.loads(THREE_ARM.read_bytes())
        self.assertEqual(
            result["arm_definition"]["nvidia_owl"],
            "Pinned OWL + diagnostic-only validation overlay; OWL owns mature "
            "host composition while the application supplies device programs.",
        )
        self.assertEqual(
            result["executed_summary"],
            {
                "raw_pyoptix_executed_protocol_invalid_count": 5,
                "raw_pyoptix_exact_silent_wrong_output_count": 4,
                "raw_pyoptix_status_before_consume_violation_count": 1,
                "owl_executed_protocol_invalid_count": 5,
                "owl_exact_silent_wrong_output_count": 4,
                "owl_status_before_consume_violation_count": 1,
                "rtdl_launch_prevented_count": 5,
                "owl_goal5799_minimum_required": 3,
                "owl_minimum_met": True,
                "owl_nearby_valid_control_exact": True,
            },
        )
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn("Pinned public NVIDIA OWL", serialized)
        self.assertNotIn('"path": "src/rtdsl/', serialized)
        self.assertNotIn('"path": "experiments/goal5796_matched/', serialized)
        self.assertNotIn(".tmp_goal5796_upstream_20260823", serialized)
        self.assertEqual(
            result["idiomatic_pyoptix_successor"]["status"],
            "PASS__UNTIMED_GPU_EXECUTED__IDENTITY_CLOSED",
        )
        self.assertEqual(
            result["idiomatic_pyoptix_successor"]
            ["registered_performance_timing_count"], 0)
        self.assertTrue(
            result["immutable_source_authorities"]
            ["all_emitted_source_references_rehashed"]
        )
        self.assertTrue(
            result["immutable_source_authorities"]
            ["all_emitted_line_references_verified"]
        )


if __name__ == "__main__":
    unittest.main()
