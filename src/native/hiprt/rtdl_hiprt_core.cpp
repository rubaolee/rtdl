template <typename T>
void copy_host_to_device(DeviceAllocation& allocation, const std::vector<T>& values) {
    if (values.empty()) {
        return;
    }
    check_oro(
        "oroMemcpyHtoD",
        oroMemcpyHtoD(allocation.oro_ptr(), const_cast<T*>(values.data()), values.size() * sizeof(T)));
}

template <typename T>
void copy_device_to_host(std::vector<T>& values, const DeviceAllocation& allocation) {
    if (values.empty()) {
        return;
    }
    check_oro(
        "oroMemcpyDtoH",
        oroMemcpyDtoH(values.data(), allocation.oro_ptr(), values.size() * sizeof(T)));
}

struct PreparedRayHitcount3D {
    HiprtRuntime runtime;
    DeviceAllocation vertex_device;
    hiprtGeometry geometry{};
    oroFunction kernel{};

    PreparedRayHitcount3D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& vertex_device_in,
        hiprtGeometry geometry_in,
        oroFunction kernel_in)
        : runtime(std::move(runtime_in)),
          vertex_device(std::move(vertex_device_in)),
          geometry(geometry_in),
          kernel(kernel_in) {}

    ~PreparedRayHitcount3D() {
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedRayHitcount3D(const PreparedRayHitcount3D&) = delete;
    PreparedRayHitcount3D& operator=(const PreparedRayHitcount3D&) = delete;
    PreparedRayHitcount3D(PreparedRayHitcount3D&&) = delete;
    PreparedRayHitcount3D& operator=(PreparedRayHitcount3D&&) = delete;
};

struct PreparedFixedRadiusNeighbors3D {
    HiprtRuntime runtime;
    DeviceAllocation search_device;
    DeviceAllocation aabb_device;
    DeviceAllocation params_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction kernel{};
    size_t search_count{};

    PreparedFixedRadiusNeighbors3D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& search_device_in,
        DeviceAllocation&& aabb_device_in,
        DeviceAllocation&& params_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable func_table_in,
        oroFunction kernel_in,
        size_t search_count_in)
        : runtime(std::move(runtime_in)),
          search_device(std::move(search_device_in)),
          aabb_device(std::move(aabb_device_in)),
          params_device(std::move(params_device_in)),
          geometry(geometry_in),
          func_table(func_table_in),
          kernel(kernel_in),
          search_count(search_count_in) {}

    ~PreparedFixedRadiusNeighbors3D() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
            func_table = nullptr;
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedFixedRadiusNeighbors3D(const PreparedFixedRadiusNeighbors3D&) = delete;
    PreparedFixedRadiusNeighbors3D& operator=(const PreparedFixedRadiusNeighbors3D&) = delete;
    PreparedFixedRadiusNeighbors3D(PreparedFixedRadiusNeighbors3D&&) = delete;
    PreparedFixedRadiusNeighbors3D& operator=(PreparedFixedRadiusNeighbors3D&&) = delete;
};

struct PreparedGraphCSR {
    HiprtRuntime runtime;
    DeviceAllocation row_offset_device;
    DeviceAllocation column_device;
    DeviceAllocation edge_device;
    DeviceAllocation aabb_device;
    hiprtGeometry geometry{};
    hiprtFuncTable bfs_func_table{};
    hiprtFuncTable triangle_func_table{};
    oroFunction bfs_kernel{};
    oroFunction triangle_kernel{};
    uint32_t vertex_count{};
    uint32_t edge_count{};

    PreparedGraphCSR(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& row_offset_device_in,
        DeviceAllocation&& column_device_in,
        DeviceAllocation&& edge_device_in,
        DeviceAllocation&& aabb_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable bfs_func_table_in,
        hiprtFuncTable triangle_func_table_in,
        oroFunction bfs_kernel_in,
        oroFunction triangle_kernel_in,
        uint32_t vertex_count_in,
        uint32_t edge_count_in)
        : runtime(std::move(runtime_in)),
          row_offset_device(std::move(row_offset_device_in)),
          column_device(std::move(column_device_in)),
          edge_device(std::move(edge_device_in)),
          aabb_device(std::move(aabb_device_in)),
          geometry(geometry_in),
          bfs_func_table(bfs_func_table_in),
          triangle_func_table(triangle_func_table_in),
          bfs_kernel(bfs_kernel_in),
          triangle_kernel(triangle_kernel_in),
          vertex_count(vertex_count_in),
          edge_count(edge_count_in) {}

    ~PreparedGraphCSR() {
        if (bfs_func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, bfs_func_table);
            bfs_func_table = nullptr;
        }
        if (triangle_func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, triangle_func_table);
            triangle_func_table = nullptr;
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedGraphCSR(const PreparedGraphCSR&) = delete;
    PreparedGraphCSR& operator=(const PreparedGraphCSR&) = delete;
    PreparedGraphCSR(PreparedGraphCSR&&) = delete;
    PreparedGraphCSR& operator=(PreparedGraphCSR&&) = delete;
};

std::vector<hiprtFloat3> encode_triangle_vertices(const RtdlTriangle3D* triangles, size_t triangle_count) {
    std::vector<hiprtFloat3> vertices;
    vertices.reserve(triangle_count * 3);
    for (size_t i = 0; i < triangle_count; ++i) {
        vertices.push_back({static_cast<float>(triangles[i].x0), static_cast<float>(triangles[i].y0), static_cast<float>(triangles[i].z0)});
        vertices.push_back({static_cast<float>(triangles[i].x1), static_cast<float>(triangles[i].y1), static_cast<float>(triangles[i].z1)});
        vertices.push_back({static_cast<float>(triangles[i].x2), static_cast<float>(triangles[i].y2), static_cast<float>(triangles[i].z2)});
    }
    return vertices;
}

std::vector<RtdlHiprtRay3DDevice> encode_rays(const RtdlRay3D* rays, size_t ray_count) {
    std::vector<RtdlHiprtRay3DDevice> ray_values;
    ray_values.reserve(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        ray_values.push_back({
            rays[i].id,
            static_cast<float>(rays[i].ox),
            static_cast<float>(rays[i].oy),
            static_cast<float>(rays[i].oz),
            static_cast<float>(rays[i].dx),
            static_cast<float>(rays[i].dy),
            static_cast<float>(rays[i].dz),
            static_cast<float>(rays[i].tmax),
        });
    }
    return ray_values;
}

std::vector<RtdlHiprtRay2DDevice> encode_rays_2d(const RtdlRay2D* rays, size_t ray_count) {
    std::vector<RtdlHiprtRay2DDevice> values;
    values.reserve(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        values.push_back({
            rays[i].id,
            static_cast<float>(rays[i].ox),
            static_cast<float>(rays[i].oy),
            static_cast<float>(rays[i].dx),
            static_cast<float>(rays[i].dy),
            static_cast<float>(rays[i].tmax),
        });
    }
    return values;
}

std::vector<RtdlHiprtPoint2DDevice> encode_points_2d(const RtdlPoint* points, size_t point_count) {
    std::vector<RtdlHiprtPoint2DDevice> values;
    values.reserve(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        values.push_back({
            points[i].id,
            static_cast<float>(points[i].x),
            static_cast<float>(points[i].y),
        });
    }
    return values;
}

std::vector<RtdlHiprtTriangle2DDevice> encode_triangles_2d(const RtdlTriangle* triangles, size_t triangle_count) {
    std::vector<RtdlHiprtTriangle2DDevice> values;
    values.reserve(triangle_count);
    for (size_t i = 0; i < triangle_count; ++i) {
        values.push_back({
            triangles[i].id,
            static_cast<float>(triangles[i].x0),
            static_cast<float>(triangles[i].y0),
            static_cast<float>(triangles[i].x1),
            static_cast<float>(triangles[i].y1),
            static_cast<float>(triangles[i].x2),
            static_cast<float>(triangles[i].y2),
        });
    }
    return values;
}

std::vector<RtdlHiprtPolygonRefDevice> encode_polygon_refs_2d(const RtdlPolygonRef* polygons, size_t polygon_count) {
    std::vector<RtdlHiprtPolygonRefDevice> values;
    values.reserve(polygon_count);
    for (size_t i = 0; i < polygon_count; ++i) {
        values.push_back({polygons[i].id, polygons[i].vertex_offset, polygons[i].vertex_count});
    }
    return values;
}

std::vector<RtdlHiprtVertex2DDevice> encode_vertices_2d(const double* vertices_xy, size_t vertex_xy_count) {
    std::vector<RtdlHiprtVertex2DDevice> values;
    values.reserve(vertex_xy_count / 2);
    for (size_t i = 0; i + 1 < vertex_xy_count; i += 2) {
        values.push_back({static_cast<float>(vertices_xy[i]), static_cast<float>(vertices_xy[i + 1])});
    }
    return values;
}

std::vector<RtdlHiprtSegmentDevice> encode_segments(const RtdlSegment* segments, size_t segment_count) {
    std::vector<RtdlHiprtSegmentDevice> values;
    values.reserve(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
        values.push_back({
            segments[i].id,
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].x1),
            static_cast<float>(segments[i].y1),
        });
    }
    return values;
}

std::vector<RtdlHiprtPoint3DDevice> encode_points(const RtdlPoint3D* points, size_t point_count) {
    std::vector<RtdlHiprtPoint3DDevice> values;
    values.reserve(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        values.push_back({
            points[i].id,
            static_cast<float>(points[i].x),
            static_cast<float>(points[i].y),
            static_cast<float>(points[i].z),
        });
    }
    return values;
}

std::vector<RtdlHiprtAabb> encode_point_aabbs(const RtdlHiprtPoint3DDevice* points, size_t point_count, float radius) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        aabbs.push_back({
            {points[i].x - radius, points[i].y - radius, points[i].z - radius, 0.0f},
            {points[i].x + radius, points[i].y + radius, points[i].z + radius, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_point_2d_aabbs(const RtdlHiprtPoint2DDevice* points, size_t point_count, float radius) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(point_count);
    constexpr float eps = 1.0e-4f;
    const float z_pad = std::max(radius, eps);
    for (size_t i = 0; i < point_count; ++i) {
        aabbs.push_back({
            {points[i].x - radius, points[i].y - radius, -z_pad, 0.0f},
            {points[i].x + radius, points[i].y + radius, z_pad, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_segment_aabbs(const RtdlHiprtSegmentDevice* segments, size_t segment_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(segment_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < segment_count; ++i) {
        const float min_x = std::min(segments[i].x0, segments[i].x1);
        const float min_y = std::min(segments[i].y0, segments[i].y1);
        const float max_x = std::max(segments[i].x0, segments[i].x1);
        const float max_y = std::max(segments[i].y0, segments[i].y1);
        aabbs.push_back({
            {min_x - eps, min_y - eps, -eps, 0.0f},
            {max_x + eps, max_y + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_segment_expanded_aabbs(
    const RtdlHiprtSegmentDevice* segments,
    size_t segment_count,
    float radius) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(segment_count);
    constexpr float eps = 1.0e-4f;
    const float pad = radius + eps;
    for (size_t i = 0; i < segment_count; ++i) {
        const float min_x = std::min(segments[i].x0, segments[i].x1);
        const float min_y = std::min(segments[i].y0, segments[i].y1);
        const float max_x = std::max(segments[i].x0, segments[i].x1);
        const float max_y = std::max(segments[i].y0, segments[i].y1);
        aabbs.push_back({
            {min_x - pad, min_y - pad, -eps, 0.0f},
            {max_x + pad, max_y + pad, eps, 0.0f},
        });
    }
    return aabbs;
}

float global_point_segment_radius(
    const RtdlHiprtPoint2DDevice* points,
    size_t point_count,
    const RtdlHiprtSegmentDevice* segments,
    size_t segment_count) {
    float min_x = 0.0f;
    float max_x = 0.0f;
    float min_y = 0.0f;
    float max_y = 0.0f;
    bool initialized = false;
    auto add_point = [&](float x, float y) {
        if (!initialized) {
            min_x = max_x = x;
            min_y = max_y = y;
            initialized = true;
            return;
        }
        min_x = std::min(min_x, x);
        max_x = std::max(max_x, x);
        min_y = std::min(min_y, y);
        max_y = std::max(max_y, y);
    };
    for (size_t i = 0; i < point_count; ++i) {
        add_point(points[i].x, points[i].y);
    }
    for (size_t i = 0; i < segment_count; ++i) {
        add_point(segments[i].x0, segments[i].y0);
        add_point(segments[i].x1, segments[i].y1);
    }
    const float dx = max_x - min_x;
    const float dy = max_y - min_y;
    return std::sqrt(dx * dx + dy * dy) + 1.0e-4f;
}

std::vector<RtdlHiprtAabb> encode_triangle_2d_aabbs(const RtdlHiprtTriangle2DDevice* triangles, size_t triangle_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(triangle_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < triangle_count; ++i) {
        const float min_x = std::min({triangles[i].x0, triangles[i].x1, triangles[i].x2});
        const float min_y = std::min({triangles[i].y0, triangles[i].y1, triangles[i].y2});
        const float max_x = std::max({triangles[i].x0, triangles[i].x1, triangles[i].x2});
        const float max_y = std::max({triangles[i].y0, triangles[i].y1, triangles[i].y2});
        aabbs.push_back({
            {min_x - eps, min_y - eps, -eps, 0.0f},
            {max_x + eps, max_y + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_polygon_aabbs(
    const RtdlHiprtPolygonRefDevice* polygons,
    size_t polygon_count,
    const RtdlHiprtVertex2DDevice* vertices,
    size_t vertex_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(polygon_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < polygon_count; ++i) {
        if (polygons[i].vertex_count == 0 || polygons[i].vertex_offset + polygons[i].vertex_count > vertex_count) {
            throw std::runtime_error("polygon vertex range is invalid");
        }
        float min_x = vertices[polygons[i].vertex_offset].x;
        float max_x = min_x;
        float min_y = vertices[polygons[i].vertex_offset].y;
        float max_y = min_y;
        for (uint32_t j = 1; j < polygons[i].vertex_count; ++j) {
            const RtdlHiprtVertex2DDevice vertex = vertices[polygons[i].vertex_offset + j];
            min_x = std::min(min_x, vertex.x);
            max_x = std::max(max_x, vertex.x);
            min_y = std::min(min_y, vertex.y);
            max_y = std::max(max_y, vertex.y);
        }
        aabbs.push_back({
            {min_x - eps, min_y - eps, -eps, 0.0f},
            {max_x + eps, max_y + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_overlay_candidate_aabbs(
    const RtdlHiprtPolygonRefDevice* right_polygons,
    size_t right_count,
    const RtdlHiprtPolygonRefDevice* left_polygons,
    size_t left_count,
    const RtdlHiprtVertex2DDevice* left_vertices,
    size_t left_vertex_count) {
    if (left_count == 0) {
        return {};
    }
    constexpr float eps = 1.0e-4f;
    float min_x = 0.0f;
    float max_x = 0.0f;
    float min_y = 0.0f;
    float max_y = 0.0f;
    bool initialized = false;
    for (size_t i = 0; i < left_count; ++i) {
        if (left_polygons[i].vertex_count == 0 || left_polygons[i].vertex_offset >= left_vertex_count) {
            throw std::runtime_error("left polygon vertex range is invalid");
        }
        const RtdlHiprtVertex2DDevice vertex = left_vertices[left_polygons[i].vertex_offset];
        if (!initialized) {
            min_x = max_x = vertex.x;
            min_y = max_y = vertex.y;
            initialized = true;
        } else {
            min_x = std::min(min_x, vertex.x);
            max_x = std::max(max_x, vertex.x);
            min_y = std::min(min_y, vertex.y);
            max_y = std::max(max_y, vertex.y);
        }
    }
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(right_count);
    for (size_t i = 0; i < right_count; ++i) {
        if (right_polygons[i].vertex_count == 0) {
            throw std::runtime_error("right polygon vertex range is invalid");
        }
        aabbs.push_back({
            {min_x - eps, min_y - eps, -eps, 0.0f},
            {max_x + eps, max_y + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtGraphEdgeDevice> encode_graph_edges(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count) {
    if (row_offset_count != static_cast<size_t>(vertex_count) + 1u) {
        throw std::runtime_error("HIPRT bfs_discover row_offset_count must equal vertex_count + 1");
    }
    if (row_offset_count == 0 || row_offsets[0] != 0u) {
        throw std::runtime_error("HIPRT bfs_discover row_offsets must start at 0");
    }
    if (row_offsets[row_offset_count - 1u] != edge_count) {
        throw std::runtime_error("HIPRT bfs_discover final row_offset must equal edge_count");
    }

    std::vector<RtdlHiprtGraphEdgeDevice> edges;
    edges.reserve(edge_count);
    for (uint32_t src = 0; src < vertex_count; ++src) {
        const uint32_t begin = row_offsets[src];
        const uint32_t end = row_offsets[src + 1u];
        if (end < begin || end > edge_count) {
            throw std::runtime_error("HIPRT bfs_discover row_offsets must be non-decreasing and within edge_count");
        }
        for (uint32_t index = begin; index < end; ++index) {
            const uint32_t dst = column_indices[index];
            if (dst >= vertex_count) {
                throw std::runtime_error("HIPRT bfs_discover column_indices must be valid vertex IDs");
            }
            edges.push_back({src, dst});
        }
    }
    return edges;
}

std::vector<RtdlHiprtAabb> encode_graph_edge_source_aabbs(const RtdlHiprtGraphEdgeDevice* edges, size_t edge_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(edge_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < edge_count; ++i) {
        const float src = static_cast<float>(edges[i].src);
        aabbs.push_back({
            {src - eps, -eps, -eps, 0.0f},
            {src + eps, eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtAabb> encode_db_row_aabbs(size_t row_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(row_count);
    constexpr float eps = 0.25f;
    for (size_t i = 0; i < row_count; ++i) {
        const float row = static_cast<float>(i);
        aabbs.push_back({
            {row - eps, -eps, -eps, 0.0f},
            {row + eps, eps, eps, 0.0f},
        });
    }
    return aabbs;
}

size_t db_find_field_index_or_throw(const RtdlDbField* fields, size_t field_count, const char* name) {
    for (size_t index = 0; index < field_count; ++index) {
        if (std::strcmp(fields[index].name, name) == 0) {
            return index;
        }
    }
    throw std::runtime_error(std::string("DB field not found: ") + name);
}

bool db_scalar_is_numeric(const RtdlDbScalar& value) {
    return value.kind == RTDL_DB_KIND_INT64 || value.kind == RTDL_DB_KIND_FLOAT64 || value.kind == RTDL_DB_KIND_BOOL;
}

double db_scalar_as_double(const RtdlDbScalar& value) {
    if (value.kind == RTDL_DB_KIND_FLOAT64) {
        return value.double_value;
    }
    return static_cast<double>(value.int_value);
}

std::vector<RtdlHiprtDbClauseDevice> encode_db_clauses_for_device(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbClause* clauses,
    size_t clause_count) {
    std::vector<RtdlHiprtDbClauseDevice> output;
    output.reserve(clause_count);
    for (size_t i = 0; i < clause_count; ++i) {
        const size_t field_index = db_find_field_index_or_throw(fields, field_count, clauses[i].field);
        if (!db_scalar_is_numeric(clauses[i].value) ||
            (clauses[i].op == RTDL_DB_OP_BETWEEN && !db_scalar_is_numeric(clauses[i].value_hi))) {
            throw std::runtime_error("HIPRT DB first wave requires numeric or text-encoded predicate values");
        }
        output.push_back({
            static_cast<uint32_t>(field_index),
            clauses[i].op,
            clauses[i].value,
            clauses[i].value_hi,
        });
    }
    return output;
}

hiprtGeometry build_triangle_geometry(
    hiprtContext context,
    DeviceAllocation& vertex_device,
    size_t vertex_count,
    size_t triangle_count) {
    hiprtTriangleMeshPrimitive mesh{};
    mesh.triangleCount = static_cast<uint32_t>(triangle_count);
    mesh.triangleStride = 0;
    mesh.triangleIndices = nullptr;
    mesh.vertexCount = static_cast<uint32_t>(vertex_count);
    mesh.vertexStride = sizeof(hiprtFloat3);
    mesh.vertices = vertex_device.get();

    hiprtGeometryBuildInput geom_input{};
    geom_input.type = hiprtPrimitiveTypeTriangleMesh;
    geom_input.primitive.triangleMesh = mesh;

    hiprtBuildOptions options{};
    options.buildFlags = hiprtBuildFlagBitPreferFastBuild;
    size_t temp_size = 0;
    check_hiprt("hiprtGetGeometryBuildTemporaryBufferSize", hiprtGetGeometryBuildTemporaryBufferSize(context, geom_input, options, temp_size));
    DeviceAllocation temp_device(temp_size);
    hiprtGeometry geometry{};
    check_hiprt("hiprtCreateGeometry", hiprtCreateGeometry(context, geom_input, options, geometry));
    try {
        check_hiprt(
            "hiprtBuildGeometry",
            hiprtBuildGeometry(context, hiprtBuildOperationBuild, geom_input, options, temp_device.get(), 0, geometry));
    } catch (...) {
        if (geometry != nullptr) {
            hiprtDestroyGeometry(context, geometry);
        }
        throw;
    }
    return geometry;
}

hiprtGeometry build_aabb_geometry(
    hiprtContext context,
    DeviceAllocation& aabb_device,
    size_t aabb_count) {
    hiprtAABBListPrimitive list{};
    list.aabbCount = static_cast<uint32_t>(aabb_count);
    list.aabbStride = sizeof(RtdlHiprtAabb);
    list.aabbs = aabb_device.get();

    hiprtGeometryBuildInput geom_input{};
    geom_input.type = hiprtPrimitiveTypeAABBList;
    geom_input.primitive.aabbList = list;
    geom_input.geomType = 0;

    hiprtBuildOptions options{};
    options.buildFlags = hiprtBuildFlagBitPreferFastBuild;
    size_t temp_size = 0;
    check_hiprt("hiprtGetGeometryBuildTemporaryBufferSize", hiprtGetGeometryBuildTemporaryBufferSize(context, geom_input, options, temp_size));
    DeviceAllocation temp_device(temp_size);
    hiprtGeometry geometry{};
    check_hiprt("hiprtCreateGeometry", hiprtCreateGeometry(context, geom_input, options, geometry));
    try {
        check_hiprt(
            "hiprtBuildGeometry",
            hiprtBuildGeometry(context, hiprtBuildOperationBuild, geom_input, options, temp_device.get(), 0, geometry));
    } catch (...) {
        if (geometry != nullptr) {
            hiprtDestroyGeometry(context, geometry);
        }
        throw;
    }
    return geometry;
}

RtdlRayHitCountRow* copy_rows_to_heap(const std::vector<RtdlRayHitCountRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlRayHitCountRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlRayHitCountRow));
    }
    return reinterpret_cast<RtdlRayHitCountRow*>(rows);
}

RtdlLsiRow* copy_lsi_rows_to_heap(const std::vector<RtdlLsiRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlLsiRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlLsiRow));
    }
    return reinterpret_cast<RtdlLsiRow*>(rows);
}

RtdlPipRow* copy_pip_rows_to_heap(const std::vector<RtdlPipRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlPipRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlPipRow));
    }
    return reinterpret_cast<RtdlPipRow*>(rows);
}

RtdlOverlayRow* copy_overlay_rows_to_heap(const std::vector<RtdlOverlayRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlOverlayRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlOverlayRow));
    }
    return reinterpret_cast<RtdlOverlayRow*>(rows);
}

RtdlPointNearestSegmentRow* copy_pns_rows_to_heap(const std::vector<RtdlPointNearestSegmentRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlPointNearestSegmentRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlPointNearestSegmentRow));
    }
    return reinterpret_cast<RtdlPointNearestSegmentRow*>(rows);
}

RtdlSegmentPolygonHitCountRow* copy_segment_polygon_hitcount_rows_to_heap(
    const std::vector<RtdlSegmentPolygonHitCountRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlSegmentPolygonHitCountRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlSegmentPolygonHitCountRow));
    }
    return reinterpret_cast<RtdlSegmentPolygonHitCountRow*>(rows);
}

RtdlSegmentPolygonAnyHitRow* copy_segment_polygon_anyhit_rows_to_heap(
    const std::vector<RtdlSegmentPolygonAnyHitRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlSegmentPolygonAnyHitRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlSegmentPolygonAnyHitRow));
    }
    return reinterpret_cast<RtdlSegmentPolygonAnyHitRow*>(rows);
}

RtdlFixedRadiusNeighborRow* copy_frn_rows_to_heap(const std::vector<RtdlFixedRadiusNeighborRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlFixedRadiusNeighborRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlFixedRadiusNeighborRow));
    }
    return reinterpret_cast<RtdlFixedRadiusNeighborRow*>(rows);
}

RtdlBfsRow* copy_bfs_rows_to_heap(const std::vector<RtdlBfsRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlBfsRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlBfsRow));
    }
    return reinterpret_cast<RtdlBfsRow*>(rows);
}

RtdlTriangleRow* copy_triangle_rows_to_heap(const std::vector<RtdlTriangleRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlTriangleRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlTriangleRow));
    }
    return reinterpret_cast<RtdlTriangleRow*>(rows);
}

RtdlDbRowIdRow* copy_db_row_id_rows_to_heap(const std::vector<RtdlDbRowIdRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlDbRowIdRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlDbRowIdRow));
    }
    return reinterpret_cast<RtdlDbRowIdRow*>(rows);
}

RtdlDbGroupedCountRow* copy_db_grouped_count_rows_to_heap(const std::vector<RtdlDbGroupedCountRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlDbGroupedCountRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlDbGroupedCountRow));
    }
    return reinterpret_cast<RtdlDbGroupedCountRow*>(rows);
}

RtdlDbGroupedSumRow* copy_db_grouped_sum_rows_to_heap(const std::vector<RtdlDbGroupedSumRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlDbGroupedSumRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlDbGroupedSumRow));
    }
    return reinterpret_cast<RtdlDbGroupedSumRow*>(rows);
}

void run_prepared_ray_hitcount_3d(
    PreparedRayHitcount3D& prepared,
    const RtdlRay3D* rays,
    size_t ray_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out) {
    std::vector<RtdlHiprtRay3DDevice> ray_values = encode_rays(rays, ray_count);
    DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay3DDevice));
    copy_host_to_device(ray_device, ray_values);
    std::vector<RtdlRayHitCountRow> output(ray_count);
    DeviceAllocation output_device(output.size() * sizeof(RtdlRayHitCountRow));

    void* ray_device_ptr = ray_device.get();
    void* output_device_ptr = output_device.get();
    uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
    void* args[] = {&prepared.geometry, &ray_device_ptr, &ray_count_u32, &output_device_ptr};
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(output, output_device);

    *rows_out = copy_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* queries,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out) {
    if (k_max == 0) {
        throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    if (k_max > 64) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports k_max <= 64");
    }
    if (radius < 0.0) {
        throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (query_count > std::numeric_limits<uint32_t>::max() || search_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports at most 2^32-1 query/search points");
    }
    if (query_count != 0 && k_max > std::numeric_limits<size_t>::max() / query_count) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d output capacity overflow");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (search_count > 0 && search_points == nullptr) {
        throw std::runtime_error("search point pointer must not be null when search_count is nonzero");
    }
    if (query_count == 0 || search_count == 0) {
        std::vector<RtdlFixedRadiusNeighborRow> empty;
        *rows_out = copy_frn_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint3DDevice> query_values = encode_points(queries, query_count);
    std::vector<RtdlHiprtPoint3DDevice> search_values = encode_points(search_points, search_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_point_aabbs(search_values.data(), search_values.size(), static_cast<float>(radius));
    RtdlHiprtFixedRadiusParams params{static_cast<float>(radius)};

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation search_device(search_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtFixedRadiusParams));
    copy_host_to_device(query_device, query_values);
    copy_host_to_device(search_device, search_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointRadius3D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = search_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            fixed_radius_neighbors_3d_kernel_source(),
            "rtdl_hiprt_fixed_radius_neighbors_3d.cu",
            "RtdlFixedRadiusNeighbors3DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = query_count * static_cast<size_t>(k_max);
        std::vector<RtdlFixedRadiusNeighborRow> output(output_capacity);
        std::vector<uint32_t> counts(query_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlFixedRadiusNeighborRow));
        DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));

        void* query_device_ptr = query_device.get();
        void* search_device_ptr = search_device.get();
        void* output_device_ptr = output_device.get();
        void* counts_device_ptr = counts_device.get();
        void* params_device_ptr = params_device.get();
        uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &query_device_ptr,
            &search_device_ptr,
            &query_count_u32,
            &k_max,
            &output_device_ptr,
            &counts_device_ptr,
            &params_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        copy_device_to_host(counts, counts_device);

        std::vector<RtdlFixedRadiusNeighborRow> compacted;
        for (size_t query_index = 0; query_index < query_count; ++query_index) {
            uint32_t count = std::min(counts[query_index], k_max);
            size_t base = query_index * static_cast<size_t>(k_max);
            for (uint32_t rank = 0; rank < count; ++rank) {
                compacted.push_back(output[base + rank]);
            }
        }
        *rows_out = copy_frn_rows_to_heap(compacted);
        *row_count_out = compacted.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

std::unique_ptr<PreparedFixedRadiusNeighbors3D> prepare_fixed_radius_neighbors_3d(
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius) {
    if (radius < 0.0) {
        throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (search_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports at most 2^32-1 search points");
    }
    if (search_count > 0 && search_points == nullptr) {
        throw std::runtime_error("search point pointer must not be null when search_count is nonzero");
    }
    if (search_count == 0) {
        throw std::runtime_error("prepared HIPRT fixed_radius_neighbors_3d requires at least one search point");
    }

    std::vector<RtdlHiprtPoint3DDevice> search_values = encode_points(search_points, search_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_point_aabbs(search_values.data(), search_values.size(), static_cast<float>(radius));
    RtdlHiprtFixedRadiusParams params{static_cast<float>(radius)};

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation search_device(search_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtFixedRadiusParams));
    copy_host_to_device(search_device, search_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointRadius3D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = search_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            fixed_radius_neighbors_3d_kernel_source(),
            "rtdl_hiprt_fixed_radius_neighbors_3d.cu",
            "RtdlFixedRadiusNeighbors3DKernel",
            &func_name_set,
            1,
            1);
        auto prepared = std::make_unique<PreparedFixedRadiusNeighbors3D>(
            std::move(runtime),
            std::move(search_device),
            std::move(aabb_device),
            std::move(params_device),
            geometry,
            func_table,
            kernel,
            search_count);
        geometry = nullptr;
        func_table = nullptr;
        return prepared;
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
}

void run_prepared_fixed_radius_neighbors_3d(
    PreparedFixedRadiusNeighbors3D& prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out) {
    if (k_max == 0) {
        throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    if (k_max > 64) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports k_max <= 64");
    }
    if (query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d currently supports at most 2^32-1 query points");
    }
    if (query_count != 0 && k_max > std::numeric_limits<size_t>::max() / query_count) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_3d output capacity overflow");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (query_count == 0 || prepared.search_count == 0) {
        std::vector<RtdlFixedRadiusNeighborRow> empty;
        *rows_out = copy_frn_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint3DDevice> query_values = encode_points(queries, query_count);
    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    copy_host_to_device(query_device, query_values);

    const size_t output_capacity = query_count * static_cast<size_t>(k_max);
    std::vector<RtdlFixedRadiusNeighborRow> output(output_capacity);
    std::vector<uint32_t> counts(query_count);
    DeviceAllocation output_device(output.size() * sizeof(RtdlFixedRadiusNeighborRow));
    DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));

    void* query_device_ptr = query_device.get();
    void* search_device_ptr = prepared.search_device.get();
    void* output_device_ptr = output_device.get();
    void* counts_device_ptr = counts_device.get();
    void* params_device_ptr = prepared.params_device.get();
    uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
    void* args[] = {
        &prepared.geometry,
        &query_device_ptr,
        &search_device_ptr,
        &query_count_u32,
        &k_max,
        &output_device_ptr,
        &counts_device_ptr,
        &params_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(output, output_device);
    copy_device_to_host(counts, counts_device);

    std::vector<RtdlFixedRadiusNeighborRow> compacted;
    for (size_t query_index = 0; query_index < query_count; ++query_index) {
        uint32_t count = std::min(counts[query_index], k_max);
        size_t base = query_index * static_cast<size_t>(k_max);
        for (uint32_t rank = 0; rank < count; ++rank) {
            compacted.push_back(output[base + rank]);
        }
    }
    *rows_out = copy_frn_rows_to_heap(compacted);
    *row_count_out = compacted.size();
}

void run_fixed_radius_neighbors_2d(
    const RtdlPoint* queries,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out) {
    if (k_max == 0) {
        throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    if (k_max > 64) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_2d currently supports k_max <= 64");
    }
    if (radius < 0.0) {
        throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (query_count > std::numeric_limits<uint32_t>::max() || search_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_2d currently supports at most 2^32-1 query/search points");
    }
    if (query_count != 0 && k_max > std::numeric_limits<size_t>::max() / query_count) {
        throw std::runtime_error("HIPRT fixed_radius_neighbors_2d output capacity overflow");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (search_count > 0 && search_points == nullptr) {
        throw std::runtime_error("search point pointer must not be null when search_count is nonzero");
    }
    if (query_count == 0 || search_count == 0) {
        std::vector<RtdlFixedRadiusNeighborRow> empty;
        *rows_out = copy_frn_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> query_values = encode_points_2d(queries, query_count);
    std::vector<RtdlHiprtPoint2DDevice> search_values = encode_points_2d(search_points, search_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_point_2d_aabbs(search_values.data(), search_values.size(), static_cast<float>(radius));
    RtdlHiprtFixedRadiusParams params{static_cast<float>(radius)};

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation search_device(search_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtFixedRadiusParams));
    copy_host_to_device(query_device, query_values);
    copy_host_to_device(search_device, search_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointRadius2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = search_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            fixed_radius_neighbors_2d_kernel_source(),
            "rtdl_hiprt_fixed_radius_neighbors_2d.cu",
            "RtdlFixedRadiusNeighbors2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = query_count * static_cast<size_t>(k_max);
        std::vector<RtdlFixedRadiusNeighborRow> output(output_capacity);
        std::vector<uint32_t> counts(query_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlFixedRadiusNeighborRow));
        DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));

        void* query_device_ptr = query_device.get();
        void* search_device_ptr = search_device.get();
        void* output_device_ptr = output_device.get();
        void* counts_device_ptr = counts_device.get();
        void* params_device_ptr = params_device.get();
        uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &query_device_ptr,
            &search_device_ptr,
            &query_count_u32,
            &k_max,
            &output_device_ptr,
            &counts_device_ptr,
            &params_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        copy_device_to_host(counts, counts_device);

        std::vector<RtdlFixedRadiusNeighborRow> compacted;
        for (size_t query_index = 0; query_index < query_count; ++query_index) {
            uint32_t count = std::min(counts[query_index], k_max);
            size_t base = query_index * static_cast<size_t>(k_max);
            for (uint32_t rank = 0; rank < count; ++rank) {
                compacted.push_back(output[base + rank]);
            }
        }
        *rows_out = copy_frn_rows_to_heap(compacted);
        *row_count_out = compacted.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void sort_lsi_rows_by_input_order(
    std::vector<RtdlLsiRow>& rows,
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count) {
    std::unordered_map<uint32_t, size_t> left_order;
    std::unordered_map<uint32_t, size_t> right_order;
    left_order.reserve(left_count);
    right_order.reserve(right_count);
    for (size_t i = 0; i < left_count; ++i) {
        left_order.emplace(left[i].id, i);
    }
    for (size_t i = 0; i < right_count; ++i) {
        right_order.emplace(right[i].id, i);
    }
    std::sort(rows.begin(), rows.end(), [&](const RtdlLsiRow& a, const RtdlLsiRow& b) {
        const size_t left_a = left_order.count(a.left_id) ? left_order[a.left_id] : std::numeric_limits<size_t>::max();
        const size_t left_b = left_order.count(b.left_id) ? left_order[b.left_id] : std::numeric_limits<size_t>::max();
        if (left_a != left_b) {
            return left_a < left_b;
        }
        const size_t right_a = right_order.count(a.right_id) ? right_order[a.right_id] : std::numeric_limits<size_t>::max();
        const size_t right_b = right_order.count(b.right_id) ? right_order[b.right_id] : std::numeric_limits<size_t>::max();
        return right_a < right_b;
    });
}

void sort_segment_polygon_anyhit_rows_by_input_order(
    std::vector<RtdlSegmentPolygonAnyHitRow>& rows,
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count) {
    std::unordered_map<uint32_t, size_t> segment_order;
    std::unordered_map<uint32_t, size_t> polygon_order;
    segment_order.reserve(segment_count);
    polygon_order.reserve(polygon_count);
    for (size_t i = 0; i < segment_count; ++i) {
        segment_order.emplace(segments[i].id, i);
    }
    for (size_t i = 0; i < polygon_count; ++i) {
        polygon_order.emplace(polygons[i].id, i);
    }
    std::sort(rows.begin(), rows.end(), [&](const RtdlSegmentPolygonAnyHitRow& a, const RtdlSegmentPolygonAnyHitRow& b) {
        const size_t segment_a = segment_order.count(a.segment_id) ? segment_order[a.segment_id] : std::numeric_limits<size_t>::max();
        const size_t segment_b = segment_order.count(b.segment_id) ? segment_order[b.segment_id] : std::numeric_limits<size_t>::max();
        if (segment_a != segment_b) {
            return segment_a < segment_b;
        }
        const size_t polygon_a = polygon_order.count(a.polygon_id) ? polygon_order[a.polygon_id] : std::numeric_limits<size_t>::max();
        const size_t polygon_b = polygon_order.count(b.polygon_id) ? polygon_order[b.polygon_id] : std::numeric_limits<size_t>::max();
        return polygon_a < polygon_b;
    });
}

void run_lsi_2d(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out) {
    if (left_count > std::numeric_limits<uint32_t>::max() || right_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT segment_intersection currently supports at most 2^32-1 left/right segments");
    }
    if (left_count != 0 && right_count > std::numeric_limits<size_t>::max() / left_count) {
        throw std::runtime_error("HIPRT segment_intersection output capacity overflow");
    }
    if (left_count > 0 && left == nullptr) {
        throw std::runtime_error("left segment pointer must not be null when left_count is nonzero");
    }
    if (right_count > 0 && right == nullptr) {
        throw std::runtime_error("right segment pointer must not be null when right_count is nonzero");
    }
    if (left_count == 0 || right_count == 0) {
        std::vector<RtdlLsiRow> empty;
        *rows_out = copy_lsi_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtSegmentDevice> left_values = encode_segments(left, left_count);
    std::vector<RtdlHiprtSegmentDevice> right_values = encode_segments(right, right_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_segment_aabbs(right_values.data(), right_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation left_device(left_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation right_device(right_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(left_device, left_values);
    copy_host_to_device(right_device, right_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlSegment2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = right_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            lsi_2d_kernel_source(),
            "rtdl_hiprt_lsi_2d.cu",
            "RtdlLsi2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = left_count * right_count;
        std::vector<RtdlLsiRow> output(output_capacity);
        std::vector<uint32_t> counts(left_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlLsiRow));
        DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));

        void* left_device_ptr = left_device.get();
        void* right_device_ptr = right_device.get();
        void* output_device_ptr = output_device.get();
        void* counts_device_ptr = counts_device.get();
        uint32_t left_count_u32 = static_cast<uint32_t>(left_count);
        uint32_t right_count_u32 = static_cast<uint32_t>(right_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((left_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &left_device_ptr,
            &right_device_ptr,
            &left_count_u32,
            &right_count_u32,
            &output_device_ptr,
            &counts_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        copy_device_to_host(counts, counts_device);

        std::vector<RtdlLsiRow> compacted;
        for (size_t left_index = 0; left_index < left_count; ++left_index) {
            uint32_t count = std::min<uint32_t>(counts[left_index], static_cast<uint32_t>(right_count));
            size_t base = left_index * right_count;
            for (uint32_t rank = 0; rank < count; ++rank) {
                compacted.push_back(output[base + rank]);
            }
        }
        sort_lsi_rows_by_input_order(compacted, left, left_count, right, right_count);
        *rows_out = copy_lsi_rows_to_heap(compacted);
        *row_count_out = compacted.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_segment_polygon_2d_common(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    bool anyhit_rows,
    RtdlSegmentPolygonHitCountRow** hitcount_rows_out,
    RtdlSegmentPolygonAnyHitRow** anyhit_rows_out,
    size_t* row_count_out) {
    if (segment_count > std::numeric_limits<uint32_t>::max() || polygon_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT segment_polygon currently supports at most 2^32-1 segments/polygons");
    }
    if (segment_count != 0 && polygon_count > std::numeric_limits<size_t>::max() / segment_count) {
        throw std::runtime_error("HIPRT segment_polygon output capacity overflow");
    }
    if (segment_count > 0 && segments == nullptr) {
        throw std::runtime_error("segment pointer must not be null when segment_count is nonzero");
    }
    if (polygon_count > 0 && polygons == nullptr) {
        throw std::runtime_error("polygon pointer must not be null when polygon_count is nonzero");
    }
    if (vertex_xy_count % 2 != 0) {
        throw std::runtime_error("polygon vertex_xy_count must be even");
    }
    if (vertex_xy_count > 0 && vertices_xy == nullptr) {
        throw std::runtime_error("polygon vertices pointer must not be null when vertex_xy_count is nonzero");
    }
    if (segment_count == 0) {
        *row_count_out = 0;
        if (anyhit_rows) {
            std::vector<RtdlSegmentPolygonAnyHitRow> empty;
            *anyhit_rows_out = copy_segment_polygon_anyhit_rows_to_heap(empty);
        } else {
            std::vector<RtdlSegmentPolygonHitCountRow> empty;
            *hitcount_rows_out = copy_segment_polygon_hitcount_rows_to_heap(empty);
        }
        return;
    }
    if (polygon_count == 0) {
        if (anyhit_rows) {
            std::vector<RtdlSegmentPolygonAnyHitRow> empty;
            *anyhit_rows_out = copy_segment_polygon_anyhit_rows_to_heap(empty);
            *row_count_out = 0;
        } else {
            std::vector<RtdlSegmentPolygonHitCountRow> output;
            output.reserve(segment_count);
            for (size_t i = 0; i < segment_count; ++i) {
                output.push_back({segments[i].id, 0u});
            }
            *hitcount_rows_out = copy_segment_polygon_hitcount_rows_to_heap(output);
            *row_count_out = output.size();
        }
        return;
    }

    std::vector<RtdlHiprtSegmentDevice> segment_values = encode_segments(segments, segment_count);
    std::vector<RtdlHiprtPolygonRefDevice> polygon_values = encode_polygon_refs_2d(polygons, polygon_count);
    std::vector<RtdlHiprtVertex2DDevice> vertex_values = encode_vertices_2d(vertices_xy, vertex_xy_count);
    std::vector<RtdlHiprtAabb> aabb_values =
        encode_polygon_aabbs(polygon_values.data(), polygon_values.size(), vertex_values.data(), vertex_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation segment_device(segment_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation polygon_device(polygon_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation vertex_device(vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation pip_data_device(sizeof(RtdlHiprtPipDataDevice));
    copy_host_to_device(segment_device, segment_values);
    copy_host_to_device(polygon_device, polygon_values);
    copy_host_to_device(vertex_device, vertex_values);
    copy_host_to_device(aabb_device, aabb_values);
    RtdlHiprtPipDataDevice pip_data{reinterpret_cast<const RtdlHiprtPolygonRefDevice*>(polygon_device.get()),
                                    reinterpret_cast<const RtdlHiprtVertex2DDevice*>(vertex_device.get())};
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(pip_data_device.oro_ptr(), &pip_data, sizeof(pip_data)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlSegmentPolygon2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = pip_data_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));

        void* segment_device_ptr = segment_device.get();
        void* polygon_device_ptr = polygon_device.get();
        uint32_t segment_count_u32 = static_cast<uint32_t>(segment_count);
        uint32_t polygon_count_u32 = static_cast<uint32_t>(polygon_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((segment_count + block_size - 1) / block_size);

        if (anyhit_rows) {
            oroFunction kernel = build_trace_kernel_from_source(
                runtime.context,
                segment_polygon_2d_kernel_source(),
                "rtdl_hiprt_segment_polygon_2d.cu",
                "RtdlSegmentPolygonAnyhit2DKernel",
                &func_name_set,
                1,
                1);
            const size_t output_capacity = segment_count * polygon_count;
            std::vector<RtdlSegmentPolygonAnyHitRow> output(output_capacity);
            std::vector<uint32_t> counts(segment_count);
            DeviceAllocation output_device(output.size() * sizeof(RtdlSegmentPolygonAnyHitRow));
            DeviceAllocation counts_device(counts.size() * sizeof(uint32_t));
            void* output_device_ptr = output_device.get();
            void* counts_device_ptr = counts_device.get();
            void* args[] = {
                &geometry,
                &segment_device_ptr,
                &polygon_device_ptr,
                &segment_count_u32,
                &polygon_count_u32,
                &output_device_ptr,
                &counts_device_ptr,
                &func_table,
            };
            check_oro(
                "oroModuleLaunchKernel",
                oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
            copy_device_to_host(output, output_device);
            copy_device_to_host(counts, counts_device);

            std::vector<RtdlSegmentPolygonAnyHitRow> compacted;
            for (size_t segment_index = 0; segment_index < segment_count; ++segment_index) {
                const uint32_t count = std::min<uint32_t>(counts[segment_index], static_cast<uint32_t>(polygon_count));
                const size_t base = segment_index * polygon_count;
                for (uint32_t rank = 0; rank < count; ++rank) {
                    compacted.push_back(output[base + rank]);
                }
            }
            sort_segment_polygon_anyhit_rows_by_input_order(compacted, segments, segment_count, polygons, polygon_count);
            *anyhit_rows_out = copy_segment_polygon_anyhit_rows_to_heap(compacted);
            *row_count_out = compacted.size();
        } else {
            oroFunction kernel = build_trace_kernel_from_source(
                runtime.context,
                segment_polygon_2d_kernel_source(),
                "rtdl_hiprt_segment_polygon_2d.cu",
                "RtdlSegmentPolygonHitcount2DKernel",
                &func_name_set,
                1,
                1);
            std::vector<RtdlSegmentPolygonHitCountRow> output(segment_count);
            DeviceAllocation output_device(output.size() * sizeof(RtdlSegmentPolygonHitCountRow));
            void* output_device_ptr = output_device.get();
            void* args[] = {
                &geometry,
                &segment_device_ptr,
                &segment_count_u32,
                &output_device_ptr,
                &func_table,
            };
            check_oro(
                "oroModuleLaunchKernel",
                oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
            copy_device_to_host(output, output_device);
            *hitcount_rows_out = copy_segment_polygon_hitcount_rows_to_heap(output);
            *row_count_out = output.size();
        }
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_segment_polygon_hitcount_2d(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonHitCountRow** rows_out,
    size_t* row_count_out) {
    RtdlSegmentPolygonAnyHitRow* unused = nullptr;
    run_segment_polygon_2d_common(
        segments,
        segment_count,
        polygons,
        polygon_count,
        vertices_xy,
        vertex_xy_count,
        false,
        rows_out,
        &unused,
        row_count_out);
}

void run_segment_polygon_anyhit_rows_2d(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonAnyHitRow** rows_out,
    size_t* row_count_out) {
    RtdlSegmentPolygonHitCountRow* unused = nullptr;
    run_segment_polygon_2d_common(
        segments,
        segment_count,
        polygons,
        polygon_count,
        vertices_xy,
        vertex_xy_count,
        true,
        &unused,
        rows_out,
        row_count_out);
}

void run_ray_hitcount_2d(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out) {
    if (ray_count > std::numeric_limits<uint32_t>::max() || triangle_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT 2D ray_triangle_hit_count currently supports at most 2^32-1 rays/triangles");
    }
    if (ray_count > 0 && rays == nullptr) {
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    }
    if (triangle_count > 0 && triangles == nullptr) {
        throw std::runtime_error("triangle pointer must not be null when triangle_count is nonzero");
    }
    if (ray_count == 0) {
        std::vector<RtdlRayHitCountRow> empty;
        *rows_out = copy_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }
    if (triangle_count == 0) {
        std::vector<RtdlRayHitCountRow> output;
        output.reserve(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            output.push_back({rays[i].id, 0u});
        }
        *rows_out = copy_rows_to_heap(output);
        *row_count_out = output.size();
        return;
    }

    std::vector<RtdlHiprtRay2DDevice> ray_values = encode_rays_2d(rays, ray_count);
    std::vector<RtdlHiprtTriangle2DDevice> triangle_values = encode_triangles_2d(triangles, triangle_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_triangle_2d_aabbs(triangle_values.data(), triangle_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay2DDevice));
    DeviceAllocation triangle_device(triangle_values.size() * sizeof(RtdlHiprtTriangle2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(ray_device, ray_values);
    copy_host_to_device(triangle_device, triangle_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlTriangle2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = triangle_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            ray_hitcount_2d_kernel_source(),
            "rtdl_hiprt_ray_hitcount_2d.cu",
            "RtdlRayHitcount2DKernel",
            &func_name_set,
            1,
            1);

        std::vector<RtdlRayHitCountRow> output(ray_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlRayHitCountRow));
        void* ray_device_ptr = ray_device.get();
        void* output_device_ptr = output_device.get();
        uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &ray_device_ptr,
            &ray_count_u32,
            &output_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);

        *rows_out = copy_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_pip_2d(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlPipRow** rows_out,
    size_t* row_count_out) {
    if (point_count > std::numeric_limits<uint32_t>::max() || polygon_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT point_in_polygon currently supports at most 2^32-1 points/polygons");
    }
    if (point_count != 0 && polygon_count > std::numeric_limits<size_t>::max() / point_count) {
        throw std::runtime_error("HIPRT point_in_polygon output capacity overflow");
    }
    if (point_count > 0 && points == nullptr) {
        throw std::runtime_error("point pointer must not be null when point_count is nonzero");
    }
    if (polygon_count > 0 && polygons == nullptr) {
        throw std::runtime_error("polygon pointer must not be null when polygon_count is nonzero");
    }
    if (vertex_xy_count % 2 != 0) {
        throw std::runtime_error("polygon vertex_xy_count must be even");
    }
    if (vertex_xy_count > 0 && vertices_xy == nullptr) {
        throw std::runtime_error("polygon vertices pointer must not be null when vertex_xy_count is nonzero");
    }
    if (point_count == 0 || polygon_count == 0) {
        std::vector<RtdlPipRow> empty;
        *rows_out = copy_pip_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> point_values = encode_points_2d(points, point_count);
    std::vector<RtdlHiprtPolygonRefDevice> polygon_values = encode_polygon_refs_2d(polygons, polygon_count);
    std::vector<RtdlHiprtVertex2DDevice> vertex_values = encode_vertices_2d(vertices_xy, vertex_xy_count);
    std::vector<RtdlHiprtAabb> aabb_values =
        encode_polygon_aabbs(polygon_values.data(), polygon_values.size(), vertex_values.data(), vertex_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation point_device(point_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation polygon_device(polygon_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation vertex_device(vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation pip_data_device(sizeof(RtdlHiprtPipDataDevice));
    copy_host_to_device(point_device, point_values);
    copy_host_to_device(polygon_device, polygon_values);
    copy_host_to_device(vertex_device, vertex_values);
    copy_host_to_device(aabb_device, aabb_values);
    RtdlHiprtPipDataDevice pip_data{reinterpret_cast<const RtdlHiprtPolygonRefDevice*>(polygon_device.get()),
                                    reinterpret_cast<const RtdlHiprtVertex2DDevice*>(vertex_device.get())};
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(pip_data_device.oro_ptr(), &pip_data, sizeof(pip_data)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPolygon2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = pip_data_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            pip_2d_kernel_source(),
            "rtdl_hiprt_pip_2d.cu",
            "RtdlPip2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = point_count * polygon_count;
        std::vector<RtdlPipRow> output(output_capacity);
        DeviceAllocation output_device(output.size() * sizeof(RtdlPipRow));
        void* point_device_ptr = point_device.get();
        void* polygon_device_ptr = polygon_device.get();
        void* output_device_ptr = output_device.get();
        uint32_t point_count_u32 = static_cast<uint32_t>(point_count);
        uint32_t polygon_count_u32 = static_cast<uint32_t>(polygon_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((point_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &point_device_ptr,
            &polygon_device_ptr,
            &point_count_u32,
            &polygon_count_u32,
            &output_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        *rows_out = copy_pip_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_overlay_2d(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlOverlayRow** rows_out,
    size_t* row_count_out) {
    if (left_count > std::numeric_limits<uint32_t>::max() || right_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT overlay_compose currently supports at most 2^32-1 left/right polygons");
    }
    if (left_count != 0 && right_count > std::numeric_limits<size_t>::max() / left_count) {
        throw std::runtime_error("HIPRT overlay_compose output capacity overflow");
    }
    if (left_count > 0 && left_polygons == nullptr) {
        throw std::runtime_error("left polygon pointer must not be null when left_count is nonzero");
    }
    if (right_count > 0 && right_polygons == nullptr) {
        throw std::runtime_error("right polygon pointer must not be null when right_count is nonzero");
    }
    if (left_vertex_xy_count % 2 != 0 || right_vertex_xy_count % 2 != 0) {
        throw std::runtime_error("polygon vertex_xy_count must be even");
    }
    if (left_vertex_xy_count > 0 && left_vertices_xy == nullptr) {
        throw std::runtime_error("left polygon vertices pointer must not be null when vertex count is nonzero");
    }
    if (right_vertex_xy_count > 0 && right_vertices_xy == nullptr) {
        throw std::runtime_error("right polygon vertices pointer must not be null when vertex count is nonzero");
    }
    if (left_count == 0 || right_count == 0) {
        std::vector<RtdlOverlayRow> empty;
        *rows_out = copy_overlay_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPolygonRefDevice> left_values = encode_polygon_refs_2d(left_polygons, left_count);
    std::vector<RtdlHiprtVertex2DDevice> left_vertex_values = encode_vertices_2d(left_vertices_xy, left_vertex_xy_count);
    std::vector<RtdlHiprtPolygonRefDevice> right_values = encode_polygon_refs_2d(right_polygons, right_count);
    std::vector<RtdlHiprtVertex2DDevice> right_vertex_values = encode_vertices_2d(right_vertices_xy, right_vertex_xy_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_overlay_candidate_aabbs(
        right_values.data(),
        right_values.size(),
        left_values.data(),
        left_values.size(),
        left_vertex_values.data(),
        left_vertex_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation left_device(left_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation left_vertex_device(left_vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation right_device(right_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation right_vertex_device(right_vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(left_device, left_values);
    copy_host_to_device(left_vertex_device, left_vertex_values);
    copy_host_to_device(right_device, right_values);
    copy_host_to_device(right_vertex_device, right_vertex_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlOverlayCandidate2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            overlay_2d_kernel_source(),
            "rtdl_hiprt_overlay_2d.cu",
            "RtdlOverlay2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = left_count * right_count;
        std::vector<RtdlOverlayRow> output(output_capacity);
        DeviceAllocation output_device(output.size() * sizeof(RtdlOverlayRow));
        void* left_device_ptr = left_device.get();
        void* left_vertex_device_ptr = left_vertex_device.get();
        void* right_device_ptr = right_device.get();
        void* right_vertex_device_ptr = right_vertex_device.get();
        void* output_device_ptr = output_device.get();
        uint32_t left_count_u32 = static_cast<uint32_t>(left_count);
        uint32_t right_count_u32 = static_cast<uint32_t>(right_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((left_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &left_device_ptr,
            &left_vertex_device_ptr,
            &right_device_ptr,
            &right_vertex_device_ptr,
            &left_count_u32,
            &right_count_u32,
            &output_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        *rows_out = copy_overlay_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_point_nearest_segment_2d(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out) {
    if (point_count > std::numeric_limits<uint32_t>::max() || segment_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT point_nearest_segment currently supports at most 2^32-1 points/segments");
    }
    if (point_count > 0 && points == nullptr) {
        throw std::runtime_error("point pointer must not be null when point_count is nonzero");
    }
    if (segment_count > 0 && segments == nullptr) {
        throw std::runtime_error("segment pointer must not be null when segment_count is nonzero");
    }
    if (point_count == 0 || segment_count == 0) {
        std::vector<RtdlPointNearestSegmentRow> empty;
        *rows_out = copy_pns_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> point_values = encode_points_2d(points, point_count);
    std::vector<RtdlHiprtSegmentDevice> segment_values = encode_segments(segments, segment_count);
    const float radius = global_point_segment_radius(point_values.data(), point_values.size(), segment_values.data(), segment_values.size());
    std::vector<RtdlHiprtAabb> aabb_values = encode_segment_expanded_aabbs(segment_values.data(), segment_values.size(), radius);
    RtdlHiprtPointSegmentParams params{radius};

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation point_device(point_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation segment_device(segment_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtPointSegmentParams));
    copy_host_to_device(point_device, point_values);
    copy_host_to_device(segment_device, segment_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointSegmentDistance2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = segment_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            point_nearest_segment_2d_kernel_source(),
            "rtdl_hiprt_point_nearest_segment_2d.cu",
            "RtdlPointNearestSegment2DKernel",
            &func_name_set,
            1,
            1);

        std::vector<RtdlPointNearestSegmentRow> output(point_count);
        std::vector<uint32_t> has_row(point_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlPointNearestSegmentRow));
        DeviceAllocation has_row_device(has_row.size() * sizeof(uint32_t));
        void* point_device_ptr = point_device.get();
        void* segment_device_ptr = segment_device.get();
        void* output_device_ptr = output_device.get();
        void* has_row_device_ptr = has_row_device.get();
        void* params_device_ptr = params_device.get();
        uint32_t point_count_u32 = static_cast<uint32_t>(point_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((point_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &point_device_ptr,
            &segment_device_ptr,
            &point_count_u32,
            &output_device_ptr,
            &has_row_device_ptr,
            &params_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(output, output_device);
        copy_device_to_host(has_row, has_row_device);

        std::vector<RtdlPointNearestSegmentRow> compacted;
        for (size_t i = 0; i < point_count; ++i) {
            if (has_row[i] != 0u) {
                compacted.push_back(output[i]);
            }
        }
        *rows_out = copy_pns_rows_to_heap(compacted);
        *row_count_out = compacted.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_bfs_expand(
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count,
    const uint32_t* visited,
    size_t visited_count,
    bool dedupe,
    RtdlBfsRow** rows_out,
    size_t* row_count_out) {
    if (frontier_count > std::numeric_limits<uint32_t>::max() ||
        edge_count > std::numeric_limits<uint32_t>::max() ||
        visited_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT bfs_discover currently supports at most 2^32-1 frontier/edge/visited rows");
    }
    if (frontier_count != 0 && edge_count > std::numeric_limits<size_t>::max() / frontier_count) {
        throw std::runtime_error("HIPRT bfs_discover output capacity overflow");
    }
    if (frontier_count > 0 && frontier == nullptr) {
        throw std::runtime_error("frontier pointer must not be null when frontier_count is nonzero");
    }
    if (row_offset_count > 0 && row_offsets == nullptr) {
        throw std::runtime_error("row_offsets pointer must not be null when row_offset_count is nonzero");
    }
    if (edge_count > 0 && column_indices == nullptr) {
        throw std::runtime_error("column_indices pointer must not be null when edge_count is nonzero");
    }
    if (visited_count > 0 && visited == nullptr) {
        throw std::runtime_error("visited pointer must not be null when visited_count is nonzero");
    }
    for (size_t i = 0; i < frontier_count; ++i) {
        if (frontier[i].vertex_id >= vertex_count) {
            throw std::runtime_error("HIPRT bfs_discover frontier vertex_id must be a valid graph vertex");
        }
    }
    for (size_t i = 0; i < visited_count; ++i) {
        if (visited[i] >= vertex_count) {
            throw std::runtime_error("HIPRT bfs_discover visited vertices must be valid graph vertex IDs");
        }
    }

    std::vector<RtdlHiprtGraphEdgeDevice> edge_values =
        encode_graph_edges(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
    if (frontier_count == 0 || edge_values.empty()) {
        std::vector<RtdlBfsRow> empty;
        *rows_out = copy_bfs_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }
    std::vector<RtdlHiprtAabb> aabb_values = encode_graph_edge_source_aabbs(edge_values.data(), edge_values.size());

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    std::vector<RtdlFrontierVertex> frontier_values(frontier, frontier + frontier_count);
    std::vector<uint32_t> visited_values(visited, visited + visited_count);
    std::vector<uint32_t> discovered(vertex_count, 0u);
    std::vector<uint32_t> row_count_device_host(1, 0u);

    DeviceAllocation frontier_device(frontier_values.size() * sizeof(RtdlFrontierVertex));
    DeviceAllocation visited_device(visited_values.size() * sizeof(uint32_t));
    DeviceAllocation edge_device(edge_values.size() * sizeof(RtdlHiprtGraphEdgeDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation discovered_device(discovered.size() * sizeof(uint32_t));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(frontier_device, frontier_values);
    copy_host_to_device(visited_device, visited_values);
    copy_host_to_device(edge_device, edge_values);
    copy_host_to_device(aabb_device, aabb_values);
    copy_host_to_device(discovered_device, discovered);
    copy_host_to_device(row_count_device, row_count_device_host);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlGraphEdgeBySource";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            bfs_expand_kernel_source(),
            "rtdl_hiprt_bfs_expand.cu",
            "RtdlBfsExpandKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = frontier_count * edge_values.size();
        std::vector<RtdlBfsRow> output(output_capacity);
        DeviceAllocation output_device(output.size() * sizeof(RtdlBfsRow));
        void* frontier_device_ptr = frontier_device.get();
        void* visited_device_ptr = visited_device.get();
        void* edge_device_ptr = edge_device.get();
        void* discovered_device_ptr = discovered_device.get();
        void* output_device_ptr = output_device.get();
        void* row_count_device_ptr = row_count_device.get();
        uint32_t frontier_count_u32 = static_cast<uint32_t>(frontier_count);
        uint32_t visited_count_u32 = static_cast<uint32_t>(visited_count);
        uint32_t edge_count_u32 = static_cast<uint32_t>(edge_values.size());
        uint32_t dedupe_u32 = dedupe ? 1u : 0u;
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((frontier_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &frontier_device_ptr,
            &frontier_count_u32,
            &visited_device_ptr,
            &visited_count_u32,
            &edge_device_ptr,
            &edge_count_u32,
            &discovered_device_ptr,
            &vertex_count,
            &dedupe_u32,
            &output_device_ptr,
            &row_count_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(row_count_device_host, row_count_device);
        const uint32_t produced = std::min<uint32_t>(row_count_device_host[0], static_cast<uint32_t>(output.size()));
        output.resize(produced);
        copy_device_to_host(output, output_device);
        std::sort(output.begin(), output.end(), [](const RtdlBfsRow& a, const RtdlBfsRow& b) {
            if (a.level != b.level) {
                return a.level < b.level;
            }
            if (a.dst_vertex != b.dst_vertex) {
                return a.dst_vertex < b.dst_vertex;
            }
            return a.src_vertex < b.src_vertex;
        });
        *rows_out = copy_bfs_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

std::unique_ptr<PreparedGraphCSR> prepare_graph_csr(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count) {
    if (row_offset_count == 0 || row_offsets == nullptr) {
        throw std::runtime_error("HIPRT prepared graph CSR row_offsets must not be empty");
    }
    if (edge_count > 0 && column_indices == nullptr) {
        throw std::runtime_error("HIPRT prepared graph CSR column_indices pointer must not be null when edge_count is nonzero");
    }
    if (row_offset_count - 1u != vertex_count) {
        throw std::runtime_error("HIPRT prepared graph CSR row_offset_count must equal vertex_count + 1");
    }
    if (edge_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared graph CSR currently supports at most 2^32-1 edges");
    }
    std::vector<RtdlHiprtGraphEdgeDevice> edge_values =
        encode_graph_edges(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
    if (edge_values.empty()) {
        throw std::runtime_error("prepared HIPRT graph CSR requires at least one edge");
    }
    std::vector<RtdlHiprtAabb> aabb_values = encode_graph_edge_source_aabbs(edge_values.data(), edge_values.size());
    std::vector<uint32_t> row_offset_values(row_offsets, row_offsets + row_offset_count);
    std::vector<uint32_t> column_values(column_indices, column_indices + edge_count);

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation row_offset_device(row_offset_values.size() * sizeof(uint32_t));
    DeviceAllocation column_device(column_values.size() * sizeof(uint32_t));
    DeviceAllocation edge_device(edge_values.size() * sizeof(RtdlHiprtGraphEdgeDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(row_offset_device, row_offset_values);
    copy_host_to_device(column_device, column_values);
    copy_host_to_device(edge_device, edge_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable bfs_func_table{};
    hiprtFuncTable triangle_func_table{};
    try {
        hiprtFuncNameSet bfs_func_name_set{};
        bfs_func_name_set.intersectFuncName = "intersectRtdlGraphEdgeBySource";
        hiprtFuncDataSet bfs_func_data_set{};
        bfs_func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, bfs_func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, bfs_func_table, 0, 0, bfs_func_data_set));
        oroFunction bfs_kernel = build_trace_kernel_from_source(
            runtime.context,
            bfs_expand_kernel_source(),
            "rtdl_hiprt_bfs_expand.cu",
            "RtdlBfsExpandKernel",
            &bfs_func_name_set,
            1,
            1);

        hiprtFuncNameSet triangle_func_name_set{};
        triangle_func_name_set.intersectFuncName = "intersectRtdlTriangleGraphEdgeBySource";
        hiprtFuncDataSet triangle_func_data_set{};
        triangle_func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, triangle_func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, triangle_func_table, 0, 0, triangle_func_data_set));
        oroFunction triangle_kernel = build_trace_kernel_from_source(
            runtime.context,
            triangle_probe_kernel_source(),
            "rtdl_hiprt_triangle_probe.cu",
            "RtdlTriangleProbeKernel",
            &triangle_func_name_set,
            1,
            1);

        auto prepared = std::make_unique<PreparedGraphCSR>(
            std::move(runtime),
            std::move(row_offset_device),
            std::move(column_device),
            std::move(edge_device),
            std::move(aabb_device),
            geometry,
            bfs_func_table,
            triangle_func_table,
            bfs_kernel,
            triangle_kernel,
            vertex_count,
            static_cast<uint32_t>(edge_values.size()));
        geometry = nullptr;
        bfs_func_table = nullptr;
        triangle_func_table = nullptr;
        return prepared;
    } catch (...) {
        if (bfs_func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, bfs_func_table);
        }
        if (triangle_func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, triangle_func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
}

void run_prepared_bfs_expand(
    PreparedGraphCSR& prepared,
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* visited,
    size_t visited_count,
    bool dedupe,
    RtdlBfsRow** rows_out,
    size_t* row_count_out) {
    if (frontier_count > std::numeric_limits<uint32_t>::max() ||
        visited_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared bfs_discover currently supports at most 2^32-1 frontier/visited rows");
    }
    if (frontier_count != 0 && static_cast<size_t>(prepared.edge_count) > std::numeric_limits<size_t>::max() / frontier_count) {
        throw std::runtime_error("HIPRT prepared bfs_discover output capacity overflow");
    }
    if (frontier_count > 0 && frontier == nullptr) {
        throw std::runtime_error("frontier pointer must not be null when frontier_count is nonzero");
    }
    if (visited_count > 0 && visited == nullptr) {
        throw std::runtime_error("visited pointer must not be null when visited_count is nonzero");
    }
    for (size_t i = 0; i < frontier_count; ++i) {
        if (frontier[i].vertex_id >= prepared.vertex_count) {
            throw std::runtime_error("HIPRT prepared bfs_discover frontier vertex_id must be a valid graph vertex");
        }
    }
    for (size_t i = 0; i < visited_count; ++i) {
        if (visited[i] >= prepared.vertex_count) {
            throw std::runtime_error("HIPRT prepared bfs_discover visited vertices must be valid graph vertex IDs");
        }
    }
    if (frontier_count == 0 || prepared.edge_count == 0) {
        std::vector<RtdlBfsRow> empty;
        *rows_out = copy_bfs_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlFrontierVertex> frontier_values(frontier, frontier + frontier_count);
    std::vector<uint32_t> visited_values(visited, visited + visited_count);
    std::vector<uint32_t> discovered(prepared.vertex_count, 0u);
    std::vector<uint32_t> row_count_device_host(1, 0u);
    DeviceAllocation frontier_device(frontier_values.size() * sizeof(RtdlFrontierVertex));
    DeviceAllocation visited_device(visited_values.size() * sizeof(uint32_t));
    DeviceAllocation discovered_device(discovered.size() * sizeof(uint32_t));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(frontier_device, frontier_values);
    copy_host_to_device(visited_device, visited_values);
    copy_host_to_device(discovered_device, discovered);
    copy_host_to_device(row_count_device, row_count_device_host);

    const size_t output_capacity = frontier_count * static_cast<size_t>(prepared.edge_count);
    std::vector<RtdlBfsRow> output(output_capacity);
    DeviceAllocation output_device(output.size() * sizeof(RtdlBfsRow));
    void* frontier_device_ptr = frontier_device.get();
    void* visited_device_ptr = visited_device.get();
    void* edge_device_ptr = prepared.edge_device.get();
    void* discovered_device_ptr = discovered_device.get();
    void* output_device_ptr = output_device.get();
    void* row_count_device_ptr = row_count_device.get();
    uint32_t frontier_count_u32 = static_cast<uint32_t>(frontier_count);
    uint32_t visited_count_u32 = static_cast<uint32_t>(visited_count);
    uint32_t dedupe_u32 = dedupe ? 1u : 0u;
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((frontier_count + block_size - 1) / block_size);
    void* args[] = {
        &prepared.geometry,
        &frontier_device_ptr,
        &frontier_count_u32,
        &visited_device_ptr,
        &visited_count_u32,
        &edge_device_ptr,
        &prepared.edge_count,
        &discovered_device_ptr,
        &prepared.vertex_count,
        &dedupe_u32,
        &output_device_ptr,
        &row_count_device_ptr,
        &prepared.bfs_func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.bfs_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(row_count_device_host, row_count_device);
    const uint32_t produced = std::min<uint32_t>(row_count_device_host[0], static_cast<uint32_t>(output.size()));
    output.resize(produced);
    copy_device_to_host(output, output_device);
    std::sort(output.begin(), output.end(), [](const RtdlBfsRow& a, const RtdlBfsRow& b) {
        if (a.level != b.level) {
            return a.level < b.level;
        }
        if (a.dst_vertex != b.dst_vertex) {
            return a.dst_vertex < b.dst_vertex;
        }
        return a.src_vertex < b.src_vertex;
    });
    *rows_out = copy_bfs_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_triangle_probe(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    bool enforce_id_ascending,
    bool unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out) {
    if (row_offset_count == 0 || row_offsets == nullptr) {
        throw std::runtime_error("HIPRT triangle_match CSR row_offsets must not be empty");
    }
    if (edge_count > 0 && column_indices == nullptr) {
        throw std::runtime_error("HIPRT triangle_match column_indices pointer must not be null when edge_count is nonzero");
    }
    if (seed_count > 0 && seeds == nullptr) {
        throw std::runtime_error("HIPRT triangle_match seed pointer must not be null when seed_count is nonzero");
    }
    if (row_offset_count - 1u > std::numeric_limits<uint32_t>::max() ||
        edge_count > std::numeric_limits<uint32_t>::max() ||
        seed_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT triangle_match currently supports at most 2^32-1 vertices/edges/seeds");
    }
    if (seed_count != 0 && edge_count > std::numeric_limits<size_t>::max() / seed_count) {
        throw std::runtime_error("HIPRT triangle_match output capacity overflow");
    }
    uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1u);
    std::vector<RtdlHiprtGraphEdgeDevice> edge_values =
        encode_graph_edges(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
    for (size_t i = 0; i < seed_count; ++i) {
        if (seeds[i].u >= vertex_count || seeds[i].v >= vertex_count) {
            throw std::runtime_error("HIPRT triangle_match edge seed vertices must be valid graph vertex IDs");
        }
    }
    if (seed_count == 0 || edge_values.empty()) {
        std::vector<RtdlTriangleRow> empty;
        *rows_out = copy_triangle_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }
    std::vector<RtdlHiprtAabb> aabb_values = encode_graph_edge_source_aabbs(edge_values.data(), edge_values.size());
    std::vector<uint32_t> row_offset_values(row_offsets, row_offsets + row_offset_count);
    std::vector<uint32_t> column_values(column_indices, column_indices + edge_count);
    std::vector<RtdlEdgeSeed> seed_values(seeds, seeds + seed_count);
    std::vector<uint32_t> row_count_device_host(1, 0u);

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation row_offset_device(row_offset_values.size() * sizeof(uint32_t));
    DeviceAllocation column_device(column_values.size() * sizeof(uint32_t));
    DeviceAllocation seed_device(seed_values.size() * sizeof(RtdlEdgeSeed));
    DeviceAllocation edge_device(edge_values.size() * sizeof(RtdlHiprtGraphEdgeDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(row_offset_device, row_offset_values);
    copy_host_to_device(column_device, column_values);
    copy_host_to_device(seed_device, seed_values);
    copy_host_to_device(edge_device, edge_values);
    copy_host_to_device(aabb_device, aabb_values);
    copy_host_to_device(row_count_device, row_count_device_host);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlTriangleGraphEdgeBySource";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            triangle_probe_kernel_source(),
            "rtdl_hiprt_triangle_probe.cu",
            "RtdlTriangleProbeKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = seed_count * edge_values.size();
        std::vector<RtdlHiprtTriangleCandidateRow> candidates(output_capacity);
        DeviceAllocation candidate_device(candidates.size() * sizeof(RtdlHiprtTriangleCandidateRow));
        void* seed_device_ptr = seed_device.get();
        void* row_offset_device_ptr = row_offset_device.get();
        void* column_device_ptr = column_device.get();
        void* edge_device_ptr = edge_device.get();
        void* candidate_device_ptr = candidate_device.get();
        void* row_count_device_ptr = row_count_device.get();
        uint32_t seed_count_u32 = static_cast<uint32_t>(seed_count);
        uint32_t edge_count_u32 = static_cast<uint32_t>(edge_values.size());
        uint32_t enforce_u32 = enforce_id_ascending ? 1u : 0u;
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((seed_count + block_size - 1) / block_size);
        void* args[] = {
            &geometry,
            &seed_device_ptr,
            &seed_count_u32,
            &row_offset_device_ptr,
            &column_device_ptr,
            &edge_device_ptr,
            &edge_count_u32,
            &vertex_count,
            &enforce_u32,
            &candidate_device_ptr,
            &row_count_device_ptr,
            &func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(row_count_device_host, row_count_device);
        const uint32_t produced = std::min<uint32_t>(row_count_device_host[0], static_cast<uint32_t>(candidates.size()));
        candidates.resize(produced);
        copy_device_to_host(candidates, candidate_device);
        std::sort(candidates.begin(), candidates.end(), [](const RtdlHiprtTriangleCandidateRow& a, const RtdlHiprtTriangleCandidateRow& b) {
            if (a.seed_index != b.seed_index) {
                return a.seed_index < b.seed_index;
            }
            if (a.w != b.w) {
                return a.w < b.w;
            }
            if (a.u != b.u) {
                return a.u < b.u;
            }
            return a.v < b.v;
        });

        std::vector<RtdlTriangleRow> output;
        output.reserve(candidates.size());
        for (const RtdlHiprtTriangleCandidateRow& candidate : candidates) {
            RtdlTriangleRow row{candidate.u, candidate.v, candidate.w};
            if (unique) {
                const bool seen = std::any_of(output.begin(), output.end(), [&](const RtdlTriangleRow& existing) {
                    return existing.u == row.u && existing.v == row.v && existing.w == row.w;
                });
                if (seen) {
                    continue;
                }
            }
            output.push_back(row);
        }
        *rows_out = copy_triangle_rows_to_heap(output);
        *row_count_out = output.size();
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
}

void run_prepared_triangle_probe(
    PreparedGraphCSR& prepared,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    bool enforce_id_ascending,
    bool unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out) {
    if (seed_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared triangle_match currently supports at most 2^32-1 seeds");
    }
    if (seed_count != 0 && static_cast<size_t>(prepared.edge_count) > std::numeric_limits<size_t>::max() / seed_count) {
        throw std::runtime_error("HIPRT prepared triangle_match output capacity overflow");
    }
    if (seed_count > 0 && seeds == nullptr) {
        throw std::runtime_error("HIPRT prepared triangle_match seed pointer must not be null when seed_count is nonzero");
    }
    for (size_t i = 0; i < seed_count; ++i) {
        if (seeds[i].u >= prepared.vertex_count || seeds[i].v >= prepared.vertex_count) {
            throw std::runtime_error("HIPRT prepared triangle_match edge seed vertices must be valid graph vertex IDs");
        }
    }
    if (seed_count == 0 || prepared.edge_count == 0) {
        std::vector<RtdlTriangleRow> empty;
        *rows_out = copy_triangle_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlEdgeSeed> seed_values(seeds, seeds + seed_count);
    std::vector<uint32_t> row_count_device_host(1, 0u);
    DeviceAllocation seed_device(seed_values.size() * sizeof(RtdlEdgeSeed));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(seed_device, seed_values);
    copy_host_to_device(row_count_device, row_count_device_host);

    const size_t output_capacity = seed_count * static_cast<size_t>(prepared.edge_count);
    std::vector<RtdlHiprtTriangleCandidateRow> candidates(output_capacity);
    DeviceAllocation candidate_device(candidates.size() * sizeof(RtdlHiprtTriangleCandidateRow));
    void* seed_device_ptr = seed_device.get();
    void* row_offset_device_ptr = prepared.row_offset_device.get();
    void* column_device_ptr = prepared.column_device.get();
    void* edge_device_ptr = prepared.edge_device.get();
    void* candidate_device_ptr = candidate_device.get();
    void* row_count_device_ptr = row_count_device.get();
    uint32_t seed_count_u32 = static_cast<uint32_t>(seed_count);
    uint32_t enforce_u32 = enforce_id_ascending ? 1u : 0u;
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((seed_count + block_size - 1) / block_size);
    void* args[] = {
        &prepared.geometry,
        &seed_device_ptr,
        &seed_count_u32,
        &row_offset_device_ptr,
        &column_device_ptr,
        &edge_device_ptr,
        &prepared.edge_count,
        &prepared.vertex_count,
        &enforce_u32,
        &candidate_device_ptr,
        &row_count_device_ptr,
        &prepared.triangle_func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.triangle_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(row_count_device_host, row_count_device);
    const uint32_t produced = std::min<uint32_t>(row_count_device_host[0], static_cast<uint32_t>(candidates.size()));
    candidates.resize(produced);
    copy_device_to_host(candidates, candidate_device);
    std::sort(candidates.begin(), candidates.end(), [](const RtdlHiprtTriangleCandidateRow& a, const RtdlHiprtTriangleCandidateRow& b) {
        if (a.seed_index != b.seed_index) {
            return a.seed_index < b.seed_index;
        }
        if (a.w != b.w) {
            return a.w < b.w;
        }
        if (a.u != b.u) {
            return a.u < b.u;
        }
        return a.v < b.v;
    });

    std::vector<RtdlTriangleRow> output;
    output.reserve(candidates.size());
    for (const RtdlHiprtTriangleCandidateRow& candidate : candidates) {
        RtdlTriangleRow row{candidate.u, candidate.v, candidate.w};
        if (unique) {
            const bool seen = std::any_of(output.begin(), output.end(), [&](const RtdlTriangleRow& existing) {
                return existing.u == row.u && existing.v == row.v && existing.w == row.w;
            });
            if (seen) {
                continue;
            }
        }
        output.push_back(row);
    }
    *rows_out = copy_triangle_rows_to_heap(output);
    *row_count_out = output.size();
}

struct PreparedDbTable {
    HiprtRuntime runtime;
    std::vector<std::string> field_names;
    std::vector<uint32_t> field_kinds;
    std::vector<RtdlDbScalar> row_values;
    DeviceAllocation row_value_device;
    DeviceAllocation aabb_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction match_kernel{};
    uint32_t row_count{};
    uint32_t field_count{};

    ~PreparedDbTable() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
    }

    PreparedDbTable() = default;
    PreparedDbTable(const PreparedDbTable&) = delete;
    PreparedDbTable& operator=(const PreparedDbTable&) = delete;
};

std::vector<RtdlDbField> prepared_db_field_views(const PreparedDbTable& prepared) {
    std::vector<RtdlDbField> fields;
    fields.reserve(prepared.field_names.size());
    for (size_t index = 0; index < prepared.field_names.size(); ++index) {
        fields.push_back({prepared.field_names[index].c_str(), prepared.field_kinds[index]});
    }
    return fields;
}

std::unique_ptr<PreparedDbTable> prepare_db_table(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count) {
    if (row_count > std::numeric_limits<uint32_t>::max() || field_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT DB prepare currently supports at most 2^32-1 rows/fields");
    }
    if (field_count == 0 || fields == nullptr) {
        throw std::runtime_error("HIPRT DB prepare fields must not be empty");
    }
    if (row_count > 0 && row_values == nullptr) {
        throw std::runtime_error("HIPRT DB prepare row_values pointer must not be null when row_count is nonzero");
    }
    if (row_count == 0) {
        throw std::runtime_error("HIPRT DB prepare currently requires at least one row");
    }

    auto prepared = std::make_unique<PreparedDbTable>();
    prepared->field_names.reserve(field_count);
    prepared->field_kinds.reserve(field_count);
    for (size_t index = 0; index < field_count; ++index) {
        if (fields[index].name == nullptr) {
            throw std::runtime_error("HIPRT DB prepare field names must not be null");
        }
        prepared->field_names.emplace_back(fields[index].name);
        prepared->field_kinds.push_back(fields[index].kind);
    }
    prepared->row_values.assign(row_values, row_values + row_count * field_count);
    prepared->row_count = static_cast<uint32_t>(row_count);
    prepared->field_count = static_cast<uint32_t>(field_count);

    std::vector<RtdlHiprtAabb> aabb_values = encode_db_row_aabbs(row_count);
    prepared->runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);
    prepared->row_value_device = DeviceAllocation(prepared->row_values.size() * sizeof(RtdlDbScalar));
    prepared->aabb_device = DeviceAllocation(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(prepared->row_value_device, prepared->row_values);
    copy_host_to_device(prepared->aabb_device, aabb_values);
    prepared->geometry = build_aabb_geometry(prepared->runtime.context, prepared->aabb_device, aabb_values.size());

    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlDbRowAabb";
    hiprtFuncDataSet func_data_set{};
    func_data_set.intersectFuncData = nullptr;
    check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(prepared->runtime.context, 1, 1, prepared->func_table));
    check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(prepared->runtime.context, prepared->func_table, 0, 0, func_data_set));
    prepared->match_kernel = build_trace_kernel_from_source(
        prepared->runtime.context,
        db_match_kernel_source(),
        "rtdl_hiprt_db_match_prepared.cu",
        "RtdlDbMatchKernel",
        &func_name_set,
        1,
        1);
    return prepared;
}

std::vector<uint32_t> run_prepared_db_match_indices(
    PreparedDbTable& prepared,
    const RtdlDbClause* clauses,
    size_t clause_count) {
    if (clause_count > 0 && clauses == nullptr) {
        throw std::runtime_error("HIPRT prepared DB clauses pointer must not be null when clause_count is nonzero");
    }
    std::vector<RtdlDbField> fields = prepared_db_field_views(prepared);
    std::vector<RtdlHiprtDbClauseDevice> clause_values =
        encode_db_clauses_for_device(fields.data(), fields.size(), clauses, clause_count);
    std::vector<uint32_t> matched(prepared.row_count, 0u);
    std::vector<uint32_t> matched_count_host(1, 0u);
    DeviceAllocation clause_device(clause_values.size() * sizeof(RtdlHiprtDbClauseDevice));
    DeviceAllocation matched_device(matched.size() * sizeof(uint32_t));
    DeviceAllocation matched_count_device(sizeof(uint32_t));
    copy_host_to_device(clause_device, clause_values);
    copy_host_to_device(matched_count_device, matched_count_host);

    void* row_value_device_ptr = prepared.row_value_device.get();
    void* clause_device_ptr = clause_device.get();
    void* matched_device_ptr = matched_device.get();
    void* matched_count_device_ptr = matched_count_device.get();
    uint32_t clause_count_u32 = static_cast<uint32_t>(clause_values.size());
    void* args[] = {
        &prepared.geometry,
        &row_value_device_ptr,
        &prepared.row_count,
        &prepared.field_count,
        &clause_device_ptr,
        &clause_count_u32,
        &matched_device_ptr,
        &matched_count_device_ptr,
        &prepared.func_table,
    };
    constexpr uint32_t block_size = 128;
    const uint32_t grid_size = static_cast<uint32_t>((prepared.row_count + block_size - 1) / block_size);
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.match_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(matched_count_host, matched_count_device);
    const uint32_t produced = std::min<uint32_t>(matched_count_host[0], static_cast<uint32_t>(matched.size()));
    matched.resize(produced);
    copy_device_to_host(matched, matched_device);
    std::sort(matched.begin(), matched.end());
    return matched;
}

void run_prepared_db_conjunctive_scan(
    PreparedDbTable& prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out) {
    std::vector<RtdlDbField> fields = prepared_db_field_views(prepared);
    const size_t row_id_index = db_find_field_index_or_throw(fields.data(), fields.size(), "row_id");
    std::vector<uint32_t> matched = run_prepared_db_match_indices(prepared, clauses, clause_count);
    std::vector<RtdlDbRowIdRow> output;
    output.reserve(matched.size());
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& row_id = prepared.row_values[static_cast<size_t>(row_index) * prepared.field_count + row_id_index];
        if (!db_scalar_is_numeric(row_id)) {
            throw std::runtime_error("HIPRT prepared DB row_id must be numeric");
        }
        output.push_back({static_cast<uint32_t>(db_scalar_as_double(row_id))});
    }
    *rows_out = copy_db_row_id_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_prepared_db_grouped_count(
    PreparedDbTable& prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out) {
    std::vector<RtdlDbField> fields = prepared_db_field_views(prepared);
    const size_t group_index = db_find_field_index_or_throw(fields.data(), fields.size(), group_key_field);
    std::vector<uint32_t> matched = run_prepared_db_match_indices(prepared, clauses, clause_count);
    std::map<int64_t, int64_t> counts;
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& group_value = prepared.row_values[static_cast<size_t>(row_index) * prepared.field_count + group_index];
        if (!db_scalar_is_numeric(group_value)) {
            throw std::runtime_error("HIPRT prepared grouped_count requires numeric or text-encoded group keys");
        }
        counts[static_cast<int64_t>(db_scalar_as_double(group_value))] += 1;
    }
    std::vector<RtdlDbGroupedCountRow> output;
    output.reserve(counts.size());
    for (const auto& item : counts) {
        output.push_back({item.first, item.second});
    }
    *rows_out = copy_db_grouped_count_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_prepared_db_grouped_sum(
    PreparedDbTable& prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out) {
    std::vector<RtdlDbField> fields = prepared_db_field_views(prepared);
    const size_t group_index = db_find_field_index_or_throw(fields.data(), fields.size(), group_key_field);
    const size_t value_index = db_find_field_index_or_throw(fields.data(), fields.size(), value_field);
    std::vector<uint32_t> matched = run_prepared_db_match_indices(prepared, clauses, clause_count);
    std::map<int64_t, double> sums;
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& group_value = prepared.row_values[static_cast<size_t>(row_index) * prepared.field_count + group_index];
        const RtdlDbScalar& sum_value = prepared.row_values[static_cast<size_t>(row_index) * prepared.field_count + value_index];
        if (!db_scalar_is_numeric(group_value) || !db_scalar_is_numeric(sum_value)) {
            throw std::runtime_error("HIPRT prepared grouped_sum requires numeric or text-encoded group keys and numeric values");
        }
        sums[static_cast<int64_t>(db_scalar_as_double(group_value))] += db_scalar_as_double(sum_value);
    }
    std::vector<RtdlDbGroupedSumRow> output;
    output.reserve(sums.size());
    for (const auto& item : sums) {
        output.push_back({item.first, item.second});
    }
    *rows_out = copy_db_grouped_sum_rows_to_heap(output);
    *row_count_out = output.size();
}

std::vector<uint32_t> run_db_match_indices(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count) {
    if (row_count > std::numeric_limits<uint32_t>::max() || field_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT DB first wave currently supports at most 2^32-1 rows/fields");
    }
    if (field_count == 0 || fields == nullptr) {
        throw std::runtime_error("HIPRT DB fields must not be empty");
    }
    if (row_count > 0 && row_values == nullptr) {
        throw std::runtime_error("HIPRT DB row_values pointer must not be null when row_count is nonzero");
    }
    if (clause_count > 0 && clauses == nullptr) {
        throw std::runtime_error("HIPRT DB clauses pointer must not be null when clause_count is nonzero");
    }
    if (row_count == 0) {
        return {};
    }
    std::vector<RtdlHiprtDbClauseDevice> clause_values =
        encode_db_clauses_for_device(fields, field_count, clauses, clause_count);
    std::vector<RtdlDbScalar> row_value_vector(row_values, row_values + row_count * field_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_db_row_aabbs(row_count);
    std::vector<uint32_t> matched(row_count, 0u);
    std::vector<uint32_t> matched_count_host(1, 0u);

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation row_value_device(row_value_vector.size() * sizeof(RtdlDbScalar));
    DeviceAllocation clause_device(clause_values.size() * sizeof(RtdlHiprtDbClauseDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation matched_device(matched.size() * sizeof(uint32_t));
    DeviceAllocation matched_count_device(sizeof(uint32_t));
    copy_host_to_device(row_value_device, row_value_vector);
    copy_host_to_device(clause_device, clause_values);
    copy_host_to_device(aabb_device, aabb_values);
    copy_host_to_device(matched_count_device, matched_count_host);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlDbRowAabb";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            db_match_kernel_source(),
            "rtdl_hiprt_db_match.cu",
            "RtdlDbMatchKernel",
            &func_name_set,
            1,
            1);

        void* row_value_device_ptr = row_value_device.get();
        void* clause_device_ptr = clause_device.get();
        void* matched_device_ptr = matched_device.get();
        void* matched_count_device_ptr = matched_count_device.get();
        uint32_t row_count_u32 = static_cast<uint32_t>(row_count);
        uint32_t field_count_u32 = static_cast<uint32_t>(field_count);
        uint32_t clause_count_u32 = static_cast<uint32_t>(clause_values.size());
        void* args[] = {
            &geometry,
            &row_value_device_ptr,
            &row_count_u32,
            &field_count_u32,
            &clause_device_ptr,
            &clause_count_u32,
            &matched_device_ptr,
            &matched_count_device_ptr,
            &func_table,
        };
        constexpr uint32_t block_size = 128;
        const uint32_t grid_size = static_cast<uint32_t>((row_count + block_size - 1) / block_size);
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(matched_count_host, matched_count_device);
        const uint32_t produced = std::min<uint32_t>(matched_count_host[0], static_cast<uint32_t>(matched.size()));
        matched.resize(produced);
        copy_device_to_host(matched, matched_device);
        std::sort(matched.begin(), matched.end());
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
        }
        throw;
    }
    if (func_table != nullptr) {
        hiprtDestroyFuncTable(runtime.context, func_table);
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(runtime.context, geometry);
    }
    return matched;
}

void run_db_conjunctive_scan(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out) {
    const size_t row_id_index = db_find_field_index_or_throw(fields, field_count, "row_id");
    std::vector<uint32_t> matched = run_db_match_indices(fields, field_count, row_values, row_count, clauses, clause_count);
    std::vector<RtdlDbRowIdRow> output;
    output.reserve(matched.size());
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& row_id = row_values[static_cast<size_t>(row_index) * field_count + row_id_index];
        if (!db_scalar_is_numeric(row_id)) {
            throw std::runtime_error("HIPRT DB row_id must be numeric");
        }
        output.push_back({static_cast<uint32_t>(db_scalar_as_double(row_id))});
    }
    *rows_out = copy_db_row_id_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_db_grouped_count(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out) {
    const size_t group_index = db_find_field_index_or_throw(fields, field_count, group_key_field);
    std::vector<uint32_t> matched = run_db_match_indices(fields, field_count, row_values, row_count, clauses, clause_count);
    std::map<int64_t, int64_t> counts;
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& group_value = row_values[static_cast<size_t>(row_index) * field_count + group_index];
        if (!db_scalar_is_numeric(group_value)) {
            throw std::runtime_error("HIPRT grouped_count requires numeric or text-encoded group keys");
        }
        counts[static_cast<int64_t>(db_scalar_as_double(group_value))] += 1;
    }
    std::vector<RtdlDbGroupedCountRow> output;
    output.reserve(counts.size());
    for (const auto& item : counts) {
        output.push_back({item.first, item.second});
    }
    *rows_out = copy_db_grouped_count_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_db_grouped_sum(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out) {
    const size_t group_index = db_find_field_index_or_throw(fields, field_count, group_key_field);
    const size_t value_index = db_find_field_index_or_throw(fields, field_count, value_field);
    std::vector<uint32_t> matched = run_db_match_indices(fields, field_count, row_values, row_count, clauses, clause_count);
    std::map<int64_t, double> sums;
    for (uint32_t row_index : matched) {
        const RtdlDbScalar& group_value = row_values[static_cast<size_t>(row_index) * field_count + group_index];
        const RtdlDbScalar& sum_value = row_values[static_cast<size_t>(row_index) * field_count + value_index];
        if (!db_scalar_is_numeric(group_value) || !db_scalar_is_numeric(sum_value)) {
            throw std::runtime_error("HIPRT grouped_sum requires numeric or text-encoded group keys and numeric values");
        }
        sums[static_cast<int64_t>(db_scalar_as_double(group_value))] += db_scalar_as_double(sum_value);
    }
    std::vector<RtdlDbGroupedSumRow> output;
    output.reserve(sums.size());
    for (const auto& item : sums) {
        output.push_back({item.first, item.second});
    }
    *rows_out = copy_db_grouped_sum_rows_to_heap(output);
    *row_count_out = output.size();
}

int handle_call(const std::function<void()>& fn, char* error_out, size_t error_size) {
    set_message(error_out, error_size, "");
    try {
        fn();
        return 0;
    } catch (const std::exception& exc) {
        set_message(error_out, error_size, exc.what());
        return 1;
    } catch (...) {
        set_message(error_out, error_size, "unknown HIPRT backend error");
        return 1;
    }
}

}  // namespace
