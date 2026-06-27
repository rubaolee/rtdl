# Goal3804 Typed-Stream Benchmark Alias Cleanup

Date: 2026-06-07

## Purpose

Goal3804 continues the legacy versioned-helper cleanup for app-facing benchmark
helpers. After Goals3800 and 3802, two obvious current typed-stream helpers still
required users to call v2.8-stamped names even though the underlying contract is
generic and current:

- Barnes-Hut grouped vector sum over typed partner columns.
- RTNN ranked summary over typed partner columns.

## Added Current Aliases

| Benchmark | Current helper/mode | Legacy helper/mode preserved |
| --- | --- | --- |
| Barnes-Hut | `describe_barnes_hut_grouped_vector_sum_typed_stream(...)`, `run_barnes_hut_grouped_vector_sum_typed_stream_preview(...)`, `grouped_vector_sum_typed_stream_plan` | `describe_barnes_hut_v2_8_grouped_vector_sum_typed_stream(...)`, `run_barnes_hut_v2_8_grouped_vector_sum_typed_stream_preview(...)`, `v2_8_grouped_vector_sum_plan` |
| RTNN | `describe_rtnn_ranked_summary_typed_stream(...)`, `run_rtnn_ranked_summary_typed_stream_preview(...)`, `ranked_summary_typed_stream_plan` | `describe_rtnn_v2_8_ranked_summary_typed_stream(...)`, `run_rtnn_v2_8_ranked_summary_typed_stream_preview(...)`, `rtnn_v2_8_ranked_summary_plan` |

## Boundary

- No native engine code changed.
- No partner is auto-selected; callers still choose the partner explicitly.
- No paper reproduction, public speedup, RT-core speedup, release, package
  install, or zero-copy claim is authorized.
- Historical versioned protocol constants remain stable.

## Validation

- `tests.goal3804_typed_stream_benchmark_alias_cleanup_test`
- Existing Goal3165 RTNN and Goal3169 Barnes-Hut typed-stream front-door tests
  remain compatible.
