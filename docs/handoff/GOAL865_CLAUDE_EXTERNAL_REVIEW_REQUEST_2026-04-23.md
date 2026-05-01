Review the bounded Goal865 road-hazard review-packet change only.

Scope:

- `/Users/rl2025/rtdl_python_only/scripts/goal865_road_hazard_review_packet.py`
- `/Users/rl2025/rtdl_python_only/tests/goal865_road_hazard_review_packet_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal865_road_hazard_review_packet_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal865_road_hazard_review_packet_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal864_segment_polygon_gate_review_packet_2026-04-23.json`

Question:

Is it correct and honest to make `road_hazard_screening` explicitly depend on
the Goal864 segment/polygon packet state, such that:

- `needs_real_optix_artifact` upstream becomes
  `needs_segment_polygon_real_optix_artifact`
- upstream gate failure becomes
  `blocked_by_segment_polygon_gate_failure`
- only `ready_for_review` upstream can make road hazard `ready_for_review`

Required output:

- write verdict file to
  `/Users/rl2025/rtdl_python_only/docs/reports/goal865_claude_external_review_2026-04-23.md`
- keep it concise
- state `ACCEPT` or `BLOCK`

