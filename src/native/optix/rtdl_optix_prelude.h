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
// Device kernels are embedded as CUDA source strings and compiled to PTX/CUBIN
// at runtime. Loaded modules are cached across calls in static singletons;
// direct-CUDA CUBIN helpers also use a build-scoped content-addressed disk cache
// so a new process can avoid repeating nvcc compilation.
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
//        -DRTDL_OPTIX_BUILD_ID='"<cache-relevant-build-input-id>"' \
//        -lcuda -lnvrtc \
//        rtdl_optix.cpp -o librtdl_optix.so
// Deployable AOT providers may instead define RTDL_OPTIX_LAZY_NVRTC and link
// -ldl.  Those providers load the build-pinned NVRTC image only if a legacy
// source-compilation entry point is actually called; precompiled V4 execution
// has no eager compiler-runtime dependency.
// Persistent CUBIN caching is disabled when RTDL_OPTIX_BUILD_ID is omitted or
// empty. Reproducible packagers should derive it from all cache-relevant native
// build inputs; the project Makefile injects a fresh ID for each actual build.

#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stack_size.h>
#include <optix_stubs.h>

#include <cuda.h>
#include <cuda_runtime.h>
#include <nvrtc.h>

#include "rtdl_optix_v4_product_status.h"

#include <algorithm>
#include <atomic>
#include <array>
#include <cassert>
#include <cerrno>
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
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

#if defined(RTDL_OPTIX_LAZY_NVRTC)
#include <dlfcn.h>
#endif

// OptiX 7.7 renamed the PTX module entry point and added the pipeline
// argument to the stack-size accumulator.  Keep one source compatible with
// the frozen 7.6--9.1 range without choosing behavior from a runtime result.
inline OptixResult rtdlOptixModuleCreateCompat(
        OptixDeviceContext context,
        const OptixModuleCompileOptions* module_options,
        const OptixPipelineCompileOptions* pipeline_options,
        const char* ptx,
        std::size_t ptx_size,
        char* log,
        std::size_t* log_size,
        OptixModule* module) {
#if OPTIX_VERSION >= 70700
    return optixModuleCreate(
        context, module_options, pipeline_options, ptx, ptx_size,
        log, log_size, module);
#else
    return optixModuleCreateFromPTX(
        context, module_options, pipeline_options, ptx, ptx_size,
        log, log_size, module);
#endif
}

inline OptixResult rtdlOptixAccumulateStackSizesCompat(
        OptixProgramGroup group,
        OptixStackSizes* sizes,
        OptixPipeline pipeline) {
#if OPTIX_VERSION >= 70700
    return optixUtilAccumulateStackSizes(group, sizes, pipeline);
#else
    (void)pipeline;
    return optixUtilAccumulateStackSizes(group, sizes);
#endif
}

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

void rtdl_cuda_local_grid_nearest_seed_3d_precompiled(
        const double* query_coords,
        const int64_t* query_ids,
        uint32_t query_count,
        const double* target_coords,
        const int64_t* target_ids,
        uint32_t target_count,
        const int64_t* cell_ids,
        const int64_t* original_cell_ids,
        const int64_t* dense_cell_positions,
        uint32_t dense_cell_position_count,
        const int64_t* point_begin_offsets,
        const int64_t* point_counts,
        const int64_t* point_row_indices,
        uint32_t point_row_index_count,
        uint32_t cell_count,
        int dim_x,
        int dim_y,
        int dim_z,
        double lower_x,
        double lower_y,
        double lower_z,
        double upper_x,
        double upper_y,
        double upper_z,
        double* nearest_distances_out,
        int64_t* nearest_item_ids_out,
        int64_t* seed_cell_ids_out,
        int64_t* seed_cell_point_counts_out,
        int64_t* grid_cell_probe_counts_out);

void rtdl_cuda_grid_branch_bound_nearest_seed_3d_precompiled(
        const double* query_coords,
        const int64_t* query_ids,
        uint32_t query_count,
        const double* target_coords,
        const int64_t* target_ids,
        uint32_t target_count,
        const int64_t* cell_ids,
        const int64_t* original_cell_ids,
        const int64_t* dense_cell_positions,
        uint32_t dense_cell_position_count,
        const int64_t* point_begin_offsets,
        const int64_t* point_counts,
        const int64_t* point_row_indices,
        uint32_t point_row_index_count,
        uint32_t cell_count,
        int dim_x,
        int dim_y,
        int dim_z,
        double lower_x,
        double lower_y,
        double lower_z,
        double upper_x,
        double upper_y,
        double upper_z,
        double* nearest_distances_out,
        int64_t* nearest_item_ids_out,
        int64_t* seed_cell_ids_out,
        int64_t* seed_cell_point_counts_out,
        int64_t* grid_cell_probe_counts_out,
        int64_t* scanned_cell_counts_out,
        int64_t* scanned_point_counts_out,
        int64_t* shell_counts_out);

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

// Goal5814 exact shared Particle device template and reusable product-native
// lifecycle.  Both source/descriptor functions support a null-output,
// zero-capacity size query.  Execute is intentionally fixed at 5,000 queries.
int rtdl_optix_v4_particle_strict_interior_source_v1(
        char* source_out, size_t source_capacity, size_t* source_bytes_out,
        char* error_out, size_t error_size);
int rtdl_optix_v4_particle_strict_interior_descriptor_v1(
        char* descriptor_out, size_t descriptor_capacity,
        size_t* descriptor_bytes_out, char* error_out, size_t error_size);
int rtdl_optix_v4_prepare_particle_strict_interior_v1(
        const char* exact_template_ptx,
        const float* vertices_xyz, size_t vertex_count,
        const uint32_t* triangle_indices, size_t triangle_count,
        const uint32_t* front_values, const uint32_t* back_values,
        uint64_t* prepared_token_out, char* error_out, size_t error_size);
int rtdl_optix_v4_execute_prepared_particle_strict_interior_v1(
        uint64_t prepared_token,
        const float* query_ox, const float* query_oy, const float* query_oz,
        const float* query_dx, const float* query_dy, const float* query_dz,
        const float* query_tmax, size_t query_count,
        uint32_t* output_selected, uint32_t* output_neighbor,
        uint32_t* output_face, RtdlV4ParticleControl* output_control,
        RtdlV4ParticleFastReceipt* output_receipt,
        char* error_out, size_t error_size);
// The v2 output pointer is native-owned packed SoA u32[3][row_count], valid
// until the next execute on the same token or destroy.  Failure returns
// nullptr/zero and performs zero application-output D2H.
int rtdl_optix_v4_execute_prepared_particle_strict_interior_v2(
        uint64_t prepared_token,
        const float* query_ox, const float* query_oy, const float* query_oz,
        const float* query_dx, const float* query_dy, const float* query_dz,
        const float* query_tmax, size_t query_count,
        const uint32_t** output_columns_soa, size_t* output_row_count,
        RtdlV4ParticleControl* output_control,
        RtdlV4ParticleFastReceipt* output_receipt,
        char* error_out, size_t error_size);
// The v3 prevalidated route has the same transfer/output ABI as v2 and is
// reserved for the product-public sealed immutable input capability.  It
// skips only repeated per-value host validation; structural validation,
// seven H2D calls, one launch and status-before-output remain mandatory.
int rtdl_optix_v4_execute_prepared_particle_strict_interior_prevalidated_v3(
        uint64_t prepared_token,
        const float* query_ox, const float* query_oy, const float* query_oz,
        const float* query_dx, const float* query_dy, const float* query_dz,
        const float* query_tmax, size_t query_count,
        const uint32_t** output_columns_soa, size_t* output_row_count,
        RtdlV4ParticleControl* output_control,
        RtdlV4ParticleFastReceipt* output_receipt,
        char* error_out, size_t error_size);
int rtdl_optix_v4_destroy_prepared_particle_strict_interior_v1(
        uint64_t* prepared_token_inout,
        char* error_out, size_t error_size);

// Behavior-level receipt emitted by the thread-local OptiX traversal audit
// session. A successful launch is claim-complete only when the native route
// bound both a nonzero traversable handle and a stable physical
// program-bundle id before the actual optixLaunch call.
struct RtdlOptixTraversalAuditSnapshot {
    uint64_t nonce_hi;
    uint64_t nonce_lo;
    uint64_t attempted_launch_count;
    uint64_t successful_launch_count;
    uint64_t failed_launch_count;
    uint64_t complete_context_launch_count;
    uint64_t incomplete_context_launch_count;
    uint64_t context_bind_count;
    uint64_t raygen_invocation_count;
    uint64_t program_bundle_mix;
    uint64_t traversable_mix;
    uint64_t pipeline_mix;
    uint64_t sbt_mix;
    uint64_t stream_mix;
    uint64_t params_mix;
    uint64_t callsite_mix;
    uint64_t first_program_bundle_id;
    uint64_t last_program_bundle_id;
    uint64_t first_traversable;
    uint64_t last_traversable;
    uint32_t pending_context_at_finish;
    uint32_t session_error;
    uint32_t incomplete_callsite_record_count;
    uint32_t incomplete_callsite_lines[32];
};

struct RtdlSegment {
    uint32_t id;
    double x0, y0, x1, y1;
};

struct RtdlRayjoinCdbSegment {
    uint32_t id;
    double x0, y0, x1, y1;
    uint32_t left_face_id;
    uint32_t right_face_id;
};
typedef RtdlRayjoinCdbSegment RtdlDirectedSegmentFace2D;

struct RtdlPoint {
    uint32_t id;
    double x, y;
};

struct RtdlAabb2D {
    uint32_t id;
    double min_x, min_y, max_x, max_y;
};

struct RtdlAabb3D {
    uint32_t id;
    double min_x, min_y, min_z, max_x, max_y, max_z;
};

struct RtdlAabbPairRow {
    uint32_t query_id;
    uint32_t indexed_id;
};
static_assert(offsetof(RtdlAabbPairRow, query_id) == 0, "RtdlAabbPairRow query offset mismatch");
static_assert(offsetof(RtdlAabbPairRow, indexed_id) == 4, "RtdlAabbPairRow indexed offset mismatch");
static_assert(sizeof(RtdlAabbPairRow) == 8, "RtdlAabbPairRow size mismatch");

struct RtdlCellMbrFrontierRow {
    int64_t frontier_kind_code;
    int64_t query_row_id;
    int64_t query_point_id;
    int64_t cell_id;
    uint64_t point_begin_offset;
    uint64_t point_count;
    double min_distance;
    double max_distance;
};

struct RtdlActiveQueryStatusStreamRow {
    int64_t active_queue_index;
    int64_t query_row_id;
    int64_t source_id;
    int64_t cell_id;
    int64_t status_code;
    int64_t transition_phase_code;
    double current_best_before_sq;
    double current_best_after_sq;
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

struct RtdlSegmentPairIdRow {
    uint32_t left_id, right_id;
};

struct RtdlSegmentFirstHitRow {
    uint32_t probe_id, primitive_id;
    double hit_x, hit_y, hit_t;
};

struct RtdlRayjoinCdbPointLocationRow {
    uint32_t point_id;
    uint32_t face_id;
    uint32_t segment_id;
    double hit_t;
};
typedef RtdlRayjoinCdbPointLocationRow RtdlDirectedSegmentPointLocationRow2D;

struct RtdlRayjoinCdbScaledPoint {
    uint32_t id;
    double x, y;
    int64_t sx, sy;
};
typedef RtdlRayjoinCdbScaledPoint RtdlDirectedSegmentScaledPoint2D;
struct RtdlDirectedSegmentDeviceQueryPoint2D {
    float x, y;
    uint32_t id;
    uint32_t has_scaled;
    int64_t sx, sy;
};

struct RtdlPipRow {
    uint32_t point_id, polygon_id, contains;
};

struct RtdlPointClosedShapeMembershipRow {
    uint32_t point_id, shape_id, membership;
};

struct RtdlPointClosedShapeBoundaryEventRow {
    uint32_t point_id, shape_id, boundary_id;
    double crossing_t, crossing_x, crossing_y;
    uint32_t event_kind;
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

struct RtdlNativeDeviceHitStreamColumns {
    uint64_t ray_ids_device_ptr;
    uint64_t primitive_ids_device_ptr;
    uint64_t row_count;
    uint64_t capacity;
    uint64_t hit_event_count;
    uint32_t overflow;
    int32_t device_ordinal;
    void* owner_handle;
    double traversal_seconds;
    uint64_t row_count_device_ptr;
    uint64_t hit_event_count_device_ptr;
    uint64_t overflow_device_ptr;
};

struct RtdlNativeDevicePairColumns {
    uint64_t left_ids_device_ptr;
    uint64_t right_ids_device_ptr;
    uint64_t row_count;
    uint64_t capacity;
    uint64_t candidate_event_count;
    uint32_t overflow;
    int32_t device_ordinal;
    void* owner_handle;
    double traversal_seconds;
    uint64_t row_count_device_ptr;
    uint64_t candidate_event_count_device_ptr;
    uint64_t overflow_device_ptr;
    uint64_t left_ordinals_device_ptr;
    uint64_t right_ordinals_device_ptr;
    uint64_t relation_status_device_ptr;
    uint64_t relation_boundary_ordinals_device_ptr;
};

struct RtdlNativePointLocationDeviceIdColumns {
    uint64_t ids_device_ptr;
    uint64_t row_count;
    uint64_t capacity;
    uint32_t overflow;
    int32_t device_ordinal;
    double traversal_seconds;
};

struct RtdlNativeClosedShapeScalarCountSummary {
    uint64_t row_count;
    uint64_t candidate_event_count;
    uint64_t boundary_candidate_event_count;
    uint64_t dropped_candidate_event_count;
    uint32_t exact_boundary_correction_used;
    uint32_t relation_status_correction_used;
    uint32_t overflow;
    int32_t device_ordinal;
    double traversal_seconds;
    double point_eps;
};

struct RtdlNativePairColumnPagePlanInfo {
    uint64_t item_count;
    uint64_t page_size;
    uint64_t page_count;
    uint64_t initial_capacity;
    uint32_t native_page_plan_handle;
    uint32_t automatic_retry_authorized;
};

struct RtdlNativeDeviceGroupedCountI64Columns {
    uint64_t counts_device_ptr;
    uint64_t group_capacity;
    uint64_t source_row_count;
    uint32_t overflow;
    int32_t device_ordinal;
    void* owner_handle;
    double reduction_seconds;
    uint64_t source_row_count_device_ptr;
    uint64_t overflow_device_ptr;
    uint64_t ambiguous_count_device_ptr;
};

struct RtdlNativeClosedShapeBoundaryEventDeviceColumns {
    uint64_t point_ids_device_ptr;
    uint64_t shape_ids_device_ptr;
    uint64_t boundary_ids_device_ptr;
    uint64_t crossing_t_device_ptr;
    uint64_t crossing_x_device_ptr;
    uint64_t crossing_y_device_ptr;
    uint64_t event_kinds_device_ptr;
    uint64_t row_count;
    uint64_t capacity;
    uint64_t candidate_event_count;
    uint32_t overflow;
    int32_t device_ordinal;
    void* owner_handle;
    double traversal_seconds;
};

struct RtdlNativeShapePairRelationDeviceColumns {
    uint64_t left_ids_device_ptr;
    uint64_t right_ids_device_ptr;
    uint64_t left_ordinals_device_ptr;
    uint64_t right_ordinals_device_ptr;
    uint64_t requires_segment_intersection_device_ptr;
    uint64_t requires_point_containment_device_ptr;
    uint64_t left_polygon_refs_device_ptr;
    uint64_t right_polygon_refs_device_ptr;
    uint64_t left_vertices_x_device_ptr;
    uint64_t left_vertices_y_device_ptr;
    uint64_t right_vertices_x_device_ptr;
    uint64_t right_vertices_y_device_ptr;
    uint64_t left_bounds_device_ptr;
    uint64_t right_bounds_device_ptr;
    uint64_t row_count;
    uint64_t capacity;
    uint64_t active_relation_count;
    uint64_t left_polygon_count;
    uint64_t right_polygon_count;
    uint64_t left_vertex_count;
    uint64_t right_vertex_count;
    uint32_t overflow;
    int32_t device_ordinal;
    void* owner_handle;
    double traversal_seconds;
    double continuation_seconds;
};

struct RtdlNativeDeviceGroupedCountI64CompactColumns {
    uint64_t group_keys_device_ptr;
    uint64_t counts_device_ptr;
    uint64_t row_count;
    uint64_t capacity;
    uint64_t group_capacity;
    uint64_t source_row_count;
    uint32_t overflow;
    int32_t device_ordinal;
    void* owner_handle;
    double reduction_seconds;
    double compaction_seconds;
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

struct RtdlFixedRadiusRankedNeighborAggregate {
    size_t query_count;
    size_t bounded_neighbor_count;
    uint64_t nearest_id_checksum;
    uint64_t kth_id_checksum;
    double sum_distance;
};
static_assert(offsetof(RtdlFixedRadiusRankedNeighborAggregate, query_count) == 0, "RtdlFixedRadiusRankedNeighborAggregate query count offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborAggregate, bounded_neighbor_count) == 8, "RtdlFixedRadiusRankedNeighborAggregate neighbor count offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborAggregate, nearest_id_checksum) == 16, "RtdlFixedRadiusRankedNeighborAggregate nearest checksum offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborAggregate, kth_id_checksum) == 24, "RtdlFixedRadiusRankedNeighborAggregate kth checksum offset mismatch");
static_assert(offsetof(RtdlFixedRadiusRankedNeighborAggregate, sum_distance) == 32, "RtdlFixedRadiusRankedNeighborAggregate sum offset mismatch");
static_assert(sizeof(RtdlFixedRadiusRankedNeighborAggregate) == 40, "RtdlFixedRadiusRankedNeighborAggregate size mismatch");

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
int  rtdl_optix_prepare_segment_pair_left_set(
         const RtdlSegment* left, size_t left_count,
         void** prepared_left_out,
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
int  rtdl_optix_count_prepared_segment_pair_intersection_prepared_left(
         void* prepared,
         void* prepared_left,
         size_t* count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_repeated(
         void* prepared,
         void* prepared_left,
         size_t repeat_count,
         size_t* count_out,
         double* total_seconds_out,
         double* min_seconds_out,
         double* max_seconds_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_direct_intersection(
         void* prepared,
         void* prepared_left,
         size_t* count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection(
         void* prepared,
         void* prepared_left,
         size_t* count_out,
         size_t* group_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection_with_predicate_mode(
         void* prepared,
         void* prepared_left,
         uint32_t predicate_mode,
         size_t* count_out,
         size_t* group_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection_with_predicate_mode(
         void* prepared,
         void* prepared_left,
         uint32_t predicate_mode,
         RtdlSegmentPairIntersectionRow** rows_out,
         size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_segment_pair_id_rows_prepared_left_grouped_range_direct_intersection_with_predicate_mode(
         void* prepared,
         void* prepared_left,
         uint32_t predicate_mode,
         RtdlSegmentPairIdRow** rows_out,
         size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_segment_pair_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode(
         void* prepared,
         void* prepared_left,
         uint32_t predicate_mode,
         RtdlNativeDevicePairColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_segment_pair_bounded_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode(
         void* prepared,
         void* prepared_left,
         uint32_t predicate_mode,
         size_t max_rows,
         RtdlNativeDevicePairColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_segment_pair_candidate_device_columns(
         void* prepared,
         const RtdlSegment* left, size_t left_count,
         size_t max_rows,
         RtdlNativeDevicePairColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_release_segment_pair_candidate_device_columns(
         void* owner_handle,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_segment_pair_left_id_count_device_columns(
         void* prepared,
         const RtdlSegment* left, size_t left_count,
         size_t group_capacity,
         RtdlNativeDeviceGroupedCountI64Columns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_segment_pair_left_id_count_device_columns_with_ambiguity_status(
         void* prepared,
         const RtdlSegment* left, size_t left_count,
         size_t group_capacity,
         RtdlNativeDeviceGroupedCountI64Columns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_segment_pair_left_id_count_prepared_left_device_columns(
         void* prepared,
         void* prepared_left,
         size_t group_capacity,
         RtdlNativeDeviceGroupedCountI64Columns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_release_segment_pair_left_id_count_device_columns(
         void* owner_handle,
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
int  rtdl_optix_prepare_directed_segment_point_location_2d(
         const RtdlDirectedSegmentFace2D* segments,
         size_t segment_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_directed_segment_point_location_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         RtdlDirectedSegmentPointLocationRow2D** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_directed_segment_point_location_points_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         void** prepared_points_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_directed_segment_point_location_device_query_points_2d(
         void* prepared,
         uint64_t device_points_ptr, size_t point_count,
         void** prepared_points_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_directed_segment_point_location_2d_device_points(
         void* prepared,
         void* prepared_points,
         size_t* positive_face_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_directed_segment_point_location_2d_device_segment_ids(
         void* prepared,
         void* prepared_points,
         size_t* point_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_directed_segment_point_location_2d_device_face_ids(
         void* prepared,
         void* prepared_points,
         size_t* point_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_directed_segment_point_location_2d_device_segment_id_columns(
         void* prepared,
         void* prepared_points,
         RtdlNativePointLocationDeviceIdColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns(
         void* prepared,
         void* prepared_points,
         RtdlNativePointLocationDeviceIdColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_directed_segment_point_location_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t* positive_face_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_directed_segment_point_location_2d(void* prepared);
void rtdl_optix_destroy_prepared_directed_segment_point_location_points_2d(void* prepared_points);
int  rtdl_optix_prepare_rayjoin_cdb_point_location_2d(
         const RtdlRayjoinCdbSegment* segments,
         size_t segment_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_rayjoin_cdb_point_location_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         RtdlRayjoinCdbPointLocationRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_rayjoin_cdb_point_location_scaled_points_2d(
         void* prepared,
         const RtdlRayjoinCdbScaledPoint* points, size_t point_count,
         RtdlRayjoinCdbPointLocationRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_rayjoin_cdb_point_location_points_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         void** prepared_points_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_rayjoin_cdb_point_location_scaled_points_2d(
         void* prepared,
         const RtdlRayjoinCdbScaledPoint* points, size_t point_count,
         void** prepared_points_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_rayjoin_cdb_point_location_2d_device_points(
         void* prepared,
         void* prepared_points,
         size_t* positive_face_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_segment_ids(
         void* prepared,
         void* prepared_points,
         size_t* point_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_face_ids(
         void* prepared,
         void* prepared_points,
         size_t* point_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_rayjoin_cdb_point_location_2d_device_segment_id_columns(
         void* prepared,
         void* prepared_points,
         RtdlNativePointLocationDeviceIdColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_rayjoin_cdb_point_location_2d_device_face_id_columns(
         void* prepared,
         void* prepared_points,
         RtdlNativePointLocationDeviceIdColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_rayjoin_cdb_point_location_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t* positive_face_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_rayjoin_cdb_point_location_2d(void* prepared);
void rtdl_optix_destroy_prepared_rayjoin_cdb_point_location_points_2d(void* prepared_points);
void rtdl_optix_destroy_prepared_segment_pair_intersection(void* prepared);
void rtdl_optix_destroy_prepared_segment_pair_left_set(void* prepared_left);
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
int  rtdl_optix_count_prepared_point_closed_shape_membership_prepared_points_2d(
         void* prepared,
         void* prepared_points,
         size_t* count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d(
         void* prepared,
         void* prepared_points,
         size_t max_candidate_rows,
         void** executor_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d(
         void* executor,
         size_t* count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d(
         void* executor);
int  rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t* count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_point_probe_columns_2d(
         const RtdlPoint* points, size_t point_count,
         void** prepared_points_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_prepared_points_2d(
         void* prepared,
         void* prepared_points,
         size_t* count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_2d(
         void* prepared,
         void* prepared_points,
         size_t request_count,
         size_t* counts_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_point_closed_shape_membership_relation_status_corrected_prepared_points_2d(
         void* prepared,
         void* prepared_points,
         double point_eps,
         RtdlNativeClosedShapeScalarCountSummary* summary_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d(
         void* prepared,
         void* prepared_points,
         double point_eps,
         void** executor_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d(
         void* executor,
         RtdlNativeClosedShapeScalarCountSummary* summary_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d(
         void* executor);
int  rtdl_optix_prepare_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d(
         void* prepared,
         void* prepared_points,
         size_t request_count,
         size_t stream_count,
         void** executor_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d(
         void* executor,
         size_t* counts_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d(
         void* executor);
int  rtdl_optix_prepare_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d(
         void* prepared,
         void* prepared_points,
         size_t request_count,
         void** graph_out,
         char* error_out, size_t error_size);
int  rtdl_optix_replay_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d(
         void* graph,
         size_t* counts_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d(
         void* graph);
int  rtdl_optix_run_prepared_point_closed_shape_first_boundary_crossing_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         RtdlPointClosedShapeBoundaryEventRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_point_closed_shape_first_boundary_crossing_device_columns_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t max_rows,
         RtdlNativeClosedShapeBoundaryEventDeviceColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_point_closed_shape_membership_candidate_device_columns_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t max_rows,
         RtdlNativeDevicePairColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_point_closed_shape_membership_relation_status_candidate_device_columns_prepared_points_2d(
         void* prepared,
         void* prepared_points,
         uint32_t relation_status_filter,
         size_t max_rows,
         RtdlNativeDevicePairColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t max_rows,
         RtdlNativeDevicePairColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_page_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t page_start, size_t page_count,
         size_t max_rows,
         RtdlNativeDevicePairColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_point_closed_shape_membership_exact_device_columns_page_plan_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t page_size, size_t initial_capacity,
         void** page_plan_out,
         RtdlNativePairColumnPagePlanInfo* info_out,
         char* error_out, size_t error_size);
int  rtdl_optix_produce_point_closed_shape_membership_exact_device_columns_page_2d(
         void* page_plan,
         size_t page_index, size_t max_rows,
         RtdlNativeDevicePairColumns* columns_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_point_closed_shape_membership_exact_device_columns_page_plan_2d(
         void* page_plan);
int  rtdl_optix_prepared_point_closed_shape_membership_point_id_count_device_columns_2d(
         void* prepared,
         const RtdlPoint* points, size_t point_count,
         size_t group_capacity,
         RtdlNativeDeviceGroupedCountI64Columns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_release_point_closed_shape_membership_candidate_device_columns_2d(
         void* owner_handle,
         char* error_out, size_t error_size);
int  rtdl_optix_release_point_closed_shape_membership_exact_device_columns_2d(
         void* owner_handle,
         char* error_out, size_t error_size);
int  rtdl_optix_release_point_closed_shape_boundary_event_device_columns_2d(
         void* owner_handle,
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
void rtdl_optix_destroy_prepared_point_probe_columns_2d(void* prepared_points);
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
int  rtdl_optix_prepare_shape_pair_relation_left_set(
         const RtdlPolygonRef* left_polys, size_t left_count,
         const double* left_verts_xy,      size_t left_vert_xy_count,
         void** prepared_left_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_shape_pair_relation_flags(
         void* prepared,
         const RtdlPolygonRef* left_polys, size_t left_count,
         const double* left_verts_xy,      size_t left_vert_xy_count,
         RtdlShapePairRelationRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_shape_pair_relation_flags(
         void* prepared,
         const RtdlPolygonRef* left_polys, size_t left_count,
         const double* left_verts_xy,      size_t left_vert_xy_count,
         size_t* active_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_shape_pair_relation_active_device(
         void* prepared,
         const RtdlPolygonRef* left_polys, size_t left_count,
         const double* left_verts_xy,      size_t left_vert_xy_count,
         size_t* active_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_count_prepared_shape_pair_relation_active_device_prepared_left(
         void* prepared,
         void* prepared_left,
         size_t* active_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_shape_pair_relation_active_device_prepared_left_executor(
         void* prepared,
         void* prepared_left,
         void** executor_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_shape_pair_relation_active_device_prepared_left_executor(
         void* executor,
         size_t* active_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_shape_pair_relation_active_device_prepared_left_executor(
         void* executor);
int  rtdl_optix_prepared_shape_pair_relation_active_device_columns(
         void* prepared,
         const RtdlPolygonRef* left_polys, size_t left_count,
         const double* left_verts_xy,      size_t left_vert_xy_count,
         size_t max_rows,
         RtdlNativeShapePairRelationDeviceColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_release_shape_pair_relation_active_device_columns(
         void* owner_handle,
         char* error_out, size_t error_size);
int  rtdl_optix_shape_pair_relation_get_last_phase_timings(
         double* left_prepare_out,
         double* left_upload_out,
         double* traversal_out,
         double* flag_download_out,
         double* containment_out,
         double* active_scan_out,
         size_t* pair_count_out,
         size_t* active_count_out,
         uint32_t* mode_out);
void rtdl_optix_destroy_prepared_shape_pair_relation_flags(void* prepared);
void rtdl_optix_destroy_prepared_shape_pair_relation_left_set(void* prepared_left);
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
int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         uint32_t deduplicate_primitives,
         size_t max_rows,
         RtdlNativeDeviceHitStreamColumns* columns_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         uint32_t deduplicate_primitives,
         size_t max_rows,
         uint64_t ray_ids_device_ptr,
         uint64_t primitive_ids_device_ptr,
         RtdlNativeDeviceHitStreamColumns* columns_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         uint32_t deduplicate_primitives,
         size_t max_rows,
         uint64_t ray_ids_device_ptr,
         uint64_t primitive_ids_device_ptr,
         uint64_t row_count_device_ptr,
         uint64_t hit_event_count_device_ptr,
         uint64_t overflow_device_ptr,
         RtdlNativeDeviceHitStreamColumns* columns_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_on_stream(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         uint32_t deduplicate_primitives,
         size_t max_rows,
         uint64_t ray_ids_device_ptr,
         uint64_t primitive_ids_device_ptr,
         uint64_t row_count_device_ptr,
         uint64_t hit_event_count_device_ptr,
         uint64_t overflow_device_ptr,
         uint64_t cuda_stream_ptr,
         RtdlNativeDeviceHitStreamColumns* columns_out,
         char* error_out, size_t error_size);
int rtdl_optix_release_ray_triangle_hit_stream_device_columns(
         void* owner_handle,
         char* error_out, size_t error_size);
int rtdl_optix_release_ray_triangle_hit_stream_async_launch(
         void* owner_handle,
         char* error_out, size_t error_size);
int rtdl_optix_primitive_grouped_i64_payload_3d_create(
         const uint32_t* primitive_group_ids, size_t primitive_group_id_count,
         const uint64_t* primitive_values, size_t primitive_value_count,
         size_t group_count,
         void** payload_handle_out,
         char* error_out, size_t error_size);
int rtdl_optix_primitive_grouped_i64_payload_3d_create_signed_v2(
         const uint32_t* primitive_group_ids, size_t primitive_group_id_count,
         const int64_t* primitive_values, size_t primitive_value_count,
         size_t group_count,
         void** payload_handle_out,
         char* error_out, size_t error_size);
/* Compiler-internal fast path. The caller must hold the immutable host-column
 * certificate covering group bounds and the signed per-group sum domain. */
int rtdl_optix_primitive_grouped_i64_payload_3d_create_signed_verified_v3(
         const uint32_t* primitive_group_ids, size_t primitive_group_id_count,
         const int64_t* primitive_values, size_t primitive_value_count,
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
int rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction_signed_v2(
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
int rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction_signed_v2(
         void* scene_handle,
         const RtdlRay3D* rays, size_t ray_count,
         const uint32_t* primitive_group_ids, size_t primitive_group_id_count,
         const int64_t* primitive_values, size_t primitive_value_count,
         size_t group_count,
         uint32_t reduction,
         uint64_t* group_counts_out,
         uint64_t* group_sums_out,
         uint64_t* group_mins_out,
         uint64_t* group_maxs_out,
         uint64_t* hit_event_count_out,
         double* traversal_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction_with_phase_timings(
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
         double* query_prepare_seconds_out,
         double* launch_seconds_out,
         double* result_download_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction_with_phase_timings_signed_v2(
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
         double* query_prepare_seconds_out,
         double* launch_seconds_out,
         double* result_download_seconds_out,
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
int rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_signed_v2(
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
int rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_with_phase_timings(
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
         double* query_prepare_seconds_out,
         double* launch_seconds_out,
         double* result_download_seconds_out,
         char* error_out, size_t error_size);
int rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_with_phase_timings_signed_v2(
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
         double* query_prepare_seconds_out,
         double* launch_seconds_out,
         double* result_download_seconds_out,
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
int  rtdl_optix_count_prepared_aabb_index_2d_multi_operation_packed_queries(
         void* prepared,
         void* prepared_point_queries,
         void* prepared_box_queries,
         size_t* point_contains_out,
         size_t* range_contains_out,
         size_t* range_intersects_out,
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
int  rtdl_optix_prepare_mutable_aabb_index_2d(
         const RtdlAabb2D* boxes, size_t box_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_refit_prepared_aabb_index_2d(
         void* prepared,
         const RtdlAabb2D* boxes, size_t box_count,
         char* error_out, size_t error_size);
int  rtdl_optix_refit_prepared_aabb_index_2d_slots(
         void* prepared,
         const uint32_t* slot_indices,
         const RtdlAabb2D* boxes,
         size_t update_count,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_aabb_queries_2d(void* prepared_queries);
void rtdl_optix_destroy_prepared_aabb_index_2d(void* prepared);
int  rtdl_optix_prepare_aabb_index_3d(
         const RtdlAabb3D* boxes, size_t box_count,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_prepared_aabb_index_3d_point_contains_rows(
         void* prepared,
         const RtdlPoint3D* point_queries, size_t point_query_count,
         RtdlAabbPairRow* rows_out, size_t row_capacity,
         size_t* emitted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_aabb_index_3d(void* prepared);
int  rtdl_optix_collect_cell_mbr_nearest_frontier_3d(
         const double* query_coords,
         const int64_t* query_point_ids,
         size_t query_count,
         const int64_t* cell_ids,
         const uint64_t* point_begin_offsets,
         const uint64_t* point_counts,
         const double* cell_mbr_min,
         const double* cell_mbr_max,
         size_t cell_count,
         double radius,
         const double* current_best_distances,
         const int64_t* current_best_item_ids,
         uint64_t max_inline_points,
         uint32_t emit_pruned_rows,
         uint64_t row_capacity,
         int64_t* frontier_kind_codes_out,
         int64_t* query_row_ids_out,
         int64_t* query_point_ids_out,
         int64_t* cell_ids_out,
         uint64_t* point_begin_offsets_out,
         uint64_t* point_counts_out,
         double* min_distances_out,
         double* max_distances_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2(
         const double* query_coords,
         const int64_t* query_point_ids,
         size_t query_count,
         const int64_t* cell_ids,
         const uint64_t* point_begin_offsets,
         const uint64_t* point_counts,
         const double* cell_mbr_min,
         const double* cell_mbr_max,
         size_t cell_count,
         double radius,
         const double* current_best_distances,
         const int64_t* current_best_item_ids,
         uint64_t max_inline_points,
         uint32_t emit_pruned_rows,
         uint32_t sort_rows,
         uint64_t row_capacity,
         int64_t* frontier_kind_codes_out,
         int64_t* query_row_ids_out,
         int64_t* query_point_ids_out,
         int64_t* cell_ids_out,
         uint64_t* point_begin_offsets_out,
         uint64_t* point_counts_out,
         double* min_distances_out,
         double* max_distances_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3(
         const double* query_coords,
         const int64_t* query_point_ids,
         size_t query_count,
         const int64_t* cell_ids,
         const uint64_t* point_begin_offsets,
         const uint64_t* point_counts,
         const double* cell_mbr_min,
         const double* cell_mbr_max,
         size_t cell_count,
         double radius,
         const double* current_best_distances,
         const int64_t* current_best_item_ids,
         const double* target_coords,
         const int64_t* target_point_ids,
         size_t target_count,
         const uint64_t* point_row_indices,
         size_t point_row_index_count,
         uint64_t max_inline_points,
         uint32_t emit_pruned_rows,
         uint32_t sort_rows,
         uint32_t inline_nearest,
         uint64_t row_capacity,
         int64_t* frontier_kind_codes_out,
         int64_t* query_row_ids_out,
         int64_t* query_point_ids_out,
         int64_t* cell_ids_out,
         uint64_t* point_begin_offsets_out,
         uint64_t* point_counts_out,
         double* min_distances_out,
         double* max_distances_out,
         double* nearest_distances_out,
         int64_t* nearest_item_ids_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v4(
         const double* query_coords,
         const int64_t* query_point_ids,
         size_t query_count,
         const int64_t* cell_ids,
         const uint64_t* point_begin_offsets,
         const uint64_t* point_counts,
         const double* cell_mbr_min,
         const double* cell_mbr_max,
         size_t cell_count,
         double radius,
         const double* current_best_distances,
         const int64_t* current_best_item_ids,
         const double* target_coords,
         const int64_t* target_point_ids,
         size_t target_count,
         const uint64_t* point_row_indices,
         size_t point_row_index_count,
         uint64_t max_inline_points,
         uint32_t emit_pruned_rows,
         uint32_t sort_rows,
         uint32_t inline_nearest,
         uint64_t row_capacity,
         int64_t* frontier_kind_codes_out,
         int64_t* query_row_ids_out,
         int64_t* query_point_ids_out,
         int64_t* cell_ids_out,
         uint64_t* point_begin_offsets_out,
         uint64_t* point_counts_out,
         double* min_distances_out,
         double* max_distances_out,
         double* nearest_distances_out,
         int64_t* nearest_item_ids_out,
         uint64_t* inline_cell_hit_count_out,
         uint64_t* inline_point_eval_count_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_point_column_domain_3d_v1(
         const double* target_coords,
         const int64_t* target_ids,
         size_t target_count,
         uint64_t* prepared_domain_token_out,
         char* error_out,
         size_t error_size);
int  rtdl_optix_collect_cell_mbr_nearest_frontier_3d_prepared_domain_v1(
         const double* query_coords,
         const int64_t* query_point_ids,
         size_t query_count,
         const int64_t* cell_ids,
         const uint64_t* point_begin_offsets,
         const uint64_t* point_counts,
         const double* cell_mbr_min,
         const double* cell_mbr_max,
         size_t cell_count,
         double radius,
         const double* current_best_distances,
         const int64_t* current_best_item_ids,
         uint64_t prepared_domain_token,
         const uint64_t* point_row_indices,
         size_t point_row_index_count,
         uint64_t max_inline_points,
         uint32_t emit_pruned_rows,
         uint32_t sort_rows,
         uint32_t inline_nearest,
         uint64_t row_capacity,
         int64_t* frontier_kind_codes_out,
         int64_t* query_row_ids_out,
         int64_t* query_point_ids_out,
         int64_t* cell_ids_out,
         uint64_t* point_begin_offsets_out,
         uint64_t* point_counts_out,
         double* min_distances_out,
         double* max_distances_out,
         double* nearest_distances_out,
         int64_t* nearest_item_ids_out,
         uint64_t* inline_cell_hit_count_out,
         uint64_t* inline_point_eval_count_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out,
         size_t error_size);
int  rtdl_optix_get_prepared_point_column_domain_3d_telemetry_v1(
         uint64_t prepared_domain_token,
         uint64_t* validation_count_out,
         uint64_t* execute_count_out,
         uint64_t* hash_set_construction_count_out,
         uint64_t* target_count_out,
         uint64_t* creator_pid_out,
         char* error_out,
         size_t error_size);
int  rtdl_optix_destroy_prepared_point_column_domain_3d_v1(
         uint64_t prepared_domain_token,
         char* error_out,
         size_t error_size);
int  rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5(
         const double* query_coords,
         const int64_t* query_point_ids,
         size_t query_count,
         const int64_t* cell_ids,
         const uint64_t* point_begin_offsets,
         const uint64_t* point_counts,
         const double* cell_mbr_min,
         const double* cell_mbr_max,
         size_t cell_count,
         double radius,
         const double* current_best_distances,
         const int64_t* current_best_item_ids,
         const double* target_coords,
         const int64_t* target_point_ids,
         size_t target_count,
         const uint64_t* point_row_indices,
         size_t point_row_index_count,
         uint64_t max_inline_points,
         uint32_t emit_pruned_rows,
         uint32_t sort_rows,
         uint32_t inline_nearest,
         uint64_t row_capacity,
         int64_t* frontier_kind_codes_out,
         int64_t* query_row_ids_out,
         int64_t* query_point_ids_out,
         int64_t* cell_ids_out,
         uint64_t* point_begin_offsets_out,
         uint64_t* point_counts_out,
         double* min_distances_out,
         double* max_distances_out,
         double* nearest_distances_out,
         int64_t* nearest_item_ids_out,
         uint64_t* inline_cell_hit_count_out,
         uint64_t* inline_point_eval_count_out,
         uint32_t global_bound_early_break,
         uint64_t* global_bound_early_break_count_out,
         double* global_bound_distance_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6(
         const double* query_coords,
         const int64_t* query_point_ids,
         size_t query_count,
         const int64_t* cell_ids,
         const uint64_t* point_begin_offsets,
         const uint64_t* point_counts,
         const double* cell_mbr_min,
         const double* cell_mbr_max,
         size_t cell_count,
         double radius,
         const double* current_best_distances,
         const int64_t* current_best_item_ids,
         const double* target_coords,
         const int64_t* target_point_ids,
         size_t target_count,
         const uint64_t* point_row_indices,
         size_t point_row_index_count,
         uint64_t max_inline_points,
         uint32_t emit_pruned_rows,
         uint32_t sort_rows,
         uint32_t inline_nearest,
         uint64_t row_capacity,
         int64_t* frontier_kind_codes_out,
         int64_t* query_row_ids_out,
         int64_t* query_point_ids_out,
         int64_t* cell_ids_out,
         uint64_t* point_begin_offsets_out,
         uint64_t* point_counts_out,
         double* min_distances_out,
         double* max_distances_out,
         double* nearest_distances_out,
         int64_t* nearest_item_ids_out,
         uint64_t* inline_cell_hit_count_out,
         uint64_t* inline_point_eval_count_out,
         uint32_t global_bound_early_break,
         uint32_t frontier_status_probe_mode,
         uint64_t* global_bound_early_break_count_out,
         double* global_bound_distance_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_collect_active_query_status_stream_3d_v1(
         const double* query_coords,
         const int64_t* query_point_ids,
         size_t query_count,
         const int64_t* cell_ids,
         const uint64_t* point_begin_offsets,
         const uint64_t* point_counts,
         const double* cell_mbr_min,
         const double* cell_mbr_max,
         size_t cell_count,
         double radius,
         const double* current_best_distances,
         const int64_t* current_best_item_ids,
         const double* target_coords,
         const int64_t* target_point_ids,
         size_t target_count,
         const uint64_t* point_row_indices,
         size_t point_row_index_count,
         uint64_t max_inline_points,
         uint32_t emit_pruned_rows,
         uint32_t inline_nearest,
         uint32_t frontier_status_probe_mode,
         uint64_t row_capacity,
         int64_t* active_queue_indices_out,
         int64_t* query_row_ids_out,
         int64_t* source_ids_out,
         int64_t* cell_ids_out,
         int64_t* status_codes_out,
         int64_t* transition_phase_codes_out,
         double* current_best_before_sq_out,
         double* current_best_after_sq_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_active_query_status_state_machine_smoke_v1(
         const int64_t* query_row_ids,
         const int64_t* active_queue_indices,
         const int64_t* source_ids,
         const double* current_best_sq,
         const int64_t* current_best_item_ids,
         size_t active_count,
         const int64_t* candidate_query_row_ids,
         const int64_t* candidate_cell_ids,
         const double* candidate_min_sq,
         const double* candidate_max_sq,
         const uint64_t* candidate_work_counts,
         size_t candidate_count,
         uint64_t heavy_threshold,
         const int64_t* feedback_active_queue_indices,
         const double* feedback_best_sq,
         const int64_t* feedback_item_ids,
         size_t feedback_count,
         uint64_t row_capacity,
         int64_t* active_queue_indices_out,
         int64_t* query_row_ids_out,
         int64_t* source_ids_out,
         int64_t* cell_ids_out,
         int64_t* status_codes_out,
         int64_t* transition_phase_codes_out,
         double* current_best_before_sq_out,
         double* current_best_after_sq_out,
         uint64_t* emitted_count_out,
         uint64_t* attempted_count_out,
         uint64_t* status_count_offloading_out,
         uint64_t* feedback_update_count_out,
         uint32_t* overflowed_out,
         char* error_out, size_t error_size);
int  rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry(
         uint64_t* accel_output_bytes,
         uint64_t* accel_temp_bytes,
         uint64_t* accel_aabb_bytes,
         uint64_t* accel_compacted_output_bytes,
         uint64_t* device_buffer_bytes,
         uint64_t* row_buffer_bytes,
         uint64_t* query_buffer_bytes,
         uint64_t* cell_buffer_bytes,
         uint64_t* target_buffer_bytes,
         uint64_t* nearest_buffer_bytes,
         uint64_t* attempted_count,
         uint64_t* emitted_count,
         uint32_t* mode);
int  rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v2(
         uint64_t* accel_output_bytes,
         uint64_t* accel_temp_bytes,
         uint64_t* accel_aabb_bytes,
         uint64_t* accel_compacted_output_bytes,
         uint64_t* device_buffer_bytes,
         uint64_t* row_buffer_bytes,
         uint64_t* query_buffer_bytes,
         uint64_t* cell_buffer_bytes,
         uint64_t* target_buffer_bytes,
         uint64_t* nearest_buffer_bytes,
         uint64_t* attempted_count,
         uint64_t* emitted_count,
         uint32_t* mode,
         uint64_t* in_queue_capacity,
         uint64_t* miss_queue_capacity,
         uint64_t* heavy_offload_row_capacity,
         uint64_t* heavy_offload_current_rows,
         uint64_t* heavy_offload_peak_rows,
         uint64_t* heavy_offload_queue_current_bytes,
         uint64_t* heavy_offload_queue_peak_bytes);
int  rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3(
         uint64_t* accel_output_bytes,
         uint64_t* accel_temp_bytes,
         uint64_t* accel_aabb_bytes,
         uint64_t* accel_compacted_output_bytes,
         uint64_t* device_buffer_bytes,
         uint64_t* row_buffer_bytes,
         uint64_t* query_buffer_bytes,
         uint64_t* cell_buffer_bytes,
         uint64_t* target_buffer_bytes,
         uint64_t* nearest_buffer_bytes,
         uint64_t* attempted_count,
         uint64_t* emitted_count,
         uint32_t* mode,
         uint64_t* in_queue_capacity,
         uint64_t* miss_queue_capacity,
         uint64_t* heavy_offload_row_capacity,
         uint64_t* heavy_offload_current_rows,
         uint64_t* heavy_offload_peak_rows,
         uint64_t* heavy_offload_queue_current_bytes,
         uint64_t* heavy_offload_queue_peak_bytes,
         uint64_t* raw_frontier_kind1_rows,
         uint64_t* raw_frontier_kind2_rows,
         uint64_t* raw_frontier_kind3_rows);
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
int  rtdl_optix_prepare_fixed_radius_query_points_3d(
         const RtdlPoint3D* query_points, size_t query_count,
         void** prepared_queries_out,
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
int  rtdl_optix_run_prepared_exact_fixed_radius_neighbors_3d_v2(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         uint32_t radius_boundary_mode,
         RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_ranked_distance_window_neighbors_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double minimum_distance,
         double radius,
         size_t k_max,
         uint32_t minimum_boundary_mode,
         uint32_t radius_boundary_mode,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusRankedNeighborSummary** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_aggregate_prepared_ranked_fixed_radius_neighbor_summaries_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusRankedNeighborAggregate* aggregate_out,
         char* error_out, size_t error_size);
int  rtdl_optix_aggregate_prepared_ranked_fixed_radius_neighbor_summaries_3d_f32(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         double radius,
         size_t k_max,
         RtdlFixedRadiusRankedNeighborAggregate* aggregate_out,
         char* error_out, size_t error_size);
int  rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32(
         void* prepared,
         void* prepared_queries,
         double radius,
         size_t k_max,
         RtdlFixedRadiusRankedNeighborAggregate* aggregate_out,
         char* error_out, size_t error_size);
int  rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch(
         void* prepared,
         void* prepared_queries,
         const double* radii,
         const size_t* k_values,
         size_t request_count,
         RtdlFixedRadiusRankedNeighborAggregate* aggregates_out,
         char* error_out, size_t error_size);
int  rtdl_optix_launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d(
         void* graph,
         uint64_t* partials_device_ptr_out,
         size_t* partial_count_out,
         size_t* request_count_out,
         size_t* query_block_count_out,
         uint64_t* cuda_stream_ptr_out,
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
void rtdl_optix_destroy_prepared_fixed_radius_query_points_3d(void* prepared_queries);
int  rtdl_optix_prepare_fixed_radius_count_threshold_3d(
         const RtdlPoint3D* search_points, size_t search_count,
         double max_radius,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_prepare_metric_knn_3d(
         const RtdlPoint3D* search_points, size_t search_count,
         double initial_radius,
         void** prepared_out,
         char* error_out, size_t error_size);
int  rtdl_optix_execute_prepared_metric_knn_3d(
         void* prepared,
         const RtdlPoint3D* query_points, size_t query_count,
         uint32_t metric_kind,
         size_t k,
         double initial_radius,
         size_t maximum_rounds,
         RtdlFixedRadiusNeighborRow** rows_out,
         size_t* row_count_out,
         size_t* completed_round_count_out,
         double* final_radius_out,
         size_t* refit_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_destroy_prepared_metric_knn_3d(void* prepared);
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
int  rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_extended_telemetry_and_execution_options(
         void* prepared,
         double radius,
         const uint32_t* predicate_flags,
         int32_t* parent_out,
         int32_t* fallback_candidate_out,
         uint64_t* telemetry_out,
         size_t telemetry_count,
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
int  rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         uint32_t* query_ids_out,
         uint32_t* neighbor_ids_out,
         double* distances_out,
         char* error_out, size_t error_size);
int  rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double radius,
         RtdlFixedRadiusNeighborRow* row_out,
         char* error_out, size_t error_size);
int  rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d(
         void* prepared,
         const RtdlPoint* query_points, size_t query_count,
         double threshold_radius,
         size_t threshold,
         double witness_radius,
         RtdlFixedRadiusNeighborRow* row_out,
         size_t* active_count_out,
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
int  rtdl_optix_columnar_device_payload_grouped_count_i64_device_columns_with_capacity(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         size_t group_capacity,
         RtdlNativeDeviceGroupedCountI64Columns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_release_device_grouped_count_i64_columns(
         void* owner_handle,
         char* error_out, size_t error_size);
int  rtdl_optix_columnar_device_payload_grouped_count_i64_compact_device_columns_with_capacity(
         const RtdlDevicePayloadField* fields, size_t field_count,
         size_t row_count,
         const RtdlColumnClause* clauses, size_t clause_count,
         const char* group_key_field,
         size_t group_capacity,
         RtdlNativeDeviceGroupedCountI64CompactColumns* columns_out,
         char* error_out, size_t error_size);
int  rtdl_optix_release_device_grouped_count_i64_compact_columns(
         void* owner_handle,
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
int  rtdl_optix_segment_pair_intersection_get_last_extended_phase_timings(
         double* total_native_out,
         double* scaled_cache_ensure_out,
         double* grouped_range_ensure_out,
         double* exact_pipeline_ensure_out,
         double* split_kernel_ensure_out,
         double* device_alloc_out,
         double* param_upload_out,
         double* optix_launch_out,
         double* count_download_out,
         double* split_kernel_launch_out,
         size_t* raw_candidate_count_out,
         size_t* emitted_count_out,
         uint32_t* mode_out);
int  rtdl_optix_rayjoin_cdb_point_location_get_last_phase_timings(
         double* point_upload_out,
         double* traversal_out,
         double* row_download_out,
         size_t* point_count_out,
         size_t* positive_face_count_out,
         uint32_t* mode_out);
int  rtdl_optix_directed_segment_point_location_get_last_phase_timings(
         double* point_upload_out,
         double* traversal_out,
         double* row_download_out,
         size_t* point_count_out,
         size_t* positive_face_count_out,
         uint32_t* mode_out);
int  rtdl_optix_rayjoin_cdb_point_location_get_last_extended_phase_timings(
         double* prepare_total_out,
         double* prepare_pipeline_ensure_out,
         double* prepare_host_copy_out,
         double* prepare_segment_pack_out,
         double* prepare_duplicate_canonicalize_out,
         double* prepare_device_upload_out,
         double* prepare_range_build_out,
         double* prepare_range_upload_out,
         double* prepare_accel_build_out,
         size_t* prepare_segment_count_out,
         size_t* prepare_range_count_out,
         uint32_t* mode_out);
int  rtdl_optix_directed_segment_point_location_get_last_extended_phase_timings(
         double* prepare_total_out,
         double* prepare_pipeline_ensure_out,
         double* prepare_host_copy_out,
         double* prepare_segment_pack_out,
         double* prepare_duplicate_canonicalize_out,
         double* prepare_device_upload_out,
         double* prepare_range_build_out,
         double* prepare_range_upload_out,
         double* prepare_accel_build_out,
         size_t* prepare_segment_count_out,
         size_t* prepare_range_count_out,
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

// Generic precompiled CUDA aggregate-hierarchy continuation lowering.
// Compiler-owned reducer codes: 0=aggregate_count,
// 1=inverse_square_scalar_sum.  No application identity enters this ABI.
int rtdl_cuda_prepare_aggregate_hierarchy_continuation_3d(
        const double* point_x,
        const double* point_y,
        const double* point_z,
        const double* point_weight,
        uint64_t point_count,
        const double* node_cx,
        const double* node_cy,
        const double* node_cz,
        const double* node_half_size,
        const double* node_weight,
        uint64_t node_count,
        const int64_t* member_offsets,
        const int64_t* member_indices,
        uint64_t member_count,
        const int64_t* child_offsets,
        const int64_t* child_indices,
        uint64_t child_count,
        const int64_t* node_next_index,
        const int64_t* node_rope_index,
        int64_t root_node_index,
        void** prepared_out,
        double* prepare_total_seconds_out,
        char* error_out,
        uint64_t error_capacity);
int rtdl_cuda_execute_prepared_aggregate_hierarchy_continuation_3d(
        void* prepared_handle,
        uint32_t reducer_kind,
        double max_ratio,
        double softening,
        uint64_t output_capacity,
        double* reducer_value_0_out,
        int64_t* visited_node_count_out,
        int64_t* aggregate_contribution_count_out,
        int64_t* exact_contribution_count_out,
        int64_t* status_code_out,
        double* kernel_seconds_out,
        double* download_seconds_out,
        double* total_seconds_out,
        char* error_out,
        uint64_t error_capacity);
int rtdl_cuda_close_prepared_aggregate_hierarchy_continuation_3d(
        void* prepared_handle,
        char* error_out,
        uint64_t error_capacity);

// Generic true-OptiX aggregate-hierarchy continuation candidate.  The ABI is
// deliberately isomorphic to the precompiled-CUDA candidate so the compiler
// can compare physical candidates for one verified generic specification.
int rtdl_optix_prepare_aggregate_hierarchy_continuation_3d(
        const double* point_x,
        const double* point_y,
        const double* point_z,
        const double* point_weight,
        uint64_t point_count,
        const double* node_cx,
        const double* node_cy,
        const double* node_cz,
        const double* node_half_size,
        const double* node_weight,
        uint64_t node_count,
        const int64_t* member_offsets,
        const int64_t* member_indices,
        uint64_t member_count,
        const int64_t* child_offsets,
        const int64_t* child_indices,
        uint64_t child_count,
        const int64_t* node_next_index,
        const int64_t* node_rope_index,
        int64_t root_node_index,
        void** prepared_out,
        double* prepare_total_seconds_out,
        char* error_out,
        uint64_t error_capacity);
int rtdl_optix_execute_prepared_aggregate_hierarchy_continuation_3d(
        void* prepared_handle,
        uint32_t reducer_kind,
        double max_ratio,
        double softening,
        uint64_t output_capacity,
        double* reducer_value_0_out,
        int64_t* visited_node_count_out,
        int64_t* aggregate_contribution_count_out,
        int64_t* exact_contribution_count_out,
        int64_t* status_code_out,
        double* traversal_seconds_out,
        double* download_seconds_out,
        double* total_seconds_out,
        char* error_out,
        uint64_t error_capacity);
int rtdl_optix_close_prepared_aggregate_hierarchy_continuation_3d(
        void* prepared_handle,
        char* error_out,
        uint64_t error_capacity);
void rtdl_optix_free_rows(void* rows);

} // extern "C"
