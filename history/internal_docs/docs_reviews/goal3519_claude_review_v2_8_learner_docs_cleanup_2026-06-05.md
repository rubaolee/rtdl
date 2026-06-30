# Goal3519: Claude Review — v2.8 Learner Docs Cleanup

Date: 2026-06-05

Reviewer: Claude (independent read-only pass)

Verdict: `accept-with-boundary`

---

## Scope

Independent review of the active learner-facing docs after the Goal3519 cleanup.
Files inspected: `README.md`, `docs/README.md`, `docs/learn/README.md`,
`docs/learn/benchmark_partner_reference_matrix.md`,
`docs/learn/partner_choice_for_custom_logic.md`,
`docs/learn/primitive_discovery_workflow.md`,
`docs/learn/prepared_execution_pattern.md`,
`docs/tutorials/README.md`, all tutorial `*.md` files,
`examples/v2_0/research_benchmarks/README.md`, and the four subdirectory
benchmark READMEs. Also inspected `tests/goal3519_v2_8_learner_docs_cleanup_test.py`
and `docs/reports/goal3519_v2_8_learner_docs_cleanup_audit_2026-06-05.md`.

---

## Q1 — Coherent v2.8 story across active learner docs

**Pass.**

Every active markdown document framed in the learner path uses consistent
`v2.8 source-tree` language. The front page leads with "current v2.8 source-tree
RTDL surface" in the first paragraph. Each tutorial carries "v2.8-facing" in its
header line. `docs/README.md` opens: "RTDL v2.8 is the active source-tree
Python+partner+RTDL app-portfolio surface on this branch." The research
benchmark door carries "RTDL v2.8 Research Benchmarks" in its title with
"primitive first" framing throughout.

An independent grep for `v2\.(3|5|6|7|x)|v2_[67]|release package` over all
active markdown paths returned zero matches, confirming the cleanup is complete
at the doc level.

---

## Q2 — Historical v2.6/v2.3 references limited to explicit history/audit contexts

**Pass.**

In `README.md`, v2.6 and v2.3 references appear only inside the "History And
Audit Trail" section (labeled links to "Historical v2.6 Release Package" and
"Historical v2.3 Release Package"). No such references appear in the learner
path, tutorial ladder, or benchmark READMEs. The docs index carries
"Release Reports" and "History Index" links as clearly separated audit rows in
its reference table, not as current surface entries.

---

## Q3 — Overclaim avoidance

**Pass.**

Boundary language is consistent, explicit, and appears at every layer:

- `README.md` blocks package-install, auto partner-selection, zero-copy, and
  broad speedup in the opening description.
- `README.md`'s "v2.8 Source-Tree Surface" section separately blocks
  package-install, broad RT-core, arbitrary PyTorch/CuPy/Numba acceleration,
  and arbitrary polygon overlay.
- `docs/learn/prepared_execution_pattern.md` lists all seven blocked claim types.
- `docs/learn/primitive_discovery_workflow.md` carries the same complete list.
- `docs/tutorials/README.md` has an explicit "Not allowed" section.
- `partner_anyhit.md` explicitly reports `true_zero_copy_authorized: false` and
  `rt_core_speedup_claim_authorized: false` in its example output.
- `partner_choice_for_custom_logic.md` and `benchmark_partner_reference_matrix.md`
  both include "This is not a release tag, package-install promise, or broad
  speedup claim" as status lines.
- All four research benchmark READMEs block paper-reproduction and public speedup
  wording and require exact script, artifact, backend, hardware, and commit
  before any performance statement.
- `hausdorff_xhd/README.md` explicitly separates `rtdl_v2_user_cuda` (CUDA-core
  continuation, not RT-core) from methods that do use OptiX RT cores.

No overclaim language was found. The pattern is thorough.

---

## Q4 — Docs test quality

**Pass.**

The test at `tests/goal3519_v2_8_learner_docs_cleanup_test.py` is well-scoped
and useful:

`test_active_docs_do_not_teach_old_versions` scans all active markdown files
under the learner dirs for stale version terms. The regex
`r"\bv2\.(?:3|5|6|7|x)\b|\bv2_[67]\b|release package"` covers the known
historical version strings and is applied to tutorial subdirectory `*.md` and
benchmark subdirectory `*/README.md` files. This will catch regressions if any
future edit reintroduces v2.6 wording in the active path.

`test_main_doors_are_v2_8_facing` adds positive assertions: it checks that the
three main door files contain required phrases such as "RTDL v2.8 Tutorials",
"Prepared Execution Pattern", and "primitive first". This prevents silent
over-erasure where the version bump is removed but no current language replaces
it.

`test_local_links_in_main_doors_resolve` resolves every local markdown link in
the four main door files against the filesystem. The audit reports this test
passed.

One observation: the root `README.md` is intentionally excluded from the stale-
term scan, because its "History And Audit Trail" section legitimately contains
`v2.6` and `v2.3` links. That exclusion is correct. The test covers what it
should.

---

## Q5 — Local links in main doors

**Pass.**

I independently verified critical links from the four main doors:

| Link target | Status |
| --- | --- |
| `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md` | exists |
| `docs/learn/prepared_execution_pattern.md` | exists |
| `docs/learn/primitive_discovery_workflow.md` | exists |
| `docs/tutorials/feature_quickstart_cookbook.md` | exists |
| `docs/reports/goal2492_benchmark_app_reconstruction_principle_and_raydb_scope_2026-05-22.md` | exists |
| `docs/release_facing_examples.md` | exists |
| `docs/history/tutorial_archive/README.md` | exists |

The test suite's link-check covers the four door files and passed. No broken
or suspicious links were identified.

The `docs/README.md` current-reference table entry that points to Goal3518's
report file (rather than any v2.6 release package) is the right current
reference pointer.

---

## Q6 — Stale code-level helper names: block or defer?

**Defer to Goal3520. Does not block Goal3519.**

An independent grep over the `examples/v2_0/research_benchmarks/` Python source
files confirms that `v2_6` and `v2_5` names remain in internal Python code:
constants such as `RAYJOIN_V2_6_NUMBA_COMPACT_MASK_VERSION`,
`RAYDB_V2_6_NUMBA_NEUTRAL_CONTINUATION_VERSION`,
`rtdl.triangle_counting.v2_6.numba_compact_mask_preview.v1`, and docstrings
that reference "v2.x user API" or "v2.5 continuation." These are entirely in
`.py` files; the test suite explicitly scans `.md` files only, and the grep
confirmed the active markdown surface is clean.

Renaming these internal version strings in Goal3519 would be a separate code
migration task. The names are internal protocol version identifiers or
docstring labels, not learner-visible doc wording. The residual risk is low
because no learner reads Python function docstrings in the benchmark source as
their primary guide — they read the READMEs, which are clean. Goal3520 is the
correct vehicle for deciding whether to alias, quarantine, or migrate these
names, since that decision requires reviewing which names are part of a stable
internal API contract and which are safe to rename.

---

## Additional Observations

**Prepared execution pattern integration is clean.** The new
`docs/learn/prepared_execution_pattern.md` and its tutorial-ladder entry at
step 7 give a clear five-phase model (prepare, pack/cache, warm, steady-state,
explain timings). The document is honest about what the `0.00387` s steady-state
number means and what it does not authorize.

**Benchmark lessons in partner-choice docs are current.** The
`benchmark_partner_reference_matrix.md` and `partner_choice_for_custom_logic.md`
correctly reference `v2_8_benchmark_matrix()` and `summarize_v2_8_benchmark_matrix()`
as the programmatic guidance path. The Triton-paused note is consistent across
both documents and the research benchmark READMEs.

**The `examples/v2_0` path stability note is handled well.** Multiple files
explain that the directory path stays `v2_0` for compatibility while the README
content is current v2.8 guidance. This is an appropriate design decision that
avoids breaking existing references while keeping learner-visible language current.

---

## Verdict

`accept-with-boundary`

The active learner docs now present one coherent v2.8 source-tree story. The
historical release links are correctly segregated. All seven blocked claim
categories are enforced consistently across the learner path. The test suite is
a useful guard for future regressions. No main-door links are broken. Stale code-
level helper names in Python source files are known residuals that do not affect
the learner path and are correctly deferred to Goal3520.

This is not release authorization. The standard blocks on public speedup
wording, package-install promises, broad RT-core claims, true-zero-copy claims,
paper-reproduction claims, hidden partner-selection, and app-specific-engine
claims remain in force.
