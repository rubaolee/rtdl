#!/usr/bin/env python3
"""Execute and seal Goal5834-B1 raw provider bits without an oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_curve import (
    BuiltinCurveStaticInput,
    CurveBooleanSegmentBatch,
    V4CurveTarget,
    curve_any_contact_boolean_source,
)
from rtdsl.v4_public_builtin_curve import PublicCurveLifecycleError


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    return json.loads(path.read_text(
        encoding="utf-8", errors="strict"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {value}")))


def _require_identity(target, source, program, materialized, native, preaction):
    observed = {
        "native_sha256": _sha(native),
        "source_sha256": source.source_sha256,
        "callback_ir_sha256": program.authority.callback.ir_sha256,
        "callback_effect_digest": program.authority.callback.effect_digest,
        "physical_schema_sha256": program.authority.schema.schema_sha256,
        "canonical_plan_sha256": program.authority.canonical_plan.plan_sha256,
        "callback_abi_sha256": program.abi.abi_sha256,
        "wrapper_source_sha256": program.wrapper.source_sha256,
        "executable_sha256": materialized.executable.executable_sha256,
    }
    for name, value in observed.items():
        if preaction.get(name) != value:
            raise RuntimeError(f"target preaction identity differs at {name}")
    if target.profile.native_sha256 != observed["native_sha256"]:
        raise RuntimeError("target profile native identity differs")
    return observed


def _execute_one(materialized, worker_row):
    static = BuiltinCurveStaticInput(**worker_row["static_input"])
    batch = CurveBooleanSegmentBatch(worker_row["queries"])
    if static.commitment_sha256 != \
            worker_row["public_static_input_commitment_sha256"] \
            or batch.commitment_sha256 != \
                worker_row["public_query_commitment_sha256"]:
        raise RuntimeError("public input commitment differs")
    prepared = materialized.prepare(static)
    with prepared:
        before = prepared.lifecycle_receipt
        primary = prepared.execute(batch)
        after_primary = prepared.lifecycle_receipt
        repeated = prepared.execute(batch)
        after_repeat = prepared.lifecycle_receipt
        reverse_batch = CurveBooleanSegmentBatch(tuple(reversed(batch.queries)))
        reversed_result = prepared.execute(reverse_batch)
        after_reverse = prepared.lifecycle_receipt
    if repeated.per_query_hit != primary.per_query_hit \
            or repeated.any_hit != primary.any_hit:
        raise RuntimeError("repeat execution changed raw provider bits")
    if reversed_result.per_query_hit != tuple(reversed(primary.per_query_hit)) \
            or reversed_result.any_hit != primary.any_hit:
        raise RuntimeError("reversed query order changed provider Boolean")
    if before["execution_count"] != 0 \
            or after_primary["execution_count"] != 1 \
            or after_repeat["execution_count"] != 2 \
            or after_reverse["execution_count"] != 3:
        raise RuntimeError("prepared lifecycle execution counts differ")
    if primary.physical_receipt.get("status_before_output") is not True \
            or primary.physical_receipt.get("host_aggregation") != \
                "OR_after_raw_receipt_seal" \
            or primary.physical_receipt.get(
                "raw_gpu_bit_vector_commitment_sha256") != \
                primary.output_sha256:
        raise RuntimeError("raw Boolean receipt binding differs")
    if primary.traversal_receipt.get(
            "physical_executor_classification") != \
            "optix_traversal_observed":
        raise RuntimeError("Boolean worker did not observe OptiX traversal")
    return {
        "family_id": worker_row["family_id"],
        "execution_id": worker_row["execution_id"],
        "normalization_origin_f64_bits":
            worker_row["normalization_origin_f64_bits"],
        "normalization_scale_f64_bits":
            worker_row["normalization_scale_f64_bits"],
        "original_input_sha256": worker_row["original_input_sha256"],
        "normalized_input_sha256": worker_row["normalized_input_sha256"],
        "public_static_input_commitment_sha256": static.commitment_sha256,
        "public_query_commitment_sha256": batch.commitment_sha256,
        "per_query_hit": list(primary.per_query_hit),
        "collision_host_or": primary.any_hit,
        "raw_gpu_bit_vector_commitment_sha256": primary.output_sha256,
        "physical_output_commitment_sha256": primary.physical_output_sha256,
        "physical_receipt": primary.physical_receipt,
        "traversal_receipt": primary.traversal_receipt,
        "device_status": list(primary.statuses),
        "role_counters": list(primary.counters),
        "repeat_per_query_hit": list(repeated.per_query_hit),
        "reversed_per_query_hit": list(reversed_result.per_query_hit),
        "lifecycle_execution_counts": [
            before["execution_count"], after_primary["execution_count"],
            after_repeat["execution_count"], after_reverse["execution_count"],
        ],
    }


def _fork_execute_one(materialized, worker_row):
    if os.name != "posix" or not hasattr(os, "fork"):
        raise RuntimeError("B3 requires the frozen Home POSIX fork boundary")
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        try:
            payload = {"ok": True, "row": _execute_one(materialized, worker_row)}
        except BaseException as exc:  # child must preserve the exact failure
            payload = {
                "ok": False,
                "error_type": type(exc).__name__,
                "error_text": str(exc),
            }
        body = json.dumps(
            payload, sort_keys=True, allow_nan=False).encode("utf-8")
        with os.fdopen(write_fd, "wb", closefd=True) as stream:
            stream.write(body)
        os._exit(0 if payload["ok"] else 1)
    os.close(write_fd)
    with os.fdopen(read_fd, "rb", closefd=True) as stream:
        body = stream.read()
    waited_pid, status = os.waitpid(pid, 0)
    if waited_pid != pid:
        raise RuntimeError("B3 child ownership differs")
    payload = json.loads(body.decode("utf-8"))
    if status != 0 or payload.get("ok") is not True:
        raise RuntimeError(
            "B3 row child failed: " + json.dumps(payload, sort_keys=True))
    return payload["row"]


def execute(args):
    worker_inputs_path = args.worker_inputs.resolve(strict=True)
    target_preaction_path = args.target_preaction.resolve(strict=True)
    fixture_authority_path = args.fixture_authority.resolve(strict=True)
    native = args.native.resolve(strict=True)
    worker_inputs = _load(worker_inputs_path)
    preaction = _load(target_preaction_path)
    if worker_inputs.get("schema") != \
            "rtdl.goal5834_b1.boolean_worker_inputs.v1" \
            or worker_inputs.get("contains_expected_output") is not False \
            or worker_inputs.get("contains_pairwise_geometry_result") is not False:
        raise RuntimeError("worker inputs contain forbidden scientific answers")
    if any("expected" in key.lower()
           for row in worker_inputs["rows"] for key in row):
        raise RuntimeError("worker row contains an expected-output key")
    allowed_preactions = {
        (
            "rtdl.goal5834_b1.home_target_preaction.v1",
            "TARGET_AND_EXECUTABLE_BOUND__PRIMARY_WORKER_ZERO_AUTHORIZED",
            "B1",
        ),
        (
            "rtdl.goal5834_b2.home_target_preaction.v1",
            "B2_TARGET_BOUND__SAME_FIXTURES__PRIMARY_WORKER_ZERO_AUTHORIZED",
            "B2",
        ),
        (
            "rtdl.goal5834_b3.home_target_preaction.v1",
            "B3_TARGET_BOUND__SAME_FIXTURES__FORK_CLEAN_ROWS_AUTHORIZED",
            "B3",
        ),
    }
    lineage = preaction.get("lineage", "B1")
    if (preaction.get("schema"), preaction.get("status"), lineage) not in \
            allowed_preactions \
            or preaction.get("application_worker_count_at_emission") != 0 \
            or preaction.get("registered_performance_timing_count") != 0:
        raise RuntimeError("target preaction status differs")
    if lineage in {"B2", "B3"} and not isinstance(
            preaction.get("predecessor_failure"), dict):
        raise RuntimeError("successor predecessor failure binding is absent")
    if preaction.get("worker_inputs_sha256") != _sha(worker_inputs_path) \
            or preaction.get("fixture_authority_sha256") != \
                _sha(fixture_authority_path) \
            or preaction.get("native_sha256") != _sha(native):
        raise RuntimeError("target preaction custody differs")

    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    target = V4CurveTarget.from_native(
        native, optix_sdk=preaction["optix_sdk"],
        compute_capability=preaction["compute_capability"])
    toolchain = V4Toolchain.current(
        compute_capability=tuple(
            int(value) for value in preaction["compute_capability"].split(".")),
        optix_include=Path(preaction["optix_include"]).resolve(strict=True),
        cuda_include=Path(preaction["cuda_include"]).resolve(strict=True),
    )
    source = curve_any_contact_boolean_source()
    program = source.compile(target=target)
    materialized = program.materialize(toolchain=toolchain)
    identities = _require_identity(
        target, source, program, materialized, native, preaction)

    rows = []
    primary_worker_count = 0
    validation_launch_count = 0
    materialization_count = 1
    forked_static_scene_worker_count = 0
    for row_index, worker_row in enumerate(worker_inputs["rows"]):
        if lineage == "B3":
            row_result = _fork_execute_one(materialized, worker_row)
            forked_static_scene_worker_count += 1
        else:
            if row_index:
            # VerifiedCurveExecutable objects are intentionally single-use:
            # preparing a static scene consumes their live registry entry.
            # Each distinct frozen static scene therefore receives a fresh,
            # identity-equal materialization.  The scientific inputs do not
            # change and no result is available at this point.
                materialized = program.materialize(toolchain=toolchain)
                _require_identity(
                    target, source, program, materialized, native, preaction)
                materialization_count += 1
            row_result = _execute_one(materialized, worker_row)
        primary_worker_count += 1
        validation_launch_count += 2
        rows.append(row_result)

    malformed = None
    try:
        CurveBooleanSegmentBatch((((0.0, 0.0), (1.0, 0.0, 0.0)),))
    except PublicCurveLifecycleError as exc:
        malformed = {
            "rejected_before_prepare_or_launch": True,
            "code": getattr(exc, "code", None),
            "message": str(exc),
        }
    if malformed is None:
        raise RuntimeError("malformed query was not rejected prelaunch")
    if primary_worker_count != worker_inputs["primary_execution_count"]:
        raise RuntimeError("primary worker denominator differs")
    return {
        "schema": (
            "rtdl.goal5834_b3.raw_gpu_boolean_receipt.v1"
            if lineage == "B3" else
            "rtdl.goal5834_b2.raw_gpu_boolean_receipt.v1"
            if lineage == "B2" else
            "rtdl.goal5834_b1.raw_gpu_boolean_receipt.v1"),
        "status": "RAW_GPU_BITS_SEALED__UNEVALUATED",
        "lineage": lineage,
        "oracle_imported_or_called": False,
        "expected_output_available_to_worker": False,
        "scope": "FUNCTIONAL_ONLY__NO_PERFORMANCE",
        "registered_performance_timing_count": 0,
        "fixture_authority_sha256": _sha(fixture_authority_path),
        "worker_inputs_sha256": _sha(worker_inputs_path),
        "target_preaction_sha256": _sha(target_preaction_path),
        "identities": identities,
        "primary_worker_count": primary_worker_count,
        "materialization_count": materialization_count,
        "forked_static_scene_worker_count": forked_static_scene_worker_count,
        "repeat_validation_launch_count": primary_worker_count,
        "reverse_order_validation_launch_count": primary_worker_count,
        "total_successful_application_launch_count":
            primary_worker_count + validation_launch_count,
        "evaluator_ineligible_worker_count": 0,
        "malformed_prelaunch_rejection": malformed,
        "rows": rows,
        "goal5835_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--fixture-authority", required=True, type=Path)
    parser.add_argument("--worker-inputs", required=True, type=Path)
    parser.add_argument("--target-preaction", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = execute(args)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": result["status"],
        "primary_worker_count": result["primary_worker_count"],
        "total_successful_application_launch_count":
            result["total_successful_application_launch_count"],
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
