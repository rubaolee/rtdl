from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
from typing import Any

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal4071_rt_dbscan_current_recommended_route_after_partition_pod.json"


def _source_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _component_size_signature(signature: dict[str, Any]) -> list[int]:
    if "component_sizes" in signature:
        return sorted(int(value) for value in signature["component_sizes"])
    cluster_sizes = signature.get("cluster_sizes")
    if isinstance(cluster_sizes, dict):
        return sorted(int(value) for value in cluster_sizes.values())
    raise ValueError(f"unsupported signature shape: {signature!r}")


def _run_route(name: str, *, mode: str, point_count: int, extra: dict[str, Any]) -> dict[str, Any]:
    print("ROUTE_START", name, mode, flush=True)
    payload = run_rt_dbscan_benchmark(
        mode=mode,
        dataset="clustered3d",
        point_count=point_count,
        radius=None,
        min_neighbors=None,
        seed=20260519,
        partner="cupy",
        include_rows=False,
        validate=False,
        **extra,
    )
    metadata = payload["metadata"]
    row = {
        "name": name,
        "mode": mode,
        "elapsed_sec": float(payload["elapsed_sec"]),
        "signature": payload["signature"],
        "component_size_signature": _component_size_signature(payload["signature"]),
        "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
        "partner": metadata.get("partner"),
        "path": metadata.get("path"),
        "signature_source": metadata.get("signature_source"),
        "column_signature_strategy": metadata.get("column_signature_strategy"),
        "partition_pair_enumeration_effective": metadata.get("partition_pair_enumeration_effective"),
        "partition_summary_pair_capacity_source": metadata.get("partition_summary_pair_capacity_source"),
        "graph_component_contract_only": metadata.get("graph_component_contract_only"),
        "full_dbscan_semantics": metadata.get("full_dbscan_semantics"),
        "materializes_python_rows": metadata.get("materializes_python_rows"),
        "materializes_component_labels": metadata.get("materializes_component_labels"),
        "release_authorized": bool(metadata.get("release_authorized", False)),
        "public_speedup_claim_authorized": bool(metadata.get("public_speedup_claim_authorized", False)),
        "rt_core_speedup_claim_authorized": bool(metadata.get("rt_core_speedup_claim_authorized", False)),
        "whole_app_speedup_claim_authorized": bool(metadata.get("whole_app_speedup_claim_authorized", False)),
        "true_zero_copy_claim_authorized": bool(metadata.get("true_zero_copy_claim_authorized", False)),
    }
    print("ROUTE_DONE", json.dumps(row, sort_keys=True), flush=True)
    return row


def run(output: pathlib.Path, point_count: int) -> dict[str, Any]:
    routes = [
        (
            "recommended_rt_core_grouped_stream_numba_signature",
            "optix_rt_core_grouped_stream_numba_column_signature_3d",
            {"repeat": 5, "warmup": 1},
        ),
        (
            "partition_count_then_emit_cupy_signature_candidate",
            "partner_cupy_prepared_partition_convergence_component_signature_3d",
            {"partition_pair_enumeration": "device_count_then_emit"},
        ),
        (
            "partner_numba_prepared_grid_components",
            "partner_numba_prepared_grid_components_3d",
            {},
        ),
        (
            "partner_cupy_prepared_grid_components",
            "partner_cupy_prepared_grid_components_3d",
            {},
        ),
    ]
    rows = [
        _run_route(name, mode=mode, point_count=point_count, extra=extra)
        for name, mode, extra in routes
    ]
    reference_signature = rows[0]["signature"]
    reference_component_size_signature = rows[0]["component_size_signature"]
    for row in rows:
        row["same_signature_as_recommended"] = row["signature"] == reference_signature
        row["same_component_size_signature_as_recommended"] = (
            row["component_size_signature"] == reference_component_size_signature
        )
        row["speedup_of_recommended_over_row"] = (
            float(row["elapsed_sec"]) / max(1.0e-12, float(rows[0]["elapsed_sec"]))
        )
    payload = {
        "goal": "Goal4071",
        "schema": "rtdl.goal4071.rt_dbscan.current_recommended_route_after_partition.v1",
        "source_commit": _source_commit(),
        "profile": "clustered3d_65536",
        "point_count": int(point_count),
        "recommended_route": rows[0]["name"],
        "claim_boundary": (
            "Internal route-positioning timing after the partition-preview chain. It does not "
            "authorize release, paper, public speedup, broad RT-core, whole-app, hidden-dispatch, "
            "automatic partner selection, app-specific engine logic, native ABI addition, or "
            "true-zero-copy claims."
        ),
        "release_authorized": False,
        "paper_speedup_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_abi_added": False,
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--point-count", type=int, default=65536)
    args = parser.parse_args()
    payload = run(args.output, args.point_count)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
