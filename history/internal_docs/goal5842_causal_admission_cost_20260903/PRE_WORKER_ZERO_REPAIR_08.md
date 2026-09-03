# Goal5842 V10 pre-worker-zero failure and V11 repair

Date: 2026-09-03

## Immutable V10 outcome

V10 ran from clean source commit
`3bf4413fab3ce4f95bf6db64f84a4ac03a55e5bd` on the bound RTX 2000 Ada
Generation pod. Stage 00 passed and produced execution-authority internal seal
`17a8a8e4d3a4d99720d94317ae7aac523f4f4eb89be1e2eb52cc2ab01a9f113f`.
Stage 01 then failed before worker zero and before any registered timing.

The complete create-only failure root, driver logs, and authority are preserved
at `pod_artifacts/goal5842_v10_preworker_failure.tar.gz`:

- bytes: `3524`
- SHA-256: `6296e6782bf86f4e41cf069921478731744ec6b0a495bd5a153cbe3e0f6f8b74`
- execution-authority file SHA-256:
  `d2352d6c4a4a06a9d29f7e6d07f275130fe81b3118ed92065c585fdd9ba696fd`
- failure marker SHA-256:
  `71222136e24031c38abfdec3ff4d276187b25b7eb3cacb701b630e05162ae4c6`
- Stage 01 command/stdout/stderr SHA-256:
  `461b879706a94cd4245b788d7053e01be10246a0cb4da9e499147473f72fdfa3`,
  `dba67b7c32e690937efd40cf1cefbfc666b00223c322ee272a1fb00d7d7f0d51`,
  and `b15ad0cb114d5ad67177f0427eb2bdc354a3cb6f510224f537a9e99dfd5c45e2`.

The relation and triangle CHECK_ON/CHECK_OFF loops each completed all 72 calls
per arm. The triangle auxiliary full-output oracle completed one call. The
sphere CHECK_ON call completed and its public output and OptiX traversal
receipt matched before a post-call lifecycle-schema assertion raised. This is
290 complete timer-free RTDL calls. They are disclosed engineering evidence,
not a complete V10 witness and not input to V11 estimators.

## Root cause

The Goal5842 sphere task uses `sphere_any_hit_count_family_route`. Its prepared
provider bridge exposes the selected route owner's receipt schema:
`rtdl.v4.prepared_sphere_any_hit_count_owner.v1`.

The V8 repair record incorrectly stated that this path directly exposed the
legacy `public_builtin_sphere` owner and therefore froze
`rtdl.v4.prepared_builtin_sphere_owner.v1` as the expected string. The V10
witness and independent recount copied that mistaken classification. Existing
Goal5842 tests were tautological: their fabricated sphere receipt copied the
same wrong literal, while their live lifecycle test covered only the relation
and triangle public-protocol owner. A separate Goal5838 test already contained
the correct selected-sphere schema but was not connected to Goal5842.

This is a witness-contract classification defect. It is not an RTDL provider,
GPU, task-correctness, or scientific-estimand failure.

## V11 repair boundary

V11 changes the expected sphere provider lifecycle schema in exactly two
independently implemented consumers: the no-timing GPU witness and the
post-transaction independent recount. A new CPU-only test constructs the real
selected-sphere owner lifecycle state and checks the emitted schema and
execution count. The actual provider/runtime output is unchanged.

V11 also pins the selected sphere prepared-runtime source because its lifecycle
receipt is now an explicit evidence dependency. It retains every task, input,
output contract, workload value, causal estimand, phase boundary, schedule,
sample count, statistic, baseline arm, hardware gate, and failure policy from
V10. The three Goal5838 frozen-core files remain byte-identical.

V11 is not a retry of V10. It is one append-only full replication permitted by
V10's create-only failure marker. It must repeat all RTDL, PyOptiX, and Direct
witnesses before worker zero. No V10 call may satisfy a V11 witness or enter a
V11 estimator.

## Claim boundary

V10 is a pre-worker-zero engineering failure with zero registered timing. V11
has no result until a fresh clean commit-bound transaction completes. One GPU
generation remains insufficient for Goal5842, and no performance, CGO,
external-review, or consensus claim follows from this repair.
