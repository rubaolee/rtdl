# Goal4221 Gemini Review: Goals4218–4219 Mixed-Route Evidence And Major Target Map

Date: 2026-06-09

Reviewer: Gemini (external AI reviewer, independent)

Verdict: **accept-with-boundary**

---

## Scope

Independent review of Goals4218 and4219 against five claim-boundary questions.
All conclusions are drawn from direct inspection of the listed artifact files.

---

## Q1: RayJoin as Contract-Split Route Evidence

**Finding: PASS**

The RayJoin measurement is correctly framed as four independent per-contract
route comparisons over bounded public-CDB slices (512 points/478 shapes).
Evidence supporting this framing:

- The `rayjoin/summary.json` boundary string explicitly disavows paper
  reproduction, automatic dispatch, public speedup, and release status.
- The route recommendation differs across contracts: Numba for `pip_one_shot`
  (RTDL/OptiX speedup 0.253×, below 1.0), RTDL/OptiX for the other three
  (speedups 1.25×, 259.99×, 211.06×). A contract-uniform result would not
  demonstrate per-contract evidence; this split does.
- `"user_route_choice_visible": true` and `"automatic_dispatch": false` appear
  in `recommended_route_summary`.
- `rayjoin_paper_reproduction_claim_authorized: false` in all claim-boundary
  locations.
- The test confirms the four-contract structure and the Numba/RTDL split with
  precise assertions before scanning the full JSON tree for forbidden True flags.

The presentation does not conflate the contract-split evidence with a
whole-application or reproduction benchmark.

---

## Q2: RT-DBSCAN Unblocked Preferred for 65k Clustered3D

**Finding: PASS**

Raw numbers from the JSON artifacts:

- Unblocked: `elapsed_sec = 0.09619`, `grouped_stream_continuation_pass_count = 1`
- Blocked: `elapsed_sec = 0.43625`, `grouped_stream_continuation_pass_count = 16`
- Observed ratio: 4.535× in favor of unblocked

Both modes carry identical `boundary_assignment_policy` and
`boundary_assignment_canonical_policy` (`single_pass_candidate_root_rebased`),
so the policy state is equalized. The blocked variant issues 16 ranged query
passes over 4096-point blocks rather than one full-item pass, which explains
the overhead at this scale.

The report correctly characterizes this result as specific to the 65k
clustered3d profile and recommends keeping the blocked variant explicit rather
than default. The test enforces the observed ratio > 4.0×. Numerics, report
text, and test assertion are mutually consistent.

---

## Q3: Goal4219 Direction at Generic Language/Runtime Level

**Finding: PASS**

Each entry in `current_major_performance_targets.py` keeps next actions at the
language/runtime or broader evidence level:

- `rayjoin_contract_split_route_policy`: "use larger/non-dense same-contract
  route evidence… do not chase app-only tricks or claim whole RayJoin
  reproduction."
- `rtdbscan_profile_aware_boundary_policy`: "broader profile/scale evidence or
  advisor logic; do not promote blocked/partitioned variants by default without
  shape-specific proof."
- `prepared_session_residency_surface`: "must not enable hidden global caching
  or automatic backend/partner selection."
- `amd_hiprt_functional_parity`: gated on AMD hardware availability, not an
  NVIDIA micro-optimization.
- `major_release_candidate_packet`: gated on user decision and multi-AI
  consensus.

The goal4219 report states the purpose as "language/runtime improvements, not
app micro-tuning" and the `CURRENT_MAJOR_PERFORMANCE_TARGET_CLAIM_BOUNDARY`
string reinforces that the map is a route/runtime planning document, not a
performance table or release authorization.

---

## Q4: Explicit User Partner Choice Preserved

**Finding: PASS**

The preservation mechanism is structural rather than only documentary:

1. `CurrentMajorPerformanceTarget.__post_init__` raises `ValueError` if
   `automatic_partner_selection_authorized` or
   `app_specific_native_engine_logic_allowed` is `True`. A target with either
   flag enabled cannot be instantiated.
2. `validate_current_major_performance_targets` enforces the same constraints
   across the full matrix and returns `status: "reject"` on any violation.
3. The test asserts both flags are `False` for all six rows.
4. Both RT-DBSCAN JSON artifacts have `"automatic_partner_selection_allowed": false`
   and `"automatic_hidden_dispatcher": false` in metadata.
5. The RayJoin summary has `"automatic_dispatch": false`.

The `prepared_session_residency_surface` next-action text additionally names
the prohibition explicitly: "must not enable hidden global caching or automatic
backend/partner selection."

This is not a policy that could accidentally drift; the dataclass constructor
prevents it at object creation time.

---

## Q5: All Claim Boundaries Closed

**Finding: PASS**

Reviewed at four levels:

**Manifest claim_boundary block:** All nine flags false. The test calls
`_forbidden_true_paths(manifest["claim_boundary"])` and asserts an empty list.

**RayJoin summary.json:** Both the top-level `claim_boundary` and the
`representative_hot_path_summary` carry all relevant flags as false. The test
scans the full summary tree recursively.

**RT-DBSCAN JSON payloads:** Both unblocked and blocked payloads carry the
claim boundary in `metadata.claim_boundary`, in `count_metadata`, and in
`native_grouped_stream_metadata`. All forbidden-flag keys present in the tree
are false. The test scans both payloads recursively.

**Goal4219 target map:** The dataclass constructor enforces eight boundary flags
remain false. The `summarize_current_major_performance_targets` output emits all
eight as false at the summary level, independent of individual row values. The
test checks all rows.

One observation: the manifest uses `broad_rt_core_speedup_claim_authorized`
while the RayJoin summary also includes `broad_rt_core_claim_authorized` in the
`representative_hot_path_summary` block. The test's FORBIDDEN_TRUE_FLAGS covers
both names. Both are false in all locations. No gap exists.

---

## Overall Assessment

Goals4218 and4219 form an internally consistent, properly bounded evidence pair.

Goal4218 correctly scopes the RayJoin measurement as per-contract route
evidence over a bounded public-CDB slice, with the correct four-way split
between Numba and RTDL/OptiX contracts. It correctly identifies the unblocked
grouped stream as the appropriate default shape for the 65k clustered3d profile,
backed by a 4.5× timing advantage and confirmed canonical policy state. All
claim boundaries are closed at the artifact, metadata, and test layers.

Goal4219 maps the next major performance directions at the generic
language/runtime level, enforces explicit user partner choice as a structural
property enforced in code, and carries no authorization for any release or
public claim. The six-target matrix covers the required status vocabulary and
is validated programmatically.

**Verdict: accept-with-boundary**

The boundary qualifier is correct: the RayJoin evidence covers a single
public-CDB scale slice; the RT-DBSCAN comparison covers one dataset and scale
profile. Both are correctly marked `needs_broader_evidence` in Goal4219. No
corrections to the claim boundaries are required; the artifacts are
self-consistent with the stated scope.
