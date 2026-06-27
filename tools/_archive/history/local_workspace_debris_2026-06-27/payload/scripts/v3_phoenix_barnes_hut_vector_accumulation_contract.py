#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402


OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")
M6_SUMMARY = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m6_barnes_hut_20260620"
    / "m6_barnes_hut_intake_summary.json"
)
M6_REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_payload() -> dict[str, Any]:
    m6 = _read_json(M6_SUMMARY)
    contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
    body_summaries = list(m6["body_summaries"])
    ratios = {
        str(row["body_count"]): float(row["optix_numba_over_fastest"])
        for row in body_summaries
    }
    contribution_rows = {
        str(row["body_count"]): int(row["contribution_row_count"])
        for row in body_summaries
    }
    fastest = {
        str(row["body_count"]): str(row["fastest_route_id"])
        for row in body_summaries
    }
    checks = {
        "m6_summary_exists": M6_SUMMARY.exists(),
        "m6_report_exists": M6_REPORT.exists(),
        "m6_is_internal_not_release": m6.get("overall_status") == "internal_m6_route_parity_evidence",
        "m6_zero_m7_rows": m6.get("phoenix_m7_qualified_release_rows") == 0,
        "m6_blocks_public_speedup": m6.get("public_speedup_claim_authorized") is False,
        "m6_blocks_rt_core_speedup": m6.get("rt_core_speedup_claim_authorized") is False,
        "m6_uses_serious_scales": sorted(int(row["body_count"]) for row in body_summaries)
        == [32768, 65536, 131072],
        "m6_all_scales_fastest_numba_cuda": all(
            row["fastest_route_id"] == "numba_cuda_fused" for row in body_summaries
        ),
        "m6_prepared_optix_slower_all_scales": all(
            float(row["optix_numba_over_fastest"]) > 1.0 for row in body_summaries
        ),
        "contract_is_generic": contract.get("app_generic") is True,
        "contract_is_device_executable_not_rt_core": (
            contract.get("status") == "implemented_cuda_device_accumulation_not_rt_core"
            and contract.get("executable") is True
            and contract["claim_boundary"].get("runtime_implemented") is True
            and contract["claim_boundary"].get("rt_core_speedup_claim_authorized") is False
        ),
        "contract_blocks_public_and_rt_claims": all(
            value is False
            for key, value in contract["claim_boundary"].items()
            if key != "runtime_implemented"
        ),
        "contract_forbids_frontier_row_hot_path": "aggregate-frontier row emission"
        in contract["must_avoid"],
        "contract_forbids_app_specific_native_logic": "app-specific native engine callbacks"
        in contract["must_avoid"],
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "barnes_hut_vector_accumulation_contract_candidate_not_m7"

    return {
        "tool": "v3_phoenix_barnes_hut_vector_accumulation_contract",
        "version": "phoenix_v3_barnes_hut_vector_accumulation_contract_2026_06_21",
        "status": status,
        "generic_capability": "vector_accumulation",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "source_packets": {
            "m6_summary": _rel(M6_SUMMARY),
            "m6_report": _rel(M6_REPORT),
        },
        "m6_route_parity_evidence": {
            "overall_status": m6["overall_status"],
            "timing_basis_mixed": bool(m6["timing_basis_mixed"]),
            "fastest_by_scale": fastest,
            "prepared_optix_numba_over_fastest": ratios,
            "contribution_rows_by_scale": contribution_rows,
            "reading": (
                "M6 is serious route-parity evidence, but it is negative for the current "
                "prepared RTDL/OptiX frontier-emission shape: fused Numba CUDA is fastest "
                "at every rerun scale, and prepared RTDL/OptiX+Numba was slower than "
                "fused Numba CUDA by 5.120x to 13.912x on the 65,536 and 131,072 rows."
            ),
        },
        "required_generic_contract": {
            "contract": contract["contract"],
            "primitive": contract["primitive"],
            "status": contract["status"],
            "executable": contract["executable"],
            "required_first_backend": contract["required_first_backend"],
            "required_native_symbols": list(contract["required_native_symbols"]),
            "cpu_reference_api": contract["cpu_reference_api"],
            "partner_reference_api": contract["partner_reference_api"],
            "output_device_columns": list(contract["output_device_columns"]),
            "must_avoid": list(contract["must_avoid"]),
            "rt_core_claim_requirements": list(contract["rt_core_claim_requirements"]),
            "implemented_runtime": dict(contract["implemented_runtime"]),
            "claim_boundary": dict(contract["claim_boundary"]),
        },
        "v3_engine_decision": (
            "Keep Barnes-Hut as a V3 engine-gap driver, not a release win. The current "
            "app-agnostic aggregate-tree fused weighted-vector primitive now accumulates "
            "directly into device vector/count columns instead of emitting aggregate-frontier "
            "rows before vector math, but the scorecard blocker is not release-cleared."
        ),
        "future_m7_requirements": [
            "Improve the generic aggregate-tree fused weighted-vector primitive, not Barnes-Hut app-specific native code.",
            "Use the same source-id keyed vector summary as the CPU reference and Numba CUDA partner reference.",
            "Avoid aggregate-frontier row emission, host frontier materialization, and host contribution materialization on the hot path.",
            "Prove an OptiX pipeline launch with optixTrace or equivalent hardware traversal before any RT-core wording.",
            "Report BVH/build, optixLaunch traversal, continuation/vector accumulation, copy/materialization, and wall timing separately.",
            "Move the Barnes-Hut scorecard blocker to parity or better under the same contract.",
            "Require fresh RTX evidence, external review, and Codex consensus before reopening any M7 promotion.",
        ],
        "forbidden_shortcuts": [
            "Do not publish Barnes-Hut RT-core speedup wording from the current prepared frontier-emission route.",
            "Do not call fused Numba CUDA an RT-core result.",
            "Do not claim whole-app Barnes-Hut acceleration or paper reproduction.",
            "Do not use route parity as a public V3-over-V2 speedup claim.",
            "Do not add app-specific native Barnes-Hut engine callbacks to pass this gate.",
        ],
        "current_packet_external_review_status": "claude_cli_blocked_not_closed",
        "current_packet_2ai_consensus_status": "not_closed_requires_external_review_before_m7",
        "review_records": {
            "call_for_review": "docs/reviews/call_for_review_phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md",
            "claude_blocked": "docs/reviews/claude_blocked_phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md",
            "expected_external_review": "docs/reviews/claude_phoenix_v3_barnes_hut_vector_accumulation_contract_review_2026-06-21.md",
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Turn Barnes-Hut/vector-accumulation into a generic V3 engine-gap contract, not an app win.",
            "was_i_foolish": (
                "No. The evidence says the current prepared RTDL/OptiX frontier-emission route is slower "
                "than fused Numba CUDA, so the honest V3 move is to define the missing reusable primitive."
            ),
            "foolish_actions": (
                "The foolish action would be to sell route parity, contribution-row scale, or OptiX participation "
                "as Barnes-Hut RT-core acceleration while the fastest measured route is not RTDL/OptiX."
            ),
            "other_path": (
                "Tune Barnes-Hut-specific code or keep quoting old M101/M121 reports. That might improve a demo, "
                "but it would not establish a language-level V3 capability."
            ),
            "different_path_now": (
                "Use this packet to drive a generic fused vector-accumulation implementation and keep all M7, "
                "release, RT-core, and broad V3-over-V2 claims blocked until the primitive has fresh evidence."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    evidence = payload["m6_route_parity_evidence"]
    contract = payload["required_generic_contract"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 Barnes-Hut Vector-Accumulation Contract",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet advances the `barnes_hut_vector_accumulation_frontier_shape`",
        "queue item by turning it into a generic V3 engine-gap contract.",
        "Apps are evidence harnesses only; this is not Barnes-Hut app development and not a new M7 row.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"rt_core_speedup_claim_authorized: {str(payload['rt_core_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        f"M7 rows added by this packet: {payload['m7_qualified_release_rows_added']}",
        "```",
        "",
        "## M6 Evidence Reading",
        "",
        f"- Status: `{evidence['overall_status']}`",
        f"- Timing basis mixed: `{str(evidence['timing_basis_mixed']).lower()}`",
        "- Fastest route by scale:",
        "",
    ]
    for body_count, route in evidence["fastest_by_scale"].items():
        ratio = evidence["prepared_optix_numba_over_fastest"][body_count]
        rows = evidence["contribution_rows_by_scale"][body_count]
        lines.append(
            f"  - `{body_count}` bodies: `{route}`; prepared RTDL/OptiX+Numba over fastest `{ratio:.3f}x`; contribution rows `{rows}`"
        )
    lines.extend(
        [
            "",
            evidence["reading"],
            "",
            "## Required Generic Contract",
            "",
            f"- Primitive: `{contract['primitive']}`",
            f"- Contract: `{contract['contract']}`",
            f"- Status: `{contract['status']}`",
            f"- Executable today: `{str(contract['executable']).lower()}`",
            f"- First backend target: `{contract['required_first_backend']}`",
            f"- CPU reference: `{contract['cpu_reference_api']}`",
            f"- Partner reference: `{contract['partner_reference_api']}`",
            "",
            "Output columns:",
            "",
        ]
    )
    lines.extend(f"- `{column}`" for column in contract["output_device_columns"])
    lines.extend(["", "Must avoid:", ""])
    lines.extend(f"- {item}" for item in contract["must_avoid"])
    lines.extend(
        [
            "",
            "RT-core claim requirements:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in contract["rt_core_claim_requirements"])
    lines.extend(
        [
            "",
            "## V3 Engine Decision",
            "",
            payload["v3_engine_decision"],
            "",
            "## Future M7 Requirements",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["future_m7_requirements"])
    lines.extend(["", "## Forbidden Shortcuts", ""])
    lines.extend(f"- {item}" for item in payload["forbidden_shortcuts"])
    lines.extend(
        [
            "",
            "## Review Status",
            "",
            f"- External review: `{payload['current_packet_external_review_status']}`",
            f"- 2-AI consensus: `{payload['current_packet_2ai_consensus_status']}`",
            f"- Call for review: `{payload['review_records']['call_for_review']}`",
            f"- Blocked Claude attempt: `{payload['review_records']['claude_blocked']}`",
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            f"   {audit['was_i_foolish']}",
            "2. If yes, what actions made the decision foolish?",
            f"   {audit['foolish_actions']}",
            "3. Was there another path that would have avoided getting stuck on that idea?",
            f"   {audit['other_path']}",
            "4. Can I now try a different path that actually solves the problem?",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit the Phoenix V3 Barnes-Hut vector-accumulation contract.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps({"status": payload["status"], "m7_rows_added": 0}, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0 if payload["status"] == "barnes_hut_vector_accumulation_contract_candidate_not_m7" else 2


if __name__ == "__main__":
    raise SystemExit(main())
