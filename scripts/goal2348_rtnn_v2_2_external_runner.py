from __future__ import annotations

import argparse
import json
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2348 RTNN v2.2 external benchmark harness.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser("generate", help="Generate deterministic RTNN-format point cloud text.")
    gen.add_argument("--point-file", type=Path, required=True)
    gen.add_argument("--point-count", type=int, required=True)
    gen.add_argument("--dimension", type=int, choices=(2, 3), required=True)
    gen.add_argument("--seed", type=int, default=2346)
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

    args = parser.parse_args(argv)

    if args.command == "generate":
        payload = {
            "runner": "goal2348_rtnn_v2_2_external_runner",
            "generated": generate_uniform_point_file(
                args.point_file,
                point_count=args.point_count,
                dimension=args.dimension,
                seed=args.seed,
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
    else:  # pragma: no cover - argparse guards this
        raise AssertionError(args.command)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
