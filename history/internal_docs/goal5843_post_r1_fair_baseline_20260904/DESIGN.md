# Goal5843 Fresh Post-R1 Fair Baseline Design

## Question

After Goal5842R1 removed repeated immutable-input scanning and moved the
ordinary public triangle route to generic device-resident checked-U64
reduction, how expensive is the current public check-on RTDL implementation
relative to a direct CUDA/OptiX implementation and the pinned current NVIDIA
PyOptiX-compatible implementation on the same GPU, input, and public output?

## Scope

The primary task is the frozen 16,384-query weighted triangle all-hit scalar.
The 4,096-by-4,096 bounded relation remains an adverse row-returning negative
control. It must not be represented as using the scalar fast path. The three
arms are Direct CUDA/OptiX, pinned PyOptiX-compatible, and ordinary public
check-on RTDL. No private checker-off path is admissible.

Each of 18 blocks contains every task and arm. All six arm orders are balanced,
task order alternates by block, and each scheduled arm is split into a fresh
first-execution process and a fresh steady process with 8 warmups and 64 timed
executions. Complete execution includes reset, launch-parameter update, the
provider-required OptiX launch count, required public-output transfer, and
status checking. Every provider waits for GPU completion and the required
public output before its timer stops. Independent oracle comparison occurs
after timing.

The primary estimand is the median of 18 within-block RTDL/Direct and
RTDL/PyOptiX ratios for steady triangle execution, with a fixed-seed 10,000-draw
bootstrap interval. Setup and first execution are descriptive secondary
results. Provider-specific setup phases are not claimed to contain identical
hidden work.

Query-upload phase placement differs across providers: RTDL performs its first
query upload in the first complete execution, whereas the inherited Direct and
PyOptiX owners upload during preparation. Therefore setup and first-execution
numbers are descriptive and must not support a causal overhead claim. The
primary steady estimand requires prepared-query reuse in all arms.

## Post-R1 RTDL Gate

The steady triangle RTDL receipt must prove the public v7 scalar path, exact
prepared-query reuse, one OptiX launch, no repeated upload or GAS build, no
host per-ray/event materialization, no role-counter materialization, 12 control
bytes plus 8 scalar bytes returned, and no auxiliary CUDA kernel launch. A
create-only formal Numba leaf cache is populated before worker zero and then
sealed read-only into the execution authority.
The first RTDL receipt separately must expose its nonzero initial query upload;
it must not be mislabeled as a reused-input execution.

Before worker zero, the transaction binds and preserves the exact RTDL native
DSO, its build manifest, the Direct executable, the pinned PyOptiX module tree,
and the loaded CuPy module entry file. The downloaded transaction archive is
accepted only after safe path/type validation, custody-hash verification, a
fresh standard-library recount, and byte-identical pod/local recount output.

## Failure And Claims

There is no registered performance success threshold. Adverse rows are valid
results and cannot be discarded. A worker error terminates the transaction;
there is no retry, and a repair requires a new preregistration. Completion is
internal technical evidence only. Public or manuscript performance wording,
hardware-independent generalization, external review, and consensus remain
explicitly unauthorized.

## Pre-Worker-Zero Repair History

The first sealed preregistration at commit `bc03f357` was superseded before
formal worker zero. A timer-free provider preflight produced the correct RTDL
triangle scalar and valid nested provider receipt, but the Goal5843 worker
incorrectly read `provider_execution` from the outer generic lifecycle and
assumed the generic result exposed a provider-only `details` field. No formal
transaction root, worker-zero marker, or timing sample existed. Repair 01
changes only the Goal5843 harness and tests, preserves the frozen Goal5838
core byte-for-byte, records the superseded seals, and requires this new v2
preregistration before formal execution.

The v2 timer-free preflight then exposed a separate relation-control harness
assumption: bounded relation has no triangle-style provider execution
extension. Its generic result does carry a self-digested traversal receipt
binding two successful OptiX launches, route, native DSO, and complete output.
Repair 02 therefore keeps the runtime unchanged and makes the Goal5843
relation boundary explicitly carry and validate that generic receipt. The v2
seal is preserved in Repair 02, and formal execution requires this v3
preregistration.
