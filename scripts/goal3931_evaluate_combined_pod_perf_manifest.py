from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CLAIM_FIELDS = (
    "release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "true_zero_copy_claim_authorized",
    "automatic_partner_selection_authorized",
    "app_specific_native_engine_logic_allowed",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a Goal3927 combined pod perf manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    summary = evaluate_manifest(args.manifest)
    text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if summary["status"] in {"accept", "accept_with_boundary"} else 1


def evaluate_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    claim_boundary = manifest.get("claim_boundary", {})
    for field in CLAIM_FIELDS:
        if claim_boundary.get(field) is not False:
            errors.append(f"claim boundary does not keep {field}=False")

    rayjoin = _evaluate_rayjoin(manifest.get("rayjoin", {}), warnings)
    rtdbscan = _evaluate_rtdbscan(tuple(manifest.get("rtdbscan", ())), errors, warnings)
    if manifest.get("status") not in {"pass", "dry_run"}:
        errors.append(f"unexpected manifest status: {manifest.get('status')}")

    status = "reject" if errors else "accept_with_boundary"
    return {
        "goal": "Goal3931",
        "source_manifest": str(path),
        "source_commit": manifest.get("source_commit"),
        "source_commit_label": manifest.get("source_commit_label"),
        "status": status,
        "errors": tuple(errors),
        "warnings": tuple(warnings),
        "rayjoin": rayjoin,
        "rtdbscan": rtdbscan,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "route_promotion_authorized": False,
        },
    }


def _evaluate_rayjoin(rayjoin: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    cases = tuple(rayjoin.get("cases", ()))
    missing_nested = tuple(
        case.get("workload", "<unknown>")
        for case in cases
        if not case.get("subprobe_wrapper_phase_timing_sec")
    )
    missing_reuse = tuple(
        case.get("workload", "<unknown>")
        for case in cases
        if case.get("loaded_case_reuse_enabled") is not True
    )
    if missing_nested:
        warnings.append(f"RayJoin cases missing nested subprobe timing: {missing_nested}")
    if missing_reuse:
        warnings.append(f"RayJoin cases without loaded-case reuse flag true: {missing_reuse}")
    return {
        "gpu": rayjoin.get("gpu"),
        "case_count": len(cases),
        "wrapper_phase_timing_present": bool(rayjoin.get("wrapper_phase_timing_sec")),
        "all_cases_have_nested_subprobe_timing": not missing_nested,
        "all_cases_use_loaded_case_reuse": not missing_reuse,
        "missing_nested_subprobe_timing": missing_nested,
        "missing_loaded_case_reuse": missing_reuse,
    }


def _evaluate_rtdbscan(
    rows: tuple[dict[str, Any], ...],
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    by_blocked = {bool(row.get("blocked")): row for row in rows if row.get("elapsed_sec") is not None}
    if False not in by_blocked or True not in by_blocked:
        errors.append("RTDBSCAN manifest must include both blocked and unblocked rows")
        return {
            "row_count": len(rows),
            "has_unblocked": False in by_blocked,
            "has_blocked": True in by_blocked,
            "blocked_vs_unblocked_speedup": None,
            "recommendation": "needs_complete_manifest",
        }

    unblocked = by_blocked[False]
    blocked = by_blocked[True]
    unblocked_elapsed = float(unblocked["elapsed_sec"])
    blocked_elapsed = float(blocked["elapsed_sec"])
    if unblocked_elapsed <= 0 or blocked_elapsed <= 0:
        errors.append("RTDBSCAN elapsed_sec values must be positive")
        speedup = None
    else:
        speedup = unblocked_elapsed / blocked_elapsed
    for row in rows:
        if row.get("partner") != "numba":
            errors.append(f"RTDBSCAN row does not use numba partner: {row.get('mode')}")
        boundary = row.get("claim_boundary", {})
        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            if boundary.get(field) is not False:
                errors.append(f"RTDBSCAN row {row.get('mode')} authorizes {field}")
    if speedup is None:
        recommendation = "needs_valid_timing"
    elif speedup >= 1.05:
        recommendation = "blocked_candidate_faster_review_before_promotion"
    elif speedup >= 0.95:
        recommendation = "blocked_candidate_near_parity_no_default_promotion"
    else:
        recommendation = "blocked_candidate_slower_keep_unblocked_default"
    if speedup is not None and speedup < 1.05:
        warnings.append("RTDBSCAN blocked mode did not clear the 1.05x review threshold")
    return {
        "row_count": len(rows),
        "has_unblocked": True,
        "has_blocked": True,
        "unblocked_elapsed_sec": unblocked_elapsed,
        "blocked_elapsed_sec": blocked_elapsed,
        "blocked_vs_unblocked_speedup": speedup,
        "review_threshold_speedup": 1.05,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    raise SystemExit(main())
