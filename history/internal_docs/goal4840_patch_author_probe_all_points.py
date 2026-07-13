from __future__ import annotations

from pathlib import Path


path = Path("/workspace/RayJoin_goal4840_author_probe/src/run_overlay.cu")
lines = path.read_text().splitlines()
start = next(i for i, line in enumerate(lines) if "auto closest = overlay->get_closet_eids(0);" in line)
end = next(i for i, line in enumerate(lines[start:], start) if line.strip() == "return;")
block = """    auto closest = overlay->get_closet_eids(0);
    auto faces = overlay->get_point_in_polygon(0);
    const auto& p_graph = *ctx.get_planar_graph(0);
    if (std::getenv("RAYJOIN_PROBE_ALL_PIP_POINTS") != nullptr) {
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
    }""".splitlines()
path.write_text("\n".join(lines[:start] + block + lines[end:]) + "\n")
print("patched all-points probe block", path)
