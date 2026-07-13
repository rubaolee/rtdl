# Owner Directive — v2.14.3 Fresh Headline Correction + Device-Resident Payoff Gate

Date: 2026-07-05
From: owner (via Claude review)
To: main implementation AI
Status: required before Goal5005 documentation

This directive supersedes any plan that headlines v2.14.3 fresh at ~5.0 s. It is based on
the reconciled fresh-regime evidence: the `--device-resident-carrier` route is ~0.78 s
**slower** in fresh one-shot than the existing host-carrier fast-pack route, with the
regression entirely in downstream (1.48 s → 2.37 s). Do not proceed to Goal5005 docs until
Actions 1–3 are complete and Action 4's gate is defined.

Do NOT roll back device-resident code. It is a flag (`--device-resident-carrier`); both
routes coexist. Deletion would discard a possibly-useful architecture stepping stone. The
correction is to the headline and framing, not the code.

---

## Action 1 — Make the fast-pack route the v2.14.3 fresh headline

Work:
- Set the v2.14.3 fresh one-shot product number to the host-carrier fast-pack route
  (`--fast-scaled-point-pack`, no `--device-resident-carrier`): ~4.22 s on top4.
- Demote the `--device-resident-carrier` ~5.0 s route to a labeled "experimental /
  architecture track."

Acceptance criteria:
- The matrix and all v2.14.3 wording show BOTH fresh numbers, same input, same regime:
  fast-pack ~4.22 s AND device-resident-carrier ~5.0 s.
- Every place the device-resident number appears is labeled: "currently ~0.78 s slower in
  fresh one-shot (downstream device-kernel compile/setup); payoff unproven."
- No document presents ~5.0 s as v2.14.3 progress without the ~4.22 s comparator adjacent.

Exit label: `completed_fresh_headline_set_to_fast_pack__device_resident_labeled_architecture_track`

## Action 2 — Fix the accounting attribution and false precision

Work:
- Re-run the SAME fresh command BEFORE and AFTER the `writer_free_hot_keys` fix in ONE
  session on ONE POD, to isolate the true accounting delta (expected ~0.003 s from the
  device midpoint query-point phases).
- Report fresh as a median-of-N with variance, not a single-run 6-decimal value.

Acceptance criteria:
- The report states the isolated accounting delta (same-run before/after) separately from
  run-to-run variance. The `4.816 s → 5.004 s` change is NOT attributed to the accounting
  fix unless the same-run delta actually accounts for it.
- Fresh is reported as `~5.0 s (median of N≥5; ±~0.2 s run variance)`, not `5.003915 s`.
- Same discipline applied to the fast-pack ~4.22 s headline (median-of-N, variance stated).

Exit label: `completed_accounting_delta_isolated__fresh_reported_as_median_with_variance`

## Action 3 — Re-audit every device-route number with the corrected accounting

Work:
- The buggy `writer_free_hot_keys` affected every `--device-resident-carrier` number before
  Goal5004: Goal4998, Goal4999's `0.3295 s` replay, Goal5001's `4.816 s`.
- Recompute the matrix's prepared-replay (`0.332861 s`) and compile-prewarm (`4.584897 s`)
  rows with the corrected key list.

Acceptance criteria:
- Every matrix cell is labeled pre-fix or post-fix accounting.
- Any cell still on pre-fix accounting is recomputed or explicitly marked provisional.

Exit label: `completed_device_route_numbers_reaudited_post_accounting_fix`

## Action 4 — Gate any further device-resident work behind a demonstrated payoff

The device-resident route only pays off in: (a) a warm long-lived process, (b) true
query-many with DISTINCT inputs, or (c) a real downstream device operator that consumes the
carrier without a host round-trip. None is demonstrated. Therefore:

Work (a decision/measurement gate, NOT implementation):
- Produce ONE measured payoff demonstration:
  - true query-many: one prepared base LSI serving ≥2 DISTINCT query inputs, fresh-measured
    per query (expect ~2 s/query per the workspace analysis, not 0.33 s); OR
  - a real generic downstream device operator (grouped count / filter / reduce) consuming
    the device carrier device-resident, end-to-end, vs the fast-pack path doing the same
    with a host boundary — showing device-resident actually wins net.

Acceptance criteria:
- If a payoff is demonstrated with numbers: device-resident may continue, scoped to that
  regime, labeled accordingly.
- If no payoff can be demonstrated: STOP the device-resident performance track for v2.14.3;
  keep the code behind its flag as experimental; do not spend further goals on it.
- No "query-many" wording anywhere unless distinct-input measurement exists (fix the CLI/help
  naming debt too).

Exit labels:
`device_resident_payoff_demonstrated_continue_scoped`
or
`device_resident_payoff_not_demonstrated_stop_track_for_v2_14_3`

---

## Order

```text
Action 1 -> Action 2 -> Action 3 -> Action 4 (gate) -> then Goal5005 docs
```

Goal5005 documentation may proceed only after Actions 1–3 are complete and Action 4 has an
exit label. Goal5005 must then document:
- fresh top4 = fast-pack ~4.22 s (median, variance);
- device-resident ~5.0 s = experimental architecture track, slower in fresh;
- compile-prewarm and prepared-replay = diagnostic;
- top4 author ratio = not measured;
- true query-many = demonstrated only if Action 4 produced distinct-input evidence.

## Non-authorization

No ~5.0 s unqualified fresh headline; no false-precision fresh number; no unlabeled matrix
cells; no further device-resident performance goals before Action 4's gate; no "query-many"
without distinct-input measurement; no author parity/ratio; no RayJoin-specific core
semantics; no public v2.14.3 release before the corrected matrix and boundary report.
