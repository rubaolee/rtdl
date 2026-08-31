from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from goal5832_protocol_shape_algebra import identity as goal5832_identity  # noqa: E402
from rtdsl.v4_family_schema import (  # noqa: E402
    CanonicalFamilyCompilationPlan,
    FamilySchemaError,
    FamilySchemaV1,
    ProtocolInstanceV1,
    admit_family_schema,
    lower_canonical_compilation_plan,
    reverify_canonical_compilation_plan,
    reverify_family_admission,
)


def _shape(prefix: str = "author") -> dict[str, object]:
    return {
        "schema": "rtdl.family_shape.v1",
        "parameters": [
            {"parameter_id": f"{prefix}_capacity", "type": "u32", "minimum": 1},
        ],
        "graph_nodes": [
            {
                "node_id": f"{prefix}_gas",
                "kind": "gas",
                "primitive_kind": "custom_primitive",
                "ordinal": 0,
                "update_policy": "static",
                "sbt_record_stride": 1,
                "children": [],
            },
        ],
        "buffers": [
            {
                "buffer_id": f"{prefix}_items",
                "ordinal": 0,
                "semantic": "application.primitive.item_id",
                "domain": "primitive",
                "value_type": "u32",
                "access": "read_only",
                "count_relation": "primitive_count",
                "alignment_bytes": 4,
                "contiguous": True,
                "residency": "device",
            },
            {
                "buffer_id": f"{prefix}_result",
                "ordinal": 1,
                "semantic": "application.result.row",
                "domain": "result",
                "value_type": "u32x2",
                "access": "write_only",
                "count_relation": "query_count",
                "alignment_bytes": 8,
                "contiguous": True,
                "residency": "device",
            },
        ],
        "channels": [
            {
                "channel_id": f"{prefix}_attr0",
                "ordinal": 0,
                "semantic": "application.item_id",
                "value_type": "u32",
                "producer": {
                    "kind": "verified_effect",
                    "role": "intersection",
                    "effect": "hit",
                },
                "ownership": "application.item_id",
                "consumers": [{"role": "closest_hit", "argument_index": 0}],
            },
        ],
        "views": [
            {
                "role": "closest_hit",
                "argument_index": 2,
                "source": {
                    "kind": "buffer_lookup",
                    "buffer_ref": f"{prefix}_items",
                    "index_channel_ref": f"{prefix}_attr0",
                },
            },
        ],
        "events": [
            {
                "event_id": f"{prefix}_row",
                "ordinal": 0,
                "value_type": "u32x2",
                "source": "ir_output",
            },
        ],
        "callback": {
            "roles": [
                {
                    "role": "intersection",
                    "cardinality": "exactly_one",
                    "allowed_effects": ["no_hit", "hit"],
                    "required_effects": ["hit"],
                },
                {
                    "role": "closest_hit",
                    "cardinality": "exactly_one",
                    "allowed_effects": ["payload"],
                    "required_effects": ["payload"],
                },
                {
                    "role": "finalize",
                    "cardinality": "exactly_one",
                    "allowed_effects": ["output"],
                    "required_effects": ["output"],
                },
            ],
        },
        "physical": {
            "root": {"node_ref": f"{prefix}_gas"},
            "metadata_bindings": [
                {
                    "role": "closest_hit",
                    "argument_index": 2,
                    "buffer_ref": f"{prefix}_items",
                    "index_channel_ref": f"{prefix}_attr0",
                },
            ],
            "channel_bindings": [
                {
                    "channel_ref": f"{prefix}_attr0",
                    "producer_role": "intersection",
                },
            ],
            "sbt": {
                "record_stride": 1,
                "record_count_relation": "primitive_count",
                "ray_type_count": 1,
            },
        },
        "result_pipeline": [
            {"operator": "emit_record", "event_ref": f"{prefix}_row"},
            {"operator": "capacity_guard", "parameter_ref": f"{prefix}_capacity"},
            {"operator": "commit_collected_rows"},
        ],
        "continuation": {
            "initial_state": f"{prefix}_prepared",
            "states": [
                {"state_id": f"{prefix}_prepared", "kind": "prepared"},
                {"state_id": f"{prefix}_launched", "kind": "launched"},
                {"state_id": f"{prefix}_status_ok", "kind": "status_ok"},
                {"state_id": f"{prefix}_status_failed", "kind": "status_failed"},
                {"state_id": f"{prefix}_committed", "kind": "committed"},
            ],
            "transitions": [
                {
                    "from_state": f"{prefix}_prepared",
                    "event": "launch",
                    "to_state": f"{prefix}_launched",
                },
                {
                    "from_state": f"{prefix}_launched",
                    "event": "observe_status_ok",
                    "to_state": f"{prefix}_status_ok",
                },
                {
                    "from_state": f"{prefix}_launched",
                    "event": "observe_status_failure",
                    "to_state": f"{prefix}_status_failed",
                },
                {
                    "from_state": f"{prefix}_status_ok",
                    "event": "copy_output",
                    "to_state": f"{prefix}_committed",
                },
            ],
            "terminal_states": [f"{prefix}_status_failed", f"{prefix}_committed"],
            "invariants": [
                "copy_output_requires_status_ok",
                "status_failure_forbids_output_copy",
            ],
        },
        "capabilities": ["callback_ir", "external.test_leaf"],
        "identity_bind_set": ["callback_ir", "actual_executable"],
        "resource_limits": {
            "max_payload_u32_slots": 8,
            "max_attribute_u32_slots": 2,
            "max_trace_depth": 1,
            "max_callable_depth": 0,
            "max_static_loop_trip_count": 1024,
            "max_total_static_iterations": 4096,
            "max_helper_call_depth": 8,
        },
    }


def _instance(shape_sha256: str, digit: str = "0") -> dict[str, object]:
    return {
        "schema": "rtdl.protocol_instance.v1",
        "family_shape_sha256": shape_sha256,
        "parameter_values": [
            {"parameter_ref": "p0", "value_type": "u32", "value": 16},
        ],
        "nominal_semantics": {"attr0": "application.item_id"},
        "callback_source_sha256": digit * 64,
        "callback_ir_sha256": "1" * 64,
        "effect_digest": "2" * 64,
        "abi_sha256": "3" * 64,
        "authorities": [
            {"authority_kind": "geometry", "authority_sha256": "4" * 64},
            {"authority_kind": "orientation", "authority_sha256": "5" * 64},
        ],
    }


def _plan(
    shape: dict[str, object] | None = None,
    *,
    behavior: str = "a" * 64,
    template: str = "external.test_template.v1",
) -> CanonicalFamilyCompilationPlan:
    schema = FamilySchemaV1(_shape() if shape is None else shape)
    instance = ProtocolInstanceV1(_instance(schema.family_shape_sha256))
    admission = admit_family_schema(
        schema,
        instance,
        behavior_schema_sha256=behavior,
        canonical_template_id=template,
    )
    return lower_canonical_compilation_plan(admission)


def _all_keys(value: object) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        result.update(value)
        for item in value.values():
            result.update(_all_keys(item))
    elif isinstance(value, list):
        for item in value:
            result.update(_all_keys(item))
    return result


class Goal5833FamilySchemaCompilationPlanTest(unittest.TestCase):
    def test_family_identity_matches_goal5832_authority_algorithm(self) -> None:
        raw = _shape()
        self.assertEqual(
            FamilySchemaV1(raw).family_shape_sha256,
            goal5832_identity("family_shape", raw),
        )

    def test_alpha_renamed_shape_is_identical(self) -> None:
        left = FamilySchemaV1(_shape("left"))
        right = FamilySchemaV1(_shape("right"))
        self.assertEqual(left.canonical_bytes, right.canonical_bytes)
        self.assertEqual(left.family_shape_sha256, right.family_shape_sha256)

    def test_generic_core_contains_no_concrete_family_dispatch(self) -> None:
        source = (ROOT / "src/rtdsl/v4_family_schema.py").read_text("utf-8").lower()
        for forbidden in (
            "builtin_triangle",
            "custom_aabb",
            "bounded_relation",
            "triangle_reduction",
            "sphere",
            "curve",
        ):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("geometryfamily", source.replace("_", ""))

    def test_schema_and_plan_are_target_and_deployment_neutral(self) -> None:
        plan = _plan()
        keys = _all_keys(plan.to_dict())
        self.assertTrue({
            "family_shape_sha256",
            "protocol_instance_sha256",
            "callback_ir_sha256",
            "effect_digest",
            "abi_sha256",
            "behavior_schema_sha256",
            "canonical_template_id",
        } <= keys)
        self.assertTrue({
            "provider",
            "target",
            "target_sha256",
            "native",
            "ptx",
            "sdk",
            "compute_capability",
            "authority_nonce",
        }.isdisjoint(keys))
        self.assertFalse(plan.to_dict()["executable"])

    def test_plan_is_deterministic_and_reverifiable(self) -> None:
        first = _plan()
        second = _plan()
        self.assertEqual(first.canonical_bytes, second.canonical_bytes)
        self.assertEqual(first.plan_sha256, second.plan_sha256)
        self.assertEqual(
            reverify_canonical_compilation_plan(first).plan_sha256,
            first.plan_sha256,
        )

    def test_all_instance_program_identities_change_the_plan(self) -> None:
        schema = FamilySchemaV1(_shape())
        baseline = _instance(schema.family_shape_sha256)
        leaves = (
            "callback_source_sha256",
            "callback_ir_sha256",
            "effect_digest",
            "abi_sha256",
        )
        digests: set[str] = set()
        for index, leaf in enumerate(leaves, start=6):
            mutated = copy.deepcopy(baseline)
            mutated[leaf] = format(index, "x") * 64
            instance = ProtocolInstanceV1(mutated)
            admission = admit_family_schema(
                schema,
                instance,
                behavior_schema_sha256="a" * 64,
                canonical_template_id="external.test_template.v1",
            )
            digests.add(lower_canonical_compilation_plan(admission).plan_sha256)
        self.assertEqual(len(digests), len(leaves))

    def test_behavior_template_role_and_family_mutations_change_the_plan(self) -> None:
        baseline = _plan()
        changed_behavior = _plan(behavior="b" * 64)
        changed_template = _plan(template="external.other_template.v1")
        changed_shape = _shape()
        changed_shape["callback"]["roles"][0]["required_effects"] = []  # type: ignore[index]
        changed_role = _plan(changed_shape)
        self.assertEqual(
            4,
            len({
                baseline.plan_sha256,
                changed_behavior.plan_sha256,
                changed_template.plan_sha256,
                changed_role.plan_sha256,
            }),
        )

    def test_cross_family_instance_swap_fails_before_plan(self) -> None:
        first = FamilySchemaV1(_shape("first"))
        changed = _shape("second")
        changed["graph_nodes"][0]["primitive_kind"] = "builtin_sphere"  # type: ignore[index]
        second = FamilySchemaV1(changed)
        instance = ProtocolInstanceV1(_instance(first.family_shape_sha256))
        with self.assertRaisesRegex(FamilySchemaError, "FS042_SHAPE_BINDING"):
            admit_family_schema(
                second,
                instance,
                behavior_schema_sha256="a" * 64,
                canonical_template_id="external.test_template.v1",
            )

    def test_authority_order_is_set_like(self) -> None:
        schema = FamilySchemaV1(_shape())
        left = _instance(schema.family_shape_sha256)
        right = copy.deepcopy(left)
        right["authorities"].reverse()  # type: ignore[union-attr]
        self.assertEqual(
            ProtocolInstanceV1(left).protocol_instance_sha256,
            ProtocolInstanceV1(right).protocol_instance_sha256,
        )

    def test_parameter_bool_alias_and_out_of_range_fail(self) -> None:
        schema = FamilySchemaV1(_shape())
        for value in (True, 0):
            instance = _instance(schema.family_shape_sha256)
            instance["parameter_values"][0]["value"] = value  # type: ignore[index]
            with self.assertRaises(FamilySchemaError):
                admit_family_schema(
                    schema,
                    instance,
                    behavior_schema_sha256="a" * 64,
                    canonical_template_id="external.test_template.v1",
                )

    def test_dangling_duplicate_unknown_and_float_fail(self) -> None:
        attacks = []
        dangling = _shape()
        dangling["physical"]["root"]["node_ref"] = "missing"  # type: ignore[index]
        attacks.append(dangling)
        duplicate = _shape()
        duplicate["buffers"][1]["buffer_id"] = duplicate["buffers"][0]["buffer_id"]  # type: ignore[index]
        attacks.append(duplicate)
        unknown = _shape()
        unknown["target"] = {"provider": "forbidden"}
        attacks.append(unknown)
        floating = _shape()
        floating["buffers"][0]["alignment_bytes"] = 4.0  # type: ignore[index]
        attacks.append(floating)
        for attack in attacks:
            with self.assertRaises(FamilySchemaError):
                FamilySchemaV1(attack)

    def test_executable_plan_request_is_rejected(self) -> None:
        schema = FamilySchemaV1(_shape())
        instance = ProtocolInstanceV1(_instance(schema.family_shape_sha256))
        for value in (True, 1):
            with self.assertRaisesRegex(FamilySchemaError, "FS044_EXECUTABLE_FORBIDDEN"):
                admit_family_schema(
                    schema,
                    instance,
                    behavior_schema_sha256="a" * 64,
                    canonical_template_id="external.test_template.v1",
                    executable=value,  # type: ignore[arg-type]
                )

    def test_readonly_documents_and_object_drift_are_detected(self) -> None:
        plan = _plan()
        with self.assertRaises(TypeError):
            plan.document["executable"] = True  # type: ignore[index]
        object.__setattr__(plan, "_canonical_document", plan.canonical_bytes + b" ")
        with self.assertRaisesRegex(FamilySchemaError, "FS050_PLAN_DRIFT"):
            reverify_canonical_compilation_plan(plan)

    def test_admission_drift_is_detected(self) -> None:
        plan = _plan()
        admission = plan.admission
        object.__setattr__(admission, "_canonical_document", admission.canonical_bytes + b" ")
        with self.assertRaisesRegex(FamilySchemaError, "FS049_ADMISSION_DRIFT"):
            reverify_family_admission(admission)


if __name__ == "__main__":
    unittest.main()
