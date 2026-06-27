# RTDL V4.0.0 Final Closeout

Status: closed for `v4.0.0`.

| Step | Status | Evidence |
| ---: | --- | --- |
| 1 | done | `VERSION` is `v4.0.0`; `pyproject.toml` is `4.0.0`. |
| 2 | done | Front page, docs index, tutorials, examples, and release doorway point to V4.0.0. |
| 3 | done | V4.0.0 release package exists under `docs/release_reports/v4_0_0/`. |
| 4 | done | M1 Linux GPU release gate exists and has a passing Linux artifact. |
| 5 | done | Public wording boundaries keep package, SDK, async, true-zero-copy, public speedup, and RT-core speedup claims blocked. |
| 6 | done | Fresh post-promotion Linux GPU gate on publication commit `a27a4c92f2b8040cb2f655350567059d756b46b1`: `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_a27a4c92_v4_m1_linux_gpu_release_gate_clean_2026-06-19.json`. |

The post-promotion Linux rerun is a validation freshness item, not permission
to widen claims. The clean rerun keeps package, SDK, async, public
true-zero-copy, public speedup, and RT-core speedup wording blocked.

Additional current-head evidence:

- All benchmark-app scale-profile clean rerun:
  `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_a27a4c92_current_benchmark_scale_profile_clean_2026-06-19.json`
- V4.0.0 release-promotion gate:
  `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_a27a4c92_v4_0_release_promotion_gate_clean_2026-06-19.json`
- Post-closeout release-promotion gate over the updated closeout text:
  `docs/reports/v4_0_release_promotion_gate_post_closeout_2026-06-19.json`
