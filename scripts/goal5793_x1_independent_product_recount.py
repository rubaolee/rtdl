"""Independent mapping-level recount of the V4 declaration admission rules.

This file deliberately imports no product module and no Goal5789-A2 checker.
It covers the product-declared ``Sequence | None`` candidate input domain,
including axes absent from Goal5789-v1.  Malformed outer candidate containers
outside that signature are rejected by the generic examiner before this
recount and are not part of the differential-parity claim.  This module
creates no live authority and has no execution path.
"""

from __future__ import annotations

import re
from typing import Mapping, Sequence


COMPATIBLE = "COMPATIBLE_FOR_DECLARED_DOMAIN"
INCOMPATIBLE = "INCOMPATIBLE"
UNKNOWN = "UNKNOWN"

_SHA256 = re.compile(r"[0-9a-f]{64}")
_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)*")
_POLICY_KEYS = frozenset({
    "input_type", "output_type", "exactness", "tie_policy", "order_policy",
    "multiplicity", "numeric_precision", "overflow_policy",
})
_MAP_GRAPH = {
    "encode": (("semantic_input",), ("geometry", "query_state")),
    "ray": (("query_state",), ("ray",)),
    "trace": (("geometry", "ray"), ("hit_stream",)),
    "continuation": (("hit_stream",), ("candidate_output",)),
    "decode": (("candidate_output",), ("semantic_output",)),
}
_SEMANTIC_KEYS = frozenset({
    "contract_id", "algorithm_identity", "declared_domain_sha256", "policy",
    "required_hit_semantics", "orientation_contract_sha256",
    "specification_source_sha256",
})
_PHYSICAL_KEYS = frozenset({
    "encoding_id", "supported_algorithm_identity", "supported_domain_sha256",
    "orientation_contract_sha256", "geometry_family", "schema_sha256",
    "callback_ir_sha256", "effect_digest", "guarantees", "maps",
    "hit_semantics", "gas_graph_depth", "gas_sbt_record_stride",
    "gas_update_policy", "buffer_contract_sha256",
    "required_target_capabilities", "source_manifest",
})
_BINDING_KEYS = frozenset({
    "callback_ir_sha256", "effect_digest", "family_schema_sha256",
    "target_sha256", "target_provider", "target_capabilities",
    "canonical_artifact_sha256", "canonical_template_id",
    "family_authority_sha256", "family_authority_nonce",
})
_CANDIDATE_KEYS = frozenset({
    "template_id", "canonical", "algorithm_identity", "declared_domain_sha256",
    "orientation_contract_sha256", "geometry_family", "schema_sha256",
    "guarantees",
})


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _is_identifier(value: object) -> bool:
    return isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None


def _mapping(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}:expected_mapping")
    return value


def _sequence(value: object, path: str) -> Sequence[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{path}:expected_sequence")
    return value


def _exact(value: object, keys: frozenset[str], path: str) -> Mapping[str, object]:
    result = _mapping(value, path)
    if set(result) != keys:
        raise ValueError(
            f"{path}:keys:missing={sorted(keys-set(result))}:"
            f"extra={sorted(set(result)-keys)}"
        )
    return result


def _strings(value: object, path: str) -> tuple[str, ...]:
    items = _sequence(value, path)
    if any(not isinstance(item, str) or not item for item in items):
        raise ValueError(f"{path}:expected_nonempty_string_sequence")
    if len(set(items)) != len(items):
        raise ValueError(f"{path}:duplicate_string")
    return tuple(items)


def _plain_int(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{path}:expected_plain_integer")
    return value


def _nonempty_string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path}:expected_nonempty_string")
    return value


def _plain_bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{path}:expected_bool")
    return value


def _string_map(value: object, path: str) -> dict[str, str]:
    result = _mapping(value, path)
    if any(not isinstance(key, str) or not isinstance(item, str)
           for key, item in result.items()):
        raise ValueError(f"{path}:expected_string_map")
    return dict(result)


def _validate_policy(
    value: dict[str, str], path: str, unknown: list[str], bad: list[str]
) -> None:
    missing = sorted(_POLICY_KEYS - set(value))
    extra = sorted(set(value) - _POLICY_KEYS)
    if missing:
        unknown.append(f"{path}:missing:{missing}")
    if extra:
        bad.append(f"{path}:extra:{extra}")


def evaluate_product_schema(
    semantic_requirement: object,
    physical_guarantee: object,
    *,
    live_binding: object,
    canonical_candidates: object,
) -> dict[str, object]:
    """Recount the complete inert product declaration from plain mappings."""

    unknown: list[str] = []
    bad: list[str] = []
    try:
        semantic = None if semantic_requirement is None else _exact(
            semantic_requirement, _SEMANTIC_KEYS, "semantic"
        )
        physical = None if physical_guarantee is None else _exact(
            physical_guarantee, _PHYSICAL_KEYS, "physical"
        )
        binding = None if live_binding is None else _exact(
            live_binding, _BINDING_KEYS, "binding"
        )
        if canonical_candidates is None:
            candidates = None
        else:
            raw_candidates = _sequence(canonical_candidates, "candidates")
            candidates = [
                _exact(item, _CANDIDATE_KEYS, f"candidates[{index}]")
                for index, item in enumerate(raw_candidates)
            ]

        semantic_policy = {} if semantic is None else _string_map(
            semantic["policy"], "semantic.policy"
        )
        physical_policy = {} if physical is None else _string_map(
            physical["guarantees"], "physical.guarantees"
        )
        required_hits = () if semantic is None else _strings(
            semantic["required_hit_semantics"], "semantic.required_hit_semantics"
        )
        hit_semantics = () if physical is None else _strings(
            physical["hit_semantics"], "physical.hit_semantics"
        )
        required_caps = () if physical is None else _strings(
            physical["required_target_capabilities"],
            "physical.required_target_capabilities",
        )
        target_caps = () if binding is None else _strings(
            binding["target_capabilities"], "binding.target_capabilities"
        )
        manifest = {} if physical is None else _string_map(
            physical["source_manifest"], "physical.source_manifest"
        )
        maps = () if physical is None else _sequence(physical["maps"], "physical.maps")
        graph_depth = None if physical is None else _plain_int(
            physical["gas_graph_depth"], "physical.gas_graph_depth"
        )
        sbt_stride = None if physical is None else _plain_int(
            physical["gas_sbt_record_stride"], "physical.gas_sbt_record_stride"
        )
        if semantic is not None:
            for key in (
                "contract_id", "algorithm_identity", "declared_domain_sha256",
                "orientation_contract_sha256", "specification_source_sha256",
            ):
                _nonempty_string(semantic[key], f"semantic.{key}")
        parsed_maps: list[dict[str, object]] = []
        if physical is not None:
            for key in (
                "encoding_id", "supported_algorithm_identity",
                "supported_domain_sha256", "orientation_contract_sha256",
                "geometry_family", "schema_sha256", "callback_ir_sha256",
                "effect_digest", "gas_update_policy", "buffer_contract_sha256",
            ):
                _nonempty_string(physical[key], f"physical.{key}")
            for index, raw in enumerate(maps):
                edge = _exact(
                    raw,
                    frozenset({
                        "kind", "source_id", "source_sha256", "consumes", "produces",
                    }),
                    f"physical.maps[{index}]",
                )
                parsed_maps.append({
                    "kind": _nonempty_string(
                        edge["kind"], f"physical.maps[{index}].kind"
                    ),
                    "source_id": _nonempty_string(
                        edge["source_id"], f"physical.maps[{index}].source_id"
                    ),
                    "source_sha256": _nonempty_string(
                        edge["source_sha256"],
                        f"physical.maps[{index}].source_sha256",
                    ),
                    "consumes": _strings(
                        edge["consumes"], f"physical.maps[{index}].consumes"
                    ),
                    "produces": _strings(
                        edge["produces"], f"physical.maps[{index}].produces"
                    ),
                })
        if binding is not None:
            for key in (
                "callback_ir_sha256", "effect_digest", "family_schema_sha256",
                "target_sha256", "target_provider", "canonical_artifact_sha256",
                "canonical_template_id", "family_authority_sha256",
                "family_authority_nonce",
            ):
                _nonempty_string(binding[key], f"binding.{key}")
        candidate_policies: list[dict[str, str]] = []
        if candidates is not None:
            for index, candidate in enumerate(candidates):
                for key in (
                    "template_id", "algorithm_identity", "declared_domain_sha256",
                    "orientation_contract_sha256", "geometry_family", "schema_sha256",
                ):
                    _nonempty_string(candidate[key], f"candidates[{index}].{key}")
                _plain_bool(candidate["canonical"], f"candidates[{index}].canonical")
                candidate_policies.append(_string_map(
                    candidate["guarantees"], f"candidates[{index}].guarantees"
                ))
    except (KeyError, TypeError, ValueError) as exc:
        return {
            "verdict": INCOMPATIBLE,
            "unknown_reasons": [],
            "incompatible_reasons": [f"malformed_input:{type(exc).__name__}:{exc}"],
            "matching_candidate_count": None,
            "canonical_template_id": None,
            "executable": False,
        }

    if semantic is None:
        unknown.append("semantic_requirement_absent")
    if physical is None:
        unknown.append("physical_guarantee_absent")
    if binding is None:
        unknown.append("live_binding_absent")
    if candidates is None:
        unknown.append("canonical_candidates_absent")

    identifier_rows: list[tuple[str, object]] = []
    if semantic is not None:
        identifier_rows.extend((
            ("semantic.contract_id", semantic["contract_id"]),
            ("semantic.algorithm_identity", semantic["algorithm_identity"]),
        ))
    if physical is not None:
        identifier_rows.extend((
            ("physical.encoding_id", physical["encoding_id"]),
            ("physical.supported_algorithm_identity", physical["supported_algorithm_identity"]),
            ("physical.geometry_family", physical["geometry_family"]),
        ))
    if binding is not None:
        identifier_rows.append(
            ("binding.canonical_template_id", binding["canonical_template_id"])
        )
    for path, value in identifier_rows:
        if not _is_identifier(value):
            bad.append(f"invalid_identifier:{path}")
    digest_rows: list[tuple[str, object]] = []
    if semantic is not None:
        digest_rows.extend((
            ("semantic.declared_domain_sha256", semantic["declared_domain_sha256"]),
            ("semantic.orientation_contract_sha256", semantic["orientation_contract_sha256"]),
            ("semantic.specification_source_sha256", semantic["specification_source_sha256"]),
        ))
    if physical is not None:
        digest_rows.extend((
            ("physical.supported_domain_sha256", physical["supported_domain_sha256"]),
            ("physical.orientation_contract_sha256", physical["orientation_contract_sha256"]),
            ("physical.schema_sha256", physical["schema_sha256"]),
            ("physical.callback_ir_sha256", physical["callback_ir_sha256"]),
            ("physical.effect_digest", physical["effect_digest"]),
            ("physical.buffer_contract_sha256", physical["buffer_contract_sha256"]),
        ))
    if binding is not None:
        digest_rows.extend((
            ("binding.callback_ir_sha256", binding["callback_ir_sha256"]),
            ("binding.effect_digest", binding["effect_digest"]),
            ("binding.family_schema_sha256", binding["family_schema_sha256"]),
            ("binding.target_sha256", binding["target_sha256"]),
            ("binding.canonical_artifact_sha256", binding["canonical_artifact_sha256"]),
            ("binding.family_authority_sha256", binding["family_authority_sha256"]),
        ))
    for path, value in digest_rows:
        if not _is_sha(value):
            bad.append(f"invalid_sha256:{path}")
    if binding is not None and (
        not isinstance(binding["family_authority_nonce"], str)
        or not binding["family_authority_nonce"]
    ):
        bad.append("invalid_binding_nonce")
    if semantic is not None:
        _validate_policy(semantic_policy, "semantic.policy", unknown, bad)
    if physical is not None:
        _validate_policy(physical_policy, "physical.guarantees", unknown, bad)
    if semantic is not None and physical is not None:
        for key in sorted(_POLICY_KEYS & set(semantic_policy) & set(physical_policy)):
            if semantic_policy[key] != physical_policy[key]:
                bad.append(f"policy_mismatch:{key}")
        if semantic["algorithm_identity"] != physical["supported_algorithm_identity"]:
            bad.append("algorithm_identity_mismatch")
        if semantic["declared_domain_sha256"] != physical["supported_domain_sha256"]:
            bad.append("declared_domain_mismatch")
        if semantic["orientation_contract_sha256"] != physical["orientation_contract_sha256"]:
            bad.append("orientation_contract_mismatch")
        missing_hits = sorted(set(required_hits) - set(hit_semantics))
        if missing_hits:
            bad.append(f"required_hit_semantics_missing:{missing_hits}")
    if physical is not None and (
        graph_depth != 1
        or sbt_stride != 1
        or physical["gas_update_policy"] not in {"static", "declared_refit"}
    ):
        bad.append("gas_contract_mismatch")

    seen: set[str] = set()
    used: set[str] = set()
    for edge in parsed_maps:
        kind = edge["kind"]
        source_id = edge["source_id"]
        consumes = edge["consumes"]
        produces = edge["produces"]
        if not isinstance(kind, str) or kind not in _MAP_GRAPH:
            bad.append(f"unknown_map_stage:{kind}")
            continue
        if kind in seen:
            bad.append(f"duplicate_map_stage:{kind}")
            continue
        seen.add(kind)
        if (consumes, produces) != _MAP_GRAPH[kind]:
            bad.append(f"map_graph_mismatch:{kind}")
        used.add(source_id)
        if source_id not in manifest:
            unknown.append(f"map_source_unknown:{kind}")
        elif manifest[source_id] != edge["source_sha256"]:
            bad.append(f"map_source_digest_mismatch:{kind}")
        if not _is_sha(edge["source_sha256"]):
            bad.append(f"invalid_map_source_sha256:{kind}")
    for kind in sorted(set(_MAP_GRAPH) - seen):
        unknown.append(f"missing_map_stage:{kind}")
    unused = sorted(set(manifest) - used)
    if unused:
        bad.append(f"unused_map_sources:{unused}")

    if physical is not None and binding is not None:
        if physical["callback_ir_sha256"] != binding["callback_ir_sha256"] \
                or physical["effect_digest"] != binding["effect_digest"]:
            bad.append("callback_binding_mismatch")
        if physical["schema_sha256"] != binding["family_schema_sha256"]:
            bad.append("family_schema_binding_mismatch")
        missing_caps = sorted(set(required_caps) - set(target_caps))
        if missing_caps:
            bad.append(f"target_capability_missing:{missing_caps}")
    if binding is not None and binding["target_provider"] != "optix":
        bad.append("target_provider_mismatch")

    matches: list[Mapping[str, object]] = []
    for index, candidate in enumerate(candidates or []):
        candidate_policy = candidate_policies[index]
        if not _is_identifier(candidate["template_id"]):
            bad.append(f"invalid_candidate_template_id:{index}")
        for key in ("declared_domain_sha256", "orientation_contract_sha256", "schema_sha256"):
            if not _is_sha(candidate[key]):
                bad.append(f"invalid_candidate_sha256:{index}:{key}")
        if semantic is not None and physical is not None \
                and candidate["canonical"] \
                and candidate["algorithm_identity"] == semantic["algorithm_identity"] \
                and candidate["declared_domain_sha256"] == semantic["declared_domain_sha256"] \
                and candidate["orientation_contract_sha256"] == semantic["orientation_contract_sha256"] \
                and candidate["geometry_family"] == physical["geometry_family"] \
                and candidate["schema_sha256"] == physical["schema_sha256"] \
                and candidate_policy == semantic_policy:
            matches.append(candidate)
    if candidates is not None and semantic is not None and physical is not None:
        if len(matches) == 0:
            bad.append("zero_canonical_matches")
        elif len(matches) > 1:
            bad.append("ambiguous_canonical_matches")
        elif binding is not None \
                and matches[0]["template_id"] != binding["canonical_template_id"]:
            bad.append("canonical_live_binding_mismatch")

    verdict = UNKNOWN if unknown else (INCOMPATIBLE if bad else COMPATIBLE)
    return {
        "verdict": verdict,
        "unknown_reasons": unknown,
        "incompatible_reasons": bad,
        "matching_candidate_count": None if candidates is None else len(matches),
        "canonical_template_id": matches[0]["template_id"] if len(matches) == 1 else None,
        "executable": False,
    }


__all__ = ["COMPATIBLE", "INCOMPATIBLE", "UNKNOWN", "evaluate_product_schema"]
