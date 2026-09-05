# Goal5845 engineering log

## Scope

Goal5845 addresses only the ordinary prepared public path for canonical bounded
relation rows. It is a successor to, not a rewrite of, Goal5843.

## Sequence

1. Profiled native, owner, protocol, family bridge, public family, and explicit
   diagnostic layers.
2. Identified status/counter materialization, duplicate row conversion, and
   repeated immutable proof/output work as avoidable steady costs.
3. Added generic native relation v8 compact execution/audit and exact validated
   immutable row transport.
4. Preserved the v3 diagnostic path behind `include_diagnostics=True`.
5. Added fail-closed unit tests for receipt fields, source generations, output
   changes, replay, public/family type admission, and ABI compatibility.
6. Froze the formal design and thresholds before the GPU transaction.
7. Built a fresh DSO from clean commit `22c6a4502`; two setup checks refused
   malformed commands before any timing worker existed.
8. Passed both untimed one-sample preflight arms with identical output hashes.
9. Ran all eight balanced alternating blocks and retained all samples.
10. Downloaded every worker, preflight, build, status, and symbol record.
11. Added a standard-library-only recount authority and hostile mutation tests.

## Frozen primary outcome

- RTDL pooled median: 366.340 us.
- PyOptiX pooled median: 3,486.126 us.
- Median within-block RTDL/PyOptiX: `0.1049444491x`.
- Reciprocal exact-arm result: `9.5288508222x`.
- Worst block RTDL/PyOptiX: `0.1073019810x`.
- RTDL public/direct native median block ratio: `1.3291058851x`.
- Samples: 1,024 per arm, zero discarded.

## Boundary

All numbers are internal engineering evidence. External review and consensus
are pending. The result must always be described as prepared steady execution
for the exact frozen task and pinned PyOptiX compatible-API arm.
