# Goal 1437 v1.5.1 COLLECT_K_BOUNDED Result Validator Capacity Metadata Hardening

## Verdict

ACCEPTED as a fail-clear validator hardening patch.

## Change

`validate_collect_k_bounded_result(...)` now rejects result dictionaries that omit both `capacity` and `valid_count` metadata.

The validator still preserves transition compatibility for callers that provide `valid_count` without `capacity`; it only removes the surprising silent fallback where both fields were absent and capacity became `0`.

The transition compatibility path is covered by a focused regression test, and the old unreachable `0` fallback was removed after external review.

## Boundary

This patch improves error clarity and metadata discipline only. It does not authorize stable `COLLECT_K_BOUNDED` promotion, public speedup wording, zero-copy wording, whole-app speedup claims, release tags, or release action.
