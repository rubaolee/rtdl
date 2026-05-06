from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


REPORT_STEM = "goal1416_v1_5_1_collect_k_native_parity_2026-05-06"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


@dataclass(frozen=True)
class ParityCase:
    name: str
    left: tuple[rt.Polygon, ...]
    right: tuple[rt.Polygon, ...]
    capacity: int
    expect_overflow: bool


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


def build_parity_cases() -> tuple[ParityCase, ...]:
    """Return unambiguous polygon cases for bounded native candidate parity."""
    left = (
        _rect(1, 0.0, 0.0, 3.0, 3.0),
        _rect(2, 10.0, 0.0, 14.0, 4.0),
    )
    right = (
        _rect(10, 1.0, 1.0, 4.0, 4.0),
        _rect(11, 11.0, 1.0, 13.0, 3.0),
        _rect(12, 20.0, 20.0, 21.0, 21.0),
    )
    empty_left = (_rect(101, 0.0, 0.0, 1.0, 1.0),)
    empty_right = (_rect(110, 5.0, 5.0, 6.0, 6.0),)
    return (
        ParityCase(
            name="empty_zero_capacity",
            left=empty_left,
            right=empty_right,
            capacity=0,
            expect_overflow=False,
        ),
        ParityCase(
            name="exact_fit_two_rows",
            left=left,
            right=right,
            capacity=2,
            expect_overflow=False,
        ),
        ParityCase(
            name="one_short_fail_closed_overflow",
            left=left,
            right=right,
            capacity=1,
            expect_overflow=True,
        ),
        ParityCase(
            name="zero_capacity_positive_fail_closed_overflow",
            left=left,
            right=right,
            capacity=0,
            expect_overflow=True,
        ),
    )


def expected_candidate_rows(case: ParityCase) -> tuple[tuple[int, int], ...]:
    rows = rt.polygon_pair_overlap_area_rows_cpu(case.left, case.right)
    return tuple(
        sorted(
            (
                int(row["left_polygon_id"]),
                int(row["right_polygon_id"]),
            )
            for row in rows
        )
    )


def run_reference_case(case: ParityCase) -> dict[str, object]:
    started = time.perf_counter()
    rows = expected_candidate_rows(case)
    try:
        row_buffer = rt.collect_k_bounded_rows(rows, k=case.capacity, row_width=2)
    except RuntimeError as exc:
        if not case.expect_overflow or "fail_closed_overflow" not in str(exc):
            return {
                "status": "fail",
                "expected_rows": rows,
                "capacity": case.capacity,
                "expect_overflow": case.expect_overflow,
                "error": str(exc),
                "elapsed_sec": time.perf_counter() - started,
            }
        return {
            "status": "pass",
            "expected_rows": rows,
            "capacity": case.capacity,
            "expect_overflow": True,
            "observed_overflow": True,
            "elapsed_sec": time.perf_counter() - started,
        }
    except Exception as exc:  # pragma: no cover - defensive report boundary
        return {
            "status": "fail",
            "expected_rows": rows,
            "capacity": case.capacity,
            "expect_overflow": case.expect_overflow,
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_sec": time.perf_counter() - started,
        }
    if case.expect_overflow:
        return {
            "status": "fail",
            "expected_rows": rows,
            "capacity": case.capacity,
            "expect_overflow": True,
            "error": "reference returned a partial/success result where overflow was expected",
            "elapsed_sec": time.perf_counter() - started,
        }
    return {
        "status": "pass",
        "expected_rows": row_buffer["candidate_id_rows"],
        "capacity": case.capacity,
        "expect_overflow": False,
        "valid_count": row_buffer["valid_count"],
        "elapsed_sec": time.perf_counter() - started,
    }


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
    return isinstance(exc, (OSError, ImportError, ValueError)) or any(
        fragment in message for fragment in unavailable_fragments
    )


def run_backend_case(
    backend: str,
    runner: BackendRunner,
    case: ParityCase,
    expected_rows: tuple[tuple[int, int], ...],
) -> dict[str, object]:
    started = time.perf_counter()
    try:
        result = runner(case.left, case.right, case.capacity)
    except RuntimeError as exc:
        if case.expect_overflow and "fail_closed_overflow" in str(exc):
            return {
                "status": "pass",
                "expected_rows": expected_rows,
                "capacity": case.capacity,
                "expect_overflow": True,
                "observed_overflow": True,
                "elapsed_sec": time.perf_counter() - started,
            }
        return {
            "status": "fail",
            "expected_rows": expected_rows,
            "capacity": case.capacity,
            "expect_overflow": case.expect_overflow,
            "error": str(exc),
            "elapsed_sec": time.perf_counter() - started,
        }
    except Exception as exc:
        if _is_backend_unavailable(exc):
            return {
                "status": "skipped",
                "expected_rows": expected_rows,
                "capacity": case.capacity,
                "expect_overflow": case.expect_overflow,
                "reason": f"{type(exc).__name__}: {exc}",
                "elapsed_sec": time.perf_counter() - started,
            }
        return {
            "status": "fail",
            "expected_rows": expected_rows,
            "capacity": case.capacity,
            "expect_overflow": case.expect_overflow,
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_sec": time.perf_counter() - started,
        }
    if case.expect_overflow:
        return {
            "status": "fail",
            "expected_rows": expected_rows,
            "capacity": case.capacity,
            "expect_overflow": True,
            "error": "backend returned success where fail-closed overflow was expected",
            "elapsed_sec": time.perf_counter() - started,
        }
    observed_rows = tuple(tuple(int(value) for value in row) for row in result["candidate_id_rows"])
    mismatches: list[str] = []
    if observed_rows != expected_rows:
        mismatches.append(f"candidate_id_rows mismatch: expected {expected_rows}, got {observed_rows}")
    if result.get("backend") != backend:
        mismatches.append(f"backend metadata mismatch: expected {backend}, got {result.get('backend')}")
    if int(result.get("capacity", -1)) != case.capacity:
        mismatches.append(f"capacity mismatch: expected {case.capacity}, got {result.get('capacity')}")
    if int(result.get("valid_count", -1)) != len(expected_rows):
        mismatches.append(f"valid_count mismatch: expected {len(expected_rows)}, got {result.get('valid_count')}")
    if result.get("overflowed") is not False:
        mismatches.append("overflowed metadata must be False for non-overflow success")
    if result.get("complete_candidate_coverage") is not True:
        mismatches.append("complete_candidate_coverage must be True")
    return {
        "status": "fail" if mismatches else "pass",
        "expected_rows": expected_rows,
        "observed_rows": observed_rows,
        "capacity": case.capacity,
        "expect_overflow": False,
        "valid_count": result.get("valid_count"),
        "mismatches": mismatches,
        "elapsed_sec": time.perf_counter() - started,
    }


def default_backend_runners() -> dict[str, BackendRunner]:
    return {
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


def run_acceptance_package(
    *,
    backends: tuple[str, ...] = ("embree", "optix"),
    required_backends: tuple[str, ...] = (),
    backend_runners: dict[str, BackendRunner] | None = None,
) -> dict[str, object]:
    started = time.perf_counter()
    runners = default_backend_runners()
    if backend_runners:
        runners.update(backend_runners)
    cases = build_parity_cases()
    case_results: list[dict[str, object]] = []
    for case in cases:
        reference = run_reference_case(case)
        backend_results: dict[str, object] = {}
        expected_rows = tuple(reference["expected_rows"])
        for backend in backends:
            backend_results[backend] = run_backend_case(
                backend,
                runners[backend],
                case,
                expected_rows,
            )
        case_results.append(
            {
                "case": case.name,
                "reference": reference,
                "backends": backend_results,
            }
        )

    failures: list[str] = []
    skipped_required: list[str] = []
    backend_summary: dict[str, dict[str, int]] = {
        backend: {"pass": 0, "fail": 0, "skipped": 0} for backend in backends
    }
    for result in case_results:
        if result["reference"]["status"] != "pass":
            failures.append(f"{result['case']}: reference {result['reference']['status']}")
        for backend, backend_result in result["backends"].items():
            status = str(backend_result["status"])
            backend_summary[backend][status] += 1
            if status == "fail":
                failures.append(f"{result['case']}: {backend} failed")
            if status == "skipped" and backend in required_backends:
                skipped_required.append(f"{result['case']}: {backend} skipped")

    accepted = not failures and not skipped_required
    return {
        "artifact": REPORT_STEM,
        "status": "accepted" if accepted else "not_accepted",
        "accepted": accepted,
        "environment": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "git_head": _git_head(),
        },
        "claim_boundary": (
            "Same-contract COLLECT_K_BOUNDED native candidate-row parity only; "
            "not a public primitive promotion, not a performance claim, and not a zero-copy claim."
        ),
        "run_scope": {
            "cases": [case.name for case in cases],
            "backends": backends,
            "required_backends": required_backends,
            "row_width": 2,
            "capacity_policy": "exact fit plus fail-closed overflow probes",
        },
        "backend_summary": backend_summary,
        "failures": failures,
        "skipped_required": skipped_required,
        "case_results": case_results,
        "elapsed_sec": time.perf_counter() - started,
    }


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


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Goal 1416 v1.5.1 COLLECT_K_BOUNDED Native Parity",
        "",
        "## Verdict",
        "",
        (
            "ACCEPTED for this measured package."
            if report["accepted"]
            else "NOT ACCEPTED for this measured package."
        ),
        "",
        str(report["claim_boundary"]),
        "",
        "## Run Scope",
        "",
        f"- Cases: {', '.join(report['run_scope']['cases'])}",
        f"- Backends requested: {', '.join(report['run_scope']['backends'])}",
        f"- Required backends: {', '.join(report['run_scope']['required_backends']) or 'none'}",
        f"- Row width: {report['run_scope']['row_width']}",
        f"- Capacity policy: {report['run_scope']['capacity_policy']}",
        f"- Platform: {report['environment']['platform']}",
        f"- Python: {report['environment']['python']}",
        f"- Git HEAD: {report['environment']['git_head']}",
        f"- Elapsed seconds: {report['elapsed_sec']:.6f}",
        "",
        "## Parity Outcome",
        "",
    ]
    for backend, summary in report["backend_summary"].items():
        lines.append(
            f"- {backend}: pass={summary['pass']}, fail={summary['fail']}, skipped={summary['skipped']}"
        )
    if report["failures"]:
        lines.append(f"- Failures: {'; '.join(report['failures'])}")
    else:
        lines.append("- Failures: none")
    if report["skipped_required"]:
        lines.append(f"- Required backend skips: {'; '.join(report['skipped_required'])}")
    else:
        lines.append("- Required backend skips: none")
    lines.extend(["", "## Backend Details", ""])
    for case_result in report["case_results"]:
        lines.append(f"- Case `{case_result['case']}` reference: {case_result['reference']['status']}")
        for backend, backend_result in case_result["backends"].items():
            detail = backend_result.get("error") or backend_result.get("reason") or ""
            suffix = f" ({detail})" if detail else ""
            lines.append(f"- Case `{case_result['case']}` {backend}: {backend_result['status']}{suffix}")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- JSON artifact: `docs/reports/{REPORT_STEM}.json`",
            f"- Markdown artifact: `docs/reports/{REPORT_STEM}.md`",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        action="append",
        choices=("embree", "optix"),
        help="Backend to include. May be passed more than once. Defaults to both.",
    )
    parser.add_argument(
        "--require-backend",
        action="append",
        choices=("embree", "optix"),
        default=[],
        help="Fail the package if this backend is skipped.",
    )
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backends = tuple(args.backend or ("embree", "optix"))
    report = run_acceptance_package(
        backends=backends,
        required_backends=tuple(args.require_backend),
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.markdown_out.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "json": str(args.json_out), "markdown": str(args.markdown_out)}))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
