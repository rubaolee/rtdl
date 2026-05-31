# Goal2773 Claude Review Intake And Revised v2.5 Plan

Date: 2026-05-31

Status: accepted correction intake. This document does not authorize release,
public speedup, or true-zero-copy wording.

## Purpose

Claude reviewed the Goal2773 v2.5 status/next-goals packet and returned
`accept-with-boundary` in:

`docs/reviews/goal2773_claude_review_v2_5_status_next_goals_2026-05-31.md`

Codex checked the review against the current source. The review is accurate and
should change the next-goal order before more app-facing primitives are built.

## Verified Corrections

### 1. Neutral-buffer audit must move earlier

Claude is correct that the code currently contains two coexisting seams:

- `src/rtdsl/neutral_buffer_seam.py` defines a real v2.5 neutral-buffer seam,
  including transfer statuses and ownership/lifetime vocabulary.
- `src/rtdsl/hit_stream_handoff.py` still contains `_maybe_torch_column(...)`
  and `torch.as_tensor(...)` paths used by hit-stream and payload builders.

This means Goal2773 understated the immediacy of the risk. The neutral seam is
not only a future design need; it is partly implemented while older torch-shaped
handoff logic remains live.

Action: run the neutral-buffer/lifetime audit immediately after the support
matrix/API declaration, before building additional app-facing primitives.

### 2. Partner-set wording must be reconciled

Claude is correct that the partner set is easy to misstate:

- `V2_5_PRIMARY_PARTNER = "triton"`.
- `V2_5_FALLBACK_PARTNER = "numba"`.
- `V2_5_CONFORMANCE_PARTNER = "cupy_conformance"`.
- `V2_5_ALLOWED_PARTNERS` includes reference, Triton, Numba fallback, and CuPy
  conformance.

The support matrix treats CuPy as descriptor/conformance support, not as a
promoted fallback kernel family. Goal2773's DBSCAN discussion leaned too loosely
on "CuPy fallback." That must be sharpened:

- If DBSCAN uses CuPy as the app-chosen irregular continuation partner, it needs
  a declared support-matrix cell and conformance tests for that role.
- If DBSCAN follows the current fallback role, the fallback must be described as
  Numba, with CuPy only as conformance/interoperability unless promoted.

Action: reconcile this before the DBSCAN continuation goal.

### 3. Existing substrate is further along than Goal2773 implied

Claude is correct that some planned primitives are extensions, not greenfield:

- `grouped_argmin_f64` already exists in the continuation protocol and Triton
  partner continuation.
- `top_k_nearest_points_2d_partner_columns` already exists as a partner adapter.

Action: treat witness/max+argmax and top-k work as contract generalization and
integration work, not first invention.

### 4. Witness/tie-break/determinism policy must be testable

Claude is correct that Goal2773 named this risk but did not add it to the
acceptance bar. The precedent exists in grouped reduction contracts: each
backend must publish a reduction order or tolerance schema.

Action: every witness, argmax, ranked/top-k, and floating reduction primitive
must declare deterministic tie behavior or explicit tolerance, and tests must
enforce it.

### 5. Tier labels need tightening

Claude is correct that:

- `librts_spatial_index` behaves like a Tier C RT/no-regression row unless a
  partner continuation phase is explicitly added.
- `spatial_rayjoin` count/parity can stay Tier A, but rows/overlay behavior is
  Tier B-like and should be labeled separately or deferred.

Action: update the benchmark manifest/plan wording before final v2.5 readiness.

## Revised Next-Goal Order

The corrected near-term order should be:

| Order | Goal | Purpose |
| ---: | --- | --- |
| 1 | Goal2774 | Declare the v2.5 grouped-reduction support matrix/API shape, including Goal2771/2772 fields. |
| 2 | Goal2775 | Audit/reconcile the neutral-buffer seam and old torch-coercion paths; define fail-closed migration requirements. |
| 3 | Goal2776 | Extend witness/max+argmax contracts from existing `grouped_argmin_f64` substrate. |
| 4 | Goal2777 | Add grouped vector-sum contract/runtime path. |
| 5 | Goal2778 | Generalize top-k/ranked summary from existing top-k adapter substrate. |
| 6 | Goal2779 | Reconcile DBSCAN partner role: Numba fallback vs promoted CuPy app-chosen irregular continuation. |
| 7 | Goal2780 | Execute tiered benchmark harnesses with corrected Tier A/B/C labels and phase timing. |
| 8 | Goal2781 | Produce v2.5 readiness packet with external review and explicit non-claim boundaries. |

This preserves the spirit of Goal2773 but moves the neutral seam/lifetime audit
from late-stage cleanup to early prerequisite work.

## Current Verdict

Codex accepts Claude's review as valid and actionable.

Goal2773 remains useful as a broad status packet, but its planned ordering must
be amended by this intake before starting the next implementation sequence.
