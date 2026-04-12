#pragma once

// rtdl_optix.cpp — NVIDIA OptiX 7 backend for rtdl
//
// Implements all current OptiX-native workloads (LSI, PIP, Overlay,
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
//   - CUDA Toolkit ≥ 11.0  (nvrtc.h, cuda.h, cuda_runtime.h)
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
#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <filesystem>
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

// ──────────────────────────────────────────────────────────────────────────────
// Public C ABI (mirrors rtdl_embree.cpp)
// ──────────────────────────────────────────────────────────────────────────────

extern "C" {

struct RtdlSegment {
    uint32_t id;
    double x0, y0, x1, y1;
};

struct RtdlPoint {
    uint32_t id;
    double x, y;
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
#pragma pack(pop)

struct RtdlLsiRow {
    uint32_t left_id, right_id;
    double intersection_point_x, intersection_point_y;
};

struct RtdlPipRow {
    uint32_t point_id, polygon_id, contains;
};

struct RtdlOverlayRow {
    uint32_t left_polygon_id, right_polygon_id;
    uint32_t requires_lsi, requires_pip;
};

struct RtdlRayHitCountRow {
    uint32_t ray_id, hit_count;
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

struct RtdlKnnNeighborRow {
    uint32_t query_id, neighbor_id;
    double distance;
    uint32_t neighbor_rank;
};

struct RtdlPointNearestSegmentRow {
    uint32_t point_id, segment_id;
    double distance;
};

int  rtdl_optix_get_version(int* major_out, int* minor_out, int* patch_out);
int  rtdl_optix_run_lsi(
         const RtdlSegment* left,  size_t left_count,
         const RtdlSegment* right, size_t right_count,
         RtdlLsiRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_pip(
         const RtdlPoint* points,     size_t point_count,
         const RtdlPolygonRef* polys, size_t poly_count,
         const double* vertices_xy,   size_t vertex_xy_count,
         uint32_t positive_only,
         RtdlPipRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_overlay(
         const RtdlPolygonRef* left_polys,  size_t left_count,
         const double* left_verts_xy,       size_t left_vert_xy_count,
         const RtdlPolygonRef* right_polys, size_t right_count,
         const double* right_verts_xy,      size_t right_vert_xy_count,
         RtdlOverlayRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
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
int  rtdl_optix_run_segment_polygon_hitcount(
         const RtdlSegment*   segments,  size_t segment_count,
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_segment_polygon_anyhit_rows(
         const RtdlSegment*   segments,  size_t segment_count,
         const RtdlPolygonRef* polygons, size_t polygon_count,
         const double* vertices_xy,      size_t vertex_xy_count,
         RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
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
int  rtdl_optix_run_knn_rows(
         const RtdlPoint* query_points, size_t query_count,
         const RtdlPoint* search_points, size_t search_count,
         size_t k,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
int  rtdl_optix_run_knn_rows_3d(
         const RtdlPoint3D* query_points, size_t query_count,
         const RtdlPoint3D* search_points, size_t search_count,
         size_t k,
         RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
         char* error_out, size_t error_size);
void rtdl_optix_free_rows(void* rows);

} // extern "C"
