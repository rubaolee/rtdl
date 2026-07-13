# Goal4919 RayJoin Paper-Reproduction Package Consolidation

Status: completed, pending external review.

## Purpose

Goal4919 consolidated the RayJoin Section 5.2, 5.3, and 5.7 reproduction line
into one reader-facing package. The goal was not to add a new claim. It was to
make the existing bounded claims easier to find and harder to misread.

## Actions

1. Added:
   - `docs/release_reports/v2_14/rayjoin_reproduction_packet.md`
2. Linked it from:
   - `docs/release_reports/v2_14/README.md`
   - `docs/public_documentation_map.md`
3. The packet links the current evidence records for:
   - Section 5.2 LSI;
   - Section 5.3 point-location/PIP;
   - Section 5.7 bounded overlay reproduction;
   - author comparator modifications;
   - correctness root-cause and repair history;
   - representative data provenance;
   - performance boundary and current stop/next-plan status.

## Claim Boundary

The packet allows this wording:

```text
RTDL v2.14 has a bounded RayJoin reproduction covering Section 5.2, Section
5.3, and the documented Section 5.7 pairs under the documented author-contract
comparator.
```

The packet does not allow:

- all-eight exact hidden-input Section 5.7 reproduction;
- broad RTDL speedup over RayJoin;
- raw unpatched-author byte equality for duplicate-half-edge ambiguous cases;
- treating representative current-source data as the old paper-hidden inputs;
- presenting Numba as correctness-critical for the reproduction.

## Why This Matters

Before this goal, readers could find the Section 5.7 public page but not a
single index tying the lower-level Section 5.2/5.3 evidence, comparator
disclosure, and performance boundary together. That made it too easy to overread
one page in isolation. The new packet makes the boundary explicit.

## Verification

Commands run from the repository root:

```powershell
rg -n "rayjoin_reproduction_packet|RayJoin Reproduction Packet" docs
rg -n "Goal[0-9]+|Claude|Gemini|Antigravity|Codex|V3|V4|Phoenix|call_for_review|verdict|review debt|redo_required|generated internal" README.md docs examples/current -g "*.md" -g "*.py"
```

Results:

- new packet is linked from the v2.14 release package and public documentation
  map;
- public leak scan: no matches.

## Exit Label

`completed_rayjoin_reproduction_packet_consolidated_no_new_claim`
