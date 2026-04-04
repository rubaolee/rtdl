# Codex Review: Goal 69 PIP Performance Direction

Date: 2026-04-04

Verdict:
- `APPROVE-WITH-NOTES`

What is technically sound:
- keeping `full_matrix` as the default preserves the accepted Goal 50 / Goal 59 contract
- adding an explicit `positive_hits` mode is the right way to measure the query shape that most closely matches indexed PostGIS positive-hit joins
- bbox pruning in the Python reference path and native oracle is a real improvement, even if it does not by itself change the asymptotic shape as strongly as a true spatial index
- the Embree sparse-path repair is important:
  - it now uses scene traversal to discover candidate polygon ids
  - it no longer scans every polygon after each point query

Current limits:
- the Linux benchmark is still blocked by host reachability:
  - SSH to `192.168.1.20` is timing out during banner exchange
- the OptiX sparse path is still only locally patched
- no accepted package timings exist yet for Goal 69

Required next steps before publication:
1. restore stable SSH access to `192.168.1.20`
2. rebuild the latest OptiX local patch there
3. run narrower Goal 69 passes:
   - `county_zipcode` first
   - likely `cpu,embree` first, then `optix`
4. compare positive-hit outputs against filtered `full_matrix` outputs on the same inputs
5. get final Gemini result review on measured data, not just design
