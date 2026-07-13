# X-HD Midterm Status After Goal5368

Date: 2026-07-09

## One-Line Status

The X-HD line has moved well beyond a bounded toy fixture: RTDL now has
externally reviewed bounded same-input correctness, generic nearest /
witness / max-nearest system primitives, strong Level-B same-source public
workload evidence, and a working author-option semantics program for
`tune_radius` and `lb` diagnostics.

Full X-HD paper reproduction is still not complete. Exact paper input identity,
full figure matrices, author RT-core option parity, and same-denominator
performance ratios remain unclosed.

The current active technical blocker is `-lb` / heavy-cell offload denominator
alignment. Goal5368 proves the author `OffloadingSize` is not equal to all raw
RTDL kind2/offload rows under the same scalar radius; the next step must align
author iterative queue state (`in_queue_idx`, `cmin2`, radius schedule, and raw
offload emission semantics).

## Objective

The active objective remains:

```text
Complete X-HD paper reproduction: the Python/RTDL/partner implementation should
provide the same functionality as the paper author's original C++/CUDA/OptiX
implementation, and should provide comprehensive performance evaluation.
User-facing target: besides language, everything else is the same.
```

This objective is not achieved yet. The current work is a disciplined advance
toward it, not a narrowed replacement for it.

## Status By Evidence Level

### Level A - Bounded Same-Input Value Reproduction

Status: complete and externally reviewed through Goal5126.

Proved:

- author `hd_exec` can be built and run on bounded fixtures;
- RTDL value routes match author `HDResult` on bounded 2-D and 3-D same-input
  gates;
- directed Hausdorff semantics were disambiguated with an asymmetric fixture;
- author and RTDL both compute directed input1 -> input2, not symmetric HD;
- bounded X-HD claim boundaries are in place.

Not proved:

- full X-HD algorithm parity;
- exact paper dataset reproduction;
- author RT-core implementation parity;
- author-vs-RTDL performance parity.

### System Extraction From X-HD

Status: externally reviewed through Goals5127-5128.

Extracted generic RTDL assets:

- pairwise L2 candidate rows;
- nearest-witness reduction;
- max-nearest / covering-radius reduction;
- non-Hausdorff genericity proof through a facility-service-radius /
  worst-served-demand fixture.

Meaning:

```text
Hausdorff remains an app-level composition.
RTDL core exposes generic nearest / witness / reduction primitives.
```

### Level B - Same-Source Representative Public Workloads

Status: strongest current functional evidence, but still not exact paper input
identity.

Primary public Level-B candidate:

```text
source = Stanford Dragon public mesh
target = Stanford HappyBuddha public mesh
```

Key facts:

- author rerun on public data produced `HDResult=0.12572988867759705`;
- RTDL route matched author rerun to about `2.4e-9`;
- public data still differs from the paper-branch log by about `1.937e-7`;
- therefore this is representative same-source evidence, not byte-identical
  exact paper input evidence.

Important Goal5211 caveat:

```text
Goal5211 global-bound early break is exact for the final directed-HD scalar
value, but per-source witnesses may be approximate.

per_source_witness_exact = false
early_aborted_sources    = 409376 / 437645
```

Allowed summary:

```text
One Level-B same-source representative workload, Dragon -> HappyBuddha,
matches the author rerun HD scalar on public data. This is exact for the
directed-HD maximum value, but not for per-source witnesses, and not for exact
paper input identity.
```

Forbidden summary:

```text
Full paper reproduction is complete.
RTDL matches the paper log exactly.
RTDL reproduces exact per-source witnesses at scale under Goal5211.
RTDL has author performance parity.
```

## Performance Progress Snapshot

The Level-B public Dragon -> HappyBuddha route has been substantially improved,
but no author ratio is authorized.

Representative route evolution:

```text
Goal5188: initial full-public RTDL route wall about 7.30s
Goal5191: inline512 route wall about 3.65s
Goal5195: intersection-stage current-best pruning about 2.6s
Goal5196: dense local-grid lookup about 2.26s
Goal5203: direct NumPy matrix input about 1.238-1.239s
Goal5204: linear max-nearest reduction about 1.17-1.18s
Goal5205: full gate total about 2.06s, route about 1.16-1.17s
Goal5207: explicit warm measured route about 0.626s after separate warmup
Goal5211: fresh route about 0.849s, explicit-warm route about 0.362s
Goal5212: full total including load about 1.531s,
          explicit-warm measured case total about 0.288s
```

These are RTDL route/regime numbers, not paper speedup ratios.

No author-vs-RTDL performance ratio is authorized because the denominators are
not aligned:

- author internal `Running.AvgTime`;
- author process wall;
- RTDL route wall;
- RTDL full case total;
- cold process;
- warm long-lived process;
- explicit warmup / measured case.

## Current Paper Figure Status

Current high-level figure status:

```text
Figure 5:
  partially explored with Level-B graphics and bounded geo candidates;
  no full figure matrix reproduction;
  no exact input status;
  no author-vs-RTDL ratio.

Figure 6:
  pruning / route diagnostics exist;
  no full paper figure reproduction.

Figure 7:
  author lb audit and Level-B lb diagnostics exist;
  exact lb comparison matrix is not reproduced.

Figure 8:
  tune_radius source / trace semantics partially mapped;
  narrow diagnostic adaptive mapping exists;
  no full Figure 8 add/double/adaptive matrix reproduction.

Figure 9:
  current author logs do not provide the required four-variant matrix;
  checked-in PDF is evidence but not a reproducible denominator.

Figure 10:
  source/scripts audited;
  checked-in scalability logs are missing;
  not reproduced.

Figure 11:
  memory denominator audit completed;
  RTDL generic offload telemetry exists;
  same-denominator author Figure 11 memory parity remains false.
```

Exact paper dataset identity remains unresolved. Public files and same-source
candidates are useful Level-B evidence; they must not be promoted to Level-C
exact paper inputs without file/hash or equivalent provenance.

## Author Option / RT-Core Feature Parity

### `tune_radius`

Implemented / review pending through Goals5354-5362:

- generic `radius_growth_step` / `radius_growth_trace` helper;
- author trace mapping for add/double/adaptive schedule math;
- route radius trace metadata;
- author-like queue reference;
- bounded and nonterminal queue trace matches;
- narrow internal mapping of explicit `-tune_radius adaptive` only when backed
  by a nonterminal author trace.

Allowed:

```text
RTDL has a narrow internal diagnostic mapping for adaptive tune_radius.
```

Not allowed:

```text
General author tune_radius support.
Figure 8 reproduction.
Author RT-core algorithm parity.
Performance or full-paper claims from tune_radius work.
```

### `lb` / Heavy-Cell Offload

Active line: Goals5363-5368 implemented / review pending.

Author semantics pinned from source:

```text
lb=0 -> processing_threshold = UINT32_MAX, offload disabled
lb=N -> cells with point_count > N are appended to the offload queue
offload row shape -> (in_queue_idx, cell_id)
WL Heavy Peak -> OffloadingSize * 2 * sizeof(uint32_t)
```

Current Level-B author pair:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
preprocessing = translate_each_input_to_min_bound
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

RTDL `lb0` disabled counterpart:

```text
HDResult                = 52.453491321261296
heavy_offload_peak_rows = 0
route wall              = about 1.657s
```

RTDL `lb256` full-cover counterpart:

```text
HDResult                = 52.453491321261296
heavy_offload_peak_rows = 24508120
author-width bytes      = 196064960
generic uint64 bytes    = 392129920
route wall              = about 38.408s
```

Behavior-level gate passed:

```text
lb0 has zero offload rows;
lb256 has positive offload rows;
both preserve the author HD value within tolerance.
```

Denominator parity did not pass:

```text
author OffloadingSize rows = 27133990
RTDL full-cover heavy rows = 24508120
RTDL / author             = 0.9032258064516129
```

Goal5367 tested scalar radius alignment:

```text
RTDL author-radius heavy rows = 21006960
author OffloadingSize        = 27133990
```

Conclusion:

```text
Scalar radius alignment preserves value but does not close row-count parity.
```

Goal5368 tested raw no-inline kind2 rows:

```text
author OffloadingSize       = 27133990
RTDL raw kind2/offload rows = 304981889
RTDL / author               = 11.239846738352892
```

Conclusion:

```text
Author OffloadingSize is not simply all raw RTDL kind2/offload rows under the
same scalar radius. The missing denominator is author iterative queue state.
```

## Goal5368 Implementation Summary

Goal5368 adds a generic native telemetry feature:

```text
rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3
```

New telemetry fields:

```text
raw_frontier_kind_counts
raw_frontier_kind1_rows
raw_frontier_kind2_rows
raw_frontier_kind3_rows
```

Python front-door diagnostic flag:

```text
allow_overflow_telemetry=True
```

Default behavior remains fail-closed. Overflow telemetry is available only when
explicitly requested for diagnostics.

Validation:

```text
local py_compile OK
focused local unittest packet: Ran 22 tests OK
POD preflight OK
POD make build-optix OK
small POD smoke returned raw kinds {"1":1,"2":1,"3":1}
large Dragon -> AsianDragon count-only probe completed
```

POD:

```text
host = 213.173.108.24
port = 13502
remote workspace = /tmp/rtdl_goal5364
GPU = NVIDIA RTX 4000 Ada Generation
```

Important artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_dragon_asian_lb256_author_radius_noinline_kind_count_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json
history/internal_docs/goal5368_xhd_cell_mbr_raw_kind_count_telemetry_result_2026-07-09.md
history/internal_docs/call_for_review_goal5368_xhd_cell_mbr_raw_kind_count_telemetry_2026-07-09.md
history/internal_docs/call_for_review_goals5363_5368_xhd_lb_heavy_offload_packet_2026-07-09.md
```

## Major Problems Solved

1. Bounded same-input value reproduction and directed-HD definition are closed.
2. Generic nearest / witness / max-nearest pipeline has been extracted from the
   X-HD app and proved with a non-Hausdorff consumer.
3. Public Level-B Dragon -> HappyBuddha scalar value match is strong.
4. The RTDL route has improved dramatically while retaining app/core boundary
   discipline.
5. Exact pairwise materialization at full scale has been avoided through
   generic grid/cell-MBR/frontier/native inline-nearest work.
6. Author `tune_radius` semantics are partially mapped with a narrow internal
   diagnostic route.
7. Author `lb` source semantics are pinned.
8. RTDL can preserve the author HD value under lb0/lb256 behavior-level
   diagnostics.
9. Generic raw frontier kind telemetry now gives us kind2/offload counts
   without materializing hundreds of millions of rows.
10. POD access is operational through `scripts/current_pod_ssh.py`; the prior
    key-auth failure mode is documented and should not be repeated.

## Major Problems Not Yet Solved

1. Exact paper dataset files / hashes remain unavailable or unproven.
2. Full figure matrix reproduction remains incomplete.
3. `-lb` row denominator parity is not established.
4. Explicit `-lb` support remains unauthorized.
5. Same-denominator Figure 11 memory parity remains false.
6. General author `tune_radius` support remains unauthorized.
7. Goal5211 high-performance route is exact-value-only; per-source witnesses
   may be approximate.
8. Author-vs-RTDL performance ratio remains unauthorized.
9. Many recent goals are implemented / review pending, not externally approved.
10. The current `lb` route gap has moved from value correctness to author queue
    state semantics.

## Immediate Review Packet

Send Goals5363-5368 for strict review:

```text
history/internal_docs/call_for_review_goals5363_5368_xhd_lb_heavy_offload_packet_2026-07-09.md
```

Main review questions:

1. Did Goal5363 correctly pin author `lb` / heavy-cell offload semantics?
2. Does Goal5365 only prove behavior-level value/offload contrast, not
   denominator parity?
3. Does Goal5366 correctly separate byte formula shape from row-count parity?
4. Does Goal5367 correctly reject scalar radius mismatch as the sole cause?
5. Does Goal5368 correctly show raw kind2/offload rows are not the author
   `OffloadingSize` denominator?
6. Is explicit `-lb` still unauthorized?
7. Are Figure 7 / Figure 11 / memory / performance claims still forbidden?
8. Is Goal5368 generic RTDL telemetry rather than an X-HD-specific primitive?

## Planned Work

### P0 - Review and lock the current lb packet

Action:

```text
Send Goals5363-5368 for strict external review.
```

Expected result:

```text
Either approve the current conclusion that -lb remains unsupported, or require
amendments before any further lb work.
```

### P1 - Author-queue-aligned lb trace gate

Build the next diagnostic around the real missing denominator:

```text
in_queue_idx
per-iteration active queue
cmin2 / current-best state
radius schedule
raw offload queue rows
author-width byte view
```

Starting evidence:

- Goal5361 proves author-like queue traces can be matched for nonterminal
  `tune_radius` using generic nearest/witness reference semantics;
- Goal5368 proves raw all-kind/kind2 counting alone is not enough;
- therefore the next gate must align queue state, not just scalar radius or
  cell point-count threshold.

Possible implementation shape:

```text
1. audit which author JSON fields expose enough queue state;
2. if JSON lacks per-source cmin2/in_queue, reconstruct RTDL queue state by
   actually executing the previous iteration nearest computation;
3. emit comparable author-like rows:
     Iteration, Radius, NumInputPoints, NumOutputPoints, CMax2,
     OffloadingSize, WL Heavy Peak candidate;
4. compare against the author Dragon -> AsianDragon lb256 trace where available.
```

Exit labels:

```text
lb_queue_denominator_aligned__consider_narrow_lb_option_mapping
lb_queue_denominator_still_unmatched__lb_option_remains_unsupported
lb_queue_state_unavailable__requires_author_instrumentation_or_deeper_route
```

### P2 - Explicit `-lb` option decision

Only after P1:

```text
decide whether explicit -lb can be supported under a narrow diagnostic route
or must remain fail-closed.
```

No support should be added merely because value correctness passes. The option
surface must be tied to the denominator semantics if it claims author option
compatibility.

### P3 - Full-paper dataset / figure work

Continue only under strict labels:

```text
Level B representative public data != exact paper input
paper-log value match != file/hash provenance
checked-in author PDF != reproducible denominator
```

Priority:

1. exact dataset provenance if available;
2. otherwise clearly labeled Level-B representative matrices;
3. no figure-level claims without exact or externally accepted denominator.

### P4 - Fair performance matrix

After functional/semantic alignment:

```text
separate author Running.AvgTime;
separate author process wall;
separate RTDL route time;
separate RTDL total time;
separate load/setup/output;
separate cold, warm, and explicit warmup regimes.
```

Only report a ratio if all relevant denominators are aligned.

### P5 - System API follow-through

Keep extracting only generic reusable features:

```text
allowed:
  generic frontier telemetry;
  generic queue/offload row schema;
  generic radius-growth schedule;
  generic cell-MBR traversal / nearest state / max-nearest reduction.

not allowed:
  X-HD-specific primitive in src/rtdsl or src/native;
  author flag semantics in RTDL core;
  figure-specific memory fields as system semantics.
```

## POD Use Plan

Use the wrapper, never naked SSH:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 upload <local> <remote>
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 download <remote> <local>
```

Known current remote state:

```text
remote workspace = /tmp/rtdl_goal5364
author / RTDL data = /tmp/xhd_goal5234/data/dragon.ply
                     /tmp/xhd_goal5234/data/asian_dragon.ply
native build       = make build-optix already completed recently
```

Expected next POD usage:

1. validate any new queue-aligned lb diagnostic in `/tmp/rtdl_goal5364`;
2. rebuild OptiX only if native files change;
3. download JSON artifacts into `Paper-reproduction-apps/x-hd-paper/results/`;
4. write a goal report and call-for-review before changing claim status.

## Current Claim Boundary

Allowed now:

```text
RTDL matches author HD values on bounded gates and selected same-source
representative public workloads.

RTDL has generic nearest / witness / frontier / telemetry primitives extracted
from X-HD pressure.

For Dragon -> AsianDragon lb256, RTDL preserves HD value and has compatible
heavy-offload byte formula shape, but row-count parity is not established.

Goal5368 shows raw RTDL kind2/offload rows are about 11.24x author
OffloadingSize under the author scalar radius.
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

## Bottom Line

The project is in a productive but unfinished state. Value correctness is no
longer the main problem on the active X-HD lb pair: RTDL already preserves the
author HD scalar under `lb0` and `lb256` style routes.

The hard problem is now semantic denominator alignment. Author `OffloadingSize`
is an iterative queue-state counter, not merely a scalar-radius heavy-cell row
count. Goal5368 proves this by showing that raw no-inline RTDL kind2 rows under
the author radius are about `11.24x` the author denominator. The next real work
is therefore an author-queue-aligned lb trace, not another scalar-radius,
materialization, or formatting probe.
