#!/usr/bin/env python3
"""Build and operate the portable, non-formal Goal5809 two-app pilot.

This tool deliberately separates three identities:

* the immutable Goal5806 target and evidence archive;
* byte-identical execution products copied from that custody chain; and
* a new Goal5809 staging target whose only semantic changes are relocated
  paths and identities derived from the relocated candidate manifest.

The Goal5809 target is diagnostic staging authority only.  Neither building,
materialising, preflighting nor collecting this bundle creates a formal worker,
registered timing, performance claim, or successor to the frozen Goal5806
target.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import gzip
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import shlex
import sys
import tarfile
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from scripts.goal5809_execution_identity import (
    SCHEMA as EXECUTION_IDENTITY_SCHEMA,
    STATUS as EXECUTION_IDENTITY_STATUS,
    admit_execution_identity,
    controlled_python_command,
    verify_loaded_pyoptix,
    verify_loaded_rtdl,
)


SCHEMA = "rtdl.goal5809.portable_two_app_pilot_bundle.v3"
STAGING_SCHEMA = "rtdl.goal5809.portable_pilot_staging_authority.v2"
PREFLIGHT_SCHEMA = "rtdl.goal5809.portable_pilot_preflight.v2"
COLLECTION_SCHEMA = "rtdl.goal5809.portable_pilot_collection.v2"

GOAL5806_ARCHIVE_BYTES = 13_201_220
GOAL5806_ARCHIVE_SHA256 = (
    "a6df09e3a4f3fe098c5e5e3bfc2b93b0998bb4b6a055e19a2205f1640e8c8089"
)
GOAL5807_ARCHIVE_BYTES = 3_494_455
GOAL5807_ARCHIVE_SHA256 = (
    "dc95d0295b2d4f525255a1543a4adff2dcd2f18c7aa755284921f55e98ec36ee"
)
GOAL5807_PILOT_SOURCE_BYTES = 57_476
GOAL5807_PILOT_SOURCE_SHA256 = (
    "0b225d3625801b7c2a065a428e148523dbe261d89971b957180281411c061389"
)
GOAL5806_TARGET_BYTES = 2_534
GOAL5806_TARGET_FILE_SHA256 = (
    "61fadabb738d311e0bd73add3fa41a2d24215324cb779c0aef5a94435f380a13"
)
GOAL5806_TARGET_SEMANTIC_SHA256 = (
    "b76ce2d7bb7aade7ac238cf0909b000a3cfaa13db33a5377249cdf338bba7534"
)
GOAL5807_CONTRACT_SHA256 = (
    "6a3540fae2a0283af4bd91ac44190f6df1154775f518f1d088293972a63a7fe7"
)
GOAL5807_CONTRACT_BYTES = 12_311
GOAL5807_RESULT_SHA256 = (
    "25fc12dcc9a54d43f5e6cde7c337c6b2f95f7e4aa46a695c5e0ba5fbe683ffe2"
)
GOAL5807_RESULT_BYTES = 7_247
GOAL5807_REVIEW_SHA256 = (
    "1993a955a05670e5403e47f46849de1ca82fe61f1d9bc756c9c48edc160c2d4c"
)
GOAL5807_REVIEW_BYTES = 21_508
GOAL5807_CLOSURE_SHA256 = (
    "a8244ece6751bf240c6d6a60dc2261788e152f678e9a18a4a3168f4498be471f"
)
GOAL5807_CLOSURE_BYTES = 11_464
GOAL5806_RESULT_SHA256 = (
    "d8cf6ca27815ef0e64b002e8e77cbd4aa40b90e042ce616a586ff49e2bee610e"
)
GOAL5806_RESULT_BYTES = 6_244
GOAL5806_TECHNICAL_REPORT_SHA256 = (
    "1d4092f5593c3a4645ad780c4cd67c230e0214d762af77d31c99cfd27748edf7"
)
GOAL5806_TECHNICAL_REPORT_BYTES = 7_491
GOAL5806_CFR_SHA256 = (
    "f0ec211e538bd60083fba939efdd02dcfb61d941267854328223712359106781"
)
GOAL5806_CFR_BYTES = 9_092
GOAL5806_EVALUATION_SHA256 = (
    "522633258826cbd38e4982c1e3d4b3ad39e5a42c528ebe26bdb03bd2b34cd9a5"
)
GOAL5806_EVALUATION_BYTES = 15_752
GOAL5806_RECOUNT_SHA256 = (
    "1608cc4060addf4ad80c16a000f400650c748754f63fb4299b35de312d159434"
)
GOAL5806_RECOUNT_BYTES = 134_807
GOAL5807_RECONCILIATION_SCRIPT_SHA256 = (
    "1618210dac398a87b2cb91bae62317d879ccf7db84403393dda2d74618a7d844"
)
GOAL5807_RECONCILIATION_SCRIPT_BYTES = 24_994
GOAL5807_RECONCILIATION_TEST_SHA256 = (
    "d23ea9219e30eea859a86f2cf409688520e80d4abe25f1b8edab1a49afda119a"
)
GOAL5807_RECONCILIATION_TEST_BYTES = 3_907
GOAL5807_RECONCILIATION_JSON_SHA256 = (
    "048f851e7c805819b70c0974b26541d11238960cb0e3c2a2f8f6bae8cda2bfd5"
)
GOAL5807_RECONCILIATION_JSON_BYTES = 13_744
GOAL5807_RECONCILIATION_REPORT_SHA256 = (
    "0fead7e0089cb724413c0b39141231e9e9c2cbc9227e468a2e5d773910f87bbb"
)
GOAL5807_RECONCILIATION_REPORT_BYTES = 5_580
GOAL5807_RECONCILIATION_ABSORPTION_SHA256 = (
    "9b11e9b162938a5d4290d6636981eea943d73f1fc4bafe2582b5434b5c3bd962"
)
GOAL5807_RECONCILIATION_ABSORPTION_BYTES = 5_218
GOAL5809_CLAIM_AUTHORITY_ADDENDUM_SHA256 = (
    "45984f993ded05b1981d2464d1435d7c626356591f3a2f1ed7652f1e94aba08b"
)
GOAL5809_CLAIM_AUTHORITY_ADDENDUM_BYTES = 5_467
GOAL5809_CLAIM_AUTHORITY_ADDENDUM_SEMANTIC_SHA256 = (
    "c11850499b7ef9c298e058b36108d570253d44398156181162cc9a92a66c4f62"
)

GOAL5806_PRIMARY_SIX_RATIOS = {
    ("relation", "DEPLOYMENT_COLD"): 2.4241460007090776,
    ("relation", "PREPARE"): 2.2625982717999946,
    ("relation", "STEADY_E2E"): 0.9711067485442226,
    ("triangle", "DEPLOYMENT_COLD"): 1.950772952707983,
    ("triangle", "PREPARE"): 1.825013505517159,
    ("triangle", "STEADY_E2E"): 1.0293902805249933,
}

TARGET_FILE_NAMES = (
    "candidate_manifest",
    "matched_ptx",
    "native_library",
    "relation_compaction_cubin",
    "runtime_manifest",
    "target_observation",
    "trust_head",
    "trust_package",
    "trust_root",
)
EXTERNAL_CUSTODY_NAMES = (
    "matched_ptx",
    "relation_compaction_cubin",
    "runtime_manifest",
    "target_observation",
)

ARCHIVE_ROOT = "goal5806_triangle_product_projection_v1"
ARCHIVE_MEMBERS = {
    "candidate_manifest": f"{ARCHIVE_ROOT}/candidates_v2/candidate_manifest.json",
    "native_library": f"{ARCHIVE_ROOT}/native/librtdl_optix.so",
    "trust_root": f"{ARCHIVE_ROOT}/trust_v5/public-root.json",
    "trust_head": f"{ARCHIVE_ROOT}/trust_v5/head-seq4.json",
    "trust_package": f"{ARCHIVE_ROOT}/trust_v5/package-seq4.json",
    "proof": "source/experiments/goal5796_matched/semantic_spec.json",
}

PAYLOAD_PATHS = {
    "matched_ptx": "payload/products/matched_device.ptx",
    "native_library": "payload/products/native/librtdl_optix.so",
    "relation_compaction_cubin": "payload/products/relation_compaction.cubin",
    "runtime_manifest": "payload/products/runtime_manifest.json",
    "target_observation": "payload/products/target_observation.json",
    "trust_root": "payload/products/trust/public-root.json",
    "trust_head": "payload/products/trust/head.json",
    "trust_package": "payload/products/trust/package.json",
    "proof": "payload/products/proof/semantic_spec.json",
}

DETACHED_RECONCILIATION_PATHS = {
    "goal5806_archive": (
        "source/history/internal_docs/"
        "goal5806_triangle_product_projection_evidence_20260826.tar.gz"),
    "goal5807_archive": (
        "source/history/internal_docs/"
        "goal5807_provider_ready_formal_v2_20260827_0112.tar.gz"),
    "goal5807_pilot_source": (
        "source/scripts/goal5807_provider_ready_pilot.py"),
}

SOURCE_FILES = (
    "experiments/goal5796_matched/pyoptix_baseline.py",
    "experiments/goal5809_pyoptix_bulk_input.py",
    "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py",
    "experiments/goal5802_premeasurement/__init__.py",
    "experiments/goal5802_premeasurement/pyoptix_scalar_arm.py",
    "experiments/goal5802_premeasurement/rtdlexe_arm.py",
    "experiments/goal5802_premeasurement/workload.py",
    "experiments/goal5805_successor/__init__.py",
    "experiments/goal5805_successor/protocol.py",
    "scripts/goal5809_portable_two_app_pilot_bundle.py",
    "scripts/goal5809_execution_identity.py",
    "scripts/goal5809_pyoptix_two_app_pilot.py",
    "scripts/goal5809_reconcile_goal5806_goal5807_phases.py",
    "scripts/goal5809_runtime_session_two_app_pilot.py",
    "scripts/goal5809_two_app_pilot_controller.py",
    "tests/goal5809_goal5806_goal5807_phase_reconciliation_test.py",
)

CELL_SPECS = (
    ("relation", "rtdl-first"),
    ("relation", "pyoptix-first"),
    ("triangle", "rtdl-first"),
    ("triangle", "pyoptix-first"),
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _pretty(value: object) -> bytes:
    return (json.dumps(
        value, allow_nan=False, indent=2, sort_keys=True,
    ) + "\n").encode("utf-8")


def _sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json_bytes(payload: bytes, label: str) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {label}")
    return value


def _read_json(path: Path) -> dict[str, Any]:
    return _read_json_bytes(path.read_bytes(), str(path))


def _write_new(path: Path, payload: bytes, *, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
    if executable and os.name == "posix":
        path.chmod(0o755)


def _file_record(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": _sha(resolved),
    }


def _require_file(
    path: Path, *, expected_bytes: int, expected_sha256: str, label: str,
) -> bytes:
    resolved = path.resolve(strict=True)
    payload = resolved.read_bytes()
    observed = (len(payload), _sha_bytes(payload))
    expected = (expected_bytes, expected_sha256)
    if observed != expected:
        raise RuntimeError({
            "frozen_product_mismatch": label,
            "path": str(resolved),
            "expected": {"bytes": expected_bytes, "sha256": expected_sha256},
            "observed": {"bytes": observed[0], "sha256": observed[1]},
        })
    return payload


def _verify_frozen_target(payload: bytes) -> dict[str, Any]:
    if (len(payload), _sha_bytes(payload)) != (
            GOAL5806_TARGET_BYTES, GOAL5806_TARGET_FILE_SHA256):
        raise RuntimeError("frozen Goal5806 target file identity differs")
    value = _read_json_bytes(payload, "frozen Goal5806 target")
    unsigned = dict(value)
    seal = unsigned.pop("target_manifest_sha256", None)
    if seal != GOAL5806_TARGET_SEMANTIC_SHA256 or seal != _digest(unsigned):
        raise RuntimeError("frozen Goal5806 target semantic identity differs")
    if tuple(sorted(value.get("files", {}))) != tuple(sorted(TARGET_FILE_NAMES)):
        raise RuntimeError("frozen Goal5806 target product set differs")
    return value


def _archive_member_bytes(archive: tarfile.TarFile, name: str) -> bytes:
    member = archive.getmember(name)
    if not member.isfile():
        raise RuntimeError(f"regular archive member required: {name}")
    stream = archive.extractfile(member)
    if stream is None:
        raise RuntimeError(f"archive member is unreadable: {name}")
    return stream.read()


def _candidate_members(candidate: Mapping[str, Any]) -> dict[str, str]:
    rows = candidate.get("candidates")
    if not isinstance(rows, Mapping):
        raise RuntimeError("frozen candidate manifest lacks candidates")
    result: dict[str, str] = {}
    for task in ("relation", "triangle"):
        row = rows.get(task)
        if not isinstance(row, Mapping):
            raise RuntimeError(f"frozen candidate row differs: {task}")
        artifact_name = Path(str(row["artifact_path"])).name
        authority_name = Path(str(row["authority_path"])).name
        result[f"{task}_artifact"] = (
            f"{ARCHIVE_ROOT}/candidates_v2/artifacts/{artifact_name}")
        result[f"{task}_authority"] = (
            f"{ARCHIVE_ROOT}/candidates_v2/{authority_name}")
    return result


def _inspect_archive(
    archive_path: Path, target_path: Path,
) -> dict[str, Any]:
    archive_payload = _require_file(
        archive_path, expected_bytes=GOAL5806_ARCHIVE_BYTES,
        expected_sha256=GOAL5806_ARCHIVE_SHA256,
        label="goal5806_evidence_archive")
    del archive_payload
    target_payload = _require_file(
        target_path, expected_bytes=GOAL5806_TARGET_BYTES,
        expected_sha256=GOAL5806_TARGET_FILE_SHA256,
        label="goal5806_frozen_target")
    target = _verify_frozen_target(target_payload)
    records = target["files"]

    present: dict[str, dict[str, object]] = {}
    missing: list[str] = []
    with tarfile.open(archive_path, "r:gz") as archive:
        candidate_payload = _archive_member_bytes(
            archive, ARCHIVE_MEMBERS["candidate_manifest"])
        candidate_record = records["candidate_manifest"]
        if (len(candidate_payload), _sha_bytes(candidate_payload)) != (
                candidate_record["bytes"], candidate_record["sha256"]):
            raise RuntimeError("archived candidate manifest differs")
        candidate = _read_json_bytes(candidate_payload, "candidate manifest")
        if candidate.get("native_sha256") \
                != records["native_library"]["sha256"]:
            raise RuntimeError("archived candidate/native lineage differs")
        member_map = {
            **ARCHIVE_MEMBERS,
            **_candidate_members(candidate),
        }

        for name in ("candidate_manifest", "native_library", "trust_root",
                     "trust_head", "trust_package"):
            payload = _archive_member_bytes(archive, member_map[name])
            record = records[name]
            if (len(payload), _sha_bytes(payload)) != (
                    record["bytes"], record["sha256"]):
                raise RuntimeError(f"archived frozen product differs: {name}")
            present[name] = {
                "archive_member": member_map[name],
                "bytes": len(payload),
                "sha256": _sha_bytes(payload),
            }

        for task in ("relation", "triangle"):
            row = candidate["candidates"][task]
            for kind in ("artifact", "authority"):
                member_name = member_map[f"{task}_{kind}"]
                payload = _archive_member_bytes(archive, member_name)
                expected = row[f"{kind}_sha256"]
                if _sha_bytes(payload) != expected:
                    raise RuntimeError(
                        f"archived {task} {kind} identity differs")
                present[f"{task}_{kind}"] = {
                    "archive_member": member_name,
                    "bytes": len(payload),
                    "sha256": expected,
                }

        proof_payload = _archive_member_bytes(archive, member_map["proof"])
        if _sha_bytes(proof_payload) != candidate.get("proof_sha256"):
            raise RuntimeError("archived candidate/proof lineage differs")
        present["callback_proof"] = {
            "archive_member": member_map["proof"],
            "bytes": len(proof_payload),
            "sha256": _sha_bytes(proof_payload),
        }

        # Do not infer absence from member names.  Check every regular member
        # with a matching byte count for the four old-POD products.
        unresolved = set(EXTERNAL_CUSTODY_NAMES)
        by_size: dict[int, list[str]] = {}
        for name in unresolved:
            by_size.setdefault(int(records[name]["bytes"]), []).append(name)
        for member in archive.getmembers():
            candidate_names = by_size.get(member.size, ())
            if not member.isfile() or not candidate_names:
                continue
            payload = _archive_member_bytes(archive, member.name)
            observed = _sha_bytes(payload)
            for name in candidate_names:
                if observed == records[name]["sha256"]:
                    present[name] = {
                        "archive_member": member.name,
                        "bytes": len(payload),
                        "sha256": observed,
                    }
                    unresolved.discard(name)
        missing.extend(sorted(unresolved))

    return {
        "schema": "rtdl.goal5809.goal5806_archive_sufficiency.v1",
        "status": (
            "SUFFICIENT" if not missing
            else "INSUFFICIENT__EXACT_EXTERNAL_CUSTODY_BYTES_REQUIRED"),
        "goal5806_archive": {
            "path": str(archive_path.resolve(strict=True)),
            "bytes": GOAL5806_ARCHIVE_BYTES,
            "sha256": GOAL5806_ARCHIVE_SHA256,
        },
        "goal5806_target": {
            "path": str(target_path.resolve(strict=True)),
            "bytes": GOAL5806_TARGET_BYTES,
            "file_sha256": GOAL5806_TARGET_FILE_SHA256,
            "semantic_sha256": GOAL5806_TARGET_SEMANTIC_SHA256,
        },
        "present_and_rehashed": present,
        "missing_exact_products": missing,
        "missing_exact_product_requirements": {
            name: dict(records[name]) for name in missing
        },
        "portable_two_arm_bundle_buildable_from_archive_alone": not missing,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "claim_authorized": False,
    }


def _copy_source_closure(repository_root: Path, destination: Path) -> None:
    source_files = list(SOURCE_FILES)
    rtdsl_root = repository_root / "src" / "rtdsl"
    source_files.extend(
        path.relative_to(repository_root).as_posix()
        for path in rtdsl_root.rglob("*.py")
        if "__pycache__" not in path.parts
    )
    for relative in sorted(set(source_files), key=lambda row: row.encode()):
        source = (repository_root / relative).resolve(strict=True)
        target = destination / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def _copy_verified_local(
    source: Path, destination: Path, record: Mapping[str, Any], label: str,
) -> None:
    payload = _require_file(
        source, expected_bytes=int(record["bytes"]),
        expected_sha256=str(record["sha256"]), label=label)
    _write_new(destination, payload)


def _require_goal5807_closure(
    payload: bytes, *, review_payload: bytes, goal5806_result_payload: bytes,
) -> dict[str, Any]:
    closure = _read_json_bytes(payload, "Goal5807 external-review closure")
    review = closure.get("external_review")
    absorption = closure.get("goal5807_absorption")
    primary = closure.get("goal5806_primary_performance_authority")
    crosswalk = closure.get("phase_crosswalk")
    diagnostic = closure.get("goal5809_authority")
    if closure.get("schema") != (
            "rtdl.goal5807.external_review_absorption_and_"
            "goal5809_claim_authority_closure.v1") \
            or closure.get("status") != (
                "COMPLETE__GOAL5807_THRESHOLD_CLAIMS_WITHDRAWN__"
                "GOAL5806_PRIMARY_AUTHORITY_RESTORED") \
            or closure.get(
                "controlling_for_goal5807_and_goal5809_claim_authority") \
            is not True \
            or not isinstance(review, Mapping) \
            or review.get("sha256") != GOAL5807_REVIEW_SHA256 \
            or review.get("bytes") != GOAL5807_REVIEW_BYTES \
            or _sha_bytes(review_payload) != GOAL5807_REVIEW_SHA256 \
            or not isinstance(absorption, Mapping) \
            or absorption.get("thresholded_claim_count_authorized") != 0 \
            or absorption.get("requested_claim_ceiling_authorized") \
            is not False \
            or absorption.get("former_pass_literals_are_inoperative_for_claims") \
            is not True \
            or len(absorption.get("withdrawn_thresholded_pass_rulings", ())) \
            != 4 \
            or not isinstance(primary, Mapping) \
            or primary.get("authority_role") \
            != "PRIMARY_PREREGISTERED_PERFORMANCE_AUTHORITY" \
            or primary.get("result_sha256") != GOAL5806_RESULT_SHA256 \
            or _sha_bytes(goal5806_result_payload) != GOAL5806_RESULT_SHA256 \
            or not isinstance(crosswalk, Mapping) \
            or crosswalk.get(
                "goal5809_split_phases_may_retroactively_fix_goal5806_or_goal5807") \
            is not False \
            or not isinstance(diagnostic, Mapping) \
            or diagnostic.get("role") != "NONFORMAL_DIAGNOSTIC_ONLY" \
            or diagnostic.get("formal_worker_count") != 0 \
            or diagnostic.get("registered_performance_timing_count") != 0 \
            or diagnostic.get("paper_evidence_authorized") is not False \
            or diagnostic.get("descriptive_ratio_computation_authorized") \
            is not True \
            or diagnostic.get(
                "inferential_or_threshold_ratio_claim_authorized") \
            is not False \
            or diagnostic.get("direct_arm_count") != 0 \
            or diagnostic.get("host_language_control_present") is not False \
            or diagnostic.get("design_attribution_authorized") is not False:
        raise RuntimeError("Goal5807 review absorption/claim closure differs")
    observed_six = {
        (str(row.get("task")), str(row.get("regime"))): row.get("ratio")
        for row in primary.get("primary_six_rows", ())
        if isinstance(row, Mapping)
    }
    if observed_six != GOAL5806_PRIMARY_SIX_RATIOS:
        raise RuntimeError("Goal5806 primary six-ratio authority differs")
    return closure


def _require_goal5807_reconciliation(payload: bytes) -> dict[str, Any]:
    value = _read_json_bytes(payload, "Goal5807 absolute phase reconciliation")
    goal5806 = value.get("goal5806")
    goal5807 = value.get("goal5807")
    method = value.get("method")
    limits = value.get("limits")
    reconciliation = value.get("reconciliation")
    if value.get("schema") \
            != "rtdl.goal5807.postreview_absolute_phase_reconciliation.v1" \
            or value.get("status") \
            != "COMPLETE__DESCRIPTIVE_RAW_ARCHIVE_RECONSTRUCTION_ONLY" \
            or not isinstance(goal5806, Mapping) \
            or goal5806.get("raw_worker_count") != 128 \
            or not isinstance(goal5807, Mapping) \
            or goal5807.get("raw_worker_count") != 128 \
            or not isinstance(method, Mapping) \
            or method.get("published_result_read") is not False \
            or method.get("primary_evaluator_output_read") is not False \
            or method.get("threshold_evaluation_performed") is not False \
            or not isinstance(limits, Mapping) \
            or limits.get("new_performance_sample_count") != 0 \
            or limits.get("new_scientific_verdict_emitted") is not False \
            or not isinstance(reconciliation, Mapping) \
            or reconciliation.get("same_named_prepare_boundary") is not False:
        raise RuntimeError("Goal5807 absolute phase reconciliation differs")
    required_goal5806_phases = {
        "DEPLOYMENT_COLD", "FIRST_EXACT_EXECUTE", "LOAD", "PREPARE",
        "STEADY_E2E",
    }
    goal5806_rows = goal5806.get("absolute_arm_medians", ())
    if not isinstance(goal5806_rows, list) or len(goal5806_rows) != 4:
        raise RuntimeError("Goal5806 absolute task/arm row count differs")
    for row in goal5806_rows:
        if not isinstance(row, Mapping) or set(
                row.get("absolute_median_ns", {})) != required_goal5806_phases:
            raise RuntimeError("Goal5806 absolute phase set differs")
    required_goal5807_phases = {
        "adapter_construct", "app_prepare", "first_exact_execute",
        "input_admission", "install_load", "provider_bind",
        "runtime_preload",
    }
    goal5807_rows = goal5807.get("absolute_arm_medians", ())
    if not isinstance(goal5807_rows, list) or len(goal5807_rows) != 4:
        raise RuntimeError("Goal5807 absolute task/arm row count differs")
    for row in goal5807_rows:
        if not isinstance(row, Mapping) or set(
                row.get("absolute_phase_median_ns", {})) \
                != required_goal5807_phases:
            raise RuntimeError("Goal5807 absolute phase set differs")
    return value


def _require_goal5807_reconciliation_absorption(
    payload: bytes, *, reconciliation_payload: bytes,
) -> dict[str, Any]:
    value = _read_json_bytes(
        payload, "Goal5807 phase-reconciliation absorption")
    predecessor = value.get("controlling_with_predecessor_closure")
    raw = value.get("raw_archive_reconciliation")
    disposition = value.get("external_review_finding_disposition")
    entry = value.get("goal5809_entry")
    formal = value.get("formal_successor_gate")
    if value.get("schema") != (
            "rtdl.goal5807.postreview_absolute_phase_reconciliation_"
            "absorption_and_goal5809_entry.v1") \
            or value.get("status") != (
                "COMPLETE__ABSOLUTE_PHASE_AND_PREPARE_RECONCILIATION_"
                "ABSORBED__DIRECT_CONTROL_REMAINS_REQUIRED_FOR_FORMAL_"
                "SUCCESSOR") \
            or not isinstance(predecessor, Mapping) \
            or predecessor.get("bytes") != GOAL5807_CLOSURE_BYTES \
            or predecessor.get("sha256") != GOAL5807_CLOSURE_SHA256 \
            or not isinstance(raw, Mapping) \
            or raw.get("result", {}).get("bytes") \
            != GOAL5807_RECONCILIATION_JSON_BYTES \
            or raw.get("result", {}).get("sha256") \
            != GOAL5807_RECONCILIATION_JSON_SHA256 \
            or _sha_bytes(reconciliation_payload) \
            != GOAL5807_RECONCILIATION_JSON_SHA256 \
            or not isinstance(disposition, Mapping) \
            or disposition.get("p1_absolute_times", {}).get("status") \
            != "CLOSED_BY_RAW_ARCHIVE_RECONSTRUCTION" \
            or disposition.get("p1_prepare_reconciliation", {}).get("status") \
            != "CLOSED_BY_RAW_ARCHIVE_RECONSTRUCTION" \
            or disposition.get("p1_direct_arm", {}).get("status") \
            != "OPEN_FOR_ANY_FORMAL_DESIGN_ATTRIBUTION_OR_PAPER_SUCCESSOR" \
            or not isinstance(entry, Mapping) \
            or entry.get("paper_evidence_authorized") is not False \
            or entry.get("old_bundle_authorized_for_execution_or_delivery") \
            is not False \
            or not isinstance(formal, Mapping) \
            or formal.get("must_restore_direct_as_first_class_arm") is not True \
            or formal.get("may_claim_protocol_safety_overhead_from_goal5809_two_arm_pilot") \
            is not False:
        raise RuntimeError("Goal5807 phase-reconciliation absorption differs")
    return value


def _require_goal5809_claim_authority_addendum(
    payload: bytes, *, closure_payload: bytes,
    reconciliation_absorption_payload: bytes,
    goal5806_archive_payload_sha256: str,
    goal5807_archive_payload: bytes,
    goal5807_pilot_source_payload: bytes,
) -> dict[str, Any]:
    value = _read_json_bytes(payload, "Goal5809 claim-authority addendum")
    unsigned = dict(value)
    seal = unsigned.pop("claim_authority_addendum_sha256", None)
    predecessors = value.get("predecessors")
    capsule = value.get("detached_reconciliation_capsule")
    correction = value.get("goal5806_primary_performance_authority_correction")
    process_cold = value.get("goal5806_full_process_cold_disposition")
    goal5807 = value.get("goal5807")
    goal5809 = value.get("goal5809")
    if value.get("schema") != (
            "rtdl.goal5809.detached_reconciliation_and_goal5806_"
            "claim_ceiling_addendum.v1") \
            or value.get("status") != (
                "COMPLETE__DETACHED_RECONCILIATION_ROOTS_REQUIRED__"
                "GOAL5806_STEADY_CEILING_NARROWED__"
                "FULL_PROCESS_PASS_WITHDRAWN") \
            or value.get(
                "controlling_for_goal5806_goal5807_goal5809_claim_authority") \
            is not True \
            or seal != GOAL5809_CLAIM_AUTHORITY_ADDENDUM_SEMANTIC_SHA256 \
            or seal != _digest(unsigned) \
            or not isinstance(predecessors, Mapping) \
            or predecessors.get("goal5807_claim_authority_closure", {}).get(
                "sha256") != GOAL5807_CLOSURE_SHA256 \
            or _sha_bytes(closure_payload) != GOAL5807_CLOSURE_SHA256 \
            or predecessors.get("goal5807_reconciliation_absorption", {}).get(
                "sha256") != GOAL5807_RECONCILIATION_ABSORPTION_SHA256 \
            or _sha_bytes(reconciliation_absorption_payload) \
            != GOAL5807_RECONCILIATION_ABSORPTION_SHA256 \
            or not isinstance(capsule, Mapping) \
            or capsule.get("required") is not True \
            or capsule.get(
                "bundled_test_must_pass_from_fresh_extraction_without_repository") \
            is not True \
            or capsule.get("expected_test_count") != 4 \
            or not isinstance(correction, Mapping) \
            or correction.get(
                "no_measurable_steady_state_cost_claim_authorized") \
            is not False \
            or not isinstance(process_cold, Mapping) \
            or process_cold.get("thresholded_claim_count_authorized") != 0 \
            or process_cold.get(
                "historical_pass_literals_are_inoperative_for_claims") \
            is not True \
            or process_cold.get(
                "fresh_process_faster_than_pyoptix_paper_claim_authorized") \
            is not False \
            or not isinstance(goal5807, Mapping) \
            or goal5807.get("thresholded_claim_count_authorized") != 0 \
            or not isinstance(goal5809, Mapping) \
            or goal5809.get("paper_evidence_authorized") is not False \
            or goal5809.get("inferential_or_threshold_ratio_claim_authorized") \
            is not False:
        raise RuntimeError("Goal5809 claim-authority addendum differs")

    roots = {
        str(row.get("role")): row
        for row in capsule.get("roots", ())
        if isinstance(row, Mapping)
    }
    expected_roots = {
        "GOAL5806_RAW_EVIDENCE_ARCHIVE": (
            DETACHED_RECONCILIATION_PATHS["goal5806_archive"],
            GOAL5806_ARCHIVE_BYTES, GOAL5806_ARCHIVE_SHA256,
            goal5806_archive_payload_sha256),
        "GOAL5807_RAW_EVIDENCE_ARCHIVE": (
            DETACHED_RECONCILIATION_PATHS["goal5807_archive"],
            GOAL5807_ARCHIVE_BYTES, GOAL5807_ARCHIVE_SHA256,
            _sha_bytes(goal5807_archive_payload)),
        "GOAL5807_PILOT_SOURCE": (
            DETACHED_RECONCILIATION_PATHS["goal5807_pilot_source"],
            GOAL5807_PILOT_SOURCE_BYTES, GOAL5807_PILOT_SOURCE_SHA256,
            _sha_bytes(goal5807_pilot_source_payload)),
    }
    if set(roots) != set(expected_roots):
        raise RuntimeError("Goal5809 detached reconciliation root set differs")
    for role, (path, size, expected_sha, observed_sha) in expected_roots.items():
        row = roots[role]
        if row.get("bundle_path") != path \
                or row.get("bytes") != size \
                or row.get("sha256") != expected_sha \
                or observed_sha != expected_sha:
            raise RuntimeError(
                f"Goal5809 detached reconciliation root differs: {role}")

    steady = {
        str(row.get("task")): row
        for row in correction.get("steady_e2e", ())
        if isinstance(row, Mapping)
    }
    if set(steady) != {"relation", "triangle"} \
            or steady["relation"].get("ratio_rtdl_over_pyoptix") \
            != GOAL5806_PRIMARY_SIX_RATIOS[("relation", "STEADY_E2E")] \
            or steady["triangle"].get("ratio_rtdl_over_pyoptix") \
            != GOAL5806_PRIMARY_SIX_RATIOS[("triangle", "STEADY_E2E")] \
            or steady["triangle"].get("ci95_low") \
            != 1.0200291004609718 \
            or steady["triangle"].get("ci95_high") \
            != 1.0364109906769723 \
            or steady["triangle"].get("ci_entirely_above_one") is not True:
        raise RuntimeError("Goal5806 corrected steady claim ceiling differs")
    historical_rows = process_cold.get("historical_rows")
    if not isinstance(historical_rows, list) or len(historical_rows) != 2 \
            or any(not isinstance(row, Mapping) for row in historical_rows) \
            or any(row.get("controlling_verdict") != (
                "WITHDRAWN__DESCRIPTIVE_ONLY__NO_THRESHOLD_OR_PAPER_CLAIM")
                   for row in historical_rows):
        raise RuntimeError("Goal5806 full-process PASS disposition differs")
    return value


def _write_detached_reconciliation_roots(
    root: Path, *, goal5806_archive: Path,
    goal5807_archive_payload: bytes,
    goal5807_pilot_source_payload: bytes,
) -> tuple[str, ...]:
    destinations = {
        "goal5806_archive": goal5806_archive.read_bytes(),
        "goal5807_archive": goal5807_archive_payload,
        "goal5807_pilot_source": goal5807_pilot_source_payload,
    }
    expected = {
        "goal5806_archive": (
            GOAL5806_ARCHIVE_BYTES, GOAL5806_ARCHIVE_SHA256),
        "goal5807_archive": (
            GOAL5807_ARCHIVE_BYTES, GOAL5807_ARCHIVE_SHA256),
        "goal5807_pilot_source": (
            GOAL5807_PILOT_SOURCE_BYTES, GOAL5807_PILOT_SOURCE_SHA256),
    }
    for role, payload_bytes in destinations.items():
        expected_bytes, expected_sha = expected[role]
        if len(payload_bytes) != expected_bytes \
                or _sha_bytes(payload_bytes) != expected_sha:
            raise RuntimeError(
                f"Goal5809 detached reconciliation payload differs: {role}")
        _write_new(root / DETACHED_RECONCILIATION_PATHS[role], payload_bytes)
    return tuple(DETACHED_RECONCILIATION_PATHS[role]
                 for role in sorted(DETACHED_RECONCILIATION_PATHS))


def _write_claim_authority_bundle_files(
    root: Path, *, payloads: Mapping[str, bytes],
) -> tuple[str, ...]:
    destinations = {
        "goal5807_contract": "frozen/goal5807_contract.json",
        "goal5807_result": "frozen/goal5807_result.json",
        "goal5807_review": (
            "frozen/review_goal5807_provider_ready_formal_result.md"),
        "goal5807_closure": (
            "frozen/goal5807_external_review_absorption_and_"
            "goal5809_claim_authority_closure.json"),
        "goal5806_result": (
            "frozen/goal5806_primary_performance_result.json"),
        "goal5806_technical_report": (
            "frozen/goal5806_primary_performance_technical_report.md"),
        "goal5806_cfr": (
            "frozen/goal5806_primary_performance_call_for_review.md"),
        "goal5806_evaluation": (
            "frozen/goal5806_primary_formal_evaluation.json"),
        "goal5806_recount": (
            "frozen/goal5806_primary_independent_recount.json"),
        "goal5807_reconciliation_json": (
            "frozen/goal5807_postreview_absolute_phase_reconciliation.json"),
        "goal5807_reconciliation_report": (
            "frozen/goal5807_postreview_absolute_phase_reconciliation.md"),
        "goal5807_reconciliation_absorption": (
            "frozen/goal5807_postreview_absolute_phase_reconciliation_"
            "absorption_and_goal5809_entry.json"),
        "goal5809_claim_authority_addendum": (
            "frozen/goal5809_detached_reconciliation_and_goal5806_"
            "claim_ceiling_addendum.json"),
    }
    if set(payloads) != set(destinations):
        raise RuntimeError("Goal5809 claim-authority payload set differs")
    for role, relative in destinations.items():
        _write_new(root / relative, payloads[role])
    return tuple(destinations[role] for role in sorted(destinations))


def _claim_authority_manifest() -> dict[str, Any]:
    return {
        "primary_preregistered_performance_goal": "GOAL5806",
        "primary_preregistered_performance_rows": 6,
        "goal5806_steady_interpretation": (
            "BOTH_TASKS_WITHIN_PREREGISTERED_FIVE_PERCENT_BOUND__"
            "TRIANGLE_RATIO_1_POINT_02939_WITH_CI_ENTIRELY_ABOVE_ONE"),
        "goal5806_no_measurable_steady_cost_claim_authorized": False,
        "goal5806_full_process_cold_thresholded_claim_count_authorized": 0,
        "goal5806_full_process_cold_historical_pass_literals_inoperative": True,
        "goal5807_role": "DIAGNOSTIC_LIFECYCLE_DECOMPOSITION_ONLY",
        "goal5807_thresholded_claim_count_authorized": 0,
        "goal5807_review_p1_absolute_times": (
            "CLOSED_BY_RAW_ARCHIVE_RECONSTRUCTION"),
        "goal5807_review_p1_prepare_reconciliation": (
            "CLOSED_BY_RAW_ARCHIVE_RECONSTRUCTION"),
        "goal5807_review_p1_direct_arm": (
            "OPEN_FOR_ANY_FORMAL_DESIGN_ATTRIBUTION_OR_PAPER_SUCCESSOR"),
        "goal5809_role": "NONFORMAL_DIAGNOSTIC_ONLY",
        "phase_crosswalk_path": (
            "frozen/goal5807_external_review_absorption_and_"
            "goal5809_claim_authority_closure.json"),
        "absolute_phase_reconciliation_path": (
            "frozen/goal5807_postreview_absolute_phase_reconciliation.json"),
        "reconciliation_absorption_path": (
            "frozen/goal5807_postreview_absolute_phase_reconciliation_"
            "absorption_and_goal5809_entry.json"),
        "controlling_claim_authority_addendum_path": (
            "frozen/goal5809_detached_reconciliation_and_goal5806_"
            "claim_ceiling_addendum.json"),
        "detached_reconciliation_test_count_required": 4,
        "detached_reconciliation_roots_embedded": True,
        "goal5809_split_phase_crosswalk_is_prospective": True,
        "goal5809_may_retroactively_fix_predecessor_result": False,
        "old_bundle_sha256": (
            "eacf84246393d3baa48f05e8187b0ac577a8e8a187071cd67c2343018575079c"),
        "old_bundle_authorized_for_execution_or_delivery": False,
    }


def _build_bundle(args: argparse.Namespace) -> dict[str, Any]:
    repository_root = args.repository_root.resolve(strict=True)
    archive_path = args.goal5806_archive.resolve(strict=True)
    target_path = args.goal5806_target.resolve(strict=True)
    sufficiency = _inspect_archive(archive_path, target_path)
    target_payload = target_path.read_bytes()
    target = _verify_frozen_target(target_payload)
    records = target["files"]

    external_paths = {
        "matched_ptx": args.matched_ptx,
        "relation_compaction_cubin": args.relation_compaction_cubin,
        "runtime_manifest": args.runtime_manifest,
        "target_observation": args.target_observation,
    }
    missing_arguments = sorted(
        name for name, path in external_paths.items() if path is None)
    if missing_arguments:
        raise RuntimeError({
            "portable_bundle_missing_exact_custody_inputs": missing_arguments,
            "archive_sufficiency": sufficiency,
        })

    contract_payload = _require_file(
        args.goal5807_contract,
        expected_bytes=GOAL5807_CONTRACT_BYTES,
        expected_sha256=GOAL5807_CONTRACT_SHA256,
        label="goal5807_frozen_contract")
    contract = _read_json_bytes(contract_payload, "Goal5807 contract")
    if contract.get("claim_boundary", {}).get("target_manifest_sha256") \
            != GOAL5806_TARGET_FILE_SHA256:
        raise RuntimeError("Goal5807 contract does not bind Goal5806 target")
    result_payload = _require_file(
        args.goal5807_result,
        expected_bytes=GOAL5807_RESULT_BYTES,
        expected_sha256=GOAL5807_RESULT_SHA256,
        label="goal5807_frozen_result")
    review_payload = _require_file(
        args.goal5807_review,
        expected_bytes=GOAL5807_REVIEW_BYTES,
        expected_sha256=GOAL5807_REVIEW_SHA256,
        label="goal5807_external_review")
    goal5806_result_payload = _require_file(
        args.goal5806_result,
        expected_bytes=GOAL5806_RESULT_BYTES,
        expected_sha256=GOAL5806_RESULT_SHA256,
        label="goal5806_primary_result")
    closure_payload = _require_file(
        args.goal5807_closure,
        expected_bytes=GOAL5807_CLOSURE_BYTES,
        expected_sha256=GOAL5807_CLOSURE_SHA256,
        label="goal5807_review_absorption_closure")
    _require_goal5807_closure(
        closure_payload,
        review_payload=review_payload,
        goal5806_result_payload=goal5806_result_payload)
    goal5806_technical_payload = _require_file(
        args.goal5806_technical_report,
        expected_bytes=GOAL5806_TECHNICAL_REPORT_BYTES,
        expected_sha256=GOAL5806_TECHNICAL_REPORT_SHA256,
        label="goal5806_primary_technical_report")
    goal5806_cfr_payload = _require_file(
        args.goal5806_cfr,
        expected_bytes=GOAL5806_CFR_BYTES,
        expected_sha256=GOAL5806_CFR_SHA256,
        label="goal5806_primary_call_for_review")
    goal5806_evaluation_payload = _require_file(
        args.goal5806_evaluation,
        expected_bytes=GOAL5806_EVALUATION_BYTES,
        expected_sha256=GOAL5806_EVALUATION_SHA256,
        label="goal5806_primary_formal_evaluation")
    goal5806_recount_payload = _require_file(
        args.goal5806_recount,
        expected_bytes=GOAL5806_RECOUNT_BYTES,
        expected_sha256=GOAL5806_RECOUNT_SHA256,
        label="goal5806_primary_independent_recount")
    reconciliation_script_payload = _require_file(
        repository_root /
        "scripts/goal5809_reconcile_goal5806_goal5807_phases.py",
        expected_bytes=GOAL5807_RECONCILIATION_SCRIPT_BYTES,
        expected_sha256=GOAL5807_RECONCILIATION_SCRIPT_SHA256,
        label="goal5807_absolute_phase_reconciliation_script")
    reconciliation_test_payload = _require_file(
        repository_root /
        "tests/goal5809_goal5806_goal5807_phase_reconciliation_test.py",
        expected_bytes=GOAL5807_RECONCILIATION_TEST_BYTES,
        expected_sha256=GOAL5807_RECONCILIATION_TEST_SHA256,
        label="goal5807_absolute_phase_reconciliation_test")
    reconciliation_json_payload = _require_file(
        args.goal5807_reconciliation_json,
        expected_bytes=GOAL5807_RECONCILIATION_JSON_BYTES,
        expected_sha256=GOAL5807_RECONCILIATION_JSON_SHA256,
        label="goal5807_absolute_phase_reconciliation_json")
    _require_goal5807_reconciliation(reconciliation_json_payload)
    reconciliation_report_payload = _require_file(
        args.goal5807_reconciliation_report,
        expected_bytes=GOAL5807_RECONCILIATION_REPORT_BYTES,
        expected_sha256=GOAL5807_RECONCILIATION_REPORT_SHA256,
        label="goal5807_absolute_phase_reconciliation_report")
    reconciliation_absorption_payload = _require_file(
        args.goal5807_reconciliation_absorption,
        expected_bytes=GOAL5807_RECONCILIATION_ABSORPTION_BYTES,
        expected_sha256=GOAL5807_RECONCILIATION_ABSORPTION_SHA256,
        label="goal5807_absolute_phase_reconciliation_absorption")
    _require_goal5807_reconciliation_absorption(
        reconciliation_absorption_payload,
        reconciliation_payload=reconciliation_json_payload)
    goal5807_archive_payload = _require_file(
        args.goal5807_archive,
        expected_bytes=GOAL5807_ARCHIVE_BYTES,
        expected_sha256=GOAL5807_ARCHIVE_SHA256,
        label="goal5807_raw_evidence_archive")
    goal5807_pilot_source_payload = _require_file(
        args.goal5807_pilot_source,
        expected_bytes=GOAL5807_PILOT_SOURCE_BYTES,
        expected_sha256=GOAL5807_PILOT_SOURCE_SHA256,
        label="goal5807_pilot_source")
    claim_addendum_payload = _require_file(
        args.goal5809_claim_authority_addendum,
        expected_bytes=GOAL5809_CLAIM_AUTHORITY_ADDENDUM_BYTES,
        expected_sha256=GOAL5809_CLAIM_AUTHORITY_ADDENDUM_SHA256,
        label="goal5809_claim_authority_addendum")
    _require_goal5809_claim_authority_addendum(
        claim_addendum_payload,
        closure_payload=closure_payload,
        reconciliation_absorption_payload=reconciliation_absorption_payload,
        goal5806_archive_payload_sha256=_sha(archive_path),
        goal5807_archive_payload=goal5807_archive_payload,
        goal5807_pilot_source_payload=goal5807_pilot_source_payload)

    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("portable bundle output already exists")
    with tempfile.TemporaryDirectory(prefix="goal5809_bundle_") as temporary:
        root = Path(temporary) / "bundle"
        root.mkdir()
        _copy_source_closure(repository_root, root)
        if (root / "source/scripts/goal5809_reconcile_goal5806_goal5807_"
                "phases.py").read_bytes() != reconciliation_script_payload \
                or (root / "source/tests/goal5809_goal5806_goal5807_phase_"
                    "reconciliation_test.py").read_bytes() \
                != reconciliation_test_payload:
            raise RuntimeError("Goal5807 reconciliation source copy differs")
        _write_new(root / "frozen/goal5806_target_manifest.json", target_payload)
        _write_claim_authority_bundle_files(root, payloads={
            "goal5807_contract": contract_payload,
            "goal5807_result": result_payload,
            "goal5807_review": review_payload,
            "goal5807_closure": closure_payload,
            "goal5806_result": goal5806_result_payload,
            "goal5806_technical_report": goal5806_technical_payload,
            "goal5806_cfr": goal5806_cfr_payload,
            "goal5806_evaluation": goal5806_evaluation_payload,
            "goal5806_recount": goal5806_recount_payload,
            "goal5807_reconciliation_json": reconciliation_json_payload,
            "goal5807_reconciliation_report": reconciliation_report_payload,
            "goal5807_reconciliation_absorption": (
                reconciliation_absorption_payload),
            "goal5809_claim_authority_addendum": claim_addendum_payload,
        })
        _write_detached_reconciliation_roots(
            root,
            goal5806_archive=archive_path,
            goal5807_archive_payload=goal5807_archive_payload,
            goal5807_pilot_source_payload=goal5807_pilot_source_payload)

        with tarfile.open(archive_path, "r:gz") as archive:
            candidate_payload = _archive_member_bytes(
                archive, ARCHIVE_MEMBERS["candidate_manifest"])
            candidate = _read_json_bytes(candidate_payload, "candidate")
            _write_new(
                root / "frozen/goal5806_candidate_manifest.json",
                candidate_payload)
            member_map = {
                **ARCHIVE_MEMBERS,
                **_candidate_members(candidate),
            }
            for name in ("native_library", "trust_root", "trust_head",
                         "trust_package", "proof"):
                _write_new(
                    root / PAYLOAD_PATHS[name],
                    _archive_member_bytes(archive, member_map[name]))
            for task in ("relation", "triangle"):
                row = candidate["candidates"][task]
                artifact_name = Path(str(row["artifact_path"])).name
                authority_name = f"{task}.authority.json"
                _write_new(
                    root / "payload/products/candidates/artifacts" /
                    artifact_name,
                    _archive_member_bytes(
                        archive, member_map[f"{task}_artifact"]))
                _write_new(
                    root / "payload/products/candidates" / authority_name,
                    _archive_member_bytes(
                        archive, member_map[f"{task}_authority"]))

        for name, source in external_paths.items():
            assert source is not None
            _copy_verified_local(
                source, root / PAYLOAD_PATHS[name], records[name], name)

        readme = """# Goal5809 portable two-app pilot

This is a diagnostic-only bundle. It creates zero formal workers and zero
registered performance timings. Its relocated target is not the frozen
Goal5806 target and does not replace Goal5806 or Goal5807 evidence. Goal5806's
operative performance authority is limited to the six preregistered post-import
rows. Their steady ratios are 0.9711 and 1.0294, both within the preregistered
5% bound; Triangle's CI is entirely above 1, so this bundle does not authorize
"no measurable steady cost." The two historical Goal5806 full-process-cold
PASS literals are descriptive-only and inoperative for threshold or paper
claims. Goal5807 is retained only as lifecycle decomposition after external
review withdrew its four thresholded PASS rulings and requested claim ceiling.
The controlling review, closure and append-only correction are embedded under
`frozen/`.

Goal5809's split phases are prospective diagnosis. They cannot retroactively
repair or redefine either predecessor. There is no Direct arm, host-language
control, or authorized design attribution in this pilot.

Materialisation creates a path-local Goal5809 successor execution identity.
The frozen Goal5802 runtime manifest is only a dependency-byte source; the new
identity also freezes the current workers, controller, runtime implementation,
matched arms, and any optional bulk helper. Preflight and every target child
receive the exact successor-manifest file SHA-256.

The two immutable raw archives and Goal5807 pilot source needed to reconstruct
the postreview reconciliation are embedded under `source/`. A detached reviewer
can run:

```sh
PYTHONPATH="$PWD/source/src:$PWD/source" python3 -m unittest \
  source.tests.goal5809_goal5806_goal5807_phase_reconciliation_test
```

On the RTX A4500 POD:

```sh
tar -xzf <bundle>.tar.gz -C <new-empty-directory>
cd <new-empty-directory>
export PYTHONPATH="$PWD/source/src:$PWD/source"
python3 source/scripts/goal5809_portable_two_app_pilot_bundle.py materialize --bundle-root . --staging-root staging
# The generated runner invokes strict preflight with the admitted retained
# interpreter and the frozen isolated-startup command before either child.
bash staging/run_pilot_matrix.sh "$PWD/outputs"
python3 source/scripts/goal5809_portable_two_app_pilot_bundle.py collect --outputs-root outputs --output-archive goal5809_pilot_outputs.tar.gz
```
"""
        _write_new(root / "RUNBOOK.md", readme.encode("utf-8"))

        manifest_rows = []
        for path in sorted(
                (row for row in root.rglob("*") if row.is_file()),
                key=lambda row: row.relative_to(root).as_posix().encode()):
            relative = path.relative_to(root).as_posix()
            manifest_rows.append({
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": _sha(path),
            })
        body: dict[str, Any] = {
            "schema": SCHEMA,
            "status": "COMPLETE__DIAGNOSTIC_PORTABLE_TWO_APP_PILOT_PAYLOAD",
            "direct_arm_count": 0,
            "host_language_control_present": False,
            "design_attribution_authorized": False,
            "frozen_lineage": {
                "goal5806_archive_sha256": GOAL5806_ARCHIVE_SHA256,
                "goal5807_archive_sha256": GOAL5807_ARCHIVE_SHA256,
                "goal5807_pilot_source_sha256": (
                    GOAL5807_PILOT_SOURCE_SHA256),
                "goal5806_target_file_sha256": GOAL5806_TARGET_FILE_SHA256,
                "goal5806_target_semantic_sha256": (
                    GOAL5806_TARGET_SEMANTIC_SHA256),
                "goal5807_contract_sha256": GOAL5807_CONTRACT_SHA256,
                "goal5807_result_sha256": GOAL5807_RESULT_SHA256,
                "goal5807_external_review_sha256": GOAL5807_REVIEW_SHA256,
                "goal5807_review_absorption_closure_sha256": (
                    GOAL5807_CLOSURE_SHA256),
                "goal5806_primary_performance_result_sha256": (
                    GOAL5806_RESULT_SHA256),
                "goal5806_primary_formal_evaluation_sha256": (
                    GOAL5806_EVALUATION_SHA256),
                "goal5806_primary_independent_recount_sha256": (
                    GOAL5806_RECOUNT_SHA256),
                "goal5807_absolute_phase_reconciliation_script_sha256": (
                    GOAL5807_RECONCILIATION_SCRIPT_SHA256),
                "goal5807_absolute_phase_reconciliation_test_sha256": (
                    GOAL5807_RECONCILIATION_TEST_SHA256),
                "goal5807_absolute_phase_reconciliation_json_sha256": (
                    GOAL5807_RECONCILIATION_JSON_SHA256),
                "goal5807_absolute_phase_reconciliation_report_sha256": (
                    GOAL5807_RECONCILIATION_REPORT_SHA256),
                "goal5807_absolute_phase_reconciliation_absorption_sha256": (
                    GOAL5807_RECONCILIATION_ABSORPTION_SHA256),
                "goal5809_claim_authority_addendum_sha256": (
                    GOAL5809_CLAIM_AUTHORITY_ADDENDUM_SHA256),
            },
            "scope": {
                "nonformal_pilot_only": True,
                "diagnostic_only": True,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "claim_authorized": False,
                "may_replace_goal5806_or_goal5807": False,
                "goal5806_is_primary_preregistered_performance_authority": True,
                "goal5807_is_diagnostic_decomposition_only": True,
                "goal5809_split_phases_are_prospective_diagnosis_only": True,
                "goal5809_may_retroactively_fix_predecessor_result": False,
                "descriptive_ratio_computation_authorized": True,
                "inferential_or_threshold_ratio_claim_authorized": False,
                "direct_arm_count": 0,
                "host_language_control_present": False,
                "design_attribution_authorized": False,
            },
            "claim_authority": _claim_authority_manifest(),
            "cell_matrix": [
                {"first_app": task, "arm_order": order}
                for task, order in CELL_SPECS
            ],
            "files": manifest_rows,
        }
        manifest = {**body, "bundle_manifest_sha256": _digest(body)}
        _write_new(root / "BUNDLE_MANIFEST.json", _pretty(manifest))
        _write_tar_gz(root, output)

    return {
        "status": "COMPLETE__DIAGNOSTIC_PORTABLE_TWO_APP_PILOT_BUNDLE_BUILT",
        "output": str(output),
        "output_bytes": output.stat().st_size,
        "output_sha256": _sha(output),
        "goal5806_archive_sufficient_alone": sufficiency[
            "portable_two_arm_bundle_buildable_from_archive_alone"],
        "external_exact_custody_products_used": sorted(external_paths),
        "detached_reconciliation_roots_embedded": 3,
        "detached_reconciliation_test_count_required": 4,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "claim_authorized": False,
        "direct_arm_count": 0,
        "host_language_control_present": False,
        "design_attribution_authorized": False,
    }


def _write_tar_gz(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
                paths = [root] + sorted(
                    root.rglob("*"),
                    key=lambda row: row.relative_to(root).as_posix().encode())
                for path in paths:
                    relative = "." if path == root \
                        else path.relative_to(root).as_posix()
                    info = tarfile.TarInfo(relative)
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    if path.is_dir():
                        info.type = tarfile.DIRTYPE
                        info.mode = 0o755
                        tar.addfile(info)
                    elif path.is_file():
                        info.size = path.stat().st_size
                        info.mode = 0o755 if path.suffix == ".sh" else 0o644
                        with path.open("rb") as handle:
                            tar.addfile(info, handle)
                    else:
                        raise RuntimeError(f"unsupported bundle member: {path}")


def _verify_bundle(bundle_root: Path) -> dict[str, Any]:
    root = bundle_root.resolve(strict=True)
    manifest_path = root / "BUNDLE_MANIFEST.json"
    manifest = _read_json(manifest_path)
    unsigned = dict(manifest)
    seal = unsigned.pop("bundle_manifest_sha256", None)
    if manifest.get("schema") != SCHEMA or seal != _digest(unsigned):
        raise RuntimeError("portable bundle manifest seal differs")
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows \
            or any(not isinstance(row, Mapping) \
                   or set(row) != {"path", "bytes", "sha256"}
                   for row in rows):
        raise RuntimeError("portable bundle manifest file rows differ")
    listed = [str(row["path"]) for row in rows]
    if listed != sorted(listed, key=lambda item: item.encode()) \
            or len(listed) != len(set(listed)) \
            or "BUNDLE_MANIFEST.json" in listed:
        raise RuntimeError("portable bundle manifest path set differs")
    expected_files = {"BUNDLE_MANIFEST.json", *listed}
    expected_directories: set[str] = set()
    for listed_path in listed:
        pure = PurePosixPath(listed_path)
        for parent in pure.parents:
            if parent != PurePosixPath("."):
                expected_directories.add(parent.as_posix())

    for row in rows:
        pure = PurePosixPath(str(row["path"]))
        relative = Path(*pure.parts)
        if pure.is_absolute() or not pure.parts \
                or any(part in {"", ".", ".."} for part in pure.parts) \
                or pure.as_posix() != str(row["path"]):
            raise RuntimeError("unsafe portable bundle manifest path")
        path = (root / relative).resolve(strict=True)
        if root not in path.parents:
            raise RuntimeError("portable bundle member escaped root")
        if type(row["bytes"]) is not int or row["bytes"] < 0 \
                or not isinstance(row["sha256"], str) \
                or _file_record(path)["bytes"] != row["bytes"] \
                or _sha(path) != row["sha256"]:
            raise RuntimeError(f"portable bundle member differs: {relative}")
    observed_files: set[str] = set()
    observed_directories: set[str] = set()
    for member in root.rglob("*"):
        if member.is_symlink():
            raise RuntimeError(
                f"portable bundle has symbolic member: {member}")
        relative = member.relative_to(root).as_posix()
        if member.is_file():
            observed_files.add(relative)
        elif member.is_dir():
            observed_directories.add(relative)
        else:
            raise RuntimeError(
                f"portable bundle has special member: {member}")
    if observed_files != expected_files \
            or observed_directories != expected_directories:
        raise RuntimeError({
            "portable_bundle_unmanifested_or_missing_members": {
                "extra_files": sorted(observed_files - expected_files),
                "missing_files": sorted(expected_files - observed_files),
                "extra_directories": sorted(
                    observed_directories - expected_directories),
                "missing_directories": sorted(
                    expected_directories - observed_directories),
            },
        })
    return manifest


def _candidate_nonpath_projection(value: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(value))
    result["native_path"] = "<PATH>"
    result["proof_path"] = "<PATH>"
    for row in result["candidates"].values():
        row["artifact_path"] = "<PATH>"
        row["authority_path"] = "<PATH>"
    return result


def _execution_file_row(path: Path, provenance: str) -> dict[str, object]:
    record = _file_record(path)
    return {
        "path": record["path"],
        "bytes": record["bytes"],
        "sha256": record["sha256"],
        "provenance": provenance,
    }


def _validate_predecessor_runtime_manifest(
    path: Path, *, expected_file_sha256: str,
    staged_target: Mapping[str, Any],
) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    if _sha(resolved) != expected_file_sha256:
        raise RuntimeError("Goal5802 predecessor runtime manifest bytes differ")
    value = _read_json(resolved)
    unsigned = dict(value)
    seal = unsigned.pop("manifest_sha256", None)
    if value.get("schema") != "rtdl.goal5802.target_runtime_manifest.v2" \
            or value.get("status") \
            != "PREPARED_UNTIMED__FORMAL_EXECUTION_LOCKED" \
            or value.get("registered_performance_timing_count") != 0 \
            or value.get("formal_worker_zero") is not False \
            or seal != _digest(unsigned):
        raise RuntimeError("Goal5802 predecessor runtime manifest differs")
    files = value.get("files")
    pyoptix = value.get("pyoptix")
    if not isinstance(files, Mapping) \
            or not all(role in files for role in (
                "pyoptix_initializer", "pyoptix_extension")) \
            or not isinstance(pyoptix, Mapping) \
            or not all(key in pyoptix for key in (
                "distribution_version", "optix_api_version")):
        raise RuntimeError("Goal5802 predecessor PyOptiX identity is absent")

    # The predecessor manifest and Goal5806 target are not independent bags of
    # files.  Require one coherent retained tuple so a correct PTX from one run
    # cannot be combined with candidates/native/trust from another.
    target_role_map = {
        "matched_ptx": "matched_ptx",
        "compaction_cubin": "relation_compaction_cubin",
        "target_observation_receipt": "target_observation",
    }
    for runtime_role, target_role in target_role_map.items():
        runtime_row = files.get(runtime_role)
        target_row = staged_target["files"][target_role]
        if not isinstance(runtime_row, Mapping) \
                or runtime_row.get("bytes") != target_row["bytes"] \
                or runtime_row.get("sha256") != target_row["sha256"]:
            raise RuntimeError({
                "Goal5809_mixed_target_lineage": runtime_role,
                "runtime_manifest": (
                    dict(runtime_row) if isinstance(runtime_row, Mapping)
                    else runtime_row),
                "goal5806_target": dict(target_row),
            })
    return value


def _validate_goal5806_successor_tuple(
    *, bundle_root: Path, staged_target: Mapping[str, Any],
    staged_candidate: Mapping[str, Any],
) -> dict[str, object]:
    """Cross-link Goal5806 successor candidates/native/proof/trust locally."""

    if staged_candidate.get("native_sha256") \
            != staged_target["files"]["native_library"]["sha256"]:
        raise RuntimeError("Goal5809 candidate/native lineage differs")
    proof_path = bundle_root / PAYLOAD_PATHS["proof"]
    if _sha(proof_path.resolve(strict=True)) \
            != staged_candidate.get("proof_sha256"):
        raise RuntimeError("Goal5809 candidate/proof lineage differs")

    head_path = Path(str(staged_target["files"]["trust_head"]["path"]))
    package_path = Path(str(staged_target["files"]["trust_package"]["path"]))
    root_path = Path(str(staged_target["files"]["trust_root"]["path"]))
    head = _read_json(head_path)
    package = _read_json(package_path)
    trust_root = _read_json(root_path)
    if head.get("current_package_sha256") \
            != staged_target["files"]["trust_package"]["sha256"] \
            or head.get("current_sequence") != package.get("sequence") \
            or not isinstance(head.get("key_id"), str) \
            or head.get("key_id") != package.get("key_id") \
            or head.get("key_id") != trust_root.get("key_id"):
        raise RuntimeError("Goal5809 Goal5806 trust head/package/root differ")
    authorities = package.get("authorities")
    if not isinstance(authorities, list):
        raise RuntimeError("Goal5809 Goal5806 trust authorities are absent")
    for task in ("relation", "triangle"):
        candidate = staged_candidate["candidates"][task]
        matches = [
            row for row in authorities
            if isinstance(row, Mapping)
            and row.get("deployment_id") == candidate["deployment_id"]
        ]
        expected = {
            "artifact_sha256": candidate["artifact_sha256"],
            "authority_sha256": candidate["authority_sha256"],
            "deployment_id": candidate["deployment_id"],
            "executable_identity_sha256": candidate[
                "executable_identity_sha256"],
            "native_library_sha256": staged_candidate["native_sha256"],
        }
        if len(matches) != 1 \
                or any(matches[0].get(key) != value
                       for key, value in expected.items()):
            raise RuntimeError(
                f"Goal5809 Goal5806 trust/candidate lineage differs: {task}")
    return {
        "candidate_native_cross_link": True,
        "candidate_proof_cross_link": True,
        "trust_head_package_root_cross_link": True,
        "candidate_authority_count_bound": 2,
    }


def _resolve_live_pyoptix(
    predecessor: Mapping[str, Any],
) -> dict[str, Any]:
    """Resolve relocated PyOptiX files in this untimed materializer process."""

    optix = importlib.import_module("optix")
    extension = importlib.import_module("optix._optix")
    initializer_path = Path(str(optix.__file__)).resolve(strict=True)
    extension_path = Path(str(extension.__file__)).resolve(strict=True)
    files = predecessor["files"]
    for role, path in (
            ("pyoptix_initializer", initializer_path),
            ("pyoptix_extension", extension_path)):
        expected = files[role]
        if path.stat().st_size != expected["bytes"] \
                or _sha(path) != expected["sha256"]:
            raise RuntimeError(f"relocated Goal5809 {role} bytes differ")
    distribution_version = importlib.metadata.version("pyoptix")
    api_version = ".".join(str(int(item)) for item in optix.version())
    expected_pyoptix = predecessor["pyoptix"]
    if distribution_version != expected_pyoptix["distribution_version"] \
            or api_version != expected_pyoptix["optix_api_version"]:
        raise RuntimeError("relocated Goal5809 PyOptiX version differs")
    return {
        "initializer_path": initializer_path,
        "extension_path": extension_path,
        "distribution_version": distribution_version,
        "api_version": api_version,
    }


def _build_successor_execution_identity(
    *, bundle_root: Path, staging_root: Path,
    staged_target_path: Path, staged_target: Mapping[str, Any],
    staged_candidate_path: Path, staged_candidate: Mapping[str, Any],
) -> tuple[dict[str, Any], bytes]:
    """Bind all current Goal5809 code and retained frozen dependencies."""

    root = bundle_root.resolve(strict=True)
    runtime_path = Path(str(staged_target["files"]["runtime_manifest"]["path"]))
    predecessor = _validate_predecessor_runtime_manifest(
        runtime_path,
        expected_file_sha256=str(
            staged_target["files"]["runtime_manifest"]["sha256"]),
        staged_target=staged_target)
    _validate_goal5806_successor_tuple(
        bundle_root=root,
        staged_target=staged_target,
        staged_candidate=staged_candidate)
    live_pyoptix = _resolve_live_pyoptix(predecessor)

    paths: dict[str, tuple[Path, str]] = {
        "rtdl_init": (
            root / "source/src/rtdsl/__init__.py", "GOAL5809_CURRENT_SOURCE"),
        "rtdlexe_module": (
            root / "source/src/rtdsl/v4_rtdlexe.py",
            "GOAL5809_CURRENT_SOURCE"),
        "goal5809_rtdl_worker": (
            root / "source/scripts/goal5809_runtime_session_two_app_pilot.py",
            "GOAL5809_CURRENT_SOURCE"),
        "goal5809_pyoptix_worker": (
            root / "source/scripts/goal5809_pyoptix_two_app_pilot.py",
            "GOAL5809_CURRENT_SOURCE"),
        "goal5809_two_app_controller": (
            root / "source/scripts/goal5809_two_app_pilot_controller.py",
            "GOAL5809_CURRENT_SOURCE"),
        "goal5809_execution_identity_helper": (
            root / "source/scripts/goal5809_execution_identity.py",
            "GOAL5809_CURRENT_SOURCE"),
        "goal5809_portable_bundle_tool": (
            root / "source/scripts/goal5809_portable_two_app_pilot_bundle.py",
            "GOAL5809_CURRENT_SOURCE"),
        "goal5809_pyoptix_bulk_input_source": (
            root / "source/experiments/goal5809_pyoptix_bulk_input.py",
            "GOAL5809_CURRENT_SOURCE"),
        "goal5800_pyoptix_idiomatic_arm_source": (
            root / "source/experiments/goal5800_pyoptix_owl/"
            "pyoptix_idiomatic_arm.py",
            "ACTIVELY_EXECUTED_RETAINED_SOURCE"),
        "goal5805_protocol_source": (
            root / "source/experiments/goal5805_successor/protocol.py",
            "ACTIVELY_EXECUTED_RETAINED_SOURCE"),
        "physical_execution_provenance_module": (
            root / "source/src/rtdsl/physical_execution_provenance.py",
            "GOAL5809_CURRENT_SOURCE"),
        "rtdlexe_arm_source": (
            root / "source/experiments/goal5802_premeasurement/rtdlexe_arm.py",
            "RETAINED_MATCHED_ARM_SOURCE"),
        "pyoptix_scalar_arm_source": (
            root / "source/experiments/goal5802_premeasurement/pyoptix_scalar_arm.py",
            "RETAINED_MATCHED_ARM_SOURCE"),
        "pyoptix_baseline_source": (
            root / "source/experiments/goal5796_matched/pyoptix_baseline.py",
            "RETAINED_MATCHED_BASELINE_SOURCE"),
        "workload_source": (
            root / "source/experiments/goal5802_premeasurement/workload.py",
            "RETAINED_MATCHED_WORKLOAD_SOURCE"),
        "matched_ptx": (
            Path(str(staged_target["files"]["matched_ptx"]["path"])),
            "FROZEN_GOAL5806_PRODUCT"),
        "relation_compaction_cubin": (
            Path(str(staged_target["files"]["relation_compaction_cubin"]["path"])),
            "FROZEN_GOAL5806_PRODUCT"),
        "native_library": (
            Path(str(staged_target["files"]["native_library"]["path"])),
            "FROZEN_GOAL5806_PRODUCT"),
        "callback_proof": (
            root / PAYLOAD_PATHS["proof"], "FROZEN_GOAL5806_PRODUCT"),
        "runtime_manifest_dependency_source": (
            runtime_path, "FROZEN_GOAL5802_DEPENDENCY_SOURCE_ONLY"),
        "trust_root": (
            Path(str(staged_target["files"]["trust_root"]["path"])),
            "FROZEN_GOAL5806_PRODUCT"),
        "trust_head": (
            Path(str(staged_target["files"]["trust_head"]["path"])),
            "FROZEN_GOAL5806_PRODUCT"),
        "trust_package": (
            Path(str(staged_target["files"]["trust_package"]["path"])),
            "FROZEN_GOAL5806_PRODUCT"),
        "staged_target_manifest": (
            staged_target_path, "GOAL5809_RELOCATED_STAGING_AUTHORITY"),
        "staged_candidate_manifest": (
            staged_candidate_path, "GOAL5809_PATH_ONLY_RELOCATED_CANDIDATE"),
        "pyoptix_initializer": (
            live_pyoptix["initializer_path"],
            "FROZEN_GOAL5802_BYTES_RELOCATED_BY_LIVE_IMPORT"),
        "pyoptix_extension": (
            live_pyoptix["extension_path"],
            "FROZEN_GOAL5802_BYTES_RELOCATED_BY_LIVE_IMPORT"),
    }
    for task in ("relation", "triangle"):
        row = staged_candidate["candidates"][task]
        paths[f"{task}_artifact"] = (
            Path(str(row["artifact_path"])), "FROZEN_GOAL5806_PRODUCT")
        paths[f"{task}_authority"] = (
            Path(str(row["authority_path"])), "FROZEN_GOAL5806_PRODUCT")

    # A dedicated bulk helper is optional.  If one exists at bundle-build
    # time, silently omitting it from the execution identity is forbidden.
    fixed = {path.resolve(strict=True) for path, _ in paths.values()}
    bulk_candidates = list((root / "source/src/rtdsl").rglob("*bulk*.py"))
    bulk_candidates.extend((root / "source/scripts").glob("goal5809*bulk*.py"))
    for index, path in enumerate(sorted(
            (row for row in bulk_candidates if row.resolve(strict=True) not in fixed),
            key=lambda row: row.relative_to(root).as_posix().encode())):
        role = f"bulk_helper_{index:02d}"
        paths[role] = (path, "GOAL5809_CURRENT_SOURCE")

    files = {
        role: _execution_file_row(path, provenance)
        for role, (path, provenance) in sorted(paths.items())
    }
    predecessor_row = staged_target["files"]["runtime_manifest"]
    body: dict[str, Any] = {
        "schema": EXECUTION_IDENTITY_SCHEMA,
        "status": EXECUTION_IDENTITY_STATUS,
        "scope": {
            "claim_authorized": False,
            "formal_worker_count": 0,
            "nonformal_pilot_only": True,
            "registered_performance_timing_count": 0,
        },
        "predecessor_runtime_manifest": {
            "path": str(runtime_path.resolve(strict=True)),
            "bytes": predecessor_row["bytes"],
            "file_sha256": predecessor_row["sha256"],
            "semantic_sha256": predecessor["manifest_sha256"],
            "dependency_source_only": True,
            "is_goal5809_execution_identity": False,
            "absolute_predecessor_paths_authoritative": False,
        },
        "pyoptix": {
            "distribution_name": "pyoptix",
            "distribution_version": live_pyoptix["distribution_version"],
            "api_version": live_pyoptix["api_version"],
            "initializer_module": "optix",
            "extension_module": "optix._optix",
            "initializer_role": "pyoptix_initializer",
            "extension_role": "pyoptix_extension",
        },
        "required_file_roles": sorted(files),
        "files": files,
    }
    value = {**body, "execution_identity_sha256": _digest(body)}
    return value, _pretty(value)


def _materialize(args: argparse.Namespace) -> dict[str, Any]:
    root = args.bundle_root.resolve(strict=True)
    bundle_manifest = _verify_bundle(root)
    staging = args.staging_root.resolve()
    if staging.exists():
        raise RuntimeError("Goal5809 staging root already exists")
    staging.mkdir(parents=True)

    frozen_target_path = root / "frozen/goal5806_target_manifest.json"
    frozen_candidate_path = root / "frozen/goal5806_candidate_manifest.json"
    frozen_target_payload = frozen_target_path.read_bytes()
    frozen_target = _verify_frozen_target(frozen_target_payload)
    frozen_candidate = _read_json(frozen_candidate_path)

    candidate = copy.deepcopy(frozen_candidate)
    candidate["native_path"] = str(
        (root / PAYLOAD_PATHS["native_library"]).resolve(strict=True))
    candidate["proof_path"] = str(
        (root / PAYLOAD_PATHS["proof"]).resolve(strict=True))
    for task in ("relation", "triangle"):
        row = candidate["candidates"][task]
        artifact_name = Path(str(row["artifact_path"])).name
        row["artifact_path"] = str((
            root / "payload/products/candidates/artifacts" / artifact_name
        ).resolve(strict=True))
        row["authority_path"] = str((
            root / "payload/products/candidates" / f"{task}.authority.json"
        ).resolve(strict=True))
    if _candidate_nonpath_projection(candidate) \
            != _candidate_nonpath_projection(frozen_candidate):
        raise RuntimeError("candidate staging changed non-path semantics")
    candidate_payload = _pretty(candidate)
    candidate_path = staging / "candidate_manifest.json"
    _write_new(candidate_path, candidate_payload)

    target = copy.deepcopy(frozen_target)
    target["files"]["candidate_manifest"] = {
        "path": str(candidate_path.resolve(strict=True)),
        "bytes": len(candidate_payload),
        "sha256": _sha_bytes(candidate_payload),
    }
    for name in TARGET_FILE_NAMES:
        if name == "candidate_manifest":
            continue
        payload_name = name if name in PAYLOAD_PATHS else None
        if payload_name is None:
            raise RuntimeError(f"no portable product path for {name}")
        target["files"][name]["path"] = str((
            root / PAYLOAD_PATHS[payload_name]).resolve(strict=True))
    target.pop("target_manifest_sha256", None)
    target["target_manifest_sha256"] = _digest(target)
    target_payload = _pretty(target)
    target_path = staging / "target_manifest.json"
    _write_new(target_path, target_payload)

    # Every non-candidate product retains exact frozen bytes and hash.  The
    # candidate descriptor changes only because its path-only manifest changes.
    unchanged_product_identities = {}
    for name in TARGET_FILE_NAMES:
        if name == "candidate_manifest":
            continue
        frozen_row = frozen_target["files"][name]
        staged_row = target["files"][name]
        unchanged_product_identities[name] = (
            frozen_row["bytes"] == staged_row["bytes"]
            and frozen_row["sha256"] == staged_row["sha256"])
    if not all(unchanged_product_identities.values()):
        raise RuntimeError("staging changed a frozen product identity")

    execution_identity, execution_identity_payload = \
        _build_successor_execution_identity(
            bundle_root=root,
            staging_root=staging,
            staged_target_path=target_path,
            staged_target=target,
            staged_candidate_path=candidate_path,
            staged_candidate=candidate,
        )
    execution_identity_path = staging / "execution_identity_manifest.json"
    _write_new(execution_identity_path, execution_identity_payload)
    execution_identity_file_sha256 = _sha_bytes(execution_identity_payload)
    # Re-read and rehash the exact staged bytes before they become the
    # controller/child preaction boundary.
    admitted_execution_identity = admit_execution_identity(
        execution_identity_path,
        expected_file_sha256=execution_identity_file_sha256)

    authority_body: dict[str, Any] = {
        "schema": STAGING_SCHEMA,
        "status": (
            "COMPLETE__DIAGNOSTIC_PILOT_STAGING_AUTHORITY__"
            "NOT_FROZEN_TARGET"),
        "scope": {
            "diagnostic_pilot_only": True,
            "nonformal_diagnostic": True,
            "formal_evidence": False,
            "paper_evidence": False,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "paper_or_performance_claim_authorized": False,
            "may_replace_goal5806_or_goal5807": False,
            "staged_target_is_frozen_goal5806_target": False,
            "successor_execution_identity_is_path_local": True,
            "successor_execution_identity_is_frozen_goal5802_manifest": False,
            "direct_arm_count": 0,
            "host_language_control_present": False,
            "design_attribution_authorized": False,
        },
        "lineage": {
            "bundle_manifest_sha256": bundle_manifest[
                "bundle_manifest_sha256"],
            "frozen_goal5806_target_file_sha256": (
                GOAL5806_TARGET_FILE_SHA256),
            "frozen_goal5806_target_semantic_sha256": (
                GOAL5806_TARGET_SEMANTIC_SHA256),
            "goal5807_contract_sha256": GOAL5807_CONTRACT_SHA256,
            "goal5807_result_sha256": GOAL5807_RESULT_SHA256,
            "goal5807_external_review_sha256": GOAL5807_REVIEW_SHA256,
            "goal5807_review_absorption_closure_sha256": (
                GOAL5807_CLOSURE_SHA256),
            "goal5806_primary_performance_result_sha256": (
                GOAL5806_RESULT_SHA256),
            "goal5807_absolute_phase_reconciliation_sha256": (
                GOAL5807_RECONCILIATION_JSON_SHA256),
            "goal5807_reconciliation_absorption_sha256": (
                GOAL5807_RECONCILIATION_ABSORPTION_SHA256),
            "goal5809_claim_authority_addendum_sha256": (
                GOAL5809_CLAIM_AUTHORITY_ADDENDUM_SHA256),
        },
        "staged_target": {
            "path": str(target_path.resolve(strict=True)),
            "bytes": len(target_payload),
            "file_sha256": _sha_bytes(target_payload),
            "semantic_sha256": target["target_manifest_sha256"],
        },
        "staged_candidate": {
            "path": str(candidate_path.resolve(strict=True)),
            "bytes": len(candidate_payload),
            "file_sha256": _sha_bytes(candidate_payload),
            "nonpath_projection_unchanged": True,
        },
        "successor_execution_identity": {
            "path": str(execution_identity_path.resolve(strict=True)),
            "bytes": len(execution_identity_payload),
            "file_sha256": execution_identity_file_sha256,
            "semantic_sha256": admitted_execution_identity[
                "execution_identity_sha256"],
            "all_bound_files_rehashed_before_authority_seal": True,
            "goal5802_runtime_manifest_is_dependency_source_only": True,
            "path_relocation_requires_new_successor_identity": True,
        },
        "rewrite_audit": {
            "candidate_manifest_only_path_fields_changed": True,
            "target_manifest_only_paths_candidate_derived_identity_and_seal_changed": True,
            "unchanged_frozen_product_identities": unchanged_product_identities,
        },
        "cell_matrix": [
            {"first_app": task, "arm_order": order}
            for task, order in CELL_SPECS
        ],
    }
    authority = {
        **authority_body,
        "staging_authority_sha256": _digest(authority_body),
    }
    authority_path = staging / "staging_authority.json"
    _write_new(authority_path, _pretty(authority))
    _write_new(
        staging / "run_pilot_matrix.sh",
        _run_script(root, staging, authority).encode("utf-8"),
        executable=True)
    return authority


def _runtime_launch_projection(
    authority: Mapping[str, Any],
) -> dict[str, Any]:
    """Reconstruct the exact controlled Python launch from frozen bytes."""

    target_row = authority["staged_target"]
    target = _read_json(Path(str(target_row["path"])))
    runtime_row = target["files"]["runtime_manifest"]
    runtime = _validate_predecessor_runtime_manifest(
        Path(str(runtime_row["path"])),
        expected_file_sha256=str(runtime_row["sha256"]),
        staged_target=target)
    projection = runtime.get("build_provenance", {}).get(
        "combined_runtime_path_projection")
    if not isinstance(projection, Mapping):
        raise RuntimeError("Goal5809 runtime launch projection is absent")
    combined_root = Path(str(projection["root_path"])).resolve(strict=True)
    interpreter = (
        combined_root / str(projection["clean_python_relative"])
    ).resolve(strict=True)
    site = (
        combined_root / str(projection["site_packages_relative"])
    ).resolve(strict=True)
    clean = runtime.get("files", {}).get("clean_python")
    if not isinstance(clean, Mapping) \
            or interpreter.stat().st_size != clean.get("bytes") \
            or _sha(interpreter) != clean.get("sha256"):
        raise RuntimeError("Goal5809 controlled interpreter bytes differ")
    identity_row = authority["successor_execution_identity"]
    admitted = admit_execution_identity(
        Path(str(identity_row["path"])),
        expected_file_sha256=str(identity_row["file_sha256"]))
    identity_files = admitted["manifest"]["files"]
    worker = Path(str(identity_files["goal5809_rtdl_worker"]["path"])).resolve(
        strict=True)
    source = worker.parent.parent.resolve(strict=True)
    source_package = (source / "src").resolve(strict=True)
    target_observation = runtime.get("target_observation")
    loader = (target_observation.get("loader_environment")
              if isinstance(target_observation, Mapping) else None)
    if not isinstance(loader, Mapping) \
            or set(loader) != {"LD_LIBRARY_PATH", "LD_PRELOAD"} \
            or loader.get("LD_PRELOAD") is not None:
        raise RuntimeError("Goal5809 controlled loader environment differs")
    return {
        "admitted_interpreter_path": str(interpreter),
        "source_package_import_root": str(source_package),
        "source_import_root": str(source),
        "site_packages_import_root": str(site),
        "loader_environment": dict(loader),
    }


def _run_script(
    bundle_root: Path, staging_root: Path, authority: Mapping[str, Any],
) -> str:
    target = authority["staged_target"]
    identity = authority["successor_execution_identity"]
    launch = _runtime_launch_projection(authority)
    preflight_command = controlled_python_command(
        launch,
        script=(bundle_root / "source/scripts/"
                "goal5809_portable_two_app_pilot_bundle.py"))
    controller_command = controlled_python_command(
        launch,
        script=(bundle_root / "source/scripts/"
                "goal5809_two_app_pilot_controller.py"))
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"BUNDLE_ROOT={json.dumps(str(bundle_root.resolve(strict=True)))}",
        f"STAGING_ROOT={json.dumps(str(staging_root.resolve(strict=True)))}",
        'OUTPUT_ROOT="${1:?usage: run_pilot_matrix.sh OUTPUT_ROOT}"',
        'if [[ -e "$OUTPUT_ROOT" ]]; then echo "output root exists" >&2; exit 2; fi',
        'mkdir -p "$OUTPUT_ROOT"',
        "unset PYTHONPATH PYTHONHOME LD_PRELOAD",
        'export PYTHONDONTWRITEBYTECODE=1',
        'export PYTHONNOUSERSITE=1',
        'unset PYTHONHASHSEED',
        ("unset LD_LIBRARY_PATH" if launch["loader_environment"][
            "LD_LIBRARY_PATH"] is None else
         "export LD_LIBRARY_PATH=" + shlex.quote(str(
             launch["loader_environment"]["LD_LIBRARY_PATH"]))),
        shlex.join(preflight_command) + " preflight \\",
        "  --bundle-root \"$BUNDLE_ROOT\" \\",
        "  --staging-root \"$STAGING_ROOT\" \\",
        "  --output \"$OUTPUT_ROOT/preflight_receipt.json\" \\",
        "  >\"$OUTPUT_ROOT/preflight.stdout.json\" \\",
        "  2>\"$OUTPUT_ROOT/preflight.stderr.bin\"",
        'mkdir -p "$OUTPUT_ROOT/staging_custody"',
        'cp -- "$BUNDLE_ROOT/BUNDLE_MANIFEST.json" '
        '"$OUTPUT_ROOT/staging_custody/BUNDLE_MANIFEST.json"',
        'cp -- "$STAGING_ROOT/staging_authority.json" '
        '"$OUTPUT_ROOT/staging_custody/staging_authority.json"',
        'cp -- "$STAGING_ROOT/execution_identity_manifest.json" '
        '"$OUTPUT_ROOT/staging_custody/execution_identity_manifest.json"',
        'cp -- "$STAGING_ROOT/target_manifest.json" '
        '"$OUTPUT_ROOT/staging_custody/target_manifest.json"',
        'cp -- "$STAGING_ROOT/candidate_manifest.json" '
        '"$OUTPUT_ROOT/staging_custody/candidate_manifest.json"',
    ]
    for first_app, arm_order in CELL_SPECS:
        cell = f"{first_app}-first__{arm_order}"
        lines.extend([
            shlex.join(controller_command) + " \\",
            "  --target-manifest \"$STAGING_ROOT/target_manifest.json\" \\",
            f"  --expected-target-manifest-sha256 {target['file_sha256']} \\",
            "  --execution-identity-manifest \"$STAGING_ROOT/"
            "execution_identity_manifest.json\" \\",
            "  --expected-execution-identity-manifest-sha256 "
            f"{identity['file_sha256']} \\",
            f"  --first-app {first_app} --arm-order {arm_order} \\",
            f"  --output-dir \"$OUTPUT_ROOT/{cell}\" \\",
            f"  >\"$OUTPUT_ROOT/{cell}.stdout.json\" \\",
            f"  2>\"$OUTPUT_ROOT/{cell}.stderr.bin\"",
        ])
    lines.append(
        'echo "Goal5809 four-cell non-formal pilot complete: $OUTPUT_ROOT"')
    return "\n".join(lines) + "\n"


def _validate_staging(staging: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    authority = _read_json(staging / "staging_authority.json")
    unsigned = dict(authority)
    seal = unsigned.pop("staging_authority_sha256", None)
    if authority.get("schema") != STAGING_SCHEMA or seal != _digest(unsigned):
        raise RuntimeError("Goal5809 staging authority seal differs")
    target_path = Path(authority["staged_target"]["path"])
    target_payload = target_path.resolve(strict=True).read_bytes()
    if _sha_bytes(target_payload) != authority["staged_target"]["file_sha256"]:
        raise RuntimeError("Goal5809 staged target file differs")
    target = _read_json_bytes(target_payload, "staged target")
    target_unsigned = dict(target)
    target_seal = target_unsigned.pop("target_manifest_sha256", None)
    if target_seal != _digest(target_unsigned) \
            or target_seal != authority["staged_target"]["semantic_sha256"]:
        raise RuntimeError("Goal5809 staged target semantic seal differs")
    for name, row in target["files"].items():
        record = _file_record(Path(str(row["path"])))
        if record != dict(row):
            raise RuntimeError(f"Goal5809 staged product differs: {name}")
    identity_row = authority.get("successor_execution_identity")
    if not isinstance(identity_row, Mapping):
        raise RuntimeError("Goal5809 successor execution identity is absent")
    identity = admit_execution_identity(
        Path(str(identity_row["path"])),
        expected_file_sha256=str(identity_row["file_sha256"]))
    if identity["execution_identity_sha256"] \
            != identity_row.get("semantic_sha256") \
            or identity["file_count"] <= 0 \
            or identity_row.get(
                "goal5802_runtime_manifest_is_dependency_source_only") \
            is not True:
        raise RuntimeError("Goal5809 successor execution identity differs")
    return authority, target


def _preflight(args: argparse.Namespace) -> dict[str, Any]:
    root = args.bundle_root.resolve(strict=True)
    bundle = _verify_bundle(root)
    staging = args.staging_root.resolve(strict=True)
    authority, target = _validate_staging(staging)

    source_root = root / "source"
    sys.path.insert(0, str(source_root / "src"))
    sys.path.insert(0, str(source_root))
    modules = {}
    for name in ("numpy", "cupy", "optix", "rtdsl", "rtdsl.v4_rtdlexe"):
        module = importlib.import_module(name)
        modules[name] = {
            "module_file": str(Path(module.__file__).resolve(strict=True)),
            "version": getattr(module, "__version__", None),
        }
    cupy = sys.modules["cupy"]
    properties = cupy.cuda.runtime.getDeviceProperties(0)
    major = int(properties.get("major", properties.get(b"major")))
    minor = int(properties.get("minor", properties.get(b"minor")))
    raw_name = properties.get("name", properties.get(b"name"))
    device_name = raw_name.decode() if isinstance(raw_name, bytes) \
        else str(raw_name)
    if [major, minor] != [8, 6] or "RTX A4500" not in device_name:
        raise RuntimeError({
            "Goal5809_target_gpu_mismatch": device_name,
            "compute_capability": [major, minor],
            "required": ["NVIDIA RTX A4500", [8, 6]],
        })
    native_path = Path(target["files"]["native_library"]["path"])
    ctypes.CDLL(str(native_path), mode=getattr(ctypes, "RTLD_LOCAL", 0))

    pilot_module = importlib.import_module(
        "scripts.goal5809_runtime_session_two_app_pilot")
    admitted = pilot_module._admit_target(
        Path(authority["staged_target"]["path"]),
        expected_file_sha256=authority["staged_target"]["file_sha256"])
    identity_row = authority["successor_execution_identity"]
    execution_identity = admit_execution_identity(
        Path(identity_row["path"]),
        expected_file_sha256=identity_row["file_sha256"],
        require_runtime_environment=True)
    rtdl_loaded = verify_loaded_rtdl(
        execution_identity,
        rtdl_module=sys.modules["rtdsl"],
        implementation_module=sys.modules["rtdsl.v4_rtdlexe"])
    pyoptix_loaded = verify_loaded_pyoptix(
        execution_identity, optix_module=sys.modules["optix"])
    receipt_body: dict[str, Any] = {
        "schema": PREFLIGHT_SCHEMA,
        "status": "COMPLETE__DIAGNOSTIC_READY_FOR_NONFORMAL_FOUR_CELL_PILOT",
        "scope": {
            "diagnostic_pilot_only": True,
            "nonformal_diagnostic": True,
            "formal_evidence": False,
            "paper_evidence": False,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "claim_authorized": False,
            "direct_arm_count": 0,
            "host_language_control_present": False,
            "design_attribution_authorized": False,
        },
        "bundle_manifest_sha256": bundle["bundle_manifest_sha256"],
        "staging_authority_sha256": authority["staging_authority_sha256"],
        "staged_target_file_sha256": admitted["target_file_sha256"],
        "staged_target_semantic_sha256": admitted["target"][
            "target_manifest_sha256"],
        "successor_execution_identity": {
            "manifest_file_sha256": execution_identity[
                "manifest_file_sha256"],
            "semantic_sha256": execution_identity[
                "execution_identity_sha256"],
            "file_count": execution_identity["file_count"],
            "files_rehashed": execution_identity["files_rehashed"],
            "runtime_environment_admission": execution_identity[
                "runtime_environment_admission"],
            "rtdl_loaded_identity": rtdl_loaded,
            "pyoptix_loaded_identity": pyoptix_loaded,
        },
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "modules": modules,
            "gpu_name": device_name,
            "compute_capability": [major, minor],
            "native_library_load": "PASS",
        },
        "cell_matrix": authority["cell_matrix"],
    }
    receipt = {**receipt_body, "preflight_sha256": _digest(receipt_body)}
    if args.output:
        _write_new(args.output.resolve(), _pretty(receipt))
    return receipt


def _collect(args: argparse.Namespace) -> dict[str, Any]:
    root = args.outputs_root.resolve(strict=True)
    preflight_path = root / "preflight_receipt.json"
    preflight = _read_json(preflight_path)
    preflight_unsigned = dict(preflight)
    preflight_seal = preflight_unsigned.pop("preflight_sha256", None)
    expected_scope = {
        "diagnostic_pilot_only": True,
        "nonformal_diagnostic": True,
        "formal_evidence": False,
        "paper_evidence": False,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "claim_authorized": False,
        "direct_arm_count": 0,
        "host_language_control_present": False,
        "design_attribution_authorized": False,
    }
    environment = preflight.get("environment")
    execution_identity = preflight.get("successor_execution_identity")
    if preflight.get("schema") != PREFLIGHT_SCHEMA \
            or preflight.get("status") \
            != "COMPLETE__DIAGNOSTIC_READY_FOR_NONFORMAL_FOUR_CELL_PILOT" \
            or preflight_seal != _digest(preflight_unsigned) \
            or preflight.get("scope") != expected_scope \
            or not isinstance(environment, Mapping) \
            or environment.get("compute_capability") != [8, 6] \
            or "RTX A4500" not in str(environment.get("gpu_name")) \
            or environment.get("native_library_load") != "PASS" \
            or not isinstance(execution_identity, Mapping) \
            or execution_identity.get("files_rehashed") is not True \
            or execution_identity.get(
                "rtdl_loaded_identity", {}).get(
                    "rtdl_loaded_identity_verified") is not True \
            or execution_identity.get(
                "pyoptix_loaded_identity", {}).get(
                    "pyoptix_loaded_identity_verified") is not True:
        raise RuntimeError("Goal5809 exact A4500 preflight receipt differs")

    expected_target_file = preflight.get("staged_target_file_sha256")
    expected_target_semantic = preflight.get(
        "staged_target_semantic_sha256")
    expected_identity_file = execution_identity.get("manifest_file_sha256")
    expected_identity_semantic = execution_identity.get("semantic_sha256")
    custody_root = root / "staging_custody"
    bundle_copy_path = custody_root / "BUNDLE_MANIFEST.json"
    authority_copy_path = custody_root / "staging_authority.json"
    identity_copy_path = custody_root / "execution_identity_manifest.json"
    target_copy_path = custody_root / "target_manifest.json"
    candidate_copy_path = custody_root / "candidate_manifest.json"

    bundle_copy = _read_json(bundle_copy_path)
    bundle_unsigned = dict(bundle_copy)
    bundle_seal = bundle_unsigned.pop("bundle_manifest_sha256", None)
    authority_copy = _read_json(authority_copy_path)
    authority_unsigned = dict(authority_copy)
    authority_seal = authority_unsigned.pop("staging_authority_sha256", None)
    identity_copy = _read_json(identity_copy_path)
    identity_unsigned = dict(identity_copy)
    identity_seal = identity_unsigned.pop("execution_identity_sha256", None)
    target_copy = _read_json(target_copy_path)
    target_unsigned = dict(target_copy)
    target_seal = target_unsigned.pop("target_manifest_sha256", None)
    candidate_descriptor = target_copy.get("files", {}).get(
        "candidate_manifest", {})
    authority_identity = authority_copy.get("successor_execution_identity", {})
    authority_target = authority_copy.get("staged_target", {})
    if bundle_copy.get("schema") != SCHEMA \
            or bundle_seal != _digest(bundle_unsigned) \
            or bundle_seal != preflight.get("bundle_manifest_sha256") \
            or authority_copy.get("schema") != STAGING_SCHEMA \
            or authority_seal != _digest(authority_unsigned) \
            or authority_seal != preflight.get("staging_authority_sha256") \
            or identity_copy.get("schema") != EXECUTION_IDENTITY_SCHEMA \
            or identity_copy.get("status") != EXECUTION_IDENTITY_STATUS \
            or identity_seal != _digest(identity_unsigned) \
            or identity_seal != expected_identity_semantic \
            or _sha(identity_copy_path) != expected_identity_file \
            or authority_identity.get("file_sha256") \
            != expected_identity_file \
            or authority_identity.get("semantic_sha256") \
            != expected_identity_semantic \
            or target_seal != _digest(target_unsigned) \
            or _sha(target_copy_path) != expected_target_file \
            or target_seal != expected_target_semantic \
            or authority_target.get("file_sha256") != expected_target_file \
            or authority_target.get("semantic_sha256") \
            != expected_target_semantic \
            or candidate_descriptor.get("bytes") \
            != candidate_copy_path.stat().st_size \
            or candidate_descriptor.get("sha256") \
            != _sha(candidate_copy_path):
        raise RuntimeError("Goal5809 collected staging custody differs")
    admitted_collected_identity = admit_execution_identity(
        identity_copy_path,
        expected_file_sha256=str(expected_identity_file))
    if admitted_collected_identity["execution_identity_sha256"] \
            != expected_identity_semantic:
        raise RuntimeError("Goal5809 collected execution identity differs")
    files = []
    cells = []
    for first_app, arm_order in CELL_SPECS:
        cell_name = f"{first_app}-first__{arm_order}"
        cell = root / cell_name
        summary = _read_json(cell / "summary.json")
        summary_unsigned = dict(summary)
        controller_seal = summary_unsigned.pop("controller_sha256", None)
        if summary.get("schema") \
                != "rtdl.goal5809.two_app_fresh_process_controller.v2" \
                or summary.get("status") \
                != ("COMPLETE__DIAGNOSTIC_TWO_ARM_TWO_APPLICATION_"
                    "FRESH_PROCESS_PILOT") \
                or controller_seal != _digest(summary_unsigned):
            raise RuntimeError(
                f"Goal5809 controller seal differs: {cell_name}")
        if summary.get("formal_worker_count") != 0 \
                or summary.get("registered_performance_timing_count") != 0:
            raise RuntimeError(f"Goal5809 cell escaped non-formal scope: {cell_name}")
        execution = summary.get("execution", {})
        if execution.get("first_app") != first_app \
                or execution.get("arm_order") != (
                    ["rtdl", "pyoptix"] if arm_order == "rtdl-first"
                    else ["pyoptix", "rtdl"]):
            raise RuntimeError(f"Goal5809 cell identity differs: {cell_name}")
        target = summary.get("target")
        identity = summary.get("execution_identity")
        if not isinstance(target, Mapping) \
                or target.get("file_sha256") != expected_target_file \
                or target.get("semantic_sha256") != expected_target_semantic \
                or not isinstance(identity, Mapping) \
                or identity.get("manifest_file_sha256") \
                != expected_identity_file \
                or identity.get("execution_identity_sha256") \
                != expected_identity_semantic:
            raise RuntimeError(
                f"Goal5809 cell preflight identity differs: {cell_name}")
        children = summary.get("children")
        if not isinstance(children, Mapping) or set(children) \
                != {"rtdl", "pyoptix"}:
            raise RuntimeError(f"Goal5809 child set differs: {cell_name}")
        child_hashes: dict[str, str] = {}
        for arm in ("rtdl", "pyoptix"):
            child = children[arm]
            if not isinstance(child, Mapping):
                raise RuntimeError(
                    f"Goal5809 child descriptor differs: {cell_name}/{arm}")
            child_path = Path(str(child.get("output_path"))).resolve(
                strict=True)
            if child_path.parent != cell.resolve(strict=True) \
                    or child_path.stat().st_size != child.get("output_bytes") \
                    or _sha(child_path) != child.get("output_sha256"):
                raise RuntimeError(
                    f"Goal5809 child file differs: {cell_name}/{arm}")
            child_result = _read_json(child_path)
            child_unsigned = dict(child_result)
            child_seal = child_unsigned.pop("pilot_sha256", None)
            expected_child = {
                "rtdl": (
                    "rtdl.goal5809.runtime_session_two_app_pilot.v2",
                    "COMPLETE__DIAGNOSTIC_TWO_APPLICATION_"
                    "RUNTIME_SESSION_PILOT"),
                "pyoptix": (
                    "rtdl.goal5809.pyoptix_two_app_pilot.v2",
                    "COMPLETE__DIAGNOSTIC_IDIOMATIC_PYOPTIX_"
                    "TWO_APPLICATION_PILOT"),
            }[arm]
            if (child_result.get("schema"), child_result.get("status")) \
                    != expected_child \
                    or child_seal != _digest(child_unsigned) \
                    or child_result.get("formal_worker_count") != 0 \
                    or child_result.get(
                        "registered_performance_timing_count") != 0:
                raise RuntimeError(
                    f"Goal5809 child seal/scope differs: {cell_name}/{arm}")
            child_hashes[arm] = str(child["output_sha256"])
        cells.append({
            "cell": cell_name,
            "first_app": first_app,
            "arm_order": arm_order,
            "controller_sha256": summary["controller_sha256"],
            "child_output_sha256": child_hashes,
        })
    for path in sorted(
            (row for row in root.rglob("*") if row.is_file()),
            key=lambda row: row.relative_to(root).as_posix().encode()):
        files.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha(path),
        })
    body: dict[str, Any] = {
        "schema": COLLECTION_SCHEMA,
        "status": "COMPLETE__DIAGNOSTIC_FOUR_NONFORMAL_CELLS_COLLECTED",
        "scope": {
            "diagnostic_pilot_only": True,
            "nonformal_diagnostic": True,
            "formal_evidence": False,
            "paper_evidence": False,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "claim_authorized": False,
            "direct_arm_count": 0,
            "host_language_control_present": False,
            "design_attribution_authorized": False,
        },
        "preflight": {
            "path": "preflight_receipt.json",
            "bytes": preflight_path.stat().st_size,
            "file_sha256": _sha(preflight_path),
            "semantic_sha256": preflight["preflight_sha256"],
            "gpu_name": environment["gpu_name"],
            "compute_capability": environment["compute_capability"],
            "staged_target_file_sha256": expected_target_file,
            "staged_target_semantic_sha256": expected_target_semantic,
            "execution_identity_manifest_file_sha256": (
                expected_identity_file),
            "execution_identity_semantic_sha256": (
                expected_identity_semantic),
            "bundle_manifest_semantic_sha256": bundle_seal,
            "staging_authority_file_sha256": _sha(authority_copy_path),
            "staging_authority_semantic_sha256": authority_seal,
            "staging_custody_copy_rehashed": True,
        },
        "cells": cells,
        "files": files,
    }
    collection = {**body, "collection_sha256": _digest(body)}
    _write_new(root / "collection_manifest.json", _pretty(collection))
    if args.output_archive:
        _write_tar_gz(root, args.output_archive.resolve())
        collection["output_archive"] = {
            "path": str(args.output_archive.resolve(strict=True)),
            "bytes": args.output_archive.resolve(strict=True).stat().st_size,
            "sha256": _sha(args.output_archive.resolve(strict=True)),
        }
    return collection


def _defaults(root: Path) -> dict[str, Path]:
    docs = root / "history" / "internal_docs"
    return {
        "archive": docs /
            "goal5806_triangle_product_projection_evidence_20260826.tar.gz",
        "goal5807_archive": docs /
            "goal5807_provider_ready_formal_v2_20260827_0112.tar.gz",
        "goal5807_pilot_source": root /
            "scripts/goal5807_provider_ready_pilot.py",
        "target": docs /
            "goal5806_same_source_postimport_target_20260826.json",
        "contract": docs /
            "goal5807_provider_ready_confirmatory_formal_contract_v2_20260827.json",
        "result": docs /
            "goal5807_provider_ready_formal_result_20260827.json",
        "review": docs /
            "review_goal5807_provider_ready_formal_result_20260827.md",
        "closure": docs /
            "goal5807_external_review_absorption_and_"
            "goal5809_claim_authority_closure_20260827.json",
        "goal5806_result": docs /
            "goal5806_triangle_product_projection_and_two_cold_"
            "regimes_result_20260826.json",
        "goal5806_technical_report": docs /
            "goal5806_triangle_product_projection_and_two_cold_"
            "regimes_technical_report_20260826.md",
        "goal5806_cfr": docs /
            "call_for_review_goal5806_triangle_product_projection_and_"
            "two_cold_regimes_20260826.md",
        "goal5806_evaluation": docs /
            "goal5806_same_source_postimport_formal_evaluation_20260826.json",
        "goal5806_recount": docs /
            "goal5806_same_source_postimport_independent_recount_20260826.json",
        "goal5807_reconciliation_json": docs /
            "goal5807_postreview_absolute_phase_reconciliation_20260827.json",
        "goal5807_reconciliation_report": docs /
            "goal5807_postreview_absolute_phase_reconciliation_20260827.md",
        "goal5807_reconciliation_absorption": docs /
            "goal5807_postreview_absolute_phase_reconciliation_absorption_"
            "and_goal5809_entry_20260827.json",
        "goal5809_claim_authority_addendum": docs /
            "goal5809_detached_reconciliation_and_goal5806_claim_ceiling_"
            "addendum_20260827.json",
    }


def _parser() -> argparse.ArgumentParser:
    repository_root = Path(__file__).resolve(strict=True).parent.parent
    defaults = _defaults(repository_root)
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument(
        "--goal5806-archive", type=Path, default=defaults["archive"])
    inspect_parser.add_argument(
        "--goal5806-target", type=Path, default=defaults["target"])
    inspect_parser.add_argument("--output", type=Path)

    build = subparsers.add_parser("build")
    build.add_argument("--repository-root", type=Path, default=repository_root)
    build.add_argument(
        "--goal5806-archive", type=Path, default=defaults["archive"])
    build.add_argument(
        "--goal5807-archive", type=Path,
        default=defaults["goal5807_archive"])
    build.add_argument(
        "--goal5807-pilot-source", type=Path,
        default=defaults["goal5807_pilot_source"])
    build.add_argument(
        "--goal5806-target", type=Path, default=defaults["target"])
    build.add_argument(
        "--goal5807-contract", type=Path, default=defaults["contract"])
    build.add_argument(
        "--goal5807-result", type=Path, default=defaults["result"])
    build.add_argument(
        "--goal5807-review", type=Path, default=defaults["review"])
    build.add_argument(
        "--goal5807-closure", type=Path, default=defaults["closure"])
    build.add_argument(
        "--goal5806-result", type=Path, default=defaults["goal5806_result"])
    build.add_argument(
        "--goal5806-technical-report", type=Path,
        default=defaults["goal5806_technical_report"])
    build.add_argument(
        "--goal5806-cfr", type=Path, default=defaults["goal5806_cfr"])
    build.add_argument(
        "--goal5806-evaluation", type=Path,
        default=defaults["goal5806_evaluation"])
    build.add_argument(
        "--goal5806-recount", type=Path,
        default=defaults["goal5806_recount"])
    build.add_argument(
        "--goal5807-reconciliation-json", type=Path,
        default=defaults["goal5807_reconciliation_json"])
    build.add_argument(
        "--goal5807-reconciliation-report", type=Path,
        default=defaults["goal5807_reconciliation_report"])
    build.add_argument(
        "--goal5807-reconciliation-absorption", type=Path,
        default=defaults["goal5807_reconciliation_absorption"])
    build.add_argument(
        "--goal5809-claim-authority-addendum", type=Path,
        default=defaults["goal5809_claim_authority_addendum"])
    build.add_argument("--matched-ptx", type=Path)
    build.add_argument("--relation-compaction-cubin", type=Path)
    build.add_argument("--runtime-manifest", type=Path)
    build.add_argument("--target-observation", type=Path)
    build.add_argument("--output", type=Path, required=True)

    materialize = subparsers.add_parser("materialize")
    materialize.add_argument("--bundle-root", type=Path, required=True)
    materialize.add_argument("--staging-root", type=Path, required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--bundle-root", type=Path, required=True)
    preflight.add_argument("--staging-root", type=Path, required=True)
    preflight.add_argument("--output", type=Path)

    collect = subparsers.add_parser("collect")
    collect.add_argument("--outputs-root", type=Path, required=True)
    collect.add_argument("--output-archive", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "inspect":
        result = _inspect_archive(args.goal5806_archive, args.goal5806_target)
        if args.output:
            _write_new(args.output.resolve(), _pretty(result))
    elif args.command == "build":
        result = _build_bundle(args)
    elif args.command == "materialize":
        result = _materialize(args)
    elif args.command == "preflight":
        result = _preflight(args)
    elif args.command == "collect":
        result = _collect(args)
    else:  # pragma: no cover - argparse enforces this branch.
        raise RuntimeError("unsupported Goal5809 bundle operation")
    sys.stdout.write(json.dumps(result, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
