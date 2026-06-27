# Phoenix V3 Post-M22 Step Alignment And Next Work

Date: 2026-06-23

Status: `post_m22_alignment_not_release_not_all_app_authorized`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
```

## Purpose

This file reconciles the Claude trunk-first sequence with the current Phoenix
V3 evidence after M22. It separates two facts that must not be merged:

1. focused runtime-trunk probes have made real progress;
2. the serious same-RT-hardware all-app V2.14/current comparison still failed
   the release bar.

## Step Status

| Step | Current status | Evidence | Release meaning |
| --- | --- | --- | --- |
| Step 0: stop and freeze | Mostly complete | Set-A/Set-B scorecard exists; all-app is frozen after M22; cache/symbol-cache work is not the main line | No release |
| Step 1: build trunk | Partly complete | `prepared_execution_session_runner` exists and records `runtime_executed=true`; multiple focused routes execute through it | No release |
| Step 2: generalize | Partly complete, needs post-M22 reconciliation | RTDBSCAN/RayJoin execute but are not material; Hausdorff/RTNN/Triangle have positive focused evidence with boundaries | No release |
| Step 3: residency default | Partly complete, not universal | M31 adds a shared audit gate and wires it through RTNN, Triangle, Barnes-Hut, RTDBSCAN M3.4, RayJoin, and Hausdorff focused packets; segment-intersection also has a core-helper audit assertion; remaining helpers still need inventory/enforcement | No release |
| Step 4: continuation core | Partly complete, not externally reviewed | M32 adds `audit_prepared_execution_continuation_metadata()` and asserts continuation-core readiness for seven generic families; M33 classifies all 11 prepared-session helpers as seven local-audit-ready families, one blocked Set-A seed, and three blocked Set-B controls | No release |
| Step 5: all-app | Blocked | M22 all-app failed: overall 1.049x, Set-A 1.013x, 4/10 apps over 1.05x | Do not rerun yet |
| Step 6: external review + release decision | Not reached | M22 verdict is `approve_blocked_not_release` | Release remains blocked |

## Focused Runtime-Trunk Evidence

| Family | Current classification | Key facts | Boundary |
| --- | --- | --- | --- |
| Barnes-Hut aggregate-tree fused vector sum | valid Step-1 trunk/capability evidence, not same-contract V2.14 speedup | runner path carries fused route at parity; internal residency true; M31 audit gate wired | M29 classified V2.14/current surfaces as not same contract |
| RTDBSCAN component signature | structural success, not material | runner vs legacy M3.4 geomean 0.9976x; M31 audit gate wired | stop as immediate material-probe path |
| RayJoin point-location topology stream | structural success, not material | runner executes; total-repeat vs incumbent 0.9738x; M31 audit gate wired for future rerun packets | do not count as material |
| Hausdorff threshold runner | positive focused evidence, M31-audited for future packets | runner vs legacy wrapper wall 1.0541x; runner vs Embree wrapper wall 1.5378x; two directed legs now audit through the shared Step-3 helper | weak positive; not broad app speedup |
| RTNN ranked summary repeat50 | M30 candidate, pending current Claude review | runner vs legacy cold-plus-query 1.3583x; runner wall 1.3702x; hot query 0.9888x; M31 audit gate wired | repeat50 prepared-session only; no single-shot claim |
| Triangle weighted summary device-output stream | accepted focused third strict Set-A probe | runner vs legacy wall 2.1167x; runtime trunk true; internal residency true; M31 audit gate wired | focused K4 clique workload only; not broad Triangle/V3 speedup |

## Why M22 Still Controls Release

M22 is the serious same-RT-hardware all-app comparison and remains the current
release-control result:

```text
overall_geomean_v3_speedup_vs_v2_14: 1.049x
set_a_geomean_v3_speedup_vs_v2_14: 1.013x
apps_above_1_05x: 4_of_10
barnes_hut_app_geomean: 0.831x
verdict: approve_blocked_not_release
```

The focused probes show that the trunk can execute and sometimes produce
material local wins. They do not erase the M22 all-app failure.

## Current Local Matrix Gate

M33 post-audit local validation now includes the full V3 rebuild matrix:

M34 local addendum while awaiting external review: the prepared-session surface
ledger gate checks that every public `prepared_execution.__all__`
prepared-session helper appears in the M33 ledger exactly once. It found and
fixed one drift: `run_fixed_radius_threshold_reached_count_2d_prepared_session`
was in the ledger but missing from `__all__`.

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_session_surface_ledger_gate_test \
  tests.v3_phoenix_m30_m33_review_bundle_gate_test \
  tests.v3_phoenix_prepared_execution_session_runner_test
Ran 39 tests
OK
```

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m30_m33_review_bundle_gate_test \
  tests.v3_phoenix_external_verdict_intake_test \
  tests.v3_release_wording_gate_test
Ran 14 tests
OK
```

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 115
Ran 600 tests in 73.275s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m36_20260623_132320.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m36_20260623_132320.stderr.txt
```

This result says the local contract/gate suite still passes after M31-M36
classification, surface-ledger, focused-gap-ledger, and grouped-reduction
core-node work. It does not
override M22, does not count as external consensus, and does not authorize
release, all-app POD spend, or public performance wording.

## Current External-Review State

Claude external review has now been obtained for M30-M34:

- raw review:
  `docs/reviews/claude_phoenix_v3_m30_m33_bundle_review_2026-06-23.raw.md`
- recorded review:
  `docs/reviews/claude_phoenix_v3_m30_m34_bundle_recorded_review_2026-06-23.md`
- Codex+Claude 2-AI consensus:
  `docs/reviews/codex_claude_phoenix_v3_m30_m34_2ai_consensus_2026-06-23.md`

Verdict:

```text
accept_m30_m33_continue_trunk_first
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
```

Claude accepted M30, M31, M32, M33, and the M34 surface-ledger correction.
Required carry-forward clarification: `Step-4 ready by local audit` means the
metadata structure passes the M31/M32 gate, not that measured material
performance gains exist for all seven families.

Gemini interim review was attempted for M30, M31, M32, M33, the M30-M33 bundle,
and the final M30-M33 bundle on 2026-06-23 and failed at authentication/client
eligibility:

```text
external_verdict_blocked_gemini_auth_ineligible_not_consensus
```

Final blocked record:

- `docs/reviews/external_review_blocked_phoenix_v3_m30_m33_bundle_final_gemini_interim_review_2026-06-23.md`

Therefore Gemini does not count as a review and does not replace Claude.

Antigravity AgentAPI was also checked after user suggestion. It is installed as
a GUI app, but automated `agentapi.bat --help` failed with
`ANTIGRAVITY_LS_ADDRESS is not set`; no Antigravity verdict was obtained:

- `docs/reviews/external_review_blocked_phoenix_v3_antigravity_agentapi_2026-06-23.md`

## Immediate Engineering Direction

Do not run all-app.

Do not spend POD on broad suites.

M35 completed the first item below as a bounded local gap ledger:

- `docs/reports/phoenix_v3_m35_focused_evidence_gap_ledger_2026-06-23.md`
- `docs/reviews/call_for_review_phoenix_v3_m35_focused_gap_ledger_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m35_focused_gap_ledger_recorded_review_2026-06-23.md`
- `docs/reviews/codex_claude_phoenix_v3_m35_focused_gap_ledger_2ai_consensus_2026-06-23.md`
- `tests/v3_phoenix_m35_focused_gap_ledger_test.py`

Claude accepted M35 with verdict `accept_m35_gap_ledger_continue_m36`; the P1
traceability fix about M3.4's AABB recommendation versus the M30-M34
grouped-reduction redirect is applied.

The next non-POD work should now follow the resulting queue:

1. promote grouped vector-sum/reduction into a runner-callable generic
   prepared-session core node; M36 local code/gates now exist and Claude
   accepted the core-node shape;
2. split component-union and component-signature accounting so union-pass cost
   is visible as a core runtime node;
3. extend M31/M32 audit wiring to any prepared-session families added after
   M33/M35;
4. keep all-app blocked until focused Set-A material evidence and Set-B parity
   preconditions are met and externally reviewed.

## Goal-Level Decision Audit

Decision: treat post-M22 focused probe progress as real runtime-trunk evidence,
but keep release/all-app blocked and move next to shared runner audit and
continuation-core work.

1. Was I foolish?

   No for this decision.

2. If yes, what actions made the decision foolish?

   The foolish action would be either discarding all focused probe evidence
   because M22 failed, or promoting focused probes into release claims. This
   file does neither.

3. Was there another path?

   Yes: rerun all-app immediately, keep tuning isolated app rows, or wait idle
   for Claude. All three would repeat prior failure modes.

4. Can I now try a different path that actually solves the problem?

   Yes. Continue trunk-first by hardening shared runner audit/residency and
   moving continuation behavior into runner-callable core nodes before another
   all-app run.
