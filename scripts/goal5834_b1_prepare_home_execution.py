#!/usr/bin/env python3
"""Bind the exact Goal5834-B1 Home target before Boolean worker zero.

This materializes the fixed Callback program but prepares no scene, launches
no ray, imports no oracle, and records no timing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_curve import V4CurveTarget, curve_any_contact_boolean_source


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    return json.loads(path.read_text(
        encoding="utf-8",
        errors="strict",
    ), parse_constant=lambda value: (_ for _ in ()).throw(
        ValueError(f"non-standard JSON constant {value}")))


def _write_artifacts(root: Path, source, program, materialized):
    root.mkdir(parents=True, exist_ok=False)
    executable = materialized.executable
    bodies = {
        "callback_source.py": source._source.encode("utf-8"),
        "wrapper.cu": executable.wrapper.source.encode("utf-8"),
        "wrapper.ptx": executable.wrapper_ptx.encode("utf-8"),
        "composed.ptx": executable.composed.ptx.encode("utf-8"),
        "nvrtc.log": materialized.compiler_log.encode("utf-8"),
    }
    for index, leaf in enumerate(executable.generated_leaves):
        bodies[f"leaf_{index}_{leaf.role.value}.py"] = \
            leaf.generated_source.encode("utf-8")
    for index, leaf in enumerate(executable.compiled_leaves):
        bodies[f"leaf_{index}_{leaf.role}.ptx"] = leaf.ptx.encode("utf-8")
    members = []
    for name, body in sorted(bodies.items()):
        path = root / name
        path.write_bytes(body)
        members.append({
            "path": name,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        })
    manifest = {
        "schema": "rtdl.goal5834_b1.materialized_executable.v1",
        "executable_sha256": executable.executable_sha256,
        "member_count": len(members),
        "members": members,
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    return {**manifest, "manifest_sha256": _sha(manifest_path)}


def prepare(args):
    native = args.native.resolve(strict=True)
    fixture_authority = args.fixture_authority.resolve(strict=True)
    worker_inputs = args.worker_inputs.resolve(strict=True)
    source_projection = args.source_projection.resolve(strict=True)
    authority = _load(fixture_authority)
    if authority.get("schema") != "rtdl.goal5834_b1.fixture_authority.v1" \
            or authority.get("status") != \
                "SCIENTIFIC_FIXTURES_FROZEN__WORKER_ZERO_FORBIDDEN" \
            or authority.get("goal5835_authorized") is not False:
        raise RuntimeError("fixture authority status differs")
    if authority["worker_inputs"]["sha256"] != _sha(worker_inputs):
        raise RuntimeError("worker inputs differ from fixture authority")
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    target = V4CurveTarget.from_native(
        native, optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability)
    toolchain = V4Toolchain.current(
        compute_capability=tuple(
            int(value) for value in args.compute_capability.split(".")),
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
    )
    source = curve_any_contact_boolean_source()
    program = source.compile(target=target)
    materialized = program.materialize(toolchain=toolchain)
    artifacts = _write_artifacts(
        args.artifact_dir.resolve(), source, program, materialized)
    lineage = args.lineage
    predecessor = None
    if lineage in {"B2", "B3"}:
        if args.predecessor_failure is None:
            raise RuntimeError("B2 requires the exact B1 predecessor failure")
        predecessor_path = args.predecessor_failure.resolve(strict=True)
        predecessor = {
            "path": str(predecessor_path),
            "sha256": _sha(predecessor_path),
        }
    elif args.predecessor_failure is not None:
        raise RuntimeError("B1 cannot carry a predecessor failure")
    return {
        "schema": (
            "rtdl.goal5834_b3.home_target_preaction.v1"
            if lineage == "B3" else
            "rtdl.goal5834_b2.home_target_preaction.v1"
            if lineage == "B2" else
            "rtdl.goal5834_b1.home_target_preaction.v1"),
        "status": (
            "B3_TARGET_BOUND__SAME_FIXTURES__FORK_CLEAN_ROWS_AUTHORIZED"
            if lineage == "B3" else
            "B2_TARGET_BOUND__SAME_FIXTURES__PRIMARY_WORKER_ZERO_AUTHORIZED"
            if lineage == "B2" else
            "TARGET_AND_EXECUTABLE_BOUND__PRIMARY_WORKER_ZERO_AUTHORIZED"),
        "lineage": lineage,
        "predecessor_failure": predecessor,
        "scope": "FUNCTIONAL_ONLY__NO_PERFORMANCE",
        "registered_performance_timing_count": 0,
        "application_worker_count_at_emission": 0,
        "fixture_authority_sha256": _sha(fixture_authority),
        "worker_inputs_sha256": _sha(worker_inputs),
        "source_projection_sha256": _sha(source_projection),
        "native_path": str(native),
        "native_sha256": _sha(native),
        "optix_sdk": args.optix_sdk,
        "compute_capability": args.compute_capability,
        "optix_include": str(args.optix_include.resolve(strict=True)),
        "cuda_include": str(args.cuda_include.resolve(strict=True)),
        "source_sha256": source.source_sha256,
        "callback_ir_sha256": program.authority.callback.ir_sha256,
        "callback_effect_digest": program.authority.callback.effect_digest,
        "physical_schema_sha256": program.authority.schema.schema_sha256,
        "canonical_plan_sha256": program.authority.canonical_plan.plan_sha256,
        "callback_abi_sha256": program.abi.abi_sha256,
        "wrapper_source_sha256": program.wrapper.source_sha256,
        "executable_sha256": materialized.executable.executable_sha256,
        "artifacts": artifacts,
        "goal5835_authorized": False,
        "outcome_accepted_unconditionally": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--compute-capability", default="6.1")
    parser.add_argument("--fixture-authority", required=True, type=Path)
    parser.add_argument("--worker-inputs", required=True, type=Path)
    parser.add_argument("--source-projection", required=True, type=Path)
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lineage", choices=("B1", "B2", "B3"), default="B1")
    parser.add_argument("--predecessor-failure", type=Path)
    args = parser.parse_args()
    result = prepare(args)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": result["status"],
        "native_sha256": result["native_sha256"],
        "executable_sha256": result["executable_sha256"],
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
