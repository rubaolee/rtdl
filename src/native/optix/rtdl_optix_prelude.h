#pragma once

// rtdl_optix.cpp - NVIDIA OptiX 7 backend for rtdl
//
// Implements all current OptiX-native workloads (segment-pair intersection, PIP, shape-pair relation,
// RayHitCount, SegmentPolygonHitcount, PointNearestSegment,
// FixedRadiusNeighbors) through the OptiX backend.
// The mature RT-traversal workloads use OptiX 7 custom-geometry BVH traversal.
// Some families still follow a bounded local maturity story:
// - SegmentPolygonHitcount now defaults to a host-indexed candidate-reduction
//   path; the older OptiX custom-AABB traversal path remains available as an
//   explicit experimental mode
// - PointNearestSegment uses CUDA-parallel brute-force
// - FixedRadiusNeighbors currently uses CUDA-parallel brute-force
//
// Device kernels are embedded as CUDA source strings and compiled to PTX at
// runtime via NVRTC.  Compiled pipelines are cached across calls in static
// singletons so the JIT cost is paid only once per workload type per process.
//
// Build requirements:
//   - CUDA Toolkit >= 11.0 11.0  (nvrtc.h, cuda.h, cuda_runtime.h)
//   - OptiX SDK 7.x  (optix.h)
//   - C++17
//
// Typical compile invocation:
//   nvcc -std=c++17 -O3 -shared -fPIC \
//        -I/path/to/optix/include \
//        -I/path/to/cuda/include \
//        -DRTDL_OPTIX_INCLUDE_DIR='"/path/to/optix/include"' \
//        -DRTDL_CUDA_INCLUDE_DIR='"/path/to/cuda/include"' \
//        -lcuda -lnvrtc \
//        rtdl_optix.cpp -o librtdl_optix.so

#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stack_size.h>
#include <optix_stubs.h>

#include <cuda.h>
#include <cuda_runtime.h>
#include <nvrtc.h>

#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <filesystem>
#include <limits>
#include <memory>
#include <mutex>
#include <new>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

void rtdl_cuda_pack_ray3d_device_columns_precompiled(
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_oz,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_dz,
        const double* ray_tmax,
        void* rays_out,
        uint32_t ray_count);

#if defined(__has_include)
#  if __has_include(<geos_c.h>)
#    include <geos_c.h>
#    define RTDL_OPTIX_HAS_GEOS 1
#  else
#    define RTDL_OPTIX_HAS_GEOS 0
#  endif
#else
#  define RTDL_OPTIX_HAS_GEOS 0
#endif

// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
// Public C ABI (mirrors rtdl_embree.cpp)
// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

extern "C" {

struct RtdlSegment {
    uint32_t id;
    double x0, y0, x1, y1;
};

struct RtdlPoint {
    uint32_t id;
    double x, y;
};

struct RtdlAabb2D {
    uint32_t id;
    double min_x, min_y, max_x, max_y;
};

struct RtdlAabbPairRow {
    uint32_t query_id;
    uint32_t indexed_id;
};
static_assert(offsetof(RtdlAabbPairRow, query_id) == 0, "RtdlAabbPairRow query offset mismatch");
static_assert(offsetof(RtdlAabbPairRow, indexed_id) == 4, "RtdlAabbPairRow indexed offset mismatch");
static_assert(sizeof(RtdlAabbPairRow) == 8, "RtdlAabbPairRow size mismatch");

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
    double x, y, z;
};

struct RtdlPolygonRef {
    uint32_t id;
    uint32_t vertex_offset;
    uint32_t vertex_count;
};

struct RtdlClosedShapeRef {
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
    double x0, y0, x1, y1, x2, y2;
};

#pragma pack(push, 1)
struct RtdlTriangle3D {
    uint32_t id;
    double x0, y0, z0, x1, y1, z1, x2, y2, z2;
};

struct RtdlRay2D {
    uint32_t id;
    double ox, oy, dx, dy, tmax;
};

struct RtdlRay3D {
    uint32_t id;
    double ox, oy, oz, dx, dy, dz, tmax;
};

struct RtdlSegment3D {
    uint32_t id;
    double x0, y0, z0, x1, y1, z1;
};
#pragma pack(pop)

struct RtdlSegmentPairIntersectionRow {
    uint32_t left_id, right_id;
    double intersection_point_x, intersection_point_y;
};

struct RtdlSegmentFirstHitRow {
    uint32_t probe_id, primitive_id;
    double hit_x, hit_y, hit_t;
};

struct RtdlPipRow {
    uint32_t point_id, polygon_id, contains;
};

struct RtdlPointClosedShapeMembershipRow {
    uint32_t point_id, shape_id, membership;
};

struct RtdlShapePairRelationRow {
    uint32_t left_polygon_id, right_polygon_id;
    uint32_t requires_segment_intersection, requires_point_containment;
};

struct RtdlRayHitCountRow {
    uint32_t ray_id, hit_count;
};

struct RtdlRayAnyHitRow {
    uint32_t ray_id, any_hit;
};

struct RtdlRayClosestHitRow {
    uint32_t ray_id, triangle_id;
    double t;
};

struct RtdlRayTriangleHitStreamRow {
    uint32_t ray_id, primitive_id;
};

struct RtdlRaySegmentGroupCountRow {
    uint32_t ray_id, group_id, hit_count, parity;
};

struct RtdlSegmentPolygonHitCountRow {
    uint32_t segment_id, hit_count;
};

struct RtdlSegmentPolygonAnyHitRow {
    uint32_t segment_id, polygon_id;
};

struct RtdlFixedRadiusNeighborRow {
    uint32_t query_id, neighbor_id;
    double distance;
};
static_assert(offsetof(RtdlFixedRadiusNeighborRow, query_id) == 0, "RtdlFixedRadiusNeighborRow query offset mismatch");
static_assert(offsetof(RtdlFixedRadiusNeighborRow, neighbor_id) == 4, "RtdlFixedRadiusNeighborRow neighbor offset mismatch");
static_assert(offsetof(RtdlFixedRadiusNeighborRow, distance) == 8, "RtdlFixedRadiusNeighborRow distance offset mismatch");
static_assert(sizeof(RtdlFixedRadiusNeighborRow) == 16, "RtdlFixedRadiusNeighborRow size mismatch");

struct RtdlFixedRadiusNeighborSummary {
    size_t count;
    double min_distance;
    double max_distance;
    double sum_distance;
};
static_assert(sizeof(size_t) == 8, "RtdlFixedRadiusNeighborSummary requires the 64-bit native OptiX ABI");
static_assert(offsetof(RtdlFixedRadiusNeighborSummary, count) == 0, "RtdlFixedRadiusNeighborSummary count offset mismatch");
static_assert(offsetof(RtdlFixedRadiusNeighborSummary, min_distance) == 8, "RtdlFixedRadiusNeighborSummary min offset mismatch");
static_assert(offsetof(RtdlFixedRadiusNeighborSummary, max_distance) == 16, "RtdlFixedRadiusNeighborSummary max offset mismatch");
static_assert(offsetof(RtdlFixedRadiusNeighborSummary, sum_distance) == 24, "RtdlFixedRadiusNeighborSummary sum offset mismatch");
static_assert(sizeof(RtdlFixedRadiusNeighborSummary) == 32, "RtdlFixedRadiusNeighborSummary size mismatch");

struct RtdlFixedRadiusCountRow {
    uint32_t query_id;
    uint32_t neighbor_count;
    uint32_t threshold_reached;
};

struct RtdlPointGroupBounds2D {
    uint32_t id;
    uint32_t point_offset;
    uint32_t point_count;
    double min_x, min_y, max_x, max_y;
};

struct RtdlKnnNeighborRow {
    uint32_t query_id, neighbor_id;
    double distance;
    uint32_t neighbor_rank;
};
static_assert(offsetof(RtdlKnnNeighborRow, query_id) == 0, "RtdlKnnNeighborRow query offset mismatch");
static_assert(offsetof(RtdlKnnNeighborRow, neighbor_id) == 4, "RtdlKnnNeighborRow neighbor offset mismatch");
static_assert(offsetof(RtdlKnnNeighborRow, distance) == 8, "RtdlKnnNeighborRow distance offset mismatch");
static_assert(offsetof(RtdlKnnNeighborRow, neighbor_rank) == 16, "RtdlKnnNeighborRow rank offset mismatch");
static_assert(sizeof(RtdlKnnNeighborRow) == 24, "RtdlKnnNeighborRow size mismatch");

struct RtdlFixedRadiusRankedNeighborSummary {
    uint32_t query_id;
    uint32_t neighbor_count;
    uint32_t nearest_neighbor_id;
    uint32_t kth_neighbor_id;
    double nearest_distance;
    double kth_distance;
    double sum_distance;
};
static_assert(offsetof(RtdlFixedRadiusRankedNeighborSummary, query_id) == 0, "RtdlFixedRadiusRankedNeighborSummary query offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborSummary, neighbor_count) == 4, "RtdlFixedRadiusRankedNeighborSummary count offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborSummary, nearest_neighbor_id) == 8, "RtdlFixedRadiusRankedNeighborSummary nearest id offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborSummary, kth_neighbor_id) == 12, "RtdlFixedRadiusRankedNeighborSummary kth id offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborSummary, nearest_distance) == 16, "RtdlFixedRadiusRankedNeighborSummary nearest distance offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborSummary, kth_distance) == 24, "RtdlFixedRadiusRankedNeighborSummary kth distance offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborSummary, sum_distance) == 32, "RtdlFixedRadiusRankedNeighborSummary sum offset mismatch");
static_assert(sizeof(RtdlFixedRadiusRankedNeighborSummary) == 40, "RtdlFixedRadiusRankedNeighborSummary size mismatch");

struct RtdlPointNearestSegmentRow {
    uint32_t point_id, segment_id;
    double distance;
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

constexpr uint32_t kRtdlColumnKindInt64 = 1u;
constexpr uint32_t kRtdlColumnKindFloat64 = 2u;
constexpr uint32_t kRtdlColumnKindBool = 3u;
constexpr uint32_t kRtdlColumnKindText = 4u;

constexpr uint32_t kRtdlDbKindInt64 = kRtdlColumnKindInt64;
constexpr uint32_t kRtdlDbKindFloat64 = kRtdlColumnKindFloat64;
constexpr uint32_t kRtdlDbKindBool = kRtdlColumnKindBool;
constexpr uint32_t kRtdlDbKindText = kRtdlColumnKindText;

struct RtdlPayloadField {
    const char* name;
    uint32_t kind;
    const int64_t* int_values;
    const double* double_values;
    const char* const* string_values;
};

constexpr uint32_t kRtdlDevicePayloadDeviceCuda = 1u;
constexpr uint32_t kRtdlDevicePayloadDtypeInt64 = 1u;
constexpr uint32_t kRtdlDevicePayloadDtypeUint32 = 2u;
constexpr uint32_t kRtdlDevicePayloadDtypeFloat64 = 3u;

struct RtdlDevicePayloadField {
    const char* name;
    uint32_t kind;
    uint32_t dtype;
    uint32_t device_type;
    uint32_t device_id;
    size_t element_count;
    size_t stride_bytes;
    uint64_t device_ptr;
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

struct RtdlGroupedSumCountRow {
    int64_t group_key;
    int64_t sum;
    int64_t count;
};

struct RtdlGroupedStatsRow {
    int64_t group_key;
    int64_t count;
    int64_t sum;
    int64_t min;
    int64_t max;
};

constexpr uint32_t kRtdlColumnCompactSummaryScanCount = 1u;
constexpr uint32_t kRtdlColumnCompactSummaryGroupedCount = 2u;
constexpr uint32_t kRtdlColumnCompactSummaryGroupedSum = 3u;

constexpr uint32_t kRtdlDbCompactSummaryScanCount = kRtdlColumnCompactSummaryScanCount;
constexpr uint32_t kRtdlDbCompactSummaryGroupedCount = kRtdlColumnCompactSummaryGroupedCount;
constexpr uint32_t kRtdlDbCompactSummaryGroupedSum = kRtdlColumnCompactSummaryGroupedSum;

struct RtdlColumnCompactSummaryRequest {
    uint32_t operation;
    const RtdlColumnClause* clauses;
    size_t clause_count;
    const char* group_key_field;
    const char* value_field;
};

struct RtdlColumnCompactSummaryResult {
    uint32_t operation;
    size_t scalar_value;
    RtdlGroupedCountRow* count_rows;
    size_t count_row_count;
    RtdlGroupedSumRow* sum_rows;
    size_t sum_row_count;
    double traversal;
    double bitset_copyback;
    double exact_filter;
    double output_pack;
    size_t raw_candidate_count;
    size_t emitted_count;
};

struct RtdlOptixColumnarPayload;

using RtdlDbField = RtdlColumnField;
using RtdlDbScalar = RtdlColumnScalar;
using RtdlDbClause = RtdlColumnClause;
using RtdlDbRowIdRow = RtdlColumnRowIdRow;
using RtdlDbGroupedCountRow = RtdlGroupedCountRow;
using RtdlDbGroupedSumRow = RtdlGroupedSumRow;
using RtdlDbGroupedSumCountRow = RtdlGroupedSumCountRow;
using RtdlDbGroupedStatsRow = RtdlGroupedStatsRow;
using RtdlDbCompactSummaryRequest = RtdlColumnCompactSummaryRequest;
using RtdlDbCompactSummaryResult = RtdlColumnCompactSummaryResult;
using RtdlOptixDbDataset = RtdlOptixColumnarPayload;

int  rtdl_optix_get_version(int* major_out, int* minor_out, int* patch_out);
int  rtdl_optix_run_segment_pair_intersection(
         const RtdlSegment* left,  size_t left_count,
         const RtdlSegment* right, size_t right_count,
         RtdlSegmentPairIntersectionRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_segment_pair_intersection(
         const RtdlSegment* right, size_t right_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_segment_pair_intersection(
         void* prepared,
         const RtdlSegment* left, size_t left_count,
         RtdlSegmentPairIntersectionRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_segment_pair_intersection(
         void* prepared,
         const RtdlSegment* left, size_t left_count,
         size_t* count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_segment_first_hit(
         void* prepared,
         const RtdlSegment* probes, size_t probe_count,
         RtdlSegmentFirstHitRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_segment_first_hit(
         void* prepared,
         const RtdlSegment* probes, size_t probe_count,
         size_t* count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_segment_pair_intersection(void* prepared);
int  rtdl_optix_run_point_primitive_anyhit_packet(
         const RtdlPoint* points,     size_t point_count,
         const RtdlPolygonRef* polys, size_t poly_count,
         const double* vertices_xy,   size_t vertex_xy_count,
         uint32_t positive_only,
         RtdlPipRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_point_closed_shape_membership_2d(
         const RtdlPoint* points,          size_t point_count,
         const RtdlClosedShapeRef* shapes, size_t shape_count,
         const double* vertices_xy,        size_t vertex_xy_count,
         uint32_t positive_only,
         RtdlPointClosedShapeMembershipRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_point_closed_shape_membership_2d(
         const RtdlClosedShapeRef* shapes, size_t shape_count,
         const double* vertices_xy,        size_t vertex_xy_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_point_closed_shape_membership_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         uint32_t positive_only,
         RtdlPointClosedShapeMembershipRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_point_closed_shape_membership_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t* count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_closed_shape_membership_get_last_phase_timings(
         double* point_pack,
         double* point_upload,
         double* candidate_count,
         double* candidate_write,
         double* candidate_download,
         double* exact_refine,
         size_t* raw_candidate_count,
         size_t* emitted_count,
         uint32_t* mode);
void rtdl_optix_destroy_prepared_point_closed_shape_membership_2d(void* prepared);
int  rtdl_optix_run_shape_pair_relation_flags(
         const RtdlPolygonRef* left_polys,  size_t left_count,
         const double* left_verts_xy,       size_t left_vert_xy_count,
         const RtdlPolygonRef* right_polys, size_t right_count,
         const double* right_verts_xy,      size_t right_vert_xy_count,
         RtdlShapePairRelationRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_shape_pair_relation_flags(
         const RtdlPolygonRef* right_polys, size_t right_count,
         const double* right_verts_xy,      size_t right_vert_xy_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_shape_pair_relation_flags(
         void* prepared,
         const RtdlPolygonRef* left_polys, size_t left_count,
         const double* left_verts_xy,      size_t left_vert_xy_count,
         RtdlShapePairRelationRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_shape_pair_relation_flags(void* prepared);
int  rtdl_optix_run_ray_hitcount(
         const RtdlRay2D*    rays,      size_t ray_count,
         const RtdlTriangle* triangles, size_t triangle_count,
         RtdlRayHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_ray_hitcount_3d(
         const RtdlRay3D*    rays,      size_t ray_count,
         const RtdlTriangle3D* triangles, size_t triangle_count,
         RtdlRayHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_ray_anyhit(
         const RtdlRay2D*    rays,      size_t ray_count,
         const RtdlTriangle* triangles, size_t triangle_count,
         RtdlRayAnyHitRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_ray_anyhit_3d(
         const RtdlRay3D*    rays,      size_t ray_count,
         const RtdlTriangle3D* triangles, size_t triangle_count,
         RtdlRayAnyHitRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_ray_closest_hit_3d(
         const RtdlRay3D*    rays,      size_t ray_count,
         const RtdlTriangle3D* triangles, size_t triangle_count,
         RtdlRayClosestHitRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_create(
         const RtdlTriangle3D* triangles, size_t triangle_count,
         void** handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_create_device_triangles(
         const uint32_t* triangle_ids,
         const double* triangle_x0,
         const double* triangle_y0,
         const double* triangle_z0,
         const double* triangle_x1,
         const double* triangle_y1,
         const double* triangle_z1,
         const double* triangle_x2,
         const double* triangle_y2,
         const double* triangle_z2,
         size_t triangle_count,
         void** handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags(
         void* handle,
         const RtdlSegment3D* segments, size_t segment_count,
         const uint32_t* group_offsets, size_t group_count,
         uint8_t* flags_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_grouped_segment_query_create(
         const RtdlSegment3D* segments, size_t segment_count,
         const uint32_t* group_offsets, size_t group_count,
         void** query_handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_flags(
         void* scene_handle,
         void* query_handle,
         uint8_t* flags_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_count(
         void* scene_handle,
         void* query_handle,
         uint32_t* flagged_group_count_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         const uint64_t* ray_weights,
         uint64_t* weighted_hit_sum_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum_device_rays(
         void* scene_handle,
         const uint32_t* ray_ids,
         const double* ray_ox,
         const double* ray_oy,
         const double* ray_oz,
         const double* ray_dx,
         const double* ray_dy,
         const double* ray_dz,
         const double* ray_tmax,
         size_t ray_count,
         const uint64_t* ray_weights,
         uint64_t* weighted_hit_sum_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         const uint32_t* primitive_group_ids, size_t primitive_group_id_count,
         const uint64_t* primitive_values, size_t primitive_value_count,
         size_t group_count,
         uint32_t reduction,
         uint64_t* group_counts_out,
         uint64_t* group_sums_out,
         uint64_t* group_mins_out,
         uint64_t* group_maxs_out,
         uint64_t* hit_event_count_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         uint32_t deduplicate_primitives,
         RtdlRayTriangleHitStreamRow* rows_out,
         size_t max_rows,
         size_t* row_count_out,
         uint64_t* hit_event_count_out,
         uint32_t* overflow_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_primitive_grouped_i64_payload_3d_create(
         const uint32_t* primitive_group_ids, size_t primitive_group_id_count,
         const uint64_t* primitive_values, size_t primitive_value_count,
         size_t group_count,
         void** payload_handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction(
         void* scene_handle,
         void* payload_handle,
         const RtdlRay3D* rays, size_t ray_count,
         uint32_t reduction,
         uint64_t* group_counts_out,
         uint64_t* group_sums_out,
         uint64_t* group_mins_out,
         uint64_t* group_maxs_out,
         uint64_t* hit_event_count_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction(
         void* scene_handle,
         void* payload_handle,
         void* ray_batch_handle,
         uint32_t reduction,
         uint64_t* group_counts_out,
         uint64_t* group_sums_out,
         uint64_t* group_mins_out,
         uint64_t* group_maxs_out,
         uint64_t* hit_event_count_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         uint64_t* hit_count_sum_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         RtdlRayClosestHitRow** rows_out, size_t* row_count_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_ray_batch_3d_create(
         const RtdlRay3D* rays, size_t ray_count,
         void** ray_batch_handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_ray_batch_3d_create_device_rays(
         const uint32_t* ray_ids,
         const double* ray_ox,
         const double* ray_oy,
         const double* ray_oz,
         const double* ray_dx,
         const double* ray_dy,
         const double* ray_dz,
         const double* ray_tmax,
         size_t ray_count,
         void** ray_batch_handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create(
         const uint32_t* ray_group_ids, size_t ray_group_id_count,
         const double* candidate_values, const uint32_t* candidate_indices,
         size_t candidate_count, size_t group_count,
         void** grouped_inputs_handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_grouped_candidate_argmin_inputs_create(
         const uint32_t* candidate_group_ids,
         const double* candidate_values,
         const uint32_t* candidate_indices,
         size_t candidate_count, size_t group_count,
         void** grouped_inputs_handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_grouped_candidate_argmin_finalize(
         void* grouped_inputs_handle,
         uint8_t* group_has_value_out,
         uint32_t* group_index_out,
         double* group_value_out,
         double* finalize_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_rows(
         void* scene_handle,
         void* ray_batch_handle,
         RtdlRayClosestHitRow** rows_out, size_t* row_count_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_closest_hit_grouped_argmin(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         const uint32_t* ray_group_ids, size_t ray_group_id_count,
         const double* candidate_values, const uint32_t* candidate_indices,
         size_t candidate_count, size_t group_count,
         uint8_t* group_has_value_out,
         uint32_t* group_index_out,
         double* group_value_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin(
         void* scene_handle,
         void* ray_batch_handle,
         const uint32_t* ray_group_ids, size_t ray_group_id_count,
         const double* candidate_values, const uint32_t* candidate_indices,
         size_t candidate_count, size_t group_count,
         uint8_t* group_has_value_out,
         uint32_t* group_index_out,
         double* group_value_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin(
         void* scene_handle,
         void* ray_batch_handle,
         void* grouped_inputs_handle,
         uint8_t* group_has_value_out,
         uint32_t* group_index_out,
         double* group_value_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin(
         void* scene_a_handle,
         void* ray_batch_a_handle,
         void* grouped_inputs_a_handle,
         void* scene_b_handle,
         void* ray_batch_b_handle,
         void* grouped_inputs_b_handle,
         uint8_t* group_has_value_out,
         uint32_t* group_index_out,
         double* group_value_out,
         double* traversal_a_seconds_out,
         double* traversal_b_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum_device_rays(
         void* scene_handle,
         const uint32_t* ray_ids,
         const double* ray_ox,
         const double* ray_oy,
         const double* ray_oz,
         const double* ray_dx,
         const double* ray_dy,
         const double* ray_dz,
         const double* ray_tmax,
         size_t ray_count,
         uint64_t* hit_count_sum_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
void rtdl_optix_static_triangle_scene_3d_grouped_segment_query_destroy(
         void* query_handle);
void rtdl_optix_primitive_grouped_i64_payload_3d_destroy(
         void* payload_handle);
void rtdl_optix_ray_batch_3d_destroy(void* ray_batch_handle);
void rtdl_optix_closest_hit_grouped_argmin_inputs_3d_destroy(void* grouped_inputs_handle);
void rtdl_optix_grouped_candidate_argmin_inputs_destroy(void* grouped_inputs_handle);
void rtdl_optix_static_triangle_scene_3d_destroy(void* handle);
int  rtdl_optix_run_ray_segment_group_count_2d(
         const RtdlRay2D* rays, size_t ray_count,
         const RtdlSegment* segments, size_t segment_count,
         const uint32_t* segment_group_ids,
         RtdlRaySegmentGroupCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_ray_segment_group_count_2d(
         const RtdlSegment* segments, size_t segment_count,
         const uint32_t* segment_group_ids,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_ray_segment_group_count_2d(
         void* prepared,
         const RtdlRay2D* rays, size_t ray_count,
         RtdlRaySegmentGroupCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d(
         void* prepared,
         const RtdlRay2D* rays, size_t ray_count,
         RtdlRaySegmentGroupCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_ray_segment_group_count_2d(void* prepared);
int  rtdl_optix_prepare_ray_anyhit_2d(
         const RtdlTriangle* triangles, size_t triangle_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_ray_anyhit_2d_device_triangles(
         const uint32_t* triangle_ids,
         const double* triangle_x0,
         const double* triangle_y0,
         const double* triangle_x1,
         const double* triangle_y1,
         const double* triangle_x2,
         const double* triangle_y2,
         size_t triangle_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs(
         const uint32_t* triangle_ids,
         const double* triangle_x0,
         const double* triangle_y0,
         const double* triangle_x1,
         const double* triangle_y1,
         const double* triangle_x2,
         const double* triangle_y2,
         const void* triangle_aabbs,
         size_t triangle_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_ray_anyhit_2d(
         void* prepared,
         const RtdlRay2D* rays, size_t ray_count,
         size_t* hit_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_ray_anyhit_2d(void* prepared);
int  rtdl_optix_prepare_aabb_index_2d(
         const RtdlAabb2D* boxes, size_t box_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_aabb_index_2d(
         void* prepared,
         const RtdlPoint* point_queries, size_t point_query_count,
         const RtdlAabb2D* box_queries, size_t box_query_count,
         uint32_t operation,
         size_t* hit_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_aabb_point_queries_2d(
         const RtdlPoint* point_queries, size_t point_query_count,
         void** queries_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_aabb_box_queries_2d(
         const RtdlAabb2D* box_queries, size_t box_query_count,
         void** queries_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_aabb_index_2d_packed_queries(
         void* prepared,
         void* prepared_queries,
         uint32_t operation,
         size_t* hit_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows(
         void* prepared,
         const RtdlAabb2D* box_queries, size_t box_query_count,
         RtdlAabbPairRow* rows_out, size_t row_capacity,
         size_t* emitted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows(
         void* prepared,
         const RtdlPoint* point_queries, size_t point_query_count,
         RtdlAabbPairRow* rows_out, size_t row_capacity,
         size_t* emitted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_aabb_queries_2d(void* prepared_queries);
void rtdl_optix_destroy_prepared_aabb_index_2d(void* prepared);
int  rtdl_optix_prepare_rays_2d(
         const RtdlRay2D* rays, size_t ray_count,
         void** rays_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_ray_anyhit_2d_packed(
         void* prepared,
         void* prepared_rays,
         size_t* hit_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_ray_anyhit_2d_device_rays(
         void* prepared,
         const uint32_t* ray_ids,
         const double* ray_ox,
         const double* ray_oy,
         const double* ray_dx,
         const double* ray_dy,
         const double* ray_tmax,
         size_t ray_count,
         size_t* hit_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_ray_anyhit_2d_device_flags(
         void* prepared,
         const uint32_t* ray_ids,
         const double* ray_ox,
         const double* ray_oy,
         const double* ray_dx,
         const double* ray_dy,
         const double* ray_tmax,
         size_t ray_count,
         uint32_t* any_hit_flags_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses(
         void* prepared,
         const uint32_t* ray_ids,
         const double* ray_ox,
         const double* ray_oy,
         const double* ray_dx,
         const double* ray_dy,
         const double* ray_tmax,
         size_t ray_count,
         uint32_t* witness_ray_ids_out,
         uint32_t* witness_primitive_ids_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_ray_anyhit_2d_device_all_witnesses(
         void* prepared,
         const uint32_t* ray_ids,
         const double* ray_ox,
         const double* ray_oy,
         const double* ray_dx,
         const double* ray_dy,
         const double* ray_tmax,
         size_t ray_count,
         uint32_t* witness_ray_ids_out,
         uint32_t* witness_primitive_ids_out,
         size_t witness_capacity,
         size_t* emitted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed(
         void* prepared,
         void* prepared_rays,
         const uint32_t* group_indices,
         size_t group_index_count,
         uint32_t* group_flags_out,
         size_t group_count,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_group_indices_2d(
         const uint32_t* group_indices,
         size_t group_index_count,
         void** group_indices_out,
         char* error_out, size_t error_size);
int  rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices(
         void* prepared,
         void* prepared_rays,
         void* prepared_group_indices,
         uint32_t* group_flags_out,
         size_t group_count,
         char* error_out, size_t error_size);
int  rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices(
         void* prepared,
         void* prepared_rays,
         void* prepared_group_indices,
         size_t group_count,
         size_t* colliding_group_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_group_indices_2d(void* prepared_group_indices);
void rtdl_optix_destroy_prepared_rays_2d(void* prepared_rays);
int  rtdl_optix_run_segment_shape_hitcount(
         const RtdlSegment*   segments,  size_t segment_count,
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_segment_shape_hitcount_2d(
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_segment_shape_hitcount_2d(
         void* prepared,
         const RtdlSegment* segments, size_t segment_count,
         RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_segment_shape_hitcount_at_least_2d(
         void* prepared,
         const RtdlSegment* segments, size_t segment_count,
         uint32_t threshold,
         size_t* count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_aggregate_prepared_segment_shape_hitcount_2d(
         void* prepared,
         const RtdlSegment* segments, size_t segment_count,
         uint32_t positive_threshold,
         size_t* row_count_out,
         uint64_t* hit_sum_out,
         size_t* positive_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_segment_shape_hitcount_2d(void* prepared);
int  rtdl_optix_run_segment_shape_anyhit_rows(
         const RtdlSegment*   segments,  size_t segment_count,
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_segment_shape_anyhit_rows_native_bounded(
         const RtdlSegment*   segments,  size_t segment_count,
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         RtdlSegmentPolygonAnyHitRow* rows_out, size_t output_capacity,
         size_t* emitted_count_out, uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_k_bounded_i64(
         const int64_t* candidate_rows, size_t candidate_count,
         size_t row_width, int64_t* rows_out, size_t row_capacity,
         size_t* emitted_count_out, uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_aggregate_frontier_2d(
         const RtdlAggregateFrontierSource2D* sources, size_t source_count,
         const RtdlAggregateFrontierNode2D* nodes, size_t node_count,
         const uint64_t* child_offsets, const int64_t* child_ids,
         const uint64_t* member_offsets, const int64_t* member_ids,
         double theta, uint64_t max_rows_per_source, uint64_t row_capacity,
         uint32_t deduplicate_fallback_targets,
         int64_t* frontier_rows_out, uint64_t* row_offsets_out,
         uint64_t* emitted_count_out, uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_k_bounded_i64_device(
         uint64_t candidate_rows_device_ptr, size_t candidate_count,
         size_t row_width, uint64_t rows_out_device_ptr, size_t row_capacity,
         size_t* emitted_count_out, uint32_t* overflowed_out,
         uint64_t* h2d_transfers_out, uint64_t* d2h_transfers_out,
         uint64_t* internal_device_transfers_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_k_cooperative_launch_capability(
         int* cooperative_launch_supported_out,
         int* cooperative_multi_device_launch_supported_out,
         int* multiprocessor_count_out,
         int* max_threads_per_block_out,
         int* max_shared_memory_per_block_optin_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_k_cooperative_launch_smoke(
         int requested_blocks, int requested_threads,
         int* observed_blocks_out,
         int* sync_observed_blocks_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_shape_pair_candidates_bounded(
         const RtdlPolygonRef* left_polygons, size_t left_count,
         const double* left_vertices_xy,      size_t left_vertex_xy_count,
         const RtdlPolygonRef* right_polygons, size_t right_count,
         const double* right_vertices_xy,      size_t right_vertex_xy_count,
         RtdlPolygonPairCandidate* candidates_out, size_t candidate_capacity,
         size_t* emitted_count_out, uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_segment_shape_anyhit_rows_2d(
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_segment_shape_anyhit_rows_2d(
         void* prepared,
         const RtdlSegment* segments, size_t segment_count,
         RtdlSegmentPolygonAnyHitRow* rows_out, size_t output_capacity,
         size_t* emitted_count_out, uint32_t* overflowed_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_segment_shape_anyhit_rows_2d(void* prepared);
int  rtdl_optix_run_point_nearest_segment(
         const RtdlPoint*   points,   size_t point_count,
         const RtdlSegment* segments, size_t segment_count,
         RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_fixed_radius_neighbors(
         const RtdlPoint* query_points, size_t query_count,
         const RtdlPoint* search_points, size_t search_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_fixed_radius_neighbors_3d(
         const RtdlPoint3D* query_points, size_t query_count,
         const RtdlPoint3D* search_points, size_t search_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_fixed_radius_neighbors_3d(
         const RtdlPoint3D* search_points, size_t search_count,
         double max_radius,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_fixed_radius_neighbors_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_exact_fixed_radius_neighbors_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusRankedNeighborSummary** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_fixed_radius_neighbors_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_summarize_prepared_fixed_radius_neighbors_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusNeighborSummary* summary_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d(void* prepared);
int  rtdl_optix_prepare_fixed_radius_count_threshold_3d(
         const RtdlPoint3D* search_points, size_t search_count,
         double max_radius,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t threshold,
         uint32_t* query_ids_out,
         uint32_t* neighbor_counts_out,
         uint32_t* threshold_flags_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_fixed_radius_adjacency_3d_device_outputs(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         const int64_t* edge_offsets,
         int32_t* neighbor_indices_out,
         size_t neighbor_index_capacity,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         size_t query_index_offset,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs_with_options(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         size_t query_index_offset,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint32_t same_root_culling,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs_with_execution_options(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         size_t query_index_offset,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint32_t same_root_culling,
         uint32_t direct_side_effect,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs(
         void* prepared,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_options(
         void* prepared,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint32_t same_root_culling,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_execution_options(
         void* prepared,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint32_t same_root_culling,
         uint32_t direct_side_effect,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry(
         void* prepared,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint64_t* telemetry_out,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_options(
         void* prepared,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint64_t* telemetry_out,
         uint32_t same_root_culling,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_execution_options(
         void* prepared,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint64_t* telemetry_out,
         uint32_t same_root_culling,
         uint32_t direct_side_effect,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs(
         void* prepared,
         size_t query_start,
         size_t query_count,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint64_t* telemetry_out,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_options(
         void* prepared,
         size_t query_start,
         size_t query_count,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint64_t* telemetry_out,
         uint32_t same_root_culling,
         size_t item_count,
         char* error_out, size_t error_size);
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_execution_options(
         void* prepared,
         size_t query_start,
         size_t query_count,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint64_t* telemetry_out,
         uint32_t same_root_culling,
         uint32_t direct_side_effect,
         size_t item_count,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d(void* prepared);
int  rtdl_optix_run_fixed_radius_count_threshold(
         const RtdlPoint* query_points, size_t query_count,
         const RtdlPoint* search_points, size_t search_count,
         double radius,
         size_t threshold,
         RtdlFixedRadiusCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_fixed_radius_count_threshold_2d(
         const RtdlPoint* search_points, size_t search_count,
         double max_radius,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns(
         const uint32_t* search_ids,
         const double* search_x,
         const double* search_y,
         size_t search_count,
         double max_radius,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_fixed_radius_count_threshold_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         size_t threshold,
         RtdlFixedRadiusCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns(
         void* prepared,
         const uint32_t* query_ids,
         const double* query_x,
         const double* query_y,
         size_t query_count,
         double radius,
         size_t threshold,
         uint32_t* query_ids_out,
         uint32_t* neighbor_counts_out,
         uint32_t* threshold_flags_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         size_t threshold,
         size_t* threshold_reached_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d(void* prepared);
int  rtdl_optix_prepare_point_group_nearest_witness_2d(
         const RtdlPoint* search_points, size_t search_count,
         const RtdlPointGroupBounds2D* groups, size_t group_count,
         double max_radius,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_point_group_threshold_reached_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         size_t threshold,
         size_t* threshold_reached_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_point_group_threshold_flags_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         size_t threshold,
         uint32_t* threshold_flags_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_point_group_nearest_witness_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         RtdlFixedRadiusNeighborRow* row_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_point_group_nearest_witness_2d(void* prepared);
int  rtdl_optix_run_k_closest_hits(
         const RtdlPoint* query_points, size_t query_count,
         const RtdlPoint* search_points, size_t search_count,
         size_t k,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_k_closest_hits_3d(
         const RtdlPoint3D* query_points, size_t query_count,
         const RtdlPoint3D* search_points, size_t search_count,
         size_t k,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_frontier_edge_traversal_packet(
         const uint32_t* row_offsets, size_t row_offset_count,
         const uint32_t* column_indices, size_t edge_index_count,
         const RtdlFrontierVertex* frontier, size_t frontier_count,
         const uint32_t* visited_vertices, size_t visited_count,
         uint32_t dedupe,
         RtdlBfsExpandRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_edge_neighbor_intersection_packet(
         const uint32_t* row_offsets, size_t row_offset_count,
         const uint32_t* column_indices, size_t edge_index_count,
         const RtdlEdgeSeed* seeds, size_t seed_count,
         uint32_t enforce_id_ascending,
         uint32_t unique,
         RtdlTriangleRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_conjunctive_scan(
         const RtdlColumnField* fields, size_t field_count,
         const RtdlColumnScalar* row_values, size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         RtdlColumnRowIdRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_grouped_count(
         const RtdlColumnField* fields, size_t field_count,
         const RtdlColumnScalar* row_values, size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         RtdlGroupedCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_grouped_sum(
         const RtdlColumnField* fields, size_t field_count,
         const RtdlColumnScalar* row_values, size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         RtdlGroupedSumRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_payload_create(
         const RtdlColumnField* fields, size_t field_count,
         const RtdlColumnScalar* row_values, size_t row_count,
         const char* const* primary_fields, size_t primary_field_count,
         RtdlOptixColumnarPayload** dataset_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_payload_create_from_columns(
         const RtdlPayloadField* fields, size_t field_count,
         size_t row_count,
         const char* const* primary_fields, size_t primary_field_count,
         RtdlOptixColumnarPayload** dataset_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_payload_create_from_device_columns(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const char* const* primary_fields, size_t primary_field_count,
         RtdlOptixColumnarPayload** dataset_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_count_i64(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         RtdlGroupedCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         size_t group_capacity,
         RtdlGroupedCountRow** rows_out, size_t* row_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_sum_i64(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         RtdlGroupedSumRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_sum_i64_with_capacity(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         size_t group_capacity,
         RtdlGroupedSumRow** rows_out, size_t* row_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_min_i64_with_capacity(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         size_t group_capacity,
         RtdlGroupedSumRow** rows_out, size_t* row_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_max_i64_with_capacity(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         size_t group_capacity,
         RtdlGroupedSumRow** rows_out, size_t* row_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_sum_count_i64_with_capacity(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         size_t group_capacity,
         RtdlGroupedSumCountRow** rows_out, size_t* row_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_stats_i64_with_capacity(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         size_t group_capacity,
         RtdlGroupedStatsRow** rows_out, size_t* row_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
void rtdl_optix_columnar_payload_destroy(RtdlOptixColumnarPayload* dataset);
int  rtdl_optix_columnar_payload_multi_predicate_scan(
         RtdlOptixColumnarPayload* dataset,
         const RtdlColumnClause* clauses, size_t clause_count,
         RtdlColumnRowIdRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_payload_multi_predicate_scan_count(
         RtdlOptixColumnarPayload* dataset,
         const RtdlColumnClause* clauses, size_t clause_count,
         size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_payload_grouped_reduction_count(
         RtdlOptixColumnarPayload* dataset,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         RtdlGroupedCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_payload_grouped_reduction_sum(
         RtdlOptixColumnarPayload* dataset,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         const char* value_field,
         RtdlGroupedSumRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_payload_compact_summary_batch(
         RtdlOptixColumnarPayload* dataset,
         const RtdlColumnCompactSummaryRequest* requests,
         size_t request_count,
         RtdlColumnCompactSummaryResult** results_out,
         size_t* result_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_columnar_compact_summary_results_destroy(
         RtdlColumnCompactSummaryResult* results,
         size_t result_count);
int  rtdl_optix_columnar_payload_get_last_phase_timings(
         double* traversal_out,
         double* bitset_copy_out,
         double* exact_filter_out,
         double* output_pack_out,
         size_t* raw_candidate_count_out,
         size_t* emitted_count_out);
int  rtdl_optix_segment_pair_intersection_get_last_phase_timings(
         double* left_upload_out,
         double* candidate_count_out,
         double* candidate_write_out,
         double* candidate_download_out,
         double* exact_refine_out,
         size_t* raw_candidate_count_out,
         size_t* emitted_count_out,
         uint32_t* mode_out);
int  rtdl_optix_fixed_radius_neighbors_3d_get_last_phase_timings(
         double* prepare_out,
         double* upload_out,
         double* candidate_count_out,
         double* count_download_out,
         double* row_offset_upload_out,
         double* candidate_write_out,
         double* row_download_out,
         double* exact_refine_out,
         size_t* raw_candidate_count_out,
         size_t* emitted_count_out,
         uint32_t* mode_out);
int  rtdl_optix_get_last_phase_timings(
         double* bvh_build_out,
         double* traversal_out,
         double* copy_out);
void rtdl_optix_free_rows(void* rows);

} // extern "C"
