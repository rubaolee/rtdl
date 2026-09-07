"""Shared, RTDL-independent loaders for registered real-scale app inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_particle(data_root: str | Path) -> dict[str, Any]:
    root = Path(data_root).resolve() / "particle"
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.particle_real_scale_input.v1":
        raise ValueError("unexpected Particle real-scale manifest")
    arrays: dict[str, np.ndarray] = {}
    for name, row in manifest["members"].items():
        path = root / name
        if not path.is_file() or sha256(path) != row["sha256"]:
            raise RuntimeError(f"Particle input member differs: {name}")
        value = np.load(path, allow_pickle=False)
        if list(value.shape) != row["shape"] or str(value.dtype) != row["dtype"]:
            raise RuntimeError(f"Particle array contract differs: {name}")
        arrays[name] = value
    return {
        "vertices": arrays["vertices_f32.npy"],
        "triangles": arrays["triangles_u32.npy"],
        "front_values": arrays["front_values_u32.npy"],
        "back_values": arrays["back_values_u32.npy"],
        "queries": arrays["queries_f32.npy"],
        "expected": arrays["expected_u32.npy"],
        "input_sha256": sha256(manifest_path),
        "independent_oracle_sha256": hashlib.sha256(
            json.dumps(
                {
                    "construction": manifest["queries"]["construction"],
                    "query_cells_sha256": manifest["members"]["query_cells_u32.npy"][
                        "sha256"
                    ],
                    "expected_sha256": manifest["members"]["expected_u32.npy"][
                        "sha256"
                    ],
                    "source_sha256": manifest["source"]["sha256"],
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
        "real_scale_manifest": manifest,
        "route_independent_expected": True,
    }


def load_triangle(
    source_root: str | Path,
    data_root: str | Path,
    *,
    dataset: str = "com-dblp",
    expected_triangle_count: int = 2_224_385,
) -> dict[str, Any]:
    source_root = Path(source_root).resolve()
    module_path = (
        source_root
        / "examples/current/research_benchmarks/triangle_counting/segmented_rt_graph.py"
    )
    spec = importlib.util.spec_from_file_location(
        "v4_pyoptix_shared_segmented_rt_graph", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load shared segmented RT-Graph producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    edge_file = Path(data_root).resolve() / "triangle" / f"{dataset}.edge"
    graph = module.build_segmented_rt_graph_csr_binary(
        edge_file, expected_triangle_count=expected_triangle_count
    )
    return {
        "dataset": dataset,
        "edge_file": edge_file,
        "edge_file_sha256": sha256(edge_file),
        "expected_triangle_count": int(expected_triangle_count),
        "graph_contract": graph,
        "segment_iterator": module.iter_segmented_rt_graph_device_geometry,
        "max_relation_rows": 1_000_000,
        "paper_algorithm": "RT-2A1",
    }


def _numbers(text: str) -> np.ndarray:
    return np.fromiter(
        (float(match.group(0)) for match in NUMBER_RE.finditer(text)),
        dtype=np.float64,
    )


def _split_wkt_top_level(text: str) -> tuple[str, ...]:
    parts = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced WKT parentheses")
        elif char == "," and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    if depth != 0:
        raise ValueError("unbalanced WKT parentheses")
    parts.append(text[start:].strip())
    return tuple(part for part in parts if part)


def _strip_outer_parens(text: str) -> str:
    value = text.strip()
    return (
        value[1:-1].strip() if value.startswith("(") and value.endswith(")") else value
    )


def _wkt_mbr(text: str) -> tuple[float, float, float, float]:
    values = _numbers(text)
    if values.size < 2 or values.size % 2:
        raise ValueError("2-D WKT coordinate count is invalid")
    xs = values[0::2]
    ys = values[1::2]
    return float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max())


def _wkt_mbrs(text: str) -> tuple[tuple[float, float, float, float], ...]:
    stripped = text.strip()
    start = stripped.find("(")
    end = stripped.rfind(")")
    if start < 0 or end <= start:
        raise ValueError("invalid WKT geometry")
    kind = stripped[:start].strip().split()[0].upper()
    body = stripped[start + 1 : end]
    if kind == "MULTIPOLYGON":
        rows = _split_wkt_top_level(body)
        if not rows:
            raise ValueError("empty MULTIPOLYGON")
        return tuple(_wkt_mbr(_strip_outer_parens(row)) for row in rows)
    if kind in {"POLYGON", "LINESTRING", "POINT"}:
        return (_wkt_mbr(body),)
    raise ValueError(f"unsupported WKT geometry: {kind}")


def load_librts(data_root: str | Path, *, operation: str) -> dict[str, Any]:
    if operation not in {"point_contains", "range_contains"}:
        raise ValueError("LibRTS operation differs")
    root = Path(data_root).resolve() / "common/librts/parks"
    cache_npz = root / "cache/parks_bz2.npz"
    cache_json = root / "cache/parks_bz2.json"
    query_path = root / f"queries/{operation}_100000.wkt"
    metadata = json.loads(cache_json.read_text(encoding="utf-8"))
    with np.load(cache_npz, allow_pickle=False) as arrays:
        indexed = {
            "id": np.ascontiguousarray(arrays["ids"], dtype=np.uint32),
            "min_x": np.ascontiguousarray(arrays["min_x"], dtype=np.float64),
            "min_y": np.ascontiguousarray(arrays["min_y"], dtype=np.float64),
            "max_x": np.ascontiguousarray(arrays["max_x"], dtype=np.float64),
            "max_y": np.ascontiguousarray(arrays["max_y"], dtype=np.float64),
        }
    if indexed["id"].size != int(metadata["row_count"]):
        raise RuntimeError("LibRTS indexed cache cardinality differs")
    rows = []
    with query_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            if operation == "point_contains":
                values = _numbers(line)
                if values.size != 2 or not line.lstrip().upper().startswith("POINT"):
                    raise ValueError("LibRTS point WKT differs")
                rows.append((float(values[0]), float(values[1])))
            else:
                rows.extend(_wkt_mbrs(line))
    queries = tuple(rows)
    if len(queries) != 100_000:
        raise RuntimeError(f"LibRTS query cardinality differs: {len(queries)}")
    expected = 112_729 if operation == "point_contains" else 105_826
    return {
        "operation": operation,
        "indexed": indexed,
        "queries": queries,
        "expected_count": expected,
        "cache_npz_sha256": sha256(cache_npz),
        "cache_json_sha256": sha256(cache_json),
        "query_sha256": sha256(query_path),
    }


__all__ = ["load_librts", "load_particle", "load_triangle", "sha256"]
