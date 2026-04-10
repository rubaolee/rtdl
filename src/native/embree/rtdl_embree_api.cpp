#if defined(_WIN32)
#  define RTDL_EMBREE_EXPORT extern "C" __declspec(dllexport)
#else
#  define RTDL_EMBREE_EXPORT extern "C"
#endif

RTDL_EMBREE_EXPORT int rtdl_embree_get_version(int* major_out, int* minor_out, int* patch_out) {
  if (major_out == nullptr || minor_out == nullptr || patch_out == nullptr) {
    return 1;
  }
  *major_out = RTC_VERSION_MAJOR;
  *minor_out = RTC_VERSION_MINOR;
  *patch_out = RTC_VERSION_PATCH;
  return 0;
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_lsi(
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

    std::vector<Segment2D> left_segments;
    std::vector<Segment2D> right_segments;
    left_segments.reserve(left_count);
    right_segments.reserve(right_count);
    for (size_t i = 0; i < left_count; ++i) {
      left_segments.push_back({left[i].id, {left[i].x0, left[i].y0}, {left[i].x1, left[i].y1}});
    }
    for (size_t i = 0; i < right_count; ++i) {
      right_segments.push_back({right[i].id, {right[i].x0, right[i].y0}, {right[i].x1, right[i].y1}});
    }

    std::vector<RtdlLsiRow> rows = lsi_native_loop(left_segments, right_segments);
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_pip(
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

    std::vector<Point2D> point_values;
    point_values.reserve(point_count);
    for (size_t i = 0; i < point_count; ++i) {
      point_values.push_back({points[i].id, {points[i].x, points[i].y}});
    }
    std::vector<Polygon2D> polygon_values = decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count);

    std::vector<RtdlPipRow> rows;
    if (positive_only != 0u) {
      EmbreeDevice device;
      PolygonSceneData data {&polygon_values};
      SceneHolder holder(device.device);
      holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
      rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(polygon_values.size()));
      rtcSetGeometryUserData(holder.geometry, &data);
      rtcSetGeometryBoundsFunction(holder.geometry, polygon_bounds, nullptr);
      rtcSetGeometryIntersectFunction(holder.geometry, polygon_intersect);
      rtcSetGeometryIntersectFilterFunction(holder.geometry, polygon_intersect_filter);
      rtcCommitGeometry(holder.geometry);
      rtcAttachGeometry(holder.scene, holder.geometry);
      rtcCommitScene(holder.scene);

#if RTDL_EMBREE_HAS_GEOS
      GeosPreparedPolygonSet geos(polygon_values);
#endif
      for (const Point2D& point : point_values) {
        std::unordered_set<uint32_t> candidate_polygon_indices;
        PipQueryState state {&point, &candidate_polygon_indices};
        RTCPointQuery query;
        query.x = static_cast<float>(point.p.x);
        query.y = static_cast<float>(point.p.y);
        query.z = 0.0f;
        query.time = 0.0f;
        query.radius = 0.0f;
        RTCPointQueryContext context;
        rtcInitPointQueryContext(&context);
        rtcPointQuery(holder.scene, &query, &context, polygon_point_query_collect, &state);
        if (candidate_polygon_indices.empty()) {
          continue;
        }
        std::vector<uint32_t> candidate_indices;
        candidate_indices.reserve(candidate_polygon_indices.size());
        for (uint32_t polygon_index : candidate_polygon_indices) {
          candidate_indices.push_back(polygon_index);
        }
        std::sort(candidate_indices.begin(), candidate_indices.end());
        for (uint32_t polygon_index : candidate_indices) {
#if RTDL_EMBREE_HAS_GEOS
          const bool contains = geos.covers(polygon_index, point.p.x, point.p.y);
#else
          const bool contains = point_in_polygon(point, polygon_values[polygon_index]);
#endif
          if (!contains) {
            continue;
          }
          rows.push_back({point.id, polygon_values[polygon_index].id, 1u});
        }
      }
    } else {
      rows.reserve(point_values.size() * polygon_values.size());
#if RTDL_EMBREE_HAS_GEOS
      GeosPreparedPolygonSet geos(polygon_values);
      for (const Point2D& point : point_values) {
        for (size_t polygon_index = 0; polygon_index < polygon_values.size(); ++polygon_index) {
          const bool contains = geos.covers(polygon_index, point.p.x, point.p.y);
          rows.push_back({point.id, polygon_values[polygon_index].id, contains ? 1u : 0u});
        }
      }
#else
      for (const Point2D& point : point_values) {
        for (const Polygon2D& polygon : polygon_values) {
          const bool contains = point_in_polygon(point, polygon);
          rows.push_back({point.id, polygon.id, contains ? 1u : 0u});
        }
      }
#endif
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_overlay(
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

    EmbreeDevice device;
    PolygonSceneData data {&right_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(right_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, polygon_bounds, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, polygon_intersect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlOverlayRow> rows;
    rows.reserve(left_values.size() * right_values.size());
    for (const Polygon2D& left_polygon : left_values) {
      std::unordered_map<uint32_t, OverlayPairFlags> flags_by_right_id;
      OverlayQueryState state {&left_polygon, &flags_by_right_id};
      g_query_kind = QueryKind::kOverlay;
      g_query_state = &state;
      for (size_t i = 0; i < left_polygon.vertices.size(); ++i) {
        Vec2 start = left_polygon.vertices[i];
        Vec2 end = left_polygon.vertices[(i + 1) % left_polygon.vertices.size()];
        Vec2 dir = sub(end, start);
        RTCRayHit rayhit;
        set_ray(&rayhit, start, dir, 1.0f);
        RTCIntersectArguments args;
        rtcInitIntersectArguments(&args);
        rtcIntersect1(holder.scene, &rayhit, &args);
      }
      for (const Polygon2D& right_polygon : right_values) {
        OverlayPairFlags flags = flags_by_right_id[right_polygon.id];
        rows.push_back({left_polygon.id, right_polygon.id, flags.requires_lsi, flags.requires_pip});
      }
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_ray_hitcount(
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

    std::vector<RayQuery2D> ray_values;
    std::vector<Triangle2D> triangle_values;
    ray_values.reserve(ray_count);
    triangle_values.reserve(triangle_count);
    for (size_t i = 0; i < ray_count; ++i) {
      ray_values.push_back({rays[i].id, {rays[i].ox, rays[i].oy}, {rays[i].dx, rays[i].dy}, rays[i].tmax});
    }
    for (size_t i = 0; i < triangle_count; ++i) {
      triangle_values.push_back({triangles[i].id, {triangles[i].x0, triangles[i].y0}, {triangles[i].x1, triangles[i].y1}, {triangles[i].x2, triangles[i].y2}});
    }

    EmbreeDevice device;
    TriangleSceneData data {&triangle_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(triangle_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, triangle_bounds, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, triangle_intersect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlRayHitCountRow> rows;
    rows.reserve(ray_values.size());
    for (const RayQuery2D& ray : ray_values) {
      uint32_t hit_count = 0;
      std::unordered_set<uint32_t> seen_triangle_ids;
      RayHitCountState state {&ray, &hit_count, &seen_triangle_ids};
      g_query_kind = QueryKind::kRayHitCount;
      g_query_state = &state;
      RTCRayHit rayhit;
      set_ray(&rayhit, ray.o, ray.d, ray.tmax);
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      rtcIntersect1(holder.scene, &rayhit, &args);
      rows.push_back({ray.id, hit_count});
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_ray_hitcount_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
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

    std::vector<RayQuery3D> ray_values;
    std::vector<Triangle3D> triangle_values;
    ray_values.reserve(ray_count);
    triangle_values.reserve(triangle_count);
    for (size_t i = 0; i < ray_count; ++i) {
      ray_values.push_back({rays[i].id, {rays[i].ox, rays[i].oy, rays[i].oz}, {rays[i].dx, rays[i].dy, rays[i].dz}, rays[i].tmax});
    }
    for (size_t i = 0; i < triangle_count; ++i) {
      triangle_values.push_back({
          triangles[i].id,
          {triangles[i].x0, triangles[i].y0, triangles[i].z0},
          {triangles[i].x1, triangles[i].y1, triangles[i].z1},
          {triangles[i].x2, triangles[i].y2, triangles[i].z2},
      });
    }

    EmbreeDevice device;
    TriangleSceneData3D data {&triangle_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(triangle_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, triangle_bounds_3d, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, triangle_intersect_3d);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlRayHitCountRow> rows;
    rows.reserve(ray_values.size());
    for (const RayQuery3D& ray : ray_values) {
      uint32_t hit_count = 0;
      std::unordered_set<uint32_t> seen_triangle_ids;
      RayHitCountState3D state {&ray, &hit_count, &seen_triangle_ids};
      g_query_kind = QueryKind::kRayHitCount;
      g_query_state = &state;
      RTCRayHit rayhit;
      set_ray_3d(&rayhit, ray.o, ray.d, ray.tmax);
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      rtcIntersect1(holder.scene, &rayhit, &args);
      rows.push_back({ray.id, hit_count});
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_segment_polygon_hitcount(
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

    std::vector<Segment2D> segment_values;
    segment_values.reserve(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
      segment_values.push_back({segments[i].id, {segments[i].x0, segments[i].y0}, {segments[i].x1, segments[i].y1}});
    }
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

RTDL_EMBREE_EXPORT int rtdl_embree_run_segment_polygon_anyhit_rows(
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

    std::vector<Segment2D> segment_values;
    segment_values.reserve(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
      segment_values.push_back({segments[i].id, {segments[i].x0, segments[i].y0}, {segments[i].x1, segments[i].y1}});
    }
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

RTDL_EMBREE_EXPORT int rtdl_embree_run_point_nearest_segment(
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

    std::vector<Point2D> point_values;
    std::vector<Segment2D> segment_values;
    point_values.reserve(point_count);
    segment_values.reserve(segment_count);
    for (size_t i = 0; i < point_count; ++i) {
      point_values.push_back({points[i].id, {points[i].x, points[i].y}});
    }
    for (size_t i = 0; i < segment_count; ++i) {
      segment_values.push_back({segments[i].id, {segments[i].x0, segments[i].y0}, {segments[i].x1, segments[i].y1}});
    }

    std::vector<RtdlPointNearestSegmentRow> rows;
    rows.reserve(point_values.size());
    for (const Point2D& point : point_values) {
      const Segment2D* best_segment = nullptr;
      float best_distance = 0.0f;
      for (const Segment2D& segment : segment_values) {
        float distance = point_segment_distance(point, segment);
        if (best_segment == nullptr ||
            distance < best_distance - kEps ||
            (std::fabs(distance - best_distance) <= kEps && segment.id < best_segment->id)) {
          best_segment = &segment;
          best_distance = distance;
        }
      }
      if (best_segment == nullptr) {
        continue;
      }
      rows.push_back({point.id, best_segment->id, best_distance});
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_fixed_radius_neighbors(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    size_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (radius < 0.0) {
      throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (k_max == 0) {
      throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point2D> query_values;
    std::vector<Point2D> search_values;
    query_values.reserve(query_count);
    search_values.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
      query_values.push_back({query_points[i].id, {query_points[i].x, query_points[i].y}});
    }
    for (size_t i = 0; i < search_count; ++i) {
      search_values.push_back({search_points[i].id, {search_points[i].x, search_points[i].y}});
    }

    EmbreeDevice device;
    PointSceneData data {&search_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(search_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, point_bounds, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlFixedRadiusNeighborRow> rows;
    for (const Point2D& query : query_values) {
      std::vector<RtdlFixedRadiusNeighborRow> query_rows;
      std::unordered_set<uint32_t> seen_neighbor_ids;
      FixedRadiusNeighborsQueryState state {&query, &search_values, radius, &query_rows, &seen_neighbor_ids};
      RTCPointQuery point_query;
      point_query.x = static_cast<float>(query.p.x);
      point_query.y = static_cast<float>(query.p.y);
      point_query.z = 0.0f;
      point_query.time = 0.0f;
      point_query.radius = static_cast<float>(radius);
      RTCPointQueryContext context;
      rtcInitPointQueryContext(&context);
      rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect, &state);
      std::sort(query_rows.begin(), query_rows.end(), [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
        if (left.distance < right.distance - 1.0e-12) {
          return true;
        }
        if (right.distance < left.distance - 1.0e-12) {
          return false;
        }
        return left.neighbor_id < right.neighbor_id;
      });
      if (query_rows.size() > k_max) {
        query_rows.resize(k_max);
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
      return left.query_id < right.query_id;
    });

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT void rtdl_embree_free_rows(void* rows) {
  std::free(rows);
}
