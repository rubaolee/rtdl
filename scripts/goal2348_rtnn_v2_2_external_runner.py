from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIMING_RE = re.compile(r"^time\s+(?P<name>.*?):\s+(?P<ms>[0-9]+(?:\.[0-9]+)?)\s+ms\s*$")


def generate_uniform_point_file(
    path: Path,
    *,
    point_count: int,
    dimension: int,
    seed: int,
    z_value: float = 0.0,
) -> dict[str, object]:
    if point_count < 0:
        raise ValueError("point_count must be non-negative")
    if dimension not in (2, 3):
        raise ValueError("dimension must be 2 or 3")
    rng = random.Random(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for _ in range(point_count):
            x = rng.random()
            y = rng.random()
            z = rng.random() if dimension == 3 else float(z_value)
            handle.write(f"{x:.9f},{y:.9f},{z:.9f}\n")
    return {
        "path": str(path),
        "point_count": point_count,
        "dimension": dimension,
        "seed": seed,
        "format": "rtnn_csv_xyz",
    }


def generate_point_file(
    path: Path,
    *,
    point_count: int,
    dimension: int,
    seed: int,
    distribution: str,
    z_value: float = 0.0,
    cluster_count: int = 8,
    cluster_stddev: float = 0.035,
) -> dict[str, object]:
    if point_count < 0:
        raise ValueError("point_count must be non-negative")
    if dimension not in (2, 3):
        raise ValueError("dimension must be 2 or 3")
    if distribution == "uniform":
        return generate_uniform_point_file(path, point_count=point_count, dimension=dimension, seed=seed, z_value=z_value)
    if distribution not in ("clustered", "shell"):
        raise ValueError("distribution must be uniform, clustered, or shell")

    rng = random.Random(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    centers = [
        tuple(rng.uniform(0.12, 0.88) for _ in range(dimension))
        for _ in range(max(1, cluster_count))
    ]
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx in range(point_count):
            if distribution == "clustered":
                center = centers[idx % len(centers)]
                coords = [
                    min(1.0, max(0.0, rng.gauss(center[axis], cluster_stddev)))
                    for axis in range(dimension)
                ]
            else:
                # A thin spherical/circular shell stresses non-uniform surface-like
                # neighborhoods without introducing paper-dataset provenance claims.
                if dimension == 2:
                    angle = rng.random() * 6.283185307179586
                    radius = min(0.49, max(0.0, rng.gauss(0.34, 0.025)))
                    coords = [0.5 + radius * math.cos(angle), 0.5 + radius * math.sin(angle)]
                else:
                    theta = rng.random() * 6.283185307179586
                    z = rng.uniform(-1.0, 1.0)
                    radial = math.sqrt(max(0.0, 1.0 - z * z))
                    radius = min(0.49, max(0.0, rng.gauss(0.34, 0.025)))
                    coords = [
                        0.5 + radius * radial * math.cos(theta),
                        0.5 + radius * radial * math.sin(theta),
                        0.5 + radius * z,
                    ]
            if dimension == 2:
                coords.append(float(z_value))
            handle.write(f"{coords[0]:.9f},{coords[1]:.9f},{coords[2]:.9f}\n")
    return {
        "path": str(path),
        "point_count": point_count,
        "dimension": dimension,
        "seed": seed,
        "distribution": distribution,
        "format": "rtnn_csv_xyz",
        "cluster_count": cluster_count if distribution == "clustered" else None,
        "cluster_stddev": cluster_stddev if distribution == "clustered" else None,
    }


def parse_rtnn_timings(text: str) -> dict[str, list[float]]:
    timings: dict[str, list[float]] = {}
    for raw_line in text.splitlines():
        match = TIMING_RE.match(raw_line.strip())
        if not match:
            continue
        name = " ".join(match.group("name").split())
        timings.setdefault(name, []).append(float(match.group("ms")))
    return timings


def _timing_summary(timings: dict[str, list[float]]) -> dict[str, object]:
    return {
        key: {
            "count": len(values),
            "total_ms": sum(values),
            "last_ms": values[-1],
            "values_ms": values,
        }
        for key, values in sorted(timings.items())
    }


def _insert_after(text: str, anchor: str, addition: str) -> tuple[str, bool]:
    if addition in text:
        return text, False
    if anchor not in text:
        raise ValueError(f"anchor not found: {anchor!r}")
    return text.replace(anchor, anchor + addition, 1), True


def _insert_after_last_prefixed_line(text: str, prefix: str, addition: str) -> tuple[str, bool]:
    if addition in text:
        return text, False
    lines = text.splitlines(keepends=True)
    insert_at = None
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            insert_at = index + 1
    if insert_at is None:
        raise ValueError(f"prefix anchor not found: {prefix!r}")
    lines.insert(insert_at, addition)
    return "".join(lines), True


def _insert_before_first_prefixed_line(text: str, prefix: str, addition: str) -> tuple[str, bool]:
    if addition in text:
        return text, False
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines.insert(index, addition)
            return "".join(lines), True
    raise ValueError(f"prefix anchor not found: {prefix!r}")


def patch_rtnn_cuda12_checkout(rtnn_root: Path) -> dict[str, object]:
    """Apply compatibility-only patches to a disposable external RTNN checkout.

    RTNN's upstream code targets an older CUDA/Thrust/NVRTC stack. The patches
    here do not change RTNN algorithms; they only add missing Thrust headers and
    use CUDA's modern device intrinsic spellings so the reference executable can
    build/run on CUDA 12 pods used for RTDL comparison work.
    """
    patches: list[dict[str, object]] = []

    edits = [
        (
            rtnn_root / "src" / "optixNSearch" / "thrust_helper.cu",
            [
                "#include <thrust/count.h>\n",
                "#include <thrust/unique.h>\n",
                "#include <thrust/tuple.h>\n",
            ],
        ),
        (
            rtnn_root / "src" / "optixNSearch" / "sort.cpp",
            ["#include <thrust/host_vector.h>\n"],
        ),
    ]
    for path, additions in edits:
        text = path.read_text(encoding="utf-8")
        changed = False
        for addition in additions:
            text, did_change = _insert_after_last_prefixed_line(text, "#include <thrust/", addition)
            changed = changed or did_change
        if changed:
            path.write_text(text, encoding="utf-8", newline="\n")
        patches.append({"path": str(path), "changed": changed, "kind": "missing_thrust_include"})

    arch_macro = (
        "#ifndef __CUDA_ARCH_LIST__\n"
        "#define __CUDA_ARCH_LIST__ 600\n"
        "#endif\n"
    )
    for path in [
        rtnn_root / "src" / "optixNSearch" / "func.h",
        rtnn_root / "src" / "optixNSearch" / "search.cpp",
        rtnn_root / "src" / "optixNSearch" / "sort.cpp",
        rtnn_root / "src" / "optixNSearch" / "util.cpp",
    ]:
        text = path.read_text(encoding="utf-8")
        text, changed = _insert_before_first_prefixed_line(text, "#include <thrust/", arch_macro)
        if changed:
            path.write_text(text, encoding="utf-8", newline="\n")
        patches.append({"path": str(path), "changed": changed, "kind": "thrust_cuda_arch_namespace"})

    geometry = rtnn_root / "src" / "optixNSearch" / "geometry.cu"
    text = geometry.read_text(encoding="utf-8")
    patched = re.sub(r"(?<!_)uint_as_float\(", "__uint_as_float(", text)
    patched = re.sub(
        r"(?<!_)float_as_uint\(",
        "__float_as_uint(",
        patched,
    )
    changed = patched != text
    if changed:
        geometry.write_text(patched, encoding="utf-8", newline="\n")
    patches.append({"path": str(geometry), "changed": changed, "kind": "nvrtc_intrinsic_spelling"})

    return {
        "runner": "goal2348_rtnn_v2_2_external_runner",
        "operation": "patch-rtnn-cuda12",
        "rtnn_root": str(rtnn_root),
        "patches": patches,
        "changed_count": sum(1 for patch in patches if patch["changed"]),
        "claim_boundary": {
            "external_rtnn_source_patch_only": True,
            "rtdl_source_changed": False,
            "algorithm_changed": False,
        },
    }


def build_rtnn_command(args: argparse.Namespace) -> list[str]:
    command = [
        str(args.rtnn_binary),
        "-f",
        str(args.point_file),
        "-sm",
        args.search_mode,
        "-d",
        str(args.device),
        "-r",
        str(args.radius),
        "-p",
        "1" if args.partition else "0",
        "-ab",
        "1" if args.auto_batch else "0",
        "-a",
        str(args.approx_mode),
    ]
    if args.query_file is not None:
        command.extend(["-q", str(args.query_file)])
    if args.search_mode == "radius":
        command.extend(["-k", str(args.k_max)])
    if args.extra_rtnn_arg:
        command.extend(args.extra_rtnn_arg)
    return command


def _read_xyz_columns(path: Path) -> tuple[list[int], list[float], list[float], list[float]]:
    ids: list[int] = []
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            if not line.strip():
                continue
            x, y, z = (float(part) for part in line.strip().split(","))
            ids.append(idx)
            xs.append(x)
            ys.append(y)
            zs.append(z)
    return ids, xs, ys, zs


def _slice_columns(
    columns: tuple[list[int], list[float], list[float], list[float]],
    begin: int,
    end: int,
) -> tuple[list[int], list[float], list[float], list[float]]:
    ids, xs, ys, zs = columns
    return ids[begin:end], xs[begin:end], ys[begin:end], zs[begin:end]


def _take_columns(
    columns: tuple[list[int], list[float], list[float], list[float]],
    indices: list[int],
) -> tuple[list[int], list[float], list[float], list[float]]:
    ids, xs, ys, zs = columns
    return (
        [ids[index] for index in indices],
        [xs[index] for index in indices],
        [ys[index] for index in indices],
        [zs[index] for index in indices],
    )


def _xyz_bounds(
    *column_sets: tuple[list[int], list[float], list[float], list[float]],
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for columns in column_sets:
        xs.extend(columns[1])
        ys.extend(columns[2])
        zs.extend(columns[3])
    if not xs:
        return (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def _grid_cell_key(
    x: float,
    y: float,
    z: float,
    *,
    mins: tuple[float, float, float],
    cell_sizes: tuple[float, float, float],
    divisions: int,
) -> tuple[int, int, int]:
    def index(value: float, axis: int) -> int:
        size = cell_sizes[axis]
        if size <= 0:
            return 0
        return max(0, min(divisions - 1, int((value - mins[axis]) / size)))

    return index(x, 0), index(y, 1), index(z, 2)


def _grid_groups(
    columns: tuple[list[int], list[float], list[float], list[float]],
    *,
    mins: tuple[float, float, float],
    maxs: tuple[float, float, float],
    divisions: int,
) -> tuple[dict[tuple[int, int, int], list[int]], tuple[float, float, float]]:
    if divisions <= 0:
        raise ValueError("partition divisions must be positive")
    spans = tuple(max(1e-12, maxs[axis] - mins[axis]) for axis in range(3))
    cell_sizes = tuple(spans[axis] / divisions for axis in range(3))
    groups: dict[tuple[int, int, int], list[int]] = {}
    _, xs, ys, zs = columns
    for index, (x, y, z) in enumerate(zip(xs, ys, zs)):
        key = _grid_cell_key(x, y, z, mins=mins, cell_sizes=cell_sizes, divisions=divisions)
        groups.setdefault(key, []).append(index)
    return groups, cell_sizes


def _neighbor_search_indices(
    key: tuple[int, int, int],
    *,
    search_groups: dict[tuple[int, int, int], list[int]],
    mins: tuple[float, float, float],
    cell_sizes: tuple[float, float, float],
    divisions: int,
    radius: float,
) -> list[int]:
    ranges = []
    for axis, cell in enumerate(key):
        cell_min = mins[axis] + cell * cell_sizes[axis]
        cell_max = mins[axis] + (cell + 1) * cell_sizes[axis]
        lo = max(0, int(math.floor((cell_min - radius - mins[axis]) / cell_sizes[axis])))
        hi = min(divisions - 1, int(math.floor((cell_max + radius - mins[axis]) / cell_sizes[axis])))
        ranges.append(range(lo, hi + 1))
    indices: list[int] = []
    for ix in ranges[0]:
        for iy in ranges[1]:
            for iz in ranges[2]:
                indices.extend(search_groups.get((ix, iy, iz), ()))
    return indices


def run_rtnn(args: argparse.Namespace) -> dict[str, object]:
    command = build_rtnn_command(args)
    env = os.environ.copy()
    if args.rtnn_library_dir:
        env["LD_LIBRARY_PATH"] = f"{args.rtnn_library_dir}:{env.get('LD_LIBRARY_PATH', '')}"
    print(f"[goal2348] RTNN start: {' '.join(command)}", flush=True)
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=args.rtnn_cwd or None,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=args.timeout_sec,
        check=False,
    )
    elapsed_sec = time.perf_counter() - started
    print(
        f"[goal2348] RTNN done returncode={completed.returncode} elapsed_sec={elapsed_sec:.6f}",
        flush=True,
    )
    combined = completed.stdout + "\n" + completed.stderr
    timings = parse_rtnn_timings(combined)
    return {
        "runner": "goal2348_rtnn_v2_2_external_runner",
        "row": args.row_label,
        "external": "RTNN",
        "returncode": completed.returncode,
        "elapsed_sec": elapsed_sec,
        "command": command,
        "search_mode": args.search_mode,
        "radius": args.radius,
        "k_max": args.k_max,
        "partition": bool(args.partition),
        "auto_batch": bool(args.auto_batch),
        "approx_mode": int(args.approx_mode),
        "timings": _timing_summary(timings),
        "stdout_tail": completed.stdout.splitlines()[-80:],
        "stderr_tail": completed.stderr.splitlines()[-80:],
        "claim_boundary": {
            "full_rtnn_reproduction": False,
            "rtdl_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "requires_same_hardware_rtdl_row": True,
        },
    }


def run_rtdl_current_2d_smoke(args: argparse.Namespace) -> dict[str, object]:
    """Run the current 2-D RTDL fixed-radius count path if the OptiX library exists.

    This is deliberately a smoke row, not a paper-equivalent RTNN row. RTNN's
    serious rows are 3-D radius+K neighbor-search rows; current RTDL v2.1 does
    not yet expose that exact fast OptiX contract.
    """
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    import rtdsl as rt  # noqa: PLC0415

    def _load_points(path: Path):
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle):
                x, y, _z = (float(part) for part in line.strip().split(","))
                rows.append({"id": idx, "x": x, "y": y})
        return tuple(rows)

    query_file = args.query_file or args.point_file
    points = _load_points(args.point_file)
    queries = points if query_file == args.point_file else _load_points(query_file)
    print(
        f"[goal2348] RTDL current 2D smoke start queries={len(queries)} points={len(points)}",
        flush=True,
    )
    started = time.perf_counter()
    try:
        rows = rt.fixed_radius_count_threshold_2d_optix(
            queries,
            points,
            radius=args.radius,
            threshold=args.threshold,
        )
        ok = True
        error = ""
    except Exception as exc:  # pragma: no cover - hardware/library path
        rows = ()
        ok = False
        error = repr(exc)
    elapsed_sec = time.perf_counter() - started
    print(f"[goal2348] RTDL current 2D smoke done ok={ok} sec={elapsed_sec:.6f}", flush=True)
    return {
        "runner": "goal2348_rtnn_v2_2_external_runner",
        "row": args.row_label,
        "external": "RTDL current",
        "mode": "current_2d_fixed_radius_count_threshold_optix_smoke",
        "ok": ok,
        "elapsed_sec": elapsed_sec,
        "query_count": len(queries),
        "search_count": len(points),
        "radius": args.radius,
        "threshold": args.threshold,
        "row_count": len(rows),
        "error": error,
        "claim_boundary": {
            "paper_equivalent_rtnn_row": False,
            "rtdl_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
        },
    }


def run_rtdl_current_3d_neighbors_smoke(args: argparse.Namespace) -> dict[str, object]:
    """Run RTDL's current 3-D fixed-radius neighbor path.

    This is a useful current-implementation baseline. Current main defaults to
    the generic uniform-cell bounded-neighbor path; setting
    RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_RT probes the simple custom-primitive
    OptiX traversal, and RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_CUDA keeps the older
    CUDA all-pairs path available for diagnostics.
    """
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    import rtdsl as rt  # noqa: PLC0415

    radius = float(args.radius)
    k_max = int(args.k_max)
    result_mode = getattr(args, "result_mode", "dict")
    execution_mode = getattr(args, "execution_mode", "run-optix")
    repeat = int(getattr(args, "repeat", 1))

    @rt.kernel(backend="rtdl", precision="float_approx")
    def _goal2348_current_fixed_radius_neighbors_3d():
        query_points = rt.input("query_points", rt.Points3D, role="probe")
        search_points = rt.input("search_points", rt.Points3D, role="build")
        candidates = rt.traverse(query_points, search_points, accel="bvh")
        hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=radius, k_max=k_max))
        return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])

    def _load_points(path: Path):
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle):
                x, y, z = (float(part) for part in line.strip().split(","))
                rows.append({"id": idx, "x": x, "y": y, "z": z})
        return tuple(rows)

    def _load_packed_points(path: Path):
        ids = []
        xs = []
        ys = []
        zs = []
        with path.open("r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle):
                x, y, z = (float(part) for part in line.strip().split(","))
                ids.append(idx)
                xs.append(x)
                ys.append(y)
                zs.append(z)
        return rt.pack_points(ids=ids, x=xs, y=ys, z=zs, dimension=3)

    query_file = args.query_file or args.point_file
    input_mode = getattr(args, "input_mode", "records")
    pack_started = time.perf_counter()
    if input_mode == "packed-columns":
        points = _load_packed_points(args.point_file)
        queries = points if query_file == args.point_file else _load_packed_points(query_file)
        point_count = int(points.count)
        query_count = int(queries.count)
    else:
        points = _load_points(args.point_file)
        queries = points if query_file == args.point_file else _load_points(query_file)
        point_count = len(points)
        query_count = len(queries)
    input_pack_sec = time.perf_counter() - pack_started
    execution_prepare_sec = 0.0
    prepared_execution = None
    prepare_error = ""
    if execution_mode == "prepared-optix":
        prepare_started = time.perf_counter()
        try:
            prepared_execution = rt.prepare_optix(_goal2348_current_fixed_radius_neighbors_3d).bind(
                query_points=queries,
                search_points=points,
            )
        except Exception as exc:  # pragma: no cover - hardware/library path
            prepare_error = repr(exc)
        execution_prepare_sec = time.perf_counter() - prepare_started
    elif execution_mode == "native-prepared-optix":
        prepare_started = time.perf_counter()
        try:
            prepared_execution = rt.prepare_optix_fixed_radius_neighbors_3d(
                points,
                max_radius=radius,
            )
        except Exception as exc:  # pragma: no cover - hardware/library path
            prepare_error = repr(exc)
        execution_prepare_sec = time.perf_counter() - prepare_started
    print(
        f"[goal2348] RTDL current 3D neighbors smoke start queries={query_count} "
        f"points={point_count} input_mode={input_mode} execution_mode={execution_mode}",
        flush=True,
    )
    elapsed_runs = []
    row_count = 0
    distance_summary = None
    ok = not prepare_error
    error = prepare_error
    phase_timings = None
    for run_index in range(repeat if ok else 0):
        started = time.perf_counter()
        try:
            if prepared_execution is not None:
                if execution_mode == "native-prepared-optix":
                    if result_mode == "count":
                        row_count = prepared_execution.count(queries, radius=radius, k_max=k_max)
                        rows = None
                        distance_summary = None
                    elif result_mode == "summary":
                        distance_summary = prepared_execution.summary(queries, radius=radius, k_max=k_max)
                        row_count = int(distance_summary["count"])
                        rows = None
                    elif result_mode == "exact-raw":
                        rows = prepared_execution.run_exact_raw(queries, radius=radius, k_max=k_max)
                        distance_summary = None
                    elif result_mode == "exact-dict":
                        rows = prepared_execution.run_exact(queries, radius=radius, k_max=k_max)
                        distance_summary = None
                    elif result_mode == "ranked-raw":
                        rows = prepared_execution.run_ranked_raw(queries, radius=radius, k_max=k_max)
                        distance_summary = None
                    elif result_mode == "ranked-dict":
                        rows = prepared_execution.run_ranked(queries, radius=radius, k_max=k_max)
                        distance_summary = None
                    elif result_mode == "ranked-summary-raw":
                        rows = prepared_execution.run_ranked_summary_raw(queries, radius=radius, k_max=k_max)
                        distance_summary = None
                    elif result_mode == "ranked-summary-dict":
                        rows = prepared_execution.run_ranked_summary(queries, radius=radius, k_max=k_max)
                        distance_summary = None
                    else:
                        rows = (
                            prepared_execution.run_raw(queries, radius=radius, k_max=k_max)
                            if result_mode == "raw"
                            else prepared_execution.run(queries, radius=radius, k_max=k_max)
                        )
                        distance_summary = None
                else:
                    if result_mode in ("count", "summary", "exact-raw", "exact-dict", "ranked-raw", "ranked-dict", "ranked-summary-raw", "ranked-summary-dict"):
                        raise ValueError("ranked/count/summary result modes require execution_mode='native-prepared-optix'")
                    rows = prepared_execution.run_raw() if result_mode == "raw" else prepared_execution.run()
                    distance_summary = None
            else:
                if result_mode in ("count", "summary", "exact-raw", "exact-dict", "ranked-raw", "ranked-dict", "ranked-summary-raw", "ranked-summary-dict"):
                    raise ValueError("ranked/count/summary result modes require execution_mode='native-prepared-optix'")
                rows = rt.run_optix(
                    _goal2348_current_fixed_radius_neighbors_3d,
                    result_mode=result_mode,
                    query_points=queries,
                    search_points=points,
                )
                distance_summary = None
            if result_mode not in ("count", "summary"):
                row_count = len(rows)
            phase_timings = rt.get_last_fixed_radius_neighbors_3d_phase_timings()
            if result_mode in ("raw", "exact-raw", "ranked-raw", "ranked-summary-raw") and rows is not None:
                rows.close()
        except Exception as exc:  # pragma: no cover - hardware/library path
            row_count = 0
            ok = False
            error = repr(exc)
            elapsed_runs.append(time.perf_counter() - started)
            break
        elapsed_runs.append(time.perf_counter() - started)
        print(
            f"[goal2348] RTDL current 3D neighbors repeat {run_index + 1}/{repeat} "
            f"ok=True sec={elapsed_runs[-1]:.6f}",
            flush=True,
        )
    elapsed_sec = elapsed_runs[-1] if elapsed_runs else 0.0
    close_prepared = getattr(prepared_execution, "close", None)
    if callable(close_prepared):
        close_prepared()
    print(f"[goal2348] RTDL current 3D neighbors smoke done ok={ok} sec={elapsed_sec:.6f}", flush=True)
    forced_cuda = os.environ.get("RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_CUDA") is not None
    forced_rt = os.environ.get("RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_RT") is not None
    if forced_cuda:
        current_native_path = "CUDA fixed-radius neighbor kernel behind OptiX runtime wrapper"
    elif forced_rt:
        current_native_path = "generic OptiX custom-primitive bounded-neighbor traversal"
    elif execution_mode == "native-prepared-optix" and result_mode == "count":
        current_native_path = "prepared generic uniform-cell exact count summary"
    elif execution_mode == "native-prepared-optix" and result_mode == "summary":
        current_native_path = "prepared generic uniform-cell exact distance summary"
    elif execution_mode == "native-prepared-optix" and result_mode in ("exact-raw", "exact-dict"):
        current_native_path = "prepared generic uniform-cell exact witness rows"
    elif execution_mode == "native-prepared-optix" and result_mode in ("ranked-raw", "ranked-dict"):
        current_native_path = "prepared generic uniform-cell ranked witness rows"
    elif execution_mode == "native-prepared-optix" and result_mode in ("ranked-summary-raw", "ranked-summary-dict"):
        current_native_path = "prepared generic uniform-cell ranked summary rows"
    elif execution_mode == "native-prepared-optix":
        current_native_path = "prepared generic uniform-cell bounded-neighbor traversal"
    else:
        current_native_path = "generic uniform-cell bounded-neighbor traversal"
    return {
        "runner": "goal2348_rtnn_v2_2_external_runner",
        "row": args.row_label,
        "external": "RTDL current",
        "mode": "current_3d_fixed_radius_neighbors_optix_smoke",
        "ok": ok,
        "elapsed_sec": elapsed_sec,
        "elapsed_runs_sec": elapsed_runs,
        "query_count": query_count,
        "search_count": point_count,
        "radius": radius,
        "k_max": k_max,
        "result_mode": result_mode,
        "input_mode": input_mode,
        "input_pack_sec": input_pack_sec,
        "execution_mode": execution_mode,
        "execution_prepare_sec": execution_prepare_sec,
        "repeat": repeat,
        "row_count": row_count,
        "distance_summary": distance_summary,
        "phase_timings": phase_timings,
        "error": error,
        "claim_boundary": {
            "paper_equivalent_rtnn_row": False,
            "rtdl_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "rt_core_neighbor_search_claim_authorized": forced_rt,
            "current_native_path": current_native_path,
            "partitioned_or_batched_like_rtnn": False,
            "prepared_execution_reuses_python_packed_inputs": execution_mode == "prepared-optix",
            "prepared_execution_reuses_native_search_grid": execution_mode == "native-prepared-optix",
            "device_resident_summary": execution_mode == "native-prepared-optix" and result_mode in ("count", "summary"),
            "device_exact_witness_rows": execution_mode == "native-prepared-optix" and result_mode in ("exact-raw", "exact-dict"),
            "device_ranked_witness_rows": execution_mode == "native-prepared-optix" and result_mode in ("ranked-raw", "ranked-dict"),
            "device_ranked_summary_rows": execution_mode == "native-prepared-optix" and result_mode in ("ranked-summary-raw", "ranked-summary-dict"),
        },
    }


def run_rtdl_batched_3d_neighbors(args: argparse.Namespace) -> dict[str, object]:
    """Run a prepared native 3D neighbor handle over query batches.

    This is the first paper-facing large-scale policy row. It is intentionally
    generic: one prepared search-side structure, explicit query batches, and a
    selected fixed-radius result contract.
    """
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    import rtdsl as rt  # noqa: PLC0415

    radius = float(args.radius)
    k_max = int(args.k_max)
    result_mode = str(args.result_mode)
    backend = str(getattr(args, "backend", "optix"))
    batch_size = int(args.query_batch_size)
    repeat = int(args.repeat)
    if batch_size <= 0:
        raise ValueError("query_batch_size must be positive")
    if result_mode not in ("count", "summary", "ranked-summary-raw", "ranked-summary-aggregate", "ranked-summary-aggregate-float32"):
        raise ValueError("batched RTDL path currently supports count, summary, ranked-summary-raw, ranked-summary-aggregate, and ranked-summary-aggregate-float32")
    if backend not in {"optix", "embree"}:
        raise ValueError("batched RTDL path supports backend='optix' or backend='embree'")
    if backend == "embree" and result_mode != "ranked-summary-raw":
        raise ValueError("Embree batched RTNN path currently supports result_mode='ranked-summary-raw'")

    load_started = time.perf_counter()
    search_columns = _read_xyz_columns(args.point_file)
    query_columns = search_columns if args.query_file is None else _read_xyz_columns(args.query_file)
    load_sec = time.perf_counter() - load_started
    search_count = len(search_columns[0])
    query_count = len(query_columns[0])

    pack_started = time.perf_counter()
    search = rt.pack_points(
        ids=search_columns[0],
        x=search_columns[1],
        y=search_columns[2],
        z=search_columns[3],
        dimension=3,
    )
    query_batches = []
    for begin in range(0, query_count, batch_size):
        batch_columns = _slice_columns(query_columns, begin, min(query_count, begin + batch_size))
        query_batches.append(
            (
                rt.pack_points(
                    ids=batch_columns[0],
                    x=batch_columns[1],
                    y=batch_columns[2],
                    z=batch_columns[3],
                    dimension=3,
                ),
                tuple(int(value) for value in batch_columns[0]),
            )
        )
    pack_sec = time.perf_counter() - pack_started

    prepare_started = time.perf_counter()
    if backend == "optix":
        prepared = rt.prepare_optix_fixed_radius_neighbors_3d(search, max_radius=radius)
        embree_kernel = None
    else:
        prepared = None
        embree_kernel = _make_rtdl_fixed_radius_neighbors_3d_kernel(rt, radius=radius, k_max=k_max)
    prepare_sec = time.perf_counter() - prepare_started

    print(
        f"[goal2348] RTDL batched 3D start backend={backend} queries={query_count} search={search_count} "
        f"batch_size={batch_size} batches={len(query_batches)} result_mode={result_mode}",
        flush=True,
    )
    elapsed_runs = []
    row_count = 0
    batch_phase_timings = []
    ranked_aggregate_summary = None
    error = ""
    ok = True
    try:
        for run_index in range(repeat):
            started = time.perf_counter()
            run_row_count = 0
            run_distance_summary = {"count": 0, "min_distance": 0.0, "max_distance": 0.0, "sum_distance": 0.0}
            run_ranked_aggregate_summary = {
                "row_count": 0,
                "bounded_neighbor_count": 0,
                "nearest_id_checksum": 0,
                "kth_id_checksum": 0,
                "sum_distance": 0.0,
            }
            run_phase_timings = []
            for batch, batch_ids in query_batches:
                if backend == "embree":
                    rows = rt.run_embree(
                        embree_kernel,
                        result_mode="raw",
                        query_points=batch,
                        search_points=search,
                    )
                    try:
                        summaries = _ranked_summary_rows_from_fixed_radius_row_view(rows, batch_ids)
                        run_row_count += len(summaries)
                    finally:
                        rows.close()
                    run_phase_timings.append(
                        {
                            "mode": "embree_fixed_radius_rows_to_ranked_summary_rows",
                            "backend": "embree",
                            "materializes_neighbor_rows": True,
                        }
                    )
                    continue

                if result_mode == "count":
                    run_row_count += int(prepared.count(batch, radius=radius, k_max=k_max))
                elif result_mode == "summary":
                    summary = prepared.summary(batch, radius=radius, k_max=k_max)
                    if summary["count"]:
                        if run_distance_summary["count"] == 0 or summary["min_distance"] < run_distance_summary["min_distance"]:
                            run_distance_summary["min_distance"] = summary["min_distance"]
                        if run_distance_summary["count"] == 0 or summary["max_distance"] > run_distance_summary["max_distance"]:
                            run_distance_summary["max_distance"] = summary["max_distance"]
                        run_distance_summary["count"] += summary["count"]
                        run_distance_summary["sum_distance"] += summary["sum_distance"]
                    run_row_count = int(run_distance_summary["count"])
                elif result_mode in {"ranked-summary-aggregate", "ranked-summary-aggregate-float32"}:
                    aggregate = prepared.aggregate_ranked_summary(
                        batch,
                        radius=radius,
                        k_max=k_max,
                        precision="float32" if result_mode == "ranked-summary-aggregate-float32" else "float64",
                    )
                    run_ranked_aggregate_summary["row_count"] += int(aggregate["query_count"])
                    run_ranked_aggregate_summary["bounded_neighbor_count"] += int(aggregate["bounded_neighbor_count"])
                    run_ranked_aggregate_summary["nearest_id_checksum"] += int(aggregate["nearest_id_checksum"])
                    run_ranked_aggregate_summary["kth_id_checksum"] += int(aggregate["kth_id_checksum"])
                    run_ranked_aggregate_summary["sum_distance"] += float(aggregate["sum_distance"])
                    run_row_count = int(run_ranked_aggregate_summary["row_count"])
                else:
                    rows = prepared.run_ranked_summary_raw(batch, radius=radius, k_max=k_max)
                    try:
                        run_row_count += len(rows)
                    finally:
                        rows.close()
                run_phase_timings.append(rt.get_last_fixed_radius_neighbors_3d_phase_timings())
            row_count = run_row_count
            batch_phase_timings = run_phase_timings
            ranked_aggregate_summary = (
                run_ranked_aggregate_summary
                if result_mode in {"ranked-summary-aggregate", "ranked-summary-aggregate-float32"}
                else None
            )
            elapsed_runs.append(time.perf_counter() - started)
            print(
                f"[goal2348] RTDL batched 3D repeat {run_index + 1}/{repeat} "
                f"ok=True sec={elapsed_runs[-1]:.6f}",
                flush=True,
            )
    except Exception as exc:  # pragma: no cover - hardware/library path
        ok = False
        error = repr(exc)
    finally:
        if prepared is not None:
            prepared.close()

    elapsed_sec = elapsed_runs[-1] if elapsed_runs else 0.0
    return {
        "runner": "goal2348_rtnn_v2_2_external_runner",
        "row": args.row_label,
        "external": "RTDL current",
        "mode": f"current_3d_fixed_radius_neighbors_{backend}_batched",
        "ok": ok,
        "backend": backend,
        "elapsed_sec": elapsed_sec,
        "elapsed_runs_sec": elapsed_runs,
        "query_count": query_count,
        "search_count": search_count,
        "query_batch_size": batch_size,
        "batch_count": len(query_batches),
        "radius": radius,
        "k_max": k_max,
        "result_mode": result_mode,
        "input_load_sec": load_sec,
        "input_pack_sec": pack_sec,
        "execution_prepare_sec": prepare_sec,
        "repeat": repeat,
        "row_count": row_count,
        "ranked_aggregate_summary": ranked_aggregate_summary,
        "batch_phase_timings": batch_phase_timings,
        "error": error,
        "contract": {
            "family": "fixed_radius_neighbors_3d",
            "mode": result_mode,
            "exact": result_mode != "ranked-summary-aggregate-float32",
            "precision": "float32" if result_mode == "ranked-summary-aggregate-float32" else "float64",
            "approximate": False,
            "bounded_k": k_max,
            "prepared_search_structure": backend == "optix",
            "batched_queries": True,
        },
        "claim_boundary": {
            "paper_equivalent_rtnn_row": False,
            "rtdl_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "rt_core_neighbor_search_claim_authorized": False,
            "partitioned_or_batched_like_rtnn": True,
            "device_ranked_summary_rows": backend == "optix" and result_mode == "ranked-summary-raw",
            "device_ranked_summary_aggregate": backend == "optix" and result_mode in {"ranked-summary-aggregate", "ranked-summary-aggregate-float32"},
            "float32_precision": result_mode == "ranked-summary-aggregate-float32",
            "embree_ranked_summary_rows": backend == "embree" and result_mode == "ranked-summary-raw",
            "materializes_neighbor_rows": backend == "embree",
        },
    }


def _make_rtdl_fixed_radius_neighbors_3d_kernel(rt_module, *, radius: float, k_max: int):
    @rt_module.kernel(backend="rtdl", precision="float_approx")
    def _goal2348_embree_fixed_radius_neighbors_3d():
        query_points = rt_module.input("query_points", rt_module.Points3D, role="probe")
        search_points = rt_module.input("search_points", rt_module.Points3D, role="build")
        candidates = rt_module.traverse(query_points, search_points, accel="bvh")
        hits = rt_module.refine(
            candidates,
            predicate=rt_module.fixed_radius_neighbors(radius=radius, k_max=k_max),
        )
        return rt_module.emit(hits, fields=["query_id", "neighbor_id", "distance"])

    return _goal2348_embree_fixed_radius_neighbors_3d


def _ranked_summary_rows_from_fixed_radius_row_view(rows, query_ids: tuple[int, ...]) -> tuple[dict[str, object], ...]:
    grouped: dict[int, list[tuple[int, float]]] = {int(query_id): [] for query_id in query_ids}
    for index in range(len(rows)):
        row = rows.rows_ptr[index]
        grouped.setdefault(int(row.query_id), []).append((int(row.neighbor_id), float(row.distance)))

    sentinel = 0xFFFFFFFF
    summaries = []
    for query_id in query_ids:
        neighbors = sorted(grouped.get(int(query_id), ()), key=lambda item: (item[1], item[0]))
        if neighbors:
            nearest_id, nearest_distance = neighbors[0]
            kth_id, kth_distance = neighbors[-1]
            sum_distance = sum(distance for _neighbor_id, distance in neighbors)
        else:
            nearest_id = sentinel
            kth_id = sentinel
            nearest_distance = 0.0
            kth_distance = 0.0
            sum_distance = 0.0
        summaries.append(
            {
                "query_id": int(query_id),
                "neighbor_count": len(neighbors),
                "nearest_neighbor_id": nearest_id,
                "kth_neighbor_id": kth_id,
                "nearest_distance": nearest_distance,
                "kth_distance": kth_distance,
                "sum_distance": sum_distance,
            }
        )
    return tuple(summaries)


def run_rtdl_adaptive_partitioned_3d_neighbors(args: argparse.Namespace) -> dict[str, object]:
    """Run exact fixed-radius ranked summaries through spatially sharded RTDL handles.

    Query cells are processed once. Each cell prepares a search-side halo that
    contains every search point that can be within ``radius`` of any query in
    the cell. The native ABI remains the same generic prepared 3-D neighbor
    summary path; the density-aware policy lives in Python orchestration.
    """
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    import rtdsl as rt  # noqa: PLC0415

    radius = float(args.radius)
    k_max = int(args.k_max)
    repeat = int(args.repeat)
    divisions = int(args.partition_divisions)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if k_max <= 0:
        raise ValueError("k_max must be positive")
    if divisions <= 0:
        raise ValueError("partition_divisions must be positive")

    load_started = time.perf_counter()
    search_columns = _read_xyz_columns(args.point_file)
    query_columns = search_columns if args.query_file is None else _read_xyz_columns(args.query_file)
    load_sec = time.perf_counter() - load_started
    search_count = len(search_columns[0])
    query_count = len(query_columns[0])
    mins, maxs = _xyz_bounds(search_columns, query_columns)

    partition_started = time.perf_counter()
    search_groups, cell_sizes = _grid_groups(search_columns, mins=mins, maxs=maxs, divisions=divisions)
    query_groups, _ = _grid_groups(query_columns, mins=mins, maxs=maxs, divisions=divisions)
    partition_sec = time.perf_counter() - partition_started

    pack_prepare_started = time.perf_counter()
    partitions = []
    partition_metadata = []
    try:
        for partition_index, key in enumerate(sorted(query_groups)):
            query_indices = query_groups[key]
            search_indices = _neighbor_search_indices(
                key,
                search_groups=search_groups,
                mins=mins,
                cell_sizes=cell_sizes,
                divisions=divisions,
                radius=radius,
            )
            query_subset = _take_columns(query_columns, query_indices)
            search_subset = _take_columns(search_columns, search_indices)
            if not search_subset[0]:
                # The same-point benchmark never hits this path, but keep the
                # metadata explicit for future asymmetric query/search datasets.
                partition_metadata.append(
                    {
                        "partition_index": partition_index,
                        "cell": key,
                        "query_count": len(query_indices),
                        "search_halo_count": 0,
                        "skipped_empty_search_halo": True,
                    }
                )
                continue
            packed_search = rt.pack_points(
                ids=search_subset[0],
                x=search_subset[1],
                y=search_subset[2],
                z=search_subset[3],
                dimension=3,
            )
            packed_queries = rt.pack_points(
                ids=query_subset[0],
                x=query_subset[1],
                y=query_subset[2],
                z=query_subset[3],
                dimension=3,
            )
            prepared = rt.prepare_optix_fixed_radius_neighbors_3d(packed_search, max_radius=radius)
            partitions.append((prepared, packed_queries, key, len(query_indices), len(search_indices)))
            partition_metadata.append(
                {
                    "partition_index": partition_index,
                    "cell": key,
                    "query_count": len(query_indices),
                    "search_halo_count": len(search_indices),
                    "skipped_empty_search_halo": False,
                }
            )
    except Exception:
        for prepared, *_ in partitions:
            prepared.close()
        raise
    pack_prepare_sec = time.perf_counter() - pack_prepare_started

    print(
        f"[goal2348] RTDL adaptive 3D start queries={query_count} search={search_count} "
        f"divisions={divisions} partitions={len(partitions)} radius={radius}",
        flush=True,
    )
    elapsed_runs = []
    row_count = 0
    phase_timings = []
    error = ""
    ok = True
    try:
        for run_index in range(repeat):
            started = time.perf_counter()
            run_row_count = 0
            run_timings = []
            for partition_index, (prepared, packed_queries, key, query_len, search_len) in enumerate(partitions):
                rows = prepared.run_ranked_summary_raw(packed_queries, radius=radius, k_max=k_max)
                try:
                    run_row_count += len(rows)
                finally:
                    rows.close()
                timing = dict(rt.get_last_fixed_radius_neighbors_3d_phase_timings())
                timing.update(
                    {
                        "partition_index": partition_index,
                        "cell": key,
                        "query_count": query_len,
                        "search_halo_count": search_len,
                    }
                )
                run_timings.append(timing)
            row_count = run_row_count
            phase_timings = run_timings
            elapsed_runs.append(time.perf_counter() - started)
            print(
                f"[goal2348] RTDL adaptive 3D repeat {run_index + 1}/{repeat} "
                f"ok=True sec={elapsed_runs[-1]:.6f}",
                flush=True,
            )
    except Exception as exc:  # pragma: no cover - hardware/library path
        ok = False
        error = repr(exc)
    finally:
        for prepared, *_ in partitions:
            prepared.close()

    total_raw_candidates = sum(int(item.get("raw_candidate_count", 0)) for item in phase_timings)
    total_candidate_time = sum(float(item.get("candidate_count_pass", 0.0)) for item in phase_timings)
    total_row_download_time = sum(float(item.get("row_download", 0.0)) for item in phase_timings)
    largest_partitions = sorted(
        partition_metadata,
        key=lambda item: (int(item["query_count"]), int(item["search_halo_count"])),
        reverse=True,
    )[:12]
    heaviest_phase_partitions = sorted(
        (
            {
                "partition_index": item.get("partition_index"),
                "cell": item.get("cell"),
                "query_count": item.get("query_count"),
                "search_halo_count": item.get("search_halo_count"),
                "raw_candidate_count": item.get("raw_candidate_count"),
                "candidate_count_pass": item.get("candidate_count_pass"),
            }
            for item in phase_timings
        ),
        key=lambda item: float(item.get("candidate_count_pass") or 0.0),
        reverse=True,
    )[:12]
    return {
        "runner": "goal2348_rtnn_v2_2_external_runner",
        "row": args.row_label,
        "external": "RTDL current",
        "mode": "current_3d_fixed_radius_neighbors_optix_adaptive_partitioned",
        "ok": ok,
        "elapsed_sec": elapsed_runs[-1] if elapsed_runs else 0.0,
        "elapsed_runs_sec": elapsed_runs,
        "query_count": query_count,
        "search_count": search_count,
        "radius": radius,
        "k_max": k_max,
        "result_mode": "ranked-summary-raw",
        "repeat": repeat,
        "row_count": row_count,
        "input_load_sec": load_sec,
        "partition_build_sec": partition_sec,
        "pack_and_prepare_partitions_sec": pack_prepare_sec,
        "partition_divisions": divisions,
        "partition_count": len(partitions),
        "skipped_empty_partition_count": sum(1 for item in partition_metadata if item["skipped_empty_search_halo"]),
        "total_raw_candidate_count": total_raw_candidates,
        "partition_summary": {
            "total_query_count": sum(int(item["query_count"]) for item in partition_metadata),
            "total_search_halo_references": sum(int(item["search_halo_count"]) for item in partition_metadata),
            "max_query_count": max((int(item["query_count"]) for item in partition_metadata), default=0),
            "max_search_halo_count": max((int(item["search_halo_count"]) for item in partition_metadata), default=0),
            "largest_partitions": largest_partitions,
        },
        "phase_summary": {
            "total_raw_candidate_count": total_raw_candidates,
            "total_candidate_count_pass": total_candidate_time,
            "total_row_download": total_row_download_time,
            "max_raw_candidate_count": max((int(item.get("raw_candidate_count", 0)) for item in phase_timings), default=0),
            "max_candidate_count_pass": max((float(item.get("candidate_count_pass", 0.0)) for item in phase_timings), default=0.0),
            "heaviest_partitions": heaviest_phase_partitions,
        },
        "error": error,
        "contract": {
            "family": "fixed_radius_neighbors_3d",
            "mode": "ranked-summary-raw",
            "exact": True,
            "approximate": False,
            "bounded_k": k_max,
            "prepared_search_structure": True,
            "batched_queries": True,
            "density_aware_spatial_partitioning": True,
        },
        "claim_boundary": {
            "paper_equivalent_rtnn_row": False,
            "rtdl_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "rt_core_neighbor_search_claim_authorized": False,
            "partitioned_or_batched_like_rtnn": True,
            "density_aware_partition_policy": True,
            "native_abi_changed_for_rtnn": False,
            "device_ranked_summary_rows": True,
        },
    }


def run_cupy_3d_ranked_summary(args: argparse.Namespace) -> dict[str, object]:
    """Run an exact CUDA-core CuPy top-K summary baseline.

    This baseline deliberately does not use RT cores. It uses vectorized/block
    CUDA-core distance evaluation through CuPy and returns the same per-query
    ranked-summary contract as Goal2384.
    """
    radius = float(args.radius)
    k_max = int(args.k_max)
    batch_size = int(args.query_batch_size)
    repeat = int(args.repeat)
    dtype_name = str(args.dtype)
    if batch_size <= 0:
        raise ValueError("query_batch_size must be positive")
    if k_max <= 0:
        raise ValueError("k_max must be positive")

    import cupy as cp  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    load_started = time.perf_counter()
    search_columns = _read_xyz_columns(args.point_file)
    query_columns = search_columns if args.query_file is None else _read_xyz_columns(args.query_file)
    load_sec = time.perf_counter() - load_started
    search_np = np.asarray(list(zip(search_columns[1], search_columns[2], search_columns[3])), dtype=np.float32 if dtype_name == "float32" else np.float64)
    query_np = np.asarray(list(zip(query_columns[1], query_columns[2], query_columns[3])), dtype=search_np.dtype)
    search_ids_np = np.asarray(search_columns[0], dtype=np.uint32)
    query_ids_np = np.asarray(query_columns[0], dtype=np.uint32)

    upload_started = time.perf_counter()
    search = cp.asarray(search_np)
    query = cp.asarray(query_np)
    search_ids = cp.asarray(search_ids_np)
    query_ids = cp.asarray(query_ids_np)
    cp.cuda.Stream.null.synchronize()
    upload_sec = time.perf_counter() - upload_started

    print(
        f"[goal2348] CuPy 3D ranked summary start queries={len(query_np)} search={len(search_np)} "
        f"batch_size={batch_size} k={k_max} dtype={dtype_name}",
        flush=True,
    )
    elapsed_runs = []
    last_summary = None
    radius_sq = radius * radius
    k_eff = min(k_max, len(search_np))
    for run_index in range(repeat):
        started = time.perf_counter()
        total_rows = 0
        total_neighbors = 0
        nearest_checksum = 0
        kth_checksum = 0
        distance_sum = 0.0
        for begin in range(0, len(query_np), batch_size):
            q = query[begin:begin + batch_size]
            qids = query_ids[begin:begin + batch_size]
            diff = q[:, None, :] - search[None, :, :]
            d2 = cp.sum(diff * diff, axis=2)
            masked = cp.where(d2 <= radius_sq, d2, cp.inf)
            part = cp.argpartition(masked, kth=k_eff - 1, axis=1)[:, :k_eff]
            top_d2 = cp.take_along_axis(masked, part, axis=1)
            order = cp.argsort(top_d2, axis=1)
            sorted_d2 = cp.take_along_axis(top_d2, order, axis=1)
            sorted_indices = cp.take_along_axis(part, order, axis=1)
            valid = cp.isfinite(sorted_d2)
            counts = cp.sum(valid, axis=1).astype(cp.uint32)
            last_pos = cp.maximum(counts.astype(cp.int64) - 1, 0)
            batch_index = cp.arange(q.shape[0])
            nearest_indices = cp.where(counts > 0, sorted_indices[:, 0], 0)
            kth_indices = cp.where(counts > 0, sorted_indices[batch_index, last_pos], 0)
            nearest_ids = cp.where(counts > 0, search_ids[nearest_indices], cp.uint32(0xffffffff))
            kth_ids = cp.where(counts > 0, search_ids[kth_indices], cp.uint32(0xffffffff))
            distances = cp.sqrt(cp.where(valid, sorted_d2, 0.0))
            sums = cp.sum(distances, axis=1)
            total_rows += int(q.shape[0])
            total_neighbors += int(cp.sum(counts).get())
            nearest_checksum += int(cp.sum(nearest_ids).get())
            kth_checksum += int(cp.sum(kth_ids).get())
            distance_sum += float(cp.sum(sums).get())
            # Touch query ids so the baseline records the same per-query contract.
            nearest_checksum += int(cp.sum(qids * 0).get())
        cp.cuda.Stream.null.synchronize()
        elapsed_runs.append(time.perf_counter() - started)
        last_summary = {
            "row_count": total_rows,
            "bounded_neighbor_count": total_neighbors,
            "nearest_id_checksum": nearest_checksum,
            "kth_id_checksum": kth_checksum,
            "sum_distance": distance_sum,
        }
        print(
            f"[goal2348] CuPy 3D ranked summary repeat {run_index + 1}/{repeat} "
            f"ok=True sec={elapsed_runs[-1]:.6f}",
            flush=True,
        )

    return {
        "runner": "goal2348_rtnn_v2_2_external_runner",
        "row": args.row_label,
        "external": "CuPy",
        "mode": "cupy_cuda_core_exact_ranked_summary_3d",
        "ok": True,
        "elapsed_sec": elapsed_runs[-1] if elapsed_runs else 0.0,
        "elapsed_runs_sec": elapsed_runs,
        "query_count": len(query_np),
        "search_count": len(search_np),
        "query_batch_size": batch_size,
        "batch_count": (len(query_np) + batch_size - 1) // batch_size,
        "radius": radius,
        "k_max": k_max,
        "dtype": dtype_name,
        "input_load_sec": load_sec,
        "device_upload_sec": upload_sec,
        "summary": last_summary,
        "contract": {
            "family": "fixed_radius_neighbors_3d",
            "mode": "ranked-summary",
            "exact": True,
            "approximate": False,
            "bounded_k": k_max,
            "prepared_search_structure": False,
            "batched_queries": True,
        },
        "claim_boundary": {
            "uses_rt_cores": False,
            "cuda_core_baseline": True,
            "paper_equivalent_rtnn_row": False,
            "rtdl_speedup_claim_authorized": False,
        },
    }


def run_cupy_grid_3d_ranked_summary(args: argparse.Namespace) -> dict[str, object]:
    """Run an exact CUDA-core uniform-grid top-K summary baseline.

    This is a stronger CUDA-only opponent than the all-pairs CuPy row. It uses
    a generic fixed-radius grid index, a CuPy RawKernel, and 27-cell neighbor
    traversal with per-query bounded top-K insertion. It still does not use RT
    cores and does not change RTDL native code.
    """
    radius = float(args.radius)
    k_max = int(args.k_max)
    repeat = int(args.repeat)
    dtype_name = str(args.dtype)
    max_grid_cells = int(args.max_grid_cells)
    if radius <= 0:
        raise ValueError("radius must be positive")
    if k_max <= 0 or k_max > 64:
        raise ValueError("cupy grid ranked summary requires 1 <= k_max <= 64")

    import cupy as cp  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    load_started = time.perf_counter()
    search_columns = _read_xyz_columns(args.point_file)
    query_columns = search_columns if args.query_file is None else _read_xyz_columns(args.query_file)
    load_sec = time.perf_counter() - load_started
    dtype = np.float32 if dtype_name == "float32" else np.float64
    if dtype is not np.float32:
        raise ValueError("cupy grid RawKernel baseline currently supports float32")
    search_np = np.asarray(list(zip(search_columns[1], search_columns[2], search_columns[3])), dtype=np.float32)
    query_np = np.asarray(list(zip(query_columns[1], query_columns[2], query_columns[3])), dtype=np.float32)
    search_ids_np = np.asarray(search_columns[0], dtype=np.uint32)
    query_ids_np = np.asarray(query_columns[0], dtype=np.uint32)

    prepare_started = time.perf_counter()
    if len(search_np) == 0 or len(query_np) == 0:
        raise ValueError("cupy grid baseline requires non-empty search and query points")
    mins_np = np.minimum(search_np.min(axis=0), query_np.min(axis=0)) - np.float32(radius * 1e-3)
    maxs_np = np.maximum(search_np.max(axis=0), query_np.max(axis=0)) + np.float32(radius * 1e-3)
    dims_np = np.maximum(1, np.ceil((maxs_np - mins_np) / np.float32(radius)).astype(np.int64) + 1)
    nx, ny, nz = (int(dims_np[0]), int(dims_np[1]), int(dims_np[2]))
    num_cells = nx * ny * nz
    if num_cells > max_grid_cells:
        raise ValueError(f"grid has {num_cells} cells, above max_grid_cells={max_grid_cells}")

    search_cell_xyz = np.floor((search_np - mins_np) / np.float32(radius)).astype(np.int64)
    search_cell_xyz[:, 0] = np.clip(search_cell_xyz[:, 0], 0, nx - 1)
    search_cell_xyz[:, 1] = np.clip(search_cell_xyz[:, 1], 0, ny - 1)
    search_cell_xyz[:, 2] = np.clip(search_cell_xyz[:, 2], 0, nz - 1)
    search_cell_ids = (
        search_cell_xyz[:, 0]
        + nx * (search_cell_xyz[:, 1] + ny * search_cell_xyz[:, 2])
    ).astype(np.int64)
    order = np.argsort(search_cell_ids, kind="stable")
    sorted_cell_ids = search_cell_ids[order]
    sorted_search_np = np.ascontiguousarray(search_np[order])
    sorted_search_ids_np = np.ascontiguousarray(search_ids_np[order])
    cell_start_np = np.full(num_cells, -1, dtype=np.int32)
    cell_end_np = np.full(num_cells, -1, dtype=np.int32)
    unique_cells, starts, counts = np.unique(sorted_cell_ids, return_index=True, return_counts=True)
    cell_start_np[unique_cells] = starts.astype(np.int32)
    cell_end_np[unique_cells] = (starts + counts).astype(np.int32)

    search_gpu = cp.asarray(sorted_search_np)
    search_ids_gpu = cp.asarray(sorted_search_ids_np)
    query_gpu = cp.asarray(query_np)
    query_ids_gpu = cp.asarray(query_ids_np)
    cell_start_gpu = cp.asarray(cell_start_np)
    cell_end_gpu = cp.asarray(cell_end_np)
    out_count = cp.empty(len(query_np), dtype=cp.uint32)
    out_nearest = cp.empty(len(query_np), dtype=cp.uint32)
    out_kth = cp.empty(len(query_np), dtype=cp.uint32)
    out_nearest_dist = cp.empty(len(query_np), dtype=cp.float32)
    out_kth_dist = cp.empty(len(query_np), dtype=cp.float32)
    out_sum = cp.empty(len(query_np), dtype=cp.float32)

    kernel_source = r'''
extern "C" __global__
void rtdl_grid_ranked_summary_3d(
    const float* query_points,
    const unsigned int* query_ids,
    const float* search_points,
    const unsigned int* search_ids,
    const int* cell_start,
    const int* cell_end,
    const int query_count,
    const int nx,
    const int ny,
    const int nz,
    const float min_x,
    const float min_y,
    const float min_z,
    const float inv_cell_size,
    const float radius_sq,
    const int k_max,
    unsigned int* out_count,
    unsigned int* out_nearest,
    unsigned int* out_kth,
    float* out_nearest_dist,
    float* out_kth_dist,
    float* out_sum) {
    int q = blockDim.x * blockIdx.x + threadIdx.x;
    if (q >= query_count) {
        return;
    }
    float qx = query_points[q * 3 + 0];
    float qy = query_points[q * 3 + 1];
    float qz = query_points[q * 3 + 2];
    int cx = (int)floorf((qx - min_x) * inv_cell_size);
    int cy = (int)floorf((qy - min_y) * inv_cell_size);
    int cz = (int)floorf((qz - min_z) * inv_cell_size);
    cx = max(0, min(nx - 1, cx));
    cy = max(0, min(ny - 1, cy));
    cz = max(0, min(nz - 1, cz));

    float best_d2[64];
    unsigned int best_id[64];
    int top_count = 0;
    for (int dz = -1; dz <= 1; ++dz) {
        int zz = cz + dz;
        if (zz < 0 || zz >= nz) continue;
        for (int dy = -1; dy <= 1; ++dy) {
            int yy = cy + dy;
            if (yy < 0 || yy >= ny) continue;
            for (int dx = -1; dx <= 1; ++dx) {
                int xx = cx + dx;
                if (xx < 0 || xx >= nx) continue;
                int cell = xx + nx * (yy + ny * zz);
                int begin = cell_start[cell];
                if (begin < 0) continue;
                int end = cell_end[cell];
                for (int s = begin; s < end; ++s) {
                    float sx = search_points[s * 3 + 0];
                    float sy = search_points[s * 3 + 1];
                    float sz = search_points[s * 3 + 2];
                    float ddx = qx - sx;
                    float ddy = qy - sy;
                    float ddz = qz - sz;
                    float d2 = ddx * ddx + ddy * ddy + ddz * ddz;
                    if (d2 > radius_sq) continue;
                    unsigned int sid = search_ids[s];
                    int pos;
                    if (top_count < k_max) {
                        pos = top_count;
                        best_d2[pos] = d2;
                        best_id[pos] = sid;
                        top_count++;
                    } else if (d2 < best_d2[k_max - 1] || (d2 == best_d2[k_max - 1] && sid < best_id[k_max - 1])) {
                        pos = k_max - 1;
                        best_d2[pos] = d2;
                        best_id[pos] = sid;
                    } else {
                        continue;
                    }
                    while (pos > 0 && (best_d2[pos] < best_d2[pos - 1] || (best_d2[pos] == best_d2[pos - 1] && best_id[pos] < best_id[pos - 1]))) {
                        float td = best_d2[pos - 1];
                        unsigned int ti = best_id[pos - 1];
                        best_d2[pos - 1] = best_d2[pos];
                        best_id[pos - 1] = best_id[pos];
                        best_d2[pos] = td;
                        best_id[pos] = ti;
                        pos--;
                    }
                }
            }
        }
    }
    out_count[q] = (unsigned int)top_count;
    if (top_count == 0) {
        out_nearest[q] = 0xffffffffu;
        out_kth[q] = 0xffffffffu;
        out_nearest_dist[q] = 3.402823466e+38F;
        out_kth_dist[q] = 3.402823466e+38F;
        out_sum[q] = 0.0f;
        return;
    }
    float sum = 0.0f;
    for (int i = 0; i < top_count; ++i) {
        sum += sqrtf(best_d2[i]);
    }
    out_nearest[q] = best_id[0];
    out_kth[q] = best_id[top_count - 1];
    out_nearest_dist[q] = sqrtf(best_d2[0]);
    out_kth_dist[q] = sqrtf(best_d2[top_count - 1]);
    out_sum[q] = sum + ((float)query_ids[q] * 0.0f);
}
'''
    kernel = cp.RawKernel(kernel_source, "rtdl_grid_ranked_summary_3d")
    kernel.compile()
    cp.cuda.Stream.null.synchronize()
    prepare_sec = time.perf_counter() - prepare_started

    print(
        f"[goal2348] CuPy grid 3D ranked summary start queries={len(query_np)} search={len(search_np)} "
        f"grid={nx}x{ny}x{nz} occupied_cells={len(unique_cells)} k={k_max}",
        flush=True,
    )
    elapsed_runs = []
    last_summary = None
    threads = 256
    blocks = (len(query_np) + threads - 1) // threads
    for run_index in range(repeat):
        started = time.perf_counter()
        kernel(
            (blocks,),
            (threads,),
            (
                query_gpu,
                query_ids_gpu,
                search_gpu,
                search_ids_gpu,
                cell_start_gpu,
                cell_end_gpu,
                np.int32(len(query_np)),
                np.int32(nx),
                np.int32(ny),
                np.int32(nz),
                np.float32(mins_np[0]),
                np.float32(mins_np[1]),
                np.float32(mins_np[2]),
                np.float32(1.0 / radius),
                np.float32(radius * radius),
                np.int32(k_max),
                out_count,
                out_nearest,
                out_kth,
                out_nearest_dist,
                out_kth_dist,
                out_sum,
            ),
        )
        cp.cuda.Stream.null.synchronize()
        elapsed_runs.append(time.perf_counter() - started)
        last_summary = {
            "row_count": int(len(query_np)),
            "bounded_neighbor_count": int(cp.sum(out_count.astype(cp.uint64)).get()),
            "nearest_id_checksum": int(cp.sum(out_nearest.astype(cp.uint64)).get()),
            "kth_id_checksum": int(cp.sum(out_kth.astype(cp.uint64)).get()),
            "sum_distance": float(cp.sum(out_sum.astype(cp.float64)).get()),
        }
        print(
            f"[goal2348] CuPy grid 3D ranked summary repeat {run_index + 1}/{repeat} "
            f"ok=True sec={elapsed_runs[-1]:.6f}",
            flush=True,
        )

    return {
        "runner": "goal2348_rtnn_v2_2_external_runner",
        "row": args.row_label,
        "external": "CuPy",
        "mode": "cupy_cuda_core_grid_exact_ranked_summary_3d",
        "ok": True,
        "elapsed_sec": elapsed_runs[-1] if elapsed_runs else 0.0,
        "elapsed_runs_sec": elapsed_runs,
        "query_count": len(query_np),
        "search_count": len(search_np),
        "radius": radius,
        "k_max": k_max,
        "dtype": dtype_name,
        "input_load_sec": load_sec,
        "grid_prepare_sec": prepare_sec,
        "grid_dimensions": [nx, ny, nz],
        "grid_cell_count": num_cells,
        "occupied_cell_count": int(len(unique_cells)),
        "summary": last_summary,
        "contract": {
            "family": "fixed_radius_neighbors_3d",
            "mode": "ranked-summary",
            "exact": True,
            "approximate": False,
            "bounded_k": k_max,
            "prepared_search_structure": True,
            "uniform_grid_cuda_core": True,
        },
        "claim_boundary": {
            "uses_rt_cores": False,
            "cuda_core_baseline": True,
            "stronger_than_all_pairs_baseline": True,
            "paper_equivalent_rtnn_row": False,
            "rtdl_speedup_claim_authorized": False,
            "native_abi_changed_for_rtnn": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2348 RTNN v2.2 external benchmark harness.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser("generate", help="Generate deterministic RTNN-format point cloud text.")
    gen.add_argument("--point-file", type=Path, required=True)
    gen.add_argument("--point-count", type=int, required=True)
    gen.add_argument("--dimension", type=int, choices=(2, 3), required=True)
    gen.add_argument("--seed", type=int, default=2346)
    gen.add_argument("--distribution", choices=("uniform", "clustered", "shell"), default="uniform")
    gen.add_argument("--cluster-count", type=int, default=8)
    gen.add_argument("--cluster-stddev", type=float, default=0.035)
    gen.add_argument("--json-out", type=Path, required=True)

    parse = subparsers.add_parser("parse-timings", help="Parse an RTNN output log into JSON timing rows.")
    parse.add_argument("--log", type=Path, required=True)
    parse.add_argument("--json-out", type=Path, required=True)

    patch = subparsers.add_parser(
        "patch-rtnn-cuda12",
        help="Patch a disposable external RTNN checkout for CUDA 12 build/runtime compatibility.",
    )
    patch.add_argument("--rtnn-root", type=Path, required=True)
    patch.add_argument("--json-out", type=Path, required=True)

    rtnn = subparsers.add_parser("run-rtnn", help="Run an external RTNN optixNSearch binary.")
    rtnn.add_argument("--rtnn-binary", type=Path, required=True)
    rtnn.add_argument("--rtnn-cwd", type=Path)
    rtnn.add_argument("--rtnn-library-dir", type=Path)
    rtnn.add_argument("--point-file", type=Path, required=True)
    rtnn.add_argument("--query-file", type=Path)
    rtnn.add_argument("--search-mode", choices=("radius", "knn"), default="radius")
    rtnn.add_argument("--radius", type=float, default=0.02)
    rtnn.add_argument("--k-max", type=int, default=50)
    rtnn.add_argument("--device", type=int, default=0)
    rtnn.add_argument("--partition", action=argparse.BooleanOptionalAction, default=True)
    rtnn.add_argument("--auto-batch", action=argparse.BooleanOptionalAction, default=True)
    rtnn.add_argument("--approx-mode", type=int, default=0)
    rtnn.add_argument("--extra-rtnn-arg", action="append")
    rtnn.add_argument("--timeout-sec", type=int, default=300)
    rtnn.add_argument("--row-label", default="rtnn_external")
    rtnn.add_argument("--json-out", type=Path, required=True)

    smoke = subparsers.add_parser("run-rtdl-current-2d-smoke", help="Run current RTDL 2-D OptiX smoke row.")
    smoke.add_argument("--point-file", type=Path, required=True)
    smoke.add_argument("--query-file", type=Path)
    smoke.add_argument("--radius", type=float, default=0.02)
    smoke.add_argument("--threshold", type=int, default=1)
    smoke.add_argument("--row-label", default="rtdl_current_2d_smoke")
    smoke.add_argument("--json-out", type=Path, required=True)

    smoke3d = subparsers.add_parser(
        "run-rtdl-current-3d-neighbors-smoke",
        help="Run current RTDL 3-D fixed-radius neighbors OptiX-runtime smoke row.",
    )
    smoke3d.add_argument("--point-file", type=Path, required=True)
    smoke3d.add_argument("--query-file", type=Path)
    smoke3d.add_argument("--radius", type=float, default=0.02)
    smoke3d.add_argument("--k-max", type=int, default=50)
    smoke3d.add_argument("--result-mode", choices=("dict", "raw", "count", "summary", "exact-raw", "exact-dict", "ranked-raw", "ranked-dict", "ranked-summary-raw", "ranked-summary-dict"), default="dict")
    smoke3d.add_argument("--input-mode", choices=("records", "packed-columns"), default="records")
    smoke3d.add_argument("--execution-mode", choices=("run-optix", "prepared-optix", "native-prepared-optix"), default="run-optix")
    smoke3d.add_argument("--repeat", type=int, default=1)
    smoke3d.add_argument("--row-label", default="rtdl_current_3d_neighbors_smoke")
    smoke3d.add_argument("--json-out", type=Path, required=True)

    batched3d = subparsers.add_parser(
        "run-rtdl-batched-3d-neighbors",
        help="Run prepared native RTDL 3-D fixed-radius neighbors over explicit query batches.",
    )
    batched3d.add_argument("--point-file", type=Path, required=True)
    batched3d.add_argument("--query-file", type=Path)
    batched3d.add_argument("--radius", type=float, default=0.02)
    batched3d.add_argument("--k-max", type=int, default=50)
    batched3d.add_argument("--backend", choices=("optix", "embree"), default="optix")
    batched3d.add_argument("--query-batch-size", type=int, default=65536)
    batched3d.add_argument("--result-mode", choices=("count", "summary", "ranked-summary-raw", "ranked-summary-aggregate", "ranked-summary-aggregate-float32"), default="ranked-summary-raw")
    batched3d.add_argument("--repeat", type=int, default=1)
    batched3d.add_argument("--row-label", default="rtdl_batched_3d_neighbors")
    batched3d.add_argument("--json-out", type=Path, required=True)

    adaptive3d = subparsers.add_parser(
        "run-rtdl-adaptive-3d-neighbors",
        help="Run exact prepared RTDL 3-D fixed-radius neighbors with density-aware spatial partitions.",
    )
    adaptive3d.add_argument("--point-file", type=Path, required=True)
    adaptive3d.add_argument("--query-file", type=Path)
    adaptive3d.add_argument("--radius", type=float, default=0.02)
    adaptive3d.add_argument("--k-max", type=int, default=50)
    adaptive3d.add_argument("--partition-divisions", type=int, default=8)
    adaptive3d.add_argument("--repeat", type=int, default=1)
    adaptive3d.add_argument("--row-label", default="rtdl_adaptive_3d_neighbors")
    adaptive3d.add_argument("--json-out", type=Path, required=True)

    cupy3d = subparsers.add_parser(
        "run-cupy-3d-ranked-summary",
        help="Run an exact CUDA-core CuPy 3-D ranked-summary baseline.",
    )
    cupy3d.add_argument("--point-file", type=Path, required=True)
    cupy3d.add_argument("--query-file", type=Path)
    cupy3d.add_argument("--radius", type=float, default=0.02)
    cupy3d.add_argument("--k-max", type=int, default=50)
    cupy3d.add_argument("--query-batch-size", type=int, default=1024)
    cupy3d.add_argument("--dtype", choices=("float32", "float64"), default="float32")
    cupy3d.add_argument("--repeat", type=int, default=1)
    cupy3d.add_argument("--row-label", default="cupy_3d_ranked_summary")
    cupy3d.add_argument("--json-out", type=Path, required=True)

    cupy_grid3d = subparsers.add_parser(
        "run-cupy-grid-3d-ranked-summary",
        help="Run an exact CUDA-core uniform-grid CuPy RawKernel 3-D ranked-summary baseline.",
    )
    cupy_grid3d.add_argument("--point-file", type=Path, required=True)
    cupy_grid3d.add_argument("--query-file", type=Path)
    cupy_grid3d.add_argument("--radius", type=float, default=0.02)
    cupy_grid3d.add_argument("--k-max", type=int, default=50)
    cupy_grid3d.add_argument("--dtype", choices=("float32",), default="float32")
    cupy_grid3d.add_argument("--max-grid-cells", type=int, default=2_000_000)
    cupy_grid3d.add_argument("--repeat", type=int, default=1)
    cupy_grid3d.add_argument("--row-label", default="cupy_grid_3d_ranked_summary")
    cupy_grid3d.add_argument("--json-out", type=Path, required=True)

    args = parser.parse_args(argv)

    if args.command == "generate":
        payload = {
            "runner": "goal2348_rtnn_v2_2_external_runner",
            "generated": generate_point_file(
                args.point_file,
                point_count=args.point_count,
                dimension=args.dimension,
                seed=args.seed,
                distribution=args.distribution,
                cluster_count=args.cluster_count,
                cluster_stddev=args.cluster_stddev,
            ),
            "claim_boundary": {
                "paper_dataset": False,
                "synthetic_input_only": True,
            },
        }
    elif args.command == "parse-timings":
        text = args.log.read_text(encoding="utf-8")
        payload = {
            "runner": "goal2348_rtnn_v2_2_external_runner",
            "log": str(args.log),
            "timings": _timing_summary(parse_rtnn_timings(text)),
        }
    elif args.command == "patch-rtnn-cuda12":
        payload = patch_rtnn_cuda12_checkout(args.rtnn_root)
    elif args.command == "run-rtnn":
        payload = run_rtnn(args)
    elif args.command == "run-rtdl-current-2d-smoke":
        payload = run_rtdl_current_2d_smoke(args)
    elif args.command == "run-rtdl-current-3d-neighbors-smoke":
        payload = run_rtdl_current_3d_neighbors_smoke(args)
    elif args.command == "run-rtdl-batched-3d-neighbors":
        payload = run_rtdl_batched_3d_neighbors(args)
    elif args.command == "run-rtdl-adaptive-3d-neighbors":
        payload = run_rtdl_adaptive_partitioned_3d_neighbors(args)
    elif args.command == "run-cupy-3d-ranked-summary":
        payload = run_cupy_3d_ranked_summary(args)
    elif args.command == "run-cupy-grid-3d-ranked-summary":
        payload = run_cupy_grid_3d_ranked_summary(args)
    else:  # pragma: no cover - argparse guards this
        raise AssertionError(args.command)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
