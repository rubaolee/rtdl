#pragma once

// rtdl_vulkan.cpp — Vulkan KHR ray-tracing backend for rtdl
//
// Implements the current Vulkan-native workload surface:
//   LSI, PIP, Overlay, RayHitCount, SegmentPolygonHitcount,
//   SegmentPolygonAnyHitRows, PointNearestSegment
// using Vulkan KHR ray-tracing extensions plus a Vulkan compute shader for
// PointNearestSegment (which does not map cleanly to ray traversal).
//
// The narrow Jaccard workloads are accepted on the public Vulkan run surface
// only through documented native CPU/oracle fallback in the Python runtime;
// they do not currently have Vulkan-native kernels or C ABI exports here.
//
// Device kernels are embedded as GLSL source strings and compiled to SPIR-V
// at runtime via shaderc.  Compiled pipelines are cached in static singletons
// so the JIT cost is paid only once per workload type per process.
//
// Build requirements:
//   - Vulkan SDK >= 1.2.162  (vulkan/vulkan.h)
//   - shaderc  (shaderc/shaderc.h, -lshaderc_combined)
//   - C++17
//
// Required Vulkan device extensions:
//   VK_KHR_acceleration_structure, VK_KHR_ray_tracing_pipeline,
//   VK_KHR_deferred_host_operations, VK_KHR_buffer_device_address,
//   VK_EXT_descriptor_indexing, VK_KHR_spirv_1_4,
//   VK_KHR_shader_float_controls
//
// Typical compile invocation (Linux):
//   g++ -std=c++17 -O3 -shared -fPIC \
//       -I$VULKAN_SDK/include \
//       rtdl_vulkan.cpp \
//       -L$VULKAN_SDK/lib -lvulkan -lshaderc_combined \
//       -o librtdl_vulkan.so

#include <vulkan/vulkan.h>
#include <shaderc/shaderc.h>

#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <mutex>
#include <new>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

#if defined(__has_include)
#  if __has_include(<geos_c.h>)
#    include <geos_c.h>
#    define RTDL_VULKAN_HAS_GEOS 1
#  else
#    define RTDL_VULKAN_HAS_GEOS 0
#  endif
#else
#  define RTDL_VULKAN_HAS_GEOS 0
#endif

// ─────────────────────────────────────────────────────────────────────────────
// Public C ABI  (identical layout to rtdl_optix.cpp — same Python binding can
// be reused by adjusting the prefix from rtdl_optix_ → rtdl_vulkan_)
// ─────────────────────────────────────────────────────────────────────────────

extern "C" {

struct RtdlSegment    { uint32_t id; double x0, y0, x1, y1; };
struct RtdlPoint      { uint32_t id; double x, y; };
struct RtdlPoint3D    { uint32_t id; double x, y, z; };
struct RtdlPolygonRef { uint32_t id, vertex_offset, vertex_count; };
struct RtdlTriangle   { uint32_t id; double x0, y0, x1, y1, x2, y2; };
#pragma pack(push, 1)
struct RtdlTriangle3D { uint32_t id; double x0, y0, z0, x1, y1, z1, x2, y2, z2; };
struct RtdlRay2D      { uint32_t id; double ox, oy, dx, dy, tmax; };
struct RtdlRay3D      { uint32_t id; double ox, oy, oz, dx, dy, dz, tmax; };
#pragma pack(pop)

struct RtdlLsiRow               { uint32_t left_id, right_id;
                                   double intersection_point_x, intersection_point_y; };
struct RtdlPipRow               { uint32_t point_id, polygon_id, contains; };
struct RtdlOverlayRow           { uint32_t left_polygon_id, right_polygon_id,
                                           requires_lsi, requires_pip; };
struct RtdlRayHitCountRow       { uint32_t ray_id, hit_count; };
struct RtdlSegmentPolygonHitCountRow { uint32_t segment_id, hit_count; };
struct RtdlSegmentPolygonAnyHitRow   { uint32_t segment_id, polygon_id; };
struct RtdlFixedRadiusNeighborRow    { uint32_t query_id, neighbor_id; double distance; };
struct RtdlKnnNeighborRow            { uint32_t query_id, neighbor_id; double distance; uint32_t neighbor_rank; };
struct RtdlPointNearestSegmentRow    { uint32_t point_id, segment_id; double distance; };
struct RtdlFrontierVertex            { uint32_t vertex_id, level; };
struct RtdlBfsExpandRow              { uint32_t src_vertex, dst_vertex, level; };
struct RtdlEdgeSeed                  { uint32_t u, v; };
struct RtdlTriangleRow               { uint32_t u, v, w; };
struct RtdlDbField                   { const char* name; uint32_t kind; };
struct RtdlDbScalar                  { uint32_t kind; int64_t int_value; double double_value; const char* string_value; };
struct RtdlDbColumn                  { const char* name; uint32_t kind; const int64_t* int_values; const double* double_values; const char* const* string_values; };
struct RtdlDbClause                  { const char* field; uint32_t op; RtdlDbScalar value; RtdlDbScalar value_hi; };
struct RtdlDbRowIdRow                { uint32_t row_id; };
struct RtdlDbGroupedCountRow         { int64_t group_key; int64_t count; };
struct RtdlDbGroupedSumRow           { int64_t group_key; int64_t sum; };
struct RtdlVulkanDbDataset;

int  rtdl_vulkan_get_version(int* major_out, int* minor_out, int* patch_out);
int  rtdl_vulkan_run_lsi(
         const RtdlSegment* left,  size_t left_count,
         const RtdlSegment* right, size_t right_count,
         RtdlLsiRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_pip(
         const RtdlPoint*     points,     size_t point_count,
         const RtdlPolygonRef* polys,     size_t poly_count,
         const double* vertices_xy,       size_t vertex_xy_count,
         uint32_t positive_only,
         RtdlPipRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_overlay(
         const RtdlPolygonRef* left_polys,  size_t left_count,
         const double* left_verts_xy,       size_t left_vert_xy_count,
         const RtdlPolygonRef* right_polys, size_t right_count,
         const double* right_verts_xy,      size_t right_vert_xy_count,
         RtdlOverlayRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_ray_hitcount(
         const RtdlRay2D*    rays,      size_t ray_count,
         const RtdlTriangle* triangles, size_t triangle_count,
         RtdlRayHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_ray_hitcount_3d(
         const RtdlRay3D*    rays,      size_t ray_count,
         const RtdlTriangle3D* triangles, size_t triangle_count,
         RtdlRayHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_segment_polygon_hitcount(
         const RtdlSegment*    segments,  size_t segment_count,
         const RtdlPolygonRef* polygons,  size_t polygon_count,
         const double* vertices_xy,       size_t vertex_xy_count,
         RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_segment_polygon_anyhit_rows(
         const RtdlSegment*    segments,  size_t segment_count,
         const RtdlPolygonRef* polygons,  size_t polygon_count,
         const double* vertices_xy,       size_t vertex_xy_count,
         RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_point_nearest_segment(
         const RtdlPoint*   points,   size_t point_count,
         const RtdlSegment* segments, size_t segment_count,
         RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_fixed_radius_neighbors(
         const RtdlPoint* query_points, size_t query_count,
         const RtdlPoint* search_points, size_t search_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_fixed_radius_neighbors_3d(
         const RtdlPoint3D* query_points, size_t query_count,
         const RtdlPoint3D* search_points, size_t search_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_knn_rows(
         const RtdlPoint* query_points, size_t query_count,
         const RtdlPoint* search_points, size_t search_count,
         size_t k,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_knn_rows_3d(
         const RtdlPoint3D* query_points, size_t query_count,
         const RtdlPoint3D* search_points, size_t search_count,
         size_t k,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_bfs_expand(
         const uint32_t* row_offsets, size_t row_offset_count,
         const uint32_t* column_indices, size_t column_index_count,
         const RtdlFrontierVertex* frontier, size_t frontier_count,
         const uint32_t* visited_vertices, size_t visited_count,
         uint32_t dedupe,
         RtdlBfsExpandRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_triangle_probe(
         const uint32_t* row_offsets, size_t row_offset_count,
         const uint32_t* column_indices, size_t column_index_count,
         const RtdlEdgeSeed* seeds, size_t seed_count,
         uint32_t enforce_id_ascending,
         uint32_t unique,
         RtdlTriangleRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_conjunctive_scan(
         const RtdlDbField* fields, size_t field_count,
         const RtdlDbScalar* row_values, size_t row_count,
         const RtdlDbClause* clauses, size_t clause_count,
         RtdlDbRowIdRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_grouped_count(
         const RtdlDbField* fields, size_t field_count,
         const RtdlDbScalar* row_values, size_t row_count,
         const RtdlDbClause* clauses, size_t clause_count,
         const char* group_key_field,
         RtdlDbGroupedCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_run_grouped_sum(
         const RtdlDbField* fields, size_t field_count,
         const RtdlDbScalar* row_values, size_t row_count,
         const RtdlDbClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         RtdlDbGroupedSumRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_db_dataset_create(
         const RtdlDbField* fields, size_t field_count,
         const RtdlDbScalar* row_values, size_t row_count,
         const char* const* primary_fields, size_t primary_field_count,
         RtdlVulkanDbDataset** dataset_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_db_dataset_create_columnar(
         const RtdlDbColumn* columns, size_t column_count,
         size_t row_count,
         const char* const* primary_fields, size_t primary_field_count,
         RtdlVulkanDbDataset** dataset_out,
         char* error_out, size_t error_size);
void rtdl_vulkan_db_dataset_destroy(RtdlVulkanDbDataset* dataset);
int  rtdl_vulkan_db_dataset_conjunctive_scan(
         RtdlVulkanDbDataset* dataset,
         const RtdlDbClause* clauses, size_t clause_count,
         RtdlDbRowIdRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_db_dataset_grouped_count(
         RtdlVulkanDbDataset* dataset,
         const RtdlDbClause* clauses, size_t clause_count,
         const char* group_key_field,
         RtdlDbGroupedCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_vulkan_db_dataset_grouped_sum(
         RtdlVulkanDbDataset* dataset,
         const RtdlDbClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         RtdlDbGroupedSumRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
void rtdl_vulkan_free_rows(void* rows);

} // extern "C"

// ─────────────────────────────────────────────────────────────────────────────
// Internal implementation
// ─────────────────────────────────────────────────────────────────────────────
