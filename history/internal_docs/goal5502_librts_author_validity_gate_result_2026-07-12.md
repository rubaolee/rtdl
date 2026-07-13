# Goal5502 LibRTS Author-Validity Gate Result

## Decision

Goal5502 applies a three-way author-validity decision to the Goal5501
same-source prefix evidence. The selected independent contract is inclusive
float32 AABB intersection. The gate does not infer that the author is wrong
from a count difference alone; it records whether each implementation agrees
with the selected generic contract and chooses the next action accordingly.

## Evidence

| prefix | author | RTDL | CPU float32 oracle | classification | decision |
|---|---:|---:|---:|---|---|
| `parks_Europe` 100K prefix | 13,695,048 | 13,695,053 | 13,695,053 | RTDL matches contract; author diverges | preserve generic RTDL; do not copy author divergence |
| `lakes.bz2` 100K prefix | 12,596,850 | 12,596,850 | 12,596,850 | both match contract | no semantic fix required for this case |
| `parks_Europe` 250K prefix | 34,240,217 | 34,240,244 | 34,240,244 | RTDL matches contract; author diverges | preserve generic RTDL; do not copy author divergence |
| `lakes.bz2` 250K prefix | 34,581,812 | 34,586,817 | 34,586,817 | RTDL matches contract; author diverges | preserve generic RTDL; do not copy author divergence |
| `parks.bz2` 100K capacity prefix | 11,815,394 | 11,815,398 | 11,815,398 | RTDL matches contract; author diverges | preserve generic RTDL; do not copy author divergence |

The `parks.bz2` full-input author run remains a CUDA allocation failure. Its
100K prefix is evidence about the selected contract, not a capacity solution.
The gate is prefix-only and does not adjudicate the full-input mismatch. The
250K prefixes make the result less likely to be a 100K sampling accident, but
they still do not establish the full-input author contract.

## System Decision

No RTDL core semantic change is authorized by this evidence. In particular:

- do not add LibRTS-specific boundary, padding, or numeric behavior to RTDL;
- do not treat the author count as authoritative when it diverges from the
  selected independent generic contract;
- do not claim that the author is definitively wrong on the full input;
- if a future full-input oracle shows RTDL diverges while the author matches,
  fix the generic RTDL implementation before claiming reproduction;
- if a future full-input oracle shows RTDL matches and the author diverges,
  preserve RTDL and close the author mismatch as an author-contract or
  implementation divergence.

## Ownership And Claim Boundary

The gate is app-owned evidence code. It reads Goal5501 artifacts and does not
modify `src/rtdsl/` or `src/native/`. The result does not claim full-input
author validity, complete range-intersects coverage, pair-row parity,
performance parity, full paper reproduction, device zero-copy, or Embree.

Result artifact:

```text
Paper-reproduction-apps/librts-paper/results/goal5502/author_validity_gate.json
Paper-reproduction-apps/librts-paper/results/goal5502/mismatch_diagnostic_250k.json
```

The current bounded LibRTS project remains closed. A full-input oracle,
author pair-row comparator, or capacity recovery is a new explicitly
authorized scope.
