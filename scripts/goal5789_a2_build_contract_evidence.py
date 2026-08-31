"""Build Goal5789-A2 certificates from immutable Goal5789 predecessors.

The builder cannot create or modify the Callback-IR authority.  It migrates
the frozen v1 certificates byte-for-byte except for the successor schema,
certificate seal, and the callback summary copied from the already frozen A2
authority.  New dispositions are computed rather than forced to reproduce the
predecessor 6/9/0 vector.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from scripts import goal5789_a2_independent_compatibility_checker as checker


ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "history/internal_docs/goal5789_contract_evidence_20260816"
OUT = ROOT / "history/internal_docs/goal5789_a2_contract_evidence_20260821"
CALLBACK_AUTHORITY = OUT / "CALLBACK_IR_AUTHORITY.json"
CALLBACK_PIN = OUT / "CALLBACK_IR_AUTHORITY_PIN.json"
TERMINAL = ROOT / "history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json"
PREDECESSOR_MANIFEST_REL = "history/internal_docs/goal5789_delivery_manifest_20260816.json"
PREDECESSOR_MANIFEST_SHA256 = "523c95139d24a84ad2ad02ff1e0bb3ee60fc87e540cdaca112c8b74870ef7667"
PREDECESSOR_MANIFEST_BYTES = 13_176
TERMINAL_SHA256 = "8a2960140381d7564a36a67c7024f2554bafe379621eef844c3edab0157be7be"
TERMINAL_BYTES = 7_647
TERMINAL_INTERNAL_SHA256 = "96d1107848d5a41cfe8016a9dcb056e6b7e85679b1a61c21669eb39449f7f862"
WORK_AUTHORITY_REL = "history/internal_docs/goal5789_a2_callback_ir_authority_binding_work_authority_20260821.json"
WORK_AUTHORITY_SHA256 = "7631ca7486afcb5515f79e99de3c3bb4020328c95bafd3d8bfe94697c5da0c1a"
WORK_AUTHORITY_BYTES = 4_556
WORK_AUTHORITY_INTERNAL_SHA256 = "e18658e0ed000de310f6bc3797e938c498f58d2de2071d9d50494781c69b6f08"


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _validate_predecessor_and_work_roots() -> None:
    manifest_path = ROOT / PREDECESSOR_MANIFEST_REL
    if (
        not manifest_path.is_file()
        or manifest_path.stat().st_size != PREDECESSOR_MANIFEST_BYTES
        or _sha_file(manifest_path) != PREDECESSOR_MANIFEST_SHA256
    ):
        raise RuntimeError("frozen Goal5789 predecessor delivery manifest identity mismatch")
    manifest = _load(manifest_path)
    rows = manifest.get("payloads")
    if (
        manifest.get("schema") != "rtdl.goal5789.delivery_manifest.v1"
        or manifest.get("payload_count") != 54
        or manifest.get("payload_bytes") != 22_224_751
        or not isinstance(rows, list)
        or len(rows) != 54
    ):
        raise RuntimeError("frozen Goal5789 predecessor delivery manifest content mismatch")
    seen: set[str] = set()
    total_bytes = 0
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "sha256", "bytes"}:
            raise RuntimeError("invalid predecessor delivery manifest row")
        relative = row["path"]
        if not isinstance(relative, str) or relative in seen:
            raise RuntimeError("duplicate predecessor delivery manifest path")
        seen.add(relative)
        path = ROOT / relative
        if (
            not path.is_file()
            or path.stat().st_size != row["bytes"]
            or _sha_file(path) != row["sha256"]
        ):
            raise RuntimeError(f"frozen Goal5789 predecessor payload mismatch: {relative}")
        total_bytes += int(row["bytes"])
    if total_bytes != manifest["payload_bytes"]:
        raise RuntimeError("frozen Goal5789 predecessor payload byte total mismatch")

    if (
        not TERMINAL.is_file()
        or TERMINAL.stat().st_size != TERMINAL_BYTES
        or _sha_file(TERMINAL) != TERMINAL_SHA256
    ):
        raise RuntimeError("controlling postreview P1 terminal identity mismatch")
    terminal = _load(TERMINAL)
    if (
        terminal.get("terminal_sha256") != TERMINAL_INTERNAL_SHA256
        or checker.digest(
            {key: value for key, value in terminal.items() if key != "terminal_sha256"}
        )
        != TERMINAL_INTERNAL_SHA256
    ):
        raise RuntimeError("controlling postreview P1 terminal seal mismatch")

    work_path = ROOT / WORK_AUTHORITY_REL
    if (
        not work_path.is_file()
        or work_path.stat().st_size != WORK_AUTHORITY_BYTES
        or _sha_file(work_path) != WORK_AUTHORITY_SHA256
    ):
        raise RuntimeError("A2 owner work authority identity mismatch")
    work = _load(work_path)
    if (
        work.get("work_authority_sha256") != WORK_AUTHORITY_INTERNAL_SHA256
        or checker.digest(
            {
                key: value
                for key, value in work.items()
                if key != "work_authority_sha256"
            }
        )
        != WORK_AUTHORITY_INTERNAL_SHA256
    ):
        raise RuntimeError("A2 owner work authority seal mismatch")


def _pretty(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _seal_section(section: dict[str, Any]) -> None:
    section["authority_sha256"] = checker.v1.nested_authority_digest(section)


def _authority_binding(callback_authority: Mapping[str, object], callback_pin: Mapping[str, object]) -> dict[str, object]:
    binding: dict[str, object] = {
        "schema": checker.CALLBACK_BINDING_SCHEMA,
        "authority_sha256": "",
        "callback_authority_path": "history/internal_docs/goal5789_a2_contract_evidence_20260821/CALLBACK_IR_AUTHORITY.json",
        "callback_authority_file_sha256": checker.file_digest_from_object(callback_authority),
        "callback_authority_sha256": callback_authority["authority_sha256"],
        "callback_authority_pin_path": "history/internal_docs/goal5789_a2_contract_evidence_20260821/CALLBACK_IR_AUTHORITY_PIN.json",
        "callback_authority_pin_file_sha256": checker.file_digest_from_object(callback_pin),
        "callback_authority_pin_sha256": callback_pin["pin_sha256"],
    }
    _seal_section(binding)
    return binding


def _migrate_authority(
    predecessor: Mapping[str, object],
    callback_authority: Mapping[str, object],
    callback_pin: Mapping[str, object],
) -> dict[str, object]:
    value = deepcopy(dict(predecessor))
    value["schema"] = checker.AUTHORITY_SCHEMA
    value["callback_ir_authority_binding"] = _authority_binding(callback_authority, callback_pin)
    value["authority_sha256"] = checker.authority_digest(value)
    return value


def _migrate_certificate(
    predecessor: Mapping[str, object],
    callback_authority: Mapping[str, object],
) -> dict[str, object]:
    value = deepcopy(dict(predecessor))
    physical = value.get("physical_encoding")
    semantic = value.get("semantic_request")
    if (
        not isinstance(physical, Mapping)
        or not isinstance(physical.get("encoding_id"), str)
        or not isinstance(semantic, Mapping)
        or not isinstance(semantic.get("contract_id"), str)
    ):
        raise RuntimeError("predecessor certificate missing physical encoding identity")
    programs = callback_authority.get("programs")
    bindings = callback_authority.get("admitted_bindings")
    if not isinstance(programs, Mapping) or not isinstance(bindings, list):
        raise RuntimeError("callback authority program catalog missing")
    matches = [
        row for row in bindings
        if isinstance(row, Mapping)
        and row.get("semantic_contract_id") == semantic["contract_id"]
        and row.get("physical_encoding_id") == physical["encoding_id"]
    ]
    if len(matches) > 1:
        raise RuntimeError("ambiguous callback authority binding")
    value["schema"] = checker.CERTIFICATE_SCHEMA
    if not matches:
        value["callback_contract"] = None
    else:
        program = programs.get(matches[0]["authority_program_sha256"])
        if not isinstance(program, Mapping) or not isinstance(program.get("callback_contract"), Mapping):
            raise RuntimeError("admitted callback authority program missing")
        value["callback_contract"] = deepcopy(dict(program["callback_contract"]))
    value["certificate_sha256"] = checker.certificate_digest(value)
    return value


def _identity(relative: str) -> dict[str, object]:
    path = ROOT / relative
    return {
        "path": relative,
        "size_bytes": path.stat().st_size,
        "file_sha256": _sha_file(path),
    }


def _result_projection(result: Mapping[str, object]) -> dict[str, object]:
    return {
        "target_capable": result["target_capable"]["verdict"],
        "semantic_compatible": result["semantic_compatible"]["verdict"],
        "semantic_reasons": list(result["semantic_compatible"]["reasons"]),
        "instance_admissible": result["instance_admissible"]["verdict"],
        "canonical_resolution": result["canonical_resolution"]["verdict"],
        "reference_admission_complete": result["reference_admission_complete"],
        "performance": result["performance"]["verdict"],
    }


def build_payloads(
    callback_authority: Mapping[str, object] | None = None,
    callback_pin: Mapping[str, object] | None = None,
) -> dict[str, bytes]:
    _validate_predecessor_and_work_roots()
    loaded_from_frozen_files = callback_authority is None and callback_pin is None
    if (callback_authority is None) != (callback_pin is None):
        raise RuntimeError("callback authority and pin must be supplied together")
    if loaded_from_frozen_files:
        if not CALLBACK_AUTHORITY.is_file() or not CALLBACK_PIN.is_file():
            raise RuntimeError("frozen A2 Callback-IR authority and pin must exist before certificate build")
        callback_authority = _load(CALLBACK_AUTHORITY)
        callback_pin = _load(CALLBACK_PIN)
    assert callback_authority is not None and callback_pin is not None
    if checker.callback_authority_digest(callback_authority) != callback_authority.get("authority_sha256"):
        raise RuntimeError("callback authority self-seal mismatch")
    if checker.callback_pin_digest(callback_pin) != callback_pin.get("pin_sha256"):
        raise RuntimeError("callback authority pin self-seal mismatch")
    actual_authority_file_sha = (
        _sha_file(CALLBACK_AUTHORITY)
        if loaded_from_frozen_files
        else checker.file_digest_from_object(callback_authority)
    )
    if callback_pin.get("callback_authority", {}).get("file_sha256") != actual_authority_file_sha:
        raise RuntimeError("callback authority external pin mismatch")
    if set(callback_authority.get("programs", {})) != checker.EXPECTED_PROGRAM_SHA256S:
        raise RuntimeError("callback authority program universe differs from reviewed A2 identities")
    if checker.canonical_bytes(callback_authority.get("admitted_bindings")) != checker.canonical_bytes(
        checker.EXPECTED_ADMITTED_BINDINGS
    ):
        raise RuntimeError("callback authority pair-to-program map differs from reviewed A2 mapping")
    if checker.canonical_bytes(callback_authority.get("claim_boundary")) != checker.canonical_bytes(
        checker.EXPECTED_CALLBACK_AUTHORITY_CLAIM_BOUNDARY
    ):
        raise RuntimeError("callback authority claim boundary differs from reviewed A2 boundary")
    for field, expected in (
        ("source_archive", checker.EXPECTED_SOURCE_ARCHIVE_IDENTITY),
        ("execution_evidence_archive", checker.EXPECTED_EXECUTION_EVIDENCE_IDENTITY),
        ("controlling_result", checker.EXPECTED_CONTROLLING_RESULT_IDENTITY),
        ("execution_leaf_manifest", checker.EXPECTED_EXECUTION_LEAF_MANIFEST_IDENTITY),
    ):
        if checker.canonical_bytes(callback_authority.get(field)) != checker.canonical_bytes(
            expected
        ):
            raise RuntimeError(f"callback authority reviewed identity mismatch: {field}")
    for program_sha256, expected in checker.EXPECTED_PROGRAM_METADATA_BY_SHA256.items():
        row = callback_authority["programs"][program_sha256]
        actual = {
            key: row.get(key)
            for key in (
                "alias",
                "callback_authority_id",
                "compile_entrypoint",
                "selected_constructor_source_paths",
            )
        }
        if checker.canonical_bytes(actual) != checker.canonical_bytes(expected):
            raise RuntimeError(
                f"callback authority producer metadata mismatch: {program_sha256}"
            )
    if checker.canonical_bytes(callback_pin.get("authorization")) != checker.canonical_bytes(
        checker.EXPECTED_CALLBACK_PIN_AUTHORIZATION
    ):
        raise RuntimeError("callback authority pin authorization is not exact all-false")

    old_authority = _load(OLD / "AUTHORITY_BUNDLE.json")
    authority = _migrate_authority(old_authority, callback_authority, callback_pin)
    payloads: dict[str, bytes] = {"AUTHORITY_BUNDLE.json": _pretty(authority)}
    inventory_rows: list[dict[str, object]] = []
    predecessor_rows: list[dict[str, object]] = []
    old_inventory = _load(OLD / "BOUNDED_INVENTORY.json")
    for old_row in old_inventory["inventory"]:
        unit_id = old_row["unit_id"]
        old_certificate_path = OLD / "certificates" / f"{unit_id}.json"
        old_result_path = OLD / "results" / f"{unit_id}.json"
        old_certificate = _load(old_certificate_path)
        old_result = _load(old_result_path)
        certificate = _migrate_certificate(old_certificate, callback_authority)
        result = checker.evaluate_certificate(certificate, authority, callback_authority, callback_pin)
        payloads[f"certificates/{unit_id}.json"] = _pretty(certificate)
        payloads[f"results/{unit_id}.json"] = _pretty(result)
        projection = _result_projection(result)
        inventory_rows.append(
            {
                "unit_id": unit_id,
                "contract_id": certificate["semantic_request"]["contract_id"],
                "encoding_id": certificate["physical_encoding"]["encoding_id"],
                "callback_authority_id": (
                    None
                    if certificate["callback_contract"] is None
                    else certificate["callback_contract"]["callback_authority_id"]
                ),
                **projection,
                "semantic_authority_present": old_row["semantic_authority_present"],
                "predecessor_semantic_compatible": old_result["semantic_compatible"]["verdict"],
            }
        )
        predecessor_rows.append(
            {
                "unit_id": unit_id,
                "certificate": {
                    "path": old_certificate_path.relative_to(ROOT).as_posix(),
                    "size_bytes": old_certificate_path.stat().st_size,
                    "file_sha256": _sha_file(old_certificate_path),
                    "certificate_sha256": old_certificate["certificate_sha256"],
                },
                "result": {
                    "path": old_result_path.relative_to(ROOT).as_posix(),
                    "size_bytes": old_result_path.stat().st_size,
                    "file_sha256": _sha_file(old_result_path),
                    "result_sha256": old_result["result_sha256"],
                    "semantic_compatible": old_result["semantic_compatible"]["verdict"],
                },
            }
        )

    old_held_authority = _load(OLD / "HELD_OUT_AUTHORITY_BUNDLE.json")
    old_held_certificate = _load(OLD / "HELD_OUT_RTXRMQ_CERTIFICATE.json")
    old_held_result = _load(OLD / "HELD_OUT_RTXRMQ_RESULT.json")
    held_authority = _migrate_authority(old_held_authority, callback_authority, callback_pin)
    held_certificate = _migrate_certificate(old_held_certificate, callback_authority)
    held_result = checker.evaluate_certificate(
        held_certificate, held_authority, callback_authority, callback_pin
    )
    payloads["HELD_OUT_AUTHORITY_BUNDLE.json"] = _pretty(held_authority)
    payloads["HELD_OUT_RTXRMQ_CERTIFICATE.json"] = _pretty(held_certificate)
    payloads["HELD_OUT_RTXRMQ_RESULT.json"] = _pretty(held_result)

    compatible_count = sum(row["semantic_compatible"] == checker.COMPATIBLE for row in inventory_rows)
    unknown_count = sum(row["semantic_compatible"] == checker.UNKNOWN for row in inventory_rows)
    incompatible_count = sum(row["semantic_compatible"] == checker.INCOMPATIBLE for row in inventory_rows)
    callback_bound_count = sum(row["callback_authority_id"] is not None for row in inventory_rows)
    callback_unbound_count = len(inventory_rows) - callback_bound_count
    inventory: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.bounded_inventory.v1",
        "inventory_sha256": "",
        "predecessor": {
            "compatible_count": old_inventory["semantic_compatible_count"],
            "unknown_count": old_inventory["semantic_unknown_count"],
            "incompatible_count": old_inventory["semantic_incompatible_count"],
            "observation_is_immutable_and_not_replaced": True,
        },
        "successor": {
            "compatible_count": compatible_count,
            "unknown_count": unknown_count,
            "incompatible_count": incompatible_count,
            "counts_were_not_forced": True,
            "callback_authority_bound_count": callback_bound_count,
            "callback_authority_unbound_count": callback_unbound_count,
            "callback_authority_coverage_denominator": len(inventory_rows),
        },
        "inventory": inventory_rows,
        "held_out_result": {
            "predecessor_semantic_compatible": old_held_result["semantic_compatible"]["verdict"],
            "successor_semantic_compatible": held_result["semantic_compatible"]["verdict"],
            "legacy_held_out_name_is_not_checker_held_out_claim": True,
            "no_special_case_replay_only": True,
        },
        "claim_boundary": {
            "registered_catalog_only": True,
            "two_geometry_families_only": True,
            "callback_summary_source_backed_and_authority_bound_for_all_inventory_rows": False,
            "callback_summary_source_backed_and_authority_bound_for_compatible_rows": (
                callback_bound_count == compatible_count
            ),
            "unbound_unknown_callback_integrity_claimed": False,
            "callback_authority_bound_inventory_count": callback_bound_count,
            "callback_authority_unbound_inventory_count": callback_unbound_count,
            "callback_authority_inventory_denominator": len(inventory_rows),
            "authority_producer_is_tcb": True,
            "jointly_wrong_authorities_detected": False,
            "soundness_claimed": False,
            "completeness_claimed": False,
            "false_rejection_rate_claimed": False,
            "goal5793_authorized": False,
            "execution_authorized": False,
        },
    }
    inventory["inventory_sha256"] = checker.digest(
        {key: value for key, value in inventory.items() if key != "inventory_sha256"}
    )
    payloads["BOUNDED_INVENTORY.json"] = _pretty(inventory)

    lineage: dict[str, object] = {
        "schema": "rtdl.goal5789_a2.predecessor_lineage.v1",
        "lineage_sha256": "",
        "predecessor_delivery_manifest": _identity(PREDECESSOR_MANIFEST_REL),
        "predecessor_authority": _identity(
            "history/internal_docs/goal5789_contract_evidence_20260816/AUTHORITY_BUNDLE.json"
        ),
        "predecessor_inventory": _identity(
            "history/internal_docs/goal5789_contract_evidence_20260816/BOUNDED_INVENTORY.json"
        ),
        "predecessor_rows": predecessor_rows,
        "predecessor_held_out": {
            "authority": _identity("history/internal_docs/goal5789_contract_evidence_20260816/HELD_OUT_AUTHORITY_BUNDLE.json"),
            "certificate": _identity("history/internal_docs/goal5789_contract_evidence_20260816/HELD_OUT_RTXRMQ_CERTIFICATE.json"),
            "result": _identity("history/internal_docs/goal5789_contract_evidence_20260816/HELD_OUT_RTXRMQ_RESULT.json"),
        },
        "controlling_p1_terminal": _identity(
            "history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json"
        ),
        "owner_work_authority": _identity(
            "history/internal_docs/goal5789_a2_callback_ir_authority_binding_work_authority_20260821.json"
        ),
        "predecessor_bytes_modified_count": 0,
        "predecessor_observation_replaced": False,
        "goal5793_authorized": False,
    }
    lineage["lineage_sha256"] = checker.digest(
        {key: value for key, value in lineage.items() if key != "lineage_sha256"}
    )
    payloads["PREDECESSOR_LINEAGE.json"] = _pretty(lineage)
    return payloads


def main() -> int:
    payloads = build_payloads()
    targets = [OUT / relative for relative in payloads]
    existing = [path for path in targets if path.exists()]
    if existing:
        raise RuntimeError(f"A2 contract evidence outputs are create-only: {existing}")
    written: list[Path] = []
    try:
        for relative, content in sorted(payloads.items()):
            path = OUT / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(content)
            written.append(path)
    except BaseException:
        for path in reversed(written):
            path.unlink(missing_ok=True)
        raise
    print(json.dumps({
        "payload_count": len(payloads),
        "inventory_file_sha256": _sha_file(OUT / "BOUNDED_INVENTORY.json"),
        "lineage_file_sha256": _sha_file(OUT / "PREDECESSOR_LINEAGE.json"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
