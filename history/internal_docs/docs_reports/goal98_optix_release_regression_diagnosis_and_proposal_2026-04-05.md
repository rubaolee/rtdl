# Goal 98 Report: OptiX Release Regression Diagnosis and Proposal

Date: 2026-04-05
Status: diagnosis complete, repair validated locally on clean Linux clone

## Trigger

Goal 94 release validation on a clean Linux clone at release head `c43f538`
found a blocking OptiX regression on the accepted long exact-source prepared
`county_zipcode` positive-hit `pip` surface.

Failing clean-clone artifact:

- `/home/lestat/work/rtdl_goal94_clean/build/goal94/optix_prepared/summary.json`

Failing values:

- PostGIS row count:
  - `39073`
- OptiX row count:
  - `38799`
- parity:
  - `false`
- OptiX backend seconds:
  - `7.817694120996748`
  - `5.145167353999568`

The failure had this shape:

- missing rows only
- no extra rows
- stable wrong digest across reruns

## Prior accepted comparison point

The previously accepted OptiX package-level claim was that on the long
exact-source `county_zipcode` positive-hit `pip` surface:

- parity was preserved
- prepared warmed reruns could beat PostGIS
- repeated raw-input reruns could beat PostGIS

So the clean-clone failure was a direct contradiction and had to block release.

## Diagnosis

The root problem was in the native OptiX positive-hit `pip` path in:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`

Specifically:

1. The OptiX positive-hit path was not using a fully conservative candidate
   generation rule.
2. In positive-hit mode, the GPU intersection program still relied on the
   float32 `point_in_polygon(...)` decision before reporting a candidate.
3. Host exact finalize only runs on rows that survive the GPU candidate stage.
4. That means any float32 false negative in the GPU point-in-polygon stage is
   unrecoverable.

This was confirmed by the diff shape:

- `missing = 274`
- `extra = 0`

That is exactly the signature of under-generation before exact finalize.

The earlier implementation also used a very tight polygon AABB pad and boundary
epsilon, which further increased the risk of float32 false negatives on the
exact-source surface.

## Repair direction

The correct fix is to make positive-hit OptiX candidate generation explicitly
conservative again.

Implemented repair:

1. widen polygon broad-phase tolerance
- increased polygon AABB padding
- widened the float32 boundary epsilon used by the GPU helper for the
  non-positive-only path only

2. more importantly, make positive-hit candidate generation stop deciding final
   truth on the GPU
- in `positive_only` mode, the OptiX intersection program now reports every
  AABB candidate
- host exact finalize remains the final inclusive truth decision

The decisive fix is item 2. Item 1 is only defense-in-depth for the
non-positive-only float32 path and is not sufficient by itself to repair the
release regression.

This matches the intended RTDL architecture better:

- GPU/OptiX:
  - candidate generation
- host:
  - exact inclusive finalize

That is also consistent with the repaired Embree direction.

## Why this proposal is correct

The positive-hit path already has host exact finalize, so false positives are
acceptable and will be filtered.

False negatives are the real danger because they silently drop correct rows.

Therefore the candidate generator must err on the side of:

- more candidates
- fewer missed true hits

not the other way around.

## Repair evidence

After the conservative-candidate repair, the clean-clone Linux reruns changed
to:

Prepared exact-source OptiX:

- artifact:
  - `/home/lestat/work/rtdl_goal94_clean/build/goal94/optix_prepared_fix2/summary.json`
- parity:
  - restored
- runs:
  - OptiX `4.686839201996918 s`
  - PostGIS `3.3708876949967816 s`
  - parity `true`
  - OptiX `2.3074421010096557 s`
  - PostGIS `3.2650011710065883 s`
  - parity `true`

Repeated raw-input exact-source OptiX:

- artifact:
  - `/home/lestat/work/rtdl_goal94_clean/build/goal94/optix_raw_fix2/summary.json`
- parity:
  - restored on all reruns
- runs:
  - first run `4.49759002099745 s`
  - repeated `2.349021426998661 s`
  - repeated `2.124993502991856 s`
  - all parity `true`

## Current conclusion

The release regression was real.

The root cause was a non-conservative OptiX positive-hit candidate generator.

The repair direction is technically sound because it restores the intended
separation:

- OptiX broad phase
- host exact finalize

The clean-clone rerun evidence now shows restored parity on both prepared and
repeated raw-input exact-source surfaces.

## Remaining work for Goal 98

- 3-way review of this diagnosis/proposal
- final code-package review
- final rerun-package review
- Goal 94 release validation report update after the OptiX repair is fully
  packaged
