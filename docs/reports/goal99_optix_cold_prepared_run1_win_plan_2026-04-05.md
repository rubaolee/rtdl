# Goal 99 Plan: OptiX Cold Prepared Run-1 Win

Date: 2026-04-05
Status: planned

## Starting point

Goal 98 restored parity on the clean-clone OptiX prepared exact-source surface,
but the first prepared rerun remains slower than PostGIS.

Current repaired values:

- OptiX run 1:
  - `4.686839201996918 s`
- PostGIS run 1:
  - `3.3708876949967816 s`
- parity:
  - `true`

## Plan

1. profile the prepared OptiX run-1 path on the clean Linux clone
2. identify what is still inside the timed `bound.run()` that behaves like a
   cold-start cost
3. reduce that cost without changing parity
4. rerun the exact same prepared surface on the clean clone
5. require review before any claim update

## Non-goals

- no raw-input goal change
- no Embree/Vulkan work
- no release-doc update until the result exists
