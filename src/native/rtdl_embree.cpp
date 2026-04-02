#include <embree4/rtcore.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <new>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

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

struct RtdlPointNearestSegmentRow {
  uint32_t point_id;
  uint32_t segment_id;
  double distance;
};

int rtdl_embree_get_version(int* major_out, int* minor_out, int* patch_out);
int rtdl_embree_run_lsi(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_pip(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlPipRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_overlay(
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
int rtdl_embree_run_ray_hitcount(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_segment_polygon_hitcount(
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
int rtdl_embree_run_point_nearest_segment(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_free_rows(void* rows);

}

namespace {

constexpr float kEps = 1.0e-6f;

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

struct RayQuery2D {
  uint32_t id;
  Vec2 o;
  Vec2 d;
  double tmax;
};

struct Bounds2D {
  double min_x;
  double min_y;
  double max_x;
  double max_y;
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
  if (std::fabs(denom) < kEps) {
    return false;
  }
  Vec2 qmp = sub(q, p);
  double t = cross(qmp, s) / denom;
  double u = cross(qmp, r) / denom;
  if (t < 0.0f || t > 1.0f || u < 0.0f || u > 1.0f) {
    return false;
  }
  if (point_out != nullptr) {
    point_out->x = p.x + t * r.x;
    point_out->y = p.y + t * r.y;
  }
  return true;
}

bool point_on_segment(const Point2D& point, const Vec2& start, const Vec2& end) {
  float cross_value = (point.p.x - start.x) * (end.y - start.y) - (point.p.y - start.y) * (end.x - start.x);
  if (std::fabs(cross_value) > kEps) {
    return false;
  }
  float dot = (point.p.x - start.x) * (end.x - start.x) + (point.p.y - start.y) * (end.y - start.y);
  if (dot < -kEps) {
    return false;
  }
  float length_sq = (end.x - start.x) * (end.x - start.x) + (end.y - start.y) * (end.y - start.y);
  if (dot - length_sq > kEps) {
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
};

struct SegmentSceneData {
  const std::vector<Segment2D>* segments;
};

struct PolygonSceneData {
  const std::vector<Polygon2D>* polygons;
};

struct TriangleSceneData {
  const std::vector<Triangle2D>* triangles;
};

struct LsiQueryState {
  const Segment2D* probe;
  std::vector<RtdlLsiRow>* rows;
};

struct PipQueryState {
  const Point2D* point;
  std::unordered_set<uint32_t>* contains_ids;
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

struct SegmentPolygonHitCountState {
  const Segment2D* segment;
  uint32_t* hit_count;
};

thread_local QueryKind g_query_kind = QueryKind::kNone;
thread_local void* g_query_state = nullptr;

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
    auto* state = static_cast<PipQueryState*>(g_query_state);
    if (point_in_polygon(*state->point, polygon)) {
      state->contains_ids->insert(polygon.id);
    }
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

}  // namespace

extern "C" int rtdl_embree_get_version(int* major_out, int* minor_out, int* patch_out) {
  if (major_out == nullptr || minor_out == nullptr || patch_out == nullptr) {
    return 1;
  }
  *major_out = RTC_VERSION_MAJOR;
  *minor_out = RTC_VERSION_MINOR;
  *patch_out = RTC_VERSION_PATCH;
  return 0;
}

extern "C" int rtdl_embree_run_lsi(
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

    EmbreeDevice device;
    SegmentSceneData data {&right_segments};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(right_segments.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, segment_bounds, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, segment_intersect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlLsiRow> rows;
    for (const Segment2D& probe : left_segments) {
      Vec2 dir = sub(probe.b, probe.a);
      float length = std::max(std::fabs(dir.x), std::fabs(dir.y));
      if (length < kEps) {
        continue;
      }
      LsiQueryState state {&probe, &rows};
      g_query_kind = QueryKind::kLsi;
      g_query_state = &state;
      RTCRayHit rayhit;
      set_ray(&rayhit, probe.a, dir, 1.0f);
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      rtcIntersect1(holder.scene, &rayhit, &args);
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_embree_run_pip(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
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
    rows.reserve(point_values.size() * polygon_values.size());
    for (const Point2D& point : point_values) {
      for (const Polygon2D& polygon : polygon_values) {
        rows.push_back({point.id, polygon.id, point_in_polygon(point, polygon) ? 1u : 0u});
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_embree_run_overlay(
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

extern "C" int rtdl_embree_run_ray_hitcount(
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

extern "C" int rtdl_embree_run_segment_polygon_hitcount(
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

    std::vector<RtdlSegmentPolygonHitCountRow> rows;
    rows.reserve(segment_values.size());
    for (const Segment2D& segment : segment_values) {
      uint32_t hit_count = 0;
      for (const Polygon2D& polygon : polygon_values) {
        if (segment_hits_polygon(segment, polygon)) {
          hit_count += 1;
        }
      }
      rows.push_back({segment.id, hit_count});
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

extern "C" int rtdl_embree_run_point_nearest_segment(
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

extern "C" void rtdl_embree_free_rows(void* rows) {
  std::free(rows);
}
