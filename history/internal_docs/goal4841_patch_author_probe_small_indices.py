from pathlib import Path


path = Path("/workspace/RayJoin_goal4840_author_probe/src/run_overlay.cu")
text = path.read_text()
old = """    } else {
      const size_t ids[] = {747, 748, 749, 750};
      for (size_t point_idx : ids) {
        const auto& point = p_graph.points[point_idx];
        std::cout << "PROBE_PIP map=0 point_idx=" << point_idx
                  << " x=" << point.x << " y=" << point.y
                  << " closest=" << closest[point_idx]
                  << " face=" << faces[point_idx] << std::endl;
      }
    }
"""
new = """    } else {
      if (p_graph.points.size() <= 4) {
        for (size_t point_idx = 0; point_idx < p_graph.points.size(); ++point_idx) {
          const auto& point = p_graph.points[point_idx];
          std::cout << "PROBE_PIP map=0 point_idx=" << point_idx
                    << " x=" << point.x << " y=" << point.y
                    << " closest=" << closest[point_idx]
                    << " face=" << faces[point_idx] << std::endl;
        }
      } else {
        const size_t ids[] = {747, 748, 749, 750};
        for (size_t point_idx : ids) {
          const auto& point = p_graph.points[point_idx];
          std::cout << "PROBE_PIP map=0 point_idx=" << point_idx
                    << " x=" << point.x << " y=" << point.y
                    << " closest=" << closest[point_idx]
                    << " face=" << faces[point_idx] << std::endl;
        }
      }
    }
"""
if old not in text:
    raise SystemExit("target block not found")
path.write_text(text.replace(old, new, 1))
