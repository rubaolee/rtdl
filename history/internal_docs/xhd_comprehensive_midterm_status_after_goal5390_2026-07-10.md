# X-HD Comprehensive Midterm Status After Goal5390

Date: 2026-07-10

## Verdict

```text
midterm_status__level_b_scalar_strong__lb_denominator_mismatch_confirmed__full_paper_not_complete
```

This is the current X-HD status source after Goal5390. It supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5389_2026-07-10.md
```

## One-Line Status

X-HD is not fully reproduced yet. RTDL has strong bounded and Level-B
same-source scalar correctness evidence, and it has extracted real generic
system APIs, but exact paper inputs, figure-level denominators, and explicit
`-lb` status-machine parity remain open. Goal5390 confirms the current full
RTDL status stream does not match the author `-lb` trace denominator.

## What Is Complete

### Bounded Same-Input Correctness

Status:

```text
complete and externally reviewed through Goal5126
```

Meaning:

```text
author hd_exec JSON gate works;
RTDL route matches directed input1 -> input2 HDResult;
directed-vs-symmetric HD ambiguity is resolved;
bounded correctness is not full paper reproduction.
```

### Generic System Extraction

Status:

```text
nearest / witness / max-nearest extraction externally reviewed through Goals5127-5128
```

Reusable assets:

```text
pairwise L2 candidate rows;
nearest witness;
max-nearest reducer;
facility-service-radius non-Hausdorff consumer;
grid cell descriptors;
cell-MBR frontiers;
native 3-D cell-MBR OptiX front door;
inline-nearest payload state;
active-query status reference;
status-trace summary helper.
```

Important architecture result:

```text
Hausdorff is an app-level composition over generic primitives, not a hard-coded
RTDL core primitive.
```

### Level-B Same-Source Scalar Correctness

Strongest current representative route:

```text
source = public Stanford Dragon, 437645 points
target = public Stanford HappyBuddha, 543652 points
author HDResult = 0.12572988867759705
RTDL HDResult = 0.12572988629271128
abs diff ~= 2.38e-9
```

This is same-source representative evidence. It is not exact paper dataset
reproduction because paper-run input bytes/hashes are still unavailable.

Other bounded / same-source scalar matches exist for graphics and geo
fixtures, but none authorizes full Figure 5 or full-paper status.

## Best Route Progress

The representative Dragon -> HappyBuddha route evolved from a slow scalable
baseline into a fast generic route:

```text
initial scalable all-source route: about 7.30s
inline-nearest threshold 512: about 3.65s
intersection-stage current-best pruning: about 2.6s
dense local-grid lookup: about 2.26s
NumPy matrix input front door: about 1.24s
linear max-nearest reduction: about 1.17-1.18s
global-bound early-break fresh route: about 0.849s
explicit warm route median: about 0.362s
Goal5212 warm measured case total: about 0.288s
```

Claim boundary:

```text
fresh, warm, route, total, and author timings are different denominators;
do not report author-vs-RTDL speedup or slowdown ratio from these numbers.
```

Goal5211/5212 caveat:

```text
per_source_witness_exact = false
early-aborted sources = 409376 / 437645
```

Therefore the fast scalar route is valid for directed-HD / max-nearest value
under the explicit early-break contract, not as a generic exact witness route.

## What Is Not Complete

### Exact Paper Inputs

Status:

```text
not complete
```

Reason:

```text
paper input file bytes / hashes / deterministic reconstruction evidence are
missing for key graphics, geo, BraTS, OSM, and TIGER/Census workloads.
```

Rule:

```text
matching point counts, MBRs, Gini values, or scalar HDResult is useful
evidence, but it is not exact paper dataset identity.
```

### Figure-Level Reproduction

Status:

```text
not complete
```

Current disposition:

```text
Figure 5: Level-B scalar candidates exist; full matrix and denominator-aligned
          performance are not complete.
Figure 7: explicit -lb support is not complete.
Figure 8: radius strategy matrix is missing.
Figure 9: auto-tune variant denominator is missing.
Figure 10: scalability / overlap matrix is missing.
Figure 11: memory denominator is not aligned.
```

### Same-Denominator Performance

Status:

```text
not authorized
```

Reason:

```text
author internal Running.AvgTime;
author process wall;
RTDL route wall;
RTDL total;
cold process;
warm process;
prepared/explicit warmup;
```

are different measurement boundaries unless a specific gate aligns them.

## The Current Hard Problem: X-HD `-lb`

The current active blocker is no longer "can RTDL compute a directed HD scalar".
It can, for representative public inputs. The active hard problem is:

```text
Can RTDL reproduce the author's explicit -lb status-machine behavior through a
generic RTDL status-stream model?
```

### Author Oracle

Goal5387 author trace v2 reports:

```text
active_in_queue_size = 437645
raw_offload_rows_before_sort_reduce = 27133990
status_count_offloading_append = 27133990
raw_offload_row_hash = 4333109858711462591
raw_offload_row_sample_point_ids = [11168, 210712, 437119]
raw_offload_row_sample_cell_ids = [2924, 17, 17]
load_balance_feedback_update_count = 294
```

This is author-side evidence only. It does not prove RTDL support.

### RTDL Goal5390 Full Gate

Goal5390 now runs the full-source RTDL bridge with no `--source-limit` and emits
the generic trace summary:

```text
source_limit = null
source_limit_applied = false
active_query_count = 437645
row_count = 2188225
raw_offload_row_hash = 10510374331443640811
sample source_ids = [18080, 219488, 437599]
sample cell_ids = [6279, 6286, 6145]
```

Comparison:

```text
active_query_count_parity = true
row_count_parity = false
hash_parity = false
RTDL rows = 2188225
author rows = 27133990
row delta = 24945765
row ratio RTDL / author = 0.08064516129032258
```

Conclusion:

```text
The mismatch is not source-limited plumbing.
The current full-source RTDL status stream still does not match the author
status-machine stream.
Explicit -lb remains unsupported.
```

## Key Problems Already Solved

```text
1. Directed vs symmetric HD ambiguity resolved.
2. Hausdorff moved out of core into generic nearest/witness/reduction composition.
3. Full-public Level-B scalar route proven feasible without all-pair materialization.
4. Naive all-pair route rejected by scale evidence.
5. Many false route optimizations closed as no-go.
6. Author -lb oracle upgraded from count-only to v2 hash/sample/status trace.
7. RTDL now has generic active-query status and trace-summary APIs.
8. Full-source trace-summary comparison now exists and confirms the remaining mismatch.
```

## Key Problems Still Open

```text
1. Exact paper input provenance.
2. Explicit -lb status-machine parity.
3. Figure 7 / Figure 11 reproduction.
4. Same-denominator performance comparison.
5. Exact per-source witness semantics under global-bound early-break.
6. External review debt for the latest Goal5386-5390 packet.
```

## Planned Work

### Immediate: Review Packet

Send Goals5386-5390 for strict review:

```text
Goal5386: author trace v2 hook plan
Goal5387: author trace v2 execution
Goal5388: generic trace-summary contract
Goal5389: source-limited bridge trace-summary smoke
Goal5390: full-source bridge trace-summary gate
```

Review question:

```text
Does Goal5390 justify closing current explicit -lb support as unsupported unless
a genuinely new native multi-round status stream is implemented?
```

### Option A: Native Multi-Round Status Stream

Implement a real generic native multi-round active-query status stream that
changes the denominator, not just bridge formatting.

Required target:

```text
active count = 437645
raw offload rows -> 27133990
hash/sample comparison to author trace v2
status and feedback fields
```

### Option B: Fail-Closed `-lb` Closeout

If Option A is too app-specific or cannot be done generically, close explicit
`-lb` support honestly:

```text
RTDL currently reproduces representative scalar HD values, but not author
explicit -lb status-machine behavior.
```

### After The `-lb` Decision

Refresh the figure/claim matrix:

```text
Figure 5 Level-B scalar status;
Figure 7 load-balance status;
Figure 11 memory denominator status;
exact input blockers;
which RTDL APIs are reusable system improvements.
```

## POD Use Expectation

Use:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<command>"
```

Do not use naked SSH.

Expected next POD work:

```text
only for native multi-round status-stream attempt or validation;
not for more source-limited smoke;
not for bridge runtime optimization before denominator semantics improve.
```

## Forbidden Summaries

Do not say:

```text
X-HD full paper reproduction is complete.
RTDL supports X-HD -lb.
RTDL reproduces Figure 7 or Figure 11.
RTDL matches author RT-core behavior.
RTDL has author-vs-RTDL performance ratio evidence.
Goal5390 proves row parity.
Goal5390 proves hash/sample parity.
Goal5211 proves exact per-source witnesses.
Public files are exact paper datasets.
```

## Allowed Summary

```text
X-HD bounded correctness and generic system extraction are strong. RTDL matches
representative directed HD scalar values on full public Level-B inputs and has
reduced the scalar route substantially. Full paper reproduction is still open
because exact paper inputs, figure denominators, and explicit -lb behavior are
not complete. The latest full-source Goal5390 gate proves active-query count
alignment but row/hash mismatch against the author trace v2 oracle:
RTDL emits 2,188,225 offload rows while author emits 27,133,990. Therefore the
next decision is either implement a genuine generic native multi-round status
stream or close explicit -lb as unsupported under the current RTDL route.
```
