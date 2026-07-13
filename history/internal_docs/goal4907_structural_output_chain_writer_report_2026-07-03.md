# Goal4907 — Structural Output-Chain Writer Optimization

Date: 2026-07-03

## Verdict Requested

`completed_structural_writer_loop_optimization__byte_equal__prepared_hot_body_win`

## Goal

Optimize the largest prepared-hot bottleneck identified by Goal4905 without
touching RTDL LSI/PIP primitives or adding a RayJoin-specific RTDL core kernel.

Goal4905 showed:

```text
writer total:       2.674s
bulk file write:    0.044s
chain loop map0:    1.955s
chain loop map1:    0.532s
```

Therefore, more file-I/O tuning would be pointless. The target had to be the
Python output-chain construction/bookkeeping loop.

## Implementation

Changed only the internal RayJoin paper-reproduction Numba harness:

```text
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
```

The change:

1. stopped maintaining duplicate `points` and `display_points` lists when they
   are identical;
2. taught `dedupe_point_pairs_numba_enabled()` to preserve that single-list
   representation;
3. replaced separate `point_ids` plus repeated f-string formatting with a
   `point_records` cache:

   ```text
   point -> (point_id, formatted_output_line)
   ```

4. retained a separate `display_line_cache` only for the rare case where display
   points differ from logical points;
5. preserved existing chain splitting, face-id assignment, point-id assignment,
   no-output skip plan, and exact output text.

This is an app-layer structural writer optimization. It is not an RTDL core
primitive change.

## Correctness

POD prepared-replay run:

```text
history/internal_docs/goal4907_structural_writer_summary_2026-07-03.json
```

Repeat 1:

| Metric | Value |
|---|---:|
| byte_equal_to_author | `true` |
| generated SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| author SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| output lines | `276,320` |
| output bytes | `6,189,260` |

The result is byte-for-byte equal to AuthorOfficial on both repeats.

## Performance

Clean prepared-hot comparison uses repeat 1.

| Metric | Goal4905 baseline | Goal4907 result | Speedup |
|---|---:|---:|---:|
| hot body total | `4.764690s` | `4.013377s` | `1.19x` |
| output writer | `2.673821s` | `1.945501s` | `1.37x` |
| chain loop map0 | `1.955336s` | `1.490763s` | `1.31x` |
| chain loop map1 | `0.531839s` | `0.331866s` | `1.60x` |
| bulk writelines | `0.043514s` | `0.048308s` | no win expected |
| LSI prepared replay | `0.006196s` | `0.006159s` | unchanged |
| vertex PIP map0 in map1 | `1.106500s` | `1.096888s` | unchanged |

Cache counts:

| Item | Value |
|---|---:|
| emitted output point lines | `256,500` |
| unique point records | `203,630` |
| unique display-line-only records | `0` |

Interpretation:

- The optimization hits exactly the measured writer-loop bottleneck.
- It does not change RTDL primitive time.
- It does not hide file I/O: bulk write remains tiny, around `0.05s`.
- The hot body is now about `4.01s` for the representative prepared replay.

## Current Prepared-Hot Bottlenecks After Goal4907

Repeat 1 phases:

| Phase | Time |
|---|---:|
| output writer | `1.946s` |
| vertex PIP map0 in map1 | `1.097s` |
| intersection reprojection | `0.468s` |
| sort map0+map1 | `0.404s` |
| LSI prepared replay | `0.006s` |

The writer remains the largest phase, but the easy structural cache/list win has
now been spent. Further writer improvement would require a larger compiled
descriptor/emission design, not another small Python tweak.

## Boundaries

Authorized claim:

- The RayJoin paper-reproduction app-layer writer now avoids duplicate
  point/display list work and repeated point-line formatting.
- On the Australia representative prepared-hot replay, it preserves byte equality
  and improves the writer phase from `2.674s` to `1.946s`.

Not authorized:

- no broad RTDL/RayJoin speedup claim;
- no full eight-pair Section 5.7 performance claim;
- no single-run cold speedup claim;
- no claim that RTDL beats AuthorOfficial overall;
- no claim that Numba accelerates RTDL primitive traversal;
- no RTDL core/native RayJoin-specific shortcut;
- no V3/V4 release resurrection.

## What This Means For The Next Step

Goal4907 confirms the Goal4906 branch decision:

```text
prepared-hot immediate branch = Branch A
```

The next work should not go back to old cold-state `native_rt_traversal`
language. The remaining prepared-hot choices are now:

1. a larger compiled/partner-assisted writer descriptor path, if we want to
   reduce the remaining `1.95s` writer;
2. point-location map0 query improvement, because vertex PIP map0 remains about
   `1.10s`;
3. cold/setup work on point-location preparation, tracked separately from hot
   replay.

The narrow next recommendation is to stop micro-tuning writer file emission and
either:

```text
Goal4908: compiled chain descriptor probe
```

or switch to the separate cold/setup branch.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. The implementation targeted the exact Goal4905 bottleneck and left RTDL
   primitives alone.

2. **What action would have made this stupid?**

   Continuing to optimize `writelines()` after measuring file I/O at `0.044s`
   would have been stupid. So would moving RayJoin output-chain logic into RTDL
   core.

3. **Was there another path?**

   Yes. A larger Numba descriptor writer could be attempted directly. I chose a
   smaller structural change first because it was low-risk, byte-equal-gated,
   and hit duplicated work visible in the current loop.

4. **Can I start a different path that truly solves the problem?**

   Yes. The remaining true paths are a compiled chain descriptor/emission design
   for the app layer, or a separate cold/setup optimization line. The current
   result narrows the next decision instead of hiding it.
