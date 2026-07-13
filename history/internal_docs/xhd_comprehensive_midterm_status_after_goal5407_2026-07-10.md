# X-HD Comprehensive Midterm Status After Goal5407

Date: 2026-07-10

Status label:

```text
level_b_scalar_strong__generic_system_extraction_real__full_cover_surface_real__author_delta_is_row_identity_gap__explicit_lb_unsupported__full_paper_not_complete
```

## 1. Executive Summary

X-HD is the active major paper-reproduction project. The current state is strong
but not finished:

1. **Bounded same-input X-HD value reproduction is complete and externally
   reviewed through Goal5126.**
2. **Generic RTDL system extraction is real.** X-HD pressure has produced
   generic nearest/witness/max-nearest helpers, grid/cell-MBR descriptors,
   frontier contracts, native 3-D cell-MBR traversal front doors, route warmup
   discipline, and active-query status-stream experiments.
3. **The strongest current representative evidence is Level B, not full paper
   reproduction.** The public Stanford Dragon -> HappyBuddha line matches the
   author HDResult on the same public inputs, but exact paper input bytes /
   hashes remain unavailable.
4. **The scalar X-HD route is fast and functionally strong, but it is not a
   same-denominator author performance comparison.**
5. **The explicit `-lb` / author raw offload stream line is still unsupported.**
   Goal5407 shows the remaining gap is not merely "add six rows per active
   query"; author sample rows are not a subset of the current RTDL full-cover
   surface, so this is a row-identity / status-machine semantics gap.

The project should not be described as full X-HD paper reproduction yet.

## 2. Core Objective

The project objective remains:

```text
Use X-HD as a paper-reproduction pressure test to improve RTDL as a general
spatial/dataflow language, while keeping paper-specific wrappers, comparators,
datasets, tolerances, and figure claims inside the paper app.
```

RTDL core may expose generic primitives. It must not become an X-HD-specific
codebase.

Allowed system-level outcomes include:

- generic pairwise L2 candidate rows;
- nearest witness;
- max-nearest / directed-Hausdorff scalar reducer;
- grid cell descriptors;
- cell-MBR frontier rows;
- native OptiX 3-D cell-MBR traversal front doors;
- active-query status rows / status-state stream contracts;
- generic worklist / offload telemetry.

App-owned X-HD responsibilities include:

- author `hd_exec` wrapper;
- exact input provenance;
- paper-log mapping;
- HDResult comparator and tolerance;
- `-lb` / figure-specific claim boundaries;
- paper figure labels and final reporting.

## 3. Completed And Reviewed Base

The reviewed base is:

```text
Goal5110: X-HD scaffold / provenance.
Goals5111-5126: bounded same-input author JSON and RTDL route gates, including
                 the directed-vs-symmetric discriminating fixture.
Goals5127-5128: generic nearest pipeline extraction and non-Hausdorff consumer.
Goal5129: full-reproduction plan, reviewed with amendment incorporated.
```

Meaning:

- X-HD's scalar directed input1 -> input2 definition is pinned.
- Bounded same-input value reproduction is accepted.
- The first system extraction is accepted: Hausdorff itself is an app-level
  composition over generic nearest/witness/reduction primitives.

This does **not** mean:

- exact paper datasets are available;
- all paper figures are reproduced;
- author X-HD RT-core algorithm is fully reproduced;
- performance parity is established.

## 4. Representative Level-B Scalar Line

The strongest scalar correctness line is public Stanford
Dragon -> HappyBuddha:

```text
workload                  = public Stanford Dragon -> HappyBuddha
author hd_exec HDResult   = 0.12572988867759705
RTDL route distance       = 0.12572988629271128
absolute difference       ~= 2.38e-9
```

This is Level B same-source representative evidence:

- same public-source family;
- same current author binary / app wrapper;
- same directed HDResult value;
- no exact author input file/hash provenance.

It is not Level C exact paper dataset reproduction.

### Current scalar performance line

The strongest fast scalar route comes from the Goal5211/Goal5212 line:

```text
Goal5211 fresh route                         ~= 0.849s
Goal5212 fresh total including input load    ~= 1.531s
Goal5211 explicit-warm route median          ~= 0.362s
Goal5212 explicit-warm measured case total   ~= 0.288s
```

Important caveat:

```text
per_source_witness_exact = false
early-aborted sources    = 409,376 / 437,645
```

This route is valid for the final directed Hausdorff / max-nearest scalar value
contract. It is not valid for consumers requiring exact per-source witness rows.

No author-vs-RTDL performance ratio is authorized from these numbers, because
author internal timing, author process wall, RTDL route wall, RTDL total wall,
cold process, warm process, and explicit warm route are different denominators.

## 5. System Work Completed From X-HD Pressure

The X-HD line has yielded reusable RTDL system capabilities:

### 5.1 Generic nearest / witness / max-nearest pipeline

Implemented and reviewed:

```text
pairwise_l2_distance_candidate_rows
nearest_witness
max_nearest_distance_witness
```

Hausdorff is now an app-level composition over these generic primitives. A
non-Hausdorff facility/service-radius consumer proves the helpers are not just
X-HD-shaped wrappers.

### 5.2 Generic grid / cell-MBR / frontier route

Implemented / review pending:

```text
grid cell descriptors
cell MBR candidate/frontier rows
nearest-state frontier split
native 3-D cell-MBR OptiX traversal
inline nearest payload path
frontier continuation
coordinate-matrix front doors
linear max-nearest reducer
```

These are generic route primitives. The X-HD app uses them for the public
Dragon/HappyBuddha Level-B route.

### 5.3 Active-query status / worklist line

Implemented / review pending:

```text
generic active-query status rows
native status-stream ABI experiments
generic status-state machine smoke
bounded status-state oracle
full-cover surface summarization
```

This line exists because X-HD `-lb` / Figure 7 / Figure 11 require a raw
offload/status stream denominator that the scalar route does not expose.

The line is not complete.

## 6. Full Paper / Figure Status

### Completed

```text
Level A bounded same-input value reproduction: complete and reviewed.
Level B public Stanford Dragon -> HappyBuddha scalar value: strong evidence.
Generic system extraction from X-HD: real and substantial.
```

### Not completed

```text
Exact paper datasets: not available / not proven by file hash.
Figure 5: not fully reproduced; selected Level-B candidates exist.
Figure 6: not fully reproduced.
Figure 7: not reproduced; explicit -lb stream unsupported.
Figure 8: not reproduced; author radius-tuning matrix unavailable.
Figure 9: not reproduced; checked logs do not contain required variants.
Figure 10: not reproduced; scalability/overlap logs unavailable.
Figure 11: not reproduced; memory denominator not aligned.
Full paper reproduction: not complete.
```

### Dataset blocker

Matching counts, Gini, bounding boxes, or paper-log HDResult is not enough to
claim exact input identity. Exact paper dataset reproduction requires file/hash
or equivalent provenance evidence.

## 7. Explicit `-lb` / Raw Status Stream Track

The `-lb` track is the main current hard problem.

### 7.1 Author oracle

Goal5387 author trace v2 provides the current oracle:

```text
active queries          = 437,645
author raw offload rows = 27,133,990
author raw row hash     = 4333109858711462591
feedback_update_count   = 294
status_count_miss       = 0
status_count_completed  = 0
status_count_aborted    = 0
```

This oracle is stronger than count-only telemetry because it exposes raw row
identity / hash samples and feedback evidence.

### 7.2 Failed or partial RTDL surfaces

Several RTDL surfaces were compared:

```text
bridge rows                  = 2,188,225  = 5 * active_count
native v7 status rows         = 2,600,727
default raw kind2 rows        = 21,006,960
full-cover surface rows       = 24,508,120 = 56 * active_count
author raw offload rows       = 27,133,990 = 62 * active_count
```

The full-cover surface is the closest known RTDL surface, but it is not author
parity.

### 7.3 Goal5405 bounded bridge

Goal5405 proved the bounded 56+6 shape:

```text
active_count = 2
rows per active = 56 + 6 = 62
total rows = 124
matched = true
```

This is useful bounded evidence, but still not full explicit `-lb`.

### 7.4 Goal5406 real full-cover surface

Goal5406 generated the real full-public RTDL full-cover surface:

```text
RTDL full-cover rows       = 24,508,120
Goal5365 full-cover rows   = 24,508,120
author Goal5387 raw rows   = 27,133,990
delta author - RTDL        = 2,625,870 = 6 * 437,645
RTDL / author row ratio    = 0.9032258064516129

RTDL row hash              = 9732286907904247845
author raw row hash        = 4333109858711462591
hash parity                = false
```

POD timing for this diagnostic:

```text
total_sec          ~= 30.6506
frontier_rows_sec  ~= 7.4860
trace_summary_sec  ~= 21.9410
```

This proves the real 56x full-cover surface exists. It does not prove explicit
`-lb`.

### 7.5 Goal5407 delta membership probe

Goal5407 isolates the full-cover -> author gap:

```text
status  = full_cover_delta_isolated__row_identity_or_feedback_semantics_still_open
matched = true

active_count                     = 437,645
total_delta_rows                 = 2,625,870
delta_rows_per_active_if_uniform = 6
delta_rows_per_active_remainder  = 0

RTDL full-cover rows             = 24,508,120
RTDL rows per active             = 56 for every active source
```

The decisive new finding is row identity:

```text
author sample (source=11168,  cell=2924) present in RTDL full-cover = false
author sample (source=210712, cell=17)   present in RTDL full-cover = false
author sample (source=437119, cell=17)   present in RTDL full-cover = false
```

Classification:

```text
author_sample_rows_not_subset_of_rtdl_full_cover__row_identity_gap
```

Interpretation:

```text
The remaining gap is not merely a uniform +6 rows/active count problem.
The author raw status stream contains sample (source, cell) rows that are not
in the current RTDL full-cover surface. Therefore explicit -lb remains
unsupported; the next question is cell-id namespace / row-identity / status
transition semantics, not a simple 56+6 row-count patch.
```

Goal5407 validation:

```text
local focused regression:
  tests.goal5407_full_cover_delta_membership_probe_test
  tests.goal5406_real_full_cover_surface_stream_gate_test
  tests.goal5405_full_cover_delta_status_bridge_test
  tests.goal5394_full_cover_delta_status_probe_test

Ran 18 tests OK
```

## 8. Problems Already Solved

### 8.1 Bounded value correctness

The project has a reviewed bounded same-input value reproduction for X-HD and
a directed-vs-symmetric fixture that proves the author contract is directed
input1 -> input2.

### 8.2 Hausdorff no longer pollutes core as an app primitive

Directed Hausdorff is expressed as generic nearest/witness/max-nearest
composition. A non-Hausdorff consumer exists.

### 8.3 Large public scalar route works

The public Dragon -> HappyBuddha route matches author scalar HDResult at full
public scale.

### 8.4 Several false performance paths are closed

No-go or neutral lines include:

```text
lower inline thresholds;
static cell order tuning;
trace-tmax / scalar ray extent;
native CUDA local-grid seed wrapper;
prepared cell-MBR accel-build caching;
v6 row remap into fake status-stream v7;
existing status-stream knob sweeps.
```

### 8.5 POD access procedure is stabilized

Use only:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<command>"
```

The current known POD endpoint is:

```text
host = 213.173.108.24
port = 13502
gpu  = NVIDIA RTX 4000 Ada Generation
```

## 9. Remaining Major Challenges

### 9.1 Exact paper datasets

The largest full-paper blocker remains input provenance. Public same-source
inputs are useful Level-B evidence, but not exact paper dataset reproduction.

### 9.2 Explicit `-lb` / Figure 7 / Figure 11

Current RTDL status-stream surfaces do not match the author raw offload stream.
Goal5407 shows the gap includes row identity, not only row count.

### 9.3 Figure-level reproduction

Figures 5-11 need dataset, author phase, and denominator alignment. Several
figures are blocked by missing logs / missing input roots / non-comparable
memory denominators.

### 9.4 Review debt

Many goals from the Level-B and full-paper exploration line are implemented /
review pending. They must not be silently promoted to externally approved.

### 9.5 Performance ratio

No performance ratio is authorized. The project has route-local timings and
author timings, but not a same-denominator performance matrix.

## 10. Immediate Next Plan

### Goal5408: Full-cover row identity / cell-id namespace reconciliation

Purpose:

```text
Determine why Goal5407's author sample (source, cell) rows are absent from the
RTDL full-cover surface.
```

Required checks:

1. Compare author cell-id namespace against RTDL compact cell ids and original
   grid cell ids.
2. For the three Goal5407 sample sources, dump or summarize RTDL full-cover
   cell sets under every available id namespace.
3. Determine whether the author sample cells can be recovered by a generic
   remapping / namespace conversion.
4. If remapping explains the sample rows, define a generic row-identity parity
   gate.
5. If remapping does not explain the sample rows, classify the gap as
   author-status-machine / feedback / load-balance processing semantics and
   keep explicit `-lb` fail-closed.

Constraints:

```text
do not hard-code 6 rows per active;
do not hard-code 62 rows per active;
do not add X-HD option names or figure semantics to RTDL core/native;
do not claim explicit -lb support without row-count and row-identity evidence.
```

POD expectation:

```text
Goal5408 can start from existing artifacts locally.
POD is needed only if new full-public author/RTDL row dumps or native probes are
required.
```

### Goal5409: Decision after row-identity reconciliation

Branch A: generic explanation found

```text
Implement the smallest app-neutral native/status-state change.
Run bounded gate first.
Then run full Dragon -> AsianDragon row-count/hash/sample/status/feedback gate.
```

Branch B: no generic explanation

```text
Close explicit -lb as unsupported under current RTDL execution model.
Record that scalar Level-B route remains strong, but Figure 7 / Figure 11 /
author raw offload stream are not reproduced.
```

### Goal5410: Consolidated review packet

Bundle Goals5401-5409, focusing on:

```text
generic status-state machine contract;
native smoke;
bounded status oracle;
full-cover surface;
Goal5407 row-identity gap;
decision to continue or fail-close explicit -lb.
```

## 11. Expected Process And Timing

This is an engineering estimate, not a guarantee.

```text
Goal5408 local artifact analysis:
  0.5-1 working session if existing artifacts are sufficient.

Goal5408 with new POD probes:
  1 POD session; expect 30-90 minutes including preflight, run, artifact sync,
  and focused tests.

Goal5409 implementation branch:
  1-2 POD sessions if a generic native/status-state change is needed.

Goal5409 fail-close branch:
  0.5 working session for decision doc, tests, and claim-boundary update.

Goal5410 consolidated review packet:
  0.5 working session after Goal5408/5409 artifacts exist.
```

POD must be used through the wrapper. Do not use naked SSH.

## 12. Current Claim Boundary

Allowed summary:

```text
X-HD has a strong Level-B public same-source scalar reproduction line and has
driven real generic RTDL system extraction. The scalar route matches author
HDResult on public Dragon -> HappyBuddha, and the fast scalar route is valid
for directed-Hausdorff/max-nearest value, with approximate per-source witnesses
under global-bound early break. Full paper reproduction is not complete.
Explicit -lb remains unsupported: the current RTDL full-cover surface is real
but still differs from the author raw offload stream by row count, hash, and
row identity.
```

Forbidden summary:

```text
Do not claim full X-HD paper reproduction.
Do not claim exact paper dataset reproduction.
Do not claim Figure 7 or Figure 11 reproduction.
Do not claim explicit -lb support.
Do not claim author performance parity or speedup.
Do not claim Goal5406 or Goal5407 closes the author raw offload stream.
Do not treat warm/diagnostic route numbers as default fresh performance.
Do not describe app-owned X-HD wrappers or comparators as RTDL core features.
```

## 13. Handoff Checklist

Latest artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5406_real_full_cover_surface_stream_gate_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5407_full_cover_delta_membership_probe_pod.json
```

Latest focused validation:

```text
$env:PYTHONPATH='src'; py -m unittest `
  tests.goal5407_full_cover_delta_membership_probe_test `
  tests.goal5406_real_full_cover_surface_stream_gate_test `
  tests.goal5405_full_cover_delta_status_bridge_test `
  tests.goal5394_full_cover_delta_status_probe_test

Ran 18 tests OK
```

Current next work:

```text
Goal5408: full-cover row identity / cell-id namespace reconciliation.
```

Current POD:

```text
host = 213.173.108.24
port = 13502
use scripts/current_pod_ssh.py only
```
