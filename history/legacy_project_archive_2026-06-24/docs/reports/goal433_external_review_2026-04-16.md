# Goal 433 External Review: v0.7 Native Prepared DB Dataset Contract

Date: 2026-04-16
Reviewer: External AI (Claude Sonnet 4.6)

## Is the native prepared DB dataset contract the right next architecture?

Yes. The Goal 432 data makes the diagnosis unambiguous: across all three RT
backends and all three query types, prepare time is ~2.5s while execute time
is ~0.04–0.09s. Python-side normalization, encoding, and ctypes marshaling own
roughly 97% of RTDL wall time. Moving all of that into a native prepared dataset
handle — built once, queried many times — is the only viable path to competitive
repeated-query performance. The "build once, query many" model is structurally
correct for this problem.

## Are the boundaries honest?

Yes. The honesty section explicitly disclaims the four things that are easiest to
oversell: RTDL becoming a DBMS, replacing PostgreSQL, supporting arbitrary SQL,
and the Goal 432 prepared-execution path already satisfying this contract. The
first-wave deferrals (text search, SQL LIKE, null-heavy semantics, float aggregate
parity, multi-column group keys) are enumerated rather than quietly omitted. The
Python/native split is stated clearly: Python retains API call, schema declaration,
backend selection, query object construction, and lifetime handle; everything
computational moves native.

The performance gate for Goal 437 is honest in a different direction: it requires
measurement of build/setup time, query-only time, total batch time, and break-even
query count, but deliberately does not pre-commit to a passing threshold. This is
appropriate for a contract goal — the contract defines the measurement model, not
the result.

## Material design gap?

One open risk: the native ABI contract specifies what the native handle owns and
what the query calls accept, but does not specify the Python-to-native data
transfer protocol (how rows and column buffers cross the boundary at dataset
creation time). The current prepare phase is ~2.5s largely because Python does
the encoding work. If the new design still requires Python to copy or marshal large
row buffers into native memory via ctypes/cffi before native ingestion begins, the
transfer overhead could become the new bottleneck instead of the encoding. This
is not a design flaw in the contract — it is an implementation risk that Goals
434–436 will need to address explicitly. The contract should survive as written,
but the implementation goals should not assume the transfer is free.

No other material gap. The correctness gate coverage (conjunctive_scan,
grouped_count, grouped_sum against Python truth, direct backend, PostgreSQL on
Linux, and repeated-query stability) is complete for the first wave. The
performance gate structure (build once, batch of queries, break-even count) maps
directly onto the problem the Goal 432 data exposed.

## Verdict

ACCEPT
