from pathlib import Path


path = Path("/workspace/RayJoin_goal4840_author_probe/src/algo/rt_pip_custom.cu")
text = path.read_text()
text = text.replace(
    "point_idx, eid, (long long)x_src_p,",
    "point_idx, (unsigned int)eid, (long long)x_src_p,",
)
text = text.replace(
    "point_idx, eid, xsect_y, diff_y, best_y);",
    "point_idx, (unsigned int)eid, xsect_y, diff_y, best_y);",
)
text = text.replace(
    "point_idx, eid, xsect_y, best_y);",
    "point_idx, (unsigned int)eid, xsect_y, best_y);",
)
text = text.replace(
    "point_idx, eid, current_e_slope, best_e_slope, query_map_id);",
    "point_idx, (unsigned int)eid, current_e_slope, best_e_slope, query_map_id);",
)
text = text.replace(
    "point_idx, eid, xsect_y, best_y, t, t_reported, (double)e.a / e.b);",
    "point_idx, (unsigned int)eid, xsect_y, best_y, t, t_reported, (double)e.a / e.b);",
)
path.write_text(text)
