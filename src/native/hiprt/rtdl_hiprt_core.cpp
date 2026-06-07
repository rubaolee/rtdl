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

struct PreparedRayAnyhit2D {
    HiprtRuntime runtime;
    DeviceAllocation triangle_device;
    DeviceAllocation aabb_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction kernel{};
    oroFunction grouped_kernel{};
    bool empty_scene{false};

    explicit PreparedRayAnyhit2D(bool empty_scene_in) : empty_scene(empty_scene_in) {}

    PreparedRayAnyhit2D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& triangle_device_in,
        DeviceAllocation&& aabb_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable func_table_in)
        : runtime(std::move(runtime_in)),
          triangle_device(std::move(triangle_device_in)),
          aabb_device(std::move(aabb_device_in)),
          geometry(geometry_in),
          func_table(func_table_in),
          empty_scene(false) {}

    ~PreparedRayAnyhit2D() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
            func_table = nullptr;
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedRayAnyhit2D(const PreparedRayAnyhit2D&) = delete;
    PreparedRayAnyhit2D& operator=(const PreparedRayAnyhit2D&) = delete;
    PreparedRayAnyhit2D(PreparedRayAnyhit2D&&) = delete;
    PreparedRayAnyhit2D& operator=(PreparedRayAnyhit2D&&) = delete;
};

struct PreparedSegmentPairIntersection2D {
    HiprtRuntime runtime;
    DeviceAllocation right_device;
    DeviceAllocation aabb_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction count_kernel{};
    size_t right_count{0};
    bool empty_scene{false};

    explicit PreparedSegmentPairIntersection2D(bool empty_scene_in) : empty_scene(empty_scene_in) {}

    PreparedSegmentPairIntersection2D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& right_device_in,
        DeviceAllocation&& aabb_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable func_table_in,
        size_t right_count_in)
        : runtime(std::move(runtime_in)),
          right_device(std::move(right_device_in)),
          aabb_device(std::move(aabb_device_in)),
          geometry(geometry_in),
          func_table(func_table_in),
          right_count(right_count_in),
          empty_scene(false) {}

    ~PreparedSegmentPairIntersection2D() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
            func_table = nullptr;
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedSegmentPairIntersection2D(const PreparedSegmentPairIntersection2D&) = delete;
    PreparedSegmentPairIntersection2D& operator=(const PreparedSegmentPairIntersection2D&) = delete;
    PreparedSegmentPairIntersection2D(PreparedSegmentPairIntersection2D&&) = delete;
    PreparedSegmentPairIntersection2D& operator=(PreparedSegmentPairIntersection2D&&) = delete;
};

struct PreparedShapePairActiveCount2D {
    HiprtRuntime runtime;
    DeviceAllocation right_device;
    DeviceAllocation right_vertex_device;
    hiprtFuncTable func_table{};
    oroFunction count_kernel{};
    size_t right_count{0};
    size_t right_vertex_count{0};
    bool empty_scene{false};

    explicit PreparedShapePairActiveCount2D(bool empty_scene_in) : empty_scene(empty_scene_in) {}

    PreparedShapePairActiveCount2D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& right_device_in,
        DeviceAllocation&& right_vertex_device_in,
        hiprtFuncTable func_table_in,
        size_t right_count_in,
        size_t right_vertex_count_in)
        : runtime(std::move(runtime_in)),
          right_device(std::move(right_device_in)),
          right_vertex_device(std::move(right_vertex_device_in)),
          func_table(func_table_in),
          right_count(right_count_in),
          right_vertex_count(right_vertex_count_in),
          empty_scene(false) {}

    ~PreparedShapePairActiveCount2D() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
            func_table = nullptr;
        }
    }

    PreparedShapePairActiveCount2D(const PreparedShapePairActiveCount2D&) = delete;
    PreparedShapePairActiveCount2D& operator=(const PreparedShapePairActiveCount2D&) = delete;
    PreparedShapePairActiveCount2D(PreparedShapePairActiveCount2D&&) = delete;
    PreparedShapePairActiveCount2D& operator=(PreparedShapePairActiveCount2D&&) = delete;
};

struct PreparedAabbIndex2D {
    HiprtRuntime runtime;
    DeviceAllocation box_device;
    DeviceAllocation aabb_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction count_kernel{};
    size_t box_count{0};
    bool empty_scene{false};

    explicit PreparedAabbIndex2D(bool empty_scene_in) : empty_scene(empty_scene_in) {}

    PreparedAabbIndex2D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& box_device_in,
        DeviceAllocation&& aabb_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable func_table_in,
        size_t box_count_in)
        : runtime(std::move(runtime_in)),
          box_device(std::move(box_device_in)),
          aabb_device(std::move(aabb_device_in)),
          geometry(geometry_in),
          func_table(func_table_in),
          box_count(box_count_in),
          empty_scene(false) {}

    ~PreparedAabbIndex2D() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
            func_table = nullptr;
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedAabbIndex2D(const PreparedAabbIndex2D&) = delete;
    PreparedAabbIndex2D& operator=(const PreparedAabbIndex2D&) = delete;
    PreparedAabbIndex2D(PreparedAabbIndex2D&&) = delete;
    PreparedAabbIndex2D& operator=(PreparedAabbIndex2D&&) = delete;
};

struct PreparedFixedRadiusNeighbors3D {
    HiprtRuntime runtime;
    DeviceAllocation search_device;
    DeviceAllocation aabb_device;
    DeviceAllocation params_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction kernel{};
    oroFunction threshold_count_kernel{};
    oroFunction threshold_flags_kernel{};
    oroFunction ranked_aggregate_kernel{};
    size_t search_count{};
    float max_radius{};

    PreparedFixedRadiusNeighbors3D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& search_device_in,
        DeviceAllocation&& aabb_device_in,
        DeviceAllocation&& params_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable func_table_in,
        oroFunction kernel_in,
        size_t search_count_in,
        float max_radius_in)
        : runtime(std::move(runtime_in)),
          search_device(std::move(search_device_in)),
          aabb_device(std::move(aabb_device_in)),
          params_device(std::move(params_device_in)),
          geometry(geometry_in),
          func_table(func_table_in),
          kernel(kernel_in),
          search_count(search_count_in),
          max_radius(max_radius_in) {}

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

struct PreparedPointGroupNearestWitness2D {
    HiprtRuntime runtime;
    DeviceAllocation search_device;
    DeviceAllocation group_device;
    DeviceAllocation aabb_device;
    DeviceAllocation params_device;
    hiprtGeometry geometry{};
    hiprtFuncTable func_table{};
    oroFunction witness_kernel{};
    oroFunction max_reduce_kernel{};
    oroFunction split_columns_kernel{};
    size_t search_count{};
    size_t group_count{};
    float max_radius{};

    PreparedPointGroupNearestWitness2D(
        HiprtRuntime&& runtime_in,
        DeviceAllocation&& search_device_in,
        DeviceAllocation&& group_device_in,
        DeviceAllocation&& aabb_device_in,
        DeviceAllocation&& params_device_in,
        hiprtGeometry geometry_in,
        hiprtFuncTable func_table_in,
        oroFunction witness_kernel_in,
        size_t search_count_in,
        size_t group_count_in,
        float max_radius_in)
        : runtime(std::move(runtime_in)),
          search_device(std::move(search_device_in)),
          group_device(std::move(group_device_in)),
          aabb_device(std::move(aabb_device_in)),
          params_device(std::move(params_device_in)),
          geometry(geometry_in),
          func_table(func_table_in),
          witness_kernel(witness_kernel_in),
          search_count(search_count_in),
          group_count(group_count_in),
          max_radius(max_radius_in) {}

    ~PreparedPointGroupNearestWitness2D() {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
            func_table = nullptr;
        }
        if (geometry != nullptr) {
            hiprtDestroyGeometry(runtime.context, geometry);
            geometry = nullptr;
        }
    }

    PreparedPointGroupNearestWitness2D(const PreparedPointGroupNearestWitness2D&) = delete;
    PreparedPointGroupNearestWitness2D& operator=(const PreparedPointGroupNearestWitness2D&) = delete;
    PreparedPointGroupNearestWitness2D(PreparedPointGroupNearestWitness2D&&) = delete;
    PreparedPointGroupNearestWitness2D& operator=(PreparedPointGroupNearestWitness2D&&) = delete;
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
    oroFunction triangle_count_kernel{};
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
        oroFunction triangle_count_kernel_in,
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
          triangle_count_kernel(triangle_count_kernel_in),
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

void validate_aabb2d_bounds(double min_x, double min_y, double max_x, double max_y) {
    const double values[4] = {min_x, min_y, max_x, max_y};
    for (double value : values) {
        if (!std::isfinite(value)) {
            throw std::runtime_error("AABB coordinates must be finite");
        }
    }
    if (max_x < min_x || max_y < min_y) {
        throw std::runtime_error("AABB max bounds must be greater than or equal to min bounds");
    }
}

std::vector<RtdlHiprtAabb2DDevice> encode_aabbs_2d(const RtdlAabb2D* boxes, size_t box_count) {
    std::vector<RtdlHiprtAabb2DDevice> values;
    values.reserve(box_count);
    for (size_t i = 0; i < box_count; ++i) {
        validate_aabb2d_bounds(boxes[i].min_x, boxes[i].min_y, boxes[i].max_x, boxes[i].max_y);
        RtdlHiprtAabb2DDevice packed{
            boxes[i].id,
            static_cast<float>(boxes[i].min_x),
            static_cast<float>(boxes[i].min_y),
            static_cast<float>(boxes[i].max_x),
            static_cast<float>(boxes[i].max_y),
        };
        if (!std::isfinite(packed.min_x) || !std::isfinite(packed.min_y)
                || !std::isfinite(packed.max_x) || !std::isfinite(packed.max_y)) {
            throw std::runtime_error("AABB coordinates are outside float32 HIPRT execution range");
        }
        values.push_back(packed);
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

std::vector<RtdlHiprtAabb> encode_aabb_index_aabbs(const RtdlHiprtAabb2DDevice* boxes, size_t box_count) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(box_count);
    constexpr float eps = 1.0e-4f;
    for (size_t i = 0; i < box_count; ++i) {
        aabbs.push_back({
            {std::min(boxes[i].min_x, boxes[i].max_x) - eps, std::min(boxes[i].min_y, boxes[i].max_y) - eps, -eps, 0.0f},
            {std::max(boxes[i].min_x, boxes[i].max_x) + eps, std::max(boxes[i].min_y, boxes[i].max_y) + eps, eps, 0.0f},
        });
    }
    return aabbs;
}

std::vector<RtdlHiprtPointGroupBounds2DDevice> encode_point_group_bounds_2d(
    const RtdlPointGroupBounds2D* groups,
    size_t group_count,
    size_t search_count) {
    std::vector<RtdlHiprtPointGroupBounds2DDevice> values;
    values.reserve(group_count);
    for (size_t i = 0; i < group_count; ++i) {
        validate_aabb2d_bounds(groups[i].min_x, groups[i].min_y, groups[i].max_x, groups[i].max_y);
        const uint64_t offset = static_cast<uint64_t>(groups[i].point_offset);
        const uint64_t count = static_cast<uint64_t>(groups[i].point_count);
        if (count == 0) {
            throw std::runtime_error("point_group_nearest group point_count must be positive");
        }
        if (offset + count > static_cast<uint64_t>(search_count)) {
            throw std::runtime_error("point_group_nearest group point span exceeds search point count");
        }
        RtdlHiprtPointGroupBounds2DDevice packed{
            static_cast<float>(groups[i].min_x),
            static_cast<float>(groups[i].min_y),
            static_cast<float>(groups[i].max_x),
            static_cast<float>(groups[i].max_y),
            groups[i].id,
            groups[i].point_offset,
            groups[i].point_count,
            0u,
        };
        if (!std::isfinite(packed.min_x) || !std::isfinite(packed.min_y)
                || !std::isfinite(packed.max_x) || !std::isfinite(packed.max_y)) {
            throw std::runtime_error("point_group_nearest group bounds are outside float32 HIPRT execution range");
        }
        values.push_back(packed);
    }
    return values;
}

std::vector<RtdlHiprtAabb> encode_point_group_bounds_aabbs_2d(
    const RtdlHiprtPointGroupBounds2DDevice* groups,
    size_t group_count,
    float max_radius) {
    std::vector<RtdlHiprtAabb> aabbs;
    aabbs.reserve(group_count);
    constexpr float eps = 1.0e-4f;
    const float pad = max_radius + eps;
    const float z_pad = std::max(max_radius, eps);
    for (size_t i = 0; i < group_count; ++i) {
        aabbs.push_back({
            {groups[i].min_x - pad, groups[i].min_y - pad, -z_pad, 0.0f},
            {groups[i].max_x + pad, groups[i].max_y + pad, z_pad, 0.0f},
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

std::vector<RtdlHiprtAabb> encode_shape_pair_candidate_aabbs(
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

std::vector<RtdlHiprtAabb> encode_shape_pair_left_envelope_aabbs(
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

RtdlRayAnyHitRow* copy_rows_to_heap(const std::vector<RtdlRayAnyHitRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlRayAnyHitRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlRayAnyHitRow));
    }
    return reinterpret_cast<RtdlRayAnyHitRow*>(rows);
}

RtdlRayClosestHitRow* copy_rows_to_heap(const std::vector<RtdlRayClosestHitRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlRayClosestHitRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlRayClosestHitRow));
    }
    return reinterpret_cast<RtdlRayClosestHitRow*>(rows);
}

RtdlSegmentPairIntersectionRow* copy_segment_intersection_rows_to_heap(const std::vector<RtdlSegmentPairIntersectionRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlSegmentPairIntersectionRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlSegmentPairIntersectionRow));
    }
    return reinterpret_cast<RtdlSegmentPairIntersectionRow*>(rows);
}

RtdlPipRow* copy_pip_rows_to_heap(const std::vector<RtdlPipRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlPipRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlPipRow));
    }
    return reinterpret_cast<RtdlPipRow*>(rows);
}

RtdlShapePairRelationRow* copy_shape_pair_relation_rows_to_heap(const std::vector<RtdlShapePairRelationRow>& output) {
    auto* rows = new unsigned char[output.size() * sizeof(RtdlShapePairRelationRow)];
    if (!output.empty()) {
        std::memcpy(rows, output.data(), output.size() * sizeof(RtdlShapePairRelationRow));
    }
    return reinterpret_cast<RtdlShapePairRelationRow*>(rows);
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

void validate_canonical_unique_edge_seeds(
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    uint32_t vertex_count,
    const char* label) {
    if (seed_count > 0 && seeds == nullptr) {
        throw std::runtime_error(std::string(label) + " seed pointer must not be null when seed_count is nonzero");
    }
    std::vector<std::pair<uint32_t, uint32_t>> pairs;
    pairs.reserve(seed_count);
    for (size_t i = 0; i < seed_count; ++i) {
        const uint32_t u = seeds[i].u;
        const uint32_t v = seeds[i].v;
        if (u >= vertex_count || v >= vertex_count) {
            throw std::runtime_error(std::string(label) + " seed vertices must be valid graph vertex IDs");
        }
        if (!(u < v)) {
            throw std::runtime_error(std::string(label) + " scalar count requires canonical ascending edge seeds");
        }
        pairs.emplace_back(u, v);
    }
    std::sort(pairs.begin(), pairs.end());
    if (std::adjacent_find(pairs.begin(), pairs.end()) != pairs.end()) {
        throw std::runtime_error(std::string(label) + " scalar count requires unique edge seeds");
    }
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

std::string replace_all_copy(std::string src, const std::string& from, const std::string& to) {
    size_t pos = 0;
    while ((pos = src.find(from, pos)) != std::string::npos) {
        src.replace(pos, from.size(), to);
        pos += to.size();
    }
    return src;
}

std::string ray_anyhit_kernel_source_3d() {
    std::string src = ray_hitcount_kernel_source();
    src = replace_all_copy(src, "RtdlRayHitcount3DKernel", "RtdlRayAnyhit3DKernel");
    src = replace_all_copy(src, "RtdlRayHitCountRow", "RtdlRayAnyHitRow");
    src = replace_all_copy(src, "hit_count", "any_hit");
    src = replace_all_copy(src, "++any_hit;", "any_hit = 1u;\n            break;");
    return src;
}

std::string ray_anyhit_kernel_source_2d() {
    std::string src = ray_hitcount_2d_kernel_source();
    src = replace_all_copy(src, "RtdlRayHitcount2DKernel", "RtdlRayAnyhit2DKernel");
    src = replace_all_copy(src, "RtdlRayHitCountRow", "RtdlRayAnyHitRow");
    src = replace_all_copy(src, "hit_count", "any_hit");
    src = replace_all_copy(src, "++any_hit;", "any_hit = 1u;\n            break;");
    return src;
}

std::string grouped_ray_anyhit_kernel_source_2d() {
    std::string src = ray_hitcount_2d_kernel_source();
    src += R"KERNEL(

extern "C" __global__ void RtdlGroupedRayAnyhit2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtRay2DDevice* rays,
    const uint32_t* group_indices,
    uint32_t ray_count,
    uint32_t group_count,
    uint32_t* group_flags,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= ray_count) {
        return;
    }
    const uint32_t group = group_indices[index];
    if (group >= group_count) {
        return;
    }

    const RtdlHiprtRay2DDevice in = rays[index];
    hiprtRay ray;
    ray.origin = {in.ox, in.oy, 0.0f};
    ray.direction = {in.dx * in.tmax, in.dy * in.tmax, 0.0f};
    ray.minT = 0.0f;
    ray.maxT = 1.0f;

    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (hit.hasHit()) {
            atomicExch(&group_flags[group], 1u);
            break;
        }
    }
}
)KERNEL";
    return src;
}

oroFunction ensure_ray_anyhit_kernel_2d(PreparedRayAnyhit2D& prepared) {
    if (prepared.kernel != nullptr) {
        return prepared.kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlTriangle2D";
    const std::string source = ray_anyhit_kernel_source_2d();
    prepared.kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        source.c_str(),
        "rtdl_hiprt_ray_anyhit_2d.cu",
        "RtdlRayAnyhit2DKernel",
        &func_name_set,
        1,
        1);
    return prepared.kernel;
}

oroFunction ensure_grouped_ray_anyhit_kernel_2d(PreparedRayAnyhit2D& prepared) {
    if (prepared.grouped_kernel != nullptr) {
        return prepared.grouped_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlTriangle2D";
    const std::string source = grouped_ray_anyhit_kernel_source_2d();
    prepared.grouped_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        source.c_str(),
        "rtdl_hiprt_grouped_ray_anyhit_2d.cu",
        "RtdlGroupedRayAnyhit2DKernel",
        &func_name_set,
        1,
        1);
    return prepared.grouped_kernel;
}

std::string segment_pair_intersection_count_kernel_source_2d() {
    std::string src = segment_pair_intersection_2d_kernel_source();
    src += R"KERNEL(

extern "C" __global__ void RtdlSegmentPairIntersectionCount2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtSegmentDevice* left_segments,
    uint32_t left_count,
    unsigned long long* total_count,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= left_count) {
        return;
    }
    const RtdlHiprtSegmentDevice left = left_segments[index];
    hiprtRay ray;
    ray.origin = {left.x0, left.y0, 0.0f};
    ray.direction = {left.x1 - left.x0, left.y1 - left.y0, 0.0f};
    ray.minT = 0.0f;
    ray.maxT = 1.0f;

    unsigned int local_count = 0u;
    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (hit.hasHit()) {
            ++local_count;
        }
    }
    if (local_count != 0u) {
        atomicAdd(total_count, static_cast<unsigned long long>(local_count));
    }
}
)KERNEL";
    return src;
}

oroFunction ensure_segment_pair_intersection_count_kernel_2d(PreparedSegmentPairIntersection2D& prepared) {
    if (prepared.count_kernel != nullptr) {
        return prepared.count_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlSegment2D";
    const std::string source = segment_pair_intersection_count_kernel_source_2d();
    prepared.count_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        source.c_str(),
        "rtdl_hiprt_segment_pair_intersection_count_2d.cu",
        "RtdlSegmentPairIntersectionCount2DKernel",
        &func_name_set,
        1,
        1);
    return prepared.count_kernel;
}

std::string shape_pair_active_count_kernel_source_2d() {
    std::string src = shape_pair_relation_flags_2d_kernel_source();
    src += R"KERNEL(

extern "C" __global__ void RtdlShapePairActiveCount2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPolygonRefDevice* left_polygons,
    const RtdlHiprtVertex2DDevice* left_vertices,
    const RtdlHiprtPolygonRefDevice* right_polygons,
    const RtdlHiprtVertex2DDevice* right_vertices,
    uint32_t left_count,
    uint32_t right_count,
    unsigned long long* active_count,
    hiprtFuncTable table) {
    const uint32_t left_index = blockIdx.x * blockDim.x + threadIdx.x;
    if (left_index >= left_count) {
        return;
    }
    const RtdlHiprtPolygonRefDevice left = left_polygons[left_index];
    const RtdlHiprtVertex2DDevice left_first = left_vertices[left.vertex_offset];

    hiprtRay ray;
    ray.origin = {left_first.x, left_first.y, 0.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = 0.0f;

    unsigned int local_count = 0u;
    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, nullptr, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit()) {
            continue;
        }
        const uint32_t right_index = hit.primID;
        if (right_index >= right_count) {
            continue;
        }
        const RtdlHiprtPolygonRefDevice right = right_polygons[right_index];
        const RtdlHiprtVertex2DDevice right_first = right_vertices[right.vertex_offset];
        const bool segment_intersection = polygonsHaveSegmentIntersection2D(left, left_vertices, right, right_vertices);
        const bool left_in_right = pointInPolygon2D(left_first.x, left_first.y, right, right_vertices);
        const bool right_in_left = pointInPolygon2D(right_first.x, right_first.y, left, left_vertices);
        if (segment_intersection || left_in_right || right_in_left) {
            ++local_count;
        }
    }
    if (local_count != 0u) {
        atomicAdd(active_count, static_cast<unsigned long long>(local_count));
    }
}
)KERNEL";
    return src;
}

oroFunction ensure_shape_pair_active_count_kernel_2d(PreparedShapePairActiveCount2D& prepared) {
    if (prepared.count_kernel != nullptr) {
        return prepared.count_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlShapePairCandidate2D";
    const std::string source = shape_pair_active_count_kernel_source_2d();
    prepared.count_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        source.c_str(),
        "rtdl_hiprt_shape_pair_active_count_2d.cu",
        "RtdlShapePairActiveCount2DKernel",
        &func_name_set,
        1,
        1);
    return prepared.count_kernel;
}

std::string fixed_radius_threshold_count_kernel_source_3d() {
    std::string src = fixed_radius_neighbors_3d_kernel_source();
    src += R"KERNEL(

extern "C" __global__ void RtdlFixedRadiusThresholdReachedCount3DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPoint3DDevice* queries,
    uint32_t query_count,
    uint32_t threshold,
    unsigned long long* threshold_reached_count,
    RtdlHiprtFixedRadiusParams* params,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= query_count || threshold == 0u) {
        return;
    }
    const RtdlHiprtPoint3DDevice query = queries[index];
    hiprtRay ray;
    ray.origin = {query.x, query.y, query.z};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = params->radius;

    uint32_t local_count = 0u;
    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, params, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit()) {
            continue;
        }
        ++local_count;
        if (local_count >= threshold) {
            atomicAdd(threshold_reached_count, 1ull);
            return;
        }
    }
}
)KERNEL";
    return src;
}

oroFunction ensure_fixed_radius_threshold_count_kernel_3d(PreparedFixedRadiusNeighbors3D& prepared) {
    if (prepared.threshold_count_kernel != nullptr) {
        return prepared.threshold_count_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlPointRadius3D";
    const std::string source = fixed_radius_threshold_count_kernel_source_3d();
    prepared.threshold_count_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        source.c_str(),
        "rtdl_hiprt_fixed_radius_threshold_count_3d.cu",
        "RtdlFixedRadiusThresholdReachedCount3DKernel",
        &func_name_set,
        1,
        1);
    return prepared.threshold_count_kernel;
}

std::string fixed_radius_threshold_flags_kernel_source_3d() {
    std::string src = fixed_radius_neighbors_3d_kernel_source();
    src += R"KERNEL(

extern "C" __global__ void RtdlFixedRadiusThresholdFlags3DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPoint3DDevice* queries,
    uint32_t query_count,
    uint32_t threshold,
    uint32_t* threshold_flags,
    RtdlHiprtFixedRadiusParams* params,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= query_count) {
        return;
    }
    threshold_flags[index] = 0u;
    if (threshold == 0u) {
        threshold_flags[index] = 1u;
        return;
    }
    const RtdlHiprtPoint3DDevice query = queries[index];
    hiprtRay ray;
    ray.origin = {query.x, query.y, query.z};
    ray.direction = {0.0f, 0.0f, 1.0f};
    ray.minT = 0.0f;
    ray.maxT = params->radius;

    uint32_t local_count = 0u;
    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, params, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (!hit.hasHit()) {
            continue;
        }
        ++local_count;
        if (local_count >= threshold) {
            threshold_flags[index] = 1u;
            return;
        }
    }
}
)KERNEL";
    return src;
}

oroFunction ensure_fixed_radius_threshold_flags_kernel_3d(PreparedFixedRadiusNeighbors3D& prepared) {
    if (prepared.threshold_flags_kernel != nullptr) {
        return prepared.threshold_flags_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlPointRadius3D";
    const std::string source = fixed_radius_threshold_flags_kernel_source_3d();
    prepared.threshold_flags_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        source.c_str(),
        "rtdl_hiprt_fixed_radius_threshold_flags_3d.cu",
        "RtdlFixedRadiusThresholdFlags3DKernel",
        &func_name_set,
        1,
        1);
    return prepared.threshold_flags_kernel;
}

std::string fixed_radius_ranked_aggregate_kernel_source_3d() {
    std::string src = fixed_radius_neighbors_3d_kernel_source();
    src += R"KERNEL(

struct RtdlFixedRadiusRankedNeighborAggregate {
    unsigned long long query_count;
    unsigned long long bounded_neighbor_count;
    unsigned long long nearest_id_checksum;
    unsigned long long kth_id_checksum;
    double sum_distance;
};

extern "C" __global__ void RtdlFixedRadiusRankedSummaryAggregate3DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPoint3DDevice* queries,
    const RtdlHiprtPoint3DDevice* search_points,
    uint32_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusRankedNeighborAggregate* aggregate,
    RtdlHiprtFixedRadiusParams* params,
    hiprtFuncTable table) {
    __shared__ unsigned long long s_query_count[128];
    __shared__ unsigned long long s_neighbor_count[128];
    __shared__ unsigned long long s_nearest_checksum[128];
    __shared__ unsigned long long s_kth_checksum[128];
    __shared__ double s_sum_distance[128];

    const uint32_t tid = threadIdx.x;
    unsigned long long local_query_count = 0ull;
    unsigned long long local_neighbor_count = 0ull;
    unsigned long long local_nearest_checksum = 0ull;
    unsigned long long local_kth_checksum = 0ull;
    double local_sum_distance = 0.0;

    for (uint32_t index = blockIdx.x * blockDim.x + tid;
         index < query_count;
         index += blockDim.x * gridDim.x) {
        local_query_count += 1ull;
        if (k_max == 0u || k_max > 64u) {
            continue;
        }

        const RtdlHiprtPoint3DDevice query = queries[index];
        float best_dist[64];
        uint32_t best_id[64];
        uint32_t count = 0u;
        for (uint32_t i = 0; i < k_max; ++i) {
            best_dist[i] = 3.402823466e+38F;
            best_id[i] = 0xFFFFFFFFu;
        }

        hiprtRay ray;
        ray.origin = {query.x, query.y, query.z};
        ray.direction = {0.0f, 0.0f, 1.0f};
        ray.minT = 0.0f;
        ray.maxT = 0.0f;

        hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, params, table);
        while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
            hiprtHit hit = traversal.getNextHit();
            if (!hit.hasHit()) {
                continue;
            }
            const RtdlHiprtPoint3DDevice neighbor = search_points[hit.primID];
            const float dist = hit.t;
            uint32_t insert_at = count < k_max ? count : k_max;
            for (uint32_t pos = 0; pos < count && pos < k_max; ++pos) {
                if (dist < best_dist[pos] || (dist == best_dist[pos] && neighbor.id < best_id[pos])) {
                    insert_at = pos;
                    break;
                }
            }
            if (insert_at >= k_max) {
                continue;
            }
            const uint32_t limit = count < k_max ? count : k_max - 1u;
            for (uint32_t pos = limit; pos > insert_at; --pos) {
                best_dist[pos] = best_dist[pos - 1u];
                best_id[pos] = best_id[pos - 1u];
            }
            best_dist[insert_at] = dist;
            best_id[insert_at] = neighbor.id;
            if (count < k_max) {
                ++count;
            }
        }

        local_neighbor_count += static_cast<unsigned long long>(count);
        if (count == 0u) {
            local_nearest_checksum += 0xffffffffull;
            local_kth_checksum += 0xffffffffull;
            continue;
        }
        local_nearest_checksum += static_cast<unsigned long long>(best_id[0]);
        local_kth_checksum += static_cast<unsigned long long>(best_id[count - 1u]);
        for (uint32_t rank = 0; rank < count; ++rank) {
            local_sum_distance += static_cast<double>(best_dist[rank]);
        }
    }

    s_query_count[tid] = local_query_count;
    s_neighbor_count[tid] = local_neighbor_count;
    s_nearest_checksum[tid] = local_nearest_checksum;
    s_kth_checksum[tid] = local_kth_checksum;
    s_sum_distance[tid] = local_sum_distance;
    __syncthreads();

    for (uint32_t stride = blockDim.x >> 1u; stride > 0u; stride >>= 1u) {
        if (tid < stride) {
            s_query_count[tid] += s_query_count[tid + stride];
            s_neighbor_count[tid] += s_neighbor_count[tid + stride];
            s_nearest_checksum[tid] += s_nearest_checksum[tid + stride];
            s_kth_checksum[tid] += s_kth_checksum[tid + stride];
            s_sum_distance[tid] += s_sum_distance[tid + stride];
        }
        __syncthreads();
    }

    if (tid == 0u) {
        atomicAdd(&aggregate->query_count, s_query_count[0]);
        atomicAdd(&aggregate->bounded_neighbor_count, s_neighbor_count[0]);
        atomicAdd(&aggregate->nearest_id_checksum, s_nearest_checksum[0]);
        atomicAdd(&aggregate->kth_id_checksum, s_kth_checksum[0]);
        atomicAdd(&aggregate->sum_distance, s_sum_distance[0]);
    }
}
)KERNEL";
    return src;
}

oroFunction ensure_fixed_radius_ranked_aggregate_kernel_3d(PreparedFixedRadiusNeighbors3D& prepared) {
    if (prepared.ranked_aggregate_kernel != nullptr) {
        return prepared.ranked_aggregate_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlPointRadius3D";
    const std::string source = fixed_radius_ranked_aggregate_kernel_source_3d();
    prepared.ranked_aggregate_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        source.c_str(),
        "rtdl_hiprt_fixed_radius_ranked_summary_aggregate_3d.cu",
        "RtdlFixedRadiusRankedSummaryAggregate3DKernel",
        &func_name_set,
        1,
        1);
    return prepared.ranked_aggregate_kernel;
}

oroFunction ensure_point_group_nearest_max_distance_kernel_2d(PreparedPointGroupNearestWitness2D& prepared) {
    if (prepared.max_reduce_kernel != nullptr) {
        return prepared.max_reduce_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlPointGroupBounds2D";
    prepared.max_reduce_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        point_group_nearest_witness_2d_kernel_source(),
        "rtdl_hiprt_point_group_nearest_witness_2d.cu",
        "RtdlPointGroupNearestMaxDistance2DKernel",
        &func_name_set,
        1,
        1);
    return prepared.max_reduce_kernel;
}

oroFunction ensure_point_group_nearest_split_columns_kernel_2d(PreparedPointGroupNearestWitness2D& prepared) {
    if (prepared.split_columns_kernel != nullptr) {
        return prepared.split_columns_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlPointGroupBounds2D";
    prepared.split_columns_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        point_group_nearest_witness_2d_kernel_source(),
        "rtdl_hiprt_point_group_nearest_witness_2d.cu",
        "RtdlPointGroupNearestWitness2DSplitColumnsKernel",
        &func_name_set,
        1,
        1);
    return prepared.split_columns_kernel;
}

const char* aabb_index_count_kernel_source_2d() {
    return R"KERNEL(
#include <hiprt/hiprt_device.h>
#include <hiprt/hiprt_vec.h>

struct RtdlHiprtPoint2DDevice {
    uint32_t id;
    float x;
    float y;
};

struct RtdlHiprtAabb2DDevice {
    uint32_t id;
    float min_x;
    float min_y;
    float max_x;
    float max_y;
};

struct RtdlHiprtAabbIndexQueryPayload {
    uint32_t operation;
    uint32_t intersect_pass;
    float point_x;
    float point_y;
    float min_x;
    float min_y;
    float max_x;
    float max_y;
};

__device__ bool aabbContainsPoint2D(const RtdlHiprtAabb2DDevice& box, float x, float y) {
    return box.min_x <= x && x <= box.max_x && box.min_y <= y && y <= box.max_y;
}

__device__ bool aabbContainsBox2D(const RtdlHiprtAabb2DDevice& outer, float min_x, float min_y, float max_x, float max_y) {
    return outer.min_x <= min_x && outer.min_y <= min_y && outer.max_x >= max_x && outer.max_y >= max_y;
}

__device__ bool segmentIntersectsAabb2D(float ax, float ay, float bx, float by, const RtdlHiprtAabb2DDevice& box) {
    const float eps = 1.0e-7f;
    float tmin = 0.0f;
    float tmax = 1.0f;
    const float dx = bx - ax;
    const float dy = by - ay;
    if (fabsf(dx) < eps) {
        if (ax < box.min_x || ax > box.max_x) return false;
    } else {
        const float inv = 1.0f / dx;
        float t0 = (box.min_x - ax) * inv;
        float t1 = (box.max_x - ax) * inv;
        if (t0 > t1) {
            const float tmp = t0;
            t0 = t1;
            t1 = tmp;
        }
        tmin = fmaxf(tmin, t0);
        tmax = fminf(tmax, t1);
        if (tmin > tmax) return false;
    }
    if (fabsf(dy) < eps) {
        if (ay < box.min_y || ay > box.max_y) return false;
    } else {
        const float inv = 1.0f / dy;
        float t0 = (box.min_y - ay) * inv;
        float t1 = (box.max_y - ay) * inv;
        if (t0 > t1) {
            const float tmp = t0;
            t0 = t1;
            t1 = tmp;
        }
        tmin = fmaxf(tmin, t0);
        tmax = fminf(tmax, t1);
        if (tmin > tmax) return false;
    }
    return true;
}

__device__ bool intersectRtdlAabbIndex2D(const hiprtRay& ray, const void* data, void* payload, hiprtHit& hit) {
    const RtdlHiprtAabb2DDevice* boxes = reinterpret_cast<const RtdlHiprtAabb2DDevice*>(data);
    const RtdlHiprtAabb2DDevice target = boxes[hit.primID];
    const RtdlHiprtAabbIndexQueryPayload* query =
        reinterpret_cast<const RtdlHiprtAabbIndexQueryPayload*>(payload);
    bool accept = false;
    if (query->operation == 1u) {
        accept = aabbContainsPoint2D(target, query->point_x, query->point_y);
    } else if (query->operation == 2u) {
        accept = aabbContainsBox2D(target, query->min_x, query->min_y, query->max_x, query->max_y);
    } else if (query->operation == 3u) {
        if (query->intersect_pass == 0u) {
            accept = segmentIntersectsAabb2D(query->min_x, query->min_y, query->max_x, query->max_y, target);
        } else {
            const bool source_antidiagonal_hits_target =
                segmentIntersectsAabb2D(query->max_x, query->min_y, query->min_x, query->max_y, target);
            RtdlHiprtAabb2DDevice source;
            source.id = 0u;
            source.min_x = query->min_x;
            source.min_y = query->min_y;
            source.max_x = query->max_x;
            source.max_y = query->max_y;
            const bool target_diagonal_hits_source =
                segmentIntersectsAabb2D(target.min_x, target.min_y, target.max_x, target.max_y, source);
            accept = source_antidiagonal_hits_target && !target_diagonal_hits_source;
        }
    }
    if (!accept) {
        return false;
    }
    hit.t = 0.0f;
    return true;
}

extern "C" __global__ void RtdlAabbIndexCount2DKernel(
    hiprtGeometry geom,
    const RtdlHiprtPoint2DDevice* point_queries,
    const RtdlHiprtAabb2DDevice* box_queries,
    uint32_t point_query_count,
    uint32_t box_query_count,
    uint32_t operation,
    uint32_t intersect_pass,
    unsigned long long* hit_count,
    hiprtFuncTable table) {
    const uint32_t index = blockIdx.x * blockDim.x + threadIdx.x;
    const uint32_t launch_count = operation == 1u ? point_query_count : box_query_count;
    if (index >= launch_count) {
        return;
    }

    RtdlHiprtAabbIndexQueryPayload payload;
    payload.operation = operation;
    payload.intersect_pass = intersect_pass;
    payload.point_x = 0.0f;
    payload.point_y = 0.0f;
    payload.min_x = 0.0f;
    payload.min_y = 0.0f;
    payload.max_x = 0.0f;
    payload.max_y = 0.0f;

    hiprtRay ray;
    ray.minT = 0.0f;
    ray.maxT = 0.0f;
    ray.origin = {0.0f, 0.0f, 0.0f};
    ray.direction = {0.0f, 0.0f, 1.0f};

    if (operation == 1u) {
        const RtdlHiprtPoint2DDevice point = point_queries[index];
        payload.point_x = point.x;
        payload.point_y = point.y;
        ray.origin = {point.x, point.y, 0.0f};
        ray.direction = {0.0f, 0.0f, 1.0f};
    } else {
        const RtdlHiprtAabb2DDevice box = box_queries[index];
        payload.min_x = box.min_x;
        payload.min_y = box.min_y;
        payload.max_x = box.max_x;
        payload.max_y = box.max_y;
        if (operation == 3u && intersect_pass == 0u) {
            ray.origin = {box.min_x, box.min_y, 0.0f};
            ray.direction = {box.max_x - box.min_x, box.max_y - box.min_y, 0.0f};
            ray.maxT = 1.0f;
        } else if (operation == 3u) {
            ray.origin = {box.max_x, box.min_y, 0.0f};
            ray.direction = {box.min_x - box.max_x, box.max_y - box.min_y, 0.0f};
            ray.maxT = 1.0f;
        } else {
            const float center_x = 0.5f * (box.min_x + box.max_x);
            const float center_y = 0.5f * (box.min_y + box.max_y);
            ray.origin = {center_x, center_y, 0.0f};
            ray.direction = {0.0f, 0.0f, 1.0f};
        }
    }

    uint32_t local_count = 0u;
    hiprtGeomCustomTraversalAnyHit traversal(geom, ray, hiprtTraversalHintDefault, &payload, table);
    while (traversal.getCurrentState() != hiprtTraversalStateFinished) {
        hiprtHit hit = traversal.getNextHit();
        if (hit.hasHit()) {
            ++local_count;
        }
    }
    if (local_count != 0u) {
        atomicAdd(hit_count, static_cast<unsigned long long>(local_count));
    }
}
)KERNEL";
}

oroFunction ensure_aabb_index_count_kernel_2d(PreparedAabbIndex2D& prepared) {
    if (prepared.count_kernel != nullptr) {
        return prepared.count_kernel;
    }
    hiprtFuncNameSet func_name_set{};
    func_name_set.intersectFuncName = "intersectRtdlAabbIndex2D";
    prepared.count_kernel = build_trace_kernel_from_source(
        prepared.runtime.context,
        aabb_index_count_kernel_source_2d(),
        "rtdl_hiprt_aabb_index_count_2d.cu",
        "RtdlAabbIndexCount2DKernel",
        &func_name_set,
        1,
        1);
    return prepared.count_kernel;
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

void run_prepared_ray_anyhit_2d(
    PreparedRayAnyhit2D& prepared,
    const RtdlRay2D* rays,
    size_t ray_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out) {
    if (ray_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared 2D ray_triangle_any_hit currently supports at most 2^32-1 rays");
    }
    if (ray_count > 0 && rays == nullptr) {
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    }
    if (ray_count == 0) {
        std::vector<RtdlRayAnyHitRow> empty;
        *rows_out = copy_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }
    if (prepared.empty_scene) {
        std::vector<RtdlRayAnyHitRow> output;
        output.reserve(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            output.push_back({rays[i].id, 0u});
        }
        *rows_out = copy_rows_to_heap(output);
        *row_count_out = output.size();
        return;
    }

    std::vector<RtdlHiprtRay2DDevice> ray_values = encode_rays_2d(rays, ray_count);
    DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay2DDevice));
    copy_host_to_device(ray_device, ray_values);
    std::vector<RtdlRayAnyHitRow> output(ray_count);
    DeviceAllocation output_device(output.size() * sizeof(RtdlRayAnyHitRow));

    void* ray_device_ptr = ray_device.get();
    void* output_device_ptr = output_device.get();
    uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
    oroFunction kernel = ensure_ray_anyhit_kernel_2d(prepared);
    void* args[] = {
        &prepared.geometry,
        &ray_device_ptr,
        &ray_count_u32,
        &output_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(output, output_device);

    *rows_out = copy_rows_to_heap(output);
    *row_count_out = output.size();
}

void run_group_flags_prepared_ray_anyhit_2d(
    PreparedRayAnyhit2D& prepared,
    const RtdlRay2D* rays,
    size_t ray_count,
    const uint32_t* group_indices,
    size_t group_index_count,
    uint32_t* group_flags_out,
    size_t group_count) {
    if (ray_count > std::numeric_limits<uint32_t>::max() || group_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared 2D grouped ray_triangle_any_hit currently supports at most 2^32-1 rays/groups");
    }
    if (ray_count > 0 && rays == nullptr) {
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    }
    if (group_index_count != ray_count) {
        throw std::runtime_error("group_index_count must match ray_count");
    }
    if (ray_count > 0 && group_indices == nullptr) {
        throw std::runtime_error("group_indices pointer must not be null when ray_count is nonzero");
    }
    if (group_count > 0 && group_flags_out == nullptr) {
        throw std::runtime_error("group_flags_out must not be null when group_count is nonzero");
    }
    if (group_count > 0) {
        std::fill(group_flags_out, group_flags_out + group_count, 0u);
    }
    if (ray_count == 0 || group_count == 0 || prepared.empty_scene) {
        return;
    }

    std::vector<uint32_t> group_values(group_indices, group_indices + group_index_count);
    for (uint32_t group : group_values) {
        if (group >= group_count) {
            throw std::runtime_error("group_indices entries must be within [0, group_count)");
        }
    }

    std::vector<RtdlHiprtRay2DDevice> ray_values = encode_rays_2d(rays, ray_count);
    std::vector<uint32_t> output(group_count, 0u);
    DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay2DDevice));
    DeviceAllocation group_index_device(group_values.size() * sizeof(uint32_t));
    DeviceAllocation output_device(output.size() * sizeof(uint32_t));
    copy_host_to_device(ray_device, ray_values);
    copy_host_to_device(group_index_device, group_values);
    copy_host_to_device(output_device, output);

    void* ray_device_ptr = ray_device.get();
    void* group_index_device_ptr = group_index_device.get();
    void* output_device_ptr = output_device.get();
    uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
    uint32_t group_count_u32 = static_cast<uint32_t>(group_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
    oroFunction kernel = ensure_grouped_ray_anyhit_kernel_2d(prepared);
    void* args[] = {
        &prepared.geometry,
        &ray_device_ptr,
        &group_index_device_ptr,
        &ray_count_u32,
        &group_count_u32,
        &output_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(output, output_device);
    std::copy(output.begin(), output.end(), group_flags_out);
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
            search_count,
            static_cast<float>(radius));
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

void write_prepared_fixed_radius_params_3d(PreparedFixedRadiusNeighbors3D& prepared, double radius) {
    if (!std::isfinite(radius)) {
        throw std::runtime_error("fixed_radius request radius must be finite");
    }
    if (radius < 0.0) {
        throw std::runtime_error("fixed_radius request radius must be non-negative");
    }
    const double epsilon = 1e-6;
    if (radius > static_cast<double>(prepared.max_radius) + epsilon) {
        throw std::runtime_error("fixed_radius request radius must not exceed the prepared maximum radius");
    }
    RtdlHiprtFixedRadiusParams params{static_cast<float>(radius)};
    check_oro(
        "oroMemcpyHtoD",
        oroMemcpyHtoD(prepared.params_device.oro_ptr(), &params, sizeof(params)));
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

void count_prepared_fixed_radius_threshold_reached_3d(
    PreparedFixedRadiusNeighbors3D& prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t threshold,
    size_t* count_out) {
    if (count_out == nullptr) {
        throw std::runtime_error("count_out must not be null");
    }
    *count_out = 0;
    if (threshold == 0) {
        throw std::runtime_error("fixed_radius threshold must be positive");
    }
    if (query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius threshold count currently supports at most 2^32-1 query points");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (query_count == 0 || prepared.search_count == 0) {
        return;
    }

    std::vector<RtdlHiprtPoint3DDevice> query_values = encode_points(queries, query_count);
    std::vector<unsigned long long> total(1, 0ull);
    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation count_device(sizeof(unsigned long long));
    copy_host_to_device(query_device, query_values);
    copy_host_to_device(count_device, total);

    void* query_device_ptr = query_device.get();
    void* count_device_ptr = count_device.get();
    void* params_device_ptr = prepared.params_device.get();
    uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
    oroFunction kernel = ensure_fixed_radius_threshold_count_kernel_3d(prepared);
    void* args[] = {
        &prepared.geometry,
        &query_device_ptr,
        &query_count_u32,
        &threshold,
        &count_device_ptr,
        &params_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(total, count_device);
    if (total[0] > static_cast<unsigned long long>(std::numeric_limits<size_t>::max())) {
        throw std::runtime_error("HIPRT fixed_radius threshold count overflowed size_t");
    }
    *count_out = static_cast<size_t>(total[0]);
}

void write_prepared_fixed_radius_threshold_flags_3d(
    PreparedFixedRadiusNeighbors3D& prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t threshold,
    uint32_t* flags_out,
    size_t flags_count) {
    if (flags_count != query_count) {
        throw std::runtime_error("flags_count must match query_count");
    }
    if (query_count > 0 && flags_out == nullptr) {
        throw std::runtime_error("flags_out must not be null when query_count is nonzero");
    }
    if (threshold == 0) {
        throw std::runtime_error("fixed_radius threshold must be positive");
    }
    if (query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius threshold flags currently support at most 2^32-1 query points");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (query_count == 0) {
        return;
    }
    if (prepared.search_count == 0) {
        std::fill(flags_out, flags_out + flags_count, 0u);
        return;
    }

    std::vector<RtdlHiprtPoint3DDevice> query_values = encode_points(queries, query_count);
    std::vector<uint32_t> flags(query_count, 0u);
    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation flags_device(flags.size() * sizeof(uint32_t));
    copy_host_to_device(query_device, query_values);
    copy_host_to_device(flags_device, flags);

    void* query_device_ptr = query_device.get();
    void* flags_device_ptr = flags_device.get();
    void* params_device_ptr = prepared.params_device.get();
    uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
    oroFunction kernel = ensure_fixed_radius_threshold_flags_kernel_3d(prepared);
    void* args[] = {
        &prepared.geometry,
        &query_device_ptr,
        &query_count_u32,
        &threshold,
        &flags_device_ptr,
        &params_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(flags, flags_device);
    std::copy(flags.begin(), flags.end(), flags_out);
}

void aggregate_prepared_fixed_radius_ranked_summary_3d(
    PreparedFixedRadiusNeighbors3D& prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusRankedNeighborAggregate* aggregate_out) {
    if (aggregate_out == nullptr) {
        throw std::runtime_error("aggregate_out must not be null");
    }
    *aggregate_out = RtdlFixedRadiusRankedNeighborAggregate{0, 0, 0, 0, 0.0};
    if (k_max == 0) {
        throw std::runtime_error("fixed_radius ranked summary aggregate k_max must be positive");
    }
    if (k_max > 64) {
        throw std::runtime_error("HIPRT fixed_radius ranked summary aggregate currently supports k_max <= 64");
    }
    if (query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT fixed_radius ranked summary aggregate currently supports at most 2^32-1 query points");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (query_count == 0) {
        return;
    }
    if (prepared.search_count == 0) {
        aggregate_out->query_count = query_count;
        return;
    }

    std::vector<RtdlHiprtPoint3DDevice> query_values = encode_points(queries, query_count);
    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint3DDevice));
    DeviceAllocation aggregate_device(sizeof(RtdlFixedRadiusRankedNeighborAggregate));
    copy_host_to_device(query_device, query_values);
    check_oro(
        "oroMemcpyHtoD",
        oroMemcpyHtoD(aggregate_device.oro_ptr(), aggregate_out, sizeof(RtdlFixedRadiusRankedNeighborAggregate)));

    void* query_device_ptr = query_device.get();
    void* search_device_ptr = prepared.search_device.get();
    void* aggregate_device_ptr = aggregate_device.get();
    void* params_device_ptr = prepared.params_device.get();
    uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>(std::min<size_t>((query_count + block_size - 1) / block_size, 4096));
    oroFunction kernel = ensure_fixed_radius_ranked_aggregate_kernel_3d(prepared);
    void* args[] = {
        &prepared.geometry,
        &query_device_ptr,
        &search_device_ptr,
        &query_count_u32,
        &k_max,
        &aggregate_device_ptr,
        &params_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    check_oro(
        "oroMemcpyDtoH",
        oroMemcpyDtoH(aggregate_out, aggregate_device.oro_ptr(), sizeof(RtdlFixedRadiusRankedNeighborAggregate)));
}

void aggregate_prepared_fixed_radius_ranked_summary_batch_3d(
    PreparedFixedRadiusNeighbors3D& prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    const double* radii,
    const uint32_t* k_values,
    size_t request_count,
    RtdlFixedRadiusRankedNeighborAggregate* aggregates_out) {
    if (request_count == 0) {
        return;
    }
    if (aggregates_out == nullptr) {
        throw std::runtime_error("aggregates_out must not be null when request_count is nonzero");
    }
    if (radii == nullptr || k_values == nullptr) {
        throw std::runtime_error("radii and k_values must not be null when request_count is nonzero");
    }
    for (size_t request_index = 0; request_index < request_count; ++request_index) {
        aggregates_out[request_index] = RtdlFixedRadiusRankedNeighborAggregate{0, 0, 0, 0, 0.0};
    }

    bool needs_restore = false;
    try {
        for (size_t request_index = 0; request_index < request_count; ++request_index) {
            write_prepared_fixed_radius_params_3d(prepared, radii[request_index]);
            needs_restore = true;
            aggregate_prepared_fixed_radius_ranked_summary_3d(
                prepared,
                queries,
                query_count,
                k_values[request_index],
                &aggregates_out[request_index]);
        }
    } catch (...) {
        if (needs_restore) {
            try {
                write_prepared_fixed_radius_params_3d(prepared, static_cast<double>(prepared.max_radius));
            } catch (...) {
            }
        }
        throw;
    }
    write_prepared_fixed_radius_params_3d(prepared, static_cast<double>(prepared.max_radius));
}

std::unique_ptr<PreparedPointGroupNearestWitness2D> prepare_point_group_nearest_witness_2d_hiprt(
    const RtdlPoint* search_points,
    size_t search_count,
    const RtdlPointGroupBounds2D* groups,
    size_t group_count,
    double max_radius) {
    if (!std::isfinite(max_radius)) {
        throw std::runtime_error("point_group_nearest max_radius must be finite");
    }
    if (max_radius < 0.0) {
        throw std::runtime_error("point_group_nearest max_radius must be non-negative");
    }
    if (search_count > std::numeric_limits<uint32_t>::max() || group_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT point_group_nearest currently supports at most 2^32-1 search points/groups");
    }
    if (search_count > 0 && search_points == nullptr) {
        throw std::runtime_error("search point pointer must not be null when search_count is nonzero");
    }
    if (group_count > 0 && groups == nullptr) {
        throw std::runtime_error("point group pointer must not be null when group_count is nonzero");
    }
    if (search_count == 0 || group_count == 0) {
        throw std::runtime_error("prepared HIPRT point_group_nearest requires at least one search point and one group");
    }

    std::vector<RtdlHiprtPoint2DDevice> search_values = encode_points_2d(search_points, search_count);
    std::vector<RtdlHiprtPointGroupBounds2DDevice> group_values =
        encode_point_group_bounds_2d(groups, group_count, search_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_point_group_bounds_aabbs_2d(
        group_values.data(),
        group_values.size(),
        static_cast<float>(max_radius));
    RtdlHiprtPointGroupNearestParams params{
        static_cast<float>(max_radius),
        static_cast<float>(max_radius),
    };

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation search_device(search_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation group_device(group_values.size() * sizeof(RtdlHiprtPointGroupBounds2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    DeviceAllocation params_device(sizeof(RtdlHiprtPointGroupNearestParams));
    copy_host_to_device(search_device, search_values);
    copy_host_to_device(group_device, group_values);
    copy_host_to_device(aabb_device, aabb_values);
    check_oro("oroMemcpyHtoD", oroMemcpyHtoD(params_device.oro_ptr(), &params, sizeof(params)));

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncNameSet func_name_set{};
        func_name_set.intersectFuncName = "intersectRtdlPointGroupBounds2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = group_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction witness_kernel = build_trace_kernel_from_source(
            runtime.context,
            point_group_nearest_witness_2d_kernel_source(),
            "rtdl_hiprt_point_group_nearest_witness_2d.cu",
            "RtdlPointGroupNearestWitness2DKernel",
            &func_name_set,
            1,
            1);
        auto prepared = std::make_unique<PreparedPointGroupNearestWitness2D>(
            std::move(runtime),
            std::move(search_device),
            std::move(group_device),
            std::move(aabb_device),
            std::move(params_device),
            geometry,
            func_table,
            witness_kernel,
            search_count,
            group_count,
            static_cast<float>(max_radius));
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

void write_prepared_point_group_nearest_params_2d(PreparedPointGroupNearestWitness2D& prepared, double radius) {
    if (!std::isfinite(radius)) {
        throw std::runtime_error("point_group_nearest request radius must be finite");
    }
    if (radius < 0.0) {
        throw std::runtime_error("point_group_nearest request radius must be non-negative");
    }
    const double epsilon = 1e-6;
    if (radius > static_cast<double>(prepared.max_radius) + epsilon) {
        throw std::runtime_error("point_group_nearest request radius must not exceed the prepared maximum radius");
    }
    RtdlHiprtPointGroupNearestParams params{
        static_cast<float>(radius),
        prepared.max_radius,
    };
    check_oro(
        "oroMemcpyHtoD",
        oroMemcpyHtoD(prepared.params_device.oro_ptr(), &params, sizeof(params)));
}

void run_prepared_point_group_nearest_witness_2d_hiprt(
    PreparedPointGroupNearestWitness2D& prepared,
    const RtdlPoint* queries,
    size_t query_count,
    double radius,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out) {
    if (query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT point_group_nearest currently supports at most 2^32-1 query points");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    write_prepared_point_group_nearest_params_2d(prepared, radius);
    if (query_count == 0) {
        std::vector<RtdlFixedRadiusNeighborRow> empty;
        *rows_out = copy_frn_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> query_values = encode_points_2d(queries, query_count);
    std::vector<RtdlFixedRadiusNeighborRow> output(query_count);
    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation output_device(output.size() * sizeof(RtdlFixedRadiusNeighborRow));
    copy_host_to_device(query_device, query_values);

    void* query_device_ptr = query_device.get();
    void* search_device_ptr = prepared.search_device.get();
    void* group_device_ptr = prepared.group_device.get();
    void* output_device_ptr = output_device.get();
    void* params_device_ptr = prepared.params_device.get();
    uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
    void* args[] = {
        &prepared.geometry,
        &query_device_ptr,
        &search_device_ptr,
        &group_device_ptr,
        &query_count_u32,
        &output_device_ptr,
        &params_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.witness_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(output, output_device);
    *rows_out = copy_frn_rows_to_heap(output);
    *row_count_out = output.size();
}

void write_prepared_point_group_nearest_witness_device_columns_2d_hiprt(
    PreparedPointGroupNearestWitness2D& prepared,
    const RtdlPoint* queries,
    size_t query_count,
    double radius,
    uint32_t* query_ids_out,
    uint32_t* neighbor_ids_out,
    double* distances_out) {
    if (query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT point_group_nearest device columns currently support at most 2^32-1 query points");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    if (query_count > 0 && (query_ids_out == nullptr || neighbor_ids_out == nullptr || distances_out == nullptr)) {
        throw std::runtime_error("point_group_nearest device column output pointers must not be null when query_count is nonzero");
    }
    write_prepared_point_group_nearest_params_2d(prepared, radius);
    if (query_count == 0) {
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> query_values = encode_points_2d(queries, query_count);
    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation row_device(query_count * sizeof(RtdlFixedRadiusNeighborRow));
    copy_host_to_device(query_device, query_values);

    void* query_device_ptr = query_device.get();
    void* search_device_ptr = prepared.search_device.get();
    void* group_device_ptr = prepared.group_device.get();
    void* row_device_ptr = row_device.get();
    void* params_device_ptr = prepared.params_device.get();
    uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
    void* witness_args[] = {
        &prepared.geometry,
        &query_device_ptr,
        &search_device_ptr,
        &group_device_ptr,
        &query_count_u32,
        &row_device_ptr,
        &params_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.witness_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, witness_args, nullptr));

    oroFunction split_kernel = ensure_point_group_nearest_split_columns_kernel_2d(prepared);
    void* split_args[] = {
        &row_device_ptr,
        &query_count_u32,
        &query_ids_out,
        &neighbor_ids_out,
        &distances_out,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(split_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, split_args, nullptr));
}

void reduce_prepared_point_group_nearest_max_distance_2d_hiprt(
    PreparedPointGroupNearestWitness2D& prepared,
    const RtdlPoint* queries,
    size_t query_count,
    double radius,
    RtdlFixedRadiusNeighborRow* row_out) {
    if (row_out == nullptr) {
        throw std::runtime_error("row_out must not be null");
    }
    *row_out = RtdlFixedRadiusNeighborRow{
        std::numeric_limits<uint32_t>::max(),
        std::numeric_limits<uint32_t>::max(),
        std::numeric_limits<double>::infinity(),
    };
    if (query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT point_group_nearest max-distance reduction currently supports at most 2^32-1 query points");
    }
    if (query_count > 0 && queries == nullptr) {
        throw std::runtime_error("query point pointer must not be null when query_count is nonzero");
    }
    write_prepared_point_group_nearest_params_2d(prepared, radius);
    if (query_count == 0) {
        return;
    }

    std::vector<RtdlHiprtPoint2DDevice> query_values = encode_points_2d(queries, query_count);
    std::vector<RtdlFixedRadiusNeighborRow> output(query_count);
    std::vector<RtdlFixedRadiusNeighborRow> reduced(1);
    DeviceAllocation query_device(query_values.size() * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation output_device(output.size() * sizeof(RtdlFixedRadiusNeighborRow));
    DeviceAllocation reduced_device(sizeof(RtdlFixedRadiusNeighborRow));
    copy_host_to_device(query_device, query_values);

    void* query_device_ptr = query_device.get();
    void* search_device_ptr = prepared.search_device.get();
    void* group_device_ptr = prepared.group_device.get();
    void* output_device_ptr = output_device.get();
    void* params_device_ptr = prepared.params_device.get();
    uint32_t query_count_u32 = static_cast<uint32_t>(query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((query_count + block_size - 1) / block_size);
    void* witness_args[] = {
        &prepared.geometry,
        &query_device_ptr,
        &search_device_ptr,
        &group_device_ptr,
        &query_count_u32,
        &output_device_ptr,
        &params_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.witness_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, witness_args, nullptr));

    void* reduced_device_ptr = reduced_device.get();
    oroFunction reduce_kernel = ensure_point_group_nearest_max_distance_kernel_2d(prepared);
    void* reduce_args[] = {
        &output_device_ptr,
        &query_count_u32,
        &reduced_device_ptr,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(reduce_kernel, 1, 1, 1, block_size, 1, 1, 0, 0, reduce_args, nullptr));
    copy_device_to_host(reduced, reduced_device);
    *row_out = reduced[0];
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

void sort_segment_intersection_rows_by_input_order(
    std::vector<RtdlSegmentPairIntersectionRow>& rows,
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
    std::sort(rows.begin(), rows.end(), [&](const RtdlSegmentPairIntersectionRow& a, const RtdlSegmentPairIntersectionRow& b) {
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

void run_segment_pair_intersection_2d(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlSegmentPairIntersectionRow** rows_out,
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
        std::vector<RtdlSegmentPairIntersectionRow> empty;
        *rows_out = copy_segment_intersection_rows_to_heap(empty);
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
            segment_pair_intersection_2d_kernel_source(),
            "rtdl_hiprt_segment_pair_intersection_2d.cu",
            "RtdlSegmentPairIntersection2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = left_count * right_count;
        std::vector<RtdlSegmentPairIntersectionRow> output(output_capacity);
        std::vector<uint32_t> counts(left_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlSegmentPairIntersectionRow));
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

        std::vector<RtdlSegmentPairIntersectionRow> compacted;
        for (size_t left_index = 0; left_index < left_count; ++left_index) {
            uint32_t count = std::min<uint32_t>(counts[left_index], static_cast<uint32_t>(right_count));
            size_t base = left_index * right_count;
            for (uint32_t rank = 0; rank < count; ++rank) {
                compacted.push_back(output[base + rank]);
            }
        }
        sort_segment_intersection_rows_by_input_order(compacted, left, left_count, right, right_count);
        *rows_out = copy_segment_intersection_rows_to_heap(compacted);
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

PreparedSegmentPairIntersection2D* prepare_segment_pair_intersection_2d(
    const RtdlSegment* right,
    size_t right_count) {
    if (right_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared segment_intersection currently supports at most 2^32-1 right segments");
    }
    if (right_count > 0 && right == nullptr) {
        throw std::runtime_error("right segment pointer must not be null when right_count is nonzero");
    }
    if (right_count == 0) {
        return new PreparedSegmentPairIntersection2D(true);
    }

    std::vector<RtdlHiprtSegmentDevice> right_values = encode_segments(right, right_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_segment_aabbs(right_values.data(), right_values.size());
    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation right_device(right_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(right_device, right_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = right_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        auto* prepared = new PreparedSegmentPairIntersection2D(
            std::move(runtime),
            std::move(right_device),
            std::move(aabb_device),
            geometry,
            func_table,
            right_count);
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

void count_prepared_segment_pair_intersection_2d(
    PreparedSegmentPairIntersection2D& prepared,
    const RtdlSegment* left,
    size_t left_count,
    size_t* count_out) {
    if (count_out == nullptr) {
        throw std::runtime_error("count_out must not be null");
    }
    *count_out = 0;
    if (left_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared segment_intersection count currently supports at most 2^32-1 left segments");
    }
    if (left_count > 0 && left == nullptr) {
        throw std::runtime_error("left segment pointer must not be null when left_count is nonzero");
    }
    if (left_count == 0 || prepared.empty_scene || prepared.right_count == 0) {
        return;
    }

    std::vector<RtdlHiprtSegmentDevice> left_values = encode_segments(left, left_count);
    std::vector<unsigned long long> total(1, 0ull);
    DeviceAllocation left_device(left_values.size() * sizeof(RtdlHiprtSegmentDevice));
    DeviceAllocation count_device(sizeof(unsigned long long));
    copy_host_to_device(left_device, left_values);
    copy_host_to_device(count_device, total);

    void* left_device_ptr = left_device.get();
    void* count_device_ptr = count_device.get();
    uint32_t left_count_u32 = static_cast<uint32_t>(left_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((left_count + block_size - 1) / block_size);
    oroFunction kernel = ensure_segment_pair_intersection_count_kernel_2d(prepared);
    void* args[] = {
        &prepared.geometry,
        &left_device_ptr,
        &left_count_u32,
        &count_device_ptr,
        &prepared.func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(total, count_device);
    if (total[0] > static_cast<unsigned long long>(std::numeric_limits<size_t>::max())) {
        throw std::runtime_error("HIPRT prepared segment_intersection count overflowed size_t");
    }
    *count_out = static_cast<size_t>(total[0]);
}

PreparedAabbIndex2D* prepare_aabb_index_2d_hiprt(
    const RtdlAabb2D* boxes,
    size_t box_count) {
    if (box_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared AABB index currently supports at most 2^32-1 boxes");
    }
    if (box_count > 0 && boxes == nullptr) {
        throw std::runtime_error("AABB box pointer must not be null when box_count is nonzero");
    }
    if (box_count == 0) {
        return new PreparedAabbIndex2D(true);
    }

    std::vector<RtdlHiprtAabb2DDevice> box_values = encode_aabbs_2d(boxes, box_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_aabb_index_aabbs(box_values.data(), box_values.size());
    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);

    DeviceAllocation box_device(box_values.size() * sizeof(RtdlHiprtAabb2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    copy_host_to_device(box_device, box_values);
    copy_host_to_device(aabb_device, aabb_values);

    hiprtGeometry geometry = build_aabb_geometry(runtime.context, aabb_device, aabb_values.size());
    hiprtFuncTable func_table{};
    try {
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = box_device.get();
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        auto* prepared = new PreparedAabbIndex2D(
            std::move(runtime),
            std::move(box_device),
            std::move(aabb_device),
            geometry,
            func_table,
            box_count);
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

uint32_t validate_aabb_index_operation_hiprt(uint32_t operation) {
    if (operation == RTDL_AABB_INDEX_OP_POINT_CONTAINS
            || operation == RTDL_AABB_INDEX_OP_RANGE_CONTAINS
            || operation == RTDL_AABB_INDEX_OP_RANGE_INTERSECTS) {
        return operation;
    }
    throw std::runtime_error("unsupported HIPRT AABB_INDEX_QUERY_2D operation");
}

void launch_aabb_index_count_pass_hiprt(
    hiprtGeometry geometry,
    hiprtFuncTable func_table,
    oroFunction kernel,
    const RtdlHiprtPoint2DDevice* point_queries,
    size_t point_query_count,
    const RtdlHiprtAabb2DDevice* box_queries,
    size_t box_query_count,
    uint32_t operation,
    uint32_t intersect_pass,
    DeviceAllocation& total_device) {
    const size_t launch_count = operation == RTDL_AABB_INDEX_OP_POINT_CONTAINS ? point_query_count : box_query_count;
    if (launch_count == 0) {
        return;
    }
    if (launch_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT AABB index query count exceeds uint32 launch limit");
    }

    DeviceAllocation point_device(point_query_count * sizeof(RtdlHiprtPoint2DDevice));
    DeviceAllocation box_device(box_query_count * sizeof(RtdlHiprtAabb2DDevice));
    if (point_query_count != 0) {
        std::vector<RtdlHiprtPoint2DDevice> point_values(point_queries, point_queries + point_query_count);
        copy_host_to_device(point_device, point_values);
    }
    if (box_query_count != 0) {
        std::vector<RtdlHiprtAabb2DDevice> box_values(box_queries, box_queries + box_query_count);
        copy_host_to_device(box_device, box_values);
    }

    void* point_device_ptr = point_device.get();
    void* box_device_ptr = box_device.get();
    void* total_device_ptr = total_device.get();
    uint32_t point_count_u32 = static_cast<uint32_t>(point_query_count);
    uint32_t box_count_u32 = static_cast<uint32_t>(box_query_count);
    uint32_t block_size = 128;
    uint32_t grid_size = static_cast<uint32_t>((launch_count + block_size - 1) / block_size);
    void* args[] = {
        &geometry,
        &point_device_ptr,
        &box_device_ptr,
        &point_count_u32,
        &box_count_u32,
        &operation,
        &intersect_pass,
        &total_device_ptr,
        &func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
}

void count_prepared_aabb_index_2d_hiprt(
    PreparedAabbIndex2D& prepared,
    const RtdlPoint* point_queries,
    size_t point_query_count,
    const RtdlAabb2D* box_queries,
    size_t box_query_count,
    uint32_t operation,
    size_t* count_out) {
    if (count_out == nullptr) {
        throw std::runtime_error("count_out must not be null");
    }
    *count_out = 0;
    operation = validate_aabb_index_operation_hiprt(operation);
    if (prepared.empty_scene || prepared.box_count == 0) {
        return;
    }
    if (point_query_count > std::numeric_limits<uint32_t>::max()
            || box_query_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT AABB index query counts exceed uint32 launch limit");
    }
    if (point_query_count > 0 && point_queries == nullptr) {
        throw std::runtime_error("point query pointer must not be null when point_query_count is nonzero");
    }
    if (box_query_count > 0 && box_queries == nullptr) {
        throw std::runtime_error("box query pointer must not be null when box_query_count is nonzero");
    }

    std::vector<RtdlHiprtPoint2DDevice> point_values;
    std::vector<RtdlHiprtAabb2DDevice> box_values;
    if (operation == RTDL_AABB_INDEX_OP_POINT_CONTAINS) {
        if (point_query_count == 0) {
            return;
        }
        point_values = encode_points_2d(point_queries, point_query_count);
    } else {
        if (box_query_count == 0) {
            return;
        }
        box_values = encode_aabbs_2d(box_queries, box_query_count);
    }

    std::vector<unsigned long long> total(1, 0ull);
    DeviceAllocation total_device(sizeof(unsigned long long));
    copy_host_to_device(total_device, total);
    oroFunction kernel = ensure_aabb_index_count_kernel_2d(prepared);

    if (operation == RTDL_AABB_INDEX_OP_RANGE_INTERSECTS) {
        launch_aabb_index_count_pass_hiprt(
            prepared.geometry,
            prepared.func_table,
            kernel,
            nullptr,
            0,
            box_values.data(),
            box_values.size(),
            operation,
            RTDL_AABB_INDEX_INTERSECT_FORWARD_PASS,
            total_device);

        std::vector<RtdlHiprtAabb> query_aabb_values = encode_aabb_index_aabbs(box_values.data(), box_values.size());
        DeviceAllocation query_box_device(box_values.size() * sizeof(RtdlHiprtAabb2DDevice));
        DeviceAllocation query_aabb_device(query_aabb_values.size() * sizeof(RtdlHiprtAabb));
        copy_host_to_device(query_box_device, box_values);
        copy_host_to_device(query_aabb_device, query_aabb_values);
        hiprtGeometry query_geometry = build_aabb_geometry(prepared.runtime.context, query_aabb_device, query_aabb_values.size());
        hiprtFuncTable query_func_table{};
        try {
            hiprtFuncDataSet func_data_set{};
            func_data_set.intersectFuncData = query_box_device.get();
            check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(prepared.runtime.context, 1, 1, query_func_table));
            check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(prepared.runtime.context, query_func_table, 0, 0, func_data_set));
            std::vector<RtdlHiprtAabb2DDevice> indexed_boxes(prepared.box_count);
            copy_device_to_host(indexed_boxes, prepared.box_device);
            launch_aabb_index_count_pass_hiprt(
                query_geometry,
                query_func_table,
                kernel,
                nullptr,
                0,
                indexed_boxes.data(),
                indexed_boxes.size(),
                operation,
                RTDL_AABB_INDEX_INTERSECT_BACKWARD_PASS,
                total_device);
        } catch (...) {
            if (query_func_table != nullptr) {
                hiprtDestroyFuncTable(prepared.runtime.context, query_func_table);
            }
            if (query_geometry != nullptr) {
                hiprtDestroyGeometry(prepared.runtime.context, query_geometry);
            }
            throw;
        }
        if (query_func_table != nullptr) {
            hiprtDestroyFuncTable(prepared.runtime.context, query_func_table);
        }
        if (query_geometry != nullptr) {
            hiprtDestroyGeometry(prepared.runtime.context, query_geometry);
        }
    } else {
        launch_aabb_index_count_pass_hiprt(
            prepared.geometry,
            prepared.func_table,
            kernel,
            point_values.empty() ? nullptr : point_values.data(),
            point_values.size(),
            box_values.empty() ? nullptr : box_values.data(),
            box_values.size(),
            operation,
            RTDL_AABB_INDEX_INTERSECT_FORWARD_PASS,
            total_device);
    }

    check_oro("oroDeviceSynchronize", oroDeviceSynchronize());
    copy_device_to_host(total, total_device);
    if (total[0] > static_cast<unsigned long long>(std::numeric_limits<size_t>::max())) {
        throw std::runtime_error("HIPRT prepared AABB index count overflowed size_t");
    }
    *count_out = static_cast<size_t>(total[0]);
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
                "rtdl_hiprt_segment_shape_2d.cu",
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
                "rtdl_hiprt_segment_shape_2d.cu",
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

void run_ray_anyhit_2d(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out) {
    if (ray_count > std::numeric_limits<uint32_t>::max() || triangle_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT 2D ray_triangle_any_hit currently supports at most 2^32-1 rays/triangles");
    }
    if (ray_count > 0 && rays == nullptr) {
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    }
    if (triangle_count > 0 && triangles == nullptr) {
        throw std::runtime_error("triangle pointer must not be null when triangle_count is nonzero");
    }
    if (ray_count == 0) {
        std::vector<RtdlRayAnyHitRow> empty;
        *rows_out = copy_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }
    if (triangle_count == 0) {
        std::vector<RtdlRayAnyHitRow> output;
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
        const std::string source = ray_anyhit_kernel_source_2d();
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            source.c_str(),
            "rtdl_hiprt_ray_anyhit_2d.cu",
            "RtdlRayAnyhit2DKernel",
            &func_name_set,
            1,
            1);

        std::vector<RtdlRayAnyHitRow> output(ray_count);
        DeviceAllocation output_device(output.size() * sizeof(RtdlRayAnyHitRow));
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
            "rtdl_hiprt_point_primitive_anyhit_2d.cu",
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

void run_shape_pair_relation_flags_2d(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlShapePairRelationRow** rows_out,
    size_t* row_count_out) {
    if (left_count > std::numeric_limits<uint32_t>::max() || right_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT shape_pair_relation_compose currently supports at most 2^32-1 left/right polygons");
    }
    if (left_count != 0 && right_count > std::numeric_limits<size_t>::max() / left_count) {
        throw std::runtime_error("HIPRT shape_pair_relation_compose output capacity overflow");
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
        std::vector<RtdlShapePairRelationRow> empty;
        *rows_out = copy_shape_pair_relation_rows_to_heap(empty);
        *row_count_out = 0;
        return;
    }

    std::vector<RtdlHiprtPolygonRefDevice> left_values = encode_polygon_refs_2d(left_polygons, left_count);
    std::vector<RtdlHiprtVertex2DDevice> left_vertex_values = encode_vertices_2d(left_vertices_xy, left_vertex_xy_count);
    std::vector<RtdlHiprtPolygonRefDevice> right_values = encode_polygon_refs_2d(right_polygons, right_count);
    std::vector<RtdlHiprtVertex2DDevice> right_vertex_values = encode_vertices_2d(right_vertices_xy, right_vertex_xy_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_shape_pair_candidate_aabbs(
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
        func_name_set.intersectFuncName = "intersectRtdlShapePairCandidate2D";
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        oroFunction kernel = build_trace_kernel_from_source(
            runtime.context,
            shape_pair_relation_flags_2d_kernel_source(),
            "rtdl_hiprt_shape_pair_relation_flags_2d.cu",
            "RtdlShapePairRelationFlags2DKernel",
            &func_name_set,
            1,
            1);

        const size_t output_capacity = left_count * right_count;
        std::vector<RtdlShapePairRelationRow> output(output_capacity);
        DeviceAllocation output_device(output.size() * sizeof(RtdlShapePairRelationRow));
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
        *rows_out = copy_shape_pair_relation_rows_to_heap(output);
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

PreparedShapePairActiveCount2D* prepare_shape_pair_active_count_2d(
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count) {
    if (right_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared shape_pair_active_count currently supports at most 2^32-1 right polygons");
    }
    if (right_count > 0 && right_polygons == nullptr) {
        throw std::runtime_error("right polygon pointer must not be null when right_count is nonzero");
    }
    if (right_vertex_xy_count % 2 != 0) {
        throw std::runtime_error("right polygon vertex_xy_count must be even");
    }
    if (right_vertex_xy_count > 0 && right_vertices_xy == nullptr) {
        throw std::runtime_error("right polygon vertices pointer must not be null when vertex count is nonzero");
    }
    if (right_count == 0) {
        return new PreparedShapePairActiveCount2D(true);
    }

    std::vector<RtdlHiprtPolygonRefDevice> right_values = encode_polygon_refs_2d(right_polygons, right_count);
    std::vector<RtdlHiprtVertex2DDevice> right_vertex_values = encode_vertices_2d(right_vertices_xy, right_vertex_xy_count);
    for (const auto& polygon : right_values) {
        if (polygon.vertex_count == 0 || polygon.vertex_offset + polygon.vertex_count > right_vertex_values.size()) {
            throw std::runtime_error("right polygon vertex range is invalid");
        }
    }

    HiprtRuntime runtime = create_runtime();
    hiprtSetLogLevel(hiprtLogLevelError);
    DeviceAllocation right_device(right_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation right_vertex_device(right_vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    copy_host_to_device(right_device, right_values);
    copy_host_to_device(right_vertex_device, right_vertex_values);

    hiprtFuncTable func_table{};
    try {
        hiprtFuncDataSet func_data_set{};
        func_data_set.intersectFuncData = nullptr;
        check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
        check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
        auto* prepared = new PreparedShapePairActiveCount2D(
            std::move(runtime),
            std::move(right_device),
            std::move(right_vertex_device),
            func_table,
            right_count,
            right_vertex_values.size());
        func_table = nullptr;
        return prepared;
    } catch (...) {
        if (func_table != nullptr) {
            hiprtDestroyFuncTable(runtime.context, func_table);
        }
        throw;
    }
}

void count_prepared_shape_pair_active_2d(
    PreparedShapePairActiveCount2D& prepared,
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    size_t* count_out) {
    if (count_out == nullptr) {
        throw std::runtime_error("count_out must not be null");
    }
    *count_out = 0;
    if (left_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared shape_pair_active_count currently supports at most 2^32-1 left polygons");
    }
    if (left_count > 0 && left_polygons == nullptr) {
        throw std::runtime_error("left polygon pointer must not be null when left_count is nonzero");
    }
    if (left_vertex_xy_count % 2 != 0) {
        throw std::runtime_error("left polygon vertex_xy_count must be even");
    }
    if (left_vertex_xy_count > 0 && left_vertices_xy == nullptr) {
        throw std::runtime_error("left polygon vertices pointer must not be null when vertex count is nonzero");
    }
    if (left_count == 0 || prepared.empty_scene || prepared.right_count == 0) {
        return;
    }

    std::vector<RtdlHiprtPolygonRefDevice> left_values = encode_polygon_refs_2d(left_polygons, left_count);
    std::vector<RtdlHiprtVertex2DDevice> left_vertex_values = encode_vertices_2d(left_vertices_xy, left_vertex_xy_count);
    std::vector<RtdlHiprtAabb> aabb_values = encode_shape_pair_left_envelope_aabbs(
        prepared.right_count,
        left_values.data(),
        left_values.size(),
        left_vertex_values.data(),
        left_vertex_values.size());

    DeviceAllocation left_device(left_values.size() * sizeof(RtdlHiprtPolygonRefDevice));
    DeviceAllocation left_vertex_device(left_vertex_values.size() * sizeof(RtdlHiprtVertex2DDevice));
    DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
    std::vector<unsigned long long> total(1, 0ull);
    DeviceAllocation count_device(sizeof(unsigned long long));
    copy_host_to_device(left_device, left_values);
    copy_host_to_device(left_vertex_device, left_vertex_values);
    copy_host_to_device(aabb_device, aabb_values);
    copy_host_to_device(count_device, total);

    hiprtGeometry geometry = build_aabb_geometry(prepared.runtime.context, aabb_device, aabb_values.size());
    try {
        void* left_device_ptr = left_device.get();
        void* left_vertex_device_ptr = left_vertex_device.get();
        void* right_device_ptr = prepared.right_device.get();
        void* right_vertex_device_ptr = prepared.right_vertex_device.get();
        void* count_device_ptr = count_device.get();
        uint32_t left_count_u32 = static_cast<uint32_t>(left_count);
        uint32_t right_count_u32 = static_cast<uint32_t>(prepared.right_count);
        uint32_t block_size = 128;
        uint32_t grid_size = static_cast<uint32_t>((left_count + block_size - 1) / block_size);
        oroFunction kernel = ensure_shape_pair_active_count_kernel_2d(prepared);
        void* args[] = {
            &geometry,
            &left_device_ptr,
            &left_vertex_device_ptr,
            &right_device_ptr,
            &right_vertex_device_ptr,
            &left_count_u32,
            &right_count_u32,
            &count_device_ptr,
            &prepared.func_table,
        };
        check_oro(
            "oroModuleLaunchKernel",
            oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
        copy_device_to_host(total, count_device);
    } catch (...) {
        if (geometry != nullptr) {
            hiprtDestroyGeometry(prepared.runtime.context, geometry);
        }
        throw;
    }
    if (geometry != nullptr) {
        hiprtDestroyGeometry(prepared.runtime.context, geometry);
    }
    if (total[0] > static_cast<unsigned long long>(std::numeric_limits<size_t>::max())) {
        throw std::runtime_error("HIPRT prepared shape_pair_active_count overflowed size_t");
    }
    *count_out = static_cast<size_t>(total[0]);
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
            "rtdl_hiprt_frontier_edge_traversal_packet.cu",
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
            "rtdl_hiprt_frontier_edge_traversal_packet.cu",
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
            triangle_cycle_candidates_kernel_source(),
            "rtdl_hiprt_triangle_cycle_candidates.cu",
            "RtdlTriangleProbeKernel",
            &triangle_func_name_set,
            1,
            1);
        oroFunction triangle_count_kernel = build_trace_kernel_from_source(
            runtime.context,
            triangle_cycle_candidates_kernel_source(),
            "rtdl_hiprt_triangle_cycle_count.cu",
            "RtdlTriangleProbeCountKernel",
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
            triangle_count_kernel,
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

void run_triangle_cycle_candidates(
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
            triangle_cycle_candidates_kernel_source(),
            "rtdl_hiprt_triangle_cycle_candidates.cu",
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

void run_prepared_triangle_cycle_candidates(
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

void count_prepared_triangle_cycle_candidates(
    PreparedGraphCSR& prepared,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    bool enforce_id_ascending,
    size_t* count_out) {
    if (count_out == nullptr) {
        throw std::runtime_error("HIPRT prepared graph-cycle count output pointer must not be null");
    }
    *count_out = 0;
    if (!enforce_id_ascending) {
        throw std::runtime_error("HIPRT prepared graph-cycle scalar count requires id-ascending canonical seeds");
    }
    if (seed_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT prepared graph-cycle scalar count currently supports at most 2^32-1 seeds");
    }
    validate_canonical_unique_edge_seeds(seeds, seed_count, prepared.vertex_count, "HIPRT prepared graph-cycle");
    if (seed_count == 0 || prepared.edge_count == 0) {
        return;
    }

    std::vector<RtdlEdgeSeed> seed_values(seeds, seeds + seed_count);
    std::vector<uint32_t> row_count_device_host(1, 0u);
    DeviceAllocation seed_device(seed_values.size() * sizeof(RtdlEdgeSeed));
    DeviceAllocation row_count_device(sizeof(uint32_t));
    copy_host_to_device(seed_device, seed_values);
    copy_host_to_device(row_count_device, row_count_device_host);

    void* seed_device_ptr = seed_device.get();
    void* row_offset_device_ptr = prepared.row_offset_device.get();
    void* column_device_ptr = prepared.column_device.get();
    void* edge_device_ptr = prepared.edge_device.get();
    void* row_count_device_ptr = row_count_device.get();
    uint32_t seed_count_u32 = static_cast<uint32_t>(seed_count);
    uint32_t enforce_u32 = 1u;
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
        &row_count_device_ptr,
        &prepared.triangle_func_table,
    };
    check_oro(
        "oroModuleLaunchKernel",
        oroModuleLaunchKernel(prepared.triangle_count_kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
    copy_device_to_host(row_count_device_host, row_count_device);
    *count_out = static_cast<size_t>(row_count_device_host[0]);
}

void count_triangle_cycle_candidates(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    bool enforce_id_ascending,
    size_t* count_out) {
    if (row_offset_count == 0 || row_offsets == nullptr) {
        throw std::runtime_error("HIPRT graph-cycle count CSR row_offsets must not be empty");
    }
    if (edge_count > 0 && column_indices == nullptr) {
        throw std::runtime_error("HIPRT graph-cycle count column_indices pointer must not be null when edge_count is nonzero");
    }
    if (row_offset_count - 1u > std::numeric_limits<uint32_t>::max() ||
        edge_count > std::numeric_limits<uint32_t>::max() ||
        seed_count > std::numeric_limits<uint32_t>::max()) {
        throw std::runtime_error("HIPRT graph-cycle count currently supports at most 2^32-1 vertices/edges/seeds");
    }
    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1u);
    validate_canonical_unique_edge_seeds(seeds, seed_count, vertex_count, "HIPRT graph-cycle");
    if (count_out == nullptr) {
        throw std::runtime_error("HIPRT graph-cycle count output pointer must not be null");
    }
    if (seed_count == 0 || edge_count == 0) {
        *count_out = 0;
        return;
    }
    auto prepared = prepare_graph_csr(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
    count_prepared_triangle_cycle_candidates(*prepared, seeds, seed_count, enforce_id_ascending, count_out);
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
        "rtdl_hiprt_predicate_match_prepared.cu",
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
            "rtdl_hiprt_predicate_match.cu",
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
