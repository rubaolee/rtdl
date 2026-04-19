#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <exception>
#include <new>
#include <vector>

#if defined(_WIN32)
#define RTDL_ADAPTIVE_EXPORT __declspec(dllexport)
#else
#define RTDL_ADAPTIVE_EXPORT __attribute__((visibility("default")))
#endif

extern "C" {

struct RtdlAdaptiveRay3D {
  uint32_t id;
  double ox;
  double oy;
  double oz;
  double dx;
  double dy;
  double dz;
  double tmax;
};

struct RtdlAdaptiveTriangle3D {
  uint32_t id;
  double x0;
  double y0;
  double z0;
  double x1;
  double y1;
  double z1;
  double x2;
  double y2;
  double z2;
};

struct RtdlAdaptiveRayHitCountRow {
  uint32_t ray_id;
  uint32_t hit_count;
};

RTDL_ADAPTIVE_EXPORT void rtdl_adaptive_free_rows(void* pointer) {
  std::free(pointer);
}

RTDL_ADAPTIVE_EXPORT int rtdl_adaptive_get_version(int* major_out, int* minor_out, int* patch_out) {
  if (major_out == nullptr || minor_out == nullptr || patch_out == nullptr) {
    return 1;
  }
  *major_out = 0;
  *minor_out = 1;
  *patch_out = 0;
  return 0;
}

RTDL_ADAPTIVE_EXPORT int rtdl_adaptive_run_ray_hitcount_3d(
    const RtdlAdaptiveRay3D* rays,
    size_t ray_count,
    const RtdlAdaptiveTriangle3D* triangles,
    size_t triangle_count,
    RtdlAdaptiveRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);

}  // extern "C"

namespace {

struct TriangleSoA {
  std::vector<uint32_t> id;
  std::vector<double> x0;
  std::vector<double> y0;
  std::vector<double> z0;
  std::vector<double> e1x;
  std::vector<double> e1y;
  std::vector<double> e1z;
  std::vector<double> e2x;
  std::vector<double> e2y;
  std::vector<double> e2z;
};

void set_error(char* error_out, size_t error_size, const char* message) {
  if (error_out == nullptr || error_size == 0) {
    return;
  }
  std::snprintf(error_out, error_size, "%s", message);
}

TriangleSoA stage_triangles_soa(const RtdlAdaptiveTriangle3D* triangles, size_t count) {
  TriangleSoA staged;
  staged.id.reserve(count);
  staged.x0.reserve(count);
  staged.y0.reserve(count);
  staged.z0.reserve(count);
  staged.e1x.reserve(count);
  staged.e1y.reserve(count);
  staged.e1z.reserve(count);
  staged.e2x.reserve(count);
  staged.e2y.reserve(count);
  staged.e2z.reserve(count);
  for (size_t i = 0; i < count; ++i) {
    const RtdlAdaptiveTriangle3D& triangle = triangles[i];
    staged.id.push_back(triangle.id);
    staged.x0.push_back(triangle.x0);
    staged.y0.push_back(triangle.y0);
    staged.z0.push_back(triangle.z0);
    staged.e1x.push_back(triangle.x1 - triangle.x0);
    staged.e1y.push_back(triangle.y1 - triangle.y0);
    staged.e1z.push_back(triangle.z1 - triangle.z0);
    staged.e2x.push_back(triangle.x2 - triangle.x0);
    staged.e2y.push_back(triangle.y2 - triangle.y0);
    staged.e2z.push_back(triangle.z2 - triangle.z0);
  }
  return staged;
}

inline bool finite_ray_hits_triangle_3d(
    const RtdlAdaptiveRay3D& ray,
    const TriangleSoA& triangles,
    size_t index) {
  constexpr double eps = 1.0e-8;

  const double pvx = ray.dy * triangles.e2z[index] - ray.dz * triangles.e2y[index];
  const double pvy = ray.dz * triangles.e2x[index] - ray.dx * triangles.e2z[index];
  const double pvz = ray.dx * triangles.e2y[index] - ray.dy * triangles.e2x[index];

  const double det = triangles.e1x[index] * pvx +
                     triangles.e1y[index] * pvy +
                     triangles.e1z[index] * pvz;
  if (std::fabs(det) <= eps) {
    return false;
  }

  const double inv_det = 1.0 / det;
  const double tvx = ray.ox - triangles.x0[index];
  const double tvy = ray.oy - triangles.y0[index];
  const double tvz = ray.oz - triangles.z0[index];

  const double u = (tvx * pvx + tvy * pvy + tvz * pvz) * inv_det;
  if (u < 0.0 || u > 1.0) {
    return false;
  }

  const double qvx = tvy * triangles.e1z[index] - tvz * triangles.e1y[index];
  const double qvy = tvz * triangles.e1x[index] - tvx * triangles.e1z[index];
  const double qvz = tvx * triangles.e1y[index] - tvy * triangles.e1x[index];

  const double v = (ray.dx * qvx + ray.dy * qvy + ray.dz * qvz) * inv_det;
  if (v < 0.0 || (u + v) > 1.0) {
    return false;
  }

  const double t = (triangles.e2x[index] * qvx +
                    triangles.e2y[index] * qvy +
                    triangles.e2z[index] * qvz) *
                   inv_det;
  return t >= 0.0 && t <= ray.tmax;
}

}  // namespace

extern "C" RTDL_ADAPTIVE_EXPORT int rtdl_adaptive_run_ray_hitcount_3d(
    const RtdlAdaptiveRay3D* rays,
    size_t ray_count,
    const RtdlAdaptiveTriangle3D* triangles,
    size_t triangle_count,
    RtdlAdaptiveRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  if (rows_out == nullptr || row_count_out == nullptr) {
    set_error(error_out, error_size, "null output passed to rtdl_adaptive_run_ray_hitcount_3d");
    return 1;
  }
  *rows_out = nullptr;
  *row_count_out = 0;
  if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
    set_error(error_out, error_size, "null input passed to rtdl_adaptive_run_ray_hitcount_3d");
    return 2;
  }

  try {
    TriangleSoA staged = stage_triangles_soa(triangles, triangle_count);
    auto* rows = static_cast<RtdlAdaptiveRayHitCountRow*>(
        std::calloc(ray_count == 0 ? 1 : ray_count, sizeof(RtdlAdaptiveRayHitCountRow)));
    if (rows == nullptr) {
      set_error(error_out, error_size, "out of memory allocating adaptive ray-hitcount rows");
      return 3;
    }

    for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
      const RtdlAdaptiveRay3D& ray = rays[ray_index];
      uint32_t hit_count = 0;
      for (size_t tri_index = 0; tri_index < triangle_count; ++tri_index) {
        hit_count += finite_ray_hits_triangle_3d(ray, staged, tri_index) ? 1u : 0u;
      }
      rows[ray_index].ray_id = ray.id;
      rows[ray_index].hit_count = hit_count;
    }

    *rows_out = rows;
    *row_count_out = ray_count;
    return 0;
  } catch (const std::bad_alloc&) {
    set_error(error_out, error_size, "out of memory in adaptive ray-hitcount kernel");
    return 4;
  } catch (const std::exception& exc) {
    set_error(error_out, error_size, exc.what());
    return 5;
  }
}
