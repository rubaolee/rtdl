# Goal 23 Spec

## Title

Goal 23: Bounded Embree Reproduction Runs

## Intent

Run the honest executable RayJoin-on-Embree reproduction package that the repo can support today under the frozen Goal 21/22 constraints.

## Frozen Inputs

- Goal 21 frozen matrix and local profile policy
- Goal 22 generator/reporting machinery
- Goal 22 dataset-source and bounded-preparation machinery

## Proposed Execution Slice

### Executed now

- Figure 13 bounded local `lsi` analogue
- Figure 14 bounded local `pip` analogue
- Table 4 bounded local overlay-seed analogue
- Figure 15 bounded local overlay-seed speedup analogue
- Table 3 partial bounded local rows for currently runnable local families

### Reported but not executed now

- any dataset family still only `source-identified`
- any exact-input path not yet acquired locally

## Deliverables

- runner/report code for the bounded reproduction slice
- generated markdown/JSON/SVG/PDF artifacts
- final Embree reproduction report
- tests for the new generation path

## Standard

No artifact may imply full RayJoin-paper coverage if a family is still only `source-identified`.
