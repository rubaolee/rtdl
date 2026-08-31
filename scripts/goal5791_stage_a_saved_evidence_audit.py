#!/usr/bin/env python3
"""Independent stdlib audit of locally saved Goal5791 Stage-A evidence."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile


EVIDENCE_MEMBERS = {
    "DEPENDENCY_LOCK.json",
    "DEPENDENCY_WHEELHOUSE.tar.gz",
    "EXECUTION_SOURCE.tar.gz",
    "SOURCE_MANIFEST.json",
    "TARGET_EVIDENCE_CONTRACT.json",
    "TARGET_MATERIALIZATION_RESOURCE_ADMISSION.json",
    "TARGET_NATIVE/librtdl_optix.so",
    "TARGET_NATIVE_BUILD_EXECVE_OPENAT_TRACE.log",
    "TARGET_NATIVE_BUILD_PRODUCER_AUDIT.json",
    "TARGET_PROGRAM_INSPECTION.json",
    "TARGET_PTX_PRODUCER_AUDIT.json",
    "TARGET_PTX_PRODUCER_OBSERVATION.json",
    "TARGET_PTX_PRODUCER_OPENAT_TRACE.log",
    "TOOLCHAIN_IDENTITY.json",
    "UPLOAD_STAGING_IDENTITY.json",
    "UPLOAD_STAGING_OPEN_RECEIPT.json",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(value: object) -> str:
    return sha(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode())


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"not one JSON object: {path}")
    return value


def sealed(value: dict[str, object], field: str) -> bool:
    unsigned = dict(value)
    claimed = unsigned.pop(field, None)
    return isinstance(claimed, str) and claimed == digest(unsigned)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    prepared = load(root / "PREPARED.json")
    runtime = load(root / "RUNTIME.json")
    post = load(root / "GOAL5791_POSTPREPARE_PREEXECUTION_AUTHORITY.json")
    authority = load(root / "TARGET_MATERIALIZATION_AUTHORITY.json")
    binding = load(root / "TARGET_MATERIALIZATION_BINDING.json")
    summary = load(root / "TARGET_FUNCTIONAL/SUMMARY.json")

    if not sealed(prepared, "receipt_sha256"):
        raise RuntimeError("PREPARED self-seal drift")
    if not sealed(runtime, "runtime_sha256"):
        raise RuntimeError("RUNTIME self-seal drift")
    if not sealed(post, "authority_sha256"):
        raise RuntimeError("postprepare authority self-seal drift")
    if not sealed(authority, "receipt_sha256"):
        raise RuntimeError("materialization authority self-seal drift")
    if not sealed(binding, "binding_sha256"):
        raise RuntimeError("materialization binding self-seal drift")
    if not sealed(summary, "summary_sha256"):
        raise RuntimeError("functional summary self-seal drift")

    paths = {
        "source": root / "EXECUTION_SOURCE.tar.gz",
        "native": root / "librtdl_optix.so",
        "evidence": root / "TARGET_MATERIALIZATION_EVIDENCE.tar.gz",
        "inspection": root / "TARGET_PROGRAM_INSPECTION.json",
        "producer": root / "TARGET_PTX_PRODUCER_OBSERVATION.json",
        "dependency": root / "DEPENDENCY_LOCK.json",
        "staging_receipt": root / "UPLOAD_STAGING_OPEN_RECEIPT.json",
    }
    expected_hashes = {
        "source": prepared["source_archive_sha256"],
        "native": prepared["native_library_sha256"],
        "evidence": prepared["target_evidence_archive_file_sha256"],
        "inspection": "c2ba693c9dab69806b5f8f8182833ea92148eeaebc66e570bc960d56748690a0",
        "producer": prepared["target_ptx_producer_observation_file_sha256"],
        "dependency": "e8fdc9b1f259e47b51a7883abca04ced8fe96b3540ebdeabd2773f7ccb5613e9",
        "staging_receipt": prepared["upload_staging_identity"][
            "staging_open_receipt_file_sha256"],
    }
    local_hashes = {name: sha(path.read_bytes()) for name, path in paths.items()}
    if local_hashes != expected_hashes:
        raise RuntimeError(f"outer hash cross-bind drift: {local_hashes!r}")

    evidence_bytes = paths["evidence"].read_bytes()
    with tarfile.open(fileobj=io.BytesIO(evidence_bytes), mode="r:gz") as arc:
        members = arc.getmembers()
        names = [m.name for m in members]
        if set(names) != EVIDENCE_MEMBERS or len(names) != len(EVIDENCE_MEMBERS) \
                or any(not m.isfile() for m in members):
            raise RuntimeError("target evidence exact-member set drift")
        embedded = {m.name: arc.extractfile(m).read() for m in members}
    twins = {
        "EXECUTION_SOURCE.tar.gz": paths["source"],
        "TARGET_NATIVE/librtdl_optix.so": paths["native"],
        "TARGET_PROGRAM_INSPECTION.json": paths["inspection"],
        "TARGET_PTX_PRODUCER_OBSERVATION.json": paths["producer"],
        "DEPENDENCY_LOCK.json": paths["dependency"],
        "UPLOAD_STAGING_OPEN_RECEIPT.json": paths["staging_receipt"],
    }
    for name, path in twins.items():
        if embedded[name] != path.read_bytes():
            raise RuntimeError(f"outer/evidence twin drift: {name}")
    if sha(embedded["DEPENDENCY_WHEELHOUSE.tar.gz"]) \
            != sha(args.wheelhouse.read_bytes()):
        raise RuntimeError("preserved wheelhouse drift")
    if not paths["native"].read_bytes().startswith(b"\x7fELF"):
        raise RuntimeError("target native is not ELF")

    lane_hashes: dict[str, str] = {}
    for lifecycle in ("cold", "prepared"):
        for variant in ("fusion_off", "fusion_on"):
            name = f"{lifecycle}__{variant}.json"
            path = root / "TARGET_FUNCTIONAL" / name
            lane = load(path)
            lane_hashes[name] = sha(path.read_bytes())
            expected_events = 7 if variant == "fusion_off" else 2
            if lane.get("status") != "PASS__CREATE_ONLY_TOKEN_SMOKE" \
                    or lane.get("matched") is not True \
                    or lane.get("token_path_only") is not True \
                    or lane.get("formal_worker_count") != 0 \
                    or lane.get("registered_performance_timing_count") != 0 \
                    or lane["segments"][0]["operation_evidence_receipt"][
                        "successful_event_count"] != expected_events:
                raise RuntimeError(f"functional lane drift: {name}")
    if lane_hashes != summary["lane_sha256"]:
        raise RuntimeError("functional summary lane hashes drift")
    for count in (
        prepared["formal_worker_count"],
        prepared["registered_performance_timing_count"],
        post["formal_worker_count"],
        post["registered_performance_timing_count"],
        summary["formal_worker_count"],
        summary["registered_performance_timing_count"],
    ):
        if isinstance(count, bool) or count != 0:
            raise RuntimeError("Stage-A zero worker/timing boundary drift")
    if prepared["formal_execution_authorized"] is not False \
            or prepared["owner_stage_b_formal_authority_created"] is not False:
        raise RuntimeError("Stage-B unexpectedly authorized")

    result = {
        "schema": "rtdl.goal5791.stage_a_saved_evidence_audit.v1",
        "status": "PASS__STAGE_A_SAVED_EVIDENCE_REHASHED_AND_CROSS_BOUND",
        "prepared_file_sha256": sha((root / "PREPARED.json").read_bytes()),
        "prepared_receipt_sha256": prepared["receipt_sha256"],
        "runtime_file_sha256": sha((root / "RUNTIME.json").read_bytes()),
        "runtime_sha256": runtime["runtime_sha256"],
        "postprepare_authority_file_sha256": sha(
            (root / "GOAL5791_POSTPREPARE_PREEXECUTION_AUTHORITY.json").read_bytes()),
        "postprepare_authority_sha256": post["authority_sha256"],
        "source_archive_sha256": local_hashes["source"],
        "native_library_sha256": local_hashes["native"],
        "target_evidence_archive_sha256": local_hashes["evidence"],
        "target_evidence_member_count": len(EVIDENCE_MEMBERS),
        "functional_lane_sha256": lane_hashes,
        "functional_lane_count": 4,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "stage_b_authority_present": False,
    }
    result["audit_sha256"] = digest(result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
