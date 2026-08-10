from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Sequence


GIB = 1024**3


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _round_up_gib(byte_count: float, *, power_of_two: bool = False) -> int:
    gib = max(1, math.ceil(byte_count / GIB))
    if not power_of_two:
        return gib
    return 1 << (gib - 1).bit_length()


def build_gate(
    q11_probe: dict[str, object],
    q42_probe: dict[str, object],
    *,
    sf1_dataset_bytes: int,
    sf1_packet_matrix_bytes: int,
    safety_factor: float = 1.2,
) -> dict[str, object]:
    probes = (q11_probe, q42_probe)
    if any(int(probe["returncode"]) != 0 for probe in probes):
        raise ValueError("all resource probes must complete successfully")
    if safety_factor < 1.0:
        raise ValueError("safety_factor must be at least 1.0")
    peak_rss = max(int(probe["peak_process_rss_bytes"]) for probe in probes)
    peak_gpu = max(int(probe["peak_process_gpu_bytes"]) for probe in probes)
    if peak_rss <= 0 or peak_gpu <= 0:
        raise ValueError("resource probes must observe positive host and GPU peaks")
    inventory = q42_probe["gpu_inventory_before"]
    if not isinstance(inventory, list) or len(inventory) != 1:
        raise ValueError("the first resource gate requires exactly one observed GPU")
    host_available = int(q42_probe["host_memory_before"]["MemAvailable"])
    gpu_free = int(inventory[0]["memory_free_bytes"])
    disk_free = int(q42_probe["tmp_disk_before"]["free_bytes"])

    sf1_rows = 6_001_215
    targets = []
    for scale_factor, row_count, scratch_floor_gib in (
        (10, None, 50),
        (20, 119_994_608, 100),
    ):
        ratio = float(scale_factor) if row_count is None else float(row_count) / float(sf1_rows)
        projected_rss = math.ceil(peak_rss * ratio)
        projected_gpu = math.ceil(peak_gpu * ratio)
        projected_disk = math.ceil((sf1_dataset_bytes + sf1_packet_matrix_bytes) * ratio)
        recommended_rss = math.ceil(projected_rss * safety_factor)
        recommended_gpu = math.ceil(projected_gpu * safety_factor)
        recommended_disk = math.ceil(projected_disk * safety_factor)
        host_pass = host_available >= recommended_rss
        gpu_pass = gpu_free >= recommended_gpu
        disk_pass = disk_free >= recommended_disk
        targets.append(
            {
                "target": f"sf{scale_factor}",
                "scale_ratio_from_observed_sf1": ratio,
                "author_row_count": row_count,
                "projected_full_envelope": {
                    "peak_process_rss_bytes": projected_rss,
                    "peak_process_gpu_bytes": projected_gpu,
                    "dataset_plus_packet_matrix_bytes": projected_disk,
                },
                "recommended_with_safety_factor": {
                    "peak_process_rss_bytes": recommended_rss,
                    "peak_process_gpu_bytes": recommended_gpu,
                    "dataset_plus_packet_matrix_bytes": recommended_disk,
                },
                "observed_host_capacity": {
                    "host_memory_pass": host_pass,
                    "gpu_memory_pass": gpu_pass,
                    "scratch_disk_pass": disk_pass,
                    "all_pass": host_pass and gpu_pass and disk_pass,
                },
                "recommended_pod_class": {
                    "host_ram_gib": _round_up_gib(recommended_rss, power_of_two=True),
                    "gpu_memory_gib": _round_up_gib(recommended_gpu, power_of_two=True),
                    "scratch_disk_gib": max(scratch_floor_gib, _round_up_gib(recommended_disk)),
                },
            }
        )

    return {
        "schema": "rtdl.paper_reproduction.raydb.scale_resource_gate.v1",
        "host": "lx1",
        "gpu": inventory[0]["name"],
        "observed_sf1": {
            "row_count": sf1_rows,
            "q11_peak_process_rss_bytes": int(q11_probe["peak_process_rss_bytes"]),
            "q11_peak_process_gpu_bytes": int(q11_probe["peak_process_gpu_bytes"]),
            "q42_peak_process_rss_bytes": int(q42_probe["peak_process_rss_bytes"]),
            "q42_peak_process_gpu_bytes": int(q42_probe["peak_process_gpu_bytes"]),
            "conservative_peak_process_rss_bytes": peak_rss,
            "conservative_peak_process_gpu_bytes": peak_gpu,
            "dataset_bytes": sf1_dataset_bytes,
            "packet_matrix_bytes": sf1_packet_matrix_bytes,
        },
        "observed_capacity": {
            "host_memory_available_bytes": host_available,
            "gpu_memory_free_bytes": gpu_free,
            "scratch_disk_free_bytes": disk_free,
        },
        "projection_model": {
            "name": "conservative_linear_full_observed_envelope",
            "safety_factor": safety_factor,
            "description": "Scale the complete observed SF1 process/GPU/disk envelope by target row ratio, then add safety headroom.",
            "limitations": [
                "This is a capacity gate, not a runtime prediction or performance result.",
                "Fixed runtime/context costs make the projection conservative at larger scales.",
                "Generator and DuckDB preprocessing peaks are not measured separately and remain a host-RAM risk.",
            ],
        },
        "targets": targets,
        "decision": {
            "current_host_sf10": "blocked_by_host_and_gpu_memory" if not targets[0]["observed_host_capacity"]["all_pass"] else "resource_gate_passed",
            "current_host_sf20": "blocked_by_host_and_gpu_memory" if not targets[1]["observed_host_capacity"]["all_pass"] else "resource_gate_passed",
            "next_action": "use_an_adequately_sized_pod_for_sf10_then_sf20; do_not_treat_capacity_as_correctness_failure",
        },
        "claim_boundary": {
            "sf10_executed": False,
            "sf20_executed": False,
            "capacity_projection_is_measured_execution": False,
            "paper_performance_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the RayDB SF10/SF20 resource gate")
    parser.add_argument("--q11-probe", type=Path, required=True)
    parser.add_argument("--q42-probe", type=Path, required=True)
    parser.add_argument("--sf1-dataset-bytes", type=int, required=True)
    parser.add_argument("--sf1-packet-matrix-bytes", type=int, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    result = build_gate(
        _load(args.q11_probe),
        _load(args.q42_probe),
        sf1_dataset_bytes=args.sf1_dataset_bytes,
        sf1_packet_matrix_bytes=args.sf1_packet_matrix_bytes,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["decision"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
