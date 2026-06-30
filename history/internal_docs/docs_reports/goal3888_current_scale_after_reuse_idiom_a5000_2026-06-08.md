# Goal3888 Current Scale Profile After Prepared-Session Reuse Idiom

## Purpose

Goal3888 refreshes the ten-app A5000 scale-profile smoke after the
prepared-session reuse tutorial and RTNN reuse-idiom mode landed. The goal is
to confirm that the app-front-door addition did not disturb the promoted
benchmark scale runner.

This is a validation intake, not a new performance-claim report.

## Environment

- Pod: `ssh root@69.30.85.203 -p 22057 -i id_ed25519_rtdl_codex`
- GPU: `NVIDIA RTX A5000`
- Driver: `580.126.09`
- Pod checkout: `/root/rtdl_goal3876_runner_1780895523`
- Source commit: `7c7137fa`
- Output artifact:
  `docs/reports/goal3888_current_scale_after_reuse_idiom_a5000/summary.json`

Environment variables:

```bash
export PYTHONPATH=/root/rtdl_goal3788_clean_1780857956/.pydeps_goal3788_numba:src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so
export RTDL_OPTIX_LIB=/root/rtdl_goal3788_clean_1780857956/build/librtdl_optix.so
export RTDL_EMBREE_LIBRARY=/root/rtdl_goal3788_clean_1780857956/build/librtdl_embree.so
```

Command:

```bash
python3 scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --output-json docs/reports/goal3888_current_scale_after_reuse_idiom_a5000/summary.json \
  --output-dir docs/reports/goal3888_current_scale_after_reuse_idiom_a5000/outputs \
  --heartbeat-sec 20 \
  --timeout-scale 1.5
```

## Result

- `exit_code`: `0`
- `all_pass`: `true`
- `json_pass_count`: `10`
- selected row count: `10`
- selected prepared-session-profiled rows: `4`
- prepared-session profile geomean prepare/hot-query ratio: `425.19260550877135`
- claim flag violations: none in parsed stdout payloads

| Row | Status | Elapsed sec | Prepared-session profiled |
| --- | --- | ---: | --- |
| `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.752 | true |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.256 | false |
| `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.503 | false |
| `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 1.502 | false |
| `contact_manifold_optix_scale_default_grid64` | pass | 1.002 | false |
| `raydb_style_optix_count_scale_default_262k` | pass | 2.253 | false |
| `barnes_hut_numba_scale_default_8192` | pass | 2.003 | false |
| `librts_spatial_index_optix_scale_default_32768` | pass | 2.003 | true |
| `rtnn_prepared_optix_scale_default_65536` | pass | 2.753 | true |
| `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.502 | true |

## Interpretation

The promoted ten-app scale runner still passes after the RTNN
`prepared_session_reuse_idiom` app-mode addition. The promoted RTNN benchmark
row remains `prepared_optix_ranked_summary`; the idiom mode is not part of the
scale runner and does not replace or perturb the benchmark path.

The four scene-heavy prepared rows continue to carry prepared-session profile
metadata:

- Hausdorff/X-HD threshold;
- LibRTS AABB index;
- RTNN ranked summary;
- triangle-counting weighted any-hit sum.

## Boundary

Goal3888 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, AMD performance wording, automatic partner/backend
selection, or app-specific native-engine logic.

The artifact is useful as a latest-commit A5000 smoke after Goal3886. It is not
a fresh v2.10 release packet and not a public performance comparison.

## Validation

Added `tests/goal3888_current_scale_after_reuse_idiom_a5000_test.py`.

The test checks:

- the artifact exit code is zero;
- `all_pass` is true;
- all ten JSON rows pass and parse;
- all per-row claim-flag violation lists are empty;
- four rows are prepared-session-profiled;
- the report records the pod, commit, row table, and non-authorizing boundary.
