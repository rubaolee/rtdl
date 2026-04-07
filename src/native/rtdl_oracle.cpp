#include <algorithm>
#include <cmath>
#include <cstdint>
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

extern "C" {

struct RtdlSegment {
  uint32_t id;
  double x0;
  double y0;
  double x1;
  double y1;
};

struct RtdlPoint {
  uint32_t id;
  double x;
  double y;
};

struct RtdlPolygonRef {
  uint32_t id;
  uint32_t vertex_offset;
  uint32_t vertex_count;
};

struct RtdlTriangle {
  uint32_t id;
  double x0;
  double y0;
  double x1;
  double y1;
  double x2;
  double y2;
};

struct RtdlRay2D {
  uint32_t id;
  double ox;
  double oy;
  double dx;
  double dy;
  double tmax;
};

struct RtdlLsiRow {
  uint32_t left_id;
  uint32_t right_id;
  double intersection_point_x;
  double intersection_point_y;
};

struct RtdlPipRow {
  uint32_t point_id;
  uint32_t polygon_id;
  uint32_t contains;
};

struct RtdlOverlayRow {
  uint32_t left_polygon_id;
  uint32_t right_polygon_id;
  uint32_t requires_lsi;
  uint32_t requires_pip;
};

struct RtdlRayHitCountRow {
  uint32_t ray_id;
  uint32_t hit_count;
};

struct RtdlSegmentPolygonHitCountRow {
  uint32_t segment_id;
  uint32_t hit_count;
};

struct RtdlSegmentPolygonAnyHitRow {
  uint32_t segment_id;
  uint32_t polygon_id;
};

struct RtdlPolygonPairOverlapAreaRow {
  uint32_t left_polygon_id;
  uint32_t right_polygon_id;
  uint32_t intersection_area;
  uint32_t left_area;
  uint32_t right_area;
  uint32_t union_area;
};

struct RtdlPointNearestSegmentRow {
  uint32_t point_id;
  uint32_t segment_id;
  double distance;
};

int rtdl_oracle_get_version(int* major_out, int* minor_out, int* patch_out);
int rtdl_oracle_run_lsi(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_pip(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    uint32_t positive_only,
    RtdlPipRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_overlay(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlOverlayRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_ray_hitcount(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_segment_polygon_hitcount(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_segment_polygon_anyhit_rows(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_polygon_pair_overlap_area_rows(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlPolygonPairOverlapAreaRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_point_nearest_segment(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_oracle_free_rows(void* rows);

}

namespace {

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

#if RTDL_ORACLE_HAS_GEOS
class GeosPreparedPolygonSet {
 public:
  explicit GeosPreparedPolygonSet(const std::vector<Polygon2D>& polygons) : context_(GEOS_init_r()) {
    if (context_ == nullptr) {
      throw std::runtime_error("failed to initialize GEOS context");
    }
    geometries_.reserve(polygons.size());
    prepared_.reserve(polygons.size());
    for (const Polygon2D& polygon : polygons) {
      GEOSGeometry* geometry = build_polygon_geometry(polygon.vertices);
      if (geometry == nullptr) {
        throw std::runtime_error("failed to build GEOS polygon geometry");
      }
      const GEOSPreparedGeometry* prepared = GEOSPrepare_r(context_, geometry);
      if (prepared == nullptr) {
        GEOSGeom_destroy_r(context_, geometry);
        throw std::runtime_error("failed to prepare GEOS polygon geometry");
      }
      geometries_.push_back(geometry);
      prepared_.push_back(prepared);
    }
  }

  GeosPreparedPolygonSet(const GeosPreparedPolygonSet&) = delete;
  GeosPreparedPolygonSet& operator=(const GeosPreparedPolygonSet&) = delete;

  ~GeosPreparedPolygonSet() {
    if (context_ == nullptr) {
      return;
    }
    for (const GEOSPreparedGeometry* prepared : prepared_) {
      if (prepared != nullptr) {
        GEOSPreparedGeom_destroy_r(context_, prepared);
      }
    }
    for (GEOSGeometry* geometry : geometries_) {
      if (geometry != nullptr) {
        GEOSGeom_destroy_r(context_, geometry);
      }
    }
    GEOS_finish_r(context_);
  }

  bool covers(size_t polygon_index, double x, double y) const {
    GEOSGeometry* point = build_point_geometry(x, y);
    if (point == nullptr) {
      throw std::runtime_error("failed to build GEOS point geometry");
    }
    char covers_value = GEOSPreparedCovers_r(context_, prepared_.at(polygon_index), point);
    GEOSGeom_destroy_r(context_, point);
    if (covers_value == 2) {
      throw std::runtime_error("GEOSPreparedCovers_r failed");
    }
    return covers_value == 1;
  }

 private:
  GEOSGeometry* build_point_geometry(double x, double y) const {
    GEOSCoordSequence* sequence = GEOSCoordSeq_create_r(context_, 1, 2);
    if (sequence == nullptr) {
      return nullptr;
    }
    if (!GEOSCoordSeq_setX_r(context_, sequence, 0, x) ||
        !GEOSCoordSeq_setY_r(context_, sequence, 0, y)) {
      GEOSCoordSeq_destroy_r(context_, sequence);
      return nullptr;
    }
    return GEOSGeom_createPoint_r(context_, sequence);
  }

  GEOSGeometry* build_polygon_geometry(const std::vector<Vec2>& vertices) const {
    size_t ring_size = vertices.size();
    bool closed = ring_size > 0 &&
                  vertices.front().x == vertices.back().x &&
                  vertices.front().y == vertices.back().y;
    if (!closed) {
      ring_size += 1;
    }
    GEOSCoordSequence* sequence = GEOSCoordSeq_create_r(context_, ring_size, 2);
    if (sequence == nullptr) {
      return nullptr;
    }
    for (size_t i = 0; i < vertices.size(); ++i) {
      if (!GEOSCoordSeq_setX_r(context_, sequence, i, vertices[i].x) ||
          !GEOSCoordSeq_setY_r(context_, sequence, i, vertices[i].y)) {
        GEOSCoordSeq_destroy_r(context_, sequence);
        return nullptr;
      }
    }
    if (!closed) {
      if (!GEOSCoordSeq_setX_r(context_, sequence, ring_size - 1, vertices.front().x) ||
          !GEOSCoordSeq_setY_r(context_, sequence, ring_size - 1, vertices.front().y)) {
        GEOSCoordSeq_destroy_r(context_, sequence);
        return nullptr;
      }
    }
    GEOSGeometry* ring = GEOSGeom_createLinearRing_r(context_, sequence);
    if (ring == nullptr) {
      return nullptr;
    }
    GEOSGeometry* polygon = GEOSGeom_createPolygon_r(context_, ring, nullptr, 0);
    if (polygon == nullptr) {
      GEOSGeom_destroy_r(context_, ring);
      return nullptr;
    }
    return polygon;
  }

  GEOSContextHandle_t context_;
  std::vector<GEOSGeometry*> geometries_;
  std::vector<const GEOSPreparedGeometry*> prepared_;
};
#endif

Vec2 sub(const Vec2& a, const Vec2& b) {
  return {a.x - b.x, a.y - b.y};
}

double cross(const Vec2& a, const Vec2& b) {
  return a.x * b.y - a.y * b.x;
}

std::vector<Segment2D> decode_segments(const RtdlSegment* records, size_t count) {
  std::vector<Segment2D> values;
  values.reserve(count);
  for (size_t i = 0; i < count; ++i) {
    values.push_back({records[i].id, {records[i].x0, records[i].y0}, {records[i].x1, records[i].y1}});
  }
  return values;
}

std::vector<Point2D> decode_points(const RtdlPoint* records, size_t count) {
  std::vector<Point2D> values;
  values.reserve(count);
  for (size_t i = 0; i < count; ++i) {
    values.push_back({records[i].id, {records[i].x, records[i].y}});
  }
  return values;
}

std::vector<Triangle2D> decode_triangles(const RtdlTriangle* records, size_t count) {
  std::vector<Triangle2D> values;
  values.reserve(count);
  for (size_t i = 0; i < count; ++i) {
    values.push_back({records[i].id, {records[i].x0, records[i].y0}, {records[i].x1, records[i].y1}, {records[i].x2, records[i].y2}});
  }
  return values;
}

std::vector<RayQuery2D> decode_rays(const RtdlRay2D* records, size_t count) {
  std::vector<RayQuery2D> values;
  values.reserve(count);
  for (size_t i = 0; i < count; ++i) {
    values.push_back({records[i].id, {records[i].ox, records[i].oy}, {records[i].dx, records[i].dy}, records[i].tmax});
  }
  return values;
}

std::vector<Polygon2D> decode_polygons(
    const RtdlPolygonRef* refs,
    size_t ref_count,
    const double* vertices_xy,
    size_t vertex_xy_count) {
  std::vector<Polygon2D> polygons;
  polygons.reserve(ref_count);
  size_t vertex_count = vertex_xy_count / 2;
  for (size_t i = 0; i < ref_count; ++i) {
    const RtdlPolygonRef& ref = refs[i];
    if (static_cast<size_t>(ref.vertex_offset) + static_cast<size_t>(ref.vertex_count) > vertex_count) {
      throw std::runtime_error("polygon vertex buffer is out of range");
    }
    if (ref.vertex_count < 3) {
      throw std::runtime_error("polygon requires at least 3 vertices");
    }
    Polygon2D polygon;
    polygon.id = ref.id;
    polygon.vertices.reserve(ref.vertex_count);
    for (size_t j = 0; j < ref.vertex_count; ++j) {
      size_t index = static_cast<size_t>(ref.vertex_offset) + j;
      polygon.vertices.push_back({vertices_xy[index * 2], vertices_xy[index * 2 + 1]});
    }
    polygons.push_back(std::move(polygon));
  }
  return polygons;
}

bool segment_intersection(const Segment2D& left, const Segment2D& right, Vec2* point_out) {
  Vec2 p = left.a;
  Vec2 r = sub(left.b, left.a);
  Vec2 q = right.a;
  Vec2 s = sub(right.b, right.a);

  double denom = cross(r, s);
  if (std::fabs(denom) < kSegmentIntersectionEps) {
    return false;
  }

  Vec2 qmp = sub(q, p);
  double t = cross(qmp, s) / denom;
  double u = cross(qmp, r) / denom;
  if (!(0.0 <= t && t <= 1.0 && 0.0 <= u && u <= 1.0)) {
    return false;
  }

  if (point_out != nullptr) {
    point_out->x = p.x + t * r.x;
    point_out->y = p.y + t * r.y;
  }
  return true;
}

bool point_on_segment(const Vec2& point, const Vec2& start, const Vec2& end) {
  double length_sq = (end.x - start.x) * (end.x - start.x) + (end.y - start.y) * (end.y - start.y);
  if (length_sq <= kPointEps * kPointEps) {
    return std::fabs(point.x - start.x) <= kPointEps &&
           std::fabs(point.y - start.y) <= kPointEps;
  }
  double length = std::sqrt(length_sq);
  double cross_value = (point.x - start.x) * (end.y - start.y) - (point.y - start.y) * (end.x - start.x);
  if (std::fabs(cross_value) > kPointEps * length) {
    return false;
  }
  double dot = (point.x - start.x) * (end.x - start.x) + (point.y - start.y) * (end.y - start.y);
  double along_eps = kPointEps * length;
  if (dot < -along_eps) {
    return false;
  }
  if (dot - length_sq > along_eps) {
    return false;
  }
  return true;
}

bool point_in_polygon(
    double x,
    double y,
    const std::vector<Vec2>& vertices) {
  Vec2 point {x, y};
  for (size_t i = 0; i < vertices.size(); ++i) {
    const Vec2& start = vertices[i];
    const Vec2& end = vertices[(i + 1) % vertices.size()];
    if (point_on_segment(point, start, end)) {
      return true;
    }
  }

  bool inside = false;
  size_t j = vertices.size() - 1;
  for (size_t i = 0; i < vertices.size(); ++i) {
    const Vec2& vi = vertices[i];
    const Vec2& vj = vertices[j];
    bool crossing = ((vi.y > y) != (vj.y > y)) &&
                    (x <= (vj.x - vi.x) * (y - vi.y) / ((vj.y - vi.y) == 0.0 ? kRayCrossingDenomEps : (vj.y - vi.y)) + vi.x);
    if (crossing) {
      inside = !inside;
    }
    j = i;
  }
  return inside;
}

std::vector<Segment2D> segments_from_polygons(const std::vector<Polygon2D>& polygons) {
  std::vector<Segment2D> segments;
  for (const Polygon2D& polygon : polygons) {
    for (size_t i = 0; i < polygon.vertices.size(); ++i) {
      segments.push_back({polygon.id, polygon.vertices[i], polygon.vertices[(i + 1) % polygon.vertices.size()]});
    }
  }
  return segments;
}

std::vector<RtdlLsiRow> oracle_lsi(
    const std::vector<Segment2D>& left_segments,
    const std::vector<Segment2D>& right_segments) {
  struct IndexedSegmentBounds {
    size_t original_index;
    const Segment2D* segment;
    double min_x;
    double max_x;
    double min_y;
    double max_y;
  };

  auto min_max = [](const Segment2D& segment) {
    return IndexedSegmentBounds{
        0,
        &segment,
        std::min(segment.a.x, segment.b.x),
        std::max(segment.a.x, segment.b.x),
        std::min(segment.a.y, segment.b.y),
        std::max(segment.a.y, segment.b.y),
    };
  };

  std::vector<IndexedSegmentBounds> build_sorted;
  build_sorted.reserve(right_segments.size());
  for (size_t index = 0; index < right_segments.size(); ++index) {
    IndexedSegmentBounds bounds = min_max(right_segments[index]);
    bounds.original_index = index;
    build_sorted.push_back(bounds);
  }
  std::stable_sort(
      build_sorted.begin(),
      build_sorted.end(),
      [](const IndexedSegmentBounds& left, const IndexedSegmentBounds& right) {
        return left.min_x < right.min_x;
      });

  std::vector<IndexedSegmentBounds> probe_sorted;
  probe_sorted.reserve(left_segments.size());
  for (size_t index = 0; index < left_segments.size(); ++index) {
    IndexedSegmentBounds bounds = min_max(left_segments[index]);
    bounds.original_index = index;
    probe_sorted.push_back(bounds);
  }
  std::stable_sort(
      probe_sorted.begin(),
      probe_sorted.end(),
      [](const IndexedSegmentBounds& left, const IndexedSegmentBounds& right) {
        return left.min_x < right.min_x;
      });

  std::vector<std::vector<std::pair<size_t, RtdlLsiRow>>> hits_by_probe(left_segments.size());
  std::vector<size_t> active;
  std::vector<size_t> next_active;
  size_t build_cursor = 0;

  for (const IndexedSegmentBounds& probe : probe_sorted) {
    while (build_cursor < build_sorted.size() && build_sorted[build_cursor].min_x <= probe.max_x) {
      active.push_back(build_cursor);
      build_cursor += 1;
    }

    next_active.clear();
    std::vector<std::pair<size_t, RtdlLsiRow>>& probe_hits = hits_by_probe[probe.original_index];
    for (size_t active_index : active) {
      const IndexedSegmentBounds& build = build_sorted[active_index];
      if (build.max_x < probe.min_x) {
        continue;
      }
      next_active.push_back(active_index);
      if (build.max_y < probe.min_y || build.min_y > probe.max_y) {
        continue;
      }
      Vec2 point {};
      if (!segment_intersection(*probe.segment, *build.segment, &point)) {
        continue;
      }
      probe_hits.push_back({
          build.original_index,
          {probe.segment->id, build.segment->id, point.x, point.y},
      });
    }
    active.swap(next_active);
  }

  std::vector<RtdlLsiRow> rows;
  for (std::vector<std::pair<size_t, RtdlLsiRow>>& probe_hits : hits_by_probe) {
    std::stable_sort(
        probe_hits.begin(),
        probe_hits.end(),
        [](const auto& left, const auto& right) {
          return left.first < right.first;
        });
    for (const auto& hit : probe_hits) {
      rows.push_back(hit.second);
    }
  }
  return rows;
}

Bounds2D bounds_for_polygon(const Polygon2D& polygon) {
  Bounds2D bounds {
      polygon.vertices[0].x,
      polygon.vertices[0].y,
      polygon.vertices[0].x,
      polygon.vertices[0].y,
  };
  for (const Vec2& vertex : polygon.vertices) {
    bounds.min_x = std::min(bounds.min_x, vertex.x);
    bounds.min_y = std::min(bounds.min_y, vertex.y);
    bounds.max_x = std::max(bounds.max_x, vertex.x);
    bounds.max_y = std::max(bounds.max_y, vertex.y);
  }
  return bounds;
}

Bounds2D bounds_for_segment(const Segment2D& segment) {
  return {
      std::min(segment.a.x, segment.b.x),
      std::min(segment.a.y, segment.b.y),
      std::max(segment.a.x, segment.b.x),
      std::max(segment.a.y, segment.b.y),
  };
}

bool bounds_overlap(const Bounds2D& left, const Bounds2D& right) {
  return !(left.max_x < right.min_x || right.max_x < left.min_x ||
           left.max_y < right.min_y || right.max_y < left.min_y);
}

Bounds2D bounds_for_polygon(const Polygon2D& polygon);

bool is_close_to_integer(double value) {
  return std::fabs(value - std::round(value)) <= 1.0e-9;
}

void require_pathology_grid_polygon(const Polygon2D& polygon) {
  if (polygon.vertices.size() < 3) {
    throw std::runtime_error("polygon_pair_overlap_area_rows requires polygons with at least 3 vertices");
  }
  for (const Vec2& vertex : polygon.vertices) {
    if (!is_close_to_integer(vertex.x) || !is_close_to_integer(vertex.y)) {
      throw std::runtime_error(
          "polygon_pair_overlap_area_rows currently requires integer-grid polygon vertices");
    }
  }
  for (size_t i = 0; i < polygon.vertices.size(); ++i) {
    const Vec2& start = polygon.vertices[i];
    const Vec2& end = polygon.vertices[(i + 1) % polygon.vertices.size()];
    const double dx = end.x - start.x;
    const double dy = end.y - start.y;
    if (std::fabs(dx) <= kPointEps && std::fabs(dy) <= kPointEps) {
      throw std::runtime_error("polygon_pair_overlap_area_rows does not accept zero-length polygon edges");
    }
    if (std::fabs(dx) > kPointEps && std::fabs(dy) > kPointEps) {
      throw std::runtime_error(
          "polygon_pair_overlap_area_rows currently requires orthogonal integer-grid polygons");
    }
  }
}

uint64_t encode_cell_key(int32_t x, int32_t y) {
  return (static_cast<uint64_t>(static_cast<uint32_t>(x)) << 32) |
         static_cast<uint64_t>(static_cast<uint32_t>(y));
}

std::vector<uint64_t> polygon_unit_cells(const Polygon2D& polygon) {
  require_pathology_grid_polygon(polygon);
  const Bounds2D bounds = bounds_for_polygon(polygon);
  const int min_x = static_cast<int>(std::floor(bounds.min_x));
  const int max_x = static_cast<int>(std::ceil(bounds.max_x));
  const int min_y = static_cast<int>(std::floor(bounds.min_y));
  const int max_y = static_cast<int>(std::ceil(bounds.max_y));
  std::vector<uint64_t> cells;
  cells.reserve(static_cast<size_t>(std::max(0, max_x - min_x) * std::max(0, max_y - min_y)));
  for (int iy = min_y; iy < max_y; ++iy) {
    for (int ix = min_x; ix < max_x; ++ix) {
      if (point_in_polygon(static_cast<double>(ix) + 0.5, static_cast<double>(iy) + 0.5, polygon.vertices)) {
        cells.push_back(encode_cell_key(ix, iy));
      }
    }
  }
  std::sort(cells.begin(), cells.end());
  cells.erase(std::unique(cells.begin(), cells.end()), cells.end());
  return cells;
}

uint32_t intersect_cell_sets(const std::vector<uint64_t>& left, const std::vector<uint64_t>& right) {
  size_t left_index = 0;
  size_t right_index = 0;
  uint32_t count = 0;
  while (left_index < left.size() && right_index < right.size()) {
    if (left[left_index] == right[right_index]) {
      count += 1;
      left_index += 1;
      right_index += 1;
    } else if (left[left_index] < right[right_index]) {
      left_index += 1;
    } else {
      right_index += 1;
    }
  }
  return count;
}

struct PolygonBucketIndex {
  double origin_x;
  double bucket_width;
  std::vector<std::vector<size_t>> buckets;
};

PolygonBucketIndex build_polygon_bucket_index(const std::vector<Bounds2D>& polygon_bounds) {
  if (polygon_bounds.empty()) {
    return {0.0, 1.0, {}};
  }
  double global_min = polygon_bounds.front().min_x;
  double global_max = polygon_bounds.front().max_x;
  for (const Bounds2D& bounds : polygon_bounds) {
    global_min = std::min(global_min, bounds.min_x);
    global_max = std::max(global_max, bounds.max_x);
  }
  const double span = std::max(global_max - global_min, 1.0e-9);
  const size_t bucket_count = std::max<size_t>(16, std::min<size_t>(polygon_bounds.size() * 2, 8192));
  const double bucket_width = span / static_cast<double>(bucket_count);
  std::vector<std::vector<size_t>> buckets(bucket_count);
  for (size_t polygon_index = 0; polygon_index < polygon_bounds.size(); ++polygon_index) {
    const Bounds2D& bounds = polygon_bounds[polygon_index];
    const auto first = static_cast<size_t>(std::clamp(
        static_cast<long long>(std::floor((bounds.min_x - global_min) / bucket_width)),
        0LL,
        static_cast<long long>(bucket_count - 1)));
    const auto last = static_cast<size_t>(std::clamp(
        static_cast<long long>(std::floor((bounds.max_x - global_min) / bucket_width)),
        0LL,
        static_cast<long long>(bucket_count - 1)));
    for (size_t bucket_id = first; bucket_id <= last; ++bucket_id) {
      buckets[bucket_id].push_back(polygon_index);
    }
  }
  return {global_min, bucket_width, std::move(buckets)};
}

std::vector<RtdlPipRow> oracle_pip(
    const std::vector<Point2D>& points,
    const std::vector<Polygon2D>& polygons,
    bool positive_only) {
  std::vector<RtdlPipRow> rows;
  if (!positive_only) {
    rows.reserve(points.size() * polygons.size());
  }
  std::vector<Bounds2D> bounds;
  if (positive_only) {
    bounds.reserve(polygons.size());
    for (const Polygon2D& polygon : polygons) {
      bounds.push_back(bounds_for_polygon(polygon));
    }
  }
#if RTDL_ORACLE_HAS_GEOS
  GeosPreparedPolygonSet geos(polygons);
  for (const Point2D& point : points) {
    for (size_t polygon_index = 0; polygon_index < polygons.size(); ++polygon_index) {
      if (positive_only) {
        const Bounds2D& b = bounds[polygon_index];
        if (point.p.x < b.min_x || point.p.x > b.max_x || point.p.y < b.min_y || point.p.y > b.max_y) {
          continue;
        }
      }
      const bool contains = geos.covers(polygon_index, point.p.x, point.p.y);
      if (positive_only && !contains) {
        continue;
      }
      rows.push_back({point.id, polygons[polygon_index].id, contains ? 1u : 0u});
    }
  }
  return rows;
#endif
  for (const Point2D& point : points) {
    for (size_t polygon_index = 0; polygon_index < polygons.size(); ++polygon_index) {
      const Polygon2D& polygon = polygons[polygon_index];
      if (positive_only) {
        const Bounds2D& b = bounds[polygon_index];
        if (point.p.x < b.min_x || point.p.x > b.max_x || point.p.y < b.min_y || point.p.y > b.max_y) {
          continue;
        }
      }
      const bool contains = point_in_polygon(point.p.x, point.p.y, polygon.vertices);
      if (positive_only && !contains) {
        continue;
      }
      rows.push_back({point.id, polygon.id, contains ? 1u : 0u});
    }
  }
  return rows;
}

bool point_in_triangle(double x, double y, const Triangle2D& triangle) {
  Vec2 v0 = sub(triangle.c, triangle.a);
  Vec2 v1 = sub(triangle.b, triangle.a);
  Vec2 v2 {x - triangle.a.x, y - triangle.a.y};

  double dot00 = v0.x * v0.x + v0.y * v0.y;
  double dot01 = v0.x * v1.x + v0.y * v1.y;
  double dot02 = v0.x * v2.x + v0.y * v2.y;
  double dot11 = v1.x * v1.x + v1.y * v1.y;
  double dot12 = v1.x * v2.x + v1.y * v2.y;

  double denom = dot00 * dot11 - dot01 * dot01;
  if (std::fabs(denom) < kPointEps) {
    return false;
  }

  double inv = 1.0 / denom;
  double u = (dot11 * dot02 - dot01 * dot12) * inv;
  double v = (dot00 * dot12 - dot01 * dot02) * inv;
  return u >= 0.0 && v >= 0.0 && (u + v) <= 1.0;
}

bool finite_ray_hits_triangle(const RayQuery2D& ray, const Triangle2D& triangle) {
  Vec2 end {ray.o.x + ray.d.x * ray.tmax, ray.o.y + ray.d.y * ray.tmax};
  Segment2D ray_segment {ray.id, ray.o, end};

  if (point_in_triangle(ray.o.x, ray.o.y, triangle) || point_in_triangle(end.x, end.y, triangle)) {
    return true;
  }

  Segment2D edges[3] = {
      {triangle.id, triangle.a, triangle.b},
      {triangle.id, triangle.b, triangle.c},
      {triangle.id, triangle.c, triangle.a},
  };
  for (const Segment2D& edge : edges) {
    if (segment_intersection(ray_segment, edge, nullptr)) {
      return true;
    }
  }
  return false;
}

bool segment_hits_polygon(const Segment2D& segment, const Polygon2D& polygon) {
  if (point_in_polygon(segment.a.x, segment.a.y, polygon.vertices)) {
    return true;
  }
  if (point_in_polygon(segment.b.x, segment.b.y, polygon.vertices)) {
    return true;
  }
  for (size_t i = 0; i < polygon.vertices.size(); ++i) {
    Segment2D edge {polygon.id, polygon.vertices[i], polygon.vertices[(i + 1) % polygon.vertices.size()]};
    if (segment_intersection(segment, edge, nullptr)) {
      return true;
    }
  }
  return false;
}

double point_segment_distance(const Point2D& point, const Segment2D& segment) {
  Vec2 v = sub(segment.b, segment.a);
  Vec2 w = sub(point.p, segment.a);
  double denom = v.x * v.x + v.y * v.y;
  if (denom < kDegenerateDistanceEps) {
    Vec2 d = sub(point.p, segment.a);
    return std::sqrt(d.x * d.x + d.y * d.y);
  }
  double t = (w.x * v.x + w.y * v.y) / denom;
  t = std::max(0.0, std::min(1.0, t));
  Vec2 projection {segment.a.x + t * v.x, segment.a.y + t * v.y};
  Vec2 d = sub(point.p, projection);
  return std::sqrt(d.x * d.x + d.y * d.y);
}

}  // namespace

extern "C" int rtdl_oracle_get_version(int* major_out, int* minor_out, int* patch_out) {
  if (major_out == nullptr || minor_out == nullptr || patch_out == nullptr) {
    return 1;
  }
  *major_out = 0;
  *minor_out = 1;
  *patch_out = 0;
  return 0;
}

extern "C" int rtdl_oracle_run_lsi(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    std::vector<RtdlLsiRow> rows = oracle_lsi(decode_segments(left, left_count), decode_segments(right, right_count));
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_oracle_run_pip(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    uint32_t positive_only,
    RtdlPipRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    std::vector<RtdlPipRow> rows = oracle_pip(
        decode_points(points, point_count),
        decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count),
        positive_only != 0u);
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_oracle_run_overlay(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlOverlayRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Polygon2D> left_values = decode_polygons(left_polygons, left_count, left_vertices_xy, left_vertex_xy_count);
    std::vector<Polygon2D> right_values = decode_polygons(right_polygons, right_count, right_vertices_xy, right_vertex_xy_count);

    std::vector<Segment2D> left_segments = segments_from_polygons(left_values);
    std::vector<Segment2D> right_segments = segments_from_polygons(right_values);
    std::vector<RtdlLsiRow> lsi_hits = oracle_lsi(left_segments, right_segments);

    std::vector<Point2D> left_points;
    left_points.reserve(left_values.size());
    for (const Polygon2D& polygon : left_values) {
      left_points.push_back({polygon.id, polygon.vertices[0]});
    }

    std::vector<Point2D> right_points;
    right_points.reserve(right_values.size());
    for (const Polygon2D& polygon : right_values) {
      right_points.push_back({polygon.id, polygon.vertices[0]});
    }

    std::vector<RtdlPipRow> left_in_right = oracle_pip(left_points, right_values, false);
    std::vector<RtdlPipRow> right_in_left = oracle_pip(right_points, left_values, false);

    std::vector<RtdlOverlayRow> rows;
    rows.reserve(left_values.size() * right_values.size());
    for (const Polygon2D& left_polygon : left_values) {
      for (const Polygon2D& right_polygon : right_values) {
        uint32_t requires_lsi = 0;
        for (const RtdlLsiRow& hit : lsi_hits) {
          if (hit.left_id == left_polygon.id && hit.right_id == right_polygon.id) {
            requires_lsi = 1;
            break;
          }
        }

        uint32_t requires_pip = 0;
        for (const RtdlPipRow& hit : left_in_right) {
          if (hit.point_id == left_polygon.id && hit.polygon_id == right_polygon.id && hit.contains == 1u) {
            requires_pip = 1;
            break;
          }
        }
        if (requires_pip == 0) {
          for (const RtdlPipRow& hit : right_in_left) {
            if (hit.point_id == right_polygon.id && hit.polygon_id == left_polygon.id && hit.contains == 1u) {
              requires_pip = 1;
              break;
            }
          }
        }

        rows.push_back({left_polygon.id, right_polygon.id, requires_lsi, requires_pip});
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_oracle_run_ray_hitcount(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<RayQuery2D> ray_values = decode_rays(rays, ray_count);
    std::vector<Triangle2D> triangle_values = decode_triangles(triangles, triangle_count);
    std::vector<RtdlRayHitCountRow> rows;
    rows.reserve(ray_values.size());
    for (const RayQuery2D& ray : ray_values) {
      uint32_t hit_count = 0;
      for (const Triangle2D& triangle : triangle_values) {
        if (finite_ray_hits_triangle(ray, triangle)) {
          hit_count += 1;
        }
      }
      rows.push_back({ray.id, hit_count});
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_oracle_run_segment_polygon_hitcount(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Segment2D> segment_values = decode_segments(segments, segment_count);
    std::vector<Polygon2D> polygon_values = decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count);
    std::vector<Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_values.size());
    for (const Polygon2D& polygon : polygon_values) {
      polygon_bounds.push_back(bounds_for_polygon(polygon));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_values.size(), 0);
    size_t stamp = 1;
    std::vector<RtdlSegmentPolygonHitCountRow> rows;
    rows.reserve(segment_values.size());
    for (const Segment2D& segment : segment_values) {
      const Bounds2D seg_bounds = bounds_for_segment(segment);
      const size_t bucket_count = bucket_index.buckets.size();
      size_t first = 0;
      size_t last = 0;
      if (bucket_count > 0) {
        first = static_cast<size_t>(std::clamp(
            static_cast<long long>(std::floor((seg_bounds.min_x - bucket_index.origin_x) / bucket_index.bucket_width)),
            0LL,
            static_cast<long long>(bucket_count - 1)));
        last = static_cast<size_t>(std::clamp(
            static_cast<long long>(std::floor((seg_bounds.max_x - bucket_index.origin_x) / bucket_index.bucket_width)),
            0LL,
            static_cast<long long>(bucket_count - 1)));
      }
      uint32_t hit_count = 0;
      for (size_t bucket_id = first; bucket_id <= last && bucket_count > 0; ++bucket_id) {
        for (size_t polygon_index : bucket_index.buckets[bucket_id]) {
          if (seen[polygon_index] == stamp) {
            continue;
          }
          seen[polygon_index] = stamp;
          if (!bounds_overlap(seg_bounds, polygon_bounds[polygon_index])) {
            continue;
          }
          const Polygon2D& polygon = polygon_values[polygon_index];
          if (segment_hits_polygon(segment, polygon)) {
            hit_count += 1;
          }
        }
      }
      rows.push_back({segment.id, hit_count});
      stamp += 1;
      if (stamp == 0) {
        std::fill(seen.begin(), seen.end(), 0);
        stamp = 1;
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_oracle_run_segment_polygon_anyhit_rows(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Segment2D> segment_values = decode_segments(segments, segment_count);
    std::vector<Polygon2D> polygon_values = decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count);
    std::vector<Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_values.size());
    for (const Polygon2D& polygon : polygon_values) {
      polygon_bounds.push_back(bounds_for_polygon(polygon));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_values.size(), 0);
    size_t stamp = 1;
    std::vector<RtdlSegmentPolygonAnyHitRow> rows;
    for (const Segment2D& segment : segment_values) {
      const Bounds2D seg_bounds = bounds_for_segment(segment);
      const size_t bucket_count = bucket_index.buckets.size();
      size_t first = 0;
      size_t last = 0;
      if (bucket_count > 0) {
        first = static_cast<size_t>(std::clamp(
            static_cast<long long>(std::floor((seg_bounds.min_x - bucket_index.origin_x) / bucket_index.bucket_width)),
            0LL,
            static_cast<long long>(bucket_count - 1)));
        last = static_cast<size_t>(std::clamp(
            static_cast<long long>(std::floor((seg_bounds.max_x - bucket_index.origin_x) / bucket_index.bucket_width)),
            0LL,
            static_cast<long long>(bucket_count - 1)));
      }
      for (size_t bucket_id = first; bucket_id <= last && bucket_count > 0; ++bucket_id) {
        for (size_t polygon_index : bucket_index.buckets[bucket_id]) {
          if (seen[polygon_index] == stamp) {
            continue;
          }
          seen[polygon_index] = stamp;
          if (!bounds_overlap(seg_bounds, polygon_bounds[polygon_index])) {
            continue;
          }
          const Polygon2D& polygon = polygon_values[polygon_index];
          if (segment_hits_polygon(segment, polygon)) {
            rows.push_back({segment.id, polygon.id});
          }
        }
      }
      stamp += 1;
      if (stamp == 0) {
        std::fill(seen.begin(), seen.end(), 0);
        stamp = 1;
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_oracle_run_polygon_pair_overlap_area_rows(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlPolygonPairOverlapAreaRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Polygon2D> left_values =
        decode_polygons(left_polygons, left_count, left_vertices_xy, left_vertex_xy_count);
    std::vector<Polygon2D> right_values =
        decode_polygons(right_polygons, right_count, right_vertices_xy, right_vertex_xy_count);
    std::vector<Bounds2D> left_bounds;
    std::vector<Bounds2D> right_bounds;
    std::vector<std::vector<uint64_t>> left_cells;
    std::vector<std::vector<uint64_t>> right_cells;
    left_bounds.reserve(left_values.size());
    right_bounds.reserve(right_values.size());
    left_cells.reserve(left_values.size());
    right_cells.reserve(right_values.size());
    for (const Polygon2D& polygon : left_values) {
      left_bounds.push_back(bounds_for_polygon(polygon));
      left_cells.push_back(polygon_unit_cells(polygon));
    }
    for (const Polygon2D& polygon : right_values) {
      right_bounds.push_back(bounds_for_polygon(polygon));
      right_cells.push_back(polygon_unit_cells(polygon));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(right_bounds);
    std::vector<size_t> seen(right_values.size(), 0);
    size_t stamp = 1;
    std::vector<RtdlPolygonPairOverlapAreaRow> rows;
    for (size_t left_index = 0; left_index < left_values.size(); ++left_index) {
      const Bounds2D& left_bound = left_bounds[left_index];
      const size_t bucket_count = bucket_index.buckets.size();
      size_t first = 0;
      size_t last = 0;
      if (bucket_count > 0) {
        first = static_cast<size_t>(std::clamp(
            static_cast<long long>(std::floor((left_bound.min_x - bucket_index.origin_x) / bucket_index.bucket_width)),
            0LL,
            static_cast<long long>(bucket_count - 1)));
        last = static_cast<size_t>(std::clamp(
            static_cast<long long>(std::floor((left_bound.max_x - bucket_index.origin_x) / bucket_index.bucket_width)),
            0LL,
            static_cast<long long>(bucket_count - 1)));
      }
      for (size_t bucket_id = first; bucket_id <= last && bucket_count > 0; ++bucket_id) {
        for (size_t right_index : bucket_index.buckets[bucket_id]) {
          if (seen[right_index] == stamp) {
            continue;
          }
          seen[right_index] = stamp;
          if (!bounds_overlap(left_bound, right_bounds[right_index])) {
            continue;
          }
          const uint32_t intersection_area = intersect_cell_sets(left_cells[left_index], right_cells[right_index]);
          if (intersection_area == 0) {
            continue;
          }
          const uint32_t left_area = static_cast<uint32_t>(left_cells[left_index].size());
          const uint32_t right_area = static_cast<uint32_t>(right_cells[right_index].size());
          rows.push_back({
              left_values[left_index].id,
              right_values[right_index].id,
              intersection_area,
              left_area,
              right_area,
              static_cast<uint32_t>(left_area + right_area - intersection_area),
          });
        }
      }
      stamp += 1;
      if (stamp == 0) {
        std::fill(seen.begin(), seen.end(), 0);
        stamp = 1;
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_oracle_run_point_nearest_segment(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point2D> point_values = decode_points(points, point_count);
    std::vector<Segment2D> segment_values = decode_segments(segments, segment_count);
    std::vector<RtdlPointNearestSegmentRow> rows;
    rows.reserve(point_values.size());
    for (const Point2D& point : point_values) {
      const Segment2D* best_segment = nullptr;
      double best_distance = 0.0;
      for (const Segment2D& segment : segment_values) {
        double distance = point_segment_distance(point, segment);
        if (best_segment == nullptr ||
            distance < best_distance - kPointEps ||
            (std::fabs(distance - best_distance) <= kPointEps && segment.id < best_segment->id)) {
          best_segment = &segment;
          best_distance = distance;
        }
      }
      if (best_segment != nullptr) {
        rows.push_back({point.id, best_segment->id, best_distance});
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" void rtdl_oracle_free_rows(void* rows) {
  std::free(rows);
}
