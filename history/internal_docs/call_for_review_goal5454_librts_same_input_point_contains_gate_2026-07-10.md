# Call For Review - Goal5454 LibRTS Same-Input Point-Contains Gate

Please strictly review the first live author/RTDL gate in the LibRTS paper app.

Primary files:

```text
Paper-reproduction-apps/librts-paper/run_same_input_point_contains_gate.py
Paper-reproduction-apps/librts-paper/librts_reproduction.py
Paper-reproduction-apps/librts-paper/author_patches/goal5454_gtx1070_sm61.patch
Paper-reproduction-apps/librts-paper/author_patches/goal5454_linux_build_notes.md
Paper-reproduction-apps/librts-paper/results/librts_goal5454_same_input_point_contains.json
tests/goal5454_librts_same_input_point_contains_gate_test.py
history/internal_docs/goal5454_librts_same_input_point_contains_gate_2026-07-10.md
```

## Questions

1. Does the runner fail closed unless the author checkout matches the pinned
   commit?
2. Do SHA-256 fields establish that the same box/point files were passed to
   author and RTDL routes?
3. Does the evidence truly show author count 5 and RTDL OptiX count 5?
4. Does RTDL also match the five exact fixture rows without claiming that the
   count-only author example exposed those rows?
5. Are the `sm_61`, gflags, Boost, GCC, and intrinsic-header changes strictly
   build compatibility rather than query-semantic patches?
6. Is the public RTDL AABB API generic and free of LibRTS identity?
7. Are local-Linux timing fields correctly limited to diagnostics with no
   author/RTDL ratio?
8. Is Embree completely absent from builds, execution, and evidence?
9. Are mutation, Ray Multicast, PIP, range-query, dataset, figure, and full-paper
   claims correctly left open?
10. Is Goal5455 range-contains the right next bounded gate?

Requested verdict:

```text
approve_goal5454_librts_same_input_point_contains_count_gate
```
