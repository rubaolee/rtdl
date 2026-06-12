# Goal4315: Claude Review — Goal4314 And Goal4312 Follow-Up Fixes

Date: 2026-06-11
Reviewer: Claude (Sonnet 4.6)
Scope: read-only review; no source files edited.

## Verdict

`accept-with-boundary` for all three slices.

Goal4314 (claim-boundary canonicalization), the Goal4312 F-N1/F-N2 runner fixes,
and the F-N3 RTNN Embree output fix each close a discrete gap without expanding
any public claim or authorizing release.

---

## Q1 — Does Goal4314 Reduce Learner-Doc Drift Without Expanding The Boundary?

**Finding: pass.**

Goal4314 adds `docs/learn/current_claim_boundaries.md` and links it from seven
front-door files. The canonical page contains no new claims; it consolidates
boundary wording that was already present across individual docs. The test
(`test_public_front_doors_link_to_canonical_boundary`) enumerates all seven
expected link locations and checks each with `subTest`, so a missing link will
be reported precisely rather than silently ignored.

The report (`goal4314_current_claim_boundary_canonicalization_2026-06-11.md`)
correctly describes the work as documentation structure, not a boundary expansion,
and repeats the full negative-authorization list.

No drift-introducing change found in the canonical page or its linked text.

---

## Q2 — Is `docs/learn/current_claim_boundaries.md` Clear And Correctly Conservative?

**Finding: pass.**

The page is the right length for a first-read boundary reference: short enough
that a new learner will finish it, specific enough that the negative list is
unambiguous.

Positive observations:

- The v2.10 / v2.11 boundary is stated at the top of the document and in the
  first section ("Active v2.11 work may appear in reports and tests, but it is
  internal engineering evidence until a reviewed release packet says otherwise").
  A learner reading only the first section gets the right mental model.
- The "What RTDL Claims" section gives the full naming requirement (primitive,
  backend, partner, hardware, command shape, output contract, reviewed artifact
  path) in a scannable bulleted form.
- The "What RTDL Does Not Claim" negative list covers all eight blocked claim
  categories tested by the public scan.
- The OptiX note ("Selecting `--backend optix` means the OptiX backend was
  selected. It is not by itself a public RT-core speedup claim.") directly
  answers the most likely misreading.
- The Partner Rule section is appropriately scoped: it names the two promoted
  partners and draws user-owned code back to the user without over-claiming.

One minor gap: the "What RTDL Does Not Claim" bullet list does not explicitly
name `release` or `app-specific native-engine logic` as blocked items. Both are
present in the per-doc boundary sections and in the runner's FORBIDDEN_TRUE_FLAGS
list, so the omission is not a correctness issue, but a future revision could
add them for completeness. This is a style note, not a blocker.

---

## Q3 — Does The Public-Doc Claim Scan Still Cover The Canonical Page And Preserve Zero Hard Blockers?

**Finding: pass.**

The artifact (`goal4248_current_public_docs_claim_boundary_scan.json`) records:

- `status: pass`
- `hard_blocker_count: 0`
- `public_file_count: 34`
- `docs/learn/current_claim_boundaries.md` is present in `public_files_scanned`
- All ten `claim_boundary` flags are `false`

The canonical page's own boundary wording (package-install, automatic partner
selection, broad RT-core acceleration, whole-application speedup, paper
reproduction, speedup, etc.) is classified as `accepted_boundary_or_negative_context`
in the finding list — correctly, because those phrases appear in negative or
boundary-marking sentences.

The live-scan test (`test_live_scan_matches_pass_boundary`) re-runs the scanner
against the current tree, so a future commit that introduces a hard blocker will
be caught immediately rather than only at the next artifact refresh.

---

## Q4 — Do The Goal4312 Follow-Up Changes Properly Address F-N1, F-N2, And F-N3?

### F-N1 — Missing stdout/path cases now have `metric_resolution_status`

**Finding: pass.**

The `_evaluate_hot_path_floor` function in
`scripts/goal3828_current_benchmark_scale_profile_runner.py` now initializes
`metric_resolution_status = "stdout_json_missing_or_unparseable"` before
attempting to parse the stdout file. The resolution path then sets it to one of:

- `"metric_numeric"` — resolved to a `float` or `int`
- `"metric_path_missing"` — JSON parsed but dotted path returned `None`
- `"metric_not_numeric"` — JSON parsed, path found, but value is not numeric

The test `test_runtime_floor_evaluation_distinguishes_missing_metric_causes`
exercises both the missing-file case (no file written) and the missing-path case
(file exists but key absent) and asserts the correct `metric_resolution_status`
for each. The `status` field in both cases becomes `"metric_not_numeric"` (the
claim-blocking status) while `metric_resolution_status` records the distinct
cause. This is the right split: a reader of the artifact can diagnose why the
metric did not resolve without the diagnostic field itself relaxing the
claim-blocking status.

### F-N2 — Dry-run summary status is `dry_run_policy_only_no_runtime_evaluation`

**Finding: pass.**

`_summarize_hot_path_floor` now has an explicit `dry_run` parameter. When
`dry_run=True` the summary status is set to
`"dry_run_policy_only_no_runtime_evaluation"` rather than falling through to
`"accept"`. The test `test_runner_dry_run_exposes_floor_policy_for_all_ten_rows`
(line 122) explicitly checks this status string, so a regression would be caught
immediately. The status string is long enough to be unambiguous in any artifact
inspection — no reader could confuse it with a runtime floor-met result.

The report documents the change and names the two targeted floor rows, which is
useful for understanding the next pod requirement.

### F-N3 — RTNN Embree output removes inherited `optix_performance`, keeps `rt_path_note`

**Finding: pass.**

The `ann_embree_quality_payload` function (lines 140–170 of
`rtdl_rtnn_benchmark_app.py`) now does:

```python
inherited_optix_note = payload.pop("optix_performance", None)
return {
    ...
    "rt_path_note": inherited_optix_note,
    "inherited_ann_optix_performance_note_present": inherited_optix_note is not None,
    ...
}
```

The key `optix_performance` is popped before the dict spread, so it cannot
appear in the output even if the upstream `ann_app.run_app` adds additional keys
in the same dict. The `rt_path_note` field re-exposes the content under a name
that is clearly scoped to RT path description, not to OptiX performance claims.
The `inherited_ann_optix_performance_note_present` flag allows tests to assert
the upstream note was present, which confirms the pop did meaningful work rather
than quietly removing nothing.

The Linux artifact (`goal4308_rtnn_embree_front_door_local_linux.json`) confirms
the fix at runtime: `stdout_tail` contains `"rt_path_note": {...}` and no
`optix_performance` key. The test at line 64–65 re-asserts this from the
persisted artifact, providing a regression guard that survives across machines.

One note: `inherited_ann_optix_performance_note_present: True` in the artifact
confirms the upstream did emit `optix_performance`. If the upstream ever stops
emitting that key the flag goes `False` and the test at line 38 (`assertTrue`)
will fail. That is the correct behavior — it alerts maintainers that the
upstream changed and the pop may no longer be doing its job.

---

## Q5 — Are Claim Boundaries Still Blocked?

**Finding: pass — all required boundaries remain blocked.**

Evidence:

| Boundary | Blocked by |
|---|---|
| Release | `release_authorized: false` in runner top-level output; FORBIDDEN_TRUE_FLAGS list |
| Public speedup wording | All 10 claim_boundary flags false in scan; runner explicit flag |
| Broad RT-core wording | Scan flag `broad_rt_core_claim_authorized: false`; RTNN app CLAIM_BOUNDARY |
| Package-install wording | Scan negative-context classification; canonical page bullet |
| Automatic partner selection | Scan flag; RTNN app claim_boundary; canonical page bullet |
| True-zero-copy wording | RTNN app claim_boundary flags; runner FORBIDDEN_TRUE_FLAGS |
| Paper reproduction | Scan flag; RTNN CLAIM_BOUNDARY `full_rtnn_paper_reproduction: False` |
| App-specific native-engine logic | `app_specific_native_engine_logic_allowed` in FORBIDDEN_TRUE_FLAGS |
| AMD/Intel GPU performance | Scan flag `amd_performance_claim_authorized`; runner list |
| Whole-app speedup | Scan flag; multiple per-doc boundary sections |

The public scan's `_find_forbidden_true_flags` recursively walks the entire
output payload, so a claim flag buried inside a nested dict would still be caught.
The FORBIDDEN_TRUE_FLAGS list in the runner is the definitive guard for runner
artifacts; the scan covers the documentation surface.

No path that would authorize any of these claims was found in the reviewed files.

---

## Summary

All five review questions pass. The three goals collectively:

1. give learners a single short entry point for claim rules (Goal4314);
2. make per-row floor diagnostics more precise for both pod runs and dry-run
   policy checks (Goal4311 follow-up, F-N1 and F-N2);
3. remove a key from the RTNN Embree output that could have been misread as
   OptiX performance evidence (F-N3).

None of these changes authorize release, public speedup wording, paper
reproduction, broad RT-core claims, or any of the other blocked categories.
The next required step remains a fresh ten-app scale-profile pod packet with the
updated runner so floor evaluations are populated from real runtime output.
