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

struct RtdlKnnNeighborRow {
  uint32_t query_id;
  uint32_t neighbor_id;
  double distance;
  uint32_t neighbor_rank;
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
void rtdl_oracle_free_rows(void* rows);

}  // extern "C"
