# Goal5851 Triangle Exact-Replay Repair

Date: 2026-09-06

## Status

`SUCCESSOR_TRANSACTION_1_RETAINED_FAILED__SECOND_GENERIC_REPAIR_IN_PROGRESS`

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

The in-progress successor caches only an identity shortcut to the already
digest-committed immutable batch. A different object, including an equal-byte
object, still enters the existing digest equality path. Any native or oracle
failure clears both forms of Python reuse eligibility. The CUDA context guard
now skips selection and restoration only when the prior context is exactly the
retained context; null or different contexts retain the old select-and-restore
behavior, including restoration after an exception.

These changes add no application vocabulary, formula, task dispatch, timer
movement, workload change, Direct change, or threshold change. The directly
affected local suite currently passes 121 tests with 3 expected skips. GPU
native build and a same-machine balanced public/Direct diagnostic remain
required before this second repair can be called effective.
