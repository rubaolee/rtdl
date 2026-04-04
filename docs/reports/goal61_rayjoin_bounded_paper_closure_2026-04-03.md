# Goal 61 RayJoin Bounded Paper Closure

Date: 2026-04-03

## Result

Under the accepted bounded/analogue rule, the RayJoin paper experiment program
is now closed as far as the currently stable and available dataset families
allow.

This closure is intentionally not a claim of:

- paper-identical reproduction
- nationwide closure
- full original continent-family coverage
- full polygon overlay materialization

It is a claim of:

- bounded accepted closure on the finishable paper surfaces
- explicit deferral of unstable or unavailable dataset families
- honest analogue labeling where fidelity is lower than the original paper

## Finished Under The Current Rule

### Figure 13

Accepted status:

- done as a scaled bounded analogue

Why:

- deterministic synthetic scalability generator exists
- accepted Figure 13-style LSI query-time and throughput outputs exist

### Figure 14

Accepted status:

- done as a scaled bounded analogue

Why:

- deterministic synthetic scalability generator exists
- accepted Figure 14-style PIP query-time and throughput outputs exist

### Table 3

Accepted status:

- closed as a bounded package for the stable and available families

Accepted bounded rows:

- `County ⊲⊳ Zipcode` on `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` on `county2300_s10` as the accepted bounded
  practical analogue for `Block ⊲⊳ Water`
- bounded `LKAU ⊲⊳ PKAU` on `sunshine_tiny`

Cross-system acceptance surface where applicable:

- PostGIS
- native C oracle
- Embree
- OptiX

Important naming boundary:

- public descriptions must preserve the `county2300_s10` qualifier for the
  `BlockGroup ⊲⊳ WaterBodies` package
- this is not a claim of nationwide `Block ⊲ Water` completion

### Table 4

Accepted status:

- done as a bounded overlay-seed analogue package

Accepted bounded surface:

- first four-system accepted `overlay-seed analogue` on bounded
  `LKAU ⊲⊳ PKAU`
- earlier bounded Embree overlay-seed analogue rows remain useful supporting
  context

Important system-coverage boundary:

- four-system overlay-seed closure is currently established on bounded
  `LKAU ⊲⊳ PKAU`
- County/Zipcode and BlockGroup/WaterBodies remain useful overlay analogue
  context from the earlier Embree package, but they are not claimed here as the
  same four-system overlay closure

### Figure 15

Accepted status:

- done as a bounded overlay-seed speedup analogue

Boundary:

- Figure 15 closure is only for the current RTDL overlay-seed semantics
- it is not a claim of full polygon overlay materialization

## Deferred Because Data Is Unavailable Or Unstable

The following continent-pair families are explicitly deferred under the current
closure rule:

- `LKAF ⊲⊳ PKAF`
- `LKAS ⊲⊳ PKAS`
- `LKEU ⊲⊳ PKEU`
- `LKNA ⊲⊳ PKNA`
- `LKSA ⊲⊳ PKSA`

Reason:

- their public acquisition/staging path is not currently stable enough to
  justify more v0.1 time

## Final Honest Position

The RayJoin experiment program is now complete **as a bounded RTDL paper-facing
closure package** under the accepted rule:

- bounded analogues count when they are implemented, reviewed, and clearly
  labeled
- unavailable dataset families do not block closure if they are explicitly
  deferred

So the finished v0.1 paper-facing status is:

- Figure 13: done-bounded
- Figure 14: done-bounded
- Table 3: done-bounded for currently stable and available families
- Table 4: done-bounded as an overlay-seed analogue
- Figure 15: done-bounded as an overlay-seed speedup analogue

## Source Basis

- `docs/rayjoin_paper_reproduction_matrix.md`
- `docs/rayjoin_paper_dataset_provenance.md`
- `docs/reports/goal23_embree_reproduction_report_2026-04-01.md`
- `docs/reports/goal50_postgis_ground_truth_2026-04-02.md`
- `docs/reports/goal54_lkau_pkau_four_system_2026-04-03.md`
- `docs/reports/goal56_overlay_four_system_closure_2026-04-03.md`
- `docs/reports/goal59_bounded_v0_1_reproduction_package_2026-04-03.md`
