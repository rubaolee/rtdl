#!/usr/bin/env python3
"""Append-only Goal5799-A1 repair after the strict hostile self-review.

The predecessor Goal5799 artifacts are immutable evidence of the miss.  This
builder creates a successor contract authority, a conservative exposure-alias
amendment, and a receipt-only bridge for independent phase-ledger recount.  It
performs no application execution, network access, GPU work, or timing.
"""

from __future__ import annotations

import argparse
import base64
import copy
import gzip
import hashlib
import json
import re
import statistics
import tarfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"

PREDECESSOR_CFR = HISTORY / "call_for_review_goal5799_local_completion_and_goal5800_5801_entry_20260824.md"
STRICT_REVIEW = HISTORY / "strict_self_review_goal5799_postcommit_hostile_audit_20260824.md"
RETURNED_REVIEW = HISTORY / "review_goal5799_cgo_contribution_performance_repair_generalization_and_usability_plan_20260824.md"
V1_CONTRACT = HISTORY / "goal5799_performance_and_evidence_contract_20260824.json"
V1_REGISTRY = HISTORY / "goal5793_x3_a1_observed_work_exposure_registry_20260824.json"
V1_LEDGER = HISTORY / "goal5799_v11_cold_phase_ledger_20260824.json"
V11_ARCHIVE = HISTORY / "goal5798_v11_rtx4000ada_formal_evidence_20260824.tar.gz"
A1_RESULT = HISTORY / "goal5797_a1_exhaustive_populated_leaf_liveness_result_20260823.json"

CONTRACT = HISTORY / "goal5799_a1_repaired_performance_and_evidence_contract_20260824.json"
REGISTRY_AMENDMENT = HISTORY / "goal5799_a1_exposure_registry_alias_and_count_amendment_20260824.json"
RECEIPT_BRIDGE = HISTORY / "goal5799_a1_v11_cold_receipt_bridge_20260824.json"
INDEPENDENT_VERIFICATION = HISTORY / "goal5799_a1_independent_verification_20260824.json"
RESULT = HISTORY / "goal5799_a1_post_self_review_closure_result_20260824.json"
SELF_REVIEW = HISTORY / "self_review_goal5799_a1_post_self_review_closure_20260824.md"
CFR = HISTORY / "call_for_review_goal5799_a1_post_self_review_closure_and_goal5800_5801_entry_20260824.md"

CORE_OUTPUTS = (CONTRACT, REGISTRY_AMENDMENT, RECEIPT_BRIDGE)
CLOSEOUT_OUTPUTS = (RESULT, SELF_REVIEW, CFR)

PINS: dict[Path, tuple[int, str]] = {
    PREDECESSOR_CFR: (10_101_527, "c80f0a0b688ea369a69a3f461a85435939174e9e058664ab1a10b9b6de13e0ee"),
    STRICT_REVIEW: (13_575, "4fe95503005c9323655ef001d49fe3b4ea5d920ca6547096d5ac0b3e3e27a1bf"),
    RETURNED_REVIEW: (39_418, "bb889cd8e08c74beab93cb1d3592d8f28f203e80150c83e8eb281d541dbf9f01"),
    V1_CONTRACT: (6_053, "0cd4e65d88c9acc009b315fcadb0c9f8bb6338747918c40d07a1e839e0ca1e56"),
    V1_REGISTRY: (177_701, "39434a34f0215158c4e83f92c7500c79c4cc3083af9be129d9557591f336196f"),
    V1_LEDGER: (99_976, "1ef0786ff9f48bb9cb806c0d6ab3423f953cc907b1758a2a885552f75bf648c3"),
    V11_ARCHIVE: (13_668_025, "05070ddc86a8e971a046fe4affb92be1cae65087438335db57fd84c81cfda11b"),
    A1_RESULT: (52_151, "4d200a198ab42291d562e9f0861badbd623cb8a36c2ef81c1c3b86fc887278a1"),
}

DOMAIN = "rtdl.goal5799.a1.post_self_review_repair"


class RepairError(ValueError):
    """Stable fail-closed repair error."""


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(payload), "sha256": sha(payload)}


def verify_inputs() -> None:
    for path, (expected_bytes, expected_sha) in PINS.items():
        if not path.is_file() or path.is_symlink():
            raise RepairError(f"PINNED_INPUT_NOT_REGULAR:{path.name}")
        payload = path.read_bytes()
        if len(payload) != expected_bytes or sha(payload) != expected_sha:
            raise RepairError(f"PINNED_INPUT_IDENTITY_MISMATCH:{path.name}")


def _payload(document: Mapping[str, Any]) -> bytes:
    return canonical_json_bytes(document) + b"\n"


def _seal(document: dict[str, Any], field: str, domain_suffix: str) -> dict[str, Any]:
    document[field] = ""
    document[field] = seal_document(
        document,
        seal_field=field,
        domain=f"{DOMAIN}.{domain_suffix}.v1",
        version=1,
    )
    return document


def _walk_leaves(value: Any, path: tuple[Any, ...] = ()) -> Iterable[tuple[tuple[Any, ...], Any]]:
    if isinstance(value, Mapping):
        for key in sorted(value, key=lambda item: str(item).encode("utf-8")):
            yield from _walk_leaves(value[key], path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_leaves(item, path + (index,))
    else:
        yield path, value


def _pointer(path: tuple[Any, ...]) -> str:
    def escape(value: Any) -> str:
        return str(value).replace("~", "~0").replace("/", "~1")

    return "/" + "/".join(escape(item) for item in path)


def _control_manifest(semantic_body: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for path, value in _walk_leaves(semantic_body):
        rows.append(
            {
                "path": _pointer(path),
                "classification": "EXACT_IDENTITY_BOUND__MUTATION_MUST_REJECT",
                "expected_value_sha256": sha(canonical_json_bytes(value)),
                "expected_type": type(value).__name__,
            }
        )
    return rows


def _contract_semantic_body() -> dict[str, Any]:
    predecessor = json.loads(V1_CONTRACT.read_text(encoding="utf-8", errors="strict"))
    predecessor.pop("contract_sha256", None)
    predecessor["schema"] = "rtdl.goal5799.a1.performance_and_evidence_contract.v2"
    predecessor["status"] = (
        "FROZEN_DECLARATIVE_CONTRACT__EXACT_WHOLE_FILE_AUTHORITY_REQUIRED__"
        "GOAL5802_EXTERNAL_CLOSURE_PENDING"
    )
    predecessor["predecessor"] = identity(V1_CONTRACT)
    predecessor["post_self_review"] = identity(STRICT_REVIEW)
    predecessor["authority_model"] = {
        "integrity": "domain-separated internal contract_sha256",
        "authenticity": "expected whole-file SHA-256 supplied outside the contract and bound by the sole CFR/Goal5802 authority",
        "standalone_verifier_requires_expected_file_sha256": True,
        "goal5802_must_bind_exact_contract_file_sha256": True,
        "selective_field_import_is_forbidden": True,
        "every_semantic_leaf_is_exact_identity_bound": True,
        "manifest_rows_are_also_bound_by_whole_file_identity": True,
        "partial_validator_claimed": False,
    }
    predecessor["review_finding_status"] = {
        "goal5799_returned_review_P1_1": "REMEDY_FROZEN__EXTERNAL_GOAL5802_CLOSURE_PENDING",
        "goal5799_returned_review_P1_2": "REMEDY_FROZEN__EXTERNAL_GOAL5802_CLOSURE_PENDING",
        "goal5799_returned_review_P1_3": "LOCAL_REGISTRY_REPAIR_COMPLETE__EXTERNAL_ACCEPTANCE_PENDING",
        "goal5799_returned_review_P1_4": "DATED_DESCOPE_FROZEN",
        "postcommit_self_review_P1_1": "REPAIRED_BY_EXACT_AUTHORITY_PLUS_EXHAUSTIVE_LEAF_SWEEP__EXTERNAL_ACCEPTANCE_PENDING",
    }
    predecessor["comparative_gates"]["STEADY_E2E"]["owl_if_measured"] = {
        "metric": "RTDL/OWL",
        "decision": "95_PERCENT_CI_UPPER_BOUND_LE_1.05",
    }
    predecessor["comparative_gates"]["PREPARE"]["owl_if_measured"] = {
        "metric": "RTDL/OWL",
        "decision": "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
    }
    predecessor["comparative_gates"]["DEPLOYMENT_COLD"]["owl_if_measured"] = {
        "metric": "RTDL/OWL",
        "decision": "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
    }
    predecessor["baselines"]["OWL"]["timing_branch"] = {
        "optional": True,
        "if_absent": "NO_OWL_PERFORMANCE_STATEMENT",
        "if_present": "SAME_REGIMES_BOUNDARIES_AND_THRESHOLDS_AS_PYOPTIX",
        "executable_residual_arm_remains_mandatory_when_timing_absent": True,
    }
    predecessor["goal5802_not_yet_frozen__all_block_formal_worker_zero"] = [
        "exact estimand and row-local aggregation",
        "pairing, order and randomization schedule",
        "sample and warmup counts",
        "confidence-interval and random-seed procedure",
        "process freshness and cache-state construction",
        "failure, timeout, crash and missing-sample disposition",
        "outlier, exclusion and no-row-dropping rules",
        "exact timed worker bytes for every arm",
        "exact host/GPU/software binding and start gate",
        "per-arm engineering-effort ledger values",
        "external competence ruling with zero P0/P1",
        "whether the optional OWL timing branch is present",
        "independent raw recount implementation",
    ]
    predecessor["anonymity"] = {
        "artifact_evidence_gate": {
            "owner": "PROJECT_OWNER_OF_RECORD",
            "blocking": True,
            "checklist": [
                "archive member names and paths",
                "usernames, home directories and hostnames",
                "repository remotes, commit authors and commit emails",
                "acknowledgments, institutions, grants and self-citations",
                "embedded histories, receipts, commands and environment dumps",
                "PDF/document metadata and hidden properties",
                "public links that deanonymize the authors",
            ],
            "pass_condition": "IDENTIFYING_HITS_ZERO_OR_EACH_EXTERNALLY_JUDGED_NONIDENTIFYING",
        },
        "manuscript_gate": {
            "owner": "PROJECT_OWNER_OF_RECORD",
            "blocking": True,
            "checklist": [
                "title, author, affiliation and PDF metadata",
                "acknowledgments, grants, artifact URLs and repository names",
                "self-citations phrased in third person",
                "distinctive internal goal names, dates, hosts and file paths",
                "supplemental filenames and generated-document properties",
                "rebuttal and cover-letter identity leakage",
            ],
            "pass_condition": "IDENTIFYING_HITS_ZERO_OR_EACH_EXTERNALLY_JUDGED_NONIDENTIFYING",
        },
        "one_gate_may_substitute_for_the_other": False,
        "owner_assignment_is_internal_and_must_not_deanonymize_external_artifacts": True,
    }
    predecessor["publication"]["diagnostic_number_rendering"] = (
        "Every value derived outside a registered measurement must carry the literal inline prefix "
        "UNREGISTERED_DIAGNOSTIC in prose and tables; schema fields remain machine-readable and are "
        "covered by a row-level diagnostic_class field."
    )
    predecessor["authorization"] = {
        "goal5800_local_untimed": True,
        "goal5801_local_untimed": True,
        "goal5802_design_and_exact_cfr": True,
        "goal5802_formal_worker_zero": False,
        "goal5802_pod_gpu_timing": False,
        "goal5803": False,
        "network_provider_query": False,
        "external_contact_or_participant": False,
        "submission_or_public_claim": False,
    }
    return predecessor


def build_contract() -> dict[str, Any]:
    semantic = _contract_semantic_body()
    manifest = _control_manifest(semantic)
    document = dict(semantic)
    document["control_leaf_manifest"] = {
        "scope": "every populated leaf in the semantic body excluding this manifest and the self-seal",
        "leaf_count": len(manifest),
        "non_decision_bearing_leaf_count": 0,
        "rows": manifest,
        "rows_sha256": sha(canonical_json_bytes(manifest)),
    }
    document["contract_sha256"] = ""
    _seal(document, "contract_sha256", "contract")
    validate_contract_document(document)
    return document


def _require_path(document: Mapping[str, Any], path: tuple[str, ...], expected: Any) -> None:
    value: Any = document
    for key in path:
        if not isinstance(value, Mapping) or key not in value:
            raise RepairError(f"CONTRACT_REQUIRED_PATH_MISSING:{'/'.join(path)}")
        value = value[key]
    if value != expected:
        raise RepairError(f"CONTRACT_REQUIRED_VALUE_MISMATCH:{'/'.join(path)}")


def validate_contract_document(document: Mapping[str, Any]) -> None:
    if not isinstance(document, Mapping):
        raise RepairError("CONTRACT_SCHEMA_INVALID")
    expected_top = set(_contract_semantic_body()) | {"control_leaf_manifest", "contract_sha256"}
    if set(document) != expected_top:
        raise RepairError("CONTRACT_TOP_LEVEL_KEYS_MISMATCH")
    expected_seal = seal_document(
        document,
        seal_field="contract_sha256",
        domain=f"{DOMAIN}.contract.v1",
        version=1,
    )
    if document.get("contract_sha256") != expected_seal:
        raise RepairError("CONTRACT_INTERNAL_SEAL_MISMATCH")
    semantic = {key: copy.deepcopy(value) for key, value in document.items() if key not in {"control_leaf_manifest", "contract_sha256"}}
    manifest = _control_manifest(semantic)
    expected_manifest = {
        "scope": "every populated leaf in the semantic body excluding this manifest and the self-seal",
        "leaf_count": len(manifest),
        "non_decision_bearing_leaf_count": 0,
        "rows": manifest,
        "rows_sha256": sha(canonical_json_bytes(manifest)),
    }
    if document.get("control_leaf_manifest") != expected_manifest:
        raise RepairError("CONTRACT_CONTROL_LEAF_MANIFEST_MISMATCH")
    required = {
        ("symmetry", "same_timer_boundaries"): True,
        ("symmetry", "same_data_and_exact_oracle"): True,
        ("symmetry", "forbid_per_arm_postresult_optimization"): True,
        ("symmetry", "arm_engineering_ledger_fields"): [
            "arm",
            "engineer_or_agent",
            "start_utc",
            "stop_utc",
            "active_minutes",
            "files_changed",
            "purpose",
            "result_seen_before_change",
        ],
        ("structural_cache_hit_assertions", "exact_ptx_identity"): True,
        ("structural_cache_hit_assertions", "same_launch_and_synchronization_counts"): True,
        ("phase_attribution", "mutually_exclusive_phases_required"): True,
        ("phase_attribution", "subtraction_residual_is_not_causal_attribution"): True,
        ("phase_attribution", "unaccounted_time_must_be_named_not_dropped"): True,
        ("amortization", "publish_build_cold_absolute_times"): True,
        ("publication", "every_diagnostic_number_prefixed_UNREGISTERED_DIAGNOSTIC"): True,
        ("anonymity", "one_gate_may_substitute_for_the_other"): False,
        ("goal5803_descope", "decision_cutoff"): "2026-08-27T23:59:59-04:00",
        ("publication", "v11_withdrawal_sentence"): (
            "The initially favorable prepared comparison was withdrawn after review found avoidable per-element "
            "Python work in the PyOptiX arm; the correction removes an RTDL-favorable measurement bias."
        ),
        ("comparative_gates", "STEADY_E2E", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.05",
        ("comparative_gates", "DEPLOYMENT_COLD", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
        ("comparative_gates", "PREPARE", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
    }
    for path, expected in required.items():
        _require_path(document, path, expected)
    if semantic != _contract_semantic_body():
        raise RepairError("CONTRACT_SEMANTIC_BODY_NOT_EXACT_AUTHORITY")


class _UnionFind:
    def __init__(self, values: Iterable[int]) -> None:
        self.parent = {value: value for value in values}

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        a, b = self.find(left), self.find(right)
        if a != b:
            self.parent[max(a, b)] = min(a, b)


def _registry_alias_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source = json.loads(V1_REGISTRY.read_text(encoding="utf-8", errors="strict"))
    rows = source.get("rows")
    if not isinstance(rows, list) or len(rows) != 200:
        raise RepairError("REGISTRY_V1_ROW_COUNT_MISMATCH")
    uf = _UnionFind(range(200))
    alias_to_ordinals: dict[tuple[str, str], list[int]] = defaultdict(list)
    amended_rows = []
    doi_exact_to_ordinals: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        ordinal = row.get("ordinal")
        if type(ordinal) is not int or not 0 <= ordinal < 200:
            raise RepairError("REGISTRY_ORDINAL_INVALID")
        if row.get("selection_eligible") is not False:
            raise RepairError("REGISTRY_ELIGIBILITY_INVALID")
        aliases = [dict(alias) for alias in row.get("aliases", [])]
        doi = row.get("doi")
        if isinstance(doi, str):
            doi_exact_to_ordinals[doi].append(ordinal)
            if doi.endswith("/pdf") and len(doi) > 4:
                aliases.append(
                    {
                        "kind": "doi_conservative_terminal_pdf_stripped",
                        "value": doi[:-4],
                    }
                )
        aliases.sort(key=lambda item: (str(item["kind"]).encode("utf-8"), str(item["value"]).encode("utf-8")))
        for alias in aliases:
            kind = str(alias["kind"])
            value = str(alias["value"])
            equivalence_kind = "doi" if kind == "doi_conservative_terminal_pdf_stripped" else kind
            alias_to_ordinals[(equivalence_kind, value)].append(ordinal)
        amended_rows.append(
            {
                "ordinal": ordinal,
                "openalex": row.get("openalex"),
                "canonical_work_identity_v1": row.get("canonical_work_identity"),
                "matching_aliases": aliases,
                "selection_eligible": False,
                "future_match_disposition": "EXPOSED__SELECTION_INELIGIBLE__NO_RESCUE",
            }
        )
    for ordinals in alias_to_ordinals.values():
        for ordinal in ordinals[1:]:
            uf.union(ordinals[0], ordinal)
    components: dict[int, list[int]] = defaultdict(list)
    for ordinal in range(200):
        components[uf.find(ordinal)].append(ordinal)
    component_rows = []
    for members in sorted(components.values(), key=lambda values: values[0]):
        shared = []
        member_set = set(members)
        for (kind, value), ordinals in alias_to_ordinals.items():
            overlap = sorted(member_set.intersection(ordinals))
            if len(overlap) >= 2:
                shared.append({"kind": kind, "value": value, "member_ordinals": overlap})
        component_rows.append(
            {
                "component_id": f"EXPOSURE_COMPONENT_{members[0]:03d}",
                "member_ordinals": members,
                "record_count": len(members),
                "shared_aliases": sorted(shared, key=lambda item: (item["kind"], item["value"])),
                "is_single_record_component": len(members) == 1,
                "scientific_same_work_asserted": False,
                "selection_disposition": "ALL_MEMBER_RECORDS_INELIGIBLE",
            }
        )
    for row in amended_rows:
        component = next(component for component in component_rows if row["ordinal"] in component["member_ordinals"])
        row["alias_component_id"] = component["component_id"]
    return amended_rows, component_rows


def build_registry_amendment() -> dict[str, Any]:
    rows, components = _registry_alias_rows()
    multi = [component for component in components if component["record_count"] > 1]
    terminal_pdf_rows = [
        row
        for row in rows
        if any(alias["kind"] == "doi_conservative_terminal_pdf_stripped" for alias in row["matching_aliases"])
    ]
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.a1.exposure_registry_alias_and_count_amendment.v1",
        "date": "2026-08-24",
        "status": "PASS__200_PROVIDER_RECORDS_PRESERVED_INELIGIBLE__ALIAS_OVERLAP_EXPLICIT",
        "predecessor_registry": identity(V1_REGISTRY),
        "terminology": {
            "observed_provider_records": 200,
            "unique_openalex_ids": 200,
            "unique_v1_canonical_strings": 200,
            "conservative_alias_components": len(components),
            "semantic_unique_scientific_work_count": "UNKNOWN__NOT_INFERRED_FROM_PROVIDER_RECORD_COUNT",
            "wording_forbidden": "200_PROVEN_DISTINCT_SCIENTIFIC_WORKS",
        },
        "matching_rule": {
            "future_task_matches_if_any_alias_matches": True,
            "alias_ambiguity_disposition": "EXPOSED__SELECTION_INELIGIBLE__POWER_LOSS_ONLY",
            "terminal_pdf_doi_policy": "retain raw/frozen DOI and add a conservative stripped alias; never edit the predecessor",
            "no_alias_match_is_not_sufficient_for_generalization_claim": True,
        },
        "counts": {
            "provider_records": len(rows),
            "selection_eligible_records": sum(row["selection_eligible"] is True for row in rows),
            "alias_components": len(components),
            "multi_record_alias_components": len(multi),
            "records_in_multi_record_alias_components": sum(component["record_count"] for component in multi),
            "terminal_pdf_conservative_alias_rows": len(terminal_pdf_rows),
        },
        "rows": rows,
        "components": components,
        "claim_boundary": {
            "goal5793_reopened": False,
            "candidate_population_constructed": False,
            "generalization_exam_added": False,
            "usability_evidence_added": False,
            "all_200_records_remain_ineligible": True,
        },
        "authorization": {
            "network": False,
            "provider_rerun": False,
            "selection": False,
            "goal5803": False,
        },
        "rows_sha256": sha(canonical_json_bytes(rows)),
        "components_sha256": sha(canonical_json_bytes(components)),
        "amendment_sha256": "",
    }
    if document["counts"] != {
        "provider_records": 200,
        "selection_eligible_records": 0,
        "alias_components": 194,
        "multi_record_alias_components": 5,
        "records_in_multi_record_alias_components": 11,
        "terminal_pdf_conservative_alias_rows": 2,
    }:
        raise RepairError(f"REGISTRY_AMENDMENT_COUNTS_MISMATCH:{document['counts']!r}")
    return _seal(document, "amendment_sha256", "registry_amendment")


def _phase_row(receipt: Mapping[str, Any]) -> dict[str, Any]:
    durations = receipt.get("durations_ns")
    if not isinstance(durations, Mapping):
        raise RepairError("RECEIPT_DURATIONS_MISSING")
    wall = durations.get("controller_process_wall_ns")
    input_ns = durations.get("input_materialization_ns")
    prepare_ns = durations.get("common_preparation_total_ns")
    execute_values = durations.get("complete_execute_ns")
    close_raw = durations.get("close_ns")
    if type(wall) is not int or wall <= 0 or type(input_ns) is not int or type(prepare_ns) is not int:
        raise RepairError("RECEIPT_PHASE_SCHEMA_INVALID")
    if not isinstance(execute_values, list) or not execute_values or any(type(value) is not int for value in execute_values):
        raise RepairError("RECEIPT_EXECUTE_SCHEMA_INVALID")
    close_ns = 0 if close_raw is None else close_raw
    if type(close_ns) is not int or close_ns < 0:
        raise RepairError("RECEIPT_CLOSE_SCHEMA_INVALID")
    execute_ns = sum(execute_values)
    directly_metered = input_ns + prepare_ns + execute_ns + close_ns
    residual = wall - directly_metered
    if residual < 0:
        raise RepairError("RECEIPT_NEGATIVE_RESIDUAL")
    return {
        "worker_id": receipt.get("worker_id"),
        "task": receipt.get("task"),
        "arm": receipt.get("arm"),
        "sample_index": receipt.get("row_sample_index"),
        "wall_ns": wall,
        "phases_ns": {
            "input_materialization_ns": input_ns,
            "common_preparation_total_ns": prepare_ns,
            "complete_execute_ns": execute_ns,
            "close_ns": close_ns,
            "controller_process_envelope_residual_ns": residual,
        },
        "close_observation": "NOT_EMITTED_BY_ARM__COUNTED_AS_ZERO_NOT_INFERRED" if close_raw is None else "DIRECTLY_METERED",
        "directly_metered_ns": directly_metered,
        "directly_metered_fraction": directly_metered / wall,
        "named_accounting_fraction": 1.0,
        "source_receipt_sha256": receipt.get("receipt_sha256"),
    }


def build_receipt_bridge() -> dict[str, Any]:
    raw_entries = []
    with tarfile.open(V11_ARCHIVE, "r:gz") as archive:
        names = sorted(name for name in archive.getnames() if name.endswith("/final_receipt.json"))
        for name in names:
            member = archive.extractfile(name)
            if member is None:
                raise RepairError(f"RECEIPT_MEMBER_MISSING:{name}")
            raw = member.read()
            parsed = json.loads(raw)
            if parsed.get("mode") != "COLD_FRESH_PROCESS":
                continue
            raw_entries.append(
                {
                    "member": name,
                    "raw_bytes": len(raw),
                    "raw_sha256": sha(raw),
                    "raw_base64": base64.b64encode(raw).decode("ascii"),
                }
            )
    if len(raw_entries) != 144:
        raise RepairError(f"RECEIPT_BRIDGE_COUNT_MISMATCH:{len(raw_entries)}")
    raw_rows = []
    for entry in raw_entries:
        raw = base64.b64decode(entry["raw_base64"], validate=True)
        raw_rows.append(_phase_row(json.loads(raw)))
    expected_ledger = json.loads(V1_LEDGER.read_text(encoding="utf-8", errors="strict"))
    if raw_rows != expected_ledger.get("rows"):
        raise RepairError("RECEIPT_BRIDGE_LEDGER_ROWS_MISMATCH")
    container = {
        "schema": "rtdl.goal5799.a1.v11_cold_raw_receipt_container.v1",
        "entries": raw_entries,
    }
    container_payload = canonical_json_bytes(container) + b"\n"
    compressed = gzip.compress(container_payload, compresslevel=9, mtime=0)
    entry_manifest = [
        {
            "member": entry["member"],
            "raw_bytes": entry["raw_bytes"],
            "raw_sha256": entry["raw_sha256"],
        }
        for entry in raw_entries
    ]
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.a1.v11_cold_receipt_bridge.v1",
        "date": "2026-08-24",
        "status": "PASS__144_RAW_COLD_RECEIPTS_EMBEDDED__ZERO_NEW_TIMINGS",
        "source_archive": identity(V11_ARCHIVE),
        "target_phase_ledger": identity(V1_LEDGER),
        "scope": {
            "raw_receipt_count": len(raw_entries),
            "new_application_execution_count": 0,
            "new_timing_sample_count": 0,
            "diagnostic_class": "UNREGISTERED_DIAGNOSTIC_RECOUNT_OF_IMMUTABLE_PREDECESSOR",
        },
        "compression": {
            "format": "gzip",
            "compresslevel": 9,
            "mtime": 0,
            "uncompressed_bytes": len(container_payload),
            "uncompressed_sha256": sha(container_payload),
            "compressed_bytes": len(compressed),
            "compressed_sha256": sha(compressed),
        },
        "entry_manifest": entry_manifest,
        "compressed_container_base64": base64.b64encode(compressed).decode("ascii"),
        "raw_phase_rows_sha256": sha(canonical_json_bytes(raw_rows)),
        "entry_manifest_sha256": sha(canonical_json_bytes(entry_manifest)),
        "claim_boundary": {
            "archive_other_members_embedded": False,
            "all_cold_final_receipts_embedded": True,
            "phase_arithmetic_reconstructable_without_repository_or_archive": True,
            "causal_attribution_established": False,
            "direct_metering_95_percent_met": False,
        },
        "bridge_sha256": "",
    }
    return _seal(document, "bridge_sha256", "receipt_bridge")


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise RepairError(f"CREATE_ONLY_OUTPUT_EXISTS:{path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def write_core() -> dict[str, Any]:
    verify_inputs()
    documents = {
        CONTRACT: build_contract(),
        REGISTRY_AMENDMENT: build_registry_amendment(),
        RECEIPT_BRIDGE: build_receipt_bridge(),
    }
    for path in CORE_OUTPUTS:
        if path.exists() or path.is_symlink():
            raise RepairError(f"CREATE_ONLY_OUTPUT_EXISTS:{path.name}")
    for path, document in documents.items():
        _write_create_only(path, _payload(document))
    return {"status": "CORE_CREATE_ONLY_PASS", "outputs": [identity(path) for path in CORE_OUTPUTS]}


def verify_core_stored() -> dict[str, Any]:
    verify_inputs()
    expected = {
        CONTRACT: _payload(build_contract()),
        REGISTRY_AMENDMENT: _payload(build_registry_amendment()),
        RECEIPT_BRIDGE: _payload(build_receipt_bridge()),
    }
    for path, payload in expected.items():
        if not path.is_file() or path.is_symlink() or path.read_bytes() != payload:
            raise RepairError(f"STORED_CORE_MISMATCH:{path.name}")
    return {"status": "CORE_POSTWRITE_VERIFY_PASS", "outputs": [identity(path) for path in CORE_OUTPUTS]}


def build_result() -> dict[str, Any]:
    if not INDEPENDENT_VERIFICATION.is_file():
        raise RepairError("INDEPENDENT_VERIFICATION_MISSING")
    verification = json.loads(INDEPENDENT_VERIFICATION.read_text(encoding="utf-8", errors="strict"))
    if verification.get("status") != "PASS__INDEPENDENT_POST_SELF_REVIEW_REPAIR_VERIFICATION":
        raise RepairError("INDEPENDENT_VERIFICATION_STATUS_INVALID")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8", errors="strict"))
    registry = json.loads(REGISTRY_AMENDMENT.read_text(encoding="utf-8", errors="strict"))
    bridge = json.loads(RECEIPT_BRIDGE.read_text(encoding="utf-8", errors="strict"))
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.a1.post_self_review_closure_result.v1",
        "date": "2026-08-24",
        "status": "PASS__GOAL5799_LOCAL_SCOPE_THOROUGHLY_COMPLETE__EXTERNAL_REVIEW_PENDING",
        "predecessor_goal5799_commit": "f851a5b5e12f8705e9c0c0d641bcb2e41ae3ac17",
        "strict_self_review_commit": "11f1093d2701c21337687366ec26e609936ffe20",
        "predecessor_cfr_disposition": "SUPERSEDED_FOR_SENDING__PRESERVED_IMMUTABLE__DO_NOT_SEND_ALONE",
        "repairs": {
            "known_accepted_invalid_contract_attacks": 17,
            "known_attacks_rejected_after_repair": 17,
            "semantic_control_leaf_count": contract["control_leaf_manifest"]["leaf_count"],
            "semantic_control_leaves_exact_identity_bound": contract["control_leaf_manifest"]["leaf_count"],
            "semantic_non_decision_bearing_leaves": 0,
            "provider_records_preserved_ineligible": registry["counts"]["provider_records"],
            "semantic_unique_work_count": "UNKNOWN",
            "alias_components_published": registry["counts"]["alias_components"],
            "raw_cold_receipts_embedded": bridge["scope"]["raw_receipt_count"],
            "new_timing_samples": 0,
            "goal5802_incomplete_items_explicit": len(contract["goal5802_not_yet_frozen__all_block_formal_worker_zero"]),
            "anonymity_checklists": 2,
        },
        "scientific_state": {
            "generalization_exam_count": 0,
            "external_v4_author_count": 0,
            "usability_study_count": 0,
            "executable_owl_residual_mechanisms": 0,
            "performance_noninferiority_established": False,
            "v11_favorable_prepared_claim_active": False,
        },
        "artifacts": {
            "contract": identity(CONTRACT),
            "registry_amendment": identity(REGISTRY_AMENDMENT),
            "receipt_bridge": identity(RECEIPT_BRIDGE),
            "independent_verification": identity(INDEPENDENT_VERIFICATION),
        },
        "authorization": {
            "goal5800_local_untimed": True,
            "goal5801_local_untimed": True,
            "goal5802_design_and_single_cfr": True,
            "goal5802_formal_worker_zero": False,
            "goal5802_pod_gpu_timing": False,
            "goal5803": False,
            "network_provider_query": False,
            "external_contact_or_participant": False,
            "submission_or_public_claim": False,
        },
        "result_sha256": "",
    }
    return _seal(document, "result_sha256", "closure_result")


def build_self_review(result: Mapping[str, Any]) -> bytes:
    text = f"""# Strict self-review — Goal5799-A1 post-self-review closure (2026-08-24)

## Verdict

**PASS at local append-only repair scope; external acceptance pending.** The predecessor miss is preserved. This amendment does not rerun or relabel any scientific result.

## The P1 repair

The old partial validator accepted 17/17 selected-invalid control mutations. The repaired contract has {result['repairs']['semantic_control_leaf_count']} populated semantic leaves. Every one is present in an exact-value manifest and is bound by the externally supplied whole-file SHA-256; zero are declared non-decision-bearing. The original 17 attacks are also resealed and reauthorized under their own mutated hashes during testing, and all 17 now reject on semantic invariants rather than only on stale seals.

This does not claim that prose can enforce future execution. Goal5802 must bind the exact repaired contract file SHA-256 in its own externally accepted premeasurement CFR. Until then P1-1/P1-2 are `REMEDY_FROZEN__EXTERNAL_GOAL5802_CLOSURE_PENDING`, not externally closed.

## Registry correction

The durable count is 200 observed provider records and 200 unique OpenAlex IDs. Semantic distinct-work count is UNKNOWN. Five multi-record conservative alias components cover eleven records; the total conservative component count is 194. Every record remains ineligible. No row was deleted, merged into a candidate, or reused for science.

## Receipt bridge

All 144 raw cold final receipts are embedded byte-exactly. The independent verifier decodes them without the repository archive, rehashes every raw member, rebuilds all phase rows and compares them to the immutable ledger. This creates zero new timings and establishes no causal share.

## Remaining locks

Generalization exams, external authors, usability studies, OWL executable mechanisms and performance noninferiority remain 0/0/0/0/not-established. Goal5802 formal workers, Goal5803, network, participants, POD/GPU timing, submission and public claims remain false.

## Residual risks

1. Exact-byte authority is only effective if Goal5802 actually pins this contract's whole-file SHA-256; selective field copying remains forbidden.
2. Conservative alias components can overexclude distinct versions or papers. That costs power only and is preferable to a hidden contamination escape.
3. The raw receipt bridge proves arithmetic and provenance, not causality or adequate direct metering; the old 95% requirement still fails.
4. The two anonymity owners are internally designated as `PROJECT_OWNER_OF_RECORD`; the external artifact must not reveal the human identity.

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
    header = f"""# SEND ONLY THIS FILE — Goal5799-A1 post-self-review closure and Goal5800/5801 entry

**This supersedes the predecessor Goal5799 CFR for sending. Send only this Markdown file.** The predecessor remains embedded and immutable evidence; it must not be deleted or silently rewritten.

## Requested verdict

Return `P0 / P1 / P2 / P3` and answer every item:

1. Does exact whole-file authority plus the exhaustive semantic-leaf manifest close the postcommit inert-control P1, including the 17 coordinated reseal attacks?
2. Is the corrected exposure statement exact: 200 provider records, 200 OpenAlex IDs, 194 conservative alias components, semantic unique-work count UNKNOWN, all records ineligible?
3. Can all 144 raw cold receipts be reconstructed from this file and can their phase rows be rebuilt without the 13.7 MB archive?
4. Are Goal5799 returned-review P1-1/P1-2 now correctly labelled remedy-frozen but externally pending until the separate Goal5802 premeasurement CFR?
5. Are the optional OWL timing branch, Goal5802 not-yet-frozen list, inline diagnostic rule and two owner/checklist anonymity gates sufficient?
6. May Goal5799 be considered locally complete and Goal5800/5801 proceed locally/untimed while every formal/external/submission lock remains false?

## Exact local result

- Contract semantic leaves: **{result['repairs']['semantic_control_leaf_count']} exact-identity-bound / 0 non-decision-bearing**.
- Known hostile controls: **17/17 rejected after coordinated mutation and reseal**.
- Exposure: **200 records / 200 OpenAlex IDs / 194 conservative components / scientific unique-work count UNKNOWN / 0 eligible**.
- Receipt bridge: **144 exact raw cold receipts / 0 new timings**.
- Scientific evidence added: **0 generalization / 0 external author / 0 usability / 0 OWL / 0 performance result**.

Local result seal: `{result['result_sha256']}`.
"""
    sections = [header]
    sections.append(_embed("predecessor Goal5799 sole CFR — superseded for sending", PREDECESSOR_CFR, "markdown"))
    sections.append(_embed("postcommit strict hostile self-review", STRICT_REVIEW, "markdown"))
    sections.append(_embed("repaired exact-authority performance/evidence contract", CONTRACT, "json"))
    sections.append(_embed("exposure registry alias/count amendment", REGISTRY_AMENDMENT, "json"))
    sections.append(_embed("144-receipt byte bridge", RECEIPT_BRIDGE, "json"))
    sections.append(_embed("independent verification", INDEPENDENT_VERIFICATION, "json"))
    sections.append(_embed("Goal5799-A1 closure result", RESULT, "json"))
    sections.append(_embed("Goal5799-A1 strict self-review", SELF_REVIEW, "markdown"))
    sections.append(_embed("Goal5799-A1 builder", Path(__file__).resolve(), "python"))
    sections.append(_embed("Goal5799-A1 independent verifier", ROOT / "scripts/goal5799_a1_independent_verify_post_self_review_repair.py", "python"))
    sections.append(_embed("Goal5799-A1 hostile tests", ROOT / "tests/goal5799_a1_post_self_review_repair_test.py", "python"))
    sections.append(
        "\n## Required return format\n\n"
        "Commit one review Markdown file naming this CFR SHA-256, the full P0/P1/P2/P3 verdict, every requested answer, and exact counterexample bytes for every P0/P1. State explicitly that neither review nor this CFR starts Goal5802 formal worker zero or Goal5803.\n"
    )
    return "".join(sections).encode("utf-8")


def write_closeout() -> dict[str, Any]:
    verify_core_stored()
    if not INDEPENDENT_VERIFICATION.is_file() or INDEPENDENT_VERIFICATION.is_symlink():
        raise RepairError("INDEPENDENT_VERIFICATION_NOT_REGULAR")
    for path in CLOSEOUT_OUTPUTS:
        if path.exists() or path.is_symlink():
            raise RepairError(f"CREATE_ONLY_OUTPUT_EXISTS:{path.name}")
    result = build_result()
    _write_create_only(RESULT, _payload(result))
    _write_create_only(SELF_REVIEW, build_self_review(result))
    _write_create_only(CFR, build_cfr(result))
    return {"status": "CLOSEOUT_CREATE_ONLY_PASS", "outputs": [identity(path) for path in CLOSEOUT_OUTPUTS]}


def verify_closeout_stored() -> dict[str, Any]:
    verify_core_stored()
    result = build_result()
    expected = {
        RESULT: _payload(result),
        SELF_REVIEW: build_self_review(result),
        CFR: build_cfr(result),
    }
    for path, payload in expected.items():
        if not path.is_file() or path.is_symlink() or path.read_bytes() != payload:
            raise RepairError(f"STORED_CLOSEOUT_MISMATCH:{path.name}")
    return {"status": "CLOSEOUT_POSTWRITE_VERIFY_PASS", "outputs": [identity(path) for path in CLOSEOUT_OUTPUTS]}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--write-core-create-only", action="store_true")
    mode.add_argument("--verify-core-stored", action="store_true")
    mode.add_argument("--write-closeout-create-only", action="store_true")
    mode.add_argument("--verify-closeout-stored", action="store_true")
    args = parser.parse_args()
    if args.write_core_create_only:
        result = write_core()
    elif args.verify_core_stored:
        result = verify_core_stored()
    elif args.write_closeout_create_only:
        result = write_closeout()
    elif args.verify_closeout_stored:
        result = verify_closeout_stored()
    else:
        verify_inputs()
        documents = [build_contract(), build_registry_amendment(), build_receipt_bridge()]
        result = {
            "status": "DRY_RUN_PASS",
            "outputs": [
                {"bytes": len(_payload(document)), "sha256": sha(_payload(document))}
                for document in documents
            ],
        }
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
