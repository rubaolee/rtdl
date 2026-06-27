# Goal1627 v1.6.x OptiX Collect-K Deferred Merge Sync Diagnostic 3-AI Consensus

## Verdict

`accepted_as_internal_diagnostic_candidate`

Codex, Claude, and Gemini agree that the opt-in
`RTDL_OPTIX_COLLECT_K_DEFER_MERGE_SYNC_DIAGNOSTIC` gate is a reasonable internal
performance diagnostic candidate for the experimental OptiX
`COLLECT_K_BOUNDED` device-pointer path.

## Consensus Points

- The default path is unchanged because the diagnostic requires an explicit
  environment variable.
- The synchronization-safety argument is acceptable for the guarded path:
  intermediate merge work stays on the same CUDA stream, and the guard requires
  device prefix compact plus device level counts so intermediate host metadata
  reads are not needed.
- The final merge level remains synchronized because the guard excludes
  `current_rows.size() == 2`.
- A4500 repeats=5 evidence preserved parity and reduced median native stage
  total for counts `65537`, `98305`, and `131072`.
- The evidence remains narrow and internal. It does not justify public speedup
  wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU claims, true
  zero-copy wording, release tags, or release action.

## Review Follow-Up

- Claude requested a source comment explaining why device prefix compact and
  device level counts are load-bearing for deferral safety. The comment was
  added.
- Claude requested a report caveat that non-final per-level `sync_ms` is not a
  reliable latency signal when the diagnostic is enabled. The caveat was added.
- Gemini approved the diagnostic and recommended proceeding with internal
  regression slices before any candidate-bundle promotion.

## Next Work

Keep the diagnostic opt-in and run a focused RTX regression slice with the flag
enabled. Only after that should the project consider whether this belongs in a
future gated candidate bundle.
