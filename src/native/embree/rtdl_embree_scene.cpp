struct EmbreeDevice {
  RTCDevice device;

  EmbreeDevice() : device(rtcNewDevice(nullptr)) {
    if (device == nullptr) {
      throw std::runtime_error("failed to create Embree device");
    }
  }

  ~EmbreeDevice() {
    if (device != nullptr) {
      rtcReleaseDevice(device);
    }
  }
};

struct SceneHolder {
  RTCScene scene;
  RTCGeometry geometry;

  SceneHolder(RTCDevice device) : scene(rtcNewScene(device)), geometry(nullptr) {
    if (scene == nullptr) {
      throw std::runtime_error("failed to create Embree scene");
    }
  }

  ~SceneHolder() {
    if (geometry != nullptr) {
      rtcReleaseGeometry(geometry);
    }
    if (scene != nullptr) {
      rtcReleaseScene(scene);
    }
  }
};

enum class QueryKind {
  kNone,
  kLsi,
  kPip,
  kOverlay,
  kRayHitCount,
  kSegmentPolygonHitCount,
  kGraphBfsExpand,
  kGraphTriangleProbe,
  kFixedRadiusNeighbors,
  kFixedRadiusNeighbors3D,
  kKnnRows,
  kKnnRows3D,
};

struct SegmentSceneData {
  const std::vector<Segment2D>* segments;
};

struct PolygonSceneData {
  const std::vector<Polygon2D>* polygons;
};

struct PointSceneData {
  const std::vector<Point2D>* points;
};

struct PointSceneData3D {
  const std::vector<Point3D>* points;
};

struct GraphEdgePoint {
  uint32_t src_vertex;
  uint32_t dst_vertex;
  Vec2 p;
};

struct GraphEdgePointSceneData {
  const std::vector<GraphEdgePoint>* points;
};

struct TriangleSceneData {
  const std::vector<Triangle2D>* triangles;
};

struct TriangleSceneData3D {
  const std::vector<Triangle3D>* triangles;
};

struct LsiQueryState {
  const Segment2D* probe;
  std::vector<RtdlLsiRow>* rows;
};

struct PipQueryState {
  const Point2D* point;
  std::unordered_set<uint32_t>* candidate_polygon_indices;
};

struct OverlayPairFlags {
  uint32_t requires_lsi;
  uint32_t requires_pip;
};

struct OverlayQueryState {
  const Polygon2D* left;
  std::unordered_map<uint32_t, OverlayPairFlags>* flags_by_right_id;
};

struct RayHitCountState {
  const RayQuery2D* ray;
  uint32_t* hit_count;
  std::unordered_set<uint32_t>* seen_triangle_ids;
};

struct RayHitCountState3D {
  const RayQuery3D* ray;
  uint32_t* hit_count;
  std::unordered_set<uint32_t>* seen_triangle_ids;
};

struct SegmentPolygonHitCountState {
  const Segment2D* segment;
  uint32_t* hit_count;
};

struct GraphBfsExpandQueryState {
  const RtdlFrontierVertex* frontier_vertex;
  const std::vector<GraphEdgePoint>* edge_points;
  const std::vector<uint8_t>* visited_flags;
  std::vector<uint8_t>* discovered_flags;
  uint32_t dedupe;
  std::vector<RtdlBfsExpandRow>* rows;
};

struct GraphTriangleProbeQueryState {
  const std::vector<GraphEdgePoint>* edge_points;
  std::vector<uint32_t>* neighbor_marks;
  uint32_t mark;
  std::vector<uint32_t>* neighbors;
};

struct FixedRadiusNeighborsQueryState {
  const Point2D* query;
  const std::vector<Point2D>* search_points;
  double radius;
  std::vector<RtdlFixedRadiusNeighborRow>* rows;
  std::unordered_set<uint32_t>* seen_neighbor_ids;
};

struct FixedRadiusNeighborsQueryState3D {
  const Point3D* query;
  const std::vector<Point3D>* search_points;
  double radius;
  std::vector<RtdlFixedRadiusNeighborRow>* rows;
  std::unordered_set<uint32_t>* seen_neighbor_ids;
};

struct KnnRowsQueryState {
  const Point2D* query;
  const std::vector<Point2D>* search_points;
  size_t k;
  std::vector<RtdlKnnNeighborRow>* rows;
  std::unordered_set<uint32_t>* seen_neighbor_ids;
};

struct KnnRowsQueryState3D {
  const Point3D* query;
  const std::vector<Point3D>* search_points;
  size_t k;
  std::vector<RtdlKnnNeighborRow>* rows;
  std::unordered_set<uint32_t>* seen_neighbor_ids;
};

thread_local QueryKind g_query_kind = QueryKind::kNone;
thread_local void* g_query_state = nullptr;

bool knn_row_is_better(const RtdlKnnNeighborRow& candidate, const RtdlKnnNeighborRow& current) {
  if (candidate.distance < current.distance - 1.0e-12) {
    return true;
  }
  if (current.distance < candidate.distance - 1.0e-12) {
    return false;
  }
  return candidate.neighbor_id < current.neighbor_id;
}

size_t knn_worst_index(const std::vector<RtdlKnnNeighborRow>& rows) {
  size_t worst_index = 0;
  for (size_t index = 1; index < rows.size(); ++index) {
    if (knn_row_is_better(rows[worst_index], rows[index])) {
      worst_index = index;
    }
  }
  return worst_index;
}

void tighten_knn_query_radius(
    RTCPointQuery* query,
    const std::vector<RtdlKnnNeighborRow>& rows,
    size_t k) {
  if (query == nullptr || rows.size() < k || rows.empty()) {
    return;
  }
  const size_t worst_index = knn_worst_index(rows);
  query->radius = static_cast<float>(rows[worst_index].distance + 1.0e-6);
}

void append_knn_candidate(
    RTCPointQueryFunctionArguments* args,
    std::vector<RtdlKnnNeighborRow>* rows,
    std::unordered_set<uint32_t>* seen_neighbor_ids,
    size_t k,
    const RtdlKnnNeighborRow& candidate) {
  if (seen_neighbor_ids->find(candidate.neighbor_id) != seen_neighbor_ids->end()) {
    return;
  }
  if (rows->size() < k) {
    rows->push_back(candidate);
    seen_neighbor_ids->insert(candidate.neighbor_id);
    tighten_knn_query_radius(args != nullptr ? args->query : nullptr, *rows, k);
    return;
  }
  const size_t worst_index = knn_worst_index(*rows);
  if (!knn_row_is_better(candidate, (*rows)[worst_index])) {
    return;
  }
  seen_neighbor_ids->erase((*rows)[worst_index].neighbor_id);
  (*rows)[worst_index] = candidate;
  seen_neighbor_ids->insert(candidate.neighbor_id);
  tighten_knn_query_radius(args != nullptr ? args->query : nullptr, *rows, k);
}

void set_ray(RTCRayHit* rayhit, const Vec2& origin, const Vec2& direction, float tmax) {
  std::memset(rayhit, 0, sizeof(RTCRayHit));
  rayhit->ray.org_x = origin.x;
  rayhit->ray.org_y = origin.y;
  rayhit->ray.org_z = 0.0f;
  rayhit->ray.tnear = 0.0f;
  rayhit->ray.dir_x = direction.x;
  rayhit->ray.dir_y = direction.y;
  rayhit->ray.dir_z = 0.0f;
  rayhit->ray.time = 0.0f;
  rayhit->ray.tfar = tmax;
  rayhit->ray.mask = 0xffffffffu;
  rayhit->ray.id = 0;
  rayhit->ray.flags = 0;
  rayhit->hit.geomID = RTC_INVALID_GEOMETRY_ID;
  rayhit->hit.primID = RTC_INVALID_GEOMETRY_ID;
  for (unsigned i = 0; i < RTC_MAX_INSTANCE_LEVEL_COUNT; ++i) {
    rayhit->hit.instID[i] = RTC_INVALID_GEOMETRY_ID;
  }
}

void set_ray_3d(RTCRayHit* rayhit, const Vec3& origin, const Vec3& direction, float tmax) {
  std::memset(rayhit, 0, sizeof(RTCRayHit));
  rayhit->ray.org_x = origin.x;
  rayhit->ray.org_y = origin.y;
  rayhit->ray.org_z = origin.z;
  rayhit->ray.tnear = 0.0f;
  rayhit->ray.dir_x = direction.x;
  rayhit->ray.dir_y = direction.y;
  rayhit->ray.dir_z = direction.z;
  rayhit->ray.time = 0.0f;
  rayhit->ray.tfar = tmax;
  rayhit->ray.mask = 0xffffffffu;
  rayhit->ray.id = 0;
  rayhit->ray.flags = 0;
  rayhit->hit.geomID = RTC_INVALID_GEOMETRY_ID;
  rayhit->hit.primID = RTC_INVALID_GEOMETRY_ID;
  for (unsigned i = 0; i < RTC_MAX_INSTANCE_LEVEL_COUNT; ++i) {
    rayhit->hit.instID[i] = RTC_INVALID_GEOMETRY_ID;
  }
}

void segment_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<SegmentSceneData*>(args->geometryUserPtr);
  const Segment2D& segment = (*data->segments)[args->primID];
  Bounds2D b = bounds_for_segment(segment);
  args->bounds_o->lower_x = b.min_x;
  args->bounds_o->lower_y = b.min_y;
  args->bounds_o->lower_z = -kEps;
  args->bounds_o->upper_x = b.max_x;
  args->bounds_o->upper_y = b.max_y;
  args->bounds_o->upper_z = kEps;
}

void polygon_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<PolygonSceneData*>(args->geometryUserPtr);
  const Polygon2D& polygon = (*data->polygons)[args->primID];
  Bounds2D b = bounds_for_polygon(polygon);
  args->bounds_o->lower_x = b.min_x;
  args->bounds_o->lower_y = b.min_y;
  args->bounds_o->lower_z = -kEps;
  args->bounds_o->upper_x = b.max_x;
  args->bounds_o->upper_y = b.max_y;
  args->bounds_o->upper_z = kEps;
}

void point_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<PointSceneData*>(args->geometryUserPtr);
  const Point2D& point = (*data->points)[args->primID];
  args->bounds_o->lower_x = point.p.x - kEps;
  args->bounds_o->lower_y = point.p.y - kEps;
  args->bounds_o->lower_z = -kEps;
  args->bounds_o->upper_x = point.p.x + kEps;
  args->bounds_o->upper_y = point.p.y + kEps;
  args->bounds_o->upper_z = kEps;
}

void point_bounds_3d(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<PointSceneData3D*>(args->geometryUserPtr);
  const Point3D& point = (*data->points)[args->primID];
  args->bounds_o->lower_x = point.p.x - kEps;
  args->bounds_o->lower_y = point.p.y - kEps;
  args->bounds_o->lower_z = point.p.z - kEps;
  args->bounds_o->upper_x = point.p.x + kEps;
  args->bounds_o->upper_y = point.p.y + kEps;
  args->bounds_o->upper_z = point.p.z + kEps;
}

void graph_edge_point_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<GraphEdgePointSceneData*>(args->geometryUserPtr);
  const GraphEdgePoint& point = (*data->points)[args->primID];
  args->bounds_o->lower_x = point.p.x - kEps;
  args->bounds_o->lower_y = point.p.y - kEps;
  args->bounds_o->lower_z = -kEps;
  args->bounds_o->upper_x = point.p.x + kEps;
  args->bounds_o->upper_y = point.p.y + kEps;
  args->bounds_o->upper_z = kEps;
}

void triangle_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<TriangleSceneData*>(args->geometryUserPtr);
  const Triangle2D& triangle = (*data->triangles)[args->primID];
  Bounds2D b = bounds_for_triangle(triangle);
  args->bounds_o->lower_x = b.min_x;
  args->bounds_o->lower_y = b.min_y;
  args->bounds_o->lower_z = -kEps;
  args->bounds_o->upper_x = b.max_x;
  args->bounds_o->upper_y = b.max_y;
  args->bounds_o->upper_z = kEps;
}

void triangle_bounds_3d(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<TriangleSceneData3D*>(args->geometryUserPtr);
  const Triangle3D& triangle = (*data->triangles)[args->primID];
  Bounds3D b = bounds_for_triangle_3d(triangle);
  args->bounds_o->lower_x = b.min_x;
  args->bounds_o->lower_y = b.min_y;
  args->bounds_o->lower_z = b.min_z;
  args->bounds_o->upper_x = b.max_x;
  args->bounds_o->upper_y = b.max_y;
  args->bounds_o->upper_z = b.max_z;
}

void segment_intersect(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_kind != QueryKind::kLsi || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<SegmentSceneData*>(args->geometryUserPtr);
  auto* state = static_cast<LsiQueryState*>(g_query_state);
  const Segment2D& build = (*data->segments)[args->primID];
  Vec2 point {};
  if (segment_intersection(*state->probe, build, &point)) {
    // LSI collects all intersecting build segments directly from the user-geometry
    // callback; this path is not limited to a single closest-hit row.
    state->rows->push_back({state->probe->id, build.id, point.x, point.y});
  }
}

void polygon_intersect(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<PolygonSceneData*>(args->geometryUserPtr);
  const Polygon2D& polygon = (*data->polygons)[args->primID];
  if (g_query_kind == QueryKind::kPip) {
    auto* rayhit = reinterpret_cast<RTCRayHit*>(args->rayhit);
    rayhit->ray.tfar = 0.0f;
    rayhit->hit.geomID = args->geomID;
    rayhit->hit.primID = args->primID;
    rayhit->hit.u = 0.0f;
    rayhit->hit.v = 0.0f;
    rayhit->hit.Ng_x = 0.0f;
    rayhit->hit.Ng_y = 0.0f;
    rayhit->hit.Ng_z = 1.0f;
    RTCFilterFunctionNArguments filter_args;
    filter_args.valid = args->valid;
    filter_args.geometryUserPtr = args->geometryUserPtr;
    filter_args.context = args->context;
    filter_args.ray = reinterpret_cast<RTCRayN*>(&rayhit->ray);
    filter_args.hit = reinterpret_cast<RTCHitN*>(&rayhit->hit);
    filter_args.N = 1;
    rtcInvokeIntersectFilterFromGeometry(args, &filter_args);
    return;
  }
  if (g_query_kind == QueryKind::kOverlay) {
    auto* state = static_cast<OverlayQueryState*>(g_query_state);
    bool requires_lsi = false;
    bool requires_pip = false;
    if (polygon_pair_flags(*state->left, polygon, &requires_lsi, &requires_pip)) {
      OverlayPairFlags& flags = (*state->flags_by_right_id)[polygon.id];
      if (requires_lsi) {
        flags.requires_lsi = 1;
      }
      if (requires_pip) {
        flags.requires_pip = 1;
      }
    }
    return;
  }
  if (g_query_kind == QueryKind::kSegmentPolygonHitCount) {
    auto* state = static_cast<SegmentPolygonHitCountState*>(g_query_state);
    if (segment_hits_polygon(*state->segment, polygon)) {
      *state->hit_count += 1;
    }
  }
}

void polygon_intersect_filter(const RTCFilterFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_kind != QueryKind::kPip || g_query_state == nullptr) {
    return;
  }
  auto* state = static_cast<PipQueryState*>(g_query_state);
  const auto* hit = reinterpret_cast<const RTCHit*>(args->hit);
  state->candidate_polygon_indices->insert(hit->primID);
  args->valid[0] = 0;
}

bool polygon_point_query_collect(RTCPointQueryFunctionArguments* args) {
  if (args == nullptr || args->userPtr == nullptr) {
    return false;
  }
  auto* state = static_cast<PipQueryState*>(args->userPtr);
  state->candidate_polygon_indices->insert(args->primID);
  return false;
}

bool point_point_query_collect(RTCPointQueryFunctionArguments* args) {
  if (args == nullptr || args->userPtr == nullptr) {
    return false;
  }
  if (g_query_kind == QueryKind::kGraphBfsExpand) {
    auto* state = static_cast<GraphBfsExpandQueryState*>(args->userPtr);
    const GraphEdgePoint& edge_point = (*state->edge_points)[args->primID];
    if ((*state->visited_flags)[edge_point.dst_vertex] != 0u) {
      return false;
    }
    if (state->dedupe != 0u && (*state->discovered_flags)[edge_point.dst_vertex] != 0u) {
      return false;
    }
    (*state->discovered_flags)[edge_point.dst_vertex] = 1u;
    state->rows->push_back(
        {state->frontier_vertex->vertex_id, edge_point.dst_vertex, state->frontier_vertex->level + 1u});
    return false;
  }
  if (g_query_kind == QueryKind::kGraphTriangleProbe) {
    auto* state = static_cast<GraphTriangleProbeQueryState*>(args->userPtr);
    const GraphEdgePoint& edge_point = (*state->edge_points)[args->primID];
    if ((*state->neighbor_marks)[edge_point.dst_vertex] == state->mark) {
      return false;
    }
    (*state->neighbor_marks)[edge_point.dst_vertex] = state->mark;
    state->neighbors->push_back(edge_point.dst_vertex);
    return false;
  }
  if (g_query_kind == QueryKind::kFixedRadiusNeighbors) {
    auto* state = static_cast<FixedRadiusNeighborsQueryState*>(args->userPtr);
    const Point2D& search_point = (*state->search_points)[args->primID];
    if (state->seen_neighbor_ids->find(search_point.id) != state->seen_neighbor_ids->end()) {
      return false;
    }
    double dx = search_point.p.x - state->query->p.x;
    double dy = search_point.p.y - state->query->p.y;
    double distance = std::sqrt(dx * dx + dy * dy);
    if (distance <= state->radius) {
      state->seen_neighbor_ids->insert(search_point.id);
      state->rows->push_back({state->query->id, search_point.id, distance});
    }
    return false;
  }
  auto* state = static_cast<KnnRowsQueryState*>(args->userPtr);
  const Point2D& search_point = (*state->search_points)[args->primID];
  double dx = search_point.p.x - state->query->p.x;
  double dy = search_point.p.y - state->query->p.y;
  double distance = std::sqrt(dx * dx + dy * dy);
  append_knn_candidate(
      args,
      state->rows,
      state->seen_neighbor_ids,
      state->k,
      {state->query->id, search_point.id, distance, 0u});
  return false;
}

bool point_point_query_collect_3d(RTCPointQueryFunctionArguments* args) {
  if (args == nullptr || args->userPtr == nullptr) {
    return false;
  }
  if (g_query_kind == QueryKind::kFixedRadiusNeighbors3D) {
    auto* state = static_cast<FixedRadiusNeighborsQueryState3D*>(args->userPtr);
    const Point3D& search_point = (*state->search_points)[args->primID];
    if (state->seen_neighbor_ids->find(search_point.id) != state->seen_neighbor_ids->end()) {
      return false;
    }
    double dx = search_point.p.x - state->query->p.x;
    double dy = search_point.p.y - state->query->p.y;
    double dz = search_point.p.z - state->query->p.z;
    double distance = std::sqrt(dx * dx + dy * dy + dz * dz);
    if (distance <= state->radius) {
      state->seen_neighbor_ids->insert(search_point.id);
      state->rows->push_back({state->query->id, search_point.id, distance});
    }
    return false;
  }
  if (g_query_kind == QueryKind::kKnnRows3D) {
    auto* state = static_cast<KnnRowsQueryState3D*>(args->userPtr);
    const Point3D& search_point = (*state->search_points)[args->primID];
    double dx = search_point.p.x - state->query->p.x;
    double dy = search_point.p.y - state->query->p.y;
    double dz = search_point.p.z - state->query->p.z;
    double distance = std::sqrt(dx * dx + dy * dy + dz * dz);
    append_knn_candidate(
        args,
        state->rows,
        state->seen_neighbor_ids,
        state->k,
        {state->query->id, search_point.id, distance, 0u});
    return false;
  }
  return false;
}

void triangle_intersect(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_kind != QueryKind::kRayHitCount || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<TriangleSceneData*>(args->geometryUserPtr);
  auto* state = static_cast<RayHitCountState*>(g_query_state);
  const Triangle2D& triangle = (*data->triangles)[args->primID];
  if (state->seen_triangle_ids->find(triangle.id) != state->seen_triangle_ids->end()) {
    return;
  }
  if (finite_ray_hits_triangle(*state->ray, triangle)) {
    state->seen_triangle_ids->insert(triangle.id);
    *state->hit_count += 1;
  }
}

void triangle_intersect_3d(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_kind != QueryKind::kRayHitCount || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<TriangleSceneData3D*>(args->geometryUserPtr);
  auto* state = static_cast<RayHitCountState3D*>(g_query_state);
  const Triangle3D& triangle = (*data->triangles)[args->primID];
  if (state->seen_triangle_ids->find(triangle.id) != state->seen_triangle_ids->end()) {
    return;
  }
  if (finite_ray_hits_triangle_3d(*state->ray, triangle)) {
    state->seen_triangle_ids->insert(triangle.id);
    *state->hit_count += 1;
  }
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
    Polygon2D polygon;
    polygon.id = ref.id;
    for (size_t j = 0; j < ref.vertex_count; ++j) {
      size_t index = static_cast<size_t>(ref.vertex_offset) + j;
      polygon.vertices.push_back({vertices_xy[index * 2], vertices_xy[index * 2 + 1]});
    }
    polygons.push_back(std::move(polygon));
  }
  return polygons;
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
