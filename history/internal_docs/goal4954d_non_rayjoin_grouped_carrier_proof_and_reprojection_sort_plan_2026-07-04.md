# Goal4954-D Non-RayJoin Grouped Carrier Proof And Reprojection/Sort Plan

Date: 2026-07-04

Status: completed_pending_review

Parent:

- `history/internal_docs/goal4954c_grouped_carrier_prototype_results_2026-07-04.md`
- Antigravity verdict: `approve_goal4954c_grouped_carrier_win_continue`

Exit label requested:

`non_rayjoin_grouped_carrier_proven__reprojection_sort_plan_ready`

## Purpose

Goal4954-D answers the governance question left open by Goal4954-C:

> Was the grouped carrier only a RayJoin app trick, or is it a generic RTDL
> spatial/dataflow representation candidate?

It also records the remaining reprojection/sort plan without pretending that
those phases have already been optimized.

## Part 1: Non-RayJoin Grouped Carrier Proof

Proof script:

```text
history/internal_docs/goal4954d_non_rayjoin_grouped_carrier_proof.py
```

Output artifact:

```text
history/internal_docs/goal4954d_non_rayjoin_grouped_carrier_proof.json
```

The same proof was also run on the POD:

```text
/root/rtdl_goal4954/_goal4954c/non_rayjoin_grouped_carrier_proof.json
```

POD result:

```text
pass True
rayjoin_imported False
groups 5
points 14
```

## Proof Content

The proof constructs a synthetic non-RayJoin spatial overlap result:

- no CDB input;
- no RayJoin import;
- no AuthorOfficial dependency;
- no paper text writer;
- no output-chain format;
- no RTDL core/runtime change.

It uses the same generic grouped carrier shape:

Group-level columns:

- `group_offset`
- `group_length`
- `label_a`
- `label_b`
- `alt_label`
- `source_side_id`
- `source_element_id`

Point-level columns:

- `x`
- `y`

Then it runs a generic downstream consumer:

```text
descriptor_pair_count_grouped
```

Expected and actual result:

```text
(10, 100): group_count=2, point_row_count=5
(10, 200): group_count=1, point_row_count=3
(20, 200): group_count=1, point_row_count=2
(20, 300): group_count=1, point_row_count=4
```

The proof passed.

## Interpretation

This proves that the grouped carrier idea is not inherently RayJoin-specific.

It does **not** by itself promote code into RTDL core. Promotion would still
require:

- normal source placement;
- public naming/API review;
- tests in the regular suite;
- non-RayJoin user documentation if exposed;
- no paper/CDB/AuthorOfficial semantics.

But the key architectural blocker is cleared:

> The grouped carrier can be described and used as a generic spatial/dataflow
> representation.

## Part 2: Reprojection/Sort Plan

Goal4954-C left these median writer-free costs:

| Phase | Median seconds |
|---|---:|
| LSI rows | 1.155147 |
| reprojection | 0.736632 |
| sort total | 0.842339 |
| grouped carrier construction | 0.961306 |
| grouped descriptor consumer | 0.060369 |

The next measured bottleneck after grouped carrier is:

```text
reprojection + sort = 1.578971s median
```

## Why Reprojection/Sort Was Not Edited In Goal4954-D

Reprojection currently uses exact rational arithmetic to preserve paper-output
correctness when reconstructing the AuthorOfficial-compatible sink.

Naively replacing it with float/Numba arithmetic would be a likely correctness
regression. It could make the binary route faster but silently sever the link
back to the paper correctness anchor.

Therefore, the next reprojection/sort work must start with a contract decision:

### Option A: Exact Binary Route

Keep exact rational reprojection because the binary route must be able to
reconstruct paper output byte-for-byte.

Likely outcome:

- limited speedup;
- Python exact arithmetic remains expensive;
- sort can perhaps be improved, but reprojection remains hard.

### Option B: Numeric Binary Route With Paper Sink As Separate Check

Allow the binary intermediate operator to store numeric/float coordinates for
downstream database-style consumers, while the paper sink keeps exact rational
reprojection for byte-equality.

Likely outcome:

- much better performance potential for binary operator workloads;
- preserves paper correctness through separate sink;
- requires explicit documentation that binary operator performance uses numeric
  coordinates, while paper reproduction uses exact formatting path.

This option matches the product insight behind Goal4954:

> Paper text output is a correctness anchor. Binary operator performance is a
> different line.

## Recommended Next Step

Goal4954-E should make a decision:

1. If binary operator performance is the product target, use Option B and build
   a numeric columnar reprojection/sort prototype.
2. If paper-output reconstructability is mandatory for every binary row, use
   Option A and accept a lower pre-fusion ceiling.

The recommended choice is Option B, because it keeps the paper correctness
anchor while allowing the RTDL binary operator to behave like a real database
operator: binary in, binary out, no paper formatting in the hot path.

## Boundary

No Layer 4 fusion is authorized here.

No RTDL core/runtime code was edited.

No public performance claim is authorized beyond:

> On the public County x Soil sample, app-owned grouped carrier prototype
> reduced writer-free hot path from 5.309s to 3.835s, while remaining far slower
> than AuthorOfficial overlay compute.

## Exit

Recommended exit:

`non_rayjoin_grouped_carrier_proven__reprojection_sort_plan_ready`
