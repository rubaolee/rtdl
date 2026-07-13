# Goal5264 - X-HD hd_exec Entrypoint Graphics Dragon/AsianDragon Result

Date: 2026-07-09

## Objective

Extend the RTDL `hd_exec`-compatible user entrypoint to a second Stanford
Graphics representative workload:

```text
Dragon -> AsianDragon scaled 1e-3
```

Goal5263 already established the same user entrypoint on Dragon -> HappyBuddha.
Goal5264 checks that the entrypoint also runs a larger target-side graphics
case through the exact-witness route.

## POD Setup

POD:

```text
NVIDIA RTX 4000 Ada Generation
remote worktree = /tmp/rtdl_goal5236
```

The remote worktree already had:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply
```

The scaled same-source candidate was uploaded from local:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon_scaled_1e-3.ply
size = 43,315,372 bytes
sha256 = 4F98D1F809CFB6DCB448E469FDD94A606DE17B45CCB160F5CD1A5423508F01FE
```

The scaling candidate was created in Goal5234 from:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon.ply
scale = 0.001
vertex_count = 3,609,600
```

## Author Comparator

Author rerun evidence from Goal5239:

```text
author_hd_result = 0.06536787003278732
paper_log_hd_result = 0.06536811590194702
point counts = 437645 / 3609600
level = level_b_same_source_candidate_only
exact_paper_dataset_reproduction_claimed = false
```

The paper-log drift remains visible:

```text
abs(author_rerun - paper_log) ~= 1.937e-7
```

That drift is evidence against claiming exact paper byte-input identity.

## Command

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply \
  -input2 Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon_scaled_1e-3.ply \
  -n_dims 3 \
  -input_type ply \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5264_dragon_asian_hd_exec_exact_witness.json \
  --rtdl-route cell-mbr-exact-witness \
  --grid-shape 32,32,32 \
  --max-inline-points 512 \
  --translate-each-input-to-min-bound
```

Downloaded artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json
```

## Result

```text
route_label = cell-mbr-exact-witness
HDResult = 0.06536787240753439
author_abs_diff = 2.3747470656587666e-09
rtdl_vs_paper_log_abs_diff ~= 2.4349441263282756e-07
matched author rerun within 1e-6 = true
point_count_a = 437645
point_count_b = 3609600
preprocessing = translate_each_input_to_min_bound
per_source_witness_exact = true
RTDL route wall = 2651.0526463389397 ms
entrypoint total = 3.399467781186104 s
```

Phase notes:

```text
grid_cell_mbrs = 0.45714739710092545 s
initial_state_seed = 2.1878338530659676 s
nearest_continuation = 0.001045040786266327 s
frontier_rows = 0.000015139579772949219 s
max_nearest_reduction = 0.0005937442183494568 s
```

This route used the exact seed path:

```text
initial_state = grid-branch-bound
initial_seed_executor = native_cuda
exact_seed_frontier_skipped = true
per_source_witness_exact = true
```

## What This Proves

This proves that the RTDL `hd_exec`-compatible user entrypoint can run another
Stanford Graphics PLY representative workload with a much larger target point
set than Dragon -> HappyBuddha.

It also proves that the exact-witness route matches the author rerun scalar
`HDResult` for this Level-B same-source/scaled candidate:

```text
abs(RTDL - author rerun) ~= 2.37e-9
```

## What This Does Not Prove

This does not prove:

```text
exact paper byte-input identity
full X-HD paper reproduction
Figure 5-11 reproduction
author RT-core algorithm equivalence
author performance parity or speedup
same-source/scaled public representative = exact paper dataset
```

The route wall is denominator-labeled diagnostic evidence only. It must not be
reported as author performance parity because the relevant denominators differ:

```text
RTDL route wall = selected RTDL route wall inside the Python app
RTDL entrypoint total = RTDL load + route + JSON process path
author process wall = author executable process wall from Goal5239
author internal AvgTime = author internal X-HD timing field from Goal5239
```

## Validation

```text
py -m unittest tests.goal5264_xhd_hd_exec_graphics_dragon_asian_pod_artifact_test
```

Expected assertions:

```text
RTDL HDResult matches author rerun within 1e-6
RTDL HDResult does not hide paper-log drift
point counts and preprocessing match the Level-B contract
per_source_witness_exact = true
claim boundary flags remain false
README and manifest record the evidence without promoting it to exact paper
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goal5264 for strict review, or fold it into the Goals5255-5264
   user-entrypoint review packet.
2. Treat `run_xhd_rtdl_hd_exec.py` as the primary RTDL entrypoint for bounded
   WKT, public ModelNet40/OFF, and Stanford Graphics/PLY representative gates.
3. Continue the remaining full-paper blockers: exact paper byte-input identity,
   missing paper datasets/Figures, and author internal AvgTime algorithm gap.
