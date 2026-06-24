# Goal 98 Result Package: OptiX Release Regression Repair

Date: 2026-04-05
Status: ready for review

## Clean-clone failure artifact

Original failing prepared artifact:

- `/home/lestat/work/rtdl_goal94_clean/build/goal94/optix_prepared/summary.json`

Failure summary:

- PostGIS row count:
  - `39073`
- OptiX row count:
  - `38799`
- parity:
  - `false`
- missing rows:
  - `274`
- extra rows:
  - `0`

## Repaired clean-clone artifacts

Prepared exact-source OptiX after fix:

- `/home/lestat/work/rtdl_goal94_clean/build/goal94/optix_prepared_fix2/summary.json`

Repeated raw-input exact-source OptiX after fix:

- `/home/lestat/work/rtdl_goal94_clean/build/goal94/optix_raw_fix2/summary.json`

## Prepared exact-source repaired result

Prepared exact-source OptiX now shows:

- row count:
  - `39073`
- digest:
  - exact match to PostGIS
- parity:
  - `true` on both reruns

Runs:

1. run 1
- OptiX:
  - `4.686839201996918 s`
- PostGIS:
  - `3.3708876949967816 s`
- parity:
  - `true`

2. run 2
- OptiX:
  - `2.3074421010096557 s`
- PostGIS:
  - `3.2650011710065883 s`
- parity:
  - `true`

Interpretation:

- parity is restored
- the accepted prepared claim boundary is restored
- the first prepared rerun is still not an unconditional win
- the warmed prepared rerun beats PostGIS

## Repeated raw-input repaired result

Repeated raw-input OptiX now shows:

- row count:
  - `39073`
- digest:
  - exact match to PostGIS
- parity:
  - `true` on all reruns

Runs:

1. first run
- OptiX:
  - `4.49759002099745 s`
- PostGIS:
  - `3.407562541004154 s`
- parity:
  - `true`

2. repeated run
- OptiX:
  - `2.349021426998661 s`
- PostGIS:
  - `3.1056660960020963 s`
- parity:
  - `true`

3. repeated run
- OptiX:
  - `2.124993502991856 s`
- PostGIS:
  - `2.986209955997765 s`
- parity:
  - `true`

Interpretation:

- the repeated raw-input exact-source claim is restored
- warmed repeated raw-input OptiX again beats PostGIS with parity preserved

## Conclusion

Goal 98 restored the accepted OptiX release story on the exact-source clean
Linux clone:

- prepared exact-source parity restored
- repeated raw-input exact-source parity restored
- warmed OptiX reruns remain competitive / faster on the accepted claim
  boundaries
