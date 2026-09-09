"""Build distinct Cartesian query grids with an independent exact oracle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

import numpy as np
from numpy.lib.format import open_memmap


NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
SCHEMA = "rtdl.v4.librts.distinct_cartesian_query_grid.v1"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _numbers(line: str) -> np.ndarray:
    return np.asarray(NUMBER_RE.findall(line), dtype=np.float64)


def _point_source_axes(path: Path) -> tuple[np.ndarray, np.ndarray, int]:
    x_values: list[float] = []
    y_values: list[float] = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            values = _numbers(line)
            if values.size != 2 or not line.lstrip().upper().startswith("POINT"):
                raise ValueError("point query source contains non-POINT WKT")
            x_values.append(float(values[0]))
            y_values.append(float(values[1]))
    if not x_values:
        raise ValueError("point query source is empty")
    return (
        np.asarray(x_values, dtype=np.float32),
        np.asarray(y_values, dtype=np.float32),
        len(x_values),
    )


def _range_source_centers_and_half_widths(
    path: Path,
) -> tuple[np.ndarray, np.ndarray, np.float32, np.float32, int]:
    minimum_x: list[float] = []
    minimum_y: list[float] = []
    maximum_x: list[float] = []
    maximum_y: list[float] = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            values = _numbers(line)
            if values.size < 2 or values.size % 2:
                raise ValueError("range query source contains invalid 2-D WKT")
            xs = values[0::2]
            ys = values[1::2]
            minimum_x.append(float(xs.min()))
            minimum_y.append(float(ys.min()))
            maximum_x.append(float(xs.max()))
            maximum_y.append(float(ys.max()))
    if not minimum_x:
        raise ValueError("range query source is empty")
    min_x = np.asarray(minimum_x, dtype=np.float32)
    min_y = np.asarray(minimum_y, dtype=np.float32)
    max_x = np.asarray(maximum_x, dtype=np.float32)
    max_y = np.asarray(maximum_y, dtype=np.float32)
    if bool((max_x < min_x).any()) or bool((max_y < min_y).any()):
        raise ValueError("range query source contains inverted bounds")
    center_x = np.asarray((min_x + max_x) * np.float32(0.5), dtype=np.float32)
    center_y = np.asarray((min_y + max_y) * np.float32(0.5), dtype=np.float32)
    half_x = np.float32(np.median((max_x - min_x) * np.float32(0.5)))
    half_y = np.float32(np.median((max_y - min_y) * np.float32(0.5)))
    if not np.isfinite(half_x) or not np.isfinite(half_y) or half_x < 0 or half_y < 0:
        raise ValueError("range query source produced invalid median half-widths")
    return center_x, center_y, half_x, half_y, len(minimum_x)


def _even_unique(values: np.ndarray, count: int, *, label: str) -> np.ndarray:
    if count <= 0:
        raise ValueError(f"{label} axis count must be positive")
    unique = np.unique(np.asarray(values, dtype=np.float32))
    if unique.size < count:
        raise ValueError(
            f"{label} source has only {unique.size} distinct float32 values, "
            f"fewer than requested {count}"
        )
    indices = (np.arange(count, dtype=np.uint64) * np.uint64(unique.size)) \
        // np.uint64(count)
    selected = np.ascontiguousarray(unique[indices.astype(np.int64)], dtype=np.float32)
    if selected.size != count or np.unique(selected).size != count:
        raise RuntimeError(f"{label} deterministic axis selection is not unique")
    return selected


def _indexed_f32(indexed: Mapping[str, Any]) -> dict[str, np.ndarray]:
    names = ("min_x", "min_y", "max_x", "max_y")
    result = {
        name: np.ascontiguousarray(np.asarray(indexed[name], dtype=np.float32))
        for name in names
    }
    count = int(result["min_x"].size)
    if count <= 0 or any(array.ndim != 1 or array.size != count for array in result.values()):
        raise ValueError("indexed AABB columns must be nonempty equal-length vectors")
    if any(not bool(np.isfinite(array).all()) for array in result.values()):
        raise ValueError("indexed AABB columns contain nonfinite coordinates")
    if bool((result["max_x"] < result["min_x"]).any()) or bool(
        (result["max_y"] < result["min_y"]).any()
    ):
        raise ValueError("indexed AABB columns contain inverted bounds")
    return result


def point_grid_oracle(
    indexed: Mapping[str, Any], x_axis: np.ndarray, y_axis: np.ndarray,
) -> int:
    """Count all inclusive box/point incidences without running RT traversal."""

    boxes = _indexed_f32(indexed)
    x_axis = np.asarray(x_axis, dtype=np.float32)
    y_axis = np.asarray(y_axis, dtype=np.float32)
    if np.unique(x_axis).size != x_axis.size or np.unique(y_axis).size != y_axis.size:
        raise ValueError("point grid axes must be unique")
    if bool((x_axis[1:] < x_axis[:-1]).any()) or bool((y_axis[1:] < y_axis[:-1]).any()):
        raise ValueError("point grid axes must be sorted")
    if int(x_axis.size) * int(y_axis.size) * int(boxes["min_x"].size) \
            > np.iinfo(np.uint64).max:
        raise OverflowError("point grid worst-case incidence count exceeds U64")
    x_count = np.searchsorted(x_axis, boxes["max_x"], side="right") \
        - np.searchsorted(x_axis, boxes["min_x"], side="left")
    y_count = np.searchsorted(y_axis, boxes["max_y"], side="right") \
        - np.searchsorted(y_axis, boxes["min_y"], side="left")
    products = x_count.astype(np.uint64) * y_count.astype(np.uint64)
    return int(products.sum(dtype=np.uint64))


def range_grid_oracle(
    indexed: Mapping[str, Any],
    min_x_axis: np.ndarray,
    max_x_axis: np.ndarray,
    min_y_axis: np.ndarray,
    max_y_axis: np.ndarray,
) -> int:
    """Count inclusive box/query-box containment for a Cartesian interval grid."""

    boxes = _indexed_f32(indexed)
    axes = tuple(
        np.asarray(value, dtype=np.float32)
        for value in (min_x_axis, max_x_axis, min_y_axis, max_y_axis)
    )
    min_x, max_x, min_y, max_y = axes
    if min_x.size != max_x.size or min_y.size != max_y.size:
        raise ValueError("range grid interval axes have unequal lengths")
    if bool((max_x < min_x).any()) or bool((max_y < min_y).any()):
        raise ValueError("range grid interval axes contain inverted bounds")
    if any(bool((axis[1:] < axis[:-1]).any()) for axis in axes):
        raise ValueError("range grid interval axes must be sorted")
    if int(min_x.size) * int(min_y.size) * int(boxes["min_x"].size) \
            > np.iinfo(np.uint64).max:
        raise OverflowError("range grid worst-case incidence count exceeds U64")
    x_first = np.searchsorted(min_x, boxes["min_x"], side="left")
    x_stop = np.searchsorted(max_x, boxes["max_x"], side="right")
    y_first = np.searchsorted(min_y, boxes["min_y"], side="left")
    y_stop = np.searchsorted(max_y, boxes["max_y"], side="right")
    x_count = np.maximum(x_stop - x_first, 0).astype(np.uint64)
    y_count = np.maximum(y_stop - y_first, 0).astype(np.uint64)
    return int((x_count * y_count).sum(dtype=np.uint64))


def _write_cartesian_columns(
    output: Path,
    *,
    x_columns: Mapping[str, np.ndarray],
    y_columns: Mapping[str, np.ndarray],
    row_chunk: int = 64,
) -> dict[str, dict[str, Any]]:
    x_count = int(next(iter(x_columns.values())).size)
    y_count = int(next(iter(y_columns.values())).size)
    if x_count <= 0 or y_count <= 0 or row_chunk <= 0:
        raise ValueError("Cartesian column dimensions and row_chunk must be positive")
    if any(array.size != x_count for array in x_columns.values()) or any(
        array.size != y_count for array in y_columns.values()
    ):
        raise ValueError("Cartesian axis columns have unequal lengths")
    query_count = x_count * y_count
    if query_count > 0xFFFFFFFF:
        raise ValueError("Cartesian query count exceeds the U32 OptiX launch limit")
    records: dict[str, dict[str, Any]] = {}
    for name, axis in x_columns.items():
        path = output / f"{name}.npy"
        target = open_memmap(path, mode="w+", dtype=np.float32, shape=(query_count,))
        for y_start in range(0, y_count, row_chunk):
            y_stop = min(y_start + row_chunk, y_count)
            target[y_start * x_count:y_stop * x_count] = np.tile(
                axis, y_stop - y_start
            )
        target.flush()
        del target
        records[name] = {
            "path": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "dtype": "float32",
            "shape": [query_count],
        }
    for name, axis in y_columns.items():
        path = output / f"{name}.npy"
        target = open_memmap(path, mode="w+", dtype=np.float32, shape=(query_count,))
        for y_start in range(0, y_count, row_chunk):
            y_stop = min(y_start + row_chunk, y_count)
            target[y_start * x_count:y_stop * x_count] = np.repeat(
                axis[y_start:y_stop], x_count
            )
        target.flush()
        del target
        records[name] = {
            "path": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "dtype": "float32",
            "shape": [query_count],
        }
    return records


def generate_query_grid(
    *,
    indexed: Mapping[str, Any],
    source_query_path: str | Path,
    operation: str,
    x_count: int,
    y_count: int,
    output: str | Path,
    indexed_identity: Mapping[str, Any] | None = None,
    stream_chunk_rows: int | None = None,
) -> dict[str, Any]:
    if x_count <= 0 or y_count <= 0:
        raise ValueError("Cartesian query axis counts must be positive")
    if x_count * y_count > 0xFFFFFFFF:
        raise ValueError("Cartesian query count exceeds the U32 OptiX launch limit")
    if stream_chunk_rows is not None and not (
        0 < stream_chunk_rows <= 0xFFFFFFFF
    ):
        raise ValueError("stream_chunk_rows must be inside nonzero U32")
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    source = Path(source_query_path).resolve(strict=True)
    if operation == "point_contains":
        source_x, source_y, source_count = _point_source_axes(source)
        x_axis = _even_unique(source_x, x_count, label="point x")
        y_axis = _even_unique(source_y, y_count, label="point y")
        expected = point_grid_oracle(indexed, x_axis, y_axis)
        columns = _write_cartesian_columns(
            output,
            x_columns={"x": x_axis},
            y_columns={"y": y_axis},
        )
        derivation = {
            "x_axis": "evenly spaced selection from sorted unique source point x",
            "y_axis": "evenly spaced selection from sorted unique source point y",
        }
    elif operation == "range_contains":
        source_x, source_y, half_x, half_y, source_count = (
            _range_source_centers_and_half_widths(source)
        )
        center_x = _even_unique(source_x, x_count, label="range center x")
        center_y = _even_unique(source_y, y_count, label="range center y")
        min_x = np.asarray(center_x - half_x, dtype=np.float32)
        max_x = np.asarray(center_x + half_x, dtype=np.float32)
        min_y = np.asarray(center_y - half_y, dtype=np.float32)
        max_y = np.asarray(center_y + half_y, dtype=np.float32)
        if np.unique(np.stack((min_x, max_x), axis=1), axis=0).shape[0] != x_count:
            raise RuntimeError("range x intervals are not distinct after float32 lowering")
        if np.unique(np.stack((min_y, max_y), axis=1), axis=0).shape[0] != y_count:
            raise RuntimeError("range y intervals are not distinct after float32 lowering")
        expected = range_grid_oracle(indexed, min_x, max_x, min_y, max_y)
        columns = _write_cartesian_columns(
            output,
            x_columns={"min_x": min_x, "max_x": max_x},
            y_columns={"min_y": min_y, "max_y": max_y},
        )
        derivation = {
            "x_axis": "source range-center x with fixed source-median float32 half-width",
            "y_axis": "source range-center y with fixed source-median float32 half-width",
            "half_width_x_f32": float(half_x),
            "half_width_y_f32": float(half_y),
        }
    else:
        raise ValueError("operation must be point_contains or range_contains")
    query_count = x_count * y_count
    manifest = {
        "schema": SCHEMA,
        "operation": operation,
        "query_count": query_count,
        "x_axis_count": x_count,
        "y_axis_count": y_count,
        "source_query_count": source_count,
        "source_query_path": str(source),
        "source_query_sha256": sha256_file(source),
        "indexed_identity": dict(indexed_identity or {}),
        "columns": columns,
        "expected_count_u64": expected,
        "mean_hits_per_query": expected / query_count,
        "all_queries_distinct": True,
        "distinctness_proof": (
            "each query is one element of the Cartesian product of two unique "
            "float32 axes; equal query rows imply equal x-axis and y-axis indices"
        ),
        "oracle": {
            "kind": "independent_axis_coverage_sum_u64",
            "rt_or_pyoptix_execution_used": False,
            "formula": "sum_over_indexed_boxes(x_axis_coverage * y_axis_coverage)",
            "inclusive_boundaries": True,
            "float_contract": "all indexed and query coordinates lowered to float32",
        },
        "derivation": derivation,
        "streaming": {
            "enabled": stream_chunk_rows is not None,
            "chunk_rows": stream_chunk_rows,
            "chunk_count": (
                None
                if stream_chunk_rows is None
                else (query_count + stream_chunk_rows - 1) // stream_chunk_rows
            ),
            "partition": "contiguous_nonoverlapping_full_cover",
            "query_validation_and_h2d_inside_action": stream_chunk_rows is not None,
        },
    }
    manifest_path = output / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def load_query_columns(manifest_path: str | Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    path = Path(manifest_path).resolve(strict=True)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unsupported LibRTS long-query manifest")
    columns: dict[str, np.ndarray] = {}
    for name, record in manifest["columns"].items():
        column_path = path.parent / record["path"]
        if sha256_file(column_path) != record["sha256"]:
            raise ValueError(f"LibRTS long-query column digest differs: {name}")
        column = np.load(column_path, mmap_mode="r", allow_pickle=False)
        if column.dtype != np.float32 or list(column.shape) != record["shape"]:
            raise ValueError(f"LibRTS long-query column contract differs: {name}")
        columns[name] = column
    if any(column.size != int(manifest["query_count"]) for column in columns.values()):
        raise ValueError("LibRTS long-query manifest cardinality differs")
    return columns, manifest


__all__ = [
    "SCHEMA",
    "generate_query_grid",
    "load_query_columns",
    "point_grid_oracle",
    "range_grid_oracle",
    "sha256_file",
]
