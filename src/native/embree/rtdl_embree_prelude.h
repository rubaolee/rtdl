#pragma once

#if defined(__has_include)
#  if __has_include(<embree4/rtcore.h>)
#    include <embree4/rtcore.h>
#    define RTDL_EMBREE_API_MAJOR 4
#  elif __has_include(<embree3/rtcore.h>)
#    include <embree3/rtcore.h>
#    define RTDL_EMBREE_API_MAJOR 3
#  else
#    error "RTDL Embree backend requires Embree 3 or Embree 4 headers"
#  endif
#else
#  include <embree4/rtcore.h>
#  define RTDL_EMBREE_API_MAJOR 4
#endif

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <exception>
#include <limits>
#include <mutex>
#include <new>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

#if RTDL_EMBREE_API_MAJOR < 4
using RTCIntersectArguments = RTCIntersectContext;
using RTCOccludedArguments = RTCIntersectContext;

inline void rtcInitIntersectArguments(RTCIntersectArguments* args) {
  rtcInitIntersectContext(args);
}

inline void rtcInitOccludedArguments(RTCOccludedArguments* args) {
  rtcInitIntersectContext(args);
}

inline void rtdlRtcIntersect1(RTCScene scene, RTCRayHit* rayhit, RTCIntersectArguments* args) {
  rtcIntersect1(scene, args, rayhit);
}

inline void rtdlRtcOccluded1(RTCScene scene, RTCRay* ray, RTCOccludedArguments* args) {
  rtcOccluded1(scene, args, ray);
}
#else
inline void rtdlRtcIntersect1(RTCScene scene, RTCRayHit* rayhit, RTCIntersectArguments* args) {
  rtcIntersect1(scene, rayhit, args);
}

inline void rtdlRtcOccluded1(RTCScene scene, RTCRay* ray, RTCOccludedArguments* args) {
  rtcOccluded1(scene, ray, args);
}
#endif

#if defined(__has_include)
#  if __has_include(<geos_c.h>)
#    include <geos_c.h>
#    define RTDL_EMBREE_HAS_GEOS 1
#  else
#    define RTDL_EMBREE_HAS_GEOS 0
#  endif
#else
#  define RTDL_EMBREE_HAS_GEOS 0
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

struct RtdlAggregateFrontierSource2D {
  int64_t id;
  double x;
  double y;
};

struct RtdlAggregateFrontierNode2D {
  int64_t id;
  double cx;
  double cy;
  double half_size;
  int32_t depth;
  int64_t dfs_index;
  int64_t resume_index;
  uint8_t is_leaf;
};

struct RtdlPoint3D {
  uint32_t id;
  double x;
  double y;
  double z;
};

struct RtdlPolygonRef {
  uint32_t id;
  uint32_t vertex_offset;
  uint32_t vertex_count;
};

struct RtdlPolygonPairCandidate {
  uint32_t left_polygon_id;
  uint32_t right_polygon_id;
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

#pragma pack(push, 1)
struct RtdlTriangle3D {
  uint32_t id;
  double x0;
  double y0;
  double z0;
  double x1;
  double y1;
  double z1;
  double x2;
  double y2;
  double z2;
};

struct RtdlRay2D {
  uint32_t id;
  double ox;
  double oy;
  double dx;
  double dy;
  double tmax;
};

struct RtdlRay3D {
  uint32_t id;
  double ox;
  double oy;
  double oz;
  double dx;
  double dy;
  double dz;
  double tmax;
};

struct RtdlSegment3D {
  uint32_t id;
  double x0;
  double y0;
  double z0;
  double x1;
  double y1;
  double z1;
};
#pragma pack(pop)

struct RtdlSegmentPairIntersectionRow {
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

struct RtdlShapePairRelationRow {
  uint32_t left_polygon_id;
  uint32_t right_polygon_id;
  uint32_t requires_segment_intersection;
  uint32_t requires_point_containment;
};

struct RtdlRayHitCountRow {
  uint32_t ray_id;
  uint32_t hit_count;
};

struct RtdlRayAnyHitRow {
  uint32_t ray_id;
  uint32_t any_hit;
};

struct RtdlRayClosestHitRow {
  uint32_t ray_id;
  uint32_t triangle_id;
  double t;
};

struct RtdlSegmentPolygonHitCountRow {
  uint32_t segment_id;
  uint32_t hit_count;
};

struct RtdlSegmentPolygonAnyHitRow {
  uint32_t segment_id;
  uint32_t polygon_id;
};

struct RtdlPointNearestSegmentRow {
  uint32_t point_id;
  uint32_t segment_id;
  double distance;
};

struct RtdlFixedRadiusNeighborRow {
  uint32_t query_id;
  uint32_t neighbor_id;
  double distance;
};

struct RtdlFixedRadiusCountRow {
  uint32_t query_id;
  uint32_t neighbor_count;
  uint32_t threshold_reached;
};

struct RtdlEmbreeFixedRadiusCountThreshold2D;
struct RtdlEmbreeKnnRows2D;

struct RtdlKnnNeighborRow {
  uint32_t query_id;
  uint32_t neighbor_id;
  double distance;
  uint32_t neighbor_rank;
};

struct RtdlDirectedHausdorffRow {
  uint32_t source_id;
  uint32_t target_id;
  double distance;
  uint32_t row_count;
};

struct RtdlFrontierVertex {
  uint32_t vertex_id;
  uint32_t level;
};

struct RtdlBfsExpandRow {
  uint32_t src_vertex;
  uint32_t dst_vertex;
  uint32_t level;
};

struct RtdlEdgeSeed {
  uint32_t u;
  uint32_t v;
};

struct RtdlTriangleRow {
  uint32_t u;
  uint32_t v;
  uint32_t w;
};

struct RtdlColumnField {
  const char* name;
  uint32_t kind;
};

struct RtdlColumnScalar {
  uint32_t kind;
  int64_t int_value;
  double double_value;
  const char* string_value;
};

struct RtdlPayloadField {
  const char* name;
  uint32_t kind;
  const int64_t* int_values;
  const double* double_values;
  const char* const* string_values;
};

struct RtdlColumnClause {
  const char* field;
  uint32_t op;
  RtdlColumnScalar value;
  RtdlColumnScalar value_hi;
};

struct RtdlColumnRowIdRow {
  uint32_t row_id;
};

struct RtdlGroupedCountRow {
  int64_t group_key;
  int64_t count;
};

struct RtdlGroupedSumRow {
  int64_t group_key;
  int64_t sum;
};

struct RtdlEmbreeColumnarPayload;

using RtdlDbField = RtdlColumnField;
using RtdlDbScalar = RtdlColumnScalar;
using RtdlDbClause = RtdlColumnClause;
using RtdlDbRowIdRow = RtdlColumnRowIdRow;
using RtdlDbGroupedCountRow = RtdlGroupedCountRow;
using RtdlDbGroupedSumRow = RtdlGroupedSumRow;
using RtdlEmbreeDbDataset = RtdlEmbreeColumnarPayload;

int rtdl_embree_get_version(int* major_out, int* minor_out, int* patch_out);
void rtdl_embree_configure_threads(size_t thread_count);
int rtdl_embree_run_segment_pair_intersection(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlSegmentPairIntersectionRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_point_primitive_anyhit_packet(
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
int rtdl_embree_run_shape_pair_relation_flags(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlShapePairRelationRow** rows_out,
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
int rtdl_embree_run_ray_hitcount_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_ray_anyhit(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_ray_anyhit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_ray_closest_hit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayClosestHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_static_triangle_scene_3d_create(
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    void** handle_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_static_triangle_scene_3d_grouped_segment_any_hit_flags(
    void* handle,
    const RtdlSegment3D* segments,
    size_t segment_count,
    const uint32_t* group_offsets,
    size_t group_count,
    uint8_t* flags_out,
    double* traversal_seconds_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction(
    void* handle,
    const RtdlRay3D* rays,
    size_t ray_count,
    const uint32_t* primitive_group_ids,
    size_t primitive_group_id_count,
    const uint64_t* primitive_values,
    size_t primitive_value_count,
    size_t group_count,
    uint32_t reduction,
    uint64_t* group_counts_out,
    uint64_t* group_sums_out,
    uint64_t* group_mins_out,
    uint64_t* group_maxs_out,
    uint64_t* hit_event_count_out,
    double* traversal_seconds_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_static_triangle_scene_3d_destroy(void* handle);
int rtdl_embree_run_segment_shape_hitcount(
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
int rtdl_embree_run_segment_shape_anyhit_rows(
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
int rtdl_embree_collect_k_bounded_i64(
    const int64_t* candidate_rows,
    size_t candidate_count,
    size_t row_width,
    int64_t* rows_out,
    size_t row_capacity,
    size_t* emitted_count_out,
    uint32_t* overflowed_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_collect_aggregate_frontier_2d(
    const RtdlAggregateFrontierSource2D* sources,
    size_t source_count,
    const RtdlAggregateFrontierNode2D* nodes,
    size_t node_count,
    const uint64_t* child_offsets,
    const int64_t* child_ids,
    const uint64_t* member_offsets,
    const int64_t* member_ids,
    double theta,
    uint64_t max_rows_per_source,
    uint64_t row_capacity,
    uint32_t deduplicate_fallback_targets,
    int64_t* frontier_rows_out,
    uint64_t* row_offsets_out,
    uint64_t* emitted_count_out,
    uint64_t* attempted_count_out,
    uint32_t* overflowed_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_collect_shape_pair_candidates_bounded(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlPolygonPairCandidate* candidates_out,
    size_t candidate_capacity,
    size_t* emitted_count_out,
    uint32_t* overflowed_out,
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
int rtdl_embree_run_fixed_radius_neighbors(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    size_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* query_points,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius,
    size_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_fixed_radius_count_threshold(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    size_t threshold,
    RtdlFixedRadiusCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_fixed_radius_count_threshold_2d_create(
    const RtdlPoint* search_points,
    size_t search_count,
    RtdlEmbreeFixedRadiusCountThreshold2D** handle_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_fixed_radius_count_threshold_2d_run(
    RtdlEmbreeFixedRadiusCountThreshold2D* handle,
    const RtdlPoint* query_points,
    size_t query_count,
    double radius,
    size_t threshold,
    RtdlFixedRadiusCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_fixed_radius_count_threshold_2d_destroy(
    RtdlEmbreeFixedRadiusCountThreshold2D* handle);
int rtdl_embree_k_closest_hits_2d_create(
    const RtdlPoint* search_points,
    size_t search_count,
    RtdlEmbreeKnnRows2D** handle_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_k_closest_hits_2d_run(
    RtdlEmbreeKnnRows2D* handle,
    const RtdlPoint* query_points,
    size_t query_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_k_closest_hits_2d_destroy(
    RtdlEmbreeKnnRows2D* handle);
int rtdl_embree_run_k_closest_hits(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_k_closest_hits_3d(
    const RtdlPoint3D* query_points,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_max_distance_nearest_candidate_2d(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    RtdlDirectedHausdorffRow* row_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_frontier_edge_traversal_packet(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_index_count,
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* visited,
    size_t visited_count,
    uint32_t dedupe,
    RtdlBfsExpandRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_edge_neighbor_intersection_packet(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_index_count,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    uint32_t enforce_id_ascending,
    uint32_t unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_conjunctive_scan(
    const RtdlColumnField* fields,
    size_t field_count,
    const RtdlColumnScalar* row_values,
    size_t row_count,
    const RtdlColumnClause* clauses,
    size_t clause_count,
    RtdlColumnRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_grouped_count(
    const RtdlColumnField* fields,
    size_t field_count,
    const RtdlColumnScalar* row_values,
    size_t row_count,
    const RtdlColumnClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_grouped_sum(
    const RtdlColumnField* fields,
    size_t field_count,
    const RtdlColumnScalar* row_values,
    size_t row_count,
    const RtdlColumnClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_columnar_payload_create(
    const RtdlColumnField* fields,
    size_t field_count,
    const RtdlColumnScalar* row_values,
    size_t row_count,
    const char* const* primary_fields,
    size_t primary_field_count,
    RtdlEmbreeColumnarPayload** dataset_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_columnar_payload_create_from_columns(
    const RtdlPayloadField* fields,
    size_t field_count,
    size_t row_count,
    const char* const* primary_fields,
    size_t primary_field_count,
    RtdlEmbreeColumnarPayload** dataset_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_columnar_payload_destroy(RtdlEmbreeColumnarPayload* dataset);
int rtdl_embree_columnar_payload_multi_predicate_scan(
    RtdlEmbreeColumnarPayload* dataset,
    const RtdlColumnClause* clauses,
    size_t clause_count,
    RtdlColumnRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_columnar_payload_grouped_reduction_count(
    RtdlEmbreeColumnarPayload* dataset,
    const RtdlColumnClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_columnar_payload_grouped_reduction_sum(
    RtdlEmbreeColumnarPayload* dataset,
    const RtdlColumnClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_free_rows(void* rows);


}  // extern "C"
