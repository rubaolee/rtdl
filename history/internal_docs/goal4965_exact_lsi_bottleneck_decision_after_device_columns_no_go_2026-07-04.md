# Goal4965 Exact LSI Bottleneck Decision After Device Columns No-Go

Date: 2026-07-04

## Exit Label

`completed_bottleneck_decision__exact_lsi_device_columns_no_go__next_attack_is_exact_lsi_compute`

## Purpose

Close the post-Goal4964 decision point.

Goal4964 tested the natural Layer-1/2 hypothesis:

> If exact LSI is slow because RTDL materializes host rows, then a generic
> exact pair-id device-column route should reduce fresh writer-free overlay
> time.

The result falsified that hypothesis on the public County x Soil sample.

Goal4965 records what that means, what no longer deserves effort, and what the
next credible performance direction is.

## Inputs Considered

### Corrected Measurement Boundary

Goal4959 and Goal4960 fixed the measurement boundary after the invalid
"2.04x" headline:

| Route | Median |
|---|---:|
| Fresh writer-free binary overlay | `0.889023s` |
| Cached/prepared replay after LSI is already computed | `0.087069s` |
| AuthorPatch overlay compute comparator | `0.0421s` |

Interpretation:

- Fresh overlay remains about `21x` slower than AuthorPatch.
- Cached replay is not a fresh overlay cost because the first LSI computation
  has already been paid.
- All performance decisions must use the fresh boundary unless the claim is
  explicitly about repeated replay of the same already-computed overlay.

### Larger Representative Input Availability

Goal4961 found that the current POD contains only the public County x Soil
sample. Historical larger representative CDBs were not present under `/root`,
`/workspace`, `/tmp`, or `/dev/shm`.

Interpretation:

- Larger representative testing is blocked by input availability.
- Do not invent or silently substitute a "large" result.
- The next engineering decision must be based on the public sample until data
  is restored.

### Exact LSI Device Columns Design And Result

Goal4963 defined the exact planar-map LSI pair-id device-column design.

Goal4964 implemented and measured it.

Median results from `goal4964_exact_lsi_pair_id_device_columns_summary.json`:

| Route | writer_free_hot_sec | Ratio vs `0.0421s` | LSI phase | Device-to-NumPy copy |
|---|---:|---:|---:|---:|
| host exact pair-id rows | `0.893045s` | `21.21x` | `0.806946s` | n/a |
| exact pair-id device columns | `0.987424s` | `23.45x` | `0.895913s` | `0.000526s` |

The semantic fingerprint was stable across all six runs:

```text
lsi_row_count = 20860
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

## Decision

### D1. Exact pair-id device columns are correct but not a performance route

The new device-column route is a useful generic capability/prototype, but it is
not the v2.14.3 performance path for RayJoin fresh overlay.

It made the fresh writer-free route slower:

```text
0.987424s device-column route
0.893045s host exact pair-id rows route
```

Therefore:

```text
Do not promote --exact-lsi-device-columns as the performance route.
```

### D2. Host row materialization/copy is not the meaningful bottleneck

The exact device-column route measured device-to-NumPy copy at:

```text
~0.000526s median
```

That is three orders of magnitude smaller than the exact LSI phase:

```text
~0.895913s median
```

So the performance gap is not explained by copying pair ids from device to host.
Moving the same exact pairs into a device-column wrapper does not address the
dominant cost.

### D3. The next bottleneck is exact planar-map LSI computation

The fresh writer-free binary route is now dominated by exact LSI:

```text
host exact LSI phase:          ~0.806946s
exact device-column LSI phase: ~0.895913s
AuthorPatch overlay compute:   ~0.0421s
```

The exact LSI phase alone is about `19x` the AuthorPatch full overlay-compute
comparator:

```text
0.806946 / 0.0421 = ~19.17x
```

This is now the central performance fact.

The remaining gap is not writer output, not cached replay, not host pair-id
copy, and not the device-column carrier itself. It is the fresh exact LSI
computation path.

## Rejected Follow-Ups

### R1. Do not continue optimizing cached replay as the main metric

Cached replay is valuable for workloads that repeatedly reuse the same LSI
result, but it is not the cost of a fresh overlay operator.

Optimizing replay cannot close the fresh overlay gap.

### R2. Do not keep moving the same exact pairs between host/device formats

Goal4964 already measured that movement/copy is small. More wrappers around the
same exact pair stream are unlikely to produce a real speedup.

### R3. Do not use candidate device columns as a substitute for exact LSI

Goal4963 already showed candidate device columns are not correctness-equivalent:

```text
candidate_event_count = 20972
exact_lsi_count       = 20860
```

The public sample correctness contract requires exact pair ids.

### R4. Do not claim near-AuthorPatch performance

The current honest fresh comparator is:

```text
~0.893s vs 0.0421s = ~21x slower
```

Any lower headline must clearly state what cost it excludes.

## Candidate Next Technical Directions

The next goal should not blindly implement all of these. It should choose the
smallest measurement-backed step.

### Option A: Single-pass exact pair-id production

Goal4964's native device-column prototype uses count+emit exact passes. A
single-pass exact route could remove one traversal/refinement pass if the native
API can support bounded output safely.

Genericity requirement:

- Output remains `{left_id,right_id}`.
- No RayJoin overlay faces, chains, text, or app-specific output contract in
  the core.

Gate:

- Must preserve exact count/fingerprint.
- Must improve the exact LSI phase against `0.806946s`.
- If it cannot beat host exact pair-id rows, kill it.

### Option B: Exact planar-map LSI predicate/traversal optimization

The exact predicate/traversal path may be doing more work than AuthorPatch or
doing equivalent work less efficiently.

This option measures and optimizes the exact LSI kernel itself:

- candidate count vs accepted exact pairs,
- direct-intersection predicate cost,
- grouped-range traversal behavior,
- duplicate/boundary filtering cost,
- any unnecessary coordinate materialization in the exact path.

Genericity requirement:

- Optimizations must apply to planar-map segment-pair LSI, not to RayJoin
  overlay output.

Gate:

- Must reduce fresh exact LSI phase on the public sample.
- Must keep exact fingerprint.
- Must include at least one synthetic contract test for boundary/shared-endpoint
  semantics.

### Option C: Admit the next large jump needs later Layer-4 pushdown/fusion

If exact LSI remains dominated by unavoidable traversal/predicate work that
RTDL performs after traversal rather than inside the traversal shader, then the
remaining gap belongs to the later data-flow-to-traversal pushdown/fusion line.

This is not a v2.14.3 Layer-1/2 win. It is the future compiler/fusion problem.

Gate:

- This conclusion must be based on a measured breakdown of the exact LSI
  phase, not on intuition.

## Recommended Next Goal

Create the next performance goal as:

```text
Goal4967: Exact Planar-Map LSI Fresh Cost Breakdown And Single-Pass Feasibility
```

Scope:

1. Measure exact LSI phase internals enough to distinguish:
   - count+emit double work,
   - predicate/traversal cost,
   - coordinate/refinement/materialization cost.
2. Prototype only if the measurement identifies a specific removable cost.
3. Keep the output generic `{left_id,right_id}`.
4. Reject RayJoin overlay-specific core changes.
5. Preserve public sample fingerprint.

The immediate Goal4966 should first close the 4959-4965 arc and document the
state honestly.

## Status Of Goals 4959-4965

| Goal | Status | Exit |
|---|---|---|
| 4959 | complete | bad `2.04x` boundary closed |
| 4960 | complete | fresh vs cached same-input measured |
| 4961 | complete | larger representative input blocked by data availability |
| 4962 | not run | blocked by Goal4961 input availability |
| 4963 | complete | exact pair-id device-column design gate |
| 4964 | complete | correctness pass, performance no-go |
| 4965 | complete | bottleneck decision: exact LSI compute is next |

## Not Authorized

- No near-AuthorPatch performance claim.
- No claim that device columns solve fresh overlay performance.
- No claim that cached replay is fresh overlay performance.
- No candidate-equivalence claim.
- No RayJoin-specific core primitive.
- No larger-input claim until the missing representative inputs are restored.
