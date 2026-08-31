#!/usr/bin/env python3
"""Observation-only RT-BarnesHut V2/V4 prepared-route profiler.

This script executes the unchanged Goal5776 paper-app routes on the real-scale
32,768-body input.  It records mutually exclusive outer-envelope accounting
for V4 by timing existing function boundaries.  The observations are
diagnostic and profiler-perturbed; no duration is a predicted saving.
"""

from __future__ import annotations

import argparse
import cProfile
from contextlib import ExitStack
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pstats
import statistics
import sys
import time
from typing import Any, Callable

from rtdsl import aggregate_hierarchy_native as aggregate_native
from rtdsl import v4_hierarchy_frontier as hierarchy_frontier
from rtdsl.optix_runtime import _load_optix_library
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _load_app(source_root: Path):
    path = source_root / "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py"
    spec = importlib.util.spec_from_file_location("goal5780_rtbh_v4", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the RT-BarnesHut V4 front door")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _receipt_ok(receipt: dict[str, object]) -> bool:
    snapshot = dict(receipt["native_snapshot"])
    successful = int(snapshot["successful_launch_count"])
    return (
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and successful > 0
        and int(snapshot["complete_context_launch_count"]) == successful
        and all(int(snapshot[name]) == 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error",
        ))
        and bool(snapshot["first_traversable"])
        and bool(snapshot["last_traversable"])
    )


class BoundaryProfiler:
    """Small inclusive boundary profiler with parent labels.

    The final accounting uses only sibling boundaries, so the reported V4
    categories are mutually exclusive and mechanically reconcile to the
    observed complete endpoint duration.
    """

    def __init__(self) -> None:
        self.active_method: str | None = None
        self.stack: list[str] = []
        self.calls: list[dict[str, object]] = []
        self._restores: list[Callable[[], None]] = []

    def patch(self, owner: object, name: str, category: str) -> None:
        original = getattr(owner, name)

        @functools.wraps(original)
        def wrapped(*args, **kwargs):
            if self.active_method is None:
                return original(*args, **kwargs)
            parent = self.stack[-1] if self.stack else None
            self.stack.append(category)
            started = time.perf_counter()
            try:
                return original(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - started
                popped = self.stack.pop()
                if popped != category:
                    raise RuntimeError("Goal5780 boundary stack corrupted")
                self.calls.append({
                    "method": self.active_method,
                    "category": category,
                    "parent": parent,
                    "seconds": elapsed,
                })

        setattr(owner, name, wrapped)
        self._restores.append(lambda: setattr(owner, name, original))

    def close(self) -> None:
        for restore in reversed(self._restores):
            restore()
        self._restores.clear()

    def sum(self, method: str, category: str, *, parent: str | None | object = ...) -> float:
        rows = [row for row in self.calls
                if row["method"] == method and row["category"] == category]
        if parent is not ...:
            rows = [row for row in rows if row["parent"] == parent]
        return sum(float(row["seconds"]) for row in rows)


def _cprofile_rows(profile: cProfile.Profile, source_root: Path) -> list[dict[str, object]]:
    wanted = {
        str((source_root / "src/rtdsl/v4_hierarchy_frontier.py").resolve()),
        str((source_root / "src/rtdsl/aggregate_hierarchy_native.py").resolve()),
        str((source_root / "src/rtdsl/physical_execution_provenance.py").resolve()),
        str((source_root / "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py").resolve()),
    }
    result: list[dict[str, object]] = []
    for (filename, line, function), values in pstats.Stats(profile).stats.items():
        if str(Path(filename).resolve()) not in wanted:
            continue
        primitive, total, self_seconds, cumulative_seconds, _callers = values
        result.append({
            "source": str(Path(filename).resolve().relative_to(source_root)),
            "line": int(line),
            "function": function,
            "primitive_calls": int(primitive),
            "total_calls": int(total),
            "self_seconds_profiled_not_saving": float(self_seconds),
            "cumulative_seconds_profiled_not_saving": float(cumulative_seconds),
        })
    return sorted(result, key=lambda row: (
        -float(row["cumulative_seconds_profiled_not_saving"]),
        str(row["source"]), int(row["line"]), str(row["function"]),
    ))


def _exclusive_v4_accounting(
    profiler: BoundaryProfiler, complete_seconds: float,
) -> dict[str, float]:
    owner = profiler.sum("v4", "v4_owner")
    native = profiler.sum("v4", "native_endpoint")
    static = profiler.sum("v4", "static_authority")
    accept = profiler.sum("v4", "endpoint_accept")
    output_digest = profiler.sum(
        "v4", "hierarchy_digest", parent="v4_owner")
    app_projection = profiler.sum("v4", "app_projection")
    owner_residual = owner - native - static - accept - output_digest
    app_residual = complete_seconds - owner - app_projection
    tolerance = 1.0e-7
    if owner_residual < -tolerance or app_residual < -tolerance:
        raise RuntimeError("Goal5780 exclusive accounting became negative")
    owner_residual = max(0.0, owner_residual)
    app_residual = max(0.0, app_residual)
    categories = {
        "native_endpoint_seconds_observed_not_saving": native,
        "prepared_static_authority_seconds_observed_not_saving": static,
        "output_binding_digest_seconds_observed_not_saving": output_digest,
        "receipt_and_endpoint_accept_seconds_observed_not_saving": accept,
        "owner_residual_copy_audit_control_seconds_observed_not_saving": owner_residual,
        "application_projection_seconds_observed_not_saving": app_projection,
        "application_wrapper_residual_seconds_observed_not_saving": app_residual,
    }
    reconciled = sum(categories.values())
    if abs(reconciled - complete_seconds) > max(1.0e-6, complete_seconds * 1.0e-5):
        raise RuntimeError("Goal5780 V4 categories do not reconcile")
    categories["reconciled_complete_seconds"] = reconciled
    categories["accounting_delta_seconds"] = reconciled - complete_seconds
    return categories


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--prepared-arrays", required=True, type=Path)
    parser.add_argument("--expected-forces", required=True, type=Path)
    parser.add_argument("--expected-prepared-sha256", required=True)
    parser.add_argument("--expected-forces-sha256", required=True)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--observations", type=int, default=4)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.observations < 2:
        raise ValueError("at least two observation blocks are required")
    source_root = args.source_root.resolve()
    native = args.native.resolve()
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    app = _load_app(source_root)
    data = app.load_real_scale_v4_input(
        args.prepared_arrays, args.expected_forces,
        expected_prepared_sha256=args.expected_prepared_sha256,
        expected_forces_sha256=args.expected_forces_sha256,
    )
    expected = tuple(data["expected_rows"])
    maximum = data["spec"].prepared_hierarchy.hierarchy.point_count
    v4_owner = app.prepare_v4(prepared_input=data)
    v2_owner = aggregate_native.prepare_aggregate_frontier_reduce_explicit_native_3d(
        data["spec"], backend="optix_traversal", max_output_rows=maximum)
    library = _load_optix_library()
    profiler = BoundaryProfiler()
    profiler.patch(
        hierarchy_frontier.PreparedHierarchyFrontierOwner,
        "execute", "v4_owner")
    profiler.patch(
        aggregate_native.PreparedNativeAggregateHierarchy3D,
        "execute", "native_endpoint")
    profiler.patch(
        hierarchy_frontier.PreparedHierarchyFrontierOwner,
        "_check_static_authority", "static_authority")
    profiler.patch(hierarchy_frontier, "_digest", "hierarchy_digest")
    profiler.patch(
        hierarchy_frontier, "_accept_hierarchy_endpoint", "endpoint_accept")
    profiler.patch(app, "_canonical_force_rows", "app_projection")

    observations: list[dict[str, object]] = []
    try:
        # Warmups are correctness/behavior gates and are never observations.
        warm_v4 = v4_owner.execute(softening=0.0)
        if not warm_v4["matched"] or not _receipt_ok(warm_v4["traversal_receipt"]):
            raise RuntimeError("Goal5780 V4 warmup failed closed")
        with OptixTraversalAuditSession.open(
            library=library, library_path=native,
        ) as audit:
            warm_physical = v2_owner.execute(softening=0.0)
            warm_v2 = app._canonical_force_rows(tuple({
                "source_id": int(row["source_id"]),
                "scalar_force": float(row["reducer_value_0"]) * float(data["force_scale"]),
            } for row in warm_physical["rows"]))
            warm_receipt = audit.finish(
                semantic_digest=str(data["input_sha256"]),
                output_digest=_digest(warm_v2),
                route_identity="goal5780:rt_barneshut:v2:warmup",
            )
        if not app._compare_force_rows(warm_v2, expected)["matched"] \
                or not _receipt_ok(warm_receipt):
            raise RuntimeError("Goal5780 V2 warmup failed closed")

        for block in range(args.observations):
            order = ("v2", "v4") if block % 2 == 0 else ("v4", "v2")
            for method in order:
                profiler.calls.clear()
                profiler.active_method = method
                if method == "v4":
                    started = time.perf_counter()
                    row = v4_owner.execute(softening=0.0)
                    complete = time.perf_counter() - started
                    profiler.active_method = None
                    if not row["matched"] or not _receipt_ok(row["traversal_receipt"]):
                        raise RuntimeError("Goal5780 V4 observation failed closed")
                    registered = float(
                        row["registered_prepared_execution_seconds"])
                    accounting = _exclusive_v4_accounting(
                        profiler, registered)
                    observations.append({
                        "block": block,
                        "order": order.index(method),
                        "method": method,
                        "complete_call_seconds_including_post_timer_comparator_profiled_not_formal": complete,
                        "registered_endpoint_seconds_profiled_not_formal": registered,
                        "output_sha256": _digest(row["output"]),
                        "traversal_receipt": row["traversal_receipt"],
                        "mutually_exclusive_accounting": accounting,
                    })
                else:
                    started = time.perf_counter()
                    with OptixTraversalAuditSession.open(
                        library=library, library_path=native,
                    ) as audit:
                        physical = v2_owner.execute(softening=0.0)
                        output = app._canonical_force_rows(tuple({
                            "source_id": int(row["source_id"]),
                            "scalar_force": (
                                float(row["reducer_value_0"])
                                * float(data["force_scale"])
                            ),
                        } for row in physical["rows"]))
                        output_sha = _digest(output)
                        receipt = audit.finish(
                            semantic_digest=str(data["input_sha256"]),
                            output_digest=output_sha,
                            route_identity=f"goal5780:rt_barneshut:v2:block{block}",
                        )
                    complete = time.perf_counter() - started
                    profiler.active_method = None
                    if not app._compare_force_rows(output, expected)["matched"] \
                            or not _receipt_ok(receipt):
                        raise RuntimeError("Goal5780 V2 observation failed closed")
                    native_seconds = profiler.sum("v2", "native_endpoint")
                    app_projection = profiler.sum("v2", "app_projection")
                    residual = complete - native_seconds - app_projection
                    if residual < -1.0e-7:
                        raise RuntimeError("Goal5780 V2 exclusive accounting became negative")
                    accounting = {
                        "native_endpoint_seconds_observed_not_saving": native_seconds,
                        "application_projection_body_excluded_seconds_observed_not_saving": app_projection,
                        "audit_projection_and_wrapper_residual_seconds_observed_not_saving": max(0.0, residual),
                    }
                    accounting["reconciled_complete_seconds"] = sum(accounting.values())
                    accounting["accounting_delta_seconds"] = (
                        accounting["reconciled_complete_seconds"] - complete)
                    observations.append({
                        "block": block,
                        "order": order.index(method),
                        "method": method,
                        "complete_endpoint_seconds_profiled_not_formal": complete,
                        "output_sha256": output_sha,
                        "traversal_receipt": receipt,
                        "mutually_exclusive_accounting": accounting,
                    })

        # A separate cProfile execution supplies call-path detail only.  It is
        # not used in the mutually exclusive accounting or any ratio.
        cprof = cProfile.Profile()
        cprof.enable()
        cprof_result = v4_owner.execute(softening=0.0)
        cprof.disable()
        if not cprof_result["matched"] or not _receipt_ok(
                cprof_result["traversal_receipt"]):
            raise RuntimeError("Goal5780 cProfile observation failed closed")
        cprofile_rows = _cprofile_rows(cprof, source_root)
    finally:
        profiler.active_method = None
        profiler.close()
        with ExitStack() as stack:
            stack.callback(v4_owner.close)
            stack.callback(v2_owner.close)

    v4_seconds = [float(row["registered_endpoint_seconds_profiled_not_formal"])
                  for row in observations if row["method"] == "v4"]
    v2_seconds = [float(row["complete_endpoint_seconds_profiled_not_formal"])
                  for row in observations if row["method"] == "v2"]
    result = {
        "schema": "rtdl.goal5780.rt_barneshut_unchanged_route_profile.v1",
        "status": "COMPLETE__OBSERVATION_ONLY__NO_REPAIR_AUTHORIZED",
        "source_identity": {
            "hierarchy_frontier_sha256": _sha(
                source_root / "src/rtdsl/v4_hierarchy_frontier.py"),
            "whole_app_sha256": _sha(
                source_root / "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py"),
            "v2_direct_sha256": _sha(
                source_root / "Paper-reproduction-apps/rt-barneshut-paper/v2_true_optix_direct.py"),
            "aggregate_hierarchy_native_sha256": _sha(
                source_root / "src/rtdsl/aggregate_hierarchy_native.py"),
            "native_library_sha256": _sha(native),
        },
        "input_identity": {
            "prepared_arrays_sha256": _sha(args.prepared_arrays),
            "expected_forces_sha256": _sha(args.expected_forces),
            "semantic_input_sha256": data["input_sha256"],
            "body_count": len(expected),
            "hierarchy_node_count": int(
                data["spec"].prepared_hierarchy.hierarchy.node_count),
        },
        "protocol": {
            "observation_count_per_method": args.observations,
            "schedule": "alternating_block_AB_BA",
            "profiler_perturbed_not_formal": True,
            "registered_formal_row_created": False,
            "mutually_exclusive_accounting": True,
            "component_medians_may_not_be_added": True,
            "observed_component_seconds_are_not_predicted_savings": True,
        },
        "observations": observations,
        "summary": {
            "v2_complete_median_seconds_profiled_not_formal": statistics.median(v2_seconds),
            "v4_registered_endpoint_median_seconds_profiled_not_formal": statistics.median(v4_seconds),
            "v4_minus_v2_median_endpoint_delta_seconds_profiled_not_formal": (
                statistics.median(v4_seconds) - statistics.median(v2_seconds)),
            "all_outputs_exact": True,
            "all_receipts_behaviorally_true_optix": True,
        },
        "cprofile_call_path_diagnostic": cprofile_rows,
        "claim_boundary": {
            "product_source_changed": False,
            "native_changed": False,
            "paper_app_changed": False,
            "performance_claimed": False,
            "predicted_saving_claimed": False,
            "repair_authorized_or_implemented": False,
            "modern_rtx_claimed": False,
            "goal5776_changed_or_relabelled": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({
        "output": str(args.output),
        "sha256": _sha(args.output),
        "status": result["status"],
        "summary": result["summary"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
