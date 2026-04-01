# Goal 21: RayJoin Matrix and Dataset Reproduction Setup

## Goal

Freeze the RayJoin-on-Embree reproduction matrix and define the dataset/provenance/local-profile setup that the later implementation and run goals will use.

## What Goal 21 Must Deliver

1. A frozen mapping from RayJoin paper artifacts to RTDL workloads:
   - Table 3
   - Table 4
   - Figure 13
   - Figure 14
   - Figure 15

2. A frozen mapping from each artifact to:
   - RTDL workload(s)
   - dataset(s)
   - provenance category
   - expected output artifact(s)

3. A dataset acquisition and substitution ledger:
   - exact public dataset available
   - derived subset required
   - synthetic substitute required

4. Reduced-size local profiles that keep the default package in the `5–10 minute` range on this Mac.

5. An explicit list of any blocking semantic/runtime gaps that Goal 22 must address.

## Required Fidelity Labels

Every paper-target case must be labeled as one of:

- `exact-input`
- `derived-input`
- `synthetic-input`

## Acceptance Bar

Goal 21 is complete when:

- every paper-target artifact is mapped
- every mapped case has a dataset status and provenance label
- every local runnable case has a reduced-size profile
- every unresolved blocker is named explicitly for Goal 22
- Gemini approves the setup and Claude agrees the plan is technically honest
