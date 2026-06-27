# Call For Review - Phoenix V3 M27 LibRTS AABB Set-B Triage And Cold OptiX Retain Fix

Date: 2026-06-23

Reviewer requested: Claude

Requested verdict label, choose one:

- `accept_with_boundary`
- `partial_not_closed`
- `reject`

## Context

M26 consensus required M27 to:

1. First triage the Embree 32768 stress regression.
2. Then attempt a bounded repair for the strict cold single-shot OptiX row.
3. Avoid all-app.

Review target:

```text
docs/reports/phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2026-06-23.md
```

Relevant code/test:

```text
examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py
tests/v3_phoenix_librts_aabb_count_runner_test.py
```

Evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m27_librts_embree_stress_triage_20260623_130838
docs/rebuild/v3/evidence/phoenix_v3_m27_optix_cold_retain_probe_20260623_131411
docs/rebuild/v3/evidence/phoenix_v3_m27_librts_optix_cold_retain_fix_ab_20260623_131633
docs/rebuild/v3/evidence/phoenix_v3_m27_librts_optix_cold_retain_fix_ab_extra_20260623_131735
```

## Summary Of M27 Findings

Embree 32768 stress triage:

```text
sample ratios current/V2.14: 1.131x, 0.898x, 0.911x
geomean: 0.975x
2 of 3 samples below 0.950x
```

OptiX retain probe:

```text
retain_repeat_outputs=true median query: 0.312370911s
retain_repeat_outputs=false median query: 0.263605766s
direct runner improvement: about 1.185x
```

Patched strict cold OptiX A/B:

```text
8 sample ratios current/V2.14:
0.531x, 1.231x, 1.174x, 1.013x, 0.883x, 0.977x, 1.077x, 1.110x
geomean: 0.973x
median sample ratio: 1.045x
pass count >=0.950x: 6/8
```

Code change:

```text
query_repeat == 1  -> retain_repeat_outputs=False
query_repeat > 1   -> retain_repeat_outputs=True
```

## Questions For Review

1. Is the single-repeat `retain_repeat_outputs=False` change technically sound and generic enough to keep?
2. Does M27 close the strict cold OptiX row with boundary, or is it still `partial_not_closed` because of outliers?
3. Should the Embree 32768 result be logged as a deterministic blocker, a stability watch blocker, or an accepted explanation-only row?
4. Is the 43-test local/POD coverage enough for this bounded code change?
5. Should M28 proceed to true Set-A runtime trunk work, or should more focused POD time be spent on cold/stability controls first?
6. Does this packet authorize release, all-app, public speedup wording, broad V3-over-V2 wording, or V4/external zero-copy/embedding scope?

## Codex Initial Recommendation

`accept_with_boundary` for the code fix, but **not** unconditional closure of Set-B controls.

Reason:

- The code change is generic and removes unnecessary output retention for single measured runs.
- Typical OptiX cold behavior crosses threshold by geomean and median sample ratio.
- Outliers remain, so release wording and all-app remain unauthorized.
- Embree 32768 should be logged as a stability watch blocker.

## Required Non-Authorization Block

Unless your review explicitly says otherwise, this packet does not authorize:

- V3 release.
- Full all-app rerun.
- Public speedup wording.
- Broad "V3 is faster than V2.x" wording.
- Hiding the OptiX outliers.
- Hiding the Embree variance.
- Counting LibRTS AABB single-shot as Set A.
- V4/external zero-copy/embedding claims.
