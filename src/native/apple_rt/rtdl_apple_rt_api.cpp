extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_get_version(int* major, int* minor, int* patch) {
    if (major == nullptr || minor == nullptr || patch == nullptr) {
        return 1;
    }
    *major = 0;
    *minor = 9;
    *patch = 3;
    return 0;
}

extern "C" RTDL_APPLE_RT_EXPORT void rtdl_apple_rt_free_rows(void* ptr) {
    std::free(ptr);
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_context_probe(char* error_out, size_t error_size) {
    @autoreleasepool {
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        if (device == nil) {
            set_message(error_out, error_size, "Metal default device is unavailable");
            return 2;
        }
        MPSRayIntersector* intersector = [[MPSRayIntersector alloc] initWithDevice:device];
        if (intersector == nil) {
            set_message(error_out, error_size, "MPSRayIntersector initialization failed");
            return 3;
        }
        set_message(error_out, error_size, [[device name] UTF8String]);
        return 0;
    }
}

extern "C" RTDL_APPLE_RT_EXPORT int rtdl_apple_rt_run_u32_add_compute(
    const uint32_t* left,
    const uint32_t* right,
    size_t value_count,
    uint32_t** values_out,
    size_t* value_count_out,
    char* error_out,
    size_t error_size) {
    if (values_out == nullptr || value_count_out == nullptr) {
        set_message(error_out, error_size, "null output passed to rtdl_apple_rt_run_u32_add_compute");
        return 1;
    }
    *values_out = nullptr;
    *value_count_out = 0;
    if (value_count == 0) {
        return 0;
    }
    if (left == nullptr || right == nullptr) {
        set_message(error_out, error_size, "null input passed to rtdl_apple_rt_run_u32_add_compute");
        return 1;
    }
    if (value_count > std::numeric_limits<size_t>::max() / sizeof(uint32_t)) {
        set_message(error_out, error_size, "Apple RT compute input is too large");
        return 1;
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
             "kernel void rtdl_u32_add(device const uint* left [[buffer(0)]],\n"
             "                         device const uint* right [[buffer(1)]],\n"
             "                         device uint* out [[buffer(2)]],\n"
             "                         uint id [[thread_position_in_grid]]) {\n"
             "    out[id] = left[id] + right[id];\n"
             "}\n";
        NSError* compile_error = nil;
        id<MTLLibrary> library = [device newLibraryWithSource:source options:nil error:&compile_error];
        if (library == nil) {
            std::string message = "Metal compute library compilation failed";
            if (compile_error != nil) {
                message += ": ";
                message += [[compile_error localizedDescription] UTF8String];
            }
            [command_queue release];
            set_message(error_out, error_size, message);
            return 4;
        }
        id<MTLFunction> function = [library newFunctionWithName:@"rtdl_u32_add"];
        if (function == nil) {
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal compute function rtdl_u32_add not found");
            return 4;
        }
        NSError* pipeline_error = nil;
        id<MTLComputePipelineState> pipeline = [device newComputePipelineStateWithFunction:function error:&pipeline_error];
        if (pipeline == nil) {
            std::string message = "Metal compute pipeline creation failed";
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

        const size_t byte_count = value_count * sizeof(uint32_t);
        id<MTLBuffer> left_buffer = [device newBufferWithBytes:left length:byte_count options:MTLResourceStorageModeShared];
        id<MTLBuffer> right_buffer = [device newBufferWithBytes:right length:byte_count options:MTLResourceStorageModeShared];
        id<MTLBuffer> out_buffer = [device newBufferWithLength:byte_count options:MTLResourceStorageModeShared];
        if (left_buffer == nil || right_buffer == nil || out_buffer == nil) {
            [out_buffer release];
            [right_buffer release];
            [left_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal compute buffer allocation failed");
            return 5;
        }

        id<MTLCommandBuffer> command_buffer = [command_queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [command_buffer computeCommandEncoder];
        if (command_buffer == nil || encoder == nil) {
            [out_buffer release];
            [right_buffer release];
            [left_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "Metal compute command encoding failed");
            return 3;
        }
        [encoder setComputePipelineState:pipeline];
        [encoder setBuffer:left_buffer offset:0 atIndex:0];
        [encoder setBuffer:right_buffer offset:0 atIndex:1];
        [encoder setBuffer:out_buffer offset:0 atIndex:2];
        const NSUInteger threadgroup_width =
            std::max<NSUInteger>(1, std::min<NSUInteger>(pipeline.maxTotalThreadsPerThreadgroup, value_count));
        [encoder dispatchThreads:MTLSizeMake(value_count, 1, 1)
            threadsPerThreadgroup:MTLSizeMake(threadgroup_width, 1, 1)];
        [encoder endEncoding];
        [command_buffer commit];
        [command_buffer waitUntilCompleted];
        if ([command_buffer error] != nil) {
            std::string message = "Metal compute command buffer failed: ";
            message += [[[command_buffer error] localizedDescription] UTF8String];
            [out_buffer release];
            [right_buffer release];
            [left_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, message);
            return 6;
        }

        auto* out = static_cast<uint32_t*>(std::malloc(byte_count));
        if (out == nullptr) {
            [out_buffer release];
            [right_buffer release];
            [left_buffer release];
            [pipeline release];
            [function release];
            [library release];
            [command_queue release];
            set_message(error_out, error_size, "out of memory allocating Apple RT compute rows");
            return 7;
        }
        std::memcpy(out, [out_buffer contents], byte_count);
        *values_out = out;
        *value_count_out = value_count;

        [out_buffer release];
        [right_buffer release];
        [left_buffer release];
        [pipeline release];
        [function release];
        [library release];
        [command_queue release];
        return 0;
    }
}

