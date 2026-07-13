#include <cuda_runtime.h>
#include <thrust/device_ptr.h>
#include <thrust/device_vector.h>
#include <thrust/execution_policy.h>
#include <thrust/extrema.h>
#include <thrust/functional.h>
#include <thrust/gather.h>
#include <thrust/iterator/zip_iterator.h>
#include <thrust/iterator/constant_iterator.h>
#include <thrust/iterator/counting_iterator.h>
#include <thrust/reduce.h>
#include <thrust/scan.h>
#include <thrust/sequence.h>
#include <thrust/sort.h>
#include <thrust/tuple.h>

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
