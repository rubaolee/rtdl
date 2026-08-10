#include <cuda_runtime.h>
#include <thrust/copy.h>
#include <thrust/device_ptr.h>
#include <thrust/device_vector.h>
#include <thrust/execution_policy.h>
#include <thrust/extrema.h>
#include <thrust/fill.h>
#include <thrust/functional.h>
#include <thrust/gather.h>
#include <thrust/iterator/zip_iterator.h>
#include <thrust/iterator/constant_iterator.h>
#include <thrust/iterator/counting_iterator.h>
#include <thrust/reduce.h>
#include <thrust/scatter.h>
#include <thrust/scan.h>
#include <thrust/sequence.h>
#include <thrust/sort.h>
#include <thrust/transform.h>
#include <thrust/tuple.h>

#include <chrono>
#include <climits>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <string>

#pragma pack(push, 1)
struct RtdlCudaGpuRay3DHost {
    float ox, oy, oz, dx, dy, dz, tmax;
    uint32_t id;
};
#pragma pack(pop)

static __global__ void rtdl_pack_ray3d_device_columns_kernel(
        const uint32_t* ids,
        const double* ox,
        const double* oy,
        const double* oz,
        const double* dx,
        const double* dy,
        const double* dz,
        const double* tmax,
        RtdlCudaGpuRay3DHost* rays,
        uint32_t ray_count)
{
    const uint32_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= ray_count) return;
    const float fdx = static_cast<float>(dx[idx]);
    const float fdy = static_cast<float>(dy[idx]);
    const float fdz = static_cast<float>(dz[idx]);
    const float len = sqrtf(fdx * fdx + fdy * fdy + fdz * fdz);
    RtdlCudaGpuRay3DHost ray;
    ray.ox = static_cast<float>(ox[idx]);
    ray.oy = static_cast<float>(oy[idx]);
    ray.oz = static_cast<float>(oz[idx]);
    if (len > 1.0e-10f) {
        ray.dx = fdx / len;
        ray.dy = fdy / len;
        ray.dz = fdz / len;
        ray.tmax = static_cast<float>(tmax[idx]) * len;
    } else {
        ray.dx = 0.0f;
        ray.dy = 0.0f;
        ray.dz = 0.0f;
        ray.tmax = 0.0f;
    }
    ray.id = ids[idx];
    rays[idx] = ray;
}

static void rtdl_cuda_check(cudaError_t status, const char* operation)
{
    if (status != cudaSuccess) {
        throw std::runtime_error(
            std::string("CUDA error during ") + operation + ": " + cudaGetErrorString(status));
    }
}

void rtdl_cuda_pack_ray3d_device_columns_precompiled(
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_oz,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_dz,
        const double* ray_tmax,
        void* rays_out,
        uint32_t ray_count)
{
    if (ray_count == 0) return;
    const unsigned block = 256;
    const unsigned grid = (ray_count + block - 1u) / block;
    rtdl_pack_ray3d_device_columns_kernel<<<grid, block>>>(
        ray_ids,
        ray_ox,
        ray_oy,
        ray_oz,
        ray_dx,
        ray_dy,
        ray_dz,
        ray_tmax,
        static_cast<RtdlCudaGpuRay3DHost*>(rays_out),
        ray_count);
    rtdl_cuda_check(cudaGetLastError(), "launching 3-D ray-column pack kernel");
    rtdl_cuda_check(cudaDeviceSynchronize(), "synchronizing 3-D ray-column pack kernel");
}

static __global__ void rtdl_local_grid_nearest_seed_3d_kernel(
        const double* query_coords,
        const int64_t* query_ids,
        uint32_t query_count,
        const double* target_coords,
        const int64_t* target_ids,
        uint32_t target_count,
        const int64_t* cell_ids,
        const int64_t* original_cell_ids,
        const int64_t* dense_cell_positions,
        uint32_t dense_cell_position_count,
        const int64_t* point_begin_offsets,
        const int64_t* point_counts,
        const int64_t* point_row_indices,
        uint32_t point_row_index_count,
        uint32_t cell_count,
        int dim_x,
        int dim_y,
        int dim_z,
        double lower_x,
        double lower_y,
        double lower_z,
        double upper_x,
        double upper_y,
        double upper_z,
        double* nearest_distances_out,
        int64_t* nearest_item_ids_out,
        int64_t* seed_cell_ids_out,
        int64_t* seed_cell_point_counts_out,
        int64_t* grid_cell_probe_counts_out)
{
    const uint32_t query_row = blockIdx.x * blockDim.x + threadIdx.x;
    if (query_row >= query_count) return;
    (void)query_ids;
    (void)original_cell_ids;
    const double qx = query_coords[static_cast<unsigned long long>(query_row) * 3ull + 0ull];
    const double qy = query_coords[static_cast<unsigned long long>(query_row) * 3ull + 1ull];
    const double qz = query_coords[static_cast<unsigned long long>(query_row) * 3ull + 2ull];

    const double extent_x = upper_x - lower_x;
    const double extent_y = upper_y - lower_y;
    const double extent_z = upper_z - lower_z;
    int base_x = 0;
    int base_y = 0;
    int base_z = 0;
    if (extent_x != 0.0) {
        base_x = static_cast<int>(floor((qx - lower_x) / extent_x * static_cast<double>(dim_x)));
        if (base_x < 0) base_x = 0;
        if (base_x >= dim_x) base_x = dim_x - 1;
    }
    if (extent_y != 0.0) {
        base_y = static_cast<int>(floor((qy - lower_y) / extent_y * static_cast<double>(dim_y)));
        if (base_y < 0) base_y = 0;
        if (base_y >= dim_y) base_y = dim_y - 1;
    }
    if (extent_z != 0.0) {
        base_z = static_cast<int>(floor((qz - lower_z) / extent_z * static_cast<double>(dim_z)));
        if (base_z < 0) base_z = 0;
        if (base_z >= dim_z) base_z = dim_z - 1;
    }

    int max_radius = dim_x;
    if (dim_y > max_radius) max_radius = dim_y;
    if (dim_z > max_radius) max_radius = dim_z;
    const double step_x = extent_x == 0.0 ? 0.0 : extent_x / static_cast<double>(dim_x);
    const double step_y = extent_y == 0.0 ? 0.0 : extent_y / static_cast<double>(dim_y);
    const double step_z = extent_z == 0.0 ? 0.0 : extent_z / static_cast<double>(dim_z);

    int64_t best_cell_index = -1ll;
    int64_t best_cell_id = 9223372036854775807ll;
    double best_grid_distance_sq = INFINITY;
    int64_t probes = 0ll;
    int found = 0;
    for (int radius = 0; radius <= max_radius; ++radius) {
        for (int dx_shell = -radius; dx_shell <= radius; ++dx_shell) {
            const int gx = base_x + dx_shell;
            if (gx < 0 || gx >= dim_x) continue;
            const int abs_dx = dx_shell >= 0 ? dx_shell : -dx_shell;
            for (int dy_shell = -radius; dy_shell <= radius; ++dy_shell) {
                const int gy = base_y + dy_shell;
                if (gy < 0 || gy >= dim_y) continue;
                const int abs_dy = dy_shell >= 0 ? dy_shell : -dy_shell;
                for (int dz_shell = -radius; dz_shell <= radius; ++dz_shell) {
                    const int gz = base_z + dz_shell;
                    if (gz < 0 || gz >= dim_z) continue;
                    const int abs_dz = dz_shell >= 0 ? dz_shell : -dz_shell;
                    int shell = abs_dx;
                    if (abs_dy > shell) shell = abs_dy;
                    if (abs_dz > shell) shell = abs_dz;
                    if (shell != radius) continue;
                    ++probes;
                    const int64_t encoded = (static_cast<int64_t>(gx) * static_cast<int64_t>(dim_y)
                            + static_cast<int64_t>(gy)) * static_cast<int64_t>(dim_z)
                            + static_cast<int64_t>(gz);
                    if (encoded < 0 || static_cast<unsigned long long>(encoded) >= dense_cell_position_count) {
                        continue;
                    }
                    const int64_t pos = dense_cell_positions[encoded];
                    if (pos < 0 || static_cast<unsigned long long>(pos) >= cell_count) {
                        continue;
                    }
                    if (point_counts[pos] <= 0) {
                        continue;
                    }

                    const double low_x = step_x == 0.0 ? lower_x : lower_x + static_cast<double>(gx) * step_x;
                    const double high_x = step_x == 0.0 ? lower_x : lower_x + static_cast<double>(gx + 1) * step_x;
                    const double low_y = step_y == 0.0 ? lower_y : lower_y + static_cast<double>(gy) * step_y;
                    const double high_y = step_y == 0.0 ? lower_y : lower_y + static_cast<double>(gy + 1) * step_y;
                    const double low_z = step_z == 0.0 ? lower_z : lower_z + static_cast<double>(gz) * step_z;
                    const double high_z = step_z == 0.0 ? lower_z : lower_z + static_cast<double>(gz + 1) * step_z;

                    double distance_sq = 0.0;
                    if (qx < low_x) {
                        const double delta = low_x - qx;
                        distance_sq += delta * delta;
                    } else if (qx > high_x) {
                        const double delta = qx - high_x;
                        distance_sq += delta * delta;
                    }
                    if (qy < low_y) {
                        const double delta = low_y - qy;
                        distance_sq += delta * delta;
                    } else if (qy > high_y) {
                        const double delta = qy - high_y;
                        distance_sq += delta * delta;
                    }
                    if (qz < low_z) {
                        const double delta = low_z - qz;
                        distance_sq += delta * delta;
                    } else if (qz > high_z) {
                        const double delta = qz - high_z;
                        distance_sq += delta * delta;
                    }

                    const int64_t cell_id = cell_ids[pos];
                    if (distance_sq < best_grid_distance_sq
                            || (distance_sq == best_grid_distance_sq && cell_id < best_cell_id)) {
                        best_grid_distance_sq = distance_sq;
                        best_cell_id = cell_id;
                        best_cell_index = pos;
                        found = 1;
                    }
                }
            }
        }
        if (found) break;
    }
    if (best_cell_index < 0) {
        best_cell_index = 0;
        best_cell_id = cell_ids[0];
    }

    const int64_t begin = point_begin_offsets[best_cell_index];
    const int64_t count = point_counts[best_cell_index];
    double best_point_distance_sq = INFINITY;
    int64_t best_point_id = 9223372036854775807ll;
    for (int64_t offset = 0; offset < count; ++offset) {
        const int64_t point_slot = begin + offset;
        if (point_slot < 0 || static_cast<unsigned long long>(point_slot) >= point_row_index_count) {
            continue;
        }
        const int64_t target_row = point_row_indices[point_slot];
        if (target_row < 0 || static_cast<unsigned long long>(target_row) >= target_count) {
            continue;
        }
        const double tx = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 0ull];
        const double ty = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 1ull];
        const double tz = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 2ull];
        const double ddx = qx - tx;
        const double ddy = qy - ty;
        const double ddz = qz - tz;
        const double distance_sq = ddx * ddx + ddy * ddy + ddz * ddz;
        const int64_t target_id = target_ids[target_row];
        if (target_id < 0) {
            continue;
        }
        if (distance_sq < best_point_distance_sq
                || (distance_sq == best_point_distance_sq && target_id < best_point_id)) {
            best_point_distance_sq = distance_sq;
            best_point_id = target_id;
        }
    }

    nearest_distances_out[query_row] = sqrt(best_point_distance_sq);
    nearest_item_ids_out[query_row] = best_point_id;
    seed_cell_ids_out[query_row] = best_cell_id;
    seed_cell_point_counts_out[query_row] = count;
    grid_cell_probe_counts_out[query_row] = probes;
}

void rtdl_cuda_local_grid_nearest_seed_3d_precompiled(
        const double* query_coords,
        const int64_t* query_ids,
        uint32_t query_count,
        const double* target_coords,
        const int64_t* target_ids,
        uint32_t target_count,
        const int64_t* cell_ids,
        const int64_t* original_cell_ids,
        const int64_t* dense_cell_positions,
        uint32_t dense_cell_position_count,
        const int64_t* point_begin_offsets,
        const int64_t* point_counts,
        const int64_t* point_row_indices,
        uint32_t point_row_index_count,
        uint32_t cell_count,
        int dim_x,
        int dim_y,
        int dim_z,
        double lower_x,
        double lower_y,
        double lower_z,
        double upper_x,
        double upper_y,
        double upper_z,
        double* nearest_distances_out,
        int64_t* nearest_item_ids_out,
        int64_t* seed_cell_ids_out,
        int64_t* seed_cell_point_counts_out,
        int64_t* grid_cell_probe_counts_out)
{
    if (query_count == 0) return;
    const unsigned block = 256;
    const unsigned grid = (query_count + block - 1u) / block;
    rtdl_local_grid_nearest_seed_3d_kernel<<<grid, block>>>(
        query_coords,
        query_ids,
        query_count,
        target_coords,
        target_ids,
        target_count,
        cell_ids,
        original_cell_ids,
        dense_cell_positions,
        dense_cell_position_count,
        point_begin_offsets,
        point_counts,
        point_row_indices,
        point_row_index_count,
        cell_count,
        dim_x,
        dim_y,
        dim_z,
        lower_x,
        lower_y,
        lower_z,
        upper_x,
        upper_y,
        upper_z,
        nearest_distances_out,
        nearest_item_ids_out,
        seed_cell_ids_out,
        seed_cell_point_counts_out,
        grid_cell_probe_counts_out);
    rtdl_cuda_check(cudaGetLastError(), "launching local-grid nearest seed 3-D kernel");
    rtdl_cuda_check(cudaDeviceSynchronize(), "synchronizing local-grid nearest seed 3-D kernel");
}

static __global__ void rtdl_grid_branch_bound_nearest_seed_3d_kernel(
        const double* query_coords,
        const int64_t* query_ids,
        uint32_t query_count,
        const double* target_coords,
        const int64_t* target_ids,
        uint32_t target_count,
        const int64_t* cell_ids,
        const int64_t* original_cell_ids,
        const int64_t* dense_cell_positions,
        uint32_t dense_cell_position_count,
        const int64_t* point_begin_offsets,
        const int64_t* point_counts,
        const int64_t* point_row_indices,
        uint32_t point_row_index_count,
        uint32_t cell_count,
        int dim_x,
        int dim_y,
        int dim_z,
        double lower_x,
        double lower_y,
        double lower_z,
        double upper_x,
        double upper_y,
        double upper_z,
        double* nearest_distances_out,
        int64_t* nearest_item_ids_out,
        int64_t* seed_cell_ids_out,
        int64_t* seed_cell_point_counts_out,
        int64_t* grid_cell_probe_counts_out,
        int64_t* scanned_cell_counts_out,
        int64_t* scanned_point_counts_out,
        int64_t* shell_counts_out)
{
    const uint32_t query_row = blockIdx.x * blockDim.x + threadIdx.x;
    if (query_row >= query_count) return;
    (void)query_ids;
    (void)original_cell_ids;
    const double qx = query_coords[static_cast<unsigned long long>(query_row) * 3ull + 0ull];
    const double qy = query_coords[static_cast<unsigned long long>(query_row) * 3ull + 1ull];
    const double qz = query_coords[static_cast<unsigned long long>(query_row) * 3ull + 2ull];

    const double extent_x = upper_x - lower_x;
    const double extent_y = upper_y - lower_y;
    const double extent_z = upper_z - lower_z;
    int base_x = 0;
    int base_y = 0;
    int base_z = 0;
    if (extent_x != 0.0) {
        base_x = static_cast<int>(floor((qx - lower_x) / extent_x * static_cast<double>(dim_x)));
        if (base_x < 0) base_x = 0;
        if (base_x >= dim_x) base_x = dim_x - 1;
    }
    if (extent_y != 0.0) {
        base_y = static_cast<int>(floor((qy - lower_y) / extent_y * static_cast<double>(dim_y)));
        if (base_y < 0) base_y = 0;
        if (base_y >= dim_y) base_y = dim_y - 1;
    }
    if (extent_z != 0.0) {
        base_z = static_cast<int>(floor((qz - lower_z) / extent_z * static_cast<double>(dim_z)));
        if (base_z < 0) base_z = 0;
        if (base_z >= dim_z) base_z = dim_z - 1;
    }

    int max_radius = dim_x;
    if (dim_y > max_radius) max_radius = dim_y;
    if (dim_z > max_radius) max_radius = dim_z;
    const double step_x = extent_x == 0.0 ? 0.0 : extent_x / static_cast<double>(dim_x);
    const double step_y = extent_y == 0.0 ? 0.0 : extent_y / static_cast<double>(dim_y);
    const double step_z = extent_z == 0.0 ? 0.0 : extent_z / static_cast<double>(dim_z);

    double best_point_distance_sq = INFINITY;
    int64_t best_point_id = 9223372036854775807ll;
    int64_t best_cell_id = -1ll;
    int64_t best_cell_point_count = 0ll;
    int64_t probes = 0ll;
    int64_t scanned_cells = 0ll;
    int64_t scanned_points = 0ll;
    int64_t shells = 0ll;

    for (int radius = 0; radius <= max_radius; ++radius) {
        double shell_min_grid_distance_sq = INFINITY;
        shells = static_cast<int64_t>(radius + 1);
        for (int dx_shell = -radius; dx_shell <= radius; ++dx_shell) {
            const int gx = base_x + dx_shell;
            if (gx < 0 || gx >= dim_x) continue;
            const int abs_dx = dx_shell >= 0 ? dx_shell : -dx_shell;
            for (int dy_shell = -radius; dy_shell <= radius; ++dy_shell) {
                const int gy = base_y + dy_shell;
                if (gy < 0 || gy >= dim_y) continue;
                const int abs_dy = dy_shell >= 0 ? dy_shell : -dy_shell;
                for (int dz_shell = -radius; dz_shell <= radius; ++dz_shell) {
                    const int gz = base_z + dz_shell;
                    if (gz < 0 || gz >= dim_z) continue;
                    const int abs_dz = dz_shell >= 0 ? dz_shell : -dz_shell;
                    int shell = abs_dx;
                    if (abs_dy > shell) shell = abs_dy;
                    if (abs_dz > shell) shell = abs_dz;
                    if (shell != radius) continue;
                    ++probes;

                    const double low_x = step_x == 0.0 ? lower_x : lower_x + static_cast<double>(gx) * step_x;
                    const double high_x = step_x == 0.0 ? lower_x : lower_x + static_cast<double>(gx + 1) * step_x;
                    const double low_y = step_y == 0.0 ? lower_y : lower_y + static_cast<double>(gy) * step_y;
                    const double high_y = step_y == 0.0 ? lower_y : lower_y + static_cast<double>(gy + 1) * step_y;
                    const double low_z = step_z == 0.0 ? lower_z : lower_z + static_cast<double>(gz) * step_z;
                    const double high_z = step_z == 0.0 ? lower_z : lower_z + static_cast<double>(gz + 1) * step_z;

                    double grid_distance_sq = 0.0;
                    if (qx < low_x) {
                        const double delta = low_x - qx;
                        grid_distance_sq += delta * delta;
                    } else if (qx > high_x) {
                        const double delta = qx - high_x;
                        grid_distance_sq += delta * delta;
                    }
                    if (qy < low_y) {
                        const double delta = low_y - qy;
                        grid_distance_sq += delta * delta;
                    } else if (qy > high_y) {
                        const double delta = qy - high_y;
                        grid_distance_sq += delta * delta;
                    }
                    if (qz < low_z) {
                        const double delta = low_z - qz;
                        grid_distance_sq += delta * delta;
                    } else if (qz > high_z) {
                        const double delta = qz - high_z;
                        grid_distance_sq += delta * delta;
                    }
                    if (grid_distance_sq < shell_min_grid_distance_sq) {
                        shell_min_grid_distance_sq = grid_distance_sq;
                    }
                    if (grid_distance_sq > best_point_distance_sq) {
                        continue;
                    }

                    const int64_t encoded = (static_cast<int64_t>(gx) * static_cast<int64_t>(dim_y)
                            + static_cast<int64_t>(gy)) * static_cast<int64_t>(dim_z)
                            + static_cast<int64_t>(gz);
                    if (encoded < 0 || static_cast<unsigned long long>(encoded) >= dense_cell_position_count) {
                        continue;
                    }
                    const int64_t pos = dense_cell_positions[encoded];
                    if (pos < 0 || static_cast<unsigned long long>(pos) >= cell_count) {
                        continue;
                    }
                    const int64_t count = point_counts[pos];
                    if (count <= 0) {
                        continue;
                    }
                    ++scanned_cells;
                    scanned_points += count;
                    const int64_t begin = point_begin_offsets[pos];
                    for (int64_t offset = 0; offset < count; ++offset) {
                        const int64_t point_slot = begin + offset;
                        if (point_slot < 0 || static_cast<unsigned long long>(point_slot) >= point_row_index_count) {
                            continue;
                        }
                        const int64_t target_row = point_row_indices[point_slot];
                        if (target_row < 0 || static_cast<unsigned long long>(target_row) >= target_count) {
                            continue;
                        }
                        const double tx = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 0ull];
                        const double ty = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 1ull];
                        const double tz = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 2ull];
                        const double ddx = qx - tx;
                        const double ddy = qy - ty;
                        const double ddz = qz - tz;
                        const double distance_sq = ddx * ddx + ddy * ddy + ddz * ddz;
                        const int64_t target_id = target_ids[target_row];
                        if (target_id < 0) {
                            continue;
                        }
                        if (distance_sq < best_point_distance_sq
                                || (distance_sq == best_point_distance_sq && target_id < best_point_id)) {
                            best_point_distance_sq = distance_sq;
                            best_point_id = target_id;
                            best_cell_id = cell_ids[pos];
                            best_cell_point_count = count;
                        }
                    }
                }
            }
        }
        if (best_point_id >= 0 && shell_min_grid_distance_sq > best_point_distance_sq) {
            break;
        }
    }

    if (best_point_id == 9223372036854775807ll) {
        const int64_t pos = 0ll;
        const int64_t begin = point_begin_offsets[pos];
        const int64_t count = point_counts[pos];
        for (int64_t offset = 0; offset < count; ++offset) {
            const int64_t point_slot = begin + offset;
            if (point_slot < 0 || static_cast<unsigned long long>(point_slot) >= point_row_index_count) {
                continue;
            }
            const int64_t target_row = point_row_indices[point_slot];
            if (target_row < 0 || static_cast<unsigned long long>(target_row) >= target_count) {
                continue;
            }
            const double tx = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 0ull];
            const double ty = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 1ull];
            const double tz = target_coords[static_cast<unsigned long long>(target_row) * 3ull + 2ull];
            const double ddx = qx - tx;
            const double ddy = qy - ty;
            const double ddz = qz - tz;
            const double distance_sq = ddx * ddx + ddy * ddy + ddz * ddz;
            const int64_t target_id = target_ids[target_row];
            if (target_id < 0) {
                continue;
            }
            if (distance_sq < best_point_distance_sq
                    || (distance_sq == best_point_distance_sq && target_id < best_point_id)) {
                best_point_distance_sq = distance_sq;
                best_point_id = target_id;
                best_cell_id = cell_ids[pos];
                best_cell_point_count = count;
            }
        }
        ++scanned_cells;
        scanned_points += count;
    }

    nearest_distances_out[query_row] = sqrt(best_point_distance_sq);
    nearest_item_ids_out[query_row] = best_point_id;
    seed_cell_ids_out[query_row] = best_cell_id;
    seed_cell_point_counts_out[query_row] = best_cell_point_count;
    grid_cell_probe_counts_out[query_row] = probes;
    scanned_cell_counts_out[query_row] = scanned_cells;
    scanned_point_counts_out[query_row] = scanned_points;
    shell_counts_out[query_row] = shells;
}

void rtdl_cuda_grid_branch_bound_nearest_seed_3d_precompiled(
        const double* query_coords,
        const int64_t* query_ids,
        uint32_t query_count,
        const double* target_coords,
        const int64_t* target_ids,
        uint32_t target_count,
        const int64_t* cell_ids,
        const int64_t* original_cell_ids,
        const int64_t* dense_cell_positions,
        uint32_t dense_cell_position_count,
        const int64_t* point_begin_offsets,
        const int64_t* point_counts,
        const int64_t* point_row_indices,
        uint32_t point_row_index_count,
        uint32_t cell_count,
        int dim_x,
        int dim_y,
        int dim_z,
        double lower_x,
        double lower_y,
        double lower_z,
        double upper_x,
        double upper_y,
        double upper_z,
        double* nearest_distances_out,
        int64_t* nearest_item_ids_out,
        int64_t* seed_cell_ids_out,
        int64_t* seed_cell_point_counts_out,
        int64_t* grid_cell_probe_counts_out,
        int64_t* scanned_cell_counts_out,
        int64_t* scanned_point_counts_out,
        int64_t* shell_counts_out)
{
    if (query_count == 0) return;
    const unsigned block = 256;
    const unsigned grid = (query_count + block - 1u) / block;
    rtdl_grid_branch_bound_nearest_seed_3d_kernel<<<grid, block>>>(
        query_coords,
        query_ids,
        query_count,
        target_coords,
        target_ids,
        target_count,
        cell_ids,
        original_cell_ids,
        dense_cell_positions,
        dense_cell_position_count,
        point_begin_offsets,
        point_counts,
        point_row_indices,
        point_row_index_count,
        cell_count,
        dim_x,
        dim_y,
        dim_z,
        lower_x,
        lower_y,
        lower_z,
        upper_x,
        upper_y,
        upper_z,
        nearest_distances_out,
        nearest_item_ids_out,
        seed_cell_ids_out,
        seed_cell_point_counts_out,
        grid_cell_probe_counts_out,
        scanned_cell_counts_out,
        scanned_point_counts_out,
        shell_counts_out);
    rtdl_cuda_check(cudaGetLastError(), "launching grid branch-bound nearest seed 3-D kernel");
    rtdl_cuda_check(cudaDeviceSynchronize(), "synchronizing grid branch-bound nearest seed 3-D kernel");
}

static __forceinline__ __device__ void rtdl_bounded_topk_insert_3d(
        double distance_sq,
        int64_t item_id,
        uint32_t limit,
        double* best_distance_sq,
        int64_t* best_item_ids,
        uint32_t* best_count)
{
    uint32_t count = *best_count;
    uint32_t position = 0u;
    while (position < count) {
        if (distance_sq < best_distance_sq[position]
                || (distance_sq == best_distance_sq[position]
                    && item_id < best_item_ids[position])) {
            break;
        }
        ++position;
    }
    if (count < limit) {
        for (uint32_t index = count; index > position; --index) {
            best_distance_sq[index] = best_distance_sq[index - 1u];
            best_item_ids[index] = best_item_ids[index - 1u];
        }
        best_distance_sq[position] = distance_sq;
        best_item_ids[position] = item_id;
        *best_count = count + 1u;
        return;
    }
    if (position >= limit) return;
    for (uint32_t index = limit - 1u; index > position; --index) {
        best_distance_sq[index] = best_distance_sq[index - 1u];
        best_item_ids[index] = best_item_ids[index - 1u];
    }
    best_distance_sq[position] = distance_sq;
    best_item_ids[position] = item_id;
}

static __forceinline__ __device__ double rtdl_point_to_grid_cell_distance_sq_3d(
        double qx,
        double qy,
        double qz,
        int gx,
        int gy,
        int gz,
        double lower_x,
        double lower_y,
        double lower_z,
        double step_x,
        double step_y,
        double step_z)
{
    const double low_x = step_x == 0.0
        ? lower_x : lower_x + static_cast<double>(gx) * step_x;
    const double high_x = step_x == 0.0
        ? lower_x : lower_x + static_cast<double>(gx + 1) * step_x;
    const double low_y = step_y == 0.0
        ? lower_y : lower_y + static_cast<double>(gy) * step_y;
    const double high_y = step_y == 0.0
        ? lower_y : lower_y + static_cast<double>(gy + 1) * step_y;
    const double low_z = step_z == 0.0
        ? lower_z : lower_z + static_cast<double>(gz) * step_z;
    const double high_z = step_z == 0.0
        ? lower_z : lower_z + static_cast<double>(gz + 1) * step_z;
    double distance_sq = 0.0;
    if (qx < low_x) {
        const double delta = low_x - qx;
        distance_sq += delta * delta;
    } else if (qx > high_x) {
        const double delta = qx - high_x;
        distance_sq += delta * delta;
    }
    if (qy < low_y) {
        const double delta = low_y - qy;
        distance_sq += delta * delta;
    } else if (qy > high_y) {
        const double delta = qy - high_y;
        distance_sq += delta * delta;
    }
    if (qz < low_z) {
        const double delta = low_z - qz;
        distance_sq += delta * delta;
    } else if (qz > high_z) {
        const double delta = qz - high_z;
        distance_sq += delta * delta;
    }
    return distance_sq;
}

static __global__ void rtdl_grid_branch_bound_exact_bounded_topk_3d_kernel(
        const double* query_coords,
        uint32_t query_count,
        const double* target_coords,
        const int64_t* target_ids,
        uint32_t target_count,
        const int64_t* dense_cell_positions,
        uint32_t dense_cell_position_count,
        const int64_t* point_begin_offsets,
        const int64_t* point_counts,
        const int64_t* point_row_indices,
        uint32_t point_row_index_count,
        uint32_t cell_count,
        int dim_x,
        int dim_y,
        int dim_z,
        double lower_x,
        double lower_y,
        double lower_z,
        double upper_x,
        double upper_y,
        double upper_z,
        double minimum_distance,
        double maximum_distance,
        uint32_t limit,
        uint32_t minimum_boundary_mode,
        uint32_t maximum_boundary_mode,
        uint32_t* counts_out,
        int64_t* item_ids_out,
        double* distances_out,
        int64_t* candidate_distance_evaluations_out,
        int64_t* grid_cell_probes_out,
        int64_t* scanned_cell_counts_out)
{
    const uint32_t query_row = blockIdx.x * blockDim.x + threadIdx.x;
    if (query_row >= query_count) return;
    const double qx =
        query_coords[static_cast<unsigned long long>(query_row) * 3ull + 0ull];
    const double qy =
        query_coords[static_cast<unsigned long long>(query_row) * 3ull + 1ull];
    const double qz =
        query_coords[static_cast<unsigned long long>(query_row) * 3ull + 2ull];
    const double extent_x = upper_x - lower_x;
    const double extent_y = upper_y - lower_y;
    const double extent_z = upper_z - lower_z;
    const double step_x =
        extent_x == 0.0 ? 0.0 : extent_x / static_cast<double>(dim_x);
    const double step_y =
        extent_y == 0.0 ? 0.0 : extent_y / static_cast<double>(dim_y);
    const double step_z =
        extent_z == 0.0 ? 0.0 : extent_z / static_cast<double>(dim_z);
    int base_x = step_x == 0.0
        ? 0 : static_cast<int>(floor((qx - lower_x) / step_x));
    int base_y = step_y == 0.0
        ? 0 : static_cast<int>(floor((qy - lower_y) / step_y));
    int base_z = step_z == 0.0
        ? 0 : static_cast<int>(floor((qz - lower_z) / step_z));
    if (base_x < 0) base_x = 0;
    if (base_x >= dim_x) base_x = dim_x - 1;
    if (base_y < 0) base_y = 0;
    if (base_y >= dim_y) base_y = dim_y - 1;
    if (base_z < 0) base_z = 0;
    if (base_z >= dim_z) base_z = dim_z - 1;

    double best_distance_sq[64];
    int64_t best_item_ids[64];
    for (uint32_t index = 0u; index < limit; ++index) {
        best_distance_sq[index] = INFINITY;
        best_item_ids[index] = 9223372036854775807ll;
    }
    uint32_t best_count = 0u;
    const double minimum_distance_sq = minimum_distance * minimum_distance;
    const double maximum_distance_sq = maximum_distance * maximum_distance;
    int max_shell = dim_x;
    if (dim_y > max_shell) max_shell = dim_y;
    if (dim_z > max_shell) max_shell = dim_z;
    int64_t candidate_evaluations = 0ll;
    int64_t grid_probes = 0ll;
    int64_t scanned_cells = 0ll;

    for (int radius = 0; radius <= max_shell; ++radius) {
        double shell_min_distance_sq = INFINITY;
        for (int dx_shell = -radius; dx_shell <= radius; ++dx_shell) {
            const int gx = base_x + dx_shell;
            if (gx < 0 || gx >= dim_x) continue;
            const int abs_dx = dx_shell >= 0 ? dx_shell : -dx_shell;
            for (int dy_shell = -radius; dy_shell <= radius; ++dy_shell) {
                const int gy = base_y + dy_shell;
                if (gy < 0 || gy >= dim_y) continue;
                const int abs_dy = dy_shell >= 0 ? dy_shell : -dy_shell;
                for (int dz_shell = -radius; dz_shell <= radius; ++dz_shell) {
                    const int gz = base_z + dz_shell;
                    if (gz < 0 || gz >= dim_z) continue;
                    const int abs_dz = dz_shell >= 0 ? dz_shell : -dz_shell;
                    int shell = abs_dx;
                    if (abs_dy > shell) shell = abs_dy;
                    if (abs_dz > shell) shell = abs_dz;
                    if (shell != radius) continue;
                    ++grid_probes;
                    const double cell_distance_sq =
                        rtdl_point_to_grid_cell_distance_sq_3d(
                            qx, qy, qz, gx, gy, gz,
                            lower_x, lower_y, lower_z,
                            step_x, step_y, step_z);
                    if (cell_distance_sq < shell_min_distance_sq) {
                        shell_min_distance_sq = cell_distance_sq;
                    }
                    double pruning_bound_sq = maximum_distance_sq;
                    if (best_count == limit
                            && best_distance_sq[limit - 1u] < pruning_bound_sq) {
                        pruning_bound_sq = best_distance_sq[limit - 1u];
                    }
                    if (cell_distance_sq > pruning_bound_sq) continue;
                    const int64_t encoded =
                        (static_cast<int64_t>(gx) * static_cast<int64_t>(dim_y)
                         + static_cast<int64_t>(gy)) * static_cast<int64_t>(dim_z)
                        + static_cast<int64_t>(gz);
                    if (encoded < 0
                            || static_cast<unsigned long long>(encoded)
                                >= dense_cell_position_count) {
                        continue;
                    }
                    const int64_t position = dense_cell_positions[encoded];
                    if (position < 0
                            || static_cast<unsigned long long>(position)
                                >= cell_count) {
                        continue;
                    }
                    const int64_t point_count = point_counts[position];
                    if (point_count <= 0) continue;
                    ++scanned_cells;
                    const int64_t begin = point_begin_offsets[position];
                    for (int64_t offset = 0; offset < point_count; ++offset) {
                        const int64_t point_slot = begin + offset;
                        if (point_slot < 0
                                || static_cast<unsigned long long>(point_slot)
                                    >= point_row_index_count) {
                            continue;
                        }
                        const int64_t target_row = point_row_indices[point_slot];
                        if (target_row < 0
                                || static_cast<unsigned long long>(target_row)
                                    >= target_count) {
                            continue;
                        }
                        ++candidate_evaluations;
                        const double tx =
                            target_coords[
                                static_cast<unsigned long long>(target_row) * 3ull
                                + 0ull];
                        const double ty =
                            target_coords[
                                static_cast<unsigned long long>(target_row) * 3ull
                                + 1ull];
                        const double tz =
                            target_coords[
                                static_cast<unsigned long long>(target_row) * 3ull
                                + 2ull];
                        const double dx = tx - qx;
                        const double dy = ty - qy;
                        const double dz = tz - qz;
                        const double distance_sq =
                            dx * dx + dy * dy + dz * dz;
                        const bool below_minimum =
                            minimum_boundary_mode == 0u
                            ? distance_sq < minimum_distance_sq
                            : distance_sq <= minimum_distance_sq;
                        const bool above_maximum =
                            maximum_boundary_mode == 0u
                            ? distance_sq > maximum_distance_sq
                            : distance_sq >= maximum_distance_sq;
                        if (below_minimum || above_maximum) continue;
                        const int64_t item_id = target_ids[target_row];
                        if (item_id < 0) continue;
                        rtdl_bounded_topk_insert_3d(
                            distance_sq,
                            item_id,
                            limit,
                            best_distance_sq,
                            best_item_ids,
                            &best_count);
                    }
                }
            }
        }
        double completed_shell_bound_sq = maximum_distance_sq;
        if (best_count == limit
                && best_distance_sq[limit - 1u] < completed_shell_bound_sq) {
            completed_shell_bound_sq = best_distance_sq[limit - 1u];
        }
        if (shell_min_distance_sq > completed_shell_bound_sq) break;
    }

    counts_out[query_row] = best_count;
    const unsigned long long row_begin =
        static_cast<unsigned long long>(query_row)
        * static_cast<unsigned long long>(limit);
    for (uint32_t rank = 0u; rank < best_count; ++rank) {
        item_ids_out[row_begin + rank] = best_item_ids[rank];
        distances_out[row_begin + rank] = sqrt(best_distance_sq[rank]);
    }
    candidate_distance_evaluations_out[query_row] = candidate_evaluations;
    grid_cell_probes_out[query_row] = grid_probes;
    scanned_cell_counts_out[query_row] = scanned_cells;
}

static void rtdl_cuda_write_error(char* error_out, uint64_t error_capacity, const char* message)
{
    if (error_out == nullptr || error_capacity == 0) return;
    if (message == nullptr) message = "unknown CUDA helper error";
    std::strncpy(error_out, message, static_cast<size_t>(error_capacity - 1));
    error_out[error_capacity - 1] = '\0';
}

static __global__ void rtdl_encode_point_grid_cells_3d_kernel(
        const double* coords,
        uint64_t point_count,
        int64_t dim_x,
        int64_t dim_y,
        int64_t dim_z,
        double lower_x,
        double lower_y,
        double lower_z,
        double upper_x,
        double upper_y,
        double upper_z,
        int64_t* encoded_out)
{
    const uint64_t idx = static_cast<uint64_t>(blockIdx.x) * blockDim.x + threadIdx.x;
    if (idx >= point_count) return;
    const double x = coords[idx * 3 + 0];
    const double y = coords[idx * 3 + 1];
    const double z = coords[idx * 3 + 2];
    const double extent_x = upper_x - lower_x;
    const double extent_y = upper_y - lower_y;
    const double extent_z = upper_z - lower_z;
    int64_t px = 0;
    int64_t py = 0;
    int64_t pz = 0;
    if (extent_x != 0.0) {
        px = static_cast<int64_t>(floor(((x - lower_x) / extent_x) * static_cast<double>(dim_x)));
        if (px < 0) px = 0;
        if (px >= dim_x) px = dim_x - 1;
    }
    if (extent_y != 0.0) {
        py = static_cast<int64_t>(floor(((y - lower_y) / extent_y) * static_cast<double>(dim_y)));
        if (py < 0) py = 0;
        if (py >= dim_y) py = dim_y - 1;
    }
    if (extent_z != 0.0) {
        pz = static_cast<int64_t>(floor(((z - lower_z) / extent_z) * static_cast<double>(dim_z)));
        if (pz < 0) pz = 0;
        if (pz >= dim_z) pz = dim_z - 1;
    }
    encoded_out[idx] = (px * dim_y + py) * dim_z + pz;
}

static __global__ void rtdl_split_xyz_columns_kernel(
        const double* coords,
        uint64_t point_count,
        double* x_out,
        double* y_out,
        double* z_out)
{
    const uint64_t idx = static_cast<uint64_t>(blockIdx.x) * blockDim.x + threadIdx.x;
    if (idx >= point_count) return;
    x_out[idx] = coords[idx * 3 + 0];
    y_out[idx] = coords[idx * 3 + 1];
    z_out[idx] = coords[idx * 3 + 2];
}

struct RtdlCellPointIdCompare {
    using Tuple = thrust::tuple<int64_t, int64_t, int64_t>;

    __host__ __device__ bool operator()(const Tuple& a, const Tuple& b) const
    {
        const int64_t cell_a = thrust::get<0>(a);
        const int64_t cell_b = thrust::get<0>(b);
        if (cell_a != cell_b) return cell_a < cell_b;
        const int64_t id_a = thrust::get<1>(a);
        const int64_t id_b = thrust::get<1>(b);
        if (id_a != id_b) return id_a < id_b;
        return thrust::get<2>(a) < thrust::get<2>(b);
    }
};

extern "C" int rtdl_cuda_point_grid_cell_mbrs_3d(
        const double* coords,
        const int64_t* point_ids,
        uint64_t point_count,
        const int64_t* grid_shape,
        const double* grid_lower_bounds,
        const double* grid_upper_bounds,
        uint32_t cell_point_order_code,
        uint64_t cell_capacity,
        int64_t* cell_ids_out,
        int64_t* original_cell_ids_out,
        int64_t* point_begin_offsets_out,
        int64_t* point_counts_out,
        int64_t* point_ids_out,
        int64_t* point_row_indices_out,
        double* min_x_out,
        double* min_y_out,
        double* min_z_out,
        double* max_x_out,
        double* max_y_out,
        double* max_z_out,
        uint64_t* cell_count_out,
        char* error_out,
        uint64_t error_capacity)
{
    try {
        if (cell_count_out == nullptr) throw std::runtime_error("cell_count_out must not be null");
        *cell_count_out = 0;
        if (point_count == 0) throw std::runtime_error("point_count must be positive");
        if (!coords || !point_ids || !grid_shape || !grid_lower_bounds || !grid_upper_bounds) {
            throw std::runtime_error("input pointers must not be null");
        }
        if (!cell_ids_out || !original_cell_ids_out || !point_begin_offsets_out || !point_counts_out
                || !point_ids_out || !point_row_indices_out
                || !min_x_out || !min_y_out || !min_z_out || !max_x_out || !max_y_out || !max_z_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (cell_point_order_code > 1) {
            throw std::runtime_error("cell_point_order_code must be 0 (point-id) or 1 (input-stable)");
        }
        const int64_t dim_x = grid_shape[0];
        const int64_t dim_y = grid_shape[1];
        const int64_t dim_z = grid_shape[2];
        if (dim_x <= 0 || dim_y <= 0 || dim_z <= 0) {
            throw std::runtime_error("grid_shape entries must be positive");
        }

        thrust::device_vector<double> d_coords(point_count * 3);
        thrust::device_vector<int64_t> d_point_ids(point_count);
        rtdl_cuda_check(cudaMemcpy(
            thrust::raw_pointer_cast(d_coords.data()),
            coords,
            sizeof(double) * static_cast<size_t>(point_count) * 3,
            cudaMemcpyHostToDevice), "uploading grid point coordinates");
        rtdl_cuda_check(cudaMemcpy(
            thrust::raw_pointer_cast(d_point_ids.data()),
            point_ids,
            sizeof(int64_t) * static_cast<size_t>(point_count),
            cudaMemcpyHostToDevice), "uploading grid point ids");
        thrust::device_vector<int64_t> d_original_point_ids = d_point_ids;

        thrust::device_vector<int64_t> d_encoded(point_count);
        thrust::device_vector<int64_t> d_row_indices(point_count);
        thrust::sequence(thrust::device, d_row_indices.begin(), d_row_indices.end(), int64_t{0});

        const unsigned block = 256;
        const unsigned grid = static_cast<unsigned>((point_count + block - 1) / block);
        rtdl_encode_point_grid_cells_3d_kernel<<<grid, block>>>(
            thrust::raw_pointer_cast(d_coords.data()),
            point_count,
            dim_x,
            dim_y,
            dim_z,
            grid_lower_bounds[0],
            grid_lower_bounds[1],
            grid_lower_bounds[2],
            grid_upper_bounds[0],
            grid_upper_bounds[1],
            grid_upper_bounds[2],
            thrust::raw_pointer_cast(d_encoded.data()));
        rtdl_cuda_check(cudaGetLastError(), "launching point grid cell encode kernel");

        if (cell_point_order_code == 0) {
            auto first = thrust::make_zip_iterator(thrust::make_tuple(
                d_encoded.begin(),
                d_point_ids.begin(),
                d_row_indices.begin()));
            thrust::sort(thrust::device, first, first + static_cast<ptrdiff_t>(point_count),
                RtdlCellPointIdCompare{});
        } else {
            thrust::stable_sort_by_key(thrust::device, d_encoded.begin(), d_encoded.end(), d_row_indices.begin());
        }

        thrust::device_vector<int64_t> d_sorted_point_ids(point_count);
        thrust::gather(
            thrust::device,
            d_row_indices.begin(),
            d_row_indices.end(),
            d_original_point_ids.begin(),
            d_sorted_point_ids.begin());

        thrust::device_vector<int64_t> d_unique_cells(point_count);
        thrust::device_vector<int64_t> d_counts(point_count);
        auto reduce_end = thrust::reduce_by_key(
            thrust::device,
            d_encoded.begin(),
            d_encoded.end(),
            thrust::make_constant_iterator(int64_t{1}),
            d_unique_cells.begin(),
            d_counts.begin());
        const uint64_t cell_count = static_cast<uint64_t>(reduce_end.first - d_unique_cells.begin());
        if (cell_count > cell_capacity) {
            throw std::runtime_error("cell output capacity is too small");
        }
        thrust::device_vector<int64_t> d_cell_ids(cell_count);
        thrust::device_vector<int64_t> d_begins(cell_count);
        thrust::sequence(thrust::device, d_cell_ids.begin(), d_cell_ids.end(), int64_t{0});
        thrust::exclusive_scan(thrust::device, d_counts.begin(), d_counts.begin() + static_cast<ptrdiff_t>(cell_count), d_begins.begin(), int64_t{0});

        thrust::device_vector<double> d_x(point_count);
        thrust::device_vector<double> d_y(point_count);
        thrust::device_vector<double> d_z(point_count);
        thrust::device_vector<double> d_sorted_x(point_count);
        thrust::device_vector<double> d_sorted_y(point_count);
        thrust::device_vector<double> d_sorted_z(point_count);
        thrust::device_vector<int64_t> d_throwaway_keys(point_count);
        thrust::device_vector<double> d_min_x(point_count);
        thrust::device_vector<double> d_min_y(point_count);
        thrust::device_vector<double> d_min_z(point_count);
        thrust::device_vector<double> d_max_x(point_count);
        thrust::device_vector<double> d_max_y(point_count);
        thrust::device_vector<double> d_max_z(point_count);
        rtdl_split_xyz_columns_kernel<<<grid, block>>>(
            thrust::raw_pointer_cast(d_coords.data()),
            point_count,
            thrust::raw_pointer_cast(d_x.data()),
            thrust::raw_pointer_cast(d_y.data()),
            thrust::raw_pointer_cast(d_z.data()));
        rtdl_cuda_check(cudaGetLastError(), "launching xyz split kernel");
        thrust::gather(thrust::device, d_row_indices.begin(), d_row_indices.end(), d_x.begin(), d_sorted_x.begin());
        thrust::gather(thrust::device, d_row_indices.begin(), d_row_indices.end(), d_y.begin(), d_sorted_y.begin());
        thrust::gather(thrust::device, d_row_indices.begin(), d_row_indices.end(), d_z.begin(), d_sorted_z.begin());

        thrust::reduce_by_key(thrust::device, d_encoded.begin(), d_encoded.end(), d_sorted_x.begin(), d_throwaway_keys.begin(), d_min_x.begin(), thrust::equal_to<int64_t>(), thrust::minimum<double>());
        thrust::reduce_by_key(thrust::device, d_encoded.begin(), d_encoded.end(), d_sorted_y.begin(), d_throwaway_keys.begin(), d_min_y.begin(), thrust::equal_to<int64_t>(), thrust::minimum<double>());
        thrust::reduce_by_key(thrust::device, d_encoded.begin(), d_encoded.end(), d_sorted_z.begin(), d_throwaway_keys.begin(), d_min_z.begin(), thrust::equal_to<int64_t>(), thrust::minimum<double>());
        thrust::reduce_by_key(thrust::device, d_encoded.begin(), d_encoded.end(), d_sorted_x.begin(), d_throwaway_keys.begin(), d_max_x.begin(), thrust::equal_to<int64_t>(), thrust::maximum<double>());
        thrust::reduce_by_key(thrust::device, d_encoded.begin(), d_encoded.end(), d_sorted_y.begin(), d_throwaway_keys.begin(), d_max_y.begin(), thrust::equal_to<int64_t>(), thrust::maximum<double>());
        thrust::reduce_by_key(thrust::device, d_encoded.begin(), d_encoded.end(), d_sorted_z.begin(), d_throwaway_keys.begin(), d_max_z.begin(), thrust::equal_to<int64_t>(), thrust::maximum<double>());

        rtdl_cuda_check(cudaMemcpy(cell_ids_out, thrust::raw_pointer_cast(d_cell_ids.data()), sizeof(int64_t) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading cell ids");
        rtdl_cuda_check(cudaMemcpy(original_cell_ids_out, thrust::raw_pointer_cast(d_unique_cells.data()), sizeof(int64_t) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading original cell ids");
        rtdl_cuda_check(cudaMemcpy(point_begin_offsets_out, thrust::raw_pointer_cast(d_begins.data()), sizeof(int64_t) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading point begin offsets");
        rtdl_cuda_check(cudaMemcpy(point_counts_out, thrust::raw_pointer_cast(d_counts.data()), sizeof(int64_t) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading point counts");
        rtdl_cuda_check(cudaMemcpy(point_ids_out, thrust::raw_pointer_cast(d_sorted_point_ids.data()), sizeof(int64_t) * static_cast<size_t>(point_count), cudaMemcpyDeviceToHost), "downloading sorted point ids");
        rtdl_cuda_check(cudaMemcpy(point_row_indices_out, thrust::raw_pointer_cast(d_row_indices.data()), sizeof(int64_t) * static_cast<size_t>(point_count), cudaMemcpyDeviceToHost), "downloading point row indices");
        rtdl_cuda_check(cudaMemcpy(min_x_out, thrust::raw_pointer_cast(d_min_x.data()), sizeof(double) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading min x");
        rtdl_cuda_check(cudaMemcpy(min_y_out, thrust::raw_pointer_cast(d_min_y.data()), sizeof(double) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading min y");
        rtdl_cuda_check(cudaMemcpy(min_z_out, thrust::raw_pointer_cast(d_min_z.data()), sizeof(double) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading min z");
        rtdl_cuda_check(cudaMemcpy(max_x_out, thrust::raw_pointer_cast(d_max_x.data()), sizeof(double) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading max x");
        rtdl_cuda_check(cudaMemcpy(max_y_out, thrust::raw_pointer_cast(d_max_y.data()), sizeof(double) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading max y");
        rtdl_cuda_check(cudaMemcpy(max_z_out, thrust::raw_pointer_cast(d_max_z.data()), sizeof(double) * static_cast<size_t>(cell_count), cudaMemcpyDeviceToHost), "downloading max z");
        *cell_count_out = cell_count;
        rtdl_cuda_check(cudaDeviceSynchronize(), "synchronizing point grid cell MBR builder");
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(error_out, error_capacity, "unknown point grid cell MBR builder failure");
        return 1;
    }
}

// Closed, app-neutral prepared lifetime for an exact 3-D nearest-state
// producer followed by a global max-witness reduction.  Targets and the
// compact grid stay resident for the lifetime of this owner.  Each execution
// uploads only the query batch and downloads one witness, bounded validation
// samples, and scalar work counters; the complete nearest-state columns never
// cross back to the host.
struct RtdlCudaPreparedNearestGrid3D {
    int64_t dim_x;
    int64_t dim_y;
    int64_t dim_z;
    double lower_x;
    double lower_y;
    double lower_z;
    double upper_x;
    double upper_y;
    double upper_z;
    uint64_t target_count;
    uint64_t cell_count;
    uint64_t dense_cell_position_count;
    thrust::device_vector<double> target_coords;
    thrust::device_vector<int64_t> target_ids;
    thrust::device_vector<int64_t> cell_ids;
    thrust::device_vector<int64_t> original_cell_ids;
    thrust::device_vector<int64_t> dense_cell_positions;
    thrust::device_vector<int64_t> point_begin_offsets;
    thrust::device_vector<int64_t> point_counts;
    thrust::device_vector<int64_t> point_row_indices;
};

struct RtdlNearestGlobalWitnessLess {
    using Tuple = thrust::tuple<double, int64_t, int64_t>;

    __host__ __device__ bool operator()(const Tuple& left, const Tuple& right) const
    {
        const double left_distance = thrust::get<0>(left);
        const double right_distance = thrust::get<0>(right);
        if (left_distance != right_distance) return left_distance < right_distance;
        // The generic host reducer resolves a distance tie by the lowest
        // logical group row, then the lowest item id.  Reverse those keys for
        // max_element so the same row wins on device.
        const int64_t left_row = thrust::get<1>(left);
        const int64_t right_row = thrust::get<1>(right);
        if (left_row != right_row) return left_row > right_row;
        return thrust::get<2>(left) > thrust::get<2>(right);
    }
};

struct RtdlFinalNearestDistanceFromSquared {
    __host__ __device__ double operator()(double squared) const
    {
        return sqrt(squared);
    }
};

// ABI-stable view shared with the prepared OptiX cell-MBR owner.  This mirrors
// GpuCellMbr3D in rtdl_optix_workloads.cpp; the static assertions on the host
// side of that owner guard the layout before a pointer crosses this boundary.
struct RtdlCudaCellMbr3DView {
    double min_x;
    double min_y;
    double min_z;
    double max_x;
    double max_y;
    double max_z;
    int64_t cell_id;
    uint64_t point_begin_offset;
    uint64_t point_count;
};
static_assert(
    sizeof(RtdlCudaCellMbr3DView) == 72,
    "RtdlCudaCellMbr3DView ABI size changed");
static_assert(
    offsetof(RtdlCudaCellMbr3DView, cell_id) == 48,
    "RtdlCudaCellMbr3DView cell_id offset changed");
static_assert(
    offsetof(RtdlCudaCellMbr3DView, point_begin_offset) == 56,
    "RtdlCudaCellMbr3DView point_begin_offset offset changed");
static_assert(
    offsetof(RtdlCudaCellMbr3DView, point_count) == 64,
    "RtdlCudaCellMbr3DView point_count offset changed");

__global__ static void rtdl_complete_heavy_cell_nearest_3d_kernel(
        const double* query_coords,
        uint32_t query_count,
        const double* target_coords,
        const int64_t* target_ids,
        uint32_t target_count,
        const RtdlCudaCellMbr3DView* cells,
        uint32_t cell_count,
        const uint64_t* point_row_indices,
        uint64_t point_row_index_count,
        uint64_t max_inline_points,
        double* nearest_distance_squares,
        int64_t* nearest_item_ids,
        uint64_t* heavy_cell_probe_counts,
        uint64_t* heavy_point_eval_counts)
{
    const uint32_t query_index = blockIdx.x * blockDim.x + threadIdx.x;
    if (query_index >= query_count) return;
    const double qx = query_coords[static_cast<uint64_t>(query_index) * 3ULL + 0ULL];
    const double qy = query_coords[static_cast<uint64_t>(query_index) * 3ULL + 1ULL];
    const double qz = query_coords[static_cast<uint64_t>(query_index) * 3ULL + 2ULL];
    double best_sq = nearest_distance_squares[query_index];
    int64_t best_id = nearest_item_ids[query_index];
    bool found = best_id >= 0 && best_sq >= 0.0 && isfinite(best_sq);
    uint64_t cell_probes = 0ULL;
    uint64_t point_evals = 0ULL;
    for (uint32_t cell_index = 0; cell_index < cell_count; ++cell_index) {
        const RtdlCudaCellMbr3DView cell = cells[cell_index];
        if (cell.point_count <= max_inline_points) continue;
        ++cell_probes;
        const double dx = qx < cell.min_x
            ? cell.min_x - qx
            : (qx > cell.max_x ? qx - cell.max_x : 0.0);
        const double dy = qy < cell.min_y
            ? cell.min_y - qy
            : (qy > cell.max_y ? qy - cell.max_y : 0.0);
        const double dz = qz < cell.min_z
            ? cell.min_z - qz
            : (qz > cell.max_z ? qz - cell.max_z : 0.0);
        const double lower_sq = dx * dx + dy * dy + dz * dz;
        if (found && lower_sq > best_sq) continue;
        if (cell.point_begin_offset > point_row_index_count
                || cell.point_count > point_row_index_count - cell.point_begin_offset) {
            // The prepared host owner validates this invariant.  Preserve a
            // deterministic invalid marker if device memory is corrupted;
            // the host-side result validator will fail closed.
            nearest_distance_squares[query_index] = (0.0 / 0.0);
            nearest_item_ids[query_index] = -1;
            heavy_cell_probe_counts[query_index] = cell_probes;
            heavy_point_eval_counts[query_index] = point_evals;
            return;
        }
        for (uint64_t offset = 0; offset < cell.point_count; ++offset) {
            const uint64_t point_slot = cell.point_begin_offset + offset;
            const uint64_t target_row = point_row_indices[point_slot];
            if (target_row >= static_cast<uint64_t>(target_count)) {
                nearest_distance_squares[query_index] = (0.0 / 0.0);
                nearest_item_ids[query_index] = -1;
                heavy_cell_probe_counts[query_index] = cell_probes;
                heavy_point_eval_counts[query_index] = point_evals;
                return;
            }
            ++point_evals;
            const double tx = target_coords[target_row * 3ULL + 0ULL];
            const double ty = target_coords[target_row * 3ULL + 1ULL];
            const double tz = target_coords[target_row * 3ULL + 2ULL];
            const double px = tx - qx;
            const double py = ty - qy;
            const double pz = tz - qz;
            const double distance_sq = px * px + py * py + pz * pz;
            const int64_t target_id = target_ids[target_row];
            if (target_id < 0) {
                nearest_distance_squares[query_index] = (0.0 / 0.0);
                nearest_item_ids[query_index] = -1;
                heavy_cell_probe_counts[query_index] = cell_probes;
                heavy_point_eval_counts[query_index] = point_evals;
                return;
            }
            if (!found
                    || distance_sq < best_sq
                    || (distance_sq == best_sq && target_id < best_id)) {
                found = true;
                best_sq = distance_sq;
                best_id = target_id;
            }
        }
    }
    nearest_distance_squares[query_index] = found ? best_sq : (1.0 / 0.0);
    nearest_item_ids[query_index] = found ? best_id : -1;
    heavy_cell_probe_counts[query_index] = cell_probes;
    heavy_point_eval_counts[query_index] = point_evals;
}

extern "C" int rtdl_cuda_complete_heavy_cells_and_reduce_nearest_global_witness_3d(
        const double* query_coords_device,
        const int64_t* query_ids_device,
        uint64_t query_count,
        const double* target_coords_device,
        const int64_t* target_ids_device,
        uint64_t target_count,
        const void* cells_device,
        uint64_t cell_count,
        const uint64_t* point_row_indices_device,
        uint64_t point_row_index_count,
        uint64_t max_inline_points,
        double* nearest_distance_squares_device,
        int64_t* nearest_item_ids_device,
        const int64_t* validation_sample_indices,
        uint64_t validation_sample_count,
        int64_t* witness_source_id_out,
        int64_t* witness_item_id_out,
        double* witness_distance_out,
        int64_t* validation_item_ids_out,
        double* validation_distances_out,
        uint64_t* heavy_cell_probes_out,
        uint64_t* heavy_point_evaluations_out,
        char* error_out,
        uint64_t error_capacity)
{
    try {
        if (query_count == 0 || query_count > static_cast<uint64_t>(UINT32_MAX)) {
            throw std::runtime_error("prepared OptiX nearest query_count must fit positive uint32");
        }
        if (target_count == 0 || target_count > static_cast<uint64_t>(UINT32_MAX)
                || cell_count == 0 || cell_count > static_cast<uint64_t>(UINT32_MAX)) {
            throw std::runtime_error("prepared OptiX nearest target/cell counts must fit positive uint32");
        }
        if (!query_coords_device || !query_ids_device || !target_coords_device
                || !target_ids_device || !cells_device || !point_row_indices_device
                || !nearest_distance_squares_device || !nearest_item_ids_device
                || !witness_source_id_out || !witness_item_id_out
                || !witness_distance_out || !heavy_cell_probes_out
                || !heavy_point_evaluations_out) {
            throw std::runtime_error("prepared OptiX nearest device/output pointers must not be null");
        }
        if (validation_sample_count != 0
                && (!validation_sample_indices
                    || !validation_item_ids_out
                    || !validation_distances_out)) {
            throw std::runtime_error("prepared OptiX nearest validation pointers must not be null");
        }
        thrust::device_vector<uint64_t> d_heavy_cell_probes(query_count);
        thrust::device_vector<uint64_t> d_heavy_point_evaluations(query_count);
        const unsigned block = 128;
        const unsigned grid = static_cast<unsigned>((query_count + block - 1) / block);
        rtdl_complete_heavy_cell_nearest_3d_kernel<<<grid, block>>>(
            query_coords_device,
            static_cast<uint32_t>(query_count),
            target_coords_device,
            target_ids_device,
            static_cast<uint32_t>(target_count),
            static_cast<const RtdlCudaCellMbr3DView*>(cells_device),
            static_cast<uint32_t>(cell_count),
            point_row_indices_device,
            point_row_index_count,
            max_inline_points,
            nearest_distance_squares_device,
            nearest_item_ids_device,
            thrust::raw_pointer_cast(d_heavy_cell_probes.data()),
            thrust::raw_pointer_cast(d_heavy_point_evaluations.data()));
        rtdl_cuda_check(
            cudaGetLastError(),
            "launching prepared OptiX nearest heavy-cell continuation");
        rtdl_cuda_check(
            cudaDeviceSynchronize(),
            "synchronizing prepared OptiX nearest heavy-cell continuation");

        // The nearest-state producer deliberately keeps squared distance for
        // exact per-query selection and inline/heavy continuation.  The
        // consumer contract, however, reduces the materialized F64 distance.
        // sqrt is not injective in F64, so reducing the squared state can pick
        // a different source row when two final distances round equal.
        thrust::device_vector<double> d_final_distances(query_count);
        auto squared_begin =
            thrust::device_pointer_cast(nearest_distance_squares_device);
        thrust::transform(
            thrust::device,
            squared_begin,
            squared_begin + static_cast<ptrdiff_t>(query_count),
            d_final_distances.begin(),
            RtdlFinalNearestDistanceFromSquared{});
        auto first = thrust::make_zip_iterator(thrust::make_tuple(
            d_final_distances.begin(),
            thrust::make_counting_iterator(int64_t{0}),
            thrust::device_pointer_cast(nearest_item_ids_device)));
        auto last = first + static_cast<ptrdiff_t>(query_count);
        auto winner = thrust::max_element(
            thrust::device,
            first,
            last,
            RtdlNearestGlobalWitnessLess{});
        const ptrdiff_t winner_index = winner - first;
        *heavy_cell_probes_out = thrust::reduce(
            thrust::device,
            d_heavy_cell_probes.begin(),
            d_heavy_cell_probes.end(),
            uint64_t{0});
        *heavy_point_evaluations_out = thrust::reduce(
            thrust::device,
            d_heavy_point_evaluations.begin(),
            d_heavy_point_evaluations.end(),
            uint64_t{0});
        rtdl_cuda_check(cudaMemcpy(
            witness_source_id_out,
            query_ids_device + winner_index,
            sizeof(int64_t),
            cudaMemcpyDeviceToHost), "downloading prepared OptiX nearest witness source id");
        rtdl_cuda_check(cudaMemcpy(
            witness_item_id_out,
            nearest_item_ids_device + winner_index,
            sizeof(int64_t),
            cudaMemcpyDeviceToHost), "downloading prepared OptiX nearest witness item id");
        rtdl_cuda_check(cudaMemcpy(
            witness_distance_out,
            thrust::raw_pointer_cast(d_final_distances.data()) + winner_index,
            sizeof(double),
            cudaMemcpyDeviceToHost), "downloading prepared OptiX nearest materialized F64 witness distance");
        if (!std::isfinite(*witness_distance_out) || *witness_distance_out < 0.0) {
            throw std::runtime_error(
                "prepared OptiX nearest materialized F64 witness distance is invalid");
        }
        if (validation_sample_count != 0) {
            thrust::device_vector<int64_t> d_sample_indices(validation_sample_count);
            rtdl_cuda_check(cudaMemcpy(
                thrust::raw_pointer_cast(d_sample_indices.data()),
                validation_sample_indices,
                sizeof(int64_t) * static_cast<size_t>(validation_sample_count),
                cudaMemcpyHostToDevice), "uploading prepared OptiX nearest validation sample indices");
            thrust::device_vector<int64_t> d_sample_item_ids(validation_sample_count);
            thrust::device_vector<double> d_sample_distances(validation_sample_count);
            thrust::gather(
                thrust::device,
                d_sample_indices.begin(),
                d_sample_indices.end(),
                thrust::device_pointer_cast(nearest_item_ids_device),
                d_sample_item_ids.begin());
            thrust::gather(
                thrust::device,
                d_sample_indices.begin(),
                d_sample_indices.end(),
                d_final_distances.begin(),
                d_sample_distances.begin());
            rtdl_cuda_check(cudaMemcpy(
                validation_item_ids_out,
                thrust::raw_pointer_cast(d_sample_item_ids.data()),
                sizeof(int64_t) * static_cast<size_t>(validation_sample_count),
                cudaMemcpyDeviceToHost), "downloading prepared OptiX nearest validation item ids");
            rtdl_cuda_check(cudaMemcpy(
                validation_distances_out,
                thrust::raw_pointer_cast(d_sample_distances.data()),
                sizeof(double) * static_cast<size_t>(validation_sample_count),
                cudaMemcpyDeviceToHost), "downloading prepared OptiX nearest validation F64 distances");
            for (uint64_t row = 0; row < validation_sample_count; ++row) {
                const double distance = validation_distances_out[row];
                if (!std::isfinite(distance) || distance < 0.0) {
                    throw std::runtime_error(
                        "prepared OptiX nearest validation F64 distance is invalid");
                }
            }
        }
        rtdl_cuda_check(
            cudaDeviceSynchronize(),
            "synchronizing prepared OptiX nearest bounded projection");
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(
            error_out,
            error_capacity,
            "unknown prepared OptiX nearest continuation failure");
        return 1;
    }
}

static int rtdl_cuda_prepare_certified_nearest_grid_3d_impl(
        const double* target_coords,
        const int64_t* target_ids,
        uint64_t target_count,
        const int64_t* grid_shape,
        const double* grid_lower_bounds,
        const double* grid_upper_bounds,
        void** prepared_out,
        uint64_t* prepared_cell_count_out,
        double* prepare_total_seconds_out,
        char* error_out,
        uint64_t error_capacity,
        bool validate_target_id_domain)
{
    const auto total_start = std::chrono::steady_clock::now();
    try {
        if (prepared_out == nullptr) throw std::runtime_error("prepared_out must not be null");
        *prepared_out = nullptr;
        if (prepared_cell_count_out == nullptr) {
            throw std::runtime_error("prepared_cell_count_out must not be null");
        }
        *prepared_cell_count_out = 0;
        if (prepare_total_seconds_out == nullptr) {
            throw std::runtime_error("prepare_total_seconds_out must not be null");
        }
        *prepare_total_seconds_out = 0.0;
        if (target_count == 0) throw std::runtime_error("target_count must be positive");
        if (!target_coords || !target_ids || !grid_shape || !grid_lower_bounds || !grid_upper_bounds) {
            throw std::runtime_error("prepared nearest-grid input pointers must not be null");
        }
        const int64_t dim_x = grid_shape[0];
        const int64_t dim_y = grid_shape[1];
        const int64_t dim_z = grid_shape[2];
        if (dim_x <= 0 || dim_y <= 0 || dim_z <= 0) {
            throw std::runtime_error("prepared nearest-grid shape entries must be positive");
        }
        const uint64_t dense_count = static_cast<uint64_t>(dim_x)
            * static_cast<uint64_t>(dim_y) * static_cast<uint64_t>(dim_z);
        if (dense_count == 0 || dense_count > static_cast<uint64_t>(UINT32_MAX)) {
            throw std::runtime_error("prepared nearest-grid volume exceeds uint32 capacity");
        }
        if (target_count > static_cast<uint64_t>(UINT32_MAX)) {
            throw std::runtime_error("prepared nearest-grid target_count exceeds uint32 capacity");
        }
        if (validate_target_id_domain) {
            for (uint64_t index = 0; index < target_count; ++index) {
                if (target_ids[index] < 0
                        || static_cast<uint64_t>(target_ids[index]) > static_cast<uint64_t>(UINT32_MAX)) {
                    throw std::runtime_error("prepared nearest-grid target id exceeds uint32 domain");
                }
            }
        }

        auto* prepared = new RtdlCudaPreparedNearestGrid3D();
        try {
            prepared->dim_x = dim_x;
            prepared->dim_y = dim_y;
            prepared->dim_z = dim_z;
            prepared->lower_x = grid_lower_bounds[0];
            prepared->lower_y = grid_lower_bounds[1];
            prepared->lower_z = grid_lower_bounds[2];
            prepared->upper_x = grid_upper_bounds[0];
            prepared->upper_y = grid_upper_bounds[1];
            prepared->upper_z = grid_upper_bounds[2];
            prepared->target_count = target_count;
            prepared->dense_cell_position_count = dense_count;
            prepared->target_coords.resize(target_count * 3);
            prepared->target_ids.resize(target_count);
            rtdl_cuda_check(cudaMemcpy(
                thrust::raw_pointer_cast(prepared->target_coords.data()),
                target_coords,
                sizeof(double) * static_cast<size_t>(target_count) * 3,
                cudaMemcpyHostToDevice), "uploading prepared nearest target coordinates");
            rtdl_cuda_check(cudaMemcpy(
                thrust::raw_pointer_cast(prepared->target_ids.data()),
                target_ids,
                sizeof(int64_t) * static_cast<size_t>(target_count),
                cudaMemcpyHostToDevice), "uploading prepared nearest target ids");

            thrust::device_vector<int64_t> encoded(target_count);
            prepared->point_row_indices.resize(target_count);
            thrust::sequence(
                thrust::device,
                prepared->point_row_indices.begin(),
                prepared->point_row_indices.end(),
                int64_t{0});
            const unsigned block = 256;
            const unsigned grid = static_cast<unsigned>((target_count + block - 1) / block);
            rtdl_encode_point_grid_cells_3d_kernel<<<grid, block>>>(
                thrust::raw_pointer_cast(prepared->target_coords.data()),
                target_count,
                dim_x,
                dim_y,
                dim_z,
                prepared->lower_x,
                prepared->lower_y,
                prepared->lower_z,
                prepared->upper_x,
                prepared->upper_y,
                prepared->upper_z,
                thrust::raw_pointer_cast(encoded.data()));
            rtdl_cuda_check(cudaGetLastError(), "launching prepared nearest-grid encode kernel");

            // Stable deterministic point spans: encoded cell, target id, then
            // original row.  Keep the resident target-id column in input order;
            // the sorted copy is only a key and the span stores original rows.
            thrust::device_vector<int64_t> sorted_target_ids = prepared->target_ids;
            auto first = thrust::make_zip_iterator(thrust::make_tuple(
                encoded.begin(),
                sorted_target_ids.begin(),
                prepared->point_row_indices.begin()));
            thrust::sort(
                thrust::device,
                first,
                first + static_cast<ptrdiff_t>(target_count),
                RtdlCellPointIdCompare{});

            thrust::device_vector<int64_t> unique_cells(target_count);
            thrust::device_vector<int64_t> counts(target_count);
            auto reduce_end = thrust::reduce_by_key(
                thrust::device,
                encoded.begin(),
                encoded.end(),
                thrust::make_constant_iterator(int64_t{1}),
                unique_cells.begin(),
                counts.begin());
            const uint64_t cell_count = static_cast<uint64_t>(
                reduce_end.first - unique_cells.begin());
            if (cell_count == 0 || cell_count > static_cast<uint64_t>(UINT32_MAX)) {
                throw std::runtime_error("prepared nearest-grid cell_count is invalid");
            }
            prepared->cell_count = cell_count;
            prepared->cell_ids.resize(cell_count);
            prepared->original_cell_ids.resize(cell_count);
            prepared->point_begin_offsets.resize(cell_count);
            prepared->point_counts.resize(cell_count);
            thrust::sequence(
                thrust::device,
                prepared->cell_ids.begin(),
                prepared->cell_ids.end(),
                int64_t{0});
            thrust::copy(
                thrust::device,
                unique_cells.begin(),
                unique_cells.begin() + static_cast<ptrdiff_t>(cell_count),
                prepared->original_cell_ids.begin());
            thrust::copy(
                thrust::device,
                counts.begin(),
                counts.begin() + static_cast<ptrdiff_t>(cell_count),
                prepared->point_counts.begin());
            thrust::exclusive_scan(
                thrust::device,
                prepared->point_counts.begin(),
                prepared->point_counts.end(),
                prepared->point_begin_offsets.begin(),
                int64_t{0});

            prepared->dense_cell_positions.resize(dense_count);
            thrust::fill(
                thrust::device,
                prepared->dense_cell_positions.begin(),
                prepared->dense_cell_positions.end(),
                int64_t{-1});
            thrust::scatter(
                thrust::device,
                prepared->cell_ids.begin(),
                prepared->cell_ids.end(),
                prepared->original_cell_ids.begin(),
                prepared->dense_cell_positions.begin());
            rtdl_cuda_check(cudaDeviceSynchronize(), "synchronizing prepared nearest-grid construction");

            *prepared_out = prepared;
            *prepared_cell_count_out = cell_count;
            *prepare_total_seconds_out = std::chrono::duration<double>(
                std::chrono::steady_clock::now() - total_start).count();
        } catch (...) {
            delete prepared;
            throw;
        }
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(error_out, error_capacity, "unknown prepared nearest-grid failure");
        return 1;
    }
}

extern "C" int rtdl_cuda_prepare_certified_nearest_grid_3d(
        const double* target_coords,
        const int64_t* target_ids,
        uint64_t target_count,
        const int64_t* grid_shape,
        const double* grid_lower_bounds,
        const double* grid_upper_bounds,
        void** prepared_out,
        uint64_t* prepared_cell_count_out,
        double* prepare_total_seconds_out,
        char* error_out,
        uint64_t error_capacity)
{
    // Raw/public compatibility ABI: independently validate every logical ID.
    return rtdl_cuda_prepare_certified_nearest_grid_3d_impl(
        target_coords,
        target_ids,
        target_count,
        grid_shape,
        grid_lower_bounds,
        grid_upper_bounds,
        prepared_out,
        prepared_cell_count_out,
        prepare_total_seconds_out,
        error_out,
        error_capacity,
        true);
}

extern "C" int rtdl_cuda_prepare_certified_nearest_grid_3d_from_validated_columns(
        const double* target_coords,
        const int64_t* target_ids,
        uint64_t target_count,
        const int64_t* grid_shape,
        const double* grid_lower_bounds,
        const double* grid_upper_bounds,
        void** prepared_out,
        uint64_t* prepared_cell_count_out,
        double* prepare_total_seconds_out,
        char* error_out,
        uint64_t error_capacity)
{
    // Compiler-internal ABI: the exact immutable point/ID objects are already
    // bound to an ImmutablePointColumnDomain3DCertificate.  Shape/count/pointer
    // checks remain O(1); the raw ABI above retains the independent O(N) scan.
    return rtdl_cuda_prepare_certified_nearest_grid_3d_impl(
        target_coords,
        target_ids,
        target_count,
        grid_shape,
        grid_lower_bounds,
        grid_upper_bounds,
        prepared_out,
        prepared_cell_count_out,
        prepare_total_seconds_out,
        error_out,
        error_capacity,
        false);
}

extern "C" int rtdl_cuda_execute_prepared_certified_nearest_global_witness_3d(
        void* prepared_handle,
        const double* query_coords,
        const int64_t* query_ids,
        uint64_t query_count,
        const int64_t* validation_sample_indices,
        uint64_t validation_sample_count,
        int64_t* witness_source_id_out,
        int64_t* witness_item_id_out,
        double* witness_distance_out,
        int64_t* validation_item_ids_out,
        double* validation_distances_out,
        int64_t* candidate_distance_evaluations_out,
        int64_t* grid_cell_probes_out,
        int64_t* scanned_cell_count_out,
        double* upload_seconds_out,
        double* nearest_kernel_seconds_out,
        double* reducer_seconds_out,
        double* download_seconds_out,
        double* total_seconds_out,
        char* error_out,
        uint64_t error_capacity)
{
    const auto total_start = std::chrono::steady_clock::now();
    try {
        auto* prepared = static_cast<RtdlCudaPreparedNearestGrid3D*>(prepared_handle);
        if (prepared == nullptr) throw std::runtime_error("prepared nearest-grid handle is null");
        if (query_count == 0) throw std::runtime_error("query_count must be positive");
        if (query_count > static_cast<uint64_t>(UINT32_MAX)) {
            throw std::runtime_error("prepared nearest query_count exceeds uint32 capacity");
        }
        if (!query_coords || !query_ids || !witness_source_id_out || !witness_item_id_out
                || !witness_distance_out || !candidate_distance_evaluations_out
                || !grid_cell_probes_out || !scanned_cell_count_out || !upload_seconds_out
                || !nearest_kernel_seconds_out || !reducer_seconds_out
                || !download_seconds_out || !total_seconds_out) {
            throw std::runtime_error("prepared nearest execution pointers must not be null");
        }
        if (validation_sample_count != 0
                && (!validation_sample_indices || !validation_item_ids_out || !validation_distances_out)) {
            throw std::runtime_error("prepared nearest validation sample pointers must not be null");
        }
        *upload_seconds_out = 0.0;
        *nearest_kernel_seconds_out = 0.0;
        *reducer_seconds_out = 0.0;
        *download_seconds_out = 0.0;
        *total_seconds_out = 0.0;

        const auto upload_start = std::chrono::steady_clock::now();
        thrust::device_vector<double> d_query_coords(query_count * 3);
        thrust::device_vector<int64_t> d_query_ids(query_count);
        rtdl_cuda_check(cudaMemcpy(
            thrust::raw_pointer_cast(d_query_coords.data()),
            query_coords,
            sizeof(double) * static_cast<size_t>(query_count) * 3,
            cudaMemcpyHostToDevice), "uploading prepared nearest query coordinates");
        rtdl_cuda_check(cudaMemcpy(
            thrust::raw_pointer_cast(d_query_ids.data()),
            query_ids,
            sizeof(int64_t) * static_cast<size_t>(query_count),
            cudaMemcpyHostToDevice), "uploading prepared nearest query ids");
        *upload_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - upload_start).count();

        thrust::device_vector<double> d_distances(query_count);
        thrust::device_vector<int64_t> d_item_ids(query_count);
        thrust::device_vector<int64_t> d_seed_cell_ids(query_count);
        thrust::device_vector<int64_t> d_seed_counts(query_count);
        thrust::device_vector<int64_t> d_probe_counts(query_count);
        thrust::device_vector<int64_t> d_scanned_cell_counts(query_count);
        thrust::device_vector<int64_t> d_scanned_point_counts(query_count);
        thrust::device_vector<int64_t> d_shell_counts(query_count);

        const auto nearest_start = std::chrono::steady_clock::now();
        rtdl_cuda_grid_branch_bound_nearest_seed_3d_precompiled(
            thrust::raw_pointer_cast(d_query_coords.data()),
            thrust::raw_pointer_cast(d_query_ids.data()),
            static_cast<uint32_t>(query_count),
            thrust::raw_pointer_cast(prepared->target_coords.data()),
            thrust::raw_pointer_cast(prepared->target_ids.data()),
            static_cast<uint32_t>(prepared->target_count),
            thrust::raw_pointer_cast(prepared->cell_ids.data()),
            thrust::raw_pointer_cast(prepared->original_cell_ids.data()),
            thrust::raw_pointer_cast(prepared->dense_cell_positions.data()),
            static_cast<uint32_t>(prepared->dense_cell_position_count),
            thrust::raw_pointer_cast(prepared->point_begin_offsets.data()),
            thrust::raw_pointer_cast(prepared->point_counts.data()),
            thrust::raw_pointer_cast(prepared->point_row_indices.data()),
            static_cast<uint32_t>(prepared->target_count),
            static_cast<uint32_t>(prepared->cell_count),
            static_cast<int>(prepared->dim_x),
            static_cast<int>(prepared->dim_y),
            static_cast<int>(prepared->dim_z),
            prepared->lower_x,
            prepared->lower_y,
            prepared->lower_z,
            prepared->upper_x,
            prepared->upper_y,
            prepared->upper_z,
            thrust::raw_pointer_cast(d_distances.data()),
            thrust::raw_pointer_cast(d_item_ids.data()),
            thrust::raw_pointer_cast(d_seed_cell_ids.data()),
            thrust::raw_pointer_cast(d_seed_counts.data()),
            thrust::raw_pointer_cast(d_probe_counts.data()),
            thrust::raw_pointer_cast(d_scanned_cell_counts.data()),
            thrust::raw_pointer_cast(d_scanned_point_counts.data()),
            thrust::raw_pointer_cast(d_shell_counts.data()));
        *nearest_kernel_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - nearest_start).count();

        const auto reducer_start = std::chrono::steady_clock::now();
        auto first = thrust::make_zip_iterator(thrust::make_tuple(
            d_distances.begin(),
            thrust::make_counting_iterator(int64_t{0}),
            d_item_ids.begin()));
        auto last = first + static_cast<ptrdiff_t>(query_count);
        auto winner = thrust::max_element(
            thrust::device,
            first,
            last,
            RtdlNearestGlobalWitnessLess{});
        const ptrdiff_t winner_index = winner - first;
        const int64_t candidate_evaluations = thrust::reduce(
            thrust::device,
            d_scanned_point_counts.begin(),
            d_scanned_point_counts.end(),
            int64_t{0});
        const int64_t grid_probes = thrust::reduce(
            thrust::device,
            d_probe_counts.begin(),
            d_probe_counts.end(),
            int64_t{0});
        const int64_t scanned_cells = thrust::reduce(
            thrust::device,
            d_scanned_cell_counts.begin(),
            d_scanned_cell_counts.end(),
            int64_t{0});
        *reducer_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - reducer_start).count();

        const auto download_start = std::chrono::steady_clock::now();
        rtdl_cuda_check(cudaMemcpy(
            witness_source_id_out,
            thrust::raw_pointer_cast(d_query_ids.data()) + winner_index,
            sizeof(int64_t),
            cudaMemcpyDeviceToHost), "downloading prepared nearest witness source id");
        rtdl_cuda_check(cudaMemcpy(
            witness_item_id_out,
            thrust::raw_pointer_cast(d_item_ids.data()) + winner_index,
            sizeof(int64_t),
            cudaMemcpyDeviceToHost), "downloading prepared nearest witness item id");
        rtdl_cuda_check(cudaMemcpy(
            witness_distance_out,
            thrust::raw_pointer_cast(d_distances.data()) + winner_index,
            sizeof(double),
            cudaMemcpyDeviceToHost), "downloading prepared nearest witness distance");
        if (validation_sample_count != 0) {
            thrust::device_vector<int64_t> d_sample_indices(validation_sample_count);
            rtdl_cuda_check(cudaMemcpy(
                thrust::raw_pointer_cast(d_sample_indices.data()),
                validation_sample_indices,
                sizeof(int64_t) * static_cast<size_t>(validation_sample_count),
                cudaMemcpyHostToDevice), "uploading prepared nearest validation sample indices");
            thrust::device_vector<int64_t> d_sample_item_ids(validation_sample_count);
            thrust::device_vector<double> d_sample_distances(validation_sample_count);
            thrust::gather(
                thrust::device,
                d_sample_indices.begin(),
                d_sample_indices.end(),
                d_item_ids.begin(),
                d_sample_item_ids.begin());
            thrust::gather(
                thrust::device,
                d_sample_indices.begin(),
                d_sample_indices.end(),
                d_distances.begin(),
                d_sample_distances.begin());
            rtdl_cuda_check(cudaMemcpy(
                validation_item_ids_out,
                thrust::raw_pointer_cast(d_sample_item_ids.data()),
                sizeof(int64_t) * static_cast<size_t>(validation_sample_count),
                cudaMemcpyDeviceToHost), "downloading prepared nearest validation item ids");
            rtdl_cuda_check(cudaMemcpy(
                validation_distances_out,
                thrust::raw_pointer_cast(d_sample_distances.data()),
                sizeof(double) * static_cast<size_t>(validation_sample_count),
                cudaMemcpyDeviceToHost), "downloading prepared nearest validation distances");
        }
        *candidate_distance_evaluations_out = candidate_evaluations;
        *grid_cell_probes_out = grid_probes;
        *scanned_cell_count_out = scanned_cells;
        rtdl_cuda_check(cudaDeviceSynchronize(), "synchronizing prepared nearest bounded projection");
        *download_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - download_start).count();
        *total_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - total_start).count();
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(error_out, error_capacity, "unknown prepared nearest execution failure");
        return 1;
    }
}

extern "C" int rtdl_cuda_execute_prepared_exact_bounded_selection_3d(
        void* prepared_handle,
        const double* query_coords,
        uint64_t query_count,
        double minimum_distance,
        double maximum_distance,
        uint32_t limit,
        uint32_t minimum_boundary_mode,
        uint32_t maximum_boundary_mode,
        uint32_t* counts_out,
        int64_t* item_ids_out,
        double* distances_out,
        int64_t* candidate_distance_evaluations_out,
        int64_t* grid_cell_probes_out,
        int64_t* scanned_cell_count_out,
        double* upload_seconds_out,
        double* selection_kernel_seconds_out,
        double* download_seconds_out,
        double* total_seconds_out,
        char* error_out,
        uint64_t error_capacity)
{
    const auto total_start = std::chrono::steady_clock::now();
    try {
        auto* prepared =
            static_cast<RtdlCudaPreparedNearestGrid3D*>(prepared_handle);
        if (prepared == nullptr) {
            throw std::runtime_error("prepared bounded-selection grid handle is null");
        }
        if (query_count == 0
                || query_count > static_cast<uint64_t>(UINT32_MAX)) {
            throw std::runtime_error(
                "prepared bounded-selection query_count must be positive and fit uint32");
        }
        if (!query_coords || !counts_out || !item_ids_out || !distances_out
                || !candidate_distance_evaluations_out || !grid_cell_probes_out
                || !scanned_cell_count_out || !upload_seconds_out
                || !selection_kernel_seconds_out || !download_seconds_out
                || !total_seconds_out) {
            throw std::runtime_error(
                "prepared bounded-selection execution pointers must not be null");
        }
        if (!std::isfinite(minimum_distance) || minimum_distance < 0.0
                || !std::isfinite(maximum_distance)
                || maximum_distance < minimum_distance) {
            throw std::runtime_error(
                "prepared bounded-selection distance window is invalid");
        }
        if (limit == 0u || limit > 64u) {
            throw std::runtime_error(
                "prepared bounded-selection limit must be in [1,64]");
        }
        if (minimum_boundary_mode > 1u || maximum_boundary_mode > 1u) {
            throw std::runtime_error(
                "prepared bounded-selection boundary modes are invalid");
        }
        if (query_count > (std::numeric_limits<size_t>::max)()
                / static_cast<size_t>(limit)) {
            throw std::runtime_error(
                "prepared bounded-selection output capacity overflows size_t");
        }
        *upload_seconds_out = 0.0;
        *selection_kernel_seconds_out = 0.0;
        *download_seconds_out = 0.0;
        *total_seconds_out = 0.0;

        const size_t row_capacity =
            static_cast<size_t>(query_count) * static_cast<size_t>(limit);
        const auto upload_start = std::chrono::steady_clock::now();
        thrust::device_vector<double> d_query_coords(query_count * 3);
        rtdl_cuda_check(cudaMemcpy(
            thrust::raw_pointer_cast(d_query_coords.data()),
            query_coords,
            sizeof(double) * static_cast<size_t>(query_count) * 3,
            cudaMemcpyHostToDevice),
            "uploading prepared bounded-selection query coordinates");
        thrust::device_vector<uint32_t> d_counts(query_count);
        thrust::device_vector<int64_t> d_item_ids(row_capacity, int64_t{-1});
        thrust::device_vector<double> d_distances(row_capacity, INFINITY);
        thrust::device_vector<int64_t> d_candidate_evaluations(query_count);
        thrust::device_vector<int64_t> d_grid_probes(query_count);
        thrust::device_vector<int64_t> d_scanned_cells(query_count);
        *upload_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - upload_start).count();

        const auto kernel_start = std::chrono::steady_clock::now();
        const unsigned block = 256u;
        const unsigned grid = static_cast<unsigned>(
            (query_count + block - 1u) / block);
        rtdl_grid_branch_bound_exact_bounded_topk_3d_kernel<<<grid, block>>>(
            thrust::raw_pointer_cast(d_query_coords.data()),
            static_cast<uint32_t>(query_count),
            thrust::raw_pointer_cast(prepared->target_coords.data()),
            thrust::raw_pointer_cast(prepared->target_ids.data()),
            static_cast<uint32_t>(prepared->target_count),
            thrust::raw_pointer_cast(prepared->dense_cell_positions.data()),
            static_cast<uint32_t>(prepared->dense_cell_position_count),
            thrust::raw_pointer_cast(prepared->point_begin_offsets.data()),
            thrust::raw_pointer_cast(prepared->point_counts.data()),
            thrust::raw_pointer_cast(prepared->point_row_indices.data()),
            static_cast<uint32_t>(prepared->target_count),
            static_cast<uint32_t>(prepared->cell_count),
            static_cast<int>(prepared->dim_x),
            static_cast<int>(prepared->dim_y),
            static_cast<int>(prepared->dim_z),
            prepared->lower_x,
            prepared->lower_y,
            prepared->lower_z,
            prepared->upper_x,
            prepared->upper_y,
            prepared->upper_z,
            minimum_distance,
            maximum_distance,
            limit,
            minimum_boundary_mode,
            maximum_boundary_mode,
            thrust::raw_pointer_cast(d_counts.data()),
            thrust::raw_pointer_cast(d_item_ids.data()),
            thrust::raw_pointer_cast(d_distances.data()),
            thrust::raw_pointer_cast(d_candidate_evaluations.data()),
            thrust::raw_pointer_cast(d_grid_probes.data()),
            thrust::raw_pointer_cast(d_scanned_cells.data()));
        rtdl_cuda_check(
            cudaGetLastError(),
            "launching exact bounded-selection branch-bound kernel");
        rtdl_cuda_check(
            cudaDeviceSynchronize(),
            "synchronizing exact bounded-selection branch-bound kernel");
        *selection_kernel_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - kernel_start).count();

        const int64_t candidate_evaluations = thrust::reduce(
            thrust::device,
            d_candidate_evaluations.begin(),
            d_candidate_evaluations.end(),
            int64_t{0});
        const int64_t grid_probes = thrust::reduce(
            thrust::device,
            d_grid_probes.begin(),
            d_grid_probes.end(),
            int64_t{0});
        const int64_t scanned_cells = thrust::reduce(
            thrust::device,
            d_scanned_cells.begin(),
            d_scanned_cells.end(),
            int64_t{0});

        const auto download_start = std::chrono::steady_clock::now();
        rtdl_cuda_check(cudaMemcpy(
            counts_out,
            thrust::raw_pointer_cast(d_counts.data()),
            sizeof(uint32_t) * static_cast<size_t>(query_count),
            cudaMemcpyDeviceToHost),
            "downloading exact bounded-selection counts");
        rtdl_cuda_check(cudaMemcpy(
            item_ids_out,
            thrust::raw_pointer_cast(d_item_ids.data()),
            sizeof(int64_t) * row_capacity,
            cudaMemcpyDeviceToHost),
            "downloading exact bounded-selection item ids");
        rtdl_cuda_check(cudaMemcpy(
            distances_out,
            thrust::raw_pointer_cast(d_distances.data()),
            sizeof(double) * row_capacity,
            cudaMemcpyDeviceToHost),
            "downloading exact bounded-selection distances");
        *candidate_distance_evaluations_out = candidate_evaluations;
        *grid_cell_probes_out = grid_probes;
        *scanned_cell_count_out = scanned_cells;
        *download_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - download_start).count();
        *total_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - total_start).count();
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(
            error_out,
            error_capacity,
            "unknown prepared exact bounded-selection execution failure");
        return 1;
    }
}

extern "C" int rtdl_cuda_close_prepared_certified_nearest_grid_3d(
        void* prepared_handle,
        char* error_out,
        uint64_t error_capacity)
{
    try {
        auto* prepared = static_cast<RtdlCudaPreparedNearestGrid3D*>(prepared_handle);
        if (prepared == nullptr) throw std::runtime_error("prepared nearest-grid handle is null");
        rtdl_cuda_check(cudaDeviceSynchronize(), "synchronizing prepared nearest-grid close");
        delete prepared;
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(error_out, error_capacity, "unknown prepared nearest-grid close failure");
        return 1;
    }
}

struct RtdlLexsortI64F64I64I64Compare {
    using Tuple = thrust::tuple<int64_t, double, int64_t, int64_t>;

    __host__ __device__ bool operator()(const Tuple& a, const Tuple& b) const
    {
        const int64_t edge_a = thrust::get<0>(a);
        const int64_t edge_b = thrust::get<0>(b);
        if (edge_a != edge_b) return edge_a < edge_b;
        const double dist_a = thrust::get<1>(a);
        const double dist_b = thrust::get<1>(b);
        if (dist_a != dist_b) return dist_a < dist_b;
        const int64_t tie_a = thrust::get<2>(a);
        const int64_t tie_b = thrust::get<2>(b);
        if (tie_a != tie_b) return tie_a < tie_b;
        return thrust::get<3>(a) < thrust::get<3>(b);
    }
};

extern "C" int rtdl_cuda_sort_i64_f64_i64_i64_lex(
        uint64_t edge_key_device_ptr,
        uint64_t dist_key_device_ptr,
        uint64_t tie_key_device_ptr,
        uint64_t order_key_device_ptr,
        uint64_t count,
        char* error_out,
        uint64_t error_capacity)
{
    try {
        if (count == 0) return 0;
        auto* edge = reinterpret_cast<int64_t*>(static_cast<uintptr_t>(edge_key_device_ptr));
        auto* dist = reinterpret_cast<double*>(static_cast<uintptr_t>(dist_key_device_ptr));
        auto* tie = reinterpret_cast<int64_t*>(static_cast<uintptr_t>(tie_key_device_ptr));
        auto* order = reinterpret_cast<int64_t*>(static_cast<uintptr_t>(order_key_device_ptr));
        if (edge == nullptr || dist == nullptr || tie == nullptr || order == nullptr) {
            throw std::runtime_error("lexsort received a null device pointer");
        }

        auto first = thrust::make_zip_iterator(thrust::make_tuple(
            thrust::device_pointer_cast(edge),
            thrust::device_pointer_cast(dist),
            thrust::device_pointer_cast(tie),
            thrust::device_pointer_cast(order)));
        thrust::sort(thrust::device, first, first + static_cast<ptrdiff_t>(count),
            RtdlLexsortI64F64I64I64Compare{});
        rtdl_cuda_check(cudaDeviceSynchronize(), "synchronizing i64/f64/i64/i64 lexsort");
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(error_out, error_capacity, "unknown lexsort failure");
        return 1;
    }
}

// Generic prepared 3-D aggregate-hierarchy continuation executor.
//
// This ABI deliberately consumes only the public aggregate-hierarchy columns
// and two closed enum codes.  It contains no application, paper, force, or
// workload identity.  The same kernel implements aggregate-count and
// inverse-square scalar reducers.
struct RtdlCudaPreparedAggregateHierarchy3D {
    uint64_t point_count;
    uint64_t node_count;
    uint64_t member_count;
    int64_t root_node_index;
    thrust::device_vector<double> point_x;
    thrust::device_vector<double> point_y;
    thrust::device_vector<double> point_z;
    thrust::device_vector<double> point_weight;
    thrust::device_vector<double> node_cx;
    thrust::device_vector<double> node_cy;
    thrust::device_vector<double> node_cz;
    thrust::device_vector<double> node_half_size;
    thrust::device_vector<double> node_weight;
    thrust::device_vector<int64_t> member_offsets;
    thrust::device_vector<int64_t> member_indices;
    thrust::device_vector<int64_t> child_offsets;
    thrust::device_vector<int64_t> node_next_index;
    thrust::device_vector<int64_t> node_rope_index;
    thrust::device_vector<double> reducer_value_0;
    thrust::device_vector<int64_t> visited_node_count;
    thrust::device_vector<int64_t> aggregate_contribution_count;
    thrust::device_vector<int64_t> exact_contribution_count;
    thrust::device_vector<int64_t> status_code;
};

static __global__ void rtdl_aggregate_hierarchy_continuation_reduce_3d_kernel(
        const double* point_x,
        const double* point_y,
        const double* point_z,
        const double* point_weight,
        uint64_t point_count,
        const double* node_cx,
        const double* node_cy,
        const double* node_cz,
        const double* node_half_size,
        const double* node_weight,
        const int64_t* member_offsets,
        const int64_t* member_indices,
        const int64_t* child_offsets,
        const int64_t* node_next_index,
        const int64_t* node_rope_index,
        uint64_t node_count,
        int64_t root_node_index,
        uint32_t reducer_kind,
        double max_ratio,
        double softening,
        double* reducer_value_0_out,
        int64_t* visited_node_count_out,
        int64_t* aggregate_contribution_count_out,
        int64_t* exact_contribution_count_out,
        int64_t* status_code_out)
{
    const uint64_t source_index =
        static_cast<uint64_t>(blockIdx.x) * blockDim.x + threadIdx.x;
    if (source_index >= point_count) return;

    double reducer_value = 0.0;
    int64_t visited_count = 0;
    int64_t aggregate_count = 0;
    int64_t exact_count = 0;
    int64_t status = 0;
    int64_t node_index = root_node_index;
    int ray_self = 0;
    const double softening_sq = softening * softening;
    uint64_t step_count = 0;
    const uint64_t step_limit = node_count * 2u + 1u;

    while (node_index >= 0) {
        if (static_cast<uint64_t>(node_index) >= node_count) {
            status = 2;
            break;
        }
        if (++step_count > step_limit) {
            status = 3;
            break;
        }
        ++visited_count;
        const int64_t child_begin = child_offsets[node_index];
        const int64_t child_end = child_offsets[node_index + 1];
        const bool is_leaf = child_begin == child_end;
        const double dx = point_x[source_index] - node_cx[node_index];
        const double dy = point_y[source_index] - node_cy[node_index];
        const double dz = point_z[source_index] - node_cz[node_index];
        const double raw_distance_sq = dx * dx + dy * dy + dz * dz;
        const double distance_sq = raw_distance_sq + softening_sq;
        const double ray_length = sqrt(raw_distance_sq) * max_ratio;
        const bool hit_current_node = node_half_size[node_index] < ray_length;

        if (hit_current_node) {
            if (is_leaf) {
                const int64_t member_begin = member_offsets[node_index];
                const int64_t member_end = member_offsets[node_index + 1];
                for (int64_t offset = member_begin; offset < member_end; ++offset) {
                    const int64_t point_index = member_indices[offset];
                    if (point_index == static_cast<int64_t>(source_index)) continue;
                    if (reducer_kind == 0u) {
                        reducer_value += 1.0;
                    } else {
                        const double ex = point_x[point_index] - point_x[source_index];
                        const double ey = point_y[point_index] - point_y[source_index];
                        const double ez = point_z[point_index] - point_z[source_index];
                        const double exact_distance_sq =
                            ex * ex + ey * ey + ez * ez + softening_sq;
                        if (exact_distance_sq > 0.0) {
                            reducer_value +=
                                point_weight[source_index] * point_weight[point_index]
                                / exact_distance_sq;
                        }
                    }
                    ++exact_count;
                }
            } else if (distance_sq > 0.0) {
                if (reducer_kind == 0u) {
                    reducer_value += 1.0;
                } else {
                    reducer_value +=
                        point_weight[source_index] * node_weight[node_index]
                        / distance_sq;
                }
                ++aggregate_count;
            }
            node_index = node_rope_index[node_index];
        } else {
            if (is_leaf && ray_self == 0) {
                const int64_t member_begin = member_offsets[node_index];
                const int64_t member_end = member_offsets[node_index + 1];
                for (int64_t offset = member_begin; offset < member_end; ++offset) {
                    const int64_t point_index = member_indices[offset];
                    if (point_index == static_cast<int64_t>(source_index)) continue;
                    if (reducer_kind == 0u) {
                        reducer_value += 1.0;
                    } else {
                        const double ex = point_x[point_index] - point_x[source_index];
                        const double ey = point_y[point_index] - point_y[source_index];
                        const double ez = point_z[point_index] - point_z[source_index];
                        const double exact_distance_sq =
                            ex * ex + ey * ey + ez * ez + softening_sq;
                        if (exact_distance_sq > 0.0) {
                            reducer_value +=
                                point_weight[source_index] * point_weight[point_index]
                                / exact_distance_sq;
                        }
                    }
                    ++exact_count;
                }
            }
            node_index = node_next_index[node_index];
        }

        if (node_index < 0) break;
        if (static_cast<uint64_t>(node_index) >= node_count) {
            status = 2;
            break;
        }
        const double next_dx = point_x[source_index] - node_cx[node_index];
        const double next_dy = point_y[source_index] - node_cy[node_index];
        const double next_dz = point_z[source_index] - node_cz[node_index];
        const double next_ray_length =
            sqrt(next_dx * next_dx + next_dy * next_dy + next_dz * next_dz)
            * max_ratio;
        ray_self = next_ray_length == 0.0 ? 1 : 0;
    }

    reducer_value_0_out[source_index] = reducer_value;
    visited_node_count_out[source_index] = visited_count;
    aggregate_contribution_count_out[source_index] = aggregate_count;
    exact_contribution_count_out[source_index] = exact_count;
    status_code_out[source_index] = status;
}

extern "C" int rtdl_cuda_prepare_aggregate_hierarchy_continuation_3d(
        const double* point_x,
        const double* point_y,
        const double* point_z,
        const double* point_weight,
        uint64_t point_count,
        const double* node_cx,
        const double* node_cy,
        const double* node_cz,
        const double* node_half_size,
        const double* node_weight,
        uint64_t node_count,
        const int64_t* member_offsets,
        const int64_t* member_indices,
        uint64_t member_count,
        const int64_t* child_offsets,
        const int64_t* child_indices,
        uint64_t child_count,
        const int64_t* node_next_index,
        const int64_t* node_rope_index,
        int64_t root_node_index,
        void** prepared_out,
        double* prepare_total_seconds_out,
        char* error_out,
        uint64_t error_capacity)
{
    const auto total_start = std::chrono::steady_clock::now();
    try {
        if (prepared_out == nullptr || prepare_total_seconds_out == nullptr) {
            throw std::runtime_error("aggregate hierarchy prepare output pointers must not be null");
        }
        *prepared_out = nullptr;
        *prepare_total_seconds_out = 0.0;
        if (point_count == 0 || node_count == 0) {
            throw std::runtime_error("aggregate hierarchy point_count and node_count must be positive");
        }
        if (point_count > static_cast<uint64_t>(UINT32_MAX)
                || node_count > static_cast<uint64_t>(INT64_MAX)
                || member_count > static_cast<uint64_t>(INT64_MAX)
                || child_count > static_cast<uint64_t>(INT64_MAX)) {
            throw std::runtime_error("aggregate hierarchy dimensions exceed native ABI capacity");
        }
        if (!point_x || !point_y || !point_z || !point_weight
                || !node_cx || !node_cy || !node_cz || !node_half_size || !node_weight
                || !member_offsets || !child_offsets || !node_next_index || !node_rope_index
                || (member_count > 0 && !member_indices)
                || (child_count > 0 && !child_indices)) {
            throw std::runtime_error("aggregate hierarchy prepare input pointers must not be null");
        }
        if (root_node_index < 0 || static_cast<uint64_t>(root_node_index) >= node_count) {
            throw std::runtime_error("aggregate hierarchy root_node_index is outside node domain");
        }
        if (member_offsets[0] != 0
                || member_offsets[node_count] != static_cast<int64_t>(member_count)
                || child_offsets[0] != 0
                || child_offsets[node_count] != static_cast<int64_t>(child_count)) {
            throw std::runtime_error("aggregate hierarchy offset boundary is invalid");
        }
        for (uint64_t index = 0; index < point_count; ++index) {
            if (!std::isfinite(point_x[index]) || !std::isfinite(point_y[index])
                    || !std::isfinite(point_z[index]) || !std::isfinite(point_weight[index])
                    || point_weight[index] < 0.0) {
                throw std::runtime_error("aggregate hierarchy point column contains an invalid value");
            }
        }
        int64_t previous_member_offset = 0;
        int64_t previous_child_offset = 0;
        for (uint64_t index = 0; index < node_count; ++index) {
            if (!std::isfinite(node_cx[index]) || !std::isfinite(node_cy[index])
                    || !std::isfinite(node_cz[index]) || !std::isfinite(node_half_size[index])
                    || !std::isfinite(node_weight[index]) || node_half_size[index] < 0.0
                    || node_weight[index] < 0.0) {
                throw std::runtime_error("aggregate hierarchy node column contains an invalid value");
            }
            const int64_t member_offset = member_offsets[index + 1];
            const int64_t child_offset = child_offsets[index + 1];
            if (member_offset < previous_member_offset
                    || member_offset > static_cast<int64_t>(member_count)
                    || child_offset < previous_child_offset
                    || child_offset > static_cast<int64_t>(child_count)) {
                throw std::runtime_error("aggregate hierarchy offsets are not monotonic");
            }
            previous_member_offset = member_offset;
            previous_child_offset = child_offset;
            const int64_t next = node_next_index[index];
            const int64_t rope = node_rope_index[index];
            if (next < -1 || (next >= 0 && static_cast<uint64_t>(next) >= node_count)
                    || rope < -1 || (rope >= 0 && static_cast<uint64_t>(rope) >= node_count)) {
                throw std::runtime_error("aggregate hierarchy continuation index is outside node domain");
            }
        }
        for (uint64_t index = 0; index < member_count; ++index) {
            const int64_t point_index = member_indices[index];
            if (point_index < 0 || static_cast<uint64_t>(point_index) >= point_count) {
                throw std::runtime_error("aggregate hierarchy member index is outside point domain");
            }
        }
        for (uint64_t index = 0; index < child_count; ++index) {
            const int64_t child_index = child_indices[index];
            if (child_index < 0 || static_cast<uint64_t>(child_index) >= node_count) {
                throw std::runtime_error("aggregate hierarchy child index is outside node domain");
            }
        }

        auto* prepared = new RtdlCudaPreparedAggregateHierarchy3D();
        try {
            prepared->point_count = point_count;
            prepared->node_count = node_count;
            prepared->member_count = member_count;
            prepared->root_node_index = root_node_index;
            prepared->point_x.assign(point_x, point_x + point_count);
            prepared->point_y.assign(point_y, point_y + point_count);
            prepared->point_z.assign(point_z, point_z + point_count);
            prepared->point_weight.assign(point_weight, point_weight + point_count);
            prepared->node_cx.assign(node_cx, node_cx + node_count);
            prepared->node_cy.assign(node_cy, node_cy + node_count);
            prepared->node_cz.assign(node_cz, node_cz + node_count);
            prepared->node_half_size.assign(node_half_size, node_half_size + node_count);
            prepared->node_weight.assign(node_weight, node_weight + node_count);
            prepared->member_offsets.assign(member_offsets, member_offsets + node_count + 1);
            if (member_count > 0) {
                prepared->member_indices.assign(member_indices, member_indices + member_count);
            }
            prepared->child_offsets.assign(child_offsets, child_offsets + node_count + 1);
            prepared->node_next_index.assign(node_next_index, node_next_index + node_count);
            prepared->node_rope_index.assign(node_rope_index, node_rope_index + node_count);
            prepared->reducer_value_0.resize(point_count);
            prepared->visited_node_count.resize(point_count);
            prepared->aggregate_contribution_count.resize(point_count);
            prepared->exact_contribution_count.resize(point_count);
            prepared->status_code.resize(point_count);
            rtdl_cuda_check(
                cudaDeviceSynchronize(),
                "synchronizing aggregate hierarchy prepare");
            *prepared_out = prepared;
            *prepare_total_seconds_out = std::chrono::duration<double>(
                std::chrono::steady_clock::now() - total_start).count();
        } catch (...) {
            delete prepared;
            throw;
        }
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(
            error_out,
            error_capacity,
            "unknown aggregate hierarchy prepare failure");
        return 1;
    }
}

extern "C" int rtdl_cuda_execute_prepared_aggregate_hierarchy_continuation_3d(
        void* prepared_handle,
        uint32_t reducer_kind,
        double max_ratio,
        double softening,
        uint64_t output_capacity,
        double* reducer_value_0_out,
        int64_t* visited_node_count_out,
        int64_t* aggregate_contribution_count_out,
        int64_t* exact_contribution_count_out,
        int64_t* status_code_out,
        double* kernel_seconds_out,
        double* download_seconds_out,
        double* total_seconds_out,
        char* error_out,
        uint64_t error_capacity)
{
    const auto total_start = std::chrono::steady_clock::now();
    try {
        auto* prepared = static_cast<RtdlCudaPreparedAggregateHierarchy3D*>(prepared_handle);
        if (prepared == nullptr) {
            throw std::runtime_error("prepared aggregate hierarchy handle is null");
        }
        if (reducer_kind > 1u) {
            throw std::runtime_error("aggregate hierarchy reducer kind is unsupported");
        }
        if (!std::isfinite(max_ratio) || max_ratio <= 0.0
                || !std::isfinite(softening) || softening < 0.0) {
            throw std::runtime_error("aggregate hierarchy execution parameters are invalid");
        }
        if (output_capacity < prepared->point_count) {
            throw std::runtime_error(
                "aggregate hierarchy output capacity would truncate complete output");
        }
        if (!reducer_value_0_out || !visited_node_count_out
                || !aggregate_contribution_count_out || !exact_contribution_count_out
                || !status_code_out || !kernel_seconds_out || !download_seconds_out
                || !total_seconds_out) {
            throw std::runtime_error("aggregate hierarchy execution output pointers must not be null");
        }
        *kernel_seconds_out = 0.0;
        *download_seconds_out = 0.0;
        *total_seconds_out = 0.0;

        const auto kernel_start = std::chrono::steady_clock::now();
        const unsigned block = 256;
        const unsigned grid = static_cast<unsigned>(
            (prepared->point_count + block - 1u) / block);
        rtdl_aggregate_hierarchy_continuation_reduce_3d_kernel<<<grid, block>>>(
            thrust::raw_pointer_cast(prepared->point_x.data()),
            thrust::raw_pointer_cast(prepared->point_y.data()),
            thrust::raw_pointer_cast(prepared->point_z.data()),
            thrust::raw_pointer_cast(prepared->point_weight.data()),
            prepared->point_count,
            thrust::raw_pointer_cast(prepared->node_cx.data()),
            thrust::raw_pointer_cast(prepared->node_cy.data()),
            thrust::raw_pointer_cast(prepared->node_cz.data()),
            thrust::raw_pointer_cast(prepared->node_half_size.data()),
            thrust::raw_pointer_cast(prepared->node_weight.data()),
            thrust::raw_pointer_cast(prepared->member_offsets.data()),
            thrust::raw_pointer_cast(prepared->member_indices.data()),
            thrust::raw_pointer_cast(prepared->child_offsets.data()),
            thrust::raw_pointer_cast(prepared->node_next_index.data()),
            thrust::raw_pointer_cast(prepared->node_rope_index.data()),
            prepared->node_count,
            prepared->root_node_index,
            reducer_kind,
            max_ratio,
            softening,
            thrust::raw_pointer_cast(prepared->reducer_value_0.data()),
            thrust::raw_pointer_cast(prepared->visited_node_count.data()),
            thrust::raw_pointer_cast(prepared->aggregate_contribution_count.data()),
            thrust::raw_pointer_cast(prepared->exact_contribution_count.data()),
            thrust::raw_pointer_cast(prepared->status_code.data()));
        rtdl_cuda_check(
            cudaGetLastError(),
            "launching aggregate hierarchy continuation reduce kernel");
        rtdl_cuda_check(
            cudaDeviceSynchronize(),
            "synchronizing aggregate hierarchy continuation reduce kernel");
        *kernel_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - kernel_start).count();

        const auto download_start = std::chrono::steady_clock::now();
        const size_t double_bytes =
            sizeof(double) * static_cast<size_t>(prepared->point_count);
        const size_t int64_bytes =
            sizeof(int64_t) * static_cast<size_t>(prepared->point_count);
        rtdl_cuda_check(cudaMemcpy(
            reducer_value_0_out,
            thrust::raw_pointer_cast(prepared->reducer_value_0.data()),
            double_bytes,
            cudaMemcpyDeviceToHost), "downloading aggregate hierarchy reducer values");
        rtdl_cuda_check(cudaMemcpy(
            visited_node_count_out,
            thrust::raw_pointer_cast(prepared->visited_node_count.data()),
            int64_bytes,
            cudaMemcpyDeviceToHost), "downloading aggregate hierarchy visited counts");
        rtdl_cuda_check(cudaMemcpy(
            aggregate_contribution_count_out,
            thrust::raw_pointer_cast(prepared->aggregate_contribution_count.data()),
            int64_bytes,
            cudaMemcpyDeviceToHost), "downloading aggregate hierarchy aggregate counts");
        rtdl_cuda_check(cudaMemcpy(
            exact_contribution_count_out,
            thrust::raw_pointer_cast(prepared->exact_contribution_count.data()),
            int64_bytes,
            cudaMemcpyDeviceToHost), "downloading aggregate hierarchy exact counts");
        rtdl_cuda_check(cudaMemcpy(
            status_code_out,
            thrust::raw_pointer_cast(prepared->status_code.data()),
            int64_bytes,
            cudaMemcpyDeviceToHost), "downloading aggregate hierarchy status codes");
        *download_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - download_start).count();
        *total_seconds_out = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - total_start).count();
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(
            error_out,
            error_capacity,
            "unknown prepared aggregate hierarchy execution failure");
        return 1;
    }
}

extern "C" int rtdl_cuda_close_prepared_aggregate_hierarchy_continuation_3d(
        void* prepared_handle,
        char* error_out,
        uint64_t error_capacity)
{
    try {
        auto* prepared = static_cast<RtdlCudaPreparedAggregateHierarchy3D*>(prepared_handle);
        if (prepared == nullptr) {
            throw std::runtime_error("prepared aggregate hierarchy handle is null");
        }
        rtdl_cuda_check(
            cudaDeviceSynchronize(),
            "synchronizing prepared aggregate hierarchy close");
        delete prepared;
        return 0;
    } catch (const std::exception& exc) {
        rtdl_cuda_write_error(error_out, error_capacity, exc.what());
        return 1;
    } catch (...) {
        rtdl_cuda_write_error(
            error_out,
            error_capacity,
            "unknown prepared aggregate hierarchy close failure");
        return 1;
    }
}
