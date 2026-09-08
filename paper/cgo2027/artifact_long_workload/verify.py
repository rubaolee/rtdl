#!/usr/bin/env python3
"""Offline verifier for the anonymous long-workload projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path, PurePosixPath


PROJECTION_SCHEMA = "rtdl.cgo2027.application_projection.v1"
MANIFEST_SCHEMA = "rtdl.cgo2027.application_projection_manifest.v1"
EXPECTED_PROJECTION_SHA256 = (
    "ae2cb7011f407c37b3850aa2a854d177baa4a6494d704eb2ddf68e89f574578c"
)
ARMS = ("old_v4", "new_v4", "pyoptix")
ENDPOINTS = ("complete", "prepared")
UNIT_IDS = (
    "particle_tracking",
    "triangle_counting__com_dblp__rt_2a1",
    "librts__parks__point_contains",
    "librts__parks__range_contains",
    "triangle_counting__cit_patents__rt_2a1__4m",
)
REQUIRED_PUBLIC_FILES = {
    "CLAIM_SCOPE.md",
    "DEPENDENCIES.md",
    "EXPECTED_RESULTS.md",
    "README.md",
    "data/application_projection.json",
    "verify.py",
}
FORBIDDEN_BYTES = (
    b"/" + b"Users/",
    b"/" + b"workspace/",
    b"/" + b"tmp/rtdl",
    b"root" + b"@",
    b"rl" + b"2025",
    b"github" + b".com/",
    b"ssh." + b"runpod.io",
    b"GPU" + b"-",
)
FORBIDDEN_PATTERNS = (
    re.compile(rb"(?i)goal[0-9]+"),
    re.compile(rb"\b[0-9a-f]{40}\b"),
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class VerificationError(ValueError):
    """The package is malformed or differs from its frozen projection."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def strict_json(path: Path) -> object:
    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise VerificationError(f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> object:
        raise VerificationError(f"non-finite JSON value in {path}: {value}")

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=object_pairs,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise VerificationError(f"cannot read strict JSON {path}: {error}") from error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def exact_keys(value: Mapping[str, object], expected: set[str], label: str) -> None:
    require(set(value) == expected, f"{label} keys differ")


def safe_relative(path: str) -> None:
    pure = PurePosixPath(path)
    require(
        path == pure.as_posix() and not pure.is_absolute()
        and ".." not in pure.parts and "." not in pure.parts,
        f"unsafe manifest path: {path}",
    )


def median(values: list[int]) -> int | float:
    require(bool(values) and all(type(item) is int and item > 0 for item in values),
            "timing sample population is invalid")
    return int(statistics.median(values))


def ratio(numerator: int | float, denominator: int | float) -> float:
    require(denominator > 0, "ratio denominator is not positive")
    return numerator / denominator


def verify_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / "manifest.json"
    manifest = strict_json(manifest_path)
    require(isinstance(manifest, dict), "manifest root is not an object")
    exact_keys(manifest, {"schema", "file_count", "files", "payload_bytes",
                          "manifest_sha256"}, "manifest")
    require(manifest["schema"] == MANIFEST_SCHEMA, "manifest schema differs")
    rows = manifest["files"]
    require(isinstance(rows, list), "manifest files are not a list")
    require(manifest["file_count"] == len(REQUIRED_PUBLIC_FILES) == len(rows),
            "manifest file count differs")
    by_path: dict[str, Mapping[str, object]] = {}
    for row in rows:
        require(isinstance(row, dict), "manifest row is not an object")
        exact_keys(row, {"path", "bytes", "sha256"}, "manifest row")
        path = row["path"]
        require(isinstance(path, str), "manifest path is not a string")
        safe_relative(path)
        require(path not in by_path, f"duplicate manifest path: {path}")
        by_path[path] = row
    require(set(by_path) == REQUIRED_PUBLIC_FILES, "manifest member set differs")

    observed_files: set[str] = set()
    payload_bytes = 0
    for path in root.rglob("*"):
        require(not path.is_symlink(), f"artifact contains symlink: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == "manifest.json":
            continue
        observed_files.add(relative)
        payload = path.read_bytes()
        row = by_path.get(relative)
        require(row is not None, f"unexpected artifact file: {relative}")
        require(row["bytes"] == len(payload), f"file size differs: {relative}")
        require(row["sha256"] == sha256_bytes(payload),
                f"file hash differs: {relative}")
        payload_bytes += len(payload)
        for marker in FORBIDDEN_BYTES:
            require(marker not in payload, f"private marker in {relative}")
        for pattern in FORBIDDEN_PATTERNS:
            require(pattern.search(payload) is None,
                    f"private pattern in {relative}")
    require(observed_files == REQUIRED_PUBLIC_FILES, "filesystem member set differs")
    require(manifest["payload_bytes"] == payload_bytes, "payload byte count differs")
    unsealed = dict(manifest)
    seal = unsealed.pop("manifest_sha256")
    require(seal == sha256_bytes(canonical_bytes(unsealed)), "manifest seal differs")
    return manifest


def worker_key(row: Mapping[str, object]) -> tuple[str, str, int, str]:
    return (
        str(row["unit_id"]), str(row["endpoint"]), int(row["block"]),
        str(row["arm"]),
    )


def recount(projection: Mapping[str, object]) -> dict[str, object]:
    exact_keys(projection, {
        "schema", "claim_boundary", "contract", "authority_cross_binding",
        "workers", "expected_cells", "expected_evaluations",
        "independent_recount_projection",
    }, "projection")
    require(projection["schema"] == PROJECTION_SCHEMA, "projection schema differs")
    claim = projection["claim_boundary"]
    require(isinstance(claim, dict), "claim boundary is not an object")
    require(claim == {
        "anonymous_projection_is_raw_custody": False,
        "external_review_complete": False,
        "offline_recount_is_gpu_execution": False,
        "public_or_manuscript_claim_authorized": False,
        "six_historical_mappings_measured": False,
    }, "claim boundary differs")
    contract = projection["contract"]
    require(isinstance(contract, dict), "contract is not an object")
    require(contract["arms"] == list(ARMS), "arm order differs")
    require(contract["endpoints"] == list(ENDPOINTS), "endpoint order differs")
    require(contract["unit_ids"] == list(UNIT_IDS), "unit order differs")
    require(contract["paired_blocks"] == 8, "paired block count differs")
    require(contract["cpu_affinity"] == [8], "registered CPU differs")
    thresholds = contract["engineering_thresholds"]
    require(thresholds == {
        "every_block_new_v4_over_pyoptix_max": 1.35,
        "median_new_v4_over_pyoptix_max": 1.2,
    }, "engineering thresholds differ")

    workers = projection["workers"]
    require(isinstance(workers, list) and len(workers) == 240,
            "worker population differs")
    expected_worker_keys = {
        (unit, endpoint, block, arm)
        for unit in UNIT_IDS for endpoint in ENDPOINTS
        for block in range(8) for arm in ARMS
    }
    observed: dict[tuple[str, str, int, str], Mapping[str, object]] = {}
    process_tokens: set[str] = set()
    timed_samples = 0
    warmups = 0
    retries = discards = timeouts = 0
    for ordinal, row in enumerate(workers):
        require(isinstance(row, dict), "worker row is not an object")
        expected_row_sha = row.get("row_sha256")
        unsealed = dict(row)
        unsealed.pop("row_sha256", None)
        require(expected_row_sha == sha256_bytes(canonical_bytes(unsealed)),
                f"worker row seal differs: {ordinal}")
        require(row.get("ordinal") == ordinal, f"worker ordinal differs: {ordinal}")
        key = worker_key(row)
        require(key not in observed, f"duplicate worker key: {key}")
        observed[key] = row
        require(row.get("status") == "PASS", f"worker failed: {key}")
        samples = row.get("primary_samples_ns")
        require(isinstance(samples, list), f"worker samples missing: {key}")
        require(row.get("primary_median_ns") == median(samples),
                f"worker median differs: {key}")
        require(row.get("retained_sample_count") == len(samples),
                f"worker sample count differs: {key}")
        require(row.get("cpu_affinity_pre") == [8]
                and row.get("cpu_affinity_post") == [8],
                f"worker affinity differs: {key}")
        require(row.get("retry_count") == 0 and row.get("discard_count") == 0,
                f"worker retry/discard differs: {key}")
        require(row.get("timeout") is False, f"worker timeout differs: {key}")
        for name in ("output_sha256", "input_identity_sha256",
                     "raw_worker_sha256", "journal_sha256"):
            require(isinstance(row.get(name), str) and HEX64.fullmatch(row[name]),
                    f"worker hash differs: {key}/{name}")
        input_identity = row.get("input_identity")
        require(isinstance(input_identity, dict),
                f"worker input identity differs: {key}")
        require(row["input_identity_sha256"]
                == sha256_bytes(canonical_bytes(input_identity)),
                f"worker input identity seal differs: {key}")
        token = row.get("process_token")
        require(isinstance(token, str) and HEX64.fullmatch(token),
                f"worker process token differs: {key}")
        require(token not in process_tokens, f"process token reused: {key}")
        process_tokens.add(token)
        timed_samples += len(samples)
        warmups += int(row.get("warmup_count", -1))
        retries += int(row["retry_count"])
        discards += int(row["discard_count"])
        timeouts += int(bool(row["timeout"]))
    require(set(observed) == expected_worker_keys, "worker key population differs")

    cells = []
    for unit in UNIT_IDS:
        for endpoint in ENDPOINTS:
            for block in range(8):
                arms = {arm: observed[(unit, endpoint, block, arm)] for arm in ARMS}
                input_hashes = {row["input_identity_sha256"] for row in arms.values()}
                output_hashes = {row["output_sha256"] for row in arms.values()}
                require(len(input_hashes) == 1, "cell input identity differs")
                require(len(output_hashes) == 1, "cell output identity differs")
                medians = {arm: arms[arm]["primary_median_ns"] for arm in ARMS}
                cells.append({
                    "unit_id": unit,
                    "endpoint": endpoint,
                    "block": block,
                    "valid": True,
                    "reason": None,
                    "medians_ns": medians,
                    "new_v4_over_old_v4": ratio(medians["new_v4"], medians["old_v4"]),
                    "new_v4_over_pyoptix": ratio(medians["new_v4"], medians["pyoptix"]),
                    "old_v4_over_pyoptix": ratio(medians["old_v4"], medians["pyoptix"]),
                })
    require(cells == projection["expected_cells"], "reconstructed cells differ")

    evaluations = []
    for unit in UNIT_IDS:
        for endpoint in ENDPOINTS:
            selected = [row for row in cells
                        if row["unit_id"] == unit and row["endpoint"] == endpoint]
            values = [row["new_v4_over_pyoptix"] for row in selected]
            evaluations.append({
                "unit_id": unit,
                "endpoint": endpoint,
                "registered_block_count": 8,
                "valid_block_count": 8,
                "median_new_v4_over_pyoptix": statistics.median(values),
                "max_new_v4_over_pyoptix": max(values),
                "engineering_target_met": (
                    statistics.median(values) <= 1.2 and max(values) <= 1.35
                ),
            })
    require(evaluations == projection["expected_evaluations"],
            "reconstructed evaluations differ")
    require(all(row["engineering_target_met"] for row in evaluations),
            "an engineering evaluation is adverse")

    independent = projection["independent_recount_projection"]
    require(independent == {
        "all_input_and_output_parity_verified": True,
        "all_journals_reconstructed": True,
        "all_raw_files_hash_verified": True,
        "distinct_process_id_count": 240,
        "engineering_target_met_for_all_ten_rows": True,
        "formal_cell_count": 80,
        "formal_worker_count": 240,
        "project_modules_imported": False,
        "status": "PASS__METHOD_AND_TARGET",
    }, "independent recount projection differs")
    require(timed_samples == 1248, "timed sample count differs")
    require(warmups == 120, "warmup count differs")
    require(retries == discards == timeouts == 0, "failure count differs")
    return {
        "schema": "rtdl.cgo2027.application_projection_recount.v1",
        "status": "PASS__APPLICATION_PROJECTION_RECOUNT",
        "worker_count": len(workers),
        "distinct_process_token_count": len(process_tokens),
        "cell_count": len(cells),
        "evaluation_count": len(evaluations),
        "timed_sample_count": timed_samples,
        "warmup_count": warmups,
        "retry_count": retries,
        "discard_count": discards,
        "timeout_count": timeouts,
        "engineering_target_met_for_all_ten_rows": True,
        "evaluations": evaluations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.artifact_root.resolve(strict=True)
    require(root.is_dir(), "artifact root is not a directory")
    verify_manifest(root)
    projection_path = root / "data/application_projection.json"
    projection_bytes = projection_path.read_bytes()
    require(sha256_bytes(projection_bytes) == EXPECTED_PROJECTION_SHA256,
            "projection byte identity differs")
    projection = strict_json(projection_path)
    require(isinstance(projection, dict), "projection root is not an object")
    result = recount(projection)
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, sort_keys=True))
        raise SystemExit(1)
