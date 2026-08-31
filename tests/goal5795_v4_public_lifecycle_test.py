from __future__ import annotations

import hashlib
import inspect
import json
import os
from pathlib import Path
import pickle
from types import SimpleNamespace
import tempfile
import threading
import unittest
from unittest.mock import patch

from rtdsl.v4 import (
    AnyHitProtocolProof,
    BoundedRelationBatch,
    BoundedRelationProtocol,
    BoundedRelationStaticInput,
    CompilerProtocolProjection,
    ProtocolLifecycleError,
    TriangleReductionBatch,
    TriangleReductionMode,
    TriangleReductionProtocol,
    TriangleReductionStaticInput,
    V4Target,
    V4Toolchain,
    compile_protocol_program,
    materialize_protocol_program,
    standard_protocol_physical_plan,
)
from rtdsl.v4_callback_lifecycle import _load_exact_native_library


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _value_sha(value) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


class _FakeOwner:
    def __init__(self, identity, family):
        self.identity = identity
        self.family = family
        self.prepare_seconds = 0.125
        self.close_count = 0
        self.execute_count = 0
        self.bad_identity = False
        self.bad_status = False
        self.bad_output_digest = False
        self.bad_receipt = False
        self.bad_receipt_digest = False

    @property
    def lifecycle_receipt(self):
        return {"execution_count": self.execute_count}

    def execute(self, value, **kwargs):
        self.execute_count += 1
        output = ((100, 10), (101, 20)) if self.family == "bounded" else 16
        output_sha = _value_sha(output)
        reported_output_sha = (
            _sha("wrong-output") if self.bad_output_digest else output_sha)
        status = ({
            "first_error_claimed": 1 if self.bad_status else 0,
            "error_code": 7 if self.bad_status else 0,
        },)
        receipt = {
            "physical_executor_classification": "optix_traversal_observed",
            "provider_library_sha256": self.identity.native_library_sha256,
            "output_digest": reported_output_sha,
            "route_identity": (
                "wrong-route" if self.bad_receipt else
                ("v4_callback_ir:custom_aabb_bounded_relation_v1"
                 if self.family == "bounded" else
                 "v4_builtin_triangle_callback_ir:checked_reduction_v1")),
            "expected_program_observed_at_receipt_edge": True,
        }
        receipt["receipt_sha256"] = _value_sha(receipt)
        if self.bad_receipt_digest:
            receipt["receipt_sha256"] = _sha("wrong-receipt")
        common = dict(
            launch_status=status,
            role_counters=(1, 1, 1, 1, 1, 1, 1),
            traversal_receipt=receipt,
            output_sha256=reported_output_sha,
            composed_ptx_sha256=(
                _sha("wrong-ptx") if self.bad_identity
                else self.identity.composed_ptx_sha256),
            native_library_sha256=self.identity.native_library_sha256,
        )
        if self.family == "bounded":
            return SimpleNamespace(
                rows=((100, 10), (101, 20)),
                raw_rows=((101, 20), (100, 10)),
                raw_event_count=2,
                duplicate_count=0,
                **common,
            )
        return SimpleNamespace(
            reduced_output=16,
            per_ray_u64=(3, 2, 0, 1),
            raw_reducer_rows=(
                {"launch_index": 0, "count": 3, "query.weight": 1},
                {"launch_index": 1, "count": 2, "query.weight": 3},
                {"launch_index": 2, "count": 0, "query.weight": 5},
                {"launch_index": 3, "count": 1, "query.weight": 7},
            ),
            **common,
        )

    def close(self):
        self.close_count += 1


class Goal5795PublicLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.native = root / "librtdl_optix.so"
        self.native.write_bytes(b"goal5795-test-native")
        self.optix_include = root / "optix"
        self.cuda_include = root / "cuda"
        self.optix_include.mkdir()
        self.cuda_include.mkdir()
        self.target = V4Target.from_native(
            self.native,
            optix_sdk="test",
            compute_capability=(8, 9),
        )
        self.toolchain = V4Toolchain(
            compute_capability=(8, 9),
            optix_include=self.optix_include,
            cuda_include=self.cuda_include,
            expected_python_version="3.11.0",
            expected_numba_version="test",
            expected_numpy_version="test",
        )
        bounded_plan = standard_protocol_physical_plan(BoundedRelationProtocol(8))
        triangle_plan = standard_protocol_physical_plan(TriangleReductionProtocol())
        self.bounded_proof = AnyHitProtocolProof(
            bounded_plan.callback_ir_sha256,
            bounded_plan.effect_digest,
            _sha("machine-checked-bounded-order-independence"),
            "external_machine_checked_order_independence_v1")
        self.triangle_proof = AnyHitProtocolProof(
            triangle_plan.callback_ir_sha256,
            triangle_plan.effect_digest,
            _sha("machine-checked-triangle-order-independence"),
            "external_machine_checked_order_independence_v1")

    def tearDown(self):
        self.temp.cleanup()

    def _fake_executable(self, label):
        return SimpleNamespace(
            executable_sha256=_sha(label + ":executable"),
            composed=SimpleNamespace(ptx_sha256=_sha(label + ":ptx")),
        )

    def _materialize_bounded(self):
        protocol = BoundedRelationProtocol(capacity=8)
        program = compile_protocol_program(
            protocol,
            physical_plan=standard_protocol_physical_plan(protocol),
            any_hit_proof=self.bounded_proof)
        executable = self._fake_executable("bounded")
        with patch(
            "rtdsl.v4_bounded_relation_optix_compiler."
            "compile_verified_bounded_relation_executable",
            return_value=(executable, "bounded compiler log"),
        ) as compiler:
            materialized = materialize_protocol_program(
                program, target=self.target, toolchain=self.toolchain)
        self.assertEqual(compiler.call_count, 1)
        return program, materialized

    def _materialize_triangle(self):
        protocol = TriangleReductionProtocol(
            TriangleReductionMode.WEIGHTED_HIT_COUNT)
        program = compile_protocol_program(
            protocol,
            physical_plan=standard_protocol_physical_plan(protocol),
            any_hit_proof=self.triangle_proof,
        )
        executable = self._fake_executable("triangle")
        with patch(
            "rtdsl.v4_triangle_reduction_optix_compiler."
            "compile_verified_triangle_reduction_executable",
            return_value=(executable, "triangle compiler log"),
        ) as compiler:
            materialized = materialize_protocol_program(
                program, target=self.target, toolchain=self.toolchain)
        self.assertEqual(compiler.call_count, 1)
        return program, materialized

    def _prepare_bounded(self):
        _program, materialized = self._materialize_bounded()
        holder = {}

        def prepare(_backend, _static, _target, _library):
            owner = _FakeOwner(materialized.identity, "bounded")
            holder["owner"] = owner
            return owner

        with patch(
            "rtdsl.v4_callback_lifecycle._load_exact_native_library",
            return_value=object(),
        ), patch(
            "rtdsl.v4_callback_lifecycle._prepare_bounded_relation_backend",
            side_effect=prepare,
        ):
            prepared = materialized.prepare(BoundedRelationStaticInput((
                (0.0, 0.0, 4.0, 1.0, 10),
                (0.0, 0.0, 1.0, 4.0, 20),
            )))
        return materialized, prepared, holder["owner"]

    def _prepare_triangle(self):
        _program, materialized = self._materialize_triangle()
        holder = {}

        def prepare(_backend, _static, _target, _library):
            owner = _FakeOwner(materialized.identity, "triangle")
            holder["owner"] = owner
            return owner

        static = TriangleReductionStaticInput(
            vertices=((0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0)),
            triangles=((0, 1, 2),),
            primitive_metadata={},
            event_capacity=1,
        )
        with patch(
            "rtdsl.v4_callback_lifecycle._load_exact_native_library",
            return_value=object(),
        ), patch(
            "rtdsl.v4_callback_lifecycle._prepare_triangle_reduction_backend",
            side_effect=prepare,
        ):
            prepared = materialized.prepare(static)
        return materialized, prepared, holder["owner"]

    def test_verified_programs_share_public_cpu_and_target_identity(self):
        bounded, materialized = self._materialize_bounded()
        self.assertEqual(
            bounded.identity.callback_ir_sha256,
            bounded.callback.ir_sha256,
        )
        self.assertEqual(
            materialized.identity.program.identity_sha256,
            bounded.identity.identity_sha256,
        )
        self.assertEqual(
            materialized.identity.native_library_sha256,
            hashlib.sha256(self.native.read_bytes()).hexdigest(),
        )
        self.assertGreaterEqual(materialized.materialize_seconds, 0.0)

    def test_independent_compiler_projection_rejects_each_mechanism_before_load(self):
        """The integrated gate must not be a declaration self-comparison."""

        from rtdsl import v4_callback_lifecycle as lifecycle

        original = lifecycle._compiled_protocol_projection
        cases = (
            (
                "CP001_ROLE_EFFECT_MISMATCH",
                lambda value: value["role_effects"].update({"any_hit": []}),
            ),
            (
                "CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH",
                lambda value: value["attribute_abi_ownership"].update(
                    {"attr0": "primitive_index_u32"}),
            ),
            (
                "CP003_PHYSICAL_BINDING_MISMATCH",
                lambda value: value["physical_bindings"].update(
                    {"geometry_family": "builtin_triangle"}),
            ),
            (
                "CP004_CONTINUATION_STATUS_MISMATCH",
                lambda value: value.update(
                    {"continuation_policy": "ALLOW_PARTIAL"}),
            ),
            (
                "CP005_EXECUTABLE_IDENTITY_MISMATCH",
                lambda value: value.update(
                    {"actual_executable_sha256": _sha("substituted-executable")}),
            ),
        )

        def projection_from_mapping(value):
            return CompilerProtocolProjection(
                family=value["family"],
                task_semantics_sha256=value["task_semantics_sha256"],
                role_effects=tuple(
                    (key, tuple(item))
                    for key, item in sorted(value["role_effects"].items())),
                attribute_abi_ownership=tuple(sorted(
                    value["attribute_abi_ownership"].items())),
                physical_bindings=tuple(sorted(
                    value["physical_bindings"].items())),
                continuation_policy=value["continuation_policy"],
                actual_executable_sha256=value["actual_executable_sha256"],
                generated_device_source_sha256=(
                    value["generated_device_source_sha256"]),
                generated_host_source_sha256=(
                    value["generated_host_source_sha256"]),
            )

        for reason, mutate in cases:
            with self.subTest(reason=reason):
                def corrupted(*args, **kwargs):
                    value = original(*args, **kwargs).to_mapping()
                    value.pop("projection_sha256")
                    mutate(value)
                    return projection_from_mapping(value)

                with patch.object(
                    lifecycle, "_compiled_protocol_projection",
                    side_effect=corrupted,
                ), patch.object(lifecycle, "_load_exact_native_library") as loader:
                    with self.assertRaisesRegex(
                        ProtocolLifecycleError, reason,
                    ):
                        self._materialize_bounded()
                loader.assert_not_called()
    def test_bounded_public_execute_and_idempotent_close(self):
        materialized, prepared, owner = self._prepare_bounded()
        self.assertEqual(materialized.state, "prepared")
        batch = BoundedRelationBatch(
            source_boxes=(
                (2.0, 0.25, 3.0, 0.75, 100),
                (0.25, 2.0, 0.75, 3.0, 101),
            ),
            expected_rows=((100, 10), (101, 20)),
        )
        result = prepared.execute(batch)
        self.assertEqual(result.output, ((100, 10), (101, 20)))
        self.assertEqual(result.executable_identity, materialized.identity)
        receipt = prepared.lifecycle_receipt
        self.assertEqual(receipt["execution_count"], 1)
        self.assertEqual(receipt["protocol_contract_verdict"], "ACCEPT")
        self.assertEqual(
            receipt["protocol_contract_decision_sha256"],
            materialized.protocol_contract_decision.to_mapping()["decision_sha256"],
        )
        prepared.close()
        prepared.close()
        self.assertEqual(owner.close_count, 1)
        with self.assertRaisesRegex(ProtocolLifecycleError, "PL026_USE_AFTER_CLOSE"):
            prepared.execute(batch)

    def test_triangle_public_execute_returns_checked_reduction(self):
        _materialized, prepared, owner = self._prepare_triangle()
        batch = TriangleReductionBatch(
            queries=(
                ((0.1, 0.1, 0.0), (0.0, 0.0, 1.0), 4.0),
                ((0.2, 0.2, 0.0), (0.0, 0.0, 1.0), 4.0),
                ((2.0, 2.0, 0.0), (0.0, 0.0, 1.0), 4.0),
                ((3.1, 0.1, 0.0), (0.0, 0.0, 1.0), 4.0),
            ),
            query_metadata={"query.weight": (1, 3, 5, 7)},
        )
        first = prepared.execute(batch)
        second = prepared.execute(batch)
        self.assertEqual(first.output, 16)
        self.assertEqual(first.details["per_ray_u64"], (3, 2, 0, 1))
        self.assertEqual(second.output, 16)
        self.assertEqual(owner.execute_count, 2)
        prepared.close()

    def test_materialized_executable_is_single_use_and_nonsserializable(self):
        materialized, prepared, _owner = self._prepare_bounded()
        with self.assertRaisesRegex(ProtocolLifecycleError, "PL020_NONSERIALIZABLE"):
            pickle.dumps(materialized)
        with self.assertRaisesRegex(ProtocolLifecycleError, "PL020_NONSERIALIZABLE"):
            pickle.dumps(prepared)
        with self.assertRaisesRegex(ProtocolLifecycleError, "PL024_EXECUTABLE_CONSUMED"):
            materialized.prepare(BoundedRelationStaticInput(()))
        prepared.close()

    def test_cross_thread_and_reentrant_use_fail_closed(self):
        _materialized, prepared, _owner = self._prepare_bounded()
        errors = []

        def cross_thread():
            try:
                prepared.execute(BoundedRelationBatch(()))
            except Exception as error:
                errors.append(str(error))

        thread = threading.Thread(target=cross_thread)
        thread.start()
        thread.join()
        self.assertEqual(len(errors), 1)
        self.assertIn("PL022_THREAD_BOUNDARY", errors[0])
        prepared._active.acquire()
        try:
            with self.assertRaisesRegex(ProtocolLifecycleError, "PL023_REENTRANT"):
                prepared.close()
        finally:
            prepared._active.release()
        prepared.close()

    def test_foreign_process_identity_and_task_name_dispatch_are_absent(self):
        _materialized, prepared, _owner = self._prepare_bounded()
        original_pid = prepared._pid
        prepared._pid = original_pid + 1
        try:
            with self.assertRaisesRegex(
                ProtocolLifecycleError, "PL021_PROCESS_BOUNDARY",
            ):
                prepared.execute(BoundedRelationBatch(()))
        finally:
            prepared._pid = original_pid
        prepared.close()

        parameters = inspect.signature(compile_protocol_program).parameters
        self.assertNotIn("task_name", parameters)
        self.assertNotIn("app_name", parameters)
        source = Path(inspect.getsourcefile(compile_protocol_program)).read_text(
            encoding="utf-8").lower()
        for registry_identity in (
            "rayjoin-paper", "triangle-counting-paper", "paper_app",
            "task_name", "app_registry",
        ):
            self.assertNotIn(registry_identity, source)

    def test_identity_or_device_status_mismatch_never_returns_result(self):
        _materialized, prepared, owner = self._prepare_bounded()
        batch = BoundedRelationBatch(())
        owner.bad_identity = True
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL028_EXECUTION_IDENTITY_MISMATCH",
        ):
            prepared.execute(batch)
        owner.bad_identity = False
        owner.bad_status = True
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL029_DEVICE_STATUS_INVALID",
        ):
            prepared.execute(batch)
        owner.bad_status = False
        owner.bad_output_digest = True
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL031_OUTPUT_IDENTITY_MISMATCH",
        ):
            prepared.execute(batch)
        owner.bad_output_digest = False
        owner.bad_receipt = True
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL032_TRAVERSAL_RECEIPT_INVALID",
        ):
            prepared.execute(batch)
        owner.bad_receipt = False
        owner.bad_receipt_digest = True
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL032_TRAVERSAL_RECEIPT_INVALID",
        ):
            prepared.execute(batch)
        prepared.close()

    def test_target_bytes_and_compute_capability_are_bound(self):
        tampered = self.native.with_name("tampered.so")
        tampered.write_bytes(b"different-native")
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL009_NATIVE_IDENTITY_MISMATCH",
        ):
            V4Target(
                profile=self.target.profile,
                native_library_path=tampered,
            )
        protocol = BoundedRelationProtocol(8)
        program = compile_protocol_program(
            protocol,
            physical_plan=standard_protocol_physical_plan(protocol),
            any_hit_proof=self.bounded_proof)
        wrong = V4Toolchain(
            compute_capability=(6, 1),
            optix_include=self.optix_include,
            cuda_include=self.cuda_include,
            expected_python_version="3.11.0",
            expected_numba_version="test",
            expected_numpy_version="test",
        )
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL017_TARGET_TOOLCHAIN_MISMATCH",
        ):
            materialize_protocol_program(
                program, target=self.target, toolchain=wrong)

    def test_unrecognized_or_decorative_proof_kind_is_rejected(self):
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL003_PROOF_KIND_INVALID",
        ):
            AnyHitProtocolProof(
                _sha("callback"), _sha("effects"), _sha("decorative"),
                "external-reviewed-proof")

    def test_physical_plan_is_public_identity_and_mutations_reject(self):
        import dataclasses

        protocol = BoundedRelationProtocol(8)
        plan = standard_protocol_physical_plan(protocol)
        self.assertEqual(plan.family, protocol.family)
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL034_PHYSICAL_PLAN_MISMATCH",
        ):
            compile_protocol_program(
                protocol,
                physical_plan=dataclasses.replace(
                    plan, output_contract="scalar_count"),
                any_hit_proof=self.bounded_proof,
            )

        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL035_PROOF_PROGRAM_MISMATCH",
        ):
            compile_protocol_program(
                protocol,
                physical_plan=plan,
                any_hit_proof=self.triangle_proof,
            )

    def test_native_dependency_load_failure_has_public_diagnostic(self):
        with patch(
            "rtdsl.optix_runtime._ensure_cuda_driver_initialized",
        ), patch(
            "rtdsl.v4_callback_lifecycle.ctypes.CDLL",
            side_effect=OSError("missing declared dependency"),
        ):
            with self.assertRaisesRegex(
                ProtocolLifecycleError, "PL030_NATIVE_LOAD_FAILED",
            ):
                _load_exact_native_library(self.target)


if __name__ == "__main__":
    unittest.main()
