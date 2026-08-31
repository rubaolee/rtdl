# Bounded Sui-derived RT-CCD edge-crossing core

## What this prototype does

A sphere-approximated robot follows a piecewise-linear trajectory. Each sphere
motion segment is a closed capsule and maps to one OptiX round-linear curve.
Each registered obstacle edge maps to one finite ray query. The fixed RTDL
Callback protocol returns one hit bit per edge; after that raw vector is sealed,
the host computes:

```text
collision = OR(per_edge_hit)
```

This is the small collision Boolean needed to show that RTDL's protocol
mechanism can support a robotics-flavoured repurposed-RT application. RTDL did
not invent RT-based collision detection or the Sui et al. algorithm.

## Why the language mechanism matters here

The application does not treat payload words as informal conventions. Its
one-field Callback IR says that make-ray initializes `hit`, closest-hit sets it,
miss preserves zero, and finalize commits only after device status succeeds.
The physical curve/SBT/provider identity and raw output vector are bound in the
receipt. PyOptiX/OWL can construct the same traversal, but that construction
alone does not enforce this cross-role application protocol.

## Exact implemented subset

- piecewise-linear motion of one or more constant-radius spheres;
- deterministic mapping of each path segment to one swept capsule;
- deterministic deduplication of triangle-mesh edges by vertex identity;
- explicit registered obstacle-edge queries;
- per-edge Boolean and aggregate collision Boolean;
- canonical scene normalization and finite frozen-domain oracle inherited from
  Goal5834-B3.

This is **not** complete RT-CCD. It excludes initial overlap/start-inside,
exact tangency, near-parallel contacts and face-interior collision without an
edge crossing. It exposes neither time of impact nor collided primitive ID.

## Evidence status

```text
paper_app_status: NOT_A_PAPER_APP
source_relation: SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES
generalization_exam_count: 0
registered_performance_timing_count: 0
```

Goal5835 does not rerun an identical provider experiment. It proves that this
case-study mapping generates the exact static/query commitments already
executed by Goal5834-B3, then composes those sealed GPU receipts with a separate
active-set oracle. The controlling B3 data contain 11/11 matching primary
executions and 33 functional true-OptiX launches.

Goal5836 is required before any Paper App promotion: paper/source fixture
provenance, author-code same-input comparison and modern-RTX functional
evidence remain absent.
