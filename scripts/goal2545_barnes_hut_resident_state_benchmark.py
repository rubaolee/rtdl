from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.v2_0.apps.simulation import rtdl_barnes_hut_force_app as app
from scripts.goal2544_barnes_hut_torch_cuda_subtree_containment import (
    CPP_SOURCE,
    CUDA_SOURCE,
    _prepare_subtree_arrays,
)


def run_resident_state_benchmark(
    *,
    body_count: int,
    bucket_size: int,
    max_depth: int,
    theta: float,
    softening: float,
    timesteps: int,
    warmups: int,
) -> dict[str, Any]:
    import torch
    from torch.utils.cpp_extension import load_inline

    if timesteps < 1:
        raise ValueError("timesteps must be positive")
    if warmups < 0:
        raise ValueError("warmups must be non-negative")
    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is required for this partner-resident benchmark")

    os.environ.setdefault("MAX_JOBS", "2")
    os.environ.setdefault("TORCH_CUDA_ARCH_LIST", "8.6")

    prepare_start = time.perf_counter()
    prepared = _prepare_subtree_arrays(body_count, bucket_size, max_depth)
    tree_prepare_ms = (time.perf_counter() - prepare_start) * 1000.0

    compile_start = time.perf_counter()
    module = load_inline(
        name="rtdl_goal2544_fused_frontier_subtree_vector_sum",
        cpp_sources=[CPP_SOURCE],
        cuda_sources=[CUDA_SOURCE],
        functions=["fused_frontier_vector_sum_subtree_cuda"],
        extra_cuda_cflags=["--use_fast_math"],
        verbose=False,
    )
    compile_ms = (time.perf_counter() - compile_start) * 1000.0

    device = torch.device("cuda:0")
    tensor_start = time.perf_counter()
    tensors = {
        "point_x": torch.tensor(prepared["point_x"], dtype=torch.float64, device=device).contiguous(),
        "point_y": torch.tensor(prepared["point_y"], dtype=torch.float64, device=device).contiguous(),
        "point_mass": torch.tensor(prepared["point_mass"], dtype=torch.float64, device=device).contiguous(),
        "node_cx": torch.tensor(prepared["node_cx"], dtype=torch.float64, device=device).contiguous(),
        "node_cy": torch.tensor(prepared["node_cy"], dtype=torch.float64, device=device).contiguous(),
        "node_half_size": torch.tensor(prepared["node_half_size"], dtype=torch.float64, device=device).contiguous(),
        "node_mass": torch.tensor(prepared["node_mass"], dtype=torch.float64, device=device).contiguous(),
        "node_resume_index": torch.tensor(prepared["node_resume_index"], dtype=torch.int64, device=device).contiguous(),
        "node_subtree_end_index": torch.tensor(prepared["node_subtree_end_index"], dtype=torch.int64, device=device).contiguous(),
        "source_leaf_node_index": torch.tensor(prepared["source_leaf_node_index"], dtype=torch.int64, device=device).contiguous(),
        "member_offsets": torch.tensor(prepared["member_offsets"], dtype=torch.int64, device=device).contiguous(),
        "member_indices": torch.tensor(prepared["member_indices"], dtype=torch.int64, device=device).contiguous(),
        "child_offsets": torch.tensor(prepared["child_offsets"], dtype=torch.int64, device=device).contiguous(),
        "child_indices": torch.tensor(prepared["child_indices"], dtype=torch.int64, device=device).contiguous(),
    }
    torch.cuda.synchronize()
    tensor_prepare_ms = (time.perf_counter() - tensor_start) * 1000.0

    def launch():
        return module.fused_frontier_vector_sum_subtree_cuda(
            tensors["point_x"],
            tensors["point_y"],
            tensors["point_mass"],
            tensors["node_cx"],
            tensors["node_cy"],
            tensors["node_half_size"],
            tensors["node_mass"],
            tensors["node_resume_index"],
            tensors["node_subtree_end_index"],
            tensors["source_leaf_node_index"],
            tensors["member_offsets"],
            tensors["member_indices"],
            tensors["child_offsets"],
            tensors["child_indices"],
            float(theta),
            float(softening),
        )

    for _ in range(warmups):
        launch()
    torch.cuda.synchronize()

    event_times: list[float] = []
    last_output = None
    wall_start = time.perf_counter()
    for _ in range(timesteps):
        start_event = torch.cuda.Event(enable_timing=True)
        end_event = torch.cuda.Event(enable_timing=True)
        start_event.record()
        last_output = launch()
        end_event.record()
        torch.cuda.synchronize()
        event_times.append(float(start_event.elapsed_time(end_event)))
    resident_wall_ms = (time.perf_counter() - wall_start) * 1000.0
    assert last_output is not None
    out_x, out_y, out_visited, out_aggregate, out_exact, status = last_output
    status_value = int(status.cpu().item())
    if status_value != 0:
        raise RuntimeError(f"CUDA subtree kernel returned status {status_value}")

    return {
        "benchmark": "barnes_hut_ppopp2025_style",
        "backend": "torch_cuda_extension_subtree_containment_resident_state",
        "contract": rt.AGGREGATE_FRONTIER_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
        "body_count": body_count,
        "bucket_size": bucket_size,
        "theta": theta,
        "softening": softening,
        "device": torch.cuda.get_device_name(0),
        "timesteps": timesteps,
        "warmups": warmups,
        "timing_ms": {
            "tree_prepare_cpu": tree_prepare_ms,
            "extension_compile": compile_ms,
            "tensor_prepare_host_to_device": tensor_prepare_ms,
            "resident_event_min": min(event_times),
            "resident_event_mean": sum(event_times) / len(event_times),
            "resident_event_total": sum(event_times),
            "resident_wall_total": resident_wall_ms,
            "resident_wall_per_timestep": resident_wall_ms / timesteps,
            "resident_event_runs": event_times,
        },
        "last_result": {
            "checksum_force_x": float(out_x.sum().cpu().item()),
            "checksum_force_y": float(out_y.sum().cpu().item()),
            "visited_node_total": int(out_visited.sum().cpu().item()),
            "aggregate_contribution_row_count": int(out_aggregate.sum().cpu().item()),
            "exact_contribution_row_count": int(out_exact.sum().cpu().item()),
        },
        "metadata": {
            "prepared_tree_reused": True,
            "prepared_tensors_reused": True,
            "partner_resident_kernel": True,
            "native_engine_app_specific": False,
            "authors_code_comparison": False,
            "paper_reproduction": False,
            "public_speedup_claim_authorized": False,
            "claim_boundary": (
                "Resident-state repeated-launch timing for the generic 2-D fused vector-sum contract. "
                "This excludes tree rebuilds and host-to-device preparation after the first setup."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resident-state repeated-launch benchmark for the Goal2544 subtree kernel.")
    parser.add_argument("--body-count", type=int, default=32768)
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--theta", type=float, default=app.THETA)
    parser.add_argument("--softening", type=float, default=app.SOFTENING)
    parser.add_argument("--timesteps", type=int, default=100)
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    payload = run_resident_state_benchmark(
        body_count=args.body_count,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
        theta=args.theta,
        softening=args.softening,
        timesteps=args.timesteps,
        warmups=args.warmups,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
