# Call For Review: Goal5208 Inline Threshold Lowering No-Go

Please strictly review Goal5208.

## Files Under Review

```text
history/internal_docs/goal5208_inline_threshold_lowering_no_go_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5207_explicit_warmup_all_then_measured_all_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5208_inline384_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5208_inline256_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5208_inline128_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
```

## Review Questions

1. Do the four artifacts compare the same full-public Dragon -> HappyBuddha
   Level-B workload under the same explicit Goal5207 warmup protocol?
2. Do all lower-threshold variants preserve correctness against the author
   HDResult?
3. Is the report correct that `384` gives only a tiny measured-route movement
   while increasing full-run wall when warmup is included?
4. Is the report correct that `256` and `128` are clear no-go variants because
   row materialization and continuation dominate any native OptiX launch saving?
5. Is keeping `max_inline_points=512` as the current default supported by the
   evidence?
6. Does the report avoid warm-only overclaiming and preserve the Goal5207
   regime boundary?
7. Does the report avoid author-vs-RTDL performance ratios, exact-paper input
   claims, author parity claims, and full-paper reproduction claims?
8. Should Goal5208 close with
   `completed_inline_threshold_lowering_no_go__keep_inline512_default`?

## Expected Answer Shape

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to review questions:
```
