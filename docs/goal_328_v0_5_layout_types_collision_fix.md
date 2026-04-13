# Goal 328: v0.5 Layout Types Collision Fix

Purpose:
- remove the `src/rtdsl/types.py` naming-collision risk called out by the full
  Gemini repo audit
- preserve the public `rtdsl` layout/type import surface while avoiding a local
  module name that shadows stdlib `types`

Success criteria:
- rename the internal module away from `types.py`
- update internal imports to the new module name
- keep `rtdsl` package-level exports working
- add a regression test that proves stdlib `types` still wins even if
  `src/rtdsl` is placed on `sys.path`

Required review:
- Gemini review saved in the repo
- Codex consensus note saved in the repo
