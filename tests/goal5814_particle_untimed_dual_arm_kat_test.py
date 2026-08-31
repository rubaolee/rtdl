from __future__ import annotations

import ast
import base64
from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
import tempfile
from types import MappingProxyType
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

from experiments.goal5814_particle import untimed_dual_arm_kat as kat
from experiments.goal5814_particle.public_pyoptix_owner import (
    CLOSEST_HIT_ENTRY,
    MISS_ENTRY,
    RAYGEN_ENTRY,
    ParticleProblemShape,
)


def _ptx() -> bytes:
    return (
        b".version 8.0\n"
        + b".visible .entry " + RAYGEN_ENTRY.encode() + b"() {}\n"
        + b".visible .entry " + CLOSEST_HIT_ENTRY.encode() + b"() {}\n"
        + b".visible .entry " + MISS_ENTRY.encode() + b"() {}\n")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _identity(path: Path, relative_to: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(relative_to).as_posix(),
        "bytes": len(data),
        "sha256": _sha256(data),
    }


def _write_canonical_manifest(
        path: Path, value: object) -> kat.ExpectedAssetAuthority:
    encoded = (json.dumps(
        value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode()
    path.write_bytes(encoded)
    return kat.ExpectedAssetAuthority(len(encoded), _sha256(encoded))


def _clone_json(value):
    return json.loads(json.dumps(value))


def _reseal_executable_manifest(path: Path, value: dict):
    body = dict(value)
    body.pop("manifest_body_sha256", None)
    document = {
        **body,
        "manifest_body_sha256": _sha256(kat._compact_json_bytes(body)),
    }
    return document, _write_canonical_manifest(path, document)


def _native_receipt(shape: ParticleProblemShape, *, success: bool):
    return MappingProxyType({
        "schema_version": 1,
        "optix_launch_count": 1,
        "query_count": shape.query_count,
        "query_h2d_copy_call_count": 7,
        "control_reset_h2d_copy_call_count": 1,
        "parameter_h2d_copy_call_count": 1,
        "control_d2h_copy_call_count": 1,
        "output_d2h_copy_call_count": 1 if success else 0,
        "host_blocking_boundary_count": 2 if success else 1,
        "status_before_output": 1,
        "query_h2d_bytes": shape.query_count * 7 * 4,
        "control_reset_h2d_bytes": 16,
        "parameter_h2d_bytes": 120,
        "control_d2h_bytes": 16,
        "output_d2h_bytes": shape.query_count * 3 * 4 if success else 0,
        "output_d2h_after_status_failure": 0,
        "boundary_owner_table_bytes": 0,
    })


class _DurableFixture:
    def __init__(self, root: Path) -> None:
        self.shape = ParticleProblemShape(4, 2, 3)
        self.directory = root / "goal5814_particle_scientific_input"
        self.directory.mkdir()
        self.vertices = np.array([
            [-2.0, -1.0, -3.0],
            [4.0, -1.0, -3.0],
            [-2.0, 5.0, -3.0],
            [-2.0, -1.0, 6.0],
        ], dtype=np.float32)
        self.triangles = np.array(
            [[0, 1, 2], [0, 1, 3]], dtype=np.uint32)
        self.front = np.array([10, 11], dtype=np.uint32)
        self.back = np.array([20, 21], dtype=np.uint32)
        self.queries = np.array([
            [0.1, 0.1, -1.0, 0.0, 0.0, 1.0, 3.0],
            [0.2, 0.2, -1.0, 0.0, 0.0, 1.0, 3.0],
            [0.3, 0.1, -1.0, 0.0, 0.0, 1.0, 3.0],
        ], dtype=np.float32)
        self.expected = np.array([
            [10, 20, 0], [11, 21, 1], [10, 20, 0],
        ], dtype=np.uint32)
        for name, value in (
                ("vertices_f32.npy", self.vertices),
                ("triangles_u32.npy", self.triangles),
                ("front_values_u32.npy", self.front),
                ("back_values_u32.npy", self.back),
                ("queries_f32.npy", self.queries),
                ("expected_u32.npy", self.expected)):
            np.save(self.directory / name, value, allow_pickle=False)
        np.save(
            self.directory / "query_cells_u32.npy",
            np.arange(self.shape.query_count, dtype=np.uint32),
            allow_pickle=False)
        (self.directory / "GOAL5776_MANIFEST.json").write_bytes(b"{}\n")
        (self.directory / "solution_4.vtu").write_bytes(b"mock-vtu-mesh\n")
        numpy_metadata = {
            "back_values_u32.npy": ("uint32", [self.shape.triangle_count]),
            "expected_u32.npy": ("uint32", [self.shape.query_count, 3]),
            "front_values_u32.npy": ("uint32", [self.shape.triangle_count]),
            "queries_f32.npy": ("float32", [self.shape.query_count, 7]),
            "query_cells_u32.npy": ("uint32", [self.shape.query_count]),
            "triangles_u32.npy": ("uint32", [self.shape.triangle_count, 3]),
            "vertices_f32.npy": ("float32", [self.shape.vertex_count, 3]),
        }
        payloads = []
        for name in sorted([
                "GOAL5776_MANIFEST.json", "solution_4.vtu",
                *numpy_metadata]):
            member = self.directory / name
            data = member.read_bytes()
            payload = {
                "bytes": len(data), "name": name,
                "sha256": _sha256(data),
                "role": (
                    "BYTE_IDENTICAL_CONTROLLING_GOAL5776_V2_MANIFEST"
                    if name == "GOAL5776_MANIFEST.json" else
                    "PINNED_PUBLIC_RTXADVECT_SOURCE_MESH"
                    if name == "solution_4.vtu" else
                    "FROZEN_GOAL5776_V2_NUMPY_PAYLOAD"),
            }
            if name in numpy_metadata:
                payload["dtype"], payload["shape"] = numpy_metadata[name]
            payloads.append(payload)
        solution = next(
            payload for payload in payloads
            if payload["name"] == "solution_4.vtu")
        upstream = next(
            payload for payload in payloads
            if payload["name"] == "GOAL5776_MANIFEST.json")
        scientific_manifest = {
            "claim_boundary": {
                "executable_bytes_frozen": False,
                "oracle_rederivation_completed": False,
                "performance_worker_authorized": False,
                "scientific_input_custody_only": True,
            },
            "controlling_policy": {
                "bytes": 1,
                "path": "history/internal_docs/mock_preaction.json",
                "sha256": "0" * 64,
            },
            "date": "2026-08-28",
            "payload_bytes": sum(payload["bytes"] for payload in payloads),
            "payload_count": 9,
            "payloads": payloads,
            "schema": kat.SCIENTIFIC_MANIFEST_SCHEMA,
            "source_authority": {
                "bytes": solution["bytes"],
                "commit": "5cfe63fed227c238905a8f24082b59b5d3160966",
                "project": "RTxAdvect",
                "repository_path": "dataset/microfludics/solution_4.vtu",
                "sha256": solution["sha256"],
            },
            "status": "DURABLE_BYTE_IDENTICAL_SUCCESSOR__NO_TMP_RUNTIME_DEPENDENCY",
            "superseded_goal5776_v1_accepted": False,
            "temporary_source_root_required_after_materialization": False,
            "upstream_goal5776_v2_manifest": {
                "bytes": upstream["bytes"],
                "copied_name": "GOAL5776_MANIFEST.json",
                "sha256": upstream["sha256"],
            },
        }
        self.scientific_document = scientific_manifest
        self.scientific_manifest = self.directory / kat.SCIENTIFIC_MANIFEST_NAME
        self.scientific_identity = _write_canonical_manifest(
            self.scientific_manifest, scientific_manifest)

        self.source = root / "particle.cu"
        self.source.write_bytes(b"mock exact source\n")
        source_sha = _sha256(self.source.read_bytes())
        self.source.rename(
            root / f"{source_sha}.particle_strict_interior.cu")
        self.source = root / f"{source_sha}.particle_strict_interior.cu"
        semantic_sha = "4" * 64
        self.descriptor = root / "particle_descriptor.json"
        self.descriptor.write_bytes((json.dumps({
            "semantic_sha256": semantic_sha,
            "source_bytes": self.source.stat().st_size,
            "source_sha256": source_sha,
        }, sort_keys=True, separators=(",", ":")) + "\n").encode())
        descriptor_sha = _sha256(self.descriptor.read_bytes())
        self.descriptor.rename(
            root / f"{descriptor_sha}.particle_descriptor.json")
        self.descriptor = root / f"{descriptor_sha}.particle_descriptor.json"
        self.ptx = root / f"{source_sha}.compute_61.pass1.ptx"
        self.ptx.write_bytes(_ptx())
        self.ptx_pass2 = root / f"{source_sha}.compute_61.pass2.ptx"
        self.ptx_pass2.write_bytes(_ptx())
        self.dso = root / "librtdl_optix.so"
        self.dso.write_bytes(b"\x7fELF" + b"mock-dso")
        decision_body = {
            "contract_sha256": "a" * 64,
            "executable_capability_issued": False,
            "findings": [],
            "projection_sha256": "b" * 64,
            "schema": "rtdl.v4.callback_protocol_contract_decision.v1",
            "verdict": "ACCEPT",
        }
        decision = {
            **decision_body,
            "decision_sha256": _sha256(kat._compact_json_bytes(decision_body)),
        }
        specialization_sha = "e" * 64
        self.rtdlexe = root / "particle.rtdlexe"
        artifact = {
            "build_identity": {},
            "descriptor_base64": base64.b64encode(
                self.descriptor.read_bytes()).decode("ascii"),
            "descriptor_sha256": _sha256(self.descriptor.read_bytes()),
            "format_version": 1,
            "native_library_sha256": _sha256(self.dso.read_bytes()),
            "ptx_base64": base64.b64encode(_ptx()).decode("ascii"),
            "ptx_sha256": _sha256(_ptx()),
            "schema": kat.PARTICLE_RTDEXE_SCHEMA,
            "source_base64": base64.b64encode(
                self.source.read_bytes()).decode("ascii"),
            "source_sha256": _sha256(self.source.read_bytes()),
            "specialization_binding": {
                "binding_sha256": specialization_sha},
            "standard_protocol": {"decision": decision},
            "template_semantic_sha256": semantic_sha,
        }
        self.rtdlexe.write_bytes((json.dumps(
            artifact, sort_keys=True, separators=(",", ":")) + "\n").encode())
        artifact_sha = _sha256(self.rtdlexe.read_bytes())
        self.rtdlexe.rename(root / f"{artifact_sha}.rtdlexe")
        self.rtdlexe = root / f"{artifact_sha}.rtdlexe"
        executable_body = {
            "build_argv": ["build_particle_rtdlexe.py", "--mock"],
            "build_host": "lx1",
            "build_only_no_registered_timing": True,
            "controlling_policy": {
                "absolute_path": "/frozen/mock/preaction.json",
                "loader_oracle_binding_sha256":
                    kat.FORMAL_LOADER_ORACLE_BINDING_SHA256,
                "sha256": kat.FORMAL_CONTROLLING_POLICY_SHA256,
            },
            "identities": {
                "artifact_absolute_path": str(self.rtdlexe),
                "artifact_bytes": self.rtdlexe.stat().st_size,
                "artifact_sha256": artifact_sha,
                "builder_source_absolute_path": "/frozen/build_particle_rtdlexe.py",
                "builder_source_sha256": "9" * 64,
                "descriptor_absolute_path": str(self.descriptor),
                "descriptor_sha256": descriptor_sha,
                "native_absolute_path": str(self.dso),
                "native_sha256": _sha256(self.dso.read_bytes()),
                "ptx_bytes": self.ptx.stat().st_size,
                "ptx_pass1_absolute_path": str(self.ptx),
                "ptx_pass2_absolute_path": str(self.ptx_pass2),
                "ptx_passes_byte_identical": True,
                "ptx_sha256": _sha256(_ptx()),
                "specialization_binding_sha256": specialization_sha,
                "template_semantic_sha256": semantic_sha,
                "template_source_absolute_path": str(self.source),
                "template_source_sha256": source_sha,
            },
            "runtime_boundary": {
                "build_self_consistency_public_load_roundtrip_passed": True,
                "compiler_numba_or_nvrtc_imported_on_cache_hit": False,
                "external_manifest_authority_kat_passed": False,
                "formal_worker_zero_authorized": False,
                "installer_authenticates_provenance_by_itself": False,
                "performance_claimed": False,
                "real_prepare_or_execute_attempted": False,
                "runtime_product_abi_symbol_count": 6,
                "runtime_product_abi_symbols": [
                    "rtdl_optix_v4_particle_strict_interior_source_v1",
                    "rtdl_optix_v4_particle_strict_interior_descriptor_v1",
                    "rtdl_optix_v4_prepare_particle_strict_interior_v1",
                    "rtdl_optix_v4_execute_prepared_particle_strict_interior_v2",
                    "rtdl_optix_v4_execute_prepared_particle_strict_interior_"
                    "prevalidated_v3",
                    "rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1",
                ],
            },
            "schema": kat.EXECUTABLE_MANIFEST_SCHEMA,
            "specialization_scope": {
                "arbitrary_user_dsl_generalization_claimed": False,
                "complete_particle_advection_claimed": False,
                "name": "STRICT_INTERIOR_STANDARD_LIBRARY_SPECIALIZATION_ONLY",
            },
            "standard_protocol": {
                "decision_sha256": decision["decision_sha256"],
                "findings": [],
                "independent_oracle_binding_sha256":
                    kat.FORMAL_LOADER_ORACLE_BINDING_SHA256,
                "independent_oracle_verifier_source_sha256":
                    kat.FORMAL_PROTOCOL_VERIFIER_SOURCE_SHA256,
                "producer": "compile_standard_builtin_triangle_program",
                "source_semantics_sha256":
                    kat.FORMAL_SOURCE_SEMANTICS_SHA256,
                "verdict": "ACCEPT",
            },
            "status": "PASS__EXACT_PUBLIC_ARTIFACT_BUILT_AND_LOAD_VERIFIED__NO_EXECUTE",
            "tool_identity": {
                "compute_arch": "compute_61",
                "numba_version": "mock",
                "numpy_version": np.__version__,
                "nvcc_absolute_path": "/usr/bin/nvcc",
                "nvcc_executable_sha256": "3" * 64,
                "optix_device_header_sha256": "2" * 64,
                "optix_include_absolute_path": "/opt/optix/include",
                "python_executable": "/usr/bin/python3",
                "python_version": "3.mock",
            },
        }
        executable_manifest = {
            **executable_body,
            "manifest_body_sha256": _sha256(
                kat._compact_json_bytes(executable_body)),
        }
        self.executable_document = executable_manifest
        self.executable_manifest = root / "EXECUTABLE_MANIFEST.json"
        self.executable_identity = _write_canonical_manifest(
            self.executable_manifest, executable_manifest)
        self.paths = kat.KatAssetPaths(
            self.directory, self.ptx, self.dso, self.rtdlexe,
            self.executable_manifest, self.executable_identity,
            self.scientific_identity)

    def load(self) -> kat.LoadedParticleKat:
        return kat.load_durable_particle_kat(
            self.paths, shape=self.shape)


def _ledger(shape: ParticleProblemShape, *, success: bool):
    return kat.KatExecutionLedger(
        h2d_copy_call_count=9,
        h2d_bytes=shape.query_count * 7 * 4 + 16 + 120,
        query_h2d_copy_call_count=7,
        query_h2d_bytes=shape.query_count * 7 * 4,
        control_reset_h2d_copy_call_count=1,
        control_reset_h2d_bytes=16,
        parameter_h2d_copy_call_count=1,
        parameter_h2d_bytes=120,
        optix_launch_call_count=1,
        raygen_invocation_count=shape.query_count,
        control_d2h_copy_call_count=1,
        control_d2h_bytes=16,
        output_d2h_copy_call_count=1 if success else 0,
        output_d2h_bytes=shape.query_count * 3 * 4 if success else 0,
        status_before_output=True,
        output_d2h_after_status_failure=0,
        blocking_boundary_count=2 if success else 1,
    )


class _FakeArm:
    def __init__(
            self, label: str, bundle: kat.LoadedParticleKat,
            events: list[str], *, failure_output_bytes: int = 0,
            fail_first_execution: bool = False,
            c_contiguous_success_output: bool = False,
            ledger_overrides: dict[str, object] | None = None,
            failure_ledger_overrides: dict[str, object] | None = None) -> None:
        self.label = label
        self.bundle = bundle
        self.deployment_capability = bundle.deployment_capability
        self.events = events
        self.failure_output_bytes = failure_output_bytes
        self.fail_first_execution = fail_first_execution
        self.c_contiguous_success_output = c_contiguous_success_output
        self.ledger_overrides = ledger_overrides or {}
        self.failure_ledger_overrides = failure_ledger_overrides or {}
        self.execute_calls = 0
        self.admission_calls = 0
        self.exact_core_calls = 0
        self.materialize_calls = 0
        self.close_calls = 0

    def _success(self, expected):
        if self.c_contiguous_success_output:
            output = expected.copy(order="C")
        else:
            packed_soa = np.empty(
                (3, self.bundle.shape.query_count), dtype=np.uint32,
                order="C")
            packed_soa[...] = expected.T
            output = packed_soa.T
        output.setflags(write=False)
        ledger = replace(
            _ledger(self.bundle.shape, success=True),
            **self.ledger_overrides)
        return kat.KatArmSuccess(
            arm=self.label,
            output=output,
            control=(self.bundle.shape.query_count, 0xFFFFFFFF, 0, 0),
            ledger=ledger,
        )

    def execute_complete(self, columns, expected):
        self.execute_calls += 1
        if self.fail_first_execution and self.execute_calls == 1:
            self.events.append(f"{self.label}_UNEXPECTED_FAILURE")
            raise kat.KatContractError("injected terminal failure")
        if columns is self.bundle.success_queries:
            self.events.append(f"{self.label}_SUCCESS")
            self.assert_common(columns, expected)
            return self._success(expected)
        if columns is self.bundle.miss_queries:
            self.events.append(f"{self.label}_MISS")
            self.assert_common(columns, expected)
            ledger = _ledger(self.bundle.shape, success=False)
            ledger = replace(
                ledger, **self.ledger_overrides,
                **self.failure_ledger_overrides)
            if self.failure_output_bytes:
                ledger = kat.KatExecutionLedger(
                    **{
                        **ledger.__dict__,
                        "output_d2h_copy_call_count": 1,
                        "output_d2h_bytes": self.failure_output_bytes,
                    })
            raise kat.KatDeviceStatusFailure(
                self.label,
                (self.bundle.shape.query_count - 1, 0, 1, 1),
                ledger,
            )
        raise AssertionError("runner supplied non-common query columns")

    def admit_exact_core_input(self, columns, expected):
        self.admission_calls += 1
        self.events.append(f"{self.label}_ADMIT")
        self.assert_common(columns, expected)
        return SimpleNamespace(
            arm=self.label, columns=columns.native_order(), expected=expected)

    def execute_exact_core(self, admitted):
        self.exact_core_calls += 1
        self.events.append(f"{self.label}_EXACT_CORE")
        if admitted.arm != self.label:
            raise AssertionError("exact core received foreign arm admission")
        common = self.bundle.success_queries.native_order()
        if len(admitted.columns) != len(common) or any(
                observed is not expected
                for observed, expected in zip(admitted.columns, common)):
            raise AssertionError("exact core did not receive common SoA columns")
        if admitted.expected is not self.bundle.expected_output:
            raise AssertionError("exact core did not receive common oracle")
        return SimpleNamespace(arm=self.label, expected=admitted.expected)

    def materialize_exact_core(self, completion):
        self.materialize_calls += 1
        self.events.append(f"{self.label}_MATERIALIZE")
        if completion.arm != self.label:
            raise AssertionError("foreign exact-core completion")
        return self._success(completion.expected)

    def assert_common(self, columns, expected):
        if not isinstance(columns, kat.KatSoAColumns):
            raise AssertionError("arm did not receive common SoA columns")
        if expected is not self.bundle.expected_output:
            raise AssertionError("arm did not receive common expected output")

    def close(self):
        self.close_calls += 1
        self.events.append(f"{self.label}_CLOSE")


class Goal5814ParticleUntimedDualArmKatTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.fixture = _DurableFixture(Path(self.temporary.name))

    def test_common_stage_builds_exact_soa_and_one_row_bbox_miss(self):
        bundle = self.fixture.load()
        self.assertEqual(bundle.prebuilt_ptx, _ptx())
        self.assertEqual(
            _sha256(bundle.rtdlexe_bytes),
            bundle.deployment_capability.artifact.sha256)
        self.assertEqual(bundle.paths.native_dso.read_bytes()[:4], b"\x7fELF")
        success = bundle.success_queries.native_order()
        failure = bundle.miss_queries.native_order()
        for index, column in enumerate(success):
            self.assertEqual(column.dtype, np.dtype(np.float32))
            self.assertEqual(column.shape, (3,))
            self.assertTrue(column.flags.c_contiguous)
            self.assertFalse(column.flags.writeable)
            self.assertTrue(np.array_equal(column, self.fixture.queries[:, index]))
        for good, bad in zip(success, failure):
            self.assertTrue(np.array_equal(good[1:], bad[1:]))
            self.assertTrue(bad.flags.c_contiguous)
            self.assertFalse(bad.flags.writeable)
        maximum = self.fixture.vertices.max(axis=0)
        self.assertTrue(np.all(np.array(failure[:3])[:, 0] > maximum))
        self.assertTrue(np.all(np.array(failure[3:6])[:, 0] > 0.0))
        self.assertEqual(failure[6][0], np.float32(1.0))

    def test_single_transaction_order_exact_success_and_zero_output_failure(self):
        bundle = self.fixture.load()
        events: list[str] = []
        owners = {}

        def factory(label):
            def prepare(received):
                self.assertIs(received, bundle)
                events.append(f"{label}_PREPARE")
                owner = _FakeArm(label, bundle, events)
                owners[label] = owner
                return owner
            return prepare

        result = kat.run_untimed_dual_arm_kat(
            bundle,
            b_factory=factory(kat.ARM_B),
            d_factory=factory(kat.ARM_D),
        )
        self.assertEqual(result.execution_order, (
            "B_SUCCESS", "D_SUCCESS", "B_MISS", "D_MISS"))
        self.assertFalse(result.timed)
        self.assertEqual(result.retry_count, 0)
        self.assertEqual(result.replacement_count, 0)
        self.assertTrue(result.b_success.exact)
        self.assertTrue(result.d_success.exact)
        self.assertTrue(result.b_success.output_read_only)
        self.assertTrue(result.d_success.output_read_only)
        self.assertTrue(result.b_miss.device_status_failure)
        self.assertTrue(result.d_miss.device_status_failure)
        self.assertEqual(result.b_miss.ledger.output_d2h_bytes, 0)
        self.assertEqual(result.d_miss.ledger.output_d2h_bytes, 0)
        self.assertEqual(owners[kat.ARM_B].execute_calls, 2)
        self.assertEqual(owners[kat.ARM_D].execute_calls, 2)
        self.assertEqual(owners[kat.ARM_B].close_calls, 1)
        self.assertEqual(owners[kat.ARM_D].close_calls, 1)
        self.assertEqual(events, [
            f"{kat.ARM_B}_PREPARE", f"{kat.ARM_D}_PREPARE",
            f"{kat.ARM_B}_SUCCESS", f"{kat.ARM_D}_SUCCESS",
            f"{kat.ARM_B}_MISS", f"{kat.ARM_D}_MISS",
            f"{kat.ARM_D}_CLOSE", f"{kat.ARM_B}_CLOSE",
        ])

    def test_exact_core_boundary_transaction_is_symmetric_and_untimed(self):
        bundle = self.fixture.load()
        events: list[str] = []
        owners = {}

        def factory(label):
            def prepare(received):
                self.assertIs(received, bundle)
                events.append(f"{label}_PREPARE")
                owner = _FakeArm(label, bundle, events)
                owners[label] = owner
                return owner
            return prepare

        def boundary(label, completion):
            self.assertEqual(completion.arm, label)
            self.assertEqual(events[-1], f"{label}_EXACT_CORE")
            events.append(f"{label}_CALLER_BOUNDARY")

        result = kat.run_untimed_dual_arm_exact_core_boundary_kat(
            bundle,
            b_factory=factory(kat.ARM_B),
            d_factory=factory(kat.ARM_D),
            caller_boundary=boundary,
        )
        self.assertFalse(result.timed)
        self.assertEqual(result.retry_count, 0)
        self.assertEqual(result.replacement_count, 0)
        self.assertTrue(result.b_success.exact)
        self.assertTrue(result.d_success.exact)
        self.assertEqual(result.b_success.ledger, _ledger(bundle.shape, success=True))
        self.assertEqual(result.d_success.ledger, _ledger(bundle.shape, success=True))
        self.assertEqual(owners[kat.ARM_B].admission_calls, 1)
        self.assertEqual(owners[kat.ARM_D].admission_calls, 1)
        self.assertEqual(owners[kat.ARM_B].exact_core_calls, 1)
        self.assertEqual(owners[kat.ARM_D].exact_core_calls, 1)
        self.assertEqual(owners[kat.ARM_B].materialize_calls, 1)
        self.assertEqual(owners[kat.ARM_D].materialize_calls, 1)
        self.assertEqual(owners[kat.ARM_B].execute_calls, 1)
        self.assertEqual(owners[kat.ARM_D].execute_calls, 1)
        self.assertEqual(events, [
            f"{kat.ARM_B}_PREPARE", f"{kat.ARM_D}_PREPARE",
            f"{kat.ARM_B}_ADMIT", f"{kat.ARM_D}_ADMIT",
            f"{kat.ARM_B}_EXACT_CORE", f"{kat.ARM_B}_CALLER_BOUNDARY",
            f"{kat.ARM_B}_MATERIALIZE",
            f"{kat.ARM_D}_EXACT_CORE", f"{kat.ARM_D}_CALLER_BOUNDARY",
            f"{kat.ARM_D}_MATERIALIZE",
            f"{kat.ARM_B}_MISS", f"{kat.ARM_D}_MISS",
            f"{kat.ARM_D}_CLOSE", f"{kat.ARM_B}_CLOSE",
        ])

    def test_c_contiguous_output_is_rejected_as_hidden_host_pack(self):
        bundle = self.fixture.load()
        events: list[str] = []
        owners = {}

        def b_factory(received):
            owners["b"] = _FakeArm(
                kat.ARM_B, received, events,
                c_contiguous_success_output=True)
            return owners["b"]

        def d_factory(received):
            owners["d"] = _FakeArm(kat.ARM_D, received, events)
            return owners["d"]

        with self.assertRaisesRegex(
                kat.KatContractError, "borrowed packed-SoA view"):
            kat.run_untimed_dual_arm_kat(
                bundle, b_factory=b_factory, d_factory=d_factory)
        self.assertEqual(owners["b"].execute_calls, 1)
        self.assertEqual(owners["d"].execute_calls, 0)
        self.assertEqual(owners["b"].close_calls, 1)
        self.assertEqual(owners["d"].close_calls, 1)

    def test_failure_output_d2h_is_terminal_contract_error(self):
        bundle = self.fixture.load()
        events: list[str] = []
        owners = {}

        def b_factory(received):
            owners["b"] = _FakeArm(kat.ARM_B, received, events,
                                   failure_output_bytes=12)
            return owners["b"]

        def d_factory(received):
            owners["d"] = _FakeArm(kat.ARM_D, received, events)
            return owners["d"]

        with self.assertRaisesRegex(kat.KatContractError, "ledger differs"):
            kat.run_untimed_dual_arm_kat(
                bundle, b_factory=b_factory, d_factory=d_factory)
        self.assertEqual(owners["b"].execute_calls, 2)
        self.assertEqual(owners["d"].execute_calls, 1)
        self.assertEqual(owners["b"].close_calls, 1)
        self.assertEqual(owners["d"].close_calls, 1)

    def test_unexpected_first_failure_is_not_retried_or_replaced(self):
        bundle = self.fixture.load()
        events: list[str] = []
        owners = {}

        def b_factory(received):
            owners["b"] = _FakeArm(
                kat.ARM_B, received, events, fail_first_execution=True)
            return owners["b"]

        def d_factory(received):
            owners["d"] = _FakeArm(kat.ARM_D, received, events)
            return owners["d"]

        with self.assertRaisesRegex(kat.KatContractError, "terminal failure"):
            kat.run_untimed_dual_arm_kat(
                bundle, b_factory=b_factory, d_factory=d_factory)
        self.assertEqual(owners["b"].execute_calls, 1)
        self.assertEqual(owners["d"].execute_calls, 0)
        self.assertEqual(owners["b"].close_calls, 1)
        self.assertEqual(owners["d"].close_calls, 1)

    def test_d_factory_is_fixed_direct_public_lifecycle_boundary(self):
        bundle = self.fixture.load()
        events = []

        class Prepared:
            def close(self):
                events.append("prepared.close")

        prepared = Prepared()

        class Loaded:
            artifact_sha256 = bundle.deployment_capability.artifact.sha256
            ptx_sha256 = bundle.deployment_capability.ptx.sha256
            ptx_bytes = bundle.prebuilt_ptx

            def prepare(self, static):
                events.append(("loaded.prepare", static))
                return prepared

            def close(self):
                events.append("loaded.close")

        installed = object()
        module = SimpleNamespace(
            install_particle_rtdlexe_deployment=mock.Mock(
                return_value=installed),
            load_particle_rtdlexe=mock.Mock(return_value=Loaded()),
            ParticleStaticInput=lambda **values: values,
            ParticleDeviceStatusError=RuntimeError,
        )
        with mock.patch.object(
                kat.importlib, "import_module", return_value=module) as imported, \
                mock.patch.object(kat, "FORMAL_PARTICLE_SHAPE", bundle.shape):
            arm = kat.prepare_public_verified_rtdlexe_kat_arm(bundle)
        imported.assert_called_once_with("rtdsl.v4_particle_rtdlexe")
        module.install_particle_rtdlexe_deployment.assert_called_once_with(
            deployment_id=(
                "goal5814/formal-dual-arm-kat/"
                f"{bundle.executable_manifest.sha256}"),
            expected_artifact_sha256=
                bundle.deployment_capability.artifact.sha256,
            expected_native_sha256=bundle.deployment_capability.native.sha256,
            expected_protocol_decision_sha256=
                bundle.deployment_capability.protocol_decision.sha256,
            expected_template_semantic_sha256=
                bundle.deployment_capability.template_semantic.sha256,
        )
        module.load_particle_rtdlexe.assert_called_once_with(
            bundle.paths.rtdlexe, deployment=installed,
            native_library_path=bundle.paths.native_dso)
        self.assertIs(arm.deployment_capability, bundle.deployment_capability)
        arm.close()
        self.assertEqual(events[-2:], ["prepared.close", "loaded.close"])

    def test_frozen_manifest_constants_and_real_executable_custody(self):
        repository = Path(kat.__file__).resolve().parents[2]
        scientific = repository / (
            "history/internal_docs/"
            "goal5814_particle_tracking_scientific_input_v1_20260828/"
            "SCIENTIFIC_INPUT_MANIFEST.json")
        executable_root = repository / (
            "history/internal_docs/goal5814_particle_executable_v2_20260828")
        executable = executable_root / "executable_manifest.json"
        self.assertEqual(scientific.stat().st_size, 3650)
        self.assertEqual(
            _sha256(scientific.read_bytes()),
            kat.FORMAL_SCIENTIFIC_MANIFEST_SHA256)
        self.assertEqual(executable.stat().st_size, 5924)
        self.assertEqual(
            _sha256(executable.read_bytes()),
            kat.FORMAL_EXECUTABLE_MANIFEST_SHA256)
        ptx = next(executable_root.glob("*.pass1.ptx"))
        artifact = next(executable_root.glob("*.rtdlexe"))
        native = executable_root / "librtdl_optix.so"
        paths = kat.KatAssetPaths(
            scientific.parent, ptx, native, artifact, executable,
            kat.ExpectedAssetAuthority(
                kat.FORMAL_EXECUTABLE_MANIFEST_BYTES,
                kat.FORMAL_EXECUTABLE_MANIFEST_SHA256))
        manifest_identity, capability = kat._verify_executable_manifest(
            paths, executable, ptx, native, artifact)
        self.assertEqual(
            manifest_identity, kat.ExpectedAssetAuthority(
                5924, kat.FORMAL_EXECUTABLE_MANIFEST_SHA256))
        self.assertEqual(
            capability.artifact.sha256,
            "ab60364a4e0006bf1ab770de672868ef6bbf46a40b9cbd6adf89fd7b03cbfdec")
        self.assertEqual(
            capability.native.sha256,
            "eceb403202209137db9ac9ff3b55f7a0009c35d7564a2b6422e9c2ab122bd9a4")
        self.assertEqual(
            capability.ptx.sha256,
            "64bd9fb77910d1c2e89551ecd842a5cd6dcfe18a8ea3f3d79d27e6fdaa578427")

    def test_wrong_request_external_manifest_authorities_fail_first(self):
        bad_scientific = replace(
            self.fixture.paths,
            scientific_manifest_identity=kat.ExpectedAssetAuthority(
                self.fixture.scientific_identity.bytes, "f" * 64))
        with self.assertRaisesRegex(
                kat.KatContractError, "scientific input manifest request-external"):
            kat.load_durable_particle_kat(
                bad_scientific, shape=self.fixture.shape)
        bad_executable = replace(
            self.fixture.paths,
            executable_manifest_identity=kat.ExpectedAssetAuthority(
                self.fixture.executable_identity.bytes, "f" * 64))
        with self.assertRaisesRegex(
                kat.KatContractError, "executable manifest request-external"):
            kat.load_durable_particle_kat(
                bad_executable, shape=self.fixture.shape)

    def test_scientific_same_length_member_tamper_is_rejected(self):
        member = self.fixture.directory / "solution_4.vtu"
        original = member.read_bytes()
        member.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        self.assertEqual(member.stat().st_size, len(original))
        with self.assertRaisesRegex(kat.KatContractError, "member identity differs"):
            self.fixture.load()

    def test_scientific_coherent_reseal_cannot_replace_external_authority(self):
        member = self.fixture.directory / "solution_4.vtu"
        original = member.read_bytes()
        member.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        document = _clone_json(self.fixture.scientific_document)
        new_sha = _sha256(member.read_bytes())
        for payload in document["payloads"]:
            if payload["name"] == "solution_4.vtu":
                payload["sha256"] = new_sha
        document["source_authority"]["sha256"] = new_sha
        resealed = _write_canonical_manifest(
            self.fixture.scientific_manifest, document)
        self.assertEqual(
            resealed.bytes, self.fixture.scientific_identity.bytes)
        self.assertNotEqual(
            resealed.sha256, self.fixture.scientific_identity.sha256)
        with self.assertRaisesRegex(kat.KatContractError, "request-external"):
            self.fixture.load()

    def test_executable_coherent_reseal_cannot_replace_external_authority(self):
        document = _clone_json(self.fixture.executable_document)
        document["build_host"] = "lx2"
        _document, resealed = _reseal_executable_manifest(
            self.fixture.executable_manifest, document)
        self.assertEqual(
            resealed.bytes, self.fixture.executable_identity.bytes)
        self.assertNotEqual(
            resealed.sha256, self.fixture.executable_identity.sha256)
        with self.assertRaisesRegex(kat.KatContractError, "request-external"):
            self.fixture.load()

    def test_standalone_ptx_must_equal_embedded_ptx_even_after_manifest_reseal(self):
        changed = _ptx().replace(b".version 8.0", b".version 8.1")
        self.fixture.ptx.write_bytes(changed)
        self.fixture.ptx_pass2.write_bytes(changed)
        document = _clone_json(self.fixture.executable_document)
        document["identities"]["ptx_sha256"] = _sha256(changed)
        _document, authority = _reseal_executable_manifest(
            self.fixture.executable_manifest, document)
        paths = replace(
            self.fixture.paths, executable_manifest_identity=authority)
        with self.assertRaisesRegex(
                kat.KatContractError, "not byte-identical"):
            kat.load_durable_particle_kat(paths, shape=self.fixture.shape)

    def test_resealed_embedded_nul_tail_and_artifact_extra_key_are_rejected(self):
        artifact = json.loads(self.fixture.rtdlexe.read_text(encoding="utf-8"))
        tailed = _ptx() + b"\0unconsumed-tail"
        artifact["ptx_base64"] = base64.b64encode(tailed).decode("ascii")
        artifact["ptx_sha256"] = _sha256(tailed)
        encoded = kat._compact_json_bytes(artifact) + b"\n"
        with self.assertRaisesRegex(kat.KatContractError, "NUL"):
            kat._verify_artifact_embedded_ptx(encoded, tailed)
        artifact["attacker_extra_key"] = 1
        encoded = kat._compact_json_bytes(artifact) + b"\n"
        with self.assertRaisesRegex(kat.KatContractError, "exact keys differ"):
            kat._verify_artifact_embedded_ptx(encoded, _ptx())

    def test_public_d_maps_complete_immutable_native_receipts(self):
        for success in (True, False):
            with self.subTest(success=success):
                observed = kat._public_d_ledger(
                    _native_receipt(self.fixture.shape, success=success))
                self.assertEqual(
                    observed, _ledger(self.fixture.shape, success=success))
        control = MappingProxyType({
            "validated_row_count": 2, "first_error": 0,
            "error_code": 1, "status": 1})
        self.assertEqual(kat._public_d_failure_control(control), (2, 0, 1, 1))

    def test_every_required_transfer_ledger_field_is_decision_bearing(self):
        bundle = self.fixture.load()
        mutations = {
            "h2d_copy_call_count": 8,
            "h2d_bytes": 1,
            "query_h2d_copy_call_count": 6,
            "query_h2d_bytes": 1,
            "control_reset_h2d_copy_call_count": 0,
            "control_reset_h2d_bytes": 0,
            "parameter_h2d_copy_call_count": 0,
            "parameter_h2d_bytes": 0,
            "optix_launch_call_count": 2,
            "raygen_invocation_count": 2,
            "control_d2h_copy_call_count": 0,
            "control_d2h_bytes": 0,
            "output_d2h_copy_call_count": 0,
            "output_d2h_bytes": 0,
            "status_before_output": False,
            "output_d2h_after_status_failure": 4,
            "blocking_boundary_count": 1,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                events = []
                with self.assertRaisesRegex(
                        kat.KatContractError, "ledger differs"):
                    kat.run_untimed_dual_arm_kat(
                        bundle,
                        b_factory=lambda received, field=field, value=value: (
                            _FakeArm(
                                kat.ARM_B, received, events,
                                ledger_overrides={field: value})),
                        d_factory=lambda received: _FakeArm(
                            kat.ARM_D, received, events),
                    )
        events = []
        with self.assertRaisesRegex(kat.KatContractError, "ledger differs"):
            kat.run_untimed_dual_arm_kat(
                bundle,
                b_factory=lambda received: _FakeArm(
                    kat.ARM_B, received, events,
                    failure_ledger_overrides={
                        "output_d2h_after_status_failure": 4}),
                d_factory=lambda received: _FakeArm(
                    kat.ARM_D, received, events),
            )
        formal = _ledger(kat.FORMAL_PARTICLE_SHAPE, success=True)
        self.assertEqual(formal.h2d_copy_call_count, 9)
        self.assertEqual(formal.h2d_bytes, 140136)
        self.assertEqual(formal.query_h2d_bytes, 140000)

    def test_equal_but_self_minted_capability_is_not_installed_authority(self):
        bundle = self.fixture.load()
        events = []

        def b_factory(received):
            arm = _FakeArm(kat.ARM_B, received, events)
            arm.deployment_capability = replace(received.deployment_capability)
            self.assertEqual(
                arm.deployment_capability, received.deployment_capability)
            self.assertIsNot(
                arm.deployment_capability, received.deployment_capability)
            return arm

        with self.assertRaisesRegex(
                kat.KatContractError, "did not install"):
            kat.run_untimed_dual_arm_kat(
                bundle, b_factory=b_factory,
                d_factory=lambda received: _FakeArm(
                    kat.ARM_D, received, events))

    def test_formal_output_is_reserved_before_prepare_and_committed_after_close(self):
        bundle = self.fixture.load()
        output = Path(self.temporary.name) / "KAT_RESULT.json"
        events = []

        def factory(label):
            def prepare(received):
                events.append(f"{label}_PREPARE")
                return _FakeArm(label, received, events)
            return prepare

        result, identity = kat.run_untimed_dual_arm_kat_to_output(
            bundle, output,
            b_factory=factory(kat.ARM_B),
            d_factory=factory(kat.ARM_D))
        self.assertEqual(events[-2:], [
            f"{kat.ARM_D}_CLOSE", f"{kat.ARM_B}_CLOSE"])
        raw = output.read_bytes()
        self.assertEqual(len(raw), identity.bytes)
        self.assertEqual(_sha256(raw), identity.sha256)
        document = json.loads(raw)
        self.assertEqual(raw, kat._canonical_result_bytes(document))
        self.assertFalse(document["timed"])
        self.assertEqual(document["retry_count"], 0)
        self.assertEqual(document["replacement_count"], 0)
        self.assertEqual(document["execution_order"], [
            "B_SUCCESS", "D_SUCCESS", "B_MISS", "D_MISS"])
        self.assertEqual(set(document["steps"]), {
            "B_SUCCESS", "D_SUCCESS", "B_MISS", "D_MISS"})
        self.assertNotIn(b'"timing"', raw)
        self.assertEqual(
            kat.write_canonical_kat_result(output, bundle, result), identity)
        output.write_bytes(b"{}\n")
        with self.assertRaisesRegex(kat.KatContractError, "non-exact"):
            kat.write_canonical_kat_result(output, bundle, result)

    def test_existing_formal_output_blocks_all_factories_and_failure_writes_no_pass(self):
        bundle = self.fixture.load()
        output = Path(self.temporary.name) / "KAT_RESULT.json"
        output.write_bytes(b"reserved\n")
        factory = mock.Mock()
        with self.assertRaisesRegex(kat.KatContractError, "already exists"):
            kat.run_untimed_dual_arm_kat_to_output(
                bundle, output, b_factory=factory, d_factory=factory)
        factory.assert_not_called()

        output.unlink()
        events = []
        with mock.patch.object(
                kat, "write_canonical_kat_result") as pure_writer:
            with self.assertRaisesRegex(kat.KatContractError, "terminal failure"):
                kat.run_untimed_dual_arm_kat_to_output(
                    bundle, output,
                    b_factory=lambda received: _FakeArm(
                        kat.ARM_B, received, events,
                        fail_first_execution=True),
                    d_factory=lambda received: _FakeArm(
                        kat.ARM_D, received, events))
        pure_writer.assert_not_called()
        self.assertFalse(output.exists())
        self.assertEqual(events[-2:], [
            f"{kat.ARM_D}_CLOSE", f"{kat.ARM_B}_CLOSE"])

    def test_formal_cli_has_no_manifest_authority_or_factory_override(self):
        destinations = {
            action.dest for action in kat._argument_parser()._actions}
        self.assertEqual(destinations, {
            "help", "scientific_input_directory", "prebuilt_ptx",
            "native_dso", "rtdlexe", "executable_manifest", "output"})
        main_source = inspect.getsource(kat._main)
        self.assertIn("FORMAL_SCIENTIFIC_MANIFEST_IDENTITY", main_source)
        self.assertIn("FORMAL_EXECUTABLE_MANIFEST_SHA256", main_source)
        self.assertIn("prepare_public_verified_rtdlexe_kat_arm", main_source)
        self.assertNotIn("load_lazy_arm_factory", main_source)
        exact_entry_source = inspect.getsource(kat.main_exact_core_boundary)
        self.assertIn("exact_core_boundary=True", exact_entry_source)

    def test_source_has_no_clock_or_attempt_loop_and_common_stage_no_transpose(self):
        source = Path(kat.__file__).read_text(encoding="utf-8")
        for forbidden in (
                "import time", "perf_counter", "process_time", "timeit",
                "np.ascontiguousarray", "queries.T"):
            self.assertNotIn(forbidden, source)
        run_source = inspect.getsource(kat.run_untimed_dual_arm_kat)
        run_tree = ast.parse(run_source)
        self.assertFalse(any(
            isinstance(node, (ast.For, ast.While))
            for node in ast.walk(run_tree)))
        self.assertLess(run_source.index("_run_success(b_arm"),
                        run_source.index("_run_success(d_arm"))
        self.assertLess(run_source.index("_run_success(d_arm"),
                        run_source.index("_run_expected_miss(b_arm"))
        self.assertLess(run_source.index("_run_expected_miss(b_arm"),
                        run_source.index("_run_expected_miss(d_arm"))
        common_source = inspect.getsource(kat._make_common_soa)
        self.assertIn("for column_index in range(7)", common_source)
        self.assertNotIn(".T", common_source)
        self.assertNotIn("ascontiguousarray", common_source)


if __name__ == "__main__":
    unittest.main()
