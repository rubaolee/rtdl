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

void apply_scene_build_quality_from_env(RTCScene scene, const char* env_name) {
  const char* raw = std::getenv(env_name);
  if (raw == nullptr || raw[0] == '\0') {
    return;
  }
  const std::string value(raw);
  if (value == "low") {
    rtcSetSceneBuildQuality(scene, RTC_BUILD_QUALITY_LOW);
  } else if (value == "medium") {
    rtcSetSceneBuildQuality(scene, RTC_BUILD_QUALITY_MEDIUM);
  } else if (value == "high") {
    rtcSetSceneBuildQuality(scene, RTC_BUILD_QUALITY_HIGH);
  } else if (value == "refit") {
    rtcSetSceneBuildQuality(scene, RTC_BUILD_QUALITY_REFIT);
  } else {
    throw std::runtime_error(std::string(env_name) + " must be one of: low, medium, high, refit");
  }
}

constexpr float kBvhCandidatePad = 2.5e-1f;
constexpr float kRayjoinCdbBoundsPad = 1.0e-4f;

enum class QueryKind {
  kNone,
  kSegmentPairIntersection,
  kPip,
  kShapePairRelation,
  kRayHitCount,
  kRayAnyHit,
  kRayClosestHit,
  kRayPrimitiveGroupedI64Reduction3D,
  kRayTriangleHitStream3D,
  kSegmentPolygonHitCount,
  kGraphBfsExpand,
  kGraphTriangleProbe,
  kFixedRadiusNeighbors,
  kFixedRadiusNeighbors3D,
  kFixedRadiusCountThreshold,
  kFixedRadiusCountThreshold3D,
  kNearestPoint,
  kKnnRows,
  kKnnRows3D,
  kColumnarPredicateScanRay,
  kColumnarGroupedCountRay,
  kColumnarGroupedSumRay,
  kRayjoinCdbPointLocation,
};

struct SegmentSceneData {
  const std::vector<Segment2D>* segments;
};

struct RayjoinCdbSegment2D {
  uint32_t id;
  Vec2 a;
  Vec2 b;
  uint32_t left_face_id;
  uint32_t right_face_id;
  int64_t rayjoin_x0 = 0;
  int64_t rayjoin_y0 = 0;
  int64_t rayjoin_x1 = 0;
  int64_t rayjoin_y1 = 0;
  bool has_rayjoin_scale = false;
};

struct RayjoinCdbSegmentSceneData {
  const std::vector<RayjoinCdbSegment2D>* segments;
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

struct ColumnarRowBox {
  size_t row_index;
  uint32_t row_id;
  double x;
  double y;
  double z;
};

struct ColumnarRowBoxSceneData {
  const std::vector<ColumnarRowBox>* boxes;
};

struct Aabb2DSceneData {
  const std::vector<RtdlAabb2D>* boxes;
};

struct TriangleSceneData {
  const std::vector<Triangle2D>* triangles;
};

struct TriangleSceneData3D {
  const std::vector<Triangle3D>* triangles;
};

struct SegmentPairIntersectionQueryState {
  const Segment2D* probe;
  std::vector<std::pair<size_t, RtdlSegmentPairIntersectionRow>>* rows;
  const std::vector<size_t>* build_order_by_primitive;
  uint32_t predicate_mode;
};

struct PipQueryState {
  const Point2D* point;
  std::unordered_set<uint32_t>* candidate_polygon_indices;
};

struct ShapePairRelationFlags {
  uint32_t requires_segment_intersection;
  uint32_t requires_point_containment;
};

struct ShapePairRelationQueryState {
  const Polygon2D* left;
  std::unordered_map<uint32_t, ShapePairRelationFlags>* flags_by_right_id;
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

struct RayjoinCdbPointLocationQueryState {
  const Point2D* point;
  uint32_t* best_primitive_index;
  uint32_t* best_segment_id;
  double* best_t;
  double* best_y;
  double* best_slope;
  bool* has_hit;
  uint32_t query_map_id;
  int64_t rayjoin_x = 0;
  int64_t rayjoin_y = 0;
  double rayjoin_rry = 0.0;
  bool has_rayjoin_scale = false;
  bool allow_equal_ties = false;
};

struct RayPrimitiveGroupedI64ReductionState3D {
  const RayQuery3D* ray;
  std::unordered_set<uint32_t>* seen_primitive_indices;
  uint64_t* hit_event_count;
};

struct RayTriangleHitStreamState3D {
  const RayQuery3D* ray;
  std::vector<RtdlRayTriangleHitStreamRow>* rows;
  std::unordered_set<uint32_t>* local_seen_primitive_indices;
  uint64_t* hit_event_count;
  bool deduplicate_primitives;
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
  uint32_t query_vertex;
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
  std::unordered_set<uint32_t>* seen_neighbor_ids;
};

struct FixedRadiusCountThresholdQueryState3D {
  const Point3D* query;
  const std::vector<Point3D>* search_points;
  double radius_squared;
  size_t threshold;
  uint32_t neighbor_count;
  uint32_t threshold_reached;
  std::unordered_set<uint32_t>* seen_neighbor_ids;
};

struct NearestPointQueryState {
  const Point2D* query;
  const std::vector<Point2D>* search_points;
  uint32_t best_neighbor_id;
  double best_distance;
  bool has_hit;
};

struct KnnRowsQueryState {
  const Point2D* query;
  const std::vector<Point2D>* search_points;
  size_t k;
  std::vector<RtdlKnnNeighborRow>* rows;
};

struct KnnRowsQueryState3D {
  const Point3D* query;
  const std::vector<Point3D>* search_points;
  size_t k;
  std::vector<RtdlKnnNeighborRow>* rows;
};

struct ColumnarPredicateScanRayQueryState {
  const RtdlColumnField* fields;
  size_t field_count;
  const RtdlColumnScalar* row_values;
  size_t row_count;
  const RtdlColumnClause* clauses;
  size_t clause_count;
  size_t max_candidate_rows;
  std::unordered_set<uint32_t>* seen_row_ids;
  std::vector<RtdlColumnRowIdRow>* rows;
};

struct ColumnarGroupedCountRayQueryState {
  const RtdlColumnField* fields;
  size_t field_count;
  const RtdlColumnScalar* row_values;
  size_t row_count;
  const RtdlColumnClause* clauses;
  size_t clause_count;
  size_t group_field_index;
  size_t max_candidate_rows;
  size_t max_groups;
  std::unordered_set<uint32_t>* seen_row_ids;
  std::unordered_map<int64_t, int64_t>* counts;
};

struct ColumnarGroupedSumRayQueryState {
  const RtdlColumnField* fields;
  size_t field_count;
  const RtdlColumnScalar* row_values;
  size_t row_count;
  const RtdlColumnClause* clauses;
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
thread_local bool g_columnar_limit_error = false;
thread_local std::string g_columnar_limit_error_message;

constexpr uint32_t kColumnKindInt64 = 1u;
constexpr uint32_t kColumnKindFloat64 = 2u;
constexpr uint32_t kColumnKindBool = 3u;
constexpr uint32_t kColumnKindText = 4u;

constexpr uint32_t kColumnOpEq = 1u;
constexpr uint32_t kColumnOpLt = 2u;
constexpr uint32_t kColumnOpLe = 3u;
constexpr uint32_t kColumnOpGt = 4u;
constexpr uint32_t kColumnOpGe = 5u;
constexpr uint32_t kColumnOpBetween = 6u;

void columnar_set_limit_error(const char* message) {
  g_columnar_limit_error = true;
  g_columnar_limit_error_message = message;
}

void columnar_clear_limit_error() {
  g_columnar_limit_error = false;
  g_columnar_limit_error_message.clear();
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

bool knn_rows_have_neighbor(
    const std::vector<RtdlKnnNeighborRow>& rows,
    uint32_t neighbor_id) {
  return std::any_of(rows.begin(), rows.end(), [&](const RtdlKnnNeighborRow& row) {
    return row.neighbor_id == neighbor_id;
  });
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
    size_t k,
    const RtdlKnnNeighborRow& candidate) {
  if (knn_rows_have_neighbor(*rows, candidate.neighbor_id)) {
    return;
  }
  if (rows->size() < k) {
    rows->push_back(candidate);
    tighten_knn_query_radius(args != nullptr ? args->query : nullptr, *rows, k);
    return;
  }
  const size_t worst_index = knn_worst_index(*rows);
  if (!knn_row_is_better(candidate, (*rows)[worst_index])) {
    return;
  }
  (*rows)[worst_index] = candidate;
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

Segment2D rayjoin_lsi_trace_segment(const Segment2D& probe) {
  Segment2D trace = probe;
  if (trace.a.x == trace.b.x) {
    if (trace.a.y > trace.b.y) {
      std::swap(trace.a, trace.b);
    }
  } else if (trace.a.x > trace.b.x) {
    std::swap(trace.a, trace.b);
  }
  return trace;
}

void set_segment_pair_query_ray(
    RTCRayHit* rayhit,
    const Segment2D& probe,
    uint32_t predicate_mode) {
  const Segment2D trace = predicate_mode == 1u
      ? rayjoin_lsi_trace_segment(probe)
      : probe;
  const Vec2 direction = sub(trace.b, trace.a);
  const double endpoint_pad = predicate_mode == 1u ? 0.0 : 1.0e-4;
  Vec2 padded_origin {
      trace.a.x - direction.x * endpoint_pad,
      trace.a.y - direction.y * endpoint_pad,
  };
  set_ray(rayhit, padded_origin, direction, static_cast<float>(1.0 + endpoint_pad * 2.0));
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

bool columnar_scalar_is_numeric(const RtdlColumnScalar& value) {
  return value.kind == kColumnKindInt64 || value.kind == kColumnKindFloat64 || value.kind == kColumnKindBool;
}

double columnar_scalar_as_double(const RtdlColumnScalar& value) {
  if (value.kind == kColumnKindInt64 || value.kind == kColumnKindBool) {
    return static_cast<double>(value.int_value);
  }
  if (value.kind == kColumnKindFloat64) {
    return value.double_value;
  }
  throw std::runtime_error("columnar scalar is not numeric");
}

int columnar_scalar_compare(const RtdlColumnScalar& left, const RtdlColumnScalar& right) {
  if (left.kind == kColumnKindText || right.kind == kColumnKindText) {
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
  const double left_value = columnar_scalar_as_double(left);
  const double right_value = columnar_scalar_as_double(right);
  if (left_value < right_value) {
    return -1;
  }
  if (left_value > right_value) {
    return 1;
  }
  return 0;
}

size_t columnar_find_field_index(const RtdlColumnField* fields, size_t field_count, const char* name) {
  for (size_t index = 0; index < field_count; ++index) {
    if (std::strcmp(fields[index].name, name) == 0) {
      return index;
    }
  }
  throw std::runtime_error(std::string("unknown columnar field: ") + name);
}

const RtdlColumnScalar& columnar_row_value(
    const RtdlColumnScalar* row_values,
    size_t row_index,
    size_t field_count,
    size_t field_index) {
  return row_values[row_index * field_count + field_index];
}

bool columnar_row_matches_clause(
    const RtdlColumnField* fields,
    size_t field_count,
    const RtdlColumnScalar* row_values,
    size_t row_index,
    const RtdlColumnClause& clause) {
  const size_t field_index = columnar_find_field_index(fields, field_count, clause.field);
  const RtdlColumnScalar& row_value = columnar_row_value(row_values, row_index, field_count, field_index);
  const int cmp_lo = columnar_scalar_compare(row_value, clause.value);
  switch (clause.op) {
    case kColumnOpEq:
      return cmp_lo == 0;
    case kColumnOpLt:
      return cmp_lo < 0;
    case kColumnOpLe:
      return cmp_lo <= 0;
    case kColumnOpGt:
      return cmp_lo > 0;
    case kColumnOpGe:
      return cmp_lo >= 0;
    case kColumnOpBetween:
      return cmp_lo >= 0 && columnar_scalar_compare(row_value, clause.value_hi) <= 0;
    default:
      throw std::runtime_error("unsupported columnar clause op");
  }
}

bool columnar_row_matches_all_clauses(
    const RtdlColumnField* fields,
    size_t field_count,
    const RtdlColumnScalar* row_values,
    size_t row_index,
    const RtdlColumnClause* clauses,
    size_t clause_count) {
  for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
    if (!columnar_row_matches_clause(fields, field_count, row_values, row_index, clauses[clause_index])) {
      return false;
    }
  }
  return true;
}

bool ray_hits_columnar_box(const RTCRay& ray, const ColumnarRowBox& box) {
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
  args->bounds_o->lower_x = b.min_x - kEps;
  args->bounds_o->lower_y = b.min_y - kEps;
  args->bounds_o->lower_z = -kEps;
  args->bounds_o->upper_x = b.max_x + kEps;
  args->bounds_o->upper_y = b.max_y + kEps;
  args->bounds_o->upper_z = kEps;
}

void rayjoin_lsi_segment_bounds(const RTCBoundsFunctionArguments* args) {
  constexpr double kRayjoinLsiBoundsPad = kBvhCandidatePad;
  auto* data = static_cast<SegmentSceneData*>(args->geometryUserPtr);
  const Segment2D& segment = (*data->segments)[args->primID];
  Bounds2D b = bounds_for_segment(segment);
  args->bounds_o->lower_x = static_cast<float>(b.min_x - kRayjoinLsiBoundsPad);
  args->bounds_o->lower_y = static_cast<float>(b.min_y - kRayjoinLsiBoundsPad);
  args->bounds_o->lower_z = static_cast<float>(-kRayjoinLsiBoundsPad);
  args->bounds_o->upper_x = static_cast<float>(b.max_x + kRayjoinLsiBoundsPad);
  args->bounds_o->upper_y = static_cast<float>(b.max_y + kRayjoinLsiBoundsPad);
  args->bounds_o->upper_z = static_cast<float>(kRayjoinLsiBoundsPad);
}

void rayjoin_cdb_segment_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<RayjoinCdbSegmentSceneData*>(args->geometryUserPtr);
  const RayjoinCdbSegment2D& segment = (*data->segments)[args->primID];
  const double min_x = std::min(segment.a.x, segment.b.x);
  const double min_y = std::min(segment.a.y, segment.b.y);
  const double max_x = std::max(segment.a.x, segment.b.x);
  const double max_y = std::max(segment.a.y, segment.b.y);
  args->bounds_o->lower_x = static_cast<float>(min_x) - kRayjoinCdbBoundsPad;
  args->bounds_o->lower_y = static_cast<float>(min_y) - kRayjoinCdbBoundsPad;
  args->bounds_o->lower_z = -kRayjoinCdbBoundsPad;
  args->bounds_o->upper_x = static_cast<float>(max_x) + kRayjoinCdbBoundsPad;
  args->bounds_o->upper_y = static_cast<float>(max_y) + kRayjoinCdbBoundsPad;
  args->bounds_o->upper_z = kRayjoinCdbBoundsPad;
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
  args->bounds_o->lower_x = static_cast<float>(point.p.x) - kBvhCandidatePad;
  args->bounds_o->lower_y = static_cast<float>(point.p.y) - kBvhCandidatePad;
  args->bounds_o->lower_z = -kBvhCandidatePad;
  args->bounds_o->upper_x = static_cast<float>(point.p.x) + kBvhCandidatePad;
  args->bounds_o->upper_y = static_cast<float>(point.p.y) + kBvhCandidatePad;
  args->bounds_o->upper_z = kBvhCandidatePad;
}

void columnar_row_box_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<ColumnarRowBoxSceneData*>(args->geometryUserPtr);
  const ColumnarRowBox& box = (*data->boxes)[args->primID];
  const float half = 0.45f;
  args->bounds_o->lower_x = static_cast<float>(box.x) - half;
  args->bounds_o->lower_y = static_cast<float>(box.y) - half;
  args->bounds_o->lower_z = static_cast<float>(box.z) - half;
  args->bounds_o->upper_x = static_cast<float>(box.x) + half;
  args->bounds_o->upper_y = static_cast<float>(box.y) + half;
  args->bounds_o->upper_z = static_cast<float>(box.z) + half;
}

void aabb2d_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<Aabb2DSceneData*>(args->geometryUserPtr);
  const RtdlAabb2D& box = (*data->boxes)[args->primID];
  args->bounds_o->lower_x = static_cast<float>(std::min(box.min_x, box.max_x)) - kEps;
  args->bounds_o->lower_y = static_cast<float>(std::min(box.min_y, box.max_y)) - kEps;
  args->bounds_o->lower_z = -kEps;
  args->bounds_o->upper_x = static_cast<float>(std::max(box.min_x, box.max_x)) + kEps;
  args->bounds_o->upper_y = static_cast<float>(std::max(box.min_y, box.max_y)) + kEps;
  args->bounds_o->upper_z = kEps;
}

void triangle_bounds(const RTCBoundsFunctionArguments* args) {
  auto* data = static_cast<TriangleSceneData*>(args->geometryUserPtr);
  const Triangle2D& triangle = (*data->triangles)[args->primID];
  Bounds2D b = bounds_for_triangle(triangle);
  args->bounds_o->lower_x = b.min_x - kBvhCandidatePad;
  args->bounds_o->lower_y = b.min_y - kBvhCandidatePad;
  args->bounds_o->lower_z = -kBvhCandidatePad;
  args->bounds_o->upper_x = b.max_x + kBvhCandidatePad;
  args->bounds_o->upper_y = b.max_y + kBvhCandidatePad;
  args->bounds_o->upper_z = kBvhCandidatePad;
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

struct RayjoinCdbLine {
  __int128 a;
  __int128 b;
  __int128 c;
};

RayjoinCdbLine rayjoin_cdb_line_for_segment(const RayjoinCdbSegment2D& segment) {
  RayjoinCdbLine line;
  line.a = static_cast<__int128>(segment.rayjoin_y0) - static_cast<__int128>(segment.rayjoin_y1);
  line.b = static_cast<__int128>(segment.rayjoin_x1) - static_cast<__int128>(segment.rayjoin_x0);
  line.c = -(static_cast<__int128>(segment.rayjoin_x0) * line.a) -
           (static_cast<__int128>(segment.rayjoin_y0) * line.b);
  if (line.b < 0) {
    line.a = -line.a;
    line.b = -line.b;
    line.c = -line.c;
  }
  return line;
}

double rayjoin_cdb_segment_slope_scaled(const RayjoinCdbSegment2D& segment) {
  const RayjoinCdbLine line = rayjoin_cdb_line_for_segment(segment);
  if (line.b == 0) {
    return 0.0;
  }
  return static_cast<double>(line.a) / static_cast<double>(line.b);
}

double rayjoin_cdb_segment_slope_world(const RayjoinCdbSegment2D& segment) {
  double a = segment.a.y - segment.b.y;
  double b = segment.b.x - segment.a.x;
  if (b < 0.0) {
    a = -a;
    b = -b;
  }
  if (b == 0.0) {
    return 0.0;
  }
  return a / b;
}

bool rayjoin_cdb_vertical_ray_segment_scaled(
    const RayjoinCdbPointLocationQueryState& state,
    const RayjoinCdbSegment2D& segment,
    double* hit_y_out,
    double* hit_t_out,
    double* slope_out) {
  if (!state.has_rayjoin_scale || !segment.has_rayjoin_scale) {
    return false;
  }
  const int64_t x_min = std::min(segment.rayjoin_x0, segment.rayjoin_x1);
  const int64_t x_max = std::max(segment.rayjoin_x0, segment.rayjoin_x1);
  const int64_t excluded_x = state.query_map_id == 0u ? x_min : x_max;
  if (state.rayjoin_x < x_min || state.rayjoin_x > x_max || state.rayjoin_x == excluded_x) {
    return false;
  }

  const RayjoinCdbLine line = rayjoin_cdb_line_for_segment(segment);
  if (line.b == 0) {
    return false;
  }
  const __int128 numerator =
      -(line.a * static_cast<__int128>(state.rayjoin_x)) - line.c;
  const double xsect_y = static_cast<double>(numerator) / static_cast<double>(line.b);
  double diff_y = static_cast<double>(state.rayjoin_y) - xsect_y;
  if (diff_y == 0.0) {
    diff_y = state.query_map_id == 0u ? -static_cast<double>(line.a) : static_cast<double>(line.a);
  }
  if (diff_y == 0.0) {
    diff_y = state.query_map_id == 0u ? -static_cast<double>(line.b) : static_cast<double>(line.b);
  }
  if (diff_y > 0.0) {
    return false;
  }
  *hit_y_out = xsect_y;
  const int64_t truncated_hit_y = static_cast<int64_t>(xsect_y);
  *hit_t_out = std::max(
      0.0,
      static_cast<double>(truncated_hit_y - state.rayjoin_y) * state.rayjoin_rry);
  *slope_out = static_cast<double>(line.a) / static_cast<double>(line.b);
  return true;
}

bool rayjoin_cdb_vertical_ray_segment_t_precise(
    const Point2D& point,
    const RayjoinCdbSegment2D& segment,
    uint32_t query_map_id,
    double* t_out,
    double* slope_out) {
  constexpr double eps = 1.0e-7;
  const double point_x = static_cast<double>(static_cast<float>(point.p.x));
  const double point_y = static_cast<double>(static_cast<float>(point.p.y));
  const double ax = static_cast<double>(static_cast<float>(segment.a.x));
  const double ay = static_cast<double>(static_cast<float>(segment.a.y));
  const double bx = static_cast<double>(static_cast<float>(segment.b.x));
  const double by = static_cast<double>(static_cast<float>(segment.b.y));
  const double sx = bx - ax;
  if (std::fabs(sx) <= eps) {
    return false;
  }
  const double lo_x = std::min(ax, bx);
  const double hi_x = std::max(ax, bx);
  const double excluded_x = query_map_id == 0u ? lo_x : hi_x;
  if (point_x < lo_x - eps || point_x > hi_x + eps || std::fabs(point_x - excluded_x) <= eps) {
    return false;
  }
  const double u = (point_x - ax) / sx;
  if (u < -eps || u > 1.0 + eps) {
    return false;
  }
  const double hit_y = ay + u * (by - ay);
  double diff_y = point_y - hit_y;
  double a = ay - by;
  double b = bx - ax;
  if (b < 0.0) {
    a = -a;
    b = -b;
  }
  if (std::fabs(diff_y) <= eps) {
    diff_y = query_map_id == 0u ? -a : a;
  }
  if (std::fabs(diff_y) <= eps) {
    diff_y = query_map_id == 0u ? -b : b;
  }
  if (diff_y > eps) {
    return false;
  }
  const double t = hit_y - point_y;
  *t_out = std::max(0.0, t);
  *slope_out = a / b;
  return true;
}

bool rayjoin_cdb_vertical_ray_segment_t(
    const Point2D& point,
    const RayjoinCdbSegment2D& segment,
    uint32_t query_map_id,
    double* t_out,
    double* slope_out) {
  constexpr float eps = 1.0e-7f;
  constexpr float refine_eps = 1.0e-5f;
  const float point_x = static_cast<float>(point.p.x);
  const float point_y = static_cast<float>(point.p.y);
  const float ax = static_cast<float>(segment.a.x);
  const float ay = static_cast<float>(segment.a.y);
  const float bx = static_cast<float>(segment.b.x);
  const float by = static_cast<float>(segment.b.y);
  const float sx = bx - ax;
  if (std::fabs(sx) <= eps) {
    return false;
  }
  const float lo_x = std::min(ax, bx);
  const float hi_x = std::max(ax, bx);
  const float excluded_x = query_map_id == 0u ? lo_x : hi_x;
  if (point_x < lo_x - eps || point_x > hi_x + eps || std::fabs(point_x - excluded_x) <= eps) {
    return false;
  }
  const float u = (point_x - ax) / sx;
  if (u < -eps || u > 1.0f + eps) {
    return false;
  }
  const float hit_y = ay + u * (by - ay);
  const float diff_y = point_y - hit_y;
  if (std::fabs(diff_y) <= refine_eps) {
    return rayjoin_cdb_vertical_ray_segment_t_precise(point, segment, query_map_id, t_out, slope_out);
  }
  float a = ay - by;
  float b = bx - ax;
  if (b < 0.0f) {
    a = -a;
    b = -b;
  }
  if (diff_y > eps) {
    return false;
  }
  const float t = hit_y - point_y;
  *t_out = static_cast<double>(std::max(0.0f, t));
  *slope_out = static_cast<double>(a / b);
  return true;
}

uint32_t rayjoin_cdb_face_for_segment_direction(const RayjoinCdbSegment2D& segment) {
  if (segment.has_rayjoin_scale) {
    return segment.rayjoin_x0 < segment.rayjoin_x1
        ? segment.right_face_id
        : segment.left_face_id;
  }
  return static_cast<float>(segment.a.x) < static_cast<float>(segment.b.x)
      ? segment.right_face_id
      : segment.left_face_id;
}

void segment_intersect(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_kind != QueryKind::kSegmentPairIntersection || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<SegmentSceneData*>(args->geometryUserPtr);
  auto* state = static_cast<SegmentPairIntersectionQueryState*>(g_query_state);
  const Segment2D& build = (*data->segments)[args->primID];
  Vec2 point {};
  const bool hit = state->predicate_mode == 1u
      ? rayjoin_lsi_segment_intersection(*state->probe, build)
      : segment_intersection(*state->probe, build, &point);
  if (hit) {
    if (state->predicate_mode == 1u &&
        !segment_intersection(*state->probe, build, &point)) {
      return;
    }
    // segment-pair intersection collects all intersecting build segments directly from the user-geometry
    // callback; this path is not limited to a single closest-hit row.
    const size_t build_order = state->build_order_by_primitive == nullptr
        ? static_cast<size_t>(args->primID)
        : state->build_order_by_primitive->at(args->primID);
    state->rows->push_back({build_order, {state->probe->id, build.id, point.x, point.y}});
  }
}

void rayjoin_cdb_point_location_intersect(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 ||
      g_query_kind != QueryKind::kRayjoinCdbPointLocation ||
      g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<RayjoinCdbSegmentSceneData*>(args->geometryUserPtr);
  auto* state = static_cast<RayjoinCdbPointLocationQueryState*>(g_query_state);
  auto* rayhit = reinterpret_cast<RTCRayHit*>(args->rayhit);
  const RayjoinCdbSegment2D& segment = (*data->segments)[args->primID];
  double hit_t = 0.0;
  double hit_y = 0.0;
  double slope = 0.0;
  bool better = false;
  if (state->has_rayjoin_scale && segment.has_rayjoin_scale) {
    if (!rayjoin_cdb_vertical_ray_segment_scaled(*state, segment, &hit_y, &hit_t, &slope)) {
      return;
    }
    if (hit_t < 0.0) {
      return;
    }
    if (hit_t < static_cast<double>(rayhit->ray.tnear) - kSegmentIntersectionEps ||
        hit_t > static_cast<double>(rayhit->ray.tfar) + kSegmentIntersectionEps) {
      return;
    }
    if (!*state->has_hit || hit_y < *state->best_y) {
      better = true;
    } else if (hit_y == *state->best_y) {
      if (*state->best_primitive_index == std::numeric_limits<uint32_t>::max()) {
        better = true;
      } else {
        const RayjoinCdbSegment2D& best_segment = (*data->segments)[*state->best_primitive_index];
        const double best_slope = rayjoin_cdb_segment_slope_scaled(best_segment);
        const bool current_slope_gt = slope > best_slope;
        better = state->query_map_id == 0u ? !current_slope_gt : current_slope_gt;
      }
    }
  } else {
    if (!rayjoin_cdb_vertical_ray_segment_t(*state->point, segment, state->query_map_id, &hit_t, &slope)) {
      return;
    }
    if (hit_t < static_cast<double>(rayhit->ray.tnear) - kSegmentIntersectionEps ||
        hit_t > static_cast<double>(rayhit->ray.tfar) + kSegmentIntersectionEps) {
      return;
    }
    better =
        !*state->has_hit ||
        hit_t < *state->best_t - kSegmentIntersectionEps ||
        (std::fabs(hit_t - *state->best_t) <= kSegmentIntersectionEps &&
         ((state->query_map_id == 0u &&
           slope < rayjoin_cdb_segment_slope_world((*data->segments)[*state->best_primitive_index]) -
                       kSegmentIntersectionEps) ||
          (state->query_map_id != 0u &&
           slope > rayjoin_cdb_segment_slope_world((*data->segments)[*state->best_primitive_index]) +
                       kSegmentIntersectionEps) ||
          (std::fabs(slope - *state->best_slope) <= kSegmentIntersectionEps &&
           segment.id < *state->best_segment_id)));
  }
  if (!better) {
    return;
  }
  *state->has_hit = true;
  *state->best_t = hit_t;
  *state->best_y = hit_y;
  *state->best_slope = slope;
  *state->best_segment_id = segment.id;
  *state->best_primitive_index = static_cast<uint32_t>(args->primID);
  const float next_t = state->allow_equal_ties
      ? std::nextafter(static_cast<float>(hit_t), std::numeric_limits<float>::infinity())
      : static_cast<float>(hit_t);
  rayhit->ray.tfar = next_t;
  rayhit->hit.geomID = args->geomID;
  rayhit->hit.primID = args->primID;
  rayhit->hit.u = 0.0f;
  rayhit->hit.v = 0.0f;
  rayhit->hit.Ng_x = 0.0f;
  rayhit->hit.Ng_y = 0.0f;
  rayhit->hit.Ng_z = 1.0f;
}

void polygon_intersect_filter(const RTCFilterFunctionNArguments* args);

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
#if RTDL_EMBREE_API_MAJOR < 4
    polygon_intersect_filter(&filter_args);
#else
    rtcInvokeIntersectFilterFromGeometry(args, &filter_args);
#endif
    return;
  }
  if (g_query_kind == QueryKind::kShapePairRelation) {
    auto* state = static_cast<ShapePairRelationQueryState*>(g_query_state);
    bool requires_segment_intersection = false;
    bool requires_point_containment = false;
    if (polygon_pair_flags(*state->left, polygon, &requires_segment_intersection, &requires_point_containment)) {
      ShapePairRelationFlags& flags = (*state->flags_by_right_id)[polygon.id];
      if (requires_segment_intersection) {
        flags.requires_segment_intersection = 1;
      }
      if (requires_point_containment) {
        flags.requires_point_containment = 1;
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

void graph_edge_point_intersect(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_state == nullptr) {
    return;
  }
  auto* data = static_cast<GraphEdgePointSceneData*>(args->geometryUserPtr);
  const GraphEdgePoint& edge_point = (*data->points)[args->primID];
  if (g_query_kind == QueryKind::kGraphBfsExpand) {
    auto* state = static_cast<GraphBfsExpandQueryState*>(g_query_state);
    if (edge_point.src_vertex != state->frontier_vertex->vertex_id) {
      return;
    }
    if ((*state->visited_flags)[edge_point.dst_vertex] != 0u) {
      return;
    }
    if (state->dedupe != 0u && (*state->discovered_flags)[edge_point.dst_vertex] != 0u) {
      return;
    }
    (*state->discovered_flags)[edge_point.dst_vertex] = 1u;
    state->rows->push_back(
        {state->frontier_vertex->vertex_id, edge_point.dst_vertex, state->frontier_vertex->level + 1u});
    return;
  }
  if (g_query_kind == QueryKind::kGraphTriangleProbe) {
    auto* state = static_cast<GraphTriangleProbeQueryState*>(g_query_state);
    if (edge_point.src_vertex != state->query_vertex) {
      return;
    }
    if ((*state->neighbor_marks)[edge_point.dst_vertex] == state->mark) {
      return;
    }
    (*state->neighbor_marks)[edge_point.dst_vertex] = state->mark;
    state->neighbors->push_back(edge_point.dst_vertex);
  }
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
    if (state->seen_neighbor_ids->find(search_point.id) != state->seen_neighbor_ids->end()) {
      return false;
    }
    double dx = search_point.p.x - state->query->p.x;
    double dy = search_point.p.y - state->query->p.y;
    double distance_squared = dx * dx + dy * dy;
    if (distance_squared <= state->radius_squared) {
      state->seen_neighbor_ids->insert(search_point.id);
      ++state->neighbor_count;
      if (state->threshold > 0 && state->neighbor_count >= state->threshold) {
        state->threshold_reached = 1u;
        args->query->radius = 0.0f;
        return true;
      }
    }
    return false;
  }
  if (g_query_kind == QueryKind::kNearestPoint) {
    auto* state = static_cast<NearestPointQueryState*>(args->userPtr);
    const Point2D& search_point = (*state->search_points)[args->primID];
    double dx = search_point.p.x - state->query->p.x;
    double dy = search_point.p.y - state->query->p.y;
    double distance = std::sqrt(dx * dx + dy * dy);
    if (!state->has_hit ||
        distance < state->best_distance - 1.0e-12 ||
        (std::abs(distance - state->best_distance) <= 1.0e-12 &&
         search_point.id < state->best_neighbor_id)) {
      state->best_neighbor_id = search_point.id;
      state->best_distance = distance;
      state->has_hit = true;
      args->query->radius = static_cast<float>(distance + 1.0e-6);
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
  if (g_query_kind == QueryKind::kFixedRadiusCountThreshold3D) {
    auto* state = static_cast<FixedRadiusCountThresholdQueryState3D*>(args->userPtr);
    if (state->threshold > 0 && state->threshold_reached != 0) {
      return false;
    }
    const Point3D& search_point = (*state->search_points)[args->primID];
    if (state->seen_neighbor_ids->find(search_point.id) != state->seen_neighbor_ids->end()) {
      return false;
    }
    double dx = search_point.p.x - state->query->p.x;
    double dy = search_point.p.y - state->query->p.y;
    double dz = search_point.p.z - state->query->p.z;
    double distance_squared = dx * dx + dy * dy + dz * dz;
    if (distance_squared <= state->radius_squared) {
      state->seen_neighbor_ids->insert(search_point.id);
      ++state->neighbor_count;
      if (state->threshold > 0 && state->neighbor_count >= state->threshold) {
        state->threshold_reached = 1u;
        args->query->radius = 0.0f;
        return true;
      }
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
  if (g_query_kind == QueryKind::kRayPrimitiveGroupedI64Reduction3D) {
    auto* state = static_cast<RayPrimitiveGroupedI64ReductionState3D*>(g_query_state);
    if (finite_ray_hits_triangle_3d(*state->ray, triangle)) {
      *state->hit_event_count += 1;
      state->seen_primitive_indices->insert(static_cast<uint32_t>(args->primID));
    }
    return;
  }
  if (g_query_kind == QueryKind::kRayTriangleHitStream3D) {
    auto* state = static_cast<RayTriangleHitStreamState3D*>(g_query_state);
    if (finite_ray_hits_triangle_3d(*state->ray, triangle)) {
      *state->hit_event_count += 1;
      const auto primitive_id = static_cast<uint32_t>(args->primID);
      if (state->deduplicate_primitives) {
        const auto inserted = state->local_seen_primitive_indices->insert(primitive_id).second;
        if (!inserted) {
          return;
        }
      }
      state->rows->push_back({state->ray->id, primitive_id});
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

void columnar_row_box_intersect(const RTCIntersectFunctionNArguments* args) {
  if (args->N != 1 || args->valid[0] != -1 || g_query_state == nullptr) {
    return;
  }
  if (g_columnar_limit_error) {
    return;
  }
  if (g_query_kind != QueryKind::kColumnarPredicateScanRay
      && g_query_kind != QueryKind::kColumnarGroupedCountRay
      && g_query_kind != QueryKind::kColumnarGroupedSumRay) {
    return;
  }
  auto* data = static_cast<ColumnarRowBoxSceneData*>(args->geometryUserPtr);
  const ColumnarRowBox& box = (*data->boxes)[args->primID];
  const auto* rayhit = reinterpret_cast<const RTCRayHit*>(args->rayhit);
  if (!ray_hits_columnar_box(rayhit->ray, box)) {
    return;
  }
  if (g_query_kind == QueryKind::kColumnarPredicateScanRay) {
    auto* state = static_cast<ColumnarPredicateScanRayQueryState*>(g_query_state);
    if (state->seen_row_ids->find(box.row_id) != state->seen_row_ids->end()) {
      return;
    }
    if (!columnar_row_matches_all_clauses(
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
      columnar_set_limit_error("first-wave Embree columnar lowering exceeded the 1000000-candidate ceiling");
      return;
    }
    state->rows->push_back({box.row_id});
    return;
  }
  if (g_query_kind == QueryKind::kColumnarGroupedCountRay) {
    auto* state = static_cast<ColumnarGroupedCountRayQueryState*>(g_query_state);
    if (state->seen_row_ids->find(box.row_id) != state->seen_row_ids->end()) {
      return;
    }
    if (!columnar_row_matches_all_clauses(
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
      columnar_set_limit_error("first-wave Embree columnar lowering exceeded the 1000000-candidate ceiling");
      return;
    }
    const RtdlColumnScalar& group_value = columnar_row_value(
        state->row_values,
        box.row_index,
        state->field_count,
        state->group_field_index);
    (*state->counts)[group_value.int_value] += 1;
    if (state->counts->size() > state->max_groups) {
      columnar_set_limit_error("first-wave Embree columnar grouped kernels exceeded the 65536-group ceiling");
    }
    return;
  }
  auto* state = static_cast<ColumnarGroupedSumRayQueryState*>(g_query_state);
  if (state->seen_row_ids->find(box.row_id) != state->seen_row_ids->end()) {
    return;
  }
  if (!columnar_row_matches_all_clauses(
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
    columnar_set_limit_error("first-wave Embree columnar lowering exceeded the 1000000-candidate ceiling");
    return;
  }
  const RtdlColumnScalar& group_value = columnar_row_value(
      state->row_values,
      box.row_index,
      state->field_count,
      state->group_field_index);
  const RtdlColumnScalar& sum_value = columnar_row_value(
      state->row_values,
      box.row_index,
      state->field_count,
      state->value_field_index);
  if (sum_value.kind != kColumnKindInt64 && sum_value.kind != kColumnKindBool) {
    columnar_set_limit_error("first-wave Embree grouped_sum supports integer-compatible value fields only");
    return;
  }
  (*state->sums)[group_value.int_value] += sum_value.int_value;
  if (state->sums->size() > state->max_groups) {
    columnar_set_limit_error("first-wave Embree columnar grouped kernels exceeded the 65536-group ceiling");
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
