# Gemini Review: Goal 289 v0.5 KITTI 4096 Boundary

Date: 2026-04-12

## Review Judgments

1. **Is the `4096` boundary described honestly?**
   Yes. The report clearly defines the `4096` boundary as the first size where strict parity breaks on a duplicate-free KITTI dataset. It accurately reports the exact conditions (0 duplicate match count) and the extent of the mismatch (140 missing/extra pairs out of 2655 rows).

2. **Does the reduced-candidate probe support the stated conclusion?**
   Yes. The script `goal289_kitti_large_set_mismatch_probe.py` successfully isolates the first failing query (`query_id: 291`) and its true top 20 candidates, and executes cuNSearch solely on this reduced subset. The report correctly reflects that parity is achieved (`true`) on this subset. This fully supports the conclusion that the failure is not inherently tied to the query point itself, nor to simple local ties, but is specifically triggered by the broader large-set search conditions.

3. **Does the report avoid overclaiming the root cause?**
   Yes. The report is appropriately conservative. It explicitly states what the failure is *not* (not a duplicate-point issue, not a simple local ordering issue) and defines the current operational boundary (duplicate-point-safe through 2048, large-set blocked at 4096). Crucially, it concludes by noting this is a "bounded host-specific result, not a broad statement about cuNSearch in general," successfully avoiding any unsubstantiated claims about the exact algorithmic or CUDA-level root cause.
