#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.current.research_benchmarks.contact_manifold import (  # noqa: E402
    rtdl_contact_manifold_benchmark_app as contact,
)
from scripts import v3_optix_hardware_gate  # noqa: E402


DEFAULT_OUT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_aabb_prepare_reuse_20260621"
)
SERIOUS_SCALE_FLOOR = 32_768
MATERIAL_WALL_SPEEDUP_FLOOR = 1.20
ALLOWED_BACKENDS = ("cpu", "embree", "optix")


def main() -> int:
    args = parse_args()
    backends = parse_backends(args.backends)
    if not args.allow_non_serious_local_smoke and args.grid_count < SERIOUS_SCALE_FLOOR:
        raise SystemExit(
            "grid-count is below the Phoenix serious scale floor; pass "
            "--allow-non-serious-local-smoke only for local smoke tests"
        )

    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    env_payload = environment_payload(require_rt_hardware=args.require_rt_hardware)
    (out_dir / "environment.json").write_text(
        json.dumps(env_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if "optix" in backends and args.require_rt_hardware and env_payload["hardware_gate"]["status"] != "pass":
        summary = build_summary(
            args=args,
            backend_payloads={},
            environment=env_payload,
            run_errors={
                "optix_hardware_gate": env_payload["hardware_gate"]["fail_closed_reason"]
                or "OptiX RT hardware gate failed"
            },
        )
        write_summary(out_dir, summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 2

    backend_payloads: dict[str, dict[str, Any]] = {}
    run_errors: dict[str, str] = {}
    for backend in backends:
        try:
            payload = run_backend(args=args, discovery_backend=backend)
            backend_payloads[backend] = payload
            (out_dir / f"aabb_prepare_reuse_{backend}.json").write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except Exception as exc:  # pragma: no cover - exercised on backend-specific hosts
            run_errors[backend] = repr(exc)
            (out_dir / f"aabb_prepare_reuse_{backend}.error.txt").write_text(
                repr(exc) + "\n",
                encoding="utf-8",
            )
            if args.fail_fast:
                break

    summary = build_summary(
        args=args,
        backend_payloads=backend_payloads,
        environment=env_payload,
        run_errors=run_errors,
    )
    write_summary(out_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["runner_completed"] else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run Phoenix V3 serious AABB prepare-reuse evidence. This runner "
            "prepares the indexed AABB scene once, then measures repeated query "
            "and collect phases for the generic aabb_index_query_2d contract."
        )
    )
    parser.add_argument("--dataset", default="jittered_grid", choices=("grid", "jittered_grid"))
    parser.add_argument("--grid-count", type=int, default=SERIOUS_SCALE_FLOOR)
    parser.add_argument("--resolution", type=int)
    parser.add_argument("--witness-capacity", type=int)
    parser.add_argument("--discovery-row-capacity", type=int)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--repeat", type=int, default=50)
    parser.add_argument("--backends", default="embree,optix")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--require-rt-hardware", action="store_true")
    parser.add_argument("--allow-non-serious-local-smoke", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    return parser.parse_args()


def parse_backends(value: str) -> tuple[str, ...]:
    raw = [part.strip().lower().replace("-", "_") for part in value.split(",") if part.strip()]
    aliases = {
        "python": "cpu",
        "cpu_python_reference": "cpu",
        "nvidia_rt": "optix",
        "cuda_optix": "optix",
    }
    normalized = tuple(dict.fromkeys(aliases.get(part, part) for part in raw))
    bad = [part for part in normalized if part not in ALLOWED_BACKENDS]
    if bad:
        raise ValueError(f"unsupported discovery backend(s): {bad}; allowed: {ALLOWED_BACKENDS}")
    if not normalized:
        raise ValueError("at least one backend is required")
    return normalized


def run_backend(*, args: argparse.Namespace, discovery_backend: str) -> dict[str, Any]:
    witness_capacity = args.witness_capacity or args.grid_count
    row_capacity = args.discovery_row_capacity or max(args.grid_count * 2, witness_capacity)
    started = time.perf_counter()
    payload = contact.aabb_broadphase_collect_k_payload(
        dataset=args.dataset,
        witness_capacity=witness_capacity,
        grid_count=args.grid_count,
        resolution=args.resolution,
        backend="cpu_python_reference",
        discovery_backend=discovery_backend,
        discovery_row_capacity=row_capacity,
        discovery_warmup_count=args.warmup,
        discovery_repeat_count=args.repeat,
    )
    runner_wall_sec = time.perf_counter() - started
    payload["phoenix_v3_aabb_prepare_reuse_runner"] = {
        "runner": "scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py",
        "generic_capability": "aabb_candidate_stream",
        "discovery_backend": discovery_backend,
        "dataset": args.dataset,
        "indexed_aabb_count": args.grid_count,
        "query_aabb_count": args.grid_count,
        "serious_scale_floor": SERIOUS_SCALE_FLOOR,
        "serious_scale": args.grid_count >= SERIOUS_SCALE_FLOOR,
        "warmup": args.warmup,
        "repeat": args.repeat,
        "witness_capacity": witness_capacity,
        "discovery_row_capacity": row_capacity,
        "runner_wall_sec": runner_wall_sec,
        "m7_promotion_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    return payload


def environment_payload(*, require_rt_hardware: bool) -> dict[str, Any]:
    nvidia_smi = run_command_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,compute_cap",
            "--format=csv,noheader",
        ]
    )
    git_head = run_command_text(["git", "rev-parse", "HEAD"], cwd=ROOT)
    hardware_gate = v3_optix_hardware_gate.build_payload(
        require_rt_hardware=require_rt_hardware,
        sample_nvidia_smi=None,
    )
    return {
        "tool": "v3_phoenix_aabb_prepare_reuse_pod_runner_environment",
        "python": sys.version,
        "cwd": str(ROOT),
        "git_head": git_head.strip(),
        "nvidia_smi": nvidia_smi.strip(),
        "hardware_gate": hardware_gate,
        "env": {
            "RTDL_OPTIX_LIBRARY": os.environ.get("RTDL_OPTIX_LIBRARY"),
            "RTDL_EMBREE_LIBRARY": os.environ.get("RTDL_EMBREE_LIBRARY"),
            "PYTHONPATH": os.environ.get("PYTHONPATH"),
        },
    }


def run_command_text(command: list[str], *, cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd is not None else None,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # pragma: no cover - host tool dependent
        return f"ERROR: {exc!r}"
    text = completed.stdout.strip()
    if completed.stderr.strip():
        text = (text + "\n" if text else "") + completed.stderr.strip()
    return text


def build_summary(
    *,
    args: argparse.Namespace,
    backend_payloads: dict[str, dict[str, Any]],
    environment: dict[str, Any],
    run_errors: dict[str, str],
) -> dict[str, Any]:
    phase_rows = {
        backend: phase_summary(payload)
        for backend, payload in sorted(backend_payloads.items())
    }
    comparisons = comparison_summary(phase_rows)
    checks = {
        "runner_completed_without_backend_errors": not run_errors,
        "serious_fixture_scale": args.grid_count >= SERIOUS_SCALE_FLOOR,
        "has_32768_indexed_aabbs": args.grid_count >= SERIOUS_SCALE_FLOOR,
        "has_32768_query_aabbs": args.grid_count >= SERIOUS_SCALE_FLOOR,
        "prepare_once_query_many_requested": args.repeat > 1,
        "embree_and_optix_present": {"embree", "optix"}.issubset(backend_payloads),
        "all_payloads_match_cpu_reference": all(
            bool(payload.get("matches_cpu_reference")) for payload in backend_payloads.values()
        )
        and bool(backend_payloads),
        "all_payloads_complete_candidate_coverage": all(
            bool(payload.get("complete_candidate_coverage")) for payload in backend_payloads.values()
        )
        and bool(backend_payloads),
        "all_payloads_observed_reuse": all(
            bool(
                payload.get("prepared_session_residency", {}).get(
                    "query_reuse_observed_within_payload"
                )
            )
            for payload in backend_payloads.values()
        )
        and bool(backend_payloads),
        "productized_runner_visible_for_prepared_backends": all(
            (
                payload.get("prepared_execution_session_runner_used") is True
                and payload.get("productized_execution_path") == "prepared_execution_session_runner"
            )
            for backend, payload in backend_payloads.items()
            if backend in {"embree", "optix"}
        ),
        "phase_table_has_prepare_query_collect_wall": all(
            row["has_prepare_query_collect_wall"] for row in phase_rows.values()
        )
        and bool(phase_rows),
        "optix_rt_hardware_gate_passed_if_required": (
            not bool(getattr(args, "require_rt_hardware", False))
            or environment.get("hardware_gate", {}).get("status") == "pass"
        ),
        "material_optix_wall_win_after_prepare_reuse": bool(
            comparisons.get("optix_over_embree_cold_plus_collect_wall_speedup", 0.0)
            >= MATERIAL_WALL_SPEEDUP_FLOOR
        ),
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    pending_review = (
        not failed_checks
        and comparisons.get("optix_over_embree_cold_plus_collect_wall_speedup", 0.0)
        >= MATERIAL_WALL_SPEEDUP_FLOOR
    )
    if pending_review:
        status = "aabb_prepare_reuse_pod_evidence_pending_2ai_not_m7"
    elif backend_payloads and not run_errors:
        status = "aabb_prepare_reuse_pod_evidence_collected_not_m7"
    else:
        status = "aabb_prepare_reuse_pod_evidence_incomplete_not_m7"
    return {
        "tool": "v3_phoenix_aabb_prepare_reuse_pod_runner",
        "status": status,
        "runner_completed": bool(backend_payloads) and not run_errors,
        "generic_capability": "aabb_candidate_stream",
        "candidate_scope": (
            "generic aabb_index_query_2d prepared-session candidate stream; "
            "contact_manifold is only the evidence harness"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_reopen_candidate_pending_2ai_review": pending_review,
        "material_wall_speedup_floor": MATERIAL_WALL_SPEEDUP_FLOOR,
        "parameters": {
            "dataset": args.dataset,
            "grid_count": args.grid_count,
            "indexed_aabb_count": args.grid_count,
            "query_aabb_count": args.grid_count,
            "resolution": args.resolution,
            "witness_capacity": args.witness_capacity or args.grid_count,
            "discovery_row_capacity": args.discovery_row_capacity
            or max(args.grid_count * 2, args.witness_capacity or args.grid_count),
            "warmup": args.warmup,
            "repeat": args.repeat,
            "backends": list(parse_backends(args.backends)),
        },
        "environment": environment,
        "phase_rows": phase_rows,
        "comparisons": comparisons,
        "checks": checks,
        "failed_checks": failed_checks,
        "run_errors": run_errors,
        "public_copy_rules": [
            "Only say this is evidence for generic AABB candidate streaming, not full contact solving.",
            "Report prepare, query, collect, and wall phases together.",
            "Report cold-plus-repeat wall before any hot-query number.",
            "Do not publish as M7 until external review and Codex consensus close.",
        ],
        "forbidden_public_wording": [
            "full contact solver speedup",
            "broad V3-over-V2 speedup",
            "paper reproduction",
            "M7-qualified before 2-AI review",
            "app-specific native contact engine",
        ],
        "goal_level_decision_audit": {
            "decision": (
                "Run or stage serious AABB prepare-reuse POD evidence through a reusable "
                "runner instead of ad hoc app timing."
            ),
            "was_i_foolish": "No. The runner keeps the candidate generic and preserves release flags false.",
            "foolish_actions": (
                "It would be foolish to quote hot-query-only speedups, to use sub-32768 toy fixtures "
                "as release evidence, or to treat contact-specific wording as a V3 engine result."
            ),
            "other_path": (
                "Continue optimizing Contact Manifold directly. That could improve one app but would "
                "not prove the reusable AABB prepared-session contract."
            ),
            "different_path_now": (
                "Use the same runner on an RTX pod, require material cold-plus-repeat wall win, "
                "then send the packet for 2-AI review before any M7 promotion."
            ),
        },
    }


def phase_summary(payload: dict[str, Any]) -> dict[str, Any]:
    phases = payload.get("run_phases") or {}
    runner_metadata = payload.get("prepared_execution_session_runner_metadata") or {}
    prepare_sec = float(phases.get("prepare_aabb_index_2d_sec", 0.0))
    query_median_sec = float(
        phases.get(
            "emit_aabb_intersection_pair_rows_2d_median_sec",
            phases.get("emit_aabb_intersection_pair_rows_2d_sec", 0.0),
        )
    )
    query_total_sec = float(
        phases.get("emit_aabb_intersection_pair_rows_2d_total_sec", query_median_sec)
    )
    collect_sec = float(phases.get("collect_k_bounded_rows_sec", 0.0))
    broadphase_wall_sec = float(phases.get("generic_aabb_broadphase_wall_sec", 0.0))
    cold_plus_collect_wall_sec = broadphase_wall_sec + collect_sec
    runner = payload.get("phoenix_v3_aabb_prepare_reuse_runner", {})
    return {
        "backend": payload.get("candidate_discovery_backend"),
        "dataset": payload.get("dataset"),
        "indexed_aabb_count": runner.get("indexed_aabb_count"),
        "query_aabb_count": runner.get("query_aabb_count"),
        "warmup": payload.get("discovery_warmup_count"),
        "repeat": payload.get("discovery_repeat_count"),
        "candidate_pairs": payload.get("aabb_candidate_pair_count"),
        "valid_rows": payload.get("valid_count"),
        "matches_cpu_reference": bool(payload.get("matches_cpu_reference")),
        "complete_candidate_coverage": bool(payload.get("complete_candidate_coverage")),
        "overflowed": bool(payload.get("overflowed")),
        "prepare_aabb_index_2d_sec": prepare_sec,
        "emit_aabb_intersection_pair_rows_2d_median_sec": query_median_sec,
        "emit_aabb_intersection_pair_rows_2d_total_sec": query_total_sec,
        "collect_k_bounded_rows_sec": collect_sec,
        "prepared_query_cache_stats": payload.get("prepared_query_cache_stats"),
        "prepared_execution_session_runner_used": bool(
            payload.get("prepared_execution_session_runner_used")
        ),
        "productized_execution_path": payload.get("productized_execution_path"),
        "prepared_execution_session_runner_runtime_executed_count": (
            runner_metadata.get("runtime_executed_count")
        ),
        "prepared_execution_session_runner_cache_hit_count": (
            runner_metadata.get("cache_hit_count")
        ),
        "python_exact_refinement_sec": float(phases.get("python_exact_refinement_sec", 0.0)),
        "generic_aabb_broadphase_wall_sec": broadphase_wall_sec,
        "cold_plus_collect_wall_sec": cold_plus_collect_wall_sec,
        "runner_wall_sec": float(runner.get("runner_wall_sec", 0.0)),
        "has_prepare_query_collect_wall": (
            prepare_sec > 0.0
            and query_median_sec > 0.0
            and collect_sec >= 0.0
            and cold_plus_collect_wall_sec > 0.0
        ),
    }


def comparison_summary(phase_rows: dict[str, dict[str, Any]]) -> dict[str, float]:
    if not {"embree", "optix"}.issubset(phase_rows):
        return {}
    embree = phase_rows["embree"]
    optix = phase_rows["optix"]
    return {
        "optix_over_embree_prepare_speedup": speedup(
            embree["prepare_aabb_index_2d_sec"],
            optix["prepare_aabb_index_2d_sec"],
        ),
        "optix_over_embree_query_median_speedup": speedup(
            embree["emit_aabb_intersection_pair_rows_2d_median_sec"],
            optix["emit_aabb_intersection_pair_rows_2d_median_sec"],
        ),
        "optix_over_embree_query_total_speedup": speedup(
            embree["emit_aabb_intersection_pair_rows_2d_total_sec"],
            optix["emit_aabb_intersection_pair_rows_2d_total_sec"],
        ),
        "optix_over_embree_collect_speedup": speedup(
            embree["collect_k_bounded_rows_sec"],
            optix["collect_k_bounded_rows_sec"],
        ),
        "optix_over_embree_broadphase_wall_speedup": speedup(
            embree["generic_aabb_broadphase_wall_sec"],
            optix["generic_aabb_broadphase_wall_sec"],
        ),
        "optix_over_embree_cold_plus_collect_wall_speedup": speedup(
            embree["cold_plus_collect_wall_sec"],
            optix["cold_plus_collect_wall_sec"],
        ),
        "optix_over_embree_runner_wall_speedup": speedup(
            embree["runner_wall_sec"],
            optix["runner_wall_sec"],
        ),
    }


def speedup(baseline_sec: float, candidate_sec: float) -> float:
    if baseline_sec <= 0.0 or candidate_sec <= 0.0:
        return 0.0
    return float(baseline_sec) / float(candidate_sec)


def write_summary(out_dir: Path, summary: dict[str, Any]) -> None:
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "README.md").write_text(render_markdown(summary), encoding="utf-8")


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 AABB Prepare-Reuse POD Evidence",
        "",
        f"Status: `{summary['status']}`.",
        "",
        "This is a generic `aabb_index_query_2d` prepared-session evidence packet.",
        "Contact Manifold is only the harness that supplies AABB rows and a CPU oracle.",
        "",
        "```text",
        f"release_authorized: {str(summary['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(summary['public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(summary['m7_promotion_authorized']).lower()}",
        "```",
        "",
        "## Parameters",
        "",
    ]
    for key, value in summary["parameters"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Phase Rows", ""])
    for backend, row in summary["phase_rows"].items():
        lines.extend(
            [
                f"### {backend}",
                "",
                f"- Prepare: `{row['prepare_aabb_index_2d_sec']:.9f}` sec",
                f"- Query median: `{row['emit_aabb_intersection_pair_rows_2d_median_sec']:.9f}` sec",
                f"- Query total: `{row['emit_aabb_intersection_pair_rows_2d_total_sec']:.9f}` sec",
                f"- Collect-k: `{row['collect_k_bounded_rows_sec']:.9f}` sec",
                f"- Broadphase wall: `{row['generic_aabb_broadphase_wall_sec']:.9f}` sec",
                f"- Cold-plus-collect wall: `{row['cold_plus_collect_wall_sec']:.9f}` sec",
                "",
            ]
        )

    lines.extend(["## Comparisons", ""])
    if summary["comparisons"]:
        for key, value in summary["comparisons"].items():
            lines.append(f"- `{key}`: `{value:.3f}x`")
    else:
        lines.append("- No Embree/OptiX comparison is available in this packet.")

    lines.extend(["", "## Checks", ""])
    for key, value in summary["checks"].items():
        lines.append(f"- `{key}`: `{str(value).lower()}`")

    if summary["failed_checks"]:
        lines.extend(["", "Failed checks:", ""])
        for key in summary["failed_checks"]:
            lines.append(f"- `{key}`")

    audit = summary["goal_level_decision_audit"]
    lines.extend(
        [
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


if __name__ == "__main__":
    raise SystemExit(main())
