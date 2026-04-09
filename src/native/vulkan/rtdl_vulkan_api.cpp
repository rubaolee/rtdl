// C ABI implementations
// ─────────────────────────────────────────────────────────────────────────────

extern "C" {

int rtdl_vulkan_get_version(int* major_out, int* minor_out, int* patch_out) {
    if (major_out) *major_out = 0;
    if (minor_out) *minor_out = 1;
    if (patch_out) *patch_out = 0;
    return 0;
}

void rtdl_vulkan_free_rows(void* rows) { std::free(rows); }

int rtdl_vulkan_run_lsi(
        const RtdlSegment* left, size_t left_count,
        const RtdlSegment* right, size_t right_count,
        RtdlLsiRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_lsi_vulkan(left, left_count, right, right_count, rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_pip(
        const RtdlPoint* points, size_t point_count,
        const RtdlPolygonRef* polys, size_t poly_count,
        const double* vertices_xy, size_t vertex_xy_count,
        uint32_t positive_only,
        RtdlPipRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_pip_vulkan(points, point_count, polys, poly_count,
                       vertices_xy, vertex_xy_count, positive_only, rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_overlay(
        const RtdlPolygonRef* left_polys, size_t left_count,
        const double* left_verts_xy, size_t left_vert_xy_count,
        const RtdlPolygonRef* right_polys, size_t right_count,
        const double* right_verts_xy, size_t right_vert_xy_count,
        RtdlOverlayRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_overlay_vulkan(left_polys, left_count, left_verts_xy, left_vert_xy_count,
                           right_polys, right_count, right_verts_xy, right_vert_xy_count,
                           rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_ray_hitcount(
        const RtdlRay2D* rays, size_t ray_count,
        const RtdlTriangle* triangles, size_t triangle_count,
        RtdlRayHitCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_ray_hitcount_vulkan(rays, ray_count, triangles, triangle_count,
                                rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_ray_hitcount_3d(
        const RtdlRay3D* rays, size_t ray_count,
        const RtdlTriangle3D* triangles, size_t triangle_count,
        RtdlRayHitCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_ray_hitcount_3d_vulkan(rays, ray_count, triangles, triangle_count,
                                   rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_segment_polygon_hitcount(
        const RtdlSegment* segments, size_t segment_count,
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy, size_t vertex_xy_count,
        RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_segment_polygon_hitcount_vulkan(segments, segment_count,
                                            polygons, polygon_count,
                                            vertices_xy, vertex_xy_count,
                                            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_segment_polygon_anyhit_rows(
        const RtdlSegment* segments, size_t segment_count,
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy, size_t vertex_xy_count,
        RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_segment_polygon_anyhit_rows_vulkan(segments, segment_count,
                                               polygons, polygon_count,
                                               vertices_xy, vertex_xy_count,
                                               rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_point_nearest_segment(
        const RtdlPoint* points, size_t point_count,
        const RtdlSegment* segments, size_t segment_count,
        RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_point_nearest_segment_vulkan(points, point_count, segments, segment_count,
                                         rows_out, row_count_out);
    }, error_out, error_size);
}

} // extern "C"
