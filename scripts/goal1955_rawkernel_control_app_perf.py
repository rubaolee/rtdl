#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import statistics
import subprocess
import sys
import time
from typing import Callable
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_control_apps_cupy_rawkernel as rawkernel_apps
from examples import rtdl_database_analytics_app
from examples import rtdl_graph_analytics_app
from examples import rtdl_polygon_pair_overlap_area_rows
from examples import rtdl_polygon_set_jaccard


DEFAULT_COPIES = {
    "database_analytics": 100_000,
    "graph_analytics": 1_000_000,
    "polygon_pair_overlap_area_rows": 512,
    "polygon_set_jaccard": 512,
}


def _timed(fn: Callable[[], dict[str, object]]) -> tuple[dict[str, object], float]:
    start = time.perf_counter()
    payload = fn()
    return payload, time.perf_counter() - start


def _progress(message: str) -> None:
    print(f"[goal1955-perf] {message}", file=sys.stderr, flush=True)


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "min_s": min(values),
        "median_s": statistics.median(values),
        "max_s": max(values),
    }


def _payload_signature(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _compact_value(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _compact_value(item) for key, item in value.items()}
    if isinstance(value, list):
        if len(value) <= 16:
            return [_compact_value(item) for item in value]
        return {
            "list_length": len(value),
            "sha256": _payload_signature(value),
            "head": value[:8],
            "tail": value[-8:],
        }
    return value


def _compact_payload(payload: dict[str, object] | None) -> dict[str, object] | None:
    if payload is None:
        return None
    compact: dict[str, object] = {
        "sha256": _payload_signature(payload),
    }
    if "summary" in payload:
        compact["summary"] = _compact_value(payload["summary"])
    if "app" in payload:
        compact["app"] = payload["app"]
    if "partner" in payload:
        compact["partner"] = payload["partner"]
    if "candidate_backend" in payload:
        compact["candidate_backend"] = payload["candidate_backend"]
    if "matches_v1_8_python_rtdl_oracle" in payload:
        compact["matches_v1_8_python_rtdl_oracle"] = payload["matches_v1_8_python_rtdl_oracle"]
    return compact


def _values_match(left: object, right: object) -> bool:
    if isinstance(left, dict) and isinstance(right, dict):
        return set(left) == set(right) and all(_values_match(left[key], right[key]) for key in left)
    if isinstance(left, float) or isinstance(right, float):
        return math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-12)
    return left == right


def _summaries_match(v1_8_payload: dict[str, object] | None, v2_payload: dict[str, object]) -> bool | None:
    if v1_8_payload is None:
        return v2_payload.get("matches_v1_8_python_rtdl_oracle")  # type: ignore[return-value]
    return _values_match(v1_8_payload.get("summary"), v2_payload.get("summary"))


def _git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()
    except Exception:
        return ""


def _gpu_info() -> dict[str, object]:
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version",
                "--format=csv,noheader",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        return {"nvidia_smi": lines}
    except Exception:
        return {"nvidia_smi": []}


def _v1_8_payload(app: str, copies: int) -> dict[str, object]:
    if app == "database_analytics":
        payload = rtdl_database_analytics_app.run_app(
            "cpu_python_reference",
            copies=copies,
            output_mode="compact_summary",
        )
        return {
            "summary": {
                "regional_dashboard": payload["sections"]["regional_dashboard"]["summary"],
                "sales_risk": payload["sections"]["sales_risk"]["summary"],
            }
        }
    if app == "graph_analytics":
        return {
            "summary": {
                "bfs": rtdl_graph_analytics_app.run_app(
                    "cpu_python_reference",
                    scenario="bfs",
                    copies=copies,
                    output_mode="summary",
                )["sections"]["bfs"]["summary"],
                "triangle_count": rtdl_graph_analytics_app.run_app(
                    "cpu_python_reference",
                    scenario="triangle_count",
                    copies=copies,
                    output_mode="summary",
                )["sections"]["triangle_count"]["summary"],
                "visibility_edges": rtdl_graph_analytics_app.run_app(
                    "cpu_python_reference",
                    scenario="visibility_edges",
                    copies=copies,
                    output_mode="summary",
                )["sections"]["visibility_edges"]["summary"],
            }
        }
    if app == "polygon_pair_overlap_area_rows":
        return rtdl_polygon_pair_overlap_area_rows.run_case(
            "cpu_python_reference",
            copies=copies,
            output_mode="summary",
        )
    if app == "polygon_set_jaccard":
        return rtdl_polygon_set_jaccard.run_case(
            "cpu_python_reference",
            copies=copies,
            output_mode="summary",
        )
    raise ValueError(f"unsupported app: {app}")


def run_one(
    app: str,
    *,
    copies: int,
    partner: str,
    candidate_backend: str,
    repeats: int,
    warmups: int,
    include_v1_8: bool,
    source_commit_label: str | None,
) -> dict[str, object]:
    _progress(
        f"app={app} copies={copies} partner={partner} candidate_backend={candidate_backend} "
        f"warmups={warmups} repeats={repeats} include_v1_8={include_v1_8}"
    )
    for index in range(warmups):
        _progress(f"app={app} warmup {index + 1}/{warmups} start")
        rawkernel_apps.run_control_app(
            app,
            copies=copies,
            partner=partner,
            candidate_backend=candidate_backend,
            verify_oracle=False,
        )
        _progress(f"app={app} warmup {index + 1}/{warmups} done")

    v2_times: list[float] = []
    v2_payload: dict[str, object] | None = None
    for index in range(repeats):
        _progress(f"app={app} v2 repeat {index + 1}/{repeats} start")
        v2_payload, elapsed = _timed(
            lambda: rawkernel_apps.run_control_app(
                app,
                copies=copies,
                partner=partner,
                candidate_backend=candidate_backend,
                verify_oracle=False,
            )
        )
        v2_times.append(elapsed)
        _progress(f"app={app} v2 repeat {index + 1}/{repeats} done elapsed_s={elapsed:.6f}")
    assert v2_payload is not None

    v1_8_payload = None
    v1_8_times: list[float] = []
    if include_v1_8:
        for index in range(repeats):
            _progress(f"app={app} v1_8 repeat {index + 1}/{repeats} start")
            v1_8_payload, elapsed = _timed(lambda: _v1_8_payload(app, copies))
            v1_8_times.append(elapsed)
            _progress(f"app={app} v1_8 repeat {index + 1}/{repeats} done elapsed_s={elapsed:.6f}")

    v1_summary = _summary(v1_8_times) if v1_8_times else None
    v2_summary = _summary(v2_times)
    ratio = (
        v2_summary["median_s"] / v1_summary["median_s"]
        if v1_summary and v1_summary["median_s"] > 0
        else None
    )
    matches_oracle = _summaries_match(v1_8_payload, v2_payload)
    return {
        "app": app,
        "copies": copies,
        "partner": partner,
        "candidate_backend": candidate_backend,
        "repeats": repeats,
        "warmups": warmups,
        "v1_8_python_rtdl_wall": v1_summary,
        "v2_rawkernel_wall": v2_summary,
        "v2_vs_v1_8_ratio": ratio,
        "v1_8_payload_signature": _compact_payload(v1_8_payload),
        "v2_payload_signature": _compact_payload(v2_payload),
        "matches_v1_8_python_rtdl_oracle": matches_oracle,
        "fairness_note": rawkernel_apps.FAIRNESS_NOTE,
    }


def build_payload(
    apps: list[str],
    *,
    copies: int | None,
    partner: str,
    candidate_backend: str,
    repeats: int,
    warmups: int,
    include_v1_8: bool,
    source_commit_label: str | None,
) -> dict[str, object]:
    results = [
        run_one(
            app,
            copies=DEFAULT_COPIES[app] if copies is None else copies,
            partner=partner,
            candidate_backend=candidate_backend,
            repeats=repeats,
            warmups=warmups,
            include_v1_8=include_v1_8,
            source_commit_label=source_commit_label,
        )
        for app in apps
    ]
    return {
        "goal": "Goal1955",
        "status": "rawkernel-control-app-perf-smoke",
        "source_commit": _git_commit(),
        "source_commit_label": source_commit_label or _git_commit(),
        "gpu_info": _gpu_info(),
        "partner": partner,
        "candidate_backend": candidate_backend,
        "results": results,
        "all_match_v1_8_python_rtdl_oracle": all(
            bool(result["matches_v1_8_python_rtdl_oracle"]) for result in results
        ),
        "claim_boundary": {
            "counts_as_v2_app_version": partner == "cupy",
            "local_linux_gtx1070_is_release_perf_evidence": False,
            "requires_pod_for_release_timing": True,
            "comparison_is_not_absolutely_fair": True,
            "whole_app_speedup_claim_authorized_without_review": False,
        },
        "fairness_note": (
            "Per explicit user decision, compare v2 Python+CuPy RawKernel+RTDL "
            "against v1.8 Python+RTDL with no user C/C++ extension. This is useful "
            "but not absolutely fair."
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure former-control apps with v2 RawKernel continuations.")
    parser.add_argument("--apps", default="all")
    parser.add_argument("--copies", type=int, default=None)
    parser.add_argument("--partner", choices=("cpu_fallback", "cupy"), default="cupy")
    parser.add_argument("--candidate-backend", choices=("cpu_all_pairs", "cupy_extent", "embree", "optix"), default="cpu_all_pairs")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--skip-v1-8", action="store_true")
    parser.add_argument("--source-commit-label", default=None)
    parser.add_argument("--output", default="docs/reports/goal1955_rawkernel_control_app_perf.json")
    args = parser.parse_args(list(argv) if argv is not None else None)

    apps = list(rawkernel_apps.CONTROL_APPS) if args.apps == "all" else [item.strip() for item in args.apps.split(",")]
    for app in apps:
        if app not in rawkernel_apps.CONTROL_APPS:
            raise ValueError(f"unsupported app: {app}")
    if args.copies is not None and args.copies <= 0:
        raise ValueError("--copies must be positive")
    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")
    if args.warmups < 0:
        raise ValueError("--warmups must be non-negative")

    payload = build_payload(
        apps,
        copies=args.copies,
        partner=args.partner,
        candidate_backend=args.candidate_backend,
        repeats=args.repeats,
        warmups=args.warmups,
        include_v1_8=not args.skip_v1_8,
        source_commit_label=args.source_commit_label,
    )
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
