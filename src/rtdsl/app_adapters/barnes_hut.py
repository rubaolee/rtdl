from __future__ import annotations

from ..partner_adapters import _column_length
from ..partner_adapters import _partner_module


_CUPY_PAIRWISE_FORCE_2D_KERNEL = None


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
    """Compute pairwise softened inverse-square force vectors over weighted points.

    This is an application-scoped partner reference for Barnes-Hut-style
    validation, not a shared RTDL engine primitive.
    """
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
            same_id = source_weighted_point_columns["ids"].reshape(-1, 1) == target_weighted_point_columns[
                "ids"
            ].reshape(1, -1)
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
