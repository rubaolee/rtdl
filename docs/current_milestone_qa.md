# Current Milestone Q/A

Date: 2026-04-05

## What is the current strongest RTDL result?

The strongest current result is the long exact-source `county_zipcode`
positive-hit `pip` surface:

- OptiX is parity-clean and faster than PostGIS on the accepted prepared and
  repeated raw-input boundaries
- Embree is parity-clean and faster than PostGIS on the same boundaries

## Is Vulkan a failure?

No.

Vulkan is now:

- hardware-validated
- parity-clean on the accepted long exact-source prepared and repeated raw-input
  boundaries
- slower than PostGIS, OptiX, and Embree on those boundaries

So Vulkan is a supported portable backend, not the current flagship performance
backend.

## What is RTDL doing in Python?

Python owns:

- DSL authorship
- lowering/orchestration
- dataset ingestion
- cache management
- public API boundaries

Recent performance work explicitly reduced Python hot-path cost by reusing
prepared and prepacked geometry automatically.

## Does the CPU still matter when using OptiX or Vulkan?

Yes.

For the mature positive-hit `pip` story, the accelerator usually does
candidate generation and the CPU exact-finalizes the candidate subset for
trusted final truth.

## Are the internal oracles still important?

Yes.

Accepted oracle trust boundary:

- Python oracle on deterministic mini envelopes
- native C oracle on deterministic small envelopes

They matter for:

- quick verification
- demos
- trustable sanity checks

## Are all RTDL workloads equally mature?

No.

The current milestone performance closure is strongest for:

- long exact-source `county_zipcode`
- positive-hit `pip`

Other workloads exist and work, but they are not all documented with the same
depth of performance closure yet.

## Why do the reports distinguish prepared and repeated raw-input timing?

Because they measure different things.

- prepared:
  - backend execution after packing/binding work is already done
- repeated raw-input:
  - what ordinary RTDL calls achieve after runtime-owned caching kicks in

Mixing these would make the performance claims misleading.

## Can RTDL honestly claim performance now?

Yes, with explicit boundaries.

Safe current claim:

- RTDL + OptiX and RTDL + Embree beat PostGIS on the accepted long exact-source
  `county_zipcode` positive-hit `pip` surface under the published prepared and
  repeated raw-input boundaries
