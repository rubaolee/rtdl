# Goal5006: 10x Preconditions, Regime Gate, And Prepared-Body Evidence

Date: 2026-07-05

## Verdict

`prepared_body_10x_evidence_recorded__fresh_10x_not_authorized__start_p3_fresh_optimizations`

## P1 Regime Declaration

The `~0.42s` 10x target is **not** a distinct-domain fresh one-shot target.

It is only valid for:

> prepared base + same scale-domain + distinct query batches

The current evidence does not yet prove that regime. It proves only a prepared operator body on the same top4 input after explicit session preparation.

Therefore:

- `~4.22s` = long-lived-process fresh fast-pack route, not cold CLI process.
- `~11.6s` = observed OS-process-cold median, high variance, from Goal5005.
- `~0.331s` = prepared operator body measurement after explicit prepare, not fresh, not true query-many.
- distinct-domain fresh has a known floor around `~2s`, because Goal5003 showed the scale-domain / workspace part is per input.

Any claim of `~0.42s` without this regime label is invalid.

## Existing Prepared-Body Evidence

Artifact:

- `history/internal_docs/goal5006_fastpack_prepared_body_repeat5_2026-07-05_v2.json`

Command route:

- `--device-columnar`
- `--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000`
- `--point-location-device-face-columns`
- `--fast-scaled-point-pack`
- `--compiled-group`
- `--prepared-operator-session --warmup-runs 1 --repeat 5`

Result on top4 County x Zipcode:

| Metric | Value |
|---|---:|
| median writer-free prepared body | `0.331s` |
| best | `0.329s` |
| worst | `0.333s` |
| median LSI phase | `0.0031s` |
| median downstream floor | `0.327s` |
| LSI rows | `428322` |
| descriptor pairs | `15014` |

The claim boundary in the artifact now says:

- `prepared_operator_body_measurement: true`
- `true_query_many_measurement: false`
- `fresh_one_shot_headline: false`

This is the correct framing.

## Interpretation

Relative to the long-lived-process fresh fast-pack route (`~4.22s`), the prepared-body measurement is about `12.8x` lower:

`4.22 / 0.331 ~= 12.8`

But this is not a fresh result. It is evidence that the operator body can meet the 10x target **after explicit prepare**.

The missing proof is true query-many:

- at least three distinct same-domain query batches;
- one distinct-domain query showing the expected workspace rebuild cost;
- per-query timings reported independently.

Until then, "query-many" wording is not authorized.

## P3 Work Starts Now

The owner directive authorizes two regime-independent improvements before P2/P4:

1. **P3-A: compile/prewarm/AOT-style setup reduction**
   - Goal: reduce the repeatable fresh setup component already identified in Goal5002.
   - Constraint: prewarm cost must be reported separately and not subtracted from fresh without a real long-lived process model.
   - Expected effect: useful but not 10x by itself.

2. **P3-B: replace weak bitonic sort with a better generic GPU ordering primitive**
   - Goal: improve `sort_map0_device_columnar_sec` / `sort_map1_device_columnar_sec`.
   - Constraint: must be generic ordering infrastructure, not RayJoin-specific sorting.
   - Correctness gate: same structural anchors and ordering validation where applicable.

## Device-Resident Track

Device-resident carrier remains stopped for v2.14.3 performance work.

It can only reopen after:

- P2 true same-domain distinct-query measurements exist; and
- device-resident end-to-end downstream beats fast-pack in that regime.

## Non-Authorization

This goal does not authorize:

- fresh 10x claims;
- cold-process 10x claims;
- true query-many claims;
- author parity claims;
- reopening device-resident performance work without the P4 gate.
