# Goal2773 — Claude Critical External Review: v2.5 Status and Next-Goals Packet

Reviewer: Claude (fresh independent external reviewer; not an author of the v2.5 work)
Date: 2026-05-31
Reviewing: `docs/reports/goal2773_v2_5_status_next_goals_review_packet_2026-05-31.md`
Verification basis: read the packet plus the current source it describes — `src/rtdsl/partner_continuation_protocol.py`, `src/rtdsl/neutral_buffer_seam.py`, `src/rtdsl/v2_5_partner_support_matrix.py`, `src/rtdsl/hit_stream_handoff.py`, `src/rtdsl/grouped_reduction_contracts.py`, and the partner adapters.

## Verdict

**accept-with-boundary.**

The packet's core framing is correct and well-grounded: the goal restatement, the five design rules, the tiered benchmark philosophy, the honest status description, and the acceptance direction all hold up, and the substrate it claims genuinely exists in code (this is not a paper plan). It has correctly internalized the prior-review guidance — partner choice belongs to the app, no forced partner, per-phase/per-partner claims, neutral-buffer + lifetime as prerequisites, DBSCAN fallback-backed.

The boundary conditions that keep this from a clean `accept` are four scoping/ordering corrections, each verifiable against the current code:

1. The packet **understates how far the neutral-buffer/lifetime work already is**, and as a result schedules its audit (Goal2780) too late — after building 4–5 new app-facing primitives on a handoff that still contains a torch-coercion path.
2. A **partner-set inconsistency**: the implemented protocol declares the fallback partner as **numba**, while the packet's narrative (DBSCAN, risk #2, tier map) leans on **CuPy**. "Partner choice is real" cannot be true while the doc and the declared protocol disagree on the partner set.
3. The **witness/determinism risk (#3) is flagged but not operationalized** in the acceptance bar.
4. The **tier definitions are applied loosely** for `librts` and `spatial_rayjoin`.

None are fatal; all are fixable in planning. Because the packet is a planning document (not a performance-evidence claim) and its status claims check out against code, the gating issue is scoping/ordering, not evidence — hence accept-with-boundary rather than needs-more-evidence or reject.

## Area-by-area assessment

### v2.5 goal restatement — correct, accept
"Prove the app-agnostic engine can hand generic device-resident RT outputs to explicit partner continuations, with per-phase partner choice, neutral buffer/lifetime discipline, and tiered same-contract evidence" is the right goal. It drops the over-committed "all 10 apps on Triton," keeps Triton as one optimized-but-not-mandatory partner, preserves the universal reference path, and requires explicit, fail-closed partner selection. This matches the design position in the prior reports and is internally consistent with design rules 1–5. No change requested.

### Design rules 1–5 — sound
App-agnostic engine, partner choice at the app layer, explicit ownership/copy semantics (with the explicit ban on calling reduced-copy/stream-staging "true zero-copy"), tiered benchmarks, and bounded claims are all correct and are the right invariants to enforce through the next push. Rule 3 in particular is well-stated and is already reflected in `neutral_buffer_seam.py`'s transfer-status vocabulary (`declared_copy`, `host_stage`, `borrowed_device_pointer_unmeasured`, `zero_copy_measured`).

### Current status after Goal2772 — honest and code-accurate
The "strong bounded OptiX hit-stream → partner-continuation substrate" description is accurate and appropriately bounded. I confirmed the substrate is real: declared continuation ops (`segmented_count_i64`, `segmented_sum_f64`, `segmented_min_f64`, `segmented_max_f64`, `grouped_argmin_f64`), a partner support-matrix scaffold (`V25PartnerSupportCell` with `reference/preview/descriptor/unsupported_fail_closed` statuses), and a neutral-buffer-seam module. The explicit "not yet a release gate / not true zero-copy / not whole-app / not full 10-app closure" disclaimers are correct. The caught-on-pod `group_last_hit_row_index` initializer bug is good evidence the review/pod loop works. No overclaim here.

### Next-goal ordering — mostly right, one real correction
Goal2774 (declare the grouped-reduction support matrix / public API shape) is correctly first, and the code confirms why: the Goal2771/2772 device-side grouped reductions (count/sum/xor/min/max/first/last keyed by `ray_id`) are **not yet reflected** in `V2_5_PARTNER_CONTINUATION_OPERATION_NAMES`, so there is a genuine gap between implemented device reductions and the declared op matrix that Goal2774 must close. Good.

The correction: **Goal2780 (neutral-buffer/lifetime audit) is scheduled too late.** The packet lists it as "ongoing" near the end and frames it as a future risk-check, but `neutral_buffer_seam.py` already exists *and* the old torch-coercing path still lives in `hit_stream_handoff.py` (`_maybe_torch_column` at the bottom of the module, used by the column/payload builders). That means there are currently **two coexisting seams** — the new neutral one and the old torch-shaped one. If Goals2775–2778 build five new app-facing reduction primitives before the audit reconciles those seams, the new primitives risk inheriting the torch leak, and Goal2780 then has to retrofit five primitives instead of one seam. Recommended order: **Goal2774 → Goal2780 (audit + remove/migrate the residual torch path) → 2775/2777 → 2776 → 2778.**

Within the reduction goals, the ordering is otherwise reasonable, and two items are further along than the packet implies (see findings F3): `grouped_argmin_f64` already exists (so Goal2775 max+argmax is a sibling extension, low risk and well-justified first), and a `top_k_nearest_points_2d` partner adapter already exists (so Goal2776 is generalization, not greenfield).

### Benchmark tier map — agrees, with two consistency nits
The A/B/C assignments match my independent assessment (`v2_5_ten_benchmark_apps_baseline_readiness_review_2026-05-29.md`). Two definitional inconsistencies:

- `librts_spatial_index` is labeled Tier A but is count-only with no partner-continuation phase; by the packet's own Tier definition (Tier A = same-contract *parity*), it has no partner to reach parity with. Its "remaining work" column even says "no-regression evidence," which is the Tier C definition. It behaves as a Tier C RT-baseline; label it accordingly or note it as "Tier A scalar count with no partner phase."
- `spatial_rayjoin` is Tier A for count/parity only; its rows/overlay path needs a device-resident continuation and is effectively Tier B. The packet's "decide count/parity v2.5 route" is vague — state explicitly that rows/overlay is deferred (or Tier B) while count/parity stays Tier A.

These don't change the plan, but the tier labels should be applied consistently or the definitions will erode.

### High-risk areas — correct, but under-counts the two-seams risk
Risks 1–5 are the right risks. Risk #1 ("global neutral-buffer seam not fully closed") is understated: it is not merely "every boundary must be checked," it is "a new seam and an old torch-coercing seam currently coexist, and the old one is still wired into the live handoff." That is a concrete, present condition, not a latent design risk, and it is the reason Goal2780 should move forward. Risk #2 (DBSCAN may not be Triton-native) is correct but collides with the partner-set inconsistency (F2). Risks 3–5 are well-stated; #3 needs to be made testable (F4).

### Acceptance bar — strong, with three additions
The bar is good and mostly complete. Add:

- **A hardware floor.** "Same-contract pod evidence" is implied but Triton requires sm_70+; state it as a hard gate so Tier A/B partner numbers are not quoted from incapable hardware.
- **No residual partner-privileging conversion.** Require that the old torch-coercion path is removed or migrated into the declared neutral seam, so "cross-partner copy/zero-copy metadata is machine-readable" cannot be true for the new seam while the old path silently coerces.
- **Per-op determinism/tie-break policy.** Each witness/argmax/top-k/float-sum op must publish a tie-break and determinism-or-tolerance policy. The precedent already exists in `grouped_reduction_contracts.py` ("backend must publish reduction order or tolerance schema"); reuse it so risk #3 is enforced, not aspirational.

## Answers to the six reviewer questions

**1. Is the v2.5 goal phrased correctly (partner-composable per-phase parity, not "all apps on Triton")?** Yes. Accept the restatement as written; it is consistent with the design rules and the prior reviews.

**2. Are the planned goals in the right order, or should top-k/witness/vector be reprioritized?** Order is mostly right and Goal2774-first is correct. One real change: **pull the neutral-buffer/lifetime audit (Goal2780) forward to immediately after Goal2774**, before the new reduction primitives, so they are built on a single reconciled seam. Among the reductions, keep 2775 (max+argmax — `grouped_argmin_f64` already exists, Hausdorff is ready) and 2777 (vector sum — contained extension) early; 2776 (top-k — a 2D adapter already exists) is lower-risk; 2778 (DBSCAN) should ship alongside the partner-set reconciliation (Q4).

**3. Does Goal2772 provide enough substrate to start app-facing primitive work, or should Goal2780 happen first?** Both, in sequence: Goal2772 is enough to *declare the matrix* (2774), but the neutral-buffer/lifetime audit should run **before** building 4–5 app-facing primitives, because the handoff still carries a torch-coercion path (`hit_stream_handoff.py`) alongside the new `neutral_buffer_seam.py`. Declare the matrix, audit/close the seam, then build the primitives.

**4. Is the DBSCAN fallback-backed path acceptable, or should pure Triton union-find be a release requirement?** Fallback-backed is the correct v2.5 answer; pure Triton union-find should **not** be a release requirement (forcing it would contradict design rule 2). But reconcile *which* partner backs the fallback: the implemented protocol declares `V2_5_FALLBACK_PARTNER = "numba"` and `V2_5_ALLOWED_PARTNERS = (reference, triton, numba)`, while the packet repeatedly names **CuPy** as the DBSCAN/irregular-phase fallback. Either promote CuPy to a declared, conformance-tested v2.5 partner cell (and say so in the matrix), or change the DBSCAN plan to the declared numba fallback. As written, the doc and the code disagree on the partner set.

**5. Are any benchmark apps missing or misclassified?** No app is missing (all 10 present). Two are loosely classified: `librts_spatial_index` functions as a Tier C no-regression RT baseline though listed Tier A; `spatial_rayjoin`'s rows/overlay path is effectively Tier B while only count/parity is Tier A. Tighten the labels or annotate the exceptions.

**6. What additional conformance tests are needed before v2.5 is internally complete?**
- A "no residual torch coercion outside the neutral seam" test (guards F2/F1).
- Per-op tie-break and determinism/tolerance tests for witness/argmax/top-k/float-sum (operationalizes risk #3).
- Cross-partner handoff transfer-status tests that require *measured* status (`zero_copy_measured`) before any zero-copy label, rejecting `borrowed_device_pointer_unmeasured` as a zero-copy claim.
- Partner-set parity tests: every declared allowed partner (reference, triton, numba, and CuPy if promoted) has a reference-parity test per declared op.
- Fail-closed tests for every unsupported (partner × op × backend) cell in the support matrix.

## Findings (file-level)

- **F1 — Two coexisting seams (medium).** `src/rtdsl/neutral_buffer_seam.py` exists with a full transfer-status/ownership/lifetime vocabulary, but `src/rtdsl/hit_stream_handoff.py` still coerces columns to torch via `_maybe_torch_column` (used by the hit-stream and payload column builders). The packet treats the seam as a future audit (Goal2780); in reality it is partly built and partly bypassed. Move the audit forward and make removal of the old path an acceptance item.
- **F2 — Partner-set mismatch (medium).** `partner_continuation_protocol.py` declares numba as the fallback partner; the packet's DBSCAN/risk narrative uses CuPy. Reconcile before Goal2778.
- **F3 — Substrate further along than stated (low, positive).** `grouped_argmin_f64` (witness-preserving) and `top_k_nearest_points_2d_partner_columns` already exist; Goals2775/2776 are extensions, not greenfield. The packet's effort estimate may be slightly conservative for those two — credit the existing scaffolding.
- **F4 — Risk #3 not testable (low).** The witness/determinism risk has no acceptance-bar hook; add per-op tie-break/determinism policy using the existing `grouped_reduction_contracts.py` precedent.
- **F5 — Tier-label drift (low).** `librts` (Tier A vs functionally Tier C) and `spatial_rayjoin` rows/overlay (Tier A vs Tier B) — apply the tier definitions consistently.

## Bottom line

This is a strong, honest planning packet that has absorbed the prior design guidance and is backed by a real, tested substrate — it earns acceptance in principle. The boundary is four corrections, all addressable before the next push and all verifiable in the current code: pull the neutral-buffer/lifetime audit forward so the new app-facing primitives are built on one reconciled seam rather than inheriting the still-live torch-coercion path; reconcile the declared partner set (numba) with the narrative's CuPy fallback so "partner choice is real" is true in code and not just prose; operationalize the witness/determinism risk in the acceptance bar; and apply the tier definitions consistently to `librts` and `spatial_rayjoin`. Make those four changes and the plan is sound to execute. Verdict: **accept-with-boundary.**
