I have all the data I need. Let me compose the review.

---

## Second AI Review — Phoenix V3 M27 LibRTS AABB Set-B Triage and Cold OptiX Retain Fix

**Date:** 2026-06-23
**Reviewer:** Claude (second AI)
**Packet:** `phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2026-06-23.md`

---

### Verdict: `accept_with_boundary`

The code fix is technically sound and should stay in trunk. The M27 mandate was satisfied. However, neither the OptiX cold watch row nor the Embree stability watch row is closed. The `accept_with_boundary` verdict applies to the code fix and M27 milestone completion, not to watch-row closure. Both watch rows carry forward as open blockers.

---

### Question 1: Is the single-repeat `retain_repeat_outputs=False` change technically sound and generic enough to keep?

**Yes, with one noted asymmetry.**

The change at `rtdl_librts_spatial_index_benchmark_app.py:460` is:

```python
retain_repeat_outputs = query_repeat != 1
```

This is a correct sentinel. For a single measured run, retaining a tuple of output copies is pure overhead with no measurement benefit, and the probe data confirms this: median 0.312s retained vs 0.263s non-retained, a 1.185x direct improvement in the runner itself.

The downstream output handling at line 477 correctly normalizes both forms:

```python
measured_outputs = result.output if isinstance(result.output, tuple) else (result.output,)
```

The test at `tests/v3_phoenix_librts_aabb_count_runner_test.py:203` (`test_optix_aabb_count_single_repeat_avoids_retaining_runner_outputs`) specifically verifies `retain_repeat_outputs=False` is passed when `query_repeat=1`, that output is parsed correctly, and that the payload is complete. The existing test at line 138 verifies `retain_repeat_outputs=True` for `query_repeat=3`. This coverage is sufficient for the targeted change.

**Noted asymmetry:** The Embree path (`run_embree_aabb_counts`, line 360) still passes `retain_repeat_outputs=True` unconditionally, even for `query_repeat=1`. This is not the subject of M27's repair and is defensible since Embree stress runs typically use repeat=20. But it is an inconsistency: if V3 later targets strict cold Embree single-shot rows, the same fix will need to be applied there. This should be noted as a known gap, not a blocker.

**Retain fix verdict: keep.**

---

### Question 2: Does M27 close the strict cold OptiX row with boundary, or is it still `partial_not_closed`?

**The row is improved but not closed. The watch row remains open.**

The verified raw numbers (confirmed from JSON evidence, not from the report alone):

| Sample | V2.14 (s) | Current (s) | Ratio | Pass ≥0.950x |
|-------:|----------:|------------:|------:|:---:|
| 1 | 0.287921481 | 0.541959584 | 0.531x | no |
| 2 | 0.323190220 | 0.262608394 | 1.231x | yes |
| 3 | 0.318295859 | 0.271197304 | 1.174x | yes |
| 4 | 0.301309660 | 0.297451943 | 1.013x | yes |
| 5 | 0.253155112 | 0.286616348 | 0.883x | no |
| 6 | 0.257144421 | 0.263328463 | 0.977x | yes |
| 7 | 0.300088473 | 0.278677516 | 1.077x | yes |
| 8 | 0.270549342 | 0.243741795 | 1.110x | yes |

Verified geomean: **0.973x** (up from the pre-patch 0.922x). Verified median: **1.045x**. Pass count: **6/8**.

**Two problems prevent closure:**

**Problem A — Sample 1 (0.531x) is severely anomalous.** The current time for s1 is 0.542s against V2.14's 0.288s. The gap between s1 and the next-worst sample (s5 at 0.883x) is enormous: s1's current time is roughly 1.88× higher than s5's current time. This distribution is bimodal, not normal variance around a mean. S1 is the first process-fresh cold run of the entire A/B batch and almost certainly includes first-time CUDA context initialization overhead that subsequent samples do not incur. The packet acknowledges the outlier but does not characterize what caused it.

This matters because the watch row was opened specifically for strict cold single-shot behavior. If the worst real-world cold case is a 0.531x run (and this is the first true cold run), the watch row objective is not yet reached. The fix helps typical cold behavior but the worst cold case is not understood.

**Problem B — Sample 5 (0.883x) is a legitimate soft failure.** It is not an anomalous outlier like s1: the current time (0.287s) is within the normal range of the distribution. V2.14 just happened to be faster that run (0.253s). This is genuine variance and is honest.

**Recommendation:** Retain the watch row as open. Record it as "improved, not closed" with explicit notation of the unexplained s1 severity. Before closure, the s1 cold-start pattern needs at least one explanation attempt: is it reproducible? Is it the first CUDA context init? Does it affect the first run after a new process, regardless of which backend version?

---

### Question 3: Embree 32768 stability watch blocker, deterministic blocker, or explanation-only?

**Log as stability watch blocker — not deterministic blocker, not explanation-only.**

The verified Embree numbers:

| Sample | V2.14 (s) | Current (s) | Ratio |
|-------:|----------:|------------:|------:|
| 1 | 0.912685543 | 0.806993507 | 1.131x |
| 2 | 0.895104237 | 0.996299259 | 0.898x |
| 3 | 0.908242274 | 0.997105952 | 0.911x |

Verified geomean: **0.975x** (above 0.950x threshold). But 2/3 samples fall below 0.950x, and the per-sample range is very wide (0.898x to 1.131x).

This is notably concerning given that these are repeat=20, warmup=5 runs. With 20 measured iterations and a 5-run warmup, the median within each sample should be stable. The variance seen here is between process-level samples, not within them, which means the instability is at the OS/driver/thermal level, not the benchmark level. V2.14 shows much tighter per-sample values (0.895–0.913s range, ~2% spread) while current shows a very wide spread (0.807–0.997s, ~24% spread). This is a real regression in stability characteristics, even if the geomean passes.

**Why not "deterministic blocker":** The geomean is above 0.950x. The packet correctly does not flag this as a mean/geomean failure.

**Why not "explanation-only":** The variance pattern is asymmetric — current is much noisier than V2.14. An explanation-only classification would imply the issue is understood and benign. It is not understood: the report offers no mechanistic explanation for why current V3 Embree 32768 is intermittently 10% slower than V2.14 while also sometimes being 13% faster.

**Stability watch blocker status:** The row should block any release or all-app claim until: either (a) a mechanistic explanation is found and accepted, or (b) a larger sample (e.g., 10+ outer samples) demonstrates consistent geomean ≥0.950x with acceptable inter-sample variance.

---

### Question 4: Is the 43-test local/POD coverage enough for this bounded code change?

**Yes, for the bounded scope of this change.**

The 43 tests cover three test modules: `v3_phoenix_librts_aabb_count_runner_test`, `v3_phoenix_prepared_execution_session_runner_test`, and `v3_phoenix_aabb_prepared_query_cache_test`. The specific new test directly verifies the `retain_repeat_outputs=False` path, including output format handling and payload completeness. The regression test for `query_repeat=3` verifies the `retain_repeat_outputs=True` path is not broken.

Both local and POD pass. The Windows pycache warning is not a test failure.

**One coverage gap to flag:** There is no POD test that runs a full benchmark invocation with `--mode optix_aabb_index --repeat 1 --warmup 0` and validates the output JSON passes claim-boundary assertions. The test coverage validates the app layer logic but the benchmark integration is only evidenced by the A/B runs. This is acceptable for Set-B work but should be noted.

---

### Question 5: Should M28 proceed to true Set-A runtime trunk work, or spend more POD time on cold/stability controls first?

**M28 may proceed to Set-A exploratory work. The Set-B watch rows must not be abandoned.**

The rationale for allowing Set-A progression:
- M27's mandate is complete.
- The two open watch rows (OptiX cold and Embree 32768 stability) are Set-B items. They do not directly affect Set-A runtime trunk work.
- Delaying Set-A indefinitely while iterating on Set-B cold stability risks never reaching the primary V3 value proposition.

**The conditions that must hold during M28:**

1. The Embree 32768 stability watch blocker and OptiX cold watch row must remain explicitly tracked and visible. M28 may not treat their open status as resolved.
2. M28 Set-A work must not generate any public speedup, all-app, or release claims based on the current Set-B control surface state.
3. If M28 Set-A work produces results that change the Set-B picture (e.g., runtime changes that affect cold startup), Set-B must be re-run before any claim update.
4. Before any V3 release packet is assembled, both watch rows must be formally resolved.

**M28 may NOT use Set-A forward progress as a reason to retroactively close Set-B watch rows without fresh POD evidence.**

---

### Question 6: Does this packet authorize release, all-app, public speedup wording, broad V3-over-V2 wording, or V4/external zero-copy/embedding scope?

**No. None of the above is authorized.**

Explicitly, this packet does not authorize:

- V3 release of any kind.
- Full all-app rerun.
- Public speedup wording of any kind.
- Broad "V3 is faster than V2.x" wording.
- Hiding the OptiX cold outliers (0.531x in s1, 0.883x in s5).
- Hiding the Embree 32768 inter-sample variance.
- Counting LibRTS AABB single-shot as Set-A evidence.
- V4 scope, external zero-copy claims, or embedding performance claims.
- Promotion of the "stability watch blocker" or "improved-not-closed" status to any kind of accepted row.

---

### Summary of New Non-Authorizations Added by This Review

Beyond the existing non-authorization block, this review adds the following:

1. **The OptiX cold watch row is not closed at any boundary level.** It is "improved" (geomean 0.973x, up from 0.922x). It is not "accepted with boundary." The 0.531x s1 outlier must be investigated before any closure claim.

2. **The s1 cold-start anomaly requires a mechanistic explanation attempt before the OptiX cold row can be marked as even conditionally closed.** Whether it is a first-CUDA-context-init artifact, a driver-level event, or something else must be established.

3. **The Embree 32768 stability watch blocker is real.** The asymmetry in per-sample variance (current V3 ~24% spread vs V2.14 ~2% spread) is not explained and cannot be classified as explanation-only.

4. **The retain fix asymmetry (Embree path still uses `retain_repeat_outputs=True` unconditionally) is a known gap** that should be logged for future Set-B Embree cold single-shot work.

---

### Evidence Integrity

All reported numbers were verified against raw JSON artifacts. SHA256 hashes are consistent within each phase: Embree triage and retain probe used `sha=29ab1553...` (pre-patch), A/B s1-s8 used `sha=7dc4d79d...` (post-patch), and V2.14 is consistent across all artifacts at `sha=e81fc79b...`. The evidence chain is clean.
