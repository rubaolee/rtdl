# Strict self-review — Goal5830 public V4 stable-sort demo

Date: 2026-08-30  
Scope: bounded functional demo and concrete CP002 value witness  
Verdict: **P0=0 · P1=0 · P2=5 · P3=1**

## Adversarial questions

### Did we disguise a host sort as RT sorting?

No.  The host computes a monotone stable key but not rank.  Rank is derived
from the OptiX-produced predecessor relation, then records are scattered in
linear time.  Python `sorted()` is only a postexecution oracle.  The expected
rows are not passed to `execute`.

### Did we prove RTDL verifies sorting?

No, and the code now demonstrates the boundary.  A complete ten-row relation
that reverses the two equal-valued records passes the generic protocol shape,
produces unique ranks, and returns the wrong stable order.  Only the
application oracle detects it.  `application_mapping_verified_by_rtdl=false`
is carried in every result.

### Is the CP002 defect real or host-modeled?

It is now both modeled and executed.  The PyOptiX control compiles two PTX
programs whose CUDA source differs in exactly one line.  The
`primitive_index` version returns the exact predicted wrong relation with CUDA
success, no exception, and no OptiX fatal/error.  The complete context-message
list and all API-returned pipeline-log strings are preserved; the latter are
not claimed to be untruncated compiler transcripts.  The RTDL contract test mutates the exact attr0
ownership leaf to `primitive_index_u32` and gets the sole reason
`CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH`.

### Is the physical-order attack hidden by identity order?

No.  The main indexed order is `(2,0,3,1)`, not `(0,1,2,3)`.  All 576 pairs of
indexed/source permutations preserve the correct logical relation, while the
primitive-index substitution produces a different exact relation.

### Can overflow leak a plausible partial sort?

No in the tested public path.  Capacity 10 succeeds.  Capacity 9 raises exact
`BoundedRelationError(code=capacity_overflow,path=rows)` with ten unique rows
observed and nine materialized; no result is returned.

## Initial review findings and closure

1. **P1: CP002 existed only as a modeled postprocessing attack.** Closed by
   the real PyOptiX one-line device mutation and a same-declaration RTDL CP002
   gate test.
2. **P1: the application-theorem negative control was invalid.** It originally
   constructed 11 rows against capacity 10 and expected the consumer to fail.
   Closed by a complete, exactly ten-row wrong total order that the rank
   consumer accepts but the stable oracle rejects.
3. **P1: PyOptiX diagnostics were filtered too aggressively.** Closed by
   publishing all 31 context messages and every module/program-group log
   string returned by the API; the claim is limited to no fatal/error rather
   than an unqualified validation “PASS.”
4. **P1: remote success was not locally preserved.** Closed by copying result,
   stdout, current source archive, native, build log, both CUDA sources, both
   PTX files, PyOptiX baseline/control and compatibility authority into a
   19.1 MB local evidence tree, then verifying it without RTDL/PyOptiX imports.
5. **P2: maximum float32 boundary was CPU-only.** Closed by adding and passing
   the Home GPU case.
6. **P2: overflow caught arbitrary exceptions.** Closed by exact type, code,
   path and observed/materialized/capacity literals.
7. **P2: huge integers and boolean permutations leaked nonuniform behavior.**
   Closed by stable application diagnostics and tests.
8. **P2: proof semantics could be overread.** Closed by the explicit result
   literal `INHERITED_FROZEN_DIGEST__PROOF_BYTES_AND_SEMANTICS_NOT_REVALIDATED_BY_GOAL5830`.
9. **P2: example hashing could target the wrong working-directory file.**
   Closed by hashing the actual imported module path.
10. **P2: the independent verifier did not freeze the exact 21 IDs or derive
    the wrong rows from physical order.** Closed by requiring the exact unique
    five fixed plus sixteen random IDs and independently reconstructing CP002
    rows from each preserved physical-order mapping.
11. **P2: the verifier under-checked identity/source claims.** Closed by
    cross-checking every result/lifecycle executable identity, the preserved
    PyOptiX baseline, compatibility authority, base CUDA, PTX identities, an
    AST proof of the one-argument `execute(BoundedRelationBatch(...))`
    boundary, and a static no-RTDL-import scan of the PyOptiX control.

## Remaining P2 limitations

1. **No RT-core hardware evidence.** GTX 1070 proves OptiX execution semantics,
   not RT-core execution or performance.
2. **No performance result.** The design materializes up to `O(n²)` rows; zero
   timings were registered.  It must not be compared with CUB/Thrust as a
   production sorter.
3. **No new-family generalization.** Sorting reuses the existing
   custom-AABB bounded-relation family; it is not a third protocol family.
4. **No external user evidence.** The authors wrote the mapping, tests and
   oracle.  This does not answer usability or third-party programmability.
5. **PyOptiX environment is the frozen v1.3 source built against OptiX 9.0
   headers.** It supports this host-binding/semantic control, not a stock
   PyOptiX 9.1 execution claim.

## P3

The first PyOptiX control attempt assumed an older baseline exposed `nvrtc` as
a module global.  The current baseline intentionally keeps compiler imports
out of the runtime graph.  The attempt stopped before a pipeline or
application launch.  The repair imports `cuda.bindings.nvrtc` inside the
control compiler function, matching the current baseline.  The empty stdout
and partial single source file are preserved.

Earlier RTDL trial files with empty stdout are also preserved, but their stderr
was not durably captured; no scientific conclusion relies on them.  Two
subsequent complete predecessor runs and the controlling environment-bearing
V4 run succeeded.

## Final honesty judgment

The demo is complete and useful **only** as a small executable explanation of
the protocol-integrity contribution.  It turns the abstract statement
“nominal payload/attribute meaning is not the same as machine width” into a
sorting failure a general systems reader can understand.  It does not repair
the paper's unseen-application or usability evidence gaps and must not be used
to imply them away.
