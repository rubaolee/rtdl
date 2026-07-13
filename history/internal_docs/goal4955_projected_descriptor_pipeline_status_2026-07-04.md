# Goal4955 Status: Projected Descriptor Pipeline

Date: 2026-07-04
Status: POD measured; real small win, below frozen useful bar

Update: Goal4956 subsequently found a stronger columnar xsect route:

```text
Goal4956 median writer-free hot path: 2.309159s
speedup vs Goal4954-E rerun baseline: 1.276418x
```

Therefore Goal4955 remains a documented sub-threshold projection-only result,
not the best v2.14.3 candidate.

## Objective

Goal4955 tests one v2.14.3 pre-fusion optimization:

```text
If the downstream consumer only needs descriptor-pair counts, do not materialize
point-geometry payload columns.
```

This is projection pushdown / late materialization.  It is a generic dataflow
optimization, not a RayJoin-specific RTDL core primitive.

The POD result is honest but not enough to close the performance goal:

```text
rerun baseline median:                 2.947452s
best projected descriptor median:      2.597365s
speedup vs rerun baseline:             1.134786x
frozen useful bar:                     >=1.15x
decision:                              below useful bar
```

Therefore this goal should **not** be described as a completed v2.14.3
performance win.  It is a real, generic, measured small improvement that falls
short of the frozen bar.

## Why This Is The Right First Cut

The v2.14.2 numeric binary route from Goal4954-E had the current best median:

```text
writer-free hot path: 2.921366s
```

For this goal, the baseline was rerun on the current POD.  The rerun baseline
median was:

```text
writer-free hot path: 2.947452s
```

Its largest remaining pre-fusion costs include:

| Phase | Goal4954-E median seconds |
|---|---:|
| LSI rows | 1.196542 |
| numeric reprojection | 0.221340 |
| numeric sort total | 0.444451 |
| grouped carrier construction | 0.909884 |
| grouped descriptor consumer | 0.059860 |

The current downstream consumer is descriptor-pair counting.  It needs:

- group labels;
- group lengths;
- group counts;
- descriptor-pair aggregation.

It does **not** need the full point geometry payload (`x`, `y`) that Goal4954-C
and Goal4954-E still materialize for 673,371 point rows.

Therefore Goal4955 first attacks avoidable payload materialization, not Layer 4
traversal fusion.

## Implemented Files

### 1. Goal definition

`history/internal_docs/goal4955_v2_14_3_rayjoin_numba_pipeline_goal_2026-07-04.md`

Freezes:

- baseline route: Goal4954-E numeric binary route;
- median baseline: `2.921366s`;
- minimum useful win: `>=1.15x`;
- target win: `>=1.5x`;
- no V3/V4 public frontdoor revival;
- no RayJoin-specific RTDL core primitive;
- no Layer 4 traversal callback/fusion;
- RTDL remains generic, RayJoin remains an app.

### 2. Projected descriptor pipeline measurement

`history/internal_docs/goal4955_projected_descriptor_pipeline_measure.py`

This script reuses Goal4954-E's public LSI/PIP/numeric route, then replaces the
grouped carrier and descriptor consumer with:

- projected descriptor carrier: no `x` / `y` point payload columns;
- same group labels and deduped group lengths required by the descriptor
  consumer;
- CPU `njit` Numba sorted-pair scan for the downstream descriptor aggregation
  when Numba is available.

This is **not** yet a CUDA/device-resident Numba continuation.  It is a
projection-pushdown prototype plus bounded Numba aggregation.  Device-resident
continuation remains a later gate.

Boundary:

- does not edit `src/rtdsl/**`;
- does not edit `src/native/**`;
- does not import bundled `rtdsl.rayjoin_overlay`;
- does not claim paper byte equality for this numeric binary route;
- keeps exact paper text output as a separate correctness route.

### 3. Non-RayJoin projected descriptor proof

`history/internal_docs/goal4955_projected_descriptor_non_rayjoin_proof.py`

Output:

`history/internal_docs/goal4955_projected_descriptor_non_rayjoin_proof.json`

This proof uses a synthetic non-RayJoin grouped spatial carrier and verifies
that descriptor-pair aggregation works without geometry payload columns.

Result:

```text
pass: true
rayjoin_imported: false
cdb_required: false
authorofficial_required: false
geometry_payload_materialized: false
```

### 4. Projected-vs-full carrier semantic unit test

`tests/goal4955_projected_descriptor_pipeline_test.py`

This test builds a small RayJoin-shaped synthetic carrier and verifies:

- the old full grouped carrier includes `x` / `y` geometry payload columns;
- the new projected descriptor carrier does not include `x` / `y`,
  `alt_label`, `source_side_id`, or `source_element_id`;
- both carriers produce identical `group_offset`, `group_length`, `label_a`,
  and `label_b` arrays;
- both descriptor-pair consumers produce the same pair count, group count,
  point-row count, and top descriptor pairs.

This test protects the optimization from silently changing the descriptor
semantics while dropping geometry payload columns.

## Local Verification Already Run

### Syntax / import surface

```text
py -m py_compile \
  history/internal_docs/goal4955_projected_descriptor_pipeline_measure.py \
  history/internal_docs/goal4955_projected_descriptor_non_rayjoin_proof.py
```

Result: pass.

### Non-RayJoin proof

```text
py history/internal_docs/goal4955_projected_descriptor_non_rayjoin_proof.py
```

Result: pass.

### Projected-vs-full carrier semantic test

```text
$env:PYTHONPATH='src'
py -m unittest tests.goal4955_projected_descriptor_pipeline_test
```

Result:

```text
Ran 1 test in 0.089s
OK
```

### Layer 1/2 existing tests

Command:

```text
$env:PYTHONPATH='src'
py -m unittest \
  tests.goal4942_device_column_row_buffer_handoff_test \
  tests.goal4943_lsi_pip_device_column_producer_audit_test \
  tests.goal4944_pip_point_location_device_column_carrier_test \
  tests.goal4946_native_device_columns_numba_execution_test \
  tests.goal4947_lsi_pair_columns_numba_handoff_test
```

Result:

```text
Ran 25 tests in 0.146s
OK (skipped=3)
```

The skipped tests are environment-dependent.

## Numba Boundary

The current Goal4955 script uses Numba as:

```text
cpu_njit_sorted_pair_scan
```

It does not claim:

- CUDA device-resident continuation;
- zero-copy end-to-end execution;
- GPU-resident reprojection/sort;
- Layer 4 traversal fusion.

This boundary matters because the current prototype still needs POD performance
measurement before we can decide whether projection pushdown alone is worth
productizing.

## POD Status And Results

The new POD endpoint was reachable with:

```text
ssh -i ~/.ssh/id_ed25519_rtdl_codex_current_pod -p 10689 root@213.173.108.15
```

POD:

```text
hostname: 9e6187bee599
GPU: NVIDIA RTX 4000 Ada Generation
native library: /root/rtdl_goal4955/build/librtdl_optix.so
```

The POD ran:

- 3 reruns of the Goal4954-E numeric binary baseline;
- 3 runs of the first projected descriptor route;
- 3 runs of an online-dedupe variant;
- 3 runs of the final minimal descriptor route.

Artifacts:

- `history/internal_docs/goal4955_artifacts/baseline_goal4954e_rerun_*.json`
- `history/internal_docs/goal4955_artifacts/projected_descriptor_run_*.json`
- `history/internal_docs/goal4955_artifacts/projected_descriptor_online_run_*.json`
- `history/internal_docs/goal4955_artifacts/projected_descriptor_minimal_run_*.json`
- `history/internal_docs/goal4955_artifacts/goal4955_pod_comparison_summary_v4.json`

Median results:

| Route | Median writer-free hot seconds | Speedup vs rerun baseline | Decision |
|---|---:|---:|---|
| Goal4954-E rerun baseline | 2.947452 | 1.000000x | baseline |
| projected descriptor, first/list route | 2.599655 | 1.133786x | small, below bar |
| projected descriptor, online-dedupe route | 2.646901 | 1.113548x | worse; reject |
| projected descriptor, minimal descriptor route | 2.597365 | 1.134786x | best, still below bar |

Relevant phase medians:

| Phase | Baseline | Minimal descriptor |
|---|---:|---:|
| LSI public rows | 1.000934 | 1.021198 |
| numeric reprojection | 0.234381 | 0.219999 |
| sort map0 | 0.231477 | 0.227377 |
| sort map1 | 0.206608 | 0.254010 |
| grouped carrier construction | 1.127682 | 0.798016 |
| descriptor consumer | 0.054767 | 0.006021 |

Interpretation:

- The projection worked where expected: carrier construction and descriptor
  aggregation became cheaper.
- It did not move LSI, sorting, or the remaining pre-fusion costs enough.
- Online dedupe was slower because it added Python branch/function overhead in
  the hot loop.
- The final minimal descriptor route is the best tested variant, but its
  `1.134786x` median speedup is below the frozen `1.15x` useful threshold.

## Exit Decision

Compare median projected route against rerun Goal4954-E baseline:

| Outcome | Exit label |
|---|---|
| `>= 1.5x` win | `v2_14_3_pipeline_win_productize_next` |
| `>= 1.15x` and `< 1.5x` | `v2_14_3_pipeline_small_win_keep_as_internal` |
| `< 1.15x` | `v2_14_3_pipeline_no_go_pre_fusion_exhausted` |
| POD remains unavailable | `blocked_by_environment` |

Actual outcome:

```text
v2_14_3_pipeline_no_go_pre_fusion_exhausted
```

This does **not** mean the implementation was useless.  It means this specific
pre-fusion projection-pushdown route is not enough to justify a v2.14.3
performance claim.

The work is still aligned with the owner principle:

```text
RTDL is a generic system.
RayJoin is an app on top of it.
```

The optimization is generic projection pushdown / late materialization.  It
does not add a RayJoin-specific RTDL core primitive.  But the measured result is
below the agreed useful bar.
