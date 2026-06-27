Review the bounded Goal864 segment/polygon gate review-packet change only.

Scope:

- `/Users/rl2025/rtdl_python_only/scripts/goal864_segment_polygon_gate_review_packet.py`
- `/Users/rl2025/rtdl_python_only/tests/goal864_segment_polygon_gate_review_packet_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal864_segment_polygon_gate_review_packet_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal864_segment_polygon_gate_review_packet_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal807_segment_polygon_optix_mode_gate_local_2026-04-23.json`

Question:

Is this review packet honest and useful?

Specifically:

- does `needs_real_optix_artifact` correctly describe the current local state
  when CPU reference exists but both OptiX paths are unavailable?
- does the packet avoid overpromoting the segment/polygon family?
- is there any logic hole in the recommendation mapping?

Required output:

- write verdict file to
  `/Users/rl2025/rtdl_python_only/docs/reports/goal864_claude_external_review_2026-04-23.md`
- keep it concise
- state `ACCEPT` or `BLOCK`

