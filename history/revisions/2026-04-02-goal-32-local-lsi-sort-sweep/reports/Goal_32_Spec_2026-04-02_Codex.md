# Goal 32 Spec

Goal 32 optimizes the local `lsi` path after Goal 31 restored exact-source correctness.

Scope:
- keep the current local `native_loop` correctness contract
- improve the current local `lsi` candidate path without restoring BVH-backed traversal
- compare a Codex optimization proposal against an independent Claude proposal if available
- allow temporary Codex+Gemini closure if Claude quota is unavailable and the user explicitly approves that fallback

Closure conditions:
- Goal 31 parity must remain intact
- new regression coverage must be added
- a measurable native speedup over the Goal 31 brute-force local baseline must be demonstrated
- the final report must keep the `native_loop` boundary explicit
