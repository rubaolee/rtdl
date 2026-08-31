#!/usr/bin/env python3
"""Regenerate the 17-case fixed-radius proof for one exact target native.

This is a functional target-materialization step.  It records no performance
timings and changes exactly one scientific source file: the compiler-owned
refinement registry.  The evidence JSON lives beside the prepared result and
is bound into that registry by SHA-256 and by the exact native identity.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import inspect
import io
import json
import os
from pathlib import Path
import platform
import pprint
import socket
import sys
import tarfile

import numpy as np


CASES = {
    "locked12": {"kind": "locked", "epsilon": 0.35, "min_points": 5},
    "endpoint_exact": {
        "kind": "explicit",
        "points": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        "epsilon": 1.0,
        "min_points": 2,
    },
    "endpoint_below": {
        "kind": "explicit",
        "points": (
            (0.0, 0.0, 0.0),
            (float(np.nextafter(np.float32(1.0), np.float32(0.0))), 0.0, 0.0),
        ),
        "epsilon": 1.0,
        "min_points": 2,
    },
    "endpoint_above": {
        "kind": "explicit",
        "points": (
            (0.0, 0.0, 0.0),
            (float(np.nextafter(np.float32(1.0), np.float32(2.0))), 0.0, 0.0),
        ),
        "epsilon": 1.0,
        "min_points": 2,
    },
    "duplicate_pair": {
        "kind": "explicit",
        "points": ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        "epsilon": 0.5,
        "min_points": 2,
    },
    **{
        f"grid{side}_{density}": {
            "kind": "grid",
            "side": side,
            "density": density,
            "epsilon": 1.01 if density == "sparse" else float(side) / 2.0,
            "min_points": 4,
        }
        for side in (3, 4, 6, 8, 10)
        for density in ("sparse", "dense")
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _load_migration(root: Path):
    path = root / "Paper-reproduction-apps/rt-dbscan-paper/rtdl3_action_migration.py"
    spec = importlib.util.spec_from_file_location("goal5769_rtdbscan_migration", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("RT-DBSCAN migration module is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _grid(side: int) -> np.ndarray:
    return np.asarray([
        (float(x), float(y), float(z))
        for x in range(side)
        for y in range(side)
        for z in range(side)
    ], dtype=np.float32)


def _cases(migration):
    rows = []
    for case_id, original in CASES.items():
        config = dict(original)
        if config["kind"] == "locked":
            points = migration._points()
        elif config["kind"] == "explicit":
            points = np.asarray(config["points"], dtype=np.float32)
        else:
            points = _grid(int(config["side"]))
        rows.append((case_id, np.ascontiguousarray(points, dtype=np.float32), {
            "epsilon": float(config["epsilon"]),
            "min_points": int(config["min_points"]),
            "tags": ["legacy_locked_case", "nx3"],
        }))
    radius = np.asarray((0x3CE20659,), dtype=np.uint32).view(np.float32)[0]
    second = np.asarray(
        (0xBCB4B2EA, 0xBC3A8C06, 0x3C455585), dtype=np.uint32,
    ).view(np.float32)
    rows.append((
        "float32_sqrt_rounding_counterexample",
        np.vstack((np.zeros((1, 3), dtype=np.float32), second[None, :])),
        {
            "epsilon": float(radius), "min_points": 2,
            "tags": ["rounding_counterexample", "sqrt_rounding_exclusion"],
        },
    ))
    rows.append((
        "nx2_zero_z_lift",
        np.asarray(((0.0, 0.0), (1.0, 0.0), (3.0, 0.0)), dtype=np.float32),
        {"epsilon": 1.0, "min_points": 2, "tags": ["nx2", "zero_z_lift"]},
    ))
    if len(rows) != 17:
        raise RuntimeError("fixed-radius evidence case cardinality changed")
    return rows


def _standalone_bruteforce_partition(
    points: np.ndarray,
    *,
    epsilon: float,
    min_points: int,
) -> dict[str, object]:
    """Independent float32 DBSCAN partition oracle for the Goal5628 gate."""

    resolved = np.asarray(points, dtype=np.float32)
    point_count = int(resolved.shape[0])
    epsilon32 = np.float32(epsilon)
    threshold_sq = np.multiply(epsilon32, epsilon32, dtype=np.float32)
    delta = np.subtract(
        resolved[:, None, :], resolved[None, :, :], dtype=np.float32
    )
    squared = np.multiply(delta, delta, dtype=np.float32)
    distance_sq = np.add(
        squared[:, :, 0], squared[:, :, 1], dtype=np.float32
    )
    if resolved.shape[1] == 3:
        distance_sq = np.add(
            distance_sq, squared[:, :, 2], dtype=np.float32
        )
    edge_mask = distance_sq <= threshold_sq
    neighbors = [
        np.flatnonzero(edge_mask[source_id]).astype(np.int64).tolist()
        for source_id in range(point_count)
    ]

    core_flags = tuple(len(row) >= int(min_points) for row in neighbors)
    parent = list(range(point_count))

    def find(item: int) -> int:
        root = item
        while parent[root] != root:
            root = parent[root]
        while parent[item] != item:
            following = parent[item]
            parent[item] = root
            item = following
        return root

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    for source_id, targets in enumerate(neighbors):
        if not core_flags[source_id]:
            continue
        for target_id in targets:
            if core_flags[target_id]:
                union(source_id, target_id)

    labels = [-1] * point_count
    for point_id, is_core in enumerate(core_flags):
        if is_core:
            labels[point_id] = find(point_id)
            continue
        candidate_roots = {
            find(target_id)
            for target_id in neighbors[point_id]
            if core_flags[target_id]
        }
        if candidate_roots:
            labels[point_id] = min(candidate_roots)

    label_map: dict[int, int] = {}
    canonical_labels = []
    for label in labels:
        if label < 0:
            canonical_labels.append(-1)
            continue
        if label not in label_map:
            label_map[label] = len(label_map)
        canonical_labels.append(label_map[label])
    return {
        "canonical_component_labels": canonical_labels,
        "core_flags": [bool(value) for value in core_flags],
    }


def _normalized_output(value: dict[str, object]) -> dict[str, object]:
    return {
        "canonical_component_labels": [
            int(item) for item in value["canonical_component_labels"]
        ],
        "core_flags": [bool(item) for item in value["core_flags"]],
    }


def _float32_hex(value: object) -> str:
    resolved = np.asarray((value,), dtype=np.float32).view(np.uint32)[0]
    return f"{int(resolved):08x}"


def _point_bits(points: np.ndarray) -> list[list[str]]:
    rows = np.ascontiguousarray(points, dtype=np.float32).view(np.uint32)
    return [[f"{int(value):08x}" for value in row] for row in rows]


def _source_files(root: Path):
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative.startswith("build/") or "/__pycache__/" in f"/{relative}/" \
                or relative.endswith(".pyc"):
            continue
        yield relative, path


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for relative, path in _source_files(root):
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha(path)))
    return digest.hexdigest()


def _deterministic_archive(root: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    stream = io.BytesIO()
    with gzip.GzipFile(fileobj=stream, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for relative, path in _source_files(root):
                data = path.read_bytes()
                info = tarfile.TarInfo(relative)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if relative.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(data))
    output.write_bytes(stream.getvalue())


def _registry_text(digest: str, capsule: dict[str, object]) -> str:
    return (
        '"""Target-generated fixed-radius evidence identity and proof capsule.\n\n'
        "Generated only after all 17 exact routes pass on the bound target native.\n"
        '"""\n\nfrom __future__ import annotations\n\n\n'
        f'TRUSTED_REFINEMENT_EVIDENCE_DIGEST: str | None = "{digest}"\n'
        "TRUSTED_REFINEMENT_EVIDENCE_CAPSULE: dict[str, object] | None = "
        + pprint.pformat(capsule, sort_dicts=True, width=88)
        + "\n\n\n__all__ = [\n"
        '    "TRUSTED_REFINEMENT_EVIDENCE_CAPSULE",\n'
        '    "TRUSTED_REFINEMENT_EVIDENCE_DIGEST",\n]\n'
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--execution-source-output", type=Path, required=True)
    parser.add_argument("--result-output", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    native = args.native.resolve(strict=True)
    for output in (args.evidence_output, args.execution_source_output, args.result_output):
        if output.exists():
            raise FileExistsError(output)
        output.parent.mkdir(parents=True, exist_ok=True)
    for candidate in (root, root / "src", root / "scripts"):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))

    from rtdsl.action_api import compile_action_source, detect_action_target_profile
    from rtdsl.fixed_radius_graph_compiler import (
        FIXED_RADIUS_GRAPH_DISTANCE_ARITHMETIC,
        FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
        FIXED_RADIUS_GRAPH_REFINEMENT_SCOPE,
        build_fixed_radius_graph_refinement_evidence_capsule,
        execute_fixed_radius_graph_refinement_evidence_routes,
        fixed_radius_graph_executable_identity_digests,
        validate_fixed_radius_graph_refinement_evidence_manifest,
    )

    if _sha(Path(os.environ.get("RTDL_OPTIX_LIB", ""))) != _sha(native):
        raise RuntimeError("target evidence native differs from active RTDL native")
    migration = _load_migration(root)
    compiled = compile_action_source(migration.ACTION_SOURCE, migration.action_contract())
    oracle_source = inspect.getsource(_standalone_bruteforce_partition).replace(
        "\r\n", "\n")
    oracle_digest = hashlib.sha256(oracle_source.encode()).hexdigest()
    expected_oracle = "7e52b42d1b2235110a9925540bbf59bea016261fc8bf64142a5a6d22b2ca53ea"
    if oracle_digest != expected_oracle:
        raise RuntimeError("independent fixed-radius oracle source drifted")
    source_identity = {
        "fixed_radius_graph_compiler_sha256": _sha(
            root / "src/rtdsl/fixed_radius_graph_compiler.py"),
        "evidence_generator_sha256": _sha(Path(__file__).resolve()),
        "crossover_oracle_module_sha256": _sha(Path(__file__).resolve()),
    }
    target = detect_action_target_profile(cpu_reference_available=False)
    rows = []
    native_identity = None
    last_capability = None
    compiler_source_sha256 = None
    for case_id, points, config in _cases(migration):
        expected = _standalone_bruteforce_partition(
            points, epsilon=config["epsilon"], min_points=config["min_points"])
        execution = execute_fixed_radius_graph_refinement_evidence_routes(
            compiled, target, points=points, radius=config["epsilon"],
            min_neighbors=config["min_points"], evidence_case_id=case_id,
            evidence_source_identity=source_identity)
        complete = _normalized_output(execution["complete_pair"]["actual"])
        spatial = _normalized_output(execution["prepared_spatial"]["actual"])
        if complete != expected or spatial != expected:
            raise RuntimeError(f"fixed-radius evidence mismatch: {case_id}")
        current_native = execution["native_library_identity"]
        current_compiler = execution["compiler_source_sha256"]
        if native_identity is None:
            native_identity = current_native
            compiler_source_sha256 = current_compiler
        elif current_native != native_identity or current_compiler != compiler_source_sha256:
            raise RuntimeError("fixed-radius evidence identity changed across cases")
        last_capability = execution["runtime_capability"]
        radius32 = np.float32(config["epsilon"])
        radius_sq32 = np.multiply(radius32, radius32, dtype=np.float32)
        rows.append({
            "case_id": case_id,
            "tags": list(config["tags"]),
            "input": {
                "dimension": int(points.shape[1]),
                "points_f32_hex": _point_bits(points),
                "radius_f32_hex": _float32_hex(radius32),
                "radius_sq_f32_hex": _float32_hex(radius_sq32),
                "min_neighbors": int(config["min_points"]),
            },
            "outputs": {
                "independent_oracle": expected,
                "complete_pair_candidate_enumeration.v1": complete,
                "prepared_spatial_radius_producer.v1": spatial,
            },
            "all_exact": True,
            "route_execution_metadata": {
                "complete_pair_candidate_enumeration.v1": execution["complete_pair"]["metadata"],
                "prepared_spatial_radius_producer.v1": execution["prepared_spatial"]["metadata"],
            },
            "execution_receipts": execution["execution_receipts"],
        })
    evidence = {
        "schema": "rtdl.fixed_radius_graph.refinement_evidence.v4",
        "status": "both_exact_executable_routes_match_independent_oracle",
        "semantic_digest": compiled.spec.semantic_digest,
        "logical_output_contract": FIXED_RADIUS_GRAPH_LOGICAL_OUTPUT_CONTRACT,
        "distance_arithmetic": FIXED_RADIUS_GRAPH_DISTANCE_ARITHMETIC,
        "refinement_scope": FIXED_RADIUS_GRAPH_REFINEMENT_SCOPE,
        "executable_identity_digests": fixed_radius_graph_executable_identity_digests(),
        "source_identity": source_identity,
        "native_library_identity": native_identity,
        "independent_oracle": {
            "symbol": "_standalone_bruteforce_partition",
            "normalized_source_sha256": oracle_digest,
            "normalization": "inspect.getsource_crlf_to_lf_utf8",
        },
        "cases": rows,
        "case_count": len(rows),
        "all_cases_exact": True,
        "functional_environment": {
            "hostname": socket.gethostname(), "platform": platform.platform(),
            "python": platform.python_version(), "numpy": np.__version__,
            "runtime_capability": last_capability,
        },
        "claim_boundary": {
            "functional_only": True, "real_gpu_routes_executed": True,
            "exclusive_gpu_claimed": False,
            "runtime_calibration_authorized": False,
            "recorded_worker_timings_discarded": True,
            "runtime_speedup_claimed": False,
        },
    }
    encoded = (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode()
    evidence_sha = hashlib.sha256(encoded).hexdigest()
    verified = validate_fixed_radius_graph_refinement_evidence_manifest(
        evidence, artifact_sha256=evidence_sha)
    capsule = build_fixed_radius_graph_refinement_evidence_capsule(verified)
    args.evidence_output.write_bytes(encoded)

    registry = root / "src/rtdsl/fixed_radius_graph_refinement_registry.py"
    before_registry_sha = _sha(registry)
    registry.write_text(_registry_text(evidence_sha, capsule), encoding="utf-8")
    after_registry_sha = _sha(registry)
    if before_registry_sha == after_registry_sha:
        raise RuntimeError("target evidence did not materialize a new registry")
    _deterministic_archive(root, args.execution_source_output)
    result = {
        "schema": "rtdl.goal5769.fixed_radius_target_rematerialization.v1",
        "source_root": str(root),
        "native_sha256": _sha(native),
        "evidence_sha256": evidence_sha,
        "case_count": 17,
        "all_cases_exact": True,
        "registry_before_sha256": before_registry_sha,
        "registry_after_sha256": after_registry_sha,
        "execution_source_sha256": _sha(args.execution_source_output),
        "execution_tree_sha256": _tree_digest(root),
        "source_delta": {
            "modified": ["src/rtdsl/fixed_radius_graph_refinement_registry.py"],
            "other_source_changes_allowed": False,
        },
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
    }
    args.result_output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
