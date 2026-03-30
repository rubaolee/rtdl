from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from .api import compile_kernel
from .baseline_contracts import BASELINE_WORKLOADS
from .baseline_contracts import compare_baseline_rows
from .baseline_contracts import validate_compiled_kernel_against_baseline
from .datasets import chains_to_polygon_refs
from .datasets import chains_to_probe_points
from .datasets import chains_to_segments
from .datasets import load_cdb
from .embree_runtime import run_embree
from .reference import Point
from .reference import Polygon
from .reference import Ray2D
from .reference import Segment
from .reference import Triangle
from .runtime import run_cpu

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DatasetCase:
    workload: str
    dataset: str
    inputs: dict[str, tuple[object, ...]]
    note: str


def infer_workload(kernel_fn_or_compiled) -> str:
    compiled = (
        kernel_fn_or_compiled
        if hasattr(kernel_fn_or_compiled, "refine_op")
        else compile_kernel(kernel_fn_or_compiled)
    )
    predicate = compiled.refine_op.predicate.name
    mapping = {
        "segment_intersection": "lsi",
        "point_in_polygon": "pip",
        "overlay_compose": "overlay",
        "ray_triangle_hit_count": "ray_tri_hitcount",
    }
    return mapping[predicate]


def representative_dataset_names(workload: str) -> tuple[str, ...]:
    return BASELINE_WORKLOADS[workload].representative_datasets


def load_representative_case(workload: str, dataset: str) -> DatasetCase:
    if workload == "lsi":
        return _load_lsi_case(dataset)
    if workload == "pip":
        return _load_pip_case(dataset)
    if workload == "overlay":
        return _load_overlay_case(dataset)
    if workload == "ray_tri_hitcount":
        return _load_ray_case(dataset)
    raise ValueError(f"unknown baseline workload `{workload}`")


def run_baseline_case(kernel_fn_or_compiled, dataset: str, backend: str = "both") -> dict[str, object]:
    compiled = (
        kernel_fn_or_compiled
        if hasattr(kernel_fn_or_compiled, "refine_op")
        else compile_kernel(kernel_fn_or_compiled)
    )
    workload = infer_workload(compiled)
    case = load_representative_case(workload, dataset)
    bound_inputs = _bind_case_inputs(case, compiled)

    payload: dict[str, object] = {
        "workload": workload,
        "dataset": dataset,
        "note": case.note,
    }
    if backend in {"cpu", "both"}:
        payload["cpu_rows"] = run_cpu(compiled, **bound_inputs)
    if backend in {"embree", "both"}:
        payload["embree_rows"] = run_embree(compiled, **bound_inputs)
    if backend == "both":
        payload["parity"] = compare_baseline_rows(
            workload,
            payload["cpu_rows"],
            payload["embree_rows"],
        )
    return payload


def _load_lsi_case(dataset: str) -> DatasetCase:
    if dataset == "authored_lsi_minimal":
        return DatasetCase(
            workload="lsi",
            dataset=dataset,
            inputs={
                "left": (
                    Segment(id=1, x0=0.0, y0=0.0, x1=2.0, y1=2.0),
                    Segment(id=2, x0=2.0, y0=0.0, x1=2.0, y1=2.0),
                ),
                "right": (
                    Segment(id=10, x0=0.0, y0=2.0, x1=2.0, y1=0.0),
                ),
            },
            note="Small authored segment intersection example.",
        )
    if dataset == "tests/fixtures/rayjoin/br_county_subset.cdb":
        county = load_cdb(ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb")
        segments = chains_to_segments(county)
        return DatasetCase(
            workload="lsi",
            dataset=dataset,
            inputs={"left": tuple(segments[0:3]), "right": tuple(segments[24:27])},
            note="Deterministic county-subset segment slice chosen to preserve CPU/Embree parity.",
        )
    raise ValueError(f"unsupported lsi dataset `{dataset}`")


def _load_pip_case(dataset: str) -> DatasetCase:
    if dataset == "authored_pip_minimal":
        return DatasetCase(
            workload="pip",
            dataset=dataset,
            inputs={
                "points": (
                    Point(id=100, x=0.5, y=0.5),
                    Point(id=101, x=3.0, y=3.0),
                ),
                "polygons": (
                    Polygon(id=200, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
                ),
            },
            note="Small authored point-in-polygon example.",
        )
    if dataset == "tests/fixtures/rayjoin/br_county_subset.cdb":
        county = load_cdb(ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb")
        polygons = _chains_to_polygons(county, limit_chains=2)
        return DatasetCase(
            workload="pip",
            dataset=dataset,
            inputs={
                "points": chains_to_probe_points(county),
                "polygons": polygons,
            },
            note="County subset probe points against deterministic chain-derived polygons.",
        )
    raise ValueError(f"unsupported pip dataset `{dataset}`")


def _load_overlay_case(dataset: str) -> DatasetCase:
    if dataset == "authored_overlay_minimal":
        return DatasetCase(
            workload="overlay",
            dataset=dataset,
            inputs={
                "left": (
                    Polygon(id=300, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
                ),
                "right": (
                    Polygon(id=301, vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))),
                ),
            },
            note="Small authored overlay seed example.",
        )
    if dataset == "tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb":
        county = load_cdb(ROOT / "tests" / "fixtures" / "rayjoin" / "br_county_subset.cdb")
        soil = load_cdb(ROOT / "tests" / "fixtures" / "rayjoin" / "br_soil_subset.cdb")
        return DatasetCase(
            workload="overlay",
            dataset=dataset,
            inputs={
                "left": _chains_to_polygons(county, limit_chains=2),
                "right": _chains_to_polygons(soil, limit_chains=2),
            },
            note="County and soil subset chain-derived polygons for overlay seed generation.",
        )
    raise ValueError(f"unsupported overlay dataset `{dataset}`")


def _load_ray_case(dataset: str) -> DatasetCase:
    from examples.rtdl_ray_tri_hitcount import make_center_rays
    from examples.rtdl_ray_tri_hitcount import make_random_triangles

    if dataset == "authored_ray_tri_minimal":
        return DatasetCase(
            workload="ray_tri_hitcount",
            dataset=dataset,
            inputs={
                "rays": (
                    Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
                    Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=2.0),
                ),
                "triangles": (
                    Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
                    Triangle(id=11, x0=6.0, y0=-1.0, x1=7.0, y1=1.0, x2=8.0, y2=-1.0),
                    Triangle(id=12, x0=-1.0, y0=3.0, x1=1.0, y1=3.0, x2=0.0, y2=4.0),
                ),
            },
            note="Small authored ray-vs-triangle example.",
        )
    if dataset == "examples/rtdl_ray_tri_hitcount.py synthetic random generators":
        return DatasetCase(
            workload="ray_tri_hitcount",
            dataset=dataset,
            inputs={
                "rays": make_center_rays(12, seed=19),
                "triangles": make_random_triangles(20, seed=17),
            },
            note="Synthetic random rays and triangles from the canonical example helpers.",
        )
    raise ValueError(f"unsupported ray_tri_hitcount dataset `{dataset}`")


def _chains_to_polygons(cdb, *, limit_chains: int | None = None) -> tuple[Polygon, ...]:
    chains = cdb.chains if limit_chains is None else cdb.chains[:limit_chains]
    polygons = []
    for chain in chains:
        if len(chain.points) < 3:
            continue
        vertices = tuple((point.x, point.y) for point in chain.points)
        polygons.append(Polygon(id=chain.chain_id, vertices=vertices))
    return tuple(polygons)


def _bind_case_inputs(case: DatasetCase, compiled) -> dict[str, tuple[object, ...]]:
    remaining = {
        key: list(value)
        for key, value in case.inputs.items()
    }
    bound: dict[str, tuple[object, ...]] = {}
    for item in compiled.inputs:
        exact = remaining.get(item.name)
        if exact is not None:
            bound[item.name] = tuple(exact)
            del remaining[item.name]
            continue

        match_key = None
        for key, value in remaining.items():
            if not value:
                continue
            sample = value[0]
            if item.geometry.name == "segments" and isinstance(sample, Segment):
                match_key = key
                break
            if item.geometry.name == "points" and isinstance(sample, Point):
                match_key = key
                break
            if item.geometry.name == "polygons" and isinstance(sample, Polygon):
                match_key = key
                break
            if item.geometry.name == "triangles" and isinstance(sample, Triangle):
                match_key = key
                break
            if item.geometry.name == "rays" and isinstance(sample, Ray2D):
                match_key = key
                break
        if match_key is None:
            raise ValueError(
                f"unable to bind representative dataset `{case.dataset}` to input `{item.name}` "
                f"for workload `{case.workload}`"
            )
        bound[item.name] = tuple(remaining.pop(match_key))
    return bound


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if hasattr(value, "__dict__") and getattr(value, "__dataclass_fields__", None):
        return {key: _json_ready(val) for key, val in value.__dict__.items()}
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run RTDL Embree baseline workloads.")
    parser.add_argument("workload", choices=BASELINE_WORKLOADS.keys())
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--backend", choices=("cpu", "embree", "both"), default="both")
    args = parser.parse_args(argv)

    dataset = args.dataset or representative_dataset_names(args.workload)[0]

    if args.workload == "lsi":
        from examples.rtdl_language_reference import county_zip_join_reference as kernel
    elif args.workload == "pip":
        from examples.rtdl_language_reference import point_in_counties_reference as kernel
    elif args.workload == "overlay":
        from examples.rtdl_language_reference import county_soil_overlay_reference as kernel
    else:
        from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference as kernel

    payload = run_baseline_case(kernel, dataset, backend=args.backend)
    print(json.dumps(_json_ready(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
