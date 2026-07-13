# Goal4844 RayJoin Reproduction POD Plan

## Current State

This line is no longer a broad unknown.

Resolved so far:

- The public County x Soil sample passed byte-for-byte after the directed point-location / overlay correctness repairs.
- The County x Zipcode same-source prefix reached a 60,000-chain byte-line match against the author intended baseline after fixing midpoint materialization.
- The main current County x Zipcode full-output mismatch has moved beyond the first 60,000 chains.

Current known remaining issues:

1. Some full-output coordinate lines differ by the final printed decimal place.
2. A later structure mismatch appears around output chain 2,272,427.
3. The second mismatch window shows duplicate / near-duplicate intersection points around the same scaled coordinate:
   - RTDL emits a 1-point chain and adjacent duplicate-point chains.
   - This likely comes from zero-length / same-internal-coordinate intersection span handling, not from LSI count failure.

The latest diagnosis narrowed the current mismatch to overlay output construction, not broad LSI failure.

## What Went Wrong In Debugging Efficiency

The internal diagnostic script `goal4840_chain_prefix_probe_scaled_points.py` uses `load_cdb()` and `_packed_overlay_inputs()` directly. That means every small window probe reloads and repacks the large CDBs:

- load: about 321 seconds
- pack: about 62 seconds
- LSI: about 27 seconds
- sort: about 30 seconds
- PIP: about 14 seconds

This was wasteful. Remaining debugging must not repeatedly reload full CDBs for every small question.

New rule:

- Use full CDB runs only as gates.
- Use cached packed inputs, focused windows, or single prepared sessions for debug probes.
- Do not start another full output run until a focused hypothesis has passed.

## Required Paper / Source / Code Understanding

Before claiming reproduction, we must explicitly map the paper and author source to RTDL behavior:

- LSI: RT traversal candidate generation, exact intersection refinement, `xsect_factor`, `enlarge`, sorted intersection rows.
- PIP: directed segment point-location, endpoint exclusion, equal-height SoS tie-break, reported-distance perturbation.
- Overlay: sorted intersections per edge, midpoint classification, output-chain flush/dedupe, dynamic face-pair renumbering.
- Engineering controls: grid size, serialized topology, data preprocessing, CDB scale/unscale contract.

This mapping must be checked against:

- the paper,
- author source code,
- author clarification,
- RTDL code paths,
- focused synthetic tests.

## POD Plan And Time Estimate

### Phase 1: Stop Expensive Debug Loop

Purpose:
Make remaining debug probes reuse loaded/packed state or operate on small windows.

Work:

- Add or adapt a focused debug runner that can emit a chain window without writing a 2GB full output.
- Prefer packed cache where possible.
- Keep current full-output artifacts for comparison; do not rerun full output as a probe.

POD time:
1-2 hours.

Exit gate:
One chain-window probe can be produced without a fresh 5-minute CDB load for each question, or a documented reason why cache reuse is not available.

### Phase 2: Resolve Current Chain-2,272,427 Structure Mismatch

Purpose:
Determine why RTDL emits a 1-point / duplicate-point chain where the author emits normal 2-point chains.

Work:

- Patch author probe only for diagnostics, not algorithm changes.
- Print author midpoint/span events around the same edge IDs:
  - `eid0=2590075/2590076/2590077`
  - `eid1=11674551/11674552/11674553`
- Compare author and RTDL:
  - sorted intersections,
  - exact/scaled coordinates,
  - midpoint point,
  - midpoint face,
  - output-chain flush/dedupe behavior.
- Fix only the proven generic bug:
  - likely zero-length same-internal-coordinate span handling or output dedupe contract.

POD time:
4-8 hours.

Exit gate:
A focused window around chain 2,272,420-2,272,460 matches the author output line-for-line, or the exact remaining product gap is documented.

### Phase 3: Full County x Zipcode Correctness Gate

Purpose:
Check whether the current repaired implementation reproduces the large same-source pair exactly.

Work:

- Run one complete RTDL output for County x Zipcode.
- Compare against the author intended baseline.
- If mismatch appears, do not loop full runs; return to focused window diagnosis.

POD time:
3-5 hours for one full gate, including compare.

Exit gate:
Either byte-line equality for the full County x Zipcode output, or a first-mismatch report with focused next bug.

### Phase 4: Revalidate Existing Section 5.7 Evidence

Purpose:
Confirm the historically reproduced pairs still hold under the repaired implementation.

Work:

- Revalidate County x Zipcode.
- Revalidate Block x Water if the required same-source/generated CDBs and author baseline are present.
- Preserve labels:
  - exact paper input only if exact author/paper files exist,
  - same-source regenerated CDB if only regenerated from same source.

POD time:
4-8 hours, depending on whether Block x Water inputs are ready and cached.

Exit gate:
Correctness table with pair, input provenance, author baseline, RTDL output, equality status.

### Phase 5: Bounded Performance Runs

Purpose:
Only after correctness passes, compare runtime honestly.

Work:

- Run author patched/intended binary and RTDL on the same available pairs.
- Record wall time, phase times, input size, output chain count, and exact correctness status.
- No broad RayJoin or RTDL performance claim unless all required pairs are covered.

POD time:
4-6 hours.

Exit gate:
Bounded performance table with correctness attached to every timing row.

### Phase 6: Closure Packet And Review

Purpose:
Turn results into a scientifically honest reproduction packet.

Work:

- Write the contract mapping.
- Write the bug/fix ledger.
- Write the input availability table.
- Write the correctness/performance table.
- Send to Antigravity and Claude when available; debt allowed only for unavailable reviewers.

POD time:
0-1 hour.

Local/documentation time:
2-4 hours.

## Total Estimate

If the current chain-2,272,427 mismatch is the last structural bug:

- POD active time: 16-24 hours.
- Calendar time with reviews/docs: about 1-2 days.

If one more structural mismatch appears after the next full gate:

- Add 6-10 POD hours per additional mismatch cycle.

Hard stop rule:

- After two more structural mismatch cycles, stop and produce a gap report instead of continuing open-ended debugging.

## Current Recommendation

Keep the POD for at least 24 more hours if the goal is serious RayJoin reproduction.

Do not spend POD on repeated full-output runs until the chain-2,272,427 focused mismatch is explained.

Immediate next action:

1. Build the cached/windowed debug path.
2. Diagnose chain 2,272,427 against author source behavior.
3. Only then rerun full County x Zipcode.
