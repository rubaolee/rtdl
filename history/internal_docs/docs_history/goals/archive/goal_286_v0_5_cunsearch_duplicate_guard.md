# Goal 286: v0.5 cuNSearch Duplicate Guard

Purpose:
- make the current duplicate-point correctness boundary actionable in the live RTDL/cuNSearch path
- stop strict-parity comparison runs from silently treating duplicate-point packages as valid cuNSearch inputs
- preserve an honest contract for future benchmark reports

Success criteria:
- a checked-in guard helper exists for exact cross-package duplicates
- the live cuNSearch comparison path consults that guard before execution
- duplicate-point packages are blocked with an explicit note instead of producing a misleading strict-parity result
- focused tests cover both allowed and blocked cases

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
