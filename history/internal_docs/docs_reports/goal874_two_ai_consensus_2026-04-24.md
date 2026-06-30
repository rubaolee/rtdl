# Goal874 Two-AI Consensus

- date: `2026-04-24`
- goal: `Goal874 RTX manifest native pair-row gate refresh`
- Codex verdict: `ACCEPT`
- Claude verdict: `ACCEPT`
- consensus: `ACCEPT`

## Decision

Goal874 is accepted.

The Goal759 RTX cloud benchmark manifest now includes
`segment_polygon_anyhit_rows_native_bounded_gate` as a deferred strict RTX gate
for Goal873. This keeps the cloud runner ready for the next RTX session while
preserving all honesty boundaries:

- The entry is deferred, not active.
- The public app path is still documented as host-indexed.
- The strict gate must pass on real RTX hardware.
- CPU row-digest parity and zero overflow are required.
- Independent artifact review remains required before promotion.

No public RT-core speedup claim or public app promotion is authorized by this
goal.
