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

extern "C" int rtdl_optix_prepare_segment_polygon_hitcount_2d(
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy, size_t vertex_xy_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!polygons && polygon_count != 0)
            throw std::runtime_error("polygons pointer must not be null when polygon_count is nonzero");
        if (!vertices_xy && vertex_xy_count != 0)
            throw std::runtime_error("vertices_xy pointer must not be null when vertex_xy_count is nonzero");
        if (polygon_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("polygon count exceeds uint32 primitive limit");
        *prepared_out = nullptr;
        *prepared_out = prepare_segment_polygon_hitcount_2d_optix(
            polygons, polygon_count, vertices_xy, vertex_xy_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_segment_polygon_hitcount_2d(
        void* prepared,
        const RtdlSegment* segments, size_t segment_count,
        RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_segment_polygon_hitcount_2d_optix(
            reinterpret_cast<PreparedSegmentPolygonHitcount2D*>(prepared),
            segments, segment_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d(
        void* prepared,
        const RtdlSegment* segments, size_t segment_count,
        uint32_t threshold,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        count_prepared_segment_polygon_hitcount_at_least_2d_optix(
            reinterpret_cast<PreparedSegmentPolygonHitcount2D*>(prepared),
            segments, segment_count, threshold, count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d(
        void* prepared,
        const RtdlSegment* segments, size_t segment_count,
        uint32_t positive_threshold,
        size_t* row_count_out,
        uint64_t* hit_sum_out,
        size_t* positive_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        aggregate_prepared_segment_polygon_hitcount_2d_optix(
            reinterpret_cast<PreparedSegmentPolygonHitcount2D*>(prepared),
            segments, segment_count, positive_threshold,
            row_count_out, hit_sum_out, positive_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_segment_polygon_hitcount_2d(void* prepared)
{
    delete reinterpret_cast<PreparedSegmentPolygonHitcount2D*>(prepared);
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

extern "C" int rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded(
        const RtdlSegment* segments, size_t segment_count,
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy, size_t vertex_xy_count,
        RtdlSegmentPolygonAnyHitRow* rows_out, size_t output_capacity,
        size_t* emitted_count_out, uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!emitted_count_out || !overflowed_out)
            throw std::runtime_error("emitted_count_out and overflowed_out must not be null");
        *emitted_count_out = 0;
        *overflowed_out = 0;
        if (!rows_out && output_capacity != 0)
            throw std::runtime_error("rows_out must not be null when output_capacity is nonzero");
        if (!segments && segment_count != 0)
            throw std::runtime_error("segments pointer must not be null when segment_count is nonzero");
        if (!polygons && polygon_count != 0)
            throw std::runtime_error("polygons pointer must not be null when polygon_count is nonzero");
        if (!vertices_xy && vertex_xy_count != 0)
            throw std::runtime_error("vertices_xy pointer must not be null when vertex_xy_count is nonzero");
        run_seg_poly_anyhit_rows_optix_native_bounded(
            segments, segment_count,
            polygons, polygon_count,
            vertices_xy, vertex_xy_count,
            rows_out, output_capacity,
            emitted_count_out, overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_polygon_pair_candidates_bounded(
        const RtdlPolygonRef* left_polygons, size_t left_count,
        const double* left_vertices_xy, size_t left_vertex_xy_count,
        const RtdlPolygonRef* right_polygons, size_t right_count,
        const double* right_vertices_xy, size_t right_vertex_xy_count,
        RtdlPolygonPairCandidate* candidates_out, size_t candidate_capacity,
        size_t* emitted_count_out, uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!emitted_count_out || !overflowed_out)
            throw std::runtime_error("emitted_count_out and overflowed_out must not be null");
        *emitted_count_out = 0;
        *overflowed_out = 0;
        if (!candidates_out && candidate_capacity != 0)
            throw std::runtime_error("candidates_out must not be null when candidate_capacity is nonzero");
        collect_polygon_pair_candidates_bounded_optix(
            left_polygons, left_count,
            left_vertices_xy, left_vertex_xy_count,
            right_polygons, right_count,
            right_vertices_xy, right_vertex_xy_count,
            candidates_out, candidate_capacity,
            emitted_count_out, overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_k_bounded_i64(
        const int64_t* candidate_rows, size_t candidate_count,
        size_t row_width, int64_t* rows_out, size_t row_capacity,
        size_t* emitted_count_out, uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!emitted_count_out || !overflowed_out)
            throw std::runtime_error("emitted_count_out and overflowed_out must not be null");
        *emitted_count_out = 0;
        *overflowed_out = 0;
        if (row_width == 0)
            throw std::runtime_error("row_width must be positive");
        if (!candidate_rows && candidate_count != 0)
            throw std::runtime_error("candidate_rows must not be null when candidate_count is nonzero");
        if (!rows_out && row_capacity != 0)
            throw std::runtime_error("rows_out must not be null when row_capacity is nonzero");
        if (candidate_count > std::numeric_limits<size_t>::max() / row_width ||
            row_capacity > std::numeric_limits<size_t>::max() / row_width)
            throw std::runtime_error("COLLECT_K_BOUNDED row buffer size overflow");

        std::vector<std::vector<int64_t>> rows;
        rows.reserve(candidate_count);
        for (size_t row_index = 0; row_index < candidate_count; ++row_index) {
            const int64_t* row = candidate_rows + row_index * row_width;
            rows.emplace_back(row, row + row_width);
        }
        std::sort(rows.begin(), rows.end());
        rows.erase(std::unique(rows.begin(), rows.end()), rows.end());

        *emitted_count_out = rows.size();
        if (rows.size() > row_capacity) {
            *overflowed_out = 1u;
            return;
        }
        for (size_t row_index = 0; row_index < rows.size(); ++row_index) {
            std::memcpy(
                rows_out + row_index * row_width,
                rows[row_index].data(),
                sizeof(int64_t) * row_width);
        }
    }, error_out, error_size);
}

struct CollectKStageProfile {
    using Clock = std::chrono::steady_clock;

    struct MergeLevel {
        size_t input_segments = 0;
        size_t pair_count = 0;
        size_t output_segments = 0;
        size_t output_capacity = 0;
        uint64_t carry_copies = 0;
        uint64_t carry_payload_copies = 0;
        double launch_ms = 0.0;
        double sync_ms = 0.0;
        double metadata_ms = 0.0;
        double carry_copy_ms = 0.0;
    };

    bool enabled = false;
    std::string path;
    std::string native_path = "unknown";
    size_t candidate_count = 0;
    size_t row_width = 0;
    size_t row_capacity = 0;
    size_t tile_count = 0;
    size_t merge_levels = 0;
    uint64_t sort_launches = 0;
    uint64_t merge_launches = 0;
    uint64_t carry_copies = 0;
    uint64_t carry_payload_copies = 0;
    uint64_t final_copies = 0;
    uint64_t metadata_fields_downloaded = 0;
    double module_load_ms = 0.0;
    double allocation_ms = 0.0;
    double sort_launch_ms = 0.0;
    double sort_sync_ms = 0.0;
    double tile_metadata_download_ms = 0.0;
    double merge_launch_ms = 0.0;
    double merge_sync_ms = 0.0;
    double merge_metadata_download_ms = 0.0;
    double carry_copy_ms = 0.0;
    double final_copy_ms = 0.0;
    std::vector<MergeLevel> merge_level_profile;
    Clock::time_point total_start = Clock::now();

    CollectKStageProfile(size_t candidates, size_t width, size_t capacity)
        : candidate_count(candidates), row_width(width), row_capacity(capacity) {
        const char* raw_path = std::getenv("RTDL_OPTIX_COLLECT_K_PROFILE_JSONL");
        if (raw_path && raw_path[0] != '\0') {
            enabled = true;
            path = raw_path;
            total_start = Clock::now();
        }
    }

    static double elapsed_ms(Clock::time_point start) {
        return std::chrono::duration<double, std::milli>(Clock::now() - start).count();
    }

    void add_since(double& bucket, Clock::time_point start) {
        if (enabled)
            bucket += elapsed_ms(start);
    }

    void record_merge_level(const MergeLevel& level) {
        if (enabled)
            merge_level_profile.push_back(level);
    }

    void append(size_t emitted_count, uint32_t overflowed,
                uint64_t h2d_transfers, uint64_t d2h_transfers,
                uint64_t internal_device_transfers) const {
        if (!enabled)
            return;
        try {
            std::ofstream out(path, std::ios::app);
            if (!out)
                return;
            out << "{"
                << "\"event\":\"collect_k_bounded_i64_device_stage_profile\","
                << "\"candidate_count\":" << candidate_count << ","
                << "\"row_width\":" << row_width << ","
                << "\"row_capacity\":" << row_capacity << ","
                << "\"native_path\":\"" << native_path << "\","
                << "\"tile_count\":" << tile_count << ","
                << "\"merge_levels\":" << merge_levels << ","
                << "\"sort_launches\":" << sort_launches << ","
                << "\"merge_launches\":" << merge_launches << ","
                << "\"carry_copies\":" << carry_copies << ","
                << "\"carry_payload_copies\":" << carry_payload_copies << ","
                << "\"final_copies\":" << final_copies << ","
                << "\"metadata_fields_downloaded\":" << metadata_fields_downloaded << ","
                << "\"emitted_count\":" << emitted_count << ","
                << "\"overflowed\":" << static_cast<unsigned>(overflowed) << ","
                << "\"h2d_transfers\":" << h2d_transfers << ","
                << "\"d2h_transfers\":" << d2h_transfers << ","
                << "\"internal_device_transfers\":" << internal_device_transfers << ","
                << "\"module_load_ms\":" << module_load_ms << ","
                << "\"allocation_ms\":" << allocation_ms << ","
                << "\"sort_launch_ms\":" << sort_launch_ms << ","
                << "\"sort_sync_ms\":" << sort_sync_ms << ","
                << "\"tile_metadata_download_ms\":" << tile_metadata_download_ms << ","
                << "\"merge_launch_ms\":" << merge_launch_ms << ","
                << "\"merge_sync_ms\":" << merge_sync_ms << ","
                << "\"merge_metadata_download_ms\":" << merge_metadata_download_ms << ","
                << "\"carry_copy_ms\":" << carry_copy_ms << ","
                << "\"final_copy_ms\":" << final_copy_ms << ","
                << "\"merge_level_profile\":[";
            for (size_t index = 0; index < merge_level_profile.size(); ++index) {
                const auto& level = merge_level_profile[index];
                if (index != 0)
                    out << ",";
                out << "{"
                    << "\"level\":" << index << ","
                    << "\"input_segments\":" << level.input_segments << ","
                    << "\"pair_count\":" << level.pair_count << ","
                    << "\"output_segments\":" << level.output_segments << ","
                    << "\"output_capacity\":" << level.output_capacity << ","
                    << "\"carry_copies\":" << level.carry_copies << ","
                    << "\"carry_payload_copies\":" << level.carry_payload_copies << ","
                    << "\"launch_ms\":" << level.launch_ms << ","
                    << "\"sync_ms\":" << level.sync_ms << ","
                    << "\"metadata_ms\":" << level.metadata_ms << ","
                    << "\"carry_copy_ms\":" << level.carry_copy_ms
                    << "}";
            }
            out << "],"
                << "\"total_ms\":" << elapsed_ms(total_start)
                << "}\n";
        } catch (...) {
            // Profiling must never change runtime behavior.
        }
    }
};

static bool collect_k_env_enabled(const char* name)
{
    const char* raw = std::getenv(name);
    return raw && raw[0] != '\0' && std::strcmp(raw, "0") != 0;
}

static bool collect_k_use_fastest_candidate()
{
    return collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE");
}

static uint64_t collect_k_predicted_carry_payload_copies(
    size_t candidate_count,
    size_t tile_size,
    bool use_batched_compact_level,
    bool use_derived_level_descriptors,
    bool use_derived_carry_alias_diagnostic)
{
    size_t current_segments = (candidate_count + tile_size - 1) / tile_size;
    uint64_t carry_payload_copies = 0;
    while (current_segments > 1) {
        const size_t pair_count = current_segments / 2;
        const bool has_carry = (current_segments % 2) != 0;
        const size_t next_segment_count = pair_count + (has_carry ? 1 : 0);
        const bool derived_carry_alias_safe_next =
            next_segment_count == 2 || (next_segment_count % 2) != 0;
        if (has_carry) {
            const bool use_derived_carry_alias_level =
                use_derived_carry_alias_diagnostic
                && use_batched_compact_level
                && current_segments != 2
                && use_derived_level_descriptors
                && derived_carry_alias_safe_next;
            if (!use_derived_carry_alias_level)
                ++carry_payload_copies;
        }
        current_segments = next_segment_count;
    }
    return carry_payload_copies;
}

static bool collect_k_use_gated_fastest_candidate(size_t candidate_count)
{
    if (!collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE"))
        return false;
    constexpr uint64_t min_payload_copy_reduction = 3;
    constexpr size_t tile_size = 2048;
    const uint64_t baseline_copies = collect_k_predicted_carry_payload_copies(
        candidate_count,
        tile_size,
        true,
        true,
        false);
    const uint64_t candidate_copies = collect_k_predicted_carry_payload_copies(
        candidate_count,
        tile_size,
        true,
        true,
        true);
    return baseline_copies >= candidate_copies + min_payload_copy_reduction;
}

static bool collect_k_use_parallel_final_compact()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT");
}

static size_t collect_k_parallel_compact_min_capacity(bool use_cub_tile_sort)
{
    const char* raw = std::getenv("RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY");
    if (!raw || raw[0] == '\0')
        return use_cub_tile_sort ? 4096 : 65536;
    char* end = nullptr;
    unsigned long long value = std::strtoull(raw, &end, 10);
    if (end == raw || value == 0)
        return use_cub_tile_sort ? 4096 : 65536;
    return static_cast<size_t>(value);
}

static bool collect_k_use_cub_tile_sort()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT");
}

static bool collect_k_use_batched_compact_level()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL");
}

static bool collect_k_use_device_prefix_compact()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT");
}

static bool collect_k_use_derived_level_descriptors()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS");
}

static bool collect_k_use_device_level_counts()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS");
}

static bool collect_k_use_device_final_counts()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS");
}

static bool collect_k_use_carry_pointer_diagnostic()
{
    return collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC");
}

static bool collect_k_use_carry_pointer_device_counts_diagnostic()
{
    return collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DEVICE_COUNTS_DIAGNOSTIC");
}

static bool collect_k_use_derived_carry_alias_diagnostic()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC");
}

static bool collect_k_reuse_workspace()
{
    return collect_k_use_fastest_candidate() || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE");
}

struct CollectKRowWidth2Workspace {
    size_t max_tiled_candidates = 0;
    CUdeviceptr temp_stage_a = 0;
    CUdeviceptr temp_stage_b = 0;
    CUdeviceptr tile_emitted_device = 0;
    CUdeviceptr tile_overflowed_device = 0;
    CUdeviceptr merge_emitted_device = 0;
    CUdeviceptr merge_overflowed_device = 0;
    CUdeviceptr merge_first_rows_device = 0;
    CUdeviceptr merge_second_rows_device = 0;
    CUdeviceptr merge_output_rows_device = 0;
    CUdeviceptr merge_first_counts_device = 0;
    CUdeviceptr merge_second_counts_device = 0;
    CUdeviceptr final_merged_rows = 0;
    CUdeviceptr final_marks = 0;
    CUdeviceptr final_block_counts = 0;
    CUdeviceptr final_block_offsets = 0;
    CUdeviceptr final_pair_offsets = 0;
    CUdeviceptr final_emitted_device = 0;
    CUdeviceptr final_overflowed_device = 0;

    void ensure(size_t requested_max_tiled_candidates)
    {
        if (max_tiled_candidates >= requested_max_tiled_candidates)
            return;
        if (max_tiled_candidates != 0)
            throw std::runtime_error("COLLECT_K_BOUNDED reusable workspace does not support growth yet");
        max_tiled_candidates = requested_max_tiled_candidates;
        CU_CHECK(cuMemAlloc(&temp_stage_a, sizeof(int64_t) * max_tiled_candidates * 2));
        CU_CHECK(cuMemAlloc(&temp_stage_b, sizeof(int64_t) * max_tiled_candidates * 2));
        CU_CHECK(cuMemAlloc(&tile_emitted_device, sizeof(size_t) * 64));
        CU_CHECK(cuMemAlloc(&tile_overflowed_device, sizeof(uint32_t) * 64));
        CU_CHECK(cuMemAlloc(&merge_emitted_device, sizeof(size_t) * 64));
        CU_CHECK(cuMemAlloc(&merge_overflowed_device, sizeof(uint32_t) * 64));
        CU_CHECK(cuMemAlloc(&merge_first_rows_device, sizeof(uint64_t) * 64));
        CU_CHECK(cuMemAlloc(&merge_second_rows_device, sizeof(uint64_t) * 64));
        CU_CHECK(cuMemAlloc(&merge_output_rows_device, sizeof(uint64_t) * 64));
        CU_CHECK(cuMemAlloc(&merge_first_counts_device, sizeof(size_t) * 64));
        CU_CHECK(cuMemAlloc(&merge_second_counts_device, sizeof(size_t) * 64));
        CU_CHECK(cuMemAlloc(&final_merged_rows, sizeof(int64_t) * max_tiled_candidates * 2));
        CU_CHECK(cuMemAlloc(&final_marks, sizeof(uint32_t) * max_tiled_candidates));
        CU_CHECK(cuMemAlloc(&final_block_counts, sizeof(uint32_t) * 512));
        CU_CHECK(cuMemAlloc(&final_block_offsets, sizeof(uint32_t) * 512));
        CU_CHECK(cuMemAlloc(&final_pair_offsets, sizeof(uint32_t) * 64));
        CU_CHECK(cuMemAlloc(&final_emitted_device, sizeof(size_t)));
        CU_CHECK(cuMemAlloc(&final_overflowed_device, sizeof(uint32_t)));
    }
};

static std::mutex g_collect_k_row_width2_workspace_mutex;
static CollectKRowWidth2Workspace g_collect_k_row_width2_workspace;

extern "C" int rtdl_optix_collect_k_bounded_i64_device(
        uint64_t candidate_rows_device_ptr, size_t candidate_count,
        size_t row_width, uint64_t rows_out_device_ptr, size_t row_capacity,
        size_t* emitted_count_out, uint32_t* overflowed_out,
        uint64_t* h2d_transfers_out, uint64_t* d2h_transfers_out,
        uint64_t* internal_device_transfers_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!emitted_count_out || !overflowed_out ||
            !h2d_transfers_out || !d2h_transfers_out || !internal_device_transfers_out)
            throw std::runtime_error("metadata and transfer-accounting outputs must not be null");
        *emitted_count_out = 0;
        *overflowed_out = 0;
        *h2d_transfers_out = 0;
        *d2h_transfers_out = 0;
        *internal_device_transfers_out = 0;
        if (row_width == 0)
            throw std::runtime_error("row_width must be positive");
        if (candidate_count != 0 && candidate_rows_device_ptr == 0)
            throw std::runtime_error("candidate_rows_device_ptr must not be zero when candidate_count is nonzero");
        if (row_capacity != 0 && rows_out_device_ptr == 0)
            throw std::runtime_error("rows_out_device_ptr must not be zero when row_capacity is nonzero");
        if (candidate_count == 0)
            return;

        CollectKStageProfile profile(candidate_count, row_width, row_capacity);
        (void)get_optix_context();
        size_t padded_count = 1;
        unsigned row_width2_shared_bytes = 0;
        int max_optin_shared_bytes = 0;
        bool row_width2_fast_supported = false;
        if (row_width == 2 && candidate_count <= 4096) {
            while (padded_count < candidate_count)
                padded_count <<= 1;
            row_width2_shared_bytes = static_cast<unsigned>(
                sizeof(int64_t) * padded_count * 2 + sizeof(uint8_t) * padded_count);
            CUdevice current_device = 0;
            CU_CHECK(cuCtxGetDevice(&current_device));
            CU_CHECK(cuDeviceGetAttribute(
                &max_optin_shared_bytes,
                CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN,
                current_device));
            row_width2_fast_supported =
                row_width2_shared_bytes <= static_cast<unsigned>(max_optin_shared_bytes);
        }
        if (row_width2_fast_supported) {
            profile.native_path = "row_width2_parallel_bitonic_sort";
            auto module_start = CollectKStageProfile::Clock::now();
            std::call_once(g_collect_k_i64_row_width2_sort.init, [&]() {
                std::string ptx = compile_to_ptx(
                    kCollectKBoundedI64RowWidth2SortKernelSrc,
                    "collect_k_bounded_i64_row_width2_sort_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_sort.module, ptx.c_str()));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_sort.fn,
                    g_collect_k_i64_row_width2_sort.module,
                    "collect_k_bounded_i64_row_width2_sort"));
            });
            profile.add_since(profile.module_load_ms, module_start);

            auto allocation_start = CollectKStageProfile::Clock::now();
            DevPtr emitted_device(sizeof(size_t));
            DevPtr overflowed_device(sizeof(uint32_t));
            CUdeviceptr candidate_rows = static_cast<CUdeviceptr>(candidate_rows_device_ptr);
            CUdeviceptr rows_out = static_cast<CUdeviceptr>(rows_out_device_ptr);
            profile.add_since(profile.allocation_ms, allocation_start);
            void* args[] = {
                &candidate_rows,
                &candidate_count,
                &padded_count,
                &rows_out,
                &row_capacity,
                &emitted_device.ptr,
                &overflowed_device.ptr,
            };
            if (row_width2_shared_bytes > 49152u) {
                CU_CHECK(cuFuncSetAttribute(
                    g_collect_k_i64_row_width2_sort.fn,
                    CU_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES,
                    static_cast<int>(row_width2_shared_bytes)));
            }
            auto sort_launch_start = CollectKStageProfile::Clock::now();
            CU_CHECK(cuLaunchKernel(
                g_collect_k_i64_row_width2_sort.fn,
                1, 1, 1,
                static_cast<unsigned>(std::min<size_t>(padded_count, 1024)), 1, 1,
                row_width2_shared_bytes, nullptr, args, nullptr));
            profile.add_since(profile.sort_launch_ms, sort_launch_start);
            profile.sort_launches = 1;
            auto sort_sync_start = CollectKStageProfile::Clock::now();
            CU_CHECK(cuStreamSynchronize(nullptr));
            profile.add_since(profile.sort_sync_ms, sort_sync_start);

            auto metadata_start = CollectKStageProfile::Clock::now();
            download(emitted_count_out, emitted_device.ptr, 1);
            download(overflowed_out, overflowed_device.ptr, 1);
            profile.add_since(profile.tile_metadata_download_ms, metadata_start);
            *d2h_transfers_out += 2;
            profile.metadata_fields_downloaded += 2;
            profile.append(*emitted_count_out, *overflowed_out, *h2d_transfers_out,
                           *d2h_transfers_out, *internal_device_transfers_out);
            return;
        }

        bool row_width2_tiled_supported = false;
        if (row_width == 2 && candidate_count > 4096 && candidate_count <= 131072) {
            const unsigned tile_shared_bytes = static_cast<unsigned>(
                sizeof(int64_t) * 4096 * 2 + sizeof(uint8_t) * 4096);
            CUdevice current_device = 0;
            CU_CHECK(cuCtxGetDevice(&current_device));
            CU_CHECK(cuDeviceGetAttribute(
                &max_optin_shared_bytes,
                CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN,
                current_device));
            row_width2_tiled_supported =
                tile_shared_bytes <= static_cast<unsigned>(max_optin_shared_bytes);
        }
        if (row_width2_tiled_supported) {
            profile.native_path = "row_width2_bounded_multi_tile_sort_merge";
            const bool use_gated_candidate_mode =
                collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE");
            const bool use_fastest_candidate_for_case = collect_k_use_fastest_candidate();
            const bool use_gated_fastest_candidate_for_case =
                collect_k_use_gated_fastest_candidate(candidate_count);
            const bool use_candidate_bundle_for_case =
                use_fastest_candidate_for_case || use_gated_fastest_candidate_for_case;
            const bool use_gated_or_candidate_bundle =
                use_gated_candidate_mode || use_candidate_bundle_for_case;
            const bool use_cub_tile_sort =
                use_gated_or_candidate_bundle || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT");
            auto module_start = CollectKStageProfile::Clock::now();
            std::call_once(g_collect_k_i64_row_width2_sort.init, [&]() {
                std::string ptx = compile_to_ptx(
                    kCollectKBoundedI64RowWidth2SortKernelSrc,
                    "collect_k_bounded_i64_row_width2_sort_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_sort.module, ptx.c_str()));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_sort.fn,
                    g_collect_k_i64_row_width2_sort.module,
                    "collect_k_bounded_i64_row_width2_sort"));
            });
            if (use_cub_tile_sort) {
                std::call_once(g_collect_k_i64_row_width2_cub_sort.init, [&]() {
                    std::string ptx = compile_to_ptx(
                        kCollectKBoundedI64RowWidth2CubSortKernelSrc,
                        "collect_k_bounded_i64_row_width2_cub_sort_kernel.cu");
                    CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_cub_sort.module, ptx.c_str()));
                    CU_CHECK(cuModuleGetFunction(
                        &g_collect_k_i64_row_width2_cub_sort.fn,
                        g_collect_k_i64_row_width2_cub_sort.module,
                        "collect_k_bounded_i64_row_width2_cub_sort"));
                    CU_CHECK(cuModuleGetFunction(
                        &g_collect_k_i64_row_width2_cub_sort_tiles.fn,
                        g_collect_k_i64_row_width2_cub_sort.module,
                        "collect_k_bounded_i64_row_width2_cub_sort_tiles"));
                });
            }
            std::call_once(g_collect_k_i64_row_width2_merge_two.init, [&]() {
                std::string ptx = compile_to_ptx(
                    kCollectKBoundedI64RowWidth2MergeTwoKernelSrc,
                    "collect_k_bounded_i64_row_width2_merge_two_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_merge_two.module, ptx.c_str()));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_merge_two.fn,
                    g_collect_k_i64_row_width2_merge_two.module,
                    "collect_k_bounded_i64_row_width2_merge_two"));
            });
            std::call_once(g_collect_k_i64_row_width2_merge_level.init, [&]() {
                std::string ptx = compile_to_ptx(
                    kCollectKBoundedI64RowWidth2MergeLevelKernelSrc,
                    "collect_k_bounded_i64_row_width2_merge_level_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_merge_level.module, ptx.c_str()));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_merge_level.fn,
                    g_collect_k_i64_row_width2_merge_level.module,
                    "collect_k_bounded_i64_row_width2_merge_level"));
            });
            std::call_once(g_collect_k_i64_row_width2_final_materialize.init, [&]() {
                std::string ptx = compile_to_ptx(
                    kCollectKBoundedI64RowWidth2FinalCompactKernelSrc,
                    "collect_k_bounded_i64_row_width2_final_compact_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_final_materialize.module, ptx.c_str()));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_materialize.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_materialize"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_materialize_counts.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_materialize_counts"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_mark_counts.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_mark_counts"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_mark_counts_counts.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_mark_counts_counts"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_compact.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_compact"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_compact_counts.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_compact_counts"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_materialize_level.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_materialize_level"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_materialize_level_derived.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_materialize_level_derived"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_materialize_level_counts_pointers.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_materialize_level_counts_pointers"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_mark_counts_level.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_mark_counts_level"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_mark_counts_level_counts"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_mark_counts_level_counts_pointers.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_mark_counts_level_counts_pointers"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_materialize_mark_counts_level_counts.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_materialize_mark_counts_level_counts"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_compact_level.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_compact_level"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_compact_level_derived"));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_final_prefix_offsets_level"));
            });
            profile.add_since(profile.module_load_ms, module_start);

            const size_t tile_size = use_cub_tile_sort ? 2048 : 4096;
            const size_t tile_count = (candidate_count + tile_size - 1) / tile_size;
            const unsigned tile_shared_bytes = static_cast<unsigned>(
                sizeof(int64_t) * tile_size * 2 + sizeof(uint8_t) * tile_size);
            if (tile_shared_bytes > 49152u) {
                CU_CHECK(cuFuncSetAttribute(
                    g_collect_k_i64_row_width2_sort.fn,
                    CU_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES,
                    static_cast<int>(tile_shared_bytes)));
            }

            const size_t max_tiled_candidates = 131072;
            profile.tile_count = tile_count;
            auto allocation_start = CollectKStageProfile::Clock::now();
            struct DeviceSlot {
                CUdeviceptr ptr = 0;
            };
            std::vector<std::unique_ptr<DevPtr>> local_allocations;
            local_allocations.reserve(18);
            std::unique_lock<std::mutex> reusable_workspace_lock;
            const bool use_reusable_workspace =
                use_gated_or_candidate_bundle || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_REUSE_WORKSPACE");
            if (use_reusable_workspace) {
                reusable_workspace_lock = std::unique_lock<std::mutex>(
                    g_collect_k_row_width2_workspace_mutex);
                g_collect_k_row_width2_workspace.ensure(max_tiled_candidates);
            }
            auto make_slot = [&](CUdeviceptr reusable_ptr, size_t bytes) {
                DeviceSlot slot;
                if (use_reusable_workspace) {
                    slot.ptr = reusable_ptr;
                    return slot;
                }
                local_allocations.push_back(std::make_unique<DevPtr>(bytes));
                slot.ptr = local_allocations.back()->ptr;
                return slot;
            };
            DeviceSlot temp_stage_a = make_slot(
                g_collect_k_row_width2_workspace.temp_stage_a,
                sizeof(int64_t) * max_tiled_candidates * 2);
            DeviceSlot temp_stage_b = make_slot(
                g_collect_k_row_width2_workspace.temp_stage_b,
                sizeof(int64_t) * max_tiled_candidates * 2);
            DeviceSlot tile_emitted_device = make_slot(
                g_collect_k_row_width2_workspace.tile_emitted_device,
                sizeof(size_t) * 64);
            DeviceSlot tile_overflowed_device = make_slot(
                g_collect_k_row_width2_workspace.tile_overflowed_device,
                sizeof(uint32_t) * 64);
            DeviceSlot merge_emitted_device = make_slot(
                g_collect_k_row_width2_workspace.merge_emitted_device,
                sizeof(size_t) * 64);
            DeviceSlot merge_overflowed_device = make_slot(
                g_collect_k_row_width2_workspace.merge_overflowed_device,
                sizeof(uint32_t) * 64);
            DeviceSlot merge_first_rows_device = make_slot(
                g_collect_k_row_width2_workspace.merge_first_rows_device,
                sizeof(uint64_t) * 64);
            DeviceSlot merge_second_rows_device = make_slot(
                g_collect_k_row_width2_workspace.merge_second_rows_device,
                sizeof(uint64_t) * 64);
            DeviceSlot merge_output_rows_device = make_slot(
                g_collect_k_row_width2_workspace.merge_output_rows_device,
                sizeof(uint64_t) * 64);
            DeviceSlot merge_first_counts_device = make_slot(
                g_collect_k_row_width2_workspace.merge_first_counts_device,
                sizeof(size_t) * 64);
            DeviceSlot merge_second_counts_device = make_slot(
                g_collect_k_row_width2_workspace.merge_second_counts_device,
                sizeof(size_t) * 64);
            DeviceSlot final_merged_rows = make_slot(
                g_collect_k_row_width2_workspace.final_merged_rows,
                sizeof(int64_t) * max_tiled_candidates * 2);
            DeviceSlot final_marks = make_slot(
                g_collect_k_row_width2_workspace.final_marks,
                sizeof(uint32_t) * max_tiled_candidates);
            DeviceSlot final_block_counts = make_slot(
                g_collect_k_row_width2_workspace.final_block_counts,
                sizeof(uint32_t) * 512);
            DeviceSlot final_block_offsets = make_slot(
                g_collect_k_row_width2_workspace.final_block_offsets,
                sizeof(uint32_t) * 512);
            DeviceSlot final_pair_offsets = make_slot(
                g_collect_k_row_width2_workspace.final_pair_offsets,
                sizeof(uint32_t) * 64);
            DeviceSlot final_emitted_device = make_slot(
                g_collect_k_row_width2_workspace.final_emitted_device,
                sizeof(size_t));
            DeviceSlot final_overflowed_device = make_slot(
                g_collect_k_row_width2_workspace.final_overflowed_device,
                sizeof(uint32_t));
            CUdeviceptr candidate_rows = static_cast<CUdeviceptr>(candidate_rows_device_ptr);
            CUdeviceptr rows_out = static_cast<CUdeviceptr>(rows_out_device_ptr);
            profile.add_since(profile.allocation_ms, allocation_start);

            auto temp_sorted_tile = [&](size_t tile_index) {
                return temp_stage_a.ptr + sizeof(int64_t) * tile_size * 2 * tile_index;
            };
            auto launch_cub_sort_tiles = [&]() {
                void* cub_sort_args[] = {
                    &candidate_rows,
                    &candidate_count,
                    &temp_stage_a.ptr,
                    &tile_emitted_device.ptr,
                    &tile_overflowed_device.ptr,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_cub_sort_tiles.fn,
                    static_cast<unsigned>(tile_count), 1, 1,
                    256, 1, 1,
                    0, nullptr, cub_sort_args, nullptr));
            };
            auto launch_sort_tile = [&](size_t tile_index) {
                size_t tile_candidate_count = std::min(tile_size, candidate_count - tile_index * tile_size);
                size_t tile_padded_count = 1;
                while (tile_padded_count < tile_candidate_count)
                    tile_padded_count <<= 1;
                CUdeviceptr tile_input = candidate_rows + sizeof(int64_t) * tile_size * 2 * tile_index;
                CUdeviceptr tile_output = temp_sorted_tile(tile_index);
                CUdeviceptr tile_emitted = tile_emitted_device.ptr + sizeof(size_t) * tile_index;
                CUdeviceptr tile_overflowed = tile_overflowed_device.ptr + sizeof(uint32_t) * tile_index;
                size_t tile_capacity = tile_size;
                if (use_cub_tile_sort) {
                    void* cub_sort_args[] = {
                        &tile_input,
                        &tile_candidate_count,
                        &tile_output,
                        &tile_capacity,
                        &tile_emitted,
                        &tile_overflowed,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_cub_sort.fn,
                        1, 1, 1,
                        256, 1, 1,
                        0, nullptr, cub_sort_args, nullptr));
                    return;
                }
                void* sort_args[] = {
                    &tile_input,
                    &tile_candidate_count,
                    &tile_padded_count,
                    &tile_output,
                    &tile_capacity,
                    &tile_emitted,
                    &tile_overflowed,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_sort.fn,
                    1, 1, 1,
                    static_cast<unsigned>(std::min<size_t>(tile_padded_count, 1024)), 1, 1,
                    tile_shared_bytes, nullptr, sort_args, nullptr));
            };
            auto launch_merge_level = [&](size_t pair_count, size_t output_capacity) {
                void* merge_args[] = {
                    &merge_first_rows_device.ptr,
                    &merge_first_counts_device.ptr,
                    &merge_second_rows_device.ptr,
                    &merge_second_counts_device.ptr,
                    &merge_output_rows_device.ptr,
                    &output_capacity,
                    &merge_emitted_device.ptr,
                    &merge_overflowed_device.ptr,
                    &pair_count,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_merge_level.fn,
                    static_cast<unsigned>(pair_count), 1, 1,
                    1, 1, 1,
                    0, nullptr, merge_args, nullptr));
            };
            auto launch_parallel_compact_pair = [&](CUdeviceptr first_rows, size_t first_count,
                                                    CUdeviceptr second_rows, size_t second_count,
                                                    CUdeviceptr output_rows, size_t output_capacity,
                                                    size_t* final_count_out) {
                size_t total = first_count + second_count;
                const unsigned threads = 256;
                const unsigned blocks = static_cast<unsigned>((total + threads - 1) / threads);
                void* materialize_args[] = {
                    &first_rows,
                    &first_count,
                    &second_rows,
                    &second_count,
                    &final_merged_rows.ptr,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_materialize.fn,
                    blocks, 1, 1,
                    threads, 1, 1,
                    0, nullptr, materialize_args, nullptr));

                void* mark_args[] = {
                    &final_merged_rows.ptr,
                    &total,
                    &final_marks.ptr,
                    &final_block_counts.ptr,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_mark_counts.fn,
                    blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, nullptr, mark_args, nullptr));
                CU_CHECK(cuStreamSynchronize(nullptr));

                std::array<uint32_t, 512> block_counts = {};
                std::array<uint32_t, 512> block_offsets = {};
                download(block_counts.data(), final_block_counts.ptr, blocks);
                uint32_t running_total = 0;
                for (unsigned block_index = 0; block_index < blocks; ++block_index) {
                    block_offsets[block_index] = running_total;
                    running_total += block_counts[block_index];
                }
                upload(final_block_offsets.ptr, block_offsets.data(), blocks);
                *final_count_out = static_cast<size_t>(running_total);

                void* compact_args[] = {
                    &final_merged_rows.ptr,
                    &final_marks.ptr,
                    &final_block_offsets.ptr,
                    &total,
                    &output_rows,
                    &output_capacity,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact.fn,
                    blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, nullptr, compact_args, nullptr));
            };
            auto launch_parallel_compact_pair_counts = [&](CUdeviceptr first_rows,
                                                           CUdeviceptr second_rows,
                                                           CUdeviceptr counts_device,
                                                           size_t scan_capacity,
                                                           CUdeviceptr output_rows,
                                                           size_t output_capacity,
                                                           size_t* final_count_out) {
                const unsigned threads = 256;
                const unsigned blocks = static_cast<unsigned>((scan_capacity + threads - 1) / threads);
                void* materialize_args[] = {
                    &first_rows,
                    &second_rows,
                    &counts_device,
                    &final_merged_rows.ptr,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_materialize_counts.fn,
                    blocks, 1, 1,
                    threads, 1, 1,
                    0, nullptr, materialize_args, nullptr));

                void* mark_args[] = {
                    &final_merged_rows.ptr,
                    &counts_device,
                    &final_marks.ptr,
                    &final_block_counts.ptr,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_mark_counts_counts.fn,
                    blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, nullptr, mark_args, nullptr));
                CU_CHECK(cuStreamSynchronize(nullptr));

                std::array<uint32_t, 512> block_counts = {};
                std::array<uint32_t, 512> block_offsets = {};
                download(block_counts.data(), final_block_counts.ptr, blocks);
                uint32_t running_total = 0;
                for (unsigned block_index = 0; block_index < blocks; ++block_index) {
                    block_offsets[block_index] = running_total;
                    running_total += block_counts[block_index];
                }
                upload(final_block_offsets.ptr, block_offsets.data(), blocks);
                *final_count_out = static_cast<size_t>(running_total);

                void* compact_args[] = {
                    &final_merged_rows.ptr,
                    &final_marks.ptr,
                    &final_block_offsets.ptr,
                    &counts_device,
                    &output_rows,
                    &output_capacity,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact_counts.fn,
                    blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, nullptr, compact_args, nullptr));
            };
            auto launch_parallel_compact_level = [&](size_t pair_count, size_t output_capacity,
                                                     size_t blocks_per_pair,
                                                     std::vector<size_t>* pair_counts_out,
                                                     bool use_device_prefix_compact,
                                                     bool use_derived_level_descriptors,
                                                     bool use_device_level_counts,
                                                     bool use_pointer_device_counts,
                                                     CUdeviceptr current_base,
                                                     CUdeviceptr current_counts_device,
                                                     CUdeviceptr next_counts_device,
                                                     size_t segment_capacity,
                                                     CUdeviceptr output_base) {
                const unsigned threads = 256;
                const unsigned total_blocks = static_cast<unsigned>(pair_count * blocks_per_pair);
                if (use_pointer_device_counts) {
                    void* materialize_args[] = {
                        &merge_first_rows_device.ptr,
                        &merge_second_rows_device.ptr,
                        &current_counts_device,
                        &output_capacity,
                        &final_merged_rows.ptr,
                        &pair_count,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_materialize_level_counts_pointers.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        0, nullptr, materialize_args, nullptr));
                } else if (use_device_level_counts) {
                    void* materialize_args[] = {
                        &current_base,
                        &current_counts_device,
                        &segment_capacity,
                        &output_capacity,
                        &final_merged_rows.ptr,
                        &pair_count,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        0, nullptr, materialize_args, nullptr));
                } else if (use_derived_level_descriptors) {
                    void* materialize_args[] = {
                        &current_base,
                        &merge_first_counts_device.ptr,
                        &merge_second_counts_device.ptr,
                        &segment_capacity,
                        &output_capacity,
                        &final_merged_rows.ptr,
                        &pair_count,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_materialize_level_derived.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        0, nullptr, materialize_args, nullptr));
                } else {
                    void* materialize_args[] = {
                        &merge_first_rows_device.ptr,
                        &merge_first_counts_device.ptr,
                        &merge_second_rows_device.ptr,
                        &merge_second_counts_device.ptr,
                        &output_capacity,
                        &final_merged_rows.ptr,
                        &pair_count,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_materialize_level.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        0, nullptr, materialize_args, nullptr));
                }

                if (use_pointer_device_counts) {
                    void* mark_args[] = {
                        &final_merged_rows.ptr,
                        &current_counts_device,
                        &output_capacity,
                        &pair_count,
                        &final_marks.ptr,
                        &final_block_counts.ptr,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_mark_counts_level_counts_pointers.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        sizeof(uint32_t) * threads, nullptr, mark_args, nullptr));
                } else if (use_device_level_counts) {
                    void* mark_args[] = {
                        &final_merged_rows.ptr,
                        &current_counts_device,
                        &output_capacity,
                        &pair_count,
                        &final_marks.ptr,
                        &final_block_counts.ptr,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        sizeof(uint32_t) * threads, nullptr, mark_args, nullptr));
                } else {
                    void* mark_args[] = {
                        &final_merged_rows.ptr,
                        &merge_first_counts_device.ptr,
                        &merge_second_counts_device.ptr,
                        &output_capacity,
                        &pair_count,
                        &final_marks.ptr,
                        &final_block_counts.ptr,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_mark_counts_level.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        sizeof(uint32_t) * threads, nullptr, mark_args, nullptr));
                }

                pair_counts_out->clear();
                pair_counts_out->resize(pair_count);
                if (use_device_prefix_compact) {
                    CUdeviceptr pair_counts_output_device =
                        use_device_level_counts ? next_counts_device : merge_emitted_device.ptr;
                    void* prefix_args[] = {
                        &final_block_counts.ptr,
                        &pair_count,
                        &blocks_per_pair,
                        &final_block_offsets.ptr,
                        &final_pair_offsets.ptr,
                        &pair_counts_output_device,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                        static_cast<unsigned>(pair_count), 1, 1,
                        1, 1, 1,
                        0, nullptr, prefix_args, nullptr));
                    if (!use_device_level_counts)
                        download(pair_counts_out->data(), merge_emitted_device.ptr, pair_count);
                } else {
                    CU_CHECK(cuStreamSynchronize(nullptr));

                    std::array<uint32_t, 512> block_counts = {};
                    std::array<uint32_t, 512> block_offsets = {};
                    std::array<uint32_t, 64> pair_offsets = {};
                    download(block_counts.data(), final_block_counts.ptr, total_blocks);
                    uint32_t running_total = 0;
                    for (size_t pair_index = 0; pair_index < pair_count; ++pair_index) {
                        pair_offsets[pair_index] = running_total;
                        uint32_t pair_total = 0;
                        for (size_t block_index = 0; block_index < blocks_per_pair; ++block_index) {
                            const size_t global_block = pair_index * blocks_per_pair + block_index;
                            block_offsets[global_block] = running_total;
                            pair_total += block_counts[global_block];
                            running_total += block_counts[global_block];
                        }
                        (*pair_counts_out)[pair_index] = static_cast<size_t>(pair_total);
                    }
                    upload(final_block_offsets.ptr, block_offsets.data(), total_blocks);
                    upload(final_pair_offsets.ptr, pair_offsets.data(), pair_count);
                }

                if (use_derived_level_descriptors) {
                    void* compact_args[] = {
                        &final_merged_rows.ptr,
                        &final_marks.ptr,
                        &final_block_offsets.ptr,
                        &final_pair_offsets.ptr,
                        &output_base,
                        &output_capacity,
                        &pair_count,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        sizeof(uint32_t) * threads, nullptr, compact_args, nullptr));
                } else {
                    void* compact_args[] = {
                        &final_merged_rows.ptr,
                        &final_marks.ptr,
                        &final_block_offsets.ptr,
                        &final_pair_offsets.ptr,
                        &merge_output_rows_device.ptr,
                        &output_capacity,
                        &pair_count,
                        &blocks_per_pair,
                    };
                    CU_CHECK(cuLaunchKernel(
                        g_collect_k_i64_row_width2_final_compact_level.fn,
                        total_blocks, 1, 1,
                        threads, 1, 1,
                        sizeof(uint32_t) * threads, nullptr, compact_args, nullptr));
                }
            };

            auto sort_launch_start = CollectKStageProfile::Clock::now();
            if (use_cub_tile_sort) {
                launch_cub_sort_tiles();
            } else {
                for (size_t tile_index = 0; tile_index < tile_count; ++tile_index)
                    launch_sort_tile(tile_index);
            }
            profile.add_since(profile.sort_launch_ms, sort_launch_start);
            profile.sort_launches += use_cub_tile_sort ? 1 : tile_count;
            auto sort_sync_start = CollectKStageProfile::Clock::now();
            CU_CHECK(cuStreamSynchronize(nullptr));
            profile.add_since(profile.sort_sync_ms, sort_sync_start);

            const bool use_parallel_final_compact =
                use_gated_or_candidate_bundle || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT");
            const bool use_batched_compact_level =
                use_gated_or_candidate_bundle || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_BATCH_COMPACT_LEVEL");
            const bool use_device_prefix_compact =
                use_gated_or_candidate_bundle || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DEVICE_PREFIX_COMPACT");
            const bool use_derived_level_descriptors =
                use_gated_or_candidate_bundle || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DERIVED_LEVEL_DESCRIPTORS");
            const bool use_device_level_counts =
                (use_gated_or_candidate_bundle || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DEVICE_LEVEL_COUNTS"))
                && use_derived_level_descriptors
                && use_device_prefix_compact;
            const bool use_device_final_counts =
                (use_gated_or_candidate_bundle || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS"))
                && use_device_level_counts;
            const bool use_carry_pointer_diagnostic =
                collect_k_use_carry_pointer_diagnostic() && use_device_level_counts;
            const bool use_carry_pointer_device_counts_diagnostic =
                collect_k_use_carry_pointer_device_counts_diagnostic() && use_device_level_counts;
            const bool use_derived_carry_alias_diagnostic =
                (use_candidate_bundle_for_case || collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC"))
                && use_device_level_counts;

            std::array<size_t, 64> tile_emitted = {};
            std::array<uint32_t, 64> tile_overflowed = {};
            auto tile_metadata_start = CollectKStageProfile::Clock::now();
            if (!use_device_level_counts)
                download(tile_emitted.data(), tile_emitted_device.ptr, tile_count);
            download(tile_overflowed.data(), tile_overflowed_device.ptr, tile_count);
            profile.add_since(profile.tile_metadata_download_ms, tile_metadata_start);
            *d2h_transfers_out += static_cast<uint64_t>(
                tile_count * (use_device_level_counts ? 1 : 2));
            profile.metadata_fields_downloaded += static_cast<uint64_t>(
                tile_count * (use_device_level_counts ? 1 : 2));
            for (size_t tile_index = 0; tile_index < tile_count; ++tile_index) {
                if (tile_overflowed[tile_index])
                    throw std::runtime_error("row_width=2 tile collect unexpectedly overflowed");
            }

            std::vector<CUdeviceptr> current_rows;
            std::vector<size_t> current_counts;
            current_rows.reserve(tile_count);
            current_counts.reserve(tile_count);
            for (size_t tile_index = 0; tile_index < tile_count; ++tile_index) {
                current_rows.push_back(temp_sorted_tile(tile_index));
                current_counts.push_back(use_device_level_counts ? 0 : tile_emitted[tile_index]);
            }

            size_t segment_capacity = tile_size;
            bool write_stage_b = true;
            uint64_t merge_launches = 0;
            const size_t parallel_compact_min_capacity =
                collect_k_parallel_compact_min_capacity(use_cub_tile_sort);
            CUdeviceptr current_counts_level_device = tile_emitted_device.ptr;
            CUdeviceptr next_counts_level_device = merge_emitted_device.ptr;
            while (current_rows.size() > 1) {
                CollectKStageProfile::MergeLevel level_profile;
                level_profile.input_segments = current_rows.size();
                const size_t pair_count = current_rows.size() / 2;
                const bool has_carry = (current_rows.size() % 2) != 0;
                const size_t output_segment_capacity = segment_capacity * 2;
                CUdeviceptr output_base = write_stage_b ? temp_stage_b.ptr : temp_stage_a.ptr;
                const size_t next_segment_count = pair_count + (has_carry ? 1 : 0);
                const bool derived_carry_alias_safe_next =
                    next_segment_count == 2 || (next_segment_count % 2) != 0;
                level_profile.pair_count = pair_count;
                level_profile.output_segments = next_segment_count;
                level_profile.output_capacity = output_segment_capacity;

                if (use_device_level_counts && !use_device_final_counts && current_rows.size() == 2) {
                    current_counts.resize(2);
                    download(current_counts.data(), current_counts_level_device, 2);
                    *d2h_transfers_out += 2;
                    profile.metadata_fields_downloaded += 2;
                }

                if (use_parallel_final_compact && output_segment_capacity >= parallel_compact_min_capacity) {
                    auto merge_launch_start = CollectKStageProfile::Clock::now();
                    std::vector<CUdeviceptr> next_rows;
                    std::vector<size_t> next_counts;
                    next_rows.reserve(pair_count + (has_carry ? 1 : 0));
                    next_counts.reserve(pair_count + (has_carry ? 1 : 0));
                    if (use_batched_compact_level && current_rows.size() != 2) {
                        const bool use_pointer_device_counts_carry_level =
                            use_carry_pointer_device_counts_diagnostic
                            && !use_derived_carry_alias_diagnostic
                            && has_carry
                            && use_derived_level_descriptors;
                        const bool use_pointer_host_counts_carry_level =
                            use_carry_pointer_diagnostic
                            && !use_derived_carry_alias_diagnostic
                            && has_carry
                            && use_derived_level_descriptors
                            && !use_pointer_device_counts_carry_level;
                        const bool use_pointer_carry_level =
                            use_pointer_host_counts_carry_level
                            || use_pointer_device_counts_carry_level;
                        const bool level_use_device_level_counts =
                            use_device_level_counts && !use_pointer_host_counts_carry_level;
                        const bool level_use_derived_level_descriptors =
                            use_derived_level_descriptors && !use_pointer_carry_level;
                        const bool level_use_pointer_device_counts =
                            use_pointer_device_counts_carry_level;
                        std::array<size_t, 64> merge_first_counts = {};
                        std::array<size_t, 64> merge_second_counts = {};
                        std::array<uint64_t, 64> merge_first_rows = {};
                        std::array<uint64_t, 64> merge_second_rows = {};
                        std::array<uint64_t, 64> merge_output_rows = {};
                        if (use_pointer_host_counts_carry_level) {
                            current_counts.resize(current_rows.size());
                            auto count_download_start = CollectKStageProfile::Clock::now();
                            download(current_counts.data(), current_counts_level_device, current_rows.size());
                            level_profile.metadata_ms += CollectKStageProfile::elapsed_ms(count_download_start);
                            *d2h_transfers_out += static_cast<uint64_t>(current_rows.size());
                            profile.metadata_fields_downloaded += static_cast<uint64_t>(current_rows.size());
                        }
                        for (size_t pair_index = 0; pair_index < pair_count; ++pair_index) {
                            CUdeviceptr pair_output =
                                output_base + sizeof(int64_t) * output_segment_capacity * 2 * pair_index;
                            if (!level_use_derived_level_descriptors) {
                                merge_first_rows[pair_index] = static_cast<uint64_t>(current_rows[pair_index * 2]);
                                merge_second_rows[pair_index] = static_cast<uint64_t>(current_rows[pair_index * 2 + 1]);
                                merge_output_rows[pair_index] = static_cast<uint64_t>(pair_output);
                            }
                            if (!level_use_device_level_counts) {
                                merge_first_counts[pair_index] = current_counts[pair_index * 2];
                                merge_second_counts[pair_index] = current_counts[pair_index * 2 + 1];
                            }
                            next_rows.push_back(pair_output);
                        }
                        if (level_use_device_level_counts) {
                            next_counts.resize(pair_count + (has_carry ? 1 : 0));
                        } else {
                            upload(merge_first_counts_device.ptr, merge_first_counts.data(), pair_count);
                            upload(merge_second_counts_device.ptr, merge_second_counts.data(), pair_count);
                        }
                        if (!level_use_derived_level_descriptors) {
                            upload(merge_first_rows_device.ptr, merge_first_rows.data(), pair_count);
                            upload(merge_second_rows_device.ptr, merge_second_rows.data(), pair_count);
                            upload(merge_output_rows_device.ptr, merge_output_rows.data(), pair_count);
                        }
                        const size_t descriptor_fields_uploaded = level_use_pointer_device_counts
                            ? 3
                            : (level_use_device_level_counts ? 0 : (level_use_derived_level_descriptors ? 2 : 5));
                        *h2d_transfers_out += static_cast<uint64_t>(pair_count * descriptor_fields_uploaded);
                        const size_t blocks_per_pair = (output_segment_capacity + 255) / 256;
                        launch_parallel_compact_level(
                            pair_count, output_segment_capacity, blocks_per_pair, &next_counts,
                            use_device_prefix_compact,
                            level_use_derived_level_descriptors,
                            level_use_device_level_counts,
                            level_use_pointer_device_counts,
                            current_rows.front(),
                            current_counts_level_device,
                            next_counts_level_device,
                            segment_capacity,
                            output_base);
                        merge_launches += use_device_prefix_compact ? 4 : 3;
                        profile.merge_launches += use_device_prefix_compact ? 4 : 3;
                    } else {
                        for (size_t pair_index = 0; pair_index < pair_count; ++pair_index) {
                            CUdeviceptr pair_output = current_rows.size() == 2
                                ? rows_out
                                : output_base + sizeof(int64_t) * output_segment_capacity * 2 * pair_index;
                            const size_t pair_capacity = current_rows.size() == 2
                                ? row_capacity
                                : output_segment_capacity;
                            size_t pair_count_out = 0;
                            if (use_device_final_counts && current_rows.size() == 2) {
                                launch_parallel_compact_pair_counts(
                                    current_rows[pair_index * 2],
                                    current_rows[pair_index * 2 + 1],
                                    current_counts_level_device,
                                    output_segment_capacity,
                                    pair_output, pair_capacity,
                                    &pair_count_out);
                            } else {
                                launch_parallel_compact_pair(
                                    current_rows[pair_index * 2], current_counts[pair_index * 2],
                                    current_rows[pair_index * 2 + 1], current_counts[pair_index * 2 + 1],
                                    pair_output, pair_capacity,
                                    &pair_count_out);
                            }
                            next_rows.push_back(pair_output);
                            next_counts.push_back(pair_count_out);
                        }
                        merge_launches += pair_count * 3;
                        profile.merge_launches += pair_count * 3;
                    }
                    level_profile.launch_ms = CollectKStageProfile::elapsed_ms(merge_launch_start);
                    if (profile.enabled)
                        profile.merge_launch_ms += level_profile.launch_ms;
                    ++profile.merge_levels;

                    auto merge_sync_start = CollectKStageProfile::Clock::now();
                    CU_CHECK(cuStreamSynchronize(nullptr));
                    level_profile.sync_ms = CollectKStageProfile::elapsed_ms(merge_sync_start);
                    if (profile.enabled)
                        profile.merge_sync_ms += level_profile.sync_ms;

                    if (!use_batched_compact_level || current_rows.size() == 2)
                        *h2d_transfers_out += static_cast<uint64_t>(pair_count);
                    const bool used_pointer_host_counts_carry_level =
                        use_carry_pointer_diagnostic
                        && !use_carry_pointer_device_counts_diagnostic
                        && has_carry
                        && use_batched_compact_level
                        && current_rows.size() != 2
                        && use_derived_level_descriptors;
                    if (!use_device_level_counts || current_rows.size() == 2 || used_pointer_host_counts_carry_level) {
                        *d2h_transfers_out += static_cast<uint64_t>(pair_count);
                        profile.metadata_fields_downloaded += static_cast<uint64_t>(pair_count);
                    }

                    if (has_carry) {
                        const bool use_derived_carry_alias_level =
                            use_derived_carry_alias_diagnostic
                            && use_batched_compact_level
                            && current_rows.size() != 2
                            && use_derived_level_descriptors
                            && derived_carry_alias_safe_next;
                        const bool use_pointer_carry_level =
                            (use_carry_pointer_diagnostic || use_carry_pointer_device_counts_diagnostic)
                            && !use_derived_carry_alias_diagnostic
                            && use_batched_compact_level
                            && current_rows.size() != 2
                            && use_derived_level_descriptors;
                        const bool use_pointer_host_counts_carry_level =
                            use_carry_pointer_diagnostic
                            && !use_carry_pointer_device_counts_diagnostic
                            && use_pointer_carry_level;
                        CUdeviceptr carry_output = (use_pointer_carry_level || use_derived_carry_alias_level)
                            ? current_rows.back()
                            : output_base + sizeof(int64_t) * output_segment_capacity * 2 * pair_count;
                        auto carry_copy_start = CollectKStageProfile::Clock::now();
                        bool copied_carry_payload = false;
                        if (!use_pointer_carry_level && !use_derived_carry_alias_level) {
                            CU_CHECK(cuMemcpyDtoD(
                                carry_output,
                                current_rows.back(),
                                sizeof(int64_t) * (use_device_level_counts ? segment_capacity : current_counts.back()) * 2));
                            copied_carry_payload = true;
                        }
                        if (use_device_level_counts) {
                            if (use_pointer_host_counts_carry_level) {
                                upload(next_counts_level_device, next_counts.data(), pair_count);
                                *h2d_transfers_out += static_cast<uint64_t>(pair_count);
                            }
                            CUdeviceptr carry_count_source =
                                current_counts_level_device + sizeof(size_t) * (current_rows.size() - 1);
                            CUdeviceptr carry_count_dest =
                                next_counts_level_device + sizeof(size_t) * pair_count;
                            CU_CHECK(cuMemcpyDtoD(carry_count_dest, carry_count_source, sizeof(size_t)));
                        }
                        level_profile.carry_copy_ms = CollectKStageProfile::elapsed_ms(carry_copy_start);
                        if (profile.enabled)
                            profile.carry_copy_ms += level_profile.carry_copy_ms;
                        ++merge_launches;
                        ++profile.carry_copies;
                        ++level_profile.carry_copies;
                        if (copied_carry_payload) {
                            ++profile.carry_payload_copies;
                            ++level_profile.carry_payload_copies;
                        }
                        next_rows.push_back(carry_output);
                        next_counts.push_back(current_counts.back());
                    }
                    profile.record_merge_level(level_profile);

                    if (current_rows.size() == 2) {
                        const size_t final_count = next_counts.front();
                        *emitted_count_out = final_count;
                        *overflowed_out = final_count > row_capacity ? 1u : 0u;
                        *internal_device_transfers_out += merge_launches;
                        profile.append(*emitted_count_out, *overflowed_out, *h2d_transfers_out,
                                       *d2h_transfers_out, *internal_device_transfers_out);
                        return;
                    }

                    current_rows = std::move(next_rows);
                    current_counts = std::move(next_counts);
                    if (use_device_level_counts)
                        std::swap(current_counts_level_device, next_counts_level_device);
                    segment_capacity = output_segment_capacity;
                    write_stage_b = !write_stage_b;
                    continue;
                }

                auto merge_launch_start = CollectKStageProfile::Clock::now();
                std::array<uint64_t, 64> merge_first_rows = {};
                std::array<uint64_t, 64> merge_second_rows = {};
                std::array<uint64_t, 64> merge_output_rows = {};
                std::array<size_t, 64> merge_first_counts = {};
                std::array<size_t, 64> merge_second_counts = {};
                for (size_t pair_index = 0; pair_index < pair_count; ++pair_index) {
                    CUdeviceptr pair_output = output_base + sizeof(int64_t) * output_segment_capacity * 2 * pair_index;
                    merge_first_rows[pair_index] = static_cast<uint64_t>(current_rows[pair_index * 2]);
                    merge_second_rows[pair_index] = static_cast<uint64_t>(current_rows[pair_index * 2 + 1]);
                    merge_output_rows[pair_index] = static_cast<uint64_t>(pair_output);
                    merge_first_counts[pair_index] = current_counts[pair_index * 2];
                    merge_second_counts[pair_index] = current_counts[pair_index * 2 + 1];
                }
                upload(merge_first_rows_device.ptr, merge_first_rows.data(), pair_count);
                upload(merge_second_rows_device.ptr, merge_second_rows.data(), pair_count);
                upload(merge_output_rows_device.ptr, merge_output_rows.data(), pair_count);
                upload(merge_first_counts_device.ptr, merge_first_counts.data(), pair_count);
                upload(merge_second_counts_device.ptr, merge_second_counts.data(), pair_count);
                *h2d_transfers_out += static_cast<uint64_t>(pair_count * 5);
                launch_merge_level(pair_count, output_segment_capacity);
                ++merge_launches;
                level_profile.launch_ms = CollectKStageProfile::elapsed_ms(merge_launch_start);
                if (profile.enabled)
                    profile.merge_launch_ms += level_profile.launch_ms;
                profile.merge_launches += 1;
                ++profile.merge_levels;
                auto merge_sync_start = CollectKStageProfile::Clock::now();
                CU_CHECK(cuStreamSynchronize(nullptr));
                level_profile.sync_ms = CollectKStageProfile::elapsed_ms(merge_sync_start);
                if (profile.enabled)
                    profile.merge_sync_ms += level_profile.sync_ms;

                std::array<size_t, 64> merge_emitted = {};
                std::array<uint32_t, 64> merge_overflowed = {};
                auto merge_metadata_start = CollectKStageProfile::Clock::now();
                download(merge_emitted.data(), merge_emitted_device.ptr, pair_count);
                download(merge_overflowed.data(), merge_overflowed_device.ptr, pair_count);
                level_profile.metadata_ms = CollectKStageProfile::elapsed_ms(merge_metadata_start);
                if (profile.enabled)
                    profile.merge_metadata_download_ms += level_profile.metadata_ms;
                *d2h_transfers_out += static_cast<uint64_t>(pair_count * 2);
                profile.metadata_fields_downloaded += static_cast<uint64_t>(pair_count * 2);

                std::vector<CUdeviceptr> next_rows;
                std::vector<size_t> next_counts;
                next_rows.reserve(pair_count + (has_carry ? 1 : 0));
                next_counts.reserve(pair_count + (has_carry ? 1 : 0));
                for (size_t pair_index = 0; pair_index < pair_count; ++pair_index) {
                    if (merge_overflowed[pair_index])
                        throw std::runtime_error("row_width=2 pair collect unexpectedly overflowed");
                    next_rows.push_back(output_base + sizeof(int64_t) * output_segment_capacity * 2 * pair_index);
                    next_counts.push_back(merge_emitted[pair_index]);
                }
                if (has_carry) {
                    CUdeviceptr carry_output =
                        output_base + sizeof(int64_t) * output_segment_capacity * 2 * pair_count;
                    auto carry_copy_start = CollectKStageProfile::Clock::now();
                    CU_CHECK(cuMemcpyDtoD(
                        carry_output,
                        current_rows.back(),
                        sizeof(int64_t) * current_counts.back() * 2));
                    level_profile.carry_copy_ms = CollectKStageProfile::elapsed_ms(carry_copy_start);
                    if (profile.enabled)
                        profile.carry_copy_ms += level_profile.carry_copy_ms;
                    ++merge_launches;
                    ++profile.carry_copies;
                    ++level_profile.carry_copies;
                    ++profile.carry_payload_copies;
                    ++level_profile.carry_payload_copies;
                    next_rows.push_back(carry_output);
                    next_counts.push_back(current_counts.back());
                }
                profile.record_merge_level(level_profile);

                current_rows = std::move(next_rows);
                current_counts = std::move(next_counts);
                segment_capacity = output_segment_capacity;
                write_stage_b = !write_stage_b;
            }

            CUdeviceptr final_source = current_rows.front();
            const size_t final_count = current_counts.front();
            *emitted_count_out = final_count;
            *overflowed_out = 0;
            if (final_count > row_capacity) {
                *overflowed_out = 1;
                *internal_device_transfers_out += merge_launches;
                profile.append(*emitted_count_out, *overflowed_out, *h2d_transfers_out,
                               *d2h_transfers_out, *internal_device_transfers_out);
                return;
            }
            auto final_copy_start = CollectKStageProfile::Clock::now();
            CU_CHECK(cuMemcpyDtoD(rows_out, final_source, sizeof(int64_t) * final_count * 2));
            profile.add_since(profile.final_copy_ms, final_copy_start);
            ++profile.final_copies;
            *internal_device_transfers_out += merge_launches + 1;
            profile.append(*emitted_count_out, *overflowed_out, *h2d_transfers_out,
                           *d2h_transfers_out, *internal_device_transfers_out);
            return;
        }

        profile.native_path = "dynamic_row_width_single_thread_fallback";
        auto module_start = CollectKStageProfile::Clock::now();
        std::call_once(g_collect_k_i64.init, [&]() {
            std::string ptx = compile_to_ptx(
                kCollectKBoundedI64KernelSrc,
                "collect_k_bounded_i64_kernel.cu");
            CU_CHECK(cuModuleLoadData(&g_collect_k_i64.module, ptx.c_str()));
            CU_CHECK(cuModuleGetFunction(
                &g_collect_k_i64.fn,
                g_collect_k_i64.module,
                "collect_k_bounded_i64"));
        });
        profile.add_since(profile.module_load_ms, module_start);

        auto allocation_start = CollectKStageProfile::Clock::now();
        DevPtr emitted_device(sizeof(size_t));
        DevPtr overflowed_device(sizeof(uint32_t));
        CUdeviceptr candidate_rows = static_cast<CUdeviceptr>(candidate_rows_device_ptr);
        CUdeviceptr rows_out = static_cast<CUdeviceptr>(rows_out_device_ptr);
        profile.add_since(profile.allocation_ms, allocation_start);
        void* args[] = {
            &candidate_rows,
            &candidate_count,
            &row_width,
            &rows_out,
            &row_capacity,
            &emitted_device.ptr,
            &overflowed_device.ptr,
        };
        auto sort_launch_start = CollectKStageProfile::Clock::now();
        CU_CHECK(cuLaunchKernel(
            g_collect_k_i64.fn,
            1, 1, 1,
            1, 1, 1,
            0, nullptr, args, nullptr));
        profile.add_since(profile.sort_launch_ms, sort_launch_start);
        profile.sort_launches = 1;
        auto sort_sync_start = CollectKStageProfile::Clock::now();
        CU_CHECK(cuStreamSynchronize(nullptr));
        profile.add_since(profile.sort_sync_ms, sort_sync_start);

        auto metadata_start = CollectKStageProfile::Clock::now();
        download(emitted_count_out, emitted_device.ptr, 1);
        download(overflowed_out, overflowed_device.ptr, 1);
        profile.add_since(profile.tile_metadata_download_ms, metadata_start);
        *d2h_transfers_out += 2;
        profile.metadata_fields_downloaded += 2;
        profile.append(*emitted_count_out, *overflowed_out, *h2d_transfers_out,
                       *d2h_transfers_out, *internal_device_transfers_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_segment_polygon_anyhit_rows_2d(
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy, size_t vertex_xy_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!polygons && polygon_count != 0)
            throw std::runtime_error("polygons pointer must not be null when polygon_count is nonzero");
        if (!vertices_xy && vertex_xy_count != 0)
            throw std::runtime_error("vertices_xy pointer must not be null when vertex_xy_count is nonzero");
        if (polygon_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("polygon count exceeds uint32 primitive limit");
        *prepared_out = nullptr;
        *prepared_out = prepare_segment_polygon_anyhit_rows_2d_optix(
            polygons, polygon_count, vertices_xy, vertex_xy_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_segment_polygon_anyhit_rows_2d(
        void* prepared,
        const RtdlSegment* segments, size_t segment_count,
        RtdlSegmentPolygonAnyHitRow* rows_out, size_t output_capacity,
        size_t* emitted_count_out, uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_segment_polygon_anyhit_rows_2d_optix(
            reinterpret_cast<PreparedSegmentPolygonAnyhitRows2D*>(prepared),
            segments, segment_count, rows_out, output_capacity,
            emitted_count_out, overflowed_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_segment_polygon_anyhit_rows_2d(void* prepared)
{
    delete reinterpret_cast<PreparedSegmentPolygonAnyhitRows2D*>(prepared);
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
        const char* mode = std::getenv("RTDL_OPTIX_GRAPH_MODE");
        if (mode != nullptr && std::strcmp(mode, "native") == 0) {
            run_bfs_expand_optix_graph_ray(
                row_offsets, row_offset_count,
                column_indices, column_index_count,
                frontier, frontier_count,
                visited_vertices, visited_count,
                dedupe,
                rows_out, row_count_out);
        } else {
            run_bfs_expand_optix_host_indexed(
                row_offsets, row_offset_count,
                column_indices, column_index_count,
                frontier, frontier_count,
                visited_vertices, visited_count,
                dedupe,
                rows_out, row_count_out);
        }
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
        const char* mode = std::getenv("RTDL_OPTIX_GRAPH_MODE");
        if (mode != nullptr && std::strcmp(mode, "native") == 0) {
            run_triangle_probe_optix_graph_ray(
                row_offsets, row_offset_count,
                column_indices, column_index_count,
                seeds, seed_count,
                enforce_id_ascending,
                unique,
                rows_out, row_count_out);
        } else {
            run_triangle_probe_optix_host_indexed(
                row_offsets, row_offset_count,
                column_indices, column_index_count,
                seeds, seed_count,
                enforce_id_ascending,
                unique,
                rows_out, row_count_out);
        }
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

static void rtdl_optix_fill_db_compact_summary_phase(RtdlDbCompactSummaryResult& result)
{
    result.traversal = g_optix_last_db_traversal_s;
    result.bitset_copyback = g_optix_last_db_bitset_copy_s;
    result.exact_filter = g_optix_last_db_exact_filter_s;
    result.output_pack = g_optix_last_db_output_pack_s;
    result.raw_candidate_count = g_optix_last_db_raw_candidate_count;
    result.emitted_count = g_optix_last_db_emitted_count;
}

extern "C" void rtdl_optix_db_compact_summary_results_destroy(
        RtdlDbCompactSummaryResult* results,
        size_t result_count)
{
    if (!results) {
        return;
    }
    for (size_t index = 0; index < result_count; ++index) {
        std::free(results[index].count_rows);
        std::free(results[index].sum_rows);
    }
    std::free(results);
}

extern "C" int rtdl_optix_db_dataset_compact_summary_batch(
        RtdlOptixDbDataset* dataset,
        const RtdlDbCompactSummaryRequest* requests,
        size_t request_count,
        RtdlDbCompactSummaryResult** results_out,
        size_t* result_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!dataset) {
            throw std::runtime_error("OptiX prepared DB dataset must not be null");
        }
        if (!results_out || !result_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (request_count > 0 && !requests) {
            throw std::runtime_error("compact summary request pointer must not be null when request_count > 0");
        }
        *results_out = nullptr;
        *result_count_out = 0;

        auto* impl = reinterpret_cast<OptixDbDatasetImpl*>(dataset);
        std::vector<RtdlDbCompactSummaryResult> results(request_count);
        try {
            for (size_t index = 0; index < request_count; ++index) {
                const RtdlDbCompactSummaryRequest& request = requests[index];
                RtdlDbCompactSummaryResult& result = results[index];
                result.operation = request.operation;
                if (request.operation == kRtdlDbCompactSummaryScanCount) {
                    run_db_conjunctive_scan_count_optix_prepared(
                        impl,
                        request.clauses,
                        request.clause_count,
                        &result.scalar_value);
                    rtdl_optix_fill_db_compact_summary_phase(result);
                } else if (request.operation == kRtdlDbCompactSummaryGroupedCount) {
                    if (!request.group_key_field) {
                        throw std::runtime_error("grouped_count compact summary requires group_key_field");
                    }
                    run_db_grouped_count_optix_prepared(
                        impl,
                        request.clauses,
                        request.clause_count,
                        request.group_key_field,
                        &result.count_rows,
                        &result.count_row_count);
                    rtdl_optix_fill_db_compact_summary_phase(result);
                } else if (request.operation == kRtdlDbCompactSummaryGroupedSum) {
                    if (!request.group_key_field || !request.value_field) {
                        throw std::runtime_error("grouped_sum compact summary requires group_key_field and value_field");
                    }
                    run_db_grouped_sum_optix_prepared(
                        impl,
                        request.clauses,
                        request.clause_count,
                        request.group_key_field,
                        request.value_field,
                        &result.sum_rows,
                        &result.sum_row_count);
                    rtdl_optix_fill_db_compact_summary_phase(result);
                } else {
                    throw std::runtime_error("unsupported DB compact-summary batch operation");
                }
            }
        } catch (...) {
            for (RtdlDbCompactSummaryResult& result : results) {
                std::free(result.count_rows);
                std::free(result.sum_rows);
                result.count_rows = nullptr;
                result.sum_rows = nullptr;
            }
            throw;
        }

        auto* out = static_cast<RtdlDbCompactSummaryResult*>(
            std::calloc(results.size(), sizeof(RtdlDbCompactSummaryResult)));
        if (!out && !results.empty()) {
            for (RtdlDbCompactSummaryResult& result : results) {
                std::free(result.count_rows);
                std::free(result.sum_rows);
                result.count_rows = nullptr;
                result.sum_rows = nullptr;
            }
            throw std::bad_alloc();
        }
        if (!results.empty()) {
            std::memcpy(out, results.data(), sizeof(RtdlDbCompactSummaryResult) * results.size());
        }
        *results_out = out;
        *result_count_out = results.size();
    }, error_out, error_size);
}

extern "C" void rtdl_optix_free_rows(void* rows) {
    std::free(rows);
}

static void ensure_collect_k_row_width2_final_compact_kernels()
{
    std::call_once(g_collect_k_i64_row_width2_final_materialize.init, [&]() {
        std::string ptx = compile_to_ptx(
            kCollectKBoundedI64RowWidth2FinalCompactKernelSrc,
            "collect_k_bounded_i64_row_width2_final_compact_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_final_materialize.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_materialize.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_materialize"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_materialize_counts.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_materialize_counts"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_mark_counts.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_mark_counts"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_mark_counts_counts.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_mark_counts_counts"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_compact.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_compact"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_compact_counts.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_compact_counts"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_materialize_level.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_materialize_level"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_materialize_level_derived.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_materialize_level_derived"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_materialize_level_counts_pointers.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_materialize_level_counts_pointers"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_mark_counts_level.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_mark_counts_level"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_mark_counts_level_counts"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_mark_counts_level_counts_pointers.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_mark_counts_level_counts_pointers"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_materialize_mark_counts_level_counts.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_materialize_mark_counts_level_counts"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_compact_level.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_compact_level"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_compact_level_derived.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_compact_level_derived"));
        CU_CHECK(cuModuleGetFunction(
            &g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_final_prefix_offsets_level"));
    });
}

extern "C" int rtdl_optix_cuda_graph_replay_probe(
        size_t repeats,
        size_t commands_per_replay,
        double* direct_ms_out,
        double* graph_ms_out,
        uint32_t* final_value_out,
        char* error_out,
        size_t error_size)
{
    return handle_native_call([&]() {
        if (!direct_ms_out || !graph_ms_out || !final_value_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (repeats == 0) {
            repeats = 1;
        }
        if (commands_per_replay == 0) {
            commands_per_replay = 1;
        }

        CUdeviceptr device_value = 0;
        CUstream stream = nullptr;
        CUgraph graph = nullptr;
        CUgraphExec graph_exec = nullptr;
        try {
            (void)get_optix_context();
            CU_CHECK(cuMemAlloc(&device_value, sizeof(uint32_t)));
            CU_CHECK(cuStreamCreate(&stream, CU_STREAM_NON_BLOCKING));

            auto direct_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index) {
                for (size_t command = 0; command < commands_per_replay; ++command) {
                    CU_CHECK(cuMemsetD32Async(
                        device_value,
                        static_cast<unsigned int>(
                            0x12340000u
                            + static_cast<uint32_t>(
                                ((index * commands_per_replay) + command) & 0xffffu)),
                        1,
                        stream));
                }
            }
            CU_CHECK(cuStreamSynchronize(stream));
            *direct_ms_out = CollectKStageProfile::elapsed_ms(direct_start);

            CU_CHECK(cuStreamBeginCapture(stream, CU_STREAM_CAPTURE_MODE_GLOBAL));
            for (size_t command = 0; command < commands_per_replay; ++command) {
                CU_CHECK(cuMemsetD32Async(
                    device_value,
                    static_cast<unsigned int>(
                        0x5a5aa500u + static_cast<uint32_t>(command & 0xffu)),
                    1,
                    stream));
            }
            CU_CHECK(cuStreamEndCapture(stream, &graph));
            CU_CHECK(cuGraphInstantiate(&graph_exec, graph, 0));

            auto graph_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index) {
                CU_CHECK(cuGraphLaunch(graph_exec, stream));
            }
            CU_CHECK(cuStreamSynchronize(stream));
            *graph_ms_out = CollectKStageProfile::elapsed_ms(graph_start);

            CU_CHECK(cuMemcpyDtoH(final_value_out, device_value, sizeof(uint32_t)));
        } catch (...) {
            if (graph_exec)
                cuGraphExecDestroy(graph_exec);
            if (graph)
                cuGraphDestroy(graph);
            if (stream)
                cuStreamDestroy(stream);
            if (device_value)
                cuMemFree(device_value);
            throw;
        }

        if (graph_exec)
            CU_CHECK(cuGraphExecDestroy(graph_exec));
        if (graph)
            CU_CHECK(cuGraphDestroy(graph));
        if (stream)
            CU_CHECK(cuStreamDestroy(stream));
        if (device_value)
            CU_CHECK(cuMemFree(device_value));
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_k_level_graph_replay_probe(
        size_t repeats,
        size_t pair_count,
        size_t segment_capacity,
        double* direct_ms_out,
        double* graph_ms_out,
        uint64_t* first_pair_count_out,
        char* error_out,
        size_t error_size)
{
    return handle_native_call([&]() {
        if (!direct_ms_out || !graph_ms_out || !first_pair_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (repeats == 0) {
            repeats = 1;
        }
        if (pair_count == 0) {
            pair_count = 1;
        }
        if (segment_capacity == 0) {
            segment_capacity = 2048;
        }

        (void)get_optix_context();
        ensure_collect_k_row_width2_final_compact_kernels();

        size_t output_capacity = segment_capacity * 2;
        const unsigned threads = 256;
        size_t blocks_per_pair = (output_capacity + threads - 1) / threads;
        const unsigned total_blocks = static_cast<unsigned>(pair_count * blocks_per_pair);
        if (total_blocks == 0 || total_blocks > 512) {
            throw std::runtime_error("collect-k graph replay probe total block count must be in 1..512");
        }

        const size_t input_segments = pair_count * 2;
        const size_t current_values = input_segments * segment_capacity * 2;
        const size_t merged_values = pair_count * output_capacity * 2;
        std::vector<int64_t> host_rows(current_values);
        std::vector<size_t> host_counts(input_segments, segment_capacity);
        for (size_t segment = 0; segment < input_segments; ++segment) {
            int64_t* segment_rows = host_rows.data() + segment * segment_capacity * 2;
            for (size_t index = 0; index < segment_capacity; ++index) {
                segment_rows[index * 2] = static_cast<int64_t>(index);
                segment_rows[index * 2 + 1] = static_cast<int64_t>(segment);
            }
        }

        CUdeviceptr current_base = 0;
        CUdeviceptr current_counts = 0;
        CUdeviceptr merged_rows = 0;
        CUdeviceptr marks = 0;
        CUdeviceptr block_counts = 0;
        CUdeviceptr block_offsets = 0;
        CUdeviceptr pair_offsets = 0;
        CUdeviceptr pair_counts = 0;
        CUdeviceptr output_base = 0;
        CUstream stream = nullptr;
        CUgraph graph = nullptr;
        CUgraphExec graph_exec = nullptr;

        auto cleanup = [&]() {
            if (graph_exec)
                cuGraphExecDestroy(graph_exec);
            if (graph)
                cuGraphDestroy(graph);
            if (stream)
                cuStreamDestroy(stream);
            if (output_base)
                cuMemFree(output_base);
            if (pair_counts)
                cuMemFree(pair_counts);
            if (pair_offsets)
                cuMemFree(pair_offsets);
            if (block_offsets)
                cuMemFree(block_offsets);
            if (block_counts)
                cuMemFree(block_counts);
            if (marks)
                cuMemFree(marks);
            if (merged_rows)
                cuMemFree(merged_rows);
            if (current_counts)
                cuMemFree(current_counts);
            if (current_base)
                cuMemFree(current_base);
        };

        try {
            CU_CHECK(cuMemAlloc(&current_base, sizeof(int64_t) * current_values));
            CU_CHECK(cuMemAlloc(&current_counts, sizeof(size_t) * input_segments));
            CU_CHECK(cuMemAlloc(&merged_rows, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemAlloc(&marks, sizeof(uint32_t) * total_blocks * threads));
            CU_CHECK(cuMemAlloc(&block_counts, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&block_offsets, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&pair_offsets, sizeof(uint32_t) * pair_count));
            CU_CHECK(cuMemAlloc(&pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemAlloc(&output_base, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemcpyHtoD(current_base, host_rows.data(), sizeof(int64_t) * host_rows.size()));
            CU_CHECK(cuMemcpyHtoD(current_counts, host_counts.data(), sizeof(size_t) * host_counts.size()));
            CU_CHECK(cuStreamCreate(&stream, CU_STREAM_NON_BLOCKING));

            auto launch_sequence = [&]() {
                void* materialize_args[] = {
                    &current_base,
                    &current_counts,
                    &segment_capacity,
                    &output_capacity,
                    &merged_rows,
                    &pair_count,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    0, stream, materialize_args, nullptr));

                void* mark_args[] = {
                    &merged_rows,
                    &current_counts,
                    &output_capacity,
                    &pair_count,
                    &marks,
                    &block_counts,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, mark_args, nullptr));

                void* prefix_args[] = {
                    &block_counts,
                    &pair_count,
                    &blocks_per_pair,
                    &block_offsets,
                    &pair_offsets,
                    &pair_counts,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                    static_cast<unsigned>(pair_count), 1, 1,
                    1, 1, 1,
                    0, stream, prefix_args, nullptr));

                void* compact_args[] = {
                    &merged_rows,
                    &marks,
                    &block_offsets,
                    &pair_offsets,
                    &output_base,
                    &output_capacity,
                    &pair_count,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, compact_args, nullptr));
            };

            auto direct_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index) {
                launch_sequence();
            }
            CU_CHECK(cuStreamSynchronize(stream));
            *direct_ms_out = CollectKStageProfile::elapsed_ms(direct_start);

            CU_CHECK(cuStreamBeginCapture(stream, CU_STREAM_CAPTURE_MODE_GLOBAL));
            launch_sequence();
            CU_CHECK(cuStreamEndCapture(stream, &graph));
            CU_CHECK(cuGraphInstantiate(&graph_exec, graph, 0));

            auto graph_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index) {
                CU_CHECK(cuGraphLaunch(graph_exec, stream));
            }
            CU_CHECK(cuStreamSynchronize(stream));
            *graph_ms_out = CollectKStageProfile::elapsed_ms(graph_start);

            size_t first_pair_count = 0;
            CU_CHECK(cuMemcpyDtoH(&first_pair_count, pair_counts, sizeof(size_t)));
            *first_pair_count_out = static_cast<uint64_t>(first_pair_count);
        } catch (...) {
            cleanup();
            throw;
        }

        cleanup();
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_k_level_graph_update_probe(
        size_t repeats,
        size_t initial_pair_count,
        size_t target_pair_count,
        size_t segment_capacity,
        double* direct_ms_out,
        double* graph_update_ms_out,
        uint64_t* first_pair_count_out,
        uint64_t* kernel_node_count_out,
        char* error_out,
        size_t error_size)
{
    return handle_native_call([&]() {
        if (!direct_ms_out || !graph_update_ms_out || !first_pair_count_out || !kernel_node_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (repeats == 0) {
            repeats = 1;
        }
        if (initial_pair_count == 0) {
            initial_pair_count = 1;
        }
        if (target_pair_count == 0) {
            target_pair_count = 1;
        }
        if (segment_capacity == 0) {
            segment_capacity = 2048;
        }

        (void)get_optix_context();
        ensure_collect_k_row_width2_final_compact_kernels();

        size_t output_capacity = segment_capacity * 2;
        const unsigned threads = 256;
        size_t blocks_per_pair = (output_capacity + threads - 1) / threads;
        const size_t max_pair_count = std::max(initial_pair_count, target_pair_count);
        const unsigned max_total_blocks = static_cast<unsigned>(max_pair_count * blocks_per_pair);
        if (max_total_blocks == 0 || max_total_blocks > 512) {
            throw std::runtime_error("collect-k graph update probe total block count must be in 1..512");
        }

        const size_t input_segments = max_pair_count * 2;
        const size_t current_values = input_segments * segment_capacity * 2;
        const size_t merged_values = max_pair_count * output_capacity * 2;
        std::vector<int64_t> host_rows(current_values);
        std::vector<size_t> host_counts(input_segments, segment_capacity);
        for (size_t segment = 0; segment < input_segments; ++segment) {
            int64_t* segment_rows = host_rows.data() + segment * segment_capacity * 2;
            for (size_t index = 0; index < segment_capacity; ++index) {
                segment_rows[index * 2] = static_cast<int64_t>(index);
                segment_rows[index * 2 + 1] = static_cast<int64_t>(segment);
            }
        }

        CUdeviceptr current_base = 0;
        CUdeviceptr current_counts = 0;
        CUdeviceptr merged_rows = 0;
        CUdeviceptr marks = 0;
        CUdeviceptr block_counts = 0;
        CUdeviceptr block_offsets = 0;
        CUdeviceptr pair_offsets = 0;
        CUdeviceptr pair_counts = 0;
        CUdeviceptr output_base = 0;
        CUstream stream = nullptr;
        CUgraph graph = nullptr;
        CUgraphExec graph_exec = nullptr;

        auto cleanup = [&]() {
            if (graph_exec)
                cuGraphExecDestroy(graph_exec);
            if (graph)
                cuGraphDestroy(graph);
            if (stream)
                cuStreamDestroy(stream);
            if (output_base)
                cuMemFree(output_base);
            if (pair_counts)
                cuMemFree(pair_counts);
            if (pair_offsets)
                cuMemFree(pair_offsets);
            if (block_offsets)
                cuMemFree(block_offsets);
            if (block_counts)
                cuMemFree(block_counts);
            if (marks)
                cuMemFree(marks);
            if (merged_rows)
                cuMemFree(merged_rows);
            if (current_counts)
                cuMemFree(current_counts);
            if (current_base)
                cuMemFree(current_base);
        };

        try {
            CU_CHECK(cuMemAlloc(&current_base, sizeof(int64_t) * current_values));
            CU_CHECK(cuMemAlloc(&current_counts, sizeof(size_t) * input_segments));
            CU_CHECK(cuMemAlloc(&merged_rows, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemAlloc(&marks, sizeof(uint32_t) * max_total_blocks * threads));
            CU_CHECK(cuMemAlloc(&block_counts, sizeof(uint32_t) * max_total_blocks));
            CU_CHECK(cuMemAlloc(&block_offsets, sizeof(uint32_t) * max_total_blocks));
            CU_CHECK(cuMemAlloc(&pair_offsets, sizeof(uint32_t) * max_pair_count));
            CU_CHECK(cuMemAlloc(&pair_counts, sizeof(size_t) * max_pair_count));
            CU_CHECK(cuMemAlloc(&output_base, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemcpyHtoD(current_base, host_rows.data(), sizeof(int64_t) * host_rows.size()));
            CU_CHECK(cuMemcpyHtoD(current_counts, host_counts.data(), sizeof(size_t) * host_counts.size()));
            CU_CHECK(cuStreamCreate(&stream, CU_STREAM_NON_BLOCKING));

            auto launch_sequence = [&](size_t active_pair_count) {
                unsigned total_blocks = static_cast<unsigned>(active_pair_count * blocks_per_pair);
                void* materialize_args[] = {
                    &current_base,
                    &current_counts,
                    &segment_capacity,
                    &output_capacity,
                    &merged_rows,
                    &active_pair_count,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    0, stream, materialize_args, nullptr));

                void* mark_args[] = {
                    &merged_rows,
                    &current_counts,
                    &output_capacity,
                    &active_pair_count,
                    &marks,
                    &block_counts,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, mark_args, nullptr));

                void* prefix_args[] = {
                    &block_counts,
                    &active_pair_count,
                    &blocks_per_pair,
                    &block_offsets,
                    &pair_offsets,
                    &pair_counts,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                    static_cast<unsigned>(active_pair_count), 1, 1,
                    1, 1, 1,
                    0, stream, prefix_args, nullptr));

                void* compact_args[] = {
                    &merged_rows,
                    &marks,
                    &block_offsets,
                    &pair_offsets,
                    &output_base,
                    &output_capacity,
                    &active_pair_count,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, compact_args, nullptr));
            };

            auto direct_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index) {
                launch_sequence(target_pair_count);
            }
            CU_CHECK(cuStreamSynchronize(stream));
            *direct_ms_out = CollectKStageProfile::elapsed_ms(direct_start);

            CU_CHECK(cuStreamBeginCapture(stream, CU_STREAM_CAPTURE_MODE_GLOBAL));
            launch_sequence(initial_pair_count);
            CU_CHECK(cuStreamEndCapture(stream, &graph));
            CU_CHECK(cuGraphInstantiate(&graph_exec, graph, 0));

            size_t node_count = 0;
            CU_CHECK(cuGraphGetNodes(graph, nullptr, &node_count));
            std::vector<CUgraphNode> nodes(node_count);
            CU_CHECK(cuGraphGetNodes(graph, nodes.data(), &node_count));
            std::vector<CUgraphNode> kernel_nodes;
            for (CUgraphNode node : nodes) {
                CUgraphNodeType node_type;
                CU_CHECK(cuGraphNodeGetType(node, &node_type));
                if (node_type == CU_GRAPH_NODE_TYPE_KERNEL) {
                    kernel_nodes.push_back(node);
                }
            }
            if (kernel_nodes.size() != 4) {
                throw std::runtime_error("collect-k graph update probe expected exactly four kernel nodes");
            }
            *kernel_node_count_out = static_cast<uint64_t>(kernel_nodes.size());

            auto set_kernel_node = [&](size_t node_index,
                                       CUfunction function,
                                       unsigned grid_x,
                                       unsigned block_x,
                                       unsigned shared_mem,
                                       void** kernel_params) {
                CUDA_KERNEL_NODE_PARAMS params = {};
                params.func = function;
                params.gridDimX = grid_x;
                params.gridDimY = 1;
                params.gridDimZ = 1;
                params.blockDimX = block_x;
                params.blockDimY = 1;
                params.blockDimZ = 1;
                params.sharedMemBytes = shared_mem;
                params.kernelParams = kernel_params;
                params.extra = nullptr;
                CU_CHECK(cuGraphExecKernelNodeSetParams(graph_exec, kernel_nodes[node_index], &params));
            };

            unsigned target_total_blocks = static_cast<unsigned>(target_pair_count * blocks_per_pair);
            void* materialize_args[] = {
                &current_base,
                &current_counts,
                &segment_capacity,
                &output_capacity,
                &merged_rows,
                &target_pair_count,
                &blocks_per_pair,
            };
            set_kernel_node(
                0,
                g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
                target_total_blocks,
                threads,
                0,
                materialize_args);

            void* mark_args[] = {
                &merged_rows,
                &current_counts,
                &output_capacity,
                &target_pair_count,
                &marks,
                &block_counts,
                &blocks_per_pair,
            };
            set_kernel_node(
                1,
                g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
                target_total_blocks,
                threads,
                sizeof(uint32_t) * threads,
                mark_args);

            void* prefix_args[] = {
                &block_counts,
                &target_pair_count,
                &blocks_per_pair,
                &block_offsets,
                &pair_offsets,
                &pair_counts,
            };
            set_kernel_node(
                2,
                g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                static_cast<unsigned>(target_pair_count),
                1,
                0,
                prefix_args);

            void* compact_args[] = {
                &merged_rows,
                &marks,
                &block_offsets,
                &pair_offsets,
                &output_base,
                &output_capacity,
                &target_pair_count,
                &blocks_per_pair,
            };
            set_kernel_node(
                3,
                g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                target_total_blocks,
                threads,
                sizeof(uint32_t) * threads,
                compact_args);

            auto graph_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index) {
                CU_CHECK(cuGraphLaunch(graph_exec, stream));
            }
            CU_CHECK(cuStreamSynchronize(stream));
            *graph_update_ms_out = CollectKStageProfile::elapsed_ms(graph_start);

            size_t first_pair_count = 0;
            CU_CHECK(cuMemcpyDtoH(&first_pair_count, pair_counts, sizeof(size_t)));
            *first_pair_count_out = static_cast<uint64_t>(first_pair_count);
        } catch (...) {
            cleanup();
            throw;
        }

        cleanup();
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_k_fused_materialize_mark_probe(
        size_t repeats,
        size_t pair_count,
        size_t segment_capacity,
        double* reference_ms_out,
        double* fused_ms_out,
        uint64_t* mismatch_count_out,
        uint64_t* first_pair_count_out,
        char* error_out,
        size_t error_size)
{
    return handle_native_call([&]() {
        if (!reference_ms_out || !fused_ms_out || !mismatch_count_out || !first_pair_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (repeats == 0)
            repeats = 1;
        if (pair_count == 0)
            pair_count = 1;
        if (segment_capacity == 0)
            segment_capacity = 2048;

        (void)get_optix_context();
        ensure_collect_k_row_width2_final_compact_kernels();

        size_t output_capacity = segment_capacity * 2;
        const unsigned threads = 256;
        size_t blocks_per_pair = (output_capacity + threads - 1) / threads;
        const unsigned total_blocks = static_cast<unsigned>(pair_count * blocks_per_pair);
        if (total_blocks == 0 || total_blocks > 4096) {
            throw std::runtime_error("collect-k fused materialize+mark probe total block count must be in 1..4096");
        }

        const size_t input_segments = pair_count * 2;
        const size_t current_values = input_segments * segment_capacity * 2;
        const size_t merged_values = pair_count * output_capacity * 2;
        const size_t mark_values = static_cast<size_t>(total_blocks) * threads;
        std::vector<int64_t> host_rows(current_values);
        std::vector<size_t> host_counts(input_segments, segment_capacity);
        for (size_t pair = 0; pair < pair_count; ++pair) {
            int64_t* first_rows = host_rows.data() + (pair * 2) * segment_capacity * 2;
            int64_t* second_rows = host_rows.data() + (pair * 2 + 1) * segment_capacity * 2;
            for (size_t index = 0; index < segment_capacity; ++index) {
                const int64_t value0 = static_cast<int64_t>(index);
                const int64_t value1 = static_cast<int64_t>(index % 7);
                first_rows[index * 2] = value0;
                first_rows[index * 2 + 1] = value1;
                second_rows[index * 2] = value0;
                second_rows[index * 2 + 1] = value1;
            }
        }

        CUdeviceptr current_base = 0;
        CUdeviceptr current_counts = 0;
        CUdeviceptr ref_merged_rows = 0;
        CUdeviceptr fused_merged_rows = 0;
        CUdeviceptr ref_marks = 0;
        CUdeviceptr fused_marks = 0;
        CUdeviceptr ref_block_counts = 0;
        CUdeviceptr fused_block_counts = 0;
        CUdeviceptr ref_block_offsets = 0;
        CUdeviceptr fused_block_offsets = 0;
        CUdeviceptr ref_pair_offsets = 0;
        CUdeviceptr fused_pair_offsets = 0;
        CUdeviceptr ref_pair_counts = 0;
        CUdeviceptr fused_pair_counts = 0;
        CUdeviceptr ref_output_base = 0;
        CUdeviceptr fused_output_base = 0;
        CUstream stream = nullptr;

        auto cleanup = [&]() {
            if (stream)
                cuStreamDestroy(stream);
            if (fused_output_base)
                cuMemFree(fused_output_base);
            if (ref_output_base)
                cuMemFree(ref_output_base);
            if (fused_pair_counts)
                cuMemFree(fused_pair_counts);
            if (ref_pair_counts)
                cuMemFree(ref_pair_counts);
            if (fused_pair_offsets)
                cuMemFree(fused_pair_offsets);
            if (ref_pair_offsets)
                cuMemFree(ref_pair_offsets);
            if (fused_block_offsets)
                cuMemFree(fused_block_offsets);
            if (ref_block_offsets)
                cuMemFree(ref_block_offsets);
            if (fused_block_counts)
                cuMemFree(fused_block_counts);
            if (ref_block_counts)
                cuMemFree(ref_block_counts);
            if (fused_marks)
                cuMemFree(fused_marks);
            if (ref_marks)
                cuMemFree(ref_marks);
            if (fused_merged_rows)
                cuMemFree(fused_merged_rows);
            if (ref_merged_rows)
                cuMemFree(ref_merged_rows);
            if (current_counts)
                cuMemFree(current_counts);
            if (current_base)
                cuMemFree(current_base);
        };

        try {
            CU_CHECK(cuMemAlloc(&current_base, sizeof(int64_t) * current_values));
            CU_CHECK(cuMemAlloc(&current_counts, sizeof(size_t) * input_segments));
            CU_CHECK(cuMemAlloc(&ref_merged_rows, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemAlloc(&fused_merged_rows, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemAlloc(&ref_marks, sizeof(uint32_t) * mark_values));
            CU_CHECK(cuMemAlloc(&fused_marks, sizeof(uint32_t) * mark_values));
            CU_CHECK(cuMemAlloc(&ref_block_counts, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&fused_block_counts, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&ref_block_offsets, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&fused_block_offsets, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&ref_pair_offsets, sizeof(uint32_t) * pair_count));
            CU_CHECK(cuMemAlloc(&fused_pair_offsets, sizeof(uint32_t) * pair_count));
            CU_CHECK(cuMemAlloc(&ref_pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemAlloc(&fused_pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemAlloc(&ref_output_base, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemAlloc(&fused_output_base, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemcpyHtoD(current_base, host_rows.data(), sizeof(int64_t) * host_rows.size()));
            CU_CHECK(cuMemcpyHtoD(current_counts, host_counts.data(), sizeof(size_t) * host_counts.size()));
            CU_CHECK(cuStreamCreate(&stream, CU_STREAM_NON_BLOCKING));

            auto launch_reference = [&]() {
                void* materialize_args[] = {
                    &current_base,
                    &current_counts,
                    &segment_capacity,
                    &output_capacity,
                    &ref_merged_rows,
                    &pair_count,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    0, stream, materialize_args, nullptr));

                void* mark_args[] = {
                    &ref_merged_rows,
                    &current_counts,
                    &output_capacity,
                    &pair_count,
                    &ref_marks,
                    &ref_block_counts,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, mark_args, nullptr));

                void* prefix_args[] = {
                    &ref_block_counts,
                    &pair_count,
                    &blocks_per_pair,
                    &ref_block_offsets,
                    &ref_pair_offsets,
                    &ref_pair_counts,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                    static_cast<unsigned>(pair_count), 1, 1,
                    1, 1, 1,
                    0, stream, prefix_args, nullptr));

                void* compact_args[] = {
                    &ref_merged_rows,
                    &ref_marks,
                    &ref_block_offsets,
                    &ref_pair_offsets,
                    &ref_output_base,
                    &output_capacity,
                    &pair_count,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, compact_args, nullptr));
            };

            auto launch_fused = [&]() {
                CU_CHECK(cuMemsetD32Async(fused_marks, 0, mark_values, stream));
                CU_CHECK(cuMemsetD32Async(fused_block_counts, 0, total_blocks, stream));
                void* fused_args[] = {
                    &current_base,
                    &current_counts,
                    &segment_capacity,
                    &output_capacity,
                    &fused_merged_rows,
                    &pair_count,
                    &fused_marks,
                    &fused_block_counts,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_materialize_mark_counts_level_counts.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    0, stream, fused_args, nullptr));

                void* prefix_args[] = {
                    &fused_block_counts,
                    &pair_count,
                    &blocks_per_pair,
                    &fused_block_offsets,
                    &fused_pair_offsets,
                    &fused_pair_counts,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                    static_cast<unsigned>(pair_count), 1, 1,
                    1, 1, 1,
                    0, stream, prefix_args, nullptr));

                void* compact_args[] = {
                    &fused_merged_rows,
                    &fused_marks,
                    &fused_block_offsets,
                    &fused_pair_offsets,
                    &fused_output_base,
                    &output_capacity,
                    &pair_count,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                    total_blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, compact_args, nullptr));
            };

            auto ref_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index)
                launch_reference();
            CU_CHECK(cuStreamSynchronize(stream));
            *reference_ms_out = CollectKStageProfile::elapsed_ms(ref_start);

            auto fused_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index)
                launch_fused();
            CU_CHECK(cuStreamSynchronize(stream));
            *fused_ms_out = CollectKStageProfile::elapsed_ms(fused_start);

            launch_reference();
            launch_fused();
            CU_CHECK(cuStreamSynchronize(stream));

            std::vector<size_t> ref_counts(pair_count);
            std::vector<size_t> fused_counts(pair_count);
            std::vector<int64_t> ref_rows(merged_values);
            std::vector<int64_t> fused_rows(merged_values);
            CU_CHECK(cuMemcpyDtoH(ref_counts.data(), ref_pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemcpyDtoH(fused_counts.data(), fused_pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemcpyDtoH(ref_rows.data(), ref_output_base, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemcpyDtoH(fused_rows.data(), fused_output_base, sizeof(int64_t) * merged_values));

            uint64_t mismatches = 0;
            for (size_t pair = 0; pair < pair_count; ++pair) {
                if (ref_counts[pair] != fused_counts[pair])
                    ++mismatches;
                const size_t compare_rows = std::min(ref_counts[pair], fused_counts[pair]);
                const size_t base = pair * output_capacity * 2;
                for (size_t row = 0; row < compare_rows; ++row) {
                    if (ref_rows[base + row * 2] != fused_rows[base + row * 2] ||
                        ref_rows[base + row * 2 + 1] != fused_rows[base + row * 2 + 1]) {
                        ++mismatches;
                    }
                }
            }
            *mismatch_count_out = mismatches;
            *first_pair_count_out = pair_count > 0 ? static_cast<uint64_t>(ref_counts[0]) : 0u;
        } catch (...) {
            cleanup();
            throw;
        }

        cleanup();
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_k_output_indexed_fused_materialize_mark_probe(
        size_t repeats,
        size_t pair_count,
        size_t segment_capacity,
        double* reference_ms_out,
        double* fused_ms_out,
        uint64_t* mismatch_count_out,
        uint64_t* first_pair_count_out,
        char* error_out,
        size_t error_size)
{
    return handle_native_call([&]() {
        if (!reference_ms_out || !fused_ms_out || !mismatch_count_out || !first_pair_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (repeats == 0)
            repeats = 1;
        if (pair_count == 0)
            pair_count = 1;
        if (segment_capacity == 0)
            segment_capacity = 2048;

        (void)get_optix_context();
        ensure_collect_k_row_width2_final_compact_kernels();

        size_t output_capacity = segment_capacity * 2;
        const unsigned threads = 256;
        size_t blocks_per_pair = (output_capacity + threads - 1) / threads;
        const unsigned total_blocks = static_cast<unsigned>(pair_count * blocks_per_pair);
        if (total_blocks == 0 || total_blocks > 4096) {
            throw std::runtime_error("collect-k output-indexed fused probe total block count must be in 1..4096");
        }

        const size_t input_segments = pair_count * 2;
        const size_t current_values = input_segments * segment_capacity * 2;
        const size_t merged_values = pair_count * output_capacity * 2;
        const size_t mark_values = static_cast<size_t>(total_blocks) * threads;
        std::vector<int64_t> host_rows(current_values);
        std::vector<size_t> host_counts(input_segments, segment_capacity);
        for (size_t pair = 0; pair < pair_count; ++pair) {
            int64_t* first_rows = host_rows.data() + (pair * 2) * segment_capacity * 2;
            int64_t* second_rows = host_rows.data() + (pair * 2 + 1) * segment_capacity * 2;
            for (size_t index = 0; index < segment_capacity; ++index) {
                const int64_t value0 = static_cast<int64_t>(index);
                const int64_t value1 = static_cast<int64_t>(index % 7);
                first_rows[index * 2] = value0;
                first_rows[index * 2 + 1] = value1;
                second_rows[index * 2] = value0;
                second_rows[index * 2 + 1] = value1;
            }
        }

        CUdeviceptr current_base = 0;
        CUdeviceptr current_counts = 0;
        CUdeviceptr ref_merged_rows = 0;
        CUdeviceptr fused_merged_rows = 0;
        CUdeviceptr ref_marks = 0;
        CUdeviceptr fused_marks = 0;
        CUdeviceptr ref_block_counts = 0;
        CUdeviceptr fused_block_counts = 0;
        CUdeviceptr ref_block_offsets = 0;
        CUdeviceptr fused_block_offsets = 0;
        CUdeviceptr ref_pair_offsets = 0;
        CUdeviceptr fused_pair_offsets = 0;
        CUdeviceptr ref_pair_counts = 0;
        CUdeviceptr fused_pair_counts = 0;
        CUdeviceptr ref_output_base = 0;
        CUdeviceptr fused_output_base = 0;
        CUstream stream = nullptr;

        auto cleanup = [&]() {
            if (stream)
                cuStreamDestroy(stream);
            if (fused_output_base)
                cuMemFree(fused_output_base);
            if (ref_output_base)
                cuMemFree(ref_output_base);
            if (fused_pair_counts)
                cuMemFree(fused_pair_counts);
            if (ref_pair_counts)
                cuMemFree(ref_pair_counts);
            if (fused_pair_offsets)
                cuMemFree(fused_pair_offsets);
            if (ref_pair_offsets)
                cuMemFree(ref_pair_offsets);
            if (fused_block_offsets)
                cuMemFree(fused_block_offsets);
            if (ref_block_offsets)
                cuMemFree(ref_block_offsets);
            if (fused_block_counts)
                cuMemFree(fused_block_counts);
            if (ref_block_counts)
                cuMemFree(ref_block_counts);
            if (fused_marks)
                cuMemFree(fused_marks);
            if (ref_marks)
                cuMemFree(ref_marks);
            if (fused_merged_rows)
                cuMemFree(fused_merged_rows);
            if (ref_merged_rows)
                cuMemFree(ref_merged_rows);
            if (current_counts)
                cuMemFree(current_counts);
            if (current_base)
                cuMemFree(current_base);
        };

        try {
            CU_CHECK(cuMemAlloc(&current_base, sizeof(int64_t) * current_values));
            CU_CHECK(cuMemAlloc(&current_counts, sizeof(size_t) * input_segments));
            CU_CHECK(cuMemAlloc(&ref_merged_rows, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemAlloc(&fused_merged_rows, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemAlloc(&ref_marks, sizeof(uint32_t) * mark_values));
            CU_CHECK(cuMemAlloc(&fused_marks, sizeof(uint32_t) * mark_values));
            CU_CHECK(cuMemAlloc(&ref_block_counts, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&fused_block_counts, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&ref_block_offsets, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&fused_block_offsets, sizeof(uint32_t) * total_blocks));
            CU_CHECK(cuMemAlloc(&ref_pair_offsets, sizeof(uint32_t) * pair_count));
            CU_CHECK(cuMemAlloc(&fused_pair_offsets, sizeof(uint32_t) * pair_count));
            CU_CHECK(cuMemAlloc(&ref_pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemAlloc(&fused_pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemAlloc(&ref_output_base, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemAlloc(&fused_output_base, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemcpyHtoD(current_base, host_rows.data(), sizeof(int64_t) * host_rows.size()));
            CU_CHECK(cuMemcpyHtoD(current_counts, host_counts.data(), sizeof(size_t) * host_counts.size()));
            CU_CHECK(cuStreamCreate(&stream, CU_STREAM_NON_BLOCKING));

            auto launch_reference = [&]() {
                void* materialize_args[] = {
                    &current_base, &current_counts, &segment_capacity, &output_capacity,
                    &ref_merged_rows, &pair_count, &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
                    total_blocks, 1, 1, threads, 1, 1, 0, stream, materialize_args, nullptr));

                void* mark_args[] = {
                    &ref_merged_rows, &current_counts, &output_capacity, &pair_count,
                    &ref_marks, &ref_block_counts, &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
                    total_blocks, 1, 1, threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, mark_args, nullptr));

                void* prefix_args[] = {
                    &ref_block_counts, &pair_count, &blocks_per_pair,
                    &ref_block_offsets, &ref_pair_offsets, &ref_pair_counts,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                    static_cast<unsigned>(pair_count), 1, 1, 1, 1, 1, 0, stream, prefix_args, nullptr));

                void* compact_args[] = {
                    &ref_merged_rows, &ref_marks, &ref_block_offsets, &ref_pair_offsets,
                    &ref_output_base, &output_capacity, &pair_count, &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                    total_blocks, 1, 1, threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, compact_args, nullptr));
            };

            auto launch_fused = [&]() {
                void* fused_args[] = {
                    &current_base, &current_counts, &segment_capacity, &output_capacity,
                    &fused_merged_rows, &pair_count, &fused_marks, &fused_block_counts,
                    &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts.fn,
                    total_blocks, 1, 1, threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, fused_args, nullptr));

                void* prefix_args[] = {
                    &fused_block_counts, &pair_count, &blocks_per_pair,
                    &fused_block_offsets, &fused_pair_offsets, &fused_pair_counts,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                    static_cast<unsigned>(pair_count), 1, 1, 1, 1, 1, 0, stream, prefix_args, nullptr));

                void* compact_args[] = {
                    &fused_merged_rows, &fused_marks, &fused_block_offsets, &fused_pair_offsets,
                    &fused_output_base, &output_capacity, &pair_count, &blocks_per_pair,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                    total_blocks, 1, 1, threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, compact_args, nullptr));
            };

            auto ref_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index)
                launch_reference();
            CU_CHECK(cuStreamSynchronize(stream));
            *reference_ms_out = CollectKStageProfile::elapsed_ms(ref_start);

            auto fused_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index)
                launch_fused();
            CU_CHECK(cuStreamSynchronize(stream));
            *fused_ms_out = CollectKStageProfile::elapsed_ms(fused_start);

            launch_reference();
            launch_fused();
            CU_CHECK(cuStreamSynchronize(stream));

            std::vector<size_t> ref_counts(pair_count);
            std::vector<size_t> fused_counts(pair_count);
            std::vector<int64_t> ref_rows(merged_values);
            std::vector<int64_t> fused_rows(merged_values);
            CU_CHECK(cuMemcpyDtoH(ref_counts.data(), ref_pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemcpyDtoH(fused_counts.data(), fused_pair_counts, sizeof(size_t) * pair_count));
            CU_CHECK(cuMemcpyDtoH(ref_rows.data(), ref_output_base, sizeof(int64_t) * merged_values));
            CU_CHECK(cuMemcpyDtoH(fused_rows.data(), fused_output_base, sizeof(int64_t) * merged_values));

            uint64_t mismatches = 0;
            for (size_t pair = 0; pair < pair_count; ++pair) {
                if (ref_counts[pair] != fused_counts[pair])
                    ++mismatches;
                const size_t compare_rows = std::min(ref_counts[pair], fused_counts[pair]);
                const size_t base = pair * output_capacity * 2;
                for (size_t row = 0; row < compare_rows; ++row) {
                    if (ref_rows[base + row * 2] != fused_rows[base + row * 2] ||
                        ref_rows[base + row * 2 + 1] != fused_rows[base + row * 2 + 1]) {
                        ++mismatches;
                    }
                }
            }
            *mismatch_count_out = mismatches;
            *first_pair_count_out = pair_count > 0 ? static_cast<uint64_t>(ref_counts[0]) : 0u;
        } catch (...) {
            cleanup();
            throw;
        }

        cleanup();
    }, error_out, error_size);
}
