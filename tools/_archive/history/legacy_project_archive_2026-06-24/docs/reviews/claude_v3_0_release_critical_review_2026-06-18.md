# RTDL v3.0 — Critical Release Review

**Reviewer:** Claude (independent technical reviewer) · **Date:** 2026-06-18
**Scope reviewed:** `v3.0` source tree (tag `v3.0` at commit `8b0b42f8`, plus post-release cleanup `cb3c4626`).
**Method:** Direct inspection of the source tree — README, docs, Makefile, `include/`, `packaging/`, `scripts/run_test_matrix.py`, and the V3.0 gate tests. File paths and line numbers cited are from this commit.

---

## Executive verdict

**Acceptable with issues — not yet ready for wider public attention.**

The learner-facing *prose* (`docs/learn/current_claim_boundaries.md`, `docs/backend_maturity.md`, `docs/release_reports/v3_0/`) is conservative and well-written, and the docs/history fencing is properly gated. But the scope boundary claimed in words is leaking through the code, build, and validation layers. Three structural leaks contradict the stated V4-exclusion boundary:

1. the canonical V3.0 validation group certifies V4 C-ABI/embedding/zero-copy work as "current";
2. a C-ABI header plus pkg-config/CMake packaging sit at the repository front door;
3. `make help` advertises C-ABI staging as a public target.

A new user — or a skeptical outsider — will read "no C ABI, no SDK, no zero-copy" in the docs while the repo root, Makefile, and test gate say otherwise. Fix the boundary leaks and the README tone density and this becomes release-quality.

**What's good (briefly):** the claim-boundary and backend-maturity pages are model examples of conservative wording; the `docs/history/v4_preparatory_embedding/` archive with its explicit "Reading Rule" is exactly right; `tests/v3_0_user_docs_history_boundary_test.py` is a real gate, not theater.

---

## Highest-risk issues (fix before publication)

### H1 — The canonical V3.0 validation group validates V4-excluded scope
`scripts/run_test_matrix.py`, the `"v3_current"` group (starts line 64), includes ~52 references to `c_abi`, `embeddability`, and `zero_copy` tests (lines ~103–145: `goal4549_…embeddability_strategy_intake`, `goal4550_…c_abi_draft`, `goal4560_…c_abi_embedding_readme`, `goal4568_…zero_copy_interop_contract`, etc.). This is the command the release package names as *the* validation gate (`docs/release_reports/v3_0/README.md` lines 21, 77). So the gate that defines "V3.0 complete" functionally certifies the embedding/C-ABI/zero-copy surface that `current_claim_boundaries.md` (lines 15–17) and the release README (lines 35–36, 67) say is **excluded from V3.0**. This is the sharpest contradiction in the release. Either these tests validate that the prep material is *fenced* (then rename/move them to a `v4_prep` group) or they validate it as *working current surface* (then the exclusion claim is false). It currently reads as the latter.

### H2 — C-ABI and SDK-packaging artifacts live at the repository front door
`include/rtdl/rtdl.h` (a C ABI header), `packaging/rtdl-c-api.pc` (pkg-config), and `packaging/rtdl-c-api-config.cmake` (CMake find-package config, exposing target `rtdl::c_api`) are top-level directories. pkg-config and CMake config files are *literally* package-install/SDK artifacts — their presence contradicts "not an SDK… C ABI not a release surface… no package-install claims." The header's own comment is honest ("V3 draft C ABI… not a frozen or backend-capable contract"), and the symbol manifest is correctly under `docs/history/v4_preparatory_embedding/` — but the placement at repo root undoes that. Worse, **`README.md`'s Repository Layout table (lines 269–281) does not list `include/`, `packaging/`, `build/`, `history/`, or `src/native/`**, so the documented layout doesn't match the real tree, and the two most scope-sensitive directories are the undocumented ones.

### H3 — `make help` advertises the embedding build surface as public
`Makefile` lines 182–185, under the literal heading `"Public targets:"`, list `build-c-api`, `stage-c-api`, `stage-c-api-prefix`, and `package-c-api-stage` ("archive the source-tree C ABI staging bundle"). A new user running `make help` is told C-ABI packaging is a public, supported action. That is V4 scope presented as current.

### H4 — None of H1–H3 is gated
`tests/v3_0_user_docs_history_boundary_test.py` fences *docs and examples* well (it asserts `examples/current/embedding` does not exist, that the C-ABI draft lives in history, etc.) — but it never inspects `include/`, `packaging/`, the Makefile public targets, or the `v3_current` group. The leak class that actually escaped is precisely the class with no guard. The good docs gate gives false confidence.

---

## User-learning issues

### L1 — The README front-loads disclaimers over teaching
The first substantive paragraph (lines 16–24) is roughly half caveats, and the "do not read this as…" catalog repeats at lines 169–180 and 197–208. Conservative is correct, but the density buries the learning path under legal-sounding negation before the reader knows what RTDL *does*. Move the full negative catalog into `current_claim_boundaries.md` (where it already lives) and leave the README a single pointer plus the Start-Fast path.

### L2 — `RTDL` vs `rtdsl` naming is unexplained
The product is RTDL, but the import is `import rtdsl as rt` (README line 84) and the editable install exposes `rtdsl` (line 58; `pyproject.toml` `include = ["rtdsl*"]`). A newcomer will trip on this. One sentence — "the import package is `rtdsl`" — fixes it.

### L3 — The learning ladder itself is clean
README → `tutorials/current/` → `examples/current/` → `scripts/rtdl_source_tree_doctor.py` is coherent and the gate `goal4273_current_tutorial_ladder_test.py` exists. This part is good; the only concern is that L1's caveat wall sits in front of it.

---

## Claim-boundary / wording issues

### C1 — `engine_support_matrix.md` overstates multi-vendor maturity
It marks Vulkan, HIPRT, and Apple RT as `native` across nearly every row (lines 25–48), with the only hedge a single line at the very bottom (line 56, HIPRT-on-Orochi). There is no inline caveat for Vulkan/Apple RT and no link to `docs/backend_maturity.md`, which correctly downgrades all three to "Proof/portability… no performance claim." A reader landing on the support matrix first sees broad multi-GPU "native" support that the claim-boundary page (line 61: no AMD/HIPRT/Intel-GPU claims) forbids. Add a banner at the top of the matrix linking `backend_maturity.md` and stating that `native` describes *feature behavior, not validated-hardware performance*.

### C2 — README's building-blocks list repeats the overstatement
Line 144 lists "CPU reference, native CPU, Embree, OptiX, HIPRT, Vulkan, Apple RT/MPS RT where documented" as backend selection. "where documented" is thin cover for naming five GPU backends at the front door. Reduce to Embree + OptiX as the active performance engines and point to backend-maturity for the rest.

The rest of the wording is strong. `current_claim_boundaries.md`, `backend_maturity.md`, and `docs/release_reports/v3_0/README.md` are conservative and explicit and should not be watered down.

---

## Test / validation gaps

- **V1 (=H1):** `v3_current` bundles V4 scope. Split it.
- **V2 (=H4):** No gate fences `include/`, `packaging/`, Makefile public targets, or the test-group composition. Extend the history-boundary gate to the code/build/test layers.
- **V3 — `make test` ≠ canonical validation.** `Makefile` line 352 runs `unittest discover -s tests` — all **2,858** test files, including every V4 embeddability test — while the release defines `run_test_matrix.py --group v3_current` as canonical. The default contributor command and the canonical command disagree. Point `make test` at the current group and give the full sweep a separate `make test-all` / archive target.
- **V4 — test-tree clutter.** 2,828 of 2,858 files are `goal####_*` (e.g. `goal30_…` through `goal4614_…`). The current gates are needles in that haystack. Consider moving archival goal tests under `tests/history/` so the current gate set is legible.
- **V5 — the docs gate is allowlist-shaped.** `v3_0_user_docs_history_boundary_test.py` scans a fixed `CURRENT_DOC_PATHS` tuple against a narrow literal forbidden-phrase list ("RTDL v2.10 is the current", etc.). New stale phrasing in any *other* current doc isn't caught. A scan of the whole non-`history/` docs tree for version-marker drift would be more durable.
- **V6 — stale top-level artifact.** `run_review_tests.py` still runs v2.0 release-candidate goal tests (`goal2319_v2_0_final_cleanup_release_candidate_test`, etc.). It's dead/misleading at the repo root. Delete or repoint to v3.0.

---

## Specific recommended edits

1. `scripts/run_test_matrix.py`: remove all `c_abi` / `embeddability` / `zero_copy` entries from `"v3_current"`; create `"v4_prep"` for them. Update `docs/release_reports/v3_0/README.md` lines 21/77 accordingly.
2. Move `include/rtdl/` and `packaging/rtdl-c-api*` under `docs/history/v4_preparatory_embedding/staging/` (or a top-level `preview/` dir whose README states V4-only). Update `Makefile` C-API paths.
3. `Makefile` lines ~182–185: relocate the `*-c-api` targets out of `"Public targets:"` into a clearly labeled `"V4 preparatory (not a V3.0 surface):"` block.
4. `tests/v3_0_user_docs_history_boundary_test.py`: add assertions that `include/rtdl/rtdl.h` and `packaging/rtdl-c-api*` are **not** at repo root, that `make help` "Public targets" contains no `c-api` target, and that `v3_current` contains no `c_abi`/`embed`/`zero_copy` module.
5. `Makefile` line 352: `test` → run the `v3_current` group; add `test-all` for the full discover sweep.
6. `docs/features/engine_support_matrix.md`: top banner linking `backend_maturity.md`; mark Vulkan/HIPRT/Apple RT columns "proof/portability — not validated-hardware performance."
7. `README.md`: list `include/`, `packaging/`, `build/`, `history/`, `src/native/` in the layout table (labeled preparatory where apt) **or** move them; trim the caveat blocks to a pointer; add the one-line `rtdsl` import note; reduce line 144 to Embree+OptiX.
8. Delete or repoint `run_review_tests.py`.

---

## "Do these first" checklist (prioritized)

1. **[P0]** Split V4 tests out of the `v3_current` group (H1/V1) — the boundary contradiction is the thing most likely to be noticed publicly.
2. **[P0]** Fence `include/` + `packaging/` out of the front door (H2).
3. **[P0]** Add the code/build/test guard to the boundary gate (H4/V2) so this cannot silently regress.
4. **[P1]** Demote the `*-c-api` Makefile targets out of "Public targets" (H3).
5. **[P1]** Make `make test` == canonical `v3_current`; separate the full sweep (V3).
6. **[P1]** Fix `engine_support_matrix.md` maturity framing + cross-link (C1).
7. **[P2]** README: layout table, caveat trimming, `rtdsl` note, backend-list trim (H2/L1/L2/C2).
8. **[P2]** Delete stale `run_review_tests.py` (V6); consider `tests/history/` relocation (V4).

---

## V4 candidates that should stay out of V3.0

The prose already names these correctly as V4 — the work is making the *artifacts and tests* match the prose: embedding / C ABI as a release surface, SDK packaging (pkg-config, CMake config), generated bindings, public true zero-copy, device-buffer query execution, external CUDA stream ordering, and device-callable fusion. Keep all of it in `docs/history/v4_preparatory_embedding/` (and a clearly-labeled staging area), validated by a separate `v4_prep` group, never by `v3_current`.

---

## Net assessment

The boundary discipline in the *writing* is excellent; the failure is that the build system, repo layout, and canonical test group never got the same fencing, so V3.0 currently certifies and advertises the very V4 surface it disclaims. None of this is deep — it is relocation, group-splitting, and a few guard assertions — but it is the difference between "conservative release" and "release whose own test gate contradicts its claims."
