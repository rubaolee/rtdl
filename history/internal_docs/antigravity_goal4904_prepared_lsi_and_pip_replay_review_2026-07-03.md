# Goal4904 Critical External Review: Prepared LSI + Prepared PIP Hot Replay Probe

Date: 2026-07-03

## Verdict Label
**`approve_goal4904_prepared_lsi_pip_hot_replay`**

***

## Findings & Answers to Review Questions

### 1. Does Goal4904 correctly use public prepared LSI query sessions and public prepared point-location sessions?
Yes. The probe script [goal4904_prepared_lsi_and_point_location_replay_probe.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py) prepares public LSI base/query sessions and point-location (PIP) sessions outside of the timing-critical hot loop. Specifically:
* It prepares the LSI base via [prepare_planar_map_lsi_2d_optix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py#L228) and the query session via [prepare_query](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py#L233).
* It prepares point-location sessions via [prepare_planar_map_point_location_2d_optix](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py#L240).
* Inside the hot-body function [run_body](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py#L64), these sessions are successfully reused: LSI uses [run_pair_id_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py#L76) and PIP uses [run_point_location](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_point_location_replay_probe.py#L100).

### 2. Does it preserve byte-for-byte output?
Yes. In [goal4904_prepared_lsi_pip_replay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_pip_replay_summary_2026-07-03.json), both runs verify byte-for-byte consistency against the AuthorOfficial reference overlay result:
* `byte_equal_to_author: true`
* `sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`
* `bytes: 6189260`
* `lines: 276320`

### 3. Is the hot-replay speedup correctly bounded to repeated-query/replay workloads?
Yes. The primary report [goal4904_prepared_lsi_and_pip_replay_report_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_and_pip_replay_report_2026-07-03.md) explicitly limits the applicability of these speedups to hot-replay or repeated-query workloads. This constraint is also recorded in the evidence JSON metadata:
* `broad_performance_claim: false`
* `single_run_speedup_claim: false`

### 4. Does the report avoid claiming single-run cold performance improvement?
Yes. The report details the setup cost components separately (totaling ~21.8s, including load, pack, and session preparations). It explicitly states: "This does not mean the single-run paper reproduction avoids LSI setup. It means RTDL has a real prepared-replay shape for repeated-query workloads." The "What This Does Not Claim" section also rejects any single-run speedup claims over the AuthorOfficial baseline.

### 5. Is the LSI replay improvement real and correctly measured (1.814s to 0.006s in the hot replay comparison)?
Yes. Comparing repeat 1 (the hot run) in the two summaries:
* **Baseline (Goal4903):** LSI query execution time (`lsi_public_pair_id_rows_sec`) is `1.81376s` in [goal4903_buffered_writer_hot_session_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4903_buffered_writer_hot_session_summary_2026-07-03.json).
* **Prepared Replay (Goal4904):** LSI query execution time is `0.00616s` in [goal4904_prepared_lsi_pip_replay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4904_prepared_lsi_pip_replay_summary_2026-07-03.json).
This represents a real ~294x speedup for the LSI phase, reducing it to a millisecond-level step.

### 6. Does the report correctly identify the remaining split: hot bottleneck is writer; cold/setup bottleneck is point-location base preparation?
Yes. The breakdown of the measurements confirms this:
* **Hot Replay Bottleneck:** The hot body total of `4.638s` is dominated by the output writer (`output_chain_write_sec` at `2.562s`, ~55.2%) and vertex PIP (`vertex_pip_map0_in_map1_sec` at `1.096s`, ~23.6%).
* **Cold/Setup Bottleneck:** The setup phase is dominated by large-map point-location base preparation (`prepare_point_location_map1_in_map0_sec` at `13.864s`, ~63.5% of the total setup time of ~21.8s).

### 7. Should Goal4904 close and authorize a next structural goal, not another trivial writer micro-tune?
Yes. Micro-tuning of the Python writer has reached diminishing returns. The review recommends closing Goal4904 and authorizing a structural change next, either:
* **App-layer (Hot Replay):** Designing a compiled/partner-assisted output-chain construction path.
* **Engine-layer (Cold/Setup):** Persisting or generically optimizing the point-location base preparation cost.

***

## Non-Authorization Boundaries (Preserved)

This review enforces and preserves all non-authorization boundaries. The following actions and claims remain **unauthorized**:
1. **Broad RTDL/RayJoin speedup claims:** Optimization is limited to the prepared-session replay path.
2. **Full Section 5.7 eight-pair claims:** Testing was only done on the representative pair.
3. **Single-run speedup over AuthorOfficial:** No general single-run performance dominance is claimed or authorized.
4. **LSI/PIP semantic changes:** Primitives and search behaviors remain completely unchanged.
5. **Hidden RayJoin-specific kernels:** No hidden kernels or proprietary layers were added.
6. **V3/V4 release resurrection:** Any lifecycle decisions for older versions remain locked.
7. **Public release/tag decisions:** Version tag decisions remain unauthorized.
