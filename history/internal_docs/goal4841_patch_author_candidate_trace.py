from pathlib import Path


path = Path("/workspace/RayJoin_goal4840_author_probe/src/algo/rt_pip_custom.cu")
text = path.read_text()

if "TRACE_GOAL4841_POINT_IDX" not in text:
    text = text.replace(
        "extern \"C\" __constant__ rayjoin::LaunchParamsPIP params;\n",
        "extern \"C\" __constant__ rayjoin::LaunchParamsPIP params;\n"
        "\n"
        "#define TRACE_GOAL4841_POINT_IDX 1u\n"
        "#define TRACE_GOAL4841_EID_LIMIT 32u\n",
    )

text = text.replace(
    "    if (x_src_p < x_min || x_src_p > x_max ||\n"
    "        x_src_p == ((query_map_id == 0) ? x_min : x_max)) {\n"
    "      continue;\n"
    "    }\n",
    "    if (x_src_p < x_min || x_src_p > x_max ||\n"
    "        x_src_p == ((query_map_id == 0) ? x_min : x_max)) {\n"
    "      if (point_idx == TRACE_GOAL4841_POINT_IDX && eid < TRACE_GOAL4841_EID_LIMIT) {\n"
    "        printf(\"TRACE4841 skip_x point=%u eid=%u x=%lld xmin=%lld xmax=%lld qmap=%u\\\\n\",\n"
    "               point_idx, eid, (long long)x_src_p, (long long)x_min, (long long)x_max, query_map_id);\n"
    "      }\n"
    "      continue;\n"
    "    }\n",
    1,
)

text = text.replace(
    "    if (diff_y > 0) {\n"
    "      continue;\n"
    "    }\n",
    "    if (diff_y > 0) {\n"
    "      if (point_idx == TRACE_GOAL4841_POINT_IDX && eid < TRACE_GOAL4841_EID_LIMIT) {\n"
    "        printf(\"TRACE4841 skip_above point=%u eid=%u xsect_y=%.17g diff_y=%.17g best_y=%.17g\\\\n\",\n"
    "               point_idx, eid, xsect_y, diff_y, best_y);\n"
    "      }\n"
    "      continue;\n"
    "    }\n",
    1,
)

text = text.replace(
    "    if (xsect_y > best_y) {\n"
    "#ifndef NDEBUG\n"
    "      params.fail_update_count[point_idx]++;\n"
    "#endif\n"
    "      continue;\n"
    "    }\n",
    "    if (xsect_y > best_y) {\n"
    "#ifndef NDEBUG\n"
    "      params.fail_update_count[point_idx]++;\n"
    "#endif\n"
    "      if (point_idx == TRACE_GOAL4841_POINT_IDX && eid < TRACE_GOAL4841_EID_LIMIT) {\n"
    "        printf(\"TRACE4841 skip_worse point=%u eid=%u xsect_y=%.17g best_y=%.17g\\\\n\",\n"
    "               point_idx, eid, xsect_y, best_y);\n"
    "      }\n"
    "      continue;\n"
    "    }\n",
    1,
)

text = text.replace(
    "      if ((!query_map_id && !flag) || (query_map_id && flag)) {\n"
    "        continue;\n"
    "      }\n",
    "      if ((!query_map_id && !flag) || (query_map_id && flag)) {\n"
    "        if (point_idx == TRACE_GOAL4841_POINT_IDX && eid < TRACE_GOAL4841_EID_LIMIT) {\n"
    "          printf(\"TRACE4841 skip_tie point=%u eid=%u current_slope=%.17g best_slope=%.17g qmap=%u\\\\n\",\n"
    "                 point_idx, eid, current_e_slope, best_e_slope, query_map_id);\n"
    "        }\n"
    "        continue;\n"
    "      }\n",
    1,
)

text = text.replace(
    "    t = (scaling.UnscaleY(xsect_y) - scaling.UnscaleY(y_src_p));\n"
    "    t_reported = rayjoin_pip_sos_report_t(t, (double)e.a / e.b, query_map_id);\n",
    "    t = (scaling.UnscaleY(xsect_y) - scaling.UnscaleY(y_src_p));\n"
    "    t_reported = rayjoin_pip_sos_report_t(t, (double)e.a / e.b, query_map_id);\n"
    "    if (point_idx == TRACE_GOAL4841_POINT_IDX && eid < TRACE_GOAL4841_EID_LIMIT) {\n"
    "      printf(\"TRACE4841 accept point=%u eid=%u xsect_y=%.17g best_y_before=%.17g t=%.17g report=%.17g slope=%.17g\\\\n\",\n"
    "             point_idx, eid, xsect_y, best_y, t, t_reported, (double)e.a / e.b);\n"
    "    }\n",
    1,
)

path.write_text(text)
