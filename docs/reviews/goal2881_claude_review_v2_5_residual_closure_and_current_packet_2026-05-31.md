# Goal2881 — Claude Critical External Review: v2.5 Residual Closure and Current Packet (Goals2878–2880)

Reviewer: Claude (fresh independent external reviewer; author of the Goal2868 review whose residuals this work addresses, but not an author of the Goal2878–2880 implementation)
Date: 2026-05-31
Audit range: `d8d63b26` → `ad2cfd23` (5 commits, Goals 2878–2880).
Verification basis: read the three deliverable reports (`goal2878_…residual_closure_map…`, `goal2879_torch_carrier_seam_authority_provenance…`, `goal2880_current_packet_after_torch_carrier_provenance…`), then inspected the code and tests they describe — `src/rtdsl/hit_stream_handoff.py` (carrier provenance fields + `validate_v2_5_hit_stream_neutral_seam_authority`), `src/rtdsl/v2_5_internal_readiness.py` (blocked actions + required-report presence), `tests/goal2879_torch_carrier_seam_authority_provenance_test.py`, and `docs/reports/goal2880_current_packet_after_seam_provenance_pod/goal2855_summary.json`. Spot-confirmed the existence and framing of the Goal2872/Goal2873 evidence the closure map leans on. No code tests run (doc/audit handoff; `git diff --check` clean).

## Verdict

**accept-with-boundary.**

The three deliverables in this range are correct and honestly scoped. The residual-closure map accurately states which Goal2868 residuals are closed, partially closed, or still release-watch items without overclaiming; the torch-carrier seam-authority provenance hardening is real, code-backed, and test-enforced; and the fresh Goal2880 seven-app packet is a genuine post-provenance refresh that is green and claim-boundary-clean. All nine v2.5 redline blocks survived this range's edits intact. The residual findings below are minor and are correctly release-gate concerns, not internal-packet defects.

**Release boundary:** This review authorizes nothing beyond the internal engineering coherence of Goals2878–2880. It does not authorize v2.5 release, a release tag, public/broad-RT-core/whole-app speedup wording, true-zero-copy wording, package-install wording, automatic Triton preview selection, or app-specific native engine logic. Final release remains blocked pending an explicit user-requested release packet and a fresh 3-AI release consensus.

## Scope boundary of this review (important)

My audit covers Goals2878–2880 directly. The closure map's F4/F5 "closed" statuses rest on **Goals2871–2876**, which are outside this range and are the declared subject of the separate **Goal2877** review. I directly verified: (a) the closure map's framing honesty (Goal2878), (b) the provenance hardening code and test (Goal2879), and (c) the seven-app packet (Goal2880); and I spot-confirmed that the Goal2872 tie-break smoke and Goal2873 conformance matrix exist and keep release-conformance false. I did **not** independently re-certify the full Goal2872–2875 conformance substance — that belongs to Goal2877. Goal2881 should not be treated as closing the conformance-matrix audit.

## Findings (ordered by severity)

### F1 — Torch carrier is provenance-hardened, not removed (low; release-watch, correctly disclosed)
Goal2879 is a real, code-level tightening of the strongest Goal2868 residual. Verified in `hit_stream_handoff.py`:
- `transfer_copy_lifetime_authority` was added to `GENERIC_HIT_STREAM_TORCH_CARRIER_FORBIDDEN_AUTHORITY_FIELDS` and **removed** from the carrier adapter's own metadata (the test asserts `assertNotIn("transfer_copy_lifetime_authority", adapter)`).
- The adapter now emits `carrier_metadata_scope = "triton_launch_carrier_only"` and `authoritative_metadata_origin = "neutral_buffer_seam_only"`.
- `validate_v2_5_hit_stream_neutral_seam_authority(...)` recursively scans the carrier for forbidden authority fields, requires the contract's `transfer_copy_lifetime_authority == "neutral_buffer_seam"`, and requires the carrier scope/origin labels — and `tests/goal2879_…provenance_test.py` enforces all of it, including that Numba uses a `cuda_array_interface_descriptor` (not the torch carrier) while Triton uses `cuda_array_interface_to_torch_carrier`.

This makes it machine-impossible for the carrier to *present itself* as the origin of transfer/copy/lifetime authority — a genuine improvement over the Goal2868 state, and exactly the kind of enforcing test I asked for. The honest residual, disclosed in both the report and the closure map: the carrier still **exists**; it was demoted, not removed. It remains a release-watch item.

### F2 — The provenance guard checks metadata/contract, not runtime dataflow (low; required before release)
`validate_v2_5_hit_stream_neutral_seam_authority` validates the carrier's *description* — that its metadata contains no forbidden authority fields and that its scope/origin labels are correct. It does not, by itself, prove that at execution time the actual buffers' copy and lifetime decisions are taken by seam calls rather than by the carrier path. This is the same contract-vs-runtime gap class as Goal2868 F5. For internal readiness this governance check is sufficient and appropriate; before a release review, the carrier should either be removed or backed by a runtime-level assertion/trace showing copy/lifetime transitions originate from the neutral seam, not only that the labels say so.

### F3 — Closure map's F4/F5 closures rest on out-of-range evidence (low; scope clarity)
The Goal2878 map is honest and well-qualified: F1 is marked "**partially closed for internal readiness … still a release-watch item**," F2 "closed as wording/metadata guard … intentionally not a parity or release claim," F4 "closed for preview-runtime conformance **bookkeeping** … keeps release conformance false," F5 "closed for the **current high-risk** Triton preview rows … broader future kernels must add the same smoke." None of these overclaim. The caveat is that F4/F5 substance lives in Goals2872–2876, which this review did not fully audit (Goal2877's lane). I spot-confirmed the supporting evidence is real and honestly bounded — Goal2873's matrix explicitly reports `release_conformance_complete: false` and keeps CuPy descriptor-only except the event-ordered hit-stream preview; Goal2872's tie-break smoke covers `grouped_argmin_f64`/`grouped_argmax_f64`/`grouped_topk_f64` with documented tie-breaks and is explicitly "not the complete per-partner conformance matrix." So the closures are accurately scoped, but Goal2881 accepting them is acceptance of the **mapping's honesty**, not independent re-certification of the conformance substance.

### F4 — "7/7 pass" parity over-read risk persists, but is correctly guarded (low; watch)
The Goal2880 packet (`goal2855_summary.json`) is a genuine post-provenance refresh: `all_pass: true`, 7 artifacts all `status: pass`, clean `source_commit 613f11e0…` (the Goal2879 pod-validation commit, so the refresh is correctly *after* the provenance change), `source_dirty: []`, and `claim_boundary_violations: {}` per app. As in Goal2868, "7/7 pass" means the canonical harnesses execute and respect their claim boundaries — **not** Tier A/B parity. The closure map closes this as a wording guard (its F2), and the readiness packet keeps all speedup/release flags false, so the mitigation is in place. No new defect; restate the watch that no readiness index quote "7/7" as parity.

### Positive confirmations
- **All nine redline blocks intact after this range's edits.** `V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS` still lists `v2_5_release`, `public_speedup_wording`, broad-RT, whole-app, `true_zero_copy_wording`, `package_install_wording`, `triton_preview_auto_selection`, and `native_app_specific_engine_logic`, with matching `*_authorized: False`. The range only **tightened**: it added required-report presence for the Goal2879/Goal2880 reports and a `keep_goal2879_torch_carrier_seam_authority_provenance_green` next-action. No block was weakened.
- **Numba does not use the torch carrier** (descriptor-only), consistent with its declared fallback role — so the carrier is Triton-launch-specific, not a general partner path.
- **The closure map is explicitly historical and non-authoritative**, defers the active conformance review to Goal2877, and restates the full release block.
- **App-agnostic boundary held**: nothing in this range introduces app-specific engine vocabulary; the work is seam-provenance metadata, readiness bookkeeping, and a packet refresh.

## Answers to the three audit questions
1. **Is the Goal2868 residual-closure map correct?** Yes — each residual is mapped with an honest, appropriately-hedged status (partially-closed/wording-guard/bookkeeping/high-risk-only), it does not overclaim, and it defers conformance substance to Goal2877.
2. **Is the torch-carrier seam-authority provenance hardening correct?** Yes — it is real, code-backed, and test-enforced; it removes the authority-looking field, labels carrier scope/origin, and machine-checks that the carrier cannot present itself as the authority origin. The honest residual (carrier exists, demoted not removed) is disclosed.
3. **Is the fresh Goal2880 seven-app packet correct?** Yes — green, 7/7, clean post-provenance commit, empty claim-boundary violations, with parity over-read correctly guarded and release flags false.

## Required fixes before a future v2.5 *release* review (not blockers for this internal work)
1. Remove the torch carrier or back the provenance guard with a runtime-level assertion/trace proving copy/lifetime transitions originate from the neutral seam at execution time, not only in metadata labels (F1/F2).
2. Complete the per-partner conformance matrix at release grade in the Goal2877 lane — move CuPy beyond descriptor-only if it is to be a release partner, and flip `release_conformance_complete` only with that evidence (F3).
3. Broaden tie-break/tolerance conformance smoke beyond the three current high-risk rows (`argmin`/`argmax`/`topk`) to every promoted continuation op before any promotion (F3).

## Optional future work (clearly separated from blockers)
- A single canonical (partner × op × backend) conformance artifact that the readiness packet links, so the supported envelope is one testable surface.
- Runtime seam-provenance tracing so the neutral seam's authority is observable in execution, not only asserted in metadata.

## Bottom line

Goals2878–2880 are a coherent, honest continuation of the v2.5 internal-readiness work and are accepted with boundaries. The residual-closure map states the Goal2868 status accurately without overclaiming; the torch-carrier provenance hardening is a real, test-enforced tightening that stops the carrier from presenting itself as the seam authority (while honestly leaving its removal as a release-watch item); and the refreshed seven-app packet is clean at a post-provenance commit with all release/speedup/zero-copy flags false. Nothing here authorizes release, public or RT-core or whole-app speedup, true zero-copy, automatic Triton selection, package install, or app-specific native engine logic, and all nine blocks remain intact. Final v2.5 release stays blocked pending an explicit user-requested release packet and a fresh 3-AI release consensus. **Verdict: accept-with-boundary.**
