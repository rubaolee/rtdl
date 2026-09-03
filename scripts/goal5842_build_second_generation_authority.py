#!/usr/bin/env python3
"""Build or verify Goal5842's Ampere V12 generation authority."""

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

from scripts.goal5842_build_first_generation_authority import (
    compact_baseline_summaries,
    compact_causal_summaries,
    materialize_frozen_source,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "history/internal_docs/goal5842_causal_admission_cost_20260903"
ARCHIVE_PATH = EVIDENCE_ROOT / "pod_artifacts/goal5842_v12_ampere_a6000_complete.tar.gz"
RECOUNT_EXPORT_PATH = EVIDENCE_ROOT / "V12_AMPERE_INDEPENDENT_RECOUNT.json"
AUTHORITY_PATH = EVIDENCE_ROOT / "V12_AMPERE_SECOND_GENERATION_AUTHORITY.json"
PREREGISTRATION_RELATIVE_PATH = (
    "history/internal_docs/goal5842_causal_admission_cost_20260903/"
    "PREREGISTRATION_V12.json"
)

SOURCE_COMMIT = "04305fc820290cc183a599376f13d2fb48175233"
TRANSACTION_NAME = "goal5842-v12-ampere-a6000-transaction01"
PREREGISTRATION_SHA256 = (
    "9bcb9876bca6234756c9c49b0caf12956fd87a13748a62074278194446e67570"
)
PREREGISTRATION_FILE_SHA256 = (
    "f90d49a1663338c729f86dd08cf3ce2b51a3845326fe349ec5b80759fd06e509"
)
ARCHIVE_SHA256 = "df4e1e1062ffbb4907608ca61c0bd791d49f182889821ab4e75c382718e444a7"
ARCHIVE_BYTES = 3_640_458
ARCHIVE_MEMBER_COUNT = 2_329
ARCHIVE_FILE_COUNT = 1_776
ARCHIVE_DIRECTORY_COUNT = 553
ARCHIVE_PAYLOAD_BYTES = 12_941_854
RECOUNT_BYTES = 30_123
RECOUNT_FILE_SHA256 = (
    "b72a1df3cc5c6983e7b6f69719bddcfb1a767e7ebd41955fd25b7b7613ae5560"
)
RECOUNT_SHA256 = "4590c10d47541d1e2bdb834f43bc6b9c3046f92bf506b7b02e5782579e7ef984"
AUTHORITY_DOMAIN = b"rtdl.goal5842.second_generation_authority.v1\0"

HARDWARE = {
    "architecture_generation": "AMPERE",
    "compute_capability": "8.6",
    "driver_version": "550.127.08",
    "gpu_model": "NVIDIA RTX A6000",
    "gpu_uuid": "GPU-6457d4af-a4bb-bff5-a9d2-02f251ceca27",
    "vram_bytes": "51527024640",
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
ARCHIVE_ROOTS = {
    TRANSACTION_NAME,
    "goal5842-direct-ampere-a6000-v1",
    "goal5842-native-ampere-a6000-v1",
    "goal5842-v12-ampere-driver.pid",
    "goal5842-v12-ampere-driver.stderr",
    "goal5842-v12-ampere-driver.stdout",
    "goal5842-v12-ampere-preflight.stderr",
    "goal5842-v12-ampere-preflight.stdout",
    "V12_AMPERE_PREPARATION_NOTES.md",
}
EXPECTED_FILES = {
    f"{TRANSACTION_NAME}/TRANSACTION_COMPLETE.json": (
        280,
        "96bec1f2adf698585fda1fd5bf53dc361374bf8099f3257c9eb2ddd60fddf72b",
    ),
    f"{TRANSACTION_NAME}/execution_authority.json": (
        3_881,
        "84b43523f2b0aa61a2cdf7b53f7caef71ff3035174a244cd49f826cb9bf0a529",
    ),
    f"{TRANSACTION_NAME}/gpu_identity_witness.json": (
        528_540,
        "2fa42f69c7a7ea3d7e8d71fd12d4c67bbe72c474abb95b2b1b4f7deafc5461b8",
    ),
    f"{TRANSACTION_NAME}/pyoptix_identity_witness.json": (
        2_597,
        "50a2dd51c2bd902142870c76b75786899aa4137323a472d3b1fbb094373bfc02",
    ),
    f"{TRANSACTION_NAME}/direct_identity_witness.json": (
        2_151,
        "e09baadbfbb30663853ef6486971bc58789e2d59d0f4d89a45b6d24e82ccac48",
    ),
    f"{TRANSACTION_NAME}/causal/result.json": (
        46_940,
        "0e4ddce2f52d4eb18cf24d0dd127f55ac82fd774a1331cbf0820f82a78f99395",
    ),
    f"{TRANSACTION_NAME}/baseline/result.json": (
        436_334,
        "c9e41cdacfe2e176f1342597e4d08cb7c9171c9cf28ecb3f7c592b5faf36ec0b",
    ),
    f"{TRANSACTION_NAME}/independent_recount.json": (
        RECOUNT_BYTES,
        RECOUNT_FILE_SHA256,
    ),
    "goal5842-direct-ampere-a6000-v1/goal5842-direct": (
        119_984,
        "6588529aa1a7fb42fd5a1a0a509145b7f57abf4184f37281c34cbe9d3bcab021",
    ),
    "goal5842-native-ampere-a6000-v1/goal5838_native_build.json": (
        14_085,
        "8aba844997b6b889348a20adf6110a8dd45cf7c86869be964ca96856778d0a22",
    ),
    "goal5842-native-ampere-a6000-v1/librtdl_optix_goal5838.so": (
        7_181_928,
        "04f319f805eaf8e420227d20b5d30cbe8a220b928112fe8915e16de0ea912a3f",
    ),
    "goal5842-native-ampere-a6000-v1/goal5838_native_build.log": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
    "goal5842-v12-ampere-driver.stdout": (
        22_823,
        "d23bb37b5074bd069d82984e199a3b3166edfde396e3423b72c977c14c23f560",
    ),
    "goal5842-v12-ampere-driver.stderr": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
    "goal5842-v12-ampere-preflight.stdout": (
        0,
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ),
    "goal5842-v12-ampere-preflight.stderr": (
        15_316,
        "aeb79d4e0335570a336160a752c7a2018a1e7c1c77d7a40a0d7ebeb52dfdbae5",
    ),
    "V12_AMPERE_PREPARATION_NOTES.md": (
        3_874,
        "b5eded6710f90023d5cbf063995ffe98430e9fdc6edee2d4991cf02052798260",
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


def validate_member_name(name: str) -> None:
    pure = PurePosixPath(name)
    require(not pure.is_absolute(), f"absolute tar member forbidden: {name}")
    require("\\" not in name, f"backslash tar member forbidden: {name}")
    require(
        all(part not in {"", ".", ".."} for part in pure.parts),
        f"unsafe tar member forbidden: {name}",
    )


def extract_verified_archive(destination: Path) -> None:
    require(ARCHIVE_PATH.is_file(), f"missing Ampere archive: {ARCHIVE_PATH}")
    require(ARCHIVE_PATH.stat().st_size == ARCHIVE_BYTES, "archive byte mismatch")
    require(file_sha256(ARCHIVE_PATH) == ARCHIVE_SHA256, "archive SHA mismatch")
    with tarfile.open(ARCHIVE_PATH, "r:gz") as archive:
        members = archive.getmembers()
        require(len(members) == ARCHIVE_MEMBER_COUNT, "archive member-count mismatch")
        names = [member.name for member in members]
        require(len(set(names)) == len(names), "archive has duplicate members")
        for member in members:
            validate_member_name(member.name)
            require(
                member.isfile() or member.isdir(),
                f"non-regular archive member forbidden: {member.name}",
            )
        require(
            sum(member.isfile() for member in members) == ARCHIVE_FILE_COUNT,
            "archive file-count mismatch",
        )
        require(
            sum(member.isdir() for member in members) == ARCHIVE_DIRECTORY_COUNT,
            "archive directory-count mismatch",
        )
        require(
            sum(member.size for member in members if member.isfile())
            == ARCHIVE_PAYLOAD_BYTES,
            "archive payload-byte mismatch",
        )
        require(
            {PurePosixPath(name).parts[0] for name in names} == ARCHIVE_ROOTS,
            "archive root set mismatch",
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


def validate_transaction(extracted: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    transaction = extracted / TRANSACTION_NAME
    require(transaction.is_dir(), "Ampere transaction root missing")
    for relative, (expected_bytes, expected_sha256) in EXPECTED_FILES.items():
        path = extracted / relative
        require(path.is_file(), f"expected file missing: {relative}")
        require(path.stat().st_size == expected_bytes, f"bytes differ: {relative}")
        require(file_sha256(path) == expected_sha256, f"SHA differs: {relative}")
    require(
        (extracted / "V12_AMPERE_PREPARATION_NOTES.md").read_bytes()
        == (EVIDENCE_ROOT / "V12_AMPERE_PREPARATION_NOTES.md").read_bytes(),
        "archived preparation notes differ from repository record",
    )
    failure_markers = sorted(
        path.name
        for path in transaction.iterdir()
        if path.is_file()
        and ("FAILED" in path.name or path.name == "failure_state.json")
    )
    require(not failure_markers, f"failure marker present: {failure_markers}")
    stage_root = transaction / "stage_logs"
    require(
        {path.name for path in stage_root.iterdir() if path.is_dir()}
        == set(EXPECTED_STAGE_NAMES),
        "stage-directory set differs",
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
            "architecture_generation": "AMPERE",
            "cross_generation_gate_passed": False,
            "public_performance_claim_authorized": False,
            "recount_sha256": RECOUNT_SHA256,
            "status": "PASS__ONE_GPU_GENERATION_TRANSACTION_COMPLETE",
        },
        "completion marker differs",
    )
    execution_authority = read_json(transaction / "execution_authority.json")
    require(execution_authority.get("source_commit") == SOURCE_COMMIT, "source differs")
    require(
        execution_authority.get("preregistration_sha256") == PREREGISTRATION_SHA256,
        "execution preregistration seal differs",
    )
    require(
        execution_authority.get("preregistration_file_sha256")
        == PREREGISTRATION_FILE_SHA256,
        "execution preregistration file SHA differs",
    )
    require(execution_authority.get("hardware") == HARDWARE, "hardware differs")
    require(execution_authority.get("repository_status_short") == [], "checkout dirty")
    require(
        execution_authority.get("status") == "AUTHORIZED_FOR_FORMAL_WORKER_ZERO"
        and execution_authority.get("owner_authorized_goal5842_execution") is True
        and execution_authority.get("gpu_execution_count") == 0
        and execution_authority.get("registered_timing_observation_count") == 0,
        "execution authority boundary differs",
    )
    witnesses = {
        "RTDL": read_json(transaction / "gpu_identity_witness.json"),
        "PyOptiX": read_json(transaction / "pyoptix_identity_witness.json"),
        "Direct": read_json(transaction / "direct_identity_witness.json"),
    }
    for label, witness in witnesses.items():
        require(witness.get("source_commit") == SOURCE_COMMIT, f"{label} source differs")
        require(
            witness.get("preregistration_sha256") == PREREGISTRATION_SHA256,
            f"{label} preregistration differs",
        )
        require(witness.get("hardware") == HARDWARE, f"{label} hardware differs")
        require(
            witness.get("registered_timing_observation_count") == 0
            and witness.get("performance_claim_authorized") is False,
            f"{label} identity witness overclaims",
        )
    require(
        witnesses["RTDL"].get("status")
        == "PASS__IDENTITY_AND_REPEATED_LIFECYCLE_NO_TIMING_OBSERVED"
        and witnesses["RTDL"].get("task_count") == 3
        and witnesses["RTDL"].get("gpu_complete_execution_call_count") == 291
        and witnesses["RTDL"].get("all_exact_identity_equal") is True,
        "RTDL identity witness differs",
    )
    require(
        witnesses["PyOptiX"].get("status")
        == "PASS__PYOPTIX_PACKAGE_FRONT_DOOR_REPEATED_LIFECYCLE_NO_TIMING_OBSERVED"
        and witnesses["PyOptiX"].get("task_count") == 2
        and witnesses["PyOptiX"].get("gpu_complete_execution_call_count") == 144,
        "PyOptiX identity witness differs",
    )
    require(
        witnesses["Direct"].get("status") == "PASS__DIRECT_FULL_ORACLE_NO_TIMING_OBSERVED"
        and witnesses["Direct"].get("task_count") == 2
        and witnesses["Direct"].get("gpu_complete_execution_call_count") == 2,
        "Direct identity witness differs",
    )
    causal = read_json(transaction / "causal/result.json")
    baseline = read_json(transaction / "baseline/result.json")
    recount = read_json(transaction / "independent_recount.json")
    require(
        causal.get("status") == "PASS__CAUSAL_ADMISSION_COHORT_COMPLETE"
        and causal.get("worker_count") == 216
        and causal.get("registered_primary_observation_count") == 216,
        "causal cohort differs",
    )
    require(
        causal.get("external_review_or_consensus") is False
        and causal.get("process_wall_is_not_causal_estimand") is True,
        "causal claim boundary differs",
    )
    require(
        baseline.get("status") == "PASS__TWO_TASK_THREE_ARM_BASELINE_COMPLETE"
        and baseline.get("subworker_count") == 216
        and baseline.get("composite_worker_count") == 108,
        "baseline cohort differs",
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
        recount.get("status") == "PASS__ONE_GPU_GENERATION_RECOUNT_COMPLETE"
        and recount.get("recount_sha256") == RECOUNT_SHA256
        and recount.get("hardware") == HARDWARE
        and recount.get("causal_receipt_count") == 216
        and recount.get("baseline_composite_count") == 108,
        "independent recount differs",
    )
    require(
        recount.get("distinct_gpu_architecture_generation_count") == 1
        and recount.get("required_gpu_architecture_generation_count") == 2
        and recount.get("cross_generation_gate_passed") is False
        and recount.get("public_performance_claim_authorized") is False
        and recount.get("external_review_or_consensus") is False,
        "single-generation recount overclaims",
    )
    return causal, baseline


def build() -> dict[str, object]:
    require(RECOUNT_EXPORT_PATH.is_file(), "missing exported Ampere recount")
    require(RECOUNT_EXPORT_PATH.stat().st_size == RECOUNT_BYTES, "recount export bytes differ")
    require(file_sha256(RECOUNT_EXPORT_PATH) == RECOUNT_FILE_SHA256, "recount export SHA differs")
    with tempfile.TemporaryDirectory(prefix="goal5842-v12-ampere-authority-") as temporary:
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
        archived = extracted / TRANSACTION_NAME / "independent_recount.json"
        require(
            replay.read_bytes() == archived.read_bytes(),
            "local recount differs from pod recount",
        )
        require(
            archived.read_bytes() == RECOUNT_EXPORT_PATH.read_bytes(),
            "exported recount differs",
        )
        result: dict[str, object] = {
            "schema": "rtdl.goal5842.second_generation_authority.v1",
            "status": (
                "PASS__V12_AMPERE_SECOND_GENERATION_EVIDENCE_VERIFIED__"
                "CROSS_GENERATION_GATE_ELIGIBLE"
            ),
            "source_commit": SOURCE_COMMIT,
            "preregistration": {
                "path": PREREGISTRATION_RELATIVE_PATH,
                "file_sha256": PREREGISTRATION_FILE_SHA256,
                "preregistration_sha256": PREREGISTRATION_SHA256,
                "v12_result_blind": False,
                "prior_generation_rows_pooled": False,
            },
            "archive": {
                "path": str(ARCHIVE_PATH.relative_to(ROOT)),
                "bytes": ARCHIVE_BYTES,
                "sha256": ARCHIVE_SHA256,
                "member_count": ARCHIVE_MEMBER_COUNT,
                "file_count": ARCHIVE_FILE_COUNT,
                "directory_count": ARCHIVE_DIRECTORY_COUNT,
                "uncompressed_regular_file_bytes": ARCHIVE_PAYLOAD_BYTES,
            },
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
                "recount_file_sha256": RECOUNT_FILE_SHA256,
                "recount_sha256": RECOUNT_SHA256,
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
            "baseline_summaries": compact_baseline_summaries(baseline["task_summaries"]),
            "claim_boundary": {
                "generation_evidence_complete": True,
                "goal5842_complete_by_this_authority_alone": False,
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
    require(observed == rebuilt, "stored second-generation authority differs from rebuild")
    return observed


def write_output(path: Path) -> dict[str, object]:
    result = build()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="ascii") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        stream.write("\n")
    return result


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args(argv)
    result = verify_stored() if args.verify_stored else write_output(args.output.resolve())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
