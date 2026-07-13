# Call For Review: Goal5086 Public RTDL API Surface Audit

Date: 2026-07-07

## Requested Verdict Label

```text
approve_goal5086_public_rtdl_api_surface_audit
```

## Review Scope

Please review:

```text
history/internal_docs/goal5086_public_rtdl_api_surface_audit_2026-07-07.md
src/rtdsl/__init__.py
src/rtdsl/optix_runtime.py
src/rtdsl/device_column_row_buffer.py
src/rtdsl/device_ordering.py
src/rtdsl/aggregate_hierarchy.py
Paper-reproduction-apps/README.md
Paper-reproduction-apps/rayjoin-paper/
Paper-reproduction-apps/rt-barneshut-paper/
```

## Context

v2.14.5 is intended to generalize from two paper apps rather than continue
app-specific debugging. Goal5085 introduced a shared status vocabulary for
paper apps. Goal5086 audits which RTDL APIs should be treated as public
language surface, experimental public-contract surface, legacy naming debt, or
app-owned assets.

The central principle is:

```text
RTDL is the generic language/system.
RayJoin and RT-BarnesHut are paper apps on top of RTDL.
```

## Review Questions

1. Does the audit correctly classify planar-map LSI/PIP as public,
   documentable generic RTDL primitives with OptiX/backend limitations?
2. Does it correctly classify `AggregateHierarchy3D` and the reference
   aggregate frontier reducer as public documentable generic RTDL APIs, while
   limiting Numba to optional parity/prototype status?
3. Does it correctly keep `device_column_*` row-buffer/handoff APIs in the
   advanced or experimental bucket rather than overclaiming zero-copy or
   whole-app speedup?
4. Does it correctly keep `device_order_by` as public-contract but not yet
   release-authorized, given `release_authorized: False` and the single
   supported signature?
5. Does it correctly prevent `device_group_by` from being documented as public?
6. Does it correctly identify RayJoin-named native/core symbols and
   `rtdsl.rayjoin_overlay` as legacy/compatibility/naming debt rather than
   first-class public language APIs?
7. Does it correctly keep RayJoin workflow, author comparator, output-chain,
   and dataset-specific choices as app-owned assets?
8. Does it correctly keep RT-BarnesHut prepared-state readers, author
   comparators, sentinel normalization, and force-output bridge as app-owned
   assets?
9. Does the audit avoid using the two successful paper apps to overclaim full
   paper reproduction or public performance?
10. Is Goal5087, a unified paper-app skeleton with required status and claim
    boundary fields, the right next step?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 10 review questions
