from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import rtdsl as rt
from scripts import run_test_matrix


PACKET_VERSION = "rtdl.v3_0.current_scope_completion.goal4614.v1"
OUT_JSON = Path("docs/reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.json")
OUT_REPORT = Path("docs/reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.md")

APP_AUTHOR_DOC = Path("docs/learn/v3_0_app_author_implementation_strategy.md")
EMBEDDABILITY_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md")
BINDING_MATRIX_DOC = Path("docs/history/v4_preparatory_embedding/v3_0_binding_and_device_interop_matrix.md")
EVIDENCE_INDEX = Path("docs/learn/benchmark_evidence_index.md")
EXPECTED_CURRENT_MODULE_COUNT = 39
V4_PREP_TOKENS: tuple[str, ...] = (
    "c_abi",
    "embedd",
    "zero_copy",
    "ctypes",
    "dlpack",
    "binding_interop",
    "toolchain_support",
    "neutral_buffer",
)

V4_DEFERRALS: tuple[dict[str, str], ...] = (
    {
        "item": "stable_packaged_sdk",
        "reason": "The current C ABI evidence is source-tree, prefix-stage, and archive-stage handoff proof, not a frozen installed SDK.",
    },
    {
        "item": "generated_language_bindings",
        "reason": "Current Python examples are hand-written ctypes examples; generated Python/Rust/Julia/C# packages remain future work.",
    },
    {
        "item": "device_buffer_query_route",
        "reason": "CUDA/DLPack-like descriptors are metadata-only today; no C ABI query route consumes device buffers.",
    },
    {
        "item": "external_cuda_stream_ordering",
        "reason": "The current C ABI has no same-stream/event ordering proof for borrowed framework streams.",
    },
    {
        "item": "public_true_zero_copy",
        "reason": "Descriptor metadata and no-hidden-copy contracts are not public true-zero-copy support.",
    },
    {
        "item": "optix_embree_c_abi_execution",
        "reason": "The current C ABI executes the host AABB2 proof route only; OptiX/Embree execution through the C ABI is future work.",
    },
    {
        "item": "device_callable_fusion",
        "reason": "PTX/OptiX callable fusion remains an optional falsifiable experiment, not a V3 completion blocker.",
    },
    {
        "item": "amd_hiprt_evidence",
        "reason": "AMD/HIPRT timing and parity remain hardware-gated future evidence, not a blocker for the NVIDIA/CPU current V3 scope.",
    },
)


def _prior_packet(module_name: str, root: Path) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    try:
        return module.build_packet(root)
    except TypeError:
        return module.build_packet()


def _read(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def _app_rows() -> tuple[dict[str, Any], ...]:
    queue = {row["app"]: row for row in rt.v3_benchmark_implementation_queue()["rows"]}
    routes = {row["app"]: row for row in rt.current_benchmark_route_decisions()}
    adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}
    rows: list[dict[str, Any]] = []
    for app in sorted(queue):
        rows.append(
            {
                "app": app,
                "queue_class": queue[app]["work_class"],
                "route_kind": routes[app]["decision_kind"],
                "partner_policy": routes[app]["partner_policy"],
                "adequacy": adequacy[app]["adequacy"],
                "current_recommended_path": adequacy[app]["current_recommended_path"],
                "next_build_target": queue[app]["next_build_target"],
                "pod_needed_next": queue[app]["pod_needed_next"],
            }
        )
    return tuple(rows)


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    queue_validation = rt.validate_v3_benchmark_implementation_queue(queue)
    target_rows = rt.current_major_performance_targets()
    target_summary = rt.summarize_current_major_performance_targets(target_rows)
    target_validation = rt.validate_current_major_performance_targets(target_rows)
    modules = run_test_matrix.group_modules("v3_current")
    app_rows = _app_rows()

    prior_packets = {
        "goal4538_completion_review_consensus": _prior_packet(
            "scripts.goal4538_m139_v3_completion_review_consensus", root
        ),
        "goal4542_post_closure_surface_audit": _prior_packet(
            "scripts.goal4542_m143_v3_post_closure_surface_audit", root
        ),
        "goal4543_major_performance_target_refresh": _prior_packet(
            "scripts.goal4543_m144_v3_major_performance_target_refresh", root
        ),
        "goal4544_app_author_strategy_doc": _prior_packet(
            "scripts.goal4544_m145_v3_app_author_strategy_doc", root
        ),
        "goal4546_current_test_matrix_gate": _prior_packet(
            "scripts.goal4546_m147_v3_current_test_matrix_gate", root
        ),
    }

    app_author_doc = _read(root, APP_AUTHOR_DOC)
    embeddability_doc = _read(root, EMBEDDABILITY_DOC)
    binding_matrix_doc = _read(root, BINDING_MATRIX_DOC)
    evidence_index = _read(root, EVIDENCE_INDEX)

    scope_completion = {
        "v3_current_scope_complete": True,
        "benchmark_app_queue_closed": True,
        "v4_deferrals_do_not_block_v3": True,
        "release_tag_authorized": False,
        "public_performance_claim_authorized": False,
        "stable_sdk_authorized": False,
        "true_zero_copy_authorized": False,
    }

    claim_boundary_flags = {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_specialized_code_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "stable_sdk_authorized": False,
        "generated_bindings_authorized": False,
        "device_buffer_query_route_authorized": False,
        "external_stream_ordering_authorized": False,
        "public_true_zero_copy_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
    }

    summary = queue["summary"]
    checks = {
        "queue_validates": queue_validation["status"] == "accept",
        "all_ten_apps_closed": len(summary["closed_current_targets"]) == 10,
        "runtime_queue_empty": tuple(summary["runtime_build_queue"]) == (),
        "claim_queue_empty": tuple(summary["claim_or_evidence_queue"]) == (),
        "design_blocker_queue_empty": tuple(summary["design_blocker_queue"]) == (),
        "future_design_queue_empty": tuple(summary["future_design_target_queue"]) == (),
        "all_app_rows_closed": all(row["queue_class"] == "closed_current_target" for row in app_rows),
        "no_app_needs_immediate_pod": not any(row["pod_needed_next"] for row in app_rows),
        "target_map_validates": target_validation["status"] == "accept",
        "target_map_has_no_immediate_pod_targets": tuple(target_summary["pod_needed_next_targets"]) == (),
        "prior_completion_packets_accept": all(
            tuple(packet.get("failed_checks", ())) == () for packet in prior_packets.values()
        ),
        "matrix_registered_and_ends_at_goal4614": (
            len(modules) == EXPECTED_CURRENT_MODULE_COUNT
            and modules[-1] == "tests.goal4614_v3_0_m215_current_scope_completion_gate_test"
        ),
        "matrix_excludes_v4_preparatory_modules": not any(
            token in module for module in modules for token in V4_PREP_TOKENS
        ),
        "app_author_doc_names_goal4614": "Goal4614" in app_author_doc,
        "app_author_doc_names_v4_deferrals": "V4 deferrals" in app_author_doc,
        "embeddability_doc_marks_v4_deferral": "V4 deferral" in embeddability_doc,
        "binding_matrix_marks_v4_deferral": "V4 deferral" in binding_matrix_doc,
        "evidence_index_links_goal4614": "Goal4614 V3 current-scope completion gate" in evidence_index,
        "all_claim_boundary_flags_false": not any(claim_boundary_flags.values()),
        "completion_scope_is_internal_current_scope": (
            scope_completion["v3_current_scope_complete"]
            and not scope_completion["release_tag_authorized"]
            and not scope_completion["stable_sdk_authorized"]
        ),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4614 / V3 M215",
        "status": "current_scope_completion_checked",
        "date": "2026-06-18",
        "checks": checks,
        "failed_checks": failed,
        "scope_completion": scope_completion,
        "claim_boundary": claim_boundary_flags,
        "v4_deferrals": V4_DEFERRALS,
        "source_packets": {name: packet["version"] for name, packet in prior_packets.items()},
        "app_queue_summary": summary,
        "target_summary": target_summary,
        "test_matrix": {
            "group": "v3_current",
            "module_count": len(modules),
            "first_module": modules[0],
            "last_module": modules[-1],
        },
        "app_rows": app_rows,
        "conclusion": (
            "Goal4614 closes the V3 current scope: the ten benchmark-app current "
            "routes are closed, the runtime/claim/design/future-design queues are "
            "empty, the app-author route policy is documented, and the V3 current "
            "test matrix is the canonical validation surface. This is a real V3 "
            "completion for the benchmark-app/current-route project scope. It does "
            "not turn V4 embeddability work into a V3 blocker, and it does not "
            "authorize public release, public performance tables, broad RT-core "
            "speedup wording, paper-reproduction wording, automatic partner "
            "selection, stable SDK wording, device-buffer query execution, external "
            "stream ordering, or public true-zero-copy claims."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4614 / V3 M215 Current-Scope Completion Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## What Is Complete In V3",
        "",
        "- All ten benchmark-app current routes are closed.",
        "- Runtime, claim/evidence, design-blocker, and future-design queues are empty.",
        "- Current route and partner policy are documented for app authors.",
        "- The canonical validation surface is `scripts/run_test_matrix.py --group v3_current`.",
        "- The current V3 completion claim is internal current-scope completion, not a public release/performance claim.",
        "",
        "## V4 Deferrals",
        "",
        "| Item | Why it is not a V3 blocker |",
        "| --- | --- |",
    ]
    for row in packet["v4_deferrals"]:
        lines.append(f"| `{row['item']}` | {row['reason']} |")

    lines.extend(
        [
            "",
            "## App Matrix",
            "",
            "| App | Route kind | Partner policy | Adequacy | Immediate pod needed |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in packet["app_rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['route_kind']}` | `{row['partner_policy']}` | "
            f"`{row['adequacy']}` | `{row['pod_needed_next']}` |"
        )

    lines.extend(
        [
            "",
            "## Test Matrix",
            "",
            f"- Group: `{packet['test_matrix']['group']}`",
            f"- Module count: `{packet['test_matrix']['module_count']}`",
            f"- First module: `{packet['test_matrix']['first_module']}`",
            f"- Last module: `{packet['test_matrix']['last_module']}`",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- V3 current-scope completion is accepted when every check passes.",
            "- No release tag, public speedup, whole-app speedup, broad RT-core, paper-reproduction, RTDL-beats-specialized-code, automatic partner-selection, stable SDK, generated-binding, device-buffer query, external-stream, public true-zero-copy, or app-specific native-engine wording is authorized by this packet.",
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
