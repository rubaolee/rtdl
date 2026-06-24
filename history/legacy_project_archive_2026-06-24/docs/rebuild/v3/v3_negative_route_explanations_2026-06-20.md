# V3 Negative Route Explanations

Status: required V3 rebuild explanation, 2026-06-20.

This note explains two rows that must never be shown as unexplained V3
performance claims:

```text
spatial_rayjoin     rayjoin_all_backend_query_summary   0.034x
librts_spatial_index aabb_index_all_count_only          0.065x
```

Both rows are useful evidence, but they are not public speedup evidence. They
are route-health and boundary evidence. If they appear in user-facing material,
the explanation below must appear with them.

## Short Answer

Yes, the slow rows use small or non-paper-equivalent fixtures.

The slow ratios do not contradict the stronger RayJoin or LibRTS-related
research direction because these rows are not paper reproductions and not the
same hot-path contract as the positive rows.

The immediate release rule is:

```text
Do not market these rows as OptiX speedups. Do not compare them to paper
numbers. Use them to explain when RTDL users should choose another route.
```

## Spatial RayJoin Standard All-Backend Row

Measured row:

```text
artifact: docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523
group:    rayjoin_all_backend_query_summary
Embree:   0.0353522002696991 sec, source workloads.total_elapsed_sec
OptiX:    1.035226359963417 sec, source prepared_query_total_sec
ratio:    0.03414924661592695x OptiX versus Embree
```

This row is not a RayJoin paper-scale performance row.

The fixture is tiny:

| Workload | Dataset | Result size |
| --- | --- | ---: |
| LSI | `tests/fixtures/rayjoin/br_county_subset.cdb` | `row_count=1` |
| Overlay seed | `tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb` | `row_count=0` |
| PIP | `tests/fixtures/rayjoin/br_county_subset.cdb` | `row_count=6` |

The timing protocol is also not claim-grade:

- `warmup=0`;
- `repeat=1`;
- the OptiX metric is a sum of prepared-query timings across three tiny
  workloads;
- the slow component is the LSI count route: `1.0348567962646484` seconds for a
  one-result fixture;
- the row exists because the repaired route must complete and match the CPU
  reference, not because it is a public speedup route.

Why can OptiX be so slow here?

For a tiny one-result or six-result fixture, CPU Embree can finish before GPU
launch, synchronization, query packing, and first-use path costs are amortized.
The OptiX path is doing a generic prepared route, not a special paper-native
RayJoin implementation. On this row the overhead dominates the real work.

The positive RayJoin evidence is a different contract:

| Row | Dataset | Timing scope |
| --- | --- | --- |
| `rayjoin_lsi_authored_tiled_x512` | `derived/authored_lsi_crossing_tiled_x512` | prepared query hot path, `warmup=1`, `repeat=5` |
| `rayjoin_overlay_seed_authored_tiled_x512` | `derived/authored_overlay_squares_tiled_x512` | prepared query hot path, `warmup=1`, `repeat=5` |
| `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | public CDB representative route | per-contract hot medians, not wrapper elapsed time |

Even those positive rows are not full RayJoin paper reproduction claims. They
are row-scoped RTDL route evidence.

## LibRTS Spatial Index Standard Row

Measured row:

```text
artifact: docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523
group:    aabb_index_all_count_only
Embree:   0.011050976812839508 sec, source run_phases.query_median_sec
OptiX:    0.16898325085639954 sec, source run_phases.query_median_sec
ratio:    0.06539687665395033x OptiX versus Embree
```

This row is not a LibRTS paper reproduction.

The row payload says:

```text
paper_reproduction: false
paper_equivalent_dataset: false
authors_code_comparison: false
native_engine_customization: false
```

The fixture is synthetic and small:

| Field | Value |
| --- | ---: |
| `dataset` | `uniform` |
| `box_count` | 1024 |
| `point_query_count` | 512 |
| `box_query_count` | 512 |
| `repeat` | 1 |
| `warmup` | 0 |

Why can OptiX be so slow here?

The row compares a generic RTDL OptiX AABB-index count-only route against an
Embree native AABB collision index on a small synthetic fixture. It is not the
LibRTS authors' implementation, not a paper-equivalent dataset, and not a
specialized app-native RTSpatial symbol. The OptiX path also executes a packed
multi-operation query contract, so GPU launch and route orchestration can easily
dominate at this size.

There is now a larger calibrated same-contract row:

```text
row:      aabb_index_all_count_only_large_32768
boxes:    32768
queries:  32768
Embree:   36.09376148879528 sec
OptiX:    0.04432278126478195 sec
ratio:    814.3388221324167x OptiX versus Embree
```

That row replaces the small negative fixture for current performance
interpretation. It is still not a LibRTS paper reproduction, not authors-code
timing, and not a full mutable spatial-index result. It is only a row-scoped
generic RTDL AABB-index candidate.

## Release Rule

For V3 public docs:

- show the two slow ratios only in a "negative or mixed rows" section;
- never place them in a headline speedup table without explanation;
- never compare them to RayJoin or LibRTS paper results;
- teach the user route decision:
  - for tiny RayJoin fixture runs, do not expect OptiX to beat Embree;
  - for the small LibRTS-style standard fixture, choose Embree;
  - for the calibrated 32768/32768 generic AABB row, the OptiX row is the
    current positive candidate, still without LibRTS paper/authors-code wording;
  - use the strengthened or representative RayJoin rows only with their exact
    row-scoped contracts and artifact paths.

## Goal-Level Decision Audit

Decision: keep the negative rows, but require a full explanation and block
public speedup wording from using them.

1. Did I make a foolish decision?

   Earlier, yes. Listing `0.034x` and `0.065x` without explaining fixture size,
   timing scope, and paper-reproduction status was not responsible.

2. What actions made it foolish?

   I treated "non-claim" as enough, instead of explaining why the result was
   slow and why it did not match the paper-style positive expectations.

3. Was there another path?

   Yes. The artifact already contained the exact evidence: tiny RayJoin
   fixtures, `paper_equivalent_dataset: false` for LibRTS, and non-claim flags.

4. Can I now try a different path that truly solves the problem?

   Yes. The negative rows now become required teaching material and release
   gates, not unexplained table entries.
