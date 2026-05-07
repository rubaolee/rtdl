from __future__ import annotations

import argparse
import ctypes
import json
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


REPORT_STEM = "goal1467_v1_5_3_typed_host_buffer_parity_2026-05-07"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


@dataclass(frozen=True)
class TypedHostParityCase:
    name: str
    candidate_rows: tuple[tuple[int, int], ...]
    capacity: int
    expect_overflow: bool


def build_parity_cases() -> tuple[TypedHostParityCase, ...]:
    rows = ((2, 11), (1, 10), (2, 11))
    return (
        TypedHostParityCase("empty_zero_capacity", (), 0, False),
        TypedHostParityCase("exact_fit_two_rows_deduplicated_sorted", rows, 2, False),
        TypedHostParityCase("one_short_fail_closed_overflow", rows, 1, True),
        TypedHostParityCase("zero_capacity_positive_fail_closed_overflow", rows, 0, True),
    )


def expected_candidate_rows(case: TypedHostParityCase) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(set(case.candidate_rows)))


def symbol_name_for_backend(backend: str) -> str:
    if backend == "embree":
        return "rtdl_embree_collect_k_bounded_i64"
    if backend == "optix":
        return "rtdl_optix_collect_k_bounded_i64"
    raise ValueError(f"unsupported typed-host parity backend: {backend}")


def load_backend_library(backend: str) -> Any:
    if backend == "embree":
        from rtdsl import embree_runtime

        return embree_runtime._load_embree_library()
    if backend == "optix":
        from rtdsl import optix_runtime

        return optix_runtime._load_optix_library()
    raise ValueError(f"unsupported typed-host parity backend: {backend}")


def prepared_output_descriptor(backend: str, capacity: int) -> dict[str, Any]:
    return rt.prepare_collect_k_result_buffer_descriptor(
        capacity=int(capacity),
        row_width=2,
        backend=backend,
        device="cpu",
        owner="rtdl",
        mutability="mutable",
        copy_boundary="prepared_host_buffer_reuse",
    )


def output_buffer(capacity: int) -> Any:
    output_len = int(capacity) * 2
    return (ctypes.c_int64 * output_len)() if output_len else None


def is_backend_unavailable(exc: Exception) -> bool:
    message = str(exc).lower()
    unavailable_fragments = (
        "does not export",
        "cannot find",
        "could not find",
        "no such file",
        "unable to load",
        "failed to load",
        "dll",
        ".so",
        "optix",
        "cuda",
        "driver",
    )
    return isinstance(exc, (OSError, ImportError, ValueError, FileNotFoundError)) or any(
        fragment in message for fragment in unavailable_fragments
    )


def run_backend_case(backend: str, library: Any, case: TypedHostParityCase) -> dict[str, Any]:
    started = time.perf_counter()
    symbol_name = symbol_name_for_backend(backend)
    input_descriptor = rt.prepare_collect_k_i64_host_input_buffer(case.candidate_rows, row_width=2)
    output_descriptor = prepared_output_descriptor(backend, case.capacity)
    rows_out = output_buffer(case.capacity)
    expected_rows = expected_candidate_rows(case)
    try:
        envelope = rt.run_native_collect_k_bounded_with_typed_host_buffers(
            input_descriptor,
            output_descriptor,
            output_buffer=rows_out,
            library=library,
            symbol_name=symbol_name,
            backend=backend,
            candidate_source_symbol="goal1467_typed_host_i64_rows",
        )
    except Exception as exc:
        if case.expect_overflow and "overflowed prepared output capacity" in str(exc):
            return {
                "status": "pass",
                "case": case.name,
                "backend": backend,
                "capacity": case.capacity,
                "expect_overflow": True,
                "observed_overflow": True,
                "expected_rows": expected_rows,
                "typed_contiguous_host_buffer_path": True,
                "elapsed_sec": time.perf_counter() - started,
            }
        if is_backend_unavailable(exc):
            return {
                "status": "skipped",
                "case": case.name,
                "backend": backend,
                "capacity": case.capacity,
                "expect_overflow": case.expect_overflow,
                "reason": f"{type(exc).__name__}: {exc}",
                "elapsed_sec": time.perf_counter() - started,
            }
        return {
            "status": "fail",
            "case": case.name,
            "backend": backend,
            "capacity": case.capacity,
            "expect_overflow": case.expect_overflow,
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_sec": time.perf_counter() - started,
        }
    observed_rows = tuple(tuple(int(value) for value in row) for row in envelope["result"]["candidate_id_rows"])
    mismatches: list[str] = []
    if case.expect_overflow:
        mismatches.append("expected overflow but typed-host envelope completed")
    if observed_rows != expected_rows:
        mismatches.append(f"candidate_id_rows mismatch: expected {expected_rows}, got {observed_rows}")
    if envelope["backend"] != backend:
        mismatches.append(f"backend metadata mismatch: expected {backend}, got {envelope['backend']}")
    if envelope["result"]["valid_count"] != len(expected_rows):
        mismatches.append(
            f"valid_count mismatch: expected {len(expected_rows)}, got {envelope['result']['valid_count']}"
        )
    if envelope["typed_contiguous_host_buffer_path"] is not True:
        mismatches.append("typed host input path flag was not true")
    return {
        "status": "fail" if mismatches else "pass",
        "case": case.name,
        "backend": backend,
        "capacity": case.capacity,
        "expect_overflow": case.expect_overflow,
        "expected_rows": expected_rows,
        "observed_rows": observed_rows,
        "valid_count": envelope["result"]["valid_count"],
        "typed_contiguous_host_buffer_path": envelope["typed_contiguous_host_buffer_path"],
        "prepared_output_buffer_reused_by_python_wrapper": envelope[
            "prepared_output_buffer_reused_by_python_wrapper"
        ],
        "mismatches": tuple(mismatches),
        "elapsed_sec": time.perf_counter() - started,
    }


def run_acceptance_package(
    *,
    backends: tuple[str, ...] = ("embree", "optix"),
    required_backends: tuple[str, ...] = (),
) -> dict[str, Any]:
    cases = build_parity_cases()
    backend_results: list[dict[str, Any]] = []
    for backend in backends:
        try:
            library = load_backend_library(backend)
        except Exception as exc:
            for case in cases:
                backend_results.append(
                    {
                        "status": "skipped",
                        "case": case.name,
                        "backend": backend,
                        "capacity": case.capacity,
                        "expect_overflow": case.expect_overflow,
                        "reason": f"{type(exc).__name__}: {exc}",
                        "elapsed_sec": 0.0,
                    }
                )
            continue
        for case in cases:
            backend_results.append(run_backend_case(backend, library, case))
    backend_summary = {
        backend: {
            "pass": sum(1 for row in backend_results if row["backend"] == backend and row["status"] == "pass"),
            "fail": sum(1 for row in backend_results if row["backend"] == backend and row["status"] == "fail"),
            "skipped": sum(1 for row in backend_results if row["backend"] == backend and row["status"] == "skipped"),
        }
        for backend in backends
    }
    skipped_required = tuple(
        row
        for row in backend_results
        if row["backend"] in required_backends and row["status"] == "skipped"
    )
    failed = tuple(row for row in backend_results if row["status"] == "fail")
    accepted = not failed and not skipped_required
    return {
        "goal": "Goal1467",
        "status": "accepted" if accepted else "not_accepted",
        "accepted": accepted,
        "primitive": "COLLECT_K_BOUNDED",
        "scope": "v1.5.3 typed host input plus prepared host output backend parity",
        "platform": platform.platform(),
        "python": sys.version,
        "backends": backends,
        "required_backends": required_backends,
        "cases": tuple(case.__dict__ for case in cases),
        "results": tuple(backend_results),
        "backend_summary": backend_summary,
        "failed": failed,
        "skipped_required": skipped_required,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This package validates typed host input plus prepared host output "
            "same-contract backend parity only. It does not authorize true "
            "zero-copy, public speedup wording, whole-app claims, stable "
            "primitive promotion, partner tensor handoff, or release action."
        ),
    }


def write_outputs(payload: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# Goal1467 v1.5.3 Typed Host Buffer Backend Parity",
        "",
        "## Verdict",
        "",
        "ACCEPTED." if payload["accepted"] else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        "- Primitive: `COLLECT_K_BOUNDED`",
        "- Surface: typed host input plus prepared host output",
        f"- Backends: {', '.join(payload['backends'])}",
        f"- Required backends: {', '.join(payload['required_backends']) or '(none)'}",
        "",
        "## Backend Summary",
        "",
    ]
    for backend, summary in payload["backend_summary"].items():
        lines.append(
            f"- `{backend}`: pass={summary['pass']} fail={summary['fail']} skipped={summary['skipped']}"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            payload["claim_boundary"],
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backends", nargs="+", default=["embree", "optix"])
    parser.add_argument("--required-backends", nargs="*", default=[])
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_PATH))
    args = parser.parse_args(argv)
    payload = run_acceptance_package(
        backends=tuple(args.backends),
        required_backends=tuple(args.required_backends),
    )
    write_outputs(payload, Path(args.json_out), Path(args.md_out))
    print(json.dumps(payload["backend_summary"], indent=2, sort_keys=True))
    return 0 if payload["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
