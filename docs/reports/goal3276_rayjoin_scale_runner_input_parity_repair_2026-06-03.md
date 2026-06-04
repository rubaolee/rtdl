# Goal3276 RayJoin Scale Runner Input-Parity Repair

Date: 2026-06-03

Status: implemented locally; pod scale rerun pending.

## Purpose

Goal3276 began as a scale diagnostic for the public RayJoin CDB slices. The
first attempted 128-slice run exposed a runner problem instead of a valid scale
result: `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py` allowed
RTDL datasets to vary, but RayJoin `query_exec` inputs were still hard-coded to
the historical 512-slice files.

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

The next step is to rerun the 128/256/384/512 scale diagnostic with both
RayJoin and RTDL pointed at matching slices.

