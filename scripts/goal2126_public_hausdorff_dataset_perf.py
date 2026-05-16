from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import struct
import sys
import tarfile
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_hausdorff_v2_function as hd


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


def make_public_cases(data_dir: Path, *, sample_count: int) -> dict[str, dict[str, object]]:
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


def _run_cupy(points_a: np.ndarray, points_b: np.ndarray, *, warmup: int) -> dict[str, object]:
    start = time.perf_counter()
    result = hd.hausdorff_distance_2d(points_a, points_b, method="cupy_rawkernel", warmup=warmup)
    return {
        "ok": True,
        "elapsed_sec": time.perf_counter() - start,
        "distance": result.distance,
        "direction": result.direction,
        "source_index": result.source_index,
        "target_index": result.target_index,
    }


def _run_rtdl_grouped_reduced(points_a: np.ndarray, points_b: np.ndarray, *, group_size: int) -> dict[str, object]:
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
    cases = make_public_cases(args.data_dir, sample_count=args.sample_count)
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
            "source_paths": case["source_paths"],
            "projection": "XY projection from public 3D PLY vertices; not a 3D surface Hausdorff claim",
            "target_points_per_group": group_size,
        }
        if not args.skip_cupy:
            print(f"[goal2126] case={name} CuPy baseline start", flush=True)
            row["cupy_rawkernel"] = _safe_call("cupy_rawkernel", lambda: _run_cupy(points_a, points_b, warmup=args.warmup))
            print(
                f"[goal2126] case={name} CuPy done ok={row['cupy_rawkernel'].get('ok')} "
                f"sec={row['cupy_rawkernel'].get('elapsed_sec')}",
                flush=True,
            )
        if not args.skip_rtdl:
            print(f"[goal2126] case={name} RTDL/OptiX grouped reduced start", flush=True)
            row["rtdl_rt_grouped_reduced_nearest_witness"] = _safe_call(
                "rtdl_rt_grouped_reduced_nearest_witness",
                lambda: _run_rtdl_grouped_reduced(points_a, points_b, group_size=group_size),
            )
            print(
                f"[goal2126] case={name} RTDL done ok={row['rtdl_rt_grouped_reduced_nearest_witness'].get('ok')} "
                f"sec={row['rtdl_rt_grouped_reduced_nearest_witness'].get('elapsed_sec')}",
                flush=True,
            )
        cupy = row.get("cupy_rawkernel")
        rtdl = row.get("rtdl_rt_grouped_reduced_nearest_witness")
        if isinstance(cupy, dict) and isinstance(rtdl, dict) and cupy.get("ok") and rtdl.get("ok"):
            row["matches_cupy"] = math.isclose(
                float(cupy["distance"]),
                float(rtdl["distance"]),
                rel_tol=args.tolerance,
                abs_tol=args.tolerance,
            )
            row["rtdl_vs_cupy_ratio"] = float(rtdl["elapsed_sec"]) / float(cupy["elapsed_sec"])
        rows.append(row)
    return {
        "goal": "goal2126_public_hausdorff_dataset_perf",
        "commit": args.commit_label,
        "gpu": _gpu_summary(),
        "datasets": STANFORD_DATASETS,
        "sample_count": args.sample_count,
        "rows": rows,
        "claim_boundary": {
            "public_dataset_evidence": True,
            "xhd_paper_exact_dataset_evidence": False,
            "xy_projection_only": True,
            "three_dimensional_surface_hausdorff_claim": False,
            "release_speedup_claim_authorized": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Public Stanford-scan Hausdorff dataset perf harness.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "scratch" / "public_hausdorff")
    parser.add_argument("--sample-count", type=int, default=131072)
    parser.add_argument("--group-size", type=int)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--skip-cupy", action="store_true")
    parser.add_argument("--skip-rtdl", action="store_true")
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
