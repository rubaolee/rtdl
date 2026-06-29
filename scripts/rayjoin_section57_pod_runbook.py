from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RAYJOIN_ENTRY = ROOT / "examples" / "paper_reproduction" / "rayjoin.py"


def _run_json(command: list[str], *, output_path: Path) -> tuple[int, dict[str, object] | None, str, str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    payload = None
    if output_path.exists():
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    else:
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = None
    return completed.returncode, payload, completed.stdout, completed.stderr


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _base_args(args: argparse.Namespace) -> list[str]:
    command = [
        "--dataset-root",
        str(args.dataset_root),
        "--output-dir",
        str(args.output_dir),
        "--query-exec",
        str(args.query_exec),
        "--polyover-exec",
        str(args.polyover_exec),
        "--implementations",
        args.implementations,
        "--author-warmup",
        str(args.author_warmup),
        "--author-repeat",
        str(args.author_repeat),
        "--rtdl-warmup",
        str(args.rtdl_warmup),
        "--rtdl-repeat",
        str(args.rtdl_repeat),
    ]
    if args.pairs:
        command.extend(["--pairs", args.pairs])
    if args.v4_numba_measurements:
        command.extend(["--v4-numba-measurements", str(args.v4_numba_measurements)])
    if args.v4_numba_section57_device_columns_ready:
        command.append("--v4-numba-section57-device-columns-ready")
    return command


def _entry_command(args: argparse.Namespace, mode: str, *extra: str) -> list[str]:
    return [sys.executable, str(RAYJOIN_ENTRY), mode, *_base_args(args), *extra]


def build_commands(args: argparse.Namespace) -> dict[str, list[str] | None]:
    preflight_json = args.output_dir / "section57_preflight.json"
    plan_json = args.output_dir / "section57_overlay_plan.json"
    plan_md = args.output_dir / "section57_overlay_plan.md"
    supplied_candidate_measurements = args.v4_numba_measurements is not None
    candidate_measurements_json = args.v4_numba_measurements or (
        args.output_dir / "section57_v4_numba_candidate_measurements.json"
    )
    args.v4_numba_measurements = candidate_measurements_json
    run_json = args.output_dir / "section57_overlay_run.json"
    summary_json = args.output_dir / "section57_overlay_summary.json"
    summary_md = args.output_dir / "section57_overlay_summary.md"

    plan_command = _entry_command(
        args,
        "--section57-plan",
        "--output-json",
        str(plan_json),
        "--output-md",
        str(plan_md),
    )
    run_extra = [
        "--run-json",
        str(run_json),
        "--summary-json",
        str(summary_json),
        "--summary-md",
        str(summary_md),
    ]
    if args.dry_run:
        run_extra.append("--dry-run")
    if args.allow_missing_inputs or args.dry_run:
        run_extra.append("--allow-missing-inputs")
    candidate_probe = None
    if not supplied_candidate_measurements:
        candidate_probe = [
            sys.executable,
            str(ROOT / "scripts" / "rayjoin_section57_numba_candidate_probe.py"),
            "--dataset-root",
            str(args.dataset_root),
            "--output-json",
            str(candidate_measurements_json),
            "--warmup",
            str(args.rtdl_warmup),
            "--repeat",
            str(args.rtdl_repeat),
        ]
        if args.pairs:
            candidate_probe.extend(["--pairs", args.pairs])
        if args.dry_run:
            candidate_probe.append("--dry-run")
        if args.v4_numba_topology_geometry_hash_match_confirmed:
            candidate_probe.append("--topology-geometry-hash-match-confirmed")
    return {
        "preflight": _entry_command(
            args,
            "--section57-preflight",
            "--output-json",
            str(preflight_json),
            "--json",
        ),
        "plan": plan_command,
        "candidate_probe": candidate_probe,
        "run": _entry_command(args, "--section57-run", *run_extra),
        "summary": _entry_command(
            args,
            "--section57-summary",
            "--output-json",
            str(summary_json),
            "--output-md",
            str(summary_md),
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "POD runbook for RayJoin Section 5.7. It preflights exact "
            "inputs, author binaries, RT-core GPU, Numba CUDA, and device-column "
            "components before running the author/V2/V4 matrix."
        )
    )
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--query-exec", required=True, type=Path)
    parser.add_argument("--polyover-exec", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--pairs")
    parser.add_argument("--implementations", default="author_rt,rtdl_optix,rtdl_embree,v4_numba")
    parser.add_argument("--author-warmup", type=int, default=5)
    parser.add_argument("--author-repeat", type=int, default=5)
    parser.add_argument("--rtdl-warmup", type=int, default=1)
    parser.add_argument("--rtdl-repeat", type=int, default=3)
    parser.add_argument(
        "--v4-numba-measurements",
        type=Path,
        help="POD-measured V4+Numba candidate timing file to import into the matrix.",
    )
    parser.add_argument(
        "--v4-numba-section57-device-columns-ready",
        action="store_true",
        help="Pass through when the Section 5.7 device-column route should enter measurement selection.",
    )
    parser.add_argument(
        "--v4-numba-topology-geometry-hash-match-confirmed",
        action="store_true",
        help="Forward only after independent full-overlay correctness comparison is available.",
    )
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-missing-inputs", action="store_true")
    parser.add_argument("--runbook-json", type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    runbook_json = args.runbook_json or (args.output_dir / "section57_pod_runbook.json")
    commands = build_commands(args)
    started = time.perf_counter()

    preflight_code, preflight, preflight_stdout, preflight_stderr = _run_json(
        commands["preflight"],
        output_path=args.output_dir / "section57_preflight.json",
    )
    ready = bool(preflight and preflight.get("ready_for_performance_run"))
    blockers = [] if preflight is None else list(preflight.get("blockers", []))

    steps: list[dict[str, object]] = [
        {
            "step": "preflight",
            "returncode": preflight_code,
            "ready_for_performance_run": ready,
            "blockers": blockers,
            "command": commands["preflight"],
            "stdout_path": None,
            "stderr": preflight_stderr,
        }
    ]
    exit_code = 0
    status = "preflight_ready" if ready else "preflight_blocked"
    if preflight_code != 0:
        exit_code = preflight_code
        status = "preflight_command_failed"
    elif args.preflight_only:
        status = "preflight_only_ready" if ready else "preflight_only_blocked"
    elif not ready and not args.dry_run:
        exit_code = 2
        status = "blocked_before_performance_run"
    else:
        for name in ("plan", "candidate_probe", "run"):
            command = commands[name]
            if command is None:
                steps.append(
                    {
                        "step": name,
                        "status": "skipped_existing_v4_numba_measurements",
                    }
                )
                continue
            completed = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout_path = args.output_dir / f"{name}.stdout.txt"
            stderr_path = args.output_dir / f"{name}.stderr.txt"
            stdout_path.write_text(completed.stdout, encoding="utf-8")
            stderr_path.write_text(completed.stderr, encoding="utf-8")
            steps.append(
                {
                    "step": name,
                    "returncode": completed.returncode,
                    "command": command,
                    "stdout_path": str(stdout_path),
                    "stderr_path": str(stderr_path),
                }
            )
            if completed.returncode != 0:
                exit_code = completed.returncode
                status = f"{name}_failed"
                break
        else:
            status = "dry_run_complete" if args.dry_run else "performance_run_complete"

    payload = {
        "schema": "rtdl.rayjoin.section57_pod_runbook.v1",
        "status": status,
        "ready_for_performance_run": ready,
        "blockers": blockers,
        "dataset_root": str(args.dataset_root),
        "output_dir": str(args.output_dir),
        "query_exec": str(args.query_exec),
        "polyover_exec": str(args.polyover_exec),
        "commands": commands,
        "steps": steps,
        "artifacts": {
            "preflight_json": str(args.output_dir / "section57_preflight.json"),
            "plan_json": str(args.output_dir / "section57_overlay_plan.json"),
            "plan_md": str(args.output_dir / "section57_overlay_plan.md"),
            "run_json": str(args.output_dir / "section57_overlay_run.json"),
            "summary_json": str(args.output_dir / "section57_overlay_summary.json"),
            "summary_md": str(args.output_dir / "section57_overlay_summary.md"),
            "v4_numba_candidate_measurements_json": str(args.v4_numba_measurements),
        },
        "claim_boundary": (
            "This runbook is execution plumbing. A release claim requires the "
            "summary rows to contain completed author_rt, V2.14 exact-suite, "
            "and V4+Numba results with correctness and timing."
        ),
        "elapsed_sec": time.perf_counter() - started,
    }
    if preflight_stdout:
        (args.output_dir / "preflight.stdout.txt").write_text(preflight_stdout, encoding="utf-8")
    if preflight_stderr:
        (args.output_dir / "preflight.stderr.txt").write_text(preflight_stderr, encoding="utf-8")
    _write_json(runbook_json, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
