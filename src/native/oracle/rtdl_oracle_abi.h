#pragma once

#include <cstddef>
#include <cstdint>

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

struct RtdlSegmentPolygonAnyHitRow {
  uint32_t segment_id;
  uint32_t polygon_id;
};

struct RtdlPolygonPairOverlapAreaRow {
  uint32_t left_polygon_id;
  uint32_t right_polygon_id;
  uint32_t intersection_area;
  uint32_t left_area;
  uint32_t right_area;
  uint32_t union_area;
};

struct RtdlPolygonSetJaccardRow {
  uint32_t intersection_area;
  uint32_t left_area;
  uint32_t right_area;
  uint32_t union_area;
  double jaccard_similarity;
};

struct RtdlPolygonPairCandidate {
  uint32_t left_polygon_id;
  uint32_t right_polygon_id;
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

struct RtdlFixedRadiusSummaryRow {
  uint32_t candidate_row_count;
  uint32_t query_count_with_candidate;
  uint32_t neighbor_count_seen;
};

struct RtdlKnnNeighborRow {
  uint32_t query_id;
  uint32_t neighbor_id;
  double distance;
  uint32_t neighbor_rank;
};

struct RtdlKnnSummaryRow {
  uint32_t approximate_row_count;
  uint32_t query_count_with_candidate;
  uint32_t max_neighbor_rank;
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

struct RtdlBfsSummaryRow {
  uint32_t discovered_edge_count;
  uint32_t discovered_vertex_count;
  uint32_t max_level;
};

struct RtdlTriangleSummaryRow {
  uint32_t triangle_count;
  uint32_t touched_vertex_count;
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
  double sum;
};

int rtdl_oracle_get_version(int* major_out, int* minor_out, int* patch_out);
int rtdl_oracle_run_lsi(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_pip(
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
int rtdl_oracle_run_overlay(
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
int rtdl_oracle_run_ray_hitcount(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_segment_polygon_hitcount(
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
int rtdl_oracle_run_segment_polygon_anyhit_rows(
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
int rtdl_oracle_run_polygon_pair_overlap_area_rows(
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
    size_t error_size);
int rtdl_oracle_run_polygon_set_jaccard(
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
    size_t error_size);
int rtdl_oracle_refine_polygon_pair_overlap_area_rows_for_pairs(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    const RtdlPolygonPairCandidate* candidates,
    size_t candidate_count,
    RtdlPolygonPairOverlapAreaRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_refine_polygon_set_jaccard_for_pairs(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    const RtdlPolygonPairCandidate* candidates,
    size_t candidate_count,
    RtdlPolygonSetJaccardRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_point_nearest_segment(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_fixed_radius_neighbors(
    const RtdlPoint* query_points,
    size_t query_point_count,
    const RtdlPoint* search_points,
    size_t search_point_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* query_points,
    size_t query_point_count,
    const RtdlPoint3D* search_points,
    size_t search_point_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_summarize_fixed_radius_rows(
    const RtdlFixedRadiusNeighborRow* rows,
    size_t row_count,
    RtdlFixedRadiusSummaryRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_knn_rows(
    const RtdlPoint* query_points,
    size_t query_point_count,
    const RtdlPoint* search_points,
    size_t search_point_count,
    uint32_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_knn_rows_3d(
    const RtdlPoint3D* query_points,
    size_t query_point_count,
    const RtdlPoint3D* search_points,
    size_t search_point_count,
    uint32_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_bounded_knn_rows(
    const RtdlPoint* query_points,
    size_t query_point_count,
    const RtdlPoint* search_points,
    size_t search_point_count,
    double radius,
    uint32_t k_max,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_bounded_knn_rows_3d(
    const RtdlPoint3D* query_points,
    size_t query_point_count,
    const RtdlPoint3D* search_points,
    size_t search_point_count,
    double radius,
    uint32_t k_max,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_summarize_knn_rows(
    const RtdlKnnNeighborRow* rows,
    size_t row_count,
    RtdlKnnSummaryRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_bfs_expand(
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
int rtdl_oracle_run_triangle_probe(
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
int rtdl_oracle_summarize_bfs_rows(
    const RtdlBfsExpandRow* rows,
    size_t row_count,
    RtdlBfsSummaryRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_summarize_triangle_rows(
    const RtdlTriangleRow* rows,
    size_t row_count,
    RtdlTriangleSummaryRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_conjunctive_scan(
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
int rtdl_oracle_run_grouped_count(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
int rtdl_oracle_run_grouped_sum(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_oracle_free_rows(void* rows);

}  // extern "C"
