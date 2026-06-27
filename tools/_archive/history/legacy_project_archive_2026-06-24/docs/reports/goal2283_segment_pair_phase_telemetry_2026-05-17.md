# Goal2283: Segment-Pair Phase Telemetry

Status: implemented locally; pod timing must be recorded separately.

## Purpose

Goal2280 rejected direct-index host exact refinement after same-pod A/B evidence
showed it was neutral or regressive. That result says the next v2.0 RayJoin/LSI
work should stop guessing at host metadata micro-optimizations and measure the
generic prepared segment-pair path by phase.

Goal2283 adds read-only phase telemetry for the OptiX segment-pair intersection
primitive. The telemetry can be read after either:

- `PreparedOptixSegmentPairIntersection.run_raw(left)`, or
- `PreparedOptixSegmentPairIntersection.count(left)`.

## Recorded Fields

The optional native/Python surface reports:

- `mode`: `rows`, `count`, or `none`;
- `left_upload`: host-to-device upload time for the left/query segment batch;
- `candidate_count_pass`: first OptiX pass that counts candidate hits;
- `candidate_write_pass`: second OptiX pass that writes candidate rows;
- `candidate_download`: copyback time for candidate rows;
- `exact_refine`: host exact segment-intersection refinement time;
- `raw_candidate_count`: candidate rows emitted by the OptiX passes;
- `emitted_count`: final exact row count or scalar count.

## Boundary

This is instrumentation, not an optimization. It does not change the public
segment-pair result contract and does not authorize a speedup claim. The goal is
to guide the next generic device-resident or partner-continuation design without
adding RayJoin-specific native engine logic.

## Expected Measurement

Pod evidence should run the same RayJoin-exported 100k LSI stream used by
Goals 2273, 2276, and 2280, then record phase dictionaries for both raw rows
and scalar count. The useful outcome is a bottleneck diagnosis, not a release
claim.
