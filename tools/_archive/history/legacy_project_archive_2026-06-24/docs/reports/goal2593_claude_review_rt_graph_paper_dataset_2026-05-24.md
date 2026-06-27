I have now read all the relevant files. Here is the structured review.

---

## Goal2593 Paper-Dataset Evaluation Review

**Verdict: ACCEPT**

The conclusion is fully supported by evidence, the claim boundary is appropriate, the engine contract is maintained, and there is no overclaiming. The app-open status is the correct engineering call.

---

### 1. Evidence Consistency

**Dataset preparation (snap_prepare_all.json → report table)**

All 7 datasets show `edge_count_matches_snap: true`. Every edge count and expected triangle count in the report table matches the JSON exactly. No discrepancy.

**End-to-end performance matrix (report numbers → raw JSON medians)**

Spot-checked all cells. Every number in the report table is the `median_total_ms` (or equivalent aggregate) from the corresponding raw file:

| Spot check | Report | Raw | Match |
|---|---|---|---|
| com-dblp RTDL 2A1 | 210.060 | `median_total_ms: 210.060` | ✓ |
| com-dblp cuGraph | 81.078 | `median_total_ms: 81.078` | ✓ |
| wiki-Talk RTDL 2A1 | 2190.360 | `median_total_ms: 2190.360` | ✓ |
| cit-Patents RTDL 2A1 | 1716.011 | `median_total_ms: 1716.011` | ✓ |
| com-lj cuGraph | 1713.029 | `median_total_ms: 1713.029` | ✓ |
| soc-LiveJournal1 rt_tc | 65658.375 | `median_pipeline_excluding_file_read_ms: 65658.375` | ✓ |
| com-orkut cuGraph | 7229.100 | `median_total_ms: 7229.100` | ✓ |

**Core timing boundary table (traversal / kernel microphase)**

All native traversal and pure-count kernel times match raw fields (`median_native_traversal_ms`, `median_triangle_count_ms`, `median_counting_ms`) to 3+ significant figures. No rounding artifacts or cherry-picking.

**Memory failure sizes**

The report uses decimal GB (÷ 10⁹). Raw bytes:

| Dataset | Raw bytes | Report | Computed |
|---|---|---|---|
| com-lj | 7,429,851,776 | 7.43 GB | 7.43 GB (÷10⁹) ✓ |
| soc-LiveJournal1 | 11,066,394,608 | 11.07 GB | 11.07 GB ✓ |
| com-orkut | 68,639,445,368 | 68.64 GB | 68.64 GB ✓ |

Both `rtdl_2a1` and `rtdl_1a2` fail with the **identical allocation size** on each large dataset, confirming the failure is in a shared CuPy pre-processing step that precedes the 2A1/1A2 path split — consistent with the "global two-hop materialization" diagnosis.

**Failure modes**

All failures are correctly labelled. `com-lj`/`soc-lj`/`com-orkut` RTDL: `MemoryError` / `std::bad_alloc` in raw JSON. `wiki-Talk` / `cit-Patents` RTDL 1A2: `CUDA driver error: out of memory` in raw JSON. com-orkut authors: `Signals.SIGKILL` (elapsed ~147–149 s) in raw JSON. All match the report.

**Correctness**

`matches_expected_triangles: true` and `matches_oracle: true` are present in all successful run records. The report claim "every successful method returned the expected triangle count" is exactly right.

---

### 2. Minor Observations (not blocking)

**cuGraph large-dataset warmup**: For com-lj, soc-LiveJournal1, and com-orkut the harness ran 0 warmup / 1–2 measured repeats. The com-lj cuGraph runs show significant variance (2003 ms, 1422 ms; median 1713 ms), suggesting the first run is cold. This is acceptable — RTDL cannot run those datasets at all, so the cuGraph baseline timing direction does not affect any claim. If cuGraph baselines are tightened later, a warmup pass should be added.

**PostgreSQL evidence gap**: The raw JSON (`goal2593_eval_postgres_com_dblp.json`) shows a 120-second `TimeoutExpired` on com-dblp — not a completion. The report text mentions "a first com-dblp attempt completed during interactive logging" before the formal timed run failed. The report correctly marks PostgreSQL as deferred with no clean JSON evidence. The K4 report's PostgreSQL data must not be extrapolated to paper datasets; the report says exactly this.

**Decimal vs. binary GB label**: The report uses "GB" with decimal division (÷ 10⁹), not GiB (÷ 2³⁰). The numbers are self-consistent. A parenthetical note in a future revision would prevent confusion, but it is not a blocker.

---

### 3. Overclaiming Check

None detected. The report:
- Does not claim RTDL is faster than any baseline end-to-end on any dataset.
- Does not extrapolate the synthetic K4 closeout to paper datasets.
- Does not claim OptiX traversal correctness across all paper datasets — only the datasets where the end-to-end pipeline completed.
- Does not compare RTDL traversal microphase time against authors' full pipeline time.
- Correctly attributes failures to a design limitation (pre-traversal materialization), not to the native OptiX engine.

---

### 4. Engine Boundary

The eval script calls `app.run_app(mode=..., backend="optix", partner="cupy")`. The README explicitly states "No graph-specific native ABI is added by this benchmark wrapper. Graph semantics remain in Python app code. The engine-facing contract stays generic." The catalog boundary note is accurate. The engine boundary is intact.

---

### 5. Verdict and Required Next Steps

**ACCEPT — the conclusion is correct and well-evidenced.**

The K4 synthetic closeout is superseded. cuGraph is the strongest end-to-end baseline on real paper datasets. RTDL is correct on the four smaller datasets (com-dblp, com-youtube, wiki-Talk, cit-Patents via 2A1; com-dblp and com-youtube via 1A2) and is blocked by pre-traversal OOM on the three largest (com-lj, soc-LiveJournal1, com-orkut). The app-open status is the right call.

**Required next steps before the benchmark app can be closed:**

1. **Either** implement segmented/streamed CuPy lowering that avoids global two-hop materialization (preferred — enables a true paper-scale claim), **or** write an explicit signed-off scalability limitation in the README stating which paper datasets are out of scope on the current path.
2. Add a warmup pass to cuGraph runs on large datasets before recording final baseline numbers.
3. PostgreSQL must complete cleanly on at least com-dblp and com-youtube before being included in any performance table.
4. No native engine ABI changes are needed; the generic contract is the right shape for the segmented path too.
