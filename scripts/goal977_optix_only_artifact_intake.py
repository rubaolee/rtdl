#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact


GOAL = "Goal977 OptiX-only artifact intake"
DATE = "2026-04-26"
DEFAULT_CLOUD_DIR = ROOT / "docs" / "reports" / "cloud_2026_04_26" / "runpod_a5000_0900"


GRAPH_BASELINES = {
    "optix_visibility_anyhit": "visibility_edges",
    "optix_native_graph_ray_bfs": "bfs",
    "optix_native_graph_ray_triangle_count": "triangle_count",
}


def _artifact_path(app: str, path_name: str, baseline_name: str) -> Path:
    return ROOT / "docs" / "reports" / f"goal835_baseline_{app}_{path_name}_{baseline_name}_2026-04-23.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _record_by_label(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(record["label"]): record
        for record in payload.get("records", ())
        if isinstance(record, dict) and "label" in record
    }


def _graph_artifact(graph_payload: dict[str, Any], baseline_name: str) -> dict[str, Any]:
    row = load_goal835_row(
        app="graph_analytics",
        path_name="graph_visibility_edges_gate",
        baseline_name=baseline_name,
    )
    records = _record_by_label(graph_payload)
    record = records[baseline_name]
    parity = (
        graph_payload.get("strict_pass") is True
        and record.get("status") == "ok"
        and record.get("parity_vs_analytic_expected") is True
    )
    digest = dict(record["digest"])
    summary = {
        "label": baseline_name,
        "scenario": record.get("scenario"),
        "sec": float(record.get("sec", 0.0)),
        "row_count": int(digest.get("row_count", 0)),
        "row_digest": str(digest.get("row_digest", "")),
        "summary": digest.get("summary"),
    }
    return build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend="optix",
        benchmark_scale={"copies": graph_payload.get("copies"), "validation_mode": graph_payload.get("validation_mode")},
        repeated_runs=3,
        correctness_parity=parity,
        phase_seconds={
            "records": float(len(graph_payload.get("records", ()))),
            "row_digest": 1.0 if digest.get("row_digest") else 0.0,
            "strict_pass": 1.0 if graph_payload.get("strict_pass") is True else 0.0,
            "strict_failures": float(len(graph_payload.get("strict_failures", ()))),
            "status": 1.0 if record.get("status") == "ok" else 0.0,
        },
        summary=summary,
        notes=[
            "Ingested from the existing Runpod A5000 graph OptiX gate artifact.",
            "Validation is analytic-summary parity at the compact graph RT sub-path contract.",
            "This artifact does not authorize public RTX speedup claims.",
        ],
        validation={
            "source_artifact": "docs/reports/cloud_2026_04_26/runpod_a5000_0900/goal889_graph_visibility_optix_gate_rtx.json",
            "strict_pass": graph_payload.get("strict_pass"),
            "strict_failures": graph_payload.get("strict_failures"),
            "record_status": record.get("status"),
            "parity_vs_analytic_expected": record.get("parity_vs_analytic_expected"),
        },
    )


def _segment_anyhit_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    baseline_name = "optix_prepared_bounded_pair_rows"
    row = load_goal835_row(
        app="segment_polygon_anyhit_rows",
        path_name="segment_polygon_anyhit_rows_prepared_bounded_gate",
        baseline_name=baseline_name,
    )
    result = dict(payload["result"])
    timings = dict(payload["timings_sec"])
    parity = (
        payload.get("strict_pass") is True
        and result.get("matches_oracle") is True
        and result.get("overflowed") is False
    )
    optix_query = timings.get("optix_query_sec", {})
    python_postprocess = timings.get("python_postprocess_sec", {})
    validation = timings.get("validation_sec", {})
    return build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend="optix",
        benchmark_scale={
            "dataset": payload.get("dataset"),
            "iterations": payload.get("iterations"),
            "output_capacity": payload.get("output_capacity"),
        },
        repeated_runs=int(payload.get("iterations", 0)),
        correctness_parity=parity,
        phase_seconds={
            "input_build_sec": float(timings.get("input_build_sec", 0.0)),
            "cpu_reference_total_sec": float(timings.get("cpu_reference_total_sec", 0.0)),
            "optix_prepare_sec": float(timings.get("optix_prepare_sec", 0.0)),
            "optix_query_sec": float(optix_query.get("median_sec", 0.0)),
            "python_postprocess_sec": float(python_postprocess.get("median_sec", 0.0)),
            "validation_sec": float(validation.get("median_sec", 0.0)),
            "optix_close_sec": float(timings.get("optix_close_sec", 0.0)),
            "emitted_count": float(result.get("emitted_count", 0)),
            "copied_count": float(result.get("copied_count", 0)),
            "overflowed": 1.0 if result.get("overflowed") else 0.0,
            "strict_pass": 1.0 if payload.get("strict_pass") is True else 0.0,
            "strict_failures": float(len(payload.get("strict_failures", ()))),
            "status": 1.0 if payload.get("status") == "pass" else 0.0,
        },
        summary={
            "dataset": payload.get("dataset"),
            "segment_count": result.get("segment_count"),
            "polygon_count": result.get("polygon_count"),
            "emitted_count": result.get("emitted_count"),
            "copied_count": result.get("copied_count"),
            "overflowed": result.get("overflowed"),
            "matches_oracle": result.get("matches_oracle"),
            "actual_digest": result.get("actual_digest"),
            "expected_digest": result.get("expected_digest"),
        },
        notes=[
            "Ingested from the existing Runpod A5000 prepared segment/polygon bounded pair-row artifact.",
            "The source artifact strict-passed with CPU digest parity and no output overflow.",
            "This artifact does not authorize public RTX speedup claims.",
        ],
        validation={
            "source_artifact": "docs/reports/cloud_2026_04_26/runpod_a5000_0900/goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json",
            "strict_pass": payload.get("strict_pass"),
            "strict_failures": payload.get("strict_failures"),
            "matches_oracle": result.get("matches_oracle"),
            "overflowed": result.get("overflowed"),
        },
    )


def collect(*, cloud_dir: Path) -> dict[str, Any]:
    graph_payload = _load_json(cloud_dir / "goal889_graph_visibility_optix_gate_rtx.json")
    segment_payload = _load_json(cloud_dir / "goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json")
    outputs: list[dict[str, Any]] = []
    for baseline_name in GRAPH_BASELINES:
        artifact = _graph_artifact(graph_payload, baseline_name)
        path = _artifact_path(artifact["app"], artifact["path_name"], artifact["baseline_name"])
        write_baseline_artifact(path, artifact)
        outputs.append({"app": artifact["app"], "baseline": artifact["baseline_name"], "path": str(path), "status": artifact["status"]})
    artifact = _segment_anyhit_artifact(segment_payload)
    path = _artifact_path(artifact["app"], artifact["path_name"], artifact["baseline_name"])
    write_baseline_artifact(path, artifact)
    outputs.append({"app": artifact["app"], "baseline": artifact["baseline_name"], "path": str(path), "status": artifact["status"]})
    return {
        "goal": GOAL,
        "date": DATE,
        "cloud_dir": str(cloud_dir),
        "artifact_count": len(outputs),
        "artifacts": outputs,
        "status": "ok" if all(item["status"] == "ok" for item in outputs) else "invalid",
        "boundary": "This intake converts existing RTX artifacts into Goal835 baseline artifacts. It does not run cloud and does not authorize public RTX speedup claims.",
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal977 OptiX-Only Artifact Intake",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        f"- source cloud dir: `{payload['cloud_dir']}`",
        f"- artifacts: `{payload['artifact_count']}`",
        "",
        "| App | Baseline | Artifact | Status |",
        "|---|---|---|---|",
    ]
    for artifact in payload["artifacts"]:
        lines.append(f"| `{artifact['app']}` | `{artifact['baseline']}` | `{artifact['path']}` | `{artifact['status']}` |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest existing RTX artifacts for remaining OptiX-only Goal835 baselines.")
    parser.add_argument("--cloud-dir", type=Path, default=DEFAULT_CLOUD_DIR)
    parser.add_argument("--output-json", default=str(ROOT / "docs" / "reports" / "goal977_optix_only_artifact_intake_2026-04-26.json"))
    parser.add_argument("--output-md", default=str(ROOT / "docs" / "reports" / "goal977_optix_only_artifact_intake_2026-04-26.md"))
    args = parser.parse_args(argv)
    payload = collect(cloud_dir=args.cloud_dir)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
