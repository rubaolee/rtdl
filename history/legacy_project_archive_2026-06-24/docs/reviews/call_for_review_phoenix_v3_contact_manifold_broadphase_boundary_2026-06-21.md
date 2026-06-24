# Call For Review: Phoenix V3 Contact Manifold Broadphase Boundary

Please critically review this Phoenix V3 packet as a release-boundary decision.

Files under review:

```text
docs/rebuild/v3/phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.md
docs/rebuild/v3/phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.json
tutorials/current/15_contact_manifold_broadphase_boundary.md
tests/v3_phoenix_contact_manifold_broadphase_boundary_test.py
```

Question:

Is it correct to keep `contact_manifold / generic_aabb_broadphase_collect_k`
as a rebuild boundary lesson, not an M7 release row, given the 1.235x query
signal, 2.759x collect-k signal, `matches_cpu_reference: true`, accepted v2.4
phase timing, 0.803x wall ratio, and standard paired V2.14 rows of 1.004x
Embree / 0.989x OptiX?

Please look for:

- any hidden full-solver or physics overclaim;
- whether the CPU-reference pass makes the lesson useful despite wall failure;
- any missing blocker before this can be M7;
- whether the test catches the dangerous future regression.
