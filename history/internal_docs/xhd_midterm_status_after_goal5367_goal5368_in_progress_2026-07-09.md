# X-HD Midterm Status After Goal5367 / Goal5368 In Progress

Date: 2026-07-09

## One-Line Status

X-HD is no longer only a small bounded fixture: RTDL now has a strong
same-source representative Level-B line for public Stanford mesh workloads and
has extracted several generic system APIs.  Full paper reproduction is still
not complete because exact paper dataset identity, full figure matrices,
author RT-core option parity, and same-denominator performance ratios remain
unproven.

The current active front is author `-lb` / heavy-offload semantics.  RTDL
matches the author HD value on the Dragon -> AsianDragon `lb256` pair, but the
raw offload denominator is not aligned with the author `OffloadingSize`.

## Objective

The active objective remains:

```text
Complete X-HD paper reproduction: the Python/RTDL/partner implementation should
provide the same functionality as the paper author's original C++/CUDA/OptiX
implementation, and should provide comprehensive performance evaluation.  User
experience target: besides language, everything else is the same.
```

This objective is not achieved yet.  The work below is progress toward it, not
a narrowed completion criterion.

## Current Evidence Tiers

### Level A: bounded same-input value reproduction

Status: complete and externally reviewed through Goal5126.

What is proved:

- author `hd_exec` can be built/run on bounded fixtures;
- RTDL value routes match author `HDResult` on bounded 2-D / 3-D same-input
  gates;
- directed Hausdorff semantics were disambiguated with an asymmetric fixture:
  author and RTDL both compute directed input1 -> input2, not symmetric HD;
- the bounded X-HD line has proper claim boundaries and no performance/parity
  overclaim.

What is not proved:

- full X-HD algorithm parity;
- exact paper dataset reproduction;
- author RT-core implementation parity;
- performance parity.

### System extraction from the X-HD app

Status: complete and externally reviewed through Goals5127-5128.

System improvements already extracted:

- generic pairwise L2 candidate rows;
- generic nearest-witness reduction;
- generic max-nearest / covering-radius reduction;
- non-Hausdorff consumer proof via a facility-service-radius / worst-served
  demand fixture.

Meaning:

Hausdorff is treated as an app-level composition of generic nearest/reduction
primitives, not as an X-HD-specific RTDL core primitive.

### Level B: same-source representative public workloads

Status: strong but bounded to representative public inputs, not exact paper
inputs.

The strongest reviewed line is public Stanford Dragon -> HappyBuddha:

- author rerun on public data produced `HDResult = 0.12572988867759705`;
- RTDL route matched author rerun to about `2.4e-9`;
- paper-branch log differs from the author rerun by about `1.937e-7`, which is
  evidence that public data is not byte-identical to the paper's original input;
- Goal5211 global-bound early break greatly improved route time but made the
  route exact-value-only: per-source witnesses are approximate for most sources
  (`per_source_witness_exact=false`, early break count `409376 / 437645`).

Allowed summary:

```text
One Level-B same-source representative workload, Dragon -> HappyBuddha, matches
the author rerun HD scalar on public data.  This is exact for the directed-HD
maximum value but not for per-source witnesses, and it is not exact paper input
identity.
```

Forbidden summary:

```text
Full paper reproduction is complete.
RTDL matches the paper log exactly.
RTDL reproduces exact per-source witnesses at scale.
RTDL has author performance parity.
```

## Performance Progress Snapshot

The main public Dragon -> HappyBuddha route improved substantially across the
Level-B effort.

Important current numbers:

```text
Goal5203: route wall about 1.238-1.239s after direct NumPy matrix PLY input
Goal5204: route wall about 1.17-1.18s after linear max-nearest reduction
Goal5205: full gate total about 2.06s; route wall about 1.16-1.17s
Goal5207: explicit warm measured route about 0.626s after separate warmup
Goal5211: fresh route about 0.849s; explicit-warm route about 0.362s
Goal5212: full total including load about 1.531s; explicit-warm measured case
          total about 0.288s
```

These are not author ratios.  They have different denominators from author
`Running.AvgTime`, author process wall, or paper figure values.  No parity or
speedup ratio is authorized without aligned dataset, hardware, denominator,
phase boundary, and regime.

## Exact Dataset / Full Figure Status

Exact paper input identity is still unresolved.

Known facts:

- `/local/storage/shared/HDDatasets` is not available in the POD environment;
- public Stanford mesh data is available and useful for Level-B representative
  work;
- ModelNet40 and geospatial/public candidates were investigated, but they do
  not close exact paper dataset identity for the full paper matrix;
- ACM/supplement and public artifact sweeps produced mapping candidates and
  request/intake protocols, but no authoritative exact paper input package has
  been proven available;
- therefore Level C exact paper dataset reproduction and Level D figure
  reproduction remain incomplete.

## Author Option / RT-Core Feature Parity Work

After the Level-B value/performance line, the work moved to paper-author option
surface parity.

### Radius / tune-radius line

Completed / implemented through Goals5354-5362:

- audited author radius-growth schedules and trace metadata;
- built author-like radius queue references and RTDL diagnostic queue routes;
- mapped narrow `-tune_radius adaptive` behavior for internal diagnostic use.

Current boundary:

- narrow adaptive/nonterminal-trace mapping is available as an internal
  diagnostic;
- general author `-tune_radius` support is not claimed;
- Figure 8 reproduction is not claimed.

### `-lb` / heavy-offload line

Current active line: Goals5363-5367 completed/implemented, Goal5368 in progress.

#### Goal5363: author semantics audit

Author behavior from source:

```text
lb=0   -> processing_threshold = UINT32_MAX, offload disabled
lb=N   -> cells with point_count > N are appended to the offload queue
rows   -> author queue row shape is effectively (in_queue_idx, cell_id)
memory -> WL Heavy Peak = OffloadingSize * 2 * sizeof(uint32_t)
```

#### Goal5364: author Dragon -> AsianDragon lb pair

Temporary Level-B input:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
exact_paper_dataset_identity_proven = false
```

Author `lb0`:

```text
HDResult       = 52.453487396240234
OffloadingSize = 0
WL Heavy Peak  = 0
```

Author `lb256`:

```text
HDResult       = 52.453487396240234
OffloadingSize = 27133990
WL Heavy Peak  = 217071920
Radius         = 79.2156982421875
NumInputPoints = 437645
```

#### Goal5365: RTDL lb counterpart behavior gate

RTDL `lb0` disabled route:

```text
max_inline_points      = 4294967295
HDResult               = 52.453491321261296
heavy_offload_peak_rows = 0
route wall             = about 1.657s
```

RTDL `lb256` full-cover route:

```text
max_inline_points       = 256
HDResult                = 52.453491321261296
heavy_offload_peak_rows = 24508120
author-width bytes      = 196064960
generic uint64 bytes    = 392129920
route wall              = about 38.408s
```

Behavior-level gate passed: `lb0` has zero offload rows, `lb256` has positive
offload rows, and both preserve the HD value within tolerance.

What did not pass:

```text
author OffloadingSize rows = 27133990
RTDL heavy rows            = 24508120
RTDL / author              = 0.9032258064516129
```

#### Goal5366: denominator reconciliation

Result:

```text
status     = lb_denominator_reconciliation_ready__row_count_parity_not_established
exit_label = lb_denominator_reconciled_shape_aligned__row_count_parity_not_established
```

The byte formula shape is compatible:

```text
author bytes = OffloadingSize * 2 * sizeof(uint32_t)
             = 27133990 * 2 * 4
             = 217071920

RTDL author-width candidate bytes = heavy_offload_peak_rows * 2 * sizeof(uint32_t)
                                  = 24508120 * 2 * 4
                                  = 196064960
```

But row-count parity is not established.  The observed delta is not explained
by RTDL host duplicate collapse in the Goal5365 artifact because raw attempted
count, emitted count, and heavy rows are equal.

#### Goal5367: author-radius probe

Purpose:

Test whether setting RTDL's radius to the author iteration radius explains the
row-count denominator gap.

Result:

```text
Author lb256:
  HDResult       = 52.453487396240234
  OffloadingSize = 27133990
  radius         = 79.2156982421875

RTDL lb256 full-cover:
  HDResult                = 52.453491321261296
  heavy_offload_peak_rows = 24508120
  radius                  = 266.9466183641096

RTDL lb256 author-radius probe:
  HDResult                = 52.453491321261296
  heavy_offload_peak_rows = 21006960
  radius                  = 79.2156982421875
```

Conclusion:

```text
Radius alignment preserves the HD value but does not close denominator parity.
It reduces RTDL heavy rows and moves farther from author OffloadingSize.
The gap is not caused merely by scalar radius mismatch.
```

Next target:

```text
align author queue / in_queue / cmin2 / raw offload iteration semantics
```

## Goal5368 In Progress: Raw Frontier Kind-Count Telemetry

Problem discovered:

For large no-inline/count-only probes, materializing frontier rows can exceed
memory.  Running with `row_capacity=0` currently tells us only total attempted
frontier rows.  It does not tell us how many attempted rows are offload kind2.

Observed diagnostic before Goal5368:

```text
Dragon -> AsianDragon
radius = author lb256 radius
max_inline_points = 256
frontier_inline_nearest = false
frontier_row_capacity = 0

Result:
  fail_closed_overflow
  attempted total frontier rows = 589961522
```

This number is useful but insufficient because it is all raw frontier kinds,
not just offload rows.  The author denominator is `OffloadingSize`, i.e. raw
offload queue rows.

Implemented so far in Goal5368:

- generic native raw frontier kind counters in OptiX cell-MBR frontier;
- new memory telemetry v3 getter:

```text
rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3
```

- new telemetry fields:

```text
raw_frontier_kind_counts
raw_frontier_kind1_rows
raw_frontier_kind2_rows
raw_frontier_kind3_rows
```

- Python front door support:

```text
allow_overflow_telemetry=True
```

Default behavior remains fail-closed.  Only explicit diagnostics return
overflow telemetry without returning rows.

Validation so far:

Local:

```text
py -m py_compile src/rtdsl/optix_runtime.py
py -m unittest tests.goal5368_cell_mbr_frontier_kind_count_telemetry_test
Ran 3 OK
```

POD:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
POD_OK
GPU = NVIDIA RTX 4000 Ada Generation, 550.127.05

make build-optix
success
```

Small POD smoke:

```text
constructed 1 query + 3 cells with one inline, one offload, one pruned row
row_capacity = 0
allow_overflow_telemetry = True

result:
  overflowed = true
  attempted_count = 3
  valid_count = 0
  schema = rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v3
  raw_frontier_kind_counts = {"1": 1, "2": 1, "3": 1}
```

Status:

```text
Goal5368 is implemented at the API/native level and has local + small-POD smoke
evidence, but the large Dragon -> AsianDragon count-only probe has not yet been
rerun after the user requested this midterm report.
```

## Current Claim Boundary

Allowed now:

```text
RTDL can match author HD value on bounded gates and selected same-source
representative public inputs.

RTDL has extracted generic nearest/frontier/reduction primitives from X-HD.

For Dragon -> AsianDragon lb256, RTDL preserves HD value and has compatible
heavy-offload byte formula shape, but row-count parity is not established.

Goal5368 adds generic raw frontier kind-count telemetry and can support the
next denominator-alignment probe.
```

Not allowed:

```text
Full X-HD paper reproduction is complete.
Exact paper dataset identity is proven.
Figure 5/6/7/8/9/10/11 reproduction is complete.
Author RT-core algorithm parity is proven.
Explicit -lb support is complete.
Row-count parity for OffloadingSize is proven.
Same-denominator memory parity is proven.
RTDL/author performance ratio is fair or final.
Per-source witnesses are exact under the Goal5211 early-break route.
```

## Major Problems Solved

1. Bounded value reproduction and directed-HD definition.
2. Generic system extraction of nearest/witness/reduction primitives.
3. Public Level-B value match on at least one large representative graphics
   workload.
4. Major route performance improvements from matrix loading, packed coordinate
   reuse, linear max-nearest reduction, native inline nearest, and global-bound
   early break.
5. App/core boundary discipline: X-HD-specific wrappers/comparators/options
   remain in the app; generic primitives stay in RTDL system layers.
6. POD SSH operating error was fixed by the wrapper rule; current POD access
   works through `scripts/current_pod_ssh.py`.
7. Author `-lb` semantics are now understood at source level.
8. Goal5368 now supplies the missing low-level telemetry needed to measure raw
   offload kind rows without materializing huge row tables.

## Major Problems Not Yet Solved

1. Exact paper datasets remain unavailable / unproven.
2. Full figure matrix reproduction is not complete.
3. Author RT-core option parity is incomplete.
4. `-lb` row denominator parity is not established.
5. `-tune_radius` support is narrow/internal, not general author option
   compatibility.
6. Goal5211 high-performance route is exact-value-only and has approximate
   per-source witnesses.
7. Fair performance comparison is still blocked by denominator / hardware /
   dataset / phase-boundary differences.
8. Some recent goals are implemented or internally documented but not all have
   completed external review.

## Next Work Plan

### P0: Finish Goal5368

Tasks:

1. rerun Dragon -> AsianDragon count-only probe after v3 telemetry;
2. collect raw kind counts:

```text
raw_frontier_kind1_rows
raw_frontier_kind2_rows
raw_frontier_kind3_rows
```

3. compare `raw_frontier_kind2_rows` with author `OffloadingSize=27133990`;
4. write:

```text
history/internal_docs/goal5368_xhd_cell_mbr_raw_kind_count_telemetry_result_2026-07-09.md
history/internal_docs/call_for_review_goal5368_xhd_cell_mbr_raw_kind_count_telemetry_2026-07-09.md
```

Expected outcomes:

- If raw kind2 count is close to author OffloadingSize, the gap is mostly
  downstream of row materialization/sort/unique or route shape.
- If raw kind2 count remains far from author OffloadingSize, the gap is in
  author iteration state: in_queue/cmin2/radius/queue ordering/offload emission
  semantics.

### P1: Author-queue-aligned lb trace

Build a route or diagnostic that aligns more of the author iteration state:

```text
in_queue_idx
cmin2 / current best state
raw offload queue rows
iteration-by-iteration radius
author offload denominator
```

This is the next likely hard semantic target if Goal5368 shows raw kind2 still
does not match.

### P2: Explicit `-lb` option gate

Only after denominator alignment evidence:

- authorize or reject explicit app-level `-lb` compatibility;
- keep generic RTDL core free of X-HD-specific option names;
- document exact allowed/forbidden claims.

### P3: Broader paper matrix / exact dataset work

Continue exact dataset and artifact work in parallel only when it does not
compete with the active semantic denominator gate:

- exact paper dataset acquisition remains the main Level-C blocker;
- if exact data remains unavailable, keep results Level-B / representative;
- do not inflate representative public data into exact paper reproduction.

### P4: Fair performance matrix

After functional/semantic alignment:

- define aligned denominator;
- separate author internal AvgTime, author wall, RTDL route, RTDL total, cold
  process, warm process, and explicit warmup regimes;
- only report ratios when the denominator is actually aligned.

## POD Use Plan

Current POD:

```text
host = 213.173.108.24
port = 13502
remote workspace = /tmp/rtdl_goal5364
GPU = NVIDIA RTX 4000 Ada Generation
```

Required operating rule:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 upload <local> <remote>
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 download <remote> <local>
```

Do not use naked SSH.

Expected next POD commands:

```text
cd /tmp/rtdl_goal5364
make build-optix
PYTHONPATH=src python3 <Goal5368 large probe>
```

Expected POD outputs:

```text
results/xhd_goal5368_*.json
raw_frontier_kind_counts with kind2 offload denominator
```

## Review / Handoff Notes

Suggested next review packet after Goal5368:

```text
Goals5363-5368: X-HD lb/heavy-offload semantics and denominator packet
```

Core questions for review:

1. Does the author `-lb` semantics audit correctly identify the denominator?
2. Does RTDL's raw kind2 telemetry measure the same shape, or a different
   denominator?
3. Is explicit `-lb` still unauthorized?
4. Is any performance/memory ratio still forbidden?
5. Does Goal5368 remain generic RTDL system telemetry rather than an X-HD
   special case?

## Bottom Line

The project has made real movement toward "same functionality except language":
bounded correctness, public representative correctness, system API extraction,
fast generic routes, and author-option semantic audits are all in place.

The current blocking technical issue is not value correctness.  RTDL can match
the author HD value on the current `lb` pair.  The issue is whether the RTDL
generic cell-MBR/offload pipeline can reproduce the author's raw heavy-offload
queue denominator for `-lb`.  Goal5368 is the immediate tool to answer that
without materializing hundreds of millions of frontier rows.
