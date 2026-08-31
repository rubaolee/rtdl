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

extern "C" int rtdl_hiprt_collect_k_bounded_i64(
    const int64_t* candidate_rows,
    size_t candidate_count,
    size_t row_width,
    int64_t* rows_out,
    size_t row_capacity,
    size_t* emitted_count_out,
    uint32_t* overflowed_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (emitted_count_out == nullptr || overflowed_out == nullptr) {
            throw std::runtime_error("emitted_count_out and overflowed_out must not be null");
        }
        *emitted_count_out = 0;
        *overflowed_out = 0;
        if (row_width == 0) {
            throw std::runtime_error("row_width must be positive");
        }
        if (candidate_rows == nullptr && candidate_count != 0) {
            throw std::runtime_error("candidate_rows must not be null when candidate_count is nonzero");
        }
        if (rows_out == nullptr && row_capacity != 0) {
            throw std::runtime_error("rows_out must not be null when row_capacity is nonzero");
        }
        if (candidate_count > std::numeric_limits<size_t>::max() / row_width ||
            row_capacity > std::numeric_limits<size_t>::max() / row_width) {
            throw std::runtime_error("COLLECT_K_BOUNDED row buffer size overflow");
        }

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

extern "C" int rtdl_hiprt_grouped_i64_count_sum(
    const int64_t* group_ids,
    const int64_t* values,
    size_t row_count,
    size_t group_count,
    int64_t* counts_out,
    int64_t* sums_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (counts_out == nullptr && group_count != 0) {
            throw std::runtime_error("counts_out must not be null when group_count is nonzero");
        }
        if (sums_out == nullptr && group_count != 0) {
            throw std::runtime_error("sums_out must not be null when group_count is nonzero");
        }
        if (group_ids == nullptr && row_count != 0) {
            throw std::runtime_error("group_ids must not be null when row_count is nonzero");
        }
        if (values == nullptr && row_count != 0) {
            throw std::runtime_error("values must not be null when row_count is nonzero");
        }
        if (group_count > static_cast<size_t>(std::numeric_limits<int64_t>::max())) {
            throw std::runtime_error("group_count exceeds dense int64 group id range");
        }

        std::vector<int64_t> counts(group_count, 0);
        std::vector<int64_t> sums(group_count, 0);
        for (size_t row_index = 0; row_index < row_count; ++row_index) {
            const int64_t group_id = group_ids[row_index];
            if (group_id < 0 || static_cast<size_t>(group_id) >= group_count) {
                throw std::runtime_error("group_id out of dense group_count range");
            }
            const size_t group_index = static_cast<size_t>(group_id);
            ++counts[group_index];
            sums[group_index] += values[row_index];
        }
        if (group_count != 0) {
            std::memcpy(counts_out, counts.data(), sizeof(int64_t) * group_count);
            std::memcpy(sums_out, sums.data(), sizeof(int64_t) * group_count);
        }
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_grouped_vector_sum_f64x2(
    const int64_t* group_ids,
    const double* values_x,
    const double* values_y,
    size_t row_count,
    size_t group_count,
    double* sums_x_out,
    double* sums_y_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (sums_x_out == nullptr && group_count != 0) {
            throw std::runtime_error("sums_x_out must not be null when group_count is nonzero");
        }
        if (sums_y_out == nullptr && group_count != 0) {
            throw std::runtime_error("sums_y_out must not be null when group_count is nonzero");
        }
        if (group_ids == nullptr && row_count != 0) {
            throw std::runtime_error("group_ids must not be null when row_count is nonzero");
        }
        if (values_x == nullptr && row_count != 0) {
            throw std::runtime_error("values_x must not be null when row_count is nonzero");
        }
        if (values_y == nullptr && row_count != 0) {
            throw std::runtime_error("values_y must not be null when row_count is nonzero");
        }
        if (group_count > static_cast<size_t>(std::numeric_limits<int64_t>::max())) {
            throw std::runtime_error("group_count exceeds dense int64 group id range");
        }

        std::vector<double> sums_x(group_count, 0.0);
        std::vector<double> sums_y(group_count, 0.0);
        for (size_t row_index = 0; row_index < row_count; ++row_index) {
            const int64_t group_id = group_ids[row_index];
            if (group_id < 0 || static_cast<size_t>(group_id) >= group_count) {
                throw std::runtime_error("group_id out of dense group_count range");
            }
            const size_t group_index = static_cast<size_t>(group_id);
            sums_x[group_index] += values_x[row_index];
            sums_y[group_index] += values_y[row_index];
        }
        if (group_count != 0) {
            std::memcpy(sums_x_out, sums_x.data(), sizeof(double) * group_count);
            std::memcpy(sums_y_out, sums_y.data(), sizeof(double) * group_count);
        }
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_columnar_i64_predicate_scan(
    const int64_t* column_values,
    size_t row_count,
    size_t column_count,
    const uint32_t* predicate_column_indices,
    const uint32_t* predicate_ops,
    const int64_t* predicate_values,
    size_t predicate_count,
    int64_t* row_ids_out,
    size_t row_capacity,
    size_t* matched_count_out,
    uint32_t* overflowed_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (matched_count_out == nullptr || overflowed_out == nullptr) {
            throw std::runtime_error("matched_count_out and overflowed_out must not be null");
        }
        *matched_count_out = 0;
        *overflowed_out = 0;
        if (column_values == nullptr && row_count != 0 && column_count != 0) {
            throw std::runtime_error("column_values must not be null when row_count and column_count are nonzero");
        }
        if (predicate_count != 0 &&
            (predicate_column_indices == nullptr || predicate_ops == nullptr || predicate_values == nullptr)) {
            throw std::runtime_error("predicate arrays must not be null when predicate_count is nonzero");
        }
        if (row_ids_out == nullptr && row_capacity != 0) {
            throw std::runtime_error("row_ids_out must not be null when row_capacity is nonzero");
        }
        if (row_count != 0 && column_count > std::numeric_limits<size_t>::max() / row_count) {
            throw std::runtime_error("columnar i64 value buffer size overflow");
        }
        if (row_count > static_cast<size_t>(std::numeric_limits<int64_t>::max())) {
            throw std::runtime_error("row_count exceeds int64 row id range");
        }
        for (size_t predicate_index = 0; predicate_index < predicate_count; ++predicate_index) {
            if (predicate_column_indices[predicate_index] >= column_count) {
                throw std::runtime_error("predicate column index out of column_count range");
            }
            if (predicate_ops[predicate_index] > 5u) {
                throw std::runtime_error("predicate op code must be 0:eq 1:ne 2:lt 3:le 4:gt 5:ge");
            }
        }

        auto compare = [](int64_t left, uint32_t op, int64_t right) -> bool {
            switch (op) {
                case 0u: return left == right;
                case 1u: return left != right;
                case 2u: return left < right;
                case 3u: return left <= right;
                case 4u: return left > right;
                case 5u: return left >= right;
                default: return false;
            }
        };

        size_t matched = 0;
        for (size_t row_index = 0; row_index < row_count; ++row_index) {
            bool keep = true;
            for (size_t predicate_index = 0; predicate_index < predicate_count; ++predicate_index) {
                const size_t column_index = static_cast<size_t>(predicate_column_indices[predicate_index]);
                const int64_t value = column_values[column_index * row_count + row_index];
                if (!compare(value, predicate_ops[predicate_index], predicate_values[predicate_index])) {
                    keep = false;
                    break;
                }
            }
            if (!keep) {
                continue;
            }
            if (matched < row_capacity) {
                row_ids_out[matched] = static_cast<int64_t>(row_index);
            } else {
                *overflowed_out = 1u;
            }
            ++matched;
        }
        *matched_count_out = matched;
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_collect_aggregate_frontier_2d(
    const RtdlAggregateFrontierSource2D* sources,
    size_t source_count,
    const RtdlAggregateFrontierNode2D* nodes,
    size_t node_count,
    const uint64_t* child_offsets,
    const int64_t* child_ids,
    const uint64_t* member_offsets,
    const int64_t* member_ids,
    double theta,
    uint64_t max_rows_per_source,
    uint64_t row_capacity,
    uint32_t deduplicate_fallback_targets,
    int64_t* frontier_rows_out,
    uint64_t* row_offsets_out,
    uint64_t* emitted_count_out,
    uint64_t* attempted_count_out,
    uint32_t* overflowed_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        constexpr size_t kRowWidth = 7;
        constexpr int64_t kKindAggregate = 1;
        constexpr int64_t kKindExact = 2;
        constexpr int64_t kMetadataFlagsNone = 0;
        const uint64_t kUnbounded = std::numeric_limits<uint64_t>::max();

        if (emitted_count_out == nullptr || attempted_count_out == nullptr || overflowed_out == nullptr) {
            throw std::runtime_error("aggregate-frontier count and overflow outputs must not be null");
        }
        *emitted_count_out = 0;
        *attempted_count_out = 0;
        *overflowed_out = 0;
        if (theta <= 0.0 || !std::isfinite(theta)) {
            throw std::runtime_error("aggregate-frontier theta must be positive and finite");
        }
        if (sources == nullptr && source_count != 0) {
            throw std::runtime_error("aggregate-frontier sources must not be null when source_count is nonzero");
        }
        if (nodes == nullptr && node_count != 0) {
            throw std::runtime_error("aggregate-frontier nodes must not be null when node_count is nonzero");
        }
        if (node_count != 0 && (child_offsets == nullptr || member_offsets == nullptr)) {
            throw std::runtime_error("aggregate-frontier CSR offsets must not be null when node_count is nonzero");
        }
        if (frontier_rows_out == nullptr && row_capacity != 0) {
            throw std::runtime_error("frontier_rows_out must not be null when row_capacity is nonzero");
        }
        if (row_offsets_out == nullptr) {
            throw std::runtime_error("row_offsets_out must not be null");
        }
        if (row_capacity > std::numeric_limits<uint64_t>::max() / kRowWidth) {
            throw std::runtime_error("aggregate-frontier row buffer size overflow");
        }
        if (node_count == 0) {
            for (size_t index = 0; index <= source_count; ++index) {
                row_offsets_out[index] = 0;
            }
            return;
        }

        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (nodes[node_index].dfs_index != static_cast<int64_t>(node_index)) {
                throw std::runtime_error("aggregate-frontier nodes must be supplied in contiguous DFS order");
            }
            if (nodes[node_index].half_size < 0.0) {
                throw std::runtime_error("aggregate-frontier node half_size must be non-negative");
            }
            if (child_offsets[node_index] > child_offsets[node_index + 1] ||
                member_offsets[node_index] > member_offsets[node_index + 1]) {
                throw std::runtime_error("aggregate-frontier CSR offsets must be monotonic");
            }
        }
        if (child_offsets[node_count] != 0 && child_ids == nullptr) {
            throw std::runtime_error("aggregate-frontier child_ids must not be null when child CSR is non-empty");
        }
        if (member_offsets[node_count] != 0 && member_ids == nullptr) {
            throw std::runtime_error("aggregate-frontier member_ids must not be null when member CSR is non-empty");
        }

        std::unordered_map<int64_t, size_t> node_index_by_id;
        node_index_by_id.reserve(node_count);
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            const auto inserted = node_index_by_id.emplace(nodes[node_index].id, node_index);
            if (!inserted.second) {
                throw std::runtime_error("aggregate-frontier duplicate node id");
            }
        }

        std::unordered_set<int64_t> child_id_set;
        child_id_set.reserve(static_cast<size_t>(child_offsets[node_count]));
        for (uint64_t child_index = 0; child_index < child_offsets[node_count]; ++child_index) {
            const int64_t child_id = child_ids[child_index];
            if (node_index_by_id.find(child_id) == node_index_by_id.end()) {
                throw std::runtime_error("aggregate-frontier child id is not present in node array");
            }
            child_id_set.insert(child_id);
        }

        std::vector<size_t> root_indices;
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (child_id_set.find(nodes[node_index].id) == child_id_set.end()) {
                root_indices.push_back(node_index);
            }
        }
        if (root_indices.empty()) {
            throw std::runtime_error("aggregate-frontier tree must contain at least one root");
        }

        std::unordered_map<int64_t, int64_t> source_leaf_dfs_by_id;
        for (size_t node_index = 0; node_index < node_count; ++node_index) {
            if (!nodes[node_index].is_leaf) {
                continue;
            }
            for (uint64_t member_index = member_offsets[node_index]; member_index < member_offsets[node_index + 1]; ++member_index) {
                source_leaf_dfs_by_id.emplace(member_ids[member_index], nodes[node_index].dfs_index);
            }
        }

        auto subtree_end = [&](const RtdlAggregateFrontierNode2D& node) -> int64_t {
            return node.resume_index >= 0 ? node.resume_index : static_cast<int64_t>(node_count);
        };

        auto node_contains_source = [&](size_t node_index, int64_t source_id) -> bool {
            const RtdlAggregateFrontierNode2D& node = nodes[node_index];
            const auto found_leaf = source_leaf_dfs_by_id.find(source_id);
            if (found_leaf != source_leaf_dfs_by_id.end()) {
                return node.dfs_index <= found_leaf->second && found_leaf->second < subtree_end(node);
            }
            for (uint64_t member_index = member_offsets[node_index]; member_index < member_offsets[node_index + 1]; ++member_index) {
                if (member_ids[member_index] == source_id) {
                    return true;
                }
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
            if (deduplicate_fallback_targets != 0) {
                fallback_seen.reserve(16);
            }

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
            for (auto root_it = root_indices.rbegin(); root_it != root_indices.rend(); ++root_it) {
                stack.push_back(*root_it);
            }
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
                    if (!append_row(kKindAggregate, node.id, node.id, node.dfs_index, resume_index)) {
                        overflowed = true;
                    }
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
                    if (target_id == source.id) {
                        continue;
                    }
                    if (deduplicate_fallback_targets != 0) {
                        const auto inserted = fallback_seen.insert(target_id);
                        if (!inserted.second) {
                            continue;
                        }
                    }
                    if (!append_row(kKindExact, target_id, node.id, node.dfs_index, resume_index)) {
                        overflowed = true;
                        break;
                    }
                }
            }
            if (overflowed) {
                return;
            }
            frontier_rows.insert(frontier_rows.end(), source_rows.begin(), source_rows.end());
            emitted_rows += static_cast<uint64_t>(source_rows.size() / kRowWidth);
            row_offsets_out[source_index + 1] = emitted_rows;
        }

        if (emitted_rows > row_capacity) {
            mark_overflow(emitted_rows);
            return;
        }
        if (!frontier_rows.empty()) {
            std::memcpy(frontier_rows_out, frontier_rows.data(), sizeof(int64_t) * frontier_rows.size());
        }
        *emitted_count_out = emitted_rows;
        *attempted_count_out = emitted_rows;
    }, error_out, error_size);
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
            hiprtFuncDataSet func_data_set{};
            func_data_set.intersectFuncData = triangle_device.get();
            check_hiprt("hiprtCreateFuncTable", hiprtCreateFuncTable(runtime.context, 1, 1, func_table));
            check_hiprt("hiprtSetFuncTable", hiprtSetFuncTable(runtime.context, func_table, 0, 0, func_data_set));
            *prepared_out = new PreparedRayAnyhit2D(
                std::move(runtime),
                std::move(triangle_device),
                std::move(aabb_device),
                geometry,
                func_table);
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

extern "C" int rtdl_hiprt_group_flags_prepared_ray_anyhit_2d_packed(
    void* prepared,
    const RtdlRay2D* rays,
    const uint32_t* group_indices,
    size_t group_index_count,
    uint32_t* group_flags_out,
    size_t group_count,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT ray-anyhit handle must not be null");
        }
        run_group_flags_prepared_ray_anyhit_2d(
            *reinterpret_cast<PreparedRayAnyhit2D*>(prepared),
            rays,
            group_index_count,
            group_indices,
            group_index_count,
            group_flags_out,
            group_count);
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

extern "C" int rtdl_hiprt_run_ray_closest_hit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayClosestHitRow** rows_out,
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
        if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()) ||
            triangle_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
            throw std::runtime_error("HIPRT 3D ray closest-hit currently supports at most 2^32-1 rays/triangles");
        }
        if (ray_count == 0 || triangle_count == 0) {
            std::vector<RtdlRayClosestHitRow> empty;
            *rows_out = copy_rows_to_heap(empty);
            *row_count_out = 0;
            return;
        }

        std::vector<hiprtFloat3> vertices = encode_triangle_vertices(triangles, triangle_count);
        std::vector<RtdlHiprtRay3DDevice> ray_values = encode_rays(rays, ray_count);
        std::vector<uint32_t> triangle_ids;
        triangle_ids.reserve(triangle_count);
        for (size_t i = 0; i < triangle_count; ++i) {
            triangle_ids.push_back(triangles[i].id);
        }

        HiprtRuntime runtime = create_runtime();
        hiprtSetLogLevel(hiprtLogLevelError);

        DeviceAllocation vertex_device(vertices.size() * sizeof(hiprtFloat3));
        DeviceAllocation ray_device(ray_values.size() * sizeof(RtdlHiprtRay3DDevice));
        DeviceAllocation triangle_id_device(triangle_ids.size() * sizeof(uint32_t));
        std::vector<uint32_t> count_seed(1, 0u);
        DeviceAllocation row_count_device(sizeof(uint32_t));
        copy_host_to_device(vertex_device, vertices);
        copy_host_to_device(ray_device, ray_values);
        copy_host_to_device(triangle_id_device, triangle_ids);
        copy_host_to_device(row_count_device, count_seed);

        hiprtGeometry geometry = build_triangle_geometry(runtime.context, vertex_device, vertices.size(), triangle_count);
        try {
            std::vector<RtdlRayClosestHitRow> output(ray_count);
            DeviceAllocation output_device(output.size() * sizeof(RtdlRayClosestHitRow));

            oroFunction kernel = build_trace_kernel_from_source(
                runtime.context,
                ray_closest_hit_kernel_source_3d(),
                "rtdl_hiprt_ray_closest_hit_3d.cu",
                "RtdlRayClosestHit3DKernel");
            uint32_t block_size = 128;
            uint32_t grid_size = static_cast<uint32_t>((ray_count + block_size - 1) / block_size);
            void* ray_device_ptr = ray_device.get();
            void* triangle_id_device_ptr = triangle_id_device.get();
            void* output_device_ptr = output_device.get();
            void* row_count_device_ptr = row_count_device.get();
            uint32_t ray_count_u32 = static_cast<uint32_t>(ray_count);
            void* args[] = {
                &geometry,
                &ray_device_ptr,
                &triangle_id_device_ptr,
                &ray_count_u32,
                &output_device_ptr,
                &row_count_device_ptr,
            };
            check_oro(
                "oroModuleLaunchKernel",
                oroModuleLaunchKernel(kernel, grid_size, 1, 1, block_size, 1, 1, 0, 0, args, nullptr));

            copy_device_to_host(count_seed, row_count_device);
            const size_t hit_count = count_seed[0];
            if (hit_count > output.size()) {
                throw std::runtime_error("HIPRT 3D ray closest-hit output row count exceeded ray count");
            }
            copy_device_to_host(output, output_device);
            output.resize(hit_count);
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

extern "C" int rtdl_hiprt_count_prepared_fixed_radius_threshold_reached_3d(
    void* prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t threshold,
    size_t* count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT fixed-radius-neighbors handle must not be null");
        }
        count_prepared_fixed_radius_threshold_reached_3d(
            *reinterpret_cast<PreparedFixedRadiusNeighbors3D*>(prepared),
            queries,
            query_count,
            threshold,
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_write_prepared_fixed_radius_threshold_flags_3d(
    void* prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t threshold,
    uint32_t* flags_out,
    size_t flags_count,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT fixed-radius-neighbors handle must not be null");
        }
        write_prepared_fixed_radius_threshold_flags_3d(
            *reinterpret_cast<PreparedFixedRadiusNeighbors3D*>(prepared),
            queries,
            query_count,
            threshold,
            flags_out,
            flags_count);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_aggregate_prepared_fixed_radius_ranked_summary_3d(
    void* prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    uint32_t k_max,
    RtdlFixedRadiusRankedNeighborAggregate* aggregate_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT fixed-radius-neighbors handle must not be null");
        }
        aggregate_prepared_fixed_radius_ranked_summary_3d(
            *reinterpret_cast<PreparedFixedRadiusNeighbors3D*>(prepared),
            queries,
            query_count,
            k_max,
            aggregate_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_aggregate_prepared_fixed_radius_ranked_summary_batch_3d(
    void* prepared,
    const RtdlPoint3D* queries,
    size_t query_count,
    const double* radii,
    const uint32_t* k_values,
    size_t request_count,
    RtdlFixedRadiusRankedNeighborAggregate* aggregates_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT fixed-radius-neighbors handle must not be null");
        }
        aggregate_prepared_fixed_radius_ranked_summary_batch_3d(
            *reinterpret_cast<PreparedFixedRadiusNeighbors3D*>(prepared),
            queries,
            query_count,
            radii,
            k_values,
            request_count,
            aggregates_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_point_group_nearest_witness_2d(
    const RtdlPoint* search_points,
    size_t search_count,
    const RtdlPointGroupBounds2D* groups,
    size_t group_count,
    double max_radius,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        auto prepared = prepare_point_group_nearest_witness_2d_hiprt(
            search_points,
            search_count,
            groups,
            group_count,
            max_radius);
        *prepared_out = prepared.release();
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_point_group_nearest_witness_2d(void* prepared) {
    delete reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared);
}

extern "C" int rtdl_hiprt_run_prepared_point_group_nearest_witness_2d(
    void* prepared,
    const RtdlPoint* queries,
    size_t query_count,
    double radius,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT point_group_nearest handle must not be null");
        }
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_prepared_point_group_nearest_witness_2d_hiprt(
            *reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            queries,
            query_count,
            radius,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_write_prepared_point_group_nearest_witness_2d_device_columns(
    void* prepared,
    const RtdlPoint* queries,
    size_t query_count,
    double radius,
    uint32_t* query_ids_out,
    uint32_t* neighbor_ids_out,
    double* distances_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT point_group_nearest handle must not be null");
        }
        write_prepared_point_group_nearest_witness_device_columns_2d_hiprt(
            *reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            queries,
            query_count,
            radius,
            query_ids_out,
            neighbor_ids_out,
            distances_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_reduce_prepared_point_group_nearest_max_distance_2d(
    void* prepared,
    const RtdlPoint* queries,
    size_t query_count,
    double radius,
    RtdlFixedRadiusNeighborRow* row_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT point_group_nearest handle must not be null");
        }
        reduce_prepared_point_group_nearest_max_distance_2d_hiprt(
            *reinterpret_cast<PreparedPointGroupNearestWitness2D*>(prepared),
            queries,
            query_count,
            radius,
            row_out);
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

extern "C" int rtdl_hiprt_run_segment_pair_intersection(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlSegmentPairIntersectionRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_segment_pair_intersection_2d(left, left_count, right, right_count, rows_out, row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_segment_pair_intersection(
    const RtdlSegment* right,
    size_t right_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        *prepared_out = prepare_segment_pair_intersection_2d(right, right_count);
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_segment_pair_intersection(void* prepared) {
    delete reinterpret_cast<PreparedSegmentPairIntersection2D*>(prepared);
}

extern "C" int rtdl_hiprt_count_prepared_segment_pair_intersection(
    void* prepared,
    const RtdlSegment* left,
    size_t left_count,
    size_t* count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT segment-pair intersection handle must not be null");
        }
        count_prepared_segment_pair_intersection_2d(
            *reinterpret_cast<PreparedSegmentPairIntersection2D*>(prepared),
            left,
            left_count,
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_prepare_aabb_index_2d(
    const RtdlAabb2D* boxes,
    size_t box_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        *prepared_out = prepare_aabb_index_2d_hiprt(boxes, box_count);
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_aabb_index_2d(void* prepared) {
    delete reinterpret_cast<PreparedAabbIndex2D*>(prepared);
}

extern "C" int rtdl_hiprt_count_prepared_aabb_index_2d(
    void* prepared,
    const RtdlPoint* point_queries,
    size_t point_query_count,
    const RtdlAabb2D* box_queries,
    size_t box_query_count,
    uint32_t operation,
    size_t* count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT AABB index handle must not be null");
        }
        count_prepared_aabb_index_2d_hiprt(
            *reinterpret_cast<PreparedAabbIndex2D*>(prepared),
            point_queries,
            point_query_count,
            box_queries,
            box_query_count,
            operation,
            count_out);
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

extern "C" int rtdl_hiprt_run_point_primitive_anyhit_packet(
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

extern "C" int rtdl_hiprt_run_shape_pair_relation_flags(
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    RtdlShapePairRelationRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (rows_out == nullptr || row_count_out == nullptr) {
            throw std::runtime_error("output pointers must not be null");
        }
        *rows_out = nullptr;
        *row_count_out = 0;
        run_shape_pair_relation_flags_2d(
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

extern "C" int rtdl_hiprt_prepare_shape_pair_relation_active_count(
    const RtdlPolygonRef* right_polygons,
    size_t right_count,
    const double* right_vertices_xy,
    size_t right_vertex_xy_count,
    void** prepared_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared_out == nullptr) {
            throw std::runtime_error("prepared_out must not be null");
        }
        *prepared_out = nullptr;
        *prepared_out = prepare_shape_pair_active_count_2d(
            right_polygons,
            right_count,
            right_vertices_xy,
            right_vertex_xy_count);
    }, error_out, error_size);
}

extern "C" void rtdl_hiprt_destroy_prepared_shape_pair_relation_active_count(void* prepared) {
    delete reinterpret_cast<PreparedShapePairActiveCount2D*>(prepared);
}

extern "C" int rtdl_hiprt_count_prepared_shape_pair_relation_active(
    void* prepared,
    const RtdlPolygonRef* left_polygons,
    size_t left_count,
    const double* left_vertices_xy,
    size_t left_vertex_xy_count,
    size_t* count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT shape-pair active-count handle must not be null");
        }
        count_prepared_shape_pair_active_2d(
            *reinterpret_cast<PreparedShapePairActiveCount2D*>(prepared),
            left_polygons,
            left_count,
            left_vertices_xy,
            left_vertex_xy_count,
            count_out);
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

extern "C" int rtdl_hiprt_run_segment_shape_hitcount(
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

extern "C" int rtdl_hiprt_run_segment_shape_anyhit_rows(
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

extern "C" int rtdl_hiprt_run_frontier_edge_traversal_packet(
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

extern "C" int rtdl_hiprt_run_prepared_frontier_edge_traversal_packet(
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

extern "C" int rtdl_hiprt_run_triangle_cycle_candidates(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_index_count,
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
        run_triangle_cycle_candidates(
            row_offsets,
            row_offset_count,
            column_indices,
            edge_index_count,
            seeds,
            seed_count,
            enforce_id_ascending != 0u,
            unique != 0u,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_run_prepared_triangle_cycle_candidates(
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
        run_prepared_triangle_cycle_candidates(
            *reinterpret_cast<PreparedGraphCSR*>(prepared),
            seeds,
            seed_count,
            enforce_id_ascending != 0,
            unique != 0,
            rows_out,
            row_count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_count_triangle_cycle_candidates(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t edge_index_count,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    uint32_t enforce_id_ascending,
    size_t* count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        count_triangle_cycle_candidates(
            row_offsets,
            row_offset_count,
            column_indices,
            edge_index_count,
            seeds,
            seed_count,
            enforce_id_ascending != 0u,
            count_out);
    }, error_out, error_size);
}

extern "C" int rtdl_hiprt_count_prepared_triangle_cycle_candidates(
    void* prepared,
    const RtdlEdgeSeed* seeds,
    size_t seed_count,
    int enforce_id_ascending,
    size_t* count_out,
    char* error_out,
    size_t error_size) {
    return handle_call([&]() {
        if (prepared == nullptr) {
            throw std::runtime_error("prepared HIPRT graph CSR handle must not be null");
        }
        count_prepared_triangle_cycle_candidates(
            *reinterpret_cast<PreparedGraphCSR*>(prepared),
            seeds,
            seed_count,
            enforce_id_ascending != 0,
            count_out);
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

extern "C" int rtdl_hiprt_prepare_columnar_payload(
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

extern "C" void rtdl_hiprt_destroy_prepared_columnar_payload(void* prepared) {
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
            throw std::runtime_error("prepared HIPRT dataset handle must not be null");
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
            throw std::runtime_error("prepared HIPRT dataset handle must not be null");
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
            throw std::runtime_error("prepared HIPRT dataset handle must not be null");
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
