# Review: Goals5079-5080 RT-BarnesHut Strict Phase And Genericity Review

Date: 2026-07-07

## Verdict

```text
approve_with_required_amendments
```

This verdict applies to both Goal5079 and Goal5080.

The bounded same-input correctness evidence is real and sufficient to close that narrow correctness claim. The phase-boundary and broader-envelope reporting are mostly honest. However, one material issue blocks a clean approval: `ContinuationPayloadOpening` is currently app-neutral in RTDL core but not independently proven generic.

## Evidence Verified

The review independently verified the load-bearing JSON artifacts and calculations rather than relying only on report prose.

### Correctness Evidence

Generic aggregate force gate:

```text
matched = true
mismatch_count = 0
max_abs_error = 1830.0
max_rel_error = 2.111e-06
atol = 0.0001
rtol = 0.0001
```

Legacy author-optix-payload diagnostic:

```text
matched = true
mismatch_count = 0
max_rel_error = 2.623e-06
```

Author new-vs-treelogy:

```text
max_abs_error = 0.0
```

### Phase Boundary Evidence

The timing ratios were verified:

```text
RTDL resident_kernel_min / author rt_core_force
= 0.856544 / 2.083
= 0.4112069216475026

RTDL resident_kernel_mean / author rt_core_force
= 0.9283 / 2.083
= about 0.44566

RTDL broader envelope / author preprocessing+execution
= (55.872 + 252.251 + 160.366 + 0.857) / 185.446
= 2.5309
```

The phase-boundary review gate was also verified to remain blocked:

```text
performance_review_complete = false
phase_boundary_accepted = false
status = blocked_review_incomplete_or_mismatched
```

This is correct governance. The phase boundary was not self-certified.

## Blocking Finding

### BF-1: `ContinuationPayloadOpening` Genericity Is Asserted But Not Proven

Repository search showed that the only functional consumers of `ContinuationPayloadOpening` are:

- RTDL core definition/export,
- Goal5066 contract tests,
- Goal5067 RT-BarnesHut adapter tests,
- RT-BarnesHut app adapter.

No non-RT-BarnesHut consumer exists.

This matters because `ContinuationPayloadOpening` was added after `SizeDistanceOpening` reproduced the geometric opening rule but failed to reproduce the author's linearized payload traversal contract. The fields `node_next_index` and `node_rope_index` are app-neutral names, but they correspond to the author's `nextPrimId` and `autoRopePrimId` payload traversal data after adapter normalization.

Goal5070's non-force genericity proof covered `SizeDistanceOpening` and `LeafOnlyOpening`; it did not cover `ContinuationPayloadOpening`.

Therefore:

```text
app-neutral in core: yes
independently genericity-proven: no
```

Reports must not treat `ContinuationPayloadOpening` as a fully proven generic RTDL capability yet.

## Required Amendments

### RA-1: Downgrade `ContinuationPayloadOpening` Claim

Goal5079 and Goal5080 must describe `ContinuationPayloadOpening` as:

```text
app-neutral in core, provisional / experimental generic, single RT-BarnesHut consumer so far
```

Allowed:

```text
AggregateHierarchy3D, SizeDistanceOpening, and LeafOnlyOpening are genericity-proven by the existing non-RT-BarnesHut tests.
```

Not allowed:

```text
ContinuationPayloadOpening is already a fully proven generic RTDL capability.
```

Future work must add a non-RT-BarnesHut continuation-payload consumer before making broader generic hierarchy traversal claims that depend on this policy.

### RA-2: Tighten Future Summary Wording

The phrase:

```text
The narrow resident force kernel is faster...
```

must not be used as an unconditional claim while the phase-boundary review gate remains blocked.

Allowed wording before phase-boundary acceptance:

```text
On this POD run, in a narrow force-kernel phase comparison pending external phase-boundary acceptance, RTDL resident kernel timing is lower than the author reported RT-core force phase.
```

Any such sentence must remain paired with the broader-envelope result:

```text
The broader reported envelope is about 2.53x slower for RTDL.
```

### RA-3: Disclose Sampling Asymmetry

The narrow ratio uses:

```text
RTDL resident_kernel_min
```

against:

```text
author rt_core_force single reported value
```

Goal5080 already reports an RTDL mean ratio, which is good. Future summaries must also state the author-side sampling basis or prefer mean-to-mean if author repeats become available.

## Non-Blocking Notes

- The correctness closure should be described as same-prepared-state plus payload-matched reproduction. It does not prove independent tree construction or independent traversal discovery.
- The generic route and legacy diagnostic route both match author output but are not bit-identical to each other; the generic route reports `max_abs_error = 1830.0`, while the legacy route reports `max_abs_error = 1139.0`. Both are within tolerance.
- Environment remediation is correctly classified as non-algorithmic build/runtime work: `ninja`, OpenGL dev packages, OptiX headers, CUDA 12.0 via `CUDA_PREFIX=/usr`, and Python `numba`.
- Local tests were not rerun by the reviewer because the shell stalled, but the load-bearing JSON was directly inspected. This does not change the verdict because the review hinges on the live POD artifacts and genericity audit.

## Goal5079 Answers

1. Yes. The live POD evidence proves the generic aggregate force same-input gate matched the patched-author force output.
2. Partially. `ContinuationPayloadOpening` is app-neutral and structurally generic, but its genericity is not yet independently proven.
3. Yes. Author binary sentinel normalization remains app-owned.
4. Mostly yes. The system boundary is preserved, except that the genericity label for `ContinuationPayloadOpening` is premature.
5. Mostly yes. Local regression covers the new opening and adapter behavior, but no non-RT-BarnesHut consumer covers `ContinuationPayloadOpening`.
6. Yes. The full POD gate includes both the generic route and the older author-policy CUDA diagnostic route.
7. Yes. The comparison reports tolerance and error details.
8. Yes. Environment remediation is non-algorithmic.
9. Yes. Narrow timing is not promoted to whole-program timing.
10. Yes. `paper_reproduction_complete` should remain false.
11. Blocking concern: BF-1.

## Goal5080 Answers

1. Yes. It distinguishes bounded same-input correctness from full paper reproduction.
2. Yes, for bounded same-input scalar force correctness.
3. Yes, but the phase is still pending external acceptance.
4. Mostly yes. The narrow kernel appears faster in the reported phase, but the claim must remain pending review and paired with envelope context.
5. Yes. The broader envelope calculation shows RTDL is about `2.53x` slower.
6. Yes. The phase review gate should remain incomplete until external review accepts it.
7. Yes. The report avoids promoting `paper_reproduction_complete=true`.
8. Partially. The app/system boundary is good, but `ContinuationPayloadOpening` genericity is overstated.
9. Blocking concern: BF-1.
10. Allowed future wording must be conditional and must include the broader-envelope caveat.

## Suggested Future Summary

Allowed after RA-1/RA-2/RA-3 are reflected:

```text
RT-BarnesHut bounded same-input scalar force correctness is closed by replaying the author's prepared state through RTDL's app-neutral aggregate-hierarchy API. The continuation-payload opening used for this route is app-neutral in core but not yet independently genericity-proven because it has only a RT-BarnesHut consumer so far. On this POD run, in a narrow force-kernel phase comparison pending external phase-boundary acceptance, RTDL resident kernel timing is lower than the author reported RT-core force phase; however, the broader reported envelope is about 2.53x slower for RTDL. No full paper performance or full paper reproduction claim is authorized.
```
