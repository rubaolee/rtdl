extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute(
    const uint32_t* row_ids,
    const float* row_values,
    size_t row_count,
    size_t field_count,
    const RtdlAppleDbNumericClause* clauses,
    size_t clause_count,
    uint32_t** row_ids_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (row_ids_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute");
        return 1;
    }
    *row_ids_out = nullptr;
    *row_count_out = 0;
    if (row_count == 0) {
        return 0;
    }
    if (row_ids == nullptr || row_values == nullptr || (clause_count > 0 && clauses == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_db_conjunctive_scan_numeric_compute");
        return 1;
    }
    if (field_count == 0) {
        set_message(error_out, error_size, "Apple RT DB scan requires at least one field");
        return 1;
    }
    if (row_count > std::numeric_limits<size_t>::max() / field_count ||
        row_count * field_count > std::numeric_limits<size_t>::max() / sizeof(float) ||
        row_count > std::numeric_limits<size_t>::max() / sizeof(uint32_t) ||
        clause_count > std::numeric_limits<size_t>::max() / sizeof(RtdlAppleDbNumericClause)) {
        set_message(error_out, error_size, "Apple RT DB scan input is too large");
        return 1;
    }
    for (size_t index = 0; index < clause_count; ++index) {
        if (clauses[index].field_index >= field_count) {
            set_message(error_out, error_size, "Apple RT DB scan clause field index is out of range");
            return 1;
        }
        if (clauses[index].op < 1 || clauses[index].op > 6) {
            set_message(error_out, error_size, "Apple RT DB scan clause operator is unsupported");
            return 1;
        }
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

        NSString* source =
            @"#include <metal_stdlib>\n"
             "using namespace metal;\n"
             "struct RtdlAppleDbNumericClause {\n"
             "    uint field_index;\n"
             "    uint op;\n"
             "    float value;\n"
             "    float value_hi;\n"
             "};\n"
             "static bool rtdl_db_match(float lhs, RtdlAppleDbNumericClause clause) {\n"
             "    if (clause.op == 1u) { return lhs == clause.value; }\n"
             "    if (clause.op == 2u) { return lhs < clause.value; }\n"
             "    if (clause.op == 3u) { return lhs <= clause.value; }\n"
             "    if (clause.op == 4u) { return lhs > clause.value; }\n"
             "    if (clause.op == 5u) { return lhs >= clause.value; }\n"
             "    return lhs >= clause.value && lhs <= clause.value_hi;\n"
             "}\n"
             "kernel void rtdl_db_conjunctive_scan(device const uint* row_ids [[buffer(0)]],\n"
             "                                      device const float* row_values [[buffer(1)]],\n"
             "                                      constant uint& field_count [[buffer(2)]],\n"
             "                                      device const RtdlAppleDbNumericClause* clauses [[buffer(3)]],\n"
             "                                      constant uint& clause_count [[buffer(4)]],\n"
             "                                      device uint* out [[buffer(5)]],\n"
             "                                      uint id [[thread_position_in_grid]]) {\n"
             "    bool matched = true;\n"
             "    for (uint i = 0; i < clause_count; ++i) {\n"
             "        RtdlAppleDbNumericClause clause = clauses[i];\n"
             "        float lhs = row_values[id * field_count + clause.field_index];\n"
             "        if (!rtdl_db_match(lhs, clause)) { matched = false; break; }\n"
             "    }\n"
             "    out[id] = matched ? 1u : 0u;\n"
             "}\n";
        NSError* compile_error = nil;
        id<MTLLibrary> library = [device newLibraryWithSource:source options:nil error:&compile_error];
        if (library == nil) {
            std::string message = "Metal DB scan library compilation failed";
            if (compile_error != nil) {
                message += ": ";
                message += [[compile_error localizedDescription] UTF8String];
            }
            [command_queue release];
            set_message(error_out, error_size, message);
            return 4;
        }
        id<MTLFunction> function = [library newFunctionWithName:@"rtdl_db_conjunctive_scan"];
        if (function == nil) {
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal DB scan function not found");
            return 4;
        }
        NSError* pipeline_error = nil;
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:function error:&pipeline_error];
        if (pipeline == nil) {
            std::string message = "Metal DB scan pipeline creation failed";
            if (pipeline_error != nil) {
                message += ": ";
                message += [[pipeline_error localizedDescription] UTF8String];
            }
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, message);
            return 4;
        }

        const size_t row_id_bytes = row_count * sizeof(uint32_t);
        const size_t value_bytes = row_count * field_count * sizeof(float);
        const size_t clause_bytes = std::max<size_t>(1, clause_count) * sizeof(RtdlAppleDbNumericClause);
        uint32_t field_count_u32 = static_cast<uint32_t>(field_count);
        uint32_t clause_count_u32 = static_cast<uint32_t>(clause_count);
        if (field_count > std::numeric_limits<uint32_t>::max() ||
            clause_count > std::numeric_limits<uint32_t>::max()) {
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Apple RT DB scan field/clause count exceeds uint32");
            return 1;
        }
        RtdlAppleDbNumericClause empty_clause{};
        id<MTLBuffer> row_id_buffer = [device newBufferWithBytes:row_ids length:row_id_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> value_buffer = [device newBufferWithBytes:row_values length:value_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> field_count_buffer = [device newBufferWithBytes:&field_count_u32 length:sizeof(uint32_t) options:MTLResourceStorageModeShared];
        id<MTLBuffer> clause_buffer = [device newBufferWithBytes:(clause_count == 0 ? &empty_clause : clauses)
                                                          length:clause_bytes
                                                         options:MTLResourceStorageModeShared];
        id<MTLBuffer> clause_count_buffer = [device newBufferWithBytes:&clause_count_u32 length:sizeof(uint32_t) options:MTLResourceStorageModeShared];
        id<MTLBuffer> out_buffer = [device newBufferWithLength:row_id_bytes options:MTLResourceStorageModeShared];
        if (row_id_buffer == nil || value_buffer == nil || field_count_buffer == nil ||
            clause_buffer == nil || clause_count_buffer == nil || out_buffer == nil) {
            [out_buffer release];
            [clause_count_buffer release];
            [clause_buffer release];
            [field_count_buffer release];
            [value_buffer release];
            [row_id_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal DB scan buffer allocation failed");
            return 5;
        }

        id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [command_buffer computeCommandEncoder];
        if (command_buffer == nil || encoder == nil) {
            [out_buffer release];
            [clause_count_buffer release];
            [clause_buffer release];
            [field_count_buffer release];
            [value_buffer release];
            [row_id_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal DB scan command encoding failed");
            return 3;
        }
        [encoder setComputePipelineState:pipeline];
        [encoder setBuffer:row_id_buffer offset:0 atIndex:0];
        [encoder setBuffer:value_buffer offset:0 atIndex:1];
        [encoder setBuffer:field_count_buffer offset:0 atIndex:2];
        [encoder setBuffer:clause_buffer offset:0 atIndex:3];
        [encoder setBuffer:clause_count_buffer offset:0 atIndex:4];
        [encoder setBuffer:out_buffer offset:0 atIndex:5];
        const NSUInteger threadgroup_width =
            std::max<NSUInteger>(1, std::min<NSUInteger>(pipeline.maxTotalThreadsPerThreadgroup, row_count));
        [encoder dispatchThreads:MTLSizeMake(row_count, 1, 1)
            threadsPerThreadgroup:MTLSizeMake(threadgroup_width, 1, 1)];
        [encoder endEncoding];
        [command_buffer commit];
        [command_buffer waitUntilCompleted];
        if ([command_buffer error] != nil) {
            std::string message = "Metal DB scan command buffer failed: ";
            message += [[[command_buffer error] localizedDescription] UTF8String];
            [out_buffer release];
            [clause_count_buffer release];
            [clause_buffer release];
            [field_count_buffer release];
            [value_buffer release];
            [row_id_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, message);
            return 6;
        }

        const auto* all_results = static_cast<const uint32_t*>([out_buffer contents]);
        size_t matched_count = 0;
        for (size_t index = 0; index < row_count; ++index) {
            if (all_results[index] != 0) {
                ++matched_count;
            }
        }
        if (matched_count > 0) {
            auto* out = static_cast<uint32_t*>(std::malloc(matched_count * sizeof(uint32_t)));
            if (out == nullptr) {
                [out_buffer release];
                [clause_count_buffer release];
                [clause_buffer release];
                [field_count_buffer release];
                [value_buffer release];
                [row_id_buffer release];
                [pipeline release];
                [function release];
                [library release];
                [command_queue release];
                set_message(error_out, error_size, "out of memory allocating Apple RT DB scan rows");
                return 7;
            }
            size_t out_index = 0;
            for (size_t index = 0; index < row_count; ++index) {
                if (all_results[index] != 0) {
                    out[out_index++] = row_ids[index];
                }
            }
            *row_ids_out = out;
            *row_count_out = matched_count;
        }

        [out_buffer release];
        [clause_count_buffer release];
        [clause_buffer release];
        [field_count_buffer release];
        [value_buffer release];
        [row_id_buffer release];
        [pipeline release];
        [function release];
        [library release];
        [command_queue release];
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_bfs_discover_compute(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    const RtdlAppleFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* frontier_edge_offsets,
    size_t output_capacity,
    const uint32_t* visited,
    size_t visited_count,
    RtdlAppleBfsRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_bfs_discover_compute");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (frontier_count == 0 || output_capacity == 0) {
        return 0;
    }
    if (row_offsets == nullptr || column_indices == nullptr || frontier == nullptr ||
        frontier_edge_offsets == nullptr || (visited_count > 0 && visited == nullptr)) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_bfs_discover_compute");
        return 1;
    }
    if (row_offset_count < 2) {
        set_message(error_out, error_size, "Apple RT BFS requires at least one graph vertex");
        return 1;
    }
    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    if (row_offset_count - 1 > std::numeric_limits<uint32_t>::max() ||
        frontier_count > std::numeric_limits<uint32_t>::max() ||
        visited_count > std::numeric_limits<uint32_t>::max() ||
        output_capacity > std::numeric_limits<uint32_t>::max()) {
        set_message(error_out, error_size, "Apple RT BFS currently supports at most uint32-sized inputs");
        return 1;
    }
    if (row_offsets[0] != 0 || row_offsets[row_offset_count - 1] != edge_count) {
        set_message(error_out, error_size, "Apple RT BFS row_offsets do not match edge count");
        return 1;
    }
    for (size_t i = 1; i < row_offset_count; ++i) {
        if (row_offsets[i] < row_offsets[i - 1] || row_offsets[i] > edge_count) {
            set_message(error_out, error_size, "Apple RT BFS row_offsets must be non-decreasing and in range");
            return 1;
        }
    }
    for (size_t i = 0; i < edge_count; ++i) {
        if (column_indices[i] >= vertex_count) {
            set_message(error_out, error_size, "Apple RT BFS column index is out of range");
            return 1;
        }
    }
    for (size_t i = 0; i < frontier_count; ++i) {
        if (frontier[i].vertex_id >= vertex_count) {
            set_message(error_out, error_size, "Apple RT BFS frontier vertex is out of range");
            return 1;
        }
    }
    for (size_t i = 0; i < visited_count; ++i) {
        if (visited[i] >= vertex_count) {
            set_message(error_out, error_size, "Apple RT BFS visited vertex is out of range");
            return 1;
        }
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
        NSString* source =
            @"#include <metal_stdlib>\n"
             "using namespace metal;\n"
             "struct FrontierVertex { uint vertex_id; uint level; };\n"
             "struct BfsRow { uint src_vertex; uint dst_vertex; uint level; };\n"
             "kernel void rtdl_bfs_discover(device const uint* row_offsets [[buffer(0)]],\n"
             "                              device const uint* column_indices [[buffer(1)]],\n"
             "                              device const FrontierVertex* frontier [[buffer(2)]],\n"
             "                              device const uint* frontier_edge_offsets [[buffer(3)]],\n"
             "                              device const uint* visited [[buffer(4)]],\n"
             "                              constant uint& visited_count [[buffer(5)]],\n"
             "                              device BfsRow* out [[buffer(6)]],\n"
             "                              uint id [[thread_position_in_grid]]) {\n"
             "    FrontierVertex item = frontier[id];\n"
             "    uint start = row_offsets[item.vertex_id];\n"
             "    uint end = row_offsets[item.vertex_id + 1u];\n"
             "    uint out_base = frontier_edge_offsets[id];\n"
             "    for (uint edge = start; edge < end; ++edge) {\n"
             "        uint dst = column_indices[edge];\n"
             "        bool is_visited = false;\n"
             "        for (uint v = 0; v < visited_count; ++v) {\n"
             "            if (visited[v] == dst) { is_visited = true; break; }\n"
             "        }\n"
             "        uint out_index = out_base + (edge - start);\n"
             "        out[out_index].src_vertex = item.vertex_id;\n"
             "        out[out_index].dst_vertex = is_visited ? 0xffffffffu : dst;\n"
             "        out[out_index].level = item.level + 1u;\n"
             "    }\n"
             "}\n";
        NSError* compile_error = nil;
        id<MTLLibrary> library = [device newLibraryWithSource:source options:nil error:&compile_error];
        if (library == nil) {
            std::string message = "Metal BFS library compilation failed";
            if (compile_error != nil) {
                message += ": ";
                message += [[compile_error localizedDescription] UTF8String];
            }
            [command_queue release];
            set_message(error_out, error_size, message);
            return 4;
        }
        id<MTLFunction> function = [library newFunctionWithName:@"rtdl_bfs_discover"];
        if (function == nil) {
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal BFS function not found");
            return 4;
        }
        NSError* pipeline_error = nil;
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:function error:&pipeline_error];
        if (pipeline == nil) {
            std::string message = "Metal BFS pipeline creation failed";
            if (pipeline_error != nil) {
                message += ": ";
                message += [[pipeline_error localizedDescription] UTF8String];
            }
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, message);
            return 4;
        }

        uint32_t visited_count_u32 = static_cast<uint32_t>(visited_count);
        uint32_t empty_visited = 0;
        const size_t row_offset_bytes = row_offset_count * sizeof(uint32_t);
        const size_t edge_bytes = std::max<size_t>(1, edge_count) * sizeof(uint32_t);
        const size_t frontier_bytes = frontier_count * sizeof(RtdlAppleFrontierVertex);
        const size_t frontier_offset_bytes = (frontier_count + 1) * sizeof(uint32_t);
        const size_t visited_bytes = std::max<size_t>(1, visited_count) * sizeof(uint32_t);
        const size_t out_bytes = output_capacity * sizeof(RtdlAppleBfsRow);
        id<MTLBuffer> row_offsets_buffer = [device newBufferWithBytes:row_offsets length:row_offset_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> column_indices_buffer = [device newBufferWithBytes:(edge_count == 0 ? &empty_visited : column_indices) length:edge_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> frontier_buffer = [device newBufferWithBytes:frontier length:frontier_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> frontier_offsets_buffer = [device newBufferWithBytes:frontier_edge_offsets length:frontier_offset_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> visited_buffer = [device newBufferWithBytes:(visited_count == 0 ? &empty_visited : visited) length:visited_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> visited_count_buffer = [device newBufferWithBytes:&visited_count_u32 length:sizeof(uint32_t) options:MTLResourceStorageModeShared];
        id<MTLBuffer> out_buffer = [device newBufferWithLength:out_bytes options:MTLResourceStorageModeShared];
        if (row_offsets_buffer == nil || column_indices_buffer == nil || frontier_buffer == nil ||
            frontier_offsets_buffer == nil || visited_buffer == nil || visited_count_buffer == nil || out_buffer == nil) {
            [out_buffer release];
            [visited_count_buffer release];
            [visited_buffer release];
            [frontier_offsets_buffer release];
            [frontier_buffer release];
            [column_indices_buffer release];
            [row_offsets_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal BFS buffer allocation failed");
            return 5;
        }
        std::memset([out_buffer contents], 0xff, out_bytes);

        id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [command_buffer computeCommandEncoder];
        if (command_buffer == nil || encoder == nil) {
            [out_buffer release];
            [visited_count_buffer release];
            [visited_buffer release];
            [frontier_offsets_buffer release];
            [frontier_buffer release];
            [column_indices_buffer release];
            [row_offsets_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal BFS command encoding failed");
            return 3;
        }
        [encoder setComputePipelineState:pipeline];
        [encoder setBuffer:row_offsets_buffer offset:0 atIndex:0];
        [encoder setBuffer:column_indices_buffer offset:0 atIndex:1];
        [encoder setBuffer:frontier_buffer offset:0 atIndex:2];
        [encoder setBuffer:frontier_offsets_buffer offset:0 atIndex:3];
        [encoder setBuffer:visited_buffer offset:0 atIndex:4];
        [encoder setBuffer:visited_count_buffer offset:0 atIndex:5];
        [encoder setBuffer:out_buffer offset:0 atIndex:6];
        const NSUInteger threadgroup_width =
            std::max<NSUInteger>(1, std::min<NSUInteger>(pipeline.maxTotalThreadsPerThreadgroup, frontier_count));
        [encoder dispatchThreads:MTLSizeMake(frontier_count, 1, 1)
            threadsPerThreadgroup:MTLSizeMake(threadgroup_width, 1, 1)];
        [encoder endEncoding];
        [command_buffer commit];
        [command_buffer waitUntilCompleted];
        if ([command_buffer error] != nil) {
            std::string message = "Metal BFS command buffer failed: ";
            message += [[[command_buffer error] localizedDescription] UTF8String];
            [out_buffer release];
            [visited_count_buffer release];
            [visited_buffer release];
            [frontier_offsets_buffer release];
            [frontier_buffer release];
            [column_indices_buffer release];
            [row_offsets_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, message);
            return 6;
        }

        const auto* all_rows = static_cast<const RtdlAppleBfsRow*>([out_buffer contents]);
        size_t matched_count = 0;
        for (size_t index = 0; index < output_capacity; ++index) {
            if (all_rows[index].dst_vertex != std::numeric_limits<uint32_t>::max()) {
                ++matched_count;
            }
        }
        if (matched_count > 0) {
            auto* out = static_cast<RtdlAppleBfsRow*>(std::malloc(matched_count * sizeof(RtdlAppleBfsRow)));
            if (out == nullptr) {
                [out_buffer release];
                [visited_count_buffer release];
                [visited_buffer release];
                [frontier_offsets_buffer release];
                [frontier_buffer release];
                [column_indices_buffer release];
                [row_offsets_buffer release];
                [pipeline release];
                [function release];
                [library release];
                [command_queue release];
                set_message(error_out, error_size, "out of memory allocating Apple RT BFS rows");
                return 7;
            }
            size_t out_index = 0;
            for (size_t index = 0; index < output_capacity; ++index) {
                if (all_rows[index].dst_vertex != std::numeric_limits<uint32_t>::max()) {
                    out[out_index++] = all_rows[index];
                }
            }
            *rows_out = out;
            *row_count_out = matched_count;
        }

        [out_buffer release];
        [visited_count_buffer release];
        [visited_buffer release];
        [frontier_offsets_buffer release];
        [frontier_buffer release];
        [column_indices_buffer release];
        [row_offsets_buffer release];
        [pipeline release];
        [function release];
        [library release];
        [command_queue release];
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_triangle_match_compute(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_count,
    const RtdlAppleEdgeSeed* seeds,
    size_t seed_count,
    const uint32_t* seed_output_offsets,
    size_t output_capacity,
    RtdlAppleTriangleRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    if (rows_out == nullptr || row_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_triangle_match_compute");
        return 1;
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (seed_count == 0 || output_capacity == 0) {
        return 0;
    }
    if (row_offsets == nullptr || column_indices == nullptr || seeds == nullptr || seed_output_offsets == nullptr) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_triangle_match_compute");
        return 1;
    }
    if (row_offset_count < 2) {
        set_message(error_out, error_size, "Apple RT triangle_match requires at least one graph vertex");
        return 1;
    }
    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    if (row_offset_count - 1 > std::numeric_limits<uint32_t>::max() ||
        seed_count > std::numeric_limits<uint32_t>::max() ||
        output_capacity > std::numeric_limits<uint32_t>::max()) {
        set_message(error_out, error_size, "Apple RT triangle_match currently supports at most uint32-sized inputs");
        return 1;
    }
    if (row_offsets[0] != 0 || row_offsets[row_offset_count - 1] != edge_count) {
        set_message(error_out, error_size, "Apple RT triangle_match row_offsets do not match edge count");
        return 1;
    }
    for (size_t i = 1; i < row_offset_count; ++i) {
        if (row_offsets[i] < row_offsets[i - 1] || row_offsets[i] > edge_count) {
            set_message(error_out, error_size, "Apple RT triangle_match row_offsets must be non-decreasing and in range");
            return 1;
        }
    }
    for (size_t i = 0; i < edge_count; ++i) {
        if (column_indices[i] >= vertex_count) {
            set_message(error_out, error_size, "Apple RT triangle_match column index is out of range");
            return 1;
        }
    }
    for (size_t i = 0; i < seed_count; ++i) {
        if (seeds[i].u >= vertex_count || seeds[i].v >= vertex_count) {
            set_message(error_out, error_size, "Apple RT triangle_match seed vertex is out of range");
            return 1;
        }
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
        NSString* source =
            @"#include <metal_stdlib>\n"
             "using namespace metal;\n"
             "struct EdgeSeed { uint u; uint v; };\n"
             "struct TriangleRow { uint u; uint v; uint w; };\n"
             "kernel void rtdl_triangle_match(device const uint* row_offsets [[buffer(0)]],\n"
             "                                device const uint* column_indices [[buffer(1)]],\n"
             "                                device const EdgeSeed* seeds [[buffer(2)]],\n"
             "                                device const uint* seed_output_offsets [[buffer(3)]],\n"
             "                                device TriangleRow* out [[buffer(4)]],\n"
             "                                uint id [[thread_position_in_grid]]) {\n"
             "    EdgeSeed seed = seeds[id];\n"
             "    uint u = seed.u;\n"
             "    uint v = seed.v;\n"
             "    uint u_start = row_offsets[u];\n"
             "    uint u_end = row_offsets[u + 1u];\n"
             "    uint v_start = row_offsets[v];\n"
             "    uint v_end = row_offsets[v + 1u];\n"
             "    uint out_base = seed_output_offsets[id];\n"
             "    for (uint edge = u_start; edge < u_end; ++edge) {\n"
             "        uint w = column_indices[edge];\n"
             "        bool matched = false;\n"
             "        if (u < v && v < w) {\n"
             "            for (uint probe = v_start; probe < v_end; ++probe) {\n"
             "                if (column_indices[probe] == w) { matched = true; break; }\n"
             "            }\n"
             "        }\n"
             "        uint out_index = out_base + (edge - u_start);\n"
             "        out[out_index].u = matched ? u : 0xffffffffu;\n"
             "        out[out_index].v = v;\n"
             "        out[out_index].w = w;\n"
             "    }\n"
             "}\n";
        NSError* compile_error = nil;
        id<MTLLibrary> library = [device newLibraryWithSource:source options:nil error:&compile_error];
        if (library == nil) {
            std::string message = "Metal triangle_match library compilation failed";
            if (compile_error != nil) {
                message += ": ";
                message += [[compile_error localizedDescription] UTF8String];
            }
            [command_queue release];
            set_message(error_out, error_size, message);
            return 4;
        }
        id<MTLFunction> function = [library newFunctionWithName:@"rtdl_triangle_match"];
        if (function == nil) {
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal triangle_match function not found");
            return 4;
        }
        NSError* pipeline_error = nil;
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:function error:&pipeline_error];
        if (pipeline == nil) {
            std::string message = "Metal triangle_match pipeline creation failed";
            if (pipeline_error != nil) {
                message += ": ";
                message += [[pipeline_error localizedDescription] UTF8String];
            }
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, message);
            return 4;
        }

        uint32_t empty_value = 0;
        const size_t row_offset_bytes = row_offset_count * sizeof(uint32_t);
        const size_t edge_bytes = std::max<size_t>(1, edge_count) * sizeof(uint32_t);
        const size_t seed_bytes = seed_count * sizeof(RtdlAppleEdgeSeed);
        const size_t seed_offset_bytes = (seed_count + 1) * sizeof(uint32_t);
        const size_t out_bytes = output_capacity * sizeof(RtdlAppleTriangleRow);
        id<MTLBuffer> row_offsets_buffer = [device newBufferWithBytes:row_offsets length:row_offset_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> column_indices_buffer = [device newBufferWithBytes:(edge_count == 0 ? &empty_value : column_indices) length:edge_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> seed_buffer = [device newBufferWithBytes:seeds length:seed_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> seed_offsets_buffer = [device newBufferWithBytes:seed_output_offsets length:seed_offset_bytes options:MTLResourceStorageModeShared];
        id<MTLBuffer> out_buffer = [device newBufferWithLength:out_bytes options:MTLResourceStorageModeShared];
        if (row_offsets_buffer == nil || column_indices_buffer == nil || seed_buffer == nil ||
            seed_offsets_buffer == nil || out_buffer == nil) {
            [out_buffer release];
            [seed_offsets_buffer release];
            [seed_buffer release];
            [column_indices_buffer release];
            [row_offsets_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal triangle_match buffer allocation failed");
            return 5;
        }
        std::memset([out_buffer contents], 0xff, out_bytes);

        id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [command_buffer computeCommandEncoder];
        if (command_buffer == nil || encoder == nil) {
            [out_buffer release];
            [seed_offsets_buffer release];
            [seed_buffer release];
            [column_indices_buffer release];
            [row_offsets_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal triangle_match command encoding failed");
            return 3;
        }
        [encoder setComputePipelineState:pipeline];
        [encoder setBuffer:row_offsets_buffer offset:0 atIndex:0];
        [encoder setBuffer:column_indices_buffer offset:0 atIndex:1];
        [encoder setBuffer:seed_buffer offset:0 atIndex:2];
        [encoder setBuffer:seed_offsets_buffer offset:0 atIndex:3];
        [encoder setBuffer:out_buffer offset:0 atIndex:4];
        const NSUInteger threadgroup_width =
            std::max<NSUInteger>(1, std::min<NSUInteger>(pipeline.maxTotalThreadsPerThreadgroup, seed_count));
        [encoder dispatchThreads:MTLSizeMake(seed_count, 1, 1)
            threadsPerThreadgroup:MTLSizeMake(threadgroup_width, 1, 1)];
        [encoder endEncoding];
        [command_buffer commit];
        [command_buffer waitUntilCompleted];
        if ([command_buffer error] != nil) {
            std::string message = "Metal triangle_match command buffer failed: ";
            message += [[[command_buffer error] localizedDescription] UTF8String];
            [out_buffer release];
            [seed_offsets_buffer release];
            [seed_buffer release];
            [column_indices_buffer release];
            [row_offsets_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, message);
            return 6;
        }

        const auto* all_rows = static_cast<const RtdlAppleTriangleRow*>([out_buffer contents]);
        size_t matched_count = 0;
        for (size_t index = 0; index < output_capacity; ++index) {
            if (all_rows[index].u != std::numeric_limits<uint32_t>::max()) {
                ++matched_count;
            }
        }
        if (matched_count > 0) {
            auto* out = static_cast<RtdlAppleTriangleRow*>(std::malloc(matched_count * sizeof(RtdlAppleTriangleRow)));
            if (out == nullptr) {
                [out_buffer release];
                [seed_offsets_buffer release];
                [seed_buffer release];
                [column_indices_buffer release];
                [row_offsets_buffer release];
                [pipeline release];
                [function release];
                [library release];
                [command_queue release];
                set_message(error_out, error_size, "out of memory allocating Apple RT triangle_match rows");
                return 7;
            }
            size_t out_index = 0;
            for (size_t index = 0; index < output_capacity; ++index) {
                if (all_rows[index].u != std::numeric_limits<uint32_t>::max()) {
                    out[out_index++] = all_rows[index];
                }
            }
            *rows_out = out;
            *row_count_out = matched_count;
        }

        [out_buffer release];
        [seed_offsets_buffer release];
        [seed_buffer release];
        [column_indices_buffer release];
        [row_offsets_buffer release];
        [pipeline release];
        [function release];
        [library release];
        [command_queue release];
        return 0;
    }
}
