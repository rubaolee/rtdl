#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.goal1503_v1_5_4_optix_collect_k_scaling_probe import (
    _expected_native_path,
    _run_case,
)
from scripts.goal1500_v1_5_4_optix_device_collect_k_measurement import CudaDriver


REPORT_STEM = "goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"
DEFAULT_JSONL_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.jsonl"
DEFAULT_LIBRARY_PATH = ROOT / "build" / "librtdl_optix.so"
DEFAULT_COUNTS = (4097, 65537, 131072)
STAGE_FIELDS = (
    "module_load_ms",
    "allocation_ms",
    "sort_launch_ms",
    "sort_sync_ms",
    "tile_metadata_download_ms",
    "merge_launch_ms",
    "merge_sync_ms",
    "merge_metadata_download_ms",
    "carry_copy_ms",
    "final_copy_ms",
    "total_ms",
)


def _run_command(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        return {"command": command, "returncode": 127, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _git_head() -> str:
    result = _run_command(["git", "rev-parse", "HEAD"])
    return result["stdout"] if result["returncode"] == 0 else "unknown"


def _load_profile_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "record_count": len(records),
        "stage_median_ms": {
            field: _median([float(record[field]) for record in records])
            for field in STAGE_FIELDS
        },
        "stage_min_ms": {
            field: min(float(record[field]) for record in records) if records else 0.0
            for field in STAGE_FIELDS
        },
        "stage_max_ms": {
            field: max(float(record[field]) for record in records) if records else 0.0
            for field in STAGE_FIELDS
        },
        "topology": {
            "native_path": records[-1]["native_path"] if records else "unknown",
            "tile_count": int(records[-1]["tile_count"]) if records else 0,
            "merge_levels": int(records[-1]["merge_levels"]) if records else 0,
            "sort_launches": int(records[-1]["sort_launches"]) if records else 0,
            "merge_launches": int(records[-1]["merge_launches"]) if records else 0,
            "carry_copies": int(records[-1]["carry_copies"]) if records else 0,
            "final_copies": int(records[-1]["final_copies"]) if records else 0,
            "metadata_fields_downloaded": int(records[-1]["metadata_fields_downloaded"]) if records else 0,
        },
    }


def expected_topology(candidate_count: int, row_width: int) -> dict[str, Any]:
    expected_path = _expected_native_path(candidate_count, row_width)
    if expected_path == "row_width2_parallel_bitonic_sort":
        return {
            "native_path": expected_path,
            "tile_count": 0,
            "merge_levels": 0,
            "sort_launches": 1,
            "merge_launches": 0,
            "carry_copies": 0,
            "final_copies": 0,
            "metadata_fields_downloaded": 2,
        }
    if expected_path != "row_width2_bounded_multi_tile_sort_merge":
        return {
            "native_path": expected_path,
            "tile_count": 0,
            "merge_levels": 0,
            "sort_launches": 1,
            "merge_launches": 0,
            "carry_copies": 0,
            "final_copies": 0,
            "metadata_fields_downloaded": 2,
        }

    tile_size = 2048 if os.environ.get("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT") else 4096
    tile_count = (candidate_count + tile_size - 1) // tile_size
    current_segments = tile_count
    segment_capacity = tile_size
    merge_levels = 0
    merge_launches = 0
    carry_copies = 0
    metadata_fields_downloaded = tile_count * 2
    while current_segments > 1:
        pair_count = current_segments // 2
        has_carry = (current_segments % 2) != 0
        output_segment_capacity = segment_capacity * 2
        merge_levels += 1
        if (
            os.environ.get("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT")
            and output_segment_capacity >= 65536
        ):
            merge_launches += pair_count * 3
            metadata_fields_downloaded += pair_count
        else:
            merge_launches += 1
            metadata_fields_downloaded += pair_count * 2
        if has_carry:
            carry_copies += 1
        current_segments = pair_count + (1 if has_carry else 0)
        segment_capacity = output_segment_capacity
    return {
        "native_path": expected_path,
        "tile_count": tile_count,
        "merge_levels": merge_levels,
        "sort_launches": tile_count,
        "merge_launches": merge_launches,
        "carry_copies": carry_copies,
        "final_copies": 0 if (
            os.environ.get("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT")
            and segment_capacity >= 65536
        ) else 1,
        "metadata_fields_downloaded": metadata_fields_downloaded,
    }


def _run_profile_case(cuda: CudaDriver, *, candidate_count: int, repeats: int, profile_path: Path) -> dict[str, Any]:
    before_records = len(_load_profile_records(profile_path))
    timing_case = _run_case(cuda, candidate_count=candidate_count, row_width=2, repeats=repeats)
    after_records = _load_profile_records(profile_path)
    new_records = after_records[before_records:]
    steady_state_records = new_records[-repeats:]
    expected_path = _expected_native_path(candidate_count, 2)
    expected_profile_topology = expected_topology(candidate_count, 2)
    stage_profile = _summarize_records(steady_state_records)
    observed_topology = stage_profile["topology"]
    return {
        **timing_case,
        "expected_profile_records": repeats + 1,
        "observed_profile_records": len(new_records),
        "steady_state_profile_records": steady_state_records,
        "stage_profile": stage_profile,
        "expected_profile_topology": expected_profile_topology,
        "profile_topology_matches_expected": observed_topology == expected_profile_topology,
        "profile_native_path_matches_expected": all(
            record.get("native_path") == expected_path for record in steady_state_records
        ),
    }


def run_probe(
    library_path: Path,
    repeats: int,
    counts: tuple[int, ...],
    profile_jsonl: Path,
    *,
    allow_local_fallback_smoke: bool = False,
) -> dict[str, Any]:
    os.environ["RTDL_OPTIX_LIB"] = str(library_path)
    cuda = CudaDriver()
    try:
        profile_path = profile_jsonl
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_path.write_text("", encoding="utf-8")
        os.environ["RTDL_OPTIX_COLLECT_K_PROFILE_JSONL"] = str(profile_path)

        cases = [
            _run_profile_case(cuda, candidate_count=count, repeats=repeats, profile_path=profile_path)
            for count in counts
        ]
        all_profile_paths_match_expected = all(
            case["profile_native_path_matches_expected"] for case in cases
        )
        all_profile_topologies_match_expected = all(
            case["profile_topology_matches_expected"] for case in cases
        )
        all_parity_passed = all(
            case["same_candidate_rows"] and case["same_valid_count"] and case["same_overflowed_flag"]
            for case in cases
        )
        all_profile_records_present = all(
            case["observed_profile_records"] == case["expected_profile_records"] for case in cases
        )
        accepted_goal1506_evidence = (
            all_parity_passed
            and all_profile_records_present
            and all_profile_paths_match_expected
            and all_profile_topologies_match_expected
        )
        return {
            "goal": "Goal1506",
            "status": "goal1506_optix_collect_k_stage_profile_probe_recorded",
            "accepted_goal1506_evidence": accepted_goal1506_evidence,
            "local_fallback_smoke_only": (
                allow_local_fallback_smoke
                and not accepted_goal1506_evidence
            ),
            "git_commit": _git_head(),
            "platform": platform.platform(),
            "device_name": cuda.device_name(),
            "cuda_driver_version": cuda.driver_version(),
            "library_path": str(library_path),
            "profile_jsonl_path": str(profile_path),
            "measured_on_real_nvidia": True,
            "python_entry_point": "scripts.goal1506_v1_5_4_optix_collect_k_stage_profile_probe",
            "native_profile_env": "RTDL_OPTIX_COLLECT_K_PROFILE_JSONL",
            "timing_scope": (
                "Python wrapper call around native OptiX/CUDA device-pointer execution, "
                "plus opt-in native host-side stage timing emitted by the same native call."
            ),
            "cases": cases,
            "all_parity_passed": all_parity_passed,
            "all_profile_records_present": all_profile_records_present,
            "all_profile_paths_match_expected": all_profile_paths_match_expected,
            "all_profile_topologies_match_expected": all_profile_topologies_match_expected,
            "claim_flags": {
                "true_zero_copy_authorized": False,
                "public_speedup_wording_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "stable_public_primitive_authorized": False,
                "partner_tensor_handoff_authorized": False,
                "release_action_authorized": False,
            },
            "claim_boundary": (
                "Goal1506 records opt-in host-side stage timing for the experimental "
                "Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not "
                "authorize public speedup wording, true zero-copy wording, whole-app "
                "claims, partner tensor handoff, stable primitive promotion, or release action."
            ),
        }
    finally:
        os.environ.pop("RTDL_OPTIX_COLLECT_K_PROFILE_JSONL", None)
        cuda.close()


def validate_probe(probe: dict[str, Any], *, allow_local_fallback_smoke: bool = False) -> dict[str, Any]:
    if probe.get("goal") != "Goal1506":
        raise ValueError("invalid Goal1506 report goal")
    if probe.get("measured_on_real_nvidia") is not True:
        raise ValueError("Goal1506 must be measured on real NVIDIA hardware")
    if probe.get("all_parity_passed") is not True:
        raise ValueError("Goal1506 requires parity for every timing case")
    if probe.get("all_profile_records_present") is not True:
        raise ValueError("Goal1506 requires every profiled call record")
    if probe.get("all_profile_paths_match_expected") is not True and not allow_local_fallback_smoke:
        raise ValueError("Goal1506 native path records must match expected paths")
    if probe.get("all_profile_topologies_match_expected") is not True and not allow_local_fallback_smoke:
        raise ValueError("Goal1506 native topology records must match expected topology")
    expected_accepted = (
        probe.get("all_parity_passed") is True
        and probe.get("all_profile_records_present") is True
        and probe.get("all_profile_paths_match_expected") is True
        and probe.get("all_profile_topologies_match_expected") is True
    )
    if probe.get("accepted_goal1506_evidence") is not expected_accepted:
        raise ValueError("Goal1506 accepted evidence flag must match core gates")
    if allow_local_fallback_smoke and probe.get("accepted_goal1506_evidence") is not True:
        if probe.get("local_fallback_smoke_only") is not True:
            raise ValueError("Goal1506 fallback smoke must be explicitly classified as smoke only")
    if not allow_local_fallback_smoke and probe.get("local_fallback_smoke_only") is not False:
        raise ValueError("Goal1506 local fallback smoke flag requires explicit smoke mode")
    for case in probe.get("cases", []):
        if case.get("row_width") != 2:
            raise ValueError("Goal1506 currently profiles row_width=2 only")
        if case.get("expected_profile_records") != case.get("observed_profile_records"):
            raise ValueError("Goal1506 missing native profile records")
        profile = case.get("stage_profile", {})
        if profile.get("record_count", 0) <= 0:
            raise ValueError("Goal1506 requires steady-state stage profile records")
        topology = profile.get("topology", {})
        expected = case.get("expected_profile_topology", {})
        if topology.get("native_path") != case.get("expected_native_path") and not allow_local_fallback_smoke:
            raise ValueError("Goal1506 profile topology native path mismatch")
        if topology != expected and not allow_local_fallback_smoke:
            raise ValueError("Goal1506 profile topology mismatch")
        for field, value in profile.get("stage_median_ms", {}).items():
            if float(value) < 0.0:
                raise ValueError(f"Goal1506 stage median must be non-negative: {field}")
    for flag, value in probe.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1506 must keep {flag}=False")
    return probe


def to_markdown(probe: dict[str, Any]) -> str:
    lines = [
        "# Goal 1506: OptiX COLLECT_K_BOUNDED Stage Profile Probe",
        "",
        "## Verdict",
        "",
        f"`{probe['status']}`",
        "",
        "## Scope",
        "",
        f"- Device: `{probe['device_name']}`",
        f"- Git commit: `{probe['git_commit']}`",
        f"- Native profile env: `{probe['native_profile_env']}`",
        f"- Accepted Goal1506 evidence: `{probe.get('accepted_goal1506_evidence')}`",
        f"- Local fallback smoke only: `{probe.get('local_fallback_smoke_only')}`",
        f"- Timing scope: {probe['timing_scope']}",
        "",
        "## Cases",
        "",
    ]
    for case in probe["cases"]:
        topology = case["stage_profile"]["topology"]
        medians = case["stage_profile"]["stage_median_ms"]
        lines.append(
            "- candidates=`{candidate_count}`, path=`{expected_native_path}`, total_ms=`{total_ms:.6f}`, "
            "sort_sync_ms=`{sort_sync_ms:.6f}`, merge_sync_ms=`{merge_sync_ms:.6f}`, "
            "metadata_ms=`{metadata_ms:.6f}`, sort_launches=`{sort_launches}`, "
            "merge_launches=`{merge_launches}`, carry_copies=`{carry_copies}`".format(
                candidate_count=case["candidate_count"],
                expected_native_path=case["expected_native_path"],
                total_ms=medians["total_ms"],
                sort_sync_ms=medians["sort_sync_ms"],
                merge_sync_ms=medians["merge_sync_ms"],
                metadata_ms=medians["tile_metadata_download_ms"] + medians["merge_metadata_download_ms"],
                sort_launches=topology["sort_launches"],
                merge_launches=topology["merge_launches"],
                carry_copies=topology["carry_copies"],
            )
        )
    lines.extend(["", "## Claim Boundary", "", probe["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run opt-in native stage profiling for OptiX collect-k.")
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY_PATH)
    parser.add_argument("--counts", nargs="+", type=int, default=list(DEFAULT_COUNTS))
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--profile-jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument(
        "--allow-local-fallback-smoke",
        action="store_true",
        help=(
            "Allow local runtime smoke artifacts when the GPU falls back from the expected "
            "tiled path. These artifacts are explicitly not accepted Goal1506 evidence."
        ),
    )
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    probe = validate_probe(
        run_probe(
            args.library,
            args.repeats,
            tuple(args.counts),
            args.profile_jsonl,
            allow_local_fallback_smoke=args.allow_local_fallback_smoke,
        ),
        allow_local_fallback_smoke=args.allow_local_fallback_smoke,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(probe, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(probe), encoding="utf-8")
    print(json.dumps({"status": probe["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
