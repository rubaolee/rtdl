#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "docs" / "reports" / "goal1746_v1_0_embree_baseline_adapter_manifest_2026-05-12.md"
DEFAULT_JSON = ROOT / "docs" / "reports" / "goal1746_v1_0_embree_baseline_adapter_manifest_2026-05-12.json"


def _cmd(app: str, *args: str, scale: str = "goal1660") -> dict[str, Any]:
    return {
        "app": app,
        "engine": "embree",
        "command": [sys.executable, *args],
        "artifact": f"docs/reports/goal1746_v1_0_{app}_embree.json",
        "scale": scale,
    }


RECOVERABLE_ROWS: list[dict[str, Any]] = [
    _cmd(
        "service_coverage_gaps",
        "examples/rtdl_service_coverage_gaps.py",
        "--backend",
        "embree",
        "--copies",
        "20000",
        "--embree-summary-mode",
        "gap_summary",
    ),
    _cmd(
        "event_hotspot_screening",
        "examples/rtdl_event_hotspot_screening.py",
        "--backend",
        "embree",
        "--copies",
        "20000",
        "--embree-summary-mode",
        "count_summary",
    ),
    _cmd(
        "facility_knn_assignment",
        "examples/rtdl_facility_knn_assignment.py",
        "--backend",
        "embree",
        "--copies",
        "20000",
        "--output-mode",
        "summary",
    ),
    _cmd(
        "road_hazard_screening",
        "examples/rtdl_road_hazard_screening.py",
        "--backend",
        "embree",
        "--copies",
        "20000",
        "--output-mode",
        "summary",
    ),
    _cmd(
        "segment_polygon_hitcount",
        "examples/rtdl_segment_polygon_hitcount.py",
        "--backend",
        "embree",
        "--copies",
        "256",
    ),
    _cmd(
        "segment_polygon_anyhit_rows",
        "examples/rtdl_segment_polygon_anyhit_rows.py",
        "--backend",
        "embree",
        "--copies",
        "256",
        "--output-mode",
        "rows",
        "--output-capacity",
        "4096",
    ),
    _cmd(
        "graph_visibility_edges",
        "examples/rtdl_graph_analytics_app.py",
        "--backend",
        "embree",
        "--scenario",
        "visibility_edges",
        "--copies",
        "20000",
        "--output-mode",
        "summary",
    ),
    _cmd(
        "graph_bfs",
        "examples/rtdl_graph_analytics_app.py",
        "--backend",
        "embree",
        "--scenario",
        "bfs",
        "--copies",
        "20000",
        "--output-mode",
        "summary",
    ),
    _cmd(
        "graph_triangle_count",
        "examples/rtdl_graph_analytics_app.py",
        "--backend",
        "embree",
        "--scenario",
        "triangle_count",
        "--copies",
        "20000",
        "--output-mode",
        "summary",
    ),
    _cmd(
        "hausdorff_distance",
        "examples/rtdl_hausdorff_distance_app.py",
        "--backend",
        "embree",
        "--copies",
        "20000",
        "--embree-result-mode",
        "directed_summary",
    ),
    _cmd(
        "ann_candidate_search",
        "examples/rtdl_ann_candidate_app.py",
        "--backend",
        "embree",
        "--copies",
        "20000",
        "--output-mode",
        "rerank_summary",
    ),
    _cmd(
        "barnes_hut_force_app",
        "examples/rtdl_barnes_hut_force_app.py",
        "--backend",
        "embree",
        "--body-count",
        "200000",
        "--output-mode",
        "candidate_summary",
    ),
    _cmd(
        "polygon_pair_overlap_area_rows",
        "examples/rtdl_polygon_pair_overlap_area_rows.py",
        "--backend",
        "embree",
        "--copies",
        "20000",
        "--output-mode",
        "summary",
    ),
    _cmd(
        "polygon_set_jaccard",
        "examples/rtdl_polygon_set_jaccard.py",
        "--backend",
        "embree",
        "--copies",
        "20000",
    ),
]


def _write_manifest(report_path: Path, json_path: Path) -> dict[str, Any]:
    payload = {
        "goal": "Goal1746",
        "verdict": "v1_0_embree_baseline_adapter_ready",
        "row_count": len(RECOVERABLE_ROWS),
        "rows": RECOVERABLE_ROWS,
        "boundary": (
            "These rows use real v1.0 Embree example/app command surfaces from the "
            "Goal1030 local baseline manifest. They are adapter candidates, not "
            "public speedup claims. Timing comparability must be assessed per row "
            "after artifacts are generated."
        ),
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Goal1746 v1.0 Embree Baseline Adapter Manifest",
        "",
        "## Verdict",
        "",
        "`v1_0_embree_baseline_adapter_ready`",
        "",
        payload["boundary"],
        "",
        "## Rows",
        "",
        "| App | Artifact | Command |",
        "| --- | --- | --- |",
    ]
    for row in RECOVERABLE_ROWS:
        command = " ".join(row["command"])
        lines.append(f"| `{row['app']}` | `{row['artifact']}` | `{command}` |")
    lines.extend(
        [
            "",
            "## Execution",
            "",
            "Run from current main and point `--baseline-workdir` at a clean v1.0 checkout with Embree built:",
            "",
            "```bash",
            "PYTHONPATH=src:. python3 scripts/goal1746_v1_0_embree_baseline_adapter.py --baseline-workdir /path/to/v1_0_checkout --run",
            "```",
            "",
            "The runner captures stdout JSON from each v1.0 app command and writes it into the current checkout's `docs/reports/` directory.",
            "",
            "## Boundary",
            "",
            "This manifest and runner recover real v1.0 Embree baseline artifacts where v1.0 exposed app-level Embree CLIs. It does not fabricate missing phase-profiler rows and does not authorize public speedup wording.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def _log(message: str) -> None:
    print(message, flush=True)


def _run_rows(
    baseline_workdir: Path,
    current_workdir: Path,
    stop_on_failure: bool,
    resume: bool,
    skip_apps: set[str],
    only_apps: set[str],
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env["PYTHONPATH"] = "src:."
    for index, row in enumerate(RECOVERABLE_ROWS, start=1):
        if only_apps and row["app"] not in only_apps:
            continue
        artifact = current_workdir / row["artifact"]
        if row["app"] in skip_apps:
            _log(f"[goal1746] skip {index}/{len(RECOVERABLE_ROWS)} {row['app']} reason=skip_app")
            results.append(
                {
                    "app": row["app"],
                    "artifact": row["artifact"],
                    "returncode": None,
                    "stdout_json": False,
                    "skipped_by_request": True,
                    "stderr_tail": "",
                    "stdout_tail": "",
                }
            )
            continue
        if resume and artifact.exists() and artifact.stat().st_size > 0:
            _log(f"[goal1746] skip {index}/{len(RECOVERABLE_ROWS)} {row['app']} existing={artifact}")
            results.append(
                {
                    "app": row["app"],
                    "artifact": row["artifact"],
                    "returncode": 0,
                    "stdout_json": True,
                    "resumed_existing_artifact": True,
                    "stderr_tail": "",
                    "stdout_tail": "",
                }
            )
            continue
        start = time.perf_counter()
        _log(
            "[goal1746] start "
            f"{index}/{len(RECOVERABLE_ROWS)} {row['app']} -> {row['artifact']}"
        )
        completed = subprocess.run(
            row["command"],
            cwd=baseline_workdir,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        artifact.parent.mkdir(parents=True, exist_ok=True)
        parsed_ok = False
        if completed.returncode == 0:
            try:
                payload = json.loads(completed.stdout)
                payload["_goal1746_adapter"] = {
                    "baseline_workdir": str(baseline_workdir),
                    "command": row["command"],
                    "source": "v1.0 Embree app CLI stdout JSON",
                }
                artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                parsed_ok = True
            except json.JSONDecodeError:
                artifact.write_text(completed.stdout, encoding="utf-8")
        results.append(
            {
                "app": row["app"],
                "artifact": row["artifact"],
                "returncode": completed.returncode,
                "stdout_json": parsed_ok,
                "elapsed_sec": time.perf_counter() - start,
                "stderr_tail": completed.stderr[-2000:],
                "stdout_tail": completed.stdout[-2000:],
            }
        )
        _log(
            "[goal1746] done "
            f"{index}/{len(RECOVERABLE_ROWS)} {row['app']} "
            f"returncode={completed.returncode} json={parsed_ok} "
            f"elapsed_sec={time.perf_counter() - start:.3f}"
        )
        if stop_on_failure and (completed.returncode != 0 or not parsed_ok):
            break
    summary = {
        "goal": "Goal1746",
        "baseline_workdir": str(baseline_workdir),
        "attempted": len(results),
        "completed": sum(1 for row in results if row["returncode"] == 0 and row["stdout_json"]),
        "results": results,
    }
    output = current_workdir / "docs" / "reports" / "goal1746_v1_0_embree_baseline_adapter_run_2026-05-12.json"
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare or run v1.0 Embree baseline adapter rows.")
    parser.add_argument("--baseline-workdir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--skip-app",
        action="append",
        default=[],
        help="Skip a recoverable row by app name; may be repeated.",
    )
    parser.add_argument(
        "--only-app",
        action="append",
        default=[],
        help="Run only this recoverable row by app name; may be repeated.",
    )
    parser.add_argument("--stop-on-failure", action="store_true")
    args = parser.parse_args(argv)
    payload = _write_manifest(args.report, args.json)
    if not args.run:
        print(json.dumps({"manifest": str(args.json), "row_count": payload["row_count"]}, sort_keys=True))
        return 0
    if args.baseline_workdir is None:
        raise SystemExit("--baseline-workdir is required with --run")
    summary = _run_rows(
        args.baseline_workdir.resolve(),
        ROOT,
        args.stop_on_failure,
        args.resume,
        set(args.skip_app),
        set(args.only_app),
    )
    print(json.dumps({"attempted": summary["attempted"], "completed": summary["completed"]}, sort_keys=True))
    return 0 if summary["attempted"] == summary["completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
