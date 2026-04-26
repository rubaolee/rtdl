#include "rtdl_oracle_internal.h"

#include <map>
#include <set>

#if defined(_WIN32)
#  define RTDL_ORACLE_EXPORT extern "C" __declspec(dllexport)
#else
#  define RTDL_ORACLE_EXPORT extern "C"
#endif

namespace rtdl::oracle {

namespace {

constexpr uint32_t kDbKindInt64 = 1;
constexpr uint32_t kDbKindFloat64 = 2;
constexpr uint32_t kDbKindBool = 3;
constexpr uint32_t kDbKindText = 4;

constexpr uint32_t kDbOpEq = 1;
constexpr uint32_t kDbOpLt = 2;
constexpr uint32_t kDbOpLe = 3;
constexpr uint32_t kDbOpGt = 4;
constexpr uint32_t kDbOpGe = 5;
constexpr uint32_t kDbOpBetween = 6;

bool db_scalar_is_numeric(const RtdlDbScalar& value) {
  return value.kind == kDbKindInt64 || value.kind == kDbKindFloat64 || value.kind == kDbKindBool;
}

double db_scalar_as_double(const RtdlDbScalar& value) {
  if (value.kind == kDbKindInt64) {
    return static_cast<double>(value.int_value);
  }
  if (value.kind == kDbKindFloat64) {
    return value.double_value;
  }
  if (value.kind == kDbKindBool) {
    return value.int_value != 0 ? 1.0 : 0.0;
  }
  throw std::runtime_error("non-numeric DB scalar cannot be used in numeric comparison");
}

const char* db_scalar_text(const RtdlDbScalar& value) {
  return value.string_value == nullptr ? "" : value.string_value;
}

int db_scalar_compare(const RtdlDbScalar& left, const RtdlDbScalar& right) {
  if (db_scalar_is_numeric(left) && db_scalar_is_numeric(right)) {
    double left_value = db_scalar_as_double(left);
    double right_value = db_scalar_as_double(right);
    if (left_value < right_value) {
      return -1;
    }
    if (left_value > right_value) {
      return 1;
    }
    return 0;
  }
  if (left.kind == kDbKindText && right.kind == kDbKindText) {
    int cmp = std::strcmp(db_scalar_text(left), db_scalar_text(right));
    if (cmp < 0) {
      return -1;
    }
    if (cmp > 0) {
      return 1;
    }
    return 0;
  }
  throw std::runtime_error("DB scalar comparison kind mismatch");
}

size_t db_find_field_index(const RtdlDbField* fields, size_t field_count, const char* name) {
  if (name == nullptr) {
    throw std::runtime_error("DB clause field name must not be null");
  }
  for (size_t index = 0; index < field_count; ++index) {
    const char* candidate = fields[index].name == nullptr ? "" : fields[index].name;
    if (std::strcmp(candidate, name) == 0) {
      return index;
    }
  }
  throw std::runtime_error(std::string("unknown DB field: ") + name);
}

const RtdlDbScalar& db_row_value(
    const RtdlDbScalar* row_values,
    size_t row_index,
    size_t field_count,
    size_t field_index) {
  return row_values[row_index * field_count + field_index];
}

bool db_row_matches(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_index,
    const RtdlDbClause& clause) {
  size_t field_index = db_find_field_index(fields, field_count, clause.field);
  const RtdlDbScalar& row_value = db_row_value(row_values, row_index, field_count, field_index);
  if (clause.op == kDbOpEq) {
    return db_scalar_compare(row_value, clause.value) == 0;
  }
  if (clause.op == kDbOpLt) {
    return db_scalar_compare(row_value, clause.value) < 0;
  }
  if (clause.op == kDbOpLe) {
    return db_scalar_compare(row_value, clause.value) <= 0;
  }
  if (clause.op == kDbOpGt) {
    return db_scalar_compare(row_value, clause.value) > 0;
  }
  if (clause.op == kDbOpGe) {
    return db_scalar_compare(row_value, clause.value) >= 0;
  }
  if (clause.op == kDbOpBetween) {
    return db_scalar_compare(row_value, clause.value) >= 0 &&
           db_scalar_compare(row_value, clause.value_hi) <= 0;
  }
  throw std::runtime_error("unsupported DB predicate operator");
}

std::vector<size_t> candidate_polygon_indexes(
    const std::vector<rtdl::oracle::Polygon2D>& polygons,
    uint32_t polygon_id) {
  std::vector<size_t> indexes;
  for (size_t index = 0; index < polygons.size(); ++index) {
    if (polygons[index].id == polygon_id) {
      indexes.push_back(index);
    }
  }
  return indexes;
}

std::set<std::pair<uint32_t, uint32_t>> normalize_polygon_pair_candidates(
    const RtdlPolygonPairCandidate* candidates,
    size_t candidate_count) {
  std::set<std::pair<uint32_t, uint32_t>> pairs;
  for (size_t index = 0; index < candidate_count; ++index) {
    pairs.insert({candidates[index].left_polygon_id, candidates[index].right_polygon_id});
  }
  return pairs;
}

std::vector<uint64_t> intersect_cell_values(
    const std::vector<uint64_t>& left,
    const std::vector<uint64_t>& right) {
  std::vector<uint64_t> cells;
  size_t left_index = 0;
  size_t right_index = 0;
  while (left_index < left.size() && right_index < right.size()) {
    if (left[left_index] == right[right_index]) {
      cells.push_back(left[left_index]);
      left_index += 1;
      right_index += 1;
    } else if (left[left_index] < right[right_index]) {
      left_index += 1;
    } else {
      right_index += 1;
    }
  }
  return cells;
}

}  // namespace

}  // namespace rtdl::oracle

RTDL_ORACLE_EXPORT int rtdl_oracle_get_version(int* major_out, int* minor_out, int* patch_out) {
  if (major_out == nullptr || minor_out == nullptr || patch_out == nullptr) {
    return 1;
  }
  *major_out = 0;
  *minor_out = 1;
  *patch_out = 0;
  return 0;
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_lsi(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    std::vector<RtdlLsiRow> rows = rtdl::oracle::oracle_lsi(
        rtdl::oracle::decode_segments(left, left_count),
        rtdl::oracle::decode_segments(right, right_count));
    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_pip(
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
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    std::vector<RtdlPipRow> rows = rtdl::oracle::oracle_pip(
        rtdl::oracle::decode_points(points, point_count),
        rtdl::oracle::decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count),
        positive_only != 0u);
    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_overlay(
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
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Polygon2D> left_values =
        rtdl::oracle::decode_polygons(left_polygons, left_count, left_vertices_xy, left_vertex_xy_count);
    std::vector<rtdl::oracle::Polygon2D> right_values =
        rtdl::oracle::decode_polygons(right_polygons, right_count, right_vertices_xy, right_vertex_xy_count);

    std::vector<rtdl::oracle::Segment2D> left_segments = rtdl::oracle::segments_from_polygons(left_values);
    std::vector<rtdl::oracle::Segment2D> right_segments = rtdl::oracle::segments_from_polygons(right_values);
    std::vector<RtdlLsiRow> lsi_hits = rtdl::oracle::oracle_lsi(left_segments, right_segments);

    std::vector<rtdl::oracle::Point2D> left_points;
    left_points.reserve(left_values.size());
    for (const rtdl::oracle::Polygon2D& polygon : left_values) {
      left_points.push_back({polygon.id, polygon.vertices[0]});
    }

    std::vector<rtdl::oracle::Point2D> right_points;
    right_points.reserve(right_values.size());
    for (const rtdl::oracle::Polygon2D& polygon : right_values) {
      right_points.push_back({polygon.id, polygon.vertices[0]});
    }

    std::vector<RtdlPipRow> left_in_right = rtdl::oracle::oracle_pip(left_points, right_values, false);
    std::vector<RtdlPipRow> right_in_left = rtdl::oracle::oracle_pip(right_points, left_values, false);

    std::vector<RtdlOverlayRow> rows;
    rows.reserve(left_values.size() * right_values.size());
    for (const rtdl::oracle::Polygon2D& left_polygon : left_values) {
      for (const rtdl::oracle::Polygon2D& right_polygon : right_values) {
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

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_ray_hitcount(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::RayQuery2D> ray_values = rtdl::oracle::decode_rays(rays, ray_count);
    std::vector<rtdl::oracle::Triangle2D> triangle_values = rtdl::oracle::decode_triangles(triangles, triangle_count);
    std::vector<RtdlRayHitCountRow> rows;
    rows.reserve(ray_values.size());
    for (const rtdl::oracle::RayQuery2D& ray : ray_values) {
      uint32_t hit_count = 0;
      for (const rtdl::oracle::Triangle2D& triangle : triangle_values) {
        if (rtdl::oracle::finite_ray_hits_triangle(ray, triangle)) {
          hit_count += 1;
        }
      }
      rows.push_back({ray.id, hit_count});
    }

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_segment_polygon_hitcount(
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
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Segment2D> segment_values = rtdl::oracle::decode_segments(segments, segment_count);
    std::vector<rtdl::oracle::Polygon2D> polygon_values =
        rtdl::oracle::decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count);
    std::vector<rtdl::oracle::Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_values.size());
    for (const rtdl::oracle::Polygon2D& polygon : polygon_values) {
      polygon_bounds.push_back(rtdl::oracle::bounds_for_polygon(polygon));
    }
    const rtdl::oracle::PolygonBucketIndex bucket_index =
        rtdl::oracle::build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_values.size(), 0);
    size_t stamp = 1;
    std::vector<RtdlSegmentPolygonHitCountRow> rows;
    rows.reserve(segment_values.size());
    for (const rtdl::oracle::Segment2D& segment : segment_values) {
      const rtdl::oracle::Bounds2D seg_bounds = rtdl::oracle::bounds_for_segment(segment);
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
          if (!rtdl::oracle::bounds_overlap(seg_bounds, polygon_bounds[polygon_index])) {
            continue;
          }
          const rtdl::oracle::Polygon2D& polygon = polygon_values[polygon_index];
          if (rtdl::oracle::segment_hits_polygon(segment, polygon)) {
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

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_segment_polygon_anyhit_rows(
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
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Segment2D> segment_values = rtdl::oracle::decode_segments(segments, segment_count);
    std::vector<rtdl::oracle::Polygon2D> polygon_values =
        rtdl::oracle::decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count);
    std::vector<rtdl::oracle::Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_values.size());
    for (const rtdl::oracle::Polygon2D& polygon : polygon_values) {
      polygon_bounds.push_back(rtdl::oracle::bounds_for_polygon(polygon));
    }
    const rtdl::oracle::PolygonBucketIndex bucket_index =
        rtdl::oracle::build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_values.size(), 0);
    size_t stamp = 1;
    std::vector<RtdlSegmentPolygonAnyHitRow> rows;
    for (const rtdl::oracle::Segment2D& segment : segment_values) {
      const rtdl::oracle::Bounds2D seg_bounds = rtdl::oracle::bounds_for_segment(segment);
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
          if (!rtdl::oracle::bounds_overlap(seg_bounds, polygon_bounds[polygon_index])) {
            continue;
          }
          const rtdl::oracle::Polygon2D& polygon = polygon_values[polygon_index];
          if (rtdl::oracle::segment_hits_polygon(segment, polygon)) {
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

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_polygon_pair_overlap_area_rows(
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
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Polygon2D> left_values =
        rtdl::oracle::decode_polygons(left_polygons, left_count, left_vertices_xy, left_vertex_xy_count);
    std::vector<rtdl::oracle::Polygon2D> right_values =
        rtdl::oracle::decode_polygons(right_polygons, right_count, right_vertices_xy, right_vertex_xy_count);
    std::vector<rtdl::oracle::Bounds2D> left_bounds;
    std::vector<rtdl::oracle::Bounds2D> right_bounds;
    std::vector<std::vector<uint64_t>> left_cells;
    std::vector<std::vector<uint64_t>> right_cells;
    left_bounds.reserve(left_values.size());
    right_bounds.reserve(right_values.size());
    left_cells.reserve(left_values.size());
    right_cells.reserve(right_values.size());
    for (const rtdl::oracle::Polygon2D& polygon : left_values) {
      left_bounds.push_back(rtdl::oracle::bounds_for_polygon(polygon));
      left_cells.push_back(rtdl::oracle::polygon_unit_cells(polygon));
    }
    for (const rtdl::oracle::Polygon2D& polygon : right_values) {
      right_bounds.push_back(rtdl::oracle::bounds_for_polygon(polygon));
      right_cells.push_back(rtdl::oracle::polygon_unit_cells(polygon));
    }
    const rtdl::oracle::PolygonBucketIndex bucket_index =
        rtdl::oracle::build_polygon_bucket_index(right_bounds);
    std::vector<size_t> seen(right_values.size(), 0);
    size_t stamp = 1;
    std::vector<RtdlPolygonPairOverlapAreaRow> rows;
    for (size_t left_index = 0; left_index < left_values.size(); ++left_index) {
      const rtdl::oracle::Bounds2D& left_bound = left_bounds[left_index];
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
          if (!rtdl::oracle::bounds_overlap(left_bound, right_bounds[right_index])) {
            continue;
          }
          const uint32_t intersection_area =
              rtdl::oracle::intersect_cell_sets(left_cells[left_index], right_cells[right_index]);
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

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_polygon_set_jaccard(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlPolygonSetJaccardRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Polygon2D> left_values =
        rtdl::oracle::decode_polygons(left_polygons, left_count, left_vertices_xy, left_vertex_xy_count);
    std::vector<rtdl::oracle::Polygon2D> right_values =
        rtdl::oracle::decode_polygons(right_polygons, right_count, right_vertices_xy, right_vertex_xy_count);
    const std::vector<uint64_t> left_cells = rtdl::oracle::polygon_set_unit_cells(left_values);
    const std::vector<uint64_t> right_cells = rtdl::oracle::polygon_set_unit_cells(right_values);
    const uint32_t intersection_area = rtdl::oracle::intersect_cell_sets(left_cells, right_cells);
    const uint32_t left_area = static_cast<uint32_t>(left_cells.size());
    const uint32_t right_area = static_cast<uint32_t>(right_cells.size());
    const uint32_t union_area = static_cast<uint32_t>(left_area + right_area - intersection_area);
    const double jaccard_similarity =
        union_area == 0 ? 0.0 : static_cast<double>(intersection_area) / static_cast<double>(union_area);

    std::vector<RtdlPolygonSetJaccardRow> rows;
    rows.push_back({intersection_area, left_area, right_area, union_area, jaccard_similarity});
    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_refine_polygon_pair_overlap_area_rows_for_pairs(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    const RtdlPolygonPairCandidate* candidates,
    size_t candidate_count,
    RtdlPolygonPairOverlapAreaRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (candidate_count > 0 && candidates == nullptr) {
      throw std::runtime_error("candidate pointer must not be null when candidate_count is non-zero");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Polygon2D> left_values =
        rtdl::oracle::decode_polygons(left_polygons, left_count, left_vertices_xy, left_vertex_xy_count);
    std::vector<rtdl::oracle::Polygon2D> right_values =
        rtdl::oracle::decode_polygons(right_polygons, right_count, right_vertices_xy, right_vertex_xy_count);
    std::vector<std::vector<uint64_t>> left_cells;
    std::vector<std::vector<uint64_t>> right_cells;
    left_cells.reserve(left_values.size());
    right_cells.reserve(right_values.size());
    for (const rtdl::oracle::Polygon2D& polygon : left_values) {
      left_cells.push_back(rtdl::oracle::polygon_unit_cells(polygon));
    }
    for (const rtdl::oracle::Polygon2D& polygon : right_values) {
      right_cells.push_back(rtdl::oracle::polygon_unit_cells(polygon));
    }
    const std::set<std::pair<uint32_t, uint32_t>> candidate_pairs =
        rtdl::oracle::normalize_polygon_pair_candidates(candidates, candidate_count);
    std::vector<RtdlPolygonPairOverlapAreaRow> rows;
    for (size_t left_index = 0; left_index < left_values.size(); ++left_index) {
      const uint32_t left_id = left_values[left_index].id;
      const uint32_t left_area = static_cast<uint32_t>(left_cells[left_index].size());
      for (size_t right_index = 0; right_index < right_values.size(); ++right_index) {
        const uint32_t right_id = right_values[right_index].id;
        if (candidate_pairs.find({left_id, right_id}) == candidate_pairs.end()) {
          continue;
        }
        const uint32_t intersection_area =
            rtdl::oracle::intersect_cell_sets(left_cells[left_index], right_cells[right_index]);
        if (intersection_area == 0) {
          continue;
        }
        const uint32_t right_area = static_cast<uint32_t>(right_cells[right_index].size());
        rows.push_back({
            left_id,
            right_id,
            intersection_area,
            left_area,
            right_area,
            static_cast<uint32_t>(left_area + right_area - intersection_area),
        });
      }
    }
    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_refine_polygon_set_jaccard_for_pairs(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    const RtdlPolygonPairCandidate* candidates,
    size_t candidate_count,
    RtdlPolygonSetJaccardRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (candidate_count > 0 && candidates == nullptr) {
      throw std::runtime_error("candidate pointer must not be null when candidate_count is non-zero");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Polygon2D> left_values =
        rtdl::oracle::decode_polygons(left_polygons, left_count, left_vertices_xy, left_vertex_xy_count);
    std::vector<rtdl::oracle::Polygon2D> right_values =
        rtdl::oracle::decode_polygons(right_polygons, right_count, right_vertices_xy, right_vertex_xy_count);
    std::vector<std::vector<uint64_t>> left_cells_by_index;
    std::vector<std::vector<uint64_t>> right_cells_by_index;
    left_cells_by_index.reserve(left_values.size());
    right_cells_by_index.reserve(right_values.size());
    for (const rtdl::oracle::Polygon2D& polygon : left_values) {
      left_cells_by_index.push_back(rtdl::oracle::polygon_unit_cells(polygon));
    }
    for (const rtdl::oracle::Polygon2D& polygon : right_values) {
      right_cells_by_index.push_back(rtdl::oracle::polygon_unit_cells(polygon));
    }
    const std::vector<uint64_t> left_cells = rtdl::oracle::polygon_set_unit_cells(left_values);
    const std::vector<uint64_t> right_cells = rtdl::oracle::polygon_set_unit_cells(right_values);

    std::vector<uint64_t> intersection_cells;
    const std::set<std::pair<uint32_t, uint32_t>> candidate_pairs =
        rtdl::oracle::normalize_polygon_pair_candidates(candidates, candidate_count);
    for (const auto& [left_id, right_id] : candidate_pairs) {
      const std::vector<size_t> left_indexes =
          rtdl::oracle::candidate_polygon_indexes(left_values, left_id);
      const std::vector<size_t> right_indexes =
          rtdl::oracle::candidate_polygon_indexes(right_values, right_id);
      for (size_t left_index : left_indexes) {
        for (size_t right_index : right_indexes) {
          std::vector<uint64_t> pair_cells = rtdl::oracle::intersect_cell_values(
              left_cells_by_index[left_index],
              right_cells_by_index[right_index]);
          intersection_cells.insert(intersection_cells.end(), pair_cells.begin(), pair_cells.end());
        }
      }
    }
    std::sort(intersection_cells.begin(), intersection_cells.end());
    intersection_cells.erase(std::unique(intersection_cells.begin(), intersection_cells.end()), intersection_cells.end());

    const uint32_t intersection_area = static_cast<uint32_t>(intersection_cells.size());
    const uint32_t left_area = static_cast<uint32_t>(left_cells.size());
    const uint32_t right_area = static_cast<uint32_t>(right_cells.size());
    const uint32_t union_area = static_cast<uint32_t>(left_area + right_area - intersection_area);
    const double jaccard_similarity =
        union_area == 0 ? 0.0 : static_cast<double>(intersection_area) / static_cast<double>(union_area);

    std::vector<RtdlPolygonSetJaccardRow> rows;
    rows.push_back({intersection_area, left_area, right_area, union_area, jaccard_similarity});
    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_point_nearest_segment(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Point2D> point_values = rtdl::oracle::decode_points(points, point_count);
    std::vector<rtdl::oracle::Segment2D> segment_values = rtdl::oracle::decode_segments(segments, segment_count);
    std::vector<RtdlPointNearestSegmentRow> rows;
    rows.reserve(point_values.size());
    for (const rtdl::oracle::Point2D& point : point_values) {
      const rtdl::oracle::Segment2D* best_segment = nullptr;
      double best_distance = 0.0;
      for (const rtdl::oracle::Segment2D& segment : segment_values) {
        double distance = rtdl::oracle::point_segment_distance(point, segment);
        if (best_segment == nullptr ||
            distance < best_distance - rtdl::oracle::kPointEps ||
            (std::fabs(distance - best_distance) <= rtdl::oracle::kPointEps &&
             segment.id < best_segment->id)) {
          best_segment = &segment;
          best_distance = distance;
        }
      }
      if (best_segment != nullptr) {
        rows.push_back({point.id, best_segment->id, best_distance});
      }
    }

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_fixed_radius_neighbors(
    const RtdlPoint* query_points,
    size_t query_point_count,
    const RtdlPoint* search_points,
    size_t search_point_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Point2D> query_values = rtdl::oracle::decode_points(query_points, query_point_count);
    std::vector<rtdl::oracle::Point2D> search_values = rtdl::oracle::decode_points(search_points, search_point_count);
    const double radius_sq = radius * radius;
    std::vector<RtdlFixedRadiusNeighborRow> rows;
    for (const rtdl::oracle::Point2D& query_point : query_values) {
      std::vector<RtdlFixedRadiusNeighborRow> query_rows;
      for (const rtdl::oracle::Point2D& search_point : search_values) {
        const double dx = search_point.p.x - query_point.p.x;
        const double dy = search_point.p.y - query_point.p.y;
        const double distance_sq = dx * dx + dy * dy;
        if (distance_sq > radius_sq) {
          continue;
        }
        query_rows.push_back({query_point.id, search_point.id, std::sqrt(distance_sq)});
      }
      std::sort(
          query_rows.begin(),
          query_rows.end(),
          [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
            if (left.distance < right.distance - rtdl::oracle::kPointEps) {
              return true;
            }
            if (right.distance < left.distance - rtdl::oracle::kPointEps) {
              return false;
            }
            return left.neighbor_id < right.neighbor_id;
          });
      if (query_rows.size() > static_cast<size_t>(k_max)) {
        query_rows.resize(static_cast<size_t>(k_max));
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(
        rows.begin(),
        rows.end(),
        [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
          return left.query_id < right.query_id;
        });

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* query_points,
    size_t query_point_count,
    const RtdlPoint3D* search_points,
    size_t search_point_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Point3D> query_values = rtdl::oracle::decode_points3d(query_points, query_point_count);
    std::vector<rtdl::oracle::Point3D> search_values = rtdl::oracle::decode_points3d(search_points, search_point_count);
    const double radius_sq = radius * radius;
    std::vector<RtdlFixedRadiusNeighborRow> rows;
    for (const rtdl::oracle::Point3D& query_point : query_values) {
      std::vector<RtdlFixedRadiusNeighborRow> query_rows;
      for (const rtdl::oracle::Point3D& search_point : search_values) {
        const double dx = search_point.p.x - query_point.p.x;
        const double dy = search_point.p.y - query_point.p.y;
        const double dz = search_point.p.z - query_point.p.z;
        const double distance_sq = dx * dx + dy * dy + dz * dz;
        if (distance_sq > radius_sq) {
          continue;
        }
        query_rows.push_back({query_point.id, search_point.id, std::sqrt(distance_sq)});
      }
      std::sort(
          query_rows.begin(),
          query_rows.end(),
          [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
            if (left.distance < right.distance - rtdl::oracle::kPointEps) {
              return true;
            }
            if (right.distance < left.distance - rtdl::oracle::kPointEps) {
              return false;
            }
            return left.neighbor_id < right.neighbor_id;
          });
      if (query_rows.size() > static_cast<size_t>(k_max)) {
        query_rows.resize(static_cast<size_t>(k_max));
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(
        rows.begin(),
        rows.end(),
        [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
          return left.query_id < right.query_id;
        });

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_summarize_fixed_radius_rows(
    const RtdlFixedRadiusNeighborRow* rows,
    size_t row_count,
    RtdlFixedRadiusSummaryRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (row_count > 0 && rows == nullptr) {
      throw std::runtime_error("fixed-radius rows pointer must not be null when row_count is non-zero");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<uint32_t> query_ids;
    std::vector<uint32_t> neighbor_ids;
    query_ids.reserve(row_count);
    neighbor_ids.reserve(row_count);
    for (size_t index = 0; index < row_count; ++index) {
      query_ids.push_back(rows[index].query_id);
      neighbor_ids.push_back(rows[index].neighbor_id);
    }
    std::sort(query_ids.begin(), query_ids.end());
    query_ids.erase(std::unique(query_ids.begin(), query_ids.end()), query_ids.end());
    std::sort(neighbor_ids.begin(), neighbor_ids.end());
    neighbor_ids.erase(std::unique(neighbor_ids.begin(), neighbor_ids.end()), neighbor_ids.end());

    std::vector<RtdlFixedRadiusSummaryRow> summary;
    summary.push_back({
        static_cast<uint32_t>(row_count),
        static_cast<uint32_t>(query_ids.size()),
        static_cast<uint32_t>(neighbor_ids.size()),
    });
    *rows_out = rtdl::oracle::copy_rows_out(summary);
    *row_count_out = summary.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_knn_rows(
    const RtdlPoint* query_points,
    size_t query_point_count,
    const RtdlPoint* search_points,
    size_t search_point_count,
    uint32_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Point2D> query_values = rtdl::oracle::decode_points(query_points, query_point_count);
    std::vector<rtdl::oracle::Point2D> search_values = rtdl::oracle::decode_points(search_points, search_point_count);
    std::vector<RtdlKnnNeighborRow> rows;
    for (const rtdl::oracle::Point2D& query_point : query_values) {
      std::vector<RtdlKnnNeighborRow> query_rows;
      query_rows.reserve(search_values.size());
      for (const rtdl::oracle::Point2D& search_point : search_values) {
        const double dx = search_point.p.x - query_point.p.x;
        const double dy = search_point.p.y - query_point.p.y;
        const double distance = std::sqrt(dx * dx + dy * dy);
        query_rows.push_back({query_point.id, search_point.id, distance, 0});
      }
      std::sort(
          query_rows.begin(),
          query_rows.end(),
          [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
            if (left.distance < right.distance - rtdl::oracle::kPointEps) {
              return true;
            }
            if (right.distance < left.distance - rtdl::oracle::kPointEps) {
              return false;
            }
            return left.neighbor_id < right.neighbor_id;
          });
      if (query_rows.size() > static_cast<size_t>(k)) {
        query_rows.resize(static_cast<size_t>(k));
      }
      for (size_t index = 0; index < query_rows.size(); ++index) {
        query_rows[index].neighbor_rank = static_cast<uint32_t>(index + 1);
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(
        rows.begin(),
        rows.end(),
        [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
          return left.query_id < right.query_id;
        });

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_knn_rows_3d(
    const RtdlPoint3D* query_points,
    size_t query_point_count,
    const RtdlPoint3D* search_points,
    size_t search_point_count,
    uint32_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Point3D> query_values = rtdl::oracle::decode_points3d(query_points, query_point_count);
    std::vector<rtdl::oracle::Point3D> search_values = rtdl::oracle::decode_points3d(search_points, search_point_count);
    std::vector<RtdlKnnNeighborRow> rows;
    for (const rtdl::oracle::Point3D& query_point : query_values) {
      std::vector<RtdlKnnNeighborRow> query_rows;
      query_rows.reserve(search_values.size());
      for (const rtdl::oracle::Point3D& search_point : search_values) {
        const double dx = search_point.p.x - query_point.p.x;
        const double dy = search_point.p.y - query_point.p.y;
        const double dz = search_point.p.z - query_point.p.z;
        const double distance = std::sqrt(dx * dx + dy * dy + dz * dz);
        query_rows.push_back({query_point.id, search_point.id, distance, 0});
      }
      std::sort(
          query_rows.begin(),
          query_rows.end(),
          [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
            if (left.distance < right.distance - rtdl::oracle::kPointEps) {
              return true;
            }
            if (right.distance < left.distance - rtdl::oracle::kPointEps) {
              return false;
            }
            return left.neighbor_id < right.neighbor_id;
          });
      if (query_rows.size() > static_cast<size_t>(k)) {
        query_rows.resize(static_cast<size_t>(k));
      }
      for (size_t index = 0; index < query_rows.size(); ++index) {
        query_rows[index].neighbor_rank = static_cast<uint32_t>(index + 1);
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(
        rows.begin(),
        rows.end(),
        [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
          return left.query_id < right.query_id;
        });

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_bounded_knn_rows(
    const RtdlPoint* query_points,
    size_t query_point_count,
    const RtdlPoint* search_points,
    size_t search_point_count,
    double radius,
    uint32_t k_max,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Point2D> query_values = rtdl::oracle::decode_points(query_points, query_point_count);
    std::vector<rtdl::oracle::Point2D> search_values = rtdl::oracle::decode_points(search_points, search_point_count);
    const double radius_sq = radius * radius;
    std::vector<RtdlKnnNeighborRow> rows;
    for (const rtdl::oracle::Point2D& query_point : query_values) {
      std::vector<RtdlKnnNeighborRow> query_rows;
      for (const rtdl::oracle::Point2D& search_point : search_values) {
        const double dx = search_point.p.x - query_point.p.x;
        const double dy = search_point.p.y - query_point.p.y;
        const double distance_sq = dx * dx + dy * dy;
        if (distance_sq > radius_sq) {
          continue;
        }
        query_rows.push_back({query_point.id, search_point.id, std::sqrt(distance_sq), 0});
      }
      std::sort(
          query_rows.begin(),
          query_rows.end(),
          [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
            if (left.distance < right.distance - rtdl::oracle::kPointEps) {
              return true;
            }
            if (right.distance < left.distance - rtdl::oracle::kPointEps) {
              return false;
            }
            return left.neighbor_id < right.neighbor_id;
          });
      if (query_rows.size() > static_cast<size_t>(k_max)) {
        query_rows.resize(static_cast<size_t>(k_max));
      }
      for (size_t index = 0; index < query_rows.size(); ++index) {
        query_rows[index].neighbor_rank = static_cast<uint32_t>(index + 1);
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(
        rows.begin(),
        rows.end(),
        [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
          return left.query_id < right.query_id;
        });

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_bounded_knn_rows_3d(
    const RtdlPoint3D* query_points,
    size_t query_point_count,
    const RtdlPoint3D* search_points,
    size_t search_point_count,
    double radius,
    uint32_t k_max,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<rtdl::oracle::Point3D> query_values = rtdl::oracle::decode_points3d(query_points, query_point_count);
    std::vector<rtdl::oracle::Point3D> search_values = rtdl::oracle::decode_points3d(search_points, search_point_count);
    const double radius_sq = radius * radius;
    std::vector<RtdlKnnNeighborRow> rows;
    for (const rtdl::oracle::Point3D& query_point : query_values) {
      std::vector<RtdlKnnNeighborRow> query_rows;
      for (const rtdl::oracle::Point3D& search_point : search_values) {
        const double dx = search_point.p.x - query_point.p.x;
        const double dy = search_point.p.y - query_point.p.y;
        const double dz = search_point.p.z - query_point.p.z;
        const double distance_sq = dx * dx + dy * dy + dz * dz;
        if (distance_sq > radius_sq) {
          continue;
        }
        query_rows.push_back({query_point.id, search_point.id, std::sqrt(distance_sq), 0});
      }
      std::sort(
          query_rows.begin(),
          query_rows.end(),
          [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
            if (left.distance < right.distance - rtdl::oracle::kPointEps) {
              return true;
            }
            if (right.distance < left.distance - rtdl::oracle::kPointEps) {
              return false;
            }
            return left.neighbor_id < right.neighbor_id;
          });
      if (query_rows.size() > static_cast<size_t>(k_max)) {
        query_rows.resize(static_cast<size_t>(k_max));
      }
      for (size_t index = 0; index < query_rows.size(); ++index) {
        query_rows[index].neighbor_rank = static_cast<uint32_t>(index + 1);
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(
        rows.begin(),
        rows.end(),
        [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
          return left.query_id < right.query_id;
        });

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_summarize_knn_rows(
    const RtdlKnnNeighborRow* rows,
    size_t row_count,
    RtdlKnnSummaryRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (row_count > 0 && rows == nullptr) {
      throw std::runtime_error("KNN rows pointer must not be null when row_count is non-zero");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<uint32_t> query_ids;
    query_ids.reserve(row_count);
    uint32_t max_neighbor_rank = 0;
    for (size_t index = 0; index < row_count; ++index) {
      query_ids.push_back(rows[index].query_id);
      max_neighbor_rank = std::max(max_neighbor_rank, rows[index].neighbor_rank);
    }
    std::sort(query_ids.begin(), query_ids.end());
    query_ids.erase(std::unique(query_ids.begin(), query_ids.end()), query_ids.end());

    std::vector<RtdlKnnSummaryRow> summary;
    summary.push_back({
        static_cast<uint32_t>(row_count),
        static_cast<uint32_t>(query_ids.size()),
        max_neighbor_rank,
    });
    *rows_out = rtdl::oracle::copy_rows_out(summary);
    *row_count_out = summary.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_bfs_expand(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t column_index_count,
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* visited,
    size_t visited_count,
    uint32_t dedupe,
    RtdlBfsExpandRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    if (row_offset_count == 0) {
      throw std::runtime_error("CSR graph row_offsets must not be empty");
    }
    if (row_offsets == nullptr) {
      throw std::runtime_error("CSR graph row_offsets pointer must not be null");
    }
    if (column_index_count > 0 && column_indices == nullptr) {
      throw std::runtime_error("CSR graph column_indices pointer must not be null");
    }
    if (frontier_count > 0 && frontier == nullptr) {
      throw std::runtime_error("frontier pointer must not be null when frontier_count > 0");
    }
    if (visited_count > 0 && visited == nullptr) {
      throw std::runtime_error("visited pointer must not be null when visited_count > 0");
    }
    if (row_offsets[0] != 0u) {
      throw std::runtime_error("CSR graph row_offsets must start at 0");
    }
    if (row_offsets[row_offset_count - 1] != column_index_count) {
      throw std::runtime_error("CSR graph final row_offset must equal edge_count");
    }

    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    for (size_t index = 1; index < row_offset_count; ++index) {
      if (row_offsets[index] < row_offsets[index - 1]) {
        throw std::runtime_error("CSR graph row_offsets must be non-decreasing");
      }
    }
    for (size_t index = 0; index < column_index_count; ++index) {
      if (column_indices[index] >= vertex_count) {
        throw std::runtime_error("CSR graph column_indices must be valid vertex IDs");
      }
    }

    std::vector<uint8_t> visited_flags(vertex_count, 0);
    for (size_t index = 0; index < visited_count; ++index) {
      if (visited[index] >= vertex_count) {
        throw std::runtime_error("visited vertex_id must be a valid graph vertex");
      }
      visited_flags[visited[index]] = 1;
    }

    std::vector<uint8_t> discovered_flags(vertex_count, 0);
    std::vector<RtdlBfsExpandRow> rows;
    for (size_t index = 0; index < frontier_count; ++index) {
      const RtdlFrontierVertex frontier_vertex = frontier[index];
      if (frontier_vertex.vertex_id >= vertex_count) {
        throw std::runtime_error("frontier vertex_id must be a valid graph vertex");
      }
      const size_t start = row_offsets[frontier_vertex.vertex_id];
      const size_t end = row_offsets[frontier_vertex.vertex_id + 1];
      for (size_t offset = start; offset < end; ++offset) {
        const uint32_t neighbor_id = column_indices[offset];
        if (visited_flags[neighbor_id] != 0u) {
          continue;
        }
        if (dedupe != 0u && discovered_flags[neighbor_id] != 0u) {
          continue;
        }
        discovered_flags[neighbor_id] = 1;
        rows.push_back(
            {frontier_vertex.vertex_id, neighbor_id, static_cast<uint32_t>(frontier_vertex.level + 1u)});
      }
    }

    std::sort(
        rows.begin(),
        rows.end(),
        [](const RtdlBfsExpandRow& left, const RtdlBfsExpandRow& right) {
          if (left.level != right.level) {
            return left.level < right.level;
          }
          if (left.dst_vertex != right.dst_vertex) {
            return left.dst_vertex < right.dst_vertex;
          }
          return left.src_vertex < right.src_vertex;
        });

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_triangle_probe(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t column_index_count,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    uint32_t enforce_id_ascending,
    uint32_t unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    if (row_offset_count == 0) {
      throw std::runtime_error("CSR graph row_offsets must not be empty");
    }
    if (row_offsets == nullptr) {
      throw std::runtime_error("CSR graph row_offsets pointer must not be null");
    }
    if (column_index_count > 0 && column_indices == nullptr) {
      throw std::runtime_error("CSR graph column_indices pointer must not be null");
    }
    if (seed_count > 0 && seeds == nullptr) {
      throw std::runtime_error("edge seed pointer must not be null when seed_count > 0");
    }
    if (row_offsets[0] != 0u) {
      throw std::runtime_error("CSR graph row_offsets must start at 0");
    }
    if (row_offsets[row_offset_count - 1] != column_index_count) {
      throw std::runtime_error("CSR graph final row_offset must equal edge_count");
    }

    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    for (size_t index = 1; index < row_offset_count; ++index) {
      if (row_offsets[index] < row_offsets[index - 1]) {
        throw std::runtime_error("CSR graph row_offsets must be non-decreasing");
      }
    }
    for (size_t index = 0; index < column_index_count; ++index) {
      if (column_indices[index] >= vertex_count) {
        throw std::runtime_error("CSR graph column_indices must be valid vertex IDs");
      }
    }

    std::vector<uint32_t> neighbor_marks(vertex_count, 0u);
    uint32_t stamp = 1u;
    std::vector<RtdlTriangleRow> rows;

    for (size_t seed_index = 0; seed_index < seed_count; ++seed_index) {
      const uint32_t u = seeds[seed_index].u;
      const uint32_t v = seeds[seed_index].v;
      if (u >= vertex_count || v >= vertex_count) {
        throw std::runtime_error("edge seed vertices must be valid graph vertex IDs");
      }
      if (u == v) {
        continue;
      }
      if (enforce_id_ascending != 0u && !(u < v)) {
        continue;
      }

      const size_t u_start = row_offsets[u];
      const size_t u_end = row_offsets[u + 1];
      const size_t v_start = row_offsets[v];
      const size_t v_end = row_offsets[v + 1];

      for (size_t offset = u_start; offset < u_end; ++offset) {
        neighbor_marks[column_indices[offset]] = stamp;
      }

      std::vector<uint32_t> common_neighbors;
      for (size_t offset = v_start; offset < v_end; ++offset) {
        const uint32_t w = column_indices[offset];
        if (neighbor_marks[w] != stamp) {
          continue;
        }
        if (enforce_id_ascending != 0u && !(v < w)) {
          continue;
        }
        common_neighbors.push_back(w);
      }
      std::sort(common_neighbors.begin(), common_neighbors.end());

      for (uint32_t w : common_neighbors) {
        if (unique != 0u) {
          const bool already_seen = std::any_of(
              rows.begin(),
              rows.end(),
              [&](const RtdlTriangleRow& row) { return row.u == u && row.v == v && row.w == w; });
          if (already_seen) {
            continue;
          }
        }
        rows.push_back({u, v, w});
      }

      stamp += 1u;
      if (stamp == 0u) {
        std::fill(neighbor_marks.begin(), neighbor_marks.end(), 0u);
        stamp = 1u;
      }
    }

    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_summarize_bfs_rows(
    const RtdlBfsExpandRow* rows,
    size_t row_count,
    RtdlBfsSummaryRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (row_count > 0 && rows == nullptr) {
      throw std::runtime_error("BFS rows pointer must not be null when row_count is non-zero");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<uint32_t> discovered_vertices;
    discovered_vertices.reserve(row_count);
    uint32_t max_level = 0;
    for (size_t index = 0; index < row_count; ++index) {
      discovered_vertices.push_back(rows[index].dst_vertex);
      max_level = std::max(max_level, rows[index].level);
    }
    std::sort(discovered_vertices.begin(), discovered_vertices.end());
    discovered_vertices.erase(std::unique(discovered_vertices.begin(), discovered_vertices.end()), discovered_vertices.end());

    std::vector<RtdlBfsSummaryRow> summary;
    summary.push_back({
        static_cast<uint32_t>(row_count),
        static_cast<uint32_t>(discovered_vertices.size()),
        max_level,
    });
    *rows_out = rtdl::oracle::copy_rows_out(summary);
    *row_count_out = summary.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_summarize_triangle_rows(
    const RtdlTriangleRow* rows,
    size_t row_count,
    RtdlTriangleSummaryRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (row_count > 0 && rows == nullptr) {
      throw std::runtime_error("triangle rows pointer must not be null when row_count is non-zero");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<uint32_t> vertices;
    vertices.reserve(row_count * 3);
    for (size_t index = 0; index < row_count; ++index) {
      vertices.push_back(rows[index].u);
      vertices.push_back(rows[index].v);
      vertices.push_back(rows[index].w);
    }
    std::sort(vertices.begin(), vertices.end());
    vertices.erase(std::unique(vertices.begin(), vertices.end()), vertices.end());

    std::vector<RtdlTriangleSummaryRow> summary;
    summary.push_back({
        static_cast<uint32_t>(row_count),
        static_cast<uint32_t>(vertices.size()),
    });
    *rows_out = rtdl::oracle::copy_rows_out(summary);
    *row_count_out = summary.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_conjunctive_scan(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (field_count == 0) {
      throw std::runtime_error("DB conjunctive scan requires at least one field");
    }
    if (row_count > 0 && row_values == nullptr) {
      throw std::runtime_error("DB conjunctive scan row_values must not be null when row_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    size_t row_id_index = rtdl::oracle::db_find_field_index(fields, field_count, "row_id");
    std::vector<RtdlDbRowIdRow> rows;
    rows.reserve(row_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
      bool matched = true;
      for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
        if (!rtdl::oracle::db_row_matches(fields, field_count, row_values, row_index, clauses[clause_index])) {
          matched = false;
          break;
        }
      }
      if (!matched) {
        continue;
      }
      const RtdlDbScalar& row_id_value =
          rtdl::oracle::db_row_value(row_values, row_index, field_count, row_id_index);
      if (!rtdl::oracle::db_scalar_is_numeric(row_id_value)) {
        throw std::runtime_error("DB conjunctive scan requires numeric row_id values");
      }
      rows.push_back({static_cast<uint32_t>(rtdl::oracle::db_scalar_as_double(row_id_value))});
    }

    std::sort(rows.begin(), rows.end(), [](const RtdlDbRowIdRow& left, const RtdlDbRowIdRow& right) {
      return left.row_id < right.row_id;
    });
    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_grouped_count(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (field_count == 0) {
      throw std::runtime_error("DB grouped count requires at least one field");
    }
    if (group_field == nullptr) {
      throw std::runtime_error("DB grouped count requires a group field");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    size_t group_index = rtdl::oracle::db_find_field_index(fields, field_count, group_field);
    std::map<int64_t, int64_t> counts;
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
      bool matched = true;
      for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
        if (!rtdl::oracle::db_row_matches(fields, field_count, row_values, row_index, clauses[clause_index])) {
          matched = false;
          break;
        }
      }
      if (!matched) {
        continue;
      }
      const RtdlDbScalar& group_value =
          rtdl::oracle::db_row_value(row_values, row_index, field_count, group_index);
      if (!rtdl::oracle::db_scalar_is_numeric(group_value)) {
        throw std::runtime_error("DB grouped count native path requires numeric-coded group keys");
      }
      int64_t key = static_cast<int64_t>(rtdl::oracle::db_scalar_as_double(group_value));
      counts[key] += 1;
    }

    std::vector<RtdlDbGroupedCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& [key, count] : counts) {
      rows.push_back({key, count});
    }
    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT int rtdl_oracle_run_grouped_sum(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return rtdl::oracle::handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (field_count == 0) {
      throw std::runtime_error("DB grouped sum requires at least one field");
    }
    if (group_field == nullptr || value_field == nullptr) {
      throw std::runtime_error("DB grouped sum requires group_field and value_field");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    size_t group_index = rtdl::oracle::db_find_field_index(fields, field_count, group_field);
    size_t value_index = rtdl::oracle::db_find_field_index(fields, field_count, value_field);
    std::map<int64_t, double> sums;
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
      bool matched = true;
      for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
        if (!rtdl::oracle::db_row_matches(fields, field_count, row_values, row_index, clauses[clause_index])) {
          matched = false;
          break;
        }
      }
      if (!matched) {
        continue;
      }
      const RtdlDbScalar& group_value =
          rtdl::oracle::db_row_value(row_values, row_index, field_count, group_index);
      const RtdlDbScalar& sum_value =
          rtdl::oracle::db_row_value(row_values, row_index, field_count, value_index);
      if (!rtdl::oracle::db_scalar_is_numeric(group_value)) {
        throw std::runtime_error("DB grouped sum native path requires numeric-coded group keys");
      }
      if (!rtdl::oracle::db_scalar_is_numeric(sum_value)) {
        throw std::runtime_error("DB grouped sum native path requires numeric value fields");
      }
      int64_t key = static_cast<int64_t>(rtdl::oracle::db_scalar_as_double(group_value));
      sums[key] += rtdl::oracle::db_scalar_as_double(sum_value);
    }

    std::vector<RtdlDbGroupedSumRow> rows;
    rows.reserve(sums.size());
    for (const auto& [key, sum] : sums) {
      rows.push_back({key, sum});
    }
    *rows_out = rtdl::oracle::copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_ORACLE_EXPORT void rtdl_oracle_free_rows(void* rows) {
  std::free(rows);
}
