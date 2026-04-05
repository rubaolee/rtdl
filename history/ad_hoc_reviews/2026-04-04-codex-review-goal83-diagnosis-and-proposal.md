# Codex Review: Goal 83 Diagnosis and Proposal

Verdict: `APPROVE`

## Findings

No blocking findings in the diagnosis/proposal document.

The document is technically coherent and matches the observed failure shape:

- exact-source long Embree positive-hit `pip` is parity-wrong
- the mismatch is stable across reruns
- the current native positive-hit path in `src/native/rtdl_embree.cpp`
  mixes candidate discovery with final truth

The proposed repair direction is also correct:

- candidate generation in the Embree callback
- host exact finalize after candidate collection
- GEOS-backed finalize when available

## Notes

- This is a diagnosis/proposal approval, not an implementation acceptance.
- The patch still needs decisive exact-source Linux reruns before Goal 83 can be
  turned into a publishable result package.
