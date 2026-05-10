# Goal1636 v1.6.x OptiX Collect-K Next Direction After Final-Pair Negatives

## Verdict

`cuda_event_mark_timing_probe_selected`

After Goals 1632-1635, the next safe collect-k performance step is not another production-path rewrite. The next step should be a CUDA-event diagnostic that brackets the final-pair mark kernel and separates actual device execution time from host-visible stream wait time.

## Evidence Summary

| Goal | Result | Consequence |
| --- | --- | --- |
| Goal1632 | Output-indexed fused materialize+mark preserved parity but was slower. | Do not integrate output-indexed fusion. |
| Goal1633 | Plain fused materialize+mark preserved parity but was slower. | Do not continue materialize+mark fusion. |
| Goal1634 | Final-pair profile found `final_pair_mark_sync_ms ~= 0.321 ms` dominating the final-pair breakdown. | Bottleneck is localized to mark/sync behavior. |
| Goal1635 | Device final-prefix prototype preserved parity but worsened total time, moving wait into `final_pair_final_sync_ms ~= 0.370 ms`. | Host prefix scan/upload is not the main bottleneck. |

## External Review

- Claude review: `docs/reviews/claude_goal1636_collect_k_next_direction_review_2026-05-09.md`
- Gemini review: `docs/reviews/gemini_goal1636_collect_k_next_direction_review_2026-05-09.md`

Both external reviews agree that the next direction should avoid more blind fusion/offload attempts. Claude recommends the lowest-risk diagnostic: CUDA events around the final mark kernel. Gemini recommends reducing dispatch/synchronization overhead, with CUDA Graphs as a later candidate if launch overhead is proven relevant.

## Selected Next Candidate

Add opt-in internal profiling fields around the final-pair mark kernel:

- `final_pair_mark_gpu_event_ms`
- `final_pair_mark_stream_wait_ms` or equivalent derived accounting

The probe should answer whether the observed `final_pair_mark_sync_ms` is mostly:

- actual mark-kernel GPU execution,
- stream wait behind earlier merge work,
- compact/final-output work that was previously hidden by asynchronous launch accounting,
- or a mix of these.

## Decision Table

| Observation | Interpretation | Next Action |
| --- | --- | --- |
| mark GPU event time is small, but host sync time is large | Stream wait / pipeline accounting dominates. | Consider stream/graph dispatch diagnostics before changing mark algorithm. |
| mark GPU event time is large | Mark kernel itself is costly. | Consider mark/compact algorithm alternatives such as final-output-specific selection. |
| compact/final sync dominates after event timing | Final-output materialization strategy is the bottleneck. | Investigate output strategy, not prefix. |

## Claim Boundary

This is an internal direction-setting artifact only. It does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
