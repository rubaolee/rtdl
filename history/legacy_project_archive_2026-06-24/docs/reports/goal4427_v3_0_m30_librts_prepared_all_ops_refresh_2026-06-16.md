# Goal4427 V3.0 M30 LibRTS Prepared All-Ops Refresh

Date: 2026-06-16

Evidence:

`docs/reports/goal4427_v3_0_m30_librts_prepared_all_ops_refresh_1m_1k_2026-06-16.json`

Status: complete. M30 refreshes the libRTS-style spatial-index row as a V3 primitive-first benchmark: generic prepared AABB index all-ops, same generated fixture, OptiX RT-core backend versus Embree CPU backend, no partner continuation.

## Contract

Both backends run:

`AABB_INDEX_QUERY_2D / generic_prepared_aabb_index_query_2d`

The measured operation is `all`, covering:

- `point_contains`
- `range_contains`
- `range_intersects`

The result is count-only. The native engine sees generic boxes and generic query streams, not LibRTS-specific symbols or app-specific callbacks.

## Dataset And Timing Basis

The run uses a generated uniform paper-like fixture:

- 1,000,000 indexed boxes
- 1,000 point queries
- 1,000 box queries
- seed 2025
- box/query widths of `0.005`
- warmup 1
- repeat 240 for Embree and 3200 for OptiX

The repeat counts differ on purpose. The comparison ratio uses the per-iteration prepared-query median. The totals are duration windows used to keep the measurement out of tiny millisecond-only territory.

CPU reference is skipped for this large row because the O(n*m) oracle would be a 1B-pair host check. Correctness is instead gated by exact cross-backend count agreement on the same generated fixture and the same primitive contract.

## Results

| Backend | Scene prepare sec | Query median sec | Query total sec | Repeat | Counts | CPU ref | Partner |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| Embree CPU | 6.869465 | 0.017218 | 10.297738 | 240 | 6,251 / 693 / 25,079 | skipped | none |
| OptiX RT cores | 2.797154 | 0.001534 | 5.099807 | 3,200 | 6,251 / 693 / 25,079 | skipped | none |

Counts are listed as `point_contains / range_contains / range_intersects`.

## Same-Contract Ratio

| Metric | Embree sec | OptiX sec | Embree / OptiX | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Prepared all-ops query median | 0.017218 | 0.001534 | 11.23x | RT cores are substantially faster for this generic prepared AABB all-ops count query. |
| Scene prepare | 6.869465 | 2.797154 | 2.46x | OptiX also prepares this large generated scene faster in this run. |
| Query duration window | 10.297738 | 5.099807 | not a speedup metric | Repeats differ, so use these only as measurement-window sanity checks. |

## Interpretation

This is one of the clearer primitive-first V3 rows. The app does not need a partner because the useful benchmark contract is already a native generic primitive: prepared AABB index count queries over point and box streams. Unlike contact manifold, there is no large app-owned refinement phase after traversal in this evidence row, so the RT-core advantage shows directly in the prepared-query median.

The result is still not a full LibRTS reproduction. The fixture is generated paper-like data, not the original paper dataset, and authors-code timing is not part of M30. It is valid evidence for RTDL's app-agnostic `AABB_INDEX_QUERY_2D` all-ops primitive.

This does not authorize a full LibRTS paper reproduction claim.

## Validation

The evidence records:

- `comparison.all_counts_match_cross_backend=true`
- `comparison.all_same_contract=true`
- `comparison.all_primitive_first_no_partner=true`
- `comparison.public_speedup_claim_authorized=false`
- `native_engine_customization=false` on both rows
- `partner_continuation_required=false` on both rows

## Closeout

M30 closes the V3 libRTS prepared all-ops refresh. Internal wording may say that, on the same generated 1M x 1K fixture and the same generic prepared AABB all-ops contract, OptiX/RT cores are 11.23x faster than Embree on the prepared-query median with matching counts. Public wording still needs the broader V3 claim gate before release, and this row must not be described as full LibRTS paper reproduction or authors-code comparison.
