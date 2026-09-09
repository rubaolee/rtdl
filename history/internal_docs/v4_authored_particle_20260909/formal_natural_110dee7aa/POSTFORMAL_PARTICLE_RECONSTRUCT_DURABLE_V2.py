#!/usr/bin/env python3
"""Reconstruct and bind Particle compiler artifacts after the formal run.

This is deliberately a post-formal reconstruction.  It never labels generated
files or receipts as bytes retained by the original timed workers.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile

import numpy as np

from experiments.v4_authored_particle.program import (
    FACE_FIRST_SOURCE,
    build_face_first_physical_plan,
    face_first_expected,
    face_first_manifest,
)
from experiments.v4_paper_apps_pyoptix.inputs import sha256
from rtdsl import v4


def digest_array(value: np.ndarray) -> str:
    value = np.ascontiguousarray(value, dtype=np.uint32)
    result = hashlib.sha256()
    result.update(value.dtype.str.encode("ascii"))
    result.update(str(tuple(value.shape)).encode("ascii"))
    result.update(memoryview(value).cast("B"))
    return result.hexdigest()


def load_particle_directory(root: Path) -> dict[str, object]:
    root = root.resolve(strict=True)
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.particle_real_scale_input.v1":
        raise ValueError("unexpected Particle real-scale manifest")
    arrays: dict[str, np.ndarray] = {}
    for name, row in manifest["members"].items():
        path = root / name
        if not path.is_file() or path.stat().st_size != row["size_bytes"]:
            raise RuntimeError(f"Particle input member size differs: {name}")
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"Particle input member differs: {name}")
        value = np.load(path, allow_pickle=False)
        if list(value.shape) != row["shape"] or str(value.dtype) != row["dtype"]:
            raise RuntimeError(f"Particle array contract differs: {name}")
        arrays[name] = value
    return {
        "vertices": arrays["vertices_f32.npy"],
        "triangles": arrays["triangles_u32.npy"],
        "front_values": arrays["front_values_u32.npy"],
        "back_values": arrays["back_values_u32.npy"],
        "queries": arrays["queries_f32.npy"],
        "expected": arrays["expected_u32.npy"],
        "input_sha256": sha256(manifest_path),
        "manifest": manifest,
    }


def write_new(path: Path, body: bytes) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    return {
        "path": str(path.resolve()),
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }


def json_bytes(value: object) -> bytes:
    return (json.dumps(
        value, sort_keys=True, indent=2, allow_nan=False,
    ) + "\n").encode("utf-8")


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def formal_rtdl_identities(archive: Path) -> dict[str, list[str]]:
    programs: list[str] = []
    executables: list[str] = []
    with tarfile.open(archive, "r:gz") as source:
        names = sorted(
            name for name in source.getnames()
            if name.endswith("/STDOUT.bin") and "FORMAL_TRANSACTION/workers/" in name
        )
        for name in names:
            member = source.extractfile(name)
            if member is None:
                raise RuntimeError(f"archive member unavailable: {name}")
            row = json.loads(member.read())
            if row.get("arm") != "rtdl":
                continue
            metadata = row["metadata"]
            programs.append(metadata["program_identity_sha256"])
            executables.append(metadata["executable_identity_sha256"])
    if len(programs) != 8 or len(set(programs)) != 1 or len(set(executables)) != 1:
        raise RuntimeError("formal RTDL executable identities are not one 8-worker set")
    return {"program": programs, "executable": executables}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--base-particle-dir", type=Path, required=True)
    parser.add_argument("--ensemble-dir", type=Path, required=True)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--save-observed-output", type=Path)
    parser.add_argument("--data-preflight-only", action="store_true")
    parser.add_argument("--compute-capability", default="8.9")
    parser.add_argument("--optix-sdk", default="8.0.0")
    args = parser.parse_args()

    source_root = args.source_root.resolve(strict=True)
    if git(source_root, "status", "--porcelain"):
        raise RuntimeError("reconstruction requires a clean source tree")
    source_commit = git(source_root, "rev-parse", "HEAD")
    source_tree = git(source_root, "rev-parse", "HEAD^{tree}")
    if source_commit != "110dee7aa11e57e984cc2509163e021d787c692a":
        raise RuntimeError(f"unexpected reconstruction source: {source_commit}")

    formal = formal_rtdl_identities(args.archive.resolve(strict=True))
    base_root = args.base_particle_dir.resolve(strict=True)
    base = load_particle_directory(base_root)
    ensemble_root = args.ensemble_dir.resolve(strict=True)
    ensemble_manifest_path = ensemble_root / "MANIFEST.json"
    ensemble = json.loads(ensemble_manifest_path.read_text(encoding="utf-8"))
    if ensemble.get("schema") != "rtdl.v4.authored_particle.transition_ensemble.v1":
        raise RuntimeError("unexpected transition-ensemble manifest")
    if ensemble["base_particle"]["manifest_sha256"] != base["input_sha256"]:
        raise RuntimeError("base Particle manifest differs from ensemble binding")
    ensemble_arrays: dict[str, np.ndarray] = {}
    for name, row in ensemble["members"].items():
        path = ensemble_root / name
        if not path.is_file() or path.stat().st_size != row["bytes"]:
            raise RuntimeError(f"ensemble member size differs: {name}")
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"ensemble member differs: {name}")
        value = np.load(path, mmap_mode="r", allow_pickle=False)
        if list(value.shape) != row["shape"] or str(value.dtype) != row["dtype"]:
            raise RuntimeError(f"ensemble array contract differs: {name}")
        ensemble_arrays[name] = value
    queries = ensemble_arrays["queries_f32.npy"]
    expected_source = ensemble_arrays["expected_u32.npy"]
    query_count = int(ensemble["queries"]["count"])
    if query_count != 160_000_000 or queries.shape != (query_count, 7):
        raise RuntimeError("reconstruction ensemble shape differs")
    if expected_source.shape != (query_count, 3):
        raise RuntimeError("reconstruction oracle shape differs")
    preflight = {
        "schema": "rtdl.v4.authored_particle.durable_data_path_preflight.v1",
        "status": "PASS__DURABLE_DIRECT_DIRECTORY_CONTRACT",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "base_particle_dir": str(base_root),
        "base_manifest_sha256": base["input_sha256"],
        "base_triangle_shape": list(base["triangles"].shape),
        "base_vertex_shape": list(base["vertices"].shape),
        "ensemble_dir": str(ensemble_root),
        "ensemble_manifest_sha256": sha256(ensemble_manifest_path),
        "query_shape": list(queries.shape),
        "expected_shape": list(expected_source.shape),
        "formal_program_identity_sha256": formal["program"][0],
        "formal_executable_identity_sha256": formal["executable"][0],
        "gpu_execution_performed": False,
    }
    if args.data_preflight_only:
        print(json.dumps(preflight, sort_keys=True, allow_nan=False))
        return 0
    for name in ("native", "optix_include", "cuda_include", "output"):
        if getattr(args, name) is None:
            raise RuntimeError(f"--{name.replace('_', '-')} is required for replay")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    artifacts = output / "compiler_artifacts"
    artifacts.mkdir()
    expected = face_first_expected(expected_source)
    oracle_sha256 = hashlib.sha256(json.dumps({
        "ensemble_construction": ensemble["queries"]["construction"],
        "ensemble_expected_sha256": ensemble["members"]["expected_u32.npy"]["sha256"],
        "query_count": query_count,
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    verified = v4.verify_builtin_triangle_callback_source(
        FACE_FIRST_SOURCE, face_first_manifest())
    physical_plan = build_face_first_physical_plan(
        verified, independent_cpu_oracle_sha256=oracle_sha256)
    capability = tuple(int(item) for item in args.compute_capability.split("."))
    target = v4.V4Target.from_native(
        args.native.resolve(strict=True), optix_sdk=args.optix_sdk,
        compute_capability=capability,
        supports_custom_aabb=True, supports_builtin_triangle=True,
    )
    toolchain = v4.V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
    )
    program = verified.compile(physical_plan=physical_plan, target=target)
    materialized = program.materialize(toolchain=toolchain)
    executable = materialized._executable

    members: list[dict[str, object]] = []
    payloads: dict[str, bytes] = {
        "callback_source.py": FACE_FIRST_SOURCE.encode("utf-8"),
        "wrapper.cu": executable.wrapper.source.encode("utf-8"),
        "wrapper.ptx": executable.wrapper_ptx.encode("utf-8"),
        "composed.ptx": executable.composed.ptx.encode("utf-8"),
        "compiler_options.json": json_bytes(list(executable.compiler_options)),
    }
    for index, leaf in enumerate(executable.generated_leaves):
        payloads[f"leaf_{index}_{leaf.role.value}.py"] = leaf.generated_source.encode("utf-8")
    for index, leaf in enumerate(executable.compiled_leaves):
        payloads[f"leaf_{index}_{leaf.role}.ptx"] = leaf.ptx.encode("utf-8")
    for name, body in sorted(payloads.items()):
        row = write_new(artifacts / name, body)
        row["name"] = name
        members.append(row)

    reconstructed_program = program.identity.identity_sha256
    reconstructed_executable = materialized.identity.identity_sha256
    if reconstructed_program != formal["program"][0]:
        raise RuntimeError("reconstructed program identity differs from formal workers")
    if reconstructed_executable != formal["executable"][0]:
        raise RuntimeError("reconstructed executable identity differs from formal workers")

    static = v4.BuiltinTriangleCallbackStaticInput(
        vertices=base["vertices"], triangles=base["triangles"],
        first_primitive_values=base["front_values"],
        second_primitive_values=base["back_values"],
    )
    owner = materialized.prepare(static)
    try:
        prepared = owner.prepare_batch(
            v4.BuiltinTriangleCallbackBatch(queries=queries))
        result = owner.execute(prepared)
        observed = np.asarray(result.output, dtype=np.uint32)
        observed_sha256 = digest_array(observed)
        expected_sha256 = digest_array(expected)
        if observed.shape != expected.shape or observed_sha256 != expected_sha256:
            raise RuntimeError("post-formal replay output differs from independent oracle")
        observed_output_binding = None
        if args.save_observed_output is not None:
            observed_output = args.save_observed_output.resolve()
            observed_output.parent.mkdir(parents=True, exist_ok=True)
            with observed_output.open("xb") as stream:
                np.save(stream, observed, allow_pickle=False)
                stream.flush()
                os.fsync(stream.fileno())
            observed_output_binding = {
                "path": str(observed_output),
                "bytes": observed_output.stat().st_size,
                "sha256": sha256(observed_output),
                "array_digest": observed_sha256,
            }
        receipt = dict(result.traversal_receipt)
        lifecycle = owner.lifecycle_receipt
        execution = {
            "schema": "rtdl.v4.authored_particle.postformal_reconstruction_execution.v1",
            "status": "PASS__POSTFORMAL_REPLAY_NOT_ORIGINAL_TIMED_WORKER_BYTES",
            "source_commit": source_commit,
            "source_tree": source_tree,
            "query_count": query_count,
            "output_shape": list(observed.shape),
            "output_sha256": observed_sha256,
            "expected_output_sha256": expected_sha256,
            "role_counters": list(result.role_counters),
            "launch_status": list(result.launch_status),
            "traversal_receipt": receipt,
            "lifecycle_receipt_before_close": lifecycle,
            "program_identity_sha256": reconstructed_program,
            "executable_identity": asdict(result.executable_identity),
            "executable_identity_sha256": reconstructed_executable,
            "protocol_contract_decision": (
                asdict(result.protocol_contract_decision)
                if is_dataclass(result.protocol_contract_decision)
                else str(result.protocol_contract_decision)
            ),
            "saved_observed_output": observed_output_binding,
        }
        execution_binding = write_new(output / "REPLAY_EXECUTION.json", json_bytes(execution))
    finally:
        owner.close()

    data_members = []
    for name in ("MANIFEST.json", "queries_f32.npy", "query_cells_u32.npy", "expected_u32.npy"):
        path = ensemble_root / name
        data_members.append({
            "name": name,
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "schema": "rtdl.v4.authored_particle.postformal_reconstruction.v1",
        "status": "PASS__IDENTITY_MATCHED_POSTFORMAL_RECONSTRUCTION",
        "claim_boundary": {
            "original_formal_generated_bytes_retained": False,
            "original_formal_full_receipt_retained": False,
            "postformal_same_source_toolchain_reconstruction": True,
            "postformal_replay_not_pooled_with_formal_timings": True,
        },
        "source_commit": source_commit,
        "source_tree": source_tree,
        "formal_archive": {
            "path": str(args.archive.resolve(strict=True)),
            "bytes": args.archive.stat().st_size,
            "sha256": sha256(args.archive),
        },
        "formal_worker_identity_count": 8,
        "formal_program_identity_sha256": formal["program"][0],
        "formal_executable_identity_sha256": formal["executable"][0],
        "reconstructed_program_identity_sha256": reconstructed_program,
        "reconstructed_executable_identity_sha256": reconstructed_executable,
        "compiler_artifact_members": members,
        "replay_execution": execution_binding,
        "resident_data_members": data_members,
        "saved_observed_output": observed_output_binding,
    }
    write_new(output / "MANIFEST.json", json_bytes(manifest))
    print(json.dumps(manifest, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
