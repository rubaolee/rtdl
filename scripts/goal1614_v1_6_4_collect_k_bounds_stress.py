#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt
from scripts import goal1467_v1_5_3_typed_host_buffer_parity as goal1467


REPORT_STEM = "goal1614_v1_6_4_collect_k_bounds_stress_2026-05-09"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"

SUPPORTED_BACKENDS = ("fake_native", "embree", "optix")
SENTINEL = -777777777


@dataclass(frozen=True)
class BoundsStressCase:
    name: str
    candidate_rows: tuple[tuple[int, ...], ...]
    capacity: int
    row_width: int
    expected_status: str
    expected_error_fragment: str = ""


class _FakeCollectKBoundedI64Symbol:
    def __call__(
        self,
        candidate_rows,
        candidate_count,
        row_width,
        rows_out,
        row_capacity,
        emitted_count_out,
        overflowed_out,
        error,
        error_size,
    ):
        width = int(row_width)
        rows = []
        for row_index in range(int(candidate_count)):
            row = tuple(int(candidate_rows[row_index * width + column]) for column in range(width))
            rows.append(row)
        canonical = tuple(sorted(set(rows)))
        ctypes.cast(emitted_count_out, ctypes.POINTER(ctypes.c_size_t))[0] = len(canonical)
        if len(canonical) > int(row_capacity):
            ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 1
            return 0
        ctypes.cast(overflowed_out, ctypes.POINTER(ctypes.c_uint32))[0] = 0
        for row_index, row in enumerate(canonical):
            for column, value in enumerate(row):
                rows_out[row_index * width + column] = int(value)
        return 0


def build_stress_cases() -> tuple[BoundsStressCase, ...]:
    return (
        BoundsStressCase("empty_zero_capacity", (), 0, 2, "pass"),
        BoundsStressCase(
            "exact_fit_unsorted_duplicates",
            ((3, 30), (1, 10), (2, 20), (1, 10)),
            3,
            2,
            "pass",
        ),
        BoundsStressCase(
            "duplicate_compression_avoids_overflow",
            ((2, 20), (2, 20), (1, 10)),
            2,
            2,
            "pass",
        ),
        BoundsStressCase(
            "k_plus_one_overflow_preserves_output",
            ((1, 10), (2, 20), (3, 30)),
            2,
            2,
            "overflow",
            "overflowed capacity",
        ),
        BoundsStressCase(
            "zero_capacity_positive_overflow",
            ((9, 90),),
            0,
            2,
            "overflow",
            "overflowed capacity",
        ),
        BoundsStressCase("row_width_one_exact", ((5,), (1,), (5,)), 2, 1, "pass"),
        BoundsStressCase("row_width_three_exact", ((0, 1, 2), (0, 1, 1)), 2, 3, "pass"),
        BoundsStressCase(
            "row_width_mismatch_rejected",
            ((1, 2, 3),),
            1,
            2,
            "value_error",
            "candidate row width mismatch",
        ),
        BoundsStressCase(
            "negative_capacity_rejected",
            (),
            -1,
            2,
            "value_error",
            "invalid dimensions",
        ),
    )


def _git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def _symbol_name(backend: str) -> str:
    if backend == "fake_native":
        return "rtdl_fake_collect_k_bounded_i64"
    return goal1467.symbol_name_for_backend(backend)


def _library(backend: str) -> Any:
    if backend == "fake_native":
        return SimpleNamespace(**{_symbol_name(backend): _FakeCollectKBoundedI64Symbol()})
    return goal1467.load_backend_library(backend)


def _descriptor(backend: str, case: BoundsStressCase) -> dict[str, Any]:
    return rt.prepare_collect_k_result_buffer_descriptor(
        capacity=case.capacity,
        row_width=case.row_width,
        backend=backend,
        device="cpu",
        owner="rtdl",
        mutability="mutable",
        copy_boundary="prepared_host_buffer_reuse",
    )


def _output_buffer(case: BoundsStressCase) -> Any:
    if case.capacity <= 0:
        return None
    length = case.capacity * case.row_width
    buffer = (ctypes.c_int64 * length)()
    for index in range(length):
        buffer[index] = SENTINEL
    return buffer


def _buffer_values(buffer: Any) -> tuple[int, ...]:
    if buffer is None:
        return ()
    return tuple(int(buffer[index]) for index in range(len(buffer)))


def _expected_rows(case: BoundsStressCase) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted(set(case.candidate_rows)))


def _backend_unavailable(exc: Exception) -> bool:
    return goal1467.is_backend_unavailable(exc)


def run_backend_case(backend: str, case: BoundsStressCase, *, library: Any | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        active_library = library if library is not None else _library(backend)
        descriptor = _descriptor(backend, case)
        output_buffer = _output_buffer(case)
        before = _buffer_values(output_buffer)
        symbol = _symbol_name(backend)
        if case.expected_status == "overflow":
            evidence = rt.validate_native_collect_k_prepared_host_output_overflow_fail_closed(
                case.candidate_rows,
                descriptor,
                output_buffer=output_buffer,
                library=active_library,
                symbol_name=symbol,
                candidate_source_symbol="goal1614_bounds_stress_rows",
                backend=backend,
            )
            after = _buffer_values(output_buffer)
            return {
                "status": "pass",
                "case": case.name,
                "backend": backend,
                "expected_status": case.expected_status,
                "capacity": case.capacity,
                "row_width": case.row_width,
                "expected_unique_count": len(_expected_rows(case)),
                "overflow_fail_closed": evidence["overflow_fail_closed_with_prepared_buffer"],
                "partial_result_returned": evidence["partial_result_returned"],
                "output_buffer_preserved": before == after,
                "elapsed_sec": time.perf_counter() - started,
            }
        envelope = rt.run_native_collect_k_bounded_rows_with_prepared_host_output_buffer(
            case.candidate_rows,
            descriptor,
            output_buffer=output_buffer,
            library=active_library,
            symbol_name=symbol,
            candidate_source_symbol="goal1614_bounds_stress_rows",
            backend=backend,
        )
        observed_rows = tuple(tuple(int(value) for value in row) for row in envelope["result"]["candidate_id_rows"])
        mismatches = []
        if case.expected_status != "pass":
            mismatches.append(f"expected {case.expected_status} but completed")
        if observed_rows != _expected_rows(case):
            mismatches.append(f"rows mismatch: expected {_expected_rows(case)}, got {observed_rows}")
        if envelope["result"]["valid_count"] != len(_expected_rows(case)):
            mismatches.append("valid_count mismatch")
        if envelope["prepared_output_buffer_reused_by_python_wrapper"] is not True:
            mismatches.append("prepared output buffer reuse flag was not true")
        return {
            "status": "fail" if mismatches else "pass",
            "case": case.name,
            "backend": backend,
            "expected_status": case.expected_status,
            "capacity": case.capacity,
            "row_width": case.row_width,
            "expected_rows": _expected_rows(case),
            "observed_rows": observed_rows,
            "valid_count": envelope["result"]["valid_count"],
            "prepared_output_buffer_reused": envelope["prepared_output_buffer_reused_by_python_wrapper"],
            "mismatches": tuple(mismatches),
            "elapsed_sec": time.perf_counter() - started,
        }
    except Exception as exc:
        if case.expected_status == "value_error" and case.expected_error_fragment in str(exc):
            return {
                "status": "pass",
                "case": case.name,
                "backend": backend,
                "expected_status": case.expected_status,
                "capacity": case.capacity,
                "row_width": case.row_width,
                "observed_error": f"{type(exc).__name__}: {exc}",
                "elapsed_sec": time.perf_counter() - started,
            }
        if _backend_unavailable(exc):
            return {
                "status": "skipped",
                "case": case.name,
                "backend": backend,
                "expected_status": case.expected_status,
                "capacity": case.capacity,
                "row_width": case.row_width,
                "reason": f"{type(exc).__name__}: {exc}",
                "elapsed_sec": time.perf_counter() - started,
            }
        return {
            "status": "fail",
            "case": case.name,
            "backend": backend,
            "expected_status": case.expected_status,
            "capacity": case.capacity,
            "row_width": case.row_width,
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_sec": time.perf_counter() - started,
        }


def run_package(
    *,
    backends: tuple[str, ...] = ("fake_native",),
    required_backends: tuple[str, ...] = ("fake_native",),
    backend_libraries: dict[str, Any] | None = None,
) -> dict[str, Any]:
    libraries = dict(backend_libraries or {})
    records = tuple(
        run_backend_case(backend, case, library=libraries.get(backend))
        for backend in backends
        for case in build_stress_cases()
    )
    failed = tuple(record for record in records if record["status"] == "fail")
    skipped_required = tuple(
        record for record in records if record["backend"] in required_backends and record["status"] == "skipped"
    )
    accepted = not failed and not skipped_required
    return {
        "goal": "Goal1614",
        "version_slot": "v1.6.4_bounds_stress_addendum",
        "status": "accepted_local_bounds_stress" if accepted else "not_accepted",
        "accepted": accepted,
        "primitive": "COLLECT_K_BOUNDED",
        "scope": "prepared_host_output_exact_bounds_stress",
        "git_commit": _git_head(),
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "backends": backends,
        "required_backends": required_backends,
        "case_count": len(build_stress_cases()),
        "records": records,
        "failed": failed,
        "skipped_required": skipped_required,
        "stable_collect_k_promotion_authorized": False,
        "public_speedup_wording_authorized": False,
        "true_zero_copy_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rtx_wording_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Goal1614 stress-tests prepared host-output COLLECT_K_BOUNDED bounds "
            "semantics. It is correctness evidence only and does not authorize "
            "stable promotion, public speedup wording, true zero-copy wording, "
            "whole-app speedup claims, broad RTX/GPU wording, release tags, or "
            "release action."
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


def validate_package(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["goal"] != "Goal1614":
        raise ValueError("Goal1614 payload must identify Goal1614")
    if payload["primitive"] != "COLLECT_K_BOUNDED":
        raise ValueError("Goal1614 must target COLLECT_K_BOUNDED")
    if payload["accepted"] is not True:
        raise ValueError("Goal1614 accepted package cannot contain failures or required skips")
    if not any(record["expected_status"] == "overflow" for record in payload["records"]):
        raise ValueError("Goal1614 must include overflow stress cases")
    for flag in (
        "stable_collect_k_promotion_authorized",
        "public_speedup_wording_authorized",
        "true_zero_copy_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "broad_rtx_wording_authorized",
        "release_action_authorized",
    ):
        if payload[flag] is not False:
            raise ValueError(f"Goal1614 must keep {flag}=False")
    boundary = payload["claim_boundary"]
    for phrase in (
        "correctness evidence only",
        "does not authorize stable promotion",
        "public speedup wording",
        "true zero-copy wording",
        "broad RTX/GPU wording",
    ):
        if phrase not in boundary:
            raise ValueError("Goal1614 claim boundary is incomplete")
    return payload


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1614 v1.6.4 COLLECT_K_BOUNDED Bounds Stress",
        "",
        "## Verdict",
        "",
        "ACCEPTED as local prepared host-output exact-bounds stress evidence."
        if payload["accepted"]
        else "NOT ACCEPTED.",
        "",
        "## Scope",
        "",
        f"- Primitive: `{payload['primitive']}`",
        f"- Scope: `{payload['scope']}`",
        f"- Backends: `{', '.join(payload['backends'])}`",
        f"- Required backends: `{', '.join(payload['required_backends'])}`",
        f"- Case count per backend: `{payload['case_count']}`",
        "- Timing is not performance evidence.",
        "",
        "## Outcome",
        "",
        "| Backend | Case | Expected | Status | Capacity | Row width |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for record in payload["records"]:
        lines.append(
            f"| `{record['backend']}` | `{record['case']}` | `{record['expected_status']}` | "
            f"`{record['status']}` | `{record['capacity']}` | `{record['row_width']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal1614 collect-k bounds stress.")
    parser.add_argument("--backends", nargs="+", default=["fake_native"])
    parser.add_argument("--required-backends", nargs="*", default=["fake_native"])
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = validate_package(
        run_package(backends=tuple(args.backends), required_backends=tuple(args.required_backends))
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "accepted": payload["accepted"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
