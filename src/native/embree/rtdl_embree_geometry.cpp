constexpr double kEps = 1.0e-6;
constexpr double kSegmentIntersectionEps = 1.0e-7;

template <typename T>
void set_error(const std::string& message, T* error_out, size_t error_size) {
  if (error_out == nullptr || error_size == 0) {
    return;
  }
  size_t length = std::min(error_size - 1, message.size());
  std::memcpy(error_out, message.data(), length);
  error_out[length] = '\0';
}

struct Vec2 {
  double x;
  double y;
};

struct Vec3 {
  double x;
  double y;
  double z;
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

struct Triangle2D {
  uint32_t id;
  Vec2 a;
  Vec2 b;
  Vec2 c;
};

struct Triangle3D {
  uint32_t id;
  Vec3 a;
  Vec3 b;
  Vec3 c;
};

struct RayQuery2D {
  uint32_t id;
  Vec2 o;
  Vec2 d;
  double tmax;
};

struct RayQuery3D {
  uint32_t id;
  Vec3 o;
  Vec3 d;
  double tmax;
};

#if RTDL_EMBREE_HAS_GEOS
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

struct Bounds2D {
  double min_x;
  double min_y;
  double max_x;
  double max_y;
};

struct Bounds3D {
  double min_x;
  double min_y;
  double min_z;
  double max_x;
  double max_y;
  double max_z;
};

Bounds2D bounds_for_segment(const Segment2D& segment) {
  return {
      std::min(segment.a.x, segment.b.x),
      std::min(segment.a.y, segment.b.y),
      std::max(segment.a.x, segment.b.x),
      std::max(segment.a.y, segment.b.y),
  };
}

Bounds2D bounds_for_triangle(const Triangle2D& triangle) {
  return {
      std::min({triangle.a.x, triangle.b.x, triangle.c.x}),
      std::min({triangle.a.y, triangle.b.y, triangle.c.y}),
      std::max({triangle.a.x, triangle.b.x, triangle.c.x}),
      std::max({triangle.a.y, triangle.b.y, triangle.c.y}),
  };
}

Bounds3D bounds_for_triangle_3d(const Triangle3D& triangle) {
  return {
      std::min({triangle.a.x, triangle.b.x, triangle.c.x}),
      std::min({triangle.a.y, triangle.b.y, triangle.c.y}),
      std::min({triangle.a.z, triangle.b.z, triangle.c.z}),
      std::max({triangle.a.x, triangle.b.x, triangle.c.x}),
      std::max({triangle.a.y, triangle.b.y, triangle.c.y}),
      std::max({triangle.a.z, triangle.b.z, triangle.c.z}),
  };
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

bool bounds_overlap(const Bounds2D& left, const Bounds2D& right) {
  return !(left.max_x < right.min_x || right.max_x < left.min_x ||
           left.max_y < right.min_y || right.max_y < left.min_y);
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

double cross(const Vec2& a, const Vec2& b) {
  return a.x * b.y - a.y * b.x;
}

Vec2 sub(const Vec2& a, const Vec2& b) {
  return {a.x - b.x, a.y - b.y};
}

bool segment_intersection(
    const Segment2D& left,
    const Segment2D& right,
    Vec2* point_out) {
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
  if (t < 0.0 || t > 1.0 || u < 0.0 || u > 1.0) {
    return false;
  }
  if (point_out != nullptr) {
    point_out->x = p.x + t * r.x;
    point_out->y = p.y + t * r.y;
  }
  return true;
}

std::vector<RtdlLsiRow> lsi_native_loop(
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

  std::vector<IndexedSegmentBounds> build_sorted;
  build_sorted.reserve(right_segments.size());
  for (size_t index = 0; index < right_segments.size(); ++index) {
    const Segment2D& build = right_segments[index];
    Bounds2D bounds = bounds_for_segment(build);
    build_sorted.push_back({
        index,
        &build,
        bounds.min_x,
        bounds.max_x,
        bounds.min_y,
        bounds.max_y,
    });
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
    const Segment2D& probe = left_segments[index];
    Bounds2D bounds = bounds_for_segment(probe);
    probe_sorted.push_back({
        index,
        &probe,
        bounds.min_x,
        bounds.max_x,
        bounds.min_y,
        bounds.max_y,
    });
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

bool point_on_segment(const Point2D& point, const Vec2& start, const Vec2& end) {
  const double point_eps = 1.0e-12;
  double length_sq = (end.x - start.x) * (end.x - start.x) + (end.y - start.y) * (end.y - start.y);
  if (length_sq <= point_eps * point_eps) {
    return std::fabs(point.p.x - start.x) <= point_eps &&
           std::fabs(point.p.y - start.y) <= point_eps;
  }
  double length = std::sqrt(length_sq);
  double cross_value = (point.p.x - start.x) * (end.y - start.y) - (point.p.y - start.y) * (end.x - start.x);
  if (std::fabs(cross_value) > point_eps * length) {
    return false;
  }
  double dot = (point.p.x - start.x) * (end.x - start.x) + (point.p.y - start.y) * (end.y - start.y);
  double along_eps = point_eps * length;
  if (dot < -along_eps) {
    return false;
  }
  if (dot - length_sq > along_eps) {
    return false;
  }
  return true;
}

bool point_in_polygon(const Point2D& point, const Polygon2D& polygon) {
  if (polygon.vertices.empty()) {
    return false;
  }
  for (size_t i = 0; i < polygon.vertices.size(); ++i) {
    const Vec2& start = polygon.vertices[i];
    const Vec2& end = polygon.vertices[(i + 1) % polygon.vertices.size()];
    if (point_on_segment(point, start, end)) {
      return true;
    }
  }
  bool inside = false;
  size_t j = polygon.vertices.size() - 1;
  for (size_t i = 0; i < polygon.vertices.size(); ++i) {
    const Vec2& vi = polygon.vertices[i];
    const Vec2& vj = polygon.vertices[j];
    bool crossing = ((vi.y > point.p.y) != (vj.y > point.p.y)) &&
                    (point.p.x <= (vj.x - vi.x) * (point.p.y - vi.y) / ((vj.y - vi.y) == 0.0f ? 1.0e-20f : (vj.y - vi.y)) + vi.x);
    if (crossing) {
      inside = !inside;
    }
    j = i;
  }
  return inside;
}

bool point_in_triangle(const Vec2& p, const Triangle2D& triangle) {
  Vec2 v0 = sub(triangle.c, triangle.a);
  Vec2 v1 = sub(triangle.b, triangle.a);
  Vec2 v2 = sub(p, triangle.a);
  float dot00 = v0.x * v0.x + v0.y * v0.y;
  float dot01 = v0.x * v1.x + v0.y * v1.y;
  float dot02 = v0.x * v2.x + v0.y * v2.y;
  float dot11 = v1.x * v1.x + v1.y * v1.y;
  float dot12 = v1.x * v2.x + v1.y * v2.y;
  float denom = dot00 * dot11 - dot01 * dot01;
  if (std::fabs(denom) < kEps) {
    return false;
  }
  float inv = 1.0f / denom;
  float u = (dot11 * dot02 - dot01 * dot12) * inv;
  float v = (dot00 * dot12 - dot01 * dot02) * inv;
  return u >= 0.0f && v >= 0.0f && (u + v) <= 1.0f;
}

bool finite_ray_hits_triangle(const RayQuery2D& ray, const Triangle2D& triangle) {
  Vec2 end {ray.o.x + ray.d.x * ray.tmax, ray.o.y + ray.d.y * ray.tmax};
  Segment2D ray_segment {ray.id, ray.o, end};
  if (point_in_triangle(ray.o, triangle) || point_in_triangle(end, triangle)) {
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

bool finite_ray_hits_triangle_3d(const RayQuery3D& ray, const Triangle3D& triangle) {
  Vec3 edge1 {
      triangle.b.x - triangle.a.x,
      triangle.b.y - triangle.a.y,
      triangle.b.z - triangle.a.z,
  };
  Vec3 edge2 {
      triangle.c.x - triangle.a.x,
      triangle.c.y - triangle.a.y,
      triangle.c.z - triangle.a.z,
  };
  Vec3 pvec {
      ray.d.y * edge2.z - ray.d.z * edge2.y,
      ray.d.z * edge2.x - ray.d.x * edge2.z,
      ray.d.x * edge2.y - ray.d.y * edge2.x,
  };
  double det = edge1.x * pvec.x + edge1.y * pvec.y + edge1.z * pvec.z;
  if (std::fabs(det) <= 1.0e-8) {
    return false;
  }
  double inv_det = 1.0 / det;
  Vec3 tvec {
      ray.o.x - triangle.a.x,
      ray.o.y - triangle.a.y,
      ray.o.z - triangle.a.z,
  };
  double u = (tvec.x * pvec.x + tvec.y * pvec.y + tvec.z * pvec.z) * inv_det;
  if (u < 0.0 || u > 1.0) {
    return false;
  }
  Vec3 qvec {
      tvec.y * edge1.z - tvec.z * edge1.y,
      tvec.z * edge1.x - tvec.x * edge1.z,
      tvec.x * edge1.y - tvec.y * edge1.x,
  };
  double v = (ray.d.x * qvec.x + ray.d.y * qvec.y + ray.d.z * qvec.z) * inv_det;
  if (v < 0.0 || (u + v) > 1.0) {
    return false;
  }
  double t = (edge2.x * qvec.x + edge2.y * qvec.y + edge2.z * qvec.z) * inv_det;
  return t >= 0.0 && t <= ray.tmax;
}

bool polygon_pair_flags(const Polygon2D& left, const Polygon2D& right, bool* requires_lsi, bool* requires_pip) {
  bool lsi = false;
  bool pip = false;

  std::vector<Segment2D> left_edges;
  std::vector<Segment2D> right_edges;
  for (size_t i = 0; i < left.vertices.size(); ++i) {
    left_edges.push_back({left.id, left.vertices[i], left.vertices[(i + 1) % left.vertices.size()]});
  }
  for (size_t i = 0; i < right.vertices.size(); ++i) {
    right_edges.push_back({right.id, right.vertices[i], right.vertices[(i + 1) % right.vertices.size()]});
  }
  for (const Segment2D& le : left_edges) {
    for (const Segment2D& re : right_edges) {
      if (segment_intersection(le, re, nullptr)) {
        lsi = true;
        break;
      }
    }
    if (lsi) {
      break;
    }
  }

  Point2D left_point {left.id, left.vertices[0]};
  Point2D right_point {right.id, right.vertices[0]};
  pip = point_in_polygon(left_point, right) || point_in_polygon(right_point, left);

  if (requires_lsi != nullptr) {
    *requires_lsi = lsi;
  }
  if (requires_pip != nullptr) {
    *requires_pip = pip;
  }
  return lsi || pip;
}

bool segment_hits_polygon(const Segment2D& segment, const Polygon2D& polygon) {
  Point2D start {segment.id, segment.a};
  Point2D end {segment.id, segment.b};
  if (point_in_polygon(start, polygon) || point_in_polygon(end, polygon)) {
    return true;
  }

  for (size_t i = 0; i < polygon.vertices.size(); ++i) {
    Segment2D edge {
        polygon.id,
        polygon.vertices[i],
        polygon.vertices[(i + 1) % polygon.vertices.size()],
    };
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
  if (denom < 1.0e-12f) {
    Vec2 d = sub(point.p, segment.a);
    return std::sqrt(d.x * d.x + d.y * d.y);
  }
  double t = (w.x * v.x + w.y * v.y) / denom;
  t = std::max(0.0, std::min(1.0, t));
  Vec2 projection {segment.a.x + t * v.x, segment.a.y + t * v.y};
  Vec2 d = sub(point.p, projection);
  return std::sqrt(d.x * d.x + d.y * d.y);
}
