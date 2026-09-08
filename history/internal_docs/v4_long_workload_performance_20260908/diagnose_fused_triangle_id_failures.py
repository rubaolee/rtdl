#!/usr/bin/env python3
"""GPU diagnostic for fused generic triangle/ray canonical-ID validation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _expect_failure(call, expected: str) -> str:
    try:
        call()
    except RuntimeError as error:
        observed = str(error)
        if expected not in observed:
            raise RuntimeError(
                f"expected failure {expected!r}, observed {observed!r}") from error
        return observed
    raise RuntimeError(f"expected failure was not raised: {expected}")


def main() -> int:
    args = _args()
    if args.output.exists():
        raise FileExistsError(args.output)
    root = args.source_root.resolve(strict=True)
    config_path = args.config.resolve(strict=True)
    config = dict(json.loads(config_path.read_text(encoding="utf-8")))
    config["source_root"] = str(root)

    import cupy as cp
    from scripts import v4_paper_apps_pyoptix_worker as worker

    data, input_identity = worker._load_input(
        "triangle_counting", config, operation=None)
    app = worker._load_module(
        root / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
        "v4_fused_id_failure_triangle_app",
    )
    owner = app.prepare_v4_segmented(
        "RT-2A1",
        **worker._rtdl_runtime(config),
        edge_file=str(data["edge_file"]),
        expected_triangle_count=int(data["expected_triangle_count"]),
        max_relation_rows=int(data["max_relation_rows"]),
        prepared_graph_contract=data["graph_contract"],
    )
    try:
        segment = next(iter(data["segment_iterator"](
            data["graph_contract"],
            paper_algorithm="RT-2A1",
            max_relation_rows=int(data["max_relation_rows"]),
            max_directed_edge_rows=int(data["max_relation_rows"]),
        )))
        triangles = segment["triangles"]
        rays = segment["rays"]
        weights = segment["ray_weights"]

        bad_triangles = dict(triangles)
        bad_triangles["ids"] = triangles["ids"].copy()
        bad_triangles["ids"][0] = cp.uint32(1)
        cp.cuda.get_current_stream().synchronize()
        triangle_error = _expect_failure(
            lambda: owner.executor.execute_segment(
                bad_triangles, rays, ray_weights=weights),
            "V4 triangle device-column IDs are not canonical launch order",
        )

        bad_rays = dict(rays)
        bad_rays["ids"] = rays["ids"].copy()
        bad_rays["ids"][0] = cp.uint32(1)
        cp.cuda.get_current_stream().synchronize()
        ray_error = _expect_failure(
            lambda: owner.executor.execute_segment(
                triangles, bad_rays, ray_weights=weights),
            "V4 ray device-column IDs are not canonical launch order",
        )

        positive = owner.executor.execute_segment(
            triangles, rays, ray_weights=weights)
        if positive.get("per_ray_host_materialized") is not False:
            raise RuntimeError("positive control materialized per-ray output")
        if int(positive["query_count"]) != int(rays["ids"].size):
            raise RuntimeError("positive-control query count mismatch")
        payload = {
            "schema": "rtdl.v4_long_workload.fused_triangle_id_gpu_diagnostic.v1",
            "formal_evidence": False,
            "pooling_into_formal_transaction_forbidden": True,
            "status": "PASS__BOTH_FUSED_ID_FAILURES_AND_POSITIVE_CONTROL",
            "input_identity": input_identity,
            "config_sha256": _sha256(config_path),
            "native_library_sha256": config["native_library_sha256"],
            "triangle_failure": triangle_error,
            "ray_failure": ray_error,
            "positive_control": {
                "query_count": int(positive["query_count"]),
                "triangle_count": int(positive["triangle_count"]),
                "reduced_output": int(positive["reduced_output"]),
                "per_ray_host_materialized": False,
                "physical_executor_classification": positive[
                    "traversal_receipt"]["physical_executor_classification"],
            },
        }
    finally:
        owner.close()
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "output": str(args.output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
