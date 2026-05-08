#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_event_hotspot_screening
from examples import rtdl_service_coverage_gaps


REPORT_STEM = "goal1516_v1_5_4_embree_materialization_summary_perf_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _git_head() -> str:
    try:
        import subprocess

        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except Exception:
        return "unknown"
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def _bench(fn: Callable[[], dict[str, object]], repeats: int, warmups: int) -> dict[str, object]:
    for _ in range(warmups):
        fn()
    samples: list[float] = []
    result: dict[str, object] | None = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - start)
    if result is None:
        raise ValueError("repeats must be at least 1")
    return {
        "repeat_count": repeats,
        "warmup_count": warmups,
        "samples_sec": samples,
        "median_sec": statistics.median(samples),
        "min_sec": min(samples),
        "max_sec": max(samples),
        "result": result,
    }


def _event_case(copies: int, repeats: int, warmups: int) -> dict[str, object]:
    row = _bench(
        lambda: rtdl_event_hotspot_screening.run_case("embree", copies=copies),
        repeats,
        warmups,
    )
    summary = _bench(
        lambda: rtdl_event_hotspot_screening.run_case(
            "embree",
            copies=copies,
            embree_summary_mode="count_summary",
        ),
        repeats,
        warmups,
    )
    row_result = row["result"]
    summary_result = summary["result"]
    parity_passed = (
        row_result["neighbor_count_by_event"] == summary_result["neighbor_count_by_event"]
        and row_result["hotspots"] == summary_result["hotspots"]
    )
    return {
        "app": "event_hotspot_screening",
        "copies": copies,
        "event_count": row_result["event_count"],
        "row_mode": {
            "median_sec": row["median_sec"],
            "min_sec": row["min_sec"],
            "max_sec": row["max_sec"],
            "row_count": len(row_result["rows"]),
            "summary_row_count": len(row_result["summary_rows"]),
        },
        "summary_mode": {
            "name": "count_summary",
            "median_sec": summary["median_sec"],
            "min_sec": summary["min_sec"],
            "max_sec": summary["max_sec"],
            "row_count": len(summary_result["rows"]),
            "summary_row_count": len(summary_result["summary_rows"]),
            "native_continuation_active": bool(summary_result["native_continuation_active"]),
        },
        "parity_passed": parity_passed,
        "summary_speedup_vs_rows": (
            float(row["median_sec"]) / float(summary["median_sec"])
            if float(summary["median_sec"]) > 0.0
            else None
        ),
        "materialized_rows_avoided": len(row_result["rows"]) - len(summary_result["rows"]),
    }


def _service_case(copies: int, repeats: int, warmups: int) -> dict[str, object]:
    row = _bench(
        lambda: rtdl_service_coverage_gaps.run_case("embree", copies=copies),
        repeats,
        warmups,
    )
    summary = _bench(
        lambda: rtdl_service_coverage_gaps.run_case(
            "embree",
            copies=copies,
            embree_summary_mode="gap_summary",
        ),
        repeats,
        warmups,
    )
    row_result = row["result"]
    summary_result = summary["result"]
    parity_passed = (
        row_result["uncovered_household_ids"] == summary_result["uncovered_household_ids"]
        and row_result["covered_household_count"] == summary_result["covered_household_count"]
    )
    return {
        "app": "service_coverage_gaps",
        "copies": copies,
        "household_count": row_result["household_count"],
        "clinic_count": row_result["clinic_count"],
        "row_mode": {
            "median_sec": row["median_sec"],
            "min_sec": row["min_sec"],
            "max_sec": row["max_sec"],
            "row_count": len(row_result["rows"]),
            "summary_row_count": len(row_result["coverage_summary_rows"]),
        },
        "summary_mode": {
            "name": "gap_summary",
            "median_sec": summary["median_sec"],
            "min_sec": summary["min_sec"],
            "max_sec": summary["max_sec"],
            "row_count": len(summary_result["rows"]),
            "summary_row_count": len(summary_result["coverage_summary_rows"]),
            "native_continuation_active": bool(summary_result["native_continuation_active"]),
        },
        "parity_passed": parity_passed,
        "summary_speedup_vs_rows": (
            float(row["median_sec"]) / float(summary["median_sec"])
            if float(summary["median_sec"]) > 0.0
            else None
        ),
        "materialized_rows_avoided": len(row_result["rows"]) - len(summary_result["rows"]),
    }


def run_suite(copies: tuple[int, ...], repeats: int, warmups: int) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for copy_count in copies:
        cases.append(_event_case(copy_count, repeats, warmups))
        cases.append(_service_case(copy_count, repeats, warmups))
    parity_passed = all(bool(case["parity_passed"]) for case in cases)
    return {
        "goal": "Goal1516",
        "status": "goal1516_embree_materialization_summary_perf_recorded",
        "valid": parity_passed,
        "git_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "embree_version": rt.embree_version(),
        "embree_threads": rt.embree_thread_config().__dict__,
        "copies": list(copies),
        "repeats": repeats,
        "warmups": warmups,
        "cases": cases,
        "all_parity_passed": parity_passed,
        "timing_scope": (
            "Python app function timing for Embree row mode versus Embree compact "
            "summary mode. This includes Python app orchestration and excludes CLI JSON printing."
        ),
        "claim_flags": {
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rtx_wording_authorized": False,
            "true_zero_copy_authorized": False,
            "stable_collect_k_promotion_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1516 is CPU Embree materialization evidence for selected app modes only. "
            "It does not authorize public speedup wording, broad RTX wording, whole-app "
            "claims, true zero-copy wording, stable COLLECT_K_BOUNDED promotion, or release action."
        ),
    }


def validate_payload(payload: dict[str, object]) -> dict[str, object]:
    if payload.get("goal") != "Goal1516":
        raise ValueError("invalid Goal1516 payload")
    cases = payload.get("cases", [])
    if not isinstance(cases, list) or not cases:
        raise ValueError("Goal1516 requires at least one case")
    if payload.get("all_parity_passed") is not all(bool(case.get("parity_passed")) for case in cases):
        raise ValueError("Goal1516 aggregate parity flag mismatch")
    if payload.get("valid") is not payload.get("all_parity_passed"):
        raise ValueError("Goal1516 valid flag must match parity")
    for case in cases:
        if int(case["summary_mode"]["row_count"]) != 0:
            raise ValueError("Goal1516 summary modes must avoid row materialization")
        if int(case["materialized_rows_avoided"]) < 0:
            raise ValueError("Goal1516 materialized row avoidance cannot be negative")
    for flag, value in payload.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1516 claim flag must remain false: {flag}")
    return payload


def to_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 1516: Embree Materialization Summary Performance",
        "",
        "## Verdict",
        "",
        f"`{payload['status']}`",
        "",
        f"- Valid: `{payload['valid']}`",
        f"- All parity passed: `{payload['all_parity_passed']}`",
        f"- Git commit: `{payload['git_commit']}`",
        f"- Host: `{payload['host']}`",
        f"- Embree version: `{payload['embree_version']}`",
        f"- Repeats: `{payload['repeats']}`",
        f"- Warmups: `{payload['warmups']}`",
        "",
        "## Cases",
        "",
        "| App | Copies | Row median sec | Summary median sec | Summary/row speedup | Row count | Summary rows | Materialized rows avoided | Parity |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for case in payload["cases"]:
        speedup = case["summary_speedup_vs_rows"]
        speedup_text = "n/a" if speedup is None else f"{float(speedup):.3f}x"
        lines.append(
            "| {app} | {copies} | {row_sec:.6f} | {summary_sec:.6f} | {speedup} | {row_count} | {summary_rows} | {avoided} | {parity} |".format(
                app=case["app"],
                copies=case["copies"],
                row_sec=float(case["row_mode"]["median_sec"]),
                summary_sec=float(case["summary_mode"]["median_sec"]),
                speedup=speedup_text,
                row_count=case["row_mode"]["row_count"],
                summary_rows=case["summary_mode"]["summary_row_count"],
                avoided=case["materialized_rows_avoided"],
                parity=case["parity_passed"],
            )
        )
    lines.extend(
        [
            "",
            "## Timing Scope",
            "",
            payload["timing_scope"],
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1516 Embree row-vs-summary materialization benchmark.")
    parser.add_argument("--copies", nargs="+", type=int, default=[256, 1024, 4096])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = validate_payload(run_suite(tuple(args.copies), args.repeats, args.warmups))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "valid": payload["valid"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
