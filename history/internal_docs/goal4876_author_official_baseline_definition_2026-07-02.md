# Goal4876: AuthorOfficial Baseline Definition And Prior Evidence Reclassification

Date: 2026-07-02

Status: `completed_pending_external_review`

## Purpose

Goal4876 defines the official comparison baseline for the RayJoin reproduction
line after the author confirmed that the corrected deterministic contract is
the official updated behavior.

The baseline is:

`AuthorOfficial = Author+RTDLContractPatch`

This is now the single fair comparator for new RayJoin reproduction evidence.

## Why This Baseline Exists

Earlier reproduction work exposed two correctness-contract gaps:

1. **Directed point-location SoS / reported-distance contract.**
   The author clarified that equal-height PIP boundary candidates need a
   slope-dependent deterministic tie behavior. Goal4834 implemented this in
   RTDL and in the patched author baseline.

2. **Duplicate half-edge canonicalization.**
   Some CDB planar maps contain exact reverse duplicate half-edges. Without an
   explicit rule, the chosen edge can depend on traversal/input order while
   representing the same geometry. Goal4868 made the RTDL contract explicit:
   group duplicate half-edges by unordered exact scaled endpoint pair and use
   the smallest stable source segment id as canonical. The author baseline was
   patched with the same rule.

Because the project owner is the paper author and confirmed this corrected
contract as the official updated behavior, comparisons should use
`AuthorOfficial` rather than the old unpatched AuthorPatch binary.

## AuthorOfficial Baseline Fingerprint

POD:

```text
ssh root@157.157.221.29 -p 23132 -i ~/.ssh/id_ed25519
```

AuthorOfficial source tree:

```text
/workspace/RayJoin_goal4834_patched_author
```

Underlying author-source HEAD:

```text
02bf6220d6d20b04af77ee20364eced75cc029c9
```

Modified files in the AuthorOfficial POD tree:

```text
src/algo/rt_pip_custom.cu
src/app/map_overlay_rt.h
src/app/output_chain.h
src/map/map.h
src/run_query.cu
src/util/markers.h
```

Diffstat captured on 2026-07-02:

```text
src/algo/rt_pip_custom.cu |  25 +++++++--
src/app/map_overlay_rt.h  |   7 +--
src/app/output_chain.h    |  16 +++++-
src/map/map.h             |  93 +++++++++++++++++++++++++++++++--
src/run_query.cu          |  23 ++++++++-
src/util/markers.h        | 128 +++++-----------------------------------------
6 files changed, 163 insertions(+), 129 deletions(-)
```

AuthorOfficial binary:

```text
/workspace/RayJoin_goal4834_patched_author/release/bin/polyover_exec
```

Binary SHA256:

```text
7ef4d5ee62180df695191d92a8ccdffcb27443a95820f04d5d6d2bd672888f47
```

Semantic patch artifacts in this repository:

- `history/internal_docs/goal4834_author_sos_t_reported.patch`
- `history/internal_docs/goal4868_author_rtdl_contract_patch.diff`

Compatibility/debug modifications in `output_chain.h`, `run_query.cu`, and
`markers.h` are part of the current POD baseline tree but are not the semantic
reason for changing the comparison contract. The semantic contract changes are
the SoS reported-distance patch and duplicate-half-edge canonicalization.

## RTDL Runtime Fingerprint Used In Latest Evidence

POD RTDL work tree:

```text
/workspace/rtdl_goal4859_exec
```

This POD directory is not a git checkout, so it must not be cited as a git
commit proof.

RTDL OptiX library:

```text
/workspace/rtdl_goal4859_exec/build/librtdl_optix.so
```

Library SHA256:

```text
f7ba19c10c5d4354f28f768192cd8b2c0ea21234492d14b41a4850549a59c664
```

## Official Wording

Allowed wording:

- "official updated RayJoin reproduction"
- "AuthorOfficial baseline"
- "AuthorOfficial = Author+RTDLContractPatch"
- "representative regenerated/current-source Section 5.x reproduction"
- "exact old paper-input reproduction" only when the exact old input CDBs and
  answers are actually present.

Forbidden wording:

- "old exact eight-pair Section 5.7 reproduction" for regenerated/current-source
  data;
- "matched old unpatched AuthorPatch" when the comparator was
  AuthorOfficial;
- broad performance claims before correctness and phase timing are reported;
- claiming Numba is used in a route where it is not on the critical path.

## Prior Evidence Reclassification

| Area | Prior evidence | New classification | Required follow-up |
|---|---|---|---|
| Section 5.2 LSI | Goal4845/Goal4853 LSI work and Section 5.2 counts | `pending_authorofficial_light_revalidation` | Goal4877 should confirm LSI counts are unchanged under AuthorOfficial. Expected to be stable because AuthorOfficial changes PIP/face-selection, not LSI. |
| Section 5.3 PIP | Goal4855/Goal4856 PIP evidence | `superseded_for_fair_comparison_until_authorofficial_rerun` | Goal4878 must rerun PIP/point-location under AuthorOfficial because this section is directly affected by SoS and duplicate-half-edge rules. |
| Section 5.7 public County x Soil sample | Goal4834 public sample | `valid_correctness_repair_sample_under_sos_contract__not_full_section57` | No broad Section 5.7 claim; useful as public-sample correctness evidence. |
| Section 5.7 County x Zipcode | Goal4872 / Goal4873 | `valid_bounded_full_stream_pair` | Keep as bounded pair evidence; ensure wording distinguishes old exact available pair from representative regenerated suite. |
| Section 5.7 Block x Water | Goal4871 / Goal4873 | `valid_bounded_full_stream_pair_under_authorofficial` | Keep as bounded pair evidence under AuthorOfficial. |
| Section 5.7 Australia Lakes x Parks representative | Goal4875 | `first_accepted_representative_public_primitive_authorofficial_result` | Use as template for representative suite expansion. |
| Remaining six Section 5.7 old pairs | Goal4873 listed as unreproduced | `not_blocking_for_representative_suite__exact_old_inputs_missing` | Goal4879 should regenerate representative/current-source inputs using author processing rules and label them correctly. |

## Current AuthorOfficial Success Anchor

Goal4875 is the first accepted representative Section 5.7 result under this
baseline.

External review:

```text
history/internal_docs/antigravity_goal4875_section57_au_representative_public_primitives_closure_review_2026-07-02.md
```

Verdict:

```text
approve_goal4875_bounded_representative_section57_public_primitives_closed
```

Byte-equal result:

```text
a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e  author_contract_au_overlay.txt
a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e  rtdl_public_overlay.txt
276320 lines, 6189260 bytes
```

This was a public RTDL route:

- public `prepare_planar_map_lsi_2d_optix`;
- public `prepare_planar_map_point_location_2d_optix`;
- Python app-level overlay assembly;
- no `rtdsl.rayjoin_overlay` import;
- no Embree;
- Numba not on the correctness-critical path.

## Decision Audit

1. **Was there a stupid failure mode here?**
   Yes: continuing to compare against old unpatched AuthorPatch after we had
   already adopted a deterministic duplicate-half-edge contract would be
   stupid. It would make RTDL look wrong for following the now-official contract.

2. **What action would make that decision stupid?**
   Treating AuthorPatch, AuthorOfficial, bundled helper outputs, and public
   primitive outputs as interchangeable. They are not interchangeable unless
   the contract and input provenance are named.

3. **Is there another path that avoids being stuck?**
   Yes: freeze AuthorOfficial as the comparator, reclassify old evidence, then
   rerun only the sections that are actually affected.

4. **Can we start a better path now?**
   Yes. Goal4877 can light-check 5.2 LSI; Goal4878 must rerun 5.3 PIP;
   Goal4879+ can expand 5.7 representative pairs without pretending the old
   hidden inputs exist.

## Exit Label

`completed_authorofficial_baseline_defined__prior_evidence_reclassified__ready_for_goal4877`
