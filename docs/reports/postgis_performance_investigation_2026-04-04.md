# PostGIS Performance Investigation

Date: `2026-04-04`

Source:

- Gemini 3.1 Pro investigation requested on the accepted bounded package timing
  deltas between PostGIS and RTDL

## Timing Evidence

### County ⊲⊳ Zipcode `top4_tx_ca_ny_pa`

#### LSI

- PostGIS: `34.0323 s`
- Native Oracle: `89.3365 s`
- Embree: `80.2707 s`
- OptiX: `53.2900 s`
- Rows: `107513`

#### PIP

- PostGIS: `0.4300 s`
- Native Oracle: `24.4170 s`
- Embree: `16.8128 s`
- OptiX: `19.2551 s`
- Rows: `16352128`
- Hits: `7817`

### BlockGroup ⊲⊳ WaterBodies `county2300_s10`

#### LSI

- PostGIS: `0.2320 s`
- Native Oracle: `0.2286 s`
- Embree: `0.2228 s`
- OptiX: `0.8933 s`
- Rows: `216`

#### PIP

- PostGIS: `0.0084 s`
- Native Oracle: `0.1496 s`
- Embree: `0.1172 s`
- OptiX: `0.6477 s`
- Rows: `71176`
- Hits: `197`

## Gemini Investigation Summary

Gemini’s main conclusions were:

1. PostGIS is faster primarily because it benefits from:
   - GiST-assisted spatial pruning
   - short-circuit boolean query behavior
   - in-database pipelined execution
   - no host/device transfer penalty

2. RTDL is currently paying for:
   - full-matrix semantics in important PIP paths
   - row-oriented output materialization
   - host-side exact finalization
   - flexibility and audit-oriented execution contracts

3. Gemini’s proposed action directions included:
   - short-circuiting for PIP
   - moving exact finalization to device
   - columnar materialization
   - device-side AABB pruning

## Accepted Reading

The strongest accepted interpretation is:

- the biggest PostGIS advantage is not that “database geometry is inherently
  better”
- the biggest advantage is that PostGIS is executing a more query-aware and
  index-aware plan for these accepted workloads

For the accepted bounded packages, RTDL often does more work than PostGIS
because it currently preserves richer row semantics and more explicit auditing
behavior.

That is especially visible in PIP:

- PostGIS can answer “which points hit which polygons?” very cheaply with an
  indexed positive-hit path
- RTDL often pays for full matrix semantics and later comparison shaping

So the largest timing gaps are partly architectural and partly semantic, not
just backend speed gaps.

## Current Practical Action Direction

The most realistic next engineering actions are:

1. add query-aware fast paths for boolean/positive-hit PIP-like workloads
2. reduce or avoid full-matrix materialization when the workload contract does
   not require it
3. redesign GPU backends so host exact refine consumes GPU-produced candidates
   instead of full Cartesian recomputation

More aggressive ideas such as device-side exact finalization or a broader
columnar runtime redesign are still interesting, but they should be treated as
later architecture work rather than the immediate next step.
