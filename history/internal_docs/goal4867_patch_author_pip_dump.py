from pathlib import Path


def main() -> None:
    path = Path("/workspace/RayJoin_goal4867_author_dump/src/app/map_overlay_rt.h")
    text = path.read_text()
    if '#include <cstdlib>\n' not in text:
        text = text.replace('#include <iomanip>\n', '#include <cstdlib>\n#include <iomanip>\n')

    marker = '    const char* dump_query_map_env = std::getenv("RJ_DUMP_PIP_QUERY_MAP_ID");'
    if marker in text:
        path.write_text(text)
        return

    needle = "    stream.Sync();\n  }\n\n  void DumpStatistics"
    insert = '''    stream.Sync();

    const char* dump_query_map_env = std::getenv("RJ_DUMP_PIP_QUERY_MAP_ID");
    const char* dump_point_index_env = std::getenv("RJ_DUMP_PIP_POINT_INDEX");
    if (dump_query_map_env != nullptr && dump_point_index_env != nullptr &&
        std::atoi(dump_query_map_env) == query_map_id) {
      long long dump_point_index = std::atoll(dump_point_index_env);
      if (dump_point_index >= 0 &&
          static_cast<size_t>(dump_point_index) < this->closest_eids_[query_map_id].size()) {
        thrust::host_vector<index_t> h_closest_eids = this->closest_eids_[query_map_id];
        thrust::host_vector<polygon_id_t> h_point_in_polygon = this->point_in_polygon_[query_map_id];
        index_t eid = h_closest_eids[static_cast<size_t>(dump_point_index)];
        polygon_id_t face = h_point_in_polygon[static_cast<size_t>(dump_point_index)];
        LOG(INFO) << "RJ_DUMP_PIP query_map_id=" << query_map_id
                  << " point_index=" << dump_point_index
                  << " closest_eid=" << eid
                  << " face=" << face;
        if (eid != std::numeric_limits<index_t>::max()) {
          const auto& base_map = *ctx.get_map(base_map_id);
          const auto& edge = base_map.get_edge(eid);
          LOG(INFO) << "RJ_DUMP_PIP_EDGE eid=" << eid
                    << " p1_idx=" << edge.p1_idx
                    << " p2_idx=" << edge.p2_idx
                    << " left=" << edge.left_polygon_id
                    << " right=" << edge.right_polygon_id
                    << " p1x=" << base_map.get_point(edge.p1_idx).x
                    << " p1y=" << base_map.get_point(edge.p1_idx).y
                    << " p2x=" << base_map.get_point(edge.p2_idx).x
                    << " p2y=" << base_map.get_point(edge.p2_idx).y;
        }
        std::exit(0);
      } else {
        LOG(INFO) << "RJ_DUMP_PIP point_index_out_of_range query_map_id=" << query_map_id
                  << " point_index=" << dump_point_index
                  << " size=" << this->closest_eids_[query_map_id].size();
      }
    }
  }

  void DumpStatistics'''
    if needle not in text:
        raise SystemExit("map_overlay_rt.h needle not found")
    path.write_text(text.replace(needle, insert, 1))


if __name__ == "__main__":
    main()
