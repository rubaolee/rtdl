from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import run_authorofficial_component_signature_gate as component_gate


ROOT = component_gate.ROOT
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper"
DEFAULT_MANIFEST = APP_DIR / "data" / "fixtures" / "representative_fixtures_manifest.json"
DEFAULT_RESULTS = APP_DIR / "results" / "representative_partition_matrix_summary.json"


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _read_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_case_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return APP_DIR / path


def _extract_rtdl_phase_metadata(rtdl_result: dict[str, object]) -> dict[str, object]:
    metadata = dict(rtdl_result.get("metadata", {}))
    native_grouped = dict(metadata.get("native_grouped_stream_metadata", {}) or {})
    count_metadata = dict(metadata.get("count_metadata", {}) or {})
    count_native = dict(count_metadata.get("native_metadata", {}) or {})
    return {
        "partner_reference_contract": metadata.get("partner_reference_contract"),
        "native_engine_row_contract": metadata.get("native_engine_row_contract"),
        "rt_core_accelerated": metadata.get("rt_core_accelerated"),
        "materializes_neighbor_rows": metadata.get("materializes_neighbor_rows"),
        "materializes_directed_adjacency_stream": metadata.get("materializes_directed_adjacency_stream"),
        "count_threshold_native_elapsed_sec": count_native.get("native_elapsed_sec"),
        "grouped_union_native_elapsed_sec": native_grouped.get("native_elapsed_sec"),
        "grouped_stream_policy": metadata.get("grouped_stream_policy"),
        "component_label_policy": metadata.get("component_label_policy"),
    }


def _run_one_case(
    case: dict[str, object],
    *,
    backend: str,
    author_binary: Path | None,
    repeat: int,
    output_dir: Path,
) -> dict[str, object]:
    input_path = _resolve_case_path(str(case["path"]))
    epsilon = float(case["epsilon"])
    min_points = int(case["min_points"])
    points = component_gate.core_gate._read_points(input_path)

    repeats: list[dict[str, object]] = []
    for repeat_index in range(int(repeat)):
        author_payload = None
        author_wall_sec = None
        author_partition = None
        if author_binary is not None:
            author_output = output_dir / f"{case['name']}_author_repeat{repeat_index}.jsonl"
            started = time.perf_counter()
            author_payload = component_gate._run_author(
                author_binary,
                input_path,
                size=len(points),
                epsilon=epsilon,
                min_points=min_points,
                output_path=author_output,
            )
            author_wall_sec = time.perf_counter() - started
            author_partition = component_gate._author_component_partition(author_payload)

        started = time.perf_counter()
        rtdl_result = component_gate._rtdl_component_result(
            points,
            epsilon=epsilon,
            min_points=min_points,
            backend=backend,
        )
        rtdl_wall_sec = time.perf_counter() - started

        signature_matched = None
        component_partition_matched = None
        core_flags_matched = None
        matched = None
        if author_partition is not None:
            signature_matched = author_partition["signature"] == rtdl_result["signature"]
            component_partition_matched = (
                author_partition["canonical_component_labels"] == rtdl_result.get("canonical_component_labels")
            )
            core_flags_matched = author_partition.get("core_flags") == rtdl_result.get("core_flags")
            matched = bool(signature_matched and component_partition_matched and core_flags_matched)

        repeats.append(
            {
                "repeat_index": repeat_index,
                "matched": matched,
                "signature_matched": signature_matched,
                "component_partition_matched": component_partition_matched,
                "core_flags_matched": core_flags_matched,
                "author_wall_sec": author_wall_sec,
                "author_reported_total_time_sec": None if author_payload is None else author_payload.get("total_time_sec"),
                "author_reported_build_time_sec": None if author_payload is None else author_payload.get("build_time_sec"),
                "author_reported_core_points_time_sec": None if author_payload is None else author_payload.get("core_points_time_sec"),
                "author_reported_cluster_formation_time_sec": None
                if author_payload is None
                else author_payload.get("cluster_formation_time_sec"),
                "rtdl_wall_sec": rtdl_wall_sec,
                "rtdl_signature": rtdl_result["signature"],
                "rtdl_phase_metadata": _extract_rtdl_phase_metadata(rtdl_result),
            }
        )

    author_wall_values = [float(item["author_wall_sec"]) for item in repeats if item["author_wall_sec"] is not None]
    author_reported_total_values = [
        float(item["author_reported_total_time_sec"])
        for item in repeats
        if item["author_reported_total_time_sec"] is not None
    ]
    rtdl_wall_values = [float(item["rtdl_wall_sec"]) for item in repeats]
    all_matched = all(item["matched"] is not False for item in repeats)
    return {
        "name": case["name"],
        "input_path": str(input_path),
        "point_count": len(points),
        "epsilon": epsilon,
        "min_points": min_points,
        "backend": backend,
        "repeat": int(repeat),
        "all_matched": bool(all_matched),
        "median_author_process_wall_sec": _median(author_wall_values),
        "median_author_reported_total_time_sec": _median(author_reported_total_values),
        "median_rtdl_wall_sec": _median(rtdl_wall_values),
        "rtdl_vs_author_process_wall_ratio": None
        if not author_wall_values
        else _median(rtdl_wall_values) / _median(author_wall_values),
        "rtdl_vs_author_reported_total_ratio": None
        if not author_reported_total_values
        else _median(rtdl_wall_values) / _median(author_reported_total_values),
        "first_repeat": repeats[0] if repeats else None,
        "repeats": repeats,
    }


def run_matrix(
    *,
    manifest_path: Path,
    backend: str,
    author_binary: Path | None,
    repeat: int,
    output_dir: Path,
    case_names: set[str] | None = None,
) -> dict[str, object]:
    manifest = _read_manifest(manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_cases = list(manifest["cases"])
    if case_names:
        raw_cases = [case for case in raw_cases if str(case["name"]) in case_names]
        missing = sorted(case_names.difference(str(case["name"]) for case in raw_cases))
        if missing:
            raise ValueError(f"Requested cases not found in manifest: {missing}")
    cases = [
        _run_one_case(
            case,
            backend=backend,
            author_binary=author_binary,
            repeat=repeat,
            output_dir=output_dir,
        )
        for case in raw_cases
    ]
    return {
        "schema": "rtdl.paper_reproduction.rt_dbscan.partition_matrix.v1",
        "paper_app": "rt-dbscan-paper",
        "manifest_path": str(manifest_path),
        "backend": backend,
        "author_comparator_used": author_binary is not None,
        "repeat": int(repeat),
        "case_filter": None if case_names is None else sorted(case_names),
        "claim_boundary": (
            "Bounded same-input representative correctness and diagnostic timing matrix. "
            "Synthetic fixtures only; not exact paper datasets and not a public speedup claim."
        ),
        "all_cases_matched": all(case["all_matched"] for case in cases),
        "cases": cases,
        "paper_reproduction_claim_authorized": False,
        "performance_claim_authorized": False,
        "whole_program_speedup_claim_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run RT-DBSCAN representative partition correctness/timing matrix.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--backend", choices=("cpu_reference", "optix_numba_component_signature"), default="cpu_reference")
    parser.add_argument("--author-binary", type=Path, default=None)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--case", action="append", default=None, help="Run only the named case; may be repeated.")
    parser.add_argument("--output-dir", type=Path, default=APP_DIR / "results" / "representative_partition_matrix_author_outputs")
    parser.add_argument("--summary", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args(argv)

    summary = run_matrix(
        manifest_path=args.manifest,
        backend=args.backend,
        author_binary=args.author_binary,
        repeat=args.repeat,
        output_dir=args.output_dir,
        case_names=None if args.case is None else set(args.case),
    )
    text = json.dumps(summary, indent=2, sort_keys=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(text + "\n", encoding="utf-8")
    print(text)
    if summary["author_comparator_used"] and not summary["all_cases_matched"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
