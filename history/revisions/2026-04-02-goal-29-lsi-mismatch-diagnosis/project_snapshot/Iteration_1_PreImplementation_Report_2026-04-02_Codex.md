# Goal 29 Pre-Implementation Report (Codex)

Known starting point:
- Goal 28D established that larger exact-source co-located slices can diverge for `lsi`
- `1 x 4` was parity-clean
- `1 x 5`, `1 x 6`, and `1 x 8` were not parity-clean
- `pip` remained parity-clean on those same slices

This strongly suggests a workload-specific issue in segment-level handling rather than a general polygon conversion failure.

The first likely families to test are:
- endpoint-touch handling
- duplicate/near-duplicate chain edges
- ring-closure edge behavior
- collinear overlap rejection or acceptance asymmetry

Success for this round is either:
- demonstrated fix and regression coverage, or
- a concrete diagnosis that narrows the unresolved bug to a specific function or rule.
