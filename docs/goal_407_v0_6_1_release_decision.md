# Goal 407: v0.6.1 Release Decision

## Objective

Record the release decision for the corrected RT graph line after:

- internal 3-AI pre-release gates
- external independent release check

## Decision boundary

The earlier `v0.6.0` tag was attached to the mis-scoped graph-runtime line and
must not be reused for the corrected RT release.

Therefore the corrected release identifier is:

- `v0.6.1`

## Acceptance condition

If the final release decision is positive, package the decision and proceed to
the git release act under Goal 408.
