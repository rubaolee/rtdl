# Claude Review — Goal4947 Layer 1/2 Status And Next Plan

Date: 2026-07-04
Reviewer: Claude (strict)
Under review: `goal4947_layer1_layer2_status_and_next_plan_2026-07-04.md`

## Verdict

```text
approve_goal4947_status_and_next_plan
(proceed with Goal4947; three strategic amendments, not blockers)
```

Disciplined and honest. It built Layer 1/2 per the blueprint, **implemented the
genericity red-lines in code (verified)**, and correctly labels the result a
capability proof, not a performance proof. Proceed — with the amendments below,
which exist to stop "capability" from accumulating without ever moving a real
RayJoin phase.

## Verified in code (not trusting the prose)

The Layer-1 red-lines from the blueprint are genuinely implemented in
`src/rtdsl/device_column_row_buffer.py`:
- L275-276: rejects any point-location id column that is not `face_id`/`segment_id`
  (`raise ValueError`), and L219 requires LSI pairs to expose exactly two fields.
- L75: `native_device_columns cannot materialize host rows before handoff`.
- L120/138: `app_specific_schema_allowed: False`; docstring: the carrier is "just
  the produced id vector … does not encode output chains, domain semantics."

So the genericity claim (Q6) is real, not asserted. Credit.

## What was actually proven — and its limit

Goals 4942-4946 proved: native PIP `face_id`/`segment_id` device columns →
generic Layer-1 row-buffer → v2.6 Numba handoff → generic Numba CUDA execution,
`host_column_materialization_used: false`, on POD hardware. That is a real
**capability/plumbing milestone.** The packet says so honestly.

**Its limit (be explicit):** the proof is **3 rows** with a **trivial op
(`uint32_equal_mask`) that RayJoin does not use.** It proves the chain *connects*,
not that it is fast, that it scales, or that it moves any RayJoin phase. RayJoin's
real numeric continuations are reprojection, sort, dedupe, midpoint — none of which
were run through the bridge yet.

## Amendments

### AM1 — Goal4949 must remeasure with the REAL hot-path continuations, not demo ops
The risk: `uint32_equal_mask` (4946) and `segmented_count_i64` (4947 candidate)
are generic but **RayJoin does not use them**, so they will never move a RayJoin
phase. If Goal4949 remeasures with these, "no phase moved" is a trivial artifact of
testing the wrong op — and it could either falsely kill Layer 2 or invite endless
plumbing demos that look like progress. **Goal4949 must route RayJoin's actual
hot-path numeric continuations (reprojection / sort / dedupe) through the Layer 1/2
bridge and measure those phases.** Do not let generic-but-RayJoin-irrelevant ops
accumulate as "capability" without a real phase moving.

### AM2 — Keep the prize in view: Layer 3 (writer) is bigger than all of Layer 1/2
Layer 1/2 attacks at most the reproj/sort (~0.8-0.9 s) plus marshalling. The
**writer is ~1.7-1.9 s (Layer 3) and is untouched by any Layer 1/2 work.** So even a
perfect Layer 1/2 leaves the single biggest cost in place. Goal4949/4951 must weigh
this honestly: "Layer 2 can recover ~0.8 s; Layer 3 can recover ~1.5 s." Be prepared
that the honest remeasure likely says **"move to Layer 3."** Do not over-invest in
Layer 2 expansion because the plumbing is fun to extend.

### AM3 — Sharpen the genericity gate (Goal4948) to USEFUL non-RayJoin work
The exit gate ("non-RayJoin columns enter the row-buffer; Numba continuation
executes") is plumbing-level again. To actually prove "not RayJoin-shaped," the gate
should show the same row-buffer + continuation machinery doing something *useful* for
a structurally different app (e.g. kNN + a reduction), not merely that a foreign
column can enter the buffer.

## One thing to check (not a blocker)
`src/rtdsl/output_assembly.py` exists in core. The packet says Layer 3 (writer/output
assembly) is **not** being worked on and must not restart without a fresh phase
table. Confirm `output_assembly.py` is pre-existing (v2.8 overlay-area work) and not
quiet Layer-3 drift; if it is new Layer-3 work, it violates the packet's own rule.

## Answers to the ten questions

1. Accurate 4942-4946 summary? Yes (POD evidence, honest).
2. Capability vs performance distinguished? Yes, explicitly.
3. 4946 = real execution not just planning? Yes — real Numba CUDA over a native
   device column, no host materialization.
4. Claim boundaries preserved? Yes.
5. Is Goal4947 the right next step? Yes (prove the LSI side of the bridge) — with
   AM1: plumbing ≠ progress; the remeasure with real ops is what counts.
6. Is Goal4948 needed? Yes (blueprint rule) — sharpen per AM3.
7. Is Goal4949 correctly placed after the execution proof? Yes, and it is the
   crucial gate — must use real hot-path ops (AM1).
8. Layer 3 kept separate? Stated yes — verify `output_assembly.py` isn't drift.
9. Goal4950/4951 gates bounded? Yes (4950 conditional on measured target +
   byte-equal + no whole-app claim; 4951 external review + explicit branch).
10. Proceed with Goal4947? Yes, with AM1-AM3.

## Non-authorization

No RayJoin whole-app speedup, no true-zero-copy, no release wording, no broad Numba
superiority, no Layer 3 writer implementation, no app-specific output-chain semantics
in core, no V3/V4. Proceed with Goal4947 as bounded capability work; the first real
performance signal is Goal4949 remeasured with actual hot-path continuations.
