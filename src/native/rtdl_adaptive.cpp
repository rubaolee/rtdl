#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <exception>
#include <new>
#include <algorithm>
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

struct RtdlAdaptiveSegment {
  uint32_t id;
  double x0;
  double y0;
  double x1;
  double y1;
};

struct RtdlAdaptivePoint {
  uint32_t id;
  double x;
  double y;
};

struct RtdlAdaptiveLsiRow {
  uint32_t left_id;
  uint32_t right_id;
  double intersection_point_x;
  double intersection_point_y;
};

struct RtdlAdaptivePointNearestSegmentRow {
  uint32_t point_id;
  uint32_t segment_id;
  double distance;
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

RTDL_ADAPTIVE_EXPORT int rtdl_adaptive_run_segment_intersection(
    const RtdlAdaptiveSegment* left,
    size_t left_count,
    const RtdlAdaptiveSegment* right,
    size_t right_count,
    RtdlAdaptiveLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);

RTDL_ADAPTIVE_EXPORT int rtdl_adaptive_run_point_nearest_segment(
    const RtdlAdaptivePoint* points,
    size_t point_count,
    const RtdlAdaptiveSegment* segments,
    size_t segment_count,
    RtdlAdaptivePointNearestSegmentRow** rows_out,
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

struct SegmentSoA {
  std::vector<uint32_t> id;
  std::vector<double> x0;
  std::vector<double> y0;
  std::vector<double> dx;
  std::vector<double> dy;
  std::vector<double> min_x;
  std::vector<double> min_y;
  std::vector<double> max_x;
  std::vector<double> max_y;
};

void set_error(char* error_out, size_t error_size, const char* message) {
  if (error_out == nullptr || error_size == 0) {
    return;
  }
  std::snprintf(error_out, error_size, "%s", message);
}

SegmentSoA stage_segments_soa(const RtdlAdaptiveSegment* segments, size_t count) {
  SegmentSoA staged;
  staged.id.reserve(count);
  staged.x0.reserve(count);
  staged.y0.reserve(count);
  staged.dx.reserve(count);
  staged.dy.reserve(count);
  staged.min_x.reserve(count);
  staged.min_y.reserve(count);
  staged.max_x.reserve(count);
  staged.max_y.reserve(count);
  for (size_t i = 0; i < count; ++i) {
    const RtdlAdaptiveSegment& segment = segments[i];
    const double dx = segment.x1 - segment.x0;
    const double dy = segment.y1 - segment.y0;
    staged.id.push_back(segment.id);
    staged.x0.push_back(segment.x0);
    staged.y0.push_back(segment.y0);
    staged.dx.push_back(dx);
    staged.dy.push_back(dy);
    staged.min_x.push_back(std::min(segment.x0, segment.x1));
    staged.min_y.push_back(std::min(segment.y0, segment.y1));
    staged.max_x.push_back(std::max(segment.x0, segment.x1));
    staged.max_y.push_back(std::max(segment.y0, segment.y1));
  }
  return staged;
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

inline bool bbox_overlap(
    double left_min_x,
    double left_min_y,
    double left_max_x,
    double left_max_y,
    const SegmentSoA& right,
    size_t index) {
  return !(left_max_x < right.min_x[index] ||
           right.max_x[index] < left_min_x ||
           left_max_y < right.min_y[index] ||
           right.max_y[index] < left_min_y);
}

inline bool segment_intersection_point(
    const RtdlAdaptiveSegment& left,
    double left_dx,
    double left_dy,
    const SegmentSoA& right,
    size_t index,
    double* ix,
    double* iy) {
  constexpr double eps = 1.0e-9;
  const double denom = left_dx * right.dy[index] - left_dy * right.dx[index];
  if (std::fabs(denom) < eps) {
    return false;
  }
  const double qmp_x = right.x0[index] - left.x0;
  const double qmp_y = right.y0[index] - left.y0;
  const double t = (qmp_x * right.dy[index] - qmp_y * right.dx[index]) / denom;
  const double u = (qmp_x * left_dy - qmp_y * left_dx) / denom;
  if (!(0.0 <= t && t <= 1.0 && 0.0 <= u && u <= 1.0)) {
    return false;
  }
  *ix = left.x0 + t * left_dx;
  *iy = left.y0 + t * left_dy;
  return true;
}

inline double point_segment_distance_sq(
    const RtdlAdaptivePoint& point,
    const SegmentSoA& segments,
    size_t index) {
  const double px = point.x - segments.x0[index];
  const double py = point.y - segments.y0[index];
  const double len_sq = segments.dx[index] * segments.dx[index] + segments.dy[index] * segments.dy[index];
  if (len_sq <= 0.0) {
    return px * px + py * py;
  }
  double t = (px * segments.dx[index] + py * segments.dy[index]) / len_sq;
  if (t < 0.0) {
    t = 0.0;
  } else if (t > 1.0) {
    t = 1.0;
  }
  const double cx = segments.x0[index] + t * segments.dx[index];
  const double cy = segments.y0[index] + t * segments.dy[index];
  const double ddx = point.x - cx;
  const double ddy = point.y - cy;
  return ddx * ddx + ddy * ddy;
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

extern "C" RTDL_ADAPTIVE_EXPORT int rtdl_adaptive_run_segment_intersection(
    const RtdlAdaptiveSegment* left,
    size_t left_count,
    const RtdlAdaptiveSegment* right,
    size_t right_count,
    RtdlAdaptiveLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  if (rows_out == nullptr || row_count_out == nullptr) {
    set_error(error_out, error_size, "null output passed to rtdl_adaptive_run_segment_intersection");
    return 1;
  }
  *rows_out = nullptr;
  *row_count_out = 0;
  if ((left_count > 0 && left == nullptr) || (right_count > 0 && right == nullptr)) {
    set_error(error_out, error_size, "null input passed to rtdl_adaptive_run_segment_intersection");
    return 2;
  }

  try {
    SegmentSoA staged_right = stage_segments_soa(right, right_count);
    std::vector<RtdlAdaptiveLsiRow> rows;
    rows.reserve(std::min(left_count * right_count, static_cast<size_t>(1024)));
    for (size_t left_index = 0; left_index < left_count; ++left_index) {
      const RtdlAdaptiveSegment& left_segment = left[left_index];
      const double left_dx = left_segment.x1 - left_segment.x0;
      const double left_dy = left_segment.y1 - left_segment.y0;
      const double left_min_x = std::min(left_segment.x0, left_segment.x1);
      const double left_min_y = std::min(left_segment.y0, left_segment.y1);
      const double left_max_x = std::max(left_segment.x0, left_segment.x1);
      const double left_max_y = std::max(left_segment.y0, left_segment.y1);
      for (size_t right_index = 0; right_index < right_count; ++right_index) {
        if (!bbox_overlap(left_min_x, left_min_y, left_max_x, left_max_y, staged_right, right_index)) {
          continue;
        }
        double ix = 0.0;
        double iy = 0.0;
        if (!segment_intersection_point(left_segment, left_dx, left_dy, staged_right, right_index, &ix, &iy)) {
          continue;
        }
        rows.push_back({left_segment.id, staged_right.id[right_index], ix, iy});
      }
    }

    auto* output = static_cast<RtdlAdaptiveLsiRow*>(
        std::calloc(rows.empty() ? 1 : rows.size(), sizeof(RtdlAdaptiveLsiRow)));
    if (output == nullptr) {
      set_error(error_out, error_size, "out of memory allocating adaptive segment-intersection rows");
      return 3;
    }
    if (!rows.empty()) {
      std::memcpy(output, rows.data(), rows.size() * sizeof(RtdlAdaptiveLsiRow));
    }
    *rows_out = output;
    *row_count_out = rows.size();
    return 0;
  } catch (const std::bad_alloc&) {
    set_error(error_out, error_size, "out of memory in adaptive segment-intersection kernel");
    return 4;
  } catch (const std::exception& exc) {
    set_error(error_out, error_size, exc.what());
    return 5;
  }
}

extern "C" RTDL_ADAPTIVE_EXPORT int rtdl_adaptive_run_point_nearest_segment(
    const RtdlAdaptivePoint* points,
    size_t point_count,
    const RtdlAdaptiveSegment* segments,
    size_t segment_count,
    RtdlAdaptivePointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  if (rows_out == nullptr || row_count_out == nullptr) {
    set_error(error_out, error_size, "null output passed to rtdl_adaptive_run_point_nearest_segment");
    return 1;
  }
  *rows_out = nullptr;
  *row_count_out = 0;
  if ((point_count > 0 && points == nullptr) || (segment_count > 0 && segments == nullptr)) {
    set_error(error_out, error_size, "null input passed to rtdl_adaptive_run_point_nearest_segment");
    return 2;
  }

  try {
    SegmentSoA staged_segments = stage_segments_soa(segments, segment_count);
    auto* rows = static_cast<RtdlAdaptivePointNearestSegmentRow*>(
        std::calloc(point_count == 0 ? 1 : point_count, sizeof(RtdlAdaptivePointNearestSegmentRow)));
    if (rows == nullptr) {
      set_error(error_out, error_size, "out of memory allocating adaptive nearest-segment rows");
      return 3;
    }

    size_t emitted = 0;
    for (size_t point_index = 0; point_index < point_count; ++point_index) {
      if (segment_count == 0) {
        continue;
      }
      const RtdlAdaptivePoint& point = points[point_index];
      double best_distance_sq = 0.0;
      uint32_t best_segment_id = 0;
      bool has_best = false;
      for (size_t segment_index = 0; segment_index < segment_count; ++segment_index) {
        const double distance_sq = point_segment_distance_sq(point, staged_segments, segment_index);
        const uint32_t segment_id = staged_segments.id[segment_index];
        if (!has_best ||
            distance_sq < best_distance_sq - 1.0e-14 ||
            (std::fabs(distance_sq - best_distance_sq) <= 1.0e-14 && segment_id < best_segment_id)) {
          best_distance_sq = distance_sq;
          best_segment_id = segment_id;
          has_best = true;
        }
      }
      if (has_best) {
        rows[emitted].point_id = point.id;
        rows[emitted].segment_id = best_segment_id;
        rows[emitted].distance = std::sqrt(best_distance_sq);
        ++emitted;
      }
    }

    *rows_out = rows;
    *row_count_out = emitted;
    return 0;
  } catch (const std::bad_alloc&) {
    set_error(error_out, error_size, "out of memory in adaptive point-nearest-segment kernel");
    return 4;
  } catch (const std::exception& exc) {
    set_error(error_out, error_size, exc.what());
    return 5;
  }
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
