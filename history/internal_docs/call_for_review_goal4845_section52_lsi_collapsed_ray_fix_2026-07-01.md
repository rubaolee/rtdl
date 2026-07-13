# Call For Review - Goal4845 Section 5.2 LSI Collapsed-Ray Candidate Fix

Date: 2026-07-01

Requested verdict labels:

- `approve_goal4845_county_zipcode_lsi_correctness_gate_passed`
- `approve_with_required_amendments`
- `block_goal4845_fix_as_insufficient_or_overfit`

## Context

The project is currently on the v2.14 public line. V3/V4 work has been isolated and is not part of the public surface.

Goal4845 targets RayJoin paper Section 5.2 LSI reproduction against AuthorPatch, not V4 and not Embree.

AuthorPatch means the author source plus accepted compatibility/intended-behavior patches.

## What was tested

Dataset pair:

- County CDB: `dtl_cnty_Point.cdb`
- Zipcode CDB: `USAZIPCodeArea_Point.cdb`

AuthorPatch command:

```text
query_exec \
  -poly1 dtl_cnty_Point.cdb \
  -poly2 USAZIPCodeArea_Point.cdb \
  -serialize=/dev/shm \
  -grid_size=15000 \
  -mode=rt \
  -query=lsi \
  -v=1 \
  -fau \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false
```

AuthorPatch result:

```text
Intersections: 961165
```

RTDL comparable direction before fix:

```text
count: 961164
```

## Diagnosis

Pair dump showed one missing pair and no extra pairs:

```text
missing_count: 1
extra_count: 0
missing pair:
  county edge zero-based id: 8480674
  zipcode edge zero-based id: 5748176
```

The CDB records were:

```text
county file edge id 8480675
8480675 2 16961349 16961350 3008 3010
-7.8550846000e+01 3.9124448000e+01
-7.8552278000e+01 3.9125105000e+01

zipcode file edge id 5748177
5748177 2 11496353 11496354 8079 8091
-7.8551014500e+01 3.9124525200e+01
-7.8551021500e+01 3.9124528600e+01
```

A source-level reproduction of the author's scaled integer `intersect_test` showed that this pair is a true hit.

The defect: under the full dataset scale, the zipcode edge's two endpoints collapse to the same `float32` candidate ray point. RTDL's raygen logic used already-float endpoint ordering/direction, so the OptiX candidate stage never invoked the exact predicate. AuthorPatch computes ordering/direction from higher precision before the final float launch values.

## Fix

File changed:

- `src/native/optix/rtdl_optix_workloads.cpp`

Change:

- In both RayJoin LSI predicate-mode segment-pair raygen paths, use `RayjoinLsiScaledSegment` exact/scaled endpoints to decide the author-style direction.
- If the float endpoints collapse but the exact/scaled segment is nonzero, extend the candidate ray by one `nextafterf` step in the exact direction.
- Keep `rayjoin_lsi_intersection_device` as the final hit predicate.

Claim:

- This is not a hard-coded RayJoin pair patch.
- It is a conservative candidate-generation repair for nonzero exact segments that collapse in float candidate space.
- Exact geometry still decides whether a candidate is counted.

## Evidence

Synthetic regression before fix:

```text
direct count  = 0
grouped count = 0
expected      = 1
```

Synthetic regression after fix:

```text
direct count  = 1
grouped count = 1
expected      = 1
```

POD test command:

```text
RTDL_OPTIX_LIB=/workspace/rtdl_goal4817_user_smoke_20260630_102224/build/librtdl_optix.so \
PYTHONPATH=src \
python3 -m unittest tests.goal4845_rayjoin_lsi_collapsed_ray_candidate_test -v
```

POD result:

```text
Ran 1 test in 10.954s
OK
```

Full County x Zipcode RTDL count after fix:

```json
{
  "count": 961165,
  "expected_authorpatch_original_count": 961165,
  "delta_vs_authorpatch_original": 0,
  "prepare_sec": 4.9012961611151695,
  "count_wall_sec": 3.4825050979852676,
  "load_sec": 166.4394359961152
}
```

## Non-claims

This review must not authorize:

- broad RayJoin paper reproduction,
- Section 5.7 overlay correctness,
- performance wins,
- Embree claims,
- V3/V4 claims,
- public release wording.

This is only a Section 5.2 County x Zipcode LSI correctness gate plus a focused core candidate-generation repair.

## Questions for reviewer

1. Is the diagnosis sufficiently supported by AuthorPatch/RTDL pair diff evidence?
2. Is the collapsed-float-ray repair a valid generic conservative-candidate repair rather than a RayJoin-specific shortcut?
3. Is the synthetic regression sufficient to guard the exposed defect?
4. Does the full County x Zipcode `961165 == 961165` count gate justify closing this slice as correctness-passed?
5. Are any further regression gates required before continuing to the next Section 5.2 dataset pair?
