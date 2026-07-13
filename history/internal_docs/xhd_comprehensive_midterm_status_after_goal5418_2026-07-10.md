# X-HD Comprehensive Midterm Status After Goal5418

## Current Verdict

```text
level_b_scalar_strong__figure5_level_b_matrix_packet_ready__exact_datasets_missing__no_ratio_authorized__full_paper_not_complete
```

This report supersedes the earlier Goal5414/Goal5417 midterm packets for
handoff and planning. It includes the current completed work, implemented
review-pending work, active blockers, and planned next goals after Goal5418.

## Project Objective

The active project remains X-HD paper reproduction with system extraction:

```text
Use X-HD as a paper-app pressure test to improve RTDL as a general spatial
language/system, while reproducing the paper only to the degree supported by
input provenance, author contracts, and denominator-aligned evidence.
```

Two bars must both be tracked:

1. **Reproduction bar**: match author/paper behavior on identified inputs and
   figures, with clear phase boundaries and no hidden regime changes.
2. **System bar**: extract reusable, app-neutral RTDL primitives from the app
   work; paper-specific wrappers, comparators, tolerances, datasets, and figure
   claims remain app-owned.

## High-Level Status

Full X-HD paper reproduction is **not complete**.

What is strong:

- bounded same-input HDResult reproduction is complete and externally reviewed
  through Goal5126;
- directed input1-to-input2 Hausdorff semantics are proved by a discriminating
  fixture;
- generic nearest/witness/max-nearest extraction is complete through
  Goals5127-5128;
- Level-B public/representative scalar correctness is strong for multiple
  graphics and bounded geo cases;
- Dragon -> HappyBuddha remains the strongest full-public Level-B graphics
  line;
- Goal5417 defines a clean Figure-5-like Level-B matrix plan;
- Goal5418 now turns that plan into a dry-run same-POD graphics command packet.

What is not complete:

- exact paper input file/hash provenance;
- exact Figure 5 full matrix;
- Figure 6/7/8/9/10/11 reproduction;
- denominator-aligned author-vs-RTDL performance ratio;
- author RT-core algorithm equivalence;
- explicit `-lb` support.

## Completed And Reviewed Foundation

### Bounded X-HD Value Reproduction

Goals5111-5126 closed bounded same-input value reproduction. The key semantic
gate was the directed-vs-symmetric fixture:

```text
directed a->b = 0.5
directed b->a = 9.0
symmetric     = 9.0
author HDResult matched directed a->b
RTDL matched directed a->b
```

This proves the paper app's bounded comparison contract is directed
input1-to-input2, not symmetric Hausdorff.

### Generic System Extraction

Goals5127-5128 extracted Hausdorff into app-neutral primitives:

```text
pairwise L2 distance candidate rows
nearest witness
max-nearest distance/witness reduction
```

Goal5128 supplied a non-Hausdorff facility/service-radius consumer, closing the
genericity concern for the max-nearest reduction path.

## Implemented, Review Pending Mainline

### Level-B Graphics And Geo Evidence

The project expanded beyond bounded same-input gates into Level-B same-source
or bounded representative evidence:

- Dragon -> HappyBuddha full-public Stanford graphics;
- ThaiStatuette-scaled -> HappyBuddha;
- ThaiStatuette-scaled -> AsianDragon-scaled;
- bounded County -> ZCTA WKT fixture;
- bounded WaterBodies -> BlockGroups WKT fixture.

These are scalar correctness/value-matching lines. They are **not** exact paper
input reproduction.

### X-HD Route/System Work

The X-HD line produced genuine reusable RTDL assets:

- generic grid cell descriptors and cell MBRs;
- generic cell-MBR frontier rows;
- native 3-D cell-MBR frontier collection;
- nearest-state frontier split;
- native inline-nearest payload pruning;
- coordinate-matrix front doors;
- generic max-nearest reducer improvements;
- app-owned PLY/WKT front doors;
- heavy/offload worklist schema and telemetry prototypes;
- payload-transition trace contract and synthetic non-app summary proof.

The strongest current Level-B Dragon -> HappyBuddha scalar route evidence
includes:

```text
author rerun HDResult ~= paper-branch author-log HDResult
RTDL HDResult matches author rerun within ~2.4e-9
```

The optional global-bound early-break route improves scalar directed-HD value
time but is exact-value-only:

```text
per_source_witness_exact = false
most per-source witnesses may be approximate under early abort
```

Therefore it must not be described as exact witness reproduction.

## The Explicit `-lb` Line Is Stopped

The `-lb` / load-balance row-identity line was investigated deeply and then
stopped.

Self-assessment:

```text
The post-dataset-blocker `-lb` / route micro-engineering line consumed many
goals chasing an implementation-level author offload stream.  That stream is
not needed for the scalar HDResult evidence already achieved, and its only
direct paper-figure use is blocked by unavailable exact datasets and missing
same-denominator logs.  Treating this as the default next attack was a
project-direction mistake; the correct current status is fail-closed under the
existing RTDL execution model.
```

Any future continuation must first name an app-neutral payload/status
transition, prove it with non-X-HD evidence, and then pass bounded gates before
returning to X-HD.  It must not resume as another X-HD-specific row-identity
reverse-engineering line.

Key evidence:

```text
Goal5406 RTDL full-cover rows = 24,508,120
Goal5387 author raw rows      = 27,133,990
delta                         = 2,625,870 = 6 * active_count
```

Goal5407 showed the gap is not just row count:

```text
sample author source/cell rows were not present in the RTDL full-cover surface
```

Goal5408 ruled out a simple compact/original cell-id namespace remap.

Goal5411 tried the bounded statused-deferral bridge and failed to recover the
author sample rows. Goal5412 fail-closed explicit `-lb` under the current
model. Goal5415 stopped the current line and returned the project to full
reproduction blockers.

Preserved system work:

```text
generic payload-transition trace contract
payload_transition_trace_summary_numpy_columns(...)
synthetic non-app behavior proof
```

Not authorized:

- explicit X-HD `-lb` support;
- Figure 7 reproduction;
- Figure 11 reproduction;
- author row/hash parity;
- memory/performance ratio;
- full paper reproduction.

## Current Goal5417/5418 Figure 5 Track

### Goal5417: Matrix Plan

Goal5417 defines a Figure-5-like Level-B same-POD matrix plan.

Primary graphics candidates:

```text
dragon_happy
thai_happy_scaled
thai_asian_scaled
```

Secondary bounded geo candidates:

```text
county_zcta_bounded
water_bg_bounded
```

Excluded:

```text
dragon_asian_scaled   author rerun does not match paper-branch log
brats_category        input provenance/access blocked
full_geo_county_zcta  full-public County count differs from paper by +32.2%
```

The plan requires separate denominator columns and authorizes no ratios.

### Goal5418: Execution Packet Readiness

Goal5418 creates the dry-run graphics execution packet:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json
```

It generates:

```text
3 graphics cases
9 graphics commands total
0 executed matrix rows
```

The packet includes author `hd_exec` commands and RTDL `run_xhd_rtdl_hd_exec.py`
commands for the primary graphics cases. It defers the bounded geo rows because
they use a different partner/Triton runner family.

The RTDL graphics commands carry the required public-graphics preprocessing:

```text
required_rtdl_preprocessing = ["translate_each_input_to_min_bound"]
all RTDL graphics commands include --translate-each-input-to-min-bound
```

This is required by the prior Dragon/HappyBuddha and ThaiStatuette gates.
Omitting it changes the scalar HDResult and invalidates the Level-B graphics
matrix row.

Goal5418 is readiness only:

```text
dry_run_only = true
same_pod_execution_claimed = false
matrix_rows_executed = 0
```

## Current Claim Boundary

Allowed:

- bounded same-input correctness;
- Level-B same-source/representative scalar correctness;
- app-owned command packets;
- route-local RTDL timing columns;
- author timing columns side-by-side;
- no-ratio phase matrices.

Forbidden:

- "full X-HD paper reproduced";
- "Figure 5 reproduced";
- "RTDL is X times faster/slower than author" without denominator review;
- promoting public/representative data to exact paper input status;
- treating early-break scalar routes as exact per-source witness routes;
- treating synthetic payload-transition traces as X-HD `-lb` support.

## Key Solved Problems

1. Directed Hausdorff semantics are established.
2. Bounded same-input author/RTDL scalar matching is complete.
3. Hausdorff has been decomposed into reusable nearest/witness/reduction
   primitives.
4. Level-B scalar correctness exists across graphics and bounded geo examples.
5. The explicit `-lb` row-identity chase has been stopped instead of allowed to
   keep consuming the project.
6. Figure 5 Level-B execution has been planned and packaged for same-POD
   graphics execution.

## Key Unsolved Problems

1. Exact paper datasets are still missing or unproven.
2. Figures 5-11 remain unreproduced under exact paper denominators.
3. Full author RT-core algorithm equivalence is not proven.
4. Explicit `-lb` support remains unsupported.
5. Figure 11 memory denominators remain not aligned.
6. Performance ratios remain unauthorized.
7. Many recent goals are implemented / review pending and need batch review.

## Immediate Next Plan

### Goal5419 - Run Graphics Matrix On POD

Input:

```text
Goal5418 command packet
```

Requirements:

```text
current POD endpoint
wrapper preflight passes
author hd_exec available
graphics input files present under /tmp/xhd_goal5298/data
RTDL route runner available
```

Execution discipline:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

Expected output:

- author `HDResult` and timing JSON for the three graphics cases;
- RTDL route JSON for each planned graphics route;
- value match status;
- author internal timing, author process wall, RTDL route wall, RTDL process
  wall, RTDL input load, witness exactness, and cold/warm regime as separate
  fields;
- `ratio_authorized=false`.

### Goal5420 - Matrix Interpretation / No-Ratio Review Packet

After Goal5419:

- consolidate all graphics rows;
- verify value matches;
- classify exact-witness vs exact-value-only routes;
- refuse ratios unless denominator alignment is separately reviewed;
- decide whether bounded geo should get a separate execution packet.

### Goal5421 - Figure Status Refresh

Refresh figure-by-figure status:

- Figure 5: Level-B matrix status after Goal5419/5420;
- Figure 7: blocked / `-lb` stopped;
- Figure 8/9/10: author denominator missing or incomplete;
- Figure 11: denominator not aligned;
- exact dataset acquisition blockers.

## POD Usage Expectation

No POD is needed to read this report or review Goal5418.

POD is needed for Goal5419. The expected use is:

1. run wrapper preflight;
2. execute author graphics commands;
3. execute RTDL graphics route commands;
4. fetch result JSONs;
5. build a local result matrix;
6. run local JSON/tests/report generation.

Do not use naked SSH. If authentication fails, first verify wrapper key usage
before declaring the POD bad.

## Expected Time Arrangement

Assuming a healthy POD and existing uploaded inputs:

```text
Goal5419 POD preflight and command execution: 1-3 hours depending on route cost
Goal5420 consolidation/report/tests:          30-60 minutes
Goal5421 status refresh:                      30-60 minutes
External review batch:                        after Goal5421
```

If the POD lacks inputs or author build:

```text
add 1 setup/repair goal before Goal5419 execution
do not rewrite the claim boundary
```

## Review Questions

1. Does this report correctly state that full X-HD paper reproduction remains
   incomplete?
2. Does it correctly summarize the completed/reviewed foundation through
   Goal5128 and the implemented-review-pending line after that?
3. Does it correctly fail-close the current explicit `-lb` line?
4. Does it correctly treat Goal5418 as dry-run readiness only?
5. Are the Goal5419/5420/5421 next steps properly ordered?
6. Does the report avoid Figure 5, exact dataset, full paper, and performance
   ratio overclaims?
7. Is the POD usage expectation concrete enough?
