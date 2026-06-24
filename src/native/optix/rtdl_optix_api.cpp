extern "C" int rtdl_optix_get_version(int* major_out, int* minor_out, int* patch_out) {
    if (!major_out || !minor_out || !patch_out) return 1;
    *major_out = OPTIX_VERSION / 10000;
    *minor_out = (OPTIX_VERSION % 10000) / 100;
    *patch_out = OPTIX_VERSION % 100;
    return 0;
}

extern "C" int rtdl_optix_collect_k_cooperative_launch_capability(
        int* cooperative_launch_supported_out,
        int* cooperative_multi_device_launch_supported_out,
        int* multiprocessor_count_out,
        int* max_threads_per_block_out,
        int* max_shared_memory_per_block_optin_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!cooperative_launch_supported_out
                || !cooperative_multi_device_launch_supported_out
                || !multiprocessor_count_out
                || !max_threads_per_block_out
                || !max_shared_memory_per_block_optin_out) {
            throw std::runtime_error("capability output pointers must not be null");
        }

        *cooperative_launch_supported_out = 0;
        *cooperative_multi_device_launch_supported_out = 0;
        *multiprocessor_count_out = 0;
        *max_threads_per_block_out = 0;
        *max_shared_memory_per_block_optin_out = 0;

        CU_CHECK(cuInit(0));
        CUdevice device = 0;
        CU_CHECK(cuDeviceGet(&device, 0));
        CU_CHECK(cuDeviceGetAttribute(
            cooperative_launch_supported_out,
            CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH,
            device));
        CU_CHECK(cuDeviceGetAttribute(
            cooperative_multi_device_launch_supported_out,
            CU_DEVICE_ATTRIBUTE_COOPERATIVE_MULTI_DEVICE_LAUNCH,
            device));
        CU_CHECK(cuDeviceGetAttribute(
            multiprocessor_count_out,
            CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT,
            device));
        CU_CHECK(cuDeviceGetAttribute(
            max_threads_per_block_out,
            CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK,
            device));
        CU_CHECK(cuDeviceGetAttribute(
            max_shared_memory_per_block_optin_out,
            CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN,
            device));
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_k_cooperative_launch_smoke(
        int requested_blocks, int requested_threads,
        int* observed_blocks_out,
        int* sync_observed_blocks_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!observed_blocks_out || !sync_observed_blocks_out)
            throw std::runtime_error("smoke output pointers must not be null");
        if (requested_blocks <= 0 || requested_threads <= 0)
            throw std::runtime_error("requested blocks and threads must be positive");
        *observed_blocks_out = 0;
        *sync_observed_blocks_out = 0;

        int cooperative_launch_supported = 0;
        CU_CHECK(cuInit(0));
        CUdevice device = 0;
        CU_CHECK(cuDeviceGet(&device, 0));
        CU_CHECK(cuDeviceGetAttribute(
            &cooperative_launch_supported,
            CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH,
            device));
        if (!cooperative_launch_supported)
            throw std::runtime_error("CUDA device does not support cooperative launch");

        (void)get_optix_context();

        std::call_once(g_collect_k_cooperative_launch_smoke.init, [&]() {
            const std::string cubin = compile_to_cubin(
                kCollectKCooperativeLaunchSmokeKernelSrc,
                "collect_k_cooperative_launch_smoke_kernel.cu");
            CU_CHECK(cuModuleLoadData(&g_collect_k_cooperative_launch_smoke.module, cubin.data()));
            CU_CHECK(cuModuleGetFunction(
                &g_collect_k_cooperative_launch_smoke.fn,
                g_collect_k_cooperative_launch_smoke.module,
                "collect_k_cooperative_launch_smoke"));
        });

        DevPtr observed(sizeof(uint32_t) * 2);
        const uint32_t zeros[2] = {0u, 0u};
        upload(observed.ptr, zeros, 2);
        void* args[] = {&observed.ptr};
        CU_CHECK(cuLaunchCooperativeKernel(
            g_collect_k_cooperative_launch_smoke.fn,
            static_cast<unsigned int>(requested_blocks), 1, 1,
            static_cast<unsigned int>(requested_threads), 1, 1,
            0, nullptr, args));
        CU_CHECK(cuStreamSynchronize(nullptr));

        uint32_t host_observed[2] = {0u, 0u};
        download(host_observed, observed.ptr, 2);
        if (host_observed[0] != static_cast<uint32_t>(requested_blocks)
                || host_observed[1] != static_cast<uint32_t>(requested_blocks)) {
            throw std::runtime_error("cooperative launch smoke returned unexpected block counts");
        }
        *observed_blocks_out = static_cast<int>(host_observed[0]);
        *sync_observed_blocks_out = static_cast<int>(host_observed[1]);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_segment_pair_intersection(
        const RtdlSegment* left,  size_t left_count,
        const RtdlSegment* right, size_t right_count,
        RtdlSegmentPairIntersectionRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (left_count == 0 || right_count == 0) return;
        run_segment_pair_intersection_optix(left, left_count, right, right_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_segment_pair_intersection(
        const RtdlSegment* right, size_t right_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!right && right_count != 0)
            throw std::runtime_error("right pointer must not be null when right_count is nonzero");
        *prepared_out = nullptr;
        *prepared_out = prepare_segment_pair_intersection_optix(right, right_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_segment_pair_left_set(
        const RtdlSegment* left, size_t left_count,
        void** prepared_left_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_left_out)
            throw std::runtime_error("prepared_left_out must not be null");
        if (!left && left_count != 0)
            throw std::runtime_error("left pointer must not be null when left_count is nonzero");
        *prepared_left_out = nullptr;
        *prepared_left_out = new PreparedSegmentPairLeftSet(left, left_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_segment_pair_intersection(
        void* prepared,
        const RtdlSegment* left, size_t left_count,
        RtdlSegmentPairIntersectionRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!left && left_count != 0)
            throw std::runtime_error("left pointer must not be null when left_count is nonzero");
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        run_prepared_segment_pair_intersection_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            left, left_count,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_segment_pair_intersection(
        void* prepared,
        const RtdlSegment* left, size_t left_count,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!left && left_count != 0)
            throw std::runtime_error("left pointer must not be null when left_count is nonzero");
        if (!count_out)
            throw std::runtime_error("count_out must not be null");
        *count_out = 0;
        count_prepared_segment_pair_intersection_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            left, left_count,
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_segment_pair_intersection_prepared_left(
        void* prepared,
        void* prepared_left,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!prepared_left)
            throw std::runtime_error("prepared segment-pair left-set handle must not be null");
        if (!count_out)
            throw std::runtime_error("count_out must not be null");
        *count_out = 0;
        count_prepared_segment_pair_intersection_prepared_left_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            reinterpret_cast<PreparedSegmentPairLeftSet*>(prepared_left),
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_repeated(
        void* prepared,
        void* prepared_left,
        size_t repeat_count,
        size_t* count_out,
        double* total_seconds_out,
        double* min_seconds_out,
        double* max_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!prepared_left)
            throw std::runtime_error("prepared segment-pair left-set handle must not be null");
        count_prepared_segment_pair_intersection_prepared_left_repeated_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            reinterpret_cast<PreparedSegmentPairLeftSet*>(prepared_left),
            repeat_count,
            count_out,
            total_seconds_out,
            min_seconds_out,
            max_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_direct_intersection(
        void* prepared,
        void* prepared_left,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!prepared_left)
            throw std::runtime_error("prepared segment-pair left-set handle must not be null");
        if (!count_out)
            throw std::runtime_error("count_out must not be null");
        *count_out = 0;
        count_prepared_segment_pair_intersection_prepared_left_direct_intersection_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            reinterpret_cast<PreparedSegmentPairLeftSet*>(prepared_left),
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection(
        void* prepared,
        void* prepared_left,
        size_t* count_out,
        size_t* group_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!prepared_left)
            throw std::runtime_error("prepared segment-pair left-set handle must not be null");
        if (!count_out)
            throw std::runtime_error("count_out must not be null");
        if (!group_count_out)
            throw std::runtime_error("group_count_out must not be null");
        *count_out = 0;
        *group_count_out = 0;
        count_prepared_segment_pair_intersection_prepared_left_grouped_range_direct_intersection_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            reinterpret_cast<PreparedSegmentPairLeftSet*>(prepared_left),
            count_out,
            group_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_segment_pair_candidate_device_columns(
        void* prepared,
        const RtdlSegment* left, size_t left_count,
        size_t max_rows,
        RtdlNativeDevicePairColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!left && left_count != 0)
            throw std::runtime_error("left pointer must not be null when left_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("segment-pair candidate device columns_out pointer must not be null");
        run_prepared_segment_pair_candidate_device_columns_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            left, left_count,
            max_rows,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_segment_pair_candidate_device_columns(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_segment_pair_candidate_device_columns_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_segment_pair_left_id_count_device_columns(
        void* prepared,
        const RtdlSegment* left, size_t left_count,
        size_t group_capacity,
        RtdlNativeDeviceGroupedCountI64Columns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!left && left_count != 0)
            throw std::runtime_error("left pointer must not be null when left_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("segment-pair left-id count columns_out pointer must not be null");
        run_prepared_segment_pair_left_id_count_device_columns_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            left,
            left_count,
            group_capacity,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_segment_pair_left_id_count_device_columns_with_ambiguity_status(
        void* prepared,
        const RtdlSegment* left, size_t left_count,
        size_t group_capacity,
        RtdlNativeDeviceGroupedCountI64Columns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!left && left_count != 0)
            throw std::runtime_error("left pointer must not be null when left_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("segment-pair left-id count columns_out pointer must not be null");
        run_prepared_segment_pair_left_id_count_device_columns_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            left,
            left_count,
            group_capacity,
            columns_out,
            true);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_segment_pair_left_id_count_prepared_left_device_columns(
        void* prepared,
        void* prepared_left,
        size_t group_capacity,
        RtdlNativeDeviceGroupedCountI64Columns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment-pair handle must not be null");
        if (!prepared_left)
            throw std::runtime_error("prepared segment-pair left-set handle must not be null");
        if (!columns_out)
            throw std::runtime_error("segment-pair left-id count columns_out pointer must not be null");
        run_prepared_segment_pair_left_id_count_device_columns_prepared_left_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            reinterpret_cast<PreparedSegmentPairLeftSet*>(prepared_left),
            group_capacity,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_segment_first_hit(
        void* prepared,
        const RtdlSegment* probes, size_t probe_count,
        RtdlSegmentFirstHitRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment first-hit handle must not be null");
        if (!probes && probe_count != 0)
            throw std::runtime_error("probe pointer must not be null when probe_count is nonzero");
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        run_prepared_segment_first_hit_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            probes, probe_count,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_segment_first_hit(
        void* prepared,
        const RtdlSegment* probes, size_t probe_count,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared segment first-hit handle must not be null");
        if (!probes && probe_count != 0)
            throw std::runtime_error("probe pointer must not be null when probe_count is nonzero");
        if (!count_out)
            throw std::runtime_error("count_out must not be null");
        *count_out = 0;
        count_prepared_segment_first_hit_optix(
            reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared),
            probes, probe_count,
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_rayjoin_cdb_point_location_2d(
        const RtdlRayjoinCdbSegment* segments,
        size_t segment_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!segments && segment_count != 0)
            throw std::runtime_error("segments pointer must not be null when segment_count is nonzero");
        *prepared_out = nullptr;
        *prepared_out = prepare_rayjoin_cdb_point_location_2d_optix(segments, segment_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_rayjoin_cdb_point_location_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        RtdlRayjoinCdbPointLocationRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared CDB point-location handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("points pointer must not be null when point_count is nonzero");
        if (!rows_out || !row_count_out)
            throw std::runtime_error("row output pointers must not be null");
        run_prepared_rayjoin_cdb_point_location_2d_optix(
            reinterpret_cast<PreparedRayjoinCdbPointLocation2D*>(prepared),
            points,
            point_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_rayjoin_cdb_point_location_points_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        void** prepared_points_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared CDB point-location handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("points pointer must not be null when point_count is nonzero");
        if (!prepared_points_out)
            throw std::runtime_error("prepared_points_out must not be null");
        *prepared_points_out = nullptr;
        *prepared_points_out = prepare_rayjoin_cdb_point_location_points_2d_optix(
            reinterpret_cast<PreparedRayjoinCdbPointLocation2D*>(prepared),
            points,
            point_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_rayjoin_cdb_point_location_2d_device_points(
        void* prepared,
        void* prepared_points,
        size_t* positive_face_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared CDB point-location handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared CDB point-location query points handle must not be null");
        if (!positive_face_count_out)
            throw std::runtime_error("positive_face_count_out must not be null");
        count_prepared_rayjoin_cdb_point_location_2d_device_points_optix(
            reinterpret_cast<PreparedRayjoinCdbPointLocation2D*>(prepared),
            reinterpret_cast<PreparedRayjoinCdbPointLocationPoints2D*>(prepared_points),
            positive_face_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_segment_ids(
        void* prepared,
        void* prepared_points,
        size_t* point_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared CDB point-location handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared CDB point-location query points handle must not be null");
        if (!point_count_out)
            throw std::runtime_error("point_count_out must not be null");
        write_prepared_rayjoin_cdb_point_location_2d_device_segment_ids_optix(
            reinterpret_cast<PreparedRayjoinCdbPointLocation2D*>(prepared),
            reinterpret_cast<PreparedRayjoinCdbPointLocationPoints2D*>(prepared_points),
            point_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_face_ids(
        void* prepared,
        void* prepared_points,
        size_t* point_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared CDB point-location handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared CDB point-location query points handle must not be null");
        if (!point_count_out)
            throw std::runtime_error("point_count_out must not be null");
        write_prepared_rayjoin_cdb_point_location_2d_device_face_ids_optix(
            reinterpret_cast<PreparedRayjoinCdbPointLocation2D*>(prepared),
            reinterpret_cast<PreparedRayjoinCdbPointLocationPoints2D*>(prepared_points),
            point_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_rayjoin_cdb_point_location_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t* positive_face_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared CDB point-location handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("points pointer must not be null when point_count is nonzero");
        if (!positive_face_count_out)
            throw std::runtime_error("positive_face_count_out must not be null");
        count_prepared_rayjoin_cdb_point_location_2d_optix(
            reinterpret_cast<PreparedRayjoinCdbPointLocation2D*>(prepared),
            points,
            point_count,
            positive_face_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_rayjoin_cdb_point_location_2d(void* prepared)
{
    delete reinterpret_cast<PreparedRayjoinCdbPointLocation2D*>(prepared);
}

extern "C" void rtdl_optix_destroy_prepared_rayjoin_cdb_point_location_points_2d(void* prepared_points)
{
    delete reinterpret_cast<PreparedRayjoinCdbPointLocationPoints2D*>(prepared_points);
}

extern "C" int rtdl_optix_prepare_directed_segment_point_location_2d(
        const RtdlDirectedSegmentFace2D* segments,
        size_t segment_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return rtdl_optix_prepare_rayjoin_cdb_point_location_2d(
        reinterpret_cast<const RtdlRayjoinCdbSegment*>(segments),
        segment_count,
        prepared_out,
        error_out,
        error_size);
}

extern "C" int rtdl_optix_run_prepared_directed_segment_point_location_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        RtdlDirectedSegmentPointLocationRow2D** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return rtdl_optix_run_prepared_rayjoin_cdb_point_location_2d(
        prepared,
        points,
        point_count,
        reinterpret_cast<RtdlRayjoinCdbPointLocationRow**>(rows_out),
        row_count_out,
        error_out,
        error_size);
}

extern "C" int rtdl_optix_prepare_directed_segment_point_location_points_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        void** prepared_points_out,
        char* error_out, size_t error_size)
{
    return rtdl_optix_prepare_rayjoin_cdb_point_location_points_2d(
        prepared,
        points,
        point_count,
        prepared_points_out,
        error_out,
        error_size);
}

extern "C" int rtdl_optix_count_prepared_directed_segment_point_location_2d_device_points(
        void* prepared,
        void* prepared_points,
        size_t* positive_face_count_out,
        char* error_out, size_t error_size)
{
    return rtdl_optix_count_prepared_rayjoin_cdb_point_location_2d_device_points(
        prepared,
        prepared_points,
        positive_face_count_out,
        error_out,
        error_size);
}

extern "C" int rtdl_optix_write_prepared_directed_segment_point_location_2d_device_segment_ids(
        void* prepared,
        void* prepared_points,
        size_t* point_count_out,
        char* error_out, size_t error_size)
{
    return rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_segment_ids(
        prepared,
        prepared_points,
        point_count_out,
        error_out,
        error_size);
}

extern "C" int rtdl_optix_write_prepared_directed_segment_point_location_2d_device_face_ids(
        void* prepared,
        void* prepared_points,
        size_t* point_count_out,
        char* error_out, size_t error_size)
{
    return rtdl_optix_write_prepared_rayjoin_cdb_point_location_2d_device_face_ids(
        prepared,
        prepared_points,
        point_count_out,
        error_out,
        error_size);
}

extern "C" int rtdl_optix_count_prepared_directed_segment_point_location_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t* positive_face_count_out,
        char* error_out, size_t error_size)
{
    return rtdl_optix_count_prepared_rayjoin_cdb_point_location_2d(
        prepared,
        points,
        point_count,
        positive_face_count_out,
        error_out,
        error_size);
}

extern "C" void rtdl_optix_destroy_prepared_directed_segment_point_location_2d(void* prepared)
{
    rtdl_optix_destroy_prepared_rayjoin_cdb_point_location_2d(prepared);
}

extern "C" void rtdl_optix_destroy_prepared_directed_segment_point_location_points_2d(void* prepared_points)
{
    rtdl_optix_destroy_prepared_rayjoin_cdb_point_location_points_2d(prepared_points);
}

extern "C" void rtdl_optix_destroy_prepared_segment_pair_intersection(void* prepared)
{
    delete reinterpret_cast<PreparedSegmentPairIntersectionBuild*>(prepared);
}

extern "C" void rtdl_optix_destroy_prepared_segment_pair_left_set(void* prepared_left)
{
    delete reinterpret_cast<PreparedSegmentPairLeftSet*>(prepared_left);
}

extern "C" int rtdl_optix_run_point_primitive_anyhit_packet(
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

extern "C" int rtdl_optix_run_point_closed_shape_membership_2d(
        const RtdlPoint* points,          size_t point_count,
        const RtdlClosedShapeRef* shapes, size_t shape_count,
        const double* vertices_xy,        size_t vertex_xy_count,
        uint32_t positive_only,
        RtdlPointClosedShapeMembershipRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_point_closed_shape_membership_2d_optix(
            points,
            point_count,
            shapes,
            shape_count,
            vertices_xy,
            vertex_xy_count,
            positive_only,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_point_closed_shape_membership_2d(
        const RtdlClosedShapeRef* shapes, size_t shape_count,
        const double* vertices_xy,        size_t vertex_xy_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!shapes && shape_count != 0)
            throw std::runtime_error("shape pointer must not be null when shape_count is nonzero");
        if (!vertices_xy && vertex_xy_count != 0)
            throw std::runtime_error("vertices pointer must not be null when vertex_xy_count is nonzero");
        *prepared_out = nullptr;
        *prepared_out = prepare_point_closed_shape_membership_2d_optix(
            shapes, shape_count, vertices_xy, vertex_xy_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_point_closed_shape_membership_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        uint32_t positive_only,
        RtdlPointClosedShapeMembershipRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        run_prepared_point_closed_shape_membership_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, positive_only, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_point_closed_shape_membership_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!count_out)
            throw std::runtime_error("count output pointer must not be null");
        *count_out = 0;
        count_prepared_point_closed_shape_membership_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_point_closed_shape_membership_prepared_points_2d(
        void* prepared,
        void* prepared_points,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!count_out)
            throw std::runtime_error("exact prepared-points count output pointer must not be null");
        *count_out = 0;
        count_prepared_point_closed_shape_membership_prepared_points_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d(
        void* prepared,
        void* prepared_points,
        size_t max_candidate_rows,
        void** executor_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!executor_out)
            throw std::runtime_error("exact prepared-points scalar-count executor output pointer must not be null");
        *executor_out = nullptr;
        *executor_out = prepare_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            max_candidate_rows);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d(
        void* executor,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!executor)
            throw std::runtime_error("exact prepared-points scalar-count executor handle must not be null");
        if (!count_out)
            throw std::runtime_error("exact prepared-points scalar-count executor count output pointer must not be null");
        *count_out = 0;
        run_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d_optix(
            reinterpret_cast<PreparedPointClosedShapeExactPreparedPointsScalarCountExecutor2D*>(executor),
            count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d(
        void* executor)
{
    delete reinterpret_cast<PreparedPointClosedShapeExactPreparedPointsScalarCountExecutor2D*>(executor);
}

extern "C" int rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!count_out)
            throw std::runtime_error("device-filtered count output pointer must not be null");
        *count_out = 0;
        count_prepared_point_closed_shape_membership_device_filtered_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_point_probe_columns_2d(
        const RtdlPoint* points, size_t point_count,
        void** prepared_points_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_points_out)
            throw std::runtime_error("prepared point-probe columns output pointer must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        *prepared_points_out = prepare_point_probe_columns_2d_optix(points, point_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_prepared_points_2d(
        void* prepared,
        void* prepared_points,
        size_t* count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!count_out)
            throw std::runtime_error("device-filtered prepared-points count output pointer must not be null");
        *count_out = 0;
        count_prepared_point_closed_shape_membership_device_filtered_prepared_points_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_2d(
        void* prepared,
        void* prepared_points,
        size_t request_count,
        size_t* counts_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!counts_out && request_count != 0)
            throw std::runtime_error("device-filtered prepared-points batch count output pointer must not be null");
        count_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            request_count,
            counts_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_point_closed_shape_membership_relation_status_corrected_prepared_points_2d(
        void* prepared,
        void* prepared_points,
        double point_eps,
        RtdlNativeClosedShapeScalarCountSummary* summary_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!summary_out)
            throw std::runtime_error("relation-status corrected scalar-count summary output pointer must not be null");
        count_prepared_point_closed_shape_membership_relation_status_corrected_prepared_points_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            point_eps,
            summary_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d(
        void* prepared,
        void* prepared_points,
        double point_eps,
        void** executor_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!executor_out)
            throw std::runtime_error("relation-status corrected scalar-count executor output pointer must not be null");
        *executor_out = nullptr;
        *executor_out = prepare_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            point_eps);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d(
        void* executor,
        RtdlNativeClosedShapeScalarCountSummary* summary_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!executor)
            throw std::runtime_error("relation-status corrected scalar-count executor handle must not be null");
        if (!summary_out)
            throw std::runtime_error("relation-status corrected scalar-count executor summary output pointer must not be null");
        run_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d_optix(
            reinterpret_cast<PreparedPointClosedShapeRelationStatusCorrectedScalarCountExecutor2D*>(executor),
            summary_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d(
        void* executor)
{
    delete reinterpret_cast<PreparedPointClosedShapeRelationStatusCorrectedScalarCountExecutor2D*>(executor);
}

extern "C" int rtdl_optix_prepare_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d(
        void* prepared,
        void* prepared_points,
        size_t request_count,
        size_t stream_count,
        void** executor_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!executor_out)
            throw std::runtime_error("prepared-points batch executor output pointer must not be null");
        *executor_out = nullptr;
        *executor_out = prepare_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            request_count,
            stream_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d(
        void* executor,
        size_t* counts_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!executor)
            throw std::runtime_error("prepared-points batch executor handle must not be null");
        run_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d_optix(
            reinterpret_cast<PreparedPointClosedShapeMembershipPreparedPointsBatchExecutor2D*>(executor),
            counts_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_executor_2d(
        void* executor)
{
    delete reinterpret_cast<PreparedPointClosedShapeMembershipPreparedPointsBatchExecutor2D*>(executor);
}

extern "C" int rtdl_optix_prepare_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d(
        void* prepared,
        void* prepared_points,
        size_t request_count,
        void** graph_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!graph_out)
            throw std::runtime_error("prepared-points batch graph output pointer must not be null");
        *graph_out = nullptr;
        *graph_out = prepare_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            request_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_replay_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d(
        void* graph,
        size_t* counts_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!graph)
            throw std::runtime_error("prepared-points batch graph handle must not be null");
        replay_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d_optix(
            reinterpret_cast<PreparedPointClosedShapeMembershipPreparedPointsBatchGraph2D*>(graph),
            counts_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d(
        void* graph)
{
    delete reinterpret_cast<PreparedPointClosedShapeMembershipPreparedPointsBatchGraph2D*>(graph);
}

extern "C" int rtdl_optix_run_prepared_point_closed_shape_first_boundary_crossing_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        RtdlPointClosedShapeBoundaryEventRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape boundary-event handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!rows_out || !row_count_out)
            throw std::runtime_error("boundary-event output pointers must not be null");
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_point_closed_shape_first_boundary_crossing_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_point_closed_shape_membership_candidate_device_columns_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t max_rows,
        RtdlNativeDevicePairColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("closed-shape membership candidate device columns_out pointer must not be null");
        run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, max_rows, columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_point_closed_shape_membership_relation_status_candidate_device_columns_prepared_points_2d(
        void* prepared,
        void* prepared_points,
        uint32_t relation_status_filter,
        size_t max_rows,
        RtdlNativeDevicePairColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!prepared_points)
            throw std::runtime_error("prepared point-probe columns handle must not be null");
        if (!columns_out)
            throw std::runtime_error("relation-status candidate device columns_out pointer must not be null");
        run_prepared_point_closed_shape_membership_relation_status_candidate_device_columns_prepared_points_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points),
            relation_status_filter, max_rows, columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t max_rows,
        RtdlNativeDevicePairColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("closed-shape exact membership device columns_out pointer must not be null");
        run_prepared_point_closed_shape_membership_exact_device_columns_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, max_rows, columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_page_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t page_start, size_t page_count,
        size_t max_rows,
        RtdlNativeDevicePairColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("closed-shape exact membership page device columns_out pointer must not be null");
        run_prepared_point_closed_shape_membership_exact_device_columns_page_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, page_start, page_count, max_rows, columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_point_closed_shape_membership_exact_device_columns_page_plan_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t page_size, size_t initial_capacity,
        void** page_plan_out,
        RtdlNativePairColumnPagePlanInfo* info_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!page_plan_out)
            throw std::runtime_error("closed-shape exact membership page_plan_out pointer must not be null");
        if (!info_out)
            throw std::runtime_error("closed-shape exact membership page plan info_out pointer must not be null");
        *page_plan_out = prepare_point_closed_shape_membership_exact_device_columns_page_plan_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, page_size, initial_capacity, info_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_produce_point_closed_shape_membership_exact_device_columns_page_2d(
        void* page_plan,
        size_t page_index, size_t max_rows,
        RtdlNativeDevicePairColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!page_plan)
            throw std::runtime_error("closed-shape exact membership page plan handle must not be null");
        if (!columns_out)
            throw std::runtime_error("closed-shape exact membership page plan columns_out pointer must not be null");
        produce_point_closed_shape_membership_exact_device_columns_page_2d_optix(
            reinterpret_cast<NativeClosedShapeExactDeviceColumnPagePlan2D*>(page_plan),
            page_index, max_rows, columns_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_point_closed_shape_membership_exact_device_columns_page_plan_2d(
        void* page_plan)
{
    delete reinterpret_cast<NativeClosedShapeExactDeviceColumnPagePlan2D*>(page_plan);
}

extern "C" int rtdl_optix_prepared_point_closed_shape_first_boundary_crossing_device_columns_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t max_rows,
        RtdlNativeClosedShapeBoundaryEventDeviceColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape boundary-event handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("closed-shape boundary-event device columns_out pointer must not be null");
        run_prepared_point_closed_shape_first_boundary_crossing_device_columns_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, max_rows, columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_point_closed_shape_membership_candidate_device_columns_2d(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_point_closed_shape_membership_candidate_device_columns_2d_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_point_closed_shape_membership_exact_device_columns_2d(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_point_closed_shape_membership_exact_device_columns_2d_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_point_closed_shape_boundary_event_device_columns_2d(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_point_closed_shape_boundary_event_device_columns_2d_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_point_closed_shape_membership_point_id_count_device_columns_2d(
        void* prepared,
        const RtdlPoint* points, size_t point_count,
        size_t group_capacity,
        RtdlNativeDeviceGroupedCountI64Columns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared closed-shape membership handle must not be null");
        if (!points && point_count != 0)
            throw std::runtime_error("point pointer must not be null when point_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("closed-shape membership point-id count device columns_out pointer must not be null");
        run_prepared_point_closed_shape_membership_point_id_count_device_columns_2d_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            points, point_count, group_capacity, columns_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_point_closed_shape_membership_2d(void* prepared)
{
    delete reinterpret_cast<PreparedShapePairRelationBuild*>(prepared);
}

extern "C" void rtdl_optix_destroy_prepared_point_probe_columns_2d(void* prepared_points)
{
    delete reinterpret_cast<PreparedPointProbeColumns2D*>(prepared_points);
}

extern "C" int rtdl_optix_run_shape_pair_relation_flags(
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        const RtdlPolygonRef* right_polys, size_t right_count,
        const double* right_verts_xy,      size_t right_vert_xy_count,
        RtdlShapePairRelationRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (left_count == 0 || right_count == 0) return;
        run_shape_pair_relation_flags_optix(left_polys, left_count, left_verts_xy, left_vert_xy_count,
                          right_polys, right_count, right_verts_xy, right_vert_xy_count,
                          rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_shape_pair_relation_flags(
        const RtdlPolygonRef* right_polys, size_t right_count,
        const double* right_verts_xy,      size_t right_vert_xy_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!right_polys && right_count != 0)
            throw std::runtime_error("right polygon pointer must not be null when right_count is nonzero");
        if (!right_verts_xy && right_vert_xy_count != 0)
            throw std::runtime_error("right vertices pointer must not be null when right_vert_xy_count is nonzero");
        *prepared_out = nullptr;
        *prepared_out = prepare_shape_pair_relation_flags_optix(
            right_polys, right_count, right_verts_xy, right_vert_xy_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_shape_pair_relation_left_set(
        const RtdlPolygonRef* left_polys, size_t left_count,
        const double* left_verts_xy,      size_t left_vert_xy_count,
        void** prepared_left_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_left_out)
            throw std::runtime_error("prepared_left_out must not be null");
        if (!left_polys && left_count != 0)
            throw std::runtime_error("left polygon pointer must not be null when left_count is nonzero");
        if (!left_verts_xy && left_vert_xy_count != 0)
            throw std::runtime_error("left vertices pointer must not be null when left_vert_xy_count is nonzero");
        *prepared_left_out = nullptr;
        *prepared_left_out = prepare_shape_pair_relation_left_set_optix(
            left_polys, left_count, left_verts_xy, left_vert_xy_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_shape_pair_relation_flags(
        void* prepared,
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        RtdlShapePairRelationRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared shape-pair relation handle must not be null");
        if (!left_polys && left_count != 0)
            throw std::runtime_error("left polygon pointer must not be null when left_count is nonzero");
        if (!left_verts_xy && left_vert_xy_count != 0)
            throw std::runtime_error("left vertices pointer must not be null when left_vert_xy_count is nonzero");
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        run_prepared_shape_pair_relation_flags_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            left_polys, left_count, left_verts_xy, left_vert_xy_count,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_shape_pair_relation_flags(
        void* prepared,
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        size_t* active_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared shape-pair relation handle must not be null");
        if (!left_polys && left_count != 0)
            throw std::runtime_error("left polygon pointer must not be null when left_count is nonzero");
        if (!left_verts_xy && left_vert_xy_count != 0)
            throw std::runtime_error("left vertices pointer must not be null when left_vert_xy_count is nonzero");
        if (!active_count_out)
            throw std::runtime_error("active_count_out must not be null");
        *active_count_out = 0;
        count_shape_pair_relation_flags_with_prepared_right_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            left_polys, left_count, left_verts_xy, left_vert_xy_count,
            active_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_shape_pair_relation_active_device(
        void* prepared,
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        size_t* active_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared shape-pair relation handle must not be null");
        if (!left_polys && left_count != 0)
            throw std::runtime_error("left polygon pointer must not be null when left_count is nonzero");
        if (!left_verts_xy && left_vert_xy_count != 0)
            throw std::runtime_error("left vertices pointer must not be null when left_vert_xy_count is nonzero");
        if (!active_count_out)
            throw std::runtime_error("active_count_out must not be null");
        *active_count_out = 0;
        count_shape_pair_relation_active_device_with_prepared_right_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            left_polys, left_count, left_verts_xy, left_vert_xy_count,
            active_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_shape_pair_relation_active_device_prepared_left(
        void* prepared,
        void* prepared_left,
        size_t* active_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared shape-pair relation handle must not be null");
        if (!prepared_left)
            throw std::runtime_error("prepared shape-pair left-set handle must not be null");
        if (!active_count_out)
            throw std::runtime_error("active_count_out must not be null");
        *active_count_out = 0;
        count_shape_pair_relation_active_device_with_prepared_left_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedShapePairRelationLeftSet*>(prepared_left),
            active_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_shape_pair_relation_active_device_prepared_left_executor(
        void* prepared,
        void* prepared_left,
        void** executor_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared shape-pair relation handle must not be null");
        if (!prepared_left)
            throw std::runtime_error("prepared shape-pair left-set handle must not be null");
        if (!executor_out)
            throw std::runtime_error("executor_out must not be null");
        *executor_out = prepare_shape_pair_relation_active_count_prepared_left_executor_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            reinterpret_cast<PreparedShapePairRelationLeftSet*>(prepared_left));
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_shape_pair_relation_active_device_prepared_left_executor(
        void* executor,
        size_t* active_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!executor)
            throw std::runtime_error("prepared-left shape-pair active-count executor must not be null");
        if (!active_count_out)
            throw std::runtime_error("active_count_out must not be null");
        *active_count_out = 0;
        run_shape_pair_relation_active_count_prepared_left_executor_optix(
            reinterpret_cast<PreparedShapePairRelationActiveCountPreparedLeftExecutor*>(executor),
            active_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepared_shape_pair_relation_active_device_columns(
        void* prepared,
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        size_t max_rows,
        RtdlNativeShapePairRelationDeviceColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared)
            throw std::runtime_error("prepared shape-pair relation handle must not be null");
        if (!left_polys && left_count != 0)
            throw std::runtime_error("left polygon pointer must not be null when left_count is nonzero");
        if (!left_verts_xy && left_vert_xy_count != 0)
            throw std::runtime_error("left vertices pointer must not be null when left_vert_xy_count is nonzero");
        if (!columns_out)
            throw std::runtime_error("shape-pair active relation device columns_out must not be null");
        run_prepared_shape_pair_relation_active_device_columns_optix(
            reinterpret_cast<PreparedShapePairRelationBuild*>(prepared),
            left_polys, left_count, left_verts_xy, left_vert_xy_count,
            max_rows, columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_shape_pair_relation_active_device_columns(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_shape_pair_relation_active_device_columns_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_shape_pair_relation_flags(void* prepared)
{
    delete reinterpret_cast<PreparedShapePairRelationBuild*>(prepared);
}

extern "C" void rtdl_optix_destroy_prepared_shape_pair_relation_left_set(void* prepared_left)
{
    delete reinterpret_cast<PreparedShapePairRelationLeftSet*>(prepared_left);
}

extern "C" void rtdl_optix_destroy_shape_pair_relation_active_device_prepared_left_executor(void* executor)
{
    delete reinterpret_cast<PreparedShapePairRelationActiveCountPreparedLeftExecutor*>(executor);
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

extern "C" int rtdl_optix_run_ray_closest_hit_3d(
        const RtdlRay3D*      rays,      size_t ray_count,
        const RtdlTriangle3D* triangles, size_t triangle_count,
        RtdlRayClosestHitRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out)
            throw std::runtime_error("output pointers must not be null");
        *rows_out = nullptr; *row_count_out = 0;
        if (ray_count == 0 || triangle_count == 0) return;
        run_ray_closest_hit_3d_optix(rays, ray_count, triangles, triangle_count,
                                     rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_create(
        const RtdlTriangle3D* triangles, size_t triangle_count,
        void** handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!handle_out)
            throw std::runtime_error("handle output pointer must not be null");
        if (!triangles && triangle_count != 0)
            throw std::runtime_error("triangle pointer must not be null when triangle_count is nonzero");
        *handle_out = nullptr;
        *handle_out = prepare_static_triangle_scene_3d_optix(triangles, triangle_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_create_device_triangles(
        const uint32_t* triangle_ids,
        const double* triangle_x0,
        const double* triangle_y0,
        const double* triangle_z0,
        const double* triangle_x1,
        const double* triangle_y1,
        const double* triangle_z1,
        const double* triangle_x2,
        const double* triangle_y2,
        const double* triangle_z2,
        size_t triangle_count,
        void** handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!handle_out)
            throw std::runtime_error("handle output pointer must not be null");
        *handle_out = nullptr;
        *handle_out = prepare_static_triangle_scene_3d_device_triangles_optix(
            triangle_ids,
            triangle_x0,
            triangle_y0,
            triangle_z0,
            triangle_x1,
            triangle_y1,
            triangle_z1,
            triangle_x2,
            triangle_y2,
            triangle_z2,
            triangle_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags(
        void* handle,
        const RtdlSegment3D* segments, size_t segment_count,
        const uint32_t* group_offsets, size_t group_count,
        uint8_t* flags_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_grouped_segment_any_hit_flags_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(handle),
            segments,
            segment_count,
            group_offsets,
            group_count,
            flags_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_grouped_segment_query_create(
        const RtdlSegment3D* segments, size_t segment_count,
        const uint32_t* group_offsets, size_t group_count,
        void** query_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!query_handle_out)
            throw std::runtime_error("query handle output pointer must not be null");
        *query_handle_out = nullptr;
        *query_handle_out = prepare_static_triangle_scene_3d_grouped_segment_query_optix(
            segments,
            segment_count,
            group_offsets,
            group_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_flags(
        void* scene_handle,
        void* query_handle,
        uint8_t* flags_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_grouped_segment_query_any_hit_flags_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedGroupedSegmentQuery3D*>(query_handle),
            flags_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_grouped_segment_query_any_hit_count(
        void* scene_handle,
        void* query_handle,
        uint32_t* flagged_group_count_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_grouped_segment_query_any_hit_count_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedGroupedSegmentQuery3D*>(query_handle),
            flagged_group_count_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        const uint64_t* ray_weights,
        uint64_t* weighted_hit_sum_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_any_hit_weighted_sum_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            ray_weights,
            weighted_hit_sum_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_any_hit_weighted_sum_device_rays(
        void* scene_handle,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_oz,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_dz,
        const double* ray_tmax,
        size_t ray_count,
        const uint64_t* ray_weights,
        uint64_t* weighted_hit_sum_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_any_hit_weighted_sum_device_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            ray_ids,
            ray_ox,
            ray_oy,
            ray_oz,
            ray_dx,
            ray_dy,
            ray_dz,
            ray_tmax,
            ray_count,
            ray_weights,
            weighted_hit_sum_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        const uint32_t* primitive_group_ids, size_t primitive_group_id_count,
        const uint64_t* primitive_values, size_t primitive_value_count,
        size_t group_count,
        uint32_t reduction,
        uint64_t* group_counts_out,
        uint64_t* group_sums_out,
        uint64_t* group_mins_out,
        uint64_t* group_maxs_out,
        uint64_t* hit_event_count_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            primitive_group_ids,
            primitive_group_id_count,
            primitive_values,
            primitive_value_count,
            group_count,
            reduction,
            group_counts_out,
            group_sums_out,
            group_mins_out,
            group_maxs_out,
            hit_event_count_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        uint32_t deduplicate_primitives,
        RtdlRayTriangleHitStreamRow* rows_out,
        size_t max_rows,
        size_t* row_count_out,
        uint64_t* hit_event_count_out,
        uint32_t* overflow_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            deduplicate_primitives,
            rows_out,
            max_rows,
            row_count_out,
            hit_event_count_out,
            overflow_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        RtdlNativeDeviceHitStreamColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            deduplicate_primitives,
            max_rows,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        uint64_t ray_ids_device_ptr,
        uint64_t primitive_ids_device_ptr,
        RtdlNativeDeviceHitStreamColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            deduplicate_primitives,
            max_rows,
            ray_ids_device_ptr,
            primitive_ids_device_ptr,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        uint64_t ray_ids_device_ptr,
        uint64_t primitive_ids_device_ptr,
        uint64_t row_count_device_ptr,
        uint64_t hit_event_count_device_ptr,
        uint64_t overflow_device_ptr,
        RtdlNativeDeviceHitStreamColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            deduplicate_primitives,
            max_rows,
            ray_ids_device_ptr,
            primitive_ids_device_ptr,
            row_count_device_ptr,
            hit_event_count_device_ptr,
            overflow_device_ptr,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_on_stream(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        uint64_t ray_ids_device_ptr,
        uint64_t primitive_ids_device_ptr,
        uint64_t row_count_device_ptr,
        uint64_t hit_event_count_device_ptr,
        uint64_t overflow_device_ptr,
        uint64_t cuda_stream_ptr,
        RtdlNativeDeviceHitStreamColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_on_stream_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            deduplicate_primitives,
            max_rows,
            ray_ids_device_ptr,
            primitive_ids_device_ptr,
            row_count_device_ptr,
            hit_event_count_device_ptr,
            overflow_device_ptr,
            cuda_stream_ptr,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_triangle_hit_stream_into_device_columns_with_status_on_stream(
        void* scene_handle,
        void* ray_batch_handle,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        uint64_t ray_ids_device_ptr,
        uint64_t primitive_ids_device_ptr,
        uint64_t row_count_device_ptr,
        uint64_t hit_event_count_device_ptr,
        uint64_t overflow_device_ptr,
        uint64_t cuda_stream_ptr,
        RtdlNativeDeviceHitStreamColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_batch_triangle_hit_stream_into_device_columns_with_status_on_stream_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            deduplicate_primitives,
            max_rows,
            ray_ids_device_ptr,
            primitive_ids_device_ptr,
            row_count_device_ptr,
            hit_event_count_device_ptr,
            overflow_device_ptr,
            cuda_stream_ptr,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_ray_triangle_hit_stream_device_columns(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_ray_triangle_hit_stream_device_columns_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_ray_triangle_hit_stream_async_launch(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_ray_triangle_hit_stream_async_launch_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_primitive_grouped_i64_payload_3d_create(
        const uint32_t* primitive_group_ids, size_t primitive_group_id_count,
        const uint64_t* primitive_values, size_t primitive_value_count,
        size_t group_count,
        void** payload_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!payload_handle_out)
            throw std::runtime_error("payload handle output pointer must not be null");
        *payload_handle_out = nullptr;
        *payload_handle_out = prepare_primitive_grouped_i64_payload_3d_optix(
            primitive_group_ids,
            primitive_group_id_count,
            primitive_values,
            primitive_value_count,
            group_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction(
        void* scene_handle,
        void* payload_handle,
        const RtdlRay3D* rays, size_t ray_count,
        uint32_t reduction,
        uint64_t* group_counts_out,
        uint64_t* group_sums_out,
        uint64_t* group_mins_out,
        uint64_t* group_maxs_out,
        uint64_t* hit_event_count_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedPrimitiveGroupedI64Payload3D*>(payload_handle),
            rays,
            ray_count,
            reduction,
            group_counts_out,
            group_sums_out,
            group_mins_out,
            group_maxs_out,
            hit_event_count_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction(
        void* scene_handle,
        void* payload_handle,
        void* ray_batch_handle,
        uint32_t reduction,
        uint64_t* group_counts_out,
        uint64_t* group_sums_out,
        uint64_t* group_mins_out,
        uint64_t* group_maxs_out,
        uint64_t* hit_event_count_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedPrimitiveGroupedI64Payload3D*>(payload_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            reduction,
            group_counts_out,
            group_sums_out,
            group_mins_out,
            group_maxs_out,
            hit_event_count_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights(
        void* scene_handle,
        void* ray_batch_handle,
        const uint64_t* ray_weights,
        size_t ray_weight_count,
        uint64_t* weighted_hit_sum_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            ray_weights,
            ray_weight_count,
            weighted_hit_sum_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_prepare_graph_executor(
        void* scene_handle,
        void* ray_batch_handle,
        const uint64_t* ray_weights,
        size_t ray_weight_count,
        uint64_t weighted_hit_sum_device_ptr,
        void** executor_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        prepare_prepared_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_graph_executor_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            ray_weights,
            ray_weight_count,
            weighted_hit_sum_device_ptr,
            executor_handle_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_launch_graph_executor_on_stream(
        void* executor_handle,
        uint64_t cuda_stream_ptr,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        launch_prepared_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_graph_executor_on_stream_optix(
            reinterpret_cast<NativeRayBatchWeightedSumDeviceOutputGraphExecutor*>(executor_handle),
            cuda_stream_ptr);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_release_graph_executor(
        void* executor_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_prepared_static_triangle_scene_3d_ray_batch_any_hit_weighted_sum_device_weights_graph_executor_optix(
            executor_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        uint64_t* hit_count_sum_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_hit_count_sum_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            hit_count_sum_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_closest_hit_rows(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        RtdlRayClosestHitRow** rows_out, size_t* row_count_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_closest_hit_rows_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            rows_out,
            row_count_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_ray_batch_3d_create(
        const RtdlRay3D* rays, size_t ray_count,
        void** ray_batch_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!ray_batch_handle_out)
            throw std::runtime_error("ray batch handle output pointer must not be null");
        *ray_batch_handle_out = nullptr;
        *ray_batch_handle_out = prepare_ray_batch_3d_optix(rays, ray_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_ray_batch_3d_create_device_rays(
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_oz,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_dz,
        const double* ray_tmax,
        size_t ray_count,
        void** ray_batch_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!ray_batch_handle_out)
            throw std::runtime_error("ray batch handle output pointer must not be null");
        *ray_batch_handle_out = nullptr;
        *ray_batch_handle_out = prepare_ray_batch_3d_device_rays_optix(
            ray_ids,
            ray_ox,
            ray_oy,
            ray_oz,
            ray_dx,
            ray_dy,
            ray_dz,
            ray_tmax,
            ray_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_ray_batch_3d_create_device_xz_constant_y_direction(
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oz,
        double ray_oy,
        double ray_dx,
        double ray_dy,
        double ray_dz,
        double ray_tmax,
        size_t ray_count,
        void** ray_batch_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!ray_batch_handle_out)
            throw std::runtime_error("ray batch handle output pointer must not be null");
        *ray_batch_handle_out = nullptr;
        *ray_batch_handle_out = prepare_ray_batch_3d_device_xz_constant_y_direction_optix(
            ray_ids,
            ray_ox,
            ray_oz,
            ray_oy,
            ray_dx,
            ray_dy,
            ray_dz,
            ray_tmax,
            ray_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create(
        const uint32_t* ray_group_ids,
        size_t ray_group_id_count,
        const double* candidate_values,
        const uint32_t* candidate_indices,
        size_t candidate_count,
        size_t group_count,
        void** grouped_inputs_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!grouped_inputs_handle_out)
            throw std::runtime_error("grouped argmin inputs handle output pointer must not be null");
        *grouped_inputs_handle_out = nullptr;
        *grouped_inputs_handle_out = prepare_closest_hit_grouped_argmin_3d_optix(
            ray_group_ids,
            ray_group_id_count,
            candidate_values,
            candidate_indices,
            candidate_count,
            group_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create_device_per_ray_groups(
        uint64_t per_ray_group_ids_device_ptr,
        size_t per_ray_group_id_count,
        uint64_t candidate_values_device_ptr,
        uint64_t candidate_indices_device_ptr,
        size_t candidate_count,
        size_t group_count,
        void** grouped_inputs_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!grouped_inputs_handle_out)
            throw std::runtime_error("device per-ray grouped argmin handle output pointer must not be null");
        *grouped_inputs_handle_out = nullptr;
        *grouped_inputs_handle_out = prepare_closest_hit_grouped_argmin_3d_device_per_ray_groups_optix(
            per_ray_group_ids_device_ptr,
            per_ray_group_id_count,
            candidate_values_device_ptr,
            candidate_indices_device_ptr,
            candidate_count,
            group_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_grouped_candidate_argmin_inputs_create(
        const uint32_t* candidate_group_ids,
        const double* candidate_values,
        const uint32_t* candidate_indices,
        size_t candidate_count,
        size_t group_count,
        void** grouped_inputs_handle_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!grouped_inputs_handle_out)
            throw std::runtime_error("grouped candidate argmin handle output pointer must not be null");
        *grouped_inputs_handle_out = nullptr;
        *grouped_inputs_handle_out = prepare_grouped_candidate_argmin_optix(
            candidate_group_ids,
            candidate_values,
            candidate_indices,
            candidate_count,
            group_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_grouped_candidate_argmin_finalize(
        void* grouped_inputs_handle,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* finalize_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_grouped_candidate_argmin_optix(
            reinterpret_cast<PreparedGroupedCandidateArgmin*>(grouped_inputs_handle),
            group_has_value_out,
            group_index_out,
            group_value_out,
            finalize_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_rows(
        void* scene_handle,
        void* ray_batch_handle,
        RtdlRayClosestHitRow** rows_out, size_t* row_count_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_rows_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            rows_out,
            row_count_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_closest_hit_grouped_argmin(
        void* scene_handle,
        const RtdlRay3D* rays, size_t ray_count,
        const uint32_t* ray_group_ids, size_t ray_group_id_count,
        const double* candidate_values, const uint32_t* candidate_indices,
        size_t candidate_count, size_t group_count,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_closest_hit_grouped_argmin_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            rays,
            ray_count,
            ray_group_ids,
            ray_group_id_count,
            candidate_values,
            candidate_indices,
            candidate_count,
            group_count,
            group_has_value_out,
            group_index_out,
            group_value_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin(
        void* scene_handle,
        void* ray_batch_handle,
        const uint32_t* ray_group_ids, size_t ray_group_id_count,
        const double* candidate_values, const uint32_t* candidate_indices,
        size_t candidate_count, size_t group_count,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            ray_group_ids,
            ray_group_id_count,
            candidate_values,
            candidate_indices,
            candidate_count,
            group_count,
            group_has_value_out,
            group_index_out,
            group_value_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin(
        void* scene_handle,
        void* ray_batch_handle,
        void* grouped_inputs_handle,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            reinterpret_cast<PreparedClosestHitGroupedArgmin3D*>(grouped_inputs_handle),
            group_has_value_out,
            group_index_out,
            group_value_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device(
        void* scene_handle,
        void* ray_batch_handle,
        void* grouped_inputs_handle,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            reinterpret_cast<PreparedClosestHitGroupedArgmin3D*>(grouped_inputs_handle),
        traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device_outputs(
        void* scene_handle,
        void* ray_batch_handle,
        void* grouped_inputs_handle,
        uint64_t group_has_value_out_device_ptr,
        uint64_t group_index_out_device_ptr,
        uint64_t group_value_out_device_ptr,
        size_t output_group_count,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device_outputs_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle),
            reinterpret_cast<PreparedClosestHitGroupedArgmin3D*>(grouped_inputs_handle),
            group_has_value_out_device_ptr,
            group_index_out_device_ptr,
            group_value_out_device_ptr,
            output_group_count,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_closest_hit_grouped_argmin_inputs_3d_finalize(
        void* grouped_inputs_handle,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        finalize_prepared_closest_hit_grouped_argmin_3d_optix(
            reinterpret_cast<PreparedClosestHitGroupedArgmin3D*>(grouped_inputs_handle),
            group_has_value_out,
            group_index_out,
            group_value_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_closest_hit_grouped_argmin_inputs_3d_copy_device_outputs(
        void* grouped_inputs_handle,
        uint64_t group_has_value_out_device_ptr,
        uint64_t group_index_out_device_ptr,
        uint64_t group_value_out_device_ptr,
        size_t output_group_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        copy_prepared_closest_hit_grouped_argmin_3d_device_outputs_optix(
            reinterpret_cast<PreparedClosestHitGroupedArgmin3D*>(grouped_inputs_handle),
            group_has_value_out_device_ptr,
            group_index_out_device_ptr,
            group_value_out_device_ptr,
            output_group_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin(
        void* scene_a_handle,
        void* ray_batch_a_handle,
        void* grouped_inputs_a_handle,
        void* scene_b_handle,
        void* ray_batch_b_handle,
        void* grouped_inputs_b_handle,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* traversal_a_seconds_out,
        double* traversal_b_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_a_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_a_handle),
            reinterpret_cast<PreparedClosestHitGroupedArgmin3D*>(grouped_inputs_a_handle),
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_b_handle),
            reinterpret_cast<PreparedRayBatch3D*>(ray_batch_b_handle),
            reinterpret_cast<PreparedClosestHitGroupedArgmin3D*>(grouped_inputs_b_handle),
            group_has_value_out,
            group_index_out,
            group_value_out,
            traversal_a_seconds_out,
            traversal_b_seconds_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum_device_rays(
        void* scene_handle,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_oz,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_dz,
        const double* ray_tmax,
        size_t ray_count,
        uint64_t* hit_count_sum_out,
        double* traversal_seconds_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_static_triangle_scene_3d_ray_hit_count_sum_device_optix(
            reinterpret_cast<PreparedStaticTriangleScene3D*>(scene_handle),
            ray_ids,
            ray_ox,
            ray_oy,
            ray_oz,
            ray_dx,
            ray_dy,
            ray_dz,
            ray_tmax,
            ray_count,
            hit_count_sum_out,
            traversal_seconds_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_static_triangle_scene_3d_grouped_segment_query_destroy(void* query_handle)
{
    delete reinterpret_cast<PreparedGroupedSegmentQuery3D*>(query_handle);
}

extern "C" void rtdl_optix_ray_batch_3d_destroy(void* ray_batch_handle)
{
    delete reinterpret_cast<PreparedRayBatch3D*>(ray_batch_handle);
}

extern "C" void rtdl_optix_closest_hit_grouped_argmin_inputs_3d_destroy(void* grouped_inputs_handle)
{
    delete reinterpret_cast<PreparedClosestHitGroupedArgmin3D*>(grouped_inputs_handle);
}

extern "C" void rtdl_optix_primitive_grouped_i64_payload_3d_destroy(void* payload_handle)
{
    delete reinterpret_cast<PreparedPrimitiveGroupedI64Payload3D*>(payload_handle);
}

extern "C" void rtdl_optix_grouped_candidate_argmin_inputs_destroy(void* grouped_inputs_handle)
{
    delete reinterpret_cast<PreparedGroupedCandidateArgmin*>(grouped_inputs_handle);
}

extern "C" void rtdl_optix_static_triangle_scene_3d_destroy(void* handle)
{
    delete reinterpret_cast<PreparedStaticTriangleScene3D*>(handle);
}

extern "C" int rtdl_optix_run_ray_segment_group_count_2d(
        const RtdlRay2D* rays, size_t ray_count,
        const RtdlSegment* segments, size_t segment_count,
        const uint32_t* segment_group_ids,
        RtdlRaySegmentGroupCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_ray_segment_group_count_2d_optix(
            rays,
            ray_count,
            segments,
            segment_count,
            segment_group_ids,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_ray_segment_group_count_2d(
        const RtdlSegment* segments, size_t segment_count,
        const uint32_t* segment_group_ids,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        *prepared_out = nullptr;
        *prepared_out = prepare_ray_segment_group_count_2d_optix(
            segments,
            segment_count,
            segment_group_ids);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_ray_segment_group_count_2d(
        void* prepared,
        const RtdlRay2D* rays, size_t ray_count,
        RtdlRaySegmentGroupCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_ray_segment_group_count_2d_optix(
            reinterpret_cast<PreparedRaySegmentGroupCount2D*>(prepared),
            rays,
            ray_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d(
        void* prepared,
        const RtdlRay2D* rays, size_t ray_count,
        RtdlRaySegmentGroupCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_ray_segment_group_odd_parity_2d_optix(
            reinterpret_cast<PreparedRaySegmentGroupCount2D*>(prepared),
            rays,
            ray_count,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_ray_segment_group_count_2d(void* prepared)
{
    delete reinterpret_cast<PreparedRaySegmentGroupCount2D*>(prepared);
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

extern "C" int rtdl_optix_prepare_ray_anyhit_2d_device_triangles(
        const uint32_t* triangle_ids,
        const double* triangle_x0,
        const double* triangle_y0,
        const double* triangle_x1,
        const double* triangle_y1,
        const double* triangle_x2,
        const double* triangle_y2,
        size_t triangle_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        *prepared_out = nullptr;
        *prepared_out = prepare_ray_anyhit_2d_device_triangles_optix(
            triangle_ids,
            triangle_x0,
            triangle_y0,
            triangle_x1,
            triangle_y1,
            triangle_x2,
            triangle_y2,
            triangle_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_ray_anyhit_2d_device_triangle_columns_aabbs(
        const uint32_t* triangle_ids,
        const double* triangle_x0,
        const double* triangle_y0,
        const double* triangle_x1,
        const double* triangle_y1,
        const double* triangle_x2,
        const double* triangle_y2,
        const void* triangle_aabbs,
        size_t triangle_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        *prepared_out = nullptr;
        *prepared_out = prepare_ray_anyhit_2d_device_triangle_columns_aabbs_optix(
            triangle_ids,
            triangle_x0,
            triangle_y0,
            triangle_x1,
            triangle_y1,
            triangle_x2,
            triangle_y2,
            triangle_aabbs,
            triangle_count);
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

extern "C" int rtdl_optix_prepare_aabb_index_2d(
        const RtdlAabb2D* boxes, size_t box_count,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!boxes && box_count != 0)
            throw std::runtime_error("boxes pointer must not be null when box_count is nonzero");
        *prepared_out = nullptr;
        *prepared_out = prepare_aabb_index_2d_optix(boxes, box_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_aabb_index_2d(
        void* prepared,
        const RtdlPoint* point_queries, size_t point_query_count,
        const RtdlAabb2D* box_queries, size_t box_query_count,
        uint32_t operation,
        size_t* hit_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!hit_count_out)
            throw std::runtime_error("hit_count_out must not be null");
        count_prepared_aabb_index_2d_optix(
            reinterpret_cast<PreparedAabbIndex2DOptix*>(prepared),
            point_queries,
            point_query_count,
            box_queries,
            box_query_count,
            operation,
            hit_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_aabb_point_queries_2d(
        const RtdlPoint* point_queries, size_t point_query_count,
        void** queries_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!queries_out)
            throw std::runtime_error("queries_out must not be null");
        if (!point_queries && point_query_count != 0)
            throw std::runtime_error("point_queries pointer must not be null when point_query_count is nonzero");
        *queries_out = nullptr;
        *queries_out = prepare_aabb_index_point_queries_2d_optix(point_queries, point_query_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_aabb_box_queries_2d(
        const RtdlAabb2D* box_queries, size_t box_query_count,
        void** queries_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!queries_out)
            throw std::runtime_error("queries_out must not be null");
        if (!box_queries && box_query_count != 0)
            throw std::runtime_error("box_queries pointer must not be null when box_query_count is nonzero");
        *queries_out = nullptr;
        *queries_out = prepare_aabb_index_box_queries_2d_optix(box_queries, box_query_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_aabb_index_2d_packed_queries(
        void* prepared,
        void* prepared_queries,
        uint32_t operation,
        size_t* hit_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!hit_count_out)
            throw std::runtime_error("hit_count_out must not be null");
        count_prepared_aabb_index_2d_packed_queries_optix(
            reinterpret_cast<PreparedAabbIndex2DOptix*>(prepared),
            reinterpret_cast<PreparedAabbIndexQueries2DOptix*>(prepared_queries),
            operation,
            hit_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_aabb_index_2d_multi_operation_packed_queries(
        void* prepared,
        void* prepared_point_queries,
        void* prepared_box_queries,
        size_t* point_contains_out,
        size_t* range_contains_out,
        size_t* range_intersects_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        count_prepared_aabb_index_2d_multi_operation_packed_queries_optix(
            reinterpret_cast<PreparedAabbIndex2DOptix*>(prepared),
            reinterpret_cast<PreparedAabbIndexQueries2DOptix*>(prepared_point_queries),
            reinterpret_cast<PreparedAabbIndexQueries2DOptix*>(prepared_box_queries),
            point_contains_out,
            range_contains_out,
            range_intersects_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows(
        void* prepared,
        const RtdlAabb2D* box_queries, size_t box_query_count,
        RtdlAabbPairRow* rows_out, size_t row_capacity,
        size_t* emitted_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        collect_prepared_aabb_index_2d_range_intersection_rows_optix(
            reinterpret_cast<PreparedAabbIndex2DOptix*>(prepared),
            box_queries,
            box_query_count,
            rows_out,
            row_capacity,
            emitted_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows_packed_queries(
        void* prepared,
        void* prepared_queries,
        RtdlAabbPairRow* rows_out, size_t row_capacity,
        size_t* emitted_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        collect_prepared_aabb_index_2d_range_intersection_rows_packed_queries_optix(
            reinterpret_cast<PreparedAabbIndex2DOptix*>(prepared),
            reinterpret_cast<PreparedAabbIndexQueries2DOptix*>(prepared_queries),
            rows_out,
            row_capacity,
            emitted_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows(
        void* prepared,
        const RtdlPoint* point_queries, size_t point_query_count,
        RtdlAabbPairRow* rows_out, size_t row_capacity,
        size_t* emitted_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        collect_prepared_aabb_index_2d_point_contains_rows_optix(
            reinterpret_cast<PreparedAabbIndex2DOptix*>(prepared),
            point_queries,
            point_query_count,
            rows_out,
            row_capacity,
            emitted_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_aabb_queries_2d(void* prepared_queries)
{
    delete reinterpret_cast<PreparedAabbIndexQueries2DOptix*>(prepared_queries);
}

extern "C" void rtdl_optix_destroy_prepared_aabb_index_2d(void* prepared)
{
    delete reinterpret_cast<PreparedAabbIndex2DOptix*>(prepared);
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

extern "C" int rtdl_optix_count_prepared_ray_anyhit_2d_device_rays(
        void* prepared,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_tmax,
        size_t ray_count,
        size_t* hit_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        count_prepared_ray_anyhit_2d_device_rays_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            ray_ids,
            ray_ox,
            ray_oy,
            ray_dx,
            ray_dy,
            ray_tmax,
            ray_count,
            hit_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_ray_anyhit_2d_device_flags(
        void* prepared,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_tmax,
        size_t ray_count,
        uint32_t* any_hit_flags_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_ray_anyhit_2d_device_flags_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            ray_ids,
            ray_ox,
            ray_oy,
            ray_dx,
            ray_dy,
            ray_tmax,
            ray_count,
            any_hit_flags_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_ray_anyhit_2d_device_witnesses(
        void* prepared,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_tmax,
        size_t ray_count,
        uint32_t* witness_ray_ids_out,
        uint32_t* witness_primitive_ids_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_ray_anyhit_2d_device_witnesses_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            ray_ids,
            ray_ox,
            ray_oy,
            ray_dx,
            ray_dy,
            ray_tmax,
            ray_count,
            witness_ray_ids_out,
            witness_primitive_ids_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_ray_anyhit_2d_device_all_witnesses(
        void* prepared,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_tmax,
        size_t ray_count,
        uint32_t* witness_ray_ids_out,
        uint32_t* witness_primitive_ids_out,
        size_t witness_capacity,
        size_t* emitted_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_ray_anyhit_2d_device_all_witnesses_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            ray_ids,
            ray_ox,
            ray_oy,
            ray_dx,
            ray_dy,
            ray_tmax,
            ray_count,
            witness_ray_ids_out,
            witness_primitive_ids_out,
            witness_capacity,
            emitted_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed(
        void* prepared,
        void* prepared_rays,
        const uint32_t* group_indices,
        size_t group_index_count,
        uint32_t* group_flags_out,
        size_t group_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_rays)
            throw std::runtime_error("prepared_rays must not be null");
        group_flags_prepared_ray_anyhit_2d_packed_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            reinterpret_cast<PreparedRays2D*>(prepared_rays),
            group_indices,
            group_index_count,
            group_flags_out,
            group_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_group_indices_2d(
        const uint32_t* group_indices,
        size_t group_index_count,
        void** group_indices_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!group_indices_out)
            throw std::runtime_error("group_indices_out must not be null");
        if (!group_indices && group_index_count != 0)
            throw std::runtime_error("group_indices pointer must not be null when group_index_count is nonzero");
        *group_indices_out = nullptr;
        *group_indices_out = prepare_group_indices_2d_optix(group_indices, group_index_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices(
        void* prepared,
        void* prepared_rays,
        void* prepared_group_indices,
        uint32_t* group_flags_out,
        size_t group_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_rays)
            throw std::runtime_error("prepared_rays must not be null");
        if (!prepared_group_indices)
            throw std::runtime_error("prepared_group_indices must not be null");
        group_flags_prepared_ray_anyhit_2d_prepared_indices_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            reinterpret_cast<PreparedRays2D*>(prepared_rays),
            reinterpret_cast<PreparedGroupIndices2D*>(prepared_group_indices),
            group_flags_out,
            group_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices(
        void* prepared,
        void* prepared_rays,
        void* prepared_group_indices,
        size_t group_count,
        size_t* colliding_group_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_rays)
            throw std::runtime_error("prepared_rays must not be null");
        if (!prepared_group_indices)
            throw std::runtime_error("prepared_group_indices must not be null");
        if (!colliding_group_count_out)
            throw std::runtime_error("colliding_group_count_out must not be null");
        count_groups_prepared_ray_anyhit_2d_prepared_indices_optix(
            reinterpret_cast<PreparedRayAnyHit2D*>(prepared),
            reinterpret_cast<PreparedRays2D*>(prepared_rays),
            reinterpret_cast<PreparedGroupIndices2D*>(prepared_group_indices),
            group_count,
            colliding_group_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_group_indices_2d(void* prepared_group_indices)
{
    delete reinterpret_cast<PreparedGroupIndices2D*>(prepared_group_indices);
}

extern "C" void rtdl_optix_destroy_prepared_rays_2d(void* prepared_rays)
{
    delete reinterpret_cast<PreparedRays2D*>(prepared_rays);
}

extern "C" int rtdl_optix_run_segment_shape_hitcount(
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

extern "C" int rtdl_optix_prepare_segment_shape_hitcount_2d(
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

extern "C" int rtdl_optix_run_prepared_segment_shape_hitcount_2d(
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

extern "C" int rtdl_optix_count_prepared_segment_shape_hitcount_at_least_2d(
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

extern "C" int rtdl_optix_aggregate_prepared_segment_shape_hitcount_2d(
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

extern "C" void rtdl_optix_destroy_prepared_segment_shape_hitcount_2d(void* prepared)
{
    delete reinterpret_cast<PreparedSegmentPolygonHitcount2D*>(prepared);
}

extern "C" int rtdl_optix_run_segment_shape_anyhit_rows(
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

extern "C" int rtdl_optix_run_segment_shape_anyhit_rows_native_bounded(
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

extern "C" int rtdl_optix_collect_shape_pair_candidates_bounded(
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

extern "C" int rtdl_optix_collect_aggregate_frontier_2d(
        const RtdlAggregateFrontierSource2D* sources, size_t source_count,
        const RtdlAggregateFrontierNode2D* nodes, size_t node_count,
        const uint64_t* child_offsets, const int64_t* child_ids,
        const uint64_t* member_offsets, const int64_t* member_ids,
        double theta, uint64_t max_rows_per_source, uint64_t row_capacity,
        uint32_t deduplicate_fallback_targets,
        int64_t* frontier_rows_out, uint64_t* row_offsets_out,
        uint64_t* emitted_count_out, uint64_t* attempted_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        constexpr size_t kRowWidth = 7;
        constexpr int64_t kKindAggregate = 1;
        constexpr int64_t kKindExact = 2;
        constexpr int64_t kMetadataFlagsNone = 0;
        const uint64_t kUnbounded = std::numeric_limits<uint64_t>::max();

        if (!emitted_count_out || !attempted_count_out || !overflowed_out)
            throw std::runtime_error("aggregate-frontier count and overflow outputs must not be null");
        *emitted_count_out = 0;
        *attempted_count_out = 0;
        *overflowed_out = 0;
        if (theta <= 0.0 || !std::isfinite(theta))
            throw std::runtime_error("aggregate-frontier theta must be positive and finite");
        if (!sources && source_count != 0)
            throw std::runtime_error("aggregate-frontier sources must not be null when source_count is nonzero");
        if (!nodes && node_count != 0)
            throw std::runtime_error("aggregate-frontier nodes must not be null when node_count is nonzero");
        if (node_count != 0 && (!child_offsets || !member_offsets))
            throw std::runtime_error("aggregate-frontier CSR offsets must not be null when node_count is nonzero");
        if (!frontier_rows_out && row_capacity != 0)
            throw std::runtime_error("frontier_rows_out must not be null when row_capacity is nonzero");
        if (!row_offsets_out)
            throw std::runtime_error("row_offsets_out must not be null");
        if (row_capacity > std::numeric_limits<uint64_t>::max() / kRowWidth)
            throw std::runtime_error("aggregate-frontier row buffer size overflow");
        if (node_count == 0) {
            for (size_t index = 0; index <= source_count; ++index)
                row_offsets_out[index] = 0;
            return;
        }

        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (nodes[node_index].dfs_index != static_cast<int64_t>(node_index))
                throw std::runtime_error("aggregate-frontier nodes must be supplied in contiguous DFS order");
            if (nodes[node_index].half_size < 0.0)
                throw std::runtime_error("aggregate-frontier node half_size must be non-negative");
            if (child_offsets[node_index] > child_offsets[node_index + 1] ||
                    member_offsets[node_index] > member_offsets[node_index + 1])
                throw std::runtime_error("aggregate-frontier CSR offsets must be monotonic");
        }
        if (child_offsets[node_count] != 0 && !child_ids)
            throw std::runtime_error("aggregate-frontier child_ids must not be null when child CSR is non-empty");
        if (member_offsets[node_count] != 0 && !member_ids)
            throw std::runtime_error("aggregate-frontier member_ids must not be null when member CSR is non-empty");

        std::unordered_map<int64_t, size_t> node_index_by_id;
        node_index_by_id.reserve(node_count);
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            const auto inserted = node_index_by_id.emplace(nodes[node_index].id, node_index);
            if (!inserted.second)
                throw std::runtime_error("aggregate-frontier duplicate node id");
        }

        std::unordered_set<int64_t> child_id_set;
        child_id_set.reserve(static_cast<size_t>(child_offsets[node_count]));
        for (uint64_t child_index = 0; child_index < child_offsets[node_count]; ++child_index) {
            const int64_t child_id = child_ids[child_index];
            if (node_index_by_id.find(child_id) == node_index_by_id.end())
                throw std::runtime_error("aggregate-frontier child id is not present in node array");
            child_id_set.insert(child_id);
        }

        std::vector<size_t> root_indices;
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (child_id_set.find(nodes[node_index].id) == child_id_set.end())
                root_indices.push_back(node_index);
        }
        if (root_indices.empty())
            throw std::runtime_error("aggregate-frontier tree must contain at least one root");

        std::unordered_map<int64_t, int64_t> source_leaf_dfs_by_id;
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (!nodes[node_index].is_leaf)
                continue;
            for (uint64_t member_index = member_offsets[node_index]; member_index < member_offsets[node_index + 1]; ++member_index)
                source_leaf_dfs_by_id.emplace(member_ids[member_index], nodes[node_index].dfs_index);
        }

        auto subtree_end = [&](const RtdlAggregateFrontierNode2D& node) -> int64_t {
            return node.resume_index >= 0 ? node.resume_index : static_cast<int64_t>(node_count);
        };

        auto node_contains_source = [&](size_t node_index, int64_t source_id) -> bool {
            const RtdlAggregateFrontierNode2D& node = nodes[node_index];
            const auto found_leaf = source_leaf_dfs_by_id.find(source_id);
            if (found_leaf != source_leaf_dfs_by_id.end())
                return node.dfs_index <= found_leaf->second && found_leaf->second < subtree_end(node);
            for (uint64_t member_index = member_offsets[node_index]; member_index < member_offsets[node_index + 1]; ++member_index) {
                if (member_ids[member_index] == source_id)
                    return true;
            }
            return false;
        };

        auto mark_overflow = [&](uint64_t attempted) {
            *overflowed_out = 1u;
            *emitted_count_out = 0;
            *attempted_count_out = attempted;
        };

        std::vector<int64_t> frontier_rows;
        frontier_rows.reserve(static_cast<size_t>(std::min<uint64_t>(row_capacity, 1024)));
        uint64_t emitted_rows = 0;
        row_offsets_out[0] = 0;

        for (size_t source_index = 0; source_index < source_count; ++source_index) {
            const RtdlAggregateFrontierSource2D& source = sources[source_index];
            std::vector<int64_t> source_rows;
            std::unordered_set<int64_t> fallback_seen;
            if (deduplicate_fallback_targets != 0)
                fallback_seen.reserve(16);

            auto append_row = [&](int64_t kind, int64_t item_id, int64_t owner_node_id, int64_t dfs_index, int64_t resume_index) -> bool {
                const uint64_t next_source_rows = static_cast<uint64_t>(source_rows.size() / kRowWidth + 1);
                const uint64_t next_total_rows = emitted_rows + next_source_rows;
                if ((max_rows_per_source != kUnbounded && next_source_rows > max_rows_per_source) ||
                        next_total_rows > row_capacity) {
                    mark_overflow(next_total_rows);
                    return false;
                }
                source_rows.push_back(source.id);
                source_rows.push_back(kind);
                source_rows.push_back(item_id);
                source_rows.push_back(owner_node_id);
                source_rows.push_back(dfs_index);
                source_rows.push_back(resume_index);
                source_rows.push_back(kMetadataFlagsNone);
                return true;
            };

            bool overflowed = false;
            std::vector<size_t> stack;
            stack.reserve(root_indices.size());
            for (auto root_it = root_indices.rbegin(); root_it != root_indices.rend(); ++root_it)
                stack.push_back(*root_it);
            while (!stack.empty() && !overflowed) {
                const size_t node_index = stack.back();
                stack.pop_back();
                const RtdlAggregateFrontierNode2D& node = nodes[node_index];
                const double dx = node.cx - source.x;
                const double dy = node.cy - source.y;
                const double distance = std::hypot(dx, dy);
                const double opening_ratio = distance == 0.0
                    ? std::numeric_limits<double>::infinity()
                    : (2.0 * node.half_size) / distance;
                const bool contains_source = node_contains_source(node_index, source.id);
                const int64_t resume_index = node.resume_index >= 0 ? node.resume_index : -1;
                if (!contains_source && opening_ratio < theta) {
                    if (!append_row(kKindAggregate, node.id, node.id, node.dfs_index, resume_index))
                        overflowed = true;
                    continue;
                }
                if (child_offsets[node_index] != child_offsets[node_index + 1]) {
                    for (uint64_t child_pos = child_offsets[node_index + 1]; child_pos > child_offsets[node_index]; --child_pos) {
                        const int64_t child_id = child_ids[child_pos - 1];
                        stack.push_back(node_index_by_id.at(child_id));
                    }
                    continue;
                }
                for (uint64_t member_index = member_offsets[node_index]; member_index < member_offsets[node_index + 1]; ++member_index) {
                    const int64_t target_id = member_ids[member_index];
                    if (target_id == source.id)
                        continue;
                    if (deduplicate_fallback_targets != 0) {
                        const auto inserted = fallback_seen.insert(target_id);
                        if (!inserted.second)
                            continue;
                    }
                    if (!append_row(kKindExact, target_id, node.id, node.dfs_index, resume_index)) {
                        overflowed = true;
                        break;
                    }
                }
            }
            if (overflowed)
                return;
            frontier_rows.insert(frontier_rows.end(), source_rows.begin(), source_rows.end());
            emitted_rows += static_cast<uint64_t>(source_rows.size() / kRowWidth);
            row_offsets_out[source_index + 1] = emitted_rows;
        }

        if (emitted_rows > row_capacity) {
            mark_overflow(emitted_rows);
            return;
        }
        if (!frontier_rows.empty())
            std::memcpy(frontier_rows_out, frontier_rows.data(), sizeof(int64_t) * frontier_rows.size());
        *emitted_count_out = emitted_rows;
        *attempted_count_out = emitted_rows;
    }, error_out, error_size);
}

struct AggregateFrontierDeviceNode2D {
    int64_t id = 0;
    double cx = 0.0;
    double cy = 0.0;
    double half_size = 0.0;
    double mass = 0.0;
    int64_t dfs_index = 0;
    int64_t resume_index = -1;
    uint64_t child_begin = 0;
    uint64_t child_end = 0;
    uint64_t member_begin = 0;
    uint64_t member_end = 0;
    uint32_t is_leaf = 0;
};

struct AggregateFrontierDeviceColumnsOutput2D {
    CUdeviceptr source_ids = 0;
    CUdeviceptr frontier_kind_codes = 0;
    CUdeviceptr item_ids = 0;
    CUdeviceptr owner_aggregate_ids = 0;
    CUdeviceptr dfs_indices = 0;
    CUdeviceptr resume_indices = 0;
    CUdeviceptr metadata_flags = 0;
    CUdeviceptr row_offsets = 0;
    CUdeviceptr per_source_counts = 0;
    CUdeviceptr row_count = 0;
    CUdeviceptr attempted_count = 0;
    CUdeviceptr overflow = 0;
    uint64_t capacity = 0;
    uint64_t source_count = 0;

    ~AggregateFrontierDeviceColumnsOutput2D() {
        if (overflow) cuMemFree(overflow);
        if (attempted_count) cuMemFree(attempted_count);
        if (row_count) cuMemFree(row_count);
        if (per_source_counts) cuMemFree(per_source_counts);
        if (row_offsets) cuMemFree(row_offsets);
        if (metadata_flags) cuMemFree(metadata_flags);
        if (resume_indices) cuMemFree(resume_indices);
        if (dfs_indices) cuMemFree(dfs_indices);
        if (owner_aggregate_ids) cuMemFree(owner_aggregate_ids);
        if (item_ids) cuMemFree(item_ids);
        if (frontier_kind_codes) cuMemFree(frontier_kind_codes);
        if (source_ids) cuMemFree(source_ids);
    }
};

struct AggregateFrontierDeviceColumnsPrepared2D {
    CUdeviceptr nodes = 0;
    CUdeviceptr child_indices = 0;
    CUdeviceptr member_ids = 0;
    CUdeviceptr root_indices = 0;
    uint64_t node_count = 0;
    uint64_t child_count = 0;
    uint64_t member_count = 0;
    uint64_t root_count = 0;
    double theta = 0.0;
    uint32_t deduplicate_fallback_targets = 1u;
    int32_t device_ordinal = -1;
    std::unique_ptr<AggregateFrontierDeviceColumnsOutput2D> last_output;
    std::mutex mutex;

    ~AggregateFrontierDeviceColumnsPrepared2D() {
        last_output.reset();
        if (root_indices) cuMemFree(root_indices);
        if (member_ids) cuMemFree(member_ids);
        if (child_indices) cuMemFree(child_indices);
        if (nodes) cuMemFree(nodes);
    }
};

struct AggregateTreeFusedWeightedVectorSumOutput2D {
    CUdeviceptr vector_x = 0;
    CUdeviceptr vector_y = 0;
    CUdeviceptr visited_counts = 0;
    CUdeviceptr aggregate_counts = 0;
    CUdeviceptr exact_counts = 0;
    uint64_t source_count = 0;
    int32_t diagnostic_status_code = 0;
    uint32_t overflow = 0;

    ~AggregateTreeFusedWeightedVectorSumOutput2D() {
        if (exact_counts) cuMemFree(exact_counts);
        if (aggregate_counts) cuMemFree(aggregate_counts);
        if (visited_counts) cuMemFree(visited_counts);
        if (vector_y) cuMemFree(vector_y);
        if (vector_x) cuMemFree(vector_x);
    }
};

struct AggregateTreeFusedWeightedVectorSumPrepared2D {
    CUdeviceptr nodes = 0;
    CUdeviceptr child_indices = 0;
    CUdeviceptr member_indices = 0;
    CUdeviceptr root_indices = 0;
    CUdeviceptr target_leaf_dfs = 0;
    CUdeviceptr target_ids = 0;
    CUdeviceptr target_x = 0;
    CUdeviceptr target_y = 0;
    CUdeviceptr target_weight = 0;
    uint64_t target_count = 0;
    uint64_t node_count = 0;
    uint64_t child_count = 0;
    uint64_t member_count = 0;
    uint64_t root_count = 0;
    int32_t device_ordinal = -1;
    std::unique_ptr<AggregateTreeFusedWeightedVectorSumOutput2D> last_output;
    std::mutex mutex;

    ~AggregateTreeFusedWeightedVectorSumPrepared2D() {
        last_output.reset();
        if (target_leaf_dfs) cuMemFree(target_leaf_dfs);
        if (root_indices) cuMemFree(root_indices);
        if (member_indices) cuMemFree(member_indices);
        if (child_indices) cuMemFree(child_indices);
        if (nodes) cuMemFree(nodes);
    }
};

struct AggregateFrontierDeviceColumnsCuFunctions {
    CUmodule module = nullptr;
    CUfunction count_fn = nullptr;
    CUfunction prefix_fn = nullptr;
    CUfunction write_fn = nullptr;
    CUfunction fused_vector_sum_fn = nullptr;
    std::once_flag init;
};

static AggregateFrontierDeviceColumnsCuFunctions g_aggregate_frontier_device_columns_2d;

static const char* kAggregateFrontierDeviceColumns2DKernelSrc = R"CUDA(
#include <math.h>
#include <stdint.h>

struct AggregateFrontierDeviceNode2D {
    long long id;
    double cx;
    double cy;
    double half_size;
    double mass;
    long long dfs_index;
    long long resume_index;
    unsigned long long child_begin;
    unsigned long long child_end;
    unsigned long long member_begin;
    unsigned long long member_end;
    unsigned int is_leaf;
};

static __device__ __forceinline__ int rtdl_af_node_contains_source(
        const AggregateFrontierDeviceNode2D* nodes,
        const long long* member_ids,
        unsigned long long node_index,
        long long source_id)
{
    const AggregateFrontierDeviceNode2D node = nodes[node_index];
    for (unsigned long long member_index = node.member_begin; member_index < node.member_end; ++member_index) {
        if (member_ids[member_index] == source_id) {
            return 1;
        }
    }
    return 0;
}

static __device__ unsigned long long rtdl_af_count_source_rows(
        const AggregateFrontierDeviceNode2D* nodes,
        const unsigned long long* child_indices,
        const long long* member_ids,
        const unsigned long long* root_indices,
        unsigned long long root_count,
        long long source_id,
        double source_x,
        double source_y,
        double theta,
        unsigned int* overflow)
{
    const int kMaxStack = 256;
    unsigned long long stack[kMaxStack];
    int top = 0;
    if (root_count > (unsigned long long)kMaxStack) {
        atomicExch(overflow, 1u);
        return 0ull;
    }
    for (unsigned long long root_pos = root_count; root_pos > 0ull; --root_pos) {
        stack[top++] = root_indices[root_pos - 1ull];
    }

    unsigned long long count = 0ull;
    while (top > 0) {
        const unsigned long long node_index = stack[--top];
        const AggregateFrontierDeviceNode2D node = nodes[node_index];
        const double dx = node.cx - source_x;
        const double dy = node.cy - source_y;
        const double distance = sqrt(dx * dx + dy * dy);
        const double opening_ratio = distance == 0.0 ? INFINITY : (2.0 * node.half_size) / distance;
        const int contains_source = rtdl_af_node_contains_source(nodes, member_ids, node_index, source_id);
        if (!contains_source && opening_ratio < theta) {
            ++count;
            continue;
        }
        if (node.child_begin != node.child_end) {
            const unsigned long long child_count = node.child_end - node.child_begin;
            if (top + (int)child_count > kMaxStack) {
                atomicExch(overflow, 1u);
                return 0ull;
            }
            for (unsigned long long child_pos = node.child_end; child_pos > node.child_begin; --child_pos) {
                stack[top++] = child_indices[child_pos - 1ull];
            }
            continue;
        }
        for (unsigned long long member_index = node.member_begin; member_index < node.member_end; ++member_index) {
            if (member_ids[member_index] != source_id) {
                ++count;
            }
        }
    }
    return count;
}

extern "C" __global__ void rtdl_aggregate_frontier_count_2d(
        const AggregateFrontierDeviceNode2D* nodes,
        const unsigned long long* child_indices,
        const long long* member_ids,
        const unsigned long long* root_indices,
        unsigned long long root_count,
        const long long* source_ids,
        const double* source_xs,
        const double* source_ys,
        unsigned long long source_count,
        double theta,
        unsigned long long* per_source_counts,
        unsigned int* overflow)
{
    const unsigned long long source_index =
        (unsigned long long)blockIdx.x * (unsigned long long)blockDim.x + (unsigned long long)threadIdx.x;
    if (source_index >= source_count) {
        return;
    }
    per_source_counts[source_index] = rtdl_af_count_source_rows(
        nodes,
        child_indices,
        member_ids,
        root_indices,
        root_count,
        source_ids[source_index],
        source_xs[source_index],
        source_ys[source_index],
        theta,
        overflow);
}

extern "C" __global__ void rtdl_aggregate_frontier_prefix_2d(
        const unsigned long long* per_source_counts,
        unsigned long long source_count,
        unsigned long long row_capacity,
        unsigned long long* row_offsets,
        unsigned long long* row_count,
        unsigned long long* attempted_count,
        unsigned int* overflow)
{
    if (threadIdx.x != 0 || blockIdx.x != 0) {
        return;
    }
    unsigned long long total = 0ull;
    row_offsets[0] = 0ull;
    for (unsigned long long source_index = 0ull; source_index < source_count; ++source_index) {
        total += per_source_counts[source_index];
        row_offsets[source_index + 1ull] = total;
    }
    *attempted_count = total;
    if (*overflow != 0u || total > row_capacity) {
        *overflow = 1u;
        *row_count = 0ull;
        return;
    }
    *row_count = total;
}

extern "C" __global__ void rtdl_aggregate_frontier_write_2d(
        const AggregateFrontierDeviceNode2D* nodes,
        const unsigned long long* child_indices,
        const long long* member_ids,
        const unsigned long long* root_indices,
        unsigned long long root_count,
        const long long* source_ids,
        const double* source_xs,
        const double* source_ys,
        unsigned long long source_count,
        double theta,
        const unsigned long long* row_offsets,
        long long* output_source_ids,
        long long* output_kind_codes,
        long long* output_item_ids,
        long long* output_owner_aggregate_ids,
        long long* output_dfs_indices,
        long long* output_resume_indices,
        long long* output_metadata_flags,
        const unsigned int* overflow)
{
    if (*overflow != 0u) {
        return;
    }
    const unsigned long long source_index =
        (unsigned long long)blockIdx.x * (unsigned long long)blockDim.x + (unsigned long long)threadIdx.x;
    if (source_index >= source_count) {
        return;
    }

    const int kMaxStack = 256;
    unsigned long long stack[kMaxStack];
    int top = 0;
    if (root_count > (unsigned long long)kMaxStack) {
        return;
    }
    for (unsigned long long root_pos = root_count; root_pos > 0ull; --root_pos) {
        stack[top++] = root_indices[root_pos - 1ull];
    }

    const long long source_id = source_ids[source_index];
    const double source_x = source_xs[source_index];
    const double source_y = source_ys[source_index];
    unsigned long long local_row = 0ull;
    const unsigned long long base_row = row_offsets[source_index];

    while (top > 0) {
        const unsigned long long node_index = stack[--top];
        const AggregateFrontierDeviceNode2D node = nodes[node_index];
        const double dx = node.cx - source_x;
        const double dy = node.cy - source_y;
        const double distance = sqrt(dx * dx + dy * dy);
        const double opening_ratio = distance == 0.0 ? INFINITY : (2.0 * node.half_size) / distance;
        const int contains_source = rtdl_af_node_contains_source(nodes, member_ids, node_index, source_id);
        if (!contains_source && opening_ratio < theta) {
            const unsigned long long out_index = base_row + local_row++;
            output_source_ids[out_index] = source_id;
            output_kind_codes[out_index] = 1ll;
            output_item_ids[out_index] = node.id;
            output_owner_aggregate_ids[out_index] = node.id;
            output_dfs_indices[out_index] = node.dfs_index;
            output_resume_indices[out_index] = node.resume_index >= 0ll ? node.resume_index : -1ll;
            output_metadata_flags[out_index] = 0ll;
            continue;
        }
        if (node.child_begin != node.child_end) {
            const unsigned long long child_count = node.child_end - node.child_begin;
            if (top + (int)child_count > kMaxStack) {
                return;
            }
            for (unsigned long long child_pos = node.child_end; child_pos > node.child_begin; --child_pos) {
                stack[top++] = child_indices[child_pos - 1ull];
            }
            continue;
        }
        for (unsigned long long member_index = node.member_begin; member_index < node.member_end; ++member_index) {
            const long long target_id = member_ids[member_index];
            if (target_id == source_id) {
                continue;
            }
            const unsigned long long out_index = base_row + local_row++;
            output_source_ids[out_index] = source_id;
            output_kind_codes[out_index] = 2ll;
            output_item_ids[out_index] = target_id;
            output_owner_aggregate_ids[out_index] = node.id;
            output_dfs_indices[out_index] = node.dfs_index;
            output_resume_indices[out_index] = node.resume_index >= 0ll ? node.resume_index : -1ll;
            output_metadata_flags[out_index] = 0ll;
        }
    }
}

static __device__ __forceinline__ long long rtdl_af_fused_source_leaf_dfs(
        const long long* target_ids,
        const long long* target_leaf_dfs,
        unsigned long long target_count,
        const long long* source_ids,
        unsigned long long source_index)
{
    const long long source_id = source_ids[source_index];
    if (source_index < target_count && target_ids[source_index] == source_id) {
        return target_leaf_dfs[source_index];
    }
    for (unsigned long long target_index = 0ull; target_index < target_count; ++target_index) {
        if (target_ids[target_index] == source_id) {
            return target_leaf_dfs[target_index];
        }
    }
    return -1ll;
}

static __device__ __forceinline__ int rtdl_af_fused_node_contains_source(
        const AggregateFrontierDeviceNode2D* nodes,
        unsigned long long node_index,
        long long source_leaf_dfs)
{
    if (source_leaf_dfs < 0ll) {
        return 0;
    }
    const AggregateFrontierDeviceNode2D node = nodes[node_index];
    const long long node_end = node.resume_index > node.dfs_index
        ? node.resume_index
        : node.dfs_index + 1ll;
    return source_leaf_dfs >= node.dfs_index && source_leaf_dfs < node_end;
}

extern "C" __global__ void rtdl_aggregate_tree_fused_weighted_vector_sum_2d(
        const AggregateFrontierDeviceNode2D* nodes,
        const unsigned long long* child_indices,
        const unsigned long long* member_indices,
        const unsigned long long* root_indices,
        unsigned long long root_count,
        const long long* target_ids,
        const long long* target_leaf_dfs,
        unsigned long long target_count,
        const double* target_xs,
        const double* target_ys,
        const double* target_weights,
        const long long* source_ids,
        const double* source_xs,
        const double* source_ys,
        const double* source_weights,
        unsigned long long source_count,
        double theta,
        double softening_sq,
        double* out_x,
        double* out_y,
        unsigned long long* out_visited,
        unsigned long long* out_aggregate,
        unsigned long long* out_exact,
        unsigned int* overflow,
        int* status)
{
    const unsigned long long source_index =
        (unsigned long long)blockIdx.x * (unsigned long long)blockDim.x + (unsigned long long)threadIdx.x;
    if (source_index >= source_count) {
        return;
    }

    const int kMaxStack = 256;
    unsigned long long stack[kMaxStack];
    int top = 0;
    if (root_count > (unsigned long long)kMaxStack) {
        atomicExch(overflow, 1u);
        atomicMax(status, 1);
        return;
    }
    for (unsigned long long root_pos = root_count; root_pos > 0ull; --root_pos) {
        stack[top++] = root_indices[root_pos - 1ull];
    }

    const long long source_id = source_ids[source_index];
    const long long source_leaf_dfs = rtdl_af_fused_source_leaf_dfs(
        target_ids, target_leaf_dfs, target_count, source_ids, source_index);
    const double sx = source_xs[source_index];
    const double sy = source_ys[source_index];
    const double smass = source_weights[source_index];
    double sum_x = 0.0;
    double sum_y = 0.0;
    unsigned long long visited = 0ull;
    unsigned long long aggregate_count = 0ull;
    unsigned long long exact_count = 0ull;

    while (top > 0) {
        const unsigned long long node_index = stack[--top];
        const AggregateFrontierDeviceNode2D node = nodes[node_index];
        ++visited;
        const double dx_node = node.cx - sx;
        const double dy_node = node.cy - sy;
        const double distance = sqrt(dx_node * dx_node + dy_node * dy_node);
        const double opening_ratio = distance == 0.0 ? INFINITY : (2.0 * node.half_size) / distance;
        const int contains_source = rtdl_af_fused_node_contains_source(
            nodes, node_index, source_leaf_dfs);
        if (!contains_source && opening_ratio < theta) {
            const double dist_sq = dx_node * dx_node + dy_node * dy_node + softening_sq;
            if (dist_sq != 0.0) {
                const double inv_dist = 1.0 / sqrt(dist_sq);
                const double scale = smass * node.mass * inv_dist * inv_dist * inv_dist;
                sum_x += dx_node * scale;
                sum_y += dy_node * scale;
            }
            ++aggregate_count;
            continue;
        }
        if (node.child_begin != node.child_end) {
            const unsigned long long child_count = node.child_end - node.child_begin;
            if (top + (int)child_count > kMaxStack) {
                atomicExch(overflow, 1u);
                atomicMax(status, 2);
                return;
            }
            for (unsigned long long child_pos = node.child_end; child_pos > node.child_begin; --child_pos) {
                stack[top++] = child_indices[child_pos - 1ull];
            }
            continue;
        }
        for (unsigned long long member_index = node.member_begin; member_index < node.member_end; ++member_index) {
            const unsigned long long target_index = member_indices[member_index];
            const long long target_id = target_ids[target_index];
            if (target_id == source_id) {
                continue;
            }
            const double dx = target_xs[target_index] - sx;
            const double dy = target_ys[target_index] - sy;
            const double dist_sq = dx * dx + dy * dy + softening_sq;
            if (dist_sq != 0.0) {
                const double inv_dist = 1.0 / sqrt(dist_sq);
                const double scale = smass * target_weights[target_index] * inv_dist * inv_dist * inv_dist;
                sum_x += dx * scale;
                sum_y += dy * scale;
            }
            ++exact_count;
        }
    }

    out_x[source_index] = sum_x;
    out_y[source_index] = sum_y;
    out_visited[source_index] = visited;
    out_aggregate[source_index] = aggregate_count;
    out_exact[source_index] = exact_count;
}
)CUDA";

static void ensure_aggregate_frontier_device_columns_2d_kernels()
{
    std::call_once(g_aggregate_frontier_device_columns_2d.init, [&]() {
        const std::string cubin = compile_to_cubin(
            kAggregateFrontierDeviceColumns2DKernelSrc,
            "aggregate_frontier_device_columns_2d_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_aggregate_frontier_device_columns_2d.module, cubin.data()));
        CU_CHECK(cuModuleGetFunction(
            &g_aggregate_frontier_device_columns_2d.count_fn,
            g_aggregate_frontier_device_columns_2d.module,
            "rtdl_aggregate_frontier_count_2d"));
        CU_CHECK(cuModuleGetFunction(
            &g_aggregate_frontier_device_columns_2d.prefix_fn,
            g_aggregate_frontier_device_columns_2d.module,
            "rtdl_aggregate_frontier_prefix_2d"));
        CU_CHECK(cuModuleGetFunction(
            &g_aggregate_frontier_device_columns_2d.write_fn,
            g_aggregate_frontier_device_columns_2d.module,
            "rtdl_aggregate_frontier_write_2d"));
        CU_CHECK(cuModuleGetFunction(
            &g_aggregate_frontier_device_columns_2d.fused_vector_sum_fn,
            g_aggregate_frontier_device_columns_2d.module,
            "rtdl_aggregate_tree_fused_weighted_vector_sum_2d"));
    });
}

static std::unique_ptr<AggregateFrontierDeviceColumnsOutput2D>
allocate_aggregate_frontier_device_columns_output_2d(uint64_t source_count, uint64_t row_capacity)
{
    auto output = std::make_unique<AggregateFrontierDeviceColumnsOutput2D>();
    output->source_count = source_count;
    output->capacity = row_capacity;

    if (row_capacity != 0) {
        const size_t bytes = sizeof(int64_t) * static_cast<size_t>(row_capacity);
        CU_CHECK(cuMemAlloc(&output->source_ids, bytes));
        CU_CHECK(cuMemAlloc(&output->frontier_kind_codes, bytes));
        CU_CHECK(cuMemAlloc(&output->item_ids, bytes));
        CU_CHECK(cuMemAlloc(&output->owner_aggregate_ids, bytes));
        CU_CHECK(cuMemAlloc(&output->dfs_indices, bytes));
        CU_CHECK(cuMemAlloc(&output->resume_indices, bytes));
        CU_CHECK(cuMemAlloc(&output->metadata_flags, bytes));
    }
    CU_CHECK(cuMemAlloc(&output->row_offsets, sizeof(uint64_t) * (static_cast<size_t>(source_count) + 1u)));
    CU_CHECK(cuMemsetD8(output->row_offsets, 0, sizeof(uint64_t) * (static_cast<size_t>(source_count) + 1u)));
    if (source_count != 0) {
        CU_CHECK(cuMemAlloc(&output->per_source_counts, sizeof(uint64_t) * static_cast<size_t>(source_count)));
        CU_CHECK(cuMemsetD8(output->per_source_counts, 0, sizeof(uint64_t) * static_cast<size_t>(source_count)));
    }
    CU_CHECK(cuMemAlloc(&output->row_count, sizeof(uint64_t)));
    CU_CHECK(cuMemAlloc(&output->attempted_count, sizeof(uint64_t)));
    CU_CHECK(cuMemAlloc(&output->overflow, sizeof(uint32_t)));
    const uint64_t zero64 = 0ull;
    const uint32_t zero32 = 0u;
    upload(output->row_count, &zero64, 1);
    upload(output->attempted_count, &zero64, 1);
    upload(output->overflow, &zero32, 1);
    return output;
}

extern "C" int rtdl_optix_prepare_aggregate_frontier_device_columns_2d(
        const RtdlAggregateFrontierNode2D* nodes, size_t node_count,
        const uint64_t* child_offsets, const int64_t* child_ids,
        const uint64_t* member_offsets, const int64_t* member_ids,
        double theta, uint32_t deduplicate_fallback_targets,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("aggregate-frontier device-column prepared_out must not be null");
        *prepared_out = nullptr;
        if (theta <= 0.0 || !std::isfinite(theta))
            throw std::runtime_error("aggregate-frontier device-column theta must be positive and finite");
        if (!nodes && node_count != 0)
            throw std::runtime_error("aggregate-frontier device-column nodes must not be null when node_count is nonzero");
        if (node_count != 0 && (!child_offsets || !member_offsets))
            throw std::runtime_error("aggregate-frontier device-column CSR offsets must not be null when node_count is nonzero");

        (void)get_optix_context();
        auto prepared = std::make_unique<AggregateFrontierDeviceColumnsPrepared2D>();
        prepared->node_count = static_cast<uint64_t>(node_count);
        prepared->theta = theta;
        prepared->deduplicate_fallback_targets = deduplicate_fallback_targets != 0 ? 1u : 0u;
        CUdevice current_device = 0;
        CU_CHECK(cuCtxGetDevice(&current_device));
        prepared->device_ordinal = static_cast<int32_t>(current_device);

        if (node_count == 0) {
            *prepared_out = prepared.release();
            return;
        }

        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (nodes[node_index].dfs_index != static_cast<int64_t>(node_index))
                throw std::runtime_error("aggregate-frontier device-column nodes must be supplied in contiguous DFS order");
            if (nodes[node_index].half_size < 0.0)
                throw std::runtime_error("aggregate-frontier device-column node half_size must be non-negative");
            if (child_offsets[node_index] > child_offsets[node_index + 1] ||
                    member_offsets[node_index] > member_offsets[node_index + 1])
                throw std::runtime_error("aggregate-frontier device-column CSR offsets must be monotonic");
        }
        const uint64_t child_count = child_offsets[node_count];
        const uint64_t member_count = member_offsets[node_count];
        if (child_count != 0 && !child_ids)
            throw std::runtime_error("aggregate-frontier device-column child_ids must not be null when child CSR is non-empty");
        if (member_count != 0 && !member_ids)
            throw std::runtime_error("aggregate-frontier device-column member_ids must not be null when member CSR is non-empty");

        std::unordered_map<int64_t, uint64_t> node_index_by_id;
        node_index_by_id.reserve(node_count);
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            const auto inserted = node_index_by_id.emplace(nodes[node_index].id, static_cast<uint64_t>(node_index));
            if (!inserted.second)
                throw std::runtime_error("aggregate-frontier device-column duplicate node id");
        }

        std::vector<uint64_t> child_indices(static_cast<size_t>(child_count));
        std::unordered_set<int64_t> child_id_set;
        child_id_set.reserve(static_cast<size_t>(child_count));
        for (uint64_t child_index = 0; child_index < child_count; ++child_index) {
            const int64_t child_id = child_ids[child_index];
            const auto found = node_index_by_id.find(child_id);
            if (found == node_index_by_id.end())
                throw std::runtime_error("aggregate-frontier device-column child id is not present in node array");
            child_indices[static_cast<size_t>(child_index)] = found->second;
            child_id_set.insert(child_id);
        }

        std::vector<uint64_t> root_indices;
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (child_id_set.find(nodes[node_index].id) == child_id_set.end())
                root_indices.push_back(static_cast<uint64_t>(node_index));
        }
        if (root_indices.empty())
            throw std::runtime_error("aggregate-frontier device-column tree must contain at least one root");

        std::vector<AggregateFrontierDeviceNode2D> device_nodes(node_count);
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            device_nodes[node_index] = {
                nodes[node_index].id,
                nodes[node_index].cx,
                nodes[node_index].cy,
                nodes[node_index].half_size,
                0.0,
                nodes[node_index].dfs_index,
                nodes[node_index].resume_index >= 0 ? nodes[node_index].resume_index : -1,
                child_offsets[node_index],
                child_offsets[node_index + 1],
                member_offsets[node_index],
                member_offsets[node_index + 1],
                nodes[node_index].is_leaf != 0 ? 1u : 0u,
            };
        }

        prepared->child_count = child_count;
        prepared->member_count = member_count;
        prepared->root_count = static_cast<uint64_t>(root_indices.size());
        CU_CHECK(cuMemAlloc(&prepared->nodes, sizeof(AggregateFrontierDeviceNode2D) * device_nodes.size()));
        upload(prepared->nodes, device_nodes.data(), device_nodes.size());
        if (!child_indices.empty()) {
            CU_CHECK(cuMemAlloc(&prepared->child_indices, sizeof(uint64_t) * child_indices.size()));
            upload(prepared->child_indices, child_indices.data(), child_indices.size());
        }
        if (member_count != 0) {
            CU_CHECK(cuMemAlloc(&prepared->member_ids, sizeof(int64_t) * static_cast<size_t>(member_count)));
            upload(prepared->member_ids, member_ids, static_cast<size_t>(member_count));
        }
        CU_CHECK(cuMemAlloc(&prepared->root_indices, sizeof(uint64_t) * root_indices.size()));
        upload(prepared->root_indices, root_indices.data(), root_indices.size());

        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_aggregate_frontier_device_columns_2d(
        void* prepared_handle,
        uint64_t source_ids_device_ptr,
        uint64_t source_x_device_ptr,
        uint64_t source_y_device_ptr,
        size_t source_count,
        uint64_t row_capacity,
        RtdlAggregateFrontierDeviceColumns2D* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_handle)
            throw std::runtime_error("aggregate-frontier device-column prepared handle must not be null");
        if (!columns_out)
            throw std::runtime_error("aggregate-frontier device-column columns_out must not be null");
        if (source_count != 0 && (source_ids_device_ptr == 0 || source_x_device_ptr == 0 || source_y_device_ptr == 0))
            throw std::runtime_error("aggregate-frontier device-column source device pointers must be nonzero when source_count is nonzero");
        *columns_out = {};

        auto* prepared = reinterpret_cast<AggregateFrontierDeviceColumnsPrepared2D*>(prepared_handle);
        std::lock_guard<std::mutex> lock(prepared->mutex);
        (void)get_optix_context();
        ensure_aggregate_frontier_device_columns_2d_kernels();

        auto output = allocate_aggregate_frontier_device_columns_output_2d(
            static_cast<uint64_t>(source_count),
            row_capacity);
        const auto traversal_start = std::chrono::steady_clock::now();
        CUstream stream = 0;

        if (source_count != 0 && prepared->root_count != 0) {
            CUdeviceptr nodes_ptr = prepared->nodes;
            CUdeviceptr child_indices_ptr = prepared->child_indices;
            CUdeviceptr member_ids_ptr = prepared->member_ids;
            CUdeviceptr root_indices_ptr = prepared->root_indices;
            CUdeviceptr source_ids_ptr = static_cast<CUdeviceptr>(source_ids_device_ptr);
            CUdeviceptr source_x_ptr = static_cast<CUdeviceptr>(source_x_device_ptr);
            CUdeviceptr source_y_ptr = static_cast<CUdeviceptr>(source_y_device_ptr);
            uint64_t root_count = prepared->root_count;
            uint64_t source_count64 = static_cast<uint64_t>(source_count);
            double theta = prepared->theta;
            CUdeviceptr per_source_counts_ptr = output->per_source_counts;
            CUdeviceptr overflow_ptr = output->overflow;
            void* count_args[] = {
                &nodes_ptr,
                &child_indices_ptr,
                &member_ids_ptr,
                &root_indices_ptr,
                &root_count,
                &source_ids_ptr,
                &source_x_ptr,
                &source_y_ptr,
                &source_count64,
                &theta,
                &per_source_counts_ptr,
                &overflow_ptr,
            };
            const unsigned threads = 128u;
            const unsigned blocks = static_cast<unsigned>((source_count + threads - 1u) / threads);
            CU_CHECK(cuLaunchKernel(
                g_aggregate_frontier_device_columns_2d.count_fn,
                blocks, 1, 1,
                threads, 1, 1,
                0, stream, count_args, nullptr));
        }

        {
            CUdeviceptr counts_ptr = output->per_source_counts;
            uint64_t source_count64 = static_cast<uint64_t>(source_count);
            uint64_t capacity64 = row_capacity;
            CUdeviceptr offsets_ptr = output->row_offsets;
            CUdeviceptr row_count_ptr = output->row_count;
            CUdeviceptr attempted_count_ptr = output->attempted_count;
            CUdeviceptr overflow_ptr = output->overflow;
            void* prefix_args[] = {
                &counts_ptr,
                &source_count64,
                &capacity64,
                &offsets_ptr,
                &row_count_ptr,
                &attempted_count_ptr,
                &overflow_ptr,
            };
            CU_CHECK(cuLaunchKernel(
                g_aggregate_frontier_device_columns_2d.prefix_fn,
                1, 1, 1,
                1, 1, 1,
                0, stream, prefix_args, nullptr));
        }

        if (source_count != 0 && row_capacity != 0 && prepared->root_count != 0) {
            CUdeviceptr nodes_ptr = prepared->nodes;
            CUdeviceptr child_indices_ptr = prepared->child_indices;
            CUdeviceptr member_ids_ptr = prepared->member_ids;
            CUdeviceptr root_indices_ptr = prepared->root_indices;
            uint64_t root_count = prepared->root_count;
            CUdeviceptr source_ids_ptr = static_cast<CUdeviceptr>(source_ids_device_ptr);
            CUdeviceptr source_x_ptr = static_cast<CUdeviceptr>(source_x_device_ptr);
            CUdeviceptr source_y_ptr = static_cast<CUdeviceptr>(source_y_device_ptr);
            uint64_t source_count64 = static_cast<uint64_t>(source_count);
            double theta = prepared->theta;
            CUdeviceptr offsets_ptr = output->row_offsets;
            CUdeviceptr output_source_ids_ptr = output->source_ids;
            CUdeviceptr output_kind_codes_ptr = output->frontier_kind_codes;
            CUdeviceptr output_item_ids_ptr = output->item_ids;
            CUdeviceptr output_owner_aggregate_ids_ptr = output->owner_aggregate_ids;
            CUdeviceptr output_dfs_indices_ptr = output->dfs_indices;
            CUdeviceptr output_resume_indices_ptr = output->resume_indices;
            CUdeviceptr output_metadata_flags_ptr = output->metadata_flags;
            CUdeviceptr overflow_ptr = output->overflow;
            void* write_args[] = {
                &nodes_ptr,
                &child_indices_ptr,
                &member_ids_ptr,
                &root_indices_ptr,
                &root_count,
                &source_ids_ptr,
                &source_x_ptr,
                &source_y_ptr,
                &source_count64,
                &theta,
                &offsets_ptr,
                &output_source_ids_ptr,
                &output_kind_codes_ptr,
                &output_item_ids_ptr,
                &output_owner_aggregate_ids_ptr,
                &output_dfs_indices_ptr,
                &output_resume_indices_ptr,
                &output_metadata_flags_ptr,
                &overflow_ptr,
            };
            const unsigned threads = 128u;
            const unsigned blocks = static_cast<unsigned>((source_count + threads - 1u) / threads);
            CU_CHECK(cuLaunchKernel(
                g_aggregate_frontier_device_columns_2d.write_fn,
                blocks, 1, 1,
                threads, 1, 1,
                0, stream, write_args, nullptr));
        }

        CU_CHECK(cuStreamSynchronize(stream));
        const auto traversal_end = std::chrono::steady_clock::now();

        uint64_t row_count = 0;
        uint64_t attempted_count = 0;
        uint32_t overflow = 0u;
        download(&row_count, output->row_count, 1);
        download(&attempted_count, output->attempted_count, 1);
        download(&overflow, output->overflow, 1);

        columns_out->source_ids_device_ptr = static_cast<uint64_t>(output->source_ids);
        columns_out->frontier_kind_codes_device_ptr = static_cast<uint64_t>(output->frontier_kind_codes);
        columns_out->item_ids_device_ptr = static_cast<uint64_t>(output->item_ids);
        columns_out->owner_aggregate_ids_device_ptr = static_cast<uint64_t>(output->owner_aggregate_ids);
        columns_out->dfs_indices_device_ptr = static_cast<uint64_t>(output->dfs_indices);
        columns_out->resume_indices_device_ptr = static_cast<uint64_t>(output->resume_indices);
        columns_out->metadata_flags_device_ptr = static_cast<uint64_t>(output->metadata_flags);
        columns_out->row_offsets_device_ptr = static_cast<uint64_t>(output->row_offsets);
        columns_out->row_count = row_count;
        columns_out->attempted_count = attempted_count;
        columns_out->capacity = row_capacity;
        columns_out->source_count = static_cast<uint64_t>(source_count);
        columns_out->overflow = overflow;
        columns_out->device_ordinal = prepared->device_ordinal;
        columns_out->owner_handle = prepared;
        columns_out->traversal_seconds = std::chrono::duration<double>(
            traversal_end - traversal_start).count();
        columns_out->row_count_device_ptr = static_cast<uint64_t>(output->row_count);
        columns_out->attempted_count_device_ptr = static_cast<uint64_t>(output->attempted_count);
        columns_out->overflow_device_ptr = static_cast<uint64_t>(output->overflow);

        prepared->last_output = std::move(output);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_aggregate_frontier_device_columns_2d(void* prepared)
{
    delete reinterpret_cast<AggregateFrontierDeviceColumnsPrepared2D*>(prepared);
}

extern "C" int rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d(
        uint64_t target_ids_device_ptr,
        uint64_t target_x_device_ptr,
        uint64_t target_y_device_ptr,
        uint64_t target_weight_device_ptr,
        size_t target_count,
        const RtdlAggregateFrontierNode2D* nodes, size_t node_count,
        const uint64_t* child_offsets, const int64_t* child_ids,
        const uint64_t* member_offsets, const int64_t* member_ids,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("aggregate-tree fused vector-sum prepared_out must not be null");
        *prepared_out = nullptr;
        if (target_count != 0 && (
                    target_ids_device_ptr == 0
                    || target_x_device_ptr == 0
                    || target_y_device_ptr == 0
                    || target_weight_device_ptr == 0))
            throw std::runtime_error("aggregate-tree fused vector-sum target device pointers must be nonzero when target_count is nonzero");
        if (!nodes && node_count != 0)
            throw std::runtime_error("aggregate-tree fused vector-sum nodes must not be null when node_count is nonzero");
        if (node_count != 0 && (!child_offsets || !member_offsets))
            throw std::runtime_error("aggregate-tree fused vector-sum CSR offsets must not be null when node_count is nonzero");
        if (node_count != 0 && child_offsets && child_offsets[node_count] != 0 && !child_ids)
            throw std::runtime_error("aggregate-tree fused vector-sum child_ids must not be null when child CSR is non-empty");
        if (node_count != 0 && member_offsets && member_offsets[node_count] != 0 && !member_ids)
            throw std::runtime_error("aggregate-tree fused vector-sum member_ids must not be null when member CSR is non-empty");

        (void)get_optix_context();
        auto prepared = std::make_unique<AggregateTreeFusedWeightedVectorSumPrepared2D>();
        prepared->target_ids = static_cast<CUdeviceptr>(target_ids_device_ptr);
        prepared->target_x = static_cast<CUdeviceptr>(target_x_device_ptr);
        prepared->target_y = static_cast<CUdeviceptr>(target_y_device_ptr);
        prepared->target_weight = static_cast<CUdeviceptr>(target_weight_device_ptr);
        prepared->target_count = static_cast<uint64_t>(target_count);
        prepared->node_count = static_cast<uint64_t>(node_count);
        CUdevice current_device = 0;
        CU_CHECK(cuCtxGetDevice(&current_device));
        prepared->device_ordinal = static_cast<int32_t>(current_device);

        if (node_count == 0) {
            *prepared_out = prepared.release();
            return;
        }

        std::vector<int64_t> target_ids(static_cast<size_t>(target_count));
        std::vector<double> target_weights(static_cast<size_t>(target_count));
        if (target_count != 0) {
            download(target_ids.data(), static_cast<CUdeviceptr>(target_ids_device_ptr), target_ids.size());
            download(target_weights.data(), static_cast<CUdeviceptr>(target_weight_device_ptr), target_weights.size());
        }
        std::unordered_map<int64_t, uint64_t> target_index_by_id;
        target_index_by_id.reserve(target_ids.size());
        for (size_t target_index = 0; target_index < target_ids.size(); ++target_index) {
            const auto inserted = target_index_by_id.emplace(
                target_ids[target_index],
                static_cast<uint64_t>(target_index));
            if (!inserted.second)
                throw std::runtime_error("aggregate-tree fused vector-sum duplicate target id");
        }

        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (nodes[node_index].dfs_index != static_cast<int64_t>(node_index))
                throw std::runtime_error("aggregate-tree fused vector-sum nodes must be supplied in contiguous DFS order");
            if (nodes[node_index].half_size < 0.0)
                throw std::runtime_error("aggregate-tree fused vector-sum node half_size must be non-negative");
            if (child_offsets[node_index] > child_offsets[node_index + 1] ||
                    member_offsets[node_index] > member_offsets[node_index + 1])
                throw std::runtime_error("aggregate-tree fused vector-sum CSR offsets must be monotonic");
        }
        const uint64_t child_count = child_offsets[node_count];
        const uint64_t member_count = member_offsets[node_count];

        std::unordered_map<int64_t, uint64_t> node_index_by_id;
        node_index_by_id.reserve(node_count);
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            const auto inserted = node_index_by_id.emplace(nodes[node_index].id, static_cast<uint64_t>(node_index));
            if (!inserted.second)
                throw std::runtime_error("aggregate-tree fused vector-sum duplicate node id");
        }

        std::vector<uint64_t> child_indices(static_cast<size_t>(child_count));
        std::unordered_set<int64_t> child_id_set;
        child_id_set.reserve(static_cast<size_t>(child_count));
        for (uint64_t child_index = 0; child_index < child_count; ++child_index) {
            const int64_t child_id = child_ids[child_index];
            const auto found = node_index_by_id.find(child_id);
            if (found == node_index_by_id.end())
                throw std::runtime_error("aggregate-tree fused vector-sum child id is not present in node array");
            child_indices[static_cast<size_t>(child_index)] = found->second;
            child_id_set.insert(child_id);
        }

        std::vector<uint64_t> member_indices(static_cast<size_t>(member_count));
        for (uint64_t member_index = 0; member_index < member_count; ++member_index) {
            const int64_t member_id = member_ids[member_index];
            const auto found = target_index_by_id.find(member_id);
            if (found == target_index_by_id.end())
                throw std::runtime_error("aggregate-tree fused vector-sum member id is not present in target id column");
            member_indices[static_cast<size_t>(member_index)] = found->second;
        }

        std::vector<int64_t> target_leaf_dfs(static_cast<size_t>(target_count), -1);
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (nodes[node_index].is_leaf == 0)
                continue;
            for (uint64_t member_pos = member_offsets[node_index];
                    member_pos < member_offsets[node_index + 1]; ++member_pos) {
                const uint64_t target_index = member_indices[static_cast<size_t>(member_pos)];
                target_leaf_dfs[static_cast<size_t>(target_index)] = nodes[node_index].dfs_index;
            }
        }
        for (size_t target_index = 0; target_index < target_leaf_dfs.size(); ++target_index) {
            if (target_leaf_dfs[target_index] < 0)
                throw std::runtime_error("aggregate-tree fused vector-sum target id is not assigned to a leaf node");
        }

        std::vector<uint64_t> root_indices;
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (child_id_set.find(nodes[node_index].id) == child_id_set.end())
                root_indices.push_back(static_cast<uint64_t>(node_index));
        }
        if (root_indices.empty())
            throw std::runtime_error("aggregate-tree fused vector-sum tree must contain at least one root");

        std::vector<AggregateFrontierDeviceNode2D> device_nodes(node_count);
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            double node_mass = 0.0;
            for (uint64_t member_pos = member_offsets[node_index]; member_pos < member_offsets[node_index + 1]; ++member_pos) {
                node_mass += target_weights[static_cast<size_t>(member_indices[static_cast<size_t>(member_pos)])];
            }
            device_nodes[node_index] = {
                nodes[node_index].id,
                nodes[node_index].cx,
                nodes[node_index].cy,
                nodes[node_index].half_size,
                node_mass,
                nodes[node_index].dfs_index,
                nodes[node_index].resume_index >= 0 ? nodes[node_index].resume_index : -1,
                child_offsets[node_index],
                child_offsets[node_index + 1],
                member_offsets[node_index],
                member_offsets[node_index + 1],
                nodes[node_index].is_leaf != 0 ? 1u : 0u,
            };
        }

        prepared->child_count = child_count;
        prepared->member_count = member_count;
        prepared->root_count = static_cast<uint64_t>(root_indices.size());
        CU_CHECK(cuMemAlloc(&prepared->nodes, sizeof(AggregateFrontierDeviceNode2D) * device_nodes.size()));
        upload(prepared->nodes, device_nodes.data(), device_nodes.size());
        if (!child_indices.empty()) {
            CU_CHECK(cuMemAlloc(&prepared->child_indices, sizeof(uint64_t) * child_indices.size()));
            upload(prepared->child_indices, child_indices.data(), child_indices.size());
        }
        if (!member_indices.empty()) {
            CU_CHECK(cuMemAlloc(&prepared->member_indices, sizeof(uint64_t) * member_indices.size()));
            upload(prepared->member_indices, member_indices.data(), member_indices.size());
        }
        if (!target_leaf_dfs.empty()) {
            CU_CHECK(cuMemAlloc(&prepared->target_leaf_dfs, sizeof(int64_t) * target_leaf_dfs.size()));
            upload(prepared->target_leaf_dfs, target_leaf_dfs.data(), target_leaf_dfs.size());
        }
        CU_CHECK(cuMemAlloc(&prepared->root_indices, sizeof(uint64_t) * root_indices.size()));
        upload(prepared->root_indices, root_indices.data(), root_indices.size());

        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_aggregate_tree_fused_weighted_vector_sum_2d(
        void* prepared,
        uint64_t source_ids_device_ptr,
        uint64_t source_x_device_ptr,
        uint64_t source_y_device_ptr,
        uint64_t source_weight_device_ptr,
        size_t source_count,
        double theta,
        double softening,
        RtdlAggregateTreeFusedWeightedVectorSum2DOutput* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!columns_out)
            throw std::runtime_error("aggregate-tree fused vector-sum columns_out must not be null");
        *columns_out = {};
        if (!prepared)
            throw std::runtime_error("aggregate-tree fused vector-sum prepared handle must not be null");
        if (source_count != 0 && (
                    source_ids_device_ptr == 0
                    || source_x_device_ptr == 0
                    || source_y_device_ptr == 0
                    || source_weight_device_ptr == 0))
            throw std::runtime_error("aggregate-tree fused vector-sum source device pointers must be nonzero when source_count is nonzero");
        if (theta <= 0.0 || !std::isfinite(theta))
            throw std::runtime_error("aggregate-tree fused vector-sum theta must be positive and finite");
        if (softening < 0.0 || !std::isfinite(softening))
            throw std::runtime_error("aggregate-tree fused vector-sum softening must be non-negative and finite");

        auto* prepared_owner = reinterpret_cast<AggregateTreeFusedWeightedVectorSumPrepared2D*>(prepared);
        std::lock_guard<std::mutex> lock(prepared_owner->mutex);
        (void)get_optix_context();
        ensure_aggregate_frontier_device_columns_2d_kernels();

        auto output = std::make_unique<AggregateTreeFusedWeightedVectorSumOutput2D>();
        output->source_count = static_cast<uint64_t>(source_count);
        if (source_count != 0) {
            CU_CHECK(cuMemAlloc(&output->vector_x, sizeof(double) * static_cast<size_t>(source_count)));
            CU_CHECK(cuMemAlloc(&output->vector_y, sizeof(double) * static_cast<size_t>(source_count)));
            CU_CHECK(cuMemAlloc(&output->visited_counts, sizeof(uint64_t) * static_cast<size_t>(source_count)));
            CU_CHECK(cuMemAlloc(&output->aggregate_counts, sizeof(uint64_t) * static_cast<size_t>(source_count)));
            CU_CHECK(cuMemAlloc(&output->exact_counts, sizeof(uint64_t) * static_cast<size_t>(source_count)));
        }
        CUdeviceptr overflow_device = 0;
        CUdeviceptr status_device = 0;
        CU_CHECK(cuMemAlloc(&overflow_device, sizeof(uint32_t)));
        CU_CHECK(cuMemAlloc(&status_device, sizeof(int32_t)));
        const uint32_t zero32 = 0u;
        const int32_t zero_i32 = 0;
        upload(overflow_device, &zero32, 1);
        upload(status_device, &zero_i32, 1);

        const auto traversal_start = std::chrono::steady_clock::now();
        CUstream stream = 0;
        if (source_count != 0 && prepared_owner->root_count != 0) {
            CUdeviceptr nodes_ptr = prepared_owner->nodes;
            CUdeviceptr child_indices_ptr = prepared_owner->child_indices;
            CUdeviceptr member_indices_ptr = prepared_owner->member_indices;
            CUdeviceptr root_indices_ptr = prepared_owner->root_indices;
            uint64_t root_count = prepared_owner->root_count;
            CUdeviceptr target_ids_ptr = prepared_owner->target_ids;
            CUdeviceptr target_leaf_dfs_ptr = prepared_owner->target_leaf_dfs;
            uint64_t target_count64 = prepared_owner->target_count;
            CUdeviceptr target_x_ptr = prepared_owner->target_x;
            CUdeviceptr target_y_ptr = prepared_owner->target_y;
            CUdeviceptr target_weight_ptr = prepared_owner->target_weight;
            CUdeviceptr source_ids_ptr = static_cast<CUdeviceptr>(source_ids_device_ptr);
            CUdeviceptr source_x_ptr = static_cast<CUdeviceptr>(source_x_device_ptr);
            CUdeviceptr source_y_ptr = static_cast<CUdeviceptr>(source_y_device_ptr);
            CUdeviceptr source_weight_ptr = static_cast<CUdeviceptr>(source_weight_device_ptr);
            uint64_t source_count64 = static_cast<uint64_t>(source_count);
            double theta_value = theta;
            double softening_sq = softening * softening;
            CUdeviceptr vector_x_ptr = output->vector_x;
            CUdeviceptr vector_y_ptr = output->vector_y;
            CUdeviceptr visited_counts_ptr = output->visited_counts;
            CUdeviceptr aggregate_counts_ptr = output->aggregate_counts;
            CUdeviceptr exact_counts_ptr = output->exact_counts;
            void* fused_args[] = {
                &nodes_ptr,
                &child_indices_ptr,
                &member_indices_ptr,
                &root_indices_ptr,
                &root_count,
                &target_ids_ptr,
                &target_leaf_dfs_ptr,
                &target_count64,
                &target_x_ptr,
                &target_y_ptr,
                &target_weight_ptr,
                &source_ids_ptr,
                &source_x_ptr,
                &source_y_ptr,
                &source_weight_ptr,
                &source_count64,
                &theta_value,
                &softening_sq,
                &vector_x_ptr,
                &vector_y_ptr,
                &visited_counts_ptr,
                &aggregate_counts_ptr,
                &exact_counts_ptr,
                &overflow_device,
                &status_device,
            };
            unsigned threads = 128u;
            if (const char* raw_threads = std::getenv("RTDL_OPTIX_AGG_TREE_FUSED_THREADS");
                    raw_threads && raw_threads[0] != '\0') {
                char* end = nullptr;
                const unsigned long parsed = std::strtoul(raw_threads, &end, 10);
                if (end != raw_threads && *end == '\0' &&
                        (parsed == 32ul || parsed == 64ul || parsed == 128ul ||
                         parsed == 256ul || parsed == 512ul || parsed == 1024ul)) {
                    threads = static_cast<unsigned>(parsed);
                }
            }
            const unsigned blocks = static_cast<unsigned>((source_count + threads - 1u) / threads);
            CU_CHECK(cuLaunchKernel(
                g_aggregate_frontier_device_columns_2d.fused_vector_sum_fn,
                blocks, 1, 1,
                threads, 1, 1,
                0, stream, fused_args, nullptr));
        }
        CU_CHECK(cuStreamSynchronize(stream));
        const auto traversal_end = std::chrono::steady_clock::now();

        uint32_t overflow = 0u;
        int32_t status = 0;
        download(&overflow, overflow_device, 1);
        download(&status, status_device, 1);
        cuMemFree(status_device);
        cuMemFree(overflow_device);

        output->overflow = overflow;
        output->diagnostic_status_code = status;
        columns_out->source_ids_device_ptr = source_ids_device_ptr;
        columns_out->vector_x_device_ptr = static_cast<uint64_t>(output->vector_x);
        columns_out->vector_y_device_ptr = static_cast<uint64_t>(output->vector_y);
        columns_out->visited_counts_device_ptr = static_cast<uint64_t>(output->visited_counts);
        columns_out->aggregate_counts_device_ptr = static_cast<uint64_t>(output->aggregate_counts);
        columns_out->exact_counts_device_ptr = static_cast<uint64_t>(output->exact_counts);
        columns_out->source_count = static_cast<uint64_t>(source_count);
        columns_out->diagnostic_status_code = status;
        columns_out->overflow = overflow;
        columns_out->device_ordinal = prepared_owner->device_ordinal;
        columns_out->owner_handle = prepared_owner;
        columns_out->bvh_build_seconds = 0.0;
        columns_out->traversal_seconds = std::chrono::duration<double>(
            traversal_end - traversal_start).count();
        columns_out->continuation_seconds = 0.0;
        columns_out->copy_seconds = 0.0;

        prepared_owner->last_output = std::move(output);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_aggregate_tree_fused_weighted_vector_sum_2d(void* prepared)
{
    delete reinterpret_cast<AggregateTreeFusedWeightedVectorSumPrepared2D*>(prepared);
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
        double event_ms = 0.0;
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
    double merge_event_ms = 0.0;
    double merge_sync_ms = 0.0;
    double merge_metadata_download_ms = 0.0;
    double carry_copy_ms = 0.0;
    double final_copy_ms = 0.0;
    double final_pair_materialize_launch_ms = 0.0;
    double final_pair_materialize_event_ms = 0.0;
    double final_pair_mark_sync_ms = 0.0;
    double final_pair_mark_event_ms = 0.0;
    double final_pair_mark_host_wait_ms = 0.0;
    double final_pair_pre_mark_wait_ms = 0.0;
    double final_pair_prefix_host_ms = 0.0;
    double final_pair_compact_launch_ms = 0.0;
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
                << "\"merge_event_ms\":" << merge_event_ms << ","
                << "\"merge_sync_ms\":" << merge_sync_ms << ","
                << "\"merge_metadata_download_ms\":" << merge_metadata_download_ms << ","
                << "\"carry_copy_ms\":" << carry_copy_ms << ","
                << "\"final_copy_ms\":" << final_copy_ms << ","
                << "\"final_pair_materialize_launch_ms\":" << final_pair_materialize_launch_ms << ","
                << "\"final_pair_materialize_event_ms\":" << final_pair_materialize_event_ms << ","
                << "\"final_pair_mark_sync_ms\":" << final_pair_mark_sync_ms << ","
                << "\"final_pair_mark_event_ms\":" << final_pair_mark_event_ms << ","
                << "\"final_pair_mark_host_wait_ms\":" << final_pair_mark_host_wait_ms << ","
                << "\"final_pair_pre_mark_wait_ms\":" << final_pair_pre_mark_wait_ms << ","
                << "\"final_pair_prefix_host_ms\":" << final_pair_prefix_host_ms << ","
                << "\"final_pair_compact_launch_ms\":" << final_pair_compact_launch_ms << ","
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
                    << "\"event_ms\":" << level.event_ms << ","
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
    constexpr uint64_t min_payload_copy_reduction = 4;
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

static bool collect_k_use_final_pair_mark_event_diagnostic()
{
    return collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_FINAL_PAIR_MARK_EVENT_DIAGNOSTIC");
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

static bool collect_k_defer_merge_sync_diagnostic()
{
    return collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC");
}

static bool collect_k_extended_128_tile_diagnostic()
{
    return collect_k_env_enabled("RTDL_OPTIX_COLLECT_K_EXTENDED_128_TILE_DIAGNOSTIC");
}

static constexpr size_t kCollectKRowWidth2BaseMaxTiledCandidates = 131072;
static constexpr size_t kCollectKRowWidth2ExtendedMaxTiledCandidates = 262144;
static constexpr size_t kCollectKRowWidth2BaseMaxTileSegments = 64;
static constexpr size_t kCollectKRowWidth2ExtendedMaxTileSegments = 128;
static constexpr size_t kCollectKRowWidth2BaseMaxPrefixBlocks = 512;
static constexpr size_t kCollectKRowWidth2ExtendedMaxPrefixBlocks = 1024;

struct CollectKRowWidth2Workspace {
    size_t max_tiled_candidates = 0;
    size_t max_tile_segments = 0;
    size_t max_prefix_blocks = 0;
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

    void release()
    {
        if (final_overflowed_device) cuMemFree(final_overflowed_device);
        if (final_emitted_device) cuMemFree(final_emitted_device);
        if (final_pair_offsets) cuMemFree(final_pair_offsets);
        if (final_block_offsets) cuMemFree(final_block_offsets);
        if (final_block_counts) cuMemFree(final_block_counts);
        if (final_marks) cuMemFree(final_marks);
        if (final_merged_rows) cuMemFree(final_merged_rows);
        if (merge_second_counts_device) cuMemFree(merge_second_counts_device);
        if (merge_first_counts_device) cuMemFree(merge_first_counts_device);
        if (merge_output_rows_device) cuMemFree(merge_output_rows_device);
        if (merge_second_rows_device) cuMemFree(merge_second_rows_device);
        if (merge_first_rows_device) cuMemFree(merge_first_rows_device);
        if (merge_overflowed_device) cuMemFree(merge_overflowed_device);
        if (merge_emitted_device) cuMemFree(merge_emitted_device);
        if (tile_overflowed_device) cuMemFree(tile_overflowed_device);
        if (tile_emitted_device) cuMemFree(tile_emitted_device);
        if (temp_stage_b) cuMemFree(temp_stage_b);
        if (temp_stage_a) cuMemFree(temp_stage_a);
        *this = CollectKRowWidth2Workspace{};
    }

    void ensure(
        size_t requested_max_tiled_candidates,
        size_t requested_max_tile_segments,
        size_t requested_max_prefix_blocks)
    {
        if (max_tiled_candidates >= requested_max_tiled_candidates
            && max_tile_segments >= requested_max_tile_segments
            && max_prefix_blocks >= requested_max_prefix_blocks)
            return;
        if (max_tiled_candidates != 0)
            release();
        max_tiled_candidates = requested_max_tiled_candidates;
        max_tile_segments = requested_max_tile_segments;
        max_prefix_blocks = requested_max_prefix_blocks;
        CU_CHECK(cuMemAlloc(&temp_stage_a, sizeof(int64_t) * max_tiled_candidates * 2));
        CU_CHECK(cuMemAlloc(&temp_stage_b, sizeof(int64_t) * max_tiled_candidates * 2));
        CU_CHECK(cuMemAlloc(&tile_emitted_device, sizeof(size_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&tile_overflowed_device, sizeof(uint32_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&merge_emitted_device, sizeof(size_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&merge_overflowed_device, sizeof(uint32_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&merge_first_rows_device, sizeof(uint64_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&merge_second_rows_device, sizeof(uint64_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&merge_output_rows_device, sizeof(uint64_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&merge_first_counts_device, sizeof(size_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&merge_second_counts_device, sizeof(size_t) * max_tile_segments));
        CU_CHECK(cuMemAlloc(&final_merged_rows, sizeof(int64_t) * max_tiled_candidates * 2));
        CU_CHECK(cuMemAlloc(&final_marks, sizeof(uint32_t) * max_tiled_candidates));
        CU_CHECK(cuMemAlloc(&final_block_counts, sizeof(uint32_t) * max_prefix_blocks));
        CU_CHECK(cuMemAlloc(&final_block_offsets, sizeof(uint32_t) * max_prefix_blocks));
        CU_CHECK(cuMemAlloc(&final_pair_offsets, sizeof(uint32_t) * max_tile_segments));
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
                std::string cubin = compile_to_cubin(
                    kCollectKBoundedI64RowWidth2SortKernelSrc,
                    "collect_k_bounded_i64_row_width2_sort_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_sort.module, cubin.data()));
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
        const bool use_extended_128_tile_diagnostic =
            collect_k_use_fastest_candidate() || collect_k_extended_128_tile_diagnostic();
        const size_t row_width2_max_tiled_candidates =
            use_extended_128_tile_diagnostic
                ? kCollectKRowWidth2ExtendedMaxTiledCandidates
                : kCollectKRowWidth2BaseMaxTiledCandidates;
        if (row_width == 2 && candidate_count > 4096 && candidate_count <= row_width2_max_tiled_candidates) {
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
                std::string cubin = compile_to_cubin(
                    kCollectKBoundedI64RowWidth2SortKernelSrc,
                    "collect_k_bounded_i64_row_width2_sort_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_sort.module, cubin.data()));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_sort.fn,
                    g_collect_k_i64_row_width2_sort.module,
                    "collect_k_bounded_i64_row_width2_sort"));
            });
            if (use_cub_tile_sort) {
                std::call_once(g_collect_k_i64_row_width2_cub_sort.init, [&]() {
                    std::string cubin = compile_to_cubin(
                        kCollectKBoundedI64RowWidth2CubSortKernelSrc,
                        "collect_k_bounded_i64_row_width2_cub_sort_kernel.cu");
                    CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_cub_sort.module, cubin.data()));
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
                std::string cubin = compile_to_cubin(
                    kCollectKBoundedI64RowWidth2MergeTwoKernelSrc,
                    "collect_k_bounded_i64_row_width2_merge_two_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_merge_two.module, cubin.data()));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_merge_two.fn,
                    g_collect_k_i64_row_width2_merge_two.module,
                    "collect_k_bounded_i64_row_width2_merge_two"));
            });
            std::call_once(g_collect_k_i64_row_width2_merge_level.init, [&]() {
                std::string cubin = compile_to_cubin(
                    kCollectKBoundedI64RowWidth2MergeLevelKernelSrc,
                    "collect_k_bounded_i64_row_width2_merge_level_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_merge_level.module, cubin.data()));
                CU_CHECK(cuModuleGetFunction(
                    &g_collect_k_i64_row_width2_merge_level.fn,
                    g_collect_k_i64_row_width2_merge_level.module,
                    "collect_k_bounded_i64_row_width2_merge_level"));
            });
            std::call_once(g_collect_k_i64_row_width2_final_materialize.init, [&]() {
                std::string cubin = compile_to_cubin(
                    kCollectKBoundedI64RowWidth2FinalCompactKernelSrc,
                    "collect_k_bounded_i64_row_width2_final_compact_kernel.cu");
                CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_final_materialize.module, cubin.data()));
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
                    &g_collect_k_i64_row_width2_four_way_materialize_mark_counts_derived.fn,
                    g_collect_k_i64_row_width2_final_materialize.module,
                    "collect_k_bounded_i64_row_width2_four_way_materialize_mark_counts_derived"));
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

            const size_t max_tiled_candidates = row_width2_max_tiled_candidates;
            const size_t max_tile_segments = use_extended_128_tile_diagnostic
                ? kCollectKRowWidth2ExtendedMaxTileSegments
                : kCollectKRowWidth2BaseMaxTileSegments;
            const size_t max_prefix_blocks = use_extended_128_tile_diagnostic
                ? kCollectKRowWidth2ExtendedMaxPrefixBlocks
                : kCollectKRowWidth2BaseMaxPrefixBlocks;
            profile.tile_count = tile_count;
            if (tile_count > max_tile_segments)
                throw std::runtime_error("COLLECT_K_BOUNDED tile descriptor capacity exceeded");
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
                g_collect_k_row_width2_workspace.ensure(
                    max_tiled_candidates,
                    max_tile_segments,
                    max_prefix_blocks);
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
                sizeof(size_t) * max_tile_segments);
            DeviceSlot tile_overflowed_device = make_slot(
                g_collect_k_row_width2_workspace.tile_overflowed_device,
                sizeof(uint32_t) * max_tile_segments);
            DeviceSlot merge_emitted_device = make_slot(
                g_collect_k_row_width2_workspace.merge_emitted_device,
                sizeof(size_t) * max_tile_segments);
            DeviceSlot merge_overflowed_device = make_slot(
                g_collect_k_row_width2_workspace.merge_overflowed_device,
                sizeof(uint32_t) * max_tile_segments);
            DeviceSlot merge_first_rows_device = make_slot(
                g_collect_k_row_width2_workspace.merge_first_rows_device,
                sizeof(uint64_t) * max_tile_segments);
            DeviceSlot merge_second_rows_device = make_slot(
                g_collect_k_row_width2_workspace.merge_second_rows_device,
                sizeof(uint64_t) * max_tile_segments);
            DeviceSlot merge_output_rows_device = make_slot(
                g_collect_k_row_width2_workspace.merge_output_rows_device,
                sizeof(uint64_t) * max_tile_segments);
            DeviceSlot merge_first_counts_device = make_slot(
                g_collect_k_row_width2_workspace.merge_first_counts_device,
                sizeof(size_t) * max_tile_segments);
            DeviceSlot merge_second_counts_device = make_slot(
                g_collect_k_row_width2_workspace.merge_second_counts_device,
                sizeof(size_t) * max_tile_segments);
            DeviceSlot final_merged_rows = make_slot(
                g_collect_k_row_width2_workspace.final_merged_rows,
                sizeof(int64_t) * max_tiled_candidates * 2);
            DeviceSlot final_marks = make_slot(
                g_collect_k_row_width2_workspace.final_marks,
                sizeof(uint32_t) * max_tiled_candidates);
            DeviceSlot final_block_counts = make_slot(
                g_collect_k_row_width2_workspace.final_block_counts,
                sizeof(uint32_t) * max_prefix_blocks);
            DeviceSlot final_block_offsets = make_slot(
                g_collect_k_row_width2_workspace.final_block_offsets,
                sizeof(uint32_t) * max_prefix_blocks);
            DeviceSlot final_pair_offsets = make_slot(
                g_collect_k_row_width2_workspace.final_pair_offsets,
                sizeof(uint32_t) * max_tile_segments);
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
            struct PendingMergeEvent {
                CUevent start = nullptr;
                CUevent stop = nullptr;
                size_t level_index = 0;
            };
            std::vector<PendingMergeEvent> pending_merge_events;
            auto resolve_pending_merge_events = [&]() {
                for (PendingMergeEvent& event : pending_merge_events) {
                    if (event.start && event.stop && event.level_index < profile.merge_level_profile.size()) {
                        float elapsed_ms = 0.0f;
                        CU_CHECK(cuEventElapsedTime(&elapsed_ms, event.start, event.stop));
                        profile.merge_level_profile[event.level_index].event_ms = static_cast<double>(elapsed_ms);
                        profile.merge_event_ms += static_cast<double>(elapsed_ms);
                    }
                    if (event.start)
                        CU_CHECK(cuEventDestroy(event.start));
                    if (event.stop)
                        CU_CHECK(cuEventDestroy(event.stop));
                }
                pending_merge_events.clear();
            };
            auto launch_parallel_compact_pair = [&](CUdeviceptr first_rows, size_t first_count,
                                                    CUdeviceptr second_rows, size_t second_count,
                                                    CUdeviceptr output_rows, size_t output_capacity,
                                                    size_t* final_count_out) {
                const bool is_final_output = output_rows == rows_out;
                size_t total = first_count + second_count;
                const unsigned threads = 256;
                const unsigned blocks = static_cast<unsigned>((total + threads - 1) / threads);
                if (blocks > max_prefix_blocks)
                    throw std::runtime_error("COLLECT_K_BOUNDED final compact block capacity exceeded");
                const bool use_final_pair_mark_event =
                    profile.enabled
                    && is_final_output
                    && collect_k_use_final_pair_mark_event_diagnostic();
                CUevent materialize_event_start = nullptr;
                CUevent materialize_event_stop = nullptr;
                if (use_final_pair_mark_event) {
                    CU_CHECK(cuEventCreate(&materialize_event_start, CU_EVENT_DEFAULT));
                    CU_CHECK(cuEventCreate(&materialize_event_stop, CU_EVENT_DEFAULT));
                    CU_CHECK(cuEventRecord(materialize_event_start, nullptr));
                }
                auto final_pair_stage_start = CollectKStageProfile::Clock::now();
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
                if (use_final_pair_mark_event)
                    CU_CHECK(cuEventRecord(materialize_event_stop, nullptr));
                if (profile.enabled && is_final_output)
                    profile.final_pair_materialize_launch_ms +=
                        CollectKStageProfile::elapsed_ms(final_pair_stage_start);

                final_pair_stage_start = CollectKStageProfile::Clock::now();
                CUevent mark_event_start = nullptr;
                CUevent mark_event_stop = nullptr;
                if (use_final_pair_mark_event) {
                    CU_CHECK(cuEventCreate(&mark_event_start, CU_EVENT_DEFAULT));
                    CU_CHECK(cuEventCreate(&mark_event_stop, CU_EVENT_DEFAULT));
                    CU_CHECK(cuEventRecord(mark_event_start, nullptr));
                }
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
                if (use_final_pair_mark_event)
                    CU_CHECK(cuEventRecord(mark_event_stop, nullptr));
                CU_CHECK(cuStreamSynchronize(nullptr));
                resolve_pending_merge_events();
                if (profile.enabled && is_final_output) {
                    const double mark_sync_ms = CollectKStageProfile::elapsed_ms(final_pair_stage_start);
                    profile.final_pair_mark_sync_ms += mark_sync_ms;
                    if (use_final_pair_mark_event) {
                        float materialize_event_ms = 0.0f;
                        float mark_event_ms = 0.0f;
                        CU_CHECK(cuEventElapsedTime(&materialize_event_ms, materialize_event_start, materialize_event_stop));
                        CU_CHECK(cuEventElapsedTime(&mark_event_ms, mark_event_start, mark_event_stop));
                        profile.final_pair_materialize_event_ms += static_cast<double>(materialize_event_ms);
                        profile.final_pair_mark_event_ms += static_cast<double>(mark_event_ms);
                        profile.final_pair_mark_host_wait_ms +=
                            std::max(0.0, mark_sync_ms - static_cast<double>(mark_event_ms));
                        profile.final_pair_pre_mark_wait_ms +=
                            std::max(0.0, mark_sync_ms
                                - static_cast<double>(materialize_event_ms)
                                - static_cast<double>(mark_event_ms));
                    }
                }
                if (materialize_event_start)
                    CU_CHECK(cuEventDestroy(materialize_event_start));
                if (materialize_event_stop)
                    CU_CHECK(cuEventDestroy(materialize_event_stop));
                if (mark_event_start)
                    CU_CHECK(cuEventDestroy(mark_event_start));
                if (mark_event_stop)
                    CU_CHECK(cuEventDestroy(mark_event_stop));

                final_pair_stage_start = CollectKStageProfile::Clock::now();
                std::vector<uint32_t> block_counts(max_prefix_blocks);
                std::vector<uint32_t> block_offsets(max_prefix_blocks);
                download(block_counts.data(), final_block_counts.ptr, blocks);
                uint32_t running_total = 0;
                for (unsigned block_index = 0; block_index < blocks; ++block_index) {
                    block_offsets[block_index] = running_total;
                    running_total += block_counts[block_index];
                }
                upload(final_block_offsets.ptr, block_offsets.data(), blocks);
                *final_count_out = static_cast<size_t>(running_total);
                if (profile.enabled && is_final_output)
                    profile.final_pair_prefix_host_ms +=
                        CollectKStageProfile::elapsed_ms(final_pair_stage_start);

                final_pair_stage_start = CollectKStageProfile::Clock::now();
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
                if (profile.enabled && is_final_output)
                    profile.final_pair_compact_launch_ms +=
                        CollectKStageProfile::elapsed_ms(final_pair_stage_start);
            };
            auto launch_parallel_compact_pair_counts = [&](CUdeviceptr first_rows,
                                                           CUdeviceptr second_rows,
                                                           CUdeviceptr counts_device,
                                                           size_t scan_capacity,
                                                           CUdeviceptr output_rows,
                                                           size_t output_capacity,
                                                           size_t* final_count_out) {
                const bool is_final_output = output_rows == rows_out;
                const unsigned threads = 256;
                const unsigned blocks = static_cast<unsigned>((scan_capacity + threads - 1) / threads);
                if (blocks > max_prefix_blocks)
                    throw std::runtime_error("COLLECT_K_BOUNDED final compact block capacity exceeded");
                const bool use_final_pair_mark_event =
                    profile.enabled
                    && is_final_output
                    && collect_k_use_final_pair_mark_event_diagnostic();
                CUevent materialize_event_start = nullptr;
                CUevent materialize_event_stop = nullptr;
                if (use_final_pair_mark_event) {
                    CU_CHECK(cuEventCreate(&materialize_event_start, CU_EVENT_DEFAULT));
                    CU_CHECK(cuEventCreate(&materialize_event_stop, CU_EVENT_DEFAULT));
                    CU_CHECK(cuEventRecord(materialize_event_start, nullptr));
                }
                auto final_pair_stage_start = CollectKStageProfile::Clock::now();
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
                if (use_final_pair_mark_event)
                    CU_CHECK(cuEventRecord(materialize_event_stop, nullptr));
                if (profile.enabled && is_final_output)
                    profile.final_pair_materialize_launch_ms +=
                        CollectKStageProfile::elapsed_ms(final_pair_stage_start);

                final_pair_stage_start = CollectKStageProfile::Clock::now();
                CUevent mark_event_start = nullptr;
                CUevent mark_event_stop = nullptr;
                if (use_final_pair_mark_event) {
                    CU_CHECK(cuEventCreate(&mark_event_start, CU_EVENT_DEFAULT));
                    CU_CHECK(cuEventCreate(&mark_event_stop, CU_EVENT_DEFAULT));
                    CU_CHECK(cuEventRecord(mark_event_start, nullptr));
                }
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
                if (use_final_pair_mark_event)
                    CU_CHECK(cuEventRecord(mark_event_stop, nullptr));
                CU_CHECK(cuStreamSynchronize(nullptr));
                resolve_pending_merge_events();
                if (profile.enabled && is_final_output) {
                    const double mark_sync_ms = CollectKStageProfile::elapsed_ms(final_pair_stage_start);
                    profile.final_pair_mark_sync_ms += mark_sync_ms;
                    if (use_final_pair_mark_event) {
                        float materialize_event_ms = 0.0f;
                        float mark_event_ms = 0.0f;
                        CU_CHECK(cuEventElapsedTime(&materialize_event_ms, materialize_event_start, materialize_event_stop));
                        CU_CHECK(cuEventElapsedTime(&mark_event_ms, mark_event_start, mark_event_stop));
                        profile.final_pair_materialize_event_ms += static_cast<double>(materialize_event_ms);
                        profile.final_pair_mark_event_ms += static_cast<double>(mark_event_ms);
                        profile.final_pair_mark_host_wait_ms +=
                            std::max(0.0, mark_sync_ms - static_cast<double>(mark_event_ms));
                        profile.final_pair_pre_mark_wait_ms +=
                            std::max(0.0, mark_sync_ms
                                - static_cast<double>(materialize_event_ms)
                                - static_cast<double>(mark_event_ms));
                    }
                }
                if (materialize_event_start)
                    CU_CHECK(cuEventDestroy(materialize_event_start));
                if (materialize_event_stop)
                    CU_CHECK(cuEventDestroy(materialize_event_stop));
                if (mark_event_start)
                    CU_CHECK(cuEventDestroy(mark_event_start));
                if (mark_event_stop)
                    CU_CHECK(cuEventDestroy(mark_event_stop));

                final_pair_stage_start = CollectKStageProfile::Clock::now();
                std::vector<uint32_t> block_counts(max_prefix_blocks);
                std::vector<uint32_t> block_offsets(max_prefix_blocks);
                download(block_counts.data(), final_block_counts.ptr, blocks);
                uint32_t running_total = 0;
                for (unsigned block_index = 0; block_index < blocks; ++block_index) {
                    block_offsets[block_index] = running_total;
                    running_total += block_counts[block_index];
                }
                upload(final_block_offsets.ptr, block_offsets.data(), blocks);
                *final_count_out = static_cast<size_t>(running_total);
                if (profile.enabled && is_final_output)
                    profile.final_pair_prefix_host_ms +=
                        CollectKStageProfile::elapsed_ms(final_pair_stage_start);

                final_pair_stage_start = CollectKStageProfile::Clock::now();
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
                if (profile.enabled && is_final_output)
                    profile.final_pair_compact_launch_ms +=
                        CollectKStageProfile::elapsed_ms(final_pair_stage_start);
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
                if (pair_count > max_tile_segments || total_blocks > max_prefix_blocks)
                    throw std::runtime_error("COLLECT_K_BOUNDED compact-level descriptor capacity exceeded");
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

                    std::vector<uint32_t> block_counts(max_prefix_blocks);
                    std::vector<uint32_t> block_offsets(max_prefix_blocks);
                    std::vector<uint32_t> pair_offsets(max_tile_segments);
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
                (use_candidate_bundle_for_case || collect_k_use_derived_carry_alias_diagnostic())
                && use_device_level_counts;

            std::vector<size_t> tile_emitted(max_tile_segments);
            std::vector<uint32_t> tile_overflowed(max_tile_segments);
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
                CUevent merge_event_start = nullptr;
                CUevent merge_event_stop = nullptr;
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
                        std::vector<size_t> merge_first_counts(max_tile_segments);
                        std::vector<size_t> merge_second_counts(max_tile_segments);
                        std::vector<uint64_t> merge_first_rows(max_tile_segments);
                        std::vector<uint64_t> merge_second_rows(max_tile_segments);
                        std::vector<uint64_t> merge_output_rows(max_tile_segments);
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
                        const bool use_merge_event =
                            profile.enabled && collect_k_use_final_pair_mark_event_diagnostic();
                        if (use_merge_event) {
                            CU_CHECK(cuEventCreate(&merge_event_start, CU_EVENT_DEFAULT));
                            CU_CHECK(cuEventCreate(&merge_event_stop, CU_EVENT_DEFAULT));
                            CU_CHECK(cuEventRecord(merge_event_start, nullptr));
                        }
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
                        if (use_merge_event)
                            CU_CHECK(cuEventRecord(merge_event_stop, nullptr));
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

                    const bool can_defer_merge_sync =
                        collect_k_defer_merge_sync_diagnostic()
                        && use_batched_compact_level
                        && current_rows.size() != 2
                        // Deferral is only safe while per-level counts and
                        // offsets remain device-resident; otherwise the host
                        // needs this synchronization before reading metadata.
                        && use_device_prefix_compact
                        && use_device_level_counts;
                    if (!can_defer_merge_sync) {
                        auto merge_sync_start = CollectKStageProfile::Clock::now();
                        CU_CHECK(cuStreamSynchronize(nullptr));
                        level_profile.sync_ms = CollectKStageProfile::elapsed_ms(merge_sync_start);
                        if (profile.enabled)
                            profile.merge_sync_ms += level_profile.sync_ms;
                    }

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
                    if (profile.enabled && merge_event_start && merge_event_stop) {
                        pending_merge_events.push_back({
                            merge_event_start,
                            merge_event_stop,
                            profile.merge_level_profile.size() - 1,
                        });
                    }

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
                std::vector<uint64_t> merge_first_rows(max_tile_segments);
                std::vector<uint64_t> merge_second_rows(max_tile_segments);
                std::vector<uint64_t> merge_output_rows(max_tile_segments);
                std::vector<size_t> merge_first_counts(max_tile_segments);
                std::vector<size_t> merge_second_counts(max_tile_segments);
                if (use_device_level_counts) {
                    current_counts.resize(current_rows.size());
                    auto count_download_start = CollectKStageProfile::Clock::now();
                    download(current_counts.data(), current_counts_level_device, current_rows.size());
                    level_profile.metadata_ms += CollectKStageProfile::elapsed_ms(count_download_start);
                    *d2h_transfers_out += static_cast<uint64_t>(current_rows.size());
                    profile.metadata_fields_downloaded += static_cast<uint64_t>(current_rows.size());
                }
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

                std::vector<size_t> merge_emitted(max_tile_segments);
                std::vector<uint32_t> merge_overflowed(max_tile_segments);
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
                if (use_device_level_counts) {
                    upload(next_counts_level_device, next_counts.data(), next_counts.size());
                    *h2d_transfers_out += static_cast<uint64_t>(next_counts.size());
                    std::swap(current_counts_level_device, next_counts_level_device);
                }

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
            std::string cubin = compile_to_cubin(
                kCollectKBoundedI64KernelSrc,
                "collect_k_bounded_i64_kernel.cu");
            CU_CHECK(cuModuleLoadData(&g_collect_k_i64.module, cubin.data()));
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

extern "C" int rtdl_optix_prepare_segment_shape_anyhit_rows_2d(
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

extern "C" int rtdl_optix_run_prepared_segment_shape_anyhit_rows_2d(
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

extern "C" void rtdl_optix_destroy_prepared_segment_shape_anyhit_rows_2d(void* prepared)
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
        if (std::getenv("RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_CUDA") != nullptr) {
            run_fixed_radius_neighbors_cuda_3d(
                query_points, query_count,
                search_points, search_count,
                radius, k_max,
                rows_out, row_count_out);
        } else if (std::getenv("RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_RT") != nullptr) {
            run_fixed_radius_neighbors_rt_3d(
                query_points, query_count,
                search_points, search_count,
                radius, k_max,
                rows_out, row_count_out);
        } else {
            run_fixed_radius_neighbors_grid_cuda_3d(
                query_points, query_count,
                search_points, search_count,
                radius, k_max,
                rows_out, row_count_out);
        }
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_fixed_radius_neighbors_3d(
        const RtdlPoint3D* search_points, size_t search_count,
        double max_radius,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!search_points && search_count != 0)
            throw std::runtime_error("search_points pointer must not be null when search_count is nonzero");
        if (max_radius <= 0.0)
            throw std::runtime_error("fixed_radius_neighbors_3d max_radius must be positive");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_neighbors_3d search_count exceeds uint32 limit");
        *prepared_out = nullptr;
        *prepared_out = prepare_fixed_radius_neighbors_grid_3d_optix(
            search_points, search_count, max_radius);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_fixed_radius_neighbors_3d(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_fixed_radius_neighbors_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            query_points, query_count, radius, k_max, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_exact_fixed_radius_neighbors_3d(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_exact_fixed_radius_neighbors_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            query_points, query_count, radius, k_max, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlKnnNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_ranked_fixed_radius_neighbors_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            query_points, query_count, radius, k_max, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusRankedNeighborSummary** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            query_points, query_count, radius, k_max, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_fixed_radius_query_points_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        void** prepared_queries_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_queries_out)
            throw std::runtime_error("prepared_queries_out must not be null");
        if (!query_points && query_count != 0)
            throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
        if (query_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
        *prepared_queries_out = nullptr;
        *prepared_queries_out = prepare_fixed_radius_query_points_grid_3d_optix(
            query_points, query_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_aggregate_prepared_ranked_fixed_radius_neighbor_summaries_3d(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusRankedNeighborAggregate* aggregate_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!aggregate_out)
            throw std::runtime_error("aggregate_out must not be null");
        *aggregate_out = aggregate_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            query_points, query_count, radius, k_max);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_aggregate_prepared_ranked_fixed_radius_neighbor_summaries_3d_f32(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusRankedNeighborAggregate* aggregate_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!aggregate_out)
            throw std::runtime_error("aggregate_out must not be null");
        *aggregate_out = aggregate_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            query_points, query_count, radius, k_max, true);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32(
        void* prepared,
        void* prepared_queries,
        double radius,
        size_t k_max,
        RtdlFixedRadiusRankedNeighborAggregate* aggregate_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!aggregate_out)
            throw std::runtime_error("aggregate_out must not be null");
        *aggregate_out = aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            reinterpret_cast<PreparedFixedRadiusQueryPoints3D*>(prepared_queries),
            radius, k_max);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch(
        void* prepared,
        void* prepared_queries,
        const double* radii,
        const size_t* k_values,
        size_t request_count,
        RtdlFixedRadiusRankedNeighborAggregate* aggregates_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            reinterpret_cast<PreparedFixedRadiusQueryPoints3D*>(prepared_queries),
            radii,
            k_values,
            request_count,
        aggregates_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_aggregate_self_query_ranked_fixed_radius_neighbor_summaries_3d_f32_batch(
        void* prepared,
        const double* radii,
        const size_t* k_values,
        size_t request_count,
        RtdlFixedRadiusRankedNeighborAggregate* aggregates_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        aggregate_self_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            radii,
            k_values,
            request_count,
            aggregates_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_fixed_radius_ranked_summary_aggregate_batch_graph_3d(
        void* prepared,
        void* prepared_queries,
        const double* radii,
        const size_t* k_values,
        size_t request_count,
        void** graph_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!graph_out)
            throw std::runtime_error("graph_out must not be null");
        *graph_out = nullptr;
        *graph_out = prepare_fixed_radius_ranked_summary_aggregate_batch_graph_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            reinterpret_cast<PreparedFixedRadiusQueryPoints3D*>(prepared_queries),
            radii,
            k_values,
            request_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_fixed_radius_self_query_ranked_summary_aggregate_batch_graph_3d(
        void* prepared,
        const double* radii,
        const size_t* k_values,
        size_t request_count,
        void** graph_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!graph_out)
            throw std::runtime_error("graph_out must not be null");
        *graph_out = nullptr;
        *graph_out = prepare_fixed_radius_self_query_ranked_summary_aggregate_batch_graph_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            radii,
            k_values,
            request_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_replay_fixed_radius_ranked_summary_aggregate_batch_graph_3d(
        void* graph,
        RtdlFixedRadiusRankedNeighborAggregate* aggregates_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        replay_fixed_radius_ranked_summary_aggregate_batch_graph_3d_optix(
            reinterpret_cast<PreparedFixedRadiusRankedSummaryAggregateBatchGraph3D*>(graph),
            aggregates_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d(
        void* graph,
        uint64_t* partials_device_ptr_out,
        size_t* partial_count_out,
        size_t* request_count_out,
        size_t* query_block_count_out,
        uint64_t* cuda_stream_ptr_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        launch_fixed_radius_ranked_summary_aggregate_batch_graph_device_partials_3d_optix(
            reinterpret_cast<PreparedFixedRadiusRankedSummaryAggregateBatchGraph3D*>(graph),
            partials_device_ptr_out,
            partial_count_out,
            request_count_out,
            query_block_count_out,
            cuda_stream_ptr_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_update_fixed_radius_ranked_summary_aggregate_batch_graph_3d(
        void* graph,
        const double* radii,
        const size_t* k_values,
        size_t request_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        update_fixed_radius_ranked_summary_aggregate_batch_graph_3d_optix(
            reinterpret_cast<PreparedFixedRadiusRankedSummaryAggregateBatchGraph3D*>(graph),
            radii,
            k_values,
            request_count);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_fixed_radius_ranked_summary_aggregate_batch_graph_3d(void* graph)
{
    delete reinterpret_cast<PreparedFixedRadiusRankedSummaryAggregateBatchGraph3D*>(graph);
}

extern "C" int rtdl_optix_count_prepared_fixed_radius_neighbors_3d(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!row_count_out)
            throw std::runtime_error("row_count_out must not be null");
        *row_count_out = count_prepared_fixed_radius_neighbors_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            query_points, query_count, radius, k_max);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_summarize_prepared_fixed_radius_neighbors_3d(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborSummary* summary_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!summary_out)
            throw std::runtime_error("summary_out must not be null");
        *summary_out = summarize_prepared_fixed_radius_neighbors_grid_3d_optix(
            reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared),
            query_points, query_count, radius, k_max);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d(void* prepared)
{
    delete reinterpret_cast<PreparedFixedRadiusNeighborsGrid3D*>(prepared);
}

extern "C" void rtdl_optix_destroy_prepared_fixed_radius_query_points_3d(void* prepared_queries)
{
    delete reinterpret_cast<PreparedFixedRadiusQueryPoints3D*>(prepared_queries);
}

extern "C" int rtdl_optix_prepare_fixed_radius_count_threshold_3d(
        const RtdlPoint3D* search_points, size_t search_count,
        double max_radius,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!search_points && search_count != 0)
            throw std::runtime_error("search_points pointer must not be null when search_count is nonzero");
        if (max_radius <= 0.0)
            throw std::runtime_error("fixed_radius_count_threshold_3d max_radius must be positive");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_count_threshold_3d search_count exceeds uint32 limit");
        *prepared_out = nullptr;
        *prepared_out = prepare_fixed_radius_count_threshold_3d_rt_optix(
            search_points, search_count, max_radius);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_device_outputs(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t threshold,
        uint32_t* query_ids_out,
        uint32_t* neighbor_counts_out,
        uint32_t* threshold_flags_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_fixed_radius_count_threshold_3d_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            query_points, query_count, radius, threshold,
            query_ids_out, neighbor_counts_out, threshold_flags_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_self_device_outputs(
        void* prepared,
        double radius,
        size_t threshold,
        uint32_t* query_ids_out,
        uint32_t* neighbor_counts_out,
        uint32_t* threshold_flags_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_fixed_radius_count_threshold_3d_self_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, threshold,
            query_ids_out, neighbor_counts_out, threshold_flags_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_fixed_radius_adjacency_3d_device_outputs(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        const int64_t* edge_offsets,
        int32_t* neighbor_indices_out,
        size_t neighbor_index_capacity,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_fixed_radius_adjacency_3d_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            query_points, query_count, radius,
            edge_offsets, neighbor_indices_out, neighbor_index_capacity);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        size_t query_index_offset,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            query_points, query_count, query_index_offset, radius,
            predicate_flags, parent_out, fallback_candidate_out, nullptr, 0, true, false, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs_with_options(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        size_t query_index_offset,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint32_t same_root_culling,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            query_points, query_count, query_index_offset, radius,
            predicate_flags, parent_out, fallback_candidate_out, nullptr,
            0, same_root_culling != 0u, false, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_device_outputs_with_execution_options(
        void* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        size_t query_index_offset,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint32_t same_root_culling,
        uint32_t direct_side_effect,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            query_points, query_count, query_index_offset, radius,
            predicate_flags, parent_out, fallback_candidate_out, nullptr,
            0, same_root_culling != 0u, direct_side_effect != 0u, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs(
        void* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, predicate_flags, parent_out, fallback_candidate_out, nullptr, 0, true, false, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_options(
        void* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint32_t same_root_culling,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, predicate_flags, parent_out, fallback_candidate_out, nullptr,
            0, same_root_culling != 0u, false, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_execution_options(
        void* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint32_t same_root_culling,
        uint32_t direct_side_effect,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, predicate_flags, parent_out, fallback_candidate_out, nullptr,
            0, same_root_culling != 0u, direct_side_effect != 0u, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry(
        void* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, predicate_flags, parent_out, fallback_candidate_out, telemetry_out, 4, true, false, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_options(
        void* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        uint32_t same_root_culling,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, predicate_flags, parent_out, fallback_candidate_out, telemetry_out,
            4, same_root_culling != 0u, false, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry_and_execution_options(
        void* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        uint32_t same_root_culling,
        uint32_t direct_side_effect,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, predicate_flags, parent_out, fallback_candidate_out, telemetry_out,
            4, same_root_culling != 0u, direct_side_effect != 0u, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_extended_telemetry_and_execution_options(
        void* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        size_t telemetry_count,
        uint32_t same_root_culling,
        uint32_t direct_side_effect,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, predicate_flags, parent_out, fallback_candidate_out, telemetry_out,
            telemetry_count, same_root_culling != 0u, direct_side_effect != 0u, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_extended_telemetry_and_execution_options_on_stream(
        void* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        size_t telemetry_count,
        uint32_t same_root_culling,
        uint32_t direct_side_effect,
        size_t item_count,
        uint64_t cuda_stream_ptr,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix_on_stream(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            radius, predicate_flags, parent_out, fallback_candidate_out, telemetry_out,
            telemetry_count, same_root_culling != 0u, direct_side_effect != 0u, item_count,
            cuda_stream_ptr);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs(
        void* prepared,
        size_t query_start,
        size_t query_count,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            query_start, query_count, radius, predicate_flags, parent_out,
            fallback_candidate_out, telemetry_out, 4, true, false, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_options(
        void* prepared,
        size_t query_start,
        size_t query_count,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        uint32_t same_root_culling,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            query_start, query_count, radius, predicate_flags, parent_out,
            fallback_candidate_out, telemetry_out, 4, same_root_culling != 0u, false, item_count);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_with_execution_options(
        void* prepared,
        size_t query_start,
        size_t query_count,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        uint32_t same_root_culling,
        uint32_t direct_side_effect,
        size_t item_count,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared),
            query_start, query_count, radius, predicate_flags, parent_out,
            fallback_candidate_out, telemetry_out,
            4, same_root_culling != 0u, direct_side_effect != 0u, item_count);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d(void* prepared)
{
    delete reinterpret_cast<PreparedFixedRadiusCountThreshold3DRt*>(prepared);
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

extern "C" int rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns(
        const uint32_t* search_ids,
        const double* search_x,
        const double* search_y,
        size_t search_count,
        double max_radius,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if ((!search_ids || !search_x || !search_y) && search_count != 0)
            throw std::runtime_error("search device column pointers must not be null when search_count is nonzero");
        if (max_radius < 0.0)
            throw std::runtime_error("fixed_radius_count_threshold max_radius must be non-negative");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_count_threshold search_count exceeds uint32 limit");
        *prepared_out = nullptr;
        *prepared_out = prepare_fixed_radius_count_threshold_2d_device_search_columns_optix(
            search_ids, search_x, search_y, search_count, max_radius);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_prepare_fixed_radius_count_threshold_2d_device_search_columns_on_stream(
        const uint32_t* search_ids,
        const double* search_x,
        const double* search_y,
        size_t search_count,
        double max_radius,
        uint64_t cuda_stream_ptr,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if ((!search_ids || !search_x || !search_y) && search_count != 0)
            throw std::runtime_error("search device column pointers must not be null when search_count is nonzero");
        if (max_radius < 0.0)
            throw std::runtime_error("fixed_radius_count_threshold max_radius must be non-negative");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("fixed_radius_count_threshold search_count exceeds uint32 limit");
        *prepared_out = nullptr;
        *prepared_out = prepare_fixed_radius_count_threshold_2d_device_search_columns_on_stream_optix(
            search_ids, search_x, search_y, search_count, max_radius, cuda_stream_ptr);
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

extern "C" int rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns(
        void* prepared,
        const uint32_t* query_ids,
        const double* query_x,
        const double* query_y,
        size_t query_count,
        double radius,
        size_t threshold,
        uint32_t* query_ids_out,
        uint32_t* neighbor_counts_out,
        uint32_t* threshold_flags_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_fixed_radius_count_threshold_2d_device_query_columns_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold2D*>(prepared),
            query_ids, query_x, query_y, query_count, radius, threshold,
            query_ids_out, neighbor_counts_out, threshold_flags_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns_on_stream(
        void* prepared,
        const uint32_t* query_ids,
        const double* query_x,
        const double* query_y,
        size_t query_count,
        double radius,
        size_t threshold,
        uint32_t* query_ids_out,
        uint32_t* neighbor_counts_out,
        uint32_t* threshold_flags_out,
        uint64_t cuda_stream_ptr,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_fixed_radius_count_threshold_2d_device_query_columns_on_stream_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold2D*>(prepared),
            query_ids, query_x, query_y, query_count, radius, threshold,
            query_ids_out, neighbor_counts_out, threshold_flags_out,
            cuda_stream_ptr);
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

extern "C" int rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double radius,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_fixed_radius_nearest_witness_2d_optix(
            reinterpret_cast<PreparedFixedRadiusCountThreshold2D*>(prepared),
            query_points, query_count, radius, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d(void* prepared)
{
    delete reinterpret_cast<PreparedFixedRadiusCountThreshold2D*>(prepared);
}

extern "C" int rtdl_optix_prepare_point_group_nearest_witness_2d(
        const RtdlPoint* search_points, size_t search_count,
        const RtdlPointGroupBounds2D* groups, size_t group_count,
        double max_radius,
        void** prepared_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!prepared_out)
            throw std::runtime_error("prepared_out must not be null");
        if (!search_points && search_count != 0)
            throw std::runtime_error("point_group search_points pointer must not be null when search_count is nonzero");
        if (!groups && group_count != 0)
            throw std::runtime_error("point_group groups pointer must not be null when group_count is nonzero");
        if (max_radius < 0.0)
            throw std::runtime_error("point_group_nearest_witness max_radius must be non-negative");
        if (search_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("point_group_nearest_witness search_count exceeds uint32 limit");
        if (group_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("point_group_nearest_witness group_count exceeds uint32 limit");
        *prepared_out = nullptr;
        *prepared_out = prepare_point_group_nearest_witness_2d_optix(
            search_points, search_count, groups, group_count, max_radius);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_count_prepared_point_group_threshold_reached_2d(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double radius,
        size_t threshold,
        size_t* threshold_reached_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        count_prepared_point_group_threshold_reached_2d_optix(
            reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            query_points, query_count, radius, threshold, threshold_reached_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_point_group_threshold_flags_2d(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double radius,
        size_t threshold,
        uint32_t* threshold_flags_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_point_group_threshold_flags_2d_optix(
            reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            query_points, query_count, radius, threshold, threshold_flags_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_prepared_point_group_nearest_witness_2d(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double radius,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_prepared_point_group_nearest_witness_2d_optix(
            reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            query_points, query_count, radius, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double radius,
        uint32_t* query_ids_out,
        uint32_t* neighbor_ids_out,
        double* distances_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_point_group_nearest_witness_2d_device_columns_optix(
            reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            query_points, query_count, radius,
            query_ids_out, neighbor_ids_out, distances_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_query_columns(
        void* prepared,
        const uint32_t* query_ids,
        const double* query_x,
        const double* query_y,
        size_t query_count,
        double radius,
        uint32_t* query_ids_out,
        uint32_t* neighbor_ids_out,
        double* distances_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        write_prepared_point_group_nearest_witness_2d_device_query_columns_optix(
            reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            query_ids, query_x, query_y, query_count, radius,
            query_ids_out, neighbor_ids_out, distances_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double radius,
        RtdlFixedRadiusNeighborRow* row_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        reduce_prepared_point_group_nearest_max_distance_2d_optix(
            reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            query_points, query_count, radius, row_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d(
        void* prepared,
        const RtdlPoint* query_points, size_t query_count,
        double threshold_radius,
        size_t threshold,
        double witness_radius,
        RtdlFixedRadiusNeighborRow* row_out,
        size_t* active_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        reduce_prepared_point_group_nearest_max_distance_active_frontier_2d_optix(
            reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            query_points, query_count, threshold_radius, threshold, witness_radius,
            row_out, active_count_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_destroy_prepared_point_group_nearest_witness_2d(void* prepared)
{
    delete reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared);
}

extern "C" int rtdl_optix_run_k_closest_hits(
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
        run_k_closest_hits_cuda(
            query_points, query_count,
            search_points, search_count,
            k,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_k_closest_hits_3d(
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
        run_k_closest_hits_cuda_3d(
            query_points, query_count,
            search_points, search_count,
            k,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_frontier_edge_traversal_packet(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t edge_index_count,
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
                column_indices, edge_index_count,
                frontier, frontier_count,
                visited_vertices, visited_count,
                dedupe,
                rows_out, row_count_out);
        } else {
            run_bfs_expand_optix_host_indexed(
                row_offsets, row_offset_count,
                column_indices, edge_index_count,
                frontier, frontier_count,
                visited_vertices, visited_count,
                dedupe,
                rows_out, row_count_out);
        }
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_edge_neighbor_intersection_packet(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t edge_index_count,
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
            run_triangle_cycle_candidates_optix_graph_ray(
                row_offsets, row_offset_count,
                column_indices, edge_index_count,
                seeds, seed_count,
                enforce_id_ascending,
                unique,
                rows_out, row_count_out);
        } else {
            run_triangle_cycle_candidates_optix_host_indexed(
                row_offsets, row_offset_count,
                column_indices, edge_index_count,
                seeds, seed_count,
                enforce_id_ascending,
                unique,
                rows_out, row_count_out);
        }
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_conjunctive_scan(
        const RtdlColumnField* fields, size_t field_count,
        const RtdlColumnScalar* row_values, size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        RtdlColumnRowIdRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_columnar_multi_predicate_scan_optix(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_grouped_count(
        const RtdlColumnField* fields, size_t field_count,
        const RtdlColumnScalar* row_values, size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        RtdlGroupedCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_columnar_grouped_count_optix(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            group_key_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_run_grouped_sum(
        const RtdlColumnField* fields, size_t field_count,
        const RtdlColumnScalar* row_values, size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlGroupedSumRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_columnar_grouped_sum_optix(
            fields, field_count,
            row_values, row_count,
            clauses, clause_count,
            group_key_field,
            value_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_payload_create(
        const RtdlColumnField* fields, size_t field_count,
        const RtdlColumnScalar* row_values, size_t row_count,
        const char* const* primary_fields, size_t primary_field_count,
        RtdlOptixColumnarPayload** dataset_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!dataset_out) {
            throw std::runtime_error("dataset output pointer must not be null");
        }
        *dataset_out = nullptr;
        auto* dataset = create_columnar_payload_optix(
            fields, field_count,
            row_values, row_count,
            primary_fields, primary_field_count);
        *dataset_out = reinterpret_cast<RtdlOptixColumnarPayload*>(dataset);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_payload_create_from_columns(
        const RtdlPayloadField* fields, size_t field_count,
        size_t row_count,
        const char* const* primary_fields, size_t primary_field_count,
        RtdlOptixColumnarPayload** dataset_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!dataset_out) {
            throw std::runtime_error("dataset output pointer must not be null");
        }
        *dataset_out = nullptr;
        auto* dataset = create_columnar_payload_optix_from_columns(
            fields, field_count,
            row_count,
            primary_fields, primary_field_count);
        *dataset_out = reinterpret_cast<RtdlOptixColumnarPayload*>(dataset);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_payload_create_from_device_columns(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const char* const* primary_fields, size_t primary_field_count,
        RtdlOptixColumnarPayload** dataset_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!dataset_out) {
            throw std::runtime_error("dataset output pointer must not be null");
        }
        *dataset_out = nullptr;
        if (!fields || field_count == 0) {
            throw std::runtime_error("device-column payload requires at least one field");
        }
        if (row_count == 0) {
            throw std::runtime_error("device-column payload requires at least one row");
        }
        uint32_t expected_device_id = 0;
        bool expected_device_id_set = false;
        bool has_row_id = false;
        for (size_t index = 0; index < field_count; ++index) {
            const RtdlDevicePayloadField& field = fields[index];
            if (!field.name || field.name[0] == '\0') {
                throw std::runtime_error("device-column payload field names must be non-empty");
            }
            if (field.device_type != kRtdlDevicePayloadDeviceCuda) {
                throw std::runtime_error("device-column payload fields must use CUDA device pointers");
            }
            if (field.device_ptr == 0) {
                throw std::runtime_error("device-column payload fields require non-zero device_ptr");
            }
            if (field.element_count != row_count) {
                throw std::runtime_error("device-column payload field length must match row_count");
            }
            if (!expected_device_id_set) {
                expected_device_id = field.device_id;
                expected_device_id_set = true;
            } else if (field.device_id != expected_device_id) {
                throw std::runtime_error("device-column payload fields must live on the same CUDA device");
            }
            size_t expected_stride = 0;
            if (field.dtype == kRtdlDevicePayloadDtypeInt64) {
                expected_stride = sizeof(int64_t);
                if (field.kind != kRtdlColumnKindInt64) {
                    throw std::runtime_error("int64 device columns must use int64 logical kind");
                }
            } else if (field.dtype == kRtdlDevicePayloadDtypeUint32) {
                expected_stride = sizeof(uint32_t);
                if (field.kind != kRtdlColumnKindInt64) {
                    throw std::runtime_error("uint32 device columns must use int64-compatible logical kind");
                }
            } else if (field.dtype == kRtdlDevicePayloadDtypeFloat64) {
                expected_stride = sizeof(double);
                if (field.kind != kRtdlColumnKindFloat64) {
                    throw std::runtime_error("float64 device columns must use float64 logical kind");
                }
            } else {
                throw std::runtime_error("unsupported device-column payload dtype");
            }
            if (field.stride_bytes != expected_stride) {
                throw std::runtime_error("device-column payload fields must be contiguous");
            }
            if (std::strcmp(field.name, "row_id") == 0) {
                if (has_row_id) {
                    throw std::runtime_error("device-column payload must contain exactly one row_id field");
                }
                if (field.kind != kRtdlColumnKindInt64) {
                    throw std::runtime_error("device-column row_id must use int64-compatible logical kind");
                }
                has_row_id = true;
            }
        }
        if (!has_row_id) {
            throw std::runtime_error("device-column payload requires a row_id field");
        }
        (void)primary_fields;
        (void)primary_field_count;
        throw std::runtime_error(
            "rtdl_optix_columnar_payload_create_from_device_columns is a fail-closed ABI scaffold; "
            "device-column descriptors validated; "
            "partner-resident columnar native execution is not implemented");
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_count_i64(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        RtdlGroupedCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_count_i64_optix(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        size_t group_capacity,
        RtdlGroupedCountRow** rows_out, size_t* row_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_count_i64_optix_with_capacity(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            group_capacity,
            rows_out,
            row_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_count_i64_device_columns_with_capacity(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        size_t group_capacity,
        RtdlNativeDeviceGroupedCountI64Columns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_count_i64_device_columns_optix_with_capacity(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            group_capacity,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_device_grouped_count_i64_columns(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_device_grouped_count_i64_columns_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_segment_pair_left_id_count_device_columns(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_device_grouped_count_i64_columns_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_count_i64_compact_device_columns_with_capacity(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        size_t group_capacity,
        RtdlNativeDeviceGroupedCountI64CompactColumns* columns_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_count_i64_compact_device_columns_optix_with_capacity(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            group_capacity,
            columns_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_release_device_grouped_count_i64_compact_columns(
        void* owner_handle,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        release_device_grouped_count_i64_compact_columns_optix(owner_handle);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_sum_i64(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlGroupedSumRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_sum_i64_optix(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            value_field,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_sum_i64_with_capacity(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedSumRow** rows_out, size_t* row_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_sum_i64_optix_with_capacity(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            value_field,
            group_capacity,
            rows_out,
            row_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_min_i64_with_capacity(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedSumRow** rows_out, size_t* row_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_min_i64_optix_with_capacity(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            value_field,
            group_capacity,
            rows_out,
            row_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_max_i64_with_capacity(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedSumRow** rows_out, size_t* row_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_max_i64_optix_with_capacity(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            value_field,
            group_capacity,
            rows_out,
            row_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_sum_count_i64_with_capacity(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedSumCountRow** rows_out, size_t* row_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_sum_count_i64_optix_with_capacity(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            value_field,
            group_capacity,
            rows_out,
            row_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_device_payload_grouped_stats_i64_with_capacity(
        const RtdlDevicePayloadField* fields, size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedStatsRow** rows_out, size_t* row_count_out,
        uint32_t* overflowed_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        run_device_column_grouped_stats_i64_optix_with_capacity(
            fields,
            field_count,
            row_count,
            clauses,
            clause_count,
            group_key_field,
            value_field,
            group_capacity,
            rows_out,
            row_count_out,
            overflowed_out);
    }, error_out, error_size);
}

extern "C" void rtdl_optix_columnar_payload_destroy(RtdlOptixColumnarPayload* dataset)
{
    delete reinterpret_cast<OptixColumnarPayloadImpl*>(dataset);
}

extern "C" int rtdl_optix_columnar_payload_multi_predicate_scan(
        RtdlOptixColumnarPayload* dataset,
        const RtdlColumnClause* clauses, size_t clause_count,
        RtdlColumnRowIdRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_columnar_multi_predicate_scan_optix_prepared(
            reinterpret_cast<OptixColumnarPayloadImpl*>(dataset),
            clauses, clause_count,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_payload_multi_predicate_scan_count(
        RtdlOptixColumnarPayload* dataset,
        const RtdlColumnClause* clauses, size_t clause_count,
        size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!row_count_out) {
            throw std::runtime_error("row_count_out pointer must not be null");
        }
        *row_count_out = 0;
        run_columnar_multi_predicate_scan_count_optix_prepared(
            reinterpret_cast<OptixColumnarPayloadImpl*>(dataset),
            clauses, clause_count,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_payload_grouped_reduction_count(
        RtdlOptixColumnarPayload* dataset,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        RtdlGroupedCountRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_columnar_grouped_count_optix_prepared(
            reinterpret_cast<OptixColumnarPayloadImpl*>(dataset),
            clauses, clause_count,
            group_key_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_optix_columnar_payload_grouped_reduction_sum(
        RtdlOptixColumnarPayload* dataset,
        const RtdlColumnClause* clauses, size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlGroupedSumRow** rows_out, size_t* row_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!rows_out || !row_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_columnar_grouped_sum_optix_prepared(
            reinterpret_cast<OptixColumnarPayloadImpl*>(dataset),
            clauses, clause_count,
            group_key_field,
            value_field,
            rows_out, row_count_out);
    }, error_out, error_size);
}

static void rtdl_optix_fill_columnar_compact_summary_phase(RtdlColumnCompactSummaryResult& result)
{
    result.traversal = g_optix_last_columnar_traversal_s;
    result.bitset_copyback = g_optix_last_columnar_bitset_copy_s;
    result.exact_filter = g_optix_last_columnar_exact_filter_s;
    result.output_pack = g_optix_last_columnar_output_pack_s;
    result.raw_candidate_count = g_optix_last_columnar_raw_candidate_count;
    result.emitted_count = g_optix_last_columnar_emitted_count;
}

extern "C" void rtdl_optix_columnar_compact_summary_results_destroy(
        RtdlColumnCompactSummaryResult* results,
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

extern "C" int rtdl_optix_columnar_payload_compact_summary_batch(
        RtdlOptixColumnarPayload* dataset,
        const RtdlColumnCompactSummaryRequest* requests,
        size_t request_count,
        RtdlColumnCompactSummaryResult** results_out,
        size_t* result_count_out,
        char* error_out, size_t error_size)
{
    return handle_native_call([&]() {
        if (!dataset) {
            throw std::runtime_error("OptiX prepared columnar payload must not be null");
        }
        if (!results_out || !result_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (request_count > 0 && !requests) {
            throw std::runtime_error("compact summary request pointer must not be null when request_count > 0");
        }
        *results_out = nullptr;
        *result_count_out = 0;

        auto* impl = reinterpret_cast<OptixColumnarPayloadImpl*>(dataset);
        std::vector<RtdlColumnCompactSummaryResult> results(request_count);
        try {
            for (size_t index = 0; index < request_count; ++index) {
                const RtdlColumnCompactSummaryRequest& request = requests[index];
                RtdlColumnCompactSummaryResult& result = results[index];
                result.operation = request.operation;
                if (request.operation == kRtdlColumnCompactSummaryScanCount) {
                    run_columnar_multi_predicate_scan_count_optix_prepared(
                        impl,
                        request.clauses,
                        request.clause_count,
                        &result.scalar_value);
                    rtdl_optix_fill_columnar_compact_summary_phase(result);
                } else if (request.operation == kRtdlColumnCompactSummaryGroupedCount) {
                    if (!request.group_key_field) {
                        throw std::runtime_error("grouped_count compact summary requires group_key_field");
                    }
                    run_columnar_grouped_count_optix_prepared(
                        impl,
                        request.clauses,
                        request.clause_count,
                        request.group_key_field,
                        &result.count_rows,
                        &result.count_row_count);
                    rtdl_optix_fill_columnar_compact_summary_phase(result);
                } else if (request.operation == kRtdlColumnCompactSummaryGroupedSum) {
                    if (!request.group_key_field || !request.value_field) {
                        throw std::runtime_error("grouped_sum compact summary requires group_key_field and value_field");
                    }
                    run_columnar_grouped_sum_optix_prepared(
                        impl,
                        request.clauses,
                        request.clause_count,
                        request.group_key_field,
                        request.value_field,
                        &result.sum_rows,
                        &result.sum_row_count);
                    rtdl_optix_fill_columnar_compact_summary_phase(result);
                } else {
                    throw std::runtime_error("unsupported columnar compact-summary batch operation");
                }
            }
        } catch (...) {
            for (RtdlColumnCompactSummaryResult& result : results) {
                std::free(result.count_rows);
                std::free(result.sum_rows);
                result.count_rows = nullptr;
                result.sum_rows = nullptr;
            }
            throw;
        }

        auto* out = static_cast<RtdlColumnCompactSummaryResult*>(
            std::calloc(results.size(), sizeof(RtdlColumnCompactSummaryResult)));
        if (!out && !results.empty()) {
            for (RtdlColumnCompactSummaryResult& result : results) {
                std::free(result.count_rows);
                std::free(result.sum_rows);
                result.count_rows = nullptr;
                result.sum_rows = nullptr;
            }
            throw std::bad_alloc();
        }
        if (!results.empty()) {
            std::memcpy(out, results.data(), sizeof(RtdlColumnCompactSummaryResult) * results.size());
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
        std::string cubin = compile_to_cubin(
            kCollectKBoundedI64RowWidth2FinalCompactKernelSrc,
            "collect_k_bounded_i64_row_width2_final_compact_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_collect_k_i64_row_width2_final_materialize.module, cubin.data()));
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
            &g_collect_k_i64_row_width2_four_way_materialize_mark_counts_derived.fn,
            g_collect_k_i64_row_width2_final_materialize.module,
            "collect_k_bounded_i64_row_width2_four_way_materialize_mark_counts_derived"));
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
        if (total_blocks == 0 || total_blocks > 4096) {
            throw std::runtime_error("collect-k graph replay probe total block count must be in 1..4096");
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
        if (max_total_blocks == 0 || max_total_blocks > 4096) {
            throw std::runtime_error("collect-k graph update probe total block count must be in 1..4096");
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

extern "C" int rtdl_optix_collect_k_four_way_merge_probe(
        size_t repeats,
        size_t group_count,
        size_t segment_capacity,
        double* reference_ms_out,
        double* four_way_ms_out,
        uint64_t* mismatch_count_out,
        uint64_t* first_group_count_out,
        char* error_out,
        size_t error_size)
{
    return handle_native_call([&]() {
        if (!reference_ms_out || !four_way_ms_out || !mismatch_count_out || !first_group_count_out) {
            throw std::runtime_error("output pointers must not be null");
        }
        if (repeats == 0)
            repeats = 1;
        if (group_count == 0)
            group_count = 1;
        if (segment_capacity == 0)
            segment_capacity = 2048;

        (void)get_optix_context();
        ensure_collect_k_row_width2_final_compact_kernels();

        const unsigned threads = 256;
        const size_t input_segments = group_count * 4;
        const size_t two_way_group_count = group_count * 2;
        const size_t two_way_output_capacity = segment_capacity * 2;
        const size_t four_way_output_capacity = segment_capacity * 4;
        const size_t input_values = input_segments * segment_capacity * 2;
        const size_t mid_values = two_way_group_count * two_way_output_capacity * 2;
        const size_t output_values = group_count * four_way_output_capacity * 2;
        const size_t two_way_blocks_per_group = (two_way_output_capacity + threads - 1) / threads;
        const size_t four_way_blocks_per_group = (four_way_output_capacity + threads - 1) / threads;
        const unsigned two_way_total_blocks = static_cast<unsigned>(two_way_group_count * two_way_blocks_per_group);
        const unsigned four_way_total_blocks = static_cast<unsigned>(group_count * four_way_blocks_per_group);
        if (two_way_total_blocks == 0 || four_way_total_blocks == 0
                || two_way_total_blocks > 4096 || four_way_total_blocks > 4096) {
            throw std::runtime_error("collect-k four-way merge probe total block count must be in 1..4096");
        }

        std::vector<int64_t> host_rows(input_values);
        std::vector<size_t> host_counts(input_segments, segment_capacity);
        for (size_t segment = 0; segment < input_segments; ++segment) {
            int64_t* rows = host_rows.data() + segment * segment_capacity * 2;
            for (size_t index = 0; index < segment_capacity; ++index) {
                rows[index * 2] = static_cast<int64_t>(index);
                rows[index * 2 + 1] = static_cast<int64_t>(index % 7);
            }
        }

        CUdeviceptr current_base = 0;
        CUdeviceptr current_counts = 0;
        CUdeviceptr ref_mid_merged_rows = 0;
        CUdeviceptr ref_mid_output_rows = 0;
        CUdeviceptr ref_mid_marks = 0;
        CUdeviceptr ref_mid_block_counts = 0;
        CUdeviceptr ref_mid_block_offsets = 0;
        CUdeviceptr ref_mid_pair_offsets = 0;
        CUdeviceptr ref_mid_counts = 0;
        CUdeviceptr ref_final_merged_rows = 0;
        CUdeviceptr ref_output_rows = 0;
        CUdeviceptr ref_final_marks = 0;
        CUdeviceptr ref_final_block_counts = 0;
        CUdeviceptr ref_final_block_offsets = 0;
        CUdeviceptr ref_final_pair_offsets = 0;
        CUdeviceptr ref_final_counts = 0;
        CUdeviceptr four_merged_rows = 0;
        CUdeviceptr four_marks = 0;
        CUdeviceptr four_block_counts = 0;
        CUdeviceptr four_block_offsets = 0;
        CUdeviceptr four_pair_offsets = 0;
        CUdeviceptr four_counts = 0;
        CUdeviceptr four_output_rows = 0;
        CUstream stream = nullptr;

        auto cleanup = [&]() {
            if (stream)
                cuStreamDestroy(stream);
            if (four_output_rows)
                cuMemFree(four_output_rows);
            if (four_counts)
                cuMemFree(four_counts);
            if (four_pair_offsets)
                cuMemFree(four_pair_offsets);
            if (four_block_offsets)
                cuMemFree(four_block_offsets);
            if (four_block_counts)
                cuMemFree(four_block_counts);
            if (four_marks)
                cuMemFree(four_marks);
            if (four_merged_rows)
                cuMemFree(four_merged_rows);
            if (ref_final_counts)
                cuMemFree(ref_final_counts);
            if (ref_final_pair_offsets)
                cuMemFree(ref_final_pair_offsets);
            if (ref_final_block_offsets)
                cuMemFree(ref_final_block_offsets);
            if (ref_final_block_counts)
                cuMemFree(ref_final_block_counts);
            if (ref_final_marks)
                cuMemFree(ref_final_marks);
            if (ref_output_rows)
                cuMemFree(ref_output_rows);
            if (ref_mid_counts)
                cuMemFree(ref_mid_counts);
            if (ref_mid_pair_offsets)
                cuMemFree(ref_mid_pair_offsets);
            if (ref_mid_block_offsets)
                cuMemFree(ref_mid_block_offsets);
            if (ref_mid_block_counts)
                cuMemFree(ref_mid_block_counts);
            if (ref_mid_marks)
                cuMemFree(ref_mid_marks);
            if (ref_final_merged_rows)
                cuMemFree(ref_final_merged_rows);
            if (ref_mid_output_rows)
                cuMemFree(ref_mid_output_rows);
            if (ref_mid_merged_rows)
                cuMemFree(ref_mid_merged_rows);
            if (current_counts)
                cuMemFree(current_counts);
            if (current_base)
                cuMemFree(current_base);
        };

        auto launch_binary_level = [&](CUdeviceptr base,
                                       CUdeviceptr counts,
                                       size_t active_group_count,
                                       size_t active_segment_capacity,
                                       size_t output_capacity,
                                       CUdeviceptr merged_rows,
                                       CUdeviceptr marks,
                                       CUdeviceptr block_counts,
                                       CUdeviceptr block_offsets,
                                       CUdeviceptr pair_offsets,
                                       CUdeviceptr pair_counts,
                                       CUdeviceptr output_rows) {
            size_t active_group_count_arg = active_group_count;
            size_t active_segment_capacity_arg = active_segment_capacity;
            size_t output_capacity_arg = output_capacity;
            size_t blocks_per_group_arg = (output_capacity + threads - 1) / threads;
            const unsigned total_blocks = static_cast<unsigned>(active_group_count * blocks_per_group_arg);
            void* materialize_args[] = {
                &base, &counts, &active_segment_capacity_arg, &output_capacity_arg,
                &merged_rows, &active_group_count_arg, &blocks_per_group_arg,
            };
            CU_CHECK(cuLaunchKernel(
                g_collect_k_i64_row_width2_final_materialize_level_counts_derived.fn,
                total_blocks, 1, 1, threads, 1, 1, 0, stream, materialize_args, nullptr));

            void* mark_args[] = {
                &merged_rows, &counts, &output_capacity_arg, &active_group_count_arg,
                &marks, &block_counts, &blocks_per_group_arg,
            };
            CU_CHECK(cuLaunchKernel(
                g_collect_k_i64_row_width2_final_mark_counts_level_counts.fn,
                total_blocks, 1, 1, threads, 1, 1,
                sizeof(uint32_t) * threads, stream, mark_args, nullptr));

            void* prefix_args[] = {
                &block_counts, &active_group_count_arg, &blocks_per_group_arg,
                &block_offsets, &pair_offsets, &pair_counts,
            };
            CU_CHECK(cuLaunchKernel(
                g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                static_cast<unsigned>(active_group_count), 1, 1,
                1, 1, 1, 0, stream, prefix_args, nullptr));

            void* compact_args[] = {
                &merged_rows, &marks, &block_offsets, &pair_offsets,
                &output_rows, &output_capacity_arg, &active_group_count_arg, &blocks_per_group_arg,
            };
            CU_CHECK(cuLaunchKernel(
                g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                total_blocks, 1, 1, threads, 1, 1,
                sizeof(uint32_t) * threads, stream, compact_args, nullptr));
        };

        try {
            CU_CHECK(cuMemAlloc(&current_base, sizeof(int64_t) * input_values));
            CU_CHECK(cuMemAlloc(&current_counts, sizeof(size_t) * input_segments));
            CU_CHECK(cuMemAlloc(&ref_mid_merged_rows, sizeof(int64_t) * mid_values));
            CU_CHECK(cuMemAlloc(&ref_mid_output_rows, sizeof(int64_t) * mid_values));
            CU_CHECK(cuMemAlloc(&ref_mid_marks, sizeof(uint32_t) * two_way_total_blocks * threads));
            CU_CHECK(cuMemAlloc(&ref_mid_block_counts, sizeof(uint32_t) * two_way_total_blocks));
            CU_CHECK(cuMemAlloc(&ref_mid_block_offsets, sizeof(uint32_t) * two_way_total_blocks));
            CU_CHECK(cuMemAlloc(&ref_mid_pair_offsets, sizeof(uint32_t) * two_way_group_count));
            CU_CHECK(cuMemAlloc(&ref_mid_counts, sizeof(size_t) * two_way_group_count));
            CU_CHECK(cuMemAlloc(&ref_final_merged_rows, sizeof(int64_t) * output_values));
            CU_CHECK(cuMemAlloc(&ref_output_rows, sizeof(int64_t) * output_values));
            CU_CHECK(cuMemAlloc(&ref_final_marks, sizeof(uint32_t) * four_way_total_blocks * threads));
            CU_CHECK(cuMemAlloc(&ref_final_block_counts, sizeof(uint32_t) * four_way_total_blocks));
            CU_CHECK(cuMemAlloc(&ref_final_block_offsets, sizeof(uint32_t) * four_way_total_blocks));
            CU_CHECK(cuMemAlloc(&ref_final_pair_offsets, sizeof(uint32_t) * group_count));
            CU_CHECK(cuMemAlloc(&ref_final_counts, sizeof(size_t) * group_count));
            CU_CHECK(cuMemAlloc(&four_merged_rows, sizeof(int64_t) * output_values));
            CU_CHECK(cuMemAlloc(&four_marks, sizeof(uint32_t) * four_way_total_blocks * threads));
            CU_CHECK(cuMemAlloc(&four_block_counts, sizeof(uint32_t) * four_way_total_blocks));
            CU_CHECK(cuMemAlloc(&four_block_offsets, sizeof(uint32_t) * four_way_total_blocks));
            CU_CHECK(cuMemAlloc(&four_pair_offsets, sizeof(uint32_t) * group_count));
            CU_CHECK(cuMemAlloc(&four_counts, sizeof(size_t) * group_count));
            CU_CHECK(cuMemAlloc(&four_output_rows, sizeof(int64_t) * output_values));
            CU_CHECK(cuMemcpyHtoD(current_base, host_rows.data(), sizeof(int64_t) * host_rows.size()));
            CU_CHECK(cuMemcpyHtoD(current_counts, host_counts.data(), sizeof(size_t) * host_counts.size()));
            CU_CHECK(cuStreamCreate(&stream, CU_STREAM_NON_BLOCKING));

            auto launch_reference = [&]() {
                launch_binary_level(
                    current_base, current_counts, two_way_group_count,
                    segment_capacity, two_way_output_capacity,
                    ref_mid_merged_rows, ref_mid_marks, ref_mid_block_counts,
                    ref_mid_block_offsets, ref_mid_pair_offsets, ref_mid_counts,
                    ref_mid_output_rows);
                launch_binary_level(
                    ref_mid_output_rows, ref_mid_counts, group_count,
                    two_way_output_capacity, four_way_output_capacity,
                    ref_final_merged_rows, ref_final_marks, ref_final_block_counts,
                    ref_final_block_offsets, ref_final_pair_offsets, ref_final_counts,
                    ref_output_rows);
            };

            auto launch_four_way = [&]() {
                CU_CHECK(cuMemsetD32Async(four_marks, 0, four_way_total_blocks * threads, stream));
                CU_CHECK(cuMemsetD32Async(four_block_counts, 0, four_way_total_blocks, stream));
                size_t four_way_output_capacity_arg = four_way_output_capacity;
                size_t group_count_arg = group_count;
                size_t segment_capacity_arg = segment_capacity;
                size_t four_way_blocks_per_group_arg = four_way_blocks_per_group;
                void* four_args[] = {
                    &current_base,
                    &current_counts,
                    &segment_capacity_arg,
                    &four_way_output_capacity_arg,
                    &four_merged_rows,
                    &group_count_arg,
                    &four_marks,
                    &four_block_counts,
                    &four_way_blocks_per_group_arg,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_four_way_materialize_mark_counts_derived.fn,
                    four_way_total_blocks, 1, 1,
                    threads, 1, 1,
                    0, stream, four_args, nullptr));

                void* prefix_args[] = {
                    &four_block_counts,
                    &group_count_arg,
                    &four_way_blocks_per_group_arg,
                    &four_block_offsets,
                    &four_pair_offsets,
                    &four_counts,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_prefix_offsets_level.fn,
                    static_cast<unsigned>(group_count), 1, 1,
                    1, 1, 1, 0, stream, prefix_args, nullptr));

                void* compact_args[] = {
                    &four_merged_rows,
                    &four_marks,
                    &four_block_offsets,
                    &four_pair_offsets,
                    &four_output_rows,
                    &four_way_output_capacity_arg,
                    &group_count_arg,
                    &four_way_blocks_per_group_arg,
                };
                CU_CHECK(cuLaunchKernel(
                    g_collect_k_i64_row_width2_final_compact_level_derived.fn,
                    four_way_total_blocks, 1, 1,
                    threads, 1, 1,
                    sizeof(uint32_t) * threads, stream, compact_args, nullptr));
            };

            auto reference_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index)
                launch_reference();
            CU_CHECK(cuStreamSynchronize(stream));
            *reference_ms_out = CollectKStageProfile::elapsed_ms(reference_start);

            auto four_way_start = CollectKStageProfile::Clock::now();
            for (size_t index = 0; index < repeats; ++index)
                launch_four_way();
            CU_CHECK(cuStreamSynchronize(stream));
            *four_way_ms_out = CollectKStageProfile::elapsed_ms(four_way_start);

            launch_reference();
            launch_four_way();
            CU_CHECK(cuStreamSynchronize(stream));

            std::vector<size_t> ref_counts(group_count);
            std::vector<size_t> four_counts_host(group_count);
            std::vector<int64_t> ref_rows(output_values);
            std::vector<int64_t> four_rows(output_values);
            CU_CHECK(cuMemcpyDtoH(ref_counts.data(), ref_final_counts, sizeof(size_t) * group_count));
            CU_CHECK(cuMemcpyDtoH(four_counts_host.data(), four_counts, sizeof(size_t) * group_count));
            CU_CHECK(cuMemcpyDtoH(ref_rows.data(), ref_output_rows, sizeof(int64_t) * output_values));
            CU_CHECK(cuMemcpyDtoH(four_rows.data(), four_output_rows, sizeof(int64_t) * output_values));

            uint64_t mismatches = 0;
            for (size_t group = 0; group < group_count; ++group) {
                if (ref_counts[group] != four_counts_host[group])
                    ++mismatches;
                const size_t compare_rows = std::min(ref_counts[group], four_counts_host[group]);
                const size_t base = group * four_way_output_capacity * 2;
                for (size_t row = 0; row < compare_rows; ++row) {
                    if (ref_rows[base + row * 2] != four_rows[base + row * 2] ||
                        ref_rows[base + row * 2 + 1] != four_rows[base + row * 2 + 1]) {
                        ++mismatches;
                    }
                }
            }

            *mismatch_count_out = mismatches;
            *first_group_count_out = group_count > 0 ? static_cast<uint64_t>(ref_counts[0]) : 0u;
        } catch (...) {
            cleanup();
            throw;
        }

        cleanup();
    }, error_out, error_size);
}
