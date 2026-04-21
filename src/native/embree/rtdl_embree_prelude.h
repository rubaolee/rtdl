#pragma once

#include <embree4/rtcore.h>

#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <exception>
#include <limits>
#include <new>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

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
#pragma pack(pop)

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

struct RtdlDbField {
  const char* name;
  uint32_t kind;
};

struct RtdlDbScalar {
  uint32_t kind;
  int64_t int_value;
  double double_value;
  const char* string_value;
};

struct RtdlDbColumn {
  const char* name;
  uint32_t kind;
  const int64_t* int_values;
  const double* double_values;
  const char* const* string_values;
};

struct RtdlDbClause {
  const char* field;
  uint32_t op;
  RtdlDbScalar value;
  RtdlDbScalar value_hi;
};

struct RtdlDbRowIdRow {
  uint32_t row_id;
};

struct RtdlDbGroupedCountRow {
  int64_t group_key;
  int64_t count;
};

struct RtdlDbGroupedSumRow {
  int64_t group_key;
  int64_t sum;
};

struct RtdlEmbreeDbDataset;

int rtdl_embree_get_version(int* major_out, int* minor_out, int* patch_out);
void rtdl_embree_configure_threads(size_t thread_count);
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
    uint32_t positive_only,
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
int rtdl_embree_run_segment_polygon_anyhit_rows(
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
int rtdl_embree_knn_rows_2d_create(
    const RtdlPoint* search_points,
    size_t search_count,
    RtdlEmbreeKnnRows2D** handle_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_knn_rows_2d_run(
    RtdlEmbreeKnnRows2D* handle,
    const RtdlPoint* query_points,
    size_t query_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_knn_rows_2d_destroy(
    RtdlEmbreeKnnRows2D* handle);
int rtdl_embree_run_knn_rows(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_knn_rows_3d(
    const RtdlPoint3D* query_points,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_directed_hausdorff_2d(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    RtdlDirectedHausdorffRow* row_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_bfs_expand(
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
    size_t error_size);
int rtdl_embree_run_triangle_probe(
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
    size_t error_size);
int rtdl_embree_run_conjunctive_scan(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_grouped_count(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_run_grouped_sum(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_db_dataset_create(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const char* const* primary_fields,
    size_t primary_field_count,
    RtdlEmbreeDbDataset** dataset_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_db_dataset_create_columnar(
    const RtdlDbColumn* columns,
    size_t column_count,
    size_t row_count,
    const char* const* primary_fields,
    size_t primary_field_count,
    RtdlEmbreeDbDataset** dataset_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_db_dataset_destroy(RtdlEmbreeDbDataset* dataset);
int rtdl_embree_db_dataset_conjunctive_scan(
    RtdlEmbreeDbDataset* dataset,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_db_dataset_grouped_count(
    RtdlEmbreeDbDataset* dataset,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_embree_db_dataset_grouped_sum(
    RtdlEmbreeDbDataset* dataset,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_free_rows(void* rows);


}  // extern "C"
