from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


PAPER = {
    "title": "LibRTS: A Spatial Indexing Library by Ray Tracing",
    "venue": "PPoPP 2025",
    "doi": "10.1145/3710848.3710850",
    "authors_code": "https://github.com/RTSpatial/RTSpatial",
}
OPERATIONS = ("point_contains", "range_contains", "range_intersects")
DATASETS = ("tiny", "uniform")
CLAIM_BOUNDARY = (
    "LibRTS-style local correctness and fixture-generation harness only. "
    "This does not reproduce the full paper, has bounded authors-code pod "
    "evidence, does not add native RTDL engine ABI, and does not authorize "
    "public speedup wording."
)


@dataclass(frozen=True)
class Point2D:
    x: float
    y: float

    def to_wkt(self) -> str:
        return f"POINT({self.x:.17g} {self.y:.17g})"


@dataclass(frozen=True)
class Box2D:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def __post_init__(self) -> None:
        if self.max_x < self.min_x or self.max_y < self.min_y:
            raise ValueError(f"invalid box: {self}")

    def contains_point(self, point: Point2D) -> bool:
        return self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y

    def contains_box(self, other: "Box2D") -> bool:
        return (
            self.min_x <= other.min_x
            and self.min_y <= other.min_y
            and self.max_x >= other.max_x
            and self.max_y >= other.max_y
        )

    def intersects_box(self, other: "Box2D") -> bool:
        return (
            other.min_x <= self.max_x
            and other.max_x >= self.min_x
            and other.min_y <= self.max_y
            and other.max_y >= self.min_y
        )

    def to_wkt(self) -> str:
        return (
            "POLYGON(("
            f"{self.min_x:.17g} {self.min_y:.17g},"
            f"{self.max_x:.17g} {self.min_y:.17g},"
            f"{self.max_x:.17g} {self.max_y:.17g},"
            f"{self.min_x:.17g} {self.max_y:.17g},"
            f"{self.min_x:.17g} {self.min_y:.17g}"
            "))"
        )


def parse_point_wkt(line: str) -> Point2D:
    text = line.strip()
    if not text.startswith("POINT(") or not text.endswith(")"):
        raise ValueError(f"unsupported point WKT: {line!r}")
    parts = text[len("POINT(") : -1].split()
    if len(parts) != 2:
        raise ValueError(f"unsupported point WKT coordinate count: {line!r}")
    return Point2D(float(parts[0]), float(parts[1]))


def parse_box_wkt(line: str) -> Box2D:
    text = line.strip()
    if not text.startswith("POLYGON((") or not text.endswith("))"):
        raise ValueError(f"unsupported box WKT: {line!r}")
    points = []
    for pair in text[len("POLYGON((") : -2].split(","):
        parts = pair.split()
        if len(parts) != 2:
            raise ValueError(f"unsupported box WKT coordinate pair: {line!r}")
        points.append((float(parts[0]), float(parts[1])))
    if len(points) < 4:
        raise ValueError(f"box WKT requires at least four points: {line!r}")
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return Box2D(min(xs), min(ys), max(xs), max(ys))


@dataclass(frozen=True)
class LibRTSFixture:
    dataset: str
    boxes: tuple[Box2D, ...]
    point_queries: tuple[Point2D, ...]
    box_queries: tuple[Box2D, ...]
    seed: int
    paper_equivalent_dataset: bool = False

    def metadata(self) -> dict[str, object]:
        return {
            "dataset": self.dataset,
            "box_count": len(self.boxes),
            "point_query_count": len(self.point_queries),
            "box_query_count": len(self.box_queries),
            "seed": self.seed,
            "paper_equivalent_dataset": self.paper_equivalent_dataset,
        }


def _random_box(rng: random.Random, *, max_width: float, max_height: float) -> Box2D:
    min_x = rng.random()
    min_y = rng.random()
    width = rng.random() * max_width
    height = rng.random() * max_height
    return Box2D(min_x, min_y, min(1.0, min_x + width), min(1.0, min_y + height))


def make_uniform_fixture(
    *,
    box_count: int,
    query_count: int,
    seed: int,
    max_box_width: float = 0.5,
    max_box_height: float = 0.5,
    max_query_width: float = 0.1,
    max_query_height: float = 0.1,
) -> LibRTSFixture:
    if box_count < 1 or query_count < 1:
        raise ValueError("box_count and query_count must be positive")
    box_rng = random.Random(seed)
    point_rng = random.Random(seed + 1)
    query_rng = random.Random(seed + 2)
    return LibRTSFixture(
        dataset="uniform",
        boxes=tuple(
            _random_box(box_rng, max_width=max_box_width, max_height=max_box_height)
            for _ in range(box_count)
        ),
        point_queries=tuple(Point2D(point_rng.random(), point_rng.random()) for _ in range(query_count)),
        box_queries=tuple(
            _random_box(query_rng, max_width=max_query_width, max_height=max_query_height)
            for _ in range(query_count)
        ),
        seed=seed,
        paper_equivalent_dataset=False,
    )


def make_tiny_fixture() -> LibRTSFixture:
    return LibRTSFixture(
        dataset="tiny",
        boxes=(
            Box2D(0.0, 0.0, 1.0, 1.0),
            Box2D(0.2, 0.2, 0.8, 0.8),
            Box2D(0.5, -0.5, 1.5, 0.5),
        ),
        point_queries=(
            Point2D(0.1, 0.1),
            Point2D(0.5, 0.5),
            Point2D(0.5, 0.6),
            Point2D(1.0, 1.1),
            Point2D(2.0, 2.0),
        ),
        box_queries=(
            Box2D(0.75, 0.25, 1.25, 0.75),
            Box2D(0.25, 0.25, 0.75, 0.75),
        ),
        seed=0,
        paper_equivalent_dataset=False,
    )


def make_fixture(args: argparse.Namespace) -> LibRTSFixture:
    if args.dataset == "tiny":
        return make_tiny_fixture()
    if args.dataset == "uniform":
        return make_uniform_fixture(
            box_count=args.box_count,
            query_count=args.query_count,
            seed=args.seed,
            max_box_width=args.max_box_width,
            max_box_height=args.max_box_height,
            max_query_width=args.max_query_width,
            max_query_height=args.max_query_height,
        )
    raise ValueError(f"unsupported dataset: {args.dataset}")


def load_wkt_fixture(
    *,
    boxes_path: Path,
    point_queries_path: Path | None = None,
    box_queries_path: Path | None = None,
    seed: int = 0,
) -> LibRTSFixture:
    boxes = tuple(parse_box_wkt(line) for line in _read_nonempty_lines(boxes_path))
    point_queries = (
        tuple(parse_point_wkt(line) for line in _read_nonempty_lines(point_queries_path))
        if point_queries_path is not None
        else ()
    )
    box_queries = (
        tuple(parse_box_wkt(line) for line in _read_nonempty_lines(box_queries_path))
        if box_queries_path is not None
        else ()
    )
    return LibRTSFixture(
        dataset="wkt",
        boxes=boxes,
        point_queries=point_queries,
        box_queries=box_queries,
        seed=seed,
        paper_equivalent_dataset=False,
    )


def _read_nonempty_lines(path: Path) -> tuple[str, ...]:
    return tuple(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def count_point_contains(boxes: Iterable[Box2D], queries: Iterable[Point2D]) -> int:
    return sum(1 for box in boxes for query in queries if box.contains_point(query))


def count_range_contains(boxes: Iterable[Box2D], queries: Iterable[Box2D]) -> int:
    """Count indexed boxes that contain query boxes, matching RTSpatial's shader."""
    return sum(1 for box in boxes for query in queries if box.contains_box(query))


def count_range_intersects(boxes: Iterable[Box2D], queries: Iterable[Box2D]) -> int:
    return sum(1 for box in boxes for query in queries if box.intersects_box(query))


def run_counts(fixture: LibRTSFixture, operation: str) -> dict[str, object]:
    operations = OPERATIONS if operation == "all" else (operation,)
    counts: dict[str, int] = {}
    started = time.perf_counter()
    for name in operations:
        if name == "point_contains":
            counts[name] = count_point_contains(fixture.boxes, fixture.point_queries)
        elif name == "range_contains":
            counts[name] = count_range_contains(fixture.boxes, fixture.box_queries)
        elif name == "range_intersects":
            counts[name] = count_range_intersects(fixture.boxes, fixture.box_queries)
        else:
            raise ValueError(f"unsupported operation: {name}")
    elapsed_sec = time.perf_counter() - started
    return {
        "app": "librts_spatial_index",
        "mode": "cpu_reference",
        "operation": operation,
        "counts": counts,
        "elapsed_sec": elapsed_sec,
        "fixture": fixture.metadata(),
        "semantics": {
            "point_contains": "indexed_box_contains_query_point",
            "range_contains": "indexed_box_contains_query_box",
            "range_intersects": "indexed_box_intersects_query_box",
            "boundary_policy": "inclusive_min_max",
        },
        "paper": PAPER,
        "claim_boundary": CLAIM_BOUNDARY,
        "native_engine_customization": False,
        "authors_code_comparison": False,
        "paper_reproduction": False,
    }


def run_grid_counts(fixture: LibRTSFixture, operation: str, *, resolution: int) -> dict[str, object]:
    primitive_result = rt.query_aabb_index_2d(
        fixture.boxes,
        point_queries=fixture.point_queries,
        box_queries=fixture.box_queries,
        resolution=resolution,
        operation=operation,
    )
    cpu_counts = run_counts(fixture, operation)["counts"]
    return {
        "app": "librts_spatial_index",
        "mode": "partner_grid_reference",
        "operation": operation,
        "generic_primitive": primitive_result["primitive"],
        "primitive_contract": primitive_result["contract"],
        "counts": primitive_result["counts"],
        "matches_cpu_reference": primitive_result["counts"] == cpu_counts,
        "candidate_checks": primitive_result["candidate_checks"],
        "elapsed_sec": primitive_result["run_phases"]["query_aabb_index_2d_sec"],
        "fixture": fixture.metadata(),
        "grid": primitive_result["index"],
        "paper": PAPER,
        "claim_boundary": (
            "LibRTS-style benchmark call into generic CPU AABB_INDEX_QUERY_2D. "
            "This is not RT-core accelerated, not authors-code timing, not a native "
            "Embree/OptiX path, and does not authorize public speedup wording."
        ),
        "native_engine_customization": False,
        "rt_core_accelerated": False,
        "authors_code_comparison": False,
        "paper_reproduction": False,
    }


def run_embree_aabb_counts(fixture: LibRTSFixture, operation: str) -> dict[str, object]:
    prepared_start = time.perf_counter()
    prepared = rt.prepare_aabb_index_2d(
        fixture.boxes,
        point_queries=fixture.point_queries,
        box_queries=fixture.box_queries,
        backend="embree",
    )
    prepare_sec = time.perf_counter() - prepared_start
    try:
        primitive_result = prepared.count(
            point_queries=fixture.point_queries,
            box_queries=fixture.box_queries,
            operation=operation,
        )
    finally:
        prepared.close()
    cpu_counts = run_counts(fixture, operation)["counts"]
    return {
        "app": "librts_spatial_index",
        "mode": "embree_aabb_index",
        "operation": operation,
        "generic_primitive": primitive_result["primitive"],
        "primitive_contract": primitive_result["contract"],
        "counts": primitive_result["counts"],
        "matches_cpu_reference": primitive_result["counts"] == cpu_counts,
        "candidate_checks": primitive_result["candidate_checks"],
        "elapsed_sec": prepare_sec + primitive_result["run_phases"]["query_aabb_index_2d_sec"],
        "fixture": fixture.metadata(),
        "run_phases": {
            "scene_prepare_sec": prepare_sec,
            "query_sec": primitive_result["run_phases"]["query_aabb_index_2d_sec"],
        },
        "index": primitive_result["index"],
        "paper": PAPER,
        "claim_boundary": (
            "LibRTS-style benchmark call into generic Embree AABB_INDEX_QUERY_2D "
            "lowered through app-agnostic columnar conjunctive scan. This is not "
            "authors-code timing, not NVIDIA RT-core accelerated, and does not "
            "authorize public speedup wording."
        ),
        "native_engine_customization": False,
        "rt_core_accelerated": False,
        "authors_code_comparison": False,
        "paper_reproduction": False,
    }


def run_optix_aabb_counts(
    fixture: LibRTSFixture,
    operation: str,
    *,
    prepared_queries: bool = True,
) -> dict[str, object]:
    operations = OPERATIONS if operation == "all" else (operation,)

    started = time.perf_counter()
    prepared = rt.prepare_optix_aabb_index_2d(fixture.boxes)
    scene_prepare_sec = time.perf_counter() - started

    counts: dict[str, int] = {}
    query_prepare_sec: dict[str, float] = {}
    query_sec: dict[str, float] = {}
    prepared_query_cache: dict[str, object] = {}
    try:
        for name in operations:
            if prepared_queries:
                query_kind = "point" if name == "point_contains" else "box"
                if query_kind not in prepared_query_cache:
                    query_started = time.perf_counter()
                    if query_kind == "point":
                        prepared_query_cache[query_kind] = rt.prepare_optix_aabb_point_queries_2d(
                            fixture.point_queries
                        )
                    else:
                        prepared_query_cache[query_kind] = rt.prepare_optix_aabb_box_queries_2d(
                            fixture.box_queries
                        )
                    query_prepare_sec[name] = time.perf_counter() - query_started
                else:
                    query_prepare_sec[name] = 0.0
                run_started = time.perf_counter()
                counts[name] = prepared.count_prepared_queries(prepared_query_cache[query_kind], operation=name)
                query_sec[name] = time.perf_counter() - run_started
            else:
                kwargs = {"operation": name}
                if name == "point_contains":
                    kwargs["point_queries"] = fixture.point_queries
                else:
                    kwargs["box_queries"] = fixture.box_queries
                run_started = time.perf_counter()
                counts[name] = prepared.count(**kwargs)
                query_sec[name] = time.perf_counter() - run_started
                query_prepare_sec[name] = 0.0
    finally:
        for prepared_query in prepared_query_cache.values():
            prepared_query.close()
        prepared.close()

    return {
        "app": "librts_spatial_index",
        "mode": "optix_aabb_index",
        "operation": operation,
        "generic_primitive": "AABB_INDEX_QUERY_2D",
        "primitive_contract": "generic_prepared_aabb_index_query_2d",
        "counts": counts,
        "elapsed_sec": scene_prepare_sec + sum(query_prepare_sec.values()) + sum(query_sec.values()),
        "fixture": fixture.metadata(),
        "run_phases": {
            "scene_prepare_sec": scene_prepare_sec,
            "query_prepare_sec": query_prepare_sec,
            "query_sec": query_sec,
        },
        "prepared_queries": prepared_queries,
        "paper": PAPER,
        "claim_boundary": (
            "Generic RTDL OptiX AABB_INDEX_QUERY_2D count-only path for point_contains, "
            "range_contains, and range_intersects. This is not a LibRTS-specific native symbol."
        ),
        "native_engine_customization": False,
        "rt_core_accelerated": True,
        "authors_code_comparison": False,
        "paper_reproduction": False,
    }


def apply_mutation_scenario(fixture: LibRTSFixture) -> tuple[Box2D, ...]:
    boxes = list(fixture.boxes)
    if len(boxes) >= 2:
        del boxes[1]
    if boxes:
        boxes[0] = Box2D(0.0, 0.0, 0.6, 0.6)
    boxes.append(Box2D(0.4, 0.4, 0.9, 0.9))
    return tuple(boxes)


def run_mutation_counts(fixture: LibRTSFixture, operation: str) -> dict[str, object]:
    mutated = LibRTSFixture(
        dataset=f"{fixture.dataset}_mutated",
        boxes=apply_mutation_scenario(fixture),
        point_queries=fixture.point_queries,
        box_queries=fixture.box_queries,
        seed=fixture.seed,
        paper_equivalent_dataset=False,
    )
    payload = run_counts(mutated, operation)
    payload["mode"] = "mutation_cpu_reference"
    payload["mutation_scenario"] = {
        "delete_ids": [1] if len(fixture.boxes) >= 2 else [],
        "update_ids": [0] if fixture.boxes else [],
        "insert_count": 1,
        "paper_pressure_point": "mutable_index_insert_delete_update",
    }
    return payload


def write_wkt_fixture(fixture: LibRTSFixture, output_dir: Path, *, include_counts: bool) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    box_path = output_dir / "boxes.wkt"
    point_path = output_dir / "point_queries.wkt"
    query_box_path = output_dir / "box_queries.wkt"
    _write_lines(box_path, (box.to_wkt() for box in fixture.boxes))
    _write_lines(point_path, (point.to_wkt() for point in fixture.point_queries))
    _write_lines(query_box_path, (box.to_wkt() for box in fixture.box_queries))

    manifest: dict[str, object] = {
        "app": "librts_spatial_index",
        "mode": "emit_wkt",
        "fixture": fixture.metadata(),
        "files": {
            "boxes": str(box_path),
            "point_queries": str(point_path),
            "box_queries": str(query_box_path),
        },
        "rtspatial_operations": {
            "point_contains": {
                "query_flag": "point_query",
                "predicate": "contains",
            },
            "range_contains": {
                "query_flag": "box_query",
                "predicate": "contains",
            },
            "range_intersects": {
                "query_flag": "box_query",
                "predicate": "intersects",
            },
        },
        "paper": PAPER,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if include_counts:
        manifest["cpu_reference"] = run_counts(fixture, "all")
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest


def _write_lines(path: Path, lines: Iterable[str]) -> None:
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")


def run_scope() -> dict[str, object]:
    return {
        "app": "librts_spatial_index",
        "mode": "scope",
        "paper": PAPER,
        "target_operations": list(OPERATIONS),
        "target_paper_features": [
            "point_query",
            "range_contains_query",
            "range_intersects_query",
            "mutable_insert_delete_update",
            "authors_rtspatial_optix_baseline",
        ],
        "current_local_modes": [
            "scope",
            "cpu_reference",
            "cpu_reference_wkt",
            "partner_grid_reference",
            "embree_aabb_index",
            "optix_aabb_index",
            "mutation_cpu_reference",
            "emit_wkt",
        ],
        "next_pod_modes": [
            "extend authors RTSpatial fixture coverage beyond uniform synthetic rows if needed",
            "repeat RTDL OptiX AABB_INDEX_QUERY_2D evidence on exact paper artifact datasets if available",
            "validate any future prepared-AABB RTDL primitive on NVIDIA",
        ],
        "native_engine_customization": False,
        "authors_code_available": True,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def v2_5_plan_payload() -> dict[str, object]:
    return {
        "app": "librts_spatial_index",
        "paper": PAPER,
        "v2_5_primitive_first_plan": {
            "selected_path": "prepared_generic_aabb_index_query_2d",
            "selected_primitives": ("AABB_INDEX_QUERY_2D",),
            "supported_operations": OPERATIONS,
            "typed_hit_stream_forced": False,
            "partner_continuation_required": False,
            "partner_continuation_reserved_for": (
                "optional grouped summaries outside the prepared AABB query path"
            ),
            "alternative_path": "segmented_count_i64_triton_summary_if_needed",
        },
        "native_engine_boundary": (
            "The native engine sees generic AABB index query contracts. LibRTS "
            "paper metadata, mutable-index experiment framing, and result "
            "interpretation stay in the benchmark app."
        ),
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "triton_speedup_claim_authorized": False,
            "primitive_first_plan_only": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LibRTS-style RTDL spatial-index benchmark harness.")
    parser.add_argument(
        "--mode",
        choices=(
            "scope",
            "cpu_reference",
            "cpu_reference_wkt",
            "partner_grid_reference",
            "embree_aabb_index",
            "optix_aabb_index",
            "mutation_cpu_reference",
            "emit_wkt",
        ),
        default="scope",
    )
    parser.add_argument("--dataset", choices=DATASETS, default="tiny")
    parser.add_argument("--operation", choices=("all", *OPERATIONS), default="all")
    parser.add_argument("--box-count", type=int, default=256)
    parser.add_argument("--query-count", type=int, default=128)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--max-box-width", type=float, default=0.5)
    parser.add_argument("--max-box-height", type=float, default=0.5)
    parser.add_argument("--max-query-width", type=float, default=0.1)
    parser.add_argument("--max-query-height", type=float, default=0.1)
    parser.add_argument("--grid-resolution", type=int, default=32)
    parser.add_argument(
        "--no-prepared-queries",
        action="store_true",
        help="Use host-staged query inputs instead of prepared GPU-resident query buffers for optix_aabb_index.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("scratch/librts_spatial_index_fixture"))
    parser.add_argument("--boxes-wkt", type=Path)
    parser.add_argument("--point-queries-wkt", type=Path)
    parser.add_argument("--box-queries-wkt", type=Path)
    parser.add_argument("--skip-counts", action="store_true", help="Do not run the O(n*m) CPU oracle while emitting WKT.")
    args = parser.parse_args(argv)

    if args.mode == "scope":
        payload = run_scope()
    elif args.mode == "cpu_reference_wkt":
        if args.boxes_wkt is None:
            raise ValueError("--boxes-wkt is required for cpu_reference_wkt")
        fixture = load_wkt_fixture(
            boxes_path=args.boxes_wkt,
            point_queries_path=args.point_queries_wkt,
            box_queries_path=args.box_queries_wkt,
            seed=args.seed,
        )
        payload = run_counts(fixture, args.operation)
        payload["mode"] = "cpu_reference_wkt"
        payload["wkt_inputs"] = {
            "boxes": str(args.boxes_wkt),
            "point_queries": str(args.point_queries_wkt) if args.point_queries_wkt is not None else None,
            "box_queries": str(args.box_queries_wkt) if args.box_queries_wkt is not None else None,
        }
    else:
        fixture = make_fixture(args)
        if args.mode == "cpu_reference":
            payload = run_counts(fixture, args.operation)
        elif args.mode == "partner_grid_reference":
            payload = run_grid_counts(fixture, args.operation, resolution=args.grid_resolution)
        elif args.mode == "embree_aabb_index":
            payload = run_embree_aabb_counts(fixture, args.operation)
        elif args.mode == "optix_aabb_index":
            payload = run_optix_aabb_counts(
                fixture,
                args.operation,
                prepared_queries=not args.no_prepared_queries,
            )
        elif args.mode == "mutation_cpu_reference":
            payload = run_mutation_counts(fixture, args.operation)
        elif args.mode == "emit_wkt":
            payload = write_wkt_fixture(fixture, args.output_dir, include_counts=not args.skip_counts)
        else:
            raise ValueError(f"unsupported mode: {args.mode}")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
