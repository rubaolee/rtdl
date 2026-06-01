# Goal2886 — Claude Critical External Review: Torch-Carrier Runtime Seam Trace and Partner-Conformance Snapshot (Goals2883, 2885)

Reviewer: Claude (fresh independent external reviewer; author of the Goal2881 review whose release-watch items this work addresses, but not an author of the Goal2883/2885 implementation)
Date: 2026-05-31
Audit range: `920df6a6` → `df0a1555` (Goals 2883–2885; the Goal2883 trace implementation lands at the `920df6a6` start anchor and is included by intent).
Verification basis: read the Goal2883 and Goal2885 reports, then inspected the code and tests they describe — `src/rtdsl/hit_stream_handoff.py` (`trace_v2_5_hit_stream_torch_carrier_runtime_seam_authority`, `_gather_payload_torch_carrier`), `src/rtdsl/v2_5_internal_readiness.py` (`_partner_conformance_snapshot`, validator), and `tests/goal2885_v2_5_partner_conformance_readiness_snapshot_test.py`. No code tests run (audit handoff); pod validation is taken from the reports' recorded runs.

## Verdict

**accept-with-boundary.**

Both deliverables materially — but partially — reduce the two Goal2881 release-watch items, and neither authorizes anything blocked. The runtime seam trace moves the torch-carrier concern from "metadata/contract provenance only" to "metadata + runtime-observed data-pointer equality + a pod-executed neutral-seam lease lifecycle, for the one carrier gather path." The conformance snapshot delivers the single canonical conformance index I suggested in Goal2881, keeps `release_conformance_complete` false under an active validator guard, and keeps descriptor-only partners visible rather than promoted. The residual findings are minor precision/scope items and remain correctly release-gate concerns.

**Release boundary:** This review authorizes nothing beyond the internal engineering coherence of Goals2883/2885. It does not authorize v2.5 release, a release tag, public/broad-RT-core/whole-app speedup wording, true-zero-copy wording, package-install wording, automatic Triton preview selection, or app-specific native engine logic. Final release remains blocked pending an explicit user-requested release packet and a fresh 3-AI release consensus.

## Did the work materially reduce the Goal2881 release-watch concerns?

**Yes, materially and honestly, but not to closure.** Goal2881 left two release-watch items: F1 (carrier exists, demoted not removed) and F2 (the seam-authority guard checked metadata/contract, not runtime dataflow). Goal2883 attacks F2 directly with two genuine runtime signals, verified in code:

1. **Embedded data-pointer observation in the real gather.** `_gather_payload_torch_carrier` computes `_data_ptr(...)` for each input column and its carrier column, derives `primitive_ids/group_ids/values_same_pointer`, and from those derives `same_pointer_evidence_observed` and `adapter_execution_proven_on_hardware` (same-pointer AND cuda AND no host copy). These are observed at execution time in the actual gather path, not asserted — and the metadata explicitly states "Pointer equality is runtime evidence for the adapter only. It does not authorize true zero-copy." This is the substantive runtime-dataflow signal Goal2881 F2 asked for.
2. **A real neutral-seam lease lifecycle.** `trace_v2_5_…runtime_seam_authority` builds seam descriptors for the three carrier columns, creates a real `create_neutral_buffer_lease`, drives `begin_partner_borrow() → complete_partner_borrow()`, and validates the lease's *derived* `event_log == (handoff_begin, continuation_complete)`, lease count, and `final_state == owner_state`, returning `status: reject` on any error. `_gather_payload_torch_carrier` records this trace when the path executes, and the report states the pod run did not skip the torch execution-path test, so it ran on real CUDA.

Together these narrow F2 from "metadata only" to "metadata + observed pointer equality + pod-executed seam lease lifecycle for the current carrier path," exactly as the Goal2883 report claims. The framing is honest: it explicitly does not remove the carrier, does not prove zero-copy, and says "future promoted partner paths still need their own runtime traces."

The Goal2885 snapshot addresses the Goal2881 optional suggestion (a single canonical conformance artifact the readiness packet links). Verified: `v2_5_internal_readiness_packet` now exposes `partner_conformance_snapshot` derived from the Goal2873 matrix (12 operations, 48 cells), and the readiness validator actively errors if `runtime_conformance_gap_count != 0`, if `release_conformance_complete is not False`, if `preview_runtime_conformance_complete is not True`, or if `cell_count != 48`. Descriptor-only cells (including `cupy_conformance`) stay visible rather than promoted. So the snapshot is a fail-closed index, not a new claim.

## Findings (ordered by severity)

### F1 — `carrier_originated_transfer_copy_lifetime: False` is asserted, not observed (low; precision)
In both the lease record and the trace return, this field is a hardcoded literal. Its name reads like an observed runtime fact, but nothing derives it from execution. The substantive runtime evidence lives in the *other* fields (observed pointer equality, derived lease `event_log`/state), so this is a naming/precision issue rather than a correctness defect — but a strict release reviewer should not read that boolean as measured. Recommend deriving it (e.g., from `same_pointer_evidence_observed` / `not host_copy_required`) or renaming it to signal an asserted design invariant, so no field claims more than it observes.

### F2 — The lease trace is a parallel attestation, adjacent to the actual copy decision (low; release-grade gap)
The seam lease lifecycle runs on descriptors *derived from* the columns, in a path separate from the real `_torch_as(..., allow_explicit_copy=...)[primitive_ids]` gather that actually moves data. So the trace proves "the neutral seam can lease these buffers with a clean `handoff_begin → continuation_complete`," not "the seam took the gather's copy/lifetime decision." The embedded pointer-equality observation partly compensates (it is in the real path), so combined they are a real narrowing — but the lease trace alone should not be read as proof that the seam *governs* the dataflow. Before a release review, the copy/lifetime decision inside `_torch_as` would ideally be routed through (or recorded by) the seam lease itself, not attested beside it.

### F3 — Carrier still exists; single-path scope; F1 narrowed not closed (low; release-watch, honestly disclosed)
Goal2881 F1 ("remove the carrier or runtime-prove the seam authority") is narrowed for the one Triton torch-carrier gather path and not generalized: the carrier remains, and other promoted partner paths have no runtime trace yet. Both reports disclose this. It stays a release-watch item.

### F4 — Snapshot is an index over out-of-range matrix substance (low; scope)
`partner_conformance_snapshot` is derived from the Goal2873 full matrix, which is in the Goal2877 lane, outside this range. Accepting the snapshot means accepting its honest indexing plus the validator guard that keeps `release_conformance_complete` false and `cell_count` fixed — it does **not** re-certify the underlying matrix substance or the per-partner kernel evidence. Same scope boundary I noted in Goal2881.

### Positive confirmations
- Observed (not asserted) pointer equality embedded in the real gather, with an explicit "not zero-copy" boundary.
- A real seam lease lifecycle with derived event-log/state validation and `status: reject` on error; pod-executed on the torch path.
- The snapshot validator fails closed: it errors if anyone flips `release_conformance_complete` to true, introduces a runtime gap, or changes the cell count.
- `cupy_conformance` is kept descriptor-only and visible, not promoted to release-grade.
- All nine v2.5 redline blocks remain intact; this range only added required-report presence for the Goal2885 report and `keep_goal2885_partner_conformance_snapshot_green` / `keep_goal2883_…` next-actions.
- Both reports frame their work as "narrowing"/"indexing," explicitly disclaim release/zero-copy/speedup/auto-Triton, and keep the release gate blocked.
- App-agnostic boundary held: nothing in this range adds app-specific engine vocabulary.

## Answers to the two audit questions
1. **Does the torch-carrier runtime seam trace materially reduce the Goal2881 release-watch concern?** Yes — materially, via observed pointer equality in the real gather plus a pod-executed seam lease lifecycle for that path. It narrows F2 substantially and partially narrows F1, without removing the carrier, generalizing to other partners, or authorizing anything (true-zero-copy stays false). The one weak spot is an asserted boolean (F1) and the lease being a parallel attestation rather than instrumentation of the copy decision (F2).
2. **Does the compact partner-conformance snapshot materially help?** Yes — it is the single canonical, fail-closed conformance index suggested in Goal2881, keeps release conformance false under validator enforcement, and keeps descriptor-only partners visible. It is a readiness-indexing improvement that authorizes nothing and re-certifies no underlying substance.

## Required fixes before a future v2.5 *release* review (not blockers for this internal work)
1. Remove the carrier, or route the actual `_torch_as` copy/lifetime decision through a seam lease so the seam *governs* the dataflow rather than attesting beside it, and generalize runtime traces to every promoted partner path (F2/F3).
2. Derive or rename `carrier_originated_transfer_copy_lifetime` so no asserted boolean reads as an observed runtime fact (F1).
3. Complete the release-grade per-partner conformance matrix in the Goal2877 lane; flip `release_conformance_complete` only with that evidence, and move `cupy_conformance` beyond descriptor-only only if it is to be a release partner (F4).

## Optional future work (clearly separated from blockers)
- Promote the runtime seam-lease trace into a reusable harness applied uniformly across all partner gather paths, so runtime provenance is a standard, not a per-path bespoke addition.
- Emit the observed pointer-equality and lease evidence into the canonical conformance snapshot so the readiness packet links runtime provenance and conformance in one surface.

## Bottom line

Goals2883 and 2885 are a coherent, honest, code-and-test-backed continuation that materially reduces — without closing — the two Goal2881 release-watch items. The runtime seam trace adds genuine execution-time evidence (observed pointer equality plus a pod-run seam lease lifecycle) for the bounded Triton carrier path while still refusing zero-copy and speedup authorization, and the conformance snapshot gives reviewers a single fail-closed index that keeps release conformance false and descriptor-only partners unpromoted. The residual items — one asserted boolean, a lease trace that attests beside rather than governs the copy decision, the still-present carrier, and the out-of-range matrix substance — are all minor and correctly remain release-gate concerns. Nothing here authorizes release, public/RT-core/whole-app speedup, true zero-copy, automatic Triton selection, package install, or app-specific native engine logic, and all nine blocks remain intact. Final v2.5 release stays blocked pending an explicit user-requested release packet and a fresh 3-AI release consensus. **Verdict: accept-with-boundary.**
