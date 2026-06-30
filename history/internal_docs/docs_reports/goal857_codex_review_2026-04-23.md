# Goal857 Codex Review

Verdict: ACCEPT

Reasoning:

- The change is narrow and honest. It does not alter segment/polygon backend
  semantics or claim promotion status.
- Adding `optix_mode` to the local perf scripts closes a real audit gap:
  future measurements can now distinguish default OptiX behavior from forced
  host-indexed fallback and the experimental native path.
- The new tests verify the important behavior:
  - mode propagation into the segment/polygon compact-summary perf runner
  - mode propagation into the road-hazard compact-output perf runner
  - emitted payloads carrying `optix_mode`
- Existing RT-core boundary tests for the segment/polygon family still pass, so
  the tooling improvement did not weaken the public honesty guard.

Boundaries:

- This is not a promotion of segment/polygon into the active RTX claim set.
- This is not evidence of RT-core speedup.
- Pair-row native OptiX output still does not exist.
