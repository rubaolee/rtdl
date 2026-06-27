#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.current.research_benchmarks.spatial_rayjoin import (  # noqa: E402
    rtdl_rayjoin_v2_spatial_join_app as rayjoin_app,
)


SCHEMA = "rtdl.phoenix_v3.spatial_rayjoin_topology_stream_m3_pod_evidence.v1"
AUTHORIZATION_TOKEN = "M66_SOURCE_SIGNATURE_GATED_TOPOLOGY_STREAM_M3_POD_AUTHORIZED"
AUTHORIZED_EXECUTION_TOKENS = (AUTHORIZATION_TOKEN,)
STATUS_DRY_RUN = "spatial_rayjoin_topology_stream_m3_dry_run_no_pod_not_m7"
STATUS_PREFLIGHT_ONLY = "spatial_rayjoin_topology_stream_m3_preflight_only_no_pod_not_m7"
STATUS_NOT_M7 = "spatial_rayjoin_topology_stream_m3_pod_evidence_pending_review_not_m7"
STATUS_FAILED = "spatial_rayjoin_topology_stream_m3_pod_evidence_failed_not_release"
M3_CONTRACT = "topology_stream_m3_phase_table_v1"
HANDLE_CONTRACT = "topology_stream_prepared_handle_v1"
PREFLIGHT_TEST_MODULES = (
    "tests.v3_phoenix_prepared_execution_session_runner_test",
    "tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test",
    "tests.v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner_test",
    "tests.v3_phoenix_m65_topology_stream_step3_audit_negative_hardening_gate_test",
)
M3_PHASES = (
    "static_scene_prepare_sec",
    "query_stream_prepare_sec",
    "device_transfer_or_residency_sec",
    "rt_traversal_sec",
    "topology_continuation_sec",
    "host_return_or_scalar_materialization_sec",
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
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
runner_path = root / "scripts" / "v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py"
prepared = prepared_path.read_text(encoding="utf-8")
app = app_path.read_text(encoding="utf-8")
runner = runner_path.read_text(encoding="utf-8")
checks = {
    "point_topology_runner_present": "def run_point_location_topology_stream_prepared_session" in prepared,
    "segment_topology_runner_present": "def run_segment_intersection_topology_stream_prepared_session" in prepared,
    "m3_bridge_helper_present": "def _topology_stream_m3_bridge_metadata" in prepared,
    "step3_audit_bridge_gate_present": "complete_non_authorizing_topology_stream_m3_bridge" in prepared,
    "rayjoin_app_emits_m3_table": "topology_stream_m3_phase_table" in app,
    "rayjoin_app_emits_prepared_handle": "topology_stream_prepared_handle" in app,
    "runner_uses_m66_token": "M66_SOURCE_SIGNATURE_GATED_TOPOLOGY_STREAM_M3_POD_AUTHORIZED" in runner,
    "runner_runs_preflight": "execute_preflight(args)" in runner,
}
failed = [name for name, passed in checks.items() if not passed]
print(json.dumps({"checks": checks, "failed": failed}, indent=2, sort_keys=True))
raise SystemExit(1 if failed else 0)
""".strip()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.current_root = Path(args.current_root).resolve()
    if not bool(args.execute):
        if bool(args.run_preflight):
            preflight, preflight_errors = execute_preflight(args)
            payload = build_dry_run_packet(
                args,
                preflight=preflight,
                preflight_errors=preflight_errors,
                status=STATUS_PREFLIGHT_ONLY if not preflight_errors else STATUS_FAILED,
            )
        else:
            payload = build_dry_run_packet(args)
    else:
        if str(args.authorization_token) not in AUTHORIZED_EXECUTION_TOKENS:
            raise SystemExit(
                "Spatial RayJoin topology-stream M3 execution requires explicit "
                "external authorization token; run without --execute for dry-run"
            )
        preflight, preflight_errors = execute_preflight(args)
        if preflight_errors:
            payload = build_dry_run_packet(
                args,
                preflight=preflight,
                preflight_errors=preflight_errors,
                status=STATUS_FAILED,
            )
        else:
            payload = run_packet(args, preflight=preflight)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Phoenix V3 Spatial RayJoin topology-stream M3 OptiX evidence."
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", default="tests/fixtures/rayjoin/br_county_subset.cdb")
    parser.add_argument(
        "--count-mode",
        choices=(
            "exact_prepared_points",
            "exact_prepared_points_executor",
            "relation_status_corrected_executor_validated",
            "device_filtered_prepared_points_validated",
        ),
        default="exact_prepared_points_executor",
    )
    parser.add_argument("--point-order-mode", default="morton_xy")
    parser.add_argument("--query-repeat", type=int, default=50)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--sample-repeat", type=int, default=3)
    parser.add_argument(
        "--exact-executor-max-candidate-rows",
        type=int,
        default=0,
        help="Max candidate rows for exact_prepared_points_executor; 0 lets the app choose a fail-closed auto capacity.",
    )
    parser.add_argument("--require-full-m3", action="store_true", default=True)
    parser.add_argument("--current-root", type=Path, default=ROOT)
    parser.add_argument("--current-python", default=sys.executable)
    parser.add_argument("--command-timeout-sec", type=float, default=600.0)
    parser.add_argument("--run-preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--authorization-token", default="")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def build_dry_run_packet(
    args: argparse.Namespace,
    *,
    preflight: dict[str, Any] | None = None,
    preflight_errors: dict[str, str] | None = None,
    status: str = STATUS_DRY_RUN,
) -> dict[str, Any]:
    errors = dict(preflight_errors or {})
    failed_checks = [f"preflight_{name}" for name in errors]
    return {
        "schema": SCHEMA,
        "status": status,
        "execute": bool(args.execute),
        "planned_execution_requires_token": AUTHORIZATION_TOKEN,
        "planned_args": {
            "dataset": str(args.dataset),
            "count_mode": str(args.count_mode),
            "point_order_mode": str(args.point_order_mode),
            "query_repeat": int(args.query_repeat),
            "warmup": int(args.warmup),
            "sample_repeat": int(args.sample_repeat),
            "exact_executor_max_candidate_rows": int(args.exact_executor_max_candidate_rows),
            "require_full_m3": bool(args.require_full_m3),
        },
        "generic_capability": "point_location_topology_stream",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "summary": {
            "execute": bool(args.execute),
            "run_preflight": bool(args.run_preflight) or preflight is not None,
            "sample_repeat": int(args.sample_repeat),
            "requires_explicit_authorization": True,
            "release_authorized": False,
            "all_app_pod_spend_authorized": False,
            "focused_pod_spend_authorized_now": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "failed_checks": failed_checks,
        },
        "preflight": preflight if preflight is not None else build_preflight(args),
        "preflight_errors": errors,
        "failed_checks": failed_checks,
        "goal_level_decision_audit": {
            "decision": "Make the Spatial RayJoin topology-stream M3 runner dry-run by default.",
            "was_i_foolish": "No.",
            "foolish_actions": (
                "The foolish action would be leaving a POD runner executable from "
                "the CLI while M49 says RayJoin route tuning and POD are blocked."
            ),
            "other_path": "Rely on instructions in docs. That is weaker than a fail-closed CLI gate.",
            "different_path_now": "Require --execute plus an explicit review token before any real run.",
        },
    }


def build_preflight(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "nvidia_smi": {
            "command": ["nvidia-smi"],
            "cwd": str(args.current_root),
            "required": True,
        },
        "current_python_version": {
            "command": [str(args.current_python), "--version"],
            "cwd": str(args.current_root),
            "required": True,
        },
        "current_git_revision": {
            "command": ["git", "rev-parse", "HEAD"],
            "cwd": str(args.current_root),
            "required": False,
        },
        "current_topology_stream_source_signature": {
            "command": [
                str(args.current_python),
                "-c",
                CURRENT_SOURCE_SIGNATURE_SCRIPT,
                str(args.current_root),
            ],
            "cwd": str(args.current_root),
            "required": True,
        },
        "current_preflight_tests": {
            "command": [str(args.current_python), "-m", "unittest", *PREFLIGHT_TEST_MODULES],
            "cwd": str(args.current_root),
            "required": True,
        },
    }


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
    output_prefix = args.output.with_suffix("")
    for name, row in build_preflight(args).items():
        stdout_path = output_prefix.parent / f"{output_prefix.name}.preflight_{name}.stdout.txt"
        stderr_path = output_prefix.parent / f"{output_prefix.name}.preflight_{name}.stderr.txt"
        print(f"[phoenix-v3-spatial-m3] preflight={name}", flush=True)
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
                errors[name] = f"exit_code={completed.returncode}"
        except Exception as exc:  # pragma: no cover - environment dependent.
            results[name] = {
                "command": list(row["command"]),
                "cwd": str(row["cwd"]),
                "required": bool(row["required"]),
                "error": repr(exc),
            }
            if bool(row["required"]):
                errors[name] = repr(exc)
    return results, errors


def run_packet(args: argparse.Namespace, *, preflight: dict[str, Any] | None = None) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    for index in range(int(args.sample_repeat)):
        print(
            f"[phoenix-v3-spatial-m3] sample {index + 1}/{int(args.sample_repeat)}",
            flush=True,
        )
        start = time.perf_counter()
        payload = rayjoin_app.run_rayjoin_prepared_optix_workload(
            "pip",
            dataset=str(args.dataset),
            result_mode="count",
            include_rows=False,
            count_mode=str(args.count_mode),
            point_order_mode=str(args.point_order_mode),
            query_repeat=int(args.query_repeat),
            warmup=int(args.warmup),
            exact_executor_max_candidate_rows=(
                int(args.exact_executor_max_candidate_rows)
                if int(args.exact_executor_max_candidate_rows) > 0
                else None
            ),
        )
        wall_sec = time.perf_counter() - start
        validate_sample(payload, require_full_m3=bool(args.require_full_m3))
        samples.append(
            {
                "sample_index": index,
                "runner_wall_sec": wall_sec,
                "row_count": int(payload["row_count"]),
                "output_contract": payload["summary"]["output_contract"],
                "phases_sec": payload["phases_sec"],
                "native_phase_timings": payload["native_phase_timings"],
                "topology_stream_m3_phase_table": payload["topology_stream_m3_phase_table"],
                "topology_stream_prepared_handle": payload["topology_stream_prepared_handle"],
                "claim_boundary": payload["claim_boundary"],
                "device_resident_continuation_status": payload["device_resident_continuation_status"],
            }
        )

    checks = build_checks(samples, require_full_m3=bool(args.require_full_m3))
    failed_checks = [name for name, ok in checks.items() if not ok]
    return {
        "schema": SCHEMA,
        "status": "fail" if failed_checks else STATUS_NOT_M7,
        "execute": True,
        "workload": "pip",
        "backend": "optix",
        "dataset": str(args.dataset),
        "count_mode": str(args.count_mode),
        "point_order_mode": str(args.point_order_mode),
        "query_repeat": int(args.query_repeat),
        "warmup": int(args.warmup),
        "sample_repeat": int(args.sample_repeat),
        "exact_executor_max_candidate_rows": int(args.exact_executor_max_candidate_rows),
        "generic_capability": "point_location_topology_stream",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_claim_authorized": False,
        "m7_promotion_authorized": False,
        "m7_qualified_release_rows_added": 0,
        "summary": summarize(samples),
        "preflight": preflight if preflight is not None else build_preflight(args),
        "preflight_errors": {},
        "checks": checks,
        "failed_checks": failed_checks,
        "samples": samples,
        "environment": {
            "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
            "git_dirty": (_command_output(["git", "status", "--short"]) or "").splitlines(),
            "nvidia_smi": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        },
        "goal_level_decision_audit": {
            "decision": "Collect a focused Spatial RayJoin topology-stream M3 POD packet without promoting M7.",
            "was_i_foolish": (
                "No. The runner verifies the new generic table/handle surface before any speedup wording."
            ),
            "foolish_actions": (
                "The foolish action would be to run another ad hoc Spatial RayJoin benchmark that omits "
                "M3 phases or silently authorizes public claims."
            ),
            "other_path": (
                "Use the older Goal3244 runner directly. That preserves useful comparisons, but it does "
                "not force the Phoenix M3 table/handle contract."
            ),
            "different_path_now": (
                "Use this focused packet as the next POD evidence intake, then judge it against wall, "
                "phase, parity, and external-review gates."
            ),
        },
    }


def validate_sample(payload: dict[str, Any], *, require_full_m3: bool) -> None:
    table = payload.get("topology_stream_m3_phase_table")
    handle = payload.get("topology_stream_prepared_handle")
    if not isinstance(table, dict) or table.get("contract") != M3_CONTRACT:
        raise RuntimeError("payload did not emit topology_stream_m3_phase_table_v1")
    if not isinstance(handle, dict) or handle.get("contract") != HANDLE_CONTRACT:
        raise RuntimeError("payload did not emit topology_stream_prepared_handle_v1")
    if require_full_m3 and not bool(table.get("full_m3_phase_table_complete")):
        raise RuntimeError(f"M3 phase table is incomplete: {table.get('missing_m3_phases_for_public_row')}")
    if not bool(handle.get("query_stream_prepared")):
        raise RuntimeError("prepared handle does not report a prepared query stream")
    for key in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "row_scoped_public_speedup_claim_authorized",
        "m7_promotion_authorized",
        "true_zero_copy_claim_authorized",
    ):
        if bool(table.get(key)) or bool(handle.get(key)):
            raise RuntimeError(f"topology stream sample illegally authorized {key}")
    summary = dict(payload.get("summary") or {})
    if int(payload.get("row_count", -1)) != int(summary.get("validation_exact_count", payload.get("row_count", -2))):
        raise RuntimeError("row_count does not match validation_exact_count")


def build_checks(samples: list[dict[str, Any]], *, require_full_m3: bool) -> dict[str, bool]:
    return {
        "samples_collected": len(samples) > 0,
        "counts_consistent": len({int(sample["row_count"]) for sample in samples}) == 1,
        "all_m3_contracts_present": all(
            sample["topology_stream_m3_phase_table"]["contract"] == M3_CONTRACT
            for sample in samples
        ),
        "all_prepared_handle_contracts_present": all(
            sample["topology_stream_prepared_handle"]["contract"] == HANDLE_CONTRACT
            for sample in samples
        ),
        "all_full_m3_when_required": (
            all(sample["topology_stream_m3_phase_table"]["full_m3_phase_table_complete"] for sample in samples)
            if require_full_m3
            else True
        ),
        "all_query_stream_prepared": all(
            sample["topology_stream_prepared_handle"]["query_stream_prepared"] for sample in samples
        ),
        "all_public_claim_flags_false": all(
            not bool(sample["topology_stream_m3_phase_table"].get("public_speedup_claim_authorized"))
            and not bool(sample["topology_stream_prepared_handle"].get("public_speedup_claim_authorized"))
            and not bool(sample["topology_stream_m3_phase_table"].get("m7_promotion_authorized"))
            and not bool(sample["topology_stream_prepared_handle"].get("m7_promotion_authorized"))
            for sample in samples
        ),
    }


def summarize(samples: list[dict[str, Any]]) -> dict[str, Any]:
    phase_medians = {
        phase: _median(
            [
                sample["topology_stream_m3_phase_table"]["phase_seconds"][phase]
                for sample in samples
                if sample["topology_stream_m3_phase_table"]["phase_seconds"][phase] is not None
            ]
        )
        for phase in M3_PHASES
    }
    return {
        "row_count": samples[-1]["row_count"] if samples else None,
        "row_count_consistent": len({int(sample["row_count"]) for sample in samples}) <= 1,
        "runner_wall_sec_median": _median([float(sample["runner_wall_sec"]) for sample in samples]),
        "prepared_query_sec_median": _median(
            [float(sample["phases_sec"]["prepared_query_sec"]) for sample in samples]
        ),
        "prepared_query_total_sec_median": _median(
            [
                float(sample["phases_sec"].get("prepared_query_sec_total_sec", sample["phases_sec"]["prepared_query_sec"]))
                for sample in samples
            ]
        ),
        "m3_phase_sec_medians": phase_medians,
        "full_m3_phase_table_complete_all_samples": all(
            sample["topology_stream_m3_phase_table"]["full_m3_phase_table_complete"]
            for sample in samples
        ),
        "query_stream_residency": (
            samples[-1]["topology_stream_prepared_handle"]["query_stream_residency"] if samples else None
        ),
        "m7_rows_added": 0,
    }


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _command_output(command: list[str]) -> str | None:
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
