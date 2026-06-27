# Call For Review: Phoenix V3 Robot Collision Flag-Stream Boundary

Please critically review this Phoenix V3 packet as a release-boundary decision.

Files under review:

```text
docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_boundary_2026-06-21.md
docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_boundary_2026-06-21.json
tutorials/current/14_robot_collision_flag_stream.md
tests/v3_phoenix_robot_collision_flag_stream_boundary_test.py
```

Question:

Is it correct to keep `robot_collision / prepared_collision_flags` as a rebuild
boundary lesson, not an M7 release row, given the 5.166x hot flag-stream signal,
69.904x traversal signal, 0.997x wall ratio, sampled-probe-only contract, and
standard paired V2.14 rows of only 1.003x Embree / 1.028x OptiX?

Please look for:

- any hidden overclaim in the tutorial wording;
- any missing blocker before this can be M7;
- whether the wall/probe-reference explanation is clear enough for users;
- whether the test catches the dangerous future regression.
