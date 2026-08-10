#!/usr/bin/env python3
"""Run one Arkade V2/V3 lane and emit a correctness/physical receipt.

CPU mode is a semantics-only local gate.  OptiX mode is fail-closed unless the
native behavioral audit observes every launch with the generic 3-D AABB
program bundle and a nonzero traversable.  Neither mode records performance.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys


APP_DIR = Path(__file__).resolve().parent
ROOT = next(parent for parent in APP_DIR.parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
for value in (str(SRC), str(APP_DIR)):
    if value not in sys.path:
        sys.path.insert(0, value)

from arkade_contract import (  # noqa: E402
    AUTHOR_SAMPLE_SHA256,
    ArkadeAlgorithm,
    compare_to_oracle,
    independent_oracle,
    load_frozen_view,
    ordered_item_id_sha256,
)
from rtdsl.metric_knn import (  # noqa: E402
    cpu_aabb_candidate_provider_3d,
    optix_aabb_candidate_provider_3d,
)
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession  # noqa: E402
from rtdl3_whole_app import (  # noqa: E402
    run_v3,
    run_v3_reference_for_functional_validation,
)


PROGRAM_BUNDLE = "metric_knn_3d"


def _load_v2():
    path = APP_DIR / "v2_14_whole_app.py"
    spec = importlib.util.spec_from_file_location("arkade_v2_14_whole_app", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the Arkade V2-direct lane")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _stable_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()


def _complete_traversal_receipt(receipt: dict[str, object]) -> bool:
    snapshot = receipt["native_snapshot"]
    successful = int(snapshot["successful_launch_count"])
    return bool(
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and receipt["expected_program_observed_at_receipt_edge"] is True
        and successful > 0
        and successful == int(snapshot["complete_context_launch_count"])
        and successful == int(snapshot["context_bind_count"])
        and int(snapshot["failed_launch_count"]) == 0
        and int(snapshot["incomplete_context_launch_count"]) == 0
        and int(snapshot["pending_context_at_finish"]) == 0
        and int(snapshot["session_error"]) == 0
        and int(snapshot["first_program_bundle_id"]) != 0
        and int(snapshot["last_program_bundle_id"]) != 0
        and int(snapshot["first_traversable"]) != 0
        and int(snapshot["last_traversable"]) != 0
        and int(snapshot["raygen_invocation_count"]) > 0
    )


def run_lane(
    *,
    version: str,
    algorithm: ArkadeAlgorithm,
    view_id: str,
    backend: str,
    memory_limit_bytes: int,
) -> dict[str, object]:
    if version not in {"v2_14", "v3"}:
        raise ValueError("version must be v2_14 or v3")
    if backend not in {"cpu", "optix"}:
        raise ValueError("backend must be cpu or optix")

    payload = load_frozen_view(view_id)
    view = payload["view"]
    expected = independent_oracle(
        algorithm,
        payload["data_points"],
        payload["query_points"],
        k=view.k,
        data_ids=payload["data_ids"],
    )
    semantic_input = {
        "application": "Arkade",
        "paper_algorithm": algorithm.value,
        "view_id": view.stable_id,
        "author_sample_sha256": AUTHOR_SAMPLE_SHA256,
        "data_count": view.data_count,
        "query_count": view.query_count,
        "k": view.k,
        "output_contract": "ordered_item_ids_by_binary32_metric_then_u32_id.v2",
    }
    semantic_digest = _stable_digest(semantic_input)
    provider = (
        cpu_aabb_candidate_provider_3d
        if backend == "cpu"
        else optix_aabb_candidate_provider_3d
    )
    common = {
        "algorithm": algorithm,
        "view": view,
        "data_points": payload["data_points"],
        "query_points": payload["query_points"],
        "data_ids": payload["data_ids"],
        "query_ids": payload["query_ids"],
    }

    audit = OptixTraversalAuditSession.open() if backend == "optix" else None
    try:
        if version == "v2_14":
            result = _load_v2().run_v2_direct(
                **common,
                candidate_provider=(provider if backend == "cpu" else None),
            )
        else:
            v3_kwargs = {
                **common,
                "target_identity": {
                    "machine_class": "nvidia_optix_functional"
                    if backend == "optix"
                    else "cpu_static_functional",
                    "backend_contract_id": "nvidia.optix_traversal.v1",
                },
                "memory_limit_bytes": memory_limit_bytes,
            }
            result = (
                run_v3(**v3_kwargs)
                if backend == "optix"
                else run_v3_reference_for_functional_validation(**v3_kwargs)
            )
        compare_to_oracle(result, expected)
        output_digest = ordered_item_id_sha256(result["ordered_item_ids"])
        traversal_receipt = (
            audit.finish(
                semantic_digest=semantic_digest,
                output_digest=output_digest,
                route_identity=f"goal5745.{version}.{algorithm.value}.{view.stable_id}",
                expected_program_bundles=(PROGRAM_BUNDLE,),
            )
            if audit is not None
            else None
        )
    except BaseException:
        if audit is not None:
            audit.abort()
        raise

    traversal_ok = (
        _complete_traversal_receipt(traversal_receipt)
        if traversal_receipt is not None
        else False
    )
    if backend == "optix" and not traversal_ok:
        raise RuntimeError(
            "Arkade OptiX lane failed behavioral traversal admission: "
            + json.dumps(traversal_receipt, sort_keys=True)
        )

    return {
        "schema": "rtdl.goal5745.arkade_four_lane_functional_receipt.v1",
        "goal": 5745,
        "pid": os.getpid(),
        "version": version,
        "method": result["metadata"]["method"],
        "paper_algorithm": algorithm.value,
        "view_id": view.stable_id,
        "backend": backend,
        "semantic_input": semantic_input,
        "semantic_digest": semantic_digest,
        "ordered_item_id_sha256": output_digest,
        "expected_ordered_item_id_sha256": ordered_item_id_sha256(
            expected["ordered_item_ids"]
        ),
        "correctness_matched": True,
        "default_selected_between_paper_algorithms": False,
        "compiler_or_canonical_resolution_used": bool(
            result["metadata"]["compiler_or_canonical_resolution_used"]
        ),
        "round_count": int(result["metadata"]["completed_round_count"]),
        "native_refit_count": int(
            result["metadata"].get("native_refit_count", 0)
        ),
        "unbounded_candidate_relation_materialized": bool(
            result["metadata"].get(
                "unbounded_candidate_relation_materialized", True
            )
        ),
        "traversal_receipt": traversal_receipt,
        "behavioral_true_optix": traversal_ok,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "rt_core_silicon_utilization_claimed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=("v2_14", "v3"), required=True)
    parser.add_argument(
        "--algorithm",
        choices=tuple(value.value for value in ArkadeAlgorithm),
        required=True,
    )
    parser.add_argument("--view", required=True)
    parser.add_argument("--backend", choices=("cpu", "optix"), required=True)
    parser.add_argument("--memory-limit-bytes", type=int, default=8 << 30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_lane(
        version=args.version,
        algorithm=ArkadeAlgorithm(args.algorithm),
        view_id=args.view,
        backend=args.backend,
        memory_limit_bytes=args.memory_limit_bytes,
    )
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        if args.output.exists():
            raise FileExistsError(f"refusing to replace existing output: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
