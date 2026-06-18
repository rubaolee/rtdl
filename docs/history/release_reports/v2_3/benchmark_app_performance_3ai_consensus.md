# RTDL v2.3 Benchmark-App Performance 3-AI Consensus

Status: accepted as a v2.3-family internal performance appendix. This does not
authorize public speedup wording.

Date: 2026-05-27

## Reviewed Documents

- `docs/release_reports/v2_3/benchmark_app_performance.md`
- `docs/release_reports/v2_3/README.md`
- `docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`
- `docs/reports/goal2655_benchmark_rt_core_speedup_summary_2026-05-27.md`
- `docs/reports/goal2653_raydb_benchmark_closeout_2026-05-27.md`
- `docs/reports/goal2653_raydb_closeout_3ai_consensus_2026-05-27.md`
- `docs/application_catalog.md`

## External Review Evidence

- Claude review:
  `docs/reports/goal2656_v2_3_benchmark_performance_claude_review_2026-05-27.md`
- Gemini review:
  `docs/reports/goal2656_v2_3_benchmark_performance_gemini_review_2026-05-27.md`

## Verdicts

Codex verdict:

- Accept after writing the appendix and aligning the v2.3 README with the
  current benchmark set.
- The appendix must stay internal and exact-subpath-only.

Gemini verdict:

- Accept.
- No blocking or non-blocking issues.
- Recommended keeping the RayDB `104.0x` row explicitly footnoted as
  setup-excluded if it is ever moved toward public text.

Claude verdict:

- Accept with fixes.
- No blocking issues.
- Required two clarity fixes before circulation:
  - add the NVIDIA RTX A5000 hardware qualifier to the executive speedup
    summary;
  - add a footnote explaining that RayDB `count` and `sum` are two primary rows
    in the statistics but one combined benchmark-app row in the compact table.

## Fixes Applied

- `docs/release_reports/v2_3/benchmark_app_performance.md` now says the primary
  speedup summary is based on NVIDIA RTX A5000 pod evidence.
- `docs/release_reports/v2_3/benchmark_app_performance.md` now explicitly says
  RayDB `count` and `sum` are distinct primary rows in the statistics and are
  combined only for compact app-level display.
- `docs/release_reports/v2_3/README.md` now lists ten promoted benchmark apps,
  includes the bounded contact witness/contact-manifold benchmark, updates the
  RayDB boundary to the current paper-shaped prepared-query status, and links
  the benchmark-performance appendix.

## Accepted Internal Wording

The following wording is accepted for internal v2.3-family documentation:

```text
Across the current 10 promoted benchmark apps, represented by 11 primary
comparison rows because RayDB has distinct grouped count and grouped sum
contracts, the measured OptiX/RTDL path beats the same-contract Embree baseline
in every row on the NVIDIA RTX A5000 pod evidence. Speedups range from 3.29x to
172.14x, with median 27.67x and geomean 24.13x. These rows are exact-subpath
measurements over RT-shaped generic primitives, not whole-application or public
benchmark claims.
```

## Still Forbidden

- Public speedup wording.
- Whole-application speedup wording.
- Author-code comparison claims.
- CUDA baseline victory claims.
- SQL/DBMS performance claims.
- Full paper-reproduction claims.
- Package-install support claims.
- True zero-copy claims.
- Universal speedup claims for every input shape.

## Consensus Decision

3-AI consensus accepts `benchmark_app_performance.md` as the v2.3-family
internal benchmark-app performance appendix after the fixes above. It may be
used as the current internal baseline for the benchmark portfolio, but any
public-facing performance wording still requires a separate review packet with
exact proposed text.
