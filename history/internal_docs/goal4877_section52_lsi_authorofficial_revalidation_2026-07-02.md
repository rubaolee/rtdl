# Goal4877: Section 5.2 LSI Revalidation Under AuthorOfficial

Date: 2026-07-02

Status: `completed_pending_external_review`

## Purpose

Goal4877 revalidates RayJoin paper Section 5.2 LSI after the project adopted
the official updated baseline:

```text
AuthorOfficial = Author+RTDLContractPatch
```

The question is narrow:

```text
Do the available Section 5.2 LSI count results change under AuthorOfficial?
```

Expected answer: no. AuthorOfficial changes directed point-location SoS and
duplicate-half-edge face selection. Those are PIP / overlay continuation
contracts, not LSI predicate contracts.

## POD Fingerprint Rechecked

POD:

```text
ssh root@157.157.221.29 -p 23132 -i ~/.ssh/id_ed25519
```

AuthorOfficial binary exists and was re-fingerprinted:

```text
/workspace/RayJoin_goal4834_patched_author/release/bin/polyover_exec
7ef4d5ee62180df695191d92a8ccdffcb27443a95820f04d5d6d2bd672888f47
```

RTDL OptiX library exists and was re-fingerprinted:

```text
/workspace/rtdl_goal4859_exec/build/librtdl_optix.so
f7ba19c10c5d4354f28f768192cd8b2c0ea21234492d14b41a4850549a59c664
```

AuthorOfficial modified-file list observed on POD:

```text
src/algo/rt_pip_custom.cu
src/app/map_overlay_rt.h
src/app/output_chain.h
src/map/map.h
src/run_query.cu
src/util/markers.h
```

The LSI kernel/predicate source is not in that list. The semantic patch files in
the repository likewise show point-location SoS and duplicate-half-edge face
selection changes, not LSI predicate changes:

- `history/internal_docs/goal4834_author_sos_t_reported.patch`
- `history/internal_docs/goal4868_author_rtdl_contract_patch.diff`

## Method

This is a light AuthorOfficial revalidation, not a new expensive all-pair run.

I did not rerun the two large CDB loads from scratch because the thing being
tested is whether AuthorOfficial changes LSI semantics. The patch-scope check
says it does not. Goal4853 already contains raw public-primitive LSI summaries
for the three available pairs.

Primary summary artifact:

```text
history/internal_docs/goal4877_section52_lsi_authorofficial_revalidation_summary.json
```

Prior raw public RTDL count summaries reused:

- `history/internal_docs/goal4853_section52_final/county_zipcode_final.json`
- `history/internal_docs/goal4853_section52_final/block_water_final.json`
- `history/internal_docs/goal4853_section52_final/australia_lakes_parks_representative_final.json`

The public RTDL route remains:

```python
prepare_planar_map_lsi_2d_optix(base).count(query)
```

No `rtdsl.rayjoin_overlay` evidence is used for the RTDL public route.

## Results

| Pair | Orientation | AuthorOfficial LSI count | RTDL public LSI count | Match | Provenance |
|---|---|---:|---:|---|---|
| County x Zipcode | County base, Zipcode query | 961165 | 961165 | yes | Goal4845 count, AuthorOfficial-stable by patch-scope check |
| Block x Water | Block base, Water query | 649605 | 649605 | yes | Goal4846 count, AuthorOfficial-stable by patch-scope check |
| Australia Lakes x Parks representative | Lakes base, Parks query | 13622 | 13622 | yes | Goal4848/4853 representative forward count, AuthorOfficial-stable by patch-scope check |

Important direction note:

Goal4875's Section 5.7 Australia overlay route uses the opposite-oriented LSI
row count `13452`. That is not a contradiction. Section 5.2 here records the
forward `Lakes base, Parks query` representative count `13622`.

## What This Proves

For the available tested Section 5.2 inputs and the representative Australia
pair, the public RTDL planar-map LSI primitive remains valid under
AuthorOfficial:

- County x Zipcode: match.
- Block x Water: match.
- Australia Lakes x Parks representative forward direction: match.

This completes the Goal4876 follow-up classification:

```text
Section 5.2 LSI: pending_authorofficial_light_revalidation
```

becomes:

```text
Section 5.2 LSI: authorofficial_revalidated_for_available_pairs
```

## What This Does Not Prove

This does not prove:

- full exact old hidden-input all-eight Section 5.2 completion;
- Section 5.3 PIP correctness under AuthorOfficial;
- Section 5.7 overlay correctness;
- any performance claim;
- any Embree claim;
- any Numba-critical-path claim.

The remaining Section 5.2 limitation is still data/provenance for the other old
paper pairs, not a known LSI primitive failure on the available tested pairs.

## Decision Audit

1. **Was there a stupid failure mode here?**
   Yes: rerunning two very large CDB loads merely to reconfirm an unchanged LSI
   predicate would look productive while testing little.

2. **What action would make that decision stupid?**
   Treating "AuthorOfficial changed PIP and overlay face selection" as if it
   automatically invalidated LSI counts, then burning POD time on blind reruns.

3. **Is there another path that avoids being stuck?**
   Yes: inspect the AuthorOfficial patch scope, verify it does not touch LSI,
   then reclassify the existing raw public LSI evidence under the updated
   baseline.

4. **Can we start a better path now?**
   Yes. Close 5.2 for the available pairs under AuthorOfficial and move to
   Goal4878, where AuthorOfficial actually matters: Section 5.3 PIP.

## Exit Label

`completed_section52_lsi_authorofficial_available_pairs_revalidated__no_fresh_large_rerun_needed`
