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
    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    for (const Point2D& query : query_values) {
      std::vector<RtdlFixedRadiusNeighborRow> query_rows;
      std::unordered_set<uint32_t> seen_neighbor_ids;
      FixedRadiusNeighborsQueryState state {&query, &search_values, radius, &query_rows, &seen_neighbor_ids};
      RTCPointQuery point_query;
      point_query.x = static_cast<float>(query.p.x);
      point_query.y = static_cast<float>(query.p.y);
      point_query.z = 0.0f;
      point_query.time = 0.0f;
      point_query.radius = static_cast<float>(radius + kFixedRadiusCandidateEps);
      RTCPointQueryContext context;
      rtcInitPointQueryContext(&context);
      g_query_kind = QueryKind::kFixedRadiusNeighbors;
      rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect, &state);
      g_query_kind = QueryKind::kNone;
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

RTDL_EMBREE_EXPORT int rtdl_embree_run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* query_points,
    size_t query_count,
    const RtdlPoint3D* search_points,
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

    std::vector<Point3D> query_values;
    std::vector<Point3D> search_values;
    query_values.reserve(query_count);
    search_values.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
      query_values.push_back({query_points[i].id, {query_points[i].x, query_points[i].y, query_points[i].z}});
    }
    for (size_t i = 0; i < search_count; ++i) {
      search_values.push_back({search_points[i].id, {search_points[i].x, search_points[i].y, search_points[i].z}});
    }

    EmbreeDevice device;
    PointSceneData3D data {&search_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(search_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, point_bounds_3d, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect_3d);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlFixedRadiusNeighborRow> rows;
    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    for (const Point3D& query : query_values) {
      std::vector<RtdlFixedRadiusNeighborRow> query_rows;
      std::unordered_set<uint32_t> seen_neighbor_ids;
      FixedRadiusNeighborsQueryState3D state {&query, &search_values, radius, &query_rows, &seen_neighbor_ids};
      RTCPointQuery point_query;
      point_query.x = static_cast<float>(query.p.x);
      point_query.y = static_cast<float>(query.p.y);
      point_query.z = static_cast<float>(query.p.z);
      point_query.time = 0.0f;
      point_query.radius = static_cast<float>(radius + kFixedRadiusCandidateEps);
      RTCPointQueryContext context;
      rtcInitPointQueryContext(&context);
      g_query_kind = QueryKind::kFixedRadiusNeighbors3D;
      rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect_3d, &state);
      g_query_kind = QueryKind::kNone;
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

RTDL_EMBREE_EXPORT int rtdl_embree_run_knn_rows(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (k == 0) {
      throw std::runtime_error("knn_rows k must be positive");
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

    std::vector<RtdlKnnNeighborRow> rows;
    for (const Point2D& query : query_values) {
      std::vector<RtdlKnnNeighborRow> query_rows;
      std::unordered_set<uint32_t> seen_neighbor_ids;
      KnnRowsQueryState state {&query, &search_values, k, &query_rows, &seen_neighbor_ids};
      RTCPointQuery point_query;
      point_query.x = static_cast<float>(query.p.x);
      point_query.y = static_cast<float>(query.p.y);
      point_query.z = 0.0f;
      point_query.time = 0.0f;
      point_query.radius = std::numeric_limits<float>::infinity();
      RTCPointQueryContext context;
      rtcInitPointQueryContext(&context);
      g_query_kind = QueryKind::kKnnRows;
      rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect, &state);
      g_query_kind = QueryKind::kNone;
      std::sort(query_rows.begin(), query_rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
        if (left.distance < right.distance - 1.0e-12) {
          return true;
        }
        if (right.distance < left.distance - 1.0e-12) {
          return false;
        }
        return left.neighbor_id < right.neighbor_id;
      });
      if (query_rows.size() > k) {
        query_rows.resize(k);
      }
      for (size_t index = 0; index < query_rows.size(); ++index) {
        query_rows[index].neighbor_rank = static_cast<uint32_t>(index + 1);
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
      return left.query_id < right.query_id;
    });

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_knn_rows_3d(
    const RtdlPoint3D* query_points,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (k == 0) {
      throw std::runtime_error("knn_rows k must be positive");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point3D> query_values;
    std::vector<Point3D> search_values;
    query_values.reserve(query_count);
    search_values.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
      query_values.push_back({query_points[i].id, {query_points[i].x, query_points[i].y, query_points[i].z}});
    }
    for (size_t i = 0; i < search_count; ++i) {
      search_values.push_back({search_points[i].id, {search_points[i].x, search_points[i].y, search_points[i].z}});
    }

    EmbreeDevice device;
    PointSceneData3D data {&search_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(search_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, point_bounds_3d, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect_3d);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlKnnNeighborRow> rows;
    for (const Point3D& query : query_values) {
      std::vector<RtdlKnnNeighborRow> query_rows;
      std::unordered_set<uint32_t> seen_neighbor_ids;
      KnnRowsQueryState3D state {&query, &search_values, k, &query_rows, &seen_neighbor_ids};
      RTCPointQuery point_query;
      point_query.x = static_cast<float>(query.p.x);
      point_query.y = static_cast<float>(query.p.y);
      point_query.z = static_cast<float>(query.p.z);
      point_query.time = 0.0f;
      point_query.radius = std::numeric_limits<float>::infinity();
      RTCPointQueryContext context;
      rtcInitPointQueryContext(&context);
      g_query_kind = QueryKind::kKnnRows3D;
      rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect_3d, &state);
      g_query_kind = QueryKind::kNone;
      std::sort(query_rows.begin(), query_rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
        if (left.distance < right.distance - 1.0e-12) {
          return true;
        }
        if (right.distance < left.distance - 1.0e-12) {
          return false;
        }
        return left.neighbor_id < right.neighbor_id;
      });
      if (query_rows.size() > k) {
        query_rows.resize(k);
      }
      for (size_t index = 0; index < query_rows.size(); ++index) {
        query_rows[index].neighbor_rank = static_cast<uint32_t>(index + 1);
      }
      rows.insert(rows.end(), query_rows.begin(), query_rows.end());
    }
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
      return left.query_id < right.query_id;
    });

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_bfs_expand(
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
  return handle_native_call([&]() {
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

    std::vector<uint8_t> visited_flags(vertex_count, 0u);
    for (size_t index = 0; index < visited_count; ++index) {
      if (visited[index] >= vertex_count) {
        throw std::runtime_error("visited vertex_id must be a valid graph vertex");
      }
      visited_flags[visited[index]] = 1u;
    }

    std::vector<GraphEdgePoint> edge_points;
    edge_points.reserve(column_index_count);
    for (uint32_t src_vertex = 0; src_vertex < vertex_count; ++src_vertex) {
      const size_t start = row_offsets[src_vertex];
      const size_t end = row_offsets[src_vertex + 1];
      for (size_t offset = start; offset < end; ++offset) {
        const uint32_t dst_vertex = column_indices[offset];
        edge_points.push_back({src_vertex, dst_vertex, {static_cast<double>(src_vertex), 0.0}});
      }
    }

    EmbreeDevice device;
    GraphEdgePointSceneData data {&edge_points};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(edge_points.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, graph_edge_point_bounds, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<uint8_t> discovered_flags(vertex_count, 0u);
    std::vector<RtdlBfsExpandRow> rows;
    for (size_t index = 0; index < frontier_count; ++index) {
      const RtdlFrontierVertex frontier_vertex = frontier[index];
      if (frontier_vertex.vertex_id >= vertex_count) {
        throw std::runtime_error("frontier vertex_id must be a valid graph vertex");
      }
      GraphBfsExpandQueryState state {
          &frontier_vertex,
          &edge_points,
          &visited_flags,
          &discovered_flags,
          dedupe,
          &rows,
      };
      RTCPointQuery point_query;
      point_query.x = static_cast<float>(frontier_vertex.vertex_id);
      point_query.y = 0.0f;
      point_query.z = 0.0f;
      point_query.time = 0.0f;
      point_query.radius = static_cast<float>(kEps * 2.0);
      RTCPointQueryContext context;
      rtcInitPointQueryContext(&context);
      g_query_kind = QueryKind::kGraphBfsExpand;
      rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect, &state);
      g_query_kind = QueryKind::kNone;
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

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_triangle_probe(
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
  return handle_native_call([&]() {
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

    std::vector<GraphEdgePoint> edge_points;
    edge_points.reserve(column_index_count);
    for (uint32_t src_vertex = 0; src_vertex < vertex_count; ++src_vertex) {
      const size_t start = row_offsets[src_vertex];
      const size_t end = row_offsets[src_vertex + 1];
      for (size_t offset = start; offset < end; ++offset) {
        const uint32_t dst_vertex = column_indices[offset];
        edge_points.push_back({src_vertex, dst_vertex, {static_cast<double>(src_vertex), 0.0}});
      }
    }

    EmbreeDevice device;
    GraphEdgePointSceneData data {&edge_points};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(edge_points.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, graph_edge_point_bounds, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<uint32_t> u_neighbor_marks(vertex_count, 0u);
    std::vector<uint32_t> v_neighbor_marks(vertex_count, 0u);
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

      std::vector<uint32_t> u_neighbors;
      GraphTriangleProbeQueryState u_state {
          &edge_points,
          &u_neighbor_marks,
          stamp,
          &u_neighbors,
      };
      RTCPointQuery u_query;
      u_query.x = static_cast<float>(u);
      u_query.y = 0.0f;
      u_query.z = 0.0f;
      u_query.time = 0.0f;
      u_query.radius = static_cast<float>(kEps * 2.0);
      RTCPointQueryContext u_context;
      rtcInitPointQueryContext(&u_context);
      g_query_kind = QueryKind::kGraphTriangleProbe;
      rtcPointQuery(holder.scene, &u_query, &u_context, point_point_query_collect, &u_state);

      std::vector<uint32_t> v_neighbors;
      GraphTriangleProbeQueryState v_state {
          &edge_points,
          &v_neighbor_marks,
          stamp,
          &v_neighbors,
      };
      RTCPointQuery v_query;
      v_query.x = static_cast<float>(v);
      v_query.y = 0.0f;
      v_query.z = 0.0f;
      v_query.time = 0.0f;
      v_query.radius = static_cast<float>(kEps * 2.0);
      RTCPointQueryContext v_context;
      rtcInitPointQueryContext(&v_context);
      rtcPointQuery(holder.scene, &v_query, &v_context, point_point_query_collect, &v_state);
      g_query_kind = QueryKind::kNone;

      const std::vector<uint32_t>& smaller = (u_neighbors.size() <= v_neighbors.size()) ? u_neighbors : v_neighbors;
      const std::vector<uint32_t>& other_neighbor_marks =
          (u_neighbors.size() <= v_neighbors.size()) ? v_neighbor_marks : u_neighbor_marks;
      std::vector<uint32_t> common_neighbors;
      common_neighbors.reserve(smaller.size());
      for (uint32_t w : smaller) {
        if (other_neighbor_marks[w] != stamp) {
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
        std::fill(u_neighbor_marks.begin(), u_neighbor_marks.end(), 0u);
        std::fill(v_neighbor_marks.begin(), v_neighbor_marks.end(), 0u);
        stamp = 1u;
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT void rtdl_embree_free_rows(void* rows) {
  std::free(rows);
}
