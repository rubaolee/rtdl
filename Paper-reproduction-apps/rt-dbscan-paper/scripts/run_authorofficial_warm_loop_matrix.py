from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import run_authorofficial_component_signature_gate as component_gate
import run_authorofficial_partition_matrix as partition_matrix


ROOT = component_gate.ROOT
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper"
DEFAULT_MANIFEST = APP_DIR / "data" / "fixtures" / "representative_fixtures_manifest.json"
DEFAULT_OUTPUT_DIR = APP_DIR / "results" / "authorofficial_warm_loop_outputs"
DEFAULT_SUMMARY = APP_DIR / "results" / "authorofficial_warm_loop_matrix_summary.json"


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _json_lines(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("{") and line.endswith("}"):
            rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"{path} does not contain JSON payload lines")
    return rows


def _run_author_warm_loop(
    author_binary: Path,
    input_path: Path,
    *,
    size: int,
    epsilon: float,
    min_points: int,
    repeat: int,
    output_path: Path,
) -> tuple[list[dict[str, object]], float, list[str]]:
    if output_path.exists():
        output_path.unlink()
    command = [
        str(author_binary),
        str(input_path),
        str(int(size)),
        str(float(epsilon)),
        str(int(min_points)),
        str(output_path),
    ]
    env = os.environ.copy()
    env["RTDL_AUTHOR_REPEAT"] = str(int(repeat))
    started = time.perf_counter()
    completed = subprocess.run(command, text=True, capture_output=True, check=False, env=env)
    process_wall_sec = time.perf_counter() - started
    if completed.returncode != 0:
        raise RuntimeError(
            "AuthorOfficial warm-loop run failed with exit code "
            f"{completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    payloads = _json_lines(output_path)
    if len(payloads) != int(repeat):
        raise ValueError(f"Expected {repeat} AuthorOfficial JSON payloads, got {len(payloads)}")
    for index, payload in enumerate(payloads):
        payload["command"] = command
        payload["stdout_tail"] = completed.stdout[-2000:]
        payload["stderr_tail"] = completed.stderr[-2000:]
        if int(payload.get("repeat_index", index)) != index:
            raise ValueError(f"AuthorOfficial repeat_index mismatch at row {index}: {payload.get('repeat_index')}")
    return payloads, process_wall_sec, command


def _author_repeat_metrics(payloads: list[dict[str, object]]) -> dict[str, object]:
    inner = [
        float(item["core_points_time_sec"]) + float(item["cluster_formation_time_sec"])
        for item in payloads
    ]
    totals = [float(item["total_time_sec"]) for item in payloads]
    builds = [float(item["build_time_sec"]) for item in payloads]
    steady_inner = inner[1:] if len(inner) > 1 else inner
    steady_total = totals[1:] if len(totals) > 1 else totals
    return {
        "author_inner_loop_sec": inner,
        "author_reported_total_sec": totals,
        "author_reported_build_sec": builds,
        "author_inner_loop_median_sec": _median(inner),
        "author_inner_loop_steady_median_sec": _median(steady_inner),
        "author_reported_total_median_sec": _median(totals),
        "author_reported_total_steady_median_sec": _median(steady_total),
    }


def _run_rtdl_repeats(
    points: tuple[tuple[float, float, float], ...],
    *,
    epsilon: float,
    min_points: int,
    backend: str,
    repeat: int,
) -> tuple[list[dict[str, object]], list[float]]:
    results: list[dict[str, object]] = []
    walls: list[float] = []
    for _ in range(int(repeat)):
        started = time.perf_counter()
        result = component_gate._rtdl_component_result(
            points,
            epsilon=epsilon,
            min_points=min_points,
            backend=backend,
        )
        walls.append(time.perf_counter() - started)
        results.append(result)
    return results, walls


def _run_case(
    case: dict[str, object],
    *,
    author_binary: Path,
    backend: str,
    repeat: int,
    output_dir: Path,
) -> dict[str, object]:
    input_path = partition_matrix._resolve_case_path(str(case["path"]))
    epsilon = float(case["epsilon"])
    min_points = int(case["min_points"])
    points = component_gate.core_gate._read_points(input_path)

    author_output = output_dir / f"{case['name']}_author_warm_loop.jsonl"
    author_payloads, author_process_wall_sec, command = _run_author_warm_loop(
        author_binary,
        input_path,
        size=len(points),
        epsilon=epsilon,
        min_points=min_points,
        repeat=repeat,
        output_path=author_output,
    )
    author_partitions = [component_gate._author_component_partition(payload) for payload in author_payloads]
    first_author_partition = author_partitions[0]
    author_partitions_stable = all(partition == first_author_partition for partition in author_partitions)

    rtdl_results, rtdl_wall_sec = _run_rtdl_repeats(
        points,
        epsilon=epsilon,
        min_points=min_points,
        backend=backend,
        repeat=repeat,
    )
    rtdl_matches = []
    for result in rtdl_results:
        rtdl_matches.append(
            bool(
                first_author_partition["signature"] == result["signature"]
                and first_author_partition["canonical_component_labels"] == result.get("canonical_component_labels")
                and first_author_partition.get("core_flags") == result.get("core_flags")
            )
        )

    rtdl_steady = rtdl_wall_sec[1:] if len(rtdl_wall_sec) > 1 else rtdl_wall_sec
    author_metrics = _author_repeat_metrics(author_payloads)
    return {
        "name": case["name"],
        "input_path": str(input_path),
        "point_count": len(points),
        "epsilon": epsilon,
        "min_points": min_points,
        "backend": backend,
        "repeat": int(repeat),
        "author_output": str(author_output),
        "author_command": command,
        "author_process_wall_sec": author_process_wall_sec,
        "author_partitions_stable": author_partitions_stable,
        "author_signature": first_author_partition["signature"],
        "author_canonical_component_labels": first_author_partition["canonical_component_labels"],
        "author_core_flags": first_author_partition["core_flags"],
        **author_metrics,
        "rtdl_wall_sec": rtdl_wall_sec,
        "rtdl_wall_median_sec": _median(rtdl_wall_sec),
        "rtdl_wall_steady_median_sec": _median(rtdl_steady),
        "rtdl_all_repeats_matched_author": all(rtdl_matches),
        "rtdl_repeat_matches": rtdl_matches,
        "rtdl_first_signature": rtdl_results[0]["signature"],
        "rtdl_phase_metadata_first": partition_matrix._extract_rtdl_phase_metadata(rtdl_results[0]),
        "rtdl_phase_metadata_last": partition_matrix._extract_rtdl_phase_metadata(rtdl_results[-1]),
        "rtdl_vs_author_inner_loop_steady_ratio": None
        if author_metrics["author_inner_loop_steady_median_sec"] in (None, 0)
        else _median(rtdl_steady) / float(author_metrics["author_inner_loop_steady_median_sec"]),
        "rtdl_vs_author_reported_total_steady_ratio": None
        if author_metrics["author_reported_total_steady_median_sec"] in (None, 0)
        else _median(rtdl_steady) / float(author_metrics["author_reported_total_steady_median_sec"]),
    }


def run_warm_loop_matrix(
    *,
    manifest_path: Path,
    author_binary: Path,
    backend: str,
    repeat: int,
    output_dir: Path,
    case_names: set[str] | None = None,
) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_cases = list(manifest["cases"])
    if case_names:
        raw_cases = [case for case in raw_cases if str(case["name"]) in case_names]
        missing = sorted(case_names.difference(str(case["name"]) for case in raw_cases))
        if missing:
            raise ValueError(f"Requested cases not found in manifest: {missing}")
    cases = [
        _run_case(
            case,
            author_binary=author_binary,
            backend=backend,
            repeat=repeat,
            output_dir=output_dir,
        )
        for case in raw_cases
    ]
    return {
        "schema": "rtdl.paper_reproduction.rt_dbscan.authorofficial_warm_loop_matrix.v1",
        "paper_app": "rt-dbscan-paper",
        "manifest_path": str(manifest_path),
        "backend": backend,
        "repeat": int(repeat),
        "case_filter": None if case_names is None else sorted(case_names),
        "regime": "author_and_rtdl_warm_repeat_same_process_per_side",
        "regime_boundary": (
            "Patched AuthorOfficial repeats the two DBSCAN launches in one process after "
            "author pipeline/accel setup. RTDL repeats the generic OptiX+Numba route in one "
            "Python process. This is a bounded same-input warm-loop diagnostic, not exact "
            "paper performance."
        ),
        "all_cases_matched": all(case["rtdl_all_repeats_matched_author"] and case["author_partitions_stable"] for case in cases),
        "cases": cases,
        "paper_reproduction_claim_authorized": False,
        "performance_claim_authorized": False,
        "whole_program_speedup_claim_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run same-process warm-loop comparison for RT-DBSCAN AuthorOfficial and RTDL.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--author-binary", type=Path, required=True)
    parser.add_argument("--backend", choices=("cpu_reference", "optix_numba_component_signature"), default="optix_numba_component_signature")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--case", action="append", default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args(argv)

    summary = run_warm_loop_matrix(
        manifest_path=args.manifest,
        author_binary=args.author_binary,
        backend=args.backend,
        repeat=args.repeat,
        output_dir=args.output_dir,
        case_names=None if args.case is None else set(args.case),
    )
    text = json.dumps(summary, indent=2, sort_keys=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(text + "\n", encoding="utf-8")
    print(text)
    if not summary["all_cases_matched"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
