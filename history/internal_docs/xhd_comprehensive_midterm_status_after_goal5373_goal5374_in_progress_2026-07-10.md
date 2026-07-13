# X-HD Comprehensive Midterm Status After Goal5373 / Goal5374 In Progress

Date: 2026-07-10

Status label:

```text
xhd_full_reproduction_midterm__level_b_strong__lb_status_machine_oracle_in_progress
```

## Executive Summary

The X-HD line has made real progress, but it is not full paper reproduction yet.

What is genuinely achieved:

- Bounded same-input X-HD scalar value reproduction is complete and externally
  reviewed through Goal5126.
- Hausdorff is no longer treated as a special RTDL core primitive. Goals5127 and
  5128 extracted a generic nearest/witness/max-nearest pipeline and proved it
  with a non-Hausdorff consumer.
- The strongest current representative evidence is Level-B public-source
  Stanford graphics work. On Dragon -> HappyBuddha, author `hd_exec` and RTDL
  match the scalar `HDResult` within about `2.4e-9`.
- The current fast Level-B route is much faster than the first scalable route:
  the all-source Dragon -> HappyBuddha route went from roughly `7.30s` route
  wall around Goal5187 to about `0.849s` fresh route with Goal5211 global-bound
  early break, and about `0.362s` explicit-warm route. After Goal5212, fresh
  full total including load is about `1.531s`, and explicit-warm measured case
  total is about `0.288s`.
- The app-owned `hd_exec`-compatible wrapper exists and can emit author-shaped
  JSON for multiple bounded and Level-B cases.
- Functional option-surface work is underway. `-tune_radius adaptive` has a
  narrow internal diagnostic mapping when backed by a nonterminal author trace.
- The current hard target is explicit `-lb` / heavy-cell offload. Goals5363-5373
  prove that count-only, scalar-radius, raw-kind2, existing-global-bound, and
  byte-formula-only explanations are insufficient. Author `-lb` depends on a
  shader payload status machine and load-balance post-processing.
- Goal5374 has already produced raw POD evidence from an instrumented author
  build. The author-side oracle reports `OffloadingSize=27133990`,
  `RawOffloadRowsBeforeSortReduce=27133990`, `RawOffloadRowsAuthorWidthBytes=
  217071920`, `StatusInitCount=437645`, and
  `StatusOffloadingAppendCount=27133990` on the Dragon -> AsianDragon `lb=256`
  diagnostic. This is not yet closed as a goal report.

What remains not achieved:

- No exact paper input file/hash provenance has been established for the full
  paper datasets. Level-B same-source evidence must not be called Level-C exact
  dataset reproduction.
- No denominator-aligned author-vs-RTDL performance ratio is authorized.
- Figure 5/7/8/9/10/11 are not fully reproduced.
- Explicit author `-lb` is still unsupported in RTDL. The current author oracle
  is ready, but the RTDL status-machine counterpart is missing.
- Current Goal5374 raw POD evidence is promising but not yet packaged into a
  completed goal report, tests, and call-for-review.

## Goal Of The Current Phase

The near-term objective is not to chase another generic route micro-optimization.
The objective is to close the biggest remaining author RT-core semantic gap:

```text
Can RTDL reproduce the author X-HD `-lb` heavy-cell/offload status-machine
behavior on the same Level-B input, with row-count / queue / status evidence,
without hard-coding an X-HD-only core primitive?
```

This matters because `-lb` is tied to:

- Figure 7 load-balance behavior;
- Figure 11 worklist / heavy-offload memory fields;
- author RT-core algorithm parity;
- the user's broader requirement that Python/RTDL be the same app-level
  behavior as the author C++/CUDA/OptiX program, except for language/system
  implementation.

## Current Scope And Claim Boundary

Allowed current claims:

```text
bounded same-input value reproduction complete through Goal5126
generic nearest/witness/max-nearest extraction complete through Goals5127-5128
Level-B public Dragon/HappyBuddha scalar value matches author rerun
current route-local performance improved substantially under explicit regimes
author -lb status-machine oracle evidence is in progress through Goal5374
```

Forbidden current claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
author RT-core algorithm parity
explicit -lb support
Figure 7 / Figure 8 / Figure 11 reproduction
same-denominator author-vs-RTDL performance ratio
same-denominator memory parity
performance parity with the author program
exact per-source witnesses under Goal5211 global-bound early break
```

## Completed Work By Stage

### Stage 1 - Scaffold, Bounded Correctness, And Provenance

Completed and externally reviewed:

- Goal5110: X-HD paper app scaffold and author provenance.
- Goals5111-5126: bounded same-input author JSON gates, RTDL route gates, and
  directed-vs-symmetric Hausdorff discrimination. The decisive asymmetric case
  proved the author reports directed input1 -> input2 Hausdorff distance, not
  symmetric Hausdorff.

Key result:

```text
bounded_same_input_reproduction_complete = true
full_paper_reproduction_complete = false
```

### Stage 2 - Generic System Extraction From X-HD

Completed and externally reviewed:

- Goal5127: extracted generic pairwise L2 candidate rows, nearest witness, and
  max-nearest reduction helpers.
- Goal5128: added a non-Hausdorff facility/service-radius consumer, closing the
  genericity concern.

System value:

```text
Hausdorff is app-level composition.
RTDL core gains reusable nearest/witness/max-nearest building blocks.
```

### Stage 3 - Full Paper Feasibility And Dataset Provenance

Implemented, much of it review pending:

- Goals5130-5131: paper target matrix and dataset provenance.
- Goals5175-5178: author log workload manifest, paper branch log index, target
  log mapping, and Dragon/HappyBuddha bridge.
- Goals5214-5216 and later exact-input sweeps: exact dataset provenance remains
  blocked.
- Goals5297-5309: public Stanford graphics and public geo acquisition/probe
  work; some Level-B candidates match values, but exact paper identity remains
  unproved.

Current conclusion:

```text
Level B same-source representative evidence is valid.
Level C exact paper dataset reproduction is not achieved.
Statistics, counts, Gini, MBRs, or matching HDResult are not file/hash identity.
```

### Stage 4 - Scalable Level-B Route And Performance Evolution

The key route evolved as follows on the Dragon -> HappyBuddha Level-B candidate:

```text
Goal5187 all-source route wall                 ~= 7.30s
Goal5189 local-grid seed route wall            ~= 5.98s
Goal5191 inline512 route wall                  ~= 3.65s
Goal5195 intersection current-best prune       ~= 2.6s
Goal5196 dense local-grid lookup               ~= 2.26s
Goal5202 coordinate-matrix reuse               ~= 2.03s
Goal5203 NumPy matrix input front door         ~= 1.24s
Goal5204 linear max-nearest reducer            ~= 1.17-1.18s
Goal5207 explicit warm route                   ~= 0.626s
Goal5211 global-bound early-break fresh route  ~= 0.849s
Goal5211 explicit-warm route median            ~= 0.362s
Goal5212 fresh full total incl. load           ~= 1.531s
Goal5212 explicit-warm measured case total     ~= 0.288s
```

Important caveat:

```text
Goal5211 is exact-value-only for directed-HD/max-nearest.
per_source_witness_exact = false
early_aborted_sources = 409376 / 437645
```

Therefore Goal5211 is a strong route-level value result, but not a generic exact
nearest-witness API default.

### Stage 5 - Figure And Paper-Section Status

Current figure status:

- Figure 5: partial Level-B value-matched graphics/geo candidates exist, but no
  full figure reproduction or same-denominator performance ratio.
- Figure 7: author `lb=0/lb=256` diagnostic exists, but full matrix is missing
  and RTDL `-lb` support is not authorized.
- Figure 8: source/scripts exist, nonterminal radius queue trace has a narrow
  internal mapping, but no full radius-strategy matrix reproduction.
- Figure 9: current author logs do not provide the expected four-variant matrix;
  checked-in PDF is evidence, not reproducible denominator.
- Figure 10: scalability/overlap inputs/logs are missing.
- Figure 11: RTDL generic worklist telemetry exists, but author WL / WL Heavy
  Peak denominators are not aligned; no memory ratio is authorized.

### Stage 6 - Author Option Surface And RT-Core Semantics

Completed / review pending highlights:

- Goals5347-5353: functional feature / variant / option-surface audits.
- Goals5354-5362: radius-growth and `-tune_radius adaptive` internal diagnostic
  route.
- Goals5363-5373: `-lb` / heavy-cell offload semantic narrowing.

Current `-tune_radius` status:

```text
Narrow internal diagnostic mapping exists for -tune_radius adaptive
when backed by a nonterminal author trace.
General author -tune_radius support is not claimed.
```

Current `-lb` status:

```text
explicit -lb support = not authorized
behavior-level lb0/lb256 gate = passed
row-count parity = not established
same-denominator memory parity = not established
author status-machine semantics = required next target
```

## Key Problems Already Solved

### Problem 1 - "Is Hausdorff An RTDL Primitive?"

Resolved:

```text
No. Hausdorff remains an app-level composition.
RTDL owns generic nearest/witness/max-nearest components.
```

### Problem 2 - Directed vs Symmetric HD Ambiguity

Resolved by Goal5126:

```text
author HDResult = directed input1 -> input2
RTDL route matches that directed contract
symmetric interpretation would fail the asymmetric fixture
```

### Problem 3 - Scalable Same-Source Value Route

Resolved for Level-B Dragon -> HappyBuddha:

```text
RTDL route matches author HDResult with abs diff ~= 2.38e-9.
Naive exact pair materialization is impossible at full scale.
The scalable cell-MBR / inline-nearest route is the valid route.
```

### Problem 4 - Bad Performance Bottleneck Attribution

Mostly resolved:

```text
Python continuation and row materialization are no longer the main story.
The route-level wins came from generic seed/frontier/inline-nearest design,
coordinate matrix reuse, input front-door cleanup, and reduction changes.
```

### Problem 5 - Figure 11 Memory Denominator Confusion

Resolved as a status decision:

```text
RTDL current memory fields are not author Figure 11 denominators.
Figure 11 remains not reproduced.
No memory ratio is authorized.
```

### Problem 6 - `-lb` Simple Explanations

Rejected through Goals5363-5373:

```text
byte formula mismatch                 rejected
scalar radius mismatch alone          rejected
materialized row-only explanation     rejected
all raw same-radius kind2 explanation rejected
existing global-bound == cmax2 abort  rejected
```

The remaining problem is author queue/status/cmin2/load-balance semantics.

## Major Problems Still Open

### Open Problem 1 - Exact Paper Inputs

No exact file/hash provenance exists for the full paper inputs.

Impact:

```text
full paper reproduction cannot be claimed
figure-level reproduction remains blocked or Level-B only
```

### Open Problem 2 - Fair Performance Denominator

Author `Running.AvgTime`, author process wall, RTDL route wall, RTDL full gate
total, cold process, warm process, and prepared replay are different
denominators.

Impact:

```text
no author-vs-RTDL performance ratio is authorized yet
```

### Open Problem 3 - Goal5211 Witness Semantics

Global-bound early break is a strong directed-HD value optimization but not a
generic exact per-source witness route.

Impact:

```text
per-source witness outputs are approximate for early-aborted sources
the route must remain explicitly labeled
```

### Open Problem 4 - Explicit `-lb`

The author `-lb` path is not just "cells with point_count > lb." It is a shader
payload status machine:

```text
payload in_q_idx
payload cmin2/current-best
kInit / kOffloading / kAborted status bits
cmax2 MBR abort
miss/offload queue updates
loadBalanceProcessing sort/reduce/restore
```

RTDL currently lacks the counterpart fields needed to prove row-count parity.

### Open Problem 5 - Review Debt

Many goals after 5130 are implemented / review pending. The strict review at
Goal5216 already required wording corrections. Future summary language must not
upgrade implemented goals to reviewed goals.

## Goal5374 Current State

Goal5374 is in progress. It has produced the first author-side status-machine
oracle evidence from a patched author build on the POD.

Files already present:

```text
Paper-reproduction-apps/x-hd-paper/scripts/instrument_xhd_author_lb_status_trace.py
tests/goal5374_author_lb_status_trace_instrumentation_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_instrument_patch_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5374_author_lb256_status_trace_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5374_author_lb_status_trace_oracle.py
```

Patch summary:

```text
author_root = /tmp/xhd-goal5112/author
patched = true
changed.launch_parameters = true
changed.shader = true
changed.rt_impl = true
marker = RTDL_GOAL5374_LB_STATUS_TRACE
```

Author Dragon -> AsianDragon `lb=256` iteration-3 trace:

```text
NumInputPoints = 437645
NumOutputPoints = 0
Radius = 79.2156982421875
OffloadingSize = 27133990
RTTime = 46.679 ms
CUDATime = 77.58 ms
ComparedPoints = 1241945719
Hits = 896287932

LBTrace.ActiveInQueueSize = 437645
LBTrace.RawOffloadRowsBeforeSortReduce = 27133990
LBTrace.RawOffloadRowsAuthorWidthBytes = 217071920
LBTrace.StatusInitCount = 437645
LBTrace.StatusOffloadingAppendCount = 27133990
LBTrace.StatusCmax2MbrAbortCount = 0
LBTrace.StatusPointLoopEarlyBreakCount = 0
```

Interpretation:

```text
The author-side oracle is real.
RawOffloadRowsBeforeSortReduce == OffloadingSize.
RawOffloadRowsAuthorWidthBytes == OffloadingSize * 2 * sizeof(uint32_t).
```

But Goal5374 is not finished until the builder, tests, result report, and
call-for-review are written.

## Next Work Plan

### Goal5374 - Finish Author `-lb` Status Trace Oracle

Purpose:

```text
Turn the raw patched-author POD evidence into a reviewed goal artifact.
```

Tasks:

1. Run `build_xhd_goal5374_author_lb_status_trace_oracle.py`.
2. Add artifact tests that verify:
   - patch summary changed all required author files;
   - `RawOffloadRowsBeforeSortReduce == OffloadingSize == 27133990`;
   - `RawOffloadRowsAuthorWidthBytes == 217071920`;
   - `StatusOffloadingAppendCount == OffloadingSize`;
   - cmax2 and point-loop abort counters are zero for this run;
   - RTDL Goal5371 row count `21006960` does not match author rows;
   - claim flags remain false.
3. Write:
   - `goal5374_xhd_author_lb_status_trace_oracle_result_2026-07-10.md`;
   - `call_for_review_goal5374_xhd_author_lb_status_trace_oracle_2026-07-10.md`.
4. Update memory.

Expected exit:

```text
author_oracle_ready__next_rtdl_status_machine_counterpart
```

POD need:

```text
No new POD run required unless the raw author JSON is invalid.
Current raw POD evidence is already downloaded.
```

### Goal5375 - RTDL Status-Machine Counterpart Against Goal5374 Oracle

Purpose:

```text
Add or audit RTDL-side telemetry/counterpart fields needed to compare against
the author oracle.
```

Minimum required fields:

```text
active_in_queue_size
raw_offload_rows_before_sort_reduce
raw_offload_rows_author_width_bytes
status_count_init
status_count_offloading
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
point_loop_early_break_count
current_best_state_source
row_count_parity_against_author_offloading_size
```

Expected output:

```text
Either row_count_parity=true, or a precise denominator mismatch explaining why
RTDL still cannot accept explicit -lb.
```

POD need:

```text
Required. This must run native RTDL telemetry on the same Dragon -> AsianDragon
Level-B input.
```

### Goal5376 - Explicit `-lb` Decision Gate

Purpose:

```text
Decide whether RTDL can accept explicit -lb under a narrow internal diagnostic
route, or must keep -lb fail-closed.
```

Possible outcomes:

```text
accept_narrow_internal_lb_mapping_after_status_oracle
reject_lb_mapping_row_denominator_not_aligned
defer_lb_until_author_queue_state_model_exists
```

POD need:

```text
Likely low if Goal5375 provides complete artifacts; otherwise may need one
confirmatory POD run.
```

### Review Packet - Goals5363-5376

Purpose:

```text
Send the full `-lb` / heavy-offload line for strict external review.
```

Must include:

- source semantics audit;
- author lb0/lb256 pair;
- RTDL behavior counterpart;
- byte-formula reconciliation;
- radius probe;
- raw kind-count probe;
- queue-state requirements;
- status-machine matrix;
- RTDL telemetry surface audit;
- author oracle;
- RTDL counterpart / decision if completed.

### After `-lb`

Only after the `-lb` status-machine line is closed should the project choose
between:

1. Further author option-surface parity work;
2. Figure 7 / Figure 11 denominator-aligned matrix work if required data exists;
3. Exact dataset acquisition / external artifact route;
4. A fresh system-extraction pass if the `-lb` counterpart produces reusable
   generic RTDL queue/status-machine primitives.

## POD Usage Expectation

Current active POD:

```text
host = 213.173.108.24
port = 13502
workspace = /tmp/rtdl_goal5364
author full source/build = /tmp/xhd-goal5112/author
author build = /tmp/xhd-goal5112/build-gcc11-optix77-fast
data = /tmp/xhd_goal5234/data/dragon.ply
       /tmp/xhd_goal5234/data/asian_dragon.ply
```

Always use:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<cmd>"
```

Do not use naked SSH.

Expected next POD use:

- Goal5374: probably no additional POD work unless re-running author oracle.
- Goal5375: required for RTDL native status-machine counterpart.
- Goal5376: optional confirmation depending on Goal5375 result.

## Time / Effort Plan

The schedule should be measured in goals, not calendar promises:

```text
Goal5374: short closeout / packaging / tests, likely no POD.
Goal5375: hard implementation / measurement goal, POD required.
Goal5376: decision / boundary goal after Goal5375 evidence.
Review packet: one strict external review node for the whole lb line.
```

If Goal5375 shows denominator parity:

```text
Proceed to narrow explicit -lb support under a diagnostic/internal route only.
Then test whether this supports Figure 7 / Figure 11 denominator work.
```

If Goal5375 does not show denominator parity:

```text
Keep explicit -lb unsupported.
Document the precise mismatch.
Do not keep tuning scalar radius or raw kind counts.
```

## Final Current Conclusion

The project is in a good but unfinished state.

The X-HD line has already delivered real RTDL system improvements and strong
Level-B representative correctness/performance evidence. The route is no longer
a toy bounded app wrapper. It is a generic cell-MBR / nearest-state /
inline-nearest / max-nearest pipeline under strict claim boundaries.

The remaining hard wall is no longer "can RTDL compute the scalar directed
Hausdorff value?" It can, on substantial public Level-B cases. The hard wall is:

```text
Can RTDL reproduce the author RT-core status-machine behaviors, especially
`-lb` heavy-cell/offload, at the same semantic denominator?
```

Goal5374 has made the first important move by producing an author-side status
oracle. The next decisive work is to build the RTDL counterpart against that
oracle. Until that passes, explicit `-lb`, Figure 7, Figure 11, author RT-core
parity, and full X-HD reproduction remain not closed.
