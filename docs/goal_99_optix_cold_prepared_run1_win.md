# Goal 99: OptiX Cold Prepared Run-1 Win

## Objective

Make the first prepared exact-source OptiX rerun beat PostGIS on the accepted
long `county_zipcode` positive-hit `pip` surface, while preserving the restored
Goal 98 parity.

## Trigger

After Goal 98, the clean-clone prepared OptiX surface is correct again, but the
first prepared rerun is still slower than PostGIS:

- OptiX:
  - `4.686839201996918 s`
- PostGIS:
  - `3.3708876949967816 s`

The warmed prepared rerun already wins, but the first prepared rerun does not.

## Required boundary

Accepted measurement boundary:

- exact-source `county_zipcode`
- positive-hit `pip`
- execution-ready / prepacked timing
- backend:
  - OptiX only

This goal is specifically about the first prepared backend run after the
prepared kernel is built and bound. It is not a raw-input goal and it is not a
full end-to-end packaging goal.

## Hard requirements

- preserve exact parity against indexed PostGIS
- preserve the accepted row count and digest
- do not weaken the Goal 98 conservative-candidate repair
- do not broaden claim language beyond the exact accepted surface

## Main question

Can OptiX beat PostGIS on **run 1** of the prepared exact-source surface, not
only on warmed reruns?

## Expected focus

Likely remaining cold-run costs include:

- first-launch GPU work not hidden by the prepared/bound state
- candidate bitset / output initialization
- candidate readback / exact finalize overhead
- any extra one-time launch or module setup still inside the timed `run()`

## Acceptance

Goal 99 is done when:

- a fresh clean Linux clone rerun shows:
  - prepared exact-source OptiX run 1 faster than PostGIS
  - parity preserved
- the repair package is reviewed before publish
