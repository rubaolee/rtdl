Keep.

Reasons:

- This is no longer just a wrapper over `baseline_runner`. The generated
  programs now own all three accepted dataset builders directly in
  `src/rtdsl/generate_only.py` and in the tracked generated artifact, which
  materially improves the “real generated program” claim.
- The docs now match the actual request contract.
  `docs/goal_111_v0_2_generate_only_mvp.md` no longer overclaims emitted-field
  control, and the final report frames the MVP narrowly and honestly.
- The package clears the minimum product test better than before: structured
  request in, runnable RTDL file out, verification included, and the file is
  more self-contained than “edit this example plus know the helper stack.”
- The Linux capable-host success for the generated `cpu` artifact matters. It
  shows this is not just a local string-rendering exercise; the emitted file
  runs on a real host under the normal executable path.

Remaining caution:

- It is still a narrow product mode, not broad code generation. One workload,
  one file shape, one family-specific renderer. That is acceptable because the
  docs now say exactly that.
- If future expansion just adds more templates with shallow substitutions, this
  should be paused quickly. But on the current package, the MVP is strong
  enough to keep.
