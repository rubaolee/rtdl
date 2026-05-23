from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any


GOAL = "goal2525_gpu_database_candidate_gate"
CLAIM_BOUNDARY = (
    "This is an environment and candidate-readiness gate for possible GPU database baselines. "
    "It does not run a GPU database benchmark and does not authorize public speedup, "
    "whole-DBMS, authors-code, RayDB reproduction, true zero-copy, or GPU-database claims."
)


PYTHON_PACKAGE_CANDIDATES = (
    "cudf",
    "pylibcudf",
    "cupy",
    "numba",
    "pyarrow",
    "duckdb",
)
COMMAND_CANDIDATES = (
    "nvidia-smi",
    "heavydb",
    "omnisci_server",
    "crystal",
)


def run_gate() -> dict[str, Any]:
    gpu_probe = _run_command(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])
    package_status = {
        name: _python_package_status(name) for name in PYTHON_PACKAGE_CANDIDATES
    }
    command_status = {name: _command_status(name) for name in COMMAND_CANDIDATES}
    candidate_decisions = {
        "postgresql": {
            "role": "SQL correctness oracle and CPU DBMS diagnostic timing",
            "status": "already_selected_by_goal2522_goal2523",
            "reason": "available on the pod after apt install and directly expresses the exact fixture contract",
        },
        "duckdb": {
            "role": "quick embedded analytical SQL baseline",
            "status": "already_selected_by_goal2524",
            "reason": "installable in an isolated Python venv and directly expresses the exact fixture contract",
        },
        "rapids_cudf": {
            "role": "first plausible GPU dataframe/database-like baseline",
            "status": "defer_to_dedicated_install_goal",
            "reason": (
                "cuDF/pylibcudf is not preinstalled in this pod. Installing RAPIDS is large, "
                "CUDA/Python-version sensitive, and should be a separate goal if we need a GPU baseline."
            ),
        },
        "heavydb_or_omnisci": {
            "role": "server-style GPU database candidate",
            "status": "not_quick_for_goal2525",
            "reason": "no server command is installed; bringing up a server would be a separate database project",
        },
        "crystal": {
            "role": "user-mentioned possible GPU database",
            "status": "not_available_on_pod",
            "reason": "no `crystal` command or Python package candidate was available in the pod probe",
        },
    }
    return {
        "goal": GOAL,
        "status": "ok",
        "app": "raydb_style_columnar_aggregate",
        "gpu_probe": gpu_probe,
        "python_package_status": package_status,
        "command_status": command_status,
        "candidate_decisions": candidate_decisions,
        "selected_next_absolute_baselines": ["postgresql_diagnostic", "duckdb_quick_baseline"],
        "gpu_database_timing_available_now": False,
        "recommended_first_gpu_database_candidate": "rapids_cudf",
        "recommended_next_gpu_goal": (
            "Create a dedicated RAPIDS/cuDF install-and-contract goal only if a GPU DB-like baseline "
            "is still worth the setup cost after PostgreSQL and DuckDB diagnostics."
        ),
        "performance_claim_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _python_package_status(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return {"available": False, "version": None}
    version = None
    try:
        module = __import__(name)
        version = getattr(module, "__version__", None)
    except Exception as exc:
        return {"available": True, "version": None, "import_error": repr(exc)}
    return {"available": True, "version": version}


def _command_status(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return {"available": path is not None, "path": path}


def _run_command(command: list[str]) -> dict[str, Any]:
    path = shutil.which(command[0])
    if path is None:
        return {"available": False, "command": command, "stdout": "", "stderr": "command not found"}
    completed = subprocess.run(command, text=True, check=False, capture_output=True)
    return {
        "available": completed.returncode == 0,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal2525 GPU database candidate gate.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = run_gate()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
