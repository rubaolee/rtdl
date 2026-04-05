---

## Technical Review: Goal 98 — OptiX Release Regression Diagnosis and Proposal

---

### 1. Verdict

**APPROVE-WITH-NOTES**

The root cause is correctly identified, the fix is architecturally sound, and the evidence is convincing. Two minor code-level observations do not block the repair but should be noted.

---

### 2. Findings

**Code confirms the diagnosis.**
`__intersection__pip_isect` (lines 933–951) shows the exact structure described: in the old code, `point_in_polygon()` (float32) ran before `optixReportIntersection` even in `positive_only` mode, making any GPU false-negative unrecoverable before host exact finalize. The fix correctly gates on `positive_only != 0u` and short-circuits directly to `optixReportIntersection(0.5f, 0u)`, bypassing the float32 PIP test entirely.

**Anyhit/collect path is correct.**
`__anyhit__pip_anyhit` records the hit into `hit_words` via `atomicOr` before calling `optixIgnoreIntersection()`, so the gather happens before the intersection is discarded. Traversal continues for all candidates. This is correct OptiX idiom for a gathering pass.

**Host exact finalize is correctly wired.**
The readback block (lines 1918–1964) iterates `hit_words`, and for every set bit calls either `geos.covers()` or `exact_point_in_polygon()` (double precision). False positives from the conservative AABB pass are properly filtered. No false negatives can be introduced here.

**Observed anomaly — redundant re-zero and re-upload (lines 1919–1920).**
In the `positive_only` path the `d_count` buffer is already zero at line 1868, and `lp` is already uploaded to `d_params` at line 1906. The re-zero and re-upload immediately before the single launch in the readback block are harmless but suggest a residual two-pass structure that was never cleaned up. Not a correctness risk, but it is confusing.

**Boundary epsilon change is dead code in the positive-only path.**
The proposal cites "widened float32 boundary epsilon" in `point_in_polygon()` (line 879, `point_eps = 1.0e-4f`) as part of the repair. In `positive_only` mode, `point_in_polygon()` is now bypassed entirely, so this epsilon change has no effect there. It only applies to the non-positive-only path. The report conflates both changes without distinguishing which path each affects.

**Performance evidence is consistent and plausible.**
First-run prepared: 4.69 s OptiX vs 3.37 s PostGIS (GPU cold). Warmed reruns: 2.31 s vs 3.27 s (OptiX wins). Raw repeated: 2.12 s vs baseline PostGIS. The conservative candidate set increases host-side work, but the warmed-run speedup shows the GPU broad-phase still provides real benefit.

---

### 3. Agreement and Disagreement

**Agreement:**
- The failure shape (274 missing, 0 extra, stable wrong digest) is the exact signature of GPU-side false negatives. The diagnosis is correct.
- The architectural claim — GPU must bias toward false positives, not false negatives, because host exact finalize handles the former but cannot recover from the latter — is correct and matches the intended RTDL design.
- The repair direction (report all AABB candidates; keep final truth on the host) is the right fix. This is the only safe option given float32 PIP on exact-source geometry.
- The AABB padding widening (`kAabbPad = 1.0e-3f`) is a sound defense-in-depth measure at the broad-phase level.

**Disagreement / clarification needed:**
- The document presents the epsilon widening and the intersection-shader bypass as co-equal parts of the repair. They are not. The intersection-shader bypass (skip `point_in_polygon` in `positive_only` mode) is the decisive fix. The epsilon change is relevant only to the non-positive-only path and should be documented separately to avoid confusion.
- The "repaired Embree direction" claim is cited as supporting evidence but is not verified here. If this parallel is load-bearing for the release narrative, it should be cross-checked against the Embree path explicitly.

---

### 4. Recommended Next Step

Proceed to the final code and rerun package review with two small clarifications in the repair documentation before publishing:

1. Annotate the `point_eps` widening in `point_in_polygon()` to make clear it applies to the `!positive_only` path only, since the positive-only path now bypasses the function entirely. This prevents future reviewers from drawing incorrect conclusions about which change fixed the regression.
2. Clean up or comment the redundant re-zero/re-upload before the single positive-only launch (lines 1919–1920) to reflect the actual single-pass structure.

Neither item needs to re-open the diagnosis or delay the regression fix itself.
