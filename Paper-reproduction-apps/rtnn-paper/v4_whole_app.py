"""Application-owned V4 complete endpoint for the frozen RTNN KNN lane."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from dataclasses import dataclass

import numpy as np

from rtdsl.v4_multiround_spatial import (
    DistanceWindowBoundaryPolicy,
    RankedDistanceWindowRequest,
)
from rtdsl.v4_multiround_spatial_optix_compiler import (
    compile_verified_multiround_spatial_executable,
)
from rtdsl.v4_multiround_spatial_optix_runtime import (
    execute_ranked_distance_window,
    prepare_multiround_spatial_callback,
)
from rtdsl.v4_multiround_spatial_standard_library import (
    compile_standard_multiround_authority,
)
from rtdsl.v4_ranked_distance_window_lowering import (
    prepare_verified_ranked_distance_window_v4,
)


APP_DIR = Path(__file__).resolve().parent
MIGRATION = APP_DIR / "rtdl3_action_migration.py"
FIXTURE = APP_DIR / "data/fixtures/goal5531_exact_knn"


def _load_app():
    name = "rtdl_v4_rtnn_app_adapter"
    if name in sys.modules:
        return sys.modules[name]
    sys.path.insert(0, str(APP_DIR))
    try:
        spec = importlib.util.spec_from_file_location(name, MIGRATION)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load frozen RTNN adapter")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(APP_DIR))


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


def _array_sha256(value) -> str:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def _paper_rows_match(actual, expected, *, distance_abs_tolerance: float = 1e-6) -> bool:
    """RTNN contract: exact query/item/rank, bounded float32 distance drift."""

    return len(actual) == len(expected) and all(
        tuple(left[:3]) == tuple(right[:3])
        and math.isclose(
            float(left[3]), float(right[3]),
            rel_tol=0.0, abs_tol=distance_abs_tolerance)
        for left, right in zip(actual, expected, strict=True)
    )


def load_real_scale_v4_input(root: str | Path):
    """Load the frozen 12M-search / 4096-query Goal5776 packet."""

    root = Path(root).resolve()
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.rtnn_real_scale_input.v1":
        raise ValueError("unexpected RTNN real-scale manifest")
    arrays = {}
    for name, row in manifest["members"].items():
        path = root / name
        if not path.is_file() or _file_sha256(path) != row["sha256"]:
            raise RuntimeError(f"RTNN real-scale member mismatch: {name}")
        value = np.load(path, allow_pickle=False)
        if list(value.shape) != row["shape"] or str(value.dtype) != row["dtype"]:
            raise RuntimeError(f"RTNN real-scale array contract mismatch: {name}")
        arrays[name] = value
    expected = tuple(zip(
        map(int, arrays["expected_query_u32.npy"]),
        map(int, arrays["expected_candidate_u32.npy"]),
        map(int, arrays["expected_rank_u32.npy"]),
        map(float, arrays["expected_distance_sq_f32.npy"]),
    ))
    contract = manifest["contract"]
    return {
        "search": np.ascontiguousarray(arrays["search_f32.npy"], dtype=np.float32),
        "queries": np.ascontiguousarray(arrays["queries_f32.npy"], dtype=np.float32),
        "expected": expected,
        "search_sha256": _array_sha256(arrays["search_f32.npy"]),
        "queries_sha256": _array_sha256(arrays["queries_f32.npy"]),
        "input_sha256": _file_sha256(manifest_path),
        "k": int(contract["k"]),
        "minimum_distance": float(contract["minimum_distance"]),
        "maximum_distance": float(contract["maximum_distance"]),
        "initial_radius": float(contract["maximum_distance"]) / 8.0,
        "maximum_rounds": 4,
        "route_independent_expected": True,
        "real_scale_manifest": manifest,
    }


def build_v4_input():
    app = _load_app()
    search = np.asarray(app._load_xyz(FIXTURE / "search.xyz"), dtype=np.float32)
    queries = np.asarray(app._load_xyz(FIXTURE / "queries.xyz"), dtype=np.float32)
    expected = app._expected_for_points(
        search, queries, k=4, min_distance=0.0, max_distance=3.0)
    return {
        "search": search,
        "queries": queries,
        "expected": expected,
        "input_sha256": _digest({
            "search": search.tolist(), "queries": queries.tolist(),
            "k": 4, "minimum_distance": 0.0, "maximum_distance": 3.0,
        }),
    }


@dataclass
class PreparedRtnnV4:
    """Application-facing owner for repeated KNN query batches."""

    owner: object
    search: np.ndarray
    app: object
    total_prepare_seconds: float
    search_sha256: str = ""
    frozen_query_sha256: str | None = None
    frozen_expected: tuple[tuple[int, int, int, float], ...] | None = None
    prepared_initial_radius: float = 0.375
    prepared_maximum_rounds: int = 4

    def execute(
        self,
        queries,
        *,
        k: int = 4,
        minimum_distance: float = 0.0,
        maximum_distance: float = 3.0,
        initial_radius: float | None = None,
        maximum_rounds: int | None = None,
    ) -> dict[str, object]:
        started = time.perf_counter()
        query_values = np.ascontiguousarray(queries, dtype=np.float32)
        selected_initial_radius = (
            self.prepared_initial_radius
            if initial_radius is None else float(initial_radius)
        )
        selected_maximum_rounds = (
            self.prepared_maximum_rounds
            if maximum_rounds is None else int(maximum_rounds)
        )
        if hasattr(self.owner, "execute_ranked"):
            result = self.owner.execute_ranked(
                query_values, k=k, minimum_distance=minimum_distance,
                maximum_distance=maximum_distance,
                initial_radius=selected_initial_radius,
                maximum_rounds=selected_maximum_rounds,
            )
            relation = self.app._relation_rows_from_rows(result.rows)
            actual = self.app._canonical_rows(relation)
        else:  # Compatibility for injected contract-test owners only.
            result = execute_ranked_distance_window(
                self.owner, query_values,
                RankedDistanceWindowRequest(
                    k=k, minimum_distance=minimum_distance,
                    maximum_distance=maximum_distance,
                    initial_radius=selected_initial_radius,
                    maximum_rounds=selected_maximum_rounds,
                    boundary_policy=DistanceWindowBoundaryPolicy.OPEN,
                ))
            actual = result.value
        elapsed = time.perf_counter() - started
        # Correctness-oracle work belongs outside the prepared endpoint timer.
        query_sha256 = _array_sha256(query_values)
        if (
            self.frozen_expected is not None
            and query_sha256 == self.frozen_query_sha256
            and int(k) == 4
            and float(minimum_distance) == 0.0
            and float(maximum_distance) == 2.0
        ):
            expected = self.frozen_expected
        else:
            expected = self.app._expected_for_points(
                self.search, query_values, k=k,
                min_distance=minimum_distance, max_distance=maximum_distance)
        return {
            "schema": "rtdl.paper_reproduction.rtnn.v4.prepared.v1",
            "input_sha256": _digest({
                "search_sha256": self.search_sha256 or _array_sha256(self.search),
                "queries_sha256": query_sha256,
                "k": k, "minimum_distance": minimum_distance,
                "maximum_distance": maximum_distance,
            }),
            "output": actual,
            "expected": expected,
            "matched": _paper_rows_match(actual, expected),
            "identity_rows_exact": (
                tuple(row[:3] for row in actual)
                == tuple(row[:3] for row in expected)),
            "distance_sq_abs_tolerance": 1e-6,
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False,
            "cold_result_replaced": False,
            "lifecycle_receipt": self.owner.lifecycle_receipt,
            "traversal_receipt": result.traversal_receipt,
            "native_library_sha256": result.native_library_sha256,
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
    search_points=None, prepared_input=None,
    initial_radius: float | None = None,
) -> PreparedRtnnV4:
    """Compile/verify once and prepare one explicit reusable search owner."""

    started = time.perf_counter()
    if prepared_input is not None and search_points is not None:
        raise ValueError("provide prepared_input or search_points, not both")
    if prepared_input is not None:
        data = prepared_input
        search = np.ascontiguousarray(data["search"], dtype=np.float32)
        selected_initial_radius = float(
            data["initial_radius"] if initial_radius is None else initial_radius
        )
        frozen_query_sha256 = str(data["queries_sha256"])
        frozen_expected = tuple(data["expected"])
    elif search_points is not None:
        data = None
        search = np.ascontiguousarray(search_points, dtype=np.float32)
        selected_initial_radius = 0.375 if initial_radius is None else float(initial_radius)
        frozen_query_sha256 = None
        frozen_expected = None
    else:
        data = build_v4_input()
        search = np.ascontiguousarray(data["search"], dtype=np.float32)
        selected_initial_radius = 0.375 if initial_radius is None else float(initial_radius)
        frozen_query_sha256 = None
        frozen_expected = None
    # The built-in paper fixture predates the real-scale prepared-input
    # envelope and therefore carries neither ``k`` nor
    # ``maximum_distance``.  Both are paper-route constants for that fixture;
    # prepared inputs may override them explicitly.  Do not make the default
    # public front door depend on optional envelope-only keys.
    intended_capacity = (
        len(data["queries"]) * int(data.get("k", 4))
        if data is not None else 4096
    )
    maximum_distance_bound = (
        float(data.get("maximum_distance", 3.0)) if data is not None else 3.0
    )
    authority, proof = compile_standard_multiround_authority(
        target, capacity=intended_capacity)
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
    owner = prepare_verified_ranked_distance_window_v4(
        authority, executable,
        any_hit_proof_authority=proof,
        search_points=search,
        maximum_distance_bound=maximum_distance_bound,
        native_library_path=native_library_path,
    )
    return PreparedRtnnV4(
        owner=owner,
        search=search,
        app=_load_app(),
        total_prepare_seconds=time.perf_counter() - started,
        search_sha256=_array_sha256(search),
        frozen_query_sha256=frozen_query_sha256,
        frozen_expected=frozen_expected,
        prepared_initial_radius=selected_initial_radius,
        prepared_maximum_rounds=(
            int(data.get("maximum_rounds", 4)) if data is not None else 4
        ),
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
        search_points=data["search"],
        initial_radius=0.375,
        native_library_path=native_library_path,
    ) as owner:
        result = execute_ranked_distance_window(
            owner,
            data["queries"],
            RankedDistanceWindowRequest(
                k=4, minimum_distance=0.0, maximum_distance=3.0,
                initial_radius=0.375, maximum_rounds=4,
                boundary_policy=DistanceWindowBoundaryPolicy.OPEN,
            ),
        )
    elapsed = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.rtnn.v4.v1",
        "input_sha256": data["input_sha256"],
        "output": result.value,
        "expected": data["expected"],
        "matched": result.value == data["expected"],
        "registered_complete_seconds": elapsed,
        "complete_timer_includes": (
            "xyz_input_load", "app_parameter_binding",
            "restricted_callback_parse_verify", "abi_and_wrapper_compile",
            "persistent_gas_prepare", "bounded_multiround_optix_execute",
            "exact_ranked_topk_materialization",
        ),
        "traversal_receipt": result.traversal_receipt,
        "native_library_sha256": result.traversal_receipt[
            "provider_library_sha256"],
        "default_selected_between_paper_algorithms": False,
    }


__all__ = [
    "PreparedRtnnV4", "build_v4_input", "load_real_scale_v4_input",
    "prepare_v4", "run_v4_complete",
]
