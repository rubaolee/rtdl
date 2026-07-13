# Goal4908 — Descriptor/Fast-Path Writer Probe Negative Result

Date: 2026-07-03

## Verdict Requested

`completed_negative_probe__byte_equal_but_slower__reverted_to_goal4907_writer`

## Goal

Probe whether the remaining Goal4907 writer chain-loop cost could be reduced by
using the existing Numba-generated chain descriptors more aggressively.

The tested idea:

```text
For chains with no intersections but terminal_keep=true:
  skip the full per-point overlay loop
  construct the chain point list directly
  emit through the same exact flush/output path
```

This used the existing Numba-assisted `has_xsects` / `terminal_keep` /
`skip_chain` plan. It did not modify RTDL core, LSI, PIP, or correctness
semantics.

## Result

The probe preserved correctness but made the prepared-hot route slower.

Evidence:

```text
history/internal_docs/goal4908_descriptor_writer_summary_2026-07-03.json
```

Repeat 1:

| Metric | Goal4907 | Goal4908 probe | Direction |
|---|---:|---:|---|
| byte_equal_to_author | `true` | `true` | preserved |
| hot body total | `4.013s` | `4.527s` | worse |
| output writer | `1.946s` | `2.222s` | worse |
| chain loop map0 | `1.491s` | `1.499s` | flat/slightly worse |
| chain loop map1 | `0.332s` | `0.335s` | flat/slightly worse |
| file summary generated | `0.021s` | `0.237s` | noisy/worse |

The probe processed:

| Descriptor | Count |
|---|---:|
| fast no-xsect kept chains | `5,140` |
| fast no-xsect kept points | `138,988` |
| skipped no-xsect chains | `399,419` |
| skipped no-xsect points | `14,996,199` |

## Interpretation

The idea was reasonable but wrong for this workload.

The old Goal4907 loop is already avoiding the most expensive no-output chains.
The remaining no-xsect-but-kept chains still need exact output. The attempted
fast path avoided some Python branch checks, but it paid for that by constructing
large Python lists of point tuples:

```text
138,988 extra direct chain points in the fast path
```

That allocation cost outweighed the saved loop logic. The result confirms that
another Python-side reshuffle is unlikely to produce a large win.

## Action Taken

The slow Goal4908 fast path was reverted from:

```text
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
```

The retained implementation is the Goal4907 writer:

- shared `points` / `display_points` representation;
- cached point-id plus formatted line records;
- byte-equal prepared-hot result;
- writer `2.674s -> 1.946s`.

## What This Teaches

Goal4908 rules out a tempting but shallow path:

```text
more Python fast paths around no-xsect kept chains
```

The remaining writer work needs a genuinely compiled descriptor design if it is
worth pursuing:

```text
Numba/C extension computes chain descriptors and point-id/layout metadata
Python only performs final exact text serialization
```

Or the project should switch to the separate cold/setup branch.

## Boundaries

This goal does not claim:

- any new speedup;
- broad RTDL/RayJoin performance;
- a primitive traversal improvement;
- a correctness change;
- a release claim.

It is a negative engineering result that preserves the better Goal4907 state.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   The probe itself was not stupid: it targeted a measured writer-loop cost and
   had a byte-equality gate. Keeping it after it slowed the run would be stupid.

2. **What action would have made this stupid?**

   Reporting only that byte equality passed, hiding the slowdown, or leaving the
   slower path in place.

3. **Was there another path?**

   Yes. A deeper compiled descriptor path may still work, but this shallow
   no-xsect kept-chain fast path does not.

4. **Can I start a different path that truly solves the problem?**

   Yes, but only if the next goal is either a real compiled descriptor design or
   the separate cold/setup line. More Python micro-fast-paths are now suspect.
