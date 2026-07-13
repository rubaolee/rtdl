# Call For Review: v2.14.5 Entry Plan

Date: 2026-07-07

## Requested Verdict Label

```text
approve_v2_14_5_entry_plan_two_paper_app_generalization
```

## Review Scope

Please review:

- `history/internal_docs/v2_14_5_entry_plan_two_paper_app_generalization_2026-07-07.md`
- `history/internal_docs/rt_barneshut_bounded_same_input_final_status_and_cleanup_2026-07-07.md`
- `Paper-reproduction-apps/README.md`
- `Paper-reproduction-apps/rt-barneshut-paper/README.md`

## Context

v2.14.4 produced two paper-reproduction app lines:

- RayJoin, which drove planar-map and device-columnar APIs;
- RT-BarnesHut, which drove generic aggregate-hierarchy / frontier-reduce APIs.

The RT-BarnesHut bounded same-input line is closed with no remaining required review debt, but full paper reproduction and broad performance claims remain explicitly not closed.

v2.14.5 should generalize from the two apps rather than continue app-specific debugging.

## Review Questions

1. Is the v2.14.5 objective correctly framed around generalizing from two paper apps?
2. Does the plan preserve the principle that RTDL is the generic system and paper apps are users?
3. Are the proposed goals ordered correctly, starting with the paper-app status model and API surface audit?
4. Does the plan avoid reopening RayJoin or RT-BarnesHut performance work without explicit authorization?
5. Does the plan correctly separate public RTDL APIs from app-owned comparator/author/output logic?
6. Is Goal5088's third-validation selection gate the right way to avoid choosing another app blindly?
7. Are the success criteria concrete enough for v2.14.5 entry?
8. Are any additional blockers or amendments needed before starting Goal5085?

## Expected Answer Shape

Please provide:

- Verdict
- Blocking findings, if any
- Required amendments, if any
- Non-blocking notes
- Answers to the 8 review questions
