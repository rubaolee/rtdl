#include <cuda_runtime.h>

#include <cmath>
#include <cstdint>
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
