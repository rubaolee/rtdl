"""V3 paper-app front door for both required RT-Graph algorithms."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


APP_DIR = Path(__file__).resolve().parent


def _load_migration():
    name = "goal5725_triangle_counting_action_migration"
    if name in sys.modules:
        return sys.modules[name]
    path = APP_DIR / "rtdl3_action_migration.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_v3(
    *,
    paper_algorithm: str,
    fixture: str = "degree_oriented_two_triangles",
    edge_file: str | None = None,
    edge_format: str = "text",
    partner: str = "none",
):
    return _load_migration().run_v3_algorithm(
        paper_algorithm=paper_algorithm,
        fixture=fixture,
        edge_file=edge_file,
        edge_format=edge_format,
        partner=partner,
        require_optix=True,
    )


__all__ = ["run_v3"]
