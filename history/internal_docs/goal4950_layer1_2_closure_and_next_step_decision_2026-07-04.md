# Goal4950 Layer 1/2 Closure And Next-Step Decision

Date: 2026-07-04

Status: completed_decision__layer1_2_capability_proven__rayjoin_performance_not_moved_enough

## Purpose

Goal4950 closes the current Layer 1/2 push honestly.

The question is:

> After building the generic row-buffer / Numba continuation path, should we keep spending effort on Layer 1/2 for RayJoin performance, or should we stop this line and move to the next layer?

This is a decision goal, not another implementation probe. It exists to prevent repeating already-run experiments under new goal numbers.

## Evidence Chain

### Layer 1: Generic Device-Column Row Buffer

Already proven by Goals 4942-4944:

- native producers can expose device-column carriers;
- carriers are wrapped by a generic row-buffer boundary;
- the row-buffer forbids app-specific schemas and pre-handoff host row materialization.

This is a real capability improvement.

### Layer 2: Numba Continuation Handoff

Already proven by Goals 4946-4948:

- native PIP device columns can feed Numba;
- native LSI pair columns can feed Numba;
- the same mechanism also works on a non-RayJoin ray/triangle hit-stream workload.

This proves the connector is generic enough to be credible. It does not prove RayJoin performance.

### Real RayJoin Hot-Path Remeasure

Goal4949 used the public RayJoin Section 5.7 County x Soil sample.

Result:

- correctness preserved: baseline and Numba variant both byte-equal to author answer;
- current Numba overlay helper is slower:
  - baseline hot rerun elapsed: `6.305s`
  - Numba variant hot rerun elapsed: `8.034s`
  - baseline writer: `2.615s`
  - Numba writer: `4.237s`
- PIP traversal is not the hot bottleneck:
  - vertex PIP total: about `0.020s`
- real remaining numeric target:
  - reprojection: about `0.73-0.75s`
  - sort total: about `0.80s`

Conclusion: the existing app-layer Numba helper must not be promoted.

### Prior Direct Reprojection/Sort Probe

Goal4924 already tested the only plausible direct Layer 2 RayJoin numeric target:

- replace `intersection_rows_from_pairs`;
- replace `sort_xsects_for_map`;
- avoid `Fraction` object materialization;
- preserve byte-for-byte output.

Result:

- byte-equal: yes;
- sort improved materially;
- reprojection remained expensive because exact author-compatible rational/scaled-coordinate semantics still require heavy integer/gcd behavior;
- hard bar failed:
  - target reprojection + sort <= `0.45s`;
  - observed about `0.55-0.59s`;
  - target hot body <= `3.45s`;
  - observed best stable workspace-hot repeat about `3.79s`.

Goal4924's exit label was `goal4924_correct_but_not_fast_stop_path`.

## Decision

Layer 1/2 should close in its current form:

- close as capability success;
- close as limited RayJoin performance no-go;
- do not run another "small Numba tweak" against RayJoin reprojection/sort unless a genuinely new algorithmic idea appears.

This is not a failure of the row-buffer architecture. It is a boundary finding:

- Layer 1/2 gives RTDL the right connector shape;
- RayJoin Section 5.7's remaining cost is not solved by simply adding more Numba around the existing app-layer code.

## Why Continuing The Same Line Would Be Foolish

Continuing Layer 2 micro-optimization would repeat known evidence:

1. Current Numba overlay helper is slower.
2. Direct reprojection/sort probe was byte-equal but missed the performance bar.
3. Writer/output assembly is the larger remaining cost.
4. PIP traversal is already tiny in prepared-hot mode.

Therefore the next useful work is not another Layer 2 tweak. The next useful work is Layer 3:

> Measure and redesign output assembly so the expensive structural part becomes generic compiled infrastructure, while final RayJoin text formatting remains app-owned.

## Next Goal Recommendation

Create Goal4951:

`Layer 3 writer/output assembly decomposition and genericity design`

Goal4951 should:

1. Measure baseline writer internals on the public sample, not only the current rejected Numba writer path.
2. Split writer cost into:
   - grouping / structural output-chain assembly;
   - point formatting;
   - line/string construction;
   - file write / bulk I/O.
3. Decide which parts can be generic RTDL infrastructure.
4. Explicitly forbid putting "RayJoin output text format" into RTDL core.
5. Produce a go/no-go decision for a compiled generic output assembly path.

## Authorized Claim

Authorized:

- Layer 1/2 row-buffer and Numba handoff are proven capabilities.
- The same mechanism passed a non-RayJoin genericity gate.
- Current RayJoin app-layer Numba helper is not a performance win.
- A prior direct reprojection/sort probe was correct but insufficient.
- The next high-value target is Layer 3 writer/output assembly.

Not authorized:

- no claim that Layer 1/2 moves RayJoin whole-app performance materially;
- no claim that Numba closes the RayJoin gap;
- no claim that current writer assembly path should be promoted;
- no app-specific RayJoin output format in RTDL core.

## Exit Label

`completed_layer1_2_capability_success__rayjoin_perf_no_go__move_to_layer3_writer_design`
