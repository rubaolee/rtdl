# Goal3276 RayJoin Scale Runner Input-Parity Repair

Date: 2026-06-03

Status: implemented and pod-measured on NVIDIA A40; scale diagnostic accepted
as internal evidence only.

## Purpose

Goal3276 began as a scale diagnostic for the public RayJoin CDB slices. The
first attempted 128-slice run exposed a runner problem instead of a valid scale
result: `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py` allowed
RTDL datasets to vary, but RayJoin `query_exec` inputs were still hard-coded to
the historical 512-slice files.

Short diagnosis: RayJoin inputs were still hard-coded while RTDL inputs varied.

That made the attempted 128-row comparison invalid:

- RayJoin LSI still used `br_county_start256_count512.cdb` plus
  `br_soil_start256_count512.cdb`;
- RTDL LSI used the requested `start0_count128` pair;
- RayJoin PIP still used `br_county_start0_count512.cdb`;
- RTDL PIP used `br_county_start0_count128.cdb`.

The resulting artifact correctly returned `needs_more_evidence` because the LSI
visible count mismatched. It must not be used as performance evidence.

## What Changed

The runner now accepts optional RayJoin input overrides:

```text
--rayjoin-lsi-poly1
--rayjoin-lsi-poly2
--rayjoin-pip-poly1
--rayjoin-pip-poly2
```

If these are omitted, the historical Goal3244 defaults are preserved. If one
override in a pair is supplied without the other, the runner fails closed.

The runner also records the actual RayJoin `input_poly1` and `input_poly2` paths
in each artifact so scale probes can be audited later.

## Boundary

This is a measurement harness repair only. It does not change RTDL runtime
semantics, native engine behavior, release status, or public speedup claims.

## Corrected Pod Scale Diagnostic

After the runner repair, the 128/256/384/512 public CDB slices were rerun with
both RayJoin and RTDL pointed at matching inputs. Artifacts:

- `docs/reports/goal3276_scale_pod/slice_128.json`
- `docs/reports/goal3276_scale_pod/slice_256.json`
- `docs/reports/goal3276_scale_pod/slice_384.json`
- `docs/reports/goal3276_scale_pod/slice_512.json`

All four artifacts are source-clean at commit
`dd30defef6b3174c2b69c61f6172aa0b94a7cb79`, preserve the visible LSI count
contract, and keep all claim-boundary flags false.

| Slice | Workload | RayJoin query ms | RTDL prepared ms | RTDL / RayJoin | RayJoin visible count | RTDL count |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 128 | LSI | 0.081221 | 0.125272 | 1.542x | 0 | 0 |
| 128 | PIP | 0.143449 | 0.164840 | 1.149x | not exposed | 360 |
| 256 | LSI | 0.208563 | 0.292344 | 1.402x | 73 | 73 |
| 256 | PIP | 0.167873 | 0.362990 | 2.162x | not exposed | 717 |
| 384 | LSI | 0.249227 | 0.529591 | 2.125x | 246 | 246 |
| 384 | PIP | 0.174337 | 0.278017 | 1.595x | not exposed | 1083 |
| 512 | LSI | 0.253651 | 0.797536 | 3.144x | 294 | 294 |
| 512 | PIP | 0.201225 | 0.375450 | 1.866x | not exposed | 1430 |

PIP native count-pass medians:

| Slice | RTDL PIP count | Median native count-pass ms |
| ---: | ---: | ---: |
| 128 | 360 | 0.084820 |
| 256 | 717 | 0.274568 |
| 384 | 1083 | 0.174796 |
| 512 | 1430 | 0.265918 |

## Interpretation

This scale pass is useful because it separates two facts:

1. The repaired runner can now perform true same-input RayJoin/RTDL comparisons
   across slices.
2. The remaining RayJoin gap is not a simple monotonic function of slice size.

For PIP, RTDL is close at 128 (`1.149x`) but still slower at every measured
slice. The 256 and 512 rows are worse than 384, which suggests the gap depends
on geometry distribution, candidate locality, and RayJoin's grouping strategy,
not just count size. For LSI, RTDL preserves visible counts but gets worse as
the start0 slice grows.

This does not authorize public speedup or RayJoin-reproduction claims. The next
engineering target should be a generic grouping/locality primitive, not another
single scalar-count pipeline tweak.
