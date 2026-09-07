"""Application-owned V4 complete endpoint for the frozen X-HD witness lane."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from dataclasses import dataclass

import numpy as np

from rtdsl.v4_exact_predicate_witness import (
    CandidateProducerKind,
    ExactPartnerAlgebra,
    ExactPredicateWitnessSchema,
    global_max_nearest_witness_f32,
    verify_exact_predicate_witness_schema,
)
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
from rtdsl.v4_global_nearest_witness_lowering import (
    prepare_verified_global_nearest_witness_v4,
)


APP_DIR = Path(__file__).resolve().parent
MIGRATION = APP_DIR / "rtdl3_action_migration.py"


def _load_app():
    name = "rtdl_v4_xhd_app_adapter"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MIGRATION)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen X-HD adapter")
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


def _array_sha256(value) -> str:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(memoryview(array).cast("B"))
    return digest.hexdigest()


def load_real_scale_v4_input(root: str | Path):
    """Load the frozen public Dragon -> HappyBuddha Goal5776 packet."""

    root = Path(root).resolve()
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "rtdl.goal5776.xhd_real_scale_input.v1":
        raise ValueError("unexpected X-HD real-scale manifest")
    arrays = {}
    for name, row in manifest["members"].items():
        path = root / name
        if not path.is_file() or _file_sha256(path) != row["sha256"]:
            raise RuntimeError(f"X-HD real-scale member mismatch: {name}")
        value = np.load(path, allow_pickle=False)
        if list(value.shape) != row["shape"] or str(value.dtype) != row["dtype"]:
            raise RuntimeError(f"X-HD real-scale array contract mismatch: {name}")
        arrays[name] = value
    expected_rows = tuple(zip(
        map(int, arrays["expected_query_u32.npy"]),
        map(int, arrays["expected_candidate_u32.npy"]),
        map(int, arrays["expected_rank_u32.npy"]),
        map(float, arrays["expected_distance_sq_f32.npy"]),
    ))
    expected = global_max_nearest_witness_f32(
        expected_rows,
        expected_query_ids=tuple(range(arrays["sources_f32.npy"].shape[0])),
    )
    contract = manifest["contract"]
    return {
        "sources": np.ascontiguousarray(arrays["sources_f32.npy"], dtype=np.float32),
        "targets": np.ascontiguousarray(arrays["targets_f32.npy"], dtype=np.float32),
        "expected": expected,
        "sources_sha256": _array_sha256(arrays["sources_f32.npy"]),
        "targets_sha256": _array_sha256(arrays["targets_f32.npy"]),
        "input_sha256": _file_sha256(manifest_path),
        "initial_radius": float(contract["initial_radius"]),
        "maximum_distance": float(contract["maximum_distance"]),
        "maximum_rounds": int(contract["maximum_rounds"]),
        "route_independent_expected": True,
        "real_scale_manifest": manifest,
    }


def _expected_for(sources: np.ndarray, targets: np.ndarray):
    all_pairs = []
    for query_id, query in enumerate(sources):
        candidates = []
        for item_id, item in enumerate(targets):
            delta = np.subtract(query, item, dtype=np.float32)
            squared = np.multiply(delta, delta, dtype=np.float32)
            d2 = np.add(np.add(squared[0], squared[1], dtype=np.float32),
                        squared[2], dtype=np.float32)
            candidates.append((float(d2), item_id))
        d2, item_id = min(candidates, key=lambda row: (row[0], row[1]))
        all_pairs.append((query_id, item_id, 1, d2))
    return global_max_nearest_witness_f32(
        all_pairs, expected_query_ids=tuple(range(len(sources))))


def build_v4_input():
    app = _load_app()
    sources2 = app._load_points(app.FIXTURE_DIR / "directed2d_asymmetric_a.wkt")
    targets2 = app._load_points(app.FIXTURE_DIR / "directed2d_asymmetric_b.wkt")
    sources = np.asarray([(x, y, 0.0) for x, y in sources2], dtype=np.float32)
    targets = np.asarray([(x, y, 0.0) for x, y in targets2], dtype=np.float32)
    expected = _expected_for(sources, targets)
    return {
        "sources": sources,
        "targets": targets,
        "expected": expected,
        "input_sha256": _digest({
            "sources": sources.tolist(), "targets": targets.tolist(),
        }),
    }


@dataclass
class PreparedXhdV4:
    """Application-facing owner for repeated directed witness queries."""

    owner: object
    targets: np.ndarray
    total_prepare_seconds: float
    maximum_distance: float
    initial_radius: float = 32.0
    maximum_rounds: int = 1
    targets_sha256: str = ""
    frozen_source_sha256: str | None = None
    frozen_expected: dict[str, object] | None = None

    def execute(self, sources) -> dict[str, object]:
        started = time.perf_counter()
        source_values = np.ascontiguousarray(sources, dtype=np.float32)
        optimized = hasattr(self.owner, "execute_global_witness")
        if optimized:
            nearest = self.owner.execute_global_witness(source_values)
            actual = dict(nearest.witness)
        else:
            nearest = execute_ranked_distance_window(
                self.owner,
                source_values,
                RankedDistanceWindowRequest(
                    k=1, minimum_distance=0.0,
                    maximum_distance=self.maximum_distance,
                    initial_radius=self.initial_radius,
                    maximum_rounds=self.maximum_rounds,
                    boundary_policy=DistanceWindowBoundaryPolicy.CLOSED,
                ),
            )
            actual = global_max_nearest_witness_f32(
                nearest.value,
                expected_query_ids=tuple(range(len(source_values))),
            )
        elapsed = time.perf_counter() - started
        # Correctness-oracle work belongs outside the prepared endpoint timer.
        source_sha256 = _array_sha256(source_values)
        if (
            self.frozen_expected is not None
            and source_sha256 == self.frozen_source_sha256
        ):
            expected = self.frozen_expected
        else:
            expected = _expected_for(source_values, self.targets)
        matched = (
            int(actual["source_id"]) == int(expected["source_id"])
            and int(actual["item_id"]) == int(expected["item_id"])
            and abs(float(actual["value"]) - float(expected["value"])) <= 1.0e-6
        )
        return {
            "schema": "rtdl.paper_reproduction.x_hd.v4.prepared.v1",
            "input_sha256": _digest({
                "sources_sha256": source_sha256,
                "targets_sha256": self.targets_sha256 or _array_sha256(self.targets),
            }),
            "output": actual,
            "expected": expected,
            "matched": matched,
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False,
            "cold_result_replaced": False,
            "lifecycle_receipt": self.owner.lifecycle_receipt,
            "traversal_receipt": nearest.traversal_receipt,
            "native_library_sha256": nearest.native_library_sha256,
            "bounded_device_global_witness_used": optimized,
            "full_per_query_host_projection_used": not optimized,
            "physical_metadata": (
                nearest.physical_metadata if optimized else None),
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
    targets=None,
    maximum_distance: float = 32.0,
    initial_radius: float | None = None,
    maximum_rounds: int | None = None,
    prepared_input=None,
) -> PreparedXhdV4:
    """Compile/verify once and prepare reusable target geometry."""

    started = time.perf_counter()
    if prepared_input is not None and targets is not None:
        raise ValueError("provide prepared_input or targets, not both")
    data = prepared_input if prepared_input is not None else build_v4_input()
    target_values = np.ascontiguousarray(
        data["targets"] if targets is None else targets, dtype=np.float32)
    selected_maximum_distance = float(
        data.get("maximum_distance", maximum_distance)
        if prepared_input is not None else maximum_distance
    )
    selected_initial_radius = float(
        data.get("initial_radius", selected_maximum_distance)
        if initial_radius is None else initial_radius
    )
    selected_maximum_rounds = int(
        data.get("maximum_rounds", 1)
        if maximum_rounds is None else maximum_rounds
    )
    authority, proof = compile_standard_multiround_authority(
        target, maximum_rounds=selected_maximum_rounds)
    exact_schema = ExactPredicateWitnessSchema(
        callback_ir_sha256=authority.relation.physical.callback.ir_sha256,
        effect_digest=authority.relation.physical.callback.effect_digest,
        physical_schema_sha256=authority.relation.physical.schema.schema_sha256,
        source_authority_nonce=authority.authority_nonce,
        producer_kind=CandidateProducerKind.SPHERE_NEAREST,
        partner_algebras=(
            ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32,),
        maximum_candidate_capacity=authority.schema.maximum_event_capacity,
    )
    exact_authority = verify_exact_predicate_witness_schema(
        callback_ir_sha256=authority.relation.physical.callback.ir_sha256,
        effect_digest=authority.relation.physical.callback.effect_digest,
        physical_schema_sha256=authority.relation.physical.schema.schema_sha256,
        source_authority_nonce=authority.authority_nonce,
        schema=exact_schema,
    )
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
    source_values = np.ascontiguousarray(data["sources"], dtype=np.float32)
    if source_values.ndim != 2 or source_values.shape[1] != 3 \
            or not len(source_values) or not np.isfinite(source_values).all():
        raise ValueError("finite non-empty float32 [Q,3] source domain required")
    owner = prepare_verified_global_nearest_witness_v4(
        authority, executable,
        exact_authority=exact_authority,
        any_hit_proof_authority=proof,
        target_points=target_values,
        query_domain_lower_bounds=np.min(source_values, axis=0),
        query_domain_upper_bounds=np.max(source_values, axis=0),
        native_library_path=native_library_path,
        maximum_query_count=len(source_values),
    )
    return PreparedXhdV4(
        owner=owner,
        targets=target_values,
        total_prepare_seconds=time.perf_counter() - started,
        maximum_distance=selected_maximum_distance,
        initial_radius=selected_initial_radius,
        maximum_rounds=selected_maximum_rounds,
        targets_sha256=_array_sha256(target_values),
        frozen_source_sha256=(
            str(data.get("sources_sha256")) if prepared_input is not None else None
        ),
        frozen_expected=(data.get("expected") if prepared_input is not None else None),
    )


def run_v4_complete(
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path,
):
    started = time.perf_counter()
    data = build_v4_input()
    authority, proof = compile_standard_multiround_authority(
        target, maximum_rounds=1)
    exact_schema = ExactPredicateWitnessSchema(
        callback_ir_sha256=authority.relation.physical.callback.ir_sha256,
        effect_digest=authority.relation.physical.callback.effect_digest,
        physical_schema_sha256=authority.relation.physical.schema.schema_sha256,
        source_authority_nonce=authority.authority_nonce,
        producer_kind=CandidateProducerKind.SPHERE_NEAREST,
        partner_algebras=(
            ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32,),
        maximum_candidate_capacity=authority.schema.maximum_event_capacity,
    )
    verify_exact_predicate_witness_schema(
        callback_ir_sha256=authority.relation.physical.callback.ir_sha256,
        effect_digest=authority.relation.physical.callback.effect_digest,
        physical_schema_sha256=authority.relation.physical.schema.schema_sha256,
        source_authority_nonce=authority.authority_nonce,
        schema=exact_schema,
    )
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
    maximum_distance = 32.0
    with prepare_multiround_spatial_callback(
        authority, executable,
        any_hit_proof_authority=proof,
        search_points=data["targets"],
        initial_radius=maximum_distance,
        native_library_path=native_library_path,
    ) as owner:
        nearest = execute_ranked_distance_window(
            owner,
            data["sources"],
            RankedDistanceWindowRequest(
                k=1, minimum_distance=0.0,
                maximum_distance=maximum_distance,
                initial_radius=maximum_distance,
                maximum_rounds=1,
                boundary_policy=DistanceWindowBoundaryPolicy.CLOSED,
            ),
        )
    actual = global_max_nearest_witness_f32(
        nearest.value,
        expected_query_ids=tuple(range(len(data["sources"]))),
    )
    elapsed = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.x_hd.v4.v1",
        "input_sha256": data["input_sha256"],
        "output": actual,
        "expected": data["expected"],
        "matched": actual == data["expected"],
        "registered_complete_seconds": elapsed,
        "complete_timer_includes": (
            "wkt_input_load", "app_owned_point_projection",
            "restricted_callback_parse_verify", "abi_and_wrapper_compile",
            "gas_prepare", "optix_nearest_execute",
            "exact_global_witness_materialization",
        ),
        "traversal_receipt": nearest.traversal_receipt,
        "native_library_sha256": nearest.traversal_receipt[
            "provider_library_sha256"],
        "default_selected_between_paper_algorithms": False,
    }


__all__ = [
    "PreparedXhdV4", "build_v4_input", "load_real_scale_v4_input",
    "prepare_v4", "run_v4_complete",
]
