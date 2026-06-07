from __future__ import annotations

from ..partner_adapters import _column_length
from ..partner_adapters import _numba_runtime_for_point_columns
from ..partner_adapters import _partner_module
from ..numba_partner_continuation import _as_numba_cuda_vector


_CUPY_PAIRWISE_FORCE_2D_KERNEL = None
_NUMBA_PAIRWISE_FORCE_2D_KERNEL = None
_NUMBA_PAIRWISE_FORCE_2D_BLOCK_REDUCE_KERNEL = None


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


def _numba_pairwise_force_2d_kernel(cuda):
    global _NUMBA_PAIRWISE_FORCE_2D_KERNEL
    if _NUMBA_PAIRWISE_FORCE_2D_KERNEL is None:
        import math

        @cuda.jit(fastmath=True)
        def pairwise_force_2d(
            source_ids,
            sx,
            sy,
            sm,
            source_count,
            target_ids,
            tx,
            ty,
            tm,
            target_count,
            softening_sq,
            exclude_equal_ids,
            out_fx,
            out_fy,
        ):
            i = cuda.grid(1)
            if i >= source_count:
                return
            source_x = sx[i]
            source_y = sy[i]
            source_mass = sm[i]
            source_id = source_ids[i]
            fx = 0.0
            fy = 0.0
            for j in range(target_count):
                if exclude_equal_ids != 0 and source_id == target_ids[j]:
                    continue
                dx = tx[j] - source_x
                dy = ty[j] - source_y
                dist_sq = dx * dx + dy * dy + softening_sq
                inv_dist = 1.0 / math.sqrt(dist_sq)
                scale = source_mass * tm[j] * inv_dist * inv_dist * inv_dist
                fx += dx * scale
                fy += dy * scale
            out_fx[i] = fx
            out_fy[i] = fy

        _NUMBA_PAIRWISE_FORCE_2D_KERNEL = pairwise_force_2d
    return _NUMBA_PAIRWISE_FORCE_2D_KERNEL


def _numba_pairwise_force_2d_block_reduce_kernel(cuda):
    global _NUMBA_PAIRWISE_FORCE_2D_BLOCK_REDUCE_KERNEL
    if _NUMBA_PAIRWISE_FORCE_2D_BLOCK_REDUCE_KERNEL is None:
        import math
        from numba import float64

        @cuda.jit(fastmath=True)
        def pairwise_force_2d_block_reduce(
            source_ids,
            sx,
            sy,
            sm,
            source_count,
            target_ids,
            tx,
            ty,
            tm,
            target_count,
            softening_sq,
            exclude_equal_ids,
            out_fx,
            out_fy,
        ):
            partial_fx = cuda.shared.array(shape=512, dtype=float64)
            partial_fy = cuda.shared.array(shape=512, dtype=float64)

            i = cuda.blockIdx.x
            lane = cuda.threadIdx.x
            fx = 0.0
            fy = 0.0
            if i < source_count:
                source_x = sx[i]
                source_y = sy[i]
                source_mass = sm[i]
                source_id = source_ids[i]
                for j in range(lane, target_count, 512):
                    if exclude_equal_ids != 0 and source_id == target_ids[j]:
                        continue
                    dx = tx[j] - source_x
                    dy = ty[j] - source_y
                    dist_sq = dx * dx + dy * dy + softening_sq
                    inv_dist = 1.0 / math.sqrt(dist_sq)
                    scale = source_mass * tm[j] * inv_dist * inv_dist * inv_dist
                    fx += dx * scale
                    fy += dy * scale

            partial_fx[lane] = fx
            partial_fy[lane] = fy
            cuda.syncthreads()

            stride = 256
            while stride > 0:
                if lane < stride:
                    partial_fx[lane] += partial_fx[lane + stride]
                    partial_fy[lane] += partial_fy[lane + stride]
                cuda.syncthreads()
                stride //= 2

            if lane == 0 and i < source_count:
                out_fx[i] = partial_fx[0]
                out_fy[i] = partial_fy[0]

        _NUMBA_PAIRWISE_FORCE_2D_BLOCK_REDUCE_KERNEL = pairwise_force_2d_block_reduce
    return _NUMBA_PAIRWISE_FORCE_2D_BLOCK_REDUCE_KERNEL


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
    runtime = _numba_runtime_for_point_columns() if partner == "numba" else _partner_module(partner)
    source_count = _column_length(source_weighted_point_columns, "ids")
    target_count = _column_length(target_weighted_point_columns, "ids")
    if source_count <= 0 or target_count <= 0:
        raise ValueError("force accumulation requires non-empty source and target columns")
    numba_force_kernel_strategy = None

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
    elif runtime["name"] == "numba":
        cuda = runtime["module"]
        np = runtime["numpy"]
        source_ids = _as_numba_cuda_vector(
            source_weighted_point_columns["ids"],
            name="source_ids",
            dtype=np.uint32,
            cuda=cuda,
            np=np,
        )
        target_ids = _as_numba_cuda_vector(
            target_weighted_point_columns["ids"],
            name="target_ids",
            dtype=np.uint32,
            cuda=cuda,
            np=np,
        )
        sx = _as_numba_cuda_vector(source_weighted_point_columns["x"], name="sx", dtype=np.float64, cuda=cuda, np=np)
        sy = _as_numba_cuda_vector(source_weighted_point_columns["y"], name="sy", dtype=np.float64, cuda=cuda, np=np)
        sm = _as_numba_cuda_vector(
            source_weighted_point_columns["weight"],
            name="sm",
            dtype=np.float64,
            cuda=cuda,
            np=np,
        )
        tx = _as_numba_cuda_vector(target_weighted_point_columns["x"], name="tx", dtype=np.float64, cuda=cuda, np=np)
        ty = _as_numba_cuda_vector(target_weighted_point_columns["y"], name="ty", dtype=np.float64, cuda=cuda, np=np)
        tm = _as_numba_cuda_vector(
            target_weighted_point_columns["weight"],
            name="tm",
            dtype=np.float64,
            cuda=cuda,
            np=np,
        )
        force_x = cuda.device_array((source_count,), dtype=np.float64)
        force_y = cuda.device_array((source_count,), dtype=np.float64)
        use_block_reduce = source_count >= 512 and target_count >= 512
        if use_block_reduce:
            threads = 512
            blocks = source_count
            kernel = _numba_pairwise_force_2d_block_reduce_kernel(cuda)
            numba_force_kernel_strategy = "block_source_target_stride_512_reduce_fastmath_true"
        else:
            threads = 128
            blocks = (source_count + threads - 1) // threads
            kernel = _numba_pairwise_force_2d_kernel(cuda)
            numba_force_kernel_strategy = "global_target_stream_fastmath_true"
        kernel[(blocks,), threads](
            source_ids,
            sx,
            sy,
            sm,
            source_count,
            target_ids,
            tx,
            ty,
            tm,
            target_count,
            softening * softening,
            1 if exclude_equal_ids else 0,
            force_x,
            force_y,
        )
    else:
        raise ValueError("partner must be 'torch', 'cupy', or 'numba'")

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
        "numba_force_kernel_strategy": numba_force_kernel_strategy,
        "numba_cuda_jit_used": runtime["name"] == "numba",
        "raw_cuda_kernel_required": False,
        "direct_device_handoff_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
        "whole_app_speedup_claim_authorized": False,
    }
    if return_metadata:
        return {"columns": columns, "metadata": metadata}
    return columns
