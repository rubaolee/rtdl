# Goal 280: v0.5 cuNSearch Live Precision Hardening

Purpose:
- fix the live cuNSearch JSON bridge so bounded real-data parity does not fail due to truncated distance formatting
- turn the first real KITTI comparison from a narrow radius-only success into a more stable live comparison path

Success criteria:
- generated live driver source writes full-enough numeric precision for both float and double builds
- unit tests cover the emitted precision settings
- the real KITTI bounded live comparison remains parity-clean at larger radii that previously failed due to output truncation

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
