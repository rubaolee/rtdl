# Goal5213 Global-Bound Initial-State Matrix No-Go Result

Date: 2026-07-09

## Verdict

```text
completed_global_bound_initial_state_matrix_no_go__keep_local_grid_cell
```

## Purpose

Goal5211 changed the X-HD Level-B route execution model by adding a generic
global-bound early-break contract for max-nearest / directed-Hausdorff
reductions. After that change, the earlier initial-state conclusion needed to
be rechecked:

```text
Maybe a stronger initial state, even if expensive before, now unlocks more
global-bound early breaks and beats the local-grid-cell default.
```

This goal tests that question directly on the same public Stanford
Dragon -> HappyBuddha all-source Level-B gate.

## Workload

```text
dataset = public Stanford graphics/dragon -> graphics/happy_buddha
source_limit = all
grid_shape = 32,32,32
max_inline_points = 512
frontier_inline_nearest = true
global_bound_early_break = true
author comparator = Goal5186 author HDResult
route contract = directed-HD / max-nearest global-bound early break
```

Baseline:

```text
Goal5212 all-source no-copy
initial_state = local-grid-cell
```

Alternatives tested:

```text
nearest-cell-mbr
grid-cell-budget
grid-branch-bound
```

## POD Evidence

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05
remote repo = /root/rtdl_goal5093
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5213_global_bound_initial_nearest-cell-mbr_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5213_global_bound_initial_grid-cell-budget_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5213_global_bound_initial_grid-branch-bound_fresh_graphics_dragon_happy_buddha_2026-07-09.json
```

All tested routes:

```text
matched = true
distance = 0.12572988629271128
frontier_rows = 0
per_source_witness_exact = false
```

## Matrix

| route | matched | route wall | case total | full total incl load | seed phase | frontier phase | native total | OptiX launch | early breaks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local-grid-cell (Goal5212 baseline) | true | 0.851737s | 0.851749s | 1.530671s | 0.218570s | 0.427984s | 0.269847s | 0.038940s | 409376 |
| nearest-cell-mbr | true | 5.410375s | 5.410387s | 6.092041s | 4.791715s | 0.414451s | 0.255220s | 0.036825s | 417598 |
| grid-cell-budget | true | 7.282947s | 7.282959s | 7.963713s | 6.671402s | 0.409149s | 0.256744s | 0.037951s | 412211 |
| grid-branch-bound | true | 10.048697s | 10.048709s | 10.729135s | 9.435198s | 0.411652s | 0.254377s | 0.036008s | 417385 |

## Interpretation

The alternatives slightly reduce or roughly preserve the later frontier/native
phase, but they spend far more time producing the initial state:

```text
local-grid-cell seed        ~= 0.219s
nearest-cell-mbr seed       ~= 4.792s
grid-cell-budget seed       ~= 6.671s
grid-branch-bound seed      ~= 9.435s
```

The global-bound early-break contract does not make the heavier initial-state
strategies worthwhile on this workload. The later phase remains about
`0.41s`, while seed construction dominates the alternatives.

## Decision

Keep the current default:

```text
initial_state = local-grid-cell
```

Do not reopen:

```text
nearest-cell-mbr as default
grid-cell-budget as default
grid-branch-bound as default
```

unless a different workload, a different device-resident seed construction
model, or new evidence changes the seed-cost structure.

## Claim Boundary

Allowed:

```text
Under Goal5211 global-bound early break, local-grid-cell remains the best
tested initial-state strategy on the public Dragon -> HappyBuddha all-source
Level-B route.
```

Not authorized:

```text
full X-HD paper reproduction
exact paper dataset identity
author-vs-RTDL performance ratio
author parity
warm-only headline
claiming global-bound fails as a route optimization
X-HD-specific RTDL primitive
```

This goal is a no-go for heavier initial-state strategies. It does not weaken
Goal5211's global-bound early-break result.

## Next Recommendation

Stop initial-state retesting for this route. The next work should be one of:

1. consolidate and send Goals5211-5213 for review;
2. decide whether Goal5211 should become the X-HD Level-B route default under
   the explicit directed-HD / max-nearest contract;
3. if continuing performance, target a larger generic execution-model change,
   not another seed-state knob.
