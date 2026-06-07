# Goal3693 RayJoin LSI Mismatch Localizer

Date: 2026-06-07

## Purpose

Goal3691 found the live RayJoin same-source blocker:

- RayJoin LSI checked count: `20860`
- RTDL exact prepared LSI row count: `20859`

Goal3693 localizes that one-row gap. The goal is not to special-case RayJoin. The goal is to identify the generic segment-pair contract requirement RTDL needs before same-source RayJoin LSI can be treated as solved.

## Evidence

Compact A5000 artifacts:

- `docs/reports/goal3693_lsi_mismatch_localizer_a5000/lsi_pair_set_diff_summary.json`
- `docs/reports/goal3693_lsi_mismatch_localizer_a5000/missing_pair_geometry.json`
- `docs/reports/goal3693_lsi_mismatch_localizer_a5000/missing_pair_precision_probe.json`
- `docs/reports/goal3693_lsi_mismatch_localizer_a5000/rayjoin_lsi_dump.log`

The pod used the same RayJoin checkout and sample inputs as Goal3691:

- county: `/root/RayJoin/test/dataset/br_county_clean_25_odyssey_final.txt`
- soil: `/root/RayJoin/test/dataset/br_soil_ascii_odyssey_final.txt`

RayJoin was instrumented locally on the pod to dump its LSI pair queue after the checked query. That instrumentation only affected the external RayJoin checkout and is not RTDL source code.

## Pair-Set Result

RTDL row ids are one-based relative to the zero-based RayJoin edge ids. After normalizing RTDL ids by subtracting one from both sides:

| Comparison | RayJoin pairs | RTDL pairs | Missing from RTDL | Extra in RTDL |
| --- | ---: | ---: | ---: | ---: |
| RTDL `left_id - 1`, `right_id - 1` | `20860` | `20859` | `1` | `0` |

The one missing RayJoin pair is:

```text
(230119, 226567)
```

This means the Goal3691 LSI mismatch is not a broad indexing, ordering, or grouping failure. It is a single segment-pair predicate/candidate-emission corner case.

## Missing Pair Geometry

RayJoin zero-based left edge `230119`:

```text
(-53.129979511, -28.763491093) -> (-53.123623658, -28.755028817)
```

RayJoin zero-based right edge `226567`:

```text
(-53.130100000, -28.756700000) -> (-53.128600000, -28.840900000)
```

Exact high-precision parametric intersection:

| Field | Value |
| --- | ---: |
| denominator | `-0.000547856236600000` |
| `t` on left segment | `0.00007568719169345676...` |
| `u` on right segment | `0.08064670444292429...` |
| intersection x | `-53.1299790299433356...` |
| intersection y | `-28.7634904525140942...` |

The orientation signal at the left endpoint is tiny:

```text
left_a_vs_right = -4.1465700000E-8
```

So this is an endpoint-near intersection. It is exactly the kind of pair where a fast float candidate predicate and a scaled/high-precision predicate can disagree.

## Precision Probe

The exact predicate classifies the pair as a hit:

```text
den = -0.000547856236600000
t   =  0.00007568719169345676...
u   =  0.08064670444292429...
```

A simulated float32 device-style predicate over rounded coordinates classifies it as outside the segment because `t` flips below zero:

```text
den = -0.0005477989325299859
t   = -0.00018010620260611176
u   =  0.08066143840551376
```

This explains the shape of the mismatch: if the RTDL device candidate path drops the pair in float precision, the later host double refinement cannot recover it because the candidate row was never emitted.

## Design Finding

RTDL needs a generic robust segment-pair candidate-emission contract for near-boundary intersections.

Good directions:

1. emit ambiguous near-boundary candidates from the native traversal path and let a host or partner exact-refine contract decide them,
2. add a generic high-precision or scaled segment-pair predicate mode for candidate emission,
3. expose typed ambiguity/status columns such as `candidate_precision_status`, `endpoint_near_status`, or `refine_required`,
4. keep all RayJoin map, CDB, and query names outside the native ABI.

Bad direction:

- adding a RayJoin-specific exception or app-shaped native entry point.

## Boundary

This report does not authorize:

- release,
- default-route promotion,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- public speedup claims,
- broad RT-core claims,
- true zero-copy claims.

It authorizes only this internal engineering conclusion: the same-source RayJoin LSI row-count gap is localized to one endpoint-near segment-pair candidate that exact arithmetic includes and float32-style candidate emission can exclude.

## Next Work

Recommended next goals:

1. define a generic robust segment-pair candidate predicate policy,
2. implement an app-agnostic ambiguous-candidate or high-precision candidate-emission path,
3. rerun the same-source RayJoin LSI pair-set probe and require exact pair parity before timing claims,
4. then optimize LSI performance against RayJoin's original query time.

