from pathlib import Path


path = Path("/workspace/RayJoin_goal4840_author_probe/src/algo/rt_pip_custom.cu")
text = path.read_text()
text = text.replace(
    'printf("TRACE4841 skip_above point=%u eid=%u xsect_y=%.17g diff_y=%.17g best_y=%.17g\\\\n",\n'
    '               point_idx, (unsigned int)eid, xsect_y, diff_y, best_y);',
    'printf("TRACE4841 skip_above point=%u eid=%u q=(%lld,%lld) p1=(%lld,%lld) p2=(%lld,%lld) xsect_y=%.17g diff_y=%.17g best_y=%.17g\\\\n",\n'
    '               point_idx, (unsigned int)eid, (long long)x_src_p, (long long)y_src_p,\n'
    '               (long long)p1.x, (long long)p1.y, (long long)p2.x, (long long)p2.y,\n'
    '               xsect_y, diff_y, best_y);',
    1,
)
text = text.replace(
    'printf("TRACE4841 accept point=%u eid=%u xsect_y=%.17g best_y_before=%.17g t=%.17g report=%.17g slope=%.17g\\\\n",\n'
    '             point_idx, (unsigned int)eid, xsect_y, best_y, t, t_reported, (double)e.a / e.b);',
    'printf("TRACE4841 accept point=%u eid=%u q=(%lld,%lld) p1=(%lld,%lld) p2=(%lld,%lld) xsect_y=%.17g best_y_before=%.17g t=%.17g report=%.17g slope=%.17g\\\\n",\n'
    '             point_idx, (unsigned int)eid, (long long)x_src_p, (long long)y_src_p,\n'
    '             (long long)p1.x, (long long)p1.y, (long long)p2.x, (long long)p2.y,\n'
    '             xsect_y, best_y, t, t_reported, (double)e.a / e.b);',
    1,
)
path.write_text(text)
