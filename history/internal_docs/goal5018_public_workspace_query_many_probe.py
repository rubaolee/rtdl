#!/usr/bin/env python3
"""Goal5018 probe: prepared-base query-many via public workspace query API."""

from __future__ import annotations

import argparse
import gc
import importlib.util
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace


def _load_goal5012(repo: Path):
    path = repo / "history" / "internal_docs" / "goal5012_overlay_shared_point_query_probe.py"
    spec = importlib.util.spec_from_file_location("goal5012_overlay_shared_point_query_probe", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_app(repo: Path):
    app_dir = repo / "Paper-reproduction-apps" / "rayjoin-paper"
    src_dir = repo / "src"
    sys.path.insert(0, str(app_dir))
    sys.path.insert(0, str(src_dir))
    import section57_overlay_columnar_binary as app  # type: ignore

    return app


def _run_public_workspace_query(app, goal5012, *, args_template, workspace, workspace_query, shared_base_points):
    query_points_in_base = None
    query_points_start = time.perf_counter()
    query_points_in_base = workspace_query.prepare_query_points_in_base()
    query_points_sec = time.perf_counter() - query_points_start
    try:
        args = SimpleNamespace(**vars(args_template))
        setattr(args, "_preloaded_left", workspace_query.query)
        setattr(args, "_preloaded_right", workspace.right)
        setattr(args, "_preloaded_bounds", workspace.bounds)
        setattr(args, "_prepared_lsi_session", workspace.lsi)
        setattr(args, "_prepared_lsi_query", workspace_query.lsi_query)
        setattr(args, "_prepared_point_location_map0_in_map1", workspace.left_in_right)
        setattr(args, "_prepared_point_location_map1_in_map0", workspace_query.base_points_in_query)
        setattr(args, "_prepared_vertex_points_map0_in_map1", query_points_in_base)
        setattr(args, "_prepared_vertex_points_map1_in_map0", shared_base_points)
        setattr(args, "_prepared_operator_session_active", True)

        run_start = time.perf_counter()
        summary = app.run_pipeline(args)
        run_elapsed = time.perf_counter() - run_start
        compact = goal5012._compact_overlay_summary(summary)
        setup = dict(workspace_query.setup_phase_seconds or {})
        total_body = (
            float(setup.get("prepare_lsi_query_sec", 0.0))
            + float(setup.get("prepare_point_location_base_in_query_sec", 0.0))
            + float(query_points_sec)
            + float(compact["writer_free_hot_sec"])
        )
        return {
            "query_setup_phase_seconds": setup,
            "prepare_query_points_in_base_sec": float(query_points_sec),
            "run_pipeline_elapsed_sec": float(run_elapsed),
            "writer_free_hot_sec_excluding_external_prepares": compact["writer_free_hot_sec"],
            "total_body_sec_including_query_prepares": float(total_body),
            "summary_compact": compact,
            "public_workspace_query_api_used": True,
            "shared_base_points_from_workspace_used": True,
        }
    finally:
        if query_points_in_base is not None:
            query_points_in_base.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--capacity", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    app = _load_app(args.repo)
    goal5012 = _load_goal5012(args.repo)
    import rtdsl as rt

    base = app.base

    result: dict[str, object] = {
        "schema": "rtdl.goal5018.public_workspace_query_many_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
        "capacity": int(args.capacity),
        "regime_under_test": "prepared_base_same_scale_domain_distinct_query_batches_public_workspace_api",
        "claim_boundary": {
            "true_query_many_distinct_batches": True,
            "prepared_replay_same_input": False,
            "public_workspace_query_api": True,
            "bundled_rayjoin_helper_used": False,
            "ten_x_claim_authorized": False,
            "author_performance_parity_claim_authorized": False,
        },
    }

    load_start = time.perf_counter()
    left = base.load_dataset_arrays(args.left)
    right = base.load_dataset_arrays(args.right)
    result["load_dataset_arrays_sec"] = float(time.perf_counter() - load_start)

    variants = []
    for batch_id in (1, 2, 3):
        variant_start = time.perf_counter()
        variant, changed_points = goal5012._make_distinct_dataset_variant(app, left, batch_id=batch_id)
        variants.append(
            {
                "batch_id": int(batch_id),
                "variant": variant,
                "changed_point_count": int(len(changed_points)),
                "variant_build_sec_not_in_body": float(time.perf_counter() - variant_start),
            }
        )

    args_template = goal5012._build_run_args(args.left, args.right, args.capacity)
    query_results = []
    workspace = None
    shared_base_points = None
    try:
        workspace_start = time.perf_counter()
        workspace = rt.prepare_planar_map_workspace_2d_optix(
            left,
            right,
            prepare_lsi=True,
            prepare_point_location=True,
        )
        result["workspace_prepare_wall_sec"] = float(time.perf_counter() - workspace_start)
        result["workspace_metadata"] = workspace.metadata()

        shared_start = time.perf_counter()
        shared_base_points = workspace.prepare_base_points_for_queries()
        result["shared_base_points_prepare_sec"] = float(time.perf_counter() - shared_start)

        for item in variants:
            with workspace.prepare_query(
                item["variant"],
                prepare_lsi=True,
                prepare_point_location=True,
            ) as workspace_query:
                row = _run_public_workspace_query(
                    app,
                    goal5012,
                    args_template=args_template,
                    workspace=workspace,
                    workspace_query=workspace_query,
                    shared_base_points=shared_base_points,
                )
                row["batch_id"] = int(item["batch_id"])
                row["changed_point_count"] = int(item["changed_point_count"])
                row["variant_build_sec_not_in_body"] = float(item["variant_build_sec_not_in_body"])
                row["query_metadata"] = workspace_query.metadata()
                query_results.append(row)
            gc.collect()
    finally:
        if shared_base_points is not None:
            shared_base_points.close()
        if workspace is not None:
            workspace.close()

    result["query_results"] = query_results
    result["decision_inputs"] = {
        "distinct_query_count": len(query_results),
        "total_body_sec": [row["total_body_sec_including_query_prepares"] for row in query_results],
        "writer_free_hot_sec_excluding_external_prepares": [
            row["writer_free_hot_sec_excluding_external_prepares"] for row in query_results
        ],
        "lsi_row_counts": [row["summary_compact"]["lsi_row_count"] for row in query_results],
        "descriptor_pair_counts": [row["summary_compact"]["descriptor_pair_count"] for row in query_results],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
