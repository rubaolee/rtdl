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

from scripts import goal732_polygon_pair_summary_output_perf as goal732
from scripts import goal733_polygon_set_jaccard_scalable_perf as goal733


REPORT_STEM = "goal1518_v1_5_4_embree_polygon_native_assisted_perf_2026-05-08"
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


def run_suite(*, pair_copies: tuple[int, ...], jaccard_copies: tuple[int, ...], repeats: int) -> dict[str, object]:
    pair = goal732.run_benchmark("embree", list(pair_copies), repeats)
    jaccard = goal733.run_benchmark(list(jaccard_copies), repeats)
    payload = {
        "goal": "Goal1518",
        "status": "goal1518_embree_polygon_native_assisted_perf_recorded",
        "valid": True,
        "git_commit": _git_head(),
        "repeats": repeats,
        "polygon_pair_overlap_area_rows": pair,
        "polygon_set_jaccard": jaccard,
        "timing_scope": (
            "Python app run_case plus json.dumps timing for selected polygon app modes. "
            "Embree uses native-assisted candidate discovery; exact polygon/set refinement "
            "and JSON serialization remain in the measured Python app envelope."
        ),
        "claim_flags": {
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_polygon_or_gis_claim_authorized": False,
            "broad_rtx_wording_authorized": False,
            "true_zero_copy_authorized": False,
            "stable_collect_k_promotion_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1518 records CPU Embree native-assisted polygon app timing for exact "
            "measured modes only. It does not authorize public speedup wording, broad "
            "polygon/GIS claims, broad RTX wording, whole-app claims, true zero-copy "
            "wording, stable COLLECT_K_BOUNDED promotion, or release action."
        ),
    }
    return validate_payload(payload)


def validate_payload(payload: dict[str, object]) -> dict[str, object]:
    if payload.get("goal") != "Goal1518":
        raise ValueError("invalid Goal1518 payload")
    pair = payload.get("polygon_pair_overlap_area_rows", {})
    jaccard = payload.get("polygon_set_jaccard", {})
    if pair.get("app") != "polygon_pair_overlap_area_rows":
        raise ValueError("Goal1518 polygon pair payload missing")
    if jaccard.get("app") != "polygon_set_jaccard":
        raise ValueError("Goal1518 Jaccard payload missing")
    if not pair.get("cases") or not jaccard.get("cases"):
        raise ValueError("Goal1518 requires polygon pair and Jaccard cases")
    for case in pair["cases"]:
        summary = case["summary"]
        if summary.get("output_mode") != "summary":
            raise ValueError("Goal1518 polygon pair summary mode missing")
        if summary.get("json_reduction_vs_rows") is None:
            raise ValueError("Goal1518 polygon pair JSON reduction must be present")
    for case in jaccard["cases"]:
        embree = case["embree"]
        if embree.get("backend") != "embree":
            raise ValueError("Goal1518 Jaccard Embree case missing")
        if embree.get("speedup_vs_cpu_python_reference") is None:
            raise ValueError("Goal1518 Jaccard comparison ratio must be present")
    for flag, value in payload.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1518 claim flag must remain false: {flag}")
    if "does not authorize public speedup wording" not in str(payload.get("claim_boundary", "")):
        raise ValueError("Goal1518 claim boundary must remain conservative")
    return payload


def to_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal 1518: Embree Polygon Native-Assisted Performance",
        "",
        "## Verdict",
        "",
        f"`{payload['status']}`",
        "",
        f"- Valid: `{payload['valid']}`",
        f"- Git commit: `{payload['git_commit']}`",
        f"- Repeats: `{payload['repeats']}`",
        "",
        "## Polygon Pair Summary",
        "",
        "| Copies | Rows median sec | Summary median sec | Summary/row ratio | Rows JSON bytes | Summary JSON bytes | JSON reduction |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in payload["polygon_pair_overlap_area_rows"]["cases"]:
        rows = case["rows"]
        summary = case["summary"]
        lines.append(
            "| {copies} | {row_sec:.6f} | {summary_sec:.6f} | {ratio:.3f}x | {row_json} | {summary_json} | {json_ratio:.3f}x |".format(
                copies=case["copies"],
                row_sec=float(rows["median_seconds"]),
                summary_sec=float(summary["median_seconds"]),
                ratio=float(summary["speedup_vs_rows"]),
                row_json=int(rows["json_bytes_median"]),
                summary_json=int(summary["json_bytes_median"]),
                json_ratio=float(summary["json_reduction_vs_rows"]),
            )
        )
    lines.extend(
        [
            "",
            "## Polygon Set Jaccard",
            "",
            "| Copies | CPU median sec | Embree median sec | Embree/CPU ratio | CPU JSON bytes | Embree JSON bytes |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for case in payload["polygon_set_jaccard"]["cases"]:
        cpu = case["cpu_python_reference"]
        embree = case["embree"]
        lines.append(
            "| {copies} | {cpu_sec:.6f} | {embree_sec:.6f} | {ratio:.3f}x | {cpu_json} | {embree_json} |".format(
                copies=case["copies"],
                cpu_sec=float(cpu["median_seconds"]),
                embree_sec=float(embree["median_seconds"]),
                ratio=float(embree["speedup_vs_cpu_python_reference"]),
                cpu_json=int(cpu["json_bytes_median"]),
                embree_json=int(embree["json_bytes_median"]),
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
    parser = argparse.ArgumentParser(description="Goal1518 Embree polygon native-assisted timing wrapper.")
    parser.add_argument("--pair-copies", nargs="+", type=int, default=[256, 1024, 4096])
    parser.add_argument("--jaccard-copies", nargs="+", type=int, default=[64, 256, 1024])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = run_suite(
        pair_copies=tuple(args.pair_copies),
        jaccard_copies=tuple(args.jaccard_copies),
        repeats=args.repeats,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "valid": payload["valid"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
