#!/usr/bin/env python3
"""Build deterministic reviewer-visible Goal5753 evidence and a twin."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_bytes(archive: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    info.mode = 0o644
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def build(workspace: Path, author: Path, survey: Path, output: Path) -> dict:
    repo_files = [
        "docs/v4/restricted_python_optix_callbacks_design.md",
        "Paper-reproduction-apps/goal5753-held-out-particle-tracking/README.md",
        "Paper-reproduction-apps/goal5753-held-out-particle-tracking/callback_attempt.py",
        "Paper-reproduction-apps/goal5753-held-out-particle-tracking/physical_contract.py",
        "Paper-reproduction-apps/goal5753-held-out-particle-tracking/independent_oracle.py",
        "scripts/goal5753_build_held_out_universe.py",
        "scripts/goal5753_select_held_out_application.py",
        "scripts/goal5753_held_out_core_seal_audit.py",
        "scripts/goal5753_held_out_particle_tracking_exam.py",
        "scripts/goal5753_held_out_particle_tracking_recount.py",
        "scripts/goal5753_compare_recounts.py",
        "scripts/goal5753_build_held_out_evidence.py",
        "tests/goal5753_selection_protocol_test.py",
        "tests/goal5753_held_out_particle_tracking_test.py",
        "history/internal_docs/goal5753_held_out_candidate_universe_20260811.json",
        "history/internal_docs/goal5753_core_freeze_and_selection_protocol_20260811.json",
        "history/internal_docs/goal5753_core_freeze_and_selection_protocol_20260811.md",
        "history/internal_docs/goal5753_nist_beacon_response_20260811.json",
        "history/internal_docs/goal5753_held_out_selection_20260811.json",
        "history/internal_docs/goal5753_frozen_core_seal_audit_preselection_20260811.json",
        "history/internal_docs/goal5753_frozen_core_seal_audit_postselection_20260811.json",
        "history/internal_docs/goal5753_frozen_core_seal_audit_final_20260811.json",
        "history/internal_docs/goal5753_held_out_particle_tracking_exam_result_20260811.json",
        "history/internal_docs/goal5753_held_out_particle_tracking_recount_windows_20260811.json",
        "history/internal_docs/goal5753_held_out_particle_tracking_recount_wsl_20260811.json",
        "history/internal_docs/goal5753_dual_platform_recount_comparison_20260811.json",
        "history/internal_docs/goal5752_home_partner_lifecycle_v4_20260811/EXECUTION_SOURCE.tar.gz",
        "history/internal_docs/goal5752_home_partner_lifecycle_v4_20260811/librtdl_optix.so",
        "history/internal_docs/goal5752_home_partner_lifecycle_v4_20260811/RESULT.json",
        "history/internal_docs/review_goal5752_owner_returned_external_20260811.md",
        "history/internal_docs/goal5752_owner_returned_external_review_absorption_20260811.json",
        "history/internal_docs/goal5752_postreview_closure_20260811.md",
    ]
    author_files = [
        "LICENSE",
        "README.md",
        "optix/optixQueryKernel.cu",
        "optix/internalTypes.h",
        "optix/OptixTriQuery.cpp",
        "query/ConvexQuery.cu",
    ]
    payloads: list[tuple[str, bytes, str]] = []
    for relative in repo_files:
        path = workspace / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        payloads.append((f"goal5753/{relative}", path.read_bytes(), str(path)))
    for relative in author_files:
        path = author / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        payloads.append((f"goal5753/AUTHOR_SOURCE/{relative}", path.read_bytes(), str(path)))
    if not survey.is_file():
        raise FileNotFoundError(survey)
    payloads.append(("goal5753/SELECTION_SOURCE/survey_source.tar", survey.read_bytes(), str(survey)))
    payloads.sort(key=lambda item: item[0].encode("utf-8"))

    manifest_rows = [
        {"path": name, "sha256": sha(data), "bytes": len(data), "source": source}
        for name, data, source in payloads
    ]
    manifest = {
        "schema": "rtdl.v4.goal5753.held_out_evidence_manifest.v1",
        "payload_count": len(payloads),
        "payload_bytes": sum(len(data) for _name, data, _source in payloads),
        "rows": manifest_rows,
    }
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.USTAR_FORMAT) as archive:
                for name, data, _source in payloads:
                    add_bytes(archive, name, data)
                add_bytes(archive, "goal5753/MANIFEST.json", manifest_bytes)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--author-source", type=Path, required=True)
    parser.add_argument("--survey-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    args = parser.parse_args()
    first = build(
        args.workspace.resolve(), args.author_source.resolve(),
        args.survey_source.resolve(), args.output.resolve(),
    )
    second = build(
        args.workspace.resolve(), args.author_source.resolve(),
        args.survey_source.resolve(), args.twin.resolve(),
    )
    if args.output.read_bytes() != args.twin.read_bytes():
        raise RuntimeError("Goal5753 evidence and twin differ")
    print(json.dumps({
        "archive_sha256": sha(args.output.read_bytes()),
        "payload_count": first["payload_count"],
        "payload_bytes": first["payload_bytes"],
        "twin_byte_identical": True,
        "manifest_equal": first == second,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
