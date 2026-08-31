"""Canonical V4 lowering to the existing partitioned grouped-I64 OptiX family.

Large relational packets cannot be converted to Python geometry/event tuples.
For the exact closed keyed-I64 triangle callback, the compiler instead verifies
and consumes the callback executable, then selects the established packed,
partitioned true-OptiX physical family.  This is a semantic lowering keyed by
the verified callback/reducer contract, not an application-name dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .physical_execution_provenance import OptixTraversalAuditSession
from .v4_triangle_reduction_optix_compiler import (
    consume_verified_triangle_reduction_executable,
)
from .v4_triangle_standard_library import (
    compile_keyed_callback,
    keyed_i64_sum_schema,
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


@dataclass(frozen=True)
class PartitionedGroupedI64Result:
    physical_result: dict[str, object]
    traversal_receipt: dict[str, object]
    callback_ptx_sha256: str
    physical_lowering: str = (
        "canonical_v4_keyed_i64_to_partitioned_packed_optix_grouped_i64_v1")


def execute_verified_partitioned_grouped_i64_v4(
    program,
    *,
    packet_runner,
    packet_path: str | Path,
    native_library,
    native_library_path: str | Path,
    partition_rows: int,
) -> PartitionedGroupedI64Result:
    """Consume one verified program and execute one bounded packed packet."""

    callback = compile_keyed_callback()
    expected_schema = keyed_i64_sum_schema(callback)
    authority = program.authority
    if (
        authority.callback.ir_sha256 != callback.ir_sha256
        or authority.callback.effect_digest != callback.effect_digest
        or authority.schema != expected_schema
    ):
        raise RuntimeError("partitioned grouped-I64 lowering requires the canonical contract")
    if not isinstance(partition_rows, int) or isinstance(partition_rows, bool) \
            or partition_rows <= 0:
        raise ValueError("positive partition_rows required")
    composed = consume_verified_triangle_reduction_executable(
        program.executable,
        program.authority,
        program.contract,
        program.abi,
        any_hit_proof_authority=program.proof,
    )
    callback_ptx_sha256 = hashlib.sha256(composed.encode()).hexdigest()
    audit = OptixTraversalAuditSession.open(
        library=native_library, library_path=Path(native_library_path).resolve())
    try:
        physical = packet_runner(
            Path(packet_path).resolve(), partition_rows=partition_rows)
        output = tuple(
            (tuple(map(int, row["group"])), int(row["value"]))
            for row in physical["rtdl_rows"])
        receipt = audit.finish(
            semantic_digest=_digest({
                "callback_ir": callback.ir_sha256,
                "effect": callback.effect_digest,
                "reducer_schema": expected_schema.schema_sha256,
                "callback_ptx": callback_ptx_sha256,
                "packet_json_sha256": physical["packet_json_sha256"],
                "partition_rows": partition_rows,
            }),
            output_digest=_digest(output),
            route_identity=(
                "v4_callback_ir:keyed_i64_sum:partitioned_packed_optix_v1"),
        )
    except Exception:
        audit.abort()
        raise
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("partitioned grouped-I64 lowering lacked OptiX traversal")
    if physical.get("partitioned_execution_requested") is not True \
            or int(physical.get("partition_count", 0)) <= 0:
        raise RuntimeError("partitioned grouped-I64 physical contract was not enforced")
    return PartitionedGroupedI64Result(
        physical_result=physical,
        traversal_receipt=receipt,
        callback_ptx_sha256=callback_ptx_sha256,
    )


__all__ = [
    "PartitionedGroupedI64Result",
    "execute_verified_partitioned_grouped_i64_v4",
]
