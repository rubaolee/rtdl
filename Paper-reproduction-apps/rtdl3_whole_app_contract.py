"""Shared app-layer contract for private RTDL 3.0 paper-app drivers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import importlib.util
from pathlib import Path
import sys
from typing import Any


SCHEMA = "rtdl.research.v3.paper_app_driver.locked_workload.v1"
REQUIRED_STAGE_KINDS = ("input", "spatial_producer", "action_or_operator", "output")
PAPER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PAPER_ROOT.parent
for _import_root in (REPO_ROOT / "src", REPO_ROOT):
    if str(_import_root) not in sys.path:
        sys.path.insert(0, str(_import_root))


def load_app_module(name: str, path: Path):
    """Load one app-owned module without turning paper-app folders into packages."""

    path = Path(path)
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load app module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def build_locked_workload_driver_result(
    *,
    app: str,
    workload: str,
    requested_execution_mode: str,
    selected_execution: str,
    stages: Sequence[Mapping[str, object]],
    output: object,
    matched: bool,
    source_result: Mapping[str, object],
) -> dict[str, Any]:
    """Build a fail-closed, explicitly bounded V3 app-driver envelope."""

    if not app or not workload:
        raise ValueError("app and workload must be non-empty")
    normalized_stages = tuple(dict(stage) for stage in stages)
    kinds = tuple(str(stage.get("kind", "")) for stage in normalized_stages)
    if kinds != REQUIRED_STAGE_KINDS:
        raise ValueError(
            "driver stages must be exactly input, spatial_producer, "
            "action_or_operator, output"
        )
    for index, stage in enumerate(normalized_stages):
        if not stage.get("name") or not stage.get("owner"):
            raise ValueError(f"stage {index} requires name and owner")
    if not isinstance(matched, bool):
        raise TypeError("matched must be bool")

    return {
        "schema": SCHEMA,
        "app": app,
        "workload": workload,
        "requested_execution_mode": requested_execution_mode,
        "selected_execution": selected_execution,
        "application_selected_backend": False,
        "stages": normalized_stages,
        "output": output,
        "matched": matched,
        "source_result": dict(source_result),
        "v3_end_to_end_driver_present": True,
        "end_to_end_locked_workload_driver_complete": matched,
        "arbitrary_paper_input_supported": False,
        "whole_paper_application_rewritten": False,
        "whole_app_migration_claimed": False,
        "runtime_performance_claimed": False,
        "paper_performance_claimed": False,
        "public_v2_release_claimed": False,
    }


__all__ = (
    "SCHEMA",
    "REQUIRED_STAGE_KINDS",
    "build_locked_workload_driver_result",
    "load_app_module",
)
