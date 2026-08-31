# Strict self-review — Goal5834-B3 Boolean collision bridge

## Verdict

`P0=0 / P1=0 / P2=3 / P3=1`

Accept Goal5834-B3 only at
`COMPLETE_REGISTERED_FIXTURE_EVALUATION` scope. Authorize Goal5835 only for the
same frozen Sui-derived edge-crossing mapping. Do not promote this result to a
Paper App, general capsule contract, new-app generalization result, usability
result, or performance result.

## Hostile questions

### Did the CPU compute collision before or instead of the GPU?

No. `WORKER_INPUTS.json` contains no expected bit or pairwise result. The
Boolean public verifier accepts only query shapes and finite f32 values and has
no static-geometry arguments. The raw worker source imports no oracle. Each raw
vector is sealed into the traversal receipt before host OR. The standalone
oracle runs only after the raw result file exists.

### Is this just First Contact with `t` and ID hidden in prose?

No. The Callback IR payload and output each have one field. The closest-hit,
miss, finalizer, physical schema and semantic digest are Boolean-specific.
Physical lanes 1 and 2 are fixed zero carrier padding and are rejected if
nonzero. The application result has no provider `t`, primitive index, or
application ID.

### Did normalization tune away a bad result?

No. The transform algorithm, exact `2^-10` margin, 10 family names, 11 concrete
inputs and expected bits were frozen at `0f13ab8a...` before worker zero. The
large-translation pair's normalized bytes were equal before either ran. B1 and
B2 failures did not change any fixture, margin, normalization, oracle or
expected output; B3 inherits `WORKER_INPUTS.json` byte-for-byte at
`55eeff37...`.

### Were failed attempts silently called infrastructure-invalid?

No. B1 and B2 have separate terminal-negative records. B1 disproved the
assumption that one live executable can prepare multiple static scenes. B2
disproved the assumption that repeated same-process NVRTC materializations are
raw-byte-identical. B3 does not weaken either check; it preserves the one exact
materialized object across fork-private child copies.

### Is the independent oracle itself trusted without challenge?

It is still part of the evaluation TCB, but it received a second algorithmic
check. An active-set enumeration independently minimized the segment/segment
quadratic for all 21 frozen pairs and reproduced every squared distance and
hit bit. Home and Windows evaluators also produced byte-identical result JSON.
This is strong for the finite corpus, not a formal proof of the oracle for all
floating-point inputs.

### Does 11/11 prove generalization?

No. The fixture corpus is small, author designed and partly constructed from
known counterexamples. `generalization_exam_count` remains 0. The result shows
that the mechanism can execute this bounded Boolean protocol and mapping on
these inputs; it does not estimate an input-class success rate.

## Open P2 findings

1. **Single provider and non-RT-core silicon.** All data are from one GTX 1070
   with one OptiX 9 provider. Goal5836 still owes modern-RTX functional evidence
   and cannot infer cross-provider/cross-GPU numeric stability.
2. **Bounded edge predicate, not full collision detection.** Start-inside,
   initial overlap, tangency, near-parallel contact and face-interior-only
   collision are unsupported or deliberately excluded. Goal5835 must put these
   limits next to its positive result.
3. **No external/generalization/usability evidence.** All code and fixtures are
   author produced. The fork-based multi-fixture evidence harness also says
   nothing about public API ergonomics. No claim may imply otherwise.

## P3 finding

The B3 evidence runner relies on POSIX fork so each child can consume an exact
single-use live executable without recompilation. This is appropriate for the
finite Home evidence campaign and is not needed by the one-scene Goal5835 app,
but it is not a portable general test runner.

## Authorization decision

Goal5835 may begin because the prerequisite question has a finite positive
answer: on the exact registered inputs, the public Boolean curve path returns
the independently expected obstacle-edge/capsule bits and collision OR. The
authorization is narrow:

- reuse exact fixture authority `0f13ab8a...` and worker inputs `55eeff37...`;
- add only the paper-to-RTDL mapping, deterministic triangle-edge
  deduplication, identity reconstruction, README and functional receipt;
- do not add a new GPU fixture, change the oracle, claim full Sui RT-CCD, call
  it a Paper App, measure performance, or request external review.

Within that scope there is no remaining P0/P1 blocker.
