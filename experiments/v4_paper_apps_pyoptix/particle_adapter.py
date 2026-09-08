"""Symmetric full-public adapters for the Particle paper-application row."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np

from experiments.goal5814_particle.public_pyoptix_owner import (
    FORMAL_PARTICLE_SHAPE,
    ParticleExecutionResult,
    prepare_formal_particle_owner,
)

from .public_runtime import compile_ptx, load_runtime

DEVICE_SOURCE = Path(__file__).with_name("particle_device.cu")


def _output_digest(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value, dtype=np.uint32)
    digest = hashlib.sha256()
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(str(tuple(array.shape)).encode("ascii"))
    digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def validate_particle_app_input(data: Mapping[str, Any]) -> dict[str, np.ndarray]:
    required = {
        "vertices",
        "triangles",
        "front_values",
        "back_values",
        "queries",
        "expected",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(f"Particle app input lacks: {', '.join(missing)}")
    result = {
        "vertices": np.ascontiguousarray(data["vertices"], dtype=np.float32),
        "triangles": np.ascontiguousarray(data["triangles"], dtype=np.uint32),
        "front_values": np.ascontiguousarray(data["front_values"], dtype=np.uint32),
        "back_values": np.ascontiguousarray(data["back_values"], dtype=np.uint32),
        "queries": np.ascontiguousarray(data["queries"], dtype=np.float32),
        "expected": np.ascontiguousarray(data["expected"], dtype=np.uint32),
    }
    shape = FORMAL_PARTICLE_SHAPE
    expected_shapes = {
        "vertices": (shape.vertex_count, 3),
        "triangles": (shape.triangle_count, 3),
        "front_values": (shape.triangle_count,),
        "back_values": (shape.triangle_count,),
        "queries": (shape.query_count, 7),
        "expected": (shape.query_count, 3),
    }
    for name, expected_shape in expected_shapes.items():
        if result[name].shape != expected_shape:
            raise ValueError(
                f"Particle {name} shape differs: "
                f"expected={expected_shape} observed={result[name].shape}"
            )
    if not bool(np.isfinite(result["vertices"]).all()) or not bool(
        np.isfinite(result["queries"]).all()
    ):
        raise ValueError("Particle float columns contain nonfinite values")
    return result


def prepare_pyoptix_particle(data: Mapping[str, Any], *, prebuilt_ptx: bytes) -> Any:
    arrays = validate_particle_app_input(data)
    return prepare_formal_particle_owner(
        prebuilt_ptx=prebuilt_ptx,
        vertices=arrays["vertices"],
        triangles=arrays["triangles"],
        front_values=arrays["front_values"],
        back_values=arrays["back_values"],
    )


def compile_particle_ptx(
    *,
    optix_include: str | Path,
    cuda_include: str | Path,
    compute_capability: tuple[int, int],
) -> bytes:
    runtime = load_runtime()
    return compile_ptx(
        runtime,
        DEVICE_SOURCE,
        optix_include=optix_include,
        cuda_include=cuda_include,
        compute_capability=compute_capability,
    )


def _particle_dynamic_arrays(data: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    queries = np.ascontiguousarray(data["queries"], dtype=np.float32)
    expected = np.ascontiguousarray(data["expected"], dtype=np.uint32)
    shape = FORMAL_PARTICLE_SHAPE
    if queries.shape != (shape.query_count, 7) or expected.shape != (
        shape.query_count,
        3,
    ):
        raise ValueError("Particle dynamic query/oracle shape differs")
    return queries, expected


def execute_pyoptix_particle(owner: Any, data: Mapping[str, Any]) -> dict[str, Any]:
    """Execute, materialize, inspect, and hash the complete public result."""

    queries, expected = _particle_dynamic_arrays(data)
    result: ParticleExecutionResult = owner.execute_complete(
        *(np.ascontiguousarray(queries[:, index]) for index in range(7)),
        expected,
    )
    output = np.asarray(result.output, dtype=np.uint32)
    if output.shape != expected.shape or not np.array_equal(output, expected):
        raise RuntimeError("Particle PyOptiX full-public output mismatch")
    counters = {
        name: int(getattr(result.operation_counts, name))
        for name in result.operation_counts.__dataclass_fields__
    }
    return {
        "schema": "rtdl.v4_paper_apps_pyoptix.particle.v1",
        "output": output,
        "output_sha256": _output_digest(output),
        "control": tuple(int(value) for value in result.control),
        "operation_counts": counters,
        "matched": True,
        "public_output_materialized_inside_call": True,
        "full_50000_step_advection": False,
    }


def observe_v4_particle_result(
    result: Mapping[str, Any], expected: np.ndarray
) -> dict[str, Any]:
    """Force the same complete-output observation on the V4 public result."""

    output = np.asarray(result["output"], dtype=np.uint32)
    expected = np.asarray(expected, dtype=np.uint32)
    if (
        result.get("matched") is not True
        or output.shape != expected.shape
        or not np.array_equal(output, expected)
    ):
        raise RuntimeError("Particle V4 full-public output mismatch")
    receipt = result.get("traversal_receipt")
    if not isinstance(receipt, Mapping):
        raise RuntimeError(  # noqa: TRY004 - malformed runtime output, not caller input
            "Particle V4 public result lacks traversal receipt"
        )
    output_sha256 = result.get("output_sha256")
    if (
        type(output_sha256) is not str
        or len(output_sha256) != 64
        or any(character not in "0123456789abcdef" for character in output_sha256)
        or receipt.get("output_digest") != output_sha256
    ):
        raise RuntimeError("Particle V4 output identity is not receipt-bound")
    return {
        "schema": "rtdl.v4_paper_apps_pyoptix.particle_v4_observation.v1",
        "output": output,
        "output_sha256": output_sha256,
        "matched": True,
        "traversal_receipt": dict(receipt),
        "lifecycle_receipt": dict(result.get("lifecycle_receipt", {})),
        "public_output_materialized_inside_call": True,
        "full_50000_step_advection": False,
    }


__all__ = [
    "DEVICE_SOURCE",
    "compile_particle_ptx",
    "execute_pyoptix_particle",
    "observe_v4_particle_result",
    "prepare_pyoptix_particle",
    "validate_particle_app_input",
]
