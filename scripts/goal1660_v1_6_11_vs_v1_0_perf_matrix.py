#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from scripts.goal1659_v1_6_11_perf_matrix import build_manifest as build_v1611_manifest


GOAL = "Goal1660"
CURRENT_VERSION = "v1.6.11"
BASELINE_VERSION = "v1.0"
BASELINE_REF = "v1.0"
REPORT_STEM = "goal1660_v1_6_11_vs_v1_0_perf_matrix_2026-05-10"
DEFAULT_JSON = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _ref_exists(ref: str) -> bool:
    return _git("rev-parse", "--verify", ref).returncode == 0


def _path_exists_at_ref(ref: str, path: str) -> bool:
    return _git("cat-file", "-e", f"{ref}:{path}").returncode == 0


def _engine_selector(command: list[str]) -> str | None:
    for flag in ("--backend", "--mode"):
        if flag in command:
            return flag
    return None


def _script_is_optix_specific(command: list[str]) -> bool:
    script = _script_path(command)
    return bool(script and "optix" in Path(script).name.lower())


def _switch_engine(command: list[str], engine: str) -> list[str]:
    converted = list(command)
    flag = _engine_selector(converted)
    if flag is None:
        raise ValueError("command has no --backend/--mode engine selector")
    index = converted.index(flag) + 1
    if index >= len(converted):
        raise ValueError(f"command has {flag} but no engine value")
    converted[index] = engine
    return converted


def _artifact_path(app: str, engine: str, version_slug: str) -> str:
    safe_app = app.replace("-", "_")
    return f"docs/reports/goal1660_{version_slug}_{safe_app}_{engine}.json"


def _with_output_path(command: list[str], app: str, engine: str, version_slug: str) -> list[str]:
    converted = list(command)
    output = _artifact_path(app, engine, version_slug)
    for flag in ("--output-json", "--json-out", "--output"):
        if flag in converted:
            index = converted.index(flag) + 1
            if index < len(converted):
                converted[index] = output
                return converted
    converted.extend(["--output-json", output])
    return converted


def _script_path(command: list[str]) -> str | None:
    for part in command:
        if part.startswith("scripts/") and part.endswith(".py"):
            return part
    return None


def _row(entry: dict[str, Any], engine: str) -> dict[str, Any]:
    pod_command = entry.get("pod_command")
    if not pod_command:
        return {
            "app": entry["app"],
            "engine": engine,
            "status": "excluded",
            "reason": "app has no v1.6.11 Embree/OptiX pod command in Goal1659 matrix",
            "compare_current": False,
            "compare_v1_0": False,
        }
    selector = _engine_selector(pod_command)
    if selector is None:
        if engine == "optix" and _script_is_optix_specific(pod_command):
            current_command = list(pod_command)
            baseline_command = list(pod_command)
            engine_selector_kind = "optix_specific_script"
        else:
            return {
                "app": entry["app"],
                "engine": engine,
                "status": "excluded",
                "reason": (
                    "source command has no --backend/--mode selector; this row would be a "
                    "decorative engine label rather than a real engine comparison"
                ),
                "script_path": _script_path(pod_command),
                "engine_selector": "none",
                "compare_current": False,
                "compare_v1_0": False,
            }
    else:
        current_command = _switch_engine(pod_command, engine)
        baseline_command = _switch_engine(pod_command, engine)
        engine_selector_kind = selector
    current = _with_output_path(
        current_command,
        entry["app"],
        engine,
        "v1_6_11",
    )
    baseline = _with_output_path(
        baseline_command,
        entry["app"],
        engine,
        "v1_0",
    )
    script = _script_path(pod_command)
    script_exists = bool(script and _path_exists_at_ref(BASELINE_REF, script))
    status = "planned" if script_exists else "blocked_v1_0_missing_script"
    shared_primitive_canonical = None
    if entry["app"] == "dbscan_clustering" and script and Path(script).name == "goal757_optix_fixed_radius_prepared_perf.py":
        status = "shared_primitive_alias" if script_exists else status
        shared_primitive_canonical = "outlier_detection"
    return {
        "app": entry["app"],
        "engine": engine,
        "status": status,
        "scope": entry["scope"],
        "purity_status": entry["purity_status"],
        "benchmark_readiness": entry["benchmark_readiness"],
        "v1_6_11_command": current,
        "v1_0_command": baseline,
        "script_path": script,
        "script_exists_in_v1_0": script_exists,
        "engine_selector": engine_selector_kind,
        "shared_primitive_canonical": shared_primitive_canonical,
        "compare_current": status == "planned",
        "compare_v1_0": script_exists and status == "planned",
        "reason": (
            "shares the same Goal757 fixed-radius threshold-count primitive row as "
            "outlier_detection, so it is tracked as app coverage but excluded from "
            "independent cross-version timing"
            if status == "shared_primitive_alias"
            else None
        ),
        "acceptance": [
            "same app",
            "same engine",
            "same command shape",
            "same scale where supported",
            "same artifact schema or explicit schema-drift note",
            "strict parity/status before timing comparison",
        ],
        "claim_boundary": (
            "This row compares v1.6.11 against v1.0 for the same engine. It is "
            "not a public speedup claim unless the final artifacts pass parity, "
            "phase metadata, and 3-AI review."
        ),
    }


def build_manifest() -> dict[str, Any]:
    v1611 = build_v1611_manifest()
    rows = []
    for entry in v1611["entries"]:
        for engine in ("embree", "optix"):
            rows.append(_row(entry, engine))
    planned = [row for row in rows if row["status"] == "planned"]
    blocked = [row for row in rows if row["status"] != "planned"]
    return {
        "goal": GOAL,
        "current_version": CURRENT_VERSION,
        "baseline_version": BASELINE_VERSION,
        "baseline_ref": BASELINE_REF,
        "baseline_ref_exists": _ref_exists(BASELINE_REF),
        "current_head": _git("rev-parse", "HEAD").stdout.strip(),
        "comparison": "v1.6.11_vs_v1.0_by_app_and_engine",
        "engines": ["embree", "optix"],
        "app_count": len(rt.public_apps()),
        "row_count": len(rows),
        "planned_row_count": len(planned),
        "blocked_or_excluded_row_count": len(blocked),
        "requires_pod": True,
        "pod_needed_after_local_preflight": True,
        "release_authorized": False,
        "tag_authorized": False,
        "public_claim_authorized": False,
        "rows": rows,
        "blocked_claims": [
            "whole_app_speedup",
            "broad_rtx_or_gpu_acceleration",
            "true_zero_copy",
            "stable_collect_k_bounded_promotion",
            "python_partner_rtdl",
            "v1_6_11_release_tag_action",
        ],
        "pod_run_contract": {
            "checkout_policy": (
                "Use two clean checkouts or worktrees on the pod: one at tag v1.0 "
                "and one at current main for the v1.6.11 release candidate."
            ),
            "build_policy": (
                "Build Embree and OptiX separately in each checkout from that checkout's source. "
                "Record commit, GPU, driver, CUDA, OptiX SDK, and build command."
            ),
            "comparison_policy": (
                "Compare only rows where both versions complete the same engine command with "
                "accepted parity/status. Missing v1.0 script or schema drift must be reported "
                "as unsupported, not as slower or faster."
            ),
        },
        "boundary": (
            "This manifest prepares the v1.6.11 versus v1.0 performance comparison. "
            "It does not publish v1.6.11, authorize a tag, or authorize public speedup "
            "wording. Final evidence needs a pod because OptiX/NVIDIA RT rows require "
            "real NVIDIA RT hardware."
        ),
    }


def validate_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["current_version"] != CURRENT_VERSION:
        raise ValueError("Goal1660 current version must remain v1.6.11")
    if payload["baseline_version"] != BASELINE_VERSION:
        raise ValueError("Goal1660 baseline version must remain v1.0")
    if payload["baseline_ref_exists"] is not True:
        raise ValueError("Goal1660 requires local v1.0 tag")
    if payload["app_count"] != len(rt.public_apps()):
        raise ValueError("Goal1660 app count mismatch")
    if payload["row_count"] != len(rt.public_apps()) * 2:
        raise ValueError("Goal1660 requires one Embree and one OptiX row per app")
    if payload["planned_row_count"] < 24:
        raise ValueError("Goal1660 should have broad comparable coverage")
    if not payload["blocked_or_excluded_row_count"]:
        raise ValueError("Goal1660 should explicitly classify frozen/unsupported rows")
    for flag in ("release_authorized", "tag_authorized", "public_claim_authorized"):
        if payload[flag] is not False:
            raise ValueError(f"Goal1660 must keep {flag}=False")
    for claim in (
        "whole_app_speedup",
        "broad_rtx_or_gpu_acceleration",
        "true_zero_copy",
        "stable_collect_k_bounded_promotion",
        "python_partner_rtdl",
    ):
        if claim not in payload["blocked_claims"]:
            raise ValueError(f"Goal1660 missing blocked claim: {claim}")
    if "v1_6_11_release_tag_action" not in payload["blocked_claims"]:
        raise ValueError("Goal1660 missing v1.6.11 release/tag blocked claim")
    by_pair = {(row["app"], row["engine"]): row for row in payload["rows"]}
    for app in rt.public_apps():
        for engine in ("embree", "optix"):
            if (app, engine) not in by_pair:
                raise ValueError(f"Goal1660 missing row for {app}/{engine}")
    if by_pair[("apple_rt_demo", "optix")]["status"] != "excluded":
        raise ValueError("Apple RT demo must be excluded from OptiX comparison")
    if by_pair[("hiprt_ray_triangle_hitcount", "optix")]["status"] != "excluded":
        raise ValueError("HIPRT demo must be excluded from OptiX comparison")
    if by_pair[("graph_analytics", "embree")]["status"] != "excluded":
        raise ValueError("Graph Embree row must be excluded unless a real engine selector exists")
    if by_pair[("graph_analytics", "optix")]["status"] != "planned":
        raise ValueError("Graph OptiX row should remain planned through its OptiX-specific script")
    if by_pair[("outlier_detection", "embree")]["status"] != "excluded":
        raise ValueError("Outlier Embree row must be excluded unless a real engine selector exists")
    if by_pair[("outlier_detection", "optix")]["status"] != "planned":
        raise ValueError("Outlier OptiX row should remain planned through its OptiX-specific script")
    if by_pair[("dbscan_clustering", "embree")]["status"] != "excluded":
        raise ValueError("DBSCAN Embree row must be excluded unless a real engine selector exists")
    dbscan_optix = by_pair[("dbscan_clustering", "optix")]
    if dbscan_optix["status"] != "shared_primitive_alias":
        raise ValueError("DBSCAN Goal757 OptiX row must be marked as shared primitive alias")
    if dbscan_optix.get("shared_primitive_canonical") != "outlier_detection":
        raise ValueError("DBSCAN shared primitive alias must point to outlier_detection")
    if dbscan_optix["compare_v1_0"] is not False:
        raise ValueError("DBSCAN shared primitive alias must not be counted as independent timing")
    if "two clean checkouts" not in payload["pod_run_contract"]["checkout_policy"]:
        raise ValueError("Goal1660 checkout policy must require two clean checkouts")
    if "unsupported" not in payload["pod_run_contract"]["comparison_policy"]:
        raise ValueError("Goal1660 must treat missing rows as unsupported")
    return payload


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1660 v1.6.11 vs v1.0 Performance Matrix",
        "",
        "## Verdict",
        "",
        "`v1_6_11_vs_v1_0_perf_matrix_prepared_not_run`",
        "",
        "This prepares a cross-version performance comparison for every public app, with one Embree row and one OptiX/NVIDIA RT row where applicable. It does not run the pod and does not authorize release or public speedup claims.",
        "",
        "## Summary",
        "",
        f"- Current version under test: `{payload['current_version']}`",
        f"- Baseline version: `{payload['baseline_version']}`",
        f"- Public apps: `{payload['app_count']}`",
        f"- Matrix rows: `{payload['row_count']}`",
        f"- Planned comparable rows: `{payload['planned_row_count']}`",
        f"- Blocked/excluded rows: `{payload['blocked_or_excluded_row_count']}`",
        "- Pod required: `True`",
        "- Non-decorative engine rule: rows without a real engine selector are excluded unless the script is explicitly OptiX-specific and the row is the OptiX row.",
        "- Shared primitive rule: DBSCAN's Goal757 OptiX row is tracked for app coverage but excluded from independent timing because it shares the fixed-radius primitive row with outlier detection.",
        "",
        "## Matrix",
        "",
        "| App | Engine | Status | Scope |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['engine']}` | `{row['status']}` | {row.get('scope', row.get('reason', ''))} |"
        )
    lines.extend(
        [
            "",
            "## Pod Contract",
            "",
            payload["pod_run_contract"]["checkout_policy"],
            "",
            payload["pod_run_contract"]["build_policy"],
            "",
            payload["pod_run_contract"]["comparison_policy"],
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit v1.6.11 versus v1.0 performance matrix.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = validate_manifest(build_manifest())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "current": CURRENT_VERSION,
                "baseline": BASELINE_VERSION,
                "planned_rows": payload["planned_row_count"],
                "row_count": payload["row_count"],
                "requires_pod": payload["requires_pod"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
