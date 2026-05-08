#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE_PATH = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
REPORT_STEM = "goal1494_v1_5_4_collect_k_optix_abi_classification_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _contains_all(text: str, needles: tuple[str, ...]) -> bool:
    return all(needle in text for needle in needles)


def classify_collect_k_optix_abi() -> dict[str, Any]:
    api = _read(API_PATH)
    prelude = _read(PRELUDE_PATH)
    signature_present = _contains_all(
        prelude,
        (
            "rtdl_optix_collect_k_bounded_i64",
            "const int64_t* candidate_rows",
            "int64_t* rows_out",
            "size_t* emitted_count_out",
            "uint32_t* overflowed_out",
        ),
    )
    host_vector_sort_present = _contains_all(
        api,
        (
            "std::vector<std::vector<int64_t>> rows",
            "rows.emplace_back(row, row + row_width)",
            "std::sort(rows.begin(), rows.end())",
            "std::unique(rows.begin(), rows.end())",
            "std::memcpy(",
        ),
    )
    device_pointer_markers_present = _contains_all(
        api,
        (
            "CUdeviceptr",
            "rtdl_optix_collect_k_bounded_i64",
            "cuMemcpyDtoH",
        ),
    )
    host_pointer_api = signature_present and host_vector_sort_present
    device_buffer_api = False
    accepted_for_goal1493_execution = False
    return {
        "goal": "Goal1494",
        "status": "goal1494_collect_k_optix_abi_classified_host_pointer",
        "symbol": "rtdl_optix_collect_k_bounded_i64",
        "api_path": str(API_PATH.relative_to(ROOT)),
        "prelude_path": str(PRELUDE_PATH.relative_to(ROOT)),
        "signature_present": signature_present,
        "host_vector_sort_present": host_vector_sort_present,
        "device_pointer_markers_present_in_same_symbol": device_pointer_markers_present,
        "host_pointer_api": host_pointer_api,
        "device_buffer_api": device_buffer_api,
        "accepted_for_goal1493_device_buffer_execution": accepted_for_goal1493_execution,
        "required_next_symbol_shape": {
            "candidate_rows": "CUdeviceptr_or_uint64_device_pointer",
            "rows_out": "CUdeviceptr_or_uint64_device_pointer",
            "metadata_out": "host_or_device_explicit",
            "transfer_accounting": "explicit_nonnegative_counters",
        },
        "claim_boundary": (
            "Goal1494 classifies the current OptiX COLLECT_K_BOUNDED ABI only. "
            "The existing symbol is host-pointer/native-library boundary work, "
            "not accepted Goal1493 device-buffer execution evidence. This does "
            "not run OptiX, does not prove true zero-copy, and does not authorize "
            "public speedup wording, whole-app claims, partner tensor handoff, "
            "stable primitive promotion, or release action."
        ),
    }


def validate_classification(report: dict[str, Any]) -> dict[str, Any]:
    if report.get("goal") != "Goal1494":
        raise ValueError("invalid Goal1494 report goal")
    if report.get("symbol") != "rtdl_optix_collect_k_bounded_i64":
        raise ValueError("Goal1494 must classify rtdl_optix_collect_k_bounded_i64")
    if report.get("signature_present") is not True:
        raise ValueError("Goal1494 expected OptiX collect_k symbol signature")
    if report.get("host_pointer_api") is not True:
        raise ValueError("Goal1494 expected current symbol to be host-pointer API")
    if report.get("device_buffer_api") is not False:
        raise ValueError("Goal1494 must not classify current symbol as device-buffer API")
    if report.get("accepted_for_goal1493_device_buffer_execution") is not False:
        raise ValueError("Goal1494 must block current symbol as Goal1493 device-buffer evidence")
    for phrase in (
        "host-pointer/native-library boundary",
        "not accepted Goal1493 device-buffer execution evidence",
        "does not run OptiX",
        "does not prove true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in report.get("claim_boundary", ""):
            raise ValueError("Goal1494 claim boundary is incomplete")
    return report


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Goal 1494: COLLECT_K_BOUNDED OptiX ABI Classification",
        "",
        "## Verdict",
        "",
        "`goal1494_collect_k_optix_abi_classified_host_pointer`",
        "",
        "## Finding",
        "",
        f"- Symbol: `{report['symbol']}`",
        f"- Current API class: `host_pointer_api={report['host_pointer_api']}`",
        f"- Device-buffer API class: `device_buffer_api={report['device_buffer_api']}`",
        f"- Accepted for Goal1493 device-buffer execution: `{report['accepted_for_goal1493_device_buffer_execution']}`",
        "",
        "## Required Next Symbol Shape",
        "",
        f"- Candidate rows: `{report['required_next_symbol_shape']['candidate_rows']}`",
        f"- Rows out: `{report['required_next_symbol_shape']['rows_out']}`",
        f"- Metadata out: `{report['required_next_symbol_shape']['metadata_out']}`",
        f"- Transfer accounting: `{report['required_next_symbol_shape']['transfer_accounting']}`",
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify the current OptiX collect_k ABI.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_classification(classify_collect_k_optix_abi())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
