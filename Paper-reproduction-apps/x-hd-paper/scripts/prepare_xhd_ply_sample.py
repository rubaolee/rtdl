from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

from xhd_input_loader import load_ascii_ply_vertices


def deterministic_sample(points: list[tuple[float, ...]], *, count: int) -> list[tuple[float, ...]]:
    if count <= 0:
        raise ValueError("sample count must be positive")
    if not points:
        raise ValueError("cannot sample an empty point set")
    if count >= len(points):
        return list(points)
    if count == 1:
        return [points[0]]
    last = len(points) - 1
    indices = sorted({round(i * last / (count - 1)) for i in range(count)})
    return [points[index] for index in indices]


def write_ascii_ply_vertices(path: Path, points: list[tuple[float, ...]]) -> None:
    if not points:
        raise ValueError("cannot write an empty PLY point set")
    n_dims = len(points[0])
    if n_dims not in {2, 3}:
        raise ValueError("PLY writer supports only 2D or 3D coordinates")
    for point in points:
        if len(point) != n_dims:
            raise ValueError("all sampled points must have the same dimension")
    rows = [
        "ply",
        "format ascii 1.0",
        f"element vertex {len(points)}",
        "property float x",
        "property float y",
    ]
    if n_dims == 3:
        rows.append("property float z")
    rows.extend(
        [
            "element face 0",
            "property list uchar int vertex_indices",
            "end_header",
        ]
    )
    rows.extend(" ".join(f"{value:.17g}" for value in point) for point in points)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    input_path = Path(args.input)
    output_path = Path(args.output)
    points = load_ascii_ply_vertices(input_path, n_dims=args.n_dims)
    sample = deterministic_sample(points, count=args.count)
    write_ascii_ply_vertices(output_path, sample)
    return {
        "schema": "rtdl.paper_reproduction.xhd.ply_sample.v1",
        "input": str(input_path),
        "output": str(output_path),
        "n_dims": args.n_dims,
        "input_point_count": len(points),
        "sample_point_count": len(sample),
        "sampling": "deterministic_even_index_sample_including_first_and_last",
        "output_sha256": sha256_file(output_path),
        "claim_boundary": {
            "same_source_sample": True,
            "exact_paper_dataset_reproduction_claimed": False,
            "performance_claimed": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare a deterministic bounded PLY sample for X-HD gates.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--n-dims", type=int, default=3)
    parser.add_argument("--count", type=int, default=256)
    args = parser.parse_args(list(argv) if argv is not None else None)
    summary = build_summary(args)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
