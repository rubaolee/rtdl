from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

from rtdsl import v4


U32_MAX = 0xFFFFFFFF
HIT_FLAG = 1
MISS_FLAG = 0
HIT_TAG = 0xA11CE001
MISS_TAG = 0xA11CE000
FRONT_HIT_KIND = 0xFE
BACK_HIT_KIND = 0xFF


PRIMITIVE_ID_SOURCE = r'''
@optix.payload
class PrimitiveIdentityPayload:
    primitive_id: u32
    hit_flag: u32
    semantic_tag: u32

@optix.record
class Query:
    origin: vec3f32
    direction: vec3f32
    tmax: f32

@optix.output
class PrimitiveIdentityOutput:
    primitive_id: u32
    hit_flag: u32
    semantic_tag: u32

@optix.program(payload=PrimitiveIdentityPayload, output=PrimitiveIdentityOutput, attributes=(), max_trace_depth=1, max_callable_depth=0)
class PrimitiveIdentityOrMiss:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[Query]) -> TraceRequest:
        query = queries[launch_id]
        initial = PrimitiveIdentityPayload(primitive_id=U32_MAX, hit_flag=MISS_FLAG, semantic_tag=MISS_TAG)
        return optix.trace_request(origin=query.origin, direction=query.direction, tmin=0.0, tmax=query.tmax, payload=initial)

    @optix.closest_hit
    def closest_hit(hit: TriangleHit, payload: PrimitiveIdentityPayload, first_metadata: ReadOnlyView[u32], second_metadata: ReadOnlyView[u32]) -> PrimitiveIdentityPayload:
        updated = PrimitiveIdentityPayload(primitive_id=hit.primitive_index, hit_flag=HIT_FLAG, semantic_tag=HIT_TAG)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: PrimitiveIdentityPayload) -> PrimitiveIdentityPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: PrimitiveIdentityPayload) -> PrimitiveIdentityOutput:
        result = PrimitiveIdentityOutput(primitive_id=payload.primitive_id, hit_flag=payload.hit_flag, semantic_tag=payload.semantic_tag)
        return optix.output(value=result)
'''


def _manifest() -> v4.CallbackModuleManifest:
    return v4.CallbackModuleManifest(
        name="primitive_identity_or_miss",
        payload_record="PrimitiveIdentityPayload",
        output_record="PrimitiveIdentityOutput",
        attribute_types=(),
        constants=(
            v4.FrozenConstant("U32_MAX", v4.U32, U32_MAX),
            v4.FrozenConstant("HIT_FLAG", v4.U32, HIT_FLAG),
            v4.FrozenConstant("MISS_FLAG", v4.U32, MISS_FLAG),
            v4.FrozenConstant("HIT_TAG", v4.U32, HIT_TAG),
            v4.FrozenConstant("MISS_TAG", v4.U32, MISS_TAG),
            v4.FrozenConstant("FRONT_HIT_KIND", v4.U32, FRONT_HIT_KIND),
            v4.FrozenConstant("BACK_HIT_KIND", v4.U32, BACK_HIT_KIND),
        ),
        numeric=v4.NumericContract(),
        resources=v4.ResourceBudget(),
        geometry=v4.GeometryContract(
            v4.GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            v4.BUILTIN_TRIANGLE_CONTRACT,
            False,
        ),
        any_hit_delivery=None,
        selected_linkage=v4.LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason=(
            "user-authored primitive-identity callback compiled by the public "
            "built-in-triangle template"
        ),
    )


def _cpu_primitive_id_or_miss(vertices, triangles, queries):
    """Independent Moller-Trumbore oracle; imports no RTDL execution route."""

    rows = []
    epsilon = 1.0e-8
    for origin, direction, tmax in queries:
        best_t = math.inf
        best_id = U32_MAX
        for primitive_id, (ia, ib, ic) in enumerate(triangles):
            a, b, c = vertices[ia], vertices[ib], vertices[ic]
            edge1 = tuple(b[index] - a[index] for index in range(3))
            edge2 = tuple(c[index] - a[index] for index in range(3))
            pvec = (
                direction[1] * edge2[2] - direction[2] * edge2[1],
                direction[2] * edge2[0] - direction[0] * edge2[2],
                direction[0] * edge2[1] - direction[1] * edge2[0],
            )
            determinant = sum(edge1[index] * pvec[index] for index in range(3))
            if abs(determinant) <= epsilon:
                continue
            inverse = 1.0 / determinant
            tvec = tuple(origin[index] - a[index] for index in range(3))
            u = sum(tvec[index] * pvec[index] for index in range(3)) * inverse
            if u < 0.0 or u > 1.0:
                continue
            qvec = (
                tvec[1] * edge1[2] - tvec[2] * edge1[1],
                tvec[2] * edge1[0] - tvec[0] * edge1[2],
                tvec[0] * edge1[1] - tvec[1] * edge1[0],
            )
            v = sum(direction[index] * qvec[index] for index in range(3)) * inverse
            if v < 0.0 or u + v > 1.0:
                continue
            distance = sum(edge2[index] * qvec[index] for index in range(3)) * inverse
            if distance < 0.0 or distance > tmax:
                continue
            if distance < best_t or (distance == best_t and primitive_id < best_id):
                best_t = distance
                best_id = primitive_id
        rows.append(
            (best_id, HIT_FLAG, HIT_TAG)
            if best_id != U32_MAX
            else (U32_MAX, MISS_FLAG, MISS_TAG)
        )
    return tuple(rows)


def _physical_plan(
    verified,
    *,
    first_metadata_argument_index: int = 2,
    second_metadata_argument_index: int = 3,
) -> v4.BuiltinTriangleCallbackPhysicalPlan:
    oracle_sha = hashlib.sha256(
        inspect.getsource(_cpu_primitive_id_or_miss).encode("utf-8"),
    ).hexdigest()
    orientation = v4.BuiltinTriangleOrientationDeclaration(
        contract_name="public_primitive_identity_ccw_front_v1",
        independent_cpu_oracle_sha256=oracle_sha,
        winding_policy=v4.TriangleWindingPolicy.CCW_IS_FRONT,
        front_hit_kind=FRONT_HIT_KIND,
        back_hit_kind=BACK_HIT_KIND,
        callback_front_hit_kind_constant="FRONT_HIT_KIND",
        callback_back_hit_kind_constant="BACK_HIT_KIND",
        front_hit_selects=v4.AdjacencySide.FRONT,
        back_hit_selects=v4.AdjacencySide.BACK,
    )
    field_ids = v4.BuiltinTriangleU32x3FieldIds(
        vertex_positions="mesh_positions",
        triangle_indices="mesh_indices",
        first_primitive_values="user_column_a",
        second_primitive_values="user_column_b",
        queries="user_rays",
        outputs="primitive_identity_rows",
        status="device_status",
    )
    return v4.build_builtin_triangle_u32x3_physical_plan(
        verified,
        field_ids=field_ids,
        orientation=orientation,
        first_metadata_argument_index=first_metadata_argument_index,
        second_metadata_argument_index=second_metadata_argument_index,
    )


def _target(native: Path, capability=(6, 1)) -> v4.V4Target:
    return v4.V4Target.from_native(
        native,
        optix_sdk="9.0.0",
        compute_capability=capability,
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )


class Goal5801GPublicGenericTriangleAuthoringTest(unittest.TestCase):
    def test_runtime_source_identity_is_newline_canonical_and_mutation_live(self):
        from rtdsl import v4_public_builtin_triangle as public_triangle

        runtime_path = Path(public_triangle.__file__).with_name(
            "v4_triangle_prepared_runtime.py")
        canonical_source = runtime_path.read_text(encoding="utf-8")
        canonical_source = canonical_source.replace("\r\n", "\n").replace(
            "\r", "\n")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lf_path = root / "runtime_lf.py"
            crlf_path = root / "runtime_crlf.py"
            changed_path = root / "runtime_changed.py"
            lf_path.write_bytes(canonical_source.encode("utf-8"))
            crlf_path.write_bytes(
                canonical_source.replace("\n", "\r\n").encode("utf-8"))
            changed_path.write_bytes(
                (canonical_source + "# semantic source mutation\n").encode(
                    "utf-8"))
            expected = public_triangle._EXPECTED_PREPARED_RUNTIME_SHA256
            self.assertEqual(
                public_triangle._source_text_sha256(lf_path), expected)
            self.assertEqual(
                public_triangle._source_text_sha256(crlf_path), expected)
            self.assertNotEqual(
                public_triangle._source_text_sha256(changed_path), expected)
        self.assertEqual(
            public_triangle._projected_runtime_binding_facts()[
                "prepared_runtime_sha256"],
            public_triangle._EXPECTED_PREPARED_RUNTIME_SHA256,
        )

    def test_wrapper_source_identity_is_hash_seed_independent(self):
        root = Path(__file__).resolve().parents[1]
        script = r'''
from pathlib import Path
import tempfile
from rtdsl import v4
from tests.goal5801_g_public_generic_triangle_authoring_test import (
    PRIMITIVE_ID_SOURCE, _manifest, _physical_plan, _target,
)
with tempfile.TemporaryDirectory() as directory:
    native = Path(directory) / "identity-only-test-native.so"
    native.write_bytes(b"identity-only-test-native")
    verified = v4.verify_builtin_triangle_callback_source(
        PRIMITIVE_ID_SOURCE, _manifest())
    program = verified.compile(
        physical_plan=_physical_plan(verified), target=_target(native))
    print(program._expected_wrapper.source_sha256)
'''
        observed = []
        for seed in ("1", "2", "2147483647"):
            environment = dict(os.environ)
            environment["PYTHONHASHSEED"] = seed
            environment["PYTHONPATH"] = str(root / "src")
            completed = subprocess.run(
                [sys.executable, "-c", script],
                cwd=root,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            observed.append(completed.stdout.strip())
        self.assertEqual(len(set(observed)), 1, observed)

    def test_public_verify_compile_is_source_authored_and_has_no_backend_action(self):
        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory) / "librtdl_optix.so"
            native.write_bytes(b"identity-only-test-native")
            target = _target(native)
            with mock.patch("ctypes.CDLL", side_effect=AssertionError("native load")), \
                    mock.patch("subprocess.Popen", side_effect=AssertionError("compiler")):
                verified = v4.verify_builtin_triangle_callback_source(
                    PRIMITIVE_ID_SOURCE, _manifest())
                program = verified.compile(
                    physical_plan=_physical_plan(verified), target=target)
            self.assertEqual(
                program.callback.program.manifest.name,
                "primitive_identity_or_miss",
            )
            self.assertEqual(
                {item.role for item in program.callback.program.functions},
                {
                    v4.CallbackRole.MAKE_RAY,
                    v4.CallbackRole.CLOSEST_HIT,
                    v4.CallbackRole.MISS,
                    v4.CallbackRole.FINALIZE,
                },
            )
            root = Path(__file__).resolve().parents[1]
            product_source = "\n".join(
                (root / relative).read_text(encoding="utf-8")
                for relative in (
                    "src/rtdsl/v4.py",
                    "src/rtdsl/v4_public_builtin_triangle.py",
                    "src/rtdsl/v4_triangle_optix_compiler.py",
                    "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
                )
            )
            for forbidden in (
                "PrimitiveIdentityOrMiss", "primitive_identity_or_miss",
                "A11CE001", "bounded_relation", "triangle_reduction",
                "raydb", "paper",
            ):
                self.assertNotIn(forbidden, product_source)
            with self.assertRaises(v4.PublicCallbackLifecycleError) as forged:
                v4.VerifiedBuiltinTriangleCallbackSource(
                    PRIMITIVE_ID_SOURCE,
                    _manifest(),
                    verified.callback,
                    _construction_token=None,
                )
            self.assertEqual(forged.exception.code, "GC027_LIVE_AUTHORITY_REQUIRED")

    def test_metadata_argument_bindings_change_generated_dataflow(self):
        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory) / "librtdl_optix.so"
            native.write_bytes(b"identity-only-test-native")
            verified = v4.verify_builtin_triangle_callback_source(
                PRIMITIVE_ID_SOURCE, _manifest())
            normal = verified.compile(
                physical_plan=_physical_plan(verified), target=_target(native))
            swapped = verified.compile(
                physical_plan=_physical_plan(
                    verified,
                    first_metadata_argument_index=3,
                    second_metadata_argument_index=2,
                ),
                target=_target(native),
            )
            normal_source = normal._expected_wrapper.source
            swapped_source = swapped._expected_wrapper.source
            self.assertNotEqual(
                normal._expected_wrapper.source_sha256,
                swapped._expected_wrapper.source_sha256,
            )
            self.assertIn(
                "RTDL_METADATA_ARGUMENT_2=primitive_front_value;"
                "SOURCE=params.front_values",
                normal_source,
            )
            self.assertIn(
                "RTDL_METADATA_ARGUMENT_3=primitive_back_value;"
                "SOURCE=params.back_values",
                normal_source,
            )
            self.assertIn(
                "RTDL_METADATA_ARGUMENT_2=primitive_back_value;"
                "SOURCE=params.back_values",
                swapped_source,
            )
            self.assertIn(
                "RTDL_METADATA_ARGUMENT_3=primitive_front_value;"
                "SOURCE=params.front_values",
                swapped_source,
            )
            normal_call = next(
                line for line in normal_source.splitlines()
                if "rtdl_v4_closest_hit_" in line and "(void)" in line)
            swapped_call = next(
                line for line in swapped_source.splitlines()
                if "rtdl_v4_closest_hit_" in line and "(void)" in line)
            self.assertLess(
                normal_call.index("params.front_values"),
                normal_call.index("params.back_values"),
            )
            self.assertLess(
                swapped_call.index("params.back_values"),
                swapped_call.index("params.front_values"),
            )

    def test_public_batch_has_no_expected_output_or_oracle_surface(self):
        with self.assertRaises(TypeError):
            v4.BuiltinTriangleCallbackBatch(
                queries=(), expected_output=(),  # type: ignore[call-arg]
            )

    def test_single_semantic_leaf_mutation_cannot_reuse_accepted_physical_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory) / "librtdl_optix.so"
            native.write_bytes(b"identity-only-test-native")
            target = _target(native)
            accepted = v4.verify_builtin_triangle_callback_source(
                PRIMITIVE_ID_SOURCE, _manifest())
            plan = _physical_plan(accepted)
            changed_source = PRIMITIVE_ID_SOURCE.replace(
                "primitive_id=hit.primitive_index",
                "primitive_id=first_metadata[hit.primitive_index]",
                1,
            )
            changed = v4.verify_builtin_triangle_callback_source(
                changed_source, _manifest())
            self.assertNotEqual(
                changed.callback.ir_sha256, accepted.callback.ir_sha256)
            self.assertEqual(
                changed.callback.effect_digest, accepted.callback.effect_digest)
            with self.assertRaises(v4.PhysicalSchemaError) as raised:
                changed.compile(physical_plan=plan, target=target)
            self.assertEqual(raised.exception.code, "callback_binding")

    def test_contract_accepts_and_all_five_mechanisms_are_sole_reason_live(self):
        from rtdsl import v4_public_builtin_triangle as public_triangle

        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory) / "librtdl_optix.so"
            native.write_bytes(b"identity-only-test-native")
            target = _target(native)
            verified = v4.verify_builtin_triangle_callback_source(
                PRIMITIVE_ID_SOURCE, _manifest())
            program = verified.compile(
                physical_plan=_physical_plan(verified), target=target)

            @dataclasses.dataclass(frozen=True)
            class Composed:
                ptx_sha256: str

            @dataclasses.dataclass(frozen=True)
            class Executable:
                wrapper: object
                composed: object
                executable_sha256: str
                authority_sha256: str
                plan_sha256: str
                abi_sha256: str

            executable = Executable(
                wrapper=program._expected_wrapper,
                composed=Composed("b" * 64),
                executable_sha256="a" * 64,
                authority_sha256=public_triangle._physical_authority_sha256(
                    program._authority),
                plan_sha256=program._canonical_plan.plan_sha256,
                abi_sha256=program._abi.abi_sha256,
            )
            with mock.patch.object(
                public_triangle,
                "_rederive_checked_executable_sha256",
                return_value="a" * 64,
            ):
                decision = public_triangle._generic_contract_decision(
                    program, executable)
            self.assertEqual(decision.verdict, "ACCEPT", decision.to_mapping())
            self.assertEqual(decision.findings, ())

            projected_effects = public_triangle._compiled_role_effects(
                program._abi)
            projected_effects["closest_hit"] = ()
            with mock.patch.object(
                public_triangle,
                "_rederive_checked_executable_sha256",
                return_value="a" * 64,
            ), mock.patch.object(
                public_triangle,
                "_compiled_role_effects",
                return_value=projected_effects,
            ):
                effect_decision = public_triangle._generic_contract_decision(
                    program, executable)
            self.assertEqual(effect_decision.verdict, "REJECT")
            self.assertEqual(
                [item.reason_id for item in effect_decision.findings],
                ["CP001_ROLE_EFFECT_MISMATCH"],
            )

            projected_ownership = public_triangle._projected_ownership(
                program._authority, program._abi)
            projected_ownership["closest_hit_payload"] = "d" * 64
            with mock.patch.object(
                public_triangle,
                "_rederive_checked_executable_sha256",
                return_value="a" * 64,
            ), mock.patch.object(
                public_triangle,
                "_projected_ownership",
                return_value=projected_ownership,
            ):
                ownership_decision = public_triangle._generic_contract_decision(
                    program, executable)
            self.assertEqual(ownership_decision.verdict, "REJECT")
            self.assertEqual(
                [item.reason_id for item in ownership_decision.findings],
                ["CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH"],
            )

            resealed_actual_only = dataclasses.replace(
                executable, executable_sha256="c" * 64)
            with mock.patch.object(
                public_triangle,
                "_rederive_checked_executable_sha256",
                return_value="a" * 64,
            ):
                identity_decision = public_triangle._generic_contract_decision(
                    program, resealed_actual_only)
            self.assertEqual(identity_decision.verdict, "REJECT")
            self.assertEqual(
                [item.reason_id for item in identity_decision.findings],
                ["CP005_EXECUTABLE_IDENTITY_MISMATCH"],
            )

            runtime_projection = public_triangle._projected_runtime_binding_facts()
            runtime_projection["native_execute_symbol"] = "wrong_native_execute_symbol"
            with mock.patch.object(
                public_triangle,
                "_rederive_checked_executable_sha256",
                return_value="a" * 64,
            ), mock.patch.object(
                public_triangle,
                "_projected_runtime_binding_facts",
                return_value=runtime_projection,
            ):
                physical_decision = public_triangle._generic_contract_decision(
                    program, executable)
            self.assertEqual(physical_decision.verdict, "REJECT")
            self.assertEqual(
                [item.reason_id for item in physical_decision.findings],
                ["CP003_PHYSICAL_BINDING_MISMATCH"],
            )

            with mock.patch.object(
                public_triangle,
                "_rederive_checked_executable_sha256",
                return_value="a" * 64,
            ), mock.patch.object(
                public_triangle,
                "_continuation_projection",
                return_value="MISSING_FAIL_CLOSED_STATUS_OR_CONTINUATION",
            ):
                continuation_decision = public_triangle._generic_contract_decision(
                    program, executable)
            self.assertEqual(continuation_decision.verdict, "REJECT")
            self.assertEqual(
                [item.reason_id for item in continuation_decision.findings],
                ["CP004_CONTINUATION_STATUS_MISMATCH"],
            )

    def test_public_execute_rechecks_exact_executable_and_receipt_identities(self):
        from rtdsl import v4_public_builtin_triangle as public_triangle
        from rtdsl.physical_execution_provenance import (
            CapturedTraversalObservation,
            _native_audit_mix_u64,
            physical_program_bundle_id,
        )

        identity = v4.BuiltinTriangleCallbackExecutableIdentity(
            program_identity_sha256="1" * 64,
            physical_schema_sha256="2" * 64,
            canonical_plan_sha256="3" * 64,
            callback_abi_sha256="4" * 64,
            wrapper_source_sha256="5" * 64,
            generated_executable_sha256="6" * 64,
            composed_ptx_sha256="7" * 64,
            native_library_sha256="8" * 64,
        )
        decision = v4.ProtocolContractDecision(
            verdict="ACCEPT",
            findings=(),
            contract_sha256="9" * 64,
            projection_sha256="a" * 64,
        )
        output = ((17, 1, HIT_TAG),)
        output_sha = public_triangle._digest(output)
        bundle = "v4_builtin_triangle_callback_ir_four_role_composed"
        bundle_id = physical_program_bundle_id(bundle)
        self.assertEqual(bundle_id, 0xD0EACA28180FDB05)
        self.assertEqual(
            _native_audit_mix_u64(0, bundle_id), 0x05DA2844B6A9E38E)
        self.assertEqual(
            _native_audit_mix_u64(0, 1), 0x2F41A7A6084CD8D6)
        snapshot_items = (
            ("nonce_hi", 1), ("nonce_lo", 2),
            ("attempted_launch_count", 1),
            ("successful_launch_count", 1), ("failed_launch_count", 0),
            ("complete_context_launch_count", 1),
            ("incomplete_context_launch_count", 0),
            ("context_bind_count", 1), ("raygen_invocation_count", 1),
            ("program_bundle_mix", _native_audit_mix_u64(0, bundle_id)),
            ("traversable_mix", _native_audit_mix_u64(0, 1)),
            ("pipeline_mix", 1), ("sbt_mix", 1), ("stream_mix", 1),
            ("params_mix", 1), ("callsite_mix", 1),
            ("first_program_bundle_id", bundle_id),
            ("last_program_bundle_id", bundle_id),
            ("first_traversable", 1), ("last_traversable", 1),
            ("pending_context_at_finish", 0), ("session_error", 0),
            ("incomplete_callsite_record_count", 0),
            ("incomplete_callsite_lines", (0,) * 32),
        )
        receipt = CapturedTraversalObservation(
            provider_library_path=Path("/evidence/librtdl_optix.so"),
            provider_library_sha256=identity.native_library_sha256,
            nonce_hi=1,
            nonce_lo=2,
            physical_executor_classification="optix_traversal_observed",
            expected_program_bundles=(bundle,),
            expected_program_bundle_ids=(bundle_id,),
            expected_program_observed_at_receipt_edge=True,
            native_snapshot_items=snapshot_items,
        ).build_receipt(
            semantic_digest="b" * 64,
            output_digest=output_sha,
            route_identity=(
                "v4_builtin_triangle_callback_ir:four_role_composed_v1"),
        )
        valid_result = types.SimpleNamespace(
            output=output,
            hit_observations=(),
            role_counters=(),
            launch_status=(),
            traversal_receipt=receipt,
            output_sha256=output_sha,
            composed_ptx_sha256=identity.composed_ptx_sha256,
            native_library_sha256=identity.native_library_sha256,
        )

        class FakeOwner:
            def __init__(self):
                self.result = valid_result
                self.seen_queries = None

            def execute(self, queries):
                self.seen_queries = queries
                return self.result

            def close(self):
                return None

        owner = FakeOwner()
        prepared = v4.PreparedBuiltinTriangleCallbackProgram(
            owner=owner,
            identity=identity,
            decision=decision,
            _construction_token=public_triangle._CONSTRUCTION_TOKEN,
        )
        batch = v4.BuiltinTriangleCallbackBatch(
            queries=(((0.0, 0.0, 1.0), (0.0, 0.0, -1.0), 2.0),),
        )
        accepted = prepared.execute(batch)
        self.assertEqual(accepted.output, output)
        self.assertEqual(owner.seen_queries, batch.queries)

        partial_body = {
            "physical_executor_classification": "optix_traversal_observed",
            "route_identity": (
                "v4_builtin_triangle_callback_ir:four_role_composed_v1"),
            "provider_library_sha256": identity.native_library_sha256,
            "output_digest": output_sha,
            "semantic_digest": "b" * 64,
            "expected_program_bundles": (bundle,),
        }
        owner.result = types.SimpleNamespace(
            **{
                **valid_result.__dict__,
                "traversal_receipt": {
                    **partial_body,
                    "receipt_sha256": public_triangle._digest(partial_body),
                },
            },
        )
        with self.assertRaises(v4.PublicCallbackLifecycleError) as partial:
            prepared.execute(batch)
        self.assertEqual(
            partial.exception.code, "GC026_TRAVERSAL_RECEIPT_INVALID")

        receipt_mutations = {
            "failed_launch": lambda forged: forged["native_snapshot"].__setitem__(
                "failed_launch_count", 1),
            "missing_raygen": lambda forged: forged["native_snapshot"].pop(
                "raygen_invocation_count"),
            "wrong_raygen_count": lambda forged: forged[
                "native_snapshot"].__setitem__("raygen_invocation_count", 0),
            "expected_program_not_observed": lambda forged: forged.__setitem__(
                "expected_program_observed_at_receipt_edge", False),
            "incomplete_context": lambda forged: forged[
                "native_snapshot"].__setitem__(
                    "incomplete_context_launch_count", 1),
            "zero_physical_traversable": lambda forged: (
                forged["native_snapshot"].__setitem__(
                    "first_traversable", 0),
                forged["native_snapshot"].__setitem__(
                    "last_traversable", 0),
                forged["native_snapshot"].__setitem__(
                    "traversable_mix", 0),
            ),
            "distinct_one_launch_traversables": lambda forged: forged[
                "native_snapshot"].__setitem__("last_traversable", 2),
            "wrong_program_bundle_mix": lambda forged: forged[
                "native_snapshot"].__setitem__("program_bundle_mix", 0),
            "wrong_traversable_mix": lambda forged: forged[
                "native_snapshot"].__setitem__("traversable_mix", 0),
            "out_of_range_native_u64": lambda forged: (
                forged["native_snapshot"].__setitem__(
                    "first_traversable", 1 << 64),
                forged["native_snapshot"].__setitem__(
                    "last_traversable", 1 << 64),
                forged["native_snapshot"].__setitem__(
                    "traversable_mix", _native_audit_mix_u64(0, 1 << 64)),
            ),
        }
        for label, mutate in receipt_mutations.items():
            forged = json.loads(json.dumps(receipt))
            mutate(forged)
            forged_body = dict(forged)
            forged_body.pop("receipt_sha256")
            forged["receipt_sha256"] = public_triangle._digest(forged_body)
            owner.result = types.SimpleNamespace(
                **{**valid_result.__dict__, "traversal_receipt": forged})
            with self.subTest(receipt_mutation=label):
                with self.assertRaises(
                        v4.PublicCallbackLifecycleError) as rejected:
                    prepared.execute(batch)
                self.assertEqual(
                    rejected.exception.code,
                    "GC026_TRAVERSAL_RECEIPT_INVALID",
                )

        owner.result = types.SimpleNamespace(
            **{**valid_result.__dict__, "composed_ptx_sha256": "c" * 64},
        )
        with self.assertRaises(v4.PublicCallbackLifecycleError) as ptx:
            prepared.execute(batch)
        self.assertEqual(ptx.exception.code, "GC023_EXECUTED_PTX_IDENTITY_MISMATCH")

        owner.result = types.SimpleNamespace(
            **{**valid_result.__dict__, "native_library_sha256": "d" * 64},
        )
        with self.assertRaises(v4.PublicCallbackLifecycleError) as native:
            prepared.execute(batch)
        self.assertEqual(native.exception.code, "GC024_EXECUTED_NATIVE_IDENTITY_MISMATCH")

        owner.result = types.SimpleNamespace(
            **{
                **valid_result.__dict__,
                "traversal_receipt": {
                    **valid_result.traversal_receipt,
                    "receipt_sha256": "e" * 64,
                },
            },
        )
        with self.assertRaises(v4.PublicCallbackLifecycleError) as receipt:
            prepared.execute(batch)
        self.assertEqual(receipt.exception.code, "GC026_TRAVERSAL_RECEIPT_INVALID")
        prepared.close()

    @unittest.skipUnless(
        os.environ.get("RTDL_GOAL5801_G_NATIVE"),
        "set RTDL_GOAL5801_G_NATIVE for the untimed Home GPU KAT",
    )
    def test_real_public_lifecycle_matches_independent_cpu_oracle(self):
        from rtdsl import v4_public_builtin_triangle as public_triangle

        native = Path(os.environ["RTDL_GOAL5801_G_NATIVE"])
        optix_include = Path(os.environ["RTDL_GOAL5801_G_OPTIX_INCLUDE"])
        cuda_include = Path(os.environ["RTDL_GOAL5801_G_CUDA_INCLUDE"])
        capability = tuple(
            int(item) for item in
            os.environ.get("RTDL_GOAL5801_G_COMPUTE_CAPABILITY", "6.1").split(".")
        )
        target = _target(native, capability)
        verified = v4.verify_builtin_triangle_callback_source(
            PRIMITIVE_ID_SOURCE, _manifest())
        physical_plan = _physical_plan(verified)

        # Hostile semantic leaf is rejected in the target-bound compile phase,
        # before materialize exists and therefore before any launch is possible.
        changed_source = PRIMITIVE_ID_SOURCE.replace(
            "primitive_id=hit.primitive_index",
            "primitive_id=first_metadata[hit.primitive_index]",
            1,
        )
        changed = v4.verify_builtin_triangle_callback_source(
            changed_source, _manifest())
        with self.assertRaises(v4.PhysicalSchemaError):
            changed.compile(physical_plan=physical_plan, target=target)

        toolchain = v4.V4Toolchain.current(
            compute_capability=capability,
            optix_include=optix_include,
            cuda_include=cuda_include,
        )
        vertices = (
            (-1.0, -1.0, 0.0), (0.0, -1.0, 0.0), (-0.5, 1.0, 0.0),
            (1.0, -1.0, 0.0), (2.0, -1.0, 0.0), (1.5, 1.0, 0.0),
        )
        triangles = ((0, 1, 2), (3, 4, 5))
        queries = (
            ((-0.5, 0.0, 1.0), (0.0, 0.0, -1.0), 10.0),
            ((1.5, 0.0, 1.0), (0.0, 0.0, -1.0), 10.0),
            ((4.0, 0.0, 1.0), (0.0, 0.0, -1.0), 10.0),
        )
        oracle = _cpu_primitive_id_or_miss(vertices, triangles, queries)
        static_input = v4.BuiltinTriangleCallbackStaticInput(
            vertices=vertices,
            triangles=triangles,
            first_primitive_values=(17, 29),
            second_primitive_values=(31, 43),
        )
        batch = v4.BuiltinTriangleCallbackBatch(queries=queries)

        def metadata_oracle(values):
            return tuple(
                (values[row[0]], row[1], row[2])
                if row[1] == HIT_FLAG else row
                for row in oracle
            )

        def run_variant(label, variant_program, expected):
            materialized = variant_program.materialize(toolchain=toolchain)
            self.assertEqual(
                materialized.protocol_contract_decision.verdict, "ACCEPT")
            # Evidence-only private inspection preserves the generated PTX
            # payload.  Application code still uses only the public lifecycle.
            composed_ptx = materialized._executable.composed.ptx
            prepared = materialized.prepare(static_input)
            try:
                result = prepared.execute(batch)
                lifecycle_receipt = prepared.lifecycle_receipt
                self.assertEqual(result.output, expected)
                self.assertEqual(
                    result.protocol_contract_decision.verdict, "ACCEPT")
                self.assertEqual(
                    result.traversal_receipt[
                        "physical_executor_classification"],
                    "optix_traversal_observed",
                )
            finally:
                prepared.close()
            self.assertTrue(prepared.closed)
            prepared.close()
            identity = {
                **dataclasses.asdict(result.executable_identity),
                "identity_sha256": result.executable_identity.identity_sha256,
            }
            projection = {
                "label": label,
                "output": [list(row) for row in result.output],
                "output_sha256": result.output_sha256,
                "hit_observations": list(result.hit_observations),
                "role_counters": list(result.role_counters),
                "launch_status": list(result.launch_status),
                "traversal_receipt": result.traversal_receipt,
                "lifecycle_receipt": lifecycle_receipt,
                "executable_identity": identity,
                "protocol_contract_decision": (
                    result.protocol_contract_decision.to_mapping()),
                "composed_ptx_bytes": len(composed_ptx.encode("utf-8")),
                "composed_ptx_sha256": hashlib.sha256(
                    composed_ptx.encode("utf-8")).hexdigest(),
            }
            return projection, composed_ptx

        baseline_program = verified.compile(
            physical_plan=physical_plan, target=target)
        normal_metadata_program = changed.compile(
            physical_plan=_physical_plan(changed), target=target)
        swapped_metadata_program = changed.compile(
            physical_plan=_physical_plan(
                changed,
                first_metadata_argument_index=3,
                second_metadata_argument_index=2,
            ),
            target=target,
        )
        baseline, baseline_ptx = run_variant(
            "baseline_primitive_identity", baseline_program, oracle)
        normal_metadata, normal_metadata_ptx = run_variant(
            "fresh_leaf_reads_argument_2_bound_to_front_values",
            normal_metadata_program,
            metadata_oracle(static_input.first_primitive_values),
        )
        swapped_metadata, swapped_metadata_ptx = run_variant(
            "same_leaf_argument_2_rebound_to_back_values",
            swapped_metadata_program,
            metadata_oracle(static_input.second_primitive_values),
        )
        self.assertNotEqual(
            normal_metadata["executable_identity"]["wrapper_source_sha256"],
            swapped_metadata["executable_identity"]["wrapper_source_sha256"],
        )

        root = Path(__file__).resolve().parents[1]
        runtime_path = root / "src/rtdsl/v4_triangle_prepared_runtime.py"
        runtime_bytes = runtime_path.read_bytes()
        product_paths = (
            "src/native/optix/rtdl_optix_core.cpp",
            "src/native/optix/rtdl_optix_prelude.h",
            "src/rtdsl/v4.py",
            "src/rtdsl/physical_execution_provenance.py",
            "src/rtdsl/v4_public_builtin_triangle.py",
            "src/rtdsl/v4_triangle_prepared_runtime.py",
            "src/rtdsl/v4_triangle_optix_compiler.py",
            "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
            "tests/goal5801_g_public_generic_triangle_authoring_test.py",
        )
        evidence = {
            "schema": "rtdl.goal5801_g.public_triangle_home_kat.v2",
            "status": "PASS__ORACLE_ISOLATED_REHASHABLE_HOME_EXECUTION",
            "oracle_output_or_expected_value_passed_into_execute": False,
            "oracle_compared_only_after_public_execute_returned": True,
            "cpu_oracle_source_identity_carried_as_plan_metadata": True,
            "prepared_runtime_source_identity": {
                "raw_bytes": len(runtime_bytes),
                "raw_sha256": hashlib.sha256(runtime_bytes).hexdigest(),
                "canonical_text_sha256": (
                    public_triangle._source_text_sha256(runtime_path)),
                "canonical_identity_is_not_raw_byte_identity": True,
            },
            "independent_cpu_oracle_sha256": hashlib.sha256(
                inspect.getsource(_cpu_primitive_id_or_miss).encode("utf-8"),
            ).hexdigest(),
            "independent_cpu_oracle_output": [list(row) for row in oracle],
            "source_files": [{
                "path": relative,
                "bytes": (root / relative).stat().st_size,
                "sha256": hashlib.sha256(
                    (root / relative).read_bytes()).hexdigest(),
            } for relative in product_paths],
            "runs": [baseline, normal_metadata, swapped_metadata],
            "stale_plan_semantic_leaf_rejected_before_materialize": True,
            "fresh_semantic_leaf_materialized_and_executed": True,
            "metadata_argument_rebinding_changed_wrapper_and_output": True,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "pod": False,
            "wsl": False,
        }
        unsigned = json.dumps(
            evidence, allow_nan=False, separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")
        evidence["receipt_sha256"] = hashlib.sha256(unsigned).hexdigest()
        output_path_value = os.environ.get("RTDL_GOAL5801_G_EVIDENCE_OUTPUT")
        if output_path_value:
            output_path = Path(output_path_value)
            if output_path.exists() or output_path.is_symlink():
                raise FileExistsError(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            for label, ptx in (
                ("baseline", baseline_ptx),
                ("normal_metadata", normal_metadata_ptx),
                ("swapped_metadata", swapped_metadata_ptx),
            ):
                ptx_path = output_path.with_name(
                    f"{output_path.stem}_{label}.ptx")
                if ptx_path.exists() or ptx_path.is_symlink():
                    raise FileExistsError(ptx_path)
                ptx_path.write_bytes(ptx.encode("utf-8"))
            output_path.write_text(
                json.dumps(evidence, indent=2, allow_nan=False) + "\n",
                encoding="utf-8",
            )
        print(
            "GOAL5801_G_HOME_EVIDENCE=" + json.dumps(
                evidence, allow_nan=False, separators=(",", ":"),
                sort_keys=True),
            flush=True,
        )


if __name__ == "__main__":
    unittest.main()
