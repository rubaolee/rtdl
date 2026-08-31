"""Standalone verifier for the Goal5793 X1 S0 reproduction capsule.

The verifier intentionally uses only the Python standard library and the
capsule's sibling ``goal5793_x1_canonical.py`` helper.  It never imports the
product, the historical S0 builders, or workspace ``src``; invokes Git; or
uses a network API.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

sys.dont_write_bytecode = True

try:
    from goal5793_x1_canonical import (
        CANONICALIZATION_NAME,
        canonical_json_bytes,
        seal_document,
        sha256_bytes,
    )
except ModuleNotFoundError:  # Imported as ``scripts.<module>`` in workspace tests.
    from scripts.goal5793_x1_canonical import (  # type: ignore
        CANONICALIZATION_NAME,
        canonical_json_bytes,
        seal_document,
        sha256_bytes,
    )


DATE = "2026-08-22"
CAPSULE_DIRNAME = "goal5793_x1_s0_reproduction_capsule"
MANIFEST_DOMAIN = "rtdl.goal5793.x1.s0_reproduction_capsule.manifest"
AUDIT_DOMAIN = "rtdl.goal5793.x1.s0_reproduction_capsule.audit"

SOURCE_NAME = "goal5793_s0_source_and_admission_freeze_20260822.json"
CANDIDATE_NAME = "goal5793_s0_known_universe_requalification_20260822.json"
PROTOCOL_NAME = "goal5793_s0_protocol_and_stage_authority_20260822.json"
RESULT_NAME = "goal5793_s0_preregistration_result_20260822.json"
INDEPENDENT_AUDIT_NAME = "goal5793_s0_independent_audit_20260822.json"
REPORT_NAME = "goal5793_s0_preregistration_technical_report_20260822.md"
SELF_REVIEW_NAME = "self_review_goal5793_s0_preregistration_20260822.md"
CFR_NAME = "call_for_review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md"
REVIEW_NAME = "review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md"
RECEIPT_NAME = "goal5793_s0_owner_send_receipt_20260822.json"
ABSORPTION_NAME = "goal5793_s0_owner_returned_external_review_absorption_20260822.json"
CLOSURE_NAME = "goal5793_s0_postreview_closure_and_x1_entry_20260822.json"

S0_DIR = "payload/s0"
V26_PATH = "payload/source_archive/goal5791_portable_source_v26_20260820.tar.gz"
DELTA_VERSION_PATH = "payload/source_deltas/VERSION"
DELTA_REQUIREMENTS_PATH = "payload/source_deltas/requirements.txt"
GOAL519_BLOB_PATH = (
    "payload/historical_blobs/"
    "goal519_rt_workload_universe_from_2603_28771_2026-04-17.md"
)
GOAL521_BLOB_PATH = (
    "payload/historical_blobs/"
    "goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md"
)

EXPECTED_SEALS = {
    SOURCE_NAME: (
        "source_authority_sha256",
        "5107d019ff5c583645e3c101021678e84381546c32310b0027ec9220ee1b4dd3",
    ),
    CANDIDATE_NAME: (
        "candidate_authority_sha256",
        "5567828708f4af7d0029880af71783cec8c267c7c9100fee949311586ebce4a0",
    ),
    PROTOCOL_NAME: (
        "protocol_authority_sha256",
        "bcdef49272ec413334edc3c9b5d3f201c8b3586f943ab2d87c032f316cfe8a4e",
    ),
    RESULT_NAME: (
        "result_sha256",
        "5e21a1a3500ec7fd125a89d0c1954d2cb34baccac6f242b904cd9cd4aa254099",
    ),
    INDEPENDENT_AUDIT_NAME: (
        "audit_sha256",
        "41959beff83496f0a469000db8fe0e581cc2f395e0de78834479627de0e7b69c",
    ),
    RECEIPT_NAME: (
        "receipt_sha256",
        "c0fec7105a51a1cf10beaa4e00f1e375240996d8c4c77d9d06abd5cfc85b095e",
    ),
    ABSORPTION_NAME: (
        "absorption_sha256",
        "e020ae2a1b100d5cccf5ab7a8a6370887c1fd4c7f650e79a54debc3aa42f3e60",
    ),
    CLOSURE_NAME: (
        "closure_sha256",
        "cc118989e6f7462eb236c414c08b7058ea4feacc8e4bac27898f9254bcb90a1a",
    ),
}

EXPECTED_SOURCE_SUMMARY = {
    "file_count": 326,
    "total_bytes": 14587884,
    "rows_canonical_bytes": 46672,
    "rows_sha256": "f26b55e6d9a120a34882e9c7ada44df5503f1f90f83db893d1d6957ab0202f97",
}
EXPECTED_V26 = {
    "bytes": 4124847,
    "sha256": "5f75d2f2793e1ec3151994031bb7ca6121fc058fc8d634ba40ae9e14f6118373",
    "present": 324,
    "missing": ["VERSION", "requirements.txt"],
}
EXPECTED_HISTORICAL_BLOBS = {
    GOAL519_BLOB_PATH: {
        "bytes": 10800,
        "sha256": "972403628507c9655acd5fdaf20349feb859c46929b6dd3431bc4af37dbe6437",
        "commit": "89079f4c0d60b8a8517b8b302170868de1e3e4a7",
        "repository_path": "docs/reports/goal519_rt_workload_universe_from_2603_28771_2026-04-17.md",
    },
    GOAL521_BLOB_PATH: {
        "bytes": 8165,
        "sha256": "590de7ef35aea6244949f187498fb3f45a90e4fc3a59ee0b538f6ba8910169ac",
        "commit": "ccd86697daa54467ab256aeba49798bf9ee06d64",
        "repository_path": "docs/reports/goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md",
    },
}

HOSTILE_IDS = {
    "H01": "ZERO_DRIFT_AUTHORITY_MISMATCH",
    "H02": "EXPLANATORY_SUBMANIFEST_OVERCLAIM",
    "H03": "UNIVERSE_ROW_SET_MISMATCH",
    "H04": "SOURCE_GAP_HYGIENE_FAILURE",
    "H05": "EXPOSURE_AUTHORITY_MISMATCH",
    "H06": "FORBIDDEN_SELECTION_FEATURE_DEPENDENCE",
    "H07": "ROLE_REQUALIFICATION_MISMATCH",
    "H08": "TRIPLET_SET_MISMATCH",
    "H09": "PREMATURE_ENTROPY_OR_SELECTION",
    "H10": "STAGE_PREDECESSOR_UNSATISFIED",
    "H11": "SEARCH_BEFORE_EXAMINER_FREEZE",
    "H12": "EXPANSION_PROTOCOL_DRIFT",
    "H13": "EXAMINER_METADATA_DEPENDENCE",
    "H14": "REGISTRY_DERIVATION_OR_CORE_DRIFT",
    "H15": "ENTROPY_DOMAIN_OR_TARGET_MISMATCH",
    "H16": "POST_OUTCOME_RESCUE",
    "H17": "OUTCOME_DEPENDENT_VALIDITY",
    "H18": "FRICTION_LEDGER_MISMATCH",
    "H19": "USABILITY_OVERCLAIM",
    "H20": "EXPOSURE_CLAIM_OVERREACH",
}


class VerificationFailure(RuntimeError):
    def __init__(self, fail_id: str, detail: str):
        self.fail_id = fail_id
        self.detail = detail
        super().__init__(f"{fail_id}: {detail}")


def fail(fail_id: str, detail: str) -> None:
    raise VerificationFailure(fail_id, detail)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail("CAPSULE_FORMAT_INVALID", f"JSON root is not an object: {path.name}")
    return value


def _identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha256_bytes(data)}


def _legacy_seal(document: Mapping[str, Any], field: str) -> str:
    body = dict(document)
    body.pop(field, None)
    return sha256_bytes(canonical_json_bytes(body))


def _legacy_reseal(document: dict[str, Any], field: str) -> dict[str, Any]:
    value = copy.deepcopy(document)
    value.pop(field, None)
    value[field] = _legacy_seal(value, field)
    return value


def _verify_legacy_seal(
    document: Mapping[str, Any], field: str, expected: str, *, label: str
) -> None:
    claimed = document.get(field)
    if claimed != expected or _legacy_seal(document, field) != expected:
        fail("S0_ROOT_BINDING_MISMATCH", f"{label} {field} mismatch")


def _canonical_relpath(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        fail("CAPSULE_FORMAT_INVALID", "empty or non-text member path")
    path = PurePosixPath(value)
    if (
        path.as_posix() != value
        or path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or "\\" in value
    ):
        fail("CAPSULE_FORMAT_INVALID", f"unsafe/noncanonical path: {value!r}")
    return path


def _manifest_payload_map(root: Path, manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if manifest.get("schema") != "rtdl.goal5793.x1.s0_reproduction_capsule.manifest.v1":
        fail("CAPSULE_MANIFEST_MISMATCH", "manifest schema differs")
    expected_seal = seal_document(
        manifest,
        seal_field="manifest_sha256",
        domain=MANIFEST_DOMAIN,
        version=1,
    )
    if manifest.get("manifest_sha256") != expected_seal:
        fail("CAPSULE_MANIFEST_MISMATCH", "manifest internal seal differs")
    if manifest.get("canonicalization") != CANONICALIZATION_NAME:
        fail("CAPSULE_MANIFEST_MISMATCH", "canonicalization differs")
    if manifest.get("hostile_fail_ids") != HOSTILE_IDS:
        fail("CAPSULE_MANIFEST_MISMATCH", "20 hostile fail ids differ")
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        fail("CAPSULE_MANIFEST_MISMATCH", "payload rows are not objects")
    paths = [row.get("path") for row in rows]
    if paths != sorted(paths, key=lambda item: str(item).encode("utf-8")) or len(paths) != len(set(paths)):
        fail("CAPSULE_MANIFEST_MISMATCH", "payload paths are not sorted unique")
    mapped: dict[str, dict[str, Any]] = {}
    for row in rows:
        rel = str(_canonical_relpath(row.get("path")))
        path = root.joinpath(*PurePosixPath(rel).parts)
        if path.is_symlink() or not path.is_file():
            fail("CAPSULE_PAYLOAD_MISMATCH", f"missing/nonregular payload: {rel}")
        ident = _identity(path)
        if ident != {"bytes": row.get("bytes"), "sha256": row.get("sha256")}:
            fail("CAPSULE_PAYLOAD_MISMATCH", f"payload identity differs: {rel}")
        if not isinstance(row.get("role"), str) or not row["role"]:
            fail("CAPSULE_MANIFEST_MISMATCH", f"payload role missing: {rel}")
        mapped[rel] = row
    actual_files = []
    for path in root.rglob("*"):
        if path.is_symlink():
            fail("CAPSULE_PAYLOAD_MISMATCH", f"symlink forbidden: {path}")
        if path.is_file():
            actual_files.append(path.relative_to(root).as_posix())
    expected_files = sorted([*mapped, "audit.json", "manifest.json"], key=lambda item: item.encode("utf-8"))
    if sorted(actual_files, key=lambda item: item.encode("utf-8")) != expected_files:
        fail("CAPSULE_PAYLOAD_MISMATCH", "unmanifested or missing capsule file")
    summary = {
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
        "rows_sha256": sha256_bytes(canonical_json_bytes(rows)),
    }
    if manifest.get("payload_summary") != summary:
        fail("CAPSULE_MANIFEST_MISMATCH", "payload summary differs")
    return mapped


def _s0_path(root: Path, name: str) -> Path:
    return root / S0_DIR / name


def _verify_s0_root_seals(root: Path) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for name, (field, expected) in EXPECTED_SEALS.items():
        document = _load_json(_s0_path(root, name))
        _verify_legacy_seal(document, field, expected, label=name)
        loaded[name] = document
    return loaded


def _verify_identity_rows(root: Path, rows: Any) -> None:
    if not isinstance(rows, list):
        fail("S0_ROOT_BINDING_MISMATCH", "identity rows are not a list")
    for row in rows:
        if not isinstance(row, dict):
            fail("S0_ROOT_BINDING_MISMATCH", "identity row is not an object")
        name = PurePosixPath(str(row.get("path"))).name
        candidate = _s0_path(root, name)
        if not candidate.is_file():
            candidate = root / "payload/authoring_tools" / name
        if not candidate.is_file():
            candidate = root / "payload/predecessors" / name
        if not candidate.is_file():
            fail("S0_ROOT_BINDING_MISMATCH", f"bound payload absent: {row.get('path')}")
        ident = _identity(candidate)
        expected = {"bytes": row.get("bytes"), "sha256": row.get("file_sha256")}
        if ident != expected:
            fail("S0_ROOT_BINDING_MISMATCH", f"bound identity differs: {row.get('path')}")


def _verify_s0_binding_chain(root: Path, documents: Mapping[str, Mapping[str, Any]]) -> None:
    result = documents[RESULT_NAME]
    _verify_identity_rows(root, result.get("supporting_artifacts"))
    _verify_identity_rows(root, result.get("authoring_tools"))
    predecessor = result.get("predecessor")
    if not isinstance(predecessor, dict):
        fail("S0_ROOT_BINDING_MISMATCH", "result predecessor missing")
    _verify_identity_rows(root, [predecessor])
    audit = documents[INDEPENDENT_AUDIT_NAME]
    _verify_identity_rows(root, audit.get("inputs"))
    candidates = documents[CANDIDATE_NAME]
    _verify_identity_rows(
        root,
        [candidates.get("source_universe"), candidates.get("source_protocol")],
    )
    receipt = documents[RECEIPT_NAME]
    cfr_identity = _identity(_s0_path(root, CFR_NAME))
    if cfr_identity != {
        "bytes": receipt.get("cfr_bytes"),
        "sha256": receipt.get("cfr_file_sha256"),
    }:
        fail("S0_ROOT_BINDING_MISMATCH", "receipt does not bind CFR")
    review_crosscheck = receipt.get("returned_review_crosscheck")
    if not isinstance(review_crosscheck, dict):
        fail("S0_ROOT_BINDING_MISMATCH", "receipt review crosscheck missing")
    if _identity(_s0_path(root, REVIEW_NAME)) != {
        "bytes": review_crosscheck.get("bytes"),
        "sha256": review_crosscheck.get("file_sha256"),
    }:
        fail("S0_ROOT_BINDING_MISMATCH", "receipt does not bind review")
    if review_crosscheck.get("reviewer_rehashed_cfr_file_sha256") != cfr_identity["sha256"]:
        fail("S0_ROOT_BINDING_MISMATCH", "review CFR rehash differs")
    for owner_name in (ABSORPTION_NAME, CLOSURE_NAME):
        owner_doc = documents[owner_name]
        _verify_identity_rows(root, owner_doc.get("bound_files"))


def _safe_v26_rows(archive_path: Path) -> dict[str, dict[str, Any]]:
    seen: set[str] = set()
    rows: dict[str, dict[str, Any]] = {}
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive:
            rel = str(_canonical_relpath(member.name))
            if rel in seen:
                fail("SOURCE_CUSTODY_MISMATCH", f"duplicate v26 member: {rel}")
            seen.add(rel)
            if member.isdir():
                continue
            if not member.isreg():
                fail("SOURCE_CUSTODY_MISMATCH", f"unsafe v26 member type: {rel}")
            handle = archive.extractfile(member)
            if handle is None:
                fail("SOURCE_CUSTODY_MISMATCH", f"unreadable v26 member: {rel}")
            data = handle.read()
            if len(data) != member.size:
                fail("SOURCE_CUSTODY_MISMATCH", f"short v26 member: {rel}")
            rows[rel] = {"bytes": len(data), "sha256": sha256_bytes(data)}
    return rows


def _verify_source_custody(root: Path, source: Mapping[str, Any]) -> dict[str, int]:
    archive_path = root / V26_PATH
    if _identity(archive_path) != {
        "bytes": EXPECTED_V26["bytes"],
        "sha256": EXPECTED_V26["sha256"],
    }:
        fail("SOURCE_CUSTODY_MISMATCH", "v26 archive identity differs")
    authority = source.get("declared_product_native_source_zero_drift_authority")
    if not isinstance(authority, dict):
        fail("SOURCE_CUSTODY_MISMATCH", "source authority missing")
    rows = authority.get("rows")
    if not isinstance(rows, list):
        fail("SOURCE_CUSTODY_MISMATCH", "source rows missing")
    computed_summary = {
        "file_count": len(rows),
        "total_bytes": sum(int(row.get("size_bytes", -1)) for row in rows),
        "rows_canonical_bytes": len(canonical_json_bytes(rows)),
        "rows_sha256": sha256_bytes(canonical_json_bytes(rows)),
    }
    if computed_summary != EXPECTED_SOURCE_SUMMARY or authority.get("summary") != EXPECTED_SOURCE_SUMMARY:
        fail("SOURCE_CUSTODY_MISMATCH", "326-row source summary differs")
    v26 = _safe_v26_rows(archive_path)
    missing: list[str] = []
    mismatch: list[str] = []
    for row in rows:
        rel = row.get("path")
        expected = {"bytes": row.get("size_bytes"), "sha256": row.get("sha256")}
        if rel in v26:
            if v26[rel] != expected:
                mismatch.append(str(rel))
        else:
            missing.append(str(rel))
    if mismatch or missing != EXPECTED_V26["missing"] or len(rows) - len(missing) != EXPECTED_V26["present"]:
        fail("SOURCE_CUSTODY_MISMATCH", f"v26 projection differs; missing={missing}, mismatch={mismatch}")
    deltas = {
        "VERSION": _identity(root / DELTA_VERSION_PATH),
        "requirements.txt": _identity(root / DELTA_REQUIREMENTS_PATH),
    }
    expected_by_path = {
        str(row["path"]): {"bytes": row["size_bytes"], "sha256": row["sha256"]}
        for row in rows
    }
    if any(deltas[name] != expected_by_path[name] for name in deltas):
        fail("SOURCE_CUSTODY_MISMATCH", "VERSION/requirements delta differs")
    return {"source_rows": len(rows), "v26_identical_rows": 324, "delta_rows": 2}


def _verify_historical_blobs(root: Path, candidates: Mapping[str, Any]) -> int:
    roots = candidates.get("historical_author_exposure", {}).get("roots")
    if not isinstance(roots, list) or len(roots) != 2:
        fail("HISTORICAL_BLOB_MISMATCH", "historical exposure roots differ")
    expected_roots = []
    for rel, expected in EXPECTED_HISTORICAL_BLOBS.items():
        if _identity(root / rel) != {"bytes": expected["bytes"], "sha256": expected["sha256"]}:
            fail("HISTORICAL_BLOB_MISMATCH", f"historical blob differs: {rel}")
        expected_roots.append(
            {
                "commit": expected["commit"],
                "path": expected["repository_path"],
                "bytes": expected["bytes"],
                "sha256": expected["sha256"],
                "meaning": next(
                    row["meaning"]
                    for row in roots
                    if row.get("commit") == expected["commit"] and row.get("path") == expected["repository_path"]
                ),
            }
        )
    if roots != expected_roots:
        fail("HISTORICAL_BLOB_MISMATCH", "historical root metadata differs")
    exposure = candidates.get("historical_author_exposure", {})
    if exposure.get("normalized_workload_family_count") != 32 or len(exposure.get("normalized_workload_families", [])) != 32:
        fail("HISTORICAL_BLOB_MISMATCH", "32-family projection differs")
    return 2


def _semantic_validation(
    source: Mapping[str, Any],
    candidates: Mapping[str, Any],
    protocol: Mapping[str, Any],
    reference_source: Mapping[str, Any],
    reference_candidates: Mapping[str, Any],
    reference_protocol: Mapping[str, Any],
) -> None:
    authority = source.get("declared_product_native_source_zero_drift_authority", {})
    reference_authority = reference_source["declared_product_native_source_zero_drift_authority"]
    if authority.get("rows") != reference_authority.get("rows") or authority.get("summary") != reference_authority.get("summary"):
        fail(HOSTILE_IDS["H01"], "326-row authority differs")
    if source.get("critical_explanatory_submanifest", {}).get("complete_authority") is not False:
        fail(HOSTILE_IDS["H02"], "41-row explanatory list marked complete")
    if [row.get("candidate_id") for row in candidates.get("rows", [])] != [
        row.get("candidate_id") for row in reference_candidates["rows"]
    ]:
        fail(HOSTILE_IDS["H03"], "35-row universe differs")
    source_gap_ids = {
        row["candidate_id"]
        for row in reference_candidates["rows"]
        if row.get("eligibility_status") == "SOURCE_GAP_ANALYZED__PERMANENTLY_SELECTION_INELIGIBLE"
    }
    rows_by_id = {row.get("candidate_id"): row for row in candidates.get("rows", [])}
    reference_rows = {row["candidate_id"]: row for row in reference_candidates["rows"]}
    for candidate_id in source_gap_ids:
        if rows_by_id[candidate_id].get("primary_source_requalification") != reference_rows[candidate_id].get("primary_source_requalification"):
            fail(HOSTILE_IDS["H04"], f"source gap differs: {candidate_id}")
    if candidates.get("source_evidence_reachability") != reference_candidates.get("source_evidence_reachability"):
        fail(HOSTILE_IDS["H04"], "source reachability boundary differs")
    full_text_policy = protocol.get("x2_systematic_expansion", {}).get("uniform_full_text_resolution", {})
    if full_text_policy.get("general_web_search_author_homepage_search_or_manual_extra_attempt_allowed") is not False:
        fail(HOSTILE_IDS["H04"], "manual source rescue enabled")
    if candidates.get("historical_author_exposure") != reference_candidates.get("historical_author_exposure"):
        fail(HOSTILE_IDS["H05"], "historical exposure roots differ")
    exposure_fields = (
        "paper_identity_visible_via_goal5753_catalog",
        "normalized_workload_family_assessed_via_goal519_521",
        "historical_catalog_roots",
    )
    for candidate_id, row in rows_by_id.items():
        if any(row.get(key) != reference_rows[candidate_id].get(key) for key in exposure_fields):
            fail(HOSTILE_IDS["H05"], f"row exposure differs: {candidate_id}")
        if row.get("performance_or_ease_used_for_eligibility") is not False:
            fail(HOSTILE_IDS["H06"], f"performance/ease affects eligibility: {candidate_id}")
    if candidates.get("uniform_policy") != reference_candidates.get("uniform_policy"):
        fail(HOSTILE_IDS["H07"], "uniform role/eligibility policy differs")
    if candidates.get("counts") != reference_candidates.get("counts"):
        fail(HOSTILE_IDS["H07"], "role counts differ")
    role_fields = (
        "selection_eligible",
        "selection_forbidden",
        "role_a_unconventional_correct_expected_admission",
        "role_b_different_geometry_or_composition",
        "role_c_non_obvious_risk",
    )
    for candidate_id, row in rows_by_id.items():
        if any(row.get(key) != reference_rows[candidate_id].get(key) for key in role_fields):
            fail(HOSTILE_IDS["H07"], f"role projection differs: {candidate_id}")
    if candidates.get("ordered_triplets") != reference_candidates.get("ordered_triplets") or candidates.get(
        "ordered_triplet_rows_sha256"
    ) != reference_candidates.get("ordered_triplet_rows_sha256"):
        fail(HOSTILE_IDS["H08"], "triplet set differs")
    current = protocol.get("current_literals", {})
    reference_current = reference_protocol["current_literals"]
    premature_keys = (
        "anchor",
        "target",
        "selected_triplet",
        "entropy_draw_count",
        "selected_candidate_count",
        "candidate_implementation_count",
        "exam_count",
    )
    if any(current.get(key) != reference_current.get(key) for key in premature_keys):
        fail(HOSTILE_IDS["H09"], "entropy/selection/implementation literal differs")
    if protocol.get("authorization") != reference_protocol.get("authorization"):
        fail(HOSTILE_IDS["H10"], "authorization keyset/value differs")
    if protocol.get("state_machine") != reference_protocol.get("state_machine") or protocol.get("current_state") != reference_protocol.get("current_state"):
        fail(HOSTILE_IDS["H11"], "examiner/search state order differs")
    if protocol.get("x2_systematic_expansion") != reference_protocol.get("x2_systematic_expansion"):
        fail(HOSTILE_IDS["H12"], "expansion protocol differs")
    if protocol.get("x1_generic_examiner_contract", {}).get("decision_code_forbidden_inputs") != reference_protocol[
        "x1_generic_examiner_contract"
    ].get("decision_code_forbidden_inputs"):
        fail(HOSTILE_IDS["H13"], "examiner forbidden-input set differs")
    if protocol.get("x1_generic_examiner_contract", {}).get("registry_derivation") != reference_protocol[
        "x1_generic_examiner_contract"
    ].get("registry_derivation"):
        fail(HOSTILE_IDS["H14"], "registry derivation differs")
    if protocol.get("permanent_goal5793_invariants") != reference_protocol.get("permanent_goal5793_invariants"):
        fail(HOSTILE_IDS["H14"], "permanent core boundary differs")
    if protocol.get("deferred_entropy") != reference_protocol.get("deferred_entropy"):
        fail(HOSTILE_IDS["H15"], "entropy verifier/domain/target differs")
    freeze = protocol.get("postselection_input_and_implementation_freeze", {})
    reference_freeze = reference_protocol["postselection_input_and_implementation_freeze"]
    rescue_keys = ("replacement_row_or_candidate_allowed", "valid_incompatible_unknown_or_zero_of_three")
    if any(freeze.get(key) != reference_freeze.get(key) for key in rescue_keys):
        fail(HOSTILE_IDS["H16"], "post-outcome rescue boundary differs")
    if freeze.get("result_dependent_validity_allowed") != reference_freeze.get("result_dependent_validity_allowed"):
        fail(HOSTILE_IDS["H17"], "outcome-dependent validity enabled")
    ledger = protocol.get("structural_friction_ledger", {})
    reference_ledger = reference_protocol["structural_friction_ledger"]
    if ledger.get("supports_easy_or_better_than_cuda_claim") is not False or ledger.get("usability_study_count") != 0:
        fail(HOSTILE_IDS["H19"], "unsupported usability claim enabled")
    ledger_projection = {key: value for key, value in ledger.items() if key not in {"supports_easy_or_better_than_cuda_claim", "usability_study_count"}}
    reference_projection = {
        key: value
        for key, value in reference_ledger.items()
        if key not in {"supports_easy_or_better_than_cuda_claim", "usability_study_count"}
    }
    if ledger_projection != reference_projection:
        fail(HOSTILE_IDS["H18"], "structural-friction ledger differs")
    for candidate_id, row in rows_by_id.items():
        if any(row.get(key) is not False for key in ("unseen_claimed", "blind_claimed", "held_out_from_design_claimed")):
            fail(HOSTILE_IDS["H20"], f"exposure overclaim: {candidate_id}")


def run_hostile_suite(
    source: Mapping[str, Any], candidates: Mapping[str, Any], protocol: Mapping[str, Any]
) -> list[dict[str, Any]]:
    cases: list[tuple[str, str, dict[str, Any], str, str]] = []

    def add(case_id: str, document_name: str, mutated: dict[str, Any], field: str) -> None:
        cases.append((case_id, HOSTILE_IDS[case_id], mutated, document_name, field))

    # One coordinated-reseal mutation for every stable H01--H20 fail class.
    s = copy.deepcopy(source)
    s["declared_product_native_source_zero_drift_authority"]["rows"] = s[
        "declared_product_native_source_zero_drift_authority"
    ]["rows"][:-1]
    add("H01", "source", _legacy_reseal(s, "source_authority_sha256"), "source_authority_sha256")
    s = copy.deepcopy(source)
    s["critical_explanatory_submanifest"]["complete_authority"] = True
    add("H02", "source", _legacy_reseal(s, "source_authority_sha256"), "source_authority_sha256")
    c = copy.deepcopy(candidates)
    c["rows"] = c["rows"][:-1]
    add("H03", "candidates", _legacy_reseal(c, "candidate_authority_sha256"), "candidate_authority_sha256")
    c = copy.deepcopy(candidates)
    gap = next(
        row
        for row in c["rows"]
        if row["eligibility_status"]
        == "SOURCE_GAP_ANALYZED__PERMANENTLY_SELECTION_INELIGIBLE"
    )
    gap["primary_source_requalification"]["source_gaps"] = []
    add("H04", "candidates", _legacy_reseal(c, "candidate_authority_sha256"), "candidate_authority_sha256")
    c = copy.deepcopy(candidates)
    c["rows"][0]["paper_identity_visible_via_goal5753_catalog"] = False
    add("H05", "candidates", _legacy_reseal(c, "candidate_authority_sha256"), "candidate_authority_sha256")
    c = copy.deepcopy(candidates)
    c["rows"][0]["performance_or_ease_used_for_eligibility"] = True
    add("H06", "candidates", _legacy_reseal(c, "candidate_authority_sha256"), "candidate_authority_sha256")
    c = copy.deepcopy(candidates)
    role_gap = next(
        row
        for row in c["rows"]
        if row["eligibility_status"]
        == "SOURCE_GAP_ANALYZED__PERMANENTLY_SELECTION_INELIGIBLE"
    )
    role_gap["role_a_unconventional_correct_expected_admission"] = "QUALIFIED"
    add("H07", "candidates", _legacy_reseal(c, "candidate_authority_sha256"), "candidate_authority_sha256")
    c = copy.deepcopy(candidates)
    c["ordered_triplets"] = [["a", "b", "c"]]
    c["ordered_triplet_rows_sha256"] = sha256_bytes(
        canonical_json_bytes(c["ordered_triplets"])
    )
    add("H08", "candidates", _legacy_reseal(c, "candidate_authority_sha256"), "candidate_authority_sha256")
    p = copy.deepcopy(protocol)
    p["current_literals"]["anchor"] = {"outputValue": "00" * 64}
    add("H09", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["authorization"]["authorizes_systematic_search"] = True
    add("H10", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    states = p["state_machine"]
    first = states.index("X1_GENERIC_EXAMINER_REGISTRY_ENV_SHARED_NATIVE_IMPLEMENTED_REVIEWED")
    second = states.index("X2_HARVESTER_ENTROPY_CLIENT_AND_EXPANSION_PROTOCOL_IMPLEMENTED_OFFLINE_REVIEWED")
    states[first], states[second] = states[second], states[first]
    add("H11", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["x2_systematic_expansion"]["logical_search_terms"] = ["CUDA"] * 11
    add("H12", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["x1_generic_examiner_contract"]["decision_code_forbidden_inputs"].remove("role_assignment")
    add("H13", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["x1_generic_examiner_contract"]["registry_derivation"]["forbidden_postfreeze_changes"] = ["x"] * 7
    add("H14", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["deferred_entropy"]["alternate_or_next_available_target_allowed"] = True
    add("H15", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["postselection_input_and_implementation_freeze"]["replacement_row_or_candidate_allowed"] = True
    add("H16", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["postselection_input_and_implementation_freeze"]["result_dependent_validity_allowed"] = True
    add("H17", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["structural_friction_ledger"]["required_for_all_three_rows_including_failures"].remove(
        "private API call count and exact call sites"
    )
    add("H18", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    p = copy.deepcopy(protocol)
    p["structural_friction_ledger"]["supports_easy_or_better_than_cuda_claim"] = True
    add("H19", "protocol", _legacy_reseal(p, "protocol_authority_sha256"), "protocol_authority_sha256")
    c = copy.deepcopy(candidates)
    c["rows"][0]["unseen_claimed"] = True
    add("H20", "candidates", _legacy_reseal(c, "candidate_authority_sha256"), "candidate_authority_sha256")

    results: list[dict[str, Any]] = []
    for case_id, expected, mutated, document_name, _field in cases:
        trial_source = mutated if document_name == "source" else source
        trial_candidates = mutated if document_name == "candidates" else candidates
        trial_protocol = mutated if document_name == "protocol" else protocol
        observed = None
        try:
            _semantic_validation(
                trial_source,
                trial_candidates,
                trial_protocol,
                source,
                candidates,
                protocol,
            )
        except VerificationFailure as exc:
            observed = exc.fail_id
        if observed != expected:
            fail("HOSTILE_SUITE_MISMATCH", f"{case_id} expected {expected}, observed {observed}")
        results.append(
            {
                "hostile_id": case_id,
                "expected_fail_id": expected,
                "observed_fail_id": observed,
                "coordinated_reseal": True,
                "pass": True,
            }
        )
    if len(results) != 20 or {row["hostile_id"] for row in results} != set(HOSTILE_IDS):
        fail("HOSTILE_SUITE_MISMATCH", "hostile suite is not exactly H01--H20")
    return results


def recompute_audit(root: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    _manifest_payload_map(root, manifest)
    documents = _verify_s0_root_seals(root)
    _verify_s0_binding_chain(root, documents)
    custody = _verify_source_custody(root, documents[SOURCE_NAME])
    historical_count = _verify_historical_blobs(root, documents[CANDIDATE_NAME])
    _semantic_validation(
        documents[SOURCE_NAME],
        documents[CANDIDATE_NAME],
        documents[PROTOCOL_NAME],
        documents[SOURCE_NAME],
        documents[CANDIDATE_NAME],
        documents[PROTOCOL_NAME],
    )
    hostile_results = run_hostile_suite(
        documents[SOURCE_NAME], documents[CANDIDATE_NAME], documents[PROTOCOL_NAME]
    )
    body: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.s0_reproduction_capsule.audit.v1",
        "goal": 5793,
        "stage": "X1_S0_REPRODUCTION_CAPSULE",
        "date": DATE,
        "status": "PASS__SELF_CONTAINED_326_ROW_RECONSTRUCTION__20_OF_20_HOSTILES__NO_GIT_SRC_NETWORK_OR_BUILD_DOCUMENTS",
        "canonicalization": CANONICALIZATION_NAME,
        "manifest_sha256": manifest["manifest_sha256"],
        "checks": {
            "manifest_payload_count": manifest["payload_summary"]["file_count"],
            "manifest_payload_bytes": manifest["payload_summary"]["total_bytes"],
            "s0_internal_seals_verified": len(EXPECTED_SEALS),
            "s0_binding_chain_verified": True,
            "source_rows_reconstructed": custody["source_rows"],
            "v26_byte_identical_rows": custody["v26_identical_rows"],
            "current_delta_rows": custody["delta_rows"],
            "historical_git_blobs_rehashed": historical_count,
            "historical_workload_family_projection_count": 32,
            "hostile_fail_id_count": len(hostile_results),
            "hostile_fail_id_pass_count": sum(bool(row["pass"]) for row in hostile_results),
            "workspace_src_reads": 0,
            "git_invocations": 0,
            "network_calls": 0,
            "original_build_documents_calls": 0,
        },
        "hostile_results": hostile_results,
        "claim_boundary": {
            "retrospective_reviewability_repair_only": True,
            "original_s0_send_retroactively_called_self_contained": False,
            "reviewed_s0_bytes_changed": False,
            "x1_generic_examiner_implemented": False,
            "x2_search_or_entropy_authorized": False,
            "generalization_evidence_count": 0,
        },
    }
    body["audit_sha256"] = seal_document(
        body,
        seal_field="audit_sha256",
        domain=AUDIT_DOMAIN,
        version=1,
    )
    return body


def verify_capsule_root(root: Path, *, require_audit: bool = True) -> dict[str, Any]:
    root = root.resolve()
    manifest = _load_json(root / "manifest.json")
    recomputed = recompute_audit(root, manifest)
    if require_audit:
        stored = _load_json(root / "audit.json")
        expected_seal = seal_document(
            stored,
            seal_field="audit_sha256",
            domain=AUDIT_DOMAIN,
            version=1,
        )
        if stored.get("audit_sha256") != expected_seal or stored != recomputed:
            fail("CAPSULE_AUDIT_MISMATCH", "stored audit differs from independent recount")
    return recomputed


def _safe_extract_capsule(archive_path: Path, destination: Path) -> Path:
    seen: set[str] = set()
    total_bytes = 0
    member_count = 0
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive:
            rel = str(_canonical_relpath(member.name))
            if rel in seen:
                fail("CAPSULE_ARCHIVE_INVALID", f"duplicate member: {rel}")
            seen.add(rel)
            member_count += 1
            if member_count > 1000:
                fail("CAPSULE_ARCHIVE_INVALID", "member limit exceeded")
            if member.isdir():
                continue
            if not member.isreg():
                fail("CAPSULE_ARCHIVE_INVALID", f"unsafe member type: {rel}")
            total_bytes += member.size
            if total_bytes > 40_000_000:
                fail("CAPSULE_ARCHIVE_INVALID", "uncompressed byte limit exceeded")
            if not rel.startswith(CAPSULE_DIRNAME + "/"):
                fail("CAPSULE_ARCHIVE_INVALID", f"member outside capsule root: {rel}")
            target = destination.joinpath(*PurePosixPath(rel).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            handle = archive.extractfile(member)
            if handle is None:
                fail("CAPSULE_ARCHIVE_INVALID", f"unreadable member: {rel}")
            data = handle.read()
            if len(data) != member.size:
                fail("CAPSULE_ARCHIVE_INVALID", f"short member: {rel}")
            target.write_bytes(data)
    root = destination / CAPSULE_DIRNAME
    if not root.is_dir():
        fail("CAPSULE_ARCHIVE_INVALID", "capsule root absent")
    return root


def verify_archive(archive_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="goal5793_x1_capsule_verify_") as temp:
        root = _safe_extract_capsule(archive_path.resolve(), Path(temp))
        return verify_capsule_root(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capsule-root", type=Path)
    group.add_argument("--archive", type=Path)
    args = parser.parse_args()
    try:
        result = (
            verify_capsule_root(args.capsule_root)
            if args.capsule_root is not None
            else verify_archive(args.archive)
        )
    except VerificationFailure as exc:
        print(json.dumps({"status": "FAIL", "fail_id": exc.fail_id, "detail": exc.detail}, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "status": "PASS",
                "audit_sha256": result["audit_sha256"],
                "source_rows": result["checks"]["source_rows_reconstructed"],
                "hostile_pass_count": result["checks"]["hostile_fail_id_pass_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
