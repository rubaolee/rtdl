# Goal1010 Public RTX README Wording Consensus

Date: 2026-04-26

Consensus: **ACCEPT**

Participants:

- Codex: applied the Goal1009 wording to the README and added regression tests.
- Claude: external review verdict `ACCEPT`.
- Gemini: external review verdict `ACCEPT`.

Decision:

- The README now carries the seven reviewed RTX A5000 prepared query/native sub-path timing statements.
- The wording preserves sub-path scope and does not introduce whole-app, default-mode, Python-postprocess, or broad RT-core acceleration claims.
- `robot_collision_screening / prepared_pose_flags` remains excluded from public RTX speedup wording.
- The public doc links to the Goal1008 large-repeat artifact intake and Goal1009 wording packet.

Verification:

- `PYTHONPATH=src:. python3 -m unittest tests.goal1009_public_rtx_wording_review_packet_test tests.goal1010_public_rtx_readme_wording_test -v`
