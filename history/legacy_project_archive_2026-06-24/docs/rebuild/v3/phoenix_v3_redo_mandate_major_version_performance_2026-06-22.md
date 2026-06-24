# Phoenix V3 Redo Mandate: Major-Version Performance

Date: 2026-06-22
Status: `redo_required`

This document supersedes the scoped `release_ready` interpretation for Phoenix
V3. The current scoped 13-row surface is not sufficient to define V3.

## New Top-Level Rule

V3 major release requires broad V2.x performance superiority.

For V3 to exist as a responsible RTRDL language/runtime release, it must show
serious, same-RT-hardware V3-vs-V2.x performance improvement across the full
benchmark suite. The benchmark apps are not the product. They are the pressure
tests that force the language/runtime to expose general capabilities users can
trust. Row-scoped wins, scoped external review, source-tree setup health, or a
green local test matrix are not enough.

Current machine-readable state:

```text
status: redo_required
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
blocking_reasons:
  - broad_v2x_performance_not_proven
  - serious_all_app_paired_evidence_failed_release_bar
  - current_scoped_13_row_surface_not_v3_major_release
```

## Why The Current Surface Is Not Enough

The current same-RT-hardware paired evidence says:

```text
same_metric_comparison_count: 46
V3 faster by >5%: 10
Within +/-5%: 32
V3 slower by >5%: 4
Geomean V3 speedup vs V2.14: 1.012x
```

That is not a major broad speedup claim. It is mostly parity plus selected
row-level improvements. A language at V3 cannot ask users to accept that as the
main value proposition.

## What Carries Forward

The 13-row Phoenix surface is not deleted. It becomes internal evidence for
what may survive into the rebuilt V3:

- grouped reduction prepared execution;
- AABB candidate stream and native query-handle work;
- RTDBSCAN component-union route;
- Triangle prepared graph chunk;
- RTNN prepared repeat50 ranked summary;
- Barnes-Hut explicit partner/fused route;
- Hausdorff threshold summary;
- Robot collision flag stream;
- Spatial topology-stream supplemental row.

These rows can seed the redo, but they do not authorize V3.

## Redo Exit Criteria

V3 can return to release consideration only after:

1. all benchmark apps are rerun seriously on the same RT hardware as
   language/runtime stress tests, without toy data substitutions;
2. every negative or surprising row is explained in user language;
3. each promoted optimization is expressed as a reusable RTRDL runtime
   capability, not an app-specific patch;
4. broad V3-vs-V2.x performance is materially positive, not 1.01x-style noise;
5. the result is validated by a local gate and external review;
6. public docs say exactly what is proven and what is not.

## Goal-Level Decision Audit

Decision: revoke the scoped Phoenix V3 release interpretation and require a
full V2.x performance redo before V3 can exist.

1. Was I foolish? Yes.
2. If yes, what actions made it foolish? I treated scoped row evidence and an
   external scoped review as if they answered the user's larger V3 question.
3. Was there another path? Yes. I should have made broad V2.x performance the
   hard major-version gate before release wording.
4. Can I now try a different path? Yes. V3 is now blocked as `redo_required`
   until serious all-app V3-vs-V2.x evidence proves it deserves release.
