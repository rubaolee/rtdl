#!/usr/bin/env python3
"""Final Goal5799-A2 authority closure and executable exposure matcher.

This verifier uses only the Python standard library.  It hard-pins the sole
authorized A1 contract/registry/receipt authorities, explicitly separates
whole-file identity coverage from semantic-invariant coverage, and can verify
all required payloads directly from the sole A2 CFR.
"""

from __future__ import annotations

import argparse
import base64
import copy
import gzip
import hashlib
import html
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"

A1_CFR = HISTORY / "call_for_review_goal5799_a1_post_self_review_closure_and_goal5800_5801_entry_20260824.md"
A1_CONTRACT = HISTORY / "goal5799_a1_repaired_performance_and_evidence_contract_20260824.json"
A1_REGISTRY = HISTORY / "goal5799_a1_exposure_registry_alias_and_count_amendment_20260824.json"
A1_BRIDGE = HISTORY / "goal5799_a1_v11_cold_receipt_bridge_20260824.json"
V1_LEDGER = HISTORY / "goal5799_v11_cold_phase_ledger_20260824.json"
A1_INDEPENDENT = HISTORY / "goal5799_a1_independent_verification_20260824.json"

RESULT = HISTORY / "goal5799_a2_final_authority_and_matcher_result_20260824.json"
SELF_REVIEW = HISTORY / "self_review_goal5799_a2_final_authority_and_matcher_20260824.md"
CFR = HISTORY / "call_for_review_goal5799_a2_final_authority_and_matcher_closure_20260824.md"

AUTHORIZED = {
    "a1_cfr": (13_394_576, "915f52e8b8253296284374f7120b1de222009d6fdcea8b1bcfd0c7ffc46bbe14"),
    "contract": (49_187, "1e5de461860713c70885b88c082bcb97ba0eb6abb451897ae44263ee3bd46d08"),
    "registry": (138_846, "87e8e02b48867cdfac15f113eb27cf1c11a7ed042971609e5a46aafda93838fb"),
    "bridge": (3_004_797, "f21aadf5c1596b97db5ffe7001f555f8ddf443e1a15b569d6cc1eb7d71946ad2"),
    "ledger": (99_976, "1ef0786ff9f48bb9cb806c0d6ab3423f953cc907b1758a2a885552f75bf648c3"),
    "a1_independent": (1_440, "6983e03fb2357f13fa443a992b54ce1a25f8dae20518ea26fe87162ebc8c4184"),
}

CANONICALIZATION = "UTF8_SORTED_KEYS_COMPACT_ENSURE_ASCII_FALSE_ALLOW_NAN_FALSE_NO_TRAILING_NEWLINE_V1"
DOMAIN = "rtdl.goal5799.a1.post_self_review_repair"
A2_DOMAIN = "rtdl.goal5799.a2.final_authority_and_matcher"


class A2Error(ValueError):
    """Stable fail-closed A2 error."""


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def seal(document: Mapping[str, Any], *, field: str, domain: str) -> str:
    body = dict(document)
    body.pop(field, None)
    framed = {
        "canonicalization": CANONICALIZATION,
        "domain": domain,
        "projection": f"document_without:{field}",
        "value": body,
        "version": 1,
    }
    return sha(canonical(framed))


def identity(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(payload), "sha256": sha(payload)}


def _verify_local_pin(path: Path, key: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise A2Error(f"PINNED_INPUT_NOT_REGULAR:{key}")
    payload = path.read_bytes()
    expected_bytes, expected_sha = AUTHORIZED[key]
    if len(payload) != expected_bytes or sha(payload) != expected_sha:
        raise A2Error(f"PINNED_INPUT_IDENTITY_MISMATCH:{key}")
    return payload


def _walk(value: Any, path: tuple[Any, ...] = ()) -> Iterable[tuple[tuple[Any, ...], Any]]:
    if isinstance(value, Mapping):
        for key in sorted(value, key=lambda item: str(item).encode("utf-8")):
            yield from _walk(value[key], path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, path + (index,))
    else:
        yield path, value


def _pointer(path: tuple[Any, ...]) -> str:
    return "/" + "/".join(str(item).replace("~", "~0").replace("/", "~1") for item in path)


def _manifest(semantic: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "path": _pointer(path),
            "classification": "EXACT_IDENTITY_BOUND__MUTATION_MUST_REJECT",
            "expected_value_sha256": sha(canonical(value)),
            "expected_type": type(value).__name__,
        }
        for path, value in _walk(semantic)
    ]


def _parse_canonical(payload: bytes, reason: str) -> dict[str, Any]:
    try:
        document = json.loads(payload)
    except Exception as exc:  # noqa: BLE001
        raise A2Error(f"{reason}_JSON_INVALID") from exc
    if payload != canonical(document) + b"\n":
        raise A2Error(f"{reason}_NONCANONICAL")
    return document


def _get(document: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = document
    for key in path:
        if not isinstance(value, Mapping) or key not in value:
            raise A2Error(f"CONTRACT_REQUIRED_PATH_MISSING:{'/'.join(path)}")
        value = value[key]
    return value


def verify_contract_payload(payload: bytes, supplied_expected_sha256: str) -> dict[str, Any]:
    authorized_sha = AUTHORIZED["contract"][1]
    if supplied_expected_sha256 != authorized_sha:
        raise A2Error("CONTRACT_EXPECTED_IDENTITY_NOT_AUTHORIZED")
    if len(payload) != AUTHORIZED["contract"][0] or sha(payload) != authorized_sha:
        raise A2Error("CONTRACT_ACTUAL_IDENTITY_MISMATCH")
    document = _parse_canonical(payload, "CONTRACT")
    if document.get("contract_sha256") != seal(document, field="contract_sha256", domain=f"{DOMAIN}.contract.v1"):
        raise A2Error("CONTRACT_INTERNAL_SEAL_MISMATCH")
    semantic = {
        key: copy.deepcopy(value)
        for key, value in document.items()
        if key not in {"control_leaf_manifest", "contract_sha256"}
    }
    rows = _manifest(semantic)
    expected_manifest = {
        "scope": "every populated leaf in the semantic body excluding this manifest and the self-seal",
        "leaf_count": len(rows),
        "non_decision_bearing_leaf_count": 0,
        "rows": rows,
        "rows_sha256": sha(canonical(rows)),
    }
    if document.get("control_leaf_manifest") != expected_manifest or len(rows) != 170:
        raise A2Error("CONTRACT_MANIFEST_MISMATCH")
    required = {
        ("publication", "v11_withdrawal_sentence"): (
            "The initially favorable prepared comparison was withdrawn after review found avoidable per-element "
            "Python work in the PyOptiX arm; the correction removes an RTDL-favorable measurement bias."
        ),
        ("baselines", "OWL", "minimum_residual_mechanisms_required"): 3,
        ("structural_cache_hit_assertions", "cache_hit_imports_numba"): False,
        ("structural_cache_hit_assertions", "cache_hit_invokes_nvrtc"): False,
        ("structural_cache_hit_assertions", "cache_hit_invokes_rtdl_compiler_or_codegen"): False,
        ("anonymity", "artifact_evidence_gate", "owner"): "PROJECT_OWNER_OF_RECORD",
        ("anonymity", "manuscript_gate", "owner"): "PROJECT_OWNER_OF_RECORD",
        ("comparative_gates", "STEADY_E2E", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.05",
        ("comparative_gates", "PREPARE", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
        ("comparative_gates", "DEPLOYMENT_COLD", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
        ("authorization", "goal5802_formal_worker_zero"): False,
        ("authorization", "goal5802_pod_gpu_timing"): False,
        ("authorization", "goal5803"): False,
        ("authorization", "network_provider_query"): False,
        ("authorization", "external_contact_or_participant"): False,
        ("authorization", "submission_or_public_claim"): False,
    }
    for path, expected in required.items():
        if _get(document, path) != expected:
            raise A2Error(f"CONTRACT_REQUIRED_VALUE_MISMATCH:{'/'.join(path)}")
    incomplete = document.get("goal5802_not_yet_frozen__all_block_formal_worker_zero")
    if not isinstance(incomplete, list) or len(incomplete) != 13 or len(set(incomplete)) != 13:
        raise A2Error("GOAL5802_BLOCKING_OBLIGATION_SET_MISMATCH")
    return {
        "authorized_file_sha256": authorized_sha,
        "identity_bound_leaf_count": 170,
        "declared_identity_exemption_count": 0,
        "semantic_invariant_paths_checked": len(required) + 1,
        "independent_liveness_claim_for_all_170_leaves": False,
    }


def verify_registry_payload(payload: bytes, supplied_expected_sha256: str) -> dict[str, Any]:
    authorized_sha = AUTHORIZED["registry"][1]
    if supplied_expected_sha256 != authorized_sha:
        raise A2Error("REGISTRY_EXPECTED_IDENTITY_NOT_AUTHORIZED")
    if len(payload) != AUTHORIZED["registry"][0] or sha(payload) != authorized_sha:
        raise A2Error("REGISTRY_ACTUAL_IDENTITY_MISMATCH")
    document = _parse_canonical(payload, "REGISTRY")
    if document.get("amendment_sha256") != seal(
        document, field="amendment_sha256", domain=f"{DOMAIN}.registry_amendment.v1"
    ):
        raise A2Error("REGISTRY_INTERNAL_SEAL_MISMATCH")
    counts = document.get("counts")
    if counts != {
        "alias_components": 194,
        "multi_record_alias_components": 5,
        "provider_records": 200,
        "records_in_multi_record_alias_components": 11,
        "selection_eligible_records": 0,
        "terminal_pdf_conservative_alias_rows": 2,
    }:
        raise A2Error("REGISTRY_COUNTS_MISMATCH")
    if document.get("terminology", {}).get("semantic_unique_scientific_work_count") != "UNKNOWN__NOT_INFERRED_FROM_PROVIDER_RECORD_COUNT":
        raise A2Error("REGISTRY_UNIQUE_WORK_CLAIM_INVALID")
    if any(row.get("selection_eligible") is not False for row in document.get("rows", [])):
        raise A2Error("REGISTRY_ELIGIBLE_ROW")
    return {
        "authorized_file_sha256": authorized_sha,
        "provider_records": 200,
        "unique_openalex_ids": len({row["openalex"] for row in document["rows"]}),
        "alias_components": 194,
        "selection_eligible_records": 0,
        "semantic_unique_work_count": "UNKNOWN",
    }


def _phase_row(receipt: Mapping[str, Any]) -> dict[str, Any]:
    durations = receipt["durations_ns"]
    wall = durations["controller_process_wall_ns"]
    input_ns = durations["input_materialization_ns"]
    prepare_ns = durations["common_preparation_total_ns"]
    execute_ns = sum(durations["complete_execute_ns"])
    close_raw = durations["close_ns"]
    close_ns = 0 if close_raw is None else close_raw
    direct = input_ns + prepare_ns + execute_ns + close_ns
    residual = wall - direct
    if residual < 0:
        raise A2Error("BRIDGE_NEGATIVE_RESIDUAL")
    return {
        "worker_id": receipt["worker_id"],
        "task": receipt["task"],
        "arm": receipt["arm"],
        "sample_index": receipt["row_sample_index"],
        "wall_ns": wall,
        "phases_ns": {
            "input_materialization_ns": input_ns,
            "common_preparation_total_ns": prepare_ns,
            "complete_execute_ns": execute_ns,
            "close_ns": close_ns,
            "controller_process_envelope_residual_ns": residual,
        },
        "close_observation": "NOT_EMITTED_BY_ARM__COUNTED_AS_ZERO_NOT_INFERRED" if close_raw is None else "DIRECTLY_METERED",
        "directly_metered_ns": direct,
        "directly_metered_fraction": direct / wall,
        "named_accounting_fraction": 1.0,
        "source_receipt_sha256": receipt["receipt_sha256"],
    }


def verify_bridge_payload(
    payload: bytes,
    supplied_expected_sha256: str,
    ledger_payload: bytes,
) -> dict[str, Any]:
    authorized_sha = AUTHORIZED["bridge"][1]
    if supplied_expected_sha256 != authorized_sha:
        raise A2Error("BRIDGE_EXPECTED_IDENTITY_NOT_AUTHORIZED")
    if len(payload) != AUTHORIZED["bridge"][0] or sha(payload) != authorized_sha:
        raise A2Error("BRIDGE_ACTUAL_IDENTITY_MISMATCH")
    if len(ledger_payload) != AUTHORIZED["ledger"][0] or sha(ledger_payload) != AUTHORIZED["ledger"][1]:
        raise A2Error("LEDGER_IDENTITY_MISMATCH")
    document = _parse_canonical(payload, "BRIDGE")
    ledger = _parse_canonical(ledger_payload, "LEDGER")
    if document.get("bridge_sha256") != seal(document, field="bridge_sha256", domain=f"{DOMAIN}.receipt_bridge.v1"):
        raise A2Error("BRIDGE_INTERNAL_SEAL_MISMATCH")
    compressed = base64.b64decode(document["compressed_container_base64"], validate=True)
    compression = document["compression"]
    if len(compressed) != compression["compressed_bytes"] or sha(compressed) != compression["compressed_sha256"]:
        raise A2Error("BRIDGE_COMPRESSED_IDENTITY_MISMATCH")
    raw_container = gzip.decompress(compressed)
    if len(raw_container) != compression["uncompressed_bytes"] or sha(raw_container) != compression["uncompressed_sha256"]:
        raise A2Error("BRIDGE_UNCOMPRESSED_IDENTITY_MISMATCH")
    container = _parse_canonical(raw_container, "RECEIPT_CONTAINER")
    entries = container["entries"]
    if len(entries) != 144:
        raise A2Error("BRIDGE_RECEIPT_COUNT_MISMATCH")
    phase_rows = []
    cells = Counter()
    raw_bytes = 0
    for entry in entries:
        raw = base64.b64decode(entry["raw_base64"], validate=True)
        if len(raw) != entry["raw_bytes"] or sha(raw) != entry["raw_sha256"]:
            raise A2Error("BRIDGE_RAW_RECEIPT_IDENTITY_MISMATCH")
        raw_bytes += len(raw)
        receipt = json.loads(raw)
        if receipt.get("mode") != "COLD_FRESH_PROCESS":
            raise A2Error("BRIDGE_NONCOLD_RECEIPT")
        phase_rows.append(_phase_row(receipt))
        cells[(receipt["task"], receipt["arm"])] += 1
    if phase_rows != ledger["rows"] or len(cells) != 6 or set(cells.values()) != {24}:
        raise A2Error("BRIDGE_PHASE_RECOUNT_MISMATCH")
    coverages = [row["directly_metered_fraction"] for row in phase_rows]
    return {
        "authorized_file_sha256": authorized_sha,
        "raw_receipts": 144,
        "raw_receipt_bytes": raw_bytes,
        "cells": 6,
        "samples_per_cell": 24,
        "coverage_min": min(coverages),
        "coverage_max": max(coverages),
        "coverage_below_0_95": sum(value < 0.95 for value in coverages),
        "new_timing_samples": 0,
    }


def _normalize_text(value: str) -> str:
    text = html.unescape(value)
    text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ").replace("&", " and ")
    text = unicodedata.normalize("NFKC", text).casefold()
    text = "".join(char if char.isalnum() else " " for char in text)
    return " ".join(text.split())


def _normalize_author(value: str) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    if "," in value:
        family = _normalize_text(value.split(",", 1)[0])
        return family.split()[-1] if family else ""
    return text.split()[-1]


def fallback_sha256(title: str, first_author: str, year: int) -> str:
    if type(year) is not int or not 1000 <= year <= 9999:
        raise A2Error("MATCHER_YEAR_INVALID")
    return sha(canonical({"first_author": _normalize_author(first_author), "title": _normalize_text(title), "year": year}))


def normalize_query_aliases(query: Mapping[str, Any]) -> set[tuple[str, str]]:
    if not isinstance(query, Mapping) or set(query) - {"doi", "arxiv", "openalex", "fallback_sha256", "fallback_source"}:
        raise A2Error("MATCHER_QUERY_SCHEMA_INVALID")
    aliases: set[tuple[str, str]] = set()
    for raw in query.get("doi", []):
        if not isinstance(raw, str):
            raise A2Error("MATCHER_DOI_INVALID")
        value = re.sub(r"(?i)^doi:\s*", "", raw.strip())
        value = re.sub(r"(?i)^https?://(?:dx\.)?doi\.org/", "", value).lower()
        if not value.startswith("10.") or "/" not in value or re.search(r"\s", value):
            raise A2Error("MATCHER_DOI_INVALID")
        aliases.add(("doi", value))
        if value.endswith("/pdf"):
            aliases.add(("doi", value[:-4]))
    for raw in query.get("arxiv", []):
        if not isinstance(raw, str):
            raise A2Error("MATCHER_ARXIV_INVALID")
        value = raw.strip().lower()
        value = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", value)
        value = re.sub(r"(?i)^arxiv:\s*", "", value).removesuffix(".pdf")
        value = re.sub(r"v[0-9]+$", "", value)
        if re.fullmatch(r"(?:[a-z-]+(?:\.[a-z-]+)?/\d{7}|\d{4}\.\d{4,5})", value) is None:
            raise A2Error("MATCHER_ARXIV_INVALID")
        aliases.add(("arxiv", value))
    for raw in query.get("openalex", []):
        if not isinstance(raw, str):
            raise A2Error("MATCHER_OPENALEX_INVALID")
        match = re.search(r"(?i)(?:^|/)(W[0-9]+)$", raw.strip())
        if match is None:
            raise A2Error("MATCHER_OPENALEX_INVALID")
        aliases.add(("openalex", match.group(1).upper()))
    for raw in query.get("fallback_sha256", []):
        if not isinstance(raw, str) or re.fullmatch(r"[0-9a-f]{64}", raw) is None:
            raise A2Error("MATCHER_FALLBACK_INVALID")
        aliases.add(("fallback_sha256", raw))
    source = query.get("fallback_source")
    if source is not None:
        if not isinstance(source, Mapping) or set(source) != {"title", "first_author", "year"}:
            raise A2Error("MATCHER_FALLBACK_SOURCE_INVALID")
        if not isinstance(source["title"], str) or not isinstance(source["first_author"], str):
            raise A2Error("MATCHER_FALLBACK_SOURCE_INVALID")
        aliases.add(("fallback_sha256", fallback_sha256(source["title"], source["first_author"], source["year"])))
    if not aliases:
        raise A2Error("MATCHER_QUERY_HAS_NO_IDENTITY")
    return aliases


def build_exposure_index(registry: Mapping[str, Any]) -> dict[tuple[str, str], set[int]]:
    index: dict[tuple[str, str], set[int]] = {}
    for row in registry["rows"]:
        if row.get("selection_eligible") is not False:
            raise A2Error("MATCHER_REGISTRY_ELIGIBILITY_INVALID")
        for alias in row["matching_aliases"]:
            kind = "doi" if alias["kind"] == "doi_conservative_terminal_pdf_stripped" else alias["kind"]
            index.setdefault((kind, alias["value"]), set()).add(row["ordinal"])
    return index


def match_exposure(query: Mapping[str, Any], registry: Mapping[str, Any]) -> dict[str, Any]:
    aliases = normalize_query_aliases(query)
    index = build_exposure_index(registry)
    matched = sorted({ordinal for alias in aliases for ordinal in index.get(alias, set())})
    return {
        "exposed": bool(matched),
        "selection_eligible": False if matched else None,
        "matched_ordinals": matched,
        "disposition": "EXPOSED__SELECTION_INELIGIBLE__NO_RESCUE" if matched else "NO_REGISTERED_ALIAS_MATCH__NOT_A_GENERALIZATION_CLAIM",
    }


def _mutated_value(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if type(value) is int:
        return value + 1
    if isinstance(value, float):
        return value + 0.125
    if value is None:
        return "MUTATED"
    return str(value) + "__MUTATED"


def _set_path(document: Any, path: tuple[Any, ...], value: Any) -> None:
    current = document
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


def _rebuild_contract_authorities(document: dict[str, Any]) -> bytes:
    semantic = {
        key: copy.deepcopy(value)
        for key, value in document.items()
        if key not in {"control_leaf_manifest", "contract_sha256"}
    }
    rows = _manifest(semantic)
    document["control_leaf_manifest"] = {
        "scope": "every populated leaf in the semantic body excluding this manifest and the self-seal",
        "leaf_count": len(rows),
        "non_decision_bearing_leaf_count": 0,
        "rows": rows,
        "rows_sha256": sha(canonical(rows)),
    }
    document["contract_sha256"] = seal(document, field="contract_sha256", domain=f"{DOMAIN}.contract.v1")
    return canonical(document) + b"\n"


def run_changed_expected_attack_matrix(contract_payload: bytes) -> dict[str, Any]:
    contract = _parse_canonical(contract_payload, "CONTRACT_ATTACK_SOURCE")
    semantic = {
        key: value
        for key, value in contract.items()
        if key not in {"control_leaf_manifest", "contract_sha256"}
    }
    rows = []
    for path, old_value in _walk(semantic):
        mutated = copy.deepcopy(contract)
        _set_path(mutated, path, _mutated_value(old_value))
        forged_payload = _rebuild_contract_authorities(mutated)
        forged_sha = sha(forged_payload)
        try:
            verify_contract_payload(forged_payload, forged_sha)
        except A2Error as exc:
            reason = str(exc)
        else:
            raise A2Error(f"CHANGED_EXPECTED_ATTACK_ACCEPTED:{_pointer(path)}")
        if reason != "CONTRACT_EXPECTED_IDENTITY_NOT_AUTHORIZED":
            raise A2Error(f"CHANGED_EXPECTED_ATTACK_WRONG_REASON:{_pointer(path)}:{reason}")
        rows.append({"path": _pointer(path), "forged_sha256": forged_sha, "reason": reason})
    if len(rows) != 170:
        raise A2Error("CHANGED_EXPECTED_ATTACK_COUNT_MISMATCH")
    return {
        "attack_count": len(rows),
        "rejected_count": len(rows),
        "accepted_count": 0,
        "reason": "CONTRACT_EXPECTED_IDENTITY_NOT_AUTHORIZED",
        "rows_sha256": sha(canonical(rows)),
        "rows": rows,
    }


def _extract(text: str, title: str) -> bytes:
    start = text.index("## Embedded: " + title)
    match = re.search(r"(?m)^(`{8,})[^\n]*\n", text[start:])
    if match is None:
        raise A2Error(f"CFR_EMBED_FENCE_MISSING:{title}")
    fence = match.group(1)
    body_start = start + match.end()
    body_end = text.index(fence, body_start)
    return text[body_start:body_end].encode("utf-8")


def verify_sole_cfr_payload(cfr_payload: bytes) -> dict[str, Any]:
    text = cfr_payload.decode("utf-8", errors="strict")
    contract_payload = _extract(text, "A1 hard-authorized contract")
    registry_payload = _extract(text, "A1 hard-authorized exposure registry")
    bridge_payload = _extract(text, "A1 hard-authorized receipt bridge")
    ledger_payload = _extract(text, "immutable phase ledger required by receipt recount")
    contract = verify_contract_payload(contract_payload, AUTHORIZED["contract"][1])
    registry = verify_registry_payload(registry_payload, AUTHORIZED["registry"][1])
    bridge = verify_bridge_payload(bridge_payload, AUTHORIZED["bridge"][1], ledger_payload)
    return {
        "contract": contract,
        "registry": registry,
        "bridge": bridge,
        "standard_library_only": True,
        "requires_repository_files": False,
        "requires_shared_canonical_helper": False,
    }


def build_result() -> dict[str, Any]:
    a1_cfr_payload = _verify_local_pin(A1_CFR, "a1_cfr")
    contract_payload = _verify_local_pin(A1_CONTRACT, "contract")
    registry_payload = _verify_local_pin(A1_REGISTRY, "registry")
    bridge_payload = _verify_local_pin(A1_BRIDGE, "bridge")
    ledger_payload = _verify_local_pin(V1_LEDGER, "ledger")
    _verify_local_pin(A1_INDEPENDENT, "a1_independent")
    contract = verify_contract_payload(contract_payload, AUTHORIZED["contract"][1])
    registry = verify_registry_payload(registry_payload, AUTHORIZED["registry"][1])
    bridge = verify_bridge_payload(bridge_payload, AUTHORIZED["bridge"][1], ledger_payload)
    registry_document = json.loads(registry_payload)
    matcher_checks = {
        "all_200_openalex_rows_match": all(
            match_exposure({"openalex": [row["openalex"]]}, registry_document)["exposed"]
            for row in registry_document["rows"]
        ),
        "doi_base_matches_terminal_pdf_component": match_exposure(
            {"doi": ["10.1051/0004-6361/201936150"]}, registry_document
        )["exposed"],
        "doi_terminal_pdf_matches": match_exposure(
            {"doi": ["https://doi.org/10.1051/0004-6361/201936150/pdf"]}, registry_document
        )["exposed"],
        "unknown_openalex_does_not_match": not match_exposure(
            {"openalex": ["W999999999999999999"]}, registry_document
        )["exposed"],
    }
    if set(matcher_checks.values()) != {True}:
        raise A2Error("MATCHER_CHECK_FAILED")
    attacks = run_changed_expected_attack_matrix(contract_payload)
    # Reproduce the subagent's strongest predecessor forgery exactly.
    forged = json.loads(contract_payload)
    forged["publication"]["v11_withdrawal_sentence"] = ""
    forged_payload = _rebuild_contract_authorities(forged)
    if len(forged_payload) != 48_998 or sha(forged_payload) != "eee7d44667d05345c0e15d5673902a176e6c32c1e4d5f4425099ffe0ad0f9678":
        raise A2Error("SUBAGENT_COUNTEREXAMPLE_REPRODUCTION_MISMATCH")
    try:
        verify_contract_payload(forged_payload, sha(forged_payload))
    except A2Error as exc:
        if str(exc) != "CONTRACT_EXPECTED_IDENTITY_NOT_AUTHORIZED":
            raise
    else:
        raise A2Error("SUBAGENT_COUNTEREXAMPLE_NOT_REJECTED")
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.a2.final_authority_and_matcher_result.v1",
        "date": "2026-08-24",
        "status": "PASS__A2_HARD_AUTHORITY_AND_MATCHER_LOCAL_CLOSURE__EXTERNAL_REVIEW_PENDING",
        "predecessor_a1_cfr": {"bytes": len(a1_cfr_payload), "sha256": sha(a1_cfr_payload)},
        "subagent_a1_verdict": "P0_0__P1_1__P2_3__P3_1",
        "subagent_p1_counterexample": {
            "mutation": "publication.v11_withdrawal_sentence = empty string",
            "forged_bytes": len(forged_payload),
            "forged_sha256": sha(forged_payload),
            "a2_disposition": "REJECT__CONTRACT_EXPECTED_IDENTITY_NOT_AUTHORIZED",
        },
        "authority": {
            "hard_pinned_contract_sha256": AUTHORIZED["contract"][1],
            "hard_pinned_registry_sha256": AUTHORIZED["registry"][1],
            "hard_pinned_bridge_sha256": AUTHORIZED["bridge"][1],
            "changed_expected_hash_can_reauthorize_successor": False,
        },
        "coverage_names": {
            "identity_bound_leaf_count": 170,
            "declared_identity_exemption_count": 0,
            "all_170_independently_semantic_liveness_tested": False,
            "semantic_invariant_paths_independently_checked": contract["semantic_invariant_paths_checked"],
        },
        "changed_expected_attack_matrix": attacks,
        "registry": registry,
        "matcher": {
            "schema": "match-any normalized DOI/arXiv/OpenAlex/fallback alias",
            "normalization_implemented_in_standard_library_only_verifier": True,
            "checks": matcher_checks,
            "goal5803_authorized": False,
        },
        "receipt_bridge": bridge,
        "sole_cfr_verifier": {
            "standard_library_only": True,
            "repository_files_required_after_extraction": False,
            "shared_canonical_helper_required": False,
        },
        "scientific_state": {
            "generalization_exam_count": 0,
            "external_v4_author_count": 0,
            "usability_study_count": 0,
            "executable_owl_residual_mechanisms": 0,
            "performance_noninferiority_established": False,
        },
        "authorization": {
            "goal5800_local_untimed": True,
            "goal5801_local_untimed": True,
            "goal5802_formal_worker_zero": False,
            "goal5802_gpu_pod_timing": False,
            "goal5803": False,
            "network": False,
            "participant": False,
            "submission_or_public_claim": False,
        },
        "result_sha256": "",
    }
    document["result_sha256"] = seal(document, field="result_sha256", domain=f"{A2_DOMAIN}.result.v1")
    return document


def build_self_review(result: Mapping[str, Any]) -> bytes:
    text = f"""# Strict self-review — Goal5799-A2 final authority and matcher closure (2026-08-24)

## Verdict

**PASS at local A2 scope; independent subagent re-review still required.** A1's P1 is admitted, reproduced and repaired append-only.

## Exact correction

A1 incorrectly claimed all 17 changed-authority attacks were rejected on semantic invariants. The independent subagent showed that the A1 verifier accepted an empty permanent-withdrawal sentence and four related forgeries when the attacker supplied a new expected SHA. A2 reproduces the strongest forged file exactly: 48,998 bytes, SHA-256 `eee7d44667d05345c0e15d5673902a176e6c32c1e4d5f4425099ffe0ad0f9678`.

A2 makes the trust root explicit: exactly one contract SHA, one registry SHA and one bridge SHA are authorized. A caller-supplied changed expected SHA cannot create authority. All {result['changed_expected_attack_matrix']['attack_count']} semantic-leaf mutations rebuild their 170-row manifest, recompute the internal seal and pass their own forged SHA as expected; all {result['changed_expected_attack_matrix']['rejected_count']} reject with `CONTRACT_EXPECTED_IDENTITY_NOT_AUTHORIZED`.

## No category inflation

The accurate phrase is **170 identity-bound leaves / 0 declared identity exemptions**. It is not “170 independently semantic-liveness-tested leaves.” A2 independently checks {result['coverage_names']['semantic_invariant_paths_independently_checked']} critical invariant paths; the exact whole-file authority binds every remaining byte.

## Matcher and one-file verifier

The match-any-alias rule is now executable with exact DOI/arXiv/OpenAlex/fallback normalization. All 200 OpenAlex rows match and remain ineligible; base and terminal-`/pdf` DOI forms match conservatively. This still does not authorize Goal5803 or create generalization evidence.

The A2 verifier uses only the standard library. Given the sole CFR, it extracts the hard-authorized contract, registry, receipt bridge and immutable ledger; it needs no repository file and no shared canonical helper.

## Locks

Scientific evidence remains 0/0/0/0/not-established for generalization/external author/usability/OWL/performance. Goal5802 workers, GPU/POD timing, Goal5803, network, participant and submission/public claims remain false.

Local result seal: `{result['result_sha256']}`.
"""
    return text.encode("utf-8")


def _embed(title: str, path: Path, language: str) -> str:
    payload = path.read_bytes()
    body = payload.decode("utf-8", errors="strict")
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", body)), default=0)
    fence = "`" * max(8, longest + 1)
    item = identity(path)
    return (
        f"\n## Embedded: {title}\n\n"
        f"`{item['path']}` — {item['bytes']:,} bytes — SHA-256 `{item['sha256']}`\n\n"
        f"{fence}{language}\n{body}"
        + ("\n" if not body.endswith("\n") else "")
        + f"{fence}\n"
    )


def build_cfr(result: Mapping[str, Any]) -> bytes:
    header = f"""# SEND ONLY THIS FILE — Goal5799-A2 final authority and matcher closure

**This supersedes A1 for sending. Send only this Markdown file.** A1 remains embedded and immutable evidence of the independently found P1.

## Requested verdict

Return `P0 / P1 / P2 / P3` and answer:

1. Does hard-pinning the sole authorized A1 contract/registry/bridge identities close the changed-expected-hash P1?
2. Does the 170/170 coordinated mutation+manifest+reseal+changed-expected matrix genuinely reject, including the exact `eee7d446…` counterexample?
3. Are identity coverage and independent semantic-invariant coverage now named without conflation?
4. Is the executable match-any-alias normalization conservative and sufficient while Goal5803 remains locked?
5. Can the standard-library-only verifier operate from this sole CFR without repository files or the shared canonical helper and reproduce all 144 phase rows?
6. May Goal5799 be considered locally complete with P0=0/P1=0, while Goal5800/5801 only may proceed locally and untimed?

## Result

- Hard-authorized contract: `{AUTHORIZED['contract'][1]}`.
- Identity-bound semantic leaves: **170**; declared exemptions: **0**; independent all-leaf semantic-liveness claim: **false**.
- Changed-expected coordinated attacks: **170/170 rejected**.
- Registry: **200 records / 194 components / 0 eligible / semantic unique count UNKNOWN**.
- Receipt bridge: **144 exact receipts / 0 new timings**.
- New scientific evidence: **none**.

Local result seal: `{result['result_sha256']}`.
"""
    parts = [header]
    parts.append(_embed("A1 predecessor CFR — superseded for sending", A1_CFR, "markdown"))
    parts.append(_embed("A1 hard-authorized contract", A1_CONTRACT, "json"))
    parts.append(_embed("A1 hard-authorized exposure registry", A1_REGISTRY, "json"))
    parts.append(_embed("A1 hard-authorized receipt bridge", A1_BRIDGE, "json"))
    parts.append(_embed("immutable phase ledger required by receipt recount", V1_LEDGER, "json"))
    parts.append(_embed("A1 independent verifier result containing the superseded weakness", A1_INDEPENDENT, "json"))
    parts.append(_embed("A2 final authority and matcher result", RESULT, "json"))
    parts.append(_embed("A2 strict self-review", SELF_REVIEW, "markdown"))
    parts.append(_embed("A2 standard-library-only verifier and builder", Path(__file__).resolve(), "python"))
    parts.append(_embed("A2 hostile tests", ROOT / "tests/goal5799_a2_final_authority_and_matcher_test.py", "python"))
    parts.append(
        "\n## Required return format\n\nCommit one review Markdown file naming this CFR SHA-256, exact verdict and every requested answer. A favorable review does not start Goal5802 or Goal5803.\n"
    )
    return "".join(parts).encode("utf-8")


def _write(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise A2Error(f"CREATE_ONLY_OUTPUT_EXISTS:{path.name}")
    with path.open("xb") as stream:
        stream.write(payload)


def write_create_only() -> dict[str, Any]:
    for path in (RESULT, SELF_REVIEW, CFR):
        if path.exists() or path.is_symlink():
            raise A2Error(f"CREATE_ONLY_OUTPUT_EXISTS:{path.name}")
    result = build_result()
    _write(RESULT, canonical(result) + b"\n")
    _write(SELF_REVIEW, build_self_review(result))
    _write(CFR, build_cfr(result))
    return {"status": "CREATE_ONLY_WRITE_PASS", "outputs": [identity(path) for path in (RESULT, SELF_REVIEW, CFR)]}


def verify_stored() -> dict[str, Any]:
    result = build_result()
    expected = {
        RESULT: canonical(result) + b"\n",
        SELF_REVIEW: build_self_review(result),
        CFR: build_cfr(result),
    }
    for path, payload in expected.items():
        if not path.is_file() or path.is_symlink() or path.read_bytes() != payload:
            raise A2Error(f"STORED_OUTPUT_MISMATCH:{path.name}")
    cfr_verification = verify_sole_cfr_payload(CFR.read_bytes())
    return {
        "status": "POSTWRITE_VERIFY_PASS",
        "outputs": [identity(path) for path in (RESULT, SELF_REVIEW, CFR)],
        "sole_cfr": cfr_verification,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--write-create-only", action="store_true")
    mode.add_argument("--verify-stored", action="store_true")
    mode.add_argument("--verify-sole-cfr", type=Path)
    args = parser.parse_args()
    if args.verify_sole_cfr is not None:
        result = verify_sole_cfr_payload(args.verify_sole_cfr.read_bytes())
    elif args.write_create_only:
        result = write_create_only()
    elif args.verify_stored:
        result = verify_stored()
    else:
        document = build_result()
        payload = canonical(document) + b"\n"
        result = {"status": "DRY_RUN_PASS", "bytes": len(payload), "sha256": sha(payload)}
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
