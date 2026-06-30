from pathlib import Path


p = Path("/workspace/RayJoin_fresh/src/algo/rt_pip_custom.cu")
backup = p.with_suffix(".cu.goal4806_pipdebug_bak")
if not backup.exists():
    backup.write_text(p.read_text())
text = backup.read_text()
old = "    params.closest_eids[point_idx] = best_e_eid;\n"
new = """    if (point_idx == 595u) {
      int debug_face = -1;
      if (best_e_eid != std::numeric_limits<rayjoin::index_t>::max()) {
        const auto& debug_e = params.base_map_edges[best_e_eid];
        const auto& debug_p1 = params.base_map_points[debug_e.p1_idx];
        const auto& debug_p2 = params.base_map_points[debug_e.p2_idx];
        debug_face = debug_p1.x < debug_p2.x ? debug_e.right_polygon_id : debug_e.left_polygon_id;
      }
      printf("GOAL4806_PIPDEBUG point=%u qsize=%llu best=%u face=%d px=%lld py=%lld\\n",
             point_idx, (unsigned long long) query_points.size(), best_e_eid, debug_face,
             (long long) p.x, (long long) p.y);
    }
    params.closest_eids[point_idx] = best_e_eid;
"""
if old not in text:
    raise SystemExit("closest_eids assignment not found")
p.write_text(text.replace(old, new))
print(f"patched {p}")
