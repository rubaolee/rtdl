#!/usr/bin/env python3
"""Validate both Goal5847 deploy-only families and fail-closed mutations."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from experiments.goal5798_premeasurement.workload import (
    relation_workload,
    triangle_workload,
)
from experiments.goal5847_aot_startup.contracts import digest

ROOT = Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _load_manifest(path: Path, source_commit: str) -> dict[str, object]:
    value = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    body = dict(value)
    observed = body.pop("manifest_sha256", None)
    if observed != digest(body) \
            or value.get("schema") != "rtdl.goal5847.aot_candidates.v1" \
            or value.get("status") \
                != "PASS__DEPLOY_ONLY_FAMILY_CANDIDATES_BUILT" \
            or value.get("source_commit") != source_commit:
        raise RuntimeError("Goal5847 candidate manifest differs")
    rows = value.get("rows")
    if not isinstance(rows, dict) or set(rows) != {"relation", "triangle"}:
        raise RuntimeError("Goal5847 candidate family set differs")
    for label, row in rows.items():
        if not isinstance(row, dict):
            raise TypeError(f"Goal5847 {label} candidate differs")
        for field, sha_field in (
            ("artifact", "artifact_sha256"),
            ("authority", "authority_sha256"),
            ("public", "public_sha256"),
            ("package", "package_sha256"),
            ("head", "head_sha256"),
        ):
            if _sha256_file(Path(str(row[field])).resolve(strict=True)) \
                    != row[sha_field]:
                raise RuntimeError(f"Goal5847 {label} {field} bytes differ")
    native = Path(str(value["native"])).resolve(strict=True)
    if _sha256_file(native) != value.get("native_sha256"):
        raise RuntimeError("Goal5847 native bytes differ")
    return value


def _install(runtime, row: dict[str, object]):
    return runtime.install_rtdlexe_deployment(
        trust_root_path=Path(str(row["public"])),
        trust_head_path=Path(str(row["head"])),
        trust_package_path=Path(str(row["package"])),
        deployment_id=str(row["deployment_id"]),
    )


def _load(runtime, row: dict[str, object], deployment):
    return runtime.load_rtdlexe(
        Path(str(row["artifact"])),
        authority_path=Path(str(row["authority"])),
        deployment=deployment,
    )


def _relation(runtime, receipt_validator, manifest, row):
    raw = relation_workload()
    expected = tuple(tuple(int(item) for item in value)
                     for value in raw["expected_rows"])
    deployment = _install(runtime, row)
    initializing = deployment.begin_provider_initialization(manifest["native"])
    loaded = _load(runtime, row, deployment)
    provider = initializing.bind(loaded)
    prepared = None
    try:
        prepared = provider.prepare(runtime.BoundedRelationStaticInput(
            tuple(tuple(value) for value in raw["indexed"])
        ))
        batch = runtime.BoundedRelationBatch(
            tuple(tuple(value) for value in raw["sources"]),
            expected_rows=expected,
        )
        result = prepared.execute(batch, include_diagnostics=True)
        if result.output != expected or result.output_sha256 != digest(expected):
            raise RuntimeError("Goal5847 relation oracle differs")
        receipt_validator(
            result.traversal_receipt,
            provider_library_sha256=str(manifest["native_sha256"]),
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_digest=digest(expected),
            expected_program_bundles=(
                "v4_custom_aabb_bounded_relation_composed",
            ),
            expected_successful_launch_count=2,
            expected_raygen_invocation_count=8192,
        )
        return {
            "output_sha256": result.output_sha256,
            "row_count": len(result.output),
            "compiler_attempt_count": provider.runtime_compiler_attempt_count,
            "family_executable_identity_sha256": (
                loaded.family_executable_identity_sha256
            ),
            "initialization_phases_ns": dict(initializing.phase_timings_ns),
            "traversal_receipt": dict(result.traversal_receipt),
        }
    finally:
        if prepared is not None:
            prepared.close()
        provider.close()


def _triangle(runtime, receipt_validator, manifest, row):
    raw = triangle_workload()
    vertices = tuple(tuple(value) for value in raw["vertices"])
    triangles = tuple(
        (index, index + 1, index + 2)
        for index in range(0, len(vertices), 3)
    )
    queries = tuple(
        (tuple(origin), tuple(direction), float(raw["tmax"]))
        for origin, direction in raw["rays"]
    )
    expected = int(raw["expected_weighted_sum"])
    deployment = _install(runtime, row)
    initializing = deployment.begin_provider_initialization(manifest["native"])
    loaded = _load(runtime, row, deployment)
    provider = initializing.bind(loaded)
    prepared = None
    try:
        prepared = provider.prepare(runtime.TriangleReductionStaticInput(
            vertices=vertices,
            triangles=triangles,
            event_capacity=len(raw["expected_per_ray"]),
        ))
        batch = runtime.TriangleReductionBatch(
            queries=queries,
            query_weights=tuple(int(value) for value in raw["weights"]),
            expected_reduced_u64=expected,
        )
        result = prepared.execute(batch, include_diagnostics=True)
        if result.output != expected or result.output_sha256 != digest(expected):
            raise RuntimeError("Goal5847 triangle oracle differs")
        receipt_validator(
            result.traversal_receipt,
            provider_library_sha256=str(manifest["native_sha256"]),
            route_identity=(
                "v4_builtin_triangle_callback_ir:checked_reduction_v1"
            ),
            output_digest=digest(expected),
            expected_program_bundles=(
                "v4_builtin_triangle_checked_reduction_composed",
            ),
            expected_successful_launch_count=1,
            expected_raygen_invocation_count=len(queries),
        )
        return {
            "output_sha256": result.output_sha256,
            "checked_u64_output": result.output,
            "compiler_attempt_count": provider.runtime_compiler_attempt_count,
            "family_executable_identity_sha256": (
                loaded.family_executable_identity_sha256
            ),
            "initialization_phases_ns": dict(initializing.phase_timings_ns),
            "traversal_receipt": dict(result.traversal_receipt),
        }
    finally:
        if prepared is not None:
            prepared.close()
        provider.close()


def _expect_rejection(action) -> str:
    try:
        action()
    except Exception as error:
        code = getattr(error, "code", None)
        if not isinstance(code, str) or not code.startswith("RX"):
            raise RuntimeError(
                "Goal5847 mutation did not fail through RTDL policy"
            ) from error
        return code
    raise RuntimeError("Goal5847 mutation was accepted")


def _mutations(runtime, manifest: dict[str, object]) -> dict[str, str]:
    rows = manifest["rows"]
    relation = rows["relation"]
    triangle = rows["triangle"]
    relation_deployment = _install(runtime, relation)
    triangle_deployment = _install(runtime, triangle)
    triangle_loaded = _load(runtime, triangle, triangle_deployment)
    results: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="goal5847-mutations-") as tmp:
        temporary = Path(tmp)
        artifact = temporary / "mutated.rtdlexe"
        shutil.copy2(relation["artifact"], artifact)
        artifact.write_bytes(artifact.read_bytes() + b"\n")
        results["artifact_byte_append"] = _expect_rejection(
            lambda: runtime.load_rtdlexe(
                artifact,
                authority_path=relation["authority"],
                deployment=relation_deployment,
            )
        )
        authority = temporary / "mutated.authority.json"
        shutil.copy2(relation["authority"], authority)
        authority.write_bytes(authority.read_bytes() + b"\n")
        results["authority_byte_append"] = _expect_rejection(
            lambda: runtime.load_rtdlexe(
                relation["artifact"],
                authority_path=authority,
                deployment=relation_deployment,
            )
        )
        native = temporary / "mutated.so"
        shutil.copy2(manifest["native"], native)
        native.write_bytes(native.read_bytes() + b"\x00")

        def reject_native() -> None:
            initializing = relation_deployment.begin_provider_initialization(native)
            try:
                loaded = _load(runtime, relation, relation_deployment)
                initializing.bind(loaded)
            finally:
                if initializing.state not in {"BOUND", "CLOSED"}:
                    initializing.close()

        results["native_byte_append"] = _expect_rejection(reject_native)

    def reject_cross_family() -> None:
        initializing = relation_deployment.begin_provider_initialization(
            manifest["native"]
        )
        try:
            initializing.bind(triangle_loaded)
        finally:
            if initializing.state not in {"BOUND", "CLOSED"}:
                initializing.close()

    results["cross_family_bind"] = _expect_rejection(reject_cross_family)
    results["unknown_deployment_slot"] = _expect_rejection(
        lambda: runtime.install_rtdlexe_deployment(
            trust_root_path=relation["public"],
            trust_head_path=relation["head"],
            trust_package_path=relation["package"],
            deployment_id="goal5847-not-a-frozen-slot",
        )
    )
    return results


def _write_create(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(
                json.dumps(value, indent=2, sort_keys=True).encode("utf-8")
                + b"\n"
            )
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if _git("rev-parse", "HEAD") != args.expected_source_commit \
            or _git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("Goal5847 validation requires exact clean source")
    manifest = _load_manifest(
        args.candidate_manifest, args.expected_source_commit
    )
    started = time.perf_counter_ns()
    from rtdsl import v4_rtdlexe as runtime
    from rtdsl.physical_execution_provenance import validate_traversal_receipt

    relation = _relation(
        runtime, validate_traversal_receipt, manifest,
        manifest["rows"]["relation"],
    )
    triangle = _triangle(
        runtime, validate_traversal_receipt, manifest,
        manifest["rows"]["triangle"],
    )
    mutations = _mutations(runtime, manifest)
    maps = Path("/proc/self/maps").read_text(
        encoding="utf-8", errors="replace"
    )
    nvrtc_mappings = sorted({
        line.rsplit(None, 1)[-1]
        for line in maps.splitlines()
        if "nvrtc" in line.lower()
    })
    compiler_package_prefixes = ("numba.", "llvmlite.")
    compiler_exact_names = {
        "numba",
        "llvmlite",
        "rtdsl.v4_callback_lifecycle",
        "rtdsl.v4_generic_family_lifecycle",
    }
    compiler_modules = sorted(
        name for name in sys.modules
        if name in compiler_exact_names
        or name.startswith(compiler_package_prefixes)
    )
    if relation["compiler_attempt_count"] != 0 \
            or triangle["compiler_attempt_count"] != 0 \
            or nvrtc_mappings or compiler_modules:
        raise RuntimeError("Goal5847 deploy-only validation touched a compiler")
    result: dict[str, object] = {
        "schema": "rtdl.goal5847.aot_gpu_validation.v1",
        "status": "PASS__AOT_RELATION_TRIANGLE_AND_MUTATIONS",
        "source_commit": args.expected_source_commit,
        "source_tree": _git("rev-parse", "HEAD^{tree}"),
        "candidate_manifest_sha256": _sha256_file(
            args.candidate_manifest.resolve(strict=True)
        ),
        "relation": relation,
        "triangle": triangle,
        "mutation_rejections": mutations,
        "runtime_compiler_modules": compiler_modules,
        "nvrtc_mappings": nvrtc_mappings,
        "elapsed_ns": time.perf_counter_ns() - started,
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    result["result_sha256"] = digest(result)
    _write_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
