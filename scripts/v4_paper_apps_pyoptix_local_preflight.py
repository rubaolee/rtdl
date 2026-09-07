#!/usr/bin/env python3
"""Create-only static authority before the V4/PyOptiX GPU dry run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STORED_MANIFEST = (
    ROOT / "history/internal_docs/v4_paper_apps_pyoptix_20260907/SOURCE_MANIFEST.json"
)
FOCUSED_TESTS = (
    "tests.v4_paper_apps_pyoptix_contract_test",
    "tests.v4_paper_apps_pyoptix_owners_test",
    "tests.v4_paper_apps_pyoptix_harness_test",
)
EXPERIMENT_SCRIPTS = (
    "scripts/build_v4_paper_apps_source_manifest.py",
    "scripts/v4_paper_apps_pyoptix_controller.py",
    "scripts/v4_paper_apps_pyoptix_extract_data.py",
    "scripts/v4_paper_apps_pyoptix_local_preflight.py",
    "scripts/v4_paper_apps_pyoptix_make_config.py",
    "scripts/v4_paper_apps_pyoptix_prepare_ptx.py",
    "scripts/v4_paper_apps_pyoptix_recount.py",
    "scripts/v4_paper_apps_pyoptix_worker.py",
)
BASELINE_MODULES = (
    "examples/current/research_benchmarks/triangle_counting/segmented_rt_graph.py",
    "experiments/goal5814_particle/public_pyoptix_owner.py",
    "experiments/v4_paper_apps_pyoptix/contracts.py",
    "experiments/v4_paper_apps_pyoptix/inputs.py",
    "experiments/v4_paper_apps_pyoptix/librts_owner.py",
    "experiments/v4_paper_apps_pyoptix/particle_adapter.py",
    "experiments/v4_paper_apps_pyoptix/public_runtime.py",
    "experiments/v4_paper_apps_pyoptix/triangle_owner.py",
)
DEVICE_ENTRIES = {
    "experiments/v4_paper_apps_pyoptix/particle_device.cu": (
        "__raygen__rtdl_particle_strict_interior",
        "__closesthit__rtdl_particle_strict_interior",
        "__miss__rtdl_particle_strict_interior",
    ),
    "experiments/v4_paper_apps_pyoptix/triangle_counting_device.cu": (
        "__raygen__paper_triangle_count",
        "__anyhit__paper_triangle_count",
        "__miss__paper_triangle_count",
    ),
    "experiments/v4_paper_apps_pyoptix/librts_device.cu": (
        "__raygen__paper_librts_count",
        "__intersection__paper_librts_count",
        "__miss__paper_librts_count",
    ),
}


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def _source_checks() -> dict[str, Any]:
    from experiments.v4_paper_apps_pyoptix.contracts import APP_SPECS
    from scripts.build_v4_paper_apps_source_manifest import build_manifest

    generated = json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n"
    stored = STORED_MANIFEST.read_text(encoding="utf-8")
    if generated != stored:
        raise RuntimeError("stored recovered-source manifest differs")
    if len(APP_SPECS) != 9:
        raise RuntimeError("paper-app denominator differs from nine")

    hashes = {}
    for relative in (*EXPERIMENT_SCRIPTS, *BASELINE_MODULES, *DEVICE_ENTRIES):
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        hashes[relative] = _sha(path)

    for relative in EXPERIMENT_SCRIPTS:
        if not os.access(ROOT / relative, os.X_OK):
            raise PermissionError(f"experiment script lacks execute bit: {relative}")

    for relative in BASELINE_MODULES:
        source = (ROOT / relative).read_text(encoding="utf-8")
        if "import rtdsl" in source or "from rtdsl" in source:
            raise RuntimeError(f"PyOptiX baseline imports RTDL: {relative}")

    for relative, entries in DEVICE_ENTRIES.items():
        source = (ROOT / relative).read_text(encoding="utf-8")
        for entry in entries:
            if source.count(entry) != 1:
                raise RuntimeError(f"device entry count differs: {relative}:{entry}")
        if "rtdl_optix" in source:
            raise RuntimeError(
                f"device baseline references RTDL native engine: {relative}"
            )

    return {
        "application_count": len(APP_SPECS),
        "source_manifest_sha256": _sha(STORED_MANIFEST),
        "executable_source_sha256": hashes,
    }


def _schedule_checks() -> dict[str, Any]:
    from scripts import v4_paper_apps_pyoptix_controller as controller

    worker_count = (
        len(controller.UNITS)
        * len(controller.ENDPOINTS)
        * len(controller.BLOCK_ORDERS)
        * 2
    )
    if (
        len(controller.UNITS) != 4
        or len(controller.ENDPOINTS) != 3
        or len(controller.BLOCK_ORDERS) != 8
        or worker_count != 192
        or sum(order[0] == "v4" for order in controller.BLOCK_ORDERS) != 4
        or sum(order[0] == "pyoptix" for order in controller.BLOCK_ORDERS) != 4
    ):
        raise RuntimeError("first-batch formal schedule differs")
    return {
        "registered_unit_count": len(controller.UNITS),
        "endpoint_count": len(controller.ENDPOINTS),
        "paired_block_count_per_unit_endpoint": len(controller.BLOCK_ORDERS),
        "formal_worker_process_count": worker_count,
        "fixed_block_orders": [list(order) for order in controller.BLOCK_ORDERS],
    }


def _run_tests() -> dict[str, Any]:
    environment = dict(os.environ)
    python_path = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT)]
    if environment.get("PYTHONPATH"):
        python_path.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(python_path)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", *FOCUSED_TESTS],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            "focused V4/PyOptiX tests failed:\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return {
        "command": [sys.executable, "-m", "unittest", *FOCUSED_TESTS],
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def build_preflight() -> dict[str, Any]:
    source = _source_checks()
    schedule = _schedule_checks()
    tests = _run_tests()
    dirty = _git("status", "--porcelain")
    return {
        "schema": "rtdl.v4_paper_apps_pyoptix.local_preflight.v1",
        "status": "PASS__LOCAL_STATIC_ONLY__GPU_DRY_RUN_REQUIRED",
        "source_commit": _git("rev-parse", "HEAD"),
        "source_tree": _git("rev-parse", "HEAD^{tree}"),
        "working_tree_clean": not bool(dirty),
        "source": source,
        "schedule": schedule,
        "tests": tests,
        "gpu_used": False,
        "formal_worker_zero_reached": False,
        "performance_result_exists": False,
        "public_or_manuscript_claim_authorized": False,
    }


def _write_create(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = build_preflight()
    _write_create(args.output, result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "formal_worker_process_count": result["schedule"][
                    "formal_worker_process_count"
                ],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
