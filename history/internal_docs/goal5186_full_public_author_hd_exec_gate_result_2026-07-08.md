# Goal5186 - X-HD Full Public Author hd_exec Gate

Date: 2026-07-08

## Verdict

```text
completed_full_public_author_hd_exec_gate__level_b_only__implemented_review_pending
```

Goal5186 runs the author `hd_exec` binary on the full public Stanford
Dragon/HappyBuddha candidate identified in Goal5178, then compares the produced
`HDResult` against the author paper-branch log value for the same workload name.

This is Level B same-source author evidence. It is not exact paper dataset
identity, not RTDL all-source route completion, not full paper reproduction, and
not a performance ratio.

## Why This Goal Exists

Goals5180-5185 validated increasing bounded Dragon source subsets against the
full public HappyBuddha target using exact subset oracles. Goal5185 reached
source_limit `8192`, where the exact subset oracle already evaluates
`4453597184` point pairs and takes about `62.34s`.

The next useful evidence boundary is therefore not a larger exact oracle by
default. It is an external author comparison for the same full public
Dragon/HappyBuddha candidate.

## Inputs

Author log workload from Goal5178:

```text
target: graphics_dragon_happy_buddha
author paper-branch path A: /local/storage/shared/HDDatasets/graphics/dragon.ply
author paper-branch path B: /local/storage/shared/HDDatasets/graphics/happy_buddha.ply
paper-branch HDResult: 0.12572969496250153
```

Public Level B candidates:

```text
Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply
  points: 437645
  SHA256: FEA87FF48F2ABA22FB53E7B67C3FF3F7B8C2A3B3A0653AF62C48BBA67C6D5744

Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip.ply
  points: 543652
  SHA256: 2283371216D748A08376A3C88698E283CC8F18D10CED348D6D133051BCF217AB
```

The point counts match the author paper-branch logs exactly. The file bytes are
not proved identical to the author's `/local/storage/shared/HDDatasets` files.

## Implementation

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py
```

The script deliberately does **not** compute an RTDL exact reference. The full
candidate has:

```text
437645 * 543652 = 237926579540 directed point pairs
```

Instead, it:

1. reads the Goal5178 priority input bridge;
2. resolves the full public Dragon/HappyBuddha PLY paths;
3. optionally runs author `hd_exec`;
4. loads author JSON `HDResult`;
5. compares that value to the paper-branch author-log `HDResult`;
6. writes a bounded Level B summary with claim flags.

New test:

```text
tests/goal5186_xhd_full_public_author_gate_test.py
```

The test uses a tiny temporary bridge and fake author JSON to verify that the
gate compares author JSON to paper-log HDResult without requiring or claiming
an RTDL exact/all-source route.

## POD Run

POD:

```text
root@213.173.108.24 -p 13502
GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
```

Author binary:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
```

This is the same author build lineage documented in Goal5112:

```text
OptiX dev headers v9.0.0 -> v7.7.0 for POD driver ABI compatibility
cuda::proclaim_return_type wrappers around three Thrust transform_reduce lambdas
```

Command:

```text
cd /root/rtdl_goal5093

/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  -input1 Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply \
  -input2 Paper-reproduction-apps/x-hd-paper/data/external/stanford/happy_recon/happy_vrip.ply \
  -n_dims 3 \
  -input_type ply \
  -variant rt \
  -execution gpu \
  -json Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_hd_exec_goal5186_graphics_dragon_happy_buddha_2026-07-08.json \
  -overwrite=true \
  -check=false
```

The command succeeded.

## Evidence Artifacts

Raw author JSON:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_hd_exec_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
```

Summary:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
```

Key values:

```text
author_input_point_counts = [437645, 543652]
author_hd_result = 0.12572988867759705
paper_log_hd_result = 0.12572969496250153
paper_log_min_abs_diff = 1.9371509552001953e-07
tolerance = 1e-6
matched = true
author_running_avg_time_ms = 7.823
author iterations = 2
```

Author JSON phase details:

```text
Iteration 1:
  NumInputPoints = 437645
  NumOutputPoints = 150
  RTTime = 2.828 ms
  CUDATime = 0.804 ms
  OffloadingSize = 58994

Iteration 2:
  NumInputPoints = 150
  NumOutputPoints = 0
  RTTime = 0.465 ms
  CUDATime = 0.193 ms
  OffloadingSize = 4427
```

## Why This Is Not Full Paper Reproduction

This goal does **not** prove exact paper dataset identity:

```text
author logs provide paths and point counts but not input file hashes;
local public files use Stanford archive names, not the author's
  /local/storage/shared/HDDatasets/graphics bytes;
no author conversion script/hash proves byte identity.
```

It also does **not** run the RTDL all-source route. Goals5180-5185 only validate
bounded source subsets up to `8192` Dragon source rows against the full target.

## Claim Boundary

This goal claims:

- author `hd_exec` successfully ran on the full public Stanford
  Dragon/HappyBuddha Level B candidate;
- the author `HDResult` from that run matches the paper-branch author-log
  `HDResult` within `1e-6`;
- the public files are a strong Level B same-source candidate because point
  counts and author HDResult align.

This goal does **not** claim:

- exact paper dataset reproduction;
- full paper reproduction;
- Figure 5 reproduction;
- RTDL all-source route completion;
- RTDL exact reference for the full candidate;
- author-vs-RTDL speedup or parity;
- denominator-aligned performance ratio.

## Validation

Commands:

```text
py -m unittest \
  tests.goal5186_xhd_full_public_author_gate_test \
  tests.goal5182_xhd_explicit_frontier_capacity_test \
  tests.goal5181_xhd_full_public_subset_scaling_gate_test \
  tests.goal5180_xhd_full_public_feasibility_gate_test

py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_author_gate.py \
  --bridge Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json \
  --author-json Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_hd_exec_goal5186_graphics_dragon_happy_buddha_2026-07-08.json \
  --output Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json \
  --run-goal Goal5186 \
  --tolerance 1e-6
```

Result:

```text
Ran 8 tests in 9.032s
OK

matched = True
author_hd_result = 0.12572988867759705
```

Known local Python noise:

```text
Could not find platform independent libraries <prefix>
```

The commands exit successfully despite this environment message.

## Manifest Update

Updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

The manifest now includes the Goal5186 raw author JSON and summary under
`evidence.result_artifacts`.

## Next Recommended Goal

Goal5187 should choose one of two honest next boundaries:

1. **RTDL all-source route attempt** for the same full public candidate, using
   the scalable route without exact oracle validation and comparing only to the
   Goal5186 author HDResult; or
2. **author/route phase matrix** that places Goal5186 author `Running.AvgTime`
   beside existing bounded-subset RTDL evidence without ratio claims.

The stronger next step is option 1, but it must be labeled carefully:

```text
route-only all-source RTDL run compared to author HDResult;
not exact-oracle validated;
not exact paper dataset identity;
not a performance ratio unless denominator alignment is separately reviewed.
```
