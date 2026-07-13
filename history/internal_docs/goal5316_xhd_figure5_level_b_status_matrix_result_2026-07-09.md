# Goal5316 - X-HD Figure-5 / Level-B Status Matrix

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5316 consolidates the current X-HD Figure-5-like evidence into one
status-bearing matrix. The goal is not to add a new route or claim Figure 5
reproduction. It makes the current evidence easier to audit by separating:

- exact paper input availability;
- same-source public candidate availability;
- author paper-config scalar evidence;
- RTDL scalar / witness evidence;
- performance denominator availability;
- allowed claim;
- current blocker.

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5316_figure5_level_b_status_matrix.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5316.figure5_level_b_status_matrix.v1
```

## Matrix Rows

The matrix has 8 rows:

```text
graphics_dragon_happy_full_public
graphics_dragon_asian_scaled_author_no_go
graphics_thai_happy_scaled
graphics_thai_asian_scaled
geo_county_zcta_bounded
geo_county_zcta_full_public_probe
geo_water_bg_bounded
geo_water_bg_full_public_corrected
```

## Key Consolidated Conclusions

### 1. No Exact Paper Input Provenance

Every row has:

```text
exact_paper_input_available = false
```

The strongest rows are Level-B same-source or bounded evidence. None proves
author paper input file/hash recovery.

### 2. No Figure-5 Completion

The global claim boundary remains:

```text
figure5_reproduction_complete = false
exact_paper_dataset_reproduction_complete = false
full_paper_reproduction_complete = false
```

This is a status matrix, not a figure reproduction claim.

### 3. No Performance Ratio

The matrix explicitly carries:

```text
author_vs_rtdl_performance_ratio_authorized = false
rows_with_denominator_aligned_performance_ratio = []
```

Reasons remain familiar:

- author `Running.AvgTime` / `ReportedTime`;
- author process wall;
- RTDL route time;
- RTDL total including input;
- warm vs fresh route;

are different denominators.

### 4. Strongest Current Graphics Row

```text
graphics_dragon_happy_full_public
```

Evidence:

```text
paper-log HDResult       = 0.12572969496250153
author rerun HDResult    = 0.12572988867759705
RTDL HDResult            = 0.12572988629271128
RTDL vs author abs diff  = 2.3848857610975216e-09
```

Boundary:

```text
Level-B full-public same-source scalar directed-HD match.
Exact-value-only for the early-break route.
```

Carry-forward caveat:

```text
global_bound_early_break = true
per_source_witness_exact = false
```

### 5. Dragon -> Asian Remains A No-Go Candidate

```text
graphics_dragon_asian_scaled_author_no_go
```

Evidence:

```text
paper-log HDResult    = 0.06536811590194702
author rerun HDResult = 0.06545527279376984
abs diff              = 8.715689182281494e-05
```

This row blocks further RTDL timing on the current public/scaled mapping unless
new input provenance appears.

### 6. Thai Graphics Rows Are Level-B Scalar Matches

ThaiStatuette-scaled -> HappyBuddha:

```text
author rerun HDResult       = 0.21912431716918945
RTDL exact / fast HDResult  = 0.2191243235042005
abs diff vs author          = 6.335011043523409e-09
```

ThaiStatuette-scaled -> AsianDragon-scaled:

```text
author rerun HDResult       = 0.28763842582702637
RTDL exact / fast HDResult  = 0.2876384148709406
abs diff vs author          = 1.0956085760849277e-08
```

Boundary:

```text
Level-B same-source scaled graphics scalar match only.
No exact paper input, no Figure 5, no ratio.
```

The matrix also preserves the witness distinction:

```text
exact-witness route: per_source_witness_exact = true
fast-scalar route:   per_source_witness_exact = false
```

### 7. Geo Bounded Rows Stay Bounded

County -> ZCTA bounded:

```text
author HDResult = 65.44752502441406
RTDL HDResult   = 65.44751976280666
abs diff        = 5.2616073986655465e-06 <= 1e-5
```

WaterBodies -> BlockGroups bounded:

```text
author HDResult = 72.38665008544922
RTDL HDResult   = 72.38664516014835
abs diff        = 4.925300871150284e-06 <= 1e-5
```

Boundary:

```text
bounded same-fixture scalar correctness only
```

These rows are not full-public, exact, representative, or performance evidence.

### 8. County -> ZCTA Full-Public Probe Blocks Exact Promotion

Goal5309 showed:

```text
County paper point count   = 9,438,045
County observed point count = 12,477,179
delta                      = +3,039,134 (+32.2009%)
```

The MBRs match paper logs to within `1e-5` degrees, but point-count mismatch
blocks exact or Figure-5 promotion for the current public County source.

### 9. Strongest Current Geo Row

```text
geo_water_bg_full_public_corrected
```

Corrected author denominator:

```text
author hd_exec full-public WKT with n_points_cell=8
```

Evidence:

```text
paper-log HDResult                         = 0.8964367508888245
author paper-config n_points_cell=8 result = 0.8964367508888245
RTDL exact-witness float64                 = 0.8964380566690101
same witness float32                       = 0.8964367508888245
abs diff float64 vs author float32         = 1.305780185645311e-06
declared tolerance                         = 2e-6
```

Boundary:

```text
Full-public WaterBodies->BlockGroups reproduces the author paper-config scalar
with n_points_cell=8. RTDL exact-witness float64 matches author/paper float32
within the explicit numeric boundary.
```

Still forbidden:

```text
exact paper WKT file recovery
Figure-5 completion
performance parity
identical internal numeric precision
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5316_figure5_level_b_status_matrix.json
py -m unittest tests.goal5316_xhd_figure5_level_b_status_matrix_test
```

Observed result:

```text
Ran 8 tests in 0.005s
OK
```

The local Python launcher printed:

```text
Could not find platform independent libraries <prefix>
```

This is the known Windows environment noise and did not affect test success.

## Claim Boundary

Allowed summary:

```text
Current X-HD evidence includes multiple Level-B same-source or bounded scalar
matches, including full-public Dragon->HappyBuddha and full-public
WaterBodies->BlockGroups under the paper-config author denominator. Exact
paper input files or hashes are still unavailable, Figure 5 is not complete,
and no author-vs-RTDL performance ratio is authorized.
```

Forbidden summaries:

```text
Figure 5 is reproduced.
Full X-HD paper reproduction is complete.
Exact paper datasets have been recovered.
RTDL has author performance parity or a speedup ratio.
Level-B public or bounded fixtures are the exact paper inputs.
The global-bound early-break route provides exact per-source witnesses.
```

## Next Work

Immediate:

```text
Send Goals5313-5316 for strict review.
```

After review, choose one:

```text
1. Input provenance: continue exact paper dataset search / file-hash recovery.
2. Figure-5 coverage: fill remaining exact-public candidate gaps, but only
   after author value prechecks.
3. Performance denominator: design a fair same-denominator matrix, if possible.
4. System extraction: promote proven generic pieces, not X-HD-specific wrappers.
```

## POD Use

Goal5316 did not use POD. It is an evidence consolidation goal.

POD is only needed if reviewers request reruns or if a new author/RTDL route is
executed.
