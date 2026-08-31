#!/usr/bin/env python3
"""One untimed-for-claims three-way functional admission worker.

The selected application front door still reports its complete endpoint time,
but this worker permanently marks that observation as functional smoke only.
It is not a formal worker and may never enter a performance cohort.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

from scripts.goal5768_three_way_frontdoors import run_complete


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_smoke(
    *,
    lane_id: str,
    method: str,
    runtime_path: Path,
    output: Path,
) -> Path:
    if output.exists():
        raise FileExistsError(output)
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    native = Path(str(runtime["native_library_path"])).resolve()
    if not native.is_file() or _sha(native) != runtime["native_library_sha256"]:
        raise RuntimeError("functional smoke native identity mismatch")
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    endpoint = run_complete(lane_id, method, runtime=runtime)
    payload = {
        "schema": "rtdl.goal5768.three_way_functional_smoke.v1",
        "lane_id": lane_id,
        "method": method,
        "parent_pid": os.getpid(),
        "python_executable": str(Path(sys.executable).resolve()),
        "python_version": platform.python_version(),
        "runtime_sha256": hashlib.sha256(runtime_path.read_bytes()).hexdigest(),
        "endpoint": endpoint,
        "formal_worker": False,
        "registered_performance_observation": False,
        "timing_present_for_cost_estimation_only": True,
        "performance_interpretation_allowed": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane-id", required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(run_smoke(
        lane_id=args.lane_id,
        method=args.method,
        runtime_path=args.runtime,
        output=args.output,
    ))


if __name__ == "__main__":
    main()
