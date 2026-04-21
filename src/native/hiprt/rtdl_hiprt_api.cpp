extern "C" int rtdl_hiprt_get_version(int* major, int* minor, int* patch) {
    if (major == nullptr || minor == nullptr || patch == nullptr) {
        return 1;
    }
    *major = HIPRT_MAJOR_VERSION;
    *minor = HIPRT_MINOR_VERSION;
    *patch = HIPRT_PATCH_VERSION;
    return 0;
}

extern "C" void rtdl_hiprt_free_rows(void* rows) {
    delete[] reinterpret_cast<unsigned char*>(rows);
}

extern "C" int rtdl_hiprt_prepare_ray_hitcount_3d(
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        if (triangle_count > 0 && triangles == nullptr) {
            throw std::runtime_error("triangle pointer must not be null when triangle_count is nonzero");
        }
        std::vector<hiprtFloat3> vertices = encode_triangle_vertices(triangles, triangle_count);
        HiprtRuntime runtime = create_runtime();
        hiprtSetLogLevel(hiprtLogLevelError);
        DeviceAllocation vertex_device(vertices.size() * sizeof(hiprtFloat3));
        copy_host_to_device(vertex_device, vertices);
        hiprtGeometry geometry = build_triangle_geometry(runtime.context, vertex_device, vertices.size(), triangle_count);
        try {
            oroFunction kernel = build_trace_kernel(runtime.context, "RtdlRayHitcount3DKernel");
            *prepared_out = new PreparedRayHitcount3D(std::move(runtime), std::move(vertex_device), geometry, kernel);
            geometry = nullptr;
        } catch (...) {
            if (geometry != nullptr) {
                hiprtDestroyGeometry(runtime.context, geometry);
            }
            throw;
        }
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_ray_hitcount_3d(void* prepared) {
    delete reinterpret_cast<PreparedRayHitcount3D*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_ray_hitcount_3d(
    void* prepared,
    const RtdlRay3D* rays,
    size_t ray_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT ray-hitcount handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        if (ray_count > 0 && rays == nullptr) {
            throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
        }
        run_prepared_ray_hitcount_3d(
            *reinterpret_cast<PreparedRayHitcount3D*>(prepared),
            rays,
            ray_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_ray_anyhit_2d(
    const RtdlTriangle* triangles,
    size_t triangle_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        if (triangle_count > std::numeric_limits<uint32_t>::max()) {
            throw std::runtime_error("HIPRT prepared 2D ray_triangle_any_hit currently supports at most 2^32-1 triangles");
        }
        if (triangle_count > 0 && triangles == nullptr) {
            throw std::runtime_error("triangle pointer must not be null when triangle_count is nonzero");
        }
        if (triangle_count == 0) {
            *prepared_out = new PreparedRayAnyhit2D(true);
            return;
        }

        std::vector<RtdlHiprtTriangle2DDevice> triangle_values = encode_triangles_2d(triangles, triangle_count);
        std::vector<RtdlHiprtAabb> aabb_values = encode_triangle_2d_aabbs(
            triangle_values.data(),
            triangle_values.size());
        HiprtRuntime runtime = create_runtime();
        hiprtSetLogLevel(hiprtLogLevelError);
        DeviceAllocation triangle_device(triangle_values.size() * sizeof(RtdlHiprtTriangle2DDevice));
        DeviceAllocation aabb_device(aabb_values.size() * sizeof(RtdlHiprtAabb));
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
            *prepared_out = new PreparedRayAnyhit2D(
                std::move(runtime),
                std::move(triangle_device),
                std::move(aabb_device),
                geometry,
                func_table,
                kernel);
            geometry = nullptr;
            func_table = nullptr;
        } catch (...) {
            if (func_table != nullptr) {
                hiprtDestroyFuncTable(runtime.context, func_table);
            }
            if (geometry != nullptr) {
                hiprtDestroyGeometry(runtime.context, geometry);
            }
            throw;
        }
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_ray_anyhit_2d(void* prepared) {
    delete reinterpret_cast<PreparedRayAnyhit2D*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_ray_anyhit_2d(
    void* prepared,
    const RtdlRay2D* rays,
    size_t ray_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT ray-anyhit handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_ray_anyhit_2d(
            *reinterpret_cast<PreparedRayAnyhit2D*>(prepared),
            rays,
            ray_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_ray_hitcount_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
            throw std::runtime_error("input pointers must not be null when counts are nonzero");
        }

        std::vector<hiprtFloat3> vertices;
        vertices.reserve(triangle_count * 3);
        for (size_t i = 0; i < triangle_count; ++i) {
            vertices.push_back({static_cast<float>(triangles[i].x0), static_cast<float>(triangles[i].y0), static_cast<float>(triangles[i].z0)});
            vertices.push_back({static_cast<float>(triangles[i].x1), static_cast<float>(triangles[i].y1), static_cast<float>(triangles[i].z1)});
            vertices.push_back({static_cast<float>(triangles[i].x2), static_cast<float>(triangles[i].y2), static_cast<float>(triangles[i].z2)});
        }
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

        HiprtRuntime runtime = create_runtime();
        hiprtSetLogLevel(hiprtLogLevelError);

        DeviceAllocation vertex_device(vertices.size() * sizeof(hiprtFloat3));
        copy_host_to_device(vertex_device, vertices);

        hiprtTriangleMeshPrimitive mesh{};
        mesh.triangleCount = static_cast<uint32_t>(triangle_count);
        mesh.triangleStride = sizeof(hiprtInt3);
        mesh.triangleIndices = nullptr;
        mesh.vertexCount = static_cast<uint32_t>(vertices.size());
        mesh.vertexStride = sizeof(hiprtFloat3);
        mesh.vertices = vertex_device.get();

        hiprtGeometryBuildInput geom_input{};
        geom_input.type = hiprtPrimitiveTypeTriangleMesh;
        geom_input.primitive.triangleMesh = mesh;

        hiprtBuildOptions options{};
        options.buildFlags = hiprtBuildFlagBitPreferFastBuild;
        size_t temp_size = 0;
        check_hiprt("hiprtGetGeometryBuildTemporaryBufferSize", hiprtGetGeometryBuildTemporaryBufferSize(runtime.context, geom_input, options, temp_size));
        DeviceAllocation temp_device(temp_size);
        hiprtGeometry geometry{};
        check_hiprt("hiprtCreateGeometry", hiprtCreateGeometry(runtime.context, geom_input, options, geometry));
        try {
            check_hiprt(
                "hiprtBuildGeometry",
                hiprtBuildGeometry(runtime.context, hiprtBuildOperationBuild, geom_input, options, temp_device.get(), 0, geometry));

            DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay3DDevice));
            copy_host_to_device(ray_device, ray_values);
            std::vector<RtdlRayHitCountRow> output(ray_count);
            DeviceAllocation output_device(output.size() * sizeof(RtdlRayHitCountRow));

            oroFunction kernel = build_trace_kernel(runtime.context, "RtdlRayHitcount3DKernel");
            uint32_t block_size = 128;
            uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
            void* ray_device_ptr = ray_device.get();
            void* output_device_ptr = output_device.get();
            uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
            void* args[] = {&geometry, &ray_device_ptr, &ray_count_u32, &output_device_ptr};
            check_oro(
                "oroModuleLaunchKernel",
                oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
            copy_device_to_host(output, output_device);

            auto* rows = new unsigned char[output.size() * sizeof(RtdlRayHitCountRow)];
            if (!output.empty()) {
                std::memcpy(rows, output.data(), output.size() * sizeof(RtdlRayHitCountRow));
            }
            *rows_out = reinterpret_cast<RtdlRayHitCountRow*>(rows);
            *row_count_out = output.size();
            check_hiprt("hiprtDestroyGeometry", hiprtDestroyGeometry(runtime.context, geometry));
            geometry = nullptr;
        } catch (...) {
            if (geometry != nullptr) {
                hiprtDestroyGeometry(runtime.context, geometry);
            }
            throw;
        }
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_ray_anyhit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
            throw std::runtime_error("input pointers must not be null when counts are nonzero");
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

        std::vector<hiprtFloat3> vertices;
        vertices.reserve(triangle_count * 3);
        for (size_t i = 0; i < triangle_count; ++i) {
            vertices.push_back({static_cast<float>(triangles[i].x0), static_cast<float>(triangles[i].y0), static_cast<float>(triangles[i].z0)});
            vertices.push_back({static_cast<float>(triangles[i].x1), static_cast<float>(triangles[i].y1), static_cast<float>(triangles[i].z1)});
            vertices.push_back({static_cast<float>(triangles[i].x2), static_cast<float>(triangles[i].y2), static_cast<float>(triangles[i].z2)});
        }
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

        HiprtRuntime runtime = create_runtime();
        hiprtSetLogLevel(hiprtLogLevelError);

        DeviceAllocation vertex_device(vertices.size() * sizeof(hiprtFloat3));
        copy_host_to_device(vertex_device, vertices);

        hiprtTriangleMeshPrimitive mesh{};
        mesh.triangleCount = static_cast<uint32_t>(triangle_count);
        mesh.triangleStride = sizeof(hiprtInt3);
        mesh.triangleIndices = nullptr;
        mesh.vertexCount = static_cast<uint32_t>(vertices.size());
        mesh.vertexStride = sizeof(hiprtFloat3);
        mesh.vertices = vertex_device.get();

        hiprtGeometryBuildInput geom_input{};
        geom_input.type = hiprtPrimitiveTypeTriangleMesh;
        geom_input.primitive.triangleMesh = mesh;

        hiprtBuildOptions options{};
        options.buildFlags = hiprtBuildFlagBitPreferFastBuild;
        size_t temp_size = 0;
        check_hiprt("hiprtGetGeometryBuildTemporaryBufferSize", hiprtGetGeometryBuildTemporaryBufferSize(runtime.context, geom_input, options, temp_size));
        DeviceAllocation temp_device(temp_size);
        hiprtGeometry geometry{};
        check_hiprt("hiprtCreateGeometry", hiprtCreateGeometry(runtime.context, geom_input, options, geometry));
        try {
            check_hiprt(
                "hiprtBuildGeometry",
                hiprtBuildGeometry(runtime.context, hiprtBuildOperationBuild, geom_input, options, temp_device.get(), 0, geometry));

            DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay3DDevice));
            copy_host_to_device(ray_device, ray_values);
            std::vector<RtdlRayAnyHitRow> output(ray_count);
            DeviceAllocation output_device(output.size() * sizeof(RtdlRayAnyHitRow));

            const std::string source = ray_anyhit_kernel_source_3d();
            oroFunction kernel = build_trace_kernel_from_source(
                runtime.context,
                source.c_str(),
                "rtdl_hiprt_ray_anyhit_3d.cu",
                "RtdlRayAnyhit3DKernel");
            uint32_t block_size = 128;
            uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
            void* ray_device_ptr = ray_device.get();
            void* output_device_ptr = output_device.get();
            uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
            void* args[] = {&geometry, &ray_device_ptr, &ray_count_u32, &output_device_ptr};
            check_oro(
                "oroModuleLaunchKernel",
                oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));
            copy_device_to_host(output, output_device);

            *rows_out = copy_rows_to_heap(output);
            *row_count_out = output.size();
            check_hiprt("hiprtDestroyGeometry", hiprtDestroyGeometry(runtime.context, geometry));
            geometry = nullptr;
        } catch (...) {
            if (geometry != nullptr) {
                hiprtDestroyGeometry(runtime.context, geometry);
            }
            throw;
        }
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* queries,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_fixed_radius_neighbors_3d(
            queries,
            query_count,
            search_points,
            search_count,
            radius,
            k_max,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_fixed_radius_neighbors_3d(
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        auto prepared = prepare_fixed_radius_neighbors_3d(search_points, search_count, radius);
        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_fixed_radius_neighbors_3d(void* prepared) {
    delete reinterpret_cast<PreparedFixedRadiusNeighbors3D*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_fixed_radius_neighbors_3d(
    void* prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT fixed-radius-neighbors handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_fixed_radius_neighbors_3d(
            *reinterpret_cast<PreparedFixedRadiusNeighbors3D*>(prepared),
            queries,
            query_count,
            k_max,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_fixed_radius_neighbors_2d(
    const RtdlPoint* queries,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    uint32_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_fixed_radius_neighbors_2d(
            queries,
            query_count,
            search_points,
            search_count,
            radius,
            k_max,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_lsi(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_lsi_2d(left, left_count, right, right_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_ray_hitcount_2d(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_ray_hitcount_2d(rays, ray_count, triangles, triangle_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_ray_anyhit_2d(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_ray_anyhit_2d(rays, ray_count, triangles, triangle_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_pip(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlPipRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_pip_2d(points, point_count, polygons, polygon_count, vertices_xy, vertex_xy_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_overlay(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlOverlayRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_overlay_2d(
            left_polygons,
            left_count,
            left_vertices_xy,
            left_vertex_xy_count,
            right_polygons,
            right_count,
            right_vertices_xy,
            right_vertex_xy_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_point_nearest_segment(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_point_nearest_segment_2d(points, point_count, segments, segment_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_segment_polygon_hitcount(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_segment_polygon_hitcount_2d(
            segments,
            segment_count,
            polygons,
            polygon_count,
            vertices_xy,
            vertex_xy_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_segment_polygon_anyhit_rows(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    RtdlSegmentPolygonAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_segment_polygon_anyhit_rows_2d(
            segments,
            segment_count,
            polygons,
            polygon_count,
            vertices_xy,
            vertex_xy_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_bfs_expand(
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count,
    const uint32_t* visited,
    size_t visited_count,
    int dedupe,
    RtdlBfsRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_bfs_expand(
            frontier,
            frontier_count,
            row_offsets,
            row_offset_count,
            column_indices,
            edge_count,
            vertex_count,
            visited,
            visited_count,
            dedupe != 0,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_graph_csr(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    uint32_t vertex_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        auto prepared = prepare_graph_csr(row_offsets, row_offset_count, column_indices, edge_count, vertex_count);
        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_graph_csr(void* prepared) {
    delete reinterpret_cast<PreparedGraphCSR*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_bfs_expand(
    void* prepared,
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* visited,
    size_t visited_count,
    int dedupe,
    RtdlBfsRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT graph CSR handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_bfs_expand(
            *reinterpret_cast<PreparedGraphCSR*>(prepared),
            frontier,
            frontier_count,
            visited,
            visited_count,
            dedupe != 0,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_triangle_probe(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t column_index_count,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    uint32_t enforce_id_ascending,
    uint32_t unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_triangle_probe(
            row_offsets,
            row_offset_count,
            column_indices,
            column_index_count,
            seeds,
            seed_count,
            enforce_id_ascending != 0u,
            unique != 0u,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_prepared_triangle_probe(
    void* prepared,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    int enforce_id_ascending,
    int unique,
    RtdlTriangleRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT graph CSR handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_triangle_probe(
            *reinterpret_cast<PreparedGraphCSR*>(prepared),
            seeds,
            seed_count,
            enforce_id_ascending != 0,
            unique != 0,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_conjunctive_scan(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_conjunctive_scan(
            fields,
            field_count,
            row_values,
            row_count,
            clauses,
            clause_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_grouped_count(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_grouped_count(
            fields,
            field_count,
            row_values,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_grouped_sum(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_db_grouped_sum(
            fields,
            field_count,
            row_values,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            value_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_db_table(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out pointer must not be null");
        }
        *prepared_out = nullptr;
        auto prepared = prepare_db_table(fields, field_count, row_values, row_count);
        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_db_table(void* prepared) {
    delete reinterpret_cast<PreparedDbTable*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_conjunctive_scan(
    void* prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT DB table handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_db_conjunctive_scan(
            *reinterpret_cast<PreparedDbTable*>(prepared),
            clauses,
            clause_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_prepared_grouped_count(
    void* prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT DB table handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_db_grouped_count(
            *reinterpret_cast<PreparedDbTable*>(prepared),
            clauses,
            clause_count,
            group_key_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_prepared_grouped_sum(
    void* prepared,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT DB table handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_db_grouped_sum(
            *reinterpret_cast<PreparedDbTable*>(prepared),
            clauses,
            clause_count,
            group_key_field,
            value_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_context_probe(
    char* device_name,
    size_t device_name_size,
    int* device_type,
    int* api_version,
    char* error,
    size_t error_size) {
    set_message(error, error_size, "");
    if (device_name == nullptr || device_name_size == 0 || device_type == nullptr || api_version == nullptr) {
        set_message(error, error_size, "null output passed to rtdl_hiprt_context_probe");
        return 1;
    }
    device_name[0] = '\0';
    *device_type = -1;
    *api_version = HIPRT_API_VERSION;

    int init_err = oroInitialize(static_cast<oroApi>(ORO_API_CUDA), 0);
    if (init_err != static_cast<int>(oroSuccess)) {
        set_message(error, error_size, oro_initialize_error_message(init_err));
        return 2;
    }
    oroError oro_err = oroInit(0);
    if (oro_err != oroSuccess) {
        set_message(error, error_size, oro_error_message("oroInit", oro_err));
        return 3;
    }

    oroDevice device{};
    oro_err = oroDeviceGet(&device, 0);
    if (oro_err != oroSuccess) {
        set_message(error, error_size, oro_error_message("oroDeviceGet(0)", oro_err));
        return 4;
    }

    oroCtx ctx{};
    oro_err = oroCtxCreate(&ctx, 0, device);
    if (oro_err != oroSuccess) {
        set_message(error, error_size, oro_error_message("oroCtxCreate", oro_err));
        return 5;
    }

    oroDeviceProp props{};
    oro_err = oroGetDeviceProperties(&props, device);
    if (oro_err != oroSuccess) {
        oroCtxDestroy(ctx);
        set_message(error, error_size, oro_error_message("oroGetDeviceProperties", oro_err));
        return 6;
    }
    set_message(device_name, device_name_size, props.name);

    hiprtContextCreationInput input{};
    input.ctxt = oroGetRawCtx(ctx);
    input.device = oroGetRawDevice(device);
    input.deviceType = std::strstr(props.name, "NVIDIA") != nullptr ? hiprtDeviceNVIDIA : hiprtDeviceAMD;
    *device_type = static_cast<int>(input.deviceType);

    hiprtContext hiprt_ctx{};
    hiprtError hiprt_err = hiprtCreateContext(HIPRT_API_VERSION, input, hiprt_ctx);
    if (hiprt_err != hiprtSuccess) {
        oroCtxDestroy(ctx);
        set_message(error, error_size, hiprt_error_message("hiprtCreateContext", hiprt_err));
        return 7;
    }
    hiprt_err = hiprtDestroyContext(hiprt_ctx);
    oroCtxDestroy(ctx);
    if (hiprt_err != hiprtSuccess) {
        set_message(error, error_size, hiprt_error_message("hiprtDestroyContext", hiprt_err));
        return 8;
    }
    return 0;
}
