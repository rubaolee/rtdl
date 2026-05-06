from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


REPORT_STEM = "goal1417_v1_5_1_collect_k_benchmark_2026-05-06"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


BackendRunner = Callable[[tuple[rt.Polygon, ...], tuple[rt.Polygon, ...], int], dict[str, object]]


def _rect(polygon_id: int, x0: float, y0: float, x1: float, y1: float) -> rt.Polygon:
    return rt.Polygon(
        polygon_id,
        (
            (x0, y0),
            (x1, y0),
            (x1, y1),
            (x0, y1),
        ),
    )


def make_benchmark_case(*, copies: int) -> dict[str, tuple[rt.Polygon, ...]]:
    """Build scaled unambiguous rectangles whose candidates equal overlap rows."""
    if copies < 1:
        raise ValueError("copies must be positive")
    left: list[rt.Polygon] = []
    right: list[rt.Polygon] = []
    for index in range(copies):
        offset = float(index * 32)
        id_offset = index * 100
        left.extend(
            (
                _rect(id_offset + 1, offset + 0.0, 0.0, offset + 3.0, 3.0),
                _rect(id_offset + 2, offset + 10.0, 0.0, offset + 14.0, 4.0),
            )
        )
        right.extend(
            (
                _rect(id_offset + 10, offset + 1.0, 1.0, offset + 4.0, 4.0),
                _rect(id_offset + 11, offset + 11.0, 1.0, offset + 13.0, 3.0),
                _rect(id_offset + 12, offset + 20.0, 20.0, offset + 21.0, 21.0),
            )
        )
    return {"left": tuple(left), "right": tuple(right)}


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _expected_candidate_rows(
    left: tuple[rt.Polygon, ...],
    right: tuple[rt.Polygon, ...],
) -> tuple[tuple[int, int], ...]:
    rows = rt.polygon_pair_overlap_area_rows_cpu(left, right)
    return tuple(
        sorted(
            (
                int(row["left_polygon_id"]),
                int(row["right_polygon_id"]),
            )
            for row in rows
        )
    )


def _reference_collect_once(
    left: tuple[rt.Polygon, ...],
    right: tuple[rt.Polygon, ...],
    capacity: int,
) -> dict[str, object]:
    rows = _expected_candidate_rows(left, right)
    return rt.collect_k_bounded_rows(rows, k=capacity, row_width=2)


def default_backend_runners() -> dict[str, BackendRunner]:
    return {
        "python_reference": _reference_collect_once,
        "embree": lambda left, right, capacity: rt.collect_polygon_pair_candidates_bounded_embree(
            left,
            right,
            candidate_capacity=capacity,
        ),
        "optix": lambda left, right, capacity: rt.collect_polygon_pair_candidates_bounded_optix(
            left,
            right,
            candidate_capacity=capacity,
        ),
    }


def _is_backend_unavailable(exc: Exception) -> bool:
    message = str(exc).lower()
    return isinstance(exc, (OSError, ImportError, ValueError)) or any(
        fragment in message
        for fragment in (
            "cannot find",
            "could not find",
            "does not export",
            "failed to load",
            "librtdl",
            "no such file",
            "unable to load",
        )
    )


def _time_call(callable_obj: Callable[[], dict[str, object]]) -> tuple[dict[str, object], float]:
    started = time.perf_counter()
    result = callable_obj()
    return result, time.perf_counter() - started


def _summarize_timings(samples: tuple[float, ...]) -> dict[str, object]:
    return {
        "samples_sec": samples,
        "min_sec": min(samples),
        "median_sec": statistics.median(samples),
        "max_sec": max(samples),
    }


def run_backend_scale(
    backend: str,
    runner: BackendRunner,
    *,
    left: tuple[rt.Polygon, ...],
    right: tuple[rt.Polygon, ...],
    capacity: int,
    expected_rows: tuple[tuple[int, int], ...],
    repeats: int,
    warmups: int,
) -> dict[str, object]:
    try:
        for _ in range(warmups):
            runner(left, right, capacity)
        samples: list[float] = []
        last_result: dict[str, object] | None = None
        for _ in range(repeats):
            result, elapsed = _time_call(lambda: runner(left, right, capacity))
            last_result = result
            samples.append(elapsed)
    except RuntimeError as exc:
        return {"status": "fail", "backend": backend, "error": str(exc)}
    except Exception as exc:
        if _is_backend_unavailable(exc):
            return {
                "status": "skipped",
                "backend": backend,
                "reason": f"{type(exc).__name__}: {exc}",
            }
        return {
            "status": "fail",
            "backend": backend,
            "error": f"{type(exc).__name__}: {exc}",
        }

    assert last_result is not None
    observed_rows = tuple(tuple(int(value) for value in row) for row in last_result["candidate_id_rows"])
    mismatches: list[str] = []
    if observed_rows != expected_rows:
        mismatches.append(f"candidate_id_rows mismatch: expected {expected_rows}, got {observed_rows}")
    if int(last_result.get("valid_count", -1)) != len(expected_rows):
        mismatches.append(f"valid_count mismatch: expected {len(expected_rows)}, got {last_result.get('valid_count')}")
    if int(last_result.get("capacity", -1)) != capacity:
        mismatches.append(f"capacity mismatch: expected {capacity}, got {last_result.get('capacity')}")
    if last_result.get("overflowed") is not False:
        mismatches.append("overflowed metadata must be False")
    if last_result.get("complete_candidate_coverage") is not True:
        mismatches.append("complete_candidate_coverage must be True")
    return {
        "status": "fail" if mismatches else "pass",
        "backend": backend,
        "candidate_count": len(expected_rows),
        "capacity": capacity,
        "timing": _summarize_timings(tuple(samples)),
        "mismatches": mismatches,
    }


def run_benchmark_package(
    *,
    copies: tuple[int, ...],
    backends: tuple[str, ...],
    required_backends: tuple[str, ...] = (),
    repeats: int = 5,
    warmups: int = 1,
    backend_runners: dict[str, BackendRunner] | None = None,
) -> dict[str, object]:
    runners = default_backend_runners()
    if backend_runners:
        runners.update(backend_runners)
    started = time.perf_counter()
    scale_results: list[dict[str, object]] = []
    for copy_count in copies:
        case_started = time.perf_counter()
        case = make_benchmark_case(copies=copy_count)
        left = case["left"]
        right = case["right"]
        expected_rows = _expected_candidate_rows(left, right)
        capacity = len(expected_rows)
        backend_results = {
            backend: run_backend_scale(
                backend,
                runners[backend],
                left=left,
                right=right,
                capacity=capacity,
                expected_rows=expected_rows,
                repeats=repeats,
                warmups=warmups,
            )
            for backend in backends
        }
        scale_results.append(
            {
                "copies": copy_count,
                "left_polygons": len(left),
                "right_polygons": len(right),
                "candidate_count": len(expected_rows),
                "capacity": capacity,
                "input_and_expected_rows_sec": time.perf_counter() - case_started,
                "backends": backend_results,
            }
        )

    failures: list[str] = []
    skipped_required: list[str] = []
    backend_summary = {backend: {"pass": 0, "fail": 0, "skipped": 0} for backend in backends}
    for scale in scale_results:
        for backend, result in scale["backends"].items():
            status = str(result["status"])
            backend_summary[backend][status] += 1
            if status == "fail":
                failures.append(f"copies={scale['copies']} backend={backend}")
            if status == "skipped" and backend in required_backends:
                skipped_required.append(f"copies={scale['copies']} backend={backend}")

    accepted = not failures and not skipped_required
    return {
        "artifact": REPORT_STEM,
        "accepted": accepted,
        "status": "accepted" if accepted else "not_accepted",
        "claim_boundary": (
            "Same-contract COLLECT_K_BOUNDED benchmark evidence only; "
            "not a public primitive promotion, not a speedup claim, and not a zero-copy claim."
        ),
        "environment": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "git_head": _git_head(),
        },
        "run_scope": {
            "copies": copies,
            "backends": backends,
            "required_backends": required_backends,
            "repeats": repeats,
            "warmups": warmups,
            "capacity_policy": "exact capacity equals expected candidate-row count",
        },
        "backend_summary": backend_summary,
        "failures": failures,
        "skipped_required": skipped_required,
        "scale_results": scale_results,
        "elapsed_sec": time.perf_counter() - started,
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Goal 1417 v1.5.1 COLLECT_K_BOUNDED Benchmark",
        "",
        "## Verdict",
        "",
        "ACCEPTED for this measured package." if report["accepted"] else "NOT ACCEPTED for this measured package.",
        "",
        str(report["claim_boundary"]),
        "",
        "## Run Scope",
        "",
        f"- Copies: {', '.join(str(value) for value in report['run_scope']['copies'])}",
        f"- Backends requested: {', '.join(report['run_scope']['backends'])}",
        f"- Required backends: {', '.join(report['run_scope']['required_backends']) or 'none'}",
        f"- Repeats: {report['run_scope']['repeats']}",
        f"- Warmups: {report['run_scope']['warmups']}",
        f"- Capacity policy: {report['run_scope']['capacity_policy']}",
        f"- Platform: {report['environment']['platform']}",
        f"- Python: {report['environment']['python']}",
        f"- Git HEAD: {report['environment']['git_head']}",
        f"- Elapsed seconds: {report['elapsed_sec']:.6f}",
        "",
        "## Backend Summary",
        "",
    ]
    for backend, summary in report["backend_summary"].items():
        lines.append(f"- {backend}: pass={summary['pass']}, fail={summary['fail']}, skipped={summary['skipped']}")
    lines.extend(["", "## Timing Table", ""])
    for scale in report["scale_results"]:
        lines.append(
            f"- copies={scale['copies']} left={scale['left_polygons']} right={scale['right_polygons']} "
            f"candidate_rows={scale['candidate_count']}"
        )
        for backend, result in scale["backends"].items():
            if result["status"] == "pass":
                timing = result["timing"]
                lines.append(
                    f"- copies={scale['copies']} backend={backend} status=pass "
                    f"median_sec={timing['median_sec']:.9f} min_sec={timing['min_sec']:.9f} max_sec={timing['max_sec']:.9f}"
                )
            else:
                detail = result.get("error") or result.get("reason") or ""
                lines.append(f"- copies={scale['copies']} backend={backend} status={result['status']} {detail}")
    lines.extend(["", "## Files", ""])
    lines.append(f"- JSON artifact: `docs/reports/{REPORT_STEM}.json`")
    lines.append(f"- Markdown artifact: `docs/reports/{REPORT_STEM}.md`")
    return "\n".join(lines) + "\n"


def _parse_int_tuple(values: list[str] | None, default: tuple[int, ...]) -> tuple[int, ...]:
    if not values:
        return default
    parsed = tuple(int(value) for value in values)
    if any(value <= 0 for value in parsed):
        raise ValueError("copies must be positive")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--copies", action="append", help="Scale copy count. May be passed more than once.")
    parser.add_argument(
        "--backend",
        action="append",
        choices=("python_reference", "embree", "optix"),
        help="Backend to include. May be passed more than once.",
    )
    parser.add_argument(
        "--require-backend",
        action="append",
        choices=("python_reference", "embree", "optix"),
        default=[],
        help="Fail the package if this backend is skipped.",
    )
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")
    if args.warmups < 0:
        raise ValueError("--warmups must be non-negative")
    report = run_benchmark_package(
        copies=_parse_int_tuple(args.copies, (1, 16, 64)),
        backends=tuple(args.backend or ("python_reference", "embree", "optix")),
        required_backends=tuple(args.require_backend),
        repeats=args.repeats,
        warmups=args.warmups,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.markdown_out.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "json": str(args.json_out), "markdown": str(args.markdown_out)}))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
