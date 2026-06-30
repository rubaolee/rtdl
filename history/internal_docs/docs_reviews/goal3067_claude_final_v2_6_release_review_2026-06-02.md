# Goal3067 Claude Final v2.6 Release Review

Date: 2026-06-02

Reviewer: Claude (claude-sonnet-4-6)

Status: final release review for Goal3066 v2.6 release action. This review is
one input to the final 3-AI release consensus before the `v2.6` tag is created.

## Scope

Read-only review of the Goal3066 release action artifacts:

- `VERSION`
- `README.md` and `docs/README.md` (front-door docs)
- `docs/release_reports/v2_6/README.md` (release package)
- `docs/reports/goal3066_v2_6_release_action_2026-06-02.md` (action record)
- `tests/goal3066_v2_6_release_action_test.py` (gate test)
- `docs/reports/goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md`
- `docs/reports/goal3061_v2_6_doc_total_audit_3ai_consensus_2026-06-02.md`
- `docs/reports/goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.md`
- `docs/reports/goal3065_v2_6_native_tutorial_validation_3ai_consensus_2026-06-02.md`

## Review Question Answers

### 1. Does `VERSION` now correctly read `v2.6`?

**Yes.** `VERSION` contains exactly `v2.6` with no trailing qualifier. The gate
test `test_version_marker_is_v2_6` asserts this directly, and the test suite
passed with `Ran 18 tests in 0.733s / OK`.

### 2. Do the current learner/front-door docs describe v2.6 as released rather than release-candidate/pre-release?

**Yes.** Both primary front-door documents use released language:

- `README.md` line 14: "This documentation is written for the v2.6 released
  RTDL surface"
- `docs/README.md` line 15–16: "Current status: RTDL v2.6 is the released
  source-tree Python+partner+RTDL app-portfolio surface."

Neither document contains "release-candidate", "release candidate", or
"pre-release". The gate test `test_front_door_docs_now_name_current_release`
checks all eleven `CURRENT_PUBLIC_DOCS` entries for exactly this condition.
The broader scan `test_current_docs_no_longer_expose_candidate_status` sweeps
the entire current-facing doc tree for six forbidden stale phrases; both tests
passed.

### 3. Does the v2.6 release package stay source-tree-only and evidence-linked?

**Yes.** `docs/release_reports/v2_6/README.md` explicitly states:

- `PYTHONPATH=src:.` is the usage model throughout the smoke commands
- "not a package-install release"
- "not a broad RT-core speedup claim"
- "not a whole-application speedup claim"
- "user-chosen partner guidance for CuPy and Numba continuations"

The package links all four consensus evidence reports (Goal3058, Goal3061,
Goal3062, Goal3065). The gate test `test_release_package_is_source_tree_only_and_evidence_linked`
verifies each of these strings and evidence pointers are present.

### 4. Are the release boundaries still intact?

**Yes.** The "What v2.6 Does Not Claim" section of the release package
explicitly lists all five required negatives:

| Boundary | Location | Status |
| --- | --- | --- |
| No package-install claim | release README "not a package-install release"; `README.md` explicit warning; Goal3066 action record | intact |
| No broad RT-core / whole-app speedup claim | release README "No universal speedup claim is made for backend flags such as `--backend optix`"; README.md Performance Boundary section | intact |
| No arbitrary partner acceleration claim | release README "No arbitrary PyTorch, CuPy, Numba, or Triton acceleration claim is made"; partner boundary docs | intact |
| No automatic partner-selection claim | release README "No automatic partner-selection claim is made"; Goal3066 action record explicitly calls this out: "automatic partner selection remains outside the release claim" | intact |
| No general zero-copy / device-residency claim | release README "No general zero-copy/device-residency product claim is made"; prior audit corrected true-zero-copy phrasing throughout current docs | intact |

### 5. Does the final gate test protect the release wording and current-doc candidate cleanup?

**Yes.** `tests/goal3066_v2_6_release_action_test.py` provides six targeted
tests:

| Test | What it guards |
| --- | --- |
| `test_version_marker_is_v2_6` | VERSION equals "v2.6" exactly |
| `test_release_action_records_authorized_boundary` | action report contains user-authorized status, tag intent, package-install denial, automatic-partner-selection denial, and Goal3065 reference |
| `test_front_door_docs_now_name_current_release` | eleven current public docs contain "v2.6" and are free of "release-candidate", "release candidate", and "pre-release" |
| `test_current_docs_no_longer_expose_candidate_status` | full current-facing doc tree is free of six forbidden stale phrases, including "release-prep" and "current v2.3 release" |
| `test_release_package_is_source_tree_only_and_evidence_linked` | release README contains version marker, PYTHONPATH usage, all five boundary denials, and all four evidence-report references |
| `test_protected_local_files_are_named_for_exclusion` | action report names all five protected local artifacts |

The test exclusion list (`EXCLUDED_CURRENT_PREFIXES`) correctly carves out
history, reports, reviews, handoff, audit, release\_reports, directives,
engineering, research/archive, generated, internal, legacy, and reference
directories so that the stale-wording scan operates only on the current-facing
surface.

The combined suite of 18 tests (Goal3066 + Goal3065 + Goal3062 + Goal3061
slices) passed in 0.733s as reported by Codex.

### 6. Is it acceptable to proceed to final 3-AI release consensus and then tag the committed tree as `v2.6`?

**Yes.** All prior gates are closed:

| Gate | Consensus record | Verdict |
| --- | --- | --- |
| Documentation total audit (86 current-facing files; 16 archived research files; 103 links / 0 broken; portable smoke OK) | Goal3061 | `accept-with-boundary` (3-AI) |
| Native tutorial / example pod validation (21/21 pass: portable Python, CPU reference, Embree, OptiX/RT, CuPy-CUDA) | Goal3065 | `accept-with-boundary` (3-AI) |
| Release action (VERSION bump, release package, front-door doc update, gate test, 18 tests OK) | Goal3066 (this review) | see below |

User authorization is on record in Goal3066: "The user explicitly authorized
the v2.6 release."

The committed tree presents a single coherent v2.6 released surface with no
stale release-candidate or pre-release claims remaining in current-facing docs.
All five claim boundaries are explicit in the release package, the front-door
README, and the gate tests. The only remaining action is creating the `v2.6`
tag after the final 3-AI consensus record is complete.

## Observations

No blocking issues found. Two minor structural observations for the record (not
blocking):

1. The `docs/release_reports/v2_6/README.md` lists benchmark app boundaries as
   a table scoped to the ten benchmark apps. These boundaries are consistent
   with the language in the individual benchmark READMEs audited under Goal3058.

2. The protected-local-files list in the Goal3066 action record covers five
   artifacts (`docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`,
   `id_ed25519_rtdl_codex`, `rtdl_v0_4.tar.gz`, `scratch/`, `Lib/`). The
   untracked `Lib/` directory visible in git status is consistent with this
   exclusion intent.

## Verdict

`accept-with-boundary`

The Goal3066 release action is a valid v2.6 release record. The committed tree
may be tagged `v2.6` after the final 3-AI release consensus is complete. The
five claim boundaries — no package-install, no broad RT-core/whole-app speedup,
no arbitrary partner acceleration, no automatic partner selection, no general
zero-copy/device-residency — must remain explicit in any downstream publication
or communication derived from this release.
