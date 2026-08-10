#!/usr/bin/env python3
"""One fresh Arkade cold or paper-search V2/V3 observation.

The registered timer is symmetric and includes frozen input loading plus the
entire selected application lane through ordered output materialization.  The
independent oracle/comparator, traversal-receipt finalization and JSON writing
are outside the timer.  This file runs one observation only; scheduling and
statistics live in separate modules.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time


APP_DIR = Path(__file__).resolve().parent
ROOT = next(parent for parent in APP_DIR.parents if (parent / "src" / "rtdsl").exists())
for value in (str(ROOT / "src"), str(APP_DIR)):
    if value not in sys.path:
        sys.path.insert(0, value)

from arkade_contract import (  # noqa: E402
    AUTHOR_SAMPLE_SHA256,
    ArkadeAlgorithm,
    FROZEN_VIEWS,
    compare_to_oracle,
    independent_oracle,
    load_frozen_view,
    ordered_item_id_sha256,
)
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession  # noqa: E402
from rtdl3_whole_app import prepare_v3, run_v3  # noqa: E402
from run_functional_receipt import (  # noqa: E402
    PROGRAM_BUNDLE,
    _complete_traversal_receipt,
)


def _load_v2():
    path = APP_DIR / "v2_14_whole_app.py"
    spec = importlib.util.spec_from_file_location("arkade_v2_14_performance_lane", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Arkade V2-direct lane")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _stable_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    ).hexdigest()


def _load_formal_identity(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("formal identity must be a JSON object")
    required = (
        "execution_source_archive_sha256",
        "source_tree_sha256",
        "plan_sha256",
        "prepared_identity_sha256",
        "machine_identity_sha256",
        "python_identity_sha256",
    )
    for name in required:
        digest = value.get(name)
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            raise ValueError(f"formal identity has invalid {name}")
    if value.get("goal") != 5745 or value.get("formal_worker_count") != 64:
        raise ValueError("formal identity has the wrong goal or worker count")
    return value


def run_observation(
    *,
    method: str,
    algorithm: ArkadeAlgorithm,
    view_id: str,
    lifecycle: str,
    pair_index: int,
    ordinal: int,
    memory_limit_bytes: int,
    formal_identity: dict[str, object],
) -> dict[str, object]:
    if method not in {"v2_direct", "v3_compiler"}:
        raise ValueError("unknown method")
    if lifecycle not in {"cold_single_invocation", "prepared_paper_search"}:
        raise ValueError("unknown lifecycle")
    if view_id not in FROZEN_VIEWS:
        raise ValueError("unknown frozen view")
    if pair_index < 0 or ordinal < 0:
        raise ValueError("pair_index and ordinal must be nonnegative")
    view = FROZEN_VIEWS[view_id]
    semantic_input = {
        "application": "Arkade",
        "paper_algorithm": algorithm.value,
        "view_id": view_id,
        "author_sample_sha256": AUTHOR_SAMPLE_SHA256,
        "data_count": view.data_count,
        "query_count": view.query_count,
        "k": view.k,
        "output_contract": "ordered_item_ids_by_binary32_metric_then_u32_id.v2",
        "lifecycle": lifecycle,
    }
    semantic_digest = _stable_digest(semantic_input)
    audit = OptixTraversalAuditSession.open()
    owner = None
    preparation_seconds = None
    try:
        if lifecycle == "prepared_paper_search":
            payload = load_frozen_view(view_id)
            prepare_started = time.perf_counter_ns()
            if method == "v2_direct":
                owner = _load_v2().prepare_v2_direct(
                    algorithm=algorithm,
                    view=payload["view"],
                    data_points=payload["data_points"],
                    data_ids=payload["data_ids"],
                )
            else:
                owner = prepare_v3(
                    algorithm=algorithm,
                    view=payload["view"],
                    data_points=payload["data_points"],
                    data_ids=payload["data_ids"],
                    target_identity={
                        "machine_class": "modern_rtx_formal",
                        "backend_contract_id": "nvidia.optix_traversal.v1",
                    },
                    memory_limit_bytes=memory_limit_bytes,
                )
            preparation_seconds = (
                time.perf_counter_ns() - prepare_started
            ) / 1_000_000_000.0
        start_ns = time.perf_counter_ns()
        if lifecycle == "cold_single_invocation":
            payload = load_frozen_view(view_id)
            common = {
                "algorithm": algorithm,
                "view": payload["view"],
                "data_points": payload["data_points"],
                "query_points": payload["query_points"],
                "data_ids": payload["data_ids"],
                "query_ids": payload["query_ids"],
            }
            if method == "v2_direct":
                result = _load_v2().run_v2_direct(**common)
            else:
                result = run_v3(
                    **common,
                    target_identity={
                        "machine_class": "modern_rtx_formal",
                        "backend_contract_id": "nvidia.optix_traversal.v1",
                    },
                    memory_limit_bytes=memory_limit_bytes,
                )
        else:
            assert owner is not None
            result = owner.execute(
                payload["query_points"], query_ids=payload["query_ids"]
            )
        registered_seconds = (time.perf_counter_ns() - start_ns) / 1_000_000_000.0
        output_digest = ordered_item_id_sha256(result["ordered_item_ids"])
        traversal_receipt = audit.finish(
            semantic_digest=semantic_digest,
            output_digest=output_digest,
            route_identity=(
                f"goal5745.{lifecycle}.{method}.{algorithm.value}."
                f"{view_id}.pair_{pair_index}"
            ),
            expected_program_bundles=(PROGRAM_BUNDLE,),
        )
    except BaseException:
        audit.abort()
        raise
    finally:
        if owner is not None:
            owner.close()

    # Correctness is deliberately outside the registered endpoint timer.
    expected = independent_oracle(
        algorithm,
        payload["data_points"],
        payload["query_points"],
        k=view.k,
        data_ids=payload["data_ids"],
    )
    compare_to_oracle(result, expected)
    if output_digest != ordered_item_id_sha256(expected["ordered_item_ids"]):
        raise RuntimeError("Arkade output digest differs from independent oracle")
    if not _complete_traversal_receipt(traversal_receipt):
        raise RuntimeError("Arkade formal endpoint lacks complete behavioral OptiX evidence")
    if not (registered_seconds > 0.0):
        raise RuntimeError("registered endpoint duration is not positive")

    return {
        "schema": "rtdl.goal5745.arkade_v2_v3_lifecycle_endpoint.v2",
        "goal": 5745,
        "pid": os.getpid(),
        "ordinal": ordinal,
        "pair_index": pair_index,
        "method": method,
        "formal_identity": formal_identity,
        "paper_algorithm": algorithm.value,
        "view_id": view_id,
        "lifecycle": lifecycle,
        "semantic_input": semantic_input,
        "semantic_digest": semantic_digest,
        "registered_endpoint_seconds": registered_seconds,
        "preparation_seconds_observed_outside_registered_timer": preparation_seconds,
        "preparation_is_free_or_omitted": False,
        "registered_timer_includes": (
            [
                "frozen_input_archive_validation_and_loading",
                "method_specific_direct_or_compiler_frontdoor",
                "metric_preprocessing",
                "native_prepare_and_initial_gas_build",
                "all_radius_rounds_and_gas_refits",
                "all_optix_launches_and_synchronization",
                "device_metric_filter_and_top_k",
                "bounded_output_download_and_materialization",
                "native_close",
            ]
            if lifecycle == "cold_single_invocation"
            else [
                "query_metric_preprocessing_and_upload",
                "all_radius_rounds_and_gas_refits",
                "all_optix_launches_and_synchronization",
                "device_metric_filter_and_top_k",
                "bounded_output_download_and_materialization",
            ]
        ),
        "registered_timer_excludes": [
            "independent_oracle",
            "correctness_comparator",
            "traversal_receipt_finalization",
            "json_serialization",
        ],
        "ordered_item_id_sha256": output_digest,
        "correctness_matched": True,
        "behavioral_true_optix": True,
        "traversal_receipt": traversal_receipt,
        "round_count": int(result["metadata"]["completed_round_count"]),
        "native_refit_count": int(result["metadata"]["native_refit_count"]),
        "persistent_gas": bool(result["metadata"]["persistent_gas"]),
        "unbounded_candidate_relation_materialized": bool(
            result["metadata"]["unbounded_candidate_relation_materialized"]
        ),
        "default_selected_between_paper_algorithms": False,
        "compiler_or_canonical_resolution_used": bool(
            result["metadata"]["compiler_or_canonical_resolution_used"]
        ),
        "ratio_direction": "v2_direct_over_v3_compiler__greater_than_one_favors_v3",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=("v2_direct", "v3_compiler"), required=True)
    parser.add_argument("--algorithm", choices=tuple(a.value for a in ArkadeAlgorithm), required=True)
    parser.add_argument("--view", choices=tuple(FROZEN_VIEWS), required=True)
    parser.add_argument(
        "--lifecycle",
        choices=("cold_single_invocation", "prepared_paper_search"),
        required=True,
    )
    parser.add_argument("--pair-index", type=int, required=True)
    parser.add_argument("--ordinal", type=int, required=True)
    parser.add_argument("--memory-limit-bytes", type=int, required=True)
    parser.add_argument("--identity-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to replace worker output: {args.output}")
    result = run_observation(
        method=args.method,
        algorithm=ArkadeAlgorithm(args.algorithm),
        view_id=args.view,
        lifecycle=args.lifecycle,
        pair_index=args.pair_index,
        ordinal=args.ordinal,
        memory_limit_bytes=args.memory_limit_bytes,
        formal_identity=_load_formal_identity(args.identity_json),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "output": str(args.output), "pid": result["pid"]}, sort_keys=True))


if __name__ == "__main__":
    main()
