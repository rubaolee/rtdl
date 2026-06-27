# Call For Review: V4 Post-Release Public Surface Cleanup

Date: 2026-06-27

Requested reviewer role: strict external reviewer for the V4.0.0 public
surface after release cleanup.

## Review Verdict Requested

Please return exactly one verdict label:

- `approve_public_surface_cleanup_for_push`
- `approve_with_required_fixes_before_push`
- `block_public_push_until_fixed`

This review is about the public repository surface after V4 cleanup. It is not
a request to re-authorize performance claims, broaden benchmark wording, or
approve V4.1/V5 work.

## Background

The release cleanup goal is simple: a new user who lands on the project should
see one current V4 system, not old V2/V3/V4 process debris, review language, or
stale paths. Historical material may exist in archival/provenance directories,
but the public learning path must not push users into it.

The cleanup covered:

- project front page;
- current docs;
- current tutorials;
- current examples;
- benchmark-app learning path;
- public Markdown links;
- machine gates that should prevent this class of drift from returning.

## Work Claimed Complete

### 1. Examples Surface

The examples surface was reorganized into three current entrypoints:

- `examples/simple/`
- `examples/benchmark_apps/`
- `examples/paper_reproduction/`

Older example layouts were moved out of the user path. The current
`examples/README.md` no longer sends users to old layouts and explains only
the three current entrypoints.

Relevant commit:

- `6e81bcb0` — `Clean V4 public examples surface`

Additional cleanup after the first review pass added clean current benchmark
app wrappers:

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

`examples/benchmark_apps/README.md` and
`tutorials/current/06_benchmark_apps.md` now point users at these wrappers
instead of the old full harness files. The full harnesses remain available
behind `--run-harness -- ...` for reproduction work.

### 2. Public Docs Surface

The current public docs were rewritten/cleaned so they read as current V4 user
documentation rather than internal release-defense material.

Files included in the docs audit:

- `README.md`
- `docs/README.md`
- `docs/v4_release_notes.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/public_documentation_map.md`
- `docs/v4_engineering_summary.md`
- `docs/learn/README.md`
- `docs/learn/operator_catalog.md`
- `docs/learn/partner_choice.md`
- `docs/learn/performance_wording.md`
- `docs/learn/source_tree_doctor.md`

The per-file action summary was written to:

- `future/v4/reviews/v4_docs_full_audit_action_summary_2026-06-27.md`

Relevant commits:

- `22c121e7` — `Clean V4 public documentation surface`
- `5dbb06ab` — `Align V4 doc gates with clean public wording`

### 3. Tutorial Surface

The current tutorial path is:

- `tutorials/current/README.md`
- `tutorials/current/01_first_run.md`
- `tutorials/current/02_hello_world.md`
- `tutorials/current/03_backend_choice.md`
- `tutorials/current/04_prepared_runtime.md`
- `tutorials/current/05_measurement_boundaries.md`
- `tutorials/current/06_benchmark_apps.md`
- `tutorials/current/07_partner_choice.md`

Claim: these tutorials now teach RTDL as a programming model, from RT-shaped
relations to the benchmark-app recipes, rather than presenting internal
measurement or review language as user education.

### 4. Link Consistency Cleanup

The public docs/examples/tutorials were cleaned so current user-facing Markdown
does not actively link users into `history/` or `future/`.

Changed files:

- `README.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `docs/v4_engineering_summary.md`
- `examples/README.md`
- `scripts/v4_universe_audit.py`
- `tests/v4_goal4640_public_docs_cleanup_test.py`

The link-specific audit record was written to:

- `future/v4/reviews/v4_public_link_consistency_audit_2026-06-27.md`
- `future/v4/reviews/v4_user_visible_file_audit_from_readme_2026-06-27.md`

Relevant commit:

- `cfb6bac4` — `Guard V4 public links`

### 5. Machine Gates Strengthened

The cleanup is now guarded by:

- `scripts/v4_universe_audit.py`
- `scripts/v4_release_clean_checkout_gate.py`
- `tests/v4_goal4640_public_docs_cleanup_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_goal4643_publication_decision_test.py`
- `tests/v4_goal4644_post_release_guardrails_test.py`
- `tests/v4_goal4646_pretag_wording_fixes_test.py`
- `tests/v4_goal4743_public_docs_current_framing_test.py`

The link gate in `scripts/v4_universe_audit.py` now checks public Markdown for:

- missing local link targets;
- links that escape the repository;
- absolute local paths;
- links to `history/` or `future/`;
- stale internal process language in public docs.

## Verification Claimed

Commands run from the repository root:

```powershell
py -3 scripts\v4_universe_audit.py
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test tests.v4_goal4644_post_release_guardrails_test tests.v4_goal4646_pretag_wording_fixes_test tests.v4_goal4743_public_docs_current_framing_test
py -3 scripts\v4_release_clean_checkout_gate.py
py -3 -m build . --sdist --wheel --outdir <temp-build-dir>
```

Claimed results:

- `scripts\v4_universe_audit.py`: `status: pass`
- `public_findings`: `[]`
- `public_link_findings`: `[]`
- public/frontdoor tests: `Ran 34 tests ... OK`
- `scripts\v4_release_clean_checkout_gate.py`: passed
- `v4.0.0` local tag points to current `HEAD`
- working tree was clean after the final link-consistency commit
- package build produced V4.0.0 sdist and wheel

Reviewer should verify the current tagged commit with:

```powershell
git rev-parse HEAD
git rev-parse 'v4.0.0^{}'
```

The two hashes should match after the final local tag update.

## Reviewer Questions

Please answer each question explicitly.

1. Is the project front page clean and consistent enough for a first-time V4
   user?
2. Do any public docs still leak internal goal numbers, review-debt language,
   reviewer names, process/audit phrasing, or old release framing?
3. Do any public docs/tutorials/examples still link users into `history/`,
   `future/`, old example layouts, old docs paths, or stale GitHub URLs?
4. Are all Markdown links in the public path correct and internally
   consistent?
5. Does `docs/app_level_benchmark_summary.md` read as a user-facing benchmark
   report rather than an internal release-defense note?
6. Does `tutorials/current/06_benchmark_apps.md` teach users how benchmark
   apps are built, rather than asking them to reason about release claims?
7. Is `examples/README.md` now clear enough: simple examples, benchmark apps,
   paper-reproduction apps, and no confusing `current`/`v4` split?
8. Do the 10 benchmark `v4_app.py` wrappers provide a clean enough current V4
   user entrypoint for each benchmark app?
9. Are the remaining full harness files acceptable as internal implementation
   harnesses behind wrappers, or must they be moved/scrubbed before push?
10. Are the public performance statements bounded, denominator-aware, and free
   of blanket speedup claims?
11. Are the new machine gates sufficient to prevent broken public links and
   stale public-surface language from returning?
12. What specific file-level fixes, if any, are required before public push?

## Known Boundary

This cleanup does not claim that every source module name inside the Python
package has been renamed away from historical naming. The package still
contains older implementation modules because V4 is a V2/V3 superset and those
routes are still part of the implementation. This review is specifically about
the public docs/tutorials/examples/front-door path and the machine gates around
that path.

If the reviewer believes package-internal source browsing is itself part of the
public user surface for this release, please mark that as a separate required
fix with exact file/path examples.

## Non-Authorization

This review does not authorize:

- new performance claims;
- broad "all benchmark apps are faster" wording;
- Tier-3 arbitrary callback claims;
- raw OptiX callback claims;
- C ABI / embedding claims;
- V4.1 work;
- remote push by itself.

It only asks whether the post-release public-surface cleanup is acceptable for
the next public push.
