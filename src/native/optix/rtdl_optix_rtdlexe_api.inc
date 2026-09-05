// App-free runtime warmup for public V4 lifecycle overlap. The native
// singleton remains the sole owner of OptiX context construction.
extern "C" int rtdl_optix_v4_warm_runtime_v1(
        char* error_out, size_t error_size) {
    return handle_native_call([&]() {
        ScopedRtdlCudaContext context_guard;
    }, error_out, error_size);
}

extern "C" uint64_t rtdl_optix_v4_runtime_compiler_attempt_count_v1() {
    return g_rtdlexe_runtime_compiler_attempt_count.load(
        std::memory_order_relaxed);
}

// Static producer schema query. This does not initialize CUDA or OptiX.
extern "C" int rtdl_optix_v4_rtdlexe_producer_descriptor_v1(
        const char* family,
        char* descriptor_out,
        size_t descriptor_capacity,
        size_t* descriptor_bytes_out,
        char* error_out,
        size_t error_size) {
    return handle_native_call([&]() {
        if (!family || !descriptor_out || descriptor_capacity == 0u ||
                !descriptor_bytes_out)
            throw std::runtime_error(
                "V4 .rtdlexe producer descriptor outputs are invalid");
        const std::string descriptor =
            v4_rtdlexe_native_producer_descriptor(std::string(family));
        if (descriptor.size() + 1u > descriptor_capacity)
            throw std::runtime_error(
                "V4 .rtdlexe producer descriptor buffer is too small");
        std::memcpy(descriptor_out, descriptor.data(), descriptor.size());
        descriptor_out[descriptor.size()] = '\0';
        *descriptor_bytes_out = descriptor.size();
    }, error_out, error_size);
}
