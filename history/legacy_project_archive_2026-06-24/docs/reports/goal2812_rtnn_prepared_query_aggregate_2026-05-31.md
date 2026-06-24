# Goal2812 RTNN Prepared-Query Aggregate Residency

Date: 2026-05-31

Verdict: accept-with-boundary.

Goal2812 adds a generic prepared-query device-residency path for the v2.5
fixed-radius 3D ranked-summary aggregate. Before this goal, RTDL prepared the
search-side grid once but still uploaded query points inside every timed repeat.
The CuPy grid opponent kept query arrays resident during timed repeats, so the
comparison still included a query-upload cost mismatch.

Goal2812 fixes that for the promoted float32 aggregate row by allowing users to
prepare query point columns once, then run repeated aggregate kernels over the
resident query handle.

This is not an RTNN-specific path. The native ABI and Python API are generic:
prepared fixed-radius query points plus ranked-neighbor aggregate over a
prepared fixed-radius search structure.

## Code Changes

| File | Change |
| --- | --- |
| `src/native/optix/rtdl_optix_workloads.cpp` | Added `PreparedFixedRadiusQueryPoints3D` and a prepared-query float32 aggregate path with direct/fallback density selection. |
| `src/native/optix/rtdl_optix_api.cpp` / `src/native/optix/rtdl_optix_prelude.h` | Added prepare/destroy/query-resident aggregate C ABI functions. |
| `src/rtdsl/optix_runtime.py` | Added `PreparedOptixFixedRadiusQueryPoints3D`, `prepare_optix_fixed_radius_query_points_3d`, and `aggregate_ranked_summary_prepared_queries(...)`. |
| `src/rtdsl/__init__.py` | Exported the prepared-query runtime API. |
| `scripts/goal2348_rtnn_v2_2_external_runner.py` | Added `ranked-summary-aggregate-prepared-query-float32` mode. |
| `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py` | Promoted the canonical RTNN v2.5 row to prepared-query median timing. |
| `tests/goal2812_rtnn_prepared_query_aggregate_test.py` | Guards the generic ABI, Python API, runner mode, and harness selection. |

## Clean Pod Evidence

Clean-from-Git pod:

```text
commit: aaf8d5799b69c61b47c4c467e777c1065ea7375f
source_dirty: []
GPU: NVIDIA RTX A5000, 570.211.01
OptiX build: pass
focused tests: 18 passed
```

Final clean-head guard after report/artifact commit:

```text
commit: aa4f0cf0a78b25c995919bc18594429f76454479
source_dirty: []
focused tests: 20 passed
```

Artifacts:

- `docs/reports/goal2812_rtnn_prepared_query_aggregate_pod/rtnn_prepared_query_median_f32_32768.json`
- `docs/reports/goal2812_rtnn_prepared_query_aggregate_pod/rtnn_prepared_query_median_f32_65536.json`

Both artifacts report `upload_sec: 0.0` inside the timed RTDL phase summaries.

## Median Timing Results

Compared with Goal2811 median timing:

| Points | Distribution | Goal2811 RTDL median (s) | Goal2812 RTDL median (s) | RTDL change | Goal2812 CuPy/RTDL |
| ---: | --- | ---: | ---: | ---: | ---: |
| 32768 | uniform | 0.000566739 | 0.000135981 | 4.168x | 0.688x |
| 32768 | clustered | 0.016192632 | 0.016044247 | 1.009x | 0.746x |
| 32768 | shell | 0.000550133 | 0.000390197 | 1.410x | 0.671x |
| 65536 | uniform | 0.000832137 | 0.000419207 | 1.985x | 0.372x |
| 65536 | clustered | 0.063930878 | 0.063771570 | 1.002x | 0.737x |
| 65536 | shell | 0.003093044 | 0.002772068 | 1.116x | 0.979x |

The prepared-query path materially improves sparse/uniform rows because query
upload was a large share of the timed path. Dense clustered rows remain compute
dominated, so their improvement is near-neutral rather than dramatic.

The 65K shell row is now near parity with the CuPy grid opponent (`0.979x`
CuPy/RTDL), but this is still not a public speedup claim.

## Interpretation

This goal validates a central v2.5 design direction: device residency must be a
first-class runtime contract on both sides of a traversal, not only for build
geometry. For RTNN-like workloads, search preparation alone was not enough;
repeated query columns also needed a stable resident handle.

The remaining gap is no longer primarily copy overhead for sparse rows. The next
generic target is a cooperative/tiled top-k reducer or a more occupancy-friendly
dense-cell path for clustered distributions.

## Claim Boundary

- No public speedup claim is authorized.
- No RTDL-beats-CuPy claim is authorized.
- No RTDL-beats-RTNN-paper claim is authorized.
- No paper reproduction claim is authorized.
- No broad RT-core speedup claim is authorized.
- No whole-app speedup claim is authorized.
- No native app-specific engine customization is introduced.
