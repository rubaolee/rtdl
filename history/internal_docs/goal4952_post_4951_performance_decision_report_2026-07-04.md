# Goal4952 Post-4951 Performance Decision Report

Date: 2026-07-04

Status: completed_pending_review

Requested exit label:

`completed_post_4951_decision__stop_cpu_numba_materializer__authorize_plain_writer_phase_audit`

## Purpose

Goal4952 is a decision goal after Goal4951.

It answers:

> After the compiled generic path-split materializer proved correct but slower,
> what work is still justified, and what work must stop?

This is not an implementation goal. Its purpose is to prevent the same failed
route from being repeated under a new goal number.

## Evidence Chain

### 1. Layer 1/2 Capability Was Real But Did Not Move RayJoin Enough

Goals 4947-4948 proved that RTDL can pass native row/device-column carriers into
Numba continuation code through a generic boundary, including one non-RayJoin
fixture.

Goal4950 closed that line honestly:

- Layer 1/2 = capability success.
- Current RayJoin app-layer Numba helpers = performance no-go.
- The next target, if any, had to be Layer 3 writer/output assembly.

### 2. Goal4951 Gate A/B Was A Valid Generic Spike

Goal4951 first built an internal compiled path-split materializer:

- no public API exposure;
- no `src/rtdsl/**` runtime changes;
- no app-identity tokens in the generic spike;
- non-RayJoin synthetic fixtures passed on the POD with Numba;
- Antigravity approved Gate A/B and authorized Gate C.

That part was useful: it proved the generic compiled path-split boundary is
expressive enough to reproduce the Python generic reference on neutral data.

### 3. Goal4951 Gate C Passed Correctness

The compiled path-split adapter was then wired into the RayJoin Section 5.7
public sample as an app adapter.

It preserved byte-for-byte output:

| Route | Byte Equal | SHA256 |
| --- | ---: | --- |
| plain `section57_overlay.py` | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| compiled path-split first run | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| compiled path-split rerun | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

Correctness is not the problem.

### 4. Goal4951 Gate D Failed Performance

Same-POD, same-data, same-cache writer comparison:

| Route | Writer Seconds | Relative To Plain |
| --- | ---: | ---: |
| plain writer | 2.583328 | 1.000x |
| compiled path-split first run | 4.207148 | 0.614x |
| compiled path-split rerun | 4.155936 | 0.622x |

Approved minimum useful gate:

```text
writer speedup >= 1.10x
```

Actual rerun:

```text
2.583328 / 4.155936 = 0.622x
```

This is a performance regression. The approved kill condition was satisfied.

Antigravity approved the closure as:

```text
approve_goal4951_correct_but_not_faster_stop
```

## Decision

The following route is closed:

```text
app adapter
-> CPU/Numba compiled generic path-split materializer
-> Python/app text formatter
```

It is correct but not fast. It must not be:

- promoted as default;
- exposed as public API;
- cited as a performance win;
- repeated with minor reshuffling.

## Why This Failed

The failure is not mysterious.

The compiled adapter still pays for:

| Group | Rerun Seconds |
| --- | ---: |
| app input construction | 0.323214 |
| compiled generic materialization | 2.389931 |
| app text formatting | 1.306298 |
| final file write | 0.043196 |

The final file write is tiny. The remaining time is structural:

- assembling path intervals;
- carrying descriptor state;
- rebuilding grouped output records;
- formatting paper-specific text lines.

The CPU/Numba materializer moved part of the chain-loop work into a compiled
function, but it introduced enough generic row-buffer/materialization overhead
that the whole writer got slower than the hand-written app path.

## What Is Still Plausible

Goal4951 does not prove all Layer 3 work is dead.

It only rejects one route:

```text
CPU/Numba row materializer wrapper
```

The only remaining plausible performance routes are:

1. **Native / device-resident output-chain construction**
   - A compiled route that owns the structural grouping and row construction
     without round-tripping through Python row materialization.
   - This might be worthwhile if a detailed phase audit shows enough generic
     structure cost to recover.

2. **Stop RayJoin-specific performance work**
   - Keep the current correct paper reproduction as the product result.
   - Do not spend more time chasing an author-level fused C++/CUDA/OptiX writer
     unless the work is generic enough to benefit other apps.

No other path is currently justified.

## What Is Not Authorized

Goal4952 does not authorize:

- another CPU/Numba path-split materializer attempt;
- another downstream generic assembly wrapper;
- native writer implementation;
- device writer implementation;
- public API exposure;
- performance claims;
- putting RayJoin output text format into RTDL core.

## Authorized Next Goal

Authorize only Goal4953:

```text
Goal4953 Plain Writer Fine-Grained Phase Audit
```

Goal4953 must be a measurement goal, not an implementation goal.

It should measure the current plain writer, because the plain writer is still
the fastest known RTDL Section 5.7 route.

Required breakdown:

- chain traversal / control flow;
- intersection grouping lookup;
- path interval construction;
- keep/drop decisions;
- point-id cache lookup/insertion;
- polygon-id cache lookup/insertion;
- coordinate formatting;
- line/header string construction;
- list append / buffer construction;
- final file write.

The purpose is to answer:

> Is there a large generic structural writer cost that a native/device route can
> recover, or is the remaining cost mostly app-specific text/formatting?

## Goal4953 Exit Branches

Goal4953 must exit into exactly one of:

1. `writer_audit_supports_native_generic_writer_goal`
   - A large recoverable generic structural portion exists.
   - Then Goal4954 may design a native/device writer feasibility plan.

2. `writer_audit_shows_app_format_bound_stop`
   - The remaining cost is mostly RayJoin-specific formatting / paper output
     semantics.
   - Stop RayJoin performance work.

3. `writer_audit_inconclusive_redo`
   - Measurements are noisy or insufficient.
   - Redo measurement only; do not implement.

## Explanation For The Owner

Goal4952 says:

- We did not fail correctness.
- We did not fail genericity.
- We failed the specific performance bet.

That distinction matters.

Goal4951 was a good experiment because it tested the most conservative generic
compiled route and killed it with numbers. The next responsible move is not to
invent another implementation immediately. It is to measure the fastest known
plain writer deeply enough to decide whether native/device writer work is a real
generic product investment or just a RayJoin-specific rabbit hole.

## Exit Label

`completed_post_4951_decision__stop_cpu_numba_materializer__authorize_plain_writer_phase_audit`
