#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


FORBID_TRUE_CLAIMS = (
    "v2_0_release_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
)


def _load(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def _check_forbidden_claims(boundary: dict[str, Any], artifact: str, errors: list[str]) -> None:
    for key in FORBID_TRUE_CLAIMS:
        if boundary.get(key):
            errors.append(f"{artifact}: {key} unexpectedly true")


def _validate_pod_provenance(
    data: dict[str, Any],
    artifact: str,
    expected_source_commit_label: str | None,
    errors: list[str],
) -> None:
    gpu = str(data.get("gpu", ""))
    if "RTX" not in gpu:
        errors.append(f"{artifact}: expected RTX GPU provenance")
    git_commit = str(data.get("git_commit", ""))
    if not git_commit or git_commit == "unknown":
        errors.append(f"{artifact}: expected git_commit provenance")
    source_commit_label = str(data.get("source_commit_label", ""))
    if expected_source_commit_label is None:
        if not source_commit_label:
            errors.append(f"{artifact}: expected source_commit_label provenance")
    elif source_commit_label != expected_source_commit_label:
        errors.append(f"{artifact}: source_commit_label mismatch")


def _validate_fixed_radius(
    base: pathlib.Path,
    expected_source_commit_label: str | None,
    errors: list[str],
    missing: list[str],
) -> None:
    artifact = "docs/reports/goal1903_fixed_radius_batch_pod.json"
    path = base / artifact
    try:
        data = _load(path)
    except FileNotFoundError:
        missing.append(artifact)
        return
    if data.get("status") != "measurement":
        errors.append(f"{artifact}: expected status=measurement")
    _validate_pod_provenance(data, artifact, expected_source_commit_label, errors)
    results = data.get("results")
    if not isinstance(results, list) or not results:
        errors.append(f"{artifact}: expected non-empty results")
        return
    for index, result in enumerate(results):
        _check_forbidden_claims(result.get("claim_boundaries", {}), f"{artifact} results[{index}]", errors)


def _validate_segment(
    base: pathlib.Path,
    count: int,
    expected_source_commit_label: str | None,
    errors: list[str],
    missing: list[str],
) -> None:
    artifact = f"docs/reports/goal1903_segment_polygon_batch_pod_{count}.json"
    path = base / artifact
    try:
        data = _load(path)
    except FileNotFoundError:
        missing.append(artifact)
        return
    if data.get("status") != "pass":
        errors.append(f"{artifact}: expected status=pass")
    _validate_pod_provenance(data, artifact, expected_source_commit_label, errors)
    if not data.get("parity", {}).get("strict_counts_match"):
        errors.append(f"{artifact}: strict_counts_match failed")
    if not data.get("claim_boundary", {}).get("same_contract_timing_row"):
        errors.append(f"{artifact}: same_contract_timing_row missing")
    _check_forbidden_claims(data.get("claim_boundary", {}), artifact, errors)


def _validate_road_hazard(
    base: pathlib.Path,
    count: int,
    expected_source_commit_label: str | None,
    errors: list[str],
    missing: list[str],
) -> None:
    artifact = f"docs/reports/goal1889_road_hazard_prepared_reuse_pod_{count}.json"
    path = base / artifact
    try:
        data = _load(path)
    except FileNotFoundError:
        missing.append(artifact)
        return
    if data.get("status") != "pass":
        errors.append(f"{artifact}: expected status=pass")
    _validate_pod_provenance(data, artifact, expected_source_commit_label, errors)
    if data.get("goal_extension") != "Goal1889":
        errors.append(f"{artifact}: expected goal_extension=Goal1889")
    if not data.get("parity", {}).get("strict_priority_flags_match"):
        errors.append(f"{artifact}: strict_priority_flags_match failed")
    _check_forbidden_claims(data.get("claim_boundary", {}), artifact, errors)
    partners = data.get("partners", {})
    if not partners:
        errors.append(f"{artifact}: expected partner results")
    for partner, result in partners.items():
        prepared = result.get("goal1889_prepared_reuse", {})
        if not prepared.get("prepared_scene_reused"):
            errors.append(f"{artifact}: {partner} prepared_scene_reused missing")
        if not prepared.get("witness_output_columns_reused"):
            errors.append(f"{artifact}: {partner} witness_output_columns_reused missing")


def _validate_summary(base: pathlib.Path, errors: list[str], missing: list[str]) -> str | None:
    artifact = "docs/reports/goal1903_v2_partner_pod_batch_summary.json"
    path = base / artifact
    try:
        data = _load(path)
    except FileNotFoundError:
        missing.append(artifact)
        return None
    source_commit_label = data.get("source_commit_label")
    if not isinstance(source_commit_label, str) or not source_commit_label:
        errors.append(f"{artifact}: expected source_commit_label")
        source_commit_label = None
    for key in ("fixed_radius", "segment_polygon", "road_hazard"):
        if not data.get(key, {}).get("requested"):
            errors.append(f"{artifact}: expected {key}.requested=true")
    _check_forbidden_claims(data.get("claim_boundary", {}), artifact, errors)
    return source_commit_label


def _parse_counts(text: str) -> list[int]:
    return [int(value) for value in text.replace(",", " ").split() if value]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Goal1903 v2 partner pod batch artifacts.")
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--segment-counts", default="512 2048")
    parser.add_argument("--road-hazard-counts", default="512 2048")
    parser.add_argument("--output", default="docs/reports/goal1905_v2_partner_pod_batch_acceptance.json")
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args(argv)

    base = pathlib.Path(args.base_dir)
    errors: list[str] = []
    missing: list[str] = []
    warnings: list[str] = []
    expected_source_commit_label = _validate_summary(base, errors, missing)
    _validate_fixed_radius(base, expected_source_commit_label, errors, missing)
    for count in _parse_counts(args.segment_counts):
        _validate_segment(base, count, expected_source_commit_label, errors, missing)
    for count in _parse_counts(args.road_hazard_counts):
        _validate_road_hazard(base, count, expected_source_commit_label, errors, missing)

    if missing and args.allow_missing:
        remaining_errors = []
        for error in errors:
            is_partial_summary_request_error = (
                "docs/reports/goal1903_v2_partner_pod_batch_summary.json: expected" in error
                and ".requested=true" in error
            )
            if is_partial_summary_request_error:
                warnings.append(error)
            else:
                remaining_errors.append(error)
        errors = remaining_errors

    status = "pass"
    if errors:
        status = "fail"
    elif missing:
        status = "blocked_missing_artifacts"

    payload = {
        "goal": "Goal1905",
        "status": status,
        "missing_artifacts": missing,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
        },
    }
    output = base / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if errors:
        return 1
    if missing and not args.allow_missing:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
