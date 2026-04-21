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
  kRayAnyHit,
  kRayClosestHit,
  kSegmentPolygonHitCount,
  kGraphBfsExpand,
  kGraphTriangleProbe,
  kFixedRadiusNeighbors,
  kFixedRadiusNeighbors3D,
  kFixedRadiusCountThreshold,
  kKnnRows,
  kKnnRows3D,
  kDbScanRay,
  kDbGroupedCountRay,
  kDbGroupedSumRay,
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

struct DbRowBox {
  size_t row_index;
  uint32_t row_id;
  double x;
  double y;
  double z;
};

struct DbRowBoxSceneData {
  const std::vector<DbRowBox>* boxes;
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

struct RayAnyHitState {
  const RayQuery2D* ray;
  uint32_t* any_hit;
};

struct RayAnyHitState3D {
  const RayQuery3D* ray;
  uint32_t* any_hit;
};

struct RayClosestHitState3D {
  const RayQuery3D* ray;
  uint32_t* best_triangle_id;
  double* best_t;
  bool* has_hit;
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

struct FixedRadiusCountThresholdQueryState {
  const Point2D* query;
  const std::vector<Point2D>* search_points;
  double radius_squared;
  size_t threshold;
  uint32_t neighbor_count;
  uint32_t threshold_reached;
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

struct DbScanRayQueryState {
  const RtdlDbField* fields;
  size_t field_count;
  const RtdlDbScalar* row_values;
  size_t row_count;
  const RtdlDbClause* clauses;
  size_t clause_count;
  size_t max_candidate_rows;
  std::unordered_set<uint32_t>* seen_row_ids;
  std::vector<RtdlDbRowIdRow>* rows;
};

struct DbGroupedCountRayQueryState {
  const RtdlDbField* fields;
  size_t field_count;
  const RtdlDbScalar* row_values;
  size_t row_count;
  const RtdlDbClause* clauses;
  size_t clause_count;
  size_t group_field_index;
  size_t max_candidate_rows;
  size_t max_groups;
  std::unordered_set<uint32_t>* seen_row_ids;
  std::unordered_map<int64_t, int64_t>* counts;
};

struct DbGroupedSumRayQueryState {
  const RtdlDbField* fields;
  size_t field_count;
  const RtdlDbScalar* row_values;
  size_t row_count;
  const RtdlDbClause* clauses;
  size_t clause_count;
  size_t group_field_index;
  size_t value_field_index;
  size_t max_candidate_rows;
  size_t max_groups;
  std::unordered_set<uint32_t>* seen_row_ids;
  std::unordered_map<int64_t, int64_t>* sums;
};

thread_local QueryKind g_query_kind = QueryKind::kNone;
thread_local void* g_query_state = nullptr;
thread_local bool g_db_limit_error = false;
thread_local std::string g_db_limit_error_message;

constexpr uint32_t kDbKindInt64 = 1u;
constexpr uint32_t kDbKindFloat64 = 2u;
constexpr uint32_t kDbKindBool = 3u;
constexpr uint32_t kDbKindText = 4u;

constexpr uint32_t kDbOpEq = 1u;
constexpr uint32_t kDbOpLt = 2u;
constexpr uint32_t kDbOpLe = 3u;
constexpr uint32_t kDbOpGt = 4u;
constexpr uint32_t kDbOpGe = 5u;
constexpr uint32_t kDbOpBetween = 6u;

void db_set_limit_error(const char* message) {
  g_db_limit_error = true;
  g_db_limit_error_message = message;
}

void db_clear_limit_error() {
  g_db_limit_error = false;
  g_db_limit_error_message.clear();
}

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

void set_ray_occluded(RTCRay* ray, const Vec2& origin, const Vec2& direction, float tmax) {
  std::memset(ray, 0, sizeof(RTCRay));
  ray->org_x = origin.x;
  ray->org_y = origin.y;
  ray->org_z = 0.0f;
  ray->tnear = 0.0f;
  ray->dir_x = direction.x;
  ray->dir_y = direction.y;
  ray->dir_z = 0.0f;
  ray->time = 0.0f;
  ray->tfar = tmax;
  ray->mask = 0xffffffffu;
  ray->id = 0;
  ray->flags = 0;
}

void set_ray_occluded_3d(RTCRay* ray, const Vec3& origin, const Vec3& direction, float tmax) {
  std::memset(ray, 0, sizeof(RTCRay));
  ray->org_x = origin.x;
  ray->org_y = origin.y;
  ray->org_z = origin.z;
  ray->tnear = 0.0f;
  ray->dir_x = direction.x;
  ray->dir_y = direction.y;
  ray->dir_z = direction.z;
  ray->time = 0.0f;
  ray->tfar = tmax;
  ray->mask = 0xffffffffu;
  ray->id = 0;
  ray->flags = 0;
}

bool db_scalar_is_numeric(const RtdlDbScalar& value) {
  return value.kind == kDbKindInt64 || value.kind == kDbKindFloat64 || value.kind == kDbKindBool;
}

double db_scalar_as_double(const RtdlDbScalar& value) {
  if (value.kind == kDbKindInt64 || value.kind == kDbKindBool) {
    return static_cast<double>(value.int_value);
  }
  if (value.kind == kDbKindFloat64) {
    return value.double_value;
  }
  throw std::runtime_error("DB scalar is not numeric");
}

int db_scalar_compare(const RtdlDbScalar& left, const RtdlDbScalar& right) {
  if (left.kind == kDbKindText || right.kind == kDbKindText) {
    const char* left_text = left.string_value == nullptr ? "" : left.string_value;
    const char* right_text = right.string_value == nullptr ? "" : right.string_value;
    const int cmp = std::strcmp(left_text, right_text);
    if (cmp < 0) {
      return -1;
    }
    if (cmp > 0) {
      return 1;
    }
    return 0;
  }
  const double left_value = db_scalar_as_double(left);
  const double right_value = db_scalar_as_double(right);
  if (left_value < right_value) {
    return -1;
  }
  if (left_value > right_value) {
    return 1;
  }
  return 0;
}

size_t db_find_field_index(const RtdlDbField* fields, size_t field_count, const char* name) {
  for (size_t index = 0; index < field_count; ++index) {
    if (std::strcmp(fields[index].name, name) == 0) {
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

bool db_row_matches_clause(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_index,
    const RtdlDbClause& clause) {
  const size_t field_index = db_find_field_index(fields, field_count, clause.field);
  const RtdlDbScalar& row_value = db_row_value(row_values, row_index, field_count, field_index);
  const int cmp_lo = db_scalar_compare(row_value, clause.value);
  switch (clause.op) {
    case kDbOpEq:
      return cmp_lo == 0;
    case kDbOpLt:
      return cmp_lo < 0;
    case kDbOpLe:
      return cmp_lo <= 0;
    case kDbOpGt:
      return cmp_lo > 0;
    case kDbOpGe:
      return cmp_lo >= 0;
    case kDbOpBetween:
      return cmp_lo >= 0 && db_scalar_compare(row_value, clause.value_hi) <= 0;
    default:
      throw std::runtime_error("unsupported DB clause op");
  }
}

bool db_row_matches_all_clauses(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_index,
    const RtdlDbClause* clauses,
    size_t clause_count) {
  for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
    if (!db_row_matches_clause(fields, field_count, row_values, row_index, clauses[clause_index])) {
      return false;
    }
  }
  return true;
}

bool ray_hits_db_box(const RTCRay& ray, const DbRowBox& box) {
  const double half = 0.45;
  const double min_x = box.x - half;
  const double max_x = box.x + half;
  const double min_y = box.y - half;
  const double max_y = box.y + half;
  const double min_z = box.z - half;
  const double max_z = box.z + half;
  double tmin = ray.tnear;
  double tmax = ray.tfar;
  const double org[3] = {ray.org_x, ray.org_y, ray.org_z};
  const double dir[3] = {ray.dir_x, ray.dir_y, ray.dir_z};
  const double mins[3] = {min_x, min_y, min_z};
  const double maxs[3] = {max_x, max_y, max_z};
  for (int axis = 0; axis < 3; ++axis) {
    if (std::abs(dir[axis]) < 1.0e-12) {
      if (org[axis] < mins[axis] || org[axis] > maxs[axis]) {
        return false;
      }
      continue;
    }
    const double inv_dir = 1.0 / dir[axis];
    double t0 = (mins[axis] - org[axis]) * inv_dir;
    double t1 = (maxs[axis] - org[axis]) * inv_dir;
    if (t0 > t1) {
      std::swap(t0, t1);
    }
    tmin = std::max(tmin, t0);
    tmax = std::min(tmax, t1);
    if (tmin > tmax) {
      return false;
    }
  }
  return true;
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

void db_row_box_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<DbRowBoxSceneData*>(args->geometryUserPtr);
  const DbRowBox& box = (*data->boxes)[args->primID];
  const float half = 0.45f;
  args->bounds_o->lower_x = static_cast<float>(box.x) - half;
  args->bounds_o->lower_y = static_cast<float>(box.y) - half;
  args->bounds_o->lower_z = static_cast<float>(box.z) - half;
  args->bounds_o->upper_x = static_cast<float>(box.x) + half;
  args->bounds_o->upper_y = static_cast<float>(box.y) + half;
  args->bounds_o->upper_z = static_cast<float>(box.z) + half;
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
  if (g_query_kind == QueryKind::kFixedRadiusCountThreshold) {
    auto* state = static_cast<FixedRadiusCountThresholdQueryState*>(args->userPtr);
    if (state->threshold > 0 && state->threshold_reached != 0) {
      return false;
    }
    const Point2D& search_point = (*state->search_points)[args->primID];
    double dx = search_point.p.x - state->query->p.x;
    double dy = search_point.p.y - state->query->p.y;
    double distance_squared = dx * dx + dy * dy;
    if (distance_squared <= state->radius_squared) {
      ++state->neighbor_count;
      if (state->threshold > 0 && state->neighbor_count >= state->threshold) {
        state->threshold_reached = 1u;
        args->query->radius = 0.0f;
        return true;
      }
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

void triangle_occluded(const RTCOccludedFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_kind != QueryKind::kRayAnyHit || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<TriangleSceneData*>(args->geometryUserPtr);
  auto* state = static_cast<RayAnyHitState*>(g_query_state);
  const Triangle2D& triangle = (*data->triangles)[args->primID];
  if (finite_ray_hits_triangle(*state->ray, triangle)) {
    *state->any_hit = 1u;
    auto* ray = reinterpret_cast<RTCRay*>(args->ray);
    ray->tfar = -std::numeric_limits<float>::infinity();
  }
}

void triangle_intersect_3d(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<TriangleSceneData3D*>(args->geometryUserPtr);
  const Triangle3D& triangle = (*data->triangles)[args->primID];
  if (g_query_kind == QueryKind::kRayHitCount) {
    auto* state = static_cast<RayHitCountState3D*>(g_query_state);
    if (state->seen_triangle_ids->find(triangle.id) != state->seen_triangle_ids->end()) {
      return;
    }
    if (finite_ray_hits_triangle_3d(*state->ray, triangle)) {
      state->seen_triangle_ids->insert(triangle.id);
      *state->hit_count += 1;
    }
    return;
  }
  if (g_query_kind == QueryKind::kRayClosestHit) {
    auto* state = static_cast<RayClosestHitState3D*>(g_query_state);
    if (state->seen_triangle_ids->find(triangle.id) != state->seen_triangle_ids->end()) {
      return;
    }
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
        state->ray->d.y * edge2.z - state->ray->d.z * edge2.y,
        state->ray->d.z * edge2.x - state->ray->d.x * edge2.z,
        state->ray->d.x * edge2.y - state->ray->d.y * edge2.x,
    };
    double det = edge1.x * pvec.x + edge1.y * pvec.y + edge1.z * pvec.z;
    if (std::fabs(det) <= 1.0e-8) {
      return;
    }
    double inv_det = 1.0 / det;
    Vec3 tvec {
        state->ray->o.x - triangle.a.x,
        state->ray->o.y - triangle.a.y,
        state->ray->o.z - triangle.a.z,
    };
    double u = (tvec.x * pvec.x + tvec.y * pvec.y + tvec.z * pvec.z) * inv_det;
    if (u < 0.0 || u > 1.0) {
      return;
    }
    Vec3 qvec {
        tvec.y * edge1.z - tvec.z * edge1.y,
        tvec.z * edge1.x - tvec.x * edge1.z,
        tvec.x * edge1.y - tvec.y * edge1.x,
    };
    double v = (state->ray->d.x * qvec.x + state->ray->d.y * qvec.y + state->ray->d.z * qvec.z) * inv_det;
    if (v < 0.0 || (u + v) > 1.0) {
      return;
    }
    double hit_t = (edge2.x * qvec.x + edge2.y * qvec.y + edge2.z * qvec.z) * inv_det;
    if (hit_t < 0.0 || hit_t > state->ray->tmax) {
      return;
    }
    state->seen_triangle_ids->insert(triangle.id);
    if (!*state->has_hit || hit_t < *state->best_t || (hit_t == *state->best_t && triangle.id < *state->best_triangle_id)) {
      *state->has_hit = true;
      *state->best_t = hit_t;
      *state->best_triangle_id = triangle.id;
    }
  }
}

void triangle_occluded_3d(const RTCOccludedFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_kind != QueryKind::kRayAnyHit || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<TriangleSceneData3D*>(args->geometryUserPtr);
  auto* state = static_cast<RayAnyHitState3D*>(g_query_state);
  const Triangle3D& triangle = (*data->triangles)[args->primID];
  if (finite_ray_hits_triangle_3d(*state->ray, triangle)) {
    *state->any_hit = 1u;
    auto* ray = reinterpret_cast<RTCRay*>(args->ray);
    ray->tfar = -std::numeric_limits<float>::infinity();
  }
}

void db_row_box_intersect(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_state == nullptr) {
    return;
  }
  if (g_db_limit_error) {
    return;
  }
  if (g_query_kind != QueryKind::kDbScanRay
      && g_query_kind != QueryKind::kDbGroupedCountRay
      && g_query_kind != QueryKind::kDbGroupedSumRay) {
    return;
  }
  auto* data = static_cast<DbRowBoxSceneData*>(args->geometryUserPtr);
  const DbRowBox& box = (*data->boxes)[args->primID];
  const auto* rayhit = reinterpret_cast<const RTCRayHit*>(args->rayhit);
  if (!ray_hits_db_box(rayhit->ray, box)) {
    return;
  }
  if (g_query_kind == QueryKind::kDbScanRay) {
    auto* state = static_cast<DbScanRayQueryState*>(g_query_state);
    if (state->seen_row_ids->find(box.row_id) != state->seen_row_ids->end()) {
      return;
    }
    if (!db_row_matches_all_clauses(
            state->fields,
            state->field_count,
            state->row_values,
            box.row_index,
            state->clauses,
            state->clause_count)) {
      return;
    }
    state->seen_row_ids->insert(box.row_id);
    if (state->seen_row_ids->size() > state->max_candidate_rows) {
      db_set_limit_error("first-wave Embree DB lowering exceeded the 250000-candidate ceiling");
      return;
    }
    state->rows->push_back({box.row_id});
    return;
  }
  if (g_query_kind == QueryKind::kDbGroupedCountRay) {
    auto* state = static_cast<DbGroupedCountRayQueryState*>(g_query_state);
    if (state->seen_row_ids->find(box.row_id) != state->seen_row_ids->end()) {
      return;
    }
    if (!db_row_matches_all_clauses(
            state->fields,
            state->field_count,
            state->row_values,
            box.row_index,
            state->clauses,
            state->clause_count)) {
      return;
    }
    state->seen_row_ids->insert(box.row_id);
    if (state->seen_row_ids->size() > state->max_candidate_rows) {
      db_set_limit_error("first-wave Embree DB lowering exceeded the 250000-candidate ceiling");
      return;
    }
    const RtdlDbScalar& group_value = db_row_value(
        state->row_values,
        box.row_index,
        state->field_count,
        state->group_field_index);
    (*state->counts)[group_value.int_value] += 1;
    if (state->counts->size() > state->max_groups) {
      db_set_limit_error("first-wave Embree DB grouped kernels exceeded the 65536-group ceiling");
    }
    return;
  }
  auto* state = static_cast<DbGroupedSumRayQueryState*>(g_query_state);
  if (state->seen_row_ids->find(box.row_id) != state->seen_row_ids->end()) {
    return;
  }
  if (!db_row_matches_all_clauses(
          state->fields,
          state->field_count,
          state->row_values,
          box.row_index,
          state->clauses,
          state->clause_count)) {
    return;
  }
  state->seen_row_ids->insert(box.row_id);
  if (state->seen_row_ids->size() > state->max_candidate_rows) {
    db_set_limit_error("first-wave Embree DB lowering exceeded the 250000-candidate ceiling");
    return;
  }
  const RtdlDbScalar& group_value = db_row_value(
      state->row_values,
      box.row_index,
      state->field_count,
      state->group_field_index);
  const RtdlDbScalar& sum_value = db_row_value(
      state->row_values,
      box.row_index,
      state->field_count,
      state->value_field_index);
  if (sum_value.kind != kDbKindInt64 && sum_value.kind != kDbKindBool) {
    db_set_limit_error("first-wave Embree grouped_sum supports integer-compatible value fields only");
    return;
  }
  (*state->sums)[group_value.int_value] += sum_value.int_value;
  if (state->sums->size() > state->max_groups) {
    db_set_limit_error("first-wave Embree DB grouped kernels exceeded the 65536-group ceiling");
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
