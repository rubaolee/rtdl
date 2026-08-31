#!/usr/bin/env python3
"""Public V4 lifecycle example for checked built-in-triangle reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rtdsl.v4 import (
    AnyHitProtocolProof,
    TriangleReductionBatch,
    TriangleReductionMode,
    TriangleReductionProtocol,
    TriangleReductionStaticInput,
    V4Target,
    V4Toolchain,
    compile_protocol_program,
    standard_protocol_physical_plan,
)


# Three depth layers at footprint A and two coincident primitives at footprint
# B.  The four rays therefore see 3, 2, 0, and 1 hits respectively.
VERTICES = (
    (0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0),
    (0.0, 0.0, 2.0), (1.0, 0.0, 2.0), (0.0, 1.0, 2.0),
    (0.0, 0.0, 3.0), (1.0, 0.0, 3.0), (0.0, 1.0, 3.0),
    (3.0, 0.0, 1.0), (4.0, 0.0, 1.0), (3.0, 1.0, 1.0),
)
TRIANGLES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (9, 10, 11), (9, 10, 11),
)
QUERIES = (
    ((0.25, 0.25, 0.0), (0.0, 0.0, 1.0), 4.0),
    ((3.25, 0.25, 0.0), (0.0, 0.0, 1.0), 4.0),
    ((10.0, 10.0, 0.0), (0.0, 0.0, 1.0), 4.0),
    ((0.25, 0.25, 0.0), (0.0, 0.0, 1.0), 1.5),
)
WEIGHTS = (1, 3, 5, 7)
EXPECTED_PER_RAY = (3, 2, 0, 1)
EXPECTED_WEIGHTED_SUM = 16


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: argparse.Namespace) -> dict[str, object]:
    proof_path = args.any_hit_proof.expanduser().resolve()
    protocol = TriangleReductionProtocol(
        TriangleReductionMode.WEIGHTED_HIT_COUNT)
    physical_plan = standard_protocol_physical_plan(protocol)
    proof = AnyHitProtocolProof(
        callback_ir_sha256=physical_plan.callback_ir_sha256,
        effect_digest=physical_plan.effect_digest,
        proof_sha256=_sha256(proof_path),
        proof_kind=args.proof_kind,
    )
    target = V4Target.from_native(
        args.native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    toolchain = V4Toolchain.current(
        compute_capability=tuple(map(int, args.compute_capability.split("."))),
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
    )

    verified = compile_protocol_program(
        protocol,
        physical_plan=physical_plan,
        any_hit_proof=proof,
    )
    materialized = verified.materialize(target=target, toolchain=toolchain)
    prepared = materialized.prepare(TriangleReductionStaticInput(
        vertices=VERTICES,
        triangles=TRIANGLES,
        primitive_metadata={},
        event_capacity=8,
    ))
    try:
        result = prepared.execute(TriangleReductionBatch(
            queries=QUERIES,
            query_metadata={"query.weight": WEIGHTS},
        ))
        lifecycle = prepared.lifecycle_receipt
    finally:
        prepared.close()
        prepared.close()

    if result.details["per_ray_u64"] != EXPECTED_PER_RAY:
        raise RuntimeError(f"unexpected per-ray counts: {result.details['per_ray_u64']!r}")
    if result.output != EXPECTED_WEIGHTED_SUM:
        raise RuntimeError(f"unexpected checked weighted sum: {result.output!r}")
    return {
        "family": verified.identity.family,
        "program_identity_sha256": verified.identity.identity_sha256,
        "executable_identity_sha256": result.executable_identity.identity_sha256,
        "per_ray_hit_counts": result.details["per_ray_u64"],
        "checked_weighted_sum": result.output,
        "output_sha256": result.output_sha256,
        "physical_executor_classification": result.traversal_receipt[
            "physical_executor_classification"],
        "lifecycle": lifecycle,
        "performance_claimed": False,
    }


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--any-hit-proof", type=Path, required=True)
    parser.add_argument(
        "--proof-kind",
        default="external_machine_checked_order_independence_v1",
    )
    return parser.parse_args()


def main() -> None:
    print(json.dumps(run(_arguments()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
