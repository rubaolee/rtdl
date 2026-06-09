# Goal4206: RT-DBSCAN Root-Shadow Parity Fixture

Date: 2026-06-09

## Purpose

Gemini's Goal4204 review asked for adversarial fixtures before any one-pass
policy renaming or promotion. Goal4206 adds and executes a root-shadow fixture
designed to stress the exact concern: a boundary item can observe a high-index
candidate while the final component root is lower.

## Fixture

The new preset is `adversarial_root_shadow_1d` in:

`scripts/goal4202_rt_dbscan_single_pass_reference_parity.py`

It uses five 3-D points laid out on a 1-D line:

- four predicate-true candidates form a connected chain whose final root is
  point `0`;
- the fifth item is a predicate-false boundary item near the high-index end of
  the chain;
- matching the Goal4194 reference requires resolving the boundary candidate
  through final roots, not merely trusting the initially observed candidate.

## Pod Result

Artifact:

`docs/reports/goal4206_rt_dbscan_root_shadow_parity_rtx4000ada/root_shadow_parity.json`

| Field | Value |
| --- | ---: |
| Commit | `ff072bbf` |
| Dataset | `adversarial_root_shadow_1d` |
| Points | 5 |
| Candidate pairs | 6 |
| Predicate-true count | 4 |
| Reference component count | 1 |
| Reference component sizes | `[5]` |
| One-pass mismatch count | 0 |
| Two-pass mismatch count | 0 |
| One-pass native pass count | 1 |
| Two-pass native pass count | 2 |

Both policies matched the Goal4194 reference labels exactly, and the one-pass
route matched the two-pass route.

## Interpretation

This is the first adversarial confirmation that the fast route's current
behavior is not just "candidate then root" in the naive sense. The native path
captures a root-like candidate, and the Numba consumer resolves that candidate
through final parent roots before materializing labels/signatures.

The result supports the ongoing direction:

- keep two-pass as explicit reference/debug machinery;
- keep one-pass as the performance route;
- rename/clarify the policy metadata only after external review of this
  adversarial evidence.

## Boundary

Goal4206 does not authorize release, route promotion, public speedup claims,
whole-app speedup claims, true-zero-copy claims, automatic partner selection, or
app-specific native engine logic.
