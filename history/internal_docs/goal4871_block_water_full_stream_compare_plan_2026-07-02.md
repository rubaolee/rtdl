# Goal4871 - Deliberate full-stream comparison for Block x Water

Date: 2026-07-02

## Purpose

Goal4870 proved that RTDL and the explicitly patched
`Author+RTDLContractPatch` comparator match exactly over the first 1,000,000
output lines for the Block x Water Section 5.7 pair.

Goal4871 attempts the full-stream correctness comparison for the same pair. It
does not change RTDL core, native code, Python runtime code, public docs, or the
author comparator. It only adds a progress-capable internal validation harness
so the run is observable and bounded.

## Why this is the correct next step

The previous evidence chain is:

- duplicate-half-edge synthetic contract passed,
- focused Block x Water witness moved as intended,
- `Author+RTDLContractPatch` built and produced output,
- 100k / 250k / 1M output prefixes matched exactly.

At this point, more synthetic tests would be lower value than a deliberate
full-stream check. The remaining question is whether the equivalence holds over
the entire 3.6G / 138,674,679-line output.

## Full-stream scale

Author comparator output:

- path: `/workspace/goal4868_author_rtdl_contract_block_water/author_rtdl_contract_block_water_overlay.txt`
- lines: `138,674,679`
- size: `3.6G`

## Controls

- Use the same `Author+RTDLContractPatch` baseline as Goals4869/4870.
- Do not compare against the old unpatched AuthorPatch baseline.
- Do not write a second 3.6G RTDL output file.
- Stream RTDL output in Python and compare each generated line against the
  existing author output.
- Print progress periodically so the run cannot become an opaque "looks busy"
  hole.
- Stop immediately on the first mismatch and record context.
- Keep the run under an explicit shell `timeout`.

## Expected result labels

Success:

`completed_block_water_full_stream_match_against_author_rtdl_contract_patch`

Mismatch:

`blocked_by_first_full_stream_mismatch_with_context`

Timeout:

`blocked_by_full_stream_runtime_cost_requires_hash_or_window_strategy`

## What this does not authorize

This goal does not authorize:

- full Section 5.7 reproduction across all pairs,
- performance claims,
- public docs,
- claims against the old unpatched author baseline,
- changes to RTDL runtime semantics.
