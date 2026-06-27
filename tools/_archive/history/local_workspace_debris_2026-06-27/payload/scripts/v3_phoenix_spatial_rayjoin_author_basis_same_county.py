from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT / "docs/rebuild/v3/evidence/phoenix_v3_spatial_author_basis_same_county_20260621"
)
AUTHOR_STDOUT = EVIDENCE_DIR / "query_exec_repeat50_stdout.txt"
AUTHOR_STDERR = EVIDENCE_DIR / "query_exec_repeat50_stderr.txt"
AUTHOR_TIME = EVIDENCE_DIR / "query_exec_repeat50_time.txt"
NVIDIA_SMI = EVIDENCE_DIR / "nvidia_smi.txt"
DATA_SHA = EVIDENCE_DIR / "br_county.cdb.sha256"
QUERY_EXEC_SHA = EVIDENCE_DIR / "query_exec.sha256"
QUERY_EXEC_PATH = EVIDENCE_DIR / "query_exec_path.txt"
WORKTREE = EVIDENCE_DIR / "worktree.txt"

EXACT_F64_INTAKE = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.json"
)
EXACT_F64_EVIDENCE = (
    ROOT
    / "docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621"
    / "relation_status_exact_f64_repeat50_sample5.json"
)

OUT_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json"
OUT_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.md"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _parse_timing_ms(log_text: str) -> dict[str, float]:
    timings: dict[str, float] = {}
    for name, value in re.findall(r" - ([^:]+):\s+([0-9.]+) ms", log_text):
        timings[name.strip()] = float(value)
    return timings


def _parse_elapsed_sec(text: str) -> float:
    match = re.search(r"elapsed_sec=([0-9.]+)", text)
    if not match:
        return 0.0
    return float(match.group(1))


def _parse_optix_launch_widths(log_text: str) -> list[int]:
    return [int(value) for value in re.findall(r"optixLaunch, \[w,h,d\] = ([0-9]+),1,1", log_text)]


def _sha_payload(path: Path) -> dict[str, str]:
    text = _read(path).strip()
    parts = text.split(maxsplit=1)
    return {
        "sha256": parts[0] if parts else "",
        "path": parts[1] if len(parts) > 1 else "",
    }


def build_packet() -> dict[str, Any]:
    stdout_text = _read(AUTHOR_STDOUT)
    stderr_text = _read(AUTHOR_STDERR)
    combined_log = stdout_text + "\n" + stderr_text
    timings = _parse_timing_ms(combined_log)
    launch_widths = _parse_optix_launch_widths(combined_log)
    exact_intake = _load_json(EXACT_F64_INTAKE)
    exact_evidence = _load_json(EXACT_F64_EVIDENCE)
    exact_summary = exact_evidence["summary"]
    rtdl_prepared_query_ms = float(exact_summary["prepared_query_sec_median"]) * 1000.0
    rtdl_runner_wall_sec = float(exact_summary["runner_wall_sec_median"])
    author_query_ms = float(timings.get("Query", 0.0))
    author_elapsed_sec = _parse_elapsed_sec(_read(AUTHOR_TIME))
    author_query_speedup_vs_rtdl = (
        rtdl_prepared_query_ms / author_query_ms if author_query_ms > 0.0 else 0.0
    )
    rtdl_runner_wall_vs_author_wrapper = (
        author_elapsed_sec / rtdl_runner_wall_sec if rtdl_runner_wall_sec > 0.0 else 0.0
    )
    query_launch_count = len(launch_widths)
    query_point_count = launch_widths[0] if launch_widths else 0

    checks = {
        "author_artifact_dir_exists": EVIDENCE_DIR.exists(),
        "author_stderr_exists": AUTHOR_STDERR.exists() and AUTHOR_STDERR.stat().st_size > 0,
        "author_stdout_empty_or_exists": AUTHOR_STDOUT.exists(),
        "author_timing_query_ms_present": author_query_ms > 0.0,
        "author_repeat50_warmup5_launch_count": query_launch_count == 55,
        "author_query_point_count_positive": query_point_count > 0,
        "same_public_county_dataset_sha_recorded": DATA_SHA.exists()
        and "data/rayjoin_public_cdb/br_county.cdb" in _read(DATA_SHA),
        "query_exec_sha_recorded": QUERY_EXEC_SHA.exists()
        and "/workspace/RayJoin_fresh/release/bin/query_exec" in _read(QUERY_EXEC_SHA),
        "same_gpu_recorded": "NVIDIA RTX 4000 Ada Generation" in _read(NVIDIA_SMI),
        "rtdl_exact_f64_intake_not_m7": exact_intake.get("m7_promotion_authorized") is False
        and exact_intake.get("release_authorized") is False,
        "rtdl_exact_count_47262": int(exact_intake.get("current_exact_count", -1)) == 47262,
        "author_query_faster_than_rtdl_prepared_query": author_query_speedup_vs_rtdl > 1.0,
        "claim_flags_false": True,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]

    return {
        "tool": "v3_phoenix_spatial_rayjoin_author_basis_same_county",
        "status": "spatial_rayjoin_same_county_author_timing_present_not_m7",
        "generic_capability": "point_location_topology_stream",
        "dataset": "data/rayjoin_public_cdb/br_county.cdb",
        "same_dataset_author_timing_basis_present": True,
        "author_result_count_printed": False,
        "author_result_count_parity_verified": False,
        "m7_promotion_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "author_run": {
            "query_exec_path": _read(QUERY_EXEC_PATH).strip(),
            "worktree": _read(WORKTREE).strip(),
            "gpu": _read(NVIDIA_SMI).strip(),
            "command_contract": "query_exec -poly1 br_county.cdb -poly2 br_county.cdb -mode=rt -query=pip -warmup=5 -repeat=50 -check=false",
            "warmup": 5,
            "repeat": 50,
            "query_point_count_from_optix_launch_width": query_point_count,
            "query_launch_count": query_launch_count,
            "timing_ms": timings,
            "query_ms": author_query_ms,
            "wrapper_elapsed_sec": author_elapsed_sec,
            "stdout_file": _rel(AUTHOR_STDOUT),
            "stderr_file": _rel(AUTHOR_STDERR),
            "time_file": _rel(AUTHOR_TIME),
            "data_sha256": _sha_payload(DATA_SHA),
            "query_exec_sha256": _sha_payload(QUERY_EXEC_SHA),
        },
        "rtdl_exact_f64_reference": {
            "intake_packet": _rel(EXACT_F64_INTAKE),
            "evidence_packet": _rel(EXACT_F64_EVIDENCE),
            "count_mode": exact_intake["count_mode"],
            "exact_count": exact_intake["current_exact_count"],
            "prepared_query_ms_median": rtdl_prepared_query_ms,
            "runner_wall_sec_median": rtdl_runner_wall_sec,
            "query_repeat": int(exact_summary["m3_phase_sec_medians"].get("prepared_query_repeat", 50))
            if "prepared_query_repeat" in exact_summary.get("m3_phase_sec_medians", {})
            else 50,
            "query_stream_residency": exact_summary["query_stream_residency"],
        },
        "comparison": {
            "rayjoin_author_query_ms": author_query_ms,
            "rtdl_exact_f64_prepared_query_ms": rtdl_prepared_query_ms,
            "rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query": author_query_speedup_vs_rtdl,
            "rtdl_exact_f64_prepared_query_relative_to_rayjoin_author_query": (
                author_query_ms / rtdl_prepared_query_ms if rtdl_prepared_query_ms > 0.0 else 0.0
            ),
            "rtdl_runner_wall_speedup_vs_rayjoin_author_wrapper": rtdl_runner_wall_vs_author_wrapper,
            "wrapper_comparison_authorized_for_public_claim": False,
            "query_timer_basis_note": (
                "RayJoin author Query is the internal query_exec timer. RTDL exact-f64 prepared query is "
                "the RTDL M3 prepared-query median for the reusable device scalar-count executor. "
                "The timers are useful author-basis evidence, but they are not a whole-app or paper "
                "comparison and RayJoin does not print the result count in this run."
            ),
        },
        "remaining_blockers_before_m7": [
            "external_ai_review_missing",
            "codex_consensus_response_missing_after_external_review",
            "rayjoin_author_result_count_not_printed_or_public_scope_review_missing",
            "rayjoin_author_query_faster_than_rtdl_exact_f64_query",
            "route_name_semantically_stale_relation_status_corrected",
            "public_wording_review_missing",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Record same-dataset RayJoin author timing for the Spatial exact-f64 candidate without promoting it.",
            "was_i_foolish": (
                "No. The author run closes the missing-timing fact but shows RayJoin author Query is faster "
                "than the current RTDL exact-f64 prepared-query path."
            ),
            "foolish_actions": (
                "The foolish action would be to claim RTDL beats RayJoin, ignore that RayJoin does not print "
                "a result count here, or compare wrapper elapsed times as public speedup evidence."
            ),
            "other_path": (
                "I could have left the blocker as missing. That would be stale now that the POD author run exists."
            ),
            "different_path_now": (
                "Use this packet to update the review gate from missing author timing to author timing present "
                "but not-M7, then continue only through external review, wording review, or generic engine work."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    author = packet["author_run"]
    rtdl = packet["rtdl_exact_f64_reference"]
    comparison = packet["comparison"]
    audit = packet["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Spatial Same-County Author Timing Basis",
        "",
        f"Status: `{packet['status']}`",
        "",
        "This packet records a same-dataset RayJoin author timing basis for the",
        "current Spatial exact-f64 candidate. It is not an M7 promotion.",
        "",
        "## Verdict",
        "",
        "- Same-dataset author timing basis present: `true`",
        "- Author result count printed: `false`",
        "- Author result count parity verified: `false`",
        "- M7 promotion authorized: `false`",
        "- RTDL-beats-RayJoin claim authorized: `false`",
        "",
        "## Author Run",
        "",
        f"- Dataset: `{packet['dataset']}` as both `-poly1` and `-poly2`",
        f"- Query exec: `{author['query_exec_path']}`",
        f"- GPU: `{author['gpu']}`",
        f"- Warmup/repeat: `{author['warmup']}` / `{author['repeat']}`",
        f"- Query point count from `optixLaunch` width: `{author['query_point_count_from_optix_launch_width']}`",
        f"- Query launch count: `{author['query_launch_count']}`",
        f"- RayJoin author Query timer: `{author['query_ms']:.6f} ms`",
        f"- RayJoin wrapper elapsed: `{author['wrapper_elapsed_sec']:.6f} s`",
        "",
        "## RTDL Exact-F64 Reference",
        "",
        f"- Intake packet: `{rtdl['intake_packet']}`",
        f"- Count mode: `{rtdl['count_mode']}`",
        f"- Exact count: `{rtdl['exact_count']}`",
        f"- RTDL prepared-query median: `{rtdl['prepared_query_ms_median']:.6f} ms`",
        f"- RTDL runner-wall median: `{rtdl['runner_wall_sec_median']:.6f} s`",
        f"- Query-stream residency: `{rtdl['query_stream_residency']}`",
        "",
        "## Comparison",
        "",
        f"- RayJoin author Query speedup vs RTDL exact-f64 prepared query: `{comparison['rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query']:.3f}x`",
        f"- RTDL exact-f64 prepared query relative to RayJoin author Query: `{comparison['rtdl_exact_f64_prepared_query_relative_to_rayjoin_author_query']:.3f}x`",
        f"- RTDL runner-wall vs RayJoin wrapper ratio, not public-claim-authorized: `{comparison['rtdl_runner_wall_speedup_vs_rayjoin_author_wrapper']:.3f}x`",
        "",
        comparison["query_timer_basis_note"],
        "",
        "## Remaining Blockers Before M7",
        "",
    ]
    for blocker in packet["remaining_blockers_before_m7"]:
        lines.append(f"- `{blocker}`")
    lines.extend(["", "## Checks", ""])
    for name, passed in packet["checks"].items():
        lines.append(f"- `{name}`: `{str(bool(passed)).lower()}`")
    lines.extend(
        [
            "",
            f"Failed checks: `{packet['failed_checks']}`",
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            f"1. Was I foolish? {audit['was_i_foolish']}",
            f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
            f"3. Was there another path? {audit['other_path']}",
            f"4. Can I now try a different path? {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(packet), encoding="utf-8")
    print(json.dumps({"status": packet["status"], "failed_checks": packet["failed_checks"]}, indent=2))


if __name__ == "__main__":
    main()
