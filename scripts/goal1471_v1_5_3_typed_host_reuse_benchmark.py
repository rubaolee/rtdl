from __future__ import annotations

import argparse
import ctypes
import json
import platform
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from scripts.goal1467_v1_5_3_typed_host_buffer_parity import is_backend_unavailable
from scripts.goal1467_v1_5_3_typed_host_buffer_parity import load_backend_library
from scripts.goal1467_v1_5_3_typed_host_buffer_parity import symbol_name_for_backend


REPORT_STEM = "goal1471_v1_5_3_typed_host_reuse_benchmark_2026-05-07"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def build_candidate_rows(*, unique_rows: int, repeats: int) -> tuple[tuple[int, int], ...]:
    if unique_rows <= 0:
        raise ValueError("unique_rows must be positive")
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    base_rows = tuple((row_id, (row_id * 17) % max(unique_rows, 1)) for row_id in range(unique_rows))
    return tuple(row for _ in range(repeats) for row in base_rows)


def output_buffer(capacity: int) -> Any:
    return (ctypes.c_int64 * (int(capacity) * 2))()


def run_backend_benchmark(
    backend: str,
    *,
    unique_rows: int,
    repeats: int,
    iterations: int,
) -> dict[str, Any]:
    candidate_rows = build_candidate_rows(unique_rows=unique_rows, repeats=repeats)
    capacity = unique_rows
    try:
        library = load_backend_library(backend)
        descriptor = rt.prepare_collect_k_result_buffer_descriptor(
            capacity=capacity,
            row_width=2,
            backend=backend,
            device="cpu",
            owner="rtdl",
            mutability="mutable",
            copy_boundary="prepared_host_buffer_reuse",
        )
        measurement = rt.measure_collect_k_typed_host_input_reuse(
            candidate_rows,
            descriptor,
            output_buffer=output_buffer(capacity),
            library=library,
            symbol_name=symbol_name_for_backend(backend),
            backend=backend,
            row_width=2,
            iterations=iterations,
        )
    except Exception as exc:
        status = "skipped" if is_backend_unavailable(exc) else "fail"
        return {
            "backend": backend,
            "status": status,
            "error": f"{type(exc).__name__}: {exc}",
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "release_action_authorized": False,
        }
    baseline_total = float(measurement["baseline_elapsed_total_s"])
    typed_total = float(measurement["typed_elapsed_total_s"])
    return {
        "backend": backend,
        "status": "pass",
        "candidate_row_count": len(candidate_rows),
        "unique_rows": unique_rows,
        "repeats": repeats,
        "iterations": iterations,
        "baseline_input_materialization_count": measurement["baseline_input_materialization_count"],
        "typed_input_materialization_count": measurement["typed_input_materialization_count"],
        "input_materialization_count_delta": measurement["input_materialization_count_delta"],
        "baseline_elapsed_total_s": baseline_total,
        "typed_elapsed_total_s": typed_total,
        "typed_to_baseline_elapsed_ratio": typed_total / baseline_total if baseline_total else None,
        "timing_recorded_for_diagnostics_only": True,
        "copy_count_or_transfer_count_measurement": True,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
    }


def run_benchmark_package(
    *,
    backends: tuple[str, ...],
    required_backends: tuple[str, ...],
    unique_rows: int,
    repeats: int,
    iterations: int,
) -> dict[str, Any]:
    results = tuple(
        run_backend_benchmark(
            backend,
            unique_rows=unique_rows,
            repeats=repeats,
            iterations=iterations,
        )
        for backend in backends
    )
    failed = tuple(row for row in results if row["status"] == "fail")
    skipped_required = tuple(
        row for row in results if row["backend"] in required_backends and row["status"] == "skipped"
    )
    accepted = not failed and not skipped_required
    return {
        "goal": "Goal1471",
        "status": "accepted" if accepted else "not_accepted",
        "accepted": accepted,
        "scope": "v1.5.3 typed host input reuse diagnostic benchmark",
        "primitive": "COLLECT_K_BOUNDED",
        "platform": platform.platform(),
        "python": sys.version,
        "backends": backends,
        "required_backends": required_backends,
        "unique_rows": unique_rows,
        "repeats": repeats,
        "iterations": iterations,
        "results": results,
        "failed": failed,
        "skipped_required": skipped_required,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This benchmark records wrapper-level input materialization counts "
            "and diagnostic timing for the accepted typed host path only. It "
            "does not authorize true zero-copy, public speedup wording, "
            "whole-app claims, stable primitive promotion, partner tensor "
            "handoff, or release action."
        ),
    }


def write_outputs(payload: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# Goal1471 v1.5.3 Typed Host Reuse Benchmark",
        "",
        "## Verdict",
        "",
        "ACCEPTED." if payload["accepted"] else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        "- Primitive: `COLLECT_K_BOUNDED`",
        "- Surface: typed host input reuse plus prepared host output",
        f"- Backends: {', '.join(payload['backends'])}",
        f"- Required backends: {', '.join(payload['required_backends']) or '(none)'}",
        f"- Unique rows: {payload['unique_rows']}",
        f"- Repeats: {payload['repeats']}",
        f"- Iterations: {payload['iterations']}",
        "",
        "## Results",
        "",
    ]
    for row in payload["results"]:
        if row["status"] != "pass":
            lines.append(f"- `{row['backend']}`: {row['status']} ({row.get('error')})")
            continue
        lines.append(
            f"- `{row['backend']}`: baseline_materializations="
            f"{row['baseline_input_materialization_count']} "
            f"typed_materializations={row['typed_input_materialization_count']} "
            f"delta={row['input_materialization_count_delta']} "
            f"baseline_total_s={row['baseline_elapsed_total_s']:.6f} "
            f"typed_total_s={row['typed_elapsed_total_s']:.6f} "
            f"ratio={row['typed_to_baseline_elapsed_ratio']:.6f}"
        )
    lines.extend(["", "## Boundary", "", payload["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backends", nargs="+", default=["embree", "optix"])
    parser.add_argument("--required-backends", nargs="*", default=[])
    parser.add_argument("--unique-rows", type=int, default=4096)
    parser.add_argument("--repeats", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_PATH))
    args = parser.parse_args(argv)
    payload = run_benchmark_package(
        backends=tuple(args.backends),
        required_backends=tuple(args.required_backends),
        unique_rows=args.unique_rows,
        repeats=args.repeats,
        iterations=args.iterations,
    )
    write_outputs(payload, Path(args.json_out), Path(args.md_out))
    print(json.dumps(payload["results"], indent=2, sort_keys=True, default=str))
    return 0 if payload["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
