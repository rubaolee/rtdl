# Goal 236 Report: v0.4 Final Release Gate And v0.5 Direction

Date: 2026-04-11
Status: implemented

## Summary

The final release boundary is now explicit:

- `v0.4.0` is not released immediately
- `v0.4.0` is blocked on three final clean-branch reviews:
  - total code review
  - total doc review
  - detailed process audit

The milestone boundary is also explicit:

- `v0.4` is the release of the nearest-neighbor line as software
- `v0.5` is the milestone for paper/implementation consistency and fuller
  experiment reproduction

## Why This Split Is Correct

The new Goal 235 audit established that RTDL `v0.4` is strong enough for a
serious RTNN-inspired nearest-neighbor story, but not yet a paper-faithful RTNN
reproduction package.

That should not retroactively invalidate `v0.4` if `v0.4` is otherwise a
technically honest and usable release. It should instead define the next
milestone correctly.

## Final v0.4 Release Gate

Before `VERSION` bump and tag creation, the clean release-prep branch must have:

1. a total code review
2. a total doc review
3. a detailed process audit

These reviews should judge:

- correctness regressions
- backend claim honesty
- documentation accuracy and usability
- release-surface consistency
- audit/process integrity

## v0.5 Direction

`v0.5` should take ownership of the paper-consistency gap.

For the nearest-neighbor line, that includes:

- experiment-faithful RTNN capability mapping
- closing the current 2D vs 3D gap
- importing or reproducing paper baselines and datasets
- adding paper-style ablation harnesses

## Outcome

The project now has a correct release/next-milestone split:

- release-gate reviews for `v0.4`
- experiment-consistency expansion for `v0.5`
