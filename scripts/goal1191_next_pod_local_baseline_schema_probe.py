#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1191 next pod local baseline schema probe"


PROBES: tuple[dict[str, Any], ...] = (
    {
        "app": "database_analytics",
        "command": [
            sys.executable,
            "scripts/goal756_db_prepared_session_perf.py",
            "--backend",
            "embree",
            "--scenario",
            "sales_risk",
            "--copies",
            "2",
            "--iterations",
            "2",
            "--output-mode",
            "compact_summary",
            "--strict",
        ],
        "output_file": "database_compact_summary_embree_probe.json",
        "mode": "output_json_arg",
        "required_paths": [
            ("results", 0, "prepared_session_warm_query_sec", "median_sec"),
            ("results", 0, "reported_run_phase_totals_sec", "compact_summary_operation_count"),
        ],
    },
    {
        "app": "graph_analytics",
        "command": [
            sys.executable,
            "examples/v2_0/apps/analytics/rtdl_graph_analytics_app.py",
            "--backend",
            "embree",
            "--scenario",
            "visibility_edges",
            "--copies",
            "2",
            "--output-mode",
            "summary",
        ],
        "output_file": "graph_visibility_edges_embree_probe.json",
        "mode": "stdout_json",
        "required_paths": [
            ("graph_phase_totals_sec", "query_visibility_pair_rows_sec"),
            ("sections", "visibility_edges", "summary", "blocked_edge_count"),
        ],
    },
    {
        "app": "road_hazard_screening",
        "command": [
            sys.executable,
            "examples/v2_0/apps/geospatial/rtdl_road_hazard_screening.py",
            "--backend",
            "embree",
            "--copies",
            "2",
            "--output-mode",
            "summary",
        ],
        "output_file": "road_hazard_native_summary_embree_probe.json",
        "mode": "stdout_json",
        "required_paths": [
            ("run_phases", "query_and_materialize_sec"),
            ("priority_segment_count",),
        ],
    },
    {
        "app": "polygon_pair_overlap_area_rows",
        "command": [
            sys.executable,
            "examples/v2_0/features/spatial/rtdl_polygon_pair_overlap_area_rows.py",
            "--backend",
            "embree",
            "--copies",
            "2",
            "--output-mode",
            "summary",
        ],
        "output_file": "polygon_pair_candidate_discovery_embree_probe.json",
        "mode": "stdout_json",
        "required_paths": [
            ("run_phases", "rt_candidate_discovery_sec"),
            ("run_phases", "native_exact_continuation_sec"),
            ("candidate_row_count",),
        ],
    },
    {
        "app": "polygon_set_jaccard",
        "command": [
            sys.executable,
            "examples/v2_0/features/spatial/rtdl_polygon_set_jaccard.py",
            "--backend",
            "embree",
            "--copies",
            "2",
            "--output-mode",
            "summary",
        ],
        "output_file": "polygon_jaccard_safe_chunk_embree_probe.json",
        "mode": "stdout_json",
        "required_paths": [
            ("run_phases", "rt_candidate_discovery_sec"),
            ("run_phases", "native_exact_continuation_sec"),
            ("candidate_row_count",),
        ],
    },
    {
        "app": "hausdorff_distance",
        "command": [
            sys.executable,
            "examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
            "--backend",
            "embree",
            "--copies",
            "2",
            "--embree-result-mode",
            "directed_summary",
            "--hausdorff-threshold",
            "0.4",
        ],
        "output_file": "hausdorff_threshold_prepared_embree_probe.json",
        "mode": "stdout_json",
        "required_paths": [
            ("run_phases", "native_directed_summary_sec"),
            ("matches_oracle",),
        ],
    },
)


def _get_path(payload: Any, path: tuple[Any, ...]) -> Any:
    current = payload
    for key in path:
        current = current[key]
    return current


def run_probe(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for probe in PROBES:
        output_path = output_dir / probe["output_file"]
        command = list(probe["command"])
        if probe["mode"] == "output_json_arg":
            command.extend(["--output-json", str(output_path)])
            completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_path = output_dir / f"{probe['app']}_stdout.txt"
            stdout_path.write_text(completed.stdout, encoding="utf-8")
        else:
            completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path = output_dir / f"{probe['app']}_stderr.txt"
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        exists = output_path.exists()
        parse_error = ""
        missing_paths: list[str] = []
        payload: Any = None
        if completed.returncode == 0 and exists:
            try:
                payload = json.loads(output_path.read_text(encoding="utf-8"))
            except Exception as exc:  # pragma: no cover - defensive diagnostics
                parse_error = str(exc)
        for required_path in probe["required_paths"]:
            if payload is None:
                missing_paths.append(".".join(map(str, required_path)))
                continue
            try:
                _get_path(payload, required_path)
            except Exception:
                missing_paths.append(".".join(map(str, required_path)))
        rows.append(
            {
                "app": probe["app"],
                "command": " ".join(command),
                "output_file": str(output_path.relative_to(ROOT)) if output_path.is_relative_to(ROOT) else str(output_path),
                "returncode": completed.returncode,
                "json_parse_error": parse_error,
                "missing_required_paths": missing_paths,
                "status": "ok" if completed.returncode == 0 and not parse_error and not missing_paths else "schema_probe_failure",
            }
        )
    failures = [row for row in rows if row["status"] != "ok"]
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not failures,
        "output_dir": str(output_dir),
        "probe_count": len(rows),
        "passing_probe_count": len(rows) - len(failures),
        "failing_probe_count": len(failures),
        "rows": rows,
        "boundary": (
            "This is a local baseline JSON/schema probe only. It does not run OptiX, "
            "does not authorize pod execution, and does not authorize public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1191 Next Pod Local Baseline Schema Probe",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- output dir: `{payload['output_dir']}`",
        f"- probes: `{payload['probe_count']}`",
        f"- passing probes: `{payload['passing_probe_count']}`",
        f"- failing probes: `{payload['failing_probe_count']}`",
        "",
        "## Rows",
        "",
        "| App | Status | Return code | Missing paths | Parse error |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        missing = ", ".join(row["missing_required_paths"]) or "none"
        parse_error = row["json_parse_error"] or "none"
        lines.append(f"| `{row['app']}` | `{row['status']}` | {row['returncode']} | `{missing}` | `{parse_error}` |")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local baseline schema probes for the next RTX pod contract.")
    parser.add_argument("--output-dir", default="docs/reports/goal1191_next_pod_local_baseline_schema_probe")
    parser.add_argument("--output-json", default="docs/reports/goal1191_next_pod_local_baseline_schema_probe_2026-04-30.json")
    parser.add_argument("--output-md", default="docs/reports/goal1191_next_pod_local_baseline_schema_probe_2026-04-30.md")
    args = parser.parse_args()

    payload = run_probe(ROOT / args.output_dir)
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "json": str(output_json), "md": str(output_md)}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
