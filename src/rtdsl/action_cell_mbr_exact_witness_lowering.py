from __future__ import annotations

import hashlib
import hmac
import math
import os
from pathlib import Path
import secrets
import threading
import time
from typing import Mapping

import numpy as np

from .action_native_identity import validate_native_library_identity
from .action_nearest_state_lowering import (
    ImmutablePointColumnDomain3DCertificate,
)


CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE = (
    "cell_mbr_exact_witness_3d_optix_traversal"
)
CELL_MBR_EXACT_WITNESS_3D_BACKEND = "optix_cell_mbr_exact_witness"
CELL_MBR_EXACT_WITNESS_FRONTIER_ROWS_PER_QUERY = 8
CELL_MBR_EXACT_WITNESS_PEAK_EXTRA_BYTES_PER_QUERY = 8192
CELL_MBR_INLINE_CONFIGURATION_POLICY = (
    "cell_mbr_cover_certified_population_up_to_reviewed_cap_v1"
)
CELL_MBR_INLINE_CONFIGURATION_FLOOR = 64
CELL_MBR_INLINE_CONFIGURATION_REVIEWED_CAP = 512
CELL_MBR_INLINE_CONFIGURATION_SOURCE_PATH = (
    "src/rtdsl/action_cell_mbr_exact_witness_lowering.py"
)
CELL_MBR_INLINE_CONFIGURATION_SOURCE_ANCHOR = (
    "CELL_MBR_INLINE_CONFIGURATION_POLICY"
)
_OWNER_SEAL_SECRET = secrets.token_bytes(32)


def _canonical_bytes(value: object) -> bytes:
    import json

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def cell_mbr_inline_configuration_policy_contract() -> dict[str, object]:
    """Return the exact source-bound production configuration policy.

    The policy is intentionally structural and timing-free.  The exact source
    digest is evaluated from the executing module bytes so a plan cannot bind
    an older resolver while claiming the current policy identity.
    """

    source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    body: dict[str, object] = {
        "schema": "rtdl.physical_configuration_policy.cell_mbr_inline.v1",
        "policy_id": CELL_MBR_INLINE_CONFIGURATION_POLICY,
        "resolution_rule": "min(reviewed_cap,max(prior_floor,max_certified_cell_population))",
        "prior_floor": CELL_MBR_INLINE_CONFIGURATION_FLOOR,
        "reviewed_cap": CELL_MBR_INLINE_CONFIGURATION_REVIEWED_CAP,
        "source_path": CELL_MBR_INLINE_CONFIGURATION_SOURCE_PATH,
        "source_sha256": source_sha256,
        "source_anchor": CELL_MBR_INLINE_CONFIGURATION_SOURCE_ANCHOR,
        "application_identity_used": False,
        "timing_or_learned_input_used": False,
        "universal_optimality_claimed": False,
    }
    body["policy_contract_sha256"] = _digest(body)
    return body


def resolve_cell_mbr_inline_configuration(
    point_counts,
    *,
    policy_contract: Mapping[str, object],
    caller_requested_max_inline_points: int,
) -> dict[str, object]:
    """Resolve one compiler-owned inline capacity from certified grid state."""

    expected = cell_mbr_inline_configuration_policy_contract()
    if not isinstance(policy_contract, Mapping) or _canonical_bytes(
        dict(policy_contract)
    ) != _canonical_bytes(expected):
        raise RuntimeError("cell-MBR physical configuration policy is missing or rebound")
    if (
        not isinstance(caller_requested_max_inline_points, int)
        or isinstance(caller_requested_max_inline_points, bool)
        or caller_requested_max_inline_points <= 0
    ):
        raise ValueError("caller_requested_max_inline_points must be positive")
    raw = np.asarray(point_counts)
    if raw.ndim != 1 or raw.size == 0 or raw.dtype.kind not in {"u", "i"}:
        raise ValueError("certified cell point_counts must be a nonempty integer column")
    if np.any(raw < 0):
        raise ValueError("certified cell point_counts cannot be negative")
    counts = np.ascontiguousarray(raw, dtype="<u8")
    maximum = int(np.max(counts))
    if maximum <= 0:
        raise ValueError("certified cell point_counts must contain target points")
    floor = int(expected["prior_floor"])
    cap = int(expected["reviewed_cap"])
    selected = min(cap, max(floor, maximum))
    counts_hasher = hashlib.sha256()
    counts_hasher.update(b"rtdl.certified_cell_population_column.v1\x00")
    counts_hasher.update(str(int(counts.size)).encode("ascii"))
    counts_hasher.update(b"\x00")
    counts_hasher.update(counts.tobytes(order="C"))
    body: dict[str, object] = {
        "schema": "rtdl.resolved_physical_configuration.cell_mbr_inline.v1",
        "policy_contract_sha256": expected["policy_contract_sha256"],
        "policy_id": expected["policy_id"],
        "certified_point_counts_sha256": counts_hasher.hexdigest(),
        "certified_cell_count": int(counts.size),
        "max_certified_cell_population": maximum,
        "prior_floor": floor,
        "reviewed_cap": cap,
        "selected_max_inline_points": selected,
        "full_cell_population_covered": selected >= maximum,
        "residual_heavy_cell_count": int(np.count_nonzero(counts > selected)),
        "caller_requested_max_inline_points": caller_requested_max_inline_points,
        "caller_parameter_override_accepted": False,
        "application_identity_used": False,
        "timing_or_learned_input_used": False,
        "universal_optimality_claimed": False,
    }
    body["resolved_configuration_sha256"] = _digest(body)
    return body


def _point_columns(points: np.ndarray, ids: np.ndarray) -> dict[str, object]:
    return {
        "ids": ids,
        "x": points[:, 0],
        "y": points[:, 1],
        "z": points[:, 2],
        "coordinate_matrix": points,
        "coordinate_matrix_fields": ("x", "y", "z"),
    }


def _exact_missing_rows(
    query_points: np.ndarray,
    target_points: np.ndarray,
    target_ids: np.ndarray,
    missing_rows: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Complete missing rows with exact streaming F64 distance and ID ties."""

    item_ids = np.empty(missing_rows.size, dtype=np.int64)
    distances = np.empty(missing_rows.size, dtype=np.float64)
    evaluations = 0
    for output_index, query_row in enumerate(missing_rows.tolist()):
        deltas = target_points - query_points[int(query_row)]
        distances_sq = np.einsum("ij,ij->i", deltas, deltas)
        best_sq = float(np.min(distances_sq))
        tied_ids = target_ids[distances_sq == best_sq]
        item_ids[output_index] = int(np.min(tied_ids))
        distances[output_index] = math.sqrt(best_sq)
        evaluations += int(target_points.shape[0])
    return item_ids, distances, evaluations


class PreparedCellMbrExactWitness3DOptix:
    """Compiler-owned composition of existing generic cell-MBR primitives.

    The owner intentionally introduces no native semantic family. It binds one
    exact native object and composes its already-existing CUDA grid/seed and
    OptiX frontier symbols into the verified certified-nearest/global-witness
    contract.
    """

    contract = "rtdl.prepared_cell_mbr_exact_witness_3d_optix.v1"
    _prepare_symbol_name = (
        "compiler_python_prepare_cell_mbr_exact_witness_3d_from_validated_columns"
    )

    def __init__(
        self,
        target_points,
        *,
        target_ids,
        column_domain_certificate,
        grid_shape,
        max_inline_points: int,
        cell_point_order: str,
        expected_native_library_identity,
        expected_native_library_ref,
        prepared_target_domain: bool = False,
        physical_configuration_policy: Mapping[str, object] | None = None,
    ) -> None:
        if not isinstance(
            column_domain_certificate,
            ImmutablePointColumnDomain3DCertificate,
        ):
            raise TypeError(
                "cell-MBR exact-witness owner requires an immutable point-domain certificate"
            )
        column_domain_certificate.validate_exact(target_points, target_ids)
        target_matrix = column_domain_certificate.target_points
        target_id_values = column_domain_certificate.target_ids
        shape = tuple(int(value) for value in grid_shape)
        if len(shape) != 3 or any(value <= 0 for value in shape):
            raise ValueError("grid_shape must contain three positive entries")
        volume = shape[0] * shape[1] * shape[2]
        if volume > (1 << 32) - 1:
            raise ValueError("grid_shape volume exceeds U32")
        if (
            not isinstance(max_inline_points, int)
            or isinstance(max_inline_points, bool)
            or max_inline_points <= 0
        ):
            raise ValueError("max_inline_points must be a positive integer")
        if cell_point_order not in {"point-id", "input-stable"}:
            raise ValueError(
                "cell_point_order must be 'point-id' or 'input-stable'"
            )
        if expected_native_library_identity is None or expected_native_library_ref is None:
            raise RuntimeError(
                "cell-MBR exact-witness owner requires a compiler-bound native identity"
            )
        if not isinstance(prepared_target_domain, bool):
            raise TypeError("prepared_target_domain must be boolean")
        identity = validate_native_library_identity(
            expected_native_library_ref,
            expected_native_library_identity,
        )

        from .partner_continuations import (
            point_grid_cell_mbrs_native_3d_cuda_columns,
        )

        grid_started = time.perf_counter()
        target_columns = _point_columns(target_matrix, target_id_values)
        grid = point_grid_cell_mbrs_native_3d_cuda_columns(
            target_columns,
            coordinate_fields=("x", "y", "z"),
            grid_shape=shape,
            cell_point_order=cell_point_order,
            return_metadata=True,
        )
        grid_seconds = time.perf_counter() - grid_started
        cell_columns = grid["cell_columns"]
        required = {
            "cell_ids",
            "original_cell_ids",
            "point_begin_offsets",
            "point_counts",
            "point_row_indices",
            "grid_shape",
            "grid_lower_bounds",
            "grid_upper_bounds",
            "min_x",
            "min_y",
            "min_z",
            "max_x",
            "max_y",
            "max_z",
        }
        if not required.issubset(cell_columns):
            raise RuntimeError(
                "generic point-grid builder returned incomplete cell-MBR columns"
            )
        cell_count = int(np.asarray(cell_columns["cell_ids"]).size)
        if cell_count <= 0:
            raise RuntimeError("generic point-grid builder returned no cells")
        requested_max_inline_points = max_inline_points
        if physical_configuration_policy is not None:
            physical_configuration = resolve_cell_mbr_inline_configuration(
                cell_columns["point_counts"],
                policy_contract=physical_configuration_policy,
                caller_requested_max_inline_points=requested_max_inline_points,
            )
            max_inline_points = int(
                physical_configuration["selected_max_inline_points"]
            )
        else:
            physical_configuration = {
                "schema": "rtdl.resolved_physical_configuration.direct_caller.v1",
                "policy_id": None,
                "selected_max_inline_points": requested_max_inline_points,
                "caller_requested_max_inline_points": requested_max_inline_points,
                "caller_parameter_override_accepted": True,
                "production_compiler_owned": False,
            }

        self._library = expected_native_library_ref
        self._native_library_identity = identity
        self._column_domain_certificate = column_domain_certificate
        self._target_points = target_matrix
        self._target_ids = target_id_values
        self._target_columns = target_columns
        self._cell_columns = cell_columns
        self._grid_metadata = dict(grid["metadata"])
        self._grid_shape = shape
        self._cell_point_order = cell_point_order
        self._max_inline_points = max_inline_points
        self._requested_max_inline_points = requested_max_inline_points
        self._physical_configuration = physical_configuration
        self._cell_count = cell_count
        self._grid_prepare_seconds = float(grid_seconds)
        self._execution_count = 0
        self._prepared_generation = secrets.token_hex(16)
        self._creator_pid = os.getpid()
        self._lock = threading.RLock()
        self._closed = False
        self._library_object_id = id(self._library)
        self._certificate_object_id = id(self._column_domain_certificate)
        self._target_points_object_id = id(self._target_points)
        self._target_ids_object_id = id(self._target_ids)
        self._cell_columns_object_id = id(self._cell_columns)
        self._prepared_target_domain_enabled = prepared_target_domain
        self._prepared_target_domain = None
        if prepared_target_domain:
            from .optix_runtime import _prepare_point_column_domain_3d_optix

            self._prepared_target_domain = _prepare_point_column_domain_3d_optix(
                column_domain_certificate=self._column_domain_certificate,
                expected_native_library_identity=self._native_library_identity,
                expected_native_library_ref=self._library,
            )
        try:
            self._binding_seal = self._issue_binding_seal()
        except Exception:
            if self._prepared_target_domain is not None:
                self._prepared_target_domain.close()
            raise

    @property
    def closed(self) -> bool:
        return self._closed

    def _binding_payload(self) -> bytes:
        return (
            f"{self.contract}\x00{id(self._library)}\x00"
            f"{self._native_library_identity.identity_digest}\x00"
            f"{id(self._column_domain_certificate)}\x00"
            f"{id(self._target_points)}\x00{id(self._target_ids)}\x00"
            f"{id(self._cell_columns)}\x00{self._grid_shape!r}\x00"
            f"{self._cell_point_order}\x00{self._max_inline_points}\x00"
            f"{self._physical_configuration.get('resolved_configuration_sha256')}\x00"
            f"{self._creator_pid}\x00{self._prepared_target_domain_enabled}\x00"
            f"{id(self._prepared_target_domain)}"
        ).encode("ascii")

    def _issue_binding_seal(self) -> str:
        return hmac.new(
            _OWNER_SEAL_SECRET,
            self._binding_payload(),
            hashlib.sha256,
        ).hexdigest()

    def _validate_binding(self) -> None:
        if os.getpid() != self._creator_pid:
            raise RuntimeError(
                "prepared cell-MBR exact-witness owner cannot cross a process boundary"
            )
        if self._closed:
            raise RuntimeError("prepared cell-MBR exact-witness owner is closed")
        if (
            id(self._library) != self._library_object_id
            or id(self._column_domain_certificate)
            != self._certificate_object_id
            or id(self._target_points) != self._target_points_object_id
            or id(self._target_ids) != self._target_ids_object_id
            or id(self._cell_columns) != self._cell_columns_object_id
            or not hmac.compare_digest(
                self._binding_seal,
                self._issue_binding_seal(),
            )
        ):
            raise RuntimeError(
                "prepared cell-MBR exact-witness object binding changed"
            )
        self._column_domain_certificate.validate_exact(
            self._target_points,
            self._target_ids,
        )
        validate_native_library_identity(
            self._library,
            self._native_library_identity,
        )

    def run(
        self,
        query_points,
        *,
        validation_sample_indices=(),
    ) -> dict[str, object]:
        with self._lock:
            return self._run_locked(
                query_points,
                validation_sample_indices=validation_sample_indices,
            )

    def _run_locked(
        self,
        query_points,
        *,
        validation_sample_indices=(),
    ) -> dict[str, object]:
        self._validate_binding()
        query_matrix = np.array(
            query_points,
            dtype=np.float64,
            order="C",
            copy=True,
        )
        if query_matrix.ndim != 2 or query_matrix.shape[1:] != (3,):
            raise ValueError("query_points must be F64[query_count][3]")
        query_count = int(query_matrix.shape[0])
        if query_count <= 0 or query_count > (1 << 32) - 1:
            raise ValueError("query_count must fit positive U32")
        if not bool(np.all(np.isfinite(query_matrix))):
            raise ValueError("query coordinates must be finite")
        sample_indices = np.ascontiguousarray(
            validation_sample_indices,
            dtype=np.int64,
        )
        if sample_indices.ndim != 1 or (
            sample_indices.size
            and (
                bool(np.any(sample_indices < 0))
                or bool(np.any(sample_indices >= query_count))
                or int(np.unique(sample_indices).size)
                != int(sample_indices.size)
            )
        ):
            raise ValueError(
                "validation_sample_indices must be unique and in range"
            )
        query_ids = np.arange(query_count, dtype=np.int64)
        query_columns = _point_columns(query_matrix, query_ids)

        from .partner_continuations import (
            cell_mbr_nearest_frontier_native_3d_optix_columns,
            max_nearest_distance_witness_numpy_columns,
            nearest_witness_from_cell_mbr_frontier_numpy_columns,
            seed_nearest_witness_from_local_grid_cell_numpy_columns,
        )

        total_started = time.perf_counter()
        seed_started = time.perf_counter()
        seed = seed_nearest_witness_from_local_grid_cell_numpy_columns(
            query_columns,
            self._target_columns,
            self._cell_columns,
            coordinate_fields=("x", "y", "z"),
            executor="native_cuda",
            return_metadata=True,
        )
        seed_seconds = time.perf_counter() - seed_started
        seed_distances = np.asarray(
            seed["columns"]["nearest_distances"],
            dtype=np.float64,
        )
        seed_item_ids = np.asarray(
            seed["columns"]["nearest_item_ids"],
            dtype=np.int64,
        )
        if (
            seed_distances.shape != (query_count,)
            or seed_item_ids.shape != (query_count,)
            or not bool(np.all(np.isfinite(seed_distances)))
            or bool(np.any(seed_distances < 0.0))
            or bool(np.any(seed_item_ids < 0))
        ):
            raise RuntimeError(
                "generic local-grid seed did not produce a finite upper bound for every query"
            )
        radius = float(np.max(seed_distances)) + 1.0e-12

        # Traversal is mandatory. An exact or apparently exact seed is never a
        # legal reason to skip this physical candidate's OptiX frontier.
        frontier_started = time.perf_counter()
        # Keep this production candidate's extra live frontier memory linear
        # and source-provable.  The generic adapter otherwise treats
        # ``row_capacity=None`` as permission to double up to the full
        # query-cell product.  DEFAULT may not call that unbounded retrying
        # route a bounded streaming program.  Overflow is deliberately a
        # typed fail-closed outcome; it is never retried, hidden, or relabelled.
        frontier_row_capacity = max(
            query_count * CELL_MBR_EXACT_WITNESS_FRONTIER_ROWS_PER_QUERY,
            1024,
        )
        if frontier_row_capacity > (1 << 32) - 1:
            raise RuntimeError(
                "cell-MBR exact-witness bounded frontier capacity exceeds U32"
            )
        frontier = cell_mbr_nearest_frontier_native_3d_optix_columns(
            query_columns,
            self._cell_columns,
            target_point_columns=self._target_columns,
            radius=radius,
            current_best_distances=seed_distances,
            current_best_item_ids=seed_item_ids,
            max_inline_points=self._max_inline_points,
            row_capacity=frontier_row_capacity,
            emit_pruned_rows=False,
            sort_rows=False,
            inline_nearest=True,
            collect_inline_stats=True,
            global_bound_early_break=False,
            collect_native_phase_timings=True,
            allow_overflow_telemetry=False,
            return_split_frontiers=False,
            return_metadata=True,
            issue_completed_state_evidence=True,
            _prepared_target_domain=self._prepared_target_domain,
        )
        frontier_seconds = time.perf_counter() - frontier_started
        expected_frontier_symbol = (
            "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_prepared_domain_v1"
            if self._prepared_target_domain_enabled
            else "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4"
        )
        if frontier["metadata"].get("native_generic_symbol") != expected_frontier_symbol:
            raise RuntimeError(
                "cell-MBR exact-witness candidate resolved the wrong OptiX frontier symbol"
            )
        prepared_domain_telemetry = frontier["metadata"].get(
            "prepared_target_domain_telemetry"
        )
        if self._prepared_target_domain_enabled:
            if not isinstance(prepared_domain_telemetry, dict):
                raise RuntimeError(
                    "prepared target-domain execution omitted native telemetry"
                )
            if (
                prepared_domain_telemetry.get("native_validation_count") != 1
                or prepared_domain_telemetry.get(
                    "per_launch_target_hash_set_construction_count"
                )
                != 0
                or prepared_domain_telemetry.get("prepared_target_domain_used")
                is not True
            ):
                raise RuntimeError(
                    "prepared target-domain native telemetry violated its contract"
                )
        if frontier["metadata"].get("inline_nearest_state_available") is not True:
            raise RuntimeError(
                "cell-MBR exact-witness traversal did not return inline nearest state"
            )
        if frontier["metadata"].get("overflowed") is not False:
            raise RuntimeError(
                "cell-MBR exact-witness traversal overflowed"
            )

        frontier_metadata = dict(frontier["metadata"])
        frontier_row_count = int(frontier_metadata.get("row_count", -1))
        if frontier_row_count < 0:
            raise RuntimeError(
                "cell-MBR exact-witness traversal omitted its row count"
            )
        producer_evidence = frontier.get(
            "_completed_nearest_state_producer_evidence"
        )
        continuation_started = time.perf_counter()
        capability_metadata = None
        producer_evidence_metadata = None
        completed_state_mode = "ordinary_nonzero_frontier_continuation"
        full_nearest_state_host_projection_used = True
        verified_completed_state_validation_seconds = 0.0
        if frontier_row_count == 0 and producer_evidence is not None:
            from .action_completed_nearest_state import (
                EXPECTED_COMPOSITION,
                EXPECTED_LOWERED_TEMPLATE,
                EXPECTED_PROGRAM_BUNDLE,
                verify_completed_nearest_state_3d,
            )

            capability = verify_completed_nearest_state_3d(
                producer_evidence,
                query_matrix=query_matrix,
                query_ids=query_ids,
                target_certificate=self._column_domain_certificate,
                native_library_identity=self._native_library_identity,
                native_library_ref=self._library,
                expected_program_bundle=EXPECTED_PROGRAM_BUNDLE,
                expected_lowered_template=EXPECTED_LOWERED_TEMPLATE,
                expected_composition=EXPECTED_COMPOSITION,
                prepared_generation=self._prepared_generation,
                execution_generation=self._execution_count + 1,
                permitted_consumer="existing_global_witness_reducer",
            )
            state_columns = capability.consume_once(
                permitted_consumer="existing_global_witness_reducer"
            )
            nearest_ids = np.asarray(
                state_columns["nearest_item_ids"],
                dtype=np.int64,
            )
            nearest_distances = np.asarray(
                state_columns["nearest_distances"],
                dtype=np.float64,
            )
            producer_evidence_metadata = producer_evidence.to_metadata()
            capability_metadata = capability.to_metadata()
            missing = np.asarray([], dtype=np.int64)
            fallback_evaluations = 0
            continuation_metadata = {
                "contract": (
                    "verified_completed_nearest_state_to_existing_global_witness"
                ),
                "candidate_distance_evaluations": 0,
                "used_frontier_row_count": 0,
            }
            completed_state_mode = "verified_completed_state_passthrough"
            full_nearest_state_host_projection_used = False
        elif frontier_row_count == 0:
            # The frozen Goal5675 policy never silently trusts a zero row
            # count.  Missing proof takes the explicit all-row exact fallback
            # inside this registered execution interval.
            missing = np.arange(query_count, dtype=np.int64)
            (
                nearest_ids,
                nearest_distances,
                fallback_evaluations,
            ) = _exact_missing_rows(
                query_matrix,
                self._target_points,
                self._target_ids,
                missing,
            )
            continuation_metadata = {
                "contract": (
                    "unverified_zero_frontier_all_row_exact_f64_fallback"
                ),
                "candidate_distance_evaluations": 0,
                "used_frontier_row_count": 0,
            }
            completed_state_mode = (
                "unverified_zero_frontier_all_row_exact_fallback"
            )
        else:
            if producer_evidence is not None:
                raise RuntimeError(
                    "completed nearest-state evidence contradicts nonzero frontier rows"
                )
            state = nearest_witness_from_cell_mbr_frontier_numpy_columns(
                query_columns,
                self._target_columns,
                self._cell_columns,
                frontier["row_table"],
                coordinate_fields=("x", "y", "z"),
                current_best_distances=frontier["nearest_state"][
                    "current_best_distances"
                ],
                current_best_item_ids=frontier["nearest_state"][
                    "current_best_item_ids"
                ],
                executor="auto",
                allow_missing=True,
                return_metadata=True,
            )
            state_columns = state["columns"]
            nearest_ids = np.asarray(
                state_columns["nearest_item_ids"],
                dtype=np.int64,
            ).copy()
            nearest_distances = np.asarray(
                state_columns["nearest_distances"],
                dtype=np.float64,
            ).copy()
            missing = np.flatnonzero(
                (nearest_ids < 0) | ~np.isfinite(nearest_distances)
            ).astype(np.int64, copy=False)
            fallback_evaluations = 0
            if missing.size:
                (
                    fallback_ids,
                    fallback_distances,
                    fallback_evaluations,
                ) = _exact_missing_rows(
                    query_matrix,
                    self._target_points,
                    self._target_ids,
                    missing,
                )
                nearest_ids[missing] = fallback_ids
                nearest_distances[missing] = fallback_distances
            continuation_metadata = dict(state["metadata"])
        continuation_seconds = time.perf_counter() - continuation_started
        if completed_state_mode == "verified_completed_state_passthrough":
            verified_completed_state_validation_seconds = (
                continuation_seconds
            )
        if (
            nearest_ids.shape != (query_count,)
            or nearest_distances.shape != (query_count,)
            or bool(np.any(nearest_ids < 0))
            or not bool(np.all(np.isfinite(nearest_distances)))
            or bool(np.any(nearest_distances < 0.0))
        ):
            raise RuntimeError(
                "cell-MBR exact-witness continuation did not cover every query"
            )

        reduce_started = time.perf_counter()
        witness = max_nearest_distance_witness_numpy_columns(
            {
                "source_ids": query_ids,
                "nearest_item_ids": nearest_ids,
                "nearest_distances": nearest_distances,
            },
            return_metadata=True,
        )
        reduce_seconds = time.perf_counter() - reduce_started
        total_seconds = time.perf_counter() - total_started
        self._validate_binding()
        self._execution_count += 1

        validation_items = nearest_ids[sample_indices].copy()
        validation_distances = nearest_distances[sample_indices].copy()
        seed_metadata = dict(seed["metadata"])
        native_phase = frontier_metadata.get("native_phase_timings")
        candidate_evaluations = (
            int(seed_metadata.get("candidate_distance_evaluations", 0))
            + int(
                continuation_metadata.get(
                    "candidate_distance_evaluations",
                    0,
                )
            )
            + int(fallback_evaluations)
        )
        certificate_metadata = self._column_domain_certificate.to_metadata()
        identity_metadata = self._native_library_identity.to_metadata()
        return {
            "actual": {
                "source_id": int(witness["source_id"]),
                "item_id": int(witness["item_id"]),
                "value": float(witness["value"]),
            },
            "validation_samples": {
                "query_row_indices": sample_indices.copy(),
                "nearest_item_ids": validation_items,
                "nearest_distances": validation_distances,
            },
            "metadata": {
                "contract": self.contract,
                "physical_executor_kind": (
                    "compiler_owned_generic_cell_mbr_exact_witness_optix_frontier"
                ),
                "physical_placement": "traversal_device_continuation",
                "native_library_identity": identity_metadata,
                "native_library_identity_digest": (
                    self._native_library_identity.identity_digest
                ),
                "native_library_identity_revalidated": True,
                "native_prepare_symbol": self._prepare_symbol_name,
                "target_column_domain_certificate_contract": (
                    certificate_metadata["contract"]
                ),
                "target_column_domain_certificate_reused": True,
                "target_column_domain_certificate": certificate_metadata,
                "target_column_domain_single_full_validation": True,
                "target_column_domain_validation_repeated": False,
                "cell_count": self._cell_count,
                "grid_shape": list(self._grid_shape),
                "cell_point_order": self._cell_point_order,
                "physical_configuration": dict(self._physical_configuration),
                "candidate_distance_evaluations": candidate_evaluations,
                "grid_cell_probes": int(
                    seed_metadata.get("grid_cell_probes", 0)
                ),
                "scanned_cell_count": int(
                    continuation_metadata.get(
                        "used_frontier_row_count",
                        0,
                    )
                ),
                "native_phase_timings_sec": {
                    "prepared_grid_cell_mbrs": self._grid_prepare_seconds,
                    "local_grid_seed": seed_seconds,
                    "optix_frontier": frontier_seconds,
                    "host_exact_continuation": (
                        0.0
                        if completed_state_mode
                        == "verified_completed_state_passthrough"
                        else continuation_seconds
                    ),
                    "verified_completed_state_validation": (
                        verified_completed_state_validation_seconds
                    ),
                    "host_global_witness": reduce_seconds,
                    "total_execution": total_seconds,
                },
                "frontier_native_phase_timings": native_phase,
                "frontier_native_symbol": frontier_metadata.get(
                    "native_generic_symbol"
                ),
                "prepared_target_domain_enabled": (
                    self._prepared_target_domain_enabled
                ),
                "prepared_target_domain_telemetry": (
                    prepared_domain_telemetry
                ),
                "frontier_row_count": int(
                    frontier_metadata.get("row_count", 0)
                ),
                "frontier_row_capacity": int(frontier_row_capacity),
                "frontier_capacity_policy": (
                    "explicit_linear_eight_rows_per_query_fail_closed"
                ),
                "frontier_row_capacity_attempts": list(
                    frontier_metadata.get("row_capacity_attempts", ())
                ),
                "frontier_inline_nearest": True,
                "frontier_inline_stats_collected": bool(
                    frontier_metadata.get("inline_stats_collected", False)
                ),
                "frontier_inline_cell_hit_count": (
                    frontier_metadata.get("inline_cell_hit_count")
                ),
                "frontier_inline_point_evaluation_count": (
                    frontier_metadata.get("inline_point_evaluation_count")
                ),
                "frontier_nearest_state_source_binding": (
                    frontier_metadata.get("nearest_state_source_binding")
                ),
                "frontier_returned_source_ids_device_evidenced": bool(
                    frontier_metadata.get(
                        "returned_source_ids_device_evidenced",
                        False,
                    )
                ),
                "frontier_was_mandatory": True,
                "exact_seed_frontier_skipped": False,
                "completed_nearest_state_mode": completed_state_mode,
                "completed_nearest_state_capability_used": (
                    completed_state_mode
                    == "verified_completed_state_passthrough"
                ),
                "completed_nearest_state_producer_evidence": (
                    producer_evidence_metadata
                ),
                "verified_completed_nearest_state": capability_metadata,
                "unverified_zero_frontier_all_row_fallback_used": (
                    completed_state_mode
                    == "unverified_zero_frontier_all_row_exact_fallback"
                ),
                "ordinary_nonzero_frontier_continuation_unchanged": (
                    completed_state_mode
                    == "ordinary_nonzero_frontier_continuation"
                ),
                "missing_fallback_count": int(missing.size),
                "missing_fallback_distance_evaluations": int(
                    fallback_evaluations
                ),
                "global_reducer_contract": witness["metadata"].get(
                    "contract"
                ),
                "target_and_grid_device_resident_for_prepared_lifetime": False,
                "nearest_state_device_resident_through_global_reducer": False,
                "host_nearest_state_handoff_visible": True,
                "full_nearest_state_host_projection_used": (
                    full_nearest_state_host_projection_used
                ),
                "native_semantic_family_added": False,
                "application_selected_backend": False,
                "app_semantics": "none",
                "runtime_speedup_claimed": False,
                "paper_performance_claimed": False,
                "execution_count": self._execution_count,
            },
        }

    def to_metadata(self) -> dict[str, object]:
        with self._lock:
            return self._to_metadata_locked()

    def _to_metadata_locked(self) -> dict[str, object]:
        if not self._closed:
            self._validate_binding()
        return {
            "contract": self.contract,
            "backend": CELL_MBR_EXACT_WITNESS_3D_BACKEND,
            "template": CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE,
            "target_count": int(self._target_points.shape[0]),
            "cell_count": self._cell_count,
            "grid_shape": list(self._grid_shape),
            "cell_point_order": self._cell_point_order,
            "max_inline_points": self._max_inline_points,
            "requested_max_inline_points": self._requested_max_inline_points,
            "physical_configuration": dict(self._physical_configuration),
            "native_library_identity": (
                self._native_library_identity.to_metadata()
            ),
            "execution_count": self._execution_count,
            "closed": self._closed,
            "prepared_target_domain_enabled": (
                self._prepared_target_domain_enabled
            ),
            "prepared_target_domain_telemetry": (
                None
                if self._prepared_target_domain is None or self._closed
                else self._prepared_target_domain.telemetry()
            ),
            "native_semantic_family_added": False,
            "application_selected_backend": False,
        }

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._validate_binding()
            if self._prepared_target_domain is not None:
                self._prepared_target_domain.close()
            self._closed = True

    def __enter__(self):
        with self._lock:
            self._validate_binding()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            if hasattr(self, "_closed") and not self._closed:
                self.close()
        except Exception:
            pass


def prepare_cell_mbr_exact_witness_3d_optix(
    target_points,
    *,
    target_ids,
    column_domain_certificate,
    grid_shape,
    max_inline_points: int,
    cell_point_order: str,
    expected_native_library_identity,
    expected_native_library_ref,
    prepared_target_domain: bool = False,
    physical_configuration_policy: Mapping[str, object] | None = None,
) -> PreparedCellMbrExactWitness3DOptix:
    return PreparedCellMbrExactWitness3DOptix(
        target_points,
        target_ids=target_ids,
        column_domain_certificate=column_domain_certificate,
        grid_shape=grid_shape,
        max_inline_points=max_inline_points,
        cell_point_order=cell_point_order,
        expected_native_library_identity=expected_native_library_identity,
        expected_native_library_ref=expected_native_library_ref,
        prepared_target_domain=prepared_target_domain,
        physical_configuration_policy=physical_configuration_policy,
    )


__all__ = (
    "CELL_MBR_EXACT_WITNESS_3D_BACKEND",
    "CELL_MBR_EXACT_WITNESS_3D_OPTIX_TRAVERSAL_TEMPLATE",
    "CELL_MBR_INLINE_CONFIGURATION_FLOOR",
    "CELL_MBR_INLINE_CONFIGURATION_POLICY",
    "CELL_MBR_INLINE_CONFIGURATION_REVIEWED_CAP",
    "PreparedCellMbrExactWitness3DOptix",
    "cell_mbr_inline_configuration_policy_contract",
    "prepare_cell_mbr_exact_witness_3d_optix",
    "resolve_cell_mbr_inline_configuration",
)
