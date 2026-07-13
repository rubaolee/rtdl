# Goal5486: LibRTS Exact Point-Contains Prepared-Phase Matrix

Date: 2026-07-11

Status: `implemented__POD_6_of_6_matched__review_pending`

## Objective

Extend the Goal5485 prepared-index phase gate from the exact `dtl_cnty`
workload to all six official Figure-6 point-contains geometry/query pairs
available in the verified archive subset. The objective is to measure the
same generic RTDL prepared-index lifecycle for every case while preserving the
count-only author contract and the existing claim boundary.

This goal does not claim Figure 6 reproduction, pair-row equality, a
performance ratio, or full-paper reproduction.

## Input Provenance

All six cases came from the Zenodo v2 `PPoPPAE-v2.tar.gz` archive. The archive
was verified before extraction with:

```text
size = 23062425365 bytes
MD5  = 89e589f086038f1cd3af9e3ed67da8c8
```

Each geometry/query member was selected from the verified extraction manifest
and independently checked by size and SHA-256. The per-case hashes are stored
in each result object and in the batch summary. The same selected files were
passed to the pinned author `query` binary and to RTDL.

The batch used the replacement POD `157.157.221.29:25039` with an NVIDIA RTX
4000 Ada, CUDA 12.8, and the pinned OptiX author/RTDL environment. Embree was
excluded from this campaign.

## Implementation

The app-owned runner is:

```text
Paper-reproduction-apps/librts-paper/run_exact_point_contains_prepared_phase_batch.py
```

For each case, the runner:

1. validates the archive and selected-member extraction evidence;
2. runs the pinned author binary and records its internal Query Time and
   Loading Time separately;
3. loads the WKT inputs into RTDL MBR/query columns;
4. prepares a generic OptiX AABB index;
5. calls the prepared public API:

```python
prepared = rt.prepare_aabb_index_2d(boxes, backend="optix")
payload = prepared.count(point_queries=points, operation="point_contains")
prepared.close()
```

6. records WKT load, index preparation, prepared query wall, and native
   primitive query as separate fields.

No LibRTS-specific primitive or author-specific backend behavior was added to
RTDL. The case list, archive selection, author wrapper, count comparator, and
claim boundary remain app-owned.

## POD Result

All six cases matched the author's integer result count:

| Case | Geometry rows | Query rows | Author result | Author query ms | RTDL WKT load s | RTDL prepare s | RTDL prepared query s | RTDL primitive s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `dtl_cnty` | 12,234 | 100,000 | 136,475 | 0.0846 | 28.411 | 0.632 | 0.376076 | 0.212734 |
| `USACensusBlockGroupBoundaries` | 248,954 | 100,000 | 148,970 | 0.0908 | 97.505 | 1.871 | 0.189807 | 0.049086 |
| `USADetailedWaterBodies` | 463,595 | 100,000 | 118,622 | 0.0886 | 34.581 | 3.430 | 0.299463 | 0.047774 |
| `parks_Europe` | 1,856,318 | 100,000 | 109,279 | 0.0842 | 139.904 | 15.441 | 0.226963 | 0.054184 |
| `lakes.bz2` | 8,327,448 | 100,000 | 103,189 | 0.0838 | 404.471 | 66.311 | 0.178843 | 0.046396 |
| `parks.bz2` | 11,544,398 | 100,000 | 112,729 | 0.0914 | 553.019 | 85.547 | 0.408325 | 0.049226 |

The machine-readable batch result is:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5486_prepared_phase_batch.json
```

The batch status is:

```text
case_count = 6
matched_case_count = 6
matched = true
```

The per-case result files preserve the exact input SHA-256 values and the
full author/RTDL phase fields.

## Interpretation

This is a stronger phase matrix than the single-case Goal5485 probe because it
shows that the generic prepared-index route preserves exact count agreement
across all six official archive member pairs, including the two largest cases.
It also exposes the scale of the current app-side front door: RTDL WKT/MBR
loading dominates the measured preparation path for the large `lakes.bz2` and
`parks.bz2` inputs, while the prepared query phase stays below 0.41 seconds in
these single runs.

The author Query Time is an internal author metric after author loading. RTDL
prepared query is wall time around a different public API call. The values are
therefore phase evidence only. They are not a fair author-vs-RTDL ratio.

Equal counts do not establish equal point-to-polygon relations. The standard
author binary does not expose pair rows for this operation. Separate
relation-level evidence exists for the different Goal5467 representative PIP
workload and must not be conflated with these six cases.

## Claim Boundary

Authorized:

- exact official archive member identity for the six selected inputs;
- same-input author/RTDL integer count agreement, 6 of 6;
- a generic prepared-index phase matrix with separate load, prepare, query,
  and primitive fields;
- the observation that the current RTDL front door is dominated by WKT/MBR
  loading on the largest inputs.

Not authorized:

- Figure 6 reproduction;
- pointwise containment or pair-row equivalence for these six cases;
- author-vs-RTDL performance ratio or speedup;
- author RT-core algorithm equivalence;
- complete LibRTS paper reproduction;
- Embree comparison.

## Verification

Local focused tests:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5485_librts_exact_point_contains_prepared_phase_gate_test tests.goal5486_librts_prepared_phase_batch_test
Ran 4 tests OK
```

The Goal5486 batch runner also produced one per-case JSON artifact and a
6-of-6 summary on the live POD. External review remains pending by design;
this result is not self-promoted to reviewed status.
