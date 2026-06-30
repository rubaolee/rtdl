# Claude Review: Goal 196 Fixed-Radius Neighbors Contract

Date: 2026-04-09
Reviewer: Claude (claude-sonnet-4-6)

## Verdict

The contract is sharp enough to implement. All three review questions — ordering,
tie policy, and `k_max` truncation — are answered without ambiguity. Two small gaps
exist but neither blocks implementation. Approved.

## Findings

**Ordering and tie policy — fully deterministic.**
The ordering rule is stated consistently across both documents: ascending `query_id`,
then ascending `distance`, then ascending `neighbor_id`. The tie rule (equal-distance
neighbors ranked by `neighbor_id`) is explicit. No underspecified case exists.

**`k_max` truncation — honest and usable.**
The overflow rule is unambiguous: sort under the public ordering rule, emit the first
`k_max` rows, emit no overflow marker. The contract also explicitly disclaims any
promise of total-neighbor counts beyond what is emitted. That is the right policy for
a first-release row-materialization workload.

**Planned-versus-implemented status — honest.**
Three separate places in the feature home state that the workload is not yet
implemented: the Status section, the Limitations list, and the Try Not section.
No user reading the document could reasonably mistake it for a shipping feature.

**Gap 1 — `exact=False` in the kernel example is unexplained.**
The example kernel passes `exact=False` to `rt.fixed_radius_neighbors`, but the
contract never defines what approximate mode means or whether it still guarantees the
public ordering and tie rules. If approximate mode is allowed to skip tie-breaking or
reorder rows, the determinism guarantee is undermined. The contract should either
remove `exact=False` from the example or state explicitly whether determinism holds
under approximate mode.

**Gap 2 — `query_id` and `neighbor_id` types are unspecified.**
The emitted fields are named but their type and source are not defined. Are they
integer row indices? Caller-supplied keys? The best-practices note says to keep them
"stable and auditable" but does not say what they are. An implementer must infer this.
A single sentence stating the expected type (e.g., non-negative integer row index) and
source would close this gap.

## Summary

The contract succeeds at its stated purpose. The radius rule, ordering, tie policy, and
truncation behavior are all determinate. The planned-only status is clear. Neither gap
is a blocker: Gap 1 is resolvable by removing `exact=False` from the example or
annotating it; Gap 2 is resolvable by one added sentence. Both are documentation-only
fixes that can be done in an early implementation goal without reopening the contract.
