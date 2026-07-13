# Goal4915 — Compiled Intersection-Chain Descriptor Plan

Date: 2026-07-03

## Requested Verdict

`approve_goal4915_compiled_intersection_chain_descriptor_probe`

## Why This Goal Exists

Goal4914 proved the public workspace API is real and does not regress the hot
path:

```text
Goal4910 hot body: 3.918s
Goal4914 workspace hot body: 3.955s
byte_equal: true
```

The remaining prepared-hot bottleneck is no longer LSI/PIP setup or primitive
execution. It is the application-layer output writer:

```text
Goal4914 repeat1 output_chain_write_sec: 1.875s
```

Goal4908 and Goal4910 already showed that shallow Python writer fast paths have
little remaining leverage:

- Goal4908 no-xsect Python fast path got slower.
- Goal4910 direct no-xsect descriptor path improved writer only
  `1.946s -> 1.840s` (`~0.106s`).

Therefore the next useful experiment must target the remaining heavy region:

```text
intersection-bearing chain assembly, not no-xsect skipping
```

## Choice

I choose:

```text
Build a compiled app-layer descriptor probe for intersection-bearing chains.
```

I explicitly do not choose:

- more point-location group-mode tuning;
- more no-xsect skip tweaks;
- cross-process GAS cache;
- RTDL core/native changes;
- raw OptiX callback work.

## Current Writer Breakdown

Goal4914 repeat1 writer sub-phases:

| Writer sub-phase | Time |
|---|---:|
| chain loop map0 | `1.380s` |
| chain loop map1 | `0.329s` |
| skip plan | `0.013s` |
| group xsects map0 | `0.0048s` |
| group xsects map1 | `0.0058s` |
| bulk writelines | `0.048s` |
| total writer | `1.875s` |

The target is the map0/map1 chain loop time:

```text
1.380s + 0.329s = 1.709s
```

## Proposed Probe

Add a new internal app-layer writer probe that:

1. keeps public RTDL LSI/PIP/workspace unchanged;
2. keeps the current AuthorOfficial output contract unchanged;
3. uses Numba or structured NumPy to precompute a descriptor table for
   intersection-bearing chains:
   - chain id;
   - map index;
   - edge spans;
   - intersection group offsets;
   - midpoint face ids;
   - point slice ranges;
   - keep/drop decision;
4. lets Python perform only the final exact text formatting and ID allocation
   that cannot safely be moved to Numba without changing output semantics;
5. compares byte-for-byte with AuthorOfficial.

This is app-layer optimization. It is not a new RTDL primitive and not a hidden
RayJoin kernel in core.

## Acceptance Bar

The probe passes only if all are true:

| Gate | Required |
|---|---|
| correctness | byte-equal to AuthorOfficial |
| boundary | no `rtdsl.rayjoin_overlay`; no `src/rtdsl` or `src/native` edits |
| target phase | intersection-bearing chain loop explicitly measured |
| writer speed | `output_chain_write_sec <= 1.50s` |
| hot body | `elapsed_sec <= 3.60s` |
| explanation | win source is descriptor/chain-loop reduction, not noise |

If byte equality fails, revert and close as failed.

If writer remains above `1.50s`, close as:

```text
correct_but_not_worth_productizing__python_text_writer_floor
```

## Why This Is Not Another Shallow Micro-Tweak

Goal4908/4910 targeted only no-xsect direct emission. That leaves the expensive
intersection-bearing path mostly unchanged.

Goal4915 must target the part still costing time:

```text
Python chain-loop assembly for chains that contain intersections.
```

If the probe cannot reduce this, the honest conclusion is that exact text output
assembly has reached a Python/app-layer floor and the next step would require a
larger native or compiled output writer product, not more small patches.

## Non-Authorization Boundary

This goal does not authorize:

- changing RTDL core/native;
- changing public workspace/LSI/PIP semantics;
- hiding RayJoin logic inside RTDL;
- broad performance claims;
- raw OptiX callbacks;
- V3/V4 resurrection.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   Not if this remains a bounded probe against the actual remaining writer
   phase. It would be stupid to repeat no-xsect fast paths or mode sweeps.

2. **What action would make this stupid?**

   Treating a tiny improvement as product value, or moving output-format-specific
   RayJoin logic into RTDL core.

3. **Was there another path?**

   Yes: stop and consolidate current results. That is acceptable if this probe
   misses the bar.

4. **Can I start a different path that truly solves the problem?**

   Yes. This probe directly tests whether the remaining writer floor is
   reducible within the app layer. If not, we stop this performance line or
   design a separately reviewed native output writer.
