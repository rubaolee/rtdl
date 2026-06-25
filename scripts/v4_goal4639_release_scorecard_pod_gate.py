#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4639_release_scorecard import evaluate_v4_goal4639_scorecard
from rtdsl.v4_goal4639_release_scorecard import v4_goal4639_run_plan
from rtdsl.v4_goal4639_release_scorecard import validate_v4_goal4639_scorecard_payload


def _json_default(value: object) -> object:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"object is not JSON serializable: {type(value)!r}")


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# V4 Goal4639 Serious Release Scorecard POD Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Recommendation: `{payload['recommendation']}`",
        "",
        "## Summary",
        "",
        f"- strong families passed: `{summary['strong_passed']}/{summary['strong_total']}`",
        f"- measured surfaces passed: `{summary['surface_passed']}/{summary['surface_total']}`",
        f"- partial controls passed: `{summary['partial_passed']}/{summary['partial_total']}`",
        f"- deferred/excluded rows: `{summary['deferred_excluded']}`",
        f"- strong representative ratio geomean: `{summary['strong_representative_ratio_geomean']}`",
        f"- failed surfaces: `{', '.join(summary['failed_surfaces']) if summary['failed_surfaces'] else 'none'}`",
        "",
        "## Surface Results",
        "",
        "| Surface | Status | Representative ratio | Failure |",
        "| --- | --- | ---: | --- |",
    ]
    for row in payload["surface_results"]:
        ratio = row["representative_ratio"]
        ratio_text = "" if ratio is None else f"{float(ratio):.6g}x"
        lines.append(
            f"| `{row['surface']}` | `{row['status']}` | {ratio_text} | {row.get('failure_reason', '')} |"
        )
    lines.extend(
        [
            "",
            "## Benchmark Family Rows",
            "",
            "| Family | Class | Passed | Surfaces |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in payload["family_rows"]:
        surfaces = ", ".join(f"`{surface}`" for surface in row["surfaces"]) if row["surfaces"] else "none"
        lines.append(f"| `{row['family']}` | `{row['class']}` | `{row['passed']}` | {surfaces} |")
    lines.extend(
        [
            "",
            "## Command Records",
            "",
        ]
    )
    for record in payload.get("command_records", []):
        lines.extend(
            [
                f"### {record['run_id']}",
                "",
                f"- surface: `{record['surface']}`",
                f"- return code: `{record['returncode']}`",
                f"- elapsed seconds: `{record['elapsed_seconds']:.3f}`",
                "",
                "```bash",
                " ".join(record["command"]),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Non-Authorization",
            "",
            "This scorecard does not authorize V4 release, V4 release-candidate wording,",
            "broad V4 speedup claims, whole-app speedup claims, all-benchmark speedup",
            "claims, public true-zero-copy claims, Tier-3 callback support, raw OptiX",
            "callback support, CuPy performance claims, C ABI, embedding, non-Python",
            "host claims, or app-specific native kernels.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_command(command: tuple[str, ...], *, env: dict[str, str]) -> tuple[int, float]:
    started = time.perf_counter()
    print(f"[goal4639] start: {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    elapsed = time.perf_counter() - started
    print(f"[goal4639] done rc={completed.returncode} elapsed_s={elapsed:.3f}", flush=True)
    return int(completed.returncode), float(elapsed)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V4 Goal4639 serious release scorecard POD gate.")
    parser.add_argument("--output-dir", type=Path, default=Path("future/v4/evidence/v4_goal4639_release_scorecard_pod_gate_2026-06-25"))
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--skip-run", action="store_true", help="Evaluate existing output-dir artifacts without launching commands.")
    parser.add_argument("--stop-on-failure", action="store_true")
    parser.add_argument("--fail-on-scorecard-fail", action="store_true")
    parser.add_argument("--python-exe", default=sys.executable)
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    json_out = args.json_out or (output_dir / "summary.json")
    md_out = args.md_out or (output_dir / "summary.md")

    plan = v4_goal4639_run_plan(output_dir, python_exe=args.python_exe, root=ROOT)
    if args.plan_only:
        payload = {
            "status": "goal4639_plan_only",
            "output_dir": output_dir.as_posix(),
            "runs": tuple(run.as_dict() for run in plan),
            "release_authorized": False,
        }
        text = json.dumps(payload, indent=2, sort_keys=True, default=_json_default)
        print(text)
        return 0

    command_records: list[dict[str, Any]] = []
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{SRC}{os.pathsep}{ROOT}" + (f"{os.pathsep}{existing_pythonpath}" if existing_pythonpath else "")

    if not args.skip_run:
        for run in plan:
            for evidence in run.evidence:
                Path(evidence).parent.mkdir(parents=True, exist_ok=True)
            returncode, elapsed = _run_command(run.command, env=env)
            record = {
                "run_id": run.run_id,
                "surface": run.surface,
                "command": run.command,
                "returncode": returncode,
                "elapsed_seconds": elapsed,
                "evidence": run.evidence,
            }
            command_records.append(record)
            if returncode != 0 and args.stop_on_failure:
                break

    payload = evaluate_v4_goal4639_scorecard(output_dir)
    payload = dict(payload)
    payload["output_dir"] = output_dir.as_posix()
    payload["command_records"] = tuple(command_records)
    payload = validate_v4_goal4639_scorecard_payload(payload)

    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2, sort_keys=True, default=_json_default) + "\n", encoding="utf-8")
    _write_markdown(payload, md_out)
    print(f"[goal4639] wrote {json_out}", flush=True)
    print(f"[goal4639] wrote {md_out}", flush=True)
    print(f"[goal4639] recommendation={payload['recommendation']}", flush=True)

    if args.fail_on_scorecard_fail and payload["recommendation"] != "release_candidate_possible_pending_3ai":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
