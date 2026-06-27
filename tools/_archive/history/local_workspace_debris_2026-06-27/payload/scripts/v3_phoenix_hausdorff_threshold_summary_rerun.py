#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_distance_app.py"
)
DEFAULT_ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_hausdorff_threshold_summary_repeat5_20260621"
)

STATUS = "hausdorff_threshold_summary_repeat5_evidence_not_promoted"
VERSION = "rtdl.v3.phoenix.hausdorff.threshold_summary.repeat5.v1"


def _run_text(command: list[str], timeout_sec: int = 10) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_sec,
        )
    except Exception as exc:  # pragma: no cover
        return f"unavailable: {exc}"
    return (completed.stdout or completed.stderr).strip()


def environment_probe() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": sys.version,
        "executable": sys.executable,
        "nvidia_smi": _run_text(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ]
        ),
        "repo_root": str(ROOT),
    }


def build_cases(copies: tuple[int, ...], *, threshold: float, repeat: int, warmup: int) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for copy_count in copies:
        for backend in ("embree", "optix"):
            command = [
                sys.executable,
                str(APP),
                "--backend",
                backend,
                "--optix-summary-mode",
                "directed_threshold_prepared",
                "--hausdorff-threshold",
                str(threshold),
                "--copies",
                str(copy_count),
                "--repeat",
                str(repeat),
                "--warmup",
                str(warmup),
            ]
            if backend == "optix":
                command.append("--require-rt-core")
            rows.append(
                {
                    "case_id": f"hausdorff_threshold_summary_{backend}_c{copy_count}_r{repeat}_w{warmup}",
                    "backend": backend,
                    "copies": copy_count,
                    "threshold": threshold,
                    "repeat": repeat,
                    "warmup": warmup,
                    "command": command,
                }
            )
    return tuple(rows)


def _phase_total(phases: dict[str, Any]) -> float | None:
    total = 0.0
    found = False
    for key in (
        "input_construction_sec",
        "scene_prepare_sec",
        "query_fixed_radius_threshold_reached_count_sec",
        "python_postprocess_sec",
        "validation_sec",
    ):
        value = phases.get(key)
        if isinstance(value, (int, float)):
            total += float(value)
            found = True
    return total if found else None


def _ratio(numerator: Any, denominator: Any) -> float | None:
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        return None
    if float(denominator) <= 0.0:
        return None
    return float(numerator) / float(denominator)


def run_case(case: dict[str, Any], artifact_dir: Path, *, timeout_sec: int, dry_run: bool) -> dict[str, Any]:
    case_id = str(case["case_id"])
    stdout_path = artifact_dir / f"{case_id}.stdout.json"
    stderr_path = artifact_dir / f"{case_id}.stderr.txt"
    row: dict[str, Any] = {
        **case,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "full_hausdorff_witness_claim_authorized": False,
    }
    if dry_run:
        return {**row, "status": "dry_run"}

    started = time.perf_counter()
    completed = subprocess.run(
        [str(part) for part in case["command"]],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout_sec,
    )
    wrapper_elapsed_sec = time.perf_counter() - started
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")

    parsed: dict[str, Any] | None = None
    parse_error = None
    try:
        loaded = json.loads(completed.stdout)
        if isinstance(loaded, dict):
            parsed = loaded
        else:
            parse_error = "stdout JSON is not an object"
    except json.JSONDecodeError as exc:
        parse_error = str(exc)

    phases = dict(parsed.get("run_phases", {})) if parsed else {}
    repeat_protocol = dict(parsed.get("repeat_protocol", {})) if parsed else {}
    return {
        **row,
        "status": "ok" if completed.returncode == 0 and parsed is not None else "failed",
        "returncode": completed.returncode,
        "stdout_json_parse_error": parse_error,
        "wrapper_elapsed_sec": wrapper_elapsed_sec,
        "point_count_a": parsed.get("point_count_a") if parsed else None,
        "point_count_b": parsed.get("point_count_b") if parsed else None,
        "within_threshold": parsed.get("within_threshold") if parsed else None,
        "matches_oracle": parsed.get("matches_oracle") if parsed else None,
        "oracle_decision_matches": parsed.get("oracle_decision_matches") if parsed else None,
        "oracle_identity_matches": parsed.get("oracle_identity_matches") if parsed else None,
        "oracle_within_threshold": parsed.get("oracle_within_threshold") if parsed else None,
        "rt_core_accelerated": parsed.get("rt_core_accelerated") if parsed else None,
        "native_continuation_active": parsed.get("native_continuation_active") if parsed else None,
        "native_continuation_backend": parsed.get("native_continuation_backend") if parsed else None,
        "repeat_protocol": repeat_protocol,
        "run_phases": phases,
        "query_sec": phases.get("query_fixed_radius_threshold_reached_count_sec"),
        "query_total_sec": repeat_protocol.get("measured_query_total_sec"),
        "scene_prepare_sec": phases.get("scene_prepare_sec"),
        "phase_total_sec": _phase_total(phases),
    }


def build_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for copies in sorted({int(row["copies"]) for row in rows if row.get("status") in {"ok", "dry_run"}}):
        embree = next((row for row in rows if row.get("copies") == copies and row.get("backend") == "embree"), None)
        optix = next((row for row in rows if row.get("copies") == copies and row.get("backend") == "optix"), None)
        if not embree or not optix:
            continue
        pairs.append(
            {
                "copies": copies,
                "point_count_a": embree.get("point_count_a"),
                "point_count_b": embree.get("point_count_b"),
                "threshold": embree.get("threshold"),
                "repeat": embree.get("repeat"),
                "warmup": embree.get("warmup"),
                "same_decision": embree.get("within_threshold") == optix.get("within_threshold"),
                "same_oracle_decision": embree.get("oracle_within_threshold") == optix.get("oracle_within_threshold"),
                "both_match_oracle": embree.get("matches_oracle") is True and optix.get("matches_oracle") is True,
                "both_oracle_decision_match": (
                    embree.get("oracle_decision_matches") is True and optix.get("oracle_decision_matches") is True
                ),
                "embree_query_sec": embree.get("query_sec"),
                "optix_query_sec": optix.get("query_sec"),
                "query_optix_over_embree": _ratio(embree.get("query_sec"), optix.get("query_sec")),
                "embree_phase_total_sec": embree.get("phase_total_sec"),
                "optix_phase_total_sec": optix.get("phase_total_sec"),
                "phase_total_optix_over_embree": _ratio(embree.get("phase_total_sec"), optix.get("phase_total_sec")),
                "embree_wrapper_elapsed_sec": embree.get("wrapper_elapsed_sec"),
                "optix_wrapper_elapsed_sec": optix.get("wrapper_elapsed_sec"),
                "wrapper_optix_over_embree": _ratio(
                    embree.get("wrapper_elapsed_sec"), optix.get("wrapper_elapsed_sec")
                ),
                "embree_scene_prepare_sec": embree.get("scene_prepare_sec"),
                "optix_scene_prepare_sec": optix.get("scene_prepare_sec"),
                "embree_native_continuation_backend": embree.get("native_continuation_backend"),
                "optix_native_continuation_backend": optix.get("native_continuation_backend"),
                "m7_promotion_authorized": False,
                "row_scoped_public_speedup_claim_authorized": False,
            }
        )
    return pairs


def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload["rows"]
    pairs = payload["pairs"]
    failed_rows = [row["case_id"] for row in rows if row.get("status") not in {"ok", "dry_run"}]
    query_speedups = [
        pair["query_optix_over_embree"]
        for pair in pairs
        if isinstance(pair.get("query_optix_over_embree"), (int, float))
    ]
    phase_speedups = [
        pair["phase_total_optix_over_embree"]
        for pair in pairs
        if isinstance(pair.get("phase_total_optix_over_embree"), (int, float))
    ]
    return {
        "status": STATUS,
        "row_count": len(rows),
        "pair_count": len(pairs),
        "failed_rows": failed_rows,
        "all_pairs_match_oracle": bool(pairs) and all(pair["both_match_oracle"] for pair in pairs),
        "all_pairs_same_decision": bool(pairs) and all(pair["same_decision"] for pair in pairs),
        "all_pairs_repeat_warmup": bool(pairs)
        and all(int(pair["repeat"]) == int(payload["repeat"]) and int(pair["warmup"]) == int(payload["warmup"]) for pair in pairs),
        "strongest_query_optix_speedup_vs_embree": max(query_speedups) if query_speedups else None,
        "weakest_query_optix_speedup_vs_embree": min(query_speedups) if query_speedups else None,
        "strongest_phase_total_optix_speedup_vs_embree": max(phase_speedups) if phase_speedups else None,
        "weakest_phase_total_optix_speedup_vs_embree": min(phase_speedups) if phase_speedups else None,
        "m7_candidate_interpretation": (
            "threshold_summary can be reviewed as row-scoped M7 only if the same-contract "
            "prepared threshold rows pass oracle checks, repeat/warmup evidence is accepted, "
            "and public wording stays threshold-decision-only"
        ),
        "m7_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "full_hausdorff_witness_claim_authorized": False,
    }


def _fmt(value: Any, *, suffix: str = "") -> str:
    if not isinstance(value, (int, float)):
        return ""
    return f"{float(value):.6g}{suffix}"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Phoenix V3 Hausdorff Threshold-Summary Repeat Evidence",
        "",
        f"status: {payload['status']}",
        "",
        "This packet compares Embree and OptiX on the same prepared fixed-radius",
        "threshold-decision contract. It is evidence for `threshold_summary`, not",
        "full exact Hausdorff witness materialization and not release authorization.",
        "",
        "## Summary",
        "",
        f"- All pairs match oracle: `{summary['all_pairs_match_oracle']}`",
        f"- All pairs same decision: `{summary['all_pairs_same_decision']}`",
        f"- All pairs repeat/warmup: `{summary['all_pairs_repeat_warmup']}`",
        f"- Strongest query OptiX/Embree speedup: `{summary['strongest_query_optix_speedup_vs_embree']}`",
        f"- Weakest query OptiX/Embree speedup: `{summary['weakest_query_optix_speedup_vs_embree']}`",
        f"- Strongest phase-total OptiX/Embree speedup: `{summary['strongest_phase_total_optix_speedup_vs_embree']}`",
        f"- Weakest phase-total OptiX/Embree speedup: `{summary['weakest_phase_total_optix_speedup_vs_embree']}`",
        "",
        "## Pairs",
        "",
        "| Copies | Points/side | Repeat | Embree query | OptiX query | Query speedup | Embree phase total | OptiX phase total | Phase speedup | Oracle |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for pair in payload["pairs"]:
        lines.append(
            "| {copies} | {points} | {repeat} | {embree_q} | {optix_q} | {query} | {embree_total} | {optix_total} | {phase} | `{oracle}` |".format(
                copies=pair["copies"],
                points=pair.get("point_count_a"),
                repeat=pair["repeat"],
                embree_q=_fmt(pair.get("embree_query_sec")),
                optix_q=_fmt(pair.get("optix_query_sec")),
                query=_fmt(pair.get("query_optix_over_embree"), suffix="x"),
                embree_total=_fmt(pair.get("embree_phase_total_sec")),
                optix_total=_fmt(pair.get("optix_phase_total_sec")),
                phase=_fmt(pair.get("phase_total_optix_over_embree"), suffix="x"),
                oracle=pair.get("both_match_oracle"),
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Not full exact Hausdorff distance or witness materialization.",
            "- Not X-HD paper reproduction.",
            "- Not broad V3-over-V2 wording.",
            "- Not M7 until external review and Codex consensus.",
            "",
            "## Goal-Level Decision Audit",
            "",
            "Decision: rerun Hausdorff threshold_summary with same-contract repeat evidence before any M7 reconsideration.",
            "",
            "1. Was I foolish?",
            "",
            "   No. This directly addresses the repeat1/no-current-RTX blocker without changing the threshold_summary contract.",
            "",
            "2. If yes, what actions made the decision foolish?",
            "",
            "   Not applicable. The foolish action would be promoting the old repeat1 wall result or switching to full Hausdorff wording.",
            "",
            "3. Was there another path?",
            "",
            "   Yes. The robot collision flag stream could be tuned next, but its blocker is wall/probe-reference dominance, not just missing repeats.",
            "",
            "4. Can I now try a different path that actually solves the problem?",
            "",
            "   Yes. Use this repeat evidence to decide whether threshold_summary deserves external row-scoped review or remains a boundary lesson.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(payload: dict[str, Any], artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (artifact_dir / "summary.md").write_text(render_markdown(payload) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Phoenix V3 Hausdorff threshold_summary repeat evidence.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--copies", type=int, action="append", default=[16_384, 65_536, 262_144])
    parser.add_argument("--threshold", type=float, default=0.4)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=3600)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    copies = tuple(sorted(set(int(value) for value in args.copies)))
    cases = build_cases(copies, threshold=float(args.threshold), repeat=int(args.repeat), warmup=int(args.warmup))
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, case in enumerate(cases, start=1):
        print(f"[hausdorff-threshold-repeat] {index}/{len(cases)} {case['case_id']}", flush=True)
        rows.append(run_case(case, args.artifact_dir, timeout_sec=int(args.timeout_sec), dry_run=bool(args.dry_run)))

    payload: dict[str, Any] = {
        "version": VERSION,
        "status": STATUS,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "artifact_dir": str(args.artifact_dir),
        "copies": list(copies),
        "threshold": float(args.threshold),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "environment": environment_probe() if not args.dry_run else {"repo_root": str(ROOT)},
        "rows": rows,
        "pairs": build_pairs(rows),
        "claim_boundary": {
            "m7_promotion_authorized": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "full_hausdorff_witness_claim_authorized": False,
        },
    }
    payload["summary"] = summarize(payload)
    write_outputs(payload, args.artifact_dir)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.artifact_dir / 'summary.json'}")
    return 0 if not payload["summary"]["failed_rows"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
