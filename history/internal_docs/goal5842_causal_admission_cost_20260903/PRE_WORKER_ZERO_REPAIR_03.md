# Goal5842 pre-worker-zero repair 03

## Incident

The third Ada transaction root was created on the supplied pod at
`/workspace/goal5842-ada-852318321-transaction03` from clean source commit
`852318321a07ccf3cec54d5eed4c68792786c001`. Stage
`00_bind_execution_authority` passed. Stage
`01_gpu_identity_witness_no_timing` completed relation and triangle
CHECK_ON/CHECK_OFF execution, then remained inside the sphere CHECK_ON call
for approximately 85 minutes at one fully utilized host CPU core.

Because the witness has no observation clock and no formal causal or baseline
worker had started, it was interrupted to obtain a Python traceback. The
create-only failure marker records `worker_zero_reached=false` and permits a
new transaction after repair. Its SHA-256 is
`4bcd197c6dc3810483d5cc42c03d2436b40520926fe9ba81c21c63a7c23b56f2`.
The captured stderr SHA-256 is
`f2d1a8f52a719917092f4d88223dc5a59567819026c1065ef6c4f2df05b42f37`.

The four completed relation/triangle calls were untimed GPU executions. The
sphere call had not reached the native invocation. Together with transaction02,
the cumulative count before the replacement transaction is eight complete,
untimed GPU execution calls and zero registered timing observations.

## Root cause

The sphere fixture used 16,384 queries and 16,384 spheres. The public runtime's
numeric-domain verifier intentionally checks every query/sphere pair with
exact `Fraction` arithmetic before invoking the native backend. The fixture
therefore requested 268,435,456 exact pair checks per ON or OFF execution.
The traceback ended in `verify_motion_segments`, before the native call; this
was neither OptiX compilation nor a GPU hang.

The 16,384 size was not part of a sphere provider-performance comparison.
Sphere is excluded from that cohort because no independent exact Direct or
PyOptiX comparator was frozen. Its role is to contribute a third public route
to the cold admission ablation and to witness exact generated/native/output
identity on a real OptiX execution. Static and batch construction occur before
the registered admission interval.

## Repair

The sphere fixture is reduced to 1,024 queries and 1,024 spheres. Each ON/OFF
execution still performs 1,048,576 exact query/sphere condition checks, then a
complete true-OptiX launch and exact output validation. The route factory,
callback, provider, CHECK_ON/CHECK_OFF construction, causal schedule, phase
boundaries, block counts, statistics, two provider-baseline tasks, failure
policy, hardware gate, and claim ceiling are unchanged.

The witness also emits flush-on-write, untimed task/phase progress records.
Those records contain no clock and do not enter any estimator. They make a
future pre-worker-zero failure attributable without interrupting a silent
process.

This is a real workload change and is not described as a byte-preserving
engineering repair. The new sphere input and oracle hashes are frozen in an
append-only v4 preregistration. The v1, v2, and v3 preregistration files remain
byte-preserved and the complete supersession chain remains verifiable.

## Claim boundary

Transaction03 is an engineering pre-worker-zero failure, not a scientific
failure or performance result. Its interrupted host-side validation duration
is diagnostic only and is not a registered Goal5842 observation. No failed
worker row exists, no row is dropped or replaced, and the replacement
transaction must repeat the complete six-call identity witness before worker
zero.
