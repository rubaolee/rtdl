# Call For Review - Goal5319 X-HD Graphics Exact-Provenance Search

Please strictly review Goal5319.

## Files Under Review

Primary files:

```text
history/internal_docs/goal5319_xhd_graphics_exact_provenance_search_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
tests/goal5319_xhd_graphics_exact_provenance_search_test.py
```

Context files:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5297_dataset_acquisition_manifest_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5316_figure5_level_b_status_matrix.json
Paper-reproduction-apps/x-hd-paper/data/external/stanford/README.md
```

## Requested Review Focus

This is a provenance search, not a performance goal.

Please attack especially:

1. Whether Goal5319 correctly refuses to promote public Stanford files to exact
   paper inputs.
2. Whether public archive/file hashes are correctly treated as local
   same-source evidence rather than author hash evidence.
3. Whether app-owned `1e-3` scaled files are correctly kept below author
   preprocessing proof.
4. Whether pair status is accurately summarized: three Level-B value matches
   and one Dragon->Asian author-value no-go.
5. Whether the tests protect against the tempting but invalid "public Stanford
   equals exact author HDDatasets" claim.

## Expected Answer Shape

Please answer in this shape:

```text
Verdict:
  approve_goal5319_graphics_exact_provenance_not_found_keep_level_b
  OR revise_goal5319_...
  OR block_goal5319_...

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Review questions:
  1. Does Goal5319 preserve the strong graphics Level-B evidence without
     overstating it as exact paper input recovery?
  2. Are public Stanford archive and extracted-file hashes carried forward
     correctly?
  3. Are those hashes correctly classified as public-source hashes, not author
     HDDatasets hashes?
  4. Are author paper-log basenames and point counts correctly treated as
     necessary but insufficient for exact input identity?
  5. Are app-owned scaled AsianDragon / ThaiStatuette files correctly kept as
     Level-B candidates rather than author preprocessing proof?
  6. Is Dragon->Asian correctly retained as an author-value no-go under the
     current public/scaled mapping?
  7. Is Dragon->HappyBuddha correctly described as the strongest current
     graphics Level-B row, with global-bound early-break / approximate witness
     caveat retained?
  8. Does the test suite lock both positive evidence and negative exact-claim
     boundaries?
  9. Should the next work remain external provenance / preprocessing search
     rather than more Dragon->Asian RTDL timing?
  10. Does this goal avoid any author-vs-RTDL performance ratio or Figure-5
      completion claim?
```

## Claim Boundary To Preserve

Allowed:

```text
Three graphics public/same-source candidates value-match author paper logs.
RTDL matches author reruns for the tested matched graphics routes.
Public Stanford archive/file hashes are recorded as local public-source evidence.
Dragon->Asian remains a no-go under the current public/scaled mapping.
```

Forbidden:

```text
Public Stanford graphics files are proven byte-identical to author HDDatasets inputs.
The app-owned scaled AsianDragon/ThaiStatuette files are proven author preprocessing outputs.
All four Figure-5 graphics pairs are value-matched.
Figure 5 graphics is reproduced exactly.
Author-vs-RTDL graphics performance ratio is authorized.
```

## Requested Verdict Label

If approved, please use:

```text
approve_goal5319_graphics_exact_provenance_not_found_keep_level_b
```
