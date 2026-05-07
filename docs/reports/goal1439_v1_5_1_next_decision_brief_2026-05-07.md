# Goal 1439 v1.5.1 Next Decision Brief

## Verdict

v1.5.1 is in a strong post-hardening state, but the next action must be an explicit product/release-surface decision.

This brief does not authorize public docs changes, stable `COLLECT_K_BOUNDED` promotion, speedup wording, zero-copy wording, whole-app speedup claims, release tags, or release action.

## What Just Happened

The v1.5.1 `COLLECT_K_BOUNDED` track completed three targeted post-review hardening patches:

- Goal1435 made readiness evidence explicit for all six required readiness gates.
- Goal1436 added a proposal-level false flag for whole-app speedup claims.
- Goal1437 made missing `capacity`/`valid_count` result metadata fail clearly while preserving `valid_count`-only transition compatibility.

Goal1438 then ran a broad Linux GPU-pod regression. The first broad run found one exact blocker outside collect-k: the Goal15 native helper could be compiled but then failed to launch with `PermissionError`. The fix restored executable bits after non-Windows native helper compilation. Focused Windows validation, focused Linux GPU-pod validation, and a second broad Linux GPU-pod rerun then passed.

Latest committed state:

```text
a78081eb Harden Goal15 native helper launch
```

Latest broad GPU-pod result:

```text
Ran 2829 tests in 1582.304s
OK (skipped=221)
```

## Current Evidence State

Accepted evidence now supports:

- The measured v1.5.1 `COLLECT_K_BOUNDED` contract foundation.
- Measured Embree and OptiX parity for the scoped native generic i64 path.
- Same-contract benchmark evidence without public speedup wording.
- A documented experimental public-candidate release-surface gate.
- Full Linux GPU-pod source-tree regression before the final hardening series.
- Post-hardening focused Windows and Linux validations.
- Post-hardening broad Linux GPU-pod regression after the Goal15 launch fix.

The evidence does not support:

- Stable `COLLECT_K_BOUNDED` promotion.
- Public speedup claims.
- Zero-copy claims.
- Whole-app speedup claims.
- Broad workload claims.
- Release tag action.
- Release action.

## Decision Options

Option A: prepare a public-doc link patch for the documented experimental candidate surface.

This would make the already-reviewed candidate docs easier to discover, while keeping the wording cautious. It still must not claim stable promotion, speedup, zero-copy, whole-app acceleration, or release action. Because this changes public-facing navigation, it should receive explicit user authorization and, ideally, a renewed external review.

Option B: keep `COLLECT_K_BOUNDED` internal for now and move technical work to v1.5.2.

This avoids public-surface risk and lets the next technical slice focus on stronger app-generic native-engine cleanup, reduced-copy buffer work, or larger OptiX measurements. It is safer if the project wants more 3-AI review before exposing the candidate docs.

## Recommendation

Choose Option A only if the user explicitly wants v1.5.1 to expose `COLLECT_K_BOUNDED` as a documented experimental public candidate.

Otherwise, choose Option B and move to v1.5.2 technical work. The best next technical target is not another evidence cleanup pass; it is a concrete Python+RTDL implementation slice that advances app-generic native collection or buffer/data-movement design without making zero-copy or speedup claims.

## Handoff Sentence

RTDL `main` is clean at `a78081eb`; v1.5.1 collect-k hardening and Goal1438 broad GPU-pod rerun are accepted, no public promotion/release/claim is authorized, and the next explicit decision is whether to add a cautious public-doc link for the documented experimental `COLLECT_K_BOUNDED` candidate or move technical work to v1.5.2.
