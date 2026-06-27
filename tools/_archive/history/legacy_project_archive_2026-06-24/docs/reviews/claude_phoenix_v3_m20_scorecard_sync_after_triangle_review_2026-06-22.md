I have read all supporting documents. Here is the external critical review.

---

# External Critical Review: Phoenix V3 M20 Scorecard Sync After Triangle

**Date:** 2026-06-23
**Reviewer role:** External critical reviewer (not a member of the production team)
**Scope:** Next-gate verdict after M19 Triangle closed the third strict Set-A material probe and the Set-A/Set-B scorecard was synced to 3/2 focused probes. This is not a release review, not an all-app POD run authorization, and not a public-wording authorization.

---

## Verdict

```
authorize_m20_all_app_protocol_preparation_no_run
```

---

## Explicit Authorization Answers

| Question | Answer |
|---|---|
| Release authorization | **No** |
| Public speedup authorization | **No** |
| Broad V3-over-V2 authorization | **No** |
| All-app POD run authorization now | **No** |
| All-app POD protocol preparation authorization now | **Yes — preparation only; run is a separate gate** |
| Triangle remains closed as the third strict Set-A probe | **Yes** |

---

## Basis for This Verdict

### The focused-probe precondition is genuinely met

The scorecard gate pre-registered `required_focused_productized_material_probe_count_before_full_all_app_pod_run: 2`. Three probes are now verified with artifact paths confirmed to exist:

- `aabb_runner_m2_1` — `material_focused_productized_path_probe_not_release`
- `hausdorff_threshold_runner_m5_after_m6_1` — `positive_focused_productized_runner_backed_probe_not_release`
- `triangle_m19_env_corrected_productized_runner` — `accepted_third_strict_set_a_material_probe_not_release`

The precondition is closed at 3/2 with margin. This was the agreed trigger for beginning protocol preparation review. Not using that trigger is not a conservative stance; it is indefinite delay against a pre-registered gate.

### Protocol preparation costs nothing and buys fail-closed discipline

Protocol preparation is not POD spend. It produces a document that pre-registers per-metric bars before any run happens. That document then needs its own independent 2-AI external authorization before any run starts. This is precisely the discipline that prevented premature POD spend throughout M11–M18. Applying it again here is correct.

### The frozen scorecard blockers have candidate focused fixes, but transfer is unverified

Both blocking items have been addressed in focused runs:

- **Barnes-Hut severe regression (0.844x, below 0.90x floor):** The focused symbol-cache fix recovered individual Barnes-Hut OptiX losses from 0.622x–0.591x to 0.999x–1.038x in the focused same-pod run. M7 intake projects app geomean recovery to ~1.009x. However, focused runs do not confirm all-app transfer.
- **LibRTS Embree AABB index Set-B row (0.869x, below 0.95x floor):** The AABB count-packing cache fix recovered the Embree count-only regression in focused repeat=3 and repeat=9 runs. The Set-B blocking row is exactly this one (`librts_embree_aabb_index`).

The open question — whether both fixes hold under the full all-app paired-run context — is precisely what an all-app run is designed to answer. Protocol preparation forces that question to be answered against pre-committed bars rather than after-the-fact rationalization.

### The M8 planning projection gap must be named explicitly

This is the most important number in this packet: even if **both** focused fixes transfer fully to the all-app setting, the M8 projection gives:

```
all-row geomean:  1.048x   (release threshold: 1.20x)
Set-A geomean:    1.039x   (release threshold: 1.20x)
Set-A apps >1.05x: 1 / 6   (release threshold: ~5 / 6)
```

The current score of 1/6 apps over 1.05x compared to a required ~5/6 makes the M8-projected outcome a non-release candidate by a large margin, not a borderline case. Protocol preparation must be approved with the team's explicit understanding that the all-app run, even in the best case, will not pass the release bar. If the expectation behind authorizing protocol preparation is that it opens a path to release through this run, that expectation is not supported by the evidence and this verdict does not authorize it.

---

## What the All-App Protocol Must Include

The protocol packet that emerges from M20 must contain every item below before it may be submitted for 2-AI authorization:

**1. Pre-registered per-metric fail-closed bars (hard thresholds, no interpretation latitude)**

| Bar | Fail condition | Basis |
|---|---|---|
| Barnes-Hut app geomean | < 0.90x → protocol FAIL | frozen Set-A severe-regression floor |
| `librts_embree_aabb_index` row | < 0.95x → protocol FAIL | frozen Set-B row floor |
| Set-A geomean | documented; not a pass/fail threshold for this run | no release expectation |
| Set-A apps over 1.05x | documented; not a pass/fail threshold for this run | no release expectation |
| Set-B geomean | < 0.98x → protocol FAIL | frozen Set-B geomean floor |
| Any new app-level severe regression below 0.90x | → protocol FAIL | no new regressions accepted |

The "documented but not a pass/fail threshold" entries exist because the planning projection already shows these will not pass the release bar. Pre-registering them as "pass/fail" would create a false gate. They must still be reported as exact numbers.

**2. Explicit non-release declaration in the protocol header**

The protocol document must state in its frontmatter that no outcome of the run, including full clearance of both blocking items, constitutes release authorization. This is required because the M8 projection leaves Set-A geomean and app-win counts far below release thresholds regardless of how the two focused fixes perform.

**3. Frozen case-ID whitelist preserved**

Every scored case_id must match the whitelist frozen in `phoenix_v3_set_a_set_b_classification_2026-06-22.json`. No new case_ids or new apps may be added without a separate preregistration review; unrecognized case_ids must cause the run to be declared out-of-scope.

**4. Same hardware requirement**

NVIDIA RTX 4000 Ada Generation, driver 550.127.05, compute capability 8.9. This matches the hardware used for the serious paired run that produced the frozen scorecard. A different GPU requires a new hardware-gate review before the protocol may proceed.

**5. Run infrastructure must match the verified M19 venv pattern**

The M18/M19 experience proved that a wrong interpreter (`/usr/bin/python3` vs project venv) produces a silent coverage failure. The protocol must require:
- Project venv interpreter (`/root/rtdl_v3_rebuild_20260620/.venv/bin/python` or equivalent verified path)
- Pre-launch subprocess interpreter check confirming `sys.executable` is the venv binary
- Fail-closed if the pre-launch check fails

**6. LibRTS OptiX AABB watch-row status must be disclosed**

The protocol must note that `librts_optix_aabb_index` (currently 1.010x in the frozen scorecard) was classified as unstable/inconclusive in focused work. It is not the current Set-B blocking row and is not a fail bar for this run, but any regression below 0.95x in this row in the all-app result must be flagged and reported without rationalization.

**7. Oracle/correctness checks for all apps**

Equivalent to the M17/M18/M19 standard: every app must produce a correctness signal matching the expected V2.14 output before performance numbers are accepted. A correctness failure for any app invalidates that app's performance rows.

**8. Post-run result handling pre-declared**

The protocol must state: if all-app result clears both blocking bars (Barnes-Hut ≥ 0.90x and LibRTS Embree AABB ≥ 0.95x), the verdict is "blocking bars cleared, run advances the scorecard baseline, release is still not authorized." If either blocking bar is not cleared, the verdict is "protocol fail, further local/focused work required before another all-app run."

---

## What Still Blocks Running the All-App POD

The following must all be complete before any all-app POD run:

1. **The M20 protocol packet does not yet exist.** This verdict authorizes preparing it, not running POD.
2. **The protocol packet requires its own 2-AI external review and authorization.** The M20 verdict here does not substitute for that review.
3. **Barnes-Hut and LibRTS Embree AABB focused fixes have not been confirmed in an all-app context.** The protocol run is the mechanism for that confirmation.
4. **LibRTS OptiX AABB focused behavior is unstable/inconclusive.** It is not the current Set-B blocking row and is not a run blocker, but it is a disclosed risk that may surface in the all-app results.
5. **Even best-case outcome does not approach release.** The run is an evidence run, not a release gate. If the team does not accept this, the protocol should not be written.

---

## What This Verdict Does Not Authorize

```
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_run_authorized_now: false
release_based_on_all_app_run_outcome: false
m19_citable_as_broad_v3_performance: false
```

---

## Why This Is Not a Deny

The deny path (`deny_m20_all_app_protocol_prepare_fix_blockers_first`) would require naming specific local/focused work that must be done before protocol preparation. The named candidates from the packet are:

- **Barnes-Hut Set-A severe regression:** A focused fix already exists and projects recovery. Additional focused Barnes-Hut work before protocol preparation has no defined stopping criterion. The focused evidence is as good as it can be without an all-app validation.
- **LibRTS Set-B Embree AABB parity row:** The focused fix exists and was verified in focused runs. The LibRTS OptiX AABB is unstable but is not the current Set-B blocking row.

More focused work on these two items would likely produce more focused evidence for the same fixes that already exist. It would not resolve the transfer question. Only an all-app run resolves that, and the only responsible way to run all-app is with a pre-registered fail-closed protocol — which is exactly what M20 authorizes preparing.

The deny verdict would be correct if there were identified local engineering changes that were likely to materially shift the scorecard expectations beyond the M8 projection. No such changes are identified in the current packet or the M9–M19 history. Denying without a named corrective path is delay, not discipline.

---

## Risks and Constraints the Team Must Acknowledge Before Writing the Protocol

1. **The all-app run will almost certainly produce a scorecard that still fails the release bar by a large margin.** This is not a reason to cancel the run; it is a reason to ensure the protocol is honest about expected outcome ranges.
2. **The classification is frozen.** Any attempt to update case-ID whitelists, reclassify apps, or add new rows before or during the run requires a separate external review.
3. **The protocol must not recycle M8 projections as run success bars.** The M8 projections (1.039x Set-A geomean, 1/5 apps) are planning estimates, not pre-registered thresholds. The protocol must pre-register actual measured thresholds, and those thresholds must be grounded in the frozen scorecard floors, not in the most optimistic projection.
4. **The Codex position ("maybe, if external review agrees") correctly named both blockers as residual risks.** This verdict accepts that risk for the purpose of protocol preparation only. If the protocol document, when written, reveals new blockers not visible from the current packet, a separate review is required before run authorization.

---

## Next Concrete Packet

```
M20 all-app POD protocol packet
  - All items under "What the All-App Protocol Must Include" above
  - Submitted for 2-AI external review and authorization
  - No run until that review returns an authorization verdict
```
