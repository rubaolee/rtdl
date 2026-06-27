#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REQUIRED_AUTHOR_SYMBOLS = (
    "rtdl_optix_prepare_rt_barneshut_author_3d",
    "rtdl_optix_run_rt_barneshut_author_3d",
    "rtdl_optix_destroy_rt_barneshut_author_3d",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _run_text(cmd: tuple[str, ...]) -> str:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return (proc.stdout or "") + "\n" + (proc.stderr or "")


def _candidate_libraries(root: Path) -> tuple[Path, ...]:
    build = root / "build"
    if not build.exists():
        return ()
    return tuple(sorted(build.glob("librtdl_optix*.so")))


def _exported_symbols(root: Path) -> dict[str, bool]:
    haystack = ""
    for lib in _candidate_libraries(root):
        haystack += _run_text(("nm", "-D", str(lib)))
    return {symbol: symbol in haystack for symbol in REQUIRED_AUTHOR_SYMBOLS}


def _source_contains(root: Path, needle: str) -> bool:
    for subdir in ("src", "scripts", "tests"):
        base = root / subdir
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py", ".cpp", ".h", ".hpp", ".cu", ".md"}:
                continue
            try:
                if needle in path.read_text(encoding="utf-8", errors="replace"):
                    return True
            except OSError:
                continue
    return False


def _inspect_version(name: str, root: Path) -> dict[str, Any]:
    symbols = _exported_symbols(root)
    source_symbols = {symbol: _source_contains(root, symbol) for symbol in REQUIRED_AUTHOR_SYMBOLS}
    has_required_symbols = all(symbols[symbol] or source_symbols[symbol] for symbol in REQUIRED_AUTHOR_SYMBOLS)
    has_contract_module = (root / "src" / "rtdsl" / "rt_barneshut_author_contract.py").exists()
    has_native_route_module = (root / "src" / "rtdsl" / "v4_rt_barneshut_native_route.py").exists()
    has_author_route_text = _source_contains(root, "rt_barneshut_author")
    has_legacy_barnes = (root / "src" / "rtdsl" / "app_adapters" / "barnes_hut.py").exists()

    if has_required_symbols and has_contract_module and has_native_route_module:
        status = "same_semantics_native_rt_core_route_present"
        comparable = True
        blocker = ""
    else:
        status = "no_same_semantics_author_route"
        comparable = False
        blocker = (
            "This version has Barnes-Hut-style routes or scripts, but not the "
            "Goal4760 author-semantics contract plus native 3D author ABI. "
            "Do not divide its historical Barnes-Hut timings by the authors' "
            "RT-BarnesHut program."
        )

    return {
        "version": name,
        "root": str(root),
        "same_semantics_author_route_available": comparable,
        "status": status,
        "required_native_author_symbols": symbols,
        "required_native_author_symbols_in_source": source_symbols,
        "has_author_contract_module": has_contract_module,
        "has_native_route_module": has_native_route_module,
        "has_rt_barneshut_author_text": has_author_route_text,
        "has_legacy_barnes_hut_adapter": has_legacy_barnes,
        "ratio_to_author_allowed": comparable,
        "ratio_blocker": blocker,
    }


def _parse_author_phase_stdout(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = {
        "sort": r"Sort Time:\s*([0-9.]+)",
        "tree_build": r"Tree build time:\s*([0-9.]+)",
        "tree_to_dfs": r"Tree to DFS time:\s*([0-9.]+)",
        "install_autoropes": r"Install AutoRopes time:\s*([0-9.]+)",
        "intersections_setup": r"Intersections setup time:\s*([0-9.]+)",
        "rt_force": r"RT Cores Force Calculations time:\s*([0-9.]+)",
        "iterative_step": r"Iterative Step time:\s*([0-9.]+)",
        "total_program": r"Total Program time:\s*([0-9.]+)",
    }
    result: dict[str, float] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            result[key] = float(match.group(1))
    return result


def _warm_v4_row(v4_json: dict[str, Any]) -> dict[str, Any]:
    runs = v4_json["native_runs"]
    if len(runs) < 2:
        raise ValueError("V4 evidence must have at least one warm native run")
    return runs[-1]


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    author_phase = _parse_author_phase_stdout(args.author_phase_stdout)
    v4_json = _read_json(args.v4_benchmark_json)
    profile_rows = _read_jsonl(args.v4_profile_jsonl)
    warm_profile = profile_rows[-1]
    warm_v4 = _warm_v4_row(v4_json)
    warm_phase = warm_v4["phase_seconds"]
    input_download = float(warm_profile.get("input_download_seconds", 0.0))
    v4_internal_program = float(warm_phase["execution_seconds"]) + input_download

    version_rows = [
        {
            "version": "author",
            "root": str(args.author_root),
            "same_semantics_author_route_available": True,
            "status": "reference_author_binary_full_phase",
            "ratio_to_author_allowed": False,
            "ratio_blocker": "Reference denominator, not compared to itself.",
            "phase_seconds": author_phase,
        },
        _inspect_version("v2_14", args.v2_root),
        _inspect_version("v3_0_2", args.v3_root),
        {
            **_inspect_version("v4_0", args.v4_root),
            "phase_seconds": {
                "sort": float(warm_profile["sort_seconds"]),
                "preprocessing": float(warm_phase["preprocessing_seconds"]),
                "rt_force": float(warm_phase["rt_force_seconds"]),
                "execution": float(warm_phase["execution_seconds"]),
                "input_download": input_download,
                "internal_program_including_input_download": v4_internal_program,
            },
            "checksum": {
                "native_force_checksum": float(warm_v4["force_checksum"]),
                "author_rt_force_checksum": float(
                    v4_json["author_binary"]["checksum_validation_against_native_warm_last"][
                        "author_rt_force_checksum"
                    ]
                ),
                "relative_error": float(
                    v4_json["author_binary"]["checksum_validation_against_native_warm_last"][
                        "checksum_relative_error"
                    ]
                ),
                "passes_tolerance": bool(
                    v4_json["author_binary"]["checksum_validation_against_native_warm_last"][
                        "passes_float_output_tolerance"
                    ]
                ),
            },
        },
    ]

    fair_ratios = {
        "v4_author_total_program_over_v4_internal_program": author_phase["total_program"]
        / v4_internal_program,
        "v4_author_rt_force_over_v4_rt_force": author_phase["rt_force"]
        / float(warm_phase["rt_force_seconds"]),
        "v4_author_sort_over_v4_sort": author_phase["sort"] / float(warm_profile["sort_seconds"]),
        "v4_author_sort_tree_over_v4_preprocessing": (
            author_phase["sort"] + author_phase["tree_build"]
        )
        / float(warm_phase["preprocessing_seconds"]),
    }

    return {
        "goal": args.goal_label,
        "schema": "rtdl.v4.goal4772.rt_barneshut_four_way_fair_compare.v1",
        "status": "four_way_protocol_complete_with_absent_v2_v3_author_routes",
        "dataset": {
            "path": str(args.dataset),
            "point_count": int(v4_json["dataset"]["point_count"]),
            "file_type": v4_json["dataset"]["file_type"],
            "same_input_for_author_and_v4": True,
            "v2_v3_same_input_not_run_because_same_semantics_route_absent": True,
        },
        "contract": {
            "name": "RT-BarnesHut author-semantics contract",
            "theta": 0.5,
            "bucket_size": 32,
            "requires_3d_author_z_order_tree": True,
            "requires_author_force_checksum": True,
            "forbids_mixing_historical_aggregate_frontier_rows": True,
        },
        "rows": version_rows,
        "fair_ratios": fair_ratios,
        "comparison_policy": {
            "author_vs_v4_allowed": True,
            "author_vs_v2_14_allowed": False,
            "author_vs_v3_0_2_allowed": False,
            "reason": (
                "V2.14 and V3.0.2 do not expose the Goal4760 author-semantics "
                "contract or native 3D author ABI. Their historical Barnes-Hut "
                "routes are different RTDL benchmark contracts."
            ),
            "no_na_policy": "Absent routes are explicit capability verdicts, not n/a.",
        },
        "claim_boundary": {
            "public_v4_tag_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "v2_v3_v4_public_speed_table_authorized": False,
            "no_copy_tree_build_claim_authorized": False,
            "broad_v4_speedup_claim_authorized": False,
        },
        "evidence": {
            "author_phase_stdout": str(args.author_phase_stdout),
            "v4_benchmark_json": str(args.v4_benchmark_json),
            "v4_profile_jsonl": str(args.v4_profile_jsonl),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal4772 RT-BarnesHut four-way fair comparison.")
    parser.add_argument("--goal-label", default="Goal4772")
    parser.add_argument("--author-root", required=True, type=Path)
    parser.add_argument("--v2-root", required=True, type=Path)
    parser.add_argument("--v3-root", required=True, type=Path)
    parser.add_argument("--v4-root", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--author-phase-stdout", required=True, type=Path)
    parser.add_argument("--v4-benchmark-json", required=True, type=Path)
    parser.add_argument("--v4-profile-jsonl", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    payload = build_payload(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
