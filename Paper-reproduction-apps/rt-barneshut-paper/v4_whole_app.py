"""Application-owned V4 complete endpoint for RT-BarnesHut."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from dataclasses import dataclass

import numpy as np

from rtdsl import (
    aggregate_frontier_reduce_execution_contract_3d,
    aggregate_frontier_reduce_reference_3d,
)

from rtdsl.v4_hierarchy_frontier import (
    HierarchyFrontierSchema,
    HierarchyReducer,
    compile_hierarchy_frontier,
    execute_hierarchy_frontier,
    hierarchy_content_sha256,
    prepare_hierarchy_frontier,
)

APP_DIR = Path(__file__).resolve().parent


def _adapter_module():
    name = "rtdl_v4_rt_barneshut_prepared_adapter"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = APP_DIR / "aggregate_hierarchy_adapter.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _fixture_module():
    name = "rtdl_v4_rt_barneshut_fixture"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = APP_DIR / "v4_fixture.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_force_rows(rows):
    return tuple({
        "source_id": int(row["source_id"]),
        "scalar_force": float(format(float(row["scalar_force"]), ".9g")),
    } for row in rows)


def _canonical_force_rows_from_values(values, *, force_scale: float):
    """Project one generic scalar column to the app's frozen row contract."""

    raw = np.asarray(values, dtype=np.float64)
    scale = float(force_scale)
    if raw.ndim != 1 or not np.isfinite(scale):
        raise RuntimeError("malformed Barnes-Hut force projection")
    scaled = raw * scale
    if not np.isfinite(scaled).all():
        raise RuntimeError("non-finite Barnes-Hut force projection")
    canonical_values = np.empty(scaled.size, dtype=np.float64)
    output = []
    for source_id, value in enumerate(scaled):
        canonical = float(format(float(value), ".9g"))
        canonical_values[source_id] = canonical
        output.append({"source_id": source_id, "scalar_force": canonical})
    frozen_values = np.frombuffer(
        canonical_values.tobytes(order="C"), dtype=np.dtype("<f8"),
    )
    return tuple(output), frozen_values


FORCE_RELATIVE_TOLERANCE = 1.0e-5
FORCE_ABSOLUTE_TOLERANCE = 1.0e-5


def _compare_force_rows(actual, expected):
    """Apply the app's frozen same-input floating force contract."""

    if len(actual) != len(expected):
        return {
            "matched": False, "mismatch_count": max(len(actual), len(expected)),
            "maximum_abs_delta": float("inf"),
            "maximum_rel_delta": float("inf"),
        }
    maximum_abs_delta = 0.0
    maximum_rel_delta = 0.0
    mismatch_count = 0
    for left, right in zip(actual, expected, strict=True):
        if int(left["source_id"]) != int(right["source_id"]):
            mismatch_count += 1
            continue
        lhs = float(left["scalar_force"])
        rhs = float(right["scalar_force"])
        absolute = abs(lhs - rhs)
        denominator = max(abs(lhs), abs(rhs), 1.0)
        relative = absolute / denominator
        maximum_abs_delta = max(maximum_abs_delta, absolute)
        maximum_rel_delta = max(maximum_rel_delta, relative)
        if absolute > FORCE_ABSOLUTE_TOLERANCE + FORCE_RELATIVE_TOLERANCE * denominator:
            mismatch_count += 1
    return {
        "matched": mismatch_count == 0,
        "mismatch_count": mismatch_count,
        "maximum_abs_delta": maximum_abs_delta,
        "maximum_rel_delta": maximum_rel_delta,
    }


def _force_value_column(rows):
    values = np.empty(len(rows), dtype=np.float64)
    for source_id, row in enumerate(rows):
        if int(row["source_id"]) != source_id:
            raise ValueError("force rows must be dense and source-ordered")
        values[source_id] = float(row["scalar_force"])
    if not np.isfinite(values).all():
        raise ValueError("force rows must be finite")
    return np.frombuffer(values.tobytes(order="C"), dtype=np.dtype("<f8"))


def _compare_force_value_columns(actual_values, expected_values):
    """Vectorized equivalent of the complete app-owned row comparator."""

    actual = np.asarray(actual_values, dtype=np.float64)
    expected = np.asarray(expected_values, dtype=np.float64)
    if actual.ndim != 1 or expected.ndim != 1 or actual.size != expected.size:
        return {
            "matched": False,
            "mismatch_count": max(int(actual.size), int(expected.size)),
            "maximum_abs_delta": float("inf"),
            "maximum_rel_delta": float("inf"),
        }
    if not np.isfinite(actual).all() or not np.isfinite(expected).all():
        return {
            "matched": False,
            "mismatch_count": int(actual.size),
            "maximum_abs_delta": float("inf"),
            "maximum_rel_delta": float("inf"),
        }
    absolute = np.abs(actual - expected)
    denominator = np.maximum(np.maximum(np.abs(actual), np.abs(expected)), 1.0)
    relative = absolute / denominator
    mismatch = absolute > (
        FORCE_ABSOLUTE_TOLERANCE + FORCE_RELATIVE_TOLERANCE * denominator
    )
    return {
        "matched": not bool(np.any(mismatch)),
        "mismatch_count": int(np.count_nonzero(mismatch)),
        "maximum_abs_delta": float(np.max(absolute, initial=0.0)),
        "maximum_rel_delta": float(np.max(relative, initial=0.0)),
    }


def _read_force_rows(path: Path):
    rows = []
    for index, raw in enumerate(path.read_text(encoding="utf-8").splitlines()):
        text = raw.strip()
        if not text:
            continue
        fields = text.split()
        if len(fields) != 2:
            raise ValueError(f"invalid force row {index}: {text!r}")
        source_id, value = int(fields[0]), float(fields[1])
        if source_id != len(rows):
            raise ValueError("force rows must be dense and source-ordered")
        rows.append({"source_id": source_id, "scalar_force": value})
    if not rows:
        raise ValueError("force file must be nonempty")
    return _canonical_force_rows(rows)


def load_real_scale_v4_input(
    prepared_arrays_path: str | Path,
    expected_forces_path: str | Path,
    *,
    expected_prepared_sha256: str,
    expected_forces_sha256: str,
):
    """Load the frozen author-exported 32,768-body hierarchy and forces."""

    prepared_arrays_path = Path(prepared_arrays_path).resolve()
    expected_forces_path = Path(expected_forces_path).resolve()
    prepared_sha256 = _file_sha256(prepared_arrays_path)
    forces_sha256 = _file_sha256(expected_forces_path)
    if prepared_sha256 != expected_prepared_sha256:
        raise RuntimeError("RT-BarnesHut prepared-array identity mismatch")
    if forces_sha256 != expected_forces_sha256:
        raise RuntimeError("RT-BarnesHut expected-force identity mismatch")
    adapter = _adapter_module()
    prepared = adapter._load_goal2547_reader()(prepared_arrays_path)
    packet = adapter.prepared_arrays_to_aggregate_hierarchy(prepared)
    expected = _read_force_rows(expected_forces_path)
    if packet["hierarchy"].point_count != len(expected):
        raise RuntimeError("RT-BarnesHut hierarchy/force row count mismatch")
    return {
        "spec": packet["reduce_spec"],
        "expected_rows": expected,
        "force_scale": float(adapter.DEFAULT_FORCE_OUTPUT_SCALE),
        "input_sha256": _digest({
            "prepared_arrays_sha256": prepared_sha256,
            "expected_forces_sha256": forces_sha256,
            "hierarchy_sha256": hierarchy_content_sha256(packet["reduce_spec"]),
        }),
        "prepared_arrays_sha256": prepared_sha256,
        "expected_forces_sha256": forces_sha256,
        "real_scale_author_state": True,
    }


def build_v4_input(*, body_count: int = 256):
    spec, expected_rows, metadata = (
        _fixture_module().rt_barneshut_author_fixture(body_count))
    hierarchy = spec.prepared_hierarchy.hierarchy
    return {
        "spec": spec,
        "expected_rows": expected_rows,
        "force_scale": float(metadata["force_scale"]),
        "input_sha256": _digest({
            "hierarchy": hierarchy_content_sha256(spec),
            "opening": spec.opening.to_metadata(),
            "reducer": spec.reducer,
            "body_count": body_count,
        }),
    }


def _schema_for(spec):
    hierarchy = spec.prepared_hierarchy.hierarchy
    return HierarchyFrontierSchema(
        producer_contract_sha256=hashlib.sha256(
            b"author_prepared_aggregate_hierarchy_force_v1").hexdigest(),
        hierarchy_sha256=hierarchy_content_sha256(spec),
        reducer=HierarchyReducer.INVERSE_SQUARE_SCALAR_SUM,
        maximum_output_rows=hierarchy.point_count,
        maximum_visits_per_source=hierarchy.node_count * 2 + 1,
    )


def _reference_rows(spec, *, softening: float, force_scale: float):
    hierarchy = spec.prepared_hierarchy.hierarchy
    execution = aggregate_frontier_reduce_execution_contract_3d(
        spec, backend="reference", max_output_rows=hierarchy.point_count)
    endpoint = aggregate_frontier_reduce_reference_3d(
        execution, softening=softening)
    return _canonical_force_rows(tuple({
        "source_id": int(row["source_id"]),
        "scalar_force": float(row["reducer_value_0"]) * force_scale,
    } for row in endpoint["rows"]))


@dataclass
class PreparedRtBarnesHutV4:
    """Application owner reusing one prepared hierarchy across force queries."""

    owner: object
    spec: object
    force_scale: float
    input_sha256: str
    total_prepare_seconds: float
    frozen_expected_rows: tuple[dict[str, float | int], ...] | None = None
    frozen_expected_values: object | None = None

    def execute(self, *, softening: float = 0.0):
        started = time.perf_counter()
        executed = self.owner.execute_columns(softening=softening)
        actual, actual_values = _canonical_force_rows_from_values(
            executed.reducer_value_0,
            force_scale=self.force_scale,
        )
        elapsed = time.perf_counter() - started
        # The independent CPU reference is a post-timer comparator.
        if self.frozen_expected_rows is not None and float(softening) == 0.0:
            expected = self.frozen_expected_rows
            expected_values = self.frozen_expected_values
        else:
            expected = _reference_rows(
                self.spec, softening=softening, force_scale=self.force_scale,
            )
            expected_values = _force_value_column(expected)
        comparison = _compare_force_value_columns(actual_values, expected_values)
        return {
            "schema": "rtdl.paper_reproduction.rt_barneshut.v4.prepared.v1",
            "input_sha256": self.input_sha256,
            "dynamic_softening": float(softening),
            "output": actual,
            "expected": expected,
            "maximum_abs_delta": comparison["maximum_abs_delta"],
            "maximum_rel_delta": comparison["maximum_rel_delta"],
            "mismatch_count": comparison["mismatch_count"],
            "force_rtol": FORCE_RELATIVE_TOLERANCE,
            "force_atol": FORCE_ABSOLUTE_TOLERANCE,
            "matched": comparison["matched"],
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False,
            "cold_result_replaced": False,
            "lifecycle_receipt": self.owner.lifecycle_receipt,
            "traversal_receipt": executed.traversal_receipt,
            "native_library_sha256": executed.traversal_receipt[
                "provider_library_sha256"],
        }

    def close(self) -> None:
        self.owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_v4(
    *, body_count: int = 256, prepared_input=None,
) -> PreparedRtBarnesHutV4:
    started = time.perf_counter()
    data = prepared_input if prepared_input is not None else build_v4_input(
        body_count=body_count)
    spec = data["spec"]
    compiled = compile_hierarchy_frontier(spec, _schema_for(spec))
    owner = prepare_hierarchy_frontier(compiled, spec)
    frozen_expected_rows = (
        tuple(data["expected_rows"]) if prepared_input is not None else None
    )
    frozen_expected_values = (
        _force_value_column(frozen_expected_rows)
        if frozen_expected_rows is not None else None
    )
    total_prepare_seconds = time.perf_counter() - started
    return PreparedRtBarnesHutV4(
        owner=owner,
        spec=spec,
        force_scale=float(data["force_scale"]),
        input_sha256=str(data["input_sha256"]),
        total_prepare_seconds=total_prepare_seconds,
        frozen_expected_rows=frozen_expected_rows,
        frozen_expected_values=frozen_expected_values,
    )


def run_v4_complete(*, body_count: int = 256):
    started = time.perf_counter()
    data = build_v4_input(body_count=body_count)
    spec = data["spec"]
    compiled = compile_hierarchy_frontier(spec, _schema_for(spec))
    executed = execute_hierarchy_frontier(compiled, spec)
    actual = tuple({
        "source_id": int(row["source_id"]),
        "scalar_force": float(row["reducer_value_0"]) * data["force_scale"],
    } for row in executed.rows)
    comparison = _compare_force_rows(actual, data["expected_rows"])
    elapsed = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.rt_barneshut.v4.v1",
        "input_sha256": data["input_sha256"],
        "output": actual,
        "expected": data["expected_rows"],
        "maximum_abs_delta": comparison["maximum_abs_delta"],
        "maximum_rel_delta": comparison["maximum_rel_delta"],
        "mismatch_count": comparison["mismatch_count"],
        "force_rtol": FORCE_RELATIVE_TOLERANCE,
        "force_atol": FORCE_ABSOLUTE_TOLERANCE,
        "matched": comparison["matched"],
        "registered_complete_seconds": elapsed,
        "complete_timer_includes": (
            "body_generation", "author_bucket_tree_build",
            "app_owned_threaded_hierarchy_projection",
            "verified_hierarchy_plan_compile", "optix_frontier_execute",
            "force_materialization",
        ),
        "traversal_receipt": executed.traversal_receipt,
        "native_library_sha256": executed.traversal_receipt[
            "provider_library_sha256"],
        "default_selected_between_paper_algorithms": False,
    }


__all__ = [
    "PreparedRtBarnesHutV4", "build_v4_input", "load_real_scale_v4_input",
    "prepare_v4", "run_v4_complete",
]
