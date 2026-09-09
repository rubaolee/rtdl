# Authored Particle RTDL versus public PyOptiX formal report

Date: 2026-09-09

## Verdict

The complete-output successor transaction passes its internal prepared-path
engineering targets on one NVIDIA RTX 4000 Ada Generation GPU:

- paired median RTDL / public PyOptiX: `1.1036103663738503x`;
- worst paired block: `1.1453657239706225x`;
- deterministic block-bootstrap 95% interval: `[1.077594013937506,
  1.1384719450739]`;
- required limits: paired median at most `1.20x` and every block at most
  `1.35x`;
- all eight blocks pass;
- 16 fresh primary workers retain 3,440 timed calls and 16 warmups;
- two fresh lifecycle workers retain one complete first execution each;
- retry count and discard count are both zero.

This is an internal engineering result. It is not externally reviewed and does
not authorize a paper or public performance claim.

## Exact identity

- Source commit: `7ac37e3fb02269d2b812b3bb8d7da741c64bb0bf`.
- Source tree: `3e907a05b57ac0b975ef07732e1e0921f0ef36d8`.
- GPU: NVIDIA RTX 4000 Ada Generation, compute capability 8.9.
- GPU UUID: `GPU-2a00572b-6cef-b9e6-db0a-c127783a5d46`.
- Driver: `550.127.05`.
- Exact native SHA-256: `e3cd7c002fb01b688ad88af74712675abc2ee79f7bdebe79b9ac854a9919723e`.
- Exact public-PyOptiX PTX SHA-256:
  `d563ac854f1c823a6f4471f3644b23d96f9e3500865718083fd8f5fec12011bc`.
- Input manifest SHA-256:
  `c6678099ecff9581726781a765213d5b0890f20ada70561b09dd6dd94a4009af`.
- Complete public output digest:
  `452ec9df2d8ee3c3a274dcbe4e175df305380f25793472e05da448e9556ed73b`.
- Independent oracle digest:
  `7351cc39534961f5c0626cbf6f6e6039305ca200307bca63decc06ce4f810c99`.

The native and public-PyOptiX PTX were both built create-only from the exact
source commit. Their manifests bind compiler/header/toolchain identities and
the visible target. The preregistration revalidated both manifests and all
source-closure files before formal worker zero.

## Workload and output contract

The workload uses the complete real Particle mesh prepared for the V4 paper-app
path:

- 314,587 vertices;
- 3,392,530 indexed triangles;
- 5,000 distinct strict-interior ray queries;
- seven `float32` query columns;
- one complete `(face_id, selected_cell, neighbor_cell)` `uint32[5000,3]`
  result per execution.

The 5,000 query rows and their first three origin columns are both pairwise
distinct. The transaction is nevertheless a short prepared workload, not a
natural at-least-one-second task and not a full 50,000-step particle advection.

Each of the 18 workers retains one complete 60,000-byte output after its timed
population. It does not retain one complete output for each of the 3,440 timed
calls. Every timed call synchronously checks its full output against the same
independent oracle before successful return. The independent recount decodes
all 18 retained outputs and compares every byte with the preserved oracle.

## Same-contract comparison

Both arms use the same mesh, indexed triangles, primitive metadata, resident
query batch, query count, full output, independent oracle, GPU, process-level
freshness and paired block schedule. Preparation is excluded from the primary
timer for both arms.

RTDL arm:

- public source verify, compile, materialize and prepare path;
- generic `provider_native_closest` built-in-triangle selection policy;
- prepared query columns remain device-resident;
- each timed call executes one complete native OptiX traversal, status check,
  complete 60,000-byte output transfer, synchronization and oracle check;
- each worker records `physical_executor_classification =
  optix_traversal_observed` and role counters
  `[0,5000,0,0,5000,0,5000]`.

Public PyOptiX arm:

- handwritten CUDA/OptiX device source compiled to an exact prebuilt PTX;
- public PyOptiX creates the module, program groups, pipeline, SBT and triangle
  GAS;
- seven query columns are uploaded once during preparation: seven H2D calls and
  140,000 bytes;
- each timed call performs zero query H2D, one real OptiX launch, status D2H and
  synchronization, complete 60,000-byte output D2H and synchronization, and
  exact oracle comparison.

The RTDL timer is conservative relative to the public PyOptiX exact-core
endpoint: RTDL returns its public result, traversal receipt and output digest
inside the timed public execute and the worker performs an additional complete
array comparison. PyOptiX performs traversal, complete D2H and its first exact
oracle comparison inside the timer, while freezing counters and rechecking the
borrowed completion after the timer. The result therefore supports a bounded
public-API overhead observation, not an assertion that every host-side
instruction is identical.

## Paired results

| Block | Order | RTDL median ns | PyOptiX median ns | RTDL / PyOptiX |
|---:|---|---:|---:|---:|
| 0 | RTDL, PyOptiX | 167,685 | 155,335 | 1.079506x |
| 1 | PyOptiX, RTDL | 172,326 | 150,455 | 1.145366x |
| 2 | RTDL, PyOptiX | 168,306 | 147,835 | 1.138472x |
| 3 | PyOptiX, RTDL | 167,316 | 150,655 | 1.110590x |
| 4 | PyOptiX, RTDL | 166,945 | 150,235 | 1.111226x |
| 5 | RTDL, PyOptiX | 167,776 | 155,695 | 1.077594x |
| 6 | PyOptiX, RTDL | 166,606 | 157,005 | 1.061151x |
| 7 | RTDL, PyOptiX | 168,415 | 153,575 | 1.096630x |

The balanced order has four RTDL-first and four PyOptiX-first blocks. No row,
sample or block was removed based on its value.

## Adverse lifecycle result

The lifecycle endpoint includes preparation, one complete first execution and
close in a fresh process:

- RTDL: `4,698,472,585 ns`;
- public PyOptiX: `480,718,877 ns`;
- RTDL / public PyOptiX: `9.773846648838797x`.

This single worker per arm is diagnostic rather than a replicated lifecycle
estimate. It is still a material adverse observation and must remain visible.
The prepared result cannot be generalized to first-result, startup, compile,
materialization, full-application or end-to-end superiority.

## Why the native-closest policy is generic

The earlier canonical-distance path collected and canonically reduced hit
information in a provider-independent order. The new physical policy delegates
nearest-hit selection to the provider's standard closest-hit semantics and
returns the selected primitive plus its two generic primitive metadata values.
The policy is expressed as a typed built-in-triangle contract and contains no
Particle names, cell-transition rule, advection rule or application formula in
the runtime or native engine. Particle owns only the mapping from the generic
three `uint32` fields to `(face, selected cell, neighbor cell)`.

This contract difference is real. The formal row compares the new generic
provider-native-closest RTDL contract with a public PyOptiX implementation of
the same closest-hit output contract. It must not be described as the older
canonical-distance route.

## Performance remediation

The material fixes before the final transaction were:

1. Add the generic provider-native closest physical policy instead of forcing
   canonical all-hit behavior for a closest-hit workload.
2. Make the public PyOptiX comparator competent by uploading immutable query
   columns once and replaying a resident prepared batch. An earlier diagnostic
   that uploaded all query columns every timed call was rejected before formal
   worker zero.
3. Cache the digest of an immutable prepared output only after byte-for-byte
   equality with the prior output; changed bytes force a new SHA-256.
4. Reuse generic traversal-audit/error buffers and preserve unique nonces.
5. Register owner-private prepared-batch authority so repeated public execute
   avoids rescanning already admitted immutable device pointers and layouts.
6. Bind the public PyOptiX PTX build to the exact source commit, source bytes,
   options, headers and Python CUDA bindings.
7. Retain one complete post-population output from every worker and independently
   compare all 18 outputs byte-for-byte with the preserved oracle.

None of these changes embeds Particle-specific native logic.

## Predecessor preservation

The predecessor source `832c97e0212b56b6e872fbfd8e5a71595dddc34d`
passed at `1.1265194287556206x` paired median and `1.1660222378042673x`
worst block, with lifecycle `9.431897022143808x`. Its transaction archive is
preserved separately. It validated complete outputs on every timed call but
retained only output hashes, not one complete worker output byte vector. It is
not pooled with or substituted for this successor.

## Claim boundary and next work

Authorized internally by this result:

- the exact 5,000-query prepared path met the stated engineering overhead
  thresholds against the exact competent public PyOptiX arm on this GPU;
- the public language/runtime path produced the complete correct output through
  observed OptiX traversal;
- the generic provider-native closest contract removed the previous avoidable
  prepared overhead without app-specific engine semantics.

Not authorized:

- a public or paper claim before independent review;
- at-least-one-second natural-task competitiveness;
- startup or lifecycle competitiveness;
- full advection, throughput scaling, cross-GPU or cross-generation claims;
- productivity, arbitrary callback, universal app or portfolio-wide claims.

The next Particle task is a deterministic natural distinct-query scale ladder
on the same real mesh, selecting a single batch whose complete prepared
execution lasts at least one second. The batch must preserve full-output
correctness and same-contract resident-query fairness. The next portfolio task
after Particle is RTNN distinct top-K correctness under duplicate logical
candidate delivery.
