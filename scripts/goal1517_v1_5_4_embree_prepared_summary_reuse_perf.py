#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts import goal718_embree_prepared_app_batch_perf as goal718


REPORT_STEM = "goal1517_v1_5_4_embree_prepared_summary_reuse_perf_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def run_suite(copies: tuple[int, ...], repeats: int, warmups: int) -> dict[str, object]:
    raw = goal718.run_suite(copies=copies, repeats=repeats, warmups=warmups)
    payload = {
        "goal": "Goal1517",
        "status": "goal1517_embree_prepared_summary_reuse_perf_recorded",
        "valid": bool(raw["valid"]),
        "git_commit": _git_head(),
        "source_goal": raw["goal"],
        "host": raw["host"],
        "platform": raw["platform"],
        "python": raw["python"],
        "embree_version": raw["embree_version"],
        "embree_threads": raw["embree_threads"],
        "copies": raw["copies"],
        "repeats": raw["repeats"],
        "warmups": raw["warmups"],
        "cases": raw["cases"],
        "timing_scope": raw["boundary"],
        "claim_flags": {
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rtx_wording_authorized": False,
            "true_zero_copy_authorized": False,
            "stable_collect_k_promotion_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1517 records CPU Embree prepared-summary reuse timings for outlier "
            "and DBSCAN app summary phases. It does not authorize public speedup "
            "wording, broad RTX wording, whole-app claims, true zero-copy wording, "
            "stable COLLECT_K_BOUNDED promotion, or release action."
        ),
    }
    return validate_payload(payload)


def validate_payload(payload: dict[str, object]) -> dict[str, object]:
    if payload.get("goal") != "Goal1517":
        raise ValueError("invalid Goal1517 payload")
    if payload.get("source_goal") != 718:
        raise ValueError("Goal1517 must wrap Goal718 prepared Embree measurements")
    cases = payload.get("cases", [])
    if not isinstance(cases, list) or not cases:
        raise ValueError("Goal1517 requires at least one case")
    for case in cases:
        for app in ("outlier", "dbscan"):
            app_payload = case[app]
            if float(app_payload["prepare_sec"]) < 0.0:
                raise ValueError("Goal1517 prepare time cannot be negative")
            if int(app_payload["prepared_run_only"]["row_count"]) <= 0:
                raise ValueError("Goal1517 prepared summary must produce per-point summary rows")
            if app_payload["prepared_speedup_vs_one_shot"] is None:
                raise ValueError("Goal1517 prepared speedup ratio must be present")
    for flag, value in payload.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1517 claim flag must remain false: {flag}")
    if "does not authorize public speedup wording" not in str(payload.get("claim_boundary", "")):
        raise ValueError("Goal1517 claim boundary must remain conservative")
    return payload


def to_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 1517: Embree Prepared Summary Reuse Performance",
        "",
        "## Verdict",
        "",
        f"`{payload['status']}`",
        "",
        f"- Valid: `{payload['valid']}`",
        f"- Git commit: `{payload['git_commit']}`",
        f"- Host: `{payload['host']}`",
        f"- Embree version: `{payload['embree_version']}`",
        f"- Repeats: `{payload['repeats']}`",
        f"- Warmups: `{payload['warmups']}`",
        "",
        "## Cases",
        "",
        "| App | Copies | Points | Prepare sec | One-shot median sec | Prepared run median sec | Prepared/one-shot ratio | Summary rows |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in payload["cases"]:
        copies = int(case["copies"])
        for app, point_key in (("outlier", "outlier_point_count"), ("dbscan", "dbscan_point_count")):
            app_payload = case[app]
            ratio = float(app_payload["prepared_speedup_vs_one_shot"])
            lines.append(
                "| {app} | {copies} | {points} | {prepare:.6f} | {one:.6f} | {prepared:.6f} | {ratio:.3f}x | {rows} |".format(
                    app=app,
                    copies=copies,
                    points=int(case[point_key]),
                    prepare=float(app_payload["prepare_sec"]),
                    one=float(app_payload["one_shot"]["median_sec"]),
                    prepared=float(app_payload["prepared_run_only"]["median_sec"]),
                    ratio=ratio,
                    rows=int(app_payload["prepared_run_only"]["row_count"]),
                )
            )
    lines.extend(
        [
            "",
            "## Timing Scope",
            "",
            str(payload["timing_scope"]),
            "",
            "## Claim Boundary",
            "",
            str(payload["claim_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1517 Embree prepared-summary reuse benchmark.")
    parser.add_argument("--copies", nargs="+", type=int, default=[512, 2048, 8192])
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_suite(tuple(args.copies), args.repeats, args.warmups)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "valid": payload["valid"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
