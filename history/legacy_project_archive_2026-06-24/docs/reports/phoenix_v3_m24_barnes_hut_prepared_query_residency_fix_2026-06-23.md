# Phoenix V3 M24 Barnes-Hut Prepared Query Residency Fix

Status: focused blocker-fix candidate, not release authorization.

## Scope

M24 targets the Barnes-Hut severe regression found by the M22 same-RT-hardware
V2.14 vs Phoenix V3 all-app run:

- M22 Barnes-Hut app geomean: `0.831x`
- M21 blocker: Barnes-Hut app geomean below the `0.900x` severe-regression floor
- Worst visible row: OptiX node coverage at 32768 bodies regressed from V2.14
  `0.041552s` to current V3 `0.071077s`

This fix does not authorize a V3 release, public speedup wording, broad
V3-over-V2 wording, or an all-app rerun before external review.

## Diagnosis

Focused micro-probes on the same RTX 4000 Ada POD separated Python packing from
native RT traversal:

| Path | V2.14 median | Current median |
| --- | ---: | ---: |
| `_body_points(32768)` | `0.050664s` | `0.036038s` |
| `pack_points(32768)` | `0.040539s` | `0.039645s` |
| non-prepacked OptiX scalar query | `0.032964s` | `0.033422s` |
| prepacked OptiX scalar query | `0.000174s` | `0.000169s` |

Conclusion: the regression was not native OptiX traversal. The benchmark was
measuring a cold/non-prepacked query path and mixing Python point packing into
the prepared query metric. The V3 runtime gap was the lack of a productized,
generic prepared-query payload on the fixed-radius threshold-count primitive.

## Implementation

Changed files:

- `src/rtdsl/generic_primitives.py`
  - added `GenericPreparedFixedRadiusCountThreshold2D.prepare_query_points(...)`
  - reports `query_points_prepacked_by_caller` using the real `PackedPoints`
    type instead of class-name string matching
- `src/rtdsl/embree_runtime.py`
  - lets `PreparedEmbreeFixedRadiusCountThreshold2D` accept `PackedPoints`
    for search/query inputs, matching the OptiX prepared path
- `examples/current/apps/simulation/rtdl_barnes_hut_force_app.py`
  - prepares Barnes-Hut node-coverage query points once through the generic
    API
  - records `query_points_prepare_sec` separately from hot query time

This is a generic prepared fixed-radius query-residency surface. Barnes-Hut is
only the first focused benchmark using it.

## Focused Stress Evidence

Artifacts:

- Previous current repro:
  `docs/rebuild/v3/evidence/phoenix_v3_m24_barnes_hut_current_repro_20260623`
- V2.14 repro:
  `docs/rebuild/v3/evidence/phoenix_v3_m24_barnes_hut_v2_14_repro_20260623`
- Fixed current rerun:
  `docs/rebuild/v3/evidence/phoenix_v3_m24_barnes_hut_current_prepacked_fix_20260623`

Same POD, same app, same stress-tier rows, case-repeat `3`.
These four rows are the Barnes-Hut stress rows that drove the M22/M21
`barnes_hut_app_geomean_floor` blocker. The post-fix Barnes-Hut blocker-row
geomean is therefore the four-row fixed-current vs V2.14 geomean below; no
all-app rerun is authorized by this focused report.

| Row | V2.14 sec | Current before fix sec | Current after fix sec | Fixed current vs V2.14 |
| --- | ---: | ---: | ---: | ---: |
| Embree 32768 | `0.131938` | `0.132735` | `0.084814` | `1.556x` |
| OptiX 32768 | `0.041552` | `0.071077` | `0.000447` | `92.918x` |
| Embree 131072 | `0.556249` | `0.545417` | `0.254535` | `2.185x` |
| OptiX 131072 | `0.296358` | `0.295900` | `0.001498` | `197.827x` |

Barnes-Hut four-row focused geomean, fixed current vs V2.14: `15.811x`.

Fixed current OptiX vs Embree within the same run:

- 32768 bodies: `189.658x`
- 131072 bodies: `169.909x`

## Repeat-50 Evidence

The single-query stress rows prove the metric split. The repeat-50 run proves
that the split corresponds to real prepared-workload value rather than only
renaming phases.

Artifacts:

- `docs/rebuild/v3/evidence/phoenix_v3_m24_barnes_hut_repeat50_20260623`

Command shape:

```bash
PYTHONPATH=src:. python examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  --mode optix_node_coverage_prepared --body-count <N> --skip-validation \
  --require-rt-core --repeat 50 --warmup 5
```

| Body count | V2.14 query total | Fixed current query total | Query total speedup | Speedup including current query prepare |
| ---: | ---: | ---: | ---: | ---: |
| 32768 | `2.161036s` | `0.008010s` | `269.792x` | `17.818x` |
| 131072 | `12.044135s` | `0.038259s` | `314.804x` | `22.812x` |

Current query preparation is explicit:

- 32768 bodies: `0.113272s`
- 131072 bodies: `0.489708s`

Single-use boundary:

- 32768 bodies: one current query-prepare plus one hot query is about
  `0.113719s`, slower than V2.14's single-query `0.041552s`
- 131072 bodies: one current query-prepare plus one hot query is about
  `0.491206s`, slower than V2.14's single-query `0.296358s`
- The prepared payload amortizes after roughly four repeated queries per
  prepared query payload. Claims must be framed as prepared/repeated-query
  improvements, not single-query wall-time improvements.

## Boundary

This fix supports the V3 prepared/resident execution goal inside RTDL:
reusable query payloads between RTDL phases. It is not external zero-copy,
embedding, multi-language host interop, or a whole Barnes-Hut force-solver
speedup.

The fixed primary metric is hot prepared-query time after generic query
preparation. Single-run wall time is not accelerated by the same factor because
scene preparation and query payload preparation remain visible setup phases.
For repeated prepared queries, the total query work plus one query-prepare step
shows material speedups of `17.818x` and `22.812x`.

For a single query per prepared payload, the current prepared-query route is
slower than the V2.14 non-prepacked route at the tested sizes. That is an
explicit boundary, not a hidden failure mode.

## Local And POD Validation

Local Windows:

- `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test`
  - `13` tests OK
- `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal757_prepared_optix_fixed_radius_count_test tests.v3_phoenix_prepared_fixed_radius_symbol_cache_test`
  - `20` tests OK, `2` skipped

POD current tree:

- `PYTHONPATH=src:. python -m unittest tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test`
  - `13` tests OK
- focused Barnes-Hut stress rerun:
  - artifact:
    `/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m24_barnes_hut_current_prepacked_fix_20260623`
  - all four rows completed with status `ok`
- release wording gate:
  - `$env:PYTHONPATH='src;.'; py -3 scripts/v3_release_wording_gate.py --pretty --json-out docs\reports\phoenix_v3_m24_release_wording_gate_after_barnes_fix_2026-06-23.json`
  - status `pass`
  - violations `[]`

## Decision Audit

1. Was I foolish?

   No. The decision follows a focused diagnosis that separated native traversal
   from Python packing and found a reusable prepared-query gap.

2. If yes, what actions made the decision foolish?

   The foolish action would have been to hide the phase split, claim whole-app
   Barnes-Hut speedup, or patch only the Barnes-Hut benchmark without exposing a
   generic prepared-query API.

3. Was there another path that avoided being stuck on that idea?

   Yes. The alternative was to keep tuning native OptiX traversal, but the
   micro-probe showed native traversal was already sub-millisecond when fed a
   prepared query payload.

4. Can I now try a different path that truly solves the problem?

   Yes. The different path is now active: productize query preparation as part
   of the generic V3 prepared fixed-radius primitive, then require repeated-query
   evidence and external review before treating the blocker as closed.

## Current Verdict

Codex local verdict: M24 is a strong blocker-fix candidate for the Barnes-Hut
primary-metric severe regression, with an explicit boundary that the large
speedups apply to prepared hot-query/repeated-query work, not single-run whole
app wall time.

Required before closure:

- external Claude or Gemini review of this report
- saved Codex consensus
- no all-app rerun from this report; only the focused Barnes-Hut blocker rows
  are accepted for M24 closure
