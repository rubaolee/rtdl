from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.prepared_execution import audit_prepared_execution_session_metadata  # noqa: E402


DEFAULT_CURRENT_APP = Path(
    "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"
)


def _geomean(values: list[float]) -> float | None:
    positive = [float(value) for value in values if float(value) > 0.0 and math.isfinite(float(value))]
    if not positive:
        return None
    return math.exp(sum(math.log(value) for value in positive) / len(positive))


def _signature_key(payload: dict[str, Any]) -> str:
    return json.dumps(payload.get("signature"), sort_keys=True)


def _make_legacy_non_runner_app(current_app: Path, output_dir: Path, repo_root: Path) -> Path:
    text = current_app.read_text(encoding="utf-8")
    needle = 'use_productized_runner = column_signature_mode and grouped_stream_partner == "numba"'
    replacement = "use_productized_runner = False  # M3.4 focused A/B legacy non-runner branch"
    if needle not in text:
        raise RuntimeError("could not locate productized-runner guard for legacy comparison app")
    root_needle = (
        'ROOT = next(parent for parent in Path(__file__).resolve().parents '
        'if (parent / "src" / "rtdsl").exists())'
    )
    root_replacement = (
        f"ROOT = Path({str(repo_root)!r}).resolve()  # M3.4 generated legacy app outside repo tree"
    )
    if root_needle not in text:
        raise RuntimeError("could not locate repo-root discovery line for legacy comparison app")
    legacy_app = output_dir / "rtdl_rt_dbscan_benchmark_app_legacy_m3_4.py"
    legacy_app.write_text(
        text.replace(root_needle, root_replacement, 1).replace(needle, replacement, 1),
        encoding="utf-8",
    )
    return legacy_app


def _run_case(
    *,
    repo_root: Path,
    app_path: Path,
    mode: str,
    dataset: str,
    point_count: int,
    repeat: int,
    warmup: int,
    sample: int,
    output_path: Path,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(app_path),
        "--mode",
        mode,
        "--dataset",
        dataset,
        "--point-count",
        str(point_count),
        "--repeat",
        str(repeat),
        "--warmup",
        str(warmup),
        "--no-validation",
    ]
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    process_elapsed = time.perf_counter() - start
    stderr_path = output_path.with_suffix(".stderr.txt")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        output_path.with_suffix(".stdout.txt").write_text(completed.stdout, encoding="utf-8")
        raise RuntimeError(
            f"case failed rc={completed.returncode} mode={mode} point_count={point_count} "
            f"sample={sample}; stderr={stderr_path}"
        )
    payload = json.loads(completed.stdout)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    metadata = payload.get("metadata", {})
    last_runner_metadata = metadata.get("prepared_execution_session_runner_last_metadata") or {}
    runner_step3_audit = audit_prepared_execution_session_metadata(last_runner_metadata)
    return {
        "mode": mode,
        "app_path": str(app_path),
        "dataset": dataset,
        "point_count": point_count,
        "repeat": repeat,
        "warmup": warmup,
        "sample": sample,
        "returncode": completed.returncode,
        "process_elapsed_sec": process_elapsed,
        "payload_elapsed_sec": float(payload["elapsed_sec"]),
        "signature_key": _signature_key(payload),
        "output_json": str(output_path),
        "stderr": str(stderr_path),
        "prepared_execution_session_runner_used": bool(
            metadata.get("prepared_execution_session_runner_used", False)
        ),
        "productized_execution_path": metadata.get("productized_execution_path"),
        "runner_runtime_executed_count": metadata.get(
            "prepared_execution_session_runner_runtime_executed_count"
        ),
        "runner_measured_repeat_count": metadata.get(
            "prepared_execution_session_runner_measured_repeat_count"
        ),
        "runner_repeated_execution": metadata.get(
            "prepared_execution_session_runner_repeated_execution"
        ),
        "runner_single_cache_lookup_for_measured_repeats": metadata.get(
            "prepared_execution_session_runner_single_cache_lookup_for_measured_repeats"
        ),
        "runner_single_report_after_measured_repeats": metadata.get(
            "prepared_execution_session_runner_single_report_after_measured_repeats"
        ),
        "runner_cache_hit_count": metadata.get(
            "prepared_execution_session_runner_cache_hit_count"
        ),
        "runner_schema": last_runner_metadata.get("schema"),
        "phoenix_v3_redesign_step": metadata.get("phoenix_v3_redesign_step"),
        "runtime_trunk_family": metadata.get("runtime_trunk_family"),
        "runtime_trunk_executes_end_to_end": bool(
            metadata.get("runtime_trunk_executes_end_to_end", False)
        ),
        "runtime_trunk_executes_end_to_end_count": metadata.get(
            "runtime_trunk_executes_end_to_end_count"
        ),
        "internal_device_residency_between_rtdl_phases": bool(
            metadata.get("internal_device_residency_between_rtdl_phases", False)
        ),
        "hot_path_host_materialization": bool(
            metadata.get("hot_path_host_materialization", True)
        ),
        "external_device_buffer_interop_authorized": bool(
            metadata.get("external_device_buffer_interop_authorized", False)
        ),
        "v4_embedding_or_external_zero_copy_authorized": bool(
            metadata.get("v4_embedding_or_external_zero_copy_authorized", False)
        ),
        "focused_material_gain_required_before_all_app": bool(
            metadata.get("focused_material_gain_required_before_all_app", False)
        ),
        "runner_measured_repeat_seconds": last_runner_metadata.get("measured_repeat_seconds"),
        "runner_route_adapter_batch_call_sec": last_runner_metadata.get("route_adapter_batch_call_sec"),
        "step3_audit": runner_step3_audit,
        "step3_audit_status": str(runner_step3_audit.get("status")),
        "step3_audit_missing_fields": tuple(runner_step3_audit.get("missing_step3_fields") or ()),
        "step3_residency_default_ready": bool(
            runner_step3_audit.get("step3_residency_default_ready")
        ),
        "prepared_query_repeat_protocol": metadata.get("prepared_query_repeat_protocol"),
        "signature_strategy": metadata.get("column_signature_strategy"),
        "materializes_python_rows": metadata.get("materializes_python_rows"),
        "release_authorized": bool(metadata.get("release_authorized", False)),
        "public_speedup_claim_authorized": bool(
            metadata.get("public_speedup_claim_authorized", False)
        ),
        "broad_v3_faster_than_v2_claim_authorized": bool(
            metadata.get("broad_v3_faster_than_v2_claim_authorized", False)
        ),
        "true_zero_copy_claim_authorized": bool(
            metadata.get("true_zero_copy_claim_authorized", False)
        ),
        "automatic_partner_selection_authorized": bool(
            metadata.get("automatic_partner_selection_authorized", False)
        ),
        "app_specific_native_engine_logic_allowed": bool(
            metadata.get("app_specific_native_engine_logic_allowed", False)
        ),
    }


def _summarize_variant(rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload_elapsed = [float(row["payload_elapsed_sec"]) for row in rows]
    process_elapsed = [float(row["process_elapsed_sec"]) for row in rows]
    signature_keys = sorted({str(row["signature_key"]) for row in rows})
    return {
        "sample_count": len(rows),
        "payload_elapsed_sec_median": statistics.median(payload_elapsed),
        "payload_elapsed_sec_min": min(payload_elapsed),
        "payload_elapsed_sec_max": max(payload_elapsed),
        "process_elapsed_sec_median": statistics.median(process_elapsed),
        "signatures_stable": len(signature_keys) == 1,
        "signature_keys": signature_keys,
        "runner_used_all_samples": all(
            bool(row["prepared_execution_session_runner_used"]) for row in rows
        ),
        "runner_runtime_executed_counts": [
            row["runner_runtime_executed_count"] for row in rows
        ],
        "runner_measured_repeat_counts": [
            row["runner_measured_repeat_count"] for row in rows
        ],
        "runner_repeated_execution_flags": [
            row["runner_repeated_execution"] for row in rows
        ],
        "runner_single_cache_lookup_flags": [
            row["runner_single_cache_lookup_for_measured_repeats"] for row in rows
        ],
        "runner_single_report_flags": [
            row["runner_single_report_after_measured_repeats"] for row in rows
        ],
        "runner_cache_hit_counts": [row["runner_cache_hit_count"] for row in rows],
        "runner_schemas": sorted(
            {str(row["runner_schema"]) for row in rows if row["runner_schema"] is not None}
        ),
        "step3_audit_statuses": sorted(
            {str(row["step3_audit_status"]) for row in rows if row["step3_audit_status"] is not None}
        ),
        "step3_audit_missing_fields": sorted(
            {
                str(field)
                for row in rows
                for field in tuple(row["step3_audit_missing_fields"] or ())
            }
        ),
        "step3_residency_default_ready_all_samples": all(
            bool(row["step3_residency_default_ready"]) for row in rows
        ),
        "runtime_trunk_executes_all_samples": all(
            bool(row["runtime_trunk_executes_end_to_end"]) for row in rows
        ),
        "runtime_trunk_executes_counts": [
            row["runtime_trunk_executes_end_to_end_count"] for row in rows
        ],
        "internal_device_residency_all_samples": all(
            bool(row["internal_device_residency_between_rtdl_phases"]) for row in rows
        ),
        "hot_path_host_materialization_any_sample": any(
            bool(row["hot_path_host_materialization"]) for row in rows
        ),
        "external_device_buffer_interop_any_sample": any(
            bool(row["external_device_buffer_interop_authorized"]) for row in rows
        ),
        "v4_embedding_or_external_zero_copy_any_sample": any(
            bool(row["v4_embedding_or_external_zero_copy_authorized"]) for row in rows
        ),
        "claim_flags_all_false": all(
            not bool(row["release_authorized"])
            and not bool(row["public_speedup_claim_authorized"])
            and not bool(row["broad_v3_faster_than_v2_claim_authorized"])
            and not bool(row["true_zero_copy_claim_authorized"])
            and not bool(row["automatic_partner_selection_authorized"])
            and not bool(row["app_specific_native_engine_logic_allowed"])
            for row in rows
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Focused Phoenix V3 RTDBSCAN M3.4 repeated-runner pod A/B."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset", default="clustered3d")
    parser.add_argument("--point-counts", default="65536,262144")
    parser.add_argument("--repeat", type=int, default=7)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--current-app", type=Path, default=DEFAULT_CURRENT_APP)
    parser.add_argument("--legacy-app", type=Path, default=None)
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    current_app = (repo_root / args.current_app).resolve() if not args.current_app.is_absolute() else args.current_app
    legacy_app = (
        (repo_root / args.legacy_app).resolve()
        if args.legacy_app is not None and not args.legacy_app.is_absolute()
        else args.legacy_app
    )
    if legacy_app is None:
        legacy_app = _make_legacy_non_runner_app(current_app, output_dir, repo_root)
    point_counts = [int(value.strip()) for value in args.point_counts.split(",") if value.strip()]
    variants = {
        "legacy_grouped_stream_numba_column_signature": {
            "app_path": legacy_app,
            "mode": "optix_rt_core_grouped_stream_numba_column_signature_3d",
        },
        "runner_grouped_stream_numba_column_signature": {
            "app_path": current_app,
            "mode": "optix_rt_core_grouped_stream_numba_column_signature_3d",
        },
        "embree_core_flags_numba_prepared_grid_column_signature": {
            "app_path": current_app,
            "mode": "embree_core_flags_numba_prepared_grid_column_signature_3d",
        },
    }
    all_rows: list[dict[str, Any]] = []
    by_scale: dict[str, dict[str, Any]] = {}
    for point_count in point_counts:
        print(f"[phoenix-v3-rtdbscan-m3.4] scale {point_count}", flush=True)
        scale_rows: dict[str, list[dict[str, Any]]] = {name: [] for name in variants}
        for variant_name, variant in variants.items():
            for sample in range(1, int(args.samples) + 1):
                print(
                    f"[phoenix-v3-rtdbscan-m3.4] {variant_name} "
                    f"point_count={point_count} sample={sample}/{args.samples}",
                    flush=True,
                )
                output_path = output_dir / f"{variant_name}_{point_count}_s{sample:02d}.json"
                row = _run_case(
                    repo_root=repo_root,
                    app_path=Path(variant["app_path"]),
                    mode=str(variant["mode"]),
                    dataset=args.dataset,
                    point_count=point_count,
                    repeat=int(args.repeat),
                    warmup=int(args.warmup),
                    sample=sample,
                    output_path=output_path,
                )
                row["variant"] = variant_name
                all_rows.append(row)
                scale_rows[variant_name].append(row)
        summaries = {
            name: _summarize_variant(rows) for name, rows in scale_rows.items()
        }
        legacy = summaries["legacy_grouped_stream_numba_column_signature"][
            "payload_elapsed_sec_median"
        ]
        runner = summaries["runner_grouped_stream_numba_column_signature"][
            "payload_elapsed_sec_median"
        ]
        embree = summaries["embree_core_flags_numba_prepared_grid_column_signature"][
            "payload_elapsed_sec_median"
        ]
        signature_sets = [
            set(summaries[name]["signature_keys"]) for name in summaries
        ]
        by_scale[str(point_count)] = {
            "variant_summaries": summaries,
            "runner_vs_legacy_speedup": legacy / runner if runner > 0.0 else None,
            "runner_vs_embree_speedup": embree / runner if runner > 0.0 else None,
            "legacy_vs_embree_speedup": embree / legacy if legacy > 0.0 else None,
            "all_variant_signatures_match": len(set.union(*signature_sets)) == 1,
        }

    runner_vs_legacy = [
        float(row["runner_vs_legacy_speedup"])
        for row in by_scale.values()
        if row["runner_vs_legacy_speedup"] is not None
    ]
    runner_vs_embree = [
        float(row["runner_vs_embree_speedup"])
        for row in by_scale.values()
        if row["runner_vs_embree_speedup"] is not None
    ]
    runner_rows = [
        row for row in all_rows if row["variant"] == "runner_grouped_stream_numba_column_signature"
    ]
    runner_step3_audit_rows = [
        {
            "point_count": int(row["point_count"]),
            "sample": int(row["sample"]),
            "status": row["step3_audit_status"],
            "step3_residency_default_ready": bool(row["step3_residency_default_ready"]),
            "missing_step3_fields": list(row["step3_audit_missing_fields"]),
        }
        for row in runner_rows
    ]
    summary = {
        "status": "rtdbscan_component_signature_runner_m3_4_pod_ab_collected_not_release",
        "date": "2026-06-22",
        "dataset": args.dataset,
        "point_counts": point_counts,
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "samples": int(args.samples),
        "variant_count": len(variants),
        "sample_count": len(all_rows),
        "legacy_app_generated_from_current": str(legacy_app),
        "measurement_note": (
            "runner elapsed_override is median(measured_repeat_seconds[i] + "
            "column_signature_sec[i]); legacy elapsed_override is median of the "
            "perf_counter window including native call plus signature."
        ),
        "scales": by_scale,
        "geomean_runner_vs_legacy_speedup": _geomean(runner_vs_legacy),
        "geomean_runner_vs_embree_speedup": _geomean(runner_vs_embree),
        "runner_metadata_present_all_runner_samples": all(
            row["prepared_execution_session_runner_used"]
            for row in all_rows
            if row["variant"] == "runner_grouped_stream_numba_column_signature"
        ),
        "runner_repeated_execution_all_runner_samples": all(
            bool(row["runner_repeated_execution"])
            for row in all_rows
            if row["variant"] == "runner_grouped_stream_numba_column_signature"
        ),
        "runner_single_cache_lookup_all_runner_samples": all(
            bool(row["runner_single_cache_lookup_for_measured_repeats"])
            for row in all_rows
            if row["variant"] == "runner_grouped_stream_numba_column_signature"
        ),
        "runner_single_report_all_runner_samples": all(
            bool(row["runner_single_report_after_measured_repeats"])
            for row in runner_rows
        ),
        "runner_step3_audit_rows": runner_step3_audit_rows,
        "runner_step3_residency_default_ready_all_runner_samples": all(
            bool(row["step3_residency_default_ready"]) for row in runner_rows
        ),
        "runtime_trunk_executes_all_runner_samples": all(
            bool(row["runtime_trunk_executes_end_to_end"])
            for row in runner_rows
        ),
        "internal_device_residency_all_runner_samples": all(
            bool(row["internal_device_residency_between_rtdl_phases"])
            for row in runner_rows
        ),
        "hot_path_host_materialization_any_runner_sample": any(
            bool(row["hot_path_host_materialization"])
            for row in runner_rows
        ),
        "external_device_buffer_interop_any_runner_sample": any(
            bool(row["external_device_buffer_interop_authorized"])
            for row in runner_rows
        ),
        "v4_embedding_or_external_zero_copy_any_runner_sample": any(
            bool(row["v4_embedding_or_external_zero_copy_authorized"])
            for row in runner_rows
        ),
        "all_claim_flags_false": all(
            not row["release_authorized"]
            and not row["public_speedup_claim_authorized"]
            and not row["broad_v3_faster_than_v2_claim_authorized"]
            and not row["true_zero_copy_claim_authorized"]
            and not row["automatic_partner_selection_authorized"]
            and not row["app_specific_native_engine_logic_allowed"]
            for row in all_rows
        ),
        "material_set_a_candidate": False,
        "legacy_parity_recovered": False,
        "material_vs_incumbent_legacy_candidate": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "full_all_app_rerun_authorized_by_this_packet": False,
        "raw_rows": all_rows,
    }
    runner_vs_embree_geo = summary["geomean_runner_vs_embree_speedup"]
    runner_vs_legacy_geo = summary["geomean_runner_vs_legacy_speedup"]
    if (
        runner_vs_legacy_geo is not None
        and runner_vs_legacy_geo >= 0.98
        and summary["runner_metadata_present_all_runner_samples"]
        and summary["runner_repeated_execution_all_runner_samples"]
        and summary["runner_single_cache_lookup_all_runner_samples"]
        and summary["runner_single_report_all_runner_samples"]
        and summary["runner_step3_residency_default_ready_all_runner_samples"]
        and summary["runtime_trunk_executes_all_runner_samples"]
        and summary["internal_device_residency_all_runner_samples"]
        and not summary["hot_path_host_materialization_any_runner_sample"]
        and not summary["external_device_buffer_interop_any_runner_sample"]
        and not summary["v4_embedding_or_external_zero_copy_any_runner_sample"]
        and summary["all_claim_flags_false"]
    ):
        summary["legacy_parity_recovered"] = True
    if (
        runner_vs_embree_geo is not None
        and runner_vs_embree_geo >= 1.15
        and runner_vs_legacy_geo is not None
        and runner_vs_legacy_geo >= 1.15
        and summary["runner_metadata_present_all_runner_samples"]
        and summary["runner_repeated_execution_all_runner_samples"]
        and summary["runner_single_cache_lookup_all_runner_samples"]
        and summary["runner_single_report_all_runner_samples"]
        and summary["runner_step3_residency_default_ready_all_runner_samples"]
        and summary["runtime_trunk_executes_all_runner_samples"]
        and summary["internal_device_residency_all_runner_samples"]
        and not summary["hot_path_host_materialization_any_runner_sample"]
        and not summary["external_device_buffer_interop_any_runner_sample"]
        and not summary["v4_embedding_or_external_zero_copy_any_runner_sample"]
        and summary["all_claim_flags_false"]
    ):
        summary["material_set_a_candidate"] = True
        summary["material_vs_incumbent_legacy_candidate"] = True
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    lines = [
        "# Phoenix V3 RTDBSCAN M3.4 Focused Pod A/B",
        "",
        f"Status: `{summary['status']}`.",
        "",
        f"- dataset: `{args.dataset}`",
        f"- point counts: `{', '.join(str(v) for v in point_counts)}`",
        f"- repeat/warmup: `{args.repeat}` / `{args.warmup}`",
        f"- samples per variant per scale: `{args.samples}`",
        f"- geomean runner vs legacy: `{summary['geomean_runner_vs_legacy_speedup']}`",
        f"- geomean runner vs Embree: `{summary['geomean_runner_vs_embree_speedup']}`",
        f"- runtime trunk executes all runner samples: `{summary['runtime_trunk_executes_all_runner_samples']}`",
        f"- internal device residency all runner samples: `{summary['internal_device_residency_all_runner_samples']}`",
        f"- runner Step-3 residency audit ready: `{summary['runner_step3_residency_default_ready_all_runner_samples']}`",
        f"- hot-path host materialization in runner samples: `{summary['hot_path_host_materialization_any_runner_sample']}`",
        f"- legacy parity recovered: `{summary['legacy_parity_recovered']}`",
        f"- material Set-A candidate: `{summary['material_set_a_candidate']}`",
        "",
        "Measurement note: runner elapsed includes measured repeat timing plus",
        "column-signature extraction; legacy elapsed uses the comparable native",
        "call plus signature perf-counter window.",
        "",
        "This focused packet does not authorize release, public speedup wording,",
        "broad V3-over-V2 wording, true-zero-copy wording, or all-app rerun.",
    ]
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
