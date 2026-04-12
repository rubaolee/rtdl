#pragma once

#include "rtdl_oracle_abi.h"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <new>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#if defined(__has_include)
#  if __has_include(<geos_c.h>)
#    include <geos_c.h>
#    define RTDL_ORACLE_HAS_GEOS 1
#  else
#    define RTDL_ORACLE_HAS_GEOS 0
#  endif
#else
#  define RTDL_ORACLE_HAS_GEOS 0
#endif

namespace rtdl::oracle {

constexpr double kSegmentIntersectionEps = 1.0e-7;
constexpr double kPointEps = 1.0e-12;
constexpr double kDegenerateDistanceEps = 1.0e-12;
constexpr double kRayCrossingDenomEps = 1.0e-20;

template <typename T>
void set_error(const std::string& message, T* error_out, size_t error_size) {
  if (error_out == nullptr || error_size == 0) {
    return;
  }
  size_t length = std::min(error_size - 1, message.size());
  std::memcpy(error_out, message.data(), length);
  error_out[length] = '\0';
}

template <typename Fn>
int handle_native_call(Fn&& fn, char* error_out, size_t error_size) {
  try {
    fn();
    return 0;
  } catch (const std::exception& ex) {
    set_error(ex.what(), error_out, error_size);
    return 1;
  }
}

template <typename T>
T* copy_rows_out(const std::vector<T>& rows) {
  if (rows.empty()) {
    return nullptr;
  }
  T* output = static_cast<T*>(std::malloc(sizeof(T) * rows.size()));
  if (output == nullptr) {
    throw std::bad_alloc();
  }
  std::memcpy(output, rows.data(), sizeof(T) * rows.size());
  return output;
}

struct Vec2 {
  double x;
  double y;
};

struct Segment2D {
  uint32_t id;
  Vec2 a;
  Vec2 b;
};

struct Point2D {
  uint32_t id;
  Vec2 p;
};

struct Vec3 {
  double x;
  double y;
  double z;
};

struct Point3D {
  uint32_t id;
  Vec3 p;
};

struct Polygon2D {
  uint32_t id;
  std::vector<Vec2> vertices;
};

struct Bounds2D {
  double min_x;
  double min_y;
  double max_x;
  double max_y;
};

struct Triangle2D {
  uint32_t id;
  Vec2 a;
  Vec2 b;
  Vec2 c;
};

struct RayQuery2D {
  uint32_t id;
  Vec2 o;
  Vec2 d;
  double tmax;
};

struct PolygonBucketIndex {
  double origin_x;
  double bucket_width;
  std::vector<std::vector<size_t>> buckets;
};

Vec2 sub(const Vec2& a, const Vec2& b);
double cross(const Vec2& a, const Vec2& b);

std::vector<Segment2D> decode_segments(const RtdlSegment* records, size_t count);
std::vector<Point2D> decode_points(const RtdlPoint* records, size_t count);
std::vector<Point3D> decode_points3d(const RtdlPoint3D* records, size_t count);
std::vector<Triangle2D> decode_triangles(const RtdlTriangle* records, size_t count);
std::vector<RayQuery2D> decode_rays(const RtdlRay2D* records, size_t count);
std::vector<Polygon2D> decode_polygons(
    const RtdlPolygonRef* refs,
    size_t ref_count,
    const double* vertices_xy,
    size_t vertex_xy_count);

bool segment_intersection(const Segment2D& left, const Segment2D& right, Vec2* point_out);
bool point_on_segment(const Vec2& point, const Vec2& start, const Vec2& end);
bool point_in_polygon(double x, double y, const std::vector<Vec2>& vertices);
std::vector<Segment2D> segments_from_polygons(const std::vector<Polygon2D>& polygons);
std::vector<RtdlLsiRow> oracle_lsi(
    const std::vector<Segment2D>& left_segments,
    const std::vector<Segment2D>& right_segments);
Bounds2D bounds_for_polygon(const Polygon2D& polygon);
Bounds2D bounds_for_segment(const Segment2D& segment);
bool bounds_overlap(const Bounds2D& left, const Bounds2D& right);
bool is_close_to_integer(double value);
void require_pathology_grid_polygon(const Polygon2D& polygon);
uint64_t encode_cell_key(int32_t x, int32_t y);
std::vector<uint64_t> polygon_unit_cells(const Polygon2D& polygon);
uint32_t intersect_cell_sets(const std::vector<uint64_t>& left, const std::vector<uint64_t>& right);
std::vector<uint64_t> polygon_set_unit_cells(const std::vector<Polygon2D>& polygons);
PolygonBucketIndex build_polygon_bucket_index(const std::vector<Bounds2D>& polygon_bounds);
std::vector<RtdlPipRow> oracle_pip(
    const std::vector<Point2D>& points,
    const std::vector<Polygon2D>& polygons,
    bool positive_only);
bool point_in_triangle(double x, double y, const Triangle2D& triangle);
bool finite_ray_hits_triangle(const RayQuery2D& ray, const Triangle2D& triangle);
bool segment_hits_polygon(const Segment2D& segment, const Polygon2D& polygon);
double point_segment_distance(const Point2D& point, const Segment2D& segment);

}  // namespace rtdl::oracle
