# Goal5035 Architecture / Design Reflection And Public Boundary Fix

Date: 2026-07-05

## Trigger

Owner asked whether the current v2.14.3 RayJoin performance line has major or minor mistakes in principle, architecture, design, or implementation, and asked to fix them rather than only explain them.

## Short Answer

There is no evidence that RTDL core was turned into a hidden RayJoin kernel in the current line. The larger problem was measurement and framing discipline: the work repeatedly improved one regime and then risked describing the result with wording from another regime.

The concrete public-facing defect found in this pass was stale wording in the RayJoin paper app README and v2.14 release packet:

- `Fresh/cold writer-free route` mixed warm-process fresh with cold CLI startup.
- `Prepared/query-many writer-free route` still reported the old `0.33-0.35s` / `~0.44s` prepared-body evidence.
- The current Goal5034 result, `0.755s` for the prepared LSI base-session six-batch writer-free binary route, was not reflected there.

That is now fixed.

## Principle-Level Issues

### P1 - Regime drift was the largest recurring mistake

The main wrong pattern was not a bad kernel; it was changing the denominator:

- cold CLI startup;
- warm-process fresh route;
- prepared operator replay;
- prepared LSI base-session with distinct batches;
- paper text writer route;
- writer-free binary route.

These are different products. Mixing them makes a real optimization look larger or smaller than it is.

Fix applied now:

- Public docs now say `Warm-process fresh writer-free route`, not `Fresh/cold`.
- Current prepared route wording says `Prepared LSI base-session, six distinct query batches`.
- The `0.755s` number is tied only to that prepared LSI base-session + six-batch + writer-free binary route.
- A regression test now blocks the stale public wording from returning.

### P2 - "One number" is useful, but only after the regime is fixed

Owner asked for one number; the right one for the current optimized operator-body route is `0.755s`. But that number must never be silently read as:

- cold CLI one-shot;
- paper text-output route;
- author parity;
- all Section 5.7 pairs.

Fix applied now:

- Public docs keep the route boundary beside the number.

## Architecture-Level Issues

### A1 - The direction is correct: generic RTDL substrate, RayJoin app on top

The current optimized path uses generic substrate pieces:

- public planar-map LSI;
- public directed point-location/PIP;
- device columns / row-buffer style handoff;
- native CUDA/Thrust lexsort;
- Numba/CUDA app continuations.

RayJoin-specific work remains in the app:

- CDB parsing and paper input workflow;
- midpoint and descriptor semantics;
- carrier construction;
- paper-compatible correctness contracts.

No RTDL core/native file was changed in Goal5033 or Goal5034.

### A2 - The current route is still not a fully general overlay engine

The binary route is a strong pipeline-operator measurement, not a general promise that every overlay workload is now fast. The app still encodes RayJoin-specific descriptor assembly. That is acceptable as an app, but it must not be promoted into RTDL core without a non-RayJoin proof.

Fix applied now:

- The public release packet now says the remaining floor is LSI pair-id production plus downstream binary continuation, not a broad solved-overlay claim.

## Design-Level Issues

### D1 - Prepared/session strategy should be explicit, not accidental

The current best number relies on a prepared LSI base session and six distinct chain-contiguous query batches. That is a legitimate pipeline/server-style workload, but it is not the same as a one-shot CLI program.

Fix applied now:

- Public docs describe it as a prepared LSI base-session route.
- Old `prepared/query-many` wording was removed from public docs because it was too loose.

### D2 - Device-resident work must prove payoff in its target regime

Earlier device-resident work looked good in replay but lost in fresh. Goal5033 and Goal5034 finally made the device route win in the prepared LSI base-session six-batch regime. This is the right way to justify it: same input, same regime, N-run artifacts.

Fix already applied by Goal5034:

- Device carrier six-batch sum improved from Goal5033 `0.911350s` to `0.755416s`.
- The app keeps this scoped to writer-free binary descriptor route only.

## Implementation-Level Issues

### I1 - Stale public documentation was wrong

The implementation had moved on, but two public-facing docs still contained old performance framing.

Fixed files:

- `Paper-reproduction-apps/rayjoin-paper/README.md`
- `docs/release_reports/v2_14/rayjoin_reproduction_packet.md`

Added guard:

- `tests/goal5035_public_perf_boundary_guard_test.py`

### I2 - Remaining measured bottleneck is LSI pair-id production

After Goal5034, the largest measured body component in the selected route is LSI pair-id production, about `0.277508s` per six-batch run. The evidence points to `scaled_cache_ensure` inside native LSI preparation, not OptiX traversal itself.

Next technical attack, when a POD is reachable:

1. keep each batch's prepared LSI query handle alive;
2. run the same six batch queries twice;
3. check whether second-pass `scaled_cache_ensure` drops.

If it drops, the fix is a productized query-batch LSI cache/preparation route. If it does not, the scaled-cache key/design is fighting cross-batch reuse and must be redesigned as a generic prepared workspace issue.

## What Was Fixed In This Goal

- Replaced stale public `Fresh/cold` wording with `Warm-process fresh`.
- Replaced stale `0.33-0.35s` prepared/query-many wording with the current `0.755s` prepared LSI base-session six-batch evidence.
- Clarified that `4.22s` excludes cold Python/CUDA process startup.
- Clarified that `0.755s` is not paper text output, not cold CLI, and not author parity.
- Added a test to prevent stale regime wording from returning.

## Exit Label

```text
completed_goal5035_regime_boundary_reflection_and_public_doc_fix
```
