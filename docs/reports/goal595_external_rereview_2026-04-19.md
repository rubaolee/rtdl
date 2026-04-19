# Goal595 External Re-Review

**Date:** 2026-04-19
**Verdict:** ACCEPT

---

## Summary

Both BLOCK items from the original review have been remediated. The harness now computes and reports coefficient of variation, emits a CV-gated stability flag per backend/workload cell, and explicitly labels all unstable medians as engineering-triage evidence. The re-run artifacts were produced with warmups=5 and repeats=20 as required. All apple_rt cells remain unstable, but that instability is now accurately captured and no public speedup claim is made anywhere in the report.

---

## Remediation checklist

### Critical (original BLOCK 1): `ray_triangle_closest_hit_3d` apple_rt variance was non-repeatable, no flagging

**Status: Remediated.**

The harness (`_stats`, `_measure`) now computes CV and sets `stable: bool(cv <= cv_threshold)`. The markdown table has an explicit `Stability` column. All unstable backend/workload pairs are collected in `unstable_results` and rendered in a `Stability Warnings` section with per-cell CV values.

The re-run result:

| Workload | apple_rt CV | Stable? |
| --- | ---: | --- |
| `ray_triangle_closest_hit_3d` | 0.895 | False |
| `ray_triangle_hit_count_3d` | 0.243 | False |
| `segment_intersection_2d` | 0.267 | False |

All three apple_rt results are correctly flagged `False`. The original review said "if outliers persist, the workload is not ready for baselining under current Apple RT state." The harness now handles that case correctly: the medians are preserved as triage data, not as public claims.

### Minor (original BLOCK 2): no CV gate — harness would write output without flagging instability

**Status: Remediated.**

`_measure` computes CV and returns a `stable` field. `run_harness` accumulates every unstable pair into `payload["unstable_results"]`. `render_markdown` renders the `Stability` column and the `Stability Warnings` block. The `Interpretation` section reads:

> "If any backend/workload cell is marked unstable, its median is evidence for engineering triage only and must not be used as public speedup wording."

This satisfies the requirement.

---

## Data observations (informational, not blocking)

1. **All three apple_rt cells are now unstable**, vs one in the original run. The `hit_count_3d` and `segment_intersection_2d` CVs rose from ≈9% and ≈14% to 24% and 27%. The previous run may have benefited from a warmer system state. This is triage data, not a regression in the harness—the harness is now correctly detecting what was always latent variance.

2. **`ray_triangle_closest_hit_3d` CV dropped from 1.03 to 0.895** with warmups=5 and repeats=20, a modest improvement. The fast-cluster / outlier bimodality appears to persist. Engineering triage on Apple RT scheduler behavior or MTLCommandBuffer overhead is warranted before this workload can be used as a public baseline.

3. **`ray_triangle_hit_count_3d` median ratio rose from 142× to 169×.** This is within the noise given CV=0.243 and likely reflects system state variation rather than a real regression. The informational note from the original review (possible absence of a hardware-backed hit-count primitive on v0.9.1) remains unaddressed but was labeled non-blocking and still is.

4. **Embree stability is unchanged and good** — all Embree cells are stable. The baseline comparison point is solid.

---

## What this ACCEPT means

The harness is fit for purpose as a v0.9.2 baseline gate. It correctly measures, flags, and constrains the interpretation of unstable apple_rt results. The artifacts make no public speedup claims. Future optimization goals must compare against this artifact and may only update public wording after repeatable stability (CV ≤ 0.15) and parity are demonstrated.

---

## Remaining informational items (carry forward)

- Engineering triage on Apple RT measurement instability (bimodal latency on `closest_hit_3d`, elevated CV on all workloads) should precede any public performance narrative.
- The `hit_count_3d` capability-gap hypothesis (software fallback vs hardware primitive) is worth documenting in the methodology section of the next artifact.
