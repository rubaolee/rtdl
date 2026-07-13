# Goal4878: Section 5.3 PIP Reproduction Under AuthorOfficial

Date: 2026-07-02

Status: `completed_pending_external_review`

## Purpose

Goal4878 reruns RayJoin paper Section 5.3 PIP/point-location under the official
updated comparator:

```text
AuthorOfficial = Author+RTDLContractPatch
```

Unlike Goal4877, this section is directly affected by the updated
point-location contract, so old AuthorPatch evidence could not simply be
reclassified. The fair comparator is the AuthorOfficial `query_exec` PIP route.

## Correct Comparator

Section 5.3 is a `query_exec -query=pip` workload. During this goal I caught and
corrected one harness mistake:

- `polyover_exec` can run a PIP-shaped workload smoke, but it is not the Section
  5.3 comparator used for per-point closest-edge diagnostics.
- `query_exec` is the correct author binary for this section.

The AuthorOfficial diagnostic line used here is:

```text
AUTHORPATCH_PIP_DIAG query_points=<N> positive_count=<closest_eids != DONTKNOW> closest_eids_fnv64=<hash>
```

It is emitted after the query timer and does not change the algorithm.

## RTDL Route

The RTDL route uses:

```python
prepare_planar_map_point_location_2d_optix(...)
```

and compares the raw point-location result:

```text
segment_id != DONTKNOW
FNV64(segment_id - 1)
```

The `-1` normalization is required because this RTDL route reports 1-based
segment ids while the author `closest_eids` are 0-based.

No `rtdsl.rayjoin_overlay` evidence is used. The reproduction runner still uses
a user-side streaming CDB packer that reaches into RTDL's packed segment layout
to avoid huge Python object graphs; that remains product/API debt, not a
correctness failure.

## Artifacts

Primary summary:

```text
history/internal_docs/goal4878_section53_pip_authorofficial_summary.json
```

Raw artifact directory:

```text
history/internal_docs/goal4878_section53_authorofficial/
```

Key files:

- `county_zipcode_authorofficial_query_exec.stderr`
- `county_zipcode_authorofficial_raw.json`
- `block_water_authorofficial_query_exec.stderr`
- `block_water_authorofficial_raw.json`
- `australia_lakes_parks_authorofficial_query_exec.stderr`
- `australia_lakes_parks_authorofficial_raw.json`

The file `australia_lakes_parks_authorofficial_pip.json` is retained only as a
workload smoke from the earlier `polyover_exec` mistake. It is not correctness
evidence for this goal.

## Results

| Pair | Query points | AuthorOfficial positives | RTDL found segments | Count match | Author hash | RTDL normalized hash | Hash match | Classification |
|---|---:|---:|---:|---|---:|---:|---|---|
| County x Zipcode | 47,862,092 | 47,327,744 | 47,327,744 | yes | 17,585,803,063,680,255,704 | 17,585,803,063,680,255,704 | yes | exact per-point closest-edge match |
| Block x Water | 44,863,618 | 44,841,020 | 44,841,020 | yes | 13,878,963,590,670,293,968 | 13,878,963,590,670,293,968 | yes | exact per-point closest-edge match |
| Australia Lakes x Parks representative | 992,505 | 958,981 | 958,981 | yes | 13,434,159,047,986,799,888 | 8,149,910,373,246,904,473 | no | count-consistent only |

## Timing Context

These are diagnostic runs, not performance claims. The RTDL raw route downloads
and hashes every returned segment id, so it is much heavier than count-only
PIP.

Observed RTDL diagnostic phase times:

| Pair | Scan sec | Pack base sec | Raw query/download sec |
|---|---:|---:|---:|
| County x Zipcode | 176.932 | 52.711 | 246.562 |
| Block x Water | 273.578 | 176.245 | 239.430 |
| Australia Lakes x Parks representative | 22.833 | 41.436 | 10.089 |

These numbers describe diagnostic cost, not optimized user-facing performance.

## Interpretation

Section 5.3 under AuthorOfficial is closed for the two serious recovered US
workloads:

- County x Zipcode: exact per-point closest-edge match.
- Block x Water: exact per-point closest-edge match.

The Australia representative row remains count-consistent only:

- found/not-found count matches exactly;
- exact closest-edge id hash differs.

This is acceptable as bounded representative evidence, but it must not be
reported as exact per-point AuthorOfficial equivalence.

## What This Does Not Prove

This does not prove:

- all eight exact hidden paper pairs;
- Section 5.7 polygon overlay;
- broad RayJoin reproduction;
- a performance win;
- an Embree result;
- a Numba-critical-path result.

Numba is not on the correctness-critical path for this Section 5.3 route.

## Decision Audit

1. **Was there a stupid failure mode here?**
   Yes: using `polyover_exec` output as if it were the Section 5.3 `query_exec`
   comparator would have been wrong.

2. **What action would make that decision stupid?**
   Treating any PIP-shaped author run as the same comparator, instead of
   checking the actual paper-section executable and diagnostic metric.

3. **Is there another path that avoids being stuck?**
   Yes: use `query_exec`, compare `closest_eids` against RTDL raw `segment_id`,
   and only classify rows exact when the full hash matches.

4. **Can we start a better path now?**
   Yes. Close Section 5.3 with the exact/count-only split above, then proceed to
   representative Section 5.7 expansion using the same strict comparator
   discipline.

## Exit Label

`completed_section53_authorofficial_two_serious_exact_one_representative_count_only`
