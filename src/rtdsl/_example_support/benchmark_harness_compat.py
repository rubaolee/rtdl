from __future__ import annotations

import importlib.util
from pathlib import Path
import runpy
import sys
from types import ModuleType


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_ARCHIVE_ROOT = ROOT / "tools" / "_archive" / "history" / "v4_0_benchmark_harness_archive_2026-06-27"

_ARCHIVED_HARNESSES = {
    "rt_dbscan": "examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
    "rtnn": "examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py",
    "triangle_counting": "examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
    "robot_collision": "examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py",
    "raydb_style": "examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py",
    "librts_spatial_index": "examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
    "contact_manifold": "examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py",
    "spatial_rayjoin": "examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py",
    "barnes_hut": "examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py",
    "hausdorff_xhd": "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
    "hausdorff_v2_function": "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_function.py",
    "hausdorff_v2_language_lab": "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py",
    "hausdorff_v2_user_benchmark": "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py",
}


def archived_harness_path(key: str) -> Path:
    try:
        relative = _ARCHIVED_HARNESSES[key]
    except KeyError as exc:
        raise ValueError(f"unknown archived benchmark harness: {key}") from exc
    path = _ARCHIVE_ROOT / relative
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def load_archived_harness_module(key: str, module_name: str) -> ModuleType:
    path = archived_harness_path(key)
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load archived benchmark harness {key} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_archived_harness(key: str, args: list[str] | None = None) -> int:
    path = archived_harness_path(key)
    forwarded = list(args or sys.argv[1:])
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]
    sys.argv = [str(path), *forwarded]
    runpy.run_path(str(path), run_name="__main__")
    return 0
