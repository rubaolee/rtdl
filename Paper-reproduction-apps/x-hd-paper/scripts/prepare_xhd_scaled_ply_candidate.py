#!/usr/bin/env python3
"""Prepare a scaled PLY vertex candidate for X-HD paper-app provenance gates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np

from xhd_input_loader import load_points_matrix


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_binary_big_endian_ply_vertices(path: Path, points: np.ndarray) -> None:
    coords = np.asarray(points, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[1] not in {2, 3}:
        raise ValueError(f"expected 2-D point matrix with 2 or 3 columns, got {coords.shape}")
    path.parent.mkdir(parents=True, exist_ok=True)
    props = ["property float x", "property float y"]
    if coords.shape[1] == 3:
        props.append("property float z")
    header = "\n".join(
        [
            "ply",
            "format binary_big_endian 1.0",
            f"element vertex {coords.shape[0]}",
            *props,
            "element face 0",
            "property list uchar int vertex_indices",
            "end_header",
        ]
    ).encode("ascii") + b"\n"
    with path.open("wb") as fh:
        fh.write(header)
        coords.astype(">f4", copy=False).tofile(fh)


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    input_path = Path(args.input)
    output_path = Path(args.output)
    points = load_points_matrix(input_path, n_dims=int(args.n_dims), input_type="ply")
    scaled = points * float(args.scale)
    write_binary_big_endian_ply_vertices(output_path, scaled)
    extents = (scaled.max(axis=0) - scaled.min(axis=0)).tolist()
    summary = {
        "schema": "rtdl.paper_reproduction.xhd.scaled_ply_candidate.v1",
        "goal": args.run_goal,
        "input": str(input_path),
        "output": str(output_path),
        "n_dims": int(args.n_dims),
        "scale": float(args.scale),
        "vertex_count": int(scaled.shape[0]),
        "output_format": "binary_big_endian 1.0",
        "faces_preserved": False,
        "coordinate_extents_after_scale": [float(value) for value in extents],
        "input_sha256": sha256_file(input_path),
        "output_sha256": sha256_file(output_path),
        "claim_boundary": {
            "app_owned_input_preprocessing": True,
            "exact_paper_dataset_identity_claimed": False,
            "paper_figure_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
    }
    if args.summary:
        summary_path = Path(args.summary)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--scale", type=float, required=True)
    parser.add_argument("--n-dims", type=int, default=3)
    parser.add_argument("--run-goal", default="Goal5234")
    args = parser.parse_args(list(argv) if argv is not None else None)
    summary = build_summary(args)
    print(
        "wrote",
        summary["output"],
        "vertices=",
        summary["vertex_count"],
        "scale=",
        summary["scale"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
