from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

try:
    import numpy as np
except ModuleNotFoundError:
    class _MissingNumpy:
        def __getattr__(self, name: str):
            raise ModuleNotFoundError(
                "numpy is required for RTDL partner continuation helpers; "
                "use a Python environment with project dependencies installed"
            )

    np = _MissingNumpy()

try:
    from numba import njit as _numba_njit
    from numba import prange as _numba_prange
except Exception:
    _numba_njit = None
    _numba_prange = range


CELL_MBR_FRONTIER_KIND_CODES = {
    "inline": 1,
    "offload": 2,
    "pruned": 3,
}

CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT = "generic_cell_mbr_nearest_frontier_native_abi_v1"

CELL_MBR_TRAVERSAL_ROW_SCHEMA = (
    "frontier_kind_code",
    "query_row_id",
    "query_point_id",
    "cell_id",
    "point_begin_offset",
    "point_count",
    "min_distance",
    "max_distance",
)

HEAVY_OFFLOAD_WORKLIST_CONTRACT = "generic_heavy_offload_worklist_v1"

HEAVY_OFFLOAD_WORKLIST_KIND_CODES = {
    "active": 1,
    "miss": 2,
    "deferred": 3,
}

HEAVY_OFFLOAD_WORKLIST_ROW_SCHEMA = (
    "work_source_id",
    "work_primitive_id",
    "work_begin_offset",
    "work_count",
    "work_kind_code",
    "work_cost_estimate",
    "lower_bound",
    "upper_bound",
)

HEAVY_OFFLOAD_INT_ID_BYTES = 8

APP_IDENTITY_FORBIDDEN_TOKENS = (
    "x" + "hd",
    "x-" + "hd",
    "haus" + "dorff",
    "pa" + "per",
    "hd_" + "exec",
)


@dataclass(frozen=True)
class PartnerCandidateRows:
    """Backend-neutral candidate row schema for v2 partner continuations."""

    query_ids: np.ndarray
    primitive_ids: np.ndarray
    values: np.ndarray | None = None
    witness_ids: np.ndarray | None = None

    def normalized(self) -> "PartnerCandidateRows":
        query_ids = np.asarray(self.query_ids, dtype=np.int64)
        primitive_ids = np.asarray(self.primitive_ids, dtype=np.int64)
        if query_ids.shape != primitive_ids.shape:
            raise ValueError("query_ids and primitive_ids must have the same shape")
        values = None if self.values is None else np.asarray(self.values, dtype=np.float64)
        witness_ids = None if self.witness_ids is None else np.asarray(self.witness_ids, dtype=np.int64)
        if values is not None and values.shape != query_ids.shape:
            raise ValueError("values must have the same shape as query_ids")
        if witness_ids is not None and witness_ids.shape != query_ids.shape:
            raise ValueError("witness_ids must have the same shape as query_ids")
        return PartnerCandidateRows(
            query_ids=query_ids,
            primitive_ids=primitive_ids,
            values=values,
            witness_ids=witness_ids,
        )


def _as_i64(values, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.int64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a 1-D array")
    return array


def _as_f64(values, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a 1-D array")
    return array


def _seed_nearest_witness_loop_impl(
    query_matrix,
    target_matrix,
    target_ids,
    cell_ids,
    cell_min_matrix,
    cell_max_matrix,
    begins,
    counts,
    point_row_indices,
):
    query_count = query_matrix.shape[0]
    target_dim = target_matrix.shape[1]
    cell_count = cell_ids.shape[0]
    best_distances = np.empty(query_count, dtype=np.float64)
    best_item_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_point_counts = np.empty(query_count, dtype=np.int64)

    for query_row in range(query_count):
        best_cell_index = -1
        best_cell_id = np.int64(9223372036854775807)
        best_mbr_distance_sq = np.inf
        for cell_index in range(cell_count):
            if counts[cell_index] <= 0:
                continue
            distance_sq = 0.0
            for axis_index in range(target_dim):
                q = query_matrix[query_row, axis_index]
                low_delta = cell_min_matrix[cell_index, axis_index] - q
                high_delta = q - cell_max_matrix[cell_index, axis_index]
                outside_delta = 0.0
                if low_delta > outside_delta:
                    outside_delta = low_delta
                if high_delta > outside_delta:
                    outside_delta = high_delta
                distance_sq += outside_delta * outside_delta
            cell_id = cell_ids[cell_index]
            if (
                distance_sq < best_mbr_distance_sq
                or (distance_sq == best_mbr_distance_sq and cell_id < best_cell_id)
            ):
                best_mbr_distance_sq = distance_sq
                best_cell_id = cell_id
                best_cell_index = cell_index

        begin = begins[best_cell_index]
        count = counts[best_cell_index]
        best_point_distance_sq = np.inf
        best_point_id = np.int64(9223372036854775807)
        for offset in range(count):
            target_row = point_row_indices[begin + offset]
            distance_sq = 0.0
            for axis_index in range(target_dim):
                delta = query_matrix[query_row, axis_index] - target_matrix[target_row, axis_index]
                distance_sq += delta * delta
            target_id = target_ids[target_row]
            if (
                distance_sq < best_point_distance_sq
                or (distance_sq == best_point_distance_sq and target_id < best_point_id)
            ):
                best_point_distance_sq = distance_sq
                best_point_id = target_id

        best_distances[query_row] = np.sqrt(best_point_distance_sq)
        best_item_ids[query_row] = best_point_id
        seed_cell_ids[query_row] = best_cell_id
        seed_cell_point_counts[query_row] = count

    return best_distances, best_item_ids, seed_cell_ids, seed_cell_point_counts


if _numba_njit is not None:
    _seed_nearest_witness_loop_impl = _numba_njit(cache=True)(_seed_nearest_witness_loop_impl)


def _seed_nearest_witness_parallel_loop_impl(
    query_matrix,
    target_matrix,
    target_ids,
    cell_ids,
    cell_min_matrix,
    cell_max_matrix,
    begins,
    counts,
    point_row_indices,
):
    query_count = query_matrix.shape[0]
    target_dim = target_matrix.shape[1]
    cell_count = cell_ids.shape[0]
    best_distances = np.empty(query_count, dtype=np.float64)
    best_item_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_point_counts = np.empty(query_count, dtype=np.int64)

    for query_row in _numba_prange(query_count):
        best_cell_index = -1
        best_cell_id = np.int64(9223372036854775807)
        best_mbr_distance_sq = np.inf
        for cell_index in range(cell_count):
            if counts[cell_index] <= 0:
                continue
            distance_sq = 0.0
            for axis_index in range(target_dim):
                q = query_matrix[query_row, axis_index]
                low_delta = cell_min_matrix[cell_index, axis_index] - q
                high_delta = q - cell_max_matrix[cell_index, axis_index]
                outside_delta = 0.0
                if low_delta > outside_delta:
                    outside_delta = low_delta
                if high_delta > outside_delta:
                    outside_delta = high_delta
                distance_sq += outside_delta * outside_delta
            cell_id = cell_ids[cell_index]
            if (
                distance_sq < best_mbr_distance_sq
                or (distance_sq == best_mbr_distance_sq and cell_id < best_cell_id)
            ):
                best_mbr_distance_sq = distance_sq
                best_cell_id = cell_id
                best_cell_index = cell_index

        begin = begins[best_cell_index]
        count = counts[best_cell_index]
        best_point_distance_sq = np.inf
        best_point_id = np.int64(9223372036854775807)
        for offset in range(count):
            target_row = point_row_indices[begin + offset]
            distance_sq = 0.0
            for axis_index in range(target_dim):
                delta = query_matrix[query_row, axis_index] - target_matrix[target_row, axis_index]
                distance_sq += delta * delta
            target_id = target_ids[target_row]
            if (
                distance_sq < best_point_distance_sq
                or (distance_sq == best_point_distance_sq and target_id < best_point_id)
            ):
                best_point_distance_sq = distance_sq
                best_point_id = target_id

        best_distances[query_row] = np.sqrt(best_point_distance_sq)
        best_item_ids[query_row] = best_point_id
        seed_cell_ids[query_row] = best_cell_id
        seed_cell_point_counts[query_row] = count

    return best_distances, best_item_ids, seed_cell_ids, seed_cell_point_counts


if _numba_njit is not None:
    _seed_nearest_witness_parallel_loop_impl = _numba_njit(cache=True, parallel=True)(
        _seed_nearest_witness_parallel_loop_impl
    )


def _encoded_grid_cell_3d(gx, gy, gz, dim_y, dim_z):
    return (gx * dim_y + gy) * dim_z + gz


def _lower_bound_i64(sorted_values, value):
    lo = 0
    hi = sorted_values.shape[0]
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_values[mid] < value:
            lo = mid + 1
        else:
            hi = mid
    return lo


def _seed_nearest_witness_grid_local_3d_parallel_impl(
    query_matrix,
    target_matrix,
    target_ids,
    cell_ids,
    original_cell_ids,
    dense_cell_positions,
    grid_shape,
    grid_lower_bounds,
    grid_upper_bounds,
    begins,
    counts,
    point_row_indices,
):
    query_count = query_matrix.shape[0]
    dim_x = int(grid_shape[0])
    dim_y = int(grid_shape[1])
    dim_z = int(grid_shape[2])
    extent_x = grid_upper_bounds[0] - grid_lower_bounds[0]
    extent_y = grid_upper_bounds[1] - grid_lower_bounds[1]
    extent_z = grid_upper_bounds[2] - grid_lower_bounds[2]
    step_x = 0.0 if extent_x == 0.0 else extent_x / dim_x
    step_y = 0.0 if extent_y == 0.0 else extent_y / dim_y
    step_z = 0.0 if extent_z == 0.0 else extent_z / dim_z
    max_radius = dim_x
    if dim_y > max_radius:
        max_radius = dim_y
    if dim_z > max_radius:
        max_radius = dim_z

    best_distances = np.empty(query_count, dtype=np.float64)
    best_item_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_point_counts = np.empty(query_count, dtype=np.int64)
    grid_cell_probe_counts = np.empty(query_count, dtype=np.int64)

    for query_row in _numba_prange(query_count):
        qx = query_matrix[query_row, 0]
        qy = query_matrix[query_row, 1]
        qz = query_matrix[query_row, 2]
        if extent_x == 0.0:
            base_x = 0
        else:
            base_x = int(np.floor((qx - grid_lower_bounds[0]) / extent_x * dim_x))
            if base_x < 0:
                base_x = 0
            if base_x >= dim_x:
                base_x = dim_x - 1
        if extent_y == 0.0:
            base_y = 0
        else:
            base_y = int(np.floor((qy - grid_lower_bounds[1]) / extent_y * dim_y))
            if base_y < 0:
                base_y = 0
            if base_y >= dim_y:
                base_y = dim_y - 1
        if extent_z == 0.0:
            base_z = 0
        else:
            base_z = int(np.floor((qz - grid_lower_bounds[2]) / extent_z * dim_z))
            if base_z < 0:
                base_z = 0
            if base_z >= dim_z:
                base_z = dim_z - 1

        best_cell_index = -1
        best_cell_id = np.int64(9223372036854775807)
        best_grid_distance_sq = np.inf
        probes = np.int64(0)
        found = False
        for radius in range(max_radius + 1):
            for dx in range(-radius, radius + 1):
                gx = base_x + dx
                if gx < 0 or gx >= dim_x:
                    continue
                abs_dx = dx if dx >= 0 else -dx
                for dy in range(-radius, radius + 1):
                    gy = base_y + dy
                    if gy < 0 or gy >= dim_y:
                        continue
                    abs_dy = dy if dy >= 0 else -dy
                    for dz in range(-radius, radius + 1):
                        gz = base_z + dz
                        if gz < 0 or gz >= dim_z:
                            continue
                        abs_dz = dz if dz >= 0 else -dz
                        shell = abs_dx
                        if abs_dy > shell:
                            shell = abs_dy
                        if abs_dz > shell:
                            shell = abs_dz
                        if shell != radius:
                            continue
                        probes += 1
                        encoded = _encoded_grid_cell_3d(gx, gy, gz, dim_y, dim_z)
                        if dense_cell_positions.shape[0] > 0:
                            pos = dense_cell_positions[encoded]
                            if pos < 0:
                                continue
                        else:
                            pos = _lower_bound_i64(original_cell_ids, encoded)
                            if pos >= original_cell_ids.shape[0] or original_cell_ids[pos] != encoded:
                                continue
                        if counts[pos] <= 0:
                            continue

                        low_x = grid_lower_bounds[0] if step_x == 0.0 else grid_lower_bounds[0] + gx * step_x
                        high_x = grid_lower_bounds[0] if step_x == 0.0 else grid_lower_bounds[0] + (gx + 1) * step_x
                        low_y = grid_lower_bounds[1] if step_y == 0.0 else grid_lower_bounds[1] + gy * step_y
                        high_y = grid_lower_bounds[1] if step_y == 0.0 else grid_lower_bounds[1] + (gy + 1) * step_y
                        low_z = grid_lower_bounds[2] if step_z == 0.0 else grid_lower_bounds[2] + gz * step_z
                        high_z = grid_lower_bounds[2] if step_z == 0.0 else grid_lower_bounds[2] + (gz + 1) * step_z

                        distance_sq = 0.0
                        if qx < low_x:
                            delta = low_x - qx
                            distance_sq += delta * delta
                        elif qx > high_x:
                            delta = qx - high_x
                            distance_sq += delta * delta
                        if qy < low_y:
                            delta = low_y - qy
                            distance_sq += delta * delta
                        elif qy > high_y:
                            delta = qy - high_y
                            distance_sq += delta * delta
                        if qz < low_z:
                            delta = low_z - qz
                            distance_sq += delta * delta
                        elif qz > high_z:
                            delta = qz - high_z
                            distance_sq += delta * delta

                        cell_id = cell_ids[pos]
                        if distance_sq < best_grid_distance_sq or (
                            distance_sq == best_grid_distance_sq and cell_id < best_cell_id
                        ):
                            best_grid_distance_sq = distance_sq
                            best_cell_id = cell_id
                            best_cell_index = pos
                            found = True
            if found:
                break

        if best_cell_index < 0:
            best_cell_index = 0
            best_cell_id = cell_ids[0]

        begin = begins[best_cell_index]
        count = counts[best_cell_index]
        best_point_distance_sq = np.inf
        best_point_id = np.int64(9223372036854775807)
        for offset in range(count):
            target_row = point_row_indices[begin + offset]
            dx = qx - target_matrix[target_row, 0]
            dy = qy - target_matrix[target_row, 1]
            dz = qz - target_matrix[target_row, 2]
            distance_sq = dx * dx + dy * dy + dz * dz
            target_id = target_ids[target_row]
            if distance_sq < best_point_distance_sq or (
                distance_sq == best_point_distance_sq and target_id < best_point_id
            ):
                best_point_distance_sq = distance_sq
                best_point_id = target_id

        best_distances[query_row] = np.sqrt(best_point_distance_sq)
        best_item_ids[query_row] = best_point_id
        seed_cell_ids[query_row] = best_cell_id
        seed_cell_point_counts[query_row] = count
        grid_cell_probe_counts[query_row] = probes

    return best_distances, best_item_ids, seed_cell_ids, seed_cell_point_counts, grid_cell_probe_counts


def _seed_nearest_witness_grid_branch_bound_3d_parallel_impl(
    query_matrix,
    target_matrix,
    target_ids,
    cell_ids,
    original_cell_ids,
    dense_cell_positions,
    grid_shape,
    grid_lower_bounds,
    grid_upper_bounds,
    begins,
    counts,
    point_row_indices,
):
    query_count = query_matrix.shape[0]
    dim_x = int(grid_shape[0])
    dim_y = int(grid_shape[1])
    dim_z = int(grid_shape[2])
    extent_x = grid_upper_bounds[0] - grid_lower_bounds[0]
    extent_y = grid_upper_bounds[1] - grid_lower_bounds[1]
    extent_z = grid_upper_bounds[2] - grid_lower_bounds[2]
    step_x = 0.0 if extent_x == 0.0 else extent_x / dim_x
    step_y = 0.0 if extent_y == 0.0 else extent_y / dim_y
    step_z = 0.0 if extent_z == 0.0 else extent_z / dim_z
    max_radius = dim_x
    if dim_y > max_radius:
        max_radius = dim_y
    if dim_z > max_radius:
        max_radius = dim_z

    best_distances = np.empty(query_count, dtype=np.float64)
    best_item_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_point_counts = np.empty(query_count, dtype=np.int64)
    grid_cell_probe_counts = np.empty(query_count, dtype=np.int64)
    scanned_cell_counts = np.empty(query_count, dtype=np.int64)
    scanned_point_counts = np.empty(query_count, dtype=np.int64)
    shell_counts = np.empty(query_count, dtype=np.int64)

    for query_row in _numba_prange(query_count):
        qx = query_matrix[query_row, 0]
        qy = query_matrix[query_row, 1]
        qz = query_matrix[query_row, 2]
        if extent_x == 0.0:
            base_x = 0
        else:
            base_x = int(np.floor((qx - grid_lower_bounds[0]) / extent_x * dim_x))
            if base_x < 0:
                base_x = 0
            if base_x >= dim_x:
                base_x = dim_x - 1
        if extent_y == 0.0:
            base_y = 0
        else:
            base_y = int(np.floor((qy - grid_lower_bounds[1]) / extent_y * dim_y))
            if base_y < 0:
                base_y = 0
            if base_y >= dim_y:
                base_y = dim_y - 1
        if extent_z == 0.0:
            base_z = 0
        else:
            base_z = int(np.floor((qz - grid_lower_bounds[2]) / extent_z * dim_z))
            if base_z < 0:
                base_z = 0
            if base_z >= dim_z:
                base_z = dim_z - 1

        best_point_distance_sq = np.inf
        best_point_id = np.int64(9223372036854775807)
        best_cell_id = np.int64(-1)
        best_cell_point_count = np.int64(0)
        probes = np.int64(0)
        scanned_cells = np.int64(0)
        scanned_points = np.int64(0)
        shells = np.int64(0)

        for radius in range(max_radius + 1):
            shell_min_grid_distance_sq = np.inf
            shells = radius + 1
            for dx in range(-radius, radius + 1):
                gx = base_x + dx
                if gx < 0 or gx >= dim_x:
                    continue
                abs_dx = dx if dx >= 0 else -dx
                for dy in range(-radius, radius + 1):
                    gy = base_y + dy
                    if gy < 0 or gy >= dim_y:
                        continue
                    abs_dy = dy if dy >= 0 else -dy
                    for dz in range(-radius, radius + 1):
                        gz = base_z + dz
                        if gz < 0 or gz >= dim_z:
                            continue
                        abs_dz = dz if dz >= 0 else -dz
                        shell = abs_dx
                        if abs_dy > shell:
                            shell = abs_dy
                        if abs_dz > shell:
                            shell = abs_dz
                        if shell != radius:
                            continue
                        probes += 1

                        low_x = grid_lower_bounds[0] if step_x == 0.0 else grid_lower_bounds[0] + gx * step_x
                        high_x = grid_lower_bounds[0] if step_x == 0.0 else grid_lower_bounds[0] + (gx + 1) * step_x
                        low_y = grid_lower_bounds[1] if step_y == 0.0 else grid_lower_bounds[1] + gy * step_y
                        high_y = grid_lower_bounds[1] if step_y == 0.0 else grid_lower_bounds[1] + (gy + 1) * step_y
                        low_z = grid_lower_bounds[2] if step_z == 0.0 else grid_lower_bounds[2] + gz * step_z
                        high_z = grid_lower_bounds[2] if step_z == 0.0 else grid_lower_bounds[2] + (gz + 1) * step_z

                        grid_distance_sq = 0.0
                        if qx < low_x:
                            delta = low_x - qx
                            grid_distance_sq += delta * delta
                        elif qx > high_x:
                            delta = qx - high_x
                            grid_distance_sq += delta * delta
                        if qy < low_y:
                            delta = low_y - qy
                            grid_distance_sq += delta * delta
                        elif qy > high_y:
                            delta = qy - high_y
                            grid_distance_sq += delta * delta
                        if qz < low_z:
                            delta = low_z - qz
                            grid_distance_sq += delta * delta
                        elif qz > high_z:
                            delta = qz - high_z
                            grid_distance_sq += delta * delta
                        if grid_distance_sq < shell_min_grid_distance_sq:
                            shell_min_grid_distance_sq = grid_distance_sq
                        if grid_distance_sq > best_point_distance_sq:
                            continue

                        encoded = _encoded_grid_cell_3d(gx, gy, gz, dim_y, dim_z)
                        if dense_cell_positions.shape[0] > 0:
                            pos = dense_cell_positions[encoded]
                            if pos < 0:
                                continue
                        else:
                            pos = _lower_bound_i64(original_cell_ids, encoded)
                            if pos >= original_cell_ids.shape[0] or original_cell_ids[pos] != encoded:
                                continue
                        count = counts[pos]
                        if count <= 0:
                            continue
                        scanned_cells += 1
                        scanned_points += count
                        begin = begins[pos]
                        for offset in range(count):
                            target_row = point_row_indices[begin + offset]
                            ddx = qx - target_matrix[target_row, 0]
                            ddy = qy - target_matrix[target_row, 1]
                            ddz = qz - target_matrix[target_row, 2]
                            distance_sq = ddx * ddx + ddy * ddy + ddz * ddz
                            target_id = target_ids[target_row]
                            if distance_sq < best_point_distance_sq or (
                                distance_sq == best_point_distance_sq and target_id < best_point_id
                            ):
                                best_point_distance_sq = distance_sq
                                best_point_id = target_id
                                best_cell_id = cell_ids[pos]
                                best_cell_point_count = count
            if best_point_id >= 0 and shell_min_grid_distance_sq > best_point_distance_sq:
                break

        if best_point_id == np.int64(9223372036854775807):
            pos = 0
            begin = begins[pos]
            count = counts[pos]
            for offset in range(count):
                target_row = point_row_indices[begin + offset]
                ddx = qx - target_matrix[target_row, 0]
                ddy = qy - target_matrix[target_row, 1]
                ddz = qz - target_matrix[target_row, 2]
                distance_sq = ddx * ddx + ddy * ddy + ddz * ddz
                target_id = target_ids[target_row]
                if distance_sq < best_point_distance_sq or (
                    distance_sq == best_point_distance_sq and target_id < best_point_id
                ):
                    best_point_distance_sq = distance_sq
                    best_point_id = target_id
                    best_cell_id = cell_ids[pos]
                    best_cell_point_count = count
            scanned_cells += 1
            scanned_points += count

        best_distances[query_row] = np.sqrt(best_point_distance_sq)
        best_item_ids[query_row] = best_point_id
        seed_cell_ids[query_row] = best_cell_id
        seed_cell_point_counts[query_row] = best_cell_point_count
        grid_cell_probe_counts[query_row] = probes
        scanned_cell_counts[query_row] = scanned_cells
        scanned_point_counts[query_row] = scanned_points
        shell_counts[query_row] = shells

    return (
        best_distances,
        best_item_ids,
        seed_cell_ids,
        seed_cell_point_counts,
        grid_cell_probe_counts,
        scanned_cell_counts,
        scanned_point_counts,
        shell_counts,
    )


def _seed_nearest_witness_grid_cell_budget_3d_parallel_impl(
    query_matrix,
    target_matrix,
    target_ids,
    cell_ids,
    original_cell_ids,
    dense_cell_positions,
    grid_shape,
    grid_lower_bounds,
    grid_upper_bounds,
    begins,
    counts,
    point_row_indices,
    max_scanned_cells_per_query,
):
    query_count = query_matrix.shape[0]
    dim_x = int(grid_shape[0])
    dim_y = int(grid_shape[1])
    dim_z = int(grid_shape[2])
    extent_x = grid_upper_bounds[0] - grid_lower_bounds[0]
    extent_y = grid_upper_bounds[1] - grid_lower_bounds[1]
    extent_z = grid_upper_bounds[2] - grid_lower_bounds[2]
    step_x = 0.0 if extent_x == 0.0 else extent_x / dim_x
    step_y = 0.0 if extent_y == 0.0 else extent_y / dim_y
    step_z = 0.0 if extent_z == 0.0 else extent_z / dim_z
    max_radius = dim_x
    if dim_y > max_radius:
        max_radius = dim_y
    if dim_z > max_radius:
        max_radius = dim_z

    best_distances = np.empty(query_count, dtype=np.float64)
    best_item_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_ids = np.empty(query_count, dtype=np.int64)
    seed_cell_point_counts = np.empty(query_count, dtype=np.int64)
    grid_cell_probe_counts = np.empty(query_count, dtype=np.int64)
    scanned_cell_counts = np.empty(query_count, dtype=np.int64)
    scanned_point_counts = np.empty(query_count, dtype=np.int64)
    shell_counts = np.empty(query_count, dtype=np.int64)

    for query_row in _numba_prange(query_count):
        qx = query_matrix[query_row, 0]
        qy = query_matrix[query_row, 1]
        qz = query_matrix[query_row, 2]
        if extent_x == 0.0:
            base_x = 0
        else:
            base_x = int(np.floor((qx - grid_lower_bounds[0]) / extent_x * dim_x))
            if base_x < 0:
                base_x = 0
            if base_x >= dim_x:
                base_x = dim_x - 1
        if extent_y == 0.0:
            base_y = 0
        else:
            base_y = int(np.floor((qy - grid_lower_bounds[1]) / extent_y * dim_y))
            if base_y < 0:
                base_y = 0
            if base_y >= dim_y:
                base_y = dim_y - 1
        if extent_z == 0.0:
            base_z = 0
        else:
            base_z = int(np.floor((qz - grid_lower_bounds[2]) / extent_z * dim_z))
            if base_z < 0:
                base_z = 0
            if base_z >= dim_z:
                base_z = dim_z - 1

        best_point_distance_sq = np.inf
        best_point_id = np.int64(9223372036854775807)
        best_cell_id = np.int64(-1)
        best_cell_point_count = np.int64(0)
        probes = np.int64(0)
        scanned_cells = np.int64(0)
        scanned_points = np.int64(0)
        shells = np.int64(0)

        stop = False
        for radius in range(max_radius + 1):
            if stop:
                break
            shell_min_grid_distance_sq = np.inf
            shells = radius + 1
            for dx in range(-radius, radius + 1):
                if stop:
                    break
                gx = base_x + dx
                if gx < 0 or gx >= dim_x:
                    continue
                abs_dx = dx if dx >= 0 else -dx
                for dy in range(-radius, radius + 1):
                    if stop:
                        break
                    gy = base_y + dy
                    if gy < 0 or gy >= dim_y:
                        continue
                    abs_dy = dy if dy >= 0 else -dy
                    for dz in range(-radius, radius + 1):
                        gz = base_z + dz
                        if gz < 0 or gz >= dim_z:
                            continue
                        abs_dz = dz if dz >= 0 else -dz
                        shell = abs_dx
                        if abs_dy > shell:
                            shell = abs_dy
                        if abs_dz > shell:
                            shell = abs_dz
                        if shell != radius:
                            continue
                        probes += 1

                        low_x = grid_lower_bounds[0] if step_x == 0.0 else grid_lower_bounds[0] + gx * step_x
                        high_x = grid_lower_bounds[0] if step_x == 0.0 else grid_lower_bounds[0] + (gx + 1) * step_x
                        low_y = grid_lower_bounds[1] if step_y == 0.0 else grid_lower_bounds[1] + gy * step_y
                        high_y = grid_lower_bounds[1] if step_y == 0.0 else grid_lower_bounds[1] + (gy + 1) * step_y
                        low_z = grid_lower_bounds[2] if step_z == 0.0 else grid_lower_bounds[2] + gz * step_z
                        high_z = grid_lower_bounds[2] if step_z == 0.0 else grid_lower_bounds[2] + (gz + 1) * step_z

                        grid_distance_sq = 0.0
                        if qx < low_x:
                            delta = low_x - qx
                            grid_distance_sq += delta * delta
                        elif qx > high_x:
                            delta = qx - high_x
                            grid_distance_sq += delta * delta
                        if qy < low_y:
                            delta = low_y - qy
                            grid_distance_sq += delta * delta
                        elif qy > high_y:
                            delta = qy - high_y
                            grid_distance_sq += delta * delta
                        if qz < low_z:
                            delta = low_z - qz
                            grid_distance_sq += delta * delta
                        elif qz > high_z:
                            delta = qz - high_z
                            grid_distance_sq += delta * delta
                        if grid_distance_sq < shell_min_grid_distance_sq:
                            shell_min_grid_distance_sq = grid_distance_sq
                        if grid_distance_sq > best_point_distance_sq:
                            continue

                        encoded = _encoded_grid_cell_3d(gx, gy, gz, dim_y, dim_z)
                        if dense_cell_positions.shape[0] > 0:
                            pos = dense_cell_positions[encoded]
                            if pos < 0:
                                continue
                        else:
                            pos = _lower_bound_i64(original_cell_ids, encoded)
                            if pos >= original_cell_ids.shape[0] or original_cell_ids[pos] != encoded:
                                continue
                        count = counts[pos]
                        if count <= 0:
                            continue
                        scanned_cells += 1
                        scanned_points += count
                        begin = begins[pos]
                        for offset in range(count):
                            target_row = point_row_indices[begin + offset]
                            ddx = qx - target_matrix[target_row, 0]
                            ddy = qy - target_matrix[target_row, 1]
                            ddz = qz - target_matrix[target_row, 2]
                            distance_sq = ddx * ddx + ddy * ddy + ddz * ddz
                            target_id = target_ids[target_row]
                            if distance_sq < best_point_distance_sq or (
                                distance_sq == best_point_distance_sq and target_id < best_point_id
                            ):
                                best_point_distance_sq = distance_sq
                                best_point_id = target_id
                                best_cell_id = cell_ids[pos]
                                best_cell_point_count = count
                        if scanned_cells >= max_scanned_cells_per_query:
                            stop = True
                            break
            if best_point_id >= 0 and shell_min_grid_distance_sq > best_point_distance_sq:
                break

        if best_point_id == np.int64(9223372036854775807):
            pos = 0
            begin = begins[pos]
            count = counts[pos]
            for offset in range(count):
                target_row = point_row_indices[begin + offset]
                ddx = qx - target_matrix[target_row, 0]
                ddy = qy - target_matrix[target_row, 1]
                ddz = qz - target_matrix[target_row, 2]
                distance_sq = ddx * ddx + ddy * ddy + ddz * ddz
                target_id = target_ids[target_row]
                if distance_sq < best_point_distance_sq or (
                    distance_sq == best_point_distance_sq and target_id < best_point_id
                ):
                    best_point_distance_sq = distance_sq
                    best_point_id = target_id
                    best_cell_id = cell_ids[pos]
                    best_cell_point_count = count
            scanned_cells += 1
            scanned_points += count

        best_distances[query_row] = np.sqrt(best_point_distance_sq)
        best_item_ids[query_row] = best_point_id
        seed_cell_ids[query_row] = best_cell_id
        seed_cell_point_counts[query_row] = best_cell_point_count
        grid_cell_probe_counts[query_row] = probes
        scanned_cell_counts[query_row] = scanned_cells
        scanned_point_counts[query_row] = scanned_points
        shell_counts[query_row] = shells

    return (
        best_distances,
        best_item_ids,
        seed_cell_ids,
        seed_cell_point_counts,
        grid_cell_probe_counts,
        scanned_cell_counts,
        scanned_point_counts,
        shell_counts,
    )


if _numba_njit is not None:
    _encoded_grid_cell_3d = _numba_njit(cache=True)(_encoded_grid_cell_3d)
    _lower_bound_i64 = _numba_njit(cache=True)(_lower_bound_i64)
    _seed_nearest_witness_grid_local_3d_parallel_impl = _numba_njit(cache=True, parallel=True)(
        _seed_nearest_witness_grid_local_3d_parallel_impl
    )
    _seed_nearest_witness_grid_branch_bound_3d_parallel_impl = _numba_njit(cache=True, parallel=True)(
        _seed_nearest_witness_grid_branch_bound_3d_parallel_impl
    )
    _seed_nearest_witness_grid_cell_budget_3d_parallel_impl = _numba_njit(cache=True, parallel=True)(
        _seed_nearest_witness_grid_cell_budget_3d_parallel_impl
    )


def _nearest_witness_from_frontier_loop_impl(
    query_matrix,
    target_matrix,
    target_ids,
    point_row_indices,
    kind_codes,
    query_row_ids,
    begins,
    counts,
    best_distances,
    best_item_ids,
    pruned_kind_code,
):
    used_frontier_rows = 0
    candidate_evaluations = 0
    target_dim = target_matrix.shape[1]
    best_distance_sq = np.empty(best_distances.shape[0], dtype=np.float64)
    for query_row in range(best_distances.shape[0]):
        best_distance_sq[query_row] = best_distances[query_row] * best_distances[query_row]

    for row_index in range(kind_codes.shape[0]):
        if kind_codes[row_index] == pruned_kind_code:
            continue
        used_frontier_rows += 1
        query_row = query_row_ids[row_index]
        begin = begins[row_index]
        count = counts[row_index]
        for offset in range(count):
            candidate_evaluations += 1
            target_row = point_row_indices[begin + offset]
            distance_sq = 0.0
            for axis_index in range(target_dim):
                delta = query_matrix[query_row, axis_index] - target_matrix[target_row, axis_index]
                distance_sq += delta * delta
            target_id = target_ids[target_row]
            current_item_id = best_item_ids[query_row]
            if current_item_id < 0:
                best_distances[query_row] = np.sqrt(distance_sq)
                best_distance_sq[query_row] = distance_sq
                best_item_ids[query_row] = target_id
            else:
                if (
                    distance_sq < best_distance_sq[query_row]
                    or (distance_sq == best_distance_sq[query_row] and target_id < current_item_id)
                ):
                    best_distances[query_row] = np.sqrt(distance_sq)
                    best_distance_sq[query_row] = distance_sq
                    best_item_ids[query_row] = target_id

    return best_distances, best_item_ids, candidate_evaluations, used_frontier_rows


if _numba_njit is not None:
    _nearest_witness_from_frontier_loop_impl = _numba_njit(cache=True)(_nearest_witness_from_frontier_loop_impl)


def _nearest_witness_from_frontier_parallel_by_query_loop_impl(
    query_matrix,
    target_matrix,
    target_ids,
    point_row_indices,
    sorted_frontier_row_indices,
    group_starts,
    group_ends,
    query_row_ids,
    begins,
    counts,
    best_distances,
    best_item_ids,
):
    target_dim = target_matrix.shape[1]
    for group_index in _numba_prange(group_starts.shape[0]):
        start = group_starts[group_index]
        end = group_ends[group_index]
        first_row_index = sorted_frontier_row_indices[start]
        query_row = query_row_ids[first_row_index]
        current_item_id = best_item_ids[query_row]
        best_distance_sq = best_distances[query_row] * best_distances[query_row]
        best_item_id = current_item_id

        for order_index in range(start, end):
            row_index = sorted_frontier_row_indices[order_index]
            begin = begins[row_index]
            count = counts[row_index]
            for offset in range(count):
                target_row = point_row_indices[begin + offset]
                distance_sq = 0.0
                for axis_index in range(target_dim):
                    delta = query_matrix[query_row, axis_index] - target_matrix[target_row, axis_index]
                    distance_sq += delta * delta
                target_id = target_ids[target_row]
                if best_item_id < 0:
                    best_distance_sq = distance_sq
                    best_item_id = target_id
                elif distance_sq < best_distance_sq or (
                    distance_sq == best_distance_sq and target_id < best_item_id
                ):
                    best_distance_sq = distance_sq
                    best_item_id = target_id

        if best_item_id >= 0:
            best_distances[query_row] = np.sqrt(best_distance_sq)
            best_item_ids[query_row] = best_item_id

    return best_distances, best_item_ids


if _numba_njit is not None:
    _nearest_witness_from_frontier_parallel_by_query_loop_impl = _numba_njit(cache=True, parallel=True)(
        _nearest_witness_from_frontier_parallel_by_query_loop_impl
    )


def _validate_group_count(group_count: int) -> int:
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    return group_count


def numpy_segmented_count(keys, group_count: int) -> np.ndarray:
    """Count rows per integer key with deterministic NumPy semantics."""

    keys = _as_i64(keys, "keys")
    group_count = _validate_group_count(group_count)
    if keys.size == 0:
        return np.zeros(group_count, dtype=np.int64)
    if np.any(keys < 0) or np.any(keys >= group_count):
        raise ValueError("keys must be in [0, group_count)")
    return np.bincount(keys, minlength=group_count).astype(np.int64, copy=False)


def numpy_segmented_sum(keys, values, group_count: int) -> np.ndarray:
    """Sum values per integer key with deterministic NumPy semantics."""

    keys = _as_i64(keys, "keys")
    values = _as_f64(values, "values")
    group_count = _validate_group_count(group_count)
    if keys.shape != values.shape:
        raise ValueError("keys and values must have the same shape")
    if keys.size == 0:
        return np.zeros(group_count, dtype=np.float64)
    if np.any(keys < 0) or np.any(keys >= group_count):
        raise ValueError("keys must be in [0, group_count)")
    return np.bincount(keys, weights=values, minlength=group_count).astype(np.float64, copy=False)


def numpy_segmented_minmax(keys, values, group_count: int, *, reduce: str) -> np.ndarray:
    """Compute per-key min or max values."""

    if reduce not in {"min", "max"}:
        raise ValueError("reduce must be 'min' or 'max'")
    keys = _as_i64(keys, "keys")
    values = _as_f64(values, "values")
    group_count = _validate_group_count(group_count)
    if keys.shape != values.shape:
        raise ValueError("keys and values must have the same shape")
    initial = np.inf if reduce == "min" else -np.inf
    out = np.full(group_count, initial, dtype=np.float64)
    if keys.size == 0:
        return out
    if np.any(keys < 0) or np.any(keys >= group_count):
        raise ValueError("keys must be in [0, group_count)")
    reducer = np.minimum.at if reduce == "min" else np.maximum.at
    reducer(out, keys, values)
    return out


def numpy_group_topk(
    group_ids,
    item_ids,
    scores,
    *,
    group_count: int,
    k: int,
    largest: bool = False,
) -> dict[str, np.ndarray]:
    """Return deterministic top-k rows per group.

    Tie-break is `score` then `item_id`, ascending for nearest/smallest scores
    and descending score then ascending item id for largest scores.
    """

    group_ids = _as_i64(group_ids, "group_ids")
    item_ids = _as_i64(item_ids, "item_ids")
    scores = _as_f64(scores, "scores")
    group_count = _validate_group_count(group_count)
    k = int(k)
    if k <= 0:
        raise ValueError("k must be positive")
    if not (group_ids.shape == item_ids.shape == scores.shape):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    if group_ids.size and (np.any(group_ids < 0) or np.any(group_ids >= group_count)):
        raise ValueError("group_ids must be in [0, group_count)")

    if group_ids.size == 0:
        return {
            "group_ids": np.asarray([], dtype=np.int64),
            "item_ids": np.asarray([], dtype=np.int64),
            "scores": np.asarray([], dtype=np.float64),
            "rank": np.asarray([], dtype=np.int64),
        }

    primary = -scores if largest else scores
    order = np.lexsort((item_ids, primary, group_ids))
    sorted_group_ids = group_ids[order]
    starts = np.empty(sorted_group_ids.size, dtype=np.bool_)
    starts[0] = True
    starts[1:] = sorted_group_ids[1:] != sorted_group_ids[:-1]
    positions = np.arange(sorted_group_ids.size, dtype=np.int64)
    group_starts = np.maximum.accumulate(np.where(starts, positions, 0))
    ranks = positions - group_starts + 1
    keep = ranks <= k
    selected = order[keep]
    return {
        "group_ids": group_ids[selected].astype(np.int64, copy=False),
        "item_ids": item_ids[selected].astype(np.int64, copy=False),
        "scores": scores[selected].astype(np.float64, copy=False),
        "rank": ranks[keep].astype(np.int64, copy=False),
    }


def numpy_group_argmin_then_global_argmax_with_witness(
    group_ids,
    item_ids,
    values,
    *,
    group_count: int,
) -> dict[str, object]:
    """Compute per-group argmin, then global argmax over those minima."""

    top1 = numpy_group_topk(
        group_ids,
        item_ids,
        values,
        group_count=group_count,
        k=1,
        largest=False,
    )
    if top1["group_ids"].size != group_count:
        missing = sorted(set(range(group_count)) - set(int(v) for v in top1["group_ids"]))
        raise ValueError(f"every group must have at least one candidate; missing groups: {missing}")
    order = np.lexsort((top1["item_ids"], top1["group_ids"], -top1["scores"]))
    winner = int(order[0])
    return {
        "group_id": int(top1["group_ids"][winner]),
        "item_id": int(top1["item_ids"][winner]),
        "value": float(top1["scores"][winner]),
        "per_group_argmin": top1,
        "contract": "generic_group_argmin_then_global_argmax_with_witness",
    }


def point_rows_to_numpy_columns(points) -> dict[str, np.ndarray]:
    rows = tuple(points)
    return {
        "ids": np.asarray([int(point.id) for point in rows], dtype=np.int64),
        "x": np.asarray([float(point.x) for point in rows], dtype=np.float64),
        "y": np.asarray([float(point.y) for point in rows], dtype=np.float64),
    }


def point_rows_to_numpy_columns_3d(points) -> dict[str, np.ndarray]:
    rows = tuple(points)
    return {
        "ids": np.asarray([int(point.id) for point in rows], dtype=np.int64),
        "x": np.asarray([float(point.x) for point in rows], dtype=np.float64),
        "y": np.asarray([float(point.y) for point in rows], dtype=np.float64),
        "z": np.asarray([float(point.z) for point in rows], dtype=np.float64),
    }


def _normalize_coordinate_fields(coordinate_fields) -> tuple[str, ...]:
    fields = tuple(str(field) for field in coordinate_fields)
    if not fields:
        raise ValueError("coordinate_fields must contain at least one coordinate column")
    if len(set(fields)) != len(fields):
        raise ValueError("coordinate_fields must not contain duplicates")
    return fields


def _point_columns_for_fields(
    point_columns: Mapping[str, object],
    *,
    coordinate_fields: tuple[str, ...],
    label: str,
) -> tuple[np.ndarray, tuple[np.ndarray, ...]]:
    ids = _as_i64(point_columns["ids"], f"{label} ids")
    coordinates = tuple(_as_f64(point_columns[field], f"{label} {field}") for field in coordinate_fields)
    if not all(ids.shape == coordinate.shape for coordinate in coordinates):
        joined = "/".join(("ids", *coordinate_fields))
        raise ValueError(f"{label} {joined} must have the same shape")
    return ids, coordinates


def _point_matrix_for_fields(
    point_columns: Mapping[str, object],
    *,
    coordinate_fields: tuple[str, ...],
    label: str,
) -> tuple[np.ndarray, tuple[np.ndarray, ...], np.ndarray, bool]:
    ids, coordinates = _point_columns_for_fields(
        point_columns,
        coordinate_fields=coordinate_fields,
        label=label,
    )
    matrix = point_columns.get("coordinate_matrix")
    matrix_fields = tuple(str(field) for field in point_columns.get("coordinate_matrix_fields", ()))
    if matrix is not None and matrix_fields == tuple(coordinate_fields):
        matrix_arr = np.asarray(matrix, dtype=np.float64)
        if matrix_arr.ndim != 2 or matrix_arr.shape != (ids.size, len(coordinate_fields)):
            raise ValueError(
                f"{label} coordinate_matrix must have shape "
                f"[point_count, {len(coordinate_fields)}]"
            )
        matrix_matches_columns = all(
            np.shares_memory(matrix_arr[:, axis], coordinates[axis])
            for axis in range(len(coordinate_fields))
        ) or all(
            np.array_equal(matrix_arr[:, axis], coordinates[axis])
            for axis in range(len(coordinate_fields))
        )
        if not matrix_matches_columns:
            raise ValueError(f"{label} coordinate_matrix does not match coordinate columns")
        if matrix_arr.flags.c_contiguous:
            return ids, coordinates, matrix_arr, True
        return ids, coordinates, np.ascontiguousarray(matrix_arr, dtype=np.float64), False
    return ids, coordinates, np.ascontiguousarray(np.column_stack(coordinates), dtype=np.float64), False


def pairwise_l2_distance_candidate_rows_numpy_columns(
    source_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    *,
    coordinate_fields=("x", "y"),
    squared: bool = False,
    return_metadata: bool = False,
):
    """Materialize generic pairwise L2 candidate rows from point columns.

    This helper emits a backend-neutral candidate row table that downstream
    grouped reductions can consume. It carries no application identity.
    """

    fields = _normalize_coordinate_fields(coordinate_fields)
    source_ids, source_coordinates = _point_columns_for_fields(
        source_point_columns,
        coordinate_fields=fields,
        label="source",
    )
    target_ids, target_coordinates = _point_columns_for_fields(
        target_point_columns,
        coordinate_fields=fields,
        label="target",
    )
    if source_ids.size == 0 or target_ids.size == 0:
        raise ValueError("pairwise L2 candidate rows require non-empty source and target columns")

    distance_sq = np.zeros((source_ids.size, target_ids.size), dtype=np.float64)
    for source_axis, target_axis in zip(source_coordinates, target_coordinates):
        delta = source_axis.reshape(-1, 1) - target_axis.reshape(1, -1)
        distance_sq += delta * delta
    values = distance_sq.reshape(-1) if squared else np.sqrt(distance_sq).reshape(-1)
    candidate_rows = PartnerCandidateRows(
        query_ids=np.repeat(np.arange(source_ids.size, dtype=np.int64), target_ids.size),
        primitive_ids=np.tile(target_ids, source_ids.size),
        values=values,
    ).normalized()
    metadata = {
        "adapter": "pairwise_l2_distance_candidate_rows_numpy_columns",
        "partner": "numpy",
        "contract": "generic_pairwise_l2_distance_candidate_rows",
        "coordinate_fields": fields,
        "source_count": int(source_ids.size),
        "target_count": int(target_ids.size),
        "row_count": int(values.size),
        "distance_value": "squared_l2" if squared else "l2",
        "app_semantics": "none",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    result = {
        "candidate_rows": candidate_rows,
        "source_ids": source_ids,
        "target_ids": target_ids,
    }
    if return_metadata:
        result["metadata"] = metadata
    return result


def nearest_witness_numpy_columns(
    candidate_rows: PartnerCandidateRows,
    source_ids,
    *,
    group_count: int | None = None,
    return_metadata: bool = False,
):
    """Reduce generic candidate rows to the nearest witness per source row."""

    rows = candidate_rows.normalized()
    if rows.values is None:
        raise ValueError("candidate_rows.values is required for nearest witness reduction")
    source_ids = _as_i64(source_ids, "source ids")
    if group_count is None:
        group_count = int(source_ids.size)
    group_count = _validate_group_count(group_count)
    if source_ids.size != group_count:
        raise ValueError("source_ids length must match group_count")
    top1 = numpy_group_topk(
        rows.query_ids,
        rows.primitive_ids,
        rows.values,
        group_count=group_count,
        k=1,
        largest=False,
    )
    if top1["group_ids"].size != group_count:
        missing = sorted(set(range(group_count)) - set(int(v) for v in top1["group_ids"]))
        raise ValueError(f"every group must have at least one candidate; missing groups: {missing}")
    order = np.argsort(top1["group_ids"], kind="stable")
    sorted_top1 = {
        "group_ids": top1["group_ids"][order].astype(np.int64, copy=False),
        "item_ids": top1["item_ids"][order].astype(np.int64, copy=False),
        "scores": top1["scores"][order].astype(np.float64, copy=False),
        "rank": top1["rank"][order].astype(np.int64, copy=False),
    }
    columns = {
        "source_ids": source_ids,
        "nearest_item_ids": sorted_top1["item_ids"],
        "nearest_distances": sorted_top1["scores"],
    }
    metadata = {
        "adapter": "nearest_witness_numpy_columns",
        "partner": "numpy",
        "contract": "generic_nearest_witness_columns",
        "source_count": int(source_ids.size),
        "candidate_row_count": int(rows.query_ids.size),
        "app_semantics": "none",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    result = {"columns": columns, "per_group_argmin": sorted_top1}
    if return_metadata:
        result["metadata"] = metadata
    return result


def max_nearest_distance_witness_numpy_columns(
    nearest_columns: Mapping[str, object],
    *,
    group_ids=None,
    return_metadata: bool = False,
):
    """Return the row with the maximum nearest-distance value.

    This is a generic max-over-nearest reduction. Applications may interpret
    the witness differently, but the function itself carries no app identity.
    """

    source_ids = _as_i64(nearest_columns["source_ids"], "source ids")
    if "nearest_item_ids" in nearest_columns:
        item_values = nearest_columns["nearest_item_ids"]
    else:
        item_values = nearest_columns["nearest_target_ids"]
    item_ids = _as_i64(item_values, "nearest item ids")
    distances = _as_f64(nearest_columns["nearest_distances"], "nearest distances")
    if not (source_ids.shape == item_ids.shape == distances.shape):
        raise ValueError("source_ids, nearest item ids, and nearest_distances must have the same shape")
    if source_ids.size == 0:
        raise ValueError("max nearest-distance witness requires at least one nearest row")
    if group_ids is None:
        group_ids = np.arange(source_ids.size, dtype=np.int64)
    group_ids = _as_i64(group_ids, "group ids")
    if group_ids.shape != source_ids.shape:
        raise ValueError("group_ids must have the same shape as nearest rows")
    reduction_strategy = "finite_max_then_tie_lexsort"
    tie_candidate_count = 0
    if np.all(np.isfinite(distances)):
        max_distance = float(np.max(distances))
        candidates = np.flatnonzero(distances == max_distance)
        tie_candidate_count = int(candidates.size)
        if candidates.size == 1:
            winner = int(candidates[0])
        else:
            tie_order = np.lexsort((item_ids[candidates], group_ids[candidates]))
            winner = int(candidates[int(tie_order[0])])
    else:
        reduction_strategy = "full_lexsort_nonfinite_fallback"
        order = np.lexsort((item_ids, group_ids, -distances))
        winner = int(order[0])
        tie_candidate_count = int(source_ids.size)
    result = {
        "source_index": int(group_ids[winner]),
        "source_id": int(source_ids[winner]),
        "item_id": int(item_ids[winner]),
        "value": float(distances[winner]),
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "max_nearest_distance_witness_numpy_columns",
            "partner": "numpy",
            "contract": "generic_max_nearest_distance_with_witness",
            "row_count": int(source_ids.size),
            "reduction_strategy": reduction_strategy,
            "tie_candidate_count": tie_candidate_count,
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def _normalize_grid_shape(grid_shape, dimension: int) -> tuple[int, ...]:
    shape = tuple(int(value) for value in grid_shape)
    if len(shape) != int(dimension):
        raise ValueError("grid_shape length must match coordinate dimension")
    if any(value <= 0 for value in shape):
        raise ValueError("grid_shape entries must be positive")
    return shape


def _aabb_distance_sq(point: tuple[float, ...], mins: tuple[float, ...], maxs: tuple[float, ...]) -> tuple[float, float]:
    min_dist_sq = 0.0
    max_dist_sq = 0.0
    for value, lower, upper in zip(point, mins, maxs):
        if value < lower:
            delta = lower - value
        elif value > upper:
            delta = value - upper
        else:
            delta = 0.0
        min_dist_sq += delta * delta
        far_delta = max(abs(value - lower), abs(value - upper))
        max_dist_sq += far_delta * far_delta
    return min_dist_sq, max_dist_sq


def point_grid_cell_mbrs_numpy_columns(
    point_columns: Mapping[str, object],
    *,
    coordinate_fields=("x", "y", "z"),
    grid_shape,
    cell_point_order: str = "point-id",
    return_metadata: bool = False,
):
    """Build generic point-grid cells with tight per-cell MBR columns.

    This reference front door is intentionally app-neutral. It groups points
    into a caller-selected rectilinear grid and emits compact cell descriptors
    that downstream traversal or candidate-generation routes can consume.
    """

    fields = _normalize_coordinate_fields(coordinate_fields)
    grid_shape = _normalize_grid_shape(grid_shape, len(fields))
    point_ids, coordinates = _point_columns_for_fields(
        point_columns,
        coordinate_fields=fields,
        label="point",
    )
    if point_ids.size == 0:
        raise ValueError("point grid cell MBRs require at least one point")

    coord_matrix = np.column_stack(coordinates)
    lower_bounds = coord_matrix.min(axis=0)
    upper_bounds = coord_matrix.max(axis=0)
    extents = upper_bounds - lower_bounds
    cell_positions = []
    for axis, axis_values in enumerate(coordinates):
        if extents[axis] == 0.0:
            position = np.zeros(point_ids.size, dtype=np.int64)
        else:
            normalized = (axis_values - lower_bounds[axis]) / extents[axis]
            position = np.floor(normalized * grid_shape[axis]).astype(np.int64)
            position = np.clip(position, 0, grid_shape[axis] - 1)
        cell_positions.append(position)

    encoded = np.zeros(point_ids.size, dtype=np.int64)
    for axis, position in enumerate(cell_positions):
        if axis == 0:
            encoded = position.astype(np.int64, copy=True)
        else:
            encoded = encoded * int(grid_shape[axis]) + position

    if cell_point_order == "point-id":
        order = np.lexsort((point_ids, encoded))
        point_order_contract = "cell_id_then_point_id"
    elif cell_point_order == "input-stable":
        order = np.argsort(encoded, kind="stable")
        point_order_contract = "cell_id_then_input_order"
    else:
        raise ValueError("cell_point_order must be 'point-id' or 'input-stable'")
    sorted_encoded = encoded[order]
    sorted_point_ids = point_ids[order]
    sorted_row_indices = order.astype(np.int64, copy=False)
    unique_encoded, begin_offsets, counts = np.unique(
        sorted_encoded,
        return_index=True,
        return_counts=True,
    )
    compact_cell_ids = np.arange(unique_encoded.size, dtype=np.int64)

    cell_columns: dict[str, np.ndarray] = {
        "cell_ids": compact_cell_ids,
        "original_cell_ids": unique_encoded.astype(np.int64, copy=False),
        "point_begin_offsets": begin_offsets.astype(np.int64, copy=False),
        "point_counts": counts.astype(np.int64, copy=False),
        "point_ids": sorted_point_ids.astype(np.int64, copy=False),
        "point_row_indices": sorted_row_indices,
        "grid_shape": np.asarray(grid_shape, dtype=np.int64),
        "grid_lower_bounds": lower_bounds.astype(np.float64, copy=False),
        "grid_upper_bounds": upper_bounds.astype(np.float64, copy=False),
    }
    reduce_offsets = begin_offsets.astype(np.int64, copy=False)
    for axis, field in enumerate(fields):
        sorted_axis = np.asarray(coordinates[axis], dtype=np.float64)[order]
        cell_columns[f"min_{field}"] = np.minimum.reduceat(sorted_axis, reduce_offsets)
        cell_columns[f"max_{field}"] = np.maximum.reduceat(sorted_axis, reduce_offsets)

    result = {"cell_columns": cell_columns}
    if return_metadata:
        result["metadata"] = {
            "adapter": "point_grid_cell_mbrs_numpy_columns",
            "partner": "numpy",
            "contract": "generic_point_grid_cell_mbr_columns",
            "coordinate_fields": fields,
            "grid_shape": grid_shape,
            "point_count": int(point_ids.size),
            "cell_count": int(unique_encoded.size),
            "cell_id_contract": "compact_zero_based_with_original_cell_ids",
            "cell_mbr_contract": "tight_mbr_over_points_in_cell",
            "cell_mbr_reduction": "numpy_reduceat",
            "cell_point_order": cell_point_order,
            "cell_point_order_contract": point_order_contract,
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def point_grid_cell_mbrs_native_3d_cuda_columns(
    point_columns: Mapping[str, object],
    *,
    coordinate_fields=("x", "y", "z"),
    grid_shape,
    cell_point_order: str = "point-id",
    return_metadata: bool = False,
):
    """Build generic 3-D point-grid cell MBR columns with native CUDA/Thrust.

    This is an app-neutral alternative backend for
    :func:`point_grid_cell_mbrs_numpy_columns`. It preserves the same column
    contract and is selected explicitly by callers that want to test the native
    path.
    """

    fields = _normalize_coordinate_fields(coordinate_fields)
    if len(fields) != 3:
        raise ValueError("native CUDA point-grid MBR builder currently supports exactly 3 coordinate fields")
    grid_shape = _normalize_grid_shape(grid_shape, len(fields))
    point_ids, coordinates = _point_columns_for_fields(
        point_columns,
        coordinate_fields=fields,
        label="point",
    )
    if point_ids.size == 0:
        raise ValueError("point grid cell MBRs require at least one point")
    coord_matrix = np.ascontiguousarray(np.column_stack(coordinates), dtype=np.float64)
    lower_bounds = coord_matrix.min(axis=0)
    upper_bounds = coord_matrix.max(axis=0)
    from .optix_runtime import point_grid_cell_mbrs_3d_cuda

    result = point_grid_cell_mbrs_3d_cuda(
        coords=coord_matrix,
        point_ids=point_ids,
        grid_shape=np.asarray(grid_shape, dtype=np.int64),
        grid_lower_bounds=lower_bounds,
        grid_upper_bounds=upper_bounds,
        cell_point_order=cell_point_order,
    )
    if return_metadata:
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "adapter": "point_grid_cell_mbrs_native_3d_cuda_columns",
                "coordinate_fields": fields,
            }
        )
        result["metadata"] = metadata
    else:
        result = {"cell_columns": result["cell_columns"]}
    return result


def radius_cell_mbr_candidate_rows_numpy_columns(
    query_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    radius: float,
    coordinate_fields=("x", "y", "z"),
    squared: bool = False,
    return_metadata: bool = False,
):
    """Emit query-to-cell candidates whose tight MBR is within `radius`.

    The candidate primitive id is the compact cell id. Values are point-to-MBR
    minimum distances, with matching max-distance columns for pruning policies.
    """

    fields = _normalize_coordinate_fields(coordinate_fields)
    radius = float(radius)
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    query_ids, query_coordinates = _point_columns_for_fields(
        query_point_columns,
        coordinate_fields=fields,
        label="query",
    )
    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    if query_ids.size == 0:
        raise ValueError("radius cell MBR candidates require at least one query point")
    if cell_ids.size == 0:
        raise ValueError("radius cell MBR candidates require at least one cell")
    cell_mins = tuple(_as_f64(cell_columns[f"min_{field}"], f"cell min_{field}") for field in fields)
    cell_maxs = tuple(_as_f64(cell_columns[f"max_{field}"], f"cell max_{field}") for field in fields)
    if not all(cell_ids.shape == axis.shape for axis in (*cell_mins, *cell_maxs)):
        raise ValueError("cell ids and cell MBR columns must have the same shape")

    radius_sq = radius * radius
    out_query_row_ids: list[int] = []
    out_cell_ids: list[int] = []
    out_min_dist_sq: list[float] = []
    out_max_dist_sq: list[float] = []
    for query_index in range(int(query_ids.size)):
        point = tuple(float(axis[query_index]) for axis in query_coordinates)
        for cell_index in range(int(cell_ids.size)):
            mins = tuple(float(axis[cell_index]) for axis in cell_mins)
            maxs = tuple(float(axis[cell_index]) for axis in cell_maxs)
            min_dist_sq, max_dist_sq = _aabb_distance_sq(point, mins, maxs)
            if min_dist_sq <= radius_sq:
                out_query_row_ids.append(query_index)
                out_cell_ids.append(int(cell_ids[cell_index]))
                out_min_dist_sq.append(min_dist_sq)
                out_max_dist_sq.append(max_dist_sq)

    min_distances_sq = np.asarray(out_min_dist_sq, dtype=np.float64)
    max_distances_sq = np.asarray(out_max_dist_sq, dtype=np.float64)
    if squared:
        values = min_distances_sq
        min_values = min_distances_sq
        max_values = max_distances_sq
        distance_value = "squared_l2_to_cell_mbr"
    else:
        values = np.sqrt(min_distances_sq)
        min_values = values
        max_values = np.sqrt(max_distances_sq)
        distance_value = "l2_to_cell_mbr"
    candidate_rows = PartnerCandidateRows(
        query_ids=np.asarray(out_query_row_ids, dtype=np.int64),
        primitive_ids=np.asarray(out_cell_ids, dtype=np.int64),
        values=values,
    ).normalized()
    columns = {
        "query_point_ids": query_ids[candidate_rows.query_ids],
        "query_row_ids": candidate_rows.query_ids,
        "cell_ids": candidate_rows.primitive_ids,
        "min_distances": min_values,
        "max_distances": max_values,
    }
    result = {"candidate_rows": candidate_rows, "columns": columns}
    if return_metadata:
        result["metadata"] = {
            "adapter": "radius_cell_mbr_candidate_rows_numpy_columns",
            "partner": "numpy",
            "contract": "generic_radius_cell_mbr_candidate_rows",
            "coordinate_fields": fields,
            "query_count": int(query_ids.size),
            "cell_count": int(cell_ids.size),
            "candidate_row_count": int(candidate_rows.query_ids.size),
            "radius": radius,
            "distance_value": distance_value,
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def _cell_count_lookup(cell_columns: Mapping[str, object]) -> dict[int, tuple[int, int, int]]:
    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    begin_offsets = _as_i64(cell_columns["point_begin_offsets"], "point begin offsets")
    point_counts = _as_i64(cell_columns["point_counts"], "point counts")
    if not (cell_ids.shape == begin_offsets.shape == point_counts.shape):
        raise ValueError("cell ids, point_begin_offsets, and point_counts must have the same shape")
    return {
        int(cell_id): (int(index), int(begin_offsets[index]), int(point_counts[index]))
        for index, cell_id in enumerate(cell_ids)
    }


def _frontier_columns_from_candidate_indices(
    *,
    candidate_columns: Mapping[str, np.ndarray],
    candidate_indices: list[int],
    cell_lookup: Mapping[int, tuple[int, int, int]],
) -> dict[str, np.ndarray]:
    query_row_ids = _as_i64(candidate_columns["query_row_ids"], "candidate query_row_ids")
    query_point_ids = _as_i64(candidate_columns["query_point_ids"], "candidate query_point_ids")
    cell_ids = _as_i64(candidate_columns["cell_ids"], "candidate cell_ids")
    min_distances = _as_f64(candidate_columns["min_distances"], "candidate min_distances")
    max_distances = _as_f64(candidate_columns["max_distances"], "candidate max_distances")
    indices = np.asarray(candidate_indices, dtype=np.int64)
    if indices.size == 0:
        return {
            "query_row_ids": np.asarray([], dtype=np.int64),
            "query_point_ids": np.asarray([], dtype=np.int64),
            "cell_ids": np.asarray([], dtype=np.int64),
            "point_begin_offsets": np.asarray([], dtype=np.int64),
            "point_counts": np.asarray([], dtype=np.int64),
            "min_distances": np.asarray([], dtype=np.float64),
            "max_distances": np.asarray([], dtype=np.float64),
        }
    selected_cell_ids = cell_ids[indices]
    begins: list[int] = []
    counts: list[int] = []
    for cell_id in selected_cell_ids:
        _, begin, count = cell_lookup[int(cell_id)]
        begins.append(begin)
        counts.append(count)
    return {
        "query_row_ids": query_row_ids[indices].astype(np.int64, copy=False),
        "query_point_ids": query_point_ids[indices].astype(np.int64, copy=False),
        "cell_ids": selected_cell_ids.astype(np.int64, copy=False),
        "point_begin_offsets": np.asarray(begins, dtype=np.int64),
        "point_counts": np.asarray(counts, dtype=np.int64),
        "min_distances": min_distances[indices].astype(np.float64, copy=False),
        "max_distances": max_distances[indices].astype(np.float64, copy=False),
    }


def nearest_state_frontier_from_cell_candidates_numpy_columns(
    candidate_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    query_point_ids,
    current_best_distances=None,
    current_best_item_ids=None,
    max_inline_points: int,
    return_metadata: bool = False,
):
    """Split cell candidates into generic inline/offload/pruned frontiers.

    This contract models the state carried by a nearest-neighbor traversal
    without applying an application-specific distance law. Candidate cells whose
    MBR lower bound cannot beat the current best distance are pruned. Remaining
    cells are split by point count so a caller can handle small cells inline and
    send large cells to a continuation/offload path.
    """

    query_point_ids = _as_i64(query_point_ids, "query point ids")
    if query_point_ids.size == 0:
        raise ValueError("query_point_ids must be non-empty")
    max_inline_points = int(max_inline_points)
    if max_inline_points < 0:
        raise ValueError("max_inline_points must be non-negative")

    query_row_ids = _as_i64(candidate_columns["query_row_ids"], "candidate query_row_ids")
    candidate_query_point_ids = _as_i64(candidate_columns["query_point_ids"], "candidate query_point_ids")
    candidate_cell_ids = _as_i64(candidate_columns["cell_ids"], "candidate cell_ids")
    min_distances = _as_f64(candidate_columns["min_distances"], "candidate min_distances")
    max_distances = _as_f64(candidate_columns["max_distances"], "candidate max_distances")
    if not (
        query_row_ids.shape
        == candidate_query_point_ids.shape
        == candidate_cell_ids.shape
        == min_distances.shape
        == max_distances.shape
    ):
        raise ValueError("candidate columns must have matching shapes")
    if query_row_ids.size and (np.any(query_row_ids < 0) or np.any(query_row_ids >= query_point_ids.size)):
        raise ValueError("candidate query_row_ids must index query_point_ids")
    if query_row_ids.size:
        expected_query_ids = query_point_ids[query_row_ids]
        if not np.array_equal(expected_query_ids, candidate_query_point_ids):
            raise ValueError("candidate query_point_ids must match query_point_ids[query_row_ids]")

    if current_best_distances is None:
        best_distances = np.full(query_point_ids.size, np.inf, dtype=np.float64)
    else:
        best_distances = _as_f64(current_best_distances, "current best distances")
        if best_distances.shape != query_point_ids.shape:
            raise ValueError("current_best_distances must have the same shape as query_point_ids")
    if current_best_item_ids is None:
        best_item_ids = np.full(query_point_ids.size, -1, dtype=np.int64)
    else:
        best_item_ids = _as_i64(current_best_item_ids, "current best item ids")
        if best_item_ids.shape != query_point_ids.shape:
            raise ValueError("current_best_item_ids must have the same shape as query_point_ids")

    cell_lookup = _cell_count_lookup(cell_columns)
    inline_indices: list[int] = []
    offload_indices: list[int] = []
    pruned_indices: list[int] = []
    unknown_cell_ids: set[int] = set()
    for candidate_index in range(int(query_row_ids.size)):
        query_index = int(query_row_ids[candidate_index])
        cell_id = int(candidate_cell_ids[candidate_index])
        if cell_id not in cell_lookup:
            unknown_cell_ids.add(cell_id)
            continue
        _, _, point_count = cell_lookup[cell_id]
        if float(min_distances[candidate_index]) >= float(best_distances[query_index]):
            pruned_indices.append(candidate_index)
        elif point_count > max_inline_points:
            offload_indices.append(candidate_index)
        else:
            inline_indices.append(candidate_index)
    if unknown_cell_ids:
        missing = sorted(unknown_cell_ids)
        raise ValueError(f"candidate cell_ids missing from cell_columns: {missing}")

    candidate_view = {
        "query_row_ids": query_row_ids,
        "query_point_ids": candidate_query_point_ids,
        "cell_ids": candidate_cell_ids,
        "min_distances": min_distances,
        "max_distances": max_distances,
    }
    inline_frontier = _frontier_columns_from_candidate_indices(
        candidate_columns=candidate_view,
        candidate_indices=inline_indices,
        cell_lookup=cell_lookup,
    )
    offload_frontier = _frontier_columns_from_candidate_indices(
        candidate_columns=candidate_view,
        candidate_indices=offload_indices,
        cell_lookup=cell_lookup,
    )
    pruned_frontier = _frontier_columns_from_candidate_indices(
        candidate_columns=candidate_view,
        candidate_indices=pruned_indices,
        cell_lookup=cell_lookup,
    )

    state = {
        "query_point_ids": query_point_ids,
        "current_best_distances": best_distances,
        "current_best_item_ids": best_item_ids,
    }
    result = {
        "nearest_state": state,
        "inline_frontier": inline_frontier,
        "offload_frontier": offload_frontier,
        "pruned_frontier": pruned_frontier,
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "nearest_state_frontier_from_cell_candidates_numpy_columns",
            "partner": "numpy",
            "contract": "generic_nearest_state_cell_frontier",
            "query_count": int(query_point_ids.size),
            "candidate_row_count": int(query_row_ids.size),
            "inline_frontier_row_count": int(len(inline_indices)),
            "offload_frontier_row_count": int(len(offload_indices)),
            "pruned_frontier_row_count": int(len(pruned_indices)),
            "max_inline_points": max_inline_points,
            "prune_rule": "candidate_min_distance >= current_best_distance",
            "offload_rule": "cell_point_count > max_inline_points",
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def cell_mbr_nearest_frontier_aabb_membership_2d_numpy_columns(
    query_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    radius: float,
    current_best_distances=None,
    current_best_item_ids=None,
    max_inline_points: int,
    row_capacity: int | None = None,
    broadphase_row_capacity: int | None = None,
    backend: str = "cpu",
    resolution: int = 32,
    return_metadata: bool = False,
):
    """Build Goal5140 frontier rows from a generic 2-D AABB membership backend.

    This is a backend-assisted front door: broadphase cell candidates may come
    from CPU/OptiX/Embree AABB membership rows, while exact point-to-MBR distance
    filtering and nearest-state frontier classification remain in this generic
    NumPy layer.
    """

    radius = float(radius)
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    query_ids, query_coordinates = _point_columns_for_fields(
        query_point_columns,
        coordinate_fields=("x", "y"),
        label="query",
    )
    if query_ids.size == 0:
        raise ValueError("query point columns must be non-empty")
    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    if cell_ids.size == 0:
        raise ValueError("cell columns must contain at least one cell")
    min_x = _as_f64(cell_columns["min_x"], "cell min_x")
    min_y = _as_f64(cell_columns["min_y"], "cell min_y")
    max_x = _as_f64(cell_columns["max_x"], "cell max_x")
    max_y = _as_f64(cell_columns["max_y"], "cell max_y")
    if not (cell_ids.shape == min_x.shape == min_y.shape == max_x.shape == max_y.shape):
        raise ValueError("cell ids and 2-D MBR columns must have the same shape")

    box_records = tuple(
        (
            float(min_x[index]),
            float(min_y[index]),
            float(max_x[index]),
            float(max_y[index]),
        )
        for index in range(int(cell_ids.size))
    )
    point_records = tuple(
        (float(query_coordinates[0][index]), float(query_coordinates[1][index]))
        for index in range(int(query_ids.size))
    )
    id_to_query_row = {int(query_id): int(index) for index, query_id in enumerate(query_ids)}
    cell_lookup = _cell_count_lookup(cell_columns)
    cell_mbr_lookup = {
        int(cell_ids[index]): (
            float(min_x[index]),
            float(min_y[index]),
            float(max_x[index]),
            float(max_y[index]),
        )
        for index in range(int(cell_ids.size))
    }
    resolved_broadphase_capacity = (
        int(query_ids.size) * int(cell_ids.size)
        if broadphase_row_capacity is None
        else int(broadphase_row_capacity)
    )
    if resolved_broadphase_capacity < 0:
        raise ValueError("broadphase_row_capacity must be non-negative")

    from .aabb_index import expanded_aabb_point_membership_rows_2d

    membership = expanded_aabb_point_membership_rows_2d(
        box_records,
        point_records,
        expansions=radius,
        indexed_ids=cell_ids.tolist(),
        source_ids=query_ids.tolist(),
        row_capacity=resolved_broadphase_capacity,
        resolution=resolution,
        backend=backend,
    )

    radius_sq = radius * radius
    out_query_row_ids: list[int] = []
    out_query_point_ids: list[int] = []
    out_cell_ids: list[int] = []
    out_min_distances: list[float] = []
    out_max_distances: list[float] = []
    for source_id, cell_id, _metadata_flags in membership["candidate_id_rows"]:
        query_row = id_to_query_row[int(source_id)]
        point = (
            float(query_coordinates[0][query_row]),
            float(query_coordinates[1][query_row]),
        )
        mins_maxs = cell_mbr_lookup[int(cell_id)]
        min_dist_sq, max_dist_sq = _aabb_distance_sq(
            point,
            (mins_maxs[0], mins_maxs[1]),
            (mins_maxs[2], mins_maxs[3]),
        )
        if min_dist_sq <= radius_sq:
            out_query_row_ids.append(query_row)
            out_query_point_ids.append(int(source_id))
            out_cell_ids.append(int(cell_id))
            out_min_distances.append(float(np.sqrt(min_dist_sq)))
            out_max_distances.append(float(np.sqrt(max_dist_sq)))

    candidate_columns = {
        "query_row_ids": np.asarray(out_query_row_ids, dtype=np.int64),
        "query_point_ids": np.asarray(out_query_point_ids, dtype=np.int64),
        "cell_ids": np.asarray(out_cell_ids, dtype=np.int64),
        "min_distances": np.asarray(out_min_distances, dtype=np.float64),
        "max_distances": np.asarray(out_max_distances, dtype=np.float64),
    }
    frontier = nearest_state_frontier_from_cell_candidates_numpy_columns(
        candidate_columns,
        cell_columns,
        query_point_ids=query_ids,
        current_best_distances=current_best_distances,
        current_best_item_ids=current_best_item_ids,
        max_inline_points=max_inline_points,
        return_metadata=True,
    )
    table = cell_mbr_frontiers_to_row_table_numpy_columns(
        frontier,
        return_metadata=True,
    )
    final_count = int(table["columns"]["frontier_kind_codes"].size)
    if row_capacity is not None and final_count > int(row_capacity):
        raise RuntimeError(
            "cell-MBR nearest frontier row output overflowed; "
            f"attempted {final_count}; capacity {int(row_capacity)}; "
            "failure_mode=fail_closed_overflow; partial_result_returned=False"
        )
    result = {
        "nearest_state": frontier["nearest_state"],
        "inline_frontier": frontier["inline_frontier"],
        "offload_frontier": frontier["offload_frontier"],
        "pruned_frontier": frontier["pruned_frontier"],
        "row_table": table,
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "cell_mbr_nearest_frontier_aabb_membership_2d_numpy_columns",
            "partner": "numpy",
            "contract": "generic_cell_mbr_nearest_frontier_aabb_membership_2d",
            "native_abi_contract": CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT,
            "traversal_backend": str(backend).lower(),
            "broadphase_contract": membership["contract"],
            "broadphase_native_symbol": membership.get("native_generic_symbol"),
            "query_count": int(query_ids.size),
            "cell_count": int(cell_ids.size),
            "broadphase_row_count": int(membership["valid_count"]),
            "exact_candidate_row_count": int(candidate_columns["query_row_ids"].size),
            "row_count": final_count,
            "row_capacity": None if row_capacity is None else int(row_capacity),
            "broadphase_row_capacity": resolved_broadphase_capacity,
            "max_inline_points": int(max_inline_points),
            "distance_filter": "exact_point_to_cell_mbr_min_distance_lte_radius",
            "state_split_contract": "generic_nearest_state_cell_frontier",
            "row_table_contract": "generic_cell_mbr_nearest_frontier_row_table",
            "app_semantics": "none",
            "native_engine_row_contract": (
                "backend_assisted_aabb_membership_plus_numpy_frontier_classification"
            ),
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def _cpu_expanded_aabb_point_membership_rows(
    *,
    query_ids: np.ndarray,
    query_coordinates: tuple[np.ndarray, ...],
    cell_ids: np.ndarray,
    cell_mins: tuple[np.ndarray, ...],
    cell_maxs: tuple[np.ndarray, ...],
    radius: float,
) -> tuple[tuple[int, int, int], ...]:
    rows: list[tuple[int, int, int]] = []
    for query_index in range(int(query_ids.size)):
        point = tuple(float(axis[query_index]) for axis in query_coordinates)
        for cell_index in range(int(cell_ids.size)):
            inside = True
            for dimension in range(len(query_coordinates)):
                if point[dimension] < float(cell_mins[dimension][cell_index]) - radius:
                    inside = False
                    break
                if point[dimension] > float(cell_maxs[dimension][cell_index]) + radius:
                    inside = False
                    break
            if inside:
                rows.append((int(query_ids[query_index]), int(cell_ids[cell_index]), 0))
    return tuple(rows)


def cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns(
    query_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    radius: float,
    current_best_distances=None,
    current_best_item_ids=None,
    max_inline_points: int,
    row_capacity: int | None = None,
    broadphase_row_capacity: int | None = None,
    backend: str = "cpu",
    return_metadata: bool = False,
):
    """Build Goal5140 frontier rows from a generic 3-D AABB membership backend.

    The broadphase can use CPU rows or the native OptiX 3-D AABB
    point-membership producer. Exact point-to-MBR distance filtering and
    nearest-state frontier classification remain in this app-neutral NumPy
    layer.
    """

    radius = float(radius)
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    query_ids, query_coordinates, query_coords, query_coordinate_matrix_reused = _point_matrix_for_fields(
        query_point_columns,
        coordinate_fields=("x", "y", "z"),
        label="query",
    )
    if query_ids.size == 0:
        raise ValueError("query point columns must be non-empty")
    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    if cell_ids.size == 0:
        raise ValueError("cell columns must contain at least one cell")
    cell_mins = tuple(_as_f64(cell_columns[f"min_{axis}"], f"cell min_{axis}") for axis in ("x", "y", "z"))
    cell_maxs = tuple(_as_f64(cell_columns[f"max_{axis}"], f"cell max_{axis}") for axis in ("x", "y", "z"))
    if not all(cell_ids.shape == axis.shape for axis in (*cell_mins, *cell_maxs)):
        raise ValueError("cell ids and 3-D MBR columns must have the same shape")

    resolved_broadphase_capacity = (
        int(query_ids.size) * int(cell_ids.size)
        if broadphase_row_capacity is None
        else int(broadphase_row_capacity)
    )
    if resolved_broadphase_capacity < 0:
        raise ValueError("broadphase_row_capacity must be non-negative")

    backend_name = str(backend).lower()
    if backend_name == "cpu":
        membership_rows = _cpu_expanded_aabb_point_membership_rows(
            query_ids=query_ids,
            query_coordinates=query_coordinates,
            cell_ids=cell_ids,
            cell_mins=cell_mins,
            cell_maxs=cell_maxs,
            radius=radius,
        )
        if len(membership_rows) > resolved_broadphase_capacity:
            raise RuntimeError(
                "3-D AABB membership broadphase overflowed; "
                f"attempted {len(membership_rows)}; capacity {resolved_broadphase_capacity}; "
                "failure_mode=fail_closed_overflow; partial_result_returned=False"
            )
        membership = {
            "contract": "generic_expanded_aabb_point_membership_rows_3d_v1",
            "backend": "cpu",
            "candidate_id_rows": membership_rows,
            "valid_count": len(membership_rows),
            "row_capacity": resolved_broadphase_capacity,
            "native_generic_symbol": None,
        }
    elif backend_name == "optix":
        expanded_boxes = tuple(
            (
                int(cell_ids[index]),
                float(cell_mins[0][index]) - radius,
                float(cell_mins[1][index]) - radius,
                float(cell_mins[2][index]) - radius,
                float(cell_maxs[0][index]) + radius,
                float(cell_maxs[1][index]) + radius,
                float(cell_maxs[2][index]) + radius,
            )
            for index in range(int(cell_ids.size))
        )
        point_records = tuple(
            (
                int(query_ids[index]),
                float(query_coordinates[0][index]),
                float(query_coordinates[1][index]),
                float(query_coordinates[2][index]),
            )
            for index in range(int(query_ids.size))
        )
        from .optix_runtime import collect_aabb_point_membership_pair_rows_3d_optix

        membership = collect_aabb_point_membership_pair_rows_3d_optix(
            expanded_boxes,
            point_records,
            row_capacity=resolved_broadphase_capacity,
        )
    else:
        raise ValueError("3-D AABB membership backend must be 'cpu' or 'optix'")

    id_to_query_row = {int(query_id): int(index) for index, query_id in enumerate(query_ids)}
    cell_mbr_lookup = {
        int(cell_ids[index]): (
            tuple(float(axis[index]) for axis in cell_mins),
            tuple(float(axis[index]) for axis in cell_maxs),
        )
        for index in range(int(cell_ids.size))
    }
    radius_sq = radius * radius
    out_query_row_ids: list[int] = []
    out_query_point_ids: list[int] = []
    out_cell_ids: list[int] = []
    out_min_distances: list[float] = []
    out_max_distances: list[float] = []
    for row in membership["candidate_id_rows"]:
        source_id = int(row[0])
        cell_id = int(row[1])
        query_row = id_to_query_row[source_id]
        point = tuple(float(axis[query_row]) for axis in query_coordinates)
        mins, maxs = cell_mbr_lookup[cell_id]
        min_dist_sq, max_dist_sq = _aabb_distance_sq(point, mins, maxs)
        if min_dist_sq <= radius_sq:
            out_query_row_ids.append(query_row)
            out_query_point_ids.append(source_id)
            out_cell_ids.append(cell_id)
            out_min_distances.append(float(np.sqrt(min_dist_sq)))
            out_max_distances.append(float(np.sqrt(max_dist_sq)))

    candidate_columns = {
        "query_row_ids": np.asarray(out_query_row_ids, dtype=np.int64),
        "query_point_ids": np.asarray(out_query_point_ids, dtype=np.int64),
        "cell_ids": np.asarray(out_cell_ids, dtype=np.int64),
        "min_distances": np.asarray(out_min_distances, dtype=np.float64),
        "max_distances": np.asarray(out_max_distances, dtype=np.float64),
    }
    frontier = nearest_state_frontier_from_cell_candidates_numpy_columns(
        candidate_columns,
        cell_columns,
        query_point_ids=query_ids,
        current_best_distances=current_best_distances,
        current_best_item_ids=current_best_item_ids,
        max_inline_points=max_inline_points,
        return_metadata=True,
    )
    table = cell_mbr_frontiers_to_row_table_numpy_columns(
        frontier,
        return_metadata=True,
    )
    final_count = int(table["columns"]["frontier_kind_codes"].size)
    if row_capacity is not None and final_count > int(row_capacity):
        raise RuntimeError(
            "cell-MBR nearest frontier row output overflowed; "
            f"attempted {final_count}; capacity {int(row_capacity)}; "
            "failure_mode=fail_closed_overflow; partial_result_returned=False"
        )
    explicit_capacity = row_capacity is not None
    resolved_capacity = None if row_capacity is None else int(row_capacity)
    full_capacity = int(query_ids.size) * int(_as_i64(cell_columns["cell_ids"], "cell ids").size)
    result = {
        "nearest_state": frontier["nearest_state"],
        "inline_frontier": frontier["inline_frontier"],
        "offload_frontier": frontier["offload_frontier"],
        "pruned_frontier": frontier["pruned_frontier"],
        "row_table": table,
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "cell_mbr_nearest_frontier_aabb_membership_3d_numpy_columns",
            "partner": "numpy",
            "contract": "generic_cell_mbr_nearest_frontier_aabb_membership_3d",
            "native_abi_contract": CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT,
            "traversal_backend": backend_name,
            "broadphase_contract": membership["contract"],
            "broadphase_native_symbol": membership.get("native_generic_symbol"),
            "query_count": int(query_ids.size),
            "cell_count": int(cell_ids.size),
            "broadphase_row_count": int(membership["valid_count"]),
            "exact_candidate_row_count": int(candidate_columns["query_row_ids"].size),
            "row_count": final_count,
            "row_capacity": None if row_capacity is None else int(row_capacity),
            "broadphase_row_capacity": resolved_broadphase_capacity,
            "max_inline_points": int(max_inline_points),
            "distance_filter": "exact_point_to_cell_mbr_min_distance_lte_radius",
            "state_split_contract": "generic_nearest_state_cell_frontier",
            "row_table_contract": "generic_cell_mbr_nearest_frontier_row_table",
            "app_semantics": "none",
            "native_engine_row_contract": (
                "backend_assisted_aabb_membership_plus_numpy_frontier_classification"
            ),
            "native_backend_complete": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def _frontier_from_native_row_table(columns: Mapping[str, np.ndarray], *, kind_code: int) -> dict[str, np.ndarray]:
    frontier_kind_codes = _as_i64(columns["frontier_kind_codes"], "frontier kind codes")
    mask = frontier_kind_codes == int(kind_code)
    return {
        "query_row_ids": _as_i64(columns["query_row_ids"], "query row ids")[mask],
        "query_point_ids": _as_i64(columns["query_point_ids"], "query point ids")[mask],
        "cell_ids": _as_i64(columns["cell_ids"], "cell ids")[mask],
        "point_begin_offsets": _as_i64(columns["point_begin_offsets"], "point begin offsets")[mask],
        "point_counts": _as_i64(columns["point_counts"], "point counts")[mask],
        "min_distances": _as_f64(columns["min_distances"], "min distances")[mask],
        "max_distances": _as_f64(columns["max_distances"], "max distances")[mask],
    }


def cell_mbr_nearest_frontier_native_3d_optix_columns(
    query_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    target_point_columns: Mapping[str, object] | None = None,
    radius: float,
    current_best_distances=None,
    current_best_item_ids=None,
    max_inline_points: int,
    row_capacity: int | None = None,
    emit_pruned_rows: bool = True,
    sort_rows: bool = True,
    inline_nearest: bool = False,
    collect_inline_stats: bool = False,
    global_bound_early_break: bool = False,
    frontier_status_probe_mode: str | int = "default",
    collect_native_phase_timings: bool = False,
    allow_overflow_telemetry: bool = False,
    return_split_frontiers: bool = True,
    return_metadata: bool = False,
    issue_completed_state_evidence: bool = False,
    _prepared_target_domain=None,
):
    """Build Goal5140 frontier rows with the bounded native OptiX 3-D collector."""

    radius = float(radius)
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    query_ids, query_coordinates, query_coords, query_coordinate_matrix_reused = _point_matrix_for_fields(
        query_point_columns,
        coordinate_fields=("x", "y", "z"),
        label="query",
    )
    if query_ids.size == 0:
        raise ValueError("query point columns must be non-empty")
    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    if cell_ids.size == 0:
        raise ValueError("cell columns must contain at least one cell")
    cell_mins = tuple(_as_f64(cell_columns[f"min_{axis}"], f"cell min_{axis}") for axis in ("x", "y", "z"))
    cell_maxs = tuple(_as_f64(cell_columns[f"max_{axis}"], f"cell max_{axis}") for axis in ("x", "y", "z"))
    if not all(cell_ids.shape == axis.shape for axis in (*cell_mins, *cell_maxs)):
        raise ValueError("cell ids and 3-D MBR columns must have the same shape")

    if current_best_distances is None:
        best_distances = np.full(query_ids.size, np.inf, dtype=np.float64)
    else:
        best_distances = _as_f64(current_best_distances, "current best distances")
        if best_distances.shape != query_ids.shape:
            raise ValueError("current_best_distances must have the same shape as query point ids")
    if current_best_item_ids is None:
        best_item_ids = np.full(query_ids.size, -1, dtype=np.int64)
    else:
        best_item_ids = _as_i64(current_best_item_ids, "current best item ids")
        if best_item_ids.shape != query_ids.shape:
            raise ValueError("current_best_item_ids must have the same shape as query point ids")

    full_capacity = int(query_ids.size) * int(cell_ids.size)
    explicit_capacity = row_capacity is not None
    resolved_capacity = full_capacity if row_capacity is None else int(row_capacity)
    if resolved_capacity < 0:
        raise ValueError("row_capacity must be non-negative")
    capacity_policy = "explicit" if explicit_capacity else "full_query_cell_product"
    if not explicit_capacity and not bool(emit_pruned_rows):
        resolved_capacity = min(full_capacity, max(int(query_ids.size) * 8, 1024))
        capacity_policy = "streaming_inferred_retry"

    cell_mbr_min = np.column_stack(cell_mins).astype(np.float64, copy=False)
    cell_mbr_max = np.column_stack(cell_maxs).astype(np.float64, copy=False)
    point_begin_offsets = np.asarray(cell_columns["point_begin_offsets"], dtype=np.uint64)
    point_counts = np.asarray(cell_columns["point_counts"], dtype=np.uint64)
    if point_begin_offsets.shape != cell_ids.shape or point_counts.shape != cell_ids.shape:
        raise ValueError("point_begin_offsets and point_counts must match cell ids")
    point_row_indices = np.asarray(cell_columns.get("point_row_indices", np.asarray([], dtype=np.uint64)), dtype=np.uint64)
    target_ids = None
    target_coords = None
    if inline_nearest:
        if target_point_columns is None:
            raise ValueError("target_point_columns is required when inline_nearest=True")
        target_ids, target_coordinates, target_coords, target_coordinate_matrix_reused = _point_matrix_for_fields(
            target_point_columns,
            coordinate_fields=("x", "y", "z"),
            label="target",
        )
        if target_ids.size == 0:
            raise ValueError("target_point_columns must be non-empty when inline_nearest=True")
        if point_row_indices.size == 0:
            raise ValueError("cell point_row_indices must be non-empty when inline_nearest=True")
        if np.any(point_row_indices >= target_ids.size):
            raise ValueError("cell point_row_indices must index target point columns when inline_nearest=True")
        target_coords = target_coords.astype(np.float64, copy=False)
    else:
        target_coordinate_matrix_reused = False

    from .optix_runtime import collect_cell_mbr_nearest_frontier_3d_optix

    capacity_attempts: list[int] = []
    attempt_capacity = resolved_capacity
    while True:
        capacity_attempts.append(int(attempt_capacity))
        try:
            native = collect_cell_mbr_nearest_frontier_3d_optix(
                query_coords=query_coords,
                query_point_ids=query_ids,
                cell_ids=cell_ids,
                point_begin_offsets=point_begin_offsets,
                point_counts=point_counts,
                cell_mbr_min=cell_mbr_min,
                cell_mbr_max=cell_mbr_max,
                radius=radius,
                current_best_distances=best_distances,
                current_best_item_ids=best_item_ids,
                max_inline_points=int(max_inline_points),
                row_capacity=attempt_capacity,
                emit_pruned_rows=bool(emit_pruned_rows),
                sort_rows=bool(sort_rows),
                inline_nearest=bool(inline_nearest),
                collect_inline_stats=bool(collect_inline_stats),
                global_bound_early_break=bool(global_bound_early_break),
                frontier_status_probe_mode=frontier_status_probe_mode,
                collect_native_phase_timings=bool(collect_native_phase_timings),
                allow_overflow_telemetry=bool(allow_overflow_telemetry),
                target_coords=target_coords,
                target_point_ids=target_ids,
                point_row_indices=point_row_indices,
                _prepared_target_domain=_prepared_target_domain,
            )
            resolved_capacity = int(attempt_capacity)
            break
        except RuntimeError as exc:
            message = str(exc)
            can_retry = (
                not explicit_capacity
                and not bool(emit_pruned_rows)
                and int(attempt_capacity) < int(full_capacity)
                and "overflow" in message.lower()
            )
            if not can_retry:
                raise
            attempt_capacity = min(int(full_capacity), max(int(attempt_capacity) * 2, int(attempt_capacity) + 1))
    columns = native["columns"]
    table = {"columns": columns}
    if return_metadata:
        table["metadata"] = {
            "adapter": "cell_mbr_nearest_frontier_native_3d_optix_columns.row_table",
            "partner": "optix",
            "contract": "generic_cell_mbr_nearest_frontier_row_table",
            "native_abi_contract": CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT,
            "row_schema": CELL_MBR_TRAVERSAL_ROW_SCHEMA,
            "frontier_kind_codes": dict(CELL_MBR_FRONTIER_KIND_CODES),
            "row_count": int(native["valid_count"]),
            "emit_pruned_rows": bool(emit_pruned_rows),
            "sort_rows": bool(sort_rows),
            "frontier_row_order": native.get(
                "frontier_row_order",
                "sorted_unique" if sort_rows else "native_unsorted",
            ),
            "inline_nearest": bool(inline_nearest),
            "overflowed": bool(native.get("overflowed", False)),
            "overflow_telemetry_only": bool(native.get("overflow_telemetry_only", False)),
            "overflow_failure_mode": native.get("overflow_failure_mode"),
            "app_semantics": "none",
            "query_coordinate_matrix_reused": bool(query_coordinate_matrix_reused),
            "target_coordinate_matrix_reused": bool(target_coordinate_matrix_reused),
            "native_engine_row_contract": "bounded_native_3d_optix_cell_mbr_frontier",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    nearest_state_distances = best_distances
    nearest_state_item_ids = best_item_ids
    inline_nearest_state_available = False
    if inline_nearest:
        nearest_columns = native.get("nearest_columns")
        if not isinstance(nearest_columns, Mapping):
            if not (allow_overflow_telemetry and bool(native.get("overflow_telemetry_only", False))):
                raise RuntimeError("native inline nearest result did not include nearest_columns")
        else:
            native_source_ids = _as_i64(nearest_columns["source_ids"], "inline nearest source ids")
            if native_source_ids.shape != query_ids.shape or not np.array_equal(native_source_ids, query_ids):
                raise RuntimeError("native inline nearest source ids do not match query point ids")
            nearest_state_distances = _as_f64(nearest_columns["nearest_distances"], "inline nearest distances")
            nearest_state_item_ids = _as_i64(nearest_columns["nearest_item_ids"], "inline nearest item ids")
            if nearest_state_distances.shape != query_ids.shape or nearest_state_item_ids.shape != query_ids.shape:
                raise RuntimeError("native inline nearest state arrays must match query point ids")
            inline_nearest_state_available = True

    result = {
        "nearest_state": {
            "query_point_ids": query_ids,
            "current_best_distances": nearest_state_distances,
            "current_best_item_ids": nearest_state_item_ids,
        },
        "row_table": table,
    }
    if return_split_frontiers:
        result.update(
            {
                "inline_frontier": _frontier_from_native_row_table(
                    columns,
                    kind_code=CELL_MBR_FRONTIER_KIND_CODES["inline"],
                ),
                "offload_frontier": _frontier_from_native_row_table(
                    columns,
                    kind_code=CELL_MBR_FRONTIER_KIND_CODES["offload"],
                ),
                "pruned_frontier": _frontier_from_native_row_table(
                    columns,
                    kind_code=CELL_MBR_FRONTIER_KIND_CODES["pruned"],
                ),
            }
        )
    if return_metadata:
        result["metadata"] = {
            "adapter": "cell_mbr_nearest_frontier_native_3d_optix_columns",
            "partner": "optix",
            "contract": "generic_cell_mbr_nearest_frontier_native_3d_optix",
            "native_abi_contract": CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT,
            "native_generic_symbol": native["native_generic_symbol"],
            "query_count": int(query_ids.size),
            "cell_count": int(cell_ids.size),
            "row_count": int(native["valid_count"]),
            "attempted_count": int(native["attempted_count"]),
            "row_capacity": resolved_capacity,
            "full_row_capacity": int(full_capacity),
            "row_capacity_policy": capacity_policy,
            "row_capacity_attempts": tuple(capacity_attempts),
            "allow_overflow_telemetry": bool(allow_overflow_telemetry),
            "overflowed": bool(native.get("overflowed", False)),
            "overflow_telemetry_only": bool(native.get("overflow_telemetry_only", False)),
            "overflow_failure_mode": native.get("overflow_failure_mode"),
            "radius": radius,
            "max_inline_points": int(max_inline_points),
            "emit_pruned_rows": bool(emit_pruned_rows),
            "sort_rows": bool(sort_rows),
            "frontier_row_order": native.get(
                "frontier_row_order",
                "sorted_unique" if sort_rows else "native_unsorted",
            ),
            "inline_nearest": bool(inline_nearest),
            "inline_nearest_state_available": bool(inline_nearest_state_available),
            "global_bound_early_break": bool(global_bound_early_break),
            "global_bound_early_break_count": native.get("global_bound_early_break_count"),
            "global_bound_distance": native.get("global_bound_distance"),
            "global_bound_contract": native.get("global_bound_contract"),
            "frontier_status_probe_mode": native.get("frontier_status_probe_mode"),
            "frontier_status_probe_mode_code": native.get("frontier_status_probe_mode_code"),
            "frontier_status_probe_contract": native.get("frontier_status_probe_contract"),
            "per_source_witness_exact": native.get("per_source_witness_exact"),
            "per_source_witness_exact_reason": native.get(
                "per_source_witness_exact_reason"
            ),
            "per_source_witness_exact_violations": tuple(
                native.get("per_source_witness_exact_violations") or ()
            ),
            "nearest_state_source_binding": native.get(
                "nearest_state_source_binding"
            ),
            "returned_source_ids_device_evidenced": bool(
                native.get("returned_source_ids_device_evidenced", False)
            ),
            "inline_stats_collected": bool(native.get("inline_stats_collected", False)),
            "inline_cell_hit_count": native.get("inline_cell_hit_count"),
            "inline_point_evaluation_count": native.get("inline_point_evaluation_count"),
            "native_phase_timings_collected": bool(native.get("native_phase_timings_collected", False)),
            "native_phase_timings": native.get("native_phase_timings"),
            "native_memory_telemetry_collected": bool(native.get("native_memory_telemetry_collected", False)),
            "native_memory_telemetry": native.get("native_memory_telemetry"),
            "prepared_target_domain_used": bool(
                native.get("prepared_target_domain_used", False)
            ),
            "prepared_target_domain_telemetry": native.get(
                "prepared_target_domain_telemetry"
            ),
            "status_machine_telemetry_collected": bool(
                native.get("status_machine_telemetry_collected", False)
            ),
            "status_machine_telemetry": native.get("status_machine_telemetry"),
            "inline_nearest_contract": (
                native.get("inline_nearest_contract")
                if inline_nearest
                else None
            ),
            "inline_nearest_pruning": (
                "payload_current_best_min_cell_distance_gt_best"
                if inline_nearest
                else None
            ),
            "intersection_pruning": native.get("intersection_pruning"),
            "intersection_attribute_min_distance_sq": native.get("intersection_attribute_min_distance_sq"),
            "anyhit_row_distance_computation": native.get("anyhit_row_distance_computation"),
            "split_frontiers_returned": bool(return_split_frontiers),
            "state_split_location": (
                "native_optix_anyhit_inline_nearest_and_offload_rows"
                if inline_nearest
                else "native_optix_anyhit"
            ),
            "distance_filter": "native_exact_point_to_cell_mbr_min_distance_lte_radius",
            "row_table_contract": "generic_cell_mbr_nearest_frontier_row_table",
            "app_semantics": "none",
            "query_coordinate_matrix_reused": bool(query_coordinate_matrix_reused),
            "target_coordinate_matrix_reused": bool(target_coordinate_matrix_reused),
            "native_backend_complete": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "claim_boundary": (
                "Bounded 3-D OptiX backend for generic cell-MBR frontier rows. "
                "It is not the full 2-D/3-D native ABI backend and not an "
                "application benchmark-performance claim."
            ),
        }
    if issue_completed_state_evidence:
        if not return_metadata or not inline_nearest:
            raise ValueError(
                "completed-state evidence requires inline_nearest=True and return_metadata=True"
            )
        from .action_completed_nearest_state import (
            _issue_completed_nearest_state_producer_evidence_3d,
        )

        result["_completed_nearest_state_producer_evidence"] = (
            _issue_completed_nearest_state_producer_evidence_3d(
                query_ids=query_ids,
                query_coordinates=query_coords,
                target_ids=target_ids,
                target_coordinates=target_coords,
                cell_columns=cell_columns,
                nearest_state=result["nearest_state"],
                frontier_columns=columns,
                metadata=result["metadata"],
                producer_objects=(
                    query_point_columns,
                    cell_columns,
                    target_point_columns,
                    native,
                    result["nearest_state"],
                    columns,
                ),
            )
        )
    return result


def nearest_witness_from_cell_mbr_frontier_numpy_columns(
    query_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    frontier_row_table: Mapping[str, object],
    *,
    coordinate_fields=("x", "y", "z"),
    current_best_distances=None,
    current_best_item_ids=None,
    executor: str = "auto",
    allow_missing: bool = False,
    return_metadata: bool = False,
):
    """Compute nearest witnesses by scanning point spans referenced by frontier rows."""

    fields = _normalize_coordinate_fields(coordinate_fields)
    query_ids, query_coordinates, query_matrix, query_coordinate_matrix_reused = _point_matrix_for_fields(
        query_point_columns,
        coordinate_fields=fields,
        label="query",
    )
    target_ids, target_coordinates, target_matrix, target_coordinate_matrix_reused = _point_matrix_for_fields(
        target_point_columns,
        coordinate_fields=fields,
        label="target",
    )
    if query_ids.size == 0 or target_ids.size == 0:
        raise ValueError("cell-MBR frontier nearest witness requires non-empty query and target columns")
    if current_best_distances is None:
        best_distances = np.full(query_ids.size, np.inf, dtype=np.float64)
    else:
        best_distances = _as_f64(current_best_distances, "current best distances").copy()
        if best_distances.shape != query_ids.shape:
            raise ValueError("current_best_distances must have the same shape as query point ids")
    if current_best_item_ids is None:
        best_item_ids = np.full(query_ids.size, -1, dtype=np.int64)
    else:
        best_item_ids = _as_i64(current_best_item_ids, "current best item ids").copy()
        if best_item_ids.shape != query_ids.shape:
            raise ValueError("current_best_item_ids must have the same shape as query point ids")

    table_columns = frontier_row_table.get("columns", frontier_row_table)
    kind_codes = _as_i64(table_columns["frontier_kind_codes"], "frontier kind codes")
    query_row_ids = _as_i64(table_columns["query_row_ids"], "frontier query row ids")
    begins = _as_i64(table_columns["point_begin_offsets"], "frontier point begin offsets")
    counts = _as_i64(table_columns["point_counts"], "frontier point counts")
    if not (kind_codes.shape == query_row_ids.shape == begins.shape == counts.shape):
        raise ValueError("frontier row columns must have matching shapes")
    if query_row_ids.size and (np.any(query_row_ids < 0) or np.any(query_row_ids >= query_ids.size)):
        raise ValueError("frontier query_row_ids must index query point columns")

    point_row_indices = _as_i64(cell_columns["point_row_indices"], "cell point row indices")
    if point_row_indices.size == 0:
        raise ValueError("cell point_row_indices must be non-empty")
    if np.any(point_row_indices < 0) or np.any(point_row_indices >= target_ids.size):
        raise ValueError("cell point_row_indices must index target point columns")
    if np.any(begins < 0) or np.any(counts < 0):
        raise ValueError("seed cell point span is outside cell point row indices")
    if np.any(begins + counts > point_row_indices.size):
        raise ValueError("seed cell point span is outside cell point row indices")

    allowed_kind_codes = np.asarray(
        (
            CELL_MBR_FRONTIER_KIND_CODES["inline"],
            CELL_MBR_FRONTIER_KIND_CODES["offload"],
            CELL_MBR_FRONTIER_KIND_CODES["pruned"],
        ),
        dtype=np.int64,
    )
    unsupported = kind_codes[~np.isin(kind_codes, allowed_kind_codes)]
    if unsupported.size:
        raise ValueError(f"unsupported frontier kind code: {int(unsupported[0])}")

    used_mask = kind_codes != CELL_MBR_FRONTIER_KIND_CODES["pruned"]
    used_query_rows = query_row_ids[used_mask]
    used_begins = begins[used_mask]
    used_counts = counts[used_mask]
    used_frontier_rows = int(used_query_rows.size)
    if used_frontier_rows:
        if np.any(used_begins < 0) or np.any(used_counts < 0):
            raise ValueError("frontier point span is outside cell point row indices")
        if np.any(used_begins + used_counts > point_row_indices.size):
            raise ValueError("frontier point span is outside cell point row indices")

    executor = str(executor).lower()
    if executor not in ("auto", "numpy", "numba", "numba_parallel"):
        raise ValueError("executor must be 'auto', 'numpy', 'numba', or 'numba_parallel'")
    use_numba = executor in ("auto", "numba", "numba_parallel") and _numba_njit is not None
    use_numba_parallel = executor in ("auto", "numba_parallel") and _numba_njit is not None
    if executor in ("numba", "numba_parallel") and _numba_njit is None:
        raise RuntimeError("Numba is not available for frontier nearest executor")

    if use_numba:
        query_matrix = np.ascontiguousarray(np.column_stack(query_coordinates), dtype=np.float64)
        target_matrix = np.ascontiguousarray(np.column_stack(target_coordinates), dtype=np.float64)
        if use_numba_parallel:
            candidate_evaluations = int(used_counts.sum()) if used_frontier_rows else 0
            if used_frontier_rows:
                used_row_indices = np.nonzero(used_mask)[0].astype(np.int64, copy=False)
                sorted_order = np.argsort(used_query_rows, kind="stable")
                sorted_frontier_row_indices = np.ascontiguousarray(used_row_indices[sorted_order], dtype=np.int64)
                sorted_query_rows = query_row_ids[sorted_frontier_row_indices]
                group_start_mask = np.empty(sorted_query_rows.size, dtype=bool)
                group_start_mask[0] = True
                group_start_mask[1:] = sorted_query_rows[1:] != sorted_query_rows[:-1]
                group_starts = np.ascontiguousarray(np.nonzero(group_start_mask)[0], dtype=np.int64)
                group_ends = np.empty(group_starts.shape[0], dtype=np.int64)
                if group_starts.size > 1:
                    group_ends[:-1] = group_starts[1:]
                if group_starts.size:
                    group_ends[-1] = sorted_frontier_row_indices.size
            else:
                sorted_frontier_row_indices = np.asarray([], dtype=np.int64)
                group_starts = np.asarray([], dtype=np.int64)
                group_ends = np.asarray([], dtype=np.int64)
            best_distances, best_item_ids = _nearest_witness_from_frontier_parallel_by_query_loop_impl(
                query_matrix,
                target_matrix,
                target_ids,
                point_row_indices,
                sorted_frontier_row_indices,
                group_starts,
                group_ends,
                query_row_ids,
                begins,
                counts,
                best_distances,
                best_item_ids,
            )
            reduction_strategy = "numba_parallel_grouped_query_loop_min_distance_then_item_id"
            executor_used = "numba_parallel"
        else:
            best_distances, best_item_ids, candidate_evaluations, used_frontier_rows = (
                _nearest_witness_from_frontier_loop_impl(
                    query_matrix,
                    target_matrix,
                    target_ids,
                    point_row_indices,
                    kind_codes,
                    query_row_ids,
                    begins,
                    counts,
                    best_distances,
                    best_item_ids,
                    CELL_MBR_FRONTIER_KIND_CODES["pruned"],
                )
            )
            reduction_strategy = "numba_loop_min_distance_then_item_id"
            executor_used = "numba"
    else:
        candidate_evaluations = int(used_counts.sum()) if used_frontier_rows else 0
        if candidate_evaluations:
            segment_starts = np.cumsum(used_counts, dtype=np.int64) - used_counts
            within_segment_offsets = np.arange(candidate_evaluations, dtype=np.int64) - np.repeat(
                segment_starts,
                used_counts,
            )
            point_positions = np.repeat(used_begins, used_counts) + within_segment_offsets
            candidate_query_rows = np.repeat(used_query_rows, used_counts)
            candidate_target_rows = point_row_indices[point_positions]
            distance_sq = np.zeros(candidate_evaluations, dtype=np.float64)
            for query_axis, target_axis in zip(query_coordinates, target_coordinates):
                delta = query_axis[candidate_query_rows] - target_axis[candidate_target_rows]
                distance_sq += delta * delta
            candidate_distances = np.sqrt(distance_sq)
            candidate_item_ids = target_ids[candidate_target_rows]
        else:
            candidate_query_rows = np.asarray([], dtype=np.int64)
            candidate_distances = np.asarray([], dtype=np.float64)
            candidate_item_ids = np.asarray([], dtype=np.int64)

        seeded_mask = best_item_ids >= 0
        if np.any(seeded_mask):
            reduce_query_rows = np.concatenate(
                (
                    candidate_query_rows,
                    np.nonzero(seeded_mask)[0].astype(np.int64, copy=False),
                )
            )
            reduce_distances = np.concatenate((candidate_distances, best_distances[seeded_mask]))
            reduce_item_ids = np.concatenate((candidate_item_ids, best_item_ids[seeded_mask]))
        else:
            reduce_query_rows = candidate_query_rows
            reduce_distances = candidate_distances
            reduce_item_ids = candidate_item_ids

        if reduce_query_rows.size:
            order = np.lexsort((reduce_item_ids, reduce_distances, reduce_query_rows))
            sorted_query_rows = reduce_query_rows[order]
            first_mask = np.empty(sorted_query_rows.size, dtype=bool)
            first_mask[0] = True
            first_mask[1:] = sorted_query_rows[1:] != sorted_query_rows[:-1]
            winners = order[first_mask]
            best_distances[reduce_query_rows[winners]] = reduce_distances[winners]
            best_item_ids[reduce_query_rows[winners]] = reduce_item_ids[winners]
        reduction_strategy = "vectorized_expand_lexsort"
        executor_used = "numpy"

    missing = np.where(best_item_ids < 0)[0]
    if missing.size and not bool(allow_missing):
        raise ValueError(
            "cell-MBR frontier nearest witness did not cover every query row; "
            f"missing query_row_ids={missing.tolist()}"
        )

    columns = {
        "source_ids": query_ids.astype(np.int64, copy=False),
        "nearest_item_ids": best_item_ids.astype(np.int64, copy=False),
        "nearest_distances": best_distances.astype(np.float64, copy=False),
    }
    result = {"columns": columns}
    if return_metadata:
        result["metadata"] = {
            "adapter": "nearest_witness_from_cell_mbr_frontier_numpy_columns",
            "partner": "numpy",
            "contract": "generic_nearest_witness_from_cell_mbr_frontier",
            "coordinate_fields": fields,
            "query_count": int(query_ids.size),
            "target_count": int(target_ids.size),
            "frontier_row_count": int(kind_codes.size),
            "used_frontier_row_count": int(used_frontier_rows),
            "candidate_distance_evaluations": int(candidate_evaluations),
            "missing_query_count": int(missing.size),
            "coverage_complete": bool(missing.size == 0),
            "allow_missing": bool(allow_missing),
            "executor": executor_used,
            "executor_requested": executor,
            "reduction_strategy": reduction_strategy,
            "app_semantics": "none",
            "native_engine_row_contract": "consumes_generic_cell_mbr_frontier_rows",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
    query_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    coordinate_fields=("x", "y", "z"),
    executor: str = "auto",
    return_metadata: bool = False,
):
    """Build a generic nearest-state upper bound from each query's nearest cell MBR.

    The seed is an exact distance to one target point from one real cell, so it
    is a valid nearest-neighbor upper bound. It is not guaranteed to be final;
    callers pass the returned distances/items into a frontier producer and
    continuation to refine the state.
    """

    fields = _normalize_coordinate_fields(coordinate_fields)
    query_ids, query_coordinates, query_matrix, query_coordinate_matrix_reused = _point_matrix_for_fields(
        query_point_columns,
        coordinate_fields=fields,
        label="query",
    )
    target_ids, target_coordinates, target_matrix, target_coordinate_matrix_reused = _point_matrix_for_fields(
        target_point_columns,
        coordinate_fields=fields,
        label="target",
    )
    if query_ids.size == 0 or target_ids.size == 0:
        raise ValueError("nearest-cell-MBR seed requires non-empty query and target columns")

    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    if cell_ids.size == 0:
        raise ValueError("cell columns must contain at least one cell")
    cell_mins = tuple(_as_f64(cell_columns[f"min_{axis}"], f"cell min_{axis}") for axis in fields)
    cell_maxs = tuple(_as_f64(cell_columns[f"max_{axis}"], f"cell max_{axis}") for axis in fields)
    if not all(cell_ids.shape == axis.shape for axis in (*cell_mins, *cell_maxs)):
        raise ValueError("cell ids and cell MBR columns must have the same shape")

    begins = _as_i64(cell_columns["point_begin_offsets"], "cell point_begin_offsets")
    counts = _as_i64(cell_columns["point_counts"], "cell point_counts")
    if begins.shape != cell_ids.shape or counts.shape != cell_ids.shape:
        raise ValueError("cell point_begin_offsets and point_counts must match cell ids")
    point_row_indices = _as_i64(cell_columns["point_row_indices"], "cell point row indices")
    if point_row_indices.size == 0:
        raise ValueError("cell point_row_indices must be non-empty")
    if np.any(point_row_indices < 0) or np.any(point_row_indices >= target_ids.size):
        raise ValueError("cell point_row_indices must index target point columns")

    best_distances = np.full(query_ids.size, np.inf, dtype=np.float64)
    best_item_ids = np.full(query_ids.size, -1, dtype=np.int64)
    seed_cell_ids = np.full(query_ids.size, -1, dtype=np.int64)
    seed_cell_point_counts = np.zeros(query_ids.size, dtype=np.int64)
    nonempty_cell_mask = counts > 0
    if not np.any(nonempty_cell_mask):
        raise ValueError("no non-empty cell available for nearest-cell-MBR seed")

    executor = str(executor).lower()
    if executor not in ("auto", "numpy", "numba", "numba_parallel"):
        raise ValueError("executor must be 'auto', 'numpy', 'numba', or 'numba_parallel'")
    use_numba = executor in ("auto", "numba", "numba_parallel") and _numba_njit is not None
    use_numba_parallel = executor in ("auto", "numba_parallel") and _numba_njit is not None
    if executor in ("numba", "numba_parallel") and _numba_njit is None:
        raise RuntimeError("Numba is not available for nearest-cell-MBR seed executor")

    query_matrix = np.ascontiguousarray(np.column_stack(query_coordinates), dtype=np.float64)
    target_matrix = np.ascontiguousarray(np.column_stack(target_coordinates), dtype=np.float64)
    cell_min_matrix = np.ascontiguousarray(np.column_stack(cell_mins), dtype=np.float64)
    cell_max_matrix = np.ascontiguousarray(np.column_stack(cell_maxs), dtype=np.float64)
    mbr_tests = int(query_ids.size * int(np.count_nonzero(nonempty_cell_mask)))
    if use_numba:
        seed_impl = (
            _seed_nearest_witness_parallel_loop_impl
            if use_numba_parallel
            else _seed_nearest_witness_loop_impl
        )
        (
            best_distances,
            best_item_ids,
            seed_cell_ids,
            seed_cell_point_counts,
        ) = seed_impl(
            query_matrix,
            target_matrix,
            target_ids,
            cell_ids,
            cell_min_matrix,
            cell_max_matrix,
            begins,
            counts,
            point_row_indices,
        )
        if np.any(seed_cell_point_counts <= 0):
            raise ValueError("no finite nearest-cell-MBR seed was found")
        candidate_evaluations = int(seed_cell_point_counts.sum())
        if use_numba_parallel:
            cell_mbr_selection = "numba_parallel_loop_min_distance_then_cell_id"
            seed_point_reduction_strategy = "numba_parallel_loop_min_distance_then_item_id"
            executor_used = "numba_parallel"
        else:
            cell_mbr_selection = "numba_loop_min_distance_then_cell_id"
            seed_point_reduction_strategy = "numba_loop_min_distance_then_item_id"
            executor_used = "numba"
    else:
        low_delta = cell_min_matrix.reshape(1, cell_ids.size, len(fields)) - query_matrix.reshape(query_ids.size, 1, len(fields))
        high_delta = query_matrix.reshape(query_ids.size, 1, len(fields)) - cell_max_matrix.reshape(1, cell_ids.size, len(fields))
        outside_delta = np.maximum(np.maximum(low_delta, high_delta), 0.0)
        min_distance_sq = np.sum(outside_delta * outside_delta, axis=2)
        min_distance_sq[:, ~nonempty_cell_mask] = np.inf
        cell_order = np.argsort(cell_ids, kind="stable")
        ordered_min_distance_sq = min_distance_sq[:, cell_order]
        ordered_seed_positions = np.argmin(ordered_min_distance_sq, axis=1)
        seed_cell_indices = cell_order[ordered_seed_positions].astype(np.int64, copy=False)
        seed_min_distance_sq = ordered_min_distance_sq[np.arange(query_ids.size), ordered_seed_positions]
        if not np.all(np.isfinite(seed_min_distance_sq)):
            raise ValueError("no finite nearest-cell-MBR seed was found")

        selected_begins = begins[seed_cell_indices]
        selected_counts = counts[seed_cell_indices]
        if np.any(selected_begins < 0) or np.any(selected_counts < 0):
            raise ValueError("seed cell point span is outside cell point row indices")
        if np.any(selected_begins + selected_counts > point_row_indices.size):
            raise ValueError("seed cell point span is outside cell point row indices")
        seed_cell_ids[:] = cell_ids[seed_cell_indices]
        seed_cell_point_counts[:] = selected_counts
        candidate_evaluations = int(selected_counts.sum())

        segment_starts = np.cumsum(selected_counts, dtype=np.int64) - selected_counts
        within_segment_offsets = np.arange(candidate_evaluations, dtype=np.int64) - np.repeat(
            segment_starts,
            selected_counts,
        )
        point_positions = np.repeat(selected_begins, selected_counts) + within_segment_offsets
        candidate_query_rows = np.repeat(np.arange(query_ids.size, dtype=np.int64), selected_counts)
        candidate_target_rows = point_row_indices[point_positions]
        distance_sq = np.zeros(candidate_evaluations, dtype=np.float64)
        for query_axis, target_axis in zip(query_coordinates, target_coordinates):
            delta = query_axis[candidate_query_rows] - target_axis[candidate_target_rows]
            distance_sq += delta * delta
        candidate_distances = np.sqrt(distance_sq)
        candidate_item_ids = target_ids[candidate_target_rows]
        order = np.lexsort((candidate_item_ids, candidate_distances, candidate_query_rows))
        sorted_query_rows = candidate_query_rows[order]
        first_mask = np.empty(sorted_query_rows.size, dtype=bool)
        first_mask[0] = True
        first_mask[1:] = sorted_query_rows[1:] != sorted_query_rows[:-1]
        winners = order[first_mask]
        best_distances[candidate_query_rows[winners]] = candidate_distances[winners]
        best_item_ids[candidate_query_rows[winners]] = candidate_item_ids[winners]
        cell_mbr_selection = "numpy_vectorized_ordered_argmin_min_distance_then_cell_id"
        seed_point_reduction_strategy = "vectorized_expand_lexsort"
        executor_used = "numpy"

    result = {
        "columns": {
            "source_ids": query_ids.astype(np.int64, copy=False),
            "nearest_item_ids": best_item_ids.astype(np.int64, copy=False),
            "nearest_distances": best_distances.astype(np.float64, copy=False),
            "seed_cell_ids": seed_cell_ids,
        }
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "seed_nearest_witness_from_nearest_cell_mbr_numpy_columns",
            "partner": "numpy",
            "contract": "generic_seed_nearest_witness_from_nearest_cell_mbr",
            "coordinate_fields": fields,
            "query_count": int(query_ids.size),
            "target_count": int(target_ids.size),
            "cell_count": int(cell_ids.size),
            "cell_mbr_tests": int(mbr_tests),
            "executor": executor_used,
            "executor_requested": executor,
            "cell_mbr_selection": cell_mbr_selection,
            "seed_point_reduction_strategy": seed_point_reduction_strategy,
            "candidate_distance_evaluations": int(candidate_evaluations),
            "max_seed_cell_point_count": int(seed_cell_point_counts.max()) if seed_cell_point_counts.size else 0,
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def seed_nearest_witness_from_local_grid_cell_numpy_columns(
    query_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    coordinate_fields=("x", "y", "z"),
    dense_lookup_max_cells: int = 8_000_000,
    executor: str = "auto",
    return_metadata: bool = False,
):
    """Build a valid nearest-state upper bound from a nearby occupied grid cell.

    Unlike `seed_nearest_witness_from_nearest_cell_mbr_numpy_columns`, this
    helper does not promise the nearest tight cell MBR. It chooses a deterministic
    occupied grid cell from the query's local grid neighborhood, then computes an
    exact witness inside that cell. The returned point distance is still a valid
    upper bound for later frontier refinement.
    """

    fields = _normalize_coordinate_fields(coordinate_fields)
    if len(fields) != 3:
        raise ValueError("local-grid-cell seed currently supports exactly 3 coordinate fields")
    query_ids, query_coordinates, query_matrix, query_coordinate_matrix_reused = _point_matrix_for_fields(
        query_point_columns,
        coordinate_fields=fields,
        label="query",
    )
    target_ids, target_coordinates, target_matrix, target_coordinate_matrix_reused = _point_matrix_for_fields(
        target_point_columns,
        coordinate_fields=fields,
        label="target",
    )
    if query_ids.size == 0 or target_ids.size == 0:
        raise ValueError("local-grid-cell seed requires non-empty query and target columns")
    executor_requested = str(executor).lower().replace("_", "-")
    if executor_requested not in ("auto", "numba", "numba-parallel", "native-cuda"):
        raise ValueError("executor must be 'auto', 'numba', 'numba_parallel', or 'native_cuda'")

    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    original_cell_ids = _as_i64(cell_columns["original_cell_ids"], "cell original_cell_ids")
    if cell_ids.size == 0:
        raise ValueError("cell columns must contain at least one cell")
    if cell_ids.shape != original_cell_ids.shape:
        raise ValueError("cell ids and original_cell_ids must have the same shape")
    begins = _as_i64(cell_columns["point_begin_offsets"], "cell point_begin_offsets")
    counts = _as_i64(cell_columns["point_counts"], "cell point_counts")
    if begins.shape != cell_ids.shape or counts.shape != cell_ids.shape:
        raise ValueError("cell point_begin_offsets and point_counts must match cell ids")
    point_row_indices = _as_i64(cell_columns["point_row_indices"], "cell point row indices")
    if point_row_indices.size == 0:
        raise ValueError("cell point_row_indices must be non-empty")
    if np.any(point_row_indices < 0) or np.any(point_row_indices >= target_ids.size):
        raise ValueError("cell point_row_indices must index target point columns")
    if np.any(counts <= 0):
        raise ValueError("local-grid-cell seed requires non-empty compact cells")

    grid_shape = _as_i64(cell_columns["grid_shape"], "cell grid_shape")
    grid_lower_bounds = _as_f64(cell_columns["grid_lower_bounds"], "cell grid_lower_bounds")
    grid_upper_bounds = _as_f64(cell_columns["grid_upper_bounds"], "cell grid_upper_bounds")
    if grid_shape.shape != (3,) or grid_lower_bounds.shape != (3,) or grid_upper_bounds.shape != (3,):
        raise ValueError("local-grid-cell seed requires 3-D grid_shape and grid bounds")
    if np.any(grid_shape <= 0):
        raise ValueError("cell grid_shape entries must be positive")
    if np.any(grid_upper_bounds < grid_lower_bounds):
        raise ValueError("cell grid bounds are invalid")
    if np.any(original_cell_ids[1:] <= original_cell_ids[:-1]):
        raise ValueError("cell original_cell_ids must be strictly increasing")
    if dense_lookup_max_cells < 0:
        raise ValueError("dense_lookup_max_cells must be non-negative")
    grid_volume = int(grid_shape[0]) * int(grid_shape[1]) * int(grid_shape[2])
    if np.any(original_cell_ids < 0) or np.any(original_cell_ids >= grid_volume):
        raise ValueError("cell original_cell_ids must fit inside grid_shape")
    if grid_volume <= int(dense_lookup_max_cells):
        dense_cell_positions = np.full(grid_volume, -1, dtype=np.int64)
        dense_cell_positions[original_cell_ids] = np.arange(original_cell_ids.size, dtype=np.int64)
        cell_lookup_strategy = "dense_grid_cell_position_table"
    else:
        dense_cell_positions = np.empty(0, dtype=np.int64)
        cell_lookup_strategy = "binary_search_original_cell_ids"

    if executor_requested == "native-cuda":
        if cell_lookup_strategy != "dense_grid_cell_position_table":
            raise ValueError("native_cuda local-grid seed requires dense lookup; increase dense_lookup_max_cells")
        from .optix_runtime import seed_nearest_witness_local_grid_cell_3d_cuda

        native = seed_nearest_witness_local_grid_cell_3d_cuda(
            query_coords=query_matrix,
            query_point_ids=query_ids,
            target_coords=target_matrix,
            target_point_ids=target_ids,
            cell_ids=cell_ids,
            original_cell_ids=original_cell_ids,
            dense_cell_positions=dense_cell_positions,
            point_begin_offsets=begins,
            point_counts=counts,
            point_row_indices=point_row_indices,
            grid_shape=grid_shape,
            grid_lower_bounds=grid_lower_bounds,
            grid_upper_bounds=grid_upper_bounds,
        )
        result = {
            "columns": {
                "source_ids": query_ids.astype(np.int64, copy=False),
                "nearest_item_ids": _as_i64(native["columns"]["nearest_item_ids"], "native nearest item ids"),
                "nearest_distances": _as_f64(native["columns"]["nearest_distances"], "native nearest distances"),
                "seed_cell_ids": _as_i64(native["columns"]["seed_cell_ids"], "native seed cell ids"),
            }
        }
        if return_metadata:
            metadata = dict(native["metadata"])
            metadata.update(
                {
                    "adapter": "seed_nearest_witness_from_local_grid_cell_numpy_columns",
                    "coordinate_fields": fields,
                    "dense_lookup_max_cells": int(dense_lookup_max_cells),
                    "executor_requested": executor,
                    "query_coordinate_matrix_reused": bool(query_coordinate_matrix_reused),
                    "target_coordinate_matrix_reused": bool(target_coordinate_matrix_reused),
                }
            )
            result["metadata"] = metadata
        return result

    if _numba_njit is None:
        raise RuntimeError("Numba is required for local-grid-cell seed executor")

    (
        best_distances,
        best_item_ids,
        seed_cell_ids,
        seed_cell_point_counts,
        grid_cell_probe_counts,
    ) = _seed_nearest_witness_grid_local_3d_parallel_impl(
        query_matrix,
        target_matrix,
        target_ids,
        cell_ids,
        original_cell_ids,
        dense_cell_positions,
        grid_shape,
        grid_lower_bounds,
        grid_upper_bounds,
        begins,
        counts,
        point_row_indices,
    )
    if np.any(seed_cell_point_counts <= 0):
        raise ValueError("no local occupied grid-cell seed was found")

    result = {
        "columns": {
            "source_ids": query_ids.astype(np.int64, copy=False),
            "nearest_item_ids": best_item_ids.astype(np.int64, copy=False),
            "nearest_distances": best_distances.astype(np.float64, copy=False),
            "seed_cell_ids": seed_cell_ids,
        }
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "seed_nearest_witness_from_local_grid_cell_numpy_columns",
            "partner": "numpy_numba",
            "contract": "generic_seed_nearest_witness_from_local_grid_cell",
            "coordinate_fields": fields,
            "query_count": int(query_ids.size),
            "target_count": int(target_ids.size),
            "cell_count": int(cell_ids.size),
            "grid_shape": tuple(int(value) for value in grid_shape.tolist()),
            "grid_cell_probes": int(grid_cell_probe_counts.sum()),
            "max_grid_cell_probes_per_query": int(grid_cell_probe_counts.max()) if grid_cell_probe_counts.size else 0,
            "cell_lookup_strategy": cell_lookup_strategy,
            "dense_lookup_cell_capacity": int(dense_cell_positions.shape[0]),
            "dense_lookup_max_cells": int(dense_lookup_max_cells),
            "executor": "numba_parallel",
            "executor_requested": executor,
            "query_coordinate_matrix_reused": bool(query_coordinate_matrix_reused),
            "target_coordinate_matrix_reused": bool(target_coordinate_matrix_reused),
            "cell_selection": "local_grid_first_occupied_shell_min_grid_cell_distance_then_cell_id",
            "seed_point_reduction_strategy": "numba_parallel_loop_min_distance_then_item_id",
            "candidate_distance_evaluations": int(seed_cell_point_counts.sum()),
            "max_seed_cell_point_count": int(seed_cell_point_counts.max()) if seed_cell_point_counts.size else 0,
            "seed_quality": "valid_upper_bound_not_nearest_cell_mbr",
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def seed_nearest_witness_from_grid_branch_bound_numpy_columns(
    query_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    coordinate_fields=("x", "y", "z"),
    dense_lookup_max_cells: int = 8_000_000,
    executor: str = "auto",
    return_metadata: bool = False,
):
    """Build a tighter generic nearest-state seed using grid-cell branch/bound.

    This helper searches local grid shells until the next shell's grid-cell AABB
    lower bound cannot improve the current exact point witness. It is still a
    generic grid/cell operation and does not encode any app or workload
    semantics.
    """

    fields = _normalize_coordinate_fields(coordinate_fields)
    if len(fields) != 3:
        raise ValueError("grid-branch-bound seed currently supports exactly 3 coordinate fields")
    query_ids, query_coordinates = _point_columns_for_fields(
        query_point_columns,
        coordinate_fields=fields,
        label="query",
    )
    target_ids, target_coordinates = _point_columns_for_fields(
        target_point_columns,
        coordinate_fields=fields,
        label="target",
    )
    if query_ids.size == 0 or target_ids.size == 0:
        raise ValueError("grid-branch-bound seed requires non-empty query and target columns")
    executor_requested = str(executor).lower().replace("_", "-")
    if executor_requested not in ("auto", "numba", "numba-parallel", "native-cuda"):
        raise ValueError("executor must be 'auto', 'numba', 'numba_parallel', or 'native_cuda'")
    if executor_requested in ("auto", "numba", "numba-parallel") and _numba_njit is None:
        raise RuntimeError("Numba is required for grid-branch-bound seed executor")

    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    original_cell_ids = _as_i64(cell_columns["original_cell_ids"], "cell original_cell_ids")
    if cell_ids.size == 0:
        raise ValueError("cell columns must contain at least one cell")
    if cell_ids.shape != original_cell_ids.shape:
        raise ValueError("cell ids and original_cell_ids must have the same shape")
    begins = _as_i64(cell_columns["point_begin_offsets"], "cell point_begin_offsets")
    counts = _as_i64(cell_columns["point_counts"], "cell point_counts")
    if begins.shape != cell_ids.shape or counts.shape != cell_ids.shape:
        raise ValueError("cell point_begin_offsets and point_counts must match cell ids")
    point_row_indices = _as_i64(cell_columns["point_row_indices"], "cell point row indices")
    if point_row_indices.size == 0:
        raise ValueError("cell point_row_indices must be non-empty")
    if np.any(point_row_indices < 0) or np.any(point_row_indices >= target_ids.size):
        raise ValueError("cell point_row_indices must index target point columns")
    if np.any(counts <= 0):
        raise ValueError("grid-branch-bound seed requires non-empty compact cells")

    grid_shape = _as_i64(cell_columns["grid_shape"], "cell grid_shape")
    grid_lower_bounds = _as_f64(cell_columns["grid_lower_bounds"], "cell grid_lower_bounds")
    grid_upper_bounds = _as_f64(cell_columns["grid_upper_bounds"], "cell grid_upper_bounds")
    if grid_shape.shape != (3,) or grid_lower_bounds.shape != (3,) or grid_upper_bounds.shape != (3,):
        raise ValueError("grid-branch-bound seed requires 3-D grid_shape and grid bounds")
    if np.any(grid_shape <= 0):
        raise ValueError("cell grid_shape entries must be positive")
    if np.any(grid_upper_bounds < grid_lower_bounds):
        raise ValueError("cell grid bounds are invalid")
    if np.any(original_cell_ids[1:] <= original_cell_ids[:-1]):
        raise ValueError("cell original_cell_ids must be strictly increasing")
    if dense_lookup_max_cells < 0:
        raise ValueError("dense_lookup_max_cells must be non-negative")
    grid_volume = int(grid_shape[0]) * int(grid_shape[1]) * int(grid_shape[2])
    if np.any(original_cell_ids < 0) or np.any(original_cell_ids >= grid_volume):
        raise ValueError("cell original_cell_ids must fit inside grid_shape")
    if grid_volume <= int(dense_lookup_max_cells):
        dense_cell_positions = np.full(grid_volume, -1, dtype=np.int64)
        dense_cell_positions[original_cell_ids] = np.arange(original_cell_ids.size, dtype=np.int64)
        cell_lookup_strategy = "dense_grid_cell_position_table"
    else:
        dense_cell_positions = np.empty(0, dtype=np.int64)
        cell_lookup_strategy = "binary_search_original_cell_ids"

    query_matrix = np.ascontiguousarray(np.column_stack(query_coordinates), dtype=np.float64)
    target_matrix = np.ascontiguousarray(np.column_stack(target_coordinates), dtype=np.float64)
    if executor_requested == "native-cuda":
        if cell_lookup_strategy != "dense_grid_cell_position_table":
            raise ValueError("native_cuda grid branch-bound seed requires dense lookup; increase dense_lookup_max_cells")
        from .optix_runtime import seed_nearest_witness_grid_branch_bound_3d_cuda

        native = seed_nearest_witness_grid_branch_bound_3d_cuda(
            query_coords=query_matrix,
            query_point_ids=query_ids,
            target_coords=target_matrix,
            target_point_ids=target_ids,
            cell_ids=cell_ids,
            original_cell_ids=original_cell_ids,
            dense_cell_positions=dense_cell_positions,
            point_begin_offsets=begins,
            point_counts=counts,
            point_row_indices=point_row_indices,
            grid_shape=grid_shape,
            grid_lower_bounds=grid_lower_bounds,
            grid_upper_bounds=grid_upper_bounds,
        )
        result = {
            "columns": {
                "source_ids": query_ids.astype(np.int64, copy=False),
                "nearest_item_ids": _as_i64(native["columns"]["nearest_item_ids"], "native nearest item ids"),
                "nearest_distances": _as_f64(native["columns"]["nearest_distances"], "native nearest distances"),
                "seed_cell_ids": _as_i64(native["columns"]["seed_cell_ids"], "native seed cell ids"),
            }
        }
        if return_metadata:
            metadata = dict(native["metadata"])
            metadata.update(
                {
                    "adapter": "seed_nearest_witness_from_grid_branch_bound_numpy_columns",
                    "coordinate_fields": fields,
                    "dense_lookup_max_cells": int(dense_lookup_max_cells),
                    "executor_requested": executor,
                    "query_coordinate_matrix_reused": False,
                    "target_coordinate_matrix_reused": False,
                }
            )
            result["metadata"] = metadata
        return result

    (
        best_distances,
        best_item_ids,
        seed_cell_ids,
        seed_cell_point_counts,
        grid_cell_probe_counts,
        scanned_cell_counts,
        scanned_point_counts,
        shell_counts,
    ) = _seed_nearest_witness_grid_branch_bound_3d_parallel_impl(
        query_matrix,
        target_matrix,
        target_ids,
        cell_ids,
        original_cell_ids,
        dense_cell_positions,
        grid_shape,
        grid_lower_bounds,
        grid_upper_bounds,
        begins,
        counts,
        point_row_indices,
    )
    if np.any(seed_cell_point_counts <= 0):
        raise ValueError("no grid-branch-bound seed was found")

    result = {
        "columns": {
            "source_ids": query_ids.astype(np.int64, copy=False),
            "nearest_item_ids": best_item_ids.astype(np.int64, copy=False),
            "nearest_distances": best_distances.astype(np.float64, copy=False),
            "seed_cell_ids": seed_cell_ids,
        }
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "seed_nearest_witness_from_grid_branch_bound_numpy_columns",
            "partner": "numpy_numba",
            "contract": "generic_seed_nearest_witness_from_grid_branch_bound",
            "coordinate_fields": fields,
            "query_count": int(query_ids.size),
            "target_count": int(target_ids.size),
            "cell_count": int(cell_ids.size),
            "grid_shape": tuple(int(value) for value in grid_shape.tolist()),
            "grid_cell_probes": int(grid_cell_probe_counts.sum()),
            "max_grid_cell_probes_per_query": int(grid_cell_probe_counts.max()) if grid_cell_probe_counts.size else 0,
            "scanned_cell_count": int(scanned_cell_counts.sum()),
            "max_scanned_cells_per_query": int(scanned_cell_counts.max()) if scanned_cell_counts.size else 0,
            "cell_lookup_strategy": cell_lookup_strategy,
            "dense_lookup_cell_capacity": int(dense_cell_positions.shape[0]),
            "dense_lookup_max_cells": int(dense_lookup_max_cells),
            "executor": "numba_parallel",
            "executor_requested": executor,
            "cell_selection": "grid_shell_branch_bound_until_lower_bound_exceeds_best_point",
            "seed_point_reduction_strategy": "numba_parallel_branch_bound_min_distance_then_item_id",
            "candidate_distance_evaluations": int(scanned_point_counts.sum()),
            "max_seed_cell_point_count": int(seed_cell_point_counts.max()) if seed_cell_point_counts.size else 0,
            "max_shells_per_query": int(shell_counts.max()) if shell_counts.size else 0,
            "seed_quality": "exact_nearest_witness_under_grid_cell_branch_bound",
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def seed_nearest_witness_from_grid_cell_budget_numpy_columns(
    query_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    coordinate_fields=("x", "y", "z"),
    max_scanned_cells_per_query: int = 4,
    dense_lookup_max_cells: int = 8_000_000,
    return_metadata: bool = False,
):
    """Build a valid nearest-state seed by scanning a bounded number of grid cells.

    This helper is a middle ground between the very cheap local-grid seed and
    the complete grid branch/bound seed. For each query it scans nearby occupied
    grid cells in deterministic shell order, updates an exact point witness
    inside each scanned cell, and stops after `max_scanned_cells_per_query`
    occupied cells or when the next shell cannot improve the current witness.
    The returned witness is still only an upper-bound seed for later frontier
    refinement; it does not promise exact nearest-neighbor completion.
    """

    fields = _normalize_coordinate_fields(coordinate_fields)
    if len(fields) != 3:
        raise ValueError("grid-cell-budget seed currently supports exactly 3 coordinate fields")
    max_scanned_cells_per_query = int(max_scanned_cells_per_query)
    if max_scanned_cells_per_query <= 0:
        raise ValueError("max_scanned_cells_per_query must be positive")
    query_ids, query_coordinates = _point_columns_for_fields(
        query_point_columns,
        coordinate_fields=fields,
        label="query",
    )
    target_ids, target_coordinates = _point_columns_for_fields(
        target_point_columns,
        coordinate_fields=fields,
        label="target",
    )
    if query_ids.size == 0 or target_ids.size == 0:
        raise ValueError("grid-cell-budget seed requires non-empty query and target columns")
    if _numba_njit is None:
        raise RuntimeError("Numba is required for grid-cell-budget seed executor")

    cell_ids = _as_i64(cell_columns["cell_ids"], "cell ids")
    original_cell_ids = _as_i64(cell_columns["original_cell_ids"], "cell original_cell_ids")
    if cell_ids.size == 0:
        raise ValueError("cell columns must contain at least one cell")
    if cell_ids.shape != original_cell_ids.shape:
        raise ValueError("cell ids and original_cell_ids must have the same shape")
    begins = _as_i64(cell_columns["point_begin_offsets"], "cell point_begin_offsets")
    counts = _as_i64(cell_columns["point_counts"], "cell point_counts")
    if begins.shape != cell_ids.shape or counts.shape != cell_ids.shape:
        raise ValueError("cell point_begin_offsets and point_counts must match cell ids")
    point_row_indices = _as_i64(cell_columns["point_row_indices"], "cell point row indices")
    if point_row_indices.size == 0:
        raise ValueError("cell point_row_indices must be non-empty")
    if np.any(point_row_indices < 0) or np.any(point_row_indices >= target_ids.size):
        raise ValueError("cell point_row_indices must index target point columns")
    if np.any(counts <= 0):
        raise ValueError("grid-cell-budget seed requires non-empty compact cells")

    grid_shape = _as_i64(cell_columns["grid_shape"], "cell grid_shape")
    grid_lower_bounds = _as_f64(cell_columns["grid_lower_bounds"], "cell grid_lower_bounds")
    grid_upper_bounds = _as_f64(cell_columns["grid_upper_bounds"], "cell grid_upper_bounds")
    if grid_shape.shape != (3,) or grid_lower_bounds.shape != (3,) or grid_upper_bounds.shape != (3,):
        raise ValueError("grid-cell-budget seed requires 3-D grid_shape and grid bounds")
    if np.any(grid_shape <= 0):
        raise ValueError("cell grid_shape entries must be positive")
    if np.any(grid_upper_bounds < grid_lower_bounds):
        raise ValueError("cell grid bounds are invalid")
    if np.any(original_cell_ids[1:] <= original_cell_ids[:-1]):
        raise ValueError("cell original_cell_ids must be strictly increasing")
    if dense_lookup_max_cells < 0:
        raise ValueError("dense_lookup_max_cells must be non-negative")
    grid_volume = int(grid_shape[0]) * int(grid_shape[1]) * int(grid_shape[2])
    if np.any(original_cell_ids < 0) or np.any(original_cell_ids >= grid_volume):
        raise ValueError("cell original_cell_ids must fit inside grid_shape")
    if grid_volume <= int(dense_lookup_max_cells):
        dense_cell_positions = np.full(grid_volume, -1, dtype=np.int64)
        dense_cell_positions[original_cell_ids] = np.arange(original_cell_ids.size, dtype=np.int64)
        cell_lookup_strategy = "dense_grid_cell_position_table"
    else:
        dense_cell_positions = np.empty(0, dtype=np.int64)
        cell_lookup_strategy = "binary_search_original_cell_ids"

    query_matrix = np.ascontiguousarray(np.column_stack(query_coordinates), dtype=np.float64)
    target_matrix = np.ascontiguousarray(np.column_stack(target_coordinates), dtype=np.float64)
    (
        best_distances,
        best_item_ids,
        seed_cell_ids,
        seed_cell_point_counts,
        grid_cell_probe_counts,
        scanned_cell_counts,
        scanned_point_counts,
        shell_counts,
    ) = _seed_nearest_witness_grid_cell_budget_3d_parallel_impl(
        query_matrix,
        target_matrix,
        target_ids,
        cell_ids,
        original_cell_ids,
        dense_cell_positions,
        grid_shape,
        grid_lower_bounds,
        grid_upper_bounds,
        begins,
        counts,
        point_row_indices,
        max_scanned_cells_per_query,
    )
    if np.any(seed_cell_point_counts <= 0):
        raise ValueError("no grid-cell-budget seed was found")

    result = {
        "columns": {
            "source_ids": query_ids.astype(np.int64, copy=False),
            "nearest_item_ids": best_item_ids.astype(np.int64, copy=False),
            "nearest_distances": best_distances.astype(np.float64, copy=False),
            "seed_cell_ids": seed_cell_ids,
        }
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "seed_nearest_witness_from_grid_cell_budget_numpy_columns",
            "partner": "numpy_numba",
            "contract": "generic_seed_nearest_witness_from_grid_cell_budget",
            "coordinate_fields": fields,
            "query_count": int(query_ids.size),
            "target_count": int(target_ids.size),
            "cell_count": int(cell_ids.size),
            "grid_shape": tuple(int(value) for value in grid_shape.tolist()),
            "grid_cell_probes": int(grid_cell_probe_counts.sum()),
            "max_grid_cell_probes_per_query": int(grid_cell_probe_counts.max()) if grid_cell_probe_counts.size else 0,
            "scanned_cell_count": int(scanned_cell_counts.sum()),
            "max_scanned_cells_per_query": int(scanned_cell_counts.max()) if scanned_cell_counts.size else 0,
            "scanned_cell_budget_per_query": int(max_scanned_cells_per_query),
            "cell_lookup_strategy": cell_lookup_strategy,
            "dense_lookup_cell_capacity": int(dense_cell_positions.shape[0]),
            "dense_lookup_max_cells": int(dense_lookup_max_cells),
            "executor": "numba_parallel",
            "cell_selection": "grid_shell_scan_with_scanned_cell_budget",
            "seed_point_reduction_strategy": "numba_parallel_bounded_grid_scan_min_distance_then_item_id",
            "candidate_distance_evaluations": int(scanned_point_counts.sum()),
            "max_seed_cell_point_count": int(seed_cell_point_counts.max()) if seed_cell_point_counts.size else 0,
            "max_shells_per_query": int(shell_counts.max()) if shell_counts.size else 0,
            "seed_quality": "valid_upper_bound_bounded_grid_cell_scan",
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def cell_mbr_nearest_frontier_numpy_columns(
    query_point_columns: Mapping[str, object],
    cell_columns: Mapping[str, object],
    *,
    radius: float,
    coordinate_fields=("x", "y", "z"),
    current_best_distances=None,
    current_best_item_ids=None,
    max_inline_points: int,
    row_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Build Goal5140 frontier rows from generic cell-MBR candidates.

    This dimension-generic reference front door composes the public
    radius-cell-MBR candidate route with nearest-state frontier classification
    and the Goal5140 row-table adapter. It is the portable oracle for future
    native/RT backends, including 3-D cell-MBR traversal.
    """

    radius = float(radius)
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    fields = _normalize_coordinate_fields(coordinate_fields)
    query_ids, _query_coordinates = _point_columns_for_fields(
        query_point_columns,
        coordinate_fields=fields,
        label="query",
    )
    if query_ids.size == 0:
        raise ValueError("query point columns must be non-empty")
    candidates = radius_cell_mbr_candidate_rows_numpy_columns(
        query_point_columns,
        cell_columns,
        radius=radius,
        coordinate_fields=fields,
        return_metadata=True,
    )
    frontier = nearest_state_frontier_from_cell_candidates_numpy_columns(
        candidates["columns"],
        cell_columns,
        query_point_ids=query_ids,
        current_best_distances=current_best_distances,
        current_best_item_ids=current_best_item_ids,
        max_inline_points=max_inline_points,
        return_metadata=True,
    )
    table = cell_mbr_frontiers_to_row_table_numpy_columns(
        frontier,
        return_metadata=True,
    )
    final_count = int(table["columns"]["frontier_kind_codes"].size)
    if row_capacity is not None and final_count > int(row_capacity):
        raise RuntimeError(
            "cell-MBR nearest frontier row output overflowed; "
            f"attempted {final_count}; capacity {int(row_capacity)}; "
            "failure_mode=fail_closed_overflow; partial_result_returned=False"
        )
    explicit_capacity = row_capacity is not None
    resolved_capacity = None if row_capacity is None else int(row_capacity)
    full_capacity = int(query_ids.size) * int(_as_i64(cell_columns["cell_ids"], "cell ids").size)
    result = {
        "nearest_state": frontier["nearest_state"],
        "inline_frontier": frontier["inline_frontier"],
        "offload_frontier": frontier["offload_frontier"],
        "pruned_frontier": frontier["pruned_frontier"],
        "row_table": table,
    }
    if return_metadata:
        result["metadata"] = {
            "adapter": "cell_mbr_nearest_frontier_numpy_columns",
            "partner": "numpy",
            "contract": "generic_cell_mbr_nearest_frontier_reference",
            "native_abi_contract": CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT,
            "coordinate_fields": fields,
            "query_count": int(query_ids.size),
            "cell_count": int(_as_i64(cell_columns["cell_ids"], "cell ids").size),
            "candidate_row_count": int(candidates["metadata"]["candidate_row_count"]),
            "row_count": final_count,
            "attempted_count": final_count,
            "row_capacity": resolved_capacity,
            "full_row_capacity": full_capacity,
            "row_capacity_policy": "explicit" if explicit_capacity else "unbounded_reference",
            "row_capacity_attempts": (resolved_capacity,) if explicit_capacity else (),
            "radius": radius,
            "max_inline_points": int(max_inline_points),
            "candidate_contract": candidates["metadata"]["contract"],
            "state_split_contract": frontier["metadata"]["contract"],
            "row_table_contract": table["metadata"]["contract"],
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_dimension_generic_reference_only",
            "native_backend_complete": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def _frontier_table_piece(frontier: Mapping[str, object], *, kind_code: int) -> dict[str, np.ndarray]:
    query_row_ids = _as_i64(frontier["query_row_ids"], "frontier query_row_ids")
    query_point_ids = _as_i64(frontier["query_point_ids"], "frontier query_point_ids")
    cell_ids = _as_i64(frontier["cell_ids"], "frontier cell_ids")
    point_begin_offsets = _as_i64(frontier["point_begin_offsets"], "frontier point_begin_offsets")
    point_counts = _as_i64(frontier["point_counts"], "frontier point_counts")
    min_distances = _as_f64(frontier["min_distances"], "frontier min_distances")
    max_distances = _as_f64(frontier["max_distances"], "frontier max_distances")
    if not (
        query_row_ids.shape
        == query_point_ids.shape
        == cell_ids.shape
        == point_begin_offsets.shape
        == point_counts.shape
        == min_distances.shape
        == max_distances.shape
    ):
        raise ValueError("frontier columns must have matching shapes")
    return {
        "frontier_kind_codes": np.full(query_row_ids.size, int(kind_code), dtype=np.int64),
        "query_row_ids": query_row_ids,
        "query_point_ids": query_point_ids,
        "cell_ids": cell_ids,
        "point_begin_offsets": point_begin_offsets,
        "point_counts": point_counts,
        "min_distances": min_distances,
        "max_distances": max_distances,
    }


def cell_mbr_frontiers_to_row_table_numpy_columns(
    frontier_result: Mapping[str, object],
    *,
    return_metadata: bool = False,
):
    """Flatten inline/offload/pruned frontiers into one ABI-shaped row table."""

    pieces = [
        _frontier_table_piece(
            frontier_result["inline_frontier"],
            kind_code=CELL_MBR_FRONTIER_KIND_CODES["inline"],
        ),
        _frontier_table_piece(
            frontier_result["offload_frontier"],
            kind_code=CELL_MBR_FRONTIER_KIND_CODES["offload"],
        ),
        _frontier_table_piece(
            frontier_result["pruned_frontier"],
            kind_code=CELL_MBR_FRONTIER_KIND_CODES["pruned"],
        ),
    ]
    columns: dict[str, np.ndarray] = {}
    for name in (
        "frontier_kind_codes",
        "query_row_ids",
        "query_point_ids",
        "cell_ids",
        "point_begin_offsets",
        "point_counts",
        "min_distances",
        "max_distances",
    ):
        arrays = [piece[name] for piece in pieces]
        columns[name] = np.concatenate(arrays) if arrays else np.asarray([], dtype=np.int64)

    result = {"columns": columns}
    if return_metadata:
        result["metadata"] = {
            "adapter": "cell_mbr_frontiers_to_row_table_numpy_columns",
            "partner": "numpy",
            "contract": "generic_cell_mbr_nearest_frontier_row_table",
            "native_abi_contract": CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT,
            "row_schema": CELL_MBR_TRAVERSAL_ROW_SCHEMA,
            "frontier_kind_codes": dict(CELL_MBR_FRONTIER_KIND_CODES),
            "row_count": int(columns["frontier_kind_codes"].size),
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def _empty_heavy_offload_worklist_columns() -> dict[str, np.ndarray]:
    return {
        "work_source_ids": np.asarray([], dtype=np.int64),
        "work_primitive_ids": np.asarray([], dtype=np.int64),
        "work_begin_offsets": np.asarray([], dtype=np.int64),
        "work_counts": np.asarray([], dtype=np.int64),
        "work_kind_codes": np.asarray([], dtype=np.int64),
        "work_cost_estimates": np.asarray([], dtype=np.float64),
        "lower_bounds": np.asarray([], dtype=np.float64),
        "upper_bounds": np.asarray([], dtype=np.float64),
    }


def heavy_offload_worklist_numpy_columns(
    source_ids,
    primitive_ids,
    begin_offsets,
    work_counts,
    lower_bounds,
    upper_bounds,
    *,
    heavy_threshold: int,
    miss_mask=None,
    deferred_mask=None,
    work_cost_estimates=None,
    row_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Build an app-neutral heavy/deferred worklist row table.

    The reference selects rows that either exceed ``heavy_threshold`` or are
    explicitly marked as miss/deferred by the caller. Capacity overflow returns
    no partial rows and records the attempted count for diagnostics.
    """

    source_ids = _as_i64(source_ids, "source ids")
    primitive_ids = _as_i64(primitive_ids, "primitive ids")
    begin_offsets = _as_i64(begin_offsets, "begin offsets")
    work_counts = _as_i64(work_counts, "work counts")
    lower_bounds = _as_f64(lower_bounds, "lower bounds")
    upper_bounds = _as_f64(upper_bounds, "upper bounds")
    expected_shape = source_ids.shape
    for name, array in (
        ("primitive ids", primitive_ids),
        ("begin offsets", begin_offsets),
        ("work counts", work_counts),
        ("lower bounds", lower_bounds),
        ("upper bounds", upper_bounds),
    ):
        if array.shape != expected_shape:
            raise ValueError(f"{name} must have the same shape as source ids")
    if np.any(begin_offsets < 0):
        raise ValueError("begin offsets must be non-negative")
    if np.any(work_counts < 0):
        raise ValueError("work counts must be non-negative")
    heavy_threshold = int(heavy_threshold)
    if heavy_threshold < 0:
        raise ValueError("heavy_threshold must be non-negative")
    if row_capacity is not None:
        row_capacity = int(row_capacity)
        if row_capacity < 0:
            raise ValueError("row_capacity must be non-negative")

    if miss_mask is None:
        miss_mask_array = np.zeros(expected_shape, dtype=bool)
    else:
        miss_mask_array = np.asarray(miss_mask, dtype=bool)
        if miss_mask_array.shape != expected_shape:
            raise ValueError("miss_mask must have the same shape as source ids")
    if deferred_mask is None:
        deferred_mask_array = np.zeros(expected_shape, dtype=bool)
    else:
        deferred_mask_array = np.asarray(deferred_mask, dtype=bool)
        if deferred_mask_array.shape != expected_shape:
            raise ValueError("deferred_mask must have the same shape as source ids")
    if np.any(miss_mask_array & deferred_mask_array):
        raise ValueError("miss_mask and deferred_mask must not overlap")

    if work_cost_estimates is None:
        work_cost_estimates = work_counts.astype(np.float64, copy=False)
    else:
        work_cost_estimates = _as_f64(work_cost_estimates, "work cost estimates")
        if work_cost_estimates.shape != expected_shape:
            raise ValueError("work cost estimates must have the same shape as source ids")

    active_mask = (work_counts > heavy_threshold) & ~(miss_mask_array | deferred_mask_array)
    selected_mask = active_mask | miss_mask_array | deferred_mask_array
    selected_indices = np.flatnonzero(selected_mask)
    attempted_count = int(selected_indices.size)
    overflowed = row_capacity is not None and attempted_count > row_capacity
    if overflowed:
        columns = _empty_heavy_offload_worklist_columns()
        row_count = 0
    else:
        kind_codes = np.empty(attempted_count, dtype=np.int64)
        selected_miss = miss_mask_array[selected_indices]
        selected_deferred = deferred_mask_array[selected_indices]
        kind_codes[:] = HEAVY_OFFLOAD_WORKLIST_KIND_CODES["active"]
        kind_codes[selected_miss] = HEAVY_OFFLOAD_WORKLIST_KIND_CODES["miss"]
        kind_codes[selected_deferred] = HEAVY_OFFLOAD_WORKLIST_KIND_CODES["deferred"]
        columns = {
            "work_source_ids": source_ids[selected_indices].astype(np.int64, copy=False),
            "work_primitive_ids": primitive_ids[selected_indices].astype(np.int64, copy=False),
            "work_begin_offsets": begin_offsets[selected_indices].astype(np.int64, copy=False),
            "work_counts": work_counts[selected_indices].astype(np.int64, copy=False),
            "work_kind_codes": kind_codes,
            "work_cost_estimates": work_cost_estimates[selected_indices].astype(np.float64, copy=False),
            "lower_bounds": lower_bounds[selected_indices].astype(np.float64, copy=False),
            "upper_bounds": upper_bounds[selected_indices].astype(np.float64, copy=False),
        }
        row_count = attempted_count

    device_buffer_bytes = int(sum(array.nbytes for array in columns.values()))
    queue_pair_bytes = int(row_count * 2 * HEAVY_OFFLOAD_INT_ID_BYTES)
    telemetry = {
        "schema": "rtdl.generic.heavy_offload_worklist.memory_telemetry.v1",
        "in_queue_capacity": int(source_ids.size),
        "miss_queue_capacity": int(np.count_nonzero(miss_mask_array)),
        "deferred_queue_capacity": int(np.count_nonzero(deferred_mask_array)),
        "in_queue_bytes": int(source_ids.size * HEAVY_OFFLOAD_INT_ID_BYTES),
        "miss_queue_bytes": int(np.count_nonzero(miss_mask_array) * HEAVY_OFFLOAD_INT_ID_BYTES),
        "deferred_queue_bytes": int(np.count_nonzero(deferred_mask_array) * HEAVY_OFFLOAD_INT_ID_BYTES),
        "heavy_offload_row_capacity": int(row_capacity if row_capacity is not None else attempted_count),
        "heavy_offload_attempted_rows": attempted_count,
        "heavy_offload_current_rows": row_count,
        "heavy_offload_peak_rows": row_count,
        "heavy_offload_queue_current_bytes": queue_pair_bytes,
        "heavy_offload_queue_peak_bytes": queue_pair_bytes,
        "device_buffer_bytes_excluding_accel": device_buffer_bytes,
        "native_accel_bytes_if_applicable": None,
    }
    result = {"columns": columns, "telemetry": telemetry}
    if return_metadata:
        result["metadata"] = {
            "adapter": "heavy_offload_worklist_numpy_columns",
            "partner": "numpy",
            "contract": HEAVY_OFFLOAD_WORKLIST_CONTRACT,
            "row_schema": HEAVY_OFFLOAD_WORKLIST_ROW_SCHEMA,
            "work_kind_codes": dict(HEAVY_OFFLOAD_WORKLIST_KIND_CODES),
            "row_count": row_count,
            "attempted_row_count": attempted_count,
            "overflowed": bool(overflowed),
            "overflow_policy": "fail_closed_no_partial_rows",
            "heavy_threshold": heavy_threshold,
            "row_capacity": None if row_capacity is None else int(row_capacity),
            "app_semantics": "none",
            "native_engine_row_contract": "not_called_partner_reference_only",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    return result


def cell_mbr_traversal_native_abi_contract() -> dict[str, object]:
    """Return the app-neutral native ABI target for cell-MBR nearest frontiers."""

    prototype = (
        "int {symbol}(const double* query_coords, const int64_t* query_point_ids, "
        "size_t query_count, const int64_t* cell_ids, const uint64_t* point_begin_offsets, "
        "const uint64_t* point_counts, const double* cell_mbr_min, const double* cell_mbr_max, "
        "size_t cell_count, uint32_t dimension, double radius, "
        "const double* current_best_distances, const int64_t* current_best_item_ids, "
        "uint64_t max_inline_points, uint64_t row_capacity, int64_t* frontier_kind_codes_out, "
        "int64_t* query_row_ids_out, int64_t* query_point_ids_out, int64_t* cell_ids_out, "
        "uint64_t* point_begin_offsets_out, uint64_t* point_counts_out, "
        "double* min_distances_out, double* max_distances_out, uint64_t* emitted_count_out, "
        "uint64_t* attempted_count_out, uint32_t* overflowed_out, char* error_out, size_t error_size)"
    )
    return {
        "primitive": "cell_mbr_nearest_frontier",
        "contract": CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT,
        "python_reference_contract": "generic_nearest_state_cell_frontier",
        "row_table_reference_contract": "generic_cell_mbr_nearest_frontier_row_table",
        "status": "specified_native_abi_no_backend_implementation",
        "executable": False,
        "app_generic": True,
        "required_native_symbols": (
            "rtdl_optix_collect_cell_mbr_nearest_frontier",
            "rtdl_embree_collect_cell_mbr_nearest_frontier",
            "rtdl_hiprt_collect_cell_mbr_nearest_frontier",
        ),
        "symbol_prototype_template": prototype,
        "supported_dimensions": (2, 3),
        "input_columns": (
            "query_coords:float64[query_count][dimension]",
            "query_point_ids:int64[query_count]",
            "cell_ids:int64[cell_count]",
            "point_begin_offsets:uint64[cell_count]",
            "point_counts:uint64[cell_count]",
            "cell_mbr_min:float64[cell_count][dimension]",
            "cell_mbr_max:float64[cell_count][dimension]",
            "current_best_distances:float64[query_count]",
            "current_best_item_ids:int64[query_count]",
        ),
        "parameters": (
            "dimension:uint32_in_{2,3}",
            "radius:float64_non_negative",
            "max_inline_points:uint64",
            "row_capacity:uint64_total_frontier_row_capacity",
        ),
        "frontier_kind_codes": dict(CELL_MBR_FRONTIER_KIND_CODES),
        "output_row_schema": CELL_MBR_TRAVERSAL_ROW_SCHEMA,
        "output_row_width": len(CELL_MBR_TRAVERSAL_ROW_SCHEMA),
        "outputs": (
            "frontier_kind_codes_out:int64[row_capacity]",
            "query_row_ids_out:int64[row_capacity]",
            "query_point_ids_out:int64[row_capacity]",
            "cell_ids_out:int64[row_capacity]",
            "point_begin_offsets_out:uint64[row_capacity]",
            "point_counts_out:uint64[row_capacity]",
            "min_distances_out:float64[row_capacity]",
            "max_distances_out:float64[row_capacity]",
            "emitted_count_out:uint64",
            "attempted_count_out:uint64",
            "overflowed_out:uint32_bool",
        ),
        "row_schema_semantics": {
            "frontier_kind_code": "1=inline, 2=offload, 3=pruned",
            "query_row_id": "zero-based row index into query columns",
            "query_point_id": "caller-supplied query point id",
            "cell_id": "compact cell id from the generic cell-MBR descriptor",
            "point_begin_offset": "begin offset into the cell's sorted point-id span",
            "point_count": "number of target points in the cell",
            "min_distance": "point-to-cell-MBR lower-bound distance",
            "max_distance": "point-to-cell-MBR upper-bound distance",
        },
        "overflow_policy": "fail_closed_no_partial_rows",
        "overflow_semantics": (
            "If overflowed_out is 1, emitted_count_out must be 0 and callers must "
            "treat all output row arrays as invalid workspace. attempted_count_out "
            "is diagnostic only."
        ),
        "engine_exclusions": (
            "application_distance_law",
            "final_reduction",
            "radius_growth_policy",
            "file_format_loader",
            "benchmark_specific_logic",
            "publication_specific_shortcuts",
        ),
        "claim_boundary": (
            "Generic cell-MBR nearest-frontier ABI only. It specifies a future "
            "native traversal handoff and row schema. No backend implementation, "
            "speedup claim, app algorithm, or benchmark result is authorized."
        ),
    }


def validate_cell_mbr_traversal_native_abi_contract() -> dict[str, object]:
    """Validate and return the generic cell-MBR traversal native ABI contract."""

    contract = cell_mbr_traversal_native_abi_contract()
    required = (
        "primitive",
        "contract",
        "python_reference_contract",
        "row_table_reference_contract",
        "status",
        "executable",
        "app_generic",
        "required_native_symbols",
        "symbol_prototype_template",
        "supported_dimensions",
        "input_columns",
        "parameters",
        "frontier_kind_codes",
        "output_row_schema",
        "output_row_width",
        "outputs",
        "row_schema_semantics",
        "overflow_policy",
        "overflow_semantics",
        "engine_exclusions",
        "claim_boundary",
    )
    for field in required:
        if field not in contract:
            raise ValueError(f"missing cell-MBR traversal ABI field: {field}")
    if contract["contract"] != CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT:
        raise ValueError("cell-MBR traversal ABI contract mismatch")
    if tuple(contract["output_row_schema"]) != CELL_MBR_TRAVERSAL_ROW_SCHEMA:
        raise ValueError("cell-MBR traversal ABI output row schema mismatch")
    if int(contract["output_row_width"]) != len(CELL_MBR_TRAVERSAL_ROW_SCHEMA):
        raise ValueError("cell-MBR traversal ABI output row width mismatch")
    if dict(contract["frontier_kind_codes"]) != dict(CELL_MBR_FRONTIER_KIND_CODES):
        raise ValueError("cell-MBR traversal ABI frontier kind codes mismatch")
    if contract["executable"] is not False:
        raise ValueError("cell-MBR traversal ABI must remain non-executable until a backend exists")
    if contract["app_generic"] is not True:
        raise ValueError("cell-MBR traversal ABI must remain app-generic")
    boundary_text = " ".join(str(value) for value in contract.values()).lower()
    for forbidden in APP_IDENTITY_FORBIDDEN_TOKENS:
        if forbidden in boundary_text:
            raise ValueError(f"cell-MBR traversal ABI leaked app vocabulary: {forbidden}")
    for phrase in ("no backend implementation", "fail_closed_no_partial_rows", "generic cell-mbr"):
        if phrase not in boundary_text:
            raise ValueError("cell-MBR traversal ABI claim boundary is incomplete")
    return contract


def plan_cell_mbr_traversal_lowering(target: str) -> dict[str, object]:
    """Return the current lowering status for generic cell-MBR traversal."""

    normalized = str(target).strip().lower()
    if normalized in {"numpy", "reference", "python"}:
        return {
            "primitive": "cell_mbr_nearest_frontier",
            "contract": "generic_nearest_state_cell_frontier",
            "target": normalized,
            "status": "implemented_numpy_reference_frontier_split",
            "executable": True,
            "native_engine_app_specific": False,
            "outputs": ("nearest_state", "inline_frontier", "offload_frontier", "pruned_frontier"),
            "claim_boundary": "NumPy reference only; no native RT traversal or performance claim.",
        }
    if normalized in {"numpy_row_table", "reference_row_table", "dimension_generic"}:
        return {
            "primitive": "cell_mbr_nearest_frontier",
            "contract": "generic_cell_mbr_nearest_frontier_reference",
            "target": normalized,
            "status": "implemented_dimension_generic_reference_row_table",
            "executable": True,
            "native_engine_app_specific": False,
            "native_backend_complete": False,
            "outputs": ("row_table", "nearest_state", "inline_frontier", "offload_frontier", "pruned_frontier"),
            "backend_options": ("numpy",),
            "claim_boundary": (
                "Dimension-generic NumPy reference row-table front door only; "
                "no native RT traversal, speedup, or app-result claim."
            ),
        }
    if normalized in {"aabb_membership_2d", "aabb-membership-2d", "backend_assisted_2d"}:
        return {
            "primitive": "cell_mbr_nearest_frontier",
            "contract": "generic_cell_mbr_nearest_frontier_aabb_membership_2d",
            "target": normalized,
            "status": "implemented_backend_assisted_2d_frontdoor",
            "executable": True,
            "native_engine_app_specific": False,
            "native_backend_complete": False,
            "outputs": ("row_table", "nearest_state", "inline_frontier", "offload_frontier", "pruned_frontier"),
            "backend_options": ("cpu", "embree", "optix"),
            "claim_boundary": (
                "Executable 2-D AABB-membership-assisted route only; exact "
                "frontier classification remains in generic NumPy; no complete "
                "native ABI backend, speedup, or app-result claim."
            ),
        }
    if normalized in {"aabb_membership_3d", "aabb-membership-3d", "backend_assisted_3d"}:
        return {
            "primitive": "cell_mbr_nearest_frontier",
            "contract": "generic_cell_mbr_nearest_frontier_aabb_membership_3d",
            "target": normalized,
            "status": "implemented_backend_assisted_3d_frontdoor",
            "executable": True,
            "native_engine_app_specific": False,
            "native_backend_complete": False,
            "outputs": ("row_table", "nearest_state", "inline_frontier", "offload_frontier", "pruned_frontier"),
            "backend_options": ("cpu", "optix"),
            "claim_boundary": (
                "Executable 3-D AABB-membership-assisted route only; exact "
                "frontier classification remains in generic NumPy; no complete "
                "native ABI backend, speedup, or app-result claim."
            ),
        }
    if normalized in {"optix_3d", "native_3d_optix", "bounded_optix_3d"}:
        return {
            "primitive": "cell_mbr_nearest_frontier",
            "contract": "generic_cell_mbr_nearest_frontier_native_3d_optix",
            "target": normalized,
            "status": "implemented_bounded_native_3d_optix_backend",
            "executable": True,
            "native_engine_app_specific": False,
            "native_backend_complete": False,
            "outputs": CELL_MBR_TRAVERSAL_ROW_SCHEMA,
            "backend_options": ("optix",),
            "native_symbol": "rtdl_optix_collect_cell_mbr_nearest_frontier_3d",
            "claim_boundary": (
                "Bounded 3-D OptiX backend exists for generic cell-MBR frontier rows; "
                "full 2-D/3-D native ABI backend, speedup, and app-result claims remain unauthorized."
            ),
        }
    if normalized in {"optix", "embree", "hiprt", "native"}:
        return {
            "primitive": "cell_mbr_nearest_frontier",
            "contract": CELL_MBR_TRAVERSAL_NATIVE_ABI_CONTRACT,
            "target": normalized,
            "status": "specified_native_abi_no_backend_implementation",
            "executable": False,
            "native_engine_app_specific": False,
            "outputs": CELL_MBR_TRAVERSAL_ROW_SCHEMA,
            "next_required_step": "implement_backend_symbol_against_validated_generic_abi",
            "claim_boundary": "ABI specified only; no native backend, speedup, or app-result claim.",
        }
    raise ValueError(
        "cell-MBR traversal lowering target must be numpy, reference, python, "
        "numpy_row_table, reference_row_table, dimension_generic, "
        "aabb_membership_2d, aabb_membership_3d, optix_3d, native_3d_optix, "
        "bounded_optix_3d, optix, embree, hiprt, or native"
    )


def directed_hausdorff_2d_numpy_columns(
    source_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    *,
    return_metadata: bool = False,
):
    """Exact directed Hausdorff as a wrapper over generic NumPy primitives."""

    source_ids, _ = _point_columns_for_fields(
        source_point_columns,
        coordinate_fields=("x", "y"),
        label="source",
    )
    target_ids, _ = _point_columns_for_fields(
        target_point_columns,
        coordinate_fields=("x", "y"),
        label="target",
    )
    if source_ids.size == 0 or target_ids.size == 0:
        raise ValueError("directed Hausdorff requires non-empty source and target columns")

    candidates = pairwise_l2_distance_candidate_rows_numpy_columns(
        source_point_columns,
        target_point_columns,
        coordinate_fields=("x", "y"),
    )
    nearest_result = nearest_witness_numpy_columns(
        candidates["candidate_rows"],
        candidates["source_ids"],
        return_metadata=True,
    )
    nearest = nearest_result["per_group_argmin"]
    columns = {
        "source_ids": source_ids,
        "nearest_target_ids": nearest["item_ids"].astype(np.int64, copy=False),
        "nearest_distances": nearest["scores"].astype(np.float64, copy=False),
    }
    witness = max_nearest_distance_witness_numpy_columns(
        {
            "source_ids": columns["source_ids"],
            "nearest_item_ids": columns["nearest_target_ids"],
            "nearest_distances": columns["nearest_distances"],
        },
        group_ids=nearest["group_ids"],
    )
    source_index = int(witness["source_index"])
    metadata = {
        "adapter": "directed_hausdorff_2d_numpy_columns",
        "partner": "numpy",
        "input_contract": "caller_supplied_partner_host_point_columns",
        "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
        "generic_pipeline_contract": (
            "pairwise_l2_distance_candidate_rows -> nearest_witness_columns -> "
            "max_nearest_distance_witness"
        ),
        "native_engine_row_contract": "not_called_partner_reference_only",
        "source_count": int(source_ids.size),
        "target_count": int(target_ids.size),
        "source_id": int(source_ids[source_index]),
        "target_id": int(witness["item_id"]),
        "distance": float(witness["value"]),
        "app_distance_materialization": "partner_numpy_exact_min_then_max_distance_with_witness",
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def directed_hausdorff_3d_numpy_columns(
    source_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    *,
    return_metadata: bool = False,
):
    """Exact directed 3D Hausdorff as a wrapper over generic primitives."""

    source_ids, _ = _point_columns_for_fields(
        source_point_columns,
        coordinate_fields=("x", "y", "z"),
        label="source",
    )
    target_ids, _ = _point_columns_for_fields(
        target_point_columns,
        coordinate_fields=("x", "y", "z"),
        label="target",
    )
    if source_ids.size == 0 or target_ids.size == 0:
        raise ValueError("directed Hausdorff requires non-empty source and target columns")

    candidates = pairwise_l2_distance_candidate_rows_numpy_columns(
        source_point_columns,
        target_point_columns,
        coordinate_fields=("x", "y", "z"),
    )
    nearest_result = nearest_witness_numpy_columns(
        candidates["candidate_rows"],
        candidates["source_ids"],
        return_metadata=True,
    )
    nearest = nearest_result["per_group_argmin"]
    columns = {
        "source_ids": source_ids,
        "nearest_target_ids": nearest["item_ids"].astype(np.int64, copy=False),
        "nearest_distances": nearest["scores"].astype(np.float64, copy=False),
    }
    witness = max_nearest_distance_witness_numpy_columns(
        {
            "source_ids": columns["source_ids"],
            "nearest_item_ids": columns["nearest_target_ids"],
            "nearest_distances": columns["nearest_distances"],
        },
        group_ids=nearest["group_ids"],
    )
    source_index = int(witness["source_index"])
    metadata = {
        "adapter": "directed_hausdorff_3d_numpy_columns",
        "partner": "numpy",
        "input_contract": "caller_supplied_partner_host_point_columns_3d",
        "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
        "generic_pipeline_contract": (
            "pairwise_l2_distance_candidate_rows -> nearest_witness_columns -> "
            "max_nearest_distance_witness"
        ),
        "native_engine_row_contract": "not_called_partner_reference_only",
        "source_count": int(source_ids.size),
        "target_count": int(target_ids.size),
        "source_id": int(source_ids[source_index]),
        "target_id": int(witness["item_id"]),
        "distance": float(witness["value"]),
        "app_distance_materialization": "partner_numpy_exact_3d_min_then_max_distance_with_witness",
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def cupy_group_topk(
    group_ids,
    item_ids,
    scores,
    *,
    group_count: int,
    k: int,
    largest: bool = False,
) -> dict[str, object]:
    """CuPy counterpart of `numpy_group_topk` for pod/device validation."""

    import cupy

    group_ids = cupy.asarray(group_ids, dtype=cupy.int64)
    item_ids = cupy.asarray(item_ids, dtype=cupy.int64)
    scores = cupy.asarray(scores, dtype=cupy.float64)
    group_count = _validate_group_count(group_count)
    k = int(k)
    if k <= 0:
        raise ValueError("k must be positive")
    if not (group_ids.shape == item_ids.shape == scores.shape):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    if int(group_ids.size) and bool(cupy.any((group_ids < 0) | (group_ids >= group_count)).item()):
        raise ValueError("group_ids must be in [0, group_count)")

    out_group_ids = []
    out_item_ids = []
    out_scores = []
    out_ranks = []
    for group in range(group_count):
        positions = cupy.where(group_ids == group)[0]
        if int(positions.size) == 0:
            continue
        group_item_ids = item_ids[positions]
        group_scores = scores[positions]
        primary = -group_scores if largest else group_scores
        item_order = cupy.argsort(group_item_ids, kind="stable")
        primary_order = cupy.argsort(primary[item_order], kind="stable")
        order = item_order[primary_order][:k]
        count = int(order.size)
        out_group_ids.append(cupy.full((count,), group, dtype=cupy.int64))
        out_item_ids.append(group_item_ids[order])
        out_scores.append(group_scores[order])
        out_ranks.append(cupy.arange(1, count + 1, dtype=cupy.int64))

    if not out_group_ids:
        return {
            "group_ids": cupy.asarray([], dtype=cupy.int64),
            "item_ids": cupy.asarray([], dtype=cupy.int64),
            "scores": cupy.asarray([], dtype=cupy.float64),
            "rank": cupy.asarray([], dtype=cupy.int64),
        }
    return {
        "group_ids": cupy.concatenate(out_group_ids),
        "item_ids": cupy.concatenate(out_item_ids),
        "scores": cupy.concatenate(out_scores),
        "rank": cupy.concatenate(out_ranks),
    }


def cupy_group_argmin_then_global_argmax_with_witness(
    group_ids,
    item_ids,
    values,
    *,
    group_count: int,
) -> dict[str, object]:
    """CuPy per-group argmin followed by global argmax with witness ids."""

    import cupy

    top1 = cupy_group_topk(
        group_ids,
        item_ids,
        values,
        group_count=group_count,
        k=1,
        largest=False,
    )
    if int(top1["group_ids"].size) != int(group_count):
        present = set(int(value) for value in cupy.asnumpy(top1["group_ids"]).tolist())
        missing = sorted(set(range(int(group_count))) - present)
        raise ValueError(f"every group must have at least one candidate; missing groups: {missing}")
    item_order = cupy.argsort(top1["item_ids"], kind="stable")
    group_order = item_order[cupy.argsort(top1["group_ids"][item_order], kind="stable")]
    score_order = group_order[cupy.argsort((-top1["scores"])[group_order], kind="stable")]
    winner = int(score_order[0].item())
    return {
        "group_id": int(top1["group_ids"][winner].item()),
        "item_id": int(top1["item_ids"][winner].item()),
        "value": float(top1["scores"][winner].item()),
        "per_group_argmin": top1,
        "contract": "generic_group_argmin_then_global_argmax_with_witness",
    }


def directed_hausdorff_2d_cupy_columns(
    source_point_columns: Mapping[str, object],
    target_point_columns: Mapping[str, object],
    *,
    return_metadata: bool = False,
):
    """Exact directed Hausdorff using generic CuPy partner primitives."""

    import cupy

    source_ids = cupy.asarray(source_point_columns["ids"], dtype=cupy.int64)
    target_ids = cupy.asarray(target_point_columns["ids"], dtype=cupy.int64)
    sx = cupy.asarray(source_point_columns["x"], dtype=cupy.float64)
    sy = cupy.asarray(source_point_columns["y"], dtype=cupy.float64)
    tx = cupy.asarray(target_point_columns["x"], dtype=cupy.float64)
    ty = cupy.asarray(target_point_columns["y"], dtype=cupy.float64)
    if not (source_ids.shape == sx.shape == sy.shape):
        raise ValueError("source ids/x/y must have the same shape")
    if not (target_ids.shape == tx.shape == ty.shape):
        raise ValueError("target ids/x/y must have the same shape")
    if int(source_ids.size) == 0 or int(target_ids.size) == 0:
        raise ValueError("directed Hausdorff requires non-empty source and target columns")

    dx = sx.reshape(-1, 1) - tx.reshape(1, -1)
    dy = sy.reshape(-1, 1) - ty.reshape(1, -1)
    distances = cupy.sqrt(dx * dx + dy * dy)
    group_ids = cupy.repeat(cupy.arange(int(source_ids.size), dtype=cupy.int64), int(target_ids.size))
    item_ids = cupy.tile(target_ids, int(source_ids.size))
    values = distances.reshape(-1)
    witness = cupy_group_argmin_then_global_argmax_with_witness(
        group_ids,
        item_ids,
        values,
        group_count=int(source_ids.size),
    )
    nearest = witness["per_group_argmin"]
    source_index = int(witness["group_id"])
    columns = {
        "source_ids": source_ids,
        "nearest_target_ids": nearest["item_ids"].astype(cupy.int64, copy=False),
        "nearest_distances": nearest["scores"].astype(cupy.float64, copy=False),
    }
    metadata = {
        "adapter": "directed_hausdorff_2d_cupy_columns",
        "partner": "cupy",
        "input_contract": "caller_supplied_partner_device_point_columns",
        "partner_reference_contract": "generic_group_argmin_then_global_argmax_with_witness",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "source_count": int(source_ids.size),
        "target_count": int(target_ids.size),
        "source_id": int(source_ids[source_index].item()),
        "target_id": int(witness["item_id"]),
        "distance": float(witness["value"]),
        "app_distance_materialization": "partner_cupy_exact_min_then_max_distance_with_witness",
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    cupy.cuda.runtime.deviceSynchronize()
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns
