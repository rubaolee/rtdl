# Call For Review - Goal5453 LibRTS Provenance Scaffold

Please strictly review the fifth RTDL paper-app intake.

Primary files:

```text
Paper-reproduction-apps/librts-paper/README.md
Paper-reproduction-apps/librts-paper/data/manifest.json
Paper-reproduction-apps/librts-paper/librts_reproduction.py
tests/goal5453_librts_paper_reproduction_scaffold_test.py
history/internal_docs/goal5453_librts_paper_reproduction_provenance_scaffold_2026-07-10.md
```

## Questions

1. Are the paper DOI, GitHub commit, Zenodo v2 DOI/archive/MD5, and build
   requirements accurately pinned?
2. Does the author contract correctly identify point/range queries and mutable
   Insert/Update/Delete behavior?
3. Is the historical LibRTS-style benchmark kept separate from paper evidence?
4. Are the reused RTDL APIs generic AABB/index capabilities rather than
   LibRTS-specific shortcuts?
5. Does the tiny point-contains fixture produce the correct five relation rows?
6. Does the local result clearly avoid claiming author agreement?
7. Is Goal5454 correctly limited to the tiny same-input author gate before
   performance, mutations, or large artifact acquisition?
8. Are all full-paper, performance, Ray Multicast, PIP, and mutability claims
   correctly forbidden at this stage?
9. Is the owner backend decision explicit: CPU as the local semantic reference,
   OptiX on Linux/POD, and no Embree work or evidence anywhere in this campaign?
10. Is the local Linux fallback correctly limited to functional evidence and
    prevented from becoming a paper-performance denominator?

Requested verdict:

```text
approve_goal5453_librts_provenance_scaffold_and_local_reference
```
