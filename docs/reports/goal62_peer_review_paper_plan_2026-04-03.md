# Goal 62 Plan: Peer-Review-Ready RTDL Paper

Date: 2026-04-03

## Manuscript target

Use an IEEE-style anonymous conference format as the concrete double-column
submission surface for this round.

Reason:

- no venue has been frozen yet
- IEEEtran provides a clean, professional double-column baseline
- the paper can later be adapted to ACM if needed

## Evidence base

The paper should draw only from accepted current-state artifacts, especially:

- Goal 50 PostGIS ground-truth closure
- Goal 54 bounded `LKAU ⊲⊳ PKAU` four-system closure
- Goal 56 bounded overlay-seed four-system closure
- Goal 59 bounded v0.1 reproduction package
- Goal 61 bounded RayJoin paper closure
- Goal 60 full consistency audit
- accepted Figure 13 / Figure 14 analogue reports

## Main sections

1. Introduction and motivation
2. RTDL design and implementation
3. Relation to RayJoin
4. Evaluation methodology
5. Bounded RayJoin experiment results
6. Limitations and validity boundaries
7. Conclusion

## Deliverables

- manuscript source package under `paper/rtdl_rayjoin_2026/`
- bibliography file
- paper README with build/audit notes
- manuscript audit report
- Gemini review
- Claude review
- Codex consensus

## Known blocker

The local shell does not currently have a LaTeX toolchain on PATH.

So this round should still produce:

- real IEEE-style LaTeX source
- vendored template/class support
- audited manuscript text

Compilation may require a later environment step unless a LaTeX engine is added
to this machine.
