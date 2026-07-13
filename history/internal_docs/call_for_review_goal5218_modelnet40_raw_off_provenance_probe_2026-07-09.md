# Call For Review: Goal5218 ModelNet40 Raw OFF Provenance Probe

Date: 2026-07-09

Please strictly review Goal5218.

Primary report:

```text
history/internal_docs/goal5218_modelnet40_raw_off_provenance_probe_result_2026-07-09.md
```

Evidence artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5218_modelnet40_glass_box_author_raw_off_probe_2026-07-09.json
```

## Context

The project needs to move beyond one Dragon -> HappyBuddha representative
workload toward broader X-HD paper reproduction. `ModelNet40` is attractive
because the author paper branch contains 400 ModelNet40 pair records and the
public dataset is officially downloadable.

Goal5218 tests whether public raw ModelNet40 OFF files can be directly used as
paper inputs.

## Key Evidence

Selected paper-branch pair:

```text
glass_box_0115.off -> glass_box_0081.off
author logged point counts = [1107, 1200]
paper-branch HDResult = 0.22594279050827026
```

Public raw OFF files from official `ModelNet40.zip`:

```text
glass_box_0115.off:
  vertex count = 1107
  SHA256 = 6a6d23cb9619c32f0c6a17082b450452f13facade3a998ed676de948c53a1b5f

glass_box_0081.off:
  vertex count = 1200
  SHA256 = d35c49cc061f73ec0211bd65c69177599a269300d1b915db1f9a36e523405048
```

Author binary on public raw OFF:

```text
HDResult = 1115.2059326171875
Running.AvgTime = 5.169 ms
Input counts = [1107, 1200]
```

## Requested Verdict Labels

Choose one:

```text
approve_goal5218_modelnet40_raw_off_not_exact_input
approve_with_required_amendments
revise_goal5218_before_using_modelnet40
block_due_to_missing_or_invalid_probe_evidence
```

## Review Questions

1. Does the evidence prove that the public raw OFF vertex counts match the
   author paper-branch logged counts for the selected pair?

2. Does the author binary result on public raw OFF fail to match the paper-log
   HDResult by a large margin?

3. Is it correct to conclude that public raw ModelNet40 OFF files cannot yet be
   treated as exact paper inputs?

4. Does the report avoid claiming ModelNet40 paper reproduction or RTDL
   correctness/performance on ModelNet40?

5. Is the next recommendation correct: inspect author preprocessing /
   normalization before trying an RTDL ModelNet40 route?

6. Are there any missing facts required before this probe can be used as
   dataset-provenance evidence?

## Expected Answer Shape

```text
Verdict:
<one requested verdict label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
6. ...
```

## Non-Authorization Boundary

This review must not authorize:

```text
ModelNet40 exact paper input found;
ModelNet40 paper reproduction complete;
public raw OFF equals author input;
RTDL ModelNet40 correctness/performance claim;
author-vs-RTDL ratio.
```
