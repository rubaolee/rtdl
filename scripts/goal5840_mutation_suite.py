#!/usr/bin/env python3
"""Apply Goal5840's frozen mutations to exact captured target bundles."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = Path(__file__).with_name("goal5840_independent_target_checker.py")
PREREGISTRATION = (
    ROOT
    / "history/internal_docs"
    / "goal5840_independent_lowering_refinement_20260903"
    / "GOAL5840_PREREGISTRATION.json"
)
FAMILY_PLAN_DOMAIN = b"rtdl.family_compilation_plan.v1\0"
FAMILY_SHAPE_DOMAIN = b"rtdl.family_shape.v1\0"
PROTOCOL_INSTANCE_DOMAIN = b"rtdl.protocol_instance.v1\0"
BUNDLE_DOMAIN = b"rtdl.v4.target_evidence_bundle.v2\0"
REPORT_DOMAIN = b"rtdl.goal5840.exact_bundle_mutation_suite.v1\0"


def _load_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "_goal5840_independent_target_checker", CHECKER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Goal5840 independent checker cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _load_checker()


class Goal5840MutationError(ValueError):
    """A bundle or frozen mutation cannot be applied exactly."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _mapping(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise Goal5840MutationError(f"{path}: dict required")
    return value


def _sequence(value: object, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise Goal5840MutationError(f"{path}: list required")
    return value


def _sealed(value: dict[str, Any], field: str) -> None:
    value[field] = _digest({key: item for key, item in value.items() if key != field})


def _load_frozen_mutations() -> dict[tuple[str, str], Mapping[str, object]]:
    document = json.loads(PREREGISTRATION.read_text(encoding="ascii"))
    rows = document.get("mutation_matrix")
    if not isinstance(rows, list):
        raise Goal5840MutationError("preregistration mutation matrix missing")
    result: dict[tuple[str, str], Mapping[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise Goal5840MutationError("preregistration mutation row is not an object")
        key = (str(row.get("route_id")), str(row.get("property_id")))
        if key in result:
            raise Goal5840MutationError(f"duplicate frozen mutation: {key}")
        result[key] = row
    expected = {
        (route_id, property_id)
        for route_id in checker.ROUTE_RULES
        for property_id in checker.PROPERTIES
    }
    if set(result) != expected or len(result) != 15:
        raise Goal5840MutationError("frozen 3x5 mutation denominator differs")
    return result


FROZEN_MUTATIONS = _load_frozen_mutations()


def _replace_blob_text(record: dict[str, Any], text: str) -> None:
    raw = text.encode("utf-8")
    record.update({
        "encoding": "utf-8",
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "base64": base64.b64encode(raw).decode("ascii"),
    })


def _requirements_sha256(shape: dict[str, Any]) -> str:
    graph_nodes = _sequence(shape.get("graph_nodes"), "family_shape.graph_nodes")
    callback = _mapping(shape.get("callback"), "family_shape.callback")
    roles = _sequence(callback.get("roles"), "family_shape.callback.roles")
    channels = _sequence(shape.get("channels"), "family_shape.channels")
    events = _sequence(shape.get("events"), "family_shape.events")
    pipeline = _sequence(shape.get("result_pipeline"), "result_pipeline")
    provider_builtins = {
        str(row["producer"]["builtin"])
        for row in channels
        if isinstance(row, dict)
        and isinstance(row.get("producer"), dict)
        and row["producer"].get("kind") == "provider_builtin"
    }
    provider_builtins.update(
        str(row["provider_builtin"])
        for row in events
        if isinstance(row, dict) and row.get("source") == "provider_builtin"
    )
    operators = []
    for raw in pipeline:
        row = _mapping(raw, "result_pipeline[]")
        if row.get("operator") != "provider_operator":
            raise Goal5840MutationError("non-provider result operator is out of scope")
        operators.append({
            "operator_id": row.get("operator_id"),
            "operator_contract_sha256": row.get("operator_contract_sha256"),
        })
    return _digest({
        "schema": "rtdl.family_plan_requirements.v1",
        "graph_kinds": sorted({str(row["kind"]) for row in graph_nodes}),
        "primitive_kinds": sorted({
            str(row["primitive_kind"])
            for row in graph_nodes
            if row["primitive_kind"] != "none"
        }),
        "callback_roles": sorted(str(row["role"]) for row in roles),
        "provider_builtins": sorted(provider_builtins),
        "operator_contracts": sorted(
            operators,
            key=lambda row: (
                str(row["operator_id"]), str(row["operator_contract_sha256"])
            ),
        ),
        "capabilities": sorted(str(item) for item in shape["capabilities"]),
    })


def _artifact_bundle_sha256(
    bundle: dict[str, Any], plan: dict[str, Any], plan_sha256: str
) -> str:
    rows = []
    for raw in _sequence(bundle.get("program_artifacts"), "program_artifacts"):
        row = _mapping(raw, "program_artifacts[]")
        payload = _mapping(row.get("payload"), "program_artifacts[].payload")
        rows.append({
            "artifact_id": row.get("artifact_id"),
            "format_id": row.get("format_id"),
            "payload_bytes": payload.get("bytes"),
            "payload_sha256": payload.get("sha256"),
        })
    rows.sort(key=lambda row: str(row["artifact_id"]))
    return _digest({
        "schema": "rtdl.family_program_artifacts.v1",
        "plan_sha256": plan_sha256,
        "callback_source_sha256": plan["callback_source_sha256"],
        "callback_ir_sha256": plan["callback_ir_sha256"],
        "effect_digest": plan["effect_digest"],
        "abi_sha256": plan["abi_sha256"],
        "behavior_schema_sha256": plan["behavior_schema_sha256"],
        "artifacts": rows,
    })


def _reseal_declaration(bundle: dict[str, Any]) -> None:
    declaration = _mapping(bundle.get("declaration"), "declaration")
    _sealed(declaration, "declaration_sha256")


def _reseal_plan_chain(bundle: dict[str, Any]) -> None:
    declaration = _mapping(bundle.get("declaration"), "declaration")
    plan = _mapping(declaration.get("family_plan"), "family_plan")
    shape = _mapping(plan.get("family_shape"), "family_shape")
    protocol = _mapping(plan.get("protocol_instance"), "protocol_instance")
    plan["family_shape_sha256"] = hashlib.sha256(
        FAMILY_SHAPE_DOMAIN + _canonical(shape)
    ).hexdigest()
    plan["protocol_instance_sha256"] = hashlib.sha256(
        PROTOCOL_INSTANCE_DOMAIN + _canonical(protocol)
    ).hexdigest()
    plan_sha256 = hashlib.sha256(
        FAMILY_PLAN_DOMAIN + _canonical(plan)
    ).hexdigest()
    declaration["plan_sha256"] = plan_sha256
    _reseal_declaration(bundle)

    physical = _mapping(bundle.get("physical_evidence"), "physical_evidence")
    projection = _mapping(physical.get("provider_projection"), "provider_projection")
    for field in (
        "family_shape_sha256", "protocol_instance_sha256",
        "callback_source_sha256", "callback_ir_sha256", "effect_digest",
        "abi_sha256", "behavior_schema_sha256", "canonical_template_id",
    ):
        projection[field] = plan[field]
    projection["plan_sha256"] = plan_sha256
    projection["requirements_sha256"] = _requirements_sha256(shape)
    projection["artifact_bundle_sha256"] = _artifact_bundle_sha256(
        bundle, plan, plan_sha256
    )
    _sealed(projection, "projection_sha256")

    generated = _mapping(bundle.get("generated_target_artifacts"), "generated")
    metadata = _mapping(generated.get("executable_metadata"), "executable_metadata")
    preimage = _mapping(metadata.get("identity_preimage"), "identity_preimage")
    if "plan_sha256" in preimage:
        preimage["plan_sha256"] = plan_sha256
        metadata["executable_sha256"] = _digest(preimage)
    identity = _mapping(physical.get("executable_identity"), "executable_identity")
    identity["provider_projection_sha256"] = projection["projection_sha256"]
    identity["plan_sha256"] = plan_sha256
    identity["executable_sha256"] = metadata["executable_sha256"]
    _sealed(identity, "identity_sha256")
    receipt = _mapping(bundle.get("execution_receipt"), "execution_receipt")
    receipt["plan_sha256"] = plan_sha256
    receipt["executable_identity_sha256"] = identity["identity_sha256"]


def _reseal_executable_chain(bundle: dict[str, Any]) -> None:
    generated = _mapping(bundle.get("generated_target_artifacts"), "generated")
    metadata = _mapping(generated.get("executable_metadata"), "executable_metadata")
    preimage = _mapping(metadata.get("identity_preimage"), "identity_preimage")
    metadata["executable_sha256"] = _digest(preimage)
    composed = _mapping(generated.get("composed_ptx"), "composed_ptx")
    metadata["composed_ptx_sha256"] = composed["sha256"]
    physical = _mapping(bundle.get("physical_evidence"), "physical_evidence")
    identity = _mapping(physical.get("executable_identity"), "executable_identity")
    identity["executable_sha256"] = metadata["executable_sha256"]
    identity["generated_artifact_sha256"] = composed["sha256"]
    _sealed(identity, "identity_sha256")
    receipt = _mapping(bundle.get("execution_receipt"), "execution_receipt")
    receipt["executable_identity_sha256"] = identity["identity_sha256"]


def _reseal_bundle(bundle: dict[str, Any]) -> None:
    body = dict(bundle)
    body["bundle_sha256"] = ""
    bundle["bundle_sha256"] = hashlib.sha256(
        BUNDLE_DOMAIN + _canonical(body)
    ).hexdigest()


def apply_frozen_mutation(
    source_bundle: Mapping[str, object], route_id: str, property_id: str
) -> tuple[dict[str, Any], str, str]:
    """Return a fully resealed copy with the exact preregistered mutation."""

    frozen = FROZEN_MUTATIONS.get((route_id, property_id))
    if frozen is None:
        raise Goal5840MutationError(f"unregistered mutation: {route_id}/{property_id}")
    bundle = copy.deepcopy(dict(source_bundle))
    if bundle.get("route_id") != route_id:
        raise Goal5840MutationError("bundle route differs from mutation route")
    selector = str(frozen["target_selector"])
    replacement = str(frozen["replacement"])

    if property_id == "CP001_ROLE_EFFECT_CLOSURE":
        if selector != "callback_abi.roles[any_hit].effects[accept_continue]":
            raise Goal5840MutationError("CP001 selector differs")
        artifacts = _sequence(bundle.get("program_artifacts"), "program_artifacts")
        matches = [
            row for row in artifacts
            if isinstance(row, dict) and row.get("artifact_id") == "rtdl.callback.abi"
        ]
        if len(matches) != 1:
            raise Goal5840MutationError("exactly one Callback ABI artifact required")
        payload = _mapping(matches[0].get("payload"), "callback_abi.payload")
        abi = json.loads(base64.b64decode(str(payload["base64"]), validate=True))
        any_hits = [
            row for row in _sequence(abi.get("roles"), "callback_abi.roles")
            if isinstance(row, dict) and row.get("role") == "any_hit"
        ]
        if len(any_hits) != 1:
            raise Goal5840MutationError("exactly one any_hit ABI role required")
        effects = _sequence(any_hits[0].get("effects"), "any_hit.effects")
        accept = [
            row for row in effects
            if isinstance(row, dict) and row.get("kind") == "accept_continue"
        ]
        if len(accept) != 1:
            raise Goal5840MutationError("exactly one accept_continue effect required")
        accept[0]["kind"] = replacement
        _sealed(abi, "abi_sha256")
        _replace_blob_text(payload, _canonical(abi).decode("ascii"))
        plan = _mapping(
            _mapping(bundle.get("declaration"), "declaration").get("family_plan"),
            "family_plan",
        )
        plan["abi_sha256"] = abi["abi_sha256"]
        _mapping(plan.get("protocol_instance"), "protocol_instance")[
            "abi_sha256"
        ] = abi["abi_sha256"]
        generated = _mapping(bundle.get("generated_target_artifacts"), "generated")
        wrapper = _mapping(generated.get("wrapper"), "wrapper")
        _mapping(wrapper.get("metadata"), "wrapper.metadata")[
            "callback_abi_sha256"
        ] = abi["abi_sha256"]
        for row in _sequence(generated.get("leaves"), "generated.leaves"):
            _mapping(row["generated_metadata"], "leaf.metadata")[
                "callback_abi_sha256"
            ] = abi["abi_sha256"]
        metadata = _mapping(generated.get("executable_metadata"), "metadata")
        preimage = _mapping(metadata.get("identity_preimage"), "identity_preimage")
        preimage["abi_sha256" if route_id.startswith("prospective::") else "abi"] = (
            abi["abi_sha256"]
        )
        _reseal_plan_chain(bundle)
        _reseal_executable_chain(bundle)
    elif property_id == "CP002_SEMANTIC_ABI_OWNERSHIP":
        plan = _mapping(
            _mapping(bundle.get("declaration"), "declaration").get("family_plan"),
            "family_plan",
        )
        if selector == "protocol_instance.nominal_semantics.output":
            protocol = _mapping(plan.get("protocol_instance"), "protocol_instance")
            _mapping(protocol.get("nominal_semantics"), "nominal_semantics")[
                "output"
            ] = replacement
        else:
            expected = (
                "family_schema.channels[relation_item_id].semantic"
                if route_id.startswith("stable::bounded")
                else "family_schema.channels[triangle_primitive_index].semantic"
            )
            if selector != expected:
                raise Goal5840MutationError("CP002 selector differs")
            shape = _mapping(plan.get("family_shape"), "family_shape")
            channels = _sequence(shape.get("channels"), "family_shape.channels")
            if len(channels) != 1:
                raise Goal5840MutationError("exactly one channel required")
            channels[0]["semantic"] = replacement
        _reseal_plan_chain(bundle)
    elif property_id == "CP003_PHYSICAL_BINDING":
        plan = _mapping(
            _mapping(bundle.get("declaration"), "declaration").get("family_plan"),
            "family_plan",
        )
        shape = _mapping(plan.get("family_shape"), "family_shape")
        if selector == "family_schema.physical.sbt.record_count_relation":
            physical = _mapping(shape.get("physical"), "family_shape.physical")
            _mapping(physical.get("sbt"), "family_shape.physical.sbt")[
                "record_count_relation"
            ] = replacement
        else:
            if selector != "family_schema.physical.primitive_kind":
                raise Goal5840MutationError("CP003 selector differs")
            nodes = _sequence(shape.get("graph_nodes"), "family_shape.graph_nodes")
            if len(nodes) != 1:
                raise Goal5840MutationError("exactly one graph node required")
            nodes[0]["primitive_kind"] = replacement
        _reseal_plan_chain(bundle)
    elif property_id == "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS":
        field, _expected = checker.ROUTE_RULES[route_id]["operator_field"]
        if selector != f"result_operator.contract.{field}":
            raise Goal5840MutationError("CP004 selector differs")
        declaration = _mapping(bundle.get("declaration"), "declaration")
        contracts = _sequence(declaration.get("operator_contracts"), "contracts")
        if len(contracts) != 1:
            raise Goal5840MutationError("exactly one operator contract required")
        contracts[0][field] = replacement
        plan = _mapping(declaration.get("family_plan"), "family_plan")
        shape = _mapping(plan.get("family_shape"), "family_shape")
        pipeline = _sequence(shape.get("result_pipeline"), "result_pipeline")
        if len(pipeline) != 1:
            raise Goal5840MutationError("exactly one result operator required")
        pipeline[0]["operator_contract_sha256"] = _digest(contracts[0])
        _reseal_plan_chain(bundle)
    elif property_id == "CP005_EXECUTABLE_IDENTITY_CHAIN":
        receipt = _mapping(bundle.get("execution_receipt"), "execution_receipt")
        if selector == "composed_ptx.bytes":
            generated = _mapping(bundle.get("generated_target_artifacts"), "generated")
            composed = _mapping(generated.get("composed_ptx"), "composed_ptx")
            changed = base64.b64decode(
                str(composed["base64"]), validate=True
            ).decode("utf-8") + (
                "\n.visible .func goal5840_different_valid_route() { ret; }\n"
            )
            _replace_blob_text(composed, changed)
            metadata = _mapping(generated.get("executable_metadata"), "metadata")
            composition = _mapping(metadata.get("composition"), "composition")
            preimage = _mapping(metadata.get("identity_preimage"), "identity_preimage")
            if composition.get("mode") == "inline_cuda_wrapper":
                wrapper = _mapping(generated.get("wrapper"), "wrapper")
                wrapper_ptx = _mapping(wrapper.get("ptx"), "wrapper.ptx")
                _replace_blob_text(wrapper_ptx, changed)
                composition["wrapper_ptx_sha256"] = wrapper_ptx["sha256"]
                preimage["wrapper_ptx"] = wrapper_ptx["sha256"]
            preimage[
                "composed_ptx_sha256"
                if route_id.startswith("prospective::")
                else "composed"
            ] = composed["sha256"]
            _reseal_executable_chain(bundle)
        elif selector == "execution_receipt.native_library_sha256":
            receipt["native_library_sha256"] = hashlib.sha256(
                f"{route_id}:different-native-library".encode()
            ).hexdigest()
        elif selector == "execution_receipt.target_sha256":
            receipt["target_sha256"] = hashlib.sha256(
                f"{route_id}:different-target".encode()
            ).hexdigest()
        else:
            raise Goal5840MutationError("CP005 selector differs")
    else:
        raise Goal5840MutationError(f"unknown property: {property_id}")

    _reseal_bundle(bundle)
    return bundle, selector, replacement


def run_exact_bundle_mutations(
    bundles: Sequence[Mapping[str, object]],
    trust_roots: Mapping[str, Mapping[str, str]],
) -> dict[str, object]:
    """Run the 15 frozen units over all four required mode bundles."""

    applications = []
    observed_modes = {route_id: set() for route_id in checker.ROUTE_RULES}
    for source in bundles:
        route_id = str(source.get("route_id"))
        receipt = source.get("execution_receipt")
        if route_id not in checker.ROUTE_RULES or not isinstance(receipt, Mapping):
            raise Goal5840MutationError("unsupported bundle or receipt")
        mode = str(receipt.get("mode"))
        observed_modes[route_id].add(mode)
        roots = trust_roots.get(f"{route_id}::{mode}")
        if roots is None:
            raise Goal5840MutationError(f"missing trust roots for {route_id}/{mode}")
        for property_id in checker.PROPERTIES:
            mutated, selector, replacement = apply_frozen_mutation(
                source, route_id, property_id
            )
            report = checker.check_target_evidence(
                mutated,
                trusted_declaration_sha256=roots["declaration_sha256"],
                trusted_executable_identity_sha256=roots[
                    "executable_identity_sha256"
                ],
                trusted_control_flow_manifest_sha256=roots[
                    "control_flow_manifest_sha256"
                ],
            )
            row = next(
                item for item in report["property_checks"]
                if item["property_id"] == property_id
            )
            expected_reason_prefix = "TC" + property_id[2:5]
            if (
                report["verdict"] != "REJECT"
                or row["verdict"] != "REJECT"
                or not str(row["reason_id"]).startswith(expected_reason_prefix)
            ):
                raise Goal5840MutationError(
                    "mutation did not reach its target property checker: "
                    f"{route_id}/{mode}/{property_id}: {report}"
                )
            applications.append({
                "route_id": route_id,
                "mode": mode,
                "property_id": property_id,
                "mutation_id": f"{route_id}::{property_id}",
                "target_selector": selector,
                "replacement": replacement,
                "preregistered_required_rejection": FROZEN_MUTATIONS[
                    (route_id, property_id)
                ]["required_rejection"],
                "checker_verdict": report["verdict"],
                "target_property_verdict": row["verdict"],
                "target_property_reason_id": row["reason_id"],
                "gpu_launch_required_for_rejection": False,
            })

    expected_modes = {
        "stable::bounded_relation::canonical_bounded_pair_collection": {
            "capacity_fail_closed_collection"
        },
        "stable::triangle_reduction::checked_u64_reduction": {
            "all_hit_count", "weighted_hit_count"
        },
        "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": {
            "accept_every_hit_and_continue"
        },
    }
    unique_units = {(row["route_id"], row["property_id"]) for row in applications}
    if observed_modes != expected_modes or len(unique_units) != 15 \
            or len(applications) != 20:
        raise Goal5840MutationError(
            f"mutation/mode denominator differs: {observed_modes!r}"
        )
    result: dict[str, object] = {
        "schema": "rtdl.goal5840.exact_bundle_mutation_suite.v1",
        "status": "PASS__ALL_FROZEN_MUTATIONS_REJECTED_BEFORE_GPU_LAUNCH",
        "preregistered_claim_unit_count": len(unique_units),
        "mode_replication_application_count": len(applications),
        "rejected_application_count": len(applications),
        "all_rejected_before_gpu_launch": True,
        "applications": applications,
        "claim_boundary": {
            "exact_captured_bundle_mutations_only": True,
            "general_soundness_theorem": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        },
        "report_sha256": "",
    }
    result["report_sha256"] = hashlib.sha256(
        REPORT_DOMAIN + _canonical(result)
    ).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", action="append", type=Path, required=True)
    parser.add_argument("--trust-roots", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    bundles = [json.loads(path.read_text(encoding="ascii")) for path in args.bundle]
    roots = json.loads(args.trust_roots.read_text(encoding="ascii"))
    result = run_exact_bundle_mutations(bundles, roots["trust_roots"])
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps({
        "output": str(args.output),
        "claim_units": result["preregistered_claim_unit_count"],
        "applications": result["mode_replication_application_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
