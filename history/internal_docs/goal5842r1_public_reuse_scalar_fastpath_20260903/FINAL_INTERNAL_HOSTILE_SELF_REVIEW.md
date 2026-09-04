# Goal5842R1 final internal hostile self-review

Date: 2026-09-04

## Verdict

**Accept for internal implementation-repair completion. Reject public or
manuscript performance claims until a fresh fair baseline and external review
exist.**

Severity count: P0=0, P1=3, P2=6, P3=2.

The code addresses a real architecture defect rather than a cosmetic timing
change. It retains public admission, adds explicit validated formal-leaf reuse,
keeps prepared target/query state, executes generic device-resident checked-U64
reduction, and returns only the requested scalar. Three complete repeats match
exact oracles and expose receipts consistent with that boundary.

## P0 findings

None found. No incorrect result, app-specific engine semantic, frozen-core
mutation, or false accepted receipt is known in the reviewed scope.

## P1 claim blockers

### P1.1 No fresh fair three-provider baseline

R1 does not rerun Direct CUDA/OptiX and PyOptiX-compatible arms from the same
new source transaction. Comparing the new 0.289-0.295 ms medians to formal V12
is useful diagnosis on the same GPU, but it is retrospective and crosses
transactions. It cannot support a public RTDL-versus-provider ratio.

Required action: create a separate preregistration, freeze one implementation
commit and output contract, then run all provider arms without discarding
adverse rows.

### P1.2 R1 evidence is one-machine and post-diagnostic

V8, V9, and V10 use the same RTX A6000 UUID. They show repeatability, not
cross-generation replication. V7-V10 were run after V6 exposed the bottleneck,
so this is intentionally adaptive engineering evidence rather than a
prospective performance experiment.

Required action: describe R1 as implementation repair. If a cross-generation
performance statement is needed, include the same frozen fresh baseline on a
second architecture.

### P1.3 No independent external review or consensus

Travel constraints explicitly deferred Claude/Gemini review. Internal hostile
review cannot substitute for independent review, and AI review cannot
substitute for Goal5841 human authoring evidence.

Required action: obtain external review after the evidence packet is frozen;
do not backfill an external verdict into this internal authority.

## P2 engineering limitations

### P2.1 Fast reuse requires exact published objects

The O(1) route requires the same query tuple and the same metadata value tuple
objects. An equal-but-distinct tuple is correctly revalidated and reuploaded.
This is safe and explicit, but users who reconstruct equal batches do not get
the fast path.

### P2.2 Formal-leaf cache hits remain expensive

Content-addressed leaf reuse reduces roughly 1.2 s compilation to roughly
0.13 s materialization, but executable reconstruction and validation remain.
The current cache is not a complete prepared-executable cache.

### P2.3 GPU runs used an unsealed development cache

The runner intentionally creates then reuses a fresh content-addressed cache.
Unit tests cover sealed read-only manifest behavior, but V8-V10 do not measure
a deployment-style sealed cache. No deployment startup claim is authorized.

### P2.4 Prepare timings are order-confounded

The scalar owner is prepared before the diagnostic owner in the runner. The
large scalar-prepare value can include first-owner CUDA/OptiX context costs;
the two prepare numbers must not be compared as route effects.

### P2.5 Row-returning relation continuation remains unresolved

The bounded-relation probe verifies cross-family cache correctness but still
returns, sorts, and validates 4,096 rows at about 13 ms. Triangle scalar
results do not generalize to row-heavy contracts.

### P2.6 Native v7 was reused rather than rebuilt for R1

R1 binds the exact previously built DSO SHA-256 and exercises its existing
generic v7 symbol. This is appropriate because the fix is primarily public
lifecycle and host-runtime wiring, but a clean-install artifact evaluation
must rebuild or independently attest that DSO.

## P3 evidence-quality limitations

### P3.1 V4 cleanup crash remains a disclosed incident

V4 first raised a deterministic Python `TypeError`, then reported status 139
during interpreter cleanup. The accepted runs do not reproduce the crash, but
the event was not reduced to an independent native destructor bug. The failure
record remains mandatory.

### P3.2 Layer profiler uses private internals

V6/V7 call provider and native layers directly for attribution. Those paths
are diagnostics only; bypassing the public audit is not a supported execution
mode and cannot be recommended to users.

## Hostile questions

### Was admission weakened to obtain the result?

No. The public lifecycle still performs admitted-program validation and opens
the traversal audit. R1 reuses state only after a successful execution has
published exact immutable objects and the native digest confirms ownership.
The private audit-bypass layer exists only in the diagnostic profiler.

### Is Python identity being mistaken for content equality?

No. Identity is deliberately a necessary condition for the zero-scan path,
not a proof for arbitrary mutable objects. Public constructors canonicalize the
batch into immutable tuples. Equal replacement tuples miss and undergo full
typed validation, digest construction, upload, and commit.

### Was host work merely hidden from the timer?

No for steady execution: the timed public call includes Python dispatch,
audit, native launch, compact status validation, scalar download, result
construction, and audit commit. Materialization and prepare are reported
separately rather than hidden. The first execution still records query upload.

### Is the reduction application-specific?

No. The native route knows triangle intersections and generic checked-U64 sum
or product-sum. Query weights are metadata selected by the admitted reducer
schema. No graph, database, force law, or benchmark name enters the operation.

### Does 0.29 ms prove RTDL beats Direct or PyOptiX?

No. Only a fresh same-transaction provider baseline can answer that question.
R1 proves that the specific 23 ms Python scan and host-vector lowering are not
necessary properties of the public RTDL design.

## Final boundary

Accepted statement:

> On one RTX A6000 engineering environment, three complete nonformal repeats
> of the repaired public triangle scalar route matched the exact oracle,
> recorded one OptiX launch with reused device inputs and only compact scalar
> output, and had 0.289-0.295 ms steady medians. Layer diagnostics attribute
> the removed approximately 23 ms to repeated Python input scanning.

Rejected statements:

- RTDL is 80x faster in a fair provider comparison.
- RTDL now beats Direct CUDA/OptiX or PyOptiX.
- The result is hardware-independent or representative of arbitrary apps.
- R1 proves the language is easy to use.
- External review or consensus is complete.

The implementation repair may be merged and used as the basis of a fresh
formal baseline. The claim blockers above remain open manuscript gates.
