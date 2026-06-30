# Goal4309: Claude Review — Goal4301–Goal4308 Fable5 Action Packet

**Reviewer:** Claude (Sonnet 4.6, read-only external follow-up)
**Date:** 2026-06-11
**Scope:** Goal4301–Goal4308 action packet taken after the Fable5 whole-project review
(Goal4302). This is a focused follow-up review, not a new whole-project review and not a
release review.
**Requested by:** External review request attached to handoff for Goal4301–Goal4308.

---

## Verdict: `accept-with-boundary`

All six goals in this packet are coherent, correctly bounded, and materially address the
highest-priority Fable5 findings that are safe and high-leverage to act on without a pod
run: F1 security (Goal4303), F5 RT-core honesty (Goal4305), F3 first contract-layer slice
(Goal4306), F8 learner onboarding (Goal4307), F7 RTNN Embree exception (Goal4308), and the
P3 Numba top-k debt (Goal4301). Claim boundaries are consistently false-closed and the test
suite is coherent with the code changes.

The boundary is fivefold. First, the most acute open Fable5 item — F6/P5 (1-second
aggregate timing floor) — is not addressed in this packet; the main ten-app evidence packet
still mixes floor-respecting rows with sub-floor rows without per-row tagging. Second, the
historical archive outside the current goal42xx/goal43xx surface is not yet scanned by the
security guard, and JSON artifacts are not covered by the current redaction test. Third, the
`partner_adapters.py` monolith has only one contract family (grouped topk) on the new shared
layer; the full adapter split and the six remaining partner-column families remain open
Fable5 P2 debt. Fourth, the kernel-DSL bridge pilot (F2/P4) that decides the language
identity has not been started. Fifth, the F4/P9 archive-curation and P10 boundary-prose
deduplication items have not been started.

Nothing in this review authorizes a release, public speedup wording, package-install
wording, true-zero-copy wording, broad RT-core wording, automatic partner selection, or
paper-reproduction claims.

---

## Findings (ordered by severity)

### F-R1 — MEDIUM: 1-second aggregate timing floor not yet applied to main packet

The most acute remaining Fable5 item (P5/F6) is not addressed in this packet and should be
the next pod goal. The current ten-app scale-profile packet mixes floor-respecting rows with
sub-millisecond medians (contact_manifold at 0.29 ms, RTNN at 0.21 ms, robot_collision at
40.9 µs) without per-row `smoke_scale_only` tagging. Any internal planning that reads those
rows as performance evidence is doing so with a known caveat. This does not block the
packet's other goals, but it is the highest-leverage remaining action that depends on pod
access.

### F-R2 — MEDIUM: Security guard covers .md files only; JSON artifacts not scanned

The `goal4303_current_security_redaction_guard_test.py` scans markdown files in
`docs/reports/`, `docs/handoff/`, and `docs/reviews/` for the goal42xx/goal43xx prefix. JSON
artifacts in `docs/reports/` are not scanned. The `goal4301_v2_11_rtnn_numba_device_topk_runner_local_linux.json`
and `goal4308_rtnn_embree_front_door_local_linux.json` artifacts contain
`"platform": "Linux-..."` and `"executable": "/usr/bin/python3"` metadata but no IP
addresses or key material; in the current artifacts, the gap is not exploited. However, the
test boundary should be documented as intentional, since pod driver stdout captures can
include connection output from prior invocations. The Goal4303 report already states the
historical archive is not covered; this note extends the same honesty to JSON artifacts.

### F-R3 — MEDIUM: Historical archive (pre-goal42xx) outside the redaction guard scope

Goal4303 explicitly documents this: "The broader historical archive still needs a planned
redaction/archive pass." This is honest. The guard at `goal4303_current_security_redaction_guard_test.py`
patterns only match `goal42*.md` and `goal43*.md` prefixes. Any pre-v2.10 report files
containing the same live-pod patterns are not scanned. The F1 risk is mitigated for
external distribution of the current surface; the historical tree risk remains open and
correctly tracked. No action is required in this packet; it should be a named item in P9.

### F-R4 — LOW: `pyproject.toml` version is 2.10.0 while active lane is v2.11

`pyproject.toml:7` declares `version = "2.10.0"`. The active development lane is v2.11 and
most evidence reports carry the `v2_11` label. A user who installs the editable package and
then reads runner artifacts labeled `rtdl.v2_11.current_embree_cpu_partner_reference.goal4308.v1`
will see a mismatch. This is a cosmetic inconsistency; it does not affect claim boundaries
or runtime behavior. Worth updating when the version identifier is next revisited. No claim
boundary implication.

### F-R5 — LOW: Tutorial hardcodes local Windows path

`tutorials/current/01_source_tree_first_run.md:20` contains
`cd C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`. This is a local filesystem
path that will not work for any other user or environment. The test in `goal4307_editable_source_tree_onboarding_test.py`
checks for the presence of `python -m pip install -e .` but does not verify that the path
used in the tutorial example is portable. This should be replaced with a generic placeholder
such as `cd /path/to/rtdl_v0_4_release_prep_review` or the repository root alias. Not a
claim boundary issue; minor usability problem.

### F-R6 — LOW: `optix_performance` field present in Embree-mode RTNN output

The `goal4308_rtnn_embree_front_door_local_linux.json` stdout capture includes an
`"optix_performance"` key in the Embree-mode output JSON. The note inside that key correctly
explains it, but the field name creates a surface impression that OptiX performance is being
measured in the Embree front door. This is harmless for internal review (the field content
is a documentation note, not a metric) but could confuse a future reviewer who reads the key
name without the note content. Consider renaming to `optix_path_note` or `rt_path_note` in
a future cleanup pass.

---

## Per-Goal Findings

### Goal4303: Security and Top-K Intake

**Question 1 — Did Goal4303 materially address Fable5 F1 for the current active tree?**

Yes, materially and honestly. The four required actions are all present and verified:

- `.gitignore` hardened: `id_ed25519*`, `*.pem`, `*.ppk`, `*.key`, `/Lib/`, `/before_*.txt`,
  `/rtdl_v0_4.tar.gz` are all present in the current `.gitignore`. The rules are specific
  enough that a `git add -A` would not commit the named key patterns.
- Root debris moved: test at line 36–38 of `goal4303_current_security_redaction_guard_test.py`
  asserts that `before_3958.txt`, `rtdl_v0_4.tar.gz`, and `Lib/` no longer exist in the
  repository root. The test passes.
- Current-goal redaction guard added: `goal4303_current_security_redaction_guard_test.py`
  scans 196 current goal42xx/goal43xx markdown files for five categories of live access
  detail. The report states zero violations and the test structure confirms each of the five
  patterns is checked.
- Current-goal review file itself redacted: the review file no longer repeats the private-key
  header, working-key filename, or live SSH command that Fable5 cited. Confirmed by grep
  above (no matches for live root SSH command strings, key header patterns, or old
  working-key filenames in the current report and handoff surface).

**Question 2 — Is the security scope honest?**

Yes. Goal4303 explicitly states: "The new guard checks...It deliberately targets the current
goal42xx/goal43xx surface; the broader historical archive still needs a planned
redaction/archive pass." The report additionally names the five still-open Fable5 items
and links to the follow-up goals. The scope boundary is precise and forward-looking.

One gap not explicitly documented in Goal4303: JSON artifacts in `docs/reports/` are not
covered by the `.md` guard (see F-R2). This is worth documenting as a named scope limit
alongside the historical archive caveat.

### Goal4301: Numba Grouped Top-K Device Rank

**Question 3 — Did Goal4301 correctly implement generic `grouped_topk_f64` without host-rank
materialization and without app-specific runtime vocabulary?**

Yes. The implementation is correctly scoped:

- The primitive name, inputs, and outputs are generic: `(group_id, item_id, score)` →
  `(group_id, item_id, score, rank, row_offsets)`. No RTNN/ANN vocabulary appears in the
  kernel or runner.
- `host_rank_materialization_used: false` is confirmed in both the fresh scaled artifact
  (`goal4301_ann_candidate_numba_device_topk_copies128_local_linux.json`) and the runner
  artifact (`goal4301_v2_11_rtnn_numba_device_topk_runner_local_linux.json`).
- The layout precondition `equal_contiguous_group_segments` is documented, enforced on-device
  with an error flag, and surfaced in the descriptor return value.
- The `k <= 16` preview limit is documented in the report ("Remaining Work") and does not
  affect the RTNN/ANN quality reference use case (k=1 in the current first consumer).
- Tie-break policy (lowest score then lowest item_id) and one-based rank emission are stated
  explicitly and the unit test (`test_numba_grouped_topk_matches_contract_when_cuda_available`)
  verifies them against a hand-constructed 6-row fixture.
- All claim flags in the adapter metadata are false (`rt_core_speedup_claim_authorized: false`,
  `whole_app_speedup_claim_authorized: false`, etc.). Confirmed from both the JSON artifact
  and the test at lines 132–134 of `goal4301_numba_grouped_topk_device_rank_test.py`.

One remaining precision note: the runner artifact at `goal4301_v2_11_rtnn_numba_device_topk_runner_local_linux.json`
carries `"route_class": "numba_cpu_partner_reference_no_embree_front_door"` and
`"version": "rtdl.v2_11.current_embree_cpu_partner_reference.goal4298.v1"`. This is
expected — Goal4301 ran the Numba quality reference row, which is a separate lane from the
Embree front door corrected by Goal4308. The two lanes are distinct and both correct; the
version label on the runner artifact reflects Goal4298 (when the runner was created) rather
than Goal4301. This is not a defect but could confuse a reviewer who reads the artifact
in isolation.

### Goal4306: Partner-Column Contracts Foundation

**Question 4 — Did Goal4306 make partner-column contracts explicit enough to close the first
Fable5 P2 slice, while honestly leaving the full `partner_adapters.py` split open?**

Yes on both counts. `partner_column_contracts.py` is well-designed:

- `RtdlGroupIdContract` is a frozen dataclass with an explicit `layout` field; three layout
  constants are defined and documented.
- `RtdlPartnerClaimBoundary` is false-by-default on all ten claim flags; `validate_partner_claim_boundary`
  rejects any true value with a named error.
- `require_group_id_contract` raises `ValueError` with specific error text rather than
  silently returning partial metadata.
- The shared contract is wired into `run_numba_grouped_topk_f64` (confirmed in
  `goal4306_partner_column_contracts_foundation_test.py` lines 63–69).

The Goal4306 report's "Remaining Work" section explicitly names six contract families not yet
on the layer: grouped sum/min/max/count, row-offset grouped reductions, pairwise score-row
producers, fixed-radius partner outputs, and route-level claim-boundary metadata. This is
honest. The test suite does not overstate coverage — it checks the Numba top-k integration
and the contract type behavior, not the broader adapter module.

The only design note: the `validate_partner_claim_boundary` function validates against a
single metadata dict rather than taking an `RtdlPartnerClaimBoundary` instance directly.
This is workable but means callers could bypass the dataclass default logic by constructing
a dict manually. For the current use case (emitting metadata from the runner) this is
acceptable. Future users of the layer should prefer `RtdlPartnerClaimBoundary().to_metadata()`
as the canonical construction path.

### Goal4305: RT-Core Honesty Matrix and Goal Tier Protocol

**Question 5 — Does Goal4305 classify RT-core evidence conservatively enough, including the
ten-app-packet framing sentence?**

Yes. The key sentence — "the ten-app packet is not ten broad RT-core speedup claims" — is
present in `rt_core_evidence_matrix.md:8` and confirmed verified by the guard test
(`goal4305_fable5_evidence_and_process_docs_test.py:16–17`). The matrix classifies all ten
apps and explicitly labels Barnes-Hut as "Partner-led evidence" without an RT-core win
claim. The "Blocked wording" section is explicit: "RTDL accelerates all ten benchmark apps
on RT cores" is listed as blocked.

The checklist ("Before using a benchmark row as performance evidence") is a useful operational
guard — it requires eight named fields before a row qualifies as performance evidence. This
is more specific than the prior state.

One minor precision point: the matrix column headers say "Current evidence class" but the
body uses more nuanced labels than the column names suggest (e.g., "Strong contract-split RT
evidence," "Strong RT evidence with partner reference sidecar"). The header says "Mixed RT
evidence" but the body uses it differently per row. This inconsistency is internal to a
learner-facing doc and does not create a claim boundary risk, but it slightly undermines
the consistency promise of the matrix. Worth normalizing to the three or four column-level
labels in a future revision.

The goal tier protocol (`goal_tier_protocol.md`) correctly preserves all non-negotiable
boundaries (native-engine app-agnosticism, blocked package-install wording, blocked broad
speedup wording, blocked true-zero-copy wording, blocked automatic partner selection) while
reducing ceremony for Tier A hygiene goals. The examples table — which classifies Goal4303
as Tier A and Goal4301 as Tier B — is accurate. The omission of Goal4305 itself from the
examples table is acceptable (it is documenting the protocol, not a new runtime change).

### Goal4307: Editable Source-Tree Onboarding

**Question 6 — Does Goal4307 improve source-tree onboarding without creating a
package-install claim?**

Yes, and the boundary is correctly enforced at multiple layers:

- `pyproject.toml` uses `name = "rtdl-source-tree"` (not `rtdl` or `rtdsl`), explicitly
  signaling this is a local development install.
- The dry-run artifact confirms: `Would install rtdl-source-tree-2.10.0` — PyPI registry
  is not involved.
- `README.md` contains: "It is not a PyPI, wheel, or package-install support claim."
- `docs/learn/source_tree_doctor.md` contains the same boundary.
- The test (`goal4307_editable_source_tree_onboarding_test.py`) checks for the three
  specific boundary phrases at lines 42–49.

The doctor integration (reporting editable metadata as an optional, non-required check) is
the right engineering choice: a user who skips the editable install still has a working
`PYTHONPATH=src:.` path, and the doctor does not penalize them.

See F-R4 (version mismatch) and F-R5 (local path in tutorial) for two minor usability gaps
that do not affect claim boundaries.

### Goal4308: RTNN Embree Front Door

**Question 7 — Does Goal4308 remove the RTNN Embree packet special case honestly, without
pretending the 2-D ANN candidate-quality mode is full 3-D RTNN paper reproduction or NVIDIA
RT-core evidence?**

Yes, precisely. The removal is complete and the boundary wording is unambiguous:

- The validator in `current_embree_cpu_partner_reference.py:425–426` now unconditionally
  requires `uses_embree: True` for every benchmark row, including RTNN. No app-specific
  exception branch remains. The test (`goal4308_rtnn_embree_front_door_test.py:25–26`)
  confirms `validation["status"] == "accept"` and `validation["errors"] == ()` on the
  updated registry.
- The RTNN row's `route_class` is `embree_cpu_rt_plus_python_continuation` — not the
  previous `numba_cpu_partner_reference_no_embree_front_door`.
- The app's `ann_embree_quality` mode boundary string is: "Embree CPU front door for the
  2-D ANN candidate-quality contract. This removes the RTNN Embree-packet special case, but
  it is not the 3-D RTNN ranked-summary path and not full RTNN paper reproduction." The test
  at line 38 confirms `"not the 3-D RTNN ranked-summary path"` is in the payload boundary.
- `rt_core_accelerated: false`, `paper_reproduction_claim_authorized: false`,
  `rt_core_speedup_claim_authorized: false` are all confirmed in the artifact stdout.

The `optix_performance` field issue (F-R6) is the only precision concern; it does not affect
claim boundaries.

One structural point worth noting: the new RTNN Embree mode wraps the `native_knn_rerank_summary`
backend, which the artifact stdout identifies as `"native_continuation_active": true`. This
means the Embree CPU library is genuinely called in the hot path, not bypassed by Python
continuation. This is correct behavior for an Embree front door.

---

## Question 8: Recommended Priority Order for Remaining Fable5 Items

Based on this review, the recommended order for the next phase:

1. **P5/F6 — 1-second timing floor packet** (next pod goal, highest evidence-integrity
   leverage). Apply goal4266-style repeat calibration to the main ten-app scale runner.
   Every row either exceeds the 1.25 s aggregate floor on its key signal or is tagged
   `smoke_scale_only`. Rerun the packet on an NVIDIA pod. This is the most direct remaining
   gap between current evidence and decision-grade reads.

2. **P2/F3 — Next partner-adapter split slice** (next local goal after timing floor).
   Migrate the grouped-sum/count/min/max family onto `RtdlGroupIdContract` and
   `RtdlPartnerClaimBoundary`. This is incremental, low-risk, and feeds the foundation
   established by Goal4306. Keep each contract family app-agnostic and tested before moving
   on.

3. **P9/F4 — Archive and report curation** (can be parallelized with item 2 since it
   requires no pod access). Move pre-v2.10 reports from the active tree into `history/` or
   an archive branch with a tombstone index. Remove the 12 goal-numbered modules from
   `src/rtdsl/`. This has the highest noise-reduction value for reviewers and contributors.

4. **P10/F8 — Boundary-prose deduplication** (quick win, no hardware). One canonical
   boundary page; replace repeated paragraphs in README and tutorials with one-line links.
   Low risk, significant readability improvement.

5. **P4/F2 — Kernel-DSL bridge pilot** (strategic decision, expensive). Lower two contracts
   through `@rt.kernel` to the same prepared native routes the benchmarks use. This is
   the decisive experiment for the language-vs-catalog identity question. It should not
   block items 1–4 and requires 3-AI consensus before the design is settled.

6. **P11 — Whole-app declared mid-scale measurement** (after timing floor is established).
   Once P5 sets the repeat policy, apply it to one declared whole-app measurement on
   `spatial_rayjoin` overlay/LSI at a public-CDB representative scale against the same-contract
   CPU/CUDA baseline. This is the template for future narrow public wording.

Boundary archive curation (P9) and boundary-prose deduplication (P10) can proceed on any
local branch without blocking pod work.

---

## Blocked Claims (unchanged from Goal4302 and re-blocked here)

This review re-blocks all claims blocked in Goal4302. Specifically:

- No release authorization, no tag, no publish action.
- No package-install or `pip install rtdl` wording.
- No broad speedup, "makes your app faster", or whole-application acceleration wording for
  the ten benchmark apps as a set (the set contains partner-led and sub-floor rows).
- No broad NVIDIA RT-core wording. No AMD or Intel GPU performance wording.
- No true-zero-copy or general device-residency wording.
- No paper-reproduction wording for RTNN, RayJoin, X-HD, LibRTS, RT-DBSCAN, or the triangle-
  counting target.
- No automatic partner selection or "RTDL accelerates CuPy/Numba programs" wording.
- No "easier than CUDA/OptiX for arbitrary RT programs" wording until the F2/P4 gap is
  resolved.

---

## Summary Table

| Goal | Finding | Verdict |
| --- | --- | --- |
| Goal4303 (security + intake) | F1 materially addressed for current surface; historical archive and JSON artifacts remain outside guard scope (honestly documented) | accept-with-boundary |
| Goal4301 (Numba device top-k) | Generic, device-resident, precondition-enforced; `k<=16` limit documented; runner artifact version label carries Goal4298 tag (expected, not a defect) | accept-with-boundary |
| Goal4305 (RT-core matrix + tier protocol) | Conservative classification; ten-app-is-not-ten-speedup sentence present; tier protocol preserves all non-negotiable boundaries; matrix label inconsistency is minor | accept-with-boundary |
| Goal4306 (partner-column contracts first slice) | Shared contract layer is correct; false-by-default boundary; wired into Numba top-k; six remaining families explicitly noted as open | accept-with-boundary |
| Goal4307 (editable onboarding) | Boundary preserved at all three doc layers; local path in tutorial and version mismatch are usability gaps only | accept-with-boundary |
| Goal4308 (RTNN Embree front door) | Exception removed; validator universally requires Embree; boundary wording is precise; `optix_performance` field name is minor cosmetic gap | accept-with-boundary |

---

*Review boundaries respected: no release authorization, no consensus file, no tags created
or moved, no public speedup/zero-copy/package-install/paper-reproduction claims made, no
source/test/doc changes. Read-only review.*
