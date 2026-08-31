from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "src" / "rtdsl").exists()
)
SRC = ROOT / "src"
RAYJOIN_APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper"
for path in (ROOT, SRC, RAYJOIN_APP, RAYJOIN_APP.parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rtdsl.datasets import CdbChain, CdbDataset, CdbPoint, write_cdb  # noqa: E402


Point = tuple[Fraction, Fraction]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _square_grid(
    *,
    name: str,
    columns: int,
    rows: int,
    spacing: Fraction,
    side: Fraction,
    offset_x: Fraction,
    offset_y: Fraction,
    face_base: int,
) -> CdbDataset:
    chains: list[CdbChain] = []
    point_id = 1
    chain_id = 1
    for row in range(rows):
        for column in range(columns):
            x0 = Fraction(column) * spacing + offset_x
            y0 = Fraction(row) * spacing + offset_y
            ring = (
                (x0, y0),
                (x0 + side, y0),
                (x0 + side, y0 + side),
                (x0, y0 + side),
                (x0, y0),
            )
            points = tuple(
                CdbPoint(x=float(x), y=float(y))
                for x, y in ring
            )
            chains.append(
                CdbChain(
                    chain_id=chain_id,
                    point_count=len(points),
                    first_point_id=point_id,
                    last_point_id=point_id + len(points) - 1,
                    left_face_id=face_base + chain_id,
                    right_face_id=0,
                    points=points,
                )
            )
            point_id += len(points)
            chain_id += 1
    return CdbDataset(name=name, chains=tuple(chains))


def authored_subdivisions() -> tuple[CdbDataset, CdbDataset]:
    """Return two non-paper closed planar subdivisions with proper crossings."""

    left = _square_grid(
        name="goal5654_authored_left_subdivision",
        columns=3,
        rows=2,
        spacing=Fraction(4),
        side=Fraction(3),
        offset_x=Fraction(0),
        offset_y=Fraction(0),
        face_base=1_000,
    )
    right = _square_grid(
        name="goal5654_authored_right_subdivision",
        columns=3,
        rows=2,
        spacing=Fraction(4),
        side=Fraction(3),
        offset_x=Fraction(5, 4),
        offset_y=Fraction(5, 4),
        face_base=2_000,
    )
    return left, right


def _fraction_point(point: CdbPoint) -> Point:
    return Fraction(str(point.x)), Fraction(str(point.y))


def _ring(chain: CdbChain) -> tuple[Point, ...]:
    points = tuple(_fraction_point(point) for point in chain.points)
    if len(points) < 4 or points[0] != points[-1]:
        raise ValueError("authored topology reference requires a closed ring")
    return points


def _cross(a: Point, b: Point) -> Fraction:
    return a[0] * b[1] - a[1] * b[0]


def _subtract(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1]


def _add_scaled(origin: Point, direction: Point, scale: Fraction) -> Point:
    return (
        origin[0] + direction[0] * scale,
        origin[1] + direction[1] * scale,
    )


def _proper_segment_intersection(
    a0: Point,
    a1: Point,
    b0: Point,
    b1: Point,
) -> tuple[Fraction, Point] | None:
    """Return the exact parameter/point for one non-collinear closed crossing."""

    ar = _subtract(a1, a0)
    br = _subtract(b1, b0)
    denominator = _cross(ar, br)
    if denominator == 0:
        return None
    delta = _subtract(b0, a0)
    ta = _cross(delta, br) / denominator
    tb = _cross(delta, ar) / denominator
    if ta < 0 or ta > 1 or tb < 0 or tb > 1:
        return None
    return ta, _add_scaled(a0, ar, ta)


def _strict_point_in_ring(point: Point, ring: tuple[Point, ...]) -> bool:
    """Exact odd-even containment; authored fixtures avoid boundary queries."""

    x, y = point
    inside = False
    for start, end in zip(ring, ring[1:]):
        x0, y0 = start
        x1, y1 = end
        cross = _cross(_subtract(end, start), _subtract(point, start))
        if cross == 0 and min(x0, x1) <= x <= max(x0, x1) and min(y0, y1) <= y <= max(y0, y1):
            raise ValueError("authored reference encountered an ambiguous boundary point")
        if (y0 > y) != (y1 > y):
            crossing_x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if crossing_x > x:
                inside = not inside
    return inside


def _face_at(point: Point, dataset: CdbDataset) -> int:
    matches = [
        int(chain.left_face_id)
        for chain in dataset.chains
        if _strict_point_in_ring(point, _ring(chain))
    ]
    if len(matches) > 1:
        raise ValueError("authored subdivision contains overlapping same-map faces")
    return matches[0] if matches else 0


def _edge_intersections(
    start: Point,
    end: Point,
    other: CdbDataset,
) -> tuple[tuple[Fraction, Point], ...]:
    by_point: dict[Point, Fraction] = {}
    for chain in other.chains:
        ring = _ring(chain)
        for other_start, other_end in zip(ring, ring[1:]):
            hit = _proper_segment_intersection(
                start,
                end,
                other_start,
                other_end,
            )
            if hit is None:
                continue
            parameter, point = hit
            previous = by_point.get(point)
            if previous is not None and previous != parameter:
                raise ValueError("one exact intersection acquired conflicting parameters")
            by_point[point] = parameter
    return tuple(
        sorted(
            ((parameter, point) for point, parameter in by_point.items()),
            key=lambda item: (item[0], item[1][0], item[1][1]),
        )
    )


def _append_deduplicated(points: list[Point], point: Point) -> None:
    if not points or points[-1] != point:
        points.append(point)


def _reference_side_groups(
    current: CdbDataset,
    other: CdbDataset,
) -> tuple[tuple[int, int, int], ...]:
    """Independently assemble exact boundary groups for one directed side."""

    groups: list[tuple[int, int, int]] = []
    for chain in current.chains:
        ring = _ring(chain)
        local_label = int(chain.left_face_id)
        current_points: list[Point] = []
        other_label = 0

        def flush() -> None:
            if current_points and local_label != 0 and other_label != 0:
                groups.append((local_label, other_label, len(current_points)))
            current_points.clear()

        for point_index, point in enumerate(ring):
            other_label = _face_at(point, other)
            _append_deduplicated(current_points, point)
            if point_index == len(ring) - 1:
                continue
            hits = _edge_intersections(point, ring[point_index + 1], other)
            if not hits:
                continue
            _append_deduplicated(current_points, hits[0][1])
            for left_hit, right_hit in zip(hits, hits[1:]):
                flush()
                midpoint = (
                    (left_hit[1][0] + right_hit[1][0]) / 2,
                    (left_hit[1][1] + right_hit[1][1]) / 2,
                )
                other_label = _face_at(midpoint, other)
                _append_deduplicated(current_points, left_hit[1])
                _append_deduplicated(current_points, right_hit[1])
            flush()
            _append_deduplicated(current_points, hits[-1][1])
        flush()
    return tuple(groups)


def independent_reference_rows(
    left: CdbDataset,
    right: CdbDataset,
) -> tuple[dict[str, int], ...]:
    aggregate: dict[tuple[int, int], list[int]] = defaultdict(lambda: [0, 0])
    for label_a, label_b, point_rows in (
        *_reference_side_groups(left, right),
        *_reference_side_groups(right, left),
    ):
        values = aggregate[(label_a, label_b)]
        values[0] += 1
        values[1] += point_rows
    return tuple(
        {
            "label_a": label_a,
            "label_b": label_b,
            "group_count": values[0],
            "point_row_count": values[1],
        }
        for (label_a, label_b), values in sorted(aggregate.items())
    )


def _slice_dataset(dataset: CdbDataset, index: int) -> CdbDataset:
    chain = dataset.chains[index]
    return CdbDataset(
        name=f"{dataset.name}_chain_{index}",
        chains=(chain,),
    )


def _canonical_rows_sha256(rows: tuple[dict[str, int], ...]) -> str:
    return hashlib.sha256(
        json.dumps(
            rows,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def run(*, work_dir: Path) -> dict[str, object]:
    """Execute the real six-batch producer and compare an independent reference."""

    work_dir.mkdir(parents=True, exist_ok=True)
    left, right = authored_subdivisions()
    left_path = write_cdb(left, work_dir / "goal5654_authored_left.cdb")
    right_path = write_cdb(right, work_dir / "goal5654_authored_right.cdb")

    whole = _load(
        "goal5654_authored_planar_map_whole_app",
        RAYJOIN_APP / "rtdl3_whole_app.py",
    )
    args = whole.prepared_six_batch_args(
        left_path,
        right_path,
        lsi_capacity=4_096,
        pair_name="goal5654_authored_planar_map_boundary_coverage",
    )
    # This is genericity/correctness evidence, not a timing result.  Observe
    # the pre-existing device validator before and after the new consumer so a
    # disagreement cannot be hidden, while the exact Fraction CPU assembly
    # below remains the correctness oracle for the authored input.
    args.collect_complete_descriptor_pair_rows_for_validation = False
    inner_consumer = whole._migration.prepared_descriptor_action_consumer(
        max_event_rows=4_096,
        collect_phase_trace=True,
        validate_against_v2=False,
    )
    device_validator_observations: list[dict[str, object]] = []

    class _ObservedRealProducerConsumer:
        def begin_producer_owned_device_batch(self, *, capacity: int):
            return inner_consumer.begin_producer_owned_device_batch(
                capacity=capacity
            )

        def __call__(self, carrier):
            before = whole._pipeline.descriptor_pair_rows_projected_device(
                carrier
            )
            actual = inner_consumer(carrier)
            after = whole._pipeline.descriptor_pair_rows_projected_device(
                carrier
            )
            device_validator_observations.append(
                {
                    "before": tuple(before["pair_rows"]),
                    "after": tuple(after["pair_rows"]),
                    "stable_across_consumer": (
                        tuple(before["pair_rows"])
                        == tuple(after["pair_rows"])
                    ),
                }
            )
            return actual

    try:
        protocol = whole._pipeline.run_pipeline_repeat_protocol(
            args,
            descriptor_consumer=_ObservedRealProducerConsumer(),
        )
        prepared_metadata = inner_consumer.to_metadata()
    finally:
        inner_consumer.close()
    measured = tuple(protocol["measured_rows"])
    if len(measured) != len(left.chains):
        raise RuntimeError(
            f"expected {len(left.chains)} real producer batches, got {len(measured)}"
        )

    comparisons = []
    for batch_index, row in enumerate(measured):
        expected = independent_reference_rows(
            _slice_dataset(left, batch_index),
            right,
        )
        actual = tuple(row["descriptor_pair_rows"])
        certificate = row.get("descriptor_device_event_batch_certificate")
        if actual != expected:
            raise RuntimeError(
                f"independent topology reference mismatch for batch {batch_index}"
            )
        if (
            not isinstance(certificate, dict)
            or certificate.get("binding_kind")
            != "compiler_preallocated_single_consume_device_batch"
            or certificate.get("state") != "consumed"
            or certificate.get("sorted_payload_permutation_used") is not False
            or certificate.get("order_indexed_checked_scan_used") is not True
        ):
            raise RuntimeError(
                f"batch {batch_index} did not use the Goal5654 compiler-owned path"
            )
        comparisons.append(
            {
                "batch_index": batch_index,
                "exact_rows": actual,
                "row_sha256": _canonical_rows_sha256(actual),
                "matched_independent_cpu_reference": True,
                "preexisting_device_validator": (
                    device_validator_observations[batch_index]
                ),
                "producer_owned_certificate": certificate,
            }
        )

    return {
        "schema": "rtdl.goal5654.authored_planar_map_boundary_coverage.v1",
        "consumer": "authored_planar_map_boundary_coverage",
        "paper_or_cdb_fixture_used": False,
        "preconstructed_carrier_columns_used": False,
        "same_spatial_producer_region": (
            "lsi",
            "intersection_reprojection",
            "intersection_sort_and_run_bounds",
            "midpoint_point_location",
            "group_formation",
        ),
        "authored_inputs": {
            "left": {
                "name": left.name,
                "chain_count": len(left.chains),
                "chains": tuple(asdict(chain) for chain in left.chains),
            },
            "right": {
                "name": right.name,
                "chain_count": len(right.chains),
                "chains": tuple(asdict(chain) for chain in right.chains),
            },
        },
        "independent_reference": (
            "exact_fraction_segment_crossings_plus_odd_even_face_location_"
            "plus_cpu_boundary_group_assembly"
        ),
        "batch_count": len(comparisons),
        "all_batches_exact": all(
            row["matched_independent_cpu_reference"]
            for row in comparisons
        ),
        "all_batches_used_same_compiler_region": all(
            row["producer_owned_certificate"]["order_indexed_checked_scan_used"]
            for row in comparisons
        ),
        "comparisons": tuple(comparisons),
        "selected_backend": prepared_metadata["prepared"][
            "identity"
        ]["selected_backend"],
        "selected_template": prepared_metadata["prepared"][
            "identity"
        ]["selected_template"],
        "preexisting_device_validator_is_correctness_oracle": False,
        "preexisting_device_validator_disagreements_are_preserved": True,
        "claim_boundary": {
            "genericity_behavioral_evidence": True,
            "paper_performance_claimed": False,
            "rayjoin_performance_claimed": False,
            "goal5648_rewritten": False,
            "pod_result_claimed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run(work_dir=args.work_dir.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
