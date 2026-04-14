#include "rtdl_oracle_internal.h"

#include <queue>

namespace rtdl::oracle {

CsrGraph decode_csr_graph(
    uint32_t vertex_count,
    const uint32_t* row_offsets,
    size_t row_offset_count,
    const uint32_t* column_indices,
    size_t column_index_count) {
  if (row_offsets == nullptr) {
    throw std::runtime_error("csr graph row_offsets must not be null");
  }
  if (row_offset_count == 0) {
    throw std::runtime_error("csr graph row_offsets must not be empty");
  }

  std::vector<uint32_t> normalized_offsets(row_offsets, row_offsets + row_offset_count);
  std::vector<uint32_t> normalized_indices;
  if (column_indices != nullptr && column_index_count > 0) {
    normalized_indices.assign(column_indices, column_indices + column_index_count);
  } else if (column_index_count > 0) {
    throw std::runtime_error("csr graph column_indices must not be null when column_index_count > 0");
  }

  if (normalized_offsets.front() != 0U) {
    throw std::runtime_error("csr graph row_offsets must start at 0");
  }
  if (normalized_offsets.back() != static_cast<uint32_t>(column_index_count)) {
    throw std::runtime_error("csr graph final row_offsets value must equal column_indices length");
  }
  for (size_t index = 1; index < normalized_offsets.size(); ++index) {
    if (normalized_offsets[index] < normalized_offsets[index - 1]) {
      throw std::runtime_error("csr graph row_offsets must be non-decreasing");
    }
  }

  for (uint32_t neighbor_id : normalized_indices) {
    if (neighbor_id >= vertex_count) {
      throw std::runtime_error("csr graph column_indices contain out-of-bounds vertex IDs");
    }
  }

  return CsrGraph{
      vertex_count,
      std::move(normalized_offsets),
      std::move(normalized_indices),
  };
}

std::vector<RtdlBfsLevelRow> oracle_bfs_levels(const CsrGraph& graph, uint32_t source_id) {
  if (source_id >= graph.vertex_count) {
    throw std::runtime_error("bfs source_id is out of bounds for the CSR graph");
  }

  std::unordered_set<uint32_t> visited;
  std::vector<uint32_t> frontier{source_id};
  std::vector<RtdlBfsLevelRow> rows;
  visited.insert(source_id);
  uint32_t level = 0U;

  while (!frontier.empty()) {
    for (uint32_t vertex_id : frontier) {
      rows.push_back({vertex_id, level});
    }

    std::vector<uint32_t> next_frontier;
    for (uint32_t vertex_id : frontier) {
      if (vertex_id >= graph.row_offsets.size() - 1) {
        continue;
      }
      const uint32_t start = graph.row_offsets[vertex_id];
      const uint32_t stop = graph.row_offsets[vertex_id + 1];
      for (uint32_t offset = start; offset < stop; ++offset) {
        const uint32_t neighbor_id = graph.column_indices[offset];
        if (visited.count(neighbor_id) != 0U) {
          continue;
        }
        visited.insert(neighbor_id);
        next_frontier.push_back(neighbor_id);
      }
    }

    std::sort(next_frontier.begin(), next_frontier.end());
    frontier = std::move(next_frontier);
    ++level;
  }

  return rows;
}

uint64_t oracle_triangle_count(const CsrGraph& graph) {
  for (uint32_t vertex_u = 0; vertex_u < graph.vertex_count; ++vertex_u) {
    if (vertex_u >= graph.row_offsets.size() - 1) {
      continue;
    }
    const uint32_t start = graph.row_offsets[vertex_u];
    const uint32_t stop = graph.row_offsets[vertex_u + 1];
    for (uint32_t offset = start; offset < stop; ++offset) {
      const uint32_t neighbor = graph.column_indices[offset];
      if (neighbor == vertex_u) {
        throw std::runtime_error("triangle_count oracle does not support self-loops (not a simple graph)");
      }
      if (offset > start) {
        if (graph.column_indices[offset - 1] >= neighbor) {
          throw std::runtime_error(
              "triangle_count oracle requires strictly ascending neighbor lists per CSR row");
        }
      }
    }
  }

  uint64_t triangle_count = 0U;
  for (uint32_t vertex_u = 0; vertex_u < graph.vertex_count; ++vertex_u) {
    if (vertex_u >= graph.row_offsets.size() - 1) {
      continue;
    }
    const uint32_t u_start = graph.row_offsets[vertex_u];
    const uint32_t u_stop = graph.row_offsets[vertex_u + 1];
    for (uint32_t u_offset = u_start; u_offset < u_stop; ++u_offset) {
      const uint32_t vertex_v = graph.column_indices[u_offset];
      if (vertex_v >= graph.vertex_count || vertex_v <= vertex_u || vertex_v >= graph.row_offsets.size() - 1) {
        continue;
      }

      uint32_t left = u_offset + 1;
      const uint32_t v_start = graph.row_offsets[vertex_v];
      const uint32_t v_stop = graph.row_offsets[vertex_v + 1];
      uint32_t right = v_start;
      while (right < v_stop && graph.column_indices[right] <= vertex_v) {
        ++right;
      }

      while (left < u_stop && right < v_stop) {
        const uint32_t left_value = graph.column_indices[left];
        const uint32_t right_value = graph.column_indices[right];
        if (left_value == right_value) {
          ++triangle_count;
          ++left;
          ++right;
        } else if (left_value < right_value) {
          ++left;
        } else {
          ++right;
        }
      }
    }
  }

  return triangle_count;
}

}  // namespace rtdl::oracle
