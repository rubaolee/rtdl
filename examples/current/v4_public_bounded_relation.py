#!/usr/bin/env python3
"""Public V4 lifecycle example for the closed custom-AABB relation family.

This example imports no RTDL implementation module.  The proof file is an
external evidence artifact: the public API hashes and binds it to the exact
verified callback, but does not pretend that arbitrary bytes prove a theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rtdsl.v4 import (
    AnyHitProtocolProof,
    BoundedRelationBatch,
    BoundedRelationProtocol,
    BoundedRelationStaticInput,
    V4Target,
    V4Toolchain,
    compile_protocol_program,
    standard_protocol_physical_plan,
)


INDEXED_BOXES = (
    (0.0, 0.0, 4.0, 1.0, 10),
    (0.0, 0.0, 1.0, 4.0, 20),
)
SOURCE_BOXES = (
    (2.0, 0.25, 3.0, 0.75, 100),
    (0.25, 2.0, 0.75, 3.0, 101),
)
EXPECTED_ROWS = ((100, 10), (101, 20))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: argparse.Namespace) -> dict[str, object]:
    proof_path = args.any_hit_proof.expanduser().resolve()
    protocol = BoundedRelationProtocol(capacity=8)
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
        any_hit_proof=proof)
    materialized = verified.materialize(target=target, toolchain=toolchain)
    prepared = materialized.prepare(BoundedRelationStaticInput(INDEXED_BOXES))
    try:
        result = prepared.execute(BoundedRelationBatch(
            SOURCE_BOXES, expected_rows=EXPECTED_ROWS))
        lifecycle = prepared.lifecycle_receipt
    finally:
        prepared.close()
        prepared.close()  # The public cleanup contract is idempotent.

    if result.output != EXPECTED_ROWS:
        raise RuntimeError(f"unexpected relation rows: {result.output!r}")
    return {
        "family": verified.identity.family,
        "program_identity_sha256": verified.identity.identity_sha256,
        "executable_identity_sha256": result.executable_identity.identity_sha256,
        "output": result.output,
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
    parser.add_argument("--compute-capability", required=True,
                        help="major.minor, for example 8.9")
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
