from __future__ import annotations

from .reference import Polygon as _CanonicalPolygon
from .reference import Segment as _CanonicalSegment
from .runtime import _normalize_records
from . import optix_runtime as _optix

_UINT32_MAX = 2**32 - 1
_CUPY_PAIRWISE_FORCE_2D_KERNEL = None


def _require_uint32_id(value: int, label: str) -> int:
    item = int(value)
    if item < 0 or item > _UINT32_MAX:
        raise ValueError(f"{label} IDs must fit uint32 for the current OptiX witness contract")
    return item


def _partner_module(partner: str):
    if partner == "torch":
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("Torch partner adapter requires torch.cuda to be available")

        def count_unique_pairs_by_ids(segment_ids, witness_ray_ids, witness_primitive_ids):
            return partner_group_count_unique_pairs_by_key(
                witness_ray_ids,
                witness_primitive_ids,
                segment_ids,
                partner="torch",
            )

        return {
            "name": "torch",
            "module": torch,
            "device": torch.device("cuda:0"),
            "uint32": torch.uint32,
            "float64": torch.float64,
            "float32": torch.float32,
            "tensor": lambda values, dtype, device: torch.tensor(values, dtype=dtype, device=device),
            "zeros": lambda shape, dtype, device: torch.zeros(shape, dtype=dtype, device=device),
            "sync": torch.cuda.synchronize,
            "to_host": lambda value: [int(item) for item in value.detach().cpu().tolist()],
            "slice": lambda value, count: value[: int(count)],
            "count_unique_pairs_by_ids": count_unique_pairs_by_ids,
            "greater_equal_uint32": lambda value, threshold: value.to(torch.int64).ge(int(threshold)).to(torch.uint32),
            "invert_binary_uint32": lambda value: (1 - value.to(torch.int64)).to(torch.uint32),
            "fixed_radius_count_threshold_2d": lambda query, search, radius, threshold: _torch_fixed_radius_count_threshold_2d(
                torch,
                query,
                search,
                radius,
                threshold,
            ),
        }
    if partner == "cupy":
        import cupy

        if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
            raise RuntimeError("CuPy partner adapter requires a CUDA device")

        def count_unique_pairs_by_ids(segment_ids, witness_ray_ids, witness_primitive_ids):
            return partner_group_count_unique_pairs_by_key(
                witness_ray_ids,
                witness_primitive_ids,
                segment_ids,
                partner="cupy",
            )

        return {
            "name": "cupy",
            "module": cupy,
            "device": None,
            "uint32": cupy.uint32,
            "float64": cupy.float64,
            "float32": cupy.float32,
            "tensor": lambda values, dtype, device: cupy.asarray(values, dtype=dtype),
            "zeros": lambda shape, dtype, device: cupy.zeros(shape, dtype=dtype),
            "sync": cupy.cuda.runtime.deviceSynchronize,
            "to_host": lambda value: [int(item) for item in cupy.asnumpy(value).tolist()],
            "slice": lambda value, count: value[: int(count)],
            "count_unique_pairs_by_ids": count_unique_pairs_by_ids,
            "greater_equal_uint32": lambda value, threshold: (value >= int(threshold)).astype(cupy.uint32, copy=False),
            "invert_binary_uint32": lambda value: (1 - value).astype(cupy.uint32, copy=False),
            "fixed_radius_count_threshold_2d": lambda query, search, radius, threshold: _cupy_fixed_radius_count_threshold_2d(
                cupy,
                query,
                search,
                radius,
                threshold,
            ),
        }
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_group_count_by_key(keys, group_count: int, *, partner: str = "torch"):
    """Count rows per integer key with the selected partner tensor runtime."""
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        if int(keys.numel()) == 0:
            return torch.zeros((group_count,), dtype=torch.uint32, device=keys.device)
        return torch.bincount(keys.to(torch.int64), minlength=group_count).to(torch.uint32)
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        if int(keys.size) == 0:
            return cupy.zeros((group_count,), dtype=cupy.uint32)
        return cupy.bincount(keys.astype(cupy.int64, copy=False), minlength=group_count).astype(cupy.uint32, copy=False)
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_group_sum_by_key(keys, values, group_count: int, *, partner: str = "torch"):
    """Sum values per integer key with the selected partner tensor runtime."""
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        out = torch.zeros((group_count,), dtype=values.dtype, device=values.device)
        if int(keys.numel()) == 0:
            return out
        out.scatter_add_(0, keys.to(torch.int64), values)
        return out
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        out = cupy.zeros((group_count,), dtype=values.dtype)
        if int(keys.size) == 0:
            return out
        cupy.add.at(out, keys.astype(cupy.int64, copy=False), values)
        return out
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_group_max_by_key(keys, values, group_count: int, *, partner: str = "torch", initial=0):
    """Compute max(values) per integer key with the selected partner tensor runtime."""
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        out = torch.full((group_count,), initial, dtype=values.dtype, device=values.device)
        if int(keys.numel()) == 0:
            return out
        return out.scatter_reduce(0, keys.to(torch.int64), values, reduce="amax", include_self=True)
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        out = cupy.full((group_count,), initial, dtype=values.dtype)
        if int(keys.size) == 0:
            return out
        cupy.maximum.at(out, keys.astype(cupy.int64, copy=False), values)
        return out
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_group_min_by_key(keys, values, group_count: int, *, partner: str = "torch", initial=0):
    """Compute min(values) per integer key with the selected partner tensor runtime."""
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        out = torch.full((group_count,), initial, dtype=values.dtype, device=values.device)
        if int(keys.numel()) == 0:
            return out
        return out.scatter_reduce(0, keys.to(torch.int64), values, reduce="amin", include_self=True)
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        out = cupy.full((group_count,), initial, dtype=values.dtype)
        if int(keys.size) == 0:
            return out
        cupy.minimum.at(out, keys.astype(cupy.int64, copy=False), values)
        return out
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_metric_table_reduce_by_key(
    metric_keys,
    values,
    output_metric_keys,
    *,
    partner: str = "torch",
    reduce: str = "sum",
    initial=0,
):
    """Reduce generic metric/value rows into requested output metric keys."""
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        if int(metric_keys.numel()) != int(values.numel()):
            raise ValueError("metric_keys and values must have the same length")
        if int(metric_keys.numel()) == 0:
            return torch.zeros_like(output_metric_keys, dtype=values.dtype)
        output_i64 = output_metric_keys.to(torch.int64)
        metric_i64 = metric_keys.to(torch.int64)
        sorted_output, sorted_to_original = torch.sort(output_i64)
        sorted_positions = torch.searchsorted(sorted_output, metric_i64)
        valid_positions = sorted_positions < int(output_i64.numel())
        if not bool(torch.all(valid_positions).item()):
            raise ValueError("metric_keys must be present in output_metric_keys")
        if not bool(torch.all(sorted_output[sorted_positions] == metric_i64).item()):
            raise ValueError("metric_keys must be present in output_metric_keys")
        group_positions = sorted_to_original[sorted_positions]
        group_count = int(output_i64.numel())
        if reduce == "sum":
            return partner_group_sum_by_key(group_positions, values, group_count, partner=partner)
        if reduce == "max":
            return partner_group_max_by_key(group_positions, values, group_count, partner=partner, initial=initial)
        if reduce == "min":
            return partner_group_min_by_key(group_positions, values, group_count, partner=partner, initial=initial)
        raise ValueError("reduce must be 'sum', 'max', or 'min'")
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        if int(metric_keys.size) != int(values.size):
            raise ValueError("metric_keys and values must have the same length")
        if int(metric_keys.size) == 0:
            return cupy.zeros_like(output_metric_keys, dtype=values.dtype)
        output_i64 = output_metric_keys.astype(cupy.int64, copy=False)
        metric_i64 = metric_keys.astype(cupy.int64, copy=False)
        sorted_to_original = cupy.argsort(output_i64)
        sorted_output = output_i64[sorted_to_original]
        sorted_positions = cupy.searchsorted(sorted_output, metric_i64)
        valid_positions = sorted_positions < int(output_i64.size)
        if not bool(cupy.all(valid_positions).item()):
            raise ValueError("metric_keys must be present in output_metric_keys")
        if not bool(cupy.all(sorted_output[sorted_positions] == metric_i64).item()):
            raise ValueError("metric_keys must be present in output_metric_keys")
        group_positions = sorted_to_original[sorted_positions].astype(cupy.int64, copy=False)
        group_count = int(output_i64.size)
        if reduce == "sum":
            return partner_group_sum_by_key(group_positions, values, group_count, partner=partner)
        if reduce == "max":
            return partner_group_max_by_key(group_positions, values, group_count, partner=partner, initial=initial)
        if reduce == "min":
            return partner_group_min_by_key(group_positions, values, group_count, partner=partner, initial=initial)
        raise ValueError("reduce must be 'sum', 'max', or 'min'")
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_mask_indices(mask, *, partner: str = "torch"):
    """Return partner-owned indices where mask is true/non-zero."""
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        return torch.nonzero(mask.to(torch.bool), as_tuple=False).reshape(-1).to(torch.int64)
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        return cupy.nonzero(mask.astype(cupy.bool_, copy=False))[0].astype(cupy.int64, copy=False)
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_take_columns_by_indices(columns: dict[str, object], indices, *, partner: str = "torch"):
    """Take the same partner-owned row indices from each column."""
    runtime = _partner_module(partner)
    if runtime["name"] in ("torch", "cupy"):
        return {name: column[indices] for name, column in columns.items()}
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_compact_columns_by_mask(columns: dict[str, object], mask, *, partner: str = "torch"):
    """Compact partner-owned columns by a true/non-zero mask without host rows."""
    indices = partner_mask_indices(mask, partner=partner)
    return partner_take_columns_by_indices(columns, indices, partner=partner)


def partner_group_any_by_key(keys, flags, group_count: int, *, partner: str = "torch"):
    """Reduce binary/int flags to one any-hit flag per integer key."""
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        out = torch.zeros((int(group_count),), dtype=torch.int64, device=flags.device)
        if int(keys.numel()) == 0:
            return out.to(torch.uint32)
        out.scatter_add_(0, keys.to(torch.int64), flags.to(torch.int64))
        return out.gt(0).to(torch.uint32)
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        sums = partner_group_sum_by_key(keys, flags, group_count, partner=partner)
        return (sums > 0).astype(cupy.uint32, copy=False)
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_unique_pair_keys(left_keys, right_keys, *, partner: str = "torch"):
    """Return unique left/right key pairs without host materialization."""
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        if int(left_keys.numel()) == 0:
            return left_keys, right_keys
        right_i64 = right_keys.to(torch.int64)
        modulus = torch.max(right_i64) + 1
        encoded = left_keys.to(torch.int64) * modulus + right_i64
        unique = torch.unique(encoded)
        return (
            torch.div(unique, modulus, rounding_mode="floor").to(left_keys.dtype),
            (unique % modulus).to(right_keys.dtype),
        )
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        if int(left_keys.size) == 0:
            return left_keys, right_keys
        right_i64 = right_keys.astype(cupy.int64, copy=False)
        modulus = cupy.max(right_i64) + cupy.asarray(1, dtype=cupy.int64)
        encoded = left_keys.astype(cupy.int64, copy=False) * modulus + right_i64
        unique = cupy.unique(encoded)
        return (
            (unique // modulus).astype(left_keys.dtype, copy=False),
            (unique % modulus).astype(right_keys.dtype, copy=False),
        )
    raise ValueError("partner must be 'torch' or 'cupy'")


def partner_group_count_unique_pairs_by_key(group_keys, item_keys, output_group_keys, *, partner: str = "torch"):
    """Count unique (group_key, item_key) pairs per requested output group key."""
    runtime = _partner_module(partner)
    if runtime["name"] == "torch":
        torch = runtime["module"]
        if int(group_keys.numel()) != int(item_keys.numel()):
            raise ValueError("group_keys and item_keys must have the same length")
        if int(group_keys.numel()) == 0:
            return torch.zeros_like(output_group_keys, dtype=torch.uint32)
        output_i64 = output_group_keys.to(torch.int64)
        group_i64 = group_keys.to(torch.int64)
        item_i64 = item_keys.to(torch.int64)
        if bool(torch.any(item_i64 < 0).item()):
            raise ValueError("item_keys must be non-negative")
        sorted_output, sorted_to_original = torch.sort(output_i64)
        sorted_positions = torch.searchsorted(sorted_output, group_i64)
        valid_positions = sorted_positions < int(output_i64.numel())
        if not bool(torch.all(valid_positions).item()):
            raise ValueError("group_keys must be present in output_group_keys")
        if not bool(torch.all(sorted_output[sorted_positions] == group_i64).item()):
            raise ValueError("group_keys must be present in output_group_keys")
        group_positions = sorted_to_original[sorted_positions]
        item_modulus = torch.max(item_i64) + 1
        unique_pairs = torch.unique(group_positions * item_modulus + item_i64)
        unique_positions = torch.div(unique_pairs, item_modulus, rounding_mode="floor")
        return torch.bincount(unique_positions, minlength=int(output_group_keys.numel())).to(torch.uint32)
    if runtime["name"] == "cupy":
        cupy = runtime["module"]
        if int(group_keys.size) != int(item_keys.size):
            raise ValueError("group_keys and item_keys must have the same length")
        if int(group_keys.size) == 0:
            return cupy.zeros_like(output_group_keys, dtype=cupy.uint32)
        output_i64 = output_group_keys.astype(cupy.int64, copy=False)
        group_i64 = group_keys.astype(cupy.int64, copy=False)
        item_i64 = item_keys.astype(cupy.int64, copy=False)
        if bool(cupy.any(item_i64 < 0).item()):
            raise ValueError("item_keys must be non-negative")
        sorted_to_original = cupy.argsort(output_i64)
        sorted_output = output_i64[sorted_to_original]
        sorted_positions = cupy.searchsorted(sorted_output, group_i64)
        valid_positions = sorted_positions < int(output_i64.size)
        if not bool(cupy.all(valid_positions).item()):
            raise ValueError("group_keys must be present in output_group_keys")
        if not bool(cupy.all(sorted_output[sorted_positions] == group_i64).item()):
            raise ValueError("group_keys must be present in output_group_keys")
        group_positions = sorted_to_original[sorted_positions].astype(cupy.int64, copy=False)
        item_modulus = cupy.max(item_i64) + cupy.asarray(1, dtype=cupy.int64)
        unique_pairs = cupy.unique(group_positions * item_modulus + item_i64)
        unique_positions = unique_pairs // item_modulus
        return cupy.bincount(unique_positions, minlength=int(output_group_keys.size)).astype(cupy.uint32, copy=False)
    raise ValueError("partner must be 'torch' or 'cupy'")


def _count_unique_pairs_for_runtime(runtime, output_group_keys, group_keys, item_keys):
    if runtime["name"] in ("torch", "cupy"):
        return partner_group_count_unique_pairs_by_key(
            group_keys,
            item_keys,
            output_group_keys,
            partner=runtime["name"],
        )
    if "count_unique_pairs_by_ids" in runtime:
        return runtime["count_unique_pairs_by_ids"](output_group_keys, group_keys, item_keys)
    raise ValueError("runtime must provide a supported partner name or count_unique_pairs_by_ids fallback")


def _torch_fixed_radius_count_threshold_2d(torch, query_columns, search_columns, radius, threshold):
    qx = query_columns["x"].to(torch.float64)
    qy = query_columns["y"].to(torch.float64)
    sx = search_columns["x"].to(torch.float64)
    sy = search_columns["y"].to(torch.float64)
    if int(qx.numel()) == 0:
        return torch.zeros((0,), dtype=torch.uint32, device=qx.device)
    if int(sx.numel()) == 0:
        return torch.zeros_like(query_columns["ids"], dtype=torch.uint32)
    radius_sq = float(radius) * float(radius)
    dx = qx.reshape(-1, 1) - sx.reshape(1, -1)
    dy = qy.reshape(-1, 1) - sy.reshape(1, -1)
    within = (dx * dx + dy * dy).le(radius_sq)
    counts = torch.sum(within.to(torch.int64), dim=1)
    return counts.to(torch.uint32)


def _cupy_fixed_radius_count_threshold_2d(cupy, query_columns, search_columns, radius, threshold):
    qx = query_columns["x"].astype(cupy.float64, copy=False)
    qy = query_columns["y"].astype(cupy.float64, copy=False)
    sx = search_columns["x"].astype(cupy.float64, copy=False)
    sy = search_columns["y"].astype(cupy.float64, copy=False)
    if int(qx.size) == 0:
        return cupy.zeros((0,), dtype=cupy.uint32)
    if int(sx.size) == 0:
        return cupy.zeros_like(query_columns["ids"], dtype=cupy.uint32)
    radius_sq = float(radius) * float(radius)
    dx = qx.reshape(-1, 1) - sx.reshape(1, -1)
    dy = qy.reshape(-1, 1) - sy.reshape(1, -1)
    within = (dx * dx + dy * dy) <= radius_sq
    counts = cupy.sum(within.astype(cupy.int64, copy=False), axis=1)
    return counts.astype(cupy.uint32, copy=False)


def _segment_ray_columns(segments: tuple[_CanonicalSegment, ...], partner: dict) -> dict[str, object]:
    device = partner["device"]
    return {
        "ids": partner["tensor"](
            [_require_uint32_id(segment.id, "segment") for segment in segments],
            partner["uint32"],
            device,
        ),
        "ox": partner["tensor"]([segment.x0 for segment in segments], partner["float64"], device),
        "oy": partner["tensor"]([segment.y0 for segment in segments], partner["float64"], device),
        "dx": partner["tensor"]([segment.x1 - segment.x0 for segment in segments], partner["float64"], device),
        "dy": partner["tensor"]([segment.y1 - segment.y0 for segment in segments], partner["float64"], device),
        "tmax": partner["tensor"]([1.0 for _ in segments], partner["float64"], device),
    }


def _point_columns(points, partner: dict) -> dict[str, object]:
    device = partner["device"]
    return {
        "ids": partner["tensor"](
            [_require_uint32_id(point.id, "point") for point in points],
            partner["uint32"],
            device,
        ),
        "x": partner["tensor"]([point.x for point in points], partner["float64"], device),
        "y": partner["tensor"]([point.y for point in points], partner["float64"], device),
    }


def point_rows_to_partner_columns(points, *, partner: str = "torch") -> dict[str, object]:
    """Convert point rows into partner-owned generic point columns."""
    runtime = _partner_module(partner)
    return _point_columns(tuple(points), runtime)


def weighted_point_rows_to_partner_columns(points, *, partner: str = "torch") -> dict[str, object]:
    """Convert rows with id/x/y/mass attributes into partner-owned weighted point columns."""
    runtime = _partner_module(partner)
    device = runtime["device"]
    rows = tuple(points)
    return {
        "ids": runtime["tensor"](
            [_require_uint32_id(point.id, "point") for point in rows],
            runtime["uint32"],
            device,
        ),
        "x": runtime["tensor"]([float(point.x) for point in rows], runtime["float64"], device),
        "y": runtime["tensor"]([float(point.y) for point in rows], runtime["float64"], device),
        "weight": runtime["tensor"]([float(point.mass) for point in rows], runtime["float64"], device),
    }


def _cupy_pairwise_force_2d_kernel(cupy):
    global _CUPY_PAIRWISE_FORCE_2D_KERNEL
    if _CUPY_PAIRWISE_FORCE_2D_KERNEL is None:
        _CUPY_PAIRWISE_FORCE_2D_KERNEL = cupy.RawKernel(
            r'''
            extern "C" __global__
            void pairwise_force_2d(
                const unsigned int* source_ids,
                const double* sx,
                const double* sy,
                const double* sm,
                const int source_count,
                const unsigned int* target_ids,
                const double* tx,
                const double* ty,
                const double* tm,
                const int target_count,
                const double softening_sq,
                const int exclude_equal_ids,
                double* out_fx,
                double* out_fy
            ) {
                const int i = blockDim.x * blockIdx.x + threadIdx.x;
                if (i >= source_count) {
                    return;
                }
                const double source_x = sx[i];
                const double source_y = sy[i];
                const double source_mass = sm[i];
                const unsigned int source_id = source_ids[i];
                double fx = 0.0;
                double fy = 0.0;
                for (int j = 0; j < target_count; ++j) {
                    if (exclude_equal_ids && source_id == target_ids[j]) {
                        continue;
                    }
                    const double dx = tx[j] - source_x;
                    const double dy = ty[j] - source_y;
                    const double dist_sq = dx * dx + dy * dy + softening_sq;
                    const double inv_dist = rsqrt(dist_sq);
                    const double scale = source_mass * tm[j] * inv_dist * inv_dist * inv_dist;
                    fx += dx * scale;
                    fy += dy * scale;
                }
                out_fx[i] = fx;
                out_fy[i] = fy;
            }
            ''',
            "pairwise_force_2d",
        )
    return _CUPY_PAIRWISE_FORCE_2D_KERNEL


def pairwise_inverse_square_force_2d_partner_columns(
    source_weighted_point_columns: dict[str, object],
    target_weighted_point_columns: dict[str, object],
    *,
    softening: float = 0.0,
    partner: str = "torch",
    exclude_equal_ids: bool = True,
    return_metadata: bool = False,
):
    """Compute pairwise softened inverse-square force vectors over generic weighted points."""
    softening = float(softening)
    if softening < 0:
        raise ValueError("softening must be non-negative")
    runtime = _partner_module(partner)
    source_count = _column_length(source_weighted_point_columns, "ids")
    target_count = _column_length(target_weighted_point_columns, "ids")
    if source_count <= 0 or target_count <= 0:
        raise ValueError("force accumulation requires non-empty source and target columns")

    if runtime["name"] == "torch":
        torch = runtime["module"]
        sx = source_weighted_point_columns["x"].to(torch.float64)
        sy = source_weighted_point_columns["y"].to(torch.float64)
        sm = source_weighted_point_columns["weight"].to(torch.float64)
        tx = target_weighted_point_columns["x"].to(torch.float64)
        ty = target_weighted_point_columns["y"].to(torch.float64)
        tm = target_weighted_point_columns["weight"].to(torch.float64)
        dx = tx.reshape(1, -1) - sx.reshape(-1, 1)
        dy = ty.reshape(1, -1) - sy.reshape(-1, 1)
        dist_sq = dx * dx + dy * dy + softening * softening
        if exclude_equal_ids:
            same_id = source_weighted_point_columns["ids"].reshape(-1, 1) == target_weighted_point_columns["ids"].reshape(1, -1)
            dist_sq = torch.where(same_id, torch.ones_like(dist_sq), dist_sq)
        inv_dist = torch.rsqrt(dist_sq)
        scale = sm.reshape(-1, 1) * tm.reshape(1, -1) * inv_dist * inv_dist * inv_dist
        if exclude_equal_ids:
            scale = torch.where(same_id, torch.zeros_like(scale), scale)
        force_x = torch.sum(dx * scale, dim=1)
        force_y = torch.sum(dy * scale, dim=1)
    elif runtime["name"] == "cupy":
        cupy = runtime["module"]
        sx = source_weighted_point_columns["x"].astype(cupy.float64, copy=False)
        sy = source_weighted_point_columns["y"].astype(cupy.float64, copy=False)
        sm = source_weighted_point_columns["weight"].astype(cupy.float64, copy=False)
        tx = target_weighted_point_columns["x"].astype(cupy.float64, copy=False)
        ty = target_weighted_point_columns["y"].astype(cupy.float64, copy=False)
        tm = target_weighted_point_columns["weight"].astype(cupy.float64, copy=False)
        force_x = cupy.zeros((source_count,), dtype=cupy.float64)
        force_y = cupy.zeros((source_count,), dtype=cupy.float64)
        threads = 128
        blocks = (source_count + threads - 1) // threads
        kernel = _cupy_pairwise_force_2d_kernel(cupy)
        kernel(
            (blocks,),
            (threads,),
            (
                source_weighted_point_columns["ids"].astype(cupy.uint32, copy=False),
                sx,
                sy,
                sm,
                source_count,
                target_weighted_point_columns["ids"].astype(cupy.uint32, copy=False),
                tx,
                ty,
                tm,
                target_count,
                softening * softening,
                1 if exclude_equal_ids else 0,
                force_x,
                force_y,
            ),
        )
    else:
        raise ValueError("partner must be 'torch' or 'cupy'")

    runtime["sync"]()
    columns = {
        "source_ids": source_weighted_point_columns["ids"],
        "force_x": force_x,
        "force_y": force_y,
    }
    metadata = {
        "adapter": "pairwise_inverse_square_force_2d_partner_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_weighted_point_columns",
        "partner_reference_contract": "generic_pairwise_inverse_square_force_2d",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "source_count": source_count,
        "target_count": target_count,
        "softening": softening,
        "exclude_equal_ids": exclude_equal_ids,
        "app_force_materialization": "partner_gpu_pairwise_vector_sum",
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def directed_hausdorff_2d_partner_columns(
    source_point_columns: dict[str, object],
    target_point_columns: dict[str, object],
    *,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Compute exact directed Hausdorff distance from generic point columns."""
    runtime = _partner_module(partner)
    source_count = _column_length(source_point_columns, "ids")
    target_count = _column_length(target_point_columns, "ids")
    if source_count <= 0 or target_count <= 0:
        raise ValueError("directed Hausdorff requires non-empty source and target columns")

    if runtime["name"] == "torch":
        torch = runtime["module"]
        sx = source_point_columns["x"].to(torch.float64)
        sy = source_point_columns["y"].to(torch.float64)
        tx = target_point_columns["x"].to(torch.float64)
        ty = target_point_columns["y"].to(torch.float64)
        dx = sx.reshape(-1, 1) - tx.reshape(1, -1)
        dy = sy.reshape(-1, 1) - ty.reshape(1, -1)
        distance_sq = dx * dx + dy * dy
        nearest_distance_sq, nearest_indices = torch.min(distance_sq, dim=1)
        directed_distance_sq, source_index = torch.max(nearest_distance_sq, dim=0)
        source_index_i = int(source_index.detach().cpu().item())
        target_index_i = int(nearest_indices[source_index_i].detach().cpu().item())
        directed_distance = torch.sqrt(directed_distance_sq)
        nearest_distances = torch.sqrt(nearest_distance_sq)
    elif runtime["name"] == "cupy":
        cupy = runtime["module"]
        sx = source_point_columns["x"].astype(cupy.float64, copy=False)
        sy = source_point_columns["y"].astype(cupy.float64, copy=False)
        tx = target_point_columns["x"].astype(cupy.float64, copy=False)
        ty = target_point_columns["y"].astype(cupy.float64, copy=False)
        dx = sx.reshape(-1, 1) - tx.reshape(1, -1)
        dy = sy.reshape(-1, 1) - ty.reshape(1, -1)
        distance_sq = dx * dx + dy * dy
        nearest_distance_sq = cupy.min(distance_sq, axis=1)
        nearest_indices = cupy.argmin(distance_sq, axis=1)
        source_index = cupy.argmax(nearest_distance_sq)
        source_index_i = int(source_index.item())
        target_index_i = int(nearest_indices[source_index_i].item())
        directed_distance_sq = nearest_distance_sq[source_index_i]
        directed_distance = cupy.sqrt(directed_distance_sq)
        nearest_distances = cupy.sqrt(nearest_distance_sq)
    else:
        raise ValueError("partner must be 'torch' or 'cupy'")

    runtime["sync"]()
    columns = {
        "source_ids": source_point_columns["ids"],
        "nearest_target_ids": target_point_columns["ids"][nearest_indices],
        "nearest_distances": nearest_distances,
    }
    metadata = {
        "adapter": "directed_hausdorff_2d_partner_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "partner_reference_contract": "generic_exact_directed_hausdorff_2d",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "source_count": source_count,
        "target_count": target_count,
        "source_id": int(runtime["to_host"](source_point_columns["ids"][source_index_i : source_index_i + 1])[0]),
        "target_id": int(runtime["to_host"](target_point_columns["ids"][target_index_i : target_index_i + 1])[0]),
        "distance": float(directed_distance.detach().cpu().item())
        if runtime["name"] == "torch"
        else float(directed_distance.item()),
        "distance_sq": float(directed_distance_sq.detach().cpu().item())
        if runtime["name"] == "torch"
        else float(directed_distance_sq.item()),
        "app_distance_materialization": "partner_gpu_exact_min_then_max_distance",
        "app_distance_host_materialization": False,
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def top_k_nearest_points_2d_partner_columns(
    query_point_columns: dict[str, object],
    candidate_point_columns: dict[str, object],
    *,
    k: int,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Compute exact ranked nearest candidate points from generic point columns."""
    k = int(k)
    if k <= 0:
        raise ValueError("k must be positive")
    runtime = _partner_module(partner)
    query_count = _column_length(query_point_columns, "ids")
    candidate_count = _column_length(candidate_point_columns, "ids")
    if query_count <= 0 or candidate_count <= 0:
        raise ValueError("top-k nearest points requires non-empty query and candidate columns")
    if k > candidate_count:
        raise ValueError("k must be <= candidate point count")

    if runtime["name"] == "torch":
        torch = runtime["module"]
        qx = query_point_columns["x"].to(torch.float64)
        qy = query_point_columns["y"].to(torch.float64)
        cx = candidate_point_columns["x"].to(torch.float64)
        cy = candidate_point_columns["y"].to(torch.float64)
        candidate_ids_i64 = candidate_point_columns["ids"].to(torch.int64)
        candidate_id_order = torch.argsort(candidate_ids_i64)
        dx = qx.reshape(-1, 1) - cx.reshape(1, -1)
        dy = qy.reshape(-1, 1) - cy.reshape(1, -1)
        distance_sq_by_id = (dx * dx + dy * dy)[:, candidate_id_order]
        rank_order_by_id = torch.argsort(distance_sq_by_id, dim=1, stable=True)[:, :k]
        nearest_indices = candidate_id_order[rank_order_by_id]
        nearest_distance_sq = torch.gather(dx * dx + dy * dy, 1, nearest_indices)
        query_ids = query_point_columns["ids"].reshape(-1, 1).expand(query_count, k).reshape(-1)
        neighbor_ids = candidate_point_columns["ids"][nearest_indices].reshape(-1)
        distances = torch.sqrt(nearest_distance_sq).reshape(-1)
        neighbor_rank = (
            torch.arange(1, k + 1, dtype=torch.int64, device=query_ids.device)
            .to(query_point_columns["ids"].dtype)
            .reshape(1, k)
            .expand(query_count, k)
            .reshape(-1)
        )
    elif runtime["name"] == "cupy":
        cupy = runtime["module"]
        qx = query_point_columns["x"].astype(cupy.float64, copy=False)
        qy = query_point_columns["y"].astype(cupy.float64, copy=False)
        cx = candidate_point_columns["x"].astype(cupy.float64, copy=False)
        cy = candidate_point_columns["y"].astype(cupy.float64, copy=False)
        candidate_ids_i64 = candidate_point_columns["ids"].astype(cupy.int64, copy=False)
        candidate_id_order = cupy.argsort(candidate_ids_i64)
        dx = qx.reshape(-1, 1) - cx.reshape(1, -1)
        dy = qy.reshape(-1, 1) - cy.reshape(1, -1)
        distance_sq = dx * dx + dy * dy
        distance_sq_by_id = distance_sq[:, candidate_id_order]
        rank_order_by_id = cupy.argsort(distance_sq_by_id, axis=1, kind="stable")[:, :k]
        nearest_indices = candidate_id_order[rank_order_by_id]
        nearest_distance_sq = cupy.take_along_axis(distance_sq, nearest_indices, axis=1)
        query_ids = cupy.repeat(query_point_columns["ids"], k)
        neighbor_ids = candidate_point_columns["ids"][nearest_indices].reshape(-1)
        distances = cupy.sqrt(nearest_distance_sq).reshape(-1)
        neighbor_rank = cupy.tile(cupy.arange(1, k + 1, dtype=cupy.uint32), query_count)
    else:
        raise ValueError("partner must be 'torch' or 'cupy'")

    runtime["sync"]()
    columns = {
        "query_ids": query_ids,
        "neighbor_ids": neighbor_ids,
        "distances": distances,
        "neighbor_rank": neighbor_rank,
    }
    metadata = {
        "adapter": "top_k_nearest_points_2d_partner_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "partner_reference_contract": "generic_exact_top_k_nearest_points_2d",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "query_count": query_count,
        "candidate_count": candidate_count,
        "k": k,
        "tie_break": "distance_then_candidate_id",
        "app_row_materialization": "caller_optional",
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def radius_graph_components_2d_partner_columns(
    point_columns: dict[str, object],
    *,
    radius: float,
    min_neighbors: int,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Label radius-graph core components over generic point columns."""
    radius = float(radius)
    min_neighbors = int(min_neighbors)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if min_neighbors < 1:
        raise ValueError("min_neighbors must be at least 1")
    runtime = _partner_module(partner)
    point_count = _column_length(point_columns, "ids")
    if point_count <= 0:
        raise ValueError("radius graph components requires non-empty point columns")

    if runtime["name"] == "torch":
        torch = runtime["module"]
        x = point_columns["x"].to(torch.float64)
        y = point_columns["y"].to(torch.float64)
        dx = x.reshape(-1, 1) - x.reshape(1, -1)
        dy = y.reshape(-1, 1) - y.reshape(1, -1)
        within = (dx * dx + dy * dy).le(radius * radius)
        neighbor_counts = torch.sum(within.to(torch.int64), dim=1)
        is_core = neighbor_counts.ge(min_neighbors)
        labels = torch.arange(point_count, dtype=torch.int64, device=x.device)
        active = within & is_core.reshape(-1, 1) & is_core.reshape(1, -1)
        for _ in range(point_count):
            candidate = torch.where(active, labels.reshape(1, -1), torch.full_like(active.to(torch.int64), point_count))
            new_labels = torch.minimum(labels, torch.min(candidate, dim=1).values)
            if bool(torch.all(new_labels == labels).item()):
                break
            labels = new_labels
        core_labels = torch.where(is_core, labels, torch.full_like(labels, -1))
        border_candidates = torch.where(
            within & is_core.reshape(1, -1),
            labels.reshape(1, -1),
            torch.full_like(within.to(torch.int64), point_count),
        )
        border_labels = torch.min(border_candidates, dim=1).values
        component_labels = torch.where(is_core, core_labels, torch.where(border_labels < point_count, border_labels, torch.full_like(labels, -1)))
        unique_labels = torch.unique(component_labels[component_labels >= 0])
        dense = torch.full_like(component_labels, -1)
        for index, label in enumerate(unique_labels.detach().cpu().tolist(), start=1):
            dense = torch.where(component_labels == int(label), torch.full_like(dense, index), dense)
        core_u32 = is_core.to(torch.uint32)
        counts_u32 = neighbor_counts.to(torch.uint32)
    elif runtime["name"] == "cupy":
        cupy = runtime["module"]
        x = point_columns["x"].astype(cupy.float64, copy=False)
        y = point_columns["y"].astype(cupy.float64, copy=False)
        dx = x.reshape(-1, 1) - x.reshape(1, -1)
        dy = y.reshape(-1, 1) - y.reshape(1, -1)
        within = (dx * dx + dy * dy) <= (radius * radius)
        neighbor_counts = cupy.sum(within.astype(cupy.int64, copy=False), axis=1)
        is_core = neighbor_counts >= min_neighbors
        labels = cupy.arange(point_count, dtype=cupy.int64)
        active = within & is_core.reshape(-1, 1) & is_core.reshape(1, -1)
        sentinel = cupy.asarray(point_count, dtype=cupy.int64)
        for _ in range(point_count):
            candidate = cupy.where(active, labels.reshape(1, -1), sentinel)
            new_labels = cupy.minimum(labels, cupy.min(candidate, axis=1))
            if bool(cupy.all(new_labels == labels).item()):
                break
            labels = new_labels
        core_labels = cupy.where(is_core, labels, cupy.full_like(labels, -1))
        border_candidates = cupy.where(
            within & is_core.reshape(1, -1),
            labels.reshape(1, -1),
            sentinel,
        )
        border_labels = cupy.min(border_candidates, axis=1)
        component_labels = cupy.where(
            is_core,
            core_labels,
            cupy.where(border_labels < point_count, border_labels, cupy.full_like(labels, -1)),
        )
        unique_labels = cupy.unique(component_labels[component_labels >= 0])
        dense = cupy.full_like(component_labels, -1)
        for index, label in enumerate(cupy.asnumpy(unique_labels).tolist(), start=1):
            dense = cupy.where(component_labels == int(label), cupy.full_like(dense, index), dense)
        core_u32 = is_core.astype(cupy.uint32, copy=False)
        counts_u32 = neighbor_counts.astype(cupy.uint32, copy=False)
    else:
        raise ValueError("partner must be 'torch' or 'cupy'")

    runtime["sync"]()
    columns = {
        "point_ids": point_columns["ids"],
        "component_labels": dense,
        "is_core": core_u32,
        "neighbor_counts": counts_u32,
    }
    metadata = {
        "adapter": "radius_graph_components_2d_partner_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "partner_reference_contract": "generic_radius_graph_component_labels_2d",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "point_count": point_count,
        "radius": radius,
        "min_neighbors": min_neighbors,
        "component_label_policy": "dense_positive_labels_by_lowest_component_seed_noise_minus_one",
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def _polygon_triangle_columns(polygons: tuple[_CanonicalPolygon, ...], partner: dict) -> tuple[dict[str, object], object]:
    ids: list[int] = []
    x0: list[float] = []
    y0: list[float] = []
    x1: list[float] = []
    y1: list[float] = []
    x2: list[float] = []
    y2: list[float] = []
    aabbs: list[list[float]] = []
    for polygon in polygons:
        vertices = tuple((float(x), float(y)) for x, y in polygon.vertices)
        if len(vertices) < 3:
            raise ValueError("polygons must have at least three vertices")
        anchor_x, anchor_y = vertices[0]
        for index in range(1, len(vertices) - 1):
            bx, by = vertices[index]
            cx, cy = vertices[index + 1]
            ids.append(_require_uint32_id(polygon.id, "polygon"))
            x0.append(anchor_x)
            y0.append(anchor_y)
            x1.append(bx)
            y1.append(by)
            x2.append(cx)
            y2.append(cy)
            min_x = min(anchor_x, bx, cx)
            min_y = min(anchor_y, by, cy)
            max_x = max(anchor_x, bx, cx)
            max_y = max(anchor_y, by, cy)
            aabbs.append([min_x, min_y, -1.0e-4, max_x, max_y, 1.0e-4])
    device = partner["device"]
    columns = {
        "ids": partner["tensor"](ids, partner["uint32"], device),
        "x0": partner["tensor"](x0, partner["float64"], device),
        "y0": partner["tensor"](y0, partner["float64"], device),
        "x1": partner["tensor"](x1, partner["float64"], device),
        "y1": partner["tensor"](y1, partner["float64"], device),
        "x2": partner["tensor"](x2, partner["float64"], device),
        "y2": partner["tensor"](y2, partner["float64"], device),
    }
    return columns, partner["tensor"](aabbs, partner["float32"], device)


def segment_polygon_anyhit_rows_optix_partner(
    segments,
    polygons,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Run segment/polygon any-hit rows as a Python+partner+RTDL adapter.

    The native engine sees only generic ray/primitive witness IDs. Polygon
    triangulation, duplicate removal, and row naming live in Python.
    """
    normalized_segments = tuple(
        segments
        if isinstance(segments, tuple) and all(isinstance(item, _CanonicalSegment) for item in segments)
        else _normalize_records("segments", "segments", segments)
    )
    normalized_polygons = tuple(
        polygons
        if isinstance(polygons, tuple) and all(isinstance(item, _CanonicalPolygon) for item in polygons)
        else _normalize_records("polygons", "polygons", polygons)
    )
    if not normalized_segments or not normalized_polygons:
        rows: tuple[dict[str, int], ...] = ()
        metadata = {
            "adapter": "segment_polygon_anyhit_rows_optix_partner",
            "partner": partner,
            "app_rows_emitted": 0,
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
        if return_metadata:
            return {"rows": rows, "metadata": metadata}
        return rows
    if output_capacity is None:
        triangle_capacity = sum(max(0, len(polygon.vertices) - 2) for polygon in normalized_polygons)
        output_capacity = max(1, len(normalized_segments) * triangle_capacity)
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")

    runtime = _partner_module(partner)
    rays = _segment_ray_columns(normalized_segments, runtime)
    triangles, triangle_aabbs = _polygon_triangle_columns(normalized_polygons, runtime)
    witness_ray_ids = runtime["zeros"]((output_capacity,), runtime["uint32"], runtime["device"])
    witness_primitive_ids = runtime["zeros"]((output_capacity,), runtime["uint32"], runtime["device"])

    scene = _optix.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
        triangles,
        triangle_aabbs,
    )
    try:
        packet = scene.write_device_any_hit_all_witnesses(
            rays,
            witness_ray_ids,
            witness_primitive_ids,
        )
        runtime["sync"]()
    finally:
        scene.close()

    metadata = dict(packet["metadata"])
    emitted_count = int(metadata["emitted_count"])
    if metadata["overflowed"]:
        raise RuntimeError("partner segment/polygon adapter overflowed; increase output_capacity")
    ray_ids = runtime["to_host"](witness_ray_ids)[:emitted_count]
    primitive_ids = runtime["to_host"](witness_primitive_ids)[:emitted_count]
    rows = tuple(
        {"segment_id": segment_id, "polygon_id": polygon_id}
        for segment_id, polygon_id in sorted(set(zip(ray_ids, primitive_ids)))
    )
    metadata.update(
        {
            "adapter": "segment_polygon_anyhit_rows_optix_partner",
            "partner": runtime["name"],
            "app_rows_emitted": len(rows),
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"rows": rows, "metadata": metadata}
    return rows


def _column_length(columns: dict[str, object], name: str) -> int:
    column = columns[name]
    shape = getattr(column, "shape", None)
    if shape is not None:
        return int(shape[0])
    values = getattr(column, "values", None)
    if values is not None:
        return len(values)
    try:
        return len(column)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ValueError(f"{name} column must expose shape[0] or a length") from exc


def _segment_polygon_all_witness_columns_optix_partner_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object] | None,
    polygon_triangle_aabbs,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    prepared_scene=None,
    witness_output_columns: dict[str, object] | None = None,
):
    ray_count = _column_length(segment_ray_columns, "ids")
    if prepared_scene is not None:
        triangle_count = int(getattr(getattr(prepared_scene, "_packed_triangles", None), "count", 0))
    elif polygon_triangle_columns is not None:
        triangle_count = _column_length(polygon_triangle_columns, "ids")
    else:
        raise ValueError("polygon_triangle_columns are required when prepared_scene is not supplied")
    runtime = _partner_module(partner)
    if ray_count == 0 or triangle_count == 0:
        metadata = {
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "emitted_count": 0,
            "overflowed": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
        empty = runtime["zeros"]((0,), runtime["uint32"], runtime["device"])
        return {
            "runtime": runtime,
            "witness_ray_ids": empty,
            "witness_primitive_ids": empty,
            "emitted_count": 0,
            "metadata": metadata,
        }
    if output_capacity is None:
        output_capacity = max(1, ray_count * triangle_count)
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")

    output_reuse_authorized = witness_output_columns is not None
    if witness_output_columns is None:
        witness_output_columns = allocate_segment_polygon_witness_partner_device_output_columns(
            output_capacity,
            partner=partner,
        )
    _require_segment_polygon_witness_output_lengths(witness_output_columns, output_capacity)
    witness_ray_ids = witness_output_columns["witness_ray_ids"]
    witness_primitive_ids = witness_output_columns["witness_primitive_ids"]

    scene_reuse_authorized = prepared_scene is not None
    scene = prepared_scene
    if scene is None:
        scene = _optix.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
            polygon_triangle_columns,
            polygon_triangle_aabbs,
        )
    try:
        packet = scene.write_device_any_hit_all_witnesses(
            segment_ray_columns,
            witness_ray_ids,
            witness_primitive_ids,
        )
        runtime["sync"]()
    finally:
        if not scene_reuse_authorized:
            scene.close()

    metadata = dict(packet["metadata"])
    metadata["prepared_scene_reused"] = scene_reuse_authorized
    metadata["witness_output_columns_reused"] = output_reuse_authorized
    emitted_count = int(metadata["emitted_count"])
    if metadata["overflowed"]:
        raise RuntimeError("partner segment/polygon column adapter overflowed; increase output_capacity")
    return {
        "runtime": runtime,
        "witness_ray_ids": witness_ray_ids,
        "witness_primitive_ids": witness_primitive_ids,
        "emitted_count": emitted_count,
        "metadata": metadata,
    }


def prepare_segment_polygon_anyhit_optix_partner_device_scene(
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
):
    """Prepare a reusable OptiX scene from partner-owned triangle columns."""
    return _optix.prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene(
        polygon_triangle_columns,
        polygon_triangle_aabbs,
    )


def allocate_segment_polygon_witness_partner_device_output_columns(
    output_capacity: int,
    *,
    partner: str = "torch",
) -> dict[str, object]:
    """Allocate reusable partner-owned witness output columns."""
    output_capacity = int(output_capacity)
    if output_capacity <= 0:
        raise ValueError("output_capacity must be positive")
    runtime = _partner_module(partner)
    return {
        "witness_ray_ids": runtime["zeros"]((output_capacity,), runtime["uint32"], runtime["device"]),
        "witness_primitive_ids": runtime["zeros"]((output_capacity,), runtime["uint32"], runtime["device"]),
    }


def allocate_robot_collision_pose_partner_device_output_columns(
    pose_count: int,
    ray_count: int,
    *,
    partner: str = "torch",
) -> dict[str, object]:
    """Allocate reusable partner-owned ray and pose flag buffers."""
    pose_count = int(pose_count)
    ray_count = int(ray_count)
    if pose_count < 0:
        raise ValueError("pose_count must be non-negative")
    if ray_count < 0:
        raise ValueError("ray_count must be non-negative")
    runtime = _partner_module(partner)
    return {
        "ray_any_hit_flags": runtime["zeros"]((ray_count,), runtime["uint32"], runtime["device"]),
        "pose_collision_flags": runtime["zeros"]((pose_count,), runtime["uint32"], runtime["device"]),
    }


def _require_robot_collision_output_column_lengths(
    output_columns: dict[str, object],
    *,
    pose_count: int,
    ray_count: int,
) -> None:
    for name, expected in (("ray_any_hit_flags", ray_count), ("pose_collision_flags", pose_count)):
        if name not in output_columns:
            raise ValueError(f"output_columns must include {name!r}")
        if _column_length(output_columns, name) != expected:
            raise ValueError(f"output_columns[{name!r}] length must match {expected}")


def _scatter_ray_flags_to_pose_flags(runtime: dict, ray_flags, pose_indices, pose_flags) -> None:
    if runtime["name"] == "torch":
        pose_flags.copy_(
            partner_group_any_by_key(
                pose_indices,
                ray_flags,
                _column_length({"pose_flags": pose_flags}, "pose_flags"),
                partner=runtime["name"],
            )
        )
        return
    if runtime["name"] == "cupy":
        pose_flags[...] = partner_group_any_by_key(
            pose_indices,
            ray_flags,
            _column_length({"pose_flags": pose_flags}, "pose_flags"),
            partner=runtime["name"],
        )
        return
    raise ValueError("partner must be 'torch' or 'cupy'")


def robot_collision_pose_flags_optix_prepared_partner_device_columns(
    prepared_scene,
    ray_columns: dict[str, object],
    pose_indices,
    *,
    pose_count: int,
    partner: str = "torch",
    output_columns: dict[str, object] | None = None,
    return_metadata: bool = False,
):
    """Return robot collision pose flags through generic ray/triangle any-hit flags.

    The native engine writes one generic any-hit flag per ray. This app-layer
    adapter reduces ray flags to one collision flag per pose with Torch/CuPy.
    """
    pose_count = int(pose_count)
    if pose_count < 0:
        raise ValueError("pose_count must be non-negative")
    ray_count = _column_length(ray_columns, "ids")
    if _column_length({"pose_indices": pose_indices}, "pose_indices") != ray_count:
        raise ValueError("pose_indices length must match ray count")
    runtime = _partner_module(partner)
    output_reuse_authorized = output_columns is not None
    if output_columns is None:
        output_columns = allocate_robot_collision_pose_partner_device_output_columns(
            pose_count,
            ray_count,
            partner=partner,
        )
    _require_robot_collision_output_column_lengths(
        output_columns,
        pose_count=pose_count,
        ray_count=ray_count,
    )
    ray_flags = output_columns["ray_any_hit_flags"]
    pose_flags = output_columns["pose_collision_flags"]
    native_result = prepared_scene.write_device_any_hit_flags(ray_columns, ray_flags)
    _scatter_ray_flags_to_pose_flags(runtime, ray_flags, pose_indices, pose_flags)
    runtime["sync"]()
    columns = {
        "ray_any_hit_flags": ray_flags,
        "pose_collision_flags": pose_flags,
    }
    metadata = dict(native_result["metadata"])
    metadata.update(
        {
            "adapter": "robot_collision_pose_flags_optix_prepared_partner_device_columns",
            "app": "robot_collision_screening",
            "partner": runtime["name"],
            "pose_count": pose_count,
            "ray_count": ray_count,
            "output_columns_reused": output_reuse_authorized,
            "input_contract": "caller_supplied_partner_device_ray_columns_and_pose_indices",
            "native_engine_row_contract": "generic_ray_primitive_any_hit_flags",
            "app_flag_materialization": "partner_gpu_pose_flags_from_native_any_hit_ray_flags",
            "app_flag_host_materialization": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def _require_segment_polygon_witness_output_lengths(
    witness_output_columns: dict[str, object],
    output_capacity: int,
) -> None:
    for name in ("witness_ray_ids", "witness_primitive_ids"):
        if name not in witness_output_columns:
            raise ValueError(f"witness_output_columns must include {name!r}")
        if _column_length(witness_output_columns, name) != output_capacity:
            raise ValueError(f"witness_output_columns[{name!r}] length must match output_capacity")


def segment_polygon_anyhit_rows_optix_partner_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Run segment/polygon rows from caller-supplied partner CUDA columns.

    The caller owns the GPU-resident ray and triangle columns. The adapter only
    allocates bounded witness output columns, invokes the generic native
    all-witness contract, and names/deduplicates app rows in Python.
    """
    witness_result = _segment_polygon_all_witness_columns_optix_partner_columns(
        segment_ray_columns,
        polygon_triangle_columns,
        polygon_triangle_aabbs,
        partner=partner,
        output_capacity=output_capacity,
    )
    runtime = witness_result["runtime"]
    emitted_count = witness_result["emitted_count"]
    metadata = dict(witness_result["metadata"])
    witness_ray_ids = witness_result["witness_ray_ids"]
    witness_primitive_ids = witness_result["witness_primitive_ids"]
    ray_ids = runtime["to_host"](witness_ray_ids)[:emitted_count]
    primitive_ids = runtime["to_host"](witness_primitive_ids)[:emitted_count]
    rows = tuple(
        {"segment_id": segment_id, "polygon_id": polygon_id}
        for segment_id, polygon_id in sorted(set(zip(ray_ids, primitive_ids)))
    )
    metadata.update(
        {
            "adapter": "segment_polygon_anyhit_rows_optix_partner_columns",
            "partner": runtime["name"],
            "app_rows_emitted": len(rows),
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"rows": rows, "metadata": metadata}
    return rows


def segment_polygon_hitcount_optix_partner_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Run segment/polygon hit counts from caller-supplied partner CUDA columns.

    This is an app-layer adapter over generic ray/primitive witness rows. The
    native engine emits witness IDs only; Python deduplicates polygon hits and
    materializes one hit-count row per input segment ID.
    """
    runtime = _partner_module(partner)
    segment_ids = runtime["to_host"](segment_ray_columns["ids"])
    if not segment_ids:
        rows: tuple[dict[str, int], ...] = ()
        metadata = {
            "adapter": "segment_polygon_hitcount_optix_partner_columns",
            "partner": runtime["name"],
            "app_rows_emitted": 0,
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "app_count_materialization": "none_empty_input",
            "app_count_host_materialization": False,
            "whole_app_true_zero_copy_authorized": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
        if return_metadata:
            return {"rows": rows, "metadata": metadata}
        return rows
    witness_result = segment_polygon_anyhit_rows_optix_partner_columns(
        segment_ray_columns,
        polygon_triangle_columns,
        polygon_triangle_aabbs,
        partner=partner,
        output_capacity=output_capacity,
        return_metadata=True,
    )
    counts = {int(segment_id): 0 for segment_id in segment_ids}
    seen_pairs = set()
    for row in witness_result["rows"]:
        pair = (int(row["segment_id"]), int(row["polygon_id"]))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        if pair[0] in counts:
            counts[pair[0]] += 1
    rows = tuple({"segment_id": segment_id, "hit_count": counts[segment_id]} for segment_id in segment_ids)
    metadata = dict(witness_result["metadata"])
    metadata.update(
        {
            "adapter": "segment_polygon_hitcount_optix_partner_columns",
            "partner": runtime["name"],
            "app_rows_emitted": len(rows),
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "app_count_materialization": "python_from_generic_witness_pairs",
            "app_count_host_materialization": True,
            "whole_app_true_zero_copy_authorized": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"rows": rows, "metadata": metadata}
    return rows


def segment_polygon_hitcount_optix_partner_device_count_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Return partner-owned segment IDs and hit-count columns.

    This adapter keeps the native call on the same generic bounded witness
    contract as the row adapters, then performs duplicate-pair removal and
    per-segment counting with PyTorch/CuPy tensor operations. It avoids
    materializing app hit-count rows on the host.
    """
    witness_result = _segment_polygon_all_witness_columns_optix_partner_columns(
        segment_ray_columns,
        polygon_triangle_columns,
        polygon_triangle_aabbs,
        partner=partner,
        output_capacity=output_capacity,
    )
    runtime = witness_result["runtime"]
    emitted_count = witness_result["emitted_count"]
    metadata = dict(witness_result["metadata"])
    witness_ray_ids = runtime["slice"](witness_result["witness_ray_ids"], emitted_count)
    witness_primitive_ids = runtime["slice"](witness_result["witness_primitive_ids"], emitted_count)
    hit_counts = _count_unique_pairs_for_runtime(
        runtime,
        segment_ray_columns["ids"],
        witness_ray_ids,
        witness_primitive_ids,
    )
    runtime["sync"]()
    columns = {
        "segment_ids": segment_ray_columns["ids"],
        "hit_counts": hit_counts,
    }
    metadata.update(
        {
            "adapter": "segment_polygon_hitcount_optix_partner_device_count_columns",
            "partner": runtime["name"],
            "app_columns_emitted": 2,
            "app_rows_emitted": _column_length(segment_ray_columns, "ids"),
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "app_count_materialization": "partner_gpu_from_generic_witness_pairs",
            "app_count_host_materialization": False,
            "whole_app_true_zero_copy_authorized": True,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def segment_polygon_hitcount_optix_prepared_partner_device_count_columns(
    prepared_scene,
    segment_ray_columns: dict[str, object],
    *,
    partner: str = "torch",
    output_capacity: int | None = None,
    witness_output_columns: dict[str, object] | None = None,
    return_metadata: bool = False,
):
    """Return partner-owned hit-count columns through a reusable triangle scene."""
    witness_result = _segment_polygon_all_witness_columns_optix_partner_columns(
        segment_ray_columns,
        None,
        None,
        partner=partner,
        output_capacity=output_capacity,
        prepared_scene=prepared_scene,
        witness_output_columns=witness_output_columns,
    )
    runtime = witness_result["runtime"]
    emitted_count = witness_result["emitted_count"]
    metadata = dict(witness_result["metadata"])
    witness_ray_ids = runtime["slice"](witness_result["witness_ray_ids"], emitted_count)
    witness_primitive_ids = runtime["slice"](witness_result["witness_primitive_ids"], emitted_count)
    hit_counts = _count_unique_pairs_for_runtime(
        runtime,
        segment_ray_columns["ids"],
        witness_ray_ids,
        witness_primitive_ids,
    )
    runtime["sync"]()
    columns = {
        "segment_ids": segment_ray_columns["ids"],
        "hit_counts": hit_counts,
    }
    metadata.update(
        {
            "adapter": "segment_polygon_hitcount_optix_prepared_partner_device_count_columns",
            "partner": runtime["name"],
            "app_columns_emitted": 2,
            "app_rows_emitted": _column_length(segment_ray_columns, "ids"),
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "app_count_materialization": "partner_gpu_from_prepared_generic_witness_pairs",
            "app_count_host_materialization": False,
            "whole_app_true_zero_copy_authorized": True,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def road_hazard_priority_flags_optix_partner_device_columns(
    segment_ray_columns: dict[str, object],
    polygon_triangle_columns: dict[str, object],
    polygon_triangle_aabbs,
    *,
    threshold: int = 2,
    partner: str = "torch",
    output_capacity: int | None = None,
    return_metadata: bool = False,
):
    """Return partner-owned road hazard priority columns.

    This app adapter reuses the generic segment/polygon hit-count partner
    column path, then applies the road-hazard priority threshold with the
    selected partner tensor library. The native engine still sees only generic
    ray/primitive witness IDs.
    """
    threshold = int(threshold)
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    hitcount_result = segment_polygon_hitcount_optix_partner_device_count_columns(
        segment_ray_columns,
        polygon_triangle_columns,
        polygon_triangle_aabbs,
        partner=partner,
        output_capacity=output_capacity,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    hitcount_columns = hitcount_result["columns"]
    priority_flags = runtime["greater_equal_uint32"](
        hitcount_columns["hit_counts"],
        threshold,
    )
    runtime["sync"]()
    columns = {
        "road_ids": hitcount_columns["segment_ids"],
        "hit_counts": hitcount_columns["hit_counts"],
        "priority_flags": priority_flags,
    }
    metadata = dict(hitcount_result["metadata"])
    metadata.update(
        {
            "adapter": "road_hazard_priority_flags_optix_partner_device_columns",
            "app": "road_hazard_screening",
            "partner": runtime["name"],
            "priority_threshold": threshold,
            "app_priority_materialization": "partner_gpu_threshold_from_hit_counts",
            "app_priority_host_materialization": False,
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def road_hazard_priority_flags_optix_prepared_partner_device_columns(
    prepared_scene,
    segment_ray_columns: dict[str, object],
    *,
    threshold: int = 2,
    partner: str = "torch",
    output_capacity: int | None = None,
    witness_output_columns: dict[str, object] | None = None,
    return_metadata: bool = False,
):
    """Return road hazard priority columns through a reusable triangle scene."""
    threshold = int(threshold)
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    hitcount_result = segment_polygon_hitcount_optix_prepared_partner_device_count_columns(
        prepared_scene,
        segment_ray_columns,
        partner=partner,
        output_capacity=output_capacity,
        witness_output_columns=witness_output_columns,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    hitcount_columns = hitcount_result["columns"]
    priority_flags = runtime["greater_equal_uint32"](
        hitcount_columns["hit_counts"],
        threshold,
    )
    runtime["sync"]()
    columns = {
        "road_ids": hitcount_columns["segment_ids"],
        "hit_counts": hitcount_columns["hit_counts"],
        "priority_flags": priority_flags,
    }
    metadata = dict(hitcount_result["metadata"])
    metadata.update(
        {
            "adapter": "road_hazard_priority_flags_optix_prepared_partner_device_columns",
            "app": "road_hazard_screening",
            "partner": runtime["name"],
            "priority_threshold": threshold,
            "app_priority_materialization": "partner_gpu_threshold_from_prepared_hit_counts",
            "app_priority_host_materialization": False,
            "input_contract": "caller_supplied_partner_device_columns",
            "native_engine_row_contract": "generic_ray_primitive_witness_pairs",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def fixed_radius_count_threshold_2d_partner_columns(
    query_point_columns: dict[str, object],
    search_point_columns: dict[str, object],
    *,
    radius: float,
    threshold: int = 1,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return partner-owned fixed-radius count and threshold columns.

    This is the protocol-first partner reference path for fixed-radius apps. It
    uses PyTorch/CuPy tensor operations over caller-owned point columns and does
    not call the native RTDL engine yet.
    """
    radius = float(radius)
    threshold = int(threshold)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    runtime = _partner_module(partner)
    neighbor_counts = runtime["fixed_radius_count_threshold_2d"](
        query_point_columns,
        search_point_columns,
        radius,
        threshold,
    )
    threshold_flags = runtime["greater_equal_uint32"](neighbor_counts, threshold)
    runtime["sync"]()
    columns = {
        "query_ids": query_point_columns["ids"],
        "neighbor_counts": neighbor_counts,
        "threshold_flags": threshold_flags,
    }
    metadata = {
        "adapter": "fixed_radius_count_threshold_2d_partner_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "partner_reference_contract": "generic_fixed_radius_count_threshold_2d",
        "native_engine_row_contract": "not_called_partner_reference_only",
        "radius": radius,
        "threshold": threshold,
        "app_count_materialization": "partner_gpu_fixed_radius_count_threshold",
        "app_count_host_materialization": False,
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def fixed_radius_count_threshold_2d_optix_partner_device_columns(
    query_point_columns: dict[str, object],
    search_point_columns: dict[str, object],
    *,
    radius: float,
    threshold: int = 1,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return OptiX-written fixed-radius count-threshold columns.

    This is the first native RTDL fixed-radius partner bridge: caller-owned
    PyTorch/CuPy point columns are handed directly to OptiX, and OptiX writes
    caller-owned output columns without app-row host materialization.
    """
    radius = float(radius)
    threshold = int(threshold)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    runtime = _partner_module(partner)
    query_count = _column_length(query_point_columns, "ids")
    search_count = _column_length(search_point_columns, "ids")
    neighbor_counts = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])
    threshold_flags = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])
    query_ids_out = runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"])

    if query_count and search_count:
        with _optix.prepare_optix_fixed_radius_count_threshold_2d_device_search_columns(
            search_point_columns,
            max_radius=radius,
        ) as prepared:
            native_result = prepared.write_device_count_threshold_columns(
                query_point_columns,
                radius=radius,
                threshold=threshold,
                query_ids_out=query_ids_out,
                neighbor_counts_out=neighbor_counts,
                threshold_flags_out=threshold_flags,
            )
        native_metadata = native_result["metadata"]
    else:
        query_ids_out = query_point_columns["ids"]
        if threshold == 0:
            threshold_flags = runtime["greater_equal_uint32"](neighbor_counts, 0)
        native_metadata = {
            "transfer_mode": "device_fixed_radius_point_columns_output_columns_zero_copy_empty_shortcut",
            "native_symbol": "not_called_empty_input",
            "direct_device_handoff_authorized": True,
            "true_zero_copy_authorized": True,
            "rt_core_speedup_claim_authorized": False,
        }
    runtime["sync"]()
    columns = {
        "query_ids": query_ids_out,
        "neighbor_counts": neighbor_counts,
        "threshold_flags": threshold_flags,
    }
    metadata = {
        "adapter": "fixed_radius_count_threshold_2d_optix_partner_device_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
        "app_count_materialization": "native_optix_device_columns",
        "app_count_host_materialization": False,
        "query_count": query_count,
        "search_count": search_count,
        "radius": radius,
        "threshold": threshold,
        "direct_device_handoff_authorized": bool(native_metadata["direct_device_handoff_authorized"]),
        "true_zero_copy_authorized": bool(native_metadata["true_zero_copy_authorized"]),
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "native_metadata": native_metadata,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene(
    search_point_columns: dict[str, object],
    *,
    max_radius: float,
    partner: str = "torch",
):
    """Prepare a reusable OptiX fixed-radius scene from partner point columns."""
    _partner_module(partner)
    return _optix.prepare_optix_fixed_radius_count_threshold_2d_device_search_columns(
        search_point_columns,
        max_radius=max_radius,
    )


def allocate_fixed_radius_count_threshold_2d_partner_device_output_columns(
    query_count: int,
    *,
    partner: str = "torch",
) -> dict[str, object]:
    """Allocate reusable partner-owned output columns for prepared fixed-radius runs."""
    query_count = int(query_count)
    if query_count < 0:
        raise ValueError("query_count must be non-negative")
    runtime = _partner_module(partner)
    return {
        "query_ids": runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"]),
        "neighbor_counts": runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"]),
        "threshold_flags": runtime["zeros"]((query_count,), runtime["uint32"], runtime["device"]),
    }


def _require_fixed_radius_output_column_lengths(output_columns: dict[str, object], query_count: int) -> None:
    for name in ("query_ids", "neighbor_counts", "threshold_flags"):
        if name not in output_columns:
            raise ValueError(f"output_columns must include {name!r}")
        if _column_length(output_columns, name) != query_count:
            raise ValueError(f"output_columns[{name!r}] length must match query point count")


def fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(
    prepared,
    query_point_columns: dict[str, object],
    *,
    radius: float,
    threshold: int = 1,
    partner: str = "torch",
    output_columns: dict[str, object] | None = None,
    return_metadata: bool = False,
):
    """Return fixed-radius columns through a reusable prepared OptiX scene."""
    radius = float(radius)
    threshold = int(threshold)
    if radius < 0:
        raise ValueError("radius must be non-negative")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    runtime = _partner_module(partner)
    query_count = _column_length(query_point_columns, "ids")
    output_reuse_authorized = output_columns is not None
    if output_columns is None:
        output_columns = allocate_fixed_radius_count_threshold_2d_partner_device_output_columns(
            query_count,
            partner=partner,
        )
    _require_fixed_radius_output_column_lengths(output_columns, query_count)
    query_ids_out = output_columns["query_ids"]
    neighbor_counts = output_columns["neighbor_counts"]
    threshold_flags = output_columns["threshold_flags"]

    native_result = prepared.write_device_count_threshold_columns(
        query_point_columns,
        radius=radius,
        threshold=threshold,
        query_ids_out=query_ids_out,
        neighbor_counts_out=neighbor_counts,
        threshold_flags_out=threshold_flags,
    )
    runtime["sync"]()
    columns = {
        "query_ids": query_ids_out,
        "neighbor_counts": neighbor_counts,
        "threshold_flags": threshold_flags,
    }
    metadata = {
        "adapter": "fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns",
        "partner": runtime["name"],
        "input_contract": "caller_supplied_partner_device_point_columns",
        "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
        "app_count_materialization": "native_optix_prepared_device_columns",
        "app_count_host_materialization": False,
        "query_count": query_count,
        "radius": radius,
        "threshold": threshold,
        "output_columns_reused": output_reuse_authorized,
        "direct_device_handoff_authorized": bool(native_result["metadata"]["direct_device_handoff_authorized"]),
        "true_zero_copy_authorized": bool(native_result["metadata"]["true_zero_copy_authorized"]),
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "native_metadata": native_result["metadata"],
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def service_coverage_gap_flags_partner_columns(
    household_point_columns: dict[str, object],
    clinic_point_columns: dict[str, object],
    *,
    radius: float,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return partner-owned service coverage flags.

    A household is uncovered when the fixed-radius neighbor count is zero. This
    remains a partner-reference app adapter until fixed-radius native
    device-column handoff exists.
    """
    result = fixed_radius_count_threshold_2d_partner_columns(
        household_point_columns,
        clinic_point_columns,
        radius=radius,
        threshold=1,
        partner=partner,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    covered_flags = result["columns"]["threshold_flags"]
    uncovered_flags = runtime["invert_binary_uint32"](covered_flags)
    runtime["sync"]()
    columns = {
        "household_ids": result["columns"]["query_ids"],
        "nearby_clinic_counts": result["columns"]["neighbor_counts"],
        "covered_flags": covered_flags,
        "uncovered_flags": uncovered_flags,
    }
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "service_coverage_gap_flags_partner_columns",
            "app": "service_coverage_gaps",
            "app_flag_materialization": "partner_gpu_threshold_flags_from_fixed_radius_counts",
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def service_coverage_gap_flags_optix_partner_device_columns(
    household_point_columns: dict[str, object],
    clinic_point_columns: dict[str, object],
    *,
    radius: float,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return native OptiX fixed-radius service coverage columns."""
    result = fixed_radius_count_threshold_2d_optix_partner_device_columns(
        household_point_columns,
        clinic_point_columns,
        radius=radius,
        threshold=1,
        partner=partner,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    covered_flags = result["columns"]["threshold_flags"]
    uncovered_flags = runtime["invert_binary_uint32"](covered_flags)
    runtime["sync"]()
    columns = {
        "household_ids": result["columns"]["query_ids"],
        "nearby_clinic_counts": result["columns"]["neighbor_counts"],
        "covered_flags": covered_flags,
        "uncovered_flags": uncovered_flags,
    }
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "service_coverage_gap_flags_optix_partner_device_columns",
            "app": "service_coverage_gaps",
            "app_flag_materialization": "partner_gpu_threshold_flags_from_native_fixed_radius_counts",
            "app_flag_host_materialization": False,
            "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def service_coverage_gap_flags_optix_prepared_partner_device_columns(
    prepared,
    household_point_columns: dict[str, object],
    *,
    radius: float,
    partner: str = "torch",
    fixed_radius_output_columns: dict[str, object] | None = None,
    return_metadata: bool = False,
):
    """Return service coverage columns through a reusable prepared scene."""
    result = fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(
        prepared,
        household_point_columns,
        radius=radius,
        threshold=1,
        partner=partner,
        output_columns=fixed_radius_output_columns,
        return_metadata=True,
    )
    runtime = _partner_module(partner)
    covered_flags = result["columns"]["threshold_flags"]
    uncovered_flags = runtime["invert_binary_uint32"](covered_flags)
    runtime["sync"]()
    columns = {
        "household_ids": result["columns"]["query_ids"],
        "nearby_clinic_counts": result["columns"]["neighbor_counts"],
        "covered_flags": covered_flags,
        "uncovered_flags": uncovered_flags,
    }
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "service_coverage_gap_flags_optix_prepared_partner_device_columns",
            "app": "service_coverage_gaps",
            "app_flag_materialization": "partner_gpu_threshold_flags_from_prepared_native_fixed_radius_counts",
            "app_flag_host_materialization": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def event_hotspot_flags_partner_columns(
    event_point_columns: dict[str, object],
    *,
    radius: float,
    hotspot_threshold: int,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return partner-owned event hotspot flags.

    The self-neighbor is included in the fixed-radius count, so the partner
    threshold is `hotspot_threshold + 1`, matching the existing app summary
    semantics.
    """
    hotspot_threshold = int(hotspot_threshold)
    if hotspot_threshold < 0:
        raise ValueError("hotspot_threshold must be non-negative")
    result = fixed_radius_count_threshold_2d_partner_columns(
        event_point_columns,
        event_point_columns,
        radius=radius,
        threshold=hotspot_threshold + 1,
        partner=partner,
        return_metadata=True,
    )
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "event_hotspot_flags_partner_columns",
            "app": "event_hotspot_screening",
            "hotspot_threshold_excluding_self": hotspot_threshold,
            "fixed_radius_threshold_including_self": hotspot_threshold + 1,
            "app_flag_materialization": "partner_gpu_threshold_flags_from_fixed_radius_counts",
        }
    )
    columns = {
        "event_ids": result["columns"]["query_ids"],
        "neighbor_counts_including_self": result["columns"]["neighbor_counts"],
        "hotspot_flags": result["columns"]["threshold_flags"],
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def event_hotspot_flags_optix_partner_device_columns(
    event_point_columns: dict[str, object],
    *,
    radius: float,
    hotspot_threshold: int,
    partner: str = "torch",
    return_metadata: bool = False,
):
    """Return native OptiX fixed-radius event hotspot columns."""
    hotspot_threshold = int(hotspot_threshold)
    if hotspot_threshold < 0:
        raise ValueError("hotspot_threshold must be non-negative")
    result = fixed_radius_count_threshold_2d_optix_partner_device_columns(
        event_point_columns,
        event_point_columns,
        radius=radius,
        threshold=hotspot_threshold + 1,
        partner=partner,
        return_metadata=True,
    )
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "event_hotspot_flags_optix_partner_device_columns",
            "app": "event_hotspot_screening",
            "hotspot_threshold_excluding_self": hotspot_threshold,
            "fixed_radius_threshold_including_self": hotspot_threshold + 1,
            "app_flag_materialization": "partner_gpu_threshold_flags_from_native_fixed_radius_counts",
            "app_flag_host_materialization": False,
            "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    columns = {
        "event_ids": result["columns"]["query_ids"],
        "neighbor_counts_including_self": result["columns"]["neighbor_counts"],
        "hotspot_flags": result["columns"]["threshold_flags"],
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns


def event_hotspot_flags_optix_prepared_partner_device_columns(
    prepared,
    event_point_columns: dict[str, object],
    *,
    radius: float,
    hotspot_threshold: int,
    partner: str = "torch",
    fixed_radius_output_columns: dict[str, object] | None = None,
    return_metadata: bool = False,
):
    """Return event hotspot columns through a reusable prepared scene."""
    hotspot_threshold = int(hotspot_threshold)
    if hotspot_threshold < 0:
        raise ValueError("hotspot_threshold must be non-negative")
    result = fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns(
        prepared,
        event_point_columns,
        radius=radius,
        threshold=hotspot_threshold + 1,
        partner=partner,
        output_columns=fixed_radius_output_columns,
        return_metadata=True,
    )
    metadata = dict(result["metadata"])
    metadata.update(
        {
            "adapter": "event_hotspot_flags_optix_prepared_partner_device_columns",
            "app": "event_hotspot_screening",
            "hotspot_threshold_excluding_self": hotspot_threshold,
            "fixed_radius_threshold_including_self": hotspot_threshold + 1,
            "app_flag_materialization": "partner_gpu_threshold_flags_from_prepared_native_fixed_radius_counts",
            "app_flag_host_materialization": False,
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        }
    )
    columns = {
        "event_ids": result["columns"]["query_ids"],
        "neighbor_counts_including_self": result["columns"]["neighbor_counts"],
        "hotspot_flags": result["columns"]["threshold_flags"],
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns
