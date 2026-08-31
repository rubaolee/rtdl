#!/usr/bin/env python3
"""Independent verifier for the Goal5799-A1 post-self-review repair.

This module deliberately does not import the repair builder.  Whole-file
digests are supplied outside the artifacts, preserving the distinction between
an internal integrity seal and external authority.
"""

from __future__ import annotations

import argparse
import base64
import copy
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
CONTRACT = HISTORY / "goal5799_a1_repaired_performance_and_evidence_contract_20260824.json"
REGISTRY_AMENDMENT = HISTORY / "goal5799_a1_exposure_registry_alias_and_count_amendment_20260824.json"
V1_REGISTRY = HISTORY / "goal5793_x3_a1_observed_work_exposure_registry_20260824.json"
RECEIPT_BRIDGE = HISTORY / "goal5799_a1_v11_cold_receipt_bridge_20260824.json"
V1_LEDGER = HISTORY / "goal5799_v11_cold_phase_ledger_20260824.json"
OUTPUT = HISTORY / "goal5799_a1_independent_verification_20260824.json"

V1_REGISTRY_BYTES = 177_701
V1_REGISTRY_SHA256 = "39434a34f0215158c4e83f92c7500c79c4cc3083af9be129d9557591f336196f"
V1_LEDGER_BYTES = 99_976
V1_LEDGER_SHA256 = "1ef0786ff9f48bb9cb806c0d6ab3423f953cc907b1758a2a885552f75bf648c3"
DOMAIN = "rtdl.goal5799.a1.post_self_review_repair"


class VerificationError(ValueError):
    """Stable fail-closed independent verification error."""


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(payload), "sha256": sha(payload)}


def _canonical_file(path: Path, expected_sha: str) -> tuple[bytes, dict[str, Any]]:
    if not path.is_file() or path.is_symlink():
        raise VerificationError(f"INPUT_NOT_REGULAR:{path.name}")
    payload = path.read_bytes()
    if sha(payload) != expected_sha:
        raise VerificationError(f"EXPECTED_FILE_IDENTITY_MISMATCH:{path.name}")
    try:
        document = json.loads(payload)
    except Exception as exc:  # noqa: BLE001
        raise VerificationError(f"JSON_INVALID:{path.name}") from exc
    if payload != canonical_json_bytes(document) + b"\n":
        raise VerificationError(f"NONCANONICAL_FILE:{path.name}")
    return payload, document


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


def _get(document: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = document
    for key in path:
        if not isinstance(value, Mapping) or key not in value:
            raise VerificationError(f"REQUIRED_PATH_MISSING:{'/'.join(path)}")
        value = value[key]
    return value


def verify_contract(path: Path, expected_sha: str) -> dict[str, Any]:
    payload, document = _canonical_file(path, expected_sha)
    expected_seal = seal_document(
        document,
        seal_field="contract_sha256",
        domain=f"{DOMAIN}.contract.v1",
        version=1,
    )
    if document.get("contract_sha256") != expected_seal:
        raise VerificationError("CONTRACT_INTERNAL_SEAL_MISMATCH")
    semantic = {
        key: copy.deepcopy(value)
        for key, value in document.items()
        if key not in {"control_leaf_manifest", "contract_sha256"}
    }
    rows = [
        {
            "path": _pointer(leaf_path),
            "classification": "EXACT_IDENTITY_BOUND__MUTATION_MUST_REJECT",
            "expected_value_sha256": sha(canonical_json_bytes(value)),
            "expected_type": type(value).__name__,
        }
        for leaf_path, value in _walk(semantic)
    ]
    expected_manifest = {
        "scope": "every populated leaf in the semantic body excluding this manifest and the self-seal",
        "leaf_count": len(rows),
        "non_decision_bearing_leaf_count": 0,
        "rows": rows,
        "rows_sha256": sha(canonical_json_bytes(rows)),
    }
    if document.get("control_leaf_manifest") != expected_manifest:
        raise VerificationError("CONTRACT_CONTROL_MANIFEST_MISMATCH")
    required = {
        ("schema",): "rtdl.goal5799.a1.performance_and_evidence_contract.v2",
        ("symmetry", "same_timer_boundaries"): True,
        ("symmetry", "same_data_and_exact_oracle"): True,
        ("symmetry", "forbid_per_arm_postresult_optimization"): True,
        ("symmetry", "arm_engineering_ledger_fields"): [
            "arm", "engineer_or_agent", "start_utc", "stop_utc", "active_minutes", "files_changed", "purpose", "result_seen_before_change"
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
        ("comparative_gates", "STEADY_E2E", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.05",
        ("comparative_gates", "DEPLOYMENT_COLD", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
        ("comparative_gates", "PREPARE", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
        ("comparative_gates", "STEADY_E2E", "owl_if_measured", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.05",
        ("comparative_gates", "DEPLOYMENT_COLD", "owl_if_measured", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
        ("comparative_gates", "PREPARE", "owl_if_measured", "decision"): "95_PERCENT_CI_UPPER_BOUND_LE_1.10",
        ("authorization", "goal5802_formal_worker_zero"): False,
        ("authorization", "goal5802_pod_gpu_timing"): False,
        ("authorization", "goal5803"): False,
        ("authorization", "network_provider_query"): False,
        ("authorization", "external_contact_or_participant"): False,
        ("authorization", "submission_or_public_claim"): False,
    }
    for required_path, expected in required.items():
        if _get(document, required_path) != expected:
            raise VerificationError(f"CONTRACT_REQUIRED_VALUE_MISMATCH:{'/'.join(required_path)}")
    incomplete = document.get("goal5802_not_yet_frozen__all_block_formal_worker_zero")
    if not isinstance(incomplete, list) or len(incomplete) != 13:
        raise VerificationError("GOAL5802_INCOMPLETE_LEDGER_MISMATCH")
    return {
        "file_bytes": len(payload),
        "file_sha256": sha(payload),
        "contract_sha256": document["contract_sha256"],
        "semantic_leaf_count": len(rows),
        "non_decision_bearing_leaf_count": 0,
        "goal5802_not_yet_frozen_count": len(incomplete),
    }


class _UF:
    def __init__(self) -> None:
        self.parent = list(range(200))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        a, b = self.find(left), self.find(right)
        if a != b:
            self.parent[max(a, b)] = min(a, b)


def _expected_registry_rows(v1_rows: list[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    aliases: dict[tuple[str, str], list[int]] = defaultdict(list)
    rows = []
    for row in v1_rows:
        ordinal = row.get("ordinal")
        if type(ordinal) is not int or not 0 <= ordinal < 200 or row.get("selection_eligible") is not False:
            raise VerificationError("V1_REGISTRY_ROW_INVALID")
        matching = [dict(alias) for alias in row.get("aliases", [])]
        doi = row.get("doi")
        if isinstance(doi, str) and doi.endswith("/pdf"):
            matching.append({"kind": "doi_conservative_terminal_pdf_stripped", "value": doi[:-4]})
        matching.sort(key=lambda item: (str(item["kind"]).encode(), str(item["value"]).encode()))
        for alias in matching:
            kind = "doi" if alias["kind"] == "doi_conservative_terminal_pdf_stripped" else alias["kind"]
            aliases[(str(kind), str(alias["value"]))].append(ordinal)
        rows.append(
            {
                "ordinal": ordinal,
                "openalex": row.get("openalex"),
                "canonical_work_identity_v1": row.get("canonical_work_identity"),
                "matching_aliases": matching,
                "selection_eligible": False,
                "future_match_disposition": "EXPOSED__SELECTION_INELIGIBLE__NO_RESCUE",
            }
        )
    uf = _UF()
    for members in aliases.values():
        for member in members[1:]:
            uf.union(members[0], member)
    components: dict[int, list[int]] = defaultdict(list)
    for ordinal in range(200):
        components[uf.find(ordinal)].append(ordinal)
    component_rows = []
    for members in sorted(components.values(), key=lambda values: values[0]):
        member_set = set(members)
        shared = []
        for (kind, value), aliases_members in aliases.items():
            overlap = sorted(member_set.intersection(aliases_members))
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
    for row in rows:
        component = next(value for value in component_rows if row["ordinal"] in value["member_ordinals"])
        row["alias_component_id"] = component["component_id"]
    return rows, component_rows


def verify_registry(path: Path, expected_sha: str) -> dict[str, Any]:
    payload, document = _canonical_file(path, expected_sha)
    v1_payload = V1_REGISTRY.read_bytes()
    if len(v1_payload) != V1_REGISTRY_BYTES or sha(v1_payload) != V1_REGISTRY_SHA256:
        raise VerificationError("V1_REGISTRY_IDENTITY_MISMATCH")
    v1 = json.loads(v1_payload)
    rows, components = _expected_registry_rows(v1["rows"])
    if document.get("rows") != rows or document.get("components") != components:
        raise VerificationError("REGISTRY_AMENDMENT_ROWS_OR_COMPONENTS_MISMATCH")
    expected_counts = {
        "provider_records": 200,
        "selection_eligible_records": 0,
        "alias_components": 194,
        "multi_record_alias_components": 5,
        "records_in_multi_record_alias_components": 11,
        "terminal_pdf_conservative_alias_rows": 2,
    }
    if document.get("counts") != expected_counts:
        raise VerificationError("REGISTRY_AMENDMENT_COUNTS_MISMATCH")
    if document.get("terminology", {}).get("semantic_unique_scientific_work_count") != "UNKNOWN__NOT_INFERRED_FROM_PROVIDER_RECORD_COUNT":
        raise VerificationError("REGISTRY_UNIQUE_WORK_CLAIM_INVALID")
    if any(row["selection_eligible"] is not False for row in rows):
        raise VerificationError("REGISTRY_ELIGIBLE_ROW")
    expected_seal = seal_document(document, seal_field="amendment_sha256", domain=f"{DOMAIN}.registry_amendment.v1", version=1)
    if document.get("amendment_sha256") != expected_seal:
        raise VerificationError("REGISTRY_AMENDMENT_SEAL_MISMATCH")
    return {
        "file_bytes": len(payload),
        "file_sha256": sha(payload),
        "provider_records": 200,
        "selection_eligible_records": 0,
        "alias_components": 194,
        "semantic_unique_work_count": "UNKNOWN",
    }


def _phase_row(receipt: Mapping[str, Any]) -> dict[str, Any]:
    durations = receipt.get("durations_ns")
    if not isinstance(durations, Mapping):
        raise VerificationError("BRIDGE_RECEIPT_DURATIONS_INVALID")
    wall = durations.get("controller_process_wall_ns")
    input_ns = durations.get("input_materialization_ns")
    prepare_ns = durations.get("common_preparation_total_ns")
    values = durations.get("complete_execute_ns")
    close_raw = durations.get("close_ns")
    if type(wall) is not int or type(input_ns) is not int or type(prepare_ns) is not int:
        raise VerificationError("BRIDGE_RECEIPT_PHASE_INVALID")
    if not isinstance(values, list) or not values or any(type(value) is not int for value in values):
        raise VerificationError("BRIDGE_RECEIPT_EXECUTE_INVALID")
    close_ns = 0 if close_raw is None else close_raw
    if type(close_ns) is not int:
        raise VerificationError("BRIDGE_RECEIPT_CLOSE_INVALID")
    execute_ns = sum(values)
    direct = input_ns + prepare_ns + execute_ns + close_ns
    residual = wall - direct
    if residual < 0:
        raise VerificationError("BRIDGE_RECEIPT_NEGATIVE_RESIDUAL")
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
        "directly_metered_ns": direct,
        "directly_metered_fraction": direct / wall,
        "named_accounting_fraction": 1.0,
        "source_receipt_sha256": receipt.get("receipt_sha256"),
    }


def verify_bridge(path: Path, expected_sha: str) -> dict[str, Any]:
    payload, document = _canonical_file(path, expected_sha)
    expected_seal = seal_document(document, seal_field="bridge_sha256", domain=f"{DOMAIN}.receipt_bridge.v1", version=1)
    if document.get("bridge_sha256") != expected_seal:
        raise VerificationError("BRIDGE_SEAL_MISMATCH")
    compressed = base64.b64decode(document.get("compressed_container_base64", ""), validate=True)
    compression = document.get("compression")
    if not isinstance(compression, Mapping):
        raise VerificationError("BRIDGE_COMPRESSION_MISSING")
    if len(compressed) != compression.get("compressed_bytes") or sha(compressed) != compression.get("compressed_sha256"):
        raise VerificationError("BRIDGE_COMPRESSED_IDENTITY_MISMATCH")
    try:
        container_payload = gzip.decompress(compressed)
    except Exception as exc:  # noqa: BLE001
        raise VerificationError("BRIDGE_GZIP_INVALID") from exc
    if len(container_payload) != compression.get("uncompressed_bytes") or sha(container_payload) != compression.get("uncompressed_sha256"):
        raise VerificationError("BRIDGE_UNCOMPRESSED_IDENTITY_MISMATCH")
    container = json.loads(container_payload)
    if container_payload != canonical_json_bytes(container) + b"\n":
        raise VerificationError("BRIDGE_CONTAINER_NONCANONICAL")
    entries = container.get("entries")
    if not isinstance(entries, list) or len(entries) != 144:
        raise VerificationError("BRIDGE_ENTRY_COUNT_MISMATCH")
    manifest = []
    phase_rows = []
    cells = Counter()
    for entry in entries:
        raw = base64.b64decode(entry.get("raw_base64", ""), validate=True)
        if len(raw) != entry.get("raw_bytes") or sha(raw) != entry.get("raw_sha256"):
            raise VerificationError("BRIDGE_RAW_RECEIPT_IDENTITY_MISMATCH")
        receipt = json.loads(raw)
        if receipt.get("mode") != "COLD_FRESH_PROCESS":
            raise VerificationError("BRIDGE_NON_COLD_RECEIPT")
        phase_rows.append(_phase_row(receipt))
        cells[(receipt.get("task"), receipt.get("arm"))] += 1
        manifest.append({"member": entry.get("member"), "raw_bytes": len(raw), "raw_sha256": sha(raw)})
    if manifest != document.get("entry_manifest"):
        raise VerificationError("BRIDGE_MANIFEST_MISMATCH")
    if len(cells) != 6 or set(cells.values()) != {24}:
        raise VerificationError("BRIDGE_CELL_COUNTS_MISMATCH")
    ledger_payload = V1_LEDGER.read_bytes()
    if len(ledger_payload) != V1_LEDGER_BYTES or sha(ledger_payload) != V1_LEDGER_SHA256:
        raise VerificationError("V1_LEDGER_IDENTITY_MISMATCH")
    ledger = json.loads(ledger_payload)
    if phase_rows != ledger.get("rows"):
        raise VerificationError("BRIDGE_PHASE_ROWS_MISMATCH")
    if sha(canonical_json_bytes(phase_rows)) != document.get("raw_phase_rows_sha256"):
        raise VerificationError("BRIDGE_PHASE_ROWS_DIGEST_MISMATCH")
    return {
        "file_bytes": len(payload),
        "file_sha256": sha(payload),
        "raw_receipts": 144,
        "cells": 6,
        "samples_per_cell": 24,
        "phase_rows_rebuilt_exactly": True,
        "new_timing_samples": 0,
    }


def build_verification(contract_sha: str, registry_sha: str, bridge_sha: str) -> dict[str, Any]:
    contract = verify_contract(CONTRACT, contract_sha)
    registry = verify_registry(REGISTRY_AMENDMENT, registry_sha)
    bridge = verify_bridge(RECEIPT_BRIDGE, bridge_sha)
    document: dict[str, Any] = {
        "schema": "rtdl.goal5799.a1.independent_post_self_review_repair_verification.v1",
        "date": "2026-08-24",
        "status": "PASS__INDEPENDENT_POST_SELF_REVIEW_REPAIR_VERIFICATION",
        "imports_repair_builder": False,
        "external_expected_file_identities": {
            "contract_sha256": contract_sha,
            "registry_amendment_sha256": registry_sha,
            "receipt_bridge_sha256": bridge_sha,
        },
        "contract": contract,
        "registry": registry,
        "receipt_bridge": bridge,
        "authorization": {
            "formal_timing": False,
            "network": False,
            "gpu_pod": False,
            "goal5803": False,
        },
        "verification_sha256": "",
    }
    document["verification_sha256"] = seal_document(
        document,
        seal_field="verification_sha256",
        domain=f"{DOMAIN}.independent_verification.v1",
        version=1,
    )
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-contract-sha256", required=True)
    parser.add_argument("--expected-registry-amendment-sha256", required=True)
    parser.add_argument("--expected-receipt-bridge-sha256", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--write-create-only", action="store_true")
    mode.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    for value in (args.expected_contract_sha256, args.expected_registry_amendment_sha256, args.expected_receipt_bridge_sha256):
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            parser.error("expected SHA-256 values must be lowercase hex")
    document = build_verification(
        args.expected_contract_sha256,
        args.expected_registry_amendment_sha256,
        args.expected_receipt_bridge_sha256,
    )
    payload = canonical_json_bytes(document) + b"\n"
    if args.write_create_only:
        if OUTPUT.exists() or OUTPUT.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        with OUTPUT.open("xb") as stream:
            stream.write(payload)
        status = "CREATE_ONLY_WRITE_PASS"
    elif args.verify_stored:
        if not OUTPUT.is_file() or OUTPUT.is_symlink() or OUTPUT.read_bytes() != payload:
            raise SystemExit("STORED_VERIFICATION_MISMATCH")
        status = "POSTWRITE_VERIFY_PASS"
    else:
        status = "DRY_RUN_PASS"
    print(json.dumps({"status": status, "bytes": len(payload), "sha256": sha(payload)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
