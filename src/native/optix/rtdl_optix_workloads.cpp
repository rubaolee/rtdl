static void run_seg_poly_hitcount_optix_host_indexed(
        const RtdlSegment*    segments,  size_t segment_count,
        const RtdlPolygonRef* polygons,  size_t polygon_count,
        const double* vertices_xy,
        RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out)
{
    std::vector<Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_count);
    for (size_t i = 0; i < polygon_count; ++i) {
        polygon_bounds.push_back(bounds_for_polygon(polygons[i], vertices_xy));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_count, 0);
    size_t stamp = 1;

    auto* out = static_cast<RtdlSegmentPolygonHitCountRow*>(
        std::malloc(sizeof(RtdlSegmentPolygonHitCountRow) * segment_count));
    if (!out && segment_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < segment_count; ++i) {
        const Bounds2D seg_bounds = bounds_for_segment(segments[i]);
        const size_t bucket_count = bucket_index.buckets.size();
        size_t first = 0;
        size_t last = 0;
        if (bucket_count > 0) {
            first = static_cast<size_t>(std::clamp(
                static_cast<long long>(std::floor((seg_bounds.min_x - bucket_index.origin_x) / bucket_index.bucket_width)),
                0LL,
                static_cast<long long>(bucket_count - 1)));
            last = static_cast<size_t>(std::clamp(
                static_cast<long long>(std::floor((seg_bounds.max_x - bucket_index.origin_x) / bucket_index.bucket_width)),
                0LL,
                static_cast<long long>(bucket_count - 1)));
        }
        uint32_t hit_count = 0;
        for (size_t bucket_id = first; bucket_id <= last && bucket_count > 0; ++bucket_id) {
            for (size_t polygon_index : bucket_index.buckets[bucket_id]) {
                if (seen[polygon_index] == stamp) {
                    continue;
                }
                seen[polygon_index] = stamp;
                if (!bounds_overlap(seg_bounds, polygon_bounds[polygon_index])) {
                    continue;
                }
                if (exact_segment_hits_polygon(segments[i], polygons[polygon_index], vertices_xy)) {
                    hit_count += 1;
                }
            }
        }
        out[i] = {segments[i].id, hit_count};
        stamp += 1;
        if (stamp == 0) {
            std::fill(seen.begin(), seen.end(), 0);
            stamp = 1;
        }
    }
    *rows_out = out;
    *row_count_out = segment_count;
}

static void run_seg_poly_anyhit_rows_optix_host_indexed(
        const RtdlSegment* segments, size_t segment_count,
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy,
        RtdlSegmentPolygonAnyHitRow** rows_out, size_t* row_count_out)
{
    std::vector<Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_count);
    for (size_t i = 0; i < polygon_count; ++i) {
        polygon_bounds.push_back(bounds_for_polygon(polygons[i], vertices_xy));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_count, 0);
    size_t stamp = 1;
    std::vector<RtdlSegmentPolygonAnyHitRow> out_rows;
    out_rows.reserve(segment_count);

    for (size_t i = 0; i < segment_count; ++i) {
        const Bounds2D seg_bounds = bounds_for_segment(segments[i]);
        const size_t bucket_count = bucket_index.buckets.size();
        size_t first = 0;
        size_t last = 0;
        if (bucket_count > 0) {
            first = static_cast<size_t>(std::clamp(
                static_cast<long long>(std::floor((seg_bounds.min_x - bucket_index.origin_x) / bucket_index.bucket_width)),
                0LL,
                static_cast<long long>(bucket_count - 1)));
            last = static_cast<size_t>(std::clamp(
                static_cast<long long>(std::floor((seg_bounds.max_x - bucket_index.origin_x) / bucket_index.bucket_width)),
                0LL,
                static_cast<long long>(bucket_count - 1)));
        }
        for (size_t bucket_id = first; bucket_id <= last && bucket_count > 0; ++bucket_id) {
            for (size_t polygon_index : bucket_index.buckets[bucket_id]) {
                if (seen[polygon_index] == stamp) {
                    continue;
                }
                seen[polygon_index] = stamp;
                if (!bounds_overlap(seg_bounds, polygon_bounds[polygon_index])) {
                    continue;
                }
                if (exact_segment_hits_polygon(segments[i], polygons[polygon_index], vertices_xy)) {
                    out_rows.push_back({segments[i].id, polygons[polygon_index].id});
                }
            }
        }
        stamp += 1;
        if (stamp == 0) {
            std::fill(seen.begin(), seen.end(), 0);
            stamp = 1;
        }
    }

    auto* out = static_cast<RtdlSegmentPolygonAnyHitRow*>(
        std::malloc(sizeof(RtdlSegmentPolygonAnyHitRow) * out_rows.size()));
    if (!out && !out_rows.empty()) throw std::bad_alloc();
    if (!out_rows.empty()) {
        std::memcpy(out, out_rows.data(), sizeof(RtdlSegmentPolygonAnyHitRow) * out_rows.size());
    }
    *rows_out = out;
    *row_count_out = out_rows.size();
}

// ──────────────────────────────────────────────────────────────────────────────
// Workload implementations
// ──────────────────────────────────────────────────────────────────────────────

// ---------- LSI --------------------------------------------------------------

struct LsiLaunchParams {
    OptixTraversableHandle traversable;
    const GpuSegment* left_segs;
    const GpuSegment* right_segs;
    GpuLsiRecord*     output;
    uint32_t*         output_count;
    uint32_t          output_capacity;
    uint32_t          probe_count;
};

static void run_lsi_optix(
        const RtdlSegment* left,  size_t left_count,
        const RtdlSegment* right, size_t right_count,
        RtdlLsiRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_lsi.init, [&]() {
        std::string ptx = compile_to_ptx(kLsiKernelSrc, "lsi_kernel.cu");
        g_lsi.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__lsi_probe",
            "__miss__lsi_miss",
            "__intersection__lsi_isect",
            "__anyhit__lsi_anyhit",
            nullptr,   // no closesthit
            4).release();
    });

    // Upload segments
    std::vector<GpuSegment> gpu_left(left_count), gpu_right(right_count);
    for (size_t i = 0; i < left_count; ++i)
        gpu_left[i]  = {(float)left[i].x0,  (float)left[i].y0,
                        (float)left[i].x1,  (float)left[i].y1,  left[i].id};
    for (size_t i = 0; i < right_count; ++i)
        gpu_right[i] = {(float)right[i].x0, (float)right[i].y0,
                        (float)right[i].x1, (float)right[i].y1, right[i].id};

    DevPtr d_left (sizeof(GpuSegment) * left_count);
    DevPtr d_right(sizeof(GpuSegment) * right_count);
    upload(d_left.ptr,  gpu_left.data(),  left_count);
    upload(d_right.ptr, gpu_right.data(), right_count);

    // Build BVH over right (build) segments
    std::vector<OptixAabb> aabbs(right_count);
    for (size_t i = 0; i < right_count; ++i)
        aabbs[i] = aabb_for_segment(gpu_right[i].x0, gpu_right[i].y0,
                                    gpu_right[i].x1, gpu_right[i].y1);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    // Output buffer
    uint32_t capacity = static_cast<uint32_t>(left_count * right_count);
    DevPtr d_output  (sizeof(GpuLsiRecord) * capacity);
    DevPtr d_count   (sizeof(uint32_t));
    uint32_t zero = 0;
    upload<uint32_t>(d_count.ptr, &zero, 1);

    // Launch params
    LsiLaunchParams lp;
    lp.traversable      = accel.handle;
    lp.left_segs        = reinterpret_cast<const GpuSegment*>(d_left.ptr);
    lp.right_segs       = reinterpret_cast<const GpuSegment*>(d_right.ptr);
    lp.output           = reinterpret_cast<GpuLsiRecord*>(d_output.ptr);
    lp.output_count     = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.output_capacity  = capacity;
    lp.probe_count      = static_cast<uint32_t>(left_count);

    DevPtr d_params(sizeof(LsiLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_lsi.pipe->pipeline, stream,
                             d_params.ptr, sizeof(LsiLaunchParams),
                             &g_lsi.pipe->sbt,
                             static_cast<unsigned>(left_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    // Read back results
    uint32_t gpu_count = 0;
    download(&gpu_count, d_count.ptr, 1);
    if (gpu_count > capacity)
        throw std::runtime_error("LSI output overflowed capacity");

    std::vector<GpuLsiRecord> gpu_rows(gpu_count);
    if (gpu_count > 0)
        download(gpu_rows.data(), d_output.ptr, gpu_count);

    std::unordered_map<uint32_t, const RtdlSegment*> left_by_id;
    std::unordered_map<uint32_t, const RtdlSegment*> right_by_id;
    left_by_id.reserve(left_count);
    right_by_id.reserve(right_count);
    for (size_t i = 0; i < left_count; ++i) {
        left_by_id.emplace(left[i].id, &left[i]);
    }
    for (size_t i = 0; i < right_count; ++i) {
        right_by_id.emplace(right[i].id, &right[i]);
    }

    std::vector<RtdlLsiRow> refined;
    refined.reserve(gpu_count);
    std::unordered_set<uint64_t> seen_pairs;
    seen_pairs.reserve(gpu_count * 2 + 1);

    for (uint32_t i = 0; i < gpu_count; ++i) {
        const auto left_it = left_by_id.find(gpu_rows[i].left_id);
        const auto right_it = right_by_id.find(gpu_rows[i].right_id);
        if (left_it == left_by_id.end() || right_it == right_by_id.end()) {
            continue;
        }
        const uint64_t pair_key =
            (static_cast<uint64_t>(gpu_rows[i].left_id) << 32) |
            static_cast<uint64_t>(gpu_rows[i].right_id);
        if (seen_pairs.find(pair_key) != seen_pairs.end()) {
            continue;
        }
        double ix = 0.0;
        double iy = 0.0;
        if (!exact_segment_intersection(*left_it->second, *right_it->second, &ix, &iy)) {
            continue;
        }
        seen_pairs.insert(pair_key);
        refined.push_back(
            RtdlLsiRow{
                gpu_rows[i].left_id,
                gpu_rows[i].right_id,
                ix,
                iy,
            });
    }

    auto* out = static_cast<RtdlLsiRow*>(std::malloc(sizeof(RtdlLsiRow) * refined.size()));
    if (!out && !refined.empty()) throw std::bad_alloc();
    for (size_t i = 0; i < refined.size(); ++i) {
        out[i] = refined[i];
    }
    *rows_out      = out;
    *row_count_out = refined.size();
}

// ---------- PIP --------------------------------------------------------------

struct PipLaunchParams {
    OptixTraversableHandle traversable;
    const float*     points_x;
    const float*     points_y;
    const uint32_t*  point_ids;
    const GpuPolygonRef* polygons;
    const float*     vertices_x;
    const float*     vertices_y;
    uint32_t*        hit_words;
    GpuPipRecord*    output;
    uint32_t*        output_count;
    uint32_t         output_capacity;
    uint32_t         positive_only;
    uint32_t         hit_word_count;
    uint32_t         polygon_count;
    uint32_t         probe_count;
};

static void run_pip_optix(
        const RtdlPoint* points,     size_t point_count,
        const RtdlPolygonRef* polys, size_t poly_count,
        const double* vertices_xy,   size_t vertex_xy_count,
        uint32_t positive_only,
        RtdlPipRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_pip.init, [&]() {
        std::string ptx = compile_to_ptx(kPipKernelSrc, "pip_kernel.cu");
        g_pip.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__pip_probe",
            "__miss__pip_miss",
            "__intersection__pip_isect",
            "__anyhit__pip_anyhit",
            nullptr, 4).release();
    });

    size_t vert_count = vertex_xy_count / 2;

    // Build GPU polygon refs and vertex arrays
    std::vector<GpuPolygonRef> gpu_polys(poly_count);
    for (size_t i = 0; i < poly_count; ++i)
        gpu_polys[i] = {polys[i].id, polys[i].vertex_offset, polys[i].vertex_count};

    std::vector<float> vx(vert_count), vy(vert_count);
    for (size_t i = 0; i < vert_count; ++i) {
        vx[i] = static_cast<float>(vertices_xy[i * 2]);
        vy[i] = static_cast<float>(vertices_xy[i * 2 + 1]);
    }

    std::vector<float>    pts_x(point_count), pts_y(point_count);
    std::vector<uint32_t> pt_ids(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        pts_x[i] = static_cast<float>(points[i].x);
        pts_y[i] = static_cast<float>(points[i].y);
        pt_ids[i] = points[i].id;
    }

    DevPtr d_polys  (sizeof(GpuPolygonRef) * poly_count);
    DevPtr d_vx     (sizeof(float) * vert_count);
    DevPtr d_vy     (sizeof(float) * vert_count);
    DevPtr d_pts_x  (sizeof(float) * point_count);
    DevPtr d_pts_y  (sizeof(float) * point_count);
    DevPtr d_pt_ids (sizeof(uint32_t) * point_count);
    upload(d_polys.ptr,   gpu_polys.data(), poly_count);
    upload(d_vx.ptr,      vx.data(),        vert_count);
    upload(d_vy.ptr,      vy.data(),        vert_count);
    upload(d_pts_x.ptr,   pts_x.data(),     point_count);
    upload(d_pts_y.ptr,   pts_y.data(),     point_count);
    upload(d_pt_ids.ptr,  pt_ids.data(),    point_count);

    // BVH over polygons
    std::vector<OptixAabb> aabbs(poly_count);
    for (size_t i = 0; i < poly_count; ++i)
        aabbs[i] = aabb_for_polygon(vertices_xy, polys[i].vertex_offset, polys[i].vertex_count);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    size_t out_count = point_count * poly_count;
    DevPtr d_count(sizeof(uint32_t));
    uint32_t zero = 0;
    upload<uint32_t>(d_count.ptr, &zero, 1);
    std::unique_ptr<DevPtr> d_hit_words;
    std::unique_ptr<DevPtr> d_output;
    if (positive_only == 0u) {
        d_output = std::make_unique<DevPtr>(sizeof(GpuPipRecord) * out_count);
        std::vector<GpuPipRecord> init_output(out_count);
        for (size_t pi = 0; pi < point_count; ++pi)
            for (size_t qi = 0; qi < poly_count; ++qi) {
                init_output[pi * poly_count + qi] = {pt_ids[pi], gpu_polys[qi].id, 0u};
            }
        upload(d_output->ptr, init_output.data(), out_count);
    } else {
        const size_t hit_word_count = (out_count + 31u) / 32u;
        d_hit_words = std::make_unique<DevPtr>(sizeof(uint32_t) * hit_word_count);
        CU_CHECK(cuMemsetD8(d_hit_words->ptr, 0, sizeof(uint32_t) * hit_word_count));
    }

    PipLaunchParams lp;
    lp.traversable    = accel.handle;
    lp.points_x       = reinterpret_cast<const float*>(d_pts_x.ptr);
    lp.points_y       = reinterpret_cast<const float*>(d_pts_y.ptr);
    lp.point_ids      = reinterpret_cast<const uint32_t*>(d_pt_ids.ptr);
    lp.polygons       = reinterpret_cast<const GpuPolygonRef*>(d_polys.ptr);
    lp.vertices_x     = reinterpret_cast<const float*>(d_vx.ptr);
    lp.vertices_y     = reinterpret_cast<const float*>(d_vy.ptr);
    const uint32_t hit_word_count = positive_only == 0u
        ? 0u
        : static_cast<uint32_t>((out_count + 31u) / 32u);
    lp.hit_words      = d_hit_words ? reinterpret_cast<uint32_t*>(d_hit_words->ptr) : nullptr;
    lp.output         = d_output ? reinterpret_cast<GpuPipRecord*>(d_output->ptr) : nullptr;
    lp.output_count   = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.output_capacity = d_output ? static_cast<uint32_t>(out_count) : 0u;
    lp.positive_only  = positive_only;
    lp.hit_word_count = hit_word_count;
    lp.polygon_count  = static_cast<uint32_t>(poly_count);
    lp.probe_count    = static_cast<uint32_t>(point_count);

    DevPtr d_params(sizeof(PipLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    if (positive_only == 0u) {
        OPTIX_CHECK(optixLaunch(g_pip.pipe->pipeline, stream,
                                 d_params.ptr, sizeof(PipLaunchParams),
                                 &g_pip.pipe->sbt,
                                 static_cast<unsigned>(point_count), 1, 1));
        CU_CHECK(cuStreamSynchronize(stream));
    }

    // Read back
    if (positive_only != 0u) {
        // Single positive-only launch: reset the shared output counter just
        // before launch. The launch params themselves are unchanged.
        upload<uint32_t>(d_count.ptr, &zero, 1);
        OPTIX_CHECK(optixLaunch(g_pip.pipe->pipeline, stream,
                                 d_params.ptr, sizeof(PipLaunchParams),
                                 &g_pip.pipe->sbt,
                                 static_cast<unsigned>(point_count), 1, 1));
        CU_CHECK(cuStreamSynchronize(stream));
        std::vector<uint32_t> hit_words(hit_word_count);
        if (hit_word_count > 0) {
            download(hit_words.data(), d_hit_words->ptr, hit_word_count);
        }
        std::vector<RtdlPipRow> rows;
        rows.reserve(out_count / 64u);
#if RTDL_OPTIX_HAS_GEOS
        GeosPreparedPolygonRefs geos(polys, poly_count, vertices_xy);
#endif
        for (size_t pi = 0; pi < point_count; ++pi) {
            for (size_t qi = 0; qi < poly_count; ++qi) {
                const size_t slot = pi * poly_count + qi;
                const uint32_t word = static_cast<uint32_t>(slot >> 5);
                const uint32_t bit  = 1u << (slot & 31u);
                if ((hit_words[word] & bit) == 0u) {
                    continue;
                }
                const RtdlPoint& point = points[pi];
                const RtdlPolygonRef& polygon = polys[qi];
#if RTDL_OPTIX_HAS_GEOS
                if (!geos.covers(qi, point.x, point.y)) {
                    continue;
                }
#else
                if (!exact_point_in_polygon(point.x, point.y, polygon, vertices_xy)) {
                    continue;
                }
#endif
                rows.push_back({point.id, polygon.id, 1u});
            }
        }
        auto* out = static_cast<RtdlPipRow*>(std::malloc(sizeof(RtdlPipRow) * rows.size()));
        if (!out && !rows.empty()) throw std::bad_alloc();
        for (size_t i = 0; i < rows.size(); ++i) {
            out[i] = rows[i];
        }
        *rows_out = out;
        *row_count_out = rows.size();
        return;
    }

    std::vector<GpuPipRecord> gpu_rows(out_count);
    download(gpu_rows.data(), d_output->ptr, out_count);

    auto* out = static_cast<RtdlPipRow*>(std::malloc(sizeof(RtdlPipRow) * out_count));
    if (!out) throw std::bad_alloc();
    for (size_t i = 0; i < out_count; ++i) {
        out[i].point_id   = gpu_rows[i].point_id;
        out[i].polygon_id = gpu_rows[i].polygon_id;
        out[i].contains   = gpu_rows[i].contains;
    }

#if RTDL_OPTIX_HAS_GEOS
    GeosPreparedPolygonRefs geos(polys, poly_count, vertices_xy);
    for (size_t pi = 0; pi < point_count; ++pi) {
        for (size_t qi = 0; qi < poly_count; ++qi) {
            const size_t out_index = pi * poly_count + qi;
            out[out_index].point_id = points[pi].id;
            out[out_index].polygon_id = polys[qi].id;
            out[out_index].contains = geos.covers(qi, points[pi].x, points[pi].y) ? 1u : 0u;
        }
    }
#else
    std::unordered_map<uint32_t, const RtdlPoint*> point_by_id;
    std::unordered_map<uint32_t, const RtdlPolygonRef*> poly_by_id;
    point_by_id.reserve(point_count);
    poly_by_id.reserve(poly_count);
    for (size_t i = 0; i < point_count; ++i) {
        point_by_id.emplace(points[i].id, &points[i]);
    }
    for (size_t i = 0; i < poly_count; ++i) {
        poly_by_id.emplace(polys[i].id, &polys[i]);
    }
    for (size_t i = 0; i < out_count; ++i) {
        const auto point_it = point_by_id.find(out[i].point_id);
        const auto poly_it = poly_by_id.find(out[i].polygon_id);
        if (point_it == point_by_id.end() || poly_it == poly_by_id.end()) {
            out[i].contains = 0;
            continue;
        }
        out[i].contains = exact_point_in_polygon(
            point_it->second->x,
            point_it->second->y,
            *poly_it->second,
            vertices_xy)
            ? 1u
            : 0u;
    }
#endif
    *rows_out      = out;
    *row_count_out = out_count;
}

// ---------- Overlay ----------------------------------------------------------

struct OverlayLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPolygonRef* left_polygons;
    const GpuPolygonRef* right_polygons;
    const float* left_vx;
    const float* left_vy;
    const float* right_vx;
    const float* right_vy;
    GpuOverlayFlags* output;
    uint32_t  right_count;
    uint32_t  left_count;
    uint32_t  launch_count;
    uint32_t  max_edges_per_poly;
};

static void run_overlay_optix(
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        const RtdlPolygonRef* right_polys, size_t right_count,
        const double* right_verts_xy,      size_t right_vert_xy_count,
        RtdlOverlayRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_overlay.init, [&]() {
        std::string ptx = compile_to_ptx(kOverlayKernelSrc, "overlay_kernel.cu");
        g_overlay.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__overlay_probe",
            "__miss__overlay_miss",
            "__intersection__overlay_isect",
            "__anyhit__overlay_anyhit",
            nullptr, 4).release();
    });

    size_t lv_count = left_vert_xy_count / 2;
    size_t rv_count = right_vert_xy_count / 2;

    std::vector<GpuPolygonRef> gpu_lp(left_count), gpu_rp(right_count);
    for (size_t i = 0; i < left_count;  ++i)
        gpu_lp[i] = {left_polys[i].id,  left_polys[i].vertex_offset,  left_polys[i].vertex_count};
    for (size_t i = 0; i < right_count; ++i)
        gpu_rp[i] = {right_polys[i].id, right_polys[i].vertex_offset, right_polys[i].vertex_count};

    std::vector<float> lvx(lv_count), lvy(lv_count), rvx(rv_count), rvy(rv_count);
    for (size_t i = 0; i < lv_count; ++i) {
        lvx[i] = static_cast<float>(left_verts_xy[i * 2]);
        lvy[i] = static_cast<float>(left_verts_xy[i * 2 + 1]);
    }
    for (size_t i = 0; i < rv_count; ++i) {
        rvx[i] = static_cast<float>(right_verts_xy[i * 2]);
        rvy[i] = static_cast<float>(right_verts_xy[i * 2 + 1]);
    }

    // Find max edges across all left polygons for launch stride
    uint32_t max_edges = 0;
    for (size_t i = 0; i < left_count; ++i)
        max_edges = std::max(max_edges, left_polys[i].vertex_count);

    DevPtr d_lp  (sizeof(GpuPolygonRef) * left_count);
    DevPtr d_rp  (sizeof(GpuPolygonRef) * right_count);
    DevPtr d_lvx (sizeof(float) * lv_count);
    DevPtr d_lvy (sizeof(float) * lv_count);
    DevPtr d_rvx (sizeof(float) * rv_count);
    DevPtr d_rvy (sizeof(float) * rv_count);
    upload(d_lp.ptr,  gpu_lp.data(), left_count);
    upload(d_rp.ptr,  gpu_rp.data(), right_count);
    upload(d_lvx.ptr, lvx.data(), lv_count);
    upload(d_lvy.ptr, lvy.data(), lv_count);
    upload(d_rvx.ptr, rvx.data(), rv_count);
    upload(d_rvy.ptr, rvy.data(), rv_count);

    // BVH over right polygon bboxes
    std::vector<OptixAabb> aabbs(right_count);
    for (size_t i = 0; i < right_count; ++i)
        aabbs[i] = aabb_for_polygon(right_verts_xy, right_polys[i].vertex_offset, right_polys[i].vertex_count);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    // Pre-allocated output: left_count * right_count, all zeros
    size_t out_count = left_count * right_count;
    DevPtr d_output(sizeof(GpuOverlayFlags) * out_count);
    CU_CHECK(cuMemsetD8(d_output.ptr, 0, sizeof(GpuOverlayFlags) * out_count));

    uint32_t launch_count = static_cast<uint32_t>(left_count) * max_edges;

    OverlayLaunchParams lp;
    lp.traversable         = accel.handle;
    lp.left_polygons       = reinterpret_cast<const GpuPolygonRef*>(d_lp.ptr);
    lp.right_polygons      = reinterpret_cast<const GpuPolygonRef*>(d_rp.ptr);
    lp.left_vx             = reinterpret_cast<const float*>(d_lvx.ptr);
    lp.left_vy             = reinterpret_cast<const float*>(d_lvy.ptr);
    lp.right_vx            = reinterpret_cast<const float*>(d_rvx.ptr);
    lp.right_vy            = reinterpret_cast<const float*>(d_rvy.ptr);
    lp.output              = reinterpret_cast<GpuOverlayFlags*>(d_output.ptr);
    lp.right_count         = static_cast<uint32_t>(right_count);
    lp.left_count          = static_cast<uint32_t>(left_count);
    lp.launch_count        = launch_count;
    lp.max_edges_per_poly  = max_edges;

    DevPtr d_params(sizeof(OverlayLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_overlay.pipe->pipeline, stream,
                             d_params.ptr, sizeof(OverlayLaunchParams),
                             &g_overlay.pipe->sbt,
                             launch_count, 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    // Also compute PIP flags: for each (left_poly, right_poly) pair, check if
    // any vertex of one polygon is inside the other.  Done on CPU after the
    // GPU LSI pass to keep the device kernel simple.
    std::vector<GpuOverlayFlags> gpu_flags(out_count);
    download(gpu_flags.data(), d_output.ptr, out_count);

    // CPU PIP supplement: match the current RTDL oracle semantics exactly.
    // overlay_compose_cpu checks only the first vertex of each polygon.
#if RTDL_OPTIX_HAS_GEOS
    GeosPreparedPolygonRefs left_geos(left_polys, left_count, left_verts_xy);
    GeosPreparedPolygonRefs right_geos(right_polys, right_count, right_verts_xy);
#endif

    for (size_t li = 0; li < left_count; ++li) {
        for (size_t ri = 0; ri < right_count; ++ri) {
            size_t slot = li * right_count + ri;
            if (gpu_flags[slot].requires_pip) continue; // already set by GPU
            bool found = false;
            if (left_polys[li].vertex_count > 0) {
                double lxv = left_verts_xy[left_polys[li].vertex_offset * 2];
                double lyv = left_verts_xy[left_polys[li].vertex_offset * 2 + 1];
#if RTDL_OPTIX_HAS_GEOS
                if (right_geos.covers(ri, lxv, lyv))
#else
                if (exact_point_in_polygon(lxv, lyv, right_polys[ri], right_verts_xy))
#endif
                    found = true;
            }
            if (!found && right_polys[ri].vertex_count > 0) {
                double rxv = right_verts_xy[right_polys[ri].vertex_offset * 2];
                double ryv = right_verts_xy[right_polys[ri].vertex_offset * 2 + 1];
#if RTDL_OPTIX_HAS_GEOS
                if (left_geos.covers(li, rxv, ryv))
#else
                if (exact_point_in_polygon(rxv, ryv, left_polys[li], left_verts_xy))
#endif
                    found = true;
            }
            if (found)
                gpu_flags[slot].requires_pip = 1;
        }
    }

    auto* out = static_cast<RtdlOverlayRow*>(std::malloc(sizeof(RtdlOverlayRow) * out_count));
    if (!out) throw std::bad_alloc();
    for (size_t i = 0; i < out_count; ++i) {
        size_t li = i / right_count, ri = i % right_count;
        out[i].left_polygon_id  = left_polys[li].id;
        out[i].right_polygon_id = right_polys[ri].id;
        out[i].requires_lsi     = gpu_flags[i].requires_lsi;
        out[i].requires_pip     = gpu_flags[i].requires_pip;
    }
    *rows_out      = out;
    *row_count_out = out_count;
}

// ---------- Ray-triangle hit count ------------------------------------------

struct RayHitCountLaunchParams {
    OptixTraversableHandle traversable;
    const GpuRay*          rays;
    const GpuTriangle*     triangles;
    GpuRayHitRecord*       output;
    uint32_t               ray_count;
};

static void run_ray_hitcount_optix(
        const RtdlRay2D*    rays,      size_t ray_count,
        const RtdlTriangle* triangles, size_t triangle_count,
        RtdlRayHitCountRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_rayhit.init, [&]() {
        std::string ptx = compile_to_ptx(kRayHitCountKernelSrc, "rayhit_kernel.cu");
        g_rayhit.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });

    std::vector<GpuRay>      gpu_rays(ray_count);
    std::vector<GpuTriangle> gpu_tris(triangle_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = {(float)rays[i].ox, (float)rays[i].oy,
                       (float)rays[i].dx, (float)rays[i].dy,
                       (float)rays[i].tmax, rays[i].id};
    for (size_t i = 0; i < triangle_count; ++i)
        gpu_tris[i] = {(float)triangles[i].x0, (float)triangles[i].y0,
                       (float)triangles[i].x1, (float)triangles[i].y1,
                       (float)triangles[i].x2, (float)triangles[i].y2, triangles[i].id};

    DevPtr d_rays(sizeof(GpuRay)      * ray_count);
    DevPtr d_tris(sizeof(GpuTriangle) * triangle_count);
    upload(d_rays.ptr, gpu_rays.data(), ray_count);
    upload(d_tris.ptr, gpu_tris.data(), triangle_count);

    std::vector<OptixAabb> aabbs(triangle_count);
    for (size_t i = 0; i < triangle_count; ++i)
        aabbs[i] = aabb_for_triangle(gpu_tris[i].x0, gpu_tris[i].y0,
                                     gpu_tris[i].x1, gpu_tris[i].y1,
                                     gpu_tris[i].x2, gpu_tris[i].y2);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    DevPtr d_output(sizeof(GpuRayHitRecord) * ray_count);

    RayHitCountLaunchParams lp;
    lp.traversable = accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay*>(d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle*>(d_tris.ptr);
    lp.output      = reinterpret_cast<GpuRayHitRecord*>(d_output.ptr);
    lp.ray_count   = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayHitCountLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayhit.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayHitCountLaunchParams),
                             &g_rayhit.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuRayHitRecord> gpu_rows(ray_count);
    download(gpu_rows.data(), d_output.ptr, ray_count);

    std::vector<uint32_t> exact_counts(ray_count, 0u);
    for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
        uint32_t count = 0u;
        for (size_t triangle_index = 0; triangle_index < triangle_count; ++triangle_index) {
            if (exact_ray_hits_triangle(rays[ray_index], triangles[triangle_index])) {
                count += 1u;
            }
        }
        exact_counts[ray_index] = count;
    }

    auto* out = static_cast<RtdlRayHitCountRow*>(
        std::malloc(sizeof(RtdlRayHitCountRow) * ray_count));
    if (!out && ray_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < ray_count; ++i) {
        out[i].ray_id    = gpu_rows[i].ray_id;
        out[i].hit_count = exact_counts[i];
    }
    *rows_out      = out;
    *row_count_out = ray_count;
}

// ---------- 3-D ray-triangle hit count (OptiX-accelerated) ------------------

struct RayHitCount3DLaunchParams {
    OptixTraversableHandle   traversable;
    const GpuRay3DHost*      rays;
    const GpuTriangle3DHost* triangles;
    GpuRayHitRecord*         output;
    uint32_t                 ray_count;
};

static void run_ray_hitcount_3d_optix(
        const RtdlRay3D*      rays,      size_t ray_count,
        const RtdlTriangle3D* triangles, size_t triangle_count,
        RtdlRayHitCountRow**  rows_out,  size_t* row_count_out)
{
    std::call_once(g_rayhit3d.init, [&]() {
        std::string ptx = compile_to_ptx(kRayHitCount3DKernelSrc, "rayhit3d_kernel.cu");
        g_rayhit3d.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit3d_probe",
            "__miss__rayhit3d_miss",
            "__intersection__rayhit3d_isect",
            "__anyhit__rayhit3d_anyhit",
            nullptr, 2).release();
    });

    // Build GPU ray array: pre-normalise direction so tmax is world-space.
    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        float dx = static_cast<float>(rays[i].dx);
        float dy = static_cast<float>(rays[i].dy);
        float dz = static_cast<float>(rays[i].dz);
        float len = std::sqrt(dx*dx + dy*dy + dz*dz);
        if (len > 1.0e-10f) {
            gpu_rays[i] = {
                static_cast<float>(rays[i].ox),
                static_cast<float>(rays[i].oy),
                static_cast<float>(rays[i].oz),
                dx / len, dy / len, dz / len,
                static_cast<float>(rays[i].tmax) * len,
                rays[i].id
            };
        } else {
            gpu_rays[i] = {
                static_cast<float>(rays[i].ox),
                static_cast<float>(rays[i].oy),
                static_cast<float>(rays[i].oz),
                0.0f, 0.0f, 0.0f, 0.0f, rays[i].id
            };
        }
    }

    std::vector<GpuTriangle3DHost> gpu_tris(triangle_count);
    for (size_t i = 0; i < triangle_count; ++i) {
        gpu_tris[i] = {
            static_cast<float>(triangles[i].x0),
            static_cast<float>(triangles[i].y0),
            static_cast<float>(triangles[i].z0),
            static_cast<float>(triangles[i].x1),
            static_cast<float>(triangles[i].y1),
            static_cast<float>(triangles[i].z1),
            static_cast<float>(triangles[i].x2),
            static_cast<float>(triangles[i].y2),
            static_cast<float>(triangles[i].z2),
            triangles[i].id
        };
    }

    DevPtr d_rays(sizeof(GpuRay3DHost)      * ray_count);
    DevPtr d_tris(sizeof(GpuTriangle3DHost) * triangle_count);
    upload(d_rays.ptr, gpu_rays.data(), ray_count);
    upload(d_tris.ptr, gpu_tris.data(), triangle_count);

    // Build AABB acceleration structure over triangles.
    std::vector<OptixAabb> aabbs(triangle_count);
    for (size_t i = 0; i < triangle_count; ++i) {
        aabbs[i] = aabb_for_triangle_3d(
            gpu_tris[i].x0, gpu_tris[i].y0, gpu_tris[i].z0,
            gpu_tris[i].x1, gpu_tris[i].y1, gpu_tris[i].z1,
            gpu_tris[i].x2, gpu_tris[i].y2, gpu_tris[i].z2);
    }
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    DevPtr d_output(sizeof(GpuRayHitRecord) * ray_count);

    RayHitCount3DLaunchParams lp;
    lp.traversable = accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle3DHost*>(d_tris.ptr);
    lp.output      = reinterpret_cast<GpuRayHitRecord*>(d_output.ptr);
    lp.ray_count   = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayHitCount3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayhit3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayHitCount3DLaunchParams),
                             &g_rayhit3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuRayHitRecord> gpu_rows(ray_count);
    download(gpu_rows.data(), d_output.ptr, ray_count);

    std::vector<uint32_t> exact_counts(ray_count, 0u);
    for (size_t ray_index = 0; ray_index < ray_count; ++ray_index) {
        uint32_t count = 0u;
        for (size_t triangle_index = 0; triangle_index < triangle_count; ++triangle_index) {
            if (exact_ray_hits_triangle_3d(rays[ray_index], triangles[triangle_index])) {
                count += 1u;
            }
        }
        exact_counts[ray_index] = count;
    }

    auto* out = static_cast<RtdlRayHitCountRow*>(
        std::malloc(sizeof(RtdlRayHitCountRow) * ray_count));
    if (!out && ray_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < ray_count; ++i) {
        out[i].ray_id    = gpu_rows[i].ray_id;
        out[i].hit_count = exact_counts[i];
    }
    *rows_out      = out;
    *row_count_out = ray_count;
}

// ---------- Segment-polygon hitcount ----------------------------------------

struct SegPolyLaunchParams {
    OptixTraversableHandle traversable;
    const GpuSegment*    segments;
    const GpuPolygonRef* polygons;
    const float* vertices_x;
    const float* vertices_y;
    GpuSegPolyRecord* output;
    uint32_t segment_count;
};

static void run_seg_poly_hitcount_optix(
        const RtdlSegment*    segments,  size_t segment_count,
        const RtdlPolygonRef* polygons,  size_t polygon_count,
        const double* vertices_xy,       size_t vertex_xy_count,
        RtdlSegmentPolygonHitCountRow** rows_out, size_t* row_count_out)
{
    if (const char* mode = std::getenv("RTDL_OPTIX_SEGPOLY_MODE");
        mode == nullptr || std::string(mode) != "native") {
        run_seg_poly_hitcount_optix_host_indexed(
            segments, segment_count, polygons, polygon_count, vertices_xy, rows_out, row_count_out);
        return;
    }

    if (polygon_count == 0) {
        auto* out = static_cast<RtdlSegmentPolygonHitCountRow*>(
            std::malloc(sizeof(RtdlSegmentPolygonHitCountRow) * segment_count));
        if (!out && segment_count > 0) throw std::bad_alloc();
        for (size_t i = 0; i < segment_count; ++i) {
            out[i].segment_id = segments[i].id;
            out[i].hit_count = 0u;
        }
        *rows_out = out;
        *row_count_out = segment_count;
        return;
    }

    std::call_once(g_segpoly.init, [&]() {
        std::string ptx = compile_to_ptx(kSegPolyHitcountKernelSrc, "segpoly_kernel.cu");
        g_segpoly.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__segpoly_probe",
            "__miss__segpoly_miss",
            "__intersection__segpoly_isect",
            "__anyhit__segpoly_anyhit",
            nullptr,
            4).release();
    });

    const size_t vert_count = vertex_xy_count / 2;
    std::vector<GpuSegment> gpu_segments(segment_count);
    std::vector<GpuPolygonRef> gpu_polygons(polygon_count);
    std::vector<float> vx(vert_count), vy(vert_count);
    for (size_t i = 0; i < segment_count; ++i) {
        gpu_segments[i] = {
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].x1),
            static_cast<float>(segments[i].y1),
            segments[i].id,
        };
    }
    for (size_t i = 0; i < polygon_count; ++i) {
        gpu_polygons[i] = {polygons[i].id, polygons[i].vertex_offset, polygons[i].vertex_count};
    }
    for (size_t i = 0; i < vert_count; ++i) {
        vx[i] = static_cast<float>(vertices_xy[i * 2]);
        vy[i] = static_cast<float>(vertices_xy[i * 2 + 1]);
    }

    DevPtr d_segments(sizeof(GpuSegment) * segment_count);
    DevPtr d_polygons(sizeof(GpuPolygonRef) * polygon_count);
    DevPtr d_vx(sizeof(float) * vert_count);
    DevPtr d_vy(sizeof(float) * vert_count);
    upload(d_segments.ptr, gpu_segments.data(), segment_count);
    upload(d_polygons.ptr, gpu_polygons.data(), polygon_count);
    upload(d_vx.ptr, vx.data(), vert_count);
    upload(d_vy.ptr, vy.data(), vert_count);

    std::vector<OptixAabb> aabbs(polygon_count);
    for (size_t i = 0; i < polygon_count; ++i) {
        aabbs[i] = aabb_for_polygon(vertices_xy, polygons[i].vertex_offset, polygons[i].vertex_count);
    }
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    DevPtr d_output(sizeof(GpuSegPolyRecord) * segment_count);

    SegPolyLaunchParams lp;
    lp.traversable = accel.handle;
    lp.segments = reinterpret_cast<const GpuSegment*>(d_segments.ptr);
    lp.polygons = reinterpret_cast<const GpuPolygonRef*>(d_polygons.ptr);
    lp.vertices_x = reinterpret_cast<const float*>(d_vx.ptr);
    lp.vertices_y = reinterpret_cast<const float*>(d_vy.ptr);
    lp.output = reinterpret_cast<GpuSegPolyRecord*>(d_output.ptr);
    lp.segment_count = static_cast<uint32_t>(segment_count);

    DevPtr d_params(sizeof(SegPolyLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_segpoly.pipe->pipeline, stream,
                             d_params.ptr, sizeof(SegPolyLaunchParams),
                             &g_segpoly.pipe->sbt,
                             static_cast<unsigned>(segment_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuSegPolyRecord> gpu_rows(segment_count);
    download(gpu_rows.data(), d_output.ptr, segment_count);

    auto* out = static_cast<RtdlSegmentPolygonHitCountRow*>(
        std::malloc(sizeof(RtdlSegmentPolygonHitCountRow) * segment_count));
    if (!out && segment_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < segment_count; ++i) {
        out[i].segment_id = gpu_rows[i].segment_id;
        out[i].hit_count = gpu_rows[i].hit_count;
    }
    *rows_out = out;
    *row_count_out = segment_count;
}

// ---------- Point-nearest-segment (CUDA parallel brute-force) ---------------

static void run_point_nearest_segment_cuda(
        const RtdlPoint*   points,   size_t point_count,
        const RtdlSegment* segments, size_t segment_count,
        RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_pns.init, [&]() {
        std::string ptx = compile_to_ptx(kPointNearestKernelSrc, "pns_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_pns.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(&g_pns.fn, g_pns.module, "point_nearest_segment"));
    });

    struct GpuPt  { float x, y; uint32_t id; };
    struct GpuSeg { float x0, y0, x1, y1; uint32_t id; };
    struct GpuPnsRec { uint32_t point_id, segment_id; float distance; };

    std::vector<GpuPt>  gpu_pts (point_count);
    std::vector<GpuSeg> gpu_segs(segment_count);
    for (size_t i = 0; i < point_count; ++i)
        gpu_pts[i] = {(float)points[i].x, (float)points[i].y, points[i].id};
    for (size_t i = 0; i < segment_count; ++i)
        gpu_segs[i] = {(float)segments[i].x0, (float)segments[i].y0,
                       (float)segments[i].x1, (float)segments[i].y1, segments[i].id};

    DevPtr d_pts (sizeof(GpuPt)  * point_count);
    DevPtr d_segs(sizeof(GpuSeg) * segment_count);
    DevPtr d_out (sizeof(GpuPnsRec) * point_count);
    upload(d_pts.ptr,  gpu_pts.data(),  point_count);
    upload(d_segs.ptr, gpu_segs.data(), segment_count);

    uint32_t pc = static_cast<uint32_t>(point_count);
    uint32_t sc = static_cast<uint32_t>(segment_count);
    void* args[] = { &d_pts.ptr, &pc, &d_segs.ptr, &sc, &d_out.ptr };

    unsigned block = 256;
    unsigned grid  = (pc + block - 1) / block;
    CU_CHECK(cuLaunchKernel(g_pns.fn, grid, 1, 1, block, 1, 1,
                             0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));

    std::vector<GpuPnsRec> gpu_rows(point_count);
    download(gpu_rows.data(), d_out.ptr, point_count);

    auto* out = static_cast<RtdlPointNearestSegmentRow*>(
        std::malloc(sizeof(RtdlPointNearestSegmentRow) * point_count));
    if (!out && point_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < point_count; ++i) {
        out[i].point_id   = gpu_rows[i].point_id;
        out[i].segment_id = gpu_rows[i].segment_id;
        out[i].distance   = static_cast<double>(gpu_rows[i].distance);
    }
    *rows_out      = out;
    *row_count_out = point_count;
}
