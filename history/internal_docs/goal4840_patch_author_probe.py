from __future__ import annotations

from pathlib import Path


path = Path("/workspace/RayJoin_goal4840_author_probe/src/run_overlay.cu")
source = path.read_text()
source = source.replace(
    "#include <array>\n#include <memory>\n",
    "#include <array>\n#include <cstdlib>\n#include <iostream>\n#include <memory>\n",
)
needle = """  FOR2 {
    auto prefix = "Map " + std::to_string(im) + ": ";

    timer_next(prefix + "Locate vertices in other map");
    overlay->LocateVerticesInOtherMap(im);
  }

  timer_next("Computer output polygons");
"""
replacement = """  FOR2 {
    auto prefix = "Map " + std::to_string(im) + ": ";

    timer_next(prefix + "Locate vertices in other map");
    overlay->LocateVerticesInOtherMap(im);
  }

  if (std::getenv("RAYJOIN_PROBE_PIP_POINTS") != nullptr) {
    auto closest = overlay->get_closet_eids(0);
    auto faces = overlay->get_point_in_polygon(0);
    const auto& p_graph = *ctx.get_planar_graph(0);
    const size_t ids[] = {747, 748, 749, 750};
    for (size_t point_idx : ids) {
      const auto& point = p_graph.points[point_idx];
      std::cout << "PROBE_PIP map=0 point_idx=" << point_idx
                << " x=" << point.x << " y=" << point.y
                << " closest=" << closest[point_idx]
                << " face=" << faces[point_idx] << std::endl;
    }
    return;
  }

  timer_next("Computer output polygons");
"""
if needle not in source:
    raise SystemExit("run_overlay.cu probe insertion anchor not found")
path.write_text(source.replace(needle, replacement))
print("patched", path)
