from __future__ import annotations

import copy
import hashlib
import json
from types import SimpleNamespace
import unittest

from rtdsl.v4_callback_lifecycle import (
    AnyHitProtocolProof,
    BoundedRelationProtocol,
    TriangleReductionMode,
    TriangleReductionProtocol,
    standard_protocol_physical_plan,
)
from rtdsl.v4_family_route_adapters import (
    bounded_relation_family_route,
    triangle_reduction_family_route,
)
from rtdsl.v4_sphere_any_hit_count_family_route import (
    sphere_any_hit_count_family_route,
)
from rtdsl.v4_target_control_flow_evidence import (
    capture_target_control_flow_evidence,
)
from rtdsl.v4_target_evidence_bundle import (
    TargetEvidenceBundleError,
    build_family_target_declaration,
    build_target_evidence_bundle,
    capture_generated_target_artifacts,
    make_blob_record,
    registered_operator_contracts,
    validate_target_evidence_bundle,
)


ROUTE_ID = "stable::triangle_reduction::checked_u64_reduction"


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")).hexdigest()


def _proof(protocol: object, label: str) -> AnyHitProtocolProof:
    plan = standard_protocol_physical_plan(protocol)
    return AnyHitProtocolProof(
        plan.callback_ir_sha256,
        plan.effect_digest,
        _sha(label),
        "external_machine_checked_order_independence_v1",
    )


def _plan() -> SimpleNamespace:
    contract = registered_operator_contracts(ROUTE_ID)[0]
    document = {
        "schema": "rtdl.family_compilation_plan.v1",
        "callback_ir_sha256": _sha("ir"),
        "abi_sha256": _sha("abi"),
        "family_shape": {
            "callback": {"roles": [{
                "role": "any_hit",
                "allowed_effects": ["accept_continue"],
                "required_effects": ["accept_continue"],
                "cardinality": "exactly_one",
            }]},
            "graph_nodes": [{"primitive_kind": "builtin_triangle"}],
            "result_pipeline": [{
                "operator_id": contract["operator_id"],
                "operator_contract_sha256": _digest(contract),
            }],
        },
        "protocol_instance": {
            "nominal_semantics": {"output": "result.checked_u64"},
            "parameter_values": [{
                "parameter_ref": "p0",
                "value_type": "namespaced_identifier",
                "value": "checked_u64_sum",
            }],
        },
    }
    return SimpleNamespace(to_dict=lambda: document, plan_sha256=_sha("plan"))


def _bundle() -> dict[str, object]:
    declaration = build_family_target_declaration(ROUTE_ID, _plan())
    leaf_source = "def leaf(out_effect_tag):\n    out_effect_tag[0] = 5\n"
    leaf_ptx = ".version 8.0\n.target sm_89\n.address_size 64\n.func leaf() {}\n"
    wrapper_source = "extern leaf; optixGetPrimitiveIndex(); status; output;"
    wrapper_ptx = ".version 8.0\n.target sm_89\n.address_size 64\n.entry raygen() {}\n"
    composed_ptx = wrapper_ptx + leaf_ptx
    wrapper_source_sha = hashlib.sha256(wrapper_source.encode()).hexdigest()
    wrapper_ptx_sha = hashlib.sha256(wrapper_ptx.encode()).hexdigest()
    leaf_source_sha = hashlib.sha256(leaf_source.encode()).hexdigest()
    leaf_ptx_sha = hashlib.sha256(leaf_ptx.encode()).hexdigest()
    composed_ptx_sha = hashlib.sha256(composed_ptx.encode()).hexdigest()
    identity_preimage = {
        "schema": "rtdl.v4.verified_triangle_reduction_executable.v1",
        "authority": _sha("authority"),
        "contract": _sha("contract"),
        "abi": _sha("abi"),
        "wrapper_source": wrapper_source_sha,
        "wrapper_ptx": wrapper_ptx_sha,
        "generated": [leaf_source_sha],
        "compiled": [leaf_ptx_sha],
        "composed": composed_ptx_sha,
        "options": ["--gpu-architecture=compute_89"],
        "nvrtc_log": _sha("nvrtc-log"),
    }
    generated = {
        "wrapper": {
            "metadata": {
                "source_sha256": wrapper_source_sha,
                "role_symbols": [["any_hit", "leaf"]],
            },
            "source": make_blob_record(wrapper_source),
            "ptx": make_blob_record(wrapper_ptx),
        },
        "leaves": [{
            "role": "any_hit",
            "generated_metadata": {
                "role": "any_hit",
                "abi_name": "leaf",
                "generated_source_sha256": leaf_source_sha,
            },
            "generated_source": make_blob_record(leaf_source),
            "compiled_metadata": {
                "role": "any_hit",
                "abi_name": "leaf",
                "ptx_sha256": leaf_ptx_sha,
            },
            "compiled_ptx": make_blob_record(leaf_ptx),
        }],
        "composed_ptx": make_blob_record(composed_ptx),
        "executable_metadata": {
            "schema": "rtdl.v4.verified_triangle_reduction_executable.v1",
            "executable_sha256": _digest(identity_preimage),
            "composed_ptx_sha256": composed_ptx_sha,
            "composition": {
                "schema": "rtdl.v4.composed_callback_ptx_evidence.v1",
                "mode": "linked_leaf_ptx",
                "ptx_version": "8.0",
                "ptx_target": "sm_89",
                "address_size": "64",
                "wrapper_ptx_sha256": wrapper_ptx_sha,
                "leaf_order": ["any_hit"],
                "leaf_bindings": [{"role": "any_hit", "symbol": "leaf"}],
                "stripped_wrapper_externs": ["leaf"],
                "stripped_numba_environments": [],
            },
            "identity_preimage": identity_preimage,
        },
    }
    abi = {
        "abi_sha256": _sha("abi"),
        "callback_ir_sha256": _sha("ir"),
        "roles": [],
    }
    control_flow = capture_target_control_flow_evidence(ROUTE_ID)
    output_sha = _sha("output")
    native_sha = _sha("native")
    return build_target_evidence_bundle(
        route_id=ROUTE_ID,
        declaration=declaration,
        declaration_authority_sha256=_sha("declaration-authority"),
        program_artifacts=[{
            "artifact_id": "rtdl.callback.abi",
            "format_id": "rtdl.callback_abi.canonical_json.v1",
            "payload": make_blob_record(json.dumps(abi, sort_keys=True)),
        }],
        generated_target_artifacts=generated,
        provider_descriptor={"descriptor_sha256": _sha("provider")},
        provider_projection={"projection_sha256": _sha("projection")},
        executable_identity={
            "generated_artifact_sha256": generated["executable_metadata"]["composed_ptx_sha256"],
        },
        target_binding={"target_sha256": _sha("target")},
        native_producer_descriptor={"primitive_kind": "builtin_triangle"},
        sbt_buffer_bindings={"record_count": 1, "buffers": []},
        target_control_flow_evidence=control_flow,
        execution_receipt={
            "schema": "rtdl.v4.goal5840_execution_receipt.v1",
            "route_id": ROUTE_ID,
            "mode": "all_hit_count",
            "plan_sha256": declaration["plan_sha256"],
            "executable_identity_sha256": _sha("identity"),
            "target_sha256": _sha("target"),
            "native_library_sha256": native_sha,
            "output_sha256": output_sha,
            "status": "OK",
            "status_code": 0,
            "status_before_output": True,
            "complete": True,
            "partial_result_exposed": False,
            "control_flow_manifest_sha256": control_flow["manifest_sha256"],
            "traversal_receipt": {
                "physical_executor_classification": "optix_traversal_observed",
                "provider_library_sha256": native_sha,
                "output_digest": output_sha,
            },
        },
    )


class Goal5840TargetEvidenceBundleTest(unittest.TestCase):
    def test_capture_reconstructs_exact_triangle_executable_preimage(self) -> None:
        source = "def leaf(out_effect_tag):\n    out_effect_tag[0] = 5\n"
        leaf_ptx = (
            ".version 8.0\n.target sm_89\n.address_size 64\n"
            ".visible .func leaf() { ret; }\n"
        )
        wrapper_source = "extern leaf; optixGetPrimitiveIndex();"
        wrapper_ptx = (
            ".version 8.0\n.target sm_89\n.address_size 64\n"
            ".visible .entry raygen() { ret; }\n"
        )
        composed_ptx = wrapper_ptx + ".visible .func leaf() { ret; }\n"
        source_sha = hashlib.sha256(source.encode()).hexdigest()
        leaf_ptx_sha = hashlib.sha256(leaf_ptx.encode()).hexdigest()
        wrapper_source_sha = hashlib.sha256(wrapper_source.encode()).hexdigest()
        wrapper_ptx_sha = hashlib.sha256(wrapper_ptx.encode()).hexdigest()
        composed_sha = hashlib.sha256(composed_ptx.encode()).hexdigest()
        generated_metadata = {
            "schema": "rtdl.v4.generated_formal_numba_leaf.v1",
            "role": "any_hit",
            "abi_name": "leaf",
            "generated_source_sha256": source_sha,
            "callback_ir_sha256": _sha("ir"),
            "callback_effect_digest": _sha("effect"),
            "callback_abi_sha256": _sha("abi"),
            "nonce_word": 1,
            "numeric_mode": "strict",
            "compiler_function_count": 1,
        }
        generated_leaf = SimpleNamespace(
            role=SimpleNamespace(value="any_hit"),
            generated_source=source,
            to_dict=lambda include_source=False: dict(generated_metadata),
        )
        compiled_leaf = SimpleNamespace(
            schema="rtdl.v4.device_function.v1",
            role="any_hit",
            abi_name="leaf",
            compute_capability=(8, 9),
            numeric_mode="strict",
            generated_source_sha256=source_sha,
            ir_sha256=_sha("ir"),
            ptx=leaf_ptx,
            ptx_sha256=leaf_ptx_sha,
            ptx_version="8.0",
            ptx_target="sm_89",
            external_symbols=(),
            numba_version="test",
            python_version="3.12",
            nonce_word=1,
            compiler_function_count=1,
        )
        wrapper = SimpleNamespace(
            schema="rtdl.v4.generated_optix_wrapper.v1",
            physical_template="test",
            callback_ir_sha256=_sha("ir"),
            callback_abi_sha256=_sha("abi"),
            source=wrapper_source,
            source_sha256=wrapper_source_sha,
            role_symbols=(("any_hit", "leaf"),),
            linked_role_symbols=True,
        )
        composed = SimpleNamespace(
            ptx=composed_ptx,
            ptx_sha256=composed_sha,
            ptx_version="8.0",
            ptx_target="sm_89",
            address_size="64",
            wrapper_ptx_sha256=wrapper_ptx_sha,
            leaf_bindings=(("any_hit", "leaf"),),
            stripped_wrapper_externs=("leaf",),
            stripped_numba_environments=(),
        )
        preimage = {
            "schema": "rtdl.v4.verified_triangle_reduction_executable.v1",
            "authority": _sha("authority"),
            "contract": _sha("contract"),
            "abi": _sha("abi"),
            "wrapper_source": wrapper_source_sha,
            "wrapper_ptx": wrapper_ptx_sha,
            "generated": [source_sha],
            "compiled": [leaf_ptx_sha],
            "composed": composed_sha,
            "options": ["--gpu-architecture=compute_89"],
            "nvrtc_log": _sha("log"),
        }
        executable = SimpleNamespace(
            schema=preimage["schema"],
            authority_sha256=preimage["authority"],
            contract_sha256=preimage["contract"],
            abi_sha256=preimage["abi"],
            wrapper=wrapper,
            wrapper_ptx=wrapper_ptx,
            generated_leaves=(generated_leaf,),
            compiled_leaves=(compiled_leaf,),
            composed=composed,
            compiler_options=tuple(preimage["options"]),
            nvrtc_log_sha256=preimage["nvrtc_log"],
            executable_sha256=_digest(preimage),
        )
        captured = capture_generated_target_artifacts(executable)
        self.assertEqual(
            captured["executable_metadata"]["identity_preimage"], preimage
        )
        self.assertEqual(
            captured["executable_metadata"]["executable_sha256"],
            _digest(preimage),
        )

    def test_three_real_route_plans_bind_exact_raw_operator_contracts(self) -> None:
        bounded_protocol = BoundedRelationProtocol(16, 0.25)
        triangle_all = TriangleReductionProtocol(TriangleReductionMode.ALL_HIT_COUNT)
        triangle_weighted = TriangleReductionProtocol(
            TriangleReductionMode.WEIGHTED_HIT_COUNT
        )
        routes = (
            (
                "stable::bounded_relation::canonical_bounded_pair_collection",
                bounded_relation_family_route(
                    bounded_protocol, _proof(bounded_protocol, "bounded")
                ),
            ),
            (
                ROUTE_ID,
                triangle_reduction_family_route(
                    triangle_all, _proof(triangle_all, "triangle-all")
                ),
            ),
            (
                ROUTE_ID,
                triangle_reduction_family_route(
                    triangle_weighted, _proof(triangle_weighted, "triangle-weighted")
                ),
            ),
            (
                "prospective::builtin_sphere::any_hit_count_continue_u64_per_query",
                sphere_any_hit_count_family_route(),
            ),
        )
        for route_id, route in routes:
            with self.subTest(route_id=route_id, plan=route.plan.plan_sha256):
                declaration = build_family_target_declaration(route_id, route.plan)
                self.assertEqual(declaration["plan_sha256"], route.plan.plan_sha256)
                self.assertEqual(declaration["route_id"], route_id)

    def test_valid_raw_bundle_round_trips(self) -> None:
        bundle = _bundle()
        validate_target_evidence_bundle(bundle)
        self.assertTrue(bundle["claim_boundary"]["raw_target_evidence_transport_only"])
        self.assertFalse(bundle["claim_boundary"]["refinement_or_correctness_established"])

    def test_execution_mode_must_match_triangle_plan(self) -> None:
        bundle = copy.deepcopy(_bundle())
        bundle["execution_receipt"]["mode"] = "weighted_hit_count"
        body = dict(bundle)
        body["bundle_sha256"] = ""
        from rtdsl.v4_target_evidence_bundle import TARGET_EVIDENCE_BUNDLE_DOMAIN
        bundle["bundle_sha256"] = hashlib.sha256(
            TARGET_EVIDENCE_BUNDLE_DOMAIN
            + json.dumps(
                body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("ascii")
        ).hexdigest()
        with self.assertRaisesRegex(
            TargetEvidenceBundleError, "TE062_EXECUTION_MODE_PLAN"
        ):
            validate_target_evidence_bundle(bundle)

    def test_compiler_projection_is_forbidden_recursively(self) -> None:
        declaration = build_family_target_declaration(ROUTE_ID, _plan())
        with self.assertRaisesRegex(
            TargetEvidenceBundleError, "TE004_COMPILER_PROJECTION_FORBIDDEN"
        ):
            build_target_evidence_bundle(
                route_id=ROUTE_ID,
                declaration=declaration,
                declaration_authority_sha256=_sha("authority"),
                program_artifacts=[{
                    "artifact_id": "bad",
                    "format_id": "bad",
                    "payload": make_blob_record(b"x"),
                }],
                generated_target_artifacts={"compiler_projection": {}},
                provider_descriptor={},
                provider_projection={},
                executable_identity={},
                target_binding={},
                native_producer_descriptor={},
                sbt_buffer_bindings={},
                target_control_flow_evidence={},
                execution_receipt={},
            )

    def test_blob_mutation_fails_even_when_outer_seal_is_stale(self) -> None:
        bundle = copy.deepcopy(_bundle())
        bundle["generated_target_artifacts"]["wrapper"]["source"]["base64"] = "eA=="
        with self.assertRaisesRegex(TargetEvidenceBundleError, "TE025_BUNDLE_SEAL"):
            validate_target_evidence_bundle(bundle)

    def test_operator_contract_bytes_must_match_plan_hash(self) -> None:
        plan = _plan()
        plan.to_dict()["family_shape"]["result_pipeline"][0][
            "operator_contract_sha256"
        ] = _sha("wrong")
        with self.assertRaisesRegex(TargetEvidenceBundleError, "TE018_OPERATOR_CONTRACT_DIGEST"):
            build_family_target_declaration(ROUTE_ID, plan)

    def test_unknown_route_fails_closed(self) -> None:
        with self.assertRaisesRegex(TargetEvidenceBundleError, "TE013_ROUTE_UNSUPPORTED"):
            registered_operator_contracts("unknown")


if __name__ == "__main__":
    unittest.main()
