# Claude Review For Goal3527 v2.8 Performance Recovery Plan

Date: 2026-06-05

Verdict: `accept-with-boundary`

---

## Summary

Goal3527 is the correct next engineering move after Goal3524. The consensus gate
before implementation is appropriate. The two-table strategy is architecturally
sound, Barnes-Hut P0 is correctly prioritized, partner language is handled
correctly, and the app-agnostic boundary is preserved. Two pre-implementation
gaps need to be closed before Codex begins any implementation work; neither
requires rejecting the plan, but both are load-bearing enough to block the
start of Workstream A or B.

---

## Findings By Severity

### Critical (block implementation)

**C1 — Workstream A schema does not inherit the sub-millisecond scale
requirement from Workstream C.**

Workstream C correctly states: "For rows below roughly one millisecond, add
either larger scale or repeated steady-state timing. Do not present
launch-noise rows as strong performance claims."

Workstream A defines required columns for the promoted-path table but does not
carry this constraint into the schema. Several rows that will appear in the
promoted-path table are sub-millisecond in the Goal3524 artifact:
- `spatial_rayjoin_optix_prepared_full_route`: 0.000483 s
- `robot_collision_optix_prepared_device_buffers`: 0.001905 s
- `raydb_optix_partner_resident_count`: 0.000655 s
- `triangle_counting_optix_rt_graph_2a1_partner`: 0.000437 s
- `rtnn_optix_prepared_3d_ranked_summary`: 0.001646 s

If the promoted-path table is populated at the same scale as Goal3524, the same
credibility problem that makes Goal3524 inadequate as a final headline will
recur in the new table. Workstream A must explicitly require minimum scale or
multi-repeat for any promoted-path row below one millisecond.

**C2 — Promoted-path contracts for RayJoin are not confirmed to exist.**

The plan (Workstream B, RayJoin P1) requires measuring "count/parity, relation
columns, shape-pair payload, and overlay-area continuation" as separate rows.
Before implementation can start on Workstream A, it must be known whether these
contracts are already runnable or whether authoring them is itself implementation
work. If the latter, there is a sequencing dependency: Workstream B (RayJoin
P1) depends on contract authoring that is not tracked in this plan. The plan
should either confirm these contracts exist and name the entry points, or add
an explicit prerequisite task for contract authoring before the promoted-path
table work starts.

---

### Moderate (should fix before implementation, non-blocking)

**M1 — "Parity" threshold for Barnes-Hut is undefined.**

Gate 3 of Workstream D says "Barnes-Hut node coverage is a real P0 regression
until investigated." The Workstream B repair action says "recover to at least
parity." Neither defines parity quantitatively. The v2.3 evidence baseline is
~12 ms; the v2.8 result is ~25–30 ms; the regression is 2–2.5x. "Parity"
should be specified (e.g., v2.8 must not exceed v2.3 by more than N%) so the
acceptance gate is not indefinitely deferred by ambiguity over whether
a 0.95x result closes the P0 item.

**M2 — Barnes-Hut investigation has no stop condition.**

The plan lists five candidate causes (codegen, launch structure, prepared-handle
setup, threshold parameters, generic bookkeeping) which is useful scaffolding.
It does not name a maximum investigation scope or a point at which an honest
"we cannot recover this row under the same contract" classification is
acceptable. Without this, the P0 item can block the entire plan indefinitely.
A fallback disposition—e.g., "if no root cause is confirmed within Goal3528 +
Goal3529 review cycles, treat Barnes-Hut as an honest regression requiring a
separate workstream"—should be added.

---

### Minor (observations, no blocking action required)

**m1 — "CuPy where needed" vs "CuPy where explicitly selected."**

Design Rule 2 says "Partners remain explicit. Current benchmark partner
continuations are CuPy **where needed**." The phrase "where needed" is slightly
ambiguous; it could be read as giving permission to substitute CuPy wherever it
is faster, rather than only where the developer explicitly selected it. Gate 5
of Workstream D uses stronger language: "CuPy is the selected partner for
current promoted partner rows that need continuation unless a row explicitly says
otherwise." The gate language is sufficient, but the design rule body would be
clearer if revised to match it.

**m2 — `case_repeat: 1` in compact artifact.**

The Goal3524 compact JSON records `case_repeat: 1` in both standard and rerun
runs. The weak rerun was a separate execution pass, not a within-run multi-repeat.
Workstream A's column list does not include a `case_repeat` or timing-methodology
field. For a promoted-path table that will be used in planning, the schema should
record whether timing is single-pass, median-of-N, or tail-of-N so the
reproducibility of any given row is auditable from the artifact alone.

---

## Answers To Review Questions

**1. Is Goal3527 the right next engineering move?**

Yes. Goal3524 returned a median speedup of 1.002x with 5 losses including a
confirmed 2–2.5x Barnes-Hut regression. Continuing to implement before
diagnosing the regression and before measuring the actual promoted-path
contracts would produce a second round of results that are equally unfit for a
release narrative. The consensus gate is the correct sequencing decision.

**2. Is the two-table strategy correct?**

Yes. The same-runner diagnostic table answers "did we regress under the old
contract?" The promoted-path table answers "what does v2.8 actually achieve
under its optimized contracts?" These are distinct questions that require
distinct methodologies. Collapsing them into one table would either hide the
regression (if only the promoted-path is shown) or misrepresent v2.8's
capabilities (if only the same-runner table is used as the headline). The
strategy is correct. The required columns for Workstream A are specific and
complete, subject to C1 above regarding scale requirements.

**3. Are Barnes-Hut P0 and RayJoin P1 correctly prioritized?**

Barnes-Hut P0 is correct. The regression is confirmed across two independent
runs on the same hardware (0.401x standard, 0.503x rerun). It is the largest
single performance signal in the Goal3524 dataset in either direction. Any
positive v2.8 performance positioning that does not first resolve this row is
not credible.

RayJoin P1 is appropriate. The 1.096x same-runner result is a small win on an
old contract that does not exercise the full v2.8 RayJoin promoted paths. It is
not a regression, so P1 is the right level; it should not be promoted to P0.
The requirement to stop using the 1.096x row as the RayJoin headline is
explicitly correct.

The P2 items are correctly grouped. The contact_manifold and triangle_counting
rows flip sign between the standard run and weak rerun (contact: 0.973x →
1.030x; triangle: 0.992x → 1.025x), which confirms they are parity/noise and
correctly receive P2 treatment rather than P0/P1.

**4. Does the plan preserve the app-agnostic engine boundary?**

Yes. The design rules state: "The app developer does not write OptiX code in
v2.8." Gate 8 states: "No app-specific native-engine shortcuts are allowed."
The promoted-path table requirement (Workstream A) measures through RTDL
primitives and explicit partner continuations, not through shortcuts that
bypass the engine boundary. The language is unambiguous and consistent
throughout.

**5. Does it handle partner language correctly?**

Yes, with the minor qualification noted in m1. PyTorch must not silently enter
the v2.8 performance path—this is stated both in Design Rule 2 and Gates 5–6
of Workstream D. The triangle_counting compact artifact notes already record
"CuPy-owned graph preprocessing/device columns," which is consistent. The
Workstream D gates are sufficient to enforce this at review time.

**6. What must change before implementation starts?**

Two changes are required (C1 and C2 above):

1. Add an explicit minimum-scale or multi-repeat requirement to the Workstream A
   promoted-path schema for rows below one millisecond. This can be a single
   sentence added to the Workstream A column definition: e.g., "For any row
   whose primary metric is below 1 ms, the artifact must record either a scale
   sufficient to make the row timing measurement noise under 5%, or a case_repeat
   sufficient to achieve the same."

2. Before Workstream A or the RayJoin P1 work begins, confirm in a pre-flight
   note (not a new implementation goal) which promoted RayJoin contracts
   (count/parity, relation columns, shape-pair payload, overlay-area
   continuation) are already runnable and which require new contract authoring.
   If authoring is required, that work must be sequenced explicitly before the
   promoted-path table measurement.

No other changes are required to proceed with the plan.

---

## Verdict

`accept-with-boundary`

The plan is accepted with the following boundary: implementation must not begin
until C1 (sub-millisecond scale requirement added to Workstream A schema) and
C2 (RayJoin promoted-path contracts confirmed or authoring sequenced) are
resolved. The consensus gate must hold until all three AI reviews are in.
Barnes-Hut P0 must be resolved—or explicitly reclassified per M2 guidance—
before any positive v2.8 promoted-path positioning is used in planning
artifacts.
