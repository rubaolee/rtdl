#include "rtdl_oracle_internal.h"

namespace rtdl::oracle {

}  // namespace rtdl::oracle

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

extern "C" int rtdl_oracle_run_ray_hitcount(
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

extern "C" int rtdl_oracle_run_polygon_set_jaccard(
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

extern "C" int rtdl_oracle_run_point_nearest_segment(
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

extern "C" int rtdl_oracle_run_fixed_radius_neighbors(
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

extern "C" void rtdl_oracle_free_rows(void* rows) {
  std::free(rows);
}
