#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _median(case: dict[str, Any], phase: str) -> float:
    return float(case.get("phase_stats", {}).get(phase, {}).get("median_sec", 0.0))


def _ratio(baseline: float, candidate: float) -> float | None:
    if baseline <= 0.0 or candidate <= 0.0:
        return None
    return baseline / candidate


def _case_key(case: dict[str, Any]) -> tuple[str, str]:
    return str(case["app"]), str(case["path"])


def _load_profile(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_profile(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_top = ("goal", "backend", "mode", "cases", "classification_change", "rtx_speedup_claim")
    for key in required_top:
        if key not in profile:
            errors.append(f"missing top-level field `{key}`")
    cases = profile.get("cases", [])
    if not isinstance(cases, list):
        errors.append("`cases` must be a list")
        return errors
    required_cases = {
        ("outlier_detection", "rows"),
        ("outlier_detection", "rt_count_threshold"),
        ("dbscan_clustering", "rows"),
        ("dbscan_clustering", "rt_core_flags"),
    }
    observed_cases = {_case_key(case) for case in cases if isinstance(case, dict) and "app" in case and "path" in case}
    missing = sorted(required_cases - observed_cases)
    for app, path in missing:
        errors.append(f"missing case `{app}/{path}`")
    for case in cases:
        if not isinstance(case, dict):
            errors.append("case entry is not an object")
            continue
        output = case.get("last_output", {})
        if not bool(output.get("matches_oracle", False)):
            errors.append(f"case `{case.get('app')}/{case.get('path')}` did not preserve oracle parity")
    return errors


def _format_float(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def _comparison_rows(profile: dict[str, Any]) -> list[dict[str, Any]]:
    cases = {_case_key(case): case for case in profile["cases"]}
    pairs = (
        ("outlier_detection", "rows", "rt_count_threshold"),
        ("dbscan_clustering", "rows", "rt_core_flags"),
    )
    rows: list[dict[str, Any]] = []
    for app, row_path, summary_path in pairs:
        row_case = cases[(app, row_path)]
        summary_case = cases[(app, summary_path)]
        row_total = _median(row_case, "total")
        summary_total = _median(summary_case, "total")
        row_backend = _median(row_case, "backend_execute_or_materialize_rows")
        summary_backend = _median(summary_case, "backend_execute_or_materialize_rows")
        rows.append(
            {
                "app": app,
                "row_path": row_path,
                "summary_path": summary_path,
                "row_total_sec": row_total,
                "summary_total_sec": summary_total,
                "total_ratio": _ratio(row_total, summary_total),
                "row_backend_sec": row_backend,
                "summary_backend_sec": summary_backend,
                "backend_ratio": _ratio(row_backend, summary_backend),
                "row_output": row_case["last_output"],
                "summary_output": summary_case["last_output"],
            }
        )
    return rows


def render_report(profile_path: Path, *, environment_path: Path | None = None) -> str:
    profile = _load_profile(profile_path)
    errors = _validate_profile(profile)
    comparisons = [] if errors else _comparison_rows(profile)
    optix_mode = profile.get("mode") == "optix" and profile.get("backend") == "optix"
    all_oracle = not errors
    eligible_for_rtx_claim_review = bool(optix_mode and all_oracle and not profile.get("classification_change", True))

    lines: list[str] = [
        "# Goal699 RTX Fixed-Radius Profile Report",
        "",
        f"Profile JSON: `{profile_path}`",
    ]
    if environment_path is not None:
        lines.append(f"Environment file: `{environment_path}`")
    lines.extend(
        [
            "",
            "## Verdict Inputs",
            "",
            f"- mode: `{profile.get('mode', 'missing')}`",
            f"- backend: `{profile.get('backend', 'missing')}`",
            f"- copies: `{profile.get('copies', 'missing')}`",
            f"- iterations: `{profile.get('iterations', 'missing')}`",
            f"- classification_change: `{str(profile.get('classification_change', 'missing')).lower()}`",
            f"- rtx_speedup_claim_in_input: `{str(profile.get('rtx_speedup_claim', 'missing')).lower()}`",
            f"- oracle_parity: `{str(all_oracle).lower()}`",
            f"- eligible_for_rtx_claim_review: `{str(eligible_for_rtx_claim_review).lower()}`",
            "",
            "## Comparison",
            "",
            "| app | row path total median (s) | summary path total median (s) | total ratio row/summary | row backend median (s) | summary backend median (s) | backend ratio row/summary |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in comparisons:
        lines.append(
            "| {app} | {row_total} | {summary_total} | {total_ratio} | {row_backend} | {summary_backend} | {backend_ratio} |".format(
                app=row["app"],
                row_total=_format_float(row["row_total_sec"], 6),
                summary_total=_format_float(row["summary_total_sec"], 6),
                total_ratio=_format_float(row["total_ratio"]),
                row_backend=_format_float(row["row_backend_sec"], 6),
                summary_backend=_format_float(row["summary_backend_sec"], 6),
                backend_ratio=_format_float(row["backend_ratio"]),
            )
        )
    if errors:
        lines.extend(["", "## Validation Errors", ""])
        lines.extend(f"- {error}" for error in errors)

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "This report is a structured interpretation of Goal697 profiler JSON. It does not by itself upgrade RTDL's public OptiX app classification.",
            "",
            "A speedup statement is review-eligible only when `mode=optix`, `backend=optix`, every case preserves oracle parity, and the environment file records RTX-class hardware. Dry-run or GTX 1070 data must remain correctness/instrumentation evidence, not RT-core performance evidence.",
            "",
            "The current native fixed-radius ABI reports whole-call timing. Packing, BVH build, OptiX launch, and copy-back are still not separately attributed.",
        ]
    )
    if environment_path is not None and environment_path.exists():
        env_text = environment_path.read_text(encoding="utf-8").strip()
        lines.extend(["", "## Environment Excerpt", "", "```text", env_text[:4000], "```"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render Goal697/Goal698 RTX profile JSON into a bounded markdown report.")
    parser.add_argument("--profile-json", type=Path, required=True)
    parser.add_argument("--environment", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    report = render_report(args.profile_json, environment_path=args.environment)
    args.output.write_text(report, encoding="utf-8")
    print(str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
