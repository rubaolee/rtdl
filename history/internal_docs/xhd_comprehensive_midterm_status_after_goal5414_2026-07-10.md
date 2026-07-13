# X-HD Comprehensive Midterm Status After Goal5414

## Current Verdict

```text
level_b_scalar_strong__full_paper_not_complete__dataset_blocker_still_primary__explicit_lb_fail_closed__generic_trace_contract_has_synthetic_non_app_proof
```

This report supersedes the Goal5408/5411 midterm status packets for current
planning.  It incorporates the external review amendments:

- the post-dataset-blocker `-lb` / full-cover / route micro-engineering line
  was an over-investment with rising risk of implementation-specific reverse
  engineering;
- the current `-lb` line should fail close by default;
- continuing is allowed only through a generic, app-neutral RTDL trace contract
  with independent non-X-HD evidence.

## Core Objective

The project objective remains:

```text
Reproduce the X-HD paper as far as the evidence allows, while improving RTDL as
a general spatial/dataflow system rather than building an X-HD-specific app.
```

The objective has two separate bars:

1. **Paper reproduction bar**: match author/paper behavior on identified
   inputs and figures, with aligned denominators and no hidden regime switches.
2. **System-improvement bar**: extract reusable RTDL abstractions from the app
   pressure tests, with non-X-HD evidence before calling them generic.

## Current Reproduction Status

### Completed / Strong Evidence

**Bounded same-input X-HD value reproduction**

Goals5111-5126 close bounded same-input value reproduction.  The directed vs
symmetric Hausdorff ambiguity was resolved by a discriminating fixture:

```text
directed a->b = 0.5
directed b->a = 9.0
symmetric     = 9.0
author HDResult matched directed a->b
RTDL matched directed a->b
```

**Generic nearest / witness / max-nearest extraction**

Goals5127-5128 extracted the directed-Hausdorff route into reusable generic
nearest/witness/reduction helpers and proved non-Hausdorff use through a
facility-service-radius consumer.

**Level-B representative graphics scalar correctness**

The strongest current representative line is Stanford Dragon / HappyBuddha:

```text
public Dragon -> HappyBuddha input pair
author rerun HDResult ~= paper-branch author log HDResult
RTDL route HDResult matches author rerun
```

This is **Level-B same-source representative scalar evidence**, not exact paper
dataset reproduction.

**More Level-B scalar evidence**

Additional graphics and geo bounded/same-source scalar candidates were run,
including ThaiStatuette variants and bounded WKT fixtures.  These expand
coverage but do not remove the exact-input blocker.

### Not Completed

Full X-HD paper reproduction is **not complete**.

The project still does not have:

- exact paper input files / hashes for all paper workloads;
- exact Figure 5 full matrix;
- Figure 6 exact input proof;
- Figure 7 load-balance matrix;
- Figure 8 radius-strategy matrix;
- Figure 9 auto-tune denominator;
- Figure 10 scalability/overlap matrix;
- Figure 11 same-denominator memory accounting;
- performance parity or speedup ratios with aligned hardware, inputs, runtime
  regime, and denominator.

## Current Performance / Timing Position

The clearest current performance-like evidence is still denominator-limited.

Allowed:

- RTDL route times for specific Level-B candidate routes;
- author `Running.AvgTime` and process wall times as separate columns;
- same-POD diagnostics when explicitly labeled;
- explicit warm / cold / route-only distinctions.

Forbidden:

- author-vs-RTDL ratio when denominator/hardware/phase boundary do not align;
- using author internal kernel time against RTDL end-to-end route time;
- using RTDL early-break scalar routes as exact per-source witness routes.

The Goal5211 early-break route is **exact-value-only**:

```text
per_source_witness_exact = false
409,376 / 437,645 sources early-aborted in the Dragon -> HappyBuddha line
```

This is valid for scalar directed-Hausdorff max-nearest value under its contract,
but it is not exact witness reproduction.

## Dataset Blocker

The decisive blocker remains exact input provenance.

The project has repeatedly confirmed:

```text
public data can support Level-B representative evidence;
public data cannot be promoted to exact paper input without file/hash or
deterministic regeneration provenance.
```

Statistics such as point counts, bounding boxes, or Gini-like summaries are
necessary but not sufficient for exact-input status.

## Strategic Self-Assessment

The external midterm review correctly identified a process failure:

```text
After the dataset blocker was already known, a large number of goals were spent
on -lb / full-cover / native route micro-engineering.
```

This work uncovered real system gaps, but it over-invested in an implementation
stream that is not needed for the scientific scalar HD result and whose main
paper use (Figure 7 / Figure 11) remains blocked by missing exact data and
denominator mismatch.

Therefore:

```text
The current explicit -lb line is fail-closed.
```

Continuing it as an X-HD-specific row-identity chase is not authorized.

## System Improvements Achieved

Despite the route-management mistake, the X-HD line did produce real RTDL
system assets:

- generic pairwise L2 candidate rows;
- generic nearest witness;
- generic max-nearest reduction;
- 3D grid/cell-MBR frontier APIs;
- native 3D cell-MBR frontier collection;
- active-query status machine reference APIs;
- heavy-offload worklist schema and telemetry;
- public route warmup protocol;
- app-owned input front doors for PLY/WKT workflows;
- generic payload-transition trace contract;
- synthetic non-app payload-transition trace summary proof.

The latest system line is:

```text
ACTIVE_QUERY_PAYLOAD_TRANSITION_TRACE_CONTRACT
payload_transition_trace_summary_numpy_columns(...)
```

Goal5414 proves a synthetic non-app trace fixture:

```text
matched = true
raw_transition_row_count = 5
status_count_offloading = 2
status_count_completed = 1
status_count_miss = 1
status_count_aborted = 1
overflow rejection passed
44 nearby tests OK
```

This is not X-HD `-lb` support.  It is the first generic behavior proof for a
future native traversal payload-transition trace stream.

## Major Problems Solved

1. **Directed HD definition solved.**
   Author and RTDL are both locked to directed input1 -> input2 for the bounded
   gates.

2. **Value-level RTDL route established.**
   RTDL can match author scalar HDResult on bounded and Level-B representative
   inputs.

3. **Hausdorff reduced to generic primitives.**
   HD is now an app-level composition over generic nearest/witness/reduction
   helpers, not a privileged core primitive.

4. **Exact-input claim discipline established.**
   Public reconstructions are not promoted to exact paper inputs without
   provenance.

5. **`-lb` fail-close reached.**
   The current frontier/status/full-cover bridge does not recover author rows
   and must not be treated as support.

6. **Generic trace escape hatch defined.**
   A new app-neutral trace contract exists, with synthetic non-app evidence,
   but no backend or X-HD support claim.

## Major Problems Not Solved

1. **Exact datasets remain unavailable.**
   This blocks full paper reproduction and most paper figure claims.

2. **Figure-level reproduction remains open.**
   Figures 5-11 are not fully reproduced under exact paper denominators.

3. **Author RT-core algorithm equivalence is not proven.**
   RTDL matches scalar values in routes, but does not reproduce all X-HD
   internal RT algorithm phases.

4. **`-lb` row identity is not solved.**
   Goal5411 failed the bounded sample-row gate, so current explicit `-lb`
   remains unsupported.

5. **Native payload-transition trace backend does not exist.**
   Goal5413/5414 are contract + CPU-reference summary only.

6. **Performance ratios are not authorized.**
   Denominators remain mismatched for author internal timing vs RTDL route /
   process wall.

## Current Files Of Record

Latest key files:

```text
history/internal_docs/goal5412_xhd_fail_close_or_native_trace_semantics_decision_2026-07-10.md
history/internal_docs/goal5413_xhd_generic_native_payload_transition_trace_contract_result_2026-07-10.md
history/internal_docs/goal5414_xhd_synthetic_payload_transition_trace_fixture_result_2026-07-10.md
history/internal_docs/call_for_review_goal5414_xhd_synthetic_payload_transition_trace_fixture_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5414_synthetic_payload_transition_trace_fixture.json
```

Latest durable memory:

```text
memory/progress.md
memory/todo.md
memory/decisions.md
```

## Next Plan

### Immediate Next Goal

```text
Goal5415_decide_stop_or_bounded_xhd_payload_transition_sample_gate
```

Goal5415 should be a decision goal, not a backend implementation goal.

It must choose one of:

```text
stop_after_synthetic_trace_proof
attempt_one_bounded_xhd_payload_transition_sample_gate
```

Recommended default:

```text
stop_after_synthetic_trace_proof
```

The only reason to attempt a bounded X-HD gate is to test whether the generic
payload-transition trace contract can recover a tiny author sample without
hard-coded row fanout or X-HD-specific status semantics.

### If Goal5415 Allows One Bounded Gate

The gate must be narrow:

- use the generic payload-transition schema;
- recover a small author sample row set;
- fail closed on overflow or missing rows;
- keep source/cell sample rows out of backend logic;
- report no Figure 7/11, no performance, no full `-lb`, no full paper.

### If Goal5415 Stops

The project should stop the `-lb` line and return to higher-value work:

1. exact dataset provenance / acquisition;
2. a fair denominator-aligned performance plan;
3. additional paper-app-general system extraction only when driven by a generic
   need and non-X-HD proof.

## POD Usage Expectation

No POD is required for Goal5415 if it is a decision-only goal.

POD is needed only if Goal5415 explicitly authorizes a bounded sample-row runner
against author traces.  If needed, use only:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

Do not use naked SSH.

## Review Questions For This Midterm

1. Does this report correctly state that full X-HD paper reproduction remains
   incomplete?
2. Does it correctly treat the current `-lb` line as fail-closed?
3. Does it sufficiently acknowledge the prior over-investment in
   implementation-specific `-lb` reverse engineering?
4. Does it correctly frame Goal5414 as synthetic non-app behavior proof only?
5. Does it avoid performance ratio, Figure 7, Figure 11, exact-dataset, and
   full-paper overclaims?
6. Is Goal5415 correctly scoped as a decision gate rather than a backend
   implementation goal?
7. Should the recommended default be to stop the current `-lb` line unless a
   bounded generic trace sample gate is explicitly approved?
