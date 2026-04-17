# Goal 236: v0.4 Final Release Gate And v0.5 Direction

Date: 2026-04-11
Status: implemented

## Objective

Freeze the correct final decision boundary for `v0.4.0` and explicitly define
what belongs to `v0.5`.

## Release Rule For v0.4.0

`v0.4.0` may proceed only after all three of the following are completed in the
clean release-prep branch:

1. total code review
2. total doc review
3. detailed process audit

These are final release-gate reviews, not open-ended redesign work.

## What v0.4 Must Prove

The `v0.4.0` release decision is about whether the nearest-neighbor line is
ready as released software:

- feature closure
- backend closure
- documentation honesty
- process honesty
- release-surface usability

It is **not** the milestone that must solve every paper-reproduction question.

## What Moves To v0.5

`v0.5` is the paper/implementation consistency milestone.

Its core requirement is:

- RTDL must be able to reproduce the relevant experiments from the target
  papers it claims to follow

For the current nearest-neighbor line, that means `v0.5` should address the
RTNN consistency gap explicitly:

- 3D nearest-neighbor public surface
- bounded-radius KNN interface
- paper datasets
- paper baseline libraries
- paper-style ablation harness
- stronger hardware-faithful reproduction where feasible

## Outcome

`v0.4.0` is now blocked on final review closure only.

`v0.5` is now defined as the milestone for paper/implementation consistency,
including honest experiment-level reproduction work.
