# Goal 30 Pre-Implementation Report (Codex)

Starting point from Goal 29:
- the exact-source `lsi` mismatch is frozen and reproducible
- float32 truncation in the active native geometry ABI is a confirmed contributing factor
- broad-phase candidate completeness remains separately unresolved

Therefore this round should be narrow:
1. widen the active native geometry ABI to double precision
2. keep the current backend logic otherwise unchanged
3. measure whether the precision-only change reduces or removes the known mismatch

This is intentionally a partial-fix round, not a full exact-source `lsi` closure round.
