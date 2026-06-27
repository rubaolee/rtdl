from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.post_closure_surface_audit.goal4542.v1"
OUT_JSON = Path("docs/reports/goal4542_v3_0_m143_post_closure_surface_audit_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4542_v3_0_m143_post_closure_surface_audit_2026-06-17.md")
GOAL4541_PACKET = Path(
    "docs/reports/goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.json"
)

CURRENT_SURFACE_FILES = (
    Path("docs/learn/benchmark_evidence_index.md"),
    Path("docs/learn/benchmark_partner_reference_matrix.md"),
    Path("docs/learn/rt_core_evidence_matrix.md"),
    Path("examples/benchmark_apps/barnes_hut/README.md"),
    Path("src/rtdsl/v3_0_benchmark_implementation_queue.py"),
    Path("src/rtdsl/current_benchmark_route_decisions.py"),
    Path("src/rtdsl/current_benchmark_adequacy.py"),
    Path("scripts/goal4522_m126_route_adequacy_consistency.py"),
    Path("scripts/goal4524_m128_benchmark_implementation_queue.py"),
    Path("scripts/goal4527_m131_barnes_hut_rt_native_traversal_semantic_gate.py"),
    Path("scripts/goal4533_m135_v3_claim_scope_closeout.py"),
    Path("scripts/goal4534_m136_v3_current_app_completion_gate.py"),
    Path("scripts/goal4535_m137_v3_completion_readiness_audit.py"),
    Path("scripts/goal4536_m138_v3_internal_completion_packet.py"),
    Path("scripts/goal4538_m139_v3_completion_review_consensus.py"),
    Path("scripts/goal4540_m141_triangle_non_graph_stream_closure_gate.py"),
    Path("scripts/goal4541_m142_barnes_hut_current_route_closure_gate.py"),
    Path("docs/reports/goal4522_v3_0_m126_route_adequacy_consistency_2026-06-17.md"),
    Path("docs/reports/goal4524_v3_0_m128_benchmark_implementation_queue_2026-06-17.md"),
    Path("docs/reports/goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.md"),
    Path("docs/reports/goal4533_v3_0_m135_v3_claim_scope_closeout_2026-06-17.md"),
    Path("docs/reports/goal4534_v3_0_m136_v3_current_app_completion_gate_2026-06-17.md"),
    Path("docs/reports/goal4535_v3_0_m137_v3_completion_readiness_audit_2026-06-17.md"),
    Path("docs/reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md"),
    Path("docs/reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md"),
    Path("docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.md"),
    Path("docs/reports/goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.md"),
)

KEY_GOAL4541_FILES = (
    Path("docs/learn/benchmark_evidence_index.md"),
    Path("docs/learn/benchmark_partner_reference_matrix.md"),
    Path("docs/learn/rt_core_evidence_matrix.md"),
    Path("examples/benchmark_apps/barnes_hut/README.md"),
    Path("src/rtdsl/v3_0_benchmark_implementation_queue.py"),
    Path("src/rtdsl/current_benchmark_route_decisions.py"),
    Path("src/rtdsl/current_benchmark_adequacy.py"),
    Path("scripts/goal4541_m142_barnes_hut_current_route_closure_gate.py"),
)

STALE_POST_CLOSURE_PATTERNS = (
    "future_design_queue_exact",
    "closed_count_is_nine",
    "closed_current_target_count_is_nine",
    "future_design_queue_barnes_only",
    "barnes_hut_is_future_design_target",
    "barnes_hut_future_design_target",
    "Barnes-Hut remains the only future design target",
    "Barnes-Hut is the only future design target",
    "Barnes-Hut is the only remaining future design target",
    "Barnes-Hut remains the only remaining future design target",
    "Nine apps are closed current targets",
    "nine apps are closed current targets",
)


def _read(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def _stale_hits(root: Path) -> dict[str, tuple[str, ...]]:
    hits: dict[str, tuple[str, ...]] = {}
    for path in CURRENT_SURFACE_FILES:
        text = _read(root, path)
        found = tuple(pattern for pattern in STALE_POST_CLOSURE_PATTERNS if pattern in text)
        if found:
            hits[path.as_posix()] = found
    return hits


def _goal4541_mentions(root: Path) -> dict[str, bool]:
    return {path.as_posix(): "Goal4541" in _read(root, path) for path in KEY_GOAL4541_FILES}


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    summary = queue["summary"]
    rows = {row["app"]: row for row in queue["rows"]}
    expected_apps = tuple(sorted(rows))
    stale_hits = _stale_hits(root)
    goal4541_mentions = _goal4541_mentions(root)
    goal4541_packet = json.loads((root / GOAL4541_PACKET).read_text(encoding="utf-8"))
    checks = {
        "queue_validates": validation["status"] == "accept",
        "queue_version_is_goal4541": queue["version"]
        == "rtdl.v3_0.benchmark_implementation_queue.goal4541.v9",
        "runtime_queue_empty": tuple(summary["runtime_build_queue"]) == (),
        "claim_queue_empty": tuple(summary["claim_or_evidence_queue"]) == (),
        "design_blocker_queue_empty": tuple(summary["design_blocker_queue"]) == (),
        "future_design_queue_empty": tuple(summary["future_design_target_queue"]) == (),
        "all_ten_apps_closed_current_targets": tuple(sorted(summary["closed_current_targets"]))
        == expected_apps,
        "barnes_hut_closed_with_goal4541": (
            rows["barnes_hut"]["work_class"] == "closed_current_target"
            and "Goal4541" in rows["barnes_hut"]["evidence_refs"]
            and not rows["barnes_hut"]["pod_needed_next"]
        ),
        "goal4541_packet_accepts": tuple(goal4541_packet["failed_checks"]) == (),
        "current_surface_no_stale_post_closure_wording": not stale_hits,
        "key_surfaces_mention_goal4541": all(goal4541_mentions.values()),
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
        "goal": "Goal4542 / V3 M143",
        "status": "post_closure_surface_audit_checked",
        "date": "2026-06-17",
        "queue_version": queue["version"],
        "queue_status": queue["status"],
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "audited_file_count": len(CURRENT_SURFACE_FILES),
        "audited_files": tuple(path.as_posix() for path in CURRENT_SURFACE_FILES),
        "stale_post_closure_pattern_hits": stale_hits,
        "goal4541_mentions": goal4541_mentions,
        "source_packets": {
            "goal4541": goal4541_packet["version"],
        },
        "claim_boundary": {
            "runtime_executed": False,
            "current_route_changed": False,
            "release_authorized": False,
            "rt_native_hierarchical_traversal_implemented": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "Goal4542 audits the post-Goal4541 current surface. The queue validates "
            "with empty runtime, claim/evidence, design-blocker, and future-design "
            "queues; all ten benchmark apps are closed current targets; Barnes-Hut "
            "is closed only as a mixed-explicit current route classification; and "
            "the audited current docs/scripts/reports have no stale nine-app or "
            "Barnes-Hut-only-future-design wording. This audit does not authorize "
            "release, public speedup, broad RT-core, paper-reproduction, automatic "
            "partner-selection, RT-native Barnes-Hut traversal, or app-specific "
            "native-engine wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["summary"]
    lines = [
        "# Goal4542 / V3 M143 Post-Closure Surface Audit",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Queue State",
        "",
        f"- Runtime queue: `{', '.join(summary['runtime_build_queue'])}`",
        f"- Claim/evidence queue: `{', '.join(summary['claim_or_evidence_queue'])}`",
        f"- Design blocker queue: `{', '.join(summary['design_blocker_queue'])}`",
        f"- Future design targets: `{', '.join(summary['future_design_target_queue'])}`",
        f"- Closed current targets: `{', '.join(summary['closed_current_targets'])}`",
        "",
        "## Surface Audit",
        "",
        f"- Audited file count: `{packet['audited_file_count']}`",
        f"- Stale post-closure pattern hits: `{len(packet['stale_post_closure_pattern_hits'])}`",
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
            "- RT-native Barnes-Hut hierarchical traversal remains unimplemented future optional research/claim expansion.",
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
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
