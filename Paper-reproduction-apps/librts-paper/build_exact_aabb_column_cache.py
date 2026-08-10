from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import numpy as np

from run_exact_point_contains_count_gate import (
    _sha256,
    load_geometry_mbr_columns,
    load_geometry_mbr_columns_fast,
)


SCHEMA = "rtdl.paper_reproduction.librts.exact_aabb_column_cache.v1"


def cache_paths(prefix: Path) -> tuple[Path, Path]:
    return prefix.with_suffix(".npz"), prefix.with_suffix(".json")


def build_cache(
    *,
    geometry_path: Path,
    cache_prefix: Path,
    fast_loader: bool = False,
) -> dict[str, object]:
    geometry_path = geometry_path.resolve()
    cache_npz, cache_json = cache_paths(cache_prefix.resolve())
    columns = (
        load_geometry_mbr_columns_fast(geometry_path)
        if fast_loader
        else load_geometry_mbr_columns(geometry_path)
    )
    metadata = {
        "schema": SCHEMA,
        "source_path": str(geometry_path),
        "source_name": geometry_path.name,
        "source_size_bytes": geometry_path.stat().st_size,
        "source_sha256": _sha256(geometry_path),
        "row_count": len(columns),
        "column_dtypes": {
            name: str(getattr(columns, name).dtype)
            for name in ("ids", "min_x", "min_y", "max_x", "max_y")
        },
        "source_format": "app-owned WKT MBR derivation",
        "loader": "numeric_numpy_fast" if fast_loader else "python_reference",
        "rtdl_core_wkt_semantics": False,
    }
    cache_npz.parent.mkdir(parents=True, exist_ok=True)
    cache_json.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=cache_npz.parent,
        prefix=f".{cache_npz.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temp_npz = Path(handle.name)
        np.savez(
            handle,
            ids=columns.ids,
            min_x=columns.min_x,
            min_y=columns.min_y,
            max_x=columns.max_x,
            max_y=columns.max_y,
        )
    temp_json = cache_json.with_name(f".{cache_json.name}.tmp")
    try:
        os.replace(temp_npz, cache_npz)
        temp_json.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temp_json, cache_json)
    finally:
        temp_npz.unlink(missing_ok=True)
        temp_json.unlink(missing_ok=True)
    return metadata | {"cache_npz": str(cache_npz), "cache_json": str(cache_json)}


def load_cached_columns(*, geometry_path: Path, cache_prefix: Path):
    import rtdsl as rt

    geometry_path = geometry_path.resolve()
    cache_npz, cache_json = cache_paths(cache_prefix.resolve())
    if not cache_npz.is_file() or not cache_json.is_file():
        raise FileNotFoundError(f"AABB cache pair is incomplete: {cache_npz}, {cache_json}")
    metadata = json.loads(cache_json.read_text(encoding="utf-8"))
    if metadata.get("schema") != SCHEMA:
        raise ValueError("unsupported AABB cache schema")
    if metadata.get("source_sha256") != _sha256(geometry_path):
        raise ValueError("AABB cache source SHA-256 does not match geometry input")
    with np.load(cache_npz, allow_pickle=False) as arrays:
        columns = rt.Aabb2DColumns(
            ids=arrays["ids"],
            min_x=arrays["min_x"],
            min_y=arrays["min_y"],
            max_x=arrays["max_x"],
            max_y=arrays["max_y"],
        )
    if len(columns) != int(metadata["row_count"]):
        raise ValueError("AABB cache row_count does not match stored arrays")
    return columns, metadata


def load_verified_cache_artifact(
    *,
    cache_prefix: Path,
    expected_npz_sha256: str,
    expected_source_sha256: str,
):
    """Load a frozen cache without reopening the multi-gigabyte WKT source.

    Goal5634 excludes WKT parsing and cache construction from the comparison.
    The data-bundle manifest and these explicit digests bind both the derived
    column artifact and the source bytes from which it was built.
    """

    import rtdsl as rt

    cache_npz, cache_json = cache_paths(cache_prefix.resolve())
    if not cache_npz.is_file() or not cache_json.is_file():
        raise FileNotFoundError(f"AABB cache pair is incomplete: {cache_npz}, {cache_json}")
    if _sha256(cache_npz) != str(expected_npz_sha256):
        raise ValueError("AABB cache NPZ SHA-256 does not match the frozen data manifest")
    metadata = json.loads(cache_json.read_text(encoding="utf-8"))
    if metadata.get("schema") != SCHEMA:
        raise ValueError("unsupported AABB cache schema")
    if metadata.get("source_sha256") != str(expected_source_sha256):
        raise ValueError("AABB cache source SHA-256 does not match the frozen source identity")
    with np.load(cache_npz, allow_pickle=False) as arrays:
        columns = rt.Aabb2DColumns(
            ids=arrays["ids"],
            min_x=arrays["min_x"],
            min_y=arrays["min_y"],
            max_x=arrays["max_x"],
            max_y=arrays["max_y"],
        )
    if len(columns) != int(metadata["row_count"]):
        raise ValueError("AABB cache row_count does not match stored arrays")
    return columns, metadata | {
        "cache_npz": str(cache_npz),
        "cache_json": str(cache_json),
        "cache_npz_sha256": str(expected_npz_sha256),
        "source_identity_verified_without_reparse": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--cache-prefix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fast-loader", action="store_true")
    args = parser.parse_args()
    result = build_cache(
        geometry_path=args.geometry,
        cache_prefix=args.cache_prefix,
        fast_loader=args.fast_loader,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
