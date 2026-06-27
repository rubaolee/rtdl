#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py"
BASE_RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
SELF_QUERY_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.json"
)
SELF_QUERY_GRAPH_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_self_query_graph_evidence_2026-06-21.json"
)
OUT_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_column_source_residency_gap_2026-06-21.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")
MATERIAL_SPEEDUP_FLOOR = 2.0


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _share(part: float, total: float) -> float:
    return part / total if total else 0.0


def _phase_shares(measurement: dict[str, Any]) -> dict[str, float]:
    input_load = float(measurement.get("input_load_sec", 0.0))
    input_pack = float(measurement.get("input_pack_sec", 0.0))
    prepare = float(measurement.get("execution_prepare_sec", 0.0))
    hot = float(measurement.get("hot_median_sec", 0.0))
    runner_wall = float(measurement.get("runner_wall_sec", input_load + input_pack + prepare + hot))
    return {
        "input_load_share_of_runner_wall": _share(input_load, runner_wall),
        "input_pack_share_of_runner_wall": _share(input_pack, runner_wall),
        "execution_prepare_share_of_runner_wall": _share(prepare, runner_wall),
        "hot_query_share_of_runner_wall": _share(hot, runner_wall),
        "non_hot_share_of_runner_wall": _share(input_load + input_pack + prepare, runner_wall),
    }


def build_payload() -> dict[str, Any]:
    runner_text = RUNNER.read_text(encoding="utf-8")
    base_runner_text = BASE_RUNNER.read_text(encoding="utf-8")
    self_query = _read_json(SELF_QUERY_EVIDENCE)
    graph = _read_json(SELF_QUERY_GRAPH_EVIDENCE)

    new_self_query = self_query["measurements"]["new_prepared_self_query"]
    cupy_grid = self_query["measurements"]["cupy_grid_reference"]
    graph_self_query = graph["measurements"]["self_query_graph"]
    direct_self_query = graph["measurements"]["direct_self_query"]

    comparisons = {
        "new_self_query_over_cupy_hot_speedup": float(
            self_query["comparisons"]["new_self_query_over_cupy_hot_speedup"]
        ),
        "new_self_query_over_cupy_cold_plus_query_speedup": float(
            self_query["comparisons"]["new_self_query_over_cupy_cold_plus_query_speedup"]
        ),
        "new_self_query_over_cupy_runner_wall_speedup": float(
            self_query["comparisons"]["new_self_query_over_cupy_runner_wall_speedup"]
        ),
        "self_query_input_load_over_hot_query": _ratio(
            float(new_self_query["input_load_sec"]),
            float(new_self_query["hot_median_sec"]),
        ),
        "self_query_non_hot_over_hot_query": _ratio(
            float(new_self_query["input_load_sec"])
            + float(new_self_query["input_pack_sec"])
            + float(new_self_query["execution_prepare_sec"]),
            float(new_self_query["hot_median_sec"]),
        ),
        "graph_over_direct_cold_plus_query_speedup": float(
            graph["comparisons"]["graph_over_direct_cold_plus_query_speedup"]
        ),
    }
    checks = {
        "self_query_evidence_exists": SELF_QUERY_EVIDENCE.exists(),
        "self_query_graph_evidence_exists": SELF_QUERY_GRAPH_EVIDENCE.exists(),
        "phoenix_runner_exposes_point_column_source": "--point-column-source" in runner_text,
        "phoenix_runner_defaults_to_npz": 'DEFAULT_POINT_COLUMN_SOURCE = "npz"' in runner_text,
        "phoenix_runner_writes_npz_columns": "write_point_columns_npz" in runner_text
        and "rtnn_npz_xyz_columns_v1" in runner_text,
        "base_runner_reads_npz_columns": "_read_xyz_columns_npz" in base_runner_text
        and "_read_xyz_columns_with_source" in base_runner_text,
        "base_runner_records_point_column_source": '"point_column_source": point_column_source'
        in base_runner_text,
        "cupy_grid_reference_uses_same_column_source": (
            "def run_cupy_grid_3d_ranked_summary" in base_runner_text
            and "_read_xyz_columns_with_source(\n        args.point_file,\n        source=point_column_source"
            in base_runner_text
            and '"point_column_source": point_column_source' in base_runner_text
        ),
        "cupy_references_use_vectorized_column_stack": (
            "_xyz_columns_to_numpy" in base_runner_text
            and "np.asarray(list(zip(search_columns[1]" not in base_runner_text
        ),
        "self_query_hot_is_material": comparisons["new_self_query_over_cupy_hot_speedup"]
        >= MATERIAL_SPEEDUP_FLOOR,
        "self_query_runner_wall_not_material": comparisons[
            "new_self_query_over_cupy_runner_wall_speedup"
        ]
        < MATERIAL_SPEEDUP_FLOOR,
        "input_load_dominates_runner_wall": _phase_shares(new_self_query)[
            "input_load_share_of_runner_wall"
        ]
        > 0.50,
        "graph_route_not_material": comparisons["graph_over_direct_cold_plus_query_speedup"]
        < MATERIAL_SPEEDUP_FLOOR,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = (
        "fail"
        if failed_checks
        else "rtnn_npz_column_source_ready_for_pod_rerun_not_m7"
    )
    return {
        "tool": "v3_phoenix_rtnn_column_source_residency_gap",
        "status": status,
        "generic_capability": "fixed_radius_neighbors_3d_column_ingestion",
        "candidate_scope": (
            "generic RTNN fixed-radius ranked-summary input/column ingestion; "
            "not an app-specific native route and not V4 interop"
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "material_speedup_floor": MATERIAL_SPEEDUP_FLOOR,
        "evidence": {
            "self_query": _rel(SELF_QUERY_EVIDENCE),
            "self_query_graph": _rel(SELF_QUERY_GRAPH_EVIDENCE),
            "phoenix_runner": _rel(RUNNER),
            "base_runner": _rel(BASE_RUNNER),
        },
        "measurements": {
            "new_prepared_self_query": {
                **new_self_query,
                **_phase_shares(new_self_query),
            },
            "cupy_grid_reference": cupy_grid,
            "direct_self_query": direct_self_query,
            "self_query_graph": graph_self_query,
        },
        "comparisons": comparisons,
        "implemented_v3_surface": {
            "point_column_source_choices": ["csv", "numpy_csv", "npz"],
            "default_point_column_source": "npz",
            "column_source_manifest_format": "rtnn_npz_xyz_columns_v1",
            "uses_existing_vectorized_pack_points": True,
            "v4_c_abi_or_embedding": False,
            "app_specific_native_engine": False,
        },
        "not_m7_blockers": [
            (
                "The existing POD evidence still has only "
                f"{comparisons['new_self_query_over_cupy_runner_wall_speedup']:.3f}x "
                "runner-wall speedup versus CuPy."
            ),
            (
                "Input load is "
                f"{_phase_shares(new_self_query)['input_load_share_of_runner_wall']:.1%} "
                "of the current prepared self-query runner wall."
            ),
            "The NPZ column-source path is implemented and locally tested, but it still needs a fresh same-hardware RTX POD rerun.",
            "No external Claude/Gemini review has accepted a rerun as an M7 row.",
        ],
        "pod_rerun_requirements": [
            "Run the serious same-contract RTNN runner with --point-column-source npz on the RTX pod.",
            "Save optix and cupy_grid full payloads, point_manifest.json, environment.json, and summary.json.",
            "Require point_column_source=npz on both phase rows.",
            "Require same-contract integer parity and sum-distance relative error <= 1e-4.",
            "Require cold-plus-query and runner-wall speedups to clear the material floor before M7 review.",
            "Send the rerun packet to external AI and record Codex consensus before any public wording.",
        ],
        "forbidden_shortcuts": [
            "Do not call the existing 19.437x hot-query result an end-to-end V3 win.",
            "Do not claim npz ingestion is a speedup until the POD rerun proves it.",
            "Do not describe this as zero-copy, embedding, C ABI, or V4 interop.",
            "Do not promote RTNN from this packet alone.",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": (
                "Move RTNN wall-path work from prose to a V3 NPZ column-source surface and "
                "a rerun gate, while keeping current RTNN rows out of M7."
            ),
            "was_i_foolish": (
                "No. This implements a generic V3 ingestion path inside the existing Python-hosted "
                "surface and blocks public claims until POD evidence exists."
            ),
            "foolish_actions": (
                "It would be foolish to repackage the 19.437x hot-query number or the 1.030x "
                "runner-wall number as proof that V3 solves RTNN."
            ),
            "other_path": (
                "I could wait for external review of AABB or design a new Barnes-Hut primitive, "
                "but that would not address the current RTNN wall-path blocker."
            ),
            "different_path_now": (
                "Run the NPZ column-source RTNN evidence path on the pod; only a material "
                "same-contract cold/runner result plus review can reopen M7."
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    m = payload["measurements"]["new_prepared_self_query"]
    c = payload["comparisons"]
    audit = payload["goal_level_decision_audit"]
    lines = [
        "# Phoenix V3 RTNN Column-Source Residency Gap",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This packet keeps RTNN on the V3 engine path: the current hot query is fast,",
        "but the whole-run wall is still dominated by input and preparation. The new",
        "`npz` column-source route is implemented for the serious runner. The npz column-source route is implemented, but it needs",
        "fresh POD evidence before any M7 or public claim; this packet is not M7.",
        "",
        "```text",
        f"release_authorized: {str(payload['release_authorized']).lower()}",
        f"public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}",
        f"m7_promotion_authorized: {str(payload['m7_promotion_authorized']).lower()}",
        "```",
        "",
        "## Current Wall Breakdown",
        "",
        f"- Hot-query speedup over CuPy grid: `{c['new_self_query_over_cupy_hot_speedup']:.3f}x`",
        f"- Cold+query speedup over CuPy grid: `{c['new_self_query_over_cupy_cold_plus_query_speedup']:.3f}x`",
        f"- Runner-wall speedup over CuPy grid: `{c['new_self_query_over_cupy_runner_wall_speedup']:.3f}x`",
        f"- Input load / hot query: `{c['self_query_input_load_over_hot_query']:.3f}x`",
        f"- Non-hot wall / hot query: `{c['self_query_non_hot_over_hot_query']:.3f}x`",
        f"- Input-load share of runner wall: `{m['input_load_share_of_runner_wall']:.3%}`",
        "",
        "## Implemented V3 Surface",
        "",
        "- `--point-column-source csv|numpy_csv|npz` on the serious RTNN runner",
        "- default `npz` column-source path for Phoenix reruns",
        "- `rtnn_npz_xyz_columns_v1` source manifest",
        "- source metadata recorded on both OptiX and CuPy phase rows",
        "- no V4 C ABI, embedding, or app-specific native engine",
        "",
        "## Not M7",
        "",
        *[f"- {item}" for item in payload["not_m7_blockers"]],
        "",
        "## POD Rerun Requirements",
        "",
        *[f"- {item}" for item in payload["pod_rerun_requirements"]],
        "",
        "## Goal-Level Decision Audit",
        "",
        f"Decision: {audit['decision']}",
        "",
        f"1. Was I foolish? {audit['was_i_foolish']}",
        f"2. If yes, what actions made the decision foolish? {audit['foolish_actions']}",
        f"3. Was there another path that would have avoided getting stuck on that idea? {audit['other_path']}",
        f"4. Can I now try a different path that actually solves the problem? {audit['different_path_now']}",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit Phoenix V3 RTNN column-source residency gap packet.")
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not payload["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
