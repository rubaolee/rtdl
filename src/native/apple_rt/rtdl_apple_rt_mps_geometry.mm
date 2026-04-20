extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_ray_closest_hit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayClosestHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_ray_closest_hit_3d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_ray_closest_hit_3d");
        return 1;
    }
    if (ray_count == 0 || triangle_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSPackedFloat3> vertices;
        vertices.reserve(triangle_count * 3);
        for (size_t i = 0; i < triangle_count; ++i) {
            const RtdlTriangle3D& tri = triangles[i];
            vertices.emplace_back(static_cast<float>(tri.x0), static_cast<float>(tri.y0), static_cast<float>(tri.z0));
            vertices.emplace_back(static_cast<float>(tri.x1), static_cast<float>(tri.y1), static_cast<float>(tri.z1));
            vertices.emplace_back(static_cast<float>(tri.x2), static_cast<float>(tri.y2), static_cast<float>(tri.z2));
        }

        id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                          length:vertices.size() * sizeof(MPSPackedFloat3)
                                                         options:MTLResourceStorageModeShared];
        if (vertex_buffer == nil) {
            set_message(error_out, error_size, "Metal vertex buffer creation failed");
            return 4;
        }

        MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
        if (accel == nil) {
            set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed");
            return 5;
        }
        accel.vertexBuffer = vertex_buffer;
        accel.vertexStride = sizeof(MPSPackedFloat3);
        accel.triangleCount = triangle_count;
        [accel rebuild];

        std::vector<MPSRayOriginMinDistanceDirectionMaxDistance> mps_rays(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            if (!valid_ray(rays[i])) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].minDistance = 0.0f;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), static_cast<float>(rays[i].oz));
            mps_rays[i].minDistance = 0.0f;
            mps_rays[i].direction = MPSPackedFloat3(static_cast<float>(rays[i].dx), static_cast<float>(rays[i].dy), static_cast<float>(rays[i].dz));
            mps_rays[i].maxDistance = finite_tmax(rays[i].tmax);
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMinDistanceDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 6;
        }

        std::vector<MPSIntersectionDistancePrimitiveIndex> intersections(ray_count);
        id<MTLBuffer> intersection_buffer = [device newBufferWithBytes:intersections.data()
                                                                length:intersections.size() * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                               options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal intersection buffer creation failed");
            return 7;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 8;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMinDistanceDirectionMaxDistance;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMinDistanceDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
        if (command_buffer == nil) {
            set_message(error_out, error_size, "Metal command buffer creation failed");
            return 9;
        }
        [intersector encodeIntersectionToCommandBuffer:command_buffer
                                      intersectionType:MPSIntersectionTypeNearest
                                             rayBuffer:ray_buffer
                                       rayBufferOffset:0
                                    intersectionBuffer:intersection_buffer
                              intersectionBufferOffset:0
                                              rayCount:ray_count
                                 accelerationStructure:accel];
        [command_buffer commit];
        [command_buffer waitUntilCompleted];
        NSError* error = [command_buffer error];
        if (error != nil) {
            set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
            return 10;
        }

        const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
        std::vector<RtdlRayClosestHitRow> rows;
        rows.reserve(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            const float distance = gpu_intersections[i].distance;
            const uint32_t primitive_index = gpu_intersections[i].primitiveIndex;
            if (distance < 0.0f || primitive_index >= triangle_count) {
                continue;
            }
            rows.push_back(RtdlRayClosestHitRow{
                rays[i].id,
                triangles[primitive_index].id,
                static_cast<double>(distance),
            });
        }
        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlRayClosestHitRow*>(std::malloc(rows.size() * sizeof(RtdlRayClosestHitRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT closest-hit rows");
            return 11;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlRayClosestHitRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_prepare_ray_closest_hit_3d(
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    void** handle_out,
    char* error_out,
    size_t error_size) {
    if (handle_out == nullptr) {
        set_message(error_out, error_size, "null handle output passed to rtdl_apple_rt_prepare_ray_closest_hit_3d");
        return 1;
    }
    *handle_out = nullptr;
    if (triangle_count > 0 && triangles == nullptr) {
        set_message(error_out, error_size, "null triangles passed to rtdl_apple_rt_prepare_ray_closest_hit_3d");
        return 1;
    }

    @autoreleasepool {
        auto* prepared = new (std::nothrow) AppleRtClosestHitPrepared();
        if (prepared == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT prepared closest-hit handle");
            return 2;
        }
        prepared->device = MTLCreateSystemDefaultDevice();
        if (prepared->device == nil) {
            delete prepared;
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 3;
        }
        prepared->command_queue = [prepared->device newCommandQueue];
        if (prepared->command_queue == nil) {
            delete prepared;
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 4;
        }
        prepared->intersector = [[MPSRayIntersector alloc] initWithDevice:prepared->device];
        if (prepared->intersector == nil) {
            delete prepared;
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 5;
        }
        prepared->intersector.cullMode = MTLCullModeNone;
        prepared->intersector.rayDataType = MPSRayDataTypeOriginMinDistanceDirectionMaxDistance;
        prepared->intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        prepared->intersector.rayStride = sizeof(MPSRayOriginMinDistanceDirectionMaxDistance);
        prepared->intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        if (triangle_count > 0) {
            std::vector<MPSPackedFloat3> vertices;
            vertices.reserve(triangle_count * 3);
            prepared->triangle_ids.reserve(triangle_count);
            for (size_t i = 0; i < triangle_count; ++i) {
                const RtdlTriangle3D& tri = triangles[i];
                vertices.emplace_back(static_cast<float>(tri.x0), static_cast<float>(tri.y0), static_cast<float>(tri.z0));
                vertices.emplace_back(static_cast<float>(tri.x1), static_cast<float>(tri.y1), static_cast<float>(tri.z1));
                vertices.emplace_back(static_cast<float>(tri.x2), static_cast<float>(tri.y2), static_cast<float>(tri.z2));
                prepared->triangle_ids.push_back(tri.id);
            }
            prepared->vertex_buffer = [prepared->device newBufferWithBytes:vertices.data()
                                                                    length:vertices.size() * sizeof(MPSPackedFloat3)
                                                                   options:MTLResourceStorageModeShared];
            if (prepared->vertex_buffer == nil) {
                delete prepared;
                set_message(error_out, error_size, "Metal vertex buffer creation failed");
                return 6;
            }
            prepared->accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:prepared->device];
            if (prepared->accel == nil) {
                delete prepared;
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed");
                return 7;
            }
            prepared->accel.vertexBuffer = prepared->vertex_buffer;
            prepared->accel.vertexStride = sizeof(MPSPackedFloat3);
            prepared->accel.triangleCount = triangle_count;
            [prepared->accel rebuild];
        }
        *handle_out = prepared;
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_prepared_ray_closest_hit_3d(
    void* handle,
    const RtdlRay3D* rays,
    size_t ray_count,
    RtdlRayClosestHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    @autoreleasepool {
        return run_closest_hit_prepared(
            static_cast<AppleRtClosestHitPrepared*>(handle),
            rays,
            ray_count,
            rows_out,
            row_count_out,
            error_out,
            error_size);
    }
}

extern "C" RTDL_APPLE_RT_EXPORT void rtdl_apple_rt_destroy_prepared_ray_closest_hit_3d(void* handle) {
    delete static_cast<AppleRtClosestHitPrepared*>(handle);
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_ray_anyhit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_ray_anyhit_3d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_ray_anyhit_3d");
        return 1;
    }
    if (ray_count == 0) {
        return 0;
    }

    std::vector<RtdlRayAnyHitRow> rows(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        rows[i] = RtdlRayAnyHitRow{rays[i].id, 0u};
    }
    if (triangle_count == 0) {
        auto* out = static_cast<RtdlRayAnyHitRow*>(std::malloc(rows.size() * sizeof(RtdlRayAnyHitRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT any-hit rows");
            return 2;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlRayAnyHitRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = [MTLCreateSystemDefaultDevice() autorelease];
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 3;
        }
        id<MTLCommandQueue> command_queue = [[device newCommandQueue] autorelease];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 4;
        }

        std::vector<MPSPackedFloat3> vertices;
        vertices.reserve(triangle_count * 3);
        for (size_t i = 0; i < triangle_count; ++i) {
            const RtdlTriangle3D& tri = triangles[i];
            vertices.emplace_back(static_cast<float>(tri.x0), static_cast<float>(tri.y0), static_cast<float>(tri.z0));
            vertices.emplace_back(static_cast<float>(tri.x1), static_cast<float>(tri.y1), static_cast<float>(tri.z1));
            vertices.emplace_back(static_cast<float>(tri.x2), static_cast<float>(tri.y2), static_cast<float>(tri.z2));
        }

        id<MTLBuffer> vertex_buffer = [[device newBufferWithBytes:vertices.data()
                                                           length:vertices.size() * sizeof(MPSPackedFloat3)
                                                          options:MTLResourceStorageModeShared] autorelease];
        if (vertex_buffer == nil) {
            set_message(error_out, error_size, "Metal vertex buffer creation failed");
            return 5;
        }

        MPSTriangleAccelerationStructure* accel = [[[MPSTriangleAccelerationStructure alloc] initWithDevice:device] autorelease];
        if (accel == nil) {
            set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed");
            return 6;
        }
        accel.vertexBuffer = vertex_buffer;
        accel.vertexStride = sizeof(MPSPackedFloat3);
        accel.triangleCount = triangle_count;
        [accel rebuild];

        std::vector<MPSRayOriginMinDistanceDirectionMaxDistance> mps_rays(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            if (!valid_ray(rays[i])) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].minDistance = 0.0f;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), static_cast<float>(rays[i].oz));
            mps_rays[i].minDistance = 0.0f;
            mps_rays[i].direction = MPSPackedFloat3(static_cast<float>(rays[i].dx), static_cast<float>(rays[i].dy), static_cast<float>(rays[i].dz));
            mps_rays[i].maxDistance = finite_tmax(rays[i].tmax);
        }

        id<MTLBuffer> ray_buffer = [[device newBufferWithBytes:mps_rays.data()
                                                        length:mps_rays.size() * sizeof(MPSRayOriginMinDistanceDirectionMaxDistance)
                                                       options:MTLResourceStorageModeShared] autorelease];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 7;
        }

        id<MTLBuffer> intersection_buffer = [[device newBufferWithLength:ray_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                  options:MTLResourceStorageModeShared] autorelease];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal intersection buffer creation failed");
            return 8;
        }

        MPSRayIntersector* intersector = [[[MPSRayIntersector alloc] initWithDevice:device] autorelease];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 9;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMinDistanceDirectionMaxDistance;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMinDistanceDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
        if (command_buffer == nil) {
            set_message(error_out, error_size, "Metal command buffer creation failed");
            return 10;
        }
        [intersector encodeIntersectionToCommandBuffer:command_buffer
                                      intersectionType:MPSIntersectionTypeNearest
                                             rayBuffer:ray_buffer
                                       rayBufferOffset:0
                                    intersectionBuffer:intersection_buffer
                              intersectionBufferOffset:0
                                              rayCount:ray_count
                                 accelerationStructure:accel];
        [command_buffer commit];
        [command_buffer waitUntilCompleted];
        NSError* error = [command_buffer error];
        if (error != nil) {
            set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
            return 11;
        }

        const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
        for (size_t i = 0; i < ray_count; ++i) {
            const float distance = gpu_intersections[i].distance;
            const uint32_t primitive_index = gpu_intersections[i].primitiveIndex;
            rows[i].any_hit = (distance >= 0.0f && primitive_index < triangle_count) ? 1u : 0u;
        }
    }

    auto* out = static_cast<RtdlRayAnyHitRow*>(std::malloc(rows.size() * sizeof(RtdlRayAnyHitRow)));
    if (out == nullptr) {
        set_message(error_out, error_size, "out of memory allocating Apple RT any-hit rows");
        return 12;
    }
    std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlRayAnyHitRow));
    *rows_out = out;
    *row_count_out = rows.size();
    return 0;
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_ray_hitcount_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_ray_hitcount_3d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_ray_hitcount_3d");
        return 1;
    }
    if (ray_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            if (!valid_ray(rays[i])) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].mask = 0;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), static_cast<float>(rays[i].oz));
            mps_rays[i].mask = 0xFFFFFFFFu;
            mps_rays[i].direction = MPSPackedFloat3(static_cast<float>(rays[i].dx), static_cast<float>(rays[i].dy), static_cast<float>(rays[i].dz));
            mps_rays[i].maxDistance = finite_tmax(rays[i].tmax);
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 4;
        }

        std::vector<uint32_t> counts(ray_count, 0);
        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:ray_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < triangle_count; chunk_begin += chunk_size) {
            const size_t chunk_count = std::min(chunk_size, triangle_count - chunk_begin);
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);

            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                gpu_rays[ray_index].mask = valid_ray(rays[ray_index]) ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            vertices.reserve(chunk_count * 3);
            std::vector<uint32_t> primitive_masks;
            primitive_masks.reserve(chunk_count);
            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlTriangle3D& tri = triangles[chunk_begin + local_index];
                vertices.emplace_back(static_cast<float>(tri.x0), static_cast<float>(tri.y0), static_cast<float>(tri.z0));
                vertices.emplace_back(static_cast<float>(tri.x1), static_cast<float>(tri.y1), static_cast<float>(tri.z1));
                vertices.emplace_back(static_cast<float>(tri.x2), static_cast<float>(tri.y2), static_cast<float>(tri.z2));
                primitive_masks.push_back(1u << local_index);
            }

            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal primitive mask buffer creation failed");
                return 8;
            }
            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.triangleCount = chunk_count;
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
                }
                [intersector encodeIntersectionToCommandBuffer:command_buffer
                                              intersectionType:MPSIntersectionTypeNearest
                                                     rayBuffer:ray_buffer
                                               rayBufferOffset:0
                                            intersectionBuffer:intersection_buffer
                                      intersectionBufferOffset:0
                                                      rayCount:ray_count
                                         accelerationStructure:accel];
                [command_buffer commit];
                [command_buffer waitUntilCompleted];
                NSError* error = [command_buffer error];
                if (error != nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                    const float distance = gpu_intersections[ray_index].distance;
                    const uint32_t primitive_index = gpu_intersections[ray_index].primitiveIndex;
                    if (distance >= 0.0f && primitive_index < chunk_count) {
                        const uint32_t bit = 1u << primitive_index;
                        if ((gpu_rays[ray_index].mask & bit) != 0u) {
                            counts[ray_index] += 1;
                            gpu_rays[ray_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[ray_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        auto* out = static_cast<RtdlRayHitCountRow*>(std::malloc(ray_count * sizeof(RtdlRayHitCountRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT hit-count rows");
            return 11;
        }
        for (size_t i = 0; i < ray_count; ++i) {
            out[i] = RtdlRayHitCountRow{rays[i].id, counts[i]};
        }
        *rows_out = out;
        *row_count_out = ray_count;
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_ray_hitcount_2d(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle2D* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_ray_hitcount_2d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((ray_count > 0 && rays == nullptr) || (triangle_count > 0 && triangles == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_ray_hitcount_2d");
        return 1;
    }
    if (ray_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(ray_count);
        for (size_t i = 0; i < ray_count; ++i) {
            if (!valid_ray_2d(rays[i])) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].mask = 0;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            // Parameter t in MPS maps to the full finite RTDL ray segment:
            // xy(t) = origin + direction * (ray.tmax * t), z(t) = -1 + 2t.
            // The z sweep makes contained 2D cases intersect the triangle prism.
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(rays[i].ox), static_cast<float>(rays[i].oy), -1.0f);
            mps_rays[i].mask = 0xFFFFFFFFu;
            mps_rays[i].direction = MPSPackedFloat3(
                static_cast<float>(rays[i].dx * rays[i].tmax),
                static_cast<float>(rays[i].dy * rays[i].tmax),
                2.0f);
            mps_rays[i].maxDistance = 1.000001f;
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 4;
        }

        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:ray_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        std::vector<uint32_t> counts(ray_count, 0);
        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < triangle_count; chunk_begin += chunk_size) {
            const size_t chunk_count = std::min(chunk_size, triangle_count - chunk_begin);
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);

            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                gpu_rays[ray_index].mask = valid_ray_2d(rays[ray_index]) ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            std::vector<uint32_t> primitive_masks;
            std::vector<size_t> primitive_triangle_offsets;
            vertices.reserve(chunk_count * 24);
            primitive_masks.reserve(chunk_count * 8);
            primitive_triangle_offsets.reserve(chunk_count * 8);

            auto add_triangle = [&](float ax, float ay, float az, float bx, float by, float bz, float cx, float cy, float cz, uint32_t mask, size_t local_index) {
                vertices.emplace_back(ax, ay, az);
                vertices.emplace_back(bx, by, bz);
                vertices.emplace_back(cx, cy, cz);
                primitive_masks.push_back(mask);
                primitive_triangle_offsets.push_back(local_index);
            };

            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlTriangle2D& tri = triangles[chunk_begin + local_index];
                const uint32_t mask = 1u << local_index;
                const float x0 = static_cast<float>(tri.x0);
                const float y0 = static_cast<float>(tri.y0);
                const float x1 = static_cast<float>(tri.x1);
                const float y1 = static_cast<float>(tri.y1);
                const float x2 = static_cast<float>(tri.x2);
                const float y2 = static_cast<float>(tri.y2);
                constexpr float z0 = -1.0f;
                constexpr float z1 = 1.0f;

                add_triangle(x0, y0, z0, x1, y1, z0, x2, y2, z0, mask, local_index);
                add_triangle(x0, y0, z1, x2, y2, z1, x1, y1, z1, mask, local_index);

                add_triangle(x0, y0, z0, x1, y1, z0, x1, y1, z1, mask, local_index);
                add_triangle(x0, y0, z0, x1, y1, z1, x0, y0, z1, mask, local_index);
                add_triangle(x1, y1, z0, x2, y2, z0, x2, y2, z1, mask, local_index);
                add_triangle(x1, y1, z0, x2, y2, z1, x1, y1, z1, mask, local_index);
                add_triangle(x2, y2, z0, x0, y0, z0, x0, y0, z1, mask, local_index);
                add_triangle(x2, y2, z0, x0, y0, z1, x2, y2, z1, mask, local_index);
            }

            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal 2D hit-count prism vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal 2D hit-count primitive mask buffer creation failed");
                return 8;
            }

            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed for 2D hit-count");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.triangleCount = primitive_masks.size();
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
                }
                [intersector encodeIntersectionToCommandBuffer:command_buffer
                                              intersectionType:MPSIntersectionTypeNearest
                                                     rayBuffer:ray_buffer
                                               rayBufferOffset:0
                                            intersectionBuffer:intersection_buffer
                                      intersectionBufferOffset:0
                                                      rayCount:ray_count
                                         accelerationStructure:accel];
                [command_buffer commit];
                [command_buffer waitUntilCompleted];
                NSError* error = [command_buffer error];
                if (error != nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* gpu_intersections = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
                    const float distance = gpu_intersections[ray_index].distance;
                    const uint32_t primitive_index = gpu_intersections[ray_index].primitiveIndex;
                    if (distance >= 0.0f && distance <= 1.000001f && primitive_index < primitive_triangle_offsets.size()) {
                        const size_t local_index = primitive_triangle_offsets[primitive_index];
                        const uint32_t bit = 1u << local_index;
                        if ((gpu_rays[ray_index].mask & bit) != 0u) {
                            const RtdlTriangle2D& tri = triangles[chunk_begin + local_index];
                            if (ray_hits_triangle_2d(rays[ray_index], tri)) {
                                counts[ray_index] += 1;
                            }
                            gpu_rays[ray_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[ray_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        auto* out = static_cast<RtdlRayHitCountRow*>(std::malloc(ray_count * sizeof(RtdlRayHitCountRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT 2D hit-count rows");
            return 12;
        }
        for (size_t i = 0; i < ray_count; ++i) {
            out[i] = RtdlRayHitCountRow{rays[i].id, counts[i]};
        }
        *rows_out = out;
        *row_count_out = ray_count;
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_fixed_radius_neighbors_2d(
    const RtdlPoint2D* queries,
    size_t query_count,
    const RtdlPoint2D* points,
    size_t point_count,
    double radius,
    uint32_t k_max,
    RtdlNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_fixed_radius_neighbors_2d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((query_count > 0 && queries == nullptr) || (point_count > 0 && points == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_fixed_radius_neighbors_2d");
        return 1;
    }
    if (!std::isfinite(radius) || radius < 0.0 || k_max == 0) {
        set_message(error_out, error_size, "invalid radius or k_max passed to rtdl_apple_rt_run_fixed_radius_neighbors_2d");
        return 1;
    }
    if (query_count == 0 || point_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(query_count);
        for (size_t i = 0; i < query_count; ++i) {
            if (!std::isfinite(queries[i].x) || !std::isfinite(queries[i].y)) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].mask = 0;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(queries[i].x), static_cast<float>(queries[i].y), -1.0f);
            mps_rays[i].mask = 0xFFFFFFFFu;
            mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 2.0f);
            mps_rays[i].maxDistance = 1.000001f;
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal query ray buffer creation failed");
            return 4;
        }
        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:query_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal neighbor intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        std::vector<std::vector<RtdlNeighborRow>> candidates_by_query(query_count);
        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < point_count; chunk_begin += chunk_size) {
            const size_t chunk_count = std::min(chunk_size, point_count - chunk_begin);
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);
            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t query_index = 0; query_index < query_count; ++query_index) {
                const bool valid_query = std::isfinite(queries[query_index].x) && std::isfinite(queries[query_index].y);
                gpu_rays[query_index].mask = valid_query ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            std::vector<uint32_t> primitive_masks;
            std::vector<size_t> primitive_point_offsets;
            vertices.reserve(chunk_count * 24);
            primitive_masks.reserve(chunk_count * 8);
            primitive_point_offsets.reserve(chunk_count * 8);

            auto add_triangle = [&](float ax, float ay, float az, float bx, float by, float bz, float cx, float cy, float cz, uint32_t mask, size_t local_index) {
                vertices.emplace_back(ax, ay, az);
                vertices.emplace_back(bx, by, bz);
                vertices.emplace_back(cx, cy, cz);
                primitive_masks.push_back(mask);
                primitive_point_offsets.push_back(local_index);
            };

            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlPoint2D& point = points[chunk_begin + local_index];
                const uint32_t mask = 1u << local_index;
                const float minx = static_cast<float>(point.x - radius);
                const float maxx = static_cast<float>(point.x + radius);
                const float miny = static_cast<float>(point.y - radius);
                const float maxy = static_cast<float>(point.y + radius);
                constexpr float z0 = -1.0f;
                constexpr float z1 = 1.0f;

                add_triangle(minx, miny, z0, maxx, miny, z0, maxx, maxy, z0, mask, local_index);
                add_triangle(minx, miny, z0, maxx, maxy, z0, minx, maxy, z0, mask, local_index);
                add_triangle(minx, miny, z1, maxx, maxy, z1, maxx, miny, z1, mask, local_index);
                add_triangle(minx, miny, z1, minx, maxy, z1, maxx, maxy, z1, mask, local_index);
                add_triangle(minx, miny, z0, maxx, miny, z0, maxx, miny, z1, mask, local_index);
                add_triangle(minx, miny, z0, maxx, miny, z1, minx, miny, z1, mask, local_index);
                add_triangle(maxx, maxy, z0, minx, maxy, z0, minx, maxy, z1, mask, local_index);
                add_triangle(maxx, maxy, z0, minx, maxy, z1, maxx, maxy, z1, mask, local_index);
                add_triangle(minx, miny, z0, minx, maxy, z0, minx, maxy, z1, mask, local_index);
                add_triangle(minx, miny, z0, minx, maxy, z1, minx, miny, z1, mask, local_index);
                add_triangle(maxx, miny, z0, maxx, maxy, z1, maxx, maxy, z0, mask, local_index);
                add_triangle(maxx, miny, z0, maxx, miny, z1, maxx, maxy, z1, mask, local_index);
            }

            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal fixed-radius box vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal fixed-radius primitive mask buffer creation failed");
                return 8;
            }

            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed for fixed-radius");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.triangleCount = primitive_masks.size();
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
                }
                [intersector encodeIntersectionToCommandBuffer:command_buffer
                                              intersectionType:MPSIntersectionTypeNearest
                                                     rayBuffer:ray_buffer
                                               rayBufferOffset:0
                                            intersectionBuffer:intersection_buffer
                                      intersectionBufferOffset:0
                                                      rayCount:query_count
                                         accelerationStructure:accel];
                [command_buffer commit];
                [command_buffer waitUntilCompleted];
                NSError* error = [command_buffer error];
                if (error != nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* hits = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t query_index = 0; query_index < query_count; ++query_index) {
                    const float distance = hits[query_index].distance;
                    const uint32_t primitive_index = hits[query_index].primitiveIndex;
                    if (distance >= 0.0f && distance <= 1.000001f && primitive_index < primitive_point_offsets.size()) {
                        const size_t local_index = primitive_point_offsets[primitive_index];
                        const uint32_t bit = 1u << local_index;
                        if ((gpu_rays[query_index].mask & bit) != 0u) {
                            const RtdlPoint2D& point = points[chunk_begin + local_index];
                            const double exact_distance = point_distance_2d(queries[query_index], point);
                            if (exact_distance <= radius + 1.0e-9) {
                                candidates_by_query[query_index].push_back(RtdlNeighborRow{queries[query_index].id, point.id, exact_distance});
                            }
                            gpu_rays[query_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[query_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        std::vector<RtdlNeighborRow> rows;
        for (auto& query_rows : candidates_by_query) {
            std::sort(query_rows.begin(), query_rows.end(), [](const auto& a, const auto& b) {
                if (a.distance != b.distance) {
                    return a.distance < b.distance;
                }
                return a.neighbor_id < b.neighbor_id;
            });
            const size_t keep = std::min(static_cast<size_t>(k_max), query_rows.size());
            for (size_t i = 0; i < keep; ++i) {
                rows.push_back(query_rows[i]);
            }
        }

        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlNeighborRow*>(std::malloc(rows.size() * sizeof(RtdlNeighborRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT fixed-radius rows");
            return 12;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlNeighborRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* queries,
    size_t query_count,
    const RtdlPoint3D* points,
    size_t point_count,
    double radius,
    uint32_t k_max,
    RtdlNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_fixed_radius_neighbors_3d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((query_count > 0 && queries == nullptr) || (point_count > 0 && points == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_fixed_radius_neighbors_3d");
        return 1;
    }
    if (!std::isfinite(radius) || radius < 0.0 || k_max == 0) {
        set_message(error_out, error_size, "invalid radius or k_max passed to rtdl_apple_rt_run_fixed_radius_neighbors_3d");
        return 1;
    }
    if (query_count == 0 || point_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(query_count);
        const float ray_extent = static_cast<float>(std::max(radius * 2.0 + 1.0e-6, 1.0e-6));
        for (size_t i = 0; i < query_count; ++i) {
            if (!std::isfinite(queries[i].x) || !std::isfinite(queries[i].y) || !std::isfinite(queries[i].z)) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].mask = 0;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(
                static_cast<float>(queries[i].x),
                static_cast<float>(queries[i].y),
                static_cast<float>(queries[i].z - radius));
            mps_rays[i].mask = 0xFFFFFFFFu;
            mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, ray_extent);
            mps_rays[i].maxDistance = 1.000001f;
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal 3D query ray buffer creation failed");
            return 4;
        }
        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:query_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal 3D neighbor intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        std::vector<std::vector<RtdlNeighborRow>> candidates_by_query(query_count);
        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < point_count; chunk_begin += chunk_size) {
            const size_t chunk_count = std::min(chunk_size, point_count - chunk_begin);
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);
            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t query_index = 0; query_index < query_count; ++query_index) {
                const bool valid_query = std::isfinite(queries[query_index].x) && std::isfinite(queries[query_index].y) && std::isfinite(queries[query_index].z);
                gpu_rays[query_index].mask = valid_query ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            std::vector<uint32_t> primitive_masks;
            std::vector<size_t> primitive_point_offsets;
            vertices.reserve(chunk_count * 36);
            primitive_masks.reserve(chunk_count * 12);
            primitive_point_offsets.reserve(chunk_count * 12);
            auto add_triangle = [&](float ax, float ay, float az, float bx, float by, float bz, float cx, float cy, float cz, uint32_t mask, size_t local_index) {
                vertices.emplace_back(ax, ay, az);
                vertices.emplace_back(bx, by, bz);
                vertices.emplace_back(cx, cy, cz);
                primitive_masks.push_back(mask);
                primitive_point_offsets.push_back(local_index);
            };

            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlPoint3D& point = points[chunk_begin + local_index];
                const uint32_t mask = 1u << local_index;
                const float x0 = static_cast<float>(point.x - radius);
                const float x1 = static_cast<float>(point.x + radius);
                const float y0 = static_cast<float>(point.y - radius);
                const float y1 = static_cast<float>(point.y + radius);
                const float z0 = static_cast<float>(point.z - radius);
                const float z1 = static_cast<float>(point.z + radius);

                add_triangle(x0, y0, z0, x1, y0, z0, x1, y1, z0, mask, local_index);
                add_triangle(x0, y0, z0, x1, y1, z0, x0, y1, z0, mask, local_index);
                add_triangle(x0, y0, z1, x1, y1, z1, x1, y0, z1, mask, local_index);
                add_triangle(x0, y0, z1, x0, y1, z1, x1, y1, z1, mask, local_index);
                add_triangle(x0, y0, z0, x1, y0, z1, x1, y0, z0, mask, local_index);
                add_triangle(x0, y0, z0, x0, y0, z1, x1, y0, z1, mask, local_index);
                add_triangle(x0, y1, z0, x1, y1, z0, x1, y1, z1, mask, local_index);
                add_triangle(x0, y1, z0, x1, y1, z1, x0, y1, z1, mask, local_index);
                add_triangle(x0, y0, z0, x0, y1, z0, x0, y1, z1, mask, local_index);
                add_triangle(x0, y0, z0, x0, y1, z1, x0, y0, z1, mask, local_index);
                add_triangle(x1, y0, z0, x1, y1, z1, x1, y1, z0, mask, local_index);
                add_triangle(x1, y0, z0, x1, y0, z1, x1, y1, z1, mask, local_index);
            }

            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal 3D fixed-radius cube vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal 3D fixed-radius primitive mask buffer creation failed");
                return 8;
            }
            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed for 3D fixed-radius");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.triangleCount = primitive_masks.size();
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
                }
                [intersector encodeIntersectionToCommandBuffer:command_buffer
                                              intersectionType:MPSIntersectionTypeNearest
                                                     rayBuffer:ray_buffer
                                               rayBufferOffset:0
                                            intersectionBuffer:intersection_buffer
                                      intersectionBufferOffset:0
                                                      rayCount:query_count
                                         accelerationStructure:accel];
                [command_buffer commit];
                [command_buffer waitUntilCompleted];
                NSError* error = [command_buffer error];
                if (error != nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* hits = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t query_index = 0; query_index < query_count; ++query_index) {
                    const float distance = hits[query_index].distance;
                    const uint32_t primitive_index = hits[query_index].primitiveIndex;
                    if (distance >= 0.0f && distance <= 1.000001f && primitive_index < primitive_point_offsets.size()) {
                        const size_t local_index = primitive_point_offsets[primitive_index];
                        const uint32_t bit = 1u << local_index;
                        if ((gpu_rays[query_index].mask & bit) != 0u) {
                            const RtdlPoint3D& point = points[chunk_begin + local_index];
                            const double exact_distance = point_distance_3d(queries[query_index], point);
                            if (exact_distance <= radius + 1.0e-9) {
                                candidates_by_query[query_index].push_back(RtdlNeighborRow{queries[query_index].id, point.id, exact_distance});
                            }
                            gpu_rays[query_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[query_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        std::vector<RtdlNeighborRow> rows;
        for (auto& query_rows : candidates_by_query) {
            std::sort(query_rows.begin(), query_rows.end(), [](const auto& a, const auto& b) {
                if (a.distance != b.distance) {
                    return a.distance < b.distance;
                }
                return a.neighbor_id < b.neighbor_id;
            });
            const size_t keep = std::min(static_cast<size_t>(k_max), query_rows.size());
            for (size_t i = 0; i < keep; ++i) {
                rows.push_back(query_rows[i]);
            }
        }
        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlNeighborRow*>(std::malloc(rows.size() * sizeof(RtdlNeighborRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT 3D fixed-radius rows");
            return 12;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlNeighborRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_point_polygon_candidates_2d(
    const RtdlPoint2D* points,
    size_t point_count,
    const RtdlPolygonBounds2D* polygons,
    size_t polygon_count,
    RtdlPointPolygonCandidateRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_point_polygon_candidates_2d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((point_count > 0 && points == nullptr) || (polygon_count > 0 && polygons == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_point_polygon_candidates_2d");
        return 1;
    }
    if (point_count == 0 || polygon_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(point_count);
        for (size_t i = 0; i < point_count; ++i) {
            if (!std::isfinite(points[i].x) || !std::isfinite(points[i].y)) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].mask = 0;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(points[i].x), static_cast<float>(points[i].y), -1.0f);
            mps_rays[i].mask = 0xFFFFFFFFu;
            mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 2.0f);
            mps_rays[i].maxDistance = 1.000001f;
        }
        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal point-polygon ray buffer creation failed");
            return 4;
        }
        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:point_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal point-polygon intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        std::vector<std::vector<std::pair<size_t, RtdlPointPolygonCandidateRow>>> candidates_by_point(point_count);
        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < polygon_count; chunk_begin += chunk_size) {
            const size_t chunk_count = std::min(chunk_size, polygon_count - chunk_begin);
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);
            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t point_index = 0; point_index < point_count; ++point_index) {
                const bool valid_point = std::isfinite(points[point_index].x) && std::isfinite(points[point_index].y);
                gpu_rays[point_index].mask = valid_point ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            std::vector<uint32_t> primitive_masks;
            std::vector<size_t> primitive_polygon_offsets;
            vertices.reserve(chunk_count * 36);
            primitive_masks.reserve(chunk_count * 12);
            primitive_polygon_offsets.reserve(chunk_count * 12);
            auto add_triangle = [&](float ax, float ay, float az, float bx, float by, float bz, float cx, float cy, float cz, uint32_t mask, size_t local_index) {
                vertices.emplace_back(ax, ay, az);
                vertices.emplace_back(bx, by, bz);
                vertices.emplace_back(cx, cy, cz);
                primitive_masks.push_back(mask);
                primitive_polygon_offsets.push_back(local_index);
            };

            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlPolygonBounds2D& bounds = polygons[chunk_begin + local_index];
                const uint32_t mask = 1u << local_index;
                constexpr float eps = 1.0e-4f;
                const float minx = static_cast<float>(bounds.minx) - eps;
                const float maxx = static_cast<float>(bounds.maxx) + eps;
                const float miny = static_cast<float>(bounds.miny) - eps;
                const float maxy = static_cast<float>(bounds.maxy) + eps;
                constexpr float z0 = -0.9999f;
                constexpr float z1 = 0.9999f;
                add_triangle(minx, miny, z0, maxx, miny, z0, maxx, maxy, z0, mask, local_index);
                add_triangle(minx, miny, z0, maxx, maxy, z0, minx, maxy, z0, mask, local_index);
                add_triangle(minx, miny, z1, maxx, maxy, z1, maxx, miny, z1, mask, local_index);
                add_triangle(minx, miny, z1, minx, maxy, z1, maxx, maxy, z1, mask, local_index);
                add_triangle(minx, miny, z0, maxx, miny, z0, maxx, miny, z1, mask, local_index);
                add_triangle(minx, miny, z0, maxx, miny, z1, minx, miny, z1, mask, local_index);
                add_triangle(maxx, maxy, z0, minx, maxy, z0, minx, maxy, z1, mask, local_index);
                add_triangle(maxx, maxy, z0, minx, maxy, z1, maxx, maxy, z1, mask, local_index);
                add_triangle(minx, miny, z0, minx, maxy, z0, minx, maxy, z1, mask, local_index);
                add_triangle(minx, miny, z0, minx, maxy, z1, minx, miny, z1, mask, local_index);
                add_triangle(maxx, miny, z0, maxx, maxy, z1, maxx, maxy, z0, mask, local_index);
                add_triangle(maxx, miny, z0, maxx, miny, z1, maxx, maxy, z1, mask, local_index);
            }

            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal point-polygon box vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal point-polygon primitive mask buffer creation failed");
                return 8;
            }
            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed for point-polygon");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.triangleCount = primitive_masks.size();
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
                }
                [intersector encodeIntersectionToCommandBuffer:command_buffer
                                              intersectionType:MPSIntersectionTypeNearest
                                                     rayBuffer:ray_buffer
                                               rayBufferOffset:0
                                            intersectionBuffer:intersection_buffer
                                      intersectionBufferOffset:0
                                                      rayCount:point_count
                                         accelerationStructure:accel];
                [command_buffer commit];
                [command_buffer waitUntilCompleted];
                NSError* error = [command_buffer error];
                if (error != nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* hits = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t point_index = 0; point_index < point_count; ++point_index) {
                    const float distance = hits[point_index].distance;
                    const uint32_t primitive_index = hits[point_index].primitiveIndex;
                    if (distance >= 0.0f && distance <= 1.000001f && primitive_index < primitive_polygon_offsets.size()) {
                        const size_t local_index = primitive_polygon_offsets[primitive_index];
                        const uint32_t bit = 1u << local_index;
                        if ((gpu_rays[point_index].mask & bit) != 0u) {
                            const RtdlPolygonBounds2D& bounds = polygons[chunk_begin + local_index];
                            candidates_by_point[point_index].push_back({
                                chunk_begin + local_index,
                                RtdlPointPolygonCandidateRow{points[point_index].id, bounds.id},
                            });
                            gpu_rays[point_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[point_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        std::vector<RtdlPointPolygonCandidateRow> rows;
        for (auto& point_rows : candidates_by_point) {
            std::sort(point_rows.begin(), point_rows.end(), [](const auto& a, const auto& b) {
                return a.first < b.first;
            });
            for (const auto& item : point_rows) {
                rows.push_back(item.second);
            }
        }
        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlPointPolygonCandidateRow*>(std::malloc(rows.size() * sizeof(RtdlPointPolygonCandidateRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT point-polygon candidate rows");
            return 12;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlPointPolygonCandidateRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_segment_polygon_candidates_2d(
    const RtdlSegment* segments,
    size_t segment_count,
    const RtdlPolygonBounds2D* polygons,
    size_t polygon_count,
    RtdlSegmentPolygonCandidateRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_segment_polygon_candidates_2d");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((segment_count > 0 && segments == nullptr) || (polygon_count > 0 && polygons == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_segment_polygon_candidates_2d");
        return 1;
    }
    if (segment_count == 0 || polygon_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMaskDirectionMaxDistance> mps_rays(segment_count);
        for (size_t i = 0; i < segment_count; ++i) {
            const RtdlSegment& segment = segments[i];
            if (!valid_segment_ray(segment)) {
                mps_rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                mps_rays[i].mask = 0;
                mps_rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                mps_rays[i].maxDistance = -1.0f;
                continue;
            }
            mps_rays[i].origin = MPSPackedFloat3(static_cast<float>(segment.x0), static_cast<float>(segment.y0), -1.0f);
            mps_rays[i].mask = 0xFFFFFFFFu;
            mps_rays[i].direction = MPSPackedFloat3(
                static_cast<float>(segment.x1 - segment.x0),
                static_cast<float>(segment.y1 - segment.y0),
                2.0f);
            mps_rays[i].maxDistance = 1.000001f;
        }
        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:mps_rays.data()
                                                       length:mps_rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal segment-polygon ray buffer creation failed");
            return 4;
        }
        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:segment_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal segment-polygon intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        std::vector<std::vector<std::pair<size_t, RtdlSegmentPolygonCandidateRow>>> candidates_by_segment(segment_count);
        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < polygon_count; chunk_begin += chunk_size) {
            const size_t chunk_count = std::min(chunk_size, polygon_count - chunk_begin);
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);
            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t segment_index = 0; segment_index < segment_count; ++segment_index) {
                gpu_rays[segment_index].mask = valid_segment_ray(segments[segment_index]) ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            std::vector<uint32_t> primitive_masks;
            std::vector<size_t> primitive_polygon_offsets;
            vertices.reserve(chunk_count * 24);
            primitive_masks.reserve(chunk_count * 8);
            primitive_polygon_offsets.reserve(chunk_count * 8);
            auto add_triangle = [&](float ax, float ay, float az, float bx, float by, float bz, float cx, float cy, float cz, uint32_t mask, size_t local_index) {
                vertices.emplace_back(ax, ay, az);
                vertices.emplace_back(bx, by, bz);
                vertices.emplace_back(cx, cy, cz);
                primitive_masks.push_back(mask);
                primitive_polygon_offsets.push_back(local_index);
            };
            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlPolygonBounds2D& bounds = polygons[chunk_begin + local_index];
                const uint32_t mask = 1u << local_index;
                constexpr float xy_eps = 1.0e-4f;
                const float minx = static_cast<float>(bounds.minx) - xy_eps;
                const float maxx = static_cast<float>(bounds.maxx) + xy_eps;
                const float miny = static_cast<float>(bounds.miny) - xy_eps;
                const float maxy = static_cast<float>(bounds.maxy) + xy_eps;
                constexpr float z0 = -0.9999f;
                constexpr float z1 = 0.9999f;
                add_triangle(minx, miny, z0, maxx, miny, z0, maxx, maxy, z0, mask, local_index);
                add_triangle(minx, miny, z0, maxx, maxy, z0, minx, maxy, z0, mask, local_index);
                add_triangle(minx, miny, z1, maxx, maxy, z1, maxx, miny, z1, mask, local_index);
                add_triangle(minx, miny, z1, minx, maxy, z1, maxx, maxy, z1, mask, local_index);
                add_triangle(minx, miny, z0, maxx, miny, z0, maxx, miny, z1, mask, local_index);
                add_triangle(minx, miny, z0, maxx, miny, z1, minx, miny, z1, mask, local_index);
                add_triangle(maxx, maxy, z0, minx, maxy, z0, minx, maxy, z1, mask, local_index);
                add_triangle(maxx, maxy, z0, minx, maxy, z1, maxx, maxy, z1, mask, local_index);
                add_triangle(minx, maxy, z0, minx, miny, z0, minx, miny, z1, mask, local_index);
                add_triangle(minx, maxy, z0, minx, miny, z1, minx, maxy, z1, mask, local_index);
                add_triangle(maxx, miny, z0, maxx, maxy, z0, maxx, maxy, z1, mask, local_index);
                add_triangle(maxx, miny, z0, maxx, maxy, z1, maxx, miny, z1, mask, local_index);
            }
            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal segment-polygon box vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal segment-polygon primitive mask buffer creation failed");
                return 8;
            }
            MPSTriangleAccelerationStructure* accel = [[MPSTriangleAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSTriangleAccelerationStructure initialization failed for segment-polygon");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.triangleCount = primitive_masks.size();
            [accel rebuild];
            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
                }
                [intersector encodeIntersectionToCommandBuffer:command_buffer
                                              intersectionType:MPSIntersectionTypeNearest
                                                     rayBuffer:ray_buffer
                                               rayBufferOffset:0
                                            intersectionBuffer:intersection_buffer
                                      intersectionBufferOffset:0
                                                      rayCount:segment_count
                                         accelerationStructure:accel];
                [command_buffer commit];
                [command_buffer waitUntilCompleted];
                NSError* error = [command_buffer error];
                if (error != nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* hits = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t segment_index = 0; segment_index < segment_count; ++segment_index) {
                    const float distance = hits[segment_index].distance;
                    const uint32_t primitive_index = hits[segment_index].primitiveIndex;
                    if (distance >= 0.0f && distance <= 1.000001f && primitive_index < primitive_polygon_offsets.size()) {
                        const size_t local_index = primitive_polygon_offsets[primitive_index];
                        const uint32_t bit = 1u << local_index;
                        if ((gpu_rays[segment_index].mask & bit) != 0u) {
                            const RtdlPolygonBounds2D& bounds = polygons[chunk_begin + local_index];
                            candidates_by_segment[segment_index].push_back({
                                chunk_begin + local_index,
                                RtdlSegmentPolygonCandidateRow{segments[segment_index].id, bounds.id},
                            });
                            gpu_rays[segment_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[segment_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        std::vector<RtdlSegmentPolygonCandidateRow> rows;
        for (auto& segment_rows : candidates_by_segment) {
            std::sort(segment_rows.begin(), segment_rows.end(), [](const auto& a, const auto& b) {
                return a.first < b.first;
            });
            for (const auto& item : segment_rows) {
                rows.push_back(item.second);
            }
        }
        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlSegmentPolygonCandidateRow*>(std::malloc(rows.size() * sizeof(RtdlSegmentPolygonCandidateRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT segment-polygon candidate rows");
            return 12;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlSegmentPolygonCandidateRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_lsi(
    const RtdlSegment* left_segments,
    size_t left_count,
    const RtdlSegment* right_segments,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_lsi");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if ((left_count > 0 && left_segments == nullptr) || (right_count > 0 && right_segments == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_lsi");
        return 1;
    }
    if (left_count == 0 || right_count == 0) {
        return 0;
    }

    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        id<MTLCommandQueue> command_queue = [device newCommandQueue];
        if (command_queue == nil) {
            set_message(error_out, error_size, "Metal command queue creation failed");
            return 3;
        }

        std::vector<MPSRayOriginMaskDirectionMaxDistance> rays(left_count);
        for (size_t i = 0; i < left_count; ++i) {
            const RtdlSegment& seg = left_segments[i];
            if (!valid_segment_ray(seg)) {
                rays[i].origin = MPSPackedFloat3(INFINITY, INFINITY, INFINITY);
                rays[i].mask = 0;
                rays[i].direction = MPSPackedFloat3(0.0f, 0.0f, 0.0f);
                rays[i].maxDistance = -1.0f;
                continue;
            }
            rays[i].origin = MPSPackedFloat3(static_cast<float>(seg.x0), static_cast<float>(seg.y0), 0.0f);
            rays[i].mask = 0xFFFFFFFFu;
            rays[i].direction = MPSPackedFloat3(static_cast<float>(seg.x1 - seg.x0), static_cast<float>(seg.y1 - seg.y0), 0.0f);
            // Keep RT traversal inclusive of segment endpoints; analytic refinement below enforces exact RTDL bounds.
            rays[i].maxDistance = 1.000001f;
        }

        id<MTLBuffer> ray_buffer = [device newBufferWithBytes:rays.data()
                                                       length:rays.size() * sizeof(MPSRayOriginMaskDirectionMaxDistance)
                                                      options:MTLResourceStorageModeShared];
        if (ray_buffer == nil) {
            set_message(error_out, error_size, "Metal ray buffer creation failed");
            return 4;
        }

        id<MTLBuffer> intersection_buffer = [device newBufferWithLength:left_count * sizeof(MPSIntersectionDistancePrimitiveIndex)
                                                                 options:MTLResourceStorageModeShared];
        if (intersection_buffer == nil) {
            set_message(error_out, error_size, "Metal intersection buffer creation failed");
            return 5;
        }

        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 6;
        }
        intersector.cullMode = MTLCullModeNone;
        intersector.rayDataType = MPSRayDataTypeOriginMaskDirectionMaxDistance;
        intersector.rayMaskOptions = MPSRayMaskOptionPrimitive;
        intersector.rayMaskOperator = MPSRayMaskOperatorAnd;
        intersector.intersectionDataType = MPSIntersectionDataTypeDistancePrimitiveIndex;
        intersector.rayStride = sizeof(MPSRayOriginMaskDirectionMaxDistance);
        intersector.intersectionStride = sizeof(MPSIntersectionDistancePrimitiveIndex);

        std::vector<std::vector<std::pair<size_t, RtdlLsiRow>>> rows_by_left(left_count);
        constexpr float z_extent = 1.0f;
        constexpr size_t chunk_size = 32;
        for (size_t chunk_begin = 0; chunk_begin < right_count; chunk_begin += chunk_size) {
            std::vector<size_t> right_indices;
            right_indices.reserve(chunk_size);
            for (size_t offset = 0; offset < chunk_size && chunk_begin + offset < right_count; ++offset) {
                const size_t right_index = chunk_begin + offset;
                if (valid_segment_ray(right_segments[right_index])) {
                    right_indices.push_back(right_index);
                }
            }
            const size_t chunk_count = right_indices.size();
            if (chunk_count == 0) {
                continue;
            }
            const uint32_t full_chunk_mask = chunk_count == 32 ? 0xFFFFFFFFu : ((1u << chunk_count) - 1u);

            auto* gpu_rays = static_cast<MPSRayOriginMaskDirectionMaxDistance*>([ray_buffer contents]);
            for (size_t left_index = 0; left_index < left_count; ++left_index) {
                gpu_rays[left_index].mask = valid_segment_ray(left_segments[left_index]) ? full_chunk_mask : 0u;
            }

            std::vector<MPSPackedFloat3> vertices;
            vertices.reserve(chunk_count * 4);
            std::vector<uint32_t> primitive_masks;
            primitive_masks.reserve(chunk_count);
            for (size_t local_index = 0; local_index < chunk_count; ++local_index) {
                const RtdlSegment& right = right_segments[right_indices[local_index]];
                vertices.emplace_back(static_cast<float>(right.x0), static_cast<float>(right.y0), -z_extent);
                vertices.emplace_back(static_cast<float>(right.x1), static_cast<float>(right.y1), -z_extent);
                vertices.emplace_back(static_cast<float>(right.x1), static_cast<float>(right.y1), z_extent);
                vertices.emplace_back(static_cast<float>(right.x0), static_cast<float>(right.y0), z_extent);
                primitive_masks.push_back(1u << local_index);
            }
            id<MTLBuffer> vertex_buffer = [device newBufferWithBytes:vertices.data()
                                                              length:vertices.size() * sizeof(MPSPackedFloat3)
                                                             options:MTLResourceStorageModeShared];
            if (vertex_buffer == nil) {
                set_message(error_out, error_size, "Metal quad vertex buffer creation failed");
                return 7;
            }
            id<MTLBuffer> mask_buffer = [device newBufferWithBytes:primitive_masks.data()
                                                            length:primitive_masks.size() * sizeof(uint32_t)
                                                           options:MTLResourceStorageModeShared];
            if (mask_buffer == nil) {
                [vertex_buffer release];
                set_message(error_out, error_size, "Metal primitive mask buffer creation failed");
                return 8;
            }

            MPSQuadrilateralAccelerationStructure* accel = [[MPSQuadrilateralAccelerationStructure alloc] initWithDevice:device];
            if (accel == nil) {
                [mask_buffer release];
                [vertex_buffer release];
                set_message(error_out, error_size, "MPSQuadrilateralAccelerationStructure initialization failed");
                return 9;
            }
            accel.vertexBuffer = vertex_buffer;
            accel.vertexStride = sizeof(MPSPackedFloat3);
            accel.maskBuffer = mask_buffer;
            accel.quadrilateralCount = chunk_count;
            [accel rebuild];

            for (size_t pass = 0; pass < chunk_count; ++pass) {
                id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
                if (command_buffer == nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, "Metal command buffer creation failed");
                    return 10;
                }
                [intersector encodeIntersectionToCommandBuffer:command_buffer
                                              intersectionType:MPSIntersectionTypeNearest
                                                     rayBuffer:ray_buffer
                                               rayBufferOffset:0
                                            intersectionBuffer:intersection_buffer
                                      intersectionBufferOffset:0
                                                      rayCount:left_count
                                         accelerationStructure:accel];
                [command_buffer commit];
                [command_buffer waitUntilCompleted];
                NSError* error = [command_buffer error];
                if (error != nil) {
                    [accel release];
                    [mask_buffer release];
                    [vertex_buffer release];
                    set_message(error_out, error_size, [[error localizedDescription] UTF8String]);
                    return 11;
                }
                const auto* hits = static_cast<const MPSIntersectionDistancePrimitiveIndex*>([intersection_buffer contents]);
                size_t active_hits = 0;
                size_t active_masks = 0;
                for (size_t left_index = 0; left_index < left_count; ++left_index) {
                    const float distance = hits[left_index].distance;
                    const uint32_t primitive_index = hits[left_index].primitiveIndex;
                    if (distance >= 0.0f && distance <= 1.000001f && primitive_index < chunk_count) {
                        const uint32_t bit = 1u << primitive_index;
                        if ((gpu_rays[left_index].mask & bit) != 0u) {
                            const size_t right_index = right_indices[primitive_index];
                            const RtdlSegment& left = left_segments[left_index];
                            const RtdlSegment& right = right_segments[right_index];
                            double ix = 0.0;
                            double iy = 0.0;
                            if (segment_intersection_point(left, right, &ix, &iy)) {
                                rows_by_left[left_index].push_back({right_index, RtdlLsiRow{left.id, right.id, ix, iy}});
                            }
                            gpu_rays[left_index].mask &= ~bit;
                            active_hits += 1;
                        }
                    }
                    if (gpu_rays[left_index].mask != 0u) {
                        active_masks += 1;
                    }
                }
                if (active_hits == 0 || active_masks == 0) {
                    break;
                }
            }
            [accel release];
            [mask_buffer release];
            [vertex_buffer release];
        }

        std::vector<RtdlLsiRow> rows;
        rows.reserve(std::min(left_count * right_count, static_cast<size_t>(1024)));
        for (auto& left_rows : rows_by_left) {
            std::sort(left_rows.begin(), left_rows.end(), [](const auto& a, const auto& b) {
                return a.first < b.first;
            });
            for (const auto& item : left_rows) {
                rows.push_back(item.second);
            }
        }

        if (rows.empty()) {
            return 0;
        }
        auto* out = static_cast<RtdlLsiRow*>(std::malloc(rows.size() * sizeof(RtdlLsiRow)));
        if (out == nullptr) {
            set_message(error_out, error_size, "out of memory allocating Apple RT segment-intersection rows");
            return 12;
        }
        std::memcpy(out, rows.data(), rows.size() * sizeof(RtdlLsiRow));
        *rows_out = out;
        *row_count_out = rows.size();
        return 0;
    }
}
