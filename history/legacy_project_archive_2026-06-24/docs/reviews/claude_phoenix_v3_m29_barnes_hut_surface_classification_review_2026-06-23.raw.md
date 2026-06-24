Review written to `docs/reviews/claude_phoenix_v3_m29_barnes_hut_surface_classification_review_2026-06-23.raw.md`.

---

## Summary

**Verdict: `approve_with_amendments`**

**One required amendment, no blocking findings.**

### Required Amendment

M28 amendment 3 — "generic" scoped to API design, not multi-app coverage — is not explicitly carried in the M29 `summary.json` `m28_carry_forward` block or the report prose. Amendments 1, 2, and 4 are carried correctly. Fix: add a `generic_scope_note` key to `m28_carry_forward` in `summary.json` (and mirror in the report) stating that "generic" in the M28 freeze is API-design scope only.

### Six Questions

1. **Classification supported by evidence?** Yes. The `summary.json` directly confirms the `mode_presence` and `function_presence` values that produce `v2_14_has_cpu_fused_or_typed_stream_only` via the classifier's decision tree. No discrepancy.

2. **Correct to stop after classification?** Yes. No same-contract v2.14 CUDA surface exists to time against; running CPU fused rows vs. the current CUDA runner would be a different-contract comparison — the exact overclaim M28 forbids.

3. **No false same-contract speedup claim?** Yes. No ratio or speedup number appears. The report explicitly states there is no equivalent v2.14 surface to compare against.

4. **Dirty working tree handled adequately?** Yes, adequately. The modified file (`scripts/goal2626_benchmark_embree_optix_baseline.py`) is not among the classified files; the relevant-file clean check (`git diff -- <relevant files>` returning `0`) is valid. Minor non-blocking gap: the check is human-attested rather than enforced inside the classifier script.

5. **M28 amendments carried forward?** 3 of 4 explicitly. Amendment 3 (generic scope) is missing — the required amendment above.

6. **Supports M30, all-app still forbidden?** Yes. One Set-A family frozen. Two required before all-app. M30 may proceed to RTDBSCAN or RTNN.
e |
| `fused_frontier_force_sum_bucketized_cpu` | **true** | true |
| `grouped_vector_sum_typed_stream_plan` | **true** | true |
| `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session` | false | true |

The classifier logic is correct:

1. Current surface present check passes (`prepared_execution_fused_vector_sum_numba_cuda`
   and `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session` are
   both true in current) — no `blocked_current_surface_missing` result.
2. v2.14 does not have `prepared_execution_fused_vector_sum_numba_cuda` or
   `fused_frontier_force_sum_bucketized_numba_cuda` — no
   `v2_14_has_equivalent_fused_surface` result.
3. v2.14 has `fused_frontier_force_sum_bucketized_cpu` and
   `grouped_vector_sum_typed_stream_plan` — classification is
   `v2_14_has_cpu_fused_or_typed_stream_only`. Correct.

The v2.14 mode list (22 modes) is consistent with the expected v2.14 state.
The current mode list (30 modes) contains the additional CUDA/prepared routes
expected from a V3 build. The SHA-256 hashes confirm the two trees are distinct
files. No discrepancy between the report's surface matrix and the `summary.json`
`mode_presence` fields.

### Q2. Is it correct not to run additional timing rows after this classification?

Yes. The classification establishes that v2.14 has no Numba CUDA fused route and
no prepared-execution session runner for aggregate-tree fused weighted-vector sum.
There is therefore no same-contract v2.14 surface to time against the current
Numba CUDA runner. Running v2.14 CPU fused rows or node-coverage rows against the
current CUDA runner would be a different-contract comparison and would constitute
exactly the overclaim M28 forbids. The decision to stop at classification is
correct.

The M28 runner/control timing evidence (geomean `0.999328x`, all rows above
`0.998x`) remains valid for the Set-A family freeze and does not need re-running
as a consequence of M29.

### Q3. Does the report avoid falsely claiming same-contract V3-over-v2.14 speedup?

Yes. The report states explicitly: "M29 therefore authorizes no same-contract
V3-over-v2.14 speedup claim for the current Barnes-Hut Numba CUDA fused runner.
There is no equivalent v2.14 current runner surface to time against." The
interpretation section and non-authorization block reinforce this. No speedup
number or ratio appears anywhere in the M29 report. The only number referenced
is the M28 runner/control geomean (`0.999328x`), which is not a V3-over-v2.14
speedup claim.

### Q4. Is the dirty v2.14 working tree handled adequately by the relevant-file clean check?

Adequately, with a minor transparency gap noted.

The v2.14 working tree has:
- `M scripts/goal2626_benchmark_embree_optix_baseline.py` — modified under
  `scripts/`, not a Barnes-Hut app or prepared_execution source file.
- `?? data/` — untracked data directory.

Neither modified file is among the two relevant classification files:
- `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `src/rtdsl/prepared_execution.py`

The report claims `git diff -- <relevant files> | wc -c` returned `0`, and the
`summary.json` SHA-256 hashes for both files are present and consistent with a
clean read. This is adequate for accepting the classification.

Minor transparency gap (non-blocking): the relevant-file clean check is a
human-attested command result reported in the prose section, not a
machine-enforced gate within the classifier script itself. The classifier reads
file contents directly without asserting the relevant files are at their
committed state. The classification result is correct, but future classifiers
should enforce this precondition internally rather than relying on out-of-band
attestation.

### Q5. Does M29 properly carry forward the M28 amendments about `runtime_sourced_material_gain`, skipped validation, "generic" scope, and `git_commit: null` provenance?

Three of four amendments are carried correctly. The fourth is absent (see
Required Amendments above).

- **Amendment 1** (`runtime_sourced_material_gain: true` scoped to historical
  OptiX/frontier displacement): carried correctly. Both `summary.json`
  `m28_carry_forward.runtime_sourced_material_gain_true_scope` and the report's
  Carry-Forward Boundaries section state this explicitly.

- **Amendment 2** (`validation_skipped: true` explained as per-row CPU/oracle
  validation skipped for serious rows): carried correctly. The
  `m28_carry_forward.validation_skipped_scope` field in `summary.json` and the
  report's Carry-Forward Boundaries section both address it.

- **Amendment 3** ("generic" scoped to API design, not multi-app coverage):
  **not carried explicitly**. Neither the `summary.json` `m28_carry_forward`
  block nor the report prose contains a reference to this amendment. M29 makes
  no genericity claim itself, so there is no active overclaim, but the
  documentation trail is incomplete. This is the required amendment.

- **Amendment 4** (`git_commit: null` remote provenance caveat): carried
  correctly. The `m28_carry_forward` block records
  `m28_remote_execution_git_commit: null` with reason. The report's Provenance
  section also states the caveat explicitly and references the M28 precedent.

### Q6. Does this result support moving to M30 for the second Set-A family, while keeping all-app forbidden?

Yes. M29 confirms Barnes-Hut aggregate-tree fused weighted-vector sum is a
capability addition in V3 (not a same-contract speedup over v2.14), and that
the M28 runner/control evidence for the first Set-A family freeze stands intact.

One Set-A family is frozen. The two-family requirement for all-app timing is not
yet met. All-app timing remains correctly forbidden.

M30 may proceed to probe a second Set-A candidate (RTDBSCAN or RTNN as
suggested in the report's Next Step section). The M30 scope must follow the same
constraints: focused POD evidence, no all-app, no public speedup claim, no broad
V3-over-V2 claim, no release wording.

---

## Additional Observations (Non-Blocking)

**Classifier `mode_presence` fallback.** The expression
`name in modes or name in app_text` uses a raw string search over the full
source text as a fallback when a mode name is not found via AST parse of the
`MODES` tuple. For short mode names this could produce false positives (comments,
string literals, etc.). All mode names in play are long and specific enough that
this is not a practical risk at the current mode set, but it is a latent
fragility if mode names become shorter or more generic in future classifiers.

**`v2_8_grouped_vector_sum_plan` in `MODE_NAMES` but not in `classify()` branching.**
This mode is tracked in `mode_presence` but plays no role in the classification
decision tree. This is correct as an informational field. It is not a bug.

**Surface matrix in report vs. `summary.json`.** The M29 report surface matrix
presents eight rows matching the eight keys in `summary.json` `mode_presence`
plus the `function_presence` entry. The matrix is correct and consistent with
the evidence. No discrepancy found.

---

## Non-Authorization

This review authorizes no Phoenix V3 release, no all-app run, no public speedup
claim, no broad V3-over-V2 claim, no RT-core speedup claim, no true-zero-copy
claim, and no V4 work.

This review is not a release gate, not a performance endorsement, and not a
claim about the correctness or quality of the rtdl codebase beyond the scope of
the M29 classification packet reviewed above.
