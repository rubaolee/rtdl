**Verdict: Goal858 is complete and correct.**

Key reasons:

1. **Docs match the test contract.** The test checks for 8 specific phrases across the two feature READMEs and the tutorial. All phrases are present and accurate in the current files — the test would pass as written.

2. **Claim boundary is honest throughout.** All three docs consistently state that `--require-rt-core` fails intentionally today, that `--optix-mode native` is experimental (not a released RT-core claim), and that pair-row native output does not exist yet. No overclaiming.

3. **Internal consistency is tight.** The hitcount and anyhit_rows READMEs, the tutorial's OptiX mode boundary table, and the report all align on the same three-state model (`auto` / `host_indexed` / `native`) with the same rejection semantics. No contradictions.

4. **Scope is clean.** The goal is documentation-only truth work; the report correctly states it does not promote anything into the active RTX claim set. The test file is appropriately narrow — it only checks phrase presence, which is the right level for doc-accuracy assertions.

5. **No gaps.** The `anyhit_rows` README correctly captures the additional boundary unique to that feature (`--output-mode rows --optix-mode native` fails; native only works for the compact path). This is the most nuanced point and it is covered.
