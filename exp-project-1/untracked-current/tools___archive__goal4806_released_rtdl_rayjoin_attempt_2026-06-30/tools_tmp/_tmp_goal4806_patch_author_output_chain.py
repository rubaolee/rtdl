from pathlib import Path


p = Path("/workspace/RayJoin_fresh/src/app/output_chain.h")
backup = p.with_suffix(".h.goal4806_rawdebug_bak")
text = backup.read_text()
text = text.replace(
    "#include <functional>\n",
    "#include <functional>\n#include <cstdlib>\n#include <fstream>\n",
)
old = """  auto flush = [&output_chains](OutputChain<coord_t>& output_chain) {
    auto& points = output_chain.points;

    if (!points.empty()) {
      if (output_chain.left_polygon_id * output_chain.other_map_polygon_id !=
              0 ||
          output_chain.right_polygon_id * output_chain.other_map_polygon_id !=
              0) {
        auto p_it = std::unique(points.begin(), points.end(),
                                [](const double2& a, const double2& b) {
                                  return a.x == b.x && a.y == b.y;
                                });
        points.resize(std::distance(points.begin(), p_it));
        output_chain.id = output_chains.size();
        output_chains.push_back(output_chain);
        points.clear();
      }
      points.clear();
    }
  };
"""
new = """  auto flush = [&output_chains](OutputChain<coord_t>& output_chain) {
    auto& points = output_chain.points;

    if (!points.empty()) {
      if (output_chain.left_polygon_id * output_chain.other_map_polygon_id !=
              0 ||
          output_chain.right_polygon_id * output_chain.other_map_polygon_id !=
              0) {
        auto p_it = std::unique(points.begin(), points.end(),
                                [](const double2& a, const double2& b) {
                                  return a.x == b.x && a.y == b.y;
                                });
        points.resize(std::distance(points.begin(), p_it));
        output_chain.id = output_chains.size();
        const char* debug_path = std::getenv("RAYJOIN_DEBUG_RAW_CHAIN_PATH");
        if (debug_path != nullptr) {
          static std::ofstream debug_stream(debug_path);
          const char* start_env = std::getenv("RAYJOIN_DEBUG_RAW_CHAIN_START");
          const char* end_env = std::getenv("RAYJOIN_DEBUG_RAW_CHAIN_END");
          const size_t start = start_env == nullptr ? 0 : std::strtoull(start_env, nullptr, 10);
          const size_t end = end_env == nullptr ? static_cast<size_t>(-1) : std::strtoull(end_env, nullptr, 10);
          const size_t one_based = output_chains.size() + 1;
          if (one_based >= start && one_based <= end) {
            debug_stream << one_based << " " << points.size() << " "
                         << output_chain.left_polygon_id << " "
                         << output_chain.right_polygon_id << " "
                         << output_chain.other_map_polygon_id;
            for (const auto& point : points) {
              debug_stream << " " << point.x << "," << point.y;
            }
            debug_stream << '\\n';
            debug_stream.flush();
          }
          const char* stop_env = std::getenv("RAYJOIN_DEBUG_RAW_CHAIN_STOP");
          if (stop_env != nullptr && one_based >= end) {
            std::exit(0);
          }
        }
        output_chains.push_back(output_chain);
        points.clear();
      }
      points.clear();
    }
  };
"""
if old not in text:
    raise SystemExit("original flush block not found")
p.write_text(text.replace(old, new))
print(f"patched {p}")
