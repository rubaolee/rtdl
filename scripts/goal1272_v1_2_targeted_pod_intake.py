#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-05"
GOAL = "Goal1272 v1.2 targeted pod artifact intake"
DEFAULT_INPUT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal1267_live_pod_2026-05-05"
    / "docs"
    / "reports"
    / "goal1267_v1_2_optix_targeted_pod_results"
)
DEFAULT_OUTPUT_JSON = ROOT / "docs/reports/goal1272_v1_2_targeted_pod_intake_2026-05-05.json"
DEFAULT_OUTPUT_MD = ROOT / "docs/reports/goal1272_v1_2_targeted_pod_intake_2026-05-05.md"


def _load_optional(input_dir: Path, name: str) -> dict[str, Any] | None:
    path = input_dir / name
    if not path.exists() or path.stat().st_size == 0:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any] | None, path: tuple[str, ...]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _float(data: dict[str, Any] | None, path: tuple[str, ...]) -> float | None:
    value = _nested(data, path)
    return float(value) if isinstance(value, (int, float)) else None


def _result0(data: dict[str, Any] | None) -> dict[str, Any] | None:
    results = data.get("results") if isinstance(data, dict) else None
    if isinstance(results, list) and results and isinstance(results[0], dict):
        return results[0]
    return None


def _ratio(embree_sec: float | None, optix_sec: float | None) -> float | None:
    if embree_sec is None or optix_sec is None or optix_sec <= 0.0:
        return None
    return embree_sec / optix_sec


def _best_ratio(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [row.get(key) for row in rows if isinstance(row.get(key), (int, float))]
    return max(values) if values else None


def _classify_speed(rows: list[dict[str, Any]], ratio_key: str = "ratio_embree_over_optix") -> str:
    best = _best_ratio(rows, ratio_key)
    if best is None:
        return "baseline_contract_incomplete"
    if best > 1.0:
        return "optix_improved"
    return "optix_still_slower_with_reason"


def _status(input_dir: Path, label: str) -> dict[str, Any] | None:
    return _load_optional(input_dir, f"{label}.status.json")


def _env_status(env: dict[str, Any] | None) -> str:
    if env is None:
        return "env_probe_missing"
    if not env.get("nvcc_exists"):
        return "env_blocked_missing_nvcc"
    if not env.get("optix_header_exists"):
        return "env_blocked_missing_optix_header"
    return "env_probe_ok"


def _build_status(input_dir: Path) -> str:
    build = _load_optional(input_dir, "make_build_optix.status.json")
    if build is None:
        return "build_status_missing"
    if build.get("exit_code") == 0:
        return "build_ok"
    return "build_failed"


def _execution_status(
    env_status: str,
    build_status: str,
    missing: list[str],
    failed_count: int,
) -> str:
    if env_status != "env_probe_ok":
        return "environment_blocked"
    if build_status != "build_ok":
        return "build_failed"
    if missing or failed_count:
        return "execution_incomplete"
    return "artifact_complete"


def _db_row(input_dir: Path, copies: int) -> dict[str, Any]:
    embree = _result0(_load_optional(input_dir, f"db_embree_sales_risk_{copies}.json"))
    optix = _result0(_load_optional(input_dir, f"db_optix_sales_risk_{copies}.json"))
    embree_sec = _float(embree, ("prepared_session_warm_query_sec", "median_sec"))
    optix_sec = _float(optix, ("prepared_session_warm_query_sec", "median_sec"))
    return {
        "copies": copies,
        "embree_status": _nested(_status(input_dir, f"db_embree_sales_risk_{copies}"), ("status",)),
        "optix_status": _nested(_status(input_dir, f"db_optix_sales_risk_{copies}"), ("status",)),
        "embree_warm_query_median_sec": embree_sec,
        "optix_warm_query_median_sec": optix_sec,
        "ratio_embree_over_optix": _ratio(embree_sec, optix_sec),
        "embree_row_materializing_ops": _nested(embree, ("db_review_observation", "row_materializing_operation_count")),
        "optix_row_materializing_ops": _nested(optix, ("db_review_observation", "row_materializing_operation_count")),
        "optix_native_counter_status": _nested(optix, ("reported_native_db_phase_totals_sec", "counter_status")),
        "optix_native_traversal_sec": _float(optix, ("reported_native_db_phase_totals_sec", "traversal_sec")),
        "optix_native_bitset_copyback_sec": _float(optix, ("reported_native_db_phase_totals_sec", "bitset_copyback_sec")),
        "optix_native_exact_filter_sec": _float(optix, ("reported_native_db_phase_totals_sec", "exact_filter_sec")),
        "optix_native_output_pack_sec": _float(optix, ("reported_native_db_phase_totals_sec", "output_pack_sec")),
        "optix_native_raw_candidate_count": _nested(optix, ("reported_native_db_phase_totals_sec", "raw_candidate_count")),
        "optix_native_emitted_count": _nested(optix, ("reported_native_db_phase_totals_sec", "emitted_count")),
    }


def _graph_gate_record(data: dict[str, Any] | None) -> dict[str, Any] | None:
    records = data.get("records") if isinstance(data, dict) else None
    if not isinstance(records, list):
        return None
    for record in records:
        if isinstance(record, dict) and record.get("label") == "optix_visibility_anyhit":
            return record
    return None


def _graph_repeat_section(data: dict[str, Any] | None) -> dict[str, Any] | None:
    return _nested(data, ("sections", "visibility_edges"))


def _graph_row(input_dir: Path, copies: int) -> dict[str, Any]:
    embree = _load_optional(input_dir, f"graph_embree_visibility_{copies}.json")
    optix_gate = _load_optional(input_dir, f"graph_optix_visibility_{copies}.json")
    optix_repeats = _load_optional(input_dir, f"graph_optix_visibility_repeats_{copies}.json")
    gate_record = _graph_gate_record(optix_gate)
    repeat_section = _graph_repeat_section(optix_repeats)
    embree_sec = _float(embree, ("graph_phase_totals_sec", "query_visibility_pair_rows_sec"))
    optix_total_sec = _float(gate_record, ("sec",))
    optix_kernel_sec = _float(gate_record, ("section_run_phases", "query_anyhit_count_sec"))
    repeat_mean_sec = _float(repeat_section, ("run_phases", "query_anyhit_count_mean_sec"))
    return {
        "copies": copies,
        "embree_query_sec": embree_sec,
        "optix_gate_total_sec": optix_total_sec,
        "optix_gate_anyhit_sec": optix_kernel_sec,
        "repeat_query_mean_sec": repeat_mean_sec,
        "repeat_query_min_sec": _float(repeat_section, ("run_phases", "query_anyhit_count_min_sec")),
        "repeat_query_first_sec": _float(repeat_section, ("run_phases", "query_anyhit_count_first_sec")),
        "repeat_count": _nested(repeat_section, ("visibility_query_repeats",)),
        "scene_prepare_sec": _float(repeat_section, ("run_phases", "scene_prepare_sec")),
        "ray_prepare_sec": _float(repeat_section, ("run_phases", "ray_prepare_sec")),
        "ray_pack_mode": _nested(repeat_section, ("ray_pack_mode",)),
        "blocker_pack_mode": _nested(repeat_section, ("blocker_pack_mode",)),
        "ratio_embree_over_optix_total": _ratio(embree_sec, optix_total_sec),
        "ratio_embree_over_optix_anyhit": _ratio(embree_sec, optix_kernel_sec),
        "ratio_embree_over_repeat_mean": _ratio(embree_sec, repeat_mean_sec),
    }


def _polygon_pair_row(input_dir: Path, copies: int) -> dict[str, Any]:
    embree = _load_optional(input_dir, f"polygon_pair_embree_{copies}.json")
    optix = _load_optional(input_dir, f"polygon_pair_optix_{copies}.json")
    embree_sec = _float(embree, ("run_phases", "rt_candidate_discovery_sec"))
    optix_sec = _float(optix, ("phases", "optix_candidate_discovery_sec"))
    return {
        "copies": copies,
        "embree_candidate_sec": embree_sec,
        "optix_candidate_sec": optix_sec,
        "ratio_embree_over_optix": _ratio(embree_sec, optix_sec),
        "parity_vs_cpu": None if optix is None else optix.get("parity_vs_cpu"),
        "candidate_count_matches_expected": _nested(optix, ("candidate_diagnostics", "candidate_count_matches_expected")),
        "candidate_count_delta_vs_expected": _nested(optix, ("candidate_diagnostics", "candidate_count_delta_vs_expected")),
        "positive_pair_count_matches_expected": _nested(optix, ("candidate_diagnostics", "positive_pair_count_matches_expected")),
        "expected_positive_pair_count": _nested(optix, ("candidate_diagnostics", "expected_positive_pair_count")),
        "optix_positive_pair_count": _nested(optix, ("candidate_diagnostics", "optix_positive_pair_count")),
    }


def _jaccard_row(input_dir: Path, copies: int) -> dict[str, Any]:
    embree = _load_optional(input_dir, f"polygon_jaccard_embree_{copies}.json")
    optix = _load_optional(input_dir, f"polygon_jaccard_optix_{copies}_chunk_1024.json")
    embree_sec = _float(embree, ("run_phases", "rt_candidate_discovery_sec"))
    optix_sec = _float(optix, ("phases", "optix_candidate_discovery_sec"))
    return {
        "copies": copies,
        "chunk_copies": _nested(optix, ("chunk_copies",)),
        "chunk_policy": _nested(optix, ("chunk_policy", "policy")),
        "chunk_public_safe": _nested(optix, ("chunk_policy", "public_safe")),
        "embree_candidate_sec": embree_sec,
        "optix_candidate_sec": optix_sec,
        "ratio_embree_over_optix": _ratio(embree_sec, optix_sec),
        "parity_vs_cpu": None if optix is None else optix.get("parity_vs_cpu"),
        "positive_pair_count_matches_expected": _nested(optix, ("candidate_diagnostics", "positive_pair_count_matches_expected")),
    }


def _expected_artifacts() -> list[str]:
    expected = [
        "rtdl_pod_env.json",
        "make_build_optix.status.json",
        "goal1267_status_summary.json",
        "goal1267_graph_ray_pack_metadata.json",
    ]
    expected.extend(f"graph_embree_visibility_{copies}.json" for copies in (30000, 60000))
    expected.extend(f"graph_optix_visibility_{copies}.json" for copies in (30000, 60000))
    expected.extend(f"graph_optix_visibility_repeats_{copies}.json" for copies in (30000, 60000))
    expected.extend(f"polygon_pair_embree_{copies}.json" for copies in (40000, 80000, 160000))
    expected.extend(f"polygon_pair_optix_{copies}.json" for copies in (40000, 80000, 160000))
    expected.extend(f"db_embree_sales_risk_{copies}.json" for copies in (100000, 300000))
    expected.extend(f"db_optix_sales_risk_{copies}.json" for copies in (100000, 300000))
    expected.extend(f"polygon_jaccard_embree_{copies}.json" for copies in (4096, 8192))
    expected.extend(f"polygon_jaccard_optix_{copies}_chunk_1024.json" for copies in (4096, 8192))
    return expected


def build_intake(input_dir: Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    env = _load_optional(input_dir, "rtdl_pod_env.json")
    status_summary = _load_optional(input_dir, "goal1267_status_summary.json") or {}
    missing = [name for name in _expected_artifacts() if not (input_dir / name).exists()]
    graph = [_graph_row(input_dir, copies) for copies in (30000, 60000)]
    db = [_db_row(input_dir, copies) for copies in (100000, 300000)]
    polygon_pair = [_polygon_pair_row(input_dir, copies) for copies in (40000, 80000, 160000)]
    jaccard = [_jaccard_row(input_dir, copies) for copies in (4096, 8192)]
    env_status = _env_status(env)
    build_status = _build_status(input_dir)
    failed_count = int(status_summary.get("failed_count", 0) or 0)
    valid = not missing and failed_count == 0 and env_status == "env_probe_ok" and build_status == "build_ok"
    execution_status = _execution_status(env_status, build_status, missing, failed_count)
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": valid,
        "input_dir": str(input_dir),
        "environment_status": env_status,
        "build_status": build_status,
        "execution_status": execution_status,
        "environment": env,
        "environment_summary": {
            "os_id": None if env is None else env.get("os_id"),
            "package_manager": None if env is None else env.get("package_manager"),
            "cuda_prefix": None if env is None else env.get("cuda_prefix"),
            "nvcc": None if env is None else env.get("nvcc"),
            "optix_prefix": None if env is None else env.get("optix_prefix"),
            "cuda_library_dir": None if env is None else env.get("cuda_library_dir"),
            "nvcc_exists": None if env is None else env.get("nvcc_exists"),
            "optix_header_exists": None if env is None else env.get("optix_header_exists"),
        },
        "status_summary": {
            "status_count": status_summary.get("status_count"),
            "failed_count": status_summary.get("failed_count"),
            "failed_labels": status_summary.get("failed_labels", []),
        },
        "missing_artifacts": missing,
        "decisions": {
            "graph_analytics": _classify_speed(graph, "ratio_embree_over_optix_total"),
            "graph_prepared_repeat": _classify_speed(graph, "ratio_embree_over_repeat_mean"),
            "database_analytics": _classify_speed(db),
            "polygon_pair_overlap_area_rows": _classify_speed(polygon_pair),
            "polygon_set_jaccard": _classify_speed(jaccard),
        },
        "graph_analytics": graph,
        "database_analytics": db,
        "polygon_pair_overlap_area_rows": polygon_pair,
        "polygon_set_jaccard": jaccard,
        "public_wording_authorized": False,
        "boundary": (
            "Goal1272 intakes copied Goal1267 v1.2 pod artifacts only. It does not run "
            "cloud work and does not authorize public RTX speedup wording."
        ),
        "consensus_requirement": (
            "Any public wording, release gate, architecture commitment, or major performance "
            "conclusion remains a key-goal decision and requires 3-AI consensus unless the "
            "user explicitly classifies it lower."
        ),
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1272 v1.2 Targeted Pod Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        f"Public wording authorized: `{payload['public_wording_authorized']}`",
        f"Environment status: `{payload['environment_status']}`",
        f"Build status: `{payload['build_status']}`",
        f"Execution status: `{payload['execution_status']}`",
        "",
        payload["boundary"],
        payload["consensus_requirement"],
        "",
        "## Status",
        "",
        f"- failed count: `{payload['status_summary']['failed_count']}`",
        f"- missing artifacts: `{len(payload['missing_artifacts'])}`",
        "",
        "## Environment",
        "",
        "| OS | Package manager | CUDA prefix | NVCC | OptiX prefix | OptiX header |",
        "| --- | --- | --- | --- | --- | --- |",
        (
            f"| `{payload['environment_summary']['os_id']}` | "
            f"`{payload['environment_summary']['package_manager']}` | "
            f"`{payload['environment_summary']['cuda_prefix']}` | "
            f"`{payload['environment_summary']['nvcc']}` | "
            f"`{payload['environment_summary']['optix_prefix']}` | "
            f"`{payload['environment_summary']['optix_header_exists']}` |"
        ),
        "",
        "## Decisions",
        "",
    ]
    for app, decision in payload["decisions"].items():
        lines.append(f"- `{app}`: `{decision}`")
    lines.extend(["", "## Graph", "", "| Copies | Embree sec | OptiX total | Repeat mean | Total ratio | Repeat ratio |", "| ---: | ---: | ---: | ---: | ---: | ---: |"])
    for row in payload["graph_analytics"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['embree_query_sec'])}` | `{_fmt(row['optix_gate_total_sec'])}` | "
            f"`{_fmt(row['repeat_query_mean_sec'])}` | `{_fmt(row['ratio_embree_over_optix_total'])}` | "
            f"`{_fmt(row['ratio_embree_over_repeat_mean'])}` |"
        )
    lines.extend(["", "## Database", "", "| Copies | Embree warm | OptiX warm | Ratio | OptiX native counters |", "| ---: | ---: | ---: | ---: | --- |"])
    for row in payload["database_analytics"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['embree_warm_query_median_sec'])}` | "
            f"`{_fmt(row['optix_warm_query_median_sec'])}` | `{_fmt(row['ratio_embree_over_optix'])}` | "
            f"`{row['optix_native_counter_status']}` |"
        )
    lines.extend(["", "## Polygon Pair", "", "| Copies | Ratio | Parity | Positive-pair parity | Candidate delta |", "| ---: | ---: | --- | --- | ---: |"])
    for row in payload["polygon_pair_overlap_area_rows"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['ratio_embree_over_optix'])}` | `{row['parity_vs_cpu']}` | "
            f"`{row['positive_pair_count_matches_expected']}` | `{_fmt(row['candidate_count_delta_vs_expected'])}` |"
        )
    lines.extend(["", "## Jaccard", "", "| Copies | Chunk | Safe | Ratio | Positive-pair parity |", "| ---: | ---: | --- | ---: | --- |"])
    for row in payload["polygon_set_jaccard"]:
        lines.append(
            f"| `{row['copies']}` | `{_fmt(row['chunk_copies'])}` | `{row['chunk_public_safe']}` | "
            f"`{_fmt(row['ratio_embree_over_optix'])}` | `{row['positive_pair_count_matches_expected']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This intake does not authorize public RTX speedup wording.",
            "Any public wording or major performance conclusion requires a separate reviewed packet and 3-AI consensus.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake Goal1267 v1.2 targeted pod artifacts.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    payload = build_intake(args.input_dir)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "missing_artifacts": len(payload["missing_artifacts"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
