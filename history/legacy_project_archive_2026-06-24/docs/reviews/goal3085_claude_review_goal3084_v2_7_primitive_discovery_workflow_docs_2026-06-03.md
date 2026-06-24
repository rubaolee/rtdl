# Claude Review of Goal3084 v2.7 Primitive Discovery Workflow Docs

**Date:** 2026-06-03

**Reviewer:** Claude (claude-sonnet-4-6)

**Handoff Document:** `docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL3084_V2_7_PRIMITIVE_DISCOVERY_WORKFLOW_DOCS_2026-06-03.md`

**Verdict: `accept-with-boundary`**

---

## Question 1: Does the example run as metadata-only discovery and avoid backend execution, partner dispatch, hidden routing, or selected partner behavior?

**Finding: Pass.**

The example (`examples/v2_0/getting_started/rtdl_primitive_discovery_workflow.py`) satisfies this question at every layer.

- The returned JSON sets `status: "metadata_only_no_execution"` (line 44).
- The `advisory_plan` exposes `plan.executes`, `plan.selected_partner`, and `plan.automatic_partner_selection_allowed` as explicit output fields, making the no-dispatch contract visible rather than assumed.
- The `claim_boundary` string in the JSON output reads: "This example does not run a backend, dispatch a partner, select a partner, authorize performance wording, or authorize release readiness. It only shows how to inspect RTDL primitive metadata."
- The deliberate use of `partner="numba"` with fixed-radius ranked planning exercises the `unsupported_fail_closed` support-matrix cell. This is the correct pedagogical choice: it shows learners that requesting a partner name does not silently enable that partner, because `selected_partner` remains `null`.
- The test (`tests/goal3084_v2_7_primitive_discovery_workflow_docs_test.py`, `test_primitive_discovery_workflow_example_runs`) asserts `selected_partner is None`, `executes is False`, and `automatic_partner_selection_allowed is False` against the actual subprocess output.

No backend is instantiated, no partner is dispatched, no hidden routing occurs.

---

## Question 2: Do the learner docs explain `find_primitive(...)`, `find_recipe(...)`, and `plan_continuation(...)` clearly without making RTDL look like an app-shaped library or hidden dispatcher?

**Finding: Pass.**

`docs/learn/primitive_discovery_workflow.md` explains each function in a dedicated section with a code snippet and a plain-language framing question.

- **Step 1** describes `find_primitive(...)` as searching "the primitive hierarchy by controlled facets" to answer: "What primitive behavior is closest to what I need?" No execution or dispatch framing is present.
- **Step 2** describes `find_recipe(...)` as searching "advisory recipes built from existing primitive nodes" and explicitly states "Recipes explain common compositions, but they are not execution paths."
- **Step 3** describes `plan_continuation(...)` as returning "an explain-only plan" and explicitly states "it never sets `selected_partner`."

The table of plan fields (lines 90–99 of the doc) confirms `selected_partner` is "Always `None`", `executes` is "Always `False`", and `automatic_partner_selection_allowed` is "Always `False`".

The architectural rule printed in the doc is unambiguous:

```
Use a fused RTDL primitive when it exactly expresses the work.
Use a partner only when your app explicitly chooses a continuation outside the primitive.
Never rely on hidden partner dispatch.
```

The framing throughout keeps RTDL as a primitive-inspection layer, not an app framework or silent dispatcher.

---

## Question 3: Do the public index links improve discoverability without frustrating normal learners with historical or release-report material?

**Finding: Pass with one version-label note.**

All seven index files add the workflow at appropriate learner entry points:

| Index file | Addition |
| --- | --- |
| `docs/learn/README.md` | Step 6 in the learner path, between the App/Example Quickstart and the Application Catalog |
| `docs/tutorials/README.md` | Step 6 in the tutorial table; also in the "Language Basics" learning track |
| `docs/app_example_quickstart.md` | Row in "Choose An App" (do-not-claim column is "execution, partner selection, or speedup"); row in "Choose An Example Type"; step 2 in the "Recommended Demo Path" |
| `docs/application_catalog.md` | Listed in the "Getting started" group under "Learner And Example Apps" and in the "Beginner Examples" table |
| `examples/README.md` | Row in "Start Here" table alongside hello-world |
| `examples/v2_0/README.md` | Second `PYTHONPATH=src:.` command example |
| `examples/v2_0/getting_started/README.md` | Explicit row in the file table |

None of the additions route learners toward historical material, release reports, or the tutorial archive. All links land in active learner sections.

**Version-label note:** `docs/tutorials/README.md` header still reads "teaches the current v2.6 released source tree" and the claim boundary section says "The v2.6 tutorial path teaches..." The workflow doc itself says "Status: v2.7 source-tree discovery workflow." This is a label inconsistency. It does not introduce a false claim (the tutorial track is v2.6; the new workflow step is a v2.7 addition to that track), but a reader following the label could be confused about which version the step belongs to. This does not block acceptance at the scope of this review.

---

## Question 4: Does wording avoid release readiness, package install, broad speedup, broad RT-core, true zero-copy, paper-reproduction, automatic Triton, and automatic partner-selection claims?

**Finding: Pass.**

`docs/learn/primitive_discovery_workflow.md` contains an explicit Boundaries section (lines 119–132) that names all eight forbidden claim categories verbatim:

> This workflow does not authorize:
> - release readiness;
> - package-install promises;
> - public speedup wording;
> - broad RT-core speedup wording;
> - true zero-copy wording;
> - automatic Triton or automatic partner selection;
> - paper-system reproduction claims;
> - app-specific native engine logic.

The example file embeds the same prohibition in the `claim_boundary` JSON field at runtime. The report doc (`docs/reports/goal3084_v2_7_primitive_discovery_workflow_docs_example_2026-06-03.md`) repeats the full list in its Boundaries section.

No performance numbers, speedup ratios, zero-copy assurances, or release-readiness statements appear anywhere in the new files. The `docs/tutorials/README.md` claim boundary section (pre-existing) lists the same prohibited wording patterns and does not add new ones.

---

## Question 5: Are the tests sufficient for this small learner workflow slice?

**Finding: Pass.**

`tests/goal3084_v2_7_primitive_discovery_workflow_docs_test.py` contains four tests proportionate to the scope:

1. **`test_primitive_discovery_workflow_example_runs`** — Runs the example as a subprocess, parses the JSON output, and asserts: `app`, `status`, `recipe_match.id`, `advisory_plan.recipe_id`, `selected_partner is None`, `executes is False`, `automatic_partner_selection_allowed is False`, `partner_options` is truthy, and `"performance wording" in claim_boundary`. This is the contract test for the entire metadata-only claim.

2. **`test_learn_doc_explains_three_step_workflow_and_boundaries`** — Reads the doc as text and checks for the three function names, "metadata-only", "selected_partner", `Always \`False\``, "does not authorize", and "automatic partner selection". This guards against doc drift.

3. **`test_public_indexes_link_workflow`** — Asserts all seven index paths contain "primitive_discovery" (case-insensitive). This prevents the workflow from being silently dropped from discoverability.

4. **`test_examples_alias_exports_workflow`** — Checks `examples.__all__` via a subprocess import. This verifies the backward-compat alias in `examples/__init__.py`.

One gap: `test_primitive_discovery_workflow_example_runs` checks only that `partner_options` is truthy, not that it contains the expected `unsupported_fail_closed` cell for the `partner="numba"` request. The report calls this cell out as the key pedagogical feature demonstrating no-auto-selection. Asserting the specific cell would make the contract more precise, but the current test is sufficient to confirm the no-execution, no-auto-selection invariants that matter for this review.

No test checks that linked doc files actually exist on disk. This is a low-risk omission given the index files are read by `test_public_indexes_link_workflow`.

Overall, the tests are proportionate and complete for a learner workflow docs slice.

---

## Summary

Goal3084 delivers a clean metadata-only primitive discovery workflow. The example, learner doc, index links, wording, and tests all stay within the metadata-only scope. The `partner="numba"` / `unsupported_fail_closed` pattern is the right teaching choice. The explicit Boundaries sections in the doc, the `claim_boundary` JSON field in the example output, and the contract assertions in the test suite together make the scope self-documenting.

Two minor items are noted but do not block acceptance:

1. `docs/tutorials/README.md` carries a v2.6 label in its header and claim boundary section while the workflow step is described as v2.7 in the learn doc. The label inconsistency does not introduce a false claim.
2. The `partner_options` assertion in `test_primitive_discovery_workflow_example_runs` checks only truthiness; it does not verify the specific `unsupported_fail_closed` cell content.

**Verdict: `accept-with-boundary`**

This review does not authorize release readiness, package-install wording, public speedup wording, broad RT-core wording, true zero-copy wording, automatic partner selection, automatic Triton selection, paper reproduction, or app-specific native engine logic. It authorizes only the metadata-only learner workflow described in the files listed above.
