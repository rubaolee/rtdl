#!/usr/bin/env python3
"""Untimed Home functional worker for the Goal5791 token-only path.

This helper is deliberately not a benchmark.  It either inspects the exact
compiled callback/target identity or runs one bounded RT-2A1 functional lane.
For a functional lane, every segment descriptor, ablation plan, operation
contract, and runtime identity is deeply admitted before device geometry is
generated.  The device phase then consumes only opaque, single-use
``VerifiedFusionExecutionToken`` instances.  Evidence sealing and oracle
comparison happen after the complete generator is exhausted.

The older Goal5790 helper remains the authority for Home-machine and PTX
producer admission and for compiling the shared OptiX producer.  No legacy
plan/nonce execution entry point is called here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _require_target_match(executor, target) -> None:
    observed = {
        "native_library_sha256": executor.native_library_sha256,
        "callback_ir_sha256": executor.callback_ir_sha256,
        "callback_authority_nonce": executor.callback_authority_nonce,
        "contract_sha256": executor.contract_sha256,
        "abi_sha256": executor.abi_sha256,
        "composed_program_sha256": executor.composed_program_sha256,
        "target_identity_sha256": executor.target_identity_sha256,
    }
    expected = {name: getattr(target, name) for name in observed}
    if observed != expected:
        raise RuntimeError(
            "Goal5791 Home executor differs from materialized target: "
            + repr({
                name: {"observed": observed[name], "expected": expected[name]}
                for name in observed if observed[name] != expected[name]
            })
        )


def _build_plan(
    *, freeze, target, variant: str, descriptor: dict[str, object],
    source_input_sha256: str,
    output_contract_sha256: str, oracle_sha256: str,
    timer_contract_sha256: str, lifecycle_contract_sha256: str,
):
    from rtdsl.v4_fusion_ablation import (
        FusionVariant,
        build_checked_u64_product_sum_ablation_plan,
    )

    descriptor_sha256 = _digest(descriptor)
    plan_input_binding = {
        "schema": "rtdl.goal5791.segment_plan_input.v1",
        "source_input_sha256": source_input_sha256,
        "segment_descriptor_sha256": descriptor_sha256,
        "formal_input": False,
    }
    if len(source_input_sha256) != 64 or any(
        character not in "0123456789abcdef"
        for character in source_input_sha256
    ):
        raise ValueError("Goal5791 Home source input SHA-256 is invalid")
    plan = build_checked_u64_product_sum_ablation_plan(
        freeze,
        variant=FusionVariant(variant),
        target_materialization=target,
        input_sha256=_digest(plan_input_binding),
        output_contract_sha256=output_contract_sha256,
        oracle_sha256=oracle_sha256,
        timer_contract_sha256=timer_contract_sha256,
        lifecycle_contract_sha256=lifecycle_contract_sha256,
        value_count=int(descriptor["query_count"]),
    )
    if plan.input_sha256 != _digest(plan_input_binding):
        raise RuntimeError("Goal5791 Home segment-plan input binding drifted")
    return plan, plan_input_binding


def _prewarm(
    *, benchmark, graph, executor, freeze, target, max_rows: int,
    source_input_sha256: str,
    output_contract_sha256: str, oracle_sha256: str,
    timer_contract_sha256: str, lifecycle_contract_sha256: str,
) -> list[dict[str, object]]:
    """Neutral same-process OFF->ON recipe prewarm for prepared Home lanes."""

    import cupy as cp
    from scripts.goal5791_segment_descriptors import (
        iter_rt2a1_segment_descriptors,
        validate_observed_segment,
    )
    from scripts.goal5791_formal_contract import CACHE_POLICY

    descriptors = [
        dict(item) for item in iter_rt2a1_segment_descriptors(
            graph, max_relation_rows=max_rows,
            max_directed_edge_rows=max_rows,
        )
    ]
    if len(descriptors) != 1:
        raise RuntimeError("Goal5791 Home neutral K4 prewarm must be one segment")
    descriptor = descriptors[0]
    rows: list[dict[str, object]] = []
    for variant in ("fusion_off", "fusion_on"):
        plan, plan_input_binding = _build_plan(
            freeze=freeze, target=target, variant=variant,
            descriptor=descriptor,
            source_input_sha256=source_input_sha256,
            output_contract_sha256=output_contract_sha256,
            oracle_sha256=oracle_sha256,
            timer_contract_sha256=timer_contract_sha256,
            lifecycle_contract_sha256=lifecycle_contract_sha256,
        )
        descriptor_sha = _digest(descriptor)
        nonce = (
            f"goal5791-home-prewarm-pid{os.getpid()}-{variant}-"
            f"s{int(descriptor['segment_id']):06d}"
        )
        token = executor.admit_fusion_execution_token(
            plan,
            operation_execution_nonce=nonce,
            plan_input_binding_sha256=_digest(plan_input_binding),
            segment_ordinal=int(descriptor["segment_id"]),
            primitive_count=int(descriptor["primitive_count"]),
            query_count=int(descriptor["query_count"]),
            segment_descriptor_sha256=descriptor_sha,
        )
        iterator = benchmark.iter_segmented_rt_graph_device_geometry(
            graph, paper_algorithm="RT-2A1",
            max_relation_rows=max_rows,
            max_directed_edge_rows=max_rows,
        )
        segment = next(iterator)
        try:
            validate_observed_segment(descriptor, segment)
            unsealed = executor.execute_segment_unsealed(
                segment["triangles"], segment["rays"],
                ray_weights=segment["ray_weights"],
                fusion_execution_token=token,
                segment_ordinal=int(descriptor["segment_id"]),
                segment_descriptor_sha256=descriptor_sha,
            )
            if unsealed.state != "device_complete_unsealed" \
                    or token.state != "consumed" \
                    or int(unsealed.reduced_output) != 4:
                unsealed.abort()
                raise RuntimeError("Goal5791 Home neutral prewarm failed")
            # A prewarm is cache neutralization, not scientific evidence.
            unsealed.abort()
            try:
                next(iterator)
            except StopIteration:
                pass
            else:
                raise RuntimeError("Goal5791 Home prewarm added a segment")
            cp.cuda.get_current_stream().synchronize()
        finally:
            iterator.close()
            del segment
            cp.get_default_memory_pool().free_all_blocks()
        rows.append({
            "variant": variant,
            "purpose": "recipe_jit_cache_neutralization_only",
            "source_input_sha256": source_input_sha256,
            "descriptor": descriptor,
            "segment_descriptor_sha256": descriptor_sha,
            "segment_plan_input_binding": plan_input_binding,
            "plan_input_binding_sha256": _digest(plan_input_binding),
            "fusion_ablation_plan": plan.to_dict(),
            "token_pre_admitted": True,
            "token_consumed_once": True,
            "launch_completed": True,
            "synchronized": True,
            "device_pool_freed": True,
            "output_exact": True,
            "formal_evidence_created": False,
            "registered_performance_timing_created": False,
        })
    return rows


def _functional(args, legacy, app) -> dict[str, object]:
    import cupy as cp
    from rtdsl.v4_fusion_ablation import (
        load_verified_shared_contract_freeze,
        verify_target_materialization_authority,
    )
    from rtdsl.v4_operation_evidence import (
        receipt_from_mapping,
        verify_operation_evidence_receipt,
    )
    from scripts.goal5791_segment_descriptors import (
        iter_rt2a1_segment_descriptors,
        validate_observed_segment,
    )
    from scripts.goal5791_formal_contract import CACHE_POLICY

    if args.shared_freeze is None or args.target_materialization is None \
            or args.edge_file is None or args.expected_triangle_count is None \
            or args.variant is None or args.lifecycle is None \
            or args.input_kind is None or args.dataset is None:
        raise ValueError("Goal5791 Home functional mode omitted an argument")
    edge = args.edge_file.resolve()
    if not edge.is_file() or args.expected_triangle_count < 0 \
            or args.max_relation_rows <= 0:
        raise ValueError("Goal5791 Home functional input is invalid")

    target_value = json.loads(
        args.target_materialization.read_text(encoding="utf-8"))
    target = verify_target_materialization_authority(target_value)
    freeze = load_verified_shared_contract_freeze(args.shared_freeze.read_bytes())
    raw_sha = _sha(edge)
    oracle_contract = {
        "schema": "rtdl.goal5791.home_bounded_oracle.v1",
        "dataset": args.dataset,
        "edge_file_sha256": raw_sha,
        "expected_triangle_count": args.expected_triangle_count,
        "authority": "independent_stdlib_simple_undirected_triangle_recount",
    }
    output_contract = {
        "schema": "rtdl.goal5791.home_output_contract.v1",
        "paper_algorithm": "RT-2A1",
        "result": "exact_u64_triangle_count",
        "overflow": "fail_closed_before_wraparound",
    }
    no_elapsed_observation_contract = {
        "schema": "rtdl.goal5791.home_zero_elapsed_observation.v1",
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "token_admission_before_device_geometry": True,
        "device_iterator_closed_before_evidence_seal": True,
    }
    lifecycle_contract = {
        "schema": "rtdl.goal5791.home_lifecycle.v1",
        "lifecycle": args.lifecycle,
        "prepared_neutral_prewarm_order": (
            ["fusion_off", "fusion_on"]
            if args.lifecycle == "prepared" else []
        ),
        "formal_worker": False,
    }

    phase_states: list[str] = []
    benchmark = app._benchmark()
    graph = benchmark.build_segmented_rt_graph_csr_binary(
        edge, expected_triangle_count=args.expected_triangle_count)
    phase_states.append("loading_complete")

    _, executor, program = legacy._compile_executor(args, app)
    _require_target_match(executor, target)
    descriptors = [
        dict(item) for item in iter_rt2a1_segment_descriptors(
            graph,
            max_relation_rows=args.max_relation_rows,
            max_directed_edge_rows=args.max_relation_rows,
        )
    ]
    if not descriptors:
        executor.close()
        raise RuntimeError("Goal5791 Home lane planned no segment")
    descriptor_hashes = [_digest(item) for item in descriptors]
    plans = []
    plan_input_bindings = []
    tokens = []
    nonces = []
    for descriptor, descriptor_sha in zip(
        descriptors, descriptor_hashes, strict=True,
    ):
        plan, plan_input_binding = _build_plan(
            freeze=freeze, target=target, variant=args.variant,
            descriptor=descriptor,
            source_input_sha256=raw_sha,
            output_contract_sha256=_digest(output_contract),
            oracle_sha256=_digest(oracle_contract),
            timer_contract_sha256=_digest(no_elapsed_observation_contract),
            lifecycle_contract_sha256=_digest(lifecycle_contract),
        )
        segment_id = int(descriptor["segment_id"])
        nonce = (
            f"goal5791-home-pid{os.getpid()}-{args.dataset}-"
            f"{args.lifecycle}-{args.variant}-s{segment_id:06d}"
        )
        token = executor.admit_fusion_execution_token(
            plan,
            operation_execution_nonce=nonce,
            plan_input_binding_sha256=_digest(plan_input_binding),
            segment_ordinal=segment_id,
            primitive_count=int(descriptor["primitive_count"]),
            query_count=int(descriptor["query_count"]),
            segment_descriptor_sha256=descriptor_sha,
        )
        if token.state != "fresh":
            executor.close()
            raise RuntimeError("Goal5791 Home token was not freshly admitted")
        plans.append(plan)
        plan_input_bindings.append(plan_input_binding)
        tokens.append(token)
        nonces.append(nonce)
    phase_states.append("preparation_complete")

    prewarm_rows: list[dict[str, object]] = []
    if args.lifecycle == "prepared":
        if args.neutral_prewarm_edge is None:
            executor.close()
            raise ValueError("prepared Home lane omitted neutral prewarm input")
        neutral_prewarm_edge = args.neutral_prewarm_edge.resolve()
        prewarm_source_input_sha256 = _sha(neutral_prewarm_edge)
        prewarm_graph = benchmark.build_segmented_rt_graph_csr_binary(
            neutral_prewarm_edge, expected_triangle_count=4)
        prewarm_rows = _prewarm(
            benchmark=benchmark, graph=prewarm_graph, executor=executor,
            freeze=freeze, target=target, max_rows=args.max_relation_rows,
            source_input_sha256=prewarm_source_input_sha256,
            output_contract_sha256=_digest(output_contract),
            oracle_sha256=_digest({
                "schema": "rtdl.goal5791.neutral_prewarm_oracle.v1",
                "input_sha256": prewarm_source_input_sha256,
                "expected_triangle_count": 4,
                "formal_input": False,
            }),
            timer_contract_sha256=_digest(no_elapsed_observation_contract),
            lifecycle_contract_sha256=_digest(lifecycle_contract),
        )
        phase_states.append("prewarm_complete")
    else:
        phase_states.append("prewarm_not_required")

    iterator = benchmark.iter_segmented_rt_graph_device_geometry(
        graph, paper_algorithm="RT-2A1",
        max_relation_rows=args.max_relation_rows,
        max_directed_edge_rows=args.max_relation_rows,
    )
    scalar_sum = 0
    pending: list[dict[str, object]] = []
    index = 0
    try:
        while True:
            try:
                segment = next(iterator)
            except StopIteration:
                break
            if index >= len(descriptors):
                raise RuntimeError("Goal5791 Home device generator added a segment")
            descriptor = descriptors[index]
            validate_observed_segment(descriptor, segment)
            token = tokens[index]
            if token.state != "fresh":
                raise RuntimeError("Goal5791 Home token was consumed early")
            unsealed = executor.execute_segment_unsealed(
                segment["triangles"], segment["rays"],
                ray_weights=segment["ray_weights"],
                fusion_execution_token=token,
                segment_ordinal=int(descriptor["segment_id"]),
                segment_descriptor_sha256=descriptor_hashes[index],
            )
            if unsealed.state != "device_complete_unsealed" \
                    or token.state != "consumed":
                unsealed.abort()
                raise RuntimeError("Goal5791 Home token/device phase incomplete")
            value = int(unsealed.reduced_output)
            if value < 0 or scalar_sum > ((1 << 64) - 1) - value:
                unsealed.abort()
                raise OverflowError("Goal5791 Home segmented U64 overflow")
            scalar_sum += value
            pending.append({
                "unsealed": unsealed,
                "descriptor": descriptor,
                "descriptor_sha256": descriptor_hashes[index],
                "plan": plans[index],
                "plan_input_binding": plan_input_bindings[index],
                "nonce": nonces[index],
            })
            del segment
            index += 1
    except BaseException:
        iterator.close()
        for row in pending:
            row["unsealed"].abort()
        executor.close()
        raise
    if index != len(descriptors) or not pending:
        for row in pending:
            row["unsealed"].abort()
        executor.close()
        raise RuntimeError("Goal5791 Home segment cardinality drifted")
    phase_states.append("execute_complete")
    iterator.close()
    phase_states.append("device_iterator_closed")

    segment_rows: list[dict[str, object]] = []
    try:
        for row in pending:
            executed = row["unsealed"].seal()
            plan = row["plan"]
            traversal = dict(executed["traversal_receipt"])
            if not legacy._receipt_ok(traversal):
                raise RuntimeError("Goal5791 Home segment lacks true OptiX")
            traversal_semantic_binding = {
                "authority": target.callback_authority_nonce,
                "contract": target.contract_sha256,
                "abi": target.abi_sha256,
                "composed_ptx": target.composed_program_sha256,
                "native": target.native_library_sha256,
                "device_column_count": True,
            }
            if traversal.get("semantic_digest") \
                    != _digest(traversal_semantic_binding):
                raise RuntimeError(
                    "Goal5791 Home traversal semantic binding drifted")
            operation = receipt_from_mapping(
                dict(executed["operation_evidence_receipt"]))
            verify_operation_evidence_receipt(
                operation, plan.operation_contract(),
                expected_execution_nonce=row["nonce"],
            )
            if executed["fusion_ablation_plan_sha256"] != plan.plan_sha256:
                raise RuntimeError("Goal5791 Home runtime returned another plan")
            segment_rows.append({
                "segment_id": int(row["descriptor"]["segment_id"]),
                "descriptor": row["descriptor"],
                "descriptor_sha256": row["descriptor_sha256"],
                "plan_sha256": plan.plan_sha256,
                "fusion_ablation_plan": plan.to_dict(),
                "segment_plan_input_binding": row["plan_input_binding"],
                "plan_input_binding_sha256": _digest(
                    row["plan_input_binding"]),
                "operation_execution_nonce": row["nonce"],
                "token_path_only": True,
                "token_pre_admitted_in_preparation": True,
                "token_state_before_execute": "fresh",
                "token_state_after_execute": "consumed",
                "legacy_plan_argument_used_during_execute": False,
                "legacy_nonce_argument_used_during_execute": False,
                "device_phase_terminal_state": "device_complete_unsealed",
                "evidence_phase_terminal_state": "sealed",
                "reduced_output": int(executed["reduced_output"]),
                "output_sha256": executed["output_sha256"],
                "operation_evidence_receipt": operation.to_dict(),
                "checked_u64_weighted_reduction": executed[
                    "checked_u64_weighted_reduction"],
                "traversal_receipt": traversal,
                "traversal_semantic_binding": traversal_semantic_binding,
            })
        phase_states.append("evidence_seal_complete")
    finally:
        for row in pending:
            if row["unsealed"].state != "sealed":
                row["unsealed"].abort()
        executor.close()
        cp.get_default_memory_pool().free_all_blocks()
    phase_states.append("executor_close_and_pool_release_complete")

    prewarm_state = (
        "prewarm_complete" if args.lifecycle == "prepared"
        else "prewarm_not_required"
    )
    expected_phase_states = [
        "loading_complete", "preparation_complete", prewarm_state,
        "execute_complete", "device_iterator_closed",
        "evidence_seal_complete", "executor_close_and_pool_release_complete",
    ]
    if phase_states != expected_phase_states:
        raise RuntimeError("Goal5791 Home functional phase order drifted")
    phase_order = {
        "schema": "rtdl.goal5791.home_functional_phase_order.v1",
        "ordered_states": phase_states,
        "loading_complete_before_preparation": True,
        "preparation_complete_before_prewarm_or_execute": True,
        "prewarm_complete_before_execute": args.lifecycle == "prepared",
        "prewarm_not_required_before_execute": args.lifecycle != "prepared",
        "execute_complete_before_device_iterator_close": True,
        "device_iterator_closed_before_seal": True,
        "seal_after_device_iterator_close": True,
        "seal_complete_before_executor_close": True,
        "executor_close_and_pool_release_complete": True,
    }

    if scalar_sum != args.expected_triangle_count:
        raise RuntimeError("Goal5791 Home output disagrees with oracle")
    expected_events = 2 if args.variant == "fusion_on" else 7
    if any(
        int(row["operation_evidence_receipt"]["successful_event_count"])
        != expected_events for row in segment_rows
    ):
        raise RuntimeError("Goal5791 Home two-versus-seven event count drifted")
    return {
        "schema": "rtdl.goal5791.home_token_functional_lane.v1",
        "status": "PASS__TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX",
        "parent_pid": os.getpid(),
        "input_kind": args.input_kind,
        "dataset": args.dataset,
        "paper_algorithm": "RT-2A1",
        "variant": args.variant,
        "lifecycle": args.lifecycle,
        "edge_file_sha256": raw_sha,
        "edge_file_bytes": edge.stat().st_size,
        "expected_triangle_count": args.expected_triangle_count,
        "output": scalar_sum,
        "matched": True,
        "output_sha256": _digest(scalar_sum),
        "native_library_sha256": target.native_library_sha256,
        "execution_source_archive_sha256": (
            target.execution_source_archive_sha256),
        "execution_source_tree_sha256": target.execution_source_tree_sha256,
        "target_materialization_receipt_sha256": target.receipt_sha256,
        "ptx_program_identity": legacy._ptx_program_identity(program),
        "segment_count": len(segment_rows),
        "segments": segment_rows,
        "token_path_only": True,
        "all_tokens_admitted_in_preparation": True,
        "deep_plan_authority_recipe_or_operation_verification_inside_execute": False,
        "execute_phase_contiguous_without_host_preparation_or_evidence_seal": True,
        "evidence_sealed_after_complete_execute": True,
        "prepared_neutral_prewarm": {
            "performed": args.lifecycle == "prepared",
            "purpose": "recipe_jit_cache_neutralization_only",
            "order": ["fusion_off", "fusion_on"] if prewarm_rows else [],
            "rows": prewarm_rows,
        },
        "cache_policy": CACHE_POLICY,
        "functional_phase_order": phase_order,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "formal_worker": False,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "performance_or_compiler_fusion_claimed": False,
        "fresh_private_cupy_cache_at_process_start": bool(getattr(
            args, "fresh_private_cupy_cache_at_process_start", False)),
        "particle_included": False,
        "execution_environment_class": getattr(
            args, "execution_environment_class", "HOME_PASCAL_FUNCTIONAL_ONLY"),
        "pod_used": bool(getattr(args, "pod_used", False)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("inspect-target", "functional"),
                        required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", choices=("61",), required=True)
    parser.add_argument("--home-machine-authority", type=Path, required=True)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--shared-freeze", type=Path)
    parser.add_argument("--target-materialization", type=Path)
    parser.add_argument("--input-kind", choices=("small", "bounded_real"))
    parser.add_argument("--dataset")
    parser.add_argument("--edge-file", type=Path)
    parser.add_argument("--neutral-prewarm-edge", type=Path)
    parser.add_argument("--expected-triangle-count", type=int)
    parser.add_argument("--max-relation-rows", type=int, default=1_000_000)
    parser.add_argument("--variant", choices=("fusion_on", "fusion_off"))
    parser.add_argument("--lifecycle", choices=("cold", "prepared", "bounded_smoke"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    if args.mode == "functional":
        cache_spelling = os.environ.get("CUPY_CACHE_DIR")
        if not cache_spelling:
            raise RuntimeError("Goal5791 Home functional cache is not isolated")
        cache = Path(cache_spelling)
        if cache.is_symlink() or not cache.is_dir() or any(cache.iterdir()):
            raise RuntimeError(
                "Goal5791 Home functional cache is not initially empty")
        args.fresh_private_cupy_cache_at_process_start = True
    source = args.source_root.resolve()
    sys.path.insert(0, str(source))
    sys.path.insert(0, str(source / "src"))
    from scripts import goal5790_home_functional_validation as legacy

    args.home_machine_authority_value = legacy._admit_home_machine(args)
    os.environ["RTDL_OPTIX_LIB"] = str(args.native.resolve())
    os.environ["RTDL_OPTIX_LIBRARY"] = str(args.native.resolve())
    app = legacy._load(
        source / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
        f"goal5791_triangle_v4_{os.getpid()}",
    )
    if args.mode == "inspect-target":
        result = legacy._inspect_target(args, app)
        result = {
            **result,
            "schema": "rtdl.goal5791.home_target_program_inspection.v1",
            "goal5791_token_api_present": True,
            "application_worker_executed": False,
            "registered_performance_timing_created": False,
        }
    else:
        result = _functional(args, legacy, app)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": result.get("status", result.get("schema")),
        "mode": args.mode,
        "output": str(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
