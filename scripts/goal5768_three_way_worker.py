#!/usr/bin/env python3
"""One create-only fresh-process endpoint for the Goal5768 cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

from scripts.goal5768_three_way_frontdoors import run_complete


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_plan(path: Path) -> dict[str, object]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    claimed = plan.get("plan_sha256")
    body = dict(plan)
    body.pop("plan_sha256", None)
    actual = hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()
    if claimed != actual:
        raise RuntimeError("formal plan digest mismatch")
    return plan


def run_worker(plan_path: Path, unit_id: str, output_root: Path) -> Path:
    plan_path = plan_path.resolve()
    plan = _load_plan(plan_path)
    units = {str(row["unit_id"]): row for row in plan["units"]}
    if unit_id not in units:
        raise ValueError("worker unit is not in the frozen plan")
    unit = units[unit_id]
    runtime = dict(plan["runtime"])
    frozen_environment = runtime.get("formal_worker_environment")
    if not isinstance(frozen_environment, dict):
        raise RuntimeError("worker plan lacks the frozen Stage-A environment")
    for name, expected in frozen_environment.items():
        observed = os.environ.get(str(name))
        if expected is None:
            if observed is not None:
                raise RuntimeError(f"formal worker environment drift: {name}")
        elif observed != expected:
            raise RuntimeError(f"formal worker environment drift: {name}")
    native_path = Path(str(runtime["native_library_path"])).resolve()
    if not native_path.is_file() or _sha(native_path) != plan["native_library_sha256"]:
        raise RuntimeError("worker native identity mismatch")
    if Path(sys.executable).resolve() != Path(str(plan["python_executable"])).resolve():
        raise RuntimeError("worker Python executable differs from frozen plan")
    if platform.python_version() != plan["python_version"]:
        raise RuntimeError("worker Python version differs from frozen plan")
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native_path)
    os.environ["RTDL_OPTIX_LIB"] = str(native_path)

    unit_root = output_root.resolve() / unit_id
    unit_root.mkdir(parents=True, exist_ok=False)
    started_ns = time.time_ns()
    result = run_complete(
        str(unit["lane_id"]), str(unit["method"]), runtime=runtime)
    completed_ns = time.time_ns()
    payload = {
        "schema": "rtdl.goal5768.three_way_worker.v1",
        "plan_sha256": plan["plan_sha256"],
        "plan_file_sha256": _sha(plan_path),
        "formal_identity_sha256": plan["formal_identity_sha256"],
        "unit": unit,
        "parent_pid": os.getpid(),
        "python_executable": str(Path(sys.executable).resolve()),
        "python_version": platform.python_version(),
        "wall_started_ns": started_ns,
        "wall_completed_ns": completed_ns,
        "wall_seconds": (completed_ns - started_ns) / 1e9,
        "endpoint": result,
    }
    path = unit_root / "RESULT.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--unit-id", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(run_worker(args.plan, args.unit_id, args.output_root))


if __name__ == "__main__":
    main()
