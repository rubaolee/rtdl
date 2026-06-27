#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.json"
)
SUMMARY = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_npz_cubin_repeat50_1048576_20260621"
    / "repeat50_compare"
    / "summary.json"
)
OPTIX_PAYLOAD = SUMMARY.parent / "rtnn_full_batch_float32_optix.json"
CUPY_PAYLOAD = SUMMARY.parent / "rtnn_full_batch_float32_cupy_grid.json"
SOURCE_MANIFEST = SUMMARY.parent.parent / "source_manifest.sha256"
CALL_FOR_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_rtnn_prepared_repeat50_amortization_review_2026-06-21.md"
)
CLAUDE_REVIEW_STREAM = CLAUDE_REVIEW.with_suffix(".stream.jsonl")
CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_rtnn_prepared_repeat50_amortization_2ai_consensus_2026-06-21.md"
)
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")

ROW_ID = "rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_hashes(text: str) -> list[str]:
    hashes = []
    for line in text.splitlines():
        parts = line.strip().split()
        if parts and len(parts[0]) == 64:
            hashes.append(parts[0])
    return hashes


def _approved_wording(evidence: dict[str, Any], summary: dict[str, Any]) -> str:
    comparisons = evidence["comparisons"]
    parity = evidence["parity"]
    params = evidence["parameters"]
    gpu = summary["environment"]["hardware_gate"]["gpus"][0]["name"]
    return (
        f"On a single {gpu} GPU, RTDL OptiX ranked-summary (float32 internal precision, "
        f"CUBIN cache) achieved {comparisons['hot_query_speedup']:.3f}x hot-query speedup, "
        f"{comparisons['cold_plus_query_speedup']:.3f}x cold-plus-query speedup, and "
        f"{comparisons['runner_wall_speedup']:.3f}x runner-wall speedup over a CuPy "
        "uniform-grid CUDA-core reference using float64 coordinate columns, at "
        f"{params['point_count']:,} points with k={params['k_max']} and radius={params['radius']}, "
        "across 50 prepared repeated queries on the same search structure. Parity was "
        "confirmed by matching integer signatures and "
        f"{parity['sum_distance_relative_error']:.3e} sum-distance relative error. "
        "Source provenance is verified by source_manifest.sha256; no git head was available "
        "from the run environment. This is a scoped prepared repeated-session amortization "
        "result only."
    )


def build_packet() -> dict[str, Any]:
    evidence = _load_json(EVIDENCE)
    summary = _load_json(SUMMARY)
    optix = _load_json(OPTIX_PAYLOAD)
    cupy = _load_json(CUPY_PAYLOAD)
    manifest_text = _read(SOURCE_MANIFEST)
    claude_text = _read(CLAUDE_REVIEW)
    consensus_text = _read(CODEX_CONSENSUS)
    consensus_flat = " ".join(consensus_text.split())
    call_text = _read(CALL_FOR_REVIEW)
    manifest_hashes = _manifest_hashes(manifest_text)

    comparisons = evidence["comparisons"]
    parity = evidence["parity"]
    params = evidence["parameters"]
    summary_comparisons = summary["comparisons"]
    optix_contract = optix["contract"]
    cupy_contract = cupy["contract"]
    material_floor = float(evidence["material_speedup_floor"])

    claude_review_ok = bool(
        CLAUDE_REVIEW.exists()
        and "APPROVE\\_WITH\\_CONDITIONS" in claude_text
        and "Cold-plus-query (1.315x) is below the 2.0x material floor" in claude_text
        and "float32 OptiX ranked-summary vs float64-coordinate CuPy grid" in claude_text
        and "source_manifest.sha256" in claude_text
        and "CuPy uniform-grid CUDA-core" in claude_text
        and "Promote the exact row" in claude_text
        and ROW_ID in claude_text
    )
    codex_consensus_ok = bool(
        CODEX_CONSENSUS.exists()
        and "claude_codex_consensus_complete_approve_one_row_scoped_m7" in consensus_flat
        and "across 50 prepared repeated queries on the same search structure" in consensus_flat
        and "7.889x" in consensus_flat
        and "1.315x" in consensus_flat
        and "3.761x" in consensus_flat
        and "float32 internal precision" in consensus_flat
        and "float64 coordinate columns" in consensus_flat
        and "source_manifest.sha256" in consensus_flat
        and ROW_ID in consensus_flat
        and "release_authorized: false" in consensus_flat
        and "broad_v3_faster_than_v2_claim_authorized: false" in consensus_flat
    )
    approved_wording = _approved_wording(evidence, summary)

    checks = {
        "evidence_exists": EVIDENCE.exists(),
        "evidence_status_pending_review": evidence.get("status")
        == "rtnn_prepared_repeat50_amortization_m7_candidate_pending_external_review_not_release",
        "candidate_row_id_exact": evidence.get("candidate_row_ids") == [ROW_ID],
        "release_flags_false": (
            evidence.get("release_authorized") is False
            and evidence.get("public_speedup_claim_authorized") is False
            and evidence.get("broad_v3_faster_than_v2_claim_authorized") is False
            and evidence.get("whole_app_speedup_claim_authorized") is False
        ),
        "parameters_repeat50_serious_scale": (
            params.get("repeat") == 50
            and params.get("point_count") == 1_048_576
            and params.get("k_max") == 50
            and params.get("radius") == 0.02
            and params.get("point_column_source") == "npz"
        ),
        "hardware_gate_rtx_ada": (
            summary.get("environment", {})
            .get("hardware_gate", {})
            .get("status")
            == "pass"
            and summary["environment"]["hardware_gate"]["gpus"][0]["name"]
            == "NVIDIA RTX 4000 Ada Generation"
        ),
        "hot_and_runner_wall_material_repeat50": (
            comparisons["hot_query_speedup"] >= material_floor
            and comparisons["runner_wall_speedup"] >= material_floor
        ),
        "cold_plus_query_disclosed_below_material_floor": (
            comparisons["cold_plus_query_speedup"] < material_floor
        ),
        "summary_comparisons_match_evidence": (
            summary_comparisons["rtdl_optix_over_cupy_grid_hot_speedup"]
            == comparisons["hot_query_speedup"]
            and summary_comparisons["rtdl_optix_over_cupy_grid_cold_plus_query_speedup"]
            == comparisons["cold_plus_query_speedup"]
            and summary_comparisons["rtdl_optix_over_cupy_grid_runner_wall_speedup"]
            == comparisons["runner_wall_speedup"]
        ),
        "parity_integer_signature_and_tolerance": (
            parity["integer_signature_match"] is True
            and parity["same_contract_signature_match"] is True
            and parity["sum_distance_relative_error"] <= parity["sum_distance_relative_tolerance"]
        ),
        "float32_float64_contract_asymmetry_disclosed": (
            optix_contract.get("precision") == "float32"
            and optix_contract.get("exact") is False
            and cupy_contract.get("exact") is True
            and cupy_contract.get("uniform_grid_cuda_core") is True
            and summary["point_manifest"]["column_source_manifest"]["coordinate_dtype"] == "float64"
        ),
        "source_manifest_sha256_present_no_git_head": (
            SOURCE_MANIFEST.exists()
            and len(manifest_hashes) >= 4
            and "fatal: not a git repository" in summary["environment"]["git_head"]
        ),
        "call_for_review_exists": CALL_FOR_REVIEW.exists()
        and ROW_ID in call_text
        and "not V3 release authorization" in call_text,
        "claude_external_review_approves_with_conditions": claude_review_ok,
        "claude_stream_log_exists": CLAUDE_REVIEW_STREAM.exists()
        and CLAUDE_REVIEW_STREAM.stat().st_size > 0,
        "codex_consensus_accepts_conditions": codex_consensus_ok,
        "approved_wording_contains_all_conditions": (
            "7.889x hot-query" in approved_wording
            and "1.315x cold-plus-query" in approved_wording
            and "3.761x runner-wall" in approved_wording
            and "across 50 prepared repeated queries on the same search structure" in approved_wording
            and "float32 internal precision" in approved_wording
            and "float64 coordinate columns" in approved_wording
            and "CuPy uniform-grid CUDA-core" in approved_wording
            and "source_manifest.sha256" in approved_wording
            and "no git head" in approved_wording
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    promotion_authorized = failed_checks == []

    candidate_row = {
        "row_id": ROW_ID,
        "app_id": "rtnn",
        "generic_capability": "ranked_summary",
        "m7_promoted": promotion_authorized,
        "row_scoped_public_speedup_claim_authorized": promotion_authorized,
        "scope": "prepared repeat50 session amortization only",
        "hardware": summary["environment"]["hardware_gate"]["gpus"][0]["name"],
        "point_count": params["point_count"],
        "repeat": params["repeat"],
        "k_max": params["k_max"],
        "radius": params["radius"],
        "baseline": "CuPy uniform-grid CUDA-core",
        "precision_disclosure": (
            "RTDL OptiX float32 internal precision versus CuPy uniform-grid CUDA-core "
            "using float64 coordinate columns"
        ),
        "hot_query_speedup": comparisons["hot_query_speedup"],
        "cold_plus_query_speedup": comparisons["cold_plus_query_speedup"],
        "runner_wall_speedup": comparisons["runner_wall_speedup"],
        "sum_distance_relative_error": parity["sum_distance_relative_error"],
        "source_manifest_hash_count": len(manifest_hashes),
        "source_manifest_path": _rel(SOURCE_MANIFEST),
        "approved_row_scoped_public_wording": approved_wording,
    }

    return {
        "tool": "v3_phoenix_rtnn_prepared_repeat50_review_gate",
        "status": (
            "rtnn_prepared_repeat50_m7_qualified_row_scoped"
            if promotion_authorized
            else "rtnn_prepared_repeat50_review_blocked_not_m7"
        ),
        "generic_capability": "ranked_summary",
        "evidence_harness_app": "rtnn",
        "candidate_scope": evidence["candidate_scope"],
        "external_review_status": (
            "claude_approve_with_conditions" if claude_review_ok else "blocked_no_external_ai_verdict"
        ),
        "current_packet_2ai_consensus_status": (
            "claude_codex_consensus_complete_approve_one_row_scoped_m7"
            if codex_consensus_ok
            else "codex_consensus_missing_or_incomplete"
        ),
        "m7_candidate_reopen_authorized": promotion_authorized,
        "m7_promotion_authorized": promotion_authorized,
        "m7_qualified_release_rows_added": 1 if promotion_authorized else 0,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": promotion_authorized,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "whole_rtnn_claim_authorized": False,
        "one_shot_rtnn_claim_authorized": False,
        "paper_equivalent_claim_authorized": False,
        "material_speedup_floor": material_floor,
        "candidate_row": candidate_row,
        "candidate_row_ids": [ROW_ID] if promotion_authorized else [],
        "accepted_conditions": [
            "repeat50 scope disclosed in every speedup sentence",
            "hot-query, cold-plus-query, and runner-wall numbers travel together",
            "float32 OptiX versus float64-coordinate CuPy uniform-grid CUDA-core disclosed",
            "source_manifest.sha256 cited because no git head was available",
            "CuPy uniform-grid CUDA-core baseline named exactly",
        ],
        "review_records": {
            "candidate_evidence": _rel(EVIDENCE),
            "repeat50_summary": _rel(SUMMARY),
            "optix_payload": _rel(OPTIX_PAYLOAD),
            "cupy_grid_payload": _rel(CUPY_PAYLOAD),
            "source_manifest": _rel(SOURCE_MANIFEST),
            "call_for_review": _rel(CALL_FOR_REVIEW),
            "claude_external_review": _rel(CLAUDE_REVIEW),
            "claude_external_review_stream": _rel(CLAUDE_REVIEW_STREAM),
            "codex_consensus": _rel(CODEX_CONSENSUS),
        },
        "forbidden_public_wording": [
            "RTNN is solved",
            "V3 solves nearest-neighbor search",
            "RTDL beats the RTNN paper implementation",
            "one-shot RTNN speedup",
            "cold-start RTNN speedup beyond the disclosed 1.315x cold-plus-query row",
            "7.889x or 3.761x without the 1.315x cold-plus-query figure and repeat50 scope",
            "general nearest-neighbor baseline",
            "broad V3-over-V2 speedup",
            "V3 release authorization",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Promote exactly one RTNN prepared repeat50 ranked-summary row after Claude "
                "review and Codex consensus, with every wording/provenance condition enforced."
            ),
            "was_i_foolish": (
                "No. This only accepts the reviewed prepared-session row and keeps all broader "
                "RTNN, V3-over-V2, and release claims false."
            ),
            "foolish_actions": (
                "It would be foolish to present 7.889x or 3.761x without the 1.315x cold-plus-query "
                "limitation, hide the float32/float64 baseline asymmetry, or call the CuPy grid "
                "reference a general nearest-neighbor baseline."
            ),
            "other_path": (
                "Leave the row pending and move to Spatial. That would avoid risk but would fail "
                "to classify a now-reviewed material prepared-session engine result."
            ),
            "different_path_now": (
                "Use this gate as the only source of truth for RTNN repeat50 M7 counting, then "
                "update classification, queue, docs, and release readiness without changing the "
                "release-blocked state."
            ),
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    row = packet["candidate_row"]
    lines = [
        "# Phoenix V3 RTNN Prepared Repeat50 Review Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "This packet classifies one RTNN evidence row as a V3 `ranked_summary`",
        "prepared-session amortization result. It is not V3 release authorization",
        "and not a whole RTNN, one-shot, paper-equivalent, or broad V3-over-V2 claim.",
        "",
        "## Verdict",
        "",
        f"- External review: `{packet['external_review_status']}`",
        f"- 2-AI consensus: `{packet['current_packet_2ai_consensus_status']}`",
        f"- M7 rows added: `{packet['m7_qualified_release_rows_added']}`",
        "- Release authorized: `false`",
        "- Broad V3-over-V2 claim authorized: `false`",
        "",
        "## Candidate Row",
        "",
        f"- Row id: `{row['row_id']}`",
        f"- Capability: `{row['generic_capability']}`",
        f"- Scope: `{row['scope']}`",
        f"- Hardware: `{row['hardware']}`",
        f"- Point count / repeat / k / radius: `{row['point_count']}` / `{row['repeat']}` / `{row['k_max']}` / `{row['radius']}`",
        f"- Hot-query speedup: `{row['hot_query_speedup']:.3f}x`",
        f"- Cold-plus-query speedup: `{row['cold_plus_query_speedup']:.3f}x`",
        f"- Runner-wall speedup: `{row['runner_wall_speedup']:.3f}x`",
        f"- Precision/baseline disclosure: {row['precision_disclosure']}.",
        f"- Parity: integer signatures match; sum-distance relative error `{row['sum_distance_relative_error']:.3e}`.",
        f"- Provenance: `{row['source_manifest_path']}`; no git head was available.",
        "",
        "## Approved Row-Scoped Wording",
        "",
        row["approved_row_scoped_public_wording"],
        "",
        "## Accepted Conditions",
        "",
    ]
    for item in packet["accepted_conditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Forbidden Wording", ""])
    for item in packet["forbidden_public_wording"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Review Records", ""])
    for label, path in packet["review_records"].items():
        lines.append(f"- {label}: `{path}`")
    lines.extend(["", "## Checks", ""])
    for name, passed in packet["checks"].items():
        lines.append(f"- `{name}`: `{str(bool(passed)).lower()}`")
    audit = packet["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            f"Failed checks: `{packet['failed_checks']}`",
            "",
            "## Goal-Level Decision Audit",
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
