# Goal 108 Scope Charter Critique

Date: 2026-04-05
Status: complete

## Main criticism

The main risk was that “programmable counting/ranking kernels” was still too
broad and could become a back door for unconstrained demos.

## Rebuttal

That category is no longer in core scope.

It survives only as `experimental`, and the charter now adds:

- a hard exclusion test:
  - if RT candidate search is not central to the computational advantage, the
    family is not in scope
- explicit gray-area non-examples
- a comparative test against the next most plausible alternative family

If a candidate workload fails those tests, it stays experimental or moves out
of scope.

## Secondary criticism

Another risk was that code generation stayed alive inside the workload charter
and quietly consumed too much effort.

## Rebuttal

The charter now removes generate-only mode from the workload-family matrix
entirely.

It remains a separate experimental product-mode effort under the Goal 107
gates.

## Final position

The charter is intentionally stricter than both the first-draft roadmap and the
first-draft scope charter.

That is its value.
