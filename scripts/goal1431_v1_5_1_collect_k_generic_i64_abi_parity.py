from __future__ import annotations

import argparse
import ctypes
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_STEM = "goal1431_v1_5_1_collect_k_generic_i64_abi_parity_2026-05-06"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


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


def _load_symbol(backend: str, library_path: Path):
    lib = ctypes.CDLL(str(library_path))
    symbol = f"rtdl_{backend}_collect_k_bounded_i64"
    fn = getattr(lib, symbol)
    fn.argtypes = [
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    fn.restype = ctypes.c_int
    return symbol, fn


def _call(
    fn,
    candidate_rows: tuple[tuple[int, int], ...],
    *,
    row_capacity: int,
) -> dict[str, Any]:
    flat = [value for row in candidate_rows for value in row]
    input_array = (ctypes.c_int64 * len(flat))(*flat)
    output_len = max(row_capacity * 2, 1)
    output_array = (ctypes.c_int64 * output_len)()
    emitted = ctypes.c_size_t()
    overflowed = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)
    status = fn(
        input_array,
        len(candidate_rows),
        2,
        output_array if row_capacity else None,
        row_capacity,
        ctypes.byref(emitted),
        ctypes.byref(overflowed),
        error,
        len(error),
    )
    return {
        "status": int(status),
        "emitted_count": int(emitted.value),
        "overflowed": int(overflowed.value),
        "rows_flat": [int(output_array[index]) for index in range(output_len)],
        "error": error.value.decode("utf-8", errors="replace"),
    }


def run_package(backend: str, library_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    symbol, fn = _load_symbol(backend, library_path)
    cases: list[dict[str, Any]] = []

    success = _call(
        fn,
        ((2, 20), (1, 10), (2, 20)),
        row_capacity=2,
    )
    cases.append(
        {
            "case": "deduplicate_and_canonicalize_exact_fit",
            "expected": {
                "status": 0,
                "emitted_count": 2,
                "overflowed": 0,
                "rows_flat_prefix": [1, 10, 2, 20],
                "error": "",
            },
            "observed": success,
            "pass": (
                success["status"] == 0
                and success["emitted_count"] == 2
                and success["overflowed"] == 0
                and success["rows_flat"][:4] == [1, 10, 2, 20]
                and success["error"] == ""
            ),
        }
    )

    overflow = _call(
        fn,
        ((2, 20), (1, 10), (2, 20)),
        row_capacity=1,
    )
    cases.append(
        {
            "case": "fail_closed_overflow_no_partial_rows",
            "expected": {
                "status": 0,
                "emitted_count": 2,
                "overflowed": 1,
                "rows_flat_prefix": [0, 0],
                "error": "",
            },
            "observed": overflow,
            "pass": (
                overflow["status"] == 0
                and overflow["emitted_count"] == 2
                and overflow["overflowed"] == 1
                and overflow["rows_flat"][:2] == [0, 0]
                and overflow["error"] == ""
            ),
        }
    )

    accepted = all(case["pass"] for case in cases)
    return {
        "artifact": REPORT_STEM,
        "status": "accepted" if accepted else "not_accepted",
        "accepted": accepted,
        "backend": backend,
        "library_path": str(library_path),
        "symbol": symbol,
        "environment": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "git_head": _git_head(),
        },
        "run_scope": {
            "row_width": 2,
            "cases": [case["case"] for case in cases],
            "capacity_policy": "exact fit plus fail-closed overflow",
        },
        "case_results": cases,
        "failures": [case["case"] for case in cases if not case["pass"]],
        "elapsed_sec": time.perf_counter() - started,
        "claim_boundary": (
            "Generic i64 COLLECT_K_BOUNDED ABI parity only; not stable primitive "
            "promotion, not speedup wording, not zero-copy wording, not whole-app "
            "behavior, and not release action."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Goal 1431 v1.5.1 COLLECT_K_BOUNDED Generic I64 ABI Parity",
        "",
        "## Verdict",
        "",
        "ACCEPTED." if report["accepted"] else "NOT ACCEPTED.",
        "",
        str(report["claim_boundary"]),
        "",
        "## Run Scope",
        "",
        f"- Backend: {report['backend']}",
        f"- Library: `{report['library_path']}`",
        f"- Symbol: `{report['symbol']}`",
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
    for case in report["case_results"]:
        observed = case["observed"]
        lines.append(
            f"- {case['case']}: {'pass' if case['pass'] else 'fail'} "
            f"(status={observed['status']}, emitted={observed['emitted_count']}, "
            f"overflowed={observed['overflowed']}, rows={observed['rows_flat']})"
        )
    lines.append(f"- Failures: {', '.join(report['failures']) if report['failures'] else 'none'}")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("embree", "optix"), required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_package(args.backend, args.library)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    args.markdown_out.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "json": str(args.json_out), "markdown": str(args.markdown_out)}))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
