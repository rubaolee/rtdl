# Goal5851 Triangle Exact-Replay Repair

Date: 2026-09-06

## Status

`SUCCESSOR_TRANSACTION_1_RETAINED_FAILED__THIRD_REPAIR_NONFORMAL_GATE_PASS__CLEAN_FORMAL_REQUIRED`

This document records a pre-freeze engineering repair. It does not complete
Goal5851 and does not authorize a public or manuscript performance claim.

## Trigger

The retained RTX 3090 transaction at source commit
`c4351f6120d1d73d7c2b72ff4d61ad747061f836` completed all 512
instrumentation workers and all 80 formal workers with no retry or discard.
Independent recount found one failed gate:

- triangle prepared public RTDL median: 67,051 ns;
- triangle Direct OptiX median: 54,029 ns;
- RTDL/Direct: `1.245276x`, above the frozen `1.20x` limit;
- relation RTDL/Direct: `1.120143x`, passing;
- every other retained gate passed.

The failure archive is immutable adverse evidence. Its SHA-256 is
`0997542ff5d3638baba4771b3f83776fe1c69043dc29c48d1634af9494e20b83`.
It must not be retried, discarded, relabeled, or pooled with a successor.

## Root Cause

The exact prepared triangle replay still crossed the Python/native boundary
through the v7 ABI with sixteen arguments. Seven host query columns and the
optional multiplier column were already device-resident and were not uploaded,
but their ctypes pointers were nevertheless selected and passed on every
application execution. Query-cache digest validation had already been fused
inside the native owner lock, so these host pointers were redundant on exact
reuse.

This is fixed host/runtime overhead, not RT traversal work and not application
math. The Direct arm has no equivalent dynamic host-column argument surface.

## Repair

The additive v9 ABI
`rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v9` accepts only:

1. prepared owner token;
2. query count and generic multiplier-mode bit;
3. the exact 32-byte committed cache digest;
4. scalar, compact-status, operation-receipt, and error outputs.

The first execution and every changed batch continue through v7, upload and
validate all packed columns, and commit the digest only after successful native
status and optional Python oracle validation. An exact cached replay goes
through v9. The native owner verifies, while holding its execution mutex, that
the query inputs and multiplier inputs exist, their count matches, the cache is
committed, and the supplied digest is byte-identical. Any native or Python
failure clears Python reuse eligibility so the next execution rebuilds through
v7.

The implementation is app-free: it names a prepared triangle-reduction family,
typed query columns, multiplier mode, cache identity, and scalar/status
outputs. It adds no graph, sphere, collision, database, or workload formula.

## Local And Pod Verification

The directly affected local suite passed 98 tests with 3 expected skips:

```text
tests.goal5801_rtdlexe_runtime_test
tests.goal5842_prepared_cache_commit_test
tests.goal5803_runtime_overflow_hostile_test
tests.goal5844_compact_execution_stamp_test
tests.goal5848_relation_fused_reuse_digest_test
tests.goal5851_triangle_fused_replay_test
```

On RTX 3090, CUDA 12.8, OptiX 9.0, driver 580.159.03, compute capability 8.6,
the dirty exploratory AOT DSO built successfully with both v7 and v9 exported.
The build manifest reported all required symbols exported and all exports
allowlisted. The DSO SHA-256 was
`72b20ccdd154058f82a318089600295e3cb3d1391986122b34a2beb080a86c1d`.
The corresponding 73-test pod subset passed.

An explicitly nonformal paired diagnostic used the same DSO, same composed PTX,
same 16,384-query weighted workload, separate prepared tokens, 12 alternating
blocks, 64 warmups, and 512 retained executions per arm per block. Every v9
block was faster than v7:

- v7 median of block medians: 69,909 ns;
- v9 median of block medians: 68,196 ns;
- median within-block v9/v7: `0.9773827189x`;
- worst within-block v9/v7: `0.9857246693x`;
- median reduction: 1,713 ns.

The downloaded diagnostic JSON SHA-256 is
`cf35507106b774ac81e2af17ab57545ca9ed50a50ef0ff89644a541959d39d56`.
It is stored outside Git under
`/Users/rl2025/RTDL_evidence/goal5848/goal5851_v9_ampere_nonformal/`.

## Claim Boundary

The paired result proves that the intended v9 path executes real OptiX work,
returns the correct scalar, preserves per-execution native receipts, and lowers
host overhead relative to v7. It is not a formal threshold evaluation because
the DSO was built from an intentionally dirty exploratory checkout and the
diagnostic used an internal construction path.

In particular, the 1,713 ns reduction must not be subtracted from an older raw
Direct timing to manufacture a passing ratio. A clean successor source must be
measured against Direct in the same balanced transaction.

## Required Next Gate

1. Commit the reviewed repair as a new source identity.
2. Build a clean minimal AOT DSO and fresh relation/triangle candidates.
3. Run a nonformal same-machine balanced RTDL/Direct comparison first.
4. Continue optimization if triangle does not clear `1.20x` with useful margin.
5. Only then preregister and execute a wholly fresh two-generation transaction.
6. Preserve the passing Ada result for `c4351f612...` as historical evidence;
   it cannot serve as generation A for a changed successor source.

## Clean Successor Transaction 1

The v9 repair was committed and pushed as
`12ab7b49c18f139543c236981e9dc43f5ddf15c8`, tree
`7933d6fdcb3db5c548546360658b5200e14c5da1`. A fresh RTX 3090 transaction
completed all 512 instrumentation workers and all 80 formal workers with zero
retry or discard. The independent recount correctly rejected the transaction:

- triangle public RTDL median: 65,263 ns;
- triangle Direct OptiX median: 53,385 ns;
- triangle median within-block RTDL/Direct: `1.220467x`, still above `1.20x`;
- relation median within-block RTDL/Direct: `1.134680x`, passing;
- triangle successor/predecessor: `0.979742x`, passing;
- relation successor/predecessor: `0.617216x`, passing.

The complete failure archive SHA-256 is
`182043089d16d36cda9f613c86d3592b3bbe7b7bcaa1bb843ab9ff4441acfe60`.
It is retained outside Git under
`/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_transaction1_failure/`.
It may not be retried, relabeled, pooled, or used as a passing generation.

## Second Generic Repair

The first v9 transaction left roughly 1.2 microseconds to the unchanged
triangle public/Direct threshold. Two generic fixed-cost sources remained:

1. The public owner reconstructed an exact-byte replay key and multiplier mode
   for every call even when the caller supplied the same immutable batch object
   that had already completed native digest commit.
2. `ScopedRtdlCudaContext` called `cuCtxSetCurrent` twice per execution even
   when `cuCtxGetCurrent` reported that the retained RTDL primary context was
   already current on the calling thread.

The committed successor caches only an identity shortcut to the already
digest-committed immutable batch. A different object, including an equal-byte
object, still enters the existing digest equality path. Any native or oracle
failure clears both forms of Python reuse eligibility. The CUDA context guard
now skips selection and restoration only when the prior context is exactly the
retained context; null or different contexts retain the old select-and-restore
behavior, including restoration after an exception.

These changes add no application vocabulary, formula, task dispatch, timer
movement, workload change, Direct change, or threshold change. They were
committed and pushed as `f65d93d4e5a7d5c50a270ace0e3edef0ec9295d6`,
tree `142b27d531628611478c51724911f835074f799f`.

A fresh clean native build on the RTX 3090 exported the required v9 ABI and
produced DSO SHA-256
`9e8f280d28302cea69d3b7eb49891e8e052148971988ed49b0365ca557d5ac6b`.
An eight-block, balanced, same-machine nonformal RTDL/Direct diagnostic then
retained 512 prepared executions per arm per block:

- public RTDL median: 65,301 ns;
- Direct OptiX median: 53,816 ns;
- median within-block RTDL/Direct: `1.2084110096x`;
- worst within-block RTDL/Direct: `1.2462025435x`.

The Direct and worst-block limits passed, but the primary `1.20x` median limit
did not. This is retained adverse engineering evidence, not a formal
transaction. Its downloaded summary SHA-256 is
`87d0fa3a9c6850c06a246b84cd418a6b84a7842b7debd9fb0829220772bd7bc2`.

## Third Generic Control-Plane Repair

Layer diagnostics localized the remaining public overhead above native v9 to
the Python owner/public control plane rather than traversal. The successor
therefore gives exact prepared replay a dedicated family-level helper after
the ordinary owner checks and non-reentrant lock have succeeded. It
precomputes stable ctypes references and fixed ABI sizes, invokes the same v9
native entry point, validates native status, reconstructs a fresh per-call
deferred operation receipt and compact status, validates the optional exact
scalar oracle, and clears all replay eligibility on any `BaseException`.

The helper does not cache an execution result or receipt, remove a check, move
a timer, change an output, alter the workload, or bypass native context and
owner locking. Native v9 still enters `ScopedRtdlCudaContext`, acquires the
prepared owner's execution mutex, and validates the committed digest, count,
multiplier mode, output pointers, launch status and receipt. A distinct
equal-byte immutable batch still takes the digest-key path once before it can
become an identity replay.

This is an outcome-directed pre-freeze performance repair developed after the
retained failures. It is evidence of implementation engineering for the
admitted triangle-reduction family; it is not prospective evidence that the
sealed compiler core automatically generated an optimization or that the same
optimization generalizes to arbitrary callbacks.

The dirty-runtime exploratory checkout reused the unchanged clean
`f65d93d4e...` DSO and AOT candidates, because this repair changes only Python
control flow. Its fresh eight-block balanced diagnostic retained 512 executions
per arm per block and reported:

- public RTDL median: 63,429 ns;
- Direct OptiX median: 53,879 ns;
- median within-block RTDL/Direct: `1.1839019978x`;
- worst within-block RTDL/Direct: `1.3243602526x`.

Both numerical limits were met in this diagnostic, but the result is not a
formal pass: the runtime checkout was intentionally dirty, one block was close
to the `1.35x` worst-block limit, and no preregistration or transaction
authority was built. The downloaded summary SHA-256 is
`dcea3edf8656c92ca082bb81c0632c2f15641bcda2adab7391b414ccae35d991`.

At this checkpoint, the complete Goal5848-focused local suite passes 128
tests. The selected adjacent suite passes 129 tests with 3 expected skips, and
the selected `python -O` suite passes 84 tests with 3 expected skips. Pod tests
against the exploratory runtime pass 51 tests. Static compilation, fatal Ruff
selectors and `git diff --check` also pass.

## Current Required Gate

1. Commit and push the reviewed third repair as a new exact source identity.
2. Check out that commit cleanly and build a fresh native DSO and fresh AOT
   candidates; do not reuse the dirty-runtime diagnostic as evidence.
3. Execute one wholly fresh RTX 3090 transaction with no retry, discard or
   pooling, and retain a failure archive if any frozen gate fails.
4. If RTX 3090 passes, run the identical final commit on a different RTX
   compute-capability generation and GPU UUID.
5. Only a passing independent cross-generation authority can complete
   Goal5851 and authorize the corresponding bounded paper claim. The older Ada
   pass at `c4351f612...` is historical and cannot be combined with this
   changed source.
