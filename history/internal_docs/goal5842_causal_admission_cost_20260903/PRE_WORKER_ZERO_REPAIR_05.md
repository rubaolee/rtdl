# Goal5842 V7 pre-worker-zero failure and V8 repair

Date: 2026-09-03

## Immutable V7 outcome

V7 ran from clean source commit
`50c0c12bf4e96991edb2c6dcaca1f93508f87282` with a fresh commit-bound native
build. It failed during the timer-free RTDL identity witness before worker zero
and before any registered timing. The complete create-only root is preserved
at `pod_artifacts/goal5842_v7_preworker_failure.tar.gz`:

- bytes: `3253`
- SHA-256: `6ad034ebfb18e9158fb7a0b610590e25c9653001ccf2fe1d94365b8a97c0dfdc`
- execution-authority file SHA-256:
  `717cdc4db1666c891e8900d9d63e0fa562877b90d5af0b07f8d09036d5dbf821`

The relation CHECK_ON prepared object completed all 72 planned executions.
Every output and traversal receipt passed before the post-loop lifecycle schema
assertion raised. These calls are disclosed untimed engineering evidence only;
they are not a complete witness and cannot enter a V8 estimator.

## Root cause

V7 correctly moved execution-count lookup from the outer generic receipt into
its nested `provider_receipt`, but it classified the nested public provider as
the hidden native owner. That was one abstraction layer too low.

The actual relation and triangle chain is:

1. `PreparedGenericFamilyProgram` emits
   `rtdl.generic_family_lifecycle.v1`;
2. its provider bridge exposes public `PreparedProtocolProgram`, whose receipt
   is `rtdl.v4.public_protocol_lifecycle.v1`; and
3. that public owner internally delegates to relation or triangle native
   owners, whose private receipt schemas are not the generic provider contract.

V7 expected the third layer's relation/triangle schema while reading the
second layer. The counter value was correct, but the schema assertion was not.

## V8 repair boundary

V8 changes the relation/triangle expected provider schema to
`rtdl.v4.public_protocol_lifecycle.v1`. The sphere path remains
`rtdl.v4.prepared_builtin_sphere_owner.v1` because its public prepared bridge
directly exposes that owner receipt. No fallback or list of acceptable schemas
is introduced.

A local test directly instantiates the actual public `PreparedProtocolProgram`
and verifies its receipt schema. Separate helper tests still require the
generic outer schema, nested provider mapping, exact provider schema, and exact
integer count. The independent recount uses the same public boundary but
implements its checks separately.

V8 retains V7's tasks, input bytes, workload sizes, schedules, phase boundaries,
sample counts, statistics, hardware design, and failure policy. It repeats all
290 RTDL and 144 PyOptiX no-registered-timing witness calls before worker zero.

## Claim boundary

V7 is not reclassified as successful and V8 is not called a retry. V7 data are
not pooled. This repair authorizes only one new create-only V8 transaction. It
does not authorize a performance claim, one-generation completion, external
review, or consensus.
