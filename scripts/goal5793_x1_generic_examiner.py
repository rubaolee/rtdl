"""Candidate-agnostic dual-path declaration examiner for Goal5793 X1.

This module evaluates only supplied declarations.  It performs no discovery,
selection, execution, compilation, timing, or executable-authority issuance.
The frozen product admission primitive and a new independent full-product-
schema recount must agree exactly on the inert decision projection.  The
frozen Goal5789-v1 checker is a separate overlap-only severity layer because
that older schema cannot express every product field.  No disagreement is a
rule for choosing the more favorable answer.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import sys
from typing import Mapping, Sequence


INPUT_SCHEMA = "rtdl.goal5793.x1.generic_examiner_input.v1"
RESULT_SCHEMA = "rtdl.goal5793.x1.generic_examiner_result.v1"
INFRA_INVALID = "INFRA_INVALID"
DISAGREEMENT = "INFRA_INVALID__NEVER_PICK_FAVORABLE_VERDICT"
ROOT = Path(__file__).resolve().parents[1]
PRODUCT_ADMISSION_PATH = ROOT / "src/rtdsl/v4_semantic_physical_admission.py"
REFERENCE_V1_PATH = ROOT / "scripts/goal5789_independent_compatibility_checker.py"
INDEPENDENT_RECOUNT_PATH = ROOT / "scripts/goal5793_x1_independent_product_recount.py"
CANONICAL_HELPER_PATH = ROOT / "scripts/goal5793_x1_canonical.py"
REGISTRY_DERIVATION_PATH = ROOT / "scripts/goal5793_x1_registry_derivation.py"
EXPECTED_PRODUCT_ADMISSION_SHA256 = (
    "eb8a4a33352b94ad18d95cabe1e9c89389427b09a2bf98dbae3028d8fa940267"
)
EXPECTED_REFERENCE_V1_SHA256 = (
    "abb1f1575af824cc37e9d9984aff8679f79cb89f4ad7ed2792ede5a3db75ac2e"
)
EXPECTED_INDEPENDENT_RECOUNT_SHA256 = (
    "daba482c415e0b92af0c6f38affaf389c8b4fb71a8d8f7fad733ea50be901b69"
)
EXPECTED_CANONICAL_HELPER_SHA256 = (
    "13b22dbae22b0a70763fdf46031c7975ab1eaebe20c37789f397242b7a1c9b3a"
)
EXPECTED_REGISTRY_DERIVATION_SHA256 = (
    "337b0480109ee0184743b30ccd09dbd6a347b182211119d4765afa76bcab1d0c"
)

# Honest coverage accounting for the frozen product rule enum.  X1 replays all
# 35 rules reachable through declaration evaluation.  SP022 is a dead fallback
# because every member of the closed eight-field policy has a dedicated rule;
# SP063/SP070/SP071 occur only during authority issuance/reverification.
DECLARATION_RULE_CLASSIFICATION = {
    "REACHED": (
        "SP000_MALFORMED_INPUT",
        "SP001_SEMANTIC_REQUIREMENT_UNKNOWN",
        "SP002_PHYSICAL_GUARANTEE_UNKNOWN",
        "SP003_LIVE_BINDING_UNKNOWN",
        "SP004_CANONICAL_CANDIDATES_UNKNOWN",
        "SP010_IDENTITY_INVALID",
        "SP011_DIGEST_INVALID",
        "SP020_POLICY_INCOMPLETE",
        "SP021_POLICY_UNSUPPORTED_FIELD",
        "SP023_REQUIRED_HIT_SEMANTIC_MISSING",
        "SP024_EXACTNESS_POLICY_MISMATCH",
        "SP025_TIE_POLICY_MISMATCH",
        "SP026_MULTIPLICITY_POLICY_MISMATCH",
        "SP027_OVERFLOW_POLICY_MISMATCH",
        "SP028_NUMERIC_PRECISION_POLICY_MISMATCH",
        "SP029_ORDER_POLICY_MISMATCH",
        "SP030_MAP_STAGE_UNKNOWN",
        "SP031_MAP_STAGE_DUPLICATE",
        "SP032_MAP_GRAPH_MISMATCH",
        "SP033_MAP_SOURCE_UNKNOWN",
        "SP034_MAP_SOURCE_DIGEST_MISMATCH",
        "SP035_INPUT_TYPE_POLICY_MISMATCH",
        "SP036_OUTPUT_TYPE_POLICY_MISMATCH",
        "SP037_ALGORITHM_IDENTITY_MISMATCH",
        "SP038_DECLARED_DOMAIN_MISMATCH",
        "SP039_ORIENTATION_CONTRACT_MISMATCH",
        "SP040_GAS_CONTRACT_MISMATCH",
        "SP041_MAP_SOURCE_UNUSED",
        "SP050_CALLBACK_BINDING_MISMATCH",
        "SP051_SCHEMA_BINDING_MISMATCH",
        "SP052_TARGET_PROVIDER_MISMATCH",
        "SP053_TARGET_CAPABILITY_MISSING",
        "SP060_CANONICAL_CANDIDATE_UNSUPPORTED",
        "SP061_CANONICAL_CANDIDATE_AMBIGUOUS",
        "SP062_CANONICAL_LIVE_BINDING_MISMATCH",
    ),
    "UNREACHABLE_BY_CURRENT_CODE": (
        "SP022_SEMANTIC_GUARANTEE_MISMATCH",
    ),
    "AUTHORITY_ONLY": (
        "SP063_PHYSICAL_AUTHORITY_NONCANONICAL",
        "SP070_AUTHORITY_NOT_LIVE",
        "SP071_AUTHORITY_BINDING_DRIFT",
    ),
}

# These names are rejected wherever they occur in the submitted structure.
# Their values are therefore unavailable to both admission paths.
FORBIDDEN_DECISION_INPUT_KEYS = frozenset({
    "candidate_id",
    "citation_key",
    "source_index",
    "role_assignment",
    "expected_disposition",
    "selected_index",
    "performance_expectation",
    "implementation_ease",
})

_TOP_KEYS = frozenset({
    "schema",
    "semantic_requirement",
    "physical_guarantee",
    "live_binding",
    "canonical_candidates",
    "reference_certificate",
    "reference_authority",
})


def _mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}:expected_mapping")
    return value


def _sequence(value: object, path: str) -> Sequence[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{path}:expected_sequence")
    return value


def _find_forbidden(value: object, path: str = "input") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str) and key in FORBIDDEN_DECISION_INPUT_KEYS:
                found.append(f"{path}.{key}")
            found.extend(_find_forbidden(child, f"{path}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            found.extend(_find_forbidden(child, f"{path}[{index}]"))
    return found


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_exact_module(path: Path, module_name: str, expected_sha256: str):
    resolved = path.resolve(strict=True)
    if _file_sha256(resolved) != expected_sha256:
        raise RuntimeError(f"frozen_module_sha256_mismatch:{resolved}")
    spec = importlib.util.spec_from_file_location(module_name, resolved)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"frozen_module_spec_unavailable:{resolved}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
    origin = Path(module.__file__).resolve(strict=True)
    if origin != resolved:
        raise RuntimeError(f"frozen_module_origin_mismatch:{origin}:{resolved}")
    return module


def _load_scientific_modules():
    product = _load_exact_module(
        PRODUCT_ADMISSION_PATH,
        "_goal5793_x1_frozen_product_admission",
        EXPECTED_PRODUCT_ADMISSION_SHA256,
    )
    reference_module = _load_exact_module(
        REFERENCE_V1_PATH,
        "_goal5793_x1_frozen_reference_v1",
        EXPECTED_REFERENCE_V1_SHA256,
    )
    recount = _load_exact_module(
        INDEPENDENT_RECOUNT_PATH,
        "_goal5793_x1_frozen_independent_product_recount",
        EXPECTED_INDEPENDENT_RECOUNT_SHA256,
    )
    return product, reference_module, recount


def _canonical_module():
    return _load_exact_module(
        CANONICAL_HELPER_PATH,
        "_goal5793_x1_frozen_canonical_helper",
        EXPECTED_CANONICAL_HELPER_SHA256,
    )


def _registry_module():
    return _load_exact_module(
        REGISTRY_DERIVATION_PATH,
        "_goal5793_x1_frozen_registry_derivation",
        EXPECTED_REGISTRY_DERIVATION_SHA256,
    )


def _canonical_digest(value, *, domain: str, version: int, projection: str):
    return _canonical_module().canonical_digest(
        value, domain=domain, version=version, projection=projection
    )


def _seal_document(document, *, seal_field: str, domain: str, version: int):
    return _canonical_module().seal_document(
        document, seal_field=seal_field, domain=domain, version=version
    )


def _frozen_runtime_dependencies() -> tuple[dict[str, str], list[str]]:
    observed = {
        "product_admission_sha256": _file_sha256(PRODUCT_ADMISSION_PATH),
        "reference_goal5789_v1_sha256": _file_sha256(REFERENCE_V1_PATH),
        "independent_product_recount_sha256": _file_sha256(
            INDEPENDENT_RECOUNT_PATH
        ),
        "canonical_helper_sha256": _file_sha256(CANONICAL_HELPER_PATH),
        "generic_examiner_sha256": _file_sha256(Path(__file__).resolve()),
        "registry_derivation_sha256": _file_sha256(REGISTRY_DERIVATION_PATH),
    }
    reasons = []
    if observed["product_admission_sha256"] != EXPECTED_PRODUCT_ADMISSION_SHA256:
        reasons.append("frozen_product_admission_bytes_mismatch")
    if observed["reference_goal5789_v1_sha256"] != EXPECTED_REFERENCE_V1_SHA256:
        reasons.append("frozen_goal5789_v1_checker_bytes_mismatch")
    if observed["independent_product_recount_sha256"] \
            != EXPECTED_INDEPENDENT_RECOUNT_SHA256:
        reasons.append("frozen_independent_product_recount_bytes_mismatch")
    if observed["canonical_helper_sha256"] != EXPECTED_CANONICAL_HELPER_SHA256:
        reasons.append("frozen_canonical_helper_bytes_mismatch")
    if observed["registry_derivation_sha256"] \
            != EXPECTED_REGISTRY_DERIVATION_SHA256:
        reasons.append("frozen_registry_derivation_bytes_mismatch")
    return observed, reasons


def _product_projection(payload: Mapping[str, object]) -> dict[str, object]:
    semantic = _mapping(payload["semantic_requirement"], "semantic_requirement")
    physical = _mapping(payload["physical_guarantee"], "physical_guarantee")
    binding = _mapping(payload["live_binding"], "live_binding")
    candidates = _sequence(payload["canonical_candidates"], "canonical_candidates")
    product_maps = _sequence(physical.get("maps"), "physical_guarantee.maps")
    raw_manifest = _mapping(
        physical.get("source_manifest"), "physical_guarantee.source_manifest"
    )
    used_manifest = {
        item.get("source_id"): raw_manifest.get(item.get("source_id"))
        for item in (
            _mapping(raw, f"physical_guarantee.maps[{index}]")
            for index, raw in enumerate(product_maps)
        )
        if isinstance(item.get("source_id"), str)
    }
    return {
        "semantic": {
            "contract_id": semantic.get("contract_id"),
            "algorithm_identity": semantic.get("algorithm_identity"),
            "declared_domain_sha256": semantic.get("declared_domain_sha256"),
            "policy": semantic.get("policy"),
            "required_hit_semantics": semantic.get("required_hit_semantics"),
            "specification_source_sha256": semantic.get(
                "specification_source_sha256"
            ),
        },
        "physical": {
            "encoding_id": physical.get("encoding_id"),
            "geometry_family": physical.get("geometry_family"),
            "schema_sha256": physical.get("schema_sha256"),
            "callback_ir_sha256": physical.get("callback_ir_sha256"),
            "effect_digest": physical.get("effect_digest"),
            "guarantees": physical.get("guarantees"),
            "maps": product_maps,
            "hit_semantics": physical.get("hit_semantics"),
            "gas": {
                "graph_depth": physical.get("gas_graph_depth"),
                "sbt_record_stride": physical.get("gas_sbt_record_stride"),
                "update_policy": physical.get("gas_update_policy"),
            },
            "buffer_contract_sha256": physical.get("buffer_contract_sha256"),
            "source_manifest": used_manifest,
        },
        "target": {
            "target_sha256": binding.get("target_sha256"),
            "provider": binding.get("target_provider"),
            "native_sha256": binding.get("canonical_artifact_sha256"),
            "capabilities": binding.get("target_capabilities"),
        },
        "canonical_candidates": [
            {
                "template_id": _mapping(item, "canonical_candidate").get(
                    "template_id"
                ),
                "canonical": _mapping(item, "canonical_candidate").get("canonical"),
                "algorithm_identity": _mapping(
                    item, "canonical_candidate"
                ).get("algorithm_identity"),
                "geometry_family": _mapping(item, "canonical_candidate").get(
                    "geometry_family"
                ),
                "schema_sha256": _mapping(item, "canonical_candidate").get(
                    "schema_sha256"
                ),
                "guarantees": _mapping(item, "canonical_candidate").get(
                    "guarantees"
                ),
            }
            for item in candidates
        ],
    }


def _reference_projection(payload: Mapping[str, object]) -> dict[str, object]:
    certificate = _mapping(payload["reference_certificate"], "reference_certificate")
    semantic = _mapping(certificate.get("semantic_request"), "semantic_request")
    physical = _mapping(certificate.get("physical_encoding"), "physical_encoding")
    callback = _mapping(certificate.get("callback_contract"), "callback_contract")
    target = _mapping(certificate.get("target_contract"), "target_contract")
    evidence = _mapping(certificate.get("evidence_contract"), "evidence_contract")
    source_pins = _mapping(evidence.get("source_pins"), "evidence_contract.source_pins")
    maps = _sequence(physical.get("maps"), "physical_encoding.maps")
    buffers = _sequence(physical.get("buffers"), "physical_encoding.buffers")
    candidates = _sequence(
        certificate.get("canonical_candidates"), "canonical_candidates"
    )
    spec_pin = semantic.get("specification_source_pin")
    geometry = physical.get("geometry_family")
    required_caps = ["optix", "bound_program_bundle", f"optix_{geometry}"]
    product_maps = []
    map_manifest: dict[str, object] = {}
    for index, raw in enumerate(maps):
        item = _mapping(raw, f"physical_encoding.maps[{index}]")
        source_pin = item.get("source_pin")
        product_maps.append({
            "kind": item.get("kind"),
            "source_id": source_pin,
            "source_sha256": item.get("source_sha256"),
            "consumes": item.get("consumes"),
            "produces": item.get("produces"),
        })
        if isinstance(source_pin, str):
            map_manifest[source_pin] = source_pins.get(source_pin)
    return {
        "semantic": {
            "contract_id": semantic.get("contract_id"),
            "algorithm_identity": semantic.get("algorithm_identity"),
            "declared_domain_sha256": semantic.get("declared_domain_sha256"),
            "policy": semantic.get("policy"),
            "required_hit_semantics": semantic.get("required_hit_semantics"),
            "specification_source_sha256": source_pins.get(spec_pin),
        },
        "physical": {
            "encoding_id": physical.get("encoding_id"),
            "geometry_family": geometry,
            "schema_sha256": physical.get("schema_sha256"),
            "callback_ir_sha256": callback.get("ir_sha256"),
            "effect_digest": callback.get("effect_digest"),
            "guarantees": physical.get("guarantees"),
            "maps": product_maps,
            "hit_semantics": [
                _mapping(item, "hit_channel").get("semantic")
                for item in _sequence(physical.get("hit_channels"), "hit_channels")
            ],
            "gas": {
                "graph_depth": _mapping(physical.get("gas"), "gas").get(
                    "graph_depth"
                ),
                "sbt_record_stride": _mapping(physical.get("gas"), "gas").get(
                    "sbt_record_stride"
                ),
                "update_policy": _mapping(physical.get("gas"), "gas").get(
                    "update_policy"
                ),
            },
            "buffer_contract_sha256": _canonical_digest(
                list(buffers),
                domain="rtdl.goal5793.x1.reference_buffer_contract",
                version=1,
                projection="goal5789_v1.physical_encoding.buffers",
            )["sha256"],
            "source_manifest": map_manifest,
        },
        "target": {
            "target_sha256": target.get("target_sha256"),
            "provider": target.get("provider"),
            "native_sha256": target.get("native_sha256"),
            "capabilities": target.get("capabilities"),
        },
        "canonical_candidates": [
            {
                "template_id": _mapping(item, "canonical_candidate").get(
                    "template_id"
                ),
                "canonical": _mapping(item, "canonical_candidate").get("canonical"),
                "algorithm_identity": _mapping(
                    item, "canonical_candidate"
                ).get("algorithm_identity"),
                "geometry_family": _mapping(item, "canonical_candidate").get(
                    "geometry_family"
                ),
                "schema_sha256": _mapping(item, "canonical_candidate").get(
                    "schema_sha256"
                ),
                "guarantees": _mapping(item, "canonical_candidate").get(
                    "guarantees"
                ),
            }
            for item in candidates
        ],
    }


def _reference_declaration_verdict(
    result: Mapping[str, object], reference_module
) -> str:
    semantic = _mapping(result.get("semantic_compatible"), "semantic_compatible")
    target = _mapping(result.get("target_capable"), "target_capable")
    canonical = _mapping(result.get("canonical_resolution"), "canonical_resolution")
    values = (
        semantic.get("verdict"),
        target.get("verdict"),
        canonical.get("verdict"),
    )
    if values[0] == reference_module.INCOMPATIBLE \
            or values[1] == reference_module.INCAPABLE \
            or values[2] in {"UNSUPPORTED", "AMBIGUOUS"}:
        return reference_module.INCOMPATIBLE
    if values != (
        reference_module.COMPATIBLE,
        reference_module.CAPABLE,
        "SOLE_CANONICAL_REFERENCE",
    ):
        return reference_module.UNKNOWN
    return reference_module.COMPATIBLE


def _invalid(reasons: list[str], *, disagreement: bool = False) -> dict[str, object]:
    result: dict[str, object] = {
        "schema": RESULT_SCHEMA,
        "status": DISAGREEMENT if disagreement else INFRA_INVALID,
        "final_verdict": None,
        "reasons": sorted(reasons),
        "product_result": None,
        "independent_product_recount": None,
        "reference_overlap_result": None,
        "executable": False,
        "execution_authorized": False,
        "performance_evaluated": False,
        "result_sha256": "",
    }
    result["result_sha256"] = _seal_document(
        result,
        seal_field="result_sha256",
        domain="rtdl.goal5793.x1.generic_examiner_result",
        version=1,
    )
    return result


def _examine_declaration_core(payload: Mapping[str, object]) -> dict[str, object]:
    """Run the declaration layers after the controlling registry gate."""

    try:
        runtime_dependencies, runtime_reasons = _frozen_runtime_dependencies()
    except Exception as exc:
        return _invalid([f"runtime_dependency_rehash_error:{type(exc).__name__}:{exc}"])
    if runtime_reasons:
        return _invalid(runtime_reasons)
    try:
        product_module, reference_module, recount_module = _load_scientific_modules()
    except Exception as exc:
        return _invalid([f"frozen_module_load_error:{type(exc).__name__}:{exc}"])
    if not isinstance(payload, Mapping):
        return _invalid(["input:expected_mapping"])
    forbidden = _find_forbidden(payload)
    if forbidden:
        return _invalid([f"forbidden_decision_input:{path}" for path in forbidden])
    if set(payload) != _TOP_KEYS:
        return _invalid([
            "input_keys_mismatch:",
            f"missing={sorted(_TOP_KEYS - set(payload))}",
            f"extra={sorted(set(payload) - _TOP_KEYS)}",
        ])
    if payload.get("schema") != INPUT_SCHEMA:
        return _invalid(["input_schema_identity"])
    for root_name in (
        "semantic_requirement",
        "physical_guarantee",
        "live_binding",
    ):
        root_value = payload[root_name]
        if root_value is not None and not isinstance(root_value, Mapping):
            return _invalid([
                f"MALFORMED_OUTSIDE_SIGNATURE:{root_name}:expected_mapping_or_none"
            ])
    candidate_root = payload["canonical_candidates"]
    if candidate_root is not None and (
        isinstance(candidate_root, (str, bytes))
        or not isinstance(candidate_root, Sequence)
    ):
        return _invalid([
            "MALFORMED_OUTSIDE_SIGNATURE:canonical_candidates:"
            "expected_sequence_or_none"
        ])
    try:
        try:
            product_result = product_module.evaluate_semantic_physical_admission(
                deepcopy(payload["semantic_requirement"]),
                deepcopy(payload["physical_guarantee"]),
                live_binding=deepcopy(payload["live_binding"]),
                canonical_candidates=deepcopy(payload["canonical_candidates"]),
            ).to_dict()
        except Exception as exc:
            return _invalid([
                f"product_evaluator_exception:{type(exc).__name__}:{exc}"
            ])
        independent_result = recount_module.evaluate_product_schema(
            deepcopy(payload["semantic_requirement"]),
            deepcopy(payload["physical_guarantee"]),
            live_binding=deepcopy(payload["live_binding"]),
            canonical_candidates=deepcopy(payload["canonical_candidates"]),
        )
        product_verdict = product_result["verdict"]
        independent_verdict = independent_result["verdict"]
        product_decision_projection = {
            "verdict": product_verdict,
            "matching_candidate_count": product_result.get(
                "matching_candidate_count"
            ),
            "canonical_template_id": product_result.get("canonical_template_id"),
            "executable": product_result.get("executable"),
        }
        independent_decision_projection = {
            "verdict": independent_verdict,
            "matching_candidate_count": independent_result.get(
                "matching_candidate_count"
            ),
            "canonical_template_id": independent_result.get(
                "canonical_template_id"
            ),
            "executable": independent_result.get("executable"),
        }
    except Exception as exc:
        return _invalid([f"examiner_input_error:{type(exc).__name__}:{exc}"])
    if product_decision_projection != independent_decision_projection:
        result = _invalid([
            "product_independent_recount_decision_projection_disagreement:"
            f"{product_decision_projection!r}:{independent_decision_projection!r}"
        ], disagreement=True)
        result["product_result"] = product_result
        result["independent_product_recount"] = independent_result
        result["result_sha256"] = _seal_document(
            result,
            seal_field="result_sha256",
            domain="rtdl.goal5793.x1.generic_examiner_result",
            version=1,
        )
        return result

    absent_roots = [
        name
        for name in (
            "semantic_requirement",
            "physical_guarantee",
            "live_binding",
            "canonical_candidates",
        )
        if payload[name] is None
    ]
    if absent_roots:
        if product_verdict != "UNKNOWN":
            return _invalid([
                "absent_product_declaration_root_did_not_produce_unknown:",
                f"roots={absent_roots}",
                f"verdict={product_verdict}",
            ])
        reference_result = {
            "status": "NOT_EXPRESSIBLE_IN_GOAL5789_V1__NOT_EVALUATED",
            "absent_product_declaration_roots": absent_roots,
        }
        result = {
            "schema": RESULT_SCHEMA,
            "status": "VALID_LAYERED_EXAMINATION",
            "final_verdict": "UNKNOWN",
            "reasons": [],
            "product_result": product_result,
            "independent_product_recount": independent_result,
            "reference_overlap_result": reference_result,
            "reference_overlap_verdict": "NOT_EVALUATED",
            "runtime_dependencies": runtime_dependencies,
            "layer_contract": {
                "full_product_schema": (
                    "product_evaluator_plus_independent_recount"
                ),
                "goal5789_v1": (
                    "not_expressible_for_absent_product_root__not_evaluated"
                ),
                "combination": (
                    "PRODUCT_UNKNOWN_PRESERVED__NO_SYNTHETIC_V1_DECLARATION"
                ),
            },
            "crosswalk_sha256": None,
            "executable": False,
            "execution_authorized": False,
            "performance_evaluated": False,
            "result_sha256": "",
        }
        result["result_sha256"] = _seal_document(
            result,
            seal_field="result_sha256",
            domain="rtdl.goal5793.x1.generic_examiner_result",
            version=1,
        )
        return result

    try:
        product_projection = _product_projection(payload)
        reference_projection = _reference_projection(payload)
        if product_projection != reference_projection:
            return _invalid(["product_reference_projection_mismatch"])
        reference_result = reference_module.evaluate_certificate(
            deepcopy(payload["reference_certificate"]),
            deepcopy(payload["reference_authority"]),
        )
        reference_verdict = _reference_declaration_verdict(
            reference_result, reference_module
        )
    except Exception as exc:
        return _invalid([f"examiner_input_error:{type(exc).__name__}:{exc}"])
    layered_verdict = product_verdict
    if reference_verdict == reference_module.INCOMPATIBLE:
        layered_verdict = reference_module.INCOMPATIBLE
    elif reference_verdict == reference_module.UNKNOWN \
            and product_verdict == reference_module.COMPATIBLE:
        layered_verdict = reference_module.UNKNOWN
    result = {
        "schema": RESULT_SCHEMA,
        "status": "VALID_LAYERED_EXAMINATION",
        "final_verdict": layered_verdict,
        "reasons": [],
        "product_result": product_result,
        "independent_product_recount": independent_result,
        "reference_overlap_result": reference_result,
        "reference_overlap_verdict": reference_verdict,
        "runtime_dependencies": runtime_dependencies,
        "layer_contract": {
            "full_product_schema": "product_evaluator_plus_independent_recount",
            "goal5789_v1": "overlap_replay_only__not_full_product_schema_authority",
            "extension_axes_independently_recounted": [
                "physical_supported_algorithm_identity",
                "physical_supported_domain_sha256",
                "semantic_physical_orientation_contract_sha256",
                "canonical_candidate_declared_domain_sha256",
                "canonical_candidate_orientation_contract_sha256",
                "live_binding_callback_effect_schema",
                "required_target_capabilities",
            ],
            "combination": "INCOMPATIBLE_DOMINATES_UNKNOWN_DOMINATES_COMPATIBLE",
        },
        "crosswalk_sha256": _canonical_digest(
            product_projection,
            domain="rtdl.goal5793.x1.product_reference_crosswalk",
            version=1,
            projection="shared_declaration_projection",
        )["sha256"],
        "executable": False,
        "execution_authorized": False,
        "performance_evaluated": False,
        "result_sha256": "",
    }
    result["result_sha256"] = _seal_document(
        result,
        seal_field="result_sha256",
        domain="rtdl.goal5793.x1.generic_examiner_result",
        version=1,
    )
    return result


def examine(
    payload: Mapping[str, object],
    registry_receipt: Mapping[str, object] | None = None,
    *,
    registry_authority: Mapping[str, object] | None = None,
    registry_stage_pin: Mapping[str, object] | None = None,
    trusted_stage_pin_sha256: str | None = None,
) -> dict[str, object]:
    """Run the public path under an out-of-band exact registry stage pin.

    The authority and stage pin are intentionally not fields in ``payload``.
    ``trusted_stage_pin_sha256`` must come from the controlling stage
    configuration, not the candidate input.
    """

    if registry_receipt is None:
        return _invalid(["registry_receipt_required_for_controlling_path"])
    if registry_authority is None:
        return _invalid(["external_registry_authority_required"])
    if registry_stage_pin is None:
        return _invalid(["external_registry_stage_pin_required"])
    if trusted_stage_pin_sha256 is None:
        return _invalid(["out_of_band_trusted_stage_pin_required"])
    try:
        registry = _registry_module()
        registry_validation = registry.verify_registered_input(
            deepcopy(payload),
            deepcopy(registry_receipt),
            deepcopy(registry_authority),
            deepcopy(registry_stage_pin),
            trusted_stage_pin_sha256,
        )
    except Exception as exc:
        return _invalid([
            f"registry_derivation_error:{type(exc).__name__}:{exc}"
        ])
    result = _examine_declaration_core(payload)
    result["registry_validation"] = registry_validation
    result["registry_receipt_sha256"] = registry_receipt.get("receipt_sha256")
    result["registry_authority_sha256"] = registry_validation.get(
        "registry_authority_sha256"
    )
    result["registry_stage_pin_sha256"] = registry_validation.get(
        "registry_stage_pin_sha256"
    )
    result["controlling_path"] = (
        "EXACT_REGISTRY_TEMPLATE_AND_SEVEN_SLOTS_THEN_PRODUCT_RECOUNT_V1_OVERLAP"
    )
    result["result_sha256"] = _seal_document(
        result,
        seal_field="result_sha256",
        domain="rtdl.goal5793.x1.generic_examiner_result",
        version=1,
    )
    return result


__all__ = [
    "DECLARATION_RULE_CLASSIFICATION",
    "DISAGREEMENT",
    "FORBIDDEN_DECISION_INPUT_KEYS",
    "INFRA_INVALID",
    "INPUT_SCHEMA",
    "RESULT_SCHEMA",
    "examine",
]
