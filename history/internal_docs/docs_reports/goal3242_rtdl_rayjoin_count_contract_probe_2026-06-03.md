# Goal3242: RTDL/RayJoin Count-Contract Probe

Date: 2026-06-03

## Purpose

Goal3232 proved RTDL row-continuation correctness on bounded public RayJoin
CDB slices. Goal3239 proved upstream RayJoin `query_exec` can run LSI/PIP
smokes on the same slices. Goal3242 switches to the fairer count-contract
question:

When RayJoin reports query/count-style timings, which RTDL route should be used
for comparison, and where is the remaining optimization gap?

## Artifact

- `docs/reports/goal3242_rtdl_rayjoin_count_contract_probe_2026-06-03.json`

RTDL commit: `b42d6ea4e5f55166db48d26b0721f312d5eacb59`

## RTDL Count Routes

| Case | RTDL Route | Contract | Count | Query/Device Phase |
| --- | --- | --- | ---: | ---: |
| `lsi_county256_soil256_count512` | `prepared_optix` | segment/segment intersection count | 269 | 1.537 ms |
| `lsi_county256_soil256_count512` | `prepared_optix_compact_grouped_count` | grouped intersection count by left id | 269 | 63.720 ms candidate columns + 295.331 ms compact count |
| `lsi_county256_soil256_count512` | `prepared_optix_left_id_dense_count_reuse` | dense left-id count column | 269 | 58.668 ms |
| `pip_county512` | `prepared_optix` | point/shape positive-hit count | 1430 | 1.268 ms |

The `prepared_optix` count route is the closest current RTDL contract for the
RayJoin `query_exec` logs on these bounded public slices. The compact grouped
routes expose useful device-column contracts, but this smoke does not show them
as the right same-slice timing comparison at this scale.

## RayJoin Query-Exec Context

From Goal3239 on the same pod and slices:

| Case | RayJoin Mode | RayJoin Result | Query Time |
| --- | --- | ---: | ---: |
| `lsi_county256_soil256_count512` | `rt` | 269 intersections | 0.229 ms |
| `lsi_county256_soil256_count512` | `grid` | 268 intersections | 0.695 ms |
| `pip_county512` | `rt` | count not printed | 0.186 ms |
| `pip_county512` | `grid` | count not printed | 2.451 ms |

## Interpretation

For LSI, the count contract is clear: RTDL prepared OptiX count and RayJoin RT
both report 269 on the same public slice. RayJoin RT is still about `6.70x`
faster on the reported query phase (`0.229 ms` vs `1.537 ms`). That is an
optimization target, not a release claim.

For PIP, RTDL reports 1430 positive assignments. RayJoin RT runs and its checker
passes, but the normal RayJoin log does not print the positive assignment count,
so PIP is not yet a count-parity comparison. RayJoin RT is about `6.83x` faster
on the query phase (`0.186 ms` vs `1.268 ms`) in this smoke.

The practical next work is therefore:

- extract or add a RayJoin PIP count log without changing algorithm behavior;
- build a repeated runner for RayJoin `query_exec` and RTDL `prepared_optix`
  count on the same slices;
- investigate the RTDL prepared-count query gap before moving back to row
  materialization or overlay;
- keep compact grouped-count routes for larger-scale/reuse experiments, not as
  the default small-slice comparison.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.
