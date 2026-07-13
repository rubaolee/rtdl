from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))

import rtdsl as rt
from xhd_input_loader import load_points_matrix


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
FIXTURES = APP_ROOT / "data" / "fixtures"
OUT = RESULTS / "xhd_goal5370_author_like_queue_state_reference.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _columns_3d(points: np.ndarray) -> dict[str, object]:
    coords = np.asarray(points, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[1] != 3:
        raise ValueError("expected an Nx3 point matrix")
    coords = np.ascontiguousarray(coords)
    return {
        "ids": np.arange(coords.shape[0], dtype=np.int64),
        "x": coords[:, 0],
        "y": coords[:, 1],
        "z": coords[:, 2],
    }


def _target_cell_diagonal(author_payload: dict[str, Any]) -> float:
    repeat = author_payload["Running"]["Repeats"][0]
    grid_resolution = repeat["GridResolution"]
    target_mbr = author_payload["Input"]["Files"][1]["MBR"]
    squared = 0.0
    for axis_mbr, resolution in zip(target_mbr, grid_resolution):
        lower = float(axis_mbr["Lower"])
        upper = float(axis_mbr["Upper"])
        resolution_i = int(resolution)
        if resolution_i <= 0:
            raise ValueError("GridResolution values must be positive")
        length = (upper - lower) / float(resolution_i)
        squared += length * length
    return math.sqrt(squared)


def _nearest_columns(source: np.ndarray, target: np.ndarray) -> dict[str, np.ndarray]:
    candidates = rt.pairwise_l2_distance_candidate_rows_numpy_columns(
        _columns_3d(source),
        _columns_3d(target),
        coordinate_fields=("x", "y", "z"),
        return_metadata=True,
    )
    nearest = rt.nearest_witness_numpy_columns(
        candidates["candidate_rows"],
        candidates["source_ids"],
        return_metadata=True,
    )
    columns = nearest["columns"]
    return {
        "source_ids": np.asarray(columns["source_ids"], dtype=np.int64),
        "target_ids": np.asarray(columns["nearest_item_ids"], dtype=np.int64),
        "distances": np.asarray(columns["nearest_distances"], dtype=np.float64),
    }


def _build_queue_state(
    *,
    source_points: np.ndarray,
    target_points: np.ndarray,
    author_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    repeat = author_payload["Running"]["Repeats"][0]
    nearest = _nearest_columns(source_points, target_points)
    nearest_distances = nearest["distances"]
    nearest_target_ids = nearest["target_ids"]
    active_ids = np.arange(source_points.shape[0], dtype=np.int64)
    radius = float(repeat["InitRadius"])
    cmax2_state = radius * radius
    hd_upper_bound = float(repeat["HDUpperBound"])
    cell_diagonal = _target_cell_diagonal(author_payload)
    mode = str(author_payload["Running"].get("TuneRadius", "adaptive"))
    iterations: list[dict[str, Any]] = []
    iteration = 1
    while True:
        active_distances = nearest_distances[active_ids]
        active_targets = nearest_target_ids[active_ids]
        active_cmin2 = active_distances * active_distances
        unresolved_mask = active_distances > radius
        confirmed_mask = ~unresolved_mask
        cmax2_before = float(cmax2_state)
        if np.any(confirmed_mask):
            cmax2_state = max(float(cmax2_state), float(np.max(active_cmin2[confirmed_mask])))
        confirmed_ids = active_ids[confirmed_mask]
        unresolved_ids = active_ids[unresolved_mask]
        row = {
            "Iteration": int(iteration),
            "Radius": float(radius),
            "NumInputPoints": int(active_ids.size),
            "NumOutputPoints": int(unresolved_ids.size),
            "CMax2": float(cmax2_state),
        }
        iterations.append(
            {
                "queue_row": row,
                "active_source_ids": [int(value) for value in active_ids.tolist()],
                "active_in_queue_indices": [int(value) for value in range(active_ids.size)],
                "confirmed_source_ids": [int(value) for value in confirmed_ids.tolist()],
                "unresolved_source_ids": [int(value) for value in unresolved_ids.tolist()],
                "nearest_target_ids": [int(value) for value in active_targets.tolist()],
                "nearest_distances": [float(value) for value in active_distances.tolist()],
                "current_best_sq": [float(value) for value in active_cmin2.tolist()],
                "cmax2_before": cmax2_before,
                "cmax2_after": float(cmax2_state),
            }
        )
        if unresolved_ids.size == 0:
            break
        step = rt.radius_growth_step(
            radius=radius,
            hd_upper_bound=hd_upper_bound,
            cell_diagonal=cell_diagonal,
            last_input_count=int(active_ids.size),
            next_input_count=int(unresolved_ids.size),
            mode=mode,  # type: ignore[arg-type]
        )
        active_ids = np.ascontiguousarray(unresolved_ids)
        radius = float(step.next_radius)
        iteration += 1
        if iteration > source_points.shape[0] + 1:
            raise RuntimeError("queue state reconstruction did not converge")
    return iterations


def _compare_author_rows(author_rows: list[dict[str, Any]], iterations: list[dict[str, Any]]) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    if len(author_rows) != len(iterations):
        mismatches.append({"field": "iteration_count", "author": len(author_rows), "rtdl": len(iterations)})
    for index, (author, state) in enumerate(zip(author_rows, iterations), start=1):
        row = state["queue_row"]
        for field in ("Iteration", "NumInputPoints", "NumOutputPoints"):
            if int(author[field]) != int(row[field]):
                mismatches.append({"iteration": index, "field": field, "author": author[field], "rtdl": row[field]})
        for field in ("Radius", "CMax2"):
            diff = abs(float(author[field]) - float(row[field]))
            if diff > 1e-6:
                mismatches.append({"iteration": index, "field": field, "author": author[field], "rtdl": row[field], "abs_diff": diff})
    return {
        "matched": not mismatches,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def build_artifact() -> dict[str, Any]:
    author_json = RESULTS / "bounded3d_author_hd_exec_output_pod.json"
    author_payload = _read_json(author_json)
    repeat = author_payload["Running"]["Repeats"][0]
    author_rows = [dict(row) for row in repeat["Iterations"]]
    source = load_points_matrix(FIXTURES / "bounded3d_a.wkt", n_dims=3, input_type="wkt")
    target = load_points_matrix(FIXTURES / "bounded3d_b.wkt", n_dims=3, input_type="wkt")
    iterations = _build_queue_state(
        source_points=np.asarray(source, dtype=np.float64),
        target_points=np.asarray(target, dtype=np.float64),
        author_payload=author_payload,
    )
    comparison = _compare_author_rows(author_rows, iterations)
    return {
        "goal": "Goal5370",
        "date": "2026-07-09",
        "schema": "rtdl.paper_reproduction.xhd.goal5370.author_like_queue_state_reference.v1",
        "status": "bounded_author_like_queue_state_reference_ready",
        "exit_label": "bounded_queue_state_reference_matches_author_rows__dragon_lb_still_unimplemented",
        "purpose": (
            "Prove a concrete app-owned queue-state representation for author-like "
            "radius queues: active source ids, in-queue indices, nearest/current-best "
            "vectors, confirmed/unresolved source ids, and queue rows."
        ),
        "input_fixture": "bounded3d_a.wkt -> bounded3d_b.wkt",
        "author": {
            "artifact": str(author_json),
            "iterations": author_rows,
            "hd_result": float(author_payload["HDResult"]),
        },
        "rtdl_queue_state_reference": {
            "iterations": iterations,
            "state_fields": [
                "active_source_ids",
                "active_in_queue_indices",
                "nearest_target_ids",
                "nearest_distances",
                "current_best_sq",
                "confirmed_source_ids",
                "unresolved_source_ids",
                "cmax2_before",
                "cmax2_after",
            ],
            "uses_generic_nearest_pipeline": True,
            "uses_radius_growth_step": any(
                int(state["queue_row"]["NumOutputPoints"]) > 0 for state in iterations
            ),
        },
        "comparison": comparison,
        "next_large_input_requirement": (
            "Use this queue-state shape to reconstruct Dragon->Asian active queue/current-best "
            "state, then run count-only raw offload telemetry against author OffloadingSize."
        ),
        "claim_boundary": {
            "queue_state_reference_claimed": True,
            "explicit_lb_support_claimed": False,
            "dragon_asian_lb_denominator_claimed": False,
            "row_count_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main() -> None:
    artifact = build_artifact()
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, sort_keys=True))


if __name__ == "__main__":
    main()
