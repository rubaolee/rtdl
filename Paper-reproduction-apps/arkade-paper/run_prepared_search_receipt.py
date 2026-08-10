#!/usr/bin/env python3
"""One functional Arkade prepared-search lifecycle receipt.

Preparation and search are observed separately.  Neither duration is a
registered performance result.  The receipt proves that both the independent
V2-direct lane and compiler-owned V3 lane keep one target set and one
refittable GAS alive across all radius-doubling rounds.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time


APP_DIR = Path(__file__).resolve().parent
ROOT = next(parent for parent in APP_DIR.parents if (parent / "src" / "rtdsl").exists())
for value in (str(ROOT / "src"), str(APP_DIR)):
    if value not in sys.path:
        sys.path.insert(0, value)

from arkade_contract import (  # noqa: E402
    ArkadeAlgorithm,
    compare_to_oracle,
    independent_oracle,
    load_frozen_view,
    ordered_item_id_sha256,
)
from rtdl3_whole_app import prepare_v3  # noqa: E402
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession  # noqa: E402
from run_functional_receipt import PROGRAM_BUNDLE, _complete_traversal_receipt  # noqa: E402


def _load_v2():
    path = APP_DIR / "v2_14_whole_app.py"
    spec = importlib.util.spec_from_file_location("arkade_v2_prepared_lane", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Arkade V2 prepared lane")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_prepared_search(
    *,
    method: str,
    algorithm: ArkadeAlgorithm,
    view_id: str,
    memory_limit_bytes: int,
) -> dict[str, object]:
    if method not in {"v2_direct", "v3_compiler"}:
        raise ValueError("method must be v2_direct or v3_compiler")
    payload = load_frozen_view(view_id)
    view = payload["view"]
    expected = independent_oracle(
        algorithm,
        payload["data_points"],
        payload["query_points"],
        k=view.k,
        data_ids=payload["data_ids"],
    )
    semantic = {
        "application": "Arkade",
        "algorithm": algorithm.value,
        "view_id": view_id,
        "lifecycle": "prepare_once_then_one_search",
        "output_order": "binary32_metric_key_then_u32_id",
    }
    semantic_digest = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()

    audit = OptixTraversalAuditSession.open()
    owner = None
    try:
        prepare_started = time.perf_counter_ns()
        if method == "v2_direct":
            owner = _load_v2().prepare_v2_direct(
                algorithm=algorithm,
                view=view,
                data_points=payload["data_points"],
                data_ids=payload["data_ids"],
            )
        else:
            owner = prepare_v3(
                algorithm=algorithm,
                view=view,
                data_points=payload["data_points"],
                data_ids=payload["data_ids"],
                target_identity={
                    "machine_class": "home_functional",
                    "backend_contract_id": "nvidia.optix_traversal.v1",
                },
                memory_limit_bytes=memory_limit_bytes,
            )
        preparation_seconds = (
            time.perf_counter_ns() - prepare_started
        ) / 1_000_000_000.0

        search_started = time.perf_counter_ns()
        result = owner.execute(
            payload["query_points"], query_ids=payload["query_ids"]
        )
        search_seconds = (
            time.perf_counter_ns() - search_started
        ) / 1_000_000_000.0
        output_digest = ordered_item_id_sha256(result["ordered_item_ids"])
        receipt = audit.finish(
            semantic_digest=semantic_digest,
            output_digest=output_digest,
            route_identity=f"goal5745.prepared.{method}.{algorithm.value}.{view_id}",
            expected_program_bundles=(PROGRAM_BUNDLE,),
        )
    except BaseException:
        audit.abort()
        raise
    finally:
        if owner is not None:
            owner.close()

    compare_to_oracle(result, expected)
    if not _complete_traversal_receipt(receipt):
        raise RuntimeError("prepared Arkade search lacks complete OptiX receipt")
    metadata = dict(result["metadata"])
    return {
        "schema": "rtdl.goal5745.arkade_prepared_search_functional.v1",
        "goal": 5745,
        "method": method,
        "algorithm": algorithm.value,
        "view_id": view_id,
        "correctness_matched": True,
        "behavioral_true_optix": True,
        "ordered_item_id_sha256": output_digest,
        "preparation_seconds_observed_not_free_or_formal": preparation_seconds,
        "search_seconds_observed_not_registered_or_formal": search_seconds,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "persistent_gas": metadata["persistent_gas"],
        "completed_round_count": metadata["completed_round_count"],
        "native_refit_count": metadata["native_refit_count"],
        "unbounded_candidate_relation_materialized": metadata[
            "unbounded_candidate_relation_materialized"
        ],
        "compiler_or_canonical_resolution_used": metadata[
            "compiler_or_canonical_resolution_used"
        ],
        "traversal_receipt": receipt,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=("v2_direct", "v3_compiler"), required=True)
    parser.add_argument("--algorithm", choices=tuple(value.value for value in ArkadeAlgorithm), required=True)
    parser.add_argument("--view", required=True)
    parser.add_argument("--memory-limit-bytes", type=int, default=1 << 30)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to replace receipt: {args.output}")
    result = run_prepared_search(
        method=args.method,
        algorithm=ArkadeAlgorithm(args.algorithm),
        view_id=args.view,
        memory_limit_bytes=args.memory_limit_bytes,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": "ok", "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
