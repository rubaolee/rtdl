constexpr uint32_t kDbKindInt64 = 1u;
constexpr uint32_t kDbKindFloat64 = 2u;
constexpr uint32_t kDbKindBool = 3u;
constexpr uint32_t kDbKindText = 4u;

constexpr uint32_t kDbOpEq = 1u;
constexpr uint32_t kDbOpLt = 2u;
constexpr uint32_t kDbOpLe = 3u;
constexpr uint32_t kDbOpGt = 4u;
constexpr uint32_t kDbOpGe = 5u;
constexpr uint32_t kDbOpBetween = 6u;

constexpr size_t kDbMaxRowsPerJob = 1000000;
constexpr size_t kDbMaxCandidateRowsPerJob = 1000000;
constexpr size_t kDbMaxGroupsPerJob = 65536;
constexpr float kDbBoxPad = 1.0e-3f;
constexpr float kGraphEdgeBoxPad = 1.0e-3f;

struct DbPrimaryAxis {
    size_t field_index;
    std::vector<double> sorted_values;
    int64_t encoded_lo;
    int64_t encoded_hi;
};

struct DbRowMeta {
    size_t row_index;
    uint32_t row_id;
};

struct DbScanLaunchParams {
    OptixTraversableHandle traversable;
    uint32_t* hit_words;
    uint32_t hit_word_count;
    uint32_t x_lo;
    uint32_t y_lo;
    uint32_t z_lo;
    uint32_t z_hi;
    uint32_t x_count;
    uint32_t y_count;
};

struct OptixDbDatasetImpl {
    std::vector<std::string> field_names;
    std::vector<RtdlDbField> fields;
    std::vector<std::string> scalar_strings;
    std::vector<RtdlDbScalar> row_values;
    size_t row_count = 0;
    std::vector<DbPrimaryAxis> primary_axes;
    std::vector<DbRowMeta> row_metas;
    std::vector<OptixAabb> aabbs;
    AccelHolder accel;
};

struct GpuGraphEdge {
    uint32_t src;
    uint32_t dst;
};

struct GpuGraphTriangleCandidate {
    uint32_t seed_index;
    uint32_t side;
    uint32_t dst_vertex;
};

thread_local double g_optix_last_db_traversal_s = 0.0;
thread_local double g_optix_last_db_bitset_copy_s = 0.0;
thread_local double g_optix_last_db_exact_filter_s = 0.0;
thread_local double g_optix_last_db_output_pack_s = 0.0;
thread_local size_t g_optix_last_db_raw_candidate_count = 0;
thread_local size_t g_optix_last_db_emitted_count = 0;

extern "C" int rtdl_optix_columnar_payload_get_last_phase_timings(
        double* traversal,
        double* bitset_copy,
        double* exact_filter,
        double* output_pack,
        size_t* raw_candidate_count,
        size_t* emitted_count)
{
    if (traversal) *traversal = g_optix_last_db_traversal_s;
    if (bitset_copy) *bitset_copy = g_optix_last_db_bitset_copy_s;
    if (exact_filter) *exact_filter = g_optix_last_db_exact_filter_s;
    if (output_pack) *output_pack = g_optix_last_db_output_pack_s;
    if (raw_candidate_count) *raw_candidate_count = g_optix_last_db_raw_candidate_count;
    if (emitted_count) *emitted_count = g_optix_last_db_emitted_count;
    return 0;
}

static size_t db_find_field_index_or_throw(
        const RtdlDbField* fields,
        size_t field_count,
        const char* name)
{
    if (!name) {
        throw std::runtime_error("DB field name must not be null");
    }
    for (size_t index = 0; index < field_count; ++index) {
        if (fields[index].name && std::strcmp(fields[index].name, name) == 0) {
            return index;
        }
    }
    throw std::runtime_error(std::string("unknown DB field: ") + name);
}

static const RtdlDbScalar& db_row_value(
        const RtdlDbScalar* row_values,
        size_t row_index,
        size_t field_count,
        size_t field_index)
{
    return row_values[row_index * field_count + field_index];
}

static bool db_scalar_is_numeric(const RtdlDbScalar& value)
{
    return value.kind == kDbKindInt64 || value.kind == kDbKindFloat64 || value.kind == kDbKindBool;
}

static bool db_field_kind_is_numeric(uint32_t kind)
{
    return kind == kDbKindInt64 || kind == kDbKindFloat64 || kind == kDbKindBool;
}

static double db_scalar_as_double(const RtdlDbScalar& value)
{
    if (value.kind == kDbKindInt64 || value.kind == kDbKindBool) {
        return static_cast<double>(value.int_value);
    }
    if (value.kind == kDbKindFloat64) {
        return value.double_value;
    }
    throw std::runtime_error("DB scalar is not numeric");
}

static int db_compare_scalar(const RtdlDbScalar& left, const RtdlDbScalar& right)
{
    if (left.kind != right.kind) {
        const double lhs = db_scalar_as_double(left);
        const double rhs = db_scalar_as_double(right);
        if (lhs < rhs) return -1;
        if (lhs > rhs) return 1;
        return 0;
    }
    switch (left.kind) {
        case kDbKindInt64:
        case kDbKindBool:
            if (left.int_value < right.int_value) return -1;
            if (left.int_value > right.int_value) return 1;
            return 0;
        case kDbKindFloat64:
            if (left.double_value < right.double_value) return -1;
            if (left.double_value > right.double_value) return 1;
            return 0;
        case kDbKindText: {
            const char* lhs = left.string_value ? left.string_value : "";
            const char* rhs = right.string_value ? right.string_value : "";
            const int cmp = std::strcmp(lhs, rhs);
            if (cmp < 0) return -1;
            if (cmp > 0) return 1;
            return 0;
        }
        default:
            throw std::runtime_error("unsupported DB scalar kind");
    }
}

static bool db_clause_matches_scalar(const RtdlDbClause& clause, const RtdlDbScalar& candidate)
{
    const int cmp_lo = db_compare_scalar(candidate, clause.value);
    switch (clause.op) {
        case kDbOpEq:
            return cmp_lo == 0;
        case kDbOpLt:
            return cmp_lo < 0;
        case kDbOpLe:
            return cmp_lo <= 0;
        case kDbOpGt:
            return cmp_lo > 0;
        case kDbOpGe:
            return cmp_lo >= 0;
        case kDbOpBetween:
            return cmp_lo >= 0 && db_compare_scalar(candidate, clause.value_hi) <= 0;
        default:
            throw std::runtime_error("unsupported DB clause op");
    }
}

static bool db_row_matches_all_clauses(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_index,
        const RtdlDbClause* clauses,
        size_t clause_count)
{
    for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
        const size_t field_index = db_find_field_index_or_throw(fields, field_count, clauses[clause_index].field);
        const RtdlDbScalar& candidate = db_row_value(row_values, row_index, field_count, field_index);
        if (!db_clause_matches_scalar(clauses[clause_index], candidate)) {
            return false;
        }
    }
    return true;
}

static std::vector<double> db_sorted_distinct_numeric_values(
        const RtdlDbScalar* row_values,
        size_t row_count,
        size_t field_count,
        size_t field_index)
{
    std::vector<double> values;
    values.reserve(row_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        const RtdlDbScalar& value = db_row_value(row_values, row_index, field_count, field_index);
        if (!db_scalar_is_numeric(value)) {
            throw std::runtime_error("first-wave OptiX DB lowering requires numeric primary scan clauses");
        }
        values.push_back(db_scalar_as_double(value));
    }
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
    return values;
}

static bool db_clause_matches_numeric_value(const RtdlDbClause& clause, double value)
{
    const double lo = db_scalar_as_double(clause.value);
    switch (clause.op) {
        case kDbOpEq:
            return value == lo;
        case kDbOpLt:
            return value < lo;
        case kDbOpLe:
            return value <= lo;
        case kDbOpGt:
            return value > lo;
        case kDbOpGe:
            return value >= lo;
        case kDbOpBetween:
            return value >= lo && value <= db_scalar_as_double(clause.value_hi);
        default:
            throw std::runtime_error("unsupported DB clause op");
    }
}

static DbPrimaryAxis db_make_primary_axis(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const RtdlDbClause& clause)
{
    const size_t field_index = db_find_field_index_or_throw(fields, field_count, clause.field);
    const std::vector<double> sorted_values =
        db_sorted_distinct_numeric_values(row_values, row_count, field_count, field_index);
    int64_t encoded_lo = -1;
    int64_t encoded_hi = -1;
    for (size_t index = 0; index < sorted_values.size(); ++index) {
        if (!db_clause_matches_numeric_value(clause, sorted_values[index])) {
            continue;
        }
        const int64_t encoded = static_cast<int64_t>(index + 1);
        if (encoded_lo < 0) {
            encoded_lo = encoded;
        }
        encoded_hi = encoded;
    }
    if (encoded_lo < 0 || encoded_hi < 0) {
        return {field_index, sorted_values, 1, 0};
    }
    return {field_index, sorted_values, encoded_lo, encoded_hi};
}

static DbPrimaryAxis db_make_full_primary_axis(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const char* field_name)
{
    const size_t field_index = db_find_field_index_or_throw(fields, field_count, field_name);
    if (!db_field_kind_is_numeric(fields[field_index].kind)) {
        throw std::runtime_error("first-wave OptiX prepared DB datasets require numeric primary RT axes");
    }
    const std::vector<double> sorted_values =
        db_sorted_distinct_numeric_values(row_values, row_count, field_count, field_index);
    return {
        field_index,
        sorted_values,
        1,
        sorted_values.empty() ? 0 : static_cast<int64_t>(sorted_values.size())};
}

static DbPrimaryAxis db_axis_with_clause_range(const DbPrimaryAxis& axis, const RtdlDbClause& clause)
{
    DbPrimaryAxis ranged = axis;
    int64_t encoded_lo = -1;
    int64_t encoded_hi = -1;
    for (size_t index = 0; index < axis.sorted_values.size(); ++index) {
        if (!db_clause_matches_numeric_value(clause, axis.sorted_values[index])) {
            continue;
        }
        const int64_t encoded = static_cast<int64_t>(index + 1);
        if (encoded_lo < 0) {
            encoded_lo = encoded;
        }
        encoded_hi = encoded;
    }
    ranged.encoded_lo = encoded_lo < 0 ? 1 : encoded_lo;
    ranged.encoded_hi = encoded_hi < 0 ? 0 : encoded_hi;
    return ranged;
}

static int64_t db_encode_axis_value(const DbPrimaryAxis& axis, const RtdlDbScalar& value)
{
    const double needle = db_scalar_as_double(value);
    const auto it = std::lower_bound(axis.sorted_values.begin(), axis.sorted_values.end(), needle);
    if (it == axis.sorted_values.end() || *it != needle) {
        throw std::runtime_error("failed to encode OptiX DB primary-axis value");
    }
    return static_cast<int64_t>(std::distance(axis.sorted_values.begin(), it) + 1);
}

static std::vector<DbRowMeta> db_build_row_metas(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count)
{
    const size_t row_id_index = db_find_field_index_or_throw(fields, field_count, "row_id");
    std::vector<DbRowMeta> metas;
    metas.reserve(row_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        const RtdlDbScalar& row_id_value = db_row_value(row_values, row_index, field_count, row_id_index);
        metas.push_back({row_index, static_cast<uint32_t>(row_id_value.int_value)});
    }
    return metas;
}

static std::vector<OptixAabb> db_build_row_aabbs(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const std::vector<DbPrimaryAxis>& axes)
{
    std::vector<OptixAabb> aabbs;
    aabbs.reserve(row_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        const float x = axes.size() >= 1
            ? static_cast<float>(db_encode_axis_value(axes[0], db_row_value(row_values, row_index, field_count, axes[0].field_index)))
            : 1.0f;
        const float y = axes.size() >= 2
            ? static_cast<float>(db_encode_axis_value(axes[1], db_row_value(row_values, row_index, field_count, axes[1].field_index)))
            : 1.0f;
        const float z = axes.size() >= 3
            ? static_cast<float>(db_encode_axis_value(axes[2], db_row_value(row_values, row_index, field_count, axes[2].field_index)))
            : 1.0f;
        OptixAabb aabb;
        aabb.minX = x - kDbBoxPad;
        aabb.minY = y - kDbBoxPad;
        aabb.minZ = z - kDbBoxPad;
        aabb.maxX = x + kDbBoxPad;
        aabb.maxY = y + kDbBoxPad;
        aabb.maxZ = z + kDbBoxPad;
        aabbs.push_back(aabb);
    }
    return aabbs;
}

static std::vector<DbPrimaryAxis> db_dataset_query_axes(
        const OptixDbDatasetImpl& dataset,
        const RtdlDbClause* clauses,
        size_t clause_count)
{
    std::vector<DbPrimaryAxis> axes = dataset.primary_axes;
    for (DbPrimaryAxis& axis : axes) {
        const char* axis_field = dataset.fields[axis.field_index].name;
        for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
            if (std::strcmp(axis_field, clauses[clause_index].field) != 0) {
                continue;
            }
            axis = db_axis_with_clause_range(axis, clauses[clause_index]);
            break;
        }
    }
    return axes;
}

static std::vector<const char*> db_default_primary_fields(const RtdlDbField* fields, size_t field_count)
{
    std::vector<const char*> names;
    for (size_t index = 0; index < field_count && names.size() < 3; ++index) {
        if (std::strcmp(fields[index].name, "row_id") == 0) {
            continue;
        }
        if (db_field_kind_is_numeric(fields[index].kind)) {
            names.push_back(fields[index].name);
        }
    }
    return names;
}

static size_t db_count_scalar_strings(const RtdlDbScalar* row_values, size_t scalar_count)
{
    size_t count = 0;
    for (size_t index = 0; index < scalar_count; ++index) {
        if (row_values[index].kind == kDbKindText && row_values[index].string_value) {
            ++count;
        }
    }
    return count;
}

static void db_copy_dataset_payload(
        OptixDbDatasetImpl& dataset,
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count)
{
    dataset.field_names.reserve(field_count);
    for (size_t index = 0; index < field_count; ++index) {
        dataset.field_names.emplace_back(fields[index].name ? fields[index].name : "");
    }
    dataset.fields.reserve(field_count);
    for (size_t index = 0; index < field_count; ++index) {
        dataset.fields.push_back({dataset.field_names[index].c_str(), fields[index].kind});
    }

    const size_t scalar_count = row_count * field_count;
    dataset.scalar_strings.reserve(db_count_scalar_strings(row_values, scalar_count));
    dataset.row_values.reserve(scalar_count);
    for (size_t index = 0; index < scalar_count; ++index) {
        RtdlDbScalar copied = row_values[index];
        if (copied.kind == kDbKindText && copied.string_value) {
            dataset.scalar_strings.emplace_back(copied.string_value);
            copied.string_value = dataset.scalar_strings.back().c_str();
        }
        dataset.row_values.push_back(copied);
    }
    dataset.row_count = row_count;
}

static void db_validate_columnar_inputs(
        const RtdlPayloadField* fields,
        size_t field_count,
        size_t row_count)
{
    if (!fields || field_count == 0) {
        throw std::runtime_error("payload fields must not be null");
    }
    if (row_count > kDbMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX DB lowering supports at most 1000000 rows per RT job");
    }
    for (size_t field_index = 0; field_index < field_count; ++field_index) {
        const RtdlPayloadField& field = fields[field_index];
        if (!field.name) {
            throw std::runtime_error("field name must not be null");
        }
        if ((field.kind == kDbKindInt64 || field.kind == kDbKindBool) && !field.int_values) {
            throw std::runtime_error("field integer/bool values must not be null");
        }
        if (field.kind == kDbKindFloat64 && !field.double_values) {
            throw std::runtime_error("field float values must not be null");
        }
        if (field.kind == kDbKindText && !field.string_values) {
            throw std::runtime_error("field text values must not be null");
        }
    }
}

static void db_copy_dataset_columnar_payload(
        OptixDbDatasetImpl& dataset,
        const RtdlPayloadField* fields,
        size_t field_count,
        size_t row_count)
{
    dataset.field_names.reserve(field_count);
    for (size_t field_index = 0; field_index < field_count; ++field_index) {
        dataset.field_names.emplace_back(fields[field_index].name ? fields[field_index].name : "");
    }
    dataset.fields.reserve(field_count);
    for (size_t field_index = 0; field_index < field_count; ++field_index) {
        dataset.fields.push_back({dataset.field_names[field_index].c_str(), fields[field_index].kind});
    }

    size_t string_count = 0;
    for (size_t field_index = 0; field_index < field_count; ++field_index) {
        if (fields[field_index].kind == kDbKindText) {
            string_count += row_count;
        }
    }
    dataset.scalar_strings.reserve(string_count);
    dataset.row_values.reserve(row_count * field_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        for (size_t field_index = 0; field_index < field_count; ++field_index) {
            const RtdlPayloadField& field = fields[field_index];
            RtdlDbScalar value{};
            value.kind = field.kind;
            if (field.kind == kDbKindFloat64) {
                value.double_value = field.double_values[row_index];
            } else if (field.kind == kDbKindText) {
                const char* text = field.string_values[row_index];
                dataset.scalar_strings.emplace_back(text ? text : "");
                value.string_value = dataset.scalar_strings.back().c_str();
            } else {
                value.int_value = field.int_values[row_index];
            }
            dataset.row_values.push_back(value);
        }
    }
    dataset.row_count = row_count;
}

static void db_validate_db_inputs(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const RtdlDbClause* clauses,
        size_t clause_count)
{
    if (!fields || field_count == 0 || !row_values) {
        throw std::runtime_error("DB table inputs must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    if (row_count > kDbMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX DB lowering supports at most 1000000 rows per RT job");
    }
}

static std::vector<size_t> db_collect_candidate_row_indices_optix(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const RtdlDbClause* clauses,
        size_t clause_count)
{
    std::vector<DbPrimaryAxis> axes;
    axes.reserve(std::min<size_t>(clause_count, 3));
    for (size_t i = 0; i < clause_count && i < 3; ++i) {
        axes.push_back(db_make_primary_axis(fields, field_count, row_values, row_count, clauses[i]));
    }
    const std::vector<OptixAabb> aabbs = db_build_row_aabbs(fields, field_count, row_values, row_count, axes);

    const uint32_t x_lo = axes.size() >= 1 ? static_cast<uint32_t>(axes[0].encoded_lo) : 1u;
    const uint32_t x_hi = axes.size() >= 1 ? static_cast<uint32_t>(axes[0].encoded_hi) : 1u;
    const uint32_t y_lo = axes.size() >= 2 ? static_cast<uint32_t>(axes[1].encoded_lo) : 1u;
    const uint32_t y_hi = axes.size() >= 2 ? static_cast<uint32_t>(axes[1].encoded_hi) : 1u;
    const uint32_t z_lo = axes.size() >= 3 ? static_cast<uint32_t>(axes[2].encoded_lo) : 1u;
    const uint32_t z_hi = axes.size() >= 3 ? static_cast<uint32_t>(axes[2].encoded_hi) : 1u;

    if (x_lo > x_hi || y_lo > y_hi || z_lo > z_hi) {
        return {};
    }

    std::call_once(g_dbscan.init, [&]() {
        std::string ptx = compile_to_ptx(kDbScanKernelSrc, "db_scan_kernel.cu");
        g_dbscan.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__db_scan_probe",
            "__miss__db_scan_miss",
            "__intersection__db_scan_isect",
            "__anyhit__db_scan_anyhit",
            nullptr,
            0).release();
    });

    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    const uint32_t hit_word_count = static_cast<uint32_t>((row_count + 31u) / 32u);
    DevPtr d_hit_words(sizeof(uint32_t) * hit_word_count);
    CU_CHECK(cuMemsetD8(d_hit_words.ptr, 0, sizeof(uint32_t) * hit_word_count));

    const uint32_t x_count = x_hi - x_lo + 1u;
    const uint32_t y_count = y_hi - y_lo + 1u;
    DbScanLaunchParams lp;
    lp.traversable = accel.handle;
    lp.hit_words = reinterpret_cast<uint32_t*>(d_hit_words.ptr);
    lp.hit_word_count = hit_word_count;
    lp.x_lo = x_lo;
    lp.y_lo = y_lo;
    lp.z_lo = z_lo;
    lp.z_hi = z_hi;
    lp.x_count = x_count;
    lp.y_count = y_count;

    DevPtr d_params(sizeof(DbScanLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(
        g_dbscan.pipe->pipeline,
        stream,
        d_params.ptr,
        sizeof(DbScanLaunchParams),
        &g_dbscan.pipe->sbt,
        x_count,
        y_count,
        1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<uint32_t> hit_words(hit_word_count, 0u);
    if (hit_word_count > 0) {
        download(hit_words.data(), d_hit_words.ptr, hit_word_count);
    }

    std::vector<size_t> row_indices;
    row_indices.reserve(std::min(row_count, kDbMaxCandidateRowsPerJob));
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        const uint32_t word = static_cast<uint32_t>(row_index >> 5);
        const uint32_t bit = 1u << (row_index & 31u);
        if ((hit_words[word] & bit) == 0u) {
            continue;
        }
        if (row_indices.size() >= kDbMaxCandidateRowsPerJob) {
            throw std::runtime_error("first-wave OptiX DB lowering exceeded the 1000000-candidate ceiling");
        }
        if (!db_row_matches_all_clauses(fields, field_count, row_values, row_index, clauses, clause_count)) {
            continue;
        }
        row_indices.push_back(row_index);
    }
    return row_indices;
}

static std::vector<size_t> db_collect_candidate_row_indices_optix_prepared(
        const OptixDbDatasetImpl& dataset,
        const RtdlDbClause* clauses,
        size_t clause_count)
{
    const std::vector<DbPrimaryAxis> axes = db_dataset_query_axes(dataset, clauses, clause_count);
    const uint32_t x_lo = axes.size() >= 1 ? static_cast<uint32_t>(axes[0].encoded_lo) : 1u;
    const uint32_t x_hi = axes.size() >= 1 ? static_cast<uint32_t>(axes[0].encoded_hi) : 1u;
    const uint32_t y_lo = axes.size() >= 2 ? static_cast<uint32_t>(axes[1].encoded_lo) : 1u;
    const uint32_t y_hi = axes.size() >= 2 ? static_cast<uint32_t>(axes[1].encoded_hi) : 1u;
    const uint32_t z_lo = axes.size() >= 3 ? static_cast<uint32_t>(axes[2].encoded_lo) : 1u;
    const uint32_t z_hi = axes.size() >= 3 ? static_cast<uint32_t>(axes[2].encoded_hi) : 1u;

    if (x_lo > x_hi || y_lo > y_hi || z_lo > z_hi) {
        return {};
    }

    std::call_once(g_dbscan.init, [&]() {
        std::string ptx = compile_to_ptx(kDbScanKernelSrc, "db_scan_kernel.cu");
        g_dbscan.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__db_scan_probe",
            "__miss__db_scan_miss",
            "__intersection__db_scan_isect",
            "__anyhit__db_scan_anyhit",
            nullptr,
            0).release();
    });

    const uint32_t hit_word_count = static_cast<uint32_t>((dataset.row_count + 31u) / 32u);
    DevPtr d_hit_words(sizeof(uint32_t) * hit_word_count);
    CU_CHECK(cuMemsetD8(d_hit_words.ptr, 0, sizeof(uint32_t) * hit_word_count));

    const uint32_t x_count = x_hi - x_lo + 1u;
    const uint32_t y_count = y_hi - y_lo + 1u;
    DbScanLaunchParams lp;
    lp.traversable = dataset.accel.handle;
    lp.hit_words = reinterpret_cast<uint32_t*>(d_hit_words.ptr);
    lp.hit_word_count = hit_word_count;
    lp.x_lo = x_lo;
    lp.y_lo = y_lo;
    lp.z_lo = z_lo;
    lp.z_hi = z_hi;
    lp.x_count = x_count;
    lp.y_count = y_count;

    DevPtr d_params(sizeof(DbScanLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(
        g_dbscan.pipe->pipeline,
        stream,
        d_params.ptr,
        sizeof(DbScanLaunchParams),
        &g_dbscan.pipe->sbt,
        x_count,
        y_count,
        1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_db_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    std::vector<uint32_t> hit_words(hit_word_count, 0u);
    if (hit_word_count > 0) {
        download(hit_words.data(), d_hit_words.ptr, hit_word_count);
    }
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_db_bitset_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();

    auto t_start_filter = std::chrono::steady_clock::now();
    size_t raw_candidate_count = 0;
    std::vector<size_t> row_indices;
    row_indices.reserve(std::min(dataset.row_count, kDbMaxCandidateRowsPerJob));
    for (size_t row_index = 0; row_index < dataset.row_count; ++row_index) {
        const uint32_t word = static_cast<uint32_t>(row_index >> 5);
        const uint32_t bit = 1u << (row_index & 31u);
        if ((hit_words[word] & bit) == 0u) {
            continue;
        }
        raw_candidate_count += 1;
        if (row_indices.size() >= kDbMaxCandidateRowsPerJob) {
            throw std::runtime_error("first-wave OptiX DB lowering exceeded the 1000000-candidate ceiling");
        }
        if (!db_row_matches_all_clauses(
                dataset.fields.data(),
                dataset.fields.size(),
                dataset.row_values.data(),
                row_index,
                clauses,
                clause_count)) {
            continue;
        }
        row_indices.push_back(row_index);
    }
    auto t_end_filter = std::chrono::steady_clock::now();
    g_optix_last_db_exact_filter_s = std::chrono::duration<double>(t_end_filter - t_start_filter).count();
    g_optix_last_db_raw_candidate_count = raw_candidate_count;
    g_optix_last_db_emitted_count = row_indices.size();
    return row_indices;
}

static void run_db_conjunctive_scan_optix(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const RtdlDbClause* clauses,
        size_t clause_count,
        RtdlDbRowIdRow** rows_out,
        size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (!fields || field_count == 0 || !row_values) {
        throw std::runtime_error("DB table inputs must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    if (row_count > kDbMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX DB lowering supports at most 1000000 rows per RT job");
    }
    const std::vector<DbRowMeta> row_metas = db_build_row_metas(fields, field_count, row_values, row_count);
    const std::vector<size_t> candidate_row_indices =
        db_collect_candidate_row_indices_optix(fields, field_count, row_values, row_count, clauses, clause_count);
    std::vector<RtdlDbRowIdRow> rows;
    rows.reserve(candidate_row_indices.size());
    for (size_t row_index : candidate_row_indices) {
        rows.push_back({row_metas[row_index].row_id});
    }

    std::sort(rows.begin(), rows.end(), [](const RtdlDbRowIdRow& left, const RtdlDbRowIdRow& right) {
        return left.row_id < right.row_id;
    });

    auto* out = static_cast<RtdlDbRowIdRow*>(std::malloc(sizeof(RtdlDbRowIdRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlDbRowIdRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_db_grouped_count_optix(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const RtdlDbClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        RtdlDbGroupedCountRow** rows_out,
        size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (!fields || field_count == 0 || !row_values || !group_key_field) {
        throw std::runtime_error("DB grouped_count inputs must not be null");
    }
    if (row_count > kDbMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX DB lowering supports at most 1000000 rows per RT job");
    }
    const size_t group_field_index = db_find_field_index_or_throw(fields, field_count, group_key_field);
    const std::vector<size_t> candidate_row_indices =
        db_collect_candidate_row_indices_optix(fields, field_count, row_values, row_count, clauses, clause_count);
    std::unordered_map<int64_t, int64_t> counts;
    for (size_t row_index : candidate_row_indices) {
        const RtdlDbScalar& group_value = db_row_value(row_values, row_index, field_count, group_field_index);
        counts[group_value.int_value] += 1;
        if (counts.size() > kDbMaxGroupsPerJob) {
            throw std::runtime_error("first-wave OptiX DB grouped kernels exceeded the 65536-group ceiling");
        }
    }
    std::vector<RtdlDbGroupedCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& entry : counts) {
        rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbGroupedCountRow& left, const RtdlDbGroupedCountRow& right) {
        return left.group_key < right.group_key;
    });
    auto* out = static_cast<RtdlDbGroupedCountRow*>(std::malloc(sizeof(RtdlDbGroupedCountRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlDbGroupedCountRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_db_grouped_sum_optix(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const RtdlDbClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlDbGroupedSumRow** rows_out,
        size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (!fields || field_count == 0 || !row_values || !group_key_field || !value_field) {
        throw std::runtime_error("DB grouped_sum inputs must not be null");
    }
    if (row_count > kDbMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX DB lowering supports at most 1000000 rows per RT job");
    }
    const size_t group_field_index = db_find_field_index_or_throw(fields, field_count, group_key_field);
    const size_t value_field_index = db_find_field_index_or_throw(fields, field_count, value_field);
    if (fields[value_field_index].kind != kDbKindInt64 && fields[value_field_index].kind != kDbKindBool) {
        throw std::runtime_error("first-wave OptiX grouped_sum supports integer-compatible value fields only");
    }
    const std::vector<size_t> candidate_row_indices =
        db_collect_candidate_row_indices_optix(fields, field_count, row_values, row_count, clauses, clause_count);
    std::unordered_map<int64_t, int64_t> sums;
    for (size_t row_index : candidate_row_indices) {
        const RtdlDbScalar& group_value = db_row_value(row_values, row_index, field_count, group_field_index);
        const RtdlDbScalar& sum_value = db_row_value(row_values, row_index, field_count, value_field_index);
        sums[group_value.int_value] += sum_value.int_value;
        if (sums.size() > kDbMaxGroupsPerJob) {
            throw std::runtime_error("first-wave OptiX DB grouped kernels exceeded the 65536-group ceiling");
        }
    }
    std::vector<RtdlDbGroupedSumRow> rows;
    rows.reserve(sums.size());
    for (const auto& entry : sums) {
        rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbGroupedSumRow& left, const RtdlDbGroupedSumRow& right) {
        return left.group_key < right.group_key;
    });
    auto* out = static_cast<RtdlDbGroupedSumRow*>(std::malloc(sizeof(RtdlDbGroupedSumRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlDbGroupedSumRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static OptixDbDatasetImpl* create_db_dataset_optix(
        const RtdlDbField* fields,
        size_t field_count,
        const RtdlDbScalar* row_values,
        size_t row_count,
        const char* const* primary_fields,
        size_t primary_field_count)
{
    db_validate_db_inputs(fields, field_count, row_values, row_count, nullptr, 0);
    std::unique_ptr<OptixDbDatasetImpl> dataset(new OptixDbDatasetImpl());
    db_copy_dataset_payload(*dataset, fields, field_count, row_values, row_count);

    std::vector<const char*> primary_names;
    if (primary_field_count > 0) {
        if (!primary_fields) {
            throw std::runtime_error("primary_fields pointer must not be null when primary_field_count > 0");
        }
        primary_names.reserve(std::min<size_t>(primary_field_count, 3));
        for (size_t index = 0; index < primary_field_count && index < 3; ++index) {
            primary_names.push_back(primary_fields[index]);
        }
    } else {
        primary_names = db_default_primary_fields(dataset->fields.data(), dataset->fields.size());
    }
    if (primary_names.empty()) {
        throw std::runtime_error("OptiX prepared DB dataset requires at least one numeric primary RT axis");
    }

    dataset->primary_axes.reserve(primary_names.size());
    for (const char* field_name : primary_names) {
        dataset->primary_axes.push_back(
            db_make_full_primary_axis(
                dataset->fields.data(),
                dataset->fields.size(),
                dataset->row_values.data(),
                dataset->row_count,
                field_name));
    }
    dataset->row_metas = db_build_row_metas(
        dataset->fields.data(),
        dataset->fields.size(),
        dataset->row_values.data(),
        dataset->row_count);
    dataset->aabbs = db_build_row_aabbs(
        dataset->fields.data(),
        dataset->fields.size(),
        dataset->row_values.data(),
        dataset->row_count,
        dataset->primary_axes);
    dataset->accel = build_custom_accel(get_optix_context(), dataset->aabbs);
    return dataset.release();
}

static OptixDbDatasetImpl* create_db_dataset_optix_columnar(
        const RtdlPayloadField* fields,
        size_t field_count,
        size_t row_count,
        const char* const* primary_fields,
        size_t primary_field_count)
{
    db_validate_columnar_inputs(fields, field_count, row_count);
    std::unique_ptr<OptixDbDatasetImpl> dataset(new OptixDbDatasetImpl());
    db_copy_dataset_columnar_payload(*dataset, fields, field_count, row_count);

    std::vector<const char*> primary_names;
    if (primary_field_count > 0) {
        if (!primary_fields) {
            throw std::runtime_error("primary_fields pointer must not be null when primary_field_count > 0");
        }
        primary_names.reserve(std::min<size_t>(primary_field_count, 3));
        for (size_t index = 0; index < primary_field_count && index < 3; ++index) {
            primary_names.push_back(primary_fields[index]);
        }
    } else {
        primary_names = db_default_primary_fields(dataset->fields.data(), dataset->fields.size());
    }
    if (primary_names.empty()) {
        throw std::runtime_error("OptiX prepared DB dataset requires at least one numeric primary RT axis");
    }

    dataset->primary_axes.reserve(primary_names.size());
    for (const char* field_name : primary_names) {
        dataset->primary_axes.push_back(
            db_make_full_primary_axis(
                dataset->fields.data(),
                dataset->fields.size(),
                dataset->row_values.data(),
                dataset->row_count,
                field_name));
    }
    dataset->row_metas = db_build_row_metas(
        dataset->fields.data(),
        dataset->fields.size(),
        dataset->row_values.data(),
        dataset->row_count);
    dataset->aabbs = db_build_row_aabbs(
        dataset->fields.data(),
        dataset->fields.size(),
        dataset->row_values.data(),
        dataset->row_count,
        dataset->primary_axes);
    dataset->accel = build_custom_accel(get_optix_context(), dataset->aabbs);
    return dataset.release();
}

static void run_db_conjunctive_scan_optix_prepared(
        OptixDbDatasetImpl* dataset,
        const RtdlDbClause* clauses,
        size_t clause_count,
        RtdlDbRowIdRow** rows_out,
        size_t* row_count_out)
{
    if (!dataset) {
        throw std::runtime_error("OptiX prepared DB dataset must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    const std::vector<size_t> candidate_row_indices =
        db_collect_candidate_row_indices_optix_prepared(*dataset, clauses, clause_count);
    auto t_start_output = std::chrono::steady_clock::now();
    std::vector<RtdlDbRowIdRow> rows;
    rows.reserve(candidate_row_indices.size());
    for (size_t row_index : candidate_row_indices) {
        rows.push_back({dataset->row_metas[row_index].row_id});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbRowIdRow& left, const RtdlDbRowIdRow& right) {
        return left.row_id < right.row_id;
    });
    auto* out = static_cast<RtdlDbRowIdRow*>(std::malloc(sizeof(RtdlDbRowIdRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlDbRowIdRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
    auto t_end_output = std::chrono::steady_clock::now();
    g_optix_last_db_output_pack_s = std::chrono::duration<double>(t_end_output - t_start_output).count();
    g_optix_last_db_emitted_count = rows.size();
}

static void run_db_conjunctive_scan_count_optix_prepared(
        OptixDbDatasetImpl* dataset,
        const RtdlDbClause* clauses,
        size_t clause_count,
        size_t* row_count_out)
{
    if (!dataset) {
        throw std::runtime_error("OptiX prepared DB dataset must not be null");
    }
    if (!row_count_out) {
        throw std::runtime_error("row_count_out pointer must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    *row_count_out = 0;

    const std::vector<size_t> candidate_row_indices =
        db_collect_candidate_row_indices_optix_prepared(*dataset, clauses, clause_count);
    auto t_start_output = std::chrono::steady_clock::now();
    *row_count_out = candidate_row_indices.size();
    auto t_end_output = std::chrono::steady_clock::now();
    g_optix_last_db_output_pack_s = std::chrono::duration<double>(t_end_output - t_start_output).count();
    g_optix_last_db_emitted_count = candidate_row_indices.size();
}

static void run_db_grouped_count_optix_prepared(
        OptixDbDatasetImpl* dataset,
        const RtdlDbClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        RtdlDbGroupedCountRow** rows_out,
        size_t* row_count_out)
{
    if (!dataset) {
        throw std::runtime_error("OptiX prepared DB dataset must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    if (!group_key_field) {
        throw std::runtime_error("group_key_field must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    const size_t group_field_index =
        db_find_field_index_or_throw(dataset->fields.data(), dataset->fields.size(), group_key_field);
    const std::vector<size_t> candidate_row_indices =
        db_collect_candidate_row_indices_optix_prepared(*dataset, clauses, clause_count);
    auto t_start_output = std::chrono::steady_clock::now();
    std::unordered_map<int64_t, int64_t> counts;
    for (size_t row_index : candidate_row_indices) {
        const RtdlDbScalar& group_value =
            db_row_value(dataset->row_values.data(), row_index, dataset->fields.size(), group_field_index);
        counts[group_value.int_value] += 1;
        if (counts.size() > kDbMaxGroupsPerJob) {
            throw std::runtime_error("first-wave OptiX DB grouped kernels exceeded the 65536-group ceiling");
        }
    }
    std::vector<RtdlDbGroupedCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& entry : counts) {
        rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbGroupedCountRow& left, const RtdlDbGroupedCountRow& right) {
        return left.group_key < right.group_key;
    });
    auto* out = static_cast<RtdlDbGroupedCountRow*>(std::malloc(sizeof(RtdlDbGroupedCountRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlDbGroupedCountRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
    auto t_end_output = std::chrono::steady_clock::now();
    g_optix_last_db_output_pack_s = std::chrono::duration<double>(t_end_output - t_start_output).count();
    g_optix_last_db_emitted_count = rows.size();
}

static void run_db_grouped_sum_optix_prepared(
        OptixDbDatasetImpl* dataset,
        const RtdlDbClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlDbGroupedSumRow** rows_out,
        size_t* row_count_out)
{
    if (!dataset) {
        throw std::runtime_error("OptiX prepared DB dataset must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    if (!group_key_field || !value_field) {
        throw std::runtime_error("group_key_field and value_field must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    const size_t group_field_index =
        db_find_field_index_or_throw(dataset->fields.data(), dataset->fields.size(), group_key_field);
    const size_t value_field_index =
        db_find_field_index_or_throw(dataset->fields.data(), dataset->fields.size(), value_field);
    if (dataset->fields[value_field_index].kind != kDbKindInt64
            && dataset->fields[value_field_index].kind != kDbKindBool) {
        throw std::runtime_error("first-wave OptiX grouped_sum supports integer-compatible value fields only");
    }
    const std::vector<size_t> candidate_row_indices =
        db_collect_candidate_row_indices_optix_prepared(*dataset, clauses, clause_count);
    auto t_start_output = std::chrono::steady_clock::now();
    std::unordered_map<int64_t, int64_t> sums;
    for (size_t row_index : candidate_row_indices) {
        const RtdlDbScalar& group_value =
            db_row_value(dataset->row_values.data(), row_index, dataset->fields.size(), group_field_index);
        const RtdlDbScalar& sum_value =
            db_row_value(dataset->row_values.data(), row_index, dataset->fields.size(), value_field_index);
        sums[group_value.int_value] += sum_value.int_value;
        if (sums.size() > kDbMaxGroupsPerJob) {
            throw std::runtime_error("first-wave OptiX DB grouped kernels exceeded the 65536-group ceiling");
        }
    }
    std::vector<RtdlDbGroupedSumRow> rows;
    rows.reserve(sums.size());
    for (const auto& entry : sums) {
        rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbGroupedSumRow& left, const RtdlDbGroupedSumRow& right) {
        return left.group_key < right.group_key;
    });
    auto* out = static_cast<RtdlDbGroupedSumRow*>(std::malloc(sizeof(RtdlDbGroupedSumRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlDbGroupedSumRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
    auto t_end_output = std::chrono::steady_clock::now();
    g_optix_last_db_output_pack_s = std::chrono::duration<double>(t_end_output - t_start_output).count();
    g_optix_last_db_emitted_count = rows.size();
}

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

static void run_seg_poly_anyhit_rows_optix_native_bounded(
        const RtdlSegment* segments, size_t segment_count,
        const RtdlPolygonRef* polygons, size_t polygon_count,
        const double* vertices_xy, size_t vertex_xy_count,
        RtdlSegmentPolygonAnyHitRow* rows_out, size_t output_capacity,
        size_t* emitted_count_out, uint32_t* overflowed_out)
{
    if (!emitted_count_out || !overflowed_out) {
        throw std::runtime_error("emitted_count_out and overflowed_out must not be null");
    }
    *emitted_count_out = 0;
    *overflowed_out = 0;
    if (segment_count == 0 || polygon_count == 0) {
        return;
    }
    if (segment_count > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("segment count exceeds uint32 launch limit");
    }
    if (polygon_count > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("polygon count exceeds uint32 primitive limit");
    }
    if (output_capacity > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("segment_polygon_anyhit_rows output_capacity exceeds uint32 limit");
    }

    std::call_once(g_segpoly_rows.init, [&]() {
        std::string ptx = compile_to_ptx(kSegPolyAnyhitRowsKernelSrc, "segpoly_rows_kernel.cu");
        g_segpoly_rows.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__segpoly_rows_probe",
            "__miss__segpoly_rows_miss",
            "__intersection__segpoly_rows_isect",
            "__anyhit__segpoly_rows_anyhit",
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

    DevPtr d_output(sizeof(RtdlSegmentPolygonAnyHitRow) * output_capacity);
    DevPtr d_count(sizeof(uint32_t));
    DevPtr d_overflowed(sizeof(uint32_t));
    uint32_t zero = 0;
    upload<uint32_t>(d_count.ptr, &zero, 1);
    upload<uint32_t>(d_overflowed.ptr, &zero, 1);

    struct SegPolyRowsLaunchParams {
        OptixTraversableHandle traversable;
        const GpuSegment* segments;
        const GpuPolygonRef* polygons;
        const float* vertices_x;
        const float* vertices_y;
        RtdlSegmentPolygonAnyHitRow* output;
        uint32_t* output_count;
        uint32_t* overflowed;
        uint32_t output_capacity;
        uint32_t segment_count;
    };

    SegPolyRowsLaunchParams lp;
    lp.traversable = accel.handle;
    lp.segments = reinterpret_cast<const GpuSegment*>(d_segments.ptr);
    lp.polygons = reinterpret_cast<const GpuPolygonRef*>(d_polygons.ptr);
    lp.vertices_x = reinterpret_cast<const float*>(d_vx.ptr);
    lp.vertices_y = reinterpret_cast<const float*>(d_vy.ptr);
    lp.output = output_capacity == 0
        ? nullptr
        : reinterpret_cast<RtdlSegmentPolygonAnyHitRow*>(d_output.ptr);
    lp.output_count = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.overflowed = reinterpret_cast<uint32_t*>(d_overflowed.ptr);
    lp.output_capacity = static_cast<uint32_t>(output_capacity);
    lp.segment_count = static_cast<uint32_t>(segment_count);

    DevPtr d_params(sizeof(SegPolyRowsLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_segpoly_rows.pipe->pipeline, stream,
                             d_params.ptr, sizeof(SegPolyRowsLaunchParams),
                             &g_segpoly_rows.pipe->sbt,
                             static_cast<unsigned>(segment_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    uint32_t emitted = 0;
    uint32_t overflowed = 0;
    download(&emitted, d_count.ptr, 1);
    download(&overflowed, d_overflowed.ptr, 1);
    const size_t rows_to_copy = std::min<size_t>(emitted, output_capacity);
    if (rows_to_copy != 0) {
        download(rows_out, d_output.ptr, rows_to_copy);
    }
    *emitted_count_out = static_cast<size_t>(emitted);
    *overflowed_out = overflowed != 0 || emitted > output_capacity ? 1u : 0u;
}

struct PreparedSegmentPolygonAnyhitRows2D {
    std::vector<GpuPolygonRef> polygons;
    std::vector<float> vertices_x;
    std::vector<float> vertices_y;
    DevPtr d_polygons;
    DevPtr d_vertices_x;
    DevPtr d_vertices_y;
    AccelHolder accel;

    PreparedSegmentPolygonAnyhitRows2D(
            const RtdlPolygonRef* source_polygons,
            size_t polygon_count,
            const double* vertices_xy,
            size_t vertex_xy_count)
        : polygons(polygon_count),
          vertices_x(vertex_xy_count / 2),
          vertices_y(vertex_xy_count / 2),
          d_polygons(sizeof(GpuPolygonRef) * polygon_count),
          d_vertices_x(sizeof(float) * (vertex_xy_count / 2)),
          d_vertices_y(sizeof(float) * (vertex_xy_count / 2))
    {
        if (vertex_xy_count % 2 != 0) {
            throw std::runtime_error("segment/polygon prepared row vertex buffer must contain x/y pairs");
        }
        if (!source_polygons && polygon_count != 0) {
            throw std::runtime_error("polygon pointer must not be null when polygon_count is nonzero");
        }
        if (!vertices_xy && vertex_xy_count != 0) {
            throw std::runtime_error("vertices_xy pointer must not be null when vertex_xy_count is nonzero");
        }
        for (size_t i = 0; i < polygon_count; ++i) {
            polygons[i] = {
                source_polygons[i].id,
                source_polygons[i].vertex_offset,
                source_polygons[i].vertex_count,
            };
        }
        for (size_t i = 0; i < vertices_x.size(); ++i) {
            vertices_x[i] = static_cast<float>(vertices_xy[i * 2]);
            vertices_y[i] = static_cast<float>(vertices_xy[i * 2 + 1]);
        }
        upload(d_polygons.ptr, polygons.data(), polygons.size());
        upload(d_vertices_x.ptr, vertices_x.data(), vertices_x.size());
        upload(d_vertices_y.ptr, vertices_y.data(), vertices_y.size());

        if (!polygons.empty()) {
            std::vector<OptixAabb> aabbs(polygons.size());
            for (size_t i = 0; i < polygons.size(); ++i) {
                aabbs[i] = aabb_for_polygon(vertices_xy, source_polygons[i].vertex_offset, source_polygons[i].vertex_count);
            }
            accel = build_custom_accel(get_optix_context(), aabbs);
        }
    }
};

static PreparedSegmentPolygonAnyhitRows2D* prepare_segment_polygon_anyhit_rows_2d_optix(
        const RtdlPolygonRef* polygons,
        size_t polygon_count,
        const double* vertices_xy,
        size_t vertex_xy_count)
{
    std::call_once(g_segpoly_rows.init, [&]() {
        std::string ptx = compile_to_ptx(kSegPolyAnyhitRowsKernelSrc, "segpoly_rows_kernel.cu");
        g_segpoly_rows.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__segpoly_rows_probe",
            "__miss__segpoly_rows_miss",
            "__intersection__segpoly_rows_isect",
            "__anyhit__segpoly_rows_anyhit",
            nullptr,
            4).release();
    });
    return new PreparedSegmentPolygonAnyhitRows2D(polygons, polygon_count, vertices_xy, vertex_xy_count);
}

static void run_prepared_segment_polygon_anyhit_rows_2d_optix(
        PreparedSegmentPolygonAnyhitRows2D* prepared,
        const RtdlSegment* segments,
        size_t segment_count,
        RtdlSegmentPolygonAnyHitRow* rows_out,
        size_t output_capacity,
        size_t* emitted_count_out,
        uint32_t* overflowed_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX segment/polygon pair-row handle must not be null");
    if (!emitted_count_out || !overflowed_out)
        throw std::runtime_error("emitted_count_out and overflowed_out must not be null");
    if (!rows_out && output_capacity != 0)
        throw std::runtime_error("rows_out must not be null when output_capacity is nonzero");
    if (!segments && segment_count != 0)
        throw std::runtime_error("segments pointer must not be null when segment_count is nonzero");
    if (segment_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("segment count exceeds uint32 launch limit");
    if (output_capacity > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("segment_polygon_anyhit_rows output_capacity exceeds uint32 limit");

    *emitted_count_out = 0;
    *overflowed_out = 0;
    if (segment_count == 0 || prepared->polygons.empty()) {
        return;
    }

    std::vector<GpuSegment> gpu_segments(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
        gpu_segments[i] = {
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].x1),
            static_cast<float>(segments[i].y1),
            segments[i].id,
        };
    }

    DevPtr d_segments(sizeof(GpuSegment) * segment_count);
    DevPtr d_output(sizeof(RtdlSegmentPolygonAnyHitRow) * output_capacity);
    DevPtr d_count(sizeof(uint32_t));
    DevPtr d_overflowed(sizeof(uint32_t));
    uint32_t zero = 0;
    upload(d_segments.ptr, gpu_segments.data(), segment_count);
    upload<uint32_t>(d_count.ptr, &zero, 1);
    upload<uint32_t>(d_overflowed.ptr, &zero, 1);

    struct SegPolyRowsLaunchParams {
        OptixTraversableHandle traversable;
        const GpuSegment* segments;
        const GpuPolygonRef* polygons;
        const float* vertices_x;
        const float* vertices_y;
        RtdlSegmentPolygonAnyHitRow* output;
        uint32_t* output_count;
        uint32_t* overflowed;
        uint32_t output_capacity;
        uint32_t segment_count;
    };

    SegPolyRowsLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.segments = reinterpret_cast<const GpuSegment*>(d_segments.ptr);
    lp.polygons = reinterpret_cast<const GpuPolygonRef*>(prepared->d_polygons.ptr);
    lp.vertices_x = reinterpret_cast<const float*>(prepared->d_vertices_x.ptr);
    lp.vertices_y = reinterpret_cast<const float*>(prepared->d_vertices_y.ptr);
    lp.output = output_capacity == 0
        ? nullptr
        : reinterpret_cast<RtdlSegmentPolygonAnyHitRow*>(d_output.ptr);
    lp.output_count = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.overflowed = reinterpret_cast<uint32_t*>(d_overflowed.ptr);
    lp.output_capacity = static_cast<uint32_t>(output_capacity);
    lp.segment_count = static_cast<uint32_t>(segment_count);

    DevPtr d_params(sizeof(SegPolyRowsLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_segpoly_rows.pipe->pipeline, stream,
                             d_params.ptr, sizeof(SegPolyRowsLaunchParams),
                             &g_segpoly_rows.pipe->sbt,
                             static_cast<unsigned>(segment_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    uint32_t emitted = 0;
    uint32_t overflowed = 0;
    download(&emitted, d_count.ptr, 1);
    download(&overflowed, d_overflowed.ptr, 1);
    const size_t rows_to_copy = std::min<size_t>(emitted, output_capacity);
    if (rows_to_copy != 0) {
        download(rows_out, d_output.ptr, rows_to_copy);
    }
    *emitted_count_out = static_cast<size_t>(emitted);
    *overflowed_out = overflowed != 0 || emitted > output_capacity ? 1u : 0u;
}

static void run_bfs_expand_optix_host_indexed(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t edge_index_count,
        const RtdlFrontierVertex* frontier, size_t frontier_count,
        const uint32_t* visited_vertices, size_t visited_count,
        uint32_t dedupe,
        RtdlBfsExpandRow** rows_out, size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (!row_offsets || row_offset_count == 0) {
        throw std::runtime_error("graph row_offsets must not be empty");
    }
    const uint64_t vertex_count = static_cast<uint64_t>(row_offset_count - 1);
    if (vertex_count > static_cast<uint64_t>(UINT32_MAX) + 1ULL) {
        throw std::runtime_error("graph vertex count exceeds uint32 limit");
    }
    if (frontier_count == 0) {
        return;
    }
    if (!column_indices && edge_index_count != 0) {
        throw std::runtime_error("graph column_indices pointer must not be null when edge count is non-zero");
    }

    for (size_t vertex = 0; vertex + 1 < row_offset_count; ++vertex) {
        const uint32_t start = row_offsets[vertex];
        const uint32_t end = row_offsets[vertex + 1];
        if (start > end) {
            throw std::runtime_error("graph row_offsets must be non-decreasing");
        }
        if (end > edge_index_count) {
            throw std::runtime_error("graph row_offsets exceed column_indices length");
        }
    }
    for (size_t edge_index = 0; edge_index < edge_index_count; ++edge_index) {
        if (column_indices[edge_index] >= vertex_count) {
            throw std::runtime_error("graph column_indices must reference valid graph vertices");
        }
    }

    std::vector<uint8_t> visited_flags(static_cast<size_t>(vertex_count), 0);
    for (size_t i = 0; i < visited_count; ++i) {
        if (visited_vertices[i] >= vertex_count) {
            throw std::runtime_error("visited vertex_id must be a valid graph vertex");
        }
        visited_flags[visited_vertices[i]] = 1;
    }

    std::vector<uint8_t> discovered_flags(static_cast<size_t>(vertex_count), 0);
    std::vector<RtdlBfsExpandRow> rows;
    rows.reserve(edge_index_count);

    for (size_t i = 0; i < frontier_count; ++i) {
        const uint32_t src = frontier[i].vertex_id;
        if (src >= vertex_count) {
            throw std::runtime_error("frontier vertex_id must be a valid graph vertex");
        }
        const uint32_t start = row_offsets[src];
        const uint32_t end = row_offsets[src + 1];
        for (uint32_t edge_index = start; edge_index < end; ++edge_index) {
            const uint32_t dst = column_indices[edge_index];
            if (visited_flags[dst]) {
                continue;
            }
            if (dedupe && discovered_flags[dst]) {
                continue;
            }
            if (dedupe) {
                discovered_flags[dst] = 1;
            }
            rows.push_back(RtdlBfsExpandRow{src, dst, frontier[i].level + 1U});
        }
    }

    std::sort(rows.begin(), rows.end(), [](const RtdlBfsExpandRow& left, const RtdlBfsExpandRow& right) {
        if (left.level != right.level) {
            return left.level < right.level;
        }
        if (left.dst_vertex != right.dst_vertex) {
            return left.dst_vertex < right.dst_vertex;
        }
        return left.src_vertex < right.src_vertex;
    });

    auto* out = static_cast<RtdlBfsExpandRow*>(std::malloc(sizeof(RtdlBfsExpandRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlBfsExpandRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void validate_graph_csr_or_throw(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t edge_index_count)
{
    if (!row_offsets || row_offset_count == 0) {
        throw std::runtime_error("CSR graph row_offsets must not be empty");
    }
    if (edge_index_count > 0 && !column_indices) {
        throw std::runtime_error("CSR graph column_indices pointer must not be null");
    }
    if (row_offsets[0] != 0u) {
        throw std::runtime_error("CSR graph row_offsets must start at 0");
    }
    if (row_offsets[row_offset_count - 1] != edge_index_count) {
        throw std::runtime_error("CSR graph final row_offset must equal edge_count");
    }
    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    for (size_t index = 1; index < row_offset_count; ++index) {
        if (row_offsets[index] < row_offsets[index - 1]) {
            throw std::runtime_error("CSR graph row_offsets must be non-decreasing");
        }
    }
    for (size_t index = 0; index < edge_index_count; ++index) {
        if (column_indices[index] >= vertex_count) {
            throw std::runtime_error("CSR graph column_indices must be valid vertex IDs");
        }
    }
}

static std::vector<GpuGraphEdge> build_graph_edges(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t edge_index_count)
{
    std::vector<GpuGraphEdge> edges;
    edges.reserve(edge_index_count);
    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    for (uint32_t src = 0; src < vertex_count; ++src) {
        for (uint32_t offset = row_offsets[src]; offset < row_offsets[src + 1]; ++offset) {
            edges.push_back({src, column_indices[offset]});
        }
    }
    return edges;
}

static std::vector<OptixAabb> build_graph_edge_aabbs(const std::vector<GpuGraphEdge>& edges)
{
    std::vector<OptixAabb> aabbs;
    aabbs.reserve(edges.size());
    for (const GpuGraphEdge& edge : edges) {
        const float x = static_cast<float>(edge.src);
        OptixAabb aabb;
        aabb.minX = x - kGraphEdgeBoxPad;
        aabb.maxX = x + kGraphEdgeBoxPad;
        aabb.minY = -kGraphEdgeBoxPad;
        aabb.maxY = kGraphEdgeBoxPad;
        aabb.minZ = -kGraphEdgeBoxPad;
        aabb.maxZ = kGraphEdgeBoxPad;
        aabbs.push_back(aabb);
    }
    return aabbs;
}

struct GraphBfsLaunchParams {
    OptixTraversableHandle traversable;
    const GpuGraphEdge* edges;
    const RtdlFrontierVertex* frontier;
    const uint32_t* visited_flags;
    uint32_t* discovered_flags;
    RtdlBfsExpandRow* output;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t frontier_count;
    uint32_t vertex_count;
    uint32_t dedupe;
};

struct GraphTriangleLaunchParams {
    OptixTraversableHandle traversable;
    const GpuGraphEdge* edges;
    const RtdlEdgeSeed* seeds;
    GpuGraphTriangleCandidate* output;
    uint32_t* output_count;
    uint32_t output_capacity;
    uint32_t seed_count;
    uint32_t vertex_count;
};

static void run_bfs_expand_optix_graph_ray(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t edge_index_count,
        const RtdlFrontierVertex* frontier, size_t frontier_count,
        const uint32_t* visited_vertices, size_t visited_count,
        uint32_t dedupe,
        RtdlBfsExpandRow** rows_out, size_t* row_count_out)
{
    validate_graph_csr_or_throw(row_offsets, row_offset_count, column_indices, edge_index_count);
    if (frontier_count > 0 && !frontier) {
        throw std::runtime_error("frontier pointer must not be null when frontier_count > 0");
    }
    if (visited_count > 0 && !visited_vertices) {
        throw std::runtime_error("visited pointer must not be null when visited_count > 0");
    }
    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    if (frontier_count > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("frontier count exceeds uint32 launch limit");
    }
    std::vector<uint32_t> visited_flags(vertex_count, 0u);
    for (size_t i = 0; i < visited_count; ++i) {
        if (visited_vertices[i] >= vertex_count) {
            throw std::runtime_error("visited vertex_id must be a valid graph vertex");
        }
        visited_flags[visited_vertices[i]] = 1u;
    }
    size_t output_capacity = 0;
    for (size_t i = 0; i < frontier_count; ++i) {
        if (frontier[i].vertex_id >= vertex_count) {
            throw std::runtime_error("frontier vertex_id must be a valid graph vertex");
        }
        output_capacity += row_offsets[frontier[i].vertex_id + 1] - row_offsets[frontier[i].vertex_id];
    }
    if (output_capacity > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("graph BFS output capacity exceeds uint32 limit");
    }
    if (frontier_count == 0 || output_capacity == 0) {
        return;
    }

    std::call_once(g_graph_bfs.init, [&]() {
        std::string ptx = compile_to_ptx(kGraphBfsRayKernelSrc, "graph_bfs_ray_kernel.cu");
        g_graph_bfs.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__graph_bfs_probe",
            "__miss__graph_bfs_miss",
            "__intersection__graph_bfs_isect",
            "__anyhit__graph_bfs_anyhit",
            nullptr,
            1).release();
    });

    const std::vector<GpuGraphEdge> edges = build_graph_edges(row_offsets, row_offset_count, column_indices, edge_index_count);
    const std::vector<OptixAabb> aabbs = build_graph_edge_aabbs(edges);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);
    DevPtr d_edges(sizeof(GpuGraphEdge) * edges.size());
    DevPtr d_frontier(sizeof(RtdlFrontierVertex) * frontier_count);
    DevPtr d_visited(sizeof(uint32_t) * visited_flags.size());
    DevPtr d_discovered(sizeof(uint32_t) * visited_flags.size());
    DevPtr d_output(sizeof(RtdlBfsExpandRow) * output_capacity);
    DevPtr d_count(sizeof(uint32_t));
    upload(d_edges.ptr, edges.data(), edges.size());
    upload(d_frontier.ptr, frontier, frontier_count);
    upload(d_visited.ptr, visited_flags.data(), visited_flags.size());
    CU_CHECK(cuMemsetD32(d_discovered.ptr, 0u, visited_flags.size()));
    CU_CHECK(cuMemsetD32(d_count.ptr, 0u, 1));

    GraphBfsLaunchParams lp;
    lp.traversable = accel.handle;
    lp.edges = reinterpret_cast<const GpuGraphEdge*>(d_edges.ptr);
    lp.frontier = reinterpret_cast<const RtdlFrontierVertex*>(d_frontier.ptr);
    lp.visited_flags = reinterpret_cast<const uint32_t*>(d_visited.ptr);
    lp.discovered_flags = reinterpret_cast<uint32_t*>(d_discovered.ptr);
    lp.output = reinterpret_cast<RtdlBfsExpandRow*>(d_output.ptr);
    lp.output_count = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.output_capacity = static_cast<uint32_t>(output_capacity);
    lp.frontier_count = static_cast<uint32_t>(frontier_count);
    lp.vertex_count = vertex_count;
    lp.dedupe = dedupe;
    DevPtr d_params(sizeof(GraphBfsLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_graph_bfs.pipe->pipeline, stream,
                             d_params.ptr, sizeof(GraphBfsLaunchParams),
                             &g_graph_bfs.pipe->sbt,
                             static_cast<unsigned>(frontier_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    uint32_t emitted = 0;
    download(&emitted, d_count.ptr, 1);
    const size_t rows_to_copy = std::min<size_t>(emitted, output_capacity);
    std::vector<RtdlBfsExpandRow> rows(rows_to_copy);
    if (rows_to_copy != 0) {
        download(rows.data(), d_output.ptr, rows_to_copy);
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlBfsExpandRow& left, const RtdlBfsExpandRow& right) {
        if (left.level != right.level) return left.level < right.level;
        if (left.dst_vertex != right.dst_vertex) return left.dst_vertex < right.dst_vertex;
        return left.src_vertex < right.src_vertex;
    });
    auto* out = static_cast<RtdlBfsExpandRow*>(std::malloc(sizeof(RtdlBfsExpandRow) * rows.size()));
    if (!out && !rows.empty()) throw std::bad_alloc();
    if (!rows.empty()) std::memcpy(out, rows.data(), sizeof(RtdlBfsExpandRow) * rows.size());
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_triangle_cycle_candidates_optix_host_indexed(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t edge_index_count,
        const RtdlEdgeSeed* seeds, size_t seed_count,
        uint32_t enforce_id_ascending,
        uint32_t unique,
        RtdlTriangleRow** rows_out, size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (!row_offsets || row_offset_count == 0) {
        throw std::runtime_error("CSR graph row_offsets must not be empty");
    }
    if (edge_index_count > 0 && !column_indices) {
        throw std::runtime_error("CSR graph column_indices pointer must not be null");
    }
    if (seed_count > 0 && !seeds) {
        throw std::runtime_error("edge seed pointer must not be null when seed_count > 0");
    }
    if (row_offsets[0] != 0u) {
        throw std::runtime_error("CSR graph row_offsets must start at 0");
    }
    if (row_offsets[row_offset_count - 1] != edge_index_count) {
        throw std::runtime_error("CSR graph final row_offset must equal edge_count");
    }

    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    for (size_t index = 1; index < row_offset_count; ++index) {
        if (row_offsets[index] < row_offsets[index - 1]) {
            throw std::runtime_error("CSR graph row_offsets must be non-decreasing");
        }
    }
    for (size_t index = 0; index < edge_index_count; ++index) {
        if (column_indices[index] >= vertex_count) {
            throw std::runtime_error("CSR graph column_indices must be valid vertex IDs");
        }
    }

    std::vector<uint32_t> neighbor_marks(vertex_count, 0u);
    uint32_t stamp = 1u;
    std::vector<RtdlTriangleRow> rows;

    for (size_t seed_index = 0; seed_index < seed_count; ++seed_index) {
        const uint32_t u = seeds[seed_index].u;
        const uint32_t v = seeds[seed_index].v;
        if (u >= vertex_count || v >= vertex_count) {
            throw std::runtime_error("edge seed vertices must be valid graph vertex IDs");
        }
        if (u == v) {
            continue;
        }
        if (enforce_id_ascending != 0u && !(u < v)) {
            continue;
        }

        const size_t u_start = row_offsets[u];
        const size_t u_end = row_offsets[u + 1];
        const size_t v_start = row_offsets[v];
        const size_t v_end = row_offsets[v + 1];

        for (size_t offset = u_start; offset < u_end; ++offset) {
            neighbor_marks[column_indices[offset]] = stamp;
        }

        std::vector<uint32_t> common_neighbors;
        for (size_t offset = v_start; offset < v_end; ++offset) {
            const uint32_t w = column_indices[offset];
            if (neighbor_marks[w] != stamp) {
                continue;
            }
            if (enforce_id_ascending != 0u && !(v < w)) {
                continue;
            }
            common_neighbors.push_back(w);
        }
        std::sort(common_neighbors.begin(), common_neighbors.end());

        for (uint32_t w : common_neighbors) {
            if (unique != 0u) {
                const bool already_seen = std::any_of(
                    rows.begin(),
                    rows.end(),
                    [&](const RtdlTriangleRow& row) { return row.u == u && row.v == v && row.w == w; });
                if (already_seen) {
                    continue;
                }
            }
            rows.push_back({u, v, w});
        }

        stamp += 1u;
        if (stamp == 0u) {
            std::fill(neighbor_marks.begin(), neighbor_marks.end(), 0u);
            stamp = 1u;
        }
    }

    auto* out = static_cast<RtdlTriangleRow*>(std::malloc(sizeof(RtdlTriangleRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlTriangleRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_triangle_cycle_candidates_optix_graph_ray(
        const uint32_t* row_offsets, size_t row_offset_count,
        const uint32_t* column_indices, size_t edge_index_count,
        const RtdlEdgeSeed* seeds, size_t seed_count,
        uint32_t enforce_id_ascending,
        uint32_t unique,
        RtdlTriangleRow** rows_out, size_t* row_count_out)
{
    validate_graph_csr_or_throw(row_offsets, row_offset_count, column_indices, edge_index_count);
    if (seed_count > 0 && !seeds) {
        throw std::runtime_error("edge seed pointer must not be null when seed_count > 0");
    }
    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    if (seed_count > static_cast<size_t>(UINT32_MAX / 2u)) {
        throw std::runtime_error("seed count exceeds graph triangle launch limit");
    }
    size_t output_capacity = 0;
    for (size_t seed_index = 0; seed_index < seed_count; ++seed_index) {
        const uint32_t u = seeds[seed_index].u;
        const uint32_t v = seeds[seed_index].v;
        if (u >= vertex_count || v >= vertex_count) {
            throw std::runtime_error("edge seed vertices must be valid graph vertex IDs");
        }
        if (u == v || (enforce_id_ascending != 0u && !(u < v))) {
            continue;
        }
        output_capacity += row_offsets[u + 1] - row_offsets[u];
        output_capacity += row_offsets[v + 1] - row_offsets[v];
    }
    if (output_capacity > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("graph triangle candidate capacity exceeds uint32 limit");
    }
    if (seed_count == 0 || output_capacity == 0) {
        return;
    }

    std::call_once(g_graph_triangle.init, [&]() {
        std::string ptx = compile_to_ptx(kGraphTriangleRayKernelSrc, "graph_triangle_ray_kernel.cu");
        g_graph_triangle.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__graph_triangle_cycle_candidates",
            "__miss__graph_triangle_miss",
            "__intersection__graph_triangle_isect",
            "__anyhit__graph_triangle_anyhit",
            nullptr,
            1).release();
    });

    const std::vector<GpuGraphEdge> edges = build_graph_edges(row_offsets, row_offset_count, column_indices, edge_index_count);
    const std::vector<OptixAabb> aabbs = build_graph_edge_aabbs(edges);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);
    DevPtr d_edges(sizeof(GpuGraphEdge) * edges.size());
    DevPtr d_seeds(sizeof(RtdlEdgeSeed) * seed_count);
    DevPtr d_output(sizeof(GpuGraphTriangleCandidate) * output_capacity);
    DevPtr d_count(sizeof(uint32_t));
    upload(d_edges.ptr, edges.data(), edges.size());
    upload(d_seeds.ptr, seeds, seed_count);
    CU_CHECK(cuMemsetD32(d_count.ptr, 0u, 1));

    GraphTriangleLaunchParams lp;
    lp.traversable = accel.handle;
    lp.edges = reinterpret_cast<const GpuGraphEdge*>(d_edges.ptr);
    lp.seeds = reinterpret_cast<const RtdlEdgeSeed*>(d_seeds.ptr);
    lp.output = reinterpret_cast<GpuGraphTriangleCandidate*>(d_output.ptr);
    lp.output_count = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.output_capacity = static_cast<uint32_t>(output_capacity);
    lp.seed_count = static_cast<uint32_t>(seed_count);
    lp.vertex_count = vertex_count;
    DevPtr d_params(sizeof(GraphTriangleLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_graph_triangle.pipe->pipeline, stream,
                             d_params.ptr, sizeof(GraphTriangleLaunchParams),
                             &g_graph_triangle.pipe->sbt,
                             static_cast<unsigned>(seed_count * 2u), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    uint32_t emitted = 0;
    download(&emitted, d_count.ptr, 1);
    const size_t candidates_to_copy = std::min<size_t>(emitted, output_capacity);
    std::vector<GpuGraphTriangleCandidate> candidates(candidates_to_copy);
    if (candidates_to_copy != 0) {
        download(candidates.data(), d_output.ptr, candidates_to_copy);
    }

    std::vector<std::vector<uint32_t>> u_neighbors(seed_count);
    std::vector<std::vector<uint32_t>> v_neighbors(seed_count);
    for (const GpuGraphTriangleCandidate& candidate : candidates) {
        if (candidate.seed_index >= seed_count) {
            continue;
        }
        std::vector<uint32_t>& bucket = candidate.side == 0u
            ? u_neighbors[candidate.seed_index]
            : v_neighbors[candidate.seed_index];
        bucket.push_back(candidate.dst_vertex);
    }

    std::vector<uint32_t> marks(vertex_count, 0u);
    uint32_t stamp = 1u;
    std::vector<RtdlTriangleRow> rows;
    for (size_t seed_index = 0; seed_index < seed_count; ++seed_index) {
        const uint32_t u = seeds[seed_index].u;
        const uint32_t v = seeds[seed_index].v;
        if (u == v || (enforce_id_ascending != 0u && !(u < v))) {
            continue;
        }
        for (uint32_t w : u_neighbors[seed_index]) {
            marks[w] = stamp;
        }
        std::vector<uint32_t> common_neighbors;
        for (uint32_t w : v_neighbors[seed_index]) {
            if (marks[w] != stamp) {
                continue;
            }
            if (enforce_id_ascending != 0u && !(v < w)) {
                continue;
            }
            common_neighbors.push_back(w);
        }
        std::sort(common_neighbors.begin(), common_neighbors.end());
        common_neighbors.erase(std::unique(common_neighbors.begin(), common_neighbors.end()), common_neighbors.end());
        for (uint32_t w : common_neighbors) {
            if (unique != 0u) {
                const bool already_seen = std::any_of(
                    rows.begin(),
                    rows.end(),
                    [&](const RtdlTriangleRow& row) { return row.u == u && row.v == v && row.w == w; });
                if (already_seen) {
                    continue;
                }
            }
            rows.push_back({u, v, w});
        }
        stamp += 1u;
        if (stamp == 0u) {
            std::fill(marks.begin(), marks.end(), 0u);
            stamp = 1u;
        }
    }

    auto* out = static_cast<RtdlTriangleRow*>(std::malloc(sizeof(RtdlTriangleRow) * rows.size()));
    if (!out && !rows.empty()) throw std::bad_alloc();
    if (!rows.empty()) std::memcpy(out, rows.data(), sizeof(RtdlTriangleRow) * rows.size());
    *rows_out = out;
    *row_count_out = rows.size();
}

// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
// Workload implementations
// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// ---------- segment-pair intersection --------------------------------------------------------------

struct SegmentPairIntersectionLaunchParams {
    OptixTraversableHandle traversable;
    const GpuSegment* left_segs;
    const GpuSegment* right_segs;
    GpuSegmentPairIntersectionRecord*     output;
    uint32_t*         output_count;
    uint32_t          output_capacity;
    uint32_t          probe_count;
};

struct PreparedSegmentPairIntersectionBuild {
    std::vector<GpuSegment> right_segments;
    std::vector<RtdlSegment> host_right_segments;
    size_t right_count = 0;
    DevPtr d_right;
    AccelHolder accel;

    PreparedSegmentPairIntersectionBuild(const RtdlSegment* right, size_t count)
        : right_segments(count),
          host_right_segments(),
          right_count(count),
          d_right(sizeof(GpuSegment) * count)
    {
        if (count > 0) {
            host_right_segments.assign(right, right + count);
        }
        for (size_t i = 0; i < count; ++i) {
            right_segments[i] = {
                static_cast<float>(right[i].x0),
                static_cast<float>(right[i].y0),
                static_cast<float>(right[i].x1),
                static_cast<float>(right[i].y1),
                right[i].id,
            };
        }
        upload(d_right.ptr, right_segments.data(), right_segments.size());

        if (!right_segments.empty()) {
            std::vector<OptixAabb> aabbs(right_segments.size());
            for (size_t i = 0; i < right_segments.size(); ++i) {
                aabbs[i] = aabb_for_segment(
                    right_segments[i].x0, right_segments[i].y0,
                    right_segments[i].x1, right_segments[i].y1);
            }
            accel = build_custom_accel(get_optix_context(), aabbs);
        }
    }
};

static void ensure_segment_pair_intersection_pipeline() {
    std::call_once(g_segment_pair_intersection.init, [&]() {
        std::string ptx = compile_to_ptx(kSegmentPairIntersectionKernelSrc, "segment_pair_intersection_kernel.cu");
        g_segment_pair_intersection.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__segment_pair_intersection_probe",
            "__miss__segment_pair_intersection_miss",
            "__intersection__segment_pair_intersection_isect",
            "__anyhit__segment_pair_intersection_anyhit",
            nullptr,   // no closesthit
            4).release();
    });
}

static void finalize_segment_pair_intersection_rows(
        const RtdlSegment* left, size_t left_count,
        const RtdlSegment* right, size_t right_count,
        const std::vector<GpuSegmentPairIntersectionRecord>& gpu_rows,
        RtdlSegmentPairIntersectionRow** rows_out,
        size_t* row_count_out)
{
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

    std::vector<RtdlSegmentPairIntersectionRow> refined;
    refined.reserve(gpu_rows.size());
    std::unordered_set<uint64_t> seen_pairs;
    seen_pairs.reserve(gpu_rows.size() * 2 + 1);

    for (const auto& gpu_row : gpu_rows) {
        const auto left_it = left_by_id.find(gpu_row.left_id);
        const auto right_it = right_by_id.find(gpu_row.right_id);
        if (left_it == left_by_id.end() || right_it == right_by_id.end()) {
            continue;
        }
        const uint64_t pair_key =
            (static_cast<uint64_t>(gpu_row.left_id) << 32) |
            static_cast<uint64_t>(gpu_row.right_id);
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
            RtdlSegmentPairIntersectionRow{
                gpu_row.left_id,
                gpu_row.right_id,
                ix,
                iy,
            });
    }

    auto* out = static_cast<RtdlSegmentPairIntersectionRow*>(
        std::malloc(sizeof(RtdlSegmentPairIntersectionRow) * refined.size()));
    if (!out && !refined.empty()) throw std::bad_alloc();
    for (size_t i = 0; i < refined.size(); ++i) {
        out[i] = refined[i];
    }
    *rows_out = out;
    *row_count_out = refined.size();
}

static void launch_segment_pair_intersection_optix(
        const RtdlSegment* left, size_t left_count,
        const GpuSegment* gpu_left_host,
        CUdeviceptr d_left_ptr,
        const GpuSegment* gpu_right_host,
        CUdeviceptr d_right_ptr,
        size_t right_count,
        OptixTraversableHandle traversable,
        RtdlSegmentPairIntersectionRow** rows_out,
        size_t* row_count_out,
        const RtdlSegment* right_host)
{
    if (left_count == 0 || right_count == 0) {
        *rows_out = nullptr;
        *row_count_out = 0;
        return;
    }
    if (right_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
        throw std::runtime_error("segment-pair intersection right segment count exceeds uint32_t launch capacity");
    }
    const uint64_t max_left_per_launch64 =
        static_cast<uint64_t>(std::numeric_limits<uint32_t>::max()) /
        static_cast<uint64_t>(right_count);
    if (max_left_per_launch64 == 0) {
        throw std::runtime_error("segment-pair intersection cannot chunk right segment set into uint32_t launch capacity");
    }
    const size_t max_left_per_launch = static_cast<size_t>(
        std::min<uint64_t>(max_left_per_launch64, static_cast<uint64_t>(left_count)));
    DevPtr d_count(sizeof(uint32_t));

    auto launch_candidate_pass = [&](
            size_t left_offset,
            size_t chunk_left_count,
            CUdeviceptr output_ptr,
            uint32_t output_capacity) -> uint32_t {
        uint32_t zero = 0;
        upload<uint32_t>(d_count.ptr, &zero, 1);
        const uint64_t chunk_capacity64 =
            static_cast<uint64_t>(chunk_left_count) * static_cast<uint64_t>(right_count);
        if (chunk_capacity64 > static_cast<uint64_t>(std::numeric_limits<uint32_t>::max())) {
            throw std::runtime_error("segment-pair intersection chunk output capacity exceeds uint32_t");
        }
        const uint32_t max_candidate_count = static_cast<uint32_t>(chunk_capacity64);
        const CUdeviceptr chunk_left_ptr =
            d_left_ptr + static_cast<CUdeviceptr>(sizeof(GpuSegment) * left_offset);

        SegmentPairIntersectionLaunchParams lp;
        lp.traversable = traversable;
        lp.left_segs = reinterpret_cast<const GpuSegment*>(chunk_left_ptr);
        lp.right_segs = reinterpret_cast<const GpuSegment*>(d_right_ptr);
        lp.output = output_capacity == 0
            ? nullptr
            : reinterpret_cast<GpuSegmentPairIntersectionRecord*>(output_ptr);
        lp.output_count = reinterpret_cast<uint32_t*>(d_count.ptr);
        lp.output_capacity = output_capacity;
        lp.probe_count = static_cast<uint32_t>(left_count);

        DevPtr d_params(sizeof(SegmentPairIntersectionLaunchParams));
        upload(d_params.ptr, &lp, 1);

        CUstream stream = 0;
        OPTIX_CHECK(optixLaunch(g_segment_pair_intersection.pipe->pipeline, stream,
                                 d_params.ptr, sizeof(SegmentPairIntersectionLaunchParams),
                                 &g_segment_pair_intersection.pipe->sbt,
                                 static_cast<unsigned>(chunk_left_count), 1, 1));
        CU_CHECK(cuStreamSynchronize(stream));

        uint32_t emitted = 0;
        download(&emitted, d_count.ptr, 1);
        if (emitted > max_candidate_count) {
            throw std::runtime_error("segment-pair intersection candidate count exceeded pair limit");
        }
        if (emitted > output_capacity && output_capacity != 0) {
            throw std::runtime_error("segment-pair intersection output overflowed capacity");
        }
        return emitted;
    };

    std::vector<GpuSegmentPairIntersectionRecord> gpu_rows;
    for (size_t left_offset = 0; left_offset < left_count; left_offset += max_left_per_launch) {
        const size_t chunk_left_count = std::min(max_left_per_launch, left_count - left_offset);
        const uint32_t gpu_count = launch_candidate_pass(left_offset, chunk_left_count, 0, 0);
        if (gpu_count == 0) {
            continue;
        }

        DevPtr d_output(sizeof(GpuSegmentPairIntersectionRecord) * gpu_count);
        const uint32_t written_count =
            launch_candidate_pass(left_offset, chunk_left_count, d_output.ptr, gpu_count);
        if (written_count != gpu_count) {
            throw std::runtime_error("segment-pair intersection candidate count changed between count and write passes");
        }

        const size_t old_size = gpu_rows.size();
        gpu_rows.resize(old_size + gpu_count);
        download(gpu_rows.data() + old_size, d_output.ptr, gpu_count);
    }

    if (gpu_rows.empty()) {
        finalize_segment_pair_intersection_rows(
            left, left_count,
            right_host, right_count,
            {},
            rows_out,
            row_count_out);
        return;
    }
    finalize_segment_pair_intersection_rows(
        left, left_count,
        right_host, right_count,
        gpu_rows,
        rows_out,
        row_count_out);
}

static void run_segment_pair_intersection_optix(
        const RtdlSegment* left,  size_t left_count,
        const RtdlSegment* right, size_t right_count,
        RtdlSegmentPairIntersectionRow** rows_out, size_t* row_count_out)
{
    ensure_segment_pair_intersection_pipeline();

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

    launch_segment_pair_intersection_optix(
        left, left_count,
        gpu_left.data(), d_left.ptr,
        gpu_right.data(), d_right.ptr,
        right_count,
        accel.handle,
        rows_out,
        row_count_out,
        right);
}

static PreparedSegmentPairIntersectionBuild* prepare_segment_pair_intersection_optix(
        const RtdlSegment* right, size_t right_count)
{
    ensure_segment_pair_intersection_pipeline();
    return new PreparedSegmentPairIntersectionBuild(right, right_count);
}

static void run_prepared_segment_pair_intersection_optix(
        PreparedSegmentPairIntersectionBuild* prepared,
        const RtdlSegment* left, size_t left_count,
        RtdlSegmentPairIntersectionRow** rows_out, size_t* row_count_out)
{
    if (!prepared) {
        throw std::runtime_error("prepared segment-pair handle must not be null");
    }
    ensure_segment_pair_intersection_pipeline();
    std::vector<GpuSegment> gpu_left(left_count);
    for (size_t i = 0; i < left_count; ++i) {
        gpu_left[i] = {
            static_cast<float>(left[i].x0),
            static_cast<float>(left[i].y0),
            static_cast<float>(left[i].x1),
            static_cast<float>(left[i].y1),
            left[i].id,
        };
    }
    DevPtr d_left(sizeof(GpuSegment) * left_count);
    upload(d_left.ptr, gpu_left.data(), gpu_left.size());

    launch_segment_pair_intersection_optix(
        left, left_count,
        gpu_left.data(), d_left.ptr,
        prepared->right_segments.data(), prepared->d_right.ptr,
        prepared->right_count,
        prepared->accel.handle,
        rows_out,
        row_count_out,
        prepared->host_right_segments.data());
}

static void run_ray_segment_group_count_2d_optix(
        const RtdlRay2D* rays, size_t ray_count,
        const RtdlSegment* segments, size_t segment_count,
        const uint32_t* segment_group_ids,
        RtdlRaySegmentGroupCountRow** rows_out, size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (ray_count == 0 || segment_count == 0) {
        return;
    }
    if (!rays) {
        throw std::runtime_error("rays pointer must not be null when ray_count is nonzero");
    }
    if (!segments) {
        throw std::runtime_error("segments pointer must not be null when segment_count is nonzero");
    }
    if (!segment_group_ids) {
        throw std::runtime_error("segment_group_ids pointer must not be null when segment_count is nonzero");
    }

    std::vector<RtdlSegment> ray_segments(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        const RtdlRay2D& ray = rays[i];
        if (!std::isfinite(ray.ox) || !std::isfinite(ray.oy) ||
            !std::isfinite(ray.dx) || !std::isfinite(ray.dy) ||
            !std::isfinite(ray.tmax)) {
            throw std::runtime_error("ray_segment_group_count requires finite ray coordinates and tmax");
        }
        if (ray.tmax < 0.0) {
            throw std::runtime_error("ray_segment_group_count requires non-negative ray tmax");
        }
        ray_segments[i] = RtdlSegment{
            ray.id,
            ray.ox,
            ray.oy,
            ray.ox + ray.dx * ray.tmax,
            ray.oy + ray.dy * ray.tmax,
        };
    }

    std::unordered_map<uint32_t, uint32_t> group_by_segment_id;
    group_by_segment_id.reserve(segment_count * 2 + 1);
    for (size_t i = 0; i < segment_count; ++i) {
        if (!std::isfinite(segments[i].x0) || !std::isfinite(segments[i].y0) ||
            !std::isfinite(segments[i].x1) || !std::isfinite(segments[i].y1)) {
            throw std::runtime_error("ray_segment_group_count requires finite segment coordinates");
        }
        const auto inserted = group_by_segment_id.emplace(segments[i].id, segment_group_ids[i]);
        if (!inserted.second) {
            throw std::runtime_error("ray_segment_group_count requires unique segment ids");
        }
    }

    RtdlSegmentPairIntersectionRow* pair_rows = nullptr;
    size_t pair_count = 0;
    run_segment_pair_intersection_optix(
        ray_segments.data(),
        ray_segments.size(),
        segments,
        segment_count,
        &pair_rows,
        &pair_count);

    struct PairRowsGuard {
        RtdlSegmentPairIntersectionRow* rows = nullptr;
        ~PairRowsGuard() { std::free(rows); }
    } guard{pair_rows};

    std::unordered_map<uint64_t, uint32_t> counts;
    counts.reserve(pair_count * 2 + 1);
    for (size_t i = 0; i < pair_count; ++i) {
        const uint32_t ray_id = pair_rows[i].left_id;
        const uint32_t segment_id = pair_rows[i].right_id;
        const auto group_it = group_by_segment_id.find(segment_id);
        if (group_it == group_by_segment_id.end()) {
            continue;
        }
        const uint32_t group_id = group_it->second;
        const uint64_t key =
            (static_cast<uint64_t>(ray_id) << 32) |
            static_cast<uint64_t>(group_id);
        uint32_t& count = counts[key];
        if (count == std::numeric_limits<uint32_t>::max()) {
            throw std::runtime_error("ray_segment_group_count hit count overflowed uint32");
        }
        ++count;
    }

    std::vector<RtdlRaySegmentGroupCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& item : counts) {
        const uint32_t ray_id = static_cast<uint32_t>(item.first >> 32);
        const uint32_t group_id = static_cast<uint32_t>(item.first & 0xffffffffu);
        const uint32_t hit_count = item.second;
        rows.push_back(RtdlRaySegmentGroupCountRow{
            ray_id,
            group_id,
            hit_count,
            hit_count & 1u,
        });
    }
    std::sort(rows.begin(), rows.end(), [](const auto& left, const auto& right) {
        if (left.ray_id != right.ray_id) return left.ray_id < right.ray_id;
        return left.group_id < right.group_id;
    });

    auto* out = static_cast<RtdlRaySegmentGroupCountRow*>(
        std::malloc(sizeof(RtdlRaySegmentGroupCountRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    for (size_t i = 0; i < rows.size(); ++i) {
        out[i] = rows[i];
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

struct PreparedRaySegmentGroupCount2D {
    std::unique_ptr<PreparedSegmentPairIntersectionBuild> segment_pairs;
    std::unordered_map<uint32_t, uint32_t> group_by_segment_id;

    PreparedRaySegmentGroupCount2D(
            const RtdlSegment* segments,
            size_t segment_count,
            const uint32_t* segment_group_ids)
        : segment_pairs(nullptr),
          group_by_segment_id()
    {
        if (!segments && segment_count != 0) {
            throw std::runtime_error("segments pointer must not be null when segment_count is nonzero");
        }
        if (!segment_group_ids && segment_count != 0) {
            throw std::runtime_error("segment_group_ids pointer must not be null when segment_count is nonzero");
        }
        group_by_segment_id.reserve(segment_count * 2 + 1);
        for (size_t i = 0; i < segment_count; ++i) {
            if (!std::isfinite(segments[i].x0) || !std::isfinite(segments[i].y0) ||
                !std::isfinite(segments[i].x1) || !std::isfinite(segments[i].y1)) {
                throw std::runtime_error("ray_segment_group_count requires finite segment coordinates");
            }
            const auto inserted = group_by_segment_id.emplace(segments[i].id, segment_group_ids[i]);
            if (!inserted.second) {
                throw std::runtime_error("ray_segment_group_count requires unique segment ids");
            }
        }
        segment_pairs = std::make_unique<PreparedSegmentPairIntersectionBuild>(segments, segment_count);
    }
};

static std::vector<RtdlSegment> ray_segments_from_finite_rays(
        const RtdlRay2D* rays,
        size_t ray_count)
{
    if (!rays && ray_count != 0) {
        throw std::runtime_error("rays pointer must not be null when ray_count is nonzero");
    }
    std::vector<RtdlSegment> ray_segments(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        const RtdlRay2D& ray = rays[i];
        if (!std::isfinite(ray.ox) || !std::isfinite(ray.oy) ||
            !std::isfinite(ray.dx) || !std::isfinite(ray.dy) ||
            !std::isfinite(ray.tmax)) {
            throw std::runtime_error("ray_segment_group_count requires finite ray coordinates and tmax");
        }
        if (ray.tmax < 0.0) {
            throw std::runtime_error("ray_segment_group_count requires non-negative ray tmax");
        }
        ray_segments[i] = RtdlSegment{
            ray.id,
            ray.ox,
            ray.oy,
            ray.ox + ray.dx * ray.tmax,
            ray.oy + ray.dy * ray.tmax,
        };
    }
    return ray_segments;
}

static void finalize_ray_segment_group_count_rows(
        const RtdlSegmentPairIntersectionRow* pair_rows,
        size_t pair_count,
        const std::unordered_map<uint32_t, uint32_t>& group_by_segment_id,
        bool odd_parity_only,
        RtdlRaySegmentGroupCountRow** rows_out,
        size_t* row_count_out)
{
    std::unordered_map<uint64_t, uint32_t> counts;
    counts.reserve(pair_count * 2 + 1);
    for (size_t i = 0; i < pair_count; ++i) {
        const uint32_t ray_id = pair_rows[i].left_id;
        const uint32_t segment_id = pair_rows[i].right_id;
        const auto group_it = group_by_segment_id.find(segment_id);
        if (group_it == group_by_segment_id.end()) {
            continue;
        }
        const uint32_t group_id = group_it->second;
        const uint64_t key =
            (static_cast<uint64_t>(ray_id) << 32) |
            static_cast<uint64_t>(group_id);
        uint32_t& count = counts[key];
        if (count == std::numeric_limits<uint32_t>::max()) {
            throw std::runtime_error("ray_segment_group_count hit count overflowed uint32");
        }
        ++count;
    }

    std::vector<RtdlRaySegmentGroupCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& item : counts) {
        const uint32_t ray_id = static_cast<uint32_t>(item.first >> 32);
        const uint32_t group_id = static_cast<uint32_t>(item.first & 0xffffffffu);
        const uint32_t hit_count = item.second;
        if (odd_parity_only && ((hit_count & 1u) == 0u)) {
            continue;
        }
        rows.push_back(RtdlRaySegmentGroupCountRow{
            ray_id,
            group_id,
            hit_count,
            hit_count & 1u,
        });
    }
    std::sort(rows.begin(), rows.end(), [](const auto& left, const auto& right) {
        if (left.ray_id != right.ray_id) return left.ray_id < right.ray_id;
        return left.group_id < right.group_id;
    });

    auto* out = static_cast<RtdlRaySegmentGroupCountRow*>(
        std::malloc(sizeof(RtdlRaySegmentGroupCountRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    for (size_t i = 0; i < rows.size(); ++i) {
        out[i] = rows[i];
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static PreparedRaySegmentGroupCount2D* prepare_ray_segment_group_count_2d_optix(
        const RtdlSegment* segments,
        size_t segment_count,
        const uint32_t* segment_group_ids)
{
    ensure_segment_pair_intersection_pipeline();
    return new PreparedRaySegmentGroupCount2D(segments, segment_count, segment_group_ids);
}

static void run_prepared_ray_segment_group_count_2d_optix(
        PreparedRaySegmentGroupCount2D* prepared,
        const RtdlRay2D* rays,
        size_t ray_count,
        RtdlRaySegmentGroupCountRow** rows_out,
        size_t* row_count_out)
{
    if (!prepared) {
        throw std::runtime_error("prepared ray_segment_group_count handle must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (ray_count == 0 || prepared->group_by_segment_id.empty()) {
        return;
    }

    std::vector<RtdlSegment> ray_segments = ray_segments_from_finite_rays(rays, ray_count);
    RtdlSegmentPairIntersectionRow* pair_rows = nullptr;
    size_t pair_count = 0;
    run_prepared_segment_pair_intersection_optix(
        prepared->segment_pairs.get(),
        ray_segments.data(),
        ray_segments.size(),
        &pair_rows,
        &pair_count);

    struct PairRowsGuard {
        RtdlSegmentPairIntersectionRow* rows = nullptr;
        ~PairRowsGuard() { std::free(rows); }
    } guard{pair_rows};

    finalize_ray_segment_group_count_rows(
        pair_rows,
        pair_count,
        prepared->group_by_segment_id,
        false,
        rows_out,
        row_count_out);
}

static void run_prepared_ray_segment_group_odd_parity_2d_optix(
        PreparedRaySegmentGroupCount2D* prepared,
        const RtdlRay2D* rays,
        size_t ray_count,
        RtdlRaySegmentGroupCountRow** rows_out,
        size_t* row_count_out)
{
    if (!prepared) {
        throw std::runtime_error("prepared ray_segment_group_count handle must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (ray_count == 0 || prepared->group_by_segment_id.empty()) {
        return;
    }

    std::vector<RtdlSegment> ray_segments = ray_segments_from_finite_rays(rays, ray_count);
    RtdlSegmentPairIntersectionRow* pair_rows = nullptr;
    size_t pair_count = 0;
    run_prepared_segment_pair_intersection_optix(
        prepared->segment_pairs.get(),
        ray_segments.data(),
        ray_segments.size(),
        &pair_rows,
        &pair_count);

    struct PairRowsGuard {
        RtdlSegmentPairIntersectionRow* rows = nullptr;
        ~PairRowsGuard() { std::free(rows); }
    } guard{pair_rows};

    finalize_ray_segment_group_count_rows(
        pair_rows,
        pair_count,
        prepared->group_by_segment_id,
        true,
        rows_out,
        row_count_out);
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
    uint32_t         point_index_offset;
    uint32_t         device_prefilter;
};

static void ensure_pip_pipeline()
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
}

static void run_pip_optix(
        const RtdlPoint* points,     size_t point_count,
        const RtdlPolygonRef* polys, size_t poly_count,
        const double* vertices_xy,   size_t vertex_xy_count,
        uint32_t positive_only,
        RtdlPipRow** rows_out, size_t* row_count_out)
{
    ensure_pip_pipeline();

    const bool profile_pip = std::getenv("RTDL_OPTIX_PIP_PROFILE") != nullptr;
    const auto t_total_start = std::chrono::steady_clock::now();
    auto seconds_between = [](std::chrono::steady_clock::time_point start,
                              std::chrono::steady_clock::time_point end) -> double {
        return std::chrono::duration<double>(end - start).count();
    };

    const auto t_pack_start = std::chrono::steady_clock::now();
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
    const auto t_pack_end = std::chrono::steady_clock::now();

    const auto t_upload_start = std::chrono::steady_clock::now();
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
    const auto t_upload_end = std::chrono::steady_clock::now();

    // BVH over polygons
    const auto t_accel_start = std::chrono::steady_clock::now();
    std::vector<OptixAabb> aabbs(poly_count);
    for (size_t i = 0; i < poly_count; ++i)
        aabbs[i] = aabb_for_polygon(vertices_xy, polys[i].vertex_offset, polys[i].vertex_count);
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);
    const auto t_accel_end = std::chrono::steady_clock::now();

    size_t out_count = point_count * poly_count;
    DevPtr d_count(sizeof(uint32_t));
    uint32_t zero = 0;
    upload<uint32_t>(d_count.ptr, &zero, 1);
    std::unique_ptr<DevPtr> d_output;
    if (positive_only == 0u) {
        d_output = std::make_unique<DevPtr>(sizeof(GpuPipRecord) * out_count);
        std::vector<GpuPipRecord> init_output(out_count);
        for (size_t pi = 0; pi < point_count; ++pi)
            for (size_t qi = 0; qi < poly_count; ++qi) {
                init_output[pi * poly_count + qi] = {pt_ids[pi], gpu_polys[qi].id, 0u};
        }
        upload(d_output->ptr, init_output.data(), out_count);
    }

    PipLaunchParams lp;
    lp.traversable    = accel.handle;
    lp.points_x       = reinterpret_cast<const float*>(d_pts_x.ptr);
    lp.points_y       = reinterpret_cast<const float*>(d_pts_y.ptr);
    lp.point_ids      = reinterpret_cast<const uint32_t*>(d_pt_ids.ptr);
    lp.polygons       = reinterpret_cast<const GpuPolygonRef*>(d_polys.ptr);
    lp.vertices_x     = reinterpret_cast<const float*>(d_vx.ptr);
    lp.vertices_y     = reinterpret_cast<const float*>(d_vy.ptr);
    lp.hit_words      = nullptr;
    lp.output         = d_output ? reinterpret_cast<GpuPipRecord*>(d_output->ptr) : nullptr;
    lp.output_count   = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.output_capacity = d_output ? static_cast<uint32_t>(out_count) : 0u;
    lp.positive_only  = positive_only;
    lp.hit_word_count = 0u;
    lp.polygon_count  = static_cast<uint32_t>(poly_count);
    lp.probe_count    = static_cast<uint32_t>(point_count);
    lp.point_index_offset = 0u;
    lp.device_prefilter =
        (positive_only != 0u && std::getenv("RTDL_OPTIX_PIP_DISABLE_DEVICE_PREFILTER") == nullptr) ? 1u : 0u;

    DevPtr d_params(sizeof(PipLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    double pip_count_pass_s = 0.0;
    double pip_write_pass_s = 0.0;
    double pip_download_s = 0.0;
    double pip_refine_s = 0.0;
    size_t pip_candidate_count = 0;
    size_t pip_chunks = 0;
    size_t pip_fallback_chunks = 0;
    const bool pip_one_pass_compact =
        std::getenv("RTDL_OPTIX_PIP_DISABLE_ONE_PASS_COMPACT") == nullptr;
    if (positive_only == 0u) {
        const auto t_launch_start = std::chrono::steady_clock::now();
        OPTIX_CHECK(optixLaunch(g_pip.pipe->pipeline, stream,
                                 d_params.ptr, sizeof(PipLaunchParams),
                                 &g_pip.pipe->sbt,
                                 static_cast<unsigned>(point_count), 1, 1));
        CU_CHECK(cuStreamSynchronize(stream));
        const auto t_launch_end = std::chrono::steady_clock::now();
        pip_write_pass_s += seconds_between(t_launch_start, t_launch_end);
    }

    if (positive_only != 0u) {
        if (point_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
            throw std::runtime_error("PIP positive-hit point count exceeds uint32_t chunk offset capacity");
        }
        if (poly_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
            throw std::runtime_error("PIP positive-hit polygon count exceeds uint32_t launch capacity");
        }
        const uint64_t max_points_per_launch64 =
            static_cast<uint64_t>(std::numeric_limits<uint32_t>::max()) /
            static_cast<uint64_t>(poly_count);
        if (max_points_per_launch64 == 0) {
            throw std::runtime_error("PIP positive-hit launch cannot chunk polygon set into uint32_t capacity");
        }
        const size_t max_points_per_launch = static_cast<size_t>(
            std::min<uint64_t>(max_points_per_launch64, static_cast<uint64_t>(point_count)));
        std::vector<GpuPipRecord> gpu_rows;

        auto launch_positive_candidate_pass = [&](
                size_t point_offset,
                size_t chunk_point_count,
                CUdeviceptr output_ptr,
                uint32_t output_capacity,
                bool allow_overflow) -> uint32_t {
            upload<uint32_t>(d_count.ptr, &zero, 1);
            const CUdeviceptr chunk_points_x =
                d_pts_x.ptr + static_cast<CUdeviceptr>(sizeof(float) * point_offset);
            const CUdeviceptr chunk_points_y =
                d_pts_y.ptr + static_cast<CUdeviceptr>(sizeof(float) * point_offset);
            const CUdeviceptr chunk_point_ids =
                d_pt_ids.ptr + static_cast<CUdeviceptr>(sizeof(uint32_t) * point_offset);
            lp.points_x = reinterpret_cast<const float*>(chunk_points_x);
            lp.points_y = reinterpret_cast<const float*>(chunk_points_y);
            lp.point_ids = reinterpret_cast<const uint32_t*>(chunk_point_ids);
            lp.output = output_capacity == 0u
                ? nullptr
                : reinterpret_cast<GpuPipRecord*>(output_ptr);
            lp.output_capacity = output_capacity;
            lp.probe_count = static_cast<uint32_t>(chunk_point_count);
            lp.point_index_offset = static_cast<uint32_t>(point_offset);
            upload(d_params.ptr, &lp, 1);
            const auto t_launch_start = std::chrono::steady_clock::now();
            OPTIX_CHECK(optixLaunch(g_pip.pipe->pipeline, stream,
                                     d_params.ptr, sizeof(PipLaunchParams),
                                     &g_pip.pipe->sbt,
                                     static_cast<unsigned>(chunk_point_count), 1, 1));
            CU_CHECK(cuStreamSynchronize(stream));
            const auto t_launch_end = std::chrono::steady_clock::now();
            if (output_capacity == 0u) {
                pip_count_pass_s += seconds_between(t_launch_start, t_launch_end);
            } else {
                pip_write_pass_s += seconds_between(t_launch_start, t_launch_end);
            }
            uint32_t emitted = 0;
            download(&emitted, d_count.ptr, 1);
            if (emitted > output_capacity && output_capacity != 0u && !allow_overflow) {
                throw std::runtime_error("PIP positive-hit output overflowed compact capacity");
            }
            return emitted;
        };

        for (size_t point_offset = 0; point_offset < point_count; point_offset += max_points_per_launch) {
            const size_t chunk_point_count = std::min(max_points_per_launch, point_count - point_offset);
            ++pip_chunks;
            uint32_t gpu_count = 0;
            if (pip_one_pass_compact) {
                const size_t optimistic_capacity_size = std::min<size_t>(
                    (std::max)(chunk_point_count, size_t{4096}),
                    static_cast<size_t>(std::numeric_limits<uint32_t>::max()));
                const uint32_t optimistic_capacity = static_cast<uint32_t>(optimistic_capacity_size);
                DevPtr d_positive_output(sizeof(GpuPipRecord) * optimistic_capacity);
                gpu_count = launch_positive_candidate_pass(
                    point_offset, chunk_point_count, d_positive_output.ptr, optimistic_capacity, true);
                pip_candidate_count += static_cast<size_t>(gpu_count);
                if (gpu_count <= optimistic_capacity) {
                    if (gpu_count == 0u) {
                        continue;
                    }
                    const size_t old_size = gpu_rows.size();
                    gpu_rows.resize(old_size + gpu_count);
                    const auto t_download_start = std::chrono::steady_clock::now();
                    download(gpu_rows.data() + old_size, d_positive_output.ptr, gpu_count);
                    const auto t_download_end = std::chrono::steady_clock::now();
                    pip_download_s += seconds_between(t_download_start, t_download_end);
                    continue;
                }
                ++pip_fallback_chunks;
            } else {
                gpu_count = launch_positive_candidate_pass(point_offset, chunk_point_count, 0, 0, false);
                pip_candidate_count += static_cast<size_t>(gpu_count);
                if (gpu_count == 0u) {
                    continue;
                }
            }
            DevPtr d_positive_output(sizeof(GpuPipRecord) * gpu_count);
            const uint32_t written_count =
                launch_positive_candidate_pass(point_offset, chunk_point_count, d_positive_output.ptr, gpu_count, false);
            if (written_count != gpu_count) {
                throw std::runtime_error("PIP positive-hit candidate count changed between count and write passes");
            }
            const size_t old_size = gpu_rows.size();
            gpu_rows.resize(old_size + gpu_count);
            const auto t_download_start = std::chrono::steady_clock::now();
            download(gpu_rows.data() + old_size, d_positive_output.ptr, gpu_count);
            const auto t_download_end = std::chrono::steady_clock::now();
            pip_download_s += seconds_between(t_download_start, t_download_end);
        }

        const auto t_refine_start = std::chrono::steady_clock::now();
        std::vector<RtdlPipRow> rows;
        rows.reserve(gpu_rows.size());
#if RTDL_OPTIX_HAS_GEOS
        GeosPreparedPolygonRefs geos(polys, poly_count, vertices_xy);
#endif
        for (const auto& gpu_row : gpu_rows) {
            const size_t pi = static_cast<size_t>(gpu_row.point_id);
            const size_t qi = static_cast<size_t>(gpu_row.polygon_id);
            if (pi >= point_count || qi >= poly_count) {
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
        const auto t_refine_end = std::chrono::steady_clock::now();
        pip_refine_s = seconds_between(t_refine_start, t_refine_end);
        auto* out = static_cast<RtdlPipRow*>(std::malloc(sizeof(RtdlPipRow) * rows.size()));
        if (!out && !rows.empty()) throw std::bad_alloc();
        for (size_t i = 0; i < rows.size(); ++i) {
            out[i] = rows[i];
        }
        *rows_out = out;
        *row_count_out = rows.size();
        if (profile_pip) {
            const auto t_total_end = std::chrono::steady_clock::now();
            std::fprintf(stderr,
                "[rtdl_optix_pip_profile] positive_only=%u one_pass=%u fallback_chunks=%zu points=%zu polygons=%zu chunks=%zu candidates=%zu emitted=%zu host_pack_s=%.9f upload_s=%.9f accel_build_s=%.9f count_pass_s=%.9f write_pass_s=%.9f compact_download_s=%.9f exact_refine_s=%.9f total_s=%.9f\n",
                positive_only,
                pip_one_pass_compact ? 1u : 0u,
                pip_fallback_chunks,
                point_count,
                poly_count,
                pip_chunks,
                pip_candidate_count,
                rows.size(),
                seconds_between(t_pack_start, t_pack_end),
                seconds_between(t_upload_start, t_upload_end),
                seconds_between(t_accel_start, t_accel_end),
                pip_count_pass_s,
                pip_write_pass_s,
                pip_download_s,
                pip_refine_s,
                seconds_between(t_total_start, t_total_end));
        }
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
    if (profile_pip) {
        const auto t_total_end = std::chrono::steady_clock::now();
        std::fprintf(stderr,
            "[rtdl_optix_pip_profile] positive_only=%u one_pass=%u fallback_chunks=%zu points=%zu polygons=%zu chunks=%zu candidates=%zu emitted=%zu host_pack_s=%.9f upload_s=%.9f accel_build_s=%.9f count_pass_s=%.9f write_pass_s=%.9f compact_download_s=%.9f exact_refine_s=%.9f total_s=%.9f\n",
            positive_only,
            pip_one_pass_compact ? 1u : 0u,
            pip_fallback_chunks,
            point_count,
            poly_count,
            pip_chunks,
            out_count,
            out_count,
            seconds_between(t_pack_start, t_pack_end),
            seconds_between(t_upload_start, t_upload_end),
            seconds_between(t_accel_start, t_accel_end),
            pip_count_pass_s,
            pip_write_pass_s,
            pip_download_s,
            pip_refine_s,
            seconds_between(t_total_start, t_total_end));
    }
}

static void run_point_closed_shape_membership_2d_optix(
        const RtdlPoint* points,           size_t point_count,
        const RtdlClosedShapeRef* shapes,  size_t shape_count,
        const double* vertices_xy,         size_t vertex_xy_count,
        uint32_t positive_only,
        RtdlPointClosedShapeMembershipRow** rows_out,
        size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (point_count == 0 || shape_count == 0) {
        return;
    }
    if (!shapes) {
        throw std::runtime_error("closed shapes pointer must not be null when shape_count is nonzero");
    }
    const auto* refs = reinterpret_cast<const RtdlPolygonRef*>(shapes);

    RtdlPipRow* raw_rows = nullptr;
    size_t raw_count = 0;
    run_pip_optix(
        points,
        point_count,
        refs,
        shape_count,
        vertices_xy,
        vertex_xy_count,
        positive_only,
        &raw_rows,
        &raw_count);

    struct RowsGuard {
        RtdlPipRow* rows = nullptr;
        ~RowsGuard() { std::free(rows); }
    } guard{raw_rows};

    auto* out = static_cast<RtdlPointClosedShapeMembershipRow*>(
        std::malloc(sizeof(RtdlPointClosedShapeMembershipRow) * raw_count));
    if (!out && raw_count != 0) {
        throw std::bad_alloc();
    }
    for (size_t i = 0; i < raw_count; ++i) {
        out[i] = RtdlPointClosedShapeMembershipRow{
            raw_rows[i].point_id,
            raw_rows[i].polygon_id,
            raw_rows[i].contains,
        };
    }
    *rows_out = out;
    *row_count_out = raw_count;
}

static void validate_polygon_ref_span_for_collection(
        const RtdlPolygonRef* polygons,
        size_t polygon_count,
        const double* vertices_xy,
        size_t vertex_xy_count,
        const char* label)
{
    if (!polygons && polygon_count != 0) {
        throw std::runtime_error(std::string(label) + " polygons pointer must not be null when count is nonzero");
    }
    if (!vertices_xy && vertex_xy_count != 0) {
        throw std::runtime_error(std::string(label) + " vertices_xy pointer must not be null when count is nonzero");
    }
    const size_t vertex_count = vertex_xy_count / 2;
    for (size_t i = 0; i < polygon_count; ++i) {
        if (polygons[i].vertex_count < 3) {
            throw std::runtime_error(std::string(label) + " polygon vertex_count must be at least 3");
        }
        const size_t offset = polygons[i].vertex_offset;
        const size_t count = polygons[i].vertex_count;
        if (offset > vertex_count || count > vertex_count - offset) {
            throw std::runtime_error(std::string(label) + " polygon offset/count exceeds vertices_xy");
        }
    }
}

static std::vector<RtdlSegment> segments_from_polygon_refs_for_collection(
        const RtdlPolygonRef* polygons,
        size_t polygon_count,
        const double* vertices_xy)
{
    std::vector<RtdlSegment> segments;
    for (size_t poly_index = 0; poly_index < polygon_count; ++poly_index) {
        const RtdlPolygonRef& polygon = polygons[poly_index];
        for (uint32_t vertex_index = 0; vertex_index < polygon.vertex_count; ++vertex_index) {
            const uint32_t next_index = (vertex_index + 1u) % polygon.vertex_count;
            const size_t start = static_cast<size_t>(polygon.vertex_offset + vertex_index) * 2u;
            const size_t end = static_cast<size_t>(polygon.vertex_offset + next_index) * 2u;
            segments.push_back(RtdlSegment{
                polygon.id,
                vertices_xy[start],
                vertices_xy[start + 1u],
                vertices_xy[end],
                vertices_xy[end + 1u],
            });
        }
    }
    return segments;
}

static std::vector<RtdlPoint> first_vertex_points_from_polygon_refs_for_collection(
        const RtdlPolygonRef* polygons,
        size_t polygon_count,
        const double* vertices_xy)
{
    std::vector<RtdlPoint> points;
    points.reserve(polygon_count);
    for (size_t poly_index = 0; poly_index < polygon_count; ++poly_index) {
        const RtdlPolygonRef& polygon = polygons[poly_index];
        const size_t first = static_cast<size_t>(polygon.vertex_offset) * 2u;
        points.push_back(RtdlPoint{
            polygon.id,
            vertices_xy[first],
            vertices_xy[first + 1u],
        });
    }
    return points;
}

static void collect_polygon_pair_candidates_bounded_optix(
        const RtdlPolygonRef* left_polygons,
        size_t left_count,
        const double* left_vertices_xy,
        size_t left_vertex_xy_count,
        const RtdlPolygonRef* right_polygons,
        size_t right_count,
        const double* right_vertices_xy,
        size_t right_vertex_xy_count,
        RtdlPolygonPairCandidate* candidates_out,
        size_t candidate_capacity,
        size_t* emitted_count_out,
        uint32_t* overflowed_out)
{
    if (!emitted_count_out || !overflowed_out) {
        throw std::runtime_error("emitted_count_out and overflowed_out must not be null");
    }
    *emitted_count_out = 0;
    *overflowed_out = 0;
    if (!candidates_out && candidate_capacity != 0) {
        throw std::runtime_error("candidates_out must not be null when candidate_capacity is nonzero");
    }
    if (left_count == 0 || right_count == 0) {
        return;
    }
    validate_polygon_ref_span_for_collection(
        left_polygons, left_count, left_vertices_xy, left_vertex_xy_count, "left");
    validate_polygon_ref_span_for_collection(
        right_polygons, right_count, right_vertices_xy, right_vertex_xy_count, "right");

    const std::vector<RtdlSegment> left_segments =
        segments_from_polygon_refs_for_collection(left_polygons, left_count, left_vertices_xy);
    const std::vector<RtdlSegment> right_segments =
        segments_from_polygon_refs_for_collection(right_polygons, right_count, right_vertices_xy);
    RtdlSegmentPairIntersectionRow* raw_segment_intersection_rows = nullptr;
    size_t segment_intersection_row_count = 0;
    run_segment_pair_intersection_optix(
        left_segments.data(), left_segments.size(),
        right_segments.data(), right_segments.size(),
        &raw_segment_intersection_rows, &segment_intersection_row_count);
    std::unique_ptr<RtdlSegmentPairIntersectionRow, decltype(&std::free)> segment_intersection_rows(raw_segment_intersection_rows, &std::free);

    std::vector<RtdlPolygonPairCandidate> candidates;
    candidates.reserve(segment_intersection_row_count);
    for (size_t i = 0; i < segment_intersection_row_count; ++i) {
        candidates.push_back({segment_intersection_rows.get()[i].left_id, segment_intersection_rows.get()[i].right_id});
    }

    const std::vector<RtdlPoint> left_first_points =
        first_vertex_points_from_polygon_refs_for_collection(left_polygons, left_count, left_vertices_xy);
    RtdlPipRow* raw_left_in_right_rows = nullptr;
    size_t left_in_right_count = 0;
    run_pip_optix(
        left_first_points.data(), left_first_points.size(),
        right_polygons, right_count,
        right_vertices_xy, right_vertex_xy_count,
        1u,
        &raw_left_in_right_rows, &left_in_right_count);
    std::unique_ptr<RtdlPipRow, decltype(&std::free)> left_in_right_rows(raw_left_in_right_rows, &std::free);
    for (size_t i = 0; i < left_in_right_count; ++i) {
        if (left_in_right_rows.get()[i].contains == 1u) {
            candidates.push_back({
                left_in_right_rows.get()[i].point_id,
                left_in_right_rows.get()[i].polygon_id,
            });
        }
    }

    const std::vector<RtdlPoint> right_first_points =
        first_vertex_points_from_polygon_refs_for_collection(right_polygons, right_count, right_vertices_xy);
    RtdlPipRow* raw_right_in_left_rows = nullptr;
    size_t right_in_left_count = 0;
    run_pip_optix(
        right_first_points.data(), right_first_points.size(),
        left_polygons, left_count,
        left_vertices_xy, left_vertex_xy_count,
        1u,
        &raw_right_in_left_rows, &right_in_left_count);
    std::unique_ptr<RtdlPipRow, decltype(&std::free)> right_in_left_rows(raw_right_in_left_rows, &std::free);
    for (size_t i = 0; i < right_in_left_count; ++i) {
        if (right_in_left_rows.get()[i].contains == 1u) {
            candidates.push_back({
                right_in_left_rows.get()[i].polygon_id,
                right_in_left_rows.get()[i].point_id,
            });
        }
    }

    std::sort(
        candidates.begin(),
        candidates.end(),
        [](const RtdlPolygonPairCandidate& a, const RtdlPolygonPairCandidate& b) {
            if (a.left_polygon_id != b.left_polygon_id) {
                return a.left_polygon_id < b.left_polygon_id;
            }
            return a.right_polygon_id < b.right_polygon_id;
        });
    candidates.erase(
        std::unique(
            candidates.begin(),
            candidates.end(),
            [](const RtdlPolygonPairCandidate& a, const RtdlPolygonPairCandidate& b) {
                return a.left_polygon_id == b.left_polygon_id &&
                       a.right_polygon_id == b.right_polygon_id;
            }),
        candidates.end());

    *emitted_count_out = candidates.size();
    if (candidates.size() > candidate_capacity) {
        *overflowed_out = 1u;
        return;
    }
    if (!candidates.empty()) {
        std::memcpy(candidates_out, candidates.data(), sizeof(RtdlPolygonPairCandidate) * candidates.size());
    }
}

// ---------- shape-pair relation ----------------------------------------------------------

struct ShapePairRelationLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPolygonRef* left_polygons;
    const GpuPolygonRef* right_polygons;
    const float* left_vx;
    const float* left_vy;
    const float* right_vx;
    const float* right_vy;
    GpuShapePairRelationFlags* output;
    uint32_t  right_count;
    uint32_t  left_count;
    uint32_t  launch_count;
    uint32_t  max_edges_per_poly;
};

static void ensure_shape_pair_relation_pipeline() {
    std::call_once(g_shape_pair_relation.init, [&]() {
        std::string ptx = compile_to_ptx(kShapePairRelationKernelSrc, "shape_pair_relation_kernel.cu");
        g_shape_pair_relation.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__shape_pair_relation_probe",
            "__miss__shape_pair_relation_miss",
            "__intersection__shape_pair_relation_isect",
            "__anyhit__shape_pair_relation_anyhit",
            nullptr, 4).release();
    });
}

struct PreparedShapePairRelationBuild {
    std::vector<RtdlPolygonRef> host_right_polygons;
    std::vector<double> host_right_vertices_xy;
    std::vector<GpuPolygonRef> right_polygons;
    std::vector<float> right_vx;
    std::vector<float> right_vy;
    size_t right_count = 0;
    size_t right_vert_xy_count = 0;
    size_t right_vert_count = 0;
    DevPtr d_right_polygons;
    DevPtr d_right_vx;
    DevPtr d_right_vy;
    AccelHolder accel;
#if RTDL_OPTIX_HAS_GEOS
    std::unique_ptr<GeosPreparedPolygonRefs> right_geos;
#endif

    PreparedShapePairRelationBuild(
            const RtdlPolygonRef* polys,
            size_t poly_count,
            const double* verts_xy,
            size_t vert_xy_count)
        : host_right_polygons(),
          host_right_vertices_xy(),
          right_polygons(poly_count),
          right_vx(vert_xy_count / 2u),
          right_vy(vert_xy_count / 2u),
          right_count(poly_count),
          right_vert_xy_count(vert_xy_count),
          right_vert_count(vert_xy_count / 2u),
          d_right_polygons(sizeof(GpuPolygonRef) * poly_count),
          d_right_vx(sizeof(float) * (vert_xy_count / 2u)),
          d_right_vy(sizeof(float) * (vert_xy_count / 2u))
    {
        if (poly_count > 0) {
            host_right_polygons.assign(polys, polys + poly_count);
        }
        if (vert_xy_count > 0) {
            host_right_vertices_xy.assign(verts_xy, verts_xy + vert_xy_count);
        }
        for (size_t i = 0; i < poly_count; ++i) {
            right_polygons[i] = {
                polys[i].id,
                polys[i].vertex_offset,
                polys[i].vertex_count,
            };
        }
        for (size_t i = 0; i < right_vert_count; ++i) {
            right_vx[i] = static_cast<float>(verts_xy[i * 2u]);
            right_vy[i] = static_cast<float>(verts_xy[i * 2u + 1u]);
        }
        upload(d_right_polygons.ptr, right_polygons.data(), right_polygons.size());
        upload(d_right_vx.ptr, right_vx.data(), right_vx.size());
        upload(d_right_vy.ptr, right_vy.data(), right_vy.size());

        if (!right_polygons.empty()) {
            std::vector<OptixAabb> aabbs(poly_count);
            for (size_t i = 0; i < poly_count; ++i) {
                aabbs[i] = aabb_for_polygon(
                    host_right_vertices_xy.data(),
                    host_right_polygons[i].vertex_offset,
                    host_right_polygons[i].vertex_count);
            }
            accel = build_custom_accel(get_optix_context(), aabbs);
        }
#if RTDL_OPTIX_HAS_GEOS
        if (!host_right_polygons.empty()) {
            right_geos = std::make_unique<GeosPreparedPolygonRefs>(
                host_right_polygons.data(),
                host_right_polygons.size(),
                host_right_vertices_xy.data());
        }
#endif
    }
};

static PreparedShapePairRelationBuild* prepare_point_closed_shape_membership_2d_optix(
        const RtdlClosedShapeRef* shapes,
        size_t shape_count,
        const double* vertices_xy,
        size_t vertex_xy_count)
{
    ensure_pip_pipeline();
    return new PreparedShapePairRelationBuild(
        reinterpret_cast<const RtdlPolygonRef*>(shapes),
        shape_count,
        vertices_xy,
        vertex_xy_count);
}

static void run_prepared_point_closed_shape_membership_2d_optix(
        PreparedShapePairRelationBuild* prepared,
        const RtdlPoint* points,
        size_t point_count,
        uint32_t positive_only,
        RtdlPointClosedShapeMembershipRow** rows_out,
        size_t* row_count_out)
{
    if (!prepared) {
        throw std::runtime_error("prepared closed-shape membership handle must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (positive_only == 0u) {
        throw std::runtime_error("prepared closed-shape membership currently supports positive-hit output only");
    }
    if (point_count == 0 || prepared->right_count == 0) {
        return;
    }
    if (point_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
        throw std::runtime_error("prepared closed-shape membership point count exceeds uint32_t chunk offset capacity");
    }
    if (prepared->right_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
        throw std::runtime_error("prepared closed-shape membership shape count exceeds uint32_t launch capacity");
    }

    ensure_pip_pipeline();

    std::vector<float> pts_x(point_count), pts_y(point_count);
    std::vector<uint32_t> pt_ids(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        pts_x[i] = static_cast<float>(points[i].x);
        pts_y[i] = static_cast<float>(points[i].y);
        pt_ids[i] = points[i].id;
    }

    DevPtr d_pts_x(sizeof(float) * point_count);
    DevPtr d_pts_y(sizeof(float) * point_count);
    DevPtr d_pt_ids(sizeof(uint32_t) * point_count);
    upload(d_pts_x.ptr, pts_x.data(), point_count);
    upload(d_pts_y.ptr, pts_y.data(), point_count);
    upload(d_pt_ids.ptr, pt_ids.data(), point_count);

    DevPtr d_count(sizeof(uint32_t));
    uint32_t zero = 0;
    upload<uint32_t>(d_count.ptr, &zero, 1);

    PipLaunchParams lp;
    lp.traversable    = prepared->accel.handle;
    lp.points_x       = reinterpret_cast<const float*>(d_pts_x.ptr);
    lp.points_y       = reinterpret_cast<const float*>(d_pts_y.ptr);
    lp.point_ids      = reinterpret_cast<const uint32_t*>(d_pt_ids.ptr);
    lp.polygons       = reinterpret_cast<const GpuPolygonRef*>(prepared->d_right_polygons.ptr);
    lp.vertices_x     = reinterpret_cast<const float*>(prepared->d_right_vx.ptr);
    lp.vertices_y     = reinterpret_cast<const float*>(prepared->d_right_vy.ptr);
    lp.hit_words      = nullptr;
    lp.output         = nullptr;
    lp.output_count   = reinterpret_cast<uint32_t*>(d_count.ptr);
    lp.output_capacity = 0u;
    lp.positive_only  = 1u;
    lp.hit_word_count = 0u;
    lp.polygon_count  = static_cast<uint32_t>(prepared->right_count);
    lp.probe_count    = static_cast<uint32_t>(point_count);
    lp.point_index_offset = 0u;
    lp.device_prefilter =
        std::getenv("RTDL_OPTIX_PIP_DISABLE_DEVICE_PREFILTER") == nullptr ? 1u : 0u;

    DevPtr d_params(sizeof(PipLaunchParams));
    upload(d_params.ptr, &lp, 1);
    CUstream stream = 0;

    const uint64_t max_points_per_launch64 =
        static_cast<uint64_t>(std::numeric_limits<uint32_t>::max()) /
        static_cast<uint64_t>(prepared->right_count);
    if (max_points_per_launch64 == 0) {
        throw std::runtime_error("prepared closed-shape membership cannot chunk shape set into uint32_t capacity");
    }
    const size_t max_points_per_launch = static_cast<size_t>(
        std::min<uint64_t>(max_points_per_launch64, static_cast<uint64_t>(point_count)));

    std::vector<GpuPipRecord> gpu_rows;
    const bool pip_one_pass_compact =
        std::getenv("RTDL_OPTIX_PIP_DISABLE_ONE_PASS_COMPACT") == nullptr;

    auto launch_positive_candidate_pass = [&](
            size_t point_offset,
            size_t chunk_point_count,
            CUdeviceptr output_ptr,
            uint32_t output_capacity,
            bool allow_overflow) -> uint32_t {
        upload<uint32_t>(d_count.ptr, &zero, 1);
        const CUdeviceptr chunk_points_x =
            d_pts_x.ptr + static_cast<CUdeviceptr>(sizeof(float) * point_offset);
        const CUdeviceptr chunk_points_y =
            d_pts_y.ptr + static_cast<CUdeviceptr>(sizeof(float) * point_offset);
        const CUdeviceptr chunk_point_ids =
            d_pt_ids.ptr + static_cast<CUdeviceptr>(sizeof(uint32_t) * point_offset);
        lp.points_x = reinterpret_cast<const float*>(chunk_points_x);
        lp.points_y = reinterpret_cast<const float*>(chunk_points_y);
        lp.point_ids = reinterpret_cast<const uint32_t*>(chunk_point_ids);
        lp.output = output_capacity == 0u
            ? nullptr
            : reinterpret_cast<GpuPipRecord*>(output_ptr);
        lp.output_capacity = output_capacity;
        lp.probe_count = static_cast<uint32_t>(chunk_point_count);
        lp.point_index_offset = static_cast<uint32_t>(point_offset);
        upload(d_params.ptr, &lp, 1);
        OPTIX_CHECK(optixLaunch(g_pip.pipe->pipeline, stream,
                                 d_params.ptr, sizeof(PipLaunchParams),
                                 &g_pip.pipe->sbt,
                                 static_cast<unsigned>(chunk_point_count), 1, 1));
        CU_CHECK(cuStreamSynchronize(stream));
        uint32_t emitted = 0;
        download(&emitted, d_count.ptr, 1);
        if (emitted > output_capacity && output_capacity != 0u && !allow_overflow) {
            throw std::runtime_error("prepared closed-shape membership output overflowed compact capacity");
        }
        return emitted;
    };

    for (size_t point_offset = 0; point_offset < point_count; point_offset += max_points_per_launch) {
        const size_t chunk_point_count = std::min(max_points_per_launch, point_count - point_offset);
        uint32_t gpu_count = 0;
        if (pip_one_pass_compact) {
            const size_t optimistic_capacity_size = std::min<size_t>(
                (std::max)(chunk_point_count, size_t{4096}),
                static_cast<size_t>(std::numeric_limits<uint32_t>::max()));
            const uint32_t optimistic_capacity = static_cast<uint32_t>(optimistic_capacity_size);
            DevPtr d_positive_output(sizeof(GpuPipRecord) * optimistic_capacity);
            gpu_count = launch_positive_candidate_pass(
                point_offset, chunk_point_count, d_positive_output.ptr, optimistic_capacity, true);
            if (gpu_count <= optimistic_capacity) {
                if (gpu_count == 0u) {
                    continue;
                }
                const size_t old_size = gpu_rows.size();
                gpu_rows.resize(old_size + gpu_count);
                download(gpu_rows.data() + old_size, d_positive_output.ptr, gpu_count);
                continue;
            }
        } else {
            gpu_count = launch_positive_candidate_pass(point_offset, chunk_point_count, 0, 0, false);
            if (gpu_count == 0u) {
                continue;
            }
        }
        DevPtr d_positive_output(sizeof(GpuPipRecord) * gpu_count);
        const uint32_t written_count =
            launch_positive_candidate_pass(point_offset, chunk_point_count, d_positive_output.ptr, gpu_count, false);
        if (written_count != gpu_count) {
            throw std::runtime_error("prepared closed-shape membership candidate count changed between count and write passes");
        }
        const size_t old_size = gpu_rows.size();
        gpu_rows.resize(old_size + gpu_count);
        download(gpu_rows.data() + old_size, d_positive_output.ptr, gpu_count);
    }

    std::vector<RtdlPointClosedShapeMembershipRow> rows;
    rows.reserve(gpu_rows.size());
    for (const auto& gpu_row : gpu_rows) {
        const size_t pi = static_cast<size_t>(gpu_row.point_id);
        const size_t qi = static_cast<size_t>(gpu_row.polygon_id);
        if (pi >= point_count || qi >= prepared->right_count) {
            continue;
        }
        const RtdlPoint& point = points[pi];
        const RtdlPolygonRef& shape = prepared->host_right_polygons[qi];
#if RTDL_OPTIX_HAS_GEOS
        if (prepared->right_geos && !prepared->right_geos->covers(qi, point.x, point.y)) {
            continue;
        }
#else
        if (!exact_point_in_polygon(point.x, point.y, shape, prepared->host_right_vertices_xy.data())) {
            continue;
        }
#endif
        rows.push_back({point.id, shape.id, 1u});
    }

    auto* out = static_cast<RtdlPointClosedShapeMembershipRow*>(
        std::malloc(sizeof(RtdlPointClosedShapeMembershipRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    for (size_t i = 0; i < rows.size(); ++i) {
        out[i] = rows[i];
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void count_prepared_point_closed_shape_membership_2d_optix(
        PreparedShapePairRelationBuild* prepared,
        const RtdlPoint* points,
        size_t point_count,
        size_t* count_out)
{
    if (!count_out) {
        throw std::runtime_error("count output pointer must not be null");
    }
    *count_out = 0;
    RtdlPointClosedShapeMembershipRow* rows = nullptr;
    size_t row_count = 0;
    run_prepared_point_closed_shape_membership_2d_optix(
        prepared,
        points,
        point_count,
        1u,
        &rows,
        &row_count);
    std::free(rows);
    *count_out = row_count;
}

static void run_shape_pair_relation_flags_with_prepared_right_optix(
        PreparedShapePairRelationBuild* prepared,
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        RtdlShapePairRelationRow** rows_out, size_t* row_count_out)
{
    if (!prepared) {
        throw std::runtime_error("prepared shape-pair relation handle must not be null");
    }
    ensure_shape_pair_relation_pipeline();
    const size_t right_count = prepared->right_count;
    if (left_count == 0 || right_count == 0) {
        *rows_out = nullptr;
        *row_count_out = 0;
        return;
    }

    size_t lv_count = left_vert_xy_count / 2;

    std::vector<GpuPolygonRef> gpu_lp(left_count);
    for (size_t i = 0; i < left_count;  ++i)
        gpu_lp[i] = {left_polys[i].id,  left_polys[i].vertex_offset,  left_polys[i].vertex_count};

    std::vector<float> lvx(lv_count), lvy(lv_count);
    for (size_t i = 0; i < lv_count; ++i) {
        lvx[i] = static_cast<float>(left_verts_xy[i * 2]);
        lvy[i] = static_cast<float>(left_verts_xy[i * 2 + 1]);
    }

    // Find max edges across all left polygons for launch stride
    uint32_t max_edges = 0;
    for (size_t i = 0; i < left_count; ++i)
        max_edges = std::max(max_edges, left_polys[i].vertex_count);

    DevPtr d_lp  (sizeof(GpuPolygonRef) * left_count);
    DevPtr d_lvx (sizeof(float) * lv_count);
    DevPtr d_lvy (sizeof(float) * lv_count);
    upload(d_lp.ptr,  gpu_lp.data(), left_count);
    upload(d_lvx.ptr, lvx.data(), lv_count);
    upload(d_lvy.ptr, lvy.data(), lv_count);

    // Pre-allocated output: left_count * right_count, all zeros
    size_t out_count = left_count * right_count;
    DevPtr d_output(sizeof(GpuShapePairRelationFlags) * out_count);
    CU_CHECK(cuMemsetD8(d_output.ptr, 0, sizeof(GpuShapePairRelationFlags) * out_count));

    uint32_t launch_count = static_cast<uint32_t>(left_count) * max_edges;

    ShapePairRelationLaunchParams lp;
    lp.traversable         = prepared->accel.handle;
    lp.left_polygons       = reinterpret_cast<const GpuPolygonRef*>(d_lp.ptr);
    lp.right_polygons      = reinterpret_cast<const GpuPolygonRef*>(prepared->d_right_polygons.ptr);
    lp.left_vx             = reinterpret_cast<const float*>(d_lvx.ptr);
    lp.left_vy             = reinterpret_cast<const float*>(d_lvy.ptr);
    lp.right_vx            = reinterpret_cast<const float*>(prepared->d_right_vx.ptr);
    lp.right_vy            = reinterpret_cast<const float*>(prepared->d_right_vy.ptr);
    lp.output              = reinterpret_cast<GpuShapePairRelationFlags*>(d_output.ptr);
    lp.right_count         = static_cast<uint32_t>(right_count);
    lp.left_count          = static_cast<uint32_t>(left_count);
    lp.launch_count        = launch_count;
    lp.max_edges_per_poly  = max_edges;

    DevPtr d_params(sizeof(ShapePairRelationLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_shape_pair_relation.pipe->pipeline, stream,
                             d_params.ptr, sizeof(ShapePairRelationLaunchParams),
                             &g_shape_pair_relation.pipe->sbt,
                             launch_count, 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    // Also compute PIP flags: for each (left_poly, right_poly) pair, check if
    // any vertex of one polygon is inside the other.  Done on CPU after the
    // GPU segment-pair intersection pass to keep the device kernel simple.
    std::vector<GpuShapePairRelationFlags> gpu_flags(out_count);
    download(gpu_flags.data(), d_output.ptr, out_count);

    // CPU PIP supplement: match the current RTDL oracle semantics exactly.
    // shape_pair_relation_comgroup_cpu checks only the first vertex of each polygon.
#if RTDL_OPTIX_HAS_GEOS
    GeosPreparedPolygonRefs left_geos(left_polys, left_count, left_verts_xy);
#endif

    for (size_t li = 0; li < left_count; ++li) {
        for (size_t ri = 0; ri < right_count; ++ri) {
            size_t slot = li * right_count + ri;
            if (gpu_flags[slot].requires_point_containment) continue; // already set by GPU
            bool found = false;
            if (left_polys[li].vertex_count > 0) {
                double lxv = left_verts_xy[left_polys[li].vertex_offset * 2];
                double lyv = left_verts_xy[left_polys[li].vertex_offset * 2 + 1];
#if RTDL_OPTIX_HAS_GEOS
                if (prepared->right_geos && prepared->right_geos->covers(ri, lxv, lyv))
#else
                if (exact_point_in_polygon(
                        lxv, lyv,
                        prepared->host_right_polygons[ri],
                        prepared->host_right_vertices_xy.data()))
#endif
                    found = true;
            }
            if (!found && prepared->host_right_polygons[ri].vertex_count > 0) {
                const RtdlPolygonRef& right_poly = prepared->host_right_polygons[ri];
                double rxv = prepared->host_right_vertices_xy[right_poly.vertex_offset * 2];
                double ryv = prepared->host_right_vertices_xy[right_poly.vertex_offset * 2 + 1];
#if RTDL_OPTIX_HAS_GEOS
                if (left_geos.covers(li, rxv, ryv))
#else
                if (exact_point_in_polygon(rxv, ryv, left_polys[li], left_verts_xy))
#endif
                    found = true;
            }
            if (found)
                gpu_flags[slot].requires_point_containment = 1;
        }
    }

    auto* out = static_cast<RtdlShapePairRelationRow*>(std::malloc(sizeof(RtdlShapePairRelationRow) * out_count));
    if (!out) throw std::bad_alloc();
    for (size_t i = 0; i < out_count; ++i) {
        size_t li = i / right_count, ri = i % right_count;
        out[i].left_polygon_id  = left_polys[li].id;
        out[i].right_polygon_id = prepared->host_right_polygons[ri].id;
        out[i].requires_segment_intersection     = gpu_flags[i].requires_segment_intersection;
        out[i].requires_point_containment     = gpu_flags[i].requires_point_containment;
    }
    *rows_out      = out;
    *row_count_out = out_count;
}

static void run_shape_pair_relation_flags_optix(
        const RtdlPolygonRef* left_polys,  size_t left_count,
        const double* left_verts_xy,       size_t left_vert_xy_count,
        const RtdlPolygonRef* right_polys, size_t right_count,
        const double* right_verts_xy,      size_t right_vert_xy_count,
        RtdlShapePairRelationRow** rows_out, size_t* row_count_out)
{
    ensure_shape_pair_relation_pipeline();
    PreparedShapePairRelationBuild prepared(right_polys, right_count, right_verts_xy, right_vert_xy_count);
    run_shape_pair_relation_flags_with_prepared_right_optix(
        &prepared,
        left_polys, left_count, left_verts_xy, left_vert_xy_count,
        rows_out, row_count_out);
}

static PreparedShapePairRelationBuild* prepare_shape_pair_relation_flags_optix(
        const RtdlPolygonRef* right_polys,
        size_t right_count,
        const double* right_verts_xy,
        size_t right_vert_xy_count)
{
    ensure_shape_pair_relation_pipeline();
    return new PreparedShapePairRelationBuild(right_polys, right_count, right_verts_xy, right_vert_xy_count);
}

static void run_prepared_shape_pair_relation_flags_optix(
        PreparedShapePairRelationBuild* prepared,
        const RtdlPolygonRef* left_polys, size_t left_count,
        const double* left_verts_xy, size_t left_vert_xy_count,
        RtdlShapePairRelationRow** rows_out, size_t* row_count_out)
{
    run_shape_pair_relation_flags_with_prepared_right_optix(
        prepared,
        left_polys, left_count, left_verts_xy, left_vert_xy_count,
        rows_out, row_count_out);
}

// ---------- Ray-triangle hit count ------------------------------------------

struct RayHitCountLaunchParams {
    OptixTraversableHandle traversable;
    const GpuRay*          rays;
    const GpuTriangle*     triangles;
    GpuRayHitRecord*       output;
    uint32_t               ray_count;
};

static std::string ray_anyhit_kernel_source_2d();

struct RayAnyHitCountLaunchParams {
    OptixTraversableHandle traversable;
    const GpuRay*          rays;
    const GpuTriangle*     triangles;
    uint32_t*              hit_count;
    uint32_t               ray_count;
};

struct RayAnyHitCountDeviceRayColumnsLaunchParams {
    OptixTraversableHandle traversable;
    const uint32_t*        ray_ids;
    const double*          ray_ox;
    const double*          ray_oy;
    const double*          ray_dx;
    const double*          ray_dy;
    const double*          ray_tmax;
    const GpuTriangle*     triangles;
    uint32_t*              hit_count;
    uint32_t               ray_count;
};

struct RayAnyHitCountDeviceColumnsLaunchParams {
    OptixTraversableHandle traversable;
    const uint32_t*        ray_ids;
    const double*          ray_ox;
    const double*          ray_oy;
    const double*          ray_dx;
    const double*          ray_dy;
    const double*          ray_tmax;
    const uint32_t*        triangle_ids;
    const double*          triangle_x0;
    const double*          triangle_y0;
    const double*          triangle_x1;
    const double*          triangle_y1;
    const double*          triangle_x2;
    const double*          triangle_y2;
    uint32_t*              hit_count;
    uint32_t               ray_count;
};

struct RayAnyHitFlagsDeviceColumnsLaunchParams {
    OptixTraversableHandle traversable;
    const uint32_t*        ray_ids;
    const double*          ray_ox;
    const double*          ray_oy;
    const double*          ray_dx;
    const double*          ray_dy;
    const double*          ray_tmax;
    const uint32_t*        triangle_ids;
    const double*          triangle_x0;
    const double*          triangle_y0;
    const double*          triangle_x1;
    const double*          triangle_y1;
    const double*          triangle_x2;
    const double*          triangle_y2;
    uint32_t*              any_hit_flags;
    uint32_t               ray_count;
};

struct RayAnyHitWitnessDeviceColumnsLaunchParams {
    OptixTraversableHandle traversable;
    const uint32_t*        ray_ids;
    const double*          ray_ox;
    const double*          ray_oy;
    const double*          ray_dx;
    const double*          ray_dy;
    const double*          ray_tmax;
    const uint32_t*        triangle_ids;
    const double*          triangle_x0;
    const double*          triangle_y0;
    const double*          triangle_x1;
    const double*          triangle_y1;
    const double*          triangle_x2;
    const double*          triangle_y2;
    uint32_t*              witness_ray_ids;
    uint32_t*              witness_primitive_ids;
    uint32_t               ray_count;
};

struct RayAnyHitAllWitnessesDeviceColumnsLaunchParams {
    OptixTraversableHandle traversable;
    const uint32_t*        ray_ids;
    const double*          ray_ox;
    const double*          ray_oy;
    const double*          ray_dx;
    const double*          ray_dy;
    const double*          ray_tmax;
    const uint32_t*        triangle_ids;
    const double*          triangle_x0;
    const double*          triangle_y0;
    const double*          triangle_x1;
    const double*          triangle_y1;
    const double*          triangle_x2;
    const double*          triangle_y2;
    uint32_t*              witness_ray_ids;
    uint32_t*              witness_primitive_ids;
    uint32_t*              emitted_count;
    uint32_t*              overflowed;
    uint32_t               witness_capacity;
    uint32_t               ray_count;
};

struct RayAnyHitGroupFlagsLaunchParams {
    OptixTraversableHandle traversable;
    const GpuRay*          rays;
    const GpuTriangle*     triangles;
    const uint32_t*        group_indices;
    uint32_t*              group_flags;
    uint32_t*              colliding_group_count;
    uint32_t               ray_count;
    uint32_t               group_count;
};

static void ensure_ray_anyhit_2d_pipeline()
{
    std::call_once(g_rayanyhit.init, [&]() {
        std::string src = ray_anyhit_kernel_source_2d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_kernel.cu");
        g_rayanyhit.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });
}

static std::string ray_anyhit_count_kernel_source_2d()
{
    std::string src = ray_anyhit_kernel_source_2d();
    const std::string old_output_field =
        "    RayHitCountRecord* output;\n";
    const std::string new_output_field =
        "    uint32_t* hit_count;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit count params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_zero_write =
        "        params.output[idx] = {r.id, 0u};\n"
        "        return;\n";
    const std::string new_zero_write =
        "        return;\n";
    pos = src.find(old_zero_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit count zero-ray path");
    src.replace(pos, old_zero_write.size(), new_zero_write);

    const std::string old_final_write =
        "    params.output[idx] = {r.id, p1};\n";
    const std::string new_final_write =
        "    if (p1 != 0u) atomicAdd(params.hit_count, 1u);\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit count output path");
    src.replace(pos, old_final_write.size(), new_final_write);
    return src;
}

static void ensure_ray_anyhit_count_2d_pipeline()
{
    std::call_once(g_rayanyhit_count.init, [&]() {
        std::string src = ray_anyhit_count_kernel_source_2d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_count_kernel.cu");
        g_rayanyhit_count.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });
}

static std::string ray_anyhit_count_device_ray_columns_kernel_source_2d()
{
    std::string src = ray_anyhit_count_kernel_source_2d();
    const std::string old_ray_field =
        "    const GpuRay*      rays;\n";
    const std::string new_ray_fields =
        "    const uint32_t* ray_ids;\n"
        "    const double* ray_ox;\n"
        "    const double* ray_oy;\n"
        "    const double* ray_dx;\n"
        "    const double* ray_dy;\n"
        "    const double* ray_tmax;\n";
    size_t pos = src.find(old_ray_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit count device-ray columns params");
    src.replace(pos, old_ray_field.size(), new_ray_fields);

    const std::string constant_decl =
        "extern \"C\" {\n"
        "__constant__ RayHitCountParams params;\n"
        "}\n";
    const std::string helper =
        "extern \"C\" {\n"
        "__constant__ RayHitCountParams params;\n"
        "}\n\n"
        "static __forceinline__ __device__ GpuRay load_ray_column(uint32_t idx) {\n"
        "    GpuRay r;\n"
        "    r.ox = static_cast<float>(params.ray_ox[idx]);\n"
        "    r.oy = static_cast<float>(params.ray_oy[idx]);\n"
        "    r.dx = static_cast<float>(params.ray_dx[idx]);\n"
        "    r.dy = static_cast<float>(params.ray_dy[idx]);\n"
        "    r.tmax = static_cast<float>(params.ray_tmax[idx]);\n"
        "    r.id = params.ray_ids[idx];\n"
        "    return r;\n"
        "}\n";
    pos = src.find(constant_decl);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to insert OptiX 2-D any-hit device-ray columns loader");
    src.replace(pos, constant_decl.size(), helper);

    const std::string packed_raygen_read =
        "const GpuRay r = params.rays[idx];";
    const std::string column_raygen_read =
        "const GpuRay r = load_ray_column(idx);";
    pos = src.find(packed_raygen_read);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit count device-ray raygen read");
    src.replace(pos, packed_raygen_read.size(), column_raygen_read);

    const std::string packed_intersection_read =
        "const GpuRay r = params.rays[ridx];";
    const std::string column_intersection_read =
        "const GpuRay r = load_ray_column(ridx);";
    pos = src.find(packed_intersection_read);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit count device-ray intersection read");
    src.replace(pos, packed_intersection_read.size(), column_intersection_read);
    return src;
}

static void ensure_ray_anyhit_count_device_ray_columns_2d_pipeline()
{
    std::call_once(g_rayanyhit_count_device_ray_columns.init, [&]() {
        std::string src = ray_anyhit_count_device_ray_columns_kernel_source_2d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_count_device_ray_columns_kernel.cu");
        g_rayanyhit_count_device_ray_columns.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });
}

static std::string ray_anyhit_count_device_columns_kernel_source_2d()
{
    std::string src = ray_anyhit_count_device_ray_columns_kernel_source_2d();
    const std::string old_triangle_field =
        "    const GpuTriangle* triangles;\n";
    const std::string new_triangle_fields =
        "    const uint32_t* triangle_ids;\n"
        "    const double* triangle_x0;\n"
        "    const double* triangle_y0;\n"
        "    const double* triangle_x1;\n"
        "    const double* triangle_y1;\n"
        "    const double* triangle_x2;\n"
        "    const double* triangle_y2;\n";
    size_t pos = src.find(old_triangle_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit count device triangle columns params");
    src.replace(pos, old_triangle_field.size(), new_triangle_fields);

    const std::string ray_loader_end =
        "static __forceinline__ __device__ GpuRay load_ray_column(uint32_t idx) {\n"
        "    GpuRay r;\n"
        "    r.ox = static_cast<float>(params.ray_ox[idx]);\n"
        "    r.oy = static_cast<float>(params.ray_oy[idx]);\n"
        "    r.dx = static_cast<float>(params.ray_dx[idx]);\n"
        "    r.dy = static_cast<float>(params.ray_dy[idx]);\n"
        "    r.tmax = static_cast<float>(params.ray_tmax[idx]);\n"
        "    r.id = params.ray_ids[idx];\n"
        "    return r;\n"
        "}\n";
    const std::string triangle_loader =
        ray_loader_end +
        "\n"
        "static __forceinline__ __device__ GpuTriangle load_triangle_column(uint32_t idx) {\n"
        "    GpuTriangle t;\n"
        "    t.x0 = static_cast<float>(params.triangle_x0[idx]);\n"
        "    t.y0 = static_cast<float>(params.triangle_y0[idx]);\n"
        "    t.x1 = static_cast<float>(params.triangle_x1[idx]);\n"
        "    t.y1 = static_cast<float>(params.triangle_y1[idx]);\n"
        "    t.x2 = static_cast<float>(params.triangle_x2[idx]);\n"
        "    t.y2 = static_cast<float>(params.triangle_y2[idx]);\n"
        "    t.id = params.triangle_ids[idx];\n"
        "    return t;\n"
        "}\n";
    pos = src.find(ray_loader_end);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to insert OptiX 2-D any-hit device triangle columns loader");
    src.replace(pos, ray_loader_end.size(), triangle_loader);

    const std::string packed_triangle_read =
        "const GpuTriangle t = params.triangles[prim];";
    const std::string column_triangle_read =
        "const GpuTriangle t = load_triangle_column(prim);";
    pos = src.find(packed_triangle_read);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit count device triangle read");
    src.replace(pos, packed_triangle_read.size(), column_triangle_read);
    return src;
}

static void ensure_ray_anyhit_count_device_columns_2d_pipeline()
{
    std::call_once(g_rayanyhit_count_device_columns.init, [&]() {
        std::string src = ray_anyhit_count_device_columns_kernel_source_2d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_count_device_columns_kernel.cu");
        g_rayanyhit_count_device_columns.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });
}

static std::string ray_anyhit_flags_device_columns_kernel_source_2d()
{
    std::string src = ray_anyhit_count_device_columns_kernel_source_2d();
    const std::string old_output_field =
        "    uint32_t* hit_count;\n";
    const std::string new_output_field =
        "    uint32_t* any_hit_flags;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit flags output params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_final_write =
        "    if (p1 != 0u) atomicAdd(params.hit_count, 1u);\n";
    const std::string new_final_write =
        "    params.any_hit_flags[idx] = p1 ? 1u : 0u;\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit flags output write");
    src.replace(pos, old_final_write.size(), new_final_write);
    return src;
}

static void ensure_ray_anyhit_flags_device_columns_2d_pipeline()
{
    std::call_once(g_rayanyhit_flags_device_columns.init, [&]() {
        std::string src = ray_anyhit_flags_device_columns_kernel_source_2d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_flags_device_columns_kernel.cu");
        g_rayanyhit_flags_device_columns.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });
}

static std::string ray_anyhit_witness_device_columns_kernel_source_2d()
{
    std::string src = ray_anyhit_count_device_columns_kernel_source_2d();
    const std::string old_output_field =
        "    uint32_t* hit_count;\n";
    const std::string new_output_field =
        "    uint32_t* witness_ray_ids;\n"
        "    uint32_t* witness_primitive_ids;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit witness output params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_final_write =
        "    if (p1 != 0u) atomicAdd(params.hit_count, 1u);\n";
    const std::string new_final_write =
        "    params.witness_ray_ids[idx] = r.id;\n"
        "    params.witness_primitive_ids[idx] = p1 ? p2 : 0xFFFFFFFFu;\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit witness output write");
    src.replace(pos, old_final_write.size(), new_final_write);

    const std::string old_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit_anyhit() {\n"
        "    optixSetPayload_1(1u);\n"
        "    optixTerminateRay();\n"
        "}\n";
    const std::string new_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit_anyhit() {\n"
        "    const uint32_t prim = optixGetPrimitiveIndex();\n"
        "    const GpuTriangle t = load_triangle_column(prim);\n"
        "    optixSetPayload_1(1u);\n"
        "    optixSetPayload_2(t.id);\n"
        "    optixTerminateRay();\n"
        "}\n";
    pos = src.find(old_anyhit);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit witness identity write");
    src.replace(pos, old_anyhit.size(), new_anyhit);
    return src;
}

static void ensure_ray_anyhit_witness_device_columns_2d_pipeline()
{
    std::call_once(g_rayanyhit_witness_device_columns.init, [&]() {
        std::string src = ray_anyhit_witness_device_columns_kernel_source_2d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_witness_device_columns_kernel.cu");
        g_rayanyhit_witness_device_columns.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });
}

static std::string ray_anyhit_all_witnesses_device_columns_kernel_source_2d()
{
    std::string src = ray_anyhit_count_device_columns_kernel_source_2d();
    for (const char* field : {
             "    const double* ray_ox;\n",
             "    const double* ray_oy;\n",
             "    const double* ray_dx;\n",
             "    const double* ray_dy;\n",
             "    const double* ray_tmax;\n",
         }) {
        size_t field_pos = src.find(field);
        if (field_pos == std::string::npos)
            throw std::runtime_error("failed to specialize OptiX 2-D all-witness ray column dtype");
        std::string replacement(field);
        size_t double_pos = replacement.find("double");
        replacement.replace(double_pos, 6, "float");
        src.replace(field_pos, std::strlen(field), replacement);
    }
    const std::string intersection_start =
        "extern \"C\" __global__ void __intersection__rayhit_isect() {\n";
    const std::string anyhit_start =
        "\nextern \"C\" __global__ void __anyhit__rayhit_anyhit()";
    const std::string new_intersection =
        "extern \"C\" __global__ void __intersection__rayhit_isect() {\n"
        "    float hit_t = optixGetRayTmin() + 1.0e-6f;\n"
        "    if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();\n"
        "    optixReportIntersection(hit_t, 0u);\n"
        "}\n";
    size_t pos = src.find(intersection_start);
    size_t end = src.find(anyhit_start, pos);
    if (pos == std::string::npos || end == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D all-witness candidate intersection");
    src.replace(pos, end - pos, new_intersection);

    const std::string old_output_field =
        "    uint32_t* hit_count;\n";
    const std::string new_output_field =
        "    uint32_t* witness_ray_ids;\n"
        "    uint32_t* witness_primitive_ids;\n"
        "    uint32_t* emitted_count;\n"
        "    uint32_t* overflowed;\n"
        "    uint32_t witness_capacity;\n";
    pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D all-witness output params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_final_write =
        "    if (p1 != 0u) atomicAdd(params.hit_count, 1u);\n";
    const std::string new_final_write =
        "    (void)p1;\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D all-witness raygen output path");
    src.replace(pos, old_final_write.size(), new_final_write);

    const std::string old_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit_anyhit() {\n"
        "    optixSetPayload_1(1u);\n"
        "    optixTerminateRay();\n"
        "}\n";
    const std::string new_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit_anyhit() {\n"
        "    const uint32_t idx = optixGetLaunchIndex().x;\n"
        "    const uint32_t prim = optixGetPrimitiveIndex();\n"
        "    const uint32_t slot = atomicAdd(params.emitted_count, 1u);\n"
        "    if (slot < params.witness_capacity) {\n"
        "        params.witness_ray_ids[slot] = params.ray_ids[idx];\n"
        "        params.witness_primitive_ids[slot] = params.triangle_ids[prim];\n"
        "    } else {\n"
        "        atomicExch(params.overflowed, 1u);\n"
        "    }\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    pos = src.find(old_anyhit);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D all-witness identity write");
    src.replace(pos, old_anyhit.size(), new_anyhit);
    return src;
}

static void ensure_ray_anyhit_all_witnesses_device_columns_2d_pipeline()
{
    std::call_once(g_rayanyhit_all_witnesses_device_columns.init, [&]() {
        std::string src = ray_anyhit_all_witnesses_device_columns_kernel_source_2d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_all_witnesses_device_columns_kernel.cu");
        g_rayanyhit_all_witnesses_device_columns.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });
}

static std::string ray_anyhit_group_flags_kernel_source_2d()
{
    std::string src = ray_anyhit_kernel_source_2d();
    const std::string old_output_field =
        "    RayHitCountRecord* output;\n"
        "    uint32_t ray_count;\n";
    const std::string new_output_field =
        "    const uint32_t* group_indices;\n"
        "    uint32_t* group_flags;\n"
        "    uint32_t* colliding_group_count;\n"
        "    uint32_t ray_count;\n"
        "    uint32_t group_count;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit group-flags params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_zero_write =
        "        params.output[idx] = {r.id, 0u};\n"
        "        return;\n";
    const std::string new_zero_write =
        "        return;\n";
    pos = src.find(old_zero_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit group-flags zero-ray path");
    src.replace(pos, old_zero_write.size(), new_zero_write);

    const std::string old_final_write =
        "    params.output[idx] = {r.id, p1};\n";
    const std::string new_final_write =
        "    if (p1 != 0u) {\n"
        "        const uint32_t group_index = params.group_indices[idx];\n"
        "        if (group_index < params.group_count) {\n"
        "            const uint32_t previous = atomicExch(&params.group_flags[group_index], 1u);\n"
        "            if (previous == 0u && params.colliding_group_count != nullptr) atomicAdd(params.colliding_group_count, 1u);\n"
        "        }\n"
        "    }\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit group-flags output path");
    src.replace(pos, old_final_write.size(), new_final_write);
    return src;
}

static void ensure_ray_anyhit_group_flags_2d_pipeline()
{
    std::call_once(g_rayanyhit_group_flags.init, [&]() {
        std::string src = ray_anyhit_group_flags_kernel_source_2d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_group_flags_kernel.cu");
        g_rayanyhit_group_flags.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit_probe",
            "__miss__rayhit_miss",
            "__intersection__rayhit_isect",
            "__anyhit__rayhit_anyhit",
            nullptr, 4).release();
    });
}

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

static std::string ray_anyhit_kernel_source_2d()
{
    std::string src(kRayHitCountKernelSrc);
    const std::string old_body =
        "extern \"C\" __global__ void __anyhit__rayhit_anyhit() {\n"
        "    uint32_t count = optixGetPayload_1();\n"
        "    optixSetPayload_1(count + 1u);\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    const std::string new_body =
        "extern \"C\" __global__ void __anyhit__rayhit_anyhit() {\n"
        "    optixSetPayload_1(1u);\n"
        "    optixTerminateRay();\n"
        "}\n";
    const size_t pos = src.find(old_body);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 2-D any-hit kernel");
    src.replace(pos, old_body.size(), new_body);
    return src;
}

static void run_ray_anyhit_optix(
        const RtdlRay2D*    rays,      size_t ray_count,
        const RtdlTriangle* triangles, size_t triangle_count,
        RtdlRayAnyHitRow** rows_out, size_t* row_count_out)
{
    ensure_ray_anyhit_2d_pipeline();

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

    DevPtr d_output(sizeof(GpuRayAnyHitRecord) * ray_count);

    RayHitCountLaunchParams lp;
    lp.traversable = accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay*>(d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle*>(d_tris.ptr);
    lp.output      = reinterpret_cast<GpuRayHitRecord*>(d_output.ptr);
    lp.ray_count   = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayHitCountLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayHitCountLaunchParams),
                             &g_rayanyhit.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuRayAnyHitRecord> gpu_rows(ray_count);
    download(gpu_rows.data(), d_output.ptr, ray_count);

    auto* out = static_cast<RtdlRayAnyHitRow*>(
        std::malloc(sizeof(RtdlRayAnyHitRow) * ray_count));
    if (!out && ray_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < ray_count; ++i) {
        out[i].ray_id = gpu_rows[i].ray_id;
        out[i].any_hit = gpu_rows[i].any_hit ? 1u : 0u;
    }
    *rows_out      = out;
    *row_count_out = ray_count;
}

struct PreparedRayAnyHit2D {
    std::vector<GpuTriangle> triangles;
    size_t triangle_count = 0;
    DevPtr d_triangles;
    AccelHolder accel;
    bool triangle_columns_zero_copy = false;
    const uint32_t* triangle_ids = nullptr;
    const double* triangle_x0 = nullptr;
    const double* triangle_y0 = nullptr;
    const double* triangle_x1 = nullptr;
    const double* triangle_y1 = nullptr;
    const double* triangle_x2 = nullptr;
    const double* triangle_y2 = nullptr;

    explicit PreparedRayAnyHit2D(const RtdlTriangle* source, size_t count)
        : triangles(count), triangle_count(count), d_triangles(sizeof(GpuTriangle) * count)
    {
        for (size_t i = 0; i < count; ++i) {
            triangles[i] = {
                static_cast<float>(source[i].x0),
                static_cast<float>(source[i].y0),
                static_cast<float>(source[i].x1),
                static_cast<float>(source[i].y1),
                static_cast<float>(source[i].x2),
                static_cast<float>(source[i].y2),
                source[i].id,
            };
        }
        upload(d_triangles.ptr, triangles.data(), triangles.size());

        if (!triangles.empty()) {
            std::vector<OptixAabb> aabbs(triangles.size());
            for (size_t i = 0; i < triangles.size(); ++i) {
                aabbs[i] = aabb_for_triangle(
                    triangles[i].x0, triangles[i].y0,
                    triangles[i].x1, triangles[i].y1,
                    triangles[i].x2, triangles[i].y2);
            }
            accel = build_custom_accel(get_optix_context(), aabbs);
        }
    }

    PreparedRayAnyHit2D(
            const uint32_t* triangle_ids,
            const double* triangle_x0,
            const double* triangle_y0,
            const double* triangle_x1,
            const double* triangle_y1,
            const double* triangle_x2,
            const double* triangle_y2,
            size_t count);

    PreparedRayAnyHit2D(
            const uint32_t* triangle_ids,
            const double* triangle_x0,
            const double* triangle_y0,
            const double* triangle_x1,
            const double* triangle_y1,
            const double* triangle_x2,
            const double* triangle_y2,
            const void* triangle_aabbs,
            size_t count);
};

struct PreparedRays2D {
    size_t ray_count;
    DevPtr d_rays;

    explicit PreparedRays2D(const RtdlRay2D* source, size_t count)
        : ray_count(count), d_rays(sizeof(GpuRay) * count)
    {
        std::vector<GpuRay> rays(count);
        for (size_t i = 0; i < count; ++i) {
            rays[i] = {
                static_cast<float>(source[i].ox),
                static_cast<float>(source[i].oy),
                static_cast<float>(source[i].dx),
                static_cast<float>(source[i].dy),
                static_cast<float>(source[i].tmax),
                source[i].id,
            };
        }
        upload(d_rays.ptr, rays.data(), rays.size());
    }
};

struct PreparedGroupIndices2D {
    size_t count;
    DevPtr d_group_indices;

    explicit PreparedGroupIndices2D(const uint32_t* source, size_t index_count)
        : count(index_count), d_group_indices(sizeof(uint32_t) * index_count)
    {
        if (!source && index_count != 0)
            throw std::runtime_error("group_indices pointer must not be null when index_count is nonzero");
        upload(d_group_indices.ptr, source, index_count);
    }
};

static void ensure_pack_triangle2d_device_columns_kernel()
{
    (void)get_optix_context();
    std::call_once(g_partner_triangle2d_pack.init, [&]() {
        const std::string ptx = compile_to_ptx(
            kPackTriangle2DDeviceColumnsKernelSrc,
            "partner_triangle2d_device_columns_pack_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_partner_triangle2d_pack.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(
            &g_partner_triangle2d_pack.fn,
            g_partner_triangle2d_pack.module,
            "pack_triangle2d_device_columns"));
    });
}

PreparedRayAnyHit2D::PreparedRayAnyHit2D(
        const uint32_t* triangle_ids,
        const double* triangle_x0,
        const double* triangle_y0,
        const double* triangle_x1,
        const double* triangle_y1,
        const double* triangle_x2,
        const double* triangle_y2,
        size_t count)
    : triangle_count(count), d_triangles(sizeof(GpuTriangle) * count)
{
    if (count == 0) return;
    if (!triangle_ids || !triangle_x0 || !triangle_y0 || !triangle_x1
            || !triangle_y1 || !triangle_x2 || !triangle_y2)
        throw std::runtime_error("partner device triangle column pointers must not be null when triangle_count is nonzero");
    if (count > std::numeric_limits<uint32_t>::max())
        throw std::runtime_error("partner device triangle column count exceeds uint32_t launch limit");

    ensure_pack_triangle2d_device_columns_kernel();

    DevPtr d_aabbs(sizeof(OptixAabb) * count);
    CUdeviceptr d_triangle_ids = reinterpret_cast<CUdeviceptr>(triangle_ids);
    CUdeviceptr d_triangle_x0 = reinterpret_cast<CUdeviceptr>(triangle_x0);
    CUdeviceptr d_triangle_y0 = reinterpret_cast<CUdeviceptr>(triangle_y0);
    CUdeviceptr d_triangle_x1 = reinterpret_cast<CUdeviceptr>(triangle_x1);
    CUdeviceptr d_triangle_y1 = reinterpret_cast<CUdeviceptr>(triangle_y1);
    CUdeviceptr d_triangle_x2 = reinterpret_cast<CUdeviceptr>(triangle_x2);
    CUdeviceptr d_triangle_y2 = reinterpret_cast<CUdeviceptr>(triangle_y2);
    uint32_t tc = static_cast<uint32_t>(count);
    void* args[] = {
        &d_triangle_ids,
        &d_triangle_x0,
        &d_triangle_y0,
        &d_triangle_x1,
        &d_triangle_y1,
        &d_triangle_x2,
        &d_triangle_y2,
        &d_triangles.ptr,
        &d_aabbs.ptr,
        &tc,
    };
    const unsigned block = 256;
    const unsigned grid = (tc + block - 1u) / block;
    CU_CHECK(cuLaunchKernel(
        g_partner_triangle2d_pack.fn,
        grid, 1, 1,
        block, 1, 1,
        0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));

    accel = build_custom_accel_from_device_aabbs(get_optix_context(), d_aabbs.ptr, count);
}

PreparedRayAnyHit2D::PreparedRayAnyHit2D(
        const uint32_t* ids,
        const double* x0,
        const double* y0,
        const double* x1,
        const double* y1,
        const double* x2,
        const double* y2,
        const void* aabbs,
        size_t count)
    : triangle_count(count),
      d_triangles(0),
      triangle_columns_zero_copy(true),
      triangle_ids(ids),
      triangle_x0(x0),
      triangle_y0(y0),
      triangle_x1(x1),
      triangle_y1(y1),
      triangle_x2(x2),
      triangle_y2(y2)
{
    if (count == 0) return;
    if (!triangle_ids || !triangle_x0 || !triangle_y0 || !triangle_x1
            || !triangle_y1 || !triangle_x2 || !triangle_y2)
        throw std::runtime_error("partner device triangle column pointers must not be null when triangle_count is nonzero");
    if (!aabbs)
        throw std::runtime_error("partner device triangle AABB buffer must not be null when triangle_count is nonzero");
    if (count > std::numeric_limits<uint32_t>::max())
        throw std::runtime_error("partner device triangle column count exceeds uint32_t launch limit");

    accel = build_custom_accel_from_borrowed_device_aabbs(
        get_optix_context(),
        reinterpret_cast<CUdeviceptr>(aabbs),
        count);
}

static PreparedRayAnyHit2D* prepare_ray_anyhit_2d_optix(
        const RtdlTriangle* triangles, size_t triangle_count)
{
    return new PreparedRayAnyHit2D(triangles, triangle_count);
}

static PreparedRayAnyHit2D* prepare_ray_anyhit_2d_device_triangles_optix(
        const uint32_t* triangle_ids,
        const double* triangle_x0,
        const double* triangle_y0,
        const double* triangle_x1,
        const double* triangle_y1,
        const double* triangle_x2,
        const double* triangle_y2,
        size_t triangle_count)
{
    return new PreparedRayAnyHit2D(
        triangle_ids,
        triangle_x0,
        triangle_y0,
        triangle_x1,
        triangle_y1,
        triangle_x2,
        triangle_y2,
        triangle_count);
}

static PreparedRayAnyHit2D* prepare_ray_anyhit_2d_device_triangle_columns_aabbs_optix(
        const uint32_t* triangle_ids,
        const double* triangle_x0,
        const double* triangle_y0,
        const double* triangle_x1,
        const double* triangle_y1,
        const double* triangle_x2,
        const double* triangle_y2,
        const void* triangle_aabbs,
        size_t triangle_count)
{
    return new PreparedRayAnyHit2D(
        triangle_ids,
        triangle_x0,
        triangle_y0,
        triangle_x1,
        triangle_y1,
        triangle_x2,
        triangle_y2,
        triangle_aabbs,
        triangle_count);
}

static PreparedRays2D* prepare_rays_2d_optix(
        const RtdlRay2D* rays, size_t ray_count)
{
    return new PreparedRays2D(rays, ray_count);
}

static PreparedGroupIndices2D* prepare_group_indices_2d_optix(
        const uint32_t* group_indices, size_t group_index_count)
{
    return new PreparedGroupIndices2D(group_indices, group_index_count);
}

static void count_prepared_ray_anyhit_2d_gpu_optix(
        PreparedRayAnyHit2D* prepared,
        CUdeviceptr d_rays,
        size_t ray_count,
        size_t* hit_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX any-hit handle must not be null");
    if (!hit_count_out) throw std::runtime_error("hit_count_out must not be null");
    *hit_count_out = 0;
    if (ray_count == 0 || prepared->triangle_count == 0) return;

    ensure_ray_anyhit_count_2d_pipeline();

    if (!d_rays) throw std::runtime_error("prepared OptiX ray buffer must not be null when ray_count is nonzero");

    DevPtr d_hit_count(sizeof(uint32_t));
    uint32_t zero = 0u;
    upload(d_hit_count.ptr, &zero, 1);

    RayAnyHitCountLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay*>(d_rays);
    lp.triangles = reinterpret_cast<const GpuTriangle*>(prepared->d_triangles.ptr);
    lp.hit_count = reinterpret_cast<uint32_t*>(d_hit_count.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayAnyHitCountLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit_count.pipe->pipeline, stream,
                            d_params.ptr, sizeof(RayAnyHitCountLaunchParams),
                            &g_rayanyhit_count.pipe->sbt,
                            static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    uint32_t count = 0u;
    download(&count, d_hit_count.ptr, 1);
    *hit_count_out = static_cast<size_t>(count);
}

static void count_prepared_ray_anyhit_2d_optix(
        PreparedRayAnyHit2D* prepared,
        const RtdlRay2D* rays, size_t ray_count,
        size_t* hit_count_out)
{
    if (!rays && ray_count != 0) throw std::runtime_error("rays pointer must not be null when ray_count is nonzero");
    std::vector<GpuRay> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        gpu_rays[i] = {
            static_cast<float>(rays[i].ox),
            static_cast<float>(rays[i].oy),
            static_cast<float>(rays[i].dx),
            static_cast<float>(rays[i].dy),
            static_cast<float>(rays[i].tmax),
            rays[i].id,
        };
    }

    DevPtr d_rays(sizeof(GpuRay) * ray_count);
    upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
    count_prepared_ray_anyhit_2d_gpu_optix(prepared, d_rays.ptr, ray_count, hit_count_out);
}

static void count_prepared_ray_anyhit_2d_packed_optix(
        PreparedRayAnyHit2D* prepared,
        PreparedRays2D* prepared_rays,
        size_t* hit_count_out)
{
    if (!prepared_rays) throw std::runtime_error("prepared OptiX rays handle must not be null");
    count_prepared_ray_anyhit_2d_gpu_optix(
        prepared,
        prepared_rays->d_rays.ptr,
        prepared_rays->ray_count,
        hit_count_out);
}

static void ensure_pack_ray2d_device_columns_kernel()
{
    (void)get_optix_context();
    std::call_once(g_partner_ray2d_pack.init, [&]() {
        const std::string ptx = compile_to_ptx(
            kPackRay2DDeviceColumnsKernelSrc,
            "partner_ray2d_device_columns_pack_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_partner_ray2d_pack.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(
            &g_partner_ray2d_pack.fn,
            g_partner_ray2d_pack.module,
            "pack_ray2d_device_columns"));
    });
}

static void count_prepared_ray_anyhit_2d_device_rays_optix(
        PreparedRayAnyHit2D* prepared,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_tmax,
        size_t ray_count,
        size_t* hit_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX any-hit handle must not be null");
    if (!hit_count_out) throw std::runtime_error("hit_count_out must not be null");
    *hit_count_out = 0;
    if (ray_count == 0 || prepared->triangle_count == 0) return;
    if (!ray_ids || !ray_ox || !ray_oy || !ray_dx || !ray_dy || !ray_tmax)
        throw std::runtime_error("partner device ray column pointers must not be null when ray_count is nonzero");
    if (ray_count > std::numeric_limits<uint32_t>::max())
        throw std::runtime_error("partner device ray column count exceeds uint32_t launch limit");

    DevPtr d_hit_count(sizeof(uint32_t));
    uint32_t zero = 0u;
    upload(d_hit_count.ptr, &zero, 1);

    CUstream stream = 0;
    if (prepared->triangle_columns_zero_copy) {
        ensure_ray_anyhit_count_device_columns_2d_pipeline();
        RayAnyHitCountDeviceColumnsLaunchParams lp;
        lp.traversable = prepared->accel.handle;
        lp.ray_ids = ray_ids;
        lp.ray_ox = ray_ox;
        lp.ray_oy = ray_oy;
        lp.ray_dx = ray_dx;
        lp.ray_dy = ray_dy;
        lp.ray_tmax = ray_tmax;
        lp.triangle_ids = prepared->triangle_ids;
        lp.triangle_x0 = prepared->triangle_x0;
        lp.triangle_y0 = prepared->triangle_y0;
        lp.triangle_x1 = prepared->triangle_x1;
        lp.triangle_y1 = prepared->triangle_y1;
        lp.triangle_x2 = prepared->triangle_x2;
        lp.triangle_y2 = prepared->triangle_y2;
        lp.hit_count = reinterpret_cast<uint32_t*>(d_hit_count.ptr);
        lp.ray_count = static_cast<uint32_t>(ray_count);

        DevPtr d_params(sizeof(RayAnyHitCountDeviceColumnsLaunchParams));
        upload(d_params.ptr, &lp, 1);
        OPTIX_CHECK(optixLaunch(g_rayanyhit_count_device_columns.pipe->pipeline, stream,
                                d_params.ptr, sizeof(RayAnyHitCountDeviceColumnsLaunchParams),
                                &g_rayanyhit_count_device_columns.pipe->sbt,
                                static_cast<unsigned>(ray_count), 1, 1));
    } else {
        ensure_ray_anyhit_count_device_ray_columns_2d_pipeline();
        RayAnyHitCountDeviceRayColumnsLaunchParams lp;
        lp.traversable = prepared->accel.handle;
        lp.ray_ids = ray_ids;
        lp.ray_ox = ray_ox;
        lp.ray_oy = ray_oy;
        lp.ray_dx = ray_dx;
        lp.ray_dy = ray_dy;
        lp.ray_tmax = ray_tmax;
        lp.triangles = reinterpret_cast<const GpuTriangle*>(prepared->d_triangles.ptr);
        lp.hit_count = reinterpret_cast<uint32_t*>(d_hit_count.ptr);
        lp.ray_count = static_cast<uint32_t>(ray_count);

        DevPtr d_params(sizeof(RayAnyHitCountDeviceRayColumnsLaunchParams));
        upload(d_params.ptr, &lp, 1);
        OPTIX_CHECK(optixLaunch(g_rayanyhit_count_device_ray_columns.pipe->pipeline, stream,
                                d_params.ptr, sizeof(RayAnyHitCountDeviceRayColumnsLaunchParams),
                                &g_rayanyhit_count_device_ray_columns.pipe->sbt,
                                static_cast<unsigned>(ray_count), 1, 1));
    }
    CU_CHECK(cuStreamSynchronize(stream));

    uint32_t count = 0u;
    download(&count, d_hit_count.ptr, 1);
    *hit_count_out = static_cast<size_t>(count);
}

static void write_prepared_ray_anyhit_2d_device_flags_optix(
        PreparedRayAnyHit2D* prepared,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_tmax,
        size_t ray_count,
        uint32_t* any_hit_flags_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX any-hit handle must not be null");
    if (!any_hit_flags_out && ray_count != 0)
        throw std::runtime_error("partner device any-hit output pointer must not be null when ray_count is nonzero");
    if (ray_count == 0) return;
    if (!ray_ids || !ray_ox || !ray_oy || !ray_dx || !ray_dy || !ray_tmax)
        throw std::runtime_error("partner device ray column pointers must not be null when ray_count is nonzero");
    if (ray_count > std::numeric_limits<uint32_t>::max())
        throw std::runtime_error("partner device ray column count exceeds uint32_t launch limit");

    CUstream stream = 0;
    if (prepared->triangle_count == 0) {
        CU_CHECK(cuMemsetD32(reinterpret_cast<CUdeviceptr>(any_hit_flags_out), 0u, ray_count));
        CU_CHECK(cuStreamSynchronize(stream));
        return;
    }
    if (!prepared->triangle_columns_zero_copy) {
        throw std::runtime_error(
            "partner device any-hit output currently requires a triangle-column zero-copy prepared scene");
    }

    ensure_ray_anyhit_flags_device_columns_2d_pipeline();

    RayAnyHitFlagsDeviceColumnsLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.ray_ids = ray_ids;
    lp.ray_ox = ray_ox;
    lp.ray_oy = ray_oy;
    lp.ray_dx = ray_dx;
    lp.ray_dy = ray_dy;
    lp.ray_tmax = ray_tmax;
    lp.triangle_ids = prepared->triangle_ids;
    lp.triangle_x0 = prepared->triangle_x0;
    lp.triangle_y0 = prepared->triangle_y0;
    lp.triangle_x1 = prepared->triangle_x1;
    lp.triangle_y1 = prepared->triangle_y1;
    lp.triangle_x2 = prepared->triangle_x2;
    lp.triangle_y2 = prepared->triangle_y2;
    lp.any_hit_flags = any_hit_flags_out;
    lp.ray_count = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayAnyHitFlagsDeviceColumnsLaunchParams));
    upload(d_params.ptr, &lp, 1);
    OPTIX_CHECK(optixLaunch(g_rayanyhit_flags_device_columns.pipe->pipeline, stream,
                            d_params.ptr, sizeof(RayAnyHitFlagsDeviceColumnsLaunchParams),
                            &g_rayanyhit_flags_device_columns.pipe->sbt,
                            static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
}

static void write_prepared_ray_anyhit_2d_device_witnesses_optix(
        PreparedRayAnyHit2D* prepared,
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_tmax,
        size_t ray_count,
        uint32_t* witness_ray_ids_out,
        uint32_t* witness_primitive_ids_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX any-hit handle must not be null");
    if ((!witness_ray_ids_out || !witness_primitive_ids_out) && ray_count != 0)
        throw std::runtime_error("partner device any-hit witness output pointers must not be null when ray_count is nonzero");
    if (ray_count == 0) return;
    if (!ray_ids || !ray_ox || !ray_oy || !ray_dx || !ray_dy || !ray_tmax)
        throw std::runtime_error("partner device ray column pointers must not be null when ray_count is nonzero");
    if (ray_count > std::numeric_limits<uint32_t>::max())
        throw std::runtime_error("partner device ray column count exceeds uint32_t launch limit");

    CUstream stream = 0;
    if (prepared->triangle_count == 0) {
        CU_CHECK(cuMemcpyDtoD(
            reinterpret_cast<CUdeviceptr>(witness_ray_ids_out),
            reinterpret_cast<CUdeviceptr>(ray_ids),
            sizeof(uint32_t) * ray_count));
        CU_CHECK(cuMemsetD32(reinterpret_cast<CUdeviceptr>(witness_primitive_ids_out), 0xFFFFFFFFu, ray_count));
        CU_CHECK(cuStreamSynchronize(stream));
        return;
    }
    if (!prepared->triangle_columns_zero_copy) {
        throw std::runtime_error(
            "partner device any-hit witness output currently requires a triangle-column zero-copy prepared scene");
    }

    ensure_ray_anyhit_witness_device_columns_2d_pipeline();

    RayAnyHitWitnessDeviceColumnsLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.ray_ids = ray_ids;
    lp.ray_ox = ray_ox;
    lp.ray_oy = ray_oy;
    lp.ray_dx = ray_dx;
    lp.ray_dy = ray_dy;
    lp.ray_tmax = ray_tmax;
    lp.triangle_ids = prepared->triangle_ids;
    lp.triangle_x0 = prepared->triangle_x0;
    lp.triangle_y0 = prepared->triangle_y0;
    lp.triangle_x1 = prepared->triangle_x1;
    lp.triangle_y1 = prepared->triangle_y1;
    lp.triangle_x2 = prepared->triangle_x2;
    lp.triangle_y2 = prepared->triangle_y2;
    lp.witness_ray_ids = witness_ray_ids_out;
    lp.witness_primitive_ids = witness_primitive_ids_out;
    lp.ray_count = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayAnyHitWitnessDeviceColumnsLaunchParams));
    upload(d_params.ptr, &lp, 1);
    OPTIX_CHECK(optixLaunch(g_rayanyhit_witness_device_columns.pipe->pipeline, stream,
                            d_params.ptr, sizeof(RayAnyHitWitnessDeviceColumnsLaunchParams),
                            &g_rayanyhit_witness_device_columns.pipe->sbt,
                            static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
}

static void write_prepared_ray_anyhit_2d_device_all_witnesses_optix(
        PreparedRayAnyHit2D* prepared,
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
        uint32_t* overflowed_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX any-hit handle must not be null");
    if (!emitted_count_out || !overflowed_out)
        throw std::runtime_error("partner device all-witness counters must not be null");
    *emitted_count_out = 0;
    *overflowed_out = 0u;
    if ((!witness_ray_ids_out || !witness_primitive_ids_out) && witness_capacity != 0)
        throw std::runtime_error("partner device all-witness output pointers must not be null when witness_capacity is nonzero");
    if (ray_count == 0 || prepared->triangle_count == 0) return;
    if (!ray_ids || !ray_ox || !ray_oy || !ray_dx || !ray_dy || !ray_tmax)
        throw std::runtime_error("partner device ray column pointers must not be null when ray_count is nonzero");
    if (ray_count > std::numeric_limits<uint32_t>::max())
        throw std::runtime_error("partner device ray column count exceeds uint32_t launch limit");
    if (witness_capacity > std::numeric_limits<uint32_t>::max())
        throw std::runtime_error("partner device all-witness capacity exceeds uint32_t launch limit");
    if (!prepared->triangle_columns_zero_copy) {
        throw std::runtime_error(
            "partner device all-witness output currently requires a triangle-column zero-copy prepared scene");
    }

    ensure_ray_anyhit_all_witnesses_device_columns_2d_pipeline();

    CUstream stream = 0;
    DevPtr d_emitted_count(sizeof(uint32_t));
    DevPtr d_overflowed(sizeof(uint32_t));
    CU_CHECK(cuMemsetD32(d_emitted_count.ptr, 0u, 1));
    CU_CHECK(cuMemsetD32(d_overflowed.ptr, 0u, 1));

    RayAnyHitAllWitnessesDeviceColumnsLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.ray_ids = ray_ids;
    lp.ray_ox = ray_ox;
    lp.ray_oy = ray_oy;
    lp.ray_dx = ray_dx;
    lp.ray_dy = ray_dy;
    lp.ray_tmax = ray_tmax;
    lp.triangle_ids = prepared->triangle_ids;
    lp.triangle_x0 = prepared->triangle_x0;
    lp.triangle_y0 = prepared->triangle_y0;
    lp.triangle_x1 = prepared->triangle_x1;
    lp.triangle_y1 = prepared->triangle_y1;
    lp.triangle_x2 = prepared->triangle_x2;
    lp.triangle_y2 = prepared->triangle_y2;
    lp.witness_ray_ids = witness_ray_ids_out;
    lp.witness_primitive_ids = witness_primitive_ids_out;
    lp.emitted_count = reinterpret_cast<uint32_t*>(d_emitted_count.ptr);
    lp.overflowed = reinterpret_cast<uint32_t*>(d_overflowed.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);
    lp.witness_capacity = static_cast<uint32_t>(witness_capacity);

    DevPtr d_params(sizeof(RayAnyHitAllWitnessesDeviceColumnsLaunchParams));
    upload(d_params.ptr, &lp, 1);
    OPTIX_CHECK(optixLaunch(g_rayanyhit_all_witnesses_device_columns.pipe->pipeline, stream,
                            d_params.ptr, sizeof(RayAnyHitAllWitnessesDeviceColumnsLaunchParams),
                            &g_rayanyhit_all_witnesses_device_columns.pipe->sbt,
                            static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    uint32_t emitted_count = 0u;
    uint32_t overflowed = 0u;
    download(&emitted_count, d_emitted_count.ptr, 1);
    download(&overflowed, d_overflowed.ptr, 1);
    *emitted_count_out = static_cast<size_t>(emitted_count);
    *overflowed_out = overflowed != 0u ? 1u : 0u;
}

static void group_flags_prepared_ray_anyhit_2d_packed_optix(
        PreparedRayAnyHit2D* prepared,
        PreparedRays2D* prepared_rays,
        const uint32_t* group_indices,
        size_t group_index_count,
        uint32_t* group_flags_out,
        size_t group_count)
{
    if (!prepared) throw std::runtime_error("prepared OptiX any-hit handle must not be null");
    if (!prepared_rays) throw std::runtime_error("prepared OptiX rays handle must not be null");
    if (!group_flags_out && group_count != 0) throw std::runtime_error("group_flags_out must not be null when group_count is nonzero");
    if (!group_indices && group_index_count != 0) throw std::runtime_error("group_indices must not be null when group_index_count is nonzero");
    if (group_index_count != prepared_rays->ray_count)
        throw std::runtime_error("group_index_count must match prepared ray count");

    for (size_t i = 0; i < group_count; ++i)
        group_flags_out[i] = 0u;
    if (prepared_rays->ray_count == 0 || prepared->triangle_count == 0 || group_count == 0)
        return;

    ensure_ray_anyhit_group_flags_2d_pipeline();

    DevPtr d_group_indices(sizeof(uint32_t) * group_index_count);
    DevPtr d_group_flags(sizeof(uint32_t) * group_count);
    std::vector<uint32_t> zero_flags(group_count, 0u);
    upload(d_group_indices.ptr, group_indices, group_index_count);
    upload(d_group_flags.ptr, zero_flags.data(), zero_flags.size());

    RayAnyHitGroupFlagsLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay*>(prepared_rays->d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle*>(prepared->d_triangles.ptr);
    lp.group_indices = reinterpret_cast<const uint32_t*>(d_group_indices.ptr);
    lp.group_flags = reinterpret_cast<uint32_t*>(d_group_flags.ptr);
    lp.colliding_group_count = nullptr;
    lp.ray_count = static_cast<uint32_t>(prepared_rays->ray_count);
    lp.group_count = static_cast<uint32_t>(group_count);

    DevPtr d_params(sizeof(RayAnyHitGroupFlagsLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit_group_flags.pipe->pipeline, stream,
                            d_params.ptr, sizeof(RayAnyHitGroupFlagsLaunchParams),
                            &g_rayanyhit_group_flags.pipe->sbt,
                            static_cast<unsigned>(prepared_rays->ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    download(group_flags_out, d_group_flags.ptr, group_count);
}

static void group_flags_prepared_ray_anyhit_2d_prepared_indices_optix(
        PreparedRayAnyHit2D* prepared,
        PreparedRays2D* prepared_rays,
        PreparedGroupIndices2D* prepared_group_indices,
        uint32_t* group_flags_out,
        size_t group_count)
{
    if (!prepared) throw std::runtime_error("prepared OptiX any-hit handle must not be null");
    if (!prepared_rays) throw std::runtime_error("prepared OptiX rays handle must not be null");
    if (!prepared_group_indices) throw std::runtime_error("prepared OptiX group-indices handle must not be null");
    if (!group_flags_out && group_count != 0) throw std::runtime_error("group_flags_out must not be null when group_count is nonzero");
    if (prepared_group_indices->count != prepared_rays->ray_count)
        throw std::runtime_error("prepared group-index count must match prepared ray count");

    for (size_t i = 0; i < group_count; ++i)
        group_flags_out[i] = 0u;
    if (prepared_rays->ray_count == 0 || prepared->triangle_count == 0 || group_count == 0)
        return;

    ensure_ray_anyhit_group_flags_2d_pipeline();

    DevPtr d_group_flags(sizeof(uint32_t) * group_count);
    std::vector<uint32_t> zero_flags(group_count, 0u);
    upload(d_group_flags.ptr, zero_flags.data(), zero_flags.size());

    RayAnyHitGroupFlagsLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay*>(prepared_rays->d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle*>(prepared->d_triangles.ptr);
    lp.group_indices = reinterpret_cast<const uint32_t*>(prepared_group_indices->d_group_indices.ptr);
    lp.group_flags = reinterpret_cast<uint32_t*>(d_group_flags.ptr);
    lp.colliding_group_count = nullptr;
    lp.ray_count = static_cast<uint32_t>(prepared_rays->ray_count);
    lp.group_count = static_cast<uint32_t>(group_count);

    DevPtr d_params(sizeof(RayAnyHitGroupFlagsLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit_group_flags.pipe->pipeline, stream,
                            d_params.ptr, sizeof(RayAnyHitGroupFlagsLaunchParams),
                            &g_rayanyhit_group_flags.pipe->sbt,
                            static_cast<unsigned>(prepared_rays->ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    download(group_flags_out, d_group_flags.ptr, group_count);
}

static void count_groups_prepared_ray_anyhit_2d_prepared_indices_optix(
        PreparedRayAnyHit2D* prepared,
        PreparedRays2D* prepared_rays,
        PreparedGroupIndices2D* prepared_group_indices,
        size_t group_count,
        size_t* colliding_group_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX any-hit handle must not be null");
    if (!prepared_rays) throw std::runtime_error("prepared OptiX rays handle must not be null");
    if (!prepared_group_indices) throw std::runtime_error("prepared OptiX group-indices handle must not be null");
    if (!colliding_group_count_out) throw std::runtime_error("colliding_group_count_out must not be null");
    if (prepared_group_indices->count != prepared_rays->ray_count)
        throw std::runtime_error("prepared group-index count must match prepared ray count");
    *colliding_group_count_out = 0;
    if (prepared_rays->ray_count == 0 || prepared->triangle_count == 0 || group_count == 0)
        return;

    ensure_ray_anyhit_group_flags_2d_pipeline();

    DevPtr d_group_flags(sizeof(uint32_t) * group_count);
    DevPtr d_colliding_group_count(sizeof(uint32_t));
    std::vector<uint32_t> zero_flags(group_count, 0u);
    uint32_t zero_count = 0u;
    upload(d_group_flags.ptr, zero_flags.data(), zero_flags.size());
    upload(d_colliding_group_count.ptr, &zero_count, 1);

    RayAnyHitGroupFlagsLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay*>(prepared_rays->d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle*>(prepared->d_triangles.ptr);
    lp.group_indices = reinterpret_cast<const uint32_t*>(prepared_group_indices->d_group_indices.ptr);
    lp.group_flags = reinterpret_cast<uint32_t*>(d_group_flags.ptr);
    lp.colliding_group_count = reinterpret_cast<uint32_t*>(d_colliding_group_count.ptr);
    lp.ray_count = static_cast<uint32_t>(prepared_rays->ray_count);
    lp.group_count = static_cast<uint32_t>(group_count);

    DevPtr d_params(sizeof(RayAnyHitGroupFlagsLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit_group_flags.pipe->pipeline, stream,
                            d_params.ptr, sizeof(RayAnyHitGroupFlagsLaunchParams),
                            &g_rayanyhit_group_flags.pipe->sbt,
                            static_cast<unsigned>(prepared_rays->ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    uint32_t count = 0u;
    download(&count, d_colliding_group_count.ptr, 1);
    *colliding_group_count_out = static_cast<size_t>(count);
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

static std::string ray_anyhit_kernel_source_3d()
{
    std::string src(kRayHitCount3DKernelSrc);
    const std::string old_body =
        "extern \"C\" __global__ void __anyhit__rayhit3d_anyhit() {\n"
        "    // Count this hit and keep traversing all triangles.\n"
        "    uint32_t count = optixGetPayload_1();\n"
        "    optixSetPayload_1(count + 1u);\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    const std::string new_body =
        "extern \"C\" __global__ void __anyhit__rayhit3d_anyhit() {\n"
        "    optixSetPayload_1(1u);\n"
        "    optixTerminateRay();\n"
        "}\n";
    const size_t pos = src.find(old_body);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D any-hit kernel");
    src.replace(pos, old_body.size(), new_body);
    return src;
}

static void run_ray_anyhit_3d_optix(
        const RtdlRay3D*      rays,      size_t ray_count,
        const RtdlTriangle3D* triangles, size_t triangle_count,
        RtdlRayAnyHitRow**  rows_out,  size_t* row_count_out)
{
    std::call_once(g_rayanyhit3d.init, [&]() {
        std::string src = ray_anyhit_kernel_source_3d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit3d_kernel.cu");
        g_rayanyhit3d.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit3d_probe",
            "__miss__rayhit3d_miss",
            "__intersection__rayhit3d_isect",
            "__anyhit__rayhit3d_anyhit",
            nullptr, 2).release();
    });

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

    std::vector<OptixAabb> aabbs(triangle_count);
    for (size_t i = 0; i < triangle_count; ++i) {
        aabbs[i] = aabb_for_triangle_3d(
            gpu_tris[i].x0, gpu_tris[i].y0, gpu_tris[i].z0,
            gpu_tris[i].x1, gpu_tris[i].y1, gpu_tris[i].z1,
            gpu_tris[i].x2, gpu_tris[i].y2, gpu_tris[i].z2);
    }
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    DevPtr d_output(sizeof(GpuRayAnyHitRecord) * ray_count);

    RayHitCount3DLaunchParams lp;
    lp.traversable = accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle3DHost*>(d_tris.ptr);
    lp.output      = reinterpret_cast<GpuRayHitRecord*>(d_output.ptr);
    lp.ray_count   = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayHitCount3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayHitCount3DLaunchParams),
                             &g_rayanyhit3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuRayAnyHitRecord> gpu_rows(ray_count);
    download(gpu_rows.data(), d_output.ptr, ray_count);

    auto* out = static_cast<RtdlRayAnyHitRow*>(
        std::malloc(sizeof(RtdlRayAnyHitRow) * ray_count));
    if (!out && ray_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < ray_count; ++i) {
        out[i].ray_id = gpu_rows[i].ray_id;
        out[i].any_hit = gpu_rows[i].any_hit ? 1u : 0u;
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

struct PreparedSegmentPolygonHitcount2D {
    std::vector<GpuPolygonRef> polygons;
    std::vector<float> vertices_x;
    std::vector<float> vertices_y;
    DevPtr d_polygons;
    DevPtr d_vertices_x;
    DevPtr d_vertices_y;
    AccelHolder accel;

    PreparedSegmentPolygonHitcount2D(
            const RtdlPolygonRef* source_polygons,
            size_t polygon_count,
            const double* vertices_xy,
            size_t vertex_xy_count)
        : polygons(polygon_count),
          vertices_x(vertex_xy_count / 2),
          vertices_y(vertex_xy_count / 2),
          d_polygons(sizeof(GpuPolygonRef) * polygon_count),
          d_vertices_x(sizeof(float) * (vertex_xy_count / 2)),
          d_vertices_y(sizeof(float) * (vertex_xy_count / 2))
    {
        if (vertex_xy_count % 2 != 0) {
            throw std::runtime_error("segment/polygon prepared vertex buffer must contain x/y pairs");
        }
        if (!source_polygons && polygon_count != 0) {
            throw std::runtime_error("polygon pointer must not be null when polygon_count is nonzero");
        }
        if (!vertices_xy && vertex_xy_count != 0) {
            throw std::runtime_error("vertices_xy pointer must not be null when vertex_xy_count is nonzero");
        }
        for (size_t i = 0; i < polygon_count; ++i) {
            polygons[i] = {
                source_polygons[i].id,
                source_polygons[i].vertex_offset,
                source_polygons[i].vertex_count,
            };
        }
        for (size_t i = 0; i < vertices_x.size(); ++i) {
            vertices_x[i] = static_cast<float>(vertices_xy[i * 2]);
            vertices_y[i] = static_cast<float>(vertices_xy[i * 2 + 1]);
        }
        upload(d_polygons.ptr, polygons.data(), polygons.size());
        upload(d_vertices_x.ptr, vertices_x.data(), vertices_x.size());
        upload(d_vertices_y.ptr, vertices_y.data(), vertices_y.size());

        if (!polygons.empty()) {
            std::vector<OptixAabb> aabbs(polygons.size());
            for (size_t i = 0; i < polygons.size(); ++i) {
                aabbs[i] = aabb_for_polygon(vertices_xy, source_polygons[i].vertex_offset, source_polygons[i].vertex_count);
            }
            accel = build_custom_accel(get_optix_context(), aabbs);
        }
    }
};

static PreparedSegmentPolygonHitcount2D* prepare_segment_polygon_hitcount_2d_optix(
        const RtdlPolygonRef* polygons,
        size_t polygon_count,
        const double* vertices_xy,
        size_t vertex_xy_count)
{
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
    return new PreparedSegmentPolygonHitcount2D(polygons, polygon_count, vertices_xy, vertex_xy_count);
}

static void run_prepared_segment_polygon_hitcount_2d_optix(
        PreparedSegmentPolygonHitcount2D* prepared,
        const RtdlSegment* segments,
        size_t segment_count,
        RtdlSegmentPolygonHitCountRow** rows_out,
        size_t* row_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX segment/polygon handle must not be null");
    if (!rows_out || !row_count_out) throw std::runtime_error("output pointers must not be null");
    if (!segments && segment_count != 0) throw std::runtime_error("segments pointer must not be null when segment_count is nonzero");
    if (segment_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("segment count exceeds uint32 launch limit");

    *rows_out = nullptr;
    *row_count_out = 0;
    if (segment_count == 0) {
        return;
    }
    if (prepared->polygons.empty()) {
        auto* out = static_cast<RtdlSegmentPolygonHitCountRow*>(
            std::malloc(sizeof(RtdlSegmentPolygonHitCountRow) * segment_count));
        if (!out && segment_count > 0) throw std::bad_alloc();
        for (size_t i = 0; i < segment_count; ++i) {
            out[i] = {segments[i].id, 0u};
        }
        *rows_out = out;
        *row_count_out = segment_count;
        return;
    }

    std::vector<GpuSegment> gpu_segments(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
        gpu_segments[i] = {
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].x1),
            static_cast<float>(segments[i].y1),
            segments[i].id,
        };
    }

    DevPtr d_segments(sizeof(GpuSegment) * segment_count);
    DevPtr d_output(sizeof(GpuSegPolyRecord) * segment_count);
    upload(d_segments.ptr, gpu_segments.data(), segment_count);

    SegPolyLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.segments = reinterpret_cast<const GpuSegment*>(d_segments.ptr);
    lp.polygons = reinterpret_cast<const GpuPolygonRef*>(prepared->d_polygons.ptr);
    lp.vertices_x = reinterpret_cast<const float*>(prepared->d_vertices_x.ptr);
    lp.vertices_y = reinterpret_cast<const float*>(prepared->d_vertices_y.ptr);
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

static void count_prepared_segment_polygon_hitcount_at_least_2d_optix(
        PreparedSegmentPolygonHitcount2D* prepared,
        const RtdlSegment* segments,
        size_t segment_count,
        uint32_t threshold,
        size_t* count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX segment/polygon handle must not be null");
    if (!count_out) throw std::runtime_error("count_out must not be null");
    if (!segments && segment_count != 0) throw std::runtime_error("segments pointer must not be null when segment_count is nonzero");
    if (segment_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("segment count exceeds uint32 launch limit");

    *count_out = 0;
    if (segment_count == 0) {
        return;
    }
    if (prepared->polygons.empty()) {
        *count_out = threshold == 0 ? segment_count : 0;
        return;
    }

    std::vector<GpuSegment> gpu_segments(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
        gpu_segments[i] = {
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].x1),
            static_cast<float>(segments[i].y1),
            segments[i].id,
        };
    }

    DevPtr d_segments(sizeof(GpuSegment) * segment_count);
    DevPtr d_output(sizeof(GpuSegPolyRecord) * segment_count);
    upload(d_segments.ptr, gpu_segments.data(), segment_count);

    SegPolyLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.segments = reinterpret_cast<const GpuSegment*>(d_segments.ptr);
    lp.polygons = reinterpret_cast<const GpuPolygonRef*>(prepared->d_polygons.ptr);
    lp.vertices_x = reinterpret_cast<const float*>(prepared->d_vertices_x.ptr);
    lp.vertices_y = reinterpret_cast<const float*>(prepared->d_vertices_y.ptr);
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

    size_t count = 0;
    for (const GpuSegPolyRecord& row : gpu_rows) {
        if (row.hit_count >= threshold) {
            ++count;
        }
    }
    *count_out = count;
}

static void aggregate_prepared_segment_polygon_hitcount_2d_optix(
        PreparedSegmentPolygonHitcount2D* prepared,
        const RtdlSegment* segments,
        size_t segment_count,
        uint32_t positive_threshold,
        size_t* row_count_out,
        uint64_t* hit_sum_out,
        size_t* positive_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX segment/polygon handle must not be null");
    if (!row_count_out || !hit_sum_out || !positive_count_out)
        throw std::runtime_error("aggregate output pointers must not be null");
    if (!segments && segment_count != 0) throw std::runtime_error("segments pointer must not be null when segment_count is nonzero");
    if (segment_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("segment count exceeds uint32 launch limit");

    *row_count_out = segment_count;
    *hit_sum_out = 0;
    *positive_count_out = 0;
    if (segment_count == 0) {
        return;
    }
    if (prepared->polygons.empty()) {
        *positive_count_out = positive_threshold == 0 ? segment_count : 0;
        return;
    }

    std::vector<GpuSegment> gpu_segments(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
        gpu_segments[i] = {
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].x1),
            static_cast<float>(segments[i].y1),
            segments[i].id,
        };
    }

    DevPtr d_segments(sizeof(GpuSegment) * segment_count);
    DevPtr d_output(sizeof(GpuSegPolyRecord) * segment_count);
    upload(d_segments.ptr, gpu_segments.data(), segment_count);

    SegPolyLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.segments = reinterpret_cast<const GpuSegment*>(d_segments.ptr);
    lp.polygons = reinterpret_cast<const GpuPolygonRef*>(prepared->d_polygons.ptr);
    lp.vertices_x = reinterpret_cast<const float*>(prepared->d_vertices_x.ptr);
    lp.vertices_y = reinterpret_cast<const float*>(prepared->d_vertices_y.ptr);
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

    uint64_t hit_sum = 0;
    size_t positive_count = 0;
    for (const GpuSegPolyRecord& row : gpu_rows) {
        hit_sum += static_cast<uint64_t>(row.hit_count);
        if (row.hit_count >= positive_threshold) {
            ++positive_count;
        }
    }
    *hit_sum_out = hit_sum;
    *positive_count_out = positive_count;
}

// ---------- Point-nearest-segment (CUDA parallel brute-force) ---------------

static void run_point_nearest_segment_cuda(
        const RtdlPoint*   points,   size_t point_count,
        const RtdlSegment* segments, size_t segment_count,
        RtdlPointNearestSegmentRow** rows_out, size_t* row_count_out)
{
    (void)get_optix_context();
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

static void run_fixed_radius_neighbors_cuda(
        const RtdlPoint* query_points, size_t query_count,
        const RtdlPoint* search_points, size_t search_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out)
{
    (void)get_optix_context();
    std::call_once(g_frn.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusNeighborsKernelSrc, "frn_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_frn.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(&g_frn.fn, g_frn.module, "fixed_radius_neighbors"));
    });

    struct GpuPt { float x, y; uint32_t id, pad; };
    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    constexpr size_t kFixedRadiusSlack = 8;

    std::vector<GpuPt> gpu_queries(query_count);
    std::vector<GpuPt> gpu_search(search_count);
    for (size_t i = 0; i < query_count; ++i)
        gpu_queries[i] = {(float)query_points[i].x, (float)query_points[i].y, query_points[i].id, 0u};
    for (size_t i = 0; i < search_count; ++i)
        gpu_search[i] = {(float)search_points[i].x, (float)search_points[i].y, search_points[i].id, 0u};

    const size_t capped_k_max = std::min(k_max, search_count);
    const size_t candidate_slack = std::min(
        kFixedRadiusSlack,
        search_count > capped_k_max ? search_count - capped_k_max : size_t{0});
    const size_t kernel_k_max = capped_k_max + candidate_slack;
    if (query_count != 0 && kernel_k_max > ((std::numeric_limits<size_t>::max)() / query_count)) {
        throw std::runtime_error("fixed_radius_neighbors output_capacity overflows size_t");
    }
    const size_t output_capacity = query_count * kernel_k_max;
    DevPtr d_queries(sizeof(GpuPt) * query_count);
    DevPtr d_search(sizeof(GpuPt) * search_count);
    DevPtr d_output(sizeof(GpuFrnRecord) * output_capacity);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    upload(d_search.ptr, gpu_search.data(), search_count);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t sc = static_cast<uint32_t>(search_count);
    float radius_f = static_cast<float>(radius + kFixedRadiusCandidateEps);
    uint32_t k_max_u32 = static_cast<uint32_t>(kernel_k_max);
    void* args[] = {
        &d_queries.ptr,
        &qc,
        &d_search.ptr,
        &sc,
        &radius_f,
        &k_max_u32,
        &d_output.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1) / block;
    CU_CHECK(cuLaunchKernel(g_frn.fn, grid, 1, 1, block, 1, 1, 0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));

    std::vector<GpuFrnRecord> gpu_rows(output_capacity);
    download(gpu_rows.data(), d_output.ptr, output_capacity);

    std::unordered_map<uint32_t, const RtdlPoint*> query_by_id;
    std::unordered_map<uint32_t, const RtdlPoint*> search_by_id;
    query_by_id.reserve(query_count);
    search_by_id.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
        query_by_id.emplace(query_points[i].id, query_points + i);
    }
    for (size_t i = 0; i < search_count; ++i) {
        search_by_id.emplace(search_points[i].id, search_points + i);
    }

    std::vector<RtdlFixedRadiusNeighborRow> exact_rows;
    exact_rows.reserve(output_capacity);
    for (size_t i = 0; i < output_capacity; ++i) {
        if (gpu_rows[i].neighbor_id == UINT32_MAX) {
            continue;
        }
        auto query_it = query_by_id.find(gpu_rows[i].query_id);
        auto search_it = search_by_id.find(gpu_rows[i].neighbor_id);
        if (query_it == query_by_id.end() || search_it == search_by_id.end()) {
            continue;
        }
        double dx = search_it->second->x - query_it->second->x;
        double dy = search_it->second->y - query_it->second->y;
        double exact_distance = std::sqrt(dx * dx + dy * dy);
        if (exact_distance <= radius) {
            exact_rows.push_back({
                gpu_rows[i].query_id,
                gpu_rows[i].neighbor_id,
                exact_distance,
            });
        }
    }

    std::stable_sort(exact_rows.begin(), exact_rows.end(), [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
        if (left.query_id != right.query_id) {
            return left.query_id < right.query_id;
        }
        if (left.distance < right.distance - 1.0e-12) {
            return true;
        }
        if (right.distance < left.distance - 1.0e-12) {
            return false;
        }
        return left.neighbor_id < right.neighbor_id;
    });

    std::vector<RtdlFixedRadiusNeighborRow> rows;
    rows.reserve(exact_rows.size());
    uint32_t current_query_id = 0;
    size_t current_count = 0;
    bool have_query = false;
    for (const auto& row : exact_rows) {
        if (!have_query || row.query_id != current_query_id) {
            current_query_id = row.query_id;
            current_count = 0;
            have_query = true;
        }
        if (current_count >= k_max) {
            continue;
        }
        rows.push_back(row);
        current_count += 1;
    }

    auto* out = static_cast<RtdlFixedRadiusNeighborRow*>(
        std::malloc(sizeof(RtdlFixedRadiusNeighborRow) * rows.size()));
    if (!out && !rows.empty()) throw std::bad_alloc();
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlFixedRadiusNeighborRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

struct FixedRadiusCountRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    const uint32_t* query_ids;
    const double* query_x;
    const double* query_y;
    const uint32_t* search_ids;
    const double* search_x;
    const double* search_y;
    GpuFixedRadiusCountRecord* output;
    uint32_t* query_ids_out;
    uint32_t* neighbor_counts_out;
    uint32_t* threshold_flags_out;
    uint32_t* threshold_reached_count;
    uint32_t query_count;
    uint32_t threshold;
    uint32_t use_device_columns;
    float radius;
    float trace_tmax;
};

struct FixedRadiusCountHostRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    GpuFixedRadiusCountRecord* output;
    uint32_t* threshold_reached_count;
    uint32_t query_count;
    uint32_t threshold;
    float radius;
    float trace_tmax;
};

struct GpuFixedRadiusNearestRecord { uint32_t query_id, neighbor_id; float distance; };

struct FixedRadiusNearestRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    GpuFixedRadiusNearestRecord* output;
    uint32_t query_count;
    float radius;
    float trace_tmax;
};

struct GpuPointGroupBounds {
    float min_x, min_y, max_x, max_y;
    uint32_t id, point_offset, point_count, pad;
};

struct PointGroupThresholdRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    const GpuPointGroupBounds* groups;
    uint32_t* threshold_reached_count;
    uint32_t* threshold_flags;
    uint32_t query_count;
    uint32_t threshold;
    float radius;
    float trace_tmax;
};

struct PointGroupNearestRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* query_points;
    const GpuPoint* search_points;
    const GpuPointGroupBounds* groups;
    GpuFixedRadiusNearestRecord* output;
    uint32_t query_count;
    float radius;
    float trace_tmax;
};

thread_local double g_optix_last_bvh_build_s = 0.0;
thread_local double g_optix_last_traversal_s = 0.0;
thread_local double g_optix_last_copy_s = 0.0;

extern "C" int rtdl_optix_get_last_phase_timings(double* bvh, double* trav, double* copy) {
    if (bvh) *bvh = g_optix_last_bvh_build_s;
    if (trav) *trav = g_optix_last_traversal_s;
    if (copy) *copy = g_optix_last_copy_s;
    return 0;
}

static void run_fixed_radius_count_threshold_rt(
        const RtdlPoint* query_points, size_t query_count,
        const RtdlPoint* search_points, size_t search_count,
        double radius,
        size_t threshold,
        RtdlFixedRadiusCountRow** rows_out, size_t* row_count_out)
{
    std::call_once(g_frn_count_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusCountRtKernelSrc, "frn_count_rt_kernel.cu");
        g_frn_count_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__frn_count_probe",
            "__miss__frn_count_miss",
            "__intersection__frn_count_isect",
            "__anyhit__frn_count_anyhit",
            nullptr, 3).release();
    });

    // Pad only the BVH broad phase; the intersection program still tests the
    // unpadded radius so this can add candidates but not accepted hits.
    constexpr float kRadiusPad = 1.0e-4f;
    const float radius_f = static_cast<float>(radius);
    const float aabb_radius = radius_f + kRadiusPad;

    std::vector<GpuPoint> gpu_queries(query_count);
    std::vector<GpuPoint> gpu_search(search_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {static_cast<float>(query_points[i].x), static_cast<float>(query_points[i].y), query_points[i].id};
    }
    for (size_t i = 0; i < search_count; ++i) {
        gpu_search[i] = {static_cast<float>(search_points[i].x), static_cast<float>(search_points[i].y), search_points[i].id};
    }

    DevPtr d_queries(sizeof(GpuPoint) * query_count);
    DevPtr d_search(sizeof(GpuPoint) * search_count);
    DevPtr d_output(sizeof(GpuFixedRadiusCountRecord) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    upload(d_search.ptr, gpu_search.data(), search_count);

    std::vector<OptixAabb> aabbs(search_count);
    for (size_t i = 0; i < search_count; ++i) {
        const float x = gpu_search[i].x;
        const float y = gpu_search[i].y;
        OptixAabb aabb;
        aabb.minX = x - aabb_radius;
        aabb.minY = y - aabb_radius;
        aabb.minZ = -aabb_radius;
        aabb.maxX = x + aabb_radius;
        aabb.maxY = y + aabb_radius;
        aabb.maxZ = aabb_radius;
        aabbs[i] = aabb;
    }
    auto t_start_bvh = std::chrono::steady_clock::now();
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);
    auto t_end_bvh = std::chrono::steady_clock::now();
    g_optix_last_bvh_build_s = std::chrono::duration<double>(t_end_bvh - t_start_bvh).count();

    FixedRadiusCountRtLaunchParams lp;
    lp.traversable = accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint*>(d_search.ptr);
    lp.query_ids = nullptr;
    lp.query_x = nullptr;
    lp.query_y = nullptr;
    lp.search_ids = nullptr;
    lp.search_x = nullptr;
    lp.search_y = nullptr;
    lp.output = reinterpret_cast<GpuFixedRadiusCountRecord*>(d_output.ptr);
    lp.query_ids_out = nullptr;
    lp.neighbor_counts_out = nullptr;
    lp.threshold_flags_out = nullptr;
    lp.threshold_reached_count = nullptr;
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.threshold = static_cast<uint32_t>(threshold);
    lp.use_device_columns = 0u;
    lp.radius = radius_f;
    lp.trace_tmax = 2.0f * aabb_radius;

    DevPtr d_params(sizeof(FixedRadiusCountRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn_count_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusCountRtLaunchParams),
                             &g_frn_count_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    std::vector<GpuFixedRadiusCountRecord> gpu_rows(query_count);
    download(gpu_rows.data(), d_output.ptr, query_count);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();

    auto* out = static_cast<RtdlFixedRadiusCountRow*>(
        std::malloc(sizeof(RtdlFixedRadiusCountRow) * query_count));
    if (!out && query_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < query_count; ++i) {
        out[i].query_id = gpu_rows[i].query_id;
        out[i].neighbor_count = gpu_rows[i].neighbor_count;
        out[i].threshold_reached = gpu_rows[i].threshold_reached ? 1u : 0u;
    }
    *rows_out = out;
    *row_count_out = query_count;
}

static void ensure_pack_point2d_fixed_radius_aabbs_kernel();

struct PreparedFixedRadiusCountThreshold2D {
    std::vector<GpuPoint> search_points;
    DevPtr d_search;
    AccelHolder accel;
    float max_radius = 0.0f;
    bool search_columns_zero_copy = false;
    const uint32_t* search_ids = nullptr;
    const double* search_x = nullptr;
    const double* search_y = nullptr;

    PreparedFixedRadiusCountThreshold2D(
            const RtdlPoint* source,
            size_t count,
            double radius_bound)
        : search_points(count),
          d_search(sizeof(GpuPoint) * count),
          max_radius(static_cast<float>(radius_bound))
    {
        for (size_t i = 0; i < count; ++i) {
            search_points[i] = {
                static_cast<float>(source[i].x),
                static_cast<float>(source[i].y),
                source[i].id
            };
        }
        upload(d_search.ptr, search_points.data(), search_points.size());

        if (!search_points.empty()) {
            constexpr float kRadiusPad = 1.0e-4f;
            const float aabb_radius = max_radius + kRadiusPad;
            std::vector<OptixAabb> aabbs(search_points.size());
            for (size_t i = 0; i < search_points.size(); ++i) {
                const float x = search_points[i].x;
                const float y = search_points[i].y;
                OptixAabb aabb;
                aabb.minX = x - aabb_radius;
                aabb.minY = y - aabb_radius;
                aabb.minZ = -aabb_radius;
                aabb.maxX = x + aabb_radius;
                aabb.maxY = y + aabb_radius;
                aabb.maxZ = aabb_radius;
                aabbs[i] = aabb;
            }
            auto t_start_bvh = std::chrono::steady_clock::now();
            accel = build_custom_accel(get_optix_context(), aabbs);
            auto t_end_bvh = std::chrono::steady_clock::now();
            g_optix_last_bvh_build_s = std::chrono::duration<double>(t_end_bvh - t_start_bvh).count();
            g_optix_last_traversal_s = 0.0;
            g_optix_last_copy_s = 0.0;
        }
    }

    PreparedFixedRadiusCountThreshold2D(
            const uint32_t* ids,
            const double* x,
            const double* y,
            size_t count,
            double radius_bound)
        : search_points(),
          d_search(0),
          max_radius(static_cast<float>(radius_bound)),
          search_columns_zero_copy(true),
          search_ids(ids),
          search_x(x),
          search_y(y)
    {
        if (count == 0) return;
        if (!search_ids || !search_x || !search_y)
            throw std::runtime_error("partner device fixed-radius search column pointers must not be null when search_count is nonzero");
        if (count > std::numeric_limits<uint32_t>::max())
            throw std::runtime_error("partner device fixed-radius search column count exceeds uint32_t launch limit");

        ensure_pack_point2d_fixed_radius_aabbs_kernel();

        constexpr float kRadiusPad = 1.0e-4f;
        float aabb_radius = max_radius + kRadiusPad;
        DevPtr d_aabbs(sizeof(OptixAabb) * count);
        CUdeviceptr d_x = reinterpret_cast<CUdeviceptr>(search_x);
        CUdeviceptr d_y = reinterpret_cast<CUdeviceptr>(search_y);
        uint32_t point_count = static_cast<uint32_t>(count);
        void* args[] = {
            &d_x,
            &d_y,
            &d_aabbs.ptr,
            &point_count,
            &aabb_radius,
        };
        const unsigned block = 256;
        const unsigned grid = (point_count + block - 1u) / block;
        CU_CHECK(cuLaunchKernel(
            g_partner_point2d_aabb_pack.fn,
            grid, 1, 1,
            block, 1, 1,
            0, nullptr, args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));

        auto t_start_bvh = std::chrono::steady_clock::now();
        accel = build_custom_accel_from_device_aabbs(get_optix_context(), d_aabbs.ptr, count);
        auto t_end_bvh = std::chrono::steady_clock::now();
        g_optix_last_bvh_build_s = std::chrono::duration<double>(t_end_bvh - t_start_bvh).count();
        g_optix_last_traversal_s = 0.0;
        g_optix_last_copy_s = 0.0;
    }
};

struct PreparedPointGroupNearestWitness2D {
    std::vector<GpuPoint> search_points;
    std::vector<GpuPointGroupBounds> groups;
    DevPtr d_search;
    DevPtr d_groups;
    AccelHolder accel;
    float max_radius = 0.0f;

    PreparedPointGroupNearestWitness2D(
            const RtdlPoint* source,
            size_t source_count,
            const RtdlPointGroupBounds2D* source_groups,
            size_t source_group_count,
            double radius_bound)
        : search_points(source_count),
          groups(source_group_count),
          d_search(sizeof(GpuPoint) * source_count),
          d_groups(sizeof(GpuPointGroupBounds) * source_group_count),
          max_radius(static_cast<float>(radius_bound))
    {
        if (source_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("point_group_nearest_witness search_count exceeds uint32 limit");
        if (source_group_count > static_cast<size_t>(UINT32_MAX))
            throw std::runtime_error("point_group_nearest_witness group_count exceeds uint32 limit");
        for (size_t i = 0; i < source_count; ++i) {
            search_points[i] = {
                static_cast<float>(source[i].x),
                static_cast<float>(source[i].y),
                source[i].id
            };
        }
        for (size_t i = 0; i < source_group_count; ++i) {
            const RtdlPointGroupBounds2D& group = source_groups[i];
            const size_t offset = static_cast<size_t>(group.point_offset);
            const size_t count = static_cast<size_t>(group.point_count);
            if (offset > source_count || count > source_count - offset)
                throw std::runtime_error("point_group_nearest_witness group span exceeds search point count");
            if (group.max_x < group.min_x || group.max_y < group.min_y)
                throw std::runtime_error("point_group_nearest_witness group bounds must be ordered");
            groups[i] = {
                static_cast<float>(group.min_x),
                static_cast<float>(group.min_y),
                static_cast<float>(group.max_x),
                static_cast<float>(group.max_y),
                group.id,
                group.point_offset,
                group.point_count,
                0u
            };
        }
        upload(d_search.ptr, search_points.data(), search_points.size());
        upload(d_groups.ptr, groups.data(), groups.size());

        if (!groups.empty()) {
            constexpr float kRadiusPad = 1.0e-4f;
            const float aabb_radius = max_radius + kRadiusPad;
            std::vector<OptixAabb> aabbs(groups.size());
            for (size_t i = 0; i < groups.size(); ++i) {
                const GpuPointGroupBounds& group = groups[i];
                OptixAabb aabb;
                aabb.minX = group.min_x - aabb_radius;
                aabb.minY = group.min_y - aabb_radius;
                aabb.minZ = -aabb_radius;
                aabb.maxX = group.max_x + aabb_radius;
                aabb.maxY = group.max_y + aabb_radius;
                aabb.maxZ = aabb_radius;
                aabbs[i] = aabb;
            }
            auto t_start_bvh = std::chrono::steady_clock::now();
            accel = build_custom_accel(get_optix_context(), aabbs);
            auto t_end_bvh = std::chrono::steady_clock::now();
            g_optix_last_bvh_build_s = std::chrono::duration<double>(t_end_bvh - t_start_bvh).count();
            g_optix_last_traversal_s = 0.0;
            g_optix_last_copy_s = 0.0;
        }
    }
};

static void ensure_pack_point2d_fixed_radius_aabbs_kernel()
{
    (void)get_optix_context();
    std::call_once(g_partner_point2d_aabb_pack.init, [&]() {
        const std::string ptx = compile_to_ptx(
            kPackPoint2DDeviceAabbsKernelSrc,
            "partner_point2d_fixed_radius_aabb_pack_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_partner_point2d_aabb_pack.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(
            &g_partner_point2d_aabb_pack.fn,
            g_partner_point2d_aabb_pack.module,
            "pack_point2d_fixed_radius_aabbs"));
    });
}

static PreparedFixedRadiusCountThreshold2D* prepare_fixed_radius_count_threshold_2d_optix(
        const RtdlPoint* search_points,
        size_t search_count,
        double max_radius)
{
    std::call_once(g_frn_count_host_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusCountHostRtKernelSrc, "frn_count_host_rt_kernel.cu");
        g_frn_count_host_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__frn_count_host_probe",
            "__miss__frn_count_host_miss",
            "__intersection__frn_count_host_isect",
            "__anyhit__frn_count_host_anyhit",
            nullptr, 3).release();
    });
    return new PreparedFixedRadiusCountThreshold2D(search_points, search_count, max_radius);
}

static PreparedFixedRadiusCountThreshold2D* prepare_fixed_radius_count_threshold_2d_device_search_columns_optix(
        const uint32_t* search_ids,
        const double* search_x,
        const double* search_y,
        size_t search_count,
        double max_radius)
{
    std::call_once(g_frn_count_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusCountRtKernelSrc, "frn_count_rt_kernel.cu");
        g_frn_count_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__frn_count_probe",
            "__miss__frn_count_miss",
            "__intersection__frn_count_isect",
            "__anyhit__frn_count_anyhit",
            nullptr, 3).release();
    });
    return new PreparedFixedRadiusCountThreshold2D(search_ids, search_x, search_y, search_count, max_radius);
}

static void run_prepared_fixed_radius_count_threshold_2d_optix(
        PreparedFixedRadiusCountThreshold2D* prepared,
        const RtdlPoint* query_points,
        size_t query_count,
        double radius,
        size_t threshold,
        RtdlFixedRadiusCountRow** rows_out,
        size_t* row_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius handle must not be null");
    if (!rows_out || !row_count_out) throw std::runtime_error("output pointers must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_count_threshold radius must be non-negative");
    if (radius > static_cast<double>(prepared->max_radius) + 1.0e-7)
        throw std::runtime_error("fixed_radius_count_threshold radius exceeds prepared max_radius");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_count_threshold query_count exceeds uint32 limit");
    if (threshold > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_count_threshold threshold exceeds uint32 limit");

    *rows_out = nullptr;
    *row_count_out = 0;
    if (query_count == 0 || prepared->search_points.empty()) return;

    std::vector<GpuPoint> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            query_points[i].id
        };
    }

    DevPtr d_queries(sizeof(GpuPoint) * query_count);
    DevPtr d_output(sizeof(GpuFixedRadiusCountRecord) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);

    FixedRadiusCountHostRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint*>(prepared->d_search.ptr);
    lp.output = reinterpret_cast<GpuFixedRadiusCountRecord*>(d_output.ptr);
    lp.threshold_reached_count = nullptr;
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.threshold = static_cast<uint32_t>(threshold);
    lp.radius = static_cast<float>(radius);
    lp.trace_tmax = 2.0f * (prepared->max_radius + 1.0e-4f);

    DevPtr d_params(sizeof(FixedRadiusCountHostRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn_count_host_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusCountHostRtLaunchParams),
                             &g_frn_count_host_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    std::vector<GpuFixedRadiusCountRecord> gpu_rows(query_count);
    download(gpu_rows.data(), d_output.ptr, query_count);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();

    auto* out = static_cast<RtdlFixedRadiusCountRow*>(
        std::malloc(sizeof(RtdlFixedRadiusCountRow) * query_count));
    if (!out && query_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < query_count; ++i) {
        out[i].query_id = gpu_rows[i].query_id;
        out[i].neighbor_count = gpu_rows[i].neighbor_count;
        out[i].threshold_reached = gpu_rows[i].threshold_reached ? 1u : 0u;
    }
    *rows_out = out;
    *row_count_out = query_count;
}

static void write_prepared_fixed_radius_count_threshold_2d_device_query_columns_optix(
        PreparedFixedRadiusCountThreshold2D* prepared,
        const uint32_t* query_ids,
        const double* query_x,
        const double* query_y,
        size_t query_count,
        double radius,
        size_t threshold,
        uint32_t* query_ids_out,
        uint32_t* neighbor_counts_out,
        uint32_t* threshold_flags_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius handle must not be null");
    if (!prepared->search_columns_zero_copy)
        throw std::runtime_error("fixed-radius device-column output requires a device-search-column prepared scene");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_count_threshold radius must be non-negative");
    if (radius > static_cast<double>(prepared->max_radius) + 1.0e-7)
        throw std::runtime_error("fixed_radius_count_threshold radius exceeds prepared max_radius");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_count_threshold query_count exceeds uint32 limit");
    if (threshold > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_count_threshold threshold exceeds uint32 limit");
    if (query_count == 0) return;
    if (!query_ids || !query_x || !query_y)
        throw std::runtime_error("partner device fixed-radius query column pointers must not be null when query_count is nonzero");
    if (!query_ids_out || !neighbor_counts_out || !threshold_flags_out)
        throw std::runtime_error("partner device fixed-radius output column pointers must not be null when query_count is nonzero");
    if (!prepared->accel.handle) {
        CUstream stream = 0;
        CU_CHECK(cuMemcpyDtoD(
            reinterpret_cast<CUdeviceptr>(query_ids_out),
            reinterpret_cast<CUdeviceptr>(query_ids),
            sizeof(uint32_t) * query_count));
        CU_CHECK(cuMemsetD32(reinterpret_cast<CUdeviceptr>(neighbor_counts_out), 0u, query_count));
        CU_CHECK(cuMemsetD32(reinterpret_cast<CUdeviceptr>(threshold_flags_out), threshold == 0 ? 1u : 0u, query_count));
        CU_CHECK(cuStreamSynchronize(stream));
        return;
    }

    FixedRadiusCountRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = nullptr;
    lp.search_points = nullptr;
    lp.query_ids = query_ids;
    lp.query_x = query_x;
    lp.query_y = query_y;
    lp.search_ids = prepared->search_ids;
    lp.search_x = prepared->search_x;
    lp.search_y = prepared->search_y;
    lp.output = nullptr;
    lp.query_ids_out = query_ids_out;
    lp.neighbor_counts_out = neighbor_counts_out;
    lp.threshold_flags_out = threshold_flags_out;
    lp.threshold_reached_count = nullptr;
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.threshold = static_cast<uint32_t>(threshold);
    lp.use_device_columns = 1u;
    lp.radius = static_cast<float>(radius);
    lp.trace_tmax = 2.0f * (prepared->max_radius + 1.0e-4f);

    DevPtr d_params(sizeof(FixedRadiusCountRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn_count_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusCountRtLaunchParams),
                             &g_frn_count_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();
    g_optix_last_copy_s = 0.0;
}

static void count_prepared_fixed_radius_threshold_reached_2d_optix(
        PreparedFixedRadiusCountThreshold2D* prepared,
        const RtdlPoint* query_points,
        size_t query_count,
        double radius,
        size_t threshold,
        size_t* threshold_reached_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius handle must not be null");
    if (!threshold_reached_count_out) throw std::runtime_error("threshold_reached_count_out must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_count_threshold radius must be non-negative");
    if (radius > static_cast<double>(prepared->max_radius) + 1.0e-7)
        throw std::runtime_error("fixed_radius_count_threshold radius exceeds prepared max_radius");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_count_threshold query_count exceeds uint32 limit");
    if (threshold > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_count_threshold threshold exceeds uint32 limit");

    *threshold_reached_count_out = 0;
    if (query_count == 0 || prepared->search_points.empty()) return;

    std::vector<GpuPoint> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            query_points[i].id
        };
    }

    DevPtr d_queries(sizeof(GpuPoint) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    DevPtr d_threshold_reached_count(sizeof(uint32_t));
    uint32_t zero = 0;
    upload(d_threshold_reached_count.ptr, &zero, 1);

    FixedRadiusCountHostRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint*>(prepared->d_search.ptr);
    lp.output = nullptr;
    lp.threshold_reached_count = reinterpret_cast<uint32_t*>(d_threshold_reached_count.ptr);
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.threshold = static_cast<uint32_t>(threshold);
    lp.radius = static_cast<float>(radius);
    lp.trace_tmax = 2.0f * (prepared->max_radius + 1.0e-4f);

    DevPtr d_params(sizeof(FixedRadiusCountHostRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn_count_host_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusCountHostRtLaunchParams),
                             &g_frn_count_host_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    uint32_t threshold_reached_count = 0;
    download(&threshold_reached_count, d_threshold_reached_count.ptr, 1);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();
    *threshold_reached_count_out = static_cast<size_t>(threshold_reached_count);
}

static void run_prepared_fixed_radius_nearest_witness_2d_optix(
        PreparedFixedRadiusCountThreshold2D* prepared,
        const RtdlPoint* query_points,
        size_t query_count,
        double radius,
        RtdlFixedRadiusNeighborRow** rows_out,
        size_t* row_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius handle must not be null");
    if (!rows_out || !row_count_out) throw std::runtime_error("output pointers must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_nearest_witness radius must be non-negative");
    if (radius > static_cast<double>(prepared->max_radius) + 1.0e-7)
        throw std::runtime_error("fixed_radius_nearest_witness radius exceeds prepared max_radius");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_nearest_witness query_count exceeds uint32 limit");

    *rows_out = nullptr;
    *row_count_out = 0;
    if (query_count == 0 || prepared->search_points.empty()) return;

    std::call_once(g_frn_nearest_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusNearestRtKernelSrc, "frn_nearest_rt_kernel.cu");
        g_frn_nearest_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__frn_nearest_probe",
            "__miss__frn_nearest_miss",
            "__intersection__frn_nearest_isect",
            "__anyhit__frn_nearest_anyhit",
            nullptr, 4).release();
    });

    std::vector<GpuPoint> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            query_points[i].id
        };
    }

    DevPtr d_queries(sizeof(GpuPoint) * query_count);
    DevPtr d_output(sizeof(GpuFixedRadiusNearestRecord) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);

    FixedRadiusNearestRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint*>(prepared->d_search.ptr);
    lp.output = reinterpret_cast<GpuFixedRadiusNearestRecord*>(d_output.ptr);
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.radius = static_cast<float>(radius);
    lp.trace_tmax = 2.0f * (prepared->max_radius + 1.0e-4f);

    DevPtr d_params(sizeof(FixedRadiusNearestRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn_nearest_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusNearestRtLaunchParams),
                             &g_frn_nearest_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    std::vector<GpuFixedRadiusNearestRecord> gpu_rows(query_count);
    download(gpu_rows.data(), d_output.ptr, query_count);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();

    auto* out = static_cast<RtdlFixedRadiusNeighborRow*>(
        std::malloc(sizeof(RtdlFixedRadiusNeighborRow) * query_count));
    if (!out && query_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < query_count; ++i) {
        out[i].query_id = gpu_rows[i].query_id;
        out[i].neighbor_id = gpu_rows[i].neighbor_id;
        out[i].distance = static_cast<double>(gpu_rows[i].distance);
    }
    *rows_out = out;
    *row_count_out = query_count;
}

static PreparedPointGroupNearestWitness2D* prepare_point_group_nearest_witness_2d_optix(
        const RtdlPoint* search_points,
        size_t search_count,
        const RtdlPointGroupBounds2D* groups,
        size_t group_count,
        double max_radius)
{
    return new PreparedPointGroupNearestWitness2D(
        search_points, search_count, groups, group_count, max_radius);
}

static void count_prepared_point_group_threshold_reached_2d_optix(
        PreparedPointGroupNearestWitness2D* prepared,
        const RtdlPoint* query_points,
        size_t query_count,
        double radius,
        size_t threshold,
        size_t* threshold_reached_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX point-group handle must not be null");
    if (!threshold_reached_count_out) throw std::runtime_error("threshold_reached_count_out must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("point_group_threshold radius must be non-negative");
    if (radius > static_cast<double>(prepared->max_radius) + 1.0e-7)
        throw std::runtime_error("point_group_threshold radius exceeds prepared max_radius");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("point_group_threshold query_count exceeds uint32 limit");
    if (threshold > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("point_group_threshold threshold exceeds uint32 limit");

    *threshold_reached_count_out = 0;
    if (query_count == 0 || prepared->groups.empty()) return;

    std::call_once(g_point_group_threshold_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kPointGroupThresholdRtKernelSrc, "point_group_threshold_rt_kernel.cu");
        g_point_group_threshold_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__point_group_threshold_probe",
            "__miss__point_group_threshold_miss",
            "__intersection__point_group_threshold_isect",
            "__anyhit__point_group_threshold_anyhit",
            nullptr, 3).release();
    });

    std::vector<GpuPoint> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            query_points[i].id
        };
    }

    DevPtr d_queries(sizeof(GpuPoint) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    DevPtr d_threshold_reached_count(sizeof(uint32_t));
    uint32_t zero = 0;
    upload(d_threshold_reached_count.ptr, &zero, 1);

    PointGroupThresholdRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint*>(prepared->d_search.ptr);
    lp.groups = reinterpret_cast<const GpuPointGroupBounds*>(prepared->d_groups.ptr);
    lp.threshold_reached_count = reinterpret_cast<uint32_t*>(d_threshold_reached_count.ptr);
    lp.threshold_flags = nullptr;
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.threshold = static_cast<uint32_t>(threshold);
    lp.radius = static_cast<float>(radius);
    lp.trace_tmax = 2.0f * (prepared->max_radius + 1.0e-4f);

    DevPtr d_params(sizeof(PointGroupThresholdRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_point_group_threshold_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(PointGroupThresholdRtLaunchParams),
                             &g_point_group_threshold_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    uint32_t threshold_reached_count = 0;
    download(&threshold_reached_count, d_threshold_reached_count.ptr, 1);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();
    *threshold_reached_count_out = static_cast<size_t>(threshold_reached_count);
}

static void write_prepared_point_group_threshold_flags_2d_optix(
        PreparedPointGroupNearestWitness2D* prepared,
        const RtdlPoint* query_points,
        size_t query_count,
        double radius,
        size_t threshold,
        uint32_t* threshold_flags_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX point-group handle must not be null");
    if (!threshold_flags_out && query_count != 0) throw std::runtime_error("threshold_flags_out must not be null when query_count is nonzero");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("point_group_threshold_flags radius must be non-negative");
    if (radius > static_cast<double>(prepared->max_radius) + 1.0e-7)
        throw std::runtime_error("point_group_threshold_flags radius exceeds prepared max_radius");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("point_group_threshold_flags query_count exceeds uint32 limit");
    if (threshold > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("point_group_threshold_flags threshold exceeds uint32 limit");

    if (query_count == 0) return;
    if (prepared->groups.empty()) {
        const uint32_t value = threshold == 0 ? 1u : 0u;
        for (size_t i = 0; i < query_count; ++i) threshold_flags_out[i] = value;
        g_optix_last_bvh_build_s = 0.0;
        g_optix_last_traversal_s = 0.0;
        g_optix_last_copy_s = 0.0;
        return;
    }

    std::call_once(g_point_group_threshold_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kPointGroupThresholdRtKernelSrc, "point_group_threshold_rt_kernel.cu");
        g_point_group_threshold_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__point_group_threshold_probe",
            "__miss__point_group_threshold_miss",
            "__intersection__point_group_threshold_isect",
            "__anyhit__point_group_threshold_anyhit",
            nullptr, 3).release();
    });

    std::vector<GpuPoint> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            query_points[i].id
        };
    }

    DevPtr d_queries(sizeof(GpuPoint) * query_count);
    DevPtr d_threshold_flags(sizeof(uint32_t) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);

    PointGroupThresholdRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint*>(prepared->d_search.ptr);
    lp.groups = reinterpret_cast<const GpuPointGroupBounds*>(prepared->d_groups.ptr);
    lp.threshold_reached_count = nullptr;
    lp.threshold_flags = reinterpret_cast<uint32_t*>(d_threshold_flags.ptr);
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.threshold = static_cast<uint32_t>(threshold);
    lp.radius = static_cast<float>(radius);
    lp.trace_tmax = 2.0f * (prepared->max_radius + 1.0e-4f);

    DevPtr d_params(sizeof(PointGroupThresholdRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_point_group_threshold_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(PointGroupThresholdRtLaunchParams),
                             &g_point_group_threshold_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    download(threshold_flags_out, d_threshold_flags.ptr, query_count);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();
}

static void run_prepared_point_group_nearest_witness_2d_optix(
        PreparedPointGroupNearestWitness2D* prepared,
        const RtdlPoint* query_points,
        size_t query_count,
        double radius,
        RtdlFixedRadiusNeighborRow** rows_out,
        size_t* row_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX point-group handle must not be null");
    if (!rows_out || !row_count_out) throw std::runtime_error("output pointers must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("point_group_nearest_witness radius must be non-negative");
    if (radius > static_cast<double>(prepared->max_radius) + 1.0e-7)
        throw std::runtime_error("point_group_nearest_witness radius exceeds prepared max_radius");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("point_group_nearest_witness query_count exceeds uint32 limit");

    *rows_out = nullptr;
    *row_count_out = 0;
    if (query_count == 0 || prepared->groups.empty()) return;

    std::call_once(g_point_group_nearest_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kPointGroupNearestRtKernelSrc, "point_group_nearest_rt_kernel.cu");
        g_point_group_nearest_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__point_group_nearest_probe",
            "__miss__point_group_nearest_miss",
            "__intersection__point_group_nearest_isect",
            "__anyhit__point_group_nearest_anyhit",
            nullptr, 4).release();
    });

    std::vector<GpuPoint> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            query_points[i].id
        };
    }

    DevPtr d_queries(sizeof(GpuPoint) * query_count);
    DevPtr d_output(sizeof(GpuFixedRadiusNearestRecord) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);

    PointGroupNearestRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint*>(prepared->d_search.ptr);
    lp.groups = reinterpret_cast<const GpuPointGroupBounds*>(prepared->d_groups.ptr);
    lp.output = reinterpret_cast<GpuFixedRadiusNearestRecord*>(d_output.ptr);
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.radius = static_cast<float>(radius);
    lp.trace_tmax = 2.0f * (prepared->max_radius + 1.0e-4f);

    DevPtr d_params(sizeof(PointGroupNearestRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_point_group_nearest_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(PointGroupNearestRtLaunchParams),
                             &g_point_group_nearest_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    std::vector<GpuFixedRadiusNearestRecord> gpu_rows(query_count);
    download(gpu_rows.data(), d_output.ptr, query_count);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();

    auto* out = static_cast<RtdlFixedRadiusNeighborRow*>(
        std::malloc(sizeof(RtdlFixedRadiusNeighborRow) * query_count));
    if (!out && query_count > 0) throw std::bad_alloc();
    for (size_t i = 0; i < query_count; ++i) {
        out[i].query_id = gpu_rows[i].query_id;
        out[i].neighbor_id = gpu_rows[i].neighbor_id;
        out[i].distance = static_cast<double>(gpu_rows[i].distance);
    }
    *rows_out = out;
    *row_count_out = query_count;
}

static void reduce_prepared_point_group_nearest_max_distance_2d_optix(
        PreparedPointGroupNearestWitness2D* prepared,
        const RtdlPoint* query_points,
        size_t query_count,
        double radius,
        RtdlFixedRadiusNeighborRow* row_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX point-group handle must not be null");
    if (!row_out) throw std::runtime_error("row_out must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("point_group_nearest_max_distance radius must be non-negative");
    if (radius > static_cast<double>(prepared->max_radius) + 1.0e-7)
        throw std::runtime_error("point_group_nearest_max_distance radius exceeds prepared max_radius");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("point_group_nearest_max_distance query_count exceeds uint32 limit");

    row_out->query_id = UINT32_MAX;
    row_out->neighbor_id = UINT32_MAX;
    row_out->distance = std::numeric_limits<double>::infinity();
    if (query_count == 0 || prepared->groups.empty()) return;

    std::call_once(g_point_group_nearest_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kPointGroupNearestRtKernelSrc, "point_group_nearest_rt_kernel.cu");
        g_point_group_nearest_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__point_group_nearest_probe",
            "__miss__point_group_nearest_miss",
            "__intersection__point_group_nearest_isect",
            "__anyhit__point_group_nearest_anyhit",
            nullptr, 4).release();
    });
    std::call_once(g_point_group_nearest_reduce.init, [&]() {
        std::string ptx = compile_to_ptx(
            kPointGroupNearestMaxReduceKernelSrc,
            "point_group_nearest_max_reduce_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_point_group_nearest_reduce.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(
            &g_point_group_nearest_reduce.fn,
            g_point_group_nearest_reduce.module,
            "reduce_point_group_nearest_max_distance"));
    });

    std::vector<GpuPoint> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            query_points[i].id
        };
    }

    DevPtr d_queries(sizeof(GpuPoint) * query_count);
    DevPtr d_output(sizeof(GpuFixedRadiusNearestRecord) * query_count);
    DevPtr d_reduced(sizeof(GpuFixedRadiusNearestRecord));
    upload(d_queries.ptr, gpu_queries.data(), query_count);

    PointGroupNearestRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint*>(prepared->d_search.ptr);
    lp.groups = reinterpret_cast<const GpuPointGroupBounds*>(prepared->d_groups.ptr);
    lp.output = reinterpret_cast<GpuFixedRadiusNearestRecord*>(d_output.ptr);
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.radius = static_cast<float>(radius);
    lp.trace_tmax = 2.0f * (prepared->max_radius + 1.0e-4f);

    DevPtr d_params(sizeof(PointGroupNearestRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_point_group_nearest_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(PointGroupNearestRtLaunchParams),
                             &g_point_group_nearest_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    uint32_t count_u32 = static_cast<uint32_t>(query_count);
    void* reduce_args[] = { &d_output.ptr, &count_u32, &d_reduced.ptr };
    CU_CHECK(cuLaunchKernel(
        g_point_group_nearest_reduce.fn,
        1, 1, 1,
        256, 1, 1,
        0, stream, reduce_args, nullptr));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    GpuFixedRadiusNearestRecord reduced{};
    download(&reduced, d_reduced.ptr, 1);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();

    row_out->query_id = reduced.query_id;
    row_out->neighbor_id = reduced.neighbor_id;
    row_out->distance = static_cast<double>(reduced.distance);
}

static void run_fixed_radius_neighbors_cuda_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        const RtdlPoint3D* search_points, size_t search_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out)
{
    (void)get_optix_context();
    std::call_once(g_frn3d.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusNeighbors3DKernelSrc, "frn3d_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_frn3d.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(&g_frn3d.fn, g_frn3d.module, "fixed_radius_neighbors_3d"));
    });

    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    constexpr size_t kFixedRadiusSlack = 8;

    std::vector<GpuPoint3DHost> gpu_queries(query_count);
    std::vector<GpuPoint3DHost> gpu_search(search_count);
    for (size_t i = 0; i < query_count; ++i)
        gpu_queries[i] = {(float)query_points[i].x, (float)query_points[i].y, (float)query_points[i].z, query_points[i].id};
    for (size_t i = 0; i < search_count; ++i)
        gpu_search[i] = {(float)search_points[i].x, (float)search_points[i].y, (float)search_points[i].z, search_points[i].id};

    const size_t capped_k_max = std::min(k_max, search_count);
    const size_t candidate_slack = std::min(
        kFixedRadiusSlack,
        search_count > capped_k_max ? search_count - capped_k_max : size_t{0});
    const size_t kernel_k_max = capped_k_max + candidate_slack;
    if (query_count != 0 && kernel_k_max > ((std::numeric_limits<size_t>::max)() / query_count)) {
        throw std::runtime_error("fixed_radius_neighbors output_capacity overflows size_t");
    }
    const size_t output_capacity = query_count * kernel_k_max;
    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    DevPtr d_search(sizeof(GpuPoint3DHost) * search_count);
    DevPtr d_output(sizeof(GpuFrnRecord) * output_capacity);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    upload(d_search.ptr, gpu_search.data(), search_count);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t sc = static_cast<uint32_t>(search_count);
    float radius_f = static_cast<float>(radius + kFixedRadiusCandidateEps);
    uint32_t k_max_u32 = static_cast<uint32_t>(kernel_k_max);
    void* args[] = {
        &d_queries.ptr,
        &qc,
        &d_search.ptr,
        &sc,
        &radius_f,
        &k_max_u32,
        &d_output.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1) / block;
    CU_CHECK(cuLaunchKernel(g_frn3d.fn, grid, 1, 1, block, 1, 1, 0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));

    std::vector<GpuFrnRecord> gpu_rows(output_capacity);
    download(gpu_rows.data(), d_output.ptr, output_capacity);

    std::unordered_map<uint32_t, const RtdlPoint3D*> query_by_id;
    std::unordered_map<uint32_t, const RtdlPoint3D*> search_by_id;
    query_by_id.reserve(query_count);
    search_by_id.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
        query_by_id.emplace(query_points[i].id, query_points + i);
    }
    for (size_t i = 0; i < search_count; ++i) {
        search_by_id.emplace(search_points[i].id, search_points + i);
    }

    std::vector<RtdlFixedRadiusNeighborRow> exact_rows;
    exact_rows.reserve(output_capacity);
    for (size_t i = 0; i < output_capacity; ++i) {
        if (gpu_rows[i].neighbor_id == UINT32_MAX) {
            continue;
        }
        auto query_it = query_by_id.find(gpu_rows[i].query_id);
        auto search_it = search_by_id.find(gpu_rows[i].neighbor_id);
        if (query_it == query_by_id.end() || search_it == search_by_id.end()) {
            continue;
        }
        double dx = search_it->second->x - query_it->second->x;
        double dy = search_it->second->y - query_it->second->y;
        double dz = search_it->second->z - query_it->second->z;
        double exact_distance = std::sqrt(dx * dx + dy * dy + dz * dz);
        if (exact_distance <= radius) {
            exact_rows.push_back({
                gpu_rows[i].query_id,
                gpu_rows[i].neighbor_id,
                exact_distance,
            });
        }
    }

    std::stable_sort(exact_rows.begin(), exact_rows.end(), [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
        if (left.query_id != right.query_id) {
            return left.query_id < right.query_id;
        }
        if (left.distance < right.distance - 1.0e-12) {
            return true;
        }
        if (right.distance < left.distance - 1.0e-12) {
            return false;
        }
        return left.neighbor_id < right.neighbor_id;
    });

    std::vector<RtdlFixedRadiusNeighborRow> rows;
    rows.reserve(exact_rows.size());
    uint32_t current_query_id = 0;
    size_t current_count = 0;
    bool have_query = false;
    for (const auto& row : exact_rows) {
        if (!have_query || row.query_id != current_query_id) {
            current_query_id = row.query_id;
            current_count = 0;
            have_query = true;
        }
        if (current_count >= k_max) {
            continue;
        }
        rows.push_back(row);
        current_count += 1;
    }

    auto* out = static_cast<RtdlFixedRadiusNeighborRow*>(
        std::malloc(sizeof(RtdlFixedRadiusNeighborRow) * rows.size()));
    if (!out && !rows.empty()) throw std::bad_alloc();
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlFixedRadiusNeighborRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_k_closest_hits_cuda(
        const RtdlPoint* query_points, size_t query_count,
        const RtdlPoint* search_points, size_t search_count,
        size_t k,
        RtdlKnnNeighborRow** rows_out, size_t* row_count_out)
{
    (void)get_optix_context();
    std::call_once(g_knn.init, [&]() {
        std::string ptx = compile_to_ptx(kKnnRowsKernelSrc, "k_closest_hits_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_knn.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(&g_knn.fn, g_knn.module, "knn_rows"));
    });

    struct GpuPt { float x, y; uint32_t id, pad; };

    std::vector<GpuPt> gpu_queries(query_count);
    std::vector<GpuPt> gpu_search(search_count);
    for (size_t i = 0; i < query_count; ++i)
        gpu_queries[i] = {(float)query_points[i].x, (float)query_points[i].y, query_points[i].id, 0u};
    for (size_t i = 0; i < search_count; ++i)
        gpu_search[i] = {(float)search_points[i].x, (float)search_points[i].y, search_points[i].id, 0u};

    if (query_count != 0 && k > ((std::numeric_limits<size_t>::max)() / query_count)) {
        throw std::runtime_error("knn_rows output_capacity overflows size_t");
    }
    const size_t output_capacity = query_count * k;
    DevPtr d_queries(sizeof(GpuPt) * query_count);
    DevPtr d_search(sizeof(GpuPt) * search_count);
    DevPtr d_output(sizeof(GpuKnnRecord) * output_capacity);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    upload(d_search.ptr, gpu_search.data(), search_count);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t sc = static_cast<uint32_t>(search_count);
    uint32_t k_u32 = static_cast<uint32_t>(k);
    void* args[] = {
        &d_queries.ptr,
        &qc,
        &d_search.ptr,
        &sc,
        &k_u32,
        &d_output.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1) / block;
    CU_CHECK(cuLaunchKernel(g_knn.fn, grid, 1, 1, block, 1, 1, 0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));

    std::vector<GpuKnnRecord> gpu_rows(output_capacity);
    download(gpu_rows.data(), d_output.ptr, output_capacity);

    std::vector<RtdlKnnNeighborRow> rows;
    rows.reserve(output_capacity);
    for (size_t i = 0; i < output_capacity; ++i) {
        if (gpu_rows[i].neighbor_id == UINT32_MAX) {
            continue;
        }
        rows.push_back({
            gpu_rows[i].query_id,
            gpu_rows[i].neighbor_id,
            static_cast<double>(gpu_rows[i].distance),
            gpu_rows[i].neighbor_rank,
        });
    }
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
        if (left.query_id != right.query_id) {
            return left.query_id < right.query_id;
        }
        return left.neighbor_rank < right.neighbor_rank;
    });

    auto* out = static_cast<RtdlKnnNeighborRow*>(
        std::malloc(sizeof(RtdlKnnNeighborRow) * rows.size()));
    if (!out && !rows.empty()) throw std::bad_alloc();
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlKnnNeighborRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_k_closest_hits_cuda_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        const RtdlPoint3D* search_points, size_t search_count,
        size_t k,
        RtdlKnnNeighborRow** rows_out, size_t* row_count_out)
{
    (void)get_optix_context();
    std::call_once(g_knn3d.init, [&]() {
        std::string ptx = compile_to_ptx(kKnnRows3DKernelSrc, "knn3d_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_knn3d.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(&g_knn3d.fn, g_knn3d.module, "knn_rows_3d"));
    });

    std::vector<GpuPoint3DHost> gpu_queries(query_count);
    std::vector<GpuPoint3DHost> gpu_search(search_count);
    for (size_t i = 0; i < query_count; ++i)
        gpu_queries[i] = {(float)query_points[i].x, (float)query_points[i].y, (float)query_points[i].z, query_points[i].id};
    for (size_t i = 0; i < search_count; ++i)
        gpu_search[i] = {(float)search_points[i].x, (float)search_points[i].y, (float)search_points[i].z, search_points[i].id};

    const size_t capped_k = std::min(k, search_count);
    const size_t candidate_slack = std::min(
        static_cast<size_t>(8),
        search_count > capped_k ? search_count - capped_k : static_cast<size_t>(0));
    const size_t kernel_k = capped_k + candidate_slack;

    if (query_count != 0 && kernel_k > ((std::numeric_limits<size_t>::max)() / query_count)) {
        throw std::runtime_error("knn_rows output_capacity overflows size_t");
    }
    const size_t output_capacity = query_count * kernel_k;
    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    DevPtr d_search(sizeof(GpuPoint3DHost) * search_count);
    DevPtr d_output(sizeof(GpuKnnRecord) * output_capacity);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    upload(d_search.ptr, gpu_search.data(), search_count);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t sc = static_cast<uint32_t>(search_count);
    uint32_t k_u32 = static_cast<uint32_t>(kernel_k);
    void* args[] = {
        &d_queries.ptr,
        &qc,
        &d_search.ptr,
        &sc,
        &k_u32,
        &d_output.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1) / block;
    CU_CHECK(cuLaunchKernel(g_knn3d.fn, grid, 1, 1, block, 1, 1, 0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));

    std::vector<GpuKnnRecord> gpu_rows(output_capacity);
    download(gpu_rows.data(), d_output.ptr, output_capacity);

    std::unordered_map<uint32_t, const RtdlPoint3D*> query_by_id;
    std::unordered_map<uint32_t, const RtdlPoint3D*> search_by_id;
    query_by_id.reserve(query_count);
    search_by_id.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
        query_by_id.emplace(query_points[i].id, query_points + i);
    }
    for (size_t i = 0; i < search_count; ++i) {
        search_by_id.emplace(search_points[i].id, search_points + i);
    }

    std::vector<RtdlKnnNeighborRow> rows;
    rows.reserve(output_capacity);
    for (size_t i = 0; i < output_capacity; ++i) {
        if (gpu_rows[i].neighbor_id == UINT32_MAX) {
            continue;
        }
        auto query_it = query_by_id.find(gpu_rows[i].query_id);
        auto search_it = search_by_id.find(gpu_rows[i].neighbor_id);
        if (query_it == query_by_id.end() || search_it == search_by_id.end()) {
            continue;
        }
        double dx = search_it->second->x - query_it->second->x;
        double dy = search_it->second->y - query_it->second->y;
        double dz = search_it->second->z - query_it->second->z;
        double exact_distance = std::sqrt(dx * dx + dy * dy + dz * dz);
        rows.push_back({
            gpu_rows[i].query_id,
            gpu_rows[i].neighbor_id,
            exact_distance,
            0u,
        });
    }
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
        if (left.query_id != right.query_id) {
            return left.query_id < right.query_id;
        }
        if (left.distance < right.distance - 1.0e-12) {
            return true;
        }
        if (right.distance < left.distance - 1.0e-12) {
            return false;
        }
        return left.neighbor_id < right.neighbor_id;
    });
    std::vector<RtdlKnnNeighborRow> trimmed_rows;
    trimmed_rows.reserve(query_count * capped_k);
    size_t index = 0;
    while (index < rows.size()) {
        const uint32_t query_id = rows[index].query_id;
        size_t end = index;
        while (end < rows.size() && rows[end].query_id == query_id) {
            ++end;
        }
        const size_t keep = std::min(capped_k, end - index);
        for (size_t offset = 0; offset < keep; ++offset) {
            auto row = rows[index + offset];
            row.neighbor_rank = static_cast<uint32_t>(offset + 1);
            trimmed_rows.push_back(row);
        }
        index = end;
    }

    auto* out = static_cast<RtdlKnnNeighborRow*>(
        std::malloc(sizeof(RtdlKnnNeighborRow) * trimmed_rows.size()));
    if (!out && !trimmed_rows.empty()) throw std::bad_alloc();
    if (!trimmed_rows.empty()) {
        std::memcpy(out, trimmed_rows.data(), sizeof(RtdlKnnNeighborRow) * trimmed_rows.size());
    }
    *rows_out = out;
    *row_count_out = trimmed_rows.size();
}
