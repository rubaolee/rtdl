# Goal4806 Authoritative Goal List (4807-4815) — Reviewed by Claude

Date: 2026-06-30
Owner of this spec: Claude (independent reviewer). The main AI executes one goal,
then submits it for review against the verification criteria here before the next
goal is authorized.

## Parent objective

> Reproduce RayJoin paper Section 5.7 Polygon Overlay as an **installed-user**
> application using **released RTDL V4.0.0 + Python + Numba**, and compare
> correctness and performance against the RayJoin author C++/CUDA/OptiX
> implementation and the existing RTDL V2.14 route.

## Likely honest outcome (state now, so it is not treated as failure)

Given (a) released V4.0.0 ships no productized Section 5.7 + Numba user app,
(b) `spatial_rayjoin` was explicitly excluded from V4.0.0, and (c) the only prior
byte-equal result came from a dirty runtime route, the **most probable honest
landing is `complete_bounded_available_input_reproduction` or
`blocked_by_released_rtdl_capability_gap`.** That is a legitimate completion, not
a failure. It must never be "rescued" by editing RTDL.

## Cross-cutting rules (apply to EVERY goal; I check these every time)

- **No edits** to `src/rtdsl/**`, `src/native/**`, or the `v4.0.0` tag/release
  contents. A missing capability is a recorded product gap, never a patch.
- **Clean-environment proof is per goal, pasted in full, not inherited:** full
  `git rev-parse HEAD` (must be `6ca0849b9930295f742485cae9a17196216e0dcf` for
  released-V4 runs), full `git status --porcelain` (empty for `src/rtdsl` and
  `src/native`), and import-path proof (no import from the dirty main worktree).
- **Bundled `rayjoin_overlay` / `rayjoin_paper_suite` / `rayjoin_artifacts` /
  `v2_13_rayjoin_authors_code_packet` calls = `bundled_rayjoin_helper`**, which
  supports only "RTDL ships a RayJoin compatibility helper," NOT "a user composed
  Section 5.7 from generic RTDL language."
- **Correctness parity is a hard gate equal to performance.** No performance goal
  starts until the matching correctness goal passes.
- **Every measured number records:** command, hardware, baseline denominator,
  data scale, raw JSON/artifact path. No bare ratios. No inflated geomeans.
- **No post-hoc reclassification.** Classifications/bars are frozen before runs.
- **Each goal ends with a call-for-review.** The next goal is not authorized until
  the prior goal passes review.
- **Live outcomes throughout:** `blocked_by_released_rtdl_capability_gap` and
  `not_complete_requires_runtime_development` remain allowed at every stage.

## Authorization state

- **Goal4807 is the only currently authorized goal.** Each later goal is
  authorized only by a passing review of its predecessor.

---

## Goal4807 — Released-only API map (READ-ONLY) [AUTHORIZED NOW]

**Purpose:** Determine exactly which released V4.0.0 callables a normal user can
use for each Section 5.7 stage, classify every route, and prove no planned step
requires editing RTDL — or surface that it is a capability gap.

**Work:**
- From a fresh `git checkout v4.0.0` worktree (not the main dirty tree),
  enumerate the Section 5.7 stages: LSI; vertex PIP map0-in-map1; vertex PIP
  map1-in-map0; midpoint PIP; output-chain construction.
- For each stage, map it to the released callable(s) a user would call.
- Classify each stage's route as exactly one of:
  `generic_rtdl_operator` / `numba_user_continuation` / `bundled_rayjoin_helper`
  / `author_or_v214_baseline` / `missing_released_capability`.

**Verification (I will check):**
1. Pasted full `git rev-parse HEAD` == `6ca0849b…` and full empty
   `git status --porcelain`; import-path proof present.
2. `git diff` on `src/rtdsl` and `src/native` is empty (read-only proven).
3. All five Section 5.7 stages present, each labeled exactly one category.
4. Explicit summary: which stages support the language claim
   (`generic_rtdl_operator` / `numba_user_continuation`) vs which only work via
   `bundled_rayjoin_helper` or are `missing_released_capability`.
5. A provisional outcome label, with `blocked_by_released_rtdl_capability_gap`
   kept live if any required stage is bundled-only or missing.

**Exit label:** API map complete; honest provisional classification recorded.

---

## Goal4808 — External user-app skeleton

**Purpose:** Create the independent user-layer reproduction app (application code,
not runtime).

**Work:** `examples/paper_reproduction/rayjoin_section57_released_user_app.py`
exposing `preflight`, `manifest`, `run-author`, `run-v214`, `run-v4-released`,
`compare`; plus `tests/goal4808_..._contract_test.py`.

**Verification (I will check):**
1. Clean-env proof pasted; no edits to forbidden paths.
2. The app's imports contain **no** untagged Goal4806 helper modules (show the
   import list / grep).
3. For the `run-v4-released` path, each Section 5.7 stage's call matches the
   Goal4807 classification; any `bundled_rayjoin_helper` call is labeled as such
   in the app output, not presented as user-language reproduction.
4. Tests prove the app **reports** missing inputs/capabilities (fail-closed),
   does not crash, and does not silently rescope (e.g., LSI-only ≠ overlay).

**Exit label:** skeleton runs, fail-closed, honestly labeled.

---

## Goal4809 — Clean V4.0.0 local user smoke

**Purpose:** Run the Goal4808 app as a simulated installed user from a clean
checkout; record exactly what is present/missing.

**Verification (I will check):**
1. Records exact `v4.0.0` commit; clean-env proof pasted.
2. Records: are exact Section 5.7 CDB inputs present? are author binaries
   present? can released RTDL execute the v4 route on available inputs?
3. Contains zero evidence from the dirty development worktree.

**Exit label:** smoke result with explicit input/capability inventory.

---

## Goal4810 — POD preflight (author / V2.14 / released V4)

**Purpose:** Prepare the POD run without starting long work blindly.

**Verification (I will check):**
1. Records POD path, GPU, driver, CUDA/OptiX versions, author repo commit,
   V2.14 route, clean V4.0.0 route, dataset root, available Section 5.7 pairs.
2. States whether the full 8-pair paper-preprocessed run is possible; if not,
   names the maximum fair slice runnable now.

**Exit label:** preflight complete; runnable scope declared.

---

## Goal4811 — Exact County×Zipcode three-way correctness slice [HARD CORRECTNESS GATE]

**Purpose:** Run the smallest exact-paper slice end to end and compare author /
V2.14 / released-V4 outputs.

**Verification (I will check):**
1. Three outputs produced: author, V2.14, released-V4 user app.
2. Byte-equal where possible; otherwise topology/geometry hash + output-chain
   mismatch diagnostics recorded. **Count-only evidence is rejected.**
3. The released-V4 route used is the one classified in Goal4807; if it relied on
   `bundled_rayjoin_helper`, the result is labeled "bundled-helper reproduction,"
   not "generic-language reproduction."
4. Clean-env proof pasted; no forbidden-path edits.

**Exit label:** correctness PASS/FAIL with diagnostics. **No performance goal
(4813) starts unless this passes.**

---

## Goal4812 — Released V4 + Numba user continuation assessment

**Purpose:** Decide whether Numba can participate in the released-V4 app **without
editing RTDL**. If not, record a product gap.

**Verification (I will check):**
1. If Numba is usable: the report records exactly what data crosses the
   Python/Numba boundary and whether it stays device-resident in the hot path
   (no host materialization), with evidence.
2. If released RTDL lacks the needed device-column/continuation route: recorded
   as a product gap (`missing_released_capability`), not patched.
3. No edits to `src/rtdsl/**` or `src/native/**` (git diff empty); clean-env
   proof pasted.

**Exit label:** Numba-usable (with boundary evidence) OR product-gap recorded.

---

## Goal4813 — POD performance slice [only after Goal4811 passes]

**Purpose:** Measure author / V2.14 / released-V4 / valid V4+Numba on the same
hardware and same inputs.

**Verification (I will check):**
1. Same hardware, same inputs, same timing boundary, recorded.
2. Table columns: author s; V2.14 s; released-V4 s; V4+Numba s (only if Goal4812
   proved it valid); correctness status; input provenance.
3. Every ratio states its **baseline denominator and scale**; honest
   distribution, no inflated geomean (carry the V4.0.0 wording discipline).
4. No toy data; no claim beyond the measured slice.

**Exit label:** measured slice recorded with honest, bounded wording.

---

## Goal4814 — Available-pairs expansion or data-gap closure

**Purpose:** Decide whether Goal4806 can be all-8-pair Section 5.7 reproduction,
or must close as a bounded available-input slice with explicit data gaps.

**Verification (I will check):**
1. Exact paper-preprocessed CDB availability listed for all eight pairs.
2. Same-source regenerated rows labeled separately and **never** counted as exact
   paper reproduction.
3. If the eight pairs are not fully available, the exact missing data is named.

**Exit label:** all-8 feasible OR bounded-slice/data-gap declared.

---

## Goal4815 — Final completion packet + external review

**Purpose:** Produce the final Goal4806 decision.

**Verification (I will check):**
1. Lists author / V2.14 / released-V4 evidence with provenance.
2. States whether Goal4806 is complete under the original objective.
3. Separates product gaps from reproduction-app bugs.
4. Picks exactly one final label:
   `complete_exact_section57_reproduction` /
   `complete_bounded_available_input_reproduction` /
   `blocked_by_missing_paper_inputs` /
   `blocked_by_released_rtdl_capability_gap` /
   `not_complete_requires_runtime_development`.
5. External review requested before any completion claim.

**Exit label:** final Goal4806 status, externally reviewed.

---

## How review works

After each goal, the main AI submits the goal's deliverables. I check them against
that goal's Verification list. Result is one of: `pass_authorize_next_goal`,
`pass_with_amendments`, or `fail_redo`. No goal beyond Goal4807 is authorized
until its predecessor returns `pass...`. Any attempt to edit `src/rtdsl/**`,
`src/native/**`, or the `v4.0.0` tag, or to present a `bundled_rayjoin_helper`
result as generic-language reproduction, is an automatic `fail_redo`.

## Non-authorization

This spec authorizes execution of Goal4807 (read-only) only. It does not authorize
later goals (each needs its predecessor's passing review), POD spend before
Goal4810/4811 gates, runtime/source edits, or any completion/performance claim
before Goal4815 external review.
