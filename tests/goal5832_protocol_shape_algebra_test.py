from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from goal5832_protocol_shape_algebra import (  # noqa: E402
    AlgebraError,
    domain_digest,
    identity,
    load_json_exact,
    same_family_shape,
    validate_deployment,
    validate_family_shape,
    validate_instance_against_shape,
    validate_protocol_instance,
    validate_scope_authority,
)


AUTHORITY = (
    ROOT / "history/internal_docs/"
    "goal5832_protocol_shape_algebra_authority_v1_20260830.json"
)


def _shape(prefix: str = "author") -> dict[str, object]:
    return {
        "schema": "rtdl.family_shape.v1",
        "parameters": [
            {"parameter_id": f"{prefix}_capacity", "type": "u32"},
        ],
        "graph_nodes": [
            {"node_id": f"{prefix}_gas", "kind": "gas",
             "primitive_kind": "custom_primitive", "ordinal": 0,
             "update_policy": "static", "sbt_record_stride": 1,
             "children": []},
        ],
        "buffers": [
            {"buffer_id": f"{prefix}_items", "ordinal": 0,
             "semantic": "application.primitive.item_id",
             "domain": "primitive", "value_type": "u32",
             "access": "read_only", "count_relation": "primitive_count",
             "alignment_bytes": 4, "contiguous": True,
             "residency": "device"},
        ],
        "channels": [
            {"channel_id": f"{prefix}_attr0", "ordinal": 0,
             "semantic": "application.item_id", "value_type": "u32",
             "producer": {"kind": "verified_effect",
                          "role": "intersection", "effect": "hit"},
             "ownership": "application.item_id",
             "consumers": [{"role": "closest_hit", "argument_index": 0}]},
        ],
        "views": [
            {"role": "closest_hit", "argument_index": 2,
             "source": {"kind": "buffer_lookup",
                        "buffer_ref": f"{prefix}_items",
                        "index_channel_ref": f"{prefix}_attr0"}},
        ],
        "events": [
            {"event_id": f"{prefix}_row", "ordinal": 0,
             "value_type": "u32x2", "source": "ir_output"},
        ],
        "callback": {
            "roles": [
                {"role": "intersection", "cardinality": "exactly_one",
                 "allowed_effects": ["no_hit", "hit"],
                 "required_effects": ["hit"]},
                {"role": "closest_hit", "cardinality": "exactly_one",
                 "allowed_effects": ["payload"],
                 "required_effects": ["payload"]},
                {"role": "finalize", "cardinality": "exactly_one",
                 "allowed_effects": ["output"],
                 "required_effects": ["output"]},
            ],
        },
        "physical": {
            "root": {"node_ref": f"{prefix}_gas"},
            "metadata_bindings": [
                {"role": "closest_hit", "argument_index": 2,
                 "buffer_ref": f"{prefix}_items",
                 "index_channel_ref": f"{prefix}_attr0"},
            ],
            "channel_bindings": [
                {"channel_ref": f"{prefix}_attr0",
                 "producer_role": "intersection"},
            ],
            "sbt": {"record_stride": 1,
                    "record_count_relation": "primitive_count",
                    "ray_type_count": 1},
        },
        "result_pipeline": [
            {"operator": "emit_record", "event_ref": f"{prefix}_row"},
            {"operator": "capacity_guard",
             "parameter_ref": f"{prefix}_capacity"},
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
                {"from_state": f"{prefix}_prepared",
                 "event": "launch",
                 "to_state": f"{prefix}_launched"},
                {"from_state": f"{prefix}_launched",
                 "event": "observe_status_ok",
                 "to_state": f"{prefix}_status_ok"},
                {"from_state": f"{prefix}_launched",
                 "event": "observe_status_failure",
                 "to_state": f"{prefix}_status_failed"},
                {"from_state": f"{prefix}_status_ok",
                 "event": "copy_output",
                 "to_state": f"{prefix}_committed"},
            ],
            "terminal_states": [f"{prefix}_committed", f"{prefix}_status_failed"],
            "invariants": ["copy_output_requires_status_ok",
                           "status_failure_forbids_output_copy"],
        },
        "capabilities": ["optix", "custom_primitive"],
        "identity_bind_set": ["actual_executable", "callback_ir"],
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


def _instance(shape_id: str, nominal: str = "application.item_id") -> dict[str, object]:
    return {
        "schema": "rtdl.protocol_instance.v1",
        "family_shape_sha256": shape_id,
        "parameter_values": [
            {"parameter_ref": "p0", "value_type": "u32", "value": 16},
        ],
        "nominal_semantics": {"attr0": nominal},
        "callback_source_sha256": "0" * 64,
        "callback_ir_sha256": "1" * 64,
        "effect_digest": "2" * 64,
        "abi_sha256": "3" * 64,
        "authorities": [
            {"authority_kind": "geometry", "authority_sha256": "4" * 64},
            {"authority_kind": "orientation", "authority_sha256": "5" * 64},
        ],
    }


def _deployment(instance_id: str, target_digit: str = "6") -> dict[str, object]:
    return {
        "schema": "rtdl.protocol_deployment.v1",
        "protocol_instance_sha256": instance_id,
        "target_profile_sha256": target_digit * 64,
        "physical_schema_sha256": "7" * 64,
        "provider": {
            "provider_id": "optix",
            "provider_version": "9.0",
            "provider_binary_sha256": "8" * 64,
            "generated_device_source_sha256": "9" * 64,
            "generated_host_source_sha256": "a" * 64,
        },
        "actual_executable_sha256": "b" * 64,
    }


class ProtocolShapeAlgebraTest(unittest.TestCase):
    def test_authority_matches_repository(self) -> None:
        authority = load_json_exact(AUTHORITY)
        validate_scope_authority(authority, ROOT)

    def test_authority_count_mutation_fails(self) -> None:
        authority = load_json_exact(AUTHORITY)
        authority["current_counts"]["fixed_protocol_constructors"] = 3
        with self.assertRaisesRegex(AlgebraError, "count ledger"):
            validate_scope_authority(authority, ROOT)

    def test_authority_overclaim_mutation_fails(self) -> None:
        authority = load_json_exact(AUTHORITY)
        authority["implementation_status"] = "FAMILY_PARAMETRIC_GPU_COMPILER_IMPLEMENTED"
        authority["claim_ceiling"]["supported_claims"].append(
            "family_parametric_gpu_compiler_implemented")
        with self.assertRaises(AlgebraError):
            validate_scope_authority(authority, ROOT)

    def test_authority_support_matrix_promotion_fails(self) -> None:
        authority = load_json_exact(AUTHORITY)
        curve = next(row for row in authority["support_matrix"]
                     if row["feature"] == "curves_leaf_primitive")
        curve.update({
            "verifier": "SUPPORTED",
            "provider_codegen": "SUPPORTED",
            "public_lifecycle": "SUPPORTED",
            "true_gpu_evidence": "SUPPORTED",
        })
        with self.assertRaises(AlgebraError):
            validate_scope_authority(authority, ROOT)

    def test_duplicate_json_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"schema":"a","schema":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(AlgebraError, "duplicate JSON key"):
                load_json_exact(path)

    def test_alpha_renaming_and_set_order_preserve_shape(self) -> None:
        left = _shape("left")
        right = _shape("right")
        right["capabilities"] = list(reversed(right["capabilities"]))
        right["identity_bind_set"] = list(reversed(right["identity_bind_set"]))
        right["callback"]["roles"][0]["allowed_effects"] = ["hit", "no_hit"]
        self.assertTrue(same_family_shape(left, right))
        self.assertEqual(identity("family_shape", left), identity("family_shape", right))

    def test_order_bearing_role_change_changes_shape(self) -> None:
        left = _shape()
        right = copy.deepcopy(left)
        right["callback"]["roles"].reverse()
        self.assertFalse(same_family_shape(left, right))

    def test_channel_ownership_change_changes_shape(self) -> None:
        left = _shape()
        right = copy.deepcopy(left)
        right["channels"][0]["ownership"] = "primitive_position"
        self.assertFalse(same_family_shape(left, right))

    def test_result_operator_order_changes_shape(self) -> None:
        left = _shape()
        right = copy.deepcopy(left)
        right["result_pipeline"][0], right["result_pipeline"][1] = (
            right["result_pipeline"][1], right["result_pipeline"][0])
        self.assertFalse(same_family_shape(left, right))

    def test_dangling_reference_rejected(self) -> None:
        shape = _shape()
        shape["physical"]["root"]["node_ref"] = "not_declared"
        with self.assertRaisesRegex(AlgebraError, "dangling local reference"):
            identity("family_shape", shape)

    def test_nominal_semantic_change_is_instance_not_shape_change(self) -> None:
        shape = _shape()
        shape_id = identity("family_shape", shape)
        left = _instance(shape_id)
        right = _instance(shape_id, "optix.primitive_index")
        validate_instance_against_shape(left, shape)
        self.assertNotEqual(
            identity("protocol_instance", left),
            identity("protocol_instance", right),
        )

    def test_target_change_is_deployment_not_instance_change(self) -> None:
        instance = _instance(identity("family_shape", _shape()))
        instance_id = identity("protocol_instance", instance)
        left = _deployment(instance_id, "6")
        right = _deployment(instance_id, "c")
        self.assertEqual(identity("protocol_instance", instance), instance_id)
        self.assertNotEqual(identity("deployment", left), identity("deployment", right))

    def test_identity_domains_are_separated(self) -> None:
        value = {"x": "same canonical bytes"}
        digests = {domain_digest(name, value) for name in (
            "family_shape", "protocol_instance", "deployment")}
        self.assertEqual(len(digests), 3)

    def test_json_float_rejected_from_normative_identity(self) -> None:
        shape = _shape()
        shape["resource_limits"]["epsilon"] = 0.5
        with self.assertRaisesRegex(AlgebraError, "floating JSON number forbidden"):
            identity("family_shape", shape)

    def test_all_three_schema_only_documents_rejected(self) -> None:
        for domain, schema in (
            ("family_shape", "rtdl.family_shape.v1"),
            ("protocol_instance", "rtdl.protocol_instance.v1"),
            ("deployment", "rtdl.protocol_deployment.v1"),
        ):
            with self.subTest(domain=domain):
                with self.assertRaisesRegex(AlgebraError, "missing keys"):
                    identity(domain, {"schema": schema})

    def test_unknown_root_and_nested_keys_rejected(self) -> None:
        shape = _shape()
        shape["junk"] = {}
        with self.assertRaisesRegex(AlgebraError, "unknown keys"):
            validate_family_shape(shape)
        shape = _shape()
        shape["callback"]["junk"] = 1
        with self.assertRaisesRegex(AlgebraError, "unknown keys"):
            validate_family_shape(shape)

    def test_bool_cannot_alias_integer(self) -> None:
        for path in ("ordinal", "max_trace_depth"):
            shape = _shape()
            if path == "ordinal":
                shape["graph_nodes"][0][path] = True
            else:
                shape["resource_limits"][path] = True
            with self.subTest(path=path):
                with self.assertRaisesRegex(AlgebraError, "not bool"):
                    validate_family_shape(shape)
        instance = _instance(identity("family_shape", _shape()))
        instance["parameter_values"][0]["value"] = True
        with self.assertRaisesRegex(AlgebraError, "not bool"):
            validate_protocol_instance(instance)

    def test_role_effect_contract_is_typed(self) -> None:
        shape = _shape()
        shape["callback"]["roles"][0]["role"] = "banana"
        with self.assertRaisesRegex(AlgebraError, "role unsupported"):
            validate_family_shape(shape)
        shape = _shape()
        shape["callback"]["roles"][0]["allowed_effects"] = ["rm_rf"]
        with self.assertRaisesRegex(AlgebraError, "unsupported values"):
            validate_family_shape(shape)
        shape = _shape()
        shape["callback"]["roles"][2]["allowed_effects"] = ["output"]
        shape["callback"]["roles"][2]["required_effects"] = ["payload"]
        with self.assertRaises(AlgebraError):
            validate_family_shape(shape)

    def test_duplicate_binder_and_bad_ordinal_rejected(self) -> None:
        shape = _shape()
        shape["parameters"].append(copy.deepcopy(shape["parameters"][0]))
        with self.assertRaisesRegex(AlgebraError, "duplicate local binder"):
            identity("family_shape", shape)
        shape = _shape()
        shape["buffers"][0]["ordinal"] = 1
        with self.assertRaisesRegex(AlgebraError, "ordinals"):
            validate_family_shape(shape)

    def test_result_operator_union_and_commit_are_enforced(self) -> None:
        shape = _shape()
        shape["result_pipeline"][0]["operator"] = "unknown"
        with self.assertRaisesRegex(AlgebraError, "operator unsupported"):
            validate_family_shape(shape)
        shape = _shape()
        shape["result_pipeline"][0]["parameter_ref"] = "author_capacity"
        with self.assertRaisesRegex(AlgebraError, "unknown keys"):
            validate_family_shape(shape)
        shape = _shape()
        shape["result_pipeline"].pop()
        with self.assertRaisesRegex(AlgebraError, "output commit"):
            validate_family_shape(shape)

    def test_status_before_output_automaton_is_enforced(self) -> None:
        shape = _shape()
        copy_transition = shape["continuation"]["transitions"][-1]
        copy_transition["from_state"] = "author_launched"
        with self.assertRaisesRegex(AlgebraError, "status_ok"):
            validate_family_shape(shape)
        shape = _shape()
        failure_transition = shape["continuation"]["transitions"][2]
        failure_transition["to_state"] = "author_committed"
        with self.assertRaisesRegex(AlgebraError, "status_failed"):
            validate_family_shape(shape)

    def test_instance_typed_binding_and_authority_set(self) -> None:
        shape = _shape()
        instance = _instance(identity("family_shape", shape))
        validate_instance_against_shape(instance, shape)
        reversed_authorities = copy.deepcopy(instance)
        reversed_authorities["authorities"].reverse()
        self.assertEqual(identity("protocol_instance", instance),
                         identity("protocol_instance", reversed_authorities))
        bad = copy.deepcopy(instance)
        bad["parameter_values"][0]["value_type"] = "u64"
        with self.assertRaisesRegex(AlgebraError, "typed parameter binding"):
            validate_instance_against_shape(bad, shape)
        bad = copy.deepcopy(instance)
        bad["authorities"].append(copy.deepcopy(bad["authorities"][0]))
        with self.assertRaisesRegex(AlgebraError, "duplicates"):
            validate_protocol_instance(bad)

    def test_instance_and_deployment_exact_digest_fields(self) -> None:
        instance = _instance(identity("family_shape", _shape()))
        instance["abi_sha256"] = "A" * 64
        with self.assertRaisesRegex(AlgebraError, "lowercase SHA-256"):
            validate_protocol_instance(instance)
        deployment = _deployment("1" * 64)
        deployment["target"] = "sm_89"
        with self.assertRaisesRegex(AlgebraError, "unknown keys"):
            validate_deployment(deployment)
        deployment = _deployment("1" * 64)
        del deployment["provider"]["provider_binary_sha256"]
        with self.assertRaisesRegex(AlgebraError, "missing keys"):
            validate_deployment(deployment)


if __name__ == "__main__":
    unittest.main()
