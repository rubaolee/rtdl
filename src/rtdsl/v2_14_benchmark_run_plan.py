from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .v2_14_benchmark_cleanup import V2_14_CLAIM_BOUNDARY
from .v2_14_benchmark_cleanup import v2_14_benchmark_cleanup_rows


V2_14_BENCHMARK_RUN_PLAN_VERSION = "rtdl.v2_14.benchmark_run_plan.goal4380.v1"
V2_14_BENCHMARK_RUN_PLAN_STATUS = "executable_plan_not_release_evidence"

DEFAULT_OUTPUT_DIR = "docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14"
DEFAULT_OVERLAY_DATASET_ROOT = "/workspace/rayjoin_section57_data/cdb_topology"
DEFAULT_RAYJOIN_QUERY_EXEC = "/workspace/RayJoin_fresh/release/bin/query_exec"
DEFAULT_RAYJOIN_POLYOVER_EXEC = "/workspace/RayJoin_fresh/release/bin/polyover_exec"


HUMAN_SCALE_SELECTION_BY_ROW_ID: dict[str, str] = {
    "hausdorff_xhd_threshold": "hausdorff_xhd",
    "spatial_rayjoin_lsi": "spatial_rayjoin_lsi",
    "spatial_rayjoin_pip": "spatial_rayjoin_pip",
    "rt_dbscan_core_flags_numba_signature": "rt_dbscan",
    "robot_collision_grouped_segment_flags": "robot_collision",
    "contact_manifold_aabb_collect_k": "contact_manifold",
    "raydb_style_grouped_i64_count": "raydb_style",
    "barnes_hut_node_coverage": "barnes_hut",
    "librts_spatial_index_aabb": "librts_spatial_index",
    "rtnn_ranked_summary": "rtnn",
    "triangle_counting_any_hit": "triangle_counting",
}


@dataclass(frozen=True)
class V214BenchmarkRunPlanRow:
    row_id: str
    app: str
    row_label: str
    runner: str
    command: tuple[str, ...]
    output_dir: str
    evidence_status: str
    claim_boundary: str
    expected_result_artifact: str
    phase_explanation_required: bool = True
    release_evidence: bool = False
    public_wording_authorized: bool = False

    def __post_init__(self) -> None:
        if self.runner not in ("human_scale_same_contract", "rayjoin_section57_overlay"):
            raise ValueError(f"{self.row_id}: unsupported runner {self.runner}")
        if not self.command:
            raise ValueError(f"{self.row_id}: command must not be empty")
        if not self.expected_result_artifact:
            raise ValueError(f"{self.row_id}: expected result artifact must be explicit")
        if self.release_evidence:
            raise ValueError(f"{self.row_id}: run-plan rows are not release evidence")
        if self.public_wording_authorized:
            raise ValueError(f"{self.row_id}: run-plan rows do not authorize public wording")

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "app": self.app,
            "row_label": self.row_label,
            "runner": self.runner,
            "command": list(self.command),
            "output_dir": self.output_dir,
            "evidence_status": self.evidence_status,
            "claim_boundary": self.claim_boundary,
            "expected_result_artifact": self.expected_result_artifact,
            "phase_explanation_required": self.phase_explanation_required,
            "release_evidence": self.release_evidence,
            "public_wording_authorized": self.public_wording_authorized,
        }


def _join(*parts: str) -> str:
    return str(Path(*parts).as_posix())


def _human_scale_command(
    *,
    python_executable: str,
    output_dir: str,
    selection: str,
) -> tuple[str, ...]:
    return (
        python_executable,
        "scripts/rtdl_human_scale_rt_vs_embree_comparison.py",
        "--output-dir",
        output_dir,
        "--only",
        selection,
    )


def _overlay_command(
    *,
    python_executable: str,
    output_dir: str,
    dataset_root: str,
    query_exec: str,
    polyover_exec: str,
    pairs: str | None,
) -> tuple[str, ...]:
    run_json = _join(output_dir, "section57_overlay_run.json")
    summary_json = _join(output_dir, "section57_overlay_summary.json")
    summary_md = _join(output_dir, "section57_overlay_summary.md")
    command = [
        python_executable,
        "scripts/rayjoin_section57_overlay_matrix.py",
        "run",
        "--dataset-root",
        dataset_root,
        "--output-dir",
        output_dir,
        "--query-exec",
        query_exec,
        "--polyover-exec",
        polyover_exec,
        "--author-warmup",
        "5",
        "--author-repeat",
        "5",
        "--rtdl-warmup",
        "1",
        "--rtdl-repeat",
        "3",
        "--run-json",
        run_json,
        "--summary-json",
        summary_json,
        "--summary-md",
        summary_md,
    ]
    if pairs:
        command.extend(["--pairs", pairs])
    return tuple(command)


def v2_14_benchmark_run_plan_rows(
    *,
    python_executable: str = "python3",
    output_dir: str = DEFAULT_OUTPUT_DIR,
    overlay_dataset_root: str = DEFAULT_OVERLAY_DATASET_ROOT,
    rayjoin_query_exec: str = DEFAULT_RAYJOIN_QUERY_EXEC,
    rayjoin_polyover_exec: str = DEFAULT_RAYJOIN_POLYOVER_EXEC,
    overlay_pairs: str | None = None,
) -> tuple[V214BenchmarkRunPlanRow, ...]:
    rows: list[V214BenchmarkRunPlanRow] = []
    human_dir = _join(output_dir, "human_scale_same_contract")
    overlay_dir = _join(output_dir, "rayjoin_section57_overlay")
    for cleanup_row in v2_14_benchmark_cleanup_rows():
        if cleanup_row.row_id == "spatial_rayjoin_overlay":
            rows.append(
                V214BenchmarkRunPlanRow(
                    row_id=cleanup_row.row_id,
                    app=cleanup_row.app,
                    row_label=cleanup_row.row_label,
                    runner="rayjoin_section57_overlay",
                    command=_overlay_command(
                        python_executable=python_executable,
                        output_dir=overlay_dir,
                        dataset_root=overlay_dataset_root,
                        query_exec=rayjoin_query_exec,
                        polyover_exec=rayjoin_polyover_exec,
                        pairs=overlay_pairs,
                    ),
                    output_dir=overlay_dir,
                    evidence_status="requires_fresh_section57_overlay_run_8_of_8",
                    claim_boundary=(
                        "Overlay output is a Section 5.7 process/app-runtime packet. "
                        "It must not be reported as author hot-compute parity."
                    ),
                    expected_result_artifact=_join(overlay_dir, "section57_overlay_summary.json"),
                )
            )
            continue
        selection = HUMAN_SCALE_SELECTION_BY_ROW_ID[cleanup_row.row_id]
        rows.append(
            V214BenchmarkRunPlanRow(
                row_id=cleanup_row.row_id,
                app=cleanup_row.app,
                row_label=cleanup_row.row_label,
                runner="human_scale_same_contract",
                command=_human_scale_command(
                    python_executable=python_executable,
                    output_dir=human_dir,
                    selection=selection,
                ),
                output_dir=human_dir,
                evidence_status="requires_fresh_same_contract_human_scale_run",
                claim_boundary=cleanup_row.required_phase_explanation,
                expected_result_artifact=_join(human_dir, "summary.json"),
            )
        )
    return tuple(rows)


def validate_v2_14_benchmark_run_plan(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = packet.get("rows")
    if not isinstance(rows, list):
        return ["rows must be a list"]
    cleanup_ids = {row.row_id for row in v2_14_benchmark_cleanup_rows()}
    row_ids = [row.get("row_id") for row in rows if isinstance(row, dict)]
    if set(row_ids) != cleanup_ids:
        errors.append("run plan must cover exactly the v2.14 cleanup row ids")
    if len(row_ids) != len(set(row_ids)):
        errors.append("row ids must be unique")
    human_rows = [row for row in rows if isinstance(row, dict) and row.get("runner") == "human_scale_same_contract"]
    overlay_rows = [row for row in rows if isinstance(row, dict) and row.get("runner") == "rayjoin_section57_overlay"]
    if len(human_rows) != 11:
        errors.append("run plan must contain 11 human-scale rows")
    if [row.get("row_id") for row in overlay_rows] != ["spatial_rayjoin_overlay"]:
        errors.append("run plan must contain exactly one RayJoin Section 5.7 overlay row")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("every row must be a dict")
            continue
        command = row.get("command")
        if not isinstance(command, list) or not command:
            errors.append(f"{row.get('row_id')}: command must be a non-empty list")
            continue
        if row.get("runner") == "human_scale_same_contract":
            if "scripts/rtdl_human_scale_rt_vs_embree_comparison.py" not in command:
                errors.append(f"{row.get('row_id')}: human-scale command missing runner")
            if "--only" not in command:
                errors.append(f"{row.get('row_id')}: human-scale command must use --only")
        if row.get("runner") == "rayjoin_section57_overlay":
            for required in (
                "scripts/rayjoin_section57_overlay_matrix.py",
                "run",
                "--query-exec",
                "--polyover-exec",
                "--summary-json",
            ):
                if required not in command:
                    errors.append(f"{row.get('row_id')}: overlay command missing {required}")
        if row.get("release_evidence") is not False:
            errors.append(f"{row.get('row_id')}: run-plan row must not be release evidence")
        if row.get("public_wording_authorized") is not False:
            errors.append(f"{row.get('row_id')}: public wording must not be authorized")
    summary = packet.get("summary", {})
    if summary.get("release_ready") is not False:
        errors.append("summary.release_ready must be false")
    if summary.get("row_count") != len(rows):
        errors.append("summary.row_count must match rows")
    if summary.get("human_scale_row_count") != len(human_rows):
        errors.append("summary.human_scale_row_count must match rows")
    if summary.get("overlay_row_count") != len(overlay_rows):
        errors.append("summary.overlay_row_count must match rows")
    return errors


def v2_14_benchmark_run_plan_packet(
    *,
    python_executable: str = "python3",
    output_dir: str = DEFAULT_OUTPUT_DIR,
    overlay_dataset_root: str = DEFAULT_OVERLAY_DATASET_ROOT,
    rayjoin_query_exec: str = DEFAULT_RAYJOIN_QUERY_EXEC,
    rayjoin_polyover_exec: str = DEFAULT_RAYJOIN_POLYOVER_EXEC,
    overlay_pairs: str | None = None,
) -> dict[str, Any]:
    rows = [
        row.to_dict()
        for row in v2_14_benchmark_run_plan_rows(
            python_executable=python_executable,
            output_dir=output_dir,
            overlay_dataset_root=overlay_dataset_root,
            rayjoin_query_exec=rayjoin_query_exec,
            rayjoin_polyover_exec=rayjoin_polyover_exec,
            overlay_pairs=overlay_pairs,
        )
    ]
    packet: dict[str, Any] = {
        "version": V2_14_BENCHMARK_RUN_PLAN_VERSION,
        "status": V2_14_BENCHMARK_RUN_PLAN_STATUS,
        "claim_boundary": V2_14_CLAIM_BOUNDARY,
        "rows": rows,
        "summary": {
            "release_ready": False,
            "row_count": len(rows),
            "human_scale_row_count": sum(1 for row in rows if row["runner"] == "human_scale_same_contract"),
            "overlay_row_count": sum(1 for row in rows if row["runner"] == "rayjoin_section57_overlay"),
            "public_wording_authorized_count": sum(1 for row in rows if row["public_wording_authorized"]),
            "release_evidence_count": sum(1 for row in rows if row["release_evidence"]),
            "overlay_pairs": overlay_pairs or "all_section57_pairs_8_of_8",
            "output_dir": output_dir,
        },
    }
    errors = validate_v2_14_benchmark_run_plan(packet)
    packet["validation"] = {
        "status": "accept_executable_plan" if not errors else "reject",
        "errors": errors,
    }
    return packet


def markdown_v2_14_benchmark_run_plan(packet: dict[str, Any] | None = None) -> str:
    payload = packet or v2_14_benchmark_run_plan_packet()
    lines = [
        "# Goal4380 v2.14 Executable Benchmark Run Plan",
        "",
        "Status: executable plan; not release evidence.",
        "",
        "## Summary",
        "",
        f"- Validation: `{payload['validation']['status']}`",
        f"- Release rows planned: `{payload['summary']['row_count']}`",
        f"- Human-scale same-contract rows: `{payload['summary']['human_scale_row_count']}`",
        f"- RayJoin Section 5.7 overlay rows: `{payload['summary']['overlay_row_count']}`",
        f"- Public wording authorized rows now: `{payload['summary']['public_wording_authorized_count']}`",
        "",
        "## Rows",
        "",
        "| Row | Runner | Evidence Status | Expected Artifact |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {row_id} | `{runner}` | {evidence_status} | `{expected_result_artifact}` |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Commands",
            "",
        ]
    )
    for row in payload["rows"]:
        lines.append(f"### {row['row_id']}")
        lines.append("")
        lines.append("```bash")
        lines.append(" ".join(row["command"]))
        lines.append("```")
        lines.append("")
    lines.extend(
        [
            "## Claim Boundary",
            "",
            V2_14_CLAIM_BOUNDARY,
            "",
            "This run plan only defines how to collect fresh evidence. The generated results still need "
            "phase-level review before any v2.14 public wording is authorized.",
        ]
    )
    return "\n".join(lines) + "\n"
