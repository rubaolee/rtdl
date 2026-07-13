# Goal4915 — Intersection-Chain Writer Probe Result

Date: 2026-07-03

## Requested Verdict

`completed_goal4915_correct_but_not_worth_productizing__python_text_writer_floor`

## Goal

Test whether the remaining prepared-hot writer bottleneck can be materially
reduced by targeting intersection-bearing chain assembly, after no-xsect writer
fast paths hit diminishing returns.

This goal stayed app-layer only:

- no `src/rtdsl/**` edits;
- no `src/native/**` edits;
- no public primitive semantics changes;
- no `rtdsl.rayjoin_overlay` import;
- no raw OptiX callback exposure.

## Implementation

Updated internal harness:

```text
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
```

Change:

- added `flush_plain_chain(...)`;
- intersection-bearing chains no longer allocate `base.OutputChain`;
- chain fragments are flushed directly through the same point/face allocation
  and output-line contract;
- no-xsect direct descriptor path from Goal4910 remains.

This is not a compiled native writer. It is a lower-overhead app-layer probe for
the intersection-bearing chain path.

## POD Evidence

Summary:

```text
history/internal_docs/goal4915_intersection_writer_summary_2026-07-03.json
```

Dataset:

```text
Australia lakes x parks representative Section 5.7 pair
```

Comparator:

```text
AuthorOfficial
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
```

## Correctness

Both repeats are byte-equal to AuthorOfficial:

```text
byte_equal_to_author: true
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
```

Counts remain stable:

| Metric | Value |
|---|---:|
| LSI row count | `13452` |
| xsects map0 | `13452` |
| xsects map1 | `13452` |
| vertex positives map0 in map1 | `193846` |
| vertex positives map1 in map0 | `30538` |

## Performance Result

Reference:

```text
Goal4914 workspace repeat1 hot body: 3.955s
Goal4914 writer:                    1.875s
```

Goal4915 repeat1:

```text
hot body: 3.832s
writer:   1.763s
```

Derived:

| Metric | Before | After | Effect |
|---|---:|---:|---:|
| hot body | `3.955s` | `3.832s` | `1.032x` |
| writer | `1.875s` | `1.763s` | `1.063x` |
| chain loop map0 | `1.380s` | `1.345s` | `1.026x` |
| chain loop map1 | `0.329s` | `0.303s` | `1.086x` |

Hard bar:

| Gate | Required | Actual | Status |
|---|---:|---:|---|
| writer | `<=1.50s` | `1.763s` | fail |
| hot body | `<=3.60s` | `3.832s` | fail |
| byte equality | true | true | pass |

## Interpretation

The probe is correct but not strong enough to productize.

It shows that removing `OutputChain` object allocation on intersection-bearing
chains helps only modestly. The remaining writer time is not dominated by that
object wrapper. It is dominated by exact text output assembly, point/face id
allocation, and Python loop semantics around the AuthorOfficial output format.

This closes the app-layer writer micro-optimization loop:

- no-xsect fast path: already mostly exhausted;
- direct no-xsect descriptor: small win;
- direct intersection-chain flush: small win;
- exact text writer remains above the hard bar.

## Recommendation

Do not continue with more Python writer micro-edits.

The next rational options are:

1. consolidate the current bounded best route; or
2. separately design a true native/compiled output writer product, with its own
   review, because that would be a larger app-output subsystem and not a small
   continuation tweak.

## Not Authorized

This result does not authorize:

- a new broad performance claim;
- a claim that RTDL has closed the author fused-writer gap;
- moving RayJoin output formatting into RTDL core;
- raw OptiX callbacks;
- public release wording changes.

## Goal-Level Decision Audit

1. **Am I being stupid?**

   No. The probe hit the named remaining writer subphase and preserved
   correctness.

2. **What action would have made this stupid?**

   Calling a 1.03x hot-body improvement a meaningful performance breakthrough.

3. **Was there another path?**

   Yes: jump directly to a native writer. That is too broad without first
   proving app-layer descriptor work can move the number.

4. **Can I start a different path that truly solves the problem?**

   Yes, but it is no longer a small Python/Numba continuation task. It would be
   a separately reviewed native/compiled output writer design. Otherwise, stop
   and consolidate.
