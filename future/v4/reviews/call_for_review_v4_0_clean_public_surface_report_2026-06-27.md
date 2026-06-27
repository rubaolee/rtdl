# Call For Review: V4.0.0 Clean Public Surface Report

Date: 2026-06-27

Requested reviewer: Antigravity

Verdict requested: choose exactly one.

- `approve_v4_0_clean_public_surface`
- `approve_with_required_minor_fixes`
- `block_public_surface_until_fixed`
- `block_release_tag_until_fixed`

## Review Goal

Please critically audit whether the V4.0.0 public surface is now clean enough
for users.

The release owner requirement was:

1. Users should see one current V4 surface, not a maze of V2/V3/V4 history.
2. Old, confusing, internal, or dead material must be moved out of the normal
   first-time path.
3. Tutorials and examples must be coherent, runnable, and not written as
   internal review-defense material.
4. Benchmark app source browsing should start from clean V4 entrypoints, not
   large historical harnesses.
5. Public links must resolve and must not send new users into history or
   maintainer provenance by accident.

## Current Release Pointer

Local and remote have been pushed.

- Branch: `codex/v4-tier2-section8`
- Tag: `v4.0.0`
- Commit: `a2c661d4f08d97937ddc4e09c0d2bdd75e988027`
- Remote branch: `origin/codex/v4-tier2-section8`
- Remote tag: `origin refs/tags/v4.0.0`

## What Was Cleaned

### Public documentation

The first-time user path was cleaned around:

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/v4_release_notes.md`
- `docs/v4_engineering_summary.md`
- `docs/app_level_benchmark_summary.md`
- `docs/public_documentation_map.md`
- `docs/learn/README.md`
- `docs/learn/operator_catalog.md`
- `docs/learn/partner_choice.md`
- `docs/learn/performance_wording.md`
- `docs/learn/source_tree_doctor.md`
- `tutorials/README.md`
- `tutorials/current/`
- `examples/README.md`
- `examples/simple/README.md`
- `examples/benchmark_apps/README.md`
- `examples/paper_reproduction/README.md`

Recorded action summaries:

- `future/v4/reviews/v4_docs_full_audit_action_summary_2026-06-27.md`
- `future/v4/reviews/v4_public_link_consistency_audit_2026-06-27.md`
- `future/v4/reviews/v4_user_visible_file_audit_from_readme_2026-06-27.md`

### Benchmark app source surface

The 10 benchmark app directories now expose `v4_app.py` as the current user
entrypoint:

- `examples/benchmark_apps/rt_dbscan/v4_app.py`
- `examples/benchmark_apps/rtnn/v4_app.py`
- `examples/benchmark_apps/triangle_counting/v4_app.py`
- `examples/benchmark_apps/robot_collision/v4_app.py`
- `examples/benchmark_apps/raydb_style/v4_app.py`
- `examples/benchmark_apps/librts_spatial_index/v4_app.py`
- `examples/benchmark_apps/contact_manifold/v4_app.py`
- `examples/benchmark_apps/spatial_rayjoin/v4_app.py`
- `examples/benchmark_apps/barnes_hut/v4_app.py`
- `examples/benchmark_apps/hausdorff_xhd/v4_app.py`

The large historical harness bodies were moved to:

- `history/v4_0_benchmark_harness_archive_2026-06-27/`

The old harness filenames remain only as small compatibility bridges so old
commands, tests, and reproduction scripts still work. The bridge layer is:

- `examples/benchmark_apps/_support/archived_harness_runner.py`

The clean V4 public entry helper is:

- `examples/benchmark_apps/_support/v4_public_entry.py`

Recorded action summary:

- `future/v4/reviews/v4_benchmark_harness_public_entry_cleanup_2026-06-27.md`

## Verification Already Run

The following passed after the final push/tag update:

```powershell
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4743_public_docs_current_framing_test tests.v4_goal4643_publication_decision_test tests.v4_goal4646_pretag_wording_fixes_test
```

Result: `Ran 30 tests ... OK`

```powershell
py -3 -m unittest tests.v4_goal4773_release_authorization_status_test tests.v4_release_clean_checkout_gate_test tests.v4_goal4775_release_staging_manifest_test
```

Result: `Ran 12 tests ... OK`

```powershell
py -3 scripts\v4_release_clean_checkout_gate.py
```

Result: `status = passed`; `tag_matches_head = true`; `working_tree_clean = true`;
`universe_public_findings = []`; `universe_unknown_untracked_count = 0`.

```powershell
py -3 scripts\v4_universe_audit.py --strict-release
```

Result: `status = pass`; `public_findings = []`; `public_link_findings = []`;
`unknown_untracked_count = 0`.

## Review Questions

Please answer every question directly.

1. Is the public first-time path clean enough for a V4.0.0 major-version
   release?
2. Do root README, docs, tutorials, and examples present one coherent current
   V4 product instead of confusing users with historical release layers?
3. Are any internal process terms, goal labels, review-debt language, or AI
   reviewer names still leaking into public user-facing docs or current
   examples?
4. Are public links consistent, resolving, and pointed at current V4 material
   rather than history/provenance?
5. Does `tutorials/current/` now read like a learning path rather than a release
   defense packet?
6. Are `examples/simple/` and `examples/benchmark_apps/*/v4_app.py` acceptable as
   runnable and browseable current examples?
7. Is the archived-harness bridge design acceptable: old full harnesses in
   `history/`, current `v4_app.py` for users, old filenames preserved only as
   compatibility bridges?
8. Does the final tag state look valid: remote branch and remote tag both point
   to `a2c661d4f08d97937ddc4e09c0d2bdd75e988027`?
9. Are the claim boundaries still honest: no broad "all benchmark apps are
   faster" claim, no public Tier-3 callback/PTX claim, no public true-zero-copy
   claim, no paper-reproduction overclaim?
10. If you block or require fixes, list exact file paths and required edits.

## Non-Authorization Boundaries

Even if you approve this cleanup, do not authorize claims outside the V4.0.0
bounded release surface. In particular, do not authorize:

- broad V4-over-V2.14 speedup wording;
- "all benchmark apps are faster";
- public arbitrary callback/PTX/Tier-3 support claims;
- public true-zero-copy or embedding/C ABI claims;
- RT-BarnesHut paper-reproduction claims beyond the documented reproduction
  boundary.

## Requested Output

Please write a review file under:

`future/v4/reviews/antigravity_v4_0_clean_public_surface_review_2026-06-27.md`

Use this structure:

1. Verdict label.
2. P0/P1/P2 findings.
3. Answers to the 10 review questions.
4. Required fixes, if any.
5. Explicit non-authorization block.
