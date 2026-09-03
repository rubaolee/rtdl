#!/usr/bin/env python3
"""Build or verify Goal5842's first-generation V12 evidence authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "history/internal_docs/goal5842_causal_admission_cost_20260903"
ARCHIVE_PATH = EVIDENCE_ROOT / "pod_artifacts/goal5842_v12_ada_complete.tar.gz"
PREREGISTRATION_RELATIVE_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V12.json"
)
AUTHORITY_PATH = EVIDENCE_ROOT / "V12_ADA_FIRST_GENERATION_AUTHORITY.json"

SOURCE_COMMIT = "04305fc820290cc183a599376f13d2fb48175233"
TRANSACTION_NAME = "goal5842-ada-04305fc82-transaction12"
PREREGISTRATION_SHA256 = (
    "9bcb9876bca6234756c9c49b0caf12956fd87a13748a62074278194446e67570"
)
PREREGISTRATION_FILE_SHA256 = (
    "f90d49a1663338c729f86dd08cf3ce2b51a3845326fe349ec5b80759fd06e509"
)
ARCHIVE_SHA256 = "6dff96a2c76674f56a467ae10ef8e50045792cbf2fc6908c93296e092e8bff21"
ARCHIVE_BYTES = 3_790_441
ARCHIVE_MEMBER_COUNT = 2_325
ARCHIVE_FILE_COUNT = 1_773
ARCHIVE_DIRECTORY_COUNT = 552
ARCHIVE_PAYLOAD_BYTES = 13_200_413
ARCHIVE_ROOTS = {
    TRANSACTION_NAME,
    "goal5842-direct-04305fc82-v12",
    "goal5842-native-04305fc82-v12",
    "goal5842-v12-driver.pid",
    "goal5842-v12-driver.stderr",
    "goal5842-v12-driver.stdout",
}
AUTHORITY_DOMAIN = b"rtdl.goal5842.first_generation_authority.v1\0"

HARDWARE = {
    "architecture_generation": "ADA",
    "compute_capability": "8.9",
    "driver_version": "580.159.04",
    "gpu_model": "NVIDIA RTX 2000 Ada Generation",
    "gpu_uuid": "GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9",
    "vram_bytes": "17175674880",
}
EXPECTED_STAGE_NAMES = (
    "00_bind_execution_authority",
    "01_gpu_identity_witness_no_timing",
    "02_pyoptix_identity_witness_no_timing",
    "03_direct_identity_witness_no_timing",
    "04_causal_admission",
    "05_three_arm_baseline",
    "06_independent_recount",
)
EXPECTED_FILES = {
    f"{TRANSACTION_NAME}/TRANSACTION_COMPLETE.json": (
        277,
        "23a39713f2455a10e179d3247cd6f37f21d56b8243324dee2ffb8cc0573539ce",
    ),
    f"{TRANSACTION_NAME}/execution_authority.json": (
        3_894,
        "ce6e6534696d90a91c66f97375abbeca3bef7f49efab6b3e138cb1855fb766da",
    ),
    f"{TRANSACTION_NAME}/gpu_identity_witness.json": (
        528_551,
        "e0660c15f17c8a22f1c97d0f8b07739e611a4379beb5cc25678c131b4c877dd2",
    ),
    f"{TRANSACTION_NAME}/pyoptix_identity_witness.json": (
        2_608,
        "1f440057a909fd75a850d8760b20cf1451fe066ea48e10792c232d5165994932",
    ),
    f"{TRANSACTION_NAME}/direct_identity_witness.json": (
        2_162,
        "ca9e7d47fd858c73b86f4479aec350bfcbf745bbc0a9d44e79ceec6b73f56ec8",
    ),
    f"{TRANSACTION_NAME}/causal/result.json": (
        47_234,
        "af35c23fa565c0f0f9efdb1bef3713d790a63fee845eed5a545cdcfef70aba02",
    ),
    f"{TRANSACTION_NAME}/baseline/result.json": (
        434_124,
        "8ae539106bc7a591e0924df2d9bfbb19a9877ae4e4582124709229184a75c029",
    ),
    f"{TRANSACTION_NAME}/independent_recount.json": (
        30_204,
        "bf5206a86009a6f9c7519dff45a92d1f527035dc0d05a609fc88f59d762b1a89",
    ),
    "goal5842-direct-04305fc82-v12": (
        119_984,
        "5f6d4d6a5dd7b5545d5283803c4ee1db51158828e84151a74004fd801eebd28c",
    ),
    "goal5842-native-04305fc82-v12/goal5838_native_build.json": (
        316_669,
        "503644b7c33844a826ede9787feb5ccdfaf1267128b22adb1b70f3bdcec3163b",
    ),
    "goal5842-native-04305fc82-v12/librtdl_optix_goal5838.so": (
        7_181_936,
        "083e1d5182f5f1653cbbff8266d587a2826d315352793b444db2a1c2d02fbbd6",
    ),
    "goal5842-v12-driver.stdout": (
        22_904,
        "a81e3fdba915c3b53374711eda9d94c2933a859be8d07877fde01afb91edcaa6",
    ),
    "goal5842-v12-driver.stderr": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def authority_seal(value: Mapping[str, object]) -> str:
    body = dict(value)
    body["authority_sha256"] = ""
    return hashlib.sha256(AUTHORITY_DOMAIN + canonical_bytes(body)).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="ascii"))
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def archive_row(path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": file_sha256(path),
        "member_count": ARCHIVE_MEMBER_COUNT,
        "file_count": ARCHIVE_FILE_COUNT,
        "directory_count": ARCHIVE_DIRECTORY_COUNT,
        "uncompressed_regular_file_bytes": ARCHIVE_PAYLOAD_BYTES,
    }


def validate_member_name(name: str) -> None:
    pure = PurePosixPath(name)
    require(not pure.is_absolute(), f"absolute tar member forbidden: {name}")
    require("\\" not in name, f"backslash tar member forbidden: {name}")
    require(
        all(part not in {"", ".", ".."} for part in pure.parts),
        f"unsafe tar member forbidden: {name}",
    )


def extract_verified_archive(destination: Path) -> None:
    require(ARCHIVE_PATH.is_file(), f"missing V12 archive: {ARCHIVE_PATH}")
    require(ARCHIVE_PATH.stat().st_size == ARCHIVE_BYTES, "V12 archive byte mismatch")
    require(file_sha256(ARCHIVE_PATH) == ARCHIVE_SHA256, "V12 archive SHA mismatch")
    with tarfile.open(ARCHIVE_PATH, "r:gz") as archive:
        members = archive.getmembers()
        require(
            len(members) == ARCHIVE_MEMBER_COUNT, "V12 archive member-count mismatch"
        )
        names = [member.name for member in members]
        require(len(set(names)) == len(names), "V12 archive has duplicate members")
        for member in members:
            validate_member_name(member.name)
            require(
                member.isfile() or member.isdir(),
                f"non-regular V12 archive member forbidden: {member.name}",
            )
        require(
            sum(member.isfile() for member in members) == ARCHIVE_FILE_COUNT,
            "V12 archive file-count mismatch",
        )
        require(
            sum(member.isdir() for member in members) == ARCHIVE_DIRECTORY_COUNT,
            "V12 archive directory-count mismatch",
        )
        require(
            sum(member.size for member in members if member.isfile())
            == ARCHIVE_PAYLOAD_BYTES,
            "V12 archive payload-byte mismatch",
        )
        require(
            {PurePosixPath(name).parts[0] for name in names} == ARCHIVE_ROOTS,
            "V12 archive root set mismatch",
        )
        for member in members:
            output = destination.joinpath(*PurePosixPath(member.name).parts)
            if member.isdir():
                output.mkdir(parents=True, exist_ok=True)
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            require(source is not None, f"cannot read tar member: {member.name}")
            with source, output.open("xb") as stream:
                shutil.copyfileobj(source, stream)


def git_blob(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    require(
        completed.returncode == 0,
        f"cannot read frozen Git blob {commit}:{path}: "
        f"{completed.stderr.decode(errors='replace').strip()}",
    )
    return completed.stdout


def materialize_frozen_source(destination: Path) -> Path:
    preregistration_bytes = git_blob(SOURCE_COMMIT, PREREGISTRATION_RELATIVE_PATH)
    require(
        hashlib.sha256(preregistration_bytes).hexdigest()
        == PREREGISTRATION_FILE_SHA256,
        "frozen preregistration file SHA mismatch",
    )
    preregistration = json.loads(preregistration_bytes)
    require(
        preregistration.get("preregistration_sha256") == PREREGISTRATION_SHA256,
        "frozen preregistration internal seal mismatch",
    )
    source_manifest = preregistration.get("source_manifest")
    require(isinstance(source_manifest, list), "frozen source manifest missing")
    preregistration_output = destination / PREREGISTRATION_RELATIVE_PATH
    preregistration_output.parent.mkdir(parents=True, exist_ok=True)
    preregistration_output.write_bytes(preregistration_bytes)
    for row in source_manifest:
        require(isinstance(row, dict), "frozen source manifest row malformed")
        path = row.get("path")
        require(isinstance(path, str) and path, "frozen source path malformed")
        blob = git_blob(SOURCE_COMMIT, path)
        require(row.get("bytes") == len(blob), f"frozen source bytes differ: {path}")
        require(
            row.get("sha256") == hashlib.sha256(blob).hexdigest(),
            f"frozen source SHA differs: {path}",
        )
        output = destination / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(blob)
    return preregistration_output


def replay_recount(source_root: Path, evidence_root: Path, output: Path) -> None:
    transaction = evidence_root / TRANSACTION_NAME
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(source_root / "src"), str(source_root))
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(source_root / "scripts/goal5842_independent_recount.py"),
            "--preregistration",
            str(source_root / PREREGISTRATION_RELATIVE_PATH),
            "--execution-authority",
            str(transaction / "execution_authority.json"),
            "--identity-witness",
            str(transaction / "gpu_identity_witness.json"),
            "--pyoptix-identity-witness",
            str(transaction / "pyoptix_identity_witness.json"),
            "--direct-identity-witness",
            str(transaction / "direct_identity_witness.json"),
            "--causal-root",
            str(transaction / "causal"),
            "--baseline-root",
            str(transaction / "baseline"),
            "--output",
            str(output),
        ],
        cwd=source_root,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    require(
        completed.returncode == 0,
        "independent recount replay failed: "
        + (completed.stderr or completed.stdout).strip(),
    )


def compact_causal_summaries(rows: object) -> list[dict[str, object]]:
    require(
        isinstance(rows, list) and len(rows) == 3, "causal task summary count differs"
    )
    keys = (
        "task",
        "worker_count",
        "block_count",
        "check_on_causal_phase_median_ns",
        "check_off_causal_phase_median_ns",
        "primary_causal_phase_delta_median_ns",
        "primary_causal_phase_delta_bootstrap_95_percent_ns",
        "route_declaration_negative_control_delta_median_ns",
        "secondary_total_capability_delta_median_ns",
        "secondary_total_capability_delta_bootstrap_95_percent_ns",
        "ratio_to_check_off_reported",
    )
    return [{key: row[key] for key in keys} for row in rows]


def compact_baseline_summaries(rows: object) -> list[dict[str, object]]:
    require(
        isinstance(rows, list) and len(rows) == 2, "baseline task summary count differs"
    )
    return [
        {
            "task": row["task"],
            "arm_medians_ns": row["arm_medians_ns"],
            "comparisons": row["comparisons"],
        }
        for row in rows
    ]


def validate_transaction(extracted: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    transaction = extracted / TRANSACTION_NAME
    require(transaction.is_dir(), "V12 transaction root missing")
    for relative, (expected_bytes, expected_sha256) in EXPECTED_FILES.items():
        path = extracted / relative
        require(path.is_file(), f"expected V12 file missing: {relative}")
        require(path.stat().st_size == expected_bytes, f"V12 bytes differ: {relative}")
        require(file_sha256(path) == expected_sha256, f"V12 SHA differs: {relative}")
    failure_markers = sorted(
        path.name
        for path in transaction.iterdir()
        if path.is_file()
        and ("FAILED" in path.name or path.name == "failure_state.json")
    )
    require(not failure_markers, f"V12 failure marker present: {failure_markers}")
    stage_root = transaction / "stage_logs"
    require(
        {path.name for path in stage_root.iterdir() if path.is_dir()}
        == set(EXPECTED_STAGE_NAMES),
        "V12 stage-directory set differs",
    )
    for stage in EXPECTED_STAGE_NAMES:
        stage_directory = stage_root / stage
        require(
            (stage_directory / "returncode.txt").read_text() == "0\n",
            f"stage failed: {stage}",
        )
        require(
            (stage_directory / "stderr.txt").read_bytes() == b"",
            f"stage stderr nonempty: {stage}",
        )
    complete = read_json(transaction / "TRANSACTION_COMPLETE.json")
    require(
        complete
        == {
            "architecture_generation": "ADA",
            "cross_generation_gate_passed": False,
            "public_performance_claim_authorized": False,
            "recount_sha256": (
                "70305326b122e15806f9a67353b259620fcbb85932f6bbc04f002b4c899bbab3"
            ),
            "status": "PASS__ONE_GPU_GENERATION_TRANSACTION_COMPLETE",
        },
        "V12 completion marker differs",
    )
    execution_authority = read_json(transaction / "execution_authority.json")
    require(
        execution_authority.get("source_commit") == SOURCE_COMMIT,
        "source commit differs",
    )
    require(
        execution_authority.get("preregistration_sha256") == PREREGISTRATION_SHA256,
        "execution preregistration seal differs",
    )
    require(
        execution_authority.get("preregistration_file_sha256")
        == PREREGISTRATION_FILE_SHA256,
        "execution preregistration file SHA differs",
    )
    require(
        execution_authority.get("hardware") == HARDWARE, "hardware identity differs"
    )
    require(
        execution_authority.get("repository_status_short") == [],
        "source checkout was dirty",
    )
    require(
        execution_authority.get("status") == "AUTHORIZED_FOR_FORMAL_WORKER_ZERO"
        and execution_authority.get("owner_authorized_goal5842_execution") is True
        and execution_authority.get("gpu_execution_count") == 0
        and execution_authority.get("registered_timing_observation_count") == 0,
        "execution authority boundary differs",
    )
    identity = read_json(transaction / "gpu_identity_witness.json")
    pyoptix_identity = read_json(transaction / "pyoptix_identity_witness.json")
    direct_identity = read_json(transaction / "direct_identity_witness.json")
    for label, witness in (
        ("RTDL", identity),
        ("PyOptiX", pyoptix_identity),
        ("Direct", direct_identity),
    ):
        require(
            witness.get("source_commit") == SOURCE_COMMIT, f"{label} source differs"
        )
        require(
            witness.get("preregistration_sha256") == PREREGISTRATION_SHA256,
            f"{label} preregistration differs",
        )
        require(witness.get("hardware") == HARDWARE, f"{label} hardware differs")
        require(
            witness.get("registered_timing_observation_count") == 0
            and witness.get("performance_claim_authorized") is False,
            f"{label} identity witness contains timing or overclaims",
        )
    require(
        identity.get("status")
        == "PASS__IDENTITY_AND_REPEATED_LIFECYCLE_NO_TIMING_OBSERVED"
        and identity.get("task_count") == 3
        and identity.get("gpu_complete_execution_call_count") == 291
        and identity.get("all_exact_identity_equal") is True,
        "RTDL identity witness summary differs",
    )
    require(
        pyoptix_identity.get("status")
        == "PASS__PYOPTIX_PACKAGE_FRONT_DOOR_REPEATED_LIFECYCLE_NO_TIMING_OBSERVED"
        and pyoptix_identity.get("task_count") == 2
        and pyoptix_identity.get("gpu_complete_execution_call_count") == 144,
        "PyOptiX identity witness summary differs",
    )
    require(
        direct_identity.get("status") == "PASS__DIRECT_FULL_ORACLE_NO_TIMING_OBSERVED"
        and direct_identity.get("task_count") == 2
        and direct_identity.get("gpu_complete_execution_call_count") == 2,
        "Direct identity witness summary differs",
    )
    causal = read_json(transaction / "causal/result.json")
    baseline = read_json(transaction / "baseline/result.json")
    recount = read_json(transaction / "independent_recount.json")
    require(
        causal.get("status") == "PASS__CAUSAL_ADMISSION_COHORT_COMPLETE",
        "causal status differs",
    )
    require(causal.get("worker_count") == 216, "causal worker count differs")
    require(
        causal.get("registered_primary_observation_count") == 216,
        "causal observation count differs",
    )
    require(
        causal.get("external_review_or_consensus") is False
        and causal.get("process_wall_is_not_causal_estimand") is True,
        "causal claim boundary differs",
    )
    require(
        baseline.get("status") == "PASS__TWO_TASK_THREE_ARM_BASELINE_COMPLETE",
        "baseline status differs",
    )
    require(baseline.get("subworker_count") == 216, "baseline subworker count differs")
    require(
        baseline.get("composite_worker_count") == 108,
        "baseline composite count differs",
    )
    require(
        baseline.get("external_review_or_consensus") is False
        and baseline.get("registered_performance_gate") is None
        and baseline.get("cross_arm_generated_artifact_identity_claimed") is False
        and baseline.get("cross_arm_public_input_output_contract_exact") is True
        and baseline.get("oracle_validation_outside_registered_intervals") is True,
        "baseline claim or fairness boundary differs",
    )
    require(
        recount.get("status") == "PASS__ONE_GPU_GENERATION_RECOUNT_COMPLETE",
        "recount status differs",
    )
    require(
        recount.get("recount_sha256") == complete["recount_sha256"],
        "recount seal differs",
    )
    require(recount.get("hardware") == HARDWARE, "recount hardware differs")
    require(recount.get("causal_receipt_count") == 216, "recount causal count differs")
    require(
        recount.get("baseline_composite_count") == 108, "recount baseline count differs"
    )
    require(
        recount.get("distinct_gpu_architecture_generation_count") == 1,
        "generation count differs",
    )
    require(
        recount.get("required_gpu_architecture_generation_count") == 2,
        "generation requirement differs",
    )
    require(
        recount.get("cross_generation_gate_passed") is False,
        "recount overclaims generation gate",
    )
    require(
        recount.get("public_performance_claim_authorized") is False,
        "recount overclaims public performance",
    )
    require(
        recount.get("external_review_or_consensus") is False,
        "recount overclaims review or consensus",
    )
    return causal, baseline


def build() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="goal5842-v12-authority-") as temporary:
        temporary_root = Path(temporary)
        extracted = temporary_root / "evidence"
        extracted.mkdir()
        extract_verified_archive(extracted)
        causal, baseline = validate_transaction(extracted)
        source_root = temporary_root / "source"
        source_root.mkdir()
        materialize_frozen_source(source_root)
        replay = temporary_root / "independent_recount_replay.json"
        replay_recount(source_root, extracted, replay)
        archived_recount = extracted / TRANSACTION_NAME / "independent_recount.json"
        require(
            replay.read_bytes() == archived_recount.read_bytes(),
            "local independent recount is not byte-identical to pod recount",
        )
        result: dict[str, object] = {
            "schema": "rtdl.goal5842.first_generation_authority.v1",
            "status": (
                "PASS__V12_ADA_FIRST_GENERATION_EVIDENCE_VERIFIED__"
                "SECOND_GENERATION_REQUIRED"
            ),
            "source_commit": SOURCE_COMMIT,
            "preregistration": {
                "path": PREREGISTRATION_RELATIVE_PATH,
                "file_sha256": PREREGISTRATION_FILE_SHA256,
                "preregistration_sha256": PREREGISTRATION_SHA256,
                "v12_result_blind": False,
                "v11_rows_pooled": False,
            },
            "archive": archive_row(ARCHIVE_PATH),
            "hardware": HARDWARE,
            "execution": {
                "formal_transaction_name": TRANSACTION_NAME,
                "formal_stage_names": list(EXPECTED_STAGE_NAMES),
                "formal_stage_count": len(EXPECTED_STAGE_NAMES),
                "all_stage_returncodes_zero": True,
                "all_stage_stderr_empty": True,
                "transaction_failure_marker_present": False,
                "causal_receipt_count": 216,
                "baseline_subworker_count": 216,
                "baseline_composite_count": 108,
                "local_recount_byte_identical_to_pod_recount": True,
                "recount_file_sha256": EXPECTED_FILES[
                    f"{TRANSACTION_NAME}/independent_recount.json"
                ][1],
                "recount_sha256": (
                    "70305326b122e15806f9a67353b259620fcbb85932f6bbc04f002b4c899bbab3"
                ),
            },
            "identity_witnesses": {
                "rtdl_task_count": 3,
                "rtdl_gpu_complete_execution_call_count": 291,
                "pyoptix_task_count": 2,
                "pyoptix_gpu_complete_execution_call_count": 144,
                "direct_task_count": 2,
                "direct_gpu_complete_execution_call_count": 2,
                "registered_timing_observation_count": 0,
                "all_registered_baseline_cross_arm_public_outputs_exact": True,
                "sphere_provider_baseline_claimed": False,
            },
            "causal_summaries": compact_causal_summaries(causal["task_summaries"]),
            "baseline_summaries": compact_baseline_summaries(
                baseline["task_summaries"]
            ),
            "claim_boundary": {
                "goal5842_complete": False,
                "observed_gpu_architecture_generation_count": 1,
                "required_gpu_architecture_generation_count": 2,
                "cross_generation_gate_passed": False,
                "cross_machine_raw_time_ratio_computed": False,
                "public_performance_claim_authorized": False,
                "external_review_or_consensus": False,
                "checker_off_is_supported_api": False,
                "checker_removal_recommended": False,
                "hardware_independent_performance_claimed": False,
            },
            "authority_sha256": "",
        }
        result["authority_sha256"] = authority_seal(result)
        return result


def verify_stored() -> dict[str, object]:
    observed = read_json(AUTHORITY_PATH)
    require(
        observed.get("authority_sha256") == authority_seal(observed),
        "stored authority seal mismatch",
    )
    rebuilt = build()
    require(
        observed == rebuilt, "stored first-generation authority differs from rebuild"
    )
    return observed


def write_output(path: Path) -> dict[str, object]:
    result = build()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="ascii") as stream:
        json.dump(
            result, stream, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False
        )
        stream.write("\n")
    return result


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args(argv)
    result = (
        verify_stored() if args.verify_stored else write_output(args.output.resolve())
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
