#!/usr/bin/env python3
"""Frozen 312-worker controller for the Goal5768 three-way cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from scripts.goal5768_three_way_frontdoors import LANES, METHODS
from scripts.goal5769_pre_pod_admission import validate_formal_authority_files


METHOD_ORDERS = (
    (METHODS[0], METHODS[1], METHODS[2]),
    (METHODS[0], METHODS[2], METHODS[1]),
    (METHODS[1], METHODS[0], METHODS[2]),
    (METHODS[1], METHODS[2], METHODS[0]),
    (METHODS[2], METHODS[0], METHODS[1]),
    (METHODS[2], METHODS[1], METHODS[0]),
    (METHODS[0], METHODS[1], METHODS[2]),
    (METHODS[1], METHODS[2], METHODS[0]),
)

FORMAL_WORKER_ENVIRONMENT_KEYS = frozenset({
    "PYTHONPATH",
    "PATH",
    "LD_LIBRARY_PATH",
    "NUMBA_CUDA_NVVM",
    "NUMBA_CUDA_LIBDEVICE",
    "RTDL_V4_CUDA_PREFIX",
    "RTDL_V4_OPTIX_PREFIX",
    "RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE",
    "CUDA_VISIBLE_DEVICES",
    "NVIDIA_VISIBLE_DEVICES",
})


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_units() -> tuple[dict[str, object], ...]:
    units = []
    for block_index, order in enumerate(METHOD_ORDERS):
        for lane_index, lane in enumerate(LANES):
            for position, method in enumerate(order):
                units.append({
                    "unit_id": f"b{block_index:02d}__l{lane_index:02d}__p{position}__{method}",
                    "block_index": block_index,
                    "lane_index": lane_index,
                    "lane_id": lane.lane_id,
                    "app": lane.app,
                    "paper_algorithm": lane.paper_algorithm,
                    "position": position,
                    "method": method,
                })
    return tuple(units)


def build_prepared_plan(
    *,
    bundle_sha256: str,
    execution_source_sha256: str,
    execution_tree_sha256: str,
    native_library_sha256: str,
    prepared_identity_sha256: str,
    target_identity_sha256: str,
    python_executable: str,
    python_version: str,
    runtime: dict[str, object],
    lane_contracts: dict[str, dict[str, str]],
) -> dict[str, object]:
    units = build_units()
    scientific = {
        "schema": "rtdl.goal5768.three_way_formal_identity.v1",
        "bundle_sha256": bundle_sha256,
        "execution_source_sha256": execution_source_sha256,
        "execution_tree_sha256": execution_tree_sha256,
        "native_library_sha256": native_library_sha256,
        "prepared_identity_sha256": prepared_identity_sha256,
        "target_identity_sha256": target_identity_sha256,
        "python_executable": str(Path(python_executable).resolve()),
        "python_version": python_version,
        "runtime": runtime,
        "methods": list(METHODS),
        "lane_ids": [lane.lane_id for lane in LANES],
        "method_orders": [list(row) for row in METHOD_ORDERS],
        "units": list(units),
        "lane_contracts": lane_contracts,
        "ratio_direction": "predecessor_over_v4__greater_than_one_favors_v4",
        "independent_rows": 26,
        "cross_row_compensation_allowed": False,
        "fixed_speedup_target_used": False,
        "comparator_inside_registered_timer": False,
    }
    formal_identity = _digest(scientific)
    plan = {
        **scientific,
        "schema": "rtdl.goal5768.three_way_prepared_formal_plan.v1",
        "status": "PREPARED_AWAITING_EXACT_OWNER_FORMAL_AUTHORITY",
        "formal_identity_sha256": formal_identity,
        "expected_worker_count": len(units),
        "expected_unique_parent_pid_count": len(units),
        "pair_count_per_comparison": len(METHOD_ORDERS),
        "required_comparisons": [
            "v2_direct_true_optix_backport_over_v4_restricted_callback_true_optix",
            "v3_compiler_true_optix_over_v4_restricted_callback_true_optix",
        ],
        "retry_resume_replacement_row_dropping_or_relabeling_allowed": False,
        "formal_worker_allowed_without_separate_authority": False,
    }
    plan["plan_sha256"] = _digest(plan)
    validate_plan(plan)
    return plan


def validate_plan(plan: dict[str, object]) -> None:
    body = dict(plan)
    claimed = body.pop("plan_sha256", None)
    if claimed != _digest(body):
        raise RuntimeError("formal plan digest mismatch")
    if plan.get("status") != "PREPARED_AWAITING_EXACT_OWNER_FORMAL_AUTHORITY":
        raise RuntimeError("unexpected formal plan status")
    if plan.get("methods") != list(METHODS):
        raise RuntimeError("formal method set drifted")
    if plan.get("lane_ids") != [lane.lane_id for lane in LANES]:
        raise RuntimeError("formal lane set drifted")
    units = tuple(plan.get("units", ()))
    if len(units) != 13 * 8 * 3 or plan.get("expected_worker_count") != 312:
        raise RuntimeError("formal schedule is not exactly 312 workers")
    if len({row["unit_id"] for row in units}) != len(units):
        raise RuntimeError("formal schedule has duplicate unit IDs")
    for lane in LANES:
        lane_units = [row for row in units if row["lane_id"] == lane.lane_id]
        for method in METHODS:
            if sum(row["method"] == method for row in lane_units) != 8:
                raise RuntimeError("formal schedule is not method-balanced")
    scientific = {
        key: plan[key]
        for key in (
            "schema", "bundle_sha256", "execution_source_sha256",
            "execution_tree_sha256", "native_library_sha256",
            "prepared_identity_sha256", "target_identity_sha256",
            "python_executable", "python_version", "runtime", "methods",
            "lane_ids", "method_orders", "units", "lane_contracts", "ratio_direction",
            "independent_rows", "cross_row_compensation_allowed",
            "fixed_speedup_target_used", "comparator_inside_registered_timer",
        )
    }
    scientific["schema"] = "rtdl.goal5768.three_way_formal_identity.v1"
    if plan.get("formal_identity_sha256") != _digest(scientific):
        raise RuntimeError("formal scientific identity mismatch")
    if plan.get("cross_row_compensation_allowed") is not False:
        raise RuntimeError("cross-row compensation must remain forbidden")
    contracts = plan.get("lane_contracts")
    if not isinstance(contracts, dict) or set(contracts) != set(plan["lane_ids"]):
        raise RuntimeError("formal plan lacks the exact per-lane input/output contracts")
    for lane_id, contract in contracts.items():
        if not isinstance(contract, dict) or set(contract) != {
            "input_sha256", "output_sha256", "expected_sha256",
        } or any(
            not isinstance(value, str) or len(value) != 64
            for value in contract.values()
        ):
            raise RuntimeError(f"formal lane contract is malformed: {lane_id}")
    if plan.get("formal_worker_allowed_without_separate_authority") is not False:
        raise RuntimeError("formal execution authority gate was weakened")
    runtime = plan.get("runtime")
    worker_environment = (
        runtime.get("formal_worker_environment")
        if isinstance(runtime, dict) else None
    )
    if not isinstance(worker_environment, dict) \
            or set(worker_environment) != FORMAL_WORKER_ENVIRONMENT_KEYS:
        raise RuntimeError("formal plan lacks the exact Stage-A worker environment")
    for name, value in worker_environment.items():
        if value is not None and (not isinstance(value, str) or not value):
            raise RuntimeError(f"formal worker environment is malformed: {name}")
    for name in (
        "PYTHONPATH", "PATH", "LD_LIBRARY_PATH", "NUMBA_CUDA_NVVM",
        "NUMBA_CUDA_LIBDEVICE", "RTDL_V4_CUDA_PREFIX",
        "RTDL_V4_OPTIX_PREFIX", "RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE",
    ):
        if not isinstance(worker_environment[name], str) \
                or not worker_environment[name]:
            raise RuntimeError(f"formal worker environment is absent: {name}")


def _formal_worker_environment(plan: dict[str, object]) -> dict[str, str]:
    """Recreate the exact partner/toolchain environment proven by Stage A."""

    runtime = plan["runtime"]
    assert isinstance(runtime, dict)
    frozen = runtime["formal_worker_environment"]
    assert isinstance(frozen, dict)
    environment = os.environ.copy()
    for name in FORMAL_WORKER_ENVIRONMENT_KEYS:
        value = frozen[name]
        if value is None:
            environment.pop(name, None)
        else:
            environment[name] = str(value)
    return environment


def validate_authority(plan: dict[str, object], authority: dict[str, object]) -> None:
    body = dict(authority)
    claimed = body.pop("authority_sha256", None)
    if claimed != _digest(body):
        raise PermissionError("owner authority digest mismatch")
    required_equal = {
        "plan_sha256": plan["plan_sha256"],
        "formal_identity_sha256": plan["formal_identity_sha256"],
        "bundle_sha256": plan["bundle_sha256"],
        "prepared_identity_sha256": plan["prepared_identity_sha256"],
        "target_identity_sha256": plan["target_identity_sha256"],
        "expected_worker_count": 312,
    }
    for name, expected in required_equal.items():
        if authority.get(name) != expected:
            raise PermissionError(f"owner authority {name} mismatch")
    if authority.get("owner_authorized_exact_formal_matrix") is not True:
        raise PermissionError("exact formal matrix lacks owner authorization")
    if not isinstance(authority.get("owner_authorization_text"), str) \
            or "312" not in authority["owner_authorization_text"]:
        raise PermissionError("owner authorization text does not bind 312 workers")
    for name in (
        "repair_allowed", "retry_allowed", "resume_allowed",
        "replacement_allowed", "row_dropping_allowed", "relabeling_allowed",
    ):
        if authority.get(name) is not False:
            raise PermissionError(f"authority must explicitly forbid {name}")


def execute(
    plan_path: Path, authority_path: Path, output_root: Path,
    owner_review_path: Path | None = None,
    review_absorption_path: Path | None = None,
) -> Path:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    validate_plan(plan)
    validate_authority(plan, authority)
    if owner_review_path is None or review_absorption_path is None:
        raise PermissionError("formal execution lacks file-backed owner review")
    validate_formal_authority_files(
        plan, authority, owner_review_path=owner_review_path.resolve(),
        review_absorption_path=review_absorption_path.resolve())
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    logs = output_root / "logs"
    logs.mkdir()
    started = time.time_ns()
    completed = []
    worker = Path(__file__).resolve().with_name("goal5768_three_way_worker.py")
    worker_environment = _formal_worker_environment(plan)
    for unit in plan["units"]:
        command = [
            str(Path(plan["python_executable"]).resolve()), str(worker),
            "--plan", str(plan_path.resolve()),
            "--unit-id", str(unit["unit_id"]),
            "--output-root", str(output_root / "raw"),
        ]
        result = subprocess.run(
            command, text=True, capture_output=True, check=False,
            env=worker_environment)
        (logs / f"{unit['unit_id']}.stdout.txt").write_text(
            result.stdout, encoding="utf-8")
        (logs / f"{unit['unit_id']}.stderr.txt").write_text(
            result.stderr, encoding="utf-8")
        if result.returncode != 0:
            failure = {
                "schema": "rtdl.goal5768.formal_terminal_failure.v1",
                "unit": unit,
                "returncode": result.returncode,
                "completed_unit_count": len(completed),
                "retry_or_resume_allowed": False,
            }
            (output_root / "TERMINAL_FAILURE.json").write_text(
                json.dumps(failure, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
            raise RuntimeError(
                f"formal unit {unit['unit_id']} failed terminally; no retry/resume")
        completed.append(str(unit["unit_id"]))
    receipt = {
        "schema": "rtdl.goal5768.formal_controller_receipt.v1",
        "plan_sha256": plan["plan_sha256"],
        "authority_sha256": authority["authority_sha256"],
        "formal_identity_sha256": plan["formal_identity_sha256"],
        "started_ns": started,
        "completed_ns": time.time_ns(),
        "completed_unit_count": len(completed),
        "expected_unit_count": 312,
        "retry_resume_replacement_row_dropping_or_relabeling_used": False,
    }
    path = output_root / "CONTROLLER_RECEIPT.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--owner-review", type=Path, required=True)
    parser.add_argument("--review-absorption", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(execute(
        args.plan, args.authority, args.output_root,
        args.owner_review, args.review_absorption))


if __name__ == "__main__":
    main()
