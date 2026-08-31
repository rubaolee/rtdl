from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
import statistics
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rayjoin_paper_suite import availability_matrix
from rtdsl.rayjoin_paper_suite import build_rayjoin_author_command
from rtdsl.rayjoin_paper_suite import dataset_file
from rtdsl.rayjoin_paper_suite import exact_suite_manifest
from rtdsl.rayjoin_paper_suite import paper_cases
from rtdsl.rayjoin_paper_suite import render_exact_suite_markdown
from rtdsl.rayjoin_paper_suite import run_rayjoin_author_command
from rtdsl.rayjoin_paper_suite import scan_cdb_file
from rtdsl.rayjoin_paper_suite import same_source_arcgis_targets


def _count_from_result(value) -> int:
    if isinstance(value, dict):
        for key in ("count", "row_count"):
            if key in value:
                return int(value[key])
        raise KeyError(f"native result dict does not contain a scalar count: {sorted(value.keys())}")
    return int(value)


def _native_query_seconds(native_timings) -> float | None:
    if native_timings is None:
        return None
    if "traversal" in native_timings:
        return float(native_timings["traversal"])
    segment_pair_phase_keys = (
        "candidate_count_pass",
        "candidate_write_pass",
        "candidate_download",
        "exact_refine",
    )
    if any(key in native_timings for key in segment_pair_phase_keys):
        total = sum(float(native_timings.get(key, 0.0) or 0.0) for key in segment_pair_phase_keys)
        return total if total > 0.0 else None
    return None


def _default_packed_cache_dir(dataset_root: str | Path) -> Path:
    return Path(dataset_root) / ".rtdl_rayjoin_overlay_packed_cache"


@contextmanager
def _packed_cache_partner_env(
    dataset_root: str | Path,
    *,
    packed_cache_dir: str | Path | None,
    disabled: bool,
):
    key = "RTDL_RAYJOIN_OVERLAY_PACKED_CACHE_DIR"
    previous = os.environ.get(key)
    if disabled:
        yield {"enabled": False, "path": None, "source": "disabled"}
        return

    cache_dir = Path(packed_cache_dir) if packed_cache_dir is not None else _default_packed_cache_dir(dataset_root)
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(cache_dir)
    try:
        yield {
            "enabled": True,
            "path": str(cache_dir),
            "source": "cli" if packed_cache_dir is not None else "default_dataset_root",
        }
    finally:
        if previous is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = previous


def _count_hot_runs(label: str, count_fn, timings_fn, *, warmup: int, repeat: int) -> dict[str, object]:
    runs = []
    for iteration in range(warmup + repeat):
        is_warmup = iteration < warmup
        start = time.perf_counter()
        result = count_fn()
        count = _count_from_result(result)
        elapsed = time.perf_counter() - start
        run = {
            "iteration": iteration,
            "is_warmup": is_warmup,
            "elapsed_sec": elapsed,
            "count": count,
            "native_timings": timings_fn(),
        }
        if isinstance(result, dict):
            run["native_result"] = result
        runs.append(run)
    hot = [float(run["elapsed_sec"]) for run in runs if not run["is_warmup"]]
    counts = [int(run["count"]) for run in runs if not run["is_warmup"]]
    native_traversal = [
        native_seconds
        for run in runs
        if not run["is_warmup"]
        for native_seconds in (_native_query_seconds(run["native_timings"]),)
        if native_seconds is not None
    ]
    return {
        "backend": label,
        "warmup": int(warmup),
        "repeat": int(repeat),
        "hot_total_sec": sum(hot),
        "hot_median_sec": statistics.median(hot) if hot else None,
        "hot_min_sec": min(hot) if hot else None,
        "hot_max_sec": max(hot) if hot else None,
        "count": counts[0] if counts else None,
        "counts_stable": len(set(counts)) <= 1,
        "native_traversal_median_sec": statistics.median(native_traversal) if native_traversal else None,
        "runs": runs,
    }


def _run_rtdl_lsi(case, *, dataset_root: str, backend: str, warmup: int, repeat: int) -> dict[str, object]:
    from rtdsl.rayjoin_overlay import _run_lsi_rows
    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs

    base_inputs = load_cdb_overlay_packed_inputs(dataset_file(dataset_root, case.pair.left_relative_path))
    query_inputs = load_cdb_overlay_packed_inputs(dataset_file(dataset_root, case.pair.right_relative_path))
    rows: dict[str, object] = {}

    def count_lsi_rows(one_backend: str):
        last_timings: dict[str, object] = {}

        def count_once() -> dict[str, object]:
            row_array, timings = _run_lsi_rows(
                one_backend,
                base_inputs.segments,
                query_inputs.segments,
                None,
                None,
                left_coords=base_inputs.segment_coords,
                right_coords=query_inputs.segment_coords,
            )
            last_timings.clear()
            last_timings.update(timings)
            return {
                "count": int(len(row_array)),
                "row_count": int(len(row_array)),
                "route": "rayjoin_overlay_lsi_rows",
            }

        return count_once, lambda: dict(last_timings)

    if backend in {"optix", "all"}:
        count_once, timings = count_lsi_rows("optix")
        rows["optix"] = _count_hot_runs(
            "rtdl_optix",
            count_once,
            timings,
            warmup=warmup,
            repeat=repeat,
        )
        rows["optix"]["predicate_contract"] = (
            "rayjoin_author_lsi_intersect_test_endpoint_collinear_contract"
        )
    if backend in {"embree", "all"}:
        count_once, timings = count_lsi_rows("embree")
        rows["embree"] = _count_hot_runs(
            "rtdl_embree",
            count_once,
            timings,
            warmup=warmup,
            repeat=repeat,
        )
        rows["embree"]["predicate_contract"] = (
            "rayjoin_author_lsi_intersect_test_endpoint_collinear_contract"
        )
    return {
        "program": "lsi",
        "input_shape": {
            "base_chains": int(base_inputs.chain_count),
            "query_chains": int(query_inputs.chain_count),
            "base_segments": int(base_inputs.edge_count),
            "query_segments": int(query_inputs.edge_count),
            "query_stream": "all_edges_from_query_map_s",
        },
        "results": rows,
    }


def _run_rtdl_pip(case, *, dataset_root: str, backend: str, warmup: int, repeat: int) -> dict[str, object]:
    import rtdsl as rt
    from rtdsl.rayjoin_overlay import _rayjoin_cdb_point_location_env
    from rtdsl.rayjoin_overlay import _shared_rayjoin_bounds
    from rtdsl.rayjoin_overlay import _directed_segment_point_location_grouping_env
    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs

    base_inputs = load_cdb_overlay_packed_inputs(dataset_file(dataset_root, case.pair.left_relative_path))
    query_inputs = load_cdb_overlay_packed_inputs(dataset_file(dataset_root, case.pair.right_relative_path))
    scale_bounds = _shared_rayjoin_bounds(base_inputs, query_inputs)
    base_segments = base_inputs.cdb_segments
    packed_query_points = query_inputs.points
    rows: dict[str, object] = {}
    with _rayjoin_cdb_point_location_env(1, scale_bounds):
        if backend in {"optix", "all"}:
            with _directed_segment_point_location_grouping_env("optix", (int(packed_query_points.count),)):
                prepared = rt.prepare_directed_segment_point_location_2d_optix(base_segments)
                prepared_points = None
                try:
                    rows["optix"] = _count_hot_runs(
                        "rtdl_optix",
                        lambda: prepared.count_positive_faces(packed_query_points),
                        prepared.last_phase_timings,
                        warmup=warmup,
                        repeat=repeat,
                    )
                    prepared_points = prepared.prepare_query_points(packed_query_points)
                    rows["optix_device_resident"] = _count_hot_runs(
                        "rtdl_optix_device_resident",
                        lambda: prepared.count_positive_faces_device_points(prepared_points),
                        prepared.last_phase_timings,
                        warmup=warmup,
                        repeat=repeat,
                    )
                    rows["optix_device_segment_ids"] = _count_hot_runs(
                        "rtdl_optix_device_segment_ids",
                        lambda: prepared.write_segment_ids_device_points(prepared_points),
                        prepared.last_phase_timings,
                        warmup=warmup,
                        repeat=repeat,
                    )
                    rows["optix_device_segment_ids"]["output_contract"] = (
                        "author_shape_device_resident_closest_segment_id_column_no_host_download_no_positive_count_atomic"
                    )
                finally:
                    if prepared_points is not None:
                        prepared_points.close()
                    prepared.close()
        if backend in {"embree", "all"}:
            prepared = rt.prepare_directed_segment_point_location_2d_embree(base_segments)
            try:
                rows["embree"] = _count_hot_runs(
                    "rtdl_embree",
                    lambda: prepared.count_positive_faces(packed_query_points),
                    prepared.last_phase_timings,
                    warmup=warmup,
                    repeat=repeat,
                )
            finally:
                prepared.close()
    return {
        "program": "pip",
        "input_shape": {
            "base_chains": base_inputs.chain_count,
            "query_chains": query_inputs.chain_count,
            "base_cdb_segments": base_inputs.edge_count,
            "query_points": query_inputs.point_count,
            "query_stream": "all_points_from_query_map_s",
        },
        "results": rows,
    }


def _overlay_phase_medians(hot_results: list[dict[str, object]]) -> dict[str, float]:
    keys = {
        key
        for result in hot_results
        for key in (result.get("phase_seconds") or {})
        if isinstance((result.get("phase_seconds") or {}).get(key), (int, float))
    }
    medians: dict[str, float] = {}
    for key in sorted(keys):
        values = [float((result.get("phase_seconds") or {}).get(key)) for result in hot_results if key in (result.get("phase_seconds") or {})]
        if values:
            medians[key] = statistics.median(values)
    return medians


def _summarize_overlay_backend_runs(
    backend: str,
    runs: list[dict[str, object]],
    *,
    warmup: int,
    repeat: int,
) -> dict[str, object]:
    hot_runs = [run for run in runs if not run["is_warmup"]]
    if not hot_runs:
        hot_runs = list(runs)
    hot_results = [run["result"] for run in hot_runs]
    totals = [float((result.get("phase_seconds") or {}).get("total_sec")) for result in hot_results]
    representative_index = sorted(range(len(hot_results)), key=lambda index: totals[index])[len(hot_results) // 2]
    representative = dict(hot_results[representative_index])
    phase_medians = _overlay_phase_medians(hot_results)
    load_pack = phase_medians.get("load_pack_inputs_sec", phase_medians.get("pack_inputs_sec", 0.0))
    total = phase_medians.get("total_sec")
    representative.update(
        {
            "backend": backend,
            "warmup": int(warmup),
            "repeat": int(repeat),
            "total_median_sec": total,
            "total_min_sec": min(totals) if totals else None,
            "total_max_sec": max(totals) if totals else None,
            "load_pack_median_sec": load_pack,
            "compute_without_load_pack_median_sec": (total - load_pack) if total is not None else None,
            "phase_median_seconds": phase_medians,
            "runs": runs,
        }
    )
    return representative


def _run_rtdl_overlay(
    case,
    *,
    dataset_root: str,
    backend: str,
    assemble_output: bool,
    output_path: Path | None,
    warmup: int,
    repeat: int,
) -> dict[str, object]:
    import rtdsl as rt
    from rtdsl.rayjoin_overlay import run_rayjoin_overlay_rtdl
    from rtdsl.rayjoin_overlay import run_rayjoin_overlay_rtdl_from_cdb_paths

    left_path = dataset_file(dataset_root, case.pair.left_relative_path)
    right_path = dataset_file(dataset_root, case.pair.right_relative_path)
    left = None
    right = None
    if assemble_output or output_path is not None:
        left = rt.load_cdb(left_path)
        right = rt.load_cdb(right_path)

    def run_one(one_backend: str, one_output: Path | None):
        if assemble_output or one_output is not None:
            return run_rayjoin_overlay_rtdl(
                left,
                right,
                backend=one_backend,
                assemble_output=assemble_output,
                output_path=one_output,
            )
        return run_rayjoin_overlay_rtdl_from_cdb_paths(
            left_path,
            right_path,
            backend=one_backend,
        )

    def run_backend(one_backend: str) -> dict[str, object]:
        runs = []
        for iteration in range(int(warmup) + int(repeat)):
            is_warmup = iteration < int(warmup)
            one_output = None
            if output_path is not None:
                suffix = output_path.suffix or ".txt"
                output_stem = f"{output_path.stem}_{one_backend}"
                if int(warmup) + int(repeat) > 1:
                    output_stem = f"{output_stem}_iter{iteration}"
                one_output = output_path.with_name(f"{output_stem}{suffix}")
            result = run_one(one_backend, one_output)
            runs.append(
                {
                    "iteration": iteration,
                    "is_warmup": is_warmup,
                    "result": result,
                }
            )
        return _summarize_overlay_backend_runs(
            one_backend,
            runs,
            warmup=warmup,
            repeat=repeat,
        )

    if backend == "all":
        return {
            "program": "overlay",
            "results": {one_backend: run_backend(one_backend) for one_backend in ("optix", "embree")},
        }
    return run_backend(backend)


def _split_csv(value: str | None) -> tuple[str, ...] | None:
    if value is None or value.strip() == "":
        return None
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _case_by_id(case_id: str):
    for case in paper_cases():
        if case.case_id == case_id:
            return case
    raise SystemExit(f"unknown case id: {case_id}")


def _write_payload(path: Path | None, payload: dict[str, object]) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path is None:
        print(text, end="")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def cmd_manifest(args: argparse.Namespace) -> None:
    payload = exact_suite_manifest(args.dataset_root)
    if args.output_json is not None:
        _write_payload(args.output_json, payload)
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.output_md is not None:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_exact_suite_markdown(payload), encoding="utf-8")


def cmd_availability(args: argparse.Namespace) -> None:
    rows = availability_matrix(
        args.dataset_root,
        pair_ids=_split_csv(args.pairs),
        program_ids=_split_csv(args.programs),
    )
    payload = {
        "schema": "rtdl.rayjoin_paper_suite.availability.v1",
        "dataset_root": str(args.dataset_root),
        "rows": [row.__dict__ | {"left": row.left.__dict__, "right": row.right.__dict__} for row in rows],
    }
    _write_payload(args.output_json, payload)


def cmd_commands(args: argparse.Namespace) -> None:
    rows = []
    for case in paper_cases(pair_ids=_split_csv(args.pairs), program_ids=_split_csv(args.programs)):
        command = build_rayjoin_author_command(
            case,
            dataset_root=args.dataset_root,
            query_exec=args.query_exec,
            polyover_exec=args.polyover_exec,
            mode=args.mode,
            serialize_prefix=args.serialize_prefix,
            grid_size=args.grid_size,
            xsect_factor=args.xsect_factor,
            enlarge=args.enlarge,
            warmup=args.warmup,
            repeat=args.repeat,
            check=args.check,
        )
        rows.append(command.__dict__ | {"command": list(command.command)})
    payload = {
        "schema": "rtdl.rayjoin_paper_suite.author_commands.v1",
        "dataset_root": str(args.dataset_root),
        "mode": args.mode,
        "rows": rows,
    }
    _write_payload(args.output_json, payload)


def cmd_scan_cdb(args: argparse.Namespace) -> None:
    stats = [scan_cdb_file(path).__dict__ for path in args.paths]
    _write_payload(
        args.output_json,
        {
            "schema": "rtdl.rayjoin_paper_suite.cdb_scan.v1",
            "files": stats,
        },
    )


def cmd_run_author(args: argparse.Namespace) -> None:
    case = _case_by_id(args.case_id)
    command = build_rayjoin_author_command(
        case,
        dataset_root=args.dataset_root,
        query_exec=args.query_exec,
        polyover_exec=args.polyover_exec,
        mode=args.mode,
        serialize_prefix=args.serialize_prefix,
        grid_size=args.grid_size,
        xsect_factor=args.xsect_factor,
        enlarge=args.enlarge,
        warmup=args.warmup,
        repeat=args.repeat,
        check=args.check,
        output_path=args.overlay_output,
    )
    result = run_rayjoin_author_command(command)
    _write_payload(args.output_json, result)


def cmd_run_rtdl(args: argparse.Namespace) -> None:
    case = _case_by_id(args.case_id)
    with _packed_cache_partner_env(
        args.dataset_root,
        packed_cache_dir=args.packed_cache_dir,
        disabled=args.disable_packed_cache,
    ) as packed_cache:
        if case.program.program_id == "lsi":
            result = _run_rtdl_lsi(
                case,
                dataset_root=args.dataset_root,
                backend=args.backend,
                warmup=args.warmup,
                repeat=args.repeat,
            )
        elif case.program.program_id == "overlay":
            result = _run_rtdl_overlay(
                case,
                dataset_root=args.dataset_root,
                backend=args.backend,
                assemble_output=args.assemble_overlay_output,
                output_path=args.overlay_output,
                warmup=args.warmup,
                repeat=args.repeat,
            )
        elif case.program.program_id == "pip":
            result = _run_rtdl_pip(
                case,
                dataset_root=args.dataset_root,
                backend=args.backend,
                warmup=args.warmup,
                repeat=args.repeat,
            )
        else:
            raise SystemExit(f"unsupported RTDL program: {case.program.program_id}")
    payload = {
        "schema": "rtdl.rayjoin_paper_suite.rtdl_run.v1",
        "case_id": case.case_id,
        "pair_id": case.pair.pair_id,
        "paper_label": case.pair.paper_label,
        "input_provenance": args.input_provenance,
        "dataset_root": str(args.dataset_root),
        "partner_cache": packed_cache,
        "program_contract": case.program.input_contract,
        **result,
    }
    _write_payload(args.output_json, payload)


def cmd_build_arcgis_cdb_tree(args: argparse.Namespace) -> None:
    import rtdsl as rt

    staged_root = Path(args.staged_root)
    dataset_root = Path(args.dataset_root)
    rows = []
    for target in same_source_arcgis_targets(_split_csv(args.targets)):
        source_root = staged_root / target.source_asset_id
        if not source_root.exists():
            raise SystemExit(f"missing staged ArcGIS source directory: {source_root}")
        dataset = rt.arcgis_pages_to_cdb(
            source_root,
            name=target.cdb_name,
            feature_id_field=target.feature_id_field,
            ignore_invalid_tail=args.ignore_invalid_tail,
            topology_mode=args.topology_mode,
        )
        output_path = dataset_root / target.output_relative_path
        rt.write_cdb(dataset, output_path)
        stats = scan_cdb_file(output_path)
        rows.append(
            {
                "target": target.__dict__,
                "source_root": str(source_root),
                "output_path": str(output_path),
                "stats": stats.__dict__,
            }
        )
    payload = {
        "schema": "rtdl.rayjoin_paper_suite.same_source_arcgis_cdb_tree.v1",
        "input_provenance": "same_source_regenerated_cdb",
        "staged_root": str(staged_root),
        "dataset_root": str(dataset_root),
        "rows": rows,
    }
    _write_payload(args.output_json, payload)


def _add_common_dataset(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dataset-root", required=True)


def _add_rayjoin_execs(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--query-exec", required=True)
    parser.add_argument("--polyover-exec", required=True)


def _add_rayjoin_params(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mode", choices=("grid", "lbvh", "rt"), default="rt")
    parser.add_argument("--serialize-prefix", default="/dev/shm")
    parser.add_argument("--grid-size", type=int, default=15000)
    parser.add_argument("--xsect-factor", default="0.1")
    parser.add_argument("--enlarge", default="3.5")
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--check", action="store_true")


def main() -> None:
    parser = argparse.ArgumentParser(description="RayJoin exact paper reproduction suite helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    manifest = subparsers.add_parser("manifest")
    _add_common_dataset(manifest)
    manifest.add_argument("--output-json", type=Path)
    manifest.add_argument("--output-md", type=Path)
    manifest.set_defaults(func=cmd_manifest)

    availability = subparsers.add_parser("availability")
    _add_common_dataset(availability)
    availability.add_argument("--pairs")
    availability.add_argument("--programs")
    availability.add_argument("--output-json", type=Path)
    availability.set_defaults(func=cmd_availability)

    commands = subparsers.add_parser("commands")
    _add_common_dataset(commands)
    _add_rayjoin_execs(commands)
    _add_rayjoin_params(commands)
    commands.add_argument("--pairs")
    commands.add_argument("--programs")
    commands.add_argument("--output-json", type=Path)
    commands.set_defaults(func=cmd_commands)

    scan = subparsers.add_parser("scan-cdb")
    scan.add_argument("paths", nargs="+", type=Path)
    scan.add_argument("--output-json", type=Path)
    scan.set_defaults(func=cmd_scan_cdb)

    run_author = subparsers.add_parser("run-author")
    _add_common_dataset(run_author)
    _add_rayjoin_execs(run_author)
    _add_rayjoin_params(run_author)
    run_author.add_argument("--case-id", required=True)
    run_author.add_argument("--overlay-output", type=Path)
    run_author.add_argument("--output-json", type=Path)
    run_author.set_defaults(func=cmd_run_author)

    run_rtdl = subparsers.add_parser("run-rtdl")
    _add_common_dataset(run_rtdl)
    run_rtdl.add_argument("--case-id", required=True)
    run_rtdl.add_argument("--backend", choices=("optix", "embree", "all"), default="all")
    run_rtdl.add_argument("--warmup", type=int, default=5)
    run_rtdl.add_argument("--repeat", type=int, default=5)
    run_rtdl.add_argument(
        "--assemble-overlay-output",
        action="store_true",
        help="Also assemble RayJoin output chains. Default mirrors polyover_exec without -output.",
    )
    run_rtdl.add_argument("--overlay-output", type=Path)
    run_rtdl.add_argument(
        "--packed-cache-dir",
        type=Path,
        help=(
            "Directory for the RayJoin CDB packed-array partner cache. "
            "Defaults to <dataset-root>/.rtdl_rayjoin_overlay_packed_cache."
        ),
    )
    run_rtdl.add_argument(
        "--disable-packed-cache",
        action="store_true",
        help="Disable the RayJoin CDB packed-array partner cache for this run.",
    )
    run_rtdl.add_argument(
        "--input-provenance",
        choices=("paper_preprocessed_cdb", "same_source_regenerated_cdb", "fixture_or_synthetic"),
        default="paper_preprocessed_cdb",
    )
    run_rtdl.add_argument("--output-json", type=Path)
    run_rtdl.set_defaults(func=cmd_run_rtdl)

    build_arcgis = subparsers.add_parser("build-arcgis-cdb-tree")
    build_arcgis.add_argument("--staged-root", required=True)
    _add_common_dataset(build_arcgis)
    build_arcgis.add_argument(
        "--targets",
        default="county,zipcode",
        help="Comma-separated same-source ArcGIS target ids.",
    )
    build_arcgis.add_argument("--ignore-invalid-tail", action="store_true")
    build_arcgis.add_argument(
        "--topology-mode",
        choices=("rings", "polygon_to_line"),
        default="polygon_to_line",
        help="Use polygon_to_line for RayJoin-style left/right-face CDB generation.",
    )
    build_arcgis.add_argument("--output-json", type=Path)
    build_arcgis.set_defaults(func=cmd_build_arcgis_cdb_tree)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
