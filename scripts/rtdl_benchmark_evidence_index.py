#!/usr/bin/env python3
"""Print the current RTDL benchmark evidence index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.current_benchmark_front_doors import (  # noqa: E402
    CURRENT_BENCHMARK_FRONT_DOOR_CLAIM_BOUNDARY,
    CURRENT_BENCHMARK_FRONT_DOOR_VERSION,
    current_benchmark_front_doors,
    summarize_current_benchmark_front_doors,
    validate_current_benchmark_front_doors,
)


EVIDENCE_REPORTS = {
    "Goal3757": "docs/reports/goal3757_robot_collision_scaled_prepared_perf_packet_2026-06-07.md",
    "Goal3758": "docs/reports/goal3758_rt_dbscan_numba_repeat_probe_support_2026-06-07.md",
    "Goal3761": "docs/reports/goal3761_rayjoin_native_pip_cross_size_current_2026-06-07.md",
    "Goal3762": "docs/reports/goal3762_barnes_hut_numba_block_reduce_force_2026-06-07.md",
    "Goal3818": "docs/reports/goal3818_current_benchmark_contract_smoke_a5000_2026-06-07.md",
    "Goal3819": "docs/reports/goal3819_triangle_counting_native_mode_probe_2026-06-07.md",
    "Goal3820": "docs/reports/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_2026-06-07.md",
    "Goal3823": "docs/reports/goal3823_current_benchmark_front_door_registry_2026-06-07.md",
    "Goal3828": "docs/reports/goal3828_current_benchmark_scale_profile_registry_2026-06-07.md",
    "Goal4215": "docs/reports/goal4215_current_benchmark_scale_profile_after_rtdbscan_policy_2026-06-09.md",
    "Goal4266": "docs/reports/goal4266_large_scale_cupy_numba_partner_comparison_2026-06-09.md",
}


APP_GUIDANCE = {
    "hausdorff_xhd": {
        "user_reading": "primitive-first OptiX path; CuPy/Numba are comparison/reference lanes",
        "pod_need": "OptiX timing needs NVIDIA pod or workstation",
    },
    "spatial_rayjoin": {
        "user_reading": "contract-split RayJoin-style path; scalar/count paths are stronger than full paper reproduction",
        "pod_need": "OptiX timing and public-CDB fixture runs need NVIDIA pod",
    },
    "rt_dbscan": {
        "user_reading": "OptiX fixed-radius flags plus explicit Numba component continuation",
        "pod_need": "OptiX plus Numba timing needs CUDA pod",
    },
    "robot_collision": {
        "user_reading": "primitive-only prepared static-scene collision count path",
        "pod_need": "OptiX timing needs NVIDIA pod",
    },
    "contact_manifold": {
        "user_reading": "bounded collect/witness primitive path; no manifold-native ABI",
        "pod_need": "OptiX timing needs NVIDIA pod",
    },
    "raydb_style": {
        "user_reading": "primitive-first grouped count path; partner rows only for unfused continuations",
        "pod_need": "OptiX timing needs NVIDIA pod; CuPy/Numba comparison needs CUDA pod",
    },
    "barnes_hut": {
        "user_reading": "aggregate-frontier pressure plus Numba exact-force reference",
        "pod_need": "Numba CUDA timing needs CUDA pod",
    },
    "librts_spatial_index": {
        "user_reading": "prepared AABB-index benchmark slice, not full mutable LibRTS",
        "pod_need": "OptiX timing needs NVIDIA pod",
    },
    "rtnn": {
        "user_reading": "prepared fixed-radius ranked summary path",
        "pod_need": "OptiX timing needs NVIDIA pod",
    },
    "triangle_counting": {
        "user_reading": "explicit native graph summary path; candidate-row interpretation stays app code",
        "pod_need": "OptiX timing needs NVIDIA pod",
    },
}


def _command_text(command: tuple[str, ...]) -> str:
    return " ".join(command)


def _resolve_evidence(refs: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    resolved = []
    for ref in refs:
        path = EVIDENCE_REPORTS.get(ref)
        resolved.append(
            {
                "ref": ref,
                "path": path,
                "exists": bool(path and (ROOT / path).exists()),
            }
        )
    return tuple(resolved)


def build_index() -> dict[str, Any]:
    rows = []
    for row in current_benchmark_front_doors():
        app = str(row["app"])
        guidance = APP_GUIDANCE[app]
        command = tuple(row["command"])
        rows.append(
            {
                "app": app,
                "row_id": row["row_id"],
                "purpose": row["purpose"],
                "command": command,
                "command_text": _command_text(command),
                "timeout_sec": row["timeout_sec"],
                "requires_optix_library": row["requires_optix_library"],
                "requires_numba": row["requires_numba"],
                "evidence_refs": row["evidence_refs"],
                "evidence_reports": _resolve_evidence(tuple(row["evidence_refs"])),
                "user_reading": guidance["user_reading"],
                "pod_need": guidance["pod_need"],
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_rt_core_claim_authorized": False,
                "paper_reproduction_claim_authorized": False,
            }
        )

    return {
        "version": CURRENT_BENCHMARK_FRONT_DOOR_VERSION,
        "status": "current_v2_10_evidence_index_not_release_authorization",
        "claim_boundary": CURRENT_BENCHMARK_FRONT_DOOR_CLAIM_BOUNDARY,
        "validation": validate_current_benchmark_front_doors(),
        "summary": summarize_current_benchmark_front_doors(),
        "rows": tuple(rows),
        "cross_cutting_reports": (
            EVIDENCE_REPORTS["Goal3823"],
            EVIDENCE_REPORTS["Goal3828"],
            EVIDENCE_REPORTS["Goal4215"],
            EVIDENCE_REPORTS["Goal4266"],
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
    }


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Current Benchmark Evidence Index",
        "",
        f"Version: `{payload['version']}`",
        "",
        "This is an evidence map, not a release or speedup authorization.",
        "",
        "| App | Row | Pod need | User reading | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        evidence = ", ".join(report["ref"] for report in row["evidence_reports"])
        lines.append(
            "| {app} | `{row_id}` | {pod_need} | {user_reading} | {evidence} |".format(
                app=row["app"],
                row_id=row["row_id"],
                pod_need=row["pod_need"],
                user_reading=row["user_reading"],
                evidence=evidence,
            )
        )
    lines.extend(
        [
            "",
            "Run the front-door registry dry-run:",
            "",
            "```bash",
            "PYTHONPATH=src:. python scripts/goal3823_current_benchmark_front_door_runner.py --dry-run",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    args = parser.parse_args(argv)

    payload = build_index()
    missing = [
        report
        for row in payload["rows"]
        for report in row["evidence_reports"]
        if not report["exists"]
    ]
    if missing:
        payload = {**payload, "status": "reject_missing_evidence_report", "missing_evidence": tuple(missing)}

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_markdown(payload), end="")

    return 0 if not missing and payload["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
