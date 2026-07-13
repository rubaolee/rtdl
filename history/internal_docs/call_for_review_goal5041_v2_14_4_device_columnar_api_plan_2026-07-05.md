# Call For Review - Goal5041 v2.14.4 Device-Columnar API Plan

Reviewer: Claude or external reviewer

Please review:

- `history/internal_docs/goal5041_v2_14_4_device_columnar_api_design_and_implementation_plan_2026-07-05.md`
- Goal5040 fairness baseline:
  - `history/internal_docs/goal5040_fair_author_rtdl_top4_performance_comparison_2026-07-05.md`
- relevant existing implementation assets:
  - `src/rtdsl/device_column_row_buffer.py`
  - `src/rtdsl/columnar_partner.py`
  - `src/rtdsl/hit_stream_handoff.py`
  - `src/rtdsl/current_prepared_session_residency_profiles.py`
  - `src/rtdsl/optix_runtime.py`

Requested verdict label:

```text
approve_v2_14_4_device_columnar_prepared_pipeline_api_plan
```

After the first external review, the design was amended to incorporate the four approval conditions:

```text
C1 - Goal5042/5050 must explicitly handle existing core/native RayJoin-named symbols.
C2 - device_order_by may ship public; device_group_by remains internal unless true device-resident reduce passes POD verification.
C3 - Goal5043 must preserve the existing four-state stream-ordering vocabulary and derive residency from metadata, never app self-declaration.
C4 - Goal5049's <=0.36s RayJoin gate must also assert device-residency/no-host-copy metadata.
```

Alternative verdict labels:

```text
revise_v2_14_4_api_plan_before_implementation
block_v2_14_4_api_plan_as_rayjoin_specific
```

## Review Questions

1. Is the v2.14.4 positioning correct: system API consolidation, not another RayJoin app optimization cycle?

2. Does the plan correctly preserve the principle that RTDL is the language system and RayJoin is only one app on top?

3. Are the proposed API concepts generic enough:

```text
DeviceColumnBuffer
PreparedGeometrySession
DeviceOrderBy
DeviceSegmentedReduce / device_group_by
PartnerContinuation
```

4. Does the plan correctly reuse and consolidate existing v2.x assets rather than pretending this starts from zero?

5. Is the forbidden list complete enough to prevent RayJoin-specific semantics from entering RTDL core?

6. Is the performance baseline correct after Goal5040:

```text
47ms = single query-batch median
0.329s = full top4 six-batch prepared binary route
1.76x slower = RTDL prepared binary vs AuthorOfficial core phases
```

7. Is the RayJoin regression gate strict and fair:

```text
top4 prepared binary six-batch sum <= 0.36s median-of-N
```

8. Is the non-RayJoin genericity proof requirement sufficient, or should v2.14.4 require two non-RayJoin apps?

9. Are the implementation goals 5042-5050 ordered correctly?

10. Should `device_order_by` and `device_group_by` be exposed in v2.14.4, or should one remain internal until more tests exist?

11. Does the plan correctly keep Layer 4 / in-traversal fusion out of v2.14.4?

12. Does the plan adequately prevent replay/query-many/fresh regime confusion?

13. Does the plan sufficiently guard ownership, lifetime, synchronization, and host-materialization metadata?

14. Were the C1-C4 external review conditions incorporated materially rather than only acknowledged?

15. Should implementation proceed, or must Goal5041 be revised first?
