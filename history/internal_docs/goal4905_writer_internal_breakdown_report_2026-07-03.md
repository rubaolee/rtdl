# Goal4905 — Output-Chain Writer Internal Breakdown

Date: 2026-07-03

## Verdict

`completed_writer_breakdown__file_io_not_bottleneck__chain_loop_is_bottleneck`

Goal4905 instrumented the RayJoin reproduction app-layer writer to identify where the remaining writer time is spent after the Goal4903 buffered-output change.

The result is decisive:

- byte-for-byte correctness is preserved;
- bulk file emission is not the bottleneck;
- the writer is dominated by Python chain construction / face+point ID bookkeeping loops, especially map0;
- further writer progress needs structural compiled/partner-assisted chain construction, not more file-I/O micro-tuning.

No RTDL LSI/PIP semantics changed.

## Files Changed

- `history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py`

Change:

- Added internal timing fields inside `write_output_chains_streaming_numba_skip`.
- Returned timing breakdown in `writer_result["goal4905_writer_phase_seconds"]`.
- Preserved exact output logic and buffered output emission from Goal4903.

## Evidence

- Writer breakdown summary:
  - `history/internal_docs/goal4905_writer_breakdown_summary_2026-07-03.json`

## Correctness

Both repeats remain byte-identical to AuthorOfficial.

Repeat 1:

```text
byte_equal_to_author: true
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
lines: 276320
bytes: 6189260
```

## Writer Breakdown

Clean view: repeat 1.

| Writer subphase | Time |
|---|---:|
| skip plan | `0.013s` |
| group xsects map0 | `0.004s` |
| group xsects map1 | `0.006s` |
| chain loop map0 | `1.955s` |
| chain loop map1 | `0.532s` |
| bulk writelines | `0.044s` |
| total writer phase | `2.674s` |

Interpretation:

- Actual file write is only about `0.044s`.
- The remaining writer cost is the Python chain loop.
- The map0 loop is the largest writer subphase because map0 has far more chains/points.
- More `write()` vs `writelines()` tuning is not the right next step.

## Hot-Replay Context

In the same run:

| Phase | Time |
|---|---:|
| total hot body | `4.765s` |
| output writer | `2.674s` |
| vertex PIP map0 in map1 | `1.107s` |
| reprojection + sorting | about `0.878s` |
| LSI prepared replay | `0.006s` |

The prepared LSI replay remains effective; writer chain construction is now the dominant hot-body phase.

## Engineering Conclusion

The next writer goal should not be another Python micro-tune. The only plausible larger writer win is structural:

```text
precompute/compile chain keep + output-chain construction
→ reduce Python per-chain/per-point bookkeeping
→ preserve exact AuthorOfficial output bytes
```

Possible routes:

- Numba-compiled chain scanning that emits compact chain descriptors, leaving final string formatting in Python;
- Numba-compiled face/point-id assignment for the kept chains;
- a two-pass writer where pass 1 computes output sizes/descriptors and pass 2 emits text;
- eventually, a binary/native writer if text output remains a required artifact.

Any such route must be treated as app-layer paper-reproduction engineering unless it is generalized into a reusable RTDL output-continuation primitive.

## What This Does Not Claim

This goal does not claim:

- a performance win by itself beyond measurement clarity;
- broad RTDL/RayJoin speedup;
- full eight-pair Section 5.7 performance;
- single-run speedup over AuthorOfficial;
- LSI/PIP traversal speedup;
- V3/V4 release resurrection.

## Goal-Level Decision Audit

1. Did I make a stupid decision?
   - No. I measured the writer internals before starting a structural rewrite.
2. What actions would have made it stupid?
   - Continuing to tweak file writes after evidence shows file I/O is only `0.044s`.
3. Was there another path?
   - Yes: immediately write a Numba/compiled writer. That might be correct, but this breakdown was needed first.
4. Did I correct course?
   - Yes. The conclusion is explicit: stop file-I/O micro-tuning; only structural chain-loop reduction can matter.
