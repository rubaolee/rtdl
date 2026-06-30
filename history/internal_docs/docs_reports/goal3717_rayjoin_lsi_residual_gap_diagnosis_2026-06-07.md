# Goal3717 RayJoin LSI Residual Gap Diagnosis

Date: 2026-06-07

Status: internal diagnosis after Goal3715. This is not a release packet, not a public speedup claim, not an RTDL-beats-RayJoin claim, not a RayJoin paper reproduction claim, not a broad RT-core speedup claim, not a true zero-copy claim, and not a native default-route authorization.

## Purpose

Goal3715 fixed the old RayJoin LSI correctness blocker:

- RayJoin LSI: `20860`
- RayJoin `-check=true` LSI: `20860`
- RTDL LSI: `20860`
- delta: `0`

The remaining problem is performance. RTDL is close but still slower on the original-RayJoin same-source Brazil sample:

| Route | Query Seconds |
| --- | ---: |
| RayJoin LSI query | `0.000873963` |
| RTDL LSI query | `0.001100961` |

RTDL is therefore `0.794x` RayJoin speed, or about `1.26x` the latency.

This report identifies where that gap lives and what engineering work is most likely to matter.

## Current RTDL LSI Phase Split

From `docs/reports/goal3715_rayjoin_original_same_source_current_a5000/summary.json`:

| RTDL LSI Phase / Value | Number |
| --- | ---: |
| hot query median | `0.001100961` |
| native `candidate_count_pass` | `0.000942941` |
| Python/ctypes/timing residual | about `0.000158020` |
| `left_upload` | `0.0` |
| `candidate_write_pass` | `0.0` |
| `candidate_download` | `0.0` |
| `exact_refine` | `0.0` |
| raw candidates | `20972` |
| emitted exact count | `20860` |
| selected native mode | `count_prepared_left` |

The residual is:

`0.001100961 - 0.000942941 = 0.000158020`

The gap to RayJoin is:

`0.001100961 - 0.000873963 = 0.000226998`

This means:

- Removing all Python/ctypes/timing residual would improve RTDL to roughly `0.000942941s`.
- That would still be about `1.079x` RayJoin's query time.
- Therefore the gap is mostly native traversal/count path, with a smaller but still meaningful host-call residual.

## Negative Probe Already Known

Goal3708 tested disabling candidate telemetry for the exact-count path and found it was slower on the measured packet. Therefore the next move should not be another telemetry toggle.

## Likely Causes

1. **Launch/API residual**: RTDL still measures a Python call into C ABI per query. RayJoin's `Query` timing is inside its native executable.
2. **Generic exact predicate overhead**: RTDL counts exact double segment intersections inside the OptiX any-hit traversal. RayJoin uses its own app-specialized high-precision/scaled predicate and layout.
3. **Generic layout overhead**: RTDL's prepared segment-pair path is app-agnostic and carries generic IDs/exact columns. RayJoin's LSI path is purpose-built around its map representation.
4. **OptiX pipeline/SBT payload shape**: RTDL's generic launch parameters and payload may be larger or less specialized than RayJoin's LSI kernel.

## Recommended Next Engineering Steps

### Step 1: Native Repeated LSI Count Executor

Add a generic prepared segment-pair exact-count repeated executor, or a diagnostic native loop wrapper, that runs the existing prepared-left count path multiple times from one C ABI call.

Purpose:

- isolate Python/ctypes overhead from native traversal time,
- make RTDL timing more comparable to RayJoin's native-internal repeat timing,
- avoid changing exactness or route semantics.

Acceptance:

- exact count remains `20860`,
- selected mode remains generic `count_prepared_left`,
- report gives native-loop per-iteration seconds and Python-call per-iteration seconds,
- no public claim wording.

### Step 2: Predicate/Layout Micro-Diagnosis

If native-loop timing is still above RayJoin, inspect the generic any-hit predicate cost.

Candidate probes:

- compare exact double predicate count against a trusted faster predicate variant on the same mismatching-sensitive set,
- measure payload/counter overhead with raw-candidate count preserved versus exact-only count only if a new probe is justified,
- inspect whether exact coordinate loads are coalesced enough for the same-source sample.

Acceptance:

- any faster predicate must preserve `20860` on same-source RayJoin and `4977` on public 4096-chain CDB,
- any route that regresses exactness stays a negative probe.

### Step 3: Same-Contract Broader Slice

After Step 1/2, rerun:

- original RayJoin same-source sample,
- public CDB 4096-chain packet,
- at least one larger or shifted public CDB slice if available.

Acceptance:

- correctness first,
- RayJoin executable comparison remains separate from all-CuPy same-contract comparison,
- weak rows stay visible.

## What Not To Do Next

- Do not claim RTDL beats RayJoin from Goal3715. LSI is still slower.
- Do not hide PIP count incomparability; RayJoin's timing output still does not print PIP count.
- Do not add RayJoin-specific native ABI names or app-specific map ownership logic.
- Do not spend more time on optional candidate telemetry unless a new measurement contradicts Goal3708.

## Immediate Next Goal

Implement Step 1: a generic native repeated prepared-left segment-pair exact-count diagnostic.

Reason:

It is low-risk, app-agnostic, and answers the most important remaining measurement question: how much of the `0.001100961s` RTDL LSI query is host-call residual versus native traversal/count work?
