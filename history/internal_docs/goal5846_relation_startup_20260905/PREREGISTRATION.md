# Goal5846 Frozen Relation Startup Experiment

## Question

Can the exact public V4 bounded-relation path load a sealed compiler
executable, overlap app-free CUDA/OptiX initialization with CPU lifecycle work,
retain every generic safety check and two real OptiX launches, and remove the
fresh-process setup debt observed after Goal5845 without regressing its steady
path?

## Frozen design

- The task is the unchanged 4096-by-4096 bounded relation returning exactly
  4096 canonical `(source_id, item_id)` rows.
- One clean Git commit, one DSO built from that commit, one new Numba-leaf
  cache, and one new full-executable cache are bound before worker zero.
- First-ever cache population is measured and preserved separately. It is not
  a registered comparison sample. Both cache manifests are then read-only and
  every worker proves their bytes remained unchanged.
- Eight blocks alternate RTDL/PyOptiX order. Every arm runs in a fresh process,
  performs 16 warmups, and retains all 128 steady samples. No sample may be
  discarded.
- RTDL setup-plus-first includes starting target-bound native initialization,
  route declaration, generic admission, sealed executable materialization,
  native/static prepare, and first public execution.
- The pinned PyOptiX arm is the exact inherited compatible-API contract. Its
  setup-plus-first includes device-source compilation, pipeline construction,
  static prepare, and first execution.
- Correctness checks and traversal-receipt expansion occur outside timing.

## Pass gates

- Every worker, exact output oracle, cache seal, and OptiX provenance check
  passes, and all 2048 registered steady samples are retained.
- Median of eight within-block RTDL/PyOptiX setup-plus-first ratios is at most
  `1.25`; the worst block is at most `2.0` and cannot be hidden.
- Pooled RTDL steady median is at most `1.15x` the frozen Goal5845 value of
  `366,340 ns`; no RTDL worker median may exceed `1.25x` that value.

## Prior diagnostics and stronger sensitivity

Corrected unregistered diagnostics observed approximately `627.851 ms` for
RTDL cached/overlapped setup-plus-first and `365.375 us` steady execution. An
earlier diagnostic accidentally timed correctness/provenance validation inside
the steady interval; those adverse rows remain disclosed but are not valid
execution-only samples.

A stronger PyOptiX sensitivity loaded precompiled PTX, disabled debug
validation, and observed `236.415 ms` setup-plus-first. This is intentionally
not hidden. It is not the frozen Goal5845-compatible primary arm because it
changes the deployment contract, but it demonstrates that passing Goal5846
does not establish general AOT deployment parity. A generic persisted
whole-route deployment artifact remains a separate engineering question.

## Claim boundary

Passing authorizes only an internal statement about this exact task, source
commit, DSO, software stack, GPU, and inherited pinned comparison contract. It
does not authorize public or manuscript wording, an arbitrary-workload claim,
cross-hardware generalization, external consensus, precompiled-PyOptiX parity,
or a claim that every setup performance debt is closed.
