#!/usr/bin/env python3
"""Run one fresh four-lane member and emit a behavior-level OptiX receipt."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile


APP_DIR = Path(__file__).resolve().parent
ROOT = next(parent for parent in APP_DIR.parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.physical_execution_provenance import OptixTraversalAuditSession


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _stable_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _receipt_is_complete(receipt: dict[str, object]) -> bool:
    snapshot = receipt["native_snapshot"]
    return bool(
        receipt["physical_executor_classification"] == "optix_traversal_observed"
        and receipt["expected_program_observed_at_receipt_edge"] is True
        and snapshot["successful_launch_count"] > 0
        and snapshot["successful_launch_count"] == snapshot["complete_context_launch_count"]
        and snapshot["failed_launch_count"] == 0
        and snapshot["incomplete_context_launch_count"] == 0
        and snapshot["pending_context_at_finish"] == 0
        and snapshot["session_error"] == 0
        and snapshot["first_program_bundle_id"] != 0
        and snapshot["last_program_bundle_id"] != 0
        and snapshot["first_traversable"] != 0
        and snapshot["last_traversable"] != 0
        and snapshot["raygen_invocation_count"] > 0
    )


def _run_segmented_epochs(
    *,
    module,
    version: str,
    paper_algorithm: str,
    edge_file: Path,
    expected_triangle_count: int,
    max_relation_rows: int,
    epoch_segments: int,
    semantic_digest: str,
    expected_program_bundle: str,
    prepared_v3_program=None,
    prepared_v3_execution_ticket=None,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Reset the CUDA/OptiX context after a bounded number of GAS builds."""

    if not hasattr(os, "fork"):
        raise RuntimeError("SEGMENT_EPOCH_EXECUTION_REQUIRES_POSIX_FORK")
    if epoch_segments <= 0:
        raise ValueError("epoch_segments must be positive")
    app = module._load_benchmark()
    contract = app.build_segmented_rt_graph_csr_binary(
        str(edge_file), expected_triangle_count=expected_triangle_count
    )
    segment_count = app.count_segmented_rt_graph_segments(
        contract,
        max_relation_rows=max_relation_rows,
        max_directed_edge_rows=max_relation_rows,
    )
    if segment_count <= 0:
        raise RuntimeError("AT_LEAST_ONE_PHYSICAL_SEGMENT_REQUIRED")
    epoch_results: list[dict[str, object]] = []
    scalar_sum = 0
    for epoch_index, start in enumerate(range(0, segment_count, epoch_segments)):
        stop = min(segment_count, start + epoch_segments)
        handle = tempfile.NamedTemporaryFile(
            prefix="goal5726_epoch_", suffix=".json", delete=False
        )
        child_path = Path(handle.name)
        handle.close()
        child_path.unlink()
        pid = os.fork()
        if pid == 0:
            try:
                with OptixTraversalAuditSession.open() as audit:
                    if version == "v2_14":
                        partial = module.run_v2_14_segmented_contract_epoch(
                            graph_contract=contract,
                            paper_algorithm=paper_algorithm,
                            max_relation_rows=max_relation_rows,
                            start_segment_id=start,
                            stop_segment_id=stop,
                        )
                    else:
                        partial = module.run_v3_segmented_contract_epoch(
                            graph_contract=contract,
                            paper_algorithm=paper_algorithm,
                            max_relation_rows=max_relation_rows,
                            start_segment_id=start,
                            stop_segment_id=stop,
                            require_optix=True,
                            prepared_program=prepared_v3_program,
                            prepared_execution_ticket=prepared_v3_execution_ticket,
                        )
                    partial_scalar = int(partial["output"]["triangle_count"])
                    epoch_semantic = _stable_digest(
                        {
                            "parent_semantic_digest": semantic_digest,
                            "epoch_index": epoch_index,
                            "start_segment_id": start,
                            "stop_segment_id": stop,
                        }
                    )
                    epoch_output = _stable_digest(
                        {
                            "partial_scalar_sum": partial_scalar,
                            "start_segment_id": start,
                            "stop_segment_id": stop,
                        }
                    )
                    receipt = audit.finish(
                        semantic_digest=epoch_semantic,
                        output_digest=epoch_output,
                        route_identity=(
                            f"goal5726.{version}.{paper_algorithm}.epoch_{epoch_index}"
                        ),
                        expected_program_bundles=(expected_program_bundle,),
                    )
                child_payload = {
                    "epoch_index": epoch_index,
                    "start_segment_id": start,
                    "stop_segment_id": stop,
                    "pid": os.getpid(),
                    "partial_result": partial,
                    "partial_scalar_sum": partial_scalar,
                    "receipt": receipt,
                }
                child_path.write_text(
                    json.dumps(child_payload, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                os._exit(0)
            except BaseException as exc:
                child_path.write_text(
                    json.dumps(
                        {
                            "epoch_index": epoch_index,
                            "start_segment_id": start,
                            "stop_segment_id": stop,
                            "pid": os.getpid(),
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        },
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                os._exit(1)
        waited_pid, status = os.waitpid(pid, 0)
        try:
            child_payload = json.loads(child_path.read_text(encoding="utf-8"))
        finally:
            child_path.unlink(missing_ok=True)
        if waited_pid != pid or not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
            raise RuntimeError(f"SEGMENT_EPOCH_FAILED:{json.dumps(child_payload, sort_keys=True)}")
        if child_payload["pid"] != pid or not _receipt_is_complete(child_payload["receipt"]):
            raise RuntimeError("SEGMENT_EPOCH_RECEIPT_FAILED_CLOSED")
        value = int(child_payload["partial_scalar_sum"])
        if value < 0 or scalar_sum > ((1 << 64) - 1) - value:
            raise RuntimeError("SEGMENT_EPOCH_U64_SUM_OVERFLOW")
        scalar_sum += value
        epoch_results.append(child_payload)
    native_shas = {
        row["receipt"]["provider_library_sha256"]
        for row in epoch_results
    }
    if len(native_shas) != 1 or len({row["pid"] for row in epoch_results}) != len(epoch_results):
        raise RuntimeError("SEGMENT_EPOCH_IDENTITY_FAILED_CLOSED")
    result = {
        "schema": f"rtdl.paper_reproduction.rt_graph_triangle_counting.{version}.segmented_epoch.v1",
        "version": "v2.14" if version == "v2_14" else "v3",
        "paper_algorithm": paper_algorithm,
        "application_selected_algorithm": True,
        "default_selected_between_paper_algorithms": False,
        "output": {"triangle_count": scalar_sum},
        "expected": {"triangle_count": int(expected_triangle_count)},
        "matched": scalar_sum == int(expected_triangle_count),
        "segmented_execution": True,
        "fresh_cuda_context_epochs": True,
        "segment_count": segment_count,
        "epoch_count": len(epoch_results),
        "epoch_segments": epoch_segments,
        "native_sha256": next(iter(native_shas)),
        "compiler_lifecycle": (
            "compiler_prepared_then_execute"
            if version == "v3" and prepared_v3_program is not None
            or version == "v3" and prepared_v3_execution_ticket is not None
            else "cold_compile_and_execute"
            if version == "v3"
            else "v2_direct_execute"
        ),
    }
    return result, epoch_results


def run_one(
    *,
    version: str,
    paper_algorithm: str,
    fixture: str,
    edge_file: Path | None = None,
    edge_format: str = "text",
    expected_triangle_count: int | None = None,
    segmented: bool = False,
    max_relation_rows: int = 1_000_000,
    epoch_segments: int = 256,
) -> dict[str, object]:
    if version == "v2_14":
        module_path = APP_DIR / "v2_14_whole_app.py"
        module = _load("goal5725_receipt_v2", module_path)
    elif version == "v3":
        module_path = APP_DIR / "rtdl3_action_migration.py"
        module = _load("goal5725_receipt_v3", module_path)
    else:
        raise ValueError("version must be v2_14 or v3")

    input_sha256 = None if edge_file is None else _file_sha256(edge_file)
    semantic_input = {
        "version": version,
        "paper_algorithm": paper_algorithm,
        "fixture": fixture,
        "edge_file_sha256": input_sha256,
        "edge_file_bytes": None if edge_file is None else edge_file.stat().st_size,
        "edge_format": edge_format,
        "entrypoint_sha256": _file_sha256(module_path),
        "algorithm_is_application_selected": True,
        "cross_algorithm_selection_allowed": False,
        "segmented_execution": segmented,
        "max_relation_rows": max_relation_rows if segmented else None,
        "epoch_segments": epoch_segments if segmented else None,
    }
    semantic_digest = _stable_digest(semantic_input)
    expected_program_bundle = (
        "ray_triangle_hit_count_sum_3d"
        if paper_algorithm == "RT-1A2"
        else "ray_triangle_any_hit_weighted_sum_3d"
    )
    if segmented and epoch_segments:
        if edge_file is None or expected_triangle_count is None:
            raise ValueError("segmented epoch execution requires edge file and author count")
        result, epoch_results = _run_segmented_epochs(
            module=module,
            version=version,
            paper_algorithm=paper_algorithm,
            edge_file=edge_file,
            expected_triangle_count=expected_triangle_count,
            max_relation_rows=max_relation_rows,
            epoch_segments=epoch_segments,
            semantic_digest=semantic_digest,
            expected_program_bundle=expected_program_bundle,
        )
        receipts = [row["receipt"] for row in epoch_results]
    else:
        with OptixTraversalAuditSession.open() as audit:
            if version == "v2_14":
                result = module.run_v2_14(
                    paper_algorithm=paper_algorithm,
                    fixture=fixture,
                    backend="optix",
                    edge_file=None if edge_file is None else str(edge_file),
                    edge_format=edge_format,
                    partner="cupy" if edge_file is not None else "none",
                    expected_triangle_count=expected_triangle_count,
                    segmented=segmented,
                    max_relation_rows=max_relation_rows,
                )
            else:
                result = module.run_v3_algorithm(
                    paper_algorithm=paper_algorithm,
                    fixture=fixture,
                    edge_file=None if edge_file is None else str(edge_file),
                    edge_format=edge_format,
                    partner="cupy" if edge_file is not None else "none",
                    require_optix=True,
                    expected_triangle_count=expected_triangle_count,
                    segmented=segmented,
                    max_relation_rows=max_relation_rows,
                )
            receipt = audit.finish(
                semantic_digest=semantic_digest,
                output_digest=_stable_digest(
                    {"paper_algorithm": paper_algorithm, "output": result["output"]}
                ),
                route_identity=f"goal5725.{version}.{paper_algorithm}",
                expected_program_bundles=(expected_program_bundle,),
            )
        receipts = [receipt]
        epoch_results = []
    if expected_triangle_count is not None and result["expected"]["triangle_count"] != expected_triangle_count:
        raise RuntimeError("AUTHOR_EXPECTED_TRIANGLE_COUNT_MISMATCH")
    correctness = {
        "paper_algorithm": result["paper_algorithm"],
        "output": result["output"],
        "expected": result["expected"],
        "matched": result["matched"],
        "default_selected_between_paper_algorithms": result[
            "default_selected_between_paper_algorithms"
        ],
    }
    output_digest = _stable_digest(correctness)
    valid = (
        result["matched"] is True
        and result["default_selected_between_paper_algorithms"] is False
        and bool(receipts)
        and all(_receipt_is_complete(receipt) for receipt in receipts)
    )
    payload: dict[str, object] = {
        "schema": (
            "rtdl.goal5726.triangle_counting_segmented_epoch_functional_receipt.v1"
            if segmented and epoch_segments
            else "rtdl.goal5725.triangle_counting_four_lane_functional_receipt.v1"
        ),
        "goal": 5726 if segmented and epoch_segments else 5725,
        "version": version,
        "paper_algorithm": paper_algorithm,
        "fixture": fixture,
        "edge_file_sha256": input_sha256,
        "edge_file_bytes": None if edge_file is None else edge_file.stat().st_size,
        "pid": __import__("os").getpid(),
        "semantic_input": semantic_input,
        "semantic_digest": semantic_digest,
        "correctness": correctness,
        "correctness_output_sha256": output_digest,
        "traversal_receipts": receipts,
        "traversal_receipt": receipts[0] if len(receipts) == 1 else None,
        "epoch_results": epoch_results,
        "functional_gate_passed": valid,
        "performance_eligible": False,
        "performance_claimed": False,
        "rt_core_silicon_utilization_claimed": False,
        "segmented_execution": segmented,
        "max_relation_rows": max_relation_rows if segmented else None,
        "epoch_segments": epoch_segments if segmented else None,
        "segment_count": result.get("segment_count") if segmented else None,
        "epoch_count": result.get("epoch_count") if segmented else None,
        "fresh_cuda_context_epochs": (
            result.get("fresh_cuda_context_epochs") if segmented else None
        ),
        "native_sha256": result.get("native_sha256") if segmented else None,
    }
    payload["payload_sha256"] = _stable_digest(payload)
    if not valid:
        raise RuntimeError(json.dumps(payload, sort_keys=True))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, choices=("v2_14", "v3"))
    parser.add_argument("--paper-algorithm", required=True, choices=("RT-1A2", "RT-2A1"))
    parser.add_argument("--fixture", default="degree_oriented_two_triangles")
    parser.add_argument("--edge-file", type=Path)
    parser.add_argument("--edge-format", choices=("text", "binary"), default="binary")
    parser.add_argument("--expected-triangle-count", type=int)
    parser.add_argument("--segmented", action="store_true")
    parser.add_argument("--max-relation-rows", type=int, default=1_000_000)
    parser.add_argument("--epoch-segments", type=int, default=256)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run_one(
        version=args.version,
        paper_algorithm=args.paper_algorithm,
        fixture=args.fixture,
        edge_file=args.edge_file,
        edge_format=args.edge_format,
        expected_triangle_count=args.expected_triangle_count,
        segmented=args.segmented,
        max_relation_rows=args.max_relation_rows,
        epoch_segments=args.epoch_segments,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
