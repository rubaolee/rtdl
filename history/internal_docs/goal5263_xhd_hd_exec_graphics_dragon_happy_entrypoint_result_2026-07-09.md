# Goal5263 - X-HD hd_exec Entrypoint Graphics Dragon/HappyBuddha Result

Date: 2026-07-09

## Objective

Run the full-public Stanford Graphics Dragon -> HappyBuddha Level-B
representative pair through the RTDL `hd_exec`-compatible user entrypoint.

Goal5260 already established all-400 public ModelNet40 coverage through the
same entrypoint family. Goal5263 extends that user-facing entrypoint evidence
to a graphics workload that appears in the paper target matrix.

## POD Setup

POD:

```text
NVIDIA RTX 4000 Ada Generation
remote worktree = /tmp/rtdl_goal5236
```

The remote worktree was missing the public Stanford PLY data files, so the two
local public same-source candidates were uploaded:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply
Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip.ply
```

Remote sizes:

```text
dragon_vrip.ply = 33M
happy_vrip.ply  = 41M
```

## Author Comparator

Author rerun evidence from Goal5186:

```text
author_hd_result = 0.12572988867759705
point counts = 437645 / 543652
level = level_b_same_source_candidate_only
exact_paper_dataset_reproduction_claimed = false
```

Author artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
```

## Commands

Fast scalar route:

```text
cd /tmp/rtdl_goal5236
export PYTHONPATH=src:.
export LD_LIBRARY_PATH=build:${LD_LIBRARY_PATH:-}
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply \
  -input2 Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip.ply \
  -n_dims 3 \
  -input_type ply \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5263_dragon_happy_hd_exec_fast_scalar.json \
  --rtdl-route cell-mbr-fast-scalar \
  --grid-shape 32,32,32 \
  --max-inline-points 512 \
  --translate-each-input-to-min-bound
```

Exact-witness route:

```text
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py \
  -input1 Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply \
  -input2 Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip.ply \
  -n_dims 3 \
  -input_type ply \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5263_dragon_happy_hd_exec_exact_witness.json \
  --rtdl-route cell-mbr-exact-witness \
  --grid-shape 32,32,32 \
  --max-inline-points 512 \
  --translate-each-input-to-min-bound
```

Downloaded artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_fast_scalar_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json
```

## Results

Fast scalar route:

```text
route_label = cell-mbr-fast-scalar
HDResult = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09
matched author within 1e-6 = true
point_count_a = 437645
point_count_b = 543652
preprocessing = translate_each_input_to_min_bound
per_source_witness_exact = false
RTDL route wall = 536.2212583422661 ms
entrypoint total = 1.2787706404924393 s
```

Exact-witness route:

```text
route_label = cell-mbr-exact-witness
HDResult = 0.12572988629271128
author_abs_diff = 2.3848857610975216e-09
matched author within 1e-6 = true
point_count_a = 437645
point_count_b = 543652
preprocessing = translate_each_input_to_min_bound
per_source_witness_exact = true
RTDL route wall = 620.9204494953156 ms
entrypoint total = 1.3659364730119705 s
```

## What This Proves

This proves that the RTDL `hd_exec`-compatible user entrypoint can run a
full-public Stanford Graphics PLY representative workload, not just bounded WKT
fixtures and ModelNet40 OFF inputs.

It also proves two route modes for the same user-facing entrypoint:

```text
cell-mbr-fast-scalar: fast HDResult route, witnesses may be approximate
cell-mbr-exact-witness: exact per-source witness route, same HDResult
```

## Claim Boundary

Allowed:

```text
The RTDL hd_exec-compatible entrypoint matched the author rerun HDResult for the
full-public Stanford Dragon -> HappyBuddha Level-B representative pair under
both fast-scalar and exact-witness route labels.
```

Allowed with caveat:

```text
The exact-witness route reports per_source_witness_exact=true. The fast-scalar
route reports per_source_witness_exact=false but matches HDResult.
```

Forbidden:

```text
exact paper byte-input identity proved
full X-HD paper reproduction complete
Figure 5-11 reproduced
author RT-core algorithm equivalence
author performance parity or speedup
same-source public representative = exact paper dataset
```

## Validation

```text
py -m unittest tests.goal5263_xhd_hd_exec_graphics_dragon_happy_pod_artifact_test
```

Result:

```text
Ran 4 tests in 0.032s
OK
```

## Status

```text
implemented_review_pending
```

## Next Recommended Work

1. Send Goal5263 for strict review, or fold it into the Goals5255-5263
   user-entrypoint review packet.
2. If approved, use `run_xhd_rtdl_hd_exec.py` as the single primary RTDL entry
   for both ModelNet40 and Stanford Graphics representative workloads.
3. Continue remaining full-paper blockers: exact paper byte-input identity,
   missing paper datasets/Figures, and author internal AvgTime algorithm gap.
