# Call For Review - Goal5314 X-HD WaterBodies/BG Corrected Comparison Summary

Please strictly review Goal5314:

```text
history/internal_docs/goal5314_xhd_water_bg_corrected_comparison_summary_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5314_water_bg_corrected_comparison_summary.json
tests/goal5314_xhd_water_bg_corrected_comparison_summary_test.py
```

Also inspect the evidence it consumes:

```text
history/internal_docs/goal5313_xhd_water_bg_author_config_alignment_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_n_points_cell_alignment_summary.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_author_water_bg_full_public_n_points_cell_8.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_witness_distance_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_water_bg_full_public_rtdl_summary.json
```

## Context

Goal5311 ran author `hd_exec` with default `n_points_cell=15` and therefore did
not match the paper log.

Goal5313 showed that the paper-branch logs use `n_points_cell=8`, and that
author `hd_exec` with `-n_points_cell=8` matches the paper log exactly.

Goal5314 creates a corrected comparison summary so future readers do not treat
the Goal5311 default rerun as the final paper-log denominator.

## Review Questions

1. Does Goal5314 correctly preserve Goal5311's `n_points_cell=15` author rerun
   as config-sensitivity evidence rather than deleting it?
2. Does it correctly supersede that default rerun for paper-log comparison with
   the Goal5313 `n_points_cell=8` paper-config denominator?
3. Does the summary correctly distinguish RTDL fast scalar from RTDL
   exact-witness correctness?
4. Is the declared `2e-6` RTDL-float64-vs-author-float32 tolerance justified by
   the witness probe?
5. Does the summary avoid claiming exact paper WKT recovery, Figure 5
   completion, performance parity, or identical numeric precision?
6. Are the tests sufficient to prevent regression to the old denominator
   confusion?
7. Should Goal5315 update public/status docs to mark the old WaterBodies/BG
   mismatch as superseded by the paper-config comparison?

## Expected Answer Shape

```text
Verdict: approve_goal5314_xhd_water_bg_corrected_comparison_summary
or
Verdict: revise_goal5314_...

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to the 7 questions:
1. ...
...
7. ...
```
