from __future__ import annotations

import argparse
import gzip
import json
import math
import shutil
import subprocess
import struct
import sys
import tarfile
import time
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_hausdorff_v2_function as hd
from examples import rtdl_hausdorff_v2_user_benchmark as lab


STANFORD_DATASETS = {
    "dragon": {
        "url": "https://graphics.stanford.edu/pub/3Dscanrep/dragon/dragon_recon.tar.gz",
        "archive": "dragon_recon.tar.gz",
        "preferred_ply": "dragon_vrip.ply",
        "source": "Stanford 3D Scanning Repository",
    },
    "happy": {
        "url": "https://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz",
        "archive": "happy_recon.tar.gz",
        "preferred_ply": "happy_vrip.ply",
        "source": "Stanford 3D Scanning Repository",
    },
}

XHD_GRAPHICS_DATASETS = {
    "dragon": {
        "kind": "tar_gz",
        "url": "https://graphics.stanford.edu/pub/3Dscanrep/dragon/dragon_recon.tar.gz",
        "archive": "dragon_recon.tar.gz",
        "preferred_ply": "dragon_vrip.ply",
        "source": "Stanford 3D Scanning Repository; X-HD graphics pair member",
    },
    "happy_buddha": {
        "kind": "tar_gz",
        "url": "https://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz",
        "archive": "happy_recon.tar.gz",
        "preferred_ply": "happy_vrip.ply",
        "source": "Stanford 3D Scanning Repository; X-HD graphics pair member",
    },
    "asian_dragon": {
        "kind": "ply_gz",
        "url": "https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_dragon.ply.gz",
        "archive": "xyzrgb_dragon.ply.gz",
        "ply_name": "asian_dragon.ply",
        "source": "Stanford 3D Scanning Repository XYZ RGB model; X-HD graphics pair member",
    },
    "thai_statuette": {
        "kind": "ply_gz",
        "url": "https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_statuette.ply.gz",
        "archive": "xyzrgb_statuette.ply.gz",
        "ply_name": "thai_statuette.ply",
        "source": "Stanford 3D Scanning Repository XYZ RGB model; X-HD graphics pair member",
    },
}

XHD_GRAPHICS_PAIRS = (
    (
        "xhd_graphics_dragon_vs_asian_dragon_xy",
        "dragon",
        "asian_dragon",
        "X-HD graphics pair: Stanford Dragon vs XYZ RGB Asian Dragon, projected to XY.",
        "mixed-density",
    ),
    (
        "xhd_graphics_thai_statuette_vs_happy_buddha_xy",
        "thai_statuette",
        "happy_buddha",
        "X-HD graphics pair: XYZ RGB Thai Statuette vs Happy Buddha, projected to XY.",
        "dense-to-medium",
    ),
    (
        "xhd_graphics_dragon_vs_happy_buddha_xy",
        "dragon",
        "happy_buddha",
        "X-HD graphics pair: Stanford Dragon vs Happy Buddha, projected to XY.",
        "medium",
    ),
    (
        "xhd_graphics_thai_statuette_vs_asian_dragon_xy",
        "thai_statuette",
        "asian_dragon",
        "X-HD graphics pair: XYZ RGB Thai Statuette vs XYZ RGB Asian Dragon, projected to XY.",
        "dense",
    ),
)

PUBLIC_GEO_DATASETS = {
    "census_counties": {
        "url": "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip",
        "archive": "tl_2023_us_county.zip",
        "shp_name": "tl_2023_us_county.shp",
        "source": "U.S. Census TIGER/Line 2023 county boundaries; public analogue for X-HD dtl_cnty.wkt",
    },
    "census_zcta": {
        "url": "https://www2.census.gov/geo/tiger/TIGER2023/ZCTA520/tl_2023_us_zcta520.zip",
        "archive": "tl_2023_us_zcta520.zip",
        "shp_name": "tl_2023_us_zcta520.shp",
        "source": "U.S. Census TIGER/Line 2023 2020 ZCTA boundaries; public analogue for X-HD uszipcode.wkt",
    },
    "naturalearth_lakes": {
        "url": "https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_lakes.zip",
        "archive": "ne_10m_lakes.zip",
        "shp_name": "ne_10m_lakes.shp",
        "source": "Natural Earth 1:10m lakes and reservoirs; public analogue for X-HD lakes.wkt",
    },
    "naturalearth_parks": {
        "url": "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_parks_and_protected_lands.zip",
        "archive": "ne_10m_parks_and_protected_lands.zip",
        "shp_name": "ne_10m_parks_and_protected_lands.shp",
        "source": "Natural Earth 1:10m parks and protected lands; public analogue for X-HD parks.wkt",
    },
}

PUBLIC_GEO_PAIRS = (
    (
        "public_geo_census_counties_vs_zcta_xy",
        "census_counties",
        "census_zcta",
        "Public geo pair mirroring X-HD dtl_cnty.wkt vs uszipcode.wkt: Census counties vs ZCTA boundaries.",
        "detailed-census",
    ),
    (
        "public_geo_lakes_vs_parks_xy",
        "naturalearth_lakes",
        "naturalearth_parks",
        "Public geo pair mirroring X-HD lakes.wkt vs parks.wkt: Natural Earth lakes vs parks/protected lands.",
        "sparse-naturalearth",
    ),
)


PLY_SCALAR_TYPES = {
    "char": ("b", 1),
    "int8": ("b", 1),
    "uchar": ("B", 1),
    "uint8": ("B", 1),
    "short": ("h", 2),
    "int16": ("h", 2),
    "ushort": ("H", 2),
    "uint16": ("H", 2),
    "int": ("i", 4),
    "int32": ("i", 4),
    "uint": ("I", 4),
    "uint32": ("I", 4),
    "float": ("f", 4),
    "float32": ("f", 4),
    "double": ("d", 8),
    "float64": ("d", 8),
}


@dataclass(frozen=True)
class PlyVertexLayout:
    format_name: str
    vertex_count: int
    property_names: tuple[str, ...]
    property_types: tuple[str, ...]
    header_bytes: int


def _read_ply_header(handle: BinaryIO) -> PlyVertexLayout:
    first = handle.readline()
    if first.strip() != b"ply":
        raise ValueError("not a PLY file")
    format_name = ""
    vertex_count: int | None = None
    property_names: list[str] = []
    property_types: list[str] = []
    in_vertex_element = False
    while True:
        line = handle.readline()
        if not line:
            raise ValueError("unexpected EOF while reading PLY header")
        text = line.decode("ascii", errors="replace").strip()
        parts = text.split()
        if not parts:
            continue
        if parts[0] == "format":
            format_name = parts[1]
        elif parts[0] == "element":
            in_vertex_element = parts[1] == "vertex"
            if in_vertex_element:
                vertex_count = int(parts[2])
        elif parts[0] == "property" and in_vertex_element:
            if parts[1] == "list":
                raise ValueError("list properties inside vertex element are not supported")
            property_types.append(parts[1])
            property_names.append(parts[2])
        elif parts[0] == "end_header":
            break
    if vertex_count is None:
        raise ValueError("PLY file has no vertex element")
    if not format_name:
        raise ValueError("PLY file has no format line")
    for required in ("x", "y", "z"):
        if required not in property_names:
            raise ValueError(f"PLY vertices do not contain required {required!r} coordinate")
    return PlyVertexLayout(
        format_name=format_name,
        vertex_count=vertex_count,
        property_names=tuple(property_names),
        property_types=tuple(property_types),
        header_bytes=handle.tell(),
    )


def load_ply_xyz(path: Path, *, limit: int | None = None) -> np.ndarray:
    with path.open("rb") as handle:
        layout = _read_ply_header(handle)
        x_index = layout.property_names.index("x")
        y_index = layout.property_names.index("y")
        z_index = layout.property_names.index("z")
        count = layout.vertex_count if limit is None else min(layout.vertex_count, int(limit))
        out = np.empty((count, 3), dtype=np.float64)
        if layout.format_name == "ascii":
            for i in range(count):
                values = handle.readline().decode("ascii", errors="replace").split()
                out[i, 0] = float(values[x_index])
                out[i, 1] = float(values[y_index])
                out[i, 2] = float(values[z_index])
            return out
        if layout.format_name not in {"binary_little_endian", "binary_big_endian"}:
            raise ValueError(f"unsupported PLY format {layout.format_name!r}")
        endian = "<" if layout.format_name == "binary_little_endian" else ">"
        fields = [PLY_SCALAR_TYPES[type_name] for type_name in layout.property_types]
        row_format = endian + "".join(fmt for fmt, _size in fields)
        row_size = sum(size for _fmt, size in fields)
        row_struct = struct.Struct(row_format)
        for i in range(count):
            row = handle.read(row_size)
            if len(row) != row_size:
                raise ValueError("unexpected EOF while reading vertex rows")
            values = row_struct.unpack(row)
            out[i, 0] = float(values[x_index])
            out[i, 1] = float(values[y_index])
            out[i, 2] = float(values[z_index])
        return out


def _download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 0:
        print(f"[goal2126] using cached {out_path}", flush=True)
        return
    print(f"[goal2126] downloading {url} -> {out_path}", flush=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        total = int(response.headers.get("Content-Length", "0") or "0")
        done = 0
        last_print = time.perf_counter()
        with out_path.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                done += len(chunk)
                now = time.perf_counter()
                if now - last_print >= 10.0:
                    if total:
                        print(f"[goal2126] downloaded {done / total:.1%}", flush=True)
                    else:
                        print(f"[goal2126] downloaded {done} bytes", flush=True)
                    last_print = now


def _extract_archive(archive: Path, extract_dir: Path) -> None:
    marker = extract_dir / ".extracted"
    if marker.exists():
        print(f"[goal2126] using extracted {extract_dir}", flush=True)
        return
    print(f"[goal2126] extracting {archive} -> {extract_dir}", flush=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        safe_root = extract_dir.resolve()
        for member in tar.getmembers():
            target = (extract_dir / member.name).resolve()
            if safe_root not in (target, *target.parents):
                raise ValueError(f"unsafe tar member path {member.name!r}")
        tar.extractall(extract_dir)
    marker.write_text("ok\n", encoding="ascii")


def _extract_zip_archive(archive: Path, extract_dir: Path) -> None:
    marker = extract_dir / ".extracted"
    if marker.exists():
        print(f"[goal2126] using extracted {extract_dir}", flush=True)
        return
    print(f"[goal2126] extracting {archive} -> {extract_dir}", flush=True)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        safe_root = extract_dir.resolve()
        for name in zf.namelist():
            target = (extract_dir / name).resolve()
            if safe_root not in (target, *target.parents):
                raise ValueError(f"unsafe zip member path {name!r}")
        zf.extractall(extract_dir)
    marker.write_text("ok\n", encoding="ascii")


def _decompress_gzip(archive: Path, out_path: Path) -> None:
    marker = out_path.with_suffix(out_path.suffix + ".decompressed")
    if marker.exists() and out_path.exists() and out_path.stat().st_size > 0:
        print(f"[goal2126] using decompressed {out_path}", flush=True)
        return
    print(f"[goal2126] decompressing {archive} -> {out_path}", flush=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(archive, "rb") as src, out_path.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
    marker.write_text("ok\n", encoding="ascii")


def ensure_stanford_dataset(name: str, data_dir: Path) -> Path:
    dataset = STANFORD_DATASETS[name]
    archive = data_dir / dataset["archive"]
    extract_dir = data_dir / name
    _download(str(dataset["url"]), archive)
    _extract_archive(archive, extract_dir)
    preferred = str(dataset["preferred_ply"])
    candidates = sorted(extract_dir.rglob("*.ply"))
    for candidate in candidates:
        if candidate.name == preferred:
            return candidate
    if not candidates:
        raise FileNotFoundError(f"no PLY files found under {extract_dir}")
    return candidates[0]


def ensure_xhd_graphics_dataset(name: str, data_dir: Path) -> Path:
    dataset = XHD_GRAPHICS_DATASETS[name]
    archive = data_dir / str(dataset["archive"])
    _download(str(dataset["url"]), archive)
    kind = str(dataset["kind"])
    if kind == "tar_gz":
        extract_dir = data_dir / name
        _extract_archive(archive, extract_dir)
        preferred = str(dataset["preferred_ply"])
        candidates = sorted(extract_dir.rglob("*.ply"))
        for candidate in candidates:
            if candidate.name == preferred:
                return candidate
        if not candidates:
            raise FileNotFoundError(f"no PLY files found under {extract_dir}")
        return candidates[0]
    if kind == "ply_gz":
        out_path = data_dir / str(dataset["ply_name"])
        _decompress_gzip(archive, out_path)
        return out_path
    raise ValueError(f"unsupported X-HD graphics dataset kind {kind!r}")


def ensure_public_geo_dataset(name: str, data_dir: Path) -> Path:
    dataset = PUBLIC_GEO_DATASETS[name]
    archive = data_dir / str(dataset["archive"])
    _download(str(dataset["url"]), archive)
    extract_dir = data_dir / name
    _extract_zip_archive(archive, extract_dir)
    shp_name = str(dataset["shp_name"])
    candidate = extract_dir / shp_name
    if candidate.exists():
        return candidate
    candidates = sorted(extract_dir.rglob("*.shp"))
    for path in candidates:
        if path.name == shp_name:
            return path
    if not candidates:
        raise FileNotFoundError(f"no shapefile found under {extract_dir}")
    return candidates[0]


def deterministic_sample(points: np.ndarray, count: int, *, seed: int) -> np.ndarray:
    if count <= 0:
        raise ValueError("sample count must be positive")
    if points.shape[0] <= count:
        return np.ascontiguousarray(points, dtype=np.float64)
    rng = np.random.default_rng(seed)
    indices = np.sort(rng.choice(points.shape[0], size=count, replace=False))
    return np.ascontiguousarray(points[indices], dtype=np.float64)


def normalize_project_xy(points: np.ndarray) -> np.ndarray:
    xy = np.asarray(points[:, :2], dtype=np.float64)
    lo = xy.min(axis=0)
    hi = xy.max(axis=0)
    span = np.maximum(hi - lo, 1.0e-12)
    return np.ascontiguousarray((xy - lo) / span, dtype=np.float64)


def _load_shapefile_xy_sample(path: Path, *, sample_count: int, seed: int) -> tuple[np.ndarray, int]:
    try:
        import shapefile  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - pod/runtime dependency path
        raise RuntimeError("public-geo suite requires pyshp; install the 'pyshp' package") from exc

    if sample_count <= 0:
        raise ValueError("sample_count must be positive")

    rng = np.random.default_rng(seed)
    reservoir = np.empty((sample_count, 2), dtype=np.float64)
    total_points = 0
    kept = 0
    start = time.perf_counter()
    last_print = start
    reader = shapefile.Reader(str(path))
    try:
        shape_count = len(reader)
        print(f"[goal2126] sampling shapefile {path} shapes={shape_count}", flush=True)
        for shape_index, shape in enumerate(reader.iterShapes(), start=1):
            for x, y, *_rest in shape.points:
                total_points += 1
                if kept < sample_count:
                    reservoir[kept, 0] = float(x)
                    reservoir[kept, 1] = float(y)
                    kept += 1
                else:
                    replacement = int(rng.integers(total_points))
                    if replacement < sample_count:
                        reservoir[replacement, 0] = float(x)
                        reservoir[replacement, 1] = float(y)
            now = time.perf_counter()
            if now - last_print >= 10.0:
                print(
                    f"[goal2126] shapefile sample progress {path.name}: "
                    f"shape={shape_index}/{shape_count} seen_points={total_points} kept={kept}",
                    flush=True,
                )
                last_print = now
    finally:
        close = getattr(reader, "close", None)
        if callable(close):
            close()
    if kept == 0:
        raise ValueError(f"shapefile contains no coordinate points: {path}")
    return np.ascontiguousarray(reservoir[:kept], dtype=np.float64), total_points


def make_stanford_cases(data_dir: Path, *, sample_count: int) -> dict[str, dict[str, object]]:
    dragon_ply = ensure_stanford_dataset("dragon", data_dir)
    happy_ply = ensure_stanford_dataset("happy", data_dir)
    print(f"[goal2126] loading {dragon_ply}", flush=True)
    dragon = normalize_project_xy(deterministic_sample(load_ply_xyz(dragon_ply), sample_count, seed=2126))
    print(f"[goal2126] loading {happy_ply}", flush=True)
    happy = normalize_project_xy(deterministic_sample(load_ply_xyz(happy_ply), sample_count, seed=2127))
    shifted = np.ascontiguousarray(dragon + np.asarray([0.015, -0.02], dtype=np.float64))
    return {
        "stanford_dragon_xy_shifted": {
            "points_a": dragon,
            "points_b": shifted,
            "source_paths": [str(dragon_ply)],
            "description": "Dragon vertices projected to XY, compared with a deterministic shifted copy.",
        },
        "stanford_dragon_vs_happy_xy": {
            "points_a": dragon,
            "points_b": happy,
            "source_paths": [str(dragon_ply), str(happy_ply)],
            "description": "Dragon and Happy Buddha vertices independently normalized and projected to XY.",
        },
    }


def make_xhd_graphics_cases(data_dir: Path, *, sample_count: int) -> dict[str, dict[str, object]]:
    loaded: dict[str, tuple[Path, np.ndarray]] = {}
    for index, name in enumerate(XHD_GRAPHICS_DATASETS):
        ply = ensure_xhd_graphics_dataset(name, data_dir)
        print(f"[goal2126] loading X-HD graphics {name}: {ply}", flush=True)
        points = normalize_project_xy(
            deterministic_sample(load_ply_xyz(ply), sample_count, seed=2134 + index)
        )
        loaded[name] = (ply, points)

    cases: dict[str, dict[str, object]] = {}
    for case_name, left, right, description, density_class in XHD_GRAPHICS_PAIRS:
        left_path, points_a = loaded[left]
        right_path, points_b = loaded[right]
        cases[case_name] = {
            "points_a": points_a,
            "points_b": points_b,
            "source_paths": [str(left_path), str(right_path)],
            "description": description,
            "density_class": density_class,
            "xhd_paper_graphics_pair": True,
        }
    return cases


def make_public_geo_cases(data_dir: Path, *, sample_count: int) -> dict[str, dict[str, object]]:
    loaded: dict[str, tuple[Path, np.ndarray, int]] = {}
    for index, name in enumerate(PUBLIC_GEO_DATASETS):
        shp = ensure_public_geo_dataset(name, data_dir)
        print(f"[goal2126] loading public geo {name}: {shp}", flush=True)
        sampled, total_points = _load_shapefile_xy_sample(
            shp,
            sample_count=sample_count,
            seed=2234 + index,
        )
        loaded[name] = (shp, normalize_project_xy(sampled), total_points)

    cases: dict[str, dict[str, object]] = {}
    for case_name, left, right, description, density_class in PUBLIC_GEO_PAIRS:
        left_path, points_a, left_total = loaded[left]
        right_path, points_b, right_total = loaded[right]
        cases[case_name] = {
            "points_a": points_a,
            "points_b": points_b,
            "source_paths": [str(left_path), str(right_path)],
            "description": description,
            "density_class": density_class,
            "public_geo_dataset_pair": True,
            "source_total_points": {
                left: int(left_total),
                right: int(right_total),
            },
        }
    return cases


def make_public_cases(
    data_dir: Path,
    *,
    sample_count: int,
    case_suite: str,
) -> dict[str, dict[str, object]]:
    if case_suite == "stanford":
        return make_stanford_cases(data_dir, sample_count=sample_count)
    if case_suite == "xhd-graphics":
        return make_xhd_graphics_cases(data_dir, sample_count=sample_count)
    if case_suite == "public-geo":
        return make_public_geo_cases(data_dir, sample_count=sample_count)
    if case_suite == "all":
        cases = make_stanford_cases(data_dir, sample_count=sample_count)
        cases.update(make_xhd_graphics_cases(data_dir, sample_count=sample_count))
        return cases
    raise ValueError(f"unsupported case suite {case_suite!r}")


def _run_cupy(points_a: np.ndarray, points_b: np.ndarray, *, warmup: int) -> dict[str, object]:
    for _ in range(max(0, int(warmup))):
        hd.hausdorff_distance_2d(points_a, points_b, method="cupy_rawkernel", warmup=0)
    start = time.perf_counter()
    result = hd.hausdorff_distance_2d(points_a, points_b, method="cupy_rawkernel", warmup=0)
    return {
        "ok": True,
        "elapsed_sec": time.perf_counter() - start,
        "distance": result.distance,
        "direction": result.direction,
        "source_index": result.source_index,
        "target_index": result.target_index,
    }


def _run_cupy_grouped_grid(
    points_a: np.ndarray,
    points_b: np.ndarray,
    *,
    group_size: int,
    warmup: int,
) -> dict[str, object]:
    columns_a = hd._as_point_columns(points_a, name="points_a")
    columns_b = hd._as_point_columns(points_b, name="points_b")
    runner = lambda source, target: lab.run_cuda_grouped_grid_rawkernel(
        source,
        target,
        target_points_per_group=group_size,
    )
    for _ in range(max(0, int(warmup))):
        lab.undirected(runner, columns_a, columns_b, warmup=0)
    start = time.perf_counter()
    result = lab.undirected(
        runner,
        columns_a,
        columns_b,
        warmup=0,
    )
    return {
        "ok": True,
        "elapsed_sec": time.perf_counter() - start,
        "distance": float(result["distance"]),
        "direction": result["direction"],
        "source_index": result[f"directed_{result['direction']}"]["source_index"],
        "target_index": result[f"directed_{result['direction']}"]["target_index"],
    }


def _run_rtdl_grouped_reduced(
    points_a: np.ndarray,
    points_b: np.ndarray,
    *,
    group_size: int,
    warmup: int,
) -> dict[str, object]:
    for _ in range(max(0, int(warmup))):
        hd.hausdorff_distance_2d_rt_grouped_reduced_nearest_witness(
            points_a,
            points_b,
            seed_with_threshold=False,
            target_points_per_group=group_size,
        )
    start = time.perf_counter()
    result = hd.hausdorff_distance_2d_rt_grouped_reduced_nearest_witness(
        points_a,
        points_b,
        seed_with_threshold=False,
        target_points_per_group=group_size,
    )
    return {
        "ok": True,
        "elapsed_sec": time.perf_counter() - start,
        "distance": result.distance,
        "direction": result.direction,
        "source_index": result.source_index,
        "target_index": result.target_index,
        "method": result.method,
    }


def _run_rtdl_grouped_seeded_pruned(
    points_a: np.ndarray,
    points_b: np.ndarray,
    *,
    group_size: int,
    seed_sample_count: int,
    warmup: int,
) -> dict[str, object]:
    for _ in range(max(0, int(warmup))):
        hd.hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness(
            points_a,
            points_b,
            seed_sample_count=seed_sample_count,
            target_points_per_group=group_size,
        )
    start = time.perf_counter()
    result = hd.hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness(
        points_a,
        points_b,
        seed_sample_count=seed_sample_count,
        target_points_per_group=group_size,
    )
    return {
        "ok": True,
        "elapsed_sec": time.perf_counter() - start,
        "distance": result.distance,
        "direction": result.direction,
        "source_index": result.source_index,
        "target_index": result.target_index,
        "method": result.method,
    }


def _safe_call(name: str, fn) -> dict[str, object]:
    try:
        return fn()
    except Exception as exc:  # pragma: no cover - artifact path
        return {"ok": False, "method": name, "error": repr(exc)}


def _gpu_summary() -> str:
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return ""
    try:
        completed = subprocess.run(
            [nvidia_smi, "--query-gpu=name,driver_version", "--format=csv,noheader"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.splitlines()[0].strip() if completed.stdout.splitlines() else ""


def run(args: argparse.Namespace) -> dict[str, object]:
    cases = make_public_cases(
        args.data_dir,
        sample_count=args.sample_count,
        case_suite=args.case_suite,
    )
    rows: list[dict[str, object]] = []
    for name, case in cases.items():
        points_a = np.asarray(case["points_a"], dtype=np.float64)
        points_b = np.asarray(case["points_b"], dtype=np.float64)
        group_size = int(args.group_size or max(64, args.sample_count // 256))
        print(f"[goal2126] case={name} n={points_a.shape[0]} group={group_size}", flush=True)
        row: dict[str, object] = {
            "case": name,
            "sample_count": int(points_a.shape[0]),
            "description": case["description"],
            "density_class": case.get("density_class", "not-classified"),
            "source_paths": case["source_paths"],
            "projection": "XY projection from public 3D PLY vertices; not a 3D surface Hausdorff claim",
            "target_points_per_group": group_size,
        }
        if "source_total_points" in case:
            row["source_total_points"] = case["source_total_points"]
            row["projection"] = (
                "Normalized lon/lat vertex coordinates from public shapefiles; "
                "not an original X-HD WKT-file reproduction"
            )
        if not args.skip_cupy:
            print(f"[goal2126] case={name} CuPy baseline start", flush=True)
            row["cupy_rawkernel"] = _safe_call("cupy_rawkernel", lambda: _run_cupy(points_a, points_b, warmup=args.warmup))
            print(
                f"[goal2126] case={name} CuPy done ok={row['cupy_rawkernel'].get('ok')} "
                f"sec={row['cupy_rawkernel'].get('elapsed_sec')}",
                flush=True,
            )
        if not args.skip_cupy_grouped_grid:
            print(f"[goal2126] case={name} CuPy grouped-grid baseline start", flush=True)
            row["cupy_grouped_grid_rawkernel"] = _safe_call(
                "cupy_grouped_grid_rawkernel",
                lambda: _run_cupy_grouped_grid(
                    points_a,
                    points_b,
                    group_size=group_size,
                    warmup=args.warmup,
                ),
            )
            print(
                f"[goal2126] case={name} CuPy grouped-grid done ok={row['cupy_grouped_grid_rawkernel'].get('ok')} "
                f"sec={row['cupy_grouped_grid_rawkernel'].get('elapsed_sec')}",
                flush=True,
            )
        if not args.skip_rtdl:
            print(f"[goal2126] case={name} RTDL/OptiX grouped reduced start", flush=True)
            row["rtdl_rt_grouped_reduced_nearest_witness"] = _safe_call(
                "rtdl_rt_grouped_reduced_nearest_witness",
                lambda: _run_rtdl_grouped_reduced(
                    points_a,
                    points_b,
                    group_size=group_size,
                    warmup=args.warmup,
                ),
            )
            print(
                f"[goal2126] case={name} RTDL done ok={row['rtdl_rt_grouped_reduced_nearest_witness'].get('ok')} "
                f"sec={row['rtdl_rt_grouped_reduced_nearest_witness'].get('elapsed_sec')}",
                flush=True,
            )
        if not args.skip_rtdl_pruned:
            print(f"[goal2126] case={name} RTDL/OptiX X-HD seeded-pruned start", flush=True)
            row["rtdl_rt_grouped_seeded_pruned_nearest_witness"] = _safe_call(
                "rtdl_rt_grouped_seeded_pruned_nearest_witness",
                lambda: _run_rtdl_grouped_seeded_pruned(
                    points_a,
                    points_b,
                    group_size=group_size,
                    seed_sample_count=args.seed_sample_count,
                    warmup=args.warmup,
                ),
            )
            print(
                f"[goal2126] case={name} RTDL seeded-pruned done "
                f"ok={row['rtdl_rt_grouped_seeded_pruned_nearest_witness'].get('ok')} "
                f"sec={row['rtdl_rt_grouped_seeded_pruned_nearest_witness'].get('elapsed_sec')}",
                flush=True,
            )
        cupy = row.get("cupy_rawkernel")
        cupy_grouped = row.get("cupy_grouped_grid_rawkernel")
        rtdl = row.get("rtdl_rt_grouped_reduced_nearest_witness")
        rtdl_pruned = row.get("rtdl_rt_grouped_seeded_pruned_nearest_witness")
        if isinstance(cupy, dict) and isinstance(rtdl, dict) and cupy.get("ok") and rtdl.get("ok"):
            row["matches_cupy"] = math.isclose(
                float(cupy["distance"]),
                float(rtdl["distance"]),
                rel_tol=args.tolerance,
                abs_tol=args.tolerance,
            )
            row["rtdl_vs_cupy_ratio"] = float(rtdl["elapsed_sec"]) / float(cupy["elapsed_sec"])
        if isinstance(cupy_grouped, dict) and isinstance(rtdl, dict) and cupy_grouped.get("ok") and rtdl.get("ok"):
            row["matches_cupy_grouped_grid"] = math.isclose(
                float(cupy_grouped["distance"]),
                float(rtdl["distance"]),
                rel_tol=args.tolerance,
                abs_tol=args.tolerance,
            )
            row["rtdl_vs_cupy_grouped_grid_ratio"] = float(rtdl["elapsed_sec"]) / float(cupy_grouped["elapsed_sec"])
        if (
            isinstance(cupy_grouped, dict)
            and isinstance(rtdl_pruned, dict)
            and cupy_grouped.get("ok")
            and rtdl_pruned.get("ok")
        ):
            row["matches_cupy_grouped_grid_seeded_pruned"] = math.isclose(
                float(cupy_grouped["distance"]),
                float(rtdl_pruned["distance"]),
                rel_tol=args.tolerance,
                abs_tol=args.tolerance,
            )
            row["rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio"] = (
                float(rtdl_pruned["elapsed_sec"]) / float(cupy_grouped["elapsed_sec"])
            )
        if isinstance(cupy, dict) and isinstance(cupy_grouped, dict) and cupy.get("ok") and cupy_grouped.get("ok"):
            row["cupy_grouped_grid_vs_dense_ratio"] = (
                float(cupy_grouped["elapsed_sec"]) / float(cupy["elapsed_sec"])
            )
        rows.append(row)
    return {
        "goal": "goal2126_public_hausdorff_dataset_perf",
        "commit": args.commit_label,
        "gpu": _gpu_summary(),
        "datasets": STANFORD_DATASETS,
        "xhd_graphics_datasets": XHD_GRAPHICS_DATASETS,
        "public_geo_datasets": PUBLIC_GEO_DATASETS,
        "case_suite": args.case_suite,
        "sample_count": args.sample_count,
        "rows": rows,
        "claim_boundary": {
            "public_dataset_evidence": True,
            "cupy_grouped_grid_fairness_baseline": not args.skip_cupy_grouped_grid,
            "xhd_seeded_pruned_rtdl_path": not args.skip_rtdl_pruned,
            "xhd_paper_graphics_dataset_names": args.case_suite in {"xhd-graphics", "all"},
            "public_geo_dataset_family": args.case_suite == "public-geo",
            "xhd_original_wkt_files": False,
            "xhd_paper_exact_dataset_evidence": False,
            "xy_projection_only": True,
            "three_dimensional_surface_hausdorff_claim": False,
            "release_speedup_claim_authorized": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Public Stanford-scan Hausdorff dataset perf harness.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "scratch" / "public_hausdorff")
    parser.add_argument("--case-suite", choices=("stanford", "xhd-graphics", "public-geo", "all"), default="stanford")
    parser.add_argument("--sample-count", type=int, default=131072)
    parser.add_argument("--group-size", type=int)
    parser.add_argument("--seed-sample-count", type=int, default=8192)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--skip-cupy", action="store_true")
    parser.add_argument("--skip-cupy-grouped-grid", action="store_true")
    parser.add_argument("--skip-rtdl", action="store_true")
    parser.add_argument("--skip-rtdl-pruned", action="store_true")
    parser.add_argument("--commit-label", default="")
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = run(args)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
