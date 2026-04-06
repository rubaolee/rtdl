Verdict: keep, but narrowly. `handoff_bundle` is materially better than Goal
111, not just prettier boilerplate.

Why:

- it adds a real artifact-shape distinction in `src/rtdsl/generate_only.py`:
  `single_file` versus `handoff_bundle`, with separate generation paths,
  manifest emission, stable program naming, and a generated README that encodes
  the run contract
- the bundle is meaningfully better for the stated handoff scenario
- the docs keep the scope honest:
  - `docs/goal_113_generate_only_maturation.md`
  - `docs/reports/goal113_generate_only_maturation_2026-04-05.md`
- the tests in `tests/goal113_generate_only_maturation_test.py` check the right
  thing: the bundle writes distinct handoff artifacts and the generated bundled
  program actually runs

Blocking issue:

- none found in the reviewed package

Caution:

- this is still only one renderer with one extra packaging mode
- it is better than Goal 111 only because the handoff scenario is concrete and
  the extra files are functional, not decorative
- if future expansion becomes mostly more bundle variants without new user
  value, pause it fast
