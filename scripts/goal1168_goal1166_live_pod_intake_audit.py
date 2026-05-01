#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal1166_live_rtx_pod_2026-04-30"
)
DEFAULT_JSON = ROOT / "docs/reports/goal1168_goal1166_live_pod_intake_audit_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1168_goal1166_live_pod_intake_audit_2026-04-30.md"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any], *keys: str) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def audit(artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    packet = artifact_dir / "goal1166_post_goal1165_next_rtx_pod_packet"
    files = {
        "ann_validation": packet / "ann_candidate_8192_validation.json",
        "ann_timing": packet / "ann_candidate_65536_timing.json",
        "robot_validation": packet / "robot_pose_flags_32768_validation.json",
        "robot_timing": packet / "robot_pose_flags_262144_timing.json",
        "jaccard_validation": packet / "polygon_jaccard_8192_chunk512_validation.json",
        "jaccard_diagnostic": packet / "polygon_jaccard_8192_chunk256_diagnostic.json",
        "intake_report": artifact_dir / "goal1166_live_rtx_pod_intake_2026-04-30.md",
        "source_context": artifact_dir / "goal1166_live_pod_source_context_2026-04-30/source_context.md",
        "runner_log": artifact_dir / "goal1166_live_pod_runner_2026-04-30.log",
    }
    missing = [name for name, path in files.items() if not path.exists()]
    loaded = {
        name: _load_json(path)
        for name, path in files.items()
        if name.endswith(("validation", "timing", "diagnostic")) and path.exists()
    }
    intake_text = files["intake_report"].read_text(encoding="utf-8") if files["intake_report"].exists() else ""
    source_text = files["source_context"].read_text(encoding="utf-8") if files["source_context"].exists() else ""

    source_markers = sorted(
        {
            str(data.get("source_commit"))
            for data in loaded.values()
            if data.get("source_commit")
        }
    )
    local_dirty_source = any("local-dirty" in marker for marker in source_markers)

    checks = {
        "all_expected_files_present": not missing,
        "single_source_marker": len(source_markers) == 1,
        "source_marked_local_dirty": local_dirty_source,
        "intake_records_engineering_accept_claim_block": (
            "ENGINEERING ACCEPT, CLAIM-GRADE BLOCKED" in intake_text
        ),
        "source_context_records_dirty_tree": (
            "not cloned from a clean git checkout" in source_text
            and "Local dirty-path count at copy time:" in source_text
            and "not claim-grade public speedup artifacts" in source_text
        ),
        "ann_validation_matches_oracle": _nested(
            loaded.get("ann_validation", {}),
            "scenario",
            "result",
            "matches_oracle",
        )
        is True,
        "ann_large_timing_validation_skipped": _nested(
            loaded.get("ann_timing", {}),
            "scenario",
            "result",
            "matches_oracle",
        )
        is None,
        "ann_large_timing_query_under_prior_timeout": (
            _nested(
                loaded.get("ann_timing", {}),
                "scenario",
                "timings_sec",
                "optix_query_sec",
                "median_sec",
            )
            or 999999.0
        )
        < 1.0,
        "robot_validation_matches_oracle": loaded.get("robot_validation", {}).get("matches_oracle")
        is True,
        "robot_timing_validation_skipped": loaded.get("robot_timing", {}).get("validated") is False
        and loaded.get("robot_timing", {}).get("matches_oracle") is None,
        "robot_timing_query_under_prior_timeout": (
            _nested(
                loaded.get("robot_timing", {}),
                "phases",
                "prepared_pose_flags_warm_query_sec",
                "median_sec",
            )
            or 999999.0
        )
        < 1.0,
        "jaccard_chunk512_passed": loaded.get("jaccard_validation", {}).get("status") == "pass",
        "jaccard_chunk256_diagnostic_failed": loaded.get("jaccard_diagnostic", {}).get("status")
        == "fail",
    }
    claim_grade_blockers = []
    if local_dirty_source:
        claim_grade_blockers.append("source tree was copied from a dirty local working tree")
    if _nested(loaded.get("ann_timing", {}), "scenario", "result", "matches_oracle") is None:
        claim_grade_blockers.append("ANN large row skipped validation and is timing-only")
    if loaded.get("robot_timing", {}).get("validated") is False:
        claim_grade_blockers.append("robot large row skipped validation and is timing-only")
    if loaded.get("jaccard_diagnostic", {}).get("status") == "fail":
        claim_grade_blockers.append("Jaccard chunk256 remains an expected diagnostic failure")

    valid = all(checks.values())
    return {
        "goal": "Goal1168 Goal1166 live RTX pod intake audit",
        "artifact_dir": str(artifact_dir),
        "valid": valid,
        "engineering_verdict": "accept" if valid else "needs_attention",
        "claim_grade_verdict": "blocked",
        "claim_grade_blockers": claim_grade_blockers,
        "missing": missing,
        "source_markers": source_markers,
        "checks": checks,
        "boundary": (
            "This audit validates the copied Goal1166 live RTX pod artifacts as "
            "engineering evidence only. It does not authorize public speedup "
            "wording or claim-grade release evidence."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1168 Goal1166 Live Pod Intake Audit",
        "",
        f"Artifact dir: `{payload['artifact_dir']}`",
        "",
        f"- valid: `{payload['valid']}`",
        f"- engineering verdict: `{payload['engineering_verdict']}`",
        f"- claim-grade verdict: `{payload['claim_grade_verdict']}`",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for name, result in payload["checks"].items():
        lines.append(f"| `{name}` | `{result}` |")
    lines.extend(["", "## Claim-Grade Blockers", ""])
    for blocker in payload["claim_grade_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit copied Goal1166 live RTX pod artifacts.")
    parser.add_argument("--artifact-dir", default=str(DEFAULT_ARTIFACT_DIR))
    parser.add_argument("--output-json", default=str(DEFAULT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_MD))
    args = parser.parse_args(argv)
    payload = audit(Path(args.artifact_dir))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
