constexpr uint32_t kColumnKindInt64 = 1u;
constexpr uint32_t kColumnKindFloat64 = 2u;
constexpr uint32_t kColumnKindBool = 3u;
constexpr uint32_t kColumnKindText = 4u;

constexpr uint32_t kColumnOpEq = 1u;
constexpr uint32_t kColumnOpLt = 2u;
constexpr uint32_t kColumnOpLe = 3u;
constexpr uint32_t kColumnOpGt = 4u;
constexpr uint32_t kColumnOpGe = 5u;
constexpr uint32_t kColumnOpBetween = 6u;

constexpr size_t kColumnarMaxRowsPerJob = 1000000;
constexpr size_t kColumnarMaxCandidateRowsPerJob = 1000000;
constexpr size_t kColumnarMaxGroupsPerJob = 65536;
constexpr size_t kDeviceColumnGroupedMaxRowsPerJob = 100000000;
constexpr float kColumnarBoxPad = 1.0e-3f;
constexpr float kGraphEdgeBoxPad = 1.0e-3f;

struct ColumnarPrimaryAxis {
    size_t field_index;
    std::vector<double> sorted_values;
    int64_t encoded_lo;
    int64_t encoded_hi;
};

struct ColumnarRowMeta {
    size_t row_index;
    uint32_t row_id;
};

struct ColumnarPredicateScanLaunchParams {
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

struct OptixColumnarPayloadImpl {
    std::vector<std::string> field_names;
    std::vector<RtdlColumnField> fields;
    std::vector<std::string> scalar_strings;
    std::vector<RtdlColumnScalar> row_values;
    size_t row_count = 0;
    std::vector<ColumnarPrimaryAxis> primary_axes;
    std::vector<ColumnarRowMeta> row_metas;
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

thread_local double g_optix_last_columnar_traversal_s = 0.0;
thread_local double g_optix_last_columnar_bitset_copy_s = 0.0;
thread_local double g_optix_last_columnar_exact_filter_s = 0.0;
thread_local double g_optix_last_columnar_output_pack_s = 0.0;
thread_local size_t g_optix_last_columnar_raw_candidate_count = 0;
thread_local size_t g_optix_last_columnar_emitted_count = 0;

thread_local double g_optix_last_segment_pair_left_upload_s = 0.0;
thread_local double g_optix_last_segment_pair_candidate_count_s = 0.0;
thread_local double g_optix_last_segment_pair_candidate_write_s = 0.0;
thread_local double g_optix_last_segment_pair_candidate_download_s = 0.0;
thread_local double g_optix_last_segment_pair_exact_refine_s = 0.0;
thread_local size_t g_optix_last_segment_pair_raw_candidate_count = 0;
thread_local size_t g_optix_last_segment_pair_emitted_count = 0;
thread_local uint32_t g_optix_last_segment_pair_mode = 0;

thread_local double g_optix_last_closed_shape_point_pack_s = 0.0;
thread_local double g_optix_last_closed_shape_point_upload_s = 0.0;
thread_local double g_optix_last_closed_shape_candidate_count_s = 0.0;
thread_local double g_optix_last_closed_shape_candidate_write_s = 0.0;
thread_local double g_optix_last_closed_shape_candidate_download_s = 0.0;
thread_local double g_optix_last_closed_shape_exact_refine_s = 0.0;
thread_local size_t g_optix_last_closed_shape_raw_candidate_count = 0;
thread_local size_t g_optix_last_closed_shape_emitted_count = 0;
thread_local uint32_t g_optix_last_closed_shape_mode = 0;

thread_local double g_optix_last_fixed_radius_3d_prepare_s = 0.0;
thread_local double g_optix_last_fixed_radius_3d_upload_s = 0.0;
thread_local double g_optix_last_fixed_radius_3d_count_s = 0.0;
thread_local double g_optix_last_fixed_radius_3d_count_download_s = 0.0;
thread_local double g_optix_last_fixed_radius_3d_row_offset_upload_s = 0.0;
thread_local double g_optix_last_fixed_radius_3d_compact_s = 0.0;
thread_local double g_optix_last_fixed_radius_3d_row_download_s = 0.0;
thread_local double g_optix_last_fixed_radius_3d_exact_refine_s = 0.0;
thread_local size_t g_optix_last_fixed_radius_3d_raw_candidate_count = 0;
thread_local size_t g_optix_last_fixed_radius_3d_emitted_count = 0;
thread_local uint32_t g_optix_last_fixed_radius_3d_mode = 0;

extern "C" int rtdl_optix_columnar_payload_get_last_phase_timings(
        double* traversal,
        double* bitset_copy,
        double* exact_filter,
        double* output_pack,
        size_t* raw_candidate_count,
        size_t* emitted_count)
{
    if (traversal) *traversal = g_optix_last_columnar_traversal_s;
    if (bitset_copy) *bitset_copy = g_optix_last_columnar_bitset_copy_s;
    if (exact_filter) *exact_filter = g_optix_last_columnar_exact_filter_s;
    if (output_pack) *output_pack = g_optix_last_columnar_output_pack_s;
    if (raw_candidate_count) *raw_candidate_count = g_optix_last_columnar_raw_candidate_count;
    if (emitted_count) *emitted_count = g_optix_last_columnar_emitted_count;
    return 0;
}

extern "C" int rtdl_optix_segment_pair_intersection_get_last_phase_timings(
        double* left_upload,
        double* candidate_count,
        double* candidate_write,
        double* candidate_download,
        double* exact_refine,
        size_t* raw_candidate_count,
        size_t* emitted_count,
        uint32_t* mode)
{
    if (left_upload) *left_upload = g_optix_last_segment_pair_left_upload_s;
    if (candidate_count) *candidate_count = g_optix_last_segment_pair_candidate_count_s;
    if (candidate_write) *candidate_write = g_optix_last_segment_pair_candidate_write_s;
    if (candidate_download) *candidate_download = g_optix_last_segment_pair_candidate_download_s;
    if (exact_refine) *exact_refine = g_optix_last_segment_pair_exact_refine_s;
    if (raw_candidate_count) *raw_candidate_count = g_optix_last_segment_pair_raw_candidate_count;
    if (emitted_count) *emitted_count = g_optix_last_segment_pair_emitted_count;
    if (mode) *mode = g_optix_last_segment_pair_mode;
    return 0;
}

extern "C" int rtdl_optix_closed_shape_membership_get_last_phase_timings(
        double* point_pack,
        double* point_upload,
        double* candidate_count,
        double* candidate_write,
        double* candidate_download,
        double* exact_refine,
        size_t* raw_candidate_count,
        size_t* emitted_count,
        uint32_t* mode)
{
    if (point_pack) *point_pack = g_optix_last_closed_shape_point_pack_s;
    if (point_upload) *point_upload = g_optix_last_closed_shape_point_upload_s;
    if (candidate_count) *candidate_count = g_optix_last_closed_shape_candidate_count_s;
    if (candidate_write) *candidate_write = g_optix_last_closed_shape_candidate_write_s;
    if (candidate_download) *candidate_download = g_optix_last_closed_shape_candidate_download_s;
    if (exact_refine) *exact_refine = g_optix_last_closed_shape_exact_refine_s;
    if (raw_candidate_count) *raw_candidate_count = g_optix_last_closed_shape_raw_candidate_count;
    if (emitted_count) *emitted_count = g_optix_last_closed_shape_emitted_count;
    if (mode) *mode = g_optix_last_closed_shape_mode;
    return 0;
}

extern "C" int rtdl_optix_fixed_radius_neighbors_3d_get_last_phase_timings(
        double* prepare,
        double* upload,
        double* candidate_count,
        double* count_download,
        double* row_offset_upload,
        double* candidate_write,
        double* row_download,
        double* exact_refine,
        size_t* raw_candidate_count,
        size_t* emitted_count,
        uint32_t* mode)
{
    if (prepare) *prepare = g_optix_last_fixed_radius_3d_prepare_s;
    if (upload) *upload = g_optix_last_fixed_radius_3d_upload_s;
    if (candidate_count) *candidate_count = g_optix_last_fixed_radius_3d_count_s;
    if (count_download) *count_download = g_optix_last_fixed_radius_3d_count_download_s;
    if (row_offset_upload) *row_offset_upload = g_optix_last_fixed_radius_3d_row_offset_upload_s;
    if (candidate_write) *candidate_write = g_optix_last_fixed_radius_3d_compact_s;
    if (row_download) *row_download = g_optix_last_fixed_radius_3d_row_download_s;
    if (exact_refine) *exact_refine = g_optix_last_fixed_radius_3d_exact_refine_s;
    if (raw_candidate_count) *raw_candidate_count = g_optix_last_fixed_radius_3d_raw_candidate_count;
    if (emitted_count) *emitted_count = g_optix_last_fixed_radius_3d_emitted_count;
    if (mode) *mode = g_optix_last_fixed_radius_3d_mode;
    return 0;
}

static void reset_segment_pair_phase_timings(uint32_t mode)
{
    g_optix_last_segment_pair_left_upload_s = 0.0;
    g_optix_last_segment_pair_candidate_count_s = 0.0;
    g_optix_last_segment_pair_candidate_write_s = 0.0;
    g_optix_last_segment_pair_candidate_download_s = 0.0;
    g_optix_last_segment_pair_exact_refine_s = 0.0;
    g_optix_last_segment_pair_raw_candidate_count = 0;
    g_optix_last_segment_pair_emitted_count = 0;
    g_optix_last_segment_pair_mode = mode;
}

static void reset_closed_shape_membership_phase_timings(uint32_t mode)
{
    g_optix_last_closed_shape_point_pack_s = 0.0;
    g_optix_last_closed_shape_point_upload_s = 0.0;
    g_optix_last_closed_shape_candidate_count_s = 0.0;
    g_optix_last_closed_shape_candidate_write_s = 0.0;
    g_optix_last_closed_shape_candidate_download_s = 0.0;
    g_optix_last_closed_shape_exact_refine_s = 0.0;
    g_optix_last_closed_shape_raw_candidate_count = 0;
    g_optix_last_closed_shape_emitted_count = 0;
    g_optix_last_closed_shape_mode = mode;
}

static void reset_fixed_radius_3d_phase_timings(uint32_t mode)
{
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    g_optix_last_fixed_radius_3d_upload_s = 0.0;
    g_optix_last_fixed_radius_3d_count_s = 0.0;
    g_optix_last_fixed_radius_3d_count_download_s = 0.0;
    g_optix_last_fixed_radius_3d_row_offset_upload_s = 0.0;
    g_optix_last_fixed_radius_3d_compact_s = 0.0;
    g_optix_last_fixed_radius_3d_row_download_s = 0.0;
    g_optix_last_fixed_radius_3d_exact_refine_s = 0.0;
    g_optix_last_fixed_radius_3d_raw_candidate_count = 0;
    g_optix_last_fixed_radius_3d_emitted_count = 0;
    g_optix_last_fixed_radius_3d_mode = mode;
}

static double seconds_between(
        std::chrono::steady_clock::time_point start,
        std::chrono::steady_clock::time_point end)
{
    return std::chrono::duration<double>(end - start).count();
}

static size_t columnar_find_field_index_or_throw(
        const RtdlColumnField* fields,
        size_t field_count,
        const char* name)
{
    if (!name) {
        throw std::runtime_error("columnar field name must not be null");
    }
    for (size_t index = 0; index < field_count; ++index) {
        if (fields[index].name && std::strcmp(fields[index].name, name) == 0) {
            return index;
        }
    }
    throw std::runtime_error(std::string("unknown columnar field: ") + name);
}

static const RtdlColumnScalar& columnar_row_value(
        const RtdlColumnScalar* row_values,
        size_t row_index,
        size_t field_count,
        size_t field_index)
{
    return row_values[row_index * field_count + field_index];
}

static bool columnar_scalar_is_numeric(const RtdlColumnScalar& value)
{
    return value.kind == kColumnKindInt64 || value.kind == kColumnKindFloat64 || value.kind == kColumnKindBool;
}

static bool columnar_field_kind_is_numeric(uint32_t kind)
{
    return kind == kColumnKindInt64 || kind == kColumnKindFloat64 || kind == kColumnKindBool;
}

static double columnar_scalar_as_double(const RtdlColumnScalar& value)
{
    if (value.kind == kColumnKindInt64 || value.kind == kColumnKindBool) {
        return static_cast<double>(value.int_value);
    }
    if (value.kind == kColumnKindFloat64) {
        return value.double_value;
    }
    throw std::runtime_error("columnar scalar is not numeric");
}

static int columnar_compare_scalar(const RtdlColumnScalar& left, const RtdlColumnScalar& right)
{
    if (left.kind != right.kind) {
        const double lhs = columnar_scalar_as_double(left);
        const double rhs = columnar_scalar_as_double(right);
        if (lhs < rhs) return -1;
        if (lhs > rhs) return 1;
        return 0;
    }
    switch (left.kind) {
        case kColumnKindInt64:
        case kColumnKindBool:
            if (left.int_value < right.int_value) return -1;
            if (left.int_value > right.int_value) return 1;
            return 0;
        case kColumnKindFloat64:
            if (left.double_value < right.double_value) return -1;
            if (left.double_value > right.double_value) return 1;
            return 0;
        case kColumnKindText: {
            const char* lhs = left.string_value ? left.string_value : "";
            const char* rhs = right.string_value ? right.string_value : "";
            const int cmp = std::strcmp(lhs, rhs);
            if (cmp < 0) return -1;
            if (cmp > 0) return 1;
            return 0;
        }
        default:
            throw std::runtime_error("unsupported columnar scalar kind");
    }
}

static bool columnar_clause_matches_scalar(const RtdlColumnClause& clause, const RtdlColumnScalar& candidate)
{
    const int cmp_lo = columnar_compare_scalar(candidate, clause.value);
    switch (clause.op) {
        case kColumnOpEq:
            return cmp_lo == 0;
        case kColumnOpLt:
            return cmp_lo < 0;
        case kColumnOpLe:
            return cmp_lo <= 0;
        case kColumnOpGt:
            return cmp_lo > 0;
        case kColumnOpGe:
            return cmp_lo >= 0;
        case kColumnOpBetween:
            return cmp_lo >= 0 && columnar_compare_scalar(candidate, clause.value_hi) <= 0;
        default:
            throw std::runtime_error("unsupported columnar clause op");
    }
}

static bool columnar_row_matches_all_clauses(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_index,
        const RtdlColumnClause* clauses,
        size_t clause_count)
{
    for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
        const size_t field_index = columnar_find_field_index_or_throw(fields, field_count, clauses[clause_index].field);
        const RtdlColumnScalar& candidate = columnar_row_value(row_values, row_index, field_count, field_index);
        if (!columnar_clause_matches_scalar(clauses[clause_index], candidate)) {
            return false;
        }
    }
    return true;
}

static std::vector<double> columnar_sorted_distinct_numeric_values(
        const RtdlColumnScalar* row_values,
        size_t row_count,
        size_t field_count,
        size_t field_index)
{
    std::vector<double> values;
    values.reserve(row_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        const RtdlColumnScalar& value = columnar_row_value(row_values, row_index, field_count, field_index);
        if (!columnar_scalar_is_numeric(value)) {
            throw std::runtime_error("first-wave OptiX columnar lowering requires numeric primary scan clauses");
        }
        values.push_back(columnar_scalar_as_double(value));
    }
    std::sort(values.begin(), values.end());
    values.erase(std::unique(values.begin(), values.end()), values.end());
    return values;
}

static bool columnar_clause_matches_numeric_value(const RtdlColumnClause& clause, double value)
{
    const double lo = columnar_scalar_as_double(clause.value);
    switch (clause.op) {
        case kColumnOpEq:
            return value == lo;
        case kColumnOpLt:
            return value < lo;
        case kColumnOpLe:
            return value <= lo;
        case kColumnOpGt:
            return value > lo;
        case kColumnOpGe:
            return value >= lo;
        case kColumnOpBetween:
            return value >= lo && value <= columnar_scalar_as_double(clause.value_hi);
        default:
            throw std::runtime_error("unsupported columnar clause op");
    }
}

static ColumnarPrimaryAxis columnar_make_primary_axis(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const RtdlColumnClause& clause)
{
    const size_t field_index = columnar_find_field_index_or_throw(fields, field_count, clause.field);
    const std::vector<double> sorted_values =
        columnar_sorted_distinct_numeric_values(row_values, row_count, field_count, field_index);
    int64_t encoded_lo = -1;
    int64_t encoded_hi = -1;
    for (size_t index = 0; index < sorted_values.size(); ++index) {
        if (!columnar_clause_matches_numeric_value(clause, sorted_values[index])) {
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

static ColumnarPrimaryAxis columnar_make_full_primary_axis(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const char* field_name)
{
    const size_t field_index = columnar_find_field_index_or_throw(fields, field_count, field_name);
    if (!columnar_field_kind_is_numeric(fields[field_index].kind)) {
        throw std::runtime_error("first-wave OptiX prepared columnar payloads require numeric primary RT axes");
    }
    const std::vector<double> sorted_values =
        columnar_sorted_distinct_numeric_values(row_values, row_count, field_count, field_index);
    return {
        field_index,
        sorted_values,
        1,
        sorted_values.empty() ? 0 : static_cast<int64_t>(sorted_values.size())};
}

static ColumnarPrimaryAxis columnar_axis_with_clause_range(const ColumnarPrimaryAxis& axis, const RtdlColumnClause& clause)
{
    ColumnarPrimaryAxis ranged = axis;
    int64_t encoded_lo = -1;
    int64_t encoded_hi = -1;
    for (size_t index = 0; index < axis.sorted_values.size(); ++index) {
        if (!columnar_clause_matches_numeric_value(clause, axis.sorted_values[index])) {
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

static int64_t columnar_encode_axis_value(const ColumnarPrimaryAxis& axis, const RtdlColumnScalar& value)
{
    const double needle = columnar_scalar_as_double(value);
    const auto it = std::lower_bound(axis.sorted_values.begin(), axis.sorted_values.end(), needle);
    if (it == axis.sorted_values.end() || *it != needle) {
        throw std::runtime_error("failed to encode OptiX columnar primary-axis value");
    }
    return static_cast<int64_t>(std::distance(axis.sorted_values.begin(), it) + 1);
}

static std::vector<ColumnarRowMeta> columnar_build_row_metas(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count)
{
    const size_t row_id_index = columnar_find_field_index_or_throw(fields, field_count, "row_id");
    std::vector<ColumnarRowMeta> metas;
    metas.reserve(row_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        const RtdlColumnScalar& row_id_value = columnar_row_value(row_values, row_index, field_count, row_id_index);
        metas.push_back({row_index, static_cast<uint32_t>(row_id_value.int_value)});
    }
    return metas;
}

static std::vector<OptixAabb> columnar_build_row_aabbs(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const std::vector<ColumnarPrimaryAxis>& axes)
{
    std::vector<OptixAabb> aabbs;
    aabbs.reserve(row_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        const float x = axes.size() >= 1
            ? static_cast<float>(columnar_encode_axis_value(axes[0], columnar_row_value(row_values, row_index, field_count, axes[0].field_index)))
            : 1.0f;
        const float y = axes.size() >= 2
            ? static_cast<float>(columnar_encode_axis_value(axes[1], columnar_row_value(row_values, row_index, field_count, axes[1].field_index)))
            : 1.0f;
        const float z = axes.size() >= 3
            ? static_cast<float>(columnar_encode_axis_value(axes[2], columnar_row_value(row_values, row_index, field_count, axes[2].field_index)))
            : 1.0f;
        OptixAabb aabb;
        aabb.minX = x - kColumnarBoxPad;
        aabb.minY = y - kColumnarBoxPad;
        aabb.minZ = z - kColumnarBoxPad;
        aabb.maxX = x + kColumnarBoxPad;
        aabb.maxY = y + kColumnarBoxPad;
        aabb.maxZ = z + kColumnarBoxPad;
        aabbs.push_back(aabb);
    }
    return aabbs;
}

static std::vector<ColumnarPrimaryAxis> columnar_dataset_query_axes(
        const OptixColumnarPayloadImpl& dataset,
        const RtdlColumnClause* clauses,
        size_t clause_count)
{
    std::vector<ColumnarPrimaryAxis> axes = dataset.primary_axes;
    for (ColumnarPrimaryAxis& axis : axes) {
        const char* axis_field = dataset.fields[axis.field_index].name;
        for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
            if (std::strcmp(axis_field, clauses[clause_index].field) != 0) {
                continue;
            }
            axis = columnar_axis_with_clause_range(axis, clauses[clause_index]);
            break;
        }
    }
    return axes;
}

static std::vector<const char*> columnar_default_primary_fields(const RtdlColumnField* fields, size_t field_count)
{
    std::vector<const char*> names;
    for (size_t index = 0; index < field_count && names.size() < 3; ++index) {
        if (std::strcmp(fields[index].name, "row_id") == 0) {
            continue;
        }
        if (columnar_field_kind_is_numeric(fields[index].kind)) {
            names.push_back(fields[index].name);
        }
    }
    return names;
}

static size_t columnar_count_scalar_strings(const RtdlColumnScalar* row_values, size_t scalar_count)
{
    size_t count = 0;
    for (size_t index = 0; index < scalar_count; ++index) {
        if (row_values[index].kind == kColumnKindText && row_values[index].string_value) {
            ++count;
        }
    }
    return count;
}

static void columnar_copy_dataset_payload(
        OptixColumnarPayloadImpl& dataset,
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
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
    dataset.scalar_strings.reserve(columnar_count_scalar_strings(row_values, scalar_count));
    dataset.row_values.reserve(scalar_count);
    for (size_t index = 0; index < scalar_count; ++index) {
        RtdlColumnScalar copied = row_values[index];
        if (copied.kind == kColumnKindText && copied.string_value) {
            dataset.scalar_strings.emplace_back(copied.string_value);
            copied.string_value = dataset.scalar_strings.back().c_str();
        }
        dataset.row_values.push_back(copied);
    }
    dataset.row_count = row_count;
}

static void columnar_validate_payload_fields(
        const RtdlPayloadField* fields,
        size_t field_count,
        size_t row_count)
{
    if (!fields || field_count == 0) {
        throw std::runtime_error("payload fields must not be null");
    }
    if (row_count > kColumnarMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX columnar lowering supports at most 1000000 rows per RT job");
    }
    for (size_t field_index = 0; field_index < field_count; ++field_index) {
        const RtdlPayloadField& field = fields[field_index];
        if (!field.name) {
            throw std::runtime_error("field name must not be null");
        }
        if ((field.kind == kColumnKindInt64 || field.kind == kColumnKindBool) && !field.int_values) {
            throw std::runtime_error("field integer/bool values must not be null");
        }
        if (field.kind == kColumnKindFloat64 && !field.double_values) {
            throw std::runtime_error("field float values must not be null");
        }
        if (field.kind == kColumnKindText && !field.string_values) {
            throw std::runtime_error("field text values must not be null");
        }
    }
}

struct DeviceColumnGroupedI64Function {
    CUmodule module = nullptr;
    CUfunction fn = nullptr;
    CUfunction init_values_fn = nullptr;
    CUfunction compact_count_fn = nullptr;
    CUfunction compact_sum_fn = nullptr;
    CUfunction compact_sum_count_fn = nullptr;
    CUfunction compact_stats_fn = nullptr;
    std::once_flag init;
};

static DeviceColumnGroupedI64Function g_device_column_grouped_i64;

struct DeviceColumnRuntimeField {
    uint64_t device_ptr;
    uint32_t kind;
    uint32_t dtype;
};

struct DeviceColumnRuntimeClause {
    uint32_t field_index;
    uint32_t op;
    uint32_t value_kind;
    int64_t int_value;
    double double_value;
    int64_t int_value_hi;
    double double_value_hi;
};

struct DeviceColumnGroupedI64Params {
    const DeviceColumnRuntimeField* fields;
    uint32_t field_count;
    uint32_t row_count;
    const DeviceColumnRuntimeClause* clauses;
    uint32_t clause_count;
    uint32_t group_field_index;
    uint32_t value_field_index;
    uint32_t operation;
    uint32_t group_capacity;
    unsigned long long* group_counts;
    unsigned long long* group_sums;
    unsigned long long* group_mins;
    unsigned long long* group_maxs;
    uint32_t* invalid_group_count;
};

struct DeviceColumnGroupedCountRow {
    int64_t group_key;
    int64_t count;
};

struct DeviceColumnGroupedSumRow {
    int64_t group_key;
    int64_t sum;
};

struct DeviceColumnGroupedSumCountRow {
    int64_t group_key;
    int64_t sum;
    int64_t count;
};

struct DeviceColumnGroupedStatsRow {
    int64_t group_key;
    int64_t count;
    int64_t sum;
    int64_t min;
    int64_t max;
};

static const char* kDeviceColumnGroupedI64KernelSrc = R"CUDA(
#include <stdint.h>

struct DeviceColumnRuntimeField {
    uint64_t device_ptr;
    uint32_t kind;
    uint32_t dtype;
};

struct DeviceColumnRuntimeClause {
    uint32_t field_index;
    uint32_t op;
    uint32_t value_kind;
    int64_t int_value;
    double double_value;
    int64_t int_value_hi;
    double double_value_hi;
};

struct DeviceColumnGroupedI64Params {
    const DeviceColumnRuntimeField* fields;
    uint32_t field_count;
    uint32_t row_count;
    const DeviceColumnRuntimeClause* clauses;
    uint32_t clause_count;
    uint32_t group_field_index;
    uint32_t value_field_index;
    uint32_t operation;
    uint32_t group_capacity;
    unsigned long long* group_counts;
    unsigned long long* group_sums;
    unsigned long long* group_mins;
    unsigned long long* group_maxs;
    uint32_t* invalid_group_count;
};

struct DeviceColumnGroupedCountRow {
    int64_t group_key;
    int64_t count;
};

struct DeviceColumnGroupedSumRow {
    int64_t group_key;
    int64_t sum;
};

struct DeviceColumnGroupedSumCountRow {
    int64_t group_key;
    int64_t sum;
    int64_t count;
};

struct DeviceColumnGroupedStatsRow {
    int64_t group_key;
    int64_t count;
    int64_t sum;
    int64_t min;
    int64_t max;
};

enum {
    RTDL_COLUMN_KIND_INT64 = 1u,
    RTDL_COLUMN_KIND_FLOAT64 = 2u,
    RTDL_DEVICE_DTYPE_INT64 = 1u,
    RTDL_DEVICE_DTYPE_UINT32 = 2u,
    RTDL_DEVICE_DTYPE_FLOAT64 = 3u,
    RTDL_COLUMN_OP_EQ = 1u,
    RTDL_COLUMN_OP_LT = 2u,
    RTDL_COLUMN_OP_LE = 3u,
    RTDL_COLUMN_OP_GT = 4u,
    RTDL_COLUMN_OP_GE = 5u,
    RTDL_COLUMN_OP_BETWEEN = 6u,
    RTDL_GROUPED_OP_COUNT = 1u,
    RTDL_GROUPED_OP_SUM = 2u,
    RTDL_GROUPED_OP_MIN = 3u,
    RTDL_GROUPED_OP_MAX = 4u,
    RTDL_GROUPED_OP_SUM_COUNT = 5u,
    RTDL_GROUPED_OP_STATS = 6u
};

__device__ double device_column_read_numeric_double(const DeviceColumnRuntimeField& field, uint32_t row)
{
    if (field.dtype == RTDL_DEVICE_DTYPE_FLOAT64) {
        return reinterpret_cast<const double*>(field.device_ptr)[row];
    }
    if (field.dtype == RTDL_DEVICE_DTYPE_UINT32) {
        return static_cast<double>(reinterpret_cast<const uint32_t*>(field.device_ptr)[row]);
    }
    return static_cast<double>(reinterpret_cast<const int64_t*>(field.device_ptr)[row]);
}

__device__ long long device_column_read_i64_compatible(const DeviceColumnRuntimeField& field, uint32_t row)
{
    if (field.dtype == RTDL_DEVICE_DTYPE_UINT32) {
        return static_cast<long long>(reinterpret_cast<const uint32_t*>(field.device_ptr)[row]);
    }
    return static_cast<long long>(reinterpret_cast<const int64_t*>(field.device_ptr)[row]);
}

__device__ double device_clause_value_as_double(uint32_t kind, int64_t int_value, double double_value)
{
    return kind == RTDL_COLUMN_KIND_FLOAT64 ? double_value : static_cast<double>(int_value);
}

__device__ bool device_clause_matches(double candidate, const DeviceColumnRuntimeClause& clause)
{
    const double lo = device_clause_value_as_double(clause.value_kind, clause.int_value, clause.double_value);
    if (clause.op == RTDL_COLUMN_OP_EQ) return candidate == lo;
    if (clause.op == RTDL_COLUMN_OP_LT) return candidate < lo;
    if (clause.op == RTDL_COLUMN_OP_LE) return candidate <= lo;
    if (clause.op == RTDL_COLUMN_OP_GT) return candidate > lo;
    if (clause.op == RTDL_COLUMN_OP_GE) return candidate >= lo;
    if (clause.op == RTDL_COLUMN_OP_BETWEEN) {
        const double hi = device_clause_value_as_double(clause.value_kind, clause.int_value_hi, clause.double_value_hi);
        return candidate >= lo && candidate <= hi;
    }
    return false;
}

__device__ long long device_atomic_min_i64(long long* address, long long value)
{
    unsigned long long* address_as_ull = reinterpret_cast<unsigned long long*>(address);
    unsigned long long old = *address_as_ull;
    unsigned long long assumed;
    do {
        assumed = old;
        const long long current = static_cast<long long>(assumed);
        if (current <= value) return current;
        old = atomicCAS(address_as_ull, assumed, static_cast<unsigned long long>(value));
    } while (assumed != old);
    return static_cast<long long>(old);
}

__device__ long long device_atomic_max_i64(long long* address, long long value)
{
    unsigned long long* address_as_ull = reinterpret_cast<unsigned long long*>(address);
    unsigned long long old = *address_as_ull;
    unsigned long long assumed;
    do {
        assumed = old;
        const long long current = static_cast<long long>(assumed);
        if (current >= value) return current;
        old = atomicCAS(address_as_ull, assumed, static_cast<unsigned long long>(value));
    } while (assumed != old);
    return static_cast<long long>(old);
}

extern "C" __global__ void device_column_grouped_i64_init_values_kernel(
    long long* group_values,
    uint32_t group_capacity,
    long long initial_value)
{
    const uint32_t group = blockIdx.x * blockDim.x + threadIdx.x;
    if (group >= group_capacity) return;
    group_values[group] = initial_value;
}

extern "C" __global__ void device_column_grouped_i64_kernel(DeviceColumnGroupedI64Params params)
{
    const uint32_t row = blockIdx.x * blockDim.x + threadIdx.x;
    if (row >= params.row_count) return;

    for (uint32_t clause_index = 0; clause_index < params.clause_count; ++clause_index) {
        const DeviceColumnRuntimeClause& clause = params.clauses[clause_index];
        const DeviceColumnRuntimeField& field = params.fields[clause.field_index];
        const double candidate = device_column_read_numeric_double(field, row);
        if (!device_clause_matches(candidate, clause)) return;
    }

    const DeviceColumnRuntimeField& group_field = params.fields[params.group_field_index];
    const long long group_key = device_column_read_i64_compatible(group_field, row);
    if (group_key < 0 || group_key >= static_cast<long long>(params.group_capacity)) {
        atomicAdd(params.invalid_group_count, 1u);
        return;
    }
    const uint32_t group = static_cast<uint32_t>(group_key);
    atomicAdd(params.group_counts + group, 1ull);
    if (params.operation == RTDL_GROUPED_OP_SUM ||
        params.operation == RTDL_GROUPED_OP_MIN ||
        params.operation == RTDL_GROUPED_OP_MAX ||
        params.operation == RTDL_GROUPED_OP_SUM_COUNT ||
        params.operation == RTDL_GROUPED_OP_STATS) {
        const DeviceColumnRuntimeField& value_field = params.fields[params.value_field_index];
        const long long value = device_column_read_i64_compatible(value_field, row);
        if (params.operation == RTDL_GROUPED_OP_SUM || params.operation == RTDL_GROUPED_OP_SUM_COUNT) {
            atomicAdd(params.group_sums + group, static_cast<unsigned long long>(value));
        } else if (params.operation == RTDL_GROUPED_OP_MIN) {
            device_atomic_min_i64(reinterpret_cast<long long*>(params.group_sums) + group, value);
        } else if (params.operation == RTDL_GROUPED_OP_MAX) {
            device_atomic_max_i64(reinterpret_cast<long long*>(params.group_sums) + group, value);
        } else {
            atomicAdd(params.group_sums + group, static_cast<unsigned long long>(value));
            device_atomic_min_i64(reinterpret_cast<long long*>(params.group_mins) + group, value);
            device_atomic_max_i64(reinterpret_cast<long long*>(params.group_maxs) + group, value);
        }
    }
}

extern "C" __global__ void device_column_grouped_i64_compact_count_kernel(
    const unsigned long long* group_counts,
    uint32_t group_capacity,
    DeviceColumnGroupedCountRow* rows_out,
    uint32_t* row_count_out)
{
    const uint32_t group = blockIdx.x * blockDim.x + threadIdx.x;
    if (group >= group_capacity) return;
    const unsigned long long count = group_counts[group];
    if (count == 0ull) return;
    const uint32_t row_index = atomicAdd(row_count_out, 1u);
    rows_out[row_index].group_key = static_cast<int64_t>(group);
    rows_out[row_index].count = static_cast<int64_t>(count);
}

extern "C" __global__ void device_column_grouped_i64_compact_sum_kernel(
    const unsigned long long* group_counts,
    const unsigned long long* group_sums,
    uint32_t group_capacity,
    DeviceColumnGroupedSumRow* rows_out,
    uint32_t* row_count_out)
{
    const uint32_t group = blockIdx.x * blockDim.x + threadIdx.x;
    if (group >= group_capacity) return;
    if (group_counts[group] == 0ull) return;
    const uint32_t row_index = atomicAdd(row_count_out, 1u);
    rows_out[row_index].group_key = static_cast<int64_t>(group);
    rows_out[row_index].sum = static_cast<int64_t>(group_sums[group]);
}

extern "C" __global__ void device_column_grouped_i64_compact_sum_count_kernel(
    const unsigned long long* group_counts,
    const unsigned long long* group_sums,
    uint32_t group_capacity,
    DeviceColumnGroupedSumCountRow* rows_out,
    uint32_t* row_count_out)
{
    const uint32_t group = blockIdx.x * blockDim.x + threadIdx.x;
    if (group >= group_capacity) return;
    const unsigned long long count = group_counts[group];
    if (count == 0ull) return;
    const uint32_t row_index = atomicAdd(row_count_out, 1u);
    rows_out[row_index].group_key = static_cast<int64_t>(group);
    rows_out[row_index].sum = static_cast<int64_t>(group_sums[group]);
    rows_out[row_index].count = static_cast<int64_t>(count);
}

extern "C" __global__ void device_column_grouped_i64_compact_stats_kernel(
    const unsigned long long* group_counts,
    const unsigned long long* group_sums,
    const unsigned long long* group_mins,
    const unsigned long long* group_maxs,
    uint32_t group_capacity,
    DeviceColumnGroupedStatsRow* rows_out,
    uint32_t* row_count_out)
{
    const uint32_t group = blockIdx.x * blockDim.x + threadIdx.x;
    if (group >= group_capacity) return;
    const unsigned long long count = group_counts[group];
    if (count == 0ull) return;
    const uint32_t row_index = atomicAdd(row_count_out, 1u);
    rows_out[row_index].group_key = static_cast<int64_t>(group);
    rows_out[row_index].count = static_cast<int64_t>(count);
    rows_out[row_index].sum = static_cast<int64_t>(group_sums[group]);
    rows_out[row_index].min = static_cast<int64_t>(group_mins[group]);
    rows_out[row_index].max = static_cast<int64_t>(group_maxs[group]);
}
)CUDA";

static size_t columnar_device_payload_field_index_or_throw(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        const char* name)
{
    if (!name) {
        throw std::runtime_error("device-column payload field name must not be null");
    }
    for (size_t index = 0; index < field_count; ++index) {
        if (fields[index].name && std::strcmp(fields[index].name, name) == 0) {
            return index;
        }
    }
    throw std::runtime_error(std::string("unknown device-column payload field: ") + name);
}

static bool columnar_device_payload_dtype_is_i64_compatible(uint32_t dtype)
{
    return dtype == kRtdlDevicePayloadDtypeInt64 || dtype == kRtdlDevicePayloadDtypeUint32;
}

constexpr uint32_t kDeviceColumnGroupedOpCount = 1u;
constexpr uint32_t kDeviceColumnGroupedOpSum = 2u;
constexpr uint32_t kDeviceColumnGroupedOpMin = 3u;
constexpr uint32_t kDeviceColumnGroupedOpMax = 4u;
constexpr uint32_t kDeviceColumnGroupedOpSumCount = 5u;
constexpr uint32_t kDeviceColumnGroupedOpStats = 6u;

static void columnar_validate_device_payload_grouped_i64_inputs(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity)
{
    if (!fields || field_count == 0) {
        throw std::runtime_error("device-column grouped execution requires at least one field");
    }
    if (row_count == 0 || row_count > kDeviceColumnGroupedMaxRowsPerJob) {
        throw std::runtime_error("device-column grouped execution row_count must be in 1..100000000");
    }
    if (group_capacity == 0 || group_capacity > kColumnarMaxRowsPerJob) {
        throw std::runtime_error("device-column grouped execution group_capacity must be in 1..1000000");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("device-column grouped execution clause pointer must not be null");
    }
    if (!group_key_field) {
        throw std::runtime_error("device-column grouped execution requires a group_key_field");
    }

    uint32_t expected_device_id = 0;
    bool expected_device_id_set = false;
    for (size_t index = 0; index < field_count; ++index) {
        const RtdlDevicePayloadField& field = fields[index];
        if (!field.name || field.name[0] == '\0') {
            throw std::runtime_error("device-column payload field names must be non-empty");
        }
        if (field.device_type != kRtdlDevicePayloadDeviceCuda) {
            throw std::runtime_error("device-column grouped execution requires CUDA device pointers");
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
        if (field.dtype == kRtdlDevicePayloadDtypeInt64) {
            if (field.kind != kRtdlColumnKindInt64 || field.stride_bytes != sizeof(int64_t)) {
                throw std::runtime_error("int64 device columns must be int64 logical kind and contiguous");
            }
        } else if (field.dtype == kRtdlDevicePayloadDtypeUint32) {
            if (field.kind != kRtdlColumnKindInt64 || field.stride_bytes != sizeof(uint32_t)) {
                throw std::runtime_error("uint32 device columns must be int64-compatible logical kind and contiguous");
            }
        } else if (field.dtype == kRtdlDevicePayloadDtypeFloat64) {
            if (field.kind != kRtdlColumnKindFloat64 || field.stride_bytes != sizeof(double)) {
                throw std::runtime_error("float64 device columns must be float64 logical kind and contiguous");
            }
        } else {
            throw std::runtime_error("unsupported device-column payload dtype");
        }
    }

    const size_t group_index = columnar_device_payload_field_index_or_throw(fields, field_count, group_key_field);
    if (!columnar_device_payload_dtype_is_i64_compatible(fields[group_index].dtype)) {
        throw std::runtime_error("device-column grouped execution requires an int64-compatible group key");
    }
    if (value_field) {
        const size_t value_index = columnar_device_payload_field_index_or_throw(fields, field_count, value_field);
        if (!columnar_device_payload_dtype_is_i64_compatible(fields[value_index].dtype)) {
            throw std::runtime_error("device-column grouped value reduction requires an int64-compatible value field");
        }
    }
    for (size_t clause_index = 0; clause_index < clause_count; ++clause_index) {
        const RtdlColumnClause& clause = clauses[clause_index];
        const size_t field_index = columnar_device_payload_field_index_or_throw(fields, field_count, clause.field);
        if (!columnar_field_kind_is_numeric(fields[field_index].kind)) {
            throw std::runtime_error("device-column grouped execution supports numeric predicates only");
        }
        if (clause.op < kColumnOpEq || clause.op > kColumnOpBetween) {
            throw std::runtime_error("device-column grouped execution encountered unsupported predicate op");
        }
        if (!columnar_scalar_is_numeric(clause.value)) {
            throw std::runtime_error("device-column grouped execution supports numeric predicate values only");
        }
        if (clause.op == kColumnOpBetween && !columnar_scalar_is_numeric(clause.value_hi)) {
            throw std::runtime_error("device-column grouped execution supports numeric between upper bounds only");
        }
    }
}

static std::vector<DeviceColumnRuntimeField> columnar_make_device_runtime_fields(
        const RtdlDevicePayloadField* fields,
        size_t field_count)
{
    std::vector<DeviceColumnRuntimeField> runtime_fields;
    runtime_fields.reserve(field_count);
    for (size_t index = 0; index < field_count; ++index) {
        runtime_fields.push_back({fields[index].device_ptr, fields[index].kind, fields[index].dtype});
    }
    return runtime_fields;
}

static std::vector<DeviceColumnRuntimeClause> columnar_make_device_runtime_clauses(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        const RtdlColumnClause* clauses,
        size_t clause_count)
{
    std::vector<DeviceColumnRuntimeClause> runtime_clauses;
    runtime_clauses.reserve(clause_count);
    for (size_t index = 0; index < clause_count; ++index) {
        const RtdlColumnClause& clause = clauses[index];
        DeviceColumnRuntimeClause encoded{};
        encoded.field_index = static_cast<uint32_t>(
            columnar_device_payload_field_index_or_throw(fields, field_count, clause.field));
        encoded.op = clause.op;
        encoded.value_kind = clause.value.kind;
        encoded.int_value = clause.value.int_value;
        encoded.double_value = clause.value.double_value;
        encoded.int_value_hi = clause.value_hi.int_value;
        encoded.double_value_hi = clause.value_hi.double_value;
        runtime_clauses.push_back(encoded);
    }
    return runtime_clauses;
}

static void columnar_launch_device_column_grouped_i64(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        uint32_t operation,
        std::vector<RtdlGroupedCountRow>& count_rows,
        std::vector<RtdlGroupedSumRow>& sum_rows,
        std::vector<RtdlGroupedSumCountRow>& sum_count_rows,
        std::vector<RtdlGroupedStatsRow>& stats_rows,
        uint32_t* overflowed_out)
{
    if (overflowed_out) {
        *overflowed_out = 0u;
    }
    columnar_validate_device_payload_grouped_i64_inputs(
        fields, field_count, row_count, clauses, clause_count, group_key_field, value_field, group_capacity);

    const std::vector<DeviceColumnRuntimeField> runtime_fields =
        columnar_make_device_runtime_fields(fields, field_count);
    const std::vector<DeviceColumnRuntimeClause> runtime_clauses =
        columnar_make_device_runtime_clauses(fields, field_count, clauses, clause_count);
    const size_t group_index = columnar_device_payload_field_index_or_throw(fields, field_count, group_key_field);
    const size_t value_index = value_field
        ? columnar_device_payload_field_index_or_throw(fields, field_count, value_field)
        : group_index;

    std::call_once(g_device_column_grouped_i64.init, [&]() {
        const std::string ptx = compile_to_ptx(
            kDeviceColumnGroupedI64KernelSrc,
            "device_column_grouped_i64_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_device_column_grouped_i64.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(
            &g_device_column_grouped_i64.fn,
            g_device_column_grouped_i64.module,
            "device_column_grouped_i64_kernel"));
        CU_CHECK(cuModuleGetFunction(
            &g_device_column_grouped_i64.init_values_fn,
            g_device_column_grouped_i64.module,
            "device_column_grouped_i64_init_values_kernel"));
        CU_CHECK(cuModuleGetFunction(
            &g_device_column_grouped_i64.compact_count_fn,
            g_device_column_grouped_i64.module,
            "device_column_grouped_i64_compact_count_kernel"));
        CU_CHECK(cuModuleGetFunction(
            &g_device_column_grouped_i64.compact_sum_fn,
            g_device_column_grouped_i64.module,
            "device_column_grouped_i64_compact_sum_kernel"));
        CU_CHECK(cuModuleGetFunction(
            &g_device_column_grouped_i64.compact_sum_count_fn,
            g_device_column_grouped_i64.module,
            "device_column_grouped_i64_compact_sum_count_kernel"));
        CU_CHECK(cuModuleGetFunction(
            &g_device_column_grouped_i64.compact_stats_fn,
            g_device_column_grouped_i64.module,
            "device_column_grouped_i64_compact_stats_kernel"));
    });

    DevPtr d_fields(sizeof(DeviceColumnRuntimeField) * runtime_fields.size());
    upload(d_fields.ptr, runtime_fields.data(), runtime_fields.size());
    DevPtr d_clauses(sizeof(DeviceColumnRuntimeClause) * std::max<size_t>(runtime_clauses.size(), 1));
    if (!runtime_clauses.empty()) {
        upload(d_clauses.ptr, runtime_clauses.data(), runtime_clauses.size());
    }
    DevPtr d_counts(sizeof(unsigned long long) * group_capacity);
    DevPtr d_sums(sizeof(unsigned long long) * group_capacity);
    std::unique_ptr<DevPtr> d_mins;
    std::unique_ptr<DevPtr> d_maxs;
    DevPtr d_invalid(sizeof(uint32_t));
    CU_CHECK(cuMemsetD8(d_counts.ptr, 0, sizeof(unsigned long long) * group_capacity));
    CU_CHECK(cuMemsetD8(d_sums.ptr, 0, sizeof(unsigned long long) * group_capacity));
    CU_CHECK(cuMemsetD8(d_invalid.ptr, 0, sizeof(uint32_t)));
    const unsigned int threads = 256;
    const unsigned int compact_blocks = static_cast<unsigned int>((group_capacity + threads - 1) / threads);
    uint32_t runtime_group_capacity = static_cast<uint32_t>(group_capacity);
    if (operation == kDeviceColumnGroupedOpMin || operation == kDeviceColumnGroupedOpMax) {
        long long initial_value = operation == kDeviceColumnGroupedOpMin
            ? std::numeric_limits<int64_t>::max()
            : std::numeric_limits<int64_t>::min();
        void* init_args[] = {
            &d_sums.ptr,
            &runtime_group_capacity,
            &initial_value,
        };
        CU_CHECK(cuLaunchKernel(
            g_device_column_grouped_i64.init_values_fn,
            compact_blocks, 1, 1,
            threads, 1, 1,
            0, nullptr, init_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
    } else if (operation == kDeviceColumnGroupedOpStats) {
        d_mins = std::make_unique<DevPtr>(sizeof(unsigned long long) * group_capacity);
        d_maxs = std::make_unique<DevPtr>(sizeof(unsigned long long) * group_capacity);
        long long min_initial_value = std::numeric_limits<int64_t>::max();
        void* min_init_args[] = {
            &d_mins->ptr,
            &runtime_group_capacity,
            &min_initial_value,
        };
        CU_CHECK(cuLaunchKernel(
            g_device_column_grouped_i64.init_values_fn,
            compact_blocks, 1, 1,
            threads, 1, 1,
            0, nullptr, min_init_args, nullptr));
        long long max_initial_value = std::numeric_limits<int64_t>::min();
        void* max_init_args[] = {
            &d_maxs->ptr,
            &runtime_group_capacity,
            &max_initial_value,
        };
        CU_CHECK(cuLaunchKernel(
            g_device_column_grouped_i64.init_values_fn,
            compact_blocks, 1, 1,
            threads, 1, 1,
            0, nullptr, max_init_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
    }

    DeviceColumnGroupedI64Params params{};
    params.fields = reinterpret_cast<const DeviceColumnRuntimeField*>(d_fields.ptr);
    params.field_count = static_cast<uint32_t>(field_count);
    params.row_count = static_cast<uint32_t>(row_count);
    params.clauses = reinterpret_cast<const DeviceColumnRuntimeClause*>(d_clauses.ptr);
    params.clause_count = static_cast<uint32_t>(clause_count);
    params.group_field_index = static_cast<uint32_t>(group_index);
    params.value_field_index = static_cast<uint32_t>(value_index);
    params.operation = operation;
    params.group_capacity = runtime_group_capacity;
    params.group_counts = reinterpret_cast<unsigned long long*>(d_counts.ptr);
    params.group_sums = reinterpret_cast<unsigned long long*>(d_sums.ptr);
    params.group_mins = d_mins ? reinterpret_cast<unsigned long long*>(d_mins->ptr) : nullptr;
    params.group_maxs = d_maxs ? reinterpret_cast<unsigned long long*>(d_maxs->ptr) : nullptr;
    params.invalid_group_count = reinterpret_cast<uint32_t*>(d_invalid.ptr);

    void* args[] = {&params};
    const unsigned int blocks = static_cast<unsigned int>((row_count + threads - 1) / threads);
    CU_CHECK(cuLaunchKernel(
        g_device_column_grouped_i64.fn,
        blocks, 1, 1,
        threads, 1, 1,
        0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));

    uint32_t invalid_group_count = 0;
    download(&invalid_group_count, d_invalid.ptr, 1);
    if (invalid_group_count != 0) {
        if (!overflowed_out) {
            throw std::runtime_error("device-column grouped execution requires dense non-negative group keys below group_capacity");
        }
        *overflowed_out = 1u;
        return;
    }

    DevPtr d_row_count(sizeof(uint32_t));
    CU_CHECK(cuMemsetD8(d_row_count.ptr, 0, sizeof(uint32_t)));
    if (operation == kDeviceColumnGroupedOpCount) {
        DevPtr d_rows(sizeof(RtdlGroupedCountRow) * group_capacity);
        void* compact_args[] = {
            &d_counts.ptr,
            &params.group_capacity,
            &d_rows.ptr,
            &d_row_count.ptr,
        };
        CU_CHECK(cuLaunchKernel(
            g_device_column_grouped_i64.compact_count_fn,
            compact_blocks, 1, 1,
            threads, 1, 1,
            0, nullptr, compact_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        uint32_t compact_row_count = 0;
        download(&compact_row_count, d_row_count.ptr, 1);
        if (compact_row_count > group_capacity) {
            throw std::runtime_error("device-column grouped compact output row count exceeded group_capacity");
        }
        count_rows.resize(compact_row_count);
        if (compact_row_count != 0) {
            download(count_rows.data(), d_rows.ptr, compact_row_count);
        }
    } else if (operation == kDeviceColumnGroupedOpSumCount) {
        DevPtr d_rows(sizeof(RtdlGroupedSumCountRow) * group_capacity);
        void* compact_args[] = {
            &d_counts.ptr,
            &d_sums.ptr,
            &params.group_capacity,
            &d_rows.ptr,
            &d_row_count.ptr,
        };
        CU_CHECK(cuLaunchKernel(
            g_device_column_grouped_i64.compact_sum_count_fn,
            compact_blocks, 1, 1,
            threads, 1, 1,
            0, nullptr, compact_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        uint32_t compact_row_count = 0;
        download(&compact_row_count, d_row_count.ptr, 1);
        if (compact_row_count > group_capacity) {
            throw std::runtime_error("device-column grouped compact output row count exceeded group_capacity");
        }
        sum_count_rows.resize(compact_row_count);
        if (compact_row_count != 0) {
            download(sum_count_rows.data(), d_rows.ptr, compact_row_count);
        }
    } else if (operation == kDeviceColumnGroupedOpStats) {
        DevPtr d_rows(sizeof(RtdlGroupedStatsRow) * group_capacity);
        void* compact_args[] = {
            &d_counts.ptr,
            &d_sums.ptr,
            &d_mins->ptr,
            &d_maxs->ptr,
            &params.group_capacity,
            &d_rows.ptr,
            &d_row_count.ptr,
        };
        CU_CHECK(cuLaunchKernel(
            g_device_column_grouped_i64.compact_stats_fn,
            compact_blocks, 1, 1,
            threads, 1, 1,
            0, nullptr, compact_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        uint32_t compact_row_count = 0;
        download(&compact_row_count, d_row_count.ptr, 1);
        if (compact_row_count > group_capacity) {
            throw std::runtime_error("device-column grouped compact output row count exceeded group_capacity");
        }
        stats_rows.resize(compact_row_count);
        if (compact_row_count != 0) {
            download(stats_rows.data(), d_rows.ptr, compact_row_count);
        }
    } else {
        DevPtr d_rows(sizeof(RtdlGroupedSumRow) * group_capacity);
        void* compact_args[] = {
            &d_counts.ptr,
            &d_sums.ptr,
            &params.group_capacity,
            &d_rows.ptr,
            &d_row_count.ptr,
        };
        CU_CHECK(cuLaunchKernel(
            g_device_column_grouped_i64.compact_sum_fn,
            compact_blocks, 1, 1,
            threads, 1, 1,
            0, nullptr, compact_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        uint32_t compact_row_count = 0;
        download(&compact_row_count, d_row_count.ptr, 1);
        if (compact_row_count > group_capacity) {
            throw std::runtime_error("device-column grouped compact output row count exceeded group_capacity");
        }
        sum_rows.resize(compact_row_count);
        if (compact_row_count != 0) {
            download(sum_rows.data(), d_rows.ptr, compact_row_count);
        }
    }
}

static void run_device_column_grouped_count_i64_optix_with_capacity(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        size_t group_capacity,
        RtdlGroupedCountRow** rows_out,
        size_t* row_count_out,
        uint32_t* overflowed_out)
{
    if (!rows_out || !row_count_out || !overflowed_out) {
        throw std::runtime_error("rows_out, row_count_out, and overflowed_out must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    *overflowed_out = 0u;

    std::vector<RtdlGroupedCountRow> rows;
    std::vector<RtdlGroupedSumRow> unused_sum_rows;
    std::vector<RtdlGroupedSumCountRow> unused_sum_count_rows;
    std::vector<RtdlGroupedStatsRow> unused_stats_rows;
    columnar_launch_device_column_grouped_i64(
        fields, field_count, row_count, clauses, clause_count, group_key_field,
        nullptr, group_capacity, kDeviceColumnGroupedOpCount,
        rows, unused_sum_rows, unused_sum_count_rows, unused_stats_rows, overflowed_out);
    if (*overflowed_out != 0u) {
        return;
    }
    auto* out = static_cast<RtdlGroupedCountRow*>(std::malloc(sizeof(RtdlGroupedCountRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedCountRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_device_column_grouped_count_i64_optix(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        RtdlGroupedCountRow** rows_out,
        size_t* row_count_out)
{
    uint32_t overflowed = 0u;
    run_device_column_grouped_count_i64_optix_with_capacity(
        fields, field_count, row_count, clauses, clause_count, group_key_field,
        kColumnarMaxGroupsPerJob, rows_out, row_count_out, &overflowed);
    if (overflowed != 0u) {
        throw std::runtime_error("device-column grouped execution requires dense non-negative group keys below group_capacity");
    }
}

static void run_device_column_grouped_sum_i64_optix_with_capacity(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedSumRow** rows_out,
        size_t* row_count_out,
        uint32_t* overflowed_out)
{
    if (!rows_out || !row_count_out || !overflowed_out) {
        throw std::runtime_error("rows_out, row_count_out, and overflowed_out must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    *overflowed_out = 0u;

    std::vector<RtdlGroupedCountRow> unused_count_rows;
    std::vector<RtdlGroupedSumRow> rows;
    std::vector<RtdlGroupedSumCountRow> unused_sum_count_rows;
    std::vector<RtdlGroupedStatsRow> unused_stats_rows;
    columnar_launch_device_column_grouped_i64(
        fields, field_count, row_count, clauses, clause_count, group_key_field,
        value_field, group_capacity, kDeviceColumnGroupedOpSum,
        unused_count_rows, rows, unused_sum_count_rows, unused_stats_rows, overflowed_out);
    if (*overflowed_out != 0u) {
        return;
    }
    auto* out = static_cast<RtdlGroupedSumRow*>(std::malloc(sizeof(RtdlGroupedSumRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedSumRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_device_column_grouped_sum_i64_optix(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlGroupedSumRow** rows_out,
        size_t* row_count_out)
{
    uint32_t overflowed = 0u;
    run_device_column_grouped_sum_i64_optix_with_capacity(
        fields, field_count, row_count, clauses, clause_count, group_key_field, value_field,
        kColumnarMaxGroupsPerJob, rows_out, row_count_out, &overflowed);
    if (overflowed != 0u) {
        throw std::runtime_error("device-column grouped execution requires dense non-negative group keys below group_capacity");
    }
}

static void run_device_column_grouped_min_i64_optix_with_capacity(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedSumRow** rows_out,
        size_t* row_count_out,
        uint32_t* overflowed_out)
{
    if (!rows_out || !row_count_out || !overflowed_out) {
        throw std::runtime_error("rows_out, row_count_out, and overflowed_out must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    *overflowed_out = 0u;

    std::vector<RtdlGroupedCountRow> unused_count_rows;
    std::vector<RtdlGroupedSumRow> rows;
    std::vector<RtdlGroupedSumCountRow> unused_sum_count_rows;
    std::vector<RtdlGroupedStatsRow> unused_stats_rows;
    columnar_launch_device_column_grouped_i64(
        fields, field_count, row_count, clauses, clause_count, group_key_field,
        value_field, group_capacity, kDeviceColumnGroupedOpMin,
        unused_count_rows, rows, unused_sum_count_rows, unused_stats_rows, overflowed_out);
    if (*overflowed_out != 0u) {
        return;
    }
    auto* out = static_cast<RtdlGroupedSumRow*>(std::malloc(sizeof(RtdlGroupedSumRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedSumRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_device_column_grouped_max_i64_optix_with_capacity(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedSumRow** rows_out,
        size_t* row_count_out,
        uint32_t* overflowed_out)
{
    if (!rows_out || !row_count_out || !overflowed_out) {
        throw std::runtime_error("rows_out, row_count_out, and overflowed_out must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    *overflowed_out = 0u;

    std::vector<RtdlGroupedCountRow> unused_count_rows;
    std::vector<RtdlGroupedSumRow> rows;
    std::vector<RtdlGroupedSumCountRow> unused_sum_count_rows;
    std::vector<RtdlGroupedStatsRow> unused_stats_rows;
    columnar_launch_device_column_grouped_i64(
        fields, field_count, row_count, clauses, clause_count, group_key_field,
        value_field, group_capacity, kDeviceColumnGroupedOpMax,
        unused_count_rows, rows, unused_sum_count_rows, unused_stats_rows, overflowed_out);
    if (*overflowed_out != 0u) {
        return;
    }
    auto* out = static_cast<RtdlGroupedSumRow*>(std::malloc(sizeof(RtdlGroupedSumRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedSumRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_device_column_grouped_sum_count_i64_optix_with_capacity(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedSumCountRow** rows_out,
        size_t* row_count_out,
        uint32_t* overflowed_out)
{
    if (!rows_out || !row_count_out || !overflowed_out) {
        throw std::runtime_error("rows_out, row_count_out, and overflowed_out must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    *overflowed_out = 0u;

    std::vector<RtdlGroupedCountRow> unused_count_rows;
    std::vector<RtdlGroupedSumRow> unused_sum_rows;
    std::vector<RtdlGroupedSumCountRow> rows;
    std::vector<RtdlGroupedStatsRow> unused_stats_rows;
    columnar_launch_device_column_grouped_i64(
        fields, field_count, row_count, clauses, clause_count, group_key_field,
        value_field, group_capacity, kDeviceColumnGroupedOpSumCount,
        unused_count_rows, unused_sum_rows, rows, unused_stats_rows, overflowed_out);
    if (*overflowed_out != 0u) {
        return;
    }
    auto* out = static_cast<RtdlGroupedSumCountRow*>(
        std::malloc(sizeof(RtdlGroupedSumCountRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedSumCountRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_device_column_grouped_stats_i64_optix_with_capacity(
        const RtdlDevicePayloadField* fields,
        size_t field_count,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        size_t group_capacity,
        RtdlGroupedStatsRow** rows_out,
        size_t* row_count_out,
        uint32_t* overflowed_out)
{
    if (!rows_out || !row_count_out || !overflowed_out) {
        throw std::runtime_error("rows_out, row_count_out, and overflowed_out must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    *overflowed_out = 0u;

    std::vector<RtdlGroupedCountRow> unused_count_rows;
    std::vector<RtdlGroupedSumRow> unused_sum_rows;
    std::vector<RtdlGroupedSumCountRow> unused_sum_count_rows;
    std::vector<RtdlGroupedStatsRow> rows;
    columnar_launch_device_column_grouped_i64(
        fields, field_count, row_count, clauses, clause_count, group_key_field,
        value_field, group_capacity, kDeviceColumnGroupedOpStats,
        unused_count_rows, unused_sum_rows, unused_sum_count_rows, rows, overflowed_out);
    if (*overflowed_out != 0u) {
        return;
    }
    auto* out = static_cast<RtdlGroupedStatsRow*>(
        std::malloc(sizeof(RtdlGroupedStatsRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedStatsRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void columnar_copy_dataset_from_payload_fields(
        OptixColumnarPayloadImpl& dataset,
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
        if (fields[field_index].kind == kColumnKindText) {
            string_count += row_count;
        }
    }
    dataset.scalar_strings.reserve(string_count);
    dataset.row_values.reserve(row_count * field_count);
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        for (size_t field_index = 0; field_index < field_count; ++field_index) {
            const RtdlPayloadField& field = fields[field_index];
            RtdlColumnScalar value{};
            value.kind = field.kind;
            if (field.kind == kColumnKindFloat64) {
                value.double_value = field.double_values[row_index];
            } else if (field.kind == kColumnKindText) {
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

static void columnar_validate_row_payload_inputs(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count)
{
    if (!fields || field_count == 0 || !row_values) {
        throw std::runtime_error("columnar table inputs must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("columnar clause pointer must not be null when clause_count > 0");
    }
    if (row_count > kColumnarMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX columnar lowering supports at most 1000000 rows per RT job");
    }
}

static std::vector<size_t> columnar_collect_candidate_row_indices_optix(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count)
{
    std::vector<ColumnarPrimaryAxis> axes;
    axes.reserve(std::min<size_t>(clause_count, 3));
    for (size_t i = 0; i < clause_count && i < 3; ++i) {
        axes.push_back(columnar_make_primary_axis(fields, field_count, row_values, row_count, clauses[i]));
    }
    const std::vector<OptixAabb> aabbs = columnar_build_row_aabbs(fields, field_count, row_values, row_count, axes);

    const uint32_t x_lo = axes.size() >= 1 ? static_cast<uint32_t>(axes[0].encoded_lo) : 1u;
    const uint32_t x_hi = axes.size() >= 1 ? static_cast<uint32_t>(axes[0].encoded_hi) : 1u;
    const uint32_t y_lo = axes.size() >= 2 ? static_cast<uint32_t>(axes[1].encoded_lo) : 1u;
    const uint32_t y_hi = axes.size() >= 2 ? static_cast<uint32_t>(axes[1].encoded_hi) : 1u;
    const uint32_t z_lo = axes.size() >= 3 ? static_cast<uint32_t>(axes[2].encoded_lo) : 1u;
    const uint32_t z_hi = axes.size() >= 3 ? static_cast<uint32_t>(axes[2].encoded_hi) : 1u;

    if (x_lo > x_hi || y_lo > y_hi || z_lo > z_hi) {
        return {};
    }

    std::call_once(g_columnar_predicate_scan.init, [&]() {
        std::string ptx = compile_to_ptx(
            kColumnarPredicateScanKernelSrc,
            "columnar_predicate_scan_kernel.cu");
        g_columnar_predicate_scan.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__columnar_predicate_scan_probe",
            "__miss__columnar_predicate_scan_miss",
            "__intersection__columnar_predicate_scan_isect",
            "__anyhit__columnar_predicate_scan_anyhit",
            nullptr,
            0).release();
    });

    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);

    const uint32_t hit_word_count = static_cast<uint32_t>((row_count + 31u) / 32u);
    DevPtr d_hit_words(sizeof(uint32_t) * hit_word_count);
    CU_CHECK(cuMemsetD8(d_hit_words.ptr, 0, sizeof(uint32_t) * hit_word_count));

    const uint32_t x_count = x_hi - x_lo + 1u;
    const uint32_t y_count = y_hi - y_lo + 1u;
    ColumnarPredicateScanLaunchParams lp;
    lp.traversable = accel.handle;
    lp.hit_words = reinterpret_cast<uint32_t*>(d_hit_words.ptr);
    lp.hit_word_count = hit_word_count;
    lp.x_lo = x_lo;
    lp.y_lo = y_lo;
    lp.z_lo = z_lo;
    lp.z_hi = z_hi;
    lp.x_count = x_count;
    lp.y_count = y_count;

    DevPtr d_params(sizeof(ColumnarPredicateScanLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(
        g_columnar_predicate_scan.pipe->pipeline,
        stream,
        d_params.ptr,
        sizeof(ColumnarPredicateScanLaunchParams),
        &g_columnar_predicate_scan.pipe->sbt,
        x_count,
        y_count,
        1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<uint32_t> hit_words(hit_word_count, 0u);
    if (hit_word_count > 0) {
        download(hit_words.data(), d_hit_words.ptr, hit_word_count);
    }

    std::vector<size_t> row_indices;
    row_indices.reserve(std::min(row_count, kColumnarMaxCandidateRowsPerJob));
    for (size_t row_index = 0; row_index < row_count; ++row_index) {
        const uint32_t word = static_cast<uint32_t>(row_index >> 5);
        const uint32_t bit = 1u << (row_index & 31u);
        if ((hit_words[word] & bit) == 0u) {
            continue;
        }
        if (row_indices.size() >= kColumnarMaxCandidateRowsPerJob) {
            throw std::runtime_error("first-wave OptiX columnar lowering exceeded the 1000000-candidate ceiling");
        }
        if (!columnar_row_matches_all_clauses(fields, field_count, row_values, row_index, clauses, clause_count)) {
            continue;
        }
        row_indices.push_back(row_index);
    }
    return row_indices;
}

static std::vector<size_t> columnar_collect_candidate_row_indices_optix_prepared(
        const OptixColumnarPayloadImpl& dataset,
        const RtdlColumnClause* clauses,
        size_t clause_count)
{
    const std::vector<ColumnarPrimaryAxis> axes = columnar_dataset_query_axes(dataset, clauses, clause_count);
    const uint32_t x_lo = axes.size() >= 1 ? static_cast<uint32_t>(axes[0].encoded_lo) : 1u;
    const uint32_t x_hi = axes.size() >= 1 ? static_cast<uint32_t>(axes[0].encoded_hi) : 1u;
    const uint32_t y_lo = axes.size() >= 2 ? static_cast<uint32_t>(axes[1].encoded_lo) : 1u;
    const uint32_t y_hi = axes.size() >= 2 ? static_cast<uint32_t>(axes[1].encoded_hi) : 1u;
    const uint32_t z_lo = axes.size() >= 3 ? static_cast<uint32_t>(axes[2].encoded_lo) : 1u;
    const uint32_t z_hi = axes.size() >= 3 ? static_cast<uint32_t>(axes[2].encoded_hi) : 1u;

    if (x_lo > x_hi || y_lo > y_hi || z_lo > z_hi) {
        return {};
    }

    std::call_once(g_columnar_predicate_scan.init, [&]() {
        std::string ptx = compile_to_ptx(
            kColumnarPredicateScanKernelSrc,
            "columnar_predicate_scan_kernel.cu");
        g_columnar_predicate_scan.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__columnar_predicate_scan_probe",
            "__miss__columnar_predicate_scan_miss",
            "__intersection__columnar_predicate_scan_isect",
            "__anyhit__columnar_predicate_scan_anyhit",
            nullptr,
            0).release();
    });

    const uint32_t hit_word_count = static_cast<uint32_t>((dataset.row_count + 31u) / 32u);
    DevPtr d_hit_words(sizeof(uint32_t) * hit_word_count);
    CU_CHECK(cuMemsetD8(d_hit_words.ptr, 0, sizeof(uint32_t) * hit_word_count));

    const uint32_t x_count = x_hi - x_lo + 1u;
    const uint32_t y_count = y_hi - y_lo + 1u;
    ColumnarPredicateScanLaunchParams lp;
    lp.traversable = dataset.accel.handle;
    lp.hit_words = reinterpret_cast<uint32_t*>(d_hit_words.ptr);
    lp.hit_word_count = hit_word_count;
    lp.x_lo = x_lo;
    lp.y_lo = y_lo;
    lp.z_lo = z_lo;
    lp.z_hi = z_hi;
    lp.x_count = x_count;
    lp.y_count = y_count;

    DevPtr d_params(sizeof(ColumnarPredicateScanLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(
        g_columnar_predicate_scan.pipe->pipeline,
        stream,
        d_params.ptr,
        sizeof(ColumnarPredicateScanLaunchParams),
        &g_columnar_predicate_scan.pipe->sbt,
        x_count,
        y_count,
        1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_columnar_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();

    auto t_start_copy = std::chrono::steady_clock::now();
    std::vector<uint32_t> hit_words(hit_word_count, 0u);
    if (hit_word_count > 0) {
        download(hit_words.data(), d_hit_words.ptr, hit_word_count);
    }
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_columnar_bitset_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();

    auto t_start_filter = std::chrono::steady_clock::now();
    size_t raw_candidate_count = 0;
    std::vector<size_t> row_indices;
    row_indices.reserve(std::min(dataset.row_count, kColumnarMaxCandidateRowsPerJob));
    for (size_t row_index = 0; row_index < dataset.row_count; ++row_index) {
        const uint32_t word = static_cast<uint32_t>(row_index >> 5);
        const uint32_t bit = 1u << (row_index & 31u);
        if ((hit_words[word] & bit) == 0u) {
            continue;
        }
        raw_candidate_count += 1;
        if (row_indices.size() >= kColumnarMaxCandidateRowsPerJob) {
            throw std::runtime_error("first-wave OptiX columnar lowering exceeded the 1000000-candidate ceiling");
        }
        if (!columnar_row_matches_all_clauses(
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
    g_optix_last_columnar_exact_filter_s = std::chrono::duration<double>(t_end_filter - t_start_filter).count();
    g_optix_last_columnar_raw_candidate_count = raw_candidate_count;
    g_optix_last_columnar_emitted_count = row_indices.size();
    return row_indices;
}

static void run_columnar_multi_predicate_scan_optix(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        RtdlColumnRowIdRow** rows_out,
        size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (!fields || field_count == 0 || !row_values) {
        throw std::runtime_error("columnar table inputs must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("columnar clause pointer must not be null when clause_count > 0");
    }
    if (row_count > kColumnarMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX columnar lowering supports at most 1000000 rows per RT job");
    }
    const std::vector<ColumnarRowMeta> row_metas = columnar_build_row_metas(fields, field_count, row_values, row_count);
    const std::vector<size_t> candidate_row_indices =
        columnar_collect_candidate_row_indices_optix(fields, field_count, row_values, row_count, clauses, clause_count);
    std::vector<RtdlColumnRowIdRow> rows;
    rows.reserve(candidate_row_indices.size());
    for (size_t row_index : candidate_row_indices) {
        rows.push_back({row_metas[row_index].row_id});
    }

    std::sort(rows.begin(), rows.end(), [](const RtdlColumnRowIdRow& left, const RtdlColumnRowIdRow& right) {
        return left.row_id < right.row_id;
    });

    auto* out = static_cast<RtdlColumnRowIdRow*>(std::malloc(sizeof(RtdlColumnRowIdRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlColumnRowIdRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_columnar_grouped_count_optix(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        RtdlGroupedCountRow** rows_out,
        size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (!fields || field_count == 0 || !row_values || !group_key_field) {
        throw std::runtime_error("columnar grouped_count inputs must not be null");
    }
    if (row_count > kColumnarMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX columnar lowering supports at most 1000000 rows per RT job");
    }
    const size_t group_field_index = columnar_find_field_index_or_throw(fields, field_count, group_key_field);
    const std::vector<size_t> candidate_row_indices =
        columnar_collect_candidate_row_indices_optix(fields, field_count, row_values, row_count, clauses, clause_count);
    std::unordered_map<int64_t, int64_t> counts;
    for (size_t row_index : candidate_row_indices) {
        const RtdlColumnScalar& group_value = columnar_row_value(row_values, row_index, field_count, group_field_index);
        counts[group_value.int_value] += 1;
        if (counts.size() > kColumnarMaxGroupsPerJob) {
            throw std::runtime_error("first-wave OptiX columnar grouped kernels exceeded the 65536-group ceiling");
        }
    }
    std::vector<RtdlGroupedCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& entry : counts) {
        rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlGroupedCountRow& left, const RtdlGroupedCountRow& right) {
        return left.group_key < right.group_key;
    });
    auto* out = static_cast<RtdlGroupedCountRow*>(std::malloc(sizeof(RtdlGroupedCountRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedCountRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_columnar_grouped_sum_optix(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlGroupedSumRow** rows_out,
        size_t* row_count_out)
{
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (!fields || field_count == 0 || !row_values || !group_key_field || !value_field) {
        throw std::runtime_error("columnar grouped_sum inputs must not be null");
    }
    if (row_count > kColumnarMaxRowsPerJob) {
        throw std::runtime_error("first-wave OptiX columnar lowering supports at most 1000000 rows per RT job");
    }
    const size_t group_field_index = columnar_find_field_index_or_throw(fields, field_count, group_key_field);
    const size_t value_field_index = columnar_find_field_index_or_throw(fields, field_count, value_field);
    if (fields[value_field_index].kind != kColumnKindInt64 && fields[value_field_index].kind != kColumnKindBool) {
        throw std::runtime_error("first-wave OptiX grouped_sum supports integer-compatible value fields only");
    }
    const std::vector<size_t> candidate_row_indices =
        columnar_collect_candidate_row_indices_optix(fields, field_count, row_values, row_count, clauses, clause_count);
    std::unordered_map<int64_t, int64_t> sums;
    for (size_t row_index : candidate_row_indices) {
        const RtdlColumnScalar& group_value = columnar_row_value(row_values, row_index, field_count, group_field_index);
        const RtdlColumnScalar& sum_value = columnar_row_value(row_values, row_index, field_count, value_field_index);
        sums[group_value.int_value] += sum_value.int_value;
        if (sums.size() > kColumnarMaxGroupsPerJob) {
            throw std::runtime_error("first-wave OptiX columnar grouped kernels exceeded the 65536-group ceiling");
        }
    }
    std::vector<RtdlGroupedSumRow> rows;
    rows.reserve(sums.size());
    for (const auto& entry : sums) {
        rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlGroupedSumRow& left, const RtdlGroupedSumRow& right) {
        return left.group_key < right.group_key;
    });
    auto* out = static_cast<RtdlGroupedSumRow*>(std::malloc(sizeof(RtdlGroupedSumRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedSumRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
}

static OptixColumnarPayloadImpl* create_columnar_payload_optix(
        const RtdlColumnField* fields,
        size_t field_count,
        const RtdlColumnScalar* row_values,
        size_t row_count,
        const char* const* primary_fields,
        size_t primary_field_count)
{
    columnar_validate_row_payload_inputs(fields, field_count, row_values, row_count, nullptr, 0);
    std::unique_ptr<OptixColumnarPayloadImpl> dataset(new OptixColumnarPayloadImpl());
    columnar_copy_dataset_payload(*dataset, fields, field_count, row_values, row_count);

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
        primary_names = columnar_default_primary_fields(dataset->fields.data(), dataset->fields.size());
    }
    if (primary_names.empty()) {
        throw std::runtime_error("OptiX prepared columnar payload requires at least one numeric primary RT axis");
    }

    dataset->primary_axes.reserve(primary_names.size());
    for (const char* field_name : primary_names) {
        dataset->primary_axes.push_back(
            columnar_make_full_primary_axis(
                dataset->fields.data(),
                dataset->fields.size(),
                dataset->row_values.data(),
                dataset->row_count,
                field_name));
    }
    dataset->row_metas = columnar_build_row_metas(
        dataset->fields.data(),
        dataset->fields.size(),
        dataset->row_values.data(),
        dataset->row_count);
    dataset->aabbs = columnar_build_row_aabbs(
        dataset->fields.data(),
        dataset->fields.size(),
        dataset->row_values.data(),
        dataset->row_count,
        dataset->primary_axes);
    dataset->accel = build_custom_accel(get_optix_context(), dataset->aabbs);
    return dataset.release();
}

static OptixColumnarPayloadImpl* create_columnar_payload_optix_from_columns(
        const RtdlPayloadField* fields,
        size_t field_count,
        size_t row_count,
        const char* const* primary_fields,
        size_t primary_field_count)
{
    columnar_validate_payload_fields(fields, field_count, row_count);
    std::unique_ptr<OptixColumnarPayloadImpl> dataset(new OptixColumnarPayloadImpl());
    columnar_copy_dataset_from_payload_fields(*dataset, fields, field_count, row_count);

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
        primary_names = columnar_default_primary_fields(dataset->fields.data(), dataset->fields.size());
    }
    if (primary_names.empty()) {
        throw std::runtime_error("OptiX prepared columnar payload requires at least one numeric primary RT axis");
    }

    dataset->primary_axes.reserve(primary_names.size());
    for (const char* field_name : primary_names) {
        dataset->primary_axes.push_back(
            columnar_make_full_primary_axis(
                dataset->fields.data(),
                dataset->fields.size(),
                dataset->row_values.data(),
                dataset->row_count,
                field_name));
    }
    dataset->row_metas = columnar_build_row_metas(
        dataset->fields.data(),
        dataset->fields.size(),
        dataset->row_values.data(),
        dataset->row_count);
    dataset->aabbs = columnar_build_row_aabbs(
        dataset->fields.data(),
        dataset->fields.size(),
        dataset->row_values.data(),
        dataset->row_count,
        dataset->primary_axes);
    dataset->accel = build_custom_accel(get_optix_context(), dataset->aabbs);
    return dataset.release();
}

static void run_columnar_multi_predicate_scan_optix_prepared(
        OptixColumnarPayloadImpl* dataset,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        RtdlColumnRowIdRow** rows_out,
        size_t* row_count_out)
{
    if (!dataset) {
        throw std::runtime_error("OptiX prepared columnar payload must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("columnar clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    const std::vector<size_t> candidate_row_indices =
        columnar_collect_candidate_row_indices_optix_prepared(*dataset, clauses, clause_count);
    auto t_start_output = std::chrono::steady_clock::now();
    std::vector<RtdlColumnRowIdRow> rows;
    rows.reserve(candidate_row_indices.size());
    for (size_t row_index : candidate_row_indices) {
        rows.push_back({dataset->row_metas[row_index].row_id});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlColumnRowIdRow& left, const RtdlColumnRowIdRow& right) {
        return left.row_id < right.row_id;
    });
    auto* out = static_cast<RtdlColumnRowIdRow*>(std::malloc(sizeof(RtdlColumnRowIdRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlColumnRowIdRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
    auto t_end_output = std::chrono::steady_clock::now();
    g_optix_last_columnar_output_pack_s = std::chrono::duration<double>(t_end_output - t_start_output).count();
    g_optix_last_columnar_emitted_count = rows.size();
}

static void run_columnar_multi_predicate_scan_count_optix_prepared(
        OptixColumnarPayloadImpl* dataset,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        size_t* row_count_out)
{
    if (!dataset) {
        throw std::runtime_error("OptiX prepared columnar payload must not be null");
    }
    if (!row_count_out) {
        throw std::runtime_error("row_count_out pointer must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("columnar clause pointer must not be null when clause_count > 0");
    }
    *row_count_out = 0;

    const std::vector<size_t> candidate_row_indices =
        columnar_collect_candidate_row_indices_optix_prepared(*dataset, clauses, clause_count);
    auto t_start_output = std::chrono::steady_clock::now();
    *row_count_out = candidate_row_indices.size();
    auto t_end_output = std::chrono::steady_clock::now();
    g_optix_last_columnar_output_pack_s = std::chrono::duration<double>(t_end_output - t_start_output).count();
    g_optix_last_columnar_emitted_count = candidate_row_indices.size();
}

static void run_columnar_grouped_count_optix_prepared(
        OptixColumnarPayloadImpl* dataset,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        RtdlGroupedCountRow** rows_out,
        size_t* row_count_out)
{
    if (!dataset) {
        throw std::runtime_error("OptiX prepared columnar payload must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    if (!group_key_field) {
        throw std::runtime_error("group_key_field must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("columnar clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    const size_t group_field_index =
        columnar_find_field_index_or_throw(dataset->fields.data(), dataset->fields.size(), group_key_field);
    const std::vector<size_t> candidate_row_indices =
        columnar_collect_candidate_row_indices_optix_prepared(*dataset, clauses, clause_count);
    auto t_start_output = std::chrono::steady_clock::now();
    std::unordered_map<int64_t, int64_t> counts;
    for (size_t row_index : candidate_row_indices) {
        const RtdlColumnScalar& group_value =
            columnar_row_value(dataset->row_values.data(), row_index, dataset->fields.size(), group_field_index);
        counts[group_value.int_value] += 1;
        if (counts.size() > kColumnarMaxGroupsPerJob) {
            throw std::runtime_error("first-wave OptiX columnar grouped kernels exceeded the 65536-group ceiling");
        }
    }
    std::vector<RtdlGroupedCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& entry : counts) {
        rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlGroupedCountRow& left, const RtdlGroupedCountRow& right) {
        return left.group_key < right.group_key;
    });
    auto* out = static_cast<RtdlGroupedCountRow*>(std::malloc(sizeof(RtdlGroupedCountRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedCountRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
    auto t_end_output = std::chrono::steady_clock::now();
    g_optix_last_columnar_output_pack_s = std::chrono::duration<double>(t_end_output - t_start_output).count();
    g_optix_last_columnar_emitted_count = rows.size();
}

static void run_columnar_grouped_sum_optix_prepared(
        OptixColumnarPayloadImpl* dataset,
        const RtdlColumnClause* clauses,
        size_t clause_count,
        const char* group_key_field,
        const char* value_field,
        RtdlGroupedSumRow** rows_out,
        size_t* row_count_out)
{
    if (!dataset) {
        throw std::runtime_error("OptiX prepared columnar payload must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("output pointers must not be null");
    }
    if (!group_key_field || !value_field) {
        throw std::runtime_error("group_key_field and value_field must not be null");
    }
    if (clause_count > 0 && !clauses) {
        throw std::runtime_error("columnar clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    const size_t group_field_index =
        columnar_find_field_index_or_throw(dataset->fields.data(), dataset->fields.size(), group_key_field);
    const size_t value_field_index =
        columnar_find_field_index_or_throw(dataset->fields.data(), dataset->fields.size(), value_field);
    if (dataset->fields[value_field_index].kind != kColumnKindInt64
            && dataset->fields[value_field_index].kind != kColumnKindBool) {
        throw std::runtime_error("first-wave OptiX grouped_sum supports integer-compatible value fields only");
    }
    const std::vector<size_t> candidate_row_indices =
        columnar_collect_candidate_row_indices_optix_prepared(*dataset, clauses, clause_count);
    auto t_start_output = std::chrono::steady_clock::now();
    std::unordered_map<int64_t, int64_t> sums;
    for (size_t row_index : candidate_row_indices) {
        const RtdlColumnScalar& group_value =
            columnar_row_value(dataset->row_values.data(), row_index, dataset->fields.size(), group_field_index);
        const RtdlColumnScalar& sum_value =
            columnar_row_value(dataset->row_values.data(), row_index, dataset->fields.size(), value_field_index);
        sums[group_value.int_value] += sum_value.int_value;
        if (sums.size() > kColumnarMaxGroupsPerJob) {
            throw std::runtime_error("first-wave OptiX columnar grouped kernels exceeded the 65536-group ceiling");
        }
    }
    std::vector<RtdlGroupedSumRow> rows;
    rows.reserve(sums.size());
    for (const auto& entry : sums) {
        rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlGroupedSumRow& left, const RtdlGroupedSumRow& right) {
        return left.group_key < right.group_key;
    });
    auto* out = static_cast<RtdlGroupedSumRow*>(std::malloc(sizeof(RtdlGroupedSumRow) * rows.size()));
    if (!out && !rows.empty()) {
        throw std::bad_alloc();
    }
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlGroupedSumRow) * rows.size());
    }
    *rows_out = out;
    *row_count_out = rows.size();
    auto t_end_output = std::chrono::steady_clock::now();
    g_optix_last_columnar_output_pack_s = std::chrono::duration<double>(t_end_output - t_start_output).count();
    g_optix_last_columnar_emitted_count = rows.size();
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
    uint32_t          left_offset;
};

struct SegmentFirstHitLaunchParams {
    OptixTraversableHandle traversable;
    const GpuSegment* probes;
    const GpuSegment* primitives;
    uint64_t* best_pair;
    uint32_t probe_count;
};

struct PreparedSegmentPairIntersectionBuild {
    std::vector<GpuSegment> right_segments;
    std::vector<RtdlSegment> host_right_segments;
    std::unordered_map<uint32_t, const RtdlSegment*> right_by_id;
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
            right_by_id.reserve(count);
            for (size_t i = 0; i < count; ++i) {
                right_by_id.emplace(host_right_segments[i].id, &host_right_segments[i]);
            }
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

static void ensure_segment_first_hit_pipeline() {
    std::call_once(g_segment_first_hit.init, [&]() {
        std::string ptx = compile_to_ptx(kSegmentFirstHitKernelSrc, "segment_first_hit_kernel.cu");
        g_segment_first_hit.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__segment_first_hit_probe",
            "__miss__segment_first_hit_miss",
            "__intersection__segment_first_hit_isect",
            "__anyhit__segment_first_hit_anyhit",
            nullptr,
            4).release();
    });
}

static void finalize_segment_pair_intersection_rows(
        const RtdlSegment* left, size_t left_count,
        const RtdlSegment* right, size_t right_count,
        const std::vector<GpuSegmentPairIntersectionRecord>& gpu_rows,
        RtdlSegmentPairIntersectionRow** rows_out,
        size_t* row_count_out,
        const std::unordered_map<uint32_t, const RtdlSegment*>* prepared_right_by_id = nullptr)
{
    std::unordered_map<uint32_t, const RtdlSegment*> left_by_id;
    left_by_id.reserve(left_count);
    for (size_t i = 0; i < left_count; ++i) {
        left_by_id.emplace(left[i].id, &left[i]);
    }
    std::unordered_map<uint32_t, const RtdlSegment*> local_right_by_id;
    const std::unordered_map<uint32_t, const RtdlSegment*>* right_lookup = prepared_right_by_id;
    if (!right_lookup) {
        local_right_by_id.reserve(right_count);
        for (size_t i = 0; i < right_count; ++i) {
            local_right_by_id.emplace(right[i].id, &right[i]);
        }
        right_lookup = &local_right_by_id;
    }

    std::vector<RtdlSegmentPairIntersectionRow> refined;
    refined.reserve(gpu_rows.size());
    std::unordered_set<uint64_t> seen_pairs;
    seen_pairs.reserve(gpu_rows.size() * 2 + 1);

    for (const auto& gpu_row : gpu_rows) {
        const RtdlSegment* left_seg = nullptr;
        const RtdlSegment* right_seg = nullptr;
        if (gpu_row.left_index < left_count && gpu_row.right_index < right_count) {
            left_seg = &left[gpu_row.left_index];
            right_seg = &right[gpu_row.right_index];
        } else {
            const auto left_it = left_by_id.find(gpu_row.left_id);
            const auto right_it = right_lookup->find(gpu_row.right_id);
            if (left_it == left_by_id.end() || right_it == right_lookup->end()) {
                continue;
            }
            left_seg = left_it->second;
            right_seg = right_it->second;
        }
        const uint64_t pair_key =
            (static_cast<uint64_t>(left_seg->id) << 32) |
            static_cast<uint64_t>(right_seg->id);
        if (seen_pairs.find(pair_key) != seen_pairs.end()) {
            continue;
        }
        double ix = 0.0;
        double iy = 0.0;
        if (!exact_segment_intersection(*left_seg, *right_seg, &ix, &iy)) {
            continue;
        }
        seen_pairs.insert(pair_key);
        refined.push_back(
            RtdlSegmentPairIntersectionRow{
                left_seg->id,
                right_seg->id,
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

static size_t count_segment_pair_intersection_rows(
        const RtdlSegment* left, size_t left_count,
        const RtdlSegment* right, size_t right_count,
        const std::vector<GpuSegmentPairIntersectionRecord>& gpu_rows,
        const std::unordered_map<uint32_t, const RtdlSegment*>* prepared_right_by_id = nullptr)
{
    std::unordered_map<uint32_t, const RtdlSegment*> left_by_id;
    left_by_id.reserve(left_count);
    for (size_t i = 0; i < left_count; ++i) {
        left_by_id.emplace(left[i].id, &left[i]);
    }
    std::unordered_map<uint32_t, const RtdlSegment*> local_right_by_id;
    const std::unordered_map<uint32_t, const RtdlSegment*>* right_lookup = prepared_right_by_id;
    if (!right_lookup) {
        local_right_by_id.reserve(right_count);
        for (size_t i = 0; i < right_count; ++i) {
            local_right_by_id.emplace(right[i].id, &right[i]);
        }
        right_lookup = &local_right_by_id;
    }

    size_t exact_count = 0;
    std::unordered_set<uint64_t> seen_pairs;
    seen_pairs.reserve(gpu_rows.size() * 2 + 1);

    for (const auto& gpu_row : gpu_rows) {
        const RtdlSegment* left_seg = nullptr;
        const RtdlSegment* right_seg = nullptr;
        if (gpu_row.left_index < left_count && gpu_row.right_index < right_count) {
            left_seg = &left[gpu_row.left_index];
            right_seg = &right[gpu_row.right_index];
        } else {
            const auto left_it = left_by_id.find(gpu_row.left_id);
            const auto right_it = right_lookup->find(gpu_row.right_id);
            if (left_it == left_by_id.end() || right_it == right_lookup->end()) {
                continue;
            }
            left_seg = left_it->second;
            right_seg = right_it->second;
        }
        const uint64_t pair_key =
            (static_cast<uint64_t>(left_seg->id) << 32) |
            static_cast<uint64_t>(right_seg->id);
        if (seen_pairs.find(pair_key) != seen_pairs.end()) {
            continue;
        }
        double ix = 0.0;
        double iy = 0.0;
        if (!exact_segment_intersection(*left_seg, *right_seg, &ix, &iy)) {
            continue;
        }
        seen_pairs.insert(pair_key);
        ++exact_count;
    }
    return exact_count;
}

static std::vector<uint64_t> collect_segment_first_hits_optix(
        const RtdlSegment* probes,
        size_t probe_count,
        CUdeviceptr d_probe_ptr,
        CUdeviceptr d_primitive_ptr,
        size_t primitive_count,
        OptixTraversableHandle traversable)
{
    if (probe_count == 0 || primitive_count == 0) {
        return {};
    }
    if (probe_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
        throw std::runtime_error("segment first-hit probe count exceeds uint32_t launch capacity");
    }
    (void)probes;
    DevPtr d_best(sizeof(uint64_t) * probe_count);
    CU_CHECK(cuMemsetD8(d_best.ptr, 0xFF, sizeof(uint64_t) * probe_count));

    SegmentFirstHitLaunchParams lp;
    lp.traversable = traversable;
    lp.probes = reinterpret_cast<const GpuSegment*>(d_probe_ptr);
    lp.primitives = reinterpret_cast<const GpuSegment*>(d_primitive_ptr);
    lp.best_pair = reinterpret_cast<uint64_t*>(d_best.ptr);
    lp.probe_count = static_cast<uint32_t>(probe_count);

    DevPtr d_params(sizeof(SegmentFirstHitLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    const auto t_launch_start = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_segment_first_hit.pipe->pipeline, stream,
                             d_params.ptr, sizeof(SegmentFirstHitLaunchParams),
                             &g_segment_first_hit.pipe->sbt,
                             static_cast<unsigned>(probe_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    const auto t_launch_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_candidate_count_s +=
        std::chrono::duration<double>(t_launch_end - t_launch_start).count();
    g_optix_last_segment_pair_raw_candidate_count += probe_count;

    std::vector<uint64_t> best(probe_count, std::numeric_limits<uint64_t>::max());
    const auto t_download_start = std::chrono::steady_clock::now();
    download(best.data(), d_best.ptr, probe_count);
    const auto t_download_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_candidate_download_s +=
        std::chrono::duration<double>(t_download_end - t_download_start).count();
    return best;
}

static std::vector<RtdlSegmentFirstHitRow> materialize_segment_first_hit_rows(
        const RtdlSegment* probes,
        size_t probe_count,
        const PreparedSegmentPairIntersectionBuild& prepared,
        const std::vector<uint64_t>& best_pairs)
{
    std::vector<RtdlSegmentFirstHitRow> refined;
    refined.reserve(best_pairs.size());
    const std::vector<RtdlSegment>& primitives = prepared.host_right_segments;
    const uint64_t no_hit = std::numeric_limits<uint64_t>::max();
    for (size_t probe_index = 0; probe_index < probe_count && probe_index < best_pairs.size(); ++probe_index) {
        const RtdlSegment& probe = probes[probe_index];
        uint64_t pair = best_pairs[probe_index];
        if (pair == no_hit) {
            continue;
        }
        size_t primitive_index = static_cast<size_t>(pair & 0xffffffffull);
        if (primitive_index >= primitives.size()) {
            continue;
        }
        const uint32_t t_key = static_cast<uint32_t>(pair >> 32);
        if (t_key == 0u) {
            continue;
        }
        const double hit_t = std::clamp(
            (static_cast<double>(t_key) - 1.0) / 4294967294.0,
            0.0,
            1.0);
        const double ix = probe.x0 + hit_t * (probe.x1 - probe.x0);
        const double iy = probe.y0 + hit_t * (probe.y1 - probe.y0);
        refined.push_back(RtdlSegmentFirstHitRow{
            probe.id,
            primitives[primitive_index].id,
            ix,
            iy,
            hit_t,
        });
    }
    return refined;
}

static std::vector<GpuSegmentPairIntersectionRecord> collect_segment_pair_intersection_candidates_optix(
        size_t left_count,
        CUdeviceptr d_left_ptr,
        CUdeviceptr d_right_ptr,
        size_t right_count,
        OptixTraversableHandle traversable)
{
    if (left_count == 0 || right_count == 0) {
        return {};
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
        lp.probe_count = static_cast<uint32_t>(chunk_left_count);
        if (left_offset > static_cast<size_t>(std::numeric_limits<uint32_t>::max()) ||
            chunk_left_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()) - left_offset) {
            throw std::runtime_error("segment-pair intersection direct candidate index exceeds uint32_t");
        }
        lp.left_offset = static_cast<uint32_t>(left_offset);

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
        const auto t_count_start = std::chrono::steady_clock::now();
        const uint32_t gpu_count = launch_candidate_pass(left_offset, chunk_left_count, 0, 0);
        const auto t_count_end = std::chrono::steady_clock::now();
        g_optix_last_segment_pair_candidate_count_s +=
            std::chrono::duration<double>(t_count_end - t_count_start).count();
        g_optix_last_segment_pair_raw_candidate_count += static_cast<size_t>(gpu_count);
        if (gpu_count == 0) {
            continue;
        }

        DevPtr d_output(sizeof(GpuSegmentPairIntersectionRecord) * gpu_count);
        const auto t_write_start = std::chrono::steady_clock::now();
        const uint32_t written_count =
            launch_candidate_pass(left_offset, chunk_left_count, d_output.ptr, gpu_count);
        const auto t_write_end = std::chrono::steady_clock::now();
        g_optix_last_segment_pair_candidate_write_s +=
            std::chrono::duration<double>(t_write_end - t_write_start).count();
        if (written_count != gpu_count) {
            throw std::runtime_error("segment-pair intersection candidate count changed between count and write passes");
        }

        const size_t old_size = gpu_rows.size();
        gpu_rows.resize(old_size + gpu_count);
        const auto t_download_start = std::chrono::steady_clock::now();
        download(gpu_rows.data() + old_size, d_output.ptr, gpu_count);
        const auto t_download_end = std::chrono::steady_clock::now();
        g_optix_last_segment_pair_candidate_download_s +=
            std::chrono::duration<double>(t_download_end - t_download_start).count();
    }

    return gpu_rows;
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
        const RtdlSegment* right_host,
        const std::unordered_map<uint32_t, const RtdlSegment*>* prepared_right_by_id = nullptr)
{
    (void)gpu_left_host;
    (void)gpu_right_host;
    const std::vector<GpuSegmentPairIntersectionRecord> gpu_rows =
        collect_segment_pair_intersection_candidates_optix(
            left_count, d_left_ptr, d_right_ptr, right_count, traversable);
    const auto t_refine_start = std::chrono::steady_clock::now();
    finalize_segment_pair_intersection_rows(
        left, left_count,
        right_host, right_count,
        gpu_rows,
        rows_out,
        row_count_out,
        prepared_right_by_id);
    const auto t_refine_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_exact_refine_s =
        std::chrono::duration<double>(t_refine_end - t_refine_start).count();
    g_optix_last_segment_pair_emitted_count = *row_count_out;
}

static void run_segment_pair_intersection_optix(
        const RtdlSegment* left,  size_t left_count,
        const RtdlSegment* right, size_t right_count,
        RtdlSegmentPairIntersectionRow** rows_out, size_t* row_count_out)
{
    ensure_segment_pair_intersection_pipeline();
    reset_segment_pair_phase_timings(1u);

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
    const auto t_upload_start = std::chrono::steady_clock::now();
    upload(d_left.ptr,  gpu_left.data(),  left_count);
    upload(d_right.ptr, gpu_right.data(), right_count);
    const auto t_upload_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_left_upload_s =
        std::chrono::duration<double>(t_upload_end - t_upload_start).count();

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
    reset_segment_pair_phase_timings(1u);
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
    const auto t_upload_start = std::chrono::steady_clock::now();
    upload(d_left.ptr, gpu_left.data(), gpu_left.size());
    const auto t_upload_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_left_upload_s =
        std::chrono::duration<double>(t_upload_end - t_upload_start).count();

    launch_segment_pair_intersection_optix(
        left, left_count,
        gpu_left.data(), d_left.ptr,
        prepared->right_segments.data(), prepared->d_right.ptr,
        prepared->right_count,
        prepared->accel.handle,
        rows_out,
        row_count_out,
        prepared->host_right_segments.data(),
        &prepared->right_by_id);
}

static void count_prepared_segment_pair_intersection_optix(
        PreparedSegmentPairIntersectionBuild* prepared,
        const RtdlSegment* left, size_t left_count,
        size_t* count_out)
{
    if (!prepared) {
        throw std::runtime_error("prepared segment-pair handle must not be null");
    }
    if (!count_out) {
        throw std::runtime_error("segment-pair count output pointer must not be null");
    }
    *count_out = 0;
    reset_segment_pair_phase_timings(2u);
    if (left_count == 0 || prepared->right_count == 0) {
        return;
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
    const auto t_upload_start = std::chrono::steady_clock::now();
    upload(d_left.ptr, gpu_left.data(), gpu_left.size());
    const auto t_upload_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_left_upload_s =
        std::chrono::duration<double>(t_upload_end - t_upload_start).count();

    const std::vector<GpuSegmentPairIntersectionRecord> gpu_rows =
        collect_segment_pair_intersection_candidates_optix(
            left_count,
            d_left.ptr,
            prepared->d_right.ptr,
            prepared->right_count,
            prepared->accel.handle);
    const auto t_refine_start = std::chrono::steady_clock::now();
    *count_out = count_segment_pair_intersection_rows(
        left,
        left_count,
        prepared->host_right_segments.data(),
        prepared->right_count,
        gpu_rows,
        &prepared->right_by_id);
    const auto t_refine_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_exact_refine_s =
        std::chrono::duration<double>(t_refine_end - t_refine_start).count();
    g_optix_last_segment_pair_emitted_count = *count_out;
}

static void run_prepared_segment_first_hit_optix(
        PreparedSegmentPairIntersectionBuild* prepared,
        const RtdlSegment* probes, size_t probe_count,
        RtdlSegmentFirstHitRow** rows_out, size_t* row_count_out)
{
    if (!prepared) {
        throw std::runtime_error("prepared segment first-hit handle must not be null");
    }
    if (!rows_out || !row_count_out) {
        throw std::runtime_error("segment first-hit output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    reset_segment_pair_phase_timings(3u);
    if (probe_count == 0 || prepared->right_count == 0) {
        return;
    }
    ensure_segment_first_hit_pipeline();
    std::vector<GpuSegment> gpu_probes(probe_count);
    for (size_t i = 0; i < probe_count; ++i) {
        gpu_probes[i] = {
            static_cast<float>(probes[i].x0),
            static_cast<float>(probes[i].y0),
            static_cast<float>(probes[i].x1),
            static_cast<float>(probes[i].y1),
            probes[i].id,
        };
    }
    DevPtr d_probes(sizeof(GpuSegment) * probe_count);
    const auto t_upload_start = std::chrono::steady_clock::now();
    upload(d_probes.ptr, gpu_probes.data(), gpu_probes.size());
    const auto t_upload_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_left_upload_s =
        std::chrono::duration<double>(t_upload_end - t_upload_start).count();

    const std::vector<uint64_t> best_pairs =
        collect_segment_first_hits_optix(
            probes,
            probe_count,
            d_probes.ptr,
            prepared->d_right.ptr,
            prepared->right_count,
            prepared->accel.handle);
    const auto t_refine_start = std::chrono::steady_clock::now();
    const std::vector<RtdlSegmentFirstHitRow> refined =
        materialize_segment_first_hit_rows(
            probes,
            probe_count,
            *prepared,
            best_pairs);
    const auto t_refine_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_exact_refine_s =
        std::chrono::duration<double>(t_refine_end - t_refine_start).count();
    g_optix_last_segment_pair_emitted_count = refined.size();

    auto* out = static_cast<RtdlSegmentFirstHitRow*>(
        std::malloc(sizeof(RtdlSegmentFirstHitRow) * refined.size()));
    if (!out && !refined.empty()) throw std::bad_alloc();
    if (!refined.empty()) {
        std::memcpy(out, refined.data(), sizeof(RtdlSegmentFirstHitRow) * refined.size());
    }
    *rows_out = out;
    *row_count_out = refined.size();
}

static void count_prepared_segment_first_hit_optix(
        PreparedSegmentPairIntersectionBuild* prepared,
        const RtdlSegment* probes, size_t probe_count,
        size_t* count_out)
{
    if (!prepared) {
        throw std::runtime_error("prepared segment first-hit handle must not be null");
    }
    if (!count_out) {
        throw std::runtime_error("segment first-hit count output pointer must not be null");
    }
    *count_out = 0;
    reset_segment_pair_phase_timings(4u);
    if (probe_count == 0 || prepared->right_count == 0) {
        return;
    }
    ensure_segment_first_hit_pipeline();
    std::vector<GpuSegment> gpu_probes(probe_count);
    for (size_t i = 0; i < probe_count; ++i) {
        gpu_probes[i] = {
            static_cast<float>(probes[i].x0),
            static_cast<float>(probes[i].y0),
            static_cast<float>(probes[i].x1),
            static_cast<float>(probes[i].y1),
            probes[i].id,
        };
    }
    DevPtr d_probes(sizeof(GpuSegment) * probe_count);
    const auto t_upload_start = std::chrono::steady_clock::now();
    upload(d_probes.ptr, gpu_probes.data(), gpu_probes.size());
    const auto t_upload_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_left_upload_s =
        std::chrono::duration<double>(t_upload_end - t_upload_start).count();

    const std::vector<uint64_t> best_pairs =
        collect_segment_first_hits_optix(
            probes,
            probe_count,
            d_probes.ptr,
            prepared->d_right.ptr,
            prepared->right_count,
            prepared->accel.handle);
    const auto t_refine_start = std::chrono::steady_clock::now();
    const std::vector<RtdlSegmentFirstHitRow> refined =
        materialize_segment_first_hit_rows(
            probes,
            probe_count,
            *prepared,
            best_pairs);
    const auto t_refine_end = std::chrono::steady_clock::now();
    g_optix_last_segment_pair_exact_refine_s =
        std::chrono::duration<double>(t_refine_end - t_refine_start).count();
    g_optix_last_segment_pair_emitted_count = refined.size();
    *count_out = refined.size();
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

    const bool profile_pip = std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_PROFILE") != nullptr;
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
        (positive_only != 0u && std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_DEVICE_PREFILTER") == nullptr) ? 1u : 0u;

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
        std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_ONE_PASS_COMPACT") == nullptr;
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
                "[rtdl_optix_point_primitive_anyhit_profile] positive_only=%u one_pass=%u fallback_chunks=%zu points=%zu polygons=%zu chunks=%zu candidates=%zu emitted=%zu host_pack_s=%.9f upload_s=%.9f accel_build_s=%.9f count_pass_s=%.9f write_pass_s=%.9f compact_download_s=%.9f exact_refine_s=%.9f total_s=%.9f\n",
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
            "[rtdl_optix_point_primitive_anyhit_profile] positive_only=%u one_pass=%u fallback_chunks=%zu points=%zu polygons=%zu chunks=%zu candidates=%zu emitted=%zu host_pack_s=%.9f upload_s=%.9f accel_build_s=%.9f count_pass_s=%.9f write_pass_s=%.9f compact_download_s=%.9f exact_refine_s=%.9f total_s=%.9f\n",
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

    reset_closed_shape_membership_phase_timings(1u);
    ensure_pip_pipeline();

    const auto t_pack_start = std::chrono::steady_clock::now();
    std::vector<float> pts_x(point_count), pts_y(point_count);
    std::vector<uint32_t> pt_ids(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        pts_x[i] = static_cast<float>(points[i].x);
        pts_y[i] = static_cast<float>(points[i].y);
        pt_ids[i] = points[i].id;
    }
    const auto t_pack_end = std::chrono::steady_clock::now();
    g_optix_last_closed_shape_point_pack_s = seconds_between(t_pack_start, t_pack_end);

    const auto t_upload_start = std::chrono::steady_clock::now();
    DevPtr d_pts_x(sizeof(float) * point_count);
    DevPtr d_pts_y(sizeof(float) * point_count);
    DevPtr d_pt_ids(sizeof(uint32_t) * point_count);
    upload(d_pts_x.ptr, pts_x.data(), point_count);
    upload(d_pts_y.ptr, pts_y.data(), point_count);
    upload(d_pt_ids.ptr, pt_ids.data(), point_count);
    const auto t_upload_end = std::chrono::steady_clock::now();
    g_optix_last_closed_shape_point_upload_s = seconds_between(t_upload_start, t_upload_end);

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
        std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_DEVICE_PREFILTER") == nullptr ? 1u : 0u;

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
        std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_ONE_PASS_COMPACT") == nullptr;

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
            g_optix_last_closed_shape_candidate_count_s += seconds_between(t_launch_start, t_launch_end);
        } else {
            g_optix_last_closed_shape_candidate_write_s += seconds_between(t_launch_start, t_launch_end);
        }
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
                const auto t_download_start = std::chrono::steady_clock::now();
                download(gpu_rows.data() + old_size, d_positive_output.ptr, gpu_count);
                const auto t_download_end = std::chrono::steady_clock::now();
                g_optix_last_closed_shape_candidate_download_s += seconds_between(t_download_start, t_download_end);
                g_optix_last_closed_shape_raw_candidate_count += gpu_count;
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
        const auto t_download_start = std::chrono::steady_clock::now();
        download(gpu_rows.data() + old_size, d_positive_output.ptr, gpu_count);
        const auto t_download_end = std::chrono::steady_clock::now();
        g_optix_last_closed_shape_candidate_download_s += seconds_between(t_download_start, t_download_end);
        g_optix_last_closed_shape_raw_candidate_count += gpu_count;
    }

    std::vector<RtdlPointClosedShapeMembershipRow> rows;
    rows.reserve(gpu_rows.size());
    const auto t_refine_start = std::chrono::steady_clock::now();
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
    const auto t_refine_end = std::chrono::steady_clock::now();
    g_optix_last_closed_shape_exact_refine_s = seconds_between(t_refine_start, t_refine_end);
    g_optix_last_closed_shape_emitted_count = rows.size();

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
    if (!prepared) {
        throw std::runtime_error("prepared closed-shape membership handle must not be null");
    }
    if (!count_out) {
        throw std::runtime_error("count output pointer must not be null");
    }
    *count_out = 0;
    if (point_count == 0 || prepared->right_count == 0) {
        return;
    }
    if (point_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
        throw std::runtime_error("prepared closed-shape membership count point count exceeds uint32_t chunk offset capacity");
    }
    if (prepared->right_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
        throw std::runtime_error("prepared closed-shape membership count shape count exceeds uint32_t launch capacity");
    }

    reset_closed_shape_membership_phase_timings(2u);
    ensure_pip_pipeline();

    const auto t_pack_start = std::chrono::steady_clock::now();
    std::vector<float> pts_x(point_count), pts_y(point_count);
    std::vector<uint32_t> pt_ids(point_count);
    for (size_t i = 0; i < point_count; ++i) {
        pts_x[i] = static_cast<float>(points[i].x);
        pts_y[i] = static_cast<float>(points[i].y);
        pt_ids[i] = points[i].id;
    }
    const auto t_pack_end = std::chrono::steady_clock::now();
    g_optix_last_closed_shape_point_pack_s = seconds_between(t_pack_start, t_pack_end);

    const auto t_upload_start = std::chrono::steady_clock::now();
    DevPtr d_pts_x(sizeof(float) * point_count);
    DevPtr d_pts_y(sizeof(float) * point_count);
    DevPtr d_pt_ids(sizeof(uint32_t) * point_count);
    upload(d_pts_x.ptr, pts_x.data(), point_count);
    upload(d_pts_y.ptr, pts_y.data(), point_count);
    upload(d_pt_ids.ptr, pt_ids.data(), point_count);
    const auto t_upload_end = std::chrono::steady_clock::now();
    g_optix_last_closed_shape_point_upload_s = seconds_between(t_upload_start, t_upload_end);

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
        std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_DEVICE_PREFILTER") == nullptr ? 1u : 0u;

    DevPtr d_params(sizeof(PipLaunchParams));
    upload(d_params.ptr, &lp, 1);
    CUstream stream = 0;

    const uint64_t max_points_per_launch64 =
        static_cast<uint64_t>(std::numeric_limits<uint32_t>::max()) /
        static_cast<uint64_t>(prepared->right_count);
    if (max_points_per_launch64 == 0) {
        throw std::runtime_error("prepared closed-shape membership count cannot chunk shape set into uint32_t capacity");
    }
    const size_t max_points_per_launch = static_cast<size_t>(
        std::min<uint64_t>(max_points_per_launch64, static_cast<uint64_t>(point_count)));

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
            g_optix_last_closed_shape_candidate_count_s += seconds_between(t_launch_start, t_launch_end);
        } else {
            g_optix_last_closed_shape_candidate_write_s += seconds_between(t_launch_start, t_launch_end);
        }
        uint32_t emitted = 0;
        download(&emitted, d_count.ptr, 1);
        if (emitted > output_capacity && output_capacity != 0u && !allow_overflow) {
            throw std::runtime_error("prepared closed-shape membership count output overflowed compact capacity");
        }
        return emitted;
    };

    const bool pip_one_pass_compact =
        std::getenv("RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DISABLE_ONE_PASS_COMPACT") == nullptr;
    size_t exact_count = 0;
    auto count_exact_hits = [&](const std::vector<GpuPipRecord>& gpu_rows) {
        const auto t_refine_start = std::chrono::steady_clock::now();
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
            ++exact_count;
        }
        const auto t_refine_end = std::chrono::steady_clock::now();
        g_optix_last_closed_shape_exact_refine_s += seconds_between(t_refine_start, t_refine_end);
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
                std::vector<GpuPipRecord> chunk_rows(gpu_count);
                const auto t_download_start = std::chrono::steady_clock::now();
                download(chunk_rows.data(), d_positive_output.ptr, gpu_count);
                const auto t_download_end = std::chrono::steady_clock::now();
                g_optix_last_closed_shape_candidate_download_s += seconds_between(t_download_start, t_download_end);
                g_optix_last_closed_shape_raw_candidate_count += gpu_count;
                count_exact_hits(chunk_rows);
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
            throw std::runtime_error("prepared closed-shape membership count candidate count changed between count and write passes");
        }
        std::vector<GpuPipRecord> chunk_rows(gpu_count);
        const auto t_download_start = std::chrono::steady_clock::now();
        download(chunk_rows.data(), d_positive_output.ptr, gpu_count);
        const auto t_download_end = std::chrono::steady_clock::now();
        g_optix_last_closed_shape_candidate_download_s += seconds_between(t_download_start, t_download_end);
        g_optix_last_closed_shape_raw_candidate_count += gpu_count;
        count_exact_hits(chunk_rows);
    }

    g_optix_last_closed_shape_emitted_count = exact_count;
    *count_out = exact_count;
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

static void ensure_pack_triangle3d_device_columns_kernel()
{
    (void)get_optix_context();
    std::call_once(g_partner_triangle3d_pack.init, [&]() {
        const std::string ptx = compile_to_ptx(
            kPackTriangle3DDeviceColumnsKernelSrc,
            "partner_triangle3d_device_columns_pack_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_partner_triangle3d_pack.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(
            &g_partner_triangle3d_pack.fn,
            g_partner_triangle3d_pack.module,
            "pack_triangle3d_device_columns"));
    });
}

static void ensure_pack_ray3d_device_columns_kernel()
{
    (void)get_optix_context();
    std::call_once(g_partner_ray3d_pack.init, [&]() {
        const std::string ptx = compile_to_ptx(
            kPackRay3DDeviceColumnsKernelSrc,
            "partner_ray3d_device_columns_pack_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_partner_ray3d_pack.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(
            &g_partner_ray3d_pack.fn,
            g_partner_ray3d_pack.module,
            "pack_ray3d_device_columns"));
    });
}

static void pack_ray3d_device_columns_to_buffer(
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_oz,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_dz,
        const double* ray_tmax,
        size_t ray_count,
        CUdeviceptr d_rays)
{
    if (ray_count == 0) return;
    if (!ray_ids || !ray_ox || !ray_oy || !ray_oz || !ray_dx || !ray_dy || !ray_dz || !ray_tmax)
        throw std::runtime_error("partner device 3-D ray column pointers must not be null when ray_count is nonzero");
    if (!d_rays)
        throw std::runtime_error("destination 3-D ray device buffer must not be null");
    if (ray_count > std::numeric_limits<uint32_t>::max())
        throw std::runtime_error("partner device 3-D ray column count exceeds uint32_t launch limit");

    uint32_t rc = static_cast<uint32_t>(ray_count);
    rtdl_cuda_pack_ray3d_device_columns_precompiled(
        ray_ids,
        ray_ox,
        ray_oy,
        ray_oz,
        ray_dx,
        ray_dy,
        ray_dz,
        ray_tmax,
        reinterpret_cast<void*>(d_rays),
        rc);
}

struct PreparedStaticTriangleScene3D {
    size_t triangle_count = 0;
    DevPtr d_triangles;
    AccelHolder accel;

    explicit PreparedStaticTriangleScene3D(const RtdlTriangle3D* source, size_t count)
        : triangle_count(count), d_triangles(sizeof(GpuTriangle3DHost) * count)
    {
        if (!source && count != 0)
            throw std::runtime_error("triangle pointer must not be null when triangle_count is nonzero");
        if (count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("triangle_count exceeds uint32 launch limit");
        if (count == 0) return;

        std::vector<GpuTriangle3DHost> gpu_tris(count);
        for (size_t i = 0; i < count; ++i) {
            const double values[9] = {
                source[i].x0, source[i].y0, source[i].z0,
                source[i].x1, source[i].y1, source[i].z1,
                source[i].x2, source[i].y2, source[i].z2,
            };
            for (double value : values) {
                if (!std::isfinite(value))
                    throw std::runtime_error("triangle coordinates must be finite");
            }
            gpu_tris[i] = {
                static_cast<float>(source[i].x0),
                static_cast<float>(source[i].y0),
                static_cast<float>(source[i].z0),
                static_cast<float>(source[i].x1),
                static_cast<float>(source[i].y1),
                static_cast<float>(source[i].z1),
                static_cast<float>(source[i].x2),
                static_cast<float>(source[i].y2),
                static_cast<float>(source[i].z2),
                source[i].id
            };
        }
        upload(d_triangles.ptr, gpu_tris.data(), gpu_tris.size());

        std::vector<OptixAabb> aabbs(count);
        for (size_t i = 0; i < count; ++i) {
            aabbs[i] = aabb_for_triangle_3d(
                gpu_tris[i].x0, gpu_tris[i].y0, gpu_tris[i].z0,
                gpu_tris[i].x1, gpu_tris[i].y1, gpu_tris[i].z1,
                gpu_tris[i].x2, gpu_tris[i].y2, gpu_tris[i].z2);
        }
        accel = build_custom_accel(get_optix_context(), aabbs);
    }

    PreparedStaticTriangleScene3D(
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
            size_t count)
        : triangle_count(count), d_triangles(sizeof(GpuTriangle3DHost) * count)
    {
        if (count == 0) return;
        if (!triangle_ids || !triangle_x0 || !triangle_y0 || !triangle_z0
                || !triangle_x1 || !triangle_y1 || !triangle_z1
                || !triangle_x2 || !triangle_y2 || !triangle_z2)
            throw std::runtime_error("partner device 3-D triangle column pointers must not be null when triangle_count is nonzero");
        if (count > std::numeric_limits<uint32_t>::max())
            throw std::runtime_error("partner device 3-D triangle column count exceeds uint32_t launch limit");

        ensure_pack_triangle3d_device_columns_kernel();

        DevPtr d_aabbs(sizeof(OptixAabb) * count);
        CUdeviceptr d_triangle_ids = reinterpret_cast<CUdeviceptr>(triangle_ids);
        CUdeviceptr d_triangle_x0 = reinterpret_cast<CUdeviceptr>(triangle_x0);
        CUdeviceptr d_triangle_y0 = reinterpret_cast<CUdeviceptr>(triangle_y0);
        CUdeviceptr d_triangle_z0 = reinterpret_cast<CUdeviceptr>(triangle_z0);
        CUdeviceptr d_triangle_x1 = reinterpret_cast<CUdeviceptr>(triangle_x1);
        CUdeviceptr d_triangle_y1 = reinterpret_cast<CUdeviceptr>(triangle_y1);
        CUdeviceptr d_triangle_z1 = reinterpret_cast<CUdeviceptr>(triangle_z1);
        CUdeviceptr d_triangle_x2 = reinterpret_cast<CUdeviceptr>(triangle_x2);
        CUdeviceptr d_triangle_y2 = reinterpret_cast<CUdeviceptr>(triangle_y2);
        CUdeviceptr d_triangle_z2 = reinterpret_cast<CUdeviceptr>(triangle_z2);
        uint32_t tc = static_cast<uint32_t>(count);
        void* args[] = {
            &d_triangle_ids,
            &d_triangle_x0,
            &d_triangle_y0,
            &d_triangle_z0,
            &d_triangle_x1,
            &d_triangle_y1,
            &d_triangle_z1,
            &d_triangle_x2,
            &d_triangle_y2,
            &d_triangle_z2,
            &d_triangles.ptr,
            &d_aabbs.ptr,
            &tc,
        };
        const unsigned block = 256;
        const unsigned grid = (tc + block - 1u) / block;
        CU_CHECK(cuLaunchKernel(
            g_partner_triangle3d_pack.fn,
            grid, 1, 1,
            block, 1, 1,
            0, nullptr, args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));

        accel = build_custom_accel_from_device_aabbs(get_optix_context(), d_aabbs.ptr, count);
    }
};

struct PreparedPrimitiveGroupedI64Payload3D {
    size_t primitive_count = 0;
    size_t group_count = 0;
    DevPtr d_groups;
    DevPtr d_values;

    PreparedPrimitiveGroupedI64Payload3D(
            const uint32_t* primitive_group_ids,
            size_t primitive_group_id_count,
            const uint64_t* primitive_values,
            size_t primitive_value_count,
            size_t group_count_in)
        : primitive_count(primitive_group_id_count),
          group_count(group_count_in),
          d_groups(sizeof(uint32_t) * primitive_group_id_count),
          d_values(sizeof(unsigned long long) * primitive_value_count)
    {
        if (primitive_group_id_count != primitive_value_count)
            throw std::runtime_error("primitive group/value payload lengths must match");
        if (!primitive_group_ids && primitive_group_id_count != 0)
            throw std::runtime_error("primitive_group_ids pointer must not be null when count is nonzero");
        if (!primitive_values && primitive_value_count != 0)
            throw std::runtime_error("primitive_values pointer must not be null when count is nonzero");
        if (primitive_group_id_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("primitive payload count exceeds uint32 limit");
        if (group_count_in > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("group_count exceeds uint32 limit");
        for (size_t primitive_index = 0; primitive_index < primitive_group_id_count; ++primitive_index) {
            if (primitive_group_ids[primitive_index] >= group_count_in)
                throw std::runtime_error("primitive_group_ids entries must be smaller than group_count");
        }
        if (primitive_group_id_count == 0)
            return;

        std::vector<unsigned long long> values(primitive_value_count);
        for (size_t primitive_index = 0; primitive_index < primitive_value_count; ++primitive_index)
            values[primitive_index] = static_cast<unsigned long long>(primitive_values[primitive_index]);
        upload(d_groups.ptr, primitive_group_ids, primitive_group_id_count);
        upload(d_values.ptr, values.data(), values.size());
    }
};

static GpuRay3DHost pack_ray_3d_as_raw_gpu_ray(const RtdlRay3D& ray);

struct PreparedRayBatch3D {
    size_t ray_count = 0;
    std::vector<uint32_t> ray_ids;
    DevPtr d_rays;
    DevPtr d_closest_hit_output;

    explicit PreparedRayBatch3D(const RtdlRay3D* rays, size_t count)
        : ray_count(count),
          ray_ids(count),
          d_rays(sizeof(GpuRay3DHost) * count),
          d_closest_hit_output(sizeof(GpuRayClosestHitRecord) * count)
    {
        if (!rays && count != 0)
            throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
        if (count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("ray_count exceeds uint32 launch limit");
        if (count == 0)
            return;

        std::vector<GpuRay3DHost> gpu_rays(count);
        for (size_t i = 0; i < count; ++i) {
            ray_ids[i] = rays[i].id;
            gpu_rays[i] = pack_ray_3d_as_raw_gpu_ray(rays[i]);
        }
        upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
    }

    PreparedRayBatch3D(
            const uint32_t* ray_ids_in,
            const double* ray_ox,
            const double* ray_oy,
            const double* ray_oz,
            const double* ray_dx,
            const double* ray_dy,
            const double* ray_dz,
            const double* ray_tmax,
            size_t count)
        : ray_count(count),
          ray_ids(count),
          d_rays(sizeof(GpuRay3DHost) * count),
          d_closest_hit_output(sizeof(GpuRayClosestHitRecord) * count)
    {
        if (count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("ray_count exceeds uint32 launch limit");
        if (count == 0)
            return;
        if (!ray_ids_in || !ray_ox || !ray_oy || !ray_oz || !ray_dx || !ray_dy || !ray_dz || !ray_tmax)
            throw std::runtime_error("device ray column pointers must not be null when ray_count is nonzero");
        std::vector<uint32_t> host_ray_ids(count);
        download(host_ray_ids.data(), reinterpret_cast<CUdeviceptr>(ray_ids_in), count);
        ray_ids = std::move(host_ray_ids);
        pack_ray3d_device_columns_to_buffer(
            ray_ids_in,
            ray_ox,
            ray_oy,
            ray_oz,
            ray_dx,
            ray_dy,
            ray_dz,
            ray_tmax,
            count,
            d_rays.ptr);
    }
};

struct PreparedClosestHitGroupedArgmin3D {
    size_t ray_group_id_count = 0;
    size_t candidate_count = 0;
    size_t group_count = 0;
    std::vector<uint32_t> ray_group_ids;
    DevPtr d_ray_group_ids;
    DevPtr d_candidate_values;
    DevPtr d_candidate_indices;
    DevPtr d_group_has_value;
    DevPtr d_group_index;
    DevPtr d_group_value;
    DevPtr d_group_best_keys;

    PreparedClosestHitGroupedArgmin3D(
            const uint32_t* ray_group_ids_in,
            size_t ray_group_id_count_in,
            const double* candidate_values,
            const uint32_t* candidate_indices,
            size_t candidate_count_in,
            size_t group_count_in)
        : ray_group_id_count(ray_group_id_count_in),
          candidate_count(candidate_count_in),
          group_count(group_count_in),
          ray_group_ids(ray_group_id_count_in),
          d_ray_group_ids(sizeof(uint32_t) * ray_group_id_count_in),
          d_candidate_values(sizeof(double) * candidate_count_in),
          d_candidate_indices(sizeof(uint32_t) * candidate_count_in),
          d_group_has_value(sizeof(uint8_t) * group_count_in),
          d_group_index(sizeof(uint32_t) * group_count_in),
          d_group_value(sizeof(double) * group_count_in),
          d_group_best_keys(sizeof(unsigned long long) * group_count_in)
    {
        if (!ray_group_ids_in && ray_group_id_count_in != 0)
            throw std::runtime_error("ray group-id map must not be null when nonempty");
        if (!candidate_values && candidate_count_in != 0)
            throw std::runtime_error("candidate values must not be null when candidate_count is nonzero");
        if (!candidate_indices && candidate_count_in != 0)
            throw std::runtime_error("candidate indices must not be null when candidate_count is nonzero");
        if (ray_group_id_count_in > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("ray_group_id_count exceeds uint32 launch limit");
        if (candidate_count_in > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("candidate_count exceeds uint32 launch limit");
        if (group_count_in > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("group_count exceeds uint32 launch limit");

        for (size_t i = 0; i < ray_group_id_count_in; ++i) {
            if (ray_group_ids_in[i] >= group_count_in)
                throw std::runtime_error("ray group id is outside the grouped argmin output range");
            ray_group_ids[i] = ray_group_ids_in[i];
        }
        upload(d_ray_group_ids.ptr, ray_group_ids_in, ray_group_id_count_in);
        upload(d_candidate_values.ptr, candidate_values, candidate_count_in);
        upload(d_candidate_indices.ptr, candidate_indices, candidate_count_in);
    }
};

struct PreparedGroupedCandidateArgmin {
    size_t candidate_count = 0;
    size_t group_count = 0;
    DevPtr d_candidate_group_ids;
    DevPtr d_candidate_values;
    DevPtr d_candidate_indices;
    DevPtr d_group_has_value;
    DevPtr d_group_index;
    DevPtr d_group_value;
    DevPtr d_group_best_keys;

    PreparedGroupedCandidateArgmin(
            const uint32_t* candidate_group_ids,
            const double* candidate_values,
            const uint32_t* candidate_indices,
            size_t candidate_count_in,
            size_t group_count_in)
        : candidate_count(candidate_count_in),
          group_count(group_count_in),
          d_candidate_group_ids(sizeof(uint32_t) * candidate_count_in),
          d_candidate_values(sizeof(double) * candidate_count_in),
          d_candidate_indices(sizeof(uint32_t) * candidate_count_in),
          d_group_has_value(sizeof(uint8_t) * group_count_in),
          d_group_index(sizeof(uint32_t) * group_count_in),
          d_group_value(sizeof(double) * group_count_in),
          d_group_best_keys(sizeof(unsigned long long) * group_count_in)
    {
        if (!candidate_group_ids && candidate_count_in != 0)
            throw std::runtime_error("candidate group ids must not be null when candidate_count is nonzero");
        if (!candidate_values && candidate_count_in != 0)
            throw std::runtime_error("candidate values must not be null when candidate_count is nonzero");
        if (!candidate_indices && candidate_count_in != 0)
            throw std::runtime_error("candidate indices must not be null when candidate_count is nonzero");
        if (candidate_count_in > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("candidate_count exceeds uint32 launch limit");
        if (group_count_in > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("group_count exceeds uint32 launch limit");
        for (size_t i = 0; i < candidate_count_in; ++i) {
            if (candidate_group_ids[i] >= group_count_in)
                throw std::runtime_error("candidate group id is outside the grouped argmin output range");
        }

        upload(d_candidate_group_ids.ptr, candidate_group_ids, candidate_count_in);
        upload(d_candidate_values.ptr, candidate_values, candidate_count_in);
        upload(d_candidate_indices.ptr, candidate_indices, candidate_count_in);
    }
};

static void validate_grouped_segment_query_3d_inputs(
        const RtdlSegment3D* segments,
        size_t segment_count,
        const uint32_t* group_offsets,
        size_t group_count)
{
    if (!segments && segment_count != 0)
        throw std::runtime_error("segment pointer must not be null when segment_count is nonzero");
    if (!group_offsets && group_count != 0)
        throw std::runtime_error("group offsets pointer must not be null when group_count is nonzero");
    if (segment_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("segment_count exceeds uint32 launch limit");
    if (group_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("group_count exceeds uint32 limit");
    if (group_count == 0) {
        if (segment_count != 0)
            throw std::runtime_error("segment_count must be zero when group_count is zero");
        return;
    }
    if (group_offsets[0] != 0u)
        throw std::runtime_error("first group offset must be zero");
    for (size_t group_index = 0; group_index < group_count; ++group_index) {
        const uint32_t begin = group_offsets[group_index];
        const uint32_t end = group_offsets[group_index + 1];
        if (end < begin)
            throw std::runtime_error("group offsets must be monotonic");
        if (static_cast<size_t>(end) > segment_count)
            throw std::runtime_error("group offsets exceed segment_count");
    }
    if (static_cast<size_t>(group_offsets[group_count]) != segment_count)
        throw std::runtime_error("final group offset must equal segment_count");
}

static GpuRay3DHost pack_segment_3d_as_gpu_ray(const RtdlSegment3D& segment)
{
    const double values[6] = {
        segment.x0, segment.y0, segment.z0,
        segment.x1, segment.y1, segment.z1,
    };
    for (double value : values) {
        if (!std::isfinite(value))
            throw std::runtime_error("segment coordinates must be finite");
    }
    const double ddx = segment.x1 - segment.x0;
    const double ddy = segment.y1 - segment.y0;
    const double ddz = segment.z1 - segment.z0;
    const double dlen = std::sqrt(ddx * ddx + ddy * ddy + ddz * ddz);
    if (dlen == 0.0)
        throw std::runtime_error("zero-length segments are invalid");
    const float dx = static_cast<float>(ddx);
    const float dy = static_cast<float>(ddy);
    const float dz = static_cast<float>(ddz);
    const float len = std::sqrt(dx * dx + dy * dy + dz * dz);
    if (!(len > 0.0f))
        throw std::runtime_error("segment length is not representable as float32");
    return {
        static_cast<float>(segment.x0),
        static_cast<float>(segment.y0),
        static_cast<float>(segment.z0),
        dx / len, dy / len, dz / len,
        len,
        segment.id
    };
}

static GpuRay3DHost pack_ray_3d_as_gpu_ray(const RtdlRay3D& ray)
{
    const double values[7] = {
        ray.ox, ray.oy, ray.oz,
        ray.dx, ray.dy, ray.dz,
        ray.tmax,
    };
    for (double value : values) {
        if (!std::isfinite(value))
            throw std::runtime_error("ray coordinates and tmax must be finite");
    }
    const float dx = static_cast<float>(ray.dx);
    const float dy = static_cast<float>(ray.dy);
    const float dz = static_cast<float>(ray.dz);
    const float len = std::sqrt(dx * dx + dy * dy + dz * dz);
    if (len > 1.0e-10f) {
        return {
            static_cast<float>(ray.ox),
            static_cast<float>(ray.oy),
            static_cast<float>(ray.oz),
            dx / len, dy / len, dz / len,
            static_cast<float>(ray.tmax) * len,
            ray.id
        };
    }
    return {
        static_cast<float>(ray.ox),
        static_cast<float>(ray.oy),
        static_cast<float>(ray.oz),
        0.0f, 0.0f, 0.0f,
        0.0f,
        ray.id
    };
}

static GpuRay3DHost pack_ray_3d_as_raw_gpu_ray(const RtdlRay3D& ray)
{
    const double values[7] = {
        ray.ox, ray.oy, ray.oz,
        ray.dx, ray.dy, ray.dz,
        ray.tmax,
    };
    for (double value : values) {
        if (!std::isfinite(value))
            throw std::runtime_error("ray coordinates and tmax must be finite");
    }
    return {
        static_cast<float>(ray.ox),
        static_cast<float>(ray.oy),
        static_cast<float>(ray.oz),
        static_cast<float>(ray.dx),
        static_cast<float>(ray.dy),
        static_cast<float>(ray.dz),
        static_cast<float>(ray.tmax),
        ray.id
    };
}

struct PreparedGroupedSegmentQuery3D {
    size_t segment_count = 0;
    size_t group_count = 0;
    DevPtr d_rays;
    DevPtr d_group_offsets;
    DevPtr d_group_indices;
    DevPtr d_group_flags;

    PreparedGroupedSegmentQuery3D(
            const RtdlSegment3D* segments,
            size_t segment_count_arg,
            const uint32_t* group_offsets,
            size_t group_count_arg)
        : segment_count(segment_count_arg),
          group_count(group_count_arg),
          d_rays(sizeof(GpuRay3DHost) * segment_count_arg),
          d_group_offsets(group_count_arg == 0 ? 0 : sizeof(uint32_t) * (group_count_arg + 1)),
          d_group_indices(sizeof(uint32_t) * segment_count_arg),
          d_group_flags(sizeof(uint32_t) * group_count_arg)
    {
        validate_grouped_segment_query_3d_inputs(
            segments,
            segment_count,
            group_offsets,
            group_count);
        if (segment_count != 0) {
            std::vector<GpuRay3DHost> gpu_rays(segment_count);
            for (size_t i = 0; i < segment_count; ++i)
                gpu_rays[i] = pack_segment_3d_as_gpu_ray(segments[i]);
            upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
        }
        if (group_count != 0) {
            upload(d_group_offsets.ptr, group_offsets, group_count + 1);
            std::vector<uint32_t> group_indices(segment_count, 0u);
            for (size_t group_index = 0; group_index < group_count; ++group_index) {
                const uint32_t begin = group_offsets[group_index];
                const uint32_t end = group_offsets[group_index + 1];
                for (uint32_t segment_index = begin; segment_index < end; ++segment_index)
                    group_indices[segment_index] = static_cast<uint32_t>(group_index);
            }
            upload(d_group_indices.ptr, group_indices.data(), group_indices.size());
        }
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

constexpr uint32_t kAabbIndexOpPointContains = 1u;
constexpr uint32_t kAabbIndexOpRangeContains = 2u;
constexpr uint32_t kAabbIndexOpRangeIntersects = 3u;
constexpr uint32_t kAabbIndexIntersectForwardPass = 0u;
constexpr uint32_t kAabbIndexIntersectBackwardPass = 1u;
constexpr float kAabbIndexZMin = -1.0e-4f;
constexpr float kAabbIndexZMax = 1.0e-4f;
constexpr float kAabbIndexPad = 1.0e-6f;

struct GpuAabb2D {
    float min_x;
    float min_y;
    float max_x;
    float max_y;
    uint32_t id;
};

struct AabbIndexQueryLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* point_queries;
    const GpuAabb2D* box_queries;
    const GpuAabb2D* indexed_boxes;
    unsigned long long* hit_count;
    RtdlAabbPairRow* rows_out;
    uint32_t point_query_count;
    uint32_t box_query_count;
    uint32_t indexed_box_count;
    uint32_t row_capacity;
    uint32_t operation;
    uint32_t intersect_pass;
    uint32_t collect_rows;
};

static void validate_aabb2d_bounds(double min_x, double min_y, double max_x, double max_y)
{
    const double values[4] = {min_x, min_y, max_x, max_y};
    for (double value : values) {
        if (!std::isfinite(value))
            throw std::runtime_error("AABB coordinates must be finite");
    }
    if (max_x < min_x || max_y < min_y)
        throw std::runtime_error("AABB max bounds must be greater than or equal to min bounds");
}

static GpuAabb2D pack_aabb2d_for_gpu(const RtdlAabb2D& box)
{
    validate_aabb2d_bounds(box.min_x, box.min_y, box.max_x, box.max_y);
    GpuAabb2D packed = {
        static_cast<float>(box.min_x),
        static_cast<float>(box.min_y),
        static_cast<float>(box.max_x),
        static_cast<float>(box.max_y),
        box.id,
    };
    if (!std::isfinite(packed.min_x) || !std::isfinite(packed.min_y)
            || !std::isfinite(packed.max_x) || !std::isfinite(packed.max_y))
        throw std::runtime_error("AABB coordinates are outside float32 OptiX execution range");
    return packed;
}

static OptixAabb optix_aabb_for_gpu_box(const GpuAabb2D& box)
{
    OptixAabb a = {};
    a.minX = std::min(box.min_x, box.max_x) - kAabbIndexPad;
    a.minY = std::min(box.min_y, box.max_y) - kAabbIndexPad;
    a.minZ = kAabbIndexZMin;
    a.maxX = std::max(box.min_x, box.max_x) + kAabbIndexPad;
    a.maxY = std::max(box.min_y, box.max_y) + kAabbIndexPad;
    a.maxZ = kAabbIndexZMax;
    return a;
}

static const char* kAabbIndexCountKernelSrc = R"CUDA(
#include <optix_device.h>

typedef unsigned int uint32_t;

struct GpuPoint {
    float x;
    float y;
    uint32_t id;
    uint32_t pad;
};

struct GpuAabb2D {
    float min_x;
    float min_y;
    float max_x;
    float max_y;
    uint32_t id;
};

struct RtdlAabbPairRow {
    uint32_t query_id;
    uint32_t indexed_id;
};

struct AabbIndexQueryLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint* point_queries;
    const GpuAabb2D* box_queries;
    const GpuAabb2D* indexed_boxes;
    unsigned long long* hit_count;
    RtdlAabbPairRow* rows_out;
    uint32_t point_query_count;
    uint32_t box_query_count;
    uint32_t indexed_box_count;
    uint32_t row_capacity;
    uint32_t operation;
    uint32_t intersect_pass;
    uint32_t collect_rows;
};

extern "C" __constant__ AabbIndexQueryLaunchParams params;

static __forceinline__ __device__ bool box_contains_point(const GpuAabb2D& box, float x, float y) {
    return box.min_x <= x && x <= box.max_x && box.min_y <= y && y <= box.max_y;
}

static __forceinline__ __device__ bool box_contains_box(const GpuAabb2D& box, const GpuAabb2D& query) {
    return box.min_x <= query.min_x
        && box.min_y <= query.min_y
        && box.max_x >= query.max_x
        && box.max_y >= query.max_y;
}

static __forceinline__ __device__ bool segment_intersects_box(
        float ax, float ay, float bx, float by, const GpuAabb2D& box) {
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

static __forceinline__ __device__ void trace_aabb_index_segment(
        float ax, float ay, float bx, float by, uint32_t payload_idx) {
    float dx = bx - ax;
    float dy = by - ay;
    const float len = sqrtf(dx * dx + dy * dy);
    float3 origin = make_float3(ax, ay, 0.0f);
    float3 direction = make_float3(0.0f, 0.0f, 1.0f);
    float tmax = 2.0f;
    if (len > 1.0e-10f) {
        direction = make_float3(dx / len, dy / len, 0.0f);
        tmax = len;
    } else {
        origin = make_float3(ax, ay, -1.0f);
    }
    unsigned int p0 = payload_idx;
    optixTrace(params.traversable,
               origin,
               direction,
               0.0f, tmax, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0);
}

extern "C" __global__ void __raygen__aabb_index_query() {
    const uint32_t idx = optixGetLaunchIndex().x;
    float x = 0.0f;
    float y = 0.0f;
    if (params.operation == 1u) {
        if (idx >= params.point_query_count) return;
        const GpuPoint q = params.point_queries[idx];
        x = q.x;
        y = q.y;
    } else if (params.operation == 2u) {
        if (idx >= params.box_query_count) return;
        const GpuAabb2D q = params.box_queries[idx];
        x = 0.5f * (q.min_x + q.max_x);
        y = 0.5f * (q.min_y + q.max_y);
    } else if (params.operation == 3u) {
        if (params.intersect_pass == 0u) {
            if (idx >= params.box_query_count) return;
            const GpuAabb2D q = params.box_queries[idx];
            trace_aabb_index_segment(q.min_x, q.min_y, q.max_x, q.max_y, idx);
        } else {
            if (idx >= params.indexed_box_count) return;
            const GpuAabb2D indexed = params.indexed_boxes[idx];
            trace_aabb_index_segment(indexed.max_x, indexed.min_y, indexed.min_x, indexed.max_y, idx);
        }
        return;
    } else {
        return;
    }
    unsigned int p0 = idx;
    optixTrace(params.traversable,
               make_float3(x, y, -1.0f),
               make_float3(0.0f, 0.0f, 1.0f),
               0.0f, 2.0f, 0.0f,
               OptixVisibilityMask(255),
               OPTIX_RAY_FLAG_NONE,
               0, 1, 0,
               p0);
}

extern "C" __global__ void __miss__aabb_index_miss() {}

extern "C" __global__ void __intersection__aabb_index_exact() {
    const uint32_t prim = optixGetPrimitiveIndex();
    const uint32_t qidx = optixGetPayload_0();
    bool accept = false;
    if (params.operation == 1u) {
        const GpuAabb2D indexed = params.indexed_boxes[prim];
        const GpuPoint query = params.point_queries[qidx];
        accept = box_contains_point(indexed, query.x, query.y);
    } else if (params.operation == 2u) {
        const GpuAabb2D indexed = params.indexed_boxes[prim];
        const GpuAabb2D query = params.box_queries[qidx];
        accept = box_contains_box(indexed, query);
    } else if (params.operation == 3u) {
        if (params.intersect_pass == 0u) {
            const GpuAabb2D indexed = params.indexed_boxes[prim];
            const GpuAabb2D query = params.box_queries[qidx];
            accept = segment_intersects_box(query.min_x, query.min_y, query.max_x, query.max_y, indexed);
        } else {
            const GpuAabb2D source = params.indexed_boxes[qidx];
            const GpuAabb2D query = params.box_queries[prim];
            const bool source_antidiagonal_hits_query =
                segment_intersects_box(source.max_x, source.min_y, source.min_x, source.max_y, query);
            const bool query_diagonal_hits_source =
                segment_intersects_box(query.min_x, query.min_y, query.max_x, query.max_y, source);
            accept = source_antidiagonal_hits_query && !query_diagonal_hits_source;
        }
    }
    if (!accept) return;
    float hit_t = optixGetRayTmin() + 1.0e-6f;
    if (hit_t > optixGetRayTmax()) hit_t = optixGetRayTmax();
    optixReportIntersection(hit_t, 0u);
}

extern "C" __global__ void __anyhit__aabb_index_count() {
    const unsigned long long row_index = atomicAdd(params.hit_count, 1ULL);
    if (params.collect_rows != 0u && row_index < params.row_capacity) {
        const uint32_t prim = optixGetPrimitiveIndex();
        const uint32_t qidx = optixGetPayload_0();
        RtdlAabbPairRow row;
        if (params.operation == 1u) {
            row.query_id = params.point_queries[qidx].id;
            row.indexed_id = params.indexed_boxes[prim].id;
        } else if (params.operation == 3u && params.intersect_pass == 0u) {
            row.query_id = params.box_queries[qidx].id;
            row.indexed_id = params.indexed_boxes[prim].id;
        } else if (params.operation == 3u) {
            row.query_id = params.box_queries[prim].id;
            row.indexed_id = params.indexed_boxes[qidx].id;
        } else {
            optixIgnoreIntersection();
            return;
        }
        params.rows_out[row_index] = row;
    }
    optixIgnoreIntersection();
}
)CUDA";

static void ensure_aabb_index_count_2d_pipeline()
{
    std::call_once(g_aabb_index_count.init, [&]() {
        std::string ptx = compile_to_ptx(kAabbIndexCountKernelSrc, "aabb_index_count_kernel.cu");
        g_aabb_index_count.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__aabb_index_query",
            "__miss__aabb_index_miss",
            "__intersection__aabb_index_exact",
            "__anyhit__aabb_index_count",
            nullptr, 1).release();
    });
}

struct PreparedAabbIndex2DOptix {
    size_t box_count = 0;
    DevPtr d_boxes;
    AccelHolder accel;

    PreparedAabbIndex2DOptix(const RtdlAabb2D* boxes, size_t count)
        : box_count(count), d_boxes(sizeof(GpuAabb2D) * count)
    {
        if (!boxes && count != 0)
            throw std::runtime_error("boxes pointer must not be null when box_count is nonzero");
        if (count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("AABB index box_count exceeds uint32 launch limit");
        if (count == 0) return;

        std::vector<GpuAabb2D> gpu_boxes(count);
        std::vector<OptixAabb> aabbs(count);
        for (size_t i = 0; i < count; ++i) {
            gpu_boxes[i] = pack_aabb2d_for_gpu(boxes[i]);
            aabbs[i] = optix_aabb_for_gpu_box(gpu_boxes[i]);
        }
        upload(d_boxes.ptr, gpu_boxes.data(), gpu_boxes.size());
        accel = build_custom_accel(get_optix_context(), aabbs);
    }
};

static PreparedAabbIndex2DOptix* prepare_aabb_index_2d_optix(
        const RtdlAabb2D* boxes,
        size_t box_count)
{
    return new PreparedAabbIndex2DOptix(boxes, box_count);
}

static GpuPoint pack_aabb_index_point_query_for_gpu(const RtdlPoint& point)
{
    const double values[2] = {point.x, point.y};
    for (double value : values) {
        if (!std::isfinite(value))
            throw std::runtime_error("point query coordinates must be finite");
    }
    GpuPoint packed = {
        static_cast<float>(point.x),
        static_cast<float>(point.y),
        point.id,
        0u,
    };
    if (!std::isfinite(packed.x) || !std::isfinite(packed.y))
        throw std::runtime_error("point query coordinates are outside float32 OptiX execution range");
    return packed;
}

struct PreparedAabbIndexQueries2DOptix {
    uint32_t operation = 0;
    size_t query_count = 0;
    DevPtr d_point_queries;
    DevPtr d_box_queries;
    AccelHolder accel;

    PreparedAabbIndexQueries2DOptix(
            const RtdlPoint* point_queries,
            size_t point_query_count)
        : operation(kAabbIndexOpPointContains),
          query_count(point_query_count),
          d_point_queries(sizeof(GpuPoint) * point_query_count),
          d_box_queries(0),
          accel()
    {
        if (!point_queries && point_query_count != 0)
            throw std::runtime_error("point_queries pointer must not be null when point_query_count is nonzero");
        if (point_query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("point_query_count exceeds uint32 launch limit");
        if (point_query_count == 0) return;
        std::vector<GpuPoint> gpu_points(point_query_count);
        for (size_t i = 0; i < point_query_count; ++i)
            gpu_points[i] = pack_aabb_index_point_query_for_gpu(point_queries[i]);
        upload(d_point_queries.ptr, gpu_points.data(), gpu_points.size());
    }

    PreparedAabbIndexQueries2DOptix(
            const RtdlAabb2D* box_queries,
            size_t box_query_count)
        : operation(kAabbIndexOpRangeContains),
          query_count(box_query_count),
          d_point_queries(0),
          d_box_queries(sizeof(GpuAabb2D) * box_query_count),
          accel()
    {
        if (!box_queries && box_query_count != 0)
            throw std::runtime_error("box_queries pointer must not be null when box_query_count is nonzero");
        if (box_query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("box_query_count exceeds uint32 launch limit");
        if (box_query_count == 0) return;
        std::vector<GpuAabb2D> gpu_boxes(box_query_count);
        std::vector<OptixAabb> aabbs(box_query_count);
        for (size_t i = 0; i < box_query_count; ++i) {
            gpu_boxes[i] = pack_aabb2d_for_gpu(box_queries[i]);
            aabbs[i] = optix_aabb_for_gpu_box(gpu_boxes[i]);
        }
        upload(d_box_queries.ptr, gpu_boxes.data(), gpu_boxes.size());
        accel = build_custom_accel(get_optix_context(), aabbs);
    }
};

static PreparedAabbIndexQueries2DOptix* prepare_aabb_index_point_queries_2d_optix(
        const RtdlPoint* point_queries,
        size_t point_query_count)
{
    return new PreparedAabbIndexQueries2DOptix(point_queries, point_query_count);
}

static PreparedAabbIndexQueries2DOptix* prepare_aabb_index_box_queries_2d_optix(
        const RtdlAabb2D* box_queries,
        size_t box_query_count)
{
    return new PreparedAabbIndexQueries2DOptix(box_queries, box_query_count);
}

static uint32_t validate_aabb_index_operation(uint32_t operation)
{
    if (operation == kAabbIndexOpPointContains
            || operation == kAabbIndexOpRangeContains
            || operation == kAabbIndexOpRangeIntersects)
        return operation;
    throw std::runtime_error(
        "unsupported OptiX AABB_INDEX_QUERY_2D operation");
}

static void launch_aabb_index_count_pass_optix(
        OptixTraversableHandle traversable,
        CUdeviceptr d_point_queries,
        size_t point_query_count,
        CUdeviceptr d_box_queries,
        size_t box_query_count,
        CUdeviceptr d_indexed_boxes,
        size_t indexed_box_count,
        uint32_t operation,
        uint32_t intersect_pass,
        size_t launch_count,
        CUdeviceptr d_hit_count,
        CUdeviceptr d_rows_out = 0,
        size_t row_capacity = 0,
        bool collect_rows = false)
{
    ensure_aabb_index_count_2d_pipeline();

    if (row_capacity > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("AABB row output capacity exceeds uint32 launch limit");
    AabbIndexQueryLaunchParams lp = {};
    lp.traversable = traversable;
    lp.point_queries = reinterpret_cast<const GpuPoint*>(d_point_queries);
    lp.box_queries = reinterpret_cast<const GpuAabb2D*>(d_box_queries);
    lp.indexed_boxes = reinterpret_cast<const GpuAabb2D*>(d_indexed_boxes);
    lp.hit_count = reinterpret_cast<unsigned long long*>(d_hit_count);
    lp.rows_out = reinterpret_cast<RtdlAabbPairRow*>(d_rows_out);
    lp.point_query_count = static_cast<uint32_t>(point_query_count);
    lp.box_query_count = static_cast<uint32_t>(box_query_count);
    lp.indexed_box_count = static_cast<uint32_t>(indexed_box_count);
    lp.row_capacity = static_cast<uint32_t>(row_capacity);
    lp.operation = operation;
    lp.intersect_pass = intersect_pass;
    lp.collect_rows = collect_rows ? 1u : 0u;

    DevPtr d_params(sizeof(AabbIndexQueryLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_aabb_index_count.pipe->pipeline, stream,
                            d_params.ptr, sizeof(AabbIndexQueryLaunchParams),
                            &g_aabb_index_count.pipe->sbt,
                            static_cast<unsigned>(launch_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
}

static void count_prepared_aabb_index_2d_device_optix(
        PreparedAabbIndex2DOptix* prepared,
        CUdeviceptr d_point_queries,
        size_t point_query_count,
        CUdeviceptr d_box_queries,
        size_t box_query_count,
        uint32_t operation,
        size_t* hit_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX AABB index handle must not be null");
    if (!hit_count_out) throw std::runtime_error("hit_count_out must not be null");
    *hit_count_out = 0;
    operation = validate_aabb_index_operation(operation);
    if (operation == kAabbIndexOpRangeIntersects)
        throw std::runtime_error("range_intersects requires prepared box queries with a query GAS");
    if (prepared->box_count == 0) return;
    if (operation == kAabbIndexOpPointContains) {
        if (!d_point_queries && point_query_count != 0)
            throw std::runtime_error("device point query buffer must not be null when point_query_count is nonzero");
        if (point_query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("point_query_count exceeds uint32 launch limit");
        if (point_query_count == 0) return;
    }
    if (operation == kAabbIndexOpRangeContains) {
        if (!d_box_queries && box_query_count != 0)
            throw std::runtime_error("device box query buffer must not be null when box_query_count is nonzero");
        if (box_query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("box_query_count exceeds uint32 launch limit");
        if (box_query_count == 0) return;
    }

    const size_t launch_count =
        operation == kAabbIndexOpPointContains ? point_query_count : box_query_count;
    DevPtr d_hit_count(sizeof(unsigned long long));
    unsigned long long zero = 0ULL;
    upload(d_hit_count.ptr, &zero, 1);

    launch_aabb_index_count_pass_optix(
        prepared->accel.handle,
        d_point_queries,
        point_query_count,
        d_box_queries,
        box_query_count,
        prepared->d_boxes.ptr,
        prepared->box_count,
        operation,
        0u,
        launch_count,
        d_hit_count.ptr);

    unsigned long long count = 0ULL;
    download(&count, d_hit_count.ptr, 1);
    *hit_count_out = static_cast<size_t>(count);
}

static void count_prepared_aabb_index_2d_range_intersects_optix(
        PreparedAabbIndex2DOptix* prepared,
        PreparedAabbIndexQueries2DOptix* prepared_queries,
        size_t* hit_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX AABB index handle must not be null");
    if (!prepared_queries) throw std::runtime_error("prepared OptiX AABB query handle must not be null");
    if (!hit_count_out) throw std::runtime_error("hit_count_out must not be null");
    *hit_count_out = 0;
    if (prepared_queries->operation != kAabbIndexOpRangeContains)
        throw std::runtime_error("range_intersects requires prepared box queries");
    if (prepared->box_count == 0 || prepared_queries->query_count == 0) return;
    if (prepared->box_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("indexed box count exceeds uint32 launch limit");
    if (prepared_queries->query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("box query count exceeds uint32 launch limit");

    DevPtr d_hit_count(sizeof(unsigned long long));
    unsigned long long zero = 0ULL;
    upload(d_hit_count.ptr, &zero, 1);

    launch_aabb_index_count_pass_optix(
        prepared->accel.handle,
        0,
        0,
        prepared_queries->d_box_queries.ptr,
        prepared_queries->query_count,
        prepared->d_boxes.ptr,
        prepared->box_count,
        kAabbIndexOpRangeIntersects,
        kAabbIndexIntersectForwardPass,
        prepared_queries->query_count,
        d_hit_count.ptr);
    launch_aabb_index_count_pass_optix(
        prepared_queries->accel.handle,
        0,
        0,
        prepared_queries->d_box_queries.ptr,
        prepared_queries->query_count,
        prepared->d_boxes.ptr,
        prepared->box_count,
        kAabbIndexOpRangeIntersects,
        kAabbIndexIntersectBackwardPass,
        prepared->box_count,
        d_hit_count.ptr);

    unsigned long long count = 0ULL;
    download(&count, d_hit_count.ptr, 1);
    *hit_count_out = static_cast<size_t>(count);
}

static void count_prepared_aabb_index_2d_optix(
        PreparedAabbIndex2DOptix* prepared,
        const RtdlPoint* point_queries,
        size_t point_query_count,
        const RtdlAabb2D* box_queries,
        size_t box_query_count,
        uint32_t operation,
        size_t* hit_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX AABB index handle must not be null");
    if (!hit_count_out) throw std::runtime_error("hit_count_out must not be null");
    *hit_count_out = 0;
    operation = validate_aabb_index_operation(operation);
    if (operation == kAabbIndexOpPointContains) {
        if (!point_queries && point_query_count != 0)
            throw std::runtime_error("point_queries pointer must not be null when point_query_count is nonzero");
        if (point_query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("point_query_count exceeds uint32 launch limit");
        if (point_query_count == 0) return;
    }
    if (operation == kAabbIndexOpRangeContains || operation == kAabbIndexOpRangeIntersects) {
        if (!box_queries && box_query_count != 0)
            throw std::runtime_error("box_queries pointer must not be null when box_query_count is nonzero");
        if (box_query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
            throw std::runtime_error("box_query_count exceeds uint32 launch limit");
        if (box_query_count == 0) return;
    }

    if (operation == kAabbIndexOpRangeIntersects) {
        PreparedAabbIndexQueries2DOptix prepared_box_queries(box_queries, box_query_count);
        count_prepared_aabb_index_2d_range_intersects_optix(prepared, &prepared_box_queries, hit_count_out);
        return;
    }

    std::vector<GpuPoint> gpu_points;
    std::vector<GpuAabb2D> gpu_query_boxes;
    DevPtr d_point_queries(operation == kAabbIndexOpPointContains ? sizeof(GpuPoint) * point_query_count : 0);
    DevPtr d_box_queries(operation == kAabbIndexOpRangeContains ? sizeof(GpuAabb2D) * box_query_count : 0);

    if (operation == kAabbIndexOpPointContains) {
        gpu_points.resize(point_query_count);
        for (size_t i = 0; i < point_query_count; ++i) {
            gpu_points[i] = pack_aabb_index_point_query_for_gpu(point_queries[i]);
        }
        upload(d_point_queries.ptr, gpu_points.data(), gpu_points.size());
    } else if (operation == kAabbIndexOpRangeContains) {
        gpu_query_boxes.resize(box_query_count);
        for (size_t i = 0; i < box_query_count; ++i)
            gpu_query_boxes[i] = pack_aabb2d_for_gpu(box_queries[i]);
        upload(d_box_queries.ptr, gpu_query_boxes.data(), gpu_query_boxes.size());
    }

    count_prepared_aabb_index_2d_device_optix(
        prepared,
        d_point_queries.ptr,
        point_query_count,
        d_box_queries.ptr,
        box_query_count,
        operation,
        hit_count_out);
}

static void count_prepared_aabb_index_2d_packed_queries_optix(
        PreparedAabbIndex2DOptix* prepared,
        PreparedAabbIndexQueries2DOptix* prepared_queries,
        uint32_t operation,
        size_t* hit_count_out)
{
    if (!prepared_queries)
        throw std::runtime_error("prepared OptiX AABB query handle must not be null");
    operation = validate_aabb_index_operation(operation);
    if (operation == kAabbIndexOpPointContains && prepared_queries->operation != kAabbIndexOpPointContains)
        throw std::runtime_error("point_contains requires prepared point queries");
    if ((operation == kAabbIndexOpRangeContains || operation == kAabbIndexOpRangeIntersects)
            && prepared_queries->operation != kAabbIndexOpRangeContains)
        throw std::runtime_error("box query operation requires prepared box queries");
    if (operation == kAabbIndexOpRangeIntersects) {
        count_prepared_aabb_index_2d_range_intersects_optix(prepared, prepared_queries, hit_count_out);
        return;
    }
    count_prepared_aabb_index_2d_device_optix(
        prepared,
        prepared_queries->d_point_queries.ptr,
        operation == kAabbIndexOpPointContains ? prepared_queries->query_count : 0,
        prepared_queries->d_box_queries.ptr,
        operation == kAabbIndexOpRangeContains ? prepared_queries->query_count : 0,
        operation,
        hit_count_out);
}

static void collect_prepared_aabb_index_2d_range_intersection_rows_optix(
        PreparedAabbIndex2DOptix* prepared,
        const RtdlAabb2D* box_queries,
        size_t box_query_count,
        RtdlAabbPairRow* rows_out,
        size_t row_capacity,
        size_t* emitted_count_out,
        uint32_t* overflowed_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX AABB index handle must not be null");
    if (!emitted_count_out) throw std::runtime_error("emitted_count_out must not be null");
    if (!overflowed_out) throw std::runtime_error("overflowed_out must not be null");
    if (!rows_out && row_capacity != 0)
        throw std::runtime_error("rows_out pointer must not be null when row_capacity is nonzero");
    if (!box_queries && box_query_count != 0)
        throw std::runtime_error("box_queries pointer must not be null when box_query_count is nonzero");
    if (prepared->box_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("indexed box count exceeds uint32 launch limit");
    if (box_query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("box query count exceeds uint32 launch limit");
    if (row_capacity > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("AABB row output capacity exceeds uint32 launch limit");

    *emitted_count_out = 0;
    *overflowed_out = 0;
    if (prepared->box_count == 0 || box_query_count == 0)
        return;

    PreparedAabbIndexQueries2DOptix prepared_queries(box_queries, box_query_count);
    DevPtr d_hit_count(sizeof(unsigned long long));
    unsigned long long zero = 0ULL;
    upload(d_hit_count.ptr, &zero, 1);
    DevPtr d_rows(sizeof(RtdlAabbPairRow) * row_capacity);

    launch_aabb_index_count_pass_optix(
        prepared->accel.handle,
        0,
        0,
        prepared_queries.d_box_queries.ptr,
        prepared_queries.query_count,
        prepared->d_boxes.ptr,
        prepared->box_count,
        kAabbIndexOpRangeIntersects,
        kAabbIndexIntersectForwardPass,
        prepared_queries.query_count,
        d_hit_count.ptr,
        d_rows.ptr,
        row_capacity,
        true);
    launch_aabb_index_count_pass_optix(
        prepared_queries.accel.handle,
        0,
        0,
        prepared_queries.d_box_queries.ptr,
        prepared_queries.query_count,
        prepared->d_boxes.ptr,
        prepared->box_count,
        kAabbIndexOpRangeIntersects,
        kAabbIndexIntersectBackwardPass,
        prepared->box_count,
        d_hit_count.ptr,
        d_rows.ptr,
        row_capacity,
        true);

    unsigned long long raw_count = 0ULL;
    download(&raw_count, d_hit_count.ptr, 1);
    if (raw_count > static_cast<unsigned long long>(std::numeric_limits<size_t>::max()))
        throw std::runtime_error("AABB row output count exceeds size_t range");
    const size_t emitted = static_cast<size_t>(raw_count);
    *emitted_count_out = emitted;
    if (emitted > row_capacity) {
        *overflowed_out = 1;
        return;
    }

    std::vector<RtdlAabbPairRow> rows(emitted);
    if (emitted != 0)
        download(rows.data(), d_rows.ptr, emitted);
    std::sort(rows.begin(), rows.end(), [](const RtdlAabbPairRow& a, const RtdlAabbPairRow& b) {
        if (a.query_id != b.query_id)
            return a.query_id < b.query_id;
        return a.indexed_id < b.indexed_id;
    });
    rows.erase(std::unique(rows.begin(), rows.end(), [](const RtdlAabbPairRow& a, const RtdlAabbPairRow& b) {
        return a.query_id == b.query_id && a.indexed_id == b.indexed_id;
    }), rows.end());
    *emitted_count_out = rows.size();
    if (!rows.empty())
        std::memcpy(rows_out, rows.data(), sizeof(RtdlAabbPairRow) * rows.size());
}

static void collect_prepared_aabb_index_2d_point_contains_rows_optix(
        PreparedAabbIndex2DOptix* prepared,
        const RtdlPoint* point_queries,
        size_t point_query_count,
        RtdlAabbPairRow* rows_out,
        size_t row_capacity,
        size_t* emitted_count_out,
        uint32_t* overflowed_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX AABB index handle must not be null");
    if (!emitted_count_out) throw std::runtime_error("emitted_count_out must not be null");
    if (!overflowed_out) throw std::runtime_error("overflowed_out must not be null");
    if (!rows_out && row_capacity != 0)
        throw std::runtime_error("rows_out pointer must not be null when row_capacity is nonzero");
    if (!point_queries && point_query_count != 0)
        throw std::runtime_error("point_queries pointer must not be null when point_query_count is nonzero");
    if (prepared->box_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("indexed box count exceeds uint32 launch limit");
    if (point_query_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("point query count exceeds uint32 launch limit");
    if (row_capacity > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("AABB row output capacity exceeds uint32 launch limit");

    *emitted_count_out = 0;
    *overflowed_out = 0;
    if (prepared->box_count == 0 || point_query_count == 0)
        return;

    std::vector<GpuPoint> gpu_points(point_query_count);
    for (size_t i = 0; i < point_query_count; ++i)
        gpu_points[i] = pack_aabb_index_point_query_for_gpu(point_queries[i]);
    DevPtr d_points(sizeof(GpuPoint) * point_query_count);
    upload(d_points.ptr, gpu_points.data(), gpu_points.size());

    DevPtr d_hit_count(sizeof(unsigned long long));
    unsigned long long zero = 0ULL;
    upload(d_hit_count.ptr, &zero, 1);
    DevPtr d_rows(sizeof(RtdlAabbPairRow) * row_capacity);

    launch_aabb_index_count_pass_optix(
        prepared->accel.handle,
        d_points.ptr,
        point_query_count,
        0,
        0,
        prepared->d_boxes.ptr,
        prepared->box_count,
        kAabbIndexOpPointContains,
        0u,
        point_query_count,
        d_hit_count.ptr,
        d_rows.ptr,
        row_capacity,
        true);

    unsigned long long raw_count = 0ULL;
    download(&raw_count, d_hit_count.ptr, 1);
    if (raw_count > static_cast<unsigned long long>(std::numeric_limits<size_t>::max()))
        throw std::runtime_error("AABB point row output count exceeds size_t range");
    const size_t emitted = static_cast<size_t>(raw_count);
    *emitted_count_out = emitted;
    if (emitted > row_capacity) {
        *overflowed_out = 1;
        return;
    }

    std::vector<RtdlAabbPairRow> rows(emitted);
    if (emitted != 0)
        download(rows.data(), d_rows.ptr, emitted);
    std::sort(rows.begin(), rows.end(), [](const RtdlAabbPairRow& a, const RtdlAabbPairRow& b) {
        if (a.query_id != b.query_id)
            return a.query_id < b.query_id;
        return a.indexed_id < b.indexed_id;
    });
    rows.erase(std::unique(rows.begin(), rows.end(), [](const RtdlAabbPairRow& a, const RtdlAabbPairRow& b) {
        return a.query_id == b.query_id && a.indexed_id == b.indexed_id;
    }), rows.end());
    *emitted_count_out = rows.size();
    if (!rows.empty())
        std::memcpy(rows_out, rows.data(), sizeof(RtdlAabbPairRow) * rows.size());
}

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

struct RayClosestHit3DLaunchParams {
    OptixTraversableHandle   traversable;
    const GpuRay3DHost*      rays;
    const GpuTriangle3DHost* triangles;
    GpuRayClosestHitRecord*  output;
    uint32_t                 ray_count;
};

struct RayHitCount3DSumLaunchParams {
    OptixTraversableHandle   traversable;
    const GpuRay3DHost*      rays;
    const GpuTriangle3DHost* triangles;
    unsigned long long*      hit_count_sum;
    uint32_t                 ray_count;
};

struct RayAnyHitWeightedSum3DLaunchParams {
    OptixTraversableHandle    traversable;
    const GpuRay3DHost*       rays;
    const GpuTriangle3DHost*  triangles;
    const unsigned long long* ray_weights;
    unsigned long long*       weighted_hit_sum;
    uint32_t                  ray_count;
};

struct RayPrimitiveGroupedI64Reduction3DLaunchParams {
    OptixTraversableHandle    traversable;
    const GpuRay3DHost*       rays;
    const GpuTriangle3DHost*  triangles;
    const uint32_t*           primitive_group_ids;
    const unsigned long long* primitive_values;
    uint32_t*                 primitive_flags;
    unsigned long long*       group_counts;
    unsigned long long*       group_sums;
    unsigned long long*       group_mins;
    unsigned long long*       group_maxs;
    unsigned long long*       hit_event_count;
    uint32_t                  ray_count;
    uint32_t                  triangle_count;
    uint32_t                  group_count;
    uint32_t                  reduction;
};

struct RayTriangleHitStream3DLaunchParams {
    OptixTraversableHandle       traversable;
    const GpuRay3DHost*          rays;
    const GpuTriangle3DHost*     triangles;
    RtdlRayTriangleHitStreamRow* rows;
    unsigned long long*          row_count;
    unsigned long long*          hit_event_count;
    uint32_t*                    overflow;
    uint32_t*                    primitive_flags;
    uint32_t                     ray_count;
    uint32_t                     triangle_count;
    uint32_t                     max_rows;
    uint32_t                     deduplicate_primitives;
};

struct RayTriangleHitStreamDeviceColumns3DLaunchParams {
    OptixTraversableHandle   traversable;
    const GpuRay3DHost*      rays;
    const GpuTriangle3DHost* triangles;
    unsigned long long*      ray_ids;
    unsigned long long*      primitive_ids;
    unsigned long long*      row_count;
    unsigned long long*      hit_event_count;
    uint32_t*                overflow;
    uint32_t*                primitive_flags;
    uint32_t                 ray_count;
    uint32_t                 triangle_count;
    uint32_t                 max_rows;
    uint32_t                 deduplicate_primitives;
};

struct NativeRayTriangleHitStreamDeviceColumnsOwner {
    CUdeviceptr ray_ids = 0;
    CUdeviceptr primitive_ids = 0;

    ~NativeRayTriangleHitStreamDeviceColumnsOwner() {
        if (ray_ids) cuMemFree(ray_ids);
        if (primitive_ids) cuMemFree(primitive_ids);
    }
};

struct NativeRayTriangleHitStreamAsyncLaunchOwner {
    CUdeviceptr rays = 0;
    CUdeviceptr primitive_flags = 0;
    CUdeviceptr params = 0;
    void* host_rays = nullptr;
    void* host_params = nullptr;
    CUstream producer_stream = 0;

    ~NativeRayTriangleHitStreamAsyncLaunchOwner() {
        if (producer_stream) cuStreamSynchronize(producer_stream);
        if (params) cuMemFree(params);
        if (primitive_flags) cuMemFree(primitive_flags);
        if (rays) cuMemFree(rays);
        if (host_params) cuMemFreeHost(host_params);
        if (host_rays) cuMemFreeHost(host_rays);
    }
};

struct RayAnyHitGroupFlags3DLaunchParams {
    OptixTraversableHandle   traversable;
    const GpuRay3DHost*      rays;
    const GpuTriangle3DHost* triangles;
    const uint32_t*          group_indices;
    uint32_t*                group_flags;
    uint32_t                 ray_count;
    uint32_t                 group_count;
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

static void ensure_ray_closest_hit_3d_pipeline()
{
    std::call_once(g_rayclosest3d.init, [&]() {
        std::string ptx = compile_to_ptx(kRayClosestHit3DKernelSrc, "rayclosest3d_kernel.cu");
        g_rayclosest3d.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayclosest3d_probe",
            "__miss__rayclosest3d_miss",
            "__intersection__rayclosest3d_isect",
            nullptr,
            "__closesthit__rayclosest3d_closesthit",
            1).release();
    });
}

static void ensure_ray_closest_hit_grouped_argmin_kernels()
{
    (void)get_optix_context();
    std::call_once(g_rayclosest3d_grouped_argmin.init, [&]() {
        const std::string cubin = compile_to_cubin(
            kRayClosestHitGroupedArgminKernelSrc,
            "rayclosest3d_grouped_argmin_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_rayclosest3d_grouped_argmin.module, cubin.data()));
        CU_CHECK(cuModuleGetFunction(
            &g_rayclosest3d_grouped_argmin.init_fn,
            g_rayclosest3d_grouped_argmin.module,
            "closest_hit_grouped_argmin_init"));
        CU_CHECK(cuModuleGetFunction(
            &g_rayclosest3d_grouped_argmin.min_key_fn,
            g_rayclosest3d_grouped_argmin.module,
            "closest_hit_grouped_argmin_min_key"));
        CU_CHECK(cuModuleGetFunction(
            &g_rayclosest3d_grouped_argmin.scatter_unique_fn,
            g_rayclosest3d_grouped_argmin.module,
            "closest_hit_grouped_argmin_scatter_unique"));
        CU_CHECK(cuModuleGetFunction(
            &g_rayclosest3d_grouped_argmin.min_index_fn,
            g_rayclosest3d_grouped_argmin.module,
            "closest_hit_grouped_argmin_min_index"));
        CU_CHECK(cuModuleGetFunction(
            &g_rayclosest3d_grouped_argmin.materialize_fn,
            g_rayclosest3d_grouped_argmin.module,
            "closest_hit_grouped_argmin_materialize"));
        CU_CHECK(cuModuleGetFunction(
            &g_rayclosest3d_grouped_argmin.merge_two_fn,
            g_rayclosest3d_grouped_argmin.module,
            "closest_hit_grouped_argmin_merge_two"));
        CU_CHECK(cuModuleGetFunction(
            &g_rayclosest3d_grouped_argmin.candidate_min_key_fn,
            g_rayclosest3d_grouped_argmin.module,
            "grouped_candidate_argmin_min_key"));
        CU_CHECK(cuModuleGetFunction(
            &g_rayclosest3d_grouped_argmin.candidate_min_index_fn,
            g_rayclosest3d_grouped_argmin.module,
            "grouped_candidate_argmin_min_index"));
    });
}

static void run_ray_closest_hit_3d_optix(
        const RtdlRay3D*      rays,      size_t ray_count,
        const RtdlTriangle3D* triangles, size_t triangle_count,
        RtdlRayClosestHitRow** rows_out, size_t* row_count_out)
{
    if (ray_count == 0 || triangle_count == 0) {
        *rows_out = nullptr;
        *row_count_out = 0;
        return;
    }
    if (!rays || !triangles)
        throw std::runtime_error("ray and triangle pointers must not be null when counts are nonzero");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("3-D ray closest-hit ray count exceeds uint32_t launch capacity");
    if (triangle_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("3-D ray closest-hit triangle count exceeds uint32_t primitive capacity");

    ensure_ray_closest_hit_3d_pipeline();

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        const double values[7] = {
            rays[i].ox, rays[i].oy, rays[i].oz,
            rays[i].dx, rays[i].dy, rays[i].dz,
            rays[i].tmax,
        };
        for (double value : values) {
            if (!std::isfinite(value))
                throw std::runtime_error("3-D ray closest-hit inputs must be finite");
        }
        gpu_rays[i] = {
            static_cast<float>(rays[i].ox),
            static_cast<float>(rays[i].oy),
            static_cast<float>(rays[i].oz),
            static_cast<float>(rays[i].dx),
            static_cast<float>(rays[i].dy),
            static_cast<float>(rays[i].dz),
            static_cast<float>(rays[i].tmax),
            rays[i].id
        };
    }

    std::vector<GpuTriangle3DHost> gpu_tris(triangle_count);
    for (size_t i = 0; i < triangle_count; ++i) {
        const double values[9] = {
            triangles[i].x0, triangles[i].y0, triangles[i].z0,
            triangles[i].x1, triangles[i].y1, triangles[i].z1,
            triangles[i].x2, triangles[i].y2, triangles[i].z2,
        };
        for (double value : values) {
            if (!std::isfinite(value))
                throw std::runtime_error("3-D triangle closest-hit inputs must be finite");
        }
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

    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
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

    DevPtr d_output(sizeof(GpuRayClosestHitRecord) * ray_count);

    RayClosestHit3DLaunchParams lp;
    lp.traversable = accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle3DHost*>(d_tris.ptr);
    lp.output      = reinterpret_cast<GpuRayClosestHitRecord*>(d_output.ptr);
    lp.ray_count   = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayClosestHit3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayclosest3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayClosestHit3DLaunchParams),
                             &g_rayclosest3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuRayClosestHitRecord> gpu_rows(ray_count);
    download(gpu_rows.data(), d_output.ptr, ray_count);

    size_t hit_count = 0;
    for (const auto& row : gpu_rows) {
        if (row.has_hit != 0u)
            ++hit_count;
    }
    auto* out = static_cast<RtdlRayClosestHitRow*>(
        std::malloc(sizeof(RtdlRayClosestHitRow) * hit_count));
    if (!out && hit_count > 0) throw std::bad_alloc();
    size_t out_index = 0;
    for (const auto& row : gpu_rows) {
        if (row.has_hit == 0u)
            continue;
        out[out_index].ray_id = row.ray_id;
        out[out_index].triangle_id = row.triangle_id;
        out[out_index].t = static_cast<double>(row.t);
        ++out_index;
    }
    *rows_out = out;
    *row_count_out = hit_count;
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

static void ensure_ray_anyhit_3d_pipeline()
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
}

static std::string ray_hitcount_sum_kernel_source_3d()
{
    std::string src(kRayHitCount3DKernelSrc);
    const std::string old_output_field =
        "    RayHitCount3DRecord*     output;\n"
        "    uint32_t                 ray_count;\n";
    const std::string new_output_field =
        "    unsigned long long*      hit_count_sum;\n"
        "    uint32_t                 ray_count;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D hit-count sum params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_zero_write =
        "        params.output[idx] = {r.id, 0u};\n"
        "        return;\n";
    const std::string new_zero_write =
        "        return;\n";
    pos = src.find(old_zero_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D hit-count sum zero-ray path");
    src.replace(pos, old_zero_write.size(), new_zero_write);

    const std::string old_final_write =
        "    params.output[idx] = {r.id, p1};\n";
    const std::string new_final_write =
        "    if (p1 != 0u) atomicAdd(params.hit_count_sum, static_cast<unsigned long long>(p1));\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D hit-count sum output path");
    src.replace(pos, old_final_write.size(), new_final_write);
    return src;
}

static void ensure_ray_hitcount_sum_3d_pipeline()
{
    std::call_once(g_rayhit3d_sum.init, [&]() {
        std::string src = ray_hitcount_sum_kernel_source_3d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayhitcount_sum3d_kernel.cu");
        g_rayhit3d_sum.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit3d_probe",
            "__miss__rayhit3d_miss",
            "__intersection__rayhit3d_isect",
            "__anyhit__rayhit3d_anyhit",
            nullptr, 2).release();
    });
}

static std::string ray_anyhit_weighted_sum_kernel_source_3d()
{
    std::string src = ray_anyhit_kernel_source_3d();
    const std::string old_output_field =
        "    RayHitCount3DRecord*     output;\n"
        "    uint32_t                 ray_count;\n";
    const std::string new_output_field =
        "    const unsigned long long* ray_weights;\n"
        "    unsigned long long*       weighted_hit_sum;\n"
        "    uint32_t                  ray_count;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D weighted any-hit sum params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_zero_write =
        "        params.output[idx] = {r.id, 0u};\n"
        "        return;\n";
    const std::string new_zero_write =
        "        return;\n";
    pos = src.find(old_zero_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D weighted any-hit sum zero-ray path");
    src.replace(pos, old_zero_write.size(), new_zero_write);

    const std::string old_final_write =
        "    params.output[idx] = {r.id, p1};\n";
    const std::string new_final_write =
        "    if (p1 != 0u) atomicAdd(params.weighted_hit_sum, params.ray_weights[idx]);\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D weighted any-hit sum output path");
    src.replace(pos, old_final_write.size(), new_final_write);
    return src;
}

static void ensure_ray_anyhit_weighted_sum_3d_pipeline()
{
    std::call_once(g_rayanyhit_weighted_sum3d.init, [&]() {
        std::string src = ray_anyhit_weighted_sum_kernel_source_3d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_weighted_sum3d_kernel.cu");
        g_rayanyhit_weighted_sum3d.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit3d_probe",
            "__miss__rayhit3d_miss",
            "__intersection__rayhit3d_isect",
            "__anyhit__rayhit3d_anyhit",
            nullptr, 2).release();
    });
}

static std::string ray_primitive_grouped_i64_reduction_kernel_source_3d()
{
    std::string src(kRayHitCount3DKernelSrc);
    const std::string old_output_field =
        "    RayHitCount3DRecord*     output;\n"
        "    uint32_t                 ray_count;\n";
    const std::string new_output_field =
        "    const uint32_t*           primitive_group_ids;\n"
        "    const unsigned long long* primitive_values;\n"
        "    uint32_t*                 primitive_flags;\n"
        "    unsigned long long*       group_counts;\n"
        "    unsigned long long*       group_sums;\n"
        "    unsigned long long*       group_mins;\n"
        "    unsigned long long*       group_maxs;\n"
        "    unsigned long long*       hit_event_count;\n"
        "    uint32_t                  ray_count;\n"
        "    uint32_t                  triangle_count;\n"
        "    uint32_t                  group_count;\n"
        "    uint32_t                  reduction;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D primitive grouped reduction params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_zero_write =
        "        params.output[idx] = {r.id, 0u};\n"
        "        return;\n";
    const std::string new_zero_write =
        "        return;\n";
    pos = src.find(old_zero_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D primitive grouped reduction zero-ray path");
    src.replace(pos, old_zero_write.size(), new_zero_write);

    const std::string old_final_write =
        "    params.output[idx] = {r.id, p1};\n";
    const std::string new_final_write =
        "    (void)p1;\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D primitive grouped reduction output path");
    src.replace(pos, old_final_write.size(), new_final_write);

    const std::string old_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit3d_anyhit() {\n"
        "    // Count this hit and keep traversing all triangles.\n"
        "    uint32_t count = optixGetPayload_1();\n"
        "    optixSetPayload_1(count + 1u);\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    const std::string new_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit3d_anyhit() {\n"
        "    const uint32_t prim = optixGetPrimitiveIndex();\n"
        "    if (prim >= params.triangle_count) {\n"
        "        optixIgnoreIntersection();\n"
        "        return;\n"
        "    }\n"
        "    atomicAdd(params.hit_event_count, 1ull);\n"
        "    const uint32_t word = prim >> 5;\n"
        "    const uint32_t mask = 1u << (prim & 31u);\n"
        "    const uint32_t old = atomicOr(&params.primitive_flags[word], mask);\n"
        "    if ((old & mask) == 0u) {\n"
        "        const uint32_t group = params.primitive_group_ids[prim];\n"
        "        if (group < params.group_count) {\n"
        "            const unsigned long long value = params.primitive_values[prim];\n"
        "            if (params.reduction == 1u) {\n"
        "                atomicAdd(&params.group_counts[group], 1ull);\n"
        "            } else if (params.reduction == 2u) {\n"
        "                atomicAdd(&params.group_sums[group], value);\n"
        "            } else if (params.reduction == 3u) {\n"
        "                atomicMin(&params.group_mins[group], value);\n"
        "            } else if (params.reduction == 4u) {\n"
        "                atomicMax(&params.group_maxs[group], value);\n"
        "            } else if (params.reduction == 5u) {\n"
        "                atomicAdd(&params.group_counts[group], 1ull);\n"
        "                atomicAdd(&params.group_sums[group], value);\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    pos = src.find(old_anyhit);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D primitive grouped reduction any-hit path");
    src.replace(pos, old_anyhit.size(), new_anyhit);
    return src;
}

static void ensure_ray_primitive_grouped_i64_reduction_3d_pipeline()
{
    std::call_once(g_rayprimitive_grouped_i64_reduction3d.init, [&]() {
        std::string src = ray_primitive_grouped_i64_reduction_kernel_source_3d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayprimitive_grouped_i64_reduction3d_kernel.cu");
        g_rayprimitive_grouped_i64_reduction3d.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit3d_probe",
            "__miss__rayhit3d_miss",
            "__intersection__rayhit3d_isect",
            "__anyhit__rayhit3d_anyhit",
            nullptr, 2).release();
    });
}

static std::string ray_triangle_hit_stream_kernel_source_3d()
{
    std::string src(kRayHitCount3DKernelSrc);
    const std::string old_output_field =
        "    RayHitCount3DRecord*     output;\n"
        "    uint32_t                 ray_count;\n";
    const std::string new_output_field =
        "    struct HitStreamRow { uint32_t ray_id; uint32_t primitive_id; };\n"
        "    HitStreamRow*            rows;\n"
        "    unsigned long long*      row_count;\n"
        "    unsigned long long*      hit_event_count;\n"
        "    uint32_t*                overflow;\n"
        "    uint32_t*                primitive_flags;\n"
        "    uint32_t                 ray_count;\n"
        "    uint32_t                 triangle_count;\n"
        "    uint32_t                 max_rows;\n"
        "    uint32_t                 deduplicate_primitives;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D hit-stream params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_zero_write =
        "        params.output[idx] = {r.id, 0u};\n"
        "        return;\n";
    const std::string new_zero_write =
        "        return;\n";
    pos = src.find(old_zero_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D hit-stream zero-ray path");
    src.replace(pos, old_zero_write.size(), new_zero_write);

    const std::string old_final_write =
        "    params.output[idx] = {r.id, p1};\n";
    const std::string new_final_write =
        "    (void)p1;\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D hit-stream final write path");
    src.replace(pos, old_final_write.size(), new_final_write);

    const std::string old_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit3d_anyhit() {\n"
        "    // Count this hit and keep traversing all triangles.\n"
        "    uint32_t count = optixGetPayload_1();\n"
        "    optixSetPayload_1(count + 1u);\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    const std::string new_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit3d_anyhit() {\n"
        "    const uint32_t prim = optixGetPrimitiveIndex();\n"
        "    const uint32_t ridx = optixGetPayload_0();\n"
        "    if (prim >= params.triangle_count || ridx >= params.ray_count) {\n"
        "        optixIgnoreIntersection();\n"
        "        return;\n"
        "    }\n"
        "    atomicAdd(params.hit_event_count, 1ull);\n"
        "    bool should_emit = true;\n"
        "    if (params.deduplicate_primitives != 0u) {\n"
        "        const uint32_t word = prim >> 5;\n"
        "        const uint32_t mask = 1u << (prim & 31u);\n"
        "        const uint32_t old = atomicOr(&params.primitive_flags[word], mask);\n"
        "        should_emit = ((old & mask) == 0u);\n"
        "    }\n"
        "    if (should_emit) {\n"
        "        const unsigned long long slot = atomicAdd(params.row_count, 1ull);\n"
        "        if (slot < static_cast<unsigned long long>(params.max_rows)) {\n"
        "            params.rows[slot] = {params.rays[ridx].id, prim};\n"
        "        } else {\n"
        "            atomicExch(params.overflow, 1u);\n"
        "        }\n"
        "    }\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    pos = src.find(old_anyhit);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D hit-stream any-hit path");
    src.replace(pos, old_anyhit.size(), new_anyhit);
    return src;
}

static void ensure_ray_triangle_hit_stream_3d_pipeline()
{
    std::call_once(g_raytriangle_hitstream3d.init, [&]() {
        std::string src = ray_triangle_hit_stream_kernel_source_3d();
        std::string ptx = compile_to_ptx(src.c_str(), "raytriangle_hitstream3d_kernel.cu");
        g_raytriangle_hitstream3d.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit3d_probe",
            "__miss__rayhit3d_miss",
            "__intersection__rayhit3d_isect",
            "__anyhit__rayhit3d_anyhit",
            nullptr, 2).release();
    });
}

static std::string ray_triangle_hit_stream_device_columns_kernel_source_3d()
{
    std::string src(kRayHitCount3DKernelSrc);
    const std::string old_output_field =
        "    RayHitCount3DRecord*     output;\n"
        "    uint32_t                 ray_count;\n";
    const std::string new_output_field =
        "    unsigned long long*      ray_ids;\n"
        "    unsigned long long*      primitive_ids;\n"
        "    unsigned long long*      row_count;\n"
        "    unsigned long long*      hit_event_count;\n"
        "    uint32_t*                overflow;\n"
        "    uint32_t*                primitive_flags;\n"
        "    uint32_t                 ray_count;\n"
        "    uint32_t                 triangle_count;\n"
        "    uint32_t                 max_rows;\n"
        "    uint32_t                 deduplicate_primitives;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D device-column hit-stream params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_zero_write =
        "        params.output[idx] = {r.id, 0u};\n"
        "        return;\n";
    const std::string new_zero_write =
        "        return;\n";
    pos = src.find(old_zero_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D device-column zero-ray path");
    src.replace(pos, old_zero_write.size(), new_zero_write);

    const std::string old_final_write =
        "    params.output[idx] = {r.id, p1};\n";
    const std::string new_final_write =
        "    (void)p1;\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D device-column final write path");
    src.replace(pos, old_final_write.size(), new_final_write);

    const std::string old_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit3d_anyhit() {\n"
        "    // Count this hit and keep traversing all triangles.\n"
        "    uint32_t count = optixGetPayload_1();\n"
        "    optixSetPayload_1(count + 1u);\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    const std::string new_anyhit =
        "extern \"C\" __global__ void __anyhit__rayhit3d_anyhit() {\n"
        "    const uint32_t prim = optixGetPrimitiveIndex();\n"
        "    const uint32_t ridx = optixGetPayload_0();\n"
        "    if (prim >= params.triangle_count || ridx >= params.ray_count) {\n"
        "        optixIgnoreIntersection();\n"
        "        return;\n"
        "    }\n"
        "    atomicAdd(params.hit_event_count, 1ull);\n"
        "    bool should_emit = true;\n"
        "    if (params.deduplicate_primitives != 0u) {\n"
        "        const uint32_t word = prim >> 5;\n"
        "        const uint32_t mask = 1u << (prim & 31u);\n"
        "        const uint32_t old = atomicOr(&params.primitive_flags[word], mask);\n"
        "        should_emit = ((old & mask) == 0u);\n"
        "    }\n"
        "    if (should_emit) {\n"
        "        const unsigned long long slot = atomicAdd(params.row_count, 1ull);\n"
        "        if (slot < static_cast<unsigned long long>(params.max_rows)) {\n"
        "            params.ray_ids[slot] = static_cast<unsigned long long>(params.rays[ridx].id);\n"
        "            params.primitive_ids[slot] = static_cast<unsigned long long>(prim);\n"
        "        } else {\n"
        "            atomicExch(params.overflow, 1u);\n"
        "        }\n"
        "    }\n"
        "    optixIgnoreIntersection();\n"
        "}\n";
    pos = src.find(old_anyhit);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D device-column hit-stream any-hit path");
    src.replace(pos, old_anyhit.size(), new_anyhit);
    return src;
}

static void ensure_ray_triangle_hit_stream_device_columns_3d_pipeline()
{
    std::call_once(g_raytriangle_hitstream_device_columns3d.init, [&]() {
        std::string src = ray_triangle_hit_stream_device_columns_kernel_source_3d();
        std::string ptx = compile_to_ptx(src.c_str(), "raytriangle_hitstream_device_columns3d_kernel.cu");
        g_raytriangle_hitstream_device_columns3d.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit3d_probe",
            "__miss__rayhit3d_miss",
            "__intersection__rayhit3d_isect",
            "__anyhit__rayhit3d_anyhit",
            nullptr, 2).release();
    });
}

static std::string ray_anyhit_group_flags_kernel_source_3d()
{
    std::string src = ray_anyhit_kernel_source_3d();
    const std::string old_output_field =
        "    RayHitCount3DRecord*     output;\n"
        "    uint32_t                 ray_count;\n";
    const std::string new_output_field =
        "    const uint32_t*          group_indices;\n"
        "    uint32_t*                group_flags;\n"
        "    uint32_t                 ray_count;\n"
        "    uint32_t                 group_count;\n";
    size_t pos = src.find(old_output_field);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D any-hit group-flags params");
    src.replace(pos, old_output_field.size(), new_output_field);

    const std::string old_zero_write =
        "        params.output[idx] = {r.id, 0u};\n"
        "        return;\n";
    const std::string new_zero_write =
        "        return;\n";
    pos = src.find(old_zero_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D any-hit group-flags zero-ray path");
    src.replace(pos, old_zero_write.size(), new_zero_write);

    const std::string old_final_write =
        "    params.output[idx] = {r.id, p1};\n";
    const std::string new_final_write =
        "    if (p1 != 0u) {\n"
        "        const uint32_t group_index = params.group_indices[idx];\n"
        "        if (group_index < params.group_count) {\n"
        "            atomicExch(&params.group_flags[group_index], 1u);\n"
        "        }\n"
        "    }\n";
    pos = src.find(old_final_write);
    if (pos == std::string::npos)
        throw std::runtime_error("failed to specialize OptiX 3-D any-hit group-flags output path");
    src.replace(pos, old_final_write.size(), new_final_write);
    return src;
}

static void ensure_ray_anyhit_group_flags_3d_pipeline()
{
    std::call_once(g_rayanyhit_group_flags3d.init, [&]() {
        std::string src = ray_anyhit_group_flags_kernel_source_3d();
        std::string ptx = compile_to_ptx(src.c_str(), "rayanyhit_group_flags3d_kernel.cu");
        g_rayanyhit_group_flags3d.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__rayhit3d_probe",
            "__miss__rayhit3d_miss",
            "__intersection__rayhit3d_isect",
            "__anyhit__rayhit3d_anyhit",
            nullptr, 2).release();
    });
}

static PreparedStaticTriangleScene3D* prepare_static_triangle_scene_3d_optix(
        const RtdlTriangle3D* triangles,
        size_t triangle_count)
{
    return new PreparedStaticTriangleScene3D(triangles, triangle_count);
}

static PreparedStaticTriangleScene3D* prepare_static_triangle_scene_3d_device_triangles_optix(
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
        size_t triangle_count)
{
    return new PreparedStaticTriangleScene3D(
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
}

static PreparedPrimitiveGroupedI64Payload3D* prepare_primitive_grouped_i64_payload_3d_optix(
        const uint32_t* primitive_group_ids,
        size_t primitive_group_id_count,
        const uint64_t* primitive_values,
        size_t primitive_value_count,
        size_t group_count)
{
    return new PreparedPrimitiveGroupedI64Payload3D(
        primitive_group_ids,
        primitive_group_id_count,
        primitive_values,
        primitive_value_count,
        group_count);
}

static PreparedRayBatch3D* prepare_ray_batch_3d_optix(
        const RtdlRay3D* rays,
        size_t ray_count)
{
    return new PreparedRayBatch3D(rays, ray_count);
}

static PreparedRayBatch3D* prepare_ray_batch_3d_device_rays_optix(
        const uint32_t* ray_ids,
        const double* ray_ox,
        const double* ray_oy,
        const double* ray_oz,
        const double* ray_dx,
        const double* ray_dy,
        const double* ray_dz,
        const double* ray_tmax,
        size_t ray_count)
{
    return new PreparedRayBatch3D(
        ray_ids,
        ray_ox,
        ray_oy,
        ray_oz,
        ray_dx,
        ray_dy,
        ray_dz,
        ray_tmax,
        ray_count);
}

static PreparedClosestHitGroupedArgmin3D* prepare_closest_hit_grouped_argmin_3d_optix(
        const uint32_t* ray_group_ids,
        size_t ray_group_id_count,
        const double* candidate_values,
        const uint32_t* candidate_indices,
        size_t candidate_count,
        size_t group_count)
{
    return new PreparedClosestHitGroupedArgmin3D(
        ray_group_ids,
        ray_group_id_count,
        candidate_values,
        candidate_indices,
        candidate_count,
        group_count);
}

static PreparedGroupedCandidateArgmin* prepare_grouped_candidate_argmin_optix(
        const uint32_t* candidate_group_ids,
        const double* candidate_values,
        const uint32_t* candidate_indices,
        size_t candidate_count,
        size_t group_count)
{
    return new PreparedGroupedCandidateArgmin(
        candidate_group_ids,
        candidate_values,
        candidate_indices,
        candidate_count,
        group_count);
}

static PreparedGroupedSegmentQuery3D* prepare_static_triangle_scene_3d_grouped_segment_query_optix(
        const RtdlSegment3D* segments,
        size_t segment_count,
        const uint32_t* group_offsets,
        size_t group_count)
{
    return new PreparedGroupedSegmentQuery3D(
        segments,
        segment_count,
        group_offsets,
        group_count);
}

static void run_prepared_static_triangle_scene_3d_grouped_segment_any_hit_flags_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlSegment3D* segments,
        size_t segment_count,
        const uint32_t* group_offsets,
        size_t group_count,
        uint8_t* flags_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!segments && segment_count != 0)
        throw std::runtime_error("segment pointer must not be null when segment_count is nonzero");
    if (!group_offsets && group_count != 0)
        throw std::runtime_error("group offsets pointer must not be null when group_count is nonzero");
    if (!flags_out && group_count != 0)
        throw std::runtime_error("flags output pointer must not be null when group_count is nonzero");
    if (segment_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("segment_count exceeds uint32 launch limit");
    if (group_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("group_count exceeds uint32 limit");

    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    for (size_t group_index = 0; group_index < group_count; ++group_index)
        flags_out[group_index] = 0u;
    if (group_count == 0) {
        if (segment_count != 0)
            throw std::runtime_error("segment_count must be zero when group_count is zero");
        return;
    }
    if (group_offsets[0] != 0u)
        throw std::runtime_error("first group offset must be zero");
    for (size_t group_index = 0; group_index < group_count; ++group_index) {
        const uint32_t begin = group_offsets[group_index];
        const uint32_t end = group_offsets[group_index + 1];
        if (end < begin)
            throw std::runtime_error("group offsets must be monotonic");
        if (static_cast<size_t>(end) > segment_count)
            throw std::runtime_error("group offsets exceed segment_count");
    }
    if (static_cast<size_t>(group_offsets[group_count]) != segment_count)
        throw std::runtime_error("final group offset must equal segment_count");
    if (segment_count == 0 || prepared->triangle_count == 0)
        return;

    std::vector<GpuRay3DHost> gpu_rays(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
        const double values[6] = {
            segments[i].x0, segments[i].y0, segments[i].z0,
            segments[i].x1, segments[i].y1, segments[i].z1,
        };
        for (double value : values) {
            if (!std::isfinite(value))
                throw std::runtime_error("segment coordinates must be finite");
        }
        const double ddx = segments[i].x1 - segments[i].x0;
        const double ddy = segments[i].y1 - segments[i].y0;
        const double ddz = segments[i].z1 - segments[i].z0;
        const double dlen = std::sqrt(ddx * ddx + ddy * ddy + ddz * ddz);
        if (dlen == 0.0)
            throw std::runtime_error("zero-length segments are invalid");
        const float dx = static_cast<float>(ddx);
        const float dy = static_cast<float>(ddy);
        const float dz = static_cast<float>(ddz);
        const float len = std::sqrt(dx * dx + dy * dy + dz * dz);
        if (!(len > 0.0f))
            throw std::runtime_error("segment length is not representable as float32");
        gpu_rays[i] = {
            static_cast<float>(segments[i].x0),
            static_cast<float>(segments[i].y0),
            static_cast<float>(segments[i].z0),
            dx / len, dy / len, dz / len,
            len,
            segments[i].id
        };
    }

    ensure_ray_anyhit_3d_pipeline();

    DevPtr d_rays(sizeof(GpuRay3DHost) * segment_count);
    DevPtr d_output(sizeof(GpuRayAnyHitRecord) * segment_count);
    upload(d_rays.ptr, gpu_rays.data(), segment_count);

    RayHitCount3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.output      = reinterpret_cast<GpuRayHitRecord*>(d_output.ptr);
    lp.ray_count   = static_cast<uint32_t>(segment_count);

    DevPtr d_params(sizeof(RayHitCount3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayHitCount3DLaunchParams),
                             &g_rayanyhit3d.pipe->sbt,
                             static_cast<unsigned>(segment_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<GpuRayAnyHitRecord> gpu_rows(segment_count);
    download(gpu_rows.data(), d_output.ptr, segment_count);
    for (size_t group_index = 0; group_index < group_count; ++group_index) {
        const uint32_t begin = group_offsets[group_index];
        const uint32_t end = group_offsets[group_index + 1];
        for (uint32_t segment_index = begin; segment_index < end; ++segment_index) {
            if (gpu_rows[segment_index].any_hit != 0u) {
                flags_out[group_index] = 1u;
                break;
            }
        }
    }
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_grouped_segment_query_any_hit_flags_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedGroupedSegmentQuery3D* query,
        uint8_t* flags_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!query)
        throw std::runtime_error("prepared query handle must not be null");
    if (!flags_out && query->group_count != 0)
        throw std::runtime_error("flags output pointer must not be null when group_count is nonzero");
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (query->group_count == 0)
        return;

    CUstream stream = 0;
    CU_CHECK(cuMemsetD32(query->d_group_flags.ptr, 0u, query->group_count));
    if (query->segment_count == 0 || prepared->triangle_count == 0) {
        CU_CHECK(cuStreamSynchronize(stream));
        for (size_t group_index = 0; group_index < query->group_count; ++group_index)
            flags_out[group_index] = 0u;
        return;
    }

    ensure_ray_anyhit_group_flags_3d_pipeline();

    RayAnyHitGroupFlags3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay3DHost*>(query->d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.group_indices = reinterpret_cast<const uint32_t*>(query->d_group_indices.ptr);
    lp.group_flags = reinterpret_cast<uint32_t*>(query->d_group_flags.ptr);
    lp.ray_count   = static_cast<uint32_t>(query->segment_count);
    lp.group_count = static_cast<uint32_t>(query->group_count);

    DevPtr d_params(sizeof(RayAnyHitGroupFlags3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_rayanyhit_group_flags3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayAnyHitGroupFlags3DLaunchParams),
                             &g_rayanyhit_group_flags3d.pipe->sbt,
                             static_cast<unsigned>(query->segment_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    std::vector<uint32_t> group_flags(query->group_count, 0u);
    download(group_flags.data(), query->d_group_flags.ptr, query->group_count);
    for (size_t group_index = 0; group_index < query->group_count; ++group_index)
        flags_out[group_index] = group_flags[group_index] != 0u ? 1u : 0u;
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_grouped_segment_query_any_hit_count_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedGroupedSegmentQuery3D* query,
        uint32_t* flagged_group_count_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!query)
        throw std::runtime_error("prepared query handle must not be null");
    if (!flagged_group_count_out)
        throw std::runtime_error("flagged group count output pointer must not be null");
    *flagged_group_count_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (query->group_count == 0)
        return;

    CUstream stream = 0;
    CU_CHECK(cuMemsetD32(query->d_group_flags.ptr, 0u, query->group_count));
    if (query->segment_count == 0 || prepared->triangle_count == 0) {
        CU_CHECK(cuStreamSynchronize(stream));
        return;
    }

    ensure_ray_anyhit_group_flags_3d_pipeline();

    RayAnyHitGroupFlags3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays        = reinterpret_cast<const GpuRay3DHost*>(query->d_rays.ptr);
    lp.triangles   = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.group_indices = reinterpret_cast<const uint32_t*>(query->d_group_indices.ptr);
    lp.group_flags = reinterpret_cast<uint32_t*>(query->d_group_flags.ptr);
    lp.ray_count   = static_cast<uint32_t>(query->segment_count);
    lp.group_count = static_cast<uint32_t>(query->group_count);

    DevPtr d_params(sizeof(RayAnyHitGroupFlags3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_rayanyhit_group_flags3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayAnyHitGroupFlags3DLaunchParams),
                             &g_rayanyhit_group_flags3d.pipe->sbt,
                             static_cast<unsigned>(query->segment_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    std::vector<uint32_t> group_flags(query->group_count, 0u);
    download(group_flags.data(), query->d_group_flags.ptr, query->group_count);
    uint32_t flagged_group_count = 0u;
    for (uint32_t flag : group_flags) {
        if (flag != 0u)
            ++flagged_group_count;
    }
    *flagged_group_count_out = flagged_group_count;
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_ray_any_hit_weighted_sum_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        const uint64_t* ray_weights,
        uint64_t* weighted_hit_sum_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!rays && ray_count != 0)
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    if (!ray_weights && ray_count != 0)
        throw std::runtime_error("ray_weights pointer must not be null when ray_count is nonzero");
    if (!weighted_hit_sum_out)
        throw std::runtime_error("weighted_hit_sum_out must not be null");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    *weighted_hit_sum_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_count == 0 || prepared->triangle_count == 0)
        return;

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    std::vector<unsigned long long> gpu_weights(ray_count);
    for (size_t i = 0; i < ray_count; ++i) {
        gpu_rays[i] = pack_ray_3d_as_gpu_ray(rays[i]);
        gpu_weights[i] = static_cast<unsigned long long>(ray_weights[i]);
    }

    ensure_ray_anyhit_weighted_sum_3d_pipeline();

    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    DevPtr d_weights(sizeof(unsigned long long) * ray_count);
    DevPtr d_sum(sizeof(unsigned long long));
    upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
    upload(d_weights.ptr, gpu_weights.data(), gpu_weights.size());
    unsigned long long zero = 0ull;
    upload(d_sum.ptr, &zero, 1);

    RayAnyHitWeightedSum3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.ray_weights = reinterpret_cast<const unsigned long long*>(d_weights.ptr);
    lp.weighted_hit_sum = reinterpret_cast<unsigned long long*>(d_sum.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayAnyHitWeightedSum3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit_weighted_sum3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayAnyHitWeightedSum3DLaunchParams),
                             &g_rayanyhit_weighted_sum3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    unsigned long long sum = 0ull;
    download(&sum, d_sum.ptr, 1);
    *weighted_hit_sum_out = static_cast<uint64_t>(sum);
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        const uint32_t* primitive_group_ids,
        size_t primitive_group_id_count,
        const uint64_t* primitive_values,
        size_t primitive_value_count,
        size_t group_count,
        uint32_t reduction,
        uint64_t* group_counts_out,
        uint64_t* group_sums_out,
        uint64_t* group_mins_out,
        uint64_t* group_maxs_out,
        uint64_t* hit_event_count_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!rays && ray_count != 0)
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    if (!primitive_group_ids && primitive_group_id_count != 0)
        throw std::runtime_error("primitive_group_ids pointer must not be null when primitive count is nonzero");
    if (!primitive_values && primitive_value_count != 0)
        throw std::runtime_error("primitive_values pointer must not be null when primitive count is nonzero");
    if (primitive_group_id_count != prepared->triangle_count)
        throw std::runtime_error("primitive_group_ids length must match prepared triangle count");
    if (primitive_value_count != prepared->triangle_count)
        throw std::runtime_error("primitive_values length must match prepared triangle count");
    if (!group_counts_out || !group_sums_out || !group_mins_out || !group_maxs_out)
        throw std::runtime_error("group output arrays must not be null");
    if (!hit_event_count_out)
        throw std::runtime_error("hit_event_count_out must not be null");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    if (prepared->triangle_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("triangle_count exceeds uint32 primitive limit");
    if (group_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("group_count exceeds uint32 limit");
    if (reduction != kDeviceColumnGroupedOpCount &&
            reduction != kDeviceColumnGroupedOpSum &&
            reduction != kDeviceColumnGroupedOpMin &&
            reduction != kDeviceColumnGroupedOpMax &&
            reduction != kDeviceColumnGroupedOpSumCount) {
        throw std::runtime_error("unsupported primitive grouped i64 reduction operation");
    }

    for (size_t group_index = 0; group_index < group_count; ++group_index) {
        group_counts_out[group_index] = 0u;
        group_sums_out[group_index] = 0u;
        group_mins_out[group_index] = std::numeric_limits<uint64_t>::max();
        group_maxs_out[group_index] = 0u;
    }
    *hit_event_count_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_count == 0 || prepared->triangle_count == 0 || group_count == 0)
        return;
    for (size_t primitive_index = 0; primitive_index < prepared->triangle_count; ++primitive_index) {
        if (primitive_group_ids[primitive_index] >= group_count)
            throw std::runtime_error("primitive_group_ids entries must be smaller than group_count");
    }

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = pack_ray_3d_as_gpu_ray(rays[i]);

    std::vector<uint32_t> groups(prepared->triangle_count);
    std::vector<unsigned long long> values(prepared->triangle_count);
    for (size_t primitive_index = 0; primitive_index < prepared->triangle_count; ++primitive_index) {
        groups[primitive_index] = primitive_group_ids[primitive_index];
        values[primitive_index] = static_cast<unsigned long long>(primitive_values[primitive_index]);
    }

    ensure_ray_primitive_grouped_i64_reduction_3d_pipeline();

    const size_t flag_word_count = (prepared->triangle_count + 31u) / 32u;
    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    DevPtr d_groups(sizeof(uint32_t) * prepared->triangle_count);
    DevPtr d_values(sizeof(unsigned long long) * prepared->triangle_count);
    DevPtr d_flags(sizeof(uint32_t) * flag_word_count);
    DevPtr d_counts(sizeof(unsigned long long) * group_count);
    DevPtr d_sums(sizeof(unsigned long long) * group_count);
    DevPtr d_mins(sizeof(unsigned long long) * group_count);
    DevPtr d_maxs(sizeof(unsigned long long) * group_count);
    DevPtr d_hit_events(sizeof(unsigned long long));

    upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
    upload(d_groups.ptr, groups.data(), groups.size());
    upload(d_values.ptr, values.data(), values.size());
    CU_CHECK(cuMemsetD32(d_flags.ptr, 0u, flag_word_count));
    CU_CHECK(cuMemsetD32(d_counts.ptr, 0u, group_count * 2u));
    CU_CHECK(cuMemsetD32(d_sums.ptr, 0u, group_count * 2u));
    CU_CHECK(cuMemsetD32(d_maxs.ptr, 0u, group_count * 2u));
    unsigned long long zero = 0ull;
    upload(d_hit_events.ptr, &zero, 1);
    std::vector<unsigned long long> min_init(group_count, std::numeric_limits<unsigned long long>::max());
    upload(d_mins.ptr, min_init.data(), min_init.size());

    RayPrimitiveGroupedI64Reduction3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.primitive_group_ids = reinterpret_cast<const uint32_t*>(d_groups.ptr);
    lp.primitive_values = reinterpret_cast<const unsigned long long*>(d_values.ptr);
    lp.primitive_flags = reinterpret_cast<uint32_t*>(d_flags.ptr);
    lp.group_counts = reinterpret_cast<unsigned long long*>(d_counts.ptr);
    lp.group_sums = reinterpret_cast<unsigned long long*>(d_sums.ptr);
    lp.group_mins = reinterpret_cast<unsigned long long*>(d_mins.ptr);
    lp.group_maxs = reinterpret_cast<unsigned long long*>(d_maxs.ptr);
    lp.hit_event_count = reinterpret_cast<unsigned long long*>(d_hit_events.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);
    lp.triangle_count = static_cast<uint32_t>(prepared->triangle_count);
    lp.group_count = static_cast<uint32_t>(group_count);
    lp.reduction = reduction;

    DevPtr d_params(sizeof(RayPrimitiveGroupedI64Reduction3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayprimitive_grouped_i64_reduction3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayPrimitiveGroupedI64Reduction3DLaunchParams),
                             &g_rayprimitive_grouped_i64_reduction3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<unsigned long long> counts(group_count, 0ull);
    std::vector<unsigned long long> sums(group_count, 0ull);
    std::vector<unsigned long long> mins(group_count, std::numeric_limits<unsigned long long>::max());
    std::vector<unsigned long long> maxs(group_count, 0ull);
    unsigned long long hit_events = 0ull;
    download(counts.data(), d_counts.ptr, group_count);
    download(sums.data(), d_sums.ptr, group_count);
    download(mins.data(), d_mins.ptr, group_count);
    download(maxs.data(), d_maxs.ptr, group_count);
    download(&hit_events, d_hit_events.ptr, 1);
    for (size_t group_index = 0; group_index < group_count; ++group_index) {
        group_counts_out[group_index] = static_cast<uint64_t>(counts[group_index]);
        group_sums_out[group_index] = static_cast<uint64_t>(sums[group_index]);
        group_mins_out[group_index] = static_cast<uint64_t>(mins[group_index]);
        group_maxs_out[group_index] = static_cast<uint64_t>(maxs[group_index]);
    }
    *hit_event_count_out = static_cast<uint64_t>(hit_events);
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        uint32_t deduplicate_primitives,
        RtdlRayTriangleHitStreamRow* rows_out,
        size_t max_rows,
        size_t* row_count_out,
        uint64_t* hit_event_count_out,
        uint32_t* overflow_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!rays && ray_count != 0)
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    if (!rows_out && max_rows != 0)
        throw std::runtime_error("hit stream rows_out pointer must not be null when max_rows is nonzero");
    if (!row_count_out || !hit_event_count_out || !overflow_out)
        throw std::runtime_error("hit stream output counters must not be null");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    if (prepared->triangle_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("triangle_count exceeds uint32 primitive limit");
    if (max_rows > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("max_rows exceeds uint32 hit-stream capacity");

    *row_count_out = 0;
    *hit_event_count_out = 0u;
    *overflow_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_count == 0 || prepared->triangle_count == 0)
        return;

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = pack_ray_3d_as_gpu_ray(rays[i]);

    ensure_ray_triangle_hit_stream_3d_pipeline();

    const size_t flag_word_count = std::max<size_t>(1, (prepared->triangle_count + 31u) / 32u);
    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    DevPtr d_rows(sizeof(RtdlRayTriangleHitStreamRow) * max_rows);
    DevPtr d_row_count(sizeof(unsigned long long));
    DevPtr d_hit_events(sizeof(unsigned long long));
    DevPtr d_overflow(sizeof(uint32_t));
    DevPtr d_flags(sizeof(uint32_t) * flag_word_count);

    upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
    unsigned long long zero64 = 0ull;
    uint32_t zero32 = 0u;
    upload(d_row_count.ptr, &zero64, 1);
    upload(d_hit_events.ptr, &zero64, 1);
    upload(d_overflow.ptr, &zero32, 1);
    CU_CHECK(cuMemsetD32(d_flags.ptr, 0u, flag_word_count));

    RayTriangleHitStream3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.rows = reinterpret_cast<RtdlRayTriangleHitStreamRow*>(d_rows.ptr);
    lp.row_count = reinterpret_cast<unsigned long long*>(d_row_count.ptr);
    lp.hit_event_count = reinterpret_cast<unsigned long long*>(d_hit_events.ptr);
    lp.overflow = reinterpret_cast<uint32_t*>(d_overflow.ptr);
    lp.primitive_flags = reinterpret_cast<uint32_t*>(d_flags.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);
    lp.triangle_count = static_cast<uint32_t>(prepared->triangle_count);
    lp.max_rows = static_cast<uint32_t>(max_rows);
    lp.deduplicate_primitives = deduplicate_primitives != 0u ? 1u : 0u;

    DevPtr d_params(sizeof(RayTriangleHitStream3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_raytriangle_hitstream3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayTriangleHitStream3DLaunchParams),
                             &g_raytriangle_hitstream3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    const auto traversal_end = std::chrono::steady_clock::now();

    unsigned long long attempted_rows = 0ull;
    unsigned long long hit_events = 0ull;
    uint32_t overflow = 0u;
    download(&attempted_rows, d_row_count.ptr, 1);
    download(&hit_events, d_hit_events.ptr, 1);
    download(&overflow, d_overflow.ptr, 1);
    if (overflow != 0u || attempted_rows > static_cast<unsigned long long>(max_rows)) {
        *row_count_out = 0;
        *overflow_out = 1u;
    } else {
        const size_t emitted = static_cast<size_t>(attempted_rows);
        if (emitted != 0)
            download(rows_out, d_rows.ptr, emitted);
        if (emitted > 1) {
            std::sort(rows_out, rows_out + emitted, [](const auto& left, const auto& right) {
                if (left.primitive_id != right.primitive_id) {
                    return left.primitive_id < right.primitive_id;
                }
                return left.ray_id < right.ray_id;
            });
        }
        *row_count_out = emitted;
        *overflow_out = 0u;
    }
    *hit_event_count_out = static_cast<uint64_t>(hit_events);
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_impl_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        CUdeviceptr caller_ray_ids,
        CUdeviceptr caller_primitive_ids,
        bool caller_owned_output,
        CUdeviceptr caller_row_count,
        CUdeviceptr caller_hit_events,
        CUdeviceptr caller_overflow,
        bool caller_owned_status,
        RtdlNativeDeviceHitStreamColumns* columns_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!rays && ray_count != 0)
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    if (!columns_out)
        throw std::runtime_error("device hit-stream columns_out pointer must not be null");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    if (prepared->triangle_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("triangle_count exceeds uint32 primitive limit");
    if (max_rows > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("max_rows exceeds uint32 hit-stream capacity");

    *columns_out = {};
    columns_out->capacity = static_cast<uint64_t>(max_rows);
    if (caller_owned_output && max_rows != 0 && (!caller_ray_ids || !caller_primitive_ids))
        throw std::runtime_error("caller-owned hit-stream output columns require nonzero device pointers");
    if (caller_owned_status && (!caller_row_count || !caller_hit_events || !caller_overflow))
        throw std::runtime_error("caller-owned hit-stream status requires nonzero device pointers");
    if (caller_owned_status) {
        unsigned long long zero64 = 0ull;
        uint32_t zero32 = 0u;
        upload(caller_row_count, &zero64, 1);
        upload(caller_hit_events, &zero64, 1);
        upload(caller_overflow, &zero32, 1);
        columns_out->row_count_device_ptr = static_cast<uint64_t>(caller_row_count);
        columns_out->hit_event_count_device_ptr = static_cast<uint64_t>(caller_hit_events);
        columns_out->overflow_device_ptr = static_cast<uint64_t>(caller_overflow);
    }
    if (ray_count == 0 || prepared->triangle_count == 0)
        return;

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = pack_ray_3d_as_gpu_ray(rays[i]);

    ensure_ray_triangle_hit_stream_device_columns_3d_pipeline();

    std::unique_ptr<NativeRayTriangleHitStreamDeviceColumnsOwner> owner;
    CUdeviceptr ray_ids_output = caller_ray_ids;
    CUdeviceptr primitive_ids_output = caller_primitive_ids;
    if (!caller_owned_output) {
        owner = std::make_unique<NativeRayTriangleHitStreamDeviceColumnsOwner>();
        if (max_rows != 0) {
            CU_CHECK(cuMemAlloc(&owner->ray_ids, sizeof(unsigned long long) * max_rows));
            CU_CHECK(cuMemAlloc(&owner->primitive_ids, sizeof(unsigned long long) * max_rows));
            ray_ids_output = owner->ray_ids;
            primitive_ids_output = owner->primitive_ids;
        }
    }

    const size_t flag_word_count = std::max<size_t>(1, (prepared->triangle_count + 31u) / 32u);
    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    std::unique_ptr<DevPtr> d_row_count_storage;
    std::unique_ptr<DevPtr> d_hit_events_storage;
    std::unique_ptr<DevPtr> d_overflow_storage;
    DevPtr d_flags(sizeof(uint32_t) * flag_word_count);
    CUdeviceptr row_count_ptr = caller_row_count;
    CUdeviceptr hit_events_ptr = caller_hit_events;
    CUdeviceptr overflow_ptr = caller_overflow;
    if (!caller_owned_status) {
        d_row_count_storage = std::make_unique<DevPtr>(sizeof(unsigned long long));
        d_hit_events_storage = std::make_unique<DevPtr>(sizeof(unsigned long long));
        d_overflow_storage = std::make_unique<DevPtr>(sizeof(uint32_t));
        row_count_ptr = d_row_count_storage->ptr;
        hit_events_ptr = d_hit_events_storage->ptr;
        overflow_ptr = d_overflow_storage->ptr;
    }

    upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
    unsigned long long zero64 = 0ull;
    uint32_t zero32 = 0u;
    upload(row_count_ptr, &zero64, 1);
    upload(hit_events_ptr, &zero64, 1);
    upload(overflow_ptr, &zero32, 1);
    CU_CHECK(cuMemsetD32(d_flags.ptr, 0u, flag_word_count));

    RayTriangleHitStreamDeviceColumns3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.ray_ids = reinterpret_cast<unsigned long long*>(ray_ids_output);
    lp.primitive_ids = reinterpret_cast<unsigned long long*>(primitive_ids_output);
    lp.row_count = reinterpret_cast<unsigned long long*>(row_count_ptr);
    lp.hit_event_count = reinterpret_cast<unsigned long long*>(hit_events_ptr);
    lp.overflow = reinterpret_cast<uint32_t*>(overflow_ptr);
    lp.primitive_flags = reinterpret_cast<uint32_t*>(d_flags.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);
    lp.triangle_count = static_cast<uint32_t>(prepared->triangle_count);
    lp.max_rows = static_cast<uint32_t>(max_rows);
    lp.deduplicate_primitives = deduplicate_primitives != 0u ? 1u : 0u;

    DevPtr d_params(sizeof(RayTriangleHitStreamDeviceColumns3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_raytriangle_hitstream_device_columns3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayTriangleHitStreamDeviceColumns3DLaunchParams),
                             &g_raytriangle_hitstream_device_columns3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    const auto traversal_end = std::chrono::steady_clock::now();

    unsigned long long attempted_rows = 0ull;
    unsigned long long hit_events = 0ull;
    uint32_t overflow = 0u;
    download(&attempted_rows, row_count_ptr, 1);
    download(&hit_events, hit_events_ptr, 1);
    download(&overflow, overflow_ptr, 1);

    columns_out->hit_event_count = static_cast<uint64_t>(hit_events);
    columns_out->traversal_seconds = std::chrono::duration<double>(traversal_end - traversal_start).count();
    CUdevice current_device = 0;
    CU_CHECK(cuCtxGetDevice(&current_device));
    columns_out->device_ordinal = static_cast<int32_t>(current_device);
    if (caller_owned_status) {
        columns_out->row_count_device_ptr = static_cast<uint64_t>(row_count_ptr);
        columns_out->hit_event_count_device_ptr = static_cast<uint64_t>(hit_events_ptr);
        columns_out->overflow_device_ptr = static_cast<uint64_t>(overflow_ptr);
    }

    if (overflow != 0u || attempted_rows > static_cast<unsigned long long>(max_rows)) {
        columns_out->row_count = 0u;
        columns_out->overflow = 1u;
        return;
    }

    columns_out->ray_ids_device_ptr = static_cast<uint64_t>(ray_ids_output);
    columns_out->primitive_ids_device_ptr = static_cast<uint64_t>(primitive_ids_output);
    columns_out->row_count = static_cast<uint64_t>(attempted_rows);
    columns_out->overflow = 0u;
    if (!caller_owned_output && owner)
        columns_out->owner_handle = owner.release();
}

static void run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        RtdlNativeDeviceHitStreamColumns* columns_out)
{
    run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_impl_optix(
        prepared,
        rays,
        ray_count,
        deduplicate_primitives,
        max_rows,
        0,
        0,
        false,
        0,
        0,
        0,
        false,
        columns_out);
}

static void run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        uint64_t ray_ids_device_ptr,
        uint64_t primitive_ids_device_ptr,
        RtdlNativeDeviceHitStreamColumns* columns_out)
{
    run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_impl_optix(
        prepared,
        rays,
        ray_count,
        deduplicate_primitives,
        max_rows,
        static_cast<CUdeviceptr>(ray_ids_device_ptr),
        static_cast<CUdeviceptr>(primitive_ids_device_ptr),
        true,
        0,
        0,
        0,
        false,
        columns_out);
}

static void run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        uint64_t ray_ids_device_ptr,
        uint64_t primitive_ids_device_ptr,
        uint64_t row_count_device_ptr,
        uint64_t hit_event_count_device_ptr,
        uint64_t overflow_device_ptr,
        RtdlNativeDeviceHitStreamColumns* columns_out)
{
    run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_impl_optix(
        prepared,
        rays,
        ray_count,
        deduplicate_primitives,
        max_rows,
        static_cast<CUdeviceptr>(ray_ids_device_ptr),
        static_cast<CUdeviceptr>(primitive_ids_device_ptr),
        true,
        static_cast<CUdeviceptr>(row_count_device_ptr),
        static_cast<CUdeviceptr>(hit_event_count_device_ptr),
        static_cast<CUdeviceptr>(overflow_device_ptr),
        true,
        columns_out);
}

static void run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_into_device_columns_with_status_on_stream_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        uint32_t deduplicate_primitives,
        size_t max_rows,
        uint64_t ray_ids_device_ptr,
        uint64_t primitive_ids_device_ptr,
        uint64_t row_count_device_ptr,
        uint64_t hit_event_count_device_ptr,
        uint64_t overflow_device_ptr,
        uint64_t cuda_stream_ptr,
        RtdlNativeDeviceHitStreamColumns* columns_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!rays && ray_count != 0)
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    if (!columns_out)
        throw std::runtime_error("device hit-stream columns_out pointer must not be null");
    if (cuda_stream_ptr == 0)
        throw std::runtime_error("same-stream hit-stream launch requires a nonzero CUDA stream pointer");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    if (prepared->triangle_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("triangle_count exceeds uint32 primitive limit");
    if (max_rows > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("max_rows exceeds uint32 hit-stream capacity");
    if (max_rows != 0 && (!ray_ids_device_ptr || !primitive_ids_device_ptr))
        throw std::runtime_error("same-stream hit-stream output columns require nonzero device pointers");
    if (!row_count_device_ptr || !hit_event_count_device_ptr || !overflow_device_ptr)
        throw std::runtime_error("same-stream hit-stream status requires nonzero device pointers");

    CUstream stream = reinterpret_cast<CUstream>(static_cast<uintptr_t>(cuda_stream_ptr));
    CUdevice current_device = 0;
    CU_CHECK(cuCtxGetDevice(&current_device));

    *columns_out = {};
    columns_out->capacity = static_cast<uint64_t>(max_rows);
    columns_out->ray_ids_device_ptr = ray_ids_device_ptr;
    columns_out->primitive_ids_device_ptr = primitive_ids_device_ptr;
    columns_out->device_ordinal = static_cast<int32_t>(current_device);
    columns_out->row_count_device_ptr = row_count_device_ptr;
    columns_out->hit_event_count_device_ptr = hit_event_count_device_ptr;
    columns_out->overflow_device_ptr = overflow_device_ptr;
    columns_out->traversal_seconds = 0.0;

    CUdeviceptr row_count_ptr = static_cast<CUdeviceptr>(row_count_device_ptr);
    CUdeviceptr hit_events_ptr = static_cast<CUdeviceptr>(hit_event_count_device_ptr);
    CUdeviceptr overflow_ptr = static_cast<CUdeviceptr>(overflow_device_ptr);
    CU_CHECK(cuMemsetD8Async(row_count_ptr, 0, sizeof(unsigned long long), stream));
    CU_CHECK(cuMemsetD8Async(hit_events_ptr, 0, sizeof(unsigned long long), stream));
    CU_CHECK(cuMemsetD32Async(overflow_ptr, 0u, 1, stream));

    if (ray_count == 0 || prepared->triangle_count == 0)
        return;

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = pack_ray_3d_as_gpu_ray(rays[i]);

    ensure_ray_triangle_hit_stream_device_columns_3d_pipeline();

    auto owner = std::make_unique<NativeRayTriangleHitStreamAsyncLaunchOwner>();
    owner->producer_stream = stream;
    const size_t flag_word_count = std::max<size_t>(1, (prepared->triangle_count + 31u) / 32u);
    CU_CHECK(cuMemAlloc(&owner->rays, sizeof(GpuRay3DHost) * ray_count));
    CU_CHECK(cuMemAlloc(&owner->primitive_flags, sizeof(uint32_t) * flag_word_count));
    CU_CHECK(cuMemAlloc(&owner->params, sizeof(RayTriangleHitStreamDeviceColumns3DLaunchParams)));
    CU_CHECK(cuMemAllocHost(&owner->host_rays, sizeof(GpuRay3DHost) * ray_count));
    CU_CHECK(cuMemAllocHost(&owner->host_params, sizeof(RayTriangleHitStreamDeviceColumns3DLaunchParams)));

    std::memcpy(owner->host_rays, gpu_rays.data(), sizeof(GpuRay3DHost) * gpu_rays.size());
    upload_async(owner->rays, static_cast<const GpuRay3DHost*>(owner->host_rays), gpu_rays.size(), stream);
    CU_CHECK(cuMemsetD32Async(owner->primitive_flags, 0u, flag_word_count, stream));

    RayTriangleHitStreamDeviceColumns3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(owner->rays);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.ray_ids = reinterpret_cast<unsigned long long*>(static_cast<CUdeviceptr>(ray_ids_device_ptr));
    lp.primitive_ids = reinterpret_cast<unsigned long long*>(static_cast<CUdeviceptr>(primitive_ids_device_ptr));
    lp.row_count = reinterpret_cast<unsigned long long*>(row_count_ptr);
    lp.hit_event_count = reinterpret_cast<unsigned long long*>(hit_events_ptr);
    lp.overflow = reinterpret_cast<uint32_t*>(overflow_ptr);
    lp.primitive_flags = reinterpret_cast<uint32_t*>(owner->primitive_flags);
    lp.ray_count = static_cast<uint32_t>(ray_count);
    lp.triangle_count = static_cast<uint32_t>(prepared->triangle_count);
    lp.max_rows = static_cast<uint32_t>(max_rows);
    lp.deduplicate_primitives = deduplicate_primitives != 0u ? 1u : 0u;

    std::memcpy(owner->host_params, &lp, sizeof(RayTriangleHitStreamDeviceColumns3DLaunchParams));
    upload_async(
        owner->params,
        static_cast<const RayTriangleHitStreamDeviceColumns3DLaunchParams*>(owner->host_params),
        1,
        stream);
    OPTIX_CHECK(optixLaunch(g_raytriangle_hitstream_device_columns3d.pipe->pipeline, stream,
                             owner->params, sizeof(RayTriangleHitStreamDeviceColumns3DLaunchParams),
                             &g_raytriangle_hitstream_device_columns3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    columns_out->owner_handle = owner.release();
}

static void release_ray_triangle_hit_stream_device_columns_optix(void* owner_handle)
{
    delete reinterpret_cast<NativeRayTriangleHitStreamDeviceColumnsOwner*>(owner_handle);
}

static void release_ray_triangle_hit_stream_async_launch_optix(void* owner_handle)
{
    delete reinterpret_cast<NativeRayTriangleHitStreamAsyncLaunchOwner*>(owner_handle);
}

static void run_prepared_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedPrimitiveGroupedI64Payload3D* payload,
        const RtdlRay3D* rays,
        size_t ray_count,
        uint32_t reduction,
        uint64_t* group_counts_out,
        uint64_t* group_sums_out,
        uint64_t* group_mins_out,
        uint64_t* group_maxs_out,
        uint64_t* hit_event_count_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!payload)
        throw std::runtime_error("prepared primitive grouped payload handle must not be null");
    if (!rays && ray_count != 0)
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    if (payload->primitive_count != prepared->triangle_count)
        throw std::runtime_error("prepared primitive payload length must match prepared triangle count");
    if (!group_counts_out || !group_sums_out || !group_mins_out || !group_maxs_out)
        throw std::runtime_error("group output arrays must not be null");
    if (!hit_event_count_out)
        throw std::runtime_error("hit_event_count_out must not be null");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    if (prepared->triangle_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("triangle_count exceeds uint32 primitive limit");
    if (payload->group_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("group_count exceeds uint32 limit");
    if (reduction != kDeviceColumnGroupedOpCount &&
            reduction != kDeviceColumnGroupedOpSum &&
            reduction != kDeviceColumnGroupedOpMin &&
            reduction != kDeviceColumnGroupedOpMax &&
            reduction != kDeviceColumnGroupedOpSumCount) {
        throw std::runtime_error("unsupported primitive grouped i64 reduction operation");
    }

    for (size_t group_index = 0; group_index < payload->group_count; ++group_index) {
        group_counts_out[group_index] = 0u;
        group_sums_out[group_index] = 0u;
        group_mins_out[group_index] = std::numeric_limits<uint64_t>::max();
        group_maxs_out[group_index] = 0u;
    }
    *hit_event_count_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_count == 0 || prepared->triangle_count == 0 || payload->group_count == 0)
        return;

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = pack_ray_3d_as_gpu_ray(rays[i]);

    ensure_ray_primitive_grouped_i64_reduction_3d_pipeline();

    const size_t flag_word_count = (prepared->triangle_count + 31u) / 32u;
    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    DevPtr d_flags(sizeof(uint32_t) * flag_word_count);
    DevPtr d_counts(sizeof(unsigned long long) * payload->group_count);
    DevPtr d_sums(sizeof(unsigned long long) * payload->group_count);
    DevPtr d_mins(sizeof(unsigned long long) * payload->group_count);
    DevPtr d_maxs(sizeof(unsigned long long) * payload->group_count);
    DevPtr d_hit_events(sizeof(unsigned long long));

    upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
    CU_CHECK(cuMemsetD32(d_flags.ptr, 0u, flag_word_count));
    CU_CHECK(cuMemsetD32(d_counts.ptr, 0u, payload->group_count * 2u));
    CU_CHECK(cuMemsetD32(d_sums.ptr, 0u, payload->group_count * 2u));
    CU_CHECK(cuMemsetD32(d_maxs.ptr, 0u, payload->group_count * 2u));
    unsigned long long zero = 0ull;
    upload(d_hit_events.ptr, &zero, 1);
    std::vector<unsigned long long> min_init(payload->group_count, std::numeric_limits<unsigned long long>::max());
    upload(d_mins.ptr, min_init.data(), min_init.size());

    RayPrimitiveGroupedI64Reduction3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.primitive_group_ids = reinterpret_cast<const uint32_t*>(payload->d_groups.ptr);
    lp.primitive_values = reinterpret_cast<const unsigned long long*>(payload->d_values.ptr);
    lp.primitive_flags = reinterpret_cast<uint32_t*>(d_flags.ptr);
    lp.group_counts = reinterpret_cast<unsigned long long*>(d_counts.ptr);
    lp.group_sums = reinterpret_cast<unsigned long long*>(d_sums.ptr);
    lp.group_mins = reinterpret_cast<unsigned long long*>(d_mins.ptr);
    lp.group_maxs = reinterpret_cast<unsigned long long*>(d_maxs.ptr);
    lp.hit_event_count = reinterpret_cast<unsigned long long*>(d_hit_events.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);
    lp.triangle_count = static_cast<uint32_t>(prepared->triangle_count);
    lp.group_count = static_cast<uint32_t>(payload->group_count);
    lp.reduction = reduction;

    DevPtr d_params(sizeof(RayPrimitiveGroupedI64Reduction3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayprimitive_grouped_i64_reduction3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayPrimitiveGroupedI64Reduction3DLaunchParams),
                             &g_rayprimitive_grouped_i64_reduction3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<unsigned long long> counts(payload->group_count, 0ull);
    std::vector<unsigned long long> sums(payload->group_count, 0ull);
    std::vector<unsigned long long> mins(payload->group_count, std::numeric_limits<unsigned long long>::max());
    std::vector<unsigned long long> maxs(payload->group_count, 0ull);
    unsigned long long hit_events = 0ull;
    download(counts.data(), d_counts.ptr, payload->group_count);
    download(sums.data(), d_sums.ptr, payload->group_count);
    download(mins.data(), d_mins.ptr, payload->group_count);
    download(maxs.data(), d_maxs.ptr, payload->group_count);
    download(&hit_events, d_hit_events.ptr, 1);
    for (size_t group_index = 0; group_index < payload->group_count; ++group_index) {
        group_counts_out[group_index] = static_cast<uint64_t>(counts[group_index]);
        group_sums_out[group_index] = static_cast<uint64_t>(sums[group_index]);
        group_mins_out[group_index] = static_cast<uint64_t>(mins[group_index]);
        group_maxs_out[group_index] = static_cast<uint64_t>(maxs[group_index]);
    }
    *hit_event_count_out = static_cast<uint64_t>(hit_events);
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedPrimitiveGroupedI64Payload3D* payload,
        PreparedRayBatch3D* ray_batch,
        uint32_t reduction,
        uint64_t* group_counts_out,
        uint64_t* group_sums_out,
        uint64_t* group_mins_out,
        uint64_t* group_maxs_out,
        uint64_t* hit_event_count_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!payload)
        throw std::runtime_error("prepared primitive grouped payload handle must not be null");
    if (!ray_batch)
        throw std::runtime_error("prepared ray batch handle must not be null");
    if (payload->primitive_count != prepared->triangle_count)
        throw std::runtime_error("prepared primitive payload length must match prepared triangle count");
    if (!group_counts_out || !group_sums_out || !group_mins_out || !group_maxs_out)
        throw std::runtime_error("group output arrays must not be null");
    if (!hit_event_count_out)
        throw std::runtime_error("hit_event_count_out must not be null");
    if (ray_batch->ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    if (prepared->triangle_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("triangle_count exceeds uint32 primitive limit");
    if (payload->group_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("group_count exceeds uint32 limit");
    if (reduction != kDeviceColumnGroupedOpCount &&
            reduction != kDeviceColumnGroupedOpSum &&
            reduction != kDeviceColumnGroupedOpMin &&
            reduction != kDeviceColumnGroupedOpMax &&
            reduction != kDeviceColumnGroupedOpSumCount) {
        throw std::runtime_error("unsupported primitive grouped i64 reduction operation");
    }

    for (size_t group_index = 0; group_index < payload->group_count; ++group_index) {
        group_counts_out[group_index] = 0u;
        group_sums_out[group_index] = 0u;
        group_mins_out[group_index] = std::numeric_limits<uint64_t>::max();
        group_maxs_out[group_index] = 0u;
    }
    *hit_event_count_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_batch->ray_count == 0 || prepared->triangle_count == 0 || payload->group_count == 0)
        return;

    ensure_ray_primitive_grouped_i64_reduction_3d_pipeline();

    const size_t flag_word_count = (prepared->triangle_count + 31u) / 32u;
    DevPtr d_flags(sizeof(uint32_t) * flag_word_count);
    DevPtr d_counts(sizeof(unsigned long long) * payload->group_count);
    DevPtr d_sums(sizeof(unsigned long long) * payload->group_count);
    DevPtr d_mins(sizeof(unsigned long long) * payload->group_count);
    DevPtr d_maxs(sizeof(unsigned long long) * payload->group_count);
    DevPtr d_hit_events(sizeof(unsigned long long));

    CU_CHECK(cuMemsetD32(d_flags.ptr, 0u, flag_word_count));
    CU_CHECK(cuMemsetD32(d_counts.ptr, 0u, payload->group_count * 2u));
    CU_CHECK(cuMemsetD32(d_sums.ptr, 0u, payload->group_count * 2u));
    CU_CHECK(cuMemsetD32(d_maxs.ptr, 0u, payload->group_count * 2u));
    unsigned long long zero = 0ull;
    upload(d_hit_events.ptr, &zero, 1);
    std::vector<unsigned long long> min_init(payload->group_count, std::numeric_limits<unsigned long long>::max());
    upload(d_mins.ptr, min_init.data(), min_init.size());

    RayPrimitiveGroupedI64Reduction3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(ray_batch->d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.primitive_group_ids = reinterpret_cast<const uint32_t*>(payload->d_groups.ptr);
    lp.primitive_values = reinterpret_cast<const unsigned long long*>(payload->d_values.ptr);
    lp.primitive_flags = reinterpret_cast<uint32_t*>(d_flags.ptr);
    lp.group_counts = reinterpret_cast<unsigned long long*>(d_counts.ptr);
    lp.group_sums = reinterpret_cast<unsigned long long*>(d_sums.ptr);
    lp.group_mins = reinterpret_cast<unsigned long long*>(d_mins.ptr);
    lp.group_maxs = reinterpret_cast<unsigned long long*>(d_maxs.ptr);
    lp.hit_event_count = reinterpret_cast<unsigned long long*>(d_hit_events.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_batch->ray_count);
    lp.triangle_count = static_cast<uint32_t>(prepared->triangle_count);
    lp.group_count = static_cast<uint32_t>(payload->group_count);
    lp.reduction = reduction;

    DevPtr d_params(sizeof(RayPrimitiveGroupedI64Reduction3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayprimitive_grouped_i64_reduction3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayPrimitiveGroupedI64Reduction3DLaunchParams),
                             &g_rayprimitive_grouped_i64_reduction3d.pipe->sbt,
                             static_cast<unsigned>(ray_batch->ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));

    std::vector<unsigned long long> counts(payload->group_count, 0ull);
    std::vector<unsigned long long> sums(payload->group_count, 0ull);
    std::vector<unsigned long long> mins(payload->group_count, std::numeric_limits<unsigned long long>::max());
    std::vector<unsigned long long> maxs(payload->group_count, 0ull);
    unsigned long long hit_events = 0ull;
    download(counts.data(), d_counts.ptr, payload->group_count);
    download(sums.data(), d_sums.ptr, payload->group_count);
    download(mins.data(), d_mins.ptr, payload->group_count);
    download(maxs.data(), d_maxs.ptr, payload->group_count);
    download(&hit_events, d_hit_events.ptr, 1);
    for (size_t group_index = 0; group_index < payload->group_count; ++group_index) {
        group_counts_out[group_index] = static_cast<uint64_t>(counts[group_index]);
        group_sums_out[group_index] = static_cast<uint64_t>(sums[group_index]);
        group_mins_out[group_index] = static_cast<uint64_t>(mins[group_index]);
        group_maxs_out[group_index] = static_cast<uint64_t>(maxs[group_index]);
    }
    *hit_event_count_out = static_cast<uint64_t>(hit_events);
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_ray_hit_count_sum_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        uint64_t* hit_count_sum_out,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!rays && ray_count != 0)
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    if (!hit_count_sum_out)
        throw std::runtime_error("hit_count_sum_out must not be null");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    *hit_count_sum_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_count == 0 || prepared->triangle_count == 0)
        return;

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = pack_ray_3d_as_gpu_ray(rays[i]);

    ensure_ray_hitcount_sum_3d_pipeline();

    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    DevPtr d_sum(sizeof(unsigned long long));
    upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());
    unsigned long long zero = 0ull;
    upload(d_sum.ptr, &zero, 1);

    RayHitCount3DSumLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.hit_count_sum = reinterpret_cast<unsigned long long*>(d_sum.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayHitCount3DSumLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayhit3d_sum.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayHitCount3DSumLaunchParams),
                             &g_rayhit3d_sum.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    unsigned long long sum = 0ull;
    download(&sum, d_sum.ptr, 1);
    *hit_count_sum_out = static_cast<uint64_t>(sum);
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void launch_prepared_static_triangle_scene_3d_ray_closest_hit_records_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        CUdeviceptr d_output,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!rays && ray_count != 0)
        throw std::runtime_error("ray pointer must not be null when ray_count is nonzero");
    if (!d_output && ray_count != 0)
        throw std::runtime_error("closest-hit output device buffer must not be null when ray_count is nonzero");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");

    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_count == 0 || prepared->triangle_count == 0)
        return;

    std::vector<GpuRay3DHost> gpu_rays(ray_count);
    for (size_t i = 0; i < ray_count; ++i)
        gpu_rays[i] = pack_ray_3d_as_raw_gpu_ray(rays[i]);

    ensure_ray_closest_hit_3d_pipeline();

    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    upload(d_rays.ptr, gpu_rays.data(), gpu_rays.size());

    RayClosestHit3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.output = reinterpret_cast<GpuRayClosestHitRecord*>(d_output);
    lp.ray_count = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayClosestHit3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayclosest3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayClosestHit3DLaunchParams),
                             &g_rayclosest3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void launch_prepared_static_triangle_scene_3d_device_ray_closest_hit_records_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedRayBatch3D* ray_batch,
        CUdeviceptr d_output,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!ray_batch)
        throw std::runtime_error("prepared ray batch handle must not be null");
    if (!d_output && ray_batch->ray_count != 0)
        throw std::runtime_error("closest-hit output device buffer must not be null when ray_count is nonzero");

    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_batch->ray_count == 0 || prepared->triangle_count == 0)
        return;

    ensure_ray_closest_hit_3d_pipeline();

    RayClosestHit3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(ray_batch->d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.output = reinterpret_cast<GpuRayClosestHitRecord*>(d_output);
    lp.ray_count = static_cast<uint32_t>(ray_batch->ray_count);

    DevPtr d_params(sizeof(RayClosestHit3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayclosest3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayClosestHit3DLaunchParams),
                             &g_rayclosest3d.pipe->sbt,
                             static_cast<unsigned>(ray_batch->ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static std::vector<GpuRayClosestHitRecord> run_prepared_static_triangle_scene_3d_ray_closest_hit_records_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        double* traversal_seconds_out)
{
    if (ray_count == 0 || !prepared || prepared->triangle_count == 0) {
        if (traversal_seconds_out)
            *traversal_seconds_out = 0.0;
        if (!prepared)
            throw std::runtime_error("prepared scene handle must not be null");
        return {};
    }

    DevPtr d_output(sizeof(GpuRayClosestHitRecord) * ray_count);
    launch_prepared_static_triangle_scene_3d_ray_closest_hit_records_optix(
        prepared,
        rays,
        ray_count,
        d_output.ptr,
        traversal_seconds_out);
    std::vector<GpuRayClosestHitRecord> gpu_rows(ray_count);
    download(gpu_rows.data(), d_output.ptr, ray_count);
    return gpu_rows;
}

static std::vector<GpuRayClosestHitRecord> run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_records_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedRayBatch3D* ray_batch,
        double* traversal_seconds_out)
{
    if (!ray_batch)
        throw std::runtime_error("prepared ray batch handle must not be null");
    if (ray_batch->ray_count == 0 || !prepared || prepared->triangle_count == 0) {
        if (traversal_seconds_out)
            *traversal_seconds_out = 0.0;
        if (!prepared)
            throw std::runtime_error("prepared scene handle must not be null");
        return {};
    }

    launch_prepared_static_triangle_scene_3d_device_ray_closest_hit_records_optix(
        prepared,
        ray_batch,
        ray_batch->d_closest_hit_output.ptr,
        traversal_seconds_out);
    std::vector<GpuRayClosestHitRecord> gpu_rows(ray_batch->ray_count);
    download(gpu_rows.data(), ray_batch->d_closest_hit_output.ptr, ray_batch->ray_count);
    return gpu_rows;
}

static void run_prepared_static_triangle_scene_3d_ray_closest_hit_rows_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        RtdlRayClosestHitRow** rows_out,
        size_t* row_count_out,
        double* traversal_seconds_out)
{
    if (!rows_out || !row_count_out)
        throw std::runtime_error("closest-hit row outputs must not be null");

    *rows_out = nullptr;
    *row_count_out = 0;
    auto gpu_rows = run_prepared_static_triangle_scene_3d_ray_closest_hit_records_optix(
        prepared,
        rays,
        ray_count,
        traversal_seconds_out);

    size_t hit_count = 0;
    for (const auto& row : gpu_rows) {
        if (row.has_hit != 0u)
            ++hit_count;
    }
    auto* out = static_cast<RtdlRayClosestHitRow*>(
        std::malloc(sizeof(RtdlRayClosestHitRow) * hit_count));
    if (!out && hit_count > 0) throw std::bad_alloc();
    size_t out_index = 0;
    for (const auto& row : gpu_rows) {
        if (row.has_hit == 0u)
            continue;
        out[out_index].ray_id = row.ray_id;
        out[out_index].triangle_id = row.triangle_id;
        out[out_index].t = static_cast<double>(row.t);
        ++out_index;
    }
    *rows_out = out;
    *row_count_out = hit_count;
}

static void run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_rows_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedRayBatch3D* ray_batch,
        RtdlRayClosestHitRow** rows_out,
        size_t* row_count_out,
        double* traversal_seconds_out)
{
    if (!rows_out || !row_count_out)
        throw std::runtime_error("closest-hit row outputs must not be null");

    *rows_out = nullptr;
    *row_count_out = 0;
    auto gpu_rows = run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_records_optix(
        prepared,
        ray_batch,
        traversal_seconds_out);

    size_t hit_count = 0;
    for (const auto& row : gpu_rows) {
        if (row.has_hit != 0u)
            ++hit_count;
    }
    auto* out = static_cast<RtdlRayClosestHitRow*>(
        std::malloc(sizeof(RtdlRayClosestHitRow) * hit_count));
    if (!out && hit_count > 0) throw std::bad_alloc();
    size_t out_index = 0;
    for (const auto& row : gpu_rows) {
        if (row.has_hit == 0u)
            continue;
        out[out_index].ray_id = row.ray_id;
        out[out_index].triangle_id = row.triangle_id;
        out[out_index].t = static_cast<double>(row.t);
        ++out_index;
    }
    *rows_out = out;
    *row_count_out = hit_count;
}

static void run_prepared_static_triangle_scene_3d_ray_closest_hit_grouped_argmin_optix(
        PreparedStaticTriangleScene3D* prepared,
        const RtdlRay3D* rays,
        size_t ray_count,
        const uint32_t* ray_group_ids,
        size_t ray_group_id_count,
        const double* candidate_values,
        const uint32_t* candidate_indices,
        size_t candidate_count,
        size_t group_count,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* traversal_seconds_out)
{
    if (!ray_group_ids && ray_group_id_count != 0)
        throw std::runtime_error("ray group-id map must not be null when nonempty");
    if (!candidate_values && candidate_count != 0)
        throw std::runtime_error("candidate values must not be null when candidate_count is nonzero");
    if (!candidate_indices && candidate_count != 0)
        throw std::runtime_error("candidate indices must not be null when candidate_count is nonzero");
    if (group_count != 0 && (!group_has_value_out || !group_index_out || !group_value_out))
        throw std::runtime_error("grouped argmin outputs must not be null when group_count is nonzero");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    if (ray_group_id_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_group_id_count exceeds uint32 launch limit");
    if (candidate_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("candidate_count exceeds uint32 launch limit");
    if (group_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("group_count exceeds uint32 launch limit");

    for (size_t i = 0; i < group_count; ++i) {
        group_has_value_out[i] = 0u;
        group_index_out[i] = std::numeric_limits<uint32_t>::max();
        group_value_out[i] = 0.0;
    }
    if (group_count == 0 || ray_count == 0 || candidate_count == 0 || !prepared || prepared->triangle_count == 0) {
        if (!prepared)
            throw std::runtime_error("prepared scene handle must not be null");
        if (traversal_seconds_out)
            *traversal_seconds_out = 0.0;
        return;
    }

    for (size_t i = 0; i < ray_group_id_count; ++i) {
        if (ray_group_ids[i] >= group_count)
            throw std::runtime_error("ray group id is outside the grouped argmin output range");
    }
    for (size_t i = 0; i < ray_count; ++i) {
        if (rays[i].id >= ray_group_id_count)
            throw std::runtime_error("ray id is outside the ray group-id map");
    }
    bool ray_groups_are_unique = true;
    std::vector<uint8_t> seen_groups(group_count, 0u);
    for (size_t i = 0; i < ray_count; ++i) {
        const uint32_t group_id = ray_group_ids[rays[i].id];
        if (seen_groups[group_id] != 0u) {
            ray_groups_are_unique = false;
            break;
        }
        seen_groups[group_id] = 1u;
    }

    DevPtr d_output(sizeof(GpuRayClosestHitRecord) * ray_count);
    launch_prepared_static_triangle_scene_3d_ray_closest_hit_records_optix(
        prepared,
        rays,
        ray_count,
        d_output.ptr,
        traversal_seconds_out);

    DevPtr d_ray_group_ids(sizeof(uint32_t) * ray_group_id_count);
    DevPtr d_candidate_values(sizeof(double) * candidate_count);
    DevPtr d_candidate_indices(sizeof(uint32_t) * candidate_count);
    DevPtr d_group_has_value(sizeof(uint8_t) * group_count);
    DevPtr d_group_index(sizeof(uint32_t) * group_count);
    DevPtr d_group_value(sizeof(double) * group_count);
    upload(d_ray_group_ids.ptr, ray_group_ids, ray_group_id_count);
    upload(d_candidate_values.ptr, candidate_values, candidate_count);
    upload(d_candidate_indices.ptr, candidate_indices, candidate_count);

    const unsigned block = 256;
    const uint32_t ray_count_u = static_cast<uint32_t>(ray_count);
    const uint32_t ray_group_id_count_u = static_cast<uint32_t>(ray_group_id_count);
    const uint32_t candidate_count_u = static_cast<uint32_t>(candidate_count);
    const uint32_t group_count_u = static_cast<uint32_t>(group_count);
    const unsigned ray_grid = (ray_count_u + block - 1u) / block;
    const unsigned group_grid = (group_count_u + block - 1u) / block;

    ensure_ray_closest_hit_grouped_argmin_kernels();
    CUdeviceptr d_has_ptr = d_group_has_value.ptr;
    CUdeviceptr d_index_ptr = d_group_index.ptr;
    CUdeviceptr d_value_ptr = d_group_value.ptr;
    CUdeviceptr d_rows_ptr = d_output.ptr;
    CUdeviceptr d_ray_group_ids_ptr = d_ray_group_ids.ptr;
    CUdeviceptr d_candidate_values_ptr = d_candidate_values.ptr;
    CUdeviceptr d_candidate_indices_ptr = d_candidate_indices.ptr;

    if (ray_groups_are_unique) {
        CU_CHECK(cuMemsetD8(d_group_has_value.ptr, 0, group_count * sizeof(uint8_t)));
        CU_CHECK(cuMemsetD8(d_group_index.ptr, 0xff, group_count * sizeof(uint32_t)));
        CU_CHECK(cuMemsetD8(d_group_value.ptr, 0, group_count * sizeof(double)));
        void* scatter_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            &d_candidate_indices_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_has_ptr,
            &d_index_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.scatter_unique_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, scatter_args, nullptr));
    } else {
        DevPtr d_group_best_keys(sizeof(unsigned long long) * group_count);
        CUdeviceptr d_keys_ptr = d_group_best_keys.ptr;
        void* init_args[] = {
            &d_keys_ptr,
            &d_has_ptr,
            &d_index_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.init_fn,
            group_grid, 1, 1,
            block, 1, 1,
            0, nullptr, init_args, nullptr));

        void* min_key_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_keys_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.min_key_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, min_key_args, nullptr));

        void* min_index_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            &d_candidate_indices_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_keys_ptr,
            &d_index_ptr,
            &d_has_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.min_index_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, min_index_args, nullptr));
    }
    CU_CHECK(cuStreamSynchronize(nullptr));

    download(group_has_value_out, d_group_has_value.ptr, group_count);
    download(group_index_out, d_group_index.ptr, group_count);
    download(group_value_out, d_group_value.ptr, group_count);
}

static void run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_grouped_argmin_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedRayBatch3D* ray_batch,
        const uint32_t* ray_group_ids,
        size_t ray_group_id_count,
        const double* candidate_values,
        const uint32_t* candidate_indices,
        size_t candidate_count,
        size_t group_count,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* traversal_seconds_out)
{
    if (!ray_batch)
        throw std::runtime_error("prepared ray batch handle must not be null");
    if (!ray_group_ids && ray_group_id_count != 0)
        throw std::runtime_error("ray group-id map must not be null when nonempty");
    if (!candidate_values && candidate_count != 0)
        throw std::runtime_error("candidate values must not be null when candidate_count is nonzero");
    if (!candidate_indices && candidate_count != 0)
        throw std::runtime_error("candidate indices must not be null when candidate_count is nonzero");
    if (group_count != 0 && (!group_has_value_out || !group_index_out || !group_value_out))
        throw std::runtime_error("grouped argmin outputs must not be null when group_count is nonzero");
    if (ray_group_id_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_group_id_count exceeds uint32 launch limit");
    if (candidate_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("candidate_count exceeds uint32 launch limit");
    if (group_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("group_count exceeds uint32 launch limit");

    const size_t ray_count = ray_batch->ray_count;
    for (size_t i = 0; i < group_count; ++i) {
        group_has_value_out[i] = 0u;
        group_index_out[i] = std::numeric_limits<uint32_t>::max();
        group_value_out[i] = 0.0;
    }
    if (group_count == 0 || ray_count == 0 || candidate_count == 0 || !prepared || prepared->triangle_count == 0) {
        if (!prepared)
            throw std::runtime_error("prepared scene handle must not be null");
        if (traversal_seconds_out)
            *traversal_seconds_out = 0.0;
        return;
    }

    for (size_t i = 0; i < ray_group_id_count; ++i) {
        if (ray_group_ids[i] >= group_count)
            throw std::runtime_error("ray group id is outside the grouped argmin output range");
    }
    for (size_t i = 0; i < ray_count; ++i) {
        if (ray_batch->ray_ids[i] >= ray_group_id_count)
            throw std::runtime_error("ray id is outside the ray group-id map");
    }
    bool ray_groups_are_unique = true;
    std::vector<uint8_t> seen_groups(group_count, 0u);
    for (size_t i = 0; i < ray_count; ++i) {
        const uint32_t group_id = ray_group_ids[ray_batch->ray_ids[i]];
        if (seen_groups[group_id] != 0u) {
            ray_groups_are_unique = false;
            break;
        }
        seen_groups[group_id] = 1u;
    }

    launch_prepared_static_triangle_scene_3d_device_ray_closest_hit_records_optix(
        prepared,
        ray_batch,
        ray_batch->d_closest_hit_output.ptr,
        traversal_seconds_out);

    DevPtr d_ray_group_ids(sizeof(uint32_t) * ray_group_id_count);
    DevPtr d_candidate_values(sizeof(double) * candidate_count);
    DevPtr d_candidate_indices(sizeof(uint32_t) * candidate_count);
    DevPtr d_group_has_value(sizeof(uint8_t) * group_count);
    DevPtr d_group_index(sizeof(uint32_t) * group_count);
    DevPtr d_group_value(sizeof(double) * group_count);
    upload(d_ray_group_ids.ptr, ray_group_ids, ray_group_id_count);
    upload(d_candidate_values.ptr, candidate_values, candidate_count);
    upload(d_candidate_indices.ptr, candidate_indices, candidate_count);

    const unsigned block = 256;
    const uint32_t ray_count_u = static_cast<uint32_t>(ray_count);
    const uint32_t ray_group_id_count_u = static_cast<uint32_t>(ray_group_id_count);
    const uint32_t candidate_count_u = static_cast<uint32_t>(candidate_count);
    const uint32_t group_count_u = static_cast<uint32_t>(group_count);
    const unsigned ray_grid = (ray_count_u + block - 1u) / block;
    const unsigned group_grid = (group_count_u + block - 1u) / block;

    ensure_ray_closest_hit_grouped_argmin_kernels();
    CUdeviceptr d_has_ptr = d_group_has_value.ptr;
    CUdeviceptr d_index_ptr = d_group_index.ptr;
    CUdeviceptr d_value_ptr = d_group_value.ptr;
    CUdeviceptr d_rows_ptr = ray_batch->d_closest_hit_output.ptr;
    CUdeviceptr d_ray_group_ids_ptr = d_ray_group_ids.ptr;
    CUdeviceptr d_candidate_values_ptr = d_candidate_values.ptr;
    CUdeviceptr d_candidate_indices_ptr = d_candidate_indices.ptr;

    if (ray_groups_are_unique) {
        CU_CHECK(cuMemsetD8(d_group_has_value.ptr, 0, group_count * sizeof(uint8_t)));
        CU_CHECK(cuMemsetD8(d_group_index.ptr, 0xff, group_count * sizeof(uint32_t)));
        CU_CHECK(cuMemsetD8(d_group_value.ptr, 0, group_count * sizeof(double)));
        void* scatter_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            &d_candidate_indices_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_has_ptr,
            &d_index_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.scatter_unique_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, scatter_args, nullptr));
    } else {
        DevPtr d_group_best_keys(sizeof(unsigned long long) * group_count);
        CUdeviceptr d_keys_ptr = d_group_best_keys.ptr;
        void* init_args[] = {
            &d_keys_ptr,
            &d_has_ptr,
            &d_index_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.init_fn,
            group_grid, 1, 1,
            block, 1, 1,
            0, nullptr, init_args, nullptr));

        void* min_key_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_keys_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.min_key_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, min_key_args, nullptr));

        void* min_index_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            &d_candidate_indices_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_keys_ptr,
            &d_index_ptr,
            &d_has_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.min_index_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, min_index_args, nullptr));
    }
    CU_CHECK(cuStreamSynchronize(nullptr));

    download(group_has_value_out, d_group_has_value.ptr, group_count);
    download(group_index_out, d_group_index.ptr, group_count);
    download(group_value_out, d_group_value.ptr, group_count);
}

static void clear_prepared_grouped_argmin_device_outputs(PreparedClosestHitGroupedArgmin3D* grouped_inputs)
{
    const size_t group_count = grouped_inputs ? grouped_inputs->group_count : 0;
    if (group_count == 0)
        return;
    CU_CHECK(cuMemsetD8(grouped_inputs->d_group_has_value.ptr, 0, group_count * sizeof(uint8_t)));
    CU_CHECK(cuMemsetD8(grouped_inputs->d_group_index.ptr, 0xff, group_count * sizeof(uint32_t)));
    CU_CHECK(cuMemsetD8(grouped_inputs->d_group_value.ptr, 0, group_count * sizeof(double)));
}

static void run_prepared_grouped_candidate_argmin_device_optix(
        PreparedGroupedCandidateArgmin* grouped_inputs,
        double* finalize_seconds_out)
{
    if (!grouped_inputs)
        throw std::runtime_error("prepared grouped candidate argmin handle must not be null");

    const size_t candidate_count = grouped_inputs->candidate_count;
    const size_t group_count = grouped_inputs->group_count;
    if (finalize_seconds_out)
        *finalize_seconds_out = 0.0;
    if (group_count == 0)
        return;

    const auto finalize_start = std::chrono::steady_clock::now();
    const unsigned block = 256;
    const uint32_t candidate_count_u = static_cast<uint32_t>(candidate_count);
    const uint32_t group_count_u = static_cast<uint32_t>(group_count);
    const unsigned candidate_grid = (candidate_count_u + block - 1u) / block;
    const unsigned group_grid = (group_count_u + block - 1u) / block;

    ensure_ray_closest_hit_grouped_argmin_kernels();
    CUdeviceptr d_keys_ptr = grouped_inputs->d_group_best_keys.ptr;
    CUdeviceptr d_has_ptr = grouped_inputs->d_group_has_value.ptr;
    CUdeviceptr d_index_ptr = grouped_inputs->d_group_index.ptr;
    CUdeviceptr d_value_ptr = grouped_inputs->d_group_value.ptr;
    CUdeviceptr d_candidate_group_ids_ptr = grouped_inputs->d_candidate_group_ids.ptr;
    CUdeviceptr d_candidate_values_ptr = grouped_inputs->d_candidate_values.ptr;
    CUdeviceptr d_candidate_indices_ptr = grouped_inputs->d_candidate_indices.ptr;

    void* init_args[] = {
        &d_keys_ptr,
        &d_has_ptr,
        &d_index_ptr,
        &d_value_ptr,
        const_cast<uint32_t*>(&group_count_u),
    };
    CU_CHECK(cuLaunchKernel(
        g_rayclosest3d_grouped_argmin.init_fn,
        group_grid, 1, 1,
        block, 1, 1,
        0, nullptr, init_args, nullptr));

    if (candidate_count_u != 0u) {
        void* min_key_args[] = {
            &d_candidate_group_ids_ptr,
            &d_candidate_values_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_keys_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.candidate_min_key_fn,
            candidate_grid, 1, 1,
            block, 1, 1,
            0, nullptr, min_key_args, nullptr));

        void* min_index_args[] = {
            &d_candidate_group_ids_ptr,
            &d_candidate_values_ptr,
            &d_candidate_indices_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_keys_ptr,
            &d_index_ptr,
            &d_has_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.candidate_min_index_fn,
            candidate_grid, 1, 1,
            block, 1, 1,
            0, nullptr, min_index_args, nullptr));
    }
    CU_CHECK(cuStreamSynchronize(nullptr));
    const auto finalize_end = std::chrono::steady_clock::now();
    if (finalize_seconds_out)
        *finalize_seconds_out = std::chrono::duration<double>(finalize_end - finalize_start).count();
}

static void run_prepared_grouped_candidate_argmin_optix(
        PreparedGroupedCandidateArgmin* grouped_inputs,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* finalize_seconds_out)
{
    if (!grouped_inputs)
        throw std::runtime_error("prepared grouped candidate argmin handle must not be null");
    const size_t group_count = grouped_inputs->group_count;
    if (group_count != 0 && (!group_has_value_out || !group_index_out || !group_value_out))
        throw std::runtime_error("grouped candidate argmin outputs must not be null when group_count is nonzero");

    run_prepared_grouped_candidate_argmin_device_optix(grouped_inputs, finalize_seconds_out);
    download(group_has_value_out, grouped_inputs->d_group_has_value.ptr, group_count);
    download(group_index_out, grouped_inputs->d_group_index.ptr, group_count);
    download(group_value_out, grouped_inputs->d_group_value.ptr, group_count);
}

static void run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedRayBatch3D* ray_batch,
        PreparedClosestHitGroupedArgmin3D* grouped_inputs,
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!ray_batch)
        throw std::runtime_error("prepared ray batch handle must not be null");
    if (!grouped_inputs)
        throw std::runtime_error("prepared grouped argmin inputs handle must not be null");

    const size_t ray_count = ray_batch->ray_count;
    const size_t ray_group_id_count = grouped_inputs->ray_group_id_count;
    const size_t candidate_count = grouped_inputs->candidate_count;
    const size_t group_count = grouped_inputs->group_count;

    if (group_count == 0) {
        if (traversal_seconds_out)
            *traversal_seconds_out = 0.0;
        return;
    }
    if (ray_count == 0 || candidate_count == 0 || prepared->triangle_count == 0) {
        clear_prepared_grouped_argmin_device_outputs(grouped_inputs);
        if (traversal_seconds_out)
            *traversal_seconds_out = 0.0;
        return;
    }

    for (size_t i = 0; i < ray_count; ++i) {
        if (ray_batch->ray_ids[i] >= ray_group_id_count)
            throw std::runtime_error("ray id is outside the prepared ray group-id map");
    }
    bool ray_groups_are_unique = true;
    std::vector<uint8_t> seen_groups(group_count, 0u);
    for (size_t i = 0; i < ray_count; ++i) {
        const uint32_t group_id = grouped_inputs->ray_group_ids[ray_batch->ray_ids[i]];
        if (seen_groups[group_id] != 0u) {
            ray_groups_are_unique = false;
            break;
        }
        seen_groups[group_id] = 1u;
    }

    launch_prepared_static_triangle_scene_3d_device_ray_closest_hit_records_optix(
        prepared,
        ray_batch,
        ray_batch->d_closest_hit_output.ptr,
        traversal_seconds_out);

    const unsigned block = 256;
    const uint32_t ray_count_u = static_cast<uint32_t>(ray_count);
    const uint32_t ray_group_id_count_u = static_cast<uint32_t>(ray_group_id_count);
    const uint32_t candidate_count_u = static_cast<uint32_t>(candidate_count);
    const uint32_t group_count_u = static_cast<uint32_t>(group_count);
    const unsigned ray_grid = (ray_count_u + block - 1u) / block;
    const unsigned group_grid = (group_count_u + block - 1u) / block;

    ensure_ray_closest_hit_grouped_argmin_kernels();
    CUdeviceptr d_has_ptr = grouped_inputs->d_group_has_value.ptr;
    CUdeviceptr d_index_ptr = grouped_inputs->d_group_index.ptr;
    CUdeviceptr d_value_ptr = grouped_inputs->d_group_value.ptr;
    CUdeviceptr d_rows_ptr = ray_batch->d_closest_hit_output.ptr;
    CUdeviceptr d_ray_group_ids_ptr = grouped_inputs->d_ray_group_ids.ptr;
    CUdeviceptr d_candidate_values_ptr = grouped_inputs->d_candidate_values.ptr;
    CUdeviceptr d_candidate_indices_ptr = grouped_inputs->d_candidate_indices.ptr;

    if (ray_groups_are_unique) {
        clear_prepared_grouped_argmin_device_outputs(grouped_inputs);
        void* scatter_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            &d_candidate_indices_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_has_ptr,
            &d_index_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.scatter_unique_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, scatter_args, nullptr));
    } else {
        CUdeviceptr d_keys_ptr = grouped_inputs->d_group_best_keys.ptr;
        void* init_args[] = {
            &d_keys_ptr,
            &d_has_ptr,
            &d_index_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.init_fn,
            group_grid, 1, 1,
            block, 1, 1,
            0, nullptr, init_args, nullptr));

        void* min_key_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_keys_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.min_key_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, min_key_args, nullptr));

        void* min_index_args[] = {
            &d_rows_ptr,
            const_cast<uint32_t*>(&ray_count_u),
            &d_ray_group_ids_ptr,
            const_cast<uint32_t*>(&ray_group_id_count_u),
            &d_candidate_values_ptr,
            &d_candidate_indices_ptr,
            const_cast<uint32_t*>(&candidate_count_u),
            &d_keys_ptr,
            &d_index_ptr,
            &d_has_ptr,
            &d_value_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.min_index_fn,
            ray_grid, 1, 1,
            block, 1, 1,
            0, nullptr, min_index_args, nullptr));
    }
    CU_CHECK(cuStreamSynchronize(nullptr));
}

static void run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_optix(
        PreparedStaticTriangleScene3D* prepared,
        PreparedRayBatch3D* ray_batch,
        PreparedClosestHitGroupedArgmin3D* grouped_inputs,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* traversal_seconds_out)
{
    if (!grouped_inputs)
        throw std::runtime_error("prepared grouped argmin inputs handle must not be null");
    const size_t group_count = grouped_inputs->group_count;
    if (group_count != 0 && (!group_has_value_out || !group_index_out || !group_value_out))
        throw std::runtime_error("grouped argmin outputs must not be null when group_count is nonzero");

    run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device_optix(
        prepared,
        ray_batch,
        grouped_inputs,
        traversal_seconds_out);
    download(group_has_value_out, grouped_inputs->d_group_has_value.ptr, group_count);
    download(group_index_out, grouped_inputs->d_group_index.ptr, group_count);
    download(group_value_out, grouped_inputs->d_group_value.ptr, group_count);
}

static void run_prepared_static_triangle_scene_3d_two_ray_batches_closest_hit_prepared_grouped_argmin_optix(
        PreparedStaticTriangleScene3D* scene_a,
        PreparedRayBatch3D* ray_batch_a,
        PreparedClosestHitGroupedArgmin3D* grouped_inputs_a,
        PreparedStaticTriangleScene3D* scene_b,
        PreparedRayBatch3D* ray_batch_b,
        PreparedClosestHitGroupedArgmin3D* grouped_inputs_b,
        uint8_t* group_has_value_out,
        uint32_t* group_index_out,
        double* group_value_out,
        double* traversal_a_seconds_out,
        double* traversal_b_seconds_out)
{
    if (!grouped_inputs_a || !grouped_inputs_b)
        throw std::runtime_error("prepared grouped argmin inputs handles must not be null");
    const size_t group_count = grouped_inputs_a->group_count;
    if (grouped_inputs_b->group_count != group_count)
        throw std::runtime_error("two-source grouped argmin inputs must have the same group_count");
    if (group_count != 0 && (!group_has_value_out || !group_index_out || !group_value_out))
        throw std::runtime_error("grouped argmin outputs must not be null when group_count is nonzero");

    run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device_optix(
        scene_a,
        ray_batch_a,
        grouped_inputs_a,
        traversal_a_seconds_out);
    run_prepared_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device_optix(
        scene_b,
        ray_batch_b,
        grouped_inputs_b,
        traversal_b_seconds_out);

    if (group_count != 0) {
        const unsigned block = 256;
        const uint32_t group_count_u = static_cast<uint32_t>(group_count);
        const unsigned group_grid = (group_count_u + block - 1u) / block;
        ensure_ray_closest_hit_grouped_argmin_kernels();
        CUdeviceptr has_a_ptr = grouped_inputs_a->d_group_has_value.ptr;
        CUdeviceptr index_a_ptr = grouped_inputs_a->d_group_index.ptr;
        CUdeviceptr value_a_ptr = grouped_inputs_a->d_group_value.ptr;
        CUdeviceptr has_b_ptr = grouped_inputs_b->d_group_has_value.ptr;
        CUdeviceptr index_b_ptr = grouped_inputs_b->d_group_index.ptr;
        CUdeviceptr value_b_ptr = grouped_inputs_b->d_group_value.ptr;
        void* merge_args[] = {
            &has_a_ptr,
            &index_a_ptr,
            &value_a_ptr,
            &has_b_ptr,
            &index_b_ptr,
            &value_b_ptr,
            &has_a_ptr,
            &index_a_ptr,
            &value_a_ptr,
            const_cast<uint32_t*>(&group_count_u),
        };
        CU_CHECK(cuLaunchKernel(
            g_rayclosest3d_grouped_argmin.merge_two_fn,
            group_grid, 1, 1,
            block, 1, 1,
            0, nullptr, merge_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
    }

    download(group_has_value_out, grouped_inputs_a->d_group_has_value.ptr, group_count);
    download(group_index_out, grouped_inputs_a->d_group_index.ptr, group_count);
    download(group_value_out, grouped_inputs_a->d_group_value.ptr, group_count);
}

static void run_prepared_static_triangle_scene_3d_ray_any_hit_weighted_sum_device_optix(
        PreparedStaticTriangleScene3D* prepared,
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
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!ray_weights && ray_count != 0)
        throw std::runtime_error("partner device ray_weights pointer must not be null when ray_count is nonzero");
    if (!weighted_hit_sum_out)
        throw std::runtime_error("weighted_hit_sum_out must not be null");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    *weighted_hit_sum_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_count == 0 || prepared->triangle_count == 0)
        return;

    ensure_ray_anyhit_weighted_sum_3d_pipeline();

    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    pack_ray3d_device_columns_to_buffer(
        ray_ids,
        ray_ox,
        ray_oy,
        ray_oz,
        ray_dx,
        ray_dy,
        ray_dz,
        ray_tmax,
        ray_count,
        d_rays.ptr);
    DevPtr d_sum(sizeof(unsigned long long));
    unsigned long long zero = 0ull;
    upload(d_sum.ptr, &zero, 1);

    RayAnyHitWeightedSum3DLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.ray_weights = reinterpret_cast<const unsigned long long*>(ray_weights);
    lp.weighted_hit_sum = reinterpret_cast<unsigned long long*>(d_sum.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayAnyHitWeightedSum3DLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayanyhit_weighted_sum3d.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayAnyHitWeightedSum3DLaunchParams),
                             &g_rayanyhit_weighted_sum3d.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    unsigned long long sum = 0ull;
    download(&sum, d_sum.ptr, 1);
    *weighted_hit_sum_out = static_cast<uint64_t>(sum);
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_prepared_static_triangle_scene_3d_ray_hit_count_sum_device_optix(
        PreparedStaticTriangleScene3D* prepared,
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
        double* traversal_seconds_out)
{
    if (!prepared)
        throw std::runtime_error("prepared scene handle must not be null");
    if (!hit_count_sum_out)
        throw std::runtime_error("hit_count_sum_out must not be null");
    if (ray_count > static_cast<size_t>(std::numeric_limits<uint32_t>::max()))
        throw std::runtime_error("ray_count exceeds uint32 launch limit");
    *hit_count_sum_out = 0u;
    if (traversal_seconds_out)
        *traversal_seconds_out = 0.0;
    if (ray_count == 0 || prepared->triangle_count == 0)
        return;

    ensure_ray_hitcount_sum_3d_pipeline();

    DevPtr d_rays(sizeof(GpuRay3DHost) * ray_count);
    pack_ray3d_device_columns_to_buffer(
        ray_ids,
        ray_ox,
        ray_oy,
        ray_oz,
        ray_dx,
        ray_dy,
        ray_dz,
        ray_tmax,
        ray_count,
        d_rays.ptr);
    DevPtr d_sum(sizeof(unsigned long long));
    unsigned long long zero = 0ull;
    upload(d_sum.ptr, &zero, 1);

    RayHitCount3DSumLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.rays = reinterpret_cast<const GpuRay3DHost*>(d_rays.ptr);
    lp.triangles = reinterpret_cast<const GpuTriangle3DHost*>(prepared->d_triangles.ptr);
    lp.hit_count_sum = reinterpret_cast<unsigned long long*>(d_sum.ptr);
    lp.ray_count = static_cast<uint32_t>(ray_count);

    DevPtr d_params(sizeof(RayHitCount3DSumLaunchParams));
    upload(d_params.ptr, &lp, 1);

    const auto traversal_start = std::chrono::steady_clock::now();
    CUstream stream = 0;
    OPTIX_CHECK(optixLaunch(g_rayhit3d_sum.pipe->pipeline, stream,
                             d_params.ptr, sizeof(RayHitCount3DSumLaunchParams),
                             &g_rayhit3d_sum.pipe->sbt,
                             static_cast<unsigned>(ray_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    unsigned long long sum = 0ull;
    download(&sum, d_sum.ptr, 1);
    *hit_count_sum_out = static_cast<uint64_t>(sum);
    const auto traversal_end = std::chrono::steady_clock::now();
    if (traversal_seconds_out)
        *traversal_seconds_out = std::chrono::duration<double>(traversal_end - traversal_start).count();
}

static void run_ray_anyhit_3d_optix(
        const RtdlRay3D*      rays,      size_t ray_count,
        const RtdlTriangle3D* triangles, size_t triangle_count,
        RtdlRayAnyHitRow**  rows_out,  size_t* row_count_out)
{
    ensure_ray_anyhit_3d_pipeline();

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

struct FixedRadiusNeighbors3DRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint3DHost* query_points;
    const GpuPoint3DHost* search_points;
    GpuFrnRecord* output;
    uint32_t query_count;
    uint32_t k_max;
    float radius;
    float trace_tmax;
};

struct FixedRadiusCountThreshold3DRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint3DHost* query_points;
    const GpuPoint3DHost* search_points;
    uint32_t* query_ids_out;
    uint32_t* neighbor_counts_out;
    uint32_t* threshold_flags_out;
    uint32_t query_count;
    uint32_t threshold;
    float radius;
    float trace_tmax;
};

struct FixedRadiusAdjacency3DRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint3DHost* query_points;
    const GpuPoint3DHost* search_points;
    const int64_t* edge_offsets;
    int32_t* neighbor_indices_out;
    uint64_t neighbor_index_capacity;
    uint32_t query_count;
    float radius;
    float trace_tmax;
};

struct FixedRadiusGroupedUnion3DRtLaunchParams {
    OptixTraversableHandle traversable;
    const GpuPoint3DHost* query_points;
    const GpuPoint3DHost* search_points;
    const uint32_t* predicate_flags;
    int32_t* parent_out;
    int32_t* fallback_candidate_out;
    uint64_t* telemetry_out;
    uint32_t query_count;
    uint32_t query_index_offset;
    uint32_t item_count;
    uint32_t all_predicate;
    uint32_t same_root_culling;
    uint32_t direct_side_effect;
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
    reset_fixed_radius_3d_phase_timings(1u);
    (void)get_optix_context();
    std::call_once(g_frn3d.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusNeighbors3DKernelSrc, "frn3d_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_frn3d.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(&g_frn3d.fn, g_frn3d.module, "fixed_radius_neighbors_3d"));
    });

    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    constexpr size_t kFixedRadiusSlack = 8;

    auto t_start_prepare = std::chrono::steady_clock::now();
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
    auto t_end_prepare = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_prepare_s = seconds_between(t_start_prepare, t_end_prepare);

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    DevPtr d_search(sizeof(GpuPoint3DHost) * search_count);
    DevPtr d_output(sizeof(GpuFrnRecord) * output_capacity);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    upload(d_search.ptr, gpu_search.data(), search_count);
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

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
    auto t_start_count = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d.fn, grid, 1, 1, block, 1, 1, 0, nullptr, args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_count = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_count, t_end_count);

    auto t_start_download = std::chrono::steady_clock::now();
    std::vector<GpuFrnRecord> gpu_rows(output_capacity);
    download(gpu_rows.data(), d_output.ptr, output_capacity);
    auto t_end_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_download, t_end_download);

    auto t_start_refine = std::chrono::steady_clock::now();
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
    auto t_end_refine = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_exact_refine_s = seconds_between(t_start_refine, t_end_refine);
    g_optix_last_fixed_radius_3d_raw_candidate_count = output_capacity;
    g_optix_last_fixed_radius_3d_emitted_count = rows.size();
    *rows_out = out;
    *row_count_out = rows.size();
}

static void ensure_fixed_radius_neighbors_grid_cuda_3d_kernel()
{
    std::call_once(g_frn3d_grid.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusNeighbors3DGridKernelSrc, "frn3d_grid_kernel.cu");
        CU_CHECK(cuModuleLoadData(&g_frn3d_grid.module, ptx.c_str()));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid"));
        g_frn3d_grid_count.module = g_frn3d_grid.module;
        g_frn3d_grid_exact_count.module = g_frn3d_grid.module;
        g_frn3d_grid_exact_summary.module = g_frn3d_grid.module;
        g_frn3d_grid_exact_rows.module = g_frn3d_grid.module;
        g_frn3d_grid_ranked_count.module = g_frn3d_grid.module;
        g_frn3d_grid_ranked_rows.module = g_frn3d_grid.module;
        g_frn3d_grid_ranked_summary.module = g_frn3d_grid.module;
        g_frn3d_grid_ranked_summary_f32.module = g_frn3d_grid.module;
        g_frn3d_grid_ranked_summary_aggregate.module = g_frn3d_grid.module;
        g_frn3d_grid_ranked_summary_aggregate_f32_direct.module = g_frn3d_grid.module;
        g_frn3d_grid_ranked_summary_aggregate_f32_blocks.module = g_frn3d_grid.module;
        g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch.module = g_frn3d_grid.module;
        g_frn3d_ranked_aggregate_partials_reduce.module = g_frn3d_grid.module;
        g_frn3d_grid_compact.module = g_frn3d_grid.module;
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_count.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_count"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_exact_count.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_exact_count"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_exact_summary.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_exact_summary"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_exact_rows.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_exact_rows"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_ranked_count.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_ranked_count"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_ranked_rows.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_ranked_rows"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_ranked_summary.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_ranked_summary"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_ranked_summary_f32.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_ranked_summary_f32"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_ranked_summary_aggregate.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_ranked_summary_aggregate"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_ranked_summary_aggregate_f32_direct.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_direct"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_ranked_summary_aggregate_f32_blocks.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_ranked_summary_aggregate_f32_blocks_batch"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_ranked_aggregate_partials_reduce.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_ranked_aggregate_partials_reduce"));
        CU_CHECK(cuModuleGetFunction(&g_frn3d_grid_compact.fn, g_frn3d_grid.module, "fixed_radius_neighbors_3d_grid_compact"));
    });
}

struct PreparedFixedRadiusNeighborsGrid3D {
    std::vector<RtdlPoint3D> search_points;
    std::vector<uint32_t> cell_offsets;
    std::unique_ptr<DevPtr> d_search;
    std::unique_ptr<DevPtr> d_search_exact;
    std::unique_ptr<DevPtr> d_offsets;
    std::unique_ptr<DevPtr> d_ranked_aggregate;
    size_t occupied_cell_count = 0;
    uint32_t grid_x = 0;
    uint32_t grid_y = 0;
    uint32_t grid_z = 0;
    float min_x = 0.0f;
    float min_y = 0.0f;
    float min_z = 0.0f;
    float inv_cell_size = 0.0f;
    double min_x_exact = 0.0;
    double min_y_exact = 0.0;
    double min_z_exact = 0.0;
    double inv_cell_size_exact = 0.0;
    double max_radius = 0.0;

    PreparedFixedRadiusNeighborsGrid3D(
            const RtdlPoint3D* source,
            size_t source_count,
            double radius_bound)
        : search_points(source_count),
          max_radius(radius_bound)
    {
        if (radius_bound <= 0.0) {
            throw std::runtime_error("fixed_radius_neighbors_3d prepared max_radius must be positive");
        }
        if (source_count == 0) {
            return;
        }
        std::copy(source, source + source_count, search_points.begin());
        ensure_fixed_radius_neighbors_grid_cuda_3d_kernel();

        double min_x_d = source[0].x;
        double min_y_d = source[0].y;
        double min_z_d = source[0].z;
        double max_x_d = source[0].x;
        double max_y_d = source[0].y;
        double max_z_d = source[0].z;
        for (size_t i = 1; i < source_count; ++i) {
            min_x_d = std::min(min_x_d, source[i].x);
            min_y_d = std::min(min_y_d, source[i].y);
            min_z_d = std::min(min_z_d, source[i].z);
            max_x_d = std::max(max_x_d, source[i].x);
            max_y_d = std::max(max_y_d, source[i].y);
            max_z_d = std::max(max_z_d, source[i].z);
        }

        const double cell_size = radius_bound;
        const auto grid_dim_for = [&](double lo, double hi) -> size_t {
            const double span = std::max(0.0, hi - lo);
            return static_cast<size_t>(std::floor(span / cell_size)) + 1u;
        };
        const size_t grid_x_size = grid_dim_for(min_x_d, max_x_d);
        const size_t grid_y_size = grid_dim_for(min_y_d, max_y_d);
        const size_t grid_z_size = grid_dim_for(min_z_d, max_z_d);
        constexpr size_t kMaxDenseGridCells = 16u * 1024u * 1024u;
        if (grid_x_size == 0 || grid_y_size == 0 || grid_z_size == 0 ||
                grid_x_size > static_cast<size_t>(UINT32_MAX) ||
                grid_y_size > static_cast<size_t>(UINT32_MAX) ||
                grid_z_size > static_cast<size_t>(UINT32_MAX) ||
                grid_x_size > ((std::numeric_limits<size_t>::max)() / grid_y_size) ||
                grid_x_size * grid_y_size > ((std::numeric_limits<size_t>::max)() / grid_z_size)) {
            throw std::runtime_error("fixed_radius_neighbors_3d prepared grid dimensions exceed supported bounds");
        }
        const size_t cell_count = grid_x_size * grid_y_size * grid_z_size;
        if (cell_count == 0 || cell_count > kMaxDenseGridCells) {
            throw std::runtime_error("fixed_radius_neighbors_3d prepared dense grid exceeds supported cell budget");
        }

        grid_x = static_cast<uint32_t>(grid_x_size);
        grid_y = static_cast<uint32_t>(grid_y_size);
        grid_z = static_cast<uint32_t>(grid_z_size);
        min_x = static_cast<float>(min_x_d);
        min_y = static_cast<float>(min_y_d);
        min_z = static_cast<float>(min_z_d);
        const double inv_cell_size_d = 1.0 / cell_size;
        inv_cell_size = static_cast<float>(inv_cell_size_d);
        min_x_exact = min_x_d;
        min_y_exact = min_y_d;
        min_z_exact = min_z_d;
        inv_cell_size_exact = inv_cell_size_d;

        const auto cell_for = [&](const RtdlPoint3D& point) -> uint32_t {
            const auto coord = [&](double value, double lo, uint32_t dim) -> uint32_t {
                long long raw = static_cast<long long>(std::floor((value - lo) * inv_cell_size_d));
                if (raw < 0) raw = 0;
                const long long max_raw = static_cast<long long>(dim) - 1;
                if (raw > max_raw) raw = max_raw;
                return static_cast<uint32_t>(raw);
            };
            const uint32_t ix = coord(point.x, min_x_d, grid_x);
            const uint32_t iy = coord(point.y, min_y_d, grid_y);
            const uint32_t iz = coord(point.z, min_z_d, grid_z);
            return (iz * grid_y + iy) * grid_x + ix;
        };

        std::vector<uint32_t> counts(cell_count, 0u);
        std::vector<uint32_t> search_cell(source_count);
        for (size_t i = 0; i < source_count; ++i) {
            const uint32_t cell = cell_for(source[i]);
            search_cell[i] = cell;
            counts[cell] += 1u;
        }
        occupied_cell_count = static_cast<size_t>(std::count_if(
            counts.begin(),
            counts.end(),
            [](uint32_t count) { return count != 0u; }));

        cell_offsets.assign(cell_count + 1u, 0u);
        for (size_t cell = 0; cell < cell_count; ++cell) {
            cell_offsets[cell + 1u] = cell_offsets[cell] + counts[cell];
        }

        std::vector<uint32_t> cursor = cell_offsets;
        std::vector<GpuPoint3DHost> sorted_search(source_count);
        std::vector<RtdlPoint3D> sorted_search_exact(source_count);
        for (size_t i = 0; i < source_count; ++i) {
            const uint32_t cell = search_cell[i];
            const uint32_t dest = cursor[cell]++;
            sorted_search[dest] = {
                static_cast<float>(source[i].x),
                static_cast<float>(source[i].y),
                static_cast<float>(source[i].z),
                source[i].id,
            };
            sorted_search_exact[dest] = source[i];
        }

        d_search = std::make_unique<DevPtr>(sizeof(GpuPoint3DHost) * sorted_search.size());
        d_search_exact = std::make_unique<DevPtr>(sizeof(RtdlPoint3D) * sorted_search_exact.size());
        d_offsets = std::make_unique<DevPtr>(sizeof(uint32_t) * cell_offsets.size());
        d_ranked_aggregate = std::make_unique<DevPtr>(sizeof(RtdlFixedRadiusRankedNeighborAggregate));
        upload(d_search->ptr, sorted_search.data(), sorted_search.size());
        upload(d_search_exact->ptr, sorted_search_exact.data(), sorted_search_exact.size());
        upload(d_offsets->ptr, cell_offsets.data(), cell_offsets.size());
    }
};

struct PreparedFixedRadiusQueryPoints3D {
    size_t query_count = 0;
    size_t aggregate_block_count = 0;
    std::unique_ptr<DevPtr> d_queries;
    std::unique_ptr<DevPtr> d_aggregate_partials;

    PreparedFixedRadiusQueryPoints3D(const RtdlPoint3D* query_points, size_t count)
        : query_count(count)
    {
        if (!query_points && count != 0) {
            throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
        }
        if (count == 0) {
            return;
        }
        std::vector<GpuPoint3DHost> gpu_queries(count);
        for (size_t i = 0; i < count; ++i) {
            gpu_queries[i] = {
                static_cast<float>(query_points[i].x),
                static_cast<float>(query_points[i].y),
                static_cast<float>(query_points[i].z),
                query_points[i].id,
            };
        }
        d_queries = std::make_unique<DevPtr>(sizeof(GpuPoint3DHost) * count);
        aggregate_block_count = (count + 255u) / 256u;
        d_aggregate_partials = std::make_unique<DevPtr>(
            sizeof(RtdlFixedRadiusRankedNeighborAggregate) * aggregate_block_count);
        upload(d_queries->ptr, gpu_queries.data(), count);
    }
};

static PreparedFixedRadiusNeighborsGrid3D* prepare_fixed_radius_neighbors_grid_3d_optix(
        const RtdlPoint3D* search_points,
        size_t search_count,
        double max_radius)
{
    return new PreparedFixedRadiusNeighborsGrid3D(search_points, search_count, max_radius);
}

static PreparedFixedRadiusQueryPoints3D* prepare_fixed_radius_query_points_grid_3d_optix(
        const RtdlPoint3D* query_points,
        size_t query_count)
{
    return new PreparedFixedRadiusQueryPoints3D(query_points, query_count);
}

static size_t count_prepared_fixed_radius_neighbors_grid_3d_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (k_max == 0)
        throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
    if (k_max > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d k_max exceeds uint32 limit");

    reset_fixed_radius_3d_phase_timings(5u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    if (query_count == 0 || prepared->search_points.empty()) return 0;

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries(sizeof(RtdlPoint3D) * query_count);
    DevPtr d_counts(sizeof(uint32_t) * query_count);
    upload(d_queries.ptr, query_points, query_count);
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    double min_x = prepared->min_x_exact;
    double min_y = prepared->min_y_exact;
    double min_z = prepared->min_z_exact;
    double inv_cell_size = prepared->inv_cell_size_exact;
    double radius_exact = radius;
    uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_max, prepared->search_points.size()));

    void* count_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search_exact->ptr,
        &prepared->d_offsets->ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_exact,
        &k_max_u32,
        &d_counts.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_count = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_exact_count.fn, grid, 1, 1, block, 1, 1, 0, nullptr, count_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_count = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_count, t_end_count);

    auto t_start_count_download = std::chrono::steady_clock::now();
    std::vector<uint32_t> gpu_counts(query_count);
    download(gpu_counts.data(), d_counts.ptr, query_count);
    size_t total_count = 0;
    for (uint32_t count : gpu_counts) {
        if (total_count > (std::numeric_limits<size_t>::max)() - static_cast<size_t>(count)) {
            throw std::runtime_error("fixed_radius_neighbors_3d count summary overflowed size_t");
        }
        total_count += static_cast<size_t>(count);
    }
    auto t_end_count_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_download_s = seconds_between(t_start_count_download, t_end_count_download);
    g_optix_last_fixed_radius_3d_raw_candidate_count = total_count;
    g_optix_last_fixed_radius_3d_emitted_count = total_count;
    return total_count;
}

static RtdlFixedRadiusNeighborSummary summarize_prepared_fixed_radius_neighbors_grid_3d_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (k_max == 0)
        throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
    if (k_max > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d k_max exceeds uint32 limit");

    reset_fixed_radius_3d_phase_timings(6u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    RtdlFixedRadiusNeighborSummary aggregate{0u, 0.0, 0.0, 0.0};
    if (query_count == 0 || prepared->search_points.empty()) return aggregate;

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries(sizeof(RtdlPoint3D) * query_count);
    DevPtr d_summaries(sizeof(RtdlFixedRadiusNeighborSummary) * query_count);
    upload(d_queries.ptr, query_points, query_count);
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    double min_x = prepared->min_x_exact;
    double min_y = prepared->min_y_exact;
    double min_z = prepared->min_z_exact;
    double inv_cell_size = prepared->inv_cell_size_exact;
    double radius_exact = radius;
    uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_max, prepared->search_points.size()));

    void* summary_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search_exact->ptr,
        &prepared->d_offsets->ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_exact,
        &k_max_u32,
        &d_summaries.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_summary = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_exact_summary.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_summary = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);

    auto t_start_download = std::chrono::steady_clock::now();
    std::vector<RtdlFixedRadiusNeighborSummary> summaries(query_count);
    download(summaries.data(), d_summaries.ptr, query_count);
    for (const auto& summary : summaries) {
        if (summary.count == 0) {
            continue;
        }
        if (aggregate.count > (std::numeric_limits<size_t>::max)() - summary.count) {
            throw std::runtime_error("fixed_radius_neighbors_3d summary count overflowed size_t");
        }
        if (aggregate.count == 0 || summary.min_distance < aggregate.min_distance) {
            aggregate.min_distance = summary.min_distance;
        }
        if (aggregate.count == 0 || summary.max_distance > aggregate.max_distance) {
            aggregate.max_distance = summary.max_distance;
        }
        aggregate.count += summary.count;
        aggregate.sum_distance += summary.sum_distance;
    }
    auto t_end_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_download_s = seconds_between(t_start_download, t_end_download);
    g_optix_last_fixed_radius_3d_raw_candidate_count = aggregate.count;
    g_optix_last_fixed_radius_3d_emitted_count = aggregate.count;
    return aggregate;
}

static void run_prepared_exact_fixed_radius_neighbors_grid_3d_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!rows_out || !row_count_out) throw std::runtime_error("output pointers must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (k_max == 0)
        throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
    if (k_max > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d k_max exceeds uint32 limit");

    *rows_out = nullptr;
    *row_count_out = 0;
    reset_fixed_radius_3d_phase_timings(7u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    if (query_count == 0 || prepared->search_points.empty()) return;

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries(sizeof(RtdlPoint3D) * query_count);
    DevPtr d_counts(sizeof(uint32_t) * query_count);
    upload(d_queries.ptr, query_points, query_count);
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    double min_x = prepared->min_x_exact;
    double min_y = prepared->min_y_exact;
    double min_z = prepared->min_z_exact;
    double inv_cell_size = prepared->inv_cell_size_exact;
    double radius_exact = radius;
    uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_max, prepared->search_points.size()));

    void* count_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search_exact->ptr,
        &prepared->d_offsets->ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_exact,
        &k_max_u32,
        &d_counts.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_count = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_exact_count.fn, grid, 1, 1, block, 1, 1, 0, nullptr, count_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_count = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_count, t_end_count);

    auto t_start_count_download = std::chrono::steady_clock::now();
    std::vector<uint32_t> exact_counts(query_count);
    download(exact_counts.data(), d_counts.ptr, query_count);
    std::vector<uint32_t> row_offsets(query_count + 1u, 0u);
    for (size_t i = 0; i < query_count; ++i) {
        row_offsets[i + 1u] = row_offsets[i] + exact_counts[i];
    }
    const size_t compact_capacity = static_cast<size_t>(row_offsets.back());
    auto t_end_count_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_download_s = seconds_between(t_start_count_download, t_end_count_download);
    g_optix_last_fixed_radius_3d_raw_candidate_count = compact_capacity;
    if (compact_capacity > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("fixed_radius_neighbors_3d prepared exact output exceeds uint32 limit");
    }
    if (compact_capacity == 0) {
        g_optix_last_fixed_radius_3d_emitted_count = 0;
        return;
    }

    DevPtr d_row_offsets(sizeof(uint32_t) * row_offsets.size());
    DevPtr d_output(sizeof(RtdlFixedRadiusNeighborRow) * compact_capacity);
    auto t_start_row_offset_upload = std::chrono::steady_clock::now();
    upload(d_row_offsets.ptr, row_offsets.data(), row_offsets.size());
    auto t_end_row_offset_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_offset_upload_s = seconds_between(t_start_row_offset_upload, t_end_row_offset_upload);

    void* row_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search_exact->ptr,
        &prepared->d_offsets->ptr,
        &d_row_offsets.ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_exact,
        &k_max_u32,
        &d_output.ptr,
    };

    auto t_start_rows = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_exact_rows.fn, grid, 1, 1, block, 1, 1, 0, nullptr, row_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_rows = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_compact_s = seconds_between(t_start_rows, t_end_rows);

    auto t_start_row_download = std::chrono::steady_clock::now();
    auto* out = static_cast<RtdlFixedRadiusNeighborRow*>(
        std::malloc(sizeof(RtdlFixedRadiusNeighborRow) * compact_capacity));
    if (!out) throw std::bad_alloc();
    download(out, d_output.ptr, compact_capacity);
    auto t_end_row_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_row_download, t_end_row_download);
    g_optix_last_fixed_radius_3d_exact_refine_s = 0.0;
    g_optix_last_fixed_radius_3d_emitted_count = compact_capacity;
    *rows_out = out;
    *row_count_out = compact_capacity;
}

static void run_prepared_ranked_fixed_radius_neighbors_grid_3d_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlKnnNeighborRow** rows_out, size_t* row_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!rows_out || !row_count_out) throw std::runtime_error("output pointers must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (k_max == 0)
        throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
    if (k_max > 64)
        throw std::runtime_error("prepared ranked fixed_radius_neighbors_3d currently supports k_max <= 64");

    *rows_out = nullptr;
    *row_count_out = 0;
    reset_fixed_radius_3d_phase_timings(8u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    if (query_count == 0 || prepared->search_points.empty()) return;

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries(sizeof(RtdlPoint3D) * query_count);
    DevPtr d_counts(sizeof(uint32_t) * query_count);
    upload(d_queries.ptr, query_points, query_count);
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    double min_x = prepared->min_x_exact;
    double min_y = prepared->min_y_exact;
    double min_z = prepared->min_z_exact;
    double inv_cell_size = prepared->inv_cell_size_exact;
    double radius_exact = radius;
    uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_max, prepared->search_points.size()));

    void* count_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search_exact->ptr,
        &prepared->d_offsets->ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_exact,
        &k_max_u32,
        &d_counts.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_count = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_count.fn, grid, 1, 1, block, 1, 1, 0, nullptr, count_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_count = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_count, t_end_count);

    auto t_start_count_download = std::chrono::steady_clock::now();
    std::vector<uint32_t> ranked_counts(query_count);
    download(ranked_counts.data(), d_counts.ptr, query_count);
    std::vector<uint32_t> row_offsets(query_count + 1u, 0u);
    uint64_t row_offset_cursor = 0u;
    for (size_t i = 0; i < query_count; ++i) {
        row_offset_cursor += ranked_counts[i];
        if (row_offset_cursor > static_cast<uint64_t>(UINT32_MAX)) {
            throw std::runtime_error("fixed_radius_neighbors_3d prepared ranked output exceeds uint32 limit");
        }
        row_offsets[i + 1u] = static_cast<uint32_t>(row_offset_cursor);
    }
    const size_t compact_capacity = static_cast<size_t>(row_offsets.back());
    auto t_end_count_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_download_s = seconds_between(t_start_count_download, t_end_count_download);
    g_optix_last_fixed_radius_3d_raw_candidate_count = compact_capacity;
    if (compact_capacity > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("fixed_radius_neighbors_3d prepared ranked output exceeds uint32 limit");
    }
    if (compact_capacity == 0) {
        g_optix_last_fixed_radius_3d_emitted_count = 0;
        return;
    }

    DevPtr d_row_offsets(sizeof(uint32_t) * row_offsets.size());
    DevPtr d_output(sizeof(RtdlKnnNeighborRow) * compact_capacity);
    auto t_start_row_offset_upload = std::chrono::steady_clock::now();
    upload(d_row_offsets.ptr, row_offsets.data(), row_offsets.size());
    auto t_end_row_offset_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_offset_upload_s = seconds_between(t_start_row_offset_upload, t_end_row_offset_upload);

    void* row_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search_exact->ptr,
        &prepared->d_offsets->ptr,
        &d_row_offsets.ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_exact,
        &k_max_u32,
        &d_output.ptr,
    };

    auto t_start_rows = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_rows.fn, grid, 1, 1, block, 1, 1, 0, nullptr, row_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_rows = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_compact_s = seconds_between(t_start_rows, t_end_rows);

    auto t_start_row_download = std::chrono::steady_clock::now();
    auto* out = static_cast<RtdlKnnNeighborRow*>(
        std::malloc(sizeof(RtdlKnnNeighborRow) * compact_capacity));
    if (!out) throw std::bad_alloc();
    download(out, d_output.ptr, compact_capacity);
    auto t_end_row_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_row_download, t_end_row_download);
    g_optix_last_fixed_radius_3d_exact_refine_s = 0.0;
    g_optix_last_fixed_radius_3d_emitted_count = compact_capacity;
    *rows_out = out;
    *row_count_out = compact_capacity;
}

static void run_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusRankedNeighborSummary** rows_out, size_t* row_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!rows_out || !row_count_out) throw std::runtime_error("output pointers must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (k_max == 0)
        throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
    if (k_max > 64)
        throw std::runtime_error("prepared ranked fixed_radius_neighbors_3d summary currently supports k_max <= 64");

    *rows_out = nullptr;
    *row_count_out = 0;
    reset_fixed_radius_3d_phase_timings(9u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    if (query_count == 0 || prepared->search_points.empty()) return;

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries(sizeof(RtdlPoint3D) * query_count);
    DevPtr d_summaries(sizeof(RtdlFixedRadiusRankedNeighborSummary) * query_count);
    upload(d_queries.ptr, query_points, query_count);
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    double min_x = prepared->min_x_exact;
    double min_y = prepared->min_y_exact;
    double min_z = prepared->min_z_exact;
    double inv_cell_size = prepared->inv_cell_size_exact;
    double radius_exact = radius;
    uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_max, prepared->search_points.size()));

    void* summary_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search_exact->ptr,
        &prepared->d_offsets->ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_exact,
        &k_max_u32,
        &d_summaries.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_summary = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_summary = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);

    auto t_start_download = std::chrono::steady_clock::now();
    auto* out = static_cast<RtdlFixedRadiusRankedNeighborSummary*>(
        std::malloc(sizeof(RtdlFixedRadiusRankedNeighborSummary) * query_count));
    if (!out) throw std::bad_alloc();
    download(out, d_summaries.ptr, query_count);
    auto t_end_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_download, t_end_download);

    size_t total_ranked_neighbors = 0u;
    for (size_t i = 0; i < query_count; ++i) {
        total_ranked_neighbors += out[i].neighbor_count;
    }
    g_optix_last_fixed_radius_3d_raw_candidate_count = total_ranked_neighbors;
    g_optix_last_fixed_radius_3d_emitted_count = query_count;
    g_optix_last_fixed_radius_3d_exact_refine_s = 0.0;
    *rows_out = out;
    *row_count_out = query_count;
}

static RtdlFixedRadiusRankedNeighborAggregate aggregate_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        bool use_float32_precision = false)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (k_max == 0)
        throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
    if (k_max > 64)
        throw std::runtime_error("prepared ranked fixed_radius_neighbors_3d aggregate currently supports k_max <= 64");

    const double mean_search_points_per_occupied_cell =
        prepared->occupied_cell_count == 0
            ? 0.0
            : static_cast<double>(prepared->search_points.size()) /
                static_cast<double>(prepared->occupied_cell_count);
    const bool use_direct_float32_aggregate =
        use_float32_precision && mean_search_points_per_occupied_cell <= 4.0;

    RtdlFixedRadiusRankedNeighborAggregate aggregate{0u, 0u, 0u, 0u, 0.0};
    reset_fixed_radius_3d_phase_timings(use_direct_float32_aggregate ? 12u : use_float32_precision ? 11u : 10u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    if (query_count == 0 || prepared->search_points.empty()) return aggregate;

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries((use_float32_precision ? sizeof(GpuPoint3DHost) : sizeof(RtdlPoint3D)) * query_count);
    std::vector<GpuPoint3DHost> gpu_queries;
    if (use_float32_precision) {
        gpu_queries.resize(query_count);
        for (size_t i = 0; i < query_count; ++i) {
            gpu_queries[i] = {
                static_cast<float>(query_points[i].x),
                static_cast<float>(query_points[i].y),
                static_cast<float>(query_points[i].z),
                query_points[i].id,
            };
        }
        upload(d_queries.ptr, gpu_queries.data(), query_count);
    } else {
        upload(d_queries.ptr, query_points, query_count);
    }
    if (!prepared->d_ranked_aggregate) throw std::runtime_error("prepared fixed_radius_neighbors_3d aggregate workspace is not initialized");
    CUdeviceptr d_aggregate = prepared->d_ranked_aggregate->ptr;
    CU_CHECK(cuMemsetD8(d_aggregate, 0, sizeof(RtdlFixedRadiusRankedNeighborAggregate)));
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_max, prepared->search_points.size()));

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_summary = std::chrono::steady_clock::now();
    if (use_direct_float32_aggregate) {
        float min_x = prepared->min_x;
        float min_y = prepared->min_y;
        float min_z = prepared->min_z;
        float inv_cell_size = prepared->inv_cell_size;
        float radius_f = static_cast<float>(radius);
        void* summary_args[] = {
            &d_queries.ptr,
            &qc,
            &prepared->d_search->ptr,
            &prepared->d_offsets->ptr,
            &grid_x,
            &grid_y,
            &grid_z,
            &min_x,
            &min_y,
            &min_z,
            &inv_cell_size,
            &radius_f,
            &k_max_u32,
            &d_aggregate,
        };
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_direct.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_summary = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);
    } else if (use_float32_precision) {
        DevPtr d_summaries(sizeof(RtdlFixedRadiusRankedNeighborSummary) * query_count);
        float min_x = prepared->min_x;
        float min_y = prepared->min_y;
        float min_z = prepared->min_z;
        float inv_cell_size = prepared->inv_cell_size;
        float radius_f = static_cast<float>(radius);
        void* summary_args[] = {
            &d_queries.ptr,
            &qc,
            &prepared->d_search->ptr,
            &prepared->d_offsets->ptr,
            &grid_x,
            &grid_y,
            &grid_z,
            &min_x,
            &min_y,
            &min_z,
            &inv_cell_size,
            &radius_f,
            &k_max_u32,
            &d_summaries.ptr,
        };
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_f32.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_summary = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);

        void* aggregate_args[] = {
            &d_summaries.ptr,
            &qc,
            &d_aggregate,
        };
        unsigned aggregate_grid = std::min<unsigned>(1024u, std::max<unsigned>(1u, grid));
        auto t_start_aggregate = std::chrono::steady_clock::now();
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate.fn, aggregate_grid, 1, 1, block, 1, 1, 0, nullptr, aggregate_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_aggregate = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_exact_refine_s = seconds_between(t_start_aggregate, t_end_aggregate);
    } else {
        DevPtr d_summaries(sizeof(RtdlFixedRadiusRankedNeighborSummary) * query_count);
        double min_x = prepared->min_x_exact;
        double min_y = prepared->min_y_exact;
        double min_z = prepared->min_z_exact;
        double inv_cell_size = prepared->inv_cell_size_exact;
        double radius_exact = radius;
        void* summary_args[] = {
            &d_queries.ptr,
            &qc,
            &prepared->d_search_exact->ptr,
            &prepared->d_offsets->ptr,
            &grid_x,
            &grid_y,
            &grid_z,
            &min_x,
            &min_y,
            &min_z,
            &inv_cell_size,
            &radius_exact,
            &k_max_u32,
            &d_summaries.ptr,
        };
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_summary = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);

        void* aggregate_args[] = {
            &d_summaries.ptr,
            &qc,
            &d_aggregate,
        };
        unsigned aggregate_grid = std::min<unsigned>(1024u, std::max<unsigned>(1u, grid));
        auto t_start_aggregate = std::chrono::steady_clock::now();
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate.fn, aggregate_grid, 1, 1, block, 1, 1, 0, nullptr, aggregate_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_aggregate = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_exact_refine_s = seconds_between(t_start_aggregate, t_end_aggregate);
    }

    auto t_start_download = std::chrono::steady_clock::now();
    download(&aggregate, d_aggregate, 1);
    auto t_end_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_download, t_end_download);

    g_optix_last_fixed_radius_3d_raw_candidate_count = aggregate.bounded_neighbor_count;
    g_optix_last_fixed_radius_3d_emitted_count = aggregate.query_count;
    return aggregate;
}

static RtdlFixedRadiusRankedNeighborAggregate aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        PreparedFixedRadiusQueryPoints3D* prepared_queries,
        double radius,
        size_t k_max)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!prepared_queries) throw std::runtime_error("prepared fixed-radius query handle must not be null");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
    }
    if (prepared_queries->query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (k_max == 0)
        throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
    if (k_max > 64)
        throw std::runtime_error("prepared ranked fixed_radius_neighbors_3d aggregate currently supports k_max <= 64");

    const double mean_search_points_per_occupied_cell =
        prepared->occupied_cell_count == 0
            ? 0.0
            : static_cast<double>(prepared->search_points.size()) /
                static_cast<double>(prepared->occupied_cell_count);
    const bool use_direct_float32_aggregate = mean_search_points_per_occupied_cell <= 4.0;
    const bool use_block_partial_direct =
        use_direct_float32_aggregate &&
        prepared_queries->query_count <= 65536u &&
        prepared_queries->d_aggregate_partials != nullptr;

    RtdlFixedRadiusRankedNeighborAggregate aggregate{0u, 0u, 0u, 0u, 0.0};
    reset_fixed_radius_3d_phase_timings(use_block_partial_direct ? 15u : use_direct_float32_aggregate ? 13u : 14u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    g_optix_last_fixed_radius_3d_upload_s = 0.0;
    if (prepared_queries->query_count == 0 || prepared->search_points.empty()) return aggregate;

    uint32_t qc = static_cast<uint32_t>(prepared_queries->query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_max, prepared->search_points.size()));

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_summary = std::chrono::steady_clock::now();
    if (use_block_partial_direct) {
        if (prepared_queries->aggregate_block_count < grid) {
            throw std::runtime_error("prepared fixed_radius_neighbors_3d aggregate partial workspace is too small");
        }
        float min_x = prepared->min_x;
        float min_y = prepared->min_y;
        float min_z = prepared->min_z;
        float inv_cell_size = prepared->inv_cell_size;
        float radius_f = static_cast<float>(radius);
        CUdeviceptr d_partials = prepared_queries->d_aggregate_partials->ptr;
        void* summary_args[] = {
            &prepared_queries->d_queries->ptr,
            &qc,
            &prepared->d_search->ptr,
            &prepared->d_offsets->ptr,
            &grid_x,
            &grid_y,
            &grid_z,
            &min_x,
            &min_y,
            &min_z,
            &inv_cell_size,
            &radius_f,
            &k_max_u32,
            &d_partials,
        };
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_blocks.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_summary = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);

        auto t_start_download = std::chrono::steady_clock::now();
        std::vector<RtdlFixedRadiusRankedNeighborAggregate> partials(grid);
        download(partials.data(), d_partials, grid);
        for (const auto& partial : partials) {
            aggregate.query_count += partial.query_count;
            aggregate.bounded_neighbor_count += partial.bounded_neighbor_count;
            aggregate.nearest_id_checksum += partial.nearest_id_checksum;
            aggregate.kth_id_checksum += partial.kth_id_checksum;
            aggregate.sum_distance += partial.sum_distance;
        }
        auto t_end_download = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_download, t_end_download);
        g_optix_last_fixed_radius_3d_raw_candidate_count = aggregate.bounded_neighbor_count;
        g_optix_last_fixed_radius_3d_emitted_count = aggregate.query_count;
        return aggregate;
    }

    if (!prepared->d_ranked_aggregate) throw std::runtime_error("prepared fixed_radius_neighbors_3d aggregate workspace is not initialized");
    CUdeviceptr d_aggregate = prepared->d_ranked_aggregate->ptr;
    CU_CHECK(cuMemsetD8(d_aggregate, 0, sizeof(RtdlFixedRadiusRankedNeighborAggregate)));

    if (use_direct_float32_aggregate) {
        float min_x = prepared->min_x;
        float min_y = prepared->min_y;
        float min_z = prepared->min_z;
        float inv_cell_size = prepared->inv_cell_size;
        float radius_f = static_cast<float>(radius);
        void* summary_args[] = {
            &prepared_queries->d_queries->ptr,
            &qc,
            &prepared->d_search->ptr,
            &prepared->d_offsets->ptr,
            &grid_x,
            &grid_y,
            &grid_z,
            &min_x,
            &min_y,
            &min_z,
            &inv_cell_size,
            &radius_f,
            &k_max_u32,
            &d_aggregate,
        };
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_direct.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_summary = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);
    } else {
        DevPtr d_summaries(sizeof(RtdlFixedRadiusRankedNeighborSummary) * prepared_queries->query_count);
        float min_x = prepared->min_x;
        float min_y = prepared->min_y;
        float min_z = prepared->min_z;
        float inv_cell_size = prepared->inv_cell_size;
        float radius_f = static_cast<float>(radius);
        void* summary_args[] = {
            &prepared_queries->d_queries->ptr,
            &qc,
            &prepared->d_search->ptr,
            &prepared->d_offsets->ptr,
            &grid_x,
            &grid_y,
            &grid_z,
            &min_x,
            &min_y,
            &min_z,
            &inv_cell_size,
            &radius_f,
            &k_max_u32,
            &d_summaries.ptr,
        };
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_f32.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_summary = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);

        void* aggregate_args[] = {
            &d_summaries.ptr,
            &qc,
            &d_aggregate,
        };
        unsigned aggregate_grid = std::min<unsigned>(1024u, std::max<unsigned>(1u, grid));
        auto t_start_aggregate = std::chrono::steady_clock::now();
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate.fn, aggregate_grid, 1, 1, block, 1, 1, 0, nullptr, aggregate_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_aggregate = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_exact_refine_s = seconds_between(t_start_aggregate, t_end_aggregate);
    }

    auto t_start_download = std::chrono::steady_clock::now();
    download(&aggregate, d_aggregate, 1);
    auto t_end_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_download, t_end_download);

    g_optix_last_fixed_radius_3d_raw_candidate_count = aggregate.bounded_neighbor_count;
    g_optix_last_fixed_radius_3d_emitted_count = aggregate.query_count;
    return aggregate;
}

static void aggregate_prepared_query_ranked_fixed_radius_neighbor_summaries_grid_3d_batch_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        PreparedFixedRadiusQueryPoints3D* prepared_queries,
        const double* radii,
        const size_t* k_values,
        size_t request_count,
        RtdlFixedRadiusRankedNeighborAggregate* aggregates_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!prepared_queries) throw std::runtime_error("prepared fixed-radius query handle must not be null");
    if (!aggregates_out && request_count != 0) throw std::runtime_error("aggregates_out must not be null when request_count is nonzero");
    if (!radii && request_count != 0) throw std::runtime_error("radii pointer must not be null when request_count is nonzero");
    if (!k_values && request_count != 0) throw std::runtime_error("k_values pointer must not be null when request_count is nonzero");
    if (prepared_queries->query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (request_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d aggregate request_count exceeds uint32 limit");

    for (size_t request_index = 0; request_index < request_count; ++request_index) {
        const double radius = radii[request_index];
        const size_t k_max = k_values[request_index];
        if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
        if (radius > prepared->max_radius + 1.0e-7) {
            throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
        }
        if (k_max == 0)
            throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
        if (k_max > 64)
            throw std::runtime_error("prepared ranked fixed_radius_neighbors_3d aggregate currently supports k_max <= 64");
    }

    const bool use_block_partial_batch = prepared_queries->query_count <= 65536u;
    reset_fixed_radius_3d_phase_timings(use_block_partial_batch ? 17u : 16u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;
    g_optix_last_fixed_radius_3d_upload_s = 0.0;
    if (request_count == 0) return;
    std::fill(
        aggregates_out,
        aggregates_out + request_count,
        RtdlFixedRadiusRankedNeighborAggregate{0u, 0u, 0u, 0u, 0.0});
    if (prepared_queries->query_count == 0 || prepared->search_points.empty()) return;

    uint32_t qc = static_cast<uint32_t>(prepared_queries->query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    float min_x = prepared->min_x;
    float min_y = prepared->min_y;
    float min_z = prepared->min_z;
    float inv_cell_size = prepared->inv_cell_size;

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_summary = std::chrono::steady_clock::now();

    if (use_block_partial_batch) {
        DevPtr d_partials(sizeof(RtdlFixedRadiusRankedNeighborAggregate) * request_count * grid);
        std::vector<float> radii_f(request_count);
        std::vector<uint32_t> k_values_u32(request_count);
        for (size_t request_index = 0; request_index < request_count; ++request_index) {
            radii_f[request_index] = static_cast<float>(radii[request_index]);
            k_values_u32[request_index] =
                static_cast<uint32_t>(std::min(k_values[request_index], prepared->search_points.size()));
        }
        DevPtr d_radii(sizeof(float) * request_count);
        DevPtr d_k_values(sizeof(uint32_t) * request_count);
        upload(d_radii.ptr, radii_f.data(), request_count);
        upload(d_k_values.ptr, k_values_u32.data(), request_count);
        uint32_t request_count_u32 = static_cast<uint32_t>(request_count);
        void* summary_args[] = {
            &prepared_queries->d_queries->ptr,
            &qc,
            &prepared->d_search->ptr,
            &prepared->d_offsets->ptr,
            &grid_x,
            &grid_y,
            &grid_z,
            &min_x,
            &min_y,
            &min_z,
            &inv_cell_size,
            &d_radii.ptr,
            &d_k_values.ptr,
            &request_count_u32,
            &d_partials.ptr,
        };
        CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_blocks_batch.fn, grid, request_count_u32, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
        DevPtr d_aggregates(sizeof(RtdlFixedRadiusRankedNeighborAggregate) * request_count);
        uint32_t partial_count_u32 = static_cast<uint32_t>(grid);
        void* reduce_args[] = {
            &d_partials.ptr,
            &partial_count_u32,
            &request_count_u32,
            &d_aggregates.ptr,
        };
        CU_CHECK(cuLaunchKernel(g_frn3d_ranked_aggregate_partials_reduce.fn, request_count_u32, 1, 1, block, 1, 1, 0, nullptr, reduce_args, nullptr));
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_summary = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);

        auto t_start_download = std::chrono::steady_clock::now();
        download(aggregates_out, d_aggregates.ptr, request_count);
        auto t_end_download = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_download, t_end_download);
    } else {
        DevPtr d_aggregates(sizeof(RtdlFixedRadiusRankedNeighborAggregate) * request_count);
        CU_CHECK(cuMemsetD8(d_aggregates.ptr, 0, sizeof(RtdlFixedRadiusRankedNeighborAggregate) * request_count));

        for (size_t request_index = 0; request_index < request_count; ++request_index) {
            float radius_f = static_cast<float>(radii[request_index]);
            uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_values[request_index], prepared->search_points.size()));
            CUdeviceptr d_aggregate = d_aggregates.ptr + sizeof(RtdlFixedRadiusRankedNeighborAggregate) * request_index;
            void* summary_args[] = {
                &prepared_queries->d_queries->ptr,
                &qc,
                &prepared->d_search->ptr,
                &prepared->d_offsets->ptr,
                &grid_x,
                &grid_y,
                &grid_z,
                &min_x,
                &min_y,
                &min_z,
                &inv_cell_size,
                &radius_f,
                &k_max_u32,
                &d_aggregate,
            };
            CU_CHECK(cuLaunchKernel(g_frn3d_grid_ranked_summary_aggregate_f32_direct.fn, grid, 1, 1, block, 1, 1, 0, nullptr, summary_args, nullptr));
        }
        CU_CHECK(cuStreamSynchronize(nullptr));
        auto t_end_summary = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_summary, t_end_summary);

        auto t_start_download = std::chrono::steady_clock::now();
        download(aggregates_out, d_aggregates.ptr, request_count);
        auto t_end_download = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_download, t_end_download);
    }

    size_t total_bounded = 0u;
    size_t total_queries = 0u;
    for (size_t request_index = 0; request_index < request_count; ++request_index) {
        total_bounded += aggregates_out[request_index].bounded_neighbor_count;
        total_queries += aggregates_out[request_index].query_count;
    }
    g_optix_last_fixed_radius_3d_raw_candidate_count = total_bounded;
    g_optix_last_fixed_radius_3d_emitted_count = total_queries;
}

static void run_prepared_fixed_radius_neighbors_grid_3d_optix(
        PreparedFixedRadiusNeighborsGrid3D* prepared,
        const RtdlPoint3D* query_points, size_t query_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius-neighbor 3D handle must not be null");
    if (!rows_out || !row_count_out) throw std::runtime_error("output pointers must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_neighbors_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_neighbors_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d query_count exceeds uint32 limit");
    if (k_max == 0)
        throw std::runtime_error("fixed_radius_neighbors_3d k_max must be positive");
    if (k_max > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_neighbors_3d k_max exceeds uint32 limit");

    *rows_out = nullptr;
    *row_count_out = 0;
    if (query_count == 0 || prepared->search_points.empty()) return;

    reset_fixed_radius_3d_phase_timings(4u);
    g_optix_last_fixed_radius_3d_prepare_s = 0.0;

    auto t_start_upload = std::chrono::steady_clock::now();
    std::vector<GpuPoint3DHost> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            static_cast<float>(query_points[i].z),
            query_points[i].id,
        };
    }
    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    DevPtr d_counts(sizeof(uint32_t) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    uint32_t qc = static_cast<uint32_t>(query_count);
    uint32_t grid_x = prepared->grid_x;
    uint32_t grid_y = prepared->grid_y;
    uint32_t grid_z = prepared->grid_z;
    float min_x = prepared->min_x;
    float min_y = prepared->min_y;
    float min_z = prepared->min_z;
    float inv_cell_size = prepared->inv_cell_size;
    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    float radius_f = static_cast<float>(radius + kFixedRadiusCandidateEps);
    uint32_t k_max_u32 = static_cast<uint32_t>(std::min(k_max, prepared->search_points.size()));

    void* count_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search->ptr,
        &prepared->d_offsets->ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_f,
        &k_max_u32,
        &d_counts.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_count = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_count.fn, grid, 1, 1, block, 1, 1, 0, nullptr, count_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_count = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_count, t_end_count);

    auto t_start_count_download = std::chrono::steady_clock::now();
    std::vector<uint32_t> gpu_counts(query_count);
    download(gpu_counts.data(), d_counts.ptr, query_count);
    std::vector<uint32_t> row_offsets(query_count + 1u, 0u);
    for (size_t i = 0; i < query_count; ++i) {
        row_offsets[i + 1u] = row_offsets[i] + std::min(gpu_counts[i], k_max_u32);
    }
    const size_t compact_capacity = static_cast<size_t>(row_offsets.back());
    auto t_end_count_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_download_s = seconds_between(t_start_count_download, t_end_count_download);
    g_optix_last_fixed_radius_3d_raw_candidate_count = compact_capacity;
    if (compact_capacity > static_cast<size_t>(UINT32_MAX)) {
        throw std::runtime_error("fixed_radius_neighbors_3d prepared compact output exceeds uint32 limit");
    }

    DevPtr d_row_offsets(sizeof(uint32_t) * row_offsets.size());
    DevPtr d_output(sizeof(GpuFrnRecord) * compact_capacity);
    auto t_start_row_offset_upload = std::chrono::steady_clock::now();
    upload(d_row_offsets.ptr, row_offsets.data(), row_offsets.size());
    auto t_end_row_offset_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_offset_upload_s = seconds_between(t_start_row_offset_upload, t_end_row_offset_upload);

    void* compact_args[] = {
        &d_queries.ptr,
        &qc,
        &prepared->d_search->ptr,
        &prepared->d_offsets->ptr,
        &d_row_offsets.ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x,
        &min_y,
        &min_z,
        &inv_cell_size,
        &radius_f,
        &k_max_u32,
        &d_output.ptr,
    };
    auto t_start_compact = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_compact.fn, grid, 1, 1, block, 1, 1, 0, nullptr, compact_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_compact = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_compact_s = seconds_between(t_start_compact, t_end_compact);

    auto t_start_row_download = std::chrono::steady_clock::now();
    std::vector<GpuFrnRecord> gpu_rows(compact_capacity);
    download(gpu_rows.data(), d_output.ptr, compact_capacity);
    auto t_end_row_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_row_download, t_end_row_download);

    auto t_start_refine = std::chrono::steady_clock::now();
    bool direct_query_ids = true;
    bool direct_search_ids = true;
    for (size_t i = 0; i < query_count; ++i) {
        if (query_points[i].id != static_cast<uint32_t>(i)) {
            direct_query_ids = false;
            break;
        }
    }
    for (size_t i = 0; i < prepared->search_points.size(); ++i) {
        if (prepared->search_points[i].id != static_cast<uint32_t>(i)) {
            direct_search_ids = false;
            break;
        }
    }

    std::vector<RtdlFixedRadiusNeighborRow> rows;
    rows.reserve(compact_capacity);
    if (direct_query_ids && direct_search_ids) {
        for (size_t qidx = 0; qidx < query_count; ++qidx) {
            size_t current_count = 0;
            const RtdlPoint3D& q = query_points[qidx];
            const size_t base = row_offsets[qidx];
            const size_t populated = row_offsets[qidx + 1u] - row_offsets[qidx];
            for (size_t slot = 0; slot < populated; ++slot) {
                const GpuFrnRecord& gpu_row = gpu_rows[base + slot];
                const size_t neighbor_index = static_cast<size_t>(gpu_row.neighbor_id);
                if (neighbor_index >= prepared->search_points.size()) {
                    continue;
                }
                const RtdlPoint3D& t = prepared->search_points[neighbor_index];
                double dx = t.x - q.x;
                double dy = t.y - q.y;
                double dz = t.z - q.z;
                double exact_distance = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (exact_distance <= radius) {
                    rows.push_back({
                        static_cast<uint32_t>(qidx),
                        gpu_row.neighbor_id,
                        exact_distance,
                    });
                    current_count += 1;
                    if (current_count >= k_max) {
                        break;
                    }
                }
            }
        }
    } else {
        std::unordered_map<uint32_t, const RtdlPoint3D*> query_by_id;
        std::unordered_map<uint32_t, const RtdlPoint3D*> search_by_id;
        query_by_id.reserve(query_count);
        search_by_id.reserve(prepared->search_points.size());
        for (size_t i = 0; i < query_count; ++i) {
            query_by_id.emplace(query_points[i].id, query_points + i);
        }
        for (size_t i = 0; i < prepared->search_points.size(); ++i) {
            search_by_id.emplace(prepared->search_points[i].id, prepared->search_points.data() + i);
        }

        std::vector<RtdlFixedRadiusNeighborRow> exact_rows;
        exact_rows.reserve(compact_capacity);
        for (size_t qidx = 0; qidx < query_count; ++qidx) {
            const size_t base = row_offsets[qidx];
            const size_t populated = row_offsets[qidx + 1u] - row_offsets[qidx];
            for (size_t slot = 0; slot < populated; ++slot) {
                const GpuFrnRecord& gpu_row = gpu_rows[base + slot];
                auto query_it = query_by_id.find(gpu_row.query_id);
                auto search_it = search_by_id.find(gpu_row.neighbor_id);
                if (query_it == query_by_id.end() || search_it == search_by_id.end()) {
                    continue;
                }
                double dx = search_it->second->x - query_it->second->x;
                double dy = search_it->second->y - query_it->second->y;
                double dz = search_it->second->z - query_it->second->z;
                double exact_distance = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (exact_distance <= radius) {
                    exact_rows.push_back({
                        gpu_row.query_id,
                        gpu_row.neighbor_id,
                        exact_distance,
                    });
                }
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
    }

    auto* out = static_cast<RtdlFixedRadiusNeighborRow*>(
        std::malloc(sizeof(RtdlFixedRadiusNeighborRow) * rows.size()));
    if (!out && !rows.empty()) throw std::bad_alloc();
    if (!rows.empty()) {
        std::memcpy(out, rows.data(), sizeof(RtdlFixedRadiusNeighborRow) * rows.size());
    }
    auto t_end_refine = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_exact_refine_s = seconds_between(t_start_refine, t_end_refine);
    g_optix_last_fixed_radius_3d_emitted_count = rows.size();
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_fixed_radius_neighbors_grid_cuda_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        const RtdlPoint3D* search_points, size_t search_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out)
{
    if (radius <= 0.0) {
        run_fixed_radius_neighbors_cuda_3d(
            query_points, query_count,
            search_points, search_count,
            radius, k_max,
            rows_out, row_count_out);
        return;
    }

    ensure_fixed_radius_neighbors_grid_cuda_3d_kernel();

    reset_fixed_radius_3d_phase_timings(2u);
    auto t_start_prepare = std::chrono::steady_clock::now();
    double min_x = search_points[0].x;
    double min_y = search_points[0].y;
    double min_z = search_points[0].z;
    double max_x = search_points[0].x;
    double max_y = search_points[0].y;
    double max_z = search_points[0].z;
    for (size_t i = 1; i < search_count; ++i) {
        min_x = std::min(min_x, search_points[i].x);
        min_y = std::min(min_y, search_points[i].y);
        min_z = std::min(min_z, search_points[i].z);
        max_x = std::max(max_x, search_points[i].x);
        max_y = std::max(max_y, search_points[i].y);
        max_z = std::max(max_z, search_points[i].z);
    }

    const double cell_size = radius;
    const auto grid_dim_for = [&](double lo, double hi) -> size_t {
        const double span = std::max(0.0, hi - lo);
        return static_cast<size_t>(std::floor(span / cell_size)) + 1u;
    };
    const size_t grid_x_size = grid_dim_for(min_x, max_x);
    const size_t grid_y_size = grid_dim_for(min_y, max_y);
    const size_t grid_z_size = grid_dim_for(min_z, max_z);
    constexpr size_t kMaxDenseGridCells = 16u * 1024u * 1024u;
    if (grid_x_size == 0 || grid_y_size == 0 || grid_z_size == 0 ||
            grid_x_size > static_cast<size_t>(UINT32_MAX) ||
            grid_y_size > static_cast<size_t>(UINT32_MAX) ||
            grid_z_size > static_cast<size_t>(UINT32_MAX) ||
            grid_x_size > ((std::numeric_limits<size_t>::max)() / grid_y_size) ||
            grid_x_size * grid_y_size > ((std::numeric_limits<size_t>::max)() / grid_z_size)) {
        run_fixed_radius_neighbors_cuda_3d(
            query_points, query_count,
            search_points, search_count,
            radius, k_max,
            rows_out, row_count_out);
        return;
    }
    const size_t cell_count = grid_x_size * grid_y_size * grid_z_size;
    if (cell_count == 0 || cell_count > kMaxDenseGridCells) {
        run_fixed_radius_neighbors_cuda_3d(
            query_points, query_count,
            search_points, search_count,
            radius, k_max,
            rows_out, row_count_out);
        return;
    }

    uint32_t grid_x = static_cast<uint32_t>(grid_x_size);
    uint32_t grid_y = static_cast<uint32_t>(grid_y_size);
    uint32_t grid_z = static_cast<uint32_t>(grid_z_size);
    const double inv_cell_size_d = 1.0 / cell_size;
    const auto cell_for = [&](const RtdlPoint3D& point) -> uint32_t {
        const auto coord = [&](double value, double lo, uint32_t dim) -> uint32_t {
            long long raw = static_cast<long long>(std::floor((value - lo) * inv_cell_size_d));
            if (raw < 0) raw = 0;
            const long long max_raw = static_cast<long long>(dim) - 1;
            if (raw > max_raw) raw = max_raw;
            return static_cast<uint32_t>(raw);
        };
        const uint32_t ix = coord(point.x, min_x, grid_x);
        const uint32_t iy = coord(point.y, min_y, grid_y);
        const uint32_t iz = coord(point.z, min_z, grid_z);
        return (iz * grid_y + iy) * grid_x + ix;
    };

    std::vector<uint32_t> counts(cell_count, 0u);
    std::vector<uint32_t> search_cell(search_count);
    for (size_t i = 0; i < search_count; ++i) {
        const uint32_t cell = cell_for(search_points[i]);
        search_cell[i] = cell;
        counts[cell] += 1u;
    }

    std::vector<uint32_t> cell_offsets(cell_count + 1u, 0u);
    for (size_t cell = 0; cell < cell_count; ++cell) {
        cell_offsets[cell + 1u] = cell_offsets[cell] + counts[cell];
    }

    std::vector<uint32_t> cursor = cell_offsets;
    std::vector<GpuPoint3DHost> sorted_search(search_count);
    for (size_t i = 0; i < search_count; ++i) {
        const uint32_t cell = search_cell[i];
        const uint32_t dest = cursor[cell]++;
        sorted_search[dest] = {
            static_cast<float>(search_points[i].x),
            static_cast<float>(search_points[i].y),
            static_cast<float>(search_points[i].z),
            search_points[i].id,
        };
    }

    std::vector<GpuPoint3DHost> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            static_cast<float>(query_points[i].z),
            query_points[i].id,
        };
    }

    const size_t kernel_k_max = std::min(k_max, search_count);
    if (query_count != 0 && kernel_k_max > ((std::numeric_limits<size_t>::max)() / query_count)) {
        throw std::runtime_error("fixed_radius_neighbors_3d grid output_capacity overflows size_t");
    }
    const size_t output_capacity = query_count * kernel_k_max;
    (void)output_capacity;
    auto t_end_prepare = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_prepare_s = seconds_between(t_start_prepare, t_end_prepare);

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    DevPtr d_search(sizeof(GpuPoint3DHost) * search_count);
    DevPtr d_offsets(sizeof(uint32_t) * cell_offsets.size());
    DevPtr d_counts(sizeof(uint32_t) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    upload(d_search.ptr, sorted_search.data(), search_count);
    upload(d_offsets.ptr, cell_offsets.data(), cell_offsets.size());
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    uint32_t qc = static_cast<uint32_t>(query_count);
    float min_x_f = static_cast<float>(min_x);
    float min_y_f = static_cast<float>(min_y);
    float min_z_f = static_cast<float>(min_z);
    float inv_cell_size = static_cast<float>(inv_cell_size_d);
    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    float radius_f = static_cast<float>(radius + kFixedRadiusCandidateEps);
    uint32_t k_max_u32 = static_cast<uint32_t>(kernel_k_max);
    void* count_args[] = {
        &d_queries.ptr,
        &qc,
        &d_search.ptr,
        &d_offsets.ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x_f,
        &min_y_f,
        &min_z_f,
        &inv_cell_size,
        &radius_f,
        &k_max_u32,
        &d_counts.ptr,
    };

    unsigned block = 256;
    unsigned grid = (qc + block - 1u) / block;
    auto t_start_count = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_count.fn, grid, 1, 1, block, 1, 1, 0, nullptr, count_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_count = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_s = seconds_between(t_start_count, t_end_count);

    auto t_start_count_download = std::chrono::steady_clock::now();
    std::vector<uint32_t> gpu_counts(query_count);
    download(gpu_counts.data(), d_counts.ptr, query_count);
    std::vector<uint32_t> row_offsets(query_count + 1u, 0u);
    for (size_t i = 0; i < query_count; ++i) {
        row_offsets[i + 1u] = row_offsets[i] + std::min(gpu_counts[i], k_max_u32);
    }
    const size_t compact_capacity = static_cast<size_t>(row_offsets.back());
    auto t_end_count_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_count_download_s = seconds_between(t_start_count_download, t_end_count_download);
    g_optix_last_fixed_radius_3d_raw_candidate_count = compact_capacity;
    if (compact_capacity > static_cast<size_t>(UINT32_MAX)) {
        run_fixed_radius_neighbors_cuda_3d(
            query_points, query_count,
            search_points, search_count,
            radius, k_max,
            rows_out, row_count_out);
        return;
    }
    DevPtr d_row_offsets(sizeof(uint32_t) * row_offsets.size());
    DevPtr d_output(sizeof(GpuFrnRecord) * compact_capacity);
    auto t_start_row_offset_upload = std::chrono::steady_clock::now();
    upload(d_row_offsets.ptr, row_offsets.data(), row_offsets.size());
    auto t_end_row_offset_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_offset_upload_s = seconds_between(t_start_row_offset_upload, t_end_row_offset_upload);
    void* compact_args[] = {
        &d_queries.ptr,
        &qc,
        &d_search.ptr,
        &d_offsets.ptr,
        &d_row_offsets.ptr,
        &grid_x,
        &grid_y,
        &grid_z,
        &min_x_f,
        &min_y_f,
        &min_z_f,
        &inv_cell_size,
        &radius_f,
        &k_max_u32,
        &d_output.ptr,
    };
    auto t_start_compact = std::chrono::steady_clock::now();
    CU_CHECK(cuLaunchKernel(g_frn3d_grid_compact.fn, grid, 1, 1, block, 1, 1, 0, nullptr, compact_args, nullptr));
    CU_CHECK(cuStreamSynchronize(nullptr));
    auto t_end_compact = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_compact_s = seconds_between(t_start_compact, t_end_compact);

    auto t_start_row_download = std::chrono::steady_clock::now();
    std::vector<GpuFrnRecord> gpu_rows(compact_capacity);
    download(gpu_rows.data(), d_output.ptr, compact_capacity);
    auto t_end_row_download = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_row_download_s = seconds_between(t_start_row_download, t_end_row_download);

    auto t_start_refine = std::chrono::steady_clock::now();
    bool direct_query_ids = true;
    bool direct_search_ids = true;
    for (size_t i = 0; i < query_count; ++i) {
        if (query_points[i].id != static_cast<uint32_t>(i)) {
            direct_query_ids = false;
            break;
        }
    }
    for (size_t i = 0; i < search_count; ++i) {
        if (search_points[i].id != static_cast<uint32_t>(i)) {
            direct_search_ids = false;
            break;
        }
    }

    if (direct_query_ids && direct_search_ids) {
        std::vector<RtdlFixedRadiusNeighborRow> rows;
        rows.reserve(compact_capacity);
        for (size_t qidx = 0; qidx < query_count; ++qidx) {
            size_t current_count = 0;
            const RtdlPoint3D& q = query_points[qidx];
            const size_t base = row_offsets[qidx];
            const size_t populated = row_offsets[qidx + 1u] - row_offsets[qidx];
            for (size_t slot = 0; slot < populated; ++slot) {
                const GpuFrnRecord& gpu_row = gpu_rows[base + slot];
                const size_t neighbor_index = static_cast<size_t>(gpu_row.neighbor_id);
                if (neighbor_index >= search_count) {
                    continue;
                }
                const RtdlPoint3D& t = search_points[neighbor_index];
                double dx = t.x - q.x;
                double dy = t.y - q.y;
                double dz = t.z - q.z;
                double exact_distance = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (exact_distance <= radius) {
                    rows.push_back({
                        static_cast<uint32_t>(qidx),
                        gpu_row.neighbor_id,
                        exact_distance,
                    });
                    current_count += 1;
                    if (current_count >= k_max) {
                        break;
                    }
                }
            }
        }
        auto* out = static_cast<RtdlFixedRadiusNeighborRow*>(
            std::malloc(sizeof(RtdlFixedRadiusNeighborRow) * rows.size()));
        if (!out && !rows.empty()) throw std::bad_alloc();
        if (!rows.empty()) {
            std::memcpy(out, rows.data(), sizeof(RtdlFixedRadiusNeighborRow) * rows.size());
        }
        auto t_end_refine = std::chrono::steady_clock::now();
        g_optix_last_fixed_radius_3d_exact_refine_s = seconds_between(t_start_refine, t_end_refine);
        g_optix_last_fixed_radius_3d_emitted_count = rows.size();
        *rows_out = out;
        *row_count_out = rows.size();
        return;
    }

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
    exact_rows.reserve(compact_capacity);
    for (size_t qidx = 0; qidx < query_count; ++qidx) {
        const size_t base = row_offsets[qidx];
        const size_t populated = row_offsets[qidx + 1u] - row_offsets[qidx];
        for (size_t slot = 0; slot < populated; ++slot) {
            const GpuFrnRecord& gpu_row = gpu_rows[base + slot];
            auto query_it = query_by_id.find(gpu_row.query_id);
            auto search_it = search_by_id.find(gpu_row.neighbor_id);
            if (query_it == query_by_id.end() || search_it == search_by_id.end()) {
                continue;
            }
            double dx = search_it->second->x - query_it->second->x;
            double dy = search_it->second->y - query_it->second->y;
            double dz = search_it->second->z - query_it->second->z;
            double exact_distance = std::sqrt(dx * dx + dy * dy + dz * dz);
            if (exact_distance <= radius) {
                exact_rows.push_back({
                    gpu_row.query_id,
                    gpu_row.neighbor_id,
                    exact_distance,
                });
            }
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
    auto t_end_refine = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_exact_refine_s = seconds_between(t_start_refine, t_end_refine);
    g_optix_last_fixed_radius_3d_raw_candidate_count = compact_capacity;
    g_optix_last_fixed_radius_3d_emitted_count = rows.size();
    *rows_out = out;
    *row_count_out = rows.size();
}

static void run_fixed_radius_neighbors_rt_3d(
        const RtdlPoint3D* query_points, size_t query_count,
        const RtdlPoint3D* search_points, size_t search_count,
        double radius,
        size_t k_max,
        RtdlFixedRadiusNeighborRow** rows_out, size_t* row_count_out)
{
    reset_fixed_radius_3d_phase_timings(3u);
    std::call_once(g_frn3d_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusNeighbors3DRtKernelSrc, "frn3d_rt_kernel.cu");
        g_frn3d_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__frn3d_probe",
            "__miss__frn3d_miss",
            "__intersection__frn3d_isect",
            "__anyhit__frn3d_anyhit",
            nullptr, 1).release();
    });

    constexpr float kRadiusPad = 1.0e-4f;
    const float radius_f = static_cast<float>(radius);
    const float aabb_radius = radius_f + kRadiusPad;

    auto t_start_prepare = std::chrono::steady_clock::now();
    std::vector<GpuPoint3DHost> gpu_queries(query_count);
    std::vector<GpuPoint3DHost> gpu_search(search_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            static_cast<float>(query_points[i].z),
            query_points[i].id,
        };
    }
    for (size_t i = 0; i < search_count; ++i) {
        gpu_search[i] = {
            static_cast<float>(search_points[i].x),
            static_cast<float>(search_points[i].y),
            static_cast<float>(search_points[i].z),
            search_points[i].id,
        };
    }

    const size_t kernel_k_max = std::min(k_max, search_count);
    if (query_count != 0 && kernel_k_max > ((std::numeric_limits<size_t>::max)() / query_count)) {
        throw std::runtime_error("fixed_radius_neighbors_3d rt output_capacity overflows size_t");
    }
    const size_t output_capacity = query_count * kernel_k_max;
    auto t_end_prepare = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_prepare_s = seconds_between(t_start_prepare, t_end_prepare);

    auto t_start_upload = std::chrono::steady_clock::now();
    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    DevPtr d_search(sizeof(GpuPoint3DHost) * search_count);
    DevPtr d_output(sizeof(GpuFrnRecord) * output_capacity);
    upload(d_queries.ptr, gpu_queries.data(), query_count);
    upload(d_search.ptr, gpu_search.data(), search_count);
    auto t_end_upload = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_upload_s = seconds_between(t_start_upload, t_end_upload);

    std::vector<OptixAabb> aabbs(search_count);
    for (size_t i = 0; i < search_count; ++i) {
        const GpuPoint3DHost& p = gpu_search[i];
        OptixAabb aabb;
        aabb.minX = p.x - aabb_radius;
        aabb.minY = p.y - aabb_radius;
        aabb.minZ = p.z - aabb_radius;
        aabb.maxX = p.x + aabb_radius;
        aabb.maxY = p.y + aabb_radius;
        aabb.maxZ = p.z + aabb_radius;
        aabbs[i] = aabb;
    }

    auto t_start_bvh = std::chrono::steady_clock::now();
    AccelHolder accel = build_custom_accel(get_optix_context(), aabbs);
    auto t_end_bvh = std::chrono::steady_clock::now();
    g_optix_last_bvh_build_s = std::chrono::duration<double>(t_end_bvh - t_start_bvh).count();
    g_optix_last_fixed_radius_3d_prepare_s += g_optix_last_bvh_build_s;

    FixedRadiusNeighbors3DRtLaunchParams lp;
    lp.traversable = accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint3DHost*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint3DHost*>(d_search.ptr);
    lp.output = reinterpret_cast<GpuFrnRecord*>(d_output.ptr);
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.k_max = static_cast<uint32_t>(kernel_k_max);
    lp.radius = radius_f;
    lp.trace_tmax = std::max(1.0e-6f, 2.0f * aabb_radius);

    DevPtr d_params(sizeof(FixedRadiusNeighbors3DRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn3d_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusNeighbors3DRtLaunchParams),
                             &g_frn3d_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();
    g_optix_last_fixed_radius_3d_compact_s = g_optix_last_traversal_s;

    auto t_start_copy = std::chrono::steady_clock::now();
    std::vector<GpuFrnRecord> gpu_rows(output_capacity);
    download(gpu_rows.data(), d_output.ptr, output_capacity);
    auto t_end_copy = std::chrono::steady_clock::now();
    g_optix_last_copy_s = std::chrono::duration<double>(t_end_copy - t_start_copy).count();
    g_optix_last_fixed_radius_3d_row_download_s = g_optix_last_copy_s;

    auto t_start_refine = std::chrono::steady_clock::now();
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
    auto t_end_refine = std::chrono::steady_clock::now();
    g_optix_last_fixed_radius_3d_exact_refine_s = seconds_between(t_start_refine, t_end_refine);
    g_optix_last_fixed_radius_3d_raw_candidate_count = output_capacity;
    g_optix_last_fixed_radius_3d_emitted_count = rows.size();
    *rows_out = out;
    *row_count_out = rows.size();
}

struct PreparedFixedRadiusCountThreshold3DRt {
    std::vector<RtdlPoint3D> search_points;
    std::unique_ptr<DevPtr> d_search;
    AccelHolder accel;
    double max_radius = 0.0;

    PreparedFixedRadiusCountThreshold3DRt(
            const RtdlPoint3D* source,
            size_t source_count,
            double radius_bound)
        : search_points(source_count),
          max_radius(radius_bound)
    {
        if (radius_bound <= 0.0) {
            throw std::runtime_error("fixed_radius_count_threshold_3d prepared max_radius must be positive");
        }
        if (!source && source_count != 0) {
            throw std::runtime_error("fixed_radius_count_threshold_3d source pointer must not be null when source_count is nonzero");
        }
        if (source_count == 0) {
            return;
        }
        std::copy(source, source + source_count, search_points.begin());
        std::vector<GpuPoint3DHost> gpu_search(source_count);
        constexpr float kRadiusPad = 1.0e-4f;
        const float aabb_radius = static_cast<float>(radius_bound) + kRadiusPad;
        std::vector<OptixAabb> aabbs(source_count);
        for (size_t i = 0; i < source_count; ++i) {
            const RtdlPoint3D& p = source[i];
            gpu_search[i] = {
                static_cast<float>(p.x),
                static_cast<float>(p.y),
                static_cast<float>(p.z),
                p.id,
            };
            OptixAabb aabb;
            aabb.minX = gpu_search[i].x - aabb_radius;
            aabb.minY = gpu_search[i].y - aabb_radius;
            aabb.minZ = gpu_search[i].z - aabb_radius;
            aabb.maxX = gpu_search[i].x + aabb_radius;
            aabb.maxY = gpu_search[i].y + aabb_radius;
            aabb.maxZ = gpu_search[i].z + aabb_radius;
            aabbs[i] = aabb;
        }
        d_search = std::make_unique<DevPtr>(sizeof(GpuPoint3DHost) * gpu_search.size());
        upload(d_search->ptr, gpu_search.data(), gpu_search.size());
        accel = build_custom_accel(get_optix_context(), aabbs);
    }
};

static PreparedFixedRadiusCountThreshold3DRt* prepare_fixed_radius_count_threshold_3d_rt_optix(
        const RtdlPoint3D* search_points,
        size_t search_count,
        double max_radius)
{
    std::call_once(g_frn3d_count_threshold_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusCountThreshold3DRtKernelSrc, "frn3d_count_threshold_rt_kernel.cu");
        g_frn3d_count_threshold_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__frn3d_count_threshold_probe",
            "__miss__frn3d_count_threshold_miss",
            "__intersection__frn3d_count_threshold_isect",
            "__anyhit__frn3d_count_threshold_anyhit",
            nullptr, 2).release();
    });
    return new PreparedFixedRadiusCountThreshold3DRt(search_points, search_count, max_radius);
}

static void write_prepared_fixed_radius_count_threshold_3d_device_outputs_optix(
        PreparedFixedRadiusCountThreshold3DRt* prepared,
        const RtdlPoint3D* query_points,
        size_t query_count,
        double radius,
        size_t threshold,
        uint32_t* query_ids_out,
        uint32_t* neighbor_counts_out,
        uint32_t* threshold_flags_out)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius count-threshold 3D handle must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_count_threshold_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_count_threshold_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_count_threshold_3d query_count exceeds uint32 limit");
    if (threshold > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_count_threshold_3d threshold exceeds uint32 limit");
    if (query_count == 0) return;
    if (!query_ids_out || !neighbor_counts_out || !threshold_flags_out)
        throw std::runtime_error("fixed_radius_count_threshold_3d device output pointers must not be null when query_count is nonzero");

    std::vector<GpuPoint3DHost> gpu_queries(query_count);
    std::vector<uint32_t> query_ids(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            static_cast<float>(query_points[i].z),
            query_points[i].id,
        };
        query_ids[i] = query_points[i].id;
    }

    if (!prepared->accel.handle || prepared->search_points.empty()) {
        CUstream stream = 0;
        CU_CHECK(cuMemcpyHtoD(reinterpret_cast<CUdeviceptr>(query_ids_out), query_ids.data(), sizeof(uint32_t) * query_count));
        CU_CHECK(cuMemsetD32(reinterpret_cast<CUdeviceptr>(neighbor_counts_out), 0u, query_count));
        CU_CHECK(cuMemsetD32(reinterpret_cast<CUdeviceptr>(threshold_flags_out), threshold == 0 ? 1u : 0u, query_count));
        CU_CHECK(cuStreamSynchronize(stream));
        return;
    }

    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);

    constexpr float kRadiusPad = 1.0e-4f;
    const float radius_f = static_cast<float>(radius);
    const float aabb_radius = static_cast<float>(prepared->max_radius) + kRadiusPad;

    FixedRadiusCountThreshold3DRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint3DHost*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint3DHost*>(prepared->d_search->ptr);
    lp.query_ids_out = query_ids_out;
    lp.neighbor_counts_out = neighbor_counts_out;
    lp.threshold_flags_out = threshold_flags_out;
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.threshold = static_cast<uint32_t>(threshold);
    lp.radius = radius_f;
    lp.trace_tmax = std::max(1.0e-6f, 2.0f * aabb_radius);

    DevPtr d_params(sizeof(FixedRadiusCountThreshold3DRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn3d_count_threshold_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusCountThreshold3DRtLaunchParams),
                             &g_frn3d_count_threshold_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();
    g_optix_last_copy_s = 0.0;
}

static void write_prepared_fixed_radius_adjacency_3d_device_outputs_optix(
        PreparedFixedRadiusCountThreshold3DRt* prepared,
        const RtdlPoint3D* query_points,
        size_t query_count,
        double radius,
        const int64_t* edge_offsets,
        int32_t* neighbor_indices_out,
        size_t neighbor_index_capacity)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius adjacency 3D handle must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_adjacency_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_adjacency_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_adjacency_3d query_count exceeds uint32 limit");
    if (query_count == 0) return;
    if (!edge_offsets || !neighbor_indices_out)
        throw std::runtime_error("fixed_radius_adjacency_3d device output pointers must not be null when query_count is nonzero");

    std::call_once(g_frn3d_adjacency_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusAdjacency3DRtKernelSrc, "frn3d_adjacency_rt_kernel.cu");
        g_frn3d_adjacency_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__frn3d_adjacency_probe",
            "__miss__frn3d_adjacency_miss",
            "__intersection__frn3d_adjacency_isect",
            "__anyhit__frn3d_adjacency_anyhit",
            nullptr, 2).release();
    });

    std::vector<GpuPoint3DHost> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            static_cast<float>(query_points[i].z),
            query_points[i].id,
        };
    }

    if (!prepared->accel.handle || prepared->search_points.empty()) {
        return;
    }

    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);

    constexpr float kRadiusPad = 1.0e-4f;
    const float radius_f = static_cast<float>(radius);
    const float aabb_radius = static_cast<float>(prepared->max_radius) + kRadiusPad;

    FixedRadiusAdjacency3DRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = reinterpret_cast<const GpuPoint3DHost*>(d_queries.ptr);
    lp.search_points = reinterpret_cast<const GpuPoint3DHost*>(prepared->d_search->ptr);
    lp.edge_offsets = edge_offsets;
    lp.neighbor_indices_out = neighbor_indices_out;
    lp.neighbor_index_capacity = static_cast<uint64_t>(neighbor_index_capacity);
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.radius = radius_f;
    lp.trace_tmax = std::max(1.0e-6f, 2.0f * aabb_radius);

    DevPtr d_params(sizeof(FixedRadiusAdjacency3DRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn3d_adjacency_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusAdjacency3DRtLaunchParams),
                             &g_frn3d_adjacency_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();
    g_optix_last_copy_s = 0.0;
}

static void launch_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
        PreparedFixedRadiusCountThreshold3DRt* prepared,
        const GpuPoint3DHost* device_query_points,
        size_t query_count,
        size_t query_index_offset,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        bool same_root_culling,
        bool direct_side_effect,
        size_t item_count);

static void apply_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
        PreparedFixedRadiusCountThreshold3DRt* prepared,
        const RtdlPoint3D* query_points,
        size_t query_count,
        size_t query_index_offset,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        bool same_root_culling,
        bool direct_side_effect,
        size_t item_count)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius grouped-union 3D handle must not be null");
    if (!query_points && query_count != 0) throw std::runtime_error("query_points pointer must not be null when query_count is nonzero");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_grouped_union_3d radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_grouped_union_3d radius exceeds prepared max_radius");
    }
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_grouped_union_3d query_count exceeds uint32 limit");
    if (query_index_offset > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_grouped_union_3d query_index_offset exceeds uint32 limit");
    if (item_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_grouped_union_3d item_count exceeds uint32 limit");
    if (query_index_offset > item_count || query_count > item_count - query_index_offset)
        throw std::runtime_error("fixed_radius_grouped_union_3d query range must be inside item_count");
    if (item_count < prepared->search_points.size())
        throw std::runtime_error("fixed_radius_grouped_union_3d workspaces must cover every prepared search item");
    if (query_count == 0) return;
    if (!predicate_flags || !parent_out || !fallback_candidate_out)
        throw std::runtime_error("fixed_radius_grouped_union_3d device continuation pointers must not be null when query_count is nonzero");

    std::vector<GpuPoint3DHost> gpu_queries(query_count);
    for (size_t i = 0; i < query_count; ++i) {
        gpu_queries[i] = {
            static_cast<float>(query_points[i].x),
            static_cast<float>(query_points[i].y),
            static_cast<float>(query_points[i].z),
            query_points[i].id,
        };
    }

    if (!prepared->accel.handle || prepared->search_points.empty()) {
        return;
    }

    DevPtr d_queries(sizeof(GpuPoint3DHost) * query_count);
    upload(d_queries.ptr, gpu_queries.data(), query_count);

    launch_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
        prepared,
        reinterpret_cast<const GpuPoint3DHost*>(d_queries.ptr),
        query_count,
        query_index_offset,
        radius,
        predicate_flags,
        parent_out,
        fallback_candidate_out,
        telemetry_out,
        same_root_culling,
        direct_side_effect,
        item_count);
}

static void apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs_optix(
        PreparedFixedRadiusCountThreshold3DRt* prepared,
        size_t query_start,
        size_t query_count,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        bool same_root_culling,
        bool direct_side_effect,
        size_t item_count)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius grouped-union 3D handle must not be null");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_grouped_union_3d_self_range radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range radius exceeds prepared max_radius");
    }
    const size_t search_count = prepared->search_points.size();
    if (query_start > search_count || query_count > search_count - query_start)
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range query range must be inside prepared search items");
    if (query_start > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range query_start exceeds uint32 limit");
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range query_count exceeds uint32 limit");
    if (item_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range item_count exceeds uint32 limit");
    if (item_count < search_count)
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range workspaces must cover every prepared search item");
    if (query_count == 0) return;
    if (!parent_out)
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range parent pointer must not be null when query_count is nonzero");
    const bool all_predicate = predicate_flags == nullptr && fallback_candidate_out == nullptr;
    if (!all_predicate && (!predicate_flags || !fallback_candidate_out))
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range predicate and fallback pointers must both be null only for all-items mode");
    if (!prepared->d_search)
        throw std::runtime_error("fixed_radius_grouped_union_3d_self_range prepared search device buffer is missing");
    if (!prepared->accel.handle || prepared->search_points.empty()) {
        return;
    }

    const GpuPoint3DHost* device_search = reinterpret_cast<const GpuPoint3DHost*>(prepared->d_search->ptr);
    launch_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
        prepared,
        device_search + query_start,
        query_count,
        query_start,
        radius,
        predicate_flags,
        parent_out,
        fallback_candidate_out,
        telemetry_out,
        same_root_culling,
        direct_side_effect,
        item_count);
}

static void launch_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
        PreparedFixedRadiusCountThreshold3DRt* prepared,
        const GpuPoint3DHost* device_query_points,
        size_t query_count,
        size_t query_index_offset,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        bool same_root_culling,
        bool direct_side_effect,
        size_t item_count)
{
    std::call_once(g_frn3d_grouped_union_rt.init, [&]() {
        std::string ptx = compile_to_ptx(kFixedRadiusGroupedUnion3DRtKernelSrc, "frn3d_grouped_union_rt_kernel.cu");
        g_frn3d_grouped_union_rt.pipe = build_pipeline(
            get_optix_context(), ptx,
            "__raygen__frn3d_grouped_union_probe",
            "__miss__frn3d_grouped_union_miss",
            "__intersection__frn3d_grouped_union_isect",
            "__anyhit__frn3d_grouped_union_anyhit",
            nullptr, 1).release();
    });

    constexpr float kRadiusPad = 1.0e-4f;
    const float radius_f = static_cast<float>(radius);
    const float aabb_radius = static_cast<float>(prepared->max_radius) + kRadiusPad;

    FixedRadiusGroupedUnion3DRtLaunchParams lp;
    lp.traversable = prepared->accel.handle;
    lp.query_points = device_query_points;
    lp.search_points = reinterpret_cast<const GpuPoint3DHost*>(prepared->d_search->ptr);
    lp.predicate_flags = predicate_flags;
    lp.parent_out = parent_out;
    lp.fallback_candidate_out = fallback_candidate_out;
    lp.telemetry_out = telemetry_out;
    lp.query_count = static_cast<uint32_t>(query_count);
    lp.query_index_offset = static_cast<uint32_t>(query_index_offset);
    lp.item_count = static_cast<uint32_t>(item_count);
    lp.all_predicate = (predicate_flags == nullptr) ? 1u : 0u;
    lp.same_root_culling = same_root_culling ? 1u : 0u;
    lp.direct_side_effect = direct_side_effect ? 1u : 0u;
    lp.radius = radius_f;
    lp.trace_tmax = std::max(1.0e-6f, 2.0f * aabb_radius);

    DevPtr d_params(sizeof(FixedRadiusGroupedUnion3DRtLaunchParams));
    upload(d_params.ptr, &lp, 1);

    CUstream stream = 0;
    g_optix_last_bvh_build_s = 0.0;
    auto t_start_trav = std::chrono::steady_clock::now();
    OPTIX_CHECK(optixLaunch(g_frn3d_grouped_union_rt.pipe->pipeline, stream,
                             d_params.ptr, sizeof(FixedRadiusGroupedUnion3DRtLaunchParams),
                             &g_frn3d_grouped_union_rt.pipe->sbt,
                             static_cast<unsigned>(query_count), 1, 1));
    CU_CHECK(cuStreamSynchronize(stream));
    auto t_end_trav = std::chrono::steady_clock::now();
    g_optix_last_traversal_s = std::chrono::duration<double>(t_end_trav - t_start_trav).count();
    g_optix_last_copy_s = 0.0;
}

static void apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_optix(
        PreparedFixedRadiusCountThreshold3DRt* prepared,
        double radius,
        const uint32_t* predicate_flags,
        int32_t* parent_out,
        int32_t* fallback_candidate_out,
        uint64_t* telemetry_out,
        bool same_root_culling,
        bool direct_side_effect,
        size_t item_count)
{
    if (!prepared) throw std::runtime_error("prepared OptiX fixed-radius grouped-union 3D handle must not be null");
    if (radius < 0.0) throw std::runtime_error("fixed_radius_grouped_union_3d_self radius must be non-negative");
    if (radius > prepared->max_radius + 1.0e-7) {
        throw std::runtime_error("fixed_radius_grouped_union_3d_self radius exceeds prepared max_radius");
    }
    const size_t query_count = prepared->search_points.size();
    if (query_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_grouped_union_3d_self query_count exceeds uint32 limit");
    if (item_count > static_cast<size_t>(UINT32_MAX))
        throw std::runtime_error("fixed_radius_grouped_union_3d_self item_count exceeds uint32 limit");
    if (item_count < query_count)
        throw std::runtime_error("fixed_radius_grouped_union_3d_self workspaces must cover every prepared search item");
    if (query_count == 0) return;
    if (!parent_out)
        throw std::runtime_error("fixed_radius_grouped_union_3d_self parent pointer must not be null when query_count is nonzero");
    const bool all_predicate = predicate_flags == nullptr && fallback_candidate_out == nullptr;
    if (!all_predicate && (!predicate_flags || !fallback_candidate_out))
        throw std::runtime_error("fixed_radius_grouped_union_3d_self predicate and fallback pointers must both be null only for all-items mode");
    if (!prepared->d_search)
        throw std::runtime_error("fixed_radius_grouped_union_3d_self prepared search device buffer is missing");
    if (!prepared->accel.handle || prepared->search_points.empty()) {
        return;
    }

    launch_prepared_fixed_radius_grouped_union_3d_device_outputs_optix(
        prepared,
        reinterpret_cast<const GpuPoint3DHost*>(prepared->d_search->ptr),
        query_count,
        0,
        radius,
        predicate_flags,
        parent_out,
        fallback_candidate_out,
        telemetry_out,
        same_root_culling,
        direct_side_effect,
        item_count);
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
