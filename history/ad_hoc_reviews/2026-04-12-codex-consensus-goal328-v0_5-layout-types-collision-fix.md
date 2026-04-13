# Codex Consensus: Goal 328

Date:
- `2026-04-12`

Conclusion:
- the `rtdsl.types` module name was a real packaging risk and worth fixing
- the rename to `layout_types.py` is small, coherent, and preserves the public
  `rtdsl` import surface
- the new regression test is the right long-term guard for this issue

Decision:
- Goal 328 is closed
