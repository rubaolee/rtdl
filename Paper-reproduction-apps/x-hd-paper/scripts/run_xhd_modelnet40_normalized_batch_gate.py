#!/usr/bin/env python3
"""Run a small ModelNet40 normalized-public-OFF batch gate.

This gate is app-owned provenance work for the X-HD paper reproduction line.
It does not add OFF, ModelNet40, or X-HD paper semantics to RTDL core.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_xhd_cell_mbr_frontier_route_gate as rtdl_route


def _modelnet_member_from_author_path(path: str) -> str:
    marker = "/ModelNet40/"
    normalized = path.replace("\\", "/")
    if marker not in normalized:
        raise ValueError(f"author path is not under ModelNet40: {path}")
    return "ModelNet40/" + normalized.split(marker, 1)[1]


def _category_from_member(member: str) -> str:
    parts = member.split("/")
    if len(parts) < 4 or parts[0] != "ModelNet40":
        raise ValueError(f"unexpected ModelNet40 zip member: {member}")
    return parts[1]


def _unique_modelnet_pair_candidates(records: list[dict[str, object]]) -> list[tuple[int, str, dict[str, object]]]:
    seen_pairs: set[tuple[str, str]] = set()
    candidates: list[tuple[int, str, dict[str, object]]] = []
    for record in records:
        if record.get("category") != "ModelNet40":
            continue
        input_payload = record.get("input", {})
        if not isinstance(input_payload, dict):
            continue
        if input_payload.get("normalize") is not True:
            continue
        if input_payload.get("translate") != 0.0:
            continue
        files = input_payload.get("files", [])
        if not isinstance(files, list) or len(files) != 2:
            continue
        path_a = str(files[0]["path"])
        path_b = str(files[1]["path"])
        key = (path_a, path_b)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        member_a = _modelnet_member_from_author_path(path_a)
        member_b = _modelnet_member_from_author_path(path_b)
        category = _category_from_member(member_a)
        total_points = int(files[0]["num_points"]) + int(files[1]["num_points"])
        enriched = {
            "record": record,
            "member_a": member_a,
            "member_b": member_b,
            "category": category,
            "total_points": total_points,
        }
        candidates.append((total_points, category, enriched))
    return candidates


def _select_unique_modelnet_pairs(
    records: list[dict[str, object]],
    *,
    max_pairs: int,
    selection_strategy: str,
) -> list[dict[str, object]]:
    candidates = _unique_modelnet_pair_candidates(records)
    if selection_strategy == "smallest_unique_pairs":
        return [item[2] for item in sorted(candidates, key=lambda item: (item[0], item[1]))[:max_pairs]]
    if selection_strategy == "largest_unique_pairs":
        return [item[2] for item in sorted(candidates, key=lambda item: (-item[0], item[1]))[:max_pairs]]
    if selection_strategy == "all_unique_pairs":
        return [item[2] for item in sorted(candidates, key=lambda item: (item[1], item[0]))[:max_pairs]]
    if selection_strategy != "smallest_unique_pairs_preferring_distinct_categories":
        raise ValueError(f"unsupported ModelNet40 selection strategy: {selection_strategy}")
    selected: list[dict[str, object]] = []
    used_categories: set[str] = set()
    for _total, category, enriched in sorted(candidates, key=lambda item: (item[0], item[1])):
        if category in used_categories:
            continue
        selected.append(enriched)
        used_categories.add(category)
        if len(selected) >= max_pairs:
            return selected
    for _total, _category, enriched in sorted(candidates, key=lambda item: (item[0], item[1])):
        pair_key = (str(enriched["member_a"]), str(enriched["member_b"]))
        if any((str(item["member_a"]), str(item["member_b"])) == pair_key for item in selected):
            continue
        selected.append(enriched)
        if len(selected) >= max_pairs:
            return selected
    return selected


def _select_chunk(
    selected: list[dict[str, object]],
    *,
    start_index: int | None,
    end_index: int | None,
    chunk_index: int | None,
    chunk_size: int | None,
) -> tuple[list[tuple[int, dict[str, object]]], dict[str, object]]:
    if (chunk_index is None) != (chunk_size is None):
        raise ValueError("--chunk-index and --chunk-size must be provided together")
    if chunk_index is not None and (start_index is not None or end_index is not None):
        raise ValueError("--chunk-index/--chunk-size cannot be combined with --start-index/--end-index")
    if chunk_index is not None and chunk_size is not None:
        if chunk_index < 0:
            raise ValueError("--chunk-index must be >= 0")
        if chunk_size <= 0:
            raise ValueError("--chunk-size must be > 0")
        start = chunk_index * chunk_size
        end = min(start + chunk_size, len(selected))
        mode = "chunk-index"
    else:
        start = int(start_index) if start_index is not None else 0
        end = int(end_index) if end_index is not None else len(selected)
        mode = "range"
    if start < 0:
        raise ValueError("chunk start index must be >= 0")
    if end < start:
        raise ValueError("chunk end index must be >= start index")
    indexed = list(enumerate(selected))
    sliced = indexed[start:end]
    return sliced, {
        "mode": mode,
        "total_selected_before_chunk": len(selected),
        "start_index": start,
        "end_index_exclusive": end,
        "chunk_index": chunk_index,
        "chunk_size": chunk_size,
        "selected_count_after_chunk": len(sliced),
    }


def _algorithm_from_author_log_payload(payload: dict[str, object]) -> str | None:
    running = payload.get("Running")
    if not isinstance(running, dict):
        return None
    repeats = running.get("Repeats")
    if not isinstance(repeats, list):
        return None
    algorithms: list[str] = []
    for repeat in repeats:
        if not isinstance(repeat, dict):
            continue
        algorithm = repeat.get("Algorithm")
        if isinstance(algorithm, str) and algorithm:
            algorithms.append(algorithm)
    unique = sorted(set(algorithms))
    if len(unique) == 1:
        return unique[0]
    if not unique:
        return None
    raise ValueError(f"mixed author log algorithms are not supported: {unique}")


def _paper_log_algorithm(record: dict[str, object], *, paper_log_repo: Path | None) -> str | None:
    if paper_log_repo is None:
        return None
    blob = record.get("blob")
    if not isinstance(blob, str) or not blob:
        return None
    completed = subprocess.run(
        ["git", "-C", str(paper_log_repo), "cat-file", "-p", blob],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"failed to read paper-log blob {blob}: {completed.stderr}")
    return _algorithm_from_author_log_payload(json.loads(completed.stdout))


def _author_runner_for_algorithm(
    algorithm: str | None,
    *,
    default_author_bin: Path,
    hybrid_author_bin: Path | None,
) -> tuple[Path, str, str]:
    normalized = (algorithm or "XHD").strip().lower()
    if normalized == "hybrid":
        if hybrid_author_bin is None:
            raise ValueError("paper log requires Algorithm=Hybrid but --author-hybrid-bin was not provided")
        return hybrid_author_bin, "hybrid", "Hybrid"
    if normalized in {"xhd", "rt"}:
        return default_author_bin, "rt", "XHD"
    raise ValueError(f"unsupported paper-log Algorithm for ModelNet40 batch gate: {algorithm!r}")


def _extract_member(zip_path: Path, member: str, extract_root: Path) -> Path:
    out = extract_root / member
    if out.exists():
        return out
    with zipfile.ZipFile(zip_path) as zf:
        if member not in zf.namelist():
            raise FileNotFoundError(f"{member} not found in {zip_path}")
        zf.extract(member, extract_root)
    return out


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _case_artifact_path(output_dir: Path, case_name: str) -> Path:
    return output_dir / "cases" / f"{case_name}.json"


def _write_case_artifact(output_dir: Path, case_name: str, payload: dict[str, object]) -> None:
    path = _case_artifact_path(output_dir, case_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_completed_case_artifact(output_dir: Path, case_name: str) -> dict[str, object] | None:
    path = _case_artifact_path(output_dir, case_name)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("case_matched") is not True:
        return None
    payload = dict(payload)
    payload["skipped_completed"] = True
    return payload


def _aggregate_existing_case_artifacts(args: argparse.Namespace) -> dict[str, object]:
    output_dir = Path(args.output_dir)
    case_dir = output_dir / "cases"
    if not case_dir.exists():
        raise FileNotFoundError(f"no case artifact directory exists: {case_dir}")
    cases: list[dict[str, object]] = []
    for path in sorted(case_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"case artifact is not an object: {path}")
        cases.append(payload)
    cases.sort(key=lambda case: int(case.get("case_index", -1)))
    matched_cases = [case for case in cases if case.get("case_matched") is True]
    failed_cases = [case for case in cases if case.get("case_matched") is not True]
    return {
        "schema": "rtdl.paper_reproduction.xhd.modelnet40_normalized_batch_gate.v2",
        "goal": str(args.goal_label),
        "status": "modelnet40_normalized_public_off_batch_aggregated_from_case_artifacts",
        "log_index": str(Path(args.log_index)) if args.log_index else None,
        "modelnet_zip": str(Path(args.modelnet_zip)) if args.modelnet_zip else None,
        "extract_root": str(Path(args.extract_root)) if args.extract_root else None,
        "selection": {
            "strategy": str(args.selection_strategy),
            "requested_max_pairs": int(args.max_pairs),
            "selected_count": len(cases),
            "chunk": {
                "mode": "aggregate-existing-cases",
                "total_selected_before_chunk": None,
                "start_index": None,
                "end_index_exclusive": None,
                "chunk_index": None,
                "chunk_size": None,
                "selected_count_after_chunk": len(cases),
            },
            "total_points_min": min((int(case.get("total_points", 0)) for case in cases), default=0),
            "total_points_max": max((int(case.get("total_points", 0)) for case in cases), default=0),
        },
        "cases": cases,
        "matched_case_count": len(matched_cases),
        "failed_case_count": len(failed_cases),
        "all_cases_matched": bool(cases and len(matched_cases) == len(cases)),
        "claim_boundary": {
            "modelnet40_batch_normalized_contract_claimed": True,
            "algorithm_aware_author_comparator_selection": bool(args.paper_log_repo),
            "modelnet40_all_pairs_reproduced": False,
            "exact_paper_dataset_identity_proved": False,
            "author_vs_rtdl_ratio_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def _run_author(
    *,
    author_bin: Path,
    variant: str,
    input1: Path,
    input2: Path,
    output_json: Path,
    n_points_cell: int | None,
    max_hit: int | None,
) -> dict[str, object]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(author_bin),
        "-input1",
        str(input1),
        "-input2",
        str(input2),
        "-n_dims",
        "3",
        "-input_type",
        "off",
        "-variant",
        str(variant),
        "-execution",
        "gpu",
        "-normalize=true",
        "-json",
        str(output_json),
        "-overwrite=true",
        "-check=false",
        "-repeat=1",
    ]
    if n_points_cell is not None:
        cmd.extend(["-n_points_cell", str(int(n_points_cell))])
    if max_hit is not None:
        cmd.extend(["-max_hit", str(int(max_hit))])
    start = time.perf_counter()
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    elapsed = time.perf_counter() - start
    return {
        "cmd": cmd,
        "returncode": int(completed.returncode),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "process_wall_sec": elapsed,
    }


def _mbrs_close(author_payload: dict[str, object], log_files: list[dict[str, object]], *, tolerance: float) -> bool:
    input_payload = author_payload["Input"]  # type: ignore[index]
    files = input_payload["Files"]  # type: ignore[index]
    for observed, expected in zip(files, log_files):
        observed_mbr = observed["MBR"]  # type: ignore[index]
        expected_mbr = expected["mbr"]
        for got_axis, want_axis in zip(observed_mbr, expected_mbr):
            if abs(float(got_axis["Lower"]) - float(want_axis["Lower"])) > tolerance:
                return False
            if abs(float(got_axis["Upper"]) - float(want_axis["Upper"])) > tolerance:
                return False
    return True


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    if bool(args.aggregate_existing_cases):
        return _aggregate_existing_case_artifacts(args)

    log_index = json.loads(Path(args.log_index).read_text(encoding="utf-8"))
    selected = _select_unique_modelnet_pairs(
        log_index["run_all_records"],
        max_pairs=int(args.max_pairs),
        selection_strategy=str(args.selection_strategy),
    )
    selected_indexed, chunk_summary = _select_chunk(
        selected,
        start_index=args.start_index,
        end_index=args.end_index,
        chunk_index=args.chunk_index,
        chunk_size=args.chunk_size,
    )
    if not selected:
        raise RuntimeError("no ModelNet40 normalized pairs selected")
    if not selected_indexed:
        raise RuntimeError("ModelNet40 chunk selected no pairs")

    zip_path = Path(args.modelnet_zip)
    extract_root = Path(args.extract_root)
    output_dir = Path(args.output_dir)
    cases: list[dict[str, object]] = []
    started = time.perf_counter()
    for case_index, item in selected_indexed:
        record = item["record"]
        assert isinstance(record, dict)
        input_payload = record["input"]
        assert isinstance(input_payload, dict)
        log_files = input_payload["files"]
        assert isinstance(log_files, list)
        member_a = str(item["member_a"])
        member_b = str(item["member_b"])
        path_a = _extract_member(zip_path, member_a, extract_root)
        path_b = _extract_member(zip_path, member_b, extract_root)
        case_name = f"{case_index:04d}_{Path(member_a).stem}__{Path(member_b).stem}"
        if bool(args.skip_completed):
            completed_case = _read_completed_case_artifact(output_dir, case_name)
            if completed_case is not None:
                cases.append(completed_case)
                continue
        author_json = output_dir / "author" / f"{case_name}.json"
        route_json = output_dir / "rtdl" / f"{case_name}.json"
        try:
            running_payload = record.get("running", {})
            n_points_cell = None
            if isinstance(running_payload, dict) and running_payload.get("num_points_per_cell") is not None:
                n_points_cell = int(running_payload["num_points_per_cell"])
            max_hit = None
            if isinstance(running_payload, dict) and running_payload.get("max_hit") is not None:
                max_hit = int(running_payload["max_hit"])
            paper_algorithm = _paper_log_algorithm(
                record,
                paper_log_repo=Path(args.paper_log_repo) if args.paper_log_repo else None,
            )
            author_bin, author_variant, expected_author_algorithm = _author_runner_for_algorithm(
                paper_algorithm,
                default_author_bin=Path(args.author_bin),
                hybrid_author_bin=Path(args.author_hybrid_bin) if args.author_hybrid_bin else None,
            )

            author_run = _run_author(
                author_bin=author_bin,
                variant=author_variant,
                input1=path_a,
                input2=path_b,
                output_json=author_json,
                n_points_cell=n_points_cell,
                max_hit=max_hit,
            )
            if author_run["returncode"] != 0:
                raise RuntimeError(f"author run failed for {case_name}: {author_run}")
            author_payload = json.loads(author_json.read_text(encoding="utf-8"))
            paper_hd = float(record["hd_result"])
            author_hd = float(author_payload["HDResult"])
            paper_abs_diff = abs(author_hd - paper_hd)
            mbr_matched = _mbrs_close(author_payload, log_files, tolerance=float(args.mbr_tolerance))
            observed_algorithms = sorted(
                {
                    str(repeat.get("Algorithm"))
                    for repeat in author_payload.get("Running", {}).get("Repeats", [])
                    if isinstance(repeat, dict) and repeat.get("Algorithm") is not None
                }
            )

            route_summary = rtdl_route.build_summary(
                argparse.Namespace(
                    input1=str(path_a),
                    input2=str(path_b),
                    n_dims=3,
                    input_type="off",
                    normalize_each_input_to_author_unit_box=True,
                translate_each_input_to_min_bound=False,
                author_float32_normalization=bool(args.author_float32_normalization),
                backend=args.backend,
                    grid_shape=args.grid_shape,
                    radius=None,
                    max_inline_points=int(args.max_inline_points),
                    initial_state=args.initial_state,
                    seed_cell_budget=4,
                    grid_branch_bound_seed_executor=args.grid_branch_bound_seed_executor,
                    frontier_nearest_executor=args.frontier_nearest_executor,
                    local_grid_seed_executor=args.local_grid_seed_executor,
                    frontier_row_order=args.frontier_row_order,
                    cell_order="native",
                    grid_cell_point_order=args.grid_cell_point_order,
                    grid_cell_builder=args.grid_cell_builder,
                    frontier_inline_nearest=bool(args.frontier_inline_nearest),
                    global_bound_early_break=bool(args.global_bound_early_break),
                    collect_inline_stats=False,
                    collect_frontier_native_phase_timings=False,
                    frontier_row_capacity=None,
                    skip_frontier_if_exact_seed=bool(args.skip_frontier_if_exact_seed),
                    direction_mode="directed-a-to-b",
                    validation_mode="author-only",
                    author_json=str(author_json),
                    tolerance=float(args.tolerance),
                )
            )
            route_json.parent.mkdir(parents=True, exist_ok=True)
            route_json.write_text(json.dumps(route_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            case = {
                "case_index": case_index,
                "case_name": case_name,
                "category": item["category"],
                "total_points": int(item["total_points"]),
                "members": [member_a, member_b],
                "public_paths": [str(path_a), str(path_b)],
                "public_sha256": [_sha256(path_a), _sha256(path_b)],
                "author_log": {
                    "relative_log_path": record.get("relative_log_path"),
                    "hd_result": paper_hd,
                    "normalize": input_payload.get("normalize"),
                    "translate": input_payload.get("translate"),
                    "type": input_payload.get("type"),
                    "point_counts": [int(log_files[0]["num_points"]), int(log_files[1]["num_points"])],
                    "num_points_per_cell": n_points_cell,
                    "max_hit": max_hit,
                    "algorithm": paper_algorithm,
                },
                "author_normalized": {
                    "json": str(author_json),
                    "author_bin": str(author_bin),
                    "variant": author_variant,
                    "expected_algorithm": expected_author_algorithm,
                    "observed_algorithms": observed_algorithms,
                    "hd_result": author_hd,
                    "running_avg_time_ms": author_payload.get("Running", {}).get("AvgTime"),
                    "process_wall_sec": author_run["process_wall_sec"],
                    "paper_abs_diff": paper_abs_diff,
                    "paper_hd_matched": bool(paper_abs_diff <= float(args.tolerance)),
                    "mbr_matched": bool(mbr_matched),
                    "algorithm_matched": bool(
                        not paper_algorithm
                        or expected_author_algorithm in observed_algorithms
                        or paper_algorithm in observed_algorithms
                    ),
                },
                "rtdl_normalized_route": {
                    "json": str(route_json),
                    "matched_author": bool(route_summary["matched"]),
                    "author_abs_diff": route_summary["author_abs_diff"],
                    "route_distance": route_summary["author_comparison_distance"],
                    "route_wall_sec": route_summary["run_phases"]["rtdl_route_sec"],
                    "total_sec": route_summary["run_phases"]["total_sec"],
                    "reference_preprocessing": route_summary["reference_preprocessing"],
                },
            }
            case["case_matched"] = bool(
                case["author_normalized"]["paper_hd_matched"]
                and case["author_normalized"]["mbr_matched"]
                and case["author_normalized"]["algorithm_matched"]
                and case["rtdl_normalized_route"]["matched_author"]
            )
        except Exception as exc:
            if not bool(args.continue_on_error):
                raise
            case = {
                "case_index": case_index,
                "case_name": case_name,
                "category": item["category"],
                "total_points": int(item["total_points"]),
                "members": [member_a, member_b],
                "public_paths": [str(path_a), str(path_b)],
                "case_matched": False,
                "case_error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            }
        _write_case_artifact(output_dir, case_name, case)
        cases.append(case)

    matched_cases = [case for case in cases if case["case_matched"]]
    failed_cases = [case for case in cases if case["case_matched"] is not True]
    return {
        "schema": "rtdl.paper_reproduction.xhd.modelnet40_normalized_batch_gate.v2",
        "goal": str(args.goal_label),
        "status": "modelnet40_normalized_public_off_batch_checked",
        "log_index": str(Path(args.log_index)),
        "modelnet_zip": str(zip_path),
        "extract_root": str(extract_root),
        "selection": {
            "strategy": str(args.selection_strategy),
            "requested_max_pairs": int(args.max_pairs),
            "chunk": chunk_summary,
            "selected_count": len(cases),
            "total_points_min": min((int(case["total_points"]) for case in cases), default=0),
            "total_points_max": max((int(case["total_points"]) for case in cases), default=0),
        },
        "cases": cases,
        "matched_case_count": len(matched_cases),
        "failed_case_count": len(failed_cases),
        "all_cases_matched": bool(len(matched_cases) == len(cases)),
        "elapsed_sec": time.perf_counter() - started,
        "claim_boundary": {
            "modelnet40_batch_normalized_contract_claimed": True,
            "algorithm_aware_author_comparator_selection": bool(args.paper_log_repo),
            "modelnet40_all_pairs_reproduced": False,
            "exact_paper_dataset_identity_proved": False,
            "author_vs_rtdl_ratio_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-index", required=True, type=Path)
    parser.add_argument("--modelnet-zip", required=True, type=Path)
    parser.add_argument("--extract-root", required=True, type=Path)
    parser.add_argument("--author-bin", required=True, type=Path)
    parser.add_argument("--author-hybrid-bin", type=Path)
    parser.add_argument("--paper-log-repo", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--max-pairs", type=int, default=5)
    parser.add_argument("--goal-label", default="Goal5223")
    parser.add_argument(
        "--selection-strategy",
        default="smallest_unique_pairs_preferring_distinct_categories",
        choices=(
            "smallest_unique_pairs_preferring_distinct_categories",
            "smallest_unique_pairs",
            "largest_unique_pairs",
            "all_unique_pairs",
        ),
    )
    parser.add_argument("--backend", default="optix", choices=("optix", "numpy"))
    parser.add_argument("--grid-shape", default="16,16,16")
    parser.add_argument("--initial-state", default="local-grid-cell")
    parser.add_argument("--local-grid-seed-executor", default="auto")
    parser.add_argument("--grid-branch-bound-seed-executor", default="auto")
    parser.add_argument("--frontier-nearest-executor", default="auto")
    parser.add_argument("--frontier-row-order", default="native")
    parser.add_argument("--grid-cell-point-order", default="point-id", choices=("point-id", "input-stable"))
    parser.add_argument("--grid-cell-builder", default="numpy", choices=("numpy", "native_cuda"))
    parser.add_argument("--frontier-inline-nearest", action="store_true")
    parser.add_argument("--global-bound-early-break", action="store_true")
    parser.add_argument("--skip-frontier-if-exact-seed", action="store_true")
    parser.add_argument("--max-inline-points", type=int, default=64)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--mbr-tolerance", type=float, default=1e-6)
    parser.add_argument("--author-float32-normalization", action="store_true")
    parser.add_argument("--start-index", type=int)
    parser.add_argument("--end-index", type=int)
    parser.add_argument("--chunk-index", type=int)
    parser.add_argument("--chunk-size", type=int)
    parser.add_argument("--skip-completed", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--aggregate-existing-cases", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "wrote",
        args.summary,
        "matched=",
        summary["all_cases_matched"],
        "cases=",
        summary["matched_case_count"],
        "/",
        summary["selection"]["selected_count"],
    )
    return 0 if summary["all_cases_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
