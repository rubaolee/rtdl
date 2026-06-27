from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "examples" / "current" / "research_benchmarks" / "robot_collision" / "rtdl_robot_collision_benchmark_app.py"
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_robot_collision_flag_stream_no_probe_paired_20260621"
)
EXPECTED_CONTRACT = "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run Phoenix V3 robot collision flag-stream evidence with correctness "
            "validation separated from no-probe-reference performance timing."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset", default="scaled")
    parser.add_argument("--pose-count", type=int, default=8192)
    parser.add_argument("--obstacle-count", type=int, default=2048)
    parser.add_argument("--link-count", type=int, default=2)
    parser.add_argument("--sample-count", type=int, default=5)
    parser.add_argument("--timed-repeats", type=int, default=101)
    parser.add_argument("--timed-warmup", type=int, default=5)
    parser.add_argument("--validation-repeats", type=int, default=5)
    parser.add_argument("--validation-warmup", type=int, default=1)
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--timeout-sec", type=int, default=900)
    parser.add_argument("--heartbeat-sec", type=float, default=30.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    _validate_args(args)

    planned = _planned_commands(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        payload = _base_payload(args=args)
        payload.update(
            {
                "status": "dry_run",
                "planned_commands": planned,
                "validation_rows": [],
                "timed_samples": [],
                "comparison": None,
            }
        )
        _write_json(args.output_dir / "summary.json", payload)
        print(json.dumps({"status": "dry_run", "planned_command_count": len(planned)}, indent=2))
        return 0

    validation_rows: list[dict[str, Any]] = []
    if not args.skip_validation:
        for backend, mode in (("embree", "embree_prepared_buffers"), ("optix", "optix_prepared_device_buffers")):
            validation_rows.append(
                _run_app_row(
                    args=args,
                    mode=mode,
                    backend=backend,
                    stem=f"validation_{backend}",
                    repeats=args.validation_repeats,
                    warmup=args.validation_warmup,
                    no_probe_reference=False,
                )
            )

    timed_samples: list[dict[str, Any]] = []
    for sample in range(1, args.sample_count + 1):
        sample_rows = []
        for backend, mode in (("embree", "embree_prepared_buffers"), ("optix", "optix_prepared_device_buffers")):
            sample_rows.append(
                _run_app_row(
                    args=args,
                    mode=mode,
                    backend=backend,
                    stem=f"timed_sample{sample:02d}_{backend}",
                    repeats=args.timed_repeats,
                    warmup=args.timed_warmup,
                    no_probe_reference=True,
                )
            )
        timed_samples.append({"sample_index": sample, "rows": sample_rows, "pair": _compare_pair(sample_rows)})

    comparison = _summarize(validation_rows=validation_rows, timed_samples=timed_samples)
    payload = _base_payload(args=args)
    payload.update(
        {
            "status": "ok",
            "planned_commands": planned,
            "validation_rows": validation_rows,
            "timed_samples": timed_samples,
            "comparison": comparison,
        }
    )
    _write_json(args.output_dir / "summary.json", payload)
    _write_markdown(args.output_dir / "summary.md", payload)
    print(
        json.dumps(
            {
                "status": "ok",
                "output_dir": str(args.output_dir),
                "validation_status": comparison["validation_status"],
                "timed_status": comparison["timed_status"],
                "mean_wrapper_embree_over_optix_no_probe": comparison["aggregate_ratios"].get(
                    "wrapper_elapsed_embree_over_optix_mean"
                ),
                "mean_tail_embree_over_optix_no_probe": comparison["aggregate_ratios"].get(
                    "tail_total_run_embree_over_optix_mean"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    positive_fields = (
        "pose_count",
        "obstacle_count",
        "link_count",
        "sample_count",
        "timed_repeats",
        "validation_repeats",
        "timeout_sec",
    )
    for field in positive_fields:
        if int(getattr(args, field)) <= 0:
            raise ValueError(f"--{field.replace('_', '-')} must be positive")
    if args.timed_warmup < 0 or args.timed_warmup >= args.timed_repeats:
        raise ValueError("--timed-warmup must be non-negative and smaller than --timed-repeats")
    if args.validation_warmup < 0 or args.validation_warmup >= args.validation_repeats:
        raise ValueError("--validation-warmup must be non-negative and smaller than --validation-repeats")
    if args.heartbeat_sec <= 0:
        raise ValueError("--heartbeat-sec must be positive")


def _planned_commands(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not args.skip_validation:
        for backend, mode in (("embree", "embree_prepared_buffers"), ("optix", "optix_prepared_device_buffers")):
            rows.append(
                {
                    "kind": "validation",
                    "backend": backend,
                    "command": _app_command(
                        args=args,
                        mode=mode,
                        repeats=args.validation_repeats,
                        warmup=args.validation_warmup,
                        no_probe_reference=False,
                        json_out=Path(f"validation_{backend}.json"),
                    ),
                }
            )
    for sample in range(1, args.sample_count + 1):
        for backend, mode in (("embree", "embree_prepared_buffers"), ("optix", "optix_prepared_device_buffers")):
            rows.append(
                {
                    "kind": "timed_no_probe",
                    "sample_index": sample,
                    "backend": backend,
                    "command": _app_command(
                        args=args,
                        mode=mode,
                        repeats=args.timed_repeats,
                        warmup=args.timed_warmup,
                        no_probe_reference=True,
                        json_out=Path(f"timed_sample{sample:02d}_{backend}.json"),
                    ),
                }
            )
    return rows


def _base_payload(*, args: argparse.Namespace) -> dict[str, Any]:
    return {
        "version": "phoenix_v3_robot_collision_flag_stream_no_probe_paired_20260621",
        "goal": "Phoenix V3 collision_flag_stream probe-reference separation evidence",
        "parameters": {
            "dataset": args.dataset,
            "pose_count": int(args.pose_count),
            "obstacle_count": int(args.obstacle_count),
            "link_count": int(args.link_count),
            "sample_count": int(args.sample_count),
            "timed_repeats": int(args.timed_repeats),
            "timed_warmup": int(args.timed_warmup),
            "validation_repeats": int(args.validation_repeats),
            "validation_warmup": int(args.validation_warmup),
            "skip_validation": bool(args.skip_validation),
        },
        "contract": EXPECTED_CONTRACT,
        "evidence_protocol": {
            "validation_rows": "CPU probe-reference validation is run separately from performance timing.",
            "timed_rows": "Timed rows pass --no-probe-reference and therefore exclude the CPU oracle.",
            "same_contract_requirement": "Validation and timed rows must keep the prepared grouped segment any-hit flag-stream contract and case shape.",
            "m7_requirement": "Promotion still requires external review; this script does not authorize release wording.",
        },
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "robot_planning_speedup_claim_authorized": False,
            "continuous_collision_claim_authorized": False,
            "exact_solid_collision_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "performance_timing_excludes_probe_reference": True,
        },
        "environment": _environment_snapshot(),
    }


def _app_command(
    *,
    args: argparse.Namespace,
    mode: str,
    repeats: int,
    warmup: int,
    no_probe_reference: bool,
    json_out: Path,
) -> list[str]:
    command = [
        sys.executable,
        str(APP),
        "--mode",
        mode,
        "--dataset",
        str(args.dataset),
        "--pose-count",
        str(args.pose_count),
        "--obstacle-count",
        str(args.obstacle_count),
        "--link-count",
        str(args.link_count),
        "--repeats",
        str(repeats),
        "--warmup",
        str(warmup),
        "--json-out",
        str(json_out),
    ]
    if no_probe_reference:
        command.append("--no-probe-reference")
    return command


def _run_app_row(
    *,
    args: argparse.Namespace,
    mode: str,
    backend: str,
    stem: str,
    repeats: int,
    warmup: int,
    no_probe_reference: bool,
) -> dict[str, Any]:
    json_path = args.output_dir / f"{stem}.json"
    stdout_path = args.output_dir / f"{stem}.stdout.txt"
    stderr_path = args.output_dir / f"{stem}.stderr.txt"
    command = _app_command(
        args=args,
        mode=mode,
        repeats=repeats,
        warmup=warmup,
        no_probe_reference=no_probe_reference,
        json_out=json_path,
    )
    started = time.perf_counter()
    print(f"[robot-collision] start {stem} repeats={repeats} warmup={warmup}", flush=True)
    with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open("w", encoding="utf-8") as stderr_file:
        process = subprocess.Popen(command, cwd=str(ROOT), text=True, stdout=stdout_file, stderr=stderr_file)
        last_heartbeat = started
        timed_out = False
        while True:
            returncode = process.poll()
            now = time.perf_counter()
            elapsed = now - started
            if returncode is not None:
                break
            if elapsed >= args.timeout_sec:
                timed_out = True
                process.kill()
                returncode = process.wait()
                break
            if now - last_heartbeat >= args.heartbeat_sec:
                print(f"[robot-collision] heartbeat {stem} elapsed={elapsed:.1f}s", flush=True)
                last_heartbeat = now
            time.sleep(0.25)
    wrapper_elapsed = time.perf_counter() - started
    print(f"[robot-collision] done {stem} rc={returncode} elapsed={wrapper_elapsed:.3f}s", flush=True)
    payload = _load_json(json_path)
    compact = _compact_payload(payload) if isinstance(payload, dict) else None
    status = "timeout" if timed_out else ("ok" if returncode == 0 and compact is not None else "fail")
    row = {
        "stem": stem,
        "backend": backend,
        "mode": mode,
        "kind": "timed_no_probe" if no_probe_reference else "validation",
        "status": status,
        "returncode": returncode,
        "wrapper_elapsed_sec": wrapper_elapsed,
        "timeout_sec": int(args.timeout_sec),
        "command": command,
        "json_path": str(json_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "stdout_bytes": stdout_path.stat().st_size if stdout_path.exists() else 0,
        "stderr_bytes": stderr_path.stat().st_size if stderr_path.exists() else 0,
        "no_probe_reference": bool(no_probe_reference),
        "payload": compact,
    }
    if status != "ok":
        row["stderr_tail"] = _tail(stderr_path)
    return row


def _compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    reuse = dict(payload["reuse_metadata"])
    case_shape = dict(payload["case_shape"])
    tail_phases = dict(payload["tail_medians"]["phase_timing_seconds"])
    summary = dict(payload["run_summary"])
    total_summary = dict(summary["total_run_seconds"])
    phase_summary = {
        str(name): dict(value)
        for name, value in dict(summary["phase_timing_seconds"]).items()
    }
    runs = [dict(row) for row in payload.get("runs", []) if not bool(row.get("is_warmup"))]
    signatures = sorted({str(row.get("flags_signature")) for row in runs if row.get("flags_signature") is not None})
    signature_hashes = [_sha256_text(value) for value in signatures]
    flagged_counts = sorted({int(row["flagged_group_count"]) for row in runs if "flagged_group_count" in row})
    return {
        "backend": payload["backend"],
        "mode": payload["mode"],
        "contract": payload["contract"],
        "dataset": payload["dataset"],
        "case_shape": case_shape,
        "lowering_mode": payload.get("lowering_mode"),
        "group_metadata_materialized": bool(payload.get("group_metadata_materialized")),
        "app_lowering_seconds": float(payload["app_lowering_seconds"]),
        "probe_reference_signature_hash": (
            None
            if payload.get("probe_reference_signature") is None
            else _sha256_text(str(payload.get("probe_reference_signature")))
        ),
        "probe_reference_validated": bool(reuse["probe_reference_validated"]),
        "probe_reference_seconds": reuse.get("probe_reference_seconds"),
        "all_measured_runs_match_probe_reference": reuse.get("all_measured_runs_match_probe_reference"),
        "all_measured_counts_match_probe_reference": reuse.get("all_measured_counts_match_probe_reference"),
        "all_run_signatures_identical": bool(reuse["all_run_signatures_identical"]),
        "host_query_output_buffers_reused": bool(reuse["host_query_output_buffers_reused"]),
        "native_query_output_buffers_reused": bool(reuse["native_query_output_buffers_reused"]),
        "measured_run_count": int(reuse["measured_run_count"]),
        "repeat_count": int(reuse["repeat_count"]),
        "warmup_rows_dropped": int(reuse["warmup_rows_dropped"]),
        "tail_total_run_median_sec": float(payload["tail_medians"]["total_run_seconds"]),
        "tail_phase_median_sec": {str(name): float(value) for name, value in tail_phases.items()},
        "total_run_window_sec": float(total_summary["total_sec"]),
        "phase_window_sec": {name: float(values["total_sec"]) for name, values in phase_summary.items()},
        "flagged_group_count_values": flagged_counts,
        "measured_signature_hashes": signature_hashes,
        "prepared_scene_reused": bool(reuse["prepared_scene_reused"]),
        "query_input_sequences_reused": bool(reuse["query_input_sequences_reused"]),
        "prepared_run_indices_strictly_increase": bool(reuse["prepared_run_indices_strictly_increase"]),
    }


def _compare_pair(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_backend = {row["backend"]: row for row in rows}
    embree = by_backend.get("embree")
    optix = by_backend.get("optix")
    if embree is None or optix is None or embree["payload"] is None or optix["payload"] is None:
        return {"status": "missing_pair"}
    e = embree["payload"]
    o = optix["payload"]
    return {
        "status": "ok",
        "same_contract": e["contract"] == o["contract"] == EXPECTED_CONTRACT,
        "same_case_shape": e["case_shape"] == o["case_shape"],
        "same_flagged_group_counts": e["flagged_group_count_values"] == o["flagged_group_count_values"],
        "same_measured_signature_hashes": e["measured_signature_hashes"] == o["measured_signature_hashes"],
        "both_probe_reference_disabled": (
            e["probe_reference_validated"] is False and o["probe_reference_validated"] is False
        ),
        "embree_tail_total_run_median_sec": e["tail_total_run_median_sec"],
        "optix_tail_total_run_median_sec": o["tail_total_run_median_sec"],
        "tail_total_run_embree_over_optix": _ratio(
            e["tail_total_run_median_sec"], o["tail_total_run_median_sec"]
        ),
        "embree_total_run_window_sec": e["total_run_window_sec"],
        "optix_total_run_window_sec": o["total_run_window_sec"],
        "total_run_window_embree_over_optix": _ratio(e["total_run_window_sec"], o["total_run_window_sec"]),
        "embree_wrapper_elapsed_sec": embree["wrapper_elapsed_sec"],
        "optix_wrapper_elapsed_sec": optix["wrapper_elapsed_sec"],
        "wrapper_elapsed_embree_over_optix": _ratio(embree["wrapper_elapsed_sec"], optix["wrapper_elapsed_sec"]),
        "embree_traversal_median_sec": e["tail_phase_median_sec"].get("traversal"),
        "optix_traversal_median_sec": o["tail_phase_median_sec"].get("traversal"),
        "traversal_embree_over_optix": _ratio(
            e["tail_phase_median_sec"].get("traversal"),
            o["tail_phase_median_sec"].get("traversal"),
        ),
    }


def _summarize(*, validation_rows: list[dict[str, Any]], timed_samples: list[dict[str, Any]]) -> dict[str, Any]:
    validation_payloads = [row["payload"] for row in validation_rows if row.get("payload") is not None]
    timed_pairs = [sample["pair"] for sample in timed_samples if sample.get("pair", {}).get("status") == "ok"]
    validation_ok = bool(validation_rows) and all(row.get("status") == "ok" for row in validation_rows)
    validation_same_contract = bool(validation_payloads) and all(
        row["contract"] == EXPECTED_CONTRACT for row in validation_payloads
    )
    validation_same_shape = len({json.dumps(row["case_shape"], sort_keys=True) for row in validation_payloads}) <= 1
    validation_all_match_reference = bool(validation_payloads) and all(
        row["all_measured_runs_match_probe_reference"] is True for row in validation_payloads
    )
    validation_signature_hashes = sorted(
        {hash_value for row in validation_payloads for hash_value in row["measured_signature_hashes"]}
    )
    timed_signature_hashes = sorted(
        {
            hash_value
            for sample in timed_samples
            for row in sample.get("rows", [])
            if row.get("payload") is not None
            for hash_value in row["payload"]["measured_signature_hashes"]
        }
    )
    aggregate_ratios = {
        "tail_total_run_embree_over_optix": _series(
            pair.get("tail_total_run_embree_over_optix") for pair in timed_pairs
        ),
        "total_run_window_embree_over_optix": _series(
            pair.get("total_run_window_embree_over_optix") for pair in timed_pairs
        ),
        "wrapper_elapsed_embree_over_optix": _series(
            pair.get("wrapper_elapsed_embree_over_optix") for pair in timed_pairs
        ),
        "traversal_embree_over_optix": _series(pair.get("traversal_embree_over_optix") for pair in timed_pairs),
    }
    flat_aggregates = {
        f"{name}_{stat}": value
        for name, summary in aggregate_ratios.items()
        for stat, value in summary.items()
    }
    all_timed_pairs_ok = len(timed_pairs) == len(timed_samples) and all(
        pair["same_contract"]
        and pair["same_case_shape"]
        and pair["same_flagged_group_counts"]
        and pair["same_measured_signature_hashes"]
        and pair["both_probe_reference_disabled"]
        for pair in timed_pairs
    )
    all_wrapper_above_1 = all(
        (pair.get("wrapper_elapsed_embree_over_optix") or 0.0) > 1.0 for pair in timed_pairs
    )
    return {
        "validation_status": "pass" if validation_ok and validation_all_match_reference else "skipped_or_fail",
        "validation_same_contract": validation_same_contract,
        "validation_same_shape": validation_same_shape,
        "validation_all_measured_runs_match_probe_reference": validation_all_match_reference,
        "timed_status": "pass" if all_timed_pairs_ok else "fail",
        "timed_pair_count": len(timed_pairs),
        "all_timed_pairs_same_contract_shape_signature_counts": all_timed_pairs_ok,
        "timed_rows_probe_reference_disabled": all(
            pair.get("both_probe_reference_disabled") is True for pair in timed_pairs
        ),
        "validation_signature_hashes": validation_signature_hashes,
        "timed_signature_hashes": sorted(set(timed_signature_hashes)),
        "validation_and_timed_signatures_overlap": bool(
            set(validation_signature_hashes).intersection(timed_signature_hashes)
        ),
        "all_wrapper_no_probe_pairs_above_1x": all_wrapper_above_1,
        "aggregate_ratios": flat_aggregates,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "review_required_before_m7": True,
    }


def _series(values: Any) -> dict[str, Any]:
    numbers = [float(value) for value in values if isinstance(value, (int, float)) and math.isfinite(float(value))]
    if not numbers:
        return {"count": 0, "min": None, "mean": None, "max": None, "stddev": None}
    mean = sum(numbers) / len(numbers)
    variance = sum((value - mean) ** 2 for value in numbers) / len(numbers)
    return {
        "count": len(numbers),
        "min": min(numbers),
        "mean": mean,
        "max": max(numbers),
        "stddev": math.sqrt(variance),
    }


def _ratio(numerator: Any, denominator: Any) -> float | None:
    if not isinstance(numerator, (int, float)) or not isinstance(denominator, (int, float)):
        return None
    if denominator == 0:
        return None
    return float(numerator) / float(denominator)


def _environment_snapshot() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "python": sys.version.replace("\n", " "),
        "git_head": _run_text(["git", "rev-parse", "HEAD"]).strip(),
        "git_status_short": _run_text(["git", "status", "--short"]).splitlines(),
        "nvidia_smi": _run_text(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ]
        ).strip(),
    }


def _run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(command, cwd=str(ROOT), text=True, capture_output=True, check=False, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return (completed.stdout or "") + (completed.stderr or "")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    comparison = payload["comparison"]
    aggregate = comparison["aggregate_ratios"]
    lines = [
        "# Phoenix V3 Robot Collision Flag-Stream No-Probe Paired Evidence",
        "",
        "Status: evidence packet, not a release claim.",
        "",
        "This packet separates CPU probe-reference validation from performance timing.",
        "Timed rows use `--no-probe-reference`; validation rows run the probe reference separately.",
        "",
        "## Summary",
        "",
        f"- validation status: `{comparison['validation_status']}`",
        f"- timed status: `{comparison['timed_status']}`",
        f"- timed pair count: {comparison['timed_pair_count']}",
        f"- mean no-probe wrapper Embree/OptiX: {aggregate.get('wrapper_elapsed_embree_over_optix_mean')}",
        f"- weakest no-probe wrapper Embree/OptiX: {aggregate.get('wrapper_elapsed_embree_over_optix_min')}",
        f"- mean no-probe tail Embree/OptiX: {aggregate.get('tail_total_run_embree_over_optix_mean')}",
        f"- mean traversal Embree/OptiX: {aggregate.get('traversal_embree_over_optix_mean')}",
        "",
        "## Claim Boundary",
        "",
        "- No full robot planning claim.",
        "- No exact solid or continuous collision claim.",
        "- No V3-over-V2 broad speedup claim.",
        "- No release or public speedup wording is authorized by this packet alone.",
        "- External review is required before any M7 promotion.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _tail(path: Path, limit: int = 4000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""
    return text[-limit:]


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
