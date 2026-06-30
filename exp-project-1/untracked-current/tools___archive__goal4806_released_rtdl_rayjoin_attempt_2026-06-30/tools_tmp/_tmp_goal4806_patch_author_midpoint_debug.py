from pathlib import Path

p = Path("/workspace/RayJoin_fresh/src/app/map_overlay_rt.h")
text = p.read_text()
bak = p.with_suffix(p.suffix + ".goal4806_middebug_bak")
if not bak.exists():
    bak.write_text(text)
else:
    text = bak.read_text()

needle = """            dev::ExactPoint<internal_coord_t> mid_p(x1 + (x2 - x1) / 2,
                                                    y1 + (y2 - y1) / 2);

            assert(begin + xsect_idx - idx < d_mid_points.size());

            d_mid_points[begin + xsect_idx - idx] = {mid_p.x, mid_p.y};
"""
replacement = """            dev::ExactPoint<internal_coord_t> mid_p(x1 + (x2 - x1) / 2,
                                                    y1 + (y2 - y1) / 2);

            assert(begin + xsect_idx - idx < d_mid_points.size());

            auto mid_debug_index = begin + xsect_idx - idx;
            if (mid_debug_index >= 590 && mid_debug_index <= 600) {
              printf("GOAL4806_MIDDEBUG im=%d idx=%u eid=%u x1_eids=%u,%u x2_eids=%u,%u x1=%.17g,%.17g x2=%.17g,%.17g midx=%.17g midy=%.17g midxi=%lld midyi=%lld\\n",
                     query_map_id,
                     (unsigned int) mid_debug_index,
                     (unsigned int) eid,
                     (unsigned int) xsect1.eid[0],
                     (unsigned int) xsect1.eid[1],
                     (unsigned int) xsect2.eid[0],
                     (unsigned int) xsect2.eid[1],
                     (double) xsect1.x,
                     (double) xsect1.y,
                     (double) xsect2.x,
                     (double) xsect2.y,
                     (double) mid_p.x,
                     (double) mid_p.y,
                     (long long) ((double) mid_p.x),
                     (long long) ((double) mid_p.y));
            }

            d_mid_points[mid_debug_index] = {mid_p.x, mid_p.y};
"""
if needle not in text:
    raise SystemExit("midpoint needle not found")
p.write_text(text.replace(needle, replacement))
