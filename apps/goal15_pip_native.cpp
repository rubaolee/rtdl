#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

extern "C" {

struct RtdlPoint {
  uint32_t id;
  float x;
  float y;
};

struct RtdlPolygonRef {
  uint32_t id;
  uint32_t vertex_offset;
  uint32_t vertex_count;
};

struct RtdlPipRow {
  uint32_t point_id;
  uint32_t polygon_id;
  uint32_t contains;
};

int rtdl_embree_run_pip(
    const RtdlPoint* points,
    size_t point_count,
    const RtdlPolygonRef* polygons,
    size_t polygon_count,
    const float* vertices_xy,
    size_t vertex_xy_count,
    RtdlPipRow** rows_out,
    size_t* row_count_out,
    char* error_out,
    size_t error_size);
void rtdl_embree_free_rows(void* rows);

}

namespace {

bool read_points_csv(const std::string& path, std::vector<RtdlPoint>* out) {
  std::ifstream stream(path);
  if (!stream) {
    std::cerr << "failed to open " << path << "\n";
    return false;
  }
  std::string line;
  while (std::getline(stream, line)) {
    if (line.empty()) {
      continue;
    }
    std::stringstream ss(line);
    std::string item;
    std::vector<std::string> fields;
    while (std::getline(ss, item, ',')) {
      fields.push_back(item);
    }
    if (fields.size() != 3) {
      std::cerr << "invalid point row: " << line << "\n";
      return false;
    }
    out->push_back(
        RtdlPoint{
            static_cast<uint32_t>(std::stoul(fields[0])),
            std::stof(fields[1]),
            std::stof(fields[2]),
        });
  }
  return true;
}

bool read_polygons_csv(
    const std::string& path,
    std::vector<RtdlPolygonRef>* polygons_out,
    std::vector<float>* vertices_out) {
  std::ifstream stream(path);
  if (!stream) {
    std::cerr << "failed to open " << path << "\n";
    return false;
  }
  std::string line;
  uint32_t offset = 0;
  while (std::getline(stream, line)) {
    if (line.empty()) {
      continue;
    }
    std::stringstream ss(line);
    std::string item;
    std::vector<std::string> fields;
    while (std::getline(ss, item, ',')) {
      fields.push_back(item);
    }
    if (fields.size() != 9) {
      std::cerr << "invalid polygon row: " << line << "\n";
      return false;
    }
    polygons_out->push_back(
        RtdlPolygonRef{
            static_cast<uint32_t>(std::stoul(fields[0])),
            offset,
            4,
        });
    for (size_t i = 1; i < fields.size(); ++i) {
      vertices_out->push_back(std::stof(fields[i]));
    }
    offset += 4;
  }
  return true;
}

bool write_pairs_csv(
    const std::string& path,
    std::vector<std::pair<uint32_t, uint32_t>> rows) {
  std::sort(rows.begin(), rows.end());
  std::ofstream stream(path);
  if (!stream) {
    std::cerr << "failed to write " << path << "\n";
    return false;
  }
  for (const auto& row : rows) {
    stream << row.first << "," << row.second << "\n";
  }
  return true;
}

bool write_timing_json(
    const std::string& path,
    double total_sec,
    size_t row_count,
    uint64_t pair_hash) {
  std::ofstream stream(path);
  if (!stream) {
    std::cerr << "failed to write " << path << "\n";
    return false;
  }
  stream << std::fixed << std::setprecision(9);
  stream << "{\n";
  stream << "  \"total_sec\": " << total_sec << ",\n";
  stream << "  \"row_count\": " << row_count << ",\n";
  stream << "  \"pair_hash\": \"" << std::hex << std::setw(16) << std::setfill('0') << pair_hash << "\"\n";
  stream << "}\n";
  return true;
}

uint64_t hash_pairs(std::vector<std::pair<uint32_t, uint32_t>> rows) {
  std::sort(rows.begin(), rows.end());
  uint64_t hash = 1469598103934665603ull;
  for (const auto& row : rows) {
    for (int shift = 0; shift < 32; shift += 8) {
      hash ^= static_cast<uint8_t>((row.first >> shift) & 0xffu);
      hash *= 1099511628211ull;
    }
    for (int shift = 0; shift < 32; shift += 8) {
      hash ^= static_cast<uint8_t>((row.second >> shift) & 0xffu);
      hash *= 1099511628211ull;
    }
  }
  return hash;
}

}  // namespace

int main(int argc, char** argv) {
  std::string points_path;
  std::string polygons_path;
  std::string pairs_out;
  std::string timing_out;
  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg == "--points" && i + 1 < argc) {
      points_path = argv[++i];
    } else if (arg == "--polygons" && i + 1 < argc) {
      polygons_path = argv[++i];
    } else if (arg == "--pairs-out" && i + 1 < argc) {
      pairs_out = argv[++i];
    } else if (arg == "--timing-out" && i + 1 < argc) {
      timing_out = argv[++i];
    } else {
      std::cerr << "usage: goal15_pip_native --points path --polygons path [--pairs-out path] --timing-out path\n";
      return 2;
    }
  }
  if (points_path.empty() || polygons_path.empty() || timing_out.empty()) {
    std::cerr << "missing required arguments\n";
    return 2;
  }

  std::vector<RtdlPoint> points;
  std::vector<RtdlPolygonRef> polygons;
  std::vector<float> vertices_xy;
  if (!read_points_csv(points_path, &points) ||
      !read_polygons_csv(polygons_path, &polygons, &vertices_xy)) {
    return 1;
  }

  RtdlPipRow* rows_ptr = nullptr;
  size_t row_count = 0;
  char error_buf[512] = {0};
  const auto start = std::chrono::steady_clock::now();
  const int status = rtdl_embree_run_pip(
      points.data(),
      points.size(),
      polygons.data(),
      polygons.size(),
      vertices_xy.data(),
      vertices_xy.size(),
      &rows_ptr,
      &row_count,
      error_buf,
      sizeof(error_buf));
  const auto end = std::chrono::steady_clock::now();
  if (status != 0) {
    std::cerr << (error_buf[0] ? error_buf : "native pip failed") << "\n";
    return 1;
  }

  std::vector<std::pair<uint32_t, uint32_t>> pairs;
  for (size_t i = 0; i < row_count; ++i) {
    if (rows_ptr[i].contains == 1) {
      pairs.emplace_back(rows_ptr[i].point_id, rows_ptr[i].polygon_id);
    }
  }
  rtdl_embree_free_rows(rows_ptr);

  const double total_sec =
      std::chrono::duration<double>(end - start).count();
  const uint64_t pair_hash = hash_pairs(pairs);
  if ((!pairs_out.empty() && !write_pairs_csv(pairs_out, pairs)) ||
      !write_timing_json(timing_out, total_sec, pairs.size(), pair_hash)) {
    return 1;
  }
  return 0;
}
