# Goal4910 — Direct Descriptor-Assisted Writer Result

Date: 2026-07-03

## Verdict Requested

`partial_descriptor_win__byte_equal__strong_bar_not_met`

## Goal

After Goal4908 showed that a Python list-based no-intersection fast path was
slower, Goal4910 tested a more direct descriptor-assisted writer path:

```text
use existing Numba descriptor plan to identify no-xsect kept chains
emit those chains directly from dataset arrays
avoid building intermediate OutputChain point/display lists for those chains
preserve exact output semantics
```

This remains app-layer paper-reproduction engineering. It does not modify RTDL
core/native code and does not change LSI/PIP primitives.

## Implementation

Changed:

```text
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
```

Added:

- `emit_direct_dataset_chain(...)`
- descriptor counters:
  - `descriptor_direct_chains`
  - `descriptor_direct_points`

The direct path only applies when:

```text
has_xsects[chain_index] == false
skip_chain[chain_index] == false
```

All chains with intersections still use the existing exact writer logic.

## Correctness

POD prepared replay artifact:

```text
history/internal_docs/goal4910_direct_descriptor_writer_summary_2026-07-03.json
```

Repeat 1:

| Metric | Value |
|---|---:|
| byte_equal_to_author | `true` |
| generated SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| author SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| output lines | `276,320` |
| output bytes | `6,189,260` |

Both repeats are byte-identical to AuthorOfficial.

## Performance

Prepared-hot repeat 1 comparison:

| Metric | Goal4907 best | Goal4910 result | Speedup |
|---|---:|---:|---:|
| hot body total | `4.013s` | `3.918s` | `1.024x` |
| output writer | `1.946s` | `1.840s` | `1.057x` |
| chain loop map0 | `1.491s` | `1.397s` | `1.067x` |
| chain loop map1 | `0.332s` | `0.335s` | no win |
| bulk writelines | `0.048s` | `0.049s` | unchanged |

Descriptor coverage:

| Counter | Value |
|---|---:|
| descriptor direct chains | `5,140` |
| descriptor direct points | `138,988` |
| skipped no-xsect chains | `399,419` |
| skipped no-xsect points | `14,996,199` |
| processed chains | `9,621` |

## Bar Result

Goal4909 set the strong implementation bar:

| Bar | Goal4910 |
|---|---:|
| writer `< 1.50s` | `1.840s` — not met |
| hot body `< 3.60s` | `3.918s` — not met |
| byte equality | met |

Therefore the correct classification is:

```text
partial_descriptor_win
```

not:

```text
completed_writer_solution
```

## Interpretation

Goal4910 is better than the negative Goal4908 path because it avoids building a
large intermediate tuple list for no-xsect kept chains. But the improvement is
small:

- only about `0.106s` on the writer phase;
- only about `0.095s` on the total prepared-hot body.

This means the shallow descriptor-assisted line is close to exhausted.

To make a large writer improvement, the next writer attempt would need to move
more of the actual chain descriptor construction and point-id/layout work into a
compiled representation. A partial no-xsect direct emitter is not enough.

## Current Best Prepared-Hot State

The best retained route is now Goal4910:

```text
hot body repeat1: 3.918s
writer repeat1:   1.840s
byte_equal:       true
```

The remaining main phases are:

| Phase | Time |
|---|---:|
| output writer | `1.840s` |
| vertex PIP map0 in map1 | `1.080s` |
| intersection reprojection | `0.482s` |
| sort map0+map1 | `0.417s` |
| LSI prepared replay | `0.006s` |

## Recommendation

Do not continue with small Python writer tweaks.

The next legitimate options are:

1. a real compiled descriptor/layout pass that covers intersection-bearing
   chains too; or
2. switch to the cold/setup branch, especially point-location preparation cost.

Given the diminishing writer returns, the recommended next step is:

```text
Goal4911: cold/setup point-location preparation reduction audit
```

That branch targets a different, still-large cost and avoids chasing fractions
of a second in Python writer code.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. This was a bounded implementation of the approved Goal4909 plan with a
   hard bar and byte-equality gate.

2. **What action would make this stupid?**

   Pretending the small win met the strong bar, or continuing many more tiny
   writer tweaks without a deeper compiled plan.

3. **Was there another path?**

   Yes. We could switch immediately to cold/setup. Goal4910 was still worth
   trying because it was low risk and directly targeted a measured chain-loop
   subcase.

4. **Can I start a different path that truly solves the problem?**

   Yes. The evidence now favors either a much deeper compiled descriptor writer
   or a pivot to cold/setup point-location preparation. The shallow writer path
   should stop.
