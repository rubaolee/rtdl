#!/usr/bin/env python3
"""Untimed public-API KAT for the fused online-monitor application fast path.

The KAT deliberately performs no clock read.  It checks actual native receipt
fields for first, exact-reuse, changed-input, and device-failure executions in
both admitted families.  Private owner introspection is used only to recover
the already-validated native receipt after the public failure raises; all
install/load/prepare/execute/close operations use the public API.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def _fail(message: str) -> None:
    raise RuntimeError(message)


def _receipt(result: object) -> dict[str, object]:
    status = dict(getattr(result, "device_status"))
    receipt = dict(status.get("operation_receipt", {}))
    if not receipt:
        _fail("public result omitted its native fast-path receipt")
    return receipt


def _require_receipt(
    receipt: dict[str, object], *, family: str, reused: bool,
    output_bytes: int, success: bool, semantic_capacity: int | None = None,
) -> None:
    expected_calls = 0 if reused else (2 if family == "relation" else 8)
    expected_builds = 0 if reused or family == "triangle" else 1
    expected_boundaries = 2 if success else 1
    expected_output = output_bytes if success else 0
    required = {
        "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
        "optix_launch_count": 2 if family == "relation" else 1,
        "host_blocking_boundary_count": expected_boundaries,
        "control_d2h_bytes": 28 if family == "relation" else 12,
        "output_d2h_bytes": expected_output,
        "status_before_output": True,
        "output_d2h_after_status_failure": 0,
        "role_counters_materialized": False,
        "prepared_input_reused": reused,
        "dynamic_device_upload_call_count": expected_calls,
        "dynamic_accel_build_count": expected_builds,
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "callback_status_kernel_launch_count": 0,
        "checked_product_kernel_launch_count": 0,
        "compact_control_finalizer_kernel_launch_count": 0,
        "total_auxiliary_cuda_kernel_launch_count": 1 if family == "relation" else 0,
        "execution_parameter_h2d_bytes": 240 if family == "relation" else 224,
        "execution_parameter_h2d_copy_call_count": 2 if family == "relation" else 1,
        "stream_ordered_memset_call_count": 4 if family == "relation" else 2,
        "status_d2h_copy_call_count": 1,
        "output_d2h_copy_call_count": 1 if success else 0,
    }
    if family == "relation":
        if type(semantic_capacity) is not int or semantic_capacity <= 0:
            _fail("relation receipt check lacks its semantic capacity")
        key_capacity = 1
        while key_capacity < 2 * semantic_capacity:
            key_capacity <<= 1
        required.update({
            "semantic_compaction_launch_count": 1,
            "semantic_compaction_key_capacity": key_capacity,
            "semantic_compaction_scratch_bytes": (
                8 * key_capacity + 8 * semantic_capacity + 8),
        })
    else:
        required.update({
            "semantic_compaction_launch_count": 0,
            "semantic_compaction_key_capacity": 0,
            "semantic_compaction_scratch_bytes": 0,
        })
    mismatches = {
        key: {"expected": expected, "observed": receipt.get(key)}
        for key, expected in required.items()
        if receipt.get(key) != expected
    }
    if mismatches:
        _fail(f"{family} fast receipt mismatch: {mismatches}")
    if int(receipt.get("dynamic_input_generation", 0)) <= 0:
        _fail(f"{family} fast receipt lacks a positive input generation")
    if reused:
        if int(receipt.get("dynamic_device_upload_bytes", -1)) != 0:
            _fail(f"{family} exact reuse performed a dynamic upload")
    elif int(receipt.get("dynamic_device_upload_bytes", 0)) <= 0:
        _fail(f"{family} first/changed execution omitted dynamic upload bytes")


def _require_diagnostic(result: object, *, family: str) -> dict[str, object]:
    status = dict(getattr(result, "device_status"))
    required = {
        "ok": True,
        "first_error_claimed": 0,
        "error_code": 0,
        "role_counters_materialized": True,
        "role_counters_internally_materialized": True,
        "fast_path_applied": False,
        "execution_path": "diagnostic_v4",
    }
    mismatches = {
        key: {"expected": expected, "observed": status.get(key)}
        for key, expected in required.items()
        if status.get(key) != expected
    }
    if mismatches:
        _fail(f"{family} diagnostic status mismatch: {mismatches}")
    counters = tuple(getattr(result, "role_counters"))
    if len(counters) != 7 or sum(counters) <= 0:
        _fail(f"{family} diagnostic role counters are absent")
    output_sha = getattr(result, "output_sha256")
    if not isinstance(output_sha, str) or len(output_sha) != 64:
        _fail(f"{family} diagnostic output digest is absent")
    if getattr(result, "traversal_receipt") is None:
        _fail(f"{family} diagnostic traversal receipt is absent")
    return {
        "device_status": status,
        "output_sha256": output_sha,
        "role_counters": list(counters),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--trust-root", type=Path, required=True)
    parser.add_argument("--trust-head", type=Path, required=True)
    parser.add_argument("--trust-package", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)

    from rtdsl import (
        BoundedRelationBatch,
        BoundedRelationStaticInput,
        TriangleReductionBatch,
        TriangleReductionStaticInput,
        install_rtdlexe_deployment,
        load_rtdlexe,
    )

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    loaded = {}
    for label, row in manifest["candidates"].items():
        deployment = install_rtdlexe_deployment(
            trust_root_path=args.trust_root,
            trust_head_path=args.trust_head,
            trust_package_path=args.trust_package,
            deployment_id=row["deployment_id"],
        )
        loaded[label] = load_rtdlexe(
            row["artifact_path"], authority_path=row["authority_path"],
            deployment=deployment,
        )

    relation_minimum = loaded["relation"].product_projection[
        "runtime"]["minimum_overlap_f32"]
    if not isinstance(relation_minimum, float) \
            or not math.isfinite(relation_minimum) \
            or relation_minimum < 0.0:
        _fail("relation artifact omitted its finite non-negative overlap bound")
    # Build the KAT geometry from the sealed semantic threshold.  The prior
    # fixed source box had area 0.25 and was therefore correctly rejected by
    # the matched-task artifact whose minimum overlap is 1.0.  A power-of-two
    # side keeps all coordinates exact in binary32 and gives area >= minimum.
    relation_scale = 1.0
    while relation_scale * relation_scale < relation_minimum:
        relation_scale *= 2.0
    if not math.isfinite(8.0 * relation_scale):
        _fail("relation overlap bound cannot form finite KAT geometry")
    indexed_hit = (
        0.0, 0.0, 4.0 * relation_scale, 4.0 * relation_scale, 100)
    indexed_miss = (
        6.0 * relation_scale, 6.0 * relation_scale,
        7.0 * relation_scale, 7.0 * relation_scale, 101)
    # This box is wholly inside indexed_hit, has sufficient overlap, and is
    # separated from indexed_hit's rising diagonal.  It therefore emits once
    # in the two-pass diagonal scheme, which is required by the K+1 hostile
    # case below to stay below the raw 2*K capacity.
    source_hit = (
        0.5 * relation_scale, 2.5 * relation_scale,
        1.5 * relation_scale, 3.5 * relation_scale)

    relation = loaded["relation"].prepare(
        BoundedRelationStaticInput((
            indexed_hit,
            indexed_miss,
        )), native_library_path=args.native,
    )
    relation_a = BoundedRelationBatch((
        (*source_hit, 10),
        (10.0 * relation_scale, 10.0 * relation_scale,
         11.0 * relation_scale, 11.0 * relation_scale, 11),
    ), expected_rows=((10, 100),))
    relation_b = BoundedRelationBatch((
        (*source_hit, 12),
    ), expected_rows=((12, 100),))
    relation_first = relation.execute(relation_a, include_diagnostics=False)
    relation_repeat = relation.execute(
        BoundedRelationBatch(tuple(relation_a.source_boxes),
                             expected_rows=((10, 100),)),
        include_diagnostics=False,
    )
    relation_changed = relation.execute(relation_b, include_diagnostics=False)
    relation_capacity = loaded["relation"].product_projection[
        "runtime"]["capacity"]
    if type(relation_capacity) is not int or relation_capacity <= 0:
        _fail("relation artifact omitted its positive bounded capacity")
    # The two diagonal passes may both emit the overlapping pair, but the
    # device compaction boundary transfers only the one unique semantic row.
    relation_rows = (8, 8, 8)
    relation_receipts = tuple(map(_receipt, (
        relation_first, relation_repeat, relation_changed)))
    for receipt, reused, output_bytes in zip(
            relation_receipts, (False, True, False), relation_rows):
        _require_receipt(receipt, family="relation", reused=reused,
                         output_bytes=output_bytes, success=True,
                         semantic_capacity=relation_capacity)
    if any(item.output_sha256 is not None or item.role_counters
           for item in (relation_first, relation_repeat, relation_changed)):
        _fail("relation application fast path materialized forensic hashes/counters")
    relation_diagnostic = relation.execute(
        relation_a, include_diagnostics=True)
    if relation_diagnostic.output != ((10, 100),):
        _fail("relation diagnostic path changed the accepted output")
    relation_diagnostic_evidence = _require_diagnostic(
        relation_diagnostic, family="relation")

    overflow_sources = tuple(
        # Off the indexed box's rising diagonal: pass 0 emits each overlap,
        # while pass 1 does not.  Thus K+1 unique rows fit inside the 2*K raw
        # buffer and can be rejected only by device-side semantic compaction.
        (*source_hit, 1000 + index)
        for index in range(relation_capacity + 1))
    try:
        relation.execute(
            BoundedRelationBatch(overflow_sources), include_diagnostics=False)
    except Exception as error:  # public fail-closed result
        relation_failure_code = getattr(error, "code", type(error).__name__)
    else:
        _fail("relation status-failure KAT unexpectedly succeeded")
    relation_failure_receipt = dict(
        relation._owner._last_fast_operation_receipt or {})
    _require_receipt(
        relation_failure_receipt, family="relation", reused=False,
        output_bytes=0, success=False, semantic_capacity=relation_capacity)
    relation.close()

    max_u32 = (1 << 32) - 1
    semantic_relation = loaded["relation"].prepare(
        BoundedRelationStaticInput(((*indexed_hit[:4], max_u32),)),
        native_library_path=args.native,
    )
    max_key_batch = BoundedRelationBatch(
        ((*source_hit, max_u32),),
        expected_rows=((max_u32, max_u32),))
    max_key_first = semantic_relation.execute(
        max_key_batch, include_diagnostics=False)
    max_key_repeat = semantic_relation.execute(
        BoundedRelationBatch(
            tuple(max_key_batch.source_boxes),
            expected_rows=((max_u32, max_u32),)),
        include_diagnostics=False)
    max_key_receipts = tuple(map(_receipt, (max_key_first, max_key_repeat)))
    for receipt, reused in zip(max_key_receipts, (False, True)):
        _require_receipt(
            receipt, family="relation", reused=reused,
            output_bytes=8, success=True,
            semantic_capacity=relation_capacity)
    if max_key_first.output != ((max_u32, max_u32),) \
            or max_key_repeat.output != ((max_u32, max_u32),):
        _fail("relation max-U64-key compaction output changed")
    semantic_overflow_sources = tuple(
        (*source_hit, index)
        for index in range(relation_capacity + 1))
    try:
        semantic_relation.execute(
            BoundedRelationBatch(semantic_overflow_sources),
            include_diagnostics=False)
    except Exception as error:
        semantic_failure_code = getattr(
            error, "code", type(error).__name__)
    else:
        _fail("relation real K+1 semantic overflow unexpectedly succeeded")
    semantic_failure_receipt = dict(
        semantic_relation._owner._last_fast_operation_receipt or {})
    semantic_failure_control = dict(
        semantic_relation._owner._last_fast_compact_control or {})
    _require_receipt(
        semantic_failure_receipt, family="relation", reused=False,
        output_bytes=0, success=False, semantic_capacity=relation_capacity)
    expected_semantic_control = {
        "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
        "raw_event_count": relation_capacity + 1,
        "unique_event_count": relation_capacity + 1,
        "overflowed": 1,
        "status": 0xffff5102,
        "semantic_capacity": relation_capacity,
        "raw_event_capacity": 2 * relation_capacity,
        "control_d2h_bytes": 28,
    }
    if semantic_failure_control != expected_semantic_control:
        _fail(f"relation real K+1 compact control mismatch: "
              f"{semantic_failure_control!r}")
    semantic_relation.close()
    semantic_hostile = {
        "k_plus_one_failure_code": semantic_failure_code,
        "k_plus_one_compact_control": semantic_failure_control,
        "k_plus_one_receipt": semantic_failure_receipt,
        "max_u64_key_output": [[max_u32, max_u32]],
        "max_u64_key_receipts": list(max_key_receipts),
        "raw_capacity": 2 * relation_capacity,
        "raw_count_below_raw_capacity": True,
        "same_input_reuse_clears_compaction_scratch": True,
    }

    triangle = loaded["triangle"].prepare(
        TriangleReductionStaticInput(
            vertices=((-1.0, -1.0, 1.0), (1.0, -1.0, 1.0),
                      (0.0, 1.0, 1.0)),
            triangles=((0, 1, 2),), event_capacity=1,
        ), native_library_path=args.native,
    )
    query = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
    triangle_a = TriangleReductionBatch(
        query, query_weights=(7,), expected_reduced_u64=7)
    triangle_b = TriangleReductionBatch(
        query, query_weights=(9,), expected_reduced_u64=9)
    triangle_first = triangle.execute(triangle_a, include_diagnostics=False)
    triangle_repeat = triangle.execute(
        TriangleReductionBatch(tuple(query), query_weights=(7,),
                               expected_reduced_u64=7),
        include_diagnostics=False,
    )
    triangle_changed = triangle.execute(triangle_b, include_diagnostics=False)
    triangle_receipts = tuple(map(_receipt, (
        triangle_first, triangle_repeat, triangle_changed)))
    for receipt, reused in zip(triangle_receipts, (False, True, False)):
        _require_receipt(receipt, family="triangle", reused=reused,
                         output_bytes=8, success=True)
    if any(item.output_sha256 is not None or item.role_counters
           for item in (triangle_first, triangle_repeat, triangle_changed)):
        _fail("triangle application fast path materialized forensic hashes/counters")
    triangle_diagnostic = triangle.execute(
        triangle_a, include_diagnostics=True)
    if triangle_diagnostic.output != 7:
        _fail("triangle diagnostic path changed the accepted output")
    triangle_diagnostic_evidence = _require_diagnostic(
        triangle_diagnostic, family="triangle")

    two_queries = query + (
        ((0.1, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
    try:
        triangle.execute(
            TriangleReductionBatch(
                two_queries, query_weights=((1 << 64) - 1, (1 << 64) - 1)),
            include_diagnostics=False,
        )
    except Exception as error:
        triangle_failure_code = getattr(error, "code", type(error).__name__)
    else:
        _fail("triangle status-failure KAT unexpectedly succeeded")
    triangle_failure_receipt = dict(
        triangle._owner._last_fast_operation_receipt or {})
    _require_receipt(
        triangle_failure_receipt, family="triangle", reused=False,
        output_bytes=0, success=False)
    triangle.close()

    result = {
        "schema": "rtdl.goal5801.fast_path_gpu_kat.v1",
        "registered_timing_count": 0,
        "relation": {
            "outputs": [list(map(list, item.output)) for item in (
                relation_first, relation_repeat, relation_changed)],
            "receipts": [*relation_receipts, relation_failure_receipt],
            "failure_code": relation_failure_code,
            "diagnostic": relation_diagnostic_evidence,
            "semantic_compaction_hostile": semantic_hostile,
        },
        "triangle": {
            "outputs": [item.output for item in (
                triangle_first, triangle_repeat, triangle_changed)],
            "receipts": [*triangle_receipts, triangle_failure_receipt],
            "failure_code": triangle_failure_code,
            "diagnostic": triangle_diagnostic_evidence,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
