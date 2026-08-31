from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import unittest

from rtdsl.v4_callback_frontend import compile_callback_source, parse_callback_source
from rtdsl.v4_callback_interpreter import execute_callback_role
from rtdsl.v4_callback_ir import (
    AnyHitDeliveryContract,
    CallbackModuleManifest,
    CallbackRole,
    CallbackVerificationError,
    GeometryAdmission,
    GeometryContract,
    LinkageMechanism,
    NumericContract,
    ResourceBudget,
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
)
from rtdsl.v4_typed_physical_schema import (
    BUILTIN_TRIANGLE_CONTRACT,
    AdjacencySide,
    BufferAccess,
    BufferDomain,
    BufferFieldSchema,
    BufferSemantic,
    CountRelation,
    GasSchema,
    GasUpdatePolicy,
    GeometryFamily,
    HitChannelProducer,
    HitChannelSchema,
    HitChannelSemantic,
    HitMetadataBinding,
    PhysicalBufferBinding,
    PhysicalSchemaError,
    PhysicalValueType,
    ReferencePhysicalTemplate,
    ReferenceTargetProfile,
    ReferenceTemplateId,
    TriangleOrientationAuthority,
    TriangleWindingPolicy,
    TypedPhysicalSchemaV1,
    default_reference_templates,
    lower_canonical_reference_plan,
    resolve_triangle_adjacency,
    triangle_author_semantics_sha256,
    typed_physical_schema_from_dict,
    verify_buffer_bindings,
    verify_callback_program_for_geometry,
    verify_reference_triangle_contents,
    verify_typed_physical_schema,
)


ROOT = Path(__file__).resolve().parents[1]
GOAL5753_ARCHIVE = ROOT / "history/internal_docs/goal5753_held_out_particle_tracking_exam_evidence_20260811.tar.gz"
AUTHOR_MEMBER = "goal5753/AUTHOR_SOURCE/optix/optixQueryKernel.cu"
ORACLE_PATH = ROOT / "Paper-reproduction-apps/goal5753-held-out-particle-tracking/independent_oracle.py"
AUTHOR_SHA256 = "e67c909d6bea027dc882189aacce4b6f82fde8e6a28c41315b46037692d3b8b7"
FRONT_HIT_KIND = 0xFE
BACK_HIT_KIND = 0xFF


TRIANGLE_SOURCE = r'''
@optix.payload
class CellPayload:
    cell_id: u32
    neighbor_id: u32
    face_id: u32

@optix.record
class Query:
    origin: vec3f32
    direction: vec3f32
    tmax: f32

@optix.output
class CellOutput:
    cell_id: u32
    neighbor_id: u32
    face_id: u32

@optix.program(
    payload=CellPayload,
    output=CellOutput,
    attributes=(),
    max_trace_depth=1,
    max_callable_depth=0,
)
class CellLocator:
    @optix.make_ray
    def make_ray(launch_id: u32, queries: ReadOnlyView[Query]) -> TraceRequest:
        query = queries[launch_id]
        initial = CellPayload(cell_id=U32_MAX, neighbor_id=U32_MAX, face_id=U32_MAX)
        return optix.trace_request(
            origin=query.origin,
            direction=query.direction,
            tmin=0.0,
            tmax=query.tmax,
            payload=initial,
        )

    @optix.closest_hit
    def closest_hit(
        hit: TriangleHit,
        payload: CellPayload,
        first_side: ReadOnlyView[u32],
        second_side: ReadOnlyView[u32],
    ) -> CellPayload:
        is_front = hit.hit_kind == FRONT_HIT_KIND
        selected = first_side[hit.primitive_index] if is_front else second_side[hit.primitive_index]
        neighbor = second_side[hit.primitive_index] if is_front else first_side[hit.primitive_index]
        updated = CellPayload(cell_id=selected, neighbor_id=neighbor, face_id=hit.primitive_index)
        return optix.payload(payload=updated)

    @optix.miss
    def miss(ray: Ray3f, payload: CellPayload) -> CellPayload:
        return optix.payload(payload=payload)

    @optix.finalize
    def finalize(payload: CellPayload) -> CellOutput:
        result = CellOutput(cell_id=payload.cell_id, neighbor_id=payload.neighbor_id, face_id=payload.face_id)
        return optix.output(value=result)
'''


def manifest() -> CallbackModuleManifest:
    from rtdsl.v4_callback_ir import FrozenConstant, U32

    return CallbackModuleManifest(
        name="cell_locator",
        payload_record="CellPayload",
        output_record="CellOutput",
        attribute_types=(),
        constants=(
            FrozenConstant("U32_MAX", U32, 0xFFFFFFFF),
            FrozenConstant("FRONT_HIT_KIND", U32, FRONT_HIT_KIND),
            FrozenConstant("BACK_HIT_KIND", U32, BACK_HIT_KIND),
        ),
        numeric=NumericContract(),
        resources=ResourceBudget(),
        geometry=GeometryContract(
            GeometryAdmission.OPTIX_BUILTIN_SEMANTICS,
            BUILTIN_TRIANGLE_CONTRACT,
            False,
        ),
        any_hit_delivery=None,
        selected_linkage=LinkageMechanism.TRUSTED_SINGLE_MODULE_COMPOSITION_V1,
        linkage_selection_reason="Goal5755 CPU/reference physical admission only",
    )


def verified_callback():
    return verify_callback_program_for_geometry(
        parse_callback_source(
            TRIANGLE_SOURCE,
            manifest(),
            schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
        ),
        GeometryFamily.BUILTIN_TRIANGLE,
    )


def author_source_bytes() -> bytes:
    with tarfile.open(GOAL5753_ARCHIVE, "r:gz") as archive:
        item = archive.extractfile(AUTHOR_MEMBER)
        assert item is not None
        return item.read()


def orientation_authority(callback=None) -> TriangleOrientationAuthority:
    callback = verified_callback() if callback is None else callback
    return TriangleOrientationAuthority(
        contract_name="goal5753_particle_face_adjacency_v1",
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        vertex_positions_semantic=BufferSemantic.VERTEX_POSITIONS,
        triangle_indices_semantic=BufferSemantic.TRIANGLE_INDICES,
        front_values_semantic=BufferSemantic.PRIMITIVE_FRONT_VALUE,
        back_values_semantic=BufferSemantic.PRIMITIVE_BACK_VALUE,
        winding_policy=TriangleWindingPolicy.CCW_IS_FRONT,
        front_hit_kind=FRONT_HIT_KIND,
        back_hit_kind=BACK_HIT_KIND,
        callback_front_hit_kind_constant="FRONT_HIT_KIND",
        callback_back_hit_kind_constant="BACK_HIT_KIND",
        front_hit_selects=AdjacencySide.FRONT,
        back_hit_selects=AdjacencySide.BACK,
        author_source_sha256=hashlib.sha256(author_source_bytes()).hexdigest(),
        author_semantics_sha256=triangle_author_semantics_sha256(
            front_hit_kind=FRONT_HIT_KIND,
            back_hit_kind=BACK_HIT_KIND,
            front_hit_selects=AdjacencySide.FRONT,
            back_hit_selects=AdjacencySide.BACK,
        ),
        independent_cpu_oracle_sha256=hashlib.sha256(ORACLE_PATH.read_bytes()).hexdigest(),
    )


def triangle_schema(callback=None) -> TypedPhysicalSchemaV1:
    callback = verified_callback() if callback is None else callback
    authority = orientation_authority(callback)
    ro = BufferAccess.READ_ONLY
    buffers = (
        BufferFieldSchema("positions_xyz", BufferSemantic.VERTEX_POSITIONS, BufferDomain.VERTEX, PhysicalValueType.VEC3F32, ro, CountRelation.VERTEX_COUNT, 16),
        BufferFieldSchema("connectivity_abc", BufferSemantic.TRIANGLE_INDICES, BufferDomain.PRIMITIVE, PhysicalValueType.VEC3U32, ro, CountRelation.PRIMITIVE_COUNT, 16),
        # Deliberately neutral field IDs: admission is driven by semantic IDs,
        # not by the strings "front" and "back".
        BufferFieldSchema("side_alpha", BufferSemantic.PRIMITIVE_FRONT_VALUE, BufferDomain.PRIMITIVE, PhysicalValueType.U32, ro, CountRelation.PRIMITIVE_COUNT),
        BufferFieldSchema("side_omega", BufferSemantic.PRIMITIVE_BACK_VALUE, BufferDomain.PRIMITIVE, PhysicalValueType.U32, ro, CountRelation.PRIMITIVE_COUNT),
        BufferFieldSchema("queries", BufferSemantic.QUERY_INPUT, BufferDomain.QUERY, PhysicalValueType.OPAQUE_RECORD, ro, CountRelation.QUERY_COUNT, 16),
        BufferFieldSchema("outputs", BufferSemantic.OUTPUT_VALUE, BufferDomain.OUTPUT, PhysicalValueType.OPAQUE_RECORD, BufferAccess.WRITE_ONLY, CountRelation.OUTPUT_COUNT_EQUALS_QUERY_COUNT, 16),
        BufferFieldSchema("status", BufferSemantic.STATUS, BufferDomain.LAUNCH_PARAM, PhysicalValueType.STATUS_RECORD, BufferAccess.INTERNAL_STATUS, CountRelation.SINGLETON, 16),
    )
    hit_roles = (CallbackRole.CLOSEST_HIT,)
    channels = (
        HitChannelSchema(HitChannelSemantic.PRIMITIVE_INDEX, PhysicalValueType.U32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
        HitChannelSchema(HitChannelSemantic.TRIANGLE_FRONT_BACK_HIT_KIND, PhysicalValueType.U32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
        HitChannelSchema(HitChannelSemantic.TRIANGLE_BARYCENTRICS, PhysicalValueType.VEC2F32, HitChannelProducer.OPTIX_BUILTIN, hit_roles),
        HitChannelSchema(HitChannelSemantic.PRIMITIVE_METADATA, PhysicalValueType.U32, HitChannelProducer.COMPILER_METADATA_LOOKUP, hit_roles),
    )
    return TypedPhysicalSchemaV1(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        geometry_family=GeometryFamily.BUILTIN_TRIANGLE,
        buffers=buffers,
        hit_channels=channels,
        hit_metadata_bindings=(
            HitMetadataBinding(CallbackRole.CLOSEST_HIT, 2, BufferSemantic.PRIMITIVE_FRONT_VALUE),
            HitMetadataBinding(CallbackRole.CLOSEST_HIT, 3, BufferSemantic.PRIMITIVE_BACK_VALUE),
        ),
        gas=GasSchema(
            GeometryFamily.BUILTIN_TRIANGLE,
            (BufferSemantic.VERTEX_POSITIONS, BufferSemantic.TRIANGLE_INDICES),
            GasUpdatePolicy.STATIC,
            1,
            1,
        ),
        triangle_winding=TriangleWindingPolicy.CCW_IS_FRONT,
        triangle_orientation_authority_sha256=authority.authority_sha256,
    )


def target(**changes) -> ReferenceTargetProfile:
    return dataclasses.replace(ReferenceTargetProfile(
        provider="optix",
        optix_sdk="8.0.0",
        compute_capability="8.9",
        native_sha256="a" * 64,
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    ), **changes)


def admitted():
    callback = verified_callback()
    authority = orientation_authority(callback)
    schema = triangle_schema(callback)
    return verify_typed_physical_schema(
        callback,
        schema,
        target=target(),
        orientation_authorities={authority.authority_sha256: authority},
    )


class Goal5755TypedPhysicalSchemaTest(unittest.TestCase):
    def test_builtin_triangle_topology_is_geometry_indexed_not_legacy_backport(self):
        spec = parse_callback_source(
            TRIANGLE_SOURCE,
            manifest(),
            schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
        )
        with self.assertRaises(CallbackVerificationError):
            compile_callback_source(TRIANGLE_SOURCE, manifest())
        verified = verify_callback_program_for_geometry(spec, GeometryFamily.BUILTIN_TRIANGLE)
        roles = {item.role for item in verified.program.functions if item.role is not None}
        self.assertEqual(roles, {CallbackRole.MAKE_RAY, CallbackRole.CLOSEST_HIT, CallbackRole.MISS, CallbackRole.FINALIZE})

    def test_triangle_bounds_or_intersection_is_conflicting_authority(self):
        inserted = TRIANGLE_SOURCE.replace(
            "    @optix.make_ray",
            "    @optix.bounds\n    def bounds(query: Query) -> Aabb3f:\n        return optix.aabb(lower=query.origin, upper=query.origin)\n\n    @optix.make_ray",
        )
        with self.assertRaisesRegex(CallbackVerificationError, "forbidden_roles"):
            verify_callback_program_for_geometry(
                parse_callback_source(inserted, manifest(), schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION),
                GeometryFamily.BUILTIN_TRIANGLE,
            )

    def test_hit_metadata_arguments_must_be_read_only_views(self):
        attacked = TRIANGLE_SOURCE.replace("first_side: ReadOnlyView[u32]", "first_side: u32")
        with self.assertRaisesRegex(CallbackVerificationError, "role_signature|subscript_base"):
            verify_callback_program_for_geometry(
                parse_callback_source(attacked, manifest(), schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION),
                GeometryFamily.BUILTIN_TRIANGLE,
            )

    def test_inert_schema_roundtrip_is_closed_and_digest_checked(self):
        schema = triangle_schema()
        self.assertEqual(typed_physical_schema_from_dict(schema.to_dict()), schema)
        extra = dict(schema.to_dict()); extra["paper_name"] = "particle_tracking"
        with self.assertRaisesRegex(PhysicalSchemaError, "closed_shape"):
            typed_physical_schema_from_dict(extra)
        mutated = json.loads(json.dumps(schema.to_dict()))
        mutated["buffers"][0]["field_id"] = "changed"
        with self.assertRaisesRegex(PhysicalSchemaError, "schema_digest"):
            typed_physical_schema_from_dict(mutated)

    def test_serialized_schema_cannot_mint_orientation_authority(self):
        callback = verified_callback(); schema = triangle_schema(callback)
        with self.assertRaisesRegex(PhysicalSchemaError, "triangle_orientation_authority_missing"):
            verify_typed_physical_schema(callback, schema, target=target(), orientation_authorities={})

    def test_author_source_and_optix_front_back_mapping_are_exactly_bound(self):
        source = author_source_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), AUTHOR_SHA256)
        text = source.decode("utf-8").replace("\r\n", "\n")
        self.assertIn("const int   faceID = optixGetPrimitiveIndex();", text)
        self.assertIn("? self.tetForFace[faceID].front\n      : self.tetForFace[faceID].back;", text)
        self.assertIn("? self.tetForFace[faceID].back\n        : self.tetForFace[faceID].front;", text)
        authority = orientation_authority()
        self.assertEqual(resolve_triangle_adjacency(authority, hit_kind=FRONT_HIT_KIND, primitive_index=1, front_values=(7, 11), back_values=(9, 13)), (11, 13))
        self.assertEqual(resolve_triangle_adjacency(authority, hit_kind=BACK_HIT_KIND, primitive_index=1, front_values=(7, 11), back_values=(9, 13)), (13, 11))

    def test_author_mapping_is_differentially_checked_against_independent_cpu_oracle(self):
        spec = importlib.util.spec_from_file_location("goal5753_independent_oracle", ORACLE_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        vertices, cells = module.two_tetra_fixture()
        cell_zero_point = module.point(1, 1, 1)  # after division below, inside cell 0
        cell_zero_point = tuple(value / 10 for value in cell_zero_point)
        cell_one_point = tuple(sum(vertices[index][axis] for index in cells[1]) / 4 for axis in range(3))
        self.assertEqual(module.locate_cell(cell_zero_point, vertices, cells), 0)
        self.assertEqual(module.locate_cell(cell_one_point, vertices, cells), 1)
        selected, neighbor = resolve_triangle_adjacency(
            orientation_authority(), hit_kind=FRONT_HIT_KIND, primitive_index=0,
            front_values=(0,), back_values=(1,),
        )
        self.assertEqual((selected, neighbor), (0, 1))

    def test_names_do_not_substitute_for_semantic_authority(self):
        callback = verified_callback(); authority = orientation_authority(callback); schema = triangle_schema(callback)
        forged = dataclasses.replace(
            schema,
            buffers=tuple(
                dataclasses.replace(item, semantic=BufferSemantic.PRIMITIVE_BACK_VALUE)
                if item.semantic is BufferSemantic.PRIMITIVE_FRONT_VALUE else item
                for item in schema.buffers
            ),
        )
        with self.assertRaises(PhysicalSchemaError):
            verify_typed_physical_schema(callback, forged, target=target(), orientation_authorities={authority.authority_sha256: authority})

    def test_target_sdk_hit_kind_values_are_authoritative(self):
        callback = verified_callback(); authority = orientation_authority(callback); schema = triangle_schema(callback)
        with self.assertRaisesRegex(PhysicalSchemaError, "triangle_target_hit_kind"):
            verify_typed_physical_schema(
                callback, schema, target=target(triangle_front_hit_kind=1, triangle_back_hit_kind=2),
                orientation_authorities={authority.authority_sha256: authority},
            )

    def test_target_without_builtin_triangle_capability_fails_closed(self):
        callback = verified_callback(); authority = orientation_authority(callback); schema = triangle_schema(callback)
        with self.assertRaisesRegex(PhysicalSchemaError, "target_builtin_triangle"):
            verify_typed_physical_schema(
                callback, schema, target=target(supports_builtin_triangle=False),
                orientation_authorities={authority.authority_sha256: authority},
            )

    def test_hit_channel_storage_type_cannot_substitute_for_semantics(self):
        callback = verified_callback(); authority = orientation_authority(callback); schema = triangle_schema(callback)
        attacked = dataclasses.replace(
            schema,
            hit_channels=tuple(
                dataclasses.replace(item, value_type=PhysicalValueType.U32)
                if item.semantic is HitChannelSemantic.TRIANGLE_BARYCENTRICS else item
                for item in schema.hit_channels
            ),
        )
        with self.assertRaisesRegex(PhysicalSchemaError, "hit_channel_type"):
            verify_typed_physical_schema(
                callback, attacked, target=target(),
                orientation_authorities={authority.authority_sha256: authority},
            )

    def test_cpu_interpreter_executes_triangle_hit_and_primitive_metadata(self):
        callback = admitted().callback
        result = execute_callback_role(callback, CallbackRole.CLOSEST_HIT, {
            "hit": {"t": 0.25, "primitive_index": 1, "hit_kind": FRONT_HIT_KIND, "barycentrics": (0.2, 0.3)},
            "payload": {"cell_id": 99, "neighbor_id": 99, "face_id": 99},
            "first_side": (7, 11),
            "second_side": (9, 13),
        })
        payload = result.effect.field("payload")
        self.assertEqual((payload.field("cell_id"), payload.field("neighbor_id"), payload.field("face_id")), (11, 13, 1))

    def test_canonical_planner_emits_one_nonexecutable_reference_plan(self):
        plan = lower_canonical_reference_plan(admitted(), default_reference_templates())
        self.assertEqual(plan.template_id, ReferenceTemplateId.BUILTIN_TRIANGLE_V1)
        self.assertFalse(plan.executable)
        self.assertRegex(plan.plan_sha256, r"^[0-9a-f]{64}$")

    def test_zero_or_multiple_canonical_templates_fail_closed(self):
        authority = admitted()
        with self.assertRaisesRegex(PhysicalSchemaError, "unsupported_physical_schema"):
            lower_canonical_reference_plan(authority, ())
        template = default_reference_templates()[1]
        with self.assertRaisesRegex(PhysicalSchemaError, "ambiguous_canonical_template"):
            lower_canonical_reference_plan(authority, (template, dataclasses.replace(template)))

    def test_existing_custom_aabb_family_remains_a_separate_canonical_mapping(self):
        from tests.goal5750_v4_callback_ir_test import SOURCE as CUSTOM_SOURCE, manifest as custom_manifest

        callback = compile_callback_source(CUSTOM_SOURCE, custom_manifest())
        schema = TypedPhysicalSchemaV1(
            callback.ir_sha256,
            callback.effect_digest,
            GeometryFamily.CUSTOM_AABB,
            (
                BufferFieldSchema(
                    "primitives", BufferSemantic.CUSTOM_PRIMITIVE_DATA,
                    BufferDomain.PRIMITIVE, PhysicalValueType.OPAQUE_RECORD,
                    BufferAccess.READ_ONLY, CountRelation.PRIMITIVE_COUNT, 16,
                ),
            ),
            (
                HitChannelSchema(
                    HitChannelSemantic.CUSTOM_HIT_KIND, PhysicalValueType.U32,
                    HitChannelProducer.VERIFIED_INTERSECTION_EFFECT,
                    (CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT),
                ),
            ),
            (),
            GasSchema(
                GeometryFamily.CUSTOM_AABB,
                (BufferSemantic.CUSTOM_PRIMITIVE_DATA,),
                GasUpdatePolicy.STATIC,
                1,
                1,
            ),
        )
        authority = verify_typed_physical_schema(callback, schema, target=target())
        plan = lower_canonical_reference_plan(authority, default_reference_templates())
        self.assertEqual(plan.template_id, ReferenceTemplateId.CUSTOM_AABB_V1)
        self.assertFalse(plan.executable)

    def test_buffer_bindings_enforce_shared_owner_device_stream_counts_and_index_range(self):
        schema = triangle_schema()
        counts = {
            BufferSemantic.VERTEX_POSITIONS: (5, None, False),
            BufferSemantic.TRIANGLE_INDICES: (2, 4, False),
            BufferSemantic.PRIMITIVE_FRONT_VALUE: (2, None, False),
            BufferSemantic.PRIMITIVE_BACK_VALUE: (2, None, False),
            BufferSemantic.QUERY_INPUT: (3, None, False),
            BufferSemantic.OUTPUT_VALUE: (3, None, True),
            BufferSemantic.STATUS: (1, None, True),
        }
        bindings = tuple(PhysicalBufferBinding(
            item.semantic, counts[item.semantic][0], 0, 7, "owner", 4,
            item.alignment_bytes, True, counts[item.semantic][2], counts[item.semantic][1],
        ) for item in schema.buffers)
        verify_buffer_bindings(schema, bindings)
        attacked = list(bindings); attacked[2] = dataclasses.replace(attacked[2], element_count=1)
        with self.assertRaisesRegex(PhysicalSchemaError, "binding_count_relation"):
            verify_buffer_bindings(schema, attacked)
        attacked = list(bindings); attacked[1] = dataclasses.replace(attacked[1], maximum_index=5)
        with self.assertRaisesRegex(PhysicalSchemaError, "triangle_index_range"):
            verify_buffer_bindings(schema, attacked)

    def test_reference_triangle_content_checks_finite_range_and_target_f32_degeneracy(self):
        verify_reference_triangle_contents(((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((0, 1, 2),))
        for vertices, indices, code in (
            (((0, 0, 0), (1, 0, 0), (float("nan"), 1, 0)), ((0, 1, 2),), "nonfinite_f32"),
            (((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((0, 1, 3),), "triangle_index"),
            (((0, 0, 0), (1, 0, 0), (2, 0, 0)), ((0, 1, 2),), "triangle_degenerate_f32"),
        ):
            with self.assertRaisesRegex(PhysicalSchemaError, code):
                verify_reference_triangle_contents(vertices, indices)

    def test_goal5753_failed_exam_artifacts_are_consumed_not_relabelled(self):
        result = json.loads((ROOT / "history/internal_docs/goal5753_held_out_particle_tracking_exam_result_20260811.json").read_text(encoding="utf-8"))
        self.assertIn("failed", json.dumps(result).lower())
        self.assertEqual(hashlib.sha256(author_source_bytes()).hexdigest(), AUTHOR_SHA256)

    def test_product_module_has_no_app_paper_dataset_or_native_execution_dispatch(self):
        source = (ROOT / "src/rtdsl/v4_typed_physical_schema.py").read_text(encoding="utf-8").lower()
        for forbidden in ("particle_tracking", "goal5753", "paper-reproduction", "ctypes", "optixlaunch", "culaunchkernel"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
