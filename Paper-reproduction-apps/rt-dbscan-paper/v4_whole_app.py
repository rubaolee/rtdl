"""Application-owned V4 complete endpoint for bounded RT-DBSCAN."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from dataclasses import dataclass

import numpy as np

from rtdsl.v4_multiround_spatial import RadiusGraphComponentsRequest
from rtdsl.v4_multiround_spatial_optix_compiler import (
    compile_verified_multiround_spatial_executable,
)
from rtdsl.v4_multiround_spatial_optix_runtime import (
    execute_radius_graph_components,
    prepare_multiround_spatial_callback,
)
from rtdsl.v4_radius_graph_grouped_lowering import (
    prepare_verified_radius_graph_grouped_v4,
)
from rtdsl.v4_multiround_spatial_standard_library import (
    compile_standard_multiround_authority,
)


APP_DIR = Path(__file__).resolve().parent
MIGRATION = APP_DIR / "rtdl3_action_migration.py"
FIXTURE = APP_DIR / "data/fixtures/border_noise3d_component_signature.csv"


def _load_app():
    name = "rtdl_v4_rt_dbscan_app_adapter"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MIGRATION)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen RT-DBSCAN adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_real_scale_v4_input(root: str | Path) -> dict[str, object]:
    """Load the route-independent public 4,096-point clustered3d packet."""

    root = Path(root).resolve()
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.rtdbscan_real_scale_input.v1":
        raise ValueError("unexpected RT-DBSCAN real-scale manifest")
    arrays: dict[str, np.ndarray] = {}
    for name, row in manifest["members"].items():
        path = root / name
        if not path.is_file() or _file_sha256(path) != row["sha256"]:
            raise RuntimeError(f"RT-DBSCAN real-scale member mismatch: {name}")
        value = np.load(path, allow_pickle=False)
        if list(value.shape) != row["shape"] or str(value.dtype) != row["dtype"]:
            raise RuntimeError(
                f"RT-DBSCAN real-scale array contract mismatch: {name}")
        arrays[name] = value
    contract = manifest["contract"]
    points = np.ascontiguousarray(arrays["points_f32.npy"], dtype=np.float32)
    if int(points.shape[0]) != int(contract["point_count"]):
        raise RuntimeError("RT-DBSCAN real-scale point-count mismatch")
    expected = {
        "canonical_component_labels": tuple(
            map(int, arrays["canonical_component_labels_i32.npy"])),
        "core_flags": tuple(
            bool(value) for value in arrays["core_flags_u8.npy"]),
        "neighbor_counts": tuple(
            map(int, arrays["neighbor_counts_u32.npy"])),
    }
    return {
        "points": points,
        "expected": expected,
        "input_sha256": _file_sha256(manifest_path),
        "epsilon": float(contract["epsilon"]),
        "min_points": int(contract["min_points"]),
        "directed_edge_count": int(manifest["oracle"]["directed_edge_count"]),
        "route_independent_expected": True,
        "real_scale_manifest": manifest,
    }


def build_v4_input():
    app = _load_app()
    points = np.loadtxt(FIXTURE, delimiter=",", comments="#", dtype=np.float32)
    expected = app._expected_from_points(points, epsilon=0.35, min_points=5)
    return {
        "points": points,
        "expected": {
            "canonical_component_labels": expected["canonical_component_labels"],
            "core_flags": expected["core_flags"],
            "neighbor_counts": expected["neighbor_counts"],
        },
        "input_sha256": _digest({
            "points": points.tolist(), "epsilon": 0.35, "min_points": 5,
        }),
    }


def _canonicalize_spatial_points_3d(points) -> np.ndarray:
    """Apply RT-DBSCAN's explicit Nx2-to-XYZ zero-z input contract."""

    point_values = np.ascontiguousarray(points, dtype=np.float32)
    if point_values.ndim != 2 or point_values.shape[1] not in (2, 3) \
            or not len(point_values) or not np.isfinite(point_values).all():
        raise ValueError(
            "finite non-empty float32 [N,2] or [N,3] points are required")
    if point_values.shape[1] == 2:
        point_values = np.ascontiguousarray(np.column_stack((
            point_values, np.zeros((len(point_values),), dtype=np.float32)
        )), dtype=np.float32)
    return point_values


@dataclass
class PreparedRtDbscanV4:
    """Application-facing owner for repeated clustering parameter requests."""

    owner: object
    points: np.ndarray
    app: object
    total_prepare_seconds: float
    frozen_expected: dict[str, object] | None = None
    frozen_input_sha256: str | None = None
    frozen_epsilon: float | None = None
    frozen_min_points: int | None = None

    def execute(
        self, *, epsilon: float = 0.35, min_points: int = 5,
    ) -> dict[str, object]:
        started = time.perf_counter()
        if hasattr(self.owner, "execute_components"):
            result = self.owner.execute_components(
                epsilon=epsilon, min_points=min_points)
        else:  # Compatibility for injected contract-test owners only.
            result = execute_radius_graph_components(
                self.owner,
                RadiusGraphComponentsRequest(
                    epsilon=epsilon, min_points=min_points))
        actual = {
            "canonical_component_labels": result.value[
                "canonical_component_labels"],
            "core_flags": result.value["core_flags"],
            "neighbor_counts": result.value["neighbor_counts"],
        }
        elapsed = time.perf_counter() - started
        # Correctness-oracle work belongs outside the prepared endpoint timer.
        if self.frozen_expected is not None:
            if (
                self.frozen_epsilon is None
                or self.frozen_min_points is None
                or np.float32(epsilon) != np.float32(self.frozen_epsilon)
                or int(min_points) != int(self.frozen_min_points)
            ):
                raise ValueError(
                    "frozen RT-DBSCAN oracle is valid only for its exact parameters")
            expected = self.frozen_expected
            input_sha256 = self.frozen_input_sha256
        else:
            expected_full = self.app._expected_from_points(
                self.points, epsilon=epsilon, min_points=min_points)
            expected = {
                "canonical_component_labels": expected_full[
                    "canonical_component_labels"],
                "core_flags": expected_full["core_flags"],
                "neighbor_counts": expected_full["neighbor_counts"],
            }
            input_sha256 = _digest({
                "points": self.points.tolist(), "epsilon": epsilon,
                "min_points": min_points,
            })
        return {
            "schema": "rtdl.paper_reproduction.rt_dbscan.v4.prepared.v2",
            "input_sha256": input_sha256,
            "output": actual,
            "expected": expected,
            "matched": actual == expected,
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False,
            "cold_result_replaced": False,
            "lifecycle_receipt": self.owner.lifecycle_receipt,
            "traversal_receipt": result.traversal_receipt,
            "native_library_sha256": result.native_library_sha256,
            "point_count_at_most_4096": len(self.points) <= 4096,
            "route_independent_expected": self.frozen_expected is not None,
        }

    def close(self) -> None:
        self.owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_v4(
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path,
    points=None,
    initial_radius: float = 0.35,
    frozen_expected: dict[str, object] | None = None,
    frozen_input_sha256: str | None = None,
    frozen_epsilon: float | None = None,
    frozen_min_points: int | None = None,
    maximum_event_capacity: int = 4096,
) -> PreparedRtDbscanV4:
    """Compile/verify once and prepare reusable fixed geometry."""

    started = time.perf_counter()
    data = build_v4_input()
    point_values = _canonicalize_spatial_points_3d(
        data["points"] if points is None else points)
    # The capacity is a pre-launch semantic/resource contract.  It is never a
    # truncation limit: an undersized declaration still rejects the complete
    # result rather than accepting a prefix.
    authority, proof = compile_standard_multiround_authority(
        target, capacity=maximum_event_capacity)
    executable, _ = compile_verified_multiround_spatial_executable(
        authority,
        any_hit_proof_authority=proof,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    owner = prepare_verified_radius_graph_grouped_v4(
        authority, executable,
        any_hit_proof_authority=proof,
        points=point_values,
        radius=initial_radius,
        native_library_path=native_library_path,
        boundary_assignment_policy="lowest_component_root_two_pass",
    )
    return PreparedRtDbscanV4(
        owner=owner,
        points=point_values,
        app=_load_app(),
        total_prepare_seconds=time.perf_counter() - started,
        frozen_expected=frozen_expected,
        frozen_input_sha256=frozen_input_sha256,
        frozen_epsilon=frozen_epsilon,
        frozen_min_points=frozen_min_points,
    )


def run_v4_complete(
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path,
):
    started = time.perf_counter()
    data = build_v4_input()
    authority, proof = compile_standard_multiround_authority(target)
    executable, _ = compile_verified_multiround_spatial_executable(
        authority,
        any_hit_proof_authority=proof,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    with prepare_multiround_spatial_callback(
        authority, executable,
        any_hit_proof_authority=proof,
        search_points=data["points"],
        initial_radius=0.35,
        native_library_path=native_library_path,
    ) as owner:
        result = execute_radius_graph_components(
            owner, RadiusGraphComponentsRequest(epsilon=0.35, min_points=5))
    actual = {
        "canonical_component_labels": result.value[
            "canonical_component_labels"],
        "core_flags": result.value["core_flags"],
        "neighbor_counts": result.value["neighbor_counts"],
    }
    elapsed = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.rt_dbscan.v4.v2",
        "input_sha256": data["input_sha256"],
        "output": actual,
        "expected": data["expected"],
        "matched": actual == data["expected"],
        "registered_complete_seconds": elapsed,
        "complete_timer_includes": (
            "csv_input_load", "app_parameter_binding",
            "restricted_callback_parse_verify", "abi_and_wrapper_compile",
            "persistent_gas_prepare", "bounded_radius_optix_execute",
            "exact_radius_graph_and_component_materialization",
        ),
        "traversal_receipt": result.traversal_receipt,
        "native_library_sha256": result.traversal_receipt[
            "provider_library_sha256"],
        "point_count_at_most_4096": len(data["points"]) <= 4096,
        "default_selected_between_paper_algorithms": False,
    }


__all__ = [
    "PreparedRtDbscanV4", "build_v4_input", "load_real_scale_v4_input",
    "prepare_v4", "run_v4_complete",
]
