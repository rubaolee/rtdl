# X-HD Comprehensive Midterm Status After Goal5401 / Goal5402 Local Smoke

Date: 2026-07-10

Status label:

```text
level_b_scalar_strong__generic_system_extraction_real__explicit_lb_status_state_machine_local_smoke_started__pod_gate_pending__full_paper_not_complete
```

## Executive Summary

X-HD is the active paper-reproduction line. The project has made real progress
on two fronts:

1. **Paper-app evidence**: RTDL reproduces the author HDResult on bounded
   same-input cases and on the strongest current Level-B public
   Dragon -> HappyBuddha workload.
2. **System extraction**: X-HD pressure has produced reusable RTDL primitives:
   generic nearest/witness/max-nearest pipelines, grid-cell descriptors,
   cell-MBR frontier rows, native 3-D cell-MBR traversal front doors,
   active-query status contracts, and native status-stream plumbing.

The project is **not yet full X-HD paper reproduction**. Exact paper input
datasets are not available by file/hash provenance, author-vs-RTDL performance
denominators are not aligned, and explicit X-HD `-lb` behavior is still
fail-closed because RTDL's current status-stream denominator does not match the
author trace.

The latest work after Goal5401 has started Goal5402: a minimal generic native
status-state smoke. Local tests pass, but POD native build and native smoke
artifacts are still pending. Goal5402 must not be called complete yet.

## Core Claim Boundary

Allowed current claims:

```text
bounded same-input X-HD HDResult reproduction is complete through Goal5126;
generic nearest/witness/max-nearest extraction is complete through Goals5127-5128;
Level-B public Dragon -> HappyBuddha scalar HDResult matches author rerun;
major generic route-performance improvements have been measured route-locally;
explicit -lb work has a generic ABI/contract and native smoke work has started.
```

Forbidden current claims:

```text
full X-HD paper reproduction;
exact paper dataset reproduction;
Figure 5/7/8/9/10/11 reproduction;
author-vs-RTDL performance parity;
same-denominator memory parity;
explicit X-HD -lb support;
native backend completion for the status-state machine;
exact per-source witnesses under early-break scalar route;
paper-app-specific logic promoted as RTDL core.
```

## What Is Completed And Externally Reviewed

### X-HD Scaffold And Bounded Reproduction

- Goal5110: X-HD paper app scaffold/provenance.
- Goals5111-5126: bounded same-input author JSON gates, RTDL value gates, and
  directed-vs-symmetric discriminating fixture.

Important result:

```text
author contract = directed input1 -> input2 Hausdorff distance
not symmetric Hausdorff
bounded X-HD same-input value reproduction = complete
```

### Generic System Extraction From X-HD

- Goal5127: decomposed directed Hausdorff into generic pipeline components:
  pairwise L2 candidate rows, nearest witness, max-nearest reduction.
- Goal5128: added a non-Hausdorff consumer proving the max-nearest helper is
  not merely an X-HD wrapper.

Important result:

```text
Hausdorff remains an app-level composition.
RTDL core exposes generic nearest/witness/reduction pieces.
```

### Full-Reproduction Plan

- Goal5129: reviewed full paper reproduction plan.

Important decision:

```text
Exact paper dataset status requires file/hash provenance.
Matching counts, Gini, logs, or HDResult values is not enough.
```

## Implemented / Review Pending Evidence

The following sections are implemented and documented, but many goals remain
`review pending`. They must not be silently upgraded to externally approved.

### Dataset And Workload Provenance

Goals5130-5131 created the paper target and dataset provenance matrices.
Subsequent goals mapped author paper-branch logs, public Stanford graphics
files, ModelNet40-like OFF inputs, public ArcGIS/TIGER-like WKT sources, and
artifact acquisition possibilities.

Current dataset conclusion:

```text
Exact paper input bytes/hashes remain unavailable.
Level-B same-source evidence is valid but not exact paper reproduction.
```

Strongest Level-B graphics candidate:

```text
source = public Stanford Dragon
target = public Stanford HappyBuddha
source points = 437,645
target points = 543,652
```

### Strongest Scalar Correctness Line

Goal5186:

```text
author hd_exec HDResult = 0.12572988867759705
matches paper-branch author-log HDResult within 1e-6
```

Goal5187:

```text
RTDL route distance = 0.12572988629271128
abs diff vs author rerun ~= 2.38e-9
```

This is the strongest current public Level-B scalar evidence. It is not exact
paper dataset reproduction.

### Phase Boundary And No-Ratio Discipline

Goal5188 records separate timing denominators:

```text
author internal Running.AvgTime ~= 7.603 ms
author process wall ~= 1.97 s
RTDL route wall ~= 7.30 s
RTDL total ~= 10.01 s
```

No author-vs-RTDL ratio is authorized from these numbers because the
denominators differ.

### Route Performance Evolution

The route-local RTDL path improved materially, while preserving the Level-B
author HDResult match. Important waypoints:

```text
Goal5188 baseline full-public route wall ~= 7.30 s
Goal5189 local-grid seed route wall ~= 5.98 s
Goal5191 inline512 empty-frontier route wall ~= 3.65 s
Goal5195 intersection-stage current-best pruning route wall ~= 2.6 s
Goal5196 dense grid-cell lookup route wall ~= 2.26 s
Goal5203 NumPy matrix input route wall ~= 1.238-1.239 s
Goal5204 linear max-nearest reducer route wall ~= 1.17-1.18 s
Goal5205 fast ASCII PLY loader full total ~= 2.06 s
Goal5211 global-bound early-break fresh route ~= 0.849 s
Goal5212 no-copy all-source selection fresh total incl load ~= 1.531 s
```

Explicit warm diagnostic:

```text
Goal5211 explicit-warm route median ~= 0.362 s
Goal5212 explicit-warm measured case total ~= 0.288 s
```

This warm number is diagnostic. It must not replace the fresh headline unless a
future prepared-runtime regime reports preparation cost and is explicitly
approved.

Critical caveat:

```text
Goal5211 early-break preserves the directed-HD scalar value, but
per_source_witness_exact = false.
409,376 / 437,645 sources early-abort, so most per-source witnesses may be
approximate.
```

Therefore this route is suitable for the directed-HD / max-nearest scalar
contract, not for exact per-source nearest-witness consumers.

### Figure And Dataset Lines

Current figure status:

```text
Figure 5: partial Level-B candidates only; no exact paper input and no ratio.
Figure 7: not reproduced; author lb=0/lb=256 matrix unavailable.
Figure 8: not reproduced; radius-strategy logs unavailable.
Figure 9: not reproduced; current logs lack the expected variant matrix.
Figure 10: not reproduced; scalability/overlap logs unavailable.
Figure 11: not reproduced; memory denominators are not aligned.
```

Memory/Figure 11 conclusion:

```text
RTDL has generic heavy/offload worklist telemetry work, but current RTDL WL and
author WL / WL Heavy Peak are not the same denominator.
same_denominator_author_figure11 = false
```

## Explicit `-lb` Status-Stream Work

The main hard blocker has moved from scalar HDResult correctness to explicit
X-HD `-lb` status-stream semantics.

### Author Oracle

Goal5387 author trace v2 oracle:

```text
active queries = 437,645
raw offload rows = 27,133,990 = 62 * active_count
raw hash = 4333109858711462591
feedback_update_count = 294
```

### RTDL Native v7 Gate

Goal5398 native v7 status-stream parity gate:

```text
active_query_count_parity = true
RTDL v7 active queries = 437,645
RTDL v7 rows = 2,600,727
RTDL / author row ratio = 0.09584756978240207
row_count_parity = false
hash_parity = false
explicit -lb remains fail-closed
```

Interpretation:

```text
The mismatch is semantic, not a trivial row remap.
Author trace records raw shader offload append rows before load-balance reduce.
Current RTDL v7 emits status rows at the existing generic frontier emission
point.
```

### Existing Knobs Exhausted

Goal5400 tested existing status-stream knobs:

```text
author rows = 27,133,990
active-initial-best-prune inline rows = 2,600,727
default no-inline rows = 2,600,727
default inline rows = 2,188,225
heavy-before-inline-prune attempted rows = 3,102,465,405 overflow
active-initial + emit_pruned_rows attempted rows = 6,436,445,015 overflow
```

Conclusion:

```text
Existing knobs either under-count by about 10x-12x or over-count by orders of
magnitude. More knob sweeps are not justified.
```

### Goal5401 Contract

Goal5401 adds the generic status-state machine spike contract:

```text
ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT
active_query_status_state_machine_native_spike_contract()
validate_active_query_status_state_machine_native_spike_contract()
```

Required semantics:

```text
raw_offload_before_continuation_reduce
post_continuation_feedback
raw row count/hash/sample telemetry
feedback_update_count telemetry
synthetic non-app gate
bounded/full app oracle gates
fail-closed overflow/mismatch behavior
```

Local validation:

```text
py -m unittest \
  tests.goal5401_status_state_machine_spike_contract_test \
  tests.goal5395_native_status_stream_abi_gate_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5380_active_query_frontier_bridge_test \
  tests.goal5382_status_machine_stream_design_test

Ran 24 tests OK
```

Goal5401 is a contract/design gate. It does not implement native backend
completion or explicit `-lb` support.

## Goal5402 Current Local Status

Goal5402 has started a minimal generic native status-state smoke.

Current local code changes include:

```text
src/native/optix/rtdl_optix_prelude.h
src/native/optix/rtdl_optix_api.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
tests/goal5402_status_state_machine_native_smoke_test.py
```

Current local API/front door:

```text
active_query_status_state_machine_smoke_native(...)
rtdl_optix_active_query_status_state_machine_smoke_v1
```

Local focused validation passed:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5402_status_state_machine_native_smoke_test \
  tests.goal5401_status_state_machine_spike_contract_test \
  tests.goal5395_native_status_stream_abi_gate_test \
  tests.goal5379_active_query_status_machine_reference_test \
  tests.goal5380_active_query_frontier_bridge_test

Ran 22 tests OK
```

Compile validation passed:

```text
$env:PYTHONPATH='src'; py -m py_compile \
  src\rtdsl\optix_runtime.py \
  src\rtdsl\active_query_status.py \
  tests\goal5402_status_state_machine_native_smoke_test.py
```

Goal5402 is **not complete** yet because the following are still missing:

```text
POD wrapper preflight for the current code state;
POD native OptiX build;
POD execution of the native smoke symbol;
POD artifact JSON;
Goal5402 result report;
Goal5402 call-for-review;
memory update after the complete goal boundary.
```

Claim boundary for Goal5402:

```text
It may prove only a synthetic generic native status-state smoke.
It must not claim explicit X-HD -lb support.
It must not claim row/hash parity against Goal5387.
It must not claim Figure 7/11 reproduction or full X-HD paper reproduction.
```

## Key Solved Problems

### 1. Direction Semantics

Goal5126 proves author HDResult is directed input1 -> input2, not symmetric
Hausdorff. This prevents a major definition error.

### 2. Exact Pairwise Materialization Avoidance

The full Dragon/HappyBuddha pair has:

```text
437,645 * 543,652 = 237,926,579,540 pairs
```

Materializing exact pair rows is infeasible. RTDL moved to generic seeded /
frontier / inline-nearest routes instead.

### 3. Generic Route Extraction

X-HD pressure produced reusable system APIs rather than an X-HD-only primitive:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest reducer;
grid-cell descriptors;
cell-MBR frontier rows;
nearest-state frontier split;
native 3-D cell-MBR traversal;
active-query status contracts.
```

### 4. Route-Local Speed Improvements

Route-local performance improved from multi-second scalar routes to sub-second
fresh route and sub-0.4s explicit-warm diagnostics while preserving scalar
HDResult. These are meaningful RTDL route improvements but not author parity.

### 5. POD Procedure Stabilized

POD work must use:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<cmd>"
```

Do not use naked SSH or old keys.

## Remaining Hard Problems

### H1. Exact Paper Dataset Provenance

Exact paper reproduction still requires file/hash or equivalent provenance for
the paper inputs. Public same-source data can support Level-B evidence, not
Level-C exact paper dataset claims.

### H2. Explicit `-lb` Status Semantics

The author `-lb` raw status trace has a denominator RTDL does not yet match.
This is the current deepest algorithmic/semantic gap.

### H3. Figure-Level Reproduction

Figures 7/8/9/10/11 are not reproduced. Some author scripts/logs exist, but
missing matrices, missing datasets, or denominator mismatches prevent claims.

### H4. Performance Denominator Alignment

The project has many useful timings, but no author-vs-RTDL ratio is authorized
unless dataset, hardware, phase boundary, and runtime regime are aligned.

### H5. Review Debt

Many goals after 5130 are implemented / review pending. Reports and
call-for-review files exist, but implementation status must remain separate
from external approval.

## Next Planned Work

### Immediate Goal: Complete Goal5402

Objective:

```text
finish the smallest native generic status-state smoke satisfying Goal5401.
```

Steps:

1. Use POD wrapper preflight.
2. Sync Goal5402 modified files to the POD workspace.
3. Run focused POD tests for Goal5402/Goal5401.
4. Build native OptiX on POD.
5. Execute a small native smoke through
   `active_query_status_state_machine_smoke_native(...)`.
6. Save POD artifact JSON.
7. Write Goal5402 result report and call-for-review.
8. Update `memory/progress.md`, `memory/todo.md`, and `memory/decisions.md`.

Expected POD requirement:

```text
required for native build and native symbol smoke
expected runtime: one focused native build plus one synthetic smoke run
```

Success label:

```text
goal5402_generic_status_state_machine_native_smoke_passed
```

Failure labels:

```text
goal5402_native_build_failed
goal5402_native_symbol_smoke_failed
goal5402_generic_boundary_violation
```

### Next Goal After Goal5402: Bounded App Gate

If Goal5402 passes synthetic smoke, the next goal should run a bounded X-HD
application-side gate that compares status-state smoke output against a small
bounded oracle. It must remain fail-closed and must not jump directly to full
paper claims.

Expected POD requirement:

```text
likely required if native symbol is used;
small bounded artifact only, not full Dragon/Asian row-hash gate yet.
```

### Next Goal After Bounded Gate: Full Goal5387 Oracle Gate

Only after bounded status-state semantics pass:

```text
run full Dragon -> AsianDragon gate against Goal5387 author trace v2:
  active_count = 437,645
  author rows = 27,133,990
  author raw hash = 4333109858711462591
  feedback_update_count = 294
```

Required comparisons:

```text
active_count parity;
row_count parity;
raw row hash or deterministic sample parity;
status_count_offloading parity;
feedback_update_count parity or explicit generic not-applicable rationale;
overflow/fail-closed behavior.
```

Success label:

```text
explicit_lb_status_state_machine_parity_candidate
```

Failure label:

```text
explicit_lb_status_state_machine_denominator_mismatch__keep_lb_fail_closed
```

### Review Plan

The next strict review packet should include:

```text
Goal5399 semantic-gap decision;
Goal5400 existing knob matrix;
Goal5401 generic status-state machine contract;
Goal5402 native synthetic smoke, if completed.
```

The review question should be whether the explicit `-lb` line remains a
legitimate generic RTDL system effort or should be stopped as requiring
paper-specific shader semantics.

## Expected Timeline

These are engineering estimates, not promises:

```text
Goal5402 POD build/smoke/report: 1 focused work block if POD is reachable.
Bounded status-state app gate: 1-2 focused work blocks after Goal5402.
Full Goal5387 oracle gate: 1-2 focused work blocks, may expand if row volume
  or native memory capacity causes fail-closed overflow.
Review packet cleanup: 1 focused work block.
```

If the full oracle gate still mismatches badly, the correct next action is not
another knob sweep. It is either a new generic status-state semantic design with
a specific hypothesis, or closing explicit `-lb` as unsupported under the
current RTDL execution model.

## Bottom Line

Current X-HD state:

```text
Scalar Level-B representative route: strong.
Generic RTDL system extraction: real.
Route-local performance: dramatically improved.
Exact paper datasets: still blocked.
Figure-level reproduction: not complete.
Explicit -lb: still fail-closed.
Current active implementation: Goal5402 native generic status-state smoke,
local tests passed, POD validation pending.
```

The project is past "can RTDL compute the same HDResult on representative
inputs?" The answer is yes for the strongest current Level-B public route. The
remaining question is harder: whether RTDL can reproduce the author's explicit
`-lb` status-machine behavior generically, without turning the language into an
X-HD-specific clone.
