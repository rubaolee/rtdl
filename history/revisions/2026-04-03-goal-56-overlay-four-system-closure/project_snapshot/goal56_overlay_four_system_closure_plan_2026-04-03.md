# Goal 56 Plan: Overlay Four-System Closure

Date: 2026-04-03

## Decision

The coordinated review for the next v0.1 slice converged on `overlay` as the
highest-value remaining workload class.

Review outcome:

- Gemini: recommended `overlay`
- Claude: recommended `overlay`
- Codex sub-agent suggested a `Block ⊲⊳ Water` closure, but that path is weaker
  because bounded four-system `BlockGroup ⊲⊳ WaterBodies` is already closed

So the accepted next direction is:

- first bounded four-system `overlay` closure

## Why Overlay Now

1. `lsi` and `pip` already have accepted bounded four-system entries.
2. Table 4 / Figure 15 remain structurally open.
3. The repo already has:
   - accepted bounded packages
   - Linux host
   - PostGIS ground truth
   - Embree and OptiX bring-up
   - test matrix
4. This is therefore a better v0.1 closure step than starting another new
   dataset family first.

## Resolved Design Question

The key issue was semantics, not infrastructure.

That question is now resolved:

- RTDL `overlay` is currently an `overlay-seed analogue`
- it emits one row for every left/right polygon pair
- the row schema is:
  - `left_polygon_id`
  - `right_polygon_id`
  - `requires_lsi`
  - `requires_pip`

So the accepted Goal 56 comparison contract is:

- compare exact rows on that four-field schema only
- do not compare full overlay geometry
- derive PostGIS truth from indexed seed predicates:
  - boundary segment intersection aggregated to polygon-pair `requires_lsi`
  - first-vertex `ST_Covers(...)` checks aggregated to polygon-pair
    `requires_pip`
- compare the full left × right polygon pair matrix, not positive rows only

## Accepted First Package

The first bounded package is:

- `LKAU ⊲⊳ PKAU`
- Goal 37 / Goal 54 `sunshine_tiny`

Reason:

- polygon-vs-polygon workload matches the current overlay kernel directly
- the package is already four-system closed for `lsi` and `pip`
- the runtime/debug cost is much lower than `County ⊲⊳ Zipcode top4`

## Planned Next Step

1. implement a bounded `LKAU ⊲⊳ PKAU` overlay four-system harness
2. run it on `192.168.1.20`
3. write the result report
4. get Gemini and Claude final review
5. publish only after at least 2-AI consensus
