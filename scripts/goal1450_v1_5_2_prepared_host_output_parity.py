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


REPORT_STEM = "goal1450_v1_5_2_prepared_host_output_parity_2026-05-07"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


@dataclass(frozen=True)
class PreparedHostOutputParityCase:
    name: str
    candidate_rows: tuple[tuple[int, int], ...]
    capacity: int
    expect_overflow: bool


def build_parity_cases() -> tuple[PreparedHostOutputParityCase, ...]:
    """Return app-generic row cases for prepared host-output parity."""
    rows = ((2, 11), (1, 10), (2, 11))
    return (
        PreparedHostOutputParityCase(
            name="empty_zero_capacity",
            candidate_rows=(),
            capacity=0,
            expect_overflow=False,
        ),
        PreparedHostOutputParityCase(
            name="exact_fit_two_rows_deduplicated_sorted",
            candidate_rows=rows,
            capacity=2,
            expect_overflow=False,
        ),
        PreparedHostOutputParityCase(
            name="one_short_fail_closed_overflow",
            candidate_rows=rows,
            capacity=1,
            expect_overflow=True,
        ),
        PreparedHostOutputParityCase(
            name="zero_capacity_positive_fail_closed_overflow",
            candidate_rows=rows,
            capacity=0,
            expect_overflow=True,
        ),
    )


def expected_candidate_rows(case: PreparedHostOutputParityCase) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(set(case.candidate_rows)))


def _symbol_name_for_backend(backend: str) -> str:
    if backend == "embree":
        return "rtdl_embree_collect_k_bounded_i64"
    if backend == "optix":
        return "rtdl_optix_collect_k_bounded_i64"
    raise ValueError(f"unsupported prepared host-output backend: {backend}")


def _load_backend_library(backend: str) -> Any:
    if backend == "embree":
        from rtdsl import embree_runtime

        return embree_runtime._load_embree_library()
    if backend == "optix":
        from rtdsl import optix_runtime

        return optix_runtime._load_optix_library()
    raise ValueError(f"unsupported prepared host-output backend: {backend}")


def _prepared_descriptor(backend: str, capacity: int) -> dict[str, Any]:
    return rt.prepare_collect_k_result_buffer_descriptor(
        capacity=int(capacity),
        row_width=2,
        backend=backend,
        device="cpu",
        owner="rtdl",
        mutability="mutable",
        copy_boundary="prepared_host_buffer_reuse",
    )


def _output_buffer(capacity: int) -> Any:
    output_len = int(capacity) * 2
    if output_len == 0:
        return None
    return (ctypes.c_int64 * output_len)()


def _is_backend_unavailable(exc: Exception) -> bool:
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


def run_backend_case(
    backend: str,
    library: Any,
    case: PreparedHostOutputParityCase,
) -> dict[str, Any]:
    started = time.perf_counter()
    symbol_name = _symbol_name_for_backend(backend)
    descriptor = _prepared_descriptor(backend, case.capacity)
    output_buffer = _output_buffer(case.capacity)
    expected_rows = expected_candidate_rows(case)
    try:
        if case.expect_overflow:
            evidence = rt.validate_native_collect_k_prepared_host_output_overflow_fail_closed(
                case.candidate_rows,
                descriptor,
                output_buffer=output_buffer,
                library=library,
                symbol_name=symbol_name,
                candidate_source_symbol="goal1450_app_generic_i64_rows",
                backend=backend,
            )
            return {
                "status": "pass",
                "case": case.name,
                "backend": backend,
                "capacity": case.capacity,
                "expect_overflow": True,
                "observed_overflow": True,
                "expected_rows": expected_rows,
                "evidence_status": evidence["status"],
                "partial_result_returned": evidence["partial_result_returned"],
                "elapsed_sec": time.perf_counter() - started,
            }
        envelope = rt.run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
            case.candidate_rows,
            descriptor,
            output_buffer=output_buffer,
            library=library,
            symbol_name=symbol_name,
            candidate_source_symbol="goal1450_app_generic_i64_rows",
            backend=backend,
        )
    except Exception as exc:
        if _is_backend_unavailable(exc):
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
    if observed_rows != expected_rows:
        mismatches.append(f"candidate_id_rows mismatch: expected {expected_rows}, got {observed_rows}")
    if envelope["backend"] != backend:
        mismatches.append(f"backend metadata mismatch: expected {backend}, got {envelope['backend']}")
    if envelope["result"]["valid_count"] != len(expected_rows):
        mismatches.append(
            f"valid_count mismatch: expected {len(expected_rows)}, got {envelope['result']['valid_count']}"
        )
    if envelope["result"]["prepared_output_buffer_reused_by_python_wrapper"] is not True:
        mismatches.append("prepared output buffer was not reported as reused by the Python wrapper")
    return {
        "status": "fail" if mismatches else "pass",
        "case": case.name,
        "backend": backend,
        "capacity": case.capacity,
        "expect_overflow": False,
        "expected_rows": expected_rows,
        "observed_rows": observed_rows,
        "valid_count": envelope["result"]["valid_count"],
        "prepared_output_buffer_reused_by_python_wrapper": envelope["result"][
            "prepared_output_buffer_reused_by_python_wrapper"
        ],
        "mismatches": tuple(mismatches),
        "elapsed_sec": time.perf_counter() - started,
    }


def run_acceptance_package(
    *,
    backends: tuple[str, ...] = ("embree", "optix"),
    required_backends: tuple[str, ...] = (),
    backend_libraries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cases = build_parity_cases()
    libraries = dict(backend_libraries or {})
    results: list[dict[str, Any]] = []
    for backend in backends:
        try:
            library = libraries[backend] if backend in libraries else _load_backend_library(backend)
        except Exception as exc:
            for case in cases:
                results.append(
                    {
                        "status": "skipped" if _is_backend_unavailable(exc) else "fail",
                        "case": case.name,
                        "backend": backend,
                        "capacity": case.capacity,
                        "expect_overflow": case.expect_overflow,
                        "reason" if _is_backend_unavailable(exc) else "error": (
                            f"{type(exc).__name__}: {exc}"
                        ),
                        "elapsed_sec": 0.0,
                    }
                )
            continue
        for case in cases:
            results.append(run_backend_case(backend, library, case))
    backend_summary: dict[str, dict[str, int]] = {}
    for backend in backends:
        backend_results = [result for result in results if result["backend"] == backend]
        backend_summary[backend] = {
            "pass": sum(1 for result in backend_results if result["status"] == "pass"),
            "fail": sum(1 for result in backend_results if result["status"] == "fail"),
            "skipped": sum(1 for result in backend_results if result["status"] == "skipped"),
        }
    skipped_required = tuple(
        result
        for result in results
        if result["backend"] in required_backends and result["status"] == "skipped"
    )
    failed = tuple(result for result in results if result["status"] == "fail")
    return {
        "goal": "Goal1450",
        "primitive": "COLLECT_K_BOUNDED",
        "track": "python_rtdl",
        "run_scope": "prepared_host_output_app_generic_i64_rows",
        "platform": platform.platform(),
        "python": sys.version,
        "backends": backends,
        "required_backends": required_backends,
        "case_count": len(cases),
        "results": tuple(results),
        "backend_summary": backend_summary,
        "failed": failed,
        "skipped_required": skipped_required,
        "accepted": not failed and not skipped_required,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Prepared host-output parity covers app-generic row-major i64 "
            "COLLECT_K_BOUNDED execution through the existing generic native "
            "symbols only. It does not authorize true zero-copy, public speedup "
            "wording, whole-app claims, stable primitive wording, or release action."
        ),
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    return value


def render_markdown(report: dict[str, Any]) -> str:
    verdict = "ACCEPTED" if report["accepted"] else "NOT ACCEPTED"
    lines = [
        "# Goal1450 v1.5.2 Prepared Host-Output Parity",
        "",
        "## Verdict",
        "",
        verdict,
        "",
        "## Run Scope",
        "",
        f"- Primitive: `{report['primitive']}`",
        f"- Scope: `{report['run_scope']}`",
        f"- Backends: `{', '.join(report['backends'])}`",
        f"- Required backends: `{', '.join(report['required_backends']) or 'none'}`",
        f"- Case count per backend: `{report['case_count']}`",
        "",
        "## Parity Outcome",
        "",
    ]
    for backend, summary in report["backend_summary"].items():
        lines.append(
            f"- {backend}: pass={summary['pass']}, fail={summary['fail']}, skipped={summary['skipped']}"
        )
    if report["failed"]:
        lines.append(f"- Failures: `{len(report['failed'])}`")
    else:
        lines.append("- Failures: none")
    if report["skipped_required"]:
        lines.append(f"- Required backend skips: `{len(report['skipped_required'])}`")
    else:
        lines.append("- Required backend skips: none")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            report["claim_boundary"],
            "",
            "This is not a public promotion, not a performance claim, not a "
            "zero-copy claim, and not a release action.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backends", nargs="+", default=["embree", "optix"])
    parser.add_argument("--required-backends", nargs="*", default=[])
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    args = parser.parse_args(argv)

    report = run_acceptance_package(
        backends=tuple(args.backends),
        required_backends=tuple(args.required_backends),
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(_json_ready(report), indent=2, sort_keys=True), encoding="utf-8")
    args.md_out.write_text(render_markdown(report), encoding="utf-8")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
