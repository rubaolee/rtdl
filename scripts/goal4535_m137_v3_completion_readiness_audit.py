from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.completion_readiness_audit.goal4535.v1"
OUT_JSON = Path("docs/reports/goal4535_v3_0_m137_v3_completion_readiness_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4535_v3_0_m137_v3_completion_readiness_audit_2026-06-17.md")

CURRENT_AUDIT_FILES = (
    Path("docs/learn/benchmark_evidence_index.md"),
    Path("examples/current/research_benchmarks/barnes_hut/README.md"),
    Path("examples/current/research_benchmarks/triangle_counting/README.md"),
    Path("examples/current/research_benchmarks/rtnn/README.md"),
    Path("examples/current/research_benchmarks/spatial_rayjoin/README.md"),
    Path("src/rtdsl/v3_0_benchmark_implementation_queue.py"),
    Path("scripts/goal4524_m128_benchmark_implementation_queue.py"),
    Path("scripts/goal4527_m131_barnes_hut_rt_native_traversal_semantic_gate.py"),
    Path("scripts/goal4533_m135_v3_claim_scope_closeout.py"),
    Path("scripts/goal4534_m136_v3_current_app_completion_gate.py"),
    Path("scripts/goal4540_m141_triangle_non_graph_stream_closure_gate.py"),
    Path("scripts/goal4541_m142_barnes_hut_current_route_closure_gate.py"),
)

STALE_CURRENT_PATTERNS = (
    "active runtime queue advances",
    "runtime queue advances to RT-DBSCAN",
    "claim/evidence packaging blockers",
    "RTNN and Spatial RayJoin remain claim/evidence",
    "Barnes-Hut and Triangle Counting are listed only as future design targets",
    "Barnes-Hut remains the only future design target",
    "Barnes-Hut is the only future design target",
)


def _stale_hits(root: Path) -> dict[str, tuple[str, ...]]:
    hits: dict[str, tuple[str, ...]] = {}
    for path in CURRENT_AUDIT_FILES:
        text = (root / path).read_text(encoding="utf-8")
        found = tuple(pattern for pattern in STALE_CURRENT_PATTERNS if pattern in text)
        if found:
            hits[path.as_posix()] = found
    return hits


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    summary = queue["summary"]
    stale_hits = _stale_hits(root)
    checks = {
        "queue_validates": validation["status"] == "accept",
        "runtime_queue_empty": tuple(summary["runtime_build_queue"]) == (),
        "claim_queue_empty": tuple(summary["claim_or_evidence_queue"]) == (),
        "design_blocker_queue_empty": tuple(summary["design_blocker_queue"]) == (),
        "future_design_queue_empty_after_goal4541": tuple(
            summary["future_design_target_queue"]
        )
        == (),
        "closed_current_target_count_is_ten": len(summary["closed_current_targets"]) == 10,
        "current_audit_files_no_stale_queue_wording": not stale_hits,
        "all_public_speedup_claims_blocked": summary["all_public_speedup_claims_blocked"],
        "all_broad_rt_core_claims_blocked": summary["all_broad_rt_core_claims_blocked"],
        "all_paper_reproduction_claims_blocked": summary["all_paper_reproduction_claims_blocked"],
        "all_automatic_partner_selection_blocked": summary[
            "all_automatic_partner_selection_blocked"
        ],
        "all_app_specific_native_engine_logic_blocked": summary[
            "all_app_specific_native_engine_logic_blocked"
        ],
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4535 / V3 M137",
        "status": "completion_readiness_audit_checked",
        "date": "2026-06-17",
        "queue_version": queue["version"],
        "queue_status": queue["status"],
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "audited_files": tuple(path.as_posix() for path in CURRENT_AUDIT_FILES),
        "stale_current_pattern_hits": stale_hits,
        "claim_boundary": {
            "current_route_changed": False,
            "runtime_executed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "Goal4535 audits the current V3 completion surface after Goal4534. "
            "The implementation queue validates with empty runtime, claim/evidence, "
            "design-blocker queues; Goal4540 accepts Triangle's non-graph stream "
            "continuation contract, and Goal4541 closes Barnes-Hut only as a "
            "current mixed-explicit route target while preserving RT-native "
            "hierarchical traversal as future optional research/claim expansion. "
            "The current reader-facing docs and "
            "queue scripts checked by this audit contain no stale wording that "
            "reopens RT-DBSCAN runtime work or RTNN/Spatial RayJoin claim blockers. "
            "This audit does not authorize release or any public speedup, broad "
            "RT-core, paper-reproduction, automatic partner-selection, or "
            "app-specific native-engine claims."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["summary"]
    lines = [
        "# Goal4535 / V3 M137 Completion Readiness Audit",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Queue Summary",
        "",
        f"- Runtime queue: `{', '.join(summary['runtime_build_queue'])}`",
        f"- Claim/evidence queue: `{', '.join(summary['claim_or_evidence_queue'])}`",
        f"- Design blocker queue: `{', '.join(summary['design_blocker_queue'])}`",
        f"- Future design target queue: `{', '.join(summary['future_design_target_queue'])}`",
        f"- Closed current targets: `{', '.join(summary['closed_current_targets'])}`",
        "",
        "## Stale Current Wording Audit",
        "",
        f"- Audited file count: `{len(packet['audited_files'])}`",
        f"- Stale pattern hits: `{len(packet['stale_current_pattern_hits'])}`",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No runtime was executed.",
            "- No current route changed.",
            "- No release, public speedup, broad RT-core, paper-reproduction, automatic partner-selection, or app-specific native-engine wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {"failed_checks": packet["failed_checks"], "status": "accept" if not packet["failed_checks"] else "reject"},
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
