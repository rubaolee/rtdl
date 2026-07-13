# Call For Review - Goal5298 X-HD Author-Only Graphics Level-B Precheck

Please strictly review Goal5298.

## Files

```text
history/internal_docs/goal5298_xhd_author_graphics_precheck_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/dragon_happy_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/dragon_asian_scaled_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/thai_happy_scaled_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5298_raw/thai_asian_scaled_author.json
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5298_author_graphics_precheck.py
tests/goal5298_xhd_author_graphics_precheck_test.py
```

## Context

Goal5297 found:

```text
The current POD is usable.
/local/storage/shared/HDDatasets is missing.
The local workspace has public Stanford graphics candidates for Dragon,
HappyBuddha, AsianDragon, and ThaiStatuette.
Those files can support Level-B same-source diagnostics after upload, but not
exact paper dataset claims.
```

Goal5298 uploads the missing public Stanford graphics files to the current POD
and runs author `hd_exec` only. It does not run RTDL.

## What Happened

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
```

Uploaded / consolidated data under:

```text
/tmp/xhd_goal5298/data
```

Remote SHA256 values matched the Goal5297 local manifest for:

```text
dragon.ply
happy_buddha.ply
asian_dragon.ply
asian_dragon_scaled_1e-3.ply
thai_statuette.ply
thai_statuette_scaled_1e-3.ply
```

Author-only matrix:

```text
case                  author HDResult        paper-log HDResult      abs diff        matched
dragon_happy          0.12572988867759705    0.12572969496250153    1.937e-7       true
dragon_asian_scaled   0.06545527279376984    0.06536811590194702    8.716e-5       false
thai_happy_scaled     0.21912431716918945    0.21912434697151184    2.980e-8       true
thai_asian_scaled     0.28763842582702637    0.28763845562934875    2.980e-8       true
```

Summary:

```text
matched_paper_log_value_count = 3 / 4
all_cases_matched_paper_log_value = false
```

## Review Questions

1. Does the evidence support that the missing public Stanford graphics files
   were uploaded to the current POD and hash-matched the local Goal5297
   manifest?
2. Is the author-only command shape appropriate for a Level-B value precheck
   (`hd_exec`, `variant=rt`, `execution=gpu`, `input_type=ply`,
   `normalize=false`, `lb=256`, `repeat=1`)?
3. Does the matrix correctly show that Dragon->HappyBuddha,
   ThaiStatuette-scaled->HappyBuddha, and
   ThaiStatuette-scaled->AsianDragon-scaled match the paper-branch author-log
   HDResult within `1e-6`?
4. Does the matrix correctly preserve Dragon->AsianDragon-scaled as a no-go
   because its current author rerun differs from the paper-log target by
   approximately `8.7e-5`?
5. Is it correct that Goal5298 is author-only evidence and should not be read
   as RTDL comparison, Figure 5/7/8/10 reproduction, exact dataset
   reproduction, or performance-ratio evidence?
6. Is the next-step recommendation correct: use the three value-matched cases
   as Level-B graphics candidates, but keep Dragon->AsianDragon out of
   value-matched claims unless better provenance appears?
7. Are the tests sufficient for this goal stage, especially the checks that
   `matched_paper_log_value_count == 3`, Dragon->Asian remains unmatched, and
   all claim-boundary flags stay false for RTDL/performance/figure/full-paper
   claims?

## Expected Verdict Labels

```text
approve_goal5298_author_graphics_precheck__three_of_four_level_b_value_matched
revise_goal5298_claim_boundary_or_case_mapping
block_goal5298_due_to_incorrect_author_value_or_upload_evidence
```
