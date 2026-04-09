#include "rtdl_oracle_internal.h"

namespace rtdl::oracle {

bool is_close_to_integer(double value) {
  return std::fabs(value - std::round(value)) <= 1.0e-9;
}

void require_pathology_grid_polygon(const Polygon2D& polygon) {
  if (polygon.vertices.size() < 3) {
    throw std::runtime_error("polygon_pair_overlap_area_rows requires polygons with at least 3 vertices");
  }
  for (const Vec2& vertex : polygon.vertices) {
    if (!is_close_to_integer(vertex.x) || !is_close_to_integer(vertex.y)) {
      throw std::runtime_error(
          "polygon_pair_overlap_area_rows currently requires integer-grid polygon vertices");
    }
  }
  for (size_t i = 0; i < polygon.vertices.size(); ++i) {
    const Vec2& start = polygon.vertices[i];
    const Vec2& end = polygon.vertices[(i + 1) % polygon.vertices.size()];
    const double dx = end.x - start.x;
    const double dy = end.y - start.y;
    if (std::fabs(dx) <= kPointEps && std::fabs(dy) <= kPointEps) {
      throw std::runtime_error("polygon_pair_overlap_area_rows does not accept zero-length polygon edges");
    }
    if (std::fabs(dx) > kPointEps && std::fabs(dy) > kPointEps) {
      throw std::runtime_error(
          "polygon_pair_overlap_area_rows currently requires orthogonal integer-grid polygons");
    }
  }
}

uint64_t encode_cell_key(int32_t x, int32_t y) {
  return (static_cast<uint64_t>(static_cast<uint32_t>(x)) << 32) |
         static_cast<uint64_t>(static_cast<uint32_t>(y));
}

std::vector<uint64_t> polygon_unit_cells(const Polygon2D& polygon) {
  require_pathology_grid_polygon(polygon);
  const Bounds2D bounds = bounds_for_polygon(polygon);
  const int min_x = static_cast<int>(std::floor(bounds.min_x));
  const int max_x = static_cast<int>(std::ceil(bounds.max_x));
  const int min_y = static_cast<int>(std::floor(bounds.min_y));
  const int max_y = static_cast<int>(std::ceil(bounds.max_y));
  std::vector<uint64_t> cells;
  cells.reserve(static_cast<size_t>(std::max(0, max_x - min_x) * std::max(0, max_y - min_y)));
  for (int iy = min_y; iy < max_y; ++iy) {
    for (int ix = min_x; ix < max_x; ++ix) {
      if (point_in_polygon(static_cast<double>(ix) + 0.5, static_cast<double>(iy) + 0.5, polygon.vertices)) {
        cells.push_back(encode_cell_key(ix, iy));
      }
    }
  }
  std::sort(cells.begin(), cells.end());
  cells.erase(std::unique(cells.begin(), cells.end()), cells.end());
  return cells;
}

uint32_t intersect_cell_sets(const std::vector<uint64_t>& left, const std::vector<uint64_t>& right) {
  size_t left_index = 0;
  size_t right_index = 0;
  uint32_t count = 0;
  while (left_index < left.size() && right_index < right.size()) {
    if (left[left_index] == right[right_index]) {
      count += 1;
      left_index += 1;
      right_index += 1;
    } else if (left[left_index] < right[right_index]) {
      left_index += 1;
    } else {
      right_index += 1;
    }
  }
  return count;
}

std::vector<uint64_t> polygon_set_unit_cells(const std::vector<Polygon2D>& polygons) {
  std::vector<uint64_t> cells;
  for (const Polygon2D& polygon : polygons) {
    std::vector<uint64_t> polygon_cells = polygon_unit_cells(polygon);
    cells.insert(cells.end(), polygon_cells.begin(), polygon_cells.end());
  }
  std::sort(cells.begin(), cells.end());
  cells.erase(std::unique(cells.begin(), cells.end()), cells.end());
  return cells;
}

}  // namespace rtdl::oracle
