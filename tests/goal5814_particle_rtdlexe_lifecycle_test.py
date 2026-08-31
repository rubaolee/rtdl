from __future__ import annotations

import base64
import ctypes
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import threading
import unittest
from unittest import mock

import numpy as np

from rtdsl import v4_particle_rtdlexe as particle


def _sha(label: str) -> str:
    return particle._sha_bytes(label.encode())


def _descriptor(source: bytes) -> bytes:
    value = {
        "schema": "rtdl.v4.particle_strict_interior_template.v1",
        "family": "builtin_triangle_particle_strict_interior_v1",
        "native_abi": "rtdl.v4.prepared_particle_strict_interior.v3",
        "semantic_sha256": _sha("semantic"),
        "source_sha256": particle._sha_bytes(source),
        "source_bytes": len(source),
        "entry_points": {
            "raygen": "__raygen__rtdl_particle_strict_interior",
            "closest_hit": "__closesthit__rtdl_particle_strict_interior",
            "miss": "__miss__rtdl_particle_strict_interior",
            "intersection": None,
            "any_hit": None,
        },
        "compile_options": {
            "language": "cuda_cxx14",
            "target": "compute_<target_cc>",
            "requires_optix_device_header": True,
        },
        "pipeline_options": {
            "uses_motion_blur": False,
            "traversable_graph": "single_gas",
            "payload_values": 2,
            "attribute_values": 2,
            "exception_flags": 0,
            "launch_params_symbol": "params",
            "primitive_type": "triangle",
            "max_trace_depth": 1,
        },
        "launch_parameter_layout": {
            "bytes": 120,
            "query_layout": "seven_soa_f32",
            "static_metadata_layout": "front_u32_back_u32_by_primitive",
            "output_layout": "selected_neighbor_face_three_soa_u32",
        },
        "domain": {
            "query_count": 5000,
            "unique_closest_face_required": True,
            "strictly_positive_barycentric_coordinates_required": True,
            "edge_or_vertex_hit": "OUTSIDE_DOMAIN_FAIL_CLOSED",
            "full_50000_step_advection": False,
        },
        "transfer_contract": {
            "query_h2d_bytes": 140000,
            "query_h2d_copy_call_count": 7,
            "optix_launch_count": 1,
            "control_d2h_bytes": 16,
            "control_before_output": True,
            "success_output_d2h_bytes": 60000,
            "failure_output_d2h_bytes": 0,
            "execute_abi_version": 3,
            "legacy_defensive_execute_abi_version": 2,
            "success_host_output": "borrowed_native_owned_pinned_packed_soa_u32",
            "borrowed_output_lifetime": "until_next_execute_or_destroy",
            "failure_host_output": "null_pointer_zero_rows",
        },
        "host_value_validation_contract": {
            "preferred_execute_symbol": (
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_"
                "prevalidated_v3"),
            "authority": (
                "product_public_registry_authenticated_token_over_"
                "immutable_bytes"),
            "admission_timing": "outside_execute",
            "admission_validates": [
                "seven_owned_read_only_c_contiguous_f32_5000",
                "all_query_values_finite", "positive_tmax",
                "nonzero_direction",
                "owned_read_only_c_contiguous_u32_5000x3_oracle",
            ],
            "native_revalidates": [
                "prepared_token", "query_count",
                "seven_non_null_query_pointers", "output_pointers",
            ],
            "native_skips_only": [
                "finite_value_rescan", "positive_tmax_rescan",
                "nonzero_direction_rescan",
            ],
            "legacy_defensive_execute_symbol": (
                "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2"),
            "legacy_native_value_scan": True,
        },
        "boundary_owner_table": {
            "present": False,
            "bytes": 0,
            "avoided_generic_table_bytes_at_frozen_scale": 94990840,
        },
    }
    return json.dumps(value, separators=(",", ":")).encode()


def _sealed_protocol() -> dict[str, object]:
    contract_body = {
        "schema": "rtdl.v4.callback_protocol_contract.v1",
        "family": "builtin_triangle_callback_ir",
        "task_semantics_sha256": _sha("task"),
        "role_effects": {},
        "attribute_abi_ownership": {},
        "physical_bindings": {},
        "continuation_policy": "REQUIRE_COMPLETE_BEFORE_CONSUME",
        "checked_executable_sha256": _sha("executable"),
    }
    contract = {
        **contract_body, "contract_sha256": particle._digest(contract_body)}
    projection_body = {
        "schema": "rtdl.v4.compiler_protocol_projection.v1",
        "family": "builtin_triangle_callback_ir",
        "task_semantics_sha256": _sha("task"),
        "role_effects": {},
        "attribute_abi_ownership": {},
        "physical_bindings": {},
        "continuation_policy": "REQUIRE_COMPLETE_BEFORE_CONSUME",
        "actual_executable_sha256": _sha("executable"),
        "generated_device_source_sha256": _sha("generic-ptx"),
        "generated_host_source_sha256": _sha("host"),
    }
    projection = {
        **projection_body,
        "projection_sha256": particle._digest(projection_body),
    }
    decision_body = {
        "schema": "rtdl.v4.callback_protocol_contract_decision.v1",
        "verdict": "ACCEPT",
        "findings": [],
        "contract_sha256": contract["contract_sha256"],
        "projection_sha256": projection["projection_sha256"],
        "executable_capability_issued": False,
    }
    decision = {
        **decision_body, "decision_sha256": particle._digest(decision_body)}
    return {
        "schema": "rtdl.v4.particle_standard_protocol_bundle.v1",
        "producer": "compile_standard_builtin_triangle_program",
        "callback_ir_sha256": _sha("callback"),
        "callback_effect_digest": _sha("effects"),
        "physical_schema_sha256": _sha("physical"),
        "canonical_plan_sha256": _sha("plan"),
        "callback_abi_sha256": _sha("abi"),
        "orientation_authority_sha256": _sha("orientation"),
        "generic_checked_executable_sha256": _sha("executable"),
        "generic_composed_ptx_sha256": _sha("generic-ptx"),
        "contract": contract,
        "projection": projection,
        "decision": decision,
    }


def _artifact(native_sha: str):
    source = b'extern "C" __global__ void particle() {}\n'
    descriptor_bytes = _descriptor(source)
    descriptor = json.loads(descriptor_bytes)
    protocol = _sealed_protocol()
    ptx = (
        b".version 7.0\n.target sm_61\n.address_size 64\n"
        b".visible .entry __raygen__rtdl_particle_strict_interior() {}\n"
        b".visible .entry __closesthit__rtdl_particle_strict_interior() {}\n"
        b".visible .entry __miss__rtdl_particle_strict_interior() {}\n"
    )
    specialization = particle._specialization_binding(
        protocol_bundle=protocol, descriptor=descriptor)
    build = {
        "schema": particle._BUILD_SCHEMA,
        "nvcc_executable_sha256": _sha("nvcc"),
        "nvcc_version_stdout_base64": base64.b64encode(b"nvcc test").decode(),
        "nvcc_version_stderr_base64": "",
        "optix_device_header_sha256": _sha("optix-header"),
        "source_sha256": particle._sha_bytes(source),
        "compiler_arguments_path_independent": ["nvcc@sha", "-ptx"],
        "independent_invocation_count": 2,
        "ptx_byte_identical": True,
        "ptx_sha256": particle._sha_bytes(ptx),
        "ptx_bytes": len(ptx),
    }
    value = {
        "schema": particle._ARTIFACT_SCHEMA,
        "format_version": 1,
        "native_library_sha256": native_sha,
        "source_sha256": particle._sha_bytes(source),
        "source_base64": base64.b64encode(source).decode(),
        "descriptor_sha256": particle._sha_bytes(descriptor_bytes),
        "descriptor_base64": base64.b64encode(descriptor_bytes).decode(),
        "template_semantic_sha256": descriptor["semantic_sha256"],
        "ptx_sha256": particle._sha_bytes(ptx),
        "ptx_base64": base64.b64encode(ptx).decode(),
        "standard_protocol": protocol,
        "specialization_binding": specialization,
        "build_identity": build,
    }
    return value, source, descriptor_bytes, ptx


def _write_artifact(directory: Path, value: Mapping[str, object]):
    raw = particle._canonical(value) + b"\n"
    digest = particle._sha_bytes(raw)
    path = directory / f"{digest}.rtdlexe"
    path.write_bytes(raw)
    return path, digest


class _FakeFunction:
    def __init__(self, callback):
        self.callback = callback
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        return self.callback(*args)


class _FakeLibrary:
    def __init__(self, source: bytes, descriptor: bytes, *, fail_status=False):
        self.calls: list[str] = []
        self.fail_status = fail_status
        self.output = (ctypes.c_uint32 * 15000)(
            *(index % 4294967295 for index in range(15000)))
        self.rtdl_optix_v4_particle_strict_interior_source_v1 = _FakeFunction(
            lambda *args: self._query("source", source, *args))
        self.rtdl_optix_v4_particle_strict_interior_descriptor_v1 = _FakeFunction(
            lambda *args: self._query("descriptor", descriptor, *args))
        self.rtdl_optix_v4_prepare_particle_strict_interior_v1 = _FakeFunction(
            self._prepare)
        self.rtdl_optix_v4_execute_prepared_particle_strict_interior_v2 = _FakeFunction(
            self._execute)
        self.rtdl_optix_v4_execute_prepared_particle_strict_interior_prevalidated_v3 = \
            _FakeFunction(self._execute_prevalidated)
        self.rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1 = _FakeFunction(
            self._destroy)

    def _query(self, name, payload, output, capacity, byte_count, error, error_size):
        self.calls.append(name)
        ctypes.cast(byte_count, ctypes.POINTER(ctypes.c_size_t))[0] = len(payload)
        if output is not None:
            ctypes.memmove(output, payload + b"\0", len(payload) + 1)
        return 0

    def _prepare(self, *args):
        self.calls.append("prepare")
        ctypes.cast(args[7], ctypes.POINTER(ctypes.c_uint64))[0] = 71
        return 0

    def _execute(self, *args):
        return self._execute_impl("execute", *args)

    def _execute_prevalidated(self, *args):
        return self._execute_impl("execute_prevalidated", *args)

    def _execute_impl(self, label, *args):
        self.calls.append(label)
        output_pointer = ctypes.cast(
            args[9], ctypes.POINTER(ctypes.POINTER(ctypes.c_uint32)))
        output_rows = ctypes.cast(args[10], ctypes.POINTER(ctypes.c_size_t))
        control = ctypes.cast(args[11], ctypes.POINTER(particle._ParticleControl))[0]
        receipt = ctypes.cast(
            args[12], ctypes.POINTER(particle._ParticleFastReceipt))[0]
        receipt.schema_version = 1
        receipt.optix_launch_count = 1
        receipt.query_count = 5000
        receipt.query_h2d_copy_call_count = 7
        receipt.control_reset_h2d_copy_call_count = 1
        receipt.parameter_h2d_copy_call_count = 1
        receipt.control_d2h_copy_call_count = 1
        receipt.query_h2d_bytes = 140000
        receipt.control_reset_h2d_bytes = 16
        receipt.parameter_h2d_bytes = 120
        receipt.control_d2h_bytes = 16
        receipt.output_d2h_after_status_failure = 0
        receipt.boundary_owner_table_bytes = 0
        receipt.status_before_output = 1
        control.first_error = 7 if self.fail_status else 0xFFFFFFFF
        control.error_code = 2 if self.fail_status else 0
        control.status = 1 if self.fail_status else 0
        control.validated_row_count = 4999 if self.fail_status else 5000
        if self.fail_status:
            output_pointer[0] = ctypes.POINTER(ctypes.c_uint32)()
            output_rows[0] = 0
            receipt.output_d2h_copy_call_count = 0
            receipt.output_d2h_bytes = 0
            receipt.host_blocking_boundary_count = 1
        else:
            output_pointer[0] = ctypes.cast(
                self.output, ctypes.POINTER(ctypes.c_uint32))
            output_rows[0] = 5000
            receipt.output_d2h_copy_call_count = 1
            receipt.output_d2h_bytes = 60000
            receipt.host_blocking_boundary_count = 2
        return 0

    def _destroy(self, token, error, error_size):
        self.calls.append("destroy")
        ctypes.cast(token, ctypes.POINTER(ctypes.c_uint64))[0] = 0
        return 0


class _FakeImage:
    def __init__(self, library, sha):
        self.library = library
        self.sha256 = sha
        self.closed = False

    def close(self):
        self.closed = True


class _NoElementIteration(np.ndarray):
    def __iter__(self):  # pragma: no cover
        raise AssertionError("element iteration forbidden")

    def tolist(self):  # pragma: no cover
        raise AssertionError("tolist forbidden")


class Goal5814ParticleRTDLExecutableLifecycleTest(unittest.TestCase):
    def test_package_lazy_surface_is_public(self):
        import rtdsl
        self.assertIs(rtdsl.build_particle_rtdlexe, particle.build_particle_rtdlexe)
        self.assertIs(
            rtdsl.install_particle_rtdlexe_deployment,
            particle.install_particle_rtdlexe_deployment)
        self.assertIs(rtdsl.load_particle_rtdlexe, particle.load_particle_rtdlexe)
        self.assertIs(
            rtdsl.prevalidate_particle_rtdlexe_exact_core_input,
            particle.prevalidate_particle_rtdlexe_exact_core_input)
        self.assertIs(
            rtdsl.ParticleDeviceStatusError,
            particle.ParticleDeviceStatusError)
        self.assertIs(
            rtdsl.ParticleExactCoreCompletion,
            particle.ParticleExactCoreCompletion)
        self.assertIs(
            rtdsl.PrevalidatedParticleRTDLExecutionInput,
            particle.PrevalidatedParticleRTDLExecutionInput)

    def test_build_entrypoint_uses_frozen_loader_oracle_binding(self):
        root = Path(__file__).resolve().parents[1]
        builder_path = (
            root / "experiments" / "goal5814_particle_tracking"
            / "build_particle_rtdlexe.py")
        spec = importlib.util.spec_from_file_location(
            "goal5814_build_particle_rtdlexe_test", builder_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        policy_path = (
            root / "history" / "internal_docs"
            / "goal5814_particle_tracking_scientific_scope_and_measurement_policy_preaction_20260828.json")
        policy, _raw = builder._load_controlling_policy(policy_path)
        self.assertEqual(
            policy["controlling_input"]["loader_oracle_binding_sha256"],
            builder.LOADER_ORACLE_BINDING_SHA256)
        self.assertNotEqual(
            builder.LOADER_ORACLE_BINDING_SHA256,
            builder.INDEPENDENT_ORACLE_VERIFIER_SHA256)
        source = builder_path.read_text(encoding="utf-8")
        self.assertIn(
            "independent_oracle_sha256=LOADER_ORACLE_BINDING_SHA256", source)

    def test_external_manifest_hash_is_checked_before_trusting_identities(self):
        root = Path(__file__).resolve().parents[1]
        verifier_path = (
            root / "experiments" / "goal5814_particle_tracking"
            / "verify_particle_rtdlexe_manifest.py")
        spec = importlib.util.spec_from_file_location(
            "goal5814_verify_particle_rtdlexe_manifest_test", verifier_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        body = {
            "schema": (
                "rtdl.goal5814.particle_strict_interior_executable_manifest.v1"),
            "identities": {"artifact_sha256": _sha("artifact")},
        }
        value = {
            **body,
            "manifest_body_sha256": verifier._sha_bytes(
                verifier._canonical(body)),
        }
        raw = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
        with tempfile.TemporaryDirectory() as raw_directory:
            path = Path(raw_directory) / "manifest.json"
            path.write_bytes(raw)
            self.assertEqual(
                verifier._load_manifest(path, verifier._sha_bytes(raw)), value)
            with self.assertRaisesRegex(
                    RuntimeError,
                    "EXTERNAL_EXECUTABLE_MANIFEST_IDENTITY_MISMATCH"):
                verifier._load_manifest(path, _sha("wrong-manifest"))

    def _loaded(self, directory: Path, *, fail_status=False):
        native_sha = _sha("native")
        artifact, source, descriptor, _ptx = _artifact(native_sha)
        path, artifact_sha = _write_artifact(directory, artifact)
        fake = _FakeLibrary(source, descriptor, fail_status=fail_status)
        image = _FakeImage(fake, native_sha)
        deployment = particle.install_particle_rtdlexe_deployment(
            deployment_id="formal-D",
            expected_artifact_sha256=artifact_sha,
            expected_native_sha256=native_sha,
            expected_protocol_decision_sha256=(
                artifact["standard_protocol"]["decision"]["decision_sha256"]),
            expected_template_semantic_sha256=artifact["template_semantic_sha256"],
        )
        with mock.patch.object(particle, "_open_verified_native", return_value=image):
            loaded = particle.load_particle_rtdlexe(
                path, deployment=deployment, native_library_path=directory / "native.so")
        return loaded, fake, image, artifact, deployment

    def test_load_prepare_execute_close_uses_only_product_abis(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            loaded, fake, image, artifact, _deployment = self._loaded(directory)
            vertices = np.zeros((3, 3), dtype="<f4")
            triangles = np.asarray(((0, 1, 2),), dtype="<u4")
            front = np.asarray((10,), dtype="<u4")
            back = np.asarray((11,), dtype="<u4")
            for value in (vertices, triangles, front, back):
                value.setflags(write=False)
            static = particle.ParticleStaticInput(
                vertices, triangles, front, back)
            columns = tuple(
                np.zeros(5000, dtype="<f4").view(_NoElementIteration)
                for _ in range(7))
            for column in columns:
                column.setflags(write=False)
            prepared = loaded.prepare(static)
            result = prepared.execute(*columns)
            self.assertEqual(result.output_u32x3.shape, (5000, 3))
            self.assertFalse(result.output_u32x3.flags.writeable)
            packed = np.ctypeslib.as_array(fake.output).reshape(3, 5000)
            self.assertTrue(np.shares_memory(result.output_u32x3, packed))
            self.assertTrue(np.array_equal(result.output_u32x3, packed.T))
            self.assertEqual(result.receipt["query_h2d_copy_call_count"], 7)
            self.assertEqual(result.receipt["output_d2h_bytes"], 60000)
            expected = packed.T.copy()
            expected.setflags(write=False)
            completed = prepared.execute_complete(
                *columns, expected_u32x3=expected)
            self.assertTrue(np.shares_memory(completed.output_u32x3, packed))
            self.assertEqual(loaded.ptx_bytes, base64.b64decode(artifact["ptx_base64"]))
            prepared.close()
            prepared.close()
            self.assertTrue(prepared.closed)
            loaded.close()
            loaded.close()
            self.assertTrue(image.closed)
            self.assertEqual(fake.calls.count("execute"), 2)
            self.assertEqual(set(fake.calls), {
                "source", "descriptor", "prepare", "execute", "destroy"})

    def test_prevalidated_exact_core_uses_only_v3_and_immutable_bytes(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, fake, _image, _artifact, _deployment = self._loaded(
                Path(raw_directory))
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            columns = [np.zeros(5000, dtype="<f4") for _ in range(7)]
            columns[5].fill(np.float32(-1.0))
            columns[6].fill(np.float32(10.0))
            expected = np.ctypeslib.as_array(
                fake.output).reshape(3, 5000).T.copy()
            for value in (*columns, expected):
                value.setflags(write=False)
            expected = expected.view()
            self.assertFalse(expected.flags.owndata)
            prepared = loaded.prepare(static)
            admitted = prepared.prevalidate_exact_core_input(
                *columns, expected_u32x3=expected)
            self.assertIsInstance(
                admitted, particle.PrevalidatedParticleRTDLExecutionInput)
            self.assertTrue(all(
                isinstance(item.base, bytes)
                for item in (*admitted.columns, admitted.expected_u32x3)))
            self.assertTrue(all(
                not item.flags.writeable
                for item in (*admitted.columns, admitted.expected_u32x3)))
            with self.assertRaises(ValueError):
                admitted.columns[0].setflags(write=True)
            with self.assertRaises(particle.ParticleRTDLExecutableError):
                admitted._columns = ()
            with self.assertRaises(particle.ParticleRTDLExecutableError):
                particle.PrevalidatedParticleRTDLExecutionInput()

            completion = prepared.execute_exact_core_prevalidated(admitted)
            result = prepared.materialize_exact_core_completion(completion)
            self.assertTrue(np.array_equal(result.output_u32x3, expected))
            self.assertEqual(fake.calls.count("execute_prevalidated"), 1)
            self.assertEqual(fake.calls.count("execute"), 0)

            forged = object.__new__(
                particle.PrevalidatedParticleRTDLExecutionInput)
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                prepared.execute_exact_core_prevalidated(forged)
            self.assertEqual(
                rejected.exception.code, "PX024_PREVALIDATED_INPUT_INVALID")
            prepared.close()
            loaded.close()

    def test_prevalidation_rejects_subclass_and_snapshots_nonowned_storage(self):
        class SpoofedBytes(np.ndarray):
            tobytes_called = False

            def tobytes(self, *args, **kwargs):
                type(self).tobytes_called = True
                return bytes(self.nbytes)

        columns = [np.zeros(5000, dtype="<f4") for _ in range(7)]
        columns[5].fill(np.float32(-1.0))
        columns[6].fill(np.float32(10.0))
        expected = np.zeros((5000, 3), dtype="<u4")
        spoofed = np.ndarray.__new__(SpoofedBytes, (5000,), dtype="<f4")
        spoofed.fill(np.float32(10.0))
        spoofed.setflags(write=False)
        columns[6] = spoofed
        for value in (*columns[:6], expected):
            value.setflags(write=False)
        with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
            particle.prevalidate_particle_rtdlexe_exact_core_input(
                *columns, expected_u32x3=expected)
        self.assertEqual(
            rejected.exception.code, "PX024_PREVALIDATED_INPUT_INVALID")
        self.assertFalse(SpoofedBytes.tobytes_called)

        columns[6] = np.full(5000, 10.0, dtype="<f4")
        backing = np.zeros(5001, dtype="<f4")
        nonowned = backing[:5000]
        nonowned.setflags(write=False)
        columns[0] = nonowned
        columns[6].setflags(write=False)
        admitted = particle.prevalidate_particle_rtdlexe_exact_core_input(
            *columns, expected_u32x3=expected)
        backing.fill(np.float32(13.0))
        sealed_columns, _sealed_expected = \
            particle._require_prevalidated_particle_rtdlexe_input(
                np, admitted)
        self.assertEqual(float(sealed_columns[0].max()), 0.0)

    def test_prevalidated_token_uses_snapshot_not_later_caller_mutation(self):
        columns = [np.zeros(5000, dtype="<f4") for _ in range(7)]
        columns[5].fill(np.float32(-1.0))
        columns[6].fill(np.float32(10.0))
        expected = np.zeros((5000, 3), dtype="<u4")
        for value in (*columns, expected):
            value.setflags(write=False)
        admitted = particle.prevalidate_particle_rtdlexe_exact_core_input(
            *columns, expected_u32x3=expected)
        columns[6].setflags(write=True)
        columns[6].fill(np.float32(0.0))
        expected.setflags(write=True)
        expected.fill(np.uint32(9))
        sealed_columns, sealed_expected = \
            particle._require_prevalidated_particle_rtdlexe_input(
                np, admitted)
        self.assertEqual(float(sealed_columns[6].min()), 10.0)
        self.assertTrue(np.array_equal(
            sealed_expected, np.zeros((5000, 3), dtype="<u4")))

    def test_complete_prevalidated_returns_full_immutable_result_without_completion_registry(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, fake, _image, _artifact, _deployment = self._loaded(
                Path(raw_directory))
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            columns = [np.zeros(5000, dtype="<f4") for _ in range(7)]
            columns[5].fill(np.float32(-1.0))
            columns[6].fill(np.float32(10.0))
            expected = np.ctypeslib.as_array(
                fake.output).reshape(3, 5000).T.copy()
            for value in (*columns, expected):
                value.setflags(write=False)
            prepared = loaded.prepare(static)
            admitted = prepared.prevalidate_exact_core_input(
                *columns, expected_u32x3=expected)
            with mock.patch.object(
                    particle, "_new_particle_core_completion",
                    wraps=particle._new_particle_core_completion) as completion:
                result = prepared.execute_complete_prevalidated(admitted)
                self.assertEqual(completion.call_count, 0)
                complete = prepared.execute_complete(
                    *columns, expected_u32x3=expected)
                self.assertEqual(completion.call_count, 0)
            self.assertTrue(np.array_equal(result.output_u32x3, expected))
            self.assertTrue(np.array_equal(complete.output_u32x3, expected))
            self.assertEqual(result.receipt, particle._SUCCESS_RECEIPT_VALUES)
            with self.assertRaises(TypeError):
                result.receipt["output_d2h_bytes"] = 0
            self.assertEqual(fake.calls.count("execute_prevalidated"), 1)
            self.assertEqual(fake.calls.count("execute"), 1)
            prepared.close()
            loaded.close()

    def test_complete_public_rejects_dispatchable_ndarray_subclasses(self):
        class ForgedPredicates(np.ndarray):
            dispatch_count = 0

            def __array_function__(self, function, types, args, kwargs):
                type(self).dispatch_count += 1
                if function is np.shares_memory:
                    return False
                if function is np.array_equal:
                    return True
                return super().__array_function__(
                    function, types, args, kwargs)

        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, fake, _image, _artifact, _deployment = self._loaded(
                Path(raw_directory))
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            columns = [np.zeros(5000, dtype="<f4") for _ in range(7)]
            columns[5].fill(np.float32(-1.0))
            columns[6].fill(np.float32(10.0))
            expected = np.ctypeslib.as_array(
                fake.output).reshape(3, 5000).T.copy()
            prepared = loaded.prepare(static)

            wrong = np.ones((5000, 3), dtype="<u4").view(
                ForgedPredicates)
            with self.assertRaises(
                    particle.ParticleRTDLExecutableError) as rejected:
                prepared.execute_exact_core(
                    *columns, expected_u32x3=wrong)
            self.assertEqual(rejected.exception.code, "PX072_EXACT_ORACLE_MISMATCH")
            self.assertEqual(fake.calls.count("execute"), 1)

            with self.assertRaises(
                    particle.ParticleRTDLExecutableError) as rejected:
                prepared.execute_complete(
                    *columns, expected_u32x3=wrong)
            self.assertEqual(rejected.exception.code, "PX072_EXACT_ORACLE_MISMATCH")
            self.assertEqual(fake.calls.count("execute"), 2)
            self.assertEqual(ForgedPredicates.dispatch_count, 0)

            forged_column = columns[0].view(ForgedPredicates)
            exact_core = prepared.execute_exact_core(
                forged_column, *columns[1:], expected_u32x3=expected)
            prepared.materialize_exact_core_completion(exact_core)
            exact_from_subclass = prepared.execute_complete(
                forged_column, *columns[1:], expected_u32x3=expected)
            self.assertTrue(np.array_equal(
                exact_from_subclass.output_u32x3, expected))
            self.assertEqual(ForgedPredicates.dispatch_count, 0)

            exact = prepared.execute_complete(
                *columns, expected_u32x3=expected)
            self.assertTrue(np.array_equal(exact.output_u32x3, expected))
            self.assertEqual(fake.calls.count("execute"), 5)
            prepared.close()
            loaded.close()

    def test_all_native_facing_arrays_sanitize_forged_subclass_metadata(self):
        class ForgedFlags:
            c_contiguous = True

        class ForgedCtypes:
            data = 1

        class ForgedStorage(np.ndarray):
            fake_dtype = None
            fake_ndim = None
            fake_shape = None

            @property
            def dtype(self):
                return self.fake_dtype

            @property
            def ndim(self):
                return self.fake_ndim

            @property
            def flags(self):
                return ForgedFlags()

            @property
            def shape(self):
                return self.fake_shape

            @property
            def ctypes(self):
                return ForgedCtypes()

        def forged(dtype, shape):
            value = np.zeros(1, dtype=np.uint8).view(ForgedStorage)
            value.fake_dtype = np.dtype(dtype)
            value.fake_ndim = len(shape)
            value.fake_shape = shape
            return value

        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, fake, _image, _artifact, _deployment = self._loaded(
                Path(raw_directory))
            vertices = forged("<f4", (1, 3))
            triangles = forged("<u4", (1, 3))
            front = forged("<u4", (1,))
            back = forged("<u4", (1,))
            with self.assertRaises(
                    particle.ParticleRTDLExecutableError) as rejected:
                particle.ParticleStaticInput(
                    vertices, triangles, front, back)
            self.assertEqual(rejected.exception.code, "PX021_BULK_INPUT_REQUIRED")
            self.assertEqual(fake.calls.count("prepare"), 0)

            safe_static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            prepared = loaded.prepare(safe_static)
            forged_query = forged("<f4", (5000,))
            with self.assertRaises(
                    particle.ParticleRTDLExecutableError) as rejected:
                prepared.execute(*(forged_query,) * 7)
            self.assertEqual(rejected.exception.code, "PX021_BULK_INPUT_REQUIRED")
            self.assertEqual(fake.calls.count("execute"), 0)

            class ForgedStaticInput(particle.ParticleStaticInput):
                pass

            forged_static = ForgedStaticInput(
                safe_static.vertices_f32, safe_static.triangles_u32,
                safe_static.front_values_u32, safe_static.back_values_u32)
            with self.assertRaises(
                    particle.ParticleRTDLExecutableError) as rejected:
                loaded.prepare(forged_static)
            self.assertEqual(rejected.exception.code, "PX020_STATIC_INPUT_INVALID")
            self.assertEqual(fake.calls.count("prepare"), 1)
            prepared.close()
            loaded.close()

    def test_complete_prevalidated_rejects_status_oracle_and_forged_token(self):
        for fail_status in (False, True):
            with self.subTest(fail_status=fail_status), \
                    tempfile.TemporaryDirectory() as raw_directory:
                loaded, fake, _image, _artifact, _deployment = self._loaded(
                    Path(raw_directory), fail_status=fail_status)
                static = particle.ParticleStaticInput(
                    np.zeros((3, 3), dtype="<f4"),
                    np.asarray(((0, 1, 2),), dtype="<u4"),
                    np.asarray((10,), dtype="<u4"),
                    np.asarray((11,), dtype="<u4"),
                )
                columns = [np.zeros(5000, dtype="<f4") for _ in range(7)]
                columns[5].fill(np.float32(-1.0))
                columns[6].fill(np.float32(10.0))
                expected = np.ctypeslib.as_array(
                    fake.output).reshape(3, 5000).T.copy()
                if not fail_status:
                    expected[0, 0] ^= np.uint32(1)
                for value in (*columns, expected):
                    value.setflags(write=False)
                prepared = loaded.prepare(static)
                admitted = prepared.prevalidate_exact_core_input(
                    *columns, expected_u32x3=expected)
                if fail_status:
                    with self.assertRaises(
                            particle.ParticleDeviceStatusError) as rejected:
                        prepared.execute_complete_prevalidated(admitted)
                    self.assertEqual(
                        rejected.exception.receipt["output_d2h_bytes"], 0)
                    self.assertEqual(
                        rejected.exception.receipt[
                            "output_d2h_after_status_failure"], 0)
                else:
                    with self.assertRaises(
                            particle.ParticleRTDLExecutableError) as rejected:
                        prepared.execute_complete_prevalidated(admitted)
                    self.assertEqual(
                        rejected.exception.code, "PX072_EXACT_ORACLE_MISMATCH")
                forged = object.__new__(
                    particle.PrevalidatedParticleRTDLExecutionInput)
                with self.assertRaises(
                        particle.ParticleRTDLExecutableError) as rejected:
                    prepared.execute_complete_prevalidated(forged)
                self.assertEqual(
                    rejected.exception.code, "PX024_PREVALIDATED_INPUT_INVALID")
                prepared.close()
                loaded.close()

    def test_success_receipt_fast_path_rejects_every_mutated_abi_field(self):
        control = particle._ParticleControl(
            validated_row_count=5000,
            first_error=0xFFFFFFFF,
            error_code=0,
            status=0,
        )
        output = ctypes.c_uint32(7)
        output_pointer = ctypes.pointer(output)
        for field_name, _ctype in particle._ParticleFastReceipt._fields_:
            with self.subTest(field=field_name):
                receipt = particle._ParticleFastReceipt.from_buffer_copy(
                    particle._SUCCESS_RECEIPT_BYTES)
                setattr(receipt, field_name, getattr(receipt, field_name) + 1)
                with self.assertRaises(
                        particle.ParticleRTDLExecutableError) as rejected:
                    particle._validate_receipt(
                        control, receipt, output_pointer=output_pointer,
                        output_rows=5000)
                self.assertEqual(rejected.exception.code, "PX070_RECEIPT_INVALID")
        receipt = particle._ParticleFastReceipt.from_buffer_copy(
            particle._SUCCESS_RECEIPT_BYTES)
        for pointer, rows in ((None, 5000), (output_pointer, 4999)):
            with self.subTest(pointer=pointer is not None, rows=rows):
                with self.assertRaises(
                        particle.ParticleRTDLExecutableError) as rejected:
                    particle._validate_receipt(
                        control, receipt, output_pointer=pointer,
                        output_rows=rows)
                self.assertEqual(rejected.exception.code, "PX070_RECEIPT_INVALID")

    def test_exact_core_defers_receipt_and_identity_materialization(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            loaded, fake, _image, _artifact, _deployment = self._loaded(directory)
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            columns = tuple(np.zeros(5000, dtype="<f4") for _ in range(7))
            expected = np.ctypeslib.as_array(
                fake.output).reshape(3, 5000).T.copy()
            prepared = loaded.prepare(static)
            with mock.patch.object(
                    particle, "_validate_receipt",
                    wraps=particle._validate_receipt) as validate:
                completion = prepared.execute_exact_core(
                    *columns, expected_u32x3=expected)
                self.assertIsInstance(
                    completion, particle.ParticleExactCoreCompletion)
                self.assertFalse(hasattr(completion, "output_u32x3"))
                self.assertEqual(validate.call_count, 0)
                result = prepared.materialize_exact_core_completion(completion)
                self.assertEqual(validate.call_count, 1)
            self.assertEqual(result.artifact_sha256, loaded.artifact_sha256)
            self.assertEqual(result.ptx_sha256, loaded.ptx_sha256)
            self.assertEqual(result.receipt["output_d2h_bytes"], 60_000)
            self.assertTrue(np.array_equal(result.output_u32x3, expected))
            with self.assertRaises(particle.ParticleRTDLExecutableError):
                particle.ParticleExactCoreCompletion()
            prepared.close()
            loaded.close()

    def test_exact_core_rejects_forged_foreign_and_stale_completions(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, fake, _image, _artifact, _deployment = self._loaded(
                Path(raw_directory))
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            columns = tuple(np.zeros(5000, dtype="<f4") for _ in range(7))
            expected = np.ctypeslib.as_array(
                fake.output).reshape(3, 5000).T.copy()
            first_owner = loaded.prepare(static)
            second_owner = loaded.prepare(static)
            stale = first_owner.execute_exact_core(
                *columns, expected_u32x3=expected)
            current = first_owner.execute_exact_core(
                *columns, expected_u32x3=expected)
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                first_owner.materialize_exact_core_completion(stale)
            self.assertEqual(rejected.exception.code, "PX061_LIFECYCLE_STATE_INVALID")
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                second_owner.materialize_exact_core_completion(current)
            self.assertEqual(rejected.exception.code, "PX061_LIFECYCLE_STATE_INVALID")
            forged = object.__new__(particle.ParticleExactCoreCompletion)
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                first_owner.materialize_exact_core_completion(forged)
            self.assertEqual(rejected.exception.code, "PX061_LIFECYCLE_STATE_INVALID")
            first_owner.materialize_exact_core_completion(current)
            first_owner.close()
            second_owner.close()
            loaded.close()

    def test_exact_core_status_failure_keeps_public_failure_evidence(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, _fake, _image, _artifact, _deployment = self._loaded(
                Path(raw_directory), fail_status=True)
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            prepared = loaded.prepare(static)
            columns = tuple(np.zeros(5000, dtype="<f4") for _ in range(7))
            expected = np.zeros((5000, 3), dtype="<u4")
            with self.assertRaises(particle.ParticleDeviceStatusError) as rejected:
                prepared.execute_exact_core(
                    *columns, expected_u32x3=expected)
            self.assertEqual(rejected.exception.receipt[
                "output_d2h_copy_call_count"], 0)
            self.assertEqual(rejected.exception.receipt["output_d2h_bytes"], 0)
            prepared.close()
            loaded.close()

    def test_strided_query_is_rejected_but_const_inputs_are_accepted(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, _fake, _image, _artifact_value, _deployment = self._loaded(
                Path(raw_directory))
            static_columns = (
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            for value in static_columns:
                value.setflags(write=False)
            prepared = loaded.prepare(particle.ParticleStaticInput(*static_columns))
            columns = tuple(np.zeros(5000, dtype="<f4") for _ in range(7))
            for column in columns:
                column.setflags(write=False)
            expected = np.ctypeslib.as_array(
                _FakeLibrary(
                    b"source", b"descriptor").output).reshape(3, 5000).T.copy()
            expected.setflags(write=False)
            # The normal fake output is deterministic and has the same values.
            prepared.execute_complete(*columns, expected_u32x3=expected)
            strided = np.zeros(10000, dtype="<f4")[::2]
            strided.setflags(write=False)
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                prepared.execute(strided, *columns[1:])
            self.assertEqual(rejected.exception.code, "PX021_BULK_INPUT_REQUIRED")
            prepared.close()
            loaded.close()

    def test_formal_oracle_rejects_previous_borrowed_output_alias(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, _fake, _image, _artifact_value, _deployment = self._loaded(
                Path(raw_directory))
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            prepared = loaded.prepare(static)
            columns = tuple(np.zeros(5000, dtype="<f4") for _ in range(7))
            previous = prepared.execute(*columns)
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                prepared.execute_complete(
                    *columns, expected_u32x3=previous.output_u32x3)
            self.assertEqual(rejected.exception.code, "PX073_ORACLE_ALIASES_OUTPUT")
            prepared.close()
            loaded.close()

    def test_formal_oracle_comparison_holds_owner_lock(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, fake, _image, _artifact_value, _deployment = self._loaded(
                Path(raw_directory))
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            prepared = loaded.prepare(static)
            columns = tuple(np.zeros(5000, dtype="<f4") for _ in range(7))
            expected = np.ctypeslib.as_array(fake.output).reshape(3, 5000).T.copy()
            comparison_entered = threading.Event()
            release_comparison = threading.Event()
            completed = []
            failures = []
            real_array_equal = np.array_equal

            def blocked_array_equal(left, right):
                comparison_entered.set()
                if not release_comparison.wait(timeout=5):
                    raise AssertionError("test did not release formal oracle")
                return real_array_equal(left, right)

            def formal_worker():
                try:
                    completed.append(prepared.execute_complete(
                        *columns, expected_u32x3=expected))
                except BaseException as exc:  # pragma: no cover - diagnostic
                    failures.append(exc)

            with mock.patch.object(np, "array_equal", side_effect=blocked_array_equal):
                worker = threading.Thread(target=formal_worker)
                worker.start()
                self.assertTrue(comparison_entered.wait(timeout=5))
                with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                    prepared.execute(*columns)
                self.assertEqual(
                    rejected.exception.code, "PX061_LIFECYCLE_STATE_INVALID")
                release_comparison.set()
                worker.join(timeout=5)
            self.assertFalse(worker.is_alive())
            self.assertEqual(failures, [])
            self.assertEqual(len(completed), 1)
            prepared.close()
            loaded.close()

    def test_status_failure_withholds_borrowed_output(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            loaded, fake, _image, _artifact_value, _deployment = self._loaded(
                Path(raw_directory), fail_status=True)
            static = particle.ParticleStaticInput(
                np.zeros((3, 3), dtype="<f4"),
                np.asarray(((0, 1, 2),), dtype="<u4"),
                np.asarray((10,), dtype="<u4"),
                np.asarray((11,), dtype="<u4"),
            )
            prepared = loaded.prepare(static)
            columns = tuple(np.zeros(5000, dtype="<f4") for _ in range(7))
            with self.assertRaises(particle.ParticleDeviceStatusError) as rejected:
                prepared.execute(*columns)
            self.assertEqual(rejected.exception.code, "PX071_DEVICE_STATUS_FAILED")
            self.assertEqual(dict(rejected.exception.control), {
                "validated_row_count": 4999,
                "first_error": 7,
                "error_code": 2,
                "status": 1,
            })
            self.assertEqual(
                rejected.exception.receipt["status_before_output"], 1)
            self.assertEqual(
                rejected.exception.receipt["output_d2h_copy_call_count"], 0)
            self.assertEqual(rejected.exception.receipt["output_d2h_bytes"], 0)
            self.assertEqual(
                rejected.exception.receipt["host_blocking_boundary_count"], 1)
            with self.assertRaises(TypeError):
                rejected.exception.receipt["output_d2h_bytes"] = 60000
            prepared.close()
            loaded.close()
            self.assertEqual(fake.calls[-2:], ["execute", "destroy"])

    def test_external_capability_is_immutable_and_unforgeable_by_clone(self):
        cap = particle.install_particle_rtdlexe_deployment(
            deployment_id="slot-D",
            expected_artifact_sha256=_sha("artifact"),
            expected_native_sha256=_sha("native"),
            expected_protocol_decision_sha256=_sha("decision"),
            expected_template_semantic_sha256=_sha("semantic"),
        )
        with self.assertRaises(particle.ParticleRTDLExecutableError) as mutated:
            cap.expected_artifact_sha256 = _sha("forged")
        self.assertEqual(mutated.exception.code, "PX010_DEPLOYMENT_AUTHORITY_MISMATCH")
        clone = object.__new__(particle.InstalledParticleRTDLDeployment)
        for name, value in (
            ("_deployment_id", cap.deployment_id),
            ("_expected_artifact_sha256", cap.expected_artifact_sha256),
            ("_expected_native_sha256", cap.expected_native_sha256),
            ("_expected_protocol_decision_sha256", cap.expected_protocol_decision_sha256),
            ("_expected_template_semantic_sha256", cap.expected_template_semantic_sha256),
            ("_token", particle._DEPLOYMENT_TOKEN),
        ):
            object.__setattr__(clone, name, value)
        with self.assertRaises(particle.ParticleRTDLExecutableError) as unissued:
            particle._require_installed_deployment(clone)
        self.assertEqual(unissued.exception.code, "PX010_DEPLOYMENT_AUTHORITY_MISMATCH")

    def test_coherent_full_reseal_forgery_fails_at_external_authority(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            native_sha = _sha("native")
            original, _source, _descriptor_bytes, _ptx = _artifact(native_sha)
            _path, original_sha = _write_artifact(directory, original)
            deployment = particle.install_particle_rtdlexe_deployment(
                deployment_id="slot-D",
                expected_artifact_sha256=original_sha,
                expected_native_sha256=native_sha,
                expected_protocol_decision_sha256=(
                    original["standard_protocol"]["decision"]["decision_sha256"]),
                expected_template_semantic_sha256=original["template_semantic_sha256"],
            )
            forged = json.loads(json.dumps(original))
            forged_ptx = b"// coherently forged ptx\n"
            forged["ptx_base64"] = base64.b64encode(forged_ptx).decode()
            forged["ptx_sha256"] = particle._sha_bytes(forged_ptx)
            forged["build_identity"]["ptx_sha256"] = forged["ptx_sha256"]
            forged["build_identity"]["ptx_bytes"] = len(forged_ptx)
            forged_path, forged_sha = _write_artifact(directory, forged)
            self.assertNotEqual(forged_sha, original_sha)
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                particle.load_particle_rtdlexe(
                    forged_path, deployment=deployment,
                    native_library_path=directory / "native.so")
            self.assertEqual(
                rejected.exception.code, "PX010_DEPLOYMENT_AUTHORITY_MISMATCH")

    def test_ptx_and_descriptor_member_tamper_are_rejected(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            loaded, _fake, _image, artifact, deployment = self._loaded(directory)
            loaded.close()
            for member in ("ptx_base64", "descriptor_base64"):
                with self.subTest(member=member):
                    tampered = json.loads(json.dumps(artifact))
                    tampered[member] = base64.b64encode(b"tampered").decode()
                    path, _sha_value = _write_artifact(directory, tampered)
                    with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                        particle.load_particle_rtdlexe(
                            path, deployment=deployment,
                            native_library_path=directory / "native.so")
                    self.assertEqual(
                        rejected.exception.code,
                        "PX010_DEPLOYMENT_AUTHORITY_MISMATCH")

    def test_coherently_resealed_ptx_nul_tail_is_not_executable_text(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            native_sha = _sha("native")
            artifact, _source, _descriptor_bytes, ptx = _artifact(native_sha)
            forged_ptx = ptx + b"\0ignored-tail"
            artifact["ptx_base64"] = base64.b64encode(forged_ptx).decode()
            artifact["ptx_sha256"] = particle._sha_bytes(forged_ptx)
            artifact["build_identity"]["ptx_sha256"] = artifact["ptx_sha256"]
            artifact["build_identity"]["ptx_bytes"] = len(forged_ptx)
            path, artifact_sha = _write_artifact(directory, artifact)
            deployment = particle.install_particle_rtdlexe_deployment(
                deployment_id="externally-frozen-forged-negative-kat",
                expected_artifact_sha256=artifact_sha,
                expected_native_sha256=native_sha,
                expected_protocol_decision_sha256=(
                    artifact["standard_protocol"]["decision"]["decision_sha256"]),
                expected_template_semantic_sha256=(
                    artifact["template_semantic_sha256"]),
            )
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                particle.load_particle_rtdlexe(
                    path, deployment=deployment,
                    native_library_path=directory / "native.so")
            self.assertEqual(rejected.exception.code, "PX008_EMBEDDED_TEXT_INVALID")

    def test_coherently_resealed_extra_ptx_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            native_sha = _sha("native")
            artifact, _source, _descriptor_bytes, ptx = _artifact(native_sha)
            forged_ptx = (
                ptx + b".visible .entry __raygen__unreviewed_extra() {}\n")
            artifact["ptx_base64"] = base64.b64encode(forged_ptx).decode()
            artifact["ptx_sha256"] = particle._sha_bytes(forged_ptx)
            artifact["build_identity"]["ptx_sha256"] = artifact["ptx_sha256"]
            artifact["build_identity"]["ptx_bytes"] = len(forged_ptx)
            path, artifact_sha = _write_artifact(directory, artifact)
            deployment = particle.install_particle_rtdlexe_deployment(
                deployment_id="externally-frozen-extra-entry-negative-kat",
                expected_artifact_sha256=artifact_sha,
                expected_native_sha256=native_sha,
                expected_protocol_decision_sha256=(
                    artifact["standard_protocol"]["decision"]["decision_sha256"]),
                expected_template_semantic_sha256=(
                    artifact["template_semantic_sha256"]),
            )
            with self.assertRaises(particle.ParticleRTDLExecutableError) as rejected:
                particle.load_particle_rtdlexe(
                    path, deployment=deployment,
                    native_library_path=directory / "native.so")
            self.assertEqual(rejected.exception.code, "PX011_PTX_ENTRY_SET_INVALID")

    def test_build_compiles_same_absolute_source_twice_and_requires_identity(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            root = Path(raw_directory).resolve()
            nvcc = root / "nvcc"
            nvcc.write_bytes(b"exact nvcc tool")
            include = root / "optix"
            include.mkdir()
            (include / "optix_device.h").write_bytes(b"exact optix header")
            calls = []

            def run(arguments, **kwargs):
                calls.append(tuple(arguments))
                if arguments[-1] == "--version":
                    return subprocess.CompletedProcess(arguments, 0, b"nvcc 12", b"")
                output = Path(kwargs["cwd"]) / arguments[arguments.index("-o") + 1]
                output.write_bytes(
                    b".version 7.0\n.target sm_61\n.address_size 64\n"
                    b".visible .entry __raygen__rtdl_particle_strict_interior() {}\n"
                    b".visible .entry __closesthit__rtdl_particle_strict_interior() {}\n"
                    b".visible .entry __miss__rtdl_particle_strict_interior() {}\n")
                return subprocess.CompletedProcess(arguments, 0, b"", b"")

            with mock.patch.object(particle.subprocess, "run", side_effect=run):
                ptx, identity, source, pass1, pass2 = particle._compile_twice(
                    source=b"source", source_sha256=particle._sha_bytes(b"source"),
                    nvcc_path=nvcc, optix_include=include,
                    compute_arch="compute_61", build_directory=root / "build")
            self.assertEqual(
                particle._PTX_ENTRY_PATTERN.findall(ptx), [
                    b"__raygen__rtdl_particle_strict_interior",
                    b"__closesthit__rtdl_particle_strict_interior",
                    b"__miss__rtdl_particle_strict_interior",
                ])
            self.assertEqual(len(calls), 3)
            self.assertEqual(identity["independent_invocation_count"], 2)
            self.assertTrue(identity["ptx_byte_identical"])
            self.assertNotIn("nvcc_absolute_path", identity)
            self.assertNotIn("source_absolute_path", identity)
            self.assertNotIn(str(root), json.dumps(identity, sort_keys=True))
            for path in (source, pass1, pass2):
                self.assertTrue(path.is_absolute())
                self.assertTrue(path.is_file())

    def test_cache_hit_imports_no_compiler_numba_or_nvrtc_modules(self):
        root = Path(__file__).resolve().parents[1]
        code = textwrap.dedent("""
            import sys
            before = set(sys.modules)
            import rtdsl.v4_particle_rtdlexe
            loaded = set(sys.modules) - before
            forbidden = sorted(name for name in loaded if
                name.startswith("rtdsl.") and (
                    "compiler" in name or "numba" in name.lower()
                    or "nvrtc" in name.lower()))
            if forbidden:
                raise SystemExit(repr(forbidden))
        """)
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(root / "src")
        completed = subprocess.run(
            [sys.executable, "-c", code], cwd=root, env=environment,
            text=True, capture_output=True, check=False)
        self.assertEqual(
            completed.returncode, 0, completed.stdout + completed.stderr)

    def test_formal_execute_source_has_no_row_materialization_or_output_copy(self):
        source = Path(particle.__file__).read_text(encoding="utf-8")
        start = source.index("class PreparedParticleRTDLExecutable")
        end = source.index("def _validate_receipt", start)
        execute = source[start:end]
        self.assertNotIn(".tolist(", execute)
        self.assertNotIn("for row", execute)
        self.assertNotIn("np.empty", execute)
        self.assertNotIn("np.asarray", execute)
        self.assertIn("np.ctypeslib.as_array", execute)
        self.assertIn("output_soa.T", execute)
        self.assertIn("def execute_complete(", execute)
        self.assertIn("np.array_equal(result.output_u32x3, expected)", execute)
        self.assertIn("def execute_exact_core(", execute)
        self.assertIn(
            "np.array_equal(completion._output_u32x3, expected)", execute)
        exact_start = execute.index("    def execute_exact_core(")
        materialize_start = execute.index(
            "    def materialize_exact_core_completion(", exact_start)
        exact_core = execute[exact_start:materialize_start]
        self.assertNotIn("_validate_receipt(", exact_core)
        self.assertNotIn("ParticleExecutionResult(", exact_core)
        self.assertNotIn("artifact_sha256", exact_core)
        self.assertNotIn("ptx_sha256", exact_core)


if __name__ == "__main__":
    unittest.main()
