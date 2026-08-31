#!/usr/bin/env python3
"""Create-only controller for the exact 208-worker Goal5774 matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import os
import subprocess
import sys

from goal5774_prepared_three_way_frontdoors import LANES, METHODS


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def schedule():
    rows = []
    for lane in LANES:
        for block in range(8):
            order = METHODS if block % 2 == 0 else tuple(reversed(METHODS))
            for ordinal, method in enumerate(order):
                rows.append({
                    "worker_index": len(rows),
                    "lane_id": lane.lane_id,
                    "method": method,
                    "block_index": block,
                    "order_ordinal": ordinal,
                })
    if len(rows) != 208:
        raise AssertionError("Goal5774 schedule must contain 208 workers")
    return tuple(rows)


def run(*, runtime: Path, output_root: Path, authorization: Path) -> Path:
    if output_root.exists():
        raise FileExistsError(output_root)
    authority = json.loads(authorization.read_text(encoding="utf-8"))
    authority_body = dict(authority)
    claimed_authority_sha256 = authority_body.pop("authority_sha256", None)
    if claimed_authority_sha256 != _digest(authority_body):
        raise PermissionError("Goal5774 owner authority digest mismatch")
    expected = {
        "schema", "bundle_sha256", "prepared_identity_sha256",
        "target_identity_sha256", "formal_identity_sha256",
        "expected_worker_count", "expected_independent_row_count",
        "owner_authorized_exactly_once", "repair_retry_resume_allowed",
        "v3_worker_allowed", "authority_sha256",
    }
    if set(authority) != expected:
        raise PermissionError("Goal5774 exact authority schema is absent")
    if (
        authority["schema"] != "rtdl.goal5774.owner_formal_authority.v1"
        or authority["owner_authorized_exactly_once"] is not True
        or authority["repair_retry_resume_allowed"] is not False
        or authority["v3_worker_allowed"] is not False
        or authority["expected_worker_count"] != 208
        or authority["expected_independent_row_count"] != 26
    ):
        raise PermissionError("Goal5774 exact owner authority is absent")
    runtime_payload = json.loads(runtime.read_text(encoding="utf-8"))
    for key in (
        "bundle_sha256", "prepared_identity_sha256", "target_identity_sha256",
        "formal_identity_sha256",
    ):
        if str(runtime_payload.get(key)) != str(authority[key]):
            raise PermissionError(f"Goal5774 authority mismatch: {key}")
    frozen_environment = runtime_payload.get("formal_worker_environment")
    if not isinstance(frozen_environment, dict):
        raise PermissionError("Goal5774 runtime lacks frozen worker environment")
    required_environment = (
        "PYTHONPATH", "PATH", "RTDL_V4_OPTIX_PREFIX",
        "RTDL_V4_CUDA_PREFIX", "RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE",
        "RTDL_OPTIX_LIB", "RTDL_OPTIX_LIBRARY",
    )
    if any(not isinstance(frozen_environment.get(name), str)
           or not frozen_environment[name] for name in required_environment):
        raise PermissionError("Goal5774 frozen worker environment is incomplete")
    worker_environment = dict(os.environ)
    worker_environment.update({
        name: value for name, value in frozen_environment.items()
        if isinstance(value, str) and value
    })
    output_root.mkdir(parents=False)
    rows = schedule()
    (output_root / "SCHEDULE.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    worker_dir = output_root / "workers"
    worker_dir.mkdir()
    worker = Path(__file__).with_name("goal5774_prepared_v2_v4_worker.py")
    for row in rows:
        destination = worker_dir / f'{row["worker_index"]:03d}.json'
        command = [
            sys.executable, str(worker), "--lane-id", row["lane_id"],
            "--method", row["method"], "--block-index", str(row["block_index"]),
            "--runtime", str(runtime), "--output", str(destination),
        ]
        completed = subprocess.run(command, check=False, env=worker_environment)
        if completed.returncode != 0:
            raise RuntimeError(
                f'Goal5774 worker {row["worker_index"]} failed terminally')
    receipt = {
        "schema": "rtdl.goal5774.prepared_v2_v4_controller_receipt.v1",
        "worker_count": len(rows),
        "schedule_sha256": _sha(output_root / "SCHEDULE.json"),
        "runtime_sha256": _sha(runtime),
        "authorization_sha256": _sha(authorization),
        "retry_resume_or_replacement_used": False,
        "v3_worker_count": 0,
    }
    path = output_root / "CONTROLLER_RECEIPT.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    args = parser.parse_args()
    print(run(runtime=args.runtime, output_root=args.output_root,
              authorization=args.authorization))


if __name__ == "__main__":
    main()
