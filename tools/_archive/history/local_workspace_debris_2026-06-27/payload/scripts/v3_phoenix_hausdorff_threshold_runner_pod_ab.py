#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.prepared_execution import audit_prepared_execution_session_metadata  # noqa: E402

APP = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_distance_app.py"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_hausdorff_threshold_runner_m5_pod_ab_20260622"
)

SCHEMA = "rtdl.phoenix_v3.hausdorff_threshold_runner_pod_ab.v1"
STATUS_NOT_RELEASE = "hausdorff_threshold_runner_m5_collected_not_release"
SERIOUS_POINTS_PER_SIDE_FLOOR = 1_048_576
RUNNER_VS_EMBREE_PHASE_TOTAL_FLOOR = 1.20
RUNNER_VS_EMBREE_WRAPPER_WALL_FLOOR = 1.20
RUNNER_VS_LEGACY_PHASE_TOTAL_FLOOR = 0.98
RUNNER_VS_LEGACY_WRAPPER_WALL_FLOOR = 0.98
EMBREE = "same_contract_embree"
LEGACY = "legacy_app_front_door_prepared_optix"
RUNNER = "productized_prepared_execution_runner"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = run_packet(args)
    (args.output_dir / "summary.json").write_text(
        json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "README.md").write_text(_readme(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Focused Phoenix V3 Hausdorff POD A/B: productized prepared-execution "
            "runner, legacy app-front-door prepared OptiX, and same-contract Embree. "
            "This never authorizes release or all-app reruns."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--copies", type=int, default=262_144)
    parser.add_argument("--threshold", type=float, default=0.4)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=1800)
    parser.add_argument("--heartbeat-sec", type=float, default=30.0)
    parser.add_argument("--require-rt-hardware", action="store_true")
    parser.add_argument("--allow-non-serious-local-smoke", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    point_count_per_side = int(args.copies) * 4
    if (
        point_count_per_side < SERIOUS_POINTS_PER_SIDE_FLOOR
        and not bool(args.allow_non_serious_local_smoke)
    ):
        raise SystemExit(
            "copies is below the Phoenix V3 Hausdorff serious scale floor; pass "
            "--allow-non-serious-local-smoke only for local smoke tests"
        )

    environment = environment_payload(require_rt_hardware=bool(args.require_rt_hardware))
    if bool(args.require_rt_hardware) and environment["hardware_gate"].get("status") != "pass":
        payload = build_payload(args, environment=environment, variant_payloads={}, run_errors={
            "optix_hardware_gate": environment["hardware_gate"].get("fail_closed_reason")
            or "OptiX RT hardware gate failed"
        })
        return payload

    variant_payloads: dict[str, dict[str, Any]] = {}
    run_errors: dict[str, str] = {}
    for variant in (EMBREE, LEGACY, RUNNER):
        try:
            print(
                f"[phoenix-v3-hausdorff-runner-ab] variant={variant} "
                f"points_per_side={point_count_per_side} repeat={int(args.repeat)}",
                flush=True,
            )
            payload = run_variant(args, variant=variant)
            variant_payloads[variant] = payload
            (args.output_dir / f"{variant}.json").write_text(
                json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except Exception as exc:  # pragma: no cover - hardware/environment dependent
            run_errors[variant] = repr(exc)
            (args.output_dir / f"{variant}.error.txt").write_text(
                repr(exc) + "\n",
                encoding="utf-8",
            )
    return build_payload(args, environment=environment, variant_payloads=variant_payloads, run_errors=run_errors)


def run_variant(args: argparse.Namespace, *, variant: str) -> dict[str, Any]:
    command = build_command(args, variant=variant)
    stdout_path = args.output_dir / f"{variant}.stdout.json"
    stderr_path = args.output_dir / f"{variant}.stderr.txt"
    if bool(args.dry_run):
        return {
            "variant": variant,
            "status": "dry_run",
            "command": command,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "all_app_rerun_authorized": False,
        }

    started = time.perf_counter()
    process = subprocess.Popen(
        [str(part) for part in command],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    deadline = started + float(args.timeout_sec)
    next_heartbeat = started + float(args.heartbeat_sec)
    timed_out = False
    while process.poll() is None:
        now = time.perf_counter()
        if now >= deadline:
            timed_out = True
            process.kill()
            break
        if now >= next_heartbeat:
            print(
                f"[phoenix-v3-hausdorff-runner-ab] heartbeat variant={variant} "
                f"elapsed={now - started:.1f}s",
                flush=True,
            )
            next_heartbeat = now + float(args.heartbeat_sec)
        time.sleep(0.2)
    stdout, stderr = process.communicate()
    wrapper_wall_sec = time.perf_counter() - started
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")

    parsed: dict[str, Any] | None = None
    parse_error = None
    try:
        loaded = json.loads(stdout or "")
        if isinstance(loaded, dict):
            parsed = loaded
        else:
            parse_error = "stdout JSON is not an object"
    except json.JSONDecodeError as exc:
        parse_error = str(exc)

    phases = dict(parsed.get("run_phases", {})) if parsed else {}
    repeat_protocol = dict(parsed.get("repeat_protocol", {})) if parsed else {}
    runner = dict(parsed.get("prepared_execution_session_runner", {})) if parsed else {}
    step3_audit = audit_hausdorff_directed_runner(runner)
    return {
        "variant": variant,
        "status": "ok" if process.returncode == 0 and parsed is not None and not timed_out else "failed",
        "returncode": process.returncode,
        "timed_out": timed_out,
        "stdout_json_parse_error": parse_error,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "command": command,
        "wrapper_wall_sec": wrapper_wall_sec,
        "point_count_a": parsed.get("point_count_a") if parsed else None,
        "point_count_b": parsed.get("point_count_b") if parsed else None,
        "within_threshold": parsed.get("within_threshold") if parsed else None,
        "matches_oracle": parsed.get("matches_oracle") if parsed else None,
        "oracle_decision_matches": parsed.get("oracle_decision_matches") if parsed else None,
        "oracle_identity_matches": parsed.get("oracle_identity_matches") if parsed else None,
        "oracle_within_threshold": parsed.get("oracle_within_threshold") if parsed else None,
        "native_continuation_backend": parsed.get("native_continuation_backend") if parsed else None,
        "rt_core_accelerated": parsed.get("rt_core_accelerated") if parsed else None,
        "run_phases": phases,
        "repeat_protocol": repeat_protocol,
        "query_sec": phases.get("query_fixed_radius_threshold_reached_count_sec"),
        "query_total_sec": repeat_protocol.get("measured_query_total_sec"),
        "runner_outer_prepare_sec": phases.get("runner_outer_prepare_sec"),
        "runner_outer_cache_load_sec": phases.get("runner_outer_cache_load_sec"),
        "runner_native_prepare_sec": phases.get("runner_native_prepare_sec"),
        "runner_outer_query_sec": phases.get("runner_outer_query_sec"),
        "runner_outer_query_total_sec": phases.get("runner_outer_query_total_sec"),
        "scene_prepare_sec": phases.get("scene_prepare_sec"),
        "phase_total_sec": phase_total(phases),
        "prepared_execution_session_runner": runner,
        "step3_audit": step3_audit,
        "step3_audit_status": step3_audit["status"],
        "step3_residency_default_ready": step3_audit["all_directed_legs_step3_ready"],
        "step3_audit_missing_fields": step3_audit["missing_step3_fields_by_leg"],
        "claim_boundary": parsed.get("claim_boundary") if parsed else None,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_hausdorff_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_rerun_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_external_buffer_claim_authorized": False,
    }


def build_command(args: argparse.Namespace, *, variant: str) -> list[str]:
    if variant == EMBREE:
        backend = "embree"
        mode = "directed_threshold_prepared"
    elif variant == LEGACY:
        backend = "optix"
        mode = "directed_threshold_prepared"
    elif variant == RUNNER:
        backend = "optix"
        mode = "directed_threshold_prepared_runner"
    else:
        raise ValueError(f"unsupported variant: {variant}")
    command = [
        sys.executable,
        str(APP),
        "--backend",
        backend,
        "--optix-summary-mode",
        mode,
        "--hausdorff-threshold",
        str(float(args.threshold)),
        "--copies",
        str(int(args.copies)),
        "--repeat",
        str(int(args.repeat)),
        "--warmup",
        str(int(args.warmup)),
    ]
    if backend == "optix":
        command.append("--require-rt-core")
    return command


def build_payload(
    args: argparse.Namespace,
    *,
    environment: dict[str, Any],
    variant_payloads: dict[str, dict[str, Any]],
    run_errors: dict[str, str],
) -> dict[str, Any]:
    comparisons = build_comparisons(variant_payloads)
    failed_checks = failed_checks_for(args, environment, variant_payloads, run_errors, comparisons)
    runner_step3_audit = variant_payloads.get(RUNNER, {}).get("step3_audit", {})
    summary = {
        "schema": SCHEMA,
        "status": STATUS_NOT_RELEASE,
        "failed_checks": failed_checks,
        "serious_points_per_side_floor": SERIOUS_POINTS_PER_SIDE_FLOOR,
        "points_per_side": int(args.copies) * 4,
        "copies": int(args.copies),
        "threshold": float(args.threshold),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "variant_count": len(variant_payloads),
        "comparisons": comparisons,
        "runner_step3_audit": runner_step3_audit,
        "runner_step3_residency_default_ready": runner_step3_audit.get(
            "all_directed_legs_step3_ready"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_hausdorff_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_rerun_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_external_buffer_claim_authorized": False,
    }
    return {
        "schema": SCHEMA,
        "summary": summary,
        "environment": environment,
        "variants": variant_payloads,
        "comparisons": comparisons,
        "run_errors": run_errors,
        "failed_checks": failed_checks,
    }


def failed_checks_for(
    args: argparse.Namespace,
    environment: dict[str, Any],
    variants: dict[str, dict[str, Any]],
    run_errors: dict[str, str],
    comparisons: dict[str, Any],
) -> list[str]:
    failed: list[str] = []
    points_per_side = int(args.copies) * 4
    if points_per_side < SERIOUS_POINTS_PER_SIDE_FLOOR and not bool(args.allow_non_serious_local_smoke):
        failed.append("points_per_side_below_serious_floor")
    if int(args.repeat) < 5:
        failed.append("repeat_below_repeat5_material_probe_floor")
    if bool(args.require_rt_hardware) and environment["hardware_gate"].get("status") != "pass":
        failed.append("optix_hardware_gate_failed")
    if run_errors:
        failed.append("variant_execution_errors_present")
    for variant in (EMBREE, LEGACY, RUNNER):
        row = variants.get(variant)
        if row is None:
            failed.append(f"missing_variant_{variant}")
            continue
        if row.get("status") not in {"ok", "dry_run"}:
            failed.append(f"variant_failed_{variant}")
        if row.get("status") == "ok" and row.get("matches_oracle") is not True:
            failed.append(f"oracle_mismatch_{variant}")
    runner = variants.get(RUNNER, {}).get("prepared_execution_session_runner", {})
    if variants.get(RUNNER, {}).get("status") == "ok":
        if runner.get("used") is not True:
            failed.append("runner_metadata_missing")
        if runner.get("both_directed_legs_runtime_executed") is not True:
            failed.append("runner_did_not_execute_both_directed_legs")
        if runner.get("both_directed_legs_runtime_trunk_end_to_end") is not True:
            failed.append("runner_not_end_to_end")
        if runner.get("both_directed_legs_no_threshold_rows_materialized_on_host") is not True:
            failed.append("runner_threshold_rows_materialized_on_host")
        if runner.get("both_directed_legs_internal_device_residency_between_rtdl_phases") is not True:
            failed.append("runner_internal_residency_not_reported")
        step3_audit = variants.get(RUNNER, {}).get("step3_audit", {})
        if step3_audit.get("all_directed_legs_step3_ready") is not True:
            failed.append("runner_step3_audit_not_ready")
    runner_vs_legacy = comparisons.get("runner_vs_legacy", {})
    if isinstance(runner_vs_legacy.get("phase_total_speedup"), (int, float)):
        if float(runner_vs_legacy["phase_total_speedup"]) < RUNNER_VS_LEGACY_PHASE_TOTAL_FLOOR:
            failed.append("runner_regressed_vs_legacy_phase_total")
    if isinstance(runner_vs_legacy.get("wrapper_wall_speedup"), (int, float)):
        if float(runner_vs_legacy["wrapper_wall_speedup"]) < RUNNER_VS_LEGACY_WRAPPER_WALL_FLOOR:
            failed.append("runner_regressed_vs_legacy_wrapper_wall")
    runner_vs_embree = comparisons.get("runner_vs_embree", {})
    if isinstance(runner_vs_embree.get("phase_total_speedup"), (int, float)):
        if float(runner_vs_embree["phase_total_speedup"]) < RUNNER_VS_EMBREE_PHASE_TOTAL_FLOOR:
            failed.append("runner_below_embree_phase_total_material_floor")
    if isinstance(runner_vs_embree.get("wrapper_wall_speedup"), (int, float)):
        if float(runner_vs_embree["wrapper_wall_speedup"]) < RUNNER_VS_EMBREE_WRAPPER_WALL_FLOOR:
            failed.append("runner_below_embree_wrapper_wall_material_floor")
    return failed


def build_comparisons(variants: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "runner_vs_legacy": compare_speed(variants.get(LEGACY), variants.get(RUNNER)),
        "runner_vs_embree": compare_speed(variants.get(EMBREE), variants.get(RUNNER)),
        "legacy_vs_embree": compare_speed(variants.get(EMBREE), variants.get(LEGACY)),
    }


def compare_speed(baseline: dict[str, Any] | None, candidate: dict[str, Any] | None) -> dict[str, Any]:
    if not baseline or not candidate:
        return {"available": False}
    return {
        "available": True,
        "baseline_variant": baseline.get("variant"),
        "candidate_variant": candidate.get("variant"),
        "query_speedup": ratio(baseline.get("query_sec"), candidate.get("query_sec")),
        "phase_total_speedup": ratio(baseline.get("phase_total_sec"), candidate.get("phase_total_sec")),
        "wrapper_wall_speedup": ratio(baseline.get("wrapper_wall_sec"), candidate.get("wrapper_wall_sec")),
        "baseline_query_sec": baseline.get("query_sec"),
        "candidate_query_sec": candidate.get("query_sec"),
        "baseline_phase_total_sec": baseline.get("phase_total_sec"),
        "candidate_phase_total_sec": candidate.get("phase_total_sec"),
        "baseline_wrapper_wall_sec": baseline.get("wrapper_wall_sec"),
        "candidate_wrapper_wall_sec": candidate.get("wrapper_wall_sec"),
    }


def audit_hausdorff_directed_runner(runner: dict[str, Any]) -> dict[str, Any]:
    directed_audit: dict[str, dict[str, Any]] = {}
    missing_by_leg: dict[str, tuple[str, ...]] = {}
    for leg in ("directed_a_to_b", "directed_b_to_a"):
        metadata = runner.get(leg)
        if isinstance(metadata, dict):
            audit = audit_prepared_execution_session_metadata(metadata)
        else:
            audit = {
                "status": "incomplete_step3_audit",
                "step3_residency_default_ready": False,
                "missing_step3_fields": ("directed_runner_metadata",),
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "all_app_rerun_authorized": False,
            }
        directed_audit[leg] = audit
        missing_by_leg[leg] = tuple(audit.get("missing_step3_fields", ()))
    all_ready = all(
        audit.get("step3_residency_default_ready") is True
        for audit in directed_audit.values()
    )
    return {
        "status": "accept_step3_ready" if all_ready else "incomplete_step3_audit",
        "all_directed_legs_step3_ready": all_ready,
        "directed_a_to_b": directed_audit["directed_a_to_b"],
        "directed_b_to_a": directed_audit["directed_b_to_a"],
        "missing_step3_fields_by_leg": missing_by_leg,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_rerun_authorized": False,
    }


def phase_total(phases: dict[str, Any]) -> float | None:
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


def ratio(numerator: Any, denominator: Any) -> float | None:
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        return None
    numerator_value = float(numerator)
    denominator_value = float(denominator)
    if denominator_value <= 0.0 or not math.isfinite(numerator_value) or not math.isfinite(denominator_value):
        return None
    return numerator_value / denominator_value


def environment_payload(*, require_rt_hardware: bool) -> dict[str, Any]:
    hardware_gate = {"status": "not_required", "require_rt_hardware": bool(require_rt_hardware)}
    if require_rt_hardware:
        try:
            from scripts import v3_optix_hardware_gate

            hardware_gate = v3_optix_hardware_gate.build_payload(
                require_rt_hardware=True,
                sample_nvidia_smi=None,
            )
        except Exception as exc:  # pragma: no cover - environment dependent
            hardware_gate = {
                "status": "fail",
                "require_rt_hardware": True,
                "fail_closed_reason": repr(exc),
            }
    return {
        "platform": platform.platform(),
        "python": sys.version,
        "executable": sys.executable,
        "repo_root": str(ROOT),
        "hardware_gate": hardware_gate,
        "nvidia_smi": run_text(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ],
        ),
    }


def run_text(command: list[str], timeout_sec: int = 10) -> str:
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


def _readme(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    comparisons = summary["comparisons"]
    runner_vs_legacy = comparisons.get("runner_vs_legacy", {})
    runner_vs_embree = comparisons.get("runner_vs_embree", {})
    return "\n".join(
        [
            "# Phoenix V3 Hausdorff Threshold Runner POD A/B",
            "",
            f"Status: `{summary['status']}`",
            "",
            "This focused packet is not release authorization and not an all-app rerun.",
            "",
            "## Configuration",
            "",
            f"- Points per side: `{summary['points_per_side']}`",
            f"- Threshold: `{summary['threshold']}`",
            f"- Repeat/warmup: `{summary['repeat']}` / `{summary['warmup']}`",
            "",
            "## Checks",
            "",
            f"- Failed checks: `{summary['failed_checks']}`",
            f"- Runner vs legacy phase-total speedup: `{runner_vs_legacy.get('phase_total_speedup')}`",
            f"- Runner vs legacy wrapper-wall speedup: `{runner_vs_legacy.get('wrapper_wall_speedup')}`",
            f"- Runner vs Embree phase-total speedup: `{runner_vs_embree.get('phase_total_speedup')}`",
            f"- Runner Step-3 audit ready: `{summary.get('runner_step3_residency_default_ready')}`",
            "",
            "## Non-Authorization",
            "",
            "Release, public speedup wording, broad V3-over-V2 wording, all-app rerun, "
            "whole-Hausdorff claims, true zero-copy claims, and V4 external-buffer claims "
            "remain false.",
            "",
        ]
    )


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


if __name__ == "__main__":
    raise SystemExit(main())
