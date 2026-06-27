#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_RELATIVE = Path(
    "examples/current/research_benchmarks/librts_spatial_index/"
    "rtdl_librts_spatial_index_benchmark_app.py"
)
SCHEMA = "rtdl.phoenix_v3.m47_librts_stability_protocol.v1"
AUTHORIZATION_TOKEN = "M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED"
M57_AUTHORIZATION_TOKEN = "M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED"
AUTHORIZED_EXECUTION_TOKENS = (AUTHORIZATION_TOKEN, M57_AUTHORIZATION_TOKEN)
STATUS_DRY_RUN = "m47_librts_stability_protocol_dry_run_no_pod_not_release"
STATUS_PREFLIGHT_ONLY = "m47_librts_stability_protocol_preflight_only_no_pod_not_release"
STATUS_COMPLETE = "m47_librts_stability_protocol_run_complete_not_release"
STATUS_FAILED = "m47_librts_stability_protocol_run_failed_not_release"
PREFLIGHT_TEST_MODULES = (
    "tests.v3_phoenix_librts_aabb_count_runner_test",
    "tests.v3_phoenix_prepared_execution_session_runner_test",
    "tests.v3_phoenix_aabb_prepared_query_cache_test",
)
CURRENT_SOURCE_SIGNATURE_SCRIPT = r"""
from __future__ import annotations

import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
prepared_path = root / "src" / "rtdsl" / "prepared_execution.py"
app_path = (
    root
    / "examples"
    / "current"
    / "research_benchmarks"
    / "librts_spatial_index"
    / "rtdl_librts_spatial_index_benchmark_app.py"
)
prepared = prepared_path.read_text(encoding="utf-8")
app = app_path.read_text(encoding="utf-8")
checks = {
    "prepared_embree_count_helper_present": "def run_aabb_index_query_2d_count_prepared_session" in prepared,
    "prepared_optix_query_set_helper_present": (
        "def run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session" in prepared
    ),
    "prepared_helpers_mark_set_b_control": prepared.count('metadata["set_b_control_candidate"] = True') >= 3,
    "prepared_helpers_mark_not_set_a_probe": prepared.count('metadata["set_a_probe_candidate"] = False') >= 3,
    "prepared_optix_helper_marks_prepared_query_mode": (
        'metadata["prepared_query_mode"] = "optix_prepared_query_set"' in prepared
    ),
    "librts_app_exposes_payload_set_b": (
        '"set_b_control_candidate": bool(runner_metadata.get("set_b_control_candidate"))' in app
    ),
    "librts_app_exposes_metadata_set_b_twice": (
        app.count('"set_b_control_candidate": bool(runner_metadata.get("set_b_control_candidate"))') >= 2
    ),
    "librts_app_exposes_optix_prepared_query_mode": (
        '"prepared_query_mode": runner_metadata.get("prepared_query_mode")' in app
    ),
}
failed = [name for name, passed in checks.items() if not passed]
print(json.dumps({"checks": checks, "failed": failed}, indent=2, sort_keys=True))
raise SystemExit(1 if failed else 0)
""".strip()


SCENARIOS: dict[str, dict[str, Any]] = {
    "optix_cold_single_shot": {
        "backend": "optix",
        "mode": "optix_aabb_index",
        "box_count": 2048,
        "query_count": 1024,
        "repeat": 1,
        "warmup": 0,
        "skip_counts": False,
        "watch_status_before_m47": "improved_not_closed",
    },
    "embree_32768_stress": {
        "backend": "embree",
        "mode": "embree_aabb_index",
        "box_count": 32768,
        "query_count": 1024,
        "repeat": 20,
        "warmup": 5,
        "skip_counts": True,
        "watch_status_before_m47": "stability_watch_blocker",
    },
}


CLAIM_BOUNDARY = {
    "release_authorized": False,
    "all_app_pod_spend_authorized": False,
    "focused_pod_spend_authorized_now": False,
    "public_speedup_claim_authorized": False,
    "broad_v3_faster_than_v2_claim_authorized": False,
    "v4_work_authorized": False,
    "embedding_work_authorized": False,
    "c_abi_work_authorized": False,
    "true_zero_copy_claim_authorized": False,
}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_or_run_packet(args)
    (args.output_dir / "summary.json").write_text(
        json.dumps(json_ready(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "README.md").write_text(readme(payload), encoding="utf-8")
    print(json.dumps(json_ready(payload["summary"]), indent=2, sort_keys=True), flush=True)
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phoenix V3 M47 LibRTS stability/cold-start protocol harness. "
            "Defaults to dry-run and does not authorize POD, all-app, release, "
            "or public speedup claims."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/rebuild/v3/evidence/phoenix_v3_m47_librts_stability_protocol_20260623")
    parser.add_argument("--scenario", choices=("all", *SCENARIOS), default="all")
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--current-root", type=Path, default=ROOT)
    parser.add_argument("--v2-root", type=Path, required=False)
    parser.add_argument("--current-python", default=sys.executable)
    parser.add_argument("--v2-python", default=sys.executable)
    parser.add_argument("--command-timeout-sec", type=float, default=600.0)
    parser.add_argument("--run-preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--authorization-token", default="")
    return parser.parse_args(argv)


def build_or_run_packet(args: argparse.Namespace) -> dict[str, Any]:
    validate_args(args)
    schedule = build_schedule(args)
    if not bool(args.execute):
        if bool(args.run_preflight):
            preflight, preflight_errors = execute_preflight(args)
            return build_payload(
                args=args,
                schedule=schedule,
                preflight=preflight,
                scenario_results={},
                run_errors=preflight_errors,
                status=STATUS_PREFLIGHT_ONLY if not preflight_errors else STATUS_FAILED,
            )
        return build_payload(
            args=args,
            schedule=schedule,
            scenario_results={},
            run_errors={},
            status=STATUS_DRY_RUN,
        )
    if str(args.authorization_token) not in AUTHORIZED_EXECUTION_TOKENS:
        raise SystemExit(
            "M47 execution requires explicit external authorization token; "
            "run dry-run without --execute while authorization is pending"
        )
    preflight, preflight_errors = execute_preflight(args)
    if preflight_errors:
        return build_payload(
            args=args,
            schedule=schedule,
            preflight=preflight,
            scenario_results={},
            run_errors=preflight_errors,
            status=STATUS_FAILED,
        )
    scenario_results, run_errors = execute_schedule(args, schedule)
    return build_payload(
        args=args,
        schedule=schedule,
        preflight=preflight,
        scenario_results=scenario_results,
        run_errors=run_errors,
        status=STATUS_COMPLETE if not run_errors else STATUS_FAILED,
    )


def validate_args(args: argparse.Namespace) -> None:
    if int(args.samples) != 8:
        raise SystemExit("M47 protocol requires exactly 8 paired samples")
    if bool(args.execute) and args.v2_root is None:
        raise SystemExit("--v2-root is required for execution")


def selected_scenarios(args: argparse.Namespace) -> tuple[str, ...]:
    if str(args.scenario) == "all":
        return tuple(SCENARIOS)
    return (str(args.scenario),)


def build_schedule(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario_id in selected_scenarios(args):
        scenario = SCENARIOS[scenario_id]
        for sample in range(1, int(args.samples) + 1):
            order = ("v2_14", "current") if sample % 2 == 1 else ("current", "v2_14")
            for tree in order:
                rows.append(
                    {
                        "scenario_id": scenario_id,
                        "tree": tree,
                        "sample": sample,
                        "order": list(order),
                        "command": command_for(args, scenario, tree=tree),
                    }
                )
    return rows


def build_preflight(args: argparse.Namespace) -> dict[str, Any]:
    rows: dict[str, Any] = {
        "nvidia_smi": {
            "command": ["nvidia-smi"],
            "cwd": str(ROOT),
            "required": True,
        },
        "current_python_version": {
            "command": [str(args.current_python), "--version"],
            "cwd": str(Path(args.current_root)),
            "required": True,
        },
        "current_git_revision": {
            "command": ["git", "rev-parse", "HEAD"],
            "cwd": str(Path(args.current_root)),
            "required": False,
        },
        "current_librts_set_b_source_signature": {
            "command": [
                str(args.current_python),
                "-c",
                CURRENT_SOURCE_SIGNATURE_SCRIPT,
                str(Path(args.current_root)),
            ],
            "cwd": str(Path(args.current_root)),
            "required": True,
        },
        "current_preflight_tests": {
            "command": [str(args.current_python), "-m", "unittest", *PREFLIGHT_TEST_MODULES],
            "cwd": str(Path(args.current_root)),
            "required": True,
        },
    }
    if args.v2_root is not None:
        rows["v2_python_version"] = {
            "command": [str(args.v2_python), "--version"],
            "cwd": str(Path(args.v2_root)),
            "required": True,
        }
        rows["v2_git_revision"] = {
            "command": ["git", "rev-parse", "HEAD"],
            "cwd": str(Path(args.v2_root)),
            "required": False,
        }
    return rows


def command_for(args: argparse.Namespace, scenario: dict[str, Any], *, tree: str) -> list[str]:
    python = str(args.current_python if tree == "current" else args.v2_python)
    if tree == "current":
        app_path = str(Path(args.current_root) / APP_RELATIVE)
    elif args.v2_root is None:
        app_path = "<v2-root-required-on-execute>/" + APP_RELATIVE.as_posix()
    else:
        app_path = str(Path(args.v2_root) / APP_RELATIVE)
    command = [
        python,
        app_path,
        "--mode",
        str(scenario["mode"]),
        "--dataset",
        "uniform",
        "--operation",
        "all",
        "--box-count",
        str(int(scenario["box_count"])),
        "--query-count",
        str(int(scenario["query_count"])),
        "--seed",
        str(int(args.seed)),
        "--repeat",
        str(int(scenario["repeat"])),
        "--warmup",
        str(int(scenario["warmup"])),
    ]
    if bool(scenario["skip_counts"]):
        command.append("--skip-counts")
    return command


def cwd_for(args: argparse.Namespace, *, tree: str) -> Path:
    if tree == "current":
        return Path(args.current_root)
    if args.v2_root is None:
        return ROOT
    return Path(args.v2_root)


def env_for_root(root: Path) -> dict[str, str]:
    env = dict(os.environ)
    entries = [str(root / "src"), str(root)]
    existing = env.get("PYTHONPATH")
    if existing:
        entries.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(entries)
    return env


def payload_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def execute_preflight(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, str]]:
    results: dict[str, Any] = {}
    errors: dict[str, str] = {}
    for name, row in build_preflight(args).items():
        stdout_path = args.output_dir / f"preflight_{name}.stdout.txt"
        stderr_path = args.output_dir / f"preflight_{name}.stderr.txt"
        print(f"[phoenix-v3-m47] preflight={name}", flush=True)
        try:
            completed = subprocess.run(
                list(row["command"]),
                cwd=str(row["cwd"]),
                env=env_for_root(Path(row["cwd"])),
                check=False,
                capture_output=True,
                text=True,
                timeout=float(args.command_timeout_sec),
            )
            stdout_path.write_text(completed.stdout, encoding="utf-8")
            stderr_path.write_text(completed.stderr, encoding="utf-8")
            results[name] = {
                "command": list(row["command"]),
                "cwd": str(row["cwd"]),
                "required": bool(row["required"]),
                "returncode": int(completed.returncode),
                "stdout": payload_path(stdout_path),
                "stderr": payload_path(stderr_path),
                "stderr_empty": completed.stderr.strip() == "",
            }
            if bool(row["required"]) and completed.returncode != 0:
                errors[f"preflight_{name}"] = f"exit_code={completed.returncode}"
        except Exception as exc:  # pragma: no cover - execution is hardware/environment dependent.
            results[name] = {
                "command": list(row["command"]),
                "cwd": str(row["cwd"]),
                "required": bool(row["required"]),
                "error": repr(exc),
            }
            if bool(row["required"]):
                errors[f"preflight_{name}"] = repr(exc)
    return results, errors


def execute_schedule(args: argparse.Namespace, schedule: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, str]]:
    raw_rows: list[dict[str, Any]] = []
    run_errors: dict[str, str] = {}
    for row in schedule:
        scenario_id = str(row["scenario_id"])
        tree = str(row["tree"])
        sample = int(row["sample"])
        name = f"{scenario_id}_{tree}_s{sample:02d}"
        stdout_path = args.output_dir / f"{name}.stdout.json"
        stderr_path = args.output_dir / f"{name}.stderr.txt"
        try:
            print(f"[phoenix-v3-m47] scenario={scenario_id} tree={tree} sample={sample}", flush=True)
            completed = subprocess.run(
                list(row["command"]),
                cwd=str(cwd_for(args, tree=tree)),
                env=env_for_root(cwd_for(args, tree=tree)),
                check=False,
                capture_output=True,
                text=True,
                timeout=float(args.command_timeout_sec),
            )
            stdout_path.write_text(completed.stdout, encoding="utf-8")
            stderr_path.write_text(completed.stderr, encoding="utf-8")
            if completed.returncode != 0:
                run_errors[name] = f"exit_code={completed.returncode}"
                continue
            payload = json.loads(completed.stdout)
            raw_rows.append(
                {
                    **row,
                    "stdout_json": payload_path(stdout_path),
                    "stderr_txt": payload_path(stderr_path),
                    "payload": payload,
                    "query_sec": extract_query_sec(payload),
                    "stderr_empty": completed.stderr.strip() == "",
                }
            )
        except Exception as exc:  # pragma: no cover - execution is hardware/environment dependent.
            run_errors[name] = repr(exc)
    return analyze_rows(raw_rows), run_errors


def extract_query_sec(payload: dict[str, Any]) -> float:
    repeat_protocol = payload.get("repeat_protocol")
    if isinstance(repeat_protocol, dict) and "query_sec_median" in repeat_protocol:
        return float(repeat_protocol["query_sec_median"])
    run_phases = payload.get("run_phases")
    if isinstance(run_phases, dict) and "query_median_sec" in run_phases:
        return float(run_phases["query_median_sec"])
    if "elapsed_sec" in payload:
        return float(payload["elapsed_sec"])
    raise ValueError("payload does not expose query timing")


def analyze_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_scenario: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_scenario.setdefault(str(row["scenario_id"]), []).append(row)
    return {scenario_id: analyze_scenario(scenario_rows) for scenario_id, scenario_rows in by_scenario.items()}


def analyze_scenario(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_sample: dict[int, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by_sample.setdefault(int(row["sample"]), {})[str(row["tree"])] = row
    paired: list[dict[str, Any]] = []
    for sample in sorted(by_sample):
        pair = by_sample[sample]
        if "current" not in pair or "v2_14" not in pair:
            continue
        current_sec = float(pair["current"]["query_sec"])
        v2_sec = float(pair["v2_14"]["query_sec"])
        fixture_contract = fixture_contract_status(pair)
        metadata_failures = current_metadata_failures(pair["current"])
        paired.append(
            {
                "sample": sample,
                "current_sec": current_sec,
                "v2_14_sec": v2_sec,
                "speedup_v2_over_current": v2_sec / current_sec if current_sec else math.inf,
                "current_stderr_empty": bool(pair["current"]["stderr_empty"]),
                "v2_14_stderr_empty": bool(pair["v2_14"]["stderr_empty"]),
                "fixture_contract_matches": fixture_contract["matches"],
                "fixture_contract_failures": fixture_contract["failures"],
                "current_metadata_ok": not metadata_failures,
                "current_metadata_failures": metadata_failures,
            }
        )
    ratios = [float(row["speedup_v2_over_current"]) for row in paired]
    first_stripped = [ratio for row, ratio in zip(paired, ratios) if int(row["sample"]) != 1]
    status = classify_ratios(ratios, first_stripped, paired)
    return {
        "paired_samples": paired,
        "sample_count": len(paired),
        "geomean": geomean(ratios),
        "median": statistics.median(ratios) if ratios else None,
        "min": min(ratios) if ratios else None,
        "max": max(ratios) if ratios else None,
        "pass_count_0_95": sum(1 for ratio in ratios if ratio >= 0.95),
        "first_sample_stripped_geomean": geomean(first_stripped),
        "first_sample_stripped_median": statistics.median(first_stripped) if first_stripped else None,
        "m47_status_label": status,
    }


def classify_ratios(ratios: list[float], first_stripped: list[float], paired: list[dict[str, Any]]) -> str:
    if not ratios:
        return "red_failure"
    metadata_ok = all(
        row.get("fixture_contract_matches") is not False
        and not row.get("current_metadata_failures")
        for row in paired
    )
    if not metadata_ok:
        return "red_failure_watch_row_open"
    stderr_ok = all(row["current_stderr_empty"] and row["v2_14_stderr_empty"] for row in paired)
    all_geo = geomean(ratios)
    med = statistics.median(ratios)
    stripped_geo = geomean(first_stripped)
    pass_count = sum(1 for ratio in ratios if ratio >= 0.95)
    min_ratio = min(ratios)
    if (
        stderr_ok
        and all_geo is not None
        and stripped_geo is not None
        and all_geo >= 0.95
        and med >= 0.95
        and pass_count >= 7
        and min_ratio >= 0.90
        and stripped_geo >= 0.98
    ):
        return "green_closure_candidate_requires_external_review"
    if all_geo is not None and all_geo >= 0.95:
        return "yellow_stability_boundary_watch_row_open"
    return "red_failure_watch_row_open"


def fixture_contract_status(pair: dict[str, dict[str, Any]]) -> dict[str, Any]:
    current_fixture = pair["current"]["payload"].get("fixture")
    v2_fixture = pair["v2_14"]["payload"].get("fixture")
    failures: list[str] = []
    if not isinstance(current_fixture, dict):
        failures.append("current_fixture_missing")
    if not isinstance(v2_fixture, dict):
        failures.append("v2_fixture_missing")
    if failures:
        return {"matches": False, "failures": failures}
    checked_fields = ("dataset", "box_count", "point_query_count", "box_query_count", "seed")
    for field in checked_fields:
        if current_fixture.get(field) != v2_fixture.get(field):
            failures.append(f"fixture_mismatch_{field}")
    current_payload = pair["current"]["payload"]
    v2_payload = pair["v2_14"]["payload"]
    for field in ("mode", "operation"):
        if current_payload.get(field) != v2_payload.get(field):
            failures.append(f"payload_mismatch_{field}")
    return {"matches": not failures, "failures": failures}


def current_metadata_failures(current_row: dict[str, Any]) -> list[str]:
    payload = current_row["payload"]
    failures: list[str] = []
    if payload.get("prepared_execution_session_runner_used") is not True:
        failures.append("prepared_execution_session_runner_used_missing")
    if payload.get("productized_execution_path") != "prepared_execution_session_runner":
        failures.append("productized_execution_path_missing")
    primitive_contract = payload.get("primitive_contract")
    if not isinstance(primitive_contract, str) or not primitive_contract.startswith("generic_prepared_aabb_index_query_2d"):
        failures.append("primitive_contract_missing_or_unexpected")
    metadata = payload.get("prepared_execution_session_runner_metadata")
    if not isinstance(metadata, dict):
        failures.append("prepared_execution_session_runner_metadata_missing")
        return failures
    if metadata.get("set_b_control_candidate") is not True:
        failures.append("set_b_control_candidate_missing")
    if payload.get("mode") == "optix_aabb_index" and metadata.get("prepared_query_mode") != "optix_prepared_query_set":
        failures.append("prepared_query_mode_missing")
    return failures


def geomean(values: list[float]) -> float | None:
    if not values:
        return None
    if any(value <= 0.0 for value in values):
        return None
    return math.exp(sum(math.log(value) for value in values) / len(values))


def build_payload(
    *,
    args: argparse.Namespace,
    schedule: list[dict[str, Any]],
    preflight: dict[str, Any] | None = None,
    scenario_results: dict[str, Any],
    run_errors: dict[str, str],
    status: str,
) -> dict[str, Any]:
    failed_checks = validate_payload(status=status, schedule=schedule, scenario_results=scenario_results, run_errors=run_errors)
    return {
        "schema": SCHEMA,
        "status": status,
        "args": {
            "scenario": str(args.scenario),
            "samples": int(args.samples),
            "seed": int(args.seed),
            "execute": bool(args.execute),
            "run_preflight": bool(args.run_preflight),
            "current_root": str(Path(args.current_root)),
            "v2_root": str(Path(args.v2_root)) if args.v2_root is not None else None,
        },
        "claim_boundary": dict(CLAIM_BOUNDARY),
        "scenarios": SCENARIOS,
        "preflight": preflight if preflight is not None else build_preflight(args),
        "schedule": schedule,
        "scenario_results": scenario_results,
        "run_errors": run_errors,
        "failed_checks": failed_checks,
        "summary": {
            "schema": SCHEMA,
            "status": status,
            "failed_check_count": len(failed_checks),
            "scenario_count": len(selected_scenarios(args)),
            "sample_count_per_scenario": int(args.samples),
            "schedule_row_count": len(schedule),
            "execute": bool(args.execute),
            "run_preflight": bool(args.run_preflight),
            "paid_pod_authorized_by_this_packet": False,
            **CLAIM_BOUNDARY,
        },
        "goal_level_decision_audit": {
            "decision": "prepare an executable M47 LibRTS stability protocol harness without authorizing or running POD",
            "was_i_foolish": "No.",
            "foolish_actions": (
                "The foolish action would be to run focused POD without reviewed "
                "ordering, first-sample, and outlier rules."
            ),
            "other_path": "Rewrite LibRTS/AABB code immediately or run all-app; both are rejected before stability evidence.",
            "different_path_now": "Use this harness as a reviewed dry-run/intake surface, then request one focused run only if external review authorizes it.",
        },
    }


def validate_payload(
    *,
    status: str,
    schedule: list[dict[str, Any]],
    scenario_results: dict[str, Any],
    run_errors: dict[str, str],
) -> list[str]:
    failed: list[str] = []
    if status == STATUS_DRY_RUN and scenario_results:
        failed.append("dry_run_must_not_have_scenario_results")
    if len(schedule) == 0:
        failed.append("schedule_missing")
    if run_errors:
        failed.append("run_errors_present")
    if any(CLAIM_BOUNDARY.values()):
        failed.append("claim_boundary_expanded")
    return failed


def readme(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 M47 LibRTS Stability Protocol Evidence",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This packet does not authorize release, all-app, paid POD, public speedup wording, V4, embedding, C ABI, or true zero-copy.",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(json_ready(payload["summary"]), indent=2, sort_keys=True),
        "```",
        "",
    ]
    return "\n".join(lines)


def json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
