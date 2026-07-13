# Goal5237 Graphics Dragon -> AsianDragon Scaled All-Source Route-Only Result

Date: 2026-07-09

## Verdict

`implemented__all_source_scaled_route_matches_author_scaled_hdresult__review_pending`

Goal5237 advances the Dragon -> AsianDragon line from bounded subsets to an
all-source RTDL route-only run over the full scaled public candidate:

```text
source = public Dragon, 437,645 points
target = scaled public AsianDragon, 3,609,600 points
backend = optix
author comparator = Goal5234 scaled-public author HDResult
author HDResult = 0.06536787003278732
paper-log HDResult = 0.06536811590194702
```

The successful route uses:

```text
preprocessing = translate_each_input_to_min_bound
global_bound_early_break = false
frontier_row_capacity = 5,000,000
```

It matches the author scaled-public HDResult:

```text
RTDL route distance = 0.06536787240753439
author scaled HDResult = 0.06536787003278732
author_abs_diff = 2.3747470656587666e-09
matched = true
```

It also remains within `1e-6` of the paper-branch log value:

```text
paper-log HDResult = 0.06536811590194702
RTDL-vs-paper-log abs diff ~= 2.434944126277097e-07
```

This is a major correctness step, but it is not yet full X-HD paper
reproduction: exact paper input byte identity remains unproved and performance
denominators are not author-aligned.

## Evidence Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/
  xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_no_global_early_break_pod_2026-07-09.json
  xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_translated_pod_2026-07-09.json
  xhd_goal5237_graphics_dragon_asian_dragon_scaled_all_source_optix_route_only_no_translate_pod_2026-07-09.json
```

The first artifact is the passing route. The other two are diagnostic no-go
runs and are retained because they define the required preprocessing and exact
mode.

## Current-Source / POD Hygiene

Goal5237 reuses the current-source POD tree created by Goal5236:

```text
remote source root = /tmp/rtdl_goal5236
rebuilt library = /tmp/rtdl_goal5236/build/librtdl_optix.so
sha256 = e29f6b523530fa8a5e382f3bb2d64fc93f2f14868a9bf1b9005fde8c649ab1bb
OptiX SDK = /root/vendor/optix-dev
CUDA = /usr/local/cuda-12.8
```

This is not an old `/tmp/rtdl_goal5144` snapshot run.

## Successful All-Source Route

Command shape:

```bash
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py \
  --bridge /tmp/xhd_goal5236/bridge_scaled_remote.json \
  --profile /tmp/xhd_goal5236/profile.json \
  --backend optix \
  --source-limits all \
  --grid-shape 32,32,32 \
  --source-selection-policy evenly-spaced \
  --translate-each-input-to-min-bound \
  --max-inline-points 512 \
  --initial-state local-grid-cell \
  --local-grid-seed-executor numba \
  --frontier-nearest-executor numba \
  --frontier-row-order native \
  --frontier-inline-nearest \
  --frontier-row-capacity 5000000 \
  --skip-exact-oracle \
  --author-hd-result 0.06536787003278732 \
  --author-tolerance 1e-6
```

Result:

```text
matched = true
match_basis = author_hd_result
author_abs_diff = 2.3747470656587666e-09

route distance/source/target =
  0.06536787240753439 / 49577 / 1803033

full source count = 437,645
full target count = 3,609,600

frontier rows = 3,306,122
frontier attempted rows = 3,306,122
frontier row capacity = 5,000,000

total candidate distance evaluations = 6,417,800,660
per_source_witness_exact = true
global_bound_early_break = false
full_all_source_route_run = true
full_pairwise_rows_materialized = false
```

Phase timings:

```text
load_full_inputs = 0.5014200136065483s
direction_total = 30.49027620255947s
  grid_cell_mbrs = 0.5977412909269333s
  initial_state_seed = 0.9031352773308754s
  frontier_rows = 0.8221020475029945s
  nearest_continuation = 28.124958105385303s
  max_nearest_reduction = 0.0007915198802947998s
total wall = 31.252301812171936s
```

The current route bottleneck is the frontier nearest continuation, not OptiX
frontier row production.

## Diagnostic No-Go Runs

### No independent min-bound translation

```text
preprocessing = []
matched = false
route distance = 0.1597462345977575
author_abs_diff = 0.09437836456497017
route source/target = 106413 / 769049
```

This shows the author-compatible RTDL route requires the app-owned
`translate_each_input_to_min_bound` preprocessing used by the successful gate.

### Translation plus global-bound early break

```text
preprocessing = translate_each_input_to_min_bound
global_bound_early_break = true
matched = false
route distance = 0.06647010360490425
author_abs_diff = 0.0011022335721169313
per_source_witness_exact = false
global_bound_early_break_count = 419,820
```

This shows `global_bound_early_break` is not valid for exact all-source
HDResult reproduction. It can be a diagnostic/performance pruning mode, but it
must not be used for exact-value paper reproduction claims.

## Interpretation

Goal5237 establishes the first all-source RTDL route-only HDResult match for a
large X-HD paper-log graphics workload candidate:

```text
Dragon -> scaled AsianDragon
RTDL all-source route-only HDResult ~= author scaled-public HDResult
```

This closes the bounded-subset limitation for this workload's scalar value,
under the current Level-B same-source candidate contract.

It also identifies two crucial execution-mode rules:

1. Use app-owned independent min-bound translation for this author-compatible
   public candidate route.
2. Disable global-bound early break for exact-value reproduction.

## Claim Boundary

Allowed:

```text
RTDL all-source route-only matches the author scaled-public HDResult for the
Dragon -> scaled AsianDragon same-source candidate within 1e-6.
```

Not allowed:

```text
full X-HD paper reproduction complete
exact paper input byte identity proved
Figure 6 reproduced
author-vs-RTDL performance parity
global-bound early break is exact for all-source HDResult
per-source witnesses remain exact when global-bound early break is enabled
```

## What Remains

1. External review for Goals5233-5237.
2. A fair performance matrix against the author on the same scaled-public
   candidate and denominator, if possible.
3. A decision on whether the independent min-bound translation is the correct
   documented author-compatible app preprocessing contract or a route-specific
   normalization that needs deeper source-code provenance.
4. Further paper targets beyond this single graphics workload.
5. Exact input byte-identity remains unproved.
