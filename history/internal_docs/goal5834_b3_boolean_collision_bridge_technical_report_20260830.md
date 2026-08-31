# Goal5834-B3 Boolean collision bridge — technical result

## Outcome

Goal5834-B3 is complete at **registered-fixture Boolean evaluation** scope.
On Home Linux, the fixed public round-linear-curve Callback program produced
raw per-query hit vectors that matched the independent canonical-float32
segment/capsule oracle on all 11 pre-frozen concrete executions from 10 named
fixture families. The result contains zero performance samples.

This closes the bounded Boolean bridge required before Goal5835. It does not
close Goal5834's withdrawn general First Contact numeric contract.

## What executed

The public Callback program has one semantic field, `hit:u32`:

- `make_ray` initializes it to zero;
- `closest_hit` sets it to one;
- `miss` preserves zero;
- `finalize` commits the bit only after the device-status discipline.

The native carrier remains `u32x3` only as a research-prototype economy. The
trusted wrapper writes zero to lanes 1 and 2, and the public runtime rejects any
nonzero padding. Neither provider time nor primitive/application identity is an
application effect or result field.

Every primary execution used `OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR`, the built-in
intersection module, the public
`compile -> materialize -> prepare -> execute -> close` lifecycle, and a true
OptiX traversal receipt. No custom intersection program was used.

The GPU-produced vector was sealed before the host computed
`collision = OR(per_query_hit)`. The application worker contained neither the
expected bits nor the pairwise geometry oracle. A fresh system-Python process,
without Numba or RTDL, recomputed the oracle only after the 115,663-byte raw
receipt existed.

## Frozen cases and result

The corpus is author designed, not representative. Its 10 families produce 11
primary executions because the large-translation family has a base and a
translated/power-of-two-scaled member.

| Execution | GPU/oracle per-query bits | Collision |
|---|---:|---:|
| single crossing | `1` | 1 |
| clear miss | `0` | 0 |
| round endcap | `1` | 1 |
| piecewise-linear OR | `0,1,0` | 1 |
| multiple robust hits | `1` | 1 |
| large-translation base | `1` | 1 |
| large-translation transformed | `1` | 1 |
| face-interior-only method boundary | `0,0,0` | 0 |
| old ordinary-`t` disagreement input | `1` | 1 |
| old near-coincident-ID disagreement input | `1` | 1 |
| old float32 tie-ID input | `1` | 1 |

The two large-translation executions have different original-input digests and
the same normalized-input digest. This repairs the only prior Goal5834
counterexample that changed the application Boolean. The three historical
`t`/ID cases demonstrate only that the new application output does not consume
those unstable fields; B3 did not re-establish an exact normalized `t` or ID
relation and makes no such claim.

Two separately frozen boundary inputs—start-inside and near-tangent/parallel—
were marked evaluator-ineligible and launched no B3 worker. Malformed shape was
rejected by the public batch constructor before prepare or launch. Face-only
triangle intersection remains a declared method boundary because the current
predicate registers obstacle edges only.

## Normalization and oracle

For each static swept-volume scene, the preaction authority computes binary64
radius-expanded bounds, a midpoint origin, and the smallest enclosing
power-of-two scale. Scene values and every later query are transformed in that
fixed frame and only then projected to binary32. The result binds exact f64
origin/scale bits, original and normalized input digests, and the public RTDL
static/query commitments.

The normative oracle evaluates the exact canonical binary32 values in
binary64. All 21 query/capsule pairs satisfy the frozen `2^-10` decision
separation and endpoint-disjoint rules; contacted pairs also satisfy the
`2^-12` cross-ratio and entry-endpoint rules. A post-result active-set
implementation independently recomputed all 21 squared distances and Boolean
decisions with zero mismatch.

## B1 and B2 failures

Neither failed predecessor is erased.

- B1 incorrectly reused one intentionally single-use `VerifiedCurveExecutable`
  across 11 static-scene prepares. It failed on the next prepare with live
  registry drift and emitted no complete raw receipt.
- B2 materialized once per scene but predicted that all raw executable hashes
  would be equal. Repeated NVRTC calls in one process incremented PTX `callseq`
  comment numbers. Wrapper source, generated leaves, the four compiled leaf
  PTX digests and compiler log were equal, but raw wrapper/composed PTX bytes
  correctly differed. The identity check was not weakened.

B3 materialized the exact target-bound executable once in a parent that had
not loaded the native OptiX provider. Eleven sequential children inherited the
same unconsumed live object, consumed it once for one static scene, sealed
primary/repeat/reverse receipts, and exited. This is evidence-harness
orchestration, not a claimed user-facing language feature. A Goal5835
application has one swept-volume static scene and one obstacle-edge query
batch, so it does not need this multi-fixture fork harness.

## Evidence and exact scope

- 11/11 primary executions match.
- 11/11 repeats and 11/11 reversed-query runs preserve their result.
- 33 successful functional OptiX launches; zero status failures.
- Home and local evaluator output are byte-identical (`786ebd49...`).
- 24/24 source projection members, 13/13 materialized artifacts, and 11/11
  preaction source members rehash; the source archive and twin are identical.
- 95/95 adjacent Goal5833/5834 tests pass.

Safe paper sentence:

> On one pinned OptiX provider, RTDL's public round-linear-curve lifecycle
> produced per-edge hit vectors whose host-OR collision results matched an
> independent canonical-float32 segment-capsule oracle on every pre-frozen
> executed fixture. The small author-designed corpus is a case study, not a
> representative sample or a generalization test.

The hardware is one GTX 1070. This proves behavioral OptiX execution, not
RT-core silicon behavior or cross-GPU numeric stability. Generalization exams,
external users, Paper App status, full RT-CCD, arbitrary capsule correctness,
exact TOI/ID, and performance evidence all remain zero or false.

Goal5835 is now authorized only to express the same registered fixtures as a
Sui-derived sphere-trajectory/obstacle-edge mapping through this public
Boolean lifecycle. Goal5836 remains the only promotion gate for paper-source
fixtures, author-code same-input comparison, modern RTX, or Paper App status.
