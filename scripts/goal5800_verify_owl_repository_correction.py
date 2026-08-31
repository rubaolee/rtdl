#!/usr/bin/env python3
"""Verify the append-only Goal5800 OWL repository-locator correction.

This verifier deliberately does not rewrite the immutable v5 bundle or result.
It proves that the code executed from v5 is the exact official NVIDIA/OWL
commit, except for the already-declared validation overlay and nine declared
Goal5800 additions, while preserving the original wrong locator as a finding.
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
OWL_REPO = ROOT / ".tmp_goal5797_owl_df7390b1"
BUNDLE = HISTORY / "goal5800_owl_untimed_functional_bundle_v5_20260824.tar.gz"
RESULT_DIR = HISTORY / "goal5800_owl_v5_lx1_untimed_result_20260824"
RERUN_DIR = HISTORY / "goal5800_owl_hostile_recheck_20260824"
OUTPUT = HISTORY / "goal5800_owl_repository_locator_correction_result_20260824.json"

OWL_COMMIT = "df7390b16bce5244b7352ca6d3e320f838297072"
OWL_TREE = "c31d2c7510050fc3d57a4c4e0a4d4d84bc7b03ff"
CORRECT_REPOSITORY = "https://github.com/NVIDIA/OWL"
INCORRECT_REPOSITORY = "https://github.com/owl-project/owl"
ROOT_NAME = "goal5800_owl_source/"
OVERLAY_PATH = "owl/DeviceContext.cpp"
EXPECTED_EXTRAS = {
    "GOAL5800_SOURCE_MANIFEST.json",
    "GOAL5800_STAGE_IDENTITY.json",
    "goal5800_evidence/owl_validation_mode_all.patch",
    "goal5800_tools/goal5800_capture_owl_untimed.py",
    "goal5800_tools/goal5800_remote_build_and_run.py",
    "samples/cmdline/s99-goal5800-owl-residual/CMakeLists.txt",
    "samples/cmdline/s99-goal5800-owl-residual/Goal5800Types.h",
    "samples/cmdline/s99-goal5800-owl-residual/deviceCode.cu",
    "samples/cmdline/s99-goal5800-owl-residual/hostCode.cpp",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(OWL_REPO), *args],
        check=True,
        capture_output=True,
    ).stdout


def tar_members(value: bytes, mode: str) -> dict[str, bytes]:
    rows: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(value), mode=mode) as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile() or member.name in rows:
                raise RuntimeError(f"unsupported or duplicate member: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"could not extract member: {member.name}")
            rows[member.name] = stream.read()
    return rows


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    if not OWL_REPO.is_dir():
        raise FileNotFoundError(OWL_REPO)

    commit = git("rev-parse", "HEAD").decode().strip()
    tree = git("show", "-s", "--format=%T", "HEAD").decode().strip()
    status = git("status", "--porcelain").decode()
    origin = git("remote", "get-url", "origin").decode().strip()
    if commit != OWL_COMMIT or tree != OWL_TREE or status:
        raise RuntimeError("official OWL checkout identity is not exact and clean")
    if origin.rstrip("/").removesuffix(".git") != CORRECT_REPOSITORY:
        raise RuntimeError(f"unexpected OWL origin: {origin}")

    official = tar_members(git("archive", "--format=tar", "HEAD"), "r:")
    bundled_all = tar_members(BUNDLE.read_bytes(), "r:gz")
    bundled = {
        name.removeprefix(ROOT_NAME): value
        for name, value in bundled_all.items()
        if name.startswith(ROOT_NAME)
    }
    if len(bundled) != len(bundled_all):
        raise RuntimeError("bundle member outside the expected root")

    stage_identity = json.loads(bundled["GOAL5800_STAGE_IDENTITY.json"])
    recorded = stage_identity["owl_upstream"]["repository"]
    if recorded != INCORRECT_REPOSITORY:
        raise RuntimeError("immutable v5 no longer preserves the locator defect")
    if stage_identity["owl_upstream"]["commit"] != OWL_COMMIT or \
            stage_identity["owl_upstream"]["tree"] != OWL_TREE:
        raise RuntimeError("immutable v5 commit/tree changed")

    missing = sorted(set(official) - set(bundled))
    mismatches = sorted(
        path for path, value in official.items()
        if path != OVERLAY_PATH and bundled.get(path) != value
    )
    extras = set(bundled) - set(official)
    if missing or mismatches or extras != EXPECTED_EXTRAS:
        raise RuntimeError(
            f"official-source bridge failed: missing={missing}, "
            f"mismatches={mismatches}, extras={sorted(extras)}")

    overlay = stage_identity["validation_overlay"]
    if overlay["changed_upstream_paths"] != [OVERLAY_PATH]:
        raise RuntimeError("validation overlay path set widened")
    if sha256_bytes(official[OVERLAY_PATH]) != \
            overlay["original_device_context_sha256"]:
        raise RuntimeError("official pre-overlay DeviceContext identity mismatch")
    if sha256_bytes(bundled[OVERLAY_PATH]) != \
            overlay["overlaid_device_context_sha256"]:
        raise RuntimeError("bundled post-overlay DeviceContext identity mismatch")

    original_raw = RESULT_DIR / "owl_raw_result.json"
    original_stdout = RESULT_DIR / "owl_runtime_stdout.bin"
    original_stderr = RESULT_DIR / "owl_runtime_stderr.bin"
    rerun_raw = RERUN_DIR / "owl_raw_result.json"
    rerun_stdout = RERUN_DIR / "owl_runtime_stdout.bin"
    rerun_stderr = RERUN_DIR / "owl_runtime_stderr.bin"
    for original_path, rerun_path in (
        (original_raw, rerun_raw),
        (original_stdout, rerun_stdout),
        (original_stderr, rerun_stderr),
    ):
        if original_path.read_bytes() != rerun_path.read_bytes():
            raise RuntimeError(f"fresh rerun differs: {rerun_path.name}")

    raw = json.loads(rerun_raw.read_bytes())
    if raw["status"] != "PASS" or len(raw["behavioral_controls"]) != 5:
        raise RuntimeError("fresh rerun semantic result did not pass")
    if rerun_stdout.read_bytes() != b"GOAL5800_OWL_UNTIMED_FUNCTIONAL_PASS\n" or \
            rerun_stderr.read_bytes():
        raise RuntimeError("fresh rerun stdout/stderr boundary mismatch")

    result = {
        "schema": "rtdl.goal5800.owl_repository_locator_correction.v1",
        "status": "PASS__P1_REPOSITORY_LOCATOR_CORRECTED_APPEND_ONLY__EXECUTION_PRESERVED",
        "finding": {
            "pre_repair_severity": "P1",
            "immutable_v5_recorded_repository": recorded,
            "recorded_repository_is_correct": False,
            "correct_repository": CORRECT_REPOSITORY,
            "v5_rewritten": False,
            "scientific_execution_invalidated": False,
        },
        "official_source_bridge": {
            "origin": origin,
            "commit": commit,
            "tree": tree,
            "official_file_count": len(official),
            "missing_file_count": 0,
            "undeclared_mismatch_count_excluding_overlay": 0,
            "declared_overlay_path": OVERLAY_PATH,
            "declared_extra_path_count": len(EXPECTED_EXTRAS),
            "original_device_context_sha256": sha256_bytes(
                official[OVERLAY_PATH]),
            "overlaid_device_context_sha256": sha256_bytes(
                bundled[OVERLAY_PATH]),
            "bundle_sha256": sha256_file(BUNDLE),
        },
        "fresh_untimed_reexecution": {
            "host": "lx1",
            "executable_sha256": sha256_file(
                RESULT_DIR / "goal5800-owl-residual"),
            "process_exit_code_observed": 0,
            "raw_result_sha256": sha256_file(rerun_raw),
            "stdout_sha256": sha256_file(rerun_stdout),
            "stderr_sha256": sha256_file(rerun_stderr),
            "raw_result_byte_identical_to_original": True,
            "stdout_byte_identical_to_original": True,
            "stderr_byte_identical_to_original": True,
            "registered_performance_timing_count": 0,
        },
        "claim_boundary": {
            "owl_promises_protocol_checking": False,
            "owl_composition_is_credited": True,
            "residual_responsibility_only": True,
            "natural_defect_incidence_claimed": False,
            "modern_rtx_or_rt_core_claimed": False,
            "performance_claimed": False,
            "new_app_generalization_claimed": False,
            "third_party_usability_claimed": False,
        },
    }
    OUTPUT.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"],
        "output_sha256": sha256_file(OUTPUT),
        "official_file_count": len(official),
        "fresh_rerun_raw_sha256": sha256_file(rerun_raw),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
