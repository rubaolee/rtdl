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

int rtdl_vulkan_run_fixed_radius_neighbors(
        const RtdlPoint* query_points, size_t query_count,
        const RtdlPoint* search_points, size_t search_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
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
        run_fixed_radius_neighbors_vulkan(
            query_points, query_count,
            search_points, search_count,
            radius, k_max,
            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_fixed_radius_neighbors_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        const RtdlPoint3D* search_points, size_t search_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
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
        run_fixed_radius_neighbors_3d_vulkan(
            query_points, query_count,
            search_points, search_count,
            radius, k_max,
            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_knn_rows(
        const RtdlPoint* query_points, size_t query_count,
        const RtdlPoint* search_points, size_t search_count,
        size_t k,
        RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
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
        run_knn_rows_vulkan(
            query_points, query_count,
            search_points, search_count,
            k,
            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_knn_rows_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        const RtdlPoint3D* search_points, size_t search_count,
        size_t k,
        RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
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
        run_knn_rows_3d_vulkan(
            query_points, query_count,
            search_points, search_count,
            k,
            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_bfs_expand(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t column_index_count,
        const RtdlFrontierVertex* frontier, size_t frontier_count,
        const uint32_t* visited_vertices, size_t visited_count,
        uint32_t dedupe,
        RtdlBfsExpandRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (frontier_count == 0) return;
        run_bfs_expand_vulkan_host_indexed(
            row_offsets, row_offset_count,
            column_indices, column_index_count,
            frontier, frontier_count,
            visited_vertices, visited_count,
            dedupe,
            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_triangle_probe(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t column_index_count,
        const RtdlEdgeSeed* seeds, size_t seed_count,
        uint32_t enforce_id_ascending,
        uint32_t unique,
        RtdlTriangleRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (seed_count == 0) return;
        run_triangle_probe_vulkan_host_indexed(
            row_offsets, row_offset_count,
            column_indices, column_index_count,
            seeds, seed_count,
            enforce_id_ascending,
            unique,
            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_conjunctive_scan(
        const RtdlDbField* fields, size_t field_count,
        const RtdlDbScalar* row_values, size_t row_count,
        const RtdlDbClause* clauses, size_t clause_count,
        RtdlDbRowIdRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_db_conjunctive_scan_vulkan(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_grouped_count(
        const RtdlDbField* fields, size_t field_count,
        const RtdlDbScalar* row_values, size_t row_count,
        const RtdlDbClause* clauses, size_t clause_count,
        const char* group_key_field,
        RtdlDbGroupedCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_db_grouped_count_vulkan(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            group_key_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

int rtdl_vulkan_run_grouped_sum(
        const RtdlDbField* fields, size_t field_count,
        const RtdlDbScalar* row_values, size_t row_count,
        const RtdlDbClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlDbGroupedSumRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size) {
    return handle_call([&] {
        run_db_grouped_sum_vulkan(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            group_key_field,
            value_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

} // extern "C"
