# External Review - v2.14.4 All Open Review Debt (Consolidated)

Date: 2026-07-06
Reviewer: external review (Claude)

overall_verdict_label: approve_v2_14_4_all_review_debt_retirement

This consolidated review covers every goal in `REVIEW_REQUIRED_GOALS`
(5048, 5049, 5050, 5051, 5052, 5053, 5055, 5056, 5057, 5058, 5059, 5060, 5061,
5062). Each goal report, its call-for-review, the relevant source, the strict
POD smoke JSON, and the release preflight script were inspected directly. The
single blocking finding from the prior review round (BF-1) has been verified as
resolved by Goal5062, so the packet is approved for release-staging review.

## BF-1 Resolution Summary

The prior review raised BF-1: the legacy RayJoin public-export enumeration was
incomplete (four names disclosed) and the preflight gate was hardcoded to that
same undercount. Goal5062 fixes both. A dynamic scan of `rtdsl.__all__` now finds
seventeen RayJoin-named public exports; I independently counted seventeen quoted
rayjoin names in `src/rtdsl/__init__.py` (case-insensitive), matching
`EXPECTED_RAYJOIN_PUBLIC_EXPORTS` exactly with no missing and no unexpected names.
All three boundary reports (Goal5050, Goal5051, Goal5059) now enumerate all
seventeen names. The gate function `check_legacy_rayjoin_public_exports_disclosed`
derives the set dynamically via `_rayjoin_exports_from_init_all` and blocks on any
observed export absent from the reports, so a newly added RayJoin export cannot
silently pass. BF-1 is resolved.

## Goal5048

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The non-rayjoin genericity proof builds a DeviceColumnBuffer
from a ray/triangle hit-stream shape (producer ray_triangle_hit_stream, columns
ray_ids/primitive_ids) and runs a public numba partner continuation binding
values to primitive_ids, proving the public API is not rayjoin-shaped. Legacy
grouped/segmented numba operation values are confirmed outside
NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS and fail closed when routed through
the public wrapper; device_group_by stays absent from rt.__all__. The live CUDA
smoke is skipped locally but is now retired on real POD hardware by Goal5056, so
the earlier POD debt is closed. Scope and claim boundary are honest.

## Goal5049

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The rayjoin Section 5.7 app now routes its native lexsort
through the public device_order_by surface. I verified the app imports
device_order_by, wraps four sort keys as a DeviceColumnBuffer using sliced
[:valid_count] device views inside `_run_public_device_order_by_native_lexsort`,
calls device_order_by(backend="native_cuda"), and no longer calls
run_cuda_lexsort_i64_f64_i64_i64_device directly. The valid_count sort boundary
is preserved so ordering/timing semantics do not silently change. No new
performance claim is made and the v2.14.3 headline is untouched. This is correct
app-level convergence on the public API.

## Goal5050

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The boundary audit distinguishes generic public API from
legacy and internal debt. After the Goal5062 amendment, Finding 3 now enumerates
the full seventeen-name RayJoin legacy public export set and classifies it as
compatibility debt rather than the earlier four. Finding 1 (public surfaces are
claim-bounded), Finding 2 (grouped/segmented numba exports remain outside the
public partner contract and fail closed), and Finding 4 (rayjoin app migrated to
one public path) all check out against source. The forbidden wording
"all core/internal symbols are RayJoin-free" is explicitly rejected. Native
symbol rename remains a deferred, disclosed debt. Honest and complete.

## Goal5051

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The api consolidation closeout presents v2.14.4 as a
DeviceColumnBuffer / PreparedGeometrySession / device_order_by /
NumbaPartnerContinuation surface, not a rayjoin speedup. The locked performance boundary
is stated as 0.328842s vs 0.187042s, i.e. 1.76x slower, and speedup,
parity, zero-copy, and RT-replacement wordings are forbidden. After the Goal5062
amendment the packet enumerates the full seventeen legacy rayjoin exports as
compatibility debt distinct from the new public generic API. The before/after
user example is accurate. Closeout correctly leaves release blocked on review
debt and cites remaining follow-ups.

## Goal5052

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The public api pod smoke runner defines two strict steps: a
public numba partner continuation CUDA step over a uint32 device column, and the
migrated rayjoin device_order_by native path. In strict mode a skipped CUDA or
OptiX step fails the run, and host_fallback_used is recorded false in the
committed result. The local non-strict path writes machine-readable evidence and
returns partial_skip without CUDA, which does not satisfy POD debt. The committed
result JSON shows overall_status pass and strict true with both steps passing.
Runner design and honesty are acceptable.

## Goal5053

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The release preflight gate is fail-closed and its result JSON
shows overall_status blocked_by_release_gates with external_review_debt as the
sole open blocker; required_goal_reports_present, strict_pod_smoke,
public_surface_internal_leak_scan, and legacy_rayjoin_public_exports_disclosed
all pass. The detector correctly excludes call_for_review_* files from counting
as completed reviews, a bug its own unit test caught. The gate now also enforces
the dynamic rayjoin export disclosure check from Goal5062. Gate scope and
blocking behavior are correct.

## Goal5055

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The remote pod smoke launcher mechanics are acceptable. The
earlier auth-failure status is correctly superseded by the successful POD run in
Goal5056 and the scripted environment bootstrap in Goal5057; the launcher gained
a -BootstrapPodEnv switch so callers do not have to remember the CUDA/Numba
environment variables manually. Nothing here reintroduces a stale blocker, and
the launcher is not used to assert any runtime success on its own.

## Goal5056

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The strict pod smoke result documents a real run on an RTX
4000 Ada POD, driver 550.127.05, CUDA 12.4. The root cause of the earlier failure
is stated precisely: numba 0.66 emitted PTX 8.7 while the POD accepted PTX 8.4,
producing CUDA_ERROR_UNSUPPORTED_PTX_VERSION, fixed by pinning numba 0.61.2 with
CUDA 12.4 packages. Strict smoke pass is recorded with real elapsed times, and the
limits are narrow: it is a runtime/API smoke, not a benchmark, and it does not
authorize speedup, parity, zero-copy, or device_group_by. This retires the POD
smoke debt from Goal5045/5047/5052.

## Goal5057

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The pod env bootstrap turns the Goal5056 manual cuda/numba fix
into repeatable scripts and verifies them on the POD. It correctly states the
failure was a toolchain mismatch, not the user's POD, and pins the CUDA 12.4
numba stack while forcing CUDA_HOME/CUDA_PATH/LD_LIBRARY_PATH/PATH to the venv
NVVM. The one-command strict smoke path and the -BootstrapPodEnv launcher switch
mean the fix is not dependent on user-side manual repair, which answers the
repeatability question.

## Goal5058

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The review debt content gate prevents a filename-only or
placeholder file from retiring review debt. The preflight now requires that a
review file is not a call_for_review_*, contains a verdict or verdict_label, and
contains at least one decision word, and it records malformed files under
external_review_debt.malformed. This closes the loophole where a matching
filename alone would falsely retire debt. Verified in the preflight script.

## Goal5059

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The legacy public export boundary amendment classifies the
RayJoin-named python helpers in rtdsl.__all__ as legacy public exports /
compatibility debt, not new v2.14.4 public generic API. After the Goal5062
follow-up the amendment enumerates the full seventeen-name set rather than the
original four, resolving the earlier undercount. It correctly keeps
all_public_exports_rayjoin_free unauthorized and defers actual removal to a later
export-hygiene goal to avoid a compatibility break. The disclosure is now
honest and complete.

## Goal5060

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The substantive review gate hardening rejects shallow template
approvals. The preflight now requires per-goal minimum length, the four verdict
fields, a goal-specific section, goal-specific terms, and a decision token, and it
exposes malformed_reasons so a rejection is explainable. It preserves the
consolidated single-file review workflow while blocking keyword-only approvals.
Verified against the preflight constants and logic.

## Goal5061

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: The consolidated review quality gate closes the padding
loophole: a whole-file length and keyword check could previously be satisfied by a
global keyword footer. The gate now requires each goal section to meet a 350
character minimum, contain the verdict fields and goal-specific terms and a
decision token in that section, and it scans for forbidden padding/keyword
stuffing phrases anywhere in the file. Substance must live in the relevant goal
section, not a global footer. Sound anti-gaming design.

## Goal5062

verdict_label: approve
pass/fail/required_amendments: pass
blocking_findings: none
non_blocking_notes: This goal makes the rayjoin export disclosure dynamic and
directly retires BF-1. Rather than trusting a static list, the gate scans
rtdsl.__all__ for quoted names containing rayjoin and compares the observed set
against the classified expected set, reporting missing_expected and unexpected
exports so a new rayjoin public export cannot silently pass. I confirmed the
dynamic scan yields exactly the seventeen names in __all__, that
EXPECTED_RAYJOIN_PUBLIC_EXPORTS matches with no missing and no unexpected entries,
and that all three boundary reports name all seventeen. The classification into
CDB/point-location bridge and paper-app support buckets is reasonable and the
future-proofing is the key improvement.

## Cross-Cutting Answers

1. v2.14.4 presents as RTDL API consolidation, not a rayjoin speedup: yes.
2. New public names are generic and claim-bounded: yes, verified in prior rounds.
3. device_group_by held back from public: yes, absent from rt and rt.__all__.
4. Public numba partner API proven on one non-rayjoin shape: yes (Goal5048), with
   broader proof left as honest future work.
5. RayJoin uses public device_order_by as an app: yes (Goal5049), no direct
   optix_runtime lexsort call remains in the app.
6. Legacy rayjoin symbols and exports disclosed honestly: yes, now complete after
   Goal5062 (seventeen exports enumerated; gate dynamic).
7. Avoids zero-copy, parity, broad speedup, RT-replacement claims: yes.
8. Preflight blocks until real review files exist: yes, blocked on
   external_review_debt for all required goals.
8a. Rejects shallow template approvals with malformed_reasons: yes (Goal5060).
8b. Rejects padding/keyword-footer consolidated reviews: yes (Goal5061).
9. Earlier POD-auth and missing-POD statuses superseded by Goal5056/5057: yes.
10. Safe to proceed to release-staging review after review debt retires: yes; no
    blocking amendments remain now that BF-1 is resolved.

## Final Packet Verdict

approve_v2_14_4_all_review_debt_retirement

Note: approval retires external review debt only. It does not authorize any
v2.14.4 speedup, author-parity, true-zero-copy, or public device_group_by claim,
and it does not assert the exports are private or the naming debt removed.
