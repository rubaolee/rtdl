from __future__ import annotations

import base64
from copy import deepcopy
import ctypes
import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from rtdsl.v4_rtdlexe import (
    InstalledRTDLDeployment,
    RTDLExecutableBuildRoots,
    RTDLExecutableError,
    build_rtdlexe,
    install_rtdlexe_deployment,
    load_rtdlexe,
)
from scripts.goal5801_rtdlexe_trust import create_root, freeze
from rtdsl import physical_execution_provenance as provenance
import rtdsl.v4_rtdlexe as runtime_module


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _native_descriptor(
        family="custom_aabb_bounded_relation_v1", *, online_monitor=True):
    bounded = family == "custom_aabb_bounded_relation_v1"
    return {
        "schema": "rtdl.v4.rtdlexe.native_producer_descriptor.v1",
        "family": family,
        "native_abi": (
            ("rtdl.v4.prepared_bounded_relation_callback.v9" if bounded
             else "rtdl.v4.prepared_triangle_reduction_callback.v9")
            if online_monitor else
            ("rtdl.v4.prepared_bounded_relation_callback.v5" if bounded
             else "rtdl.v4.prepared_triangle_reduction_callback.v5")),
        "program_bundle": ("v4_custom_aabb_bounded_relation_composed" if bounded
                           else "v4_builtin_triangle_checked_reduction_composed"),
        "module_compile": {"max_register_count": 0, "optimization_level": 0,
                           "debug_level": 0},
        "pipeline_compile": {"uses_motion_blur": 0, "traversable_graph_flags": 1,
                             "payload_values": 3 if bounded else 2,
                             "attribute_values": 1 if bounded else 2,
                             "exception_flags": 0, "launch_params_symbol": "params",
                             "primitive_type_flags": 1 if bounded else 2},
        "pipeline_link": {"max_trace_depth": 1, "direct_callable_depth": 0,
                          "continuation_callable_depth": 0,
                          "max_traversable_graph_depth": 1},
        "program_groups": {"count": 3, "raygen": "raygen", "miss": "miss",
                           "intersection": "intersection" if bounded else None,
                           "any_hit": "any_hit", "closest_hit": "closest" if bounded else None},
        "sbt": {"header_bytes": 32, "alignment": 16, "raygen_record_bytes": 32,
                "miss_record_bytes": 32, "hitgroup_record_bytes": 32,
                "raygen_record_count": 1, "miss_record_count": 1,
                "hitgroup_record_count": 1},
        "launch_parameters": {"struct_bytes": 128,
                              "layout": ["traversable:0:8", "status:120:8"]},
        "status": {"device_row_bytes": runtime_module.ctypes.sizeof(
                       runtime_module._DeviceStatusRow),
                   "product_summary_bytes": runtime_module.ctypes.sizeof(
                       runtime_module._ProductStatusSummary),
                   "product_summary_schema_version": 2,
                   "fast_control_bytes": (
                       (28 if bounded else 88) if online_monitor
                       else (16 if bounded else 4)),
                   "fast_host_blocking_boundaries": 2,
                   "fast_host_blocking_boundary_scope":
                       "status_and_output__dynamic_setup_separate",
                   "fast_receipt_bytes": runtime_module.ctypes.sizeof(
                       runtime_module._FastPathReceipt),
                   "fast_receipt_schema_version": 2,
                   "fast_receipt_semantic_field_count": 27,
                   "fast_receipt_field_offsets": dict(
                       runtime_module._FAST_PATH_RECEIPT_FIELD_OFFSETS),
                   "optix_validation_mode": "OFF",
                   "fast_semantic_compaction_algorithm": (
                       "u64_atomiccas_linear_probe_v1" if bounded else "NONE"),
                   "fast_semantic_compaction_launch_count": 1 if bounded else 0,
                   "fast_callback_status_kernel_launch_count": (
                       0 if online_monitor else (5 if bounded else 3)),
                   "fast_checked_product_kernel_launch_count": (
                       0 if online_monitor or bounded else 2),
                   "fast_compact_control_finalizer_kernel_launch_count": (
                       0 if online_monitor else 1),
                   "fast_total_auxiliary_cuda_kernel_launch_count": (
                       (1 if bounded else 0) if online_monitor
                       else (7 if bounded else 6)),
                   "fast_execution_parameter_h2d_copy_call_count": 2 if bounded else 1,
                   "fast_execution_parameter_h2d_bytes": (
                       (240 if bounded else 224) if online_monitor
                       else (224 if bounded else 200)),
                   "fast_stream_ordered_memset_call_count": (
                       (4 if bounded else 2) if online_monitor
                       else (9 if bounded else 4)),
                   "fast_status_d2h_copy_call_count": 1,
                   "fast_dynamic_setup_separately_accounted": True,
                   "fast_role_counters_materialized": False,
                   "diagnostic_role_counters_materialized": True,
                   "fast_status_before_output": True,
                   "required_invocation_mask": (1 << 1) | (1 << 6),
                   "terminal_invocation_mask": ((1 << 4) | (1 << 5)) if bounded else (1 << 5),
                   "success_transfer_is_constant_size": True},
        "product_output": ({"schema": "rtdl.v4.bounded_relation_rows.v1",
                            "row_bytes": 8, "capacity_bounded": True} if bounded else {
            "schema": "rtdl.v4.checked_u64_device_product_sum.v1", "scalar_bytes": 8,
            "checked_result_bytes": runtime_module.ctypes.sizeof(
                runtime_module._CheckedProductResult),
            "per_ray_detail_d2h_on_product_success": False,
            "event_row_detail_d2h_on_product_success": False,
            "unit_or_u64_multiplier": True}),
    }


class _MappingObject:
    def __init__(self, value):
        self.value = value

    def to_mapping(self):
        return deepcopy(self.value)


class _DictObject:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return deepcopy(self.value)


def _sealed(value: dict[str, object], key: str) -> dict[str, object]:
    return {**value, key: _digest(value)}


def _candidate(label: str, deployment_id: str):
    family = "custom_aabb_bounded_relation_v1"
    ptx = f".version 7.8\n.target sm_89\n.address_size 64\n// {label}\n"
    ptx_sha = hashlib.sha256(ptx.encode()).hexdigest()
    generated_executable_sha = _sha(label + ":generated-executable")
    task_sha = _sha(label + ":task")
    declaration = _sealed({
        "schema": "rtdl.v4.protocol_contract_declaration.v1",
        "family": family,
        "task_semantics_sha256": task_sha,
        "role_effects": {"finalize": ["output"]},
        "attribute_abi_ownership": {"payload0": "finalize"},
        "physical_bindings": {"geometry": "custom_aabb"},
        "continuation_policy": "SINGLE_TRACE_STATUS_REQUIRED",
        "checked_executable_sha256": generated_executable_sha,
    }, "contract_sha256")
    projection = _sealed({
        "schema": "rtdl.v4.compiler_protocol_projection.v1",
        "family": family,
        "task_semantics_sha256": task_sha,
        "role_effects": {"finalize": ["output"]},
        "attribute_abi_ownership": {"payload0": "finalize"},
        "physical_bindings": {"geometry": "custom_aabb"},
        "continuation_policy": "SINGLE_TRACE_STATUS_REQUIRED",
        "actual_executable_sha256": generated_executable_sha,
        "generated_device_source_sha256": ptx_sha,
        "generated_host_source_sha256": _sha(label + ":host"),
    }, "projection_sha256")
    decision = _sealed({
        "schema": "rtdl.v4.protocol_contract_decision.v1",
        "verdict": "ACCEPT", "findings": [],
        "contract_sha256": declaration["contract_sha256"],
        "projection_sha256": projection["projection_sha256"],
        "executable_capability_issued": False,
    }, "decision_sha256")
    abi_body = {
        "schema_id": "rtdl.v4.callback_abi",
        "schema_version": "1",
        "callback_ir_sha256": _sha(label + ":callback-ir"),
        "callback_effect_digest": _sha(label + ":effects"),
        "any_hit_proof_sha256": None,
        "any_hit_proof_kind": None,
        "any_hit_delivery_contract": None,
        "runtime_status_codes": {"OK": 0},
        "roles": [{"role": "finalize", "effects": [{"kind": "output"}]}],
    }
    abi = {**abi_body, "abi_sha256": _digest(abi_body)}
    composed = SimpleNamespace(
        ptx=ptx, ptx_sha256=ptx_sha, ptx_version="7.8", ptx_target="sm_89",
        address_size="64", leaf_bindings=(("finalize", _sha(label + ":leaf-ptx")),),
    )
    wrapper = SimpleNamespace(
        source_sha256=_sha(label + ":wrapper"), schema="wrapper-v1",
        physical_template="custom-aabb-v1", role_symbols=(("finalize", "rtdl_finalize"),),
    )
    executable = SimpleNamespace(
        generated_leaves=(SimpleNamespace(
            role=SimpleNamespace(value="finalize"),
            generated_source_sha256=_sha(label + ":leaf-source")),),
        compiled_leaves=(SimpleNamespace(
            role="finalize", ptx_sha256=_sha(label + ":leaf-ptx")),),
        composed=composed, wrapper=wrapper, compiler_options=("--use_fast_math=false",),
    )
    identity_value = {
        "program_identity_sha256": _sha(label + ":program"),
        "target_sha256": _sha("target"),
        "physical_schema_sha256": _sha(label + ":physical"),
        "contract_sha256": declaration["contract_sha256"],
        "abi_sha256": abi["abi_sha256"],
        "generated_executable_sha256": generated_executable_sha,
        "composed_ptx_sha256": ptx_sha,
        "native_library_sha256": _sha("native"),
    }
    identity = _DictObject(identity_value)
    identity.program = SimpleNamespace(family=family)
    identity.identity_sha256 = _digest(identity_value)
    target = SimpleNamespace(profile=SimpleNamespace(
        target_sha256=_sha("target"), native_sha256=_sha("native"),
        provider="optix", optix_sdk="8.1.0", supports_custom_aabb=True,
        supports_builtin_triangle=True, max_graph_depth=1,
    ))
    toolchain = SimpleNamespace(
        compute_capability=(8, 9), expected_python_version="3.11.9",
        expected_numba_version="0.61.0", expected_numpy_version="2.1.0",
    )
    materialized = SimpleNamespace(
        protocol_contract_decision=_MappingObject(decision), identity=identity,
        _target=target, _toolchain=toolchain,
        _program=SimpleNamespace(protocol=SimpleNamespace(capacity=8, minimum_overlap_f32=0.0)),
        _backend={
            "executable": executable, "abi": _DictObject(abi),
            "contract": _DictObject({"contract_sha256": declaration["contract_sha256"]}),
            "authority": SimpleNamespace(),
        },
    )
    return materialized, declaration, projection


class Goal5801RTDLExecutableRuntimeTest(unittest.TestCase):
    def test_fast_receipt_ctypes_layout_and_first_reuse_failure_contract(self):
        receipt_type = runtime_module._FastPathReceipt
        self.assertEqual(ctypes.sizeof(receipt_type), 128)
        self.assertEqual({
            field: getattr(receipt_type, field).offset
            for field, _ctype in receipt_type._fields_
        }, runtime_module._FAST_PATH_RECEIPT_FIELD_OFFSETS)
        self.assertEqual(runtime_module._FAST_PATH_RECEIPT_FIELD_OFFSETS, {
            "schema_version": 0,
            "optix_launch_count": 4,
            "host_blocking_boundary_count": 8,
            "control_d2h_bytes": 12,
            "output_d2h_bytes": 16,
            "status_before_output": 24,
            "output_d2h_after_status_failure": 28,
            "role_counters_materialized": 32,
            "prepared_input_reused": 36,
            "dynamic_device_upload_call_count": 40,
            "dynamic_accel_build_count": 44,
            "dynamic_explicit_sync_count": 48,
            "dynamic_blocking_upload_call_count": 52,
            "dynamic_device_upload_bytes": 56,
            "dynamic_input_generation": 64,
            "semantic_compaction_launch_count": 72,
            "semantic_compaction_key_capacity": 76,
            "semantic_compaction_scratch_bytes": 80,
            "callback_status_kernel_launch_count": 88,
            "checked_product_kernel_launch_count": 92,
            "compact_control_finalizer_kernel_launch_count": 96,
            "total_auxiliary_cuda_kernel_launch_count": 100,
            "execution_parameter_h2d_bytes": 104,
            "execution_parameter_h2d_copy_call_count": 112,
            "stream_ordered_memset_call_count": 116,
            "status_d2h_copy_call_count": 120,
            "output_d2h_copy_call_count": 124,
        })

        descriptor = _native_descriptor(online_monitor=False)
        runtime_module._validate_native_producer_descriptor(
            descriptor,
            family="custom_aabb_bounded_relation_v1",
            native_abi="rtdl.v4.prepared_bounded_relation_callback.v5",
            program_bundle="v4_custom_aabb_bounded_relation_composed",
        )
        # A same-size native/Python ABI can still be incompatible when two
        # equally sized fields move.  Loading must reject that before execute.
        swapped = deepcopy(descriptor)
        offsets = swapped["status"]["fast_receipt_field_offsets"]
        offsets["schema_version"], offsets["optix_launch_count"] = (
            offsets["optix_launch_count"], offsets["schema_version"])
        with self.assertRaisesRegex(
                RTDLExecutableError, "RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH"):
            runtime_module._validate_native_producer_descriptor(
                swapped,
                family="custom_aabb_bounded_relation_v1",
                native_abi="rtdl.v4.prepared_bounded_relation_callback.v5",
                program_bundle="v4_custom_aabb_bounded_relation_composed",
            )

        def make_receipt(*, family, reused, success=True):
            receipt = receipt_type()
            receipt.schema_version = 2
            receipt.optix_launch_count = 2 if family == runtime_module._BOUNDED else 1
            receipt.host_blocking_boundary_count = 2 if success else 1
            receipt.control_d2h_bytes = 16 if family == runtime_module._BOUNDED else 4
            receipt.output_d2h_bytes = (
                32768 if family == runtime_module._BOUNDED else 8
            ) if success else 0
            receipt.status_before_output = 1
            receipt.role_counters_materialized = 0
            receipt.prepared_input_reused = int(reused)
            if not reused:
                receipt.dynamic_device_upload_call_count = (
                    2 if family == runtime_module._BOUNDED else 8)
                receipt.dynamic_device_upload_bytes = (
                    4096 if family == runtime_module._BOUNDED else 1024)
                receipt.dynamic_accel_build_count = int(
                    family == runtime_module._BOUNDED)
            receipt.dynamic_input_generation = 1
            if family == runtime_module._BOUNDED:
                receipt.semantic_compaction_launch_count = 1
                receipt.semantic_compaction_key_capacity = 8192
                receipt.semantic_compaction_scratch_bytes = 98312
                receipt.callback_status_kernel_launch_count = 5
                receipt.compact_control_finalizer_kernel_launch_count = 1
                receipt.total_auxiliary_cuda_kernel_launch_count = 7
            else:
                receipt.callback_status_kernel_launch_count = 3
                receipt.checked_product_kernel_launch_count = 2
                receipt.compact_control_finalizer_kernel_launch_count = 1
                receipt.total_auxiliary_cuda_kernel_launch_count = 6
            receipt.execution_parameter_h2d_bytes = (
                224 if family == runtime_module._BOUNDED else 200)
            receipt.execution_parameter_h2d_copy_call_count = (
                2 if family == runtime_module._BOUNDED else 1)
            receipt.stream_ordered_memset_call_count = (
                9 if family == runtime_module._BOUNDED else 4)
            receipt.status_d2h_copy_call_count = 1
            receipt.output_d2h_copy_call_count = int(success)
            return receipt

        for family, output_bytes in (
                (runtime_module._BOUNDED, 32768),
                (runtime_module._TRIANGLE, 8)):
            with self.subTest(family=family, lane="first"):
                first = runtime_module._validate_fast_operation_receipt(
                    make_receipt(family=family, reused=False),
                    family=family, compact_status=0,
                    expected_output_d2h_bytes=output_bytes,
                    expected_prepared_input_reused=False,
                    expected_semantic_capacity=(
                        4096 if family == runtime_module._BOUNDED else None))
                self.assertEqual(first["host_blocking_boundary_count"], 2)
                self.assertEqual(first["dynamic_blocking_upload_call_count"], 0)
                self.assertEqual(first["dynamic_explicit_sync_count"], 0)
            with self.subTest(family=family, lane="reuse"):
                reuse = runtime_module._validate_fast_operation_receipt(
                    make_receipt(family=family, reused=True),
                    family=family, compact_status=0,
                    expected_output_d2h_bytes=output_bytes,
                    expected_prepared_input_reused=True,
                    expected_semantic_capacity=(
                        4096 if family == runtime_module._BOUNDED else None))
                self.assertEqual(reuse["dynamic_device_upload_call_count"], 0)
            with self.subTest(family=family, lane="failure"):
                failed = runtime_module._validate_fast_operation_receipt(
                    make_receipt(family=family, reused=False, success=False),
                    family=family, compact_status=17,
                    expected_output_d2h_bytes=output_bytes,
                    expected_prepared_input_reused=False,
                    expected_semantic_capacity=(
                        4096 if family == runtime_module._BOUNDED else None))
                self.assertEqual(failed["host_blocking_boundary_count"], 1)
                self.assertEqual(failed["output_d2h_bytes"], 0)

    def test_relation_async_setup_has_no_allocator_or_retirement_after_enqueue(self):
        source = (ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text(
            encoding="utf-8")
        begin = source.index("static void execute_v4_prepared_bounded_relation_callback(")
        end = source.index(
            "static void execute_v4_prepared_bounded_relation_callback_summary(", begin)
        body = source[begin:end]
        enqueue = body.index("upload_async(\n                    next_device->ptr")
        first_control_reset = body.index(
            "cuMemsetD8Async(\n            prepared->fast_control->ptr", enqueue)
        between = body[enqueue:first_control_reset]
        self.assertNotIn("cuMemAlloc", between)
        self.assertNotIn("ensure_v4_relation_", between)
        self.assertNotIn(".reset()", between)
        self.assertLess(
            body.index("retired_source_accel = std::move"), enqueue)
        self.assertIn(
            "(void)cuStreamSynchronize(execution_stream);", between)
        # The only synchronization in this range is the explicit failure-path
        # drain inside catch; a successful receipt never passes through it.
        self.assertEqual(between.count("cuStreamSynchronize"), 1)

    @classmethod
    def setUpClass(cls):
        cls.class_temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.class_temp.name)
        cls.private = cls.root / "TEST_ONLY_private.json"
        cls.public = cls.root / "TEST_ONLY_public.json"
        create_root(
            private_path=cls.private, public_path=cls.public,
            key_id="TEST_ONLY_goal5801_fixture", bits=2048,
        )
        cls.artifacts = cls.root / "artifacts"
        cls.artifacts.mkdir()
        cls.authority_a = cls.root / "a.authority.json"
        cls.authority_b = cls.root / "b.authority.json"
        cls.built_a = cls._build("A", "slot-A", cls.authority_a)
        cls.built_b = cls._build("B", "slot-B", cls.authority_b)
        cls.package_a = cls.root / "package-a.json"
        cls.package_ab = cls.root / "package-ab.json"
        cls.head_a = cls.root / "head-a.json"
        cls.head_ab = cls.root / "head-ab.json"
        freeze(private_path=cls.private, root_path=cls.public,
               authority_path=cls.authority_a, output_path=cls.package_a,
               head_output_path=cls.head_a,
               previous_path=None)
        freeze(private_path=cls.private, root_path=cls.public,
               authority_path=cls.authority_b, output_path=cls.package_ab,
               head_output_path=cls.head_ab,
               previous_path=cls.package_a)

    @classmethod
    def tearDownClass(cls):
        cls.class_temp.cleanup()

    @classmethod
    def _build(cls, label, deployment_id, authority_path, *, native_descriptor=None):
        materialized, declaration, projection = _candidate(label, deployment_id)
        roots = RTDLExecutableBuildRoots(
            llvmlite_version="0.44.0", cuda_toolkit_version="12.8",
            link_options=("max_trace_depth=1", "debug=none"),
        )
        with patch(
            "rtdsl.v4_callback_lifecycle._declared_protocol_contract",
            return_value=_MappingObject(declaration),
        ), patch(
            "rtdsl.v4_callback_lifecycle._compiled_protocol_projection",
            return_value=_MappingObject(projection),
        ), patch.object(
            runtime_module, "_build_native_producer_descriptor",
            return_value=native_descriptor or _native_descriptor(),
        ):
            return build_rtdlexe(
                materialized, artifact_directory=cls.artifacts,
                authority_path=authority_path, build_roots=roots,
                deployment_id=deployment_id,
            )

    def test_build_dataflow_carries_full_provider_and_runtime_schema(self):
        artifact = json.loads(self.built_a.artifact_path.read_text(encoding="utf-8"))
        product = artifact["product_projection"]
        provider = product["provider_key"]
        execution = product["execution_schema"]
        self.assertEqual(provider["llvmlite_version"], "0.44.0")
        self.assertEqual(provider["cuda_toolkit_version"], "12.8")
        self.assertEqual(provider["generated_source_sha256_by_role"][0][0], "finalize")
        self.assertEqual(provider["leaf_ptx_sha256_by_role"][0][0], "finalize")
        self.assertEqual(set(execution["producer_inputs"]), {
            "module", "program_group", "pipeline", "sbt", "launch_parameters", "status"})
        declaration_contract = artifact["protocol_declaration"]["contract_sha256"]
        self.assertEqual(
            {row["contract_sha256"] for row in execution["producer_inputs"].values()},
            {declaration_contract},
        )
        self.assertFalse(execution["actual_runtime_handle_bytes_bound"])

    def test_execution_schema_binds_public_declaration_not_backend_leaf_contract(self):
        materialized, declaration, projection = _candidate("distinct", "slot-distinct")
        materialized._backend["contract"] = _DictObject({
            "contract_sha256": _sha("distinct-backend-leaf-contract")})
        authority = self.root / "distinct.authority.json"
        with patch(
            "rtdsl.v4_callback_lifecycle._declared_protocol_contract",
            return_value=_MappingObject(declaration),
        ), patch(
            "rtdsl.v4_callback_lifecycle._compiled_protocol_projection",
            return_value=_MappingObject(projection),
        ), patch.object(
            runtime_module, "_build_native_producer_descriptor",
            return_value=_native_descriptor(),
        ):
            built = build_rtdlexe(
                materialized, artifact_directory=self.artifacts,
                authority_path=authority,
                build_roots=RTDLExecutableBuildRoots(
                    llvmlite_version="0.44.0", cuda_toolkit_version="12.8",
                    link_options=("max_trace_depth=1", "debug=none")),
                deployment_id="slot-distinct")
        artifact = json.loads(built.artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(
            {row["contract_sha256"] for row in artifact["product_projection"]
             ["execution_schema"]["producer_inputs"].values()},
            {declaration["contract_sha256"]},
        )

    def test_public_surface_and_native_product_spec_are_not_decorative(self):
        import rtdsl
        for name in ("BoundedRelationBatch", "BoundedRelationStaticInput",
                     "TriangleReductionBatch", "TriangleReductionStaticInput",
                     "RTDLExecutionResult"):
            self.assertIs(getattr(rtdsl, name), getattr(runtime_module, name))
        for explicit, target in (
            ("RTDLExecutableBoundedRelationBatch", "BoundedRelationBatch"),
            ("RTDLExecutableBoundedRelationStaticInput", "BoundedRelationStaticInput"),
            ("RTDLExecutableTriangleReductionBatch", "TriangleReductionBatch"),
            ("RTDLExecutableTriangleReductionStaticInput", "TriangleReductionStaticInput"),
        ):
            self.assertIs(getattr(rtdsl, explicit), getattr(runtime_module, target))
        core = (ROOT / "src/native/optix/rtdl_optix_core.cpp").read_text(
            encoding="utf-8")
        poc = (ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text(
            encoding="utf-8")
        reducer = (ROOT / "src/native/optix/rtdl_optix_cuda_helpers.cu").read_text(
            encoding="utf-8")
        self.assertIn("const RtdlexeNativeProducerSpec& spec", core)
        self.assertIn("pco.numPayloadValues = spec.max_payload_values", core)
        self.assertIn("plo.maxTraceDepth = spec.max_trace_depth", core)
        self.assertIn("v4_rtdlexe_triangle_producer_spec());", poc)
        self.assertIn("v4_rtdlexe_bounded_producer_spec());", poc)
        self.assertIn("producer_spec.required_invocation_mask", poc)
        self.assertIn("(mask & ~((1u << 7u) - 1u)) != 0u", reducer)
        self.assertIn("bounds_phase != (intersection_count != 0u)", reducer)
        runtime_source = (ROOT / "src/rtdsl/v4_rtdlexe.py").read_text(
            encoding="utf-8")
        capability_body = runtime_source.split(
            "def _initialize_cuda_and_get_capability", 1)[1].split(
                "def _load_native_library", 1)[0]
        self.assertNotIn("cuDevicePrimaryCtxRetain", capability_body)
        self.assertNotIn("cuCtxSetCurrent", capability_body)
        context_guard = core.split("class ScopedRtdlCudaContext", 1)[1].split(
            "// ---------- SBT record types", 1)[0]
        self.assertIn("catch (...) {", context_guard)
        self.assertIn("(void)cuCtxSetCurrent(prior_);", context_guard)
        self.assertLess(
            context_guard.index("(void)cuCtxSetCurrent(prior_);"),
            context_guard.index("throw;"),
        )
        init_context = core.split("static void init_optix_context()", 1)[1].split(
            "static OptixDeviceContext get_optix_context()", 1)[0]
        self.assertIn("OptixDeviceContext created = nullptr;", init_context)
        self.assertIn(
            "opts.validationMode = OPTIX_DEVICE_CONTEXT_VALIDATION_MODE_OFF;",
            init_context,
        )
        self.assertNotIn(
            "OPTIX_DEVICE_CONTEXT_VALIDATION_MODE_ALL", init_context)
        self.assertIn("optixDeviceContextDestroy(created)", init_context)
        self.assertIn("cuDevicePrimaryCtxRelease(dev)", init_context)
        self.assertIn("cuCtxSetCurrent(prior)", init_context)
        init_catch = init_context.split("catch (...) {", 1)[1].split(
            "throw;", 1)[0]
        self.assertLess(
            init_catch.index("cuCtxSetCurrent(prior)"),
            init_catch.index("cuDevicePrimaryCtxRelease(dev)"),
        )
        self.assertGreater(
            init_context.index("g_cuda_primary_ctx = retained;"),
            init_context.index("catch (...)"),
        )

    def test_bounded_relation_cache_reuse_is_native_two_phase_committed(self):
        poc = (ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text(
            encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8")
        runtime = (ROOT / "src/rtdsl/v4_rtdlexe.py").read_text(
            encoding="utf-8")
        execute_native = poc.split(
            "static void execute_v4_prepared_bounded_relation_callback(", 1)[1].split(
                "static void execute_v4_prepared_bounded_relation_callback_summary(", 1)[0]
        self.assertIn("!prepared->source_cache_committed", execute_native)
        self.assertIn("prepared->source_cache_committed = false;", execute_native)
        self.assertIn("++prepared->source_cache_build_count;", execute_native)
        # The only remaining occurrence is the now-unused helper declaration;
        # a false reuse request can no longer silently take the equality fast path.
        self.assertEqual(poc.count("v4_relation_boxes_equal("), 1)
        self.assertIn(
            "rtdl_optix_v4_prepared_bounded_relation_source_cache_build_count_v1",
            api)
        self.assertIn(
            "rtdl_optix_v4_commit_prepared_bounded_relation_source_cache_v2", api)
        self.assertIn(
            "rtdl_optix_v4_prepared_bounded_relation_source_cache_digest_v1", api)
        execute_public = runtime.split(
            "class _PreparedBoundedOwner:", 1)[1].split(
                "class _PreparedTriangleOwner:", 1)[0]
        self.assertIn("RX044_NATIVE_REUSE_MISMATCH", execute_public)
        self.assertLess(
            execute_public.index("RX043_ORACLE_MISMATCH"),
            execute_public.index("self._commit_source_cache(batch._device_input_sha256)"),
        )
        self.assertLess(
            execute_public.index("receipt = audit.finish("),
            execute_public.index("self._commit_source_cache(batch._device_input_sha256)"),
        )
        self.assertIn("except BaseException:", execute_public)
        self.assertIn(
            "self._source_cache_reusable(",
            execute_public)
        self.assertIn("source_cache_digest_valid", poc)
        owner = runtime_module._PreparedBoundedOwner.__new__(
            runtime_module._PreparedBoundedOwner)
        owner._last_batch_key = ("a" * 64, 1, 16, 4)
        owner._last_source_arrays = (object(), object())
        owner._native_source_cache_digest = lambda: "a" * 64
        self.assertTrue(owner._source_cache_reusable(
            ("a" * 64, 1, 16, 4), "a" * 64))
        # Same count/shape but different bytes is not reusable.
        self.assertFalse(owner._source_cache_reusable(
            ("b" * 64, 1, 16, 4), "b" * 64))
        # Deterministic interrupt window: Python still names A while native
        # has already committed B.  The exact native digest prevents reuse.
        owner._native_source_cache_digest = lambda: "b" * 64
        self.assertFalse(owner._source_cache_reusable(
            ("a" * 64, 1, 16, 4), "a" * 64))
        triangle_public = runtime.split(
            "class _PreparedTriangleOwner:", 1)[1].split(
            "def _initialize_cuda_and_get_capability", 1)[0]
        self.assertIn("except BaseException:", triangle_public)

    def test_triangle_cache_is_digest_committed_and_interrupt_safe(self):
        poc = (ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text(
            encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8")
        self.assertIn("query_cache_committed", poc)
        self.assertIn("query_cache_digest_valid", poc)
        self.assertIn(
            "rtdl_optix_v4_commit_prepared_triangle_reduction_cache_v1", api)
        self.assertIn(
            "rtdl_optix_v4_prepared_triangle_reduction_cache_digest_v1", api)

        relation_execute = poc.split(
            "static void execute_v4_prepared_bounded_relation_callback(", 1
        )[1].split(
            "static void execute_v4_prepared_bounded_relation_callback_summary(", 1
        )[0]
        self.assertIn(
            "2ull * prepared->semantic_capacity", relation_execute)
        self.assertNotIn(
            "2ull * (prepared->semantic_capacity + 1ull)", relation_execute)

        def make_batch(x_value):
            return runtime_module.TriangleReductionBatch(
                queries=(((x_value, 0, 0), (0, 0, 1), 2),))

        batch_a = make_batch(0.0)
        batch_b = make_batch(1.0)
        owner = runtime_module._PreparedTriangleOwner.__new__(
            runtime_module._PreparedTriangleOwner)
        owner._token = 1
        owner._event_capacity = 1
        owner._library = object()
        owner._native_sha = "a" * 64
        owner._ptx_sha = "b" * 64
        owner._mode = "all_hit_count"
        owner._artifact_identity = "c" * 64
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._active = threading.Lock()
        owner._last_fast_operation_receipt = None

        def batch_key(batch):
            return (
                batch._device_input_sha256, len(batch.queries),
                len(batch._packed_origins_f32),
                len(batch._packed_directions_f32),
                len(batch._packed_tmax_f32),
                len(batch._packed_weights_u64 or b""),
            )

        owner._last_batch_key = batch_key(batch_a)
        owner._last_query_arrays = (object(), object(), object(), object())
        native = {
            "digest": batch_a._device_input_sha256,
            "pending": None,
            "successors": [
                ("B", batch_b._device_input_sha256, 222),
                ("A", batch_a._device_input_sha256, 111),
            ],
            "value": 111,
            "reuse_flags": [],
            "generation": 1,
        }

        def fake_execute(*args):
            reused = int(args[5])
            native["reuse_flags"].append(reused)
            if not reused:
                _label, digest, value = native["successors"].pop(0)
                native["pending"] = digest
                native["digest"] = None
                native["value"] = value
                native["generation"] += 1
            ctypes.cast(
                args[9], ctypes.POINTER(ctypes.c_uint64))[0] = native["value"]
            ctypes.cast(
                args[10], ctypes.POINTER(ctypes.c_uint32))[0] = 0
            receipt = ctypes.cast(
                args[11], ctypes.POINTER(runtime_module._FastPathReceipt))[0]
            receipt.schema_version = 2
            receipt.optix_launch_count = 1
            receipt.host_blocking_boundary_count = 2
            receipt.control_d2h_bytes = 4
            receipt.output_d2h_bytes = 8
            receipt.status_before_output = 1
            receipt.prepared_input_reused = reused
            receipt.dynamic_input_generation = native["generation"]
            receipt.callback_status_kernel_launch_count = 3
            receipt.checked_product_kernel_launch_count = 2
            receipt.compact_control_finalizer_kernel_launch_count = 1
            receipt.total_auxiliary_cuda_kernel_launch_count = 6
            receipt.execution_parameter_h2d_bytes = 200
            receipt.execution_parameter_h2d_copy_call_count = 1
            receipt.stream_ordered_memset_call_count = 4
            receipt.status_d2h_copy_call_count = 1
            receipt.output_d2h_copy_call_count = 1
            if not reused:
                receipt.dynamic_device_upload_call_count = 7
                receipt.dynamic_device_upload_bytes = 28
            return 0

        def commit(digest):
            self.assertEqual(digest, native["pending"])
            native["digest"] = digest
            native["pending"] = None

        class FakeAudit:
            def finish(self, **_kwargs):
                return {"receipt": "complete"}

            def abort(self):
                return None

        owner._execute_fast = fake_execute
        owner._execute_diagnostic = object()
        owner._commit_query_cache = commit
        owner._native_query_cache_digest = lambda: native["digest"]
        source_lines, source_start = inspect.getsourcelines(
            runtime_module._PreparedTriangleOwner.execute)
        publish_line = source_start + next(
            index for index, line in enumerate(source_lines)
            if "self._last_batch_key = batch_key" in line)

        def interrupt_before_publish(frame, event, _argument):
            if frame.f_code is runtime_module._PreparedTriangleOwner.execute.__code__ \
                    and event == "line" and frame.f_lineno == publish_line:
                raise KeyboardInterrupt("injected after native commit")
            return interrupt_before_publish

        with patch.object(runtime_module, "_open_audit", return_value=FakeAudit()), \
                patch.object(runtime_module, "_validate_product_summary",
                             return_value=({"ok": True}, ())):
            sys.settrace(interrupt_before_publish)
            try:
                with self.assertRaisesRegex(
                        KeyboardInterrupt, "injected after native commit"):
                    owner.execute(batch_b, diagnostics=False)
            finally:
                sys.settrace(None)
            self.assertIsNone(owner._last_batch_key)
            self.assertIsNone(owner._last_query_arrays)
            self.assertEqual(native["digest"], batch_b._device_input_sha256)
            output, *_rest = owner.execute(batch_a, diagnostics=False)
        self.assertEqual(output, 111)
        self.assertEqual(native["reuse_flags"], [0, 0])
        self.assertEqual(native["digest"], batch_a._device_input_sha256)

    def test_trust_documents_are_each_parsed_and_hashed_from_one_read(self):
        paths = {
            self.public.resolve(), self.head_ab.resolve(), self.package_ab.resolve(),
        }
        payloads = {path: path.read_bytes() for path in paths}
        calls = {path: 0 for path in paths}
        original = runtime_module._read_regular_bytes_once

        def one_read(path, *, code):
            resolved = path.resolve()
            if resolved in calls:
                calls[resolved] += 1
                if calls[resolved] != 1:
                    raise AssertionError(f"trust path reread: {resolved}")
                return payloads[resolved]
            return original(path, code=code)

        with patch.object(
                runtime_module, "_read_regular_bytes_once", side_effect=one_read):
            deployment = install_rtdlexe_deployment(
                trust_root_path=self.public, trust_head_path=self.head_ab,
                trust_package_path=self.package_ab, deployment_id="slot-A")
        self.assertEqual(deployment.deployment_id, "slot-A")
        self.assertEqual(set(calls.values()), {1})

    def test_authority_artifact_swap_between_hash_and_parse_cannot_change_runtime(self):
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab, deployment_id="slot-A")
        authority_path = self.authority_a.resolve()
        artifact_path = self.built_a.artifact_path.resolve()
        authority_a = authority_path.read_bytes()
        artifact_a = artifact_path.read_bytes()

        artifact_b_object = json.loads(artifact_a)
        artifact_b_object["product_projection"]["runtime"]["capacity"] = 1
        artifact_b = _canonical(artifact_b_object) + b"\n"
        authority_b_object = json.loads(authority_a)
        authority_b_object["product_projection_sha256"] = _digest(
            artifact_b_object["product_projection"])
        authority_body = dict(authority_b_object)
        authority_body.pop("authority_seal")
        authority_b_object["authority_seal"] = hashlib.sha256(
            runtime_module._AUTHORITY_DOMAIN + _canonical(authority_body)
        ).hexdigest()
        authority_b = _canonical(authority_b_object) + b"\n"

        calls = {authority_path: 0, artifact_path: 0}
        original = runtime_module._read_regular_bytes_once

        def alternating(path, *, code):
            resolved = path.resolve()
            if resolved == authority_path:
                calls[resolved] += 1
                return authority_a if calls[resolved] == 1 else authority_b
            if resolved == artifact_path:
                calls[resolved] += 1
                return artifact_a if calls[resolved] == 1 else artifact_b
            return original(path, code=code)

        with patch.object(
                runtime_module, "_read_regular_bytes_once",
                side_effect=alternating):
            loaded = load_rtdlexe(
                artifact_path, authority_path=authority_path,
                deployment=deployment)
        self.assertEqual(loaded.product_projection["runtime"]["capacity"], 8)
        self.assertEqual(calls, {authority_path: 1, artifact_path: 1})

    @unittest.skipUnless(
        os.name == "posix" and Path("/proc/self/fd").is_dir(),
        "sealed Linux native loading is the qualified path",
    )
    def test_native_path_swap_cannot_change_opened_inode_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            native = Path(temporary) / "librtdl_optix.so"
            replacement = Path(temporary) / "replacement.so"
            trusted = b"trusted-native-image"
            substituted = b"substituted-native"
            native.write_bytes(trusted)
            replacement.write_bytes(substituted)

            class FakeLibrary:
                _handle = 34567

            observations = {}

            def fake_cdll(load_path):
                # Reproduce an ordinary atomic A -> B pathname replacement
                # after verification.  The held fd must continue to name A.
                os.replace(replacement, native)
                observations["load_path"] = str(load_path)
                observations["loaded_bytes"] = Path(load_path).read_bytes()
                return FakeLibrary()

            with patch.object(
                    runtime_module, "_initialize_cuda_and_get_capability",
                    return_value=(8, 9)), patch.object(
                    runtime_module.ctypes, "CDLL", side_effect=fake_cdll):
                library = runtime_module._load_native_library(
                    native,
                    expected_sha256=hashlib.sha256(trusted).hexdigest(),
                    expected_compute_capability=(8, 9),
                )
            self.assertNotEqual(Path(observations["load_path"]), native)
            self.assertEqual(observations["loaded_bytes"], trusted)
            self.assertEqual(native.read_bytes(), substituted)
            self.assertEqual(
                library._rtdl_loaded_library_sha256,
                hashlib.sha256(trusted).hexdigest())
            descriptor = library._rtdl_native_image_fd
            cache_key = library._rtdl_native_cache_key
            runtime_module._release_native_library_image(library)
            self.assertEqual(library._handle, 0)
            self.assertEqual(library._rtdl_native_image_fd, -1)
            snapshot = runtime_module._native_image_cache_snapshot()[cache_key]
            self.assertEqual(snapshot["image_descriptor"], descriptor)
            self.assertEqual(snapshot["active_lease_count"], 0)
            os.fstat(descriptor)

    def test_signed_coherent_descriptor_change_rejects_unchanged_native(self):
        changed_descriptor = _native_descriptor()
        changed_descriptor["pipeline_compile"]["payload_values"] = 4
        authority_c = self.root / "c.authority.json"
        built_c = self._build(
            "C", "slot-C", authority_c,
            native_descriptor=changed_descriptor)
        package_abc = self.root / "package-abc.json"
        head_abc = self.root / "head-abc.json"
        freeze(private_path=self.private, root_path=self.public,
               authority_path=authority_c, output_path=package_abc,
               head_output_path=head_abc, previous_path=self.package_ab)
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=head_abc,
            trust_package_path=package_abc, deployment_id="slot-C")
        loaded = load_rtdlexe(
            built_c.artifact_path, authority_path=authority_c,
            deployment=deployment)
        with patch.object(runtime_module, "_load_native_library", return_value=object()), \
                patch.object(runtime_module, "_query_native_producer_descriptor",
                             return_value=_native_descriptor()), \
                patch.object(runtime_module, "_release_native_library_image"):
            with self.assertRaisesRegex(
                    RTDLExecutableError, "RX055_NATIVE_PRODUCER_SCHEMA_MISMATCH"):
                loaded.prepare(
                    runtime_module.BoundedRelationStaticInput(
                        ((0, 0, 1, 1, 1),)),
                    native_library_path=self.root / "mock-native.so")

    def test_valid_install_and_load(self):
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab,
            deployment_id="slot-A")
        loaded = load_rtdlexe(
            self.built_a.artifact_path, authority_path=self.authority_a,
            deployment=deployment)
        self.assertEqual(loaded.deployment_id, "slot-A")
        self.assertEqual(loaded.executable_identity_sha256,
                         self.built_a.executable_identity_sha256)
        with self.assertRaises(TypeError):
            loaded.product_projection["runtime"]["capacity"] = 999

    def test_zero_error_but_incomplete_fixed_product_summary_rejects(self):
        summary = runtime_module._ProductStatusSummary()
        summary.schema_version = 2
        summary.ok = 1
        summary.validated_row_count = 2
        summary.required_invocation_mask = (1 << 1) | (1 << 6)
        summary.terminal_invocation_mask = (1 << 4) | (1 << 5)
        summary.first_invalid_row = (1 << 64) - 1
        summary.success_status_d2h_bytes = runtime_module.ctypes.sizeof(
            runtime_module._ProductStatusSummary)
        valid_counters = (0, 2, 0, 0, 2, 0, 2)
        for index, value in enumerate(valid_counters):
            summary.role_counters[index] = value
        status, counters = runtime_module._validate_product_summary(
            summary, valid_counters, launch_count=2,
            terminal_invocation_mask=(1 << 4) | (1 << 5))
        self.assertTrue(status["ok"])
        self.assertEqual(counters, valid_counters)
        hostile = (
            ("missing_finalize", valid_counters[:-1] + (0,), None, None),
            ("device_error", valid_counters, "error_code", 7),
            ("incomplete", valid_counters, "invalid_row_count", 1),
            ("wrong_required", valid_counters, "required_invocation_mask", 1 << 1),
            ("wrong_terminal", valid_counters, "terminal_invocation_mask", 1 << 4),
            ("wrong_bytes", valid_counters, "success_status_d2h_bytes", 0),
        )
        for label, counters_value, field, value in hostile:
            changed = runtime_module._ProductStatusSummary.from_buffer_copy(summary)
            if field is not None:
                setattr(changed, field, value)
            with self.subTest(label=label):
                with self.assertRaisesRegex(RTDLExecutableError, "RX035_DEVICE_STATUS_INVALID"):
                    runtime_module._validate_product_summary(
                        changed, counters_value, launch_count=2,
                        terminal_invocation_mask=(1 << 4) | (1 << 5))

    def test_semantic_integers_and_build_scalars_reject_lossy_coercion(self):
        valid_box = (0.0, 0.0, 1.0, 1.0, 7)
        for value in (7.9, True, -1, 1 << 32):
            with self.subTest(field="bounded_id", value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, "RX006_INPUT_INVALID"):
                runtime_module.BoundedRelationBatch(((*valid_box[:4], value),))
            with self.subTest(field="static_id", value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, "RX006_INPUT_INVALID"):
                runtime_module.BoundedRelationStaticInput(((*valid_box[:4], value),))
            with self.subTest(field="oracle_id", value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, "RX006_INPUT_INVALID"):
                runtime_module.BoundedRelationBatch((valid_box,), expected_rows=((7, value),))

        vertices = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        for value in (1.5, True, -1, 1 << 32):
            with self.subTest(field="triangle_index", value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, "RX006_INPUT_INVALID"):
                runtime_module.TriangleReductionStaticInput(
                    vertices=vertices, triangles=((0, 1, value),))
        for value in (2.5, True, -1, 1 << 64):
            with self.subTest(field="weight", value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, "RX006_INPUT_INVALID"):
                runtime_module.TriangleReductionBatch(
                    queries=(((0, 0, 0), (0, 0, 1), 2),),
                    query_weights=(value,))
            with self.subTest(field="triangle_oracle", value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, "RX006_INPUT_INVALID"):
                runtime_module.TriangleReductionBatch(
                    queries=(((0, 0, 0), (0, 0, 1), 2),),
                    expected_reduced_u64=value)
        for value in (True, -1, 0, 1 << 32, 1 << 64):
            with self.subTest(field="event_capacity", value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, "RX006_INPUT_INVALID"):
                runtime_module.TriangleReductionStaticInput(
                    vertices=vertices, triangles=((0, 1, 2),),
                    event_capacity=value)

        import numpy as np
        numpy_batch = runtime_module.BoundedRelationBatch(
            ((0, 0, 1, 1, np.uint32(7)),),
            expected_rows=((np.uint32(7), np.uint32(8)),))
        self.assertEqual(numpy_batch.source_boxes[0][4], 7)
        numpy_triangle = runtime_module.TriangleReductionStaticInput(
            vertices=vertices,
            triangles=((np.uint32(0), np.uint32(1), np.uint32(2)),))
        self.assertEqual(numpy_triangle.triangles, ((0, 1, 2),))
        numpy_weights = runtime_module.TriangleReductionBatch(
            queries=(((0, 0, 0), (0, 0, 1), 2),),
            query_weights=(np.uint64(9),))
        self.assertEqual(numpy_weights.query_weights, (9,))

        class Owner:
            def execute(self, batch, *, diagnostics):
                raise AssertionError("non-bool diagnostics reached owner")

            def close(self):
                pass

        prepared = runtime_module.PreparedRTDLExecutable(
            family="custom_aabb_bounded_relation_v1",
            executable_identity_sha256=_sha("strict-diagnostics"), owner=Owner())
        with self.assertRaisesRegex(RTDLExecutableError, "RX006_INPUT_INVALID"):
            prepared.execute(runtime_module.BoundedRelationBatch((valid_box,)),
                             include_diagnostics="false")

        profile = SimpleNamespace(
            target_sha256=_sha("target"), native_sha256=_sha("native"),
            provider="optix", optix_sdk="9.0.0", supports_custom_aabb=True,
            supports_builtin_triangle=True, max_graph_depth=1)
        toolchain = SimpleNamespace(
            compute_capability=(6, 1), expected_python_version="3.11",
            expected_numba_version="0.61", expected_numpy_version="2.0")
        materialized = SimpleNamespace(
            _target=SimpleNamespace(profile=profile), _toolchain=toolchain)
        for field, value in (("supports_custom_aabb", 1),
                             ("supports_builtin_triangle", "yes"),
                             ("max_graph_depth", 0.5),
                             ("max_graph_depth", 0)):
            changed = SimpleNamespace(**vars(profile))
            setattr(changed, field, value)
            materialized._target = SimpleNamespace(profile=changed)
            with self.subTest(field=field, value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, "RX005_BUILD_INPUT_INVALID"):
                runtime_module._target_projection(materialized)
        materialized._target = SimpleNamespace(profile=profile)
        materialized._toolchain = SimpleNamespace(**vars(toolchain))
        materialized._toolchain.compute_capability = (6.1, 1)
        with self.assertRaisesRegex(RTDLExecutableError, "RX005_BUILD_INPUT_INVALID"):
            runtime_module._target_projection(materialized)
        bad_protocol = SimpleNamespace(capacity=8, minimum_overlap_f32=True)
        with self.assertRaisesRegex(RTDLExecutableError, "RX005_BUILD_INPUT_INVALID"):
            runtime_module._runtime_projection(
                SimpleNamespace(_program=SimpleNamespace(protocol=bad_protocol)),
                "custom_aabb_bounded_relation_v1")

    def test_candidate_not_frozen_and_old_package_rollback_reject(self):
        with self.assertRaisesRegex(RTDLExecutableError, "RX049_DEPLOYMENT_SLOT_NOT_FROZEN"):
            install_rtdlexe_deployment(
                trust_root_path=self.public, trust_head_path=self.head_a,
                trust_package_path=self.package_a,
                deployment_id="slot-B")
        # A is genuinely signed and contains a valid slot-A, but the separately
        # installed current head is AB/sequence 2: fresh rollback must fail.
        with self.assertRaisesRegex(RTDLExecutableError, "RX054_TRUST_PACKAGE_ROLLBACK"):
            install_rtdlexe_deployment(
                trust_root_path=self.public, trust_head_path=self.head_ab,
                trust_package_path=self.package_a,
                deployment_id="slot-A")

    def test_two_signed_same_family_tasks_cannot_cross_slots(self):
        deployment_a = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab,
            deployment_id="slot-A")
        with self.assertRaisesRegex(RTDLExecutableError, "RX050_DEPLOYMENT_INTENT_MISMATCH"):
            load_rtdlexe(self.built_b.artifact_path,
                         authority_path=self.authority_b, deployment=deployment_a)

    def test_capability_is_immutable_and_trust_bytes_are_rechecked(self):
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab,
            deployment_id="slot-A")
        with self.assertRaises(TypeError):
            deployment.entry["family"] = "forged"
        with self.assertRaisesRegex(RTDLExecutableError, "RX048_DEPLOYMENT_CAPABILITY_INVALID"):
            deployment.deployment_id = "slot-B"
        copied = self.root / "tamper-package.json"
        copied.write_bytes(self.package_ab.read_bytes())
        mutable = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=copied,
            deployment_id="slot-A")
        copied.write_bytes(copied.read_bytes() + b" ")
        with self.assertRaisesRegex(RTDLExecutableError, "RX048_DEPLOYMENT_CAPABILITY_INVALID"):
            load_rtdlexe(self.built_a.artifact_path,
                         authority_path=self.authority_a, deployment=mutable)
        rollback = self.root / "rollback-package.json"
        rollback.write_bytes(self.package_ab.read_bytes())
        installed_latest = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=rollback,
            deployment_id="slot-A")
        rollback.write_bytes(self.package_a.read_bytes())
        with self.assertRaisesRegex(RTDLExecutableError, "RX048_DEPLOYMENT_CAPABILITY_INVALID"):
            load_rtdlexe(self.built_a.artifact_path,
                         authority_path=self.authority_a, deployment=installed_latest)

    def test_modified_registry_signature_rejects(self):
        package = json.loads(self.package_ab.read_text(encoding="utf-8"))
        package["authorities"][0]["family"] = "forged-family"
        path = self.root / "signature-tampered.json"
        path.write_bytes(_canonical(package) + b"\n")
        with self.assertRaisesRegex(RTDLExecutableError, "RX047_TRUST_PACKAGE_SIGNATURE_INVALID"):
            install_rtdlexe_deployment(
                trust_root_path=self.public, trust_head_path=self.head_ab,
                trust_package_path=path,
                deployment_id="slot-A")

    def _coherent_reseal(self, mutate):
        artifact = json.loads(self.built_a.artifact_path.read_text(encoding="utf-8"))
        authority = json.loads(self.authority_a.read_text(encoding="utf-8"))
        mutate(artifact)
        artifact_bytes = _canonical(artifact) + b"\n"
        artifact_sha = hashlib.sha256(artifact_bytes).hexdigest()
        artifact_path = self.root / f"{artifact_sha}.rtdlexe"
        artifact_path.write_bytes(artifact_bytes)
        body = dict(authority); body.pop("authority_seal")
        body["artifact_sha256"] = artifact_sha
        body["artifact_bytes"] = len(artifact_bytes)
        body["product_projection_sha256"] = _digest(artifact["product_projection"])
        import rtdsl.v4_rtdlexe as module
        authority = {
            **body,
            "authority_seal": hashlib.sha256(
                module._AUTHORITY_DOMAIN + _canonical(body)).hexdigest(),
        }
        authority_path = self.root / f"forge-{artifact_sha}.authority.json"
        authority_path.write_bytes(_canonical(authority) + b"\n")
        return artifact_path, authority_path

    def test_coherent_cache_poison_reseal_cannot_change_expected_hash(self):
        def mutate(artifact):
            provider = artifact["product_projection"]["provider_key"]
            provider["wrapper_numeric_policy"] = "forged-but-self-consistent"
            body = dict(provider); body.pop("provider_key_sha256")
            provider["provider_key_sha256"] = _digest(body)

        artifact_path, authority_path = self._coherent_reseal(mutate)
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab,
            deployment_id="slot-A")
        self.assertNotIn("expected_authority_sha256", load_rtdlexe.__annotations__)
        with self.assertRaisesRegex(RTDLExecutableError, "RX050_DEPLOYMENT_INTENT_MISMATCH"):
            load_rtdlexe(artifact_path, authority_path=authority_path,
                         deployment=deployment)

    def test_partial_identity_chain_deletions_reject(self):
        mutations = (
            lambda artifact: artifact["product_projection"]["provider_key"].pop("llvmlite_version"),
            lambda artifact: artifact["product_projection"]["execution_schema"]
                ["producer_inputs"].pop("sbt"),
            lambda artifact: artifact["product_projection"].pop("provider_key"),
        )
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab,
            deployment_id="slot-A")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                artifact_path, authority_path = self._coherent_reseal(mutation)
                with self.assertRaises(RTDLExecutableError):
                    load_rtdlexe(artifact_path, authority_path=authority_path,
                                 deployment=deployment)

    def test_schema_rollback_and_device_substitution_reject(self):
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab,
            deployment_id="slot-A")
        for value in (0, True, 1.0):
            artifact_path, authority_path = self._coherent_reseal(
                lambda artifact, exact=value: artifact.__setitem__(
                    "format_version", exact))
            with self.subTest(format_version=value), \
                    self.assertRaisesRegex(
                        RTDLExecutableError, "RX024_ARTIFACT_SCHEMA_ROLLBACK"):
                load_rtdlexe(artifact_path, authority_path=authority_path,
                             deployment=deployment)

        exact_authority = json.loads(self.authority_a.read_text(encoding="utf-8"))
        for field, value, expected_code in (
            ("authority_version", True, "RX019_AUTHORITY_SCHEMA_ROLLBACK"),
            ("authority_version", 1.0, "RX019_AUTHORITY_SCHEMA_ROLLBACK"),
            ("artifact_bytes", True, "RX018_AUTHORITY_INVALID"),
            ("artifact_bytes", float(exact_authority["artifact_bytes"]),
             "RX018_AUTHORITY_INVALID"),
        ):
            body = dict(exact_authority); body.pop("authority_seal")
            body[field] = value
            changed = {**body, "authority_seal": hashlib.sha256(
                runtime_module._AUTHORITY_DOMAIN + _canonical(body)).hexdigest()}
            path = self.root / f"authority-type-{field}-{repr(value)}.json"
            path.write_bytes(_canonical(changed) + b"\n")
            with self.subTest(field=field, value=value), \
                    self.assertRaisesRegex(RTDLExecutableError, expected_code):
                load_rtdlexe(self.built_a.artifact_path,
                             authority_path=path, deployment=deployment)

        def substitute_device(artifact):
            product = artifact["product_projection"]
            product["target_toolchain"]["compute_capability"] = [9, 0]
            provider = product["provider_key"]
            provider["target_compute_capability"] = [9, 0]
            provider_body = dict(provider); provider_body.pop("provider_key_sha256")
            provider["provider_key_sha256"] = _digest(provider_body)

        artifact_path, authority_path = self._coherent_reseal(substitute_device)
        authority = json.loads(authority_path.read_text(encoding="utf-8"))
        body = dict(authority); body.pop("authority_seal")
        body["target_compute_capability"] = [9, 0]
        body["authority_seal"] = hashlib.sha256(
            runtime_module._AUTHORITY_DOMAIN + _canonical(body)).hexdigest()
        authority_path.write_bytes(_canonical(body) + b"\n")
        with self.assertRaisesRegex(RTDLExecutableError, "RX050_DEPLOYMENT_INTENT_MISMATCH"):
            load_rtdlexe(artifact_path, authority_path=authority_path,
                         deployment=deployment)

    def test_offline_freeze_rejects_lossy_authority_scalar_types(self):
        exact_authority = json.loads(self.authority_a.read_text(encoding="utf-8"))
        for index, (field, value) in enumerate((
            ("authority_version", True),
            ("authority_version", 1.0),
            ("artifact_bytes", True),
            ("artifact_bytes", float(exact_authority["artifact_bytes"])),
        )):
            body = dict(exact_authority); body.pop("authority_seal")
            body[field] = value
            changed = {**body, "authority_seal": hashlib.sha256(
                runtime_module._AUTHORITY_DOMAIN + _canonical(body)).hexdigest()}
            path = self.root / f"freeze-type-{index}.authority.json"
            path.write_bytes(_canonical(changed) + b"\n")
            with self.subTest(field=field, value=value), \
                    self.assertRaisesRegex(ValueError, "detached authority schema invalid"):
                freeze(
                    private_path=self.private, root_path=self.public,
                    authority_path=path,
                    output_path=self.root / f"freeze-type-{index}.package.json",
                    head_output_path=self.root / f"freeze-type-{index}.head.json",
                    previous_path=None,
                )

    def test_public_load_prepare_execute_close_lifecycle(self):
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab,
            deployment_id="slot-A")
        loaded = load_rtdlexe(
            self.built_a.artifact_path, authority_path=self.authority_a,
            deployment=deployment)

        class Owner:
            closed = False

            def execute(self, batch, *, diagnostics):
                self.batch = batch; self.diagnostics = diagnostics
                output = ((1, 2),)
                return output, _digest(output), {"ok": True}, (0, 1, 0, 0, 1, 0, 1), None

            def close(self):
                self.closed = True

        owner = Owner()
        expected_descriptor = _native_descriptor()
        with patch.object(runtime_module, "_load_native_library", return_value=object()), \
                patch.object(runtime_module, "_query_native_producer_descriptor",
                             return_value=expected_descriptor), \
                patch.object(runtime_module, "_PreparedBoundedOwner", return_value=owner):
            prepared = loaded.prepare(
                runtime_module.BoundedRelationStaticInput(((0, 0, 1, 1, 1),)),
                native_library_path=self.root / "mock-native.so")
            result = prepared.execute(
                runtime_module.BoundedRelationBatch(((0, 0, 1, 1, 2),)))
            self.assertEqual(result.output, ((1, 2),))
            prepared.close(); prepared.close()
            self.assertTrue(owner.closed)
            with self.assertRaisesRegex(RTDLExecutableError, "RX037_USE_AFTER_CLOSE"):
                prepared.execute(runtime_module.BoundedRelationBatch(((0, 0, 1, 1, 2),)))

    def test_canonical_identity_parses_and_hashes_one_opened_descriptor(self):
        """A pathname replacement cannot supply parse bytes after hash bytes."""

        with tempfile.TemporaryDirectory(dir=self.root) as temporary:
            directory = Path(temporary)
            opened = directory / "opened.json"
            requested = directory / "requested.json"
            first = _canonical({"identity": "verified-A"}) + b"\n"
            second = _canonical({"identity": "replacement-B"}) + b"\n"
            opened.write_bytes(first)
            requested.write_bytes(second)
            descriptor = os.open(opened, os.O_RDONLY)
            opened_stat = os.fstat(descriptor)
            with patch.object(
                runtime_module, "_open_regular_readonly",
                return_value=(descriptor, opened_stat),
            ) as opened_once:
                parsed, raw = runtime_module._read_canonical_json_with_raw(
                    requested, code="RX023_ARTIFACT_INVALID")
            opened_once.assert_called_once_with(
                requested, code="RX023_ARTIFACT_INVALID")
            self.assertEqual(raw, first)
            self.assertEqual(parsed, {"identity": "verified-A"})
            self.assertEqual(hashlib.sha256(raw).hexdigest(), hashlib.sha256(first).hexdigest())
            self.assertEqual(requested.read_bytes(), second)

    def test_load_reads_each_canonical_input_once(self):
        deployment = install_rtdlexe_deployment(
            trust_root_path=self.public, trust_head_path=self.head_ab,
            trust_package_path=self.package_ab, deployment_id="slot-A")
        original = runtime_module._read_regular_bytes_once
        counts: dict[Path, int] = {}

        def counted(path, *, code):
            normalized = runtime_module._absolute_unresolved_path(path)
            counts[normalized] = counts.get(normalized, 0) + 1
            return original(normalized, code=code)

        with patch.object(runtime_module, "_read_regular_bytes_once", side_effect=counted):
            loaded = load_rtdlexe(
                self.built_a.artifact_path, authority_path=self.authority_a,
                deployment=deployment)
        self.assertEqual(loaded.executable_identity_sha256,
                         self.built_a.executable_identity_sha256)
        expected = (
            self.public, self.head_ab, self.package_ab,
            self.authority_a, self.built_a.artifact_path,
        )
        self.assertEqual(
            {runtime_module._absolute_unresolved_path(path): counts.get(
                runtime_module._absolute_unresolved_path(path), 0)
             for path in expected},
            {runtime_module._absolute_unresolved_path(path): 1 for path in expected},
        )

    def test_native_identity_loads_a_sealed_image_through_one_unique_alias(self):
        """The loader must never give glibc a reusable fd-path spelling."""

        class FakeLibrary:
            pass

        verified = b"verified native inode bytes"
        replacement_path = self.root / "replacement-native.so"
        replacement_path.write_bytes(b"different path bytes")
        source_descriptor = 731
        image_descriptor = 941
        required_seals = 15
        alias_directory = Path("/private/rtdl-native-unique")
        alias_path = alias_directory / "image-exact.so"
        library = FakeLibrary()
        library._handle = 12345
        with patch.object(
            runtime_module, "_open_regular_readonly",
            return_value=(source_descriptor, object()),
        ) as opened_once, patch.object(
            runtime_module, "_read_descriptor_bytes",
            side_effect=((verified, object()), (verified, object())),
        ) as read_twice, patch.object(
            runtime_module, "_sealed_native_image_descriptor",
            return_value=(image_descriptor, required_seals),
        ) as sealed_image, patch.object(
            runtime_module, "_create_unique_native_loader_alias",
            return_value=(alias_directory, alias_path),
        ) as unique_alias, patch.object(
            runtime_module, "_remove_native_loader_alias",
        ) as remove_alias, patch.object(
            runtime_module, "_native_image_seals",
            return_value=required_seals,
        ), patch.object(
            runtime_module.ctypes, "CDLL", return_value=library,
        ) as cdll, patch.object(runtime_module.os, "close") as close:
            loaded = runtime_module._load_verified_native_file_descriptor(
                replacement_path,
                expected_sha256=hashlib.sha256(verified).hexdigest(),
                code="RX005_BUILD_INPUT_INVALID",
                identity_path="materialized.target.native_library_path")
            self.assertIs(loaded._rtdl_native_cache_entry.library, library)
            opened_once.assert_called_once_with(
                runtime_module._absolute_unresolved_path(replacement_path),
                code="RX005_BUILD_INPUT_INVALID")
            self.assertEqual(read_twice.call_count, 2)
            sealed_image.assert_called_once_with(
                verified,
                expected_sha256=hashlib.sha256(verified).hexdigest(),
                code="RX005_BUILD_INPUT_INVALID",
                identity_path="materialized.target.native_library_path")
            unique_alias.assert_called_once_with(
                image_descriptor,
                observed_sha256=hashlib.sha256(verified).hexdigest(),
                code="RX005_BUILD_INPUT_INVALID",
                identity_path="materialized.target.native_library_path")
            cdll.assert_called_once_with(str(alias_path))
            remove_alias.assert_called_once_with(
                alias_path, alias_directory,
                code="RX005_BUILD_INPUT_INVALID",
                identity_path="materialized.target.native_library_path")
            self.assertEqual(loaded._rtdl_loaded_library_sha256,
                             hashlib.sha256(verified).hexdigest())
            self.assertEqual(loaded._rtdl_native_loader_alias, str(alias_path))
            runtime_module._release_native_library_image(loaded)
            runtime_module._release_native_library_image(loaded)
            self.assertEqual(loaded._handle, 0)
            self.assertEqual(loaded._rtdl_native_image_fd, -1)
            self.assertTrue(loaded._rtdl_native_image_released)
            snapshot = runtime_module._native_image_cache_snapshot()[
                hashlib.sha256(verified).hexdigest()]
            self.assertEqual(snapshot["loader_handle"], 12345)
            self.assertEqual(snapshot["image_descriptor"], image_descriptor)
            self.assertEqual(snapshot["active_lease_count"], 0)
            self.assertEqual(
                [call.args[0] for call in close.call_args_list],
                [source_descriptor])

    def test_native_release_removes_strong_identity_and_audit_registries(self):
        path = self.root / "registered-native.so"
        path.write_bytes(b"registered-native")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        backing = SimpleNamespace(_handle=23456)
        entry = runtime_module._NativeImageCacheEntry(
            library=backing, sha256=digest, source_path=path,
            image_descriptor=73, image_seals=15, loader_alias="private-alias",
            owner_pid=os.getpid(), usable=True)
        with runtime_module._NATIVE_IMAGE_CACHE_LOCK:
            runtime_module._NATIVE_IMAGE_CACHE[digest] = entry
            library = runtime_module._acquire_native_image_lease(
                entry, source_path=path)
        provenance._register_loaded_provider_identity(
            library, path, digest)
        with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
            provenance._AUDIT_ABI_REGISTERED[id(library)] = library
        runtime_module._release_native_library_image(library)
        runtime_module._release_native_library_image(library)
        with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
            self.assertNotIn(id(library), provenance._LOADED_PROVIDER_IDENTITIES)
            self.assertNotIn(id(library), provenance._AUDIT_ABI_REGISTERED)
        self.assertEqual(library._handle, 0)
        self.assertEqual(library._rtdl_native_image_fd, -1)
        self.assertEqual(backing._handle, 23456)
        self.assertEqual(entry.active_lease_ids, set())

    def test_owner_release_failure_is_resumable_without_second_destroy(self):
        owner = runtime_module._PreparedBoundedOwner.__new__(
            runtime_module._PreparedBoundedOwner)
        owner._token_cell = ctypes.c_uint64(1)
        owner._token = 1
        owner._closed = False
        owner._release_complete = False
        owner._close_failure = None
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._active = threading.Lock()
        path = self.root / "owner-release-native.so"
        path.write_bytes(b"owner-release-native")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entry = runtime_module._NativeImageCacheEntry(
            library=SimpleNamespace(_handle=34567), sha256=digest,
            source_path=path, image_descriptor=74, image_seals=15,
            loader_alias="owner-release-alias", owner_pid=os.getpid(),
            usable=True)
        with runtime_module._NATIVE_IMAGE_CACHE_LOCK:
            runtime_module._NATIVE_IMAGE_CACHE[digest] = entry
            lease = runtime_module._acquire_native_image_lease(
                entry, source_path=path)
        owner._library = lease
        owner._execute_fast = object()
        owner._execute_diagnostic = object()
        owner._build_count = object()
        owner._commit = object()
        owner._cache_digest = object()
        destroy_calls = []

        def destroy(token_pointer, *_args):
            destroy_calls.append(True)
            token_pointer._obj.value = 0
            return 0

        owner._destroy = destroy
        real_release = runtime_module._release_native_library_image
        release_calls = []

        def release_then_interrupt(library):
            release_calls.append(True)
            real_release(library)
            if len(release_calls) == 1:
                raise KeyboardInterrupt("injected after complete lease release")

        with patch.object(
                runtime_module, "_release_native_library_image",
                side_effect=release_then_interrupt) as release:
            with self.assertRaisesRegex(
                    KeyboardInterrupt, "injected after complete lease release"):
                owner.close()
            self.assertTrue(owner._closed)
            self.assertFalse(owner._release_complete)
            self.assertIs(owner._library, lease)
            self.assertIsNone(owner._execute_fast)
            self.assertIsNone(owner._execute_diagnostic)
            self.assertIsNone(owner._destroy)
            self.assertTrue(lease._rtdl_native_image_released)
            self.assertEqual(entry.active_lease_ids, set())
            with self.assertRaises(RTDLExecutableError) as use_after_close:
                owner._check()
            self.assertEqual(use_after_close.exception.code, "RX037_USE_AFTER_CLOSE")
            owner.close()
            self.assertTrue(owner._release_complete)
            self.assertIsNone(owner._library)
            self.assertIsNone(owner._close_failure)
            self.assertEqual(release.call_count, 2)
        self.assertEqual(len(destroy_calls), 1)

    def test_release_resumes_after_unregistration_publication_interrupt(self):
        path = self.root / "release-unregister.so"
        path.write_bytes(b"release-unregister")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entry = runtime_module._NativeImageCacheEntry(
            library=SimpleNamespace(_handle=45678), sha256=digest,
            source_path=path, image_descriptor=75, image_seals=15,
            loader_alias="unregister-alias", owner_pid=os.getpid(), usable=True)
        with runtime_module._NATIVE_IMAGE_CACHE_LOCK:
            runtime_module._NATIVE_IMAGE_CACHE[digest] = entry
            lease = runtime_module._acquire_native_image_lease(
                entry, source_path=path)
        provenance._register_loaded_provider_identity(lease, path, digest)
        with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
            provenance._AUDIT_ABI_REGISTERED[id(lease)] = lease
        real_unregister = provenance._unregister_loaded_provider_identity
        calls = []

        def unregister_then_interrupt(library):
            real_unregister(library)
            calls.append(True)
            if len(calls) == 1:
                raise KeyboardInterrupt("after provenance publication")

        with patch.object(
                provenance, "_unregister_loaded_provider_identity",
                side_effect=unregister_then_interrupt):
            with self.assertRaisesRegex(
                    KeyboardInterrupt, "after provenance publication"):
                runtime_module._release_native_library_image(lease)
            self.assertEqual(lease._rtdl_native_image_release_phase, "ACTIVE")
            self.assertIn(lease._rtdl_native_cache_lease_id,
                          entry.active_lease_ids)
            with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
                self.assertNotIn(id(lease), provenance._LOADED_PROVIDER_IDENTITIES)
                self.assertNotIn(id(lease), provenance._AUDIT_ABI_REGISTERED)
            runtime_module._release_native_library_image(lease)
        self.assertEqual(lease._rtdl_native_image_release_phase, "COMPLETE")
        self.assertEqual(entry.active_lease_ids, set())
        self.assertIsNone(lease._rtdl_native_image_release_error)

    def test_release_resumes_after_lease_removal_publication_interrupt(self):
        path = self.root / "release-remove.so"
        path.write_bytes(b"release-remove")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entry = runtime_module._NativeImageCacheEntry(
            library=SimpleNamespace(_handle=56789), sha256=digest,
            source_path=path, image_descriptor=76, image_seals=15,
            loader_alias="remove-alias", owner_pid=os.getpid(), usable=True)
        with runtime_module._NATIVE_IMAGE_CACHE_LOCK:
            runtime_module._NATIVE_IMAGE_CACHE[digest] = entry
            lease = runtime_module._acquire_native_image_lease(
                entry, source_path=path)
        real_remove = runtime_module._remove_native_cache_lease
        calls = []

        def remove_then_interrupt(cache_entry, lease_id):
            real_remove(cache_entry, lease_id)
            calls.append(True)
            if len(calls) == 1:
                raise KeyboardInterrupt("after lease removal publication")

        with patch.object(
                runtime_module, "_remove_native_cache_lease",
                side_effect=remove_then_interrupt):
            with self.assertRaisesRegex(
                    KeyboardInterrupt, "after lease removal publication"):
                runtime_module._release_native_library_image(lease)
            self.assertEqual(
                lease._rtdl_native_image_release_phase,
                "PROVENANCE_UNREGISTERED")
            self.assertEqual(entry.active_lease_ids, set())
            runtime_module._release_native_library_image(lease)
        self.assertEqual(lease._rtdl_native_image_release_phase, "COMPLETE")
        self.assertTrue(lease._rtdl_native_image_released)
        self.assertIsNone(lease._rtdl_native_image_release_error)

    def test_release_resumes_after_final_phase_publication_interrupt(self):
        path = self.root / "release-complete.so"
        path.write_bytes(b"release-complete")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entry = runtime_module._NativeImageCacheEntry(
            library=SimpleNamespace(_handle=67890), sha256=digest,
            source_path=path, image_descriptor=77, image_seals=15,
            loader_alias="complete-alias", owner_pid=os.getpid(), usable=True)
        with runtime_module._NATIVE_IMAGE_CACHE_LOCK:
            runtime_module._NATIVE_IMAGE_CACHE[digest] = entry
            lease = runtime_module._acquire_native_image_lease(
                entry, source_path=path)
        real_complete = runtime_module._complete_native_cache_lease_release
        calls = []

        def phase_then_interrupt(library):
            library._rtdl_native_image_release_phase = "COMPLETE"
            calls.append(True)
            if len(calls) == 1:
                raise KeyboardInterrupt("after final phase publication")
            real_complete(library)

        with patch.object(
                runtime_module, "_complete_native_cache_lease_release",
                side_effect=phase_then_interrupt):
            with self.assertRaisesRegex(
                    KeyboardInterrupt, "after final phase publication"):
                runtime_module._release_native_library_image(lease)
            self.assertEqual(lease._rtdl_native_image_release_phase, "COMPLETE")
            self.assertFalse(lease._rtdl_native_image_released)
            self.assertEqual(entry.active_lease_ids, set())
            runtime_module._release_native_library_image(lease)
        self.assertTrue(lease._rtdl_native_image_released)
        self.assertIsNone(lease._rtdl_native_image_release_error)

    def test_native_lease_acquisition_rolls_back_constructor_failure(self):
        path = self.root / "acquire-constructor.so"
        digest = hashlib.sha256(b"acquire-constructor").hexdigest()
        entry = runtime_module._NativeImageCacheEntry(
            library=SimpleNamespace(_handle=78901), sha256=digest,
            source_path=path, image_descriptor=78, image_seals=15,
            loader_alias="constructor-alias", owner_pid=os.getpid(), usable=True)
        with patch.object(
                runtime_module, "_NativeLibraryLease",
                side_effect=KeyboardInterrupt("lease constructor")):
            with self.assertRaisesRegex(KeyboardInterrupt, "lease constructor"):
                runtime_module._acquire_native_image_lease(
                    entry, source_path=path)
        self.assertEqual(entry.active_lease_ids, set())
        self.assertEqual(entry.acquisition_count, 0)

    def test_native_lease_admission_cleans_registration_and_handoff_failures(self):
        for label in ("registration", "handoff"):
            with self.subTest(label=label):
                path = self.root / f"acquire-{label}.so"
                path.write_bytes(label.encode("ascii"))
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                entry = runtime_module._NativeImageCacheEntry(
                    library=SimpleNamespace(_handle=80000 + len(label)),
                    sha256=digest, source_path=path,
                    image_descriptor=80 + len(label), image_seals=15,
                    loader_alias=f"{label}-alias", owner_pid=os.getpid(),
                    usable=True)
                if label == "registration":
                    real_register = (
                        runtime_module._register_native_image_lease_provenance)

                    def fail_registration(library, *, source_path, digest):
                        real_register(
                            library, source_path=source_path, digest=digest)
                        raise KeyboardInterrupt("registration import boundary")

                    registration = patch.object(
                        runtime_module,
                        "_register_native_image_lease_provenance",
                        side_effect=fail_registration)
                    handoff = patch.object(
                        runtime_module, "_native_image_lease_handoff")
                    expected = "registration import boundary"
                else:
                    registration = patch.object(
                        runtime_module,
                        "_register_native_image_lease_provenance",
                        wraps=runtime_module._register_native_image_lease_provenance)
                    handoff = patch.object(
                        runtime_module, "_native_image_lease_handoff",
                        side_effect=KeyboardInterrupt("return handoff boundary"))
                    expected = "return handoff boundary"
                with runtime_module._NATIVE_IMAGE_CACHE_LOCK:
                    runtime_module._NATIVE_IMAGE_CACHE[digest] = entry
                with registration, handoff:
                    with self.assertRaisesRegex(KeyboardInterrupt, expected):
                        runtime_module._admit_native_image_lease(
                            entry, source_path=path, register_provenance=True)
                self.assertEqual(entry.active_lease_ids, set())
                with provenance._LOADED_PROVIDER_IDENTITIES_LOCK:
                    registered = [
                        key for key, row in provenance._LOADED_PROVIDER_IDENTITIES.items()
                        if row[2] == digest]
                self.assertEqual(registered, [])

    def test_fork_poison_rejects_before_any_cuda_initialization(self):
        with patch.object(
                runtime_module, "_NATIVE_IMAGE_CACHE_FORK_POISONED", True), \
                patch.object(
                    runtime_module, "_initialize_cuda_and_get_capability") \
                as initialize:
            with self.assertRaises(RTDLExecutableError) as rejected:
                runtime_module._load_native_library(
                    self.root / "must-not-open.so",
                    expected_sha256="a" * 64,
                    expected_compute_capability=(8, 9))
        self.assertEqual(
            rejected.exception.code, "RX047_NATIVE_CACHE_FORK_POISONED")
        initialize.assert_not_called()

    def test_load_quarantine_does_not_block_existing_lease_cleanup(self):
        path = self.root / "live-before-quarantine.so"
        path.write_bytes(b"live-before-quarantine")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entry = runtime_module._NativeImageCacheEntry(
            library=SimpleNamespace(_handle=81234), sha256=digest,
            source_path=path, image_descriptor=91, image_seals=15,
            loader_alias="live-before-quarantine-alias",
            owner_pid=os.getpid(), usable=True)
        with runtime_module._NATIVE_IMAGE_CACHE_LOCK:
            runtime_module._NATIVE_IMAGE_CACHE[digest] = entry
            lease = runtime_module._acquire_native_image_lease(
                entry, source_path=path)
        with patch.object(
                runtime_module, "_NATIVE_IMAGE_CACHE_LOAD_POISONED", True), \
                patch.object(
                    runtime_module, "_NATIVE_IMAGE_CACHE_LOAD_FAILURE",
                    "injected B post-dlopen failure"):
            with self.assertRaises(RTDLExecutableError) as admission:
                runtime_module._native_image_cache_guard(
                    code="RX005_BUILD_INPUT_INVALID", identity_path="native.B")
            self.assertEqual(
                admission.exception.code, "RX048_NATIVE_CACHE_QUARANTINED")
            runtime_module._release_native_library_image(lease)
        self.assertTrue(lease._rtdl_native_image_released)
        self.assertEqual(entry.active_lease_ids, set())

    def test_native_zero_token_cell_prevents_second_destroy_after_interrupt(self):
        for owner_class, family in (
                (runtime_module._PreparedBoundedOwner, "bounded"),
                (runtime_module._PreparedTriangleOwner, "triangle")):
            with self.subTest(family=family):
                owner = owner_class.__new__(owner_class)
                owner._token_cell = ctypes.c_uint64(99)
                owner._token = 99
                owner._closed = False
                owner._release_complete = False
                owner._close_failure = None
                owner._pid = os.getpid()
                owner._thread = threading.get_ident()
                owner._active = threading.Lock()
                owner._library = object()
                owner._execute_fast = object()
                owner._execute_diagnostic = object()
                owner._commit = object()
                owner._cache_digest = object()
                if family == "bounded":
                    owner._build_count = object()
                destroy_calls = []

                def destroy(token_pointer, *_args):
                    destroy_calls.append(True)
                    token_pointer._obj.value = 0
                    raise KeyboardInterrupt("after native erase and zero")

                owner._destroy = destroy
                with patch.object(
                        runtime_module, "_release_native_library_image") as release:
                    with self.assertRaisesRegex(
                            KeyboardInterrupt, "after native erase and zero"):
                        owner.close()
                    self.assertEqual(owner._token_cell.value, 0)
                    self.assertEqual(owner._token, 0)
                    self.assertTrue(owner._closed)
                    self.assertIsNone(owner._execute_fast)
                    self.assertIsNone(owner._execute_diagnostic)
                    self.assertIsNone(owner._destroy)
                    release.assert_not_called()
                    owner.close()
                    release.assert_called_once()
                self.assertEqual(len(destroy_calls), 1)
                self.assertTrue(owner._release_complete)
                self.assertIsNone(owner._library)

    @unittest.skipUnless(
        os.name == "posix" and hasattr(os, "memfd_create") and
        Path("/proc/self/fd").is_dir(),
        "sealed memfd native loading is the qualified Linux path",
    )
    def test_content_cache_keeps_distinct_images_and_reuses_only_same_digest(self):
        compiler = shutil.which("cc")
        if compiler is None:
            self.skipTest("C compiler unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            rows = []
            for label, value in (("a", 111), ("b", 222)):
                source = directory / f"{label}.c"
                image = directory / f"{label}.so"
                source.write_text(
                    f"int marker(void){{return {value};}}\n", encoding="utf-8")
                subprocess.run(
                    [compiler, "-shared", "-fPIC", str(source), "-o", str(image)],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                library = runtime_module._load_verified_native_file_descriptor(
                    image, expected_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                    code="RX005_BUILD_INPUT_INVALID", identity_path=f"native.{label}")
                library.marker.argtypes = []
                library.marker.restype = ctypes.c_int
                digest = hashlib.sha256(image.read_bytes()).hexdigest()
                map_needle = f"memfd:rtdl-native-{digest[:16]}"
                map_rows_before_release = sum(
                    map_needle in row
                    for row in Path("/proc/self/maps").read_text(
                        encoding="utf-8").splitlines())
                rows.append({
                    "label": label,
                    "marker": int(library.marker()),
                    "descriptor": library._rtdl_native_image_fd,
                    "handle": library._handle,
                    "alias": library._rtdl_native_loader_alias,
                    "seals": library._rtdl_native_image_seals,
                    "map_rows_before_release": map_rows_before_release,
                    "entry_identity": library._rtdl_native_cache_entry_identity,
                    "lease_id": library._rtdl_native_cache_lease_id,
                })
                runtime_module._release_native_library_image(library)
                rows[-1]["map_rows_after_release"] = sum(
                    map_needle in row
                    for row in Path("/proc/self/maps").read_text(
                        encoding="utf-8").splitlines())
                rows[-1]["invalidated_handle"] = library._handle
                rows[-1]["active_after_release"] = (
                    library._rtdl_native_cache_active_lease_count)
            first, second = rows
            self.assertEqual(first["marker"], 111)
            self.assertEqual(second["marker"], 222)
            # The old defect required closing A's fd and allowing B to reuse
            # the same /proc/self/fd/N spelling.  A content-cache entry retains
            # its sealed fd, so that precondition is structurally absent.
            self.assertNotEqual(first["descriptor"], second["descriptor"])
            self.assertNotEqual(first["alias"], second["alias"])
            self.assertNotEqual(first["entry_identity"], second["entry_identity"])
            self.assertEqual(first["seals"], 15)
            self.assertEqual(second["seals"], 15)
            self.assertGreater(first["map_rows_before_release"], 0)
            self.assertGreater(second["map_rows_before_release"], 0)
            self.assertEqual(first["map_rows_after_release"],
                             first["map_rows_before_release"])
            self.assertEqual(second["map_rows_after_release"],
                             second["map_rows_before_release"])
            self.assertEqual(first["invalidated_handle"], 0)
            self.assertEqual(second["invalidated_handle"], 0)
            self.assertEqual(first["active_after_release"], 0)
            self.assertEqual(second["active_after_release"], 0)

            image_a = directory / "a.so"
            digest_a = hashlib.sha256(image_a.read_bytes()).hexdigest()
            again = runtime_module._load_verified_native_file_descriptor(
                image_a, expected_sha256=digest_a,
                code="RX005_BUILD_INPUT_INVALID", identity_path="native.a.again")
            again.marker.argtypes = []
            again.marker.restype = ctypes.c_int
            self.assertEqual(int(again.marker()), 111)
            self.assertEqual(again._handle, first["handle"])
            self.assertEqual(again._rtdl_native_image_fd, first["descriptor"])
            self.assertEqual(
                again._rtdl_native_cache_entry_identity, first["entry_identity"])
            self.assertNotEqual(
                again._rtdl_native_cache_lease_id, first["lease_id"])
            self.assertEqual(again._rtdl_native_cache_acquisition_count, 2)
            runtime_module._release_native_library_image(again)
            self.assertEqual(again._rtdl_native_cache_active_lease_count, 0)

    @unittest.skipUnless(
        os.name == "posix" and hasattr(os, "memfd_create") and
        Path("/proc/self/fd").is_dir(),
        "sealed memfd native loading is the qualified Linux path",
    )
    def test_post_dlopen_failure_is_quarantined_and_live_lease_still_closes(self):
        compiler = shutil.which("cc")
        if compiler is None:
            self.skipTest("C compiler unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            images = {}
            for label, value in (("live", 333), ("fail", 444)):
                source = directory / f"{label}.c"
                image = directory / f"{label}.so"
                source.write_text(
                    f"int marker(void){{return {value};}}\n", encoding="utf-8")
                subprocess.run(
                    [compiler, "-shared", "-fPIC", str(source), "-o", str(image)],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                images[label] = image
            live_digest = hashlib.sha256(images["live"].read_bytes()).hexdigest()
            live = runtime_module._load_verified_native_file_descriptor(
                images["live"], expected_sha256=live_digest,
                code="RX005_BUILD_INPUT_INVALID", identity_path="native.live")
            failed_digest = hashlib.sha256(images["fail"].read_bytes()).hexdigest()
            original_remove = runtime_module._remove_native_loader_alias
            remove_calls = []

            def cleanup_then_interrupt(alias, alias_directory, *, code, identity_path):
                remove_calls.append(True)
                original_remove(
                    alias, alias_directory, code=code, identity_path=identity_path)
                raise KeyboardInterrupt("after dlopen before validation publication")

            with patch.object(
                    runtime_module, "_NATIVE_IMAGE_CACHE_LOAD_POISONED", False), \
                    patch.object(
                        runtime_module, "_NATIVE_IMAGE_CACHE_LOAD_FAILURE", None), \
                    patch.object(
                        runtime_module, "_remove_native_loader_alias",
                        side_effect=cleanup_then_interrupt):
                with self.assertRaisesRegex(
                        KeyboardInterrupt,
                        "after dlopen before validation publication"):
                    runtime_module._load_verified_native_file_descriptor(
                        images["fail"], expected_sha256=failed_digest,
                        code="RX005_BUILD_INPUT_INVALID",
                        identity_path="native.fail")
                failed_entry = runtime_module._NATIVE_IMAGE_CACHE[failed_digest]
                self.assertFalse(failed_entry.usable)
                self.assertIsNotNone(failed_entry.load_failure)
                marker = f"memfd:rtdl-native-{failed_digest[:16]}"
                rows_before = [
                    row for row in Path("/proc/self/maps").read_text(
                        encoding="utf-8").splitlines() if marker in row]
                self.assertGreater(len(rows_before), 0)
                with self.assertRaises(RTDLExecutableError) as retry:
                    runtime_module._load_verified_native_file_descriptor(
                        images["fail"], expected_sha256=failed_digest,
                        code="RX005_BUILD_INPUT_INVALID",
                        identity_path="native.fail.retry")
                self.assertEqual(
                    retry.exception.code, "RX048_NATIVE_CACHE_QUARANTINED")
                rows_after = [
                    row for row in Path("/proc/self/maps").read_text(
                        encoding="utf-8").splitlines() if marker in row]
                self.assertEqual(rows_after, rows_before)
                runtime_module._release_native_library_image(live)
                self.assertEqual(live._rtdl_native_cache_active_lease_count, 0)
            self.assertGreaterEqual(len(remove_calls), 1)

    def test_untimed_smoke_guard_admits_only_the_exact_sealed_private_alias(self):
        source = (ROOT / "scripts/goal5801_lx1_untimed_smoke.py").read_text(
            encoding="utf-8")
        self.assertIn(
            'r"rtdl-native-[0-9]+-[a-z0-9_]{8}"', source)
        self.assertIn('r"/proc/self/fd/[0-9]+", os.readlink(candidate)', source)
        self.assertIn("_sha_file(candidate) == exact_native_sha256", source)
        self.assertIn("sealed_native_alias or lowered", source)
        self.assertNotIn("label == exact_native or", source)
        self.assertNotIn("native_probe = ctypes.CDLL(exact_native)", source)
        self.assertIn("def _executing_dso_observation", source)
        self.assertIn("native_compiler_attempts_by_executing_dso", source)

    def test_untimed_smoke_exercises_native_digest_interrupt_window(self):
        source = (ROOT / "scripts/goal5801_lx1_untimed_smoke.py").read_text(
            encoding="utf-8")
        self.assertIn("relation.execute.interrupt_window_commit_b", source)
        self.assertIn("relation.execute.interrupt_window_rebuild_a", source)
        self.assertIn("triangle.execute.interrupt_window_rebuild_a", source)
        self.assertIn("triangle.execute.interrupt_window_repeat_a", source)
        self.assertIn("simulated_native_committed_batch", source)
        self.assertIn('"required_recovery_build_delta": 1', source)
        self.assertIn('"required_recovery_reused": False', source)

    def test_final_component_symlink_is_rejected_before_resolution(self):
        with tempfile.TemporaryDirectory(dir=self.root) as temporary:
            directory = Path(temporary)
            target = directory / "target.json"
            link = directory / "input.json"
            target.write_bytes(_canonical({"ok": True}) + b"\n")
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            with self.assertRaisesRegex(
                    RTDLExecutableError, "regular non-symlink file required"):
                runtime_module._read_regular_bytes_once(
                    link, code="RX023_ARTIFACT_INVALID")

    def test_close_failure_does_not_falsely_publish_closed_state(self):
        class ThrowingOwner:
            attempts = 0

            def close(self):
                self.attempts += 1
                if self.attempts == 1:
                    raise RuntimeError("injected destroy failure")

        owner = ThrowingOwner()
        prepared = runtime_module.PreparedRTDLExecutable(
            family="custom_aabb_bounded_relation_v1",
            executable_identity_sha256=_sha("close-retry"), owner=owner)
        with self.assertRaisesRegex(RuntimeError, "injected destroy failure"):
            prepared.close()
        self.assertFalse(prepared.closed)
        prepared.close()
        self.assertTrue(prepared.closed)
        self.assertEqual(owner.attempts, 2)

    def test_cache_hit_load_fresh_process_public_import_has_no_compiler_or_native_load(self):
        code = r'''
import ctypes, json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import rtdsl
from rtdsl import install_rtdlexe_deployment, load_rtdlexe
import rtdsl.v4_rtdlexe as runtime
def forbidden(*args, **kwargs):
    raise AssertionError("native/compiler dynamic library call on cache hit")
ctypes.CDLL = forbidden
runtime.ctypes.CDLL = forbidden
deployment = install_rtdlexe_deployment(
    trust_root_path=sys.argv[2], trust_head_path=sys.argv[3],
    trust_package_path=sys.argv[4], deployment_id="slot-A")
loaded = load_rtdlexe(sys.argv[5], authority_path=sys.argv[6], deployment=deployment)
forbidden_prefixes = ("numba", "llvmlite", "rtdsl.v4_callback_lifecycle",
    "rtdsl.v4_callback_numba_codegen", "rtdsl.v4_callback_optix_compiler",
    "rtdsl.v4_bounded_relation_optix_compiler", "rtdsl.v4_triangle_optix_compiler")
bad = sorted(name for name in sys.modules if name.startswith(forbidden_prefixes))
print(json.dumps({"bad": bad, "family": loaded.family}, sort_keys=True))
'''
        # This workspace's Windows launcher has a known broken isolated-prefix
        # configuration; a distinct PID still gives the required fresh import
        # trace.  POSIX uses isolated mode.
        interpreter = ["py"] if os.name == "nt" else [sys.executable, "-I"]
        completed = subprocess.run(
            [*interpreter, "-c", code, str(SRC), str(self.public), str(self.head_ab),
             str(self.package_ab), str(self.built_a.artifact_path), str(self.authority_a)],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout.strip())
        self.assertEqual(result["bad"], [])
        self.assertEqual(result["family"], "custom_aabb_bounded_relation_v1")

    def test_triangle_wrapper_identity_is_stable_across_python_hash_seeds(self):
        """Executable identity must not inherit set iteration order."""

        code = r'''
import json
from tests.goal5759_v4_triangle_reduction_target_test import (
    _compiled, all_hit_schema, compile_count_callback,
)
from rtdsl.v4_triangle_reduction_optix_wrapper_codegen import (
    generate_trusted_optix_triangle_reduction_wrapper_v1,
)
callback = compile_count_callback()
authority, proof, abi, contract = _compiled(callback, all_hit_schema(callback))
wrapper = generate_trusted_optix_triangle_reduction_wrapper_v1(
    authority, contract, abi, any_hit_proof_authority=proof,
)
print(json.dumps({
    "role_symbols": wrapper.role_symbols,
    "source_sha256": wrapper.source_sha256,
}, sort_keys=True))
'''
        observations = []
        for seed in ("1", "2", "3", "5", "17", "29"):
            environment = dict(os.environ)
            environment["PYTHONHASHSEED"] = seed
            environment["PYTHONPATH"] = os.pathsep.join(
                item for item in (
                    str(SRC), str(ROOT), environment.get("PYTHONPATH", ""),
                ) if item
            )
            completed = subprocess.run(
                [sys.executable, "-c", code],
                cwd=ROOT,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            observations.append(json.loads(completed.stdout))
        self.assertTrue(all(item == observations[0] for item in observations))
        self.assertEqual(
            [item[0] for item in observations[0]["role_symbols"]],
            ["make_ray", "any_hit", "miss", "finalize"],
        )

    def test_candidate_build_requires_a_strict_deployment_generation(self):
        from scripts import goal5801_lx1_untimed_smoke as smoke

        for invalid in ("", "v0", "1", "v1/other", "latest", "v01"):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    ValueError, "deployment generation"):
                smoke.build(SimpleNamespace(
                    output=self.root / "unused-candidate",
                    deployment_generation=invalid,
                ))
        source = (ROOT / "scripts/goal5801_lx1_untimed_smoke.py").read_text()
        self.assertIn(
            'builder.add_argument("--deployment-generation", required=True)',
            source,
        )

    def test_candidate_build_requires_and_binds_exact_relation_threshold(self):
        from rtdsl.v4 import (
            BoundedRelationProtocol,
            TriangleReductionMode,
            TriangleReductionProtocol,
        )
        from scripts import goal5801_lx1_untimed_smoke as smoke

        protocols = smoke._protocols(
            SimpleNamespace(
                deployment_generation="v3",
                relation_minimum_overlap_f32=1.0,
            ),
            BoundedRelationProtocol,
            TriangleReductionMode,
            TriangleReductionProtocol,
        )
        relation = protocols[0][2]
        self.assertEqual(relation.capacity, 4096)
        self.assertEqual(relation.minimum_overlap_f32, 1.0)
        source = (ROOT / "scripts/goal5801_lx1_untimed_smoke.py").read_text()
        self.assertIn('"rtdl.goal5801.lx1_untimed_candidate_manifest.v2"', source)
        self.assertIn('"minimum_overlap_f32_bits"', source)
        self.assertIn('"--relation-minimum-overlap-f32"', source)

        for invalid in (
                float("nan"), float("inf"), 1e100, -1.0, 0.1, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                smoke._relation_minimum_overlap_f32(invalid)


if __name__ == "__main__":
    unittest.main()
