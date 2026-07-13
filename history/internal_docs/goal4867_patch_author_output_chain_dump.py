from __future__ import annotations

from pathlib import Path


def main() -> None:
    path = Path("/workspace/RayJoin_goal4867_author_dump/src/app/output_chain.h")
    text = path.read_text()
    text = text.replace("#include <cstdint>\n", "#include <cstdint>\n#include <cstdlib>\n", 1)
    needle = "  std::map<std::pair<int64_t, int64_t>, size_t> face_ids;\n"
    insert = r'''  const char* dump_output_chain_index_env = std::getenv("RJ_DUMP_OUTPUT_CHAIN_INDEX");
  if (dump_output_chain_index_env != nullptr) {
    long long center = std::atoll(dump_output_chain_index_env);
    long long radius = 2;
    const char* radius_env = std::getenv("RJ_DUMP_OUTPUT_CHAIN_RADIUS");
    if (radius_env != nullptr) {
      radius = std::atoll(radius_env);
    }
    long long begin = std::max(0LL, center - radius);
    long long end = std::min<long long>(static_cast<long long>(output_chains.size()), center + radius + 1);
    LOG(INFO) << "RJ_DUMP output_chains_size=" << output_chains.size()
              << " center=" << center << " radius=" << radius;
    for (long long i = begin; i < end; ++i) {
      const auto& c = output_chains[static_cast<size_t>(i)];
      LOG(INFO) << "RJ_DUMP raw_index=" << i
                << " output_chain_no=" << (i + 1)
                << " point_count=" << c.points.size()
                << " left=" << c.left_polygon_id
                << " right=" << c.right_polygon_id
                << " other=" << c.other_map_polygon_id;
      for (size_t j = 0; j < c.points.size(); ++j) {
        LOG(INFO) << "RJ_DUMP point raw_index=" << i
                  << " point_index=" << j
                  << " x=" << c.points[j].x
                  << " y=" << c.points[j].y;
      }
    }
    std::exit(0);
  }

'''
    if needle not in text:
        raise SystemExit("needle not found in output_chain.h")
    path.write_text(text.replace(needle, insert + needle, 1))


if __name__ == "__main__":
    main()
