from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.current.getting_started.rtdl_hello_world_backends import hello_world_kernel
from examples.current.getting_started.rtdl_hello_world_backends import make_scene


BACKENDS = ("cpu_python_reference", "cpu", "embree", "optix", "vulkan")


@dataclass(frozen=True)
class PreparedHelloWorldScene:
    rays: tuple[Any, ...]
    triangles: tuple[Any, ...]
    visible_label: str
    expected_triangle_hit_count: int

    @property
    def dataset(self) -> dict[str, object]:
        return {
            "name": "hello_world_ray_triangle_scene",
            "ray_count": len(self.rays),
            "triangle_count": len(self.triangles),
            "expected_visible_label": self.visible_label,
        }

    def run(self, backend: str) -> tuple[dict[str, object], ...]:
        return _run_rows(backend, self.rays, self.triangles)


def _run_rows(backend: str, rays: tuple[Any, ...], triangles: tuple[Any, ...]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(hello_world_kernel, rays=rays, triangles=triangles)
    elif backend == "cpu":
        rows = rt.run_cpu(hello_world_kernel, rays=rays, triangles=triangles)
    elif backend == "embree":
        rows = rt.run_embree(hello_world_kernel, rays=rays, triangles=triangles)
    elif backend == "optix":
        rows = rt.run_optix(hello_world_kernel, rays=rays, triangles=triangles)
    elif backend == "vulkan":
        rows = rt.run_vulkan(hello_world_kernel, rays=rays, triangles=triangles)
    else:
        raise ValueError(f"unsupported backend: {backend}")
    return tuple(dict(row) for row in rows)


def _prepare_scene() -> PreparedHelloWorldScene:
    rays, rectangles, triangles = make_scene()
    hit_rectangles = [rect for rect in rectangles if rect.y0 <= 0.0 <= rect.y1]
    if len(hit_rectangles) != 1:
        raise AssertionError(f"expected exactly one visible hit rectangle, got {hit_rectangles}")
    return PreparedHelloWorldScene(
        rays=tuple(rays),
        triangles=tuple(triangles),
        visible_label=hit_rectangles[0].label,
        expected_triangle_hit_count=2,
    )


def _cache_backend_name(backend: str) -> str:
    return "cpu" if backend == "cpu_python_reference" else backend


def _git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    commit = completed.stdout.strip()
    return commit or "unknown"


def _command_for(*, backend: str, repeats: int, warmup: int) -> str:
    command = ["python", "examples/current/getting_started/rtdl_prepared_measurement_demo.py"]
    if backend != "cpu_python_reference":
        command.extend(["--backend", backend])
    if repeats != 5:
        command.extend(["--repeats", str(repeats)])
    if warmup != 1:
        command.extend(["--warmup", str(warmup)])
    return " ".join(command)


def run_demo(
    *,
    backend: str = "cpu_python_reference",
    repeats: int = 5,
    warmup: int = 1,
) -> dict[str, object]:
    if backend not in BACKENDS:
        raise ValueError(f"unsupported backend: {backend}")
    if int(repeats) <= 0:
        raise ValueError("repeats must be positive")
    if int(warmup) < 0:
        raise ValueError("warmup must be non-negative")

    setup_start = perf_counter()
    cache = rt.ExplicitPreparedSessionCache(max_entries=1)
    key = rt.make_prepared_session_cache_key(
        primitive="ray_triangle_any_hit_count_2d",
        backend=_cache_backend_name(backend),
        input_fingerprints={
            "rays": {"rows": 1, "source": "hello_world_demo"},
            "triangles": {"rows": 6, "source": "hello_world_demo"},
        },
        parameters={"accel": "bvh", "precision": "float_approx"},
        partner="none",
        device="host",
    )
    policy = rt.RtdlPreparedSessionResidencyPolicy(
        cache_key=key,
        cache_enabled=True,
        cold_prepare_phase="prepare_scene_or_payload",
        hot_query_phase="steady_state_kernel_run",
    )
    setup_s = perf_counter() - setup_start

    prepare_call_count = 0

    def prepare_session() -> PreparedHelloWorldScene:
        nonlocal prepare_call_count
        prepare_call_count += 1
        return _prepare_scene()

    prepare_start = perf_counter()
    first = rt.get_or_prepare_explicit_session(cache, key, prepare_session, policy=policy)
    prepare_s = perf_counter() - prepare_start

    reuse_start = perf_counter()
    second = rt.get_or_prepare_explicit_session(cache, key, prepare_session, policy=policy)
    cache_reuse_check_s = perf_counter() - reuse_start

    prepared = second.value
    warmup_start = perf_counter()
    for _ in range(int(warmup)):
        prepared.run(backend)
    warmup_s = perf_counter() - warmup_start

    repeat_timings: list[float] = []
    steady_rows: list[tuple[dict[str, object], ...]] = []
    for _ in range(int(repeats)):
        repeat_start = perf_counter()
        rows = prepared.run(backend)
        repeat_timings.append(perf_counter() - repeat_start)
        steady_rows.append(rows)
    steady_state_s = sum(repeat_timings)

    validation_start = perf_counter()
    oracle_rows = prepared.run("cpu_python_reference")
    rows_match_oracle = all(rows == oracle_rows for rows in steady_rows)
    last_rows = steady_rows[-1]
    triangle_hit_count = int(last_rows[0]["hit_count"]) if last_rows else 0
    correctness_ok = (
        rows_match_oracle
        and triangle_hit_count == prepared.expected_triangle_hit_count
        and prepared.visible_label == "hello, world"
    )
    validation_s = perf_counter() - validation_start

    return {
        "app": "prepared_measurement_demo",
        "status": "current_v3_teaching_demo",
        "command": _command_for(backend=backend, repeats=int(repeats), warmup=int(warmup)),
        "commit": _git_commit(),
        "backend": backend,
        "partner": "none",
        "dataset": prepared.dataset,
        "timed_phase": "steady_state_kernel_run",
        "warmup_repeat_count": int(warmup),
        "steady_state_repeat_count": int(repeats),
        "steady_state_repeat_timings_s": repeat_timings,
        "steady_state_total_s": steady_state_s,
        "steady_state_avg_s": steady_state_s / int(repeats),
        "phases_s": {
            "setup": setup_s,
            "prepare": prepare_s,
            "cache_reuse_check": cache_reuse_check_s,
            "warmup": warmup_s,
            "steady_state": steady_state_s,
            "validation": validation_s,
        },
        "prepared_session_residency": {
            "explicit_reuse_helper": "get_or_prepare_explicit_session",
            "prepared_call_count": prepare_call_count,
            "cache_hit_sequence": [first.cache_hit, second.cache_hit],
            "cache_event_log": list(second.cache_event_log),
            "policy": policy.to_metadata(),
            "cache": cache.to_metadata(),
        },
        "rows": list(last_rows),
        "correctness": {
            "validated": correctness_ok,
            "oracle_backend": "cpu_python_reference",
            "steady_rows_match_oracle": rows_match_oracle,
            "expected_triangle_hit_count": prepared.expected_triangle_hit_count,
            "observed_triangle_hit_count": triangle_hit_count,
            "visible_hit_label": prepared.visible_label,
        },
        "measurement_scope": {
            "teaching_demo_only": True,
            "setup_prepare_warmup_excluded_from_steady_state": True,
        },
    }


def summarize_demo(payload: dict[str, object]) -> dict[str, object]:
    correctness = payload["correctness"]
    prepared = payload["prepared_session_residency"]
    assert isinstance(correctness, dict)
    assert isinstance(prepared, dict)
    return {
        "app": payload["app"],
        "backend": payload["backend"],
        "validated": correctness["validated"],
        "visible_hit_label": correctness["visible_hit_label"],
        "prepared_call_count": prepared["prepared_call_count"],
        "cache_hit_sequence": prepared["cache_hit_sequence"],
        "warmup_repeat_count": payload["warmup_repeat_count"],
        "steady_state_repeat_count": payload["steady_state_repeat_count"],
        "steady_state_avg_s": payload["steady_state_avg_s"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Portable V3 prepared-session measurement discipline demo."
    )
    parser.add_argument("--backend", default="cpu_python_reference", choices=BACKENDS)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--json", action="store_true", help="Print the full measurement payload.")
    args = parser.parse_args(argv)
    payload = run_demo(backend=args.backend, repeats=args.repeats, warmup=args.warmup)
    output = payload if args.json else summarize_demo(payload)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
