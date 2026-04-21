#if defined(_WIN32)
#  define RTDL_EMBREE_EXPORT extern "C" __declspec(dllexport)
#else
#  define RTDL_EMBREE_EXPORT extern "C"
#endif

namespace {

constexpr size_t kDbMaxRowsPerJob = 1000000;
constexpr size_t kDbMaxCandidateRowsPerJob = 250000;
constexpr size_t kDbMaxGroupsPerJob = 65536;
std::atomic<size_t> g_embree_thread_override {0};

struct DbPrimaryAxis {
  size_t field_index;
  std::vector<double> sorted_values;
  int64_t encoded_lo;
  int64_t encoded_hi;
};

struct EmbreeDbDatasetImpl {
  std::vector<std::string> field_names;
  std::vector<RtdlDbField> fields;
  std::vector<std::string> scalar_strings;
  std::vector<RtdlDbScalar> row_values;
  size_t row_count;
  std::vector<DbPrimaryAxis> primary_axes;
  std::vector<DbRowBox> boxes;
  DbRowBoxSceneData scene_data;
  EmbreeDevice device;
  SceneHolder holder;

  EmbreeDbDatasetImpl() : row_count(0), scene_data {&boxes}, device(), holder(device.device) {}
};

size_t embree_hardware_threads() {
  const unsigned int detected = std::thread::hardware_concurrency();
  return std::max<size_t>(1, static_cast<size_t>(detected == 0 ? 1 : detected));
}

size_t parse_embree_env_threads() {
  const char* raw = std::getenv("RTDL_EMBREE_THREADS");
  if (raw == nullptr || raw[0] == '\0') {
    return embree_hardware_threads();
  }
  const std::string value(raw);
  if (value == "auto") {
    return embree_hardware_threads();
  }
  char* end = nullptr;
  const unsigned long long parsed = std::strtoull(raw, &end, 10);
  if (end == raw || *end != '\0' || parsed == 0) {
    throw std::runtime_error("RTDL_EMBREE_THREADS must be a positive integer or 'auto'");
  }
  return static_cast<size_t>(parsed);
}

size_t embree_dispatch_thread_count(size_t work_count) {
  if (work_count == 0) {
    return 0;
  }
  const size_t override_threads = g_embree_thread_override.load();
  const size_t requested = override_threads == 0 ? parse_embree_env_threads() : override_threads;
  return std::max<size_t>(1, std::min(requested, work_count));
}

template <typename Row, typename WorkerFn>
std::vector<Row> run_query_ranges(size_t query_count, WorkerFn worker_fn) {
  const size_t worker_count = embree_dispatch_thread_count(query_count);
  if (worker_count == 0) {
    return {};
  }
  std::vector<std::vector<Row>> worker_rows(worker_count);
  if (worker_count == 1) {
    worker_fn(0, query_count, worker_rows[0]);
    return worker_rows[0];
  }

  std::vector<std::thread> workers;
  std::vector<std::exception_ptr> exceptions(worker_count);
  workers.reserve(worker_count);
  const size_t chunk = (query_count + worker_count - 1) / worker_count;
  for (size_t worker_index = 0; worker_index < worker_count; ++worker_index) {
    const size_t begin = worker_index * chunk;
    const size_t end = std::min(query_count, begin + chunk);
    workers.emplace_back([&, worker_index, begin, end]() {
      try {
        worker_fn(begin, end, worker_rows[worker_index]);
      } catch (...) {
        exceptions[worker_index] = std::current_exception();
      }
    });
  }
  for (std::thread& worker : workers) {
    worker.join();
  }
  for (const std::exception_ptr& exception : exceptions) {
    if (exception) {
      std::rethrow_exception(exception);
    }
  }

  size_t total_rows = 0;
  for (const auto& local_rows : worker_rows) {
    total_rows += local_rows.size();
  }
  std::vector<Row> rows;
  rows.reserve(total_rows);
  for (const auto& local_rows : worker_rows) {
    rows.insert(rows.end(), local_rows.begin(), local_rows.end());
  }
  return rows;
}

template <typename WorkerFn>
void run_query_index_ranges(size_t query_count, WorkerFn worker_fn) {
  const size_t worker_count = embree_dispatch_thread_count(query_count);
  if (worker_count == 0) {
    return;
  }
  if (worker_count == 1) {
    worker_fn(0, query_count);
    return;
  }

  std::vector<std::thread> workers;
  std::vector<std::exception_ptr> exceptions(worker_count);
  workers.reserve(worker_count);
  const size_t chunk = (query_count + worker_count - 1) / worker_count;
  for (size_t worker_index = 0; worker_index < worker_count; ++worker_index) {
    const size_t begin = worker_index * chunk;
    const size_t end = std::min(query_count, begin + chunk);
    workers.emplace_back([&, worker_index, begin, end]() {
      try {
        worker_fn(begin, end);
      } catch (...) {
        exceptions[worker_index] = std::current_exception();
      }
    });
  }
  for (std::thread& worker : workers) {
    worker.join();
  }
  for (const std::exception_ptr& exception : exceptions) {
    if (exception) {
      std::rethrow_exception(exception);
    }
  }
}

size_t db_find_field_index_or_throw(const RtdlDbField* fields, size_t field_count, const char* name) {
  return db_find_field_index(fields, field_count, name);
}

bool db_field_kind_is_numeric(uint32_t kind) {
  return kind == kDbKindInt64 || kind == kDbKindFloat64 || kind == kDbKindBool;
}

std::vector<double> db_sorted_distinct_numeric_values(
    const RtdlDbScalar* row_values,
    size_t row_count,
    size_t field_count,
    size_t field_index) {
  std::vector<double> values;
  values.reserve(row_count);
  for (size_t row_index = 0; row_index < row_count; ++row_index) {
    const RtdlDbScalar& value = db_row_value(row_values, row_index, field_count, field_index);
    if (!db_scalar_is_numeric(value)) {
      throw std::runtime_error("first-wave Embree DB lowering requires numeric primary scan clauses");
    }
    values.push_back(db_scalar_as_double(value));
  }
  std::sort(values.begin(), values.end());
  values.erase(std::unique(values.begin(), values.end()), values.end());
  return values;
}

bool db_clause_matches_numeric_value(const RtdlDbClause& clause, double value) {
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

DbPrimaryAxis db_make_full_primary_axis(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const char* field_name) {
  const size_t field_index = db_find_field_index_or_throw(fields, field_count, field_name);
  if (!db_field_kind_is_numeric(fields[field_index].kind)) {
    throw std::runtime_error("first-wave Embree prepared DB datasets require numeric primary RT axes");
  }
  const std::vector<double> sorted_values =
      db_sorted_distinct_numeric_values(row_values, row_count, field_count, field_index);
  return {
      field_index,
      sorted_values,
      1,
      sorted_values.empty() ? 0 : static_cast<int64_t>(sorted_values.size())};
}

DbPrimaryAxis db_make_primary_axis(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause& clause) {
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

DbPrimaryAxis db_axis_with_clause_range(const DbPrimaryAxis& axis, const RtdlDbClause& clause) {
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

int64_t db_encode_axis_value(const DbPrimaryAxis& axis, const RtdlDbScalar& value) {
  const double needle = db_scalar_as_double(value);
  const auto it = std::lower_bound(axis.sorted_values.begin(), axis.sorted_values.end(), needle);
  if (it == axis.sorted_values.end() || *it != needle) {
    throw std::runtime_error("failed to encode DB primary-axis value");
  }
  return static_cast<int64_t>(std::distance(axis.sorted_values.begin(), it) + 1);
}

std::vector<DbRowBox> db_build_row_boxes(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const std::vector<DbPrimaryAxis>& axes) {
  const size_t row_id_index = db_find_field_index_or_throw(fields, field_count, "row_id");
  std::vector<DbRowBox> boxes;
  boxes.reserve(row_count);
  for (size_t row_index = 0; row_index < row_count; ++row_index) {
    const RtdlDbScalar& row_id_value = db_row_value(row_values, row_index, field_count, row_id_index);
    const double x = axes.size() >= 1
        ? static_cast<double>(db_encode_axis_value(axes[0], db_row_value(row_values, row_index, field_count, axes[0].field_index)))
        : 1.0;
    const double y = axes.size() >= 2
        ? static_cast<double>(db_encode_axis_value(axes[1], db_row_value(row_values, row_index, field_count, axes[1].field_index)))
        : 1.0;
    const double z = axes.size() >= 3
        ? static_cast<double>(db_encode_axis_value(axes[2], db_row_value(row_values, row_index, field_count, axes[2].field_index)))
        : 1.0;
    boxes.push_back({row_index, static_cast<uint32_t>(row_id_value.int_value), x, y, z});
  }
  return boxes;
}

std::vector<DbPrimaryAxis> db_dataset_query_axes(
    const EmbreeDbDatasetImpl& dataset,
    const RtdlDbClause* clauses,
    size_t clause_count) {
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

template <typename LaunchFn>
void db_launch_primary_matrix_rays(
    const std::vector<DbPrimaryAxis>& axes,
    LaunchFn&& launch_fn) {
  const int64_t x_lo = axes.size() >= 1 ? axes[0].encoded_lo : 1;
  const int64_t x_hi = axes.size() >= 1 ? axes[0].encoded_hi : 1;
  const int64_t y_lo = axes.size() >= 2 ? axes[1].encoded_lo : 1;
  const int64_t y_hi = axes.size() >= 2 ? axes[1].encoded_hi : 1;
  const int64_t z_lo = axes.size() >= 3 ? axes[2].encoded_lo : 1;
  const int64_t z_hi = axes.size() >= 3 ? axes[2].encoded_hi : 1;
  if (x_lo > x_hi || y_lo > y_hi || z_lo > z_hi) {
    return;
  }
  for (int64_t x = x_lo; x <= x_hi; ++x) {
    for (int64_t y = y_lo; y <= y_hi; ++y) {
      launch_fn(x, y, z_lo, z_hi);
    }
  }
}

void db_throw_if_row_count_exceeds_limit(size_t row_count) {
  if (row_count > kDbMaxRowsPerJob) {
    throw std::runtime_error("first-wave Embree DB lowering supports at most 1000000 rows per RT job");
  }
}

void db_throw_if_limit_error() {
  if (!g_db_limit_error) {
    return;
  }
  const std::string message = g_db_limit_error_message;
  db_clear_limit_error();
  throw std::runtime_error(message);
}

void db_validate_db_inputs(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const RtdlDbClause* clauses,
    size_t clause_count) {
  if (field_count == 0 || fields == nullptr || row_values == nullptr) {
    throw std::runtime_error("DB table inputs must not be null");
  }
  if (clause_count > 0 && clauses == nullptr) {
    throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
  }
  db_throw_if_row_count_exceeds_limit(row_count);
}

std::vector<const char*> db_default_primary_fields(const RtdlDbField* fields, size_t field_count) {
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

size_t db_count_scalar_strings(const RtdlDbScalar* row_values, size_t scalar_count) {
  size_t count = 0;
  for (size_t index = 0; index < scalar_count; ++index) {
    if (row_values[index].kind == kDbKindText && row_values[index].string_value != nullptr) {
      ++count;
    }
  }
  return count;
}

void db_copy_dataset_table(
    EmbreeDbDatasetImpl& dataset,
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count) {
  dataset.field_names.reserve(field_count);
  for (size_t index = 0; index < field_count; ++index) {
    dataset.field_names.emplace_back(fields[index].name == nullptr ? "" : fields[index].name);
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
    if (copied.kind == kDbKindText && copied.string_value != nullptr) {
      dataset.scalar_strings.emplace_back(copied.string_value);
      copied.string_value = dataset.scalar_strings.back().c_str();
    }
    dataset.row_values.push_back(copied);
  }
  dataset.row_count = row_count;
}

void db_validate_columnar_inputs(
    const RtdlDbColumn* columns,
    size_t column_count,
    size_t row_count) {
  if (column_count == 0 || columns == nullptr) {
    throw std::runtime_error("DB columnar inputs must not be null");
  }
  db_throw_if_row_count_exceeds_limit(row_count);
  for (size_t column_index = 0; column_index < column_count; ++column_index) {
    const RtdlDbColumn& column = columns[column_index];
    if (column.name == nullptr) {
      throw std::runtime_error("DB column name must not be null");
    }
    if ((column.kind == kDbKindInt64 || column.kind == kDbKindBool) && column.int_values == nullptr) {
      throw std::runtime_error("DB integer/bool column values must not be null");
    }
    if (column.kind == kDbKindFloat64 && column.double_values == nullptr) {
      throw std::runtime_error("DB float column values must not be null");
    }
    if (column.kind == kDbKindText && column.string_values == nullptr) {
      throw std::runtime_error("DB text column values must not be null");
    }
  }
}

void db_copy_dataset_columnar_table(
    EmbreeDbDatasetImpl& dataset,
    const RtdlDbColumn* columns,
    size_t column_count,
    size_t row_count) {
  dataset.field_names.reserve(column_count);
  for (size_t column_index = 0; column_index < column_count; ++column_index) {
    dataset.field_names.emplace_back(columns[column_index].name == nullptr ? "" : columns[column_index].name);
  }
  dataset.fields.reserve(column_count);
  for (size_t column_index = 0; column_index < column_count; ++column_index) {
    dataset.fields.push_back({dataset.field_names[column_index].c_str(), columns[column_index].kind});
  }

  size_t string_count = 0;
  for (size_t column_index = 0; column_index < column_count; ++column_index) {
    if (columns[column_index].kind == kDbKindText) {
      string_count += row_count;
    }
  }
  dataset.scalar_strings.reserve(string_count);
  dataset.row_values.reserve(row_count * column_count);
  for (size_t row_index = 0; row_index < row_count; ++row_index) {
    for (size_t column_index = 0; column_index < column_count; ++column_index) {
      const RtdlDbColumn& column = columns[column_index];
      RtdlDbScalar value{};
      value.kind = column.kind;
      if (column.kind == kDbKindFloat64) {
        value.double_value = column.double_values[row_index];
      } else if (column.kind == kDbKindText) {
        const char* text = column.string_values[row_index];
        dataset.scalar_strings.emplace_back(text == nullptr ? "" : text);
        value.string_value = dataset.scalar_strings.back().c_str();
      } else {
        value.int_value = column.int_values[row_index];
      }
      dataset.row_values.push_back(value);
    }
  }
  dataset.row_count = row_count;
}

void db_attach_dataset_scene(EmbreeDbDatasetImpl& dataset) {
  dataset.holder.geometry = rtcNewGeometry(dataset.device.device, RTC_GEOMETRY_TYPE_USER);
  rtcSetGeometryUserPrimitiveCount(dataset.holder.geometry, static_cast<unsigned>(dataset.boxes.size()));
  rtcSetGeometryUserData(dataset.holder.geometry, &dataset.scene_data);
  rtcSetGeometryBoundsFunction(dataset.holder.geometry, db_row_box_bounds, nullptr);
  rtcSetGeometryIntersectFunction(dataset.holder.geometry, db_row_box_intersect);
  rtcCommitGeometry(dataset.holder.geometry);
  rtcAttachGeometry(dataset.holder.scene, dataset.holder.geometry);
  rtcCommitScene(dataset.holder.scene);
}

template <typename LaunchFn>
void db_run_dataset_rays(const EmbreeDbDatasetImpl& dataset, const std::vector<DbPrimaryAxis>& axes, LaunchFn&& launch_fn) {
  db_clear_limit_error();
  db_launch_primary_matrix_rays(axes, [&](int64_t x, int64_t y, int64_t z_lo, int64_t z_hi) {
    RTCRayHit rayhit;
    set_ray_3d(
        &rayhit,
        {static_cast<double>(x), static_cast<double>(y), static_cast<double>(z_lo) - 1.0},
        {0.0, 0.0, 1.0},
        static_cast<float>((z_hi - z_lo) + 2));
    RTCIntersectArguments args;
    rtcInitIntersectArguments(&args);
    launch_fn(rayhit, args);
    db_throw_if_limit_error();
  });
}

}  // namespace

RTDL_EMBREE_EXPORT int rtdl_embree_get_version(int* major_out, int* minor_out, int* patch_out) {
  if (major_out == nullptr || minor_out == nullptr || patch_out == nullptr) {
    return 1;
  }
  *major_out = RTC_VERSION_MAJOR;
  *minor_out = RTC_VERSION_MINOR;
  *patch_out = RTC_VERSION_PATCH;
  return 0;
}

RTDL_EMBREE_EXPORT void rtdl_embree_configure_threads(size_t thread_count) {
  g_embree_thread_override.store(thread_count);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_lsi(
    const RtdlSegment* left,
    size_t left_count,
    const RtdlSegment* right,
    size_t right_count,
    RtdlLsiRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Segment2D> left_segments;
    std::vector<Segment2D> right_segments;
    left_segments.reserve(left_count);
    right_segments.reserve(right_count);
    for (size_t i = 0; i < left_count; ++i) {
      left_segments.push_back({left[i].id, {left[i].x0, left[i].y0}, {left[i].x1, left[i].y1}});
    }
    for (size_t i = 0; i < right_count; ++i) {
      right_segments.push_back({right[i].id, {right[i].x0, right[i].y0}, {right[i].x1, right[i].y1}});
    }

    std::vector<RtdlLsiRow> rows = lsi_native_loop(left_segments, right_segments);
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_pip(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const double* vertices_xy,
    size_t vertex_xy_count,
    uint32_t positive_only,
    RtdlPipRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point2D> point_values;
    point_values.reserve(point_count);
    for (size_t i = 0; i < point_count; ++i) {
      point_values.push_back({points[i].id, {points[i].x, points[i].y}});
    }
    std::vector<Polygon2D> polygon_values = decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count);

    std::vector<RtdlPipRow> rows;
    if (positive_only != 0u) {
      EmbreeDevice device;
      PolygonSceneData data {&polygon_values};
      SceneHolder holder(device.device);
      holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
      rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(polygon_values.size()));
      rtcSetGeometryUserData(holder.geometry, &data);
      rtcSetGeometryBoundsFunction(holder.geometry, polygon_bounds, nullptr);
      rtcSetGeometryIntersectFunction(holder.geometry, polygon_intersect);
      rtcSetGeometryIntersectFilterFunction(holder.geometry, polygon_intersect_filter);
      rtcCommitGeometry(holder.geometry);
      rtcAttachGeometry(holder.scene, holder.geometry);
      rtcCommitScene(holder.scene);

#if RTDL_EMBREE_HAS_GEOS
      GeosPreparedPolygonSet geos(polygon_values);
#endif
      for (const Point2D& point : point_values) {
        std::unordered_set<uint32_t> candidate_polygon_indices;
        PipQueryState state {&point, &candidate_polygon_indices};
        RTCPointQuery query;
        query.x = static_cast<float>(point.p.x);
        query.y = static_cast<float>(point.p.y);
        query.z = 0.0f;
        query.time = 0.0f;
        query.radius = 0.0f;
        RTCPointQueryContext context;
        rtcInitPointQueryContext(&context);
        rtcPointQuery(holder.scene, &query, &context, polygon_point_query_collect, &state);
        if (candidate_polygon_indices.empty()) {
          continue;
        }
        std::vector<uint32_t> candidate_indices;
        candidate_indices.reserve(candidate_polygon_indices.size());
        for (uint32_t polygon_index : candidate_polygon_indices) {
          candidate_indices.push_back(polygon_index);
        }
        std::sort(candidate_indices.begin(), candidate_indices.end());
        for (uint32_t polygon_index : candidate_indices) {
#if RTDL_EMBREE_HAS_GEOS
          const bool contains = geos.covers(polygon_index, point.p.x, point.p.y);
#else
          const bool contains = point_in_polygon(point, polygon_values[polygon_index]);
#endif
          if (!contains) {
            continue;
          }
          rows.push_back({point.id, polygon_values[polygon_index].id, 1u});
        }
      }
    } else {
      rows.reserve(point_values.size() * polygon_values.size());
#if RTDL_EMBREE_HAS_GEOS
      GeosPreparedPolygonSet geos(polygon_values);
      for (const Point2D& point : point_values) {
        for (size_t polygon_index = 0; polygon_index < polygon_values.size(); ++polygon_index) {
          const bool contains = geos.covers(polygon_index, point.p.x, point.p.y);
          rows.push_back({point.id, polygon_values[polygon_index].id, contains ? 1u : 0u});
        }
      }
#else
      for (const Point2D& point : point_values) {
        for (const Polygon2D& polygon : polygon_values) {
          const bool contains = point_in_polygon(point, polygon);
          rows.push_back({point.id, polygon.id, contains ? 1u : 0u});
        }
      }
#endif
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_overlay(
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
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Polygon2D> left_values = decode_polygons(left_polygons, left_count, left_vertices_xy, left_vertex_xy_count);
    std::vector<Polygon2D> right_values = decode_polygons(right_polygons, right_count, right_vertices_xy, right_vertex_xy_count);

    EmbreeDevice device;
    PolygonSceneData data {&right_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(right_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, polygon_bounds, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, polygon_intersect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlOverlayRow> rows;
    rows.reserve(left_values.size() * right_values.size());
    for (const Polygon2D& left_polygon : left_values) {
      std::unordered_map<uint32_t, OverlayPairFlags> flags_by_right_id;
      OverlayQueryState state {&left_polygon, &flags_by_right_id};
      g_query_kind = QueryKind::kOverlay;
      g_query_state = &state;
      for (size_t i = 0; i < left_polygon.vertices.size(); ++i) {
        Vec2 start = left_polygon.vertices[i];
        Vec2 end = left_polygon.vertices[(i + 1) % left_polygon.vertices.size()];
        Vec2 dir = sub(end, start);
        RTCRayHit rayhit;
        set_ray(&rayhit, start, dir, 1.0f);
        RTCIntersectArguments args;
        rtcInitIntersectArguments(&args);
        rtcIntersect1(holder.scene, &rayhit, &args);
      }
      for (const Polygon2D& right_polygon : right_values) {
        OverlayPairFlags flags = flags_by_right_id[right_polygon.id];
        rows.push_back({left_polygon.id, right_polygon.id, flags.requires_lsi, flags.requires_pip});
      }
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_ray_hitcount(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<RayQuery2D> ray_values;
    std::vector<Triangle2D> triangle_values;
    ray_values.reserve(ray_count);
    triangle_values.reserve(triangle_count);
    for (size_t i = 0; i < ray_count; ++i) {
      ray_values.push_back({rays[i].id, {rays[i].ox, rays[i].oy}, {rays[i].dx, rays[i].dy}, rays[i].tmax});
    }
    for (size_t i = 0; i < triangle_count; ++i) {
      triangle_values.push_back({triangles[i].id, {triangles[i].x0, triangles[i].y0}, {triangles[i].x1, triangles[i].y1}, {triangles[i].x2, triangles[i].y2}});
    }

    EmbreeDevice device;
    TriangleSceneData data {&triangle_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(triangle_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, triangle_bounds, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, triangle_intersect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlRayHitCountRow> rows;
    rows.reserve(ray_values.size());
    for (const RayQuery2D& ray : ray_values) {
      uint32_t hit_count = 0;
      std::unordered_set<uint32_t> seen_triangle_ids;
      RayHitCountState state {&ray, &hit_count, &seen_triangle_ids};
      g_query_kind = QueryKind::kRayHitCount;
      g_query_state = &state;
      RTCRayHit rayhit;
      set_ray(&rayhit, ray.o, ray.d, ray.tmax);
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      rtcIntersect1(holder.scene, &rayhit, &args);
      rows.push_back({ray.id, hit_count});
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_ray_hitcount_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayHitCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<RayQuery3D> ray_values;
    std::vector<Triangle3D> triangle_values;
    ray_values.reserve(ray_count);
    triangle_values.reserve(triangle_count);
    for (size_t i = 0; i < ray_count; ++i) {
      ray_values.push_back({rays[i].id, {rays[i].ox, rays[i].oy, rays[i].oz}, {rays[i].dx, rays[i].dy, rays[i].dz}, rays[i].tmax});
    }
    for (size_t i = 0; i < triangle_count; ++i) {
      triangle_values.push_back({
          triangles[i].id,
          {triangles[i].x0, triangles[i].y0, triangles[i].z0},
          {triangles[i].x1, triangles[i].y1, triangles[i].z1},
          {triangles[i].x2, triangles[i].y2, triangles[i].z2},
      });
    }

    EmbreeDevice device;
    TriangleSceneData3D data {&triangle_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(triangle_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, triangle_bounds_3d, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, triangle_intersect_3d);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlRayHitCountRow> rows;
    rows.reserve(ray_values.size());
    for (const RayQuery3D& ray : ray_values) {
      uint32_t hit_count = 0;
      std::unordered_set<uint32_t> seen_triangle_ids;
      RayHitCountState3D state {&ray, &hit_count, &seen_triangle_ids};
      g_query_kind = QueryKind::kRayHitCount;
      g_query_state = &state;
      RTCRayHit rayhit;
      set_ray_3d(&rayhit, ray.o, ray.d, ray.tmax);
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      rtcIntersect1(holder.scene, &rayhit, &args);
      rows.push_back({ray.id, hit_count});
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_ray_anyhit(
    const RtdlRay2D* rays,
    size_t ray_count,
    const RtdlTriangle* triangles,
    size_t triangle_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<RayQuery2D> ray_values;
    std::vector<Triangle2D> triangle_values;
    ray_values.reserve(ray_count);
    triangle_values.reserve(triangle_count);
    for (size_t i = 0; i < ray_count; ++i) {
      ray_values.push_back({rays[i].id, {rays[i].ox, rays[i].oy}, {rays[i].dx, rays[i].dy}, rays[i].tmax});
    }
    for (size_t i = 0; i < triangle_count; ++i) {
      triangle_values.push_back({triangles[i].id, {triangles[i].x0, triangles[i].y0}, {triangles[i].x1, triangles[i].y1}, {triangles[i].x2, triangles[i].y2}});
    }

    EmbreeDevice device;
    TriangleSceneData data {&triangle_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(triangle_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, triangle_bounds, nullptr);
    rtcSetGeometryOccludedFunction(holder.geometry, triangle_occluded);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlRayAnyHitRow> rows;
    rows.reserve(ray_values.size());
    for (const RayQuery2D& ray : ray_values) {
      uint32_t any_hit = 0u;
      RayAnyHitState state {&ray, &any_hit};
      g_query_kind = QueryKind::kRayAnyHit;
      g_query_state = &state;
      RTCRay embree_ray;
      set_ray_occluded(&embree_ray, ray.o, ray.d, ray.tmax);
      RTCOccludedArguments args;
      rtcInitOccludedArguments(&args);
      rtcOccluded1(holder.scene, &embree_ray, &args);
      rows.push_back({ray.id, any_hit});
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_ray_anyhit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayAnyHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<RayQuery3D> ray_values;
    std::vector<Triangle3D> triangle_values;
    ray_values.reserve(ray_count);
    triangle_values.reserve(triangle_count);
    for (size_t i = 0; i < ray_count; ++i) {
      ray_values.push_back({rays[i].id, {rays[i].ox, rays[i].oy, rays[i].oz}, {rays[i].dx, rays[i].dy, rays[i].dz}, rays[i].tmax});
    }
    for (size_t i = 0; i < triangle_count; ++i) {
      triangle_values.push_back({
          triangles[i].id,
          {triangles[i].x0, triangles[i].y0, triangles[i].z0},
          {triangles[i].x1, triangles[i].y1, triangles[i].z1},
          {triangles[i].x2, triangles[i].y2, triangles[i].z2},
      });
    }

    EmbreeDevice device;
    TriangleSceneData3D data {&triangle_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(triangle_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, triangle_bounds_3d, nullptr);
    rtcSetGeometryOccludedFunction(holder.geometry, triangle_occluded_3d);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlRayAnyHitRow> rows;
    rows.reserve(ray_values.size());
    for (const RayQuery3D& ray : ray_values) {
      uint32_t any_hit = 0u;
      RayAnyHitState3D state {&ray, &any_hit};
      g_query_kind = QueryKind::kRayAnyHit;
      g_query_state = &state;
      RTCRay embree_ray;
      set_ray_occluded_3d(&embree_ray, ray.o, ray.d, ray.tmax);
      RTCOccludedArguments args;
      rtcInitOccludedArguments(&args);
      rtcOccluded1(holder.scene, &embree_ray, &args);
      rows.push_back({ray.id, any_hit});
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_ray_closest_hit_3d(
    const RtdlRay3D* rays,
    size_t ray_count,
    const RtdlTriangle3D* triangles,
    size_t triangle_count,
    RtdlRayClosestHitRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<RayQuery3D> ray_values;
    std::vector<Triangle3D> triangle_values;
    ray_values.reserve(ray_count);
    triangle_values.reserve(triangle_count);
    for (size_t i = 0; i < ray_count; ++i) {
      ray_values.push_back({rays[i].id, {rays[i].ox, rays[i].oy, rays[i].oz}, {rays[i].dx, rays[i].dy, rays[i].dz}, rays[i].tmax});
    }
    for (size_t i = 0; i < triangle_count; ++i) {
      triangle_values.push_back({
          triangles[i].id,
          {triangles[i].x0, triangles[i].y0, triangles[i].z0},
          {triangles[i].x1, triangles[i].y1, triangles[i].z1},
          {triangles[i].x2, triangles[i].y2, triangles[i].z2},
      });
    }

    EmbreeDevice device;
    TriangleSceneData3D data {&triangle_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(triangle_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, triangle_bounds_3d, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, triangle_intersect_3d);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlRayClosestHitRow> rows;
    rows.reserve(ray_values.size());
    for (const RayQuery3D& ray : ray_values) {
      uint32_t best_triangle_id = 0;
      double best_t = 0.0;
      bool has_hit = false;
      std::unordered_set<uint32_t> seen_triangle_ids;
      RayClosestHitState3D state {&ray, &best_triangle_id, &best_t, &has_hit, &seen_triangle_ids};
      g_query_kind = QueryKind::kRayClosestHit;
      g_query_state = &state;
      RTCRayHit rayhit;
      set_ray_3d(&rayhit, ray.o, ray.d, ray.tmax);
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      rtcIntersect1(holder.scene, &rayhit, &args);
      if (has_hit) {
        rows.push_back({ray.id, best_triangle_id, best_t});
      }
    }
    g_query_kind = QueryKind::kNone;
    g_query_state = nullptr;

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_segment_polygon_hitcount(
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
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Segment2D> segment_values;
    segment_values.reserve(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
      segment_values.push_back({segments[i].id, {segments[i].x0, segments[i].y0}, {segments[i].x1, segments[i].y1}});
    }
    std::vector<Polygon2D> polygon_values = decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count);
    std::vector<Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_values.size());
    for (const Polygon2D& polygon : polygon_values) {
      polygon_bounds.push_back(bounds_for_polygon(polygon));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_values.size(), 0);
    size_t stamp = 1;

    std::vector<RtdlSegmentPolygonHitCountRow> rows;
    rows.reserve(segment_values.size());
    for (const Segment2D& segment : segment_values) {
      const Bounds2D seg_bounds = bounds_for_segment(segment);
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
          const Polygon2D& polygon = polygon_values[polygon_index];
          if (segment_hits_polygon(segment, polygon)) {
            hit_count += 1;
          }
        }
      }
      rows.push_back({segment.id, hit_count});
      stamp += 1;
      if (stamp == 0) {
        std::fill(seen.begin(), seen.end(), 0);
        stamp = 1;
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_segment_polygon_anyhit_rows(
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
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Segment2D> segment_values;
    segment_values.reserve(segment_count);
    for (size_t i = 0; i < segment_count; ++i) {
      segment_values.push_back({segments[i].id, {segments[i].x0, segments[i].y0}, {segments[i].x1, segments[i].y1}});
    }
    std::vector<Polygon2D> polygon_values = decode_polygons(polygons, polygon_count, vertices_xy, vertex_xy_count);
    std::vector<Bounds2D> polygon_bounds;
    polygon_bounds.reserve(polygon_values.size());
    for (const Polygon2D& polygon : polygon_values) {
      polygon_bounds.push_back(bounds_for_polygon(polygon));
    }
    const PolygonBucketIndex bucket_index = build_polygon_bucket_index(polygon_bounds);
    std::vector<size_t> seen(polygon_values.size(), 0);
    size_t stamp = 1;
    std::vector<RtdlSegmentPolygonAnyHitRow> rows;
    for (const Segment2D& segment : segment_values) {
      const Bounds2D seg_bounds = bounds_for_segment(segment);
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
          const Polygon2D& polygon = polygon_values[polygon_index];
          if (segment_hits_polygon(segment, polygon)) {
            rows.push_back({segment.id, polygon.id});
          }
        }
      }
      stamp += 1;
      if (stamp == 0) {
        std::fill(seen.begin(), seen.end(), 0);
        stamp = 1;
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_point_nearest_segment(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlSegment* segments,
    size_t segment_count,
    RtdlPointNearestSegmentRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point2D> point_values;
    std::vector<Segment2D> segment_values;
    point_values.reserve(point_count);
    segment_values.reserve(segment_count);
    for (size_t i = 0; i < point_count; ++i) {
      point_values.push_back({points[i].id, {points[i].x, points[i].y}});
    }
    for (size_t i = 0; i < segment_count; ++i) {
      segment_values.push_back({segments[i].id, {segments[i].x0, segments[i].y0}, {segments[i].x1, segments[i].y1}});
    }

    std::vector<RtdlPointNearestSegmentRow> rows;
    rows.reserve(point_values.size());
    for (const Point2D& point : point_values) {
      const Segment2D* best_segment = nullptr;
      float best_distance = 0.0f;
      for (const Segment2D& segment : segment_values) {
        float distance = point_segment_distance(point, segment);
        if (best_segment == nullptr ||
            distance < best_distance - kEps ||
            (std::fabs(distance - best_distance) <= kEps && segment.id < best_segment->id)) {
          best_segment = &segment;
          best_distance = distance;
        }
      }
      if (best_segment == nullptr) {
        continue;
      }
      rows.push_back({point.id, best_segment->id, best_distance});
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_fixed_radius_neighbors(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    size_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (radius < 0.0) {
      throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (k_max == 0) {
      throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point2D> query_values;
    std::vector<Point2D> search_values;
    query_values.reserve(query_count);
    search_values.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
      query_values.push_back({query_points[i].id, {query_points[i].x, query_points[i].y}});
    }
    for (size_t i = 0; i < search_count; ++i) {
      search_values.push_back({search_points[i].id, {search_points[i].x, search_points[i].y}});
    }

    EmbreeDevice device;
    PointSceneData data {&search_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(search_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, point_bounds, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    std::vector<RtdlFixedRadiusNeighborRow> rows = run_query_ranges<RtdlFixedRadiusNeighborRow>(
        query_values.size(),
        [&](size_t begin, size_t end, std::vector<RtdlFixedRadiusNeighborRow>& local_rows) {
      for (size_t query_index = begin; query_index < end; ++query_index) {
        const Point2D& query = query_values[query_index];
        std::vector<RtdlFixedRadiusNeighborRow> query_rows;
        std::unordered_set<uint32_t> seen_neighbor_ids;
        FixedRadiusNeighborsQueryState state {&query, &search_values, radius, &query_rows, &seen_neighbor_ids};
        RTCPointQuery point_query;
        point_query.x = static_cast<float>(query.p.x);
        point_query.y = static_cast<float>(query.p.y);
        point_query.z = 0.0f;
        point_query.time = 0.0f;
        point_query.radius = static_cast<float>(radius + kFixedRadiusCandidateEps);
        RTCPointQueryContext context;
        rtcInitPointQueryContext(&context);
        g_query_kind = QueryKind::kFixedRadiusNeighbors;
        rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect, &state);
        g_query_kind = QueryKind::kNone;
        std::sort(query_rows.begin(), query_rows.end(), [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
          if (left.distance < right.distance - 1.0e-12) {
            return true;
          }
          if (right.distance < left.distance - 1.0e-12) {
            return false;
          }
          return left.neighbor_id < right.neighbor_id;
        });
        if (query_rows.size() > k_max) {
          query_rows.resize(k_max);
        }
        local_rows.insert(local_rows.end(), query_rows.begin(), query_rows.end());
      }
    });
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
      return left.query_id < right.query_id;
    });

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_fixed_radius_neighbors_3d(
    const RtdlPoint3D* query_points,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    double radius,
    size_t k_max,
    RtdlFixedRadiusNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (radius < 0.0) {
      throw std::runtime_error("fixed_radius_neighbors radius must be non-negative");
    }
    if (k_max == 0) {
      throw std::runtime_error("fixed_radius_neighbors k_max must be positive");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point3D> query_values;
    std::vector<Point3D> search_values;
    query_values.reserve(query_count);
    search_values.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
      query_values.push_back({query_points[i].id, {query_points[i].x, query_points[i].y, query_points[i].z}});
    }
    for (size_t i = 0; i < search_count; ++i) {
      search_values.push_back({search_points[i].id, {search_points[i].x, search_points[i].y, search_points[i].z}});
    }

    EmbreeDevice device;
    PointSceneData3D data {&search_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(search_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, point_bounds_3d, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect_3d);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    std::vector<RtdlFixedRadiusNeighborRow> rows = run_query_ranges<RtdlFixedRadiusNeighborRow>(
        query_values.size(),
        [&](size_t begin, size_t end, std::vector<RtdlFixedRadiusNeighborRow>& local_rows) {
      for (size_t query_index = begin; query_index < end; ++query_index) {
        const Point3D& query = query_values[query_index];
        std::vector<RtdlFixedRadiusNeighborRow> query_rows;
        std::unordered_set<uint32_t> seen_neighbor_ids;
        FixedRadiusNeighborsQueryState3D state {&query, &search_values, radius, &query_rows, &seen_neighbor_ids};
        RTCPointQuery point_query;
        point_query.x = static_cast<float>(query.p.x);
        point_query.y = static_cast<float>(query.p.y);
        point_query.z = static_cast<float>(query.p.z);
        point_query.time = 0.0f;
        point_query.radius = static_cast<float>(radius + kFixedRadiusCandidateEps);
        RTCPointQueryContext context;
        rtcInitPointQueryContext(&context);
        g_query_kind = QueryKind::kFixedRadiusNeighbors3D;
        rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect_3d, &state);
        g_query_kind = QueryKind::kNone;
        std::sort(query_rows.begin(), query_rows.end(), [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
          if (left.distance < right.distance - 1.0e-12) {
            return true;
          }
          if (right.distance < left.distance - 1.0e-12) {
            return false;
          }
          return left.neighbor_id < right.neighbor_id;
        });
        if (query_rows.size() > k_max) {
          query_rows.resize(k_max);
        }
        local_rows.insert(local_rows.end(), query_rows.begin(), query_rows.end());
      }
    });
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlFixedRadiusNeighborRow& left, const RtdlFixedRadiusNeighborRow& right) {
      return left.query_id < right.query_id;
    });

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_fixed_radius_count_threshold(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    double radius,
    size_t threshold,
    RtdlFixedRadiusCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (radius < 0.0) {
      throw std::runtime_error("fixed_radius_count_threshold radius must be non-negative");
    }
    if (threshold > static_cast<size_t>(std::numeric_limits<uint32_t>::max())) {
      throw std::runtime_error("fixed_radius_count_threshold threshold exceeds uint32 limit");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point2D> query_values;
    std::vector<Point2D> search_values;
    query_values.reserve(query_count);
    search_values.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
      query_values.push_back({query_points[i].id, {query_points[i].x, query_points[i].y}});
    }
    for (size_t i = 0; i < search_count; ++i) {
      search_values.push_back({search_points[i].id, {search_points[i].x, search_points[i].y}});
    }

    EmbreeDevice device;
    PointSceneData data {&search_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(search_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, point_bounds, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    constexpr double kFixedRadiusCandidateEps = 1.0e-4;
    std::vector<RtdlFixedRadiusCountRow> rows(query_values.size());
    run_query_index_ranges(query_values.size(), [&](size_t begin, size_t end) {
      for (size_t query_index = begin; query_index < end; ++query_index) {
        const Point2D& query = query_values[query_index];
        FixedRadiusCountThresholdQueryState state {
            &query,
            &search_values,
            radius * radius,
            threshold,
            0u,
            0u};
        RTCPointQuery point_query;
        point_query.x = static_cast<float>(query.p.x);
        point_query.y = static_cast<float>(query.p.y);
        point_query.z = 0.0f;
        point_query.time = 0.0f;
        point_query.radius = static_cast<float>(radius + kFixedRadiusCandidateEps);
        RTCPointQueryContext context;
        rtcInitPointQueryContext(&context);
        g_query_kind = QueryKind::kFixedRadiusCountThreshold;
        rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect, &state);
        g_query_kind = QueryKind::kNone;
        rows[query_index] = {
            query.id,
            state.neighbor_count,
            state.threshold_reached};
      }
    });
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_knn_rows(
    const RtdlPoint* query_points,
    size_t query_count,
    const RtdlPoint* search_points,
    size_t search_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (k == 0) {
      throw std::runtime_error("knn_rows k must be positive");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point2D> query_values;
    std::vector<Point2D> search_values;
    query_values.reserve(query_count);
    search_values.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
      query_values.push_back({query_points[i].id, {query_points[i].x, query_points[i].y}});
    }
    for (size_t i = 0; i < search_count; ++i) {
      search_values.push_back({search_points[i].id, {search_points[i].x, search_points[i].y}});
    }

    EmbreeDevice device;
    PointSceneData data {&search_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(search_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, point_bounds, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlKnnNeighborRow> rows = run_query_ranges<RtdlKnnNeighborRow>(
        query_values.size(),
        [&](size_t begin, size_t end, std::vector<RtdlKnnNeighborRow>& local_rows) {
      for (size_t query_index = begin; query_index < end; ++query_index) {
        const Point2D& query = query_values[query_index];
        std::vector<RtdlKnnNeighborRow> query_rows;
        std::unordered_set<uint32_t> seen_neighbor_ids;
        KnnRowsQueryState state {&query, &search_values, k, &query_rows, &seen_neighbor_ids};
        RTCPointQuery point_query;
        point_query.x = static_cast<float>(query.p.x);
        point_query.y = static_cast<float>(query.p.y);
        point_query.z = 0.0f;
        point_query.time = 0.0f;
        point_query.radius = std::numeric_limits<float>::infinity();
        RTCPointQueryContext context;
        rtcInitPointQueryContext(&context);
        g_query_kind = QueryKind::kKnnRows;
        rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect, &state);
        g_query_kind = QueryKind::kNone;
        std::sort(query_rows.begin(), query_rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
          if (left.distance < right.distance - 1.0e-12) {
            return true;
          }
          if (right.distance < left.distance - 1.0e-12) {
            return false;
          }
          return left.neighbor_id < right.neighbor_id;
        });
        if (query_rows.size() > k) {
          query_rows.resize(k);
        }
        for (size_t index = 0; index < query_rows.size(); ++index) {
          query_rows[index].neighbor_rank = static_cast<uint32_t>(index + 1);
        }
        local_rows.insert(local_rows.end(), query_rows.begin(), query_rows.end());
      }
    });
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
      return left.query_id < right.query_id;
    });

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_knn_rows_3d(
    const RtdlPoint3D* query_points,
    size_t query_count,
    const RtdlPoint3D* search_points,
    size_t search_count,
    size_t k,
    RtdlKnnNeighborRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (k == 0) {
      throw std::runtime_error("knn_rows k must be positive");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    std::vector<Point3D> query_values;
    std::vector<Point3D> search_values;
    query_values.reserve(query_count);
    search_values.reserve(search_count);
    for (size_t i = 0; i < query_count; ++i) {
      query_values.push_back({query_points[i].id, {query_points[i].x, query_points[i].y, query_points[i].z}});
    }
    for (size_t i = 0; i < search_count; ++i) {
      search_values.push_back({search_points[i].id, {search_points[i].x, search_points[i].y, search_points[i].z}});
    }

    EmbreeDevice device;
    PointSceneData3D data {&search_values};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(search_values.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, point_bounds_3d, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect_3d);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<RtdlKnnNeighborRow> rows = run_query_ranges<RtdlKnnNeighborRow>(
        query_values.size(),
        [&](size_t begin, size_t end, std::vector<RtdlKnnNeighborRow>& local_rows) {
      for (size_t query_index = begin; query_index < end; ++query_index) {
        const Point3D& query = query_values[query_index];
        std::vector<RtdlKnnNeighborRow> query_rows;
        std::unordered_set<uint32_t> seen_neighbor_ids;
        KnnRowsQueryState3D state {&query, &search_values, k, &query_rows, &seen_neighbor_ids};
        RTCPointQuery point_query;
        point_query.x = static_cast<float>(query.p.x);
        point_query.y = static_cast<float>(query.p.y);
        point_query.z = static_cast<float>(query.p.z);
        point_query.time = 0.0f;
        point_query.radius = std::numeric_limits<float>::infinity();
        RTCPointQueryContext context;
        rtcInitPointQueryContext(&context);
        g_query_kind = QueryKind::kKnnRows3D;
        rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect_3d, &state);
        g_query_kind = QueryKind::kNone;
        std::sort(query_rows.begin(), query_rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
          if (left.distance < right.distance - 1.0e-12) {
            return true;
          }
          if (right.distance < left.distance - 1.0e-12) {
            return false;
          }
          return left.neighbor_id < right.neighbor_id;
        });
        if (query_rows.size() > k) {
          query_rows.resize(k);
        }
        for (size_t index = 0; index < query_rows.size(); ++index) {
          query_rows[index].neighbor_rank = static_cast<uint32_t>(index + 1);
        }
        local_rows.insert(local_rows.end(), query_rows.begin(), query_rows.end());
      }
    });
    std::stable_sort(rows.begin(), rows.end(), [](const RtdlKnnNeighborRow& left, const RtdlKnnNeighborRow& right) {
      return left.query_id < right.query_id;
    });

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_bfs_expand(
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t column_index_count,
    const RtdlFrontierVertex* frontier,
    size_t frontier_count,
    const uint32_t* visited,
    size_t visited_count,
    uint32_t dedupe,
    RtdlBfsExpandRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    if (row_offset_count == 0) {
      throw std::runtime_error("CSR graph row_offsets must not be empty");
    }
    if (row_offsets == nullptr) {
      throw std::runtime_error("CSR graph row_offsets pointer must not be null");
    }
    if (column_index_count > 0 && column_indices == nullptr) {
      throw std::runtime_error("CSR graph column_indices pointer must not be null");
    }
    if (frontier_count > 0 && frontier == nullptr) {
      throw std::runtime_error("frontier pointer must not be null when frontier_count > 0");
    }
    if (visited_count > 0 && visited == nullptr) {
      throw std::runtime_error("visited pointer must not be null when visited_count > 0");
    }
    if (row_offsets[0] != 0u) {
      throw std::runtime_error("CSR graph row_offsets must start at 0");
    }
    if (row_offsets[row_offset_count - 1] != column_index_count) {
      throw std::runtime_error("CSR graph final row_offset must equal edge_count");
    }

    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    for (size_t index = 1; index < row_offset_count; ++index) {
      if (row_offsets[index] < row_offsets[index - 1]) {
        throw std::runtime_error("CSR graph row_offsets must be non-decreasing");
      }
    }
    for (size_t index = 0; index < column_index_count; ++index) {
      if (column_indices[index] >= vertex_count) {
        throw std::runtime_error("CSR graph column_indices must be valid vertex IDs");
      }
    }

    std::vector<uint8_t> visited_flags(vertex_count, 0u);
    for (size_t index = 0; index < visited_count; ++index) {
      if (visited[index] >= vertex_count) {
        throw std::runtime_error("visited vertex_id must be a valid graph vertex");
      }
      visited_flags[visited[index]] = 1u;
    }

    std::vector<GraphEdgePoint> edge_points;
    edge_points.reserve(column_index_count);
    for (uint32_t src_vertex = 0; src_vertex < vertex_count; ++src_vertex) {
      const size_t start = row_offsets[src_vertex];
      const size_t end = row_offsets[src_vertex + 1];
      for (size_t offset = start; offset < end; ++offset) {
        const uint32_t dst_vertex = column_indices[offset];
        edge_points.push_back({src_vertex, dst_vertex, {static_cast<double>(src_vertex), 0.0}});
      }
    }

    EmbreeDevice device;
    GraphEdgePointSceneData data {&edge_points};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(edge_points.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, graph_edge_point_bounds, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<uint8_t> discovered_flags(vertex_count, 0u);
    std::vector<RtdlBfsExpandRow> rows;
    for (size_t index = 0; index < frontier_count; ++index) {
      const RtdlFrontierVertex frontier_vertex = frontier[index];
      if (frontier_vertex.vertex_id >= vertex_count) {
        throw std::runtime_error("frontier vertex_id must be a valid graph vertex");
      }
      GraphBfsExpandQueryState state {
          &frontier_vertex,
          &edge_points,
          &visited_flags,
          &discovered_flags,
          dedupe,
          &rows,
      };
      RTCPointQuery point_query;
      point_query.x = static_cast<float>(frontier_vertex.vertex_id);
      point_query.y = 0.0f;
      point_query.z = 0.0f;
      point_query.time = 0.0f;
      point_query.radius = static_cast<float>(kEps * 2.0);
      RTCPointQueryContext context;
      rtcInitPointQueryContext(&context);
      g_query_kind = QueryKind::kGraphBfsExpand;
      rtcPointQuery(holder.scene, &point_query, &context, point_point_query_collect, &state);
      g_query_kind = QueryKind::kNone;
    }

    std::sort(
        rows.begin(),
        rows.end(),
        [](const RtdlBfsExpandRow& left, const RtdlBfsExpandRow& right) {
          if (left.level != right.level) {
            return left.level < right.level;
          }
          if (left.dst_vertex != right.dst_vertex) {
            return left.dst_vertex < right.dst_vertex;
          }
          return left.src_vertex < right.src_vertex;
        });

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_triangle_probe(
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
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;

    if (row_offset_count == 0) {
      throw std::runtime_error("CSR graph row_offsets must not be empty");
    }
    if (row_offsets == nullptr) {
      throw std::runtime_error("CSR graph row_offsets pointer must not be null");
    }
    if (column_index_count > 0 && column_indices == nullptr) {
      throw std::runtime_error("CSR graph column_indices pointer must not be null");
    }
    if (seed_count > 0 && seeds == nullptr) {
      throw std::runtime_error("edge seed pointer must not be null when seed_count > 0");
    }
    if (row_offsets[0] != 0u) {
      throw std::runtime_error("CSR graph row_offsets must start at 0");
    }
    if (row_offsets[row_offset_count - 1] != column_index_count) {
      throw std::runtime_error("CSR graph final row_offset must equal edge_count");
    }

    const uint32_t vertex_count = static_cast<uint32_t>(row_offset_count - 1);
    for (size_t index = 1; index < row_offset_count; ++index) {
      if (row_offsets[index] < row_offsets[index - 1]) {
        throw std::runtime_error("CSR graph row_offsets must be non-decreasing");
      }
    }
    for (size_t index = 0; index < column_index_count; ++index) {
      if (column_indices[index] >= vertex_count) {
        throw std::runtime_error("CSR graph column_indices must be valid vertex IDs");
      }
    }

    std::vector<GraphEdgePoint> edge_points;
    edge_points.reserve(column_index_count);
    for (uint32_t src_vertex = 0; src_vertex < vertex_count; ++src_vertex) {
      const size_t start = row_offsets[src_vertex];
      const size_t end = row_offsets[src_vertex + 1];
      for (size_t offset = start; offset < end; ++offset) {
        const uint32_t dst_vertex = column_indices[offset];
        edge_points.push_back({src_vertex, dst_vertex, {static_cast<double>(src_vertex), 0.0}});
      }
    }

    EmbreeDevice device;
    GraphEdgePointSceneData data {&edge_points};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(edge_points.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, graph_edge_point_bounds, nullptr);
    rtcSetGeometryPointQueryFunction(holder.geometry, point_point_query_collect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::vector<uint32_t> u_neighbor_marks(vertex_count, 0u);
    std::vector<uint32_t> v_neighbor_marks(vertex_count, 0u);
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

      std::vector<uint32_t> u_neighbors;
      GraphTriangleProbeQueryState u_state {
          &edge_points,
          &u_neighbor_marks,
          stamp,
          &u_neighbors,
      };
      RTCPointQuery u_query;
      u_query.x = static_cast<float>(u);
      u_query.y = 0.0f;
      u_query.z = 0.0f;
      u_query.time = 0.0f;
      u_query.radius = static_cast<float>(kEps * 2.0);
      RTCPointQueryContext u_context;
      rtcInitPointQueryContext(&u_context);
      g_query_kind = QueryKind::kGraphTriangleProbe;
      rtcPointQuery(holder.scene, &u_query, &u_context, point_point_query_collect, &u_state);

      std::vector<uint32_t> v_neighbors;
      GraphTriangleProbeQueryState v_state {
          &edge_points,
          &v_neighbor_marks,
          stamp,
          &v_neighbors,
      };
      RTCPointQuery v_query;
      v_query.x = static_cast<float>(v);
      v_query.y = 0.0f;
      v_query.z = 0.0f;
      v_query.time = 0.0f;
      v_query.radius = static_cast<float>(kEps * 2.0);
      RTCPointQueryContext v_context;
      rtcInitPointQueryContext(&v_context);
      rtcPointQuery(holder.scene, &v_query, &v_context, point_point_query_collect, &v_state);
      g_query_kind = QueryKind::kNone;

      const std::vector<uint32_t>& smaller = (u_neighbors.size() <= v_neighbors.size()) ? u_neighbors : v_neighbors;
      const std::vector<uint32_t>& other_neighbor_marks =
          (u_neighbors.size() <= v_neighbors.size()) ? v_neighbor_marks : u_neighbor_marks;
      std::vector<uint32_t> common_neighbors;
      common_neighbors.reserve(smaller.size());
      for (uint32_t w : smaller) {
        if (other_neighbor_marks[w] != stamp) {
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
        std::fill(u_neighbor_marks.begin(), u_neighbor_marks.end(), 0u);
        std::fill(v_neighbor_marks.begin(), v_neighbor_marks.end(), 0u);
        stamp = 1u;
      }
    }

    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_conjunctive_scan(
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
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (field_count == 0 || fields == nullptr || row_values == nullptr) {
      throw std::runtime_error("DB table inputs must not be null");
    }
    if (clause_count > 0 && clauses == nullptr) {
      throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    db_throw_if_row_count_exceeds_limit(row_count);
    std::vector<DbPrimaryAxis> axes;
    axes.reserve(std::min<size_t>(clause_count, 3));
    for (size_t i = 0; i < clause_count && i < 3; ++i) {
      axes.push_back(db_make_primary_axis(fields, field_count, row_values, row_count, clauses[i]));
    }
    const std::vector<DbRowBox> boxes = db_build_row_boxes(fields, field_count, row_values, row_count, axes);

    EmbreeDevice device;
    DbRowBoxSceneData data {&boxes};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(boxes.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, db_row_box_bounds, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, db_row_box_intersect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::unordered_set<uint32_t> seen_row_ids;
    std::vector<RtdlDbRowIdRow> rows;
    DbScanRayQueryState state {
        fields,
        field_count,
        row_values,
        row_count,
        clauses,
        clause_count,
        kDbMaxCandidateRowsPerJob,
        &seen_row_ids,
        &rows};
    db_clear_limit_error();
    db_launch_primary_matrix_rays(axes, [&](int64_t x, int64_t y, int64_t z_lo, int64_t z_hi) {
      RTCRayHit rayhit;
      set_ray_3d(
          &rayhit,
          {static_cast<double>(x), static_cast<double>(y), static_cast<double>(z_lo) - 1.0},
          {0.0, 0.0, 1.0},
          static_cast<float>((z_hi - z_lo) + 2));
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      g_query_kind = QueryKind::kDbScanRay;
      g_query_state = &state;
      rtcIntersect1(holder.scene, &rayhit, &args);
      g_query_kind = QueryKind::kNone;
      g_query_state = nullptr;
      db_throw_if_limit_error();
    });
    std::sort(rows.begin(), rows.end(), [](const RtdlDbRowIdRow& left, const RtdlDbRowIdRow& right) {
      return left.row_id < right.row_id;
    });
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_grouped_count(
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
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (field_count == 0 || fields == nullptr || row_values == nullptr || group_key_field == nullptr) {
      throw std::runtime_error("DB grouped_count inputs must not be null");
    }
    db_throw_if_row_count_exceeds_limit(row_count);
    std::vector<DbPrimaryAxis> axes;
    axes.reserve(std::min<size_t>(clause_count, 3));
    for (size_t i = 0; i < clause_count && i < 3; ++i) {
      axes.push_back(db_make_primary_axis(fields, field_count, row_values, row_count, clauses[i]));
    }
    const std::vector<DbRowBox> boxes = db_build_row_boxes(fields, field_count, row_values, row_count, axes);
    const size_t group_field_index = db_find_field_index_or_throw(fields, field_count, group_key_field);

    EmbreeDevice device;
    DbRowBoxSceneData data {&boxes};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(boxes.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, db_row_box_bounds, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, db_row_box_intersect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::unordered_set<uint32_t> seen_row_ids;
    std::unordered_map<int64_t, int64_t> counts;
    DbGroupedCountRayQueryState state {
        fields,
        field_count,
        row_values,
        row_count,
        clauses,
        clause_count,
        group_field_index,
        kDbMaxCandidateRowsPerJob,
        kDbMaxGroupsPerJob,
        &seen_row_ids,
        &counts};
    db_clear_limit_error();
    db_launch_primary_matrix_rays(axes, [&](int64_t x, int64_t y, int64_t z_lo, int64_t z_hi) {
      RTCRayHit rayhit;
      set_ray_3d(
          &rayhit,
          {static_cast<double>(x), static_cast<double>(y), static_cast<double>(z_lo) - 1.0},
          {0.0, 0.0, 1.0},
          static_cast<float>((z_hi - z_lo) + 2));
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      g_query_kind = QueryKind::kDbGroupedCountRay;
      g_query_state = &state;
      rtcIntersect1(holder.scene, &rayhit, &args);
      g_query_kind = QueryKind::kNone;
      g_query_state = nullptr;
      db_throw_if_limit_error();
    });
    std::vector<RtdlDbGroupedCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& entry : counts) {
      rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbGroupedCountRow& left, const RtdlDbGroupedCountRow& right) {
      return left.group_key < right.group_key;
    });
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_run_grouped_sum(
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
  return handle_native_call([&]() {
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    if (field_count == 0 || fields == nullptr || row_values == nullptr || group_key_field == nullptr || value_field == nullptr) {
      throw std::runtime_error("DB grouped_sum inputs must not be null");
    }
    db_throw_if_row_count_exceeds_limit(row_count);
    std::vector<DbPrimaryAxis> axes;
    axes.reserve(std::min<size_t>(clause_count, 3));
    for (size_t i = 0; i < clause_count && i < 3; ++i) {
      axes.push_back(db_make_primary_axis(fields, field_count, row_values, row_count, clauses[i]));
    }
    const std::vector<DbRowBox> boxes = db_build_row_boxes(fields, field_count, row_values, row_count, axes);
    const size_t group_field_index = db_find_field_index_or_throw(fields, field_count, group_key_field);
    const size_t value_field_index = db_find_field_index_or_throw(fields, field_count, value_field);
    if (fields[value_field_index].kind != kDbKindInt64 && fields[value_field_index].kind != kDbKindBool) {
      throw std::runtime_error("first-wave Embree grouped_sum supports integer-compatible value fields only");
    }

    EmbreeDevice device;
    DbRowBoxSceneData data {&boxes};
    SceneHolder holder(device.device);
    holder.geometry = rtcNewGeometry(device.device, RTC_GEOMETRY_TYPE_USER);
    rtcSetGeometryUserPrimitiveCount(holder.geometry, static_cast<unsigned>(boxes.size()));
    rtcSetGeometryUserData(holder.geometry, &data);
    rtcSetGeometryBoundsFunction(holder.geometry, db_row_box_bounds, nullptr);
    rtcSetGeometryIntersectFunction(holder.geometry, db_row_box_intersect);
    rtcCommitGeometry(holder.geometry);
    rtcAttachGeometry(holder.scene, holder.geometry);
    rtcCommitScene(holder.scene);

    std::unordered_set<uint32_t> seen_row_ids;
    std::unordered_map<int64_t, int64_t> sums;
    DbGroupedSumRayQueryState state {
        fields,
        field_count,
        row_values,
        row_count,
        clauses,
        clause_count,
        group_field_index,
        value_field_index,
        kDbMaxCandidateRowsPerJob,
        kDbMaxGroupsPerJob,
        &seen_row_ids,
        &sums};
    db_clear_limit_error();
    db_launch_primary_matrix_rays(axes, [&](int64_t x, int64_t y, int64_t z_lo, int64_t z_hi) {
      RTCRayHit rayhit;
      set_ray_3d(
          &rayhit,
          {static_cast<double>(x), static_cast<double>(y), static_cast<double>(z_lo) - 1.0},
          {0.0, 0.0, 1.0},
          static_cast<float>((z_hi - z_lo) + 2));
      RTCIntersectArguments args;
      rtcInitIntersectArguments(&args);
      g_query_kind = QueryKind::kDbGroupedSumRay;
      g_query_state = &state;
      rtcIntersect1(holder.scene, &rayhit, &args);
      g_query_kind = QueryKind::kNone;
      g_query_state = nullptr;
      db_throw_if_limit_error();
    });
    std::vector<RtdlDbGroupedSumRow> rows;
    rows.reserve(sums.size());
    for (const auto& entry : sums) {
      rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbGroupedSumRow& left, const RtdlDbGroupedSumRow& right) {
      return left.group_key < right.group_key;
    });
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_db_dataset_create(
    const RtdlDbField* fields,
    size_t field_count,
    const RtdlDbScalar* row_values,
    size_t row_count,
    const char* const* primary_fields,
    size_t primary_field_count,
    RtdlEmbreeDbDataset** dataset_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (dataset_out == nullptr) {
      throw std::runtime_error("dataset output pointer must not be null");
    }
    *dataset_out = nullptr;
    db_validate_db_inputs(fields, field_count, row_values, row_count, nullptr, 0);

    EmbreeDbDatasetImpl* dataset = new EmbreeDbDatasetImpl();
    try {
      db_copy_dataset_table(*dataset, fields, field_count, row_values, row_count);

      std::vector<const char*> primary_names;
      if (primary_field_count > 0) {
        if (primary_fields == nullptr) {
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
        throw std::runtime_error("Embree prepared DB dataset requires at least one numeric primary RT axis");
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
      dataset->boxes = db_build_row_boxes(
          dataset->fields.data(),
          dataset->fields.size(),
          dataset->row_values.data(),
          dataset->row_count,
          dataset->primary_axes);
      db_attach_dataset_scene(*dataset);
      *dataset_out = reinterpret_cast<RtdlEmbreeDbDataset*>(dataset);
    } catch (...) {
      delete dataset;
      throw;
    }
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_db_dataset_create_columnar(
    const RtdlDbColumn* columns,
    size_t column_count,
    size_t row_count,
    const char* const* primary_fields,
    size_t primary_field_count,
    RtdlEmbreeDbDataset** dataset_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (dataset_out == nullptr) {
      throw std::runtime_error("dataset output pointer must not be null");
    }
    *dataset_out = nullptr;
    db_validate_columnar_inputs(columns, column_count, row_count);

    EmbreeDbDatasetImpl* dataset = new EmbreeDbDatasetImpl();
    try {
      db_copy_dataset_columnar_table(*dataset, columns, column_count, row_count);

      std::vector<const char*> primary_names;
      if (primary_field_count > 0) {
        if (primary_fields == nullptr) {
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
        throw std::runtime_error("Embree prepared DB dataset requires at least one numeric primary RT axis");
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
      dataset->boxes = db_build_row_boxes(
          dataset->fields.data(),
          dataset->fields.size(),
          dataset->row_values.data(),
          dataset->row_count,
          dataset->primary_axes);
      db_attach_dataset_scene(*dataset);
      *dataset_out = reinterpret_cast<RtdlEmbreeDbDataset*>(dataset);
    } catch (...) {
      delete dataset;
      throw;
    }
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT void rtdl_embree_db_dataset_destroy(RtdlEmbreeDbDataset* dataset) {
  delete reinterpret_cast<EmbreeDbDatasetImpl*>(dataset);
}

RTDL_EMBREE_EXPORT int rtdl_embree_db_dataset_conjunctive_scan(
    RtdlEmbreeDbDataset* dataset,
    const RtdlDbClause* clauses,
    size_t clause_count,
    RtdlDbRowIdRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (dataset == nullptr) {
      throw std::runtime_error("Embree prepared DB dataset must not be null");
    }
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (clause_count > 0 && clauses == nullptr) {
      throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    auto* impl = reinterpret_cast<EmbreeDbDatasetImpl*>(dataset);

    const std::vector<DbPrimaryAxis> axes = db_dataset_query_axes(*impl, clauses, clause_count);
    std::unordered_set<uint32_t> seen_row_ids;
    std::vector<RtdlDbRowIdRow> rows;
    DbScanRayQueryState state {
        impl->fields.data(),
        impl->fields.size(),
        impl->row_values.data(),
        impl->row_count,
        clauses,
        clause_count,
        kDbMaxCandidateRowsPerJob,
        &seen_row_ids,
        &rows};
    db_run_dataset_rays(*impl, axes, [&](RTCRayHit& rayhit, RTCIntersectArguments& args) {
      g_query_kind = QueryKind::kDbScanRay;
      g_query_state = &state;
      rtcIntersect1(impl->holder.scene, &rayhit, &args);
      g_query_kind = QueryKind::kNone;
      g_query_state = nullptr;
    });
    std::sort(rows.begin(), rows.end(), [](const RtdlDbRowIdRow& left, const RtdlDbRowIdRow& right) {
      return left.row_id < right.row_id;
    });
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_db_dataset_grouped_count(
    RtdlEmbreeDbDataset* dataset,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    RtdlDbGroupedCountRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (dataset == nullptr) {
      throw std::runtime_error("Embree prepared DB dataset must not be null");
    }
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (group_key_field == nullptr) {
      throw std::runtime_error("group_key_field must not be null");
    }
    if (clause_count > 0 && clauses == nullptr) {
      throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    auto* impl = reinterpret_cast<EmbreeDbDatasetImpl*>(dataset);

    const size_t group_field_index =
        db_find_field_index_or_throw(impl->fields.data(), impl->fields.size(), group_key_field);
    const std::vector<DbPrimaryAxis> axes = db_dataset_query_axes(*impl, clauses, clause_count);
    std::unordered_set<uint32_t> seen_row_ids;
    std::unordered_map<int64_t, int64_t> counts;
    DbGroupedCountRayQueryState state {
        impl->fields.data(),
        impl->fields.size(),
        impl->row_values.data(),
        impl->row_count,
        clauses,
        clause_count,
        group_field_index,
        kDbMaxCandidateRowsPerJob,
        kDbMaxGroupsPerJob,
        &seen_row_ids,
        &counts};
    db_run_dataset_rays(*impl, axes, [&](RTCRayHit& rayhit, RTCIntersectArguments& args) {
      g_query_kind = QueryKind::kDbGroupedCountRay;
      g_query_state = &state;
      rtcIntersect1(impl->holder.scene, &rayhit, &args);
      g_query_kind = QueryKind::kNone;
      g_query_state = nullptr;
    });
    std::vector<RtdlDbGroupedCountRow> rows;
    rows.reserve(counts.size());
    for (const auto& entry : counts) {
      rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbGroupedCountRow& left, const RtdlDbGroupedCountRow& right) {
      return left.group_key < right.group_key;
    });
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT int rtdl_embree_db_dataset_grouped_sum(
    RtdlEmbreeDbDataset* dataset,
    const RtdlDbClause* clauses,
    size_t clause_count,
    const char* group_key_field,
    const char* value_field,
    RtdlDbGroupedSumRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size) {
  return handle_native_call([&]() {
    if (dataset == nullptr) {
      throw std::runtime_error("Embree prepared DB dataset must not be null");
    }
    if (rows_out == nullptr || row_count_out == nullptr) {
      throw std::runtime_error("output pointers must not be null");
    }
    if (group_key_field == nullptr || value_field == nullptr) {
      throw std::runtime_error("group_key_field and value_field must not be null");
    }
    if (clause_count > 0 && clauses == nullptr) {
      throw std::runtime_error("DB clause pointer must not be null when clause_count > 0");
    }
    *rows_out = nullptr;
    *row_count_out = 0;
    auto* impl = reinterpret_cast<EmbreeDbDatasetImpl*>(dataset);

    const size_t group_field_index =
        db_find_field_index_or_throw(impl->fields.data(), impl->fields.size(), group_key_field);
    const size_t value_field_index =
        db_find_field_index_or_throw(impl->fields.data(), impl->fields.size(), value_field);
    if (impl->fields[value_field_index].kind != kDbKindInt64
        && impl->fields[value_field_index].kind != kDbKindBool) {
      throw std::runtime_error("first-wave Embree grouped_sum supports integer-compatible value fields only");
    }

    const std::vector<DbPrimaryAxis> axes = db_dataset_query_axes(*impl, clauses, clause_count);
    std::unordered_set<uint32_t> seen_row_ids;
    std::unordered_map<int64_t, int64_t> sums;
    DbGroupedSumRayQueryState state {
        impl->fields.data(),
        impl->fields.size(),
        impl->row_values.data(),
        impl->row_count,
        clauses,
        clause_count,
        group_field_index,
        value_field_index,
        kDbMaxCandidateRowsPerJob,
        kDbMaxGroupsPerJob,
        &seen_row_ids,
        &sums};
    db_run_dataset_rays(*impl, axes, [&](RTCRayHit& rayhit, RTCIntersectArguments& args) {
      g_query_kind = QueryKind::kDbGroupedSumRay;
      g_query_state = &state;
      rtcIntersect1(impl->holder.scene, &rayhit, &args);
      g_query_kind = QueryKind::kNone;
      g_query_state = nullptr;
    });
    std::vector<RtdlDbGroupedSumRow> rows;
    rows.reserve(sums.size());
    for (const auto& entry : sums) {
      rows.push_back({entry.first, entry.second});
    }
    std::sort(rows.begin(), rows.end(), [](const RtdlDbGroupedSumRow& left, const RtdlDbGroupedSumRow& right) {
      return left.group_key < right.group_key;
    });
    *rows_out = copy_rows_out(rows);
    *row_count_out = rows.size();
  }, error_out, error_size);
}

RTDL_EMBREE_EXPORT void rtdl_embree_free_rows(void* rows) {
  std::free(rows);
}
