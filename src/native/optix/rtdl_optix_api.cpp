extern "C" int rtdl_optix_get_version(int* major_out, int* minor_out, int* patch_out) {
    if (!major_out || !minor_out || !patch_out) return 1;
    *major_out = OPTIX_VERSION / 10000;
    *minor_out = (OPTIX_VERSION % 10000) / 100;
    *patch_out = OPTIX_VERSION % 100;
    return 0;
}

extern "C" int rtdl_optix_run_lsi(
        const RtdlSegment* left,  size_t left_count,
        const RtdlSegment* right, size_t right_count,
        RtdlLsiRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (left_count == 0 || right_count == 0) return;
        run_lsi_optix(left, left_count, right, right_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_pip(
        const RtdlPoint* points,     size_t point_count,
        const RtdlPolygonRef* polys, size_t poly_count,
        const double* vertices_xy,   size_t vertex_xy_count,
        uint32_t positive_only,
        RtdlPipRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (point_count == 0 || poly_count == 0) return;
        run_pip_optix(points, point_count, polys, poly_count,
                      vertices_xy, vertex_xy_count, positive_only, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_overlay(
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        const RtdlPolygonRef* right_polys, size_t right_count,
        const double* right_verts_xy,      size_t right_vert_xy_count,
        RtdlOverlayRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (left_count == 0 || right_count == 0) return;
        run_overlay_optix(left_polys, left_count, left_verts_xy, left_vert_xy_count,
                          right_polys, right_count, right_verts_xy, right_vert_xy_count,
                          rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_ray_hitcount(
        const RtdlRay2D*    rays,      size_t ray_count,
        const RtdlTriangle* triangles, size_t triangle_count,
        RtdlRayHitCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (ray_count == 0) return;
        run_ray_hitcount_optix(rays, ray_count, triangles, triangle_count,
                               rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_ray_hitcount_3d(
        const RtdlRay3D*      rays,      size_t ray_count,
        const RtdlTriangle3D* triangles, size_t triangle_count,
        RtdlRayHitCountRow**  rows_out,  size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (ray_count == 0) return;
        run_ray_hitcount_3d_optix(rays, ray_count, triangles, triangle_count,
                                   rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_ray_anyhit(
        const RtdlRay2D*    rays,      size_t ray_count,
        const RtdlTriangle* triangles, size_t triangle_count,
        RtdlRayAnyHitRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (ray_count == 0) return;
        run_ray_anyhit_optix(rays, ray_count, triangles, triangle_count,
                             rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_ray_anyhit_3d(
        const RtdlRay3D*      rays,      size_t ray_count,
        const RtdlTriangle3D* triangles, size_t triangle_count,
        RtdlRayAnyHitRow**  rows_out,  size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (ray_count == 0) return;
        run_ray_anyhit_3d_optix(rays, ray_count, triangles, triangle_count,
                                rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_ray_anyhit_2d(
        const RtdlTriangle* triangles, size_t triangle_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!triangles && triangle_count != 0)
            throw std::runtime_error("triangles pointer must not be null when triangle_count is nonzero");
        *prepared_out = nullptr;
        *prepared_out = prepare_ray_anyhit_2d_optix(triangles, triangle_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_ray_anyhit_2d(
        void* prepared,
        const RtdlRay2D* rays, size_t ray_count,
        size_t* hit_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rays && ray_count != 0)
            throw std::runtime_error("rays pointer must not be null when ray_count is nonzero");
        if (!hit_count_out)
            throw std::runtime_error("hit_count_out must not be null");
        count_prepared_ray_anyhit_2d_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            rays, ray_count, hit_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_ray_anyhit_2d(void* prepared)
{
    delete reinterpret_cast<PreparedRayAnyHit2D*>(prepared);
}

extern "C" int rtdl_optix_prepare_rays_2d(
        const RtdlRay2D* rays, size_t ray_count,
        void** rays_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rays_out)
            throw std::runtime_error("rays_out must not be null");
        if (!rays && ray_count != 0)
            throw std::runtime_error("rays pointer must not be null when ray_count is nonzero");
        *rays_out = nullptr;
        *rays_out = prepare_rays_2d_optix(rays, ray_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_ray_anyhit_2d_packed(
        void* prepared,
        void* prepared_rays,
        size_t* hit_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_rays)
            throw std::runtime_error("prepared_rays must not be null");
        if (!hit_count_out)
            throw std::runtime_error("hit_count_out must not be null");
        count_prepared_ray_anyhit_2d_packed_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            reinterpret_cast<PreparedRays2D*>(prepared_rays),
            hit_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed(
        void* prepared,
        void* prepared_rays,
        const uint32_t* pose_indices,
        size_t pose_index_count,
        uint32_t* pose_flags_out,
        size_t pose_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_rays)
            throw std::runtime_error("prepared_rays must not be null");
        pose_flags_prepared_ray_anyhit_2d_packed_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            reinterpret_cast<PreparedRays2D*>(prepared_rays),
            pose_indices,
            pose_index_count,
            pose_flags_out,
            pose_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_pose_indices_2d(
        const uint32_t* pose_indices,
        size_t pose_index_count,
        void** pose_indices_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!pose_indices_out)
            throw std::runtime_error("pose_indices_out must not be null");
        if (!pose_indices && pose_index_count != 0)
            throw std::runtime_error("pose_indices pointer must not be null when pose_index_count is nonzero");
        *pose_indices_out = nullptr;
        *pose_indices_out = prepare_pose_indices_2d_optix(pose_indices, pose_index_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_pose_flags_prepared_ray_anyhit_2d_prepared_indices(
        void* prepared,
        void* prepared_rays,
        void* prepared_pose_indices,
        uint32_t* pose_flags_out,
        size_t pose_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_rays)
            throw std::runtime_error("prepared_rays must not be null");
        if (!prepared_pose_indices)
            throw std::runtime_error("prepared_pose_indices must not be null");
        pose_flags_prepared_ray_anyhit_2d_prepared_indices_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            reinterpret_cast<PreparedRays2D*>(prepared_rays),
            reinterpret_cast<PreparedPoseIndices2D*>(prepared_pose_indices),
            pose_flags_out,
            pose_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_poses_prepared_ray_anyhit_2d_prepared_indices(
        void* prepared,
        void* prepared_rays,
        void* prepared_pose_indices,
        size_t pose_count,
        size_t* colliding_pose_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_rays)
            throw std::runtime_error("prepared_rays must not be null");
        if (!prepared_pose_indices)
            throw std::runtime_error("prepared_pose_indices must not be null");
        if (!colliding_pose_count_out)
            throw std::runtime_error("colliding_pose_count_out must not be null");
        count_poses_prepared_ray_anyhit_2d_prepared_indices_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            reinterpret_cast<PreparedRays2D*>(prepared_rays),
            reinterpret_cast<PreparedPoseIndices2D*>(prepared_pose_indices),
            pose_count,
            colliding_pose_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_pose_indices_2d(void* prepared_pose_indices)
{
    delete reinterpret_cast<PreparedPoseIndices2D*>(prepared_pose_indices);
}

extern "C" void rtdl_optix_destroy_prepared_rays_2d(void* prepared_rays)
{
    delete reinterpret_cast<PreparedRays2D*>(prepared_rays);
}

extern "C" int rtdl_optix_run_segment_polygon_hitcount(
        const RtdlSegment*    segments,  size_t segment_count,
        const RtdlPolygonRef* polygons,  size_t polygon_count,
        const double* vertices_xy,       size_t vertex_xy_count,
        RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (segment_count == 0) return;
        run_seg_poly_hitcount_optix(segments, segment_count,
                                    polygons, polygon_count,
                                    vertices_xy, vertex_xy_count,
                                    rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_segment_polygon_anyhit_rows(
        const RtdlSegment* segments, size_t segment_count,
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy, size_t vertex_xy_count,
        RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (segment_count == 0 || polygon_count == 0) return;
        (void)vertex_xy_count;
        run_seg_poly_anyhit_rows_optix_host_indexed(
            segments, segment_count, polygons, polygon_count, vertices_xy, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_point_nearest_segment(
        const RtdlPoint*   points,   size_t point_count,
        const RtdlSegment* segments, size_t segment_count,
        RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (point_count == 0) return;
        run_point_nearest_segment_cuda(points, point_count,
                                       segments, segment_count,
                                       rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_fixed_radius_neighbors(
        const RtdlPoint* query_points, size_t query_count,
        const RtdlPoint* search_points, size_t search_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        if (radius < 0.0)
            throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
        if (k_max == 0)
            throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
        if (query_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_neighbors query_count exceeds uint32 limit");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_neighbors search_count exceeds uint32 limit");
        if (k_max > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_neighbors k_max exceeds uint32 limit");
        *rows_out = nullptr; *row_count_out = 0;
        if (query_count == 0 || search_count == 0) return;
        run_fixed_radius_neighbors_cuda(
            query_points, query_count,
            search_points, search_count,
            radius, k_max,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_fixed_radius_neighbors_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        const RtdlPoint3D* search_points, size_t search_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        if (radius < 0.0)
            throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
        if (k_max == 0)
            throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
        if (query_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_neighbors query_count exceeds uint32 limit");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_neighbors search_count exceeds uint32 limit");
        if (k_max > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_neighbors k_max exceeds uint32 limit");
        *rows_out = nullptr; *row_count_out = 0;
        if (query_count == 0 || search_count == 0) return;
        run_fixed_radius_neighbors_cuda_3d(
            query_points, query_count,
            search_points, search_count,
            radius, k_max,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_fixed_radius_count_threshold(
        const RtdlPoint* query_points, size_t query_count,
        const RtdlPoint* search_points, size_t search_count,
        double radius,
        size_t threshold,
        RtdlFixedRadiusCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        if (radius < 0.0)
            throw std::runtime_error("fixed_radius_count_threshold radius must be non-negative");
        if (query_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_count_threshold query_count exceeds uint32 limit");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_count_threshold search_count exceeds uint32 limit");
        if (threshold > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_count_threshold threshold exceeds uint32 limit");
        *rows_out = nullptr; *row_count_out = 0;
        if (query_count == 0 || search_count == 0) return;
        run_fixed_radius_count_threshold_rt(
            query_points, query_count,
            search_points, search_count,
            radius, threshold,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_fixed_radius_count_threshold_2d(
        const RtdlPoint* search_points, size_t search_count,
        double max_radius,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!search_points && search_count != 0)
            throw std::runtime_error("search_points pointer must not be null when search_count is nonzero");
        if (max_radius < 0.0)
            throw std::runtime_error("fixed_radius_count_threshold max_radius must be non-negative");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_count_threshold search_count exceeds uint32 limit");
        *prepared_out = nullptr;
        *prepared_out = prepare_fixed_radius_count_threshold_2d_optix(
            search_points, search_count, max_radius);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_fixed_radius_count_threshold_2d(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double radius,
        size_t threshold,
        RtdlFixedRadiusCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_fixed_radius_count_threshold_2d_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold2D*>(prepared),
            query_points, query_count, radius, threshold, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double radius,
        size_t threshold,
        size_t* threshold_reached_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        count_prepared_fixed_radius_threshold_reached_2d_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold2D*>(prepared),
            query_points, query_count, radius, threshold, threshold_reached_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d(void* prepared)
{
    delete reinterpret_cast<PreparedFixedRadiusCountThreshold2D*>(prepared);
}

extern "C" int rtdl_optix_run_knn_rows(
        const RtdlPoint* query_points, size_t query_count,
        const RtdlPoint* search_points, size_t search_count,
        size_t k,
        RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        if (k == 0)
            throw std::runtime_error("knn_rows k must be positive");
        if (query_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("knn_rows query_count exceeds uint32 limit");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("knn_rows search_count exceeds uint32 limit");
        if (k > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("knn_rows k exceeds uint32 limit");
        *rows_out = nullptr; *row_count_out = 0;
        if (query_count == 0 || search_count == 0) return;
        run_knn_rows_cuda(
            query_points, query_count,
            search_points, search_count,
            k,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_knn_rows_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        const RtdlPoint3D* search_points, size_t search_count,
        size_t k,
        RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        if (k == 0)
            throw std::runtime_error("knn_rows k must be positive");
        if (query_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("knn_rows query_count exceeds uint32 limit");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("knn_rows search_count exceeds uint32 limit");
        if (k > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("knn_rows k exceeds uint32 limit");
        *rows_out = nullptr; *row_count_out = 0;
        if (query_count == 0 || search_count == 0) return;
        run_knn_rows_cuda_3d(
            query_points, query_count,
            search_points, search_count,
            k,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_bfs_expand(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t column_index_count,
        const RtdlFrontierVertex* frontier, size_t frontier_count,
        const uint32_t* visited_vertices, size_t visited_count,
        uint32_t dedupe,
        RtdlBfsExpandRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (frontier_count == 0) return;
        run_bfs_expand_optix_host_indexed(
            row_offsets, row_offset_count,
            column_indices, column_index_count,
            frontier, frontier_count,
            visited_vertices, visited_count,
            dedupe,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_triangle_probe(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t column_index_count,
        const RtdlEdgeSeed* seeds, size_t seed_count,
        uint32_t enforce_id_ascending,
        uint32_t unique,
        RtdlTriangleRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (seed_count == 0) return;
        run_triangle_probe_optix_host_indexed(
            row_offsets, row_offset_count,
            column_indices, column_index_count,
            seeds, seed_count,
            enforce_id_ascending,
            unique,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_conjunctive_scan(
        const RtdlDbField* fields, size_t field_count,
        const RtdlDbScalar* row_values, size_t row_count,
        const RtdlDbClause* clauses, size_t clause_count,
        RtdlDbRowIdRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_conjunctive_scan_optix(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_grouped_count(
        const RtdlDbField* fields, size_t field_count,
        const RtdlDbScalar* row_values, size_t row_count,
        const RtdlDbClause* clauses, size_t clause_count,
        const char* group_key_field,
        RtdlDbGroupedCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_grouped_count_optix(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            group_key_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_grouped_sum(
        const RtdlDbField* fields, size_t field_count,
        const RtdlDbScalar* row_values, size_t row_count,
        const RtdlDbClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlDbGroupedSumRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_grouped_sum_optix(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            group_key_field,
            value_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_db_dataset_create(
        const RtdlDbField* fields, size_t field_count,
        const RtdlDbScalar* row_values, size_t row_count,
        const char* const* primary_fields, size_t primary_field_count,
        RtdlOptixDbDataset** dataset_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!dataset_out) {
            throw std::runtime_error("dataset output pointer must not be null");
        }
        *dataset_out = nullptr;
        auto* dataset = create_db_dataset_optix(
            fields, field_count,
            row_values, row_count,
            primary_fields, primary_field_count);
        *dataset_out = reinterpret_cast<RtdlOptixDbDataset*>(dataset);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_db_dataset_create_columnar(
        const RtdlDbColumn* columns, size_t column_count,
        size_t row_count,
        const char* const* primary_fields, size_t primary_field_count,
        RtdlOptixDbDataset** dataset_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!dataset_out) {
            throw std::runtime_error("dataset output pointer must not be null");
        }
        *dataset_out = nullptr;
        auto* dataset = create_db_dataset_optix_columnar(
            columns, column_count,
            row_count,
            primary_fields, primary_field_count);
        *dataset_out = reinterpret_cast<RtdlOptixDbDataset*>(dataset);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_db_dataset_destroy(RtdlOptixDbDataset* dataset)
{
    delete reinterpret_cast<OptixDbDatasetImpl*>(dataset);
}

extern "C" int rtdl_optix_db_dataset_conjunctive_scan(
        RtdlOptixDbDataset* dataset,
        const RtdlDbClause* clauses, size_t clause_count,
        RtdlDbRowIdRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_conjunctive_scan_optix_prepared(
            reinterpret_cast<OptixDbDatasetImpl*>(dataset),
            clauses, clause_count,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_db_dataset_conjunctive_scan_count(
        RtdlOptixDbDataset* dataset,
        const RtdlDbClause* clauses, size_t clause_count,
        size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!row_count_out) {
            throw std::runtime_error("row_count_out pointer must not be null");
        }
        *row_count_out = 0;
        run_db_conjunctive_scan_count_optix_prepared(
            reinterpret_cast<OptixDbDatasetImpl*>(dataset),
            clauses, clause_count,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_db_dataset_grouped_count(
        RtdlOptixDbDataset* dataset,
        const RtdlDbClause* clauses, size_t clause_count,
        const char* group_key_field,
        RtdlDbGroupedCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_grouped_count_optix_prepared(
            reinterpret_cast<OptixDbDatasetImpl*>(dataset),
            clauses, clause_count,
            group_key_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_db_dataset_grouped_sum(
        RtdlOptixDbDataset* dataset,
        const RtdlDbClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlDbGroupedSumRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_grouped_sum_optix_prepared(
            reinterpret_cast<OptixDbDatasetImpl*>(dataset),
            clauses, clause_count,
            group_key_field,
            value_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_free_rows(void* rows) {
    std::free(rows);
}
